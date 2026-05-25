import re
import streamlit as st
from utils.campanhas import gerar_campanha, OBJETIVOS, PUBLICOS, SERVICOS
from components.cards import render_campaign_result_card
from components.fontes import render_markdown_with_copy


def _sanitizar(texto: str) -> str:
    """Remove tags HTML que o Gemini insiste em gerar."""
    texto = re.sub(r'<[^>]*>', '', texto)
    texto = re.sub(r'\n{3,}', '\n\n', texto)
    return texto


def render():
    st.markdown('<div class="animate-in">', unsafe_allow_html=True)
    st.markdown(
        '<div class="app-card" style="margin-bottom: 2rem;">'
        '<h2 style="margin:0; color: var(--primary);">📢 Gerador de Campanhas</h2>'
        '<p style="color: var(--on-surface-variant); margin-top: 0.5rem; font-size: 0.95rem;">'
        'Crie uma campanha de marketing completa para a unidade Tatuapé.</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    with st.container(border=False):
        st.markdown('<div class="app-card" style="margin-bottom: 1.5rem;">', unsafe_allow_html=True)
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            nome_campanha = st.text_input("Nome da Campanha (opcional)", placeholder="Ex: Campanha Volta às Aulas 2026")
            objetivo = st.selectbox("Objetivo da campanha", OBJETIVOS)
            publico = st.selectbox("Público-alvo", PUBLICOS)
        with col_c2:
            servico = st.selectbox("Serviço", SERVICOS)
            orcamento = st.number_input("Orçamento Estimado (R$)", min_value=0.0, step=100.0, value=0.0)
            datas = st.text_input("Período / Datas planejadas", placeholder="Ex: De 01/06 a 30/06")
        
        canais = st.multiselect(
            "Canais de divulgação preferenciais",
            ["Instagram", "Facebook", "E-mail", "WhatsApp", "SMS", "Google Ads", "Material Impresso"],
            default=["Instagram", "WhatsApp", "Material Impresso"]
        )

        if st.button("Gerar Campanha", type="primary", use_container_width=True, disabled=st.session_state.processing):
            st.session_state.processing = True
            progress = st.progress(0, text="Iniciando criação da campanha...")
            progress.progress(25, text="Analisando objetivos...")
            resultado = gerar_campanha(
                objetivo, publico, servico,
                nome=nome_campanha, canais=canais, orcamento=orcamento, datas=datas
            )
            progress.progress(75, text="Montando estrutura da campanha...")
            progress.progress(100, text="Concluído!")
            progress.empty()
            if resultado["status"] == "ok":
                st.session_state.campanhas_geradas += 1
                st.session_state.ultima_campanha = _sanitizar(resultado["conteudo"])
                st.session_state.ultima_campanha_contexto = resultado.get("contexto_usado", False)
                st.session_state.dados_ultima_campanha = {
                    "nome": nome_campanha,
                    "objetivo": objetivo,
                    "publico": publico,
                    "servico": servico,
                    "orcamento": orcamento,
                    "canais": canais,
                    "datas": datas
                }
                st.toast("Campanha gerada com sucesso!")
            else:
                st.error(f"❌ Não foi possível gerar a campanha: {resultado['mensagem']}")
            st.session_state.processing = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # Display generated campaign if available
    _conteudo = st.session_state.get("ultima_campanha") or ""
    if not isinstance(_conteudo, str):
        _conteudo = ""
    # Sanitizar HTML residual de cache anterior ao fix
    _conteudo = _sanitizar(_conteudo)
    if _conteudo:
        st.divider()
        st.markdown(
            '<div class="app-card" style="margin-top: 2rem;">'
            '<h3 style="margin-top:0; color: var(--primary);">📝 Detalhes da Campanha</h3>'
            '</div>',
            unsafe_allow_html=True,
        )
        
        dados = st.session_state.get("dados_ultima_campanha", {})
        ctx_usado = st.session_state.get("ultima_campanha_contexto", False)
        
        if ctx_usado:
            st.success("✅ Campanha personalizada com base nas suas fontes carregadas.")
        else:
            st.info("📚 Nenhuma fonte carregada — campanha baseada em conhecimento geral.")

        if dados:
            card_html = render_campaign_result_card(
                nome=dados.get("nome", ""),
                objetivo=dados.get("objetivo", ""),
                publico=dados.get("publico", ""),
                servico=dados.get("servico", ""),
                orcamento=dados.get("orcamento", 0.0),
                canais=dados.get("canais", []),
                datas=dados.get("datas", "")
            )
            st.markdown(card_html, unsafe_allow_html=True)
            
        render_markdown_with_copy(
            _conteudo,
            key="camp_copy",
            label="Copiar Campanha",
        )
    st.markdown('</div>', unsafe_allow_html=True)
