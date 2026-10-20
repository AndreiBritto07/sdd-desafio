"""Motor de reembolso v0.2. Somente biblioteca padrão Python 3.11."""
import json
import re
import unicodedata
from datetime import date
from decimal import Decimal, ROUND_HALF_UP, localcontext, InvalidOperation
from .validacao_global import ErroGlobal, pares_unicos, validar_envelope, data_estrita

CENT = Decimal('0.01')
ZERO = Decimal('0.00')
TETO = Decimal('1000000000000')
ASCII = ' \t\n\r\f\v'

class Numero(Decimal):
    def __new__(cls, valor):
        obj = super().__new__(cls, valor)
        obj.lexema = valor
        return obj

def parse(texto, codigo):
    try:
        return json.loads(texto, parse_float=Numero, parse_int=Numero,
                          object_pairs_hook=pares_unicos,
                          parse_constant=lambda v: (_ for _ in ()).throw(ValueError(v)))
    except ErroGlobal as e:
        raise ErroGlobal(codigo, str(e)) from e
    except (ValueError, json.JSONDecodeError, UnicodeError) as e:
        raise ErroGlobal(codigo, f'JSON inválido: {e}') from e

def numero(v, zero=True):
    return isinstance(v, Decimal) and v.is_finite() and (v >= 0 if zero else v > 0) and 'e' not in getattr(v, 'lexema', '').lower()

def dinheiro(v):
    if not numero(v, False) or v > TETO: return False
    raw = getattr(v, 'lexema', str(v))
    return bool(re.fullmatch(r'(?:0|[1-9]\d*)(?:\.\d{1,2})?', raw))

def quant(v):
    with localcontext() as ctx:
        ctx.prec = max(60, len(v.as_tuple().digits) + abs(v.as_tuple().exponent) + 10)
        return v.quantize(CENT, rounding=ROUND_HALF_UP)

def validar_politica(d):
    if not isinstance(d, dict) or d.get('versao') != 'v4' or d.get('moeda_base') != 'BRL':
        raise ErroGlobal('POLITICA_INVALIDA', 'Versão ou moeda-base inválida')
    try: data_estrita(d['vigencia'])
    except (KeyError, ValueError, TypeError): raise ErroGlobal('POLITICA_INVALIDA', 'Vigência inválida')
    if not isinstance(d.get('padrao'), dict) or not isinstance(d.get('centros_custo'), dict):
        raise ErroGlobal('POLITICA_INVALIDA', 'Regras ausentes')
    if not numero(d.get('nota_fiscal_obrigatoria_acima_de')) or not numero(d.get('acrescimo_em_viagem_percentual')):
        raise ErroGlobal('POLITICA_INVALIDA', 'Parâmetros fiscais inválidos')
    for centro, regras in [('padrao', d['padrao']), *d['centros_custo'].items()]:
        if not isinstance(centro, str) or not isinstance(regras, dict):
            raise ErroGlobal('POLITICA_INVALIDA', 'Centro ou regras inválidos')
        for categoria, regra in regras.items():
            if not isinstance(categoria, str) or not isinstance(regra, dict) or not numero(regra.get('limite')) or regra.get('periodicidade') not in ('dia', 'diaria', 'mes'):
                raise ErroGlobal('POLITICA_INVALIDA', f'Regra inválida: {centro}/{categoria}')
            if 'observacao' in regra and not isinstance(regra['observacao'], str):
                raise ErroGlobal('POLITICA_INVALIDA', 'Observação inválida')
    return d

def validar_cambio(d):
    if not isinstance(d, dict) or set(d) != {'moeda_base', 'fonte', 'observacao', 'taxas'} or d['moeda_base'] != 'BRL' or not isinstance(d['fonte'], str) or not isinstance(d['observacao'], str):
        raise ErroGlobal('CAMBIO_INVALIDO', 'Cabeçalho de câmbio inválido')
    taxas = d['taxas']
    if not isinstance(taxas, dict) or not taxas: raise ErroGlobal('CAMBIO_INVALIDO', 'Taxas ausentes')
    for dia, moedas in taxas.items():
        try: data_estrita(dia)
        except (ValueError, TypeError): raise ErroGlobal('CAMBIO_INVALIDO', 'Data de cotação inválida')
        if not isinstance(moedas, dict) or not moedas: raise ErroGlobal('CAMBIO_INVALIDO', 'Moedas ausentes')
        for moeda, taxa in moedas.items():
            if not isinstance(moeda, str) or not re.fullmatch('[A-Z]{3}', moeda) or not numero(taxa, False):
                raise ErroGlobal('CAMBIO_INVALIDO', 'Cotação inválida')
    return d

def cotar(cambio, moeda, dia):
    if moeda == 'BRL': return Decimal(1)
    candidatos = [(d, moedas[moeda]) for d, moedas in cambio['taxas'].items() if d <= dia and moeda in moedas]
    return max(candidatos)[1] if candidatos else None

