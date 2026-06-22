import pytest
from utils.helpers import (
    formatar_numero,
    truncar_texto,
    parse_duration_days,
    sanitizar_html,
    tratar_erro_ia,
)


# ── formatar_numero ──


class TestFormatarNumero:
    def test_inteiro(self):
        assert formatar_numero(1234) == "1.234"

    def test_float(self):
        # Python f-string coloca "," nos separadores: 1234.5 → "1,234.5" → "1.234.5"
        assert formatar_numero(1234.5) == "1.234.5"

    def test_milhao(self):
        assert formatar_numero(1_000_000) == "1.000.000"

    def test_zero(self):
        assert formatar_numero(0) == "0"

    def test_pequeno(self):
        assert formatar_numero(7) == "7"

    def test_negativo(self):
        assert formatar_numero(-1500) == "-1.500"


# ── truncar_texto ──


class TestTruncarTexto:
    def test_texto_curto_inalterado(self):
        assert truncar_texto("Hello") == "Hello"

    def test_texto_exato_no_limite(self):
        assert truncar_texto("a" * 100) == "a" * 100

    def test_texto_ultrapassa_limite(self):
        resultado = truncar_texto("a" * 200)
        assert len(resultado) == 100
        assert resultado.endswith("...")

    def test_max_length_personalizado(self):
        resultado = truncar_texto("abcdefghij", max_length=5)
        assert resultado == "ab..."

    def test_sufixo_personalizado(self):
        resultado = truncar_texto("abcdefghij", max_length=6, sufixo="[+]")
        assert resultado == "abc[+]"

    def test_string_vazia(self):
        assert truncar_texto("") == ""

    def test_texto_exatamente_mais_sufixo(self):
        """Quando o texto cabe exatamente com o sufixo, trunca."""
        resultado = truncar_texto("abcdefghij", max_length=5, sufixo="..")
        assert resultado == "abc.."

    def test_max_length_menor_que_sufixo(self):
        """Quando max_length é menor que o sufixo, o resultado pode
        ultrapassar max_length (comportamento atual da funcao)."""
        resultado = truncar_texto("abc", max_length=2, sufixo="....")
        # Resultado: "a...." — o texto e o sufixo sao concatenados
        assert len(resultado) > 2


# ── parse_duration_days ──


class TestParseDurationDays:
    def test_direct_days(self):
        assert parse_duration_days("15 dias") == 15
        assert parse_duration_days("5 dias") == 5
        assert parse_duration_days("10d") == 10
        assert parse_duration_days("  8 dias   ") == 8

    def test_weeks(self):
        assert parse_duration_days("2 semanas") == 14
        assert parse_duration_days("3 semanas") == 21
        assert parse_duration_days("1 sem") == 7

    def test_months(self):
        assert parse_duration_days("1 mês") == 30
        assert parse_duration_days("2 meses") == 60
        assert parse_duration_days("1 mes") == 30

    def test_date_range(self):
        assert parse_duration_days("de 01/06 a 15/06") == 15
        assert parse_duration_days("01/06/2026 a 30/06/2026") == 30
        assert parse_duration_days("de 28/05/2026 até 02/06/2026") == 6

    def test_fallback(self):
        assert parse_duration_days("") == 30
        assert parse_duration_days(None) == 30
        assert parse_duration_days("período indeterminado") == 30


# ── sanitizar_html ──


class TestSanitizarHtml:
    def test_remove_tags_simples(self):
        assert sanitizar_html("<p>Olá</p>") == "Olá"

    def test_remove_tags_aninhadas(self):
        assert sanitizar_html("<div><b>Texto</b> legal</div>") == "Texto legal"

    def test_remove_tags_com_atributos(self):
        assert (
            sanitizar_html('<a href="http://exemplo.com">Link</a>') == "Link"
        )

    def test_sem_html_retorna_igual(self):
        assert sanitizar_html("Texto simples sem tags") == "Texto simples sem tags"

    def test_normaliza_quebras_excessivas(self):
        assert sanitizar_html("Linha1\n\n\n\nLinha2") == "Linha1\n\nLinha2"
        assert sanitizar_html("A\n\n\n\n\n\nB") == "A\n\nB"

    def test_strip_espacos_brancos(self):
        assert sanitizar_html("  texto com espaços  ") == "texto com espaços"

    def test_string_vazia(self):
        assert sanitizar_html("") == ""

    def test_apenas_tags(self):
        assert sanitizar_html("<br/><br/>") == ""

    def test_tags_com_quebras_de_linha(self):
        assert sanitizar_html("<ul>\n<li>Item</li>\n</ul>") == "Item"

    def test_self_closing(self):
        assert sanitizar_html("Olá<br/>Mundo") == "OláMundo"

    def test_html_entities_permanecem(self):
        result = sanitizar_html("<p>Café &amp; Leite</p>")
        assert "Café" in result
        assert "Leite" in result


# ── tratar_erro_ia ──


class TestTratarErroIa:
    def test_erro_api_key(self):
        msg = tratar_erro_ia(Exception("API_KEY inválida"))
        assert "Chave de API" in msg
        assert "Hermes Operator" in msg
        assert "🔑" in msg

    def test_erro_api_key_no_str(self):
        msg = tratar_erro_ia(Exception("api key not found"))
        assert "Chave de API" in msg

    def test_rate_limit_generico(self):
        msg = tratar_erro_ia(Exception("429 Too Many Requests"))
        assert "limite de requisições" in msg
        assert "⚠️" in msg
        assert "diário" not in msg  # sem "daily" → genérico

    def test_rate_limit_diario(self):
        msg = tratar_erro_ia(Exception("daily rate limit exceeded"))
        assert "limite **diário**" in msg
        assert "diário" in msg

    def test_servico_indisponivel_500(self):
        msg = tratar_erro_ia(Exception("500 Internal Server Error"))
        assert "indisponível" in msg
        assert "🔧" in msg

    def test_servico_indisponivel_timeout(self):
        msg = tratar_erro_ia(Exception("timeout"))
        assert "indisponível" in msg

    def test_servico_indisponivel_503(self):
        msg = tratar_erro_ia(Exception("503 Service Unavailable"))
        assert "indisponível" in msg

    def test_bloqueio_seguranca_safety(self):
        msg = tratar_erro_ia(Exception("safety settings"))
        assert "bloqueado" in msg
        assert "🛡️" in msg

    def test_bloqueio_seguranca_blocked(self):
        msg = tratar_erro_ia(Exception("blocked due to content"))
        assert "bloqueado" in msg

    def test_erro_generico(self):
        msg = tratar_erro_ia(Exception("Algo deu errado"))
        assert "Erro inesperado" in msg
        assert "❌" in msg

    def test_com_provedor_personalizado(self):
        msg = tratar_erro_ia(Exception("API_KEY inválida"), provedor="Gemini")
        assert "Gemini" in msg
        assert "Hermes Operator" not in msg

    def test_mensagem_curta_200_chars(self):
        msg = tratar_erro_ia(Exception("x" * 500))
        assert len(msg) < 300  # Não deve incluir a mensagem gigante inteira
