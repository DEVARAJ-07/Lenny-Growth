# Artifact Generation Skill

## Philosophy & Safety Model

When a user asks for dashboards, code snippets, visual calculators, comparison tables, or standalone documents:

### 1. Output Format
- Generate complete, self-contained Markdown or modern HTML/CSS.
- For HTML: include inline CSS (using modern clean aesthetics matching the dark MindMerge theme: `#0F1117` background, `#1A1D24` cards, `#FF6B35` highlights).
- Self-contained: No external CDN fonts, scripts, or network fetches.

### 2. Security Restrictions (Strict Sandboxing)
- Untrusted execution model: Artifacts are rendered inside an `iframe` with `sandbox="allow-scripts"` and strictly **NO `allow-same-origin`**.
- Content Security Policy (CSP):
  `default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:;`
- Never execute parent document navigation, cookie access, or network calls.
