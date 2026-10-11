# Engineering & Autonomous Agent Development Journal

This journal chronicles the key engineering challenges, technical trade-offs, and iterative solutions formulated while constructing **The Lenny Growth Assistant**.

---

## 📅 Session 1: Environment Assessment & Hardware Profiling
- **Challenge**: The user requested downloading top local LLMs with fast response and deep thinking to a dedicated location (`D:\LLMs`), avoiding cloud dependencies for core demos.
- **Hardware Profile Detected**:
  - GPU: NVIDIA GeForce RTX 2050 (4 GB VRAM)
  - RAM: 16 GB DDR4
  - OS: Windows 11
- **Decisions**:
  - Selected model portfolio optimized for 4 GB VRAM envelope:
    1. `nomic-embed-text:latest` (274 MB, 768 dims) for local semantic embeddings.
    2. `qwen2.5:3b` (1.9 GB, Q4_K_M) achieving ~43.6 tok/s for ultra-fast grounded QA.
    3. `deepseek-r1:1.5b` (1.1 GB, Q4_K_M) achieving ~17.1 tok/s with `<think>` chain-of-thought.
    4. `llama3.2:3b` (2.0 GB, Q4_K_M) achieving ~32.2 tok/s for long-form drafting.
  - Configured Ollama with `OLLAMA_MODELS=D:\LLMs\ollama_store`.
  - Added individual directories with model cards at `D:\LLMs\01-deepseek-r1-1.5b`, `02-qwen2.5-3b`, `03-llama3.2-3b`, `04-nomic-embed-text`.

---

## 📅 Session 2: Ingestion & Hybrid Retrieval Engineering
- **Challenge**: Indexing Lenny's Podcast transcripts with zero hallucinations and accurate timestamped citations.
- **Decisions**:
  - Cloned repository `ChatPRD/lennys-podcast-transcripts` containing 303 episodes.
  - Implemented `TranscriptChunker` to split on conversational turns and speaker transitions with 50-token overlap, retaining exact timestamps `(HH:MM:SS)`.
  - Designed **Hybrid Reciprocal Rank Fusion (RRF)**:
    - Pure vector search often struggled with specific guest names ("Elena Verna", "Adam Fishman") or industry acronyms ("PLG", "CAC:LTV").
    - Lexical search catches precise tokens and guest names.
    - Added comprehensive stopword filtering and length thresholding to prevent false lexical matches on queries like *"How do I bake a chocolate cake?"*.
    - Formula: $\text{RRF}(d) = \sum_{m \in \{\text{lexical}, \text{vector}\}} \frac{1}{60 + \text{rank}_m(d)}$.

---

## 📅 Session 3: MindMerge 3D Frontend & Sandbox Security
- **Challenge**: Replicating the MindMerge UI from `stitch_3d_chatbot_ui_platform.zip` with high visual fidelity, 60 FPS 3D canvas, and secure Claude-style artifact rendering.
- **Decisions**:
  - Built 3D Neural Emblem using React Three Fiber (`@react-three/fiber` + `three`):
    - Capped pixel ratio `dpr={[1, 1.5]}` to prevent retina lag.
    - Low-poly geometry (< 500 triangles total) and single draw-call particle buffer.
    - Smooth mouse parallax using `THREE.MathUtils.lerp`.
  - Implemented strict iframe sandbox for generated HTML artifacts:
    - Configured with `sandbox="allow-scripts"` and explicit omission of `allow-same-origin`.
    - Injected strict Content Security Policy meta tags.
  - Created SSE streaming client with real-time token rendering, DeepSeek thought accordion, and code tabs.

---

## 📅 Session 4: Automated Verification & Test Coverage
- **Challenge**: Ensuring 100% test reliability across routing, schema validation, health checks, and failure modes.
- **Decisions**:
  - Implemented 10 comprehensive tests using `pytest` and `pytest-asyncio`.
  - Discovered and fixed substring token matching in `lexical_score` (prevented false matches of single-letter substrings against titles).
  - All 10 tests passed in 2.38s.
  - Verified Vite build for production with 0 errors.
