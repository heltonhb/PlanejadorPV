"""Componentes de upload e sidebar."""

import streamlit as st
from utils.documentos import processar_documento, _get_collection as _get_docs_collection, sanitizar_id, salvar_resumo_documento
from utils.ingestao import processar_url, processar_html, processar_instagram, processar_texto, processar_planilha
from utils.resumos import gerar_resumo
from utils.firebase_store import salvar_fonte_meta, remover_fonte_meta


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
                        container.markdown(
                            f'<div class="success-msg">✅ **PDF processado:** {nome} — '
                            f'{resultado["total_chunks"]} trechos, '
                            f'{resultado["total_caracteres"]} caracteres '
                            f'({resultado["paginas"]} páginas)</div>',
                            unsafe_allow_html=True,
                        )
                        st.session_state.documentos.append(nome)
                        resumo = gerar_resumo(resultado.get("texto_completo", ""), "pdf")
                        salvar_resumo_documento(sanitizar_id(nome), resumo)
                        st.session_state.documentos_meta[nome] = {
                            "fonte": "pdf",
                            "nome": nome,
                            "chunks": resultado["total_chunks"],
                            "caracteres": resultado["total_caracteres"],
                            "paginas": resultado["paginas"],
                            "documento_id": sanitizar_id(nome),
                            "resumo": resumo,
                        }
                        salvar_fonte_meta(nome, st.session_state.documentos_meta[nome])
                    else:
                        container.error(f"{resultado['mensagem']}")
                except Exception as e:
                    container.error(f"Não foi possível processar **{nome}**. Verifique se o arquivo é um PDF válido e tente novamente.")

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
                        f"{resultado['total_chunks']} trechos, "
                        f"{resultado['total_caracteres']} caracteres"
                    )
                    st.session_state.documentos.append(url)
                    resumo = gerar_resumo(resultado.get("texto_completo", ""), "url")
                    salvar_resumo_documento(sanitizar_id(f"url_{url}"), resumo)
                    st.session_state.documentos_meta[url] = {
                        "fonte": "url",
                        "nome": resultado.get("titulo", url),
                        "chunks": resultado["total_chunks"],
                        "caracteres": resultado["total_caracteres"],
                        "url": url,
                        "documento_id": sanitizar_id(f"url_{url}"),
                        "resumo": resumo,
                    }
                    salvar_fonte_meta(url, st.session_state.documentos_meta[url])
                else:
                    container.error(f"Não foi possível acessar a URL. Verifique se o link está correto e tente novamente.")
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
                            f"{resultado['total_chunks']} trechos, "
                            f"{resultado['total_caracteres']} caracteres"
                        )
                        st.session_state.documentos.append(nome)
                        resumo = gerar_resumo(resultado.get("texto_completo", ""), "html")
                        salvar_resumo_documento(sanitizar_id(nome), resumo)
                        st.session_state.documentos_meta[nome] = {
                            "fonte": "html",
                            "nome": resultado.get("titulo", nome),
                            "chunks": resultado["total_chunks"],
                            "caracteres": resultado["total_caracteres"],
                            "arquivo": nome,
                            "documento_id": sanitizar_id(nome),
                            "resumo": resumo,
                        }
                        salvar_fonte_meta(nome, st.session_state.documentos_meta[nome])
                    else:
                        container.error(f"{resultado['mensagem']}")
                except Exception as e:
                    container.error(f"Não foi possível processar **{nome}**. Verifique se o HTML é válido e tente novamente.")
                    if len(str(e)) > 200:
                        container.exception(e)

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
                        f"Instagram @{perfil} — {resultado['total_chunks']} trechos, "
                        f"{resultado['total_caracteres']} caracteres "
                        f"({resultado['posts']} posts)"
                    )
                    st.session_state.documentos.append(chave)
                    resumo = gerar_resumo(resultado.get("texto_completo", ""), "instagram")
                    salvar_resumo_documento(sanitizar_id(chave), resumo)
                    st.session_state.documentos_meta[chave] = {
                        "fonte": "instagram",
                        "nome": perfil,
                        "chunks": resultado["total_chunks"],
                        "caracteres": resultado["total_caracteres"],
                        "posts": resultado["posts"],
                        "documento_id": sanitizar_id(chave),
                        "resumo": resumo,
                    }
                    salvar_fonte_meta(chave, st.session_state.documentos_meta[chave])
                else:
                    container.error(f"Não foi possível acessar o perfil @{perfil}. Verifique o nome e tente novamente.")
            else:
                container.info("Perfil já processado.")

    elif aba == "Texto":
        texto = container.text_area(
            "Cole o texto aqui",
            placeholder="Cole um artigo, e-mail, briefing ou qualquer conteúdo de texto...",
            height=200, key=f"{key_prefix}texto",
        )
        titulo_input = container.text_input(
            "Título (opcional)", placeholder="Ex: Briefing campanha maio",
            key=f"{key_prefix}txt_titulo",
        )
        if texto and container.button("Processar Texto", key=f"{key_prefix}txt_btn"):
            chave = f"txt_{texto[:30]}"
            if chave not in st.session_state.documentos:
                with container.status(f"Processando texto..."):
                    resultado = processar_texto(texto, titulo=titulo_input)
                if resultado["status"] == "ok":
                    container.success(
                        f"Texto: {resultado['titulo']} — "
                        f"{resultado['total_chunks']} trechos, "
                        f"{resultado['total_caracteres']} caracteres"
                    )
                    st.session_state.documentos.append(chave)
                    resumo = gerar_resumo(resultado.get("texto_completo", ""), "texto")
                    salvar_resumo_documento(resultado["documento_id"], resumo)
                    st.session_state.documentos_meta[chave] = {
                        "fonte": "texto",
                        "nome": resultado.get("titulo", "Texto"),
                        "chunks": resultado["total_chunks"],
                        "caracteres": resultado["total_caracteres"],
                        "documento_id": resultado["documento_id"],
                        "resumo": resumo,
                    }
                    salvar_fonte_meta(chave, st.session_state.documentos_meta[chave])
                else:
                    container.error(f"Não foi possível processar o texto. {resultado['mensagem']}")
            else:
                container.info("Texto já processado.")

    elif aba == "Planilha":
        planilha_file = container.file_uploader(
            "Escolha uma planilha (.xlsx)", type="xlsx",
            key=f"{key_prefix}planilha",
        )
        if planilha_file and container.button("Processar Planilha", key=f"{key_prefix}xls_btn"):
            chave = f"xls_{planilha_file.name}"
            if chave not in st.session_state.documentos:
                with container.status(f"Processando {planilha_file.name}..."):
                    resultado = processar_planilha(planilha_file.read(), nome_arquivo=planilha_file.name)
                if resultado["status"] == "ok":
                    container.success(
                        f"Planilha: {resultado['titulo']} — "
                        f"{resultado['total_chunks']} trechos, "
                        f"{resultado['total_caracteres']} caracteres"
                    )
                    st.session_state.documentos.append(chave)
                    resumo = gerar_resumo(resultado.get("texto_completo", ""), "planilha")
                    salvar_resumo_documento(resultado["documento_id"], resumo)
                    st.session_state.documentos_meta[chave] = {
                        "fonte": "planilha",
                        "nome": resultado.get("titulo", planilha_file.name),
                        "chunks": resultado["total_chunks"],
                        "caracteres": resultado["total_caracteres"],
                        "documento_id": resultado["documento_id"],
                        "resumo": resumo,
                    }
                    salvar_fonte_meta(chave, st.session_state.documentos_meta[chave])
                else:
                    container.error(f"Não foi possível processar a planilha. {resultado['mensagem']}")
            else:
                container.info("Planilha já processada.")


