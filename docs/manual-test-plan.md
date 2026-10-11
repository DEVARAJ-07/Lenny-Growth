# Manual Test Plan: The Lenny Growth Assistant

This manual test plan guides evaluators through verifying all core capabilities, safety boundaries, local LLM execution, 3D graphics, and sandboxed artifacts.

---

## 🎯 Test Environment Setup

1. **Start Local Ollama**:
   ```powershell
   powershell -File scripts/start-ollama.ps1
   ```
   Ensure models are active: `ollama list` (`qwen2.5:3b`, `deepseek-r1:1.5b`, `llama3.2:3b`, `nomic-embed-text:latest`).

2. **Start Backend**:
   ```powershell
   uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload
   ```

3. **Start Frontend**:
   ```powershell
   cd frontend
   npm run dev
   ```
   Navigate to `http://localhost:5173`.

---

## 📋 Test Matrix

| ID | Feature / Flow | Test Input / Action | Expected Result | Pass/Fail |
|---|---|---|---|---|
| **TC-01** | Grounded Q&A | *"What does Adam Fishman say about onboarding?"* | Responds with tactical onboarding insights citing Adam Fishman, episode title, and timestamp markers (e.g. `[00:49:51]`). | [ ] |
| **TC-02** | Zero Hallucination Refusal | *"How do I bake a chocolate cake?"* | System immediately triggers refusal template: *"I searched through Lenny's 300+ podcast transcripts, but this topic is not covered in the episodes."* Zero speculative tokens. | [ ] |
| **TC-03** | Ship 30 for 30 Atomic Essay | *"Write a Ship 30 essay on product-market fit"* | Generates structured essay with Irresistible Hook headline, skimmable H2 subheadings, bullet points, operator citations, and Monday morning checklist. Toast displays verified score. | [ ] |
| **TC-04** | Interactive Artifact Sandbox | *"Create an interactive retention calculator in HTML"* | Response embeds code tabs (`[HTML] [CSS] [JS]`) and displays an artifact pill. Clicking "View Sandbox" opens the slide-out viewer with live interactive calculator inside a secure iframe. | [ ] |
| **TC-05** | Model Switching (DeepSeek Reasoning) | Select **DeepSeek R1** pill and submit *"How should growth leaders evaluate virality?"* | Assistant displays collapsible **Reasoning Process** accordion containing `<think>` tokens, followed by grounded response. | [ ] |
| **TC-06** | 3D Neural Canvas & Parallax | Move cursor across the screen | Central 3D geometric core smoothly tilts with cursor via mouse parallax. Hovering slightly expands the core. Framerate remains locked at 60 FPS. | [ ] |
| **TC-07** | History Drawer & Session CRUD | Click "+", ask a question, delete a session, click "Clear history" | New session is created with first 6 words as title. Deleting removes the session. "Clear history" clears the drawer and resets state. | [ ] |
| **TC-08** | Sandbox Security Verification | Inspect sandbox iframe element in DevTools | `sandbox="allow-scripts"` is present; `allow-same-origin` is omitted. Cookies and parent DOM are inaccessible from the iframe. | [ ] |

---

## 🔍 Detailed Test Scripts

### Scenario 1: Grounded Citations Verification
1. Open chat workspace.
2. Ensure model is set to **Qwen 2.5 3B** (fast local model).
3. In the input box, type:
   > *"What does Adam Fishman say about growth loops and onboarding?"*
4. Press Enter.
5. **Observe**:
   - Response streams in real-time.
   - Assistant card displays a **Grounded Citations (Verified Sources)** accordion.
   - Expanding citations reveals guest name "Adam Fishman", episode title, and clickable/viewable timestamp badges (e.g., `[00:36:53]`).

### Scenario 2: Out-of-Scope Query Refusal
1. In the input box, type:
   > *"What is the best recipe for baking chocolate chip cookies?"*
2. Press Enter.
3. **Observe**:
   - Zero hallucination trigger: system recognizes query falls outside podcast scope.
   - Refusal message states: *"I searched through Lenny's 300+ podcast transcripts, but this topic is not covered in the episodes."*
   - No hallucinated recipe or outside knowledge is returned.

### Scenario 3: Ship 30 for 30 Essay Generation
1. In the input box, type:
   > *"Write a Ship 30 essay on finding product-market fit."*
2. Press Enter.
3. **Observe**:
   - Orchestrator classifies intent as `ship30`.
   - Generates headline with a bold hook.
   - Structured H2 subheadings with short paragraphs.
   - Operator citations referencing Lenny's guests.
   - Ends with an actionable Monday-morning checklist.
   - Toast notification reports verified validation score.

### Scenario 4: Sandboxed Artifact Viewer
1. In the input box, type:
   > *"Create an interactive retention calculator in HTML with custom sliders."*
2. Press Enter.
3. **Observe**:
   - Assistant card outputs self-contained HTML/CSS.
   - "View Sandbox" pill appears in the card.
   - Clicking opens the slide-out Claude-style panel.
   - "Preview" tab renders interactive sliders and calculations.
   - "Source Code" tab shows raw syntax.
   - "Copy" and "Download" buttons function properly.
