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
from utils.firebase_store import carregar_fontes_meta
from utils.relatorios import resumo_conteudo
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
# Firestore é complementar: se disponível, usa metadados extras.
_FONTES_RESTAURADAS = 0

try:
    _rel = resumo_conteudo()
    _fontes_detalhadas = _rel.get("fontes_detalhadas") or []
    if _fontes_detalhadas:
        _meta_rebuild = {}
        for item in _fontes_detalhadas:
            chave = item["titulo"]
            if chave in _meta_rebuild:
                # Agrupar chunks de mesmo título
                _meta_rebuild[chave]["chunks"] += item["chunks"]
                _meta_rebuild[chave]["caracteres"] += item["caracteres"]
            else:
                _meta_rebuild[chave] = {
                    "fonte": item["fonte"],
                    "nome": item["titulo"],
                    "chunks": item["chunks"],
                    "caracteres": item["caracteres"],
                    "documento_id": item.get("documento_id", ""),
                }
        # Mescla com Firestore (metadados extras, se disponível)
        try:
            _meta_firebase = carregar_fontes_meta()
            if _meta_firebase:
                for chave, meta in _meta_firebase.items():
                    if chave in _meta_rebuild:
                        _meta_rebuild[chave].update(meta)
                    else:
                        _meta_rebuild[chave] = meta
        except Exception:
            pass
        st.session_state.documentos_meta = _meta_rebuild
        st.session_state.documentos = list(_meta_rebuild.keys())
        st.session_state._fontes_restauradas = True
        _FONTES_RESTAURADAS = len(_meta_rebuild)
    elif _recarregou > 0:
        # ChromaDB recarregou do Firestore mas resumo_conteudo não retornou fontes
        # Tenta reconstruir manualmente da collection
        logger.info("Tentando reconstruir metadados diretamente da collection...")
        try:
            _data = _get_docs_collection().get(include=["metadatas"])
            if _data and _data["ids"]:
                _meta_rebuild = {}
                for i, md in enumerate(_data["metadatas"]):
                    if md is None:
                        continue
                    titulo = md.get("arquivo") or md.get("url") or md.get("titulo") or f"documento_{i}"
                    fonte = md.get("fonte", "desconhecido")
                    if titulo not in _meta_rebuild:
                        _meta_rebuild[titulo] = {
                            "fonte": fonte,
                            "nome": titulo,
                            "chunks": 0,
                            "caracteres": 0,
                            "documento_id": md.get("documento_id", ""),
                        }
                    _meta_rebuild[titulo]["chunks"] += 1
                    _meta_rebuild[titulo]["caracteres"] += len(str(md.get("texto", "")))
                if _meta_rebuild:
                    st.session_state.documentos_meta = _meta_rebuild
                    st.session_state.documentos = list(_meta_rebuild.keys())
                    st.session_state._fontes_restauradas = True
                    _FONTES_RESTAURADAS = len(_meta_rebuild)
                    logger.info("Reconstrução manual: %d fontes", _FONTES_RESTAURADAS)
        except Exception as e:
            logger.warning("Reconstrução manual falhou: %s", e)
except Exception as e:
    logger.warning("Falha ao reconstruir fontes do ChromaDB: %s", e)
    _FONTES_RESTAURADAS = 0
    # Fallback: tenta só Firestore
    try:
        _meta_restaurado = carregar_fontes_meta()
        if _meta_restaurado:
            st.session_state.documentos_meta = _meta_restaurado
            st.session_state.documentos = list(_meta_restaurado.keys())
            st.session_state._fontes_restauradas = True
            _FONTES_RESTAURADAS = len(_meta_restaurado)
    except Exception:
        pass
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