def sidebar_upload():
    st.sidebar.title("Fontes de informação")
    aba = st.sidebar.radio("Tipo de fonte", ["PDF", "URL", "HTML", "Instagram", "Texto", "Planilha"], key="sidebar_aba")
    _render_upload_tab(st.sidebar, aba, key_prefix="side_")

    st.sidebar.divider()
    st.sidebar.markdown("### Fontes carregadas")
    if st.session_state.documentos:
        icones = {"pdf": "📄", "url": "🔗", "html": "🌐", "instagram": "📷", "texto": "📝", "planilha": "📊"}
        for chave in list(st.session_state.documentos):
            meta = st.session_state.documentos_meta.get(chave)
            if meta is None:
                st.sidebar.markdown(f"- {chave}")
                continue
            fonte = meta["fonte"]
            nome = meta.get("nome", chave)
            chunks = meta.get("chunks", "?")
            icone = icones.get(fonte, "📄")
            col1, col2 = st.sidebar.columns([5, 1])
            with col1:
                st.markdown(f"**{icone} {nome}**")
                st.caption(f"{chunks} trechos")
            with col2:
                if st.button("🗑️", key=f"del_{chave}", help="Remover esta fonte"):
                    colecao = _get_docs_collection()
                    try:
                        colecao.delete(where={"documento_id": meta["documento_id"]})
                    except Exception:
                        pass
                    st.session_state.documentos.remove(chave)
                    st.session_state.documentos_meta.pop(chave, None)
                    remover_fonte_meta(chave)
                    st.rerun()
        with st.sidebar.popover("Limpar tudo", use_container_width=True):
            st.warning("Isso vai apagar **todas as fontes** e o **histórico de conversa**. Não é possível desfazer.")
            if st.button("Sim, apagar tudo", type="primary", use_container_width=True):
                try:
                    _get_docs_collection().delete(where={})
                except Exception:
                    pass
                try:
                    from utils.firebase_store import limpar_firestore
                    limpar_firestore()
                except Exception:
                    pass
                st.session_state.documentos = []
                st.session_state.documentos_meta = {}
                st.session_state.mensagens = []
                st.session_state.sugestoes_usadas = False
                st.session_state.calendarios_gerados = 0
                st.session_state.campanhas_geradas = 0
                st.rerun()
    else:
        st.sidebar.markdown("*Nenhuma fonte carregada.*")
