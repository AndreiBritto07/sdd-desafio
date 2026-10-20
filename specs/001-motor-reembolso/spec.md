# Spec: Motor de Cálculo de Reembolso

**Versão:** 0.2 · **Status:** proposta, pendente de aprovação oficial · **Data:** 2026-10-20

Esta versão é a base de `DECISIONS.md`, `tasks.md` e `plan.md`. As correções 70 a 75 são propostas pendentes de aprovação e valem como texto normativo somente após aprovação ou ajuste. A correção 69 (competência ausente ou inválida, datas inexistentes em `periodo` e incompatibilidade com o mês) e a mudança do Dia 2 continuam em aberto e não são presumidas. A versão 0.1 está no histórico do repositório.

## 1. Problema

O financeiro confere despesas manualmente contra uma política ambígua, gerando demora e decisões inconsistentes.

## 2. Objetivo

Calcular o reembolso de um colaborador em um período, explicando cada decisão e permitindo reconciliar os totais.

## 3. Fora de escopo

Não efetua pagamentos, não valida autenticidade de notas, não consulta sistemas externos, não autentica usuários, não mantém histórico entre execuções, não converte moedas, não oferece interface gráfica, não processa múltiplos colaboradores no mesmo lote, não reconcilia estornos, não infere viagens nem quantidade de diárias de texto livre. Sem comprovação estruturada de viagem, nenhum limite recebe o acréscimo de 50%. Essa é uma limitação assumida, não uma remoção silenciosa da política.

## 4. Entrada e saída

### 4.1 Entrada

| Campo | Tipo | Regra |
|---|---|---|
| `colaborador` | objeto | Obrigatório |
| `colaborador.id`, `nome`, `centro_custo` | texto não vazio | Obrigatórios; qualquer falha rejeita o lote com `ENTRADA_INVALIDA` |
| `periodo` | objeto | Obrigatório |
| `periodo.competencia` | texto `YYYY-MM` | Mês válido. Ausente ou inválido: correção 69 |
| `periodo.inicio`, `periodo.fim` | data `YYYY-MM-DD` | Datas reais. Inversão válida: RN-006. Data inexistente: correção 69 |
| `despesas` | lista | Obrigatória; pode estar vazia |
| `despesas[].id` | texto | Opcional. Ausente: gerado (RN-014). Presente, vazio ou só com espaços: `CAMPO_OBRIGATORIO` (correção 73). Tipo incorreto: `TIPO_OU_FORMATO_INVALIDO` |
| `despesas[].data` | data `YYYY-MM-DD` | Obrigatória. Data inexistente (ex.: 2026-02-30): `TIPO_OU_FORMATO_INVALIDO` (correção 74) |
| `despesas[].categoria` | texto não vazio | Obrigatória; normalização em RN-011 |
| `despesas[].descricao`, `fornecedor` | texto não vazio | Obrigatórios; sem normalização na saída (comparação em RN-007) |
| `despesas[].valor` | número decimal finito | Booleano e texto numérico não são aceitos |
| `despesas[].tem_nota_fiscal` | booleano | Somente `true` ou `false` |

Regras gerais de entrada:

- Chaves são exatas e sensíveis a maiúsculas. Campos extras, na raiz, no envelope ou nas despesas, são ignorados e não alteram cálculos.
- Em despesa, campo obrigatório ausente gera `CAMPO_OBRIGATORIO`. Campo vazio ou só com espaços gera `CAMPO_OBRIGATORIO`. Tipo ou formato incorreto gera `TIPO_OU_FORMATO_INVALIDO`. Em `colaborador`, qualquer falha rejeita o lote com `ENTRADA_INVALIDA`.
- Datas não têm hora nem fuso. Valores estão em reais. Não há limite artificial de itens nesta versão.

### 4.2 Saída de sucesso

Objeto com `versao_spec: "0.2"`, `colaborador`, `periodo` (já corrigido, se houve inversão), `avisos` (lista global de códigos), `items` (ordem original) e `resumo`. Índices são zero-based e contam todos os itens da entrada. Valores monetários têm duas casas decimais, exceto `valor_original`, que é preservado como recebido.

