# Relatório — Desafio SDD

**Repositório:** https://github.com/AndreiBritto07/sdd-desafio  
**Data:** 20/10/2026  
**Status:** relatório baseado nas evidências disponíveis; campos de experiência pessoal e histórico ainda requerem confirmação.

> Critério de transparência: resultados de terminal e hashes apresentados são evidências observadas; interpretações sobre qualidade, cobertura e autoria são identificadas como tais. Não foram presumidas sessões exportadas do Claude Code.

## Delegação

A definição das regras e a aprovação de decisões ficaram com o responsável pelo projeto. Houve assistência de IA na análise de ambiguidades, revisão documental, proposta de arquitetura e preparação de trechos de implementação e testes. A execução local, inspeção dos resultados e realização dos commits foram conduzidas pelo responsável, conforme capturas de terminal compartilhadas.

| Atividade | Divisão observável | Evidência |
|---|---|---|
| Identificar ambiguidades | Análise assistida por IA; decisões discutidas com o responsável | `spec.md` e `DECISIONS.md` |
| Decidir ambiguidades | Responsável aprovou escolhas explícitas | `DECISIONS.md` |
| Especificar | Iterações assistidas por IA e revisão do responsável | `spec.md` |
| Arquitetura | Stack Python 3.11 aprovada pelo responsável | `plan.md`; `docs/evidencias/T-001-baseline.md` |
| Implementar | Código integrado e versionado pelo responsável, com assistência de IA | `src/`; commit `2789c78` |
| Testar | Suíte executada localmente pelo responsável | `tests/`; saída de `unittest` |
| Envelope 2 | Decisões incorporadas aos documentos e cenários executados | `spec.md`, `DECISIONS.md`, `tasks.md`, `docs/evidencias/` |

**Onde deleguei e me arrependi / onde deveria ter delegado:** não é possível concluir apenas pelos arquivos e capturas; preencher com um episódio real antes da entrega.

**Subagentes, skills, MCP e hooks:** não há evidência suficiente para afirmar uso ou ausência. Confirmar com o responsável.

## Descrição — transformar ambiguidade em regra verificável

**Exemplo escolhido: limite de representação em `CC-COMERCIAL`.**

**Ambiguidade identificada:** a política externa contém limite de R$ 300,00 para representação, mas era necessário explicitar se uma política futura poderia ultrapassar esse valor.

**Decisão final do responsável:** R$ 300,00 é **teto máximo**; a política externa pode estabelecer limite inferior, mas não superior. A regra deve constar em `spec.md` e `DECISIONS.md` e ser refletida na implementação e em testes.

**Evidência de execução:** no processamento do exemplo do Envelope 2, um item de representação de R$ 340,00 foi apresentado como `PARCIAL`, com R$ 300,00 reembolsáveis e motivo `LIMITE_DIARIO`.

**Primeira redação literal e hash específico da alteração:** a recuperar no histórico de commits ou sessões. Não foi inventada uma versão inicial.

## Discernimento — proposta de IA confrontada com evidências

**Caso documentável: alcance de validações do baseline.** Durante a inspeção dos arquivos externos, foram executadas verificações de sintaxe, chaves JSON repetidas e verificações selecionadas de campos. Esses resultados **não comprovavam** conformidade semântica integral com RN-019 e RN-020. O relatório `docs/evidencias/T-001-baseline.md` foi ajustado para distinguir a inspeção concluída da validação normativa ainda não demonstrada.

**Por que importou:** declarar uma validação integral sem testes correspondentes teria criado rastreabilidade falsa. A correção preservou a limitação e direcionou a validação completa às tarefas de implementação.

**Evidência:** `docs/evidencias/T-001-baseline.md`, commits `6aad0c8` e `ac12323` (confirmar hashes completos via `git log`).

**Sessão exportada correspondente:** ainda não identificada. Sem exportação verificável, não atribuir esse episódio a uma sessão específica do Claude Code.

## Diligência — verificações efetivamente observadas

Foram observadas as seguintes verificações:

