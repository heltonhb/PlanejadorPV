import os
from datetime import date
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from markdown_it import MarkdownIt

from utils.documentos import processar_documento, _get_collection as _get_docs_collection, sanitizar_id, salvar_resumo_documento
from utils.ingestao import processar_url, processar_html, processar_instagram, processar_texto, processar_planilha
from utils.ia_engine import perguntar
from utils.perguntas_sugeridas import PERGUNTAS_SUGERIDAS
from utils.calendario import gerar_calendario, MESES
from utils.campanhas import gerar_campanha, OBJETIVOS, PUBLICOS, SERVICOS
from utils.legendas_instagram import gerar_legenda, TOM_ESTILO
from utils.resumos import gerar_resumo
from utils.exportacao import exportar_relatorio_csv, exportar_markdown_docx

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
        --primary: #00A859;
        --primary-dark: #007A40;
        --primary-light: #4ADE80;
        --primary-container: #E8F5E9;
        --on-primary-container: #00210d;
        
        --secondary: #005CAA;
        --secondary-dark: #003F7A;
        --secondary-light: #3B82F6;
        --secondary-container: #E3F2FD;
        
        --tertiary: #F7B731;
        --tertiary-dark: #E09E1A;
        --tertiary-container: #FFFDE7;
        
        --danger: #E84C3D;
        --danger-dark: #C0392B;
        --danger-container: #FFEBEE;
        
        --background: #F8F9FA;
        --surface: #ffffff;
        --on-surface: #1A1C1E;
        --on-surface-variant: #44474E;
        
        --outline: #74777F;
        --outline-variant: #C4C6D0;
        
        --glass-bg: rgba(255, 255, 255, 0.7);
        --glass-border: rgba(255, 255, 255, 0.4);
        --glass-blur: blur(12px);
        
        --shadow-sm: 0 2px 4px rgba(0,0,0,0.05);
        --shadow-md: 0 4px 12px rgba(0,0,0,0.08);
        --shadow-lg: 0 12px 24px rgba(0,0,0,0.12);
        
        --radius-sm: 8px;
        --radius-md: 12px;
        --radius-lg: 16px;
        --radius-xl: 24px;
        
        --font-main: 'Inter', system-ui, -apple-system, sans-serif;
    }

    * { font-family: var(--font-main); }
    
    [data-testid="stAppViewContainer"] {
        background-color: var(--background);
    }

    /* ── Animations ── */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .animate-in {
        animation: fadeIn 0.4s ease-out forwards;
    }

    /* ── Layout ── */
    .stMainBlockContainer { 
        padding-top: 1.5rem !important; 
        max-width: 1240px !important;
    }

    /* ── Header ── */
    .app-header {
        background: linear-gradient(135deg, #006D38 0%, #00A859 100%);
        padding: 1.5rem 2rem;
        border-radius: var(--radius-lg);
        margin-bottom: 2rem;
        color: white;
        box-shadow: var(--shadow-lg);
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .app-header::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -10%;
        width: 400px;
        height: 400px;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        border-radius: 50%;
    }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background: #00210d !important;
        border-right: 1px solid rgba(255,255,255,0.05);
    }
    
    section[data-testid="stSidebar"] .stSidebarContent {
        padding: 1.5rem 1rem;
    }

    section[data-testid="stSidebar"] h2 {
        color: var(--primary-light);
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-bottom: 1rem;
        font-weight: 700;
        opacity: 0.8;
    }

    section[data-testid="stSidebar"] .stRadio label {
        background: transparent !important;
        border-radius: var(--radius-md) !important;
        color: rgba(255,255,255,0.7) !important;
        padding: 0.75rem 1rem !important;
        margin-bottom: 0.25rem !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        border: 1px solid transparent !important;
    }

    section[data-testid="stSidebar"] .stRadio label:hover {
        background: rgba(255,255,255,0.05) !important;
        color: white !important;
    }

    section[data-testid="stSidebar"] .stRadio label:has(input:checked) {
        background: rgba(0, 168, 89, 0.15) !important;
        color: var(--primary-light) !important;
        border: 1px solid rgba(0, 168, 89, 0.3) !important;
        font-weight: 600 !important;
    }

    /* ── Metric Cards ── */
    .metric-card {
        border-radius: var(--radius-lg);
        padding: 1.5rem;
        background: white;
        border: 1px solid var(--outline-variant);
        box-shadow: var(--shadow-sm);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: var(--shadow-lg);
        border-color: var(--primary);
    }

    .metric-card-val {
        font-size: 2.5rem;
        font-weight: 800;
        color: var(--on-surface);
        line-height: 1;
        margin-bottom: 0.5rem;
    }

    .metric-card-label {
        font-size: 0.85rem;
        font-weight: 600;
        color: var(--on-surface-variant);
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .metric-green { border-top: 4px solid var(--primary); }
    .metric-blue { border-top: 4px solid var(--secondary); }
    .metric-yellow { border-top: 4px solid var(--tertiary); }
    .metric-red { border-top: 4px solid var(--danger); }

    /* ── Custom Cards ── */
    .app-card {
        background: white;
        border: 1px solid var(--outline-variant);
        border-radius: var(--radius-lg);
        padding: 1.75rem;
        margin: 1.5rem 0;
        box-shadow: var(--shadow-sm);
        transition: box-shadow 0.3s ease;
    }
    
    .app-card:hover {
        box-shadow: var(--shadow-md);
    }

    /* ── Tabs ── */
    .stTabs [role="tablist"] {
        padding: 0.5rem;
        background: rgba(0, 0, 0, 0.03);
        border-radius: var(--radius-md);
        gap: 0.5rem;
    }
    
    .stTabs [role="tab"] {
        padding: 0.6rem 1.25rem;
        border-radius: var(--radius-sm);
        color: var(--on-surface-variant);
        font-weight: 600;
        transition: all 0.2s ease;
    }
    
    .stTabs [role="tab"][aria-selected="true"] {
        background: white !important;
        color: var(--primary) !important;
        box-shadow: var(--shadow-sm) !important;
    }

    /* ── Chat ── */
    div[data-testid="stChatMessage"] {
        padding: 1.25rem !important;
        border-radius: var(--radius-md) !important;
        margin-bottom: 1rem !important;
        border: 1px solid transparent !important;
    }

    div[data-testid="stChatMessage"][aria-label*="user"] {
        background: var(--primary-container) !important;
        border-color: rgba(0, 168, 89, 0.1) !important;
    }

    div[data-testid="stChatMessage"][aria-label*="assistant"] {
        background: white !important;
        border-color: var(--outline-variant) !important;
        box-shadow: var(--shadow-sm) !important;
    }

    /* ── Inputs ── */
    div[data-baseweb="input"], div[data-baseweb="select"], div[data-baseweb="textarea"] {
        border-radius: var(--radius-md) !important;
    }
    
    .stButton button {
        border-radius: var(--radius-md) !important;
        padding: 0.6rem 1.5rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }

    .stButton button[kind="primary"] {
        background: var(--primary) !important;
        border: none !important;
        box-shadow: 0 4px 14px 0 rgba(0, 168, 89, 0.3) !important;
    }

    .stButton button[kind="primary"]:hover {
        background: var(--primary-dark) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(0, 168, 89, 0.23) !important;
    }
    div.stButton > button:not([kind="primary"]) {
        border: 1px solid var(--info);
        color: var(--info);
        background: transparent;
    }
    div.stButton > button:not([kind="primary"]):hover:not(:disabled) {
        background: rgba(0, 92, 170, 0.05);
        border-color: var(--info-dark);
        color: var(--info-dark);
    }

    div[class*="st-key-sugestao_"] button {
        height: 100%;
        white-space: normal;
        word-break: break-word;
        text-align: left;
        padding: 0.6rem 0.85rem;
        font-size: 0.82rem;
        border-radius: var(--radius-sm);
        background: var(--surface-container-lowest) !important;
        border: 1px solid var(--outline-variant) !important;
        color: var(--on-surface-variant) !important;
        transition: all 0.15s ease;
    }
    /* ── Alerts ── */
    .stAlert { 
        border: 1px solid var(--outline-variant) !important;
        border-radius: var(--radius-md) !important;
        background: white !important;
    }
    
    div[data-testid="stAlert"] {
        padding: 1rem !important;
    }

    /* ── Tables ── */
    table {
        width: 100% !important;
        border-collapse: separate !important;
        border-spacing: 0 !important;
        margin: 1.5rem 0 !important;
        border: 1px solid var(--outline-variant) !important;
        border-radius: var(--radius-md) !important;
        overflow: hidden !important;
    }
    
    th {
        background-color: var(--surface-container-high, #f0f4f8) !important;
        color: var(--on-surface) !important;
        font-weight: 700 !important;
        padding: 1rem !important;
        text-align: left !important;
        border-bottom: 2px solid var(--outline-variant) !important;
    }
    
    td {
        padding: 0.85rem 1rem !important;
        border-bottom: 1px solid var(--outline-variant) !important;
        color: var(--on-surface-variant) !important;
    }

    /* ── Expander ── */
    div[data-testid="stExpander"] {
        border: 1px solid var(--outline-variant) !important;
        border-radius: var(--radius-md) !important;
        background: white !important;
        margin-bottom: 1rem !important;
    }

    /* ── Footer ── */
    .app-footer {
        text-align: center;
        color: var(--on-surface-variant);
        font-size: 0.85rem;
        padding: 3rem 0 2rem;
        opacity: 0.7;
    }

    /* ── Status Pulse ── */
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(0, 168, 89, 0.4); }
        70% { box-shadow: 0 0 0 10px rgba(0, 168, 89, 0); }
        100% { box-shadow: 0 0 0 0 rgba(0, 168, 89, 0); }
    }
    
    .status-pulse {
        width: 10px;
        height: 10px;
        background: var(--primary);
        border-radius: 50%;
        display: inline-block;
        margin-right: 8px;
        animation: pulse 2s infinite;
    }

    /* ── Mobile Optimization ── */
    @media (max-width: 640px) {
        .stMainBlockContainer { padding: 1rem !important; }
        .app-header { padding: 1.25rem !important; }
        .app-title { font-size: 1.25rem !important; }
        .metric-card-val { font-size: 2rem !important; }
        
        .stTabs [role="tablist"] {
            flex-wrap: nowrap !important;
            overflow-x: auto !important;
            padding: 0.25rem !important;
        }
        
        .stTabs [role="tab"] {
            padding: 0.5rem 1rem !important;
            font-size: 0.8rem !important;
        }
    }
