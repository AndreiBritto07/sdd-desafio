# plans.md — Plano de execução do motor de cálculo de reembolso

**Base:** `spec.md` v0.2 (proposta) e `DECISIONS.md`  
**Status:** planejamento; decisões ainda pendentes de aprovação oficial.  
**Data:** 20/10/2026

## Objetivo

Transformar a especificação proposta em uma implementação determinística, testável e rastreável, sem assumir requisitos ainda não definidos. A execução deve preservar a separação entre erros de lote e erros de item, permitir reconciliar os totais e produzir explicações para cada decisão.

## Premissas e restrições

- `spec.md` v0.2 continua sendo uma proposta, não uma aprovação oficial.
- A mudança de requisito do Dia 2 ainda não foi recebida; revisar regras, testes e documentação afetados quando chegar.
- A correção 69, sobre competência/datas inválidas além da inversão de datas válidas, está em aberto. Não implementar comportamento definitivo para esses casos antes da decisão.
- A estrutura e a linguagem do projeto, a localização dos testes e os comandos reais devem ser confirmados inspecionando o repositório; não presumir caminhos ou tecnologias.
- Não afirmar que testes passaram sem executá-los e registrar o resultado.

## Fases

### Fase 1 — Fechar decisões e estabelecer a baseline

1. Resolver a correção 69.
2. Verificar se existem outras correções não resolvidas no `spec.md` e no `DECISIONS.md`.
3. Receber o requisito do Dia 2 quando disponível e analisar impacto.
4. Confirmar qual versão da especificação será submetida à aprovação oficial.

**Saída:** lista de decisões fechadas, pendências explícitas e baseline de requisitos aprovada para implementação.

### Fase 2 — Inspecionar o repositório

1. Examinar a árvore de arquivos, instruções do projeto, linguagem, dependências e comandos existentes.
2. Localizar a implementação do motor, a CLI, os testes e os dados de exemplo.
3. Executar a suíte existente sem alterações e registrar resultados como baseline.
4. Comparar implementação e testes com `spec.md` e identificar lacunas, conflitos e regressões potenciais.

**Saída:** relatório curto de estado atual, comandos reproduzíveis e lista de arquivos que provavelmente precisarão de mudança.

### Fase 3 — Desenhar contrato e validação

1. Documentar o formato de entrada e os esquemas de sucesso/erro.
2. Implementar parsing JSON que detecte chaves repetidas em qualquer objeto e rejeite o lote com `JSON_INVALIDO` sem resultado financeiro parcial.
3. Validar envelope e campos obrigatórios de `colaborador`; erro causa `ENTRADA_INVALIDA` para o lote inteiro.
4. Validar cada despesa em ordem fixa, registrando todos os erros estruturais de forma determinística.
5. Ignorar campos extras conforme a especificação.
6. Tratar IDs ausentes, inválidos, repetidos e gerados segundo as regras documentadas.

**Saída:** contrato de entrada e saída implementado com testes unitários de validação.

### Fase 4 — Implementar cálculo e precedência

1. Normalizar categoria e valores conforme as regras.
2. Validar período e competência somente conforme decisões fechadas; manter bloqueada a parte da correção 69 ainda não decidida.
3. Identificar duplicatas por ID antes da deduplicação por conteúdo.
4. Para conteúdo, comparar data e categoria normalizadas, fornecedor/descrição com NFC, trim ASCII externo e comparação sem diferença de caixa, e valor arredondado a duas casas; ignorar indicador fiscal e campos extras.
5. Aplicar motivos, avisos, limites e precedência em uma ordem explícita.
6. Garantir que itens inválidos permaneçam em `items`, mas não entrem em `total_itens`, contagens nem totais financeiros.
7. Garantir invariantes dos totais e que nenhum reembolso seja negativo ou superior ao valor solicitado.

**Saída:** cálculo de negócio coberto por testes unitários e casos de fronteira.

### Fase 5 — CLI e erros operacionais

1. Implementar ou ajustar `calcular --input <arquivo> --output <arquivo>` conforme a CLI existente.
2. Confirmar códigos de saída: `0` sucesso, `2` entrada/lote inválido, `3` erro de I/O.
3. Manter logs fora do JSON de resultado.
4. Verificar comportamento de arquivos inexistentes, leitura/escrita e ausência de saída parcial em falha de lote.
5. Confirmar determinismo: mesma entrada produz a mesma saída financeira.

**Saída:** testes de integração/CLI com comandos reproduzíveis.

### Fase 6 — Testes, exemplos e rastreabilidade

1. Associar cada AC a um identificador de teste real, usando a estrutura encontrada no repositório.
2. Criar casos automatizados para AC-001 a AC-021 e os casos de borda aplicáveis.
3. Cobrir explicitamente chaves JSON repetidas, colaborador incompleto, IDs gerados/colididos/inválidos/repetidos, duplicatas, arredondamento, datas invertidas e invariantes de totais.
4. Recalcular exemplos de entrada/saída por execução real, comparar com os valores documentados e corrigir discrepâncias.
5. Atualizar a matriz AMB → RN → AC → teste; registrar “sem relação direta” quando aplicável.
6. Marcar testes como validados somente após execução aprovada.

**Saída:** suíte executada, resultados documentados e rastreabilidade completa.

### Fase 7 — Revisão e entrega

1. Rodar formatter, linter, análise estática e suíte de testes disponíveis no projeto.
2. Revisar diff para detectar alterações fora de escopo, requisitos inventados ou mudanças incompatíveis.
3. Atualizar `spec.md`, `DECISIONS.md`, `plans.md` e `task.md` para refletir o estado real.
4. Submeter as alterações por commit/branch/pull request conforme o fluxo do repositório, após confirmação do usuário quando necessária.
5. Informar explicitamente testes executados, resultados, limitações e pendências.

**Saída:** mudança revisável e rastreável, pronta para aprovação.

## Critérios de conclusão

- [ ] Correção 69 decidida e todas as demais pendências identificadas.
- [ ] Repositório e comandos reais inspecionados.
- [ ] Erros de lote e erros de item seguem o contrato.
- [ ] IDs e duplicatas são determinísticos conforme a especificação.
- [ ] Cálculos e resumos respeitam todas as invariantes.
- [ ] Cada critério de aceite aplicável está ligado a um teste automatizado identificável.
- [ ] Suíte executada; resultados e falhas registrados sem alegações não verificadas.
- [ ] Exemplos recalculados por execução.
- [ ] Matriz de rastreabilidade revisada.
- [ ] Mudanças documentais e de código revisadas e prontas para aprovação.

## Riscos e mitigação

| Risco | Mitigação |
|---|---|
| Requisito do Dia 2 muda a política | Manter pendente e revisar impacto antes de aprovar a especificação final. |
| Comportamento de período fica ambíguo | Não implementar interpretação definitiva para a correção 69 antes da decisão. |
| Parser JSON não detecta chaves repetidas | Escolher ou implementar parsing que preserve e valide chaves antes de convertê-las em mapa/dicionário. |
| Resumo diverge dos itens | Testar invariantes e recalcular exemplos usando a implementação. |
| Testes não correspondem aos ACs | Usar IDs reais e matriz de rastreabilidade; não inventar nomes/caminhos antes de inspecionar o repositório. |
| Especificação continua proposta | Manter status explícito até aprovação oficial. |
