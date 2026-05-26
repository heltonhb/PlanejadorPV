import streamlit as st
import streamlit.components.v1 as components
from utils.legendas_instagram import gerar_legenda
from utils.constants import TOM_ESTILO
from components.instagram import parse_instagram_options, render_instagram_mockup
import logging


def render():
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
                        try:
                            resultado = gerar_legenda(
                                image=img_pil,
                                tom=tom,
                                tema=tema,
                                instrucoes=instrucoes,
                            )
                        except Exception as e:
                            logging.getLogger(__name__).exception("Erro ao gerar legendas")
                            st.error(f"❌ Erro inesperado ao gerar legendas: {e}")
                            st.rerun()
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
