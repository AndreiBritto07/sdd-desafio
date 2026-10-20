# Relatório — Desafio SDD

**Repositório:** https://github.com/AndreiBritto07/sdd-desafio  
**Data:** 20/10/2026  
**Status:** relato de execução baseado em evidências observadas; cobertura integral e informações pessoais não presumidas.

> Transparência: capturas de terminal e hashes observados comprovam execuções pontuais. Não há sessões exportadas do Claude Code comprovadas. A assistência relatada foi realizada com ChatGPT.

## Delegação

As regras e decisões foram aprovadas pelo responsável. O ChatGPT auxiliou na análise de ambiguidades, redação e revisão da especificação, planejamento, preparação de código e testes e diagnóstico de resultados. O responsável integrou os arquivos, executou os comandos no ambiente local, conferiu saídas e realizou os commits e pushes mostrados nas capturas.

| Atividade | Participação e evidência |
|---|---|
| Identificação e resolução de ambiguidades | Discussões assistidas por IA; decisões consolidadas em `DECISIONS.md` |
| Especificação | Revisões de `spec.md` com decisões aprovadas pelo responsável |
| Arquitetura | Python 3.11, `decimal.Decimal`, `unittest`, `argparse`; `plan.md` e `docs/evidencias/T-001-baseline.md` |
| Implementação | Código em `src/`, commit `2789c78`, integrado pelo responsável com assistência de IA |
| Testes | Suíte em `tests/`, executada localmente; última execução: 16 testes, `OK`, sem skips |
| Envelope 2 | Regras nos documentos, quatro exemplos em `exemplos/envelope/`, commit `b3aaeff` |

**Onde deleguei e me arrependi / onde deveria ter delegado:** requer relato pessoal do responsável; não é inferível de commits.

**Subagentes, skills, MCP e hooks:** não há evidência de uso no material revisado. O trabalho assistido documentado ocorreu com ChatGPT, sem atribuir sessões inexistentes ao Claude Code.

## Descrição — ambiguidade transformada em regra

**Exemplo:** limite de representação em `CC-COMERCIAL`.

**Ambiguidade:** a política apresentava R$ 300,00 para representação; faltava decidir se esse valor poderia ser ampliado por outra política.

**Decisão:** R$ 300,00 é teto máximo absoluto. Uma política pode estabelecer valor menor, nunca maior. Ver `DECISIONS.md` (CONS-001), `spec.md` (RN-019/AC-034) e `tasks.md` (T-041).

**Evidência funcional observada:** no exemplo do Envelope 2, representação de R$ 340,00 resultou em reembolso de R$ 300,00, status `PARCIAL` e motivo `LIMITE_DIARIO`. Isso demonstra o cenário executado, não todas as variações da política.

**Primeira redação literal e commit exato da mudança:** não identificados com segurança; consultar histórico do Git antes de afirmar.

## Discernimento — IA confrontada com evidência

**Caso concreto:** durante o baseline, verificações de sintaxe JSON, chaves repetidas e alguns campos foram inicialmente tratadas como indicativas de validação dos arquivos externos. Essas verificações não demonstravam conformidade semântica integral de RN-019 e RN-020.

**Detecção e correção:** ao revisar a diferença entre inspeção e validação normativa, a evidência `docs/evidencias/T-001-baseline.md` foi ajustada para delimitar o que havia sido efetivamente comprovado. Referências: commits `6aad0c8` e `ac12323`.

**Lição:** uma inspeção parcial não pode ser registrada como teste integral de requisitos. Não atribuir este episódio a uma sessão exportada do Claude Code.

## Diligência — verificações realizadas

