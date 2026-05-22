---
phase: 6
slug: mobile-ui-enhancement
status: draft
tool: streamlit-css
created: 2026-05-21
---

# Fase 6 — Mobile UI Enhancement

> Design contract for mobile interface improvements targeting a truly premium feel on smartphones.

**Escopo:** Apenas CSS customizado + modificações pontuais em Python para componentes dinâmicos.
**Não altera:** Estrutura de dados, motor RAG, lógica de negócio, rotas de backend.

---

## 1. Design Tokens (Mobile Overrides)

Todas as variáveis CSS existentes permanecem. Acrescentar estes tokens mobile:

```css
--touch-target-min: 44px;
--mobile-padding-x: 0.75rem;
--mobile-padding-y: 0.5rem;
--mobile-font-size: 0.95rem;
--mobile-card-padding: 0.75rem;
--safe-top: env(safe-area-inset-top, 0px);
--safe-bottom: env(safe-area-inset-bottom, 0px);
```

---

## 2. Breakpoint Strategy

| Breakpoint | Dispositivo | Mudanças |
|------------|-------------|----------|
| < 360px | Phones pequenos | Compacto máximo, fonte reduzida |
| 360–480px | Phones padrão | Alvo principal de design |
| 481–768px | Phones grandes / tablets pequenos | Espaçamento intermediário |
| 769–1024px | Tablets | Grid 2 colunas parcial |
| > 1024px | Desktop | Comportamento atual (inalterado) |

**Regra:** O design mobile é o padrão; media queries `min-width` adicionam complexidade progressiva.

**Foco visual (< 640px):** A barra de navegação inferior é o elemento focal — fixa, sempre visível. Acima dela, o header estabelece identidade visual, seguido pelos cards de métricas como âncora primária de dados. O chat e assistente priorizam legibilidade com fonte aumentada.

---

## 3. Melhorias Específicas

### 3.1 Bottom Navigation Bar

Substituir tabs do topo por uma bottom bar fixa em mobile.

**Implementação:**
```css
@media (max-width: 640px) {
    /* General body text readability */
    p, span, div, label, .stMarkdown {
        line-height: 1.5 !important;
    }
    div[data-testid="stTabs"] {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        z-index: 9999;
        background: white;
        border-top: 1px solid var(--outline-variant);
        padding-bottom: var(--safe-bottom);
        box-shadow: 0 -2px 12px rgba(0,0,0,0.08);
    }
    div[data-testid="stTabs"] div[role="tablist"] {
        display: flex;
        justify-content: space-around;
        align-items: center;
        padding: 0.25rem 0;
        gap: 0;
    }
    div[data-testid="stTabs"] button[role="tab"] {
        font-size: 0.75rem;
        padding: 0.5rem 0.25rem;
        min-width: 0;
        flex: 1;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 4px;
        border-radius: var(--radius-sm);
        background: transparent;
        border: none;
        color: var(--on-surface-variant);
        font-weight: 500;
        min-height: var(--touch-target-min);
    }
    div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
        color: var(--primary);
        background: rgba(0, 168, 89, 0.08);
    }
    /* Add bottom padding to main content to avoid tab overlap */
    .stMainBlockContainer {
        padding-bottom: 72px !important;
    }
}
```

**Comportamento:** Tabs ficam fixas na parte inferior, com ícones emoji + label truncado. A tab ativa ganha destaque com cor primária e fundo sutil.

### 3.2 Sidebar Mobile

Sidebar atualmente ocupa tela inteira em mobile. Melhorar:

```css
@media (max-width: 640px) {
    section[data-testid="stSidebar"] {
        width: 85vw !important;
        max-width: 320px !important;
        transform: translateX(-100%);
        transition: transform 0.3s ease;
        z-index: 10000;
    }
    section[data-testid="stSidebar"][aria-expanded="true"] {
        transform: translateX(0);
    }
    /* Overlay escuro quando sidebar aberta */
    section[data-testid="stSidebar"]::before {
        content: '';
        position: fixed;
        inset: 0;
        background: rgba(0,0,0,0.4);
        z-index: -1;
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    section[data-testid="stSidebar"][aria-expanded="true"]::before {
        opacity: 1;
    }
    section[data-testid="stSidebar"] .stSidebarContent {
        position: relative;
        z-index: 1;
        background: linear-gradient(180deg, #003F20, #007A40);
        height: 100%;
        overflow-y: auto;
    }
}
```

