from utils.perguntas_sugeridas import PERGUNTAS_SUGERIDAS


class TestPerguntasSugeridas:
    def test_lista_nao_vazia(self):
        assert len(PERGUNTAS_SUGERIDAS) > 0

    def test_todos_itens_sao_strings(self):
        for grupo in PERGUNTAS_SUGERIDAS:
            assert isinstance(grupo, dict)
            assert "categoria" in grupo
            assert "perguntas" in grupo
            for pergunta in grupo["perguntas"]:
                assert isinstance(pergunta, str)

    def test_cada_pergunta_termina_com_interrogacao_ou_ponto(self):
        for grupo in PERGUNTAS_SUGERIDAS:
            for pergunta in grupo["perguntas"]:
                assert pergunta.endswith("?") or pergunta.endswith("."), f"Pergunta/instrução não termina com '?' ou '.': {pergunta!r}"
