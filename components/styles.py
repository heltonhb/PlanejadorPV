"""Carregamento de estilos CSS e scripts do tema."""

import streamlit as st
from pathlib import Path

HTML_TEMPLATE = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<script>
(function() {
    // Dark mode é o padrão
    const DARK = 'dark', LIGHT = 'light';
    function getTheme() { return localStorage.getItem('pv-theme') || DARK; }
    function setTheme(t) {
        localStorage.setItem('pv-theme', t);
        document.documentElement.setAttribute('data-theme', t);
        // Atualiza meta theme-color
        var meta = document.querySelector('meta[name="theme-color"]');
        if (meta) meta.content = t === DARK ? '#0D1117' : '#006D38';
    }
    // Aplica tema salvo antes do render (evita flash)
    var saved = getTheme();
    document.documentElement.setAttribute('data-theme', saved);
    var meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.content = saved === DARK ? '#0D1117' : '#006D38';
    // Atualiza o botão com o ícone e texto do tema atual
    function updateThemeButton() {
        var btn = document.getElementById('themeToggleBtn');
        if (!btn) return;
        var current = getTheme();
        if (current === DARK) {
            btn.innerHTML = '🌙 <span style="font-size:0.8rem;opacity:0.8;">Escuro</span>';
        } else {
            btn.innerHTML = '☀️ <span style="font-size:0.8rem;opacity:0.8;">Claro</span>';
        }
    }
    // Escuta clique no botão de tema via addEventListener (evita conflito com React)
    document.addEventListener('click', function(e) {
        if (e.target.id === 'themeToggleBtn' || e.target.closest('#themeToggleBtn')) {
            var current = getTheme();
            setTheme(current === DARK ? LIGHT : DARK);
            updateThemeButton();
            // Recarrega para aplicar nos componentes Streamlit
            location.reload();
        }
    });
    // Atualiza o botão assim que carregar
    document.addEventListener('DOMContentLoaded', updateThemeButton);
    updateThemeButton();
})();
</script>
<style>
{css_content}
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
"""


def inject_css_and_theme():
    """Injeta CSS externo, scripts de tema e meta tags PWA."""
    css_path = Path(__file__).parent.parent / "assets" / "style.css"
    css_content = css_path.read_text(encoding="utf-8")
    
    st.markdown(HTML_TEMPLATE.replace("{css_content}", css_content), unsafe_allow_html=True)
