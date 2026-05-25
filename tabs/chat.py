import streamlit as st
from utils.ia_engine import perguntar
from utils.ingestao import processar_texto
from utils.perguntas_sugeridas import PERGUNTAS_SUGERIDAS
from utils.exportacao import exportar_markdown_docx
from components.fontes import exibir_fontes


def render():
    st.markdown('<div class="animate-in">', unsafe_allow_html=True)
    col_titulo, col_limpar = st.columns([0.85, 0.15])
    with col_titulo:
        st.markdown(
            '<div class="app-card" style="margin-bottom: 2rem;">'
            '<h2 style="margin:0; color: var(--primary);">💬 Assistente de Marketing</h2>'
            '<p style="color: var(--on-surface-variant); margin-top: 0.5rem; font-size: 0.95rem;">'
            'Carregue informações na barra lateral e faça perguntas sobre o conteúdo para gerar insights e materiais.</p>'
            '</div>',
            unsafe_allow_html=True,
        )
    with col_limpar:
        if st.session_state.mensagens:
            if st.button("🗑️ Limpar conversa", use_container_width=True, help="Apaga todo o histórico da conversa atual."):
                st.session_state.mensagens = []
                st.session_state.sugestoes_usadas = False
                st.rerun()

    if not st.session_state.mensagens and not st.session_state.sugestoes_usadas:
        with st.container(border=False):
            st.markdown(
                '<h3 style="margin-bottom:0.75rem; color: var(--on-surface);">💡 Sugestões de perguntas</h3>'
                '<p style="color:var(--on-surface-variant);margin:0 0 1.5rem 0; font-size: 0.95rem;">'
                'Clique em uma pergunta abaixo para começar uma conversa:</p>',
                unsafe_allow_html=True,
            )

            for idx_cat, grupo in enumerate(PERGUNTAS_SUGERIDAS):
                st.markdown(
                    f'<h4 style="margin-top: 1.75rem; margin-bottom: 0.75rem; '
                    f'color: var(--primary-light); font-size: 0.95rem; font-weight: 600;">'
                    f'{grupo["categoria"]}</h4>',
                    unsafe_allow_html=True,
                )
                cols = st.columns(3)
                for i, pergunta in enumerate(grupo["perguntas"]):
                    with cols[i % 3]:
                        if st.button(
                            pergunta, key=f"sugestao_{idx_cat}_{i}",
                            use_container_width=True,
                        ):
                            st.session_state.sugestoes_usadas = True
                            st.session_state.mensagens.append({"role": "user", "content": pergunta})
                            with st.chat_message("user"):
                                st.markdown(pergunta)
                            with st.chat_message("assistant"):
                                with st.spinner("Consultando fontes..."):
                                    resultado = perguntar(pergunta)
                                st.markdown(resultado["resposta"], unsafe_allow_html=True)
                                if resultado["fontes"]:
                                    exibir_fontes(resultado["fontes"])
                            st.session_state.mensagens.append({
                                "role": "assistant", "content": resultado["resposta"],
                                "fontes": resultado["fontes"],
                            })
                            st.rerun()

    for i, msg in enumerate(st.session_state.mensagens):
        with st.chat_message(msg["role"]):
            st.markdown(f'<div class="animate-in" style="animation-delay: {0.1 + i*0.05}s;">{msg["content"]}</div>', unsafe_allow_html=True)
            if msg["role"] == "assistant" and msg.get("fontes"):
                exibir_fontes(msg["fontes"])
            if msg["role"] == "assistant" and i == len(st.session_state.mensagens) - 1:
                col_exp, col_base = st.columns(2)
                with col_exp:
                    docx_bytes = exportar_markdown_docx(msg["content"])
                    st.download_button(
                        "📥 Baixar DOCX",
                        data=docx_bytes,
                        file_name="resposta_assistente.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True,
                        key=f"exp_msg_{i}",
                    )
                with col_base:
                    if st.button("📚 Incluir na base", key=f"inc_msg_{i}", use_container_width=True):
                        with st.spinner("Adicionando à base de conhecimento..."):
                            proc = processar_texto(
                                msg["content"],
                                titulo=f"Resposta do assistente #{i}",
                            )
                        if proc["status"] == "ok":
                            st.success(f"✅ Adicionado ({proc['total_chunks']} trechos).")
                        else:
                            st.error(f"❌ {proc['mensagem']}")
                with st.expander("📋 Copiar resposta — clique para ver e copiar o texto", expanded=False):
                    st.code(msg["content"], language="markdown")

    if prompt := st.chat_input("Faça uma pergunta sobre os documentos..."):
        st.session_state.mensagens.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(f'<div class="animate-in">{prompt}</div>', unsafe_allow_html=True)

        with st.chat_message("assistant"):
            with st.spinner("Consultando fontes..."):
                resultado = perguntar(prompt)
            st.markdown(f'<div class="animate-in">{resultado["resposta"]}</div>', unsafe_allow_html=True)
            if resultado["fontes"]:
                exibir_fontes(resultado["fontes"])
        st.session_state.mensagens.append({
            "role": "assistant", "content": resultado["resposta"],
            "fontes": resultado["fontes"],
        })
    st.markdown('</div>', unsafe_allow_html=True)
