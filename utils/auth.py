"""
Autenticação básica para o PlanejadorPV.

Carrega APP_PASSWORD de variável de ambiente (.env) ou st.secrets e
renderiza uma tela de login se a senha estiver configurada.

Uso:
    from utils.auth import require_auth
    require_auth()
"""
import os
import streamlit as st


def _carregar_senha() -> str:
    """Carrega APP_PASSWORD de env ou st.secrets (nessa ordem)."""
    env_pwd = os.getenv("APP_PASSWORD") or ""
    sec_pwd = ""
    try:
        sec_pwd = st.secrets.get("app_password", "")
    except Exception:
        pass
    return env_pwd or sec_pwd


def require_auth() -> None:
    """Verifica autenticação e renderiza tela de login se necessário.

    Deve ser chamada antes de qualquer outro código da aplicação.
    Se a senha não estiver configurada, passa sem autenticação.
    Se configurada e o usuário não estiver autenticado, renderiza
    o formulário de login e interrompe com st.stop().
    """
    if st.session_state.get("_auth_checked"):
        return

    app_password = _carregar_senha()
    st.session_state._app_password = app_password
    st.session_state._auth_checked = True

    if not app_password:
        return

    if not st.session_state.get("authenticated", False):
        _renderizar_tela_login()


def _renderizar_tela_login() -> None:
    """Renderiza o formulário de login com senha."""
    st.markdown(
        """
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
            pwd = st.text_input(
                "Senha",
                type="password",
                label_visibility="collapsed",
                placeholder="Digite a senha...",
            )
            if st.button("Entrar", type="primary", use_container_width=True):
                if pwd == st.session_state._app_password:
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("❌ Senha incorreta.")
    st.stop()
