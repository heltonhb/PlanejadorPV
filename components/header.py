"""Componente do cabeçalho do app."""

import base64
import streamlit as st


def _load_svg_as_base64(path):
    try:
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
            return f"data:image/svg+xml;base64,{b64}"
    except Exception:
        return ""


def render_header():
    logo_img = f'<img src="{_load_svg_as_base64("assets/logo.svg")}" alt="PlanejadorPV" />'
    st.markdown(f"""
<div class="app-header animate-in">
    <div class="app-header-content">
        <div class="app-header-left">
            <div class="app-header-logo">{logo_img}</div>
            <div class="app-header-title-group">
                <div class="app-title">Marketing Planner</div>
                <div class="app-subtitle">Ensina Mais Turma da Mônica · Unidade Tatuapé</div>
            </div>
        </div>
        <div class="app-header-right">
            <button id="themeToggleBtn" class="app-header-theme-btn">🌓</button>
            <div class="app-header-greeting">
                <span class="status-pulse"></span>
                Olá, Gestor! 👋
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
