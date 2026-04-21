# Context-Aware File Organizer with Local OCR + Vision LLM

**Status:** ✅ Production — last updated 2026-04-21
**Host:** i7-11700, 62 GB RAM, RTX 3080 Ti 12 GB
**Workflow:** `7NyfPW2rX0fsTEep` (File Organizer (Event-Driven))

---

## Context

The previous n8n file organizer categorized by extension only. Goal was to drive categorization from file *content* — a PDF invoice lands in `Documents/Invoices/<vendor>/`, a research paper in `Documents/Research/`, a screenshot in `Images/Screenshots/`. Fully local.

Environment: `nvidia-container-toolkit 1.19.0`, Docker `nvidia` runtime. Trigger: `/home/andrea/scripts/download-monitor.sh` (inotifywait → webhook).

---

## Architecture (as built)

```
download-monitor.sh (inotifywait, systemd service)
        │  close_write / moved_to on ~/Downloads/
        ▼
  POST http://localhost:5678/webhook/file-added
        │
        ▼  n8n container (network_mode: host)
  Webhook
  → Classify File  (executeCommand)
        stdin JSON | node /home/andrea/scripts/classify.js
        stdout: { category, subfolder, sourcePath, targetPath, method, confidence }
  → Parse Classification (code node)
  → Move File (executeCommand)
        mkdir -p "$(dirname targetPath)" && mv sourcePath targetPath
  → Log Action (executeCommand)
  → Respond to Webhook

  classify.js routing:
    FAST_MAP[ext] → direct category, no LLM
    pdf            → unpdf text extraction → LLM text prompt
    image exts     → base64 → LLM vision prompt
    text/code exts → first 8 KB → LLM text prompt
    office exts    → pandoc → plain text → first 8 KB → LLM text prompt
    unknown        → try UTF-8 read → LLM text prompt; if unreadable → extensionFallback()
    LLM result     → accepted if whitelist ∧ confidence ≥ 0.6; else extensionFallback()
```

---

## Routing rules

### Fast path (extension only, instant)

| Extension(s) | Destination |
|---|---|
| `stl 3mf obj step stp iges igs amf gcode f3d fcstd blend` | `3D Printing/` |
| `xls xlsx csv ods fods` | `Spreadsheets/` |
| `ppt pptx odp key` | `Presentations/` |
| `mp4 mkv avi mov wmv flv webm m4v` | `Videos/` |
| `mp3 wav flac aac m4a ogg wma` | `Audio/` |
| `zip rar 7z tar gz bz2 xz tgz` | `Archives/` |
| `deb rpm appimage exe msi flatpakref snap flatpak pkg dmg` | `Installers/` |
| `hwp hwpx` | `Documents/HWP/` |
| `svg` | `Images/` |

### LLM path (content-driven)

| Input | How sent to model |
|---|---|
| `jpg jpeg png webp heic tiff bmp gif` | base64 in `images[]` (vision) |
| `pdf` | text extracted via `unpdf` → 8 KB text prompt |
| `txt md markdown json yaml yml xml html css py js ts sh bash c cpp h go rs php java` | first 8 KB → text prompt |
| `doc docx odt odf rtf fodt` | pandoc → plain text → first 8 KB → text prompt |

**LLM whitelist** (accepted categories):
`Documents/Invoices`, `Documents/Receipts`, `Documents/Contracts`, `Documents/Research`, `Documents/Manuals`, `Documents/Forms`, `Documents/Letters`, `Documents/Notes`, `Images/Screenshots`, `Images/Photos`, `Images/Scans`, `Images/Diagrams`, `Images/Memes`, `Code`

**extensionFallback()** — used when LLM returns low-confidence / non-whitelist / error:

| Extension | Fallback |
|---|---|
| `pdf` | `Documents/PDF/` |
| `md markdown` | `Documents/Markdown/` |
| `txt` | `Documents/Text/` |
| `doc docx odt odf rtf fodt` | `Documents/Word/` |
| image exts | `Images/` |
| code exts | `Code/` |
| anything else | `Other/` |

Scanned PDFs (text extraction yields < 50 chars) skip the LLM entirely and go straight to `Documents/PDF/`.

---

## Components

### 1. Ollama (native systemd)

- Installed: `curl -fsSL https://ollama.com/install.sh | sh`
- Model: `ollama pull qwen2.5vl:7b` (5.9 GB disk, ~6–12 GB VRAM warm)
- Service: `/etc/systemd/system/ollama.service` — **enabled**, auto-restart
- Override: `/etc/systemd/system/ollama.service.d/override.conf`
  ```ini
  [Service]
  Environment="OLLAMA_HOST=0.0.0.0"
  ```
- GPU auto-detected. Model unloads after 5 min idle (VRAM freed).

### 2. n8n (Docker, custom image)