**Nota:** Streamlit não expõe `aria-expanded` de forma direta. Alternativa: usar classe `sidebar-open` no body via `st.markdown` + JS, ou usar seletor CSS baseado na visibilidade do sidebar.

### 3.3 Header Responsivo

Header atual com logo 80px + texto lado a lado. Em mobile, empilhar verticalmente:

```css
@media (max-width: 480px) {
    .app-header-content {
        flex-direction: column;
        align-items: flex-start !important;
        gap: 0.5rem !important;
    }
    .app-header-content > div:first-child {
        flex-direction: column !important;
        align-items: flex-start !important;
        gap: 0.25rem !important;
    }
    .app-header img {
        height: 48px !important;
        max-width: 200px !important;
    }
    .app-title {
        font-size: 1rem !important;
    }
    .app-subtitle {
        font-size: 0.75rem !important;
    }
    /* Greeting badge — smaller */
    .app-header-content > div:last-child {
        font-size: 0.75rem !important;
        padding: 4px 12px !important;
        align-self: flex-start;
    }
}
```

### 3.4 Metric Cards Mobile

Cards do dashboard em grid de 2 colunas em mobile (em vez de 4):

```css
@media (max-width: 480px) {
    .metric-card {
        padding: 0.75rem !important;
    }
    .metric-card-val {
        font-size: 1.6rem !important;
    }
    .metric-card-label {
        font-size: 0.75rem !important;
    }
    /* Forçar 2 colunas nos cards */
    div.row-widget.stColumns > div[data-testid="column"] {
        flex: 0 0 50% !important;
        max-width: 50% !important;
        min-width: 0 !important;
        padding: 4px;
    }
}
```

### 3.5 Chat Bubbles Mobile

```css
@media (max-width: 480px) {
    div[data-testid="stChatMessage"] {
        max-width: 92% !important;
        font-size: 0.85rem !important;
        padding: 0.5rem 0.75rem !important;
        border-radius: 14px !important;
    }
    div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) {
        margin-left: auto !important;
    }
    /* Chat input */
    div[data-testid="stChatInput"] {
        position: sticky;
        bottom: 60px; /* avoid tab bar */
        z-index: 100;
    }
    div[data-testid="stChatInput"] textarea {
        font-size: 0.85rem !important;
        min-height: var(--touch-target-min) !important;
    }
}
```

### 3.6 Forms & Inputs Mobile

```css
@media (max-width: 640px) {
    div[data-testid="stSelectbox"], div[data-testid="stTextInput"],
    div[data-testid="stNumberInput"], div[data-testid="stDateInput"],
    div[data-testid="stMultiselect"], div[data-testid="stFileUploader"] {
        width: 100% !important;
        min-width: 0 !important;
    }
    div[data-testid="stSelectbox"] input, div[data-testid="stTextInput"] input,
    div[data-testid="stNumberInput"] input, div[data-testid="stDateInput"] input {
        min-height: var(--touch-target-min) !important;
        font-size: 0.85rem !important;
    }
    button[kind="secondary"], button[kind="primary"] {
        min-height: var(--touch-target-min) !important;
        font-size: 0.85rem !important;
    }
}
```

### 3.7 Tables & Generated Content Mobile

```css
@media (max-width: 640px) {
    div[data-testid="stTable"], div[data-testid="stDataFrame"] {
        font-size: 0.75rem !important;
        overflow-x: auto !important;
        -webkit-overflow-scrolling: touch;
    }
    /* Generated content cards */
    .app-card {
        padding: 0.75rem !important;
        border-radius: var(--radius-md) !important;
    }
    .app-card h3 {
        font-size: 1rem !important;
    }
    .app-card p {
        font-size: 0.85rem !important;
    }
}
```

### 3.8 Touch Targets

Garantir que todos os elementos interativos tenham no mínimo 44×44px:

```css
@media (max-width: 640px) {
    button, a, select, input, textarea,
    [role="button"], [role="tab"], [role="radio"],
    [role="checkbox"], [data-testid="stExpander"] summary,
    .stDownloadButton button {
        min-height: var(--touch-target-min) !important;
    }
    /* Expander header */
    [data-testid="stExpander"] summary {
        padding: 0.75rem 0.75rem !important;
        font-size: 0.85rem !important;
    }
}
```

### 3.9 Loading & Empty States Mobile