- Inspeção dos exemplos JSON e dos arquivos externos do Envelope 2.
- Verificações selecionadas de parsing estrito, chaves repetidas e campos da política/câmbio.
- Uso de `git diff --cached --check` antes de commits; houve alerta de espaços finais em `docs/evidencias/cc-desconhecido.md`, corrigido antes do commit posterior.
- Execução de `python -m src calcular` com os quatro argumentos obrigatórios, incluindo exemplo oficial e centro de custo desconhecido.
- Última execução observada de `python -m unittest discover -s tests -v`: **16 testes executados, 16 aprovados, zero falhas, zero ignorados**.
- Última verificação de `git status --short` mostrada antes da geração temporária do resultado da CLI: sem alterações pendentes. Após gerar `resultado-envelope.json`, o status precisa ser conferido novamente.

**Porcentagem de diffs integralmente revisados:** não medida.

**Limitação:** 16 testes aprovados não comprovam cobertura de AC-001 a AC-036. A matriz de rastreabilidade por teste ainda precisa de conferência específica. Os testes foram preparados com assistência de IA; sua qualidade exige revisão independente das expectativas.

## O Envelope 2

**Alterações:** incorporação de `politica-v4.json`, `cambio.json`, despesas em moedas estrangeiras, regras por centro de custo, hospedagem, representação, conversão e contrato de saída.

**Ordem observada:** consolidação de decisões e especificação, preparação de fixtures, validação global, motor/CLI, testes de saída, exemplos oficiais e documentação. A ordem exata e o diff acumulado devem ser extraídos do histórico Git.

**Evidências:**

- `docs/evidencias/T-001-baseline.md` — baseline e limites da inspeção.
- `tests/test_fixtures.py` — fixtures.
- `tests/test_validacao_global.py` — validações globais.
- `tests/test_motor_integrado.py` — cenários selecionados do motor.
- `tests/test_contrato_saida.py` — saída e formatação monetária.
- `docs/evidencias/cc-desconhecido.md` — cenário de fallback.
- `exemplos/envelope/` — quatro JSONs oficiais versionados.

**Medições não disponíveis:** número de arquivos editados manualmente, tempo decorrido e diff agregado de absorção. Para obter o último, identificar o commit imediatamente anterior à absorção e executar `git diff <commit-base> HEAD --stat`.

**Benefício observado da especificação:** tornar explícitas as decisões de limite comercial, moeda, conversão e arredondamento antes da implementação. Não foi medido tempo economizado.

## Rastreabilidade e commits

| Evidência | Commit abreviado |
|---|---|
| Consolidação pós-Envelope 2 | `cb8cacd` |
| Baseline e complemento | `6aad0c8`, `ac12323` |
| Fixtures | `69fc292` |
| Validação global | `6ee59ee` |
| Testes monetários e hospedagem | `5b8beae` |
| Motor e CLI | `2789c78` |
| Evidência de CC desconhecido e tarefas | `7ea1c00` |
| README e relatório | `0b6bd46` |
| Testes com exemplos oficiais | `b3aaeff` |
| Reserva de diretório de sessões | `01cbc34` |
| Instruções `CLAUDE.md` | `aa39da2` |

Hashes abreviados foram observados no histórico compartilhado; confirmar os completos com `git log --oneline` se exigido.

## Fechamento

**Onde valeu a pena:** um desafio com regras financeiras, múltiplas ambiguidades, exigência de auditoria e mudança contratual relevante.

**Onde talvez não valesse:** um script descartável, sem decisões ambíguas e sem exigência de rastreabilidade.

**O que faria diferente:** iniciar testes e registro de evidências mais cedo e associar cada AC a um teste real.

**Aprendizado:** testes verdes não dispensam revisão da especificação e não comprovam requisitos não exercitados.

## Pendências verificáveis antes da entrega

1. Atualizar `spec.md`, `plan.md` e `tasks.md` para refletir implementação e testes já observados, sem marcar cobertura não comprovada.
2. Conferir a matriz AC-001 a AC-036 versus testes efetivos.
3. Confirmar o status do Git após a geração do JSON temporário e removê-lo se não for artefato de entrega.
4. Completar apenas com fatos pessoais verificáveis os relatos de delegação, arrependimento, ferramentas e revisão de diffs.
5. Registrar sessões **reais** somente se existirem. `.gitkeep` não é evidência de sessão.
