# Spec — Motor de Cálculo de Reembolso

**Versão:** 0.1 · **Status:** proposta para revisada por Andrei · **Data:** 19/10/2026

As decisões abaixo são propostas explícitas deste documento, não respostas oficiais nem decisões já aprovadas pelo participante. Uma vez adotadas, formam um comportamento completo e verificável. Revisar especialmente viagem, diárias, duplicatas e ordem de consumo antes de implementar. A mudança do Dia 2 é desconhecida.

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
| despesas[].id | texto não vazio | Sim; único quando presente e válido |
| despesas[].data | data YYYY-MM-DD | Sim |
| despesas[].categoria | texto | Sim; normalização definida em RN-011 |
| despesas[].descricao, fornecedor | texto não vazio | Sim; sem normalização |
| despesas[].valor | número decimal finito | Sim; booleano não é número, não aceitar texto numérico |
| despesas[].tem_nota_fiscal | booleano | Sim; somente true ou false |

Strings obrigatórias contendo somente espaços são inválidas. Chaves são exatas; extras são ignoradas. Raiz não objeto, despesas não lista, colaborador/período inválidos e IDs repetidos invalidam o lote. Datas não têm hora/fuso. Valores estão em reais. Sem limite artificial de quantidade de itens nesta versão.

### Saída de sucesso
Objeto com versao_spec (texto), colaborador e periodo preservados, avisos (lista de códigos), items (lista em ordem original) e resumo (objeto). Índices são zero-based e identificam o item mesmo quando seu id está ausente. Valores monetários de saída são números não negativos de até duas casas, exceto valor_original, preservado como número da entrada quando válido; zeros à direita não são obrigatórios.

| Campo de items[] | Tipo | Significado |
|---|---|---|
| indice | inteiro >= 0 | Posição no arquivo |
| id | texto ou null | Identificador, null quando ausente/inválido |
| valor_original | número ou null | Valor recebido se numericamente válido |
| valor_solicitado | número | Valor positivo válido arredondado; senão 0 |
| categoria_normalizada | texto ou null | Valor normalizado se disponível |
| valor_reembolsavel | número | Pagamento calculado |
| status | texto enum | APROVADO, PARCIAL, RECUSADO, IGNORADO |
| motivo | texto enum | Código principal abaixo |
| justificativa | texto não vazio | Explicação humana coerente, redação livre |
| duplicata_de_indice | inteiro ou null | Primeiro item equivalente |
| avisos | lista de textos | DIARIAS_NAO_INFORMADAS quando hospedagem estruturalmente válida |

Motivos permitidos: DADO_INVALIDO, DUPLICATA, ESTORNO_NAO_PROCESSADO, VALOR_ZERO, FORA_DA_COMPETENCIA, CATEGORIA_NAO_PREVISTA, NOTA_FISCAL_OBRIGATORIA, LIMITE_ESGOTADO, LIMITE_APLICADO, DENTRO_DO_LIMITE. Em DADO_INVALIDO, incluir erros como lista de {campo, codigo}, códigos CAMPO_OBRIGATORIO ou TIPO_OU_FORMATO_INVALIDO; demais itens usam erros: [].

resumo contém total_itens; quantidades por status (aprovados, parciais, recusados, ignorados); total_solicitado, total_reembolsavel, total_nao_reembolsavel. Lista vazia resulta em todos os totais e contagens zero. Aviso global VIAGEM_NAO_INFORMADA consta em todo sucesso, inclusive lista vazia. Hospedagem acrescenta aviso por item, mesmo se recusada.

Falha de lote: objeto {versao_spec: "0.1", erro: {codigo, mensagem}}, sem items/resumo. Códigos: JSON_INVALIDO, ENTRADA_INVALIDA, IDS_REPETIDOS, ERRO_IO. Nenhuma saída financeira parcial em falha. Erro de leitura/escrita deve ser informado no canal de erro quando não for possível gravar resultado.