| Campo de `items[]` | Tipo | Significado |
|---|---|---|
| `indice` | inteiro ≥ 0 | Posição na lista original |
| `id` | texto ou `null` | Original preservado; gerado se ausente; `null` se presente e inválido |
| `valor_original` | número ou `null` | Valor recebido, se numericamente válido |
| `valor_solicitado` | número | Valor positivo arredondado para itens estruturalmente válidos com valor positivo; `0` para zero, negativo ou estrutura inválida |
| `categoria_normalizada` | texto ou `null` | Disponível quando a categoria foi lida |
| `valor_reembolsavel` | número | Pagamento calculado |
| `status` | enum | `APROVADO`, `PARCIAL`, `RECUSADO`, `IGNORADO` |
| `motivo` | enum | Motivo principal (seção 8) |
| `justificativa` | texto não vazio | Explicação humana coerente com o motivo |
| `duplicata_de_indice` | inteiro ou `null` | Índice do item canônico, quando aplicável |
| `avisos` | lista de códigos | `DIARIAS_NAO_INFORMADAS` em hospedagem estruturalmente válida |
| `erros` | lista de `{campo, codigo}` | Erros estruturais, na ordem fixa da seção 8. Vazia quando o item é estruturalmente válido |

**Motivos permitidos:** `DADO_INVALIDO`, `ID_REPETIDO`, `DUPLICATA`, `ESTORNO_NAO_PROCESSADO`, `VALOR_ZERO`, `FORA_DA_COMPETENCIA`, `CATEGORIA_NAO_PREVISTA`, `NOTA_FISCAL_OBRIGATORIA`, `LIMITE_ESGOTADO`, `LIMITE_APLICADO`, `DENTRO_DO_LIMITE`.

**Códigos de erro (campo `erros`):** `CAMPO_OBRIGATORIO`, `TIPO_OU_FORMATO_INVALIDO`.

**Resumo:**

- `total_itens`, `aprovados`, `parciais`, `recusados` e `ignorados` contam somente itens estruturalmente válidos. Isso inclui repetidos, duplicatas, zero e negativos.
- Itens estruturalmente inválidos ficam em `items` com `status: RECUSADO` e `motivo: DADO_INVALIDO`, mas não entram em `recusados` nem em `total_itens`.
- `total_solicitado`: soma de `valor_solicitado` dos itens com status `APROVADO` ou `PARCIAL` (correção 70).
- `total_reembolsavel`: soma de `valor_reembolsavel` dos mesmos itens.
- `total_nao_reembolsavel = total_solicitado − total_reembolsavel`. Cobre somente itens `APROVADO` e `PARCIAL`. Recusas e duplicatas não entram em nenhum total e são conciliadas item a item em `items` (correção 75).
- Lista vazia resulta em totais e contagens zero.
- `VIAGEM_NAO_INFORMADA` consta em `avisos` do envelope em todo sucesso, inclusive com lista vazia.

### 4.3 Falha de lote

Objeto `{versao_spec: "0.2", erro: {codigo, mensagem}}`, sem `items` nem `resumo`. Códigos: `JSON_INVALIDO`, `ENTRADA_INVALIDA`, `ERRO_IO`. Nenhuma saída financeira parcial é gravada em falha. `JSON_INVALIDO` e `ENTRADA_INVALIDA` (código de saída 2) gravam esse objeto em `--output`. `ERRO_IO` (código de saída 3) não grava arquivo de saída; a mensagem vai para stderr.

### 4.4 Exemplo de saída (alimentação de 61,00 com nota)

```json
{"versao_spec":"0.2","colaborador":{"id":"c-1","nome":"Exemplo","centro_custo":"CC"},"periodo":{"competencia":"2026-07","inicio":"2026-07-01","fim":"2026-07-31"},"avisos":["VIAGEM_NAO_INFORMADA"],"items":[{"indice":0,"id":"x-1","valor_original":61.00,"valor_solicitado":61.00,"categoria_normalizada":"alimentacao","valor_reembolsavel":60.00,"status":"PARCIAL","motivo":"LIMITE_APLICADO","justificativa":"Aplicado limite diário de R$ 60,00.","duplicata_de_indice":null,"avisos":[],"erros":[]}],"resumo":{"total_itens":1,"aprovados":0,"parciais":1,"recusados":0,"ignorados":0,"total_solicitado":61.00,"total_reembolsavel":60.00,"total_nao_reembolsavel":1.00}}
```

