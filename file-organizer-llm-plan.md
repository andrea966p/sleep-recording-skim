# Context-Aware File Organizer with Local OCR + Vision LLM

**Status:** ✅ Deployed and verified — 2026-04-21
**Host:** i7-11700, 62 GB RAM, RTX 3080 Ti 12 GB
**Workflow:** `7NyfPW2rX0fsTEep` (File Organizer (Event-Driven))

---

## Context

The previous n8n file organizer categorized by extension only. Goal was to drive categorization from file *content* — a PDF invoice lands in `Documents/Invoices/<vendor>/`, a research paper in `Documents/Research/`, a screenshot in `Images/Screenshots/`. Fully local.

Environment pre-checks: `nvidia-container-toolkit 1.19.0`, Docker `nvidia` runtime, 138 GB free disk. Trigger: `/home/andrea/scripts/download-monitor.sh` (inotifywait → webhook).

## Decisions (confirmed up-front)

| Decision | Choice |
|---|---|
| LLM scope | All non-media files: PDFs, images, text, Office docs, code. Skip videos, audio, archives, installers, 3D printing. |
| Folder scheme | Fixed top-level whitelist; LLM proposes free-form subfolder. |
| Ollama install | Native on the host (systemd service). |
| Office docs | Extract text via pandoc, then LLM. |
| Model | `qwen2.5vl:7b` (vision + text in one). |

---

## Architecture (as built)

```
download-monitor.sh (inotifywait)
        │
        ▼
  POST /webhook/file-added      ← n8n container (network_mode: host)
        │
        ▼
  ┌─ Webhook ─┐
  │ Classify File  (executeCommand) ──► node /home/andrea/scripts/classify.js "<filepath>" "<filename>"
  │ Parse Classification (code)
  │ Move File (executeCommand)
  │ Log Action (executeCommand)
  │ Respond to Webhook
  └────────────┘
        │
        ▼
  classify.js decides:
   • FAST_MAP extension → direct category (media / archives / installers / 3D / HWP / SVG / spreadsheets / presentations)
   • else → POST http://localhost:11434/api/generate (qwen2.5vl:7b, format=json)
        ◦ images / PDFs: sent as base64 in `images[]`
        ◦ text files: first 8 KB of content inlined
        ◦ office docs: pandoc → plain text, first 8 KB inlined
   • JSON { category, subfolder, confidence } — only accepted if whitelist ∧ confidence ≥ 0.6, else → Other
```

**Single-script design note:** Original plan had a multi-node n8n graph (Read Binary File → HTTP Request → Parse JSON, with IF branches). The final implementation collapses all of that into one Node.js script (`classify.js`) called from a single `executeCommand` node. Reasons: (1) n8n HTTP Request node + host-mode Ollama needed brittle URL handling, (2) branching logic and base64 encoding are trivial in Node, (3) fewer nodes = easier to reason about and version in plain files.

---

## Components — final state

### 1. Ollama (native)

- Install: `curl -fsSL https://ollama.com/install.sh | sh`
- Model: `ollama pull qwen2.5vl:7b` (5.9 GB on disk, ~6 GB VRAM warm)
- Service: `/etc/systemd/system/ollama.service` (installer default).
- **Drop-in override** `/etc/systemd/system/ollama.service.d/override.conf`:
  ```ini
  [Service]
  Environment="OLLAMA_HOST=0.0.0.0"
  ```
  (Originally needed so container could reach it. With final `network_mode: host` this is redundant but harmless — left in place.)
- Auto-detected GPU, unloads after 5 min idle.

### 2. Custom n8n image with pandoc

`/home/andrea/Projects/n8n/Dockerfile`:
```dockerfile
FROM n8nio/n8n:latest
USER root
ARG PANDOC_VERSION=3.6.4
RUN wget -qO- "https://github.com/jgm/pandoc/releases/download/${PANDOC_VERSION}/pandoc-${PANDOC_VERSION}-linux-amd64.tar.gz" | \
    tar xz --strip-components=2 -C /usr/local/bin "pandoc-${PANDOC_VERSION}/bin/pandoc"
USER node
```