Exemplo para uma alimentação válida de 61,00 com nota:
```json
{"versao_spec":"0.1","colaborador":{"id":"c-1","nome":"Exemplo","centro_custo":"CC"},"periodo":{"competencia":"2026-07","inicio":"2026-07-01","fim":"2026-07-31"},"avisos":["VIAGEM_NAO_INFORMADA"],"items":[{"indice":0,"id":"x-1","valor_original":61,"valor_solicitado":61,"categoria_normalizada":"alimentacao","valor_reembolsavel":60,"status":"PARCIAL","motivo":"LIMITE_APLICADO","justificativa":"Aplicado limite diário de R$ 60,00.","duplicata_de_indice":null,"avisos":[],"erros":[]}],"resumo":{"total_itens":1,"aprovados":0,"parciais":1,"recusados":0,"ignorados":0,"total_solicitado":61,"total_reembolsavel":60,"total_nao_reembolsavel":1}}
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
**Regra:** Usar data da despesa, pois lançamento não existe. Aceitar inicio <= data <= fim. Inicio/fim devem ser válidos, ordenados e estar no mês competencia.
**Origem:** Despesas devem ser lançadas dentro do período de competência. Evidência: d-008/d-014.
**Aceite AC-006:** 2026-04-15 recusa; 2026-07-01 e 2026-07-31 aceitam no período de julho.

### RN-007 — Identificação de duplicatas
**Regra:** Comparar data, categoria normalizada, fornecedor e descrição exatos e valor decimal original equivalente. Ignorar id e tem_nota_fiscal na chave. Primeiro item estruturalmente válido é canônico, mesmo se recusado; posteriores pagam zero e referenciam seu índice.
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
**Regra:** JSON inválido, chaves JSON repetidas, envelope inválido ou IDs de despesa repetidos abortam lote. Item com campo obrigatório ausente/tipo inválido é recusado com DADO_INVALIDO; demais continuam. ID ausente gera id null e usa índice.
**Origem:** Entrada de referência define forma, mas não recuperação. Evidência: Caso adicional.
**Aceite AC-014:** Item valor string 60 recusa; próximo item válido paga normalmente. IDs repetidos abortam.

### RN-015 — Precedência e motivos
**Regra:** Aplicar a ordem da seção 8; emitir um motivo principal, avisos separados. Duplicatas podem referenciar item recusado.
**Origem:** Política contém regras sobrepostas. Evidência: d-013.
**Aceite AC-015:** Airbnb 690 sem nota: NOTA_FISCAL_OBRIGATORIA, sem consumir teto de hotel.

### RN-016 — Totais e status
**Regra:** Solicitado soma todos os valores positivos estruturalmente válidos arredondados, inclusive duplicatas/recusas; reembolsável soma pagamentos; não reembolsável é diferença. Valores negativos/zero ignorados não entram. Contagens particionam itens.
**Origem:** Schema de saída é definido pelo participante. Evidência: Todos os itens.
**Aceite AC-016:** Total de referência solicitado 1861,84; reembolsável 585,43; não reembolsável 1276,41.

### RN-017 — Contrato de execução
CLI aceita calcular --input <arquivo> --output <arquivo>. Sucesso retorna código 0; entrada/lote inválido retorna 2; falha de I/O retorna 3. Não misturar logs com resultado. Uma mesma entrada produz saída financeira idêntica, sem depender da hora de execução. **AC-017:** executar com exemplo grava JSON coerente e retorna 0; arquivo inexistente retorna 3; JSON inválido retorna 2.

### RN-018 — Estrutura da saída
Cada item gera exatamente um resultado; schema e invariantes da seção 4 são obrigatórios. **AC-018:** soma dos quatro status = total_itens = quantidade da entrada; soma pagamentos = total_reembolsavel; solicitado - reembolsável = não reembolsável; nenhum pagamento negativo ou maior que solicitado.

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
| Categoria em maiúscula com ID idêntico | ID repetido invalida lote antes das regras de item |
| Mesmo conteúdo, IDs diferentes | Segundo ignorado; comparação valor 54.90 = 54.9 |
| Mesmo conteúdo com fornecedor em caixa diferente | Não duplicata, pois fornecedor é exato |
| Valores 33,333 e 33,334, demais campos iguais | Não duplicatas, mesmo normalizando ambos a 33,33 |
| Canônico sem nota, repetição com nota | Canônico recusado; posterior ignorado; nenhum paga |
| Item inválido antes de cópia válida | Inválido não vira canônico; válido pode pagar |
| Despesa fora do mês e sem nota | FORA_DA_COMPETENCIA prevalece |
| Categoria desconhecida e sem nota | CATEGORIA_NAO_PREVISTA prevalece |
| Duas hospedagens com nota 200 + 100 na mesma data | 200 + 50; aviso de diárias em ambos |
| Dia inicial/final / um dia fora | Aceita/aceita/recusa |
| Campo booleano com valor "false" | DADO_INVALIDO |
| despesas vazia | Sucesso e totais zero |
| Período cruzando meses | Lote inválido nesta versão |

## 8. Ordem de aplicação das regras
1. Validar JSON e envelope; checar IDs repetidos válidos antes de avaliar itens. Falha aborta lote.
2. Validar campos de cada item. Inválido: RECUSADO/DADO_INVALIDO, solicitado zero; não participa da deduplicação.
3. Normalizar categoria e quantizar valor, preservar original. Identificar e registrar primeiro canônico pela chave RN-007, inclusive negativos e zeros. Repetição: IGNORADO/DUPLICATA, solicitado positivo continua no total.
4. Valor original negativo: IGNORADO/ESTORNO_NAO_PROCESSADO. Valor original zero ou positivo arredondado zero: IGNORADO/VALOR_ZERO.
5. Verificar competência; fora: RECUSADO/FORA_DA_COMPETENCIA.
6. Verificar categoria; desconhecida: RECUSADO/CATEGORIA_NAO_PREVISTA.
7. Verificar nota sobre valor original; falta obrigatória: RECUSADO/NOTA_FISCAL_OBRIGATORIA.
8. Aplicar somente teto base, conforme RN-005/RN-010; consumir saldo diário por categoria na ordem de entrada. Pagamento integral positivo: APROVADO/DENTRO_DO_LIMITE; entre zero e solicitado: PARCIAL/LIMITE_APLICADO; zero: RECUSADO/LIMITE_ESGOTADO.
9. Consolidar totais e avisos. Somente pagamentos consomem saldo; saldos não transitam entre datas/categorias.

## 9. Critérios de aceite
- [ ] AC-001 a AC-018 e casos de borda passam conforme decisões adotadas.
- [ ] Os 14 itens do exemplo geram a tabela e os totais da seção abaixo.
- [ ] Campos ausentes, erros fiscais e duplicatas não desaparecem da saída.
- [ ] JSON de entrada não muda de contrato para acomodar viagem/diárias.
- [ ] Nenhum conhecimento externo é necessário para calcular a saída.

### Resultado calculado do exemplo (sob esta proposta)
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

14 itens: 3 aprovados, 4 parciais, 5 recusados, 2 ignorados. Solicitado 1861,84; reembolsável 585,43; não reembolsável 1276,41. Esses números são derivados da proposta, não de um gabarito oficial ou execução de produto existente.

## 10. O que fica em aberto
nada em aberto 