## 5. Regras de negócio

**RN-001 — Agregação diária.** Somar por colaborador, data e categoria. Limites: alimentação R$ 60; transporte R$ 80.
Origem: "Alimentação tem limite de R$ 60 por dia." Evidência: d-001/d-002.
**AC-001:** 72,50 + 38,00 no mesmo dia → 60,00 e 0,00.

**RN-002 — Distribuição do teto.** Consumir o saldo pela ordem dos itens no arquivo. Itens recusados, ignorados ou inválidos não consomem saldo.
Origem: "Despesas acima do limite são reembolsadas parcialmente." Evidência: d-001/d-002.
**AC-002:** 38,00 antes de 72,50 → 38,00 e 22,00; total 60,00.

**RN-003 — Fronteira do limite.** Reembolsar o mínimo entre o valor normalizado e o saldo disponível. Igualdade ao teto é aprovação integral. Saldo zero recusa com `LIMITE_ESGOTADO`. Evidência: d-014.
**AC-003:** alimentação de 59,99 / 60,00 / 60,01 → paga 59,99 / 60,00 / 60,00.

**RN-004 — Obrigatoriedade fiscal.** Exigir nota quando o valor original positivo, antes de arredondar e limitar, for estritamente maior que R$ 100. Verificação por item. Evidência: d-003/d-004/d-013.
**AC-004:** 100,00 sem nota pode pagar até o teto; 100,01 sem nota é recusado com `NOTA_FISCAL_OBRIGATORIA`.

**RN-005 — Viagem sem campo.** Não inferir viagem de descrição, hotel, aeroporto ou centro de custo. Não aplicar acréscimo. Emitir `VIAGEM_NAO_INFORMADA`. Evidência: d-003/d-010/d-011.
**AC-005:** corrida de aeroporto de 100,00 continua limitada a 80; hotel de 480 continua limitado a 250.

**RN-006 — Competência e período.** Usar a data da despesa. Aceitar `inicio <= data <= fim`. Se `inicio` e `fim` forem datas válidas e estiverem invertidas, trocá-las e devolver o período corrigido. As datas devem pertencer ao mês de competência. Competência ausente ou inválida, datas inexistentes em `periodo` e incompatibilidade com o mês (exceto inversão) dependem da **correção 69**, em aberto. Evidência: d-008/d-014.
**AC-006:** 2026-04-15 é recusado com `FORA_DA_COMPETENCIA`; 2026-07-01 e 2026-07-31 são aceitos em julho.
**AC-021:** período com inversão válida é corrigido e o período corrigido aparece na saída.

**RN-007 — Identificação de duplicatas.**

1. Validar a estrutura antes de qualquer deduplicação.
2. ID: remover espaços ASCII das extremidades e comparar sem diferenciar maiúsculas. A primeira ocorrência estruturalmente válida é mantida. A posterior é `RECUSADO` com motivo `ID_REPETIDO` e `erros` vazio, e o lote continua. Itens com estrutura inválida não reservam ID.
3. Conteúdo, somente entre IDs diferentes e apenas para itens com valor positivo (correção 72): data normalizada, categoria normalizada, fornecedor e descrição (NFC, trim ASCII externo, sem diferença de caixa) e valor arredondado a duas casas (RN-009). Não comparar `tem_nota_fiscal` nem campos extras.
4. O primeiro item válido com esse conteúdo é canônico, mesmo que seja recusado por regra de negócio. Os posteriores são `IGNORADO` com motivo `DUPLICATA`, reembolso zero e `duplicata_de_indice` apontando para o canônico.

Evidência: d-006/d-007.
**AC-007:** d-006 paga 54,90; d-007 é `IGNORADO` com `duplicata_de_indice: 5`.

**RN-008 — Estorno e valor zero.** Valor negativo: `IGNORADO` com motivo `ESTORNO_NAO_PROCESSADO`. Valor zero (original ou após arredondamento): `IGNORADO` com motivo `VALOR_ZERO`. Ambos com reembolso zero e sem compensação. Não entram na deduplicação (correção 72). Evidência: d-009.
**AC-008:** −45,00 paga 0 e não altera o saldo nem o total solicitado.

