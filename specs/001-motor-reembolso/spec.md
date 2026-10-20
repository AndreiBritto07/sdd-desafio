# Spec — Motor de Cálculo de Reembolso

**Versão:** 0.2 · **Status:** proposta, pendente de aprovação oficial · **Data:** 20/10/2026

Este documento consolida as correções decididas durante a revisão, mas essas escolhas continuam sendo propostas e não equivalem a aprovação oficial. A versão 0.1 é preservada no histórico do repositório. A mudança do Dia 2 ainda não foi recebida; regras relacionadas deverão ser revisadas quando o requisito chegar. A correção 69 (tratamento de competência/datas inválidas além da inversão) permanece em aberto e não é presumida nesta versão.

## 1. Problema
O financeiro confere despesas manualmente contra uma política ambígua, gerando demora e decisões inconsistentes.

## 2. Objetivo
Calcular o reembolso de um colaborador em um período, explicando cada decisão e permitindo reconciliar todos os totais.

## 3. Fora de escopo
Não efetua pagamentos, não valida autenticidade de notas, não consulta sistemas externos, não autentica usuários, não mantém histórico entre execuções, não converte moedas, não oferece interface gráfica, não processa múltiplos colaboradores no mesmo lote, não reconcilia estornos, não infere viagens ou quantidade de diárias de texto. Sem comprovação estruturada de viagem, nenhum limite recebe os 50% adicionais; isso é uma limitação assumida, não remoção silenciosa da política.

## 4. Entrada e saída
### Entrada
Mantém exatamente o formato do exemplo original.

| Campo | Tipo | Obrigatório / significado |
|---|---|---|
| colaborador | objeto | Sim |
| colaborador.id, nome, centro_custo | texto não vazio | Sim, identificação; preservar |
| periodo | objeto | Sim |
| periodo.competencia | texto YYYY-MM | Sim, mês válido |
| periodo.inicio, fim | data YYYY-MM-DD | Sim, datas reais inclusivas no mês de competência |
| despesas | lista | Sim, pode estar vazia |
| despesas[].id | texto | Opcional; se ausente, gerar ID determinístico; se presente, deve ser texto não vazio válido |
| despesas[].data | data YYYY-MM-DD | Sim |
| despesas[].categoria | texto | Sim; normalização definida em RN-011 |
| despesas[].descricao, fornecedor | texto não vazio | Sim; sem normalização |
| despesas[].valor | número decimal finito | Sim; booleano não é número, não aceitar texto numérico |
| despesas[].tem_nota_fiscal | booleano | Sim; somente true ou false |

Strings obrigatórias contendo somente espaços são inválidas. Chaves são exatas; campos extras são ignorados. Campos extras na raiz, envelope e despesas não alteram cálculos. JSON inválido, chaves JSON repetidas, envelope inválido ou colaborador incompleto/inválido rejeitam o lote inteiro. Campo `id` de despesa ausente gera ID; presente mas vazio, composto só por espaços ou com tipo incorreto torna a despesa estruturalmente inválida. ID repetido rejeita somente a ocorrência posterior no nível do item; o lote continua. Datas não têm hora/fuso. Valores estão em reais. Sem limite artificial de quantidade de itens nesta versão.

### Saída de sucesso
Objeto com `versao_spec: "0.2"`, colaborador e período usados no processamento, avisos (lista de códigos), `items` (lista em ordem original) e `resumo`. Índices são zero-based. ID ausente é gerado como `gerado-{índice}`; em colisão normalizada, tentar `gerado-{índice}-1`, `-2` etc. O índice original inclui todos os itens da entrada. ID fornecido é preservado exatamente na saída; para comparação, remover espaços ASCII das extremidades e ignorar diferença entre maiúsculas/minúsculas. ID inválido presente retorna `id: null`; nunca gerar ID para substituir um valor presente inválido. Valores monetários de saída têm até duas casas, exceto `valor_original`, preservado quando numericamente válido.

| Campo de items[] | Tipo | Significado |
|---|---|---|
| indice | inteiro >= 0 | Posição no arquivo |
| id | texto ou null | ID original preservado; gerado quando ausente; null quando presente mas inválido |
| valor_original | número ou null | Valor recebido se numericamente válido |
| valor_solicitado | número | Valor positivo arredondado para itens estruturalmente válidos; para itens inválidos/zero-negativos, 0; itens duplicados e recusados por regra podem manter o valor arredondado |
| categoria_normalizada | texto ou null | Valor normalizado se disponível |
| valor_reembolsavel | número | Pagamento calculado |
| status | texto enum | APROVADO, PARCIAL, RECUSADO, IGNORADO |
| motivo | texto enum | Código principal abaixo |
| justificativa | texto não vazio | Explicação humana coerente, redação livre |
| duplicata_de_indice | inteiro ou null | Primeiro item equivalente |
| avisos | lista de textos | DIARIAS_NAO_INFORMADAS quando hospedagem estruturalmente válida |

