# Design Specification (design.md)
## The Lenny Growth Assistant UI/UX Architecture

**Document Version:** 2.0.0  
**Design Paradigm:** Warm Sandal & Espresso Dark Brown Palette with Claude AI Simplicity and 3D Tactile Depth  

---

## 1. UI/UX Principles & Aesthetic Philosophy

1. **Warm Sandal Canvas & Dark Espresso Sidebar:** 
   The interface embraces a refined organic color palette:
   - **Main Chat Workspace:** Warm Sandal gradient (`#FAF5ED` to `#EFE6D8`) delivering high legibility and visual comfort for extended strategy reading.
   - **Navigation Sidebar:** Rich Dark Sandal & Espresso Brown (`#241A14` to `#1C130E`) providing grounding contrast and structural hierarchy.
   - **Recent Chats Hover:** Dark Brown (`#3E271B`) with crisp high-contrast warm cream text (`#FFFDF8`) for clear mouse tracking and responsive visual feedback.
2. **Contextual Continuity (Claude-style Artifacts & File Previews):**
   - Attached files (PDFs, Markdown, text files) display as native thumbnail cards directly inside the composer.
   - Interactive HTML/CSS artifacts slide open into an isolated, sandboxed side-drawer with CSP protection, preserving conversation flow.
3. **Wider, Stretchable 3D Spatial Frame:**
   The application container stretches dynamically (`max-w-[98vw] 2xl:max-w-[1720px] h-[96vh]`) with layered perspective shadows (`shadow-[0_28px_65px_rgba(28,19,14,0.4),0_0_35px_rgba(179,107,57,0.15)]`), creating an expansive, tactile 3D workstation.
4. **Transparent Source Grounding:**
   Every generated response attributes facts directly to Lenny's 300+ podcast transcripts with guest name and exact episode timestamp markers (e.g., `Elena Verna (00:00:26)`, `Adam Fishman (00:14:22)`).

---

## 2. Information Architecture & Layout Grid

```
+--------------------------------------------------------------------------------------------------------------+
|  EXPANSIVE 3D WORKSPACE CONTAINER (Width: up to 98vw / 1720px, Height: 96vh, Border: #4A3527)                 |
|                                                                                                              |
|  +--------------------+  +---------------------------------------------------------------------------------+ |
|  | LEFT SIDEBAR       |  | MAIN CHAT WORKSPACE (Sandal Gradient: #FAF5ED -> #EFE6D8)                       | |
|  | (Dark Sandal-Brown |  |                                                                                 | |
|  |  #241A14, 280px)   |  | - Header: Sidebar Toggle, "Free plan · Upgrade" pill, Info & Docs button        | |
|  |                    |  |                                                                                 | |
|  | - Brand:           |  | - Blank State (New Chat):                                                       | |
|  |   ✻ The Lenny      |  |   * Hero Greeting: "✻ Good morning / afternoon / evening, Sir"                 | |
|  |     Growth         |  |   * Centered Sandal Composer Card (#FAF7F2, 3D border & shadow)                 | |
|  |     Assistant      |  |                                                                                 | |
|  | - + Start new chat |  | - Active Conversation:                                                          | |
|  | - Recent chats     |  |   * User Bubble (right-aligned, cream card #FAF6F0)                             | |
|  |   (Dark brown hover|  |   * Assistant Bubble (left-aligned, warm sandal #F7F2EB)                        | |
|  |    #3E271B, high   |  |   * DeepSeek Reasoning Accordion (<think> step-by-step CoT)                     | |
|  |    contrast text)  |  |   * Verbatim Podcast Timestamp Citations                                        | |
|  | - Settings Button  |  |   * Bottom Docked Composer with Model Switcher & 3D Send Button                 | |
|  | - User Profile:    |  |                                                                                 | |
|  |   "S Sir · Free"   |  |                                                                                 | |
|  +--------------------+  +---------------------------------------------------------------------------------+ |
|                                                                                                              |
|  +---------------------------------------------------------------------------------------------------------+ |
|  | SLIDE-OUT ARTIFACT VIEWER (50% Split Drawer when active)                                                | |
|  | - Sandboxed iframe with strict Content-Security-Policy (CSP) & DOMPurify                                 | |
|  | - Code vs. Live Render tabs, Copy Code, Download buttons                                                | |
|  +---------------------------------------------------------------------------------------------------------+ |
+--------------------------------------------------------------------------------------------------------------+
```

---

## 3. Key Interaction States & Component Specs

### 3.1 Time-of-Day Greeting (Sir)
* Dynamic system greeting evaluating local client hours:
  * 05:00 – 11:59: `✻ Good morning, Sir`
  * 12:00 – 16:59: `✻ Good afternoon, Sir`
  * 17:00 – 04:59: `✻ Good evening, Sir`
* Profile pill at the bottom of the sidebar displays initial avatar `S` with username `Sir`.

### 3.2 In-Composer Model Selector
* Clean Model Toggle popover located on the right side of the composer toolbar.
* Displays clean model names with no redundant drafting or speed tags:
  1. **Qwen 2.5 3B** (Default local GPU)
  2. **DeepSeek R1** (Local reasoning with `<think>` tags)
  3. **Llama 3.2 3B** (Local drafting)
  4. **Sonnet 3.7** (Frontier cloud provider)

### 3.3 3D Tactile Send Button
* Layered terracotta-to-amber gradient (`from-[#9B4518] via-[#B85721] to-[#D47135]`).
* Dual-stage shadow: `shadow-[0_4px_12px_rgba(155,69,24,0.35),inset_0_1px_1px_rgba(255,255,255,0.4)]`.
* Hover elevation (`scale-105`) with smooth arrow nudge up, active depression (`scale-90`) with inner shadow.

### 3.4 Settings Page
* Clean, non-distracting modal opened from the sidebar "Settings" button.
* **Available Models & Architecture**: Non-selectable informative cards detailing each model's one-liner purpose.
* **Plan Settings**: Displays active plan tier with direct "Upgrade Plan" CTA opening the $10 / $20 / $50 Pro Plans modal.

### 3.5 Pro Plans Modal ($10 / $20 / $50)
* **Free ($0)**: Local GPU acceleration on RTX 2050 (Qwen, DeepSeek R1, Llama 3.2), full transcripts RAG.
* **Pro ($10/mo)**: Claude 3.7 Sonnet cloud queries, sandboxed HTML artifacts, high-priority GPU queue.
* **Team ($20/mo/seat)**: S3 team knowledge base, shared transcript annotations, team Supabase schema.
* **Enterprise / Paid Schema ($50/mo)**: Dedicated Supabase schema, automated S3 bucket sync, real-time token tracking tables.

---

## 4. Accessibility & Contrast Verification
* **Background to Text Contrast:** All Sandal text maintains WCAG AA compliant ratios (Dark Brown `#251A13` on Sandal `#FAF5ED` achieves `12.4:1`).
* **Sidebar Hover Contrast:** Hovering over recent chats shifts background to `#3E271B` with text at `#FFFDF8` (`14.1:1` contrast ratio).
* **Keyboard Navigation:** Full support for `Enter` to send, `Shift+Enter` for multi-line inputs, and `Escape` to close modals.