**RN-009 — Precisão monetária.** Arredondar cada valor positivo a duas casas, metade para cima. Totalizar os valores já arredondados. Manter o valor original na saída. Evidência: d-011.
**AC-009:** 33,333 → 33,33; 33,335 → 33,34; 0,004 → 0,00, ignorado por `VALOR_ZERO`.

**RN-010 — Diárias de hospedagem.** Não extrair número de diárias de texto livre. Considerar uma diária por data informada, compartilhada por todas as hospedagens do mesmo colaborador e data. Limite de R$ 250 por diária. Sinalizar `DIARIAS_NAO_INFORMADAS` em cada hospedagem estruturalmente válida. Evidência: d-010/d-013.
**AC-010:** hotel de 480 com descrição "2 diárias" paga 250; Airbnb de 690 sem nota paga 0.

**RN-011 — Categoria.** Remover espaços ASCII das extremidades e converter A-Z para a-z, somente no campo `categoria`. Aceitos: `alimentacao`, `transporte_urbano`, `hospedagem`. Não remover acentos e não criar aliases. Categoria vazia ou só com espaços: `CAMPO_OBRIGATORIO`. Categoria fora do vocabulário: `CATEGORIA_NAO_PREVISTA`. Evidência: d-014/d-005.
**AC-011:** `ALIMENTACAO` e `Alimentacao` são tratadas como `alimentacao`; `alimentação` e `coworking` são `CATEGORIA_NAO_PREVISTA`.

**RN-012 — Fim de semana.** Aplicar as regras em todos os dias civis, inclusive sábados, domingos e feriados. Evidência: d-012.
**AC-012:** sábado 2026-07-18, alimentação de 47,20, paga 47,20.

**RN-013 — Chaves e campos extras.** Chaves exatas. `tem_nota_fiscal` é obrigatório e booleano real. Aliases não substituem campos. Campos extras são ignorados.
**AC-013:** `temNotaFiscal` sem `tem_nota_fiscal` invalida o item com `CAMPO_OBRIGATORIO`; `false` é válido; `"false"` não é (`TIPO_OU_FORMATO_INVALIDO`).

**RN-014 — Falhas de entrada.**

- JSON inválido ou chave repetida em qualquer objeto: `JSON_INVALIDO`, lote rejeitado sem resultado parcial.
- Envelope inválido ou campo obrigatório de `colaborador` ausente, vazio ou de tipo incorreto: `ENTRADA_INVALIDA`, lote rejeitado.
- Despesa: registrar todos os erros estruturais na ordem fixa da seção 8, recusar uma vez com `RECUSADO` e motivo `DADO_INVALIDO`, e continuar o lote.
- ID ausente: gerar `gerado-{índice}`, com o índice zero-based da lista completa. Em colisão com qualquer ID fornecido ou já gerado (normalizado), usar `gerado-{índice}-1`, `-2` etc.
- ID presente inválido: `id: null`, sem substituto gerado.

**AC-014:** item com valor `"60"` é recusado e o próximo item é processado; ID repetido recusa somente a ocorrência posterior com motivo `ID_REPETIDO`; colaborador incompleto rejeita o lote com `ENTRADA_INVALIDA`.
**AC-019:** JSON com chave repetida em qualquer objeto rejeita o lote com `JSON_INVALIDO`, sem resultado financeiro parcial.
**AC-020:** colaborador incompleto (ausente, vazio, só espaços ou tipo incorreto em qualquer campo obrigatório) rejeita o lote com `ENTRADA_INVALIDA`.

**RN-015 — Precedência e motivos.** Aplicar a ordem da seção 8. Emitir um motivo principal por item. Avisos globais (`VIAGEM_NAO_INFORMADA`) ficam em `avisos` do envelope. Avisos de hospedagem (`DIARIAS_NAO_INFORMADAS`) ficam em `items[].avisos`. Duplicatas podem referenciar item recusado.
**AC-015:** Airbnb de 690 sem nota recebe `NOTA_FISCAL_OBRIGATORIA` e não consome o teto de hospedagem.

