"""
Worker de extração para execução em subprocesso.
Streamlit Cloud executa o script em thread não-principal,
onde signal.signal() não funciona. Este worker roda em
um processo dedicado.
"""
import json
import sys
import tempfile
import traceback

# --- Copiar as funções de extração aqui (evita import circular) ---

import pdfplumber
import fitz
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _extrair_pdfplumber(tmp_path: str) -> tuple[str, int]:
    try:
        with pdfplumber.open(tmp_path) as pdf:
            paginas = len(pdf.pages)
            partes = []
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    partes.append(t)
            return "\n".join(partes), paginas
    except Exception:
        logger.warning("pdfplumber falhou no worker")
        return "", 0


def _extrair_pymupdf(tmp_path: str) -> tuple[str, int]:
    try:
        doc = fitz.open(tmp_path)
        paginas = len(doc)
        texto = "\n".join(page.get_text() or "" for page in doc)
        doc.close()
        return texto, paginas
    except Exception:
        logger.warning("pymupdf falhou no worker")
        return "", 0


def _extrair_worker(pdf_bytes: bytes) -> dict:
    """Executa extração em processo dedicado."""
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(pdf_bytes)
        tmp_path = tmp.name

    try:
        texto, paginas = _extrair_pdfplumber(tmp_path)
        metodo = "pdfplumber"
        if not texto or not texto.strip():
            logger.info("worker: pdfplumber vazio, tentando pymupdf")
            texto, paginas = _extrair_pymupdf(tmp_path)
            metodo = "pymupdf"

        return {
            "texto": texto or "",
            "metodo": metodo,
            "paginas": paginas,
        }
    except Exception as e:
        return {
            "texto": "",
            "metodo": f"erro: {e}",
            "paginas": 0,
        }
    finally:
        import os
        try:
            os.unlink(tmp_path)
        except Exception:
            pass


if __name__ == "__main__":
    # Recebe bytes do PDF via stdin (base64)
    # Formato: {"pdf_b64": "..."}
    raw = sys.stdin.buffer.read()
    import base64
    try:
        data = json.loads(raw)
        pdf_b64 = data["pdf_b64"]
        pdf_bytes = base64.b64decode(pdf_b64)
        resultado = _extrair_worker(pdf_bytes)
        sys.stdout.write(json.dumps(resultado))
        sys.stdout.flush()
    except Exception as e:
        sys.stdout.write(json.dumps({
            "texto": "",
            "metodo": f"erro: {e}",
            "paginas": 0,
        }))
        sys.stdout.flush()