```css
@media (max-width: 640px) {
    div[data-testid="stStatusWidget"] {
        font-size: 0.85rem !important;
        padding: 0.5rem 0.75rem !important;
    }
    div.stSpinner {
        font-size: 0.85rem !important;
    }
}
```

### 3.10 Safe Areas (Notch)

App já injeta `safe-area-inset-top`. Garantir uso completo:

```css
@media (display-mode: standalone) {
    .stApp {
        padding-top: var(--safe-top);
        padding-bottom: var(--safe-bottom);
    }
    /* Quando PWA standalone, tabs não competem com barra do sistema */
    div[data-testid="stTabs"] {
        padding-bottom: calc(0.25rem + var(--safe-bottom));
    }
}
```

---

## 4. Animações e Micro-interações

```css
/* Mobile-specific page transitions */
@media (max-width: 640px) {
    .stTabs, .stMainBlockContainer {
        animation: fadeSlideIn 0.25s ease-out;
    }
    @keyframes fadeSlideIn {
        from { opacity: 0; transform: translateY(8px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    /* Button press feedback */
    button:active {
        transform: scale(0.97);
    }
}
```

---

## 5. Anti-padrões (o que NÃO fazer)

| Anti-padrão | Motivo |
|-------------|--------|
| Esconder sidebar permanentemente | Sidebar contém filtros essenciais |
| Font-size < 14px em body text | Prejudica legibilidade. Exceção: labels de navegação (tabs) podem ser menores |
| Hover-only interactions | Não funciona em touch |
| Modais muito grandes | Cobrem conteúdo em tela pequena |
| Overflow horizontal | Causa scroll horizontal indesejado |
| Fixed elements sem safe-area | Cobrem notch/home indicator |
| Ausência de line-height em body text | Dificulta leitura em telas pequenas |

**Line-height recomendado:** `1.5` para body text mobile (fontes 0.75rem–0.85rem), `1.3` para headings (1rem+).

---

## 6. Critérios de Aceitação

1. **Bottom nav** funciona em mobile: 4 tabs visíveis, rolagem horizontal NÃO é necessária
2. **Header** empilha verticalmente em < 480px sem quebrar layout
3. **Sidebar** em mobile não ocupa mais que 85% da largura da tela
4. **Cards** do dashboard exibem em grid 2×2 em mobile
5. **Chat** bubbles têm cantos arredondados e padding adequados
6. **Touch targets** mínimos de 44px em todos elementos interativos
7. **Safe areas** são respeitadas (testar em PWA standalone)
8. **Navegação** não causa scroll horizontal ou zoom indesejado
9. **Tabelas** de conteúdo gerado roláveis horizontalmente sem quebrar layout
10. **Nenhum conteúdo** fica oculto atrás da bottom nav

---

## 7. Riscos e Mitigações

| Risco | Mitigação |
|-------|-----------|
| Streamlit não permite bottom tabs facilmente | Usar `position: fixed` + z-index no container das tabs. Se não funcionar, recuar para tabs no topo com scroll horizontal |
| Safe-area-inset não funciona em alguns browsers | Fallback para 0px via `env()` com fall chain |
| Sidebar com `transform` conflita com Streamlit internals | Testar em mobile real; alternativa: `width: 85vw !important` sem animação |
| Bottom nav sobrepõe chat input | Adicionar `padding-bottom: 70px` ao `stChatInput` container |

---

## 8. Checklist de Verificação

- [ ] Bottom tab bar fixa com espaçamento safe-area
- [ ] Tabs com ícone + label, tab ativa destacada
- [ ] Conteúdo principal com padding-bottom para não ficar atrás das tabs
- [ ] Header empilhado verticalmente em < 480px
- [ ] Sidebar com overlay e largura responsiva em mobile
- [ ] Dashboard cards em grid 2×2 no mobile
- [ ] Chat bubbles com padding e tamanho adequado
- [ ] Chat input sticky com espaço para bottom nav
- [ ] Inputs full-width com touch targets 44px+
- [ ] Botões primários full-width em mobile
- [ ] Tabelas com overflow-x scroll em mobile
- [ ] Safe areas aplicadas (PWA standalone)
- [ ] Animações fadeSlideIn em transições mobile
- [ ] Touch feedback (scale on press)
- [ ] Nenhum hover-only interaction
- [ ] Testing em 3 resoluções: 375px, 414px, 768px
