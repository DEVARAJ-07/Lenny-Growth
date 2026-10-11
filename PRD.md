# Product Requirements Document (PRD)
## The Lenny Growth Assistant

**Role:** Forward Deployed Engineer (FDE) Engagement Deliverable  
**Version:** 1.0.0  
**Target Delivery:** 12 Oct 2026  
**Status:** Approved for Implementation  

---

## 1. Executive Summary & Discovery Brief

### 1.1 Context & Engagement Scenario
Product and Growth teams at fast-scaling tech companies frequently reference **Lenny's Podcast**—an archive of 300+ in-depth interviews with world-class product leaders (e.g., Shreyas Doshi, Elena Verna, Brian Chesky, Adam Fishman). However, team members spend hours listening, searching, and trying to recall specific frameworks. 

Existing public LLMs hallucinate general product advice rather than citing actual operator experiences. The client requested a turn-key internal assistant that reads transcripts, provides 100% grounded answers with exact episode and timestamp citations, produces publication-ready Ship 30 for 30 essays, and renders interactive artifacts natively in-app.

### 1.2 User & Problem Definition
* **Primary Users:** Growth Product Managers, Heads of Growth, Product Marketing Managers, and Founders.
* **Core Job-to-be-Done (JTBD):** *"When I am planning a growth initiative, pricing change, or onboarding redesign, I want to retrieve proven, battle-tested operator playbooks from Lenny's guests, so that I can make high-conviction decisions and communicate them clearly without listening to 50 hours of audio."*
* **Pain Removed:**
  1. **Time Sink:** Eliminates hours spent scouring YouTube, Spotify, or unstructured transcripts.
  2. **Hallucination Risk:** Eliminates generic AI speculation by strictly constraining synthesis to retrieved transcript chunks.
  3. **Context Switching:** Generates ready-to-share Ship 30 for 30 essays and rendered HTML artifacts directly in the app, eliminating prompt engineering and tool toggling.

### 1.3 Success Metrics
| Metric Category | Target | Measurement Method |
|---|---|---|
| **Grounding Accuracy** | $\ge 90\%$ | Golden set of 20 benchmark domain questions citing verified episode titles, guests, and timestamp markers. |
| **Refusal Quality** | $\ge 95\%$ | 5+ out-of-scope queries (e.g., cooking recipes, quantum electrodynamics) where assistant explicitly states: *"The transcripts don't cover this."* |
| **First Token Latency** | $< 1.5\text{s}$ (Cloud) / $< 4\text{s}$ (Local GPU) | Measured from user submission to first SSE token stream event. |
| **Time-to-Artifact** | $< 90\text{s}$ | Complete generation, structural validation, and rendering of a ~1,250-word Ship 30 essay. |
| **Evaluator Operability** | $< 10\text{ minutes}$ | Fresh evaluator setup time from clean clone to running containerized stack using documented steps. |

### 1.4 Assumptions
1. **User Identity & Multi-Tenancy:** The client team operates internally behind an enterprise network or VPN. Anonymous/session-based user mapping is sufficient for local evaluation, while PostgreSQL stores persistent `users` and `sessions` records.
2. **Local Hardware Constraints:** The local deployment evaluator may have diverse hardware (laptops with 8–16 GB RAM and limited VRAM). Thus, the local model defaults to high-efficiency $\le 4\text{B}$ parameter models (`qwen2.5:3b`, `llama3.2:3b`, `deepseek-r1:1.5b`) and `nomic-embed-text` (274 MB).
3. **Ingestion Refresh Cadence:** Transcripts are updated upstream periodically. Ingestion is idempotent using MD5 content hashing to enable re-running without duplicating embeddings.
4. **Cloud LLM Key Provisioning:** Cloud models (Anthropic Claude, OpenAI) are optional enhancements. If keys are missing, the system gracefully falls back to local Ollama with a visible UI notification.

### 1.5 Scope Choices (Inclusions vs. Intentional Exclusions)
* **Included:**
  * Hybrid search (PostgreSQL `tsvector` Full-Text Search + `pgvector` Cosine Similarity) merged via Reciprocal Rank Fusion (RRF).
  * Server-Sent Events (SSE) token-by-token streaming.
  * Dedicated Ship 30 for 30 skill with automated structural and word-count validation.
  * In-app sandboxed Artifact Viewer with strict Content Security Policy (CSP) and DOMPurify.
  * MindMerge split-panel design with ambient React Three Fiber 3D canvas (capped at 60 FPS).