**RN-016 — Totais e status.** Ver seção 4.2 (correção 70 e escopo da correção 75). Contagens particionam os itens estruturalmente válidos.
**AC-016:** o resumo exclui recusados, duplicatas, ignorados e itens estruturalmente inválidos dos totais financeiros.

**RN-017 — Contrato de execução (CLI).** `calcular --input <arquivo> --output <arquivo>`. Código `0` para sucesso, `2` para entrada ou lote inválido, `3` para erro de I/O. Logs ficam fora do JSON de resultado. A mesma entrada produz a mesma saída financeira.
**AC-017:** exemplo válido grava JSON e retorna `0`; arquivo inexistente retorna `3`; JSON inválido retorna `2`; duas execuções com a mesma entrada produzem a mesma saída financeira.

**RN-018 — Estrutura e invariantes.** Cada item válido gera exatamente um objeto em `items`. Itens estruturalmente inválidos permanecem em `items`, mas ficam fora de contagens e totais.
**AC-018:** soma das contagens = `total_itens`; soma dos pagamentos = `total_reembolsavel`; `total_solicitado − total_reembolsavel = total_nao_reembolsavel`; nenhum pagamento é negativo nem maior que o valor solicitado.

## 6. Ambiguidades e decisões

O detalhamento de cada decisão, com justificativa e teste, está em `DECISIONS.md`.

| AMB | Tema | Regra | AC |
|---|---|---|---|
| AMB-001 | Agregação diária | RN-001 | AC-001 |
| AMB-002 | Distribuição do teto | RN-002 | AC-002 |
| AMB-003 | Fronteira do limite | RN-003 | AC-003 |
| AMB-004 | Obrigatoriedade fiscal | RN-004 | AC-004 |
| AMB-005 | Viagem sem campo | RN-005 | AC-005 |
| AMB-006 | Competência | RN-006 | AC-006, AC-021 |
| AMB-007 | Duplicatas | RN-007 | AC-007, AC-014 |
| AMB-008 | Estorno e valor zero | RN-008 | AC-008 |
| AMB-009 | Precisão monetária | RN-009 | AC-009 |
| AMB-010 | Diárias | RN-010 | AC-010 |
| AMB-011 | Categoria | RN-011 | AC-011 |
| AMB-012 | Fim de semana | RN-012 | AC-012 |
| AMB-013 | Chaves | RN-013 | AC-013 |
| AMB-014 | Falhas de entrada | RN-014 | AC-014, AC-019, AC-020 |
| AMB-015 | Precedência | RN-015 | AC-015 |
| AMB-016 | Totais e status | RN-016, RN-018 | AC-016, AC-018 |

## 7. Casos de borda

| Caso | Resultado |
|---|---|
| Teto exato e um centavo acima | Integral no teto; parcial acima |
| Nota `false`: 99,99 / 100,00 / 100,01 | Sem bloqueio / sem bloqueio / `NOTA_FISCAL_OBRIGATORIA` |
| 100,004 sem nota | Recusa fiscal (valor original positivo acima de 100) |
| 33,335 e 33,333 | 33,34 e 33,33 |
| Duas despesas de 30,005 no mesmo dia | 30,01 + 29,99 = 60,00 |
| Valores −45, 0 e 0,004 | Ignorados; não consomem teto |
| `Alimentacao`, `ALIMENTACAO`, `alimentacao` | Mesma categoria |
| `" alimentacao "` | Aceito após trim ASCII |
| `alimentação`, `transporteUrbano` | `CATEGORIA_NAO_PREVISTA` |
| ID repetido após trim e sem diferença de caixa | Segunda ocorrência `RECUSADO` com motivo `ID_REPETIDO`; lote continua |
| Mesmo conteúdo, IDs diferentes | Segundo `IGNORADO` com motivo `DUPLICATA` |
| Fornecedor com caixa diferente | Duplicata após NFC, trim e sem diferença de caixa |
| Valores 10,004 e 10,00, demais campos iguais | Duplicata (comparação após arredondamento) |
| Canônico sem nota, repetição com nota | Canônico `RECUSADO`; repetição `IGNORADO`; nada é pago |
| Item inválido antes de cópia válida | Inválido não é canônico; a cópia válida pode pagar |
| Zero antes de valor positivo igual | Zero não é canônico (correção 72) |
| Despesa fora do mês e sem nota | `FORA_DA_COMPETENCIA` prevalece |
| Categoria desconhecida e sem nota | `CATEGORIA_NAO_PREVISTA` prevalece |
| Duas hospedagens de 200 + 100 na mesma data | 200 + 50; aviso em ambas |
| Campo booleano com valor `"false"` | `TIPO_OU_FORMATO_INVALIDO` |
| Data de despesa `2026-02-30` | `TIPO_OU_FORMATO_INVALIDO` (correção 74) |
| `despesas` vazia | Sucesso com totais zero |
| Datas inicial e final invertidas e válidas | Trocar e devolver o período corrigido |

