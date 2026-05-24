import os
import streamlit as st

st.set_page_config(
    page_title="Marketing Planner",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="auto",
)

from dotenv import load_dotenv
from utils.documentos import _get_collection as _get_docs_collection
from utils.firebase_store import carregar_fontes_meta
from components import inject_css_and_theme, render_header, sidebar_upload
from tabs import (
    render_dashboard,
    render_chat,
    render_calendario,
    render_campanhas,
    render_relatorios,
    render_legendas,
)

load_dotenv()

# Inicialização da coleção ChromaDB
try:
    collection = _get_docs_collection()
    if collection.count() == 0:
        from utils.firebase_store import recarregar_chunks
        recarregar_chunks()
except Exception:
    pass

# Injetar CSS e configurações visuais
inject_css_and_theme()

# Renderizar Cabeçalho
render_header()

# Inicializar Estados do Streamlit
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
if "legendas_geradas" not in st.session_state:
    st.session_state.legendas_geradas = []
if "legendas_imagens_b64" not in st.session_state:
    st.session_state.legendas_imagens_b64 = []
if "documentos_meta" not in st.session_state:
    st.session_state.documentos_meta = {}

# Restaurar metadados do Firestore se session_state estiver vazio
# (acontece quando o Streamlit reinicia/redeploy)
if not st.session_state.documentos_meta:
    try:
        _meta_restaurado = carregar_fontes_meta()
        if _meta_restaurado:
            st.session_state.documentos_meta = _meta_restaurado
            st.session_state.documentos = list(_meta_restaurado.keys())
    except Exception:
        pass
if "ultimo_calendario" not in st.session_state:
    st.session_state.ultimo_calendario = None
if "ultima_campanha" not in st.session_state:
    st.session_state.ultima_campanha = None

# Sidebar Ingestão de Arquivos
sidebar_upload()

# Abas Principais
with st.container(key="main_tabs"):
    tab_dash, tab_assistente, tab_calendario, tab_campanhas, tab_relatorio, tab_legendas = st.tabs(
        ["📊 Painel", "💬 Chat", "📅 Calendário", "📢 Campanhas", "📋 Relatórios", "📸 Legendas"],
    )

    with tab_dash:
        render_dashboard()
        
    with tab_assistente:
        render_chat()
        
    with tab_calendario:
        render_calendario()
        
    with tab_campanhas:
        render_campanhas()
        
    with tab_relatorio:
        render_relatorios()
        
    with tab_legendas:
        render_legendas()

# Rodapé
st.markdown("""
<div class="app-footer">
    PlanejadorPV © 2025 — Ensina Mais Turma da Mônica · Unidade Tatuapé
</div>
""", unsafe_allow_html=True)