Motivos permitidos: `DADO_INVALIDO`, `DUPLICATA`, `ESTORNO_NAO_PROCESSADO`, `VALOR_ZERO`, `FORA_DA_COMPETENCIA`, `CATEGORIA_NAO_PREVISTA`, `NOTA_FISCAL_OBRIGATORIA`, `LIMITE_ESGOTADO`, `LIMITE_APLICADO`, `DENTRO_DO_LIMITE`. `erros` é sempre uma lista de `{campo, codigo}`; campos estruturais inválidos registram todos os erros em ordem fixa, usando `CAMPO_OBRIGATORIO`, `TIPO_OU_FORMATO_INVALIDO` ou `ID_REPETIDO`. Repetição de ID gera `status: RECUSADO`, `motivo: DADO_INVALIDO` e erro `ID_REPETIDO`. Duplicata por conteúdo com ID diferente gera `IGNORADO`/`DUPLICATA` e define `duplicata_de_indice`. Itens estruturalmente inválidos permanecem em `items`, mas não entram em `total_itens`, contagens por status nem totais financeiros.

`resumo` contém `total_itens`, quantidades por status (`aprovados`, `parciais`, `recusados`, `ignorados`), `total_solicitado`, `total_reembolsavel` e `total_nao_reembolsavel`. `total_itens` e contagens incluem somente despesas estruturalmente válidas, inclusive duplicatas por conteúdo, IDs repetidos e itens ignorados por valor zero/negativo; despesas estruturalmente inválidas ficam fora. `total_solicitado` soma valores arredondados de despesas estruturalmente válidas que chegam ao cálculo de elegibilidade antes dos limites; itens recusados por regra de negócio, duplicados, ignorados e estruturalmente inválidos são excluídos. `total_reembolsavel` soma pagamentos efetivos. `total_nao_reembolsavel = total_solicitado - total_reembolsavel`. Lista vazia resulta em totais e contagens zero. Aviso global `VIAGEM_NAO_INFORMADA` consta em todo sucesso, inclusive lista vazia. Hospedagem acrescenta aviso por item, mesmo se recusada.

Falha de lote: objeto `{versao_spec: "0.2", erro: {codigo, mensagem}}`, sem `items`/`resumo`. Códigos: `JSON_INVALIDO`, `ENTRADA_INVALIDA`, `ERRO_IO`. Chaves repetidas no mesmo objeto JSON causam `JSON_INVALIDO`; colaborador obrigatório incompleto/inválido ou envelope inválido causa `ENTRADA_INVALIDA`. IDs repetidos de despesa não causam falha de lote. Nenhuma saída financeira parcial em falha. Erro de leitura/escrita deve ser informado no canal de erro quando não for possível gravar resultado.

Exemplo para uma alimentação válida de 61,00 com nota:
```json
{"versao_spec":"0.2","colaborador":{"id":"c-1","nome":"Exemplo","centro_custo":"CC"},"periodo":{"competencia":"2026-07","inicio":"2026-07-01","fim":"2026-07-31"},"avisos":["VIAGEM_NAO_INFORMADA"],"items":[{"indice":0,"id":"x-1","valor_original":61,"valor_solicitado":61,"categoria_normalizada":"alimentacao","valor_reembolsavel":60,"status":"PARCIAL","motivo":"LIMITE_APLICADO","justificativa":"Aplicado limite diário de R$ 60,00.","duplicata_de_indice":null,"avisos":[],"erros":[]}],"resumo":{"total_itens":1,"aprovados":0,"parciais":1,"recusados":0,"ignorados":0,"total_solicitado":61,"total_reembolsavel":60,"total_nao_reembolsavel":1}}
```

## 5. Regras de negócio

### RN-001 — Agregação diária
**Regra:** Somar por colaborador, data e categoria; alimentação 60, transporte 80.
**Origem:** Alimentação tem limite de R$ 60 por dia. Evidência: d-001/d-002.
**Aceite AC-001:** 72,50 + 38,00 no mesmo dia: 60,00 e 0,00.

### RN-002 — Distribuição do teto
**Regra:** Consumir saldo pela ordem dos itens no arquivo; itens recusados/ignorados não consomem saldo.
**Origem:** Despesas acima do limite são reembolsadas parcialmente. Evidência: d-001/d-002.
**Aceite AC-002:** 38,00 antes de 72,50 resulta em 38,00 e 22,00; mesmo total 60,00.