## 8. Ordem de aplicação (precedência)

1. Parsing JSON estrito. Chave repetida ou JSON inválido: `JSON_INVALIDO`, lote rejeitado.
2. Envelope e colaborador. Falha: `ENTRADA_INVALIDA`, lote rejeitado.
3. Período (RN-006). Inverter datas válidas e devolver o período corrigido. Demais casos dependem da correção 69.
4. Coletar todos os IDs fornecidos, normalizados, inclusive os de itens inválidos. Essa coleta serve somente para evitar colisão com IDs gerados. Não reserva ID para deduplicação (RN-007.2).
5. Gerar IDs ausentes (RN-014). ID presente inválido: `id: null`.
6. Validar a estrutura de cada despesa em ordem fixa: `id`; depois os campos obrigatórios na ordem da seção 4.1; depois os opcionais. Registrar todos os erros em `erros`. Item inválido: `RECUSADO` com motivo `DADO_INVALIDO`, fora de contagens e totais, sem reservar ID.
7. ID repetido (somente itens estruturalmente válidos): ocorrência posterior `RECUSADO` com motivo `ID_REPETIDO` e `erros` vazio.
8. Zero e negativo: `IGNORADO` com motivo `VALOR_ZERO` ou `ESTORNO_NAO_PROCESSADO`. Não entram na deduplicação (correção 72).
9. Duplicata por conteúdo (itens com valor positivo e IDs não repetidos): `IGNORADO` com motivo `DUPLICATA`, apontando para o canônico (primeiro válido com esse conteúdo, mesmo que depois seja recusado).
10. Competência: `FORA_DA_COMPETENCIA`.
11. Categoria: `CATEGORIA_NAO_PREVISTA`.
12. Nota fiscal: `NOTA_FISCAL_OBRIGATORIA`.
13. Limites diários, na ordem de entrada: `LIMITE_ESGOTADO` (saldo zero), `LIMITE_APLICADO` (parcial) ou `DENTRO_DO_LIMITE`.
14. Resumo (seção 4.2). Ordem original de `items` preservada.

## 9. Critérios de aceite

- [ ] AC-001 a AC-021 associados a testes automatizados identificáveis (seção 11). Nenhum critério é marcado como validado antes da execução e aprovação.
- [ ] Os 14 itens do exemplo geram os resultados da tabela abaixo. São valores esperados da proposta, não gabarito oficial.
- [ ] Campos ausentes, erros fiscais e duplicatas não desaparecem da saída.
- [ ] O contrato de entrada não muda para acomodar viagem ou diárias.

### Resultado esperado do exemplo (proposta; não validado por execução)

| Item | Solicitado | Reembolsável | Status | Motivo |
|---|---:|---:|---|---|
| d-001 | 72,50 | 60,00 | PARCIAL | LIMITE_APLICADO |
| d-002 | 38,00 | 0,00 | RECUSADO | LIMITE_ESGOTADO |
| d-003 | 100,00 | 80,00 | PARCIAL | LIMITE_APLICADO |
| d-004 | 100,01 | 0,00 | RECUSADO | NOTA_FISCAL_OBRIGATORIA |
| d-005 | 89,00 | 0,00 | RECUSADO | CATEGORIA_NAO_PREVISTA |
| d-006 | 54,90 | 54,90 | APROVADO | DENTRO_DO_LIMITE |
| d-007 | 54,90 | 0,00 | IGNORADO | DUPLICATA (índice 5) |
| d-008 | 41,00 | 0,00 | RECUSADO | FORA_DA_COMPETENCIA |
| d-009 | 0,00 | 0,00 | IGNORADO | ESTORNO_NAO_PROCESSADO |
| d-010 | 480,00 | 250,00 | PARCIAL | LIMITE_APLICADO |
| d-011 | 33,33 | 33,33 | APROVADO | DENTRO_DO_LIMITE |
| d-012 | 47,20 | 47,20 | APROVADO | DENTRO_DO_LIMITE |
| d-013 | 690,00 | 0,00 | RECUSADO | NOTA_FISCAL_OBRIGATORIA |
| d-014 | 61,00 | 60,00 | PARCIAL | LIMITE_APLICADO |

