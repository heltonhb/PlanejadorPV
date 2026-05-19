import os
from datetime import date
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from utils.documentos import processar_documento, _get_collection as _get_docs_collection
from utils.ingestao import processar_url, processar_html, processar_instagram
from utils.ia_engine import perguntar
from utils.perguntas_sugeridas import PERGUNTAS_SUGERIDAS
from utils.calendario import gerar_calendario, MESES
from utils.campanhas import gerar_campanha, OBJETIVOS, PUBLICOS, SERVICOS

load_dotenv()

try:
    collection = _get_docs_collection()
    if collection.count() == 0:
        from utils.firebase_store import recarregar_chunks
        recarregar_chunks()
except Exception:
    pass

st.set_page_config(
    page_title="Marketing Planner",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="auto",
)

st.markdown("""
<style>
    :root { --pwa-bar-height: env(safe-area-inset-top, 0px); }
    /* mobile: stacked columns, readable text */
    @media (max-width: 640px) {
        .stMainBlockContainer { padding: 1rem 0.75rem !important; }
        .stColumn > div { min-width: 100% !important; }
        div[data-testid="column"] { width: 100% !important; flex: 0 0 100% !important; }
        .stChatMessage { font-size: 0.95rem; }
        section[data-testid="stSidebar"] .stSidebarContent { padding: 0.75rem; }
        button[kind="primary"] { width: 100% !important; }
    }
</style>
<!-- PWA meta tags -->
<meta name="theme-color" content="#FF4B4B">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Mkt Planner">
<link rel="apple-touch-icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 512 512'%3E%3Crect width='512' height='512' rx='64' fill='%23FF4B4B'/%3E%3Ctext x='256' y='340' text-anchor='middle' font-size='280' fill='white'%3E📊%3C/text%3E%3C/svg%3E">
<script>
(function(){
    var m = {
        name: "PlanejadorPV — Marketing Planner",
        short_name: "Mkt Planner",
        description: "Planejamento de marketing para franquias",
        start_url: ".",
        display: "standalone",
        background_color: "#0E1117",
        theme_color: "#FF4B4B",
        orientation: "portrait-primary",
        categories: ["business","marketing"],
        icons: [{
            src: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 512 512'%3E%3Crect width='512' height='512' rx='64' fill='%23FF4B4B'/%3E%3Ctext x='256' y='340' text-anchor='middle' font-size='280' fill='white'%3E📊%3C/text%3E%3C/svg%3E",
            sizes: "512x512",
            type: "image/svg+xml",
            purpose: "any maskable"
        }]
    };
    var b = new Blob([JSON.stringify(m)], {type:"application/json"});
    var l = document.createElement("link");
    l.rel = "manifest"; l.href = URL.createObjectURL(b);
    document.head.appendChild(l);
})();
</script>
""", unsafe_allow_html=True)

if "mensagens" not in st.session_state:
    st.session_state.mensagens = []
if "documentos" not in st.session_state:
    st.session_state.documentos = []


def exibir_fontes(fontes: list[dict]):
    seen = set()
    items = []
    for f in fontes:
        label = f.get("arquivo") or f.get("url") or f.get("perfil") or f.get("fonte", "?")
        chave = (label, f["fonte"])
        if chave not in seen:
            seen.add(chave)
            items.append(f"**{f['fonte'].upper()}**: {label}  · relevância {f['relevancia']}")
    with st.expander("Fontes consultadas", expanded=False):
        for item in items:
            st.markdown(item)


