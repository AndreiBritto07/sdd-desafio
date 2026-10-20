# Decisões do motor de reembolso

**Versão do registro:** 0.2, alinhada a `spec.md` v0.2. Os documentos têm versionamento independente; a versão 0.2 de cada um corresponde a esta revisão.
**Data:** 2026-10-20
**Estado:** propostas pendentes de aprovação oficial. Nenhuma decisão aqui equivale a aprovação do participante.

Cada decisão indica a regra (RN), o critério de aceite (AC) e o teste automatizado. Vínculos não confirmados na suíte real ficam como "pendente".

## Índice

| AMB | Tema | RN | AC | Teste(s) | Evidência |
|---|---|---|---|---|---|
| AMB-001 | Agregação diária | RN-001 | AC-001 | `test_agregacao_diaria_alimentacao` | d-001/d-002 |
| AMB-002 | Distribuição do teto | RN-002 | AC-002 | `test_distribuicao_teto_ordem_entrada` | d-001/d-002 |
| AMB-003 | Fronteira do limite | RN-003 | AC-003 | `test_fronteira_limite_alimentacao` | d-014 |
| AMB-004 | Obrigatoriedade fiscal | RN-004 | AC-004 | `test_nota_fiscal_acima_de_100` | d-003/d-004/d-013 |
| AMB-005 | Viagem sem campo | RN-005 | AC-005 | `test_viagem_nao_aplica_acrescimo` | d-003/d-010/d-011 |
| AMB-006 | Competência | RN-006 | AC-006, AC-021 | `test_competencia_inclusiva`, `test_periodo_invertido_e_corrigido` | d-008/d-014 |
| AMB-007 | Duplicatas | RN-007 | AC-007, AC-014 | `test_duplicata_aponta_canonico`, `test_id_repetido_recusa_somente_ocorrencia_posterior` | d-006/d-007 |
| AMB-008 | Estorno e valor zero | RN-008 | AC-008 | `test_estorno_nao_processado` | d-009 |
| AMB-009 | Precisão monetária | RN-009 | AC-009 | `test_arredondamento_half_up` | d-011 |
| AMB-010 | Diárias | RN-010 | AC-010 | `test_diarias_nao_extraidas_do_texto` | d-010/d-013 |
| AMB-011 | Categoria | RN-011 | AC-011 | `test_normalizacao_categoria` | d-014/d-005 |
| AMB-012 | Fim de semana | RN-012 | AC-012 | `test_fim_de_semana_aplica_regras` | d-012 |
| AMB-013 | Chaves | RN-013 | AC-013 | `test_chaves_exatas_e_booleano` | Caso adicional |
| AMB-014 | Falhas de entrada | RN-014 | AC-014, AC-019, AC-020 | `test_entrada_invalida_por_item`, `test_chave_json_repetida_rejeita_lote`, `test_colaborador_incompleto_rejeita_lote` | Caso adicional |
| AMB-015 | Precedência | RN-015 | AC-015 | `test_precedencia_motivos` | d-013 |
| AMB-016 | Totais e status | RN-016, RN-018 | AC-016, AC-018 | `test_totais_excluem_nao_elegiveis`, `test_invariantes_financeiros` | Todos os itens |

## Decisões

**AMB-001 — Agregação diária.** Texto: "Alimentação tem limite de R$ 60 por dia." Dúvida: por item ou por dia?
Decisão: somar por colaborador, data e categoria. Alimentação R$ 60; transporte R$ 80.
Justificativa: impedir que o teto seja multiplicado pelo número de comprovantes.

**AMB-002 — Distribuição do teto.** Texto: "Despesas acima do limite são reembolsadas parcialmente." Dúvida: rateio ou prioridade?
Decisão: consumir o saldo na ordem dos itens no arquivo. Itens recusados, ignorados ou inválidos não consomem saldo.
Justificativa: distribuição simples, auditável e determinística.

**AMB-003 — Fronteira do limite.** Dúvida: igual ao teto é parcial?
Decisão: reembolsar o mínimo entre o valor normalizado e o saldo disponível. Igualdade é aprovação integral. Saldo zero recusa com `LIMITE_ESGOTADO`.
Justificativa: cortar somente o excedente.

