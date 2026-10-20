# Decisões do motor de reembolso

Registro das ambiguidades (AMB) identificadas na spec v0.2 e das decisões tomadas para cada uma. Cada decisão referencia a regra (RN) correspondente e a evidência usada.

## Índice

| AMB | Tema | Regra | Evidência |
|---|---|---|---|
| AMB-001 | Agregação diária | RN-001 | d-001/d-002 |
| AMB-002 | Distribuição do teto | RN-002 | d-001/d-002 |
| AMB-003 | Fronteira do limite | RN-003 | d-014 |
| AMB-004 | Obrigatoriedade fiscal | RN-004 | d-003/d-004/d-013 |
| AMB-005 | Viagem sem campo | RN-005 | d-003/d-010/d-011 |
| AMB-006 | Competência | RN-006 | d-008/d-014 |
| AMB-007 | Identificação de duplicatas | RN-007 | d-006/d-007 |
| AMB-008 | Estorno | RN-008 | d-009 |
| AMB-009 | Precisão monetária | RN-009 | d-011 |
| AMB-010 | Quantidade de diárias | RN-010 | d-010/d-013 |
| AMB-011 | Capitalização de valores | RN-011 | d-014/d-005 |
| AMB-012 | Fim de semana | RN-012 | d-012 |
| AMB-013 | Capitalização de chaves | RN-013 | Caso adicional solicitado |
| AMB-014 | Falhas de entrada | RN-014 | Caso adicional |
| AMB-015 | Precedência e motivos | RN-015 | d-013 |
| AMB-016 | Totais e status | RN-016 | Todos os itens |

---

## AMB-001 — Agregação diária

- **Texto original:** Alimentação tem limite de R$ 60 por dia.
- **Dúvida:** Por item ou soma diária?
- **Decisão:** Somar por colaborador, data e categoria. Alimentação: R$ 60. Transporte: R$ 80.
- **Justificativa:** Impedir multiplicação do teto pelo número de comprovantes.
- **Regra:** RN-001. **Evidência:** d-001/d-002.

## AMB-002 — Distribuição do teto

- **Texto original:** Despesas acima do limite são reembolsadas parcialmente.
- **Dúvida:** Rateio ou prioridade?
- **Decisão:** Consumir o saldo pela ordem dos itens no arquivo. Itens recusados ou ignorados não consomem saldo.
- **Justificativa:** Distribuição simples, auditável e determinística.
- **Regra:** RN-002. **Evidência:** d-001/d-002.

## AMB-003 — Fronteira do limite

- **Texto original:** Despesas acima do limite são reembolsadas parcialmente.
- **Dúvida:** Igual ao teto é parcial?
- **Decisão:** Reembolsar o mínimo entre o valor normalizado e o saldo disponível. Igualdade é aprovação integral. Saldo zero recusa.
- **Justificativa:** Cortar somente o excedente.
- **Regra:** RN-003. **Evidência:** d-014.

## AMB-004 — Obrigatoriedade fiscal

- **Texto original:** Nota fiscal é obrigatória acima de R$ 100.
- **Dúvida:** R$ 100,00 exige nota? Sobre o valor original ou o reembolsável?
- **Decisão:** Exigir nota quando o valor original positivo, antes de arredondar e limitar, for estritamente maior que R$ 100. A verificação é feita por item.
- **Justificativa:** Impedir que teto ou arredondamento dispensem comprovante obrigatório.
- **Regra:** RN-004. **Evidência:** d-003/d-004/d-013.

## AMB-005 — Viagem sem campo

- **Texto original:** Colaborador em viagem tem limites ampliados em 50%.
- **Dúvida:** Como comprovar viagem sem atributo?
- **Decisão:** Não inferir viagem a partir de descrição, hotel, aeroporto ou centro de custo. No formato atual, não aplicar acréscimo e registrar o aviso `VIAGEM_NAO_INFORMADA` no resultado.
- **Justificativa:** Evitar concessão sem informação verificável. A restrição é explícita e pode ser revisada.
- **Regra:** RN-005. **Evidência:** d-003/d-010/d-011.

## AMB-006 — Competência

- **Texto original:** Despesas devem ser lançadas dentro do período de competência.
- **Dúvida:** Data do gasto ou do lançamento? Limites são inclusivos?
- **Decisão:** Usar a data da despesa, pois não existe data de lançamento. Aceitar `início <= data <= fim`. Início e fim devem ser válidos, estar ordenados e pertencer ao mês de competência.
- **Justificativa:** Preservar o contrato existente e não inventar data de lançamento.
- **Regra:** RN-006. **Evidência:** d-008/d-014.

## AMB-007 — Identificação de duplicatas

- **Texto original:** Duplicatas devem ser tratadas.
- **Dúvida:** A identificação é por ID ou por conteúdo? Qual item permanece?
- **Decisão:** Comparar data, categoria normalizada, fornecedor, descrição exatos e valor decimal original equivalente. `id` e `tem_nota_fiscal` não entram na chave. O primeiro item estruturalmente válido é canônico, mesmo se for recusado. Os posteriores recebem reembolso zero e referenciam o índice do canônico.
- **Justificativa:** IDs diferentes não impedem duplicidade. Não escolher silenciosamente o comprovante mais favorável.
- **Regra:** RN-007. **Evidência:** d-006/d-007.

