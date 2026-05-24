import streamlit as st
from utils.documentos import _get_collection as _get_docs_collection
from components import render_upload_tab


def render():
    st.markdown('<div class="animate-in">', unsafe_allow_html=True)
    st.markdown(
        '<div class="app-card" style="margin-bottom: 2rem;">'
        '<h2 style="margin:0; color: var(--primary);">📊 Visão Geral do Painel</h2>'
        '<p style="color: var(--on-surface-variant); margin-top: 0.5rem; font-size: 0.95rem;">'
        'Acompanhe o status da sua base de conhecimento e as atividades recentes.</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    try:
        collection = _get_docs_collection()
        total_chunks = collection.count()
    except Exception:
        total_chunks = 0

    total_perguntas = len([m for m in st.session_state.mensagens if m["role"] == "user"])
    total_calendarios = st.session_state.get("calendarios_gerados", 0)
    total_campanhas = st.session_state.get("campanhas_geradas", 0)
    total_conteudos = total_calendarios + total_campanhas + len(st.session_state.legendas_geradas)
    total_fontes = len(st.session_state.documentos)

    col1, col2, col3, col4 = st.columns(4)
    col1.markdown(
        f'<div class="metric-card metric-green animate-in" style="animation-delay: 0.1s;">'
        f'<div class="metric-card-label">📁 Fontes Ativas</div>'
        f'<div class="metric-card-val">{total_fontes}</div>'
        f'<div style="font-size: 0.75rem; color: var(--primary); font-weight: 700;">↑ Pronto para consulta</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
    col2.markdown(
        f'<div class="metric-card metric-blue animate-in" style="animation-delay: 0.15s;">'
        f'<div class="metric-card-label">📄 Fragmentos (RAG)</div>'
        f'<div class="metric-card-val">{total_chunks}</div>'
        f'<div style="font-size: 0.75rem; color: var(--secondary); font-weight: 700;">Conhecimento indexado</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
    col3.markdown(
        f'<div class="metric-card metric-yellow animate-in" style="animation-delay: 0.2s;">'
        f'<div class="metric-card-label">💬 Interações</div>'
        f'<div class="metric-card-val">{total_perguntas}</div>'
        f'<div style="font-size: 0.75rem; color: var(--tertiary-dark); font-weight: 700;">Perguntas respondidas</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
    col4.markdown(
        f'<div class="metric-card metric-red animate-in" style="animation-delay: 0.25s;">'
        f'<div class="metric-card-label">✨ Ativos Criados</div>'
        f'<div class="metric-card-val">{total_conteudos}</div>'
        f'<div style="font-size: 0.75rem; color: var(--danger); font-weight: 700;">Conteúdos gerados</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # Os gráficos de distribuição foram removidos pois não refletiam dados reais.
    # Futuramente, substituir por visualizações baseadas em dados do RAG.

    if st.session_state.documentos:
        st.markdown(
            '<h3 style="margin-bottom:1rem; margin-top: 2rem; color: var(--on-surface);">📂 Fontes carregadas</h3>',
            unsafe_allow_html=True,
        )
        cols = st.columns(2)
        icones = {"pdf": "📄", "url": "🔗", "html": "🌐", "instagram": "📷", "texto": "📝", "planilha": "📊"}
        for i, chave in enumerate(st.session_state.documentos):
            meta = st.session_state.documentos_meta.get(chave)
            if meta:
                fonte = meta["fonte"]
                nome = meta.get("nome", chave)
                icone = icones.get(fonte, "📄")
                extra = ""
                if "paginas" in meta:
                    extra = f" · {meta['paginas']} páginas"
                elif "posts" in meta:
                    extra = f" · {meta['posts']} posts"
                elif "url" in meta:
                    extra = f" · URL"
                cols[i % 2].markdown(
                    f'<div class="app-card animate-in" style="animation-delay: {0.4 + i*0.05}s; padding:1rem 1.25rem; margin: 0.5rem 0;">'
                    f'<strong style="color: var(--on-surface);">{icone} {nome}</strong><br>'
                    f'<small style="color:var(--on-surface-variant); font-size: 0.8rem;">'
                    f'{meta.get("chunks", "?")} trechos · {meta.get("caracteres", 0):,} caracteres{extra}'
                    f'</small></div>',
                    unsafe_allow_html=True,
                )
            else:
                cols[i % 2].markdown(f"- {chave}")
    else:
        st.markdown(
            '<div class="app-card-empty animate-in" style="animation-delay: 0.4s; padding: 3.5rem 1.5rem; text-align: center; border-radius: var(--radius-lg); border: 2px dashed var(--outline-variant); background: var(--card-bg); margin: 1.5rem 0;">'
            '<div style="font-size: 4rem; margin-bottom: 1rem; display: inline-block;">📚</div>'
            '<h3 style="color: var(--on-surface); margin-top: 0.5rem; margin-bottom: 0.5rem; font-weight:700;">Nenhuma fonte carregada</h3>'
            '<p style="color: var(--on-surface-variant); font-size: 0.95rem; margin: 0;">'
            'Use a barra lateral para adicionar PDFs, URLs, HTMLs, perfis de Instagram, textos ou planilhas e comece a analisar!'
            '</p>'
            '</div>',
            unsafe_allow_html=True,
        )

    st.markdown(
        '<div class="app-card animate-in" style="animation-delay: 0.45s; padding:1rem 1.25rem; margin-top: 2rem;">'
        '<div style="display:flex;gap:0.75rem;align-items:center;flex-wrap:wrap;">'
        '<span style="font-size:1.5rem;">💡</span>'
        '<span style="font-size:0.9rem;color:var(--on-surface-variant);">'
        'Explore as abas <strong>💬 Chat</strong> para interagir com seus documentos, '
        '<strong>📅 Calendário</strong> para organizar suas ações mensais, '
        '<strong>📢 Campanhas</strong> para criar estratégias completas, '
        'ou <strong>📸 Legendas</strong> para gerar conteúdo visual para o Instagram.'
        '</span></div></div>',
        unsafe_allow_html=True,
    )

    st.divider()
    with st.expander("📂 Adicionar fonte (dispositivos móveis)", expanded=False):
        st.markdown(
            "*No computador, use a barra lateral. Aqui você também pode adicionar fontes.*"
        )
        aba_mobile = st.radio("Tipo", ["PDF", "URL", "HTML", "Instagram", "Texto", "Planilha"], key="mobile_aba")
        render_upload_tab(st, aba_mobile, key_prefix="mob_")
    st.markdown('</div>', unsafe_allow_html=True)
