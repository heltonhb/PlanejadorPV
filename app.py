import os
from datetime import date
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from markdown_it import MarkdownIt

from utils.documentos import processar_documento, _get_collection as _get_docs_collection
from utils.ingestao import processar_url, processar_html, processar_instagram, processar_texto, processar_planilha
from utils.ia_engine import perguntar
from utils.perguntas_sugeridas import PERGUNTAS_SUGERIDAS
from utils.calendario import gerar_calendario, MESES
from utils.campanhas import gerar_campanha, OBJETIVOS, PUBLICOS, SERVICOS

load_dotenv()

_md = MarkdownIt()

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
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    :root {
        --brand-blue: #005CAA;
        --brand-blue-dark: #003F7A;
        --brand-blue-light: #E8F0FE;
        --brand-green: #00A859;
        --brand-green-light: #E6F9F0;
        --brand-yellow: #F7B731;
        --brand-yellow-light: #FEF7E6;
        --brand-red: #E84C3D;
        --brand-red-light: #FDEDEC;
        --gray-50: #F8F9FA;
        --gray-100: #F1F3F5;
        --gray-200: #E9ECEF;
        --gray-300: #DEE2E6;
        --gray-600: #6C757D;
        --gray-800: #343A40;
        --gray-900: #212529;
        --pwa-bar-height: env(safe-area-inset-top, 0px);
    }

    * { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }

    div[data-testid="stMetricValue"] { color: var(--brand-blue); font-weight: 700; }
    div[data-testid="stMetricLabel"] { font-size: 0.85rem; color: var(--gray-600); }

    .app-header {
        background: linear-gradient(135deg, var(--brand-blue), var(--brand-blue-dark));
        padding: 1rem 2rem;
        border-radius: 0.5rem;
        margin-bottom: 1.5rem;
        color: white;
    }
    .app-header-content { display: flex; align-items: center; gap: 1rem; }
    .app-logo { font-size: 2rem; line-height: 1; }
    .app-title { font-size: 1.5rem; font-weight: 700; }
    .app-subtitle { font-size: 0.875rem; opacity: 0.9; }

    .app-card {
        background: white;
        border: 1px solid var(--gray-200);
        border-radius: 0.75rem;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
        color: var(--gray-900);
    }
    .app-card h1, .app-card h2, .app-card h3 { color: var(--brand-blue); margin-top: 1rem; }
    .app-card h1:first-child, .app-card h2:first-child, .app-card h3:first-child { margin-top: 0; }
    .app-card p { color: var(--gray-800); line-height: 1.6; margin-bottom: 0.75rem; }
    .app-card ul, .app-card ol { padding-left: 1.25rem; margin-bottom: 0.75rem; }
    .app-card li { margin-bottom: 0.35rem; color: var(--gray-800); }
    .app-card hr { border: none; border-top: 2px solid var(--gray-200); margin: 1rem 0; }
    .app-card strong { color: var(--brand-blue-dark); }

    .app-card-empty {
        background: var(--gray-50);
        border: 2px dashed var(--gray-300);
        border-radius: 0.75rem;
        padding: 2.5rem 1.5rem;
        text-align: center;
        color: var(--gray-600);
        margin: 1rem 0;
    }

    .stAlert { border-left-color: var(--brand-blue) !important; }
    div[data-testid="stAlert"] { border-radius: 0.5rem; }

    div.stButton > button[kind="primary"] {
        background: var(--brand-blue);
        border: none;
        font-weight: 600;
        transition: all 0.15s ease;
    }
    div.stButton > button[kind="primary"]:hover:not(:disabled) {
        background: var(--brand-blue-dark);
        transform: translateY(-1px);
        box-shadow: 0 2px 8px rgba(0,92,170,0.3);
    }

    .suggestion-btn div.stButton > button {
        height: 100%;
        white-space: normal;
        word-break: break-word;
        text-align: left;
        padding: 0.5rem 0.75rem;
        font-size: 0.85rem;
        border-radius: 0.5rem;
        background: var(--gray-50);
        border: 1px solid var(--gray-200);
        color: var(--gray-800);
        transition: all 0.15s ease;
    }
    .suggestion-btn div.stButton > button:hover {
        background: var(--brand-blue-light);
        border-color: var(--brand-blue);
        color: var(--brand-blue);
    }

    .success-msg div[data-testid="stAlert"] { border-left-color: var(--brand-green) !important; }
    .success-msg div[data-testid="stAlert"] svg { fill: var(--brand-green); }

    .app-footer {
        text-align: center;
        color: var(--gray-600);
        font-size: 0.8rem;
        padding: 2rem 0 1rem;
        border-top: 1px solid var(--gray-200);
        margin-top: 2rem;
    }

    @media (max-width: 640px) {
        .stMainBlockContainer { padding: 1rem 0.75rem !important; }
        .stColumn > div { min-width: 100% !important; }
        div[data-testid="column"] { width: 100% !important; flex: 0 0 100% !important; }
        .stChatMessage { font-size: 0.95rem; }
        section[data-testid="stSidebar"] .stSidebarContent { padding: 0.75rem; }
        button[kind="primary"] { width: 100% !important; }
        .app-header { padding: 0.75rem 1rem; }
        .app-title { font-size: 1.25rem; }
        .app-card { padding: 1rem; }
    }
