import unittest
from src.validacao_global import ErroGlobal, carregar_entrada, validar_envelope, falha


def valido():
    return {'colaborador': {'id':'1','nome':'Pessoa','centro_custo':'CC-ADM'},
            'periodo': {'competencia':'2026-07','inicio':'2026-07-01','fim':'2026-07-31'},
            'despesas': []}

class TestValidacaoGlobal(unittest.TestCase):
    def test_envelope_invalido_rejeita_lote(self):
        for alteracao in ({'despesas':{}}, {'colaborador':[]}, {'periodo':None}):
            with self.subTest(alteracao=alteracao):
                dados = valido(); dados.update(alteracao)
                with self.assertRaises(ErroGlobal) as ctx:
                    validar_envelope(dados)
                self.assertEqual(ctx.exception.codigo, 'ENTRADA_INVALIDA')
                self.assertNotIn('items', falha(ctx.exception))
                self.assertNotIn('resumo', falha(ctx.exception))

    def test_periodo_global_invalido_rejeita_lote(self):
        for campo, valor in [('competencia','2026-13'),('inicio','2026-07-32'),('fim','2026-08-01')]:
            with self.subTest(campo=campo):
                dados=valido(); dados['periodo'][campo]=valor
                with self.assertRaises(ErroGlobal) as ctx:
                    validar_envelope(dados)
                self.assertEqual(ctx.exception.codigo,'ENTRADA_INVALIDA')

    def test_periodo_invertido_corrigido(self):
        dados=valido(); dados['periodo']['inicio']='2026-07-31'; dados['periodo']['fim']='2026-07-01'
        self.assertEqual(validar_envelope(dados)['periodo']['inicio'],'2026-07-01')

    def test_json_malformado_e_chave_repetida(self):
        for texto in ('{', '{"a":1,"a":2}', '{"a":NaN}'):
            with self.subTest(texto=texto), self.assertRaises(ErroGlobal) as ctx:
                carregar_entrada(texto)
            self.assertEqual(ctx.exception.codigo,'JSON_INVALIDO')

    def test_colaborador_obrigatorio(self):
        for campo in ('id','nome','centro_custo'):
            for valor in (None, '', '  ', 12, []):
                with self.subTest(campo=campo,valor=valor):
                    dados=valido(); dados['colaborador'][campo]=valor
                    with self.assertRaises(ErroGlobal): validar_envelope(dados)

if __name__=='__main__': unittest.main()
