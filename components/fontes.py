"""Componentes de exibição de fontes e renderização de markdown."""

import streamlit as st
from markdown_it import MarkdownIt

_md = MarkdownIt()


def render_markdown_with_copy(markdown_text, key, label="📋 Copiar Markdown"):
    """Render markdown content with a copyable code block.
    
    Shows rendered markdown in a styled card, then a code block
    with Streamlit's native copy button (clipboard icon top-right).
    """
    st.markdown(
        f'<div class="app-card" style="margin-bottom: 0.5rem;">'
        f'{_md.render(markdown_text)}'
        f'</div>',
        unsafe_allow_html=True,
    )
    with st.expander(f"📋 {label} — clique para ver e copiar o texto", expanded=False):
        st.code(markdown_text, language="markdown")


def exibir_fontes(fontes: list[dict]):
    seen = set()
    chips_html = []
    for f in fontes:
        label = f.get("arquivo") or f.get("url") or f.get("perfil") or f.get("fonte", "?")
        if len(label) > 25:
            label = label[:22] + "..."
        chave = (label, f["fonte"])
        if chave not in seen:
            seen.add(chave)
            tipo = f["fonte"].lower()
            badge_class = f"app-badge app-badge-{tipo}"
            chips_html.append(
                f'<span class="{badge_class}">'
                f'{label}'
                f'</span>'
            )
            
    if chips_html:
        st.markdown(
            f'<div style="margin-top: 8px; margin-bottom: 12px; display: flex; flex-wrap: wrap; align-items: center;">'
            f'<span style="font-size: 0.8rem; color: var(--on-surface-variant); margin-right: 8px; font-weight: 600;">📚 Fontes citadas:</span>'
            f'{"".join(chips_html)}'
            f'</div>',
            unsafe_allow_html=True
        )