### RN-003 — Fronteira do limite
**Regra:** Reembolsar o mínimo entre valor normalizado e saldo disponível; igualdade é aprovação integral; saldo zero recusa.
**Origem:** Despesas acima do limite são reembolsadas parcialmente. Evidência: d-014.
**Aceite AC-003:** Alimentação isolada 59,99/60,00/60,01 paga 59,99/60,00/60,00.

### RN-004 — Obrigatoriedade fiscal
**Regra:** Exigir nota quando valor positivo original, antes de arredondar e limitar, for estritamente maior que 100; verificar por item.
**Origem:** Nota fiscal é obrigatória acima de R$ 100. Evidência: d-003/d-004/d-013.
**Aceite AC-004:** 100,00 sem nota pode pagar 80; 100,01 sem nota paga 0, mesmo com teto 80.

### RN-005 — Viagem sem campo
**Regra:** Não inferir viagem de descrição, hotel, aeroporto ou centro de custo. No formato atual não aplicar acréscimo; registrar aviso VIAGEM_NAO_INFORMADA no resultado.
**Origem:** Colaborador em viagem tem limites ampliados em 50%. Evidência: d-003/d-010/d-011.
**Aceite AC-005:** Corrida aeroporto 100,00 continua limitada a 80; hotel 480 continua limitado a 250.

### RN-006 — Competência
**Regra:** Usar data da despesa, pois lançamento não existe. Aceitar `inicio <= data <= fim`. Datas de início e fim válidas e invertidas são trocadas automaticamente; a saída retorna o período corrigido efetivamente usado. As datas devem pertencer ao mês de competência. O tratamento de competência ausente/inválida, data inexistente ou incompatibilidade com o mês (exceto inversão válida) permanece em aberto na correção 69; não inferir comportamento adicional.
**Origem:** Despesas devem ser lançadas dentro do período de competência. Evidência: d-008/d-014.
**Aceite AC-006:** 2026-04-15 recusa; 2026-07-01 e 2026-07-31 aceitam no período de julho. Se `inicio` e `fim` forem datas válidas mas estiverem invertidas, trocar a ordem e retornar o período corrigido. Outros erros de período aguardam a correção 69.

### RN-007 — Identificação de duplicatas
**Regra:** Validar estrutura antes de deduplicar. Para ID, remover espaços ASCII das extremidades e comparar sem diferenciar maiúsculas/minúsculas; preservar o texto original na saída. A primeira ocorrência estruturalmente válida de um ID é mantida; ocorrência posterior com o mesmo ID é `RECUSADO`/`DADO_INVALIDO`, com erro `ID_REPETIDO`, sem abortar o lote. IDs de itens estruturalmente inválidos não reservam o ID para deduplicação. Só entre IDs diferentes comparar conteúdo: data normalizada, categoria normalizada, fornecedor e descrição normalizados por Unicode NFC + trim ASCII nas extremidades + comparação sem diferença de caixa, e valor arredondado a duas casas (RN-009). Não considerar `tem_nota_fiscal` nem campos extras. O primeiro item estruturalmente válido com aquele conteúdo é canônico mesmo se recusado por regra de negócio; posterior é `IGNORADO`/`DUPLICATA`, `valor_reembolsavel: 0` e `duplicata_de_indice` aponta ao canônico.
**Origem:** Duplicatas devem ser tratadas. Evidência: d-006/d-007.
**Aceite AC-007:** d-006 paga 54,90; d-007 é ignorado com referencia ao índice 5.

### RN-008 — Estorno
**Regra:** Ignorar valores negativos, reembolso zero, motivo ESTORNO_NAO_PROCESSADO; não compensar outras despesas.
**Origem:** Entrada de exemplo contém valor negativo; política não esclarece. Evidência: d-009.
**Aceite AC-008:** -45,00 paga 0 e não aumenta saldo nem diminui total solicitado.

### RN-009 — Precisão monetária
**Regra:** Arredondar cada valor positivo para duas casas, metade para cima; totalizar valores já arredondados. Manter valor original no resultado. Zero original ou arredondado é ignorado.
**Origem:** Entrada inclui 33.333. Evidência: d-011.
**Aceite AC-009:** 33,333 -> 33,33; 33,335 -> 33,34; 0,004 -> 0,00 ignorado.

### RN-010 — Quantidade de diárias
**Regra:** Não extrair números de texto livre. Considerar uma diária por data informada, compartilhada por todas as hospedagens do mesmo colaborador/data; sinalizar DIARIAS_NAO_INFORMADAS.
**Origem:** Hospedagem tem limite de R$ 250 por diária. Evidência: d-010/d-013.
**Aceite AC-010:** Hotel 480 com descrição 2 diarias paga 250; Airbnb 690 sem nota paga 0.