Why wget+tar instead of `apk add pandoc`: the upstream `n8nio/n8n:latest` is a Docker Hardened image — `apk` is not present, and `apt-get` is not applicable (Alpine-based). Static binary is the cleanest route.

### 3. docker-compose.yml

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

**Key divergence from plan:** Originally `extra_hosts: ["host.docker.internal:host-gateway"]` with bridge networking. That path failed because UFW's default DROP policy blocked Docker bridge traffic to the host, and Docker's iptables rules bypass UFW — adding UFW allow rules didn't help. Switched to `network_mode: host` so the container shares the host's network namespace, making `localhost:11434` trivially reachable. `NODES_EXCLUDE=[]` is needed to re-enable the `executeCommand` node in n8n v2.

### 4. classify.js

`/home/andrea/scripts/classify.js` — single-entry Node script (Node's built-in `fetch`). Invoked by the n8n `executeCommand` node with `(filepath, filename)`. Prints one line of JSON to stdout:
```json
{ "category": "...", "subfolder": "...", "sourcePath": "...", "targetPath": "...", "method": "...", "confidence": 0.xx }
```

Whitelist + confidence threshold are applied only when `method === 'llm'`. Extension-path results (`method: 'extension'`) bypass both, so `.stl` reaches `3D Printing` even though that category isn't in the LLM whitelist.

LLM prompt (JSON-forced via Ollama's `format: "json"`):
```
You are a file categorizer. Analyze the content and pick exactly ONE category from this list:
Documents/Invoices, Documents/Receipts, Documents/Contracts, Documents/Research,
Documents/Manuals, Documents/Forms, Documents/Letters, Documents/Notes,
Documents/PDF, Documents/Markdown, Documents/Text, Documents/Word,
Images/Screenshots, Images/Photos, Images/Scans, Images/Diagrams, Images/Memes,
Code, Other

Also propose an optional subfolder name (max 30 chars, kebab-case, empty string if
none fits — prefer empty over weak groupings).

Return ONLY valid JSON, no prose:
{"category":"<from list>","subfolder":"<string or empty>","confidence":<0.0-1.0>}
```

Subfolder sanitization: regex strips non-alphanumerics to `-`, collapses runs, trims, caps at 30 chars.

### 5. n8n workflow (DB patch)

- Workflow ID: `7NyfPW2rX0fsTEep`
- activeVersionId: `46802bae-9844-4f7e-b9f9-b9a1b1bcdbff`
- Node graph in DB: `Webhook → Classify File → Parse Classification → Move File → Log Action → Respond to Webhook`
- Patched both `workflow_entity.nodes` *and* the matching `workflow_history.nodes` row. **Important:** n8n must be stopped during the patch, otherwise the WAL file overwrites the change on next checkpoint.

---

## Routing rules (final)

**Fast path (extension, no LLM):**
- 3D Printing: `stl 3mf obj step stp iges igs amf gcode f3d fcstd blend`
- Spreadsheets: `xls xlsx csv ods fods`
- Presentations: `ppt pptx odp key`
- Videos: `mp4 mkv avi mov wmv flv webm m4v`
- Audio: `mp3 wav flac aac m4a ogg wma`
- Archives: `zip rar 7z tar gz bz2 xz tgz`
- Installers: `deb rpm AppImage appimage exe msi flatpakref snap flatpak pkg dmg`
- Korean docs: `hwp hwpx` → `Documents/HWP`
- SVG → `Images` (vector assets usually, not photos)

**LLM path:**
- Images: `jpg jpeg png webp heic tiff bmp gif` (base64 → vision model)
- PDFs: `pdf` (base64 → vision model)
- Text-based: `txt md markdown json yaml yml xml py js ts html css sh bash c cpp h go rs php java` (8 KB head → text prompt)
- Office: `doc docx odt odf rtf fodt` (pandoc → plain → 8 KB head → text prompt)
- Unknown extension → try as UTF-8 text; if unreadable → `Other`

---

## Files touched

- ✅ **New** `/home/andrea/Projects/n8n/Dockerfile`
- ✅ **Modified** `/home/andrea/Projects/n8n/docker-compose.yml`
- ✅ **New** `/home/andrea/scripts/classify.js`
- ✅ **Modified** `/home/andrea/Projects/n8n/data/database.sqlite` (workflow + history rows)
- ✅ **New (installer)** `/etc/systemd/system/ollama.service`, `/usr/local/bin/ollama`
- ✅ **New (manual)** `/etc/systemd/system/ollama.service.d/override.conf`
- Unchanged: `/home/andrea/scripts/download-monitor.sh`

---

## Verification (2026-04-21)

| # | Check | Result |
|---|---|---|
| 1 | `systemctl is-active ollama` | ✅ `active` |
| 2 | `curl -s http://localhost:11434/api/tags` lists `qwen2.5vl:7b` | ✅ model present (5.9 GB) |
| 3 | Container reaches Ollama (`docker exec n8n wget -qO- http://localhost:11434/api/tags`) | ✅ works via host network |
| 4 | `docker exec n8n which pandoc` | ✅ `/usr/local/bin/pandoc` (3.6.4) |
| 5 | `docker logs n8n` shows "Activated workflow" | ✅ `File Organizer (Event-Driven)` |
| 6 | `.stl` end-to-end | ✅ `Organized/3D Printing/test_e2e.stl` (fast path) |
| 7 | Fake invoice `.txt` end-to-end | ✅ `Organized/Documents/Invoices/test_invoice/test_invoice.txt` (LLM path, correct category + sensible subfolder) |
| 8 | `Organized/` top-level categories present | ✅ 3D Printing, Archives, Audio, Code, Documents, Images, Installers, Other, Presentations, Spreadsheets, Videos |
| 9 | `Organized/Documents/` subfolders present | ✅ HWP, Invoices, Markdown, PDF, Text, Word |

---

## Incidents & fixes (hit during deploy)

1. **n8n container not running** → `docker compose up -d`.
2. **`executeCommand` disabled in n8n v2** → added `NODES_EXCLUDE=[]`.
3. **SQLite WAL overwrote patch** → stop n8n → patch → start.
4. **`activeVersionId` mismatch** → when updating `workflow_history`, keep `versionId` in sync with `workflow_entity.activeVersionId`.
5. **Ollama "could not connect"** on first run → `sudo systemctl start ollama` (unit was installed but not started).
6. **`apk add pandoc` failed** → hardened image, no apk. Switched to wget + static binary.
7. **`apt-get install pandoc` failed** → image is Alpine, not Debian. Same fix.
8. **Container could not reach host Ollama (bridge + extra_hosts)** → UFW DROP + Docker iptables bypass blocked it. Allow rule didn't help. Fix: `network_mode: host` and drop `extra_hosts`.
9. **STL landed in `Other` instead of `3D Printing`** → `buildResult` applied CATEGORY_WHITELIST to extension-path results. Fix: gate whitelist/confidence checks on `method === 'llm'` only.

---

## Budget (actual)

| Resource | Cost |
|---|---|
| Disk | 5.9 GB model + pandoc ~200 MB in image layer |
| VRAM | ~6 GB when warm, unloads after 5 min idle |
| Latency | Fast path <1 s; LLM path ~3–6 s warm, ~15 s on cold load |
| Idle CPU/GPU | Near zero |

---

## Operational notes

- **Logs:** `/tmp/n8n-file-organizer.log` (one line per processed file), `/tmp/classify-error.log` (classify.js stderr).
- **Restart sequence** after future DB edits: `docker compose down` → patch sqlite → `docker compose up -d`.
- **Changing the model:** edit `MODEL` in `classify.js`; no rebuild needed (script is volume-mounted).
- **Adding a category:** update `CATEGORY_WHITELIST` *and* the `PROMPT` list in `classify.js` (LLM only). Fast-path categories go in `FAST_MAP`.
- **Confidence threshold:** currently 0.6 in `buildResult`. Lower to admit more categorized results at the cost of occasional mis-routes.
