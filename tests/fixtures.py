"""Fixtures reutilizáveis da T-002; sem implementação de regras de negócio."""
from copy import deepcopy
from decimal import Decimal
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]


def colaborador(**alteracoes):
    dados = {"id": "COL-001", "nome": "Colaborador Exemplo", "centro_custo": "CC-ADM"}
    dados.update(alteracoes)
    return dados


def periodo(**alteracoes):
    dados = {"competencia": "2026-07", "inicio": "2026-07-13", "fim": "2026-07-13"}
    dados.update(alteracoes)
    return dados


def despesa(**alteracoes):
    dados = {
        "id": "DESP-001", "data": "2026-07-13", "categoria": "alimentacao",
        "descricao": "Refeicao", "fornecedor": "Restaurante Exemplo",
        "valor": Decimal("40.00"), "tem_nota_fiscal": True,
    }
    dados.update(alteracoes)
    return dados


def entrada(*, colaborador_dados=None, periodo_dados=None, despesas=None):
    return {
        "colaborador": deepcopy(colaborador_dados if colaborador_dados is not None else colaborador()),
        "periodo": deepcopy(periodo_dados if periodo_dados is not None else periodo()),
        "despesas": deepcopy(despesas if despesas is not None else [despesa()]),
    }


def ler_json_original(caminho):
    """Lê um arquivo original; não infere schema nem aprova validade semântica."""
    def pares_unicos(pares):
        obj = {}
        for chave, valor in pares:
            if chave in obj:
                raise ValueError(f"Chave JSON repetida: {chave}")
            obj[chave] = valor
        return obj

    def constante_invalida(valor):
        raise ValueError(f"Constante JSON invalida: {valor}")

    return json.loads(
        Path(caminho).read_text(encoding="utf-8"),
        parse_float=Decimal,
        parse_int=Decimal,
        object_pairs_hook=pares_unicos,
        parse_constant=constante_invalida,
    )


def politica():
    return deepcopy(ler_json_original(RAIZ / "exemplos/envelope/politica-v4.json"))


def cambio():
    return deepcopy(ler_json_original(RAIZ / "exemplos/envelope/cambio.json"))