</style>
<meta name="theme-color" content="#006D38">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="PV Planner">
<link rel="apple-touch-icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 512 512'%3E%3Crect width='512' height='512' rx='64' fill='%23006D38'/%3E%3Ctext x='256' y='340' text-anchor='middle' font-size='280' fill='white'%3E📊%3C/text%3E%3C/svg%3E">
<script>
(function(){
    var m = {
        name: "PlanejadorPV — Marketing Planner",
        short_name: "Mkt Planner",
        description: "Planejamento de marketing para franquias",
        start_url: ".",
        display: "standalone",
        background_color: "#0E1117",
        theme_color: "#006D38",
        orientation: "portrait-primary",
        categories: ["business","marketing"],
        icons: [{
            src: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 120 120'%3E%3Cdefs%3E%3ClinearGradient id='g' x1='0' y1='0' x2='1' y2='1'%3E%3Cstop offset='0%25' stop-color='%23006D38'/%3E%3Cstop offset='100%25' stop-color='%23004A25'/%3E%3C/linearGradient%3E%3C/defs%3E%3Ccircle cx='60' cy='60' r='58' fill='none' stroke='url(%23g)' stroke-width='2'/%3E%3Cpath d='M60 60 L60 10 A50 50 0 0 1 108 38 Z' fill='%2300A859'/%3E%3Cpath d='M60 60 L108 38 A50 50 0 0 1 86 104 Z' fill='%23F7B731'/%3E%3Cpath d='M60 60 L86 104 A50 50 0 0 1 60 110 Z' fill='%23006D38'/%3E%3Cpath d='M60 60 L60 110 A50 50 0 0 1 12 60 Z' fill='%23E84C3D'/%3E%3Cpath d='M60 60 L12 60 A50 50 0 0 1 60 10 Z' fill='%23E8F0FE'/%3E%3Ccircle cx='60' cy='60' r='8' fill='white' stroke='url(%23g)' stroke-width='2'/%3E%3Cpolyline points='32,84 48,68 58,74 74,54' fill='none' stroke='%2300A859' stroke-width='3.5'/%3E%3Cpolygon points='74,54 66,50 76,50' fill='%2300A859'/%3E%3C/svg%3E",
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
<script>
(function(){
    var sidebar = document.querySelector('section[data-testid="stSidebar"]');
    if (sidebar) {
        var observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(m) {
                if (m.type === 'attributes' && m.attributeName === 'aria-expanded') {
                    document.body.classList.toggle('sidebar-open', sidebar.getAttribute('aria-expanded') === 'true');
                }
            });
        });
        observer.observe(sidebar, { attributes: true, attributeFilter: ['aria-expanded'] });
        document.body.classList.toggle('sidebar-open', sidebar.getAttribute('aria-expanded') === 'true');
    }
})();
</script>
""", unsafe_allow_html=True)

import base64

def _load_svg_as_base64(path):
    try:
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
            return f"data:image/svg+xml;base64,{b64}"
    except Exception:
        return ""

logo_img = f'<img src="{_load_svg_as_base64("assets/logo.svg")}" alt="PlanejadorPV" style="height:80px;width:auto;max-width:380px;display:block;" />'

st.markdown(f"""
<div class="app-header animate-in">
    <div class="app-header-content" style="display: flex; justify-content: space-between; align-items: center; width: 100%;">
        <div style="display: flex; align-items: center; gap: 1.5rem;">
            <div style="flex-shrink:0; filter: drop-shadow(0 4px 8px rgba(0,0,0,0.2));">{logo_img}</div>
            <div>
                <div class="app-title" style="font-weight: 800; font-size: 1.8rem; color: white; letter-spacing: -0.5px;">Marketing Planner</div>
                <div class="app-subtitle" style="font-size: 0.9rem; opacity: 0.9; color: rgba(255,255,255,0.9); font-weight: 500;">Ensina Mais Turma da Mônica · Unidade Tatuapé</div>
            </div>
        </div>
        <div style="background: rgba(255, 255, 255, 0.15); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.25); padding: 0.6rem 1.25rem; border-radius: 100px; font-weight: 600; font-size: 0.9rem; color: white; display: flex; align-items: center; gap: 0.5rem; box-shadow: var(--shadow-sm);">
            <span class="status-pulse"></span>
            Olá, Gestor! 👋
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
if "legendas_geradas" not in st.session_state:
    st.session_state.legendas_geradas = []
if "legendas_imagens_b64" not in st.session_state:
    st.session_state.legendas_imagens_b64 = []
if "documentos_meta" not in st.session_state:
    st.session_state.documentos_meta = {}
if "ultimo_calendario" not in st.session_state:
    st.session_state.ultimo_calendario = None
if "ultima_campanha" not in st.session_state:
    st.session_state.ultima_campanha = None


def render_markdown_with_copy(markdown_text, key, label="📋 Copiar Markdown"):
    """Render markdown content with a copyable code block.
    
    Shows rendered markdown in a styled card, then a code block
    with Streamlit's native copy button (clipboard icon top-right).
    """
    st.markdown(
        f'<div class="app-card" style="margin-bottom: 0.5rem;">'
        f'{_md.render(markdown_text)}'
        f'</div>',
        unsafe_allow_html=True,
    )
    with st.expander(f"📋 {label} — clique para ver e copiar o texto", expanded=False):
        st.code(markdown_text, language="markdown")




def render_campaign_result_card(nome, objetivo, publico, servico, orcamento, canais, datas):
    if not nome:
        nome = f"Campanha: {objetivo}"
    
    budget_str = f"R$ {orcamento:,.2f}" if orcamento > 0 else "Não informado"
    dates_str = datas if datas else "Não informada"
    
    channel_pills = []
    if canais:
        for c in canais:
            c_clean = c.lower()
            if "insta" in c_clean:
                class_name = "channel-instagram"
            elif "face" in c_clean:
                class_name = "channel-facebook"
            elif "email" in c_clean or "e-mail" in c_clean:
                class_name = "channel-email"
            elif "whats" in c_clean:
                class_name = "channel-whatsapp"
            elif "sms" in c_clean:
                class_name = "channel-sms"
            elif "ads" in c_clean:
                class_name = "channel-ads"
            else:
                class_name = "channel-impresso"
            channel_pills.append(f'<span class="channel-pill {class_name}">{c}</span>')
    else:
        channel_pills.append('<span class="channel-pill channel-whatsapp">WhatsApp</span>')
        channel_pills.append('<span class="channel-pill channel-instagram">Instagram</span>')
        channel_pills.append('<span class="channel-pill channel-impresso">Material Impresso</span>')
    
    channels_html = f'<div class="campaign-channel-pills">{"".join(channel_pills)}</div>'
    
    metrics_map = {
        "Atrair novos alunos": "15+ novas matrículas",
        "Reaquecer leads antigos": "50+ contatos retomados",
        "Fidelizar alunos atuais": "95%+ taxa de renovação",
        "Divulgar novo serviço ou curso": "30+ demonstrações agendadas",
        "Promover matrículas (ação sazonal)": "25+ matrículas no período",
        "Gerar indicação de alunos": "20+ indicações de pais"
    }
    expected_metric = metrics_map.get(objetivo, "15+ leads qualificados")
    
    timeline_steps = [
        {"week": "Semana 1", "label": "Planejamento", "desc": "Criação dos criativos e disparos iniciais WhatsApp."},
        {"week": "Semana 2", "label": "Captação", "desc": "Postagem regular, anúncios online e landing page ativa."},
        {"week": "Semana 3", "label": "Vendas", "desc": "Contato telefônico com leads, agendamento de testes."},
        {"week": "Semana 4", "label": "Matrículas", "desc": "Fechamento na unidade Tatuapé e acolhimento dos alunos."}
    ]
    
    steps_html = ""
    for idx, step in enumerate(timeline_steps):
        steps_html += f"""
        <div class="timeline-step">
            <div class="timeline-icon">{idx+1}</div>
            <div class="timeline-label">{step['week']} - {step['label']}</div>
            <div class="timeline-desc">{step['desc']}</div>
        </div>
        """
        
    styles = """
    <style>
        .campaign-result-card {
            background: #ffffff !important;
            border: 1px solid var(--outline-variant) !important;
            border-radius: 12px !important;
            padding: 1.5rem !important;
            margin-top: 1rem !important;
            margin-bottom: 1.5rem !important;
            box-shadow: var(--shadow-md) !important;
            text-align: left !important;
            color: #343A40 !important;
        }
        .campaign-result-title {
            color: var(--primary) !important;
            font-weight: 800 !important;
            font-size: 1.4rem !important;
            margin-top: 0 !important;
            margin-bottom: 1rem !important;
            text-align: left !important;
        }
        .campaign-meta-grid {
            display: grid !important;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)) !important;
            gap: 1rem !important;
            margin-bottom: 1.5rem !important;
        }
        .campaign-meta-item {
            background: var(--surface-container) !important;
            padding: 0.75rem !important;
            border-radius: 8px !important;
            border: 1px solid var(--outline-variant) !important;
            text-align: left !important;
        }
        .campaign-meta-label {
            font-size: 0.72rem !important;
            color: var(--on-surface-variant) !important;
            text-transform: uppercase !important;
            font-weight: 600 !important;
        }
        .campaign-meta-value {
            font-size: 0.9rem !important;
            font-weight: 700 !important;
            color: var(--text-primary) !important;
            margin-top: 2px !important;
        }
        .campaign-channel-pills {
            display: flex !important;
            flex-wrap: wrap !important;
            gap: 6px !important;
            margin-top: 6px !important;
        }
        .channel-pill {
            font-size: 0.72rem !important;
            font-weight: 700 !important;
            padding: 4px 12px !important;
            border-radius: 20px !important;
            color: white !important;
            display: inline-block !important;
        }
        .channel-instagram { background-color: #E84C3D !important; }
        .channel-facebook { background-color: #005CAA !important; }
        .channel-email { background-color: #F7B731 !important; color: #343A40 !important; }
        .channel-whatsapp { background-color: #00A859 !important; }
        .channel-sms { background-color: #6C757D !important; }
        .channel-ads { background-color: #E09E1A !important; }
        .channel-impresso { background-color: #8E44AD !important; }
        
        .timeline-container {
            margin-top: 1.5rem !important;
            border-top: 1px solid var(--outline-variant) !important;
            padding-top: 1.5rem !important;
            text-align: left !important;
        }
        .timeline-title {
            font-size: 1rem !important;
            font-weight: 700 !important;
            color: var(--primary) !important;
            margin-bottom: 1rem !important;
            text-align: left !important;
        }
        .timeline-steps {
            display: flex !important;
            justify-content: space-between !important;
            position: relative !important;
            margin-bottom: 1rem !important;
            flex-wrap: nowrap !important;
        }
        .timeline-steps::before {
            content: '' !important;
            position: absolute !important;
            top: 20px !important;
            left: 12.5% !important;
            right: 12.5% !important;
            height: 4px !important;
            background: var(--outline-variant) !important;
            z-index: 1 !important;
        }
        .timeline-step {
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important;
            width: 25% !important;
            position: relative !important;
            z-index: 2 !important;
        }
        .timeline-icon {
            width: 40px !important;
            height: 40px !important;
            border-radius: 50% !important;
            background: var(--primary) !important;
            border: 3px solid white !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            font-weight: 800 !important;
            font-size: 0.95rem !important;
            color: white !important;
            box-shadow: var(--shadow-sm) !important;
        }
        .timeline-label {
            font-size: 0.8rem !important;
            font-weight: 700 !important;
            margin-top: 8px !important;
            text-align: center !important;
            color: var(--text-primary) !important;
        }
        .timeline-desc {
            font-size: 0.72rem !important;
            color: var(--on-surface-variant) !important;
            text-align: center !important;
            margin-top: 4px !important;
            max-width: 90% !important;
            line-height: 1.3 !important;
        }
        
        @media (max-width: 640px) {
            .timeline-steps { flex-wrap: wrap !important; gap: 1rem !important; }
            .timeline-steps::before { display: none !important; }
            .timeline-step { width: 100% !important; flex-direction: row !important; align-items: flex-start !important; text-align: left !important; }
            .timeline-label { margin-top: 0 !important; margin-left: 10px !important; text-align: left !important; }
            .timeline-desc { text-align: left !important; margin-top: 2px !important; margin-left: 10px !important; max-width: 100% !important; }
        }
    </style>
    """
    
    card_html = f"""
    {styles}
    <div class="campaign-result-card">
        <div class="campaign-result-title">📢 {nome}</div>
        <div class="campaign-meta-grid">
            <div class="campaign-meta-item">
                <div class="campaign-meta-label">Objetivo Principal</div>
                <div class="campaign-meta-value">{objetivo}</div>
            </div>
            <div class="campaign-meta-item">
                <div class="campaign-meta-label">Público-Alvo</div>
                <div class="campaign-meta-value">{publico}</div>
            </div>
            <div class="campaign-meta-item">
                <div class="campaign-meta-label">Serviço em Foco</div>
                <div class="campaign-meta-value">{servico}</div>
            </div>
            <div class="campaign-meta-item">
                <div class="campaign-meta-label">Orçamento Estimado</div>
                <div class="campaign-meta-value">{budget_str}</div>
            </div>
            <div class="campaign-meta-item">
                <div class="campaign-meta-label">Período Planejado</div>
                <div class="campaign-meta-value">{dates_str}</div>
            </div>
            <div class="campaign-meta-item">
                <div class="campaign-meta-label">Métrica Estimada</div>
                <div class="campaign-meta-value" style="color: var(--primary);">{expected_metric}</div>
            </div>
        </div>
        
        <div style="margin-bottom: 1rem; text-align: left;">
            <div class="campaign-meta-label">Canais de Divulgação</div>
            {channels_html}
        </div>
        
        <div class="timeline-container">
            <div class="timeline-title">📍 Cronograma e Fluxo Visual</div>
            <div class="timeline-steps">
                {steps_html}
            </div>
        </div>
    </div>
    """
    return card_html

def parse_instagram_options(markdown_content):
    import re
    header_indices = [m.start() for m in re.finditer(r'##\s*(?:Opção|opcao)\s*\d+', markdown_content, re.IGNORECASE)]
    
    options = []
    if len(header_indices) >= 2:
        for idx in range(len(header_indices)):
            start = header_indices[idx]
            end = header_indices[idx+1] if idx + 1 < len(header_indices) else len(markdown_content)
            options.append(markdown_content[start:end].strip())
    else:
        parts = markdown_content.split('---')
        for p in parts:
            p_clean = p.strip()
            if p_clean:
                options.append(p_clean)
                
    options = [o for o in options if o]
    return options if options else [markdown_content]

def render_instagram_mockup(index, title, content_markdown, img_base64_str):
    lines = content_markdown.strip().split('\n')
    body_lines = []
    hashtags = ""
    
    for line in lines:
        if line.strip().lower().startswith("##"):
            continue
        if "hashtags:" in line.lower() or "#" in line:
            if "#" in line:
                hashtags += " " + line.replace("**Hashtags:**", "").replace("Hashtags:", "").strip()
        else:
            body_lines.append(line)
            
    body_text = "\n".join(body_lines).strip()
    
    if not hashtags:
        import re
        all_tags = re.findall(r'#\w+', content_markdown)
        if all_tags:
            hashtags = " ".join(all_tags)
            for tag in all_tags:
                body_text = body_text.replace(tag, "")
            body_text = body_text.strip()
            
    if not body_text:
        body_text = content_markdown
        
    caption_id = f"insta-caption-{index}"
    btn_id = f"insta-btn-{index}"
    
    if img_base64_str:
        image_html = f'<img src="{img_base64_str}" class="instagram-image" />'
    else:
        image_html = f"""
        <div style="width:100% !important; height:250px !important; background: linear-gradient(135deg, #00A859, #005CAA) !important; display:flex !important; flex-direction:column !important; align-items:center !important; justify-content:center !important; color:white !important; padding: 20px !important; text-align:center !important;">
            <span style="font-size: 3rem !important;">📸</span>
            <span style="font-size: 0.95rem !important; font-weight:700 !important; margin-top:10px !important; color: white !important;">Ensina Mais Turma da Mônica</span>
            <span style="font-size: 0.8rem !important; opacity:0.8 !important; margin-top:4px !important; color: white !important;">Unidade Tatuapé</span>
        </div>
        """
        
    styles = """
    <style>
        .instagram-card {
            background: #ffffff !important;
            border: 1px solid #dbdbdb !important;
            border-radius: 12px !important;
            max-width: 470px !important;
            margin: 1.5rem auto !important;
            box-shadow: 0px 4px 12px rgba(0,0,0,0.05) !important;
            overflow: hidden !important;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
            color: #262626 !important;
            text-align: left !important;
        }
        .instagram-header {
            display: flex !important;
            align-items: center !important;
            padding: 12px 16px !important;
            border-bottom: 1px solid #efefef !important;
        }
        .instagram-avatar {
            width: 32px !important;
            height: 32px !important;
            border-radius: 50% !important;
            background: linear-gradient(45deg, #f09433 0%, #e6683c 25%, #dc2743 50%, #cc2366 75%, #bc1888 100%) !important;
            padding: 2px !important;
            margin-right: 10px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
        }
        .instagram-avatar-inner {
            width: 100% !important;
            height: 100% !important;
            border-radius: 50% !important;
            background: #00A859 !important;
            color: white !important;
            font-weight: bold !important;
            font-size: 10px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            border: 2px solid white !important;
        }
        .instagram-userinfo {
            display: flex !important;
            flex-direction: column !important;
        }
        .instagram-username {
            font-weight: 600 !important;
            font-size: 13px !important;
            color: #262626 !important;
            line-height: 1.2 !important;
        }
        .instagram-location {
            font-size: 11px !important;
            color: #8e8e8e !important;
        }
        .instagram-image-container {
            width: 100% !important;
            max-height: 470px !important;
            overflow: hidden !important;
            background-color: #fafafa !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
        }
        .instagram-image {
            width: 100% !important;
            height: auto !important;
            display: block !important;
            object-fit: cover !important;
        }
        .instagram-actions {
            display: flex !important;
            justify-content: space-between !important;
            padding: 12px 16px 8px 16px !important;
            font-size: 1.3rem !important;
            cursor: pointer !important;
        }
        .instagram-actions-left {
            display: flex !important;
            gap: 16px !important;
        }
        .instagram-likes {
            padding: 0 16px 8px 16px !important;
            font-size: 13px !important;
            font-weight: 500 !important;
            color: #262626 !important;
        }
        .instagram-caption-container {
            padding: 0 16px 16px 16px !important;
            font-size: 13px !important;
            line-height: 1.5 !important;
            color: #262626 !important;
        }
        .instagram-caption-text {
            word-break: break-word !important;
            white-space: pre-wrap !important;
        }
        .instagram-caption-text strong {
            color: #262626 !important;
            margin-right: 6px !important;
        }
        .instagram-hashtags {
            color: #00376b !important;
            margin-top: 8px !important;
            font-weight: 500 !important;
            word-break: break-word !important;
        }
        .instagram-copy-btn {
            display: block !important;
            width: 100% !important;
            margin-top: 14px !important;
            padding: 8px 12px !important;
            background-color: var(--primary) !important;
            background: linear-gradient(135deg, var(--primary), var(--primary-dark)) !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            font-size: 12px !important;
            font-weight: 600 !important;
            cursor: pointer !important;
            transition: all 0.2s ease !important;
            text-align: center !important;
            box-shadow: 0px 2px 4px rgba(0, 168, 89, 0.1) !important;
        }
        .instagram-copy-btn:hover {
            background: linear-gradient(135deg, var(--primary-dark), #005a30) !important;
            box-shadow: 0px 4px 8px rgba(0, 168, 89, 0.2) !important;
            transform: translateY(-1px) !important;
        }
    </style>
    """

    script_html = """
    <script>
    if (typeof window.copyCaptionText !== 'function') {
        window.copyCaptionText = function(captionId, btnId) {
            const captionEl = document.getElementById(captionId);
            if (!captionEl) return;
            const bodyEl = captionEl.querySelector('.caption-body');
            const tagsEl = captionEl.nextElementSibling;
            
            let textToCopy = '';
            if (bodyEl) {
                textToCopy += bodyEl.innerText.trim();
            } else {
                textToCopy += captionEl.innerText.replace('ensinamais.tatuape', '').trim();
            }
            
            if (tagsEl && tagsEl.classList.contains('instagram-hashtags')) {
                textToCopy += '\\n\\n' + tagsEl.innerText.trim();
            }
            
            function showSuccess(bId) {
                const btn = document.getElementById(bId);
                if (!btn) return;
                const originalText = btn.innerHTML;
                btn.innerHTML = "✅ Copiado!";
                btn.style.backgroundColor = "#00A859";
                btn.style.color = "white";
                setTimeout(() => {
                    btn.innerHTML = originalText;
                    btn.style.backgroundColor = "";
                    btn.style.color = "";
                }, 2000);
            }
            
            function fallbackCopy(text, bId) {
                const textArea = document.createElement("textarea");
                textArea.value = text;
                textArea.style.position = "fixed";
                document.body.appendChild(textArea);
                textArea.focus();
                textArea.select();
                try {
                    document.execCommand('copy');
                    showSuccess(bId);
                } catch (err) {
                    console.error('Fallback copy failed', err);
                    alert('Não foi possível copiar a legenda automaticamente.');
                }
                document.body.removeChild(textArea);
            }
            
            if (navigator.clipboard && window.isSecureContext) {
                navigator.clipboard.writeText(textToCopy).then(() => {
                    showSuccess(btnId);
                }).catch(err => {
                    fallbackCopy(textToCopy, btnId);
                });
            } else {
                fallbackCopy(textToCopy, btnId);
            }
        };
    }
    </script>
    """
        
    html = f"""
    {styles}
    {script_html}
    <div class="instagram-card">
        <div class="instagram-header">
            <div class="instagram-avatar">
                <div class="instagram-avatar-inner">EM</div>
            </div>
            <div class="instagram-userinfo">
                <span class="instagram-username">ensinamais.tatuape</span>
                <span class="instagram-location">Tatuapé, São Paulo</span>
            </div>
        </div>
        <div class="instagram-image-container">
            {image_html}
        </div>
        <div class="instagram-actions">
            <div class="instagram-actions-left">
                <span>❤️</span>
                <span>💬</span>
                <span>✈️</span>
            </div>
            <div>
                <span>🔖</span>
            </div>
        </div>
        <div class="instagram-likes">
            Curtido por <strong>ensinamais.tatuape</strong> e outras pessoas
        </div>
        <div class="instagram-caption-container">
            <div class="instagram-caption-text" id="{caption_id}"><strong>ensinamais.tatuape</strong> <span class="caption-body">{body_text}</span></div>
            <div class="instagram-hashtags">{hashtags}</div>
            <button class="instagram-copy-btn" id="{btn_id}" onclick="copyCaptionText('{caption_id}', '{btn_id}')">
                📋 Copiar Legenda
            </button>
        </div>
    </div>
    """
    return html

def exibir_fontes(fontes: list[dict]):
    seen = set()
    chips_html = []
    for f in fontes:
        label = f.get("arquivo") or f.get("url") or f.get("perfil") or f.get("fonte", "?")
        if len(label) > 25:
            label = label[:22] + "..."
        chave = (label, f["fonte"])
        if chave not in seen:
            seen.add(chave)
            colors = {
                "pdf": ("#00A859", "#ffffff"),
                "url": ("#005CAA", "#ffffff"),
                "html": ("#005CAA", "#ffffff"),
                "instagram": ("#E84C3D", "#ffffff"),
                "texto": ("#F7B731", "#343A40"),
                "planilha": ("#007A40", "#ffffff")
            }
            bg, text_color = colors.get(f["fonte"].lower(), ("#6C757D", "#ffffff"))
            chips_html.append(
                f'<span style="display: inline-block; padding: 4px 10px; border-radius: 20px; '
                f'background-color: {bg}; color: {text_color}; font-size: 0.75rem; font-weight: 600; '
                f'margin-right: 8px; margin-bottom: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">'
                f'{f["fonte"].upper()}: {label}'
                f'</span>'
            )
            
    if chips_html:
        st.markdown(
            f'<div style="margin-top: 8px; margin-bottom: 12px; display: flex; flex-wrap: wrap; align-items: center;">'
            f'<span style="font-size: 0.8rem; color: #6C757D; margin-right: 8px; font-weight: 600;">Fontes citadas:</span>'
            f'{"".join(chips_html)}'
            f'</div>',
            unsafe_allow_html=True
        )


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
                st.caption(f"{chunks} chunks")
            with col2:
                if st.button("🗑️", key=f"del_{chave}", help="Remover esta fonte"):
                    colecao = _get_docs_collection()
                    try:
                        colecao.delete(where={"documento_id": meta["documento_id"]})
                    except Exception:
                        pass
                    st.session_state.documentos.remove(chave)
                    st.session_state.documentos_meta.pop(chave, None)
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


sidebar_upload()

with st.container(key="main_tabs"):
    tab_dash, tab_assistente, tab_calendario, tab_campanhas, tab_relatorio, tab_legendas = st.tabs(
        ["📊 Painel", "💬 Chat", "📅 Calendário", "📢 Campanhas", "📋 Relatórios", "📸 Legendas"],
    )

with tab_dash:
    st.markdown('<div class="animate-in">', unsafe_allow_html=True)
    st.markdown(
        '<div class="app-card" style="margin-bottom: 2rem;">'
        '<h2 style="margin:0; color: var(--primary);">📊 Visão Geral do Painel</h2>'
        '<p style="color: var(--on-surface-variant); margin-top: 0.5rem; font-size: 0.95rem;">'
        'Acompanhe o status da sua base de conhecimento e as atividades recentes.</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    try:
        collection = _get_docs_collection()
        total_chunks = collection.count()
    except Exception:
        total_chunks = 0

    total_perguntas = len([m for m in st.session_state.mensagens if m["role"] == "user"])
    total_calendarios = st.session_state.get("calendarios_gerados", 0)
    total_campanhas = st.session_state.get("campanhas_geradas", 0)
    total_conteudos = total_calendarios + total_campanhas + len(st.session_state.legendas_geradas)
    total_fontes = len(st.session_state.documentos)

    col1, col2, col3, col4 = st.columns(4)
    col1.markdown(
        f'<div class="metric-card metric-green animate-in" style="animation-delay: 0.1s;">'
        f'<div class="metric-card-label">📁 Fontes Ativas</div>'
        f'<div class="metric-card-val">{total_fontes}</div>'
        f'<div style="font-size: 0.75rem; color: var(--primary); font-weight: 700;">↑ Pronto para consulta</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
    col2.markdown(
        f'<div class="metric-card metric-blue animate-in" style="animation-delay: 0.15s;">'
        f'<div class="metric-card-label">📄 Fragmentos (RAG)</div>'
        f'<div class="metric-card-val">{total_chunks}</div>'
        f'<div style="font-size: 0.75rem; color: var(--secondary); font-weight: 700;">Conhecimento indexado</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
    col3.markdown(
        f'<div class="metric-card metric-yellow animate-in" style="animation-delay: 0.2s;">'
        f'<div class="metric-card-label">💬 Interações</div>'
        f'<div class="metric-card-val">{total_perguntas}</div>'
        f'<div style="font-size: 0.75rem; color: var(--tertiary-dark); font-weight: 700;">Perguntas respondidas</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
    col4.markdown(
        f'<div class="metric-card metric-red animate-in" style="animation-delay: 0.25s;">'
        f'<div class="metric-card-label">✨ Ativos Criados</div>'
        f'<div class="metric-card-val">{total_conteudos}</div>'
        f'<div style="font-size: 0.75rem; color: var(--danger); font-weight: 700;">Conteúdos gerados</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    col_chart1, col_chart2 = st.columns(2)
    with col_chart1:
        st.markdown(
            f'<div class="app-card animate-in" style="animation-delay: 0.3s; display:flex;flex-direction:column;justify-content:center;align-items:center;height:100%;padding:1.75rem;">'
            f'<h3 style="margin-top: 0; margin-bottom: 1.5rem; color: var(--on-surface); width:100%; font-weight:700;">📊 Distribuição das Fontes</h3>'
            f'<img src="{_load_svg_as_base64("assets/pizza_chart.svg")}" alt="Distribuição por categoria" style="max-width:100%;height:auto;max-height:220px;display:block;margin:auto;" />'
            f'</div>',
            unsafe_allow_html=True,
        )
    with col_chart2:
        st.markdown(
            f'<div class="app-card animate-in" style="animation-delay: 0.35s; display:flex;flex-direction:column;justify-content:center;height:100%;padding:1.75rem;">'
            f'<h3 style="margin-top: 0; margin-bottom: 1.5rem; color: var(--on-surface); font-weight:700;">📈 Conteúdos por Categoria</h3>'
            f'<div style="margin-bottom: 1rem;">'
            f'<div style="display: flex; justify-content: space-between; font-size: 0.85rem; font-weight: 600; margin-bottom: 0.25rem; color: var(--on-surface-variant);">'
            f'<span>📅 Calendários</span>'
            f'<span>42%</span>'
            f'</div>'
            f'<div style="background: var(--primary-container); border-radius: 6px; height: 12px; overflow: hidden; width: 100%;">'
            f'<div style="background: linear-gradient(90deg, var(--primary), var(--primary-dark)); width: 42%; height: 100%; border-radius: 6px;"></div>'
            f'</div>'
            f'</div>'
            f'<div style="margin-bottom: 1rem;">'
            f'<div style="display: flex; justify-content: space-between; font-size: 0.85rem; font-weight: 600; margin-bottom: 0.25rem; color: var(--on-surface-variant);">'
            f'<span>📢 Campanhas</span>'
            f'<span>28%</span>'
            f'</div>'
            f'<div style="background: var(--secondary-container); border-radius: 6px; height: 12px; overflow: hidden; width: 100%;">'
            f'<div style="background: linear-gradient(90deg, var(--secondary), var(--secondary-dark)); width: 28%; height: 100%; border-radius: 6px;"></div>'
            f'</div>'
            f'</div>'
            f'<div style="margin-bottom: 1rem;">'
            f'<div style="display: flex; justify-content: space-between; font-size: 0.85rem; font-weight: 600; margin-bottom: 0.25rem; color: var(--on-surface-variant);">'
            f'<span>📸 Legendas</span>'
            f'<span>18%</span>'
            f'</div>'
            f'<div style="background: var(--tertiary-container); border-radius: 6px; height: 12px; overflow: hidden; width: 100%;">'
            f'<div style="background: linear-gradient(90deg, var(--tertiary), var(--tertiary-dark)); width: 18%; height: 100%; border-radius: 6px;"></div>'
            f'</div>'
            f'</div>'
            f'<div style="margin-bottom: 0.5rem;">'
            f'<div style="display: flex; justify-content: space-between; font-size: 0.85rem; font-weight: 600; margin-bottom: 0.25rem; color: var(--on-surface-variant);">'
            f'<span>📋 Análises</span>'
            f'<span>12%</span>'
            f'</div>'
            f'<div style="background: var(--danger-container); border-radius: 6px; height: 12px; overflow: hidden; width: 100%;">'
            f'<div style="background: linear-gradient(90deg, var(--danger), var(--danger-dark)); width: 12%; height: 100%; border-radius: 6px;"></div>'
            f'</div>'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    if st.session_state.documentos:
        st.markdown(
            '<h3 style="margin-bottom:1rem; margin-top: 2rem; color: var(--on-surface);">📂 Fontes carregadas</h3>',
            unsafe_allow_html=True,
        )
        cols = st.columns(2)
        icones = {"pdf": "📄", "url": "🔗", "html": "🌐", "instagram": "📷", "texto": "📝", "planilha": "📊"}
        for i, chave in enumerate(st.session_state.documentos):
            meta = st.session_state.documentos_meta.get(chave)
            if meta:
                fonte = meta["fonte"]
                nome = meta.get("nome", chave)
                icone = icones.get(fonte, "📄")
                extra = ""
                if "paginas" in meta:
                    extra = f" · {meta['paginas']} páginas"
                elif "posts" in meta:
                    extra = f" · {meta['posts']} posts"
                elif "url" in meta:
                    extra = f" · URL"
                cols[i % 2].markdown(
                    f'<div class="app-card animate-in" style="animation-delay: {0.4 + i*0.05}s; padding:1rem 1.25rem; margin: 0.5rem 0;">'
                    f'<strong style="color: var(--on-surface);">{icone} {nome}</strong><br>'
                    f'<small style="color:var(--on-surface-variant); font-size: 0.8rem;">'
                    f'{meta.get("chunks", "?")} chunks · {meta.get("caracteres", 0):,} caracteres{extra}'
                    f'</small></div>',
                    unsafe_allow_html=True,
                )
            else:
                cols[i % 2].markdown(f"- {chave}")
    else:
        st.markdown(
            '<div class="app-card-empty animate-in" style="animation-delay: 0.4s; padding: 3.5rem 1.5rem; text-align: center; border-radius: var(--radius-lg); border: 2px dashed var(--outline-variant); background: white; margin: 1.5rem 0;">'
            '<div style="font-size: 4rem; margin-bottom: 1rem; display: inline-block;">📚</div>'
            '<h3 style="color: var(--on-surface); margin-top: 0.5rem; margin-bottom: 0.5rem; font-weight:700;">Nenhuma fonte carregada</h3>'
            '<p style="color: var(--on-surface-variant); font-size: 0.95rem; margin: 0;">'
            'Use a barra lateral para adicionar PDFs, URLs, HTMLs, perfis de Instagram, textos ou planilhas e comece a analisar!'
            '</p>'
            '</div>',
            unsafe_allow_html=True,
        )

    st.markdown(
        '<div class="app-card animate-in" style="animation-delay: 0.45s; padding:1rem 1.25rem; margin-top: 2rem;">'
        '<div style="display:flex;gap:0.75rem;align-items:center;flex-wrap:wrap;">'
        '<span style="font-size:1.5rem;">💡</span>'
        '<span style="font-size:0.9rem;color:var(--on-surface-variant);">'
        'Explore as abas <strong>💬 Chat</strong> para interagir com seus documentos, '
        '<strong>📅 Calendário</strong> para organizar suas ações mensais, '
        '<strong>📢 Campanhas</strong> para criar estratégias completas, '
        'ou <strong>📸 Legendas</strong> para gerar conteúdo visual para o Instagram.'
        '</span></div></div>',
        unsafe_allow_html=True,
    )

    st.divider()
    with st.expander("📂 Adicionar fonte (dispositivos móveis)", expanded=False):
        st.markdown(
            "*No computador, use a barra lateral. Aqui você também pode adicionar fontes.*"
        )
        aba_mobile = st.radio("Tipo", ["PDF", "URL", "HTML", "Instagram", "Texto", "Planilha"], key="mobile_aba")
        _render_upload_tab(st, aba_mobile, key_prefix="mob_")
st.markdown('</div>', unsafe_allow_html=True)

with tab_assistente:
    st.markdown('<div class="animate-in">', unsafe_allow_html=True)
    col_titulo, col_limpar = st.columns([0.85, 0.15])
    with col_titulo:
        st.markdown(
            '<div class="app-card" style="margin-bottom: 2rem;">'
            '<h2 style="margin:0; color: var(--primary);">💬 Assistente de Marketing</h2>'
            '<p style="color: var(--on-surface-variant); margin-top: 0.5rem; font-size: 0.95rem;">'
            'Carregue informações na barra lateral e faça perguntas sobre o conteúdo para gerar insights e materiais.</p>'
            '</div>',
            unsafe_allow_html=True,
        )
    with col_limpar:
        if st.session_state.mensagens:
            if st.button("🗑️ Limpar conversa", use_container_width=True, help="Apaga todo o histórico da conversa atual."):
                st.session_state.mensagens = []
                st.session_state.sugestoes_usadas = False
                st.rerun()

    if not st.session_state.mensagens and not st.session_state.sugestoes_usadas:
        with st.container(border=False):
            st.markdown(
                '<h3 style="margin-bottom:0.75rem; color: var(--on-surface);">💡 Sugestões de perguntas</h3>'
                '<p style="color:var(--on-surface-variant);margin:0 0 1.5rem 0; font-size: 0.95rem;">'
                'Clique em uma pergunta abaixo para começar uma conversa:</p>',
                unsafe_allow_html=True,
            )

            for idx_cat, grupo in enumerate(PERGUNTAS_SUGERIDAS):
                st.markdown(f"<h4 style=\"margin-top: 1.5rem; margin-bottom: 0.75rem; color: var(--on-surface);\">{grupo['categoria']}</h4>", unsafe_allow_html=True)
                cols = st.columns(3)
                for i, pergunta in enumerate(grupo["perguntas"]):
                    with cols[i % 3]:
                        if st.button(
                            pergunta, key=f"sugestao_{idx_cat}_{i}",
                            use_container_width=True,
                        ):
                            st.session_state.sugestoes_usadas = True
                            st.session_state.mensagens.append({"role": "user", "content": pergunta})
                            with st.chat_message("user"):
                                st.markdown(pergunta)
                            with st.chat_message("assistant"):
                                with st.spinner("Consultando fontes..."):
                                    resultado = perguntar(pergunta)
                                st.markdown(resultado["resposta"], unsafe_allow_html=True)
                                if resultado["fontes"]:
                                    exibir_fontes(resultado["fontes"])
                            st.session_state.mensagens.append({
                                "role": "assistant", "content": resultado["resposta"],
                                "fontes": resultado["fontes"],
                            })
                            st.rerun()

    for i, msg in enumerate(st.session_state.mensagens):
        with st.chat_message(msg["role"]):
            st.markdown(f'<div class="animate-in" style="animation-delay: {0.1 + i*0.05}s;">{msg["content"]}</div>', unsafe_allow_html=True)
            if msg["role"] == "assistant" and msg.get("fontes"):
                exibir_fontes(msg["fontes"])
            if msg["role"] == "assistant" and i == len(st.session_state.mensagens) - 1:
                col_exp, col_base = st.columns(2)
                with col_exp:
                    docx_bytes = exportar_markdown_docx(msg["content"])
                    st.download_button(
                        "📥 Baixar DOCX",
                        data=docx_bytes,
                        file_name="resposta_assistente.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True,
                        key=f"exp_msg_{i}",
                    )
                with col_base:
                    if st.button("📚 Incluir na base", key=f"inc_msg_{i}", use_container_width=True):
                        with st.spinner("Adicionando à base de conhecimento..."):
                            proc = processar_texto(
                                msg["content"],
                                titulo=f"Resposta do assistente #{i}",
                            )
                        if proc["status"] == "ok":
                            st.success(f"✅ Adicionado ({proc['total_chunks']} chunks).")
                        else:
                            st.error(f"❌ {proc['mensagem']}")
                with st.expander("📋 Copiar resposta — clique para ver e copiar o texto", expanded=False):
                    st.code(msg["content"], language="markdown")

    if prompt := st.chat_input("Faça uma pergunta sobre os documentos..."):
        st.session_state.mensagens.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(f'<div class="animate-in">{prompt}</div>', unsafe_allow_html=True)

        with st.chat_message("assistant"):
            with st.spinner("Consultando fontes..."):
                resultado = perguntar(prompt)
            st.markdown(f'<div class="animate-in">{resultado["resposta"]}</div>', unsafe_allow_html=True)
            if resultado["fontes"]:
                exibir_fontes(resultado["fontes"])
        st.session_state.mensagens.append({
            "role": "assistant", "content": resultado["resposta"],
            "fontes": resultado["fontes"],
        })
    st.markdown('</div>', unsafe_allow_html=True)

with tab_calendario:
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

with tab_campanhas:
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
                st.session_state.ultima_campanha = resultado["conteudo"]
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
    if st.session_state.get("ultima_campanha"):
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
            st.session_state.ultima_campanha,
            key="camp_copy",
            label="Copiar Campanha",
        )
    st.markdown('</div>', unsafe_allow_html=True)

with tab_relatorio:
    st.markdown('<div class="animate-in">', unsafe_allow_html=True)
    st.markdown(
        '<div class="app-card" style="margin-bottom: 2rem;">'
        '<h2 style="margin:0; color: var(--primary);">📋 Relatório de Conteúdo Ingerido</h2>'
        '<p style="color: var(--on-surface-variant); margin-top: 0.5rem; font-size: 0.95rem;">'
        'Visão detalhada de todo o conteúdo gerado e das fontes carregadas.</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    # Database RAG status section
    st.divider()
    st.markdown(
        '<div class="app-card" style="margin-top: 2rem; margin-bottom: 2rem;">'
        '<h3 style="margin-top:0; color: var(--on-surface);">📁 Base de Dados & Fontes Ingeridas (RAG)</h3>'
        '<p style="color: var(--on-surface-variant); margin-top: 0.5rem; font-size: 0.95rem;">'
        'Abaixo você confere o status e detalhamento dos arquivos importados na base vetorial (Chroma).</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    from utils.relatorios import resumo_conteudo
    relatorio = resumo_conteudo()

    if relatorio["total_chunks"] == 0:
        st.markdown(
            '<div class="app-card-empty animate-in" style="padding: 3.5rem 1.5rem; text-align: center; border-radius: var(--radius-lg); border: 2px dashed var(--outline-variant); background: white; margin: 1.5rem 0;">'
            '<div style="font-size: 4rem; margin-bottom: 1rem; display: inline-block;">📂</div>'
            '<h3 style="color: var(--on-surface); margin-top: 0.5rem; margin-bottom: 0.5rem; font-weight:700;">Nenhuma fonte na base de conhecimento (RAG)</h3>'
            '<p style="color: var(--on-surface-variant); font-size: 0.95rem; margin: 0;">'
            'Carregue fontes pela barra lateral ou pelo Dashboard para personalizar os conteúdos.'
            '</p>'
            '</div>',
            unsafe_allow_html=True,
        )
    else:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(
                f'<div class="app-card animate-in" style="animation-delay: 0.1s; text-align:center;padding:1.25rem 1rem;">'
                f'<div style="font-size:2.2rem;font-weight:800;color:var(--primary);">'
                f'{relatorio["total_chunks"]}</div>'
                f'<div style="font-size:0.85rem;color:var(--on-surface-variant);font-weight:500;">'
                f'📄 Total de chunks</div></div>',
                unsafe_allow_html=True,
            )
        with col2:
            st.markdown(
                f'<div class="app-card animate-in" style="animation-delay: 0.15s; text-align:center;padding:1.25rem 1rem;">'
                f'<div style="font-size:2.2rem;font-weight:800;color:var(--primary);">'
                f'{relatorio["total_caracteres"]:,}</div>'
                f'<div style="font-size:0.85rem;color:var(--on-surface-variant);font-weight:500;">'
                f'📏 Total de caracteres</div></div>',
                unsafe_allow_html=True,
            )
        with col3:
            st.markdown(
                f'<div class="app-card animate-in" style="animation-delay: 0.2s; text-align:center;padding:1.25rem 1rem;">'
                f'<div style="font-size:2.2rem;font-weight:800;color:var(--primary);">'
                f'{len(relatorio["por_fonte"])}</div>'
                f'<div style="font-size:0.85rem;color:var(--on-surface-variant);font-weight:500;">'
                f'🗂️ Tipos de fonte</div></div>',
                unsafe_allow_html=True,
            )

        st.markdown(
            '<h4 style="margin-top: 2rem; margin-bottom:1rem;font-weight:700; color: var(--on-surface);">📊 Distribuição por tipo de fonte</h4>',
            unsafe_allow_html=True,
        )

        por_fonte_items = sorted(relatorio["por_fonte"].items())
        cols_fonte = st.columns(len(por_fonte_items))
        icones_f = {"pdf": "📄", "url": "🔗", "html": "🌐", "instagram": "📷", "texto": "📝", "planilha": "📊"}
        nomes_f = {"pdf": "PDF", "url": "URL", "html": "HTML", "instagram": "Instagram", "texto": "Texto", "planilha": "Planilha"}
        for idx, (fonte, dados) in enumerate(por_fonte_items):
            with cols_fonte[idx]:
                icone = icones_f.get(fonte, "📄")
                nome = nomes_f.get(fonte, fonte.capitalize())
                st.markdown(
                    f'<div class="app-card animate-in" style="animation-delay: {0.25 + idx*0.05}s; text-align:center;padding:1rem;">'
                    f'<div style="font-size:1.4rem;font-weight:800;color:var(--primary);">'
                    f'{dados["chunks"]}</div>'
                    f'<div style="font-size:0.8rem;color:var(--on-surface-variant);font-weight:500;">'
                    f'{icone} {nome}</div>'
                    f'<div style="font-size:0.75rem;color:var(--on-surface-variant);">'
                    f'{dados["caracteres"]:,} caracteres</div></div>',
                    unsafe_allow_html=True,
                )

        st.markdown(
            '<h4 style="margin-top: 2rem; margin-bottom:1rem;font-weight:700; color: var(--on-surface);">📋 Detalhamento por documento</h4>',
            unsafe_allow_html=True,
        )

        for idx, item in enumerate(relatorio["fontes_detalhadas"]):
            documento_id = item.get("documento_id")
            resumo = item.get("resumo", "")
            resumo_html = ""
            if resumo:
                resumo_html = f'<br><span style="color: var(--on-surface-variant); font-size: 0.82rem; font-style: italic;">{resumo}</span>'

            c1, c2 = st.columns([5, 1])
            with c1:
                st.markdown(
                    f'<div class="app-card animate-in" style="animation-delay: {0.35 + idx*0.05}s; padding: 0.75rem 1rem;">'
                    f'<span style="font-size: 1.1rem; font-weight: 600;">{item["icone"]} {item["titulo"]}</span><br>'
                    f'<span style="color: var(--on-surface-variant); font-size: 0.85rem;">'
                    f'{item["chunks"]} chunks · {item["caracteres"]:,} caracteres'
                    f"</span>"
                    f"{resumo_html}"
                    f"</div>",
                    unsafe_allow_html=True,
                )
            with c2:
                if documento_id and st.button("🗑️ Excluir", key=f"del_rel_{documento_id}", help="Remover esta fonte"):
                    colecao = _get_docs_collection()
                    try:
                        colecao.delete(where={"documento_id": documento_id})
                    except Exception:
                        pass
                    for chv, meta in list(st.session_state.documentos_meta.items()):
                        if meta.get("documento_id") == documento_id:
                            st.session_state.documentos.remove(chv)
                            st.session_state.documentos_meta.pop(chv, None)
                            break
                    st.rerun()

        with st.container(border=False):
            st.markdown('<div class="app-card" style="margin-top: 2rem;">', unsafe_allow_html=True)
            st.markdown(
                '<h4 style="margin-top:0; margin-bottom:1rem;font-weight:700; color: var(--on-surface);">📥 Exportar relatório da base</h4>',
                unsafe_allow_html=True,
            )
            csv_data = exportar_relatorio_csv(relatorio)
            st.download_button(
                "📥 Exportar CSV",
                data=csv_data,
                file_name="relatorio_conteudo.csv",
                mime="text/csv",
                use_container_width=True,
                key="btn_exportar_relatorio",
            )
            st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with tab_legendas:
    st.markdown(
        '<div class="app-card">'
        '<h2>📸 Legendas para Instagram</h2>'
        '<p style="color: var(--on-surface-variant); margin: 0;">'
        'Faça upload de uma imagem e gere legendas prontas para o Instagram '
        'com o tom e estilo ideais para a franquia.</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        col_img, col_config = st.columns([2, 1])

        with col_img:
            uploaded_image = st.file_uploader(
                "Escolha uma imagem",
                type=["jpg", "jpeg", "png", "webp"],
                key="legendas_img",
            )
            if uploaded_image:
                from PIL import Image
                img = Image.open(uploaded_image)
                st.image(img, caption="Imagem selecionada", use_container_width=True)

        with col_config:
            tom = st.selectbox(
                "Tom da legenda",
                options=list(TOM_ESTILO.keys()),
                index=0,
                key="legendas_tom",
            )
            tema = st.text_input(
                "Tema (opcional)",
                placeholder="Ex: Dia das Mães, matrículas, dica de estudo...",
                key="legendas_tema",
            )
            instrucoes = st.text_area(
                "Contexto / Instruções (opcional)",
                placeholder="Ex: Destacar o desconto de 15% nas matrículas de robótica...",
                key="legendas_instrucoes",
            )

            if st.button(
                "✨ Gerar Legendas",
                type="primary",
                use_container_width=True,
                disabled="legendas_img" not in st.session_state or not uploaded_image,
            ):
                if not uploaded_image:
                    st.warning("Faça upload de uma imagem primeiro.")
                else:
                    from PIL import Image as PILImage
                    img_pil = PILImage.open(uploaded_image)
                    
                    import io
                    import base64
                    buffered = io.BytesIO()
                    if img_pil.mode in ("RGBA", "P"):
                        img_pil_rgb = img_pil.convert("RGB")
                    else:
                        img_pil_rgb = img_pil
                    img_pil_rgb.save(buffered, format="JPEG")
                    img_b64 = "data:image/jpeg;base64," + base64.b64encode(buffered.getvalue()).decode()
                    
                    with st.spinner("Analisando imagem e gerando legendas..."):
                        resultado = gerar_legenda(
                            image=img_pil,
                            tom=tom,
                            tema=tema,
                            instrucoes=instrucoes,
                        )
                    if resultado["status"] == "ok":
                        st.session_state.legendas_geradas.append(resultado["conteudo"])
                        st.session_state.legendas_imagens_b64.append(img_b64)
                        st.balloons()
                    else:
                        st.error(resultado.get("mensagem", "Erro ao gerar legendas."))

    if st.session_state.legendas_geradas:
        st.divider()
        st.markdown(
            '<div class="app-card">'
            '<h3>📝 Legendas geradas</h3></div>',
            unsafe_allow_html=True,
        )
        import streamlit.components.v1 as components
        for i, legenda in enumerate(reversed(st.session_state.legendas_geradas), 1):
            orig_idx = len(st.session_state.legendas_geradas) - i
            if len(st.session_state.legendas_imagens_b64) > orig_idx:
                img_b64 = st.session_state.legendas_imagens_b64[orig_idx]
            else:
                img_b64 = None
                
            with st.container(border=True):
                st.markdown(
                    f'<strong>Geração #{orig_idx + 1}</strong>',
                    unsafe_allow_html=True,
                )
                options = parse_instagram_options(legenda)
                tabs = st.tabs([f"Opção {idx+1}" for idx in range(len(options))])
                for idx, option in enumerate(options):
                    with tabs[idx]:
                        mockup_html = render_instagram_mockup(
                            index=f"{orig_idx}-{idx}",
                            title=f"Opção {idx+1}",
                            content_markdown=option,
                            img_base64_str=img_b64,
                        )
                        components.html(mockup_html, height=720, scrolling=True)
                        with st.expander("📋 Copiar Legenda — clique para ver e copiar o texto", expanded=False):
                            st.code(option, language="markdown")
                st.divider()

st.markdown("""
<div class="app-footer">
    PlanejadorPV © 2025 — Ensina Mais Turma da Mônica · Unidade Tatuapé
</div>
""", unsafe_allow_html=True)
