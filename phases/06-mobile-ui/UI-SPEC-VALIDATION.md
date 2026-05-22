# UI-SPEC Validation Report

**Phase:** 6 — Mobile UI Enhancement  
**Spec:** `phases/06-mobile-ui/UI-SPEC.md`  
**Codebase:** `app.py`  
**Date:** 2026-05-22  
**Reviewer:** GSD UI Checker

---

## Dimension Results

| # | Dimension | Verdict | Summary |
|---|-----------|---------|---------|
| 1 | Copywriting | **PASS** | No new user-facing text introduced; pure CSS enhancement spec |
| 2 | Visuals | **FLAG** | Focal point implied but not explicitly declared |
| 3 | Color | **PASS** | Reuses existing CSS variable system; no new accent declarations |
| 4 | Typography | **FLAG** | 9 distinct font-size values across component overrides |
| 5 | Spacing | **BLOCK** | Non-multiple-of-4 values: 70px, 2px gap, 0.875rem (14px) |
| 6 | Registry Safety | **PASS** | No third-party registries; pure Streamlit CSS |

**Status: ⚠️ BLOCKED** (Dimension 5 must be resolved before planning)

---

## Dimension 1 — Copywriting: PASS

**Question:** Are all user-facing text elements specific and actionable?

**Result:** PASS — No new user-facing text is introduced by this spec.

**Evidence:**
- UI-SPEC.md Section 1-8 is entirely CSS/styling overrides — no CTAs, labels, empty states, or error copy are defined.
- All buttons, messages, and content text are inherited from the existing `app.py` codebase (e.g., tab labels at line 1964, button texts at line 1940).
- The spec follows its declared scope: *"Apenas CSS customizado + modificações pontuais em Python para componentes dinâmicos"*.

**Recommendation (non-blocking):** None.

---

## Dimension 2 — Visuals: FLAG

**Question:** Are focal points and visual hierarchy declared?

**Result:** FLAG — Visual hierarchy is implied structurally but not explicitly declared.

**Evidence:**
- **Bottom nav** (Section 3.1) is positioned `fixed` at bottom with `z-index: 9999` and the active tab gains `--primary` color — this structurally *implies* it's the primary navigation focal point.
- **Metric cards** (Section 3.4) get a 2×2 grid treatment on mobile — visually prominent.
- **Primary buttons** (Section 3.6) become `width: 100%` in mobile — full-width emphasis.
- **However**, nowhere does the spec explicitly state: *"The visual focal point on the primary screen is the bottom navigation bar"* or declare a deliberate visual hierarchy (what draws the eye first? the metric cards summary? the header branding? the bottom nav?).

**Fix Recommendation (non-blocking):**
Add a one-line statement in Section 2 (Breakpoint Strategy) or Section 3 preamble:
> *"On mobile (< 640px), the visual focal point is the bottom navigation bar. Below it, the header establishes brand identity, followed by metric cards as the primary data anchor on the Dashboard tab."*

---

## Dimension 3 — Color: PASS

**Question:** Is the color contract specific enough to prevent accent overuse?

**Result:** PASS — No new color tokens defined; reuses existing CSS variable system conservatively.

**Evidence:**
- Section 3.1 uses `var(--primary)` (line 92) only for the **active tab highlight** and its subtle background `rgba(0, 168, 89, 0.08)` (line 93).
- Section 3.2 uses a green gradient `linear-gradient(180deg, #003F20, #007A40)` for sidebar background — this is a decorative background, not an accent.
- No new accent colors are declared.
- The existing `app.py` CSS already defines `--primary: #00A859` (line 25) and uses it sparingly.
- Destructive actions exist in the codebase (e.g., "Limpar tudo" / "Sim, apagar tudo" at lines 1938–1940) but they pre-date this spec and are styled with `type="primary"` (green) — a pre-existing design decision.

**Recommendation (non-blocking):** None.

---

## Dimension 4 — Typography: FLAG

**Question:** Is the type scale constrained enough to prevent visual noise?

**Result:** FLAG — More than 4 distinct font-size values across component overrides, though these are responsive adjustments.

**Evidence:**
The spec declares these distinct `font-size` values across different components (at 16px base):

| Value | Renders to | Context |
|-------|-----------|---------|
| 0.65rem | ~10.4px | Tab labels (Section 3.1) |
| 0.7rem | ~11.2px | Metric-card label (Section 3.4) |
| 0.75rem | ~12px | Tables/dataframes, subtitle (Sections 3.3, 3.7) |
| 0.8rem | ~12.8px | Status widget, spinner, card `<p>` (Sections 3.7, 3.9) |
| 0.85rem | ~13.6px | Chat messages, buttons, expander (Sections 3.5, 3.6, 3.8) |
| 0.9rem | ~14.4px | Chat input, form inputs (Sections 3.5, 3.6) |
| 0.95rem | ~15.2px | Card `<h3>`, mobile font baseline (Section 3.7) |
| 1.1rem | ~17.6px | App title (Section 3.3) |
| 1.6rem | ~25.6px | Metric-card value (Section 3.4) |

