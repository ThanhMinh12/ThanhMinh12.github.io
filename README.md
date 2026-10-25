# Thanh Bui Minh

Personal portfolio: <https://thanhminh12.github.io/>

A white portfolio with grouped, left-aligned experience entries and project descriptions
beside real application screenshots and demo/source links. Built with HTML, CSS,
and small, dependency-free JavaScript enhancements: active section navigation
and keyboard-accessible image previews. Reduced-motion preferences are respected;
all content and links remain usable without JavaScript. No build step is needed.
Source Sans 3 is self-hosted under its bundled SIL Open Font License.

GitHub Pages publishes the root of the `main` branch. To preview locally:

```bash
python3 -m http.server 4317
```

Browser regression checks (requires Python Playwright and its Chromium browser):

```bash
python scripts/smoke_ui.py --url http://127.0.0.1:4317
```

Detour has a temporary AWS preview. Fretwork and SceneSeek run their React/FastAPI
stacks on existing free Hugging Face Spaces; GPU queues and quotas apply, and
uploaded files expire after an hour. Screenshots show the real application UIs.