### RN-011 — Capitalização de valores
**Regra:** Remover espaços ASCII nas extremidades e converter A-Z em a-z somente no valor categoria. Aceitar alimentacao, transporte_urbano, hospedagem. Não remover acentos nem criar aliases.
**Origem:** Categorias fora da política não são reembolsáveis. Evidência: d-014/d-005.
**Aceite AC-011:** ALIMENTACAO e Alimentacao pagam até 60; alimentação e coworking recusam.

### RN-012 — Fim de semana
**Regra:** Aplicar regras em todos os dias civis, inclusive sábados, domingos e feriados.
**Origem:** Política não restringe dias úteis. Evidência: d-012.
**Aceite AC-012:** Sábado 18/07/2026, alimentação 47,20, paga 47,20.

### RN-013 — Capitalização de chaves
**Regra:** Chaves são exatas e sensíveis a maiúsculas: tem_nota_fiscal obrigatório e booleano real. Aliases não substituem campos. Campos adicionais são ignorados e não afetam regras.
**Origem:** Respeite o formato da entrada. Evidência: Caso adicional solicitado.
**Aceite AC-013:** temNotaFiscal sem tem_nota_fiscal invalida item; false é válido, string false não.

### RN-014 — Falhas de entrada
**Regra:** JSON inválido e chaves repetidas em objeto JSON causam falha de lote `JSON_INVALIDO`; envelope inválido ou qualquer campo obrigatório de `colaborador` ausente, vazio ou de tipo incorreto causa `ENTRADA_INVALIDA`. Despesas são validadas individualmente: registrar todos os erros estruturais em ordem determinística e recusar uma única vez com `RECUSADO`/`DADO_INVALIDO`; continuar o lote. ID ausente gera ID determinístico baseado no índice original; ID presente inválido é `null` e não é substituído por ID gerado. ID repetido em despesa estruturalmente válida rejeita apenas a ocorrência posterior, com erro `ID_REPETIDO`. Campos extras são ignorados.
**Origem:** Entrada de referência define forma, mas não recuperação. Evidência: Caso adicional.
**Aceite AC-014:** Item com valor string `60` é recusado e o próximo item válido é processado; ID repetido recusa somente a ocorrência posterior com `ID_REPETIDO`; JSON com chaves repetidas rejeita o lote com `JSON_INVALIDO`; colaborador incompleto rejeita o lote com `ENTRADA_INVALIDA`.

### RN-015 — Precedência e motivos
**Regra:** Aplicar a ordem da seção 8; emitir um motivo principal, avisos separados. Duplicatas podem referenciar item recusado.
**Origem:** Política contém regras sobrepostas. Evidência: d-013.
**Aceite AC-015:** Airbnb 690 sem nota: NOTA_FISCAL_OBRIGATORIA, sem consumir teto de hotel.

### RN-016 — Totais e status
**Regra:** Solicitado soma todos os valores positivos estruturalmente válidos arredondados, inclusive duplicatas/recusas; reembolsável soma pagamentos; não reembolsável é diferença. Valores negativos/zero ignorados não entram. Contagens particionam itens.
**Origem:** Schema de saída é definido pelo participante. Evidência: Todos os itens.
**Aceite AC-016:** O resumo exclui recusas, duplicatas, ignorados e estruturalmente inválidos dos totais financeiros; `total_nao_reembolsavel` é a diferença entre solicitado e reembolsável. Os números do exemplo são recalculados na seção 9 e permanecem pendentes de validação automatizada.

### RN-017 — Contrato de execução
CLI aceita calcular --input <arquivo> --output <arquivo>. Sucesso retorna código 0; entrada/lote inválido retorna 2; falha de I/O retorna 3. Não misturar logs com resultado. Uma mesma entrada produz saída financeira idêntica, sem depender da hora de execução. **AC-017:** executar com exemplo grava JSON coerente e retorna 0; arquivo inexistente retorna 3; JSON inválido retorna 2.

### RN-018 — Estrutura da saída
Cada item gera exatamente um objeto em `items`; despesas estruturalmente inválidas permanecem na lista, mas ficam fora de `total_itens`, contagens e totais financeiros. **AC-018:** soma dos quatro status = `total_itens` (não necessariamente quantidade da entrada); soma dos pagamentos = `total_reembolsavel`; `total_solicitado - total_reembolsavel = total_nao_reembolsavel`; nenhum pagamento é negativo ou maior que o valor solicitado.

## 6. Ambiguidades identificadas e decisões
As referências abaixo são uma análise própria, não a lista fechada do avaliador. Quando a política é silenciosa, isso está indicado na origem, sem atribuir ao RH um texto que ele não escreveu.

### AMB-001 — Agregação diária
**Texto original / origem:** Alimentação tem limite de R$ 60 por dia.
**Dúvida:** Por item ou soma diária?
**Decisão proposta:** Somar por colaborador, data e categoria; alimentação 60, transporte 80.
**Justificativa:** Impedir multiplicação do teto pelo número de comprovantes.
**Regra:** RN-001. **Evidência:** d-001/d-002.