def _render_upload_tab(container, aba, key_prefix=""):
    if aba == "PDF":
        uploaded_file = container.file_uploader(
            "Upload PDF", type=["pdf"], accept_multiple_files=False, key=f"{key_prefix}pdf",
        )
        if uploaded_file:
            nome = uploaded_file.name
            if nome not in st.session_state.documentos:
                try:
                    with container.status(f"Processando {nome}..."):
                        pdf_bytes = uploaded_file.read()
                        resultado = processar_documento(pdf_bytes, nome_arquivo=nome)
                    if resultado["status"] == "ok":
                        container.success(
                            f"PDF: {nome} — {resultado['total_chunks']} chunks, "
                            f"{resultado['total_caracteres']} caracteres "
                            f"({resultado['paginas']} páginas, {resultado['metodo']})"
                        )
                        st.session_state.documentos.append(nome)
                    else:
                        container.error(f"{resultado['mensagem']}")
                except Exception as e:
                    container.error(f"Erro ao processar {nome}: {e}")

    elif aba == "URL":
        url = container.text_input(
            "URL do site", placeholder="https://exemplo.com/artigo", key=f"{key_prefix}url",
        )
        if url and container.button("Processar URL", key=f"{key_prefix}url_btn"):
            if url not in st.session_state.documentos:
                with container.status(f"Acessando {url}..."):
                    resultado = processar_url(url)
                if resultado["status"] == "ok":
                    container.success(
                        f"URL: {resultado['titulo']} — "
                        f"{resultado['total_chunks']} chunks, "
                        f"{resultado['total_caracteres']} caracteres"
                    )
                    st.session_state.documentos.append(url)
                else:
                    container.error(resultado["mensagem"])
            else:
                container.info("URL já processada.")

    elif aba == "HTML":
        uploaded_html = container.file_uploader(
            "Upload HTML", type=["html", "htm"], accept_multiple_files=False, key=f"{key_prefix}html",
        )
        if uploaded_html:
            nome = uploaded_html.name
            if nome not in st.session_state.documentos:
                try:
                    with container.status(f"Processando {nome}..."):
                        resultado = processar_html(uploaded_html.read(), nome_arquivo=nome)
                    if resultado["status"] == "ok":
                        container.success(
                            f"HTML: {resultado['titulo']} — "
                            f"{resultado['total_chunks']} chunks, "
                            f"{resultado['total_caracteres']} caracteres"
                        )
                        st.session_state.documentos.append(nome)
                    else:
                        container.error(resultado["mensagem"])
                except Exception as e:
                    container.error(f"Erro ao processar {nome}: {e}")

    elif aba == "Instagram":
        perfil = container.text_input(
            "Perfil do Instagram", placeholder="exemplo_perfil", key=f"{key_prefix}ig",
        )
        if perfil and container.button("Processar Perfil", key=f"{key_prefix}ig_btn"):
            chave = f"ig_{perfil}"
            if chave not in st.session_state.documentos:
                with container.status(f"Buscando @{perfil}..."):
                    resultado = processar_instagram(perfil)
                if resultado["status"] == "ok":
                    container.success(
                        f"Instagram @{perfil} — {resultado['total_chunks']} chunks, "
                        f"{resultado['total_caracteres']} caracteres "
                        f"({resultado['posts']} posts)"
                    )
                    st.session_state.documentos.append(chave)
                else:
                    container.error(resultado["mensagem"])
            else:
                container.info("Perfil já processado.")


def sidebar_upload():
    st.sidebar.title("Fontes de informação")
    aba = st.sidebar.radio("Tipo de fonte", ["PDF", "URL", "HTML", "Instagram"], key="sidebar_aba")
    _render_upload_tab(st.sidebar, aba, key_prefix="side_")

    st.sidebar.divider()
    st.sidebar.markdown("### Fontes carregadas")
    if st.session_state.documentos:
        for doc in st.session_state.documentos:
            st.sidebar.markdown(f"- {doc}")
        if st.sidebar.button("Limpar tudo"):
            from utils.documentos import _get_collection
            try:
                _get_collection().delete(where={})
            except Exception:
                pass
            try:
                from utils.firebase_store import limpar_firestore
                limpar_firestore()
            except Exception:
                pass
            st.session_state.documentos = []
            st.session_state.mensagens = []
            st.rerun()
    else:
        st.sidebar.markdown("*Nenhuma fonte carregada.*")


sidebar_upload()

tab_dash, tab_assistente, tab_calendario, tab_campanhas = st.tabs(
    ["📊 Dashboard", "💬 Assistente", "📅 Calendário Editorial", "📢 Gerador de Campanhas"],
)

with tab_dash:
    st.title("Dashboard — Marketing Planner")
    st.markdown("### Visão geral das fontes carregadas")

    try:
        collection = _get_docs_collection()
        total_chunks = collection.count()
    except Exception:
        total_chunks = 0

    col1, col2, col3 = st.columns(3)
    col1.metric("Fontes carregadas", len(st.session_state.documentos))
    col2.metric("Chunks na base vetorial", total_chunks)
    col3.metric("Perguntas feitas", len([m for m in st.session_state.mensagens if m["role"] == "user"]))

    if st.session_state.documentos:
        st.markdown("#### Fontes")
        for doc in st.session_state.documentos:
            st.markdown(f"- {doc}")
    else:
        st.info("Nenhuma fonte carregada ainda. Use a barra lateral para adicionar PDFs, URLs, HTML ou Instagram.")

    st.divider()
    with st.expander("📂 Adicionar fonte (dispositivos móveis)", expanded=False):
        st.markdown(
            "*No computador, use a barra lateral. Aqui você também pode adicionar fontes.*"
        )
        aba_mobile = st.radio("Tipo", ["PDF", "URL", "HTML", "Instagram"], key="mobile_aba")
        _render_upload_tab(st, aba_mobile, key_prefix="mob_")

    st.divider()
    st.markdown(
        "Use as abas **💬 Assistente** para conversar com seus documentos, "
        "**📅 Calendário Editorial** para gerar um plano mensal de marketing, "
        "ou **📢 Gerador de Campanhas** para campanhas completas."
    )

