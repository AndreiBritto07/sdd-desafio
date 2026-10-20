"""Testes complementares de regressão do motor SDD (spec 0.2).

Execute na raiz do repositório:
    python -m unittest tests.test_criterios_complementares -v

Os testes não alteram os arquivos de produção. Uma falha exige análise
conjunta com spec.md e DECISIONS.md antes de mudar o motor.
"""
import json
import subprocess
import sys
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from src.motor import executar, parse, serializar


def politica():
    return {
        "versao": "v4", "vigencia": "2026-07-01", "moeda_base": "BRL",
        "padrao": {
            "alimentacao": {"limite": Decimal("60"), "periodicidade": "dia"},
            "transporte": {"limite": Decimal("100"), "periodicidade": "mes"},
            "hospedagem": {"limite": Decimal("400"), "periodicidade": "dia"},
        },
        "centros_custo": {
            "CC-COMERCIAL": {
                "alimentacao": {"limite": Decimal("60"), "periodicidade": "dia"},
                "representacao": {"limite": Decimal("500"), "periodicidade": "dia"},
            },
            "CC-ENG-PLATAFORMA": {
                "hospedagem": {"limite": Decimal("400"), "periodicidade": "dia"},
            },
        },
        "nota_fiscal_obrigatoria_acima_de": Decimal("100"),
        "acrescimo_em_viagem_percentual": Decimal("50"),
    }


def cambio():
    return {"moeda_base": "BRL", "fonte": "fixture", "observacao": "teste",
            "taxas": {"2026-07-13": {"USD": Decimal("5.42")}}}


def despesa(ident, valor, *, categoria="alimentacao", moeda="BRL", data="2026-07-13", nf=True):
    return {"id": ident, "data": data, "categoria": categoria,
            "descricao": "Despesa " + str(ident), "fornecedor": "Fornecedor",
            "valor": Decimal(str(valor)), "moeda": moeda, "tem_nota_fiscal": nf}


def processar(despesas, *, centro="CC-ADM", pol=None, cam=None):
    entrada = {"colaborador": {"id": "C-1", "nome": "Pessoa", "centro_custo": centro},
               "periodo": {"competencia": "2026-07", "inicio": "2026-07-01", "fim": "2026-07-31"},
               "despesas": despesas}
    return executar(entrada, pol if pol is not None else politica(), cam if cam is not None else cambio())


class TestCriteriosComplementares(unittest.TestCase):
    def test_ac001_limite_diario_na_ordem_72_50_e_38(self):
        r = processar([despesa("a", "72.50"), despesa("b", "38.00")])
        self.assertEqual([i["valor_reembolsavel"] for i in r["items"]],
                         [Decimal("60.00"), Decimal("0.00")])
        self.assertIn("LIMITE_DIARIO", r["items"][1]["motivos"])

    def test_ac002_ordem_invertida_38_e_72_50(self):
        r = processar([despesa("a", "38.00"), despesa("b", "72.50")])
        self.assertEqual([i["valor_reembolsavel"] for i in r["items"]],
                         [Decimal("38.00"), Decimal("22.00")])

    def test_ac007_id_repetido_e_identificacao(self):
        a = despesa("repetido", "10.00")
        b = despesa("repetido", "15.00")
        r = processar([a, b])
        self.assertIn("ID_REPETIDO", [e["codigo"] for e in r["items"][1]["erros"]])
        self.assertEqual(r["items"][1]["valor_reembolsavel"], Decimal("0.00"))

    def test_ac024_moeda_omitida_usa_brl(self):
        d = despesa("a", "10.00")
        del d["moeda"]
        r = processar([d])
        self.assertEqual(r["items"][0]["moeda"], "BRL")
        self.assertEqual(r["items"][0]["valor_convertido"], Decimal("10.00"))

    def test_ac024_moeda_minuscula_invalida(self):
        r = processar([despesa("a", "10.00", moeda="usd")])
        self.assertEqual(r["items"][0]["status"], "RECUSADO")
        self.assertIn("moeda", [e["campo"] for e in r["items"][0]["erros"]])

    def test_ac026_arredondamento_meio_para_cima(self):
        cam = cambio()
        cam["taxas"]["2026-07-13"]["USD"] = Decimal("1.005")
        r = processar([despesa("a", "1.00", moeda="USD")], cam=cam)
        self.assertEqual(r["items"][0]["valor_convertido"], Decimal("1.01"))

    def test_ac030_sem_cotacao_nao_gera_reembolso(self):
        r = processar([despesa("a", "10.00", moeda="EUR")])
        self.assertEqual(r["items"][0]["status"], "RECUSADO")
        self.assertIn("MOEDA_SEM_COTACAO", r["items"][0]["motivos"])
        self.assertFalse(r["resumo"]["totais_completos"])

    def test_ac033_centro_desconhecido_usa_politica_padrao(self):
        r = processar([despesa("a", "80.00")], centro="CENTRO-NAO-CADASTRADO")
        self.assertEqual(r["items"][0]["valor_reembolsavel"], Decimal("60.00"))

    def test_ac035_hospedagem_proibida_para_engenharia(self):
        r = processar([despesa("a", "50.00", categoria="hospedagem")], centro="CC-ENG-PLATAFORMA")
        self.assertEqual(r["items"][0]["status"], "RECUSADO")
        self.assertIn("CATEGORIA_NAO_PERMITIDA", r["items"][0]["motivos"])

    def test_ac017_cli_sucesso_e_erro_global(self):
        raiz = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmp:
            pasta = Path(tmp)
            entrada = pasta / "entrada.json"
            saida = pasta / "saida.json"
            pol = pasta / "politica.json"
            cam = pasta / "cambio.json"
            entrada.write_text(json.dumps({
                "colaborador": {"id": "1", "nome": "Pessoa", "centro_custo": "CC-ADM"},
                "periodo": {"competencia": "2026-07", "inicio": "2026-07-01", "fim": "2026-07-31"},
                "despesas": []}), encoding="utf-8")
            pol.write_text(serializar(politica()), encoding="utf-8")
            cam.write_text(serializar(cambio()), encoding="utf-8")
            comando = [sys.executable, "-m", "src", "calcular", "--input", str(entrada),
                       "--output", str(saida), "--politica", str(pol), "--cambio", str(cam)]
            sucesso = subprocess.run(comando, cwd=raiz, capture_output=True, text=True)
            self.assertEqual(sucesso.returncode, 0, sucesso.stderr)
            self.assertIn("resumo", json.loads(saida.read_text(encoding="utf-8")))
            entrada.write_text("{", encoding="utf-8")
            erro = subprocess.run(comando, cwd=raiz, capture_output=True, text=True)
            self.assertEqual(erro.returncode, 2, erro.stderr)
            self.assertEqual(json.loads(saida.read_text(encoding="utf-8"))["erro"]["codigo"], "JSON_INVALIDO")
            entrada.unlink()
            io = subprocess.run(comando, cwd=raiz, capture_output=True, text=True)
            self.assertEqual(io.returncode, 3, io.stderr)


if __name__ == "__main__":
    unittest.main()
