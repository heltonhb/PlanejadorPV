import streamlit as st
from utils.documentos import _get_collection as _get_docs_collection, deletar_do_chromadb
from utils.relatorios import resumo_conteudo
from utils.exportacao import exportar_relatorio_csv
from utils.firebase_store import remover_fonte_meta
import logging


def render():
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

    try:
        relatorio = resumo_conteudo()
    except Exception as e:
        logging.getLogger(__name__).exception("Erro ao carregar relatório")
        st.error(f"❌ Erro ao carregar relatório da base de dados: {e}")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    if relatorio["total_chunks"] == 0:
        st.markdown(
            '<div class="app-card-empty animate-in" style="padding: 3.5rem 1.5rem; text-align: center; border-radius: var(--radius-lg); border: 2px dashed var(--outline-variant); background: var(--card-bg); margin: 1.5rem 0;">'
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
                f'📄 Total de trechos</div></div>',
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
        cores_f = {"pdf": "var(--secondary)", "url": "var(--primary)", "html": "var(--tertiary)", "instagram": "#E1306C", "texto": "var(--on-surface-variant)", "planilha": "var(--info)"}
        for idx, (fonte, dados) in enumerate(por_fonte_items):
            with cols_fonte[idx]:
                icone = icones_f.get(fonte, "📄")
                nome = nomes_f.get(fonte, fonte.capitalize())
                cor = cores_f.get(fonte, "var(--primary)")
                st.markdown(
                    f'<div class="app-card animate-in" style="animation-delay: {0.25 + idx*0.05}s; text-align:center;padding:1rem; border-top: 3px solid {cor};">'
                    f'<div style="font-size:1.4rem;font-weight:800;color:var(--primary);">'
                    f'{dados["chunks"]}</div>'
                    f'<div style="font-size:0.8rem;color:var(--on-surface-variant);font-weight:500;">'
                    f'{icone} {nome}</div>'
                    f'<div style="font-size:0.75rem;color:var(--on-surface-variant);">'
                    f'{dados["caracteres"]:,} caracteres</div></div>',
                    unsafe_allow_html=True,
                )

        st.markdown(
            '<h4 style="margin-top: 2rem; margin-bottom:1rem;font-weight:700; color: var(--on-surface);">'
            '📋 Fontes carregadas <span style="font-size:0.85rem;font-weight:400;color:var(--on-surface-variant);">'
            '— clique no título para expandir os detalhes</span></h4>',
            unsafe_allow_html=True,
        )

        # Agrupa as fontes detalhadas por tipo para exibição organizada
        fontes_por_tipo = {}
        for item in relatorio["fontes_detalhadas"]:
            tipo = item["fonte"]
            if tipo not in fontes_por_tipo:
                fontes_por_tipo[tipo] = []
            fontes_por_tipo[tipo].append(item)

        idx_global = 0
        for tipo, items in sorted(fontes_por_tipo.items()):
            icone_tipo = icones_f.get(tipo, "📄")
            nome_tipo = nomes_f.get(tipo, tipo.capitalize())
            cor_tipo = cores_f.get(tipo, "var(--primary)")
            total_items = len(items)
            total_chunks_tipo = sum(it["chunks"] for it in items)

            doc_suffix = "" if total_items == 1 else "s"
            chunks_suffix = "" if total_chunks_tipo == 1 else "s"

            # Cabeçalho do grupo
            st.markdown(
                f'<div style="display:flex;align-items:center;gap:0.75rem;margin-top:1.75rem;margin-bottom:0.75rem;'
                f'padding:0.5rem 0.75rem;border-radius:var(--radius-md);background:var(--primary-container);">'
                f'<span style="font-size:1.3rem;">{icone_tipo}</span>'
                f'<span style="font-weight:700;font-size:1.05rem;color:var(--on-surface);">{nome_tipo}</span>'
                f'<span style="background:{cor_tipo};color:white;padding:0.15rem 0.6rem;border-radius:100px;'
                f'font-size:0.75rem;font-weight:600;">{total_items} doc{doc_suffix}</span>'
                f'<span style="font-size:0.82rem;color:var(--on-surface-variant);margin-left:auto;">'
                f'{total_chunks_tipo} trecho{chunks_suffix}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

            for item in items:
                documento_id = item.get("documento_id")
                resumo = item.get("resumo", "")
                preview = item.get("preview", "")

                with st.expander(
                    f'{item["icone"]} {item["titulo"]}',
                    expanded=False,
                ):
                    cols_info = st.columns([1, 1, 1])
                    with cols_info[0]:
                        st.markdown(f'<span style="font-size:0.85rem;color:var(--on-surface-variant);">📦 Trechos</span><br><span style="font-size:1.3rem;font-weight:700;">{item["chunks"]}</span>', unsafe_allow_html=True)
                    with cols_info[1]:
                        st.markdown(f'<span style="font-size:0.85rem;color:var(--on-surface-variant);">📏 Caracteres</span><br><span style="font-size:1.3rem;font-weight:700;">{item["caracteres"]:,}</span>', unsafe_allow_html=True)
                    with cols_info[2]:
                        if documento_id and st.button("🗑️ Remover", key=f"del_rel_{documento_id}", help="Remover esta fonte da base", use_container_width=True):
                            deletar_do_chromadb(documento_id, documento_id)
                            for chv, meta in list(st.session_state.documentos_meta.items()):
                                if meta.get("documento_id") == documento_id:
                                    st.session_state.documentos.remove(chv)
                                    st.session_state.documentos_meta.pop(chv, None)
                                    remover_fonte_meta(chv)
                                    break
                            st.rerun()

                    # Resumo amigável
                    if resumo:
                        st.markdown(
                            f'<div style="background:var(--primary-container);border-radius:var(--radius-sm);'
                            f'padding:0.75rem 1rem;margin-top:0.75rem;border-left:3px solid var(--primary);">'
                            f'<span style="font-size:0.8rem;font-weight:600;color:var(--primary);">📝 Resumo</span><br>'
                            f'<span style="font-size:0.9rem;color:var(--on-surface);">{resumo}</span>'
                            f'</div>',
                            unsafe_allow_html=True,
                        )

                    # Preview do conteúdo
                    if preview:
                        with st.container(border=False):
                            st.markdown(
                                f'<details style="margin-top:0.5rem;">'
                                f'<summary style="cursor:pointer;font-size:0.82rem;font-weight:600;color:var(--on-surface-variant);">'
                                f'🔍 Ver preview do conteúdo</summary>'
                                f'<div style="margin-top:0.5rem;padding:0.75rem;background:var(--input-bg);border-radius:var(--radius-sm);'
                                f'font-size:0.82rem;color:var(--on-surface-variant);line-height:1.6;border:1px solid var(--outline-variant);">'
                                f'{preview}…'
                                f'</div></details>',
                                unsafe_allow_html=True,
                            )

                idx_global += 1

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