def normalizar_categoria(s):
    return s.strip(ASCII).translate(str.maketrans('ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'))

def normalizar_texto(s):
    return unicodedata.normalize('NFC', s.strip(ASCII)).casefold()

def base_item(i, despesa, id_saida):
    return dict(indice=i, id=id_saida, categoria_normalizada=None, moeda=None,
                valor_original=None, valor_convertido=None, valor_solicitado=ZERO,
                valor_reembolsavel=ZERO, status='RECUSADO', motivos=[], motivo='DADO_INVALIDO',
                justificativa='Despesa inválida', duplicata_de_indice=None, avisos=[], erros=[])

def adicionar(item, codigo):
    if codigo not in item['motivos']: item['motivos'].append(codigo)

def executar(entrada, politica, cambio):
    dados = validar_envelope(entrada)
    validar_politica(politica)
    validar_cambio(cambio)
    centro = dados['colaborador']['centro_custo']
    regras = politica['centros_custo'].get(centro, politica['padrao'])
    inicio, fim = dados['periodo']['inicio'], dados['periodo']['fim']
    ids_fornecidos = {x['id'].strip(ASCII).casefold() for x in dados['despesas'] if isinstance(x, dict) and isinstance(x.get('id'), str)}
    ids_usados = set(ids_fornecidos)
    ids_validos, conteudos, saldos_dia, saldos_mes = {}, {}, {}, {}
    items, resumo = [], dict(total_itens=0, aprovados=0, parciais=0, recusados=0, ignorados=0,
                              total_original_convertido=ZERO, total_solicitado=ZERO,
                              total_reembolsavel=ZERO, total_nao_reembolsavel=ZERO, totais_completos=True)
    for i, desp in enumerate(dados['despesas']):
        d = desp if isinstance(desp, dict) else {}
        id_val = d.get('id')
        if 'id' not in d:
            gerado = f'gerado-{i}'
            n = 0
            while gerado.casefold() in ids_usados:
                n += 1
                gerado = f'gerado-{i}-{n}'
            ids_usados.add(gerado.casefold())
            id_val = gerado
        elif not isinstance(id_val, str) or not id_val.strip(): id_val = None
        item = base_item(i, desp, id_val)
        erros = item['erros']
        def erro(campo, codigo): erros.append({'campo': campo, 'codigo': codigo})
        if 'id' in d and id_val is None: erro('id','TIPO_OU_FORMATO_INVALIDO')
        try: dia = data_estrita(d.get('data')); data_ok = True
        except (ValueError, TypeError): dia = None; data_ok = False; erro('data', 'TIPO_OU_FORMATO_INVALIDO' if 'data' in d else 'CAMPO_OBRIGATORIO')
        for campo in ('categoria','descricao','fornecedor'):
            if campo not in d: erro(campo,'CAMPO_OBRIGATORIO')
            elif not isinstance(d[campo], str) or not d[campo].strip(): erro(campo,'TIPO_OU_FORMATO_INVALIDO')
        if isinstance(d.get('categoria'), str) and d['categoria'].strip(): item['categoria_normalizada'] = normalizar_categoria(d['categoria'])
        valor = d.get('valor')
        if not dinheiro(valor): erro('valor','TIPO_OU_FORMATO_INVALIDO' if 'valor' in d else 'CAMPO_OBRIGATORIO')
        else: item['valor_original'] = quant(valor)
        if 'tem_nota_fiscal' not in d: erro('tem_nota_fiscal','CAMPO_OBRIGATORIO')
        elif type(d['tem_nota_fiscal']) is not bool: erro('tem_nota_fiscal','TIPO_OU_FORMATO_INVALIDO')
        moeda = d.get('moeda', 'BRL')
        if not isinstance(moeda, str) or not re.fullmatch('[A-Z]{3}', moeda):
            erro('moeda','TIPO_OU_FORMATO_INVALIDO'); moeda = None
        item['moeda'] = moeda
        if item['categoria_normalizada'] == 'hospedagem' and not erros:
            item['avisos'].append('DIARIAS_NAO_INFORMADAS')
        taxa = cotar(cambio, moeda, d['data']) if moeda and data_ok else (Decimal(1) if moeda == 'BRL' else None)
        if item['valor_original'] is not None and moeda is not None and (moeda == 'BRL' or taxa is not None):
            try:
                with localcontext() as ctx:
                    ctx.prec = max(60, len(valor.as_tuple().digits) + len(taxa.as_tuple().digits) + abs(taxa.as_tuple().exponent) + 10)
                    convertido = quant(valor * taxa)
                item['valor_convertido'] = convertido
                resumo['total_original_convertido'] += convertido
            except (InvalidOperation, OverflowError, MemoryError): adicionar(item, 'ENTRADA_INVALIDA')
        else:
            resumo['totais_completos'] = False
        if erros:
            adicionar(item, 'ENTRADA_INVALIDA' if any(e['campo'] in ('valor','moeda') for e in erros) else 'DADO_INVALIDO')
        else:
            resumo['total_itens'] += 1
            chave_id = id_val.strip(ASCII).casefold()
            if chave_id in ids_validos:
                erro('id','ID_REPETIDO'); adicionar(item,'DADO_INVALIDO')
            else:
                ids_validos[chave_id] = i
                chave_conteudo = (d['data'], item['categoria_normalizada'], normalizar_texto(d['fornecedor']), normalizar_texto(d['descricao']), moeda, item['valor_original'])
                if chave_conteudo in conteudos:
                    item['status'] = 'IGNORADO'; adicionar(item,'DUPLICATA'); item['duplicata_de_indice'] = conteudos[chave_conteudo]
                else:
                    conteudos[chave_conteudo] = i
                    categoria = item['categoria_normalizada']
                    regra = regras.get(categoria)
                    if regra is None or (centro == 'CC-ENG-PLATAFORMA' and categoria == 'hospedagem') or (regra and regra['limite'] == 0):
                        adicionar(item,'CATEGORIA_NAO_PERMITIDA')
                    if not inicio <= d['data'] <= fim: adicionar(item,'FORA_DA_COMPETENCIA')
                    if moeda != 'BRL' and taxa is None: adicionar(item,'MOEDA_SEM_COTACAO')
                    if item['valor_convertido'] is None and taxa is not None: adicionar(item,'ENTRADA_INVALIDA')
                    if not item['motivos']:
                        valor_brl = item['valor_convertido']
                        limites = []
                        if regra['periodicidade'] in ('dia','diaria'):
                            limite_dia = regra['limite']
                            if centro == 'CC-COMERCIAL' and categoria == 'representacao': limite_dia = min(limite_dia, Decimal(300))
                            chave = (categoria, d['data'])
                            saldo = max(ZERO, limite_dia - saldos_dia.get(chave,ZERO))
                            limites.append(('LIMITE_DIARIO',saldo,chave))
                        if regra['periodicidade'] == 'mes':
                            chave = (categoria,d['data'][:7]); saldo = max(ZERO,regra['limite'] - saldos_mes.get(chave,ZERO))
                            limites.append(('LIMITE_MENSAL',saldo,chave))
                        preliminar = min([valor_brl] + [x[1] for x in limites])
                        limite_motivos = [codigo for codigo,saldo,_ in limites if saldo < valor_brl]
                        if preliminar > politica['nota_fiscal_obrigatoria_acima_de'] and not d['tem_nota_fiscal']:
                            adicionar(item,'NOTA_FISCAL_OBRIGATORIA_AUSENTE')
                        for codigo in limite_motivos: adicionar(item,codigo)
                        if 'NOTA_FISCAL_OBRIGATORIA_AUSENTE' not in item['motivos']:
                            item['valor_reembolsavel'] = preliminar
                            resumo['total_solicitado'] += valor_brl
                            for codigo,_,chave in limites:
                                if codigo == 'LIMITE_DIARIO': saldos_dia[chave] = saldos_dia.get(chave,ZERO) + preliminar
                                else: saldos_mes[chave] = saldos_mes.get(chave,ZERO) + preliminar
                            item['status'] = 'APROVADO' if preliminar == valor_brl else ('PARCIAL' if preliminar > 0 else 'RECUSADO')
        if item['valor_convertido'] is not None: item['valor_solicitado'] = item['valor_convertido']
        if item['status'] == 'RECUSADO' and not item['motivos']: adicionar(item,'DADO_INVALIDO')
        item['motivo'] = item['motivos'][0] if item['motivos'] else 'DENTRO_DO_LIMITE'
        item['justificativa'] = 'Despesa aprovada integralmente' if item['status'] == 'APROVADO' else ('Despesa duplicada' if item['status'] == 'IGNORADO' else 'Motivos: ' + ', '.join(item['motivos']))
        if not any(e['codigo'] != 'ID_REPETIDO' for e in erros): resumo[{'APROVADO':'aprovados','PARCIAL':'parciais','RECUSADO':'recusados','IGNORADO':'ignorados'}[item['status']]] += 1
        items.append(item)
        resumo['total_reembolsavel'] += item['valor_reembolsavel']
    resumo['total_nao_reembolsavel'] = resumo['total_solicitado'] - resumo['total_reembolsavel']
    return dict(versao_spec='0.2', colaborador=dados['colaborador'], periodo=dados['periodo'], avisos=['VIAGEM_NAO_INFORMADA'], items=items, resumo=resumo)

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal): return f'__DECIMAL__{quant(obj):.2f}__'
        return super().default(obj)

def serializar(d):
    texto = json.dumps(d, ensure_ascii=False, indent=2, cls=DecimalEncoder)
    return re.sub(r'"__DECIMAL__(-?\d+\.\d{2})__"', lambda m: m.group(1), texto) + '\n'
