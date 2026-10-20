# Instruções do Projeto — Motor de Reembolso

## Objetivo
Implementar um motor de cálculo de reembolso de despesas, seguindo a abordagem Spec-Driven Development (SDD) e as regras do Envelope 2.

## Tecnologias
- Python 3.11+
- Biblioteca padrão do Python
- `decimal.Decimal` para cálculos financeiros
- `unittest` para testes automatizados

## Fontes de verdade
- `specs/001-motor-reembolso/spec.md`: requisitos e critérios de aceitação.
- `specs/001-motor-reembolso/DECISIONS.md`: decisões e resolução de ambiguidades.
- `specs/001-motor-reembolso/tasks.md`: tarefas e rastreabilidade.
- `specs/001-motor-reembolso/plan.md`: planejamento técnico.

Em caso de divergência, consultar as decisões registradas e manter os documentos sincronizados. Não alterar regras de negócio silenciosamente.

## Estrutura
- `src/`: implementação do motor e da CLI.
- `tests/`: testes automatizados.
- `exemplos/envelope/`: entradas oficiais do Envelope 2.
- `docs/RELATORIO.md`: relatório do desenvolvimento.
- `docs/evidencias/`: evidências verificáveis.
- `docs/sessions/`: espaço reservado para exportações reais de sessões, quando existentes.

## Execução

```bash
python -m src calcular \
  --input exemplos/envelope/despesas-envelope.json \
  --output resultado-envelope.json \
  --politica exemplos/envelope/politica-v4.json \
  --cambio exemplos/envelope/cambio.json
```

## Testes

```bash
python -m unittest discover -s tests -v
```

## Regras de desenvolvimento
1. Implementar de acordo com a especificação vigente.
2. Priorizar consistência com decisões anteriores.
3. Não usar ponto flutuante binário nos cálculos financeiros.
4. Preservar a ordem das despesas e