### AMB-002 — Distribuição do teto
**Texto original / origem:** Despesas acima do limite são reembolsadas parcialmente.
**Dúvida:** Rateio ou prioridade?
**Decisão proposta:** Consumir saldo pela ordem dos itens no arquivo; itens recusados/ignorados não consomem saldo.
**Justificativa:** Produzir distribuição simples, auditável e determinística.
**Regra:** RN-002. **Evidência:** d-001/d-002.

### AMB-003 — Fronteira do limite
**Texto original / origem:** Despesas acima do limite são reembolsadas parcialmente.
**Dúvida:** Igual ao teto é parcial?
**Decisão proposta:** Reembolsar o mínimo entre valor normalizado e saldo disponível; igualdade é aprovação integral; saldo zero recusa.
**Justificativa:** Cortar somente excedente.
**Regra:** RN-003. **Evidência:** d-014.

### AMB-004 — Obrigatoriedade fiscal
**Texto original / origem:** Nota fiscal é obrigatória acima de R$ 100.
**Dúvida:** 100,00 exige nota? Sobre valor original ou reembolsável?
**Decisão proposta:** Exigir nota quando valor positivo original, antes de arredondar e limitar, for estritamente maior que 100; verificar por item.
**Justificativa:** Não permitir que teto ou arredondamento dispense comprovante obrigatório.
**Regra:** RN-004. **Evidência:** d-003/d-004/d-013.

### AMB-005 — Viagem sem campo
**Texto original / origem:** Colaborador em viagem tem limites ampliados em 50%.
**Dúvida:** Como comprovar viagem sem atributo?
**Decisão proposta:** Não inferir viagem de descrição, hotel, aeroporto ou centro de custo. No formato atual não aplicar acréscimo; registrar aviso VIAGEM_NAO_INFORMADA no resultado.
**Justificativa:** Evitar concessão sem informação verificável; restrição explícita e revisável.
**Regra:** RN-005. **Evidência:** d-003/d-010/d-011.

### AMB-006 — Competência
**Texto original / origem:** Despesas devem ser lançadas dentro do período de competência.
**Dúvida:** Data do gasto ou lançamento? Limites inclusivos?
**Decisão proposta:** Usar data da despesa, pois lançamento não existe. Aceitar inicio <= data <= fim. Inicio/fim devem ser válidos, ordenados e estar no mês competencia.
**Justificativa:** Preservar contrato existente e não inventar data de lançamento.
**Regra:** RN-006. **Evidência:** d-008/d-014.

### AMB-007 — Identificação de duplicatas
**Texto original / origem:** Duplicatas devem ser tratadas.
**Dúvida:** ID ou conteúdo? Qual item permanece?
**Decisão proposta:** Comparar data, categoria normalizada, fornecedor e descrição exatos e valor decimal original equivalente. Ignorar id e tem_nota_fiscal na chave. Primeiro item estruturalmente válido é canônico, mesmo se recusado; posteriores pagam zero e referenciam seu índice.
**Justificativa:** IDs diferentes não impedem duplicidade; não escolher comprovante mais favorável silenciosamente.
**Regra:** RN-007. **Evidência:** d-006/d-007.

### AMB-008 — Estorno
**Texto original / origem:** Entrada de exemplo contém valor negativo; política não esclarece.
**Dúvida:** Abater orçamento ou recusar?
**Decisão proposta:** Ignorar valores negativos, reembolso zero, motivo ESTORNO_NAO_PROCESSADO; não compensar outras despesas.
**Justificativa:** Não há vínculo com despesa original para conciliação segura.
**Regra:** RN-008. **Evidência:** d-009.

### AMB-009 — Precisão monetária
**Texto original / origem:** Entrada inclui 33.333.
**Dúvida:** Rejeitar ou arredondar? Em qual momento?
**Decisão proposta:** Arredondar cada valor positivo para duas casas, metade para cima; totalizar valores já arredondados. Manter valor original no resultado. Zero original ou arredondado é ignorado.
**Justificativa:** Resultados monetários consistentes e auditáveis.
**Regra:** RN-009. **Evidência:** d-011.

### AMB-010 — Quantidade de diárias
**Texto original / origem:** Hospedagem tem limite de R$ 250 por diária.
**Dúvida:** Como obter quantidade ausente?
**Decisão proposta:** Não extrair números de texto livre. Considerar uma diária por data informada, compartilhada por todas as hospedagens do mesmo colaborador/data; sinalizar DIARIAS_NAO_INFORMADAS.
**Justificativa:** Evitar interpretação frágil de descrições; decisão conservadora explícita.
**Regra:** RN-010. **Evidência:** d-010/d-013.