Count: **9 distinct font sizes** — well over the 4-size limit.

**Justification for FLAG (not BLOCK):**
These are **component-specific responsive overrides**, not a typographic scale definition. The existing type system (Inter font, base 14px at line 18 of app.py CSS, `--font-size-sm: 0.875rem` etc.) remains unchanged. Each component override serves a distinct purpose (ensuring legibility on small screens). However, the sheer number of distinct sizes creates maintainability risk.

**Recommendation (non-blocking):**
Consolidate where possible: group similar sizes (e.g., unify inputs/chat-input at 0.9rem with buttons at 0.85rem; or unify metric-label at 0.7rem with table text at 0.75rem).

---

## Dimension 5 — Spacing: ⛔ BLOCK

**Question:** Does the spacing scale maintain grid alignment?

**Result:** BLOCK — Non-multiple-of-4 spacing values present.

**Evidence:**

1. **`padding-bottom: 70px !important`** (Section 3.1, line 97)  
   `70 ÷ 4 = 17.5` — **NOT a multiple of 4.**  
   Context: Bottom padding on main block container to prevent content from hiding behind the fixed bottom tab bar.

2. **`gap: 2px`** (Section 3.1, line 83)  
   `2 ÷ 4 = 0.5` — **NOT a multiple of 4.**  
   Context: Gap between tab icon emoji and label in the bottom nav bar.

3. **`--mobile-card-padding: 0.875rem`** (Section 1, line 27)  
   At 16px base: `0.875 × 16 = 14px`. `14 ÷ 4 = 3.5` — **NOT a multiple of 4.**  
   Context: Design token for card padding on mobile.

4. **`padding: 0.625rem 0.75rem`** (Section 3.8, line 290)  
   At 16px base: `0.625 × 16 = 10px`. `10 ÷ 4 = 2.5` — **NOT a multiple of 4.**  
   Context: Expander header padding on mobile.

**Required Fixes:**
- Replace `70px` → `72px` (multiple of 4; 18 × 4 = 72) or `68px` (17 × 4 = 68).  
  72px is recommended as it accommodates the 44px touch target + 28px padding/decoration overhead.
- Replace `gap: 2px` → `gap: 4px` (multiple of 4).
- Replace `--mobile-card-padding: 0.875rem` → `--mobile-card-padding: 0.75rem` (12px) or `1rem` (16px).
- Replace `0.625rem` → `0.5rem` (8px) or `0.75rem` (12px) for expander padding.

**Severity:** BLOCK — Spacing alignment breaks the 4px grid system. Planning cannot proceed until values are corrected.

---

## Dimension 6 — Registry Safety: PASS

**Question:** Are third-party component sources actually vetted?

**Result:** PASS — No third-party registries involved.

**Evidence:**
- UI-SPEC.md declares `tool: streamlit-css` in frontmatter and uses only inline CSS overrides on Streamlit's built-in components (`st.tabs`, `st.chat_message`, `st.columns`, `st.sidebar`, etc.).
- No shadcn/ui, magic-ui, or any external component registry is referenced.
- No npm packages or CDN scripts are introduced.

**Note:** The spec's Section 3.1 bottom-tab approach uses `position: fixed` + `z-index: 9999` on Streamlit's native `st.tabs` — this is a pure CSS technique, not a third-party component.

**Recommendation (non-blocking):** None.

---

## Summary of Required Fixes

### BLOCKING (must fix before planning)

| # | Dimension | Location | Issue | Fix |
|---|-----------|----------|-------|-----|
| B1 | Spacing | Section 3.1, line 97 | `padding-bottom: 70px` (not multiple of 4) | Change to `72px` or `68px` |
| B2 | Spacing | Section 3.1, line 83 | `gap: 2px` (not multiple of 4) | Change to `4px` |
| B3 | Spacing | Section 1, line 27 | `--mobile-card-padding: 0.875rem` → 14px (not multiple of 4) | Change to `0.75rem` (12px) or `1rem` (16px) |
| B4 | Spacing | Section 3.8, line 290 | `padding: 0.625rem` → 10px (not multiple of 4) | Change to `0.5rem` (8px) or `0.75rem` (12px) |

### Recommendations (non-blocking flags)

| # | Dimension | Location | Recommendation |
|---|-----------|----------|---------------|
| F1 | Visuals | Section 3 preamble | Add explicit focal point declaration |
| F2 | Typography | Sections 3.3–3.9 | Consolidate font sizes to ≤4 distinct values |

---

## Verification Checklist

- [x] All required reading loaded before analysis (UI-SPEC.md, app.py)
- [x] All 6 dimensions evaluated
- [x] BLOCK verdicts have exact fix descriptions
- [x] FLAG verdicts have recommendations
- [x] Evidence cited with specific section/line references
- [x] No modifications made to UI-SPEC.md (read-only review)

---

## Next Steps

1. Researcher applies the 4 spacing fixes in UI-SPEC.md
2. Optionally addresses the font-size consolidation and focal point declaration
3. Re-run `/gsd-ui-phase` for re-verification
4. Once approved, planning phase can proceed