**`/home/andrea/Projects/n8n/Dockerfile`:**
```dockerfile
FROM n8nio/n8n:latest
USER root
ARG PANDOC_VERSION=3.6.4
RUN wget -qO- "https://github.com/jgm/pandoc/releases/download/${PANDOC_VERSION}/pandoc-${PANDOC_VERSION}-linux-amd64.tar.gz" | \
    tar xz --strip-components=2 -C /usr/local/bin "pandoc-${PANDOC_VERSION}/bin/pandoc"
USER node
```
Note: `apk` and `apt-get` are not available in the Docker Hardened Alpine image — static binary is the only option.

**`/home/andrea/Projects/n8n/docker-compose.yml`:**
```yaml
version: '3.8'
services:
  n8n:
    build: .
    container_name: n8n
    restart: unless-stopped
    network_mode: host
    environment:
      - N8N_HOST=${N8N_HOST}
      - N8N_PORT=5678
      - N8N_PROTOCOL=http
      - GENERIC_TIMEZONE=${TIMEZONE}
      - TZ=${TIMEZONE}
      - WEBHOOK_URL=${WEBHOOK_URL}
      - N8N_ENCRYPTION_KEY=${N8N_ENCRYPTION_KEY}
      - N8N_USER_MANAGEMENT_DISABLED=false
      - NODES_EXCLUDE=[]
      - OLLAMA_URL=http://localhost:11434
    volumes:
      - ./data:/home/node/.n8n
      - /home/andrea/Downloads:/home/andrea/Downloads
      - /home/andrea/scripts:/home/andrea/scripts
    user: "1000:1000"
```
- `network_mode: host` — container shares host network namespace, `localhost:11434` reaches Ollama directly.
- `NODES_EXCLUDE=[]` — required in n8n v2 to re-enable the `executeCommand` node.
- `restart: unless-stopped` — Docker auto-restarts n8n when the Docker daemon starts.

### 3. classify.js

**`/home/andrea/scripts/classify.js`** — Node.js script, reads JSON from stdin, prints JSON to stdout.

```
Input (stdin):  {"filepath": "/path/to/file", "filename": "file.pdf"}
Output (stdout): {"category":"Documents/Research","subfolder":"neuroscience","sourcePath":"...","targetPath":"...","method":"llm","confidence":0.95}
```

Dependencies: `unpdf` npm package at `/home/andrea/scripts/node_modules/` (volume-mounted, visible to container).
- Install: `cd /home/andrea/scripts && npm install unpdf`

**n8n Classify File command:**
```
node /home/andrea/scripts/classify.js <<'__CLSFY_INPUT__' 2>>/tmp/classify-error.log
{"filepath":{{ JSON.stringify($json.body?.filepath || $json.filepath) }},"filename":{{ JSON.stringify($json.body?.filename || $json.filename) }}}
__CLSFY_INPUT__
```
Using heredoc with single-quoted delimiter: n8n `{{ }}` expressions are resolved before shell sees the string, but shell does no further expansion inside the heredoc body — so `$`, backticks, quotes in filenames are safe.

### 4. download-monitor.service

**`/etc/systemd/system/download-monitor.service`:**
```ini
[Unit]
Description=Download Folder Monitor
After=network.target docker.service
Wants=docker.service

[Service]
Type=simple
User=andrea
ExecStartPre=/bin/sh -c 'until curl -sf http://localhost:5678/healthz >/dev/null 2>&1; do sleep 3; done'
ExecStart=/home/andrea/scripts/download-monitor.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```
`ExecStartPre` polls n8n's `/healthz` every 3 s before starting inotifywait — ensures no events are lost during the post-reboot boot window while n8n is still initialising.

### 5. n8n workflow (DB)

- Workflow ID: `7NyfPW2rX0fsTEep`
- activeVersionId: `46802bae-9844-4f7e-b9f9-b9a1b1bcdbff`
- Node graph: `Webhook → Classify File → Parse Classification → Move File → Log Action → Respond to Webhook`
- **Patch procedure** (for future edits): `docker compose down` → edit sqlite → `docker compose up -d`. Must stop n8n first — WAL file overwrites changes on next checkpoint if n8n is running. Patch both `workflow_entity.nodes` AND `workflow_history.nodes` for the matching `versionId`.

---

## Reboot survival (all services enabled)

| Service | Enabled | Restart policy |
|---|---|---|
| `ollama` | ✅ | `Restart=always` |
| `docker` | ✅ | system service |
| `n8n` (container) | ✅ via Docker | `restart: unless-stopped` |
| `download-monitor` | ✅ | `Restart=always` + healthcheck wait |

Boot order: Docker → n8n (auto via restart policy) → download-monitor (waits for n8n healthz).

---

## All incidents & fixes