### AMB-011 — Capitalização de valores
**Texto original / origem:** Categorias fora da política não são reembolsáveis.
**Dúvida:** ALIMENTACAO equivale a alimentacao?
**Decisão proposta:** Remover espaços ASCII nas extremidades e converter A-Z em a-z somente no valor categoria. Aceitar alimentacao, transporte_urbano, hospedagem. Não remover acentos nem criar aliases.
**Justificativa:** Resolver variação observada preservando vocabulário fechado.
**Regra:** RN-011. **Evidência:** d-014/d-005.

### AMB-012 — Fim de semana
**Texto original / origem:** Política não restringe dias úteis.
**Dúvida:** Plantão sábado pode reembolsar?
**Decisão proposta:** Aplicar regras em todos os dias civis, inclusive sábados, domingos e feriados.
**Justificativa:** Não criar restrição ausente da política.
**Regra:** RN-012. **Evidência:** d-012.

### AMB-013 — Capitalização de chaves
**Texto original / origem:** Respeite o formato da entrada.
**Dúvida:** temNotaFiscal ou TEM_NOTA_FISCAL são aliases?
**Decisão proposta:** Chaves são exatas e sensíveis a maiúsculas: tem_nota_fiscal obrigatório e booleano real. Aliases não substituem campos. Campos adicionais são ignorados e não afetam regras.
**Justificativa:** Separar normalização de um valor de mudança do contrato.
**Regra:** RN-013. **Evidência:** Caso adicional solicitado.

### AMB-014 — Falhas de entrada
**Texto original / origem:** Entrada de referência define forma, mas não recuperação.
**Dúvida:** Um item inválido aborta lote?
**Decisão proposta:** JSON inválido, chaves JSON repetidas, envelope inválido ou IDs de despesa repetidos abortam lote. Item com campo obrigatório ausente/tipo inválido é recusado com DADO_INVALIDO; demais continuam. ID ausente gera id null e usa índice.
**Justificativa:** Evitar perda do lote por uma despesa e garantir identidade não ambígua.
**Regra:** RN-014. **Evidência:** Caso adicional.

### AMB-015 — Precedência e motivos
**Texto original / origem:** Política contém regras sobrepostas.
**Dúvida:** Qual motivo prevalece?
**Decisão proposta:** Aplicar a ordem da seção 8; emitir um motivo principal, avisos separados. Duplicatas podem referenciar item recusado.
**Justificativa:** Evitar resultados e consumo de teto dependentes de verificações implícitas.
**Regra:** RN-015. **Evidência:** d-013.

### AMB-016 — Totais e status
**Texto original / origem:** Schema de saída é definido pelo participante.
**Dúvida:** Negativos contam? Zero é parcial?
**Decisão proposta:** Solicitado soma todos os valores positivos estruturalmente válidos arredondados, inclusive duplicatas/recusas; reembolsável soma pagamentos; não reembolsável é diferença. Valores negativos/zero ignorados não entram. Contagens particionam itens.
**Justificativa:** Permitir conciliação explícita entre entrada, recusas e pagamento.
**Regra:** RN-016. **Evidência:** Todos os itens.

## 7. Casos de borda
| Caso | Resultado esperado |
|---|---|
| Teto exato e um centavo acima | RN-003: integral no teto, parcial acima |
| Nota false para 99,99 / 100,00 / 100,01 | Sem bloqueio / sem bloqueio / recusa; teto continua aplicável |
| 100,004 sem nota | Recusa fiscal, apesar de arredondar a 100,00 |
| 33,335 e 33,333 | 33,34 e 33,33 |
| Duas despesas 30,005 no mesmo dia | 30,01 + 29,99 = 60,00 |
| Valor -45 / 0 / 0,004 | Ignorados, não consomem teto |
| Alimentacao / ALIMENTACAO / alimentacao | Mesma categoria |
| " alimentacao " | Aceita após remover espaços ASCII extremos |
| alimentação / transporteUrbano | Categorias não previstas |
| ID repetido após trim ASCII e comparação sem caixa | Segunda ocorrência estruturalmente válida é RECUSADO/DADO_INVALIDO com ID_REPETIDO; lote continua |
| Mesmo conteúdo, IDs diferentes | Segundo IGNORADO/DUPLICATA; valores são comparados após arredondamento a duas casas |
| Mesmo conteúdo com fornecedor em caixa diferente | Duplicata após NFC, trim ASCII externo e comparação sem diferença de caixa |
| Valores 10,004 e 10,00, demais campos iguais | Podem ser duplicatas porque a comparação usa valores arredondados |
| Canônico sem nota, repetição com nota | Canônico recusado; posterior ignorado; nenhum paga |
| Item inválido antes de cópia válida | Inválido não vira canônico; válido pode pagar |
| Despesa fora do mês e sem nota | FORA_DA_COMPETENCIA prevalece |
| Categoria desconhecida e sem nota | CATEGORIA_NAO_PREVISTA prevalece |
| Duas hospedagens com nota 200 + 100 na mesma data | 200 + 50; aviso de diárias em ambos |
| Dia inicial/final / um dia fora | Aceita/aceita/recusa |
| Campo booleano com valor "false" | DADO_INVALIDO |
| despesas vazia | Sucesso e totais zero |
| Datas inicial/final invertidas e válidas | Trocar automaticamente e retornar o período corrigido; outros erros de período aguardam decisão 69 |

