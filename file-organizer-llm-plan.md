# Context-Aware File Organizer with Local OCR + Vision LLM

## Context

The current n8n file organizer categorizes by extension only. The user wants content-driven sorting — e.g. a PDF invoice lands in `Documents/Invoices/Acme-Corp/`, a neuroscience paper in `Documents/Research/Neuroscience/`, a screenshot in `Images/Screenshots/`. Fully local on the host (i7-11700, 62 GB RAM, RTX 3080 Ti 12 GB VRAM).

Environment already prepared: `nvidia-container-toolkit 1.19.0` installed, Docker has `nvidia` runtime, 138 GB free disk. Workflow active: id `7NyfPW2rX0fsTEep` at `/home/andrea/Projects/n8n/data/database.sqlite`, triggered by `/home/andrea/scripts/download-monitor.sh`.

## User-confirmed decisions

| Decision | Choice |
|---|---|
| LLM scope | All non-media files: PDFs, images, text files, Office docs, code. Skip videos, audio, archives, installers, 3D printing. |
| Folder scheme | Fixed top-level whitelist; LLM proposes free-form subfolder. |
| Ollama install | Native on the host (systemd service). |
| Office docs (.doc/.docx/.odt) | Extract text so LLM can categorize them — custom n8n image with `pandoc`. |

## Approach

### 1. Install Ollama + model (native)

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull qwen2.5vl:7b      # ~6 GB disk, ~6 GB VRAM
```

Installer creates `/etc/systemd/system/ollama.service`, binds to `127.0.0.1:11434`, auto-detects GPU. One model covers both roles — Qwen2.5-VL handles images *and* plain text inputs via `/api/generate`.

### 2. Custom n8n image with pandoc

Create `/home/andrea/Projects/n8n/Dockerfile`:

```Dockerfile
FROM n8nio/n8n:latest
USER root
RUN apk add --no-cache pandoc
USER node
```

Update `docker-compose.yml`:
- Replace `image: n8nio/n8n:latest` with `build: .`
- Add `extra_hosts: ["host.docker.internal:host-gateway"]` so n8n can reach host Ollama
- Add `OLLAMA_URL=http://host.docker.internal:11434`

Rebuild: `docker compose build && docker compose up -d`.

### 3. Routing rules inside the workflow

**LLM path (content-aware):**
- PDFs: `pdf`
- Images: `jpg jpeg png webp heic tiff bmp gif`
- Text-based: `txt md markdown json yaml yml xml py js ts html css sh bash c cpp h go rs php java`
- Office (extracted to text via pandoc first): `doc docx odt odf rtf fodt`

**Fast path (extension only):**
- Spreadsheets / presentations: `xls xlsx csv ods ppt pptx odp key` (too structured for content sort)
- 3D Printing: `stl 3mf obj step stp iges igs amf gcode f3d fcstd blend`
- Videos: `mp4 mkv avi mov wmv flv webm m4v`
- Audio: `mp3 wav flac aac m4a ogg wma`
- Archives: `zip rar 7z tar gz bz2 xz tgz`
- Installers: `deb rpm AppImage appimage exe msi flatpakref snap flatpak pkg dmg`
- Korean docs: `hwp hwpx` (no good open-source extractor)
- SVG: fast path — too often vector assets, not content

### 4. Revised workflow graph

```
Webhook
  └─► Prepare (Code)
        inputs: filename, filepath
        outputs: { use_llm, llm_mode ("image"|"text"), 
                   fallback_category, fallback_targetPath, extension }

  ├── IF use_llm == true AND llm_mode == "image"
  │      └─► Read Binary File (filepath)
  │            └─► HTTP Request → POST http://host.docker.internal:11434/api/generate
  │                  body: { model: "qwen2.5vl:7b", format: "json",
  │                          prompt: <categorize prompt>,
  │                          images: ["<base64>"] }
  │            └─► Parse JSON → finalize targetPath
  │
  ├── IF use_llm == true AND llm_mode == "text"
  │      ├── IF extension in office set:
  │      │     Execute Command: pandoc "<filepath>" -t plain | head -c 8192
  │      └── ELSE:
  │            Read File (first 8 KB)
  │      └─► HTTP Request → POST http://host.docker.internal:11434/api/generate
  │            body: { model: "qwen2.5vl:7b", format: "json",
  │                    prompt: <categorize prompt with file content> }
  │      └─► Parse JSON → finalize targetPath
  │
  └── ELSE
        └─► use fallback_targetPath

  └─► Move File (executeCommand)
  └─► Log Action (executeCommand)
  └─► Respond to Webhook
```