with tab_assistente:
    st.title("Assistente RAG — Marketing para Franquias")
    st.markdown(
        "Carregue informações na barra lateral e faça perguntas sobre o conteúdo."
    )

    if not st.session_state.mensagens:
        st.markdown("### Sugestões de perguntas")
        st.markdown("Clique em uma pergunta abaixo para começar:")

        for grupo in PERGUNTAS_SUGERIDAS:
            st.markdown(f"**{grupo['categoria']}**")
            cols = st.columns(3)
            for i, pergunta in enumerate(grupo["perguntas"]):
                if cols[i % 3].button(
                    pergunta, key=f"sugestao_{grupo['categoria']}_{i}",
                    use_container_width=True,
                ):
                    st.session_state.mensagens.append({"role": "user", "content": pergunta})
                    with st.chat_message("user"):
                        st.markdown(pergunta)
                    with st.chat_message("assistant"):
                        with st.spinner("Consultando fontes..."):
                            resultado = perguntar(pergunta)
                        st.markdown(resultado["resposta"])
                        if resultado["fontes"]:
                            exibir_fontes(resultado["fontes"])
                    st.session_state.mensagens.append({
                        "role": "assistant", "content": resultado["resposta"],
                        "fontes": resultado["fontes"],
                    })
                    st.rerun()

    for msg in st.session_state.mensagens:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant" and msg.get("fontes"):
                exibir_fontes(msg["fontes"])

    if prompt := st.chat_input("Faça uma pergunta sobre os documentos..."):
        st.session_state.mensagens.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Consultando fontes..."):
                resultado = perguntar(prompt)
            st.markdown(resultado["resposta"])
            if resultado["fontes"]:
                exibir_fontes(resultado["fontes"])
        st.session_state.mensagens.append({
            "role": "assistant", "content": resultado["resposta"],
            "fontes": resultado["fontes"],
        })

with tab_calendario:
    st.title("📅 Calendário Editorial")
    st.markdown(
        "Gere um plano mensal de ações de marketing personalizado "
        "para a unidade Tatuapé."
    )

    hoje = date.today()
    col_mes, col_ano = st.columns(2)
    with col_mes:
        mes_idx = MESES.index(MESES[hoje.month - 1])
        mes_selecionado = st.selectbox("Mês", MESES, index=mes_idx)
    with col_ano:
        ano_selecionado = st.number_input("Ano", value=hoje.year, min_value=2024, max_value=2030)

    if st.button("Gerar Calendário", type="primary", use_container_width=True):
        with st.spinner(f"Gerando calendário de {mes_selecionado}..."):
            resultado = gerar_calendario(mes_selecionado, ano_selecionado)
        if resultado["status"] == "ok":
            if resultado.get("contexto_usado"):
                st.info("Calendário gerado com base nas fontes carregadas.")
            else:
                st.info("Nenhuma fonte carregada — usei conhecimento geral do calendário escolar.")
            st.markdown(resultado["conteudo"])
        else:
            st.error(resultado["mensagem"])

with tab_campanhas:
    st.title("📢 Gerador de Campanhas")
    st.markdown(
        "Crie uma campanha de marketing completa para a unidade Tatuapé."
    )

    objetivo = st.selectbox("Objetivo da campanha", OBJETIVOS)
    publico = st.selectbox("Público-alvo", PUBLICOS)
    servico = st.selectbox("Serviço", SERVICOS)

    if st.button("Gerar Campanha", type="primary", use_container_width=True):
        with st.spinner("Criando campanha..."):
            resultado = gerar_campanha(objetivo, publico, servico)
        if resultado["status"] == "ok":
            if resultado.get("contexto_usado"):
                st.info("Campanha personalizada com base nas fontes carregadas.")
            else:
                st.info("Nenhuma fonte carregada — campanha baseada em conhecimento geral.")
            st.markdown(resultado["conteudo"])
        else:
            st.error(resultado["mensagem"])
