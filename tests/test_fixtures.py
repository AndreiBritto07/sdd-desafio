"""Aceite T-002: fixtures carregáveis, independentes da data corrente."""
import unittest
from decimal import Decimal
from pathlib import Path

from tests.fixtures import entrada, despesa, colaborador, periodo, politica, cambio, RAIZ


class TestFixtures(unittest.TestCase):
    def test_fixtures_validas_carregam(self):
        self.assertEqual(entrada()["colaborador"]["centro_custo"], "CC-ADM")
        self.assertEqual(entrada()["periodo"]["competencia"], "2026-07")
        self.assertEqual(entrada()["despesas"][0]["valor"], Decimal("40.00"))
        self.assertEqual(politica()["moeda_base"], "BRL")
        self.assertEqual(cambio()["moeda_base"], "BRL")

    def test_fixture_alteracoes_nao_vazam(self):
        primeira = entrada()
        primeira["despesas"][0]["descricao"] = "Alterada"
        self.assertEqual(entrada()["despesas"][0]["descricao"], "Refeicao")
        self.assertEqual(despesa(valor=Decimal("1.20"))["valor"], Decimal("1.20"))
        self.assertEqual(colaborador(centro_custo="CC-COMERCIAL")["centro_custo"], "CC-COMERCIAL")
        self.assertEqual(periodo(fim="2026-07-14")["fim"], "2026-07-14")

    def test_arquivos_externos_reais_disponiveis(self):
        self.assertTrue((RAIZ / "exemplos/envelope/politica-v4.json").is_file())
        self.assertTrue((RAIZ / "exemplos/envelope/cambio.json").is_file())


if __name__ == "__main__":
    unittest.main()
