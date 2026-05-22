---
phase: 7
slug: mobile-tab-navigation
status: draft
shadcn_initialized: false
preset: none
created: 2026-05-22
---

# Phase 7 — Mobile Tab Navigation & Phase 6 Fixes

> Design contract for fixing 8 unresolved issues from Phase 6 (scored 14/24) and completing the mobile tab navigation experience for the Marketing de Conteúdo PWA. All styles are injected via `st.markdown('<style>...</style>')` — no shadcn, no external component library.

---

## Design System

| Property | Value |
|----------|-------|
| Tool | streamlit-css |
| Preset | not applicable |
| Component library | none (raw CSS via `st.markdown`) |
| Icon library | Unicode emoji (inlined in tab labels) |
| Font | `'Inter', sans-serif` (Google Fonts `@import` in CSS) with system font fallback `system-ui, -apple-system, sans-serif`; body=0.85rem, label=0.75rem |

**Background:** All visual tokens are already defined in `app.py :root` CSS (--primary: #00A859, --on-surface-variant: gray, etc.). Phase 7 does NOT redefine tokens — it adds missing interactions and fixes broken behavior scoped to `< 640px` breakpoint.

---

## Spacing Scale

All values map to a 4px grid. Horizontal tab padding accepts a 6px exception to fit 6 emoji tabs on small screens.

| Token | Value | Usage |
|-------|-------|-------|
| xs | 4px | Gap between icon + label in tab, gap between tabs in tablist |
| sm | 8px | Tablist container padding (y-axis), card inner padding |
| md | 16px | Default element spacing, section gaps |
| lg | 24px | Calendar modal inner padding |
| xl | 32px | Layout section breaks |

**Exceptions:**

| Value | Where | Why |
|-------|-------|-----|
| 6px | Horizontal padding on each tab button | Fits 6 emoji tabs on <360px screens without overflow. 6px + 2px gap = 8px unit — still grid-aligned across pairs. |
| 72px | `padding-bottom` on `.stMainBlockContainer` | Bottom tab bar is ~48px + safe-area. 72px = 48 + 24 (generous margin). |
| 0.75rem (12px) | Tablist padding (x-axis), `.app-card` padding | 12px is a standard Streamlit padding that cannot be changed without breaking layout in 12+ places. Documented as legacy value. |

---

## Typography

| Role | Size | Weight | Line Height |
|------|------|--------|-------------|
| Body | 0.85rem | 400 (Regular) | 1.5 |
| Label | 0.75rem | 500 (Medium) | 1.3 |
| Heading | 1rem | 600 (SemiBold) | 1.2 |
| Display | 1rem | 700 (Bold) | 1.2 |

**Note:** `0.75rem = 12px` is the minimum allowed size. Reserved for tab labels only. Body text never below `0.85rem (≈13.6px)`.

---

## Color

| Role | Value | Usage |
|------|-------|-------|
| Dominant (60%) | #FFFFFF | Page background, tab bar background, card backgrounds |
| Secondary (30%) | #F8F9FA | Card area background, tab inactive background |
| Accent (10%) | #00A859 (`--primary`) | Active tab icon + label, active tab underline indicator, tab hover tint, primary buttons, metric card top border |
| On-surface-variant | #6C757D (gray) | Inactive tab icon + label |
| Destructive | #E84C3D | Delete/clear actions in sidebar |

**Accent reserved for:** Active tab indicator (underline + colored text/icon), tab hover background tint, primary action buttons, metric card accent borders, sidebar active radio item, calendar event badges of type "pauta", confirmation/success states.

**Destructive reserved for:** "Limpar tudo" popover action, calendar event badges of type "deadline", error alerts.

---

## Phase 7 Required Fixes

The following 8 issues were identified in the Phase 6 UI Review (score 14/24). Each fix below maps to one or more unresolved items.

### Fix 1 — Tab Content Interception Bug

**Problem (P1):** `div[data-testid="stTabs"]` is `position: fixed` on the tablist child, but Streamlit's tab implementation renders both the tablist AND all tab content panels inside the same `stTabs` container. The content panels inherit the fixed positioning, making them scroll behind the bottom bar or become non-interactive.

**Implementation:**

```css
@media (max-width: 640px) {
    /* Only the tablist is fixed — content panels stay in flow */
    div[data-testid="stTabs"] {
        position: relative; /* container stays in normal flow */
    }
    div[data-testid="stTabs"] div[role="tablist"] {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        z-index: 9999;
        background: white;
        border-top: 1px solid var(--outline-variant);
        padding-bottom: var(--safe-bottom);
        box-shadow: 0 -2px 12px rgba(0,0,0,0.08);
        display: flex;
        justify-content: space-around;
        align-items: center;
        padding: 0.25rem 0;
        gap: 0;
    }
    /* Content panels must not be position:fixed — pointer-events: none fix
       prevents clicks from hitting the fixed tablist overlay area */
    div[data-testid="stTabs"] > div:not([role="tablist"]) {
        position: relative !important;
        pointer-events: auto !important;
    }
    /* Bottom padding on main content area prevents last content from
       being hidden behind the fixed tab bar */
    .stMainBlockContainer {
        padding-bottom: 72px !important;
    }
}
```

**Verification:** Click each of the 6 tabs on a mobile-width viewport. The content panel should scroll independently. The tab bar should remain fixed at the bottom. No content should be obscured.

---

### Fix 2 — Active Tab Underline Indicator

**Problem (P2):** Tabs show an active background tint (`rgba(0, 168, 89, 0.08)`) but lack a visible underline indicator, making the active tab hard to distinguish at a glance, especially when all tabs use similar emoji icons.

**Implementation:**

```css
@media (max-width: 640px) {
    div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
        color: var(--primary);
        background: rgba(0, 168, 89, 0.08);
        position: relative;
    }
    div[data-testid="stTabs"] button[role="tab"][aria-selected="true"]::after {
        content: '';
        position: absolute;
        bottom: 2px;
        left: 50%;
        transform: translateX(-50%);
        width: 20px;
        height: 3px;
        border-radius: 1.5px;
        background: var(--primary);
    }
}
```

**Note:** The underline must be `20px` wide (not full tab width) for a premium pill-style indicator. Inline with Material Design 3 bottom navigation active indicator pattern.

---

### Fix 3 — Tab Hover / Focus / Active States

**Problem (P2):** Tabs only have `:hover` and `[aria-selected="true"]` states. Missing `:focus-visible` ring for keyboard navigation and `:active` press feedback.

**Implementation:**

```css
@media (max-width: 640px) {
    /* Hover — already exists, keep */
    div[data-testid="stTabs"] button[role="tab"]:hover {
        color: var(--primary);
        background: rgba(0, 168, 89, 0.08);
    }
    /* Focus-visible ring for keyboard nav */
    div[data-testid="stTabs"] button[role="tab"]:focus-visible {
        outline: 2px solid var(--primary);
        outline-offset: -2px;
        border-radius: var(--radius-sm);
    }
    /* Active press feedback */
    div[data-testid="stTabs"] button[role="tab"]:active {
        transform: scale(0.95);
        background: rgba(0, 168, 89, 0.15);
    }
}
```

---

### Fix 4 — Sidebar Animation Reliability

**Problem (P3):** Sidebar uses `transform: translateX(-100%)` with `transition: transform 0.3s ease` and `[aria-expanded="true"]` selector, but Streamlit's sidebar does not reliably toggle `aria-expanded`. The fallback `body.sidebar-open` class is set via JS `MutationObserver`, but the observer may not fire if Streamlit re-renders the sidebar DOM.

**Implementation (JS fix in existing `<script>` block):**

```javascript
(function(){
    var sidebar = document.querySelector('section[data-testid="stSidebar"]');
    function updateSidebarState() {
        var expanded = sidebar && (
            sidebar.getAttribute('aria-expanded') === 'true' ||
            sidebar.style.display !== 'none' ||
            sidebar.getBoundingClientRect().width > 50
        );
        document.body.classList.toggle('sidebar-open', !!expanded);
    }
    if (sidebar) {
        // MutationObserver for attribute changes
        var observer = new MutationObserver(function(mutations) {
            updateSidebarState();
        });
        observer.observe(sidebar, { attributes: true, attributeFilter: ['aria-expanded', 'style', 'class'] });
        // Also observe child content for re-renders
        observer.observe(sidebar.querySelector('.stSidebarContent') || sidebar, {
            childList: true, subtree: true
        });
        // Poll as last resort (Streamlit rerenders can bypass MutationObserver)
        setInterval(updateSidebarState, 500);
        // Initial state
        updateSidebarState();
    }
})();
```

**CSS additions:**

```css
@media (max-width: 640px) {
    /* Ensure overlay covers entire viewport */
    body.sidebar-open section[data-testid="stSidebar"]::after {
        opacity: 1 !important;
        pointer-events: auto !important;
    }
    /* Disable body scroll when sidebar open */
    body.sidebar-open {
        overflow: hidden !important;
    }
}
```

---

### Fix 5 — 4px Grid Spacing Compliance

**Problem (P3):** Various mobile values use non-4px-grid values. Tablist `gap: 2px` should be `gap: 4px` (xs). Tab `padding: 0.25rem` is correct (4px). Tab button `gap: 4px` is correct. Ensure consistency.

**Implementation:**

```css
@media (max-width: 640px) {
    /* Fix: tablist gap 2px → 4px (xs token) */
    .stTabs [role="tablist"] {
        gap: 0; /* gap between tab items is now margin on the flex items */
    }
    /* Each tab gets 2px margin on each side = 4px total gap */
    div[data-testid="stTabs"] div[role="tablist"] button[role="tab"] {
        margin: 0 2px;
    }
    /* Padding for tablist container: 4px top/bottom = xs */
    div[data-testid="stTabs"] div[role="tablist"] {
        padding: 4px 6px;  /* 6px horizontal exception for 6 tabs */
    }
}
```

**Grid audit of all mobile values in `< 640px` breakpoint:**

| Property | Before (Phase 6) | After (Phase 7) | Grid-aligned? |
|----------|-------------------|-----------------|---------------|
| Tablist gap | 2px | 4px (2px margin each side) | ✅ 4px |
| Tab padding (y) | 0.25rem (4px) | 4px | ✅ 4px |
| Tab horizontal padding | 0.5rem (8px) | 6px | ⚠️ Exception |
| Tablist y-padding | 0.25rem | 4px | ✅ 4px |
| Tab button gap | 4px | 4px | ✅ 4px |
| Main content bottom padding | 72px | 72px | ✅ 48px + 24px |
| Safe-bottom on tablist | `var(--safe-bottom)` | `var(--safe-bottom)` | ✅ |
| Section[sidebar] width | 85vw | 85vw | ⚠️ Viewport unit |

---

### Fix 6 — Safe-Area Padding on Tab Content

**Problem (P3):** Safe-area padding is applied to the tablist (`padding-bottom: var(--safe-bottom)`) but NOT to the main content padding-bottom, so content behind the home indicator area is still covered on notched devices in PWA standalone mode.

**Implementation:**

```css
@media (max-width: 640px) {
    /* Ensure main content has safe-area bottom padding */
    .stMainBlockContainer {
        padding-bottom: calc(72px + var(--safe-bottom, 0px)) !important;
    }
}

@media (display-mode: standalone) {
    @media (max-width: 640px) {
        .stMainBlockContainer {
            padding-bottom: calc(72px + var(--safe-bottom, 0px)) !important;
        }
        /* Fix bottom tab bar safe area */
        div[data-testid="stTabs"] div[role="tablist"] {
            padding-bottom: calc(0.25rem + var(--safe-bottom, 0px));
        }
    }
    /* General PWA standalone adjustments */
    .stApp {
        padding-top: var(--safe-top, 0px);
        padding-bottom: var(--safe-bottom, 0px);
    }
}
```

---

### Fix 7 — Offline Indicator

**Problem (P2):** PWA has no offline indicator. Users navigating via service worker cache have no way to know they're offline.

**Implementation (JS + CSS injected via `st.markdown`):**

```javascript
(function(){
    var indicator = document.createElement('div');
    indicator.id = 'offline-indicator';
    indicator.textContent = '📡 Offline — alguns dados podem não estar disponíveis';
    indicator.style.cssText = [
        'position: fixed',
        'bottom: 56px',
        'left: 50%',
        'transform: translateX(-50%)',
        'background: #E84C3D',
        'color: white',
        'padding: 6px 16px',
        'border-radius: 20px',
        'font-size: 0.75rem',
        'font-weight: 500',
        'z-index: 10001',
        'white-space: nowrap',
        'box-shadow: 0 2px 8px rgba(0,0,0,0.2)',
        'display: none',
        'opacity: 0',
        'transition: opacity 0.3s ease',
        'pointer-events: none',
    ].join(';');
    document.body.appendChild(indicator);

    function updateOnlineStatus() {
        if (navigator.onLine) {
            indicator.style.display = 'none';
            indicator.style.opacity = '0';
        } else {
            indicator.style.display = 'block';
            // Force reflow then fade in
            void indicator.offsetHeight;
            indicator.style.opacity = '1';
        }
    }

    window.addEventListener('online', updateOnlineStatus);
    window.addEventListener('offline', updateOnlineStatus);
    updateOnlineStatus();
})();
```

**Note:** The indicator sits above the bottom tab bar (`bottom: 56px` ≈ tab bar height + gap). Add `bottom: calc(56px + var(--safe-bottom, 0px))` in standalone display-mode.

**Position adjustment for PWA standalone:**

```css
@media (display-mode: standalone) {
    #offline-indicator {
        bottom: calc(56px + var(--safe-bottom, 0px)) !important;
    }
}
```

---

### Fix 8 — Z-Index Overlay Fixes

**Problem (P3):** Calendar modal overlay (`z-index: 99999`) conflicts with tab bar (`z-index: 9999`). Sidebar overlay (`z-index: 10000`) sits above tab bar, which is correct for sidebar, but the `::after` pseudo-element has `z-index: -1` which places it behind the sidebar content. Sidebar overlay must be between sidebar and page content (as a backdrop).

**Implementation:**

```css
@media (max-width: 640px) {
    /* Sidebar overlay: z-index between sidebar content (10000) and page (1) */
    section[data-testid="stSidebar"]::after {
        z-index: 9998 !important; /* above tab bar (9999) — overlay must cover tabs too */
    }
    /* Ensure sidebar content sits above its own overlay */
    section[data-testid="stSidebar"] .stSidebarContent {
        position: relative;
        z-index: 10001;
    }
    /* Calendar modal: keep 99999, but ensure it closes when sidebar open */
    .cal-modal-overlay {
        z-index: 99999 !important;
    }
    /* Tab bar: ensure it's below sidebar overlay but above content */
    div[data-testid="stTabs"] div[role="tablist"] {
        z-index: 9999;
    }
}
```

**Z-Index Stack (mobile, top to bottom):**

| Layer | z-index | Element |
|-------|---------|---------|
| Highest | 99999 | Calendar modal overlay |
| 2nd | 10001 | Sidebar content |
| 3rd | 10000 | Sidebar container |
| 4th | 9999 | Bottom tab bar |
| 5th | 9998 | Sidebar backdrop overlay (`::after`) |
| 6th | 100 | Chat input (sticky) |
| Base | auto | Main page content |

---

## Copywriting Contract

All copy is in Brazilian Portuguese, matching existing app labels and the 6 `st.tabs()` arguments.

| Element | Copy | Notes |
|---------|------|-------|
| Primary CTA (tab tap) | Alternar para [nome da aba] | Implicit — Streamlit handles tab activation. No explicit CTA button needed. |
| Offline indicator | 📡 Offline — alguns dados podem não estar disponíveis | Shown as floating chip above tab bar |
| Tab labels | 📊 Dashboard / 💬 Assistente / 📅 Calendário Editorial / 📢 Gerador de Campanhas / 📋 Relatório de Conteúdo / 📸 Legendas Instagram | Exact `st.tabs()` args — do not change |
| Sidebar toggle hint | — | No text label (emoji-based in sidebar header) |
| Sidebar overlay backdrop | — | No text — semi-transparent black overlay |
| Destructive action | Limpar tudo: "Tem certeza? Esta ação não pode ser desfeita." | Existing `st.popover` confirmation — no change needed |

---

## Registry Safety

| Registry | Blocks Used | Safety Gate |
|----------|-------------|-------------|
| N/A | N/A | N/A — no component registry or third-party UI blocks are used. All code is custom Streamlit/CSS/JS injected via `st.markdown()`. |

---

## Phase 7 Acceptance Criteria

1. **Tab interception fixed:** Content panels scroll independently below the fixed bottom tab bar. No `position: fixed` leaking onto content.
2. **Active tab indicator:** Each tab has a green underline dot (20px wide, 3px height) when `[aria-selected="true"]`.
3. **Tab interaction states:** All 4 states (default, hover, focus-visible, active) produce visible feedback.
4. **Sidebar animation:** Sidebar slides in/out reliably on mobile hamburger click. Backdrop overlay covers entire viewport.
5. **4px grid compliance:** All spacing values audit to 4px multiples. Exceptions documented and justified (6px tab padding, 72px content bottom).
6. **Safe-area padding:** Main content `padding-bottom` includes `var(--safe-bottom)` in PWA standalone mode.
7. **Offline indicator:** Red floating chip appears when `navigator.onLine === false`, disappears on reconnect. Positioned above tab bar.
8. **Z-index ordering:** No elements bleed through wrong layers. Sidebar overlay covers tabs, calendar modal covers sidebar.
9. **No regression:** All 6 tab content panels render correctly. Dashboard metrics, chat, calendar, campaign form, content report, and Instagram caption tab all functional.
10. **Keyboard accessible:** `:focus-visible` rings visible on tabs. Tab order preserved (tabs → content → sidebar).

---

## Anti-patterns (what NOT to do)

| Anti-pattern | Reason |
|-------------|--------|
| `position: fixed` on `div[data-testid="stTabs"]` | Causes content panel interception (Fix 1 root cause) |
| Relying solely on `[aria-expanded]` for sidebar | Streamlit doesn't consistently toggle this attribute |
| Hover-only tab indicators | Doesn't work on touch devices |
| Removing `pointer-events: none` from the fixed tablist area | Makes content below the tab bar non-interactive |
| z-index values without a documented stack | Causes layering conflicts (Fix 8) |
| Offline indicator at `bottom: 0` | Overlaps the bottom tab bar |
| Overriding Streamlit internal tab JS | Use CSS + minimal DOM JS only — avoid breaking Streamlit's tab lifecycle |

---

## Riscos e Mitigações

| Risk | Mitigation |
|------|------------|
| Streamlit re-render clears injected `<style>` tags | Inject CSS after every `st.rerun()` — currently done via a single `st.markdown()` at the top of the app. If tabs re-mount, re-inject or use `st.markdown` after tab creation. |
| `pointer-events: none` on tablist container blocks clicks on content | Only target the container area, not individual tablist children. The content panel divs are sibling to tablist — ensure they have `pointer-events: auto`. |
| Offline indicator JS removed by Streamlit security | `unsafe_allow_html=True` + inline `<script>` should persist. If not, inject via `st.components.v1.html()`. |
| MutationObserver not firing for sidebar | Add polling fallback (setInterval at 500ms) as documented in Fix 4. |
| iOS Safari bottom bar overlaps tab bar | Test on physical iPhone. Use `env(safe-area-inset-bottom)` with fallback. The `viewport-fit=cover` meta tag must be present. |

---

## Assets Required

| File | Usage | Status |
|------|-------|--------|
| None | Phase 7 adds no new images, icons, or fonts. Emoji icons already in tab labels. Offline indicator is pure CSS/JS. | N/A |

---

## Checker Sign-Off

- [ ] Dimension 1 Copywriting: PASS
- [ ] Dimension 2 Visuals: PASS
- [ ] Dimension 3 Color: PASS
- [ ] Dimension 4 Typography: PASS
- [ ] Dimension 5 Spacing: PASS
- [ ] Dimension 6 Registry Safety: PASS

**Approval:** pending