* **Intentionally Excluded & Why:**
  * *Next.js Server Side Rendering (SSR):* Redundant complexity because FastAPI already owns the backend business logic and database ORM. React + Vite provides a cleaner, faster static single-page application.
  * *WebSockets:* SSE is unidirectional, simpler, connection-resilient, and native to HTTP/2, perfectly matching token streaming.
  * *Autonomous Multi-Agent Swarms:* Unnecessary latency and non-determinism for a focused RAG assistant. A deterministic router loop provides superior predictability and speed.

### 1.6 Risks & Mitigations
| Risk | Severity | Mitigation Strategy |
|---|---|---|
| **Hallucination** | High | Strict RRF similarity cutoff. If highest chunk score is below threshold, output hard refusal template. Explicit system prompt bans ungrounded external knowledge. |
| **Local Model Latency** | Medium | Utilize GPU-optimized quantized models ($\le 3.8\text{B}$ parameters) fitting 100% in VRAM, stream tokens over SSE, and cap prompt context. |
| **Cloud Cost Spike** | Low | Cap max output tokens, log token usage per session, and enable local Ollama by default. |
| **Untrusted HTML Rendering** | Critical | Render inside `<iframe sandbox="allow-scripts" srcdoc=...>` omitting `allow-same-origin`. Enforce strict CSP blocking network, parent DOM access, and external assets. |
| **Service Outage (Ollama/DB)** | Medium | Structured health checks (`/health/db`, `/health/llm`), graceful error responses with actionable repair hints (`"hint": "Run ollama serve..."`). |

---

## 2. Product Capabilities & User Flows

### Flow 1: Grounded Conversational Q&A
1. User enters a query (e.g., *"How did Patreon optimize their onboarding funnel according to Adam Fishman?"*).
2. Backend generates query embedding via `nomic-embed-text` and extracts lexemes for full-text search.
3. Hybrid Search queries PostgreSQL `chunks` table, computing RRF combined rank score.
4. If score $\ge \text{threshold}$:
   * Chunks are injected into context with `[Episode: Title | Guest | Timestamp]`.
   * LLM streams grounded answer with inline citations.
   * Citations drawer renders interactive cards with guest, episode title, and timestamp.
5. If score $< \text{threshold}$:
   * LLM returns: *"I checked Lenny's transcripts, but this topic is not covered in the episodes."*

### Flow 2: Ship 30 for 30 Content Generation
1. User requests an essay (e.g., *"Write a Ship 30 for 30 essay on hiring growth engineers based on Lenny's talks"*).
2. Agent Router identifies `ship30` intent and activates the Ship 30 skill.
3. Skill retrieves relevant transcript evidence and drafts a post structured around:
   * Compelling Hook (Headline + 1-2 sentence lead)
   * Skimmable Rhythm (Short paragraphs, subheadings, bullet lists, selective bolding)
   * Core Narrative Arc (Problem $\to$ Insight $\to$ Framework $\to$ Action)
   * Specific Actionable Takeaway
   * Transcript Grounding citations
4. Post-processor validator inspects:
   * Word count targeting ~1,250 words.
   * Structural elements (headers, bolding, bullet points).
5. Output is streamed to chat and automatically packaged into an Artifact.

### Flow 3: Interactive Artifact Generation & Viewer
1. User requests code or document (e.g., *"Create an HTML/CSS dashboard summarizing the 5 growth competency levels"*).
2. Agent Router delegates to Artifact Generator.
3. Generates complete, self-contained HTML/CSS.
4. Persists record in `artifacts` table.
5. UI displays artifact card with tabs (`HTML`, `CSS`, `Preview`) and automatically opens the side-by-side Sandboxed Viewer.
6. Viewer provides **Copy Code** and **Download File** capabilities.

---

## 3. Acceptance Criteria

- [x] **AC-1 (Grounded Retrieval):** Answers accurately cite transcript guest, episode title, and timestamp.
- [x] **AC-2 (Refusal Mode):** Unrelated queries trigger explicit refusal without hallucinating facts.
- [x] **AC-3 (Ship 30 Skill):** Generates ~1,250-word structured essay adhering to formatting rules.
- [x] **AC-4 (Artifact Isolation):** Generated HTML is isolated from parent cookies, storage, and scripts.
- [x] **AC-5 (Model Switcher):** Evaluator can toggle between Ollama (local) and Claude/OpenAI via config or UI.
- [x] **AC-6 (Structured Errors):** All failures return `{ "error": { "code", "message", "request_id", "hint" } }`.
- [x] **AC-7 (Persistence):** Sessions and messages are stored in PostgreSQL and reloadable across restarts.
- [x] **AC-8 (One-Command Startup):** System boots cleanly via standard command / Docker workflow.