1. **n8n container not running** → `docker compose up -d`.
2. **`executeCommand` disabled in n8n v2** → added `NODES_EXCLUDE=[]` to compose env.
3. **SQLite WAL overwrote DB patch** → must stop n8n before patching.
4. **`activeVersionId` mismatch** → must patch both `workflow_entity` and `workflow_history` with matching versionId.
5. **Ollama "could not connect"** → service installed but not started; `sudo systemctl start ollama`.
6. **`apk add pandoc` failed** → Docker Hardened image has no apk. Used wget + static binary.
7. **Container couldn't reach Ollama** (bridge + extra_hosts) → UFW DROP + Docker iptables bypass blocked bridge traffic. Fix: `network_mode: host`.
8. **STL → `Other` instead of `3D Printing`** → whitelist check applied to all paths. Fix: only apply when `method === 'llm'`.
9. **PDFs all landing in `Other`** → `qwen2.5vl` vision endpoint rejects raw PDF bytes (`image: unknown format`). Fix: extract text with `unpdf` (Mozilla PDF.js), send as text prompt.
10. **LLM using `Documents/Text` as lazy default** → `Documents/{PDF,Markdown,Text,Word}` were in LLM whitelist. Fix: remove them; LLM picks only meaningful categories; `extensionFallback()` handles the generic buckets.
11. **Shell injection risk / filename special chars** → classify.js was invoked with shell-interpolated double-quoted args. Fix: pass via stdin heredoc with `JSON.stringify()` escaping in n8n expression.
12. **Docker disabled on boot** → `sudo systemctl enable docker`; n8n wasn't starting after reboot.
13. **download-monitor started before n8n ready** → added `ExecStartPre` healthcheck loop to service unit.

---

## Known issues / future work

- **Log Action node** references `$json.method`, `$json.category` etc. but at that point `$json` is the output of the preceding Move File `executeCommand` node (stdout/stderr), not Parse Classification. All log lines show `[]  →` empty. Fix: change references to `$('Parse Classification').item.json.method` etc.
- **Subfolder names truncated at 30 chars** — can break mid-word (e.g., `Arducam-UVC-Camera-Adapter-Boa`). Could truncate at word boundary or reduce the cap.
- **LLM biases toward `Documents/Research`** for any technical markdown. Borderline files (setup guides, homelab notes) often land there instead of `Notes` or `Manuals`. Prompt tuning or a second-pass re-classification could help.
- **Scanned PDFs** (no embedded text) fall back to `Documents/PDF/` without content understanding. Would need page→image rendering + vision call for true OCR; currently skipped.

---

## Budget (actual, measured)

| Resource | Cost |
|---|---|
| Disk | 5.9 GB model + ~200 MB pandoc layer |
| VRAM | 11–12 GB when warm (larger than expected — KV cache), unloads after 5 min idle |
| GPU power | ~350 W during inference, ~37 W idle |
| Latency | Fast path < 1 s; LLM path 3–6 s warm, ~15 s cold load |
| Throughput | ~60 files / 10 min (mixed fast + LLM batch) |

---

## Operational reference

| Task | Command |
|---|---|
| Check all services | `systemctl is-active ollama docker download-monitor` |
| Restart everything | `sudo systemctl restart ollama download-monitor && cd ~/Projects/n8n && docker compose restart` |
| Live classify log | `docker exec n8n tail -f /tmp/n8n-file-organizer.log` |
| classify.js errors | `docker exec n8n tail -f /tmp/classify-error.log` |
| Rebuild n8n image | `cd ~/Projects/n8n && docker compose build && docker compose up -d` |
| Patch workflow DB | `docker compose down` → edit sqlite → `docker compose up -d` |
| Change model | Edit `MODEL` in `/home/andrea/scripts/classify.js` (no rebuild) |
| Add LLM category | Add to `CATEGORY_WHITELIST` + `PROMPT` in `classify.js` |
| Add fast-path category | Add to `FAST_MAP` in `classify.js` |
| Re-trigger a file | `curl -X POST http://localhost:5678/webhook/file-added -H 'Content-Type: application/json' -d '{"filepath":"/path/to/file","filename":"file.ext"}'` |

---

## Live test results (2026-04-21, 385 files)

| Category | Files |
|---|---|
| Images | 110 |
| Other | 98 (binaries, unreadable, genuinely uncategorisable) |
| 3D Printing | 57 |
| Code | 22 |
| Spreadsheets | 15 |
| Documents/Research | 24 |
| Documents/Manuals | 15 |
| Documents/PDF | 8 |
| Documents/Forms | 8 |
| Documents/Text | 5 |
| Documents/Invoices | 4 |
| Documents/HWP | 3 |
| Documents/Notes | 3 |
| Documents/Receipts | 2 |
| Documents/Letters | 1 |
| Presentations | 5 |
| Archives | 2 |
| Installers | 2 |
| Videos | 1 |