</style>
<meta name="theme-color" content="#005CAA">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Mkt Planner">
<link rel="apple-touch-icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 512 512'%3E%3Crect width='512' height='512' rx='64' fill='%23005CAA'/%3E%3Ctext x='256' y='340' text-anchor='middle' font-size='280' fill='white'%3E📊%3C/text%3E%3C/svg%3E">
<script>
(function(){
    var m = {
        name: "PlanejadorPV — Marketing Planner",
        short_name: "Mkt Planner",
        description: "Planejamento de marketing para franquias",
        start_url: ".",
        display: "standalone",
        background_color: "#0E1117",
        theme_color: "#005CAA",
        orientation: "portrait-primary",
        categories: ["business","marketing"],
        icons: [{
            src: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 512 512'%3E%3Crect width='512' height='512' rx='64' fill='%23005CAA'/%3E%3Ctext x='256' y='340' text-anchor='middle' font-size='280' fill='white'%3E📊%3C/text%3E%3C/svg%3E",
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

st.markdown("""
<div class="app-header">
    <div class="app-header-content">
        <div class="app-logo">📊</div>
        <div>
            <div class="app-title">PlanejadorPV</div>
            <div class="app-subtitle">Marketing Planner — Ensina Mais Turma da Mônica · Unidade Tatuapé</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

if "mensagens" not in st.session_state:
    st.session_state.mensagens = []
if "documentos" not in st.session_state:
    st.session_state.documentos = []
if "processing" not in st.session_state:
    st.session_state.processing = False
if "sugestoes_usadas" not in st.session_state:
    st.session_state.sugestoes_usadas = False
if "calendarios_gerados" not in st.session_state:
    st.session_state.calendarios_gerados = 0
if "campanhas_geradas" not in st.session_state:
    st.session_state.campanhas_geradas = 0


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
                        container.markdown(
                            f'<div class="success-msg">✅ **PDF processado:** {nome} — '
                            f'{resultado["total_chunks"]} trechos, '
                            f'{resultado["total_caracteres"]} caracteres '
                            f'({resultado["paginas"]} páginas)</div>',
                            unsafe_allow_html=True,
                        )
                        st.session_state.documentos.append(nome)
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
                        f"{resultado['total_chunks']} chunks, "
                        f"{resultado['total_caracteres']} caracteres"
                    )
                    st.session_state.documentos.append(url)
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
                            f"{resultado['total_chunks']} chunks, "
                            f"{resultado['total_caracteres']} caracteres"
                        )
                        st.session_state.documentos.append(nome)
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
                        f"Instagram @{perfil} — {resultado['total_chunks']} chunks, "
                        f"{resultado['total_caracteres']} caracteres "
                        f"({resultado['posts']} posts)"
                    )
                    st.session_state.documentos.append(chave)
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
                        f"{resultado['total_chunks']} chunks, "
                        f"{resultado['total_caracteres']} caracteres"
                    )
                    st.session_state.documentos.append(chave)
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
                        f"{resultado['total_chunks']} chunks, "
                        f"{resultado['total_caracteres']} caracteres"
                    )
                    st.session_state.documentos.append(chave)
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
        for doc in st.session_state.documentos:
            st.sidebar.markdown(f"- {doc}")
        with st.sidebar.popover("Limpar tudo", use_container_width=True):
            st.warning("Isso vai apagar **todas as fontes** e o **histórico de conversa**. Não é possível desfazer.")
            if st.button("Sim, apagar tudo", type="primary", use_container_width=True):
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
                st.session_state.sugestoes_usadas = False
                st.session_state.calendarios_gerados = 0
                st.session_state.campanhas_geradas = 0
                st.rerun()
    else:
        st.sidebar.markdown("*Nenhuma fonte carregada.*")


sidebar_upload()

tab_dash, tab_assistente, tab_calendario, tab_campanhas, tab_relatorio = st.tabs(
    ["📊 Dashboard", "💬 Assistente", "📅 Calendário Editorial", "📢 Gerador de Campanhas", "📋 Relatório de Conteúdo"],
)

with tab_dash:
    st.title("Dashboard — Marketing Planner")
    st.markdown("### Visão geral das fontes carregadas")

    try:
        collection = _get_docs_collection()
        total_chunks = collection.count()
    except Exception:
        total_chunks = 0

    total_perguntas = len([m for m in st.session_state.mensagens if m["role"] == "user"])
    total_calendarios = st.session_state.get("calendarios_gerados", 0)
    total_campanhas = st.session_state.get("campanhas_geradas", 0)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📁 Fontes carregadas", len(st.session_state.documentos))
    col2.metric("📄 Documentos na base", total_chunks)
    col3.metric("💬 Perguntas feitas", total_perguntas)
    col4.metric("📊 Conteúdos gerados", total_calendarios + total_campanhas)

    if st.session_state.documentos:
        st.markdown("#### Fontes carregadas")
        cols = st.columns(2)
        for i, doc in enumerate(st.session_state.documentos):
            icon = "📄" if doc.endswith(".pdf") else "🔗" if doc.startswith("http") else "📷" if doc.startswith("ig_") else "📝" if doc.startswith("txt_") else "📊"
            cols[i % 2].markdown(f"- {icon} {doc}")
    else:
        st.markdown(
            '<div class="app-card-empty">'
            '📂 <strong>Nenhuma fonte carregada</strong><br>'
            'Use a barra lateral para adicionar PDFs, URLs, HTML, Instagram, texto ou planilhas.'
            '</div>',
            unsafe_allow_html=True,
        )

    st.divider()
    with st.expander("📂 Adicionar fonte (dispositivos móveis)", expanded=False):
        st.markdown(
            "*No computador, use a barra lateral. Aqui você também pode adicionar fontes.*"
        )
        aba_mobile = st.radio("Tipo", ["PDF", "URL", "HTML", "Instagram", "Texto", "Planilha"], key="mobile_aba")
        _render_upload_tab(st, aba_mobile, key_prefix="mob_")

    st.divider()
    st.markdown(
        "Use as abas **💬 Assistente** para conversar com seus documentos, "
        "**📅 Calendário Editorial** para gerar um plano mensal de marketing, "
        "ou **📢 Gerador de Campanhas** para campanhas completas."
    )

with tab_assistente:
    st.title("💬 Assistente — Marketing para Franquias")
    st.markdown(
        "Carregue informações na barra lateral e faça perguntas sobre o conteúdo."
    )

    if not st.session_state.mensagens and not st.session_state.sugestoes_usadas:
        st.markdown("### Sugestões de perguntas")
        st.markdown("Clique em uma pergunta abaixo para começar:")

        for grupo in PERGUNTAS_SUGERIDAS:
            st.markdown(f"**{grupo['categoria']}**")
            cols = st.columns(3)
            for i, pergunta in enumerate(grupo["perguntas"]):
                with cols[i % 3]:
                    st.markdown('<div class="suggestion-btn">', unsafe_allow_html=True)
                    if st.button(
                        pergunta, key=f"sugestao_{grupo['categoria']}_{i}",
                        use_container_width=True,
                    ):
                        st.session_state.sugestoes_usadas = True
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
                    st.markdown('</div>', unsafe_allow_html=True)

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

    if st.button("Gerar Calendário", type="primary", use_container_width=True, disabled=st.session_state.processing):
        st.session_state.processing = True
        progress = st.progress(0, text="Iniciando geração do calendário...")
        progress.progress(30, text="Consultando fontes...")
        resultado = gerar_calendario(mes_selecionado, ano_selecionado)
        progress.progress(80, text="Estruturando resultado...")
        progress.progress(100, text="Concluído!")
        progress.empty()
        if resultado["status"] == "ok":
            if resultado.get("contexto_usado"):
                st.success("✅ Calendário gerado com base nas suas fontes carregadas.")
            else:
                st.info("📚 Nenhuma fonte carregada — usei conhecimento geral do calendário escolar.")
            html_content = _md.render(resultado["conteudo"])
            st.markdown(f'<div class="app-card">{html_content}</div>', unsafe_allow_html=True)
            st.session_state.calendarios_gerados += 1
        else:
            st.error(f"❌ Não foi possível gerar o calendário: {resultado['mensagem']}")
        st.session_state.processing = False

with tab_campanhas:
    st.title("📢 Gerador de Campanhas")
    st.markdown(
        "Crie uma campanha de marketing completa para a unidade Tatuapé."
    )

    objetivo = st.selectbox("Objetivo da campanha", OBJETIVOS)
    publico = st.selectbox("Público-alvo", PUBLICOS)
    servico = st.selectbox("Serviço", SERVICOS)

    if st.button("Gerar Campanha", type="primary", use_container_width=True, disabled=st.session_state.processing):
        st.session_state.processing = True
        progress = st.progress(0, text="Iniciando criação da campanha...")
        progress.progress(25, text="Analisando objetivos...")
        resultado = gerar_campanha(objetivo, publico, servico)
        progress.progress(75, text="Montando estrutura da campanha...")
        progress.progress(100, text="Concluído!")
        progress.empty()
        if resultado["status"] == "ok":
            if resultado.get("contexto_usado"):
                st.success("✅ Campanha personalizada com base nas suas fontes carregadas.")
            else:
                st.info("📚 Nenhuma fonte carregada — campanha baseada em conhecimento geral.")
            html_content = _md.render(resultado["conteudo"])
            st.markdown(f'<div class="app-card">{html_content}</div>', unsafe_allow_html=True)
            st.session_state.campanhas_geradas += 1
        else:
            st.error(f"❌ Não foi possível gerar a campanha: {resultado['mensagem']}")
        st.session_state.processing = False

with tab_relatorio:
    st.title("📋 Relatório de Conteúdo Ingerido")
    st.markdown("Visão detalhada de todo o conteúdo carregado no sistema.")

    from utils.relatorios import resumo_conteudo
    relatorio = resumo_conteudo()

    if relatorio["total_chunks"] == 0:
        st.markdown(
            '<div class="app-card-empty">'
            "📂 <strong>Nenhum conteúdo ingerido</strong><br>"
            "Carregue fontes pela barra lateral ou pelo Dashboard."
            "</div>",
            unsafe_allow_html=True,
        )
    else:
        col1, col2, col3 = st.columns(3)
        col1.metric("📄 Total de chunks", relatorio["total_chunks"])
        col2.metric("📏 Total de caracteres", f"{relatorio['total_caracteres']:,}".replace(",", "."))
        col3.metric("🗂️ Tipos de fonte", len(relatorio["por_fonte"]))

        st.divider()
        st.markdown("### Distribuição por tipo de fonte")

        por_fonte_items = sorted(relatorio["por_fonte"].items())
        cols_fonte = st.columns(len(por_fonte_items))
        icones_f = {"pdf": "📄", "url": "🔗", "html": "🌐", "instagram": "📷", "texto": "📝", "planilha": "📊"}
        nomes_f = {"pdf": "PDF", "url": "URL", "html": "HTML", "instagram": "Instagram", "texto": "Texto", "planilha": "Planilha"}
        for idx, (fonte, dados) in enumerate(por_fonte_items):
            with cols_fonte[idx]:
                icone = icones_f.get(fonte, "📄")
                nome = nomes_f.get(fonte, fonte.capitalize())
                st.metric(f"{icone} {nome}", dados["chunks"], f"{dados['caracteres']:,} caracteres".replace(",", "."))

        st.divider()
        st.markdown("### Detalhamento por documento")

        for item in relatorio["fontes_detalhadas"]:
            st.markdown(
                f'<div class="app-card" style="padding: 0.75rem 1rem;">'
                f'<span style="font-size: 1.1rem; font-weight: 600;">{item["icone"]} {item["titulo"]}</span><br>'
                f'<span style="color: var(--gray-600); font-size: 0.85rem;">'
                f'{item["chunks"]} chunks · {item["caracteres"]:,} caracteres'
                f"</span>"
                f"</div>",
                unsafe_allow_html=True,
            )

st.markdown("""
<div class="app-footer">
    PlanejadorPV © 2025 — Ensina Mais Turma da Mônica · Unidade Tatuapé
</div>
""", unsafe_allow_html=True)
