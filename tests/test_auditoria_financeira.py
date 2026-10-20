"""Testes adicionais de regressão: AC-004/029, 023, 028, 031, 034 e 036.

Execute na raiz do repositório: python -m unittest discover -s tests -v
Não modifica o motor. Falhas indicam divergência a investigar.
"""
import copy
import json
import unittest
from decimal import Decimal

from src.motor import executar, parse
from src.validacao_global import ErroGlobal


def numero(valor):
    return Decimal(str(valor))


def politica(representacao=None, alimentacao=None, mensal=None):
    padrao = {"alimentacao": {"limite": 500, "periodicidade": "dia"}}
    centros = {}
    if representacao is not None:
        centros["CC-COMERCIAL"] = {
            "representacao": {"limite": representacao, "periodicidade": "dia"}
        }
    if alimentacao is not None:
        padrao["alimentacao"]["limite"] = alimentacao
    if mensal is not None:
        padrao["transporte"] = {"limite": mensal, "periodicidade": "mes"}
    return {"versao": "v4", "vigencia": "2026-07-01", "moeda_base": "BRL",
            "padrao": padrao, "centros_custo": centros,
            "nota_fiscal_obrigatoria_acima_de": 100,
            "acrescimo_em_viagem_percentual": 50}


def cambio():
    return {"moeda_base": "BRL", "fonte": "fixture", "observacao": "teste",
            "taxas": {"2026-07-13": {"USD": 5, "EUR": 6}}}


def despesa(ident, valor, categoria="alimentacao", moeda="BRL", nf=True, dia="2026-07-13"):
    return {"id": ident, "data": dia, "categoria": categoria,
            "descricao": f"Compra {ident}", "fornecedor": "Fornecedor",
            "valor": valor, "moeda": moeda, "tem_nota_fiscal": nf}


def executar_caso(despesas, pol=None, cam=None, cc="OUTRO"):
    envelope = {"colaborador": {"id": "1", "nome": "Teste", "centro_custo": cc},
                "periodo": {"competencia": "2026-07", "inicio": "2026-07-01",
                            "fim": "2026-07-31"}, "despesas": despesas}
    # Serialização preserva o contrato JSON e impede que fixtures usem Decimal diretamente.
    def carregar(d, codigo):
        return parse(json.dumps(d, ensure_ascii=False), codigo)
    return executar(carregar(envelope, "JSON_INVALIDO"),
                    carregar(pol if pol is not None else politica(), "POLITICA_INVALIDA"),
                    carregar(cam if cam is not None else cambio(), "CAMBIO_INVALIDO"))


class TestAuditoriaRegrasFinanceiras(unittest.TestCase):
    def test_ac034_representacao_politica_200_restringe_teto(self):
        r = executar_caso([despesa("r1", 340, "representacao")],
                          politica(representacao=200), cc="CC-COMERCIAL")
        self.assertEqual(r["items"][0]["status"], "PARCIAL")
        self.assertEqual(r["items"][0]["valor_reembolsavel"], numero("200.00"))
        self.assertIn("LIMITE_DIARIO", r["items"][0]["motivos"])

    def test_ac034_representacao_politica_500_nao_supera_300(self):
        r = executar_caso([despesa("r1", 340, "representacao")],
                          politica(representacao=500), cc="CC-COMERCIAL")
        self.assertEqual(r["items"][0]["valor_reembolsavel"], numero("300.00"))

    def test_ac004_nota_fiscal_100_exato_nao_bloqueia(self):
        r = executar_caso([despesa("n1", 100, nf=False)])
        self.assertEqual(r["items"][0]["status"], "APROVADO")
        self.assertEqual(r["resumo"]["total_reembolsavel"], numero("100.00"))

    def test_ac029_nota_fiscal_100_01_bloqueia_sem_consumir_saldo(self):
        r = executar_caso([despesa("n1", 100.01, nf=False),
                           despesa("n2", 100, nf=True)])
        self.assertIn("NOTA_FISCAL_OBRIGATORIA_AUSENTE", r["items"][0]["motivos"])
        self.assertEqual(r["items"][0]["valor_reembolsavel"], numero("0.00"))
        self.assertEqual(r["items"][1]["valor_reembolsavel"], numero("100.00"))

    def test_ac023_cotacao_duplicada_mesmo_valor_rejeitada(self):
        texto = ('{"moeda_base":"BRL","fonte":"fixture","observacao":"teste",'
                 '"taxas":{"2026-07-13":{"USD":5,"USD":5}}}')
        with self.assertRaises(ErroGlobal) as cm:
            executar_caso([despesa("a", 10)], cam=parse(texto, "CAMBIO_INVALIDO"))
        self.assertEqual(cm.exception.codigo, "CAMBIO_INVALIDO")

    def test_ac023_cambio_invalido_em_data_nao_utilizada(self):
        cam = cambio()
        cam["taxas"]["2026-07-14"] = {"EUR": 0}
        with self.assertRaises(ErroGlobal) as cm:
            executar_caso([despesa("a", 10)], cam=cam)
        self.assertEqual(cm.exception.codigo, "CAMBIO_INVALIDO")

    def test_ac028_limite_mensal_compartilhado(self):
        r = executar_caso([despesa("m1", 70, "transporte"),
                           despesa("m2", 50, "transporte", dia="2026-07-14")],
                          politica(mensal=100))
        self.assertEqual([x["valor_reembolsavel"] for x in r["items"]],
                         [numero("70.00"), numero("30.00")])
        self.assertIn("LIMITE_MENSAL", r["items"][1]["motivos"])

    def test_ac031_reconciliacao_de_bases(self):
        r = executar_caso([despesa("a", 80), despesa("b", 50),
                           despesa("c", 30, categoria="nao_prevista")],
                          politica(alimentacao=100))
        s = r["resumo"]
        self.assertEqual(s["total_original_convertido"], numero("160.00"))
        self.assertEqual(s["total_solicitado"], numero("130.00"))
        self.assertEqual(s["total_reembolsavel"], numero("100.00"))
        self.assertEqual(s["total_nao_reembolsavel"], numero("30.00"))
        self.assertEqual(s["total_nao_reembolsavel"],
                         s["total_solicitado"] - s["total_reembolsavel"])

    def test_ac036_moedas_diferentes_nao_sao_duplicatas(self):
        a = despesa("usd", 10, moeda="USD")
        b = despesa("eur", 10, moeda="EUR")
        b["descricao"] = a["descricao"]
        r = executar_caso([a, b])
        self.assertNotIn("DUPLICATA", r["items"][1]["motivos"])
        self.assertIsNone(r["items"][1]["duplicata_de_indice"])
        self.assertEqual(r["resumo"]["total_original_convertido"], numero("110.00"))


if __name__ == "__main__":
    unittest.main()