## 8. Ordem de aplicação das regras
1. Fazer parsing JSON estrito; qualquer chave repetida em qualquer objeto causa `JSON_INVALIDO` e rejeita o lote inteiro, sem resultado financeiro parcial.
2. Validar envelope e colaborador. Se qualquer campo obrigatório de `colaborador` estiver ausente, vazio ou com tipo incorreto, rejeitar lote inteiro com `ENTRADA_INVALIDA`.
3. Validar período conforme RN-006. Trocar datas inicial/final invertidas quando ambas forem datas válidas; retornar as datas corrigidas. Não presumir tratamento para outros erros de período enquanto a correção 69 estiver em aberto.
4. Preparar conjunto de IDs normalizados de todos os IDs fornecidos em despesas, inclusive IDs presentes em despesas estruturalmente inválidas, apenas para evitar colisão com IDs gerados. Normalização de comparação: trim ASCII nas extremidades + comparação sem diferença de caixa.
5. Percorrer despesas na ordem original e gerar o ID se o campo estiver ausente: `gerado-{índice}`; se colidir com ID fornecido ou já gerado, tentar `gerado-{índice}-1`, depois `-2` e assim por diante. Índice é zero-based na lista original. Se `id` estiver presente mas vazio, só espaços ASCII ou tipo incorreto, não gerar substituto: `id: null` e erro estrutural.
6. Validar a estrutura de cada despesa em ordem fixa de campos: ID; demais campos obrigatórios na ordem do schema; por último campos opcionais definidos. Registrar todos os erros encontrados independentemente da ordem das chaves JSON. Item inválido recebe `RECUSADO`/`DADO_INVALIDO`, fica em `items`, não reserva ID e não entra em `total_itens`, contagens ou totais financeiros.
7. Para despesa estruturalmente válida, verificar repetição de ID antes de deduplicação por conteúdo. A primeira ocorrência estruturalmente válida do ID é a referência; a posterior recebe `RECUSADO`/`DADO_INVALIDO`, `erros: [{campo: "id", codigo: "ID_REPETIDO"}]`, é contada em `total_itens` e `recusados`, não entra em totais financeiros, e o lote continua.
8. Para IDs distintos, normalizar categoria, data, fornecedor (NFC + trim ASCII externo + sem diferença de caixa), descrição (mesma regra) e valor arredondado a duas casas. Não comparar `tem_nota_fiscal` nem campos extras. Duplicata de conteúdo recebe `IGNORADO`/`DUPLICATA`, valor arredondado preservado em `valor_solicitado`, reembolso zero e referência ao primeiro item estruturalmente válido com aquele conteúdo, mesmo que tenha sido recusado por regra de negócio. Conta em `total_itens`/`ignorados`, não entra em totais financeiros.
9. Aplicar regras de negócio aos itens restantes na ordem definida: quantizar valor (metade para cima), ignorar negativos (`ESTORNO_NAO_PROCESSADO`) e valores zero/após arredondamento (`VALOR_ZERO`) com valores solicitados e reembolsáveis iguais a zero; verificar competência, categoria, nota fiscal; então aplicar os limites diários base e consumir saldo na ordem de entrada. Itens estruturalmente válidos recusados por regra de negócio mantêm `valor_solicitado` arredondado, mas são excluídos de totais financeiros. Itens válidos ignorados por zero/negativo contam nos status e em `total_itens`, mas não nos totais financeiros.
10. Calcular resumo: `total_itens` e contagens apenas de itens estruturalmente válidos; `total_solicitado` soma somente valores elegíveis que chegam ao cálculo de limites; excluir recusados, duplicatas, ignorados e estruturalmente inválidos. `total_reembolsavel` soma pagamentos; `total_nao_reembolsavel = total_solicitado - total_reembolsavel`. Preservar ordem original de `items` e retornar `periodo` corrigido quando houver inversão automática.

## 9. Critérios de aceite
- [ ] AC-001 a AC-018 e os casos de borda estão associados a testes automatizados identificáveis; não marcar como validados antes da execução e aprovação dos testes.
- [ ] Os 14 itens do exemplo geram os resultados recalculados abaixo; são resultados esperados da proposta, não gabarito oficial nem execução validada.
- [ ] Campos ausentes, erros fiscais e duplicatas não desaparecem da saída.
- [ ] JSON de entrada não muda de contrato para acomodar viagem/diárias.
- [ ] Nenhum conhecimento externo é necessário para calcular a saída.

