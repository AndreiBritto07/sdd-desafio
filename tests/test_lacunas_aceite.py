"""Auditoria complementar da spec 0.2: casos de borda e contratos ainda não demonstrados.

Rodar na raiz: python -m unittest discover -s tests -v
Falhas indicam lacunas a investigar, NÃO autorizam alterar expectativas sem revisar a spec.
"""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from src.motor import executar, parse, serializar
from src.validacao_global import ErroGlobal


def P():
    return parse('{"versao":"v4","vigencia":"2026-07-01","moeda_base":"BRL",'
                 '"padrao":{"alimentacao":{"limite":60,"periodicidade":"dia"},'
                 '"hospedagem":{"limite":400,"periodicidade":"diaria"},'
                 '"transporte":{"limite":100,"periodicidade":"mes"}},'
                 '"centros_custo":{},"nota_fiscal_obrigatoria_acima_de":100,'
                 '"acrescimo_em_viagem_percentual":50}', 'POLITICA_INVALIDA')


def C():
    return parse('{"moeda_base":"BRL","fonte":"teste","observacao":"teste",'
                 '"taxas":{"2026-07-10":{"USD":5.40},"2026-07-13":{"USD":5.42}}}', 'CAMBIO_INVALIDO')


def D(i='a', valor='10.00', **changes):
    d = {'id': i, 'data': '2026-07-13', 'categoria': 'alimentacao',
         'descricao': 'Compra '+str(i), 'fornecedor': 'Loja',
         'valor': Decimal(valor), 'tem_nota_fiscal': True, 'moeda': 'BRL'}
    d.update(changes)
    return d


def E(ds, **changes):
    e = {'colaborador': {'id': 'C1', 'nome': 'Pessoa', 'centro_custo': 'CC-ADM'},
         'periodo': {'competencia': '2026-07', 'inicio': '2026-07-01', 'fim': '2026-07-31'},
         'despesas': ds}
    e.update(changes)
    return e


def run(ds, pol=None, cam=None, **changes):
    return executar(E(ds, **changes), pol if pol is not None else P(), cam if cam is not None else C())