## AMB-008 — Estorno

- **Texto original:** A entrada de exemplo contém valor negativo. A política não esclarece.
- **Dúvida:** Abater do orçamento ou recusar?
- **Decisão:** Ignorar valores negativos, com reembolso zero e motivo `ESTORNO_NAO_PROCESSADO`. Não compensar outras despesas.
- **Justificativa:** Não há vínculo com a despesa original para conciliação segura.
- **Regra:** RN-008. **Evidência:** d-009.

## AMB-009 — Precisão monetária

- **Texto original:** A entrada inclui 33.333.
- **Dúvida:** Rejeitar ou arredondar? Em qual momento?
- **Decisão:** Arredondar cada valor positivo para duas casas, com metade para cima, e totalizar os valores já arredondados. O valor original é mantido no resultado. Valor zero, original ou arredondado, é ignorado.
- **Justificativa:** Resultados monetários consistentes e auditáveis.
- **Regra:** RN-009. **Evidência:** d-011.

## AMB-010 — Quantidade de diárias

- **Texto original:** Hospedagem tem limite de R$ 250 por diária.
- **Dúvida:** Como obter a quantidade quando ela está ausente?
- **Decisão:** Não extrair números de texto livre. Considerar uma diária por data informada, compartilhada por todas as hospedagens do mesmo colaborador e data. Sinalizar `DIARIAS_NAO_INFORMADAS`.
- **Justificativa:** Evitar interpretação frágil de descrições. A decisão conservadora fica explícita.
- **Regra:** RN-010. **Evidência:** d-010/d-013.

## AMB-011 — Capitalização de valores

- **Texto original:** Categorias fora da política não são reembolsáveis.
- **Dúvida:** `ALIMENTACAO` equivale a `alimentacao`?
- **Decisão:** No valor de `categoria`, remover espaços ASCII nas extremidades e converter A-Z para a-z. Aceitar `alimentacao`, `transporte_urbano` e `hospedagem`. Não remover acentos nem criar aliases.
- **Justificativa:** Resolver a variação observada preservando o vocabulário fechado.
- **Regra:** RN-011. **Evidência:** d-014/d-005.

## AMB-012 — Fim de semana

- **Texto original:** A política não restringe dias úteis.
- **Dúvida:** Plantão em sábado pode ser reembolsado?
- **Decisão:** Aplicar as regras em todos os dias civis, inclusive sábados, domingos e feriados.
- **Justificativa:** Não criar restrição ausente da política.
- **Regra:** RN-012. **Evidência:** d-012.

## AMB-013 — Capitalização de chaves

- **Texto original:** Respeite o formato da entrada.
- **Dúvida:** `temNotaFiscal` e `TEM_NOTA_FISCAL` são aliases?
- **Decisão:** As chaves são exatas e sensíveis a maiúsculas. `tem_nota_fiscal` é obrigatório e deve ser booleano. Aliases não substituem campos. Campos adicionais são ignorados e não afetam as regras.
- **Justificativa:** Separar a normalização de valores da mudança de contrato.
- **Regra:** RN-013. **Evidência:** caso adicional solicitado.

## AMB-014 — Falhas de entrada

- **Texto original:** A entrada de referência define a forma, mas não a recuperação.
- **Dúvida:** Um item inválido aborta o lote?
- **Decisão:**
  - JSON inválido, chaves JSON repetidas, envelope inválido ou IDs de despesa repetidos abortam o lote.
  - Item com campo obrigatório ausente ou tipo inválido é recusado com `DADO_INVALIDO`. Os demais continuam.
  - ID ausente gera `id: null` e o item é identificado pelo índice.
- **Justificativa:** Evitar a perda do lote por causa de uma despesa e garantir identidade não ambígua.
- **Regra:** RN-014. **Evidência:** caso adicional.

## AMB-015 — Precedência e motivos

- **Texto original:** A política contém regras sobrepostas.
- **Dúvida:** Qual motivo prevalece?
- **Decisão:** Aplicar a ordem da seção 8. Emitir um motivo principal e avisos separados. Duplicatas podem referenciar item recusado.
- **Justificativa:** Evitar resultados e consumo de teto dependentes de verificações implícitas.
- **Regra:** RN-015. **Evidência:** d-013.

## AMB-016 — Totais e status

- **Texto original:** O schema de saída é definido pelo participante.
- **Dúvida:** Valores negativos contam? Zero é parcial?
- **Decisão:**
  - **Solicitado:** soma todos os valores positivos estruturalmente válidos, arredondados, inclusive duplicatas e recusas.
  - **Reembolsável:** soma os pagamentos.
  - **Não reembolsável:** é a diferença entre solicitado e reembolsável.
  - Valores negativos e zero ignorados não entram nos totais.
  - As contagens particionam os itens.
- **Justificativa:** Permitir conciliação explícita entre entrada, recusas e pagamentos.
- **Regra:** RN-016. **Evidência:** todos os itens.