Finalization rule: if LLM JSON has `confidence >= 0.6` and `category` is in the whitelist, use `Organized/<category>/<subfolder>/<filename>`. Otherwise use `fallback_targetPath` from the Prepare node.

### 5. LLM prompt (shared by both modes, JSON-forced)

```
You are a file categorizer. Given the file content below, pick ONE top-level 
category from this list EXACTLY:
  Documents/Invoices, Documents/Receipts, Documents/Contracts,
  Documents/Research, Documents/Manuals, Documents/Forms,
  Documents/Letters, Documents/Notes, Documents/PDF,
  Documents/Markdown, Documents/Text, Documents/Word,
  Images/Screenshots, Images/Photos, Images/Scans,
  Images/Diagrams, Images/Memes,
  Code, Other

Also propose an optional short subfolder (<= 30 chars, snake_or-kebab, empty
string if none fits — prefer empty over inventing weak groupings).

Filename: <filename>
<content or image follows>

Return STRICT JSON only:
{"category": "<whitelisted>", "subfolder": "<string-or-empty>", "confidence": 0.0..1.0}
```

Ollama's `format: "json"` mode forces parseable output.

### 6. Files touched

- **New** `/home/andrea/Projects/n8n/Dockerfile` — n8n + pandoc.
- `/home/andrea/Projects/n8n/docker-compose.yml` — swap `image` for `build: .`, add `extra_hosts`, add `OLLAMA_URL` env.
- `/home/andrea/Projects/n8n/data/database.sqlite` — update `workflow_entity.nodes` and the matching `workflow_history.nodes` row for `workflowId = 7NyfPW2rX0fsTEep`, keeping `activeVersionId = 46802bae-9844-4f7e-b9f9-b9a1b1bcdbff`. Stop n8n → patch DB → start n8n (same pattern that worked in the prior fix).
- `/home/andrea/Downloads/file-organizer-workflow.json` — mirror for the user-facing export.
- **Unchanged:** `/home/andrea/scripts/download-monitor.sh`.
- **New (installer-managed):** `/etc/systemd/system/ollama.service`, `/usr/local/bin/ollama`.

### 7. Budget

| Resource | Cost |
|---|---|
| Disk | ~6 GB model + ~200 MB pandoc in image |
| VRAM | ~6 GB when LLM is warm (Ollama unloads after 5 min idle) |
| Latency | Fast path <1 s; LLM path ~3–6 s (first call after idle ~15 s for model load) |
| Idle CPU/GPU | Near zero — Ollama only warms on first request |

## Verification

1. `systemctl is-active ollama` → `active`.
2. `curl -s http://localhost:11434/api/tags | grep qwen2.5vl` → model listed.
3. `docker exec n8n curl -s http://host.docker.internal:11434/api/tags` → same output from inside the container.
4. `docker exec n8n which pandoc` → `/usr/bin/pandoc`.
5. `docker logs n8n 2>&1 | grep "Activated workflow"` → shows `File Organizer (Event-Driven)`.
6. Drop `.stl` → arrives in `Organized/3D Printing/` within ~2 s. (Fast path regression check.)
7. Drop a screenshot PNG → arrives in `Organized/Images/Screenshots/`.
8. Drop a known invoice PDF → arrives in `Organized/Documents/Invoices/<vendor-or-empty>/`.
9. Drop a `.docx` essay → arrives in `Organized/Documents/Research/` or similar, proving pandoc path works.
10. Drop a blurry/empty PDF → lands in `Organized/Documents/PDF/` (low-confidence fallback).
11. `nvidia-smi` during (7–9) shows VRAM ~6 GB, then drops after 5 min idle.
12. `/tmp/n8n-file-organizer.log` has one line per processed file.