class TestLacunasAceite(unittest.TestCase):
    def test_ac003_fronteiras_do_limite(self):
        for valor, esperado in [('59.99','59.99'),('60.00','60.00'),('60.01','60.00')]:
            with self.subTest(valor=valor):
                r=run([D(valor=valor)])
                self.assertEqual(r['items'][0]['valor_reembolsavel'],Decimal(esperado))

    def test_ac005_viagem_textual_nao_amplia_limite(self):
        r=run([D(valor='80.00', descricao='viagem internacional de trabalho')])
        self.assertEqual(r['items'][0]['valor_reembolsavel'],Decimal('60.00'))
        self.assertIn('VIAGEM_NAO_INFORMADA',r['avisos'])

    def test_ac005_lista_vazia_mantem_aviso_e_totais(self):
        r=run([])
        self.assertIn('VIAGEM_NAO_INFORMADA',r['avisos'])
        self.assertTrue(r['resumo']['totais_completos'])
        self.assertEqual(r['resumo']['total_reembolsavel'],0)

    def test_ac006_periodo_inclusivo(self):
        r=run([D('inicio',data='2026-07-01'),D('fim',data='2026-07-31')])
        self.assertEqual([i['status'] for i in r['items']],['APROVADO','APROVADO'])

    def test_ac006_data_invalida_nao_aborta_lote(self):
        r=run([D('ruim',data='2026-02-30'),D('bom')])
        self.assertEqual(r['items'][0]['status'],'RECUSADO')
        self.assertIn('DADO_INVALIDO',r['items'][0]['motivos'])
        self.assertEqual(r['items'][1]['status'],'APROVADO')

    def test_ac008_zero_negativo_nao_compensam(self):
        r=run([D('zero','0'),D('neg','-15'),D('ok','60')])
        self.assertEqual([i['status'] for i in r['items']],['RECUSADO','RECUSADO','APROVADO'])
        self.assertEqual(r['resumo']['total_reembolsavel'],60)

    def test_ac009_aceita_inteiro_uma_e_duas_casas(self):
        for raw in ('10','10.5','10.50'):
            with self.subTest(raw=raw):
                d=D(); d['valor']=parse('{"v":'+raw+'}','JSON_INVALIDO')['v']
                r=run([d]); self.assertEqual(r['items'][0]['status'],'APROVADO')
                self.assertIn('"valor_original": 10.',serializar(r))

    def test_ac009_tres_casas_invalida_sem_arredondar(self):
        r=run([D(valor='10.501')])
        self.assertIsNone(r['items'][0]['valor_original'])
        self.assertIn('ENTRADA_INVALIDA',r['items'][0]['motivos'])

    def test_ac010_hospedagens_compartilham_diaria(self):
        r=run([D('h1','250',categoria='hospedagem'),D('h2','250',categoria='hospedagem')])
        self.assertEqual([i['valor_reembolsavel'] for i in r['items']],[Decimal(250),Decimal(150)])
        self.assertTrue(all('DIARIAS_NAO_INFORMADAS' in i['avisos'] for i in r['items']))

    def test_ac010_texto_duas_diarias_nao_multiplica_teto(self):
        r=run([D('h1','450',categoria='hospedagem',descricao='2 diárias')])
        self.assertEqual(r['items'][0]['valor_reembolsavel'],400)

    def test_ac011_normalizacao_ascii_sem_aliases(self):
        r=run([D('a',categoria='  ALIMENTACAO  '),D('b',categoria='alimentação')])
        self.assertEqual(r['items'][0]['categoria_normalizada'],'alimentacao')
        self.assertIn('CATEGORIA_NAO_PERMITIDA',r['items'][1]['motivos'])

    def test_ac012_fim_de_semana_permitido(self):
        r=run([D('sab',data='2026-07-11'),D('dom',data='2026-07-12')])
        self.assertEqual([i['status'] for i in r['items']],['APROVADO','APROVADO'])

    def test_ac013_extras_ignorados(self):
        base=run([D()]); d=D(); d['campo_extra']='xyz'
        e=E([d], campo_extra='xyz'); e['colaborador']['extra']='x';e['periodo']['extra']='x'
        alterado=executar(e,P(),C())
        self.assertEqual(alterado['resumo'],base['resumo'])
        self.assertEqual(alterado['items'][0]['valor_reembolsavel'],base['items'][0]['valor_reembolsavel'])

    def test_ac013_booleano_estrito_e_chaves_exatas(self):
        for val in (1,'true',None):
            with self.subTest(val=val):
                r=run([D(tem_nota_fiscal=val)])
                self.assertIn('tem_nota_fiscal',[x['campo'] for x in r['items'][0]['erros']])
        d=D();d['temNotaFiscal']=d.pop('tem_nota_fiscal')
        self.assertIn('tem_nota_fiscal',[x['campo'] for x in run([d])['items'][0]['erros']])

    def test_ac014_erro_estrutural_em_ordem_fixa(self):
        d={'moeda':'usd','tem_nota_fiscal':1,'valor':'10','fornecedor':'',
           'descricao':None,'categoria':3,'data':'errado','id':None}
        campos=[e['campo'] for e in run([d])['items'][0]['erros']]
        self.assertEqual(campos,['id','data','categoria','descricao','fornecedor','valor','tem_nota_fiscal','moeda'])

    def test_ac014_geracao_id_colisao_com_fornecido_invalido(self):
        d=D('gerado-0');d['valor']=Decimal('-1')
        sem_id=D('a');del sem_id['id']
        r=run([sem_id,d])
        self.assertEqual(r['items'][0]['id'],'gerado-0-1')

    def test_ac014_id_presente_invalido_nao_gera_substituto(self):
        r=run([D(None)])
        self.assertIsNone(r['items'][0]['id'])
        self.assertEqual(r['items'][0]['erros'][0]['campo'],'id')

    def test_ac014_id_ausente_em_item_invalido_e_gerado(self):
        d=D();del d['id'];d['data']='data ruim'
        self.assertEqual(run([d])['items'][0]['id'],'gerado-0')

    def test_ac007_id_equivalente_casefold_trim_ascii(self):
        r=run([D(' A '),D('a',valor='11')])
        self.assertEqual(r['items'][0]['id'],' A ')
        self.assertIn('ID_REPETIDO',[e['codigo'] for e in r['items'][1]['erros']])

    def test_ac007_conteudo_duplicado_aponta_canonico_inelegivel(self):
        a=D('a',categoria='categoria-proibida',descricao='  CAFÉ ',fornecedor=' LOJA ')
        b=D('b',categoria='categoria-proibida',descricao=' café ',fornecedor='loja')
        r=run([a,b]);self.assertEqual(r['items'][1]['status'],'IGNORADO')
        self.assertEqual(r['items'][1]['duplicata_de_indice'],0)

    def test_ac018_contagens_excluem_invalidos_mas_incluem_duplicatas(self):
        a=D('a'); b=D('b',descricao=a['descricao']); c=D('a',valor='20'); d=D('d',valor='0')
        r=run([a,b,c,d]);s=r['resumo']
        self.assertEqual(s['total_itens'],3)
        self.assertEqual(s['aprovados']+s['parciais']+s['recusados']+s['ignorados'],3)

    def test_ac015_motivos_sao_unicos_e_singular_primeiro(self):
        r=run([D('a',valor='80')])
        for i in r['items']:
            self.assertEqual(len(i['motivos']),len(set(i['motivos'])))
            self.assertEqual(i['motivo'],i['motivos'][0] if i['motivos'] else 'DENTRO_DO_LIMITE')

    def test_ac016_recusa_somente_por_limite_conta_solicitado(self):
        r=run([D('a','60'),D('b','20')]);s=r['resumo']
        self.assertEqual(s['total_solicitado'],80)
        self.assertEqual(s['total_reembolsavel'],60)
        self.assertEqual(s['total_nao_reembolsavel'],20)

    def test_ac019_chaves_repetidas_em_objeto_aninhado(self):
        with self.assertRaises(ErroGlobal) as ctx:
            parse('{"colaborador":{"id":"1","id":"2"}}','JSON_INVALIDO')
        self.assertEqual(ctx.exception.codigo,'JSON_INVALIDO')

    def test_ac020_colaborador_incompleto_rejeita_lote(self):
        for chave in ('id','nome','centro_custo'):
            e=E([]);del e['colaborador'][chave]
            with self.subTest(chave=chave),self.assertRaises(ErroGlobal) as ctx:
                executar(e,P(),C())
            self.assertEqual(ctx.exception.codigo,'ENTRADA_INVALIDA')

    def test_ac021_periodo_invertido_retornado(self):
        periodo={'competencia':'2026-07','inicio':'2026-07-31','fim':'2026-07-01'}
        r=run([D()],periodo=periodo)
        self.assertEqual((r['periodo']['inicio'],r['periodo']['fim']),('2026-07-01','2026-07-31'))

    def test_ac022_politica_invalida_rejeitada_globalmente(self):
        for chave in ('versao','vigencia','padrao'):
            pol=P();del pol[chave]
            with self.subTest(chave=chave),self.assertRaises(ErroGlobal) as ctx:
                run([D()],pol=pol)
            self.assertEqual(ctx.exception.codigo,'POLITICA_INVALIDA')

    def test_ac023_cambio_cientifico_rejeitado(self):
        cam=parse('{"moeda_base":"BRL","fonte":"x","observacao":"x",'
                  '"taxas":{"2026-07-13":{"USD":5.42e0}}}','CAMBIO_INVALIDO')
        with self.assertRaises(ErroGlobal) as ctx: run([D()],cam=cam)
        self.assertEqual(ctx.exception.codigo,'CAMBIO_INVALIDO')

    def test_ac023_cambio_string_zero_negativo_e_moeda_invalida(self):
        for moeda,valor in [('USD','"5.42"'),('USD','0'),('USD','-1'),('usd','5.42')]:
            with self.subTest(moeda=moeda,valor=valor):
                cam=parse('{"moeda_base":"BRL","fonte":"x","observacao":"x",'
                          '"taxas":{"2026-07-13":{"'+moeda+'":'+valor+'}}}','CAMBIO_INVALIDO')
                with self.assertRaises(ErroGlobal) as ctx: run([],cam=cam)
                self.assertEqual(ctx.exception.codigo,'CAMBIO_INVALIDO')

    def test_ac023_cambio_zeros_finais_permitidos(self):
        cam=C();cam['taxas']['2026-07-13']['USD']=parse('{"v":5.4200}','CAMBIO_INVALIDO')['v']
        r=run([D(moeda='USD')],cam=cam)
        self.assertEqual(r['items'][0]['valor_convertido'],Decimal('54.20'))

    def test_ac024_moeda_nula_invalida_item(self):
        r=run([D(moeda=None),D('ok')])
        self.assertIn('moeda',[x['campo'] for x in r['items'][0]['erros']])
        self.assertEqual(r['items'][1]['status'],'APROVADO')

    def test_ac025_cotacao_exata_precede_anterior(self):
        r=run([D(moeda='USD')]);self.assertEqual(r['items'][0]['valor_convertido'],Decimal('54.20'))

    def test_ac025_cotacao_futura_nao_e_utilizada(self):
        r=run([D(moeda='USD',data='2026-07-01')])
        self.assertIn('MOEDA_SEM_COTACAO',r['items'][0]['motivos'])

    def test_ac026_conversao_arredondada_a_zero_valida(self):
        cam=C();cam['taxas']['2026-07-13']['USD']=Decimal('0.0001')
        r=run([D(valor='1.00',moeda='USD')],cam=cam)
        self.assertEqual(r['items'][0]['status'],'APROVADO')
        self.assertEqual(r['items'][0]['valor_convertido'],0)

    def test_ac027_teto_inclusivo_e_acima_rejeitado(self):
        r=run([D('limite','1000000000000'),D('acima','1000000000000.01')])
        self.assertIsNotNone(r['items'][0]['valor_original'])
        self.assertIsNone(r['items'][1]['valor_original'])

    def test_ac027_cientifico_original_rejeitado(self):
        d=D();d['valor']=parse('{"v":1.05e1}','JSON_INVALIDO')['v']
        self.assertIn('ENTRADA_INVALIDA',run([d])['items'][0]['motivos'])

    def test_ac028_mensal_compartilhado_entre_dias(self):
        r=run([D('a','70',categoria='transporte'),D('b','70',categoria='transporte',data='2026-07-14')])
        self.assertEqual([i['valor_reembolsavel'] for i in r['items']],[Decimal(70),Decimal(30)])

    def test_ac029_nota_fiscal_sobre_preliminar(self):
        p=P();p['padrao']['alimentacao']['limite']=Decimal('120')
        r=run([D('sem','150',tem_nota_fiscal=False),D('com','100')],pol=p)
        self.assertIn('NOTA_FISCAL_OBRIGATORIA_AUSENTE',r['items'][0]['motivos'])
        self.assertEqual(r['items'][1]['valor_reembolsavel'],100)

    def test_ac030_sem_cotacao_marca_incompleto_mas_continua(self):
        r=run([D('sem',moeda='EUR'),D('ok')])
        self.assertFalse(r['resumo']['totais_completos'])
        self.assertEqual(r['items'][1]['status'],'APROVADO')

    def test_ac031_bruto_inclui_inelegivel_e_duplicata(self):
        a=D('a',categoria='inexistente');b=D('b',categoria='inexistente',descricao=a['descricao'])
        r=run([a,b]);self.assertEqual(r['resumo']['total_original_convertido'],20)
        self.assertEqual(r['resumo']['total_solicitado'],0)

    def test_ac032_serializacao_monetaria_duas_casas(self):
        r=run([D(valor='10.5')]);s=serializar(r)
        self.assertIn('"valor_original": 10.50',s)
        self.assertIn('"total_reembolsavel": 10.50',s)
        self.assertNotIn('"valor_original": "10.50"',s)

    def test_ac033_categoria_ausente_na_politica_recusada(self):
        r=run([D(categoria='nao-permitida')]);self.assertIn('CATEGORIA_NAO_PERMITIDA',r['items'][0]['motivos'])

    def test_ac034_comercial_300_exato(self):
        p=P();p['centros_custo']['CC-COMERCIAL']={'representacao':{'limite':Decimal('500'),'periodicidade':'dia'}}
        e=E([D(categoria='representacao',valor='300')]);e['colaborador']['centro_custo']='CC-COMERCIAL'
        r=executar(e,p,C());self.assertEqual(r['items'][0]['valor_reembolsavel'],300)

    def test_ac036_moedas_diferentes_nao_duplicam(self):
        a=D('a');b=D('b',moeda='USD',descricao=a['descricao'])
        r=run([a,b]);self.assertNotEqual(r['items'][1]['status'],'IGNORADO')

    def test_ac017_cli_argumento_obrigatorio_ausente_saida_2(self):
        p=subprocess.run([sys.executable,'-m','src','calcular'],capture_output=True,text=True)
        self.assertEqual(p.returncode,2)

    def test_ac017_cli_io_entrada_inexistente_saida_3(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);pol=root/'p.json';cam=root/'c.json';out=root/'o.json'
            pol.write_text(serializar(P()),encoding='utf-8')
            cam.write_text(serializar(C()),encoding='utf-8')
            p=subprocess.run([sys.executable,'-m','src','calcular','--input',str(root/'nao_existe.json'),
                '--output',str(out),'--politica',str(pol),'--cambio',str(cam)],capture_output=True,text=True)
            self.assertEqual(p.returncode,3)
            self.assertEqual(json.loads(out.read_text(encoding='utf-8'))['erro']['codigo'],'ERRO_IO')

    def test_ac017_cli_escrita_invalida_saida_3(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);inp=root/'e.json';pol=root/'p.json';cam=root/'c.json'
            inp.write_text(serializar(E([])),encoding='utf-8')
            pol.write_text(serializar(P()),encoding='utf-8')
            cam.write_text(serializar(C()),encoding='utf-8')
            p=subprocess.run([sys.executable,'-m','src','calcular','--input',str(inp),
                '--output',str(root/'pasta_ausente'/'saida.json'),'--politica',str(pol),
                '--cambio',str(cam)],capture_output=True,text=True)
            self.assertEqual(p.returncode,3)

if __name__ == '__main__':
    unittest.main()
