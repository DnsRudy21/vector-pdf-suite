<div align="center">

# ⚡ Vector PDF Suite

### Private, fast and batch-first PDF tools — right on your computer.

![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.116-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=111827)
![Electron](https://img.shields.io/badge/Electron-43-47848F?logo=electron&logoColor=white)
![License](https://img.shields.io/badge/License-AGPL--3.0-22c55e)

**Convert · Merge · Split · Compress · Protect · Extract**

</div>

---

## What is Vector PDF Suite?

Vector PDF Suite is a modern PDF workspace designed for teachers, students and everyday office workflows. It processes documents locally, supports batches of up to 50 files and provides a polished interface for the most common PDF operations.

No account is required. The desktop and portable editions run entirely on the user's computer.

## Academic origin

Vector PDF Suite began as an academic project created to give students and teachers a friendly, dependable way to work with documents without uploading classroom material to third-party services. Its design prioritizes clarity, privacy and practical workflows that are easy to explain in a lab, classroom or workshop.

The project is now public so educators, students and developers can study its architecture, adapt it to their communities and contribute improvements. It is intended to be both a useful application and an approachable full-stack reference project.

## Highlights

| Tool | What it does |
| --- | --- |
| PDF to Images | Export every page as PNG, JPG, BMP or TIFF with adjustable DPI and quality. |
| Images to PDF | Combine multiple images into one ordered PDF document. |
| Merge PDFs | Join several PDF files in the exact order shown in the interface. |
| Split PDFs | Create one file per page or split using custom page ranges. |
| Compress PDFs | Clean and recompress PDF streams, images and fonts. |
| Protect PDFs | Apply AES-256 password protection and content permissions. |
| Watermark | Add a custom text watermark with adjustable opacity. |
| PDF to Word/Excel | Extract page text into editable DOCX or XLSX files. |
| Metadata | Export document properties and page counts as JSON. |

Additional features include:

- Batch processing for up to **50 files**.
- Drag and drop with manual file ordering.
- Live progress, cooperative cancellation and clear error messages.
- SHA-256 disk cache with TTL and size-based eviction.
- Light and dark themes with accessible native controls.
- Web, Docker, Windows installer and single-file portable builds.
- Automatic temporary-file cleanup and bounded upload sizes.

## Architecture

```text
VECTOR_PDFSUITE/
├── backend/
│   ├── app/                 FastAPI API, cache and PDF engine
│   ├── tests/               API and operation tests
│   ├── Dockerfile
│   ├── requirements.txt     Production dependencies
│   └── requirements-dev.txt Development and packaging tools
├── frontend/
│   ├── electron/            Windows desktop shell
│   ├── src/                 React application
│   ├── Dockerfile
│   └── package.json
├── .github/workflows/       Continuous integration
├── docker-compose.yml
├── install.cmd              Windows development setup
├── start.cmd                Local development launcher
├── build-portable.cmd       Single-file Windows build
└── build-desktop.cmd        Windows installer build
```

The React client sends multipart jobs to FastAPI. Uploaded files are streamed to isolated temporary directories, processed outside the event loop and returned directly or as ZIP archives. Repeated jobs are resolved from a persistent content-addressed cache.

## Quick start

### Requirements

- Python 3.11 or newer
- Node.js 20 or newer with Corepack
- Windows 10/11 for desktop packaging

### Windows

```powershell
.\install.cmd
.\start.cmd
```

Open [http://localhost:5173](http://localhost:5173). API documentation is available at [http://localhost:8000/docs](http://localhost:8000/docs).

### Manual setup

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r backend/requirements-dev.txt
corepack enable
pnpm install --frozen-lockfile
```

Run the API and client in separate terminals:

```bash
cd backend && uvicorn app.main:app --reload
pnpm dev
```

## Fork, customize and improve

1. Click **Fork** on GitHub or clone the repository.
2. Create a branch for your change: `git switch -c feat/my-improvement`.
3. Run the development setup and verify the existing tests.
4. Implement and document the improvement.
5. Run tests and the production build before opening a pull request.

The backend and frontend are intentionally separated, so contributors can replace the interface, add API operations, improve document processing or create packaging targets without rewriting the entire application.

## Docker

```bash
docker compose up --build
```

The application will be available at [http://localhost:8080](http://localhost:8080).

## Windows releases

Build a single portable executable:

```powershell
.\build-portable.cmd
```

Build the standard desktop installer:

```powershell
.\build-desktop.cmd
```

Generated binaries are intentionally excluded from Git. Publish them through **GitHub Releases** instead of committing them to the repository.

When publishing a release, attach the portable executable or installer to a tagged GitHub Release. GitHub automatically provides source archives for the tag; keep those archives available so binary recipients can obtain the corresponding source code required by the AGPL.

## API overview

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/api/health` | Service and worker health. |
| `GET` | `/api/capabilities` | Supported operations and limits. |
| `POST` | `/api/jobs` | Create a batch-processing job. |
| `GET` | `/api/jobs/{job_id}` | Read status and progress. |
| `DELETE` | `/api/jobs/{job_id}` | Request cancellation. |
| `GET` | `/api/jobs/{job_id}/download` | Download a completed result. |

Interactive OpenAPI documentation is generated automatically at `/docs`.

## Limits and privacy

- Maximum **100 MB per file**.
- Maximum **500 MB per batch**.
- Maximum **50 files per job**.
- Files are processed locally and temporary inputs are removed after completion.
- Word and Excel export extracts text by page; it does not recreate complex layouts pixel-for-pixel.
- Compression results depend on how efficiently the source PDF was originally encoded.

## Testing

```bash
pip install -r backend/requirements-dev.txt
PYTHONPATH=backend pytest backend/tests -q
pnpm build
```

GitHub Actions runs backend tests and a production frontend build for every push and pull request.

## Author

Created with care for students and educators by **Engineer José Carlos Malacara Espinosa**.

## License

Vector PDF Suite is released under the [GNU Affero General Public License v3.0](LICENSE). You may use, study, modify and redistribute it, provided that redistributed or network-accessible modified versions comply with the AGPL and make their corresponding source code available.

This license is required by the open-source licensing terms of PyMuPDF/MuPDF. A commercial PyMuPDF license may provide different terms for proprietary distributions. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for dependency information.
