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
)

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


def sidebar_upload():
    st.sidebar.title("Fontes de informação")
    aba = st.sidebar.radio("Tipo de fonte", ["PDF", "URL", "HTML", "Instagram"])
    if aba == "PDF":
        uploaded_file = st.sidebar.file_uploader(
            "Upload PDF", type=["pdf"], accept_multiple_files=False,
        )
        if uploaded_file:
            nome = uploaded_file.name
            if nome not in st.session_state.documentos:
                try:
                    with st.sidebar.status(f"Processando {nome}..."):
                        pdf_bytes = uploaded_file.read()
                        resultado = processar_documento(pdf_bytes, nome_arquivo=nome)
                    if resultado["status"] == "ok":
                        st.sidebar.success(
                            f"PDF: {nome} — {resultado['total_chunks']} chunks, "
                            f"{resultado['total_caracteres']} caracteres "
                            f"({resultado['paginas']} páginas, {resultado['metodo']})"
                        )
                        st.session_state.documentos.append(nome)
                    else:
                        st.sidebar.error(f"{resultado['mensagem']}")
                except Exception as e:
                    st.sidebar.error(f"Erro ao processar {nome}: {e}")

    elif aba == "URL":
        url = st.sidebar.text_input("URL do site", placeholder="https://exemplo.com/artigo")
        if url and st.sidebar.button("Processar URL"):
            if url not in st.session_state.documentos:
                with st.sidebar.status(f"Acessando {url}..."):
                    resultado = processar_url(url)
                if resultado["status"] == "ok":
                    st.sidebar.success(
                        f"URL: {resultado['titulo']} — "
                        f"{resultado['total_chunks']} chunks, "
                        f"{resultado['total_caracteres']} caracteres"
                    )
                    st.session_state.documentos.append(url)
                else:
                    st.sidebar.error(resultado["mensagem"])
            else:
                st.sidebar.info("URL já processada.")

    elif aba == "HTML":
        uploaded_html = st.sidebar.file_uploader(
            "Upload HTML", type=["html", "htm"], accept_multiple_files=False,
        )
        if uploaded_html:
            nome = uploaded_html.name
            if nome not in st.session_state.documentos:
                try:
                    with st.sidebar.status(f"Processando {nome}..."):
                        resultado = processar_html(uploaded_html.read(), nome_arquivo=nome)
                    if resultado["status"] == "ok":
                        st.sidebar.success(
                            f"HTML: {resultado['titulo']} — "
                            f"{resultado['total_chunks']} chunks, "
                            f"{resultado['total_caracteres']} caracteres"
                        )
                        st.session_state.documentos.append(nome)
                    else:
                        st.sidebar.error(resultado["mensagem"])
                except Exception as e:
                    st.sidebar.error(f"Erro ao processar {nome}: {e}")

    elif aba == "Instagram":
        perfil = st.sidebar.text_input(
            "Perfil do Instagram", placeholder="exemplo_perfil",
        )
        if perfil and st.sidebar.button("Processar Perfil"):
            chave = f"ig_{perfil}"
            if chave not in st.session_state.documentos:
                with st.sidebar.status(f"Buscando @{perfil}..."):
                    resultado = processar_instagram(perfil)
                if resultado["status"] == "ok":
                    st.sidebar.success(
                        f"Instagram @{perfil} — {resultado['total_chunks']} chunks, "
                        f"{resultado['total_caracteres']} caracteres "
                        f"({resultado['posts']} posts)"
                    )
                    st.session_state.documentos.append(chave)
                else:
                    st.sidebar.error(resultado["mensagem"])
            else:
                st.sidebar.info("Perfil já processado.")

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