**AMB-004 — Obrigatoriedade fiscal.** Texto: "Nota fiscal é obrigatória acima de R$ 100." Dúvida: 100,00 exige nota? Sobre o valor original ou o reembolsável?
Decisão: exigir nota quando o valor original positivo, antes de arredondar e limitar, for estritamente maior que R$ 100. Verificação por item.
Justificativa: impedir que teto ou arredondamento dispensem comprovante obrigatório.

**AMB-005 — Viagem sem campo.** Texto: "Colaborador em viagem tem limites ampliados em 50%." Dúvida: como comprovar viagem sem atributo?
Decisão: não inferir viagem de descrição, hotel, aeroporto ou centro de custo. Não aplicar acréscimo. Emitir `VIAGEM_NAO_INFORMADA` em `avisos` do envelope.
Justificativa: evitar concessão sem informação verificável. A restrição é explícita e pode ser revisada.

**AMB-006 — Competência.** Texto: "Despesas devem ser lançadas dentro do período de competência." Dúvida: data do gasto ou do lançamento? Limites são inclusivos?
Decisão: usar a data da despesa e aceitar `inicio <= data <= fim`. Se início e fim forem datas válidas e estiverem invertidas, trocá-las e devolver o período corrigido. Competência ausente ou inválida, datas inexistentes em `periodo` e incompatibilidade com o mês: correção 69, em aberto.
Justificativa: não existe data de lançamento; não inventar um campo.

**AMB-007 — Duplicatas.** Texto: "Duplicatas devem ser tratadas." Dúvida: por ID ou por conteúdo? Qual item permanece?
Decisão: primeiro verificar ID repetido (trim ASCII e sem diferença de caixa). A ocorrência posterior é `RECUSADO` com motivo `ID_REPETIDO` e `erros` vazio. Depois, comparar conteúdo somente entre IDs diferentes e somente para valores positivos (correção 72). O primeiro válido com o mesmo conteúdo é canônico, mesmo que seja recusado depois. As cópias são `IGNORADO` com motivo `DUPLICATA` e apontam para o canônico.
Justificativa: IDs diferentes não impedem duplicidade, e não se escolhe silenciosamente o comprovante mais favorável. Repetição de ID depende do lote, por isso é motivo e não erro estrutural.

**AMB-008 — Estorno e valor zero.** Texto: a entrada de exemplo contém valor negativo; a política não esclarece. Dúvida: abater ou recusar?
Decisão: negativo: `IGNORADO` com `ESTORNO_NAO_PROCESSADO`. Zero (original ou após arredondamento): `IGNORADO` com `VALOR_ZERO`. Reembolso zero, sem compensação.
Justificativa: não há vínculo com a despesa original para conciliação segura.

**AMB-009 — Precisão monetária.** Texto: a entrada inclui 33.333. Dúvida: rejeitar ou arredondar? Quando?
Decisão: arredondar cada valor positivo a duas casas, metade para cima. Totalizar valores já arredondados. Manter o original na saída.
Justificativa: resultados monetários consistentes e auditáveis.

**AMB-010 — Diárias.** Texto: "Hospedagem tem limite de R$ 250 por diária." Dúvida: como obter a quantidade quando ausente?
Decisão: não extrair números de texto livre. Uma diária por data informada, compartilhada pelas hospedagens do mesmo colaborador e data. Sinalizar `DIARIAS_NAO_INFORMADAS` em `items[].avisos`.
Justificativa: evitar interpretação frágil de descrições.

**AMB-011 — Categoria.** Texto: "Categorias fora da política não são reembolsáveis." Dúvida: `ALIMENTACAO` equivale a `alimentacao`?
Decisão: trim ASCII e A-Z para a-z somente no campo `categoria`. Aceitos: `alimentacao`, `transporte_urbano`, `hospedagem`. Sem remoção de acentos e sem aliases.
Justificativa: resolver a variação de caixa sem ampliar o vocabulário.

**AMB-012 — Fim de semana.** Texto: a política não restringe dias úteis. Dúvida: plantão em sábado pode ser reembolsado?
Decisão: aplicar as regras a todos os dias civis, inclusive fins de semana e feriados.
Justificativa: não criar restrição ausente da política.

