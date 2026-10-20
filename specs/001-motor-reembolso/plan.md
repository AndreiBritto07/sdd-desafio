# Plano técnico — Motor de Cálculo de Reembolso

**Revisão documental:** 20/10/2026 — contrato consolidado pós-Envelope 2  
**Base normativa:** `spec.md` v0.2, `DECISIONS.md` e `tasks.md` T-001 a T-047.  
**Estado:** planejamento; implementação, aprovação externa e testes executados não presumidos.

## 1. Objetivo e limites

Implementar uma CLI determinística que processe um colaborador por lote, valide entrada e arquivos externos, converta valores para BRL, aplique regras de elegibilidade, nota fiscal e limites, e produza resultado auditável. A especificação prevalece sobre este plano em caso de divergência; registrar a divergência antes de codificar. Não reabrir decisões consolidadas silenciosamente.

## 2. Contrato da CLI (CONS-008; RN-017; AC-017)

```bash
calcular --input entrada.json --output resultado.json --politica politica-v4.json --cambio cambio.json
```

Os quatro argumentos são obrigatórios. Não há descoberta automática de política/câmbio, defaults de caminhos ou valores embutidos. O comando de execução real (script, módulo ou binário) será documentado depois de confirmar a stack. Saída 0 para lote processado; 2 para falhas globais de contrato/entrada/política/câmbio; 3 para I/O da entrada principal ou escrita. Nunca publicar JSON financeiro parcial em falha global. Logs não integram o JSON.

## 3. Descoberta obrigatória antes de codificar (T-001)

1. Inspecionar a árvore real do fork, instruções `CLAUDE.md`, ferramentas e dependências.
2. Obter os arquivos originais `politica-v4.json` e `cambio.json` do Envelope 2, registrar os caminhos, nomes de campos, tipos, estrutura de coleções e exemplos válidos/inválidos. **Não presumir campos não inspecionados.**
3. Identificar fixtures e exemplo original de 14 despesas; não usar resultado antigo como gabarito da política v4.
4. Executar testes preexistentes, se houver, e registrar comando, data e resultado. Se não houver suíte, registrar sua ausência.
5. Escolher stack compatível com parser que preserve lexemas numéricos e suporte decimal exato; registrar escolha técnica sem mudar regras de negócio.

**Saída da T-001:** inventário de arquivos, schemas observados, stack, comando de execução e estado-base reproduzível.

## 4. Arquitetura lógica proposta

- **CLI / I/O:** argumentos obrigatórios, leitura, escrita e códigos de saída.
- **Parser JSON estrito:** chaves repetidas, tipos e lexemas numéricos preservados.
- **Validação global:** envelope, colaborador, competência e período.
- **Validação de item:** campos obrigatórios, datas, ID, moeda e valor original.
- **Leitores externos:** validação integral da política e do câmbio segundo os schemas reais.
- **Identidade e duplicidade:** IDs gerados, colisões, comparação normalizada e conteúdo canônico.
- **Cálculo financeiro:** cotação da data/anterior, decimal exato, half-up por item, centavos inteiros, limites e NF.
- **Saída / reconciliação:** status, motivos ordenados, avisos, quatro totais, invariantes e serialização monetária com duas casas.

Os nomes acima são responsabilidades lógicas, não diretórios ou módulos já existentes. Definir arquivos concretos após T-001.

## 5. Ordem de implementação por dependências

| Fase | Tarefas | Resultado verificável |
|---|---|---|
| 0. Baseline | T-001 | Schemas originais e comandos reais inspecionados |
| 1. Fundamentos | T-002, T-036, T-003 a T-006 | Fixtures válidas, decimal exato e erros globais |
| 2. Dados externos | T-033, T-035, T-034 | Política/câmbio validados e fallback correto |
| 3. Despesas e IDs | T-037, T-007 a T-013, T-016 a T-019 | Validação individual e duplicidade determinística |
| 4. Conversão | T-038, T-039, T-014 | Seleção cambial, half-up e overflow por item |
| 5. Regras | T-015, T-017, T-020 a T-022, T-040 a T-042 | Limites, competência, hospedagem, representação e NF |
| 6. Resultado | T-023 a T-026, T-043, T-044 | Status, motivos, totais e invariantes |
| 7. CLI | T-027, T-028 | Quatro argumentos e códigos 0/2/3 testados |
| 8. Integração e entrega | T-029 a T-032, T-045 a T-047 | Regressão, README, rastreabilidade e evidências |

A ordem é indicativa; respeitar dependências explícitas de `tasks.md` e registrar qualquer reorganização sem renumerar tarefas.

## 6. Contratos de erro (CONS-009)

- **Global:** `erro.codigo` = `JSON_INVALIDO`, `ENTRADA_INVALIDA`, `POLITICA_INVALIDA`, `CAMBIO_INVALIDO` ou `ERRO_IO`; sem `items`/`resumo`.
- **Individual:** `items[].motivos` pode conter `DADO_INVALIDO` para estrutura/ID ou `ENTRADA_INVALIDA` para valor, moeda e capacidade de conversão; item permanece, lote prossegue.
- **Exemplos de regressão:** colaborador sem ID → global; `valor: 10.501` → individual monetário; data inexistente de despesa → individual estrutural; período global inválido → global.

Não criar novos aliases de motivos. Precedência e base dos totais seguem RN-015/016/026.

## 7. Estratégia de testes e rastreabilidade

Criar testes unitários para parsers, normalização, valores, limites e deduplicação; integração para CLI/arquivos externos; regressão para fixture original e Envelope 2; propriedades/invariantes para contagens e totais. Cobrir limites inclusivos/exclusivos, moedas sem cotação, câmbio futuro, cotação duplicada, falhas globais e continuidade de itens.

A matriz executável deve registrar para cada **AC-001 a AC-036**: `AC | RN | T | arquivo::teste | comando | resultado | evidência/commit`. Preencher caminhos e resultados apenas após criar e executar testes. Até lá: **NÃO EXECUTADO**. T-030 e T-045 fecham mapeamento; T-047 executa e documenta a suíte completa.

## 8. Evidências e commits

Para cada tarefa: alteração focada, testes relacionados, comando e saída registrados, vínculo RN/AC/T, commit identificável. Registrar sessões e decisões técnicas em `docs/sessions/` conforme exigências do desafio e produzir `docs/RELATORIO.md` com intervenções humanas, verificações, falhas e limitações. Não atribuir aprovação formal ao avaliador.

## 9. Riscos e mitigação

| Risco | Mitigação |
|---|---|
| Schema externo presumido | Bloquear leitores até T-001 inspecionar JSONs originais |
| Parser perde precisão/lexema | Decimal exato e testes para científico, casas e zeros finais |
| Regras antigas reaparecem | Regressão pós-Envelope 2 e DECISIONS como histórico de substituições |
| Código global confundido com item | Testes distintos para `erro.codigo` e `items[].motivos` |
| Totais não reconciliam | Invariantes RN-018 e bases RN-016/026 |
| Testes declarados sem execução | Registrar status NÃO EXECUTADO até evidência real |

## 10. Critérios para iniciar implementação

- [x] Contrato dos quatro argumentos definido documentalmente.
- [x] Escopo dos erros esclarecido documentalmente.
- [ ] T-001 concluída com schemas e stack verificados.
- [ ] Fixtures válidas criadas a partir dos schemas inspecionados.
- [ ] Testes iniciais executados e resultados registrados.

Este plano não equivale à conclusão das tarefas nem à aprovação da especificação.
