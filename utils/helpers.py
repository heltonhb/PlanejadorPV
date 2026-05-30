import re
import logging

logger = logging.getLogger(__name__)


def formatar_numero(numero: int | float) -> str:
    """Formata números com separadores de milhar."""
    return f"{numero:,}".replace(",", ".")


def truncar_texto(texto: str, max_length: int = 100, sufixo: str = "...") -> str:
    """Trunca texto longo adicionando sufixo."""
    if len(texto) <= max_length:
        return texto
    return texto[:max_length - len(sufixo)] + sufixo


def parse_duration_days(datas_str: str) -> int:
    """
    Analisa a string de período/datas e estima a duração da campanha em dias.
    Exemplos:
      - "15 dias" -> 15
      - "3 semanas" -> 21
      - "de 01/06 a 15/06" -> 15
    """
    if not datas_str:
        return 30  # Padrão: 30 dias se não informado
    
    import re
    import datetime
    
    datas_clean = datas_str.lower().strip()
    
    # 1. Busca por menções diretas a dias, semanas ou meses
    match_days = re.search(r'(\d+)\s*(dia|dias|d\b)', datas_clean)
    if match_days:
        return int(match_days.group(1))
        
    match_weeks = re.search(r'(\d+)\s*(semana|semanas|sem\b)', datas_clean)
    if match_weeks:
        return int(match_weeks.group(1)) * 7
        
    match_months = re.search(r'(\d+)\s*(mês|mes|meses|m\b)', datas_clean)
    if match_months:
        return int(match_months.group(1)) * 30
        
    # 2. Busca por intervalos de datas no formato DD/MM ou DD/MM/AAAA
    # Padrão flexível para capturar dia, mês e opcionalmente o ano
    date_pattern = r'(\d{1,2})[/\-](\d{1,2})(?:[/\-](\d{2,4}))?'
    matches = re.findall(date_pattern, datas_clean)
    
    if len(matches) >= 2:
        try:
            dates = []
            for match in matches[:2]:
                day = int(match[0])
                month = int(match[1])
                # Determina o ano (padrão 2026 com base no tempo do sistema)
                if match[2]:
                    year_str = match[2]
                    if len(year_str) == 2:
                        year = 2000 + int(year_str)
                    else:
                        year = int(year_str)
                else:
                    year = 2026
                dates.append(datetime.date(year, month, day))
            
            delta = dates[1] - dates[0]
            days = abs(delta.days) + 1  # Inclui o dia de início
            if 0 < days <= 365:
                return days
        except Exception:
            pass
            
    return 30


def sanitizar_html(texto: str) -> str:
    """
    Remove tags HTML que o Gemini insiste em gerar e normaliza
    quebras de linha excessivas.
    """
    texto = re.sub(r"<[^>]*>", "", texto)
    texto = re.sub(r"\n{3,}", "\n\n", texto)
    return texto.strip()


def tratar_erro_ia(erro: Exception, provedor: str = "Hermes Operator") -> str:
    """
    Retorna mensagem de erro amigável padronizada para qualquer provedor de IA.

    Args:
        erro: Exceção capturada.
        provedor: Nome do provedor para exibição na mensagem.

    Returns:
        Mensagem de erro amigável em português.
    """
    msg = str(erro).lower()

    if "API_KEY" in str(erro).upper() or "api key" in msg:
        return (
            f"🔑 Chave de API do **{provedor}** não configurada ou inválida. "
            f"Configure a variável no arquivo .env ou nas secrets do Streamlit."
        )
    if "quota" in msg or "429" in msg or "rate limit" in msg or "too many" in msg:
        if "daily" in msg or "per day" in msg or "diário" in msg:
            return (
                f"⚠️ **{provedor}**: limite **diário** de requisições excedido. "
                f"Tente novamente amanhã ou configure uma chave com cota maior."
            )
        return (
            f"⚠️ **{provedor}**: limite de requisições excedido. "
            f"Aguarde alguns instantes e tente novamente."
        )
    if any(w in msg for w in ["500", "503", "unavailable", "timeout", "temporariamente"]):
        return (
            f"🔧 **{provedor}** temporariamente indisponível. "
            f"Tente novamente em alguns minutos."
        )
    if "safety" in msg or "blocked" in msg or "harm" in msg:
        return (
            f"🛡️ O conteúdo foi bloqueado pelas regras de segurança do **{provedor}**. "
            f"Revise o prompt e tente novamente."
        )
    return f"❌ Erro inesperado no **{provedor}**: {str(erro)[:200]}"