- Leitura e inspeção de arquivos JSON de exemplo e do Envelope 2.
- Parsing estrito selecionado para detectar chaves repetidas e constantes JSON inválidas.
- Execução de verificações parciais de política e câmbio, sem alegar conformidade semântica integral.
- `git diff --cached --check` antes de commits; em uma execução, o comando apontou espaços ao final das linhas 3 e 4 de `docs/evidencias/cc-desconhecido.md`.
- Execução de `python -m unittest discover -s tests -v`: **16 testes, resultado `OK`**.
- Execução da CLI com o exemplo do Envelope 2 e com centro de custo desconhecido.

**Porcentagem de diffs lidos integralmente:** não medida; não estimar sem evidência.

**Limitações:** os testes aprovados demonstram os cenários implementados na suíte, não cobertura integral da spec. A execução com centro de custo desconhecido apresentou fallback para a política padrão e resumo com `totais_completos: true`; trata-se de evidência de um caso, não de todos os centros de custo.

## O Envelope 2

**Alterações tratadas:** política externa `politica-v4.json`, cotações `cambio.json`, despesas em outras moedas, regras por centro de custo, representação, hospedagem e contrato de saída.

**Ordem observada em alto nível:** especificação e decisões foram consolidadas antes da implementação registrada nos commits posteriores. Para afirmar a ordem exata de todas as alterações, consultar `git log --oneline --all` e os arquivos de sessões.

**Evidências técnicas:**

- `docs/evidencias/T-001-baseline.md`: inspeção inicial, limitações e stack escolhida.
- `tests/test_fixtures.py`: fixtures reutilizáveis.
- `tests/test_validacao_global.py`: cenários de envelope e colaborador.
- `tests/test_motor_integrado.py`: cenários selecionados do motor.
- `tests/test_contrato_saida.py`: contrato e serialização.
- `docs/evidencias/cc-desconhecido.md`: cenário de fallback, conforme registro local.

**Medições ainda necessárias:** quantidade de arquivos editados manualmente, tempo decorrido e diff agregado de absorção. Para obter o diff sem inventar números, identificar o commit anterior ao Envelope 2 e executar:

```bash
git diff <commit-anterior-ao-envelope> HEAD --stat
```

**O que a especificação poupou:** forneceu um local explícito para registrar escolhas antes de codificar, especialmente as regras de centro de custo, moeda e arredondamento. Esta é uma avaliação do processo, não uma medição de horas economizadas.

## Rastreabilidade e commits observados

| Evidência | Referência |
|---|---|
| Consolidação documental após Envelope 2 | `cb8cacd` |
| Baseline técnico | `6aad0c8` |
| Complemento do parecer de inspeção | `ac12323` |
| Fixtures | `69fc292` |
| Validação global | `6ee59ee` |
| Testes de contrato de saída | `5b8beae` |
| Motor e CLI | `2789c78` |
| Atualização documental final observada | `7eafc00` |
| Publicação remota | `git push origin main` concluído na captura de 20/10/2026 |

Os hashes acima são abreviados e devem ser conferidos em `git log --oneline` antes da entrega.

## Fechamento

**Para qual tamanho de projeto valeu a pena:** o processo mostrou utilidade em um desafio com regras financeiras, casos de borda e alteração contratual relevante, nos quais decisões implícitas gerariam comportamentos inconsistentes.

**Para qual não valeria:** em um script descartável e sem regras ambíguas, a documentação completa poderia custar mais que a implementação.

**O que faria diferente:** iniciar os testes e as exportações de sessões mais cedo, mantendo cada evidência associada à tarefa e ao commit correspondente.

**Aprendizado:** testes verdes não dispensam revisão da especificação nem provam cobertura de requisitos que não foram exercitados.

## Pendências antes da entrega

1. Confirmar as informações pessoais sobre delegação, arrependimento e ferramentas utilizadas; não preencher por suposição.
2. Exportar e versionar sessões **reais** em `docs/sessions/`, se disponíveis; não criar sessões fictícias.
3. Corrigir os espaços em branco identificados em `docs/evidencias/cc-desconhecido.md`.
4. Garantir que os quatro JSONs oficiais do Envelope 2 estejam versionados.
5. Conferir os hashes, o status de `tasks.md` e a coerência final com `spec.md`, `plan.md` e `DECISIONS.md`.
