# Demo Video Script (2-3 Minutes Walkthrough)
**Role:** Forward Deployed Engineer (FDE)  
**Project:** The Lenny Growth Assistant (MindMerge 3D AI Platform)  
**Format:** Camera on, screen share, crisp operator tone.

---

## ⏱️ Video Breakdown

| Timestamp | Section | Screen Visual | Talking Points |
|---|---|---|---|
| **0:00 - 0:30** | Introduction & Problem Space | Web camera + MindMerge UI landing view | *"Hi everyone! I'm presenting The Lenny Growth Assistant, built as a forward deployed internal partner for product and growth leaders. With over 300 episodes of Lenny's Podcast, the challenge isn't access to data—it's fast, zero-hallucination tactical synthesis that operators can trust on Monday morning."* |
| **0:30 - 1:00** | Architecture & Local Hardware | Split screen showing `nvidia-smi` / Ollama daemon at `D:\LLMs` | *"For privacy, cost, and edge deployment, this system is running 100% locally on an NVIDIA GeForce RTX 2050 with 4GB VRAM. We have four specialized models running out of `D:\LLMs`: `nomic-embed-text` for 768-dimensional embeddings, `qwen2.5:3b` producing 44 tokens per second, `deepseek-r1:1.5b` for chain-of-thought reasoning, and `llama3.2:3b` for conversational drafting."* |
| **1:00 - 1:40** | Grounded Citations & Zero Hallucination | Type: *"What does Adam Fishman say about onboarding?"* then *"How do I bake a chocolate cake?"* | *"Let's test retrieval. Notice as Qwen streams back: every single claim is bound to transcript excerpts. Expanding our Citations accordion shows verified guest names, episode titles, and precise timestamps—like Adam Fishman at 00:49:51. Now watch what happens when we ask an out-of-scope question like 'How do I bake a chocolate cake?'. The system immediately triggers our refusal cutoff: 'I searched through Lenny's 300+ transcripts, but this topic is not covered'. Zero hallucination, zero wasted tokens."* |
| **1:40 - 2:15** | Ship 30 Essays & Sandboxed Artifacts | Select Ship 30 prompt, then generate interactive HTML calculator | *"Next, we built specialized agent workflows. When prompted for essays, our orchestrator invokes the Ship 30 skill, generating a 1,250-word atomic essay with an irresistible hook, tactical framework, operator quotes, and Monday-morning checklist, scored in real-time by an automated validator. For metrics, it generates interactive HTML artifacts. Clicking 'View Sandbox' slides out our Claude-style viewer, running safely inside an iframe with strict Content Security Policy and no same-origin access."* |
| **2:15 - 2:50** | 3D Experience & Technical Trade-offs | Show 3D Neural Core mouse parallax and code tabs | *"On the frontend, we faithfully implemented the MindMerge design with React Three Fiber. Notice the 3D Neural Core: it tilts with mouse parallax at 60 FPS while keeping draw calls under 30. Regarding trade-offs: we chose Reciprocal Rank Fusion over pure dense vectors because dense vectors often miss exact guest names like Elena Verna or specific acronyms. BM25 catches the entity; vectors catch semantic intent."* |
| **2:50 - 3:00** | Conclusion & Next Steps | Camera | *"This platform is completely dockerized, comes with automated pytest test suites, and is ready for production deployment with PostgreSQL and pgvector. Thank you!"* |