Contagens: 3 aprovados, 4 parciais, 5 recusados, 2 ignorados (total 14).
`total_solicitado` = 848,93 (APROVADO + PARCIAL). `total_reembolsavel` = 585,43. `total_nao_reembolsavel` = 263,50.

## 10. Em aberto

- **Correção 69:** competência ausente ou inválida, datas inexistentes em `periodo` e incompatibilidade com o mês. Não implementar política definitiva até a decisão.
- **Correções 70 a 75:** propostas pendentes de aprovação (ver `DECISIONS.md`).
- **Dia 2:** requisito ainda não recebido. Revisar regras e testes quando chegar.
- **Evidências d-001 a d-014:** o conjunto de dados de referência precisa ser confirmado em `exemplos/` antes da execução.
- **Testes:** nenhum teste é marcado como validado sem execução real.

## 11. Rastreabilidade

| Critério | Regra | Tarefa(s) | Teste(s) |
|---|---|---|---|
| AC-001 | RN-001 | T-021 | `test_agregacao_diaria_alimentacao` |
| AC-002 | RN-002 | T-021 | `test_distribuicao_teto_ordem_entrada` |
| AC-003 | RN-003 | T-021 | `test_fronteira_limite_alimentacao` |
| AC-004 | RN-004 | T-019 | `test_nota_fiscal_acima_de_100` |
| AC-005 | RN-005 | T-022 | `test_viagem_nao_aplica_acrescimo` |
| AC-006 | RN-006 | T-015 | `test_competencia_inclusiva` |
| AC-007 | RN-007 | T-016, T-017 | `test_duplicata_aponta_canonico`, `test_duplicata_conteudo_com_ids_diferentes` |
| AC-008 | RN-008 | T-013 | `test_estorno_nao_processado` |
| AC-009 | RN-009 | T-011, T-013 | `test_arredondamento_half_up` |
| AC-010 | RN-010 | T-023 | `test_diarias_nao_extraidas_do_texto` |
| AC-011 | RN-011 | T-012, T-020 | `test_normalizacao_categoria`, `test_categoria_nao_prevista_recusa` |
| AC-012 | RN-012 | T-020 | `test_fim_de_semana_aplica_regras` |
| AC-013 | RN-013 | T-005, T-007 | `test_chaves_exatas_e_booleano` |
| AC-014 | RN-014 | T-006, T-008, T-009, T-010 | `test_entrada_invalida_por_item`, `test_id_repetido_recusa_somente_ocorrencia_posterior` |
| AC-015 | RN-015 | T-018 | `test_precedencia_motivos` |
| AC-016 | RN-016 | T-024, T-026 | `test_totais_excluem_nao_elegiveis` |
| AC-017 | RN-017 | T-028, T-029 | `test_cli_codigos_de_saida`, `test_mesma_entrada_mesma_saida` |
| AC-018 | RN-018 | T-025, T-026 | `test_invariantes_financeiros` |
| AC-019 | RN-014 | T-003 | `test_chave_json_repetida_rejeita_lote` |
| AC-020 | RN-014 | T-004 | `test_colaborador_incompleto_rejeita_lote` |
| AC-021 | RN-006 | T-014 | `test_periodo_invertido_e_corrigido` |

A coluna Teste(s) lista os testes principais. A lista completa de testes por AC está em `tasks.md`, que é a fonte de T-031. Os nomes de teste são propostos e devem ser confirmados na suíte real. Todas as AMB têm ao menos um AC vinculado.