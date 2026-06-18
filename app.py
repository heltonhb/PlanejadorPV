"""Wrapper de diagnóstico para capturar exceções de startup."""
import sys as _sys
import os as _os
import traceback as _tb

_SRC = _os.path.join(_os.path.dirname(__file__), "_app_main.py")

try:
    exec(compile(open(_SRC, encoding="utf-8").read(), _SRC, "exec"))
except Exception:
    import streamlit as _st
    try:
        _st.set_page_config(
            page_title="Erro de Inicialização",
            page_icon="🚨",
            layout="wide",
        )
    except Exception:
        pass  # set_page_config já foi chamada antes do crash
    _st.error("## 🚨 Erro de inicialização do PlanejadorPV")
    _st.code(_tb.format_exc(), language="python", line_numbers=False)
    _st.stop()
