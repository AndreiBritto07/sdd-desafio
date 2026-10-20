"""Validação global RN-006/RN-014, sem regras financeiras."""
import json
import re
from datetime import date
from decimal import Decimal

class ErroGlobal(ValueError):
    def __init__(self, codigo, mensagem):
        super().__init__(mensagem)
        self.codigo = codigo


def pares_unicos(pares):
    resultado = {}
    for chave, valor in pares:
        if chave in resultado:
            raise ErroGlobal('JSON_INVALIDO', f'Chave JSON repetida: {chave}')
        resultado[chave] = valor
    return resultado


def constante_invalida(valor):
    raise ErroGlobal('JSON_INVALIDO', f'Constante JSON inválida: {valor}')


def carregar_entrada(texto):
    try:
        return json.loads(texto, parse_float=Decimal, parse_int=Decimal,
                          parse_constant=constante_invalida, object_pairs_hook=pares_unicos)
    except (json.JSONDecodeError, UnicodeError) as exc:
        raise ErroGlobal('JSON_INVALIDO', 'JSON principal inválido') from exc


def data_estrita(valor):
    if not isinstance(valor, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', valor):
        raise ValueError('Formato de data inválido')
    data = date.fromisoformat(valor)
    if data.isoformat() != valor:
        raise ValueError('Data inválida')
    return data


def texto_obrigatorio(obj, chave):
    valor = obj.get(chave)
    if not isinstance(valor, str) or not valor.strip():
        raise ErroGlobal('ENTRADA_INVALIDA', f'Campo obrigatório inválido: {chave}')


def validar_envelope(dados):
    if not isinstance(dados, dict):
        raise ErroGlobal('ENTRADA_INVALIDA', 'Raiz deve ser objeto')
    colaborador = dados.get('colaborador')
    periodo = dados.get('periodo')
    despesas = dados.get('despesas')
    if not isinstance(colaborador, dict):
        raise ErroGlobal('ENTRADA_INVALIDA', 'colaborador deve ser objeto')
    for chave in ('id', 'nome', 'centro_custo'):
        texto_obrigatorio(colaborador, chave)
    if not isinstance(periodo, dict):
        raise ErroGlobal('ENTRADA_INVALIDA', 'periodo deve ser objeto')
    if not isinstance(despesas, list):
        raise ErroGlobal('ENTRADA_INVALIDA', 'despesas deve ser lista')
    competencia = periodo.get('competencia')
    if not isinstance(competencia, str) or not re.fullmatch(r'\d{4}-(0[1-9]|1[0-2])', competencia):
        raise ErroGlobal('ENTRADA_INVALIDA', 'Competência inválida')
    try:
        inicio, fim = data_estrita(periodo.get('inicio')), data_estrita(periodo.get('fim'))
    except (ValueError, TypeError) as exc:
        raise ErroGlobal('ENTRADA_INVALIDA', 'Datas globais inválidas') from exc
    if inicio.strftime('%Y-%m') != competencia or fim.strftime('%Y-%m') != competencia:
        raise ErroGlobal('ENTRADA_INVALIDA', 'Datas fora da competência')
    resultado = dict(dados)
    resultado['periodo'] = dict(periodo)
    resultado['periodo']['inicio'] = min(inicio, fim).isoformat()
    resultado['periodo']['fim'] = max(inicio, fim).isoformat()
    return resultado


def falha(exc):
    return {'versao_spec': '0.2', 'erro': {'codigo': exc.codigo, 'mensagem': str(exc)}}
