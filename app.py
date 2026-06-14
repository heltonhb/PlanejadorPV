import logging
import os
import streamlit as st

# Desabilitar telemetria do OpenTelemetry antes de qualquer import do chromadb
os.environ["OTEL_SDK_DISABLED"] = "true"
os.environ["OTEL_PYTHON_DISABLED"] = "true"

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

# ── Autenticação básica (opcional) ──
# Configure APP_PASSWORD no .env ou st.secrets["app_password"] para ativar
if not st.session_state.get("_auth_checked"):
    _env_pwd = os.getenv("APP_PASSWORD") or ""
    _sec_pwd = ""
    try:
        _sec_pwd = st.secrets.get("app_password", "")
    except Exception:
        pass
    APP_PASSWORD = _env_pwd or _sec_pwd
    st.session_state._app_password = APP_PASSWORD
    st.session_state._auth_checked = True

APP_PASSWORD = st.session_state.get("_app_password", "")

if APP_PASSWORD:
    if not st.session_state.get("authenticated", False):
        st.markdown(
            f"""
            <div style="display:flex;justify-content:center;align-items:center;min-height:80vh;">
            <div class="app-card" style="max-width:400px;width:100%;padding:2.5rem;text-align:center;">
            <div style="font-size:3rem;margin-bottom:1rem;">🔒</div>
            <h2 style="color:var(--primary);margin:0 0 0.5rem;">Acesso Restrito</h2>
            <p style="color:var(--on-surface-variant);font-size:0.9rem;margin-bottom:1.5rem;">
            Digite a senha para acessar o PlanejadorPV.</p>
            </div></div>
            """,
            unsafe_allow_html=True,
        )
        with st.container():
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                pwd = st.text_input("Senha", type="password", label_visibility="collapsed",
                                    placeholder="Digite a senha...")
                if st.button("Entrar", type="primary", use_container_width=True):
                    if pwd == APP_PASSWORD:
                        st.session_state.authenticated = True
                        st.rerun()
                    else:
                        st.error("❌ Senha incorreta.")
        st.stop()

# Inicialização da coleção ChromaDB
# No Streamlit Cloud, o disco é efêmero — o ChromaDB morre no reboot.
# Por isso SEMPRE tentamos recarregar do Firestore.
_recarregou = 0
_MAX_TENTATIVAS = 3
_collection = None
for _tentativa in range(_MAX_TENTATIVAS):
    try:
        _collection = _get_docs_collection()
        _total_inicial = _collection.count()
        if _total_inicial == 0:
            from utils.firebase_store import recarregar_chunks
            _recarregou = recarregar_chunks()
            if _recarregou > 0:
                logger.info("Firestore → ChromaDB: %d chunks restaurados", _recarregou)
        break
    except Exception as e:
        logger.warning("Tentativa %d/%d — Erro ao conectar ao ChromaDB: %s", _tentativa + 1, _MAX_TENTATIVAS, e)
        if _tentativa < _MAX_TENTATIVAS - 1:
            import time
            time.sleep(1)
        else:
            logger.error("Falha após %d tentativas. Algumas funcionalidades podem não estar disponíveis.", _MAX_TENTATIVAS)
            _collection = None

# Backfill automático: chunks legados sem documento_id recebem um
try:
    from utils.documentos import _backfill_documento_id
    _backfill_documento_id()
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

# ── Reconstruir lista de fontes do ChromaDB (apenas no boot) ──
# Só roda na primeira execução após restart/redeploy.
# A flag _restauracao_feita impede que o rebuild dispare novamente
# quando o usuário remove a última fonte (documentos ficaria vazio).
if not st.session_state.get("_restauracao_feita") and not st.session_state.documentos:
    from utils.restore import reconstruir_fontes

    _meta_rebuild, _FONTES_RESTAURADAS = reconstruir_fontes(recarregou=_recarregou)
    if _meta_rebuild:
        st.session_state.documentos_meta = _meta_rebuild
        st.session_state.documentos = list(_meta_rebuild.keys())
        st.session_state._fontes_restauradas = True
    st.session_state._restauracao_feita = True

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
