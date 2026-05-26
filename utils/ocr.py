"""
Gerenciamento do modelo OCR Tesseract para português.
"""
import logging
from pathlib import Path
from typing import Optional

from utils.config import TESSDATA_PATH, TESSDATA_URL

logger = logging.getLogger(__name__)

_CAMINHOS_SISTEMA_OCR = [
    Path("/usr/share/tesseract-ocr/5/tessdata"),
    Path("/usr/share/tesseract-ocr/4/tessdata"),
    Path("/usr/share/tesseract-ocr/3/tessdata"),
    Path("/usr/local/share/tessdata"),
    Path("/usr/share/tessdata"),
]


def encontrar_modelo_ocr() -> Optional[Path]:
    """Procura o modelo OCR por.traineddata, baixa se necessário."""
    local = TESSDATA_PATH / "por.traineddata"
    if local.exists():
        return local

    for p in _CAMINHOS_SISTEMA_OCR:
        modelo = p / "por.traineddata"
        if modelo.exists():
            logger.info("Modelo OCR encontrado em: %s", modelo)
            return modelo

    TESSDATA_PATH.mkdir(parents=True, exist_ok=True)
    try:
        import requests as req
        logger.info("Baixando modelo OCR português...")
        r = req.get(TESSDATA_URL, timeout=30)
        r.raise_for_status()
        local.write_bytes(r.content)
        logger.info("Modelo OCR baixado: %s", local)
        return local
    except Exception as e:
        logger.warning("não foi possível baixar modelo OCR: %s", e)
        return None


def diagnosticar_ocr() -> str:
    """Retorna diagnóstico do estado do OCR."""
    diag = []
    try:
        import tesserocr
        diag.append(f"tesserocr OK (v{getattr(tesserocr, '__version__', '?')})")
        modelo = encontrar_modelo_ocr()
        if modelo:
            diag.append("modelo OK")
            try:
                from tesserocr import PyTessBaseAPI
                api = PyTessBaseAPI(lang="por", path=str(modelo.parent))
                api.End()
                diag.append("PyTessBaseAPI OK")
            except Exception as e2:
                diag.append(f"PyTessBaseAPI ERRO: {e2}")
        else:
            diag.append("modelo AUSENTE")
    except Exception as e:
        diag.append(f"tesserocr AUSENTE: {e}")

    try:
        import pytesseract
        v = pytesseract.__version__ if hasattr(pytesseract, '__version__') else '?'
        diag.append(f"pytesseract OK (v{v})")
        try:
            pytesseract.get_tesseract_version()
            diag.append("tesseract bin OK")
        except Exception as e2:
            diag.append(f"tesseract bin ERRO: {e2}")
    except Exception as e:
        diag.append(f"pytesseract AUSENTE: {e}")

    return "; ".join(diag)
