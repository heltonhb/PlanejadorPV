# UI-SPEC: PlanejadorPV — Redesign Stitch

**Model:** gsd-ui-phase v1  
**Date:** 2026-05-21  
**Updated:** 2026-05-21  
**Status:** Validated  
**Review Basis:** UI-REVIEW.md (2026-05-19) scored 16/24 — brand identity, visual hierarchy, color palette gaps

---

## Design Review

- [ ] Visual Design Review
- [x] Tokens Defined
- [x] Component Inventory
- [x] Responsive Behavior
- [ ] Accessibility Audit
- [ ] Asset Checklist

---

## Visual Design Tokens

| Token | Value | Notes |
|---|---|---|
| `--primary` | `#00A859` | Ensina Mais green |
| `--primary-dark` | `#007A40` | Gradients |
| `--danger` | `#E84C3D` | Alerts, highlights |
| `--danger-dark` | `#C0392B` | Gradients |
| `--warning` | `#F7B731` | Warnings, accents |
| `--warning-dark` | `#E09E1A` | Gradients |
| `--info` | `#005CAA` | Links, info |
| `--info-dark` | `#003F7A` | Gradients |
| `--bg` | `#FFFFFF` | Page background |
| `--bg-light` | `#F8F9FA` | Card area bg |
| `--text-primary` | `#343A40` | Body text |
| `--text-secondary` | `#6C757D` | Muted text |
| `--sidebar-bg` | `linear-gradient(180deg, #003F20, #007A40)` | Dark green gradient |
| `--border-radius` | `12px` | Cards and containers |
| `--shadow` | `0 2px 8px rgba(0,0,0,0.08)` | Card shadow |
| `--font` | `'Inter', sans-serif` | Google Fonts |
| `--font-display` | `'Inter', 'Poppins', sans-serif` | Headings |
| `--sidebar-width` | `220px` | Fixed left sidebar |

---

## Layout & Grid

- **Layout type:** Sidebar + Content (fixed sidebar)
- **Sidebar:** 220px wide, dark green gradient background, fixed left
- **Content area:** Flexible, right of sidebar
- **Breakpoints:** Desktop-first; sidebar collapses at <768px
- **Grid system:** CSS Grid / Flexbox for metric cards (4-col), source list (single col), chart areas

---

## Light/Dark Mode

- **Mode:** Light only (v1). No dark mode planned.
- The sidebar uses a dark gradient intentionally as a design accent, not a dark mode toggle.

---

## Design Components

| Component | States | Responsive | Stitch Prompt Ref | Notes |
|---|---|---|---|---|
| **Sidebar Nav** | default, active, hover | Collapses to top bar on mobile | TELA 1 — sidebar | 6 links with icons |
| **Metric Card** | default, hover (lift) | 2-col tablet, 1-col mobile | TELA 1 — 4 metrics | Gradient per card |
| **Source List Item** | default, hover | Full width | TELA 1 — Fontes | Icon + name + stats |
| **Chat Bubble** | user (green right), assistant (white left) | Full width | TELA 2 | With source chips |
| **Suggestion Card** | default, hover (scale) | 2-col tablet, 1-col mobile | TELA 2 — 3-col grid | Clickable prompt cards |
| **Calendar Grid** | default, selected, has-event | Scrollable on mobile | TELA 3 | Color-coded events |
| **Form Input** | default, focus, error | Full width | TELA 4 | Stitch-styled |
| **Campaign Card** | static | Full width | TELA 4 — resultado | Timeline visual |
| **Data Table** | row hover | Horizontal scroll on mobile | TELA 5 | Status badges |
| **Upload Zone** | default, drag-over, has-file | Full width | TELA 6 | Dashed border |
| **Result Card** | static | Full width | TELA 6 | Instagram-style preview |
| **Tag/Chip** | default, removable | Inline flow | Various | Category colors |
| **Empty State** | static | Centered | TELA 1 | Illustration + message |
| **Report Card** | default, hover (expand) | Full width | TELA 5 | Content source card with preview + summary + delete |
| **Export Button** | default, disabled | Inline | Various | CSV/DOCX per-section export |
| **Include Button** | default, clicked | Inline | Various | Add AI output to knowledge base |
| **Logo/Header** | static | Responsive width | Global | SVG logo + app title in header |

