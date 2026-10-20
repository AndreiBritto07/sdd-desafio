import unittest
from src.motor import parse, executar, serializar
from decimal import Decimal
from src.validacao_global import ErroGlobal

P = '{"versao":"v4","vigencia":"2026-07-01","moeda_base":"BRL","padrao":{"alimentacao":{"limite":60,"periodicidade":"dia"}},"centros_custo":{},"nota_fiscal_obrigatoria_acima_de":100,"acrescimo_em_viagem_percentual":50}'
C = '{"moeda_base":"BRL","fonte":"x","observacao":"x","taxas":{"2026-07-13":{"USD":5.42}}}'
E = '{"colaborador":{"id":"1","nome":"A","centro_custo":"X"},"periodo":{"competencia":"2026-07","inicio":"2026-07-01","fim":"2026-07-31"},"despesas":[{"data":"2026-07-13","categoria":"alimentacao","descricao":"Almoco","fornecedor":"F","valor":10.5,"tem_nota_fiscal":false}]}'
class TestMotor(unittest.TestCase):
    def run_motor(self, entrada=E):
        return executar(parse(entrada,'JSON_INVALIDO'),parse(P,'POLITICA_INVALIDA'),parse(C,'CAMBIO_INVALIDO'))
    def test_aprovacao_basica(self):
        r=self.run_motor(); self.assertEqual(r['resumo']['total_reembolsavel'],10.5)
        self.assertIn('"valor_reembolsavel": 10.50',serializar(r))
    def test_valor_cientifico_invalido(self):
        r=self.run_motor(E.replace('10.5','1.05e1'))
        self.assertEqual(r['items'][0]['status'],'RECUSADO')
    def test_duplicidade_chave_json(self):
        with self.assertRaises(ErroGlobal): parse('{"x":1,"x":2}','JSON_INVALIDO')
    def test_limite_parcial(self):
        r=self.run_motor(E.replace('10.5','80'))
        self.assertEqual(r['items'][0]['status'],'PARCIAL')
        self.assertEqual(r['resumo']['total_reembolsavel'],60)
    def test_cotacao_anterior(self):
        r=self.run_motor(E.replace('"valor":10.5','"valor":10.5,"moeda":"USD"').replace('2026-07-13','2026-07-14'))
        self.assertEqual(r['items'][0]['valor_convertido'],Decimal('56.91'))
if __name__=='__main__': unittest.main()
