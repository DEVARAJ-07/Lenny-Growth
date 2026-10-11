# Troubleshooting Guide: The Lenny Growth Assistant

This document outlines common operational issues, diagnostics, and recovery steps.

---

## 1. Local Ollama Service Issues

### Symptom: `Cannot connect to local Ollama service at http://127.0.0.1:11434`
- **Cause**: Ollama daemon is not running or stopped.
- **Solution**:
  1. Open PowerShell and run:
     ```powershell
     powershell -ExecutionPolicy Bypass -File scripts\start-ollama.ps1
     ```
  2. Verify it is running by checking tags:
     ```powershell
     curl.exe -s http://127.0.0.1:11434/api/tags
     ```
  3. Ensure the environment variable is pointing to the models disk:
     ```powershell
     $env:OLLAMA_MODELS = "D:\LLMs\ollama_store"
     ```

### Symptom: Models are not found or pulling to `C:\Users\...` instead of `D:\LLMs`
- **Cause**: `OLLAMA_MODELS` was not set before launching `ollama.exe`.
- **Solution**:
  Always start Ollama using `scripts/start-ollama.ps1`, which explicitly exports:
  ```powershell
  $env:OLLAMA_MODELS = "D:\LLMs\ollama_store"
  ```

---

## 2. GPU CUDA Acceleration Verification

### Checking GPU utilization:
Run in PowerShell:
```powershell
nvidia-smi
```
During local model inference (`qwen2.5:3b`, `deepseek-r1:1.5b`), you should see `ollama_llama_server.exe` running on the NVIDIA GPU using approximately 1.5 GB to 2.4 GB of VRAM.

### Forcing CPU mode (if GPU VRAM is full):
Ollama automatically offloads layers to CPU if VRAM is constrained. To monitor layer offload, check the Ollama daemon logs.

---

## 3. Database & Ingestion Issues

### Symptom: `greenlet_spawn has not been called`
- **Cause**: SQLAlchemy asyncio requires `greenlet` when using async drivers.
- **Solution**: Ensure greenlet is installed in the virtual environment:
  ```powershell
  & ".\.venv\Scripts\pip.exe" install greenlet
  ```

### Switching between SQLite and PostgreSQL:
In `.env`:
- **SQLite (zero-dependency local development)**:
  ```env
  DATABASE_URL=sqlite+aiosqlite:///./lenny_growth.db
  ```
- **PostgreSQL with pgvector (production deployment)**:
  ```env
  DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/lenny_growth
  ```

---

## 4. Frontend & 3D Canvas Diagnostics

### Symptom: WebGL context lost or black canvas
- **Cause**: High GPU pressure or browser hardware acceleration disabled.
- **Solution**:
  1. Enable hardware acceleration in your browser settings (`chrome://settings/system`).
  2. The canvas uses `dpr={[1, 1.5]}` and `powerPreference="high-performance"` to minimize GPU draw overhead.

### Symptom: API requests fail with 404 or CORS errors
- **Cause**: Vite dev server not proxying backend routes.
- **Solution**:
  Ensure `frontend/vite.config.ts` includes proxy routes for `/health`, `/sessions`, `/artifacts`, and `/admin`.
  Alternatively, ensure the FastAPI server is running on `127.0.0.1:8000`.

---

## 5. Security Sandbox Inquiries

### How to verify sandbox isolation:
Right-click on an interactive artifact in the browser and select **Inspect Element**. Check the `<iframe>` attributes:
```html
<iframe srcdoc="..." sandbox="allow-scripts" class="..."></iframe>
```
Notice that `allow-same-origin` is absent. This guarantees that scripts executing inside the artifact:
- Cannot access `window.parent`
- Cannot access `document.cookie`
- Cannot access `localStorage` or `sessionStorage`
- Cannot make credentialed requests to internal endpoints