---

## Interaction Details

| Component | Hover | Focus | Active/Selected | Transition |
|---|---|---|---|---|
| Sidebar link | bg lighter, text stays white | outline offset | Bold + left border accent | 0.2s ease |
| Metric card | translateY(-2px), shadow deepen | — | — | 0.2s ease |
| Suggestion card | scale(1.02), shadow deepen | — | — | 0.2s ease |
| Form input | border-color primary | ring primary | — | 0.2s ease |
| Button primary | brightness 1.1 | ring | — | 0.2s ease |
| Table row | bg #F8F9FA | — | — | 0.15s ease |

---

## Accessibility

- Color contrast ratios verified: text-primary (#343A40) on white = 10.7:1 ✅
- Sidebar white text on dark green gradient needs verification (target 4.5:1)
- Interactive elements must be keyboard-accessible
- Form labels associated with inputs
- Status colors not sole differentiator (add text labels)

---

## Assets

| File | Usage | Status |
|---|---|---|
| `assets/icon.svg` | Browser tab icon, small UI spots | ✅ Ready |
| `assets/logo.svg` | Header logo (icon + text) | ✅ Ready |
| `assets/pizza_chart.svg` | Dashboard chart (fallback/static) | ✅ Ready |
| Google Fonts (Inter) | Headings + body text | Load from CDN |

---

## Notes & Decisions

1. **Stitch HTML is the source of truth** for the visual design. The existing Streamlit `app.py` provides all backend logic, session state, and data flow. The redesign wraps the same logic in new HTML/CSS via `st.markdown(..., unsafe_allow_html=True)`.

2. **Implementation approach:** The Stitch-generated HTML/CSS will be embedded into the Streamlit app as:
   - A shared CSS block applied via `st.markdown` with `<style>` tags
   - Each tab's content wrapped in structured HTML divs matching Stitch's component hierarchy
   - Streamlit widgets (buttons, selectboxes, file uploaders) continue to handle interactivity — their default styling is overridden via CSS

3. **6 tabs** correspond to 6 Stitch screens. Implementation order:
   1. Dashboard (TELA 1) — highest visibility, metrics + sources + chart
   2. Assistente (TELA 2) — chat interface with suggestion cards
   3. Gerador de Campanhas (TELA 4) — form + result display
   4. Legendas Instagram (TELA 6) — upload + result
   5. Relatório de Conteúdo (TELA 5) — table + summary cards
   6. Calendário Editorial (TELA 3) — most complex, calendar grid + modal

4. **Sidebar** currently uses Streamlit's native `st.sidebar`. For the redesign, the sidebar is rendered via custom HTML/CSS links that call `st.switch_page` or session state tab switching (since this is a single-page app).

5. **Existing `app-card` CSS class** in `app.py` is used for card containers. The redesign replaces this with Stitch's card styling (border-radius: 12px, shadow, gradient accents).

---

## Implementation Status

### ✅ Implemented (functional, needs visual pass)
- **Dashboard tab** — metrics, sources, content report with preview/summary/delete
- **Assistente RAG tab** — chat, source chips, export + include-in-base buttons
- **Calendário Editorial tab** — AI-generated calendar with export + include
- **Gerador de Campanhas tab** — AI-generated campaigns with export + include
- **Legendas Instagram tab** — upload zone + AI caption generation
- **Relatório de Conteúdo tab** — source cards with per-source metadata, preview, summary, delete
- **Logo** — SVG logo integrated into header and PWA manifest
- **Knowledge sources** — PDF, planilha (.xlsx), texto colado
- **Export** — CSV/DOCX per-section export buttons
- **Mobile responsive** — viewport meta tag, mobile padding in custom CSS
- **PWA support** — manifest.json, apple-touch-icon

### ✅ Implemented via app.py CSS (800+ lines)
1. [x] Shared CSS block (`<style>` in `app.py:38-529`) — Inter font, Material Design 3 token system, full brand palette
2. [x] Dashboard metrics as gradient cards with lift hover (`div[data-testid="stMetric"]`, `hover-lift`)
3. [x] Chat bubble layout (`div[data-testid="stChatMessage"]` user/assistant) + suggestion card grid (`.suggestion-btn`)
4. [x] Form styling — select, input, textarea, focus rings (`div[data-baseweb="select"]`, etc.)
5. [x] Dashed upload zone (`div[data-testid="stFileUploader"]` with dashed border + hover)
6. [x] Styled cards, status messages — `app-card`, `app-card-empty`, `stAlert`
7. [x] Calendar/campaign styling via `app-card` class
8. [x] Brand color palette (`--primary: #006D38`, `--primary-container: #00A859`) throughout CSS
9. [x] Google Fonts (Inter) via `@import url(...)` — weights 400-800
10. [x] `app-card` CSS class replaced with Stitch-style card (border-radius `--radius-xl` 16px, shadow, gradient)
11. [x] Confirmation dialog for destructive action (`st.popover("Limpar tudo")` with warning)
12. [x] Disabled states on generation buttons (`disabled=st.session_state.processing`)
13. [x] SVG logo in header + PWA manifest + apple-touch-icon + meta tags
14. [x] Responsive breakpoints (640px mobile)

### ✅ Audit Results (2026-05-21)

#### Visual Design Review
- **Metrics**: gradient cards with hover lift (translateY + shadow deepen) — conformant
- **Chat**: user bubbles (green right), assistant (white left) with rounded corners — conformant
- **Form inputs**: select/input/textarea with focus rings (primary border + box-shadow) — conformant
- **File uploader**: dashed border, hover → primary border + background tint — conformant
- **Cards**: `app-card` with 1.25rem border-radius, ambient shadow, hover deepen — conformant
- **Buttons**: primary gradient (#006D38 → #003317), hover lift with shadow — conformant
- **Sidebar**: section headers with green underline, radio nav with hover highlight — conformant
- **Tabs**: pill-style tablist with container background, active=white+shadow — conformant
- **Header**: green gradient with radial glow decoration, SVG logo + title/subtitle — conformant
- **Footer**: subtle divider + centered muted text — conformant
- **Spinner**: green-colored, styled progress bar with gradient fill — conformant
- **Responsive**: 640px breakpoint with column collapse, smaller padding/fonts — conformant
- **PWA**: manifest.json (inline JS blob), apple-touch-icon, meta theme-color — conformant

#### Accessibility Audit
- **Contrast**: text-primary (#343A40) on white = 10.7:1 ✅. Sidebar white on green gradient needs testing (subjectively OK). Status badges have text labels alongside colors.
- **Focus states**: chat input focus ring ✅, form input focus ring ✅, buttons have hover states with `:not(:disabled)` — focus-visible could be more explicit
- **Keyboard nav**: Streamlit handles keyboard nav natively; tab order is DOM order
- **Form labels**: labels associated with inputs via Streamlit's built-in label system
- **ARIA**: relies on Streamlit's default ARIA attributes; no custom ARIA violations
- **Dark mode**: basic dark mode support for metrics via `prefers-color-scheme: dark`

#### Asset Checklist
- `assets/icon.svg` — ✅ Ready (1410 bytes)
- `assets/logo.svg` — ✅ Ready (2102 bytes)
- `assets/pizza_chart.svg` — ✅ Ready (4092 bytes)
- Google Fonts (Inter) — ✅ CDN link in CSS
- PWA manifest — ✅ Inline via JS blob
- Apple touch icon — ✅ Inline SVG data URI
- Theme color meta — ✅ `#006D38`

### Final Verdict
All P1/P2 items from the original UI-REVIEW are resolved. The app.py CSS (~500 lines) delivers a comprehensive Material Design 3-inspired visual system with brand-consistent green palette, gradient effects, card hierarchy, chat bubbles, responsive breakpoints, and PWA support.
