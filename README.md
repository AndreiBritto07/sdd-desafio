# Motor de Cálculo de Reembolso — Desafio SDD

Implementação em Python 3.11 de um motor de reembolso orientado por especificação, com processamento de despesas em JSON, política externa por centro de custo e conversão de moedas por cotações históricas. O projeto incorpora as alterações do **Envelope 2**.

**Repositório:** https://github.com/AndreiBritto07/sdd-desafio

## Requisitos

- Python 3.11 (biblioteca padrão apenas: `decimal`, `json`, `argparse`, `unittest` e demais módulos nativos).
- Executar os comandos a partir da raiz do repositório.

## Como executar

O comando exige explicitamente os quatro caminhos: entrada, saída, política e câmbio.

```bash
python -m src calcular \
  --input exemplos/envelope/despesas-envelope.json \
  --output resultado-envelope.json \
  --politica exemplos/envelope/politica-v4.json \
  --cambio exemplos/envelope/cambio.json
```

Exemplo de centro de custo desconhecido:

```bash
python -m src calcular \
  --input exemplos/envelope/despesas-envelope-cc-desconhecido.json \
  --output resultado-cc-desconhecido.json \
  --politica exemplos/envelope/politica-v4.json \
  --cambio exemplos/envelope/cambio.json
```

Para visualizar a saída formatada:

```bash
python -m json.tool resultado-envelope.json
```

Os exemplos em `exemplos/envelope/` precisam estar presentes localmente. Se ainda não estiverem versionados, adicione os quatro arquivos JSON oficiais do Envelope 2 antes da entrega.

## Como testar

```bash
python -m unittest discover -s tests -v
```

**Evidência observada em 20/10/2026:** 16 testes executados, todos com resultado `OK`. A suíte cobre fixtures, validação global, casos selecionados do motor, contrato da CLI e serialização. Isso **não** comprova cobertura integral de todos os requisitos ou cenários de erro.

## Contrato e comportamentos

O contrato normativo está em [`specs/001-motor-reembolso/spec.md`](specs/001-motor-reembolso/spec.md), complementado por [`DECISIONS.md`](specs/001-motor-reembolso/DECISIONS.md). Entre as regras previstas estão:

- Validação do envelope e dos campos obrigatórios do colaborador.
- Tratamento individual de despesas inválidas sem necessariamente rejeitar todo o lote.
- Limites por categoria e centro de custo, incluindo fallback para a política padrão quando aplicável.
- Conversão para BRL com cotação anterior disponível, quando necessário.
- Aplicação de limites e exigência de nota fiscal conforme a política.
- Teto máximo de R$ 300,00 para representação em `CC-COMERCIAL`.
- Saída JSON com itens, motivos, avisos e resumo financeiro.

A implementação e os testes devem ser consultados para verificar quais cenários estão efetivamente cobertos. **Valores exibidos por `python -m json.tool` podem aparecer com uma casa decimal**, portanto a inspeção visual desse comando não demonstra preservação de duas casas no arquivo original.

## Organização

| Caminho | Finalidade |
|---|---|
| `src/` | Código Python do motor e entrada da CLI |
| `tests/` | Testes automatizados e fixtures |
| `specs/001-motor-reembolso/spec.md` | Requisitos e critérios de aceite |
| `specs/001-motor-reembolso/plan.md` | Plano técnico |
| `specs/001-motor-reembolso/tasks.md` | Tarefas e rastreabilidade |
| `specs/001-motor-reembolso/DECISIONS.md` | Histórico de decisões |
| `docs/evidencias/` | Evidências de inspeção e execução |
| `docs/sessions/` | Exportações das sessões, quando disponíveis |
| `docs/RELATORIO.md` | Relatório final |

## Evidências e limites

Foram observadas execuções da CLI com os exemplos do Envelope 2 e um cenário de centro de custo desconhecido, além da suíte de 16 testes. Os resultados de execução não substituem auditoria de conformidade completa da especificação.

Consulte [`docs/RELATORIO.md`](docs/RELATORIO.md) para rastreabilidade, decisões e limitações identificadas.
