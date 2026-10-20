# Plano de execução: motor de reembolso

**Versão:** 0.2 · **Data:** 2026-10-20
**Base:** `spec.md` v0.2 e `DECISIONS.md` v0.2, ambos propostos.
**Backlog:** `tasks.md` (T-001 a T-033).

## Objetivo

Transformar a especificação em uma implementação determinística, testável e rastreável, sem assumir requisitos não aprovados.

## Premissas

- `spec.md` e `DECISIONS.md` são propostas. A aprovação formal é pré-requisito para dar o plano como concluído.
- A correção 69 bloqueia apenas a competência ausente ou inválida e as datas inexistentes em `periodo` (parte de T-015). A comparação inclusiva (T-015) e a inversão de datas válidas (T-014) já estão decididas.
- Linguagem, estrutura de código, localização dos testes e comandos reais devem ser confirmados inspecionando o repositório. Não presumir caminhos nem tecnologias.
- Nenhum teste é marcado como aprovado sem execução registrada.
- O repositório pode conter apenas documentação, exemplos e templates. Verificar antes de planejar a implementação.

## Fases

### Fase 1: Fechar decisões

1. Decidir a correção 69 (bloqueio da parte de T-015 que trata competência ausente ou inválida).
2. Aprovar ou ajustar as correções 70 a 75.
3. Receber o requisito do Dia 2 e analisar o impacto.
4. Confirmar a versão de `spec.md` que será submetida à aprovação.

**Saída:** decisões fechadas, pendências explícitas e baseline de requisitos.

### Fase 2: Inspecionar o repositório

1. Examinar a árvore de arquivos, `CLAUDE.md`, linguagem, dependências e comandos existentes.
2. Verificar se existem implementação do motor, CLI, testes e dados de exemplo (`exemplos/`). Se não existirem, registrar.
3. Executar a suíte existente, se houver, sem alterações, e registrar o resultado (T-001).
4. Comparar o estado atual com a spec e listar lacunas e conflitos.

**Saída:** relatório de estado, comandos reproduzíveis e lista de arquivos a alterar.

### Fase 3: Contrato de entrada

Cobre T-002 a T-007.

1. Parser JSON estrito, com chaves repetidas (T-003).
2. Envelope e colaborador, com `ENTRADA_INVALIDA` (T-004).
3. Chaves exatas, campos extras e booleano (T-005).
4. Validação estrutural de despesas, com erros em ordem fixa (T-006).
5. Despesa inválida mantida em `items` e fora do resumo (T-007).

**Saída:** contrato de entrada com testes unitários.

### Fase 4: Identificadores

Cobre T-008 a T-010.

1. Geração de ID ausente, com índice original (T-008).
2. Colisões de IDs gerados, com sufixos (T-009).
3. ID repetido como motivo `ID_REPETIDO` e normalização de comparação (T-010).

**Saída:** IDs determinísticos com testes de colisão e repetição.

### Fase 5: Cálculo e precedência

Cobre T-011 a T-023.

1. Arredondamento half-up e valores zero ou negativos (T-011, T-013).
2. Normalização de categoria (T-012).
3. Período: inversão (T-014) e competência inclusiva (T-015, sujeita à correção 69 nos casos indicados).
4. Deduplicação por conteúdo e canônico (T-016, T-017).
5. Precedência de motivos (T-018), nota fiscal (T-019), dias civis e categoria (T-020).
6. Limites diários (T-021), viagem (T-022) e diárias de hospedagem (T-023).

**Saída:** cálculo coberto por testes unitários e casos de fronteira.

### Fase 6: Saída e totais

Cobre T-024 a T-027.

1. Valores preservados em itens não elegíveis (T-024).
2. Resumo e contagens (T-025).
3. Totais financeiros e invariantes (T-026, sujeita às correções 70 e 75).
4. Saída estável com `versao_spec`, `periodo` e ordem (T-027).

**Saída:** resumo que reconcilia com os itens e satisfaz os invariantes.

### Fase 7: CLI e erros operacionais

Cobre T-028 e T-029.

1. Contrato `calcular --input --output`, com códigos `0`, `2` e `3`.
2. Logs fora do JSON de resultado.
3. Arquivo inexistente, leitura e escrita, sem saída parcial em falha de lote ou de I/O.
4. Determinismo: mesma entrada produz a mesma saída financeira (T-028).

**Saída:** testes de integração e de CLI reproduzíveis.

### Fase 8: Verificação, rastreabilidade e entrega

Cobre T-030 a T-033.

1. Transformar o exemplo de 14 itens em regressão e comparar com a execução real (T-030).
2. Confirmar a matriz AC → tarefa → teste, inclusive a seção 11 da spec (T-031).
3. Documentar uso e executar os comandos em ambiente limpo (T-032).
4. Rodar formatter, linter e análise estática, se existirem. Executar a suíte completa e registrar resultados (T-033).
5. Revisar o diff para detectar alterações fora do escopo ou requisitos inventados.
6. Atualizar `spec.md`, `DECISIONS.md`, `plan.md` e `tasks.md` para refletir o estado real.
7. Submeter por commit e branch conforme o fluxo do repositório, após confirmação.
8. Informar testes executados, resultados, limitações e pendências.

**Saída:** mudança revisável e rastreável, pronta para aprovação.

## Critérios de conclusão

- [ ] Correção 69 decidida. Correções 70 a 75 aprovadas ou ajustadas.
- [ ] Repositório e comandos inspecionados.
- [ ] Erros de lote e de item seguem o contrato.
- [ ] IDs e duplicatas determinísticos.
- [ ] Totais e invariantes respeitados.
- [ ] Cada AC ligado a um teste identificável.
- [ ] Suíte executada, com resultados e falhas registrados.
- [ ] Exemplo recalculado por execução.
- [ ] Matriz de rastreabilidade revisada.
- [ ] Documentos e código revisados e prontos para aprovação.

## Riscos e mitigação

| Risco | Mitigação |
|---|---|
| Dia 2 muda a política | Manter pendente e revisar a spec antes da aprovação |
| Competência ambígua | Não implementar interpretação definitiva antes da correção 69 (parte de T-015) |
| Parser não detecta chaves repetidas | Validar chaves antes de converter em mapa |
| Resumo diverge dos itens | Testar invariantes e recalcular o exemplo por execução |
| Testes não correspondem aos ACs | Usar os IDs reais da suíte e a matriz; não inventar nomes ou caminhos |
| Especificação continua proposta | Manter o status explícito até a aprovação |
| Correções 69 a 75 não aprovadas | Não implementar antes da aprovação: casos da 69 em T-015; T-006 (73 e 74); T-013, T-016 e T-017 (72); T-018 (71); T-024 e T-026 (75 e 70) |