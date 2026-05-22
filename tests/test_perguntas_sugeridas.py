from utils.perguntas_sugeridas import PERGUNTAS_SUGERIDAS


class TestPerguntasSugeridas:
    def test_lista_nao_vazia(self):
        assert len(PERGUNTAS_SUGERIDAS) > 0

    def test_todos_itens_sao_strings(self):
        for pergunta in PERGUNTAS_SUGERIDAS:
            assert isinstance(pergunta, str)

    def test_cada_pergunta_termina_com_interrogacao(self):
        for pergunta in PERGUNTAS_SUGERIDAS:
            assert pergunta.endswith("?"), f"Pergunta não termina com '?': {pergunta!r}"