### Resultado esperado recalculado do exemplo (proposta; ainda não validado por execução de testes)
| Item | Solicitado | Reembolsável | Status | Motivo |
|---|---:|---:|---|---|
| d-001 |72,50|60,00|PARCIAL|LIMITE_APLICADO|
| d-002 |38,00|0,00|RECUSADO|LIMITE_ESGOTADO|
| d-003 |100,00|80,00|PARCIAL|LIMITE_APLICADO|
| d-004 |100,01|0,00|RECUSADO|NOTA_FISCAL_OBRIGATORIA|
| d-005 |89,00|0,00|RECUSADO|CATEGORIA_NAO_PREVISTA|
| d-006 |54,90|54,90|APROVADO|DENTRO_DO_LIMITE|
| d-007 |54,90|0,00|IGNORADO|DUPLICATA|
| d-008 |41,00|0,00|RECUSADO|FORA_DA_COMPETENCIA|
| d-009 |0,00|0,00|IGNORADO|ESTORNO_NAO_PROCESSADO|
| d-010 |480,00|250,00|PARCIAL|LIMITE_APLICADO|
| d-011 |33,33|33,33|APROVADO|DENTRO_DO_LIMITE|
| d-012 |47,20|47,20|APROVADO|DENTRO_DO_LIMITE|
| d-013 |690,00|0,00|RECUSADO|NOTA_FISCAL_OBRIGATORIA|
| d-014 |61,00|60,00|PARCIAL|LIMITE_APLICADO|

Contagens dos 14 itens estruturalmente válidos: 3 aprovados, 4 parciais, 5 recusados, 2 ignorados. `total_solicitado` esperado: 848,93; `total_reembolsavel`: 585,43; `total_nao_reembolsavel`: 263,50. São cálculos derivados das regras propostas e precisam ser confirmados pelos testes automatizados; não são gabarito oficial nem execução validada.

## 10. O que fica em aberto
- **Mudança do Dia 2:** requisito ainda não recebido; revisar regras e testes relacionados quando estiver disponível.
- **Correção 69 — período inválido:** decisão ainda não tomada para competência ausente/inválida, datas inexistentes ou datas incompatíveis com o mês de competência. A única decisão já tomada é trocar datas inicial/final válidas quando estiverem invertidas e retornar o período corrigido.
- **Execução de testes:** os critérios e vínculos de rastreabilidade são requisitos de trabalho; nenhum teste deve ser marcado como validado até execução e aprovação reais.

## 11. Rastreabilidade e testes
Cada critério de aceite deve estar ligado a uma regra de negócio e a um teste automatizado identificável. A tabela abaixo define o vínculo funcional; o identificador concreto do arquivo de teste deve corresponder à suíte real do repositório e não deve ser inventado antes de inspecioná-la.

| Critério | Regra(s) | Teste automatizado | Estado |
|---|---|---|---|
| AC-001 a AC-012 | RN-001 a RN-012 | Identificador da suíte correspondente a confirmar no repositório | Pendente de inspeção/execução |
| AC-013 | RN-013 | Teste de chaves exatas, campos extras e booleanos | Pendente de inspeção/execução |
| AC-014 | RN-014 | Testes de JSON inválido, chaves repetidas, envelope, colaborador incompleto, ID gerado/ inválido/repetido e validação de item | Pendente de inspeção/execução |
| AC-015 | RN-015 | Teste de precedência de motivos e consumo de saldo | Pendente de inspeção/execução |
| AC-016 | RN-016, RN-018 | Teste de resumo e exclusões dos totais | Pendente de inspeção/execução |
| AC-017 | RN-017 | Testes CLI de sucesso, entrada inválida e erro de I/O | Pendente de inspeção/execução |
| AC-018 | RN-018 | Teste de invariantes de saída | Pendente de inspeção/execução |
| AC-019 | RN-014 | Chaves JSON repetidas rejeitam lote com `JSON_INVALIDO`, sem resultado parcial | Pendente de criar/verificar teste |
| AC-020 | RN-014 | Colaborador incompleto rejeita lote com `ENTRADA_INVALIDA` | Pendente de criar/verificar teste |
| AC-021 | RN-006 | Inversão de datas válidas é corrigida e período corrigido é retornado | Pendente de criar/verificar teste |

AMB-001–AMB-016 → RN correspondente → AC da regra → teste automatizado: manter esse encadeamento explícito. Quando uma AMB não tiver relação direta com um AC, registrar “sem relação direta” em vez de criar vínculo artificial. 
