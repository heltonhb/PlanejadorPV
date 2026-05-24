import streamlit as st
from datetime import date
from utils.calendario import gerar_calendario, MESES
from components.fontes import render_markdown_with_copy


def render():
    st.markdown('<div class="animate-in">', unsafe_allow_html=True)
    st.markdown(
        '<div class="app-card" style="margin-bottom: 2rem;">'
        '<h2 style="margin:0; color: var(--primary);">📅 Calendário Editorial</h2>'
        '<p style="color: var(--on-surface-variant); margin-top: 0.5rem; font-size: 0.95rem;">'
        'Gere um plano mensal de ações de marketing personalizado '
        'para a unidade Tatuapé.</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    with st.container(border=False):
        st.markdown('<div class="app-card" style="margin-bottom: 1.5rem;">', unsafe_allow_html=True)
        hoje = date.today()
        col_mes, col_ano = st.columns(2)
        with col_mes:
            mes_idx = MESES.index(MESES[hoje.month - 1])
            mes_selecionado = st.selectbox("Mês", MESES, index=mes_idx)
        with col_ano:
            ano_selecionado = st.number_input("Ano", value=hoje.year, min_value=2024, max_value=2030)

        if st.button("Gerar Calendário", type="primary", use_container_width=True, disabled=st.session_state.processing):
            st.session_state.processing = True
            progress = st.progress(0, text="Iniciando geração do calendário...")
            progress.progress(30, text="Consultando fontes...")
            resultado = gerar_calendario(mes_selecionado, ano_selecionado)
            progress.progress(80, text="Estruturando resultado...")
            progress.progress(100, text="Concluído!")
            progress.empty()
            if resultado["status"] == "ok":
                st.session_state.calendarios_gerados += 1
                st.session_state.ultimo_calendario = resultado["conteudo"]
                st.session_state.ultimo_calendario_contexto = resultado.get("contexto_usado", False)
                st.session_state.ultimo_calendario_mes = mes_selecionado
                st.session_state.ultimo_calendario_ano = ano_selecionado
                st.toast("Calendário gerado com sucesso!")
            else:
                st.error(f"❌ Não foi possível gerar o calendário: {resultado['mensagem']}")
            st.session_state.processing = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # Display generated calendar if available
    if st.session_state.get("ultimo_calendario"):
        st.divider()
        st.markdown(
            '<div class="app-card" style="margin-top: 2rem;">'
            '<h3 style="margin-top:0; color: var(--primary);">📝 Calendário Planejado</h3>'
            '</div>',
            unsafe_allow_html=True,
        )
        
        mes_cal = st.session_state.get("ultimo_calendario_mes", mes_selecionado)
        ano_cal = st.session_state.get("ultimo_calendario_ano", ano_selecionado)
        ctx_usado = st.session_state.get("ultimo_calendario_contexto", False)
        
        if ctx_usado:
            st.success("✅ Calendário gerado com base nas suas fontes carregadas.")
        else:
            st.info("📚 Nenhuma fonte carregada — usei conhecimento geral do calendário escolar.")
            
        render_markdown_with_copy(
            st.session_state.ultimo_calendario,
            key="cal_copy",
            label="Copiar Calendário",
        )
    st.markdown('</div>', unsafe_allow_html=True)
