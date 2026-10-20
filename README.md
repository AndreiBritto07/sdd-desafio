# Motor de Cálculo de Reembolso — Desafio SDD

Implementação em Python 3.11 de um motor de reembolso orientado por especificação, com processamento de despesas em JSON, política externa por centro de custo e conversão de moedas por cotações históricas. O projeto incorpora as alterações do **Envelope 2**.

**Repositório:** https://github.com/AndreiBritto07/sdd-desafio

## Requisitos

- Python 3.11, usando apenas a biblioteca padrão (`decimal`, `json`, `argparse`, `unittest` e demais módulos nativos).
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

Os exemplos em `exemplos/envelope/` precisam estar presentes localmente. Confirme antes da entrega que os arquivos JSON oficiais necessários estão versionados; os comandos acima dependem deles.

## Como testar

```bash
python -m unittest discover -s tests -v
```

**Evidência informada em 20/10/2026:** `Ran 84 tests in 3.665s` seguido de `OK`, após remoção de arquivo de testes duplicado. Isso comprova a execução reportada da suíte naquele ambiente, **não** a cobertura integral de todos os requisitos ou cenários de erro. A contagem pode depender de arquivos de exemplo gerados localmente.

## Contrato e comportamentos

O contrato normativo está em [`specs/001-motor-reembolso/spec.md`](specs/001-motor-reembolso/spec.md), complementado por [`DECISIONS.md`](specs/001-motor-reembolso/DECISIONS.md). Entre as regras previstas estão:

- Validação do envelope e dos campos obrigatórios do colaborador.
- Tratamento individual de despesas inválidas sem necessariamente rejeitar todo o lote.
- Limites por categoria e centro de custo, incluindo fallback para a política padrão quando aplicável.
- Conversão para BRL com cotação anterior disponível, quando necessário.
- Aplicação de limites e exigência de nota fiscal conforme a política.
- Teto diário de R$ 300,00 para representação em `CC-COMERCIAL`, inclusive quando há limite mensal aplicável.
- Saída JSON com itens, motivos, avisos e resumo financeiro.

A implementação e os testes devem ser consultados para verificar quais cenários estão efetivamente cobertos. **Valores exibidos por `python -m json.tool` podem aparecer com uma casa decimal**; portanto, a inspeção visual desse comando não demonstra preservação de duas casas no arquivo original.

## Organização

| Caminho | Finalidade |
|---|---|
| `src/` | Código Python do motor e entrada da CLI |
| `tests/` | Testes automatizados e fixtures |
| `specs/001-motor-reembolso/spec.md` | Requisitos e critérios de aceite |
| `specs/001-motor-reembolso/plan.md` | Plano técnico |
| `specs/001-motor-reembolso/tasks.md` | Tarefas e rastreabilidade |
| `specs/001-motor-reembolso/DECISIONS.md` | Histórico de decisões |
| `docs/MATRIZ_RASTREABILIDADE_AC.md` | Matriz de critérios de aceite e referências a testes |
| `docs/evidencias/` | Evidências de inspeção e execução |
| `docs/sessions/` | Exportações de sessões, quando disponíveis |
| `docs/RELATORIO.md` | Relatório da execução e limitações |

## Evidências e limites

Foram relatadas execuções da CLI com exemplos do Envelope 2 e um cenário de centro de custo desconhecido, além da execução de 84 testes com resultado `OK`. O commit de consolidação `3a4e8e2` foi enviado à branch `main`. Os testes incluem a verificação do teto diário para representação comercial e a simulação de falha numérica individual; **esta última não demonstra um overflow espontâneo com uma cotação extrema**.

Os resultados não substituem uma auditoria completa de conformidade com os dois envelopes. Não há comprovação de exports reais de sessões do Claude Code no material analisado; não devem ser presumidos nem fabricados.

Consulte [`docs/RELATORIO.md`](docs/RELATORIO.md) e [`docs/MATRIZ_RASTREABILIDADE_AC.md`](docs/MATRIZ_RASTREABILIDADE_AC.md) para detalhes de evidências, rastreabilidade e limitações identificadas.
