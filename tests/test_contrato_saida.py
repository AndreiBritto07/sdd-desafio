"""Regressões de formato monetário e hospedagem do Envelope 2."""
import json
import re
import unittest
from decimal import Decimal
from pathlib import Path

from src.motor import executar, serializar


class TestContratoSaida(unittest.TestCase):
    def test_serializacao_preserva_duas_casas_em_json_original(self):
        texto = serializar({
            'valor_original': Decimal('340.0'),
            'valor_reembolsavel': Decimal('300'),
            'valor_convertido': Decimal('85.26'),
        })
        self.assertRegex(texto, r'"valor_original"\s*:\s*340\.00\s*[,}]')
        self.assertRegex(texto, r'"valor_reembolsavel"\s*:\s*300\.00\s*[,}]')
        self.assertRegex(texto, r'"valor_convertido"\s*:\s*85\.26\s*[,}]')
        self.assertEqual(json.loads(texto)['valor_reembolsavel'], 300)

    def test_hospedagem_sem_diarias_limita_a_400_e_avisa(self):
        # Regressão do cenário observado no Envelope 2, sem presumir
        # multiplicação por diárias não informadas.
        entrada = {
            'colaborador': {'id': 'C-001', 'nome': 'Teste', 'centro_custo': 'CC-COMERCIAL'},
            'periodo': {'competencia': '2026-07', 'inicio': '2026-07-01', 'fim': '2026-07-31'},
            'despesas': [{
                'id': 'e-007', 'data': '2026-07-15', 'categoria': 'hospedagem',
                'descricao': 'Hospedagem', 'fornecedor': 'Hotel',
                'valor': Decimal('1200.00'), 'moeda': 'BRL', 'tem_nota_fiscal': True,
            }],
        }
        politica = {
            'versao': 'v4', 'vigencia': '2026-07-01', 'moeda_base': 'BRL',
            'padrao': {'hospedagem': {'limite': Decimal('250'), 'periodicidade': 'diaria'}},
            'centros_custo': {'CC-COMERCIAL': {
                'hospedagem': {'limite': Decimal('400'), 'periodicidade': 'diaria'},
            }},
            'nota_fiscal_obrigatoria_acima_de': Decimal('100'),
            'acrescimo_em_viagem_percentual': Decimal('50'),
        }
        cambio = {'moeda_base': 'BRL', 'fonte': 'PTAX', 'observacao': '',
                  'taxas': {'2026-07-15': {'USD': Decimal('5.42')}}}
        resultado = executar(entrada, politica, cambio)
        item = resultado['items'][0]
        self.assertEqual(item['valor_reembolsavel'], Decimal('400.00'))
        self.assertEqual(item['status'], 'PARCIAL')
        self.assertIn('DIARIAS_NAO_INFORMADAS', item['avisos'])
        self.assertIn('LIMITE_DIARIO', item['motivos'])

    def test_cli_original_usa_duas_casas_se_resultado_existe(self):
        caminho = Path('resultado-envelope.json')
        if not caminho.exists():
            self.skipTest('Execute a CLI para gerar resultado-envelope.json')
        texto = caminho.read_text(encoding='utf-8')
        self.assertRegex(texto, r'"valor_reembolsavel"\s*:\s*300\.00\s*[,}]')
        self.assertRegex(texto, r'"valor_reembolsavel"\s*:\s*400\.00\s*[,}]')
        json.loads(texto)


if __name__ == '__main__':
    unittest.main()