**AMB-013 — Chaves.** Texto: "Respeite o formato da entrada." Dúvida: `temNotaFiscal` e `TEM_NOTA_FISCAL` são aliases?
Decisão: chaves exatas e sensíveis a maiúsculas. `tem_nota_fiscal` é obrigatório e booleano real: ausente gera `CAMPO_OBRIGATORIO`; `"false"` gera `TIPO_OU_FORMATO_INVALIDO`. Aliases não substituem campos. Campos extras são ignorados.
Justificativa: separar a normalização de valores de uma mudança de contrato.

**AMB-014 — Falhas de entrada.** Dúvida: um item inválido aborta o lote? Como tratar IDs ausentes, presentes inválidos e repetidos?
Decisão: JSON inválido ou chave repetida: `JSON_INVALIDO`. Envelope ou colaborador incompleto: `ENTRADA_INVALIDA`. Despesa estruturalmente inválida: `RECUSADO` com motivo `DADO_INVALIDO`, erros em ordem fixa, e o lote continua. ID ausente: `gerado-{índice}`, com desvio em colisão. ID presente inválido: `null`, sem substituto. ID repetido: somente a ocorrência posterior, `RECUSADO` com motivo `ID_REPETIDO`.
Justificativa: comportamento determinístico, sem saída parcial em erro de lote e sem perda de despesas válidas por causa de um ID repetido.

**AMB-015 — Precedência e motivos.** Texto: "A política contém regras sobrepostas." Dúvida: qual motivo prevalece?
Decisão: aplicar a ordem da seção 8 da spec. Um motivo principal por item. Avisos globais em `avisos` do envelope; avisos de hospedagem em `items[].avisos`.
Justificativa: evitar resultados que dependam de verificações implícitas.

**AMB-016 — Totais e status.** Dúvida: quais itens entram em contagens e totais?
Decisão: `total_itens` e contagens incluem itens estruturalmente válidos, inclusive repetidos, duplicatas, zero e negativos. Itens estruturalmente inválidos ficam fora. `total_solicitado` soma `valor_solicitado` apenas de `APROVADO` e `PARCIAL` (correção 70). `total_reembolsavel` soma os pagamentos. `total_nao_reembolsavel = total_solicitado − total_reembolsavel`.
Justificativa: permitir reconciliação entre o que foi aprovado e o que foi pago. A conciliação de recusas e duplicatas é feita item a item (correção 75).

## Correções

| Nº | Decisão | Relação | Estado |
|---:|---|---|---|
| 69 | Competência ausente ou inválida, datas inexistentes em `periodo` e incompatibilidade com o mês. Inversão válida já está decidida (RN-006) | RN-006, AC-006 | **Em aberto** (não decidida) |
| 70 | `total_solicitado` soma só `APROVADO` e `PARCIAL`. Reproduz 848,93 do exemplo | RN-016, AC-016 | Proposta pendente |
| 71 | Precedência explícita: estrutura → ID repetido → zero/negativo → duplicata → competência → categoria → nota → limite | RN-015, AC-015 | Proposta pendente |
| 72 | Zero e negativo nunca são canônicos nem entram na deduplicação por conteúdo | RN-007, RN-008 | Proposta pendente |
| 73 | Campo obrigatório vazio ou só com espaços gera `CAMPO_OBRIGATORIO`. Tipo ou formato incorreto gera `TIPO_OU_FORMATO_INVALIDO`. Vale para `id` presente vazio ou só com espaços | RN-011, RN-014 | Proposta pendente |
| 74 | Data inexistente em despesa (ex.: 2026-02-30) é `TIPO_OU_FORMATO_INVALIDO`. Não se confunde com a correção 69, que trata o período | RN-014 | Proposta pendente |
| 75 | Escopo dos totais: `total_solicitado`, `total_reembolsavel` e `total_nao_reembolsavel` cobrem só `APROVADO` e `PARCIAL`. Recusas e duplicatas são conciliadas item a item, sem novo campo | RN-016, RN-018 | Proposta pendente |

Dia 2: requisito ainda não recebido. Revisar `spec.md`, `DECISIONS.md` e `tasks.md` quando chegar.