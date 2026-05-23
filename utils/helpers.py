def formatar_numero(numero: int | float) -> str:
    """Formata números com separadores de milhar."""
    return f"{numero:,}".replace(",", ".")


def truncar_texto(texto: str, max_length: int = 100, sufixo: str = "...") -> str:
    """Trunca texto longo adicionando sufixo."""
    if len(texto) <= max_length:
        return texto
    return texto[:max_length - len(sufixo)] + sufixo
