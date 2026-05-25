import logging
import os
import streamlit as st

logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="Marketing Planner",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="auto",
)

from dotenv import load_dotenv
from utils.documentos import _get_collection as _get_docs_collection
from utils.restore import reconstruir_fontes
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
# No Streamlit Cloud, o disco é efêmero — o ChromaDB morre no reboot.
# Por isso SEMPRE tentamos recarregar do Firestore.
try:
    collection = _get_docs_collection()
    _total_inicial = collection.count()
    _recarregou = 0
    if _total_inicial == 0:
        from utils.firebase_store import recarregar_chunks
        _recarregou = recarregar_chunks()
        if _recarregou > 0:
            logger.info("Firestore → ChromaDB: %d chunks restaurados", _recarregou)
except Exception as e:
    logger.warning("Não foi possível recarregar do Firestore: %s", e)
    _recarregou = 0

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

# ── Reconstruir lista de fontes do ChromaDB ──
# Toda vez que o session_state for recriado (reboot/redeploy),
# buscamos os metadados reais do banco vetorial.
from utils.restore import reconstruir_fontes

_meta_rebuild, _FONTES_RESTAURADAS = reconstruir_fontes(recarregou=_recarregou)
if _meta_rebuild:
    st.session_state.documentos_meta = _meta_rebuild
    st.session_state.documentos = list(_meta_rebuild.keys())
    st.session_state._fontes_restauradas = True

if "ultimo_calendario" not in st.session_state:
    st.session_state.ultimo_calendario = None
if "ultima_campanha" not in st.session_state:
    st.session_state.ultima_campanha = None

# Sidebar Ingestão de Arquivos
sidebar_upload()

# Abas Principais
with st.container():
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
