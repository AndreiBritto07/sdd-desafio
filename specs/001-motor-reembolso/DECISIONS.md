# Decisões do motor de reembolso

**Estado:** registro de propostas, pendente de aprovação oficial. As escolhas de revisão abaixo não equivalem a aprovação oficial do participante. `spec.md` e `DECISIONS.md` mantêm versionamento independente; a relação entre versões deve ser explicada, não presumida como numeração igual. A versão proposta de `spec.md` nesta revisão é 0.2.

Registro das ambiguidades (AMB) e decisões de revisão. Cada decisão deve referenciar a regra (RN), critério de aceite (AC) e teste automatizado correspondente quando houver relação direta; vínculos ainda não confirmados são marcados como pendentes.

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
- **Dúvida:** Data do gasto ou do lançamento? Limites são inclusivos? Como tratar outros períodos inválidos?
- **Decisão proposta:** Usar a data da despesa, pois não existe data de lançamento. Aceitar `início <= data <= fim`. Se as datas de início/fim forem válidas e estiverem invertidas, trocá-las e retornar o período corrigido. O tratamento de competência ausente/inválida, datas inexistentes ou incompatibilidade com o mês continua em aberto pela correção 69.
- **Justificativa:** Preservar o contrato existente e não inventar data de lançamento.
- **Regra:** RN-006. **Evidência:** d-008/d-014.

## AMB-007 — Identificação de duplicatas

- **Texto original:** Duplicatas devem ser tratadas.
- **Dúvida:** A identificação é por ID ou por conteúdo? Qual item permanece?
- **Decisão proposta:** Verificar ID primeiro, após trim ASCII nas extremidades e comparação sem diferença de caixa. Ocorrência posterior de ID repetido é `RECUSADO`/`DADO_INVALIDO` com `ID_REPETIDO`. Só IDs diferentes entram na comparação de conteúdo: data normalizada, categoria normalizada, fornecedor/descrição após Unicode NFC, trim ASCII externo e comparação sem diferença de caixa, e valor arredondado a duas casas. Ignorar `tem_nota_fiscal` e campos extras. Primeiro item estruturalmente válido com aquele conteúdo é canônico mesmo se recusado por regra de negócio; cópia é `IGNORADO`/`DUPLICATA` e aponta para o índice canônico.
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
- **Texto original / origem:** Entrada de referência define forma, mas não recuperação.
- **Dúvida:** Um item inválido aborta lote? Como tratar IDs ausentes/repetidos?
- **Decisão proposta:** JSON inválido ou chaves JSON repetidas rejeitam o lote com `JSON_INVALIDO`; envelope inválido ou qualquer campo obrigatório de colaborador ausente, vazio ou de tipo incorreto rejeita o lote com `ENTRADA_INVALIDA`. Despesas estruturalmente inválidas são recusadas individualmente e todos os erros são registrados em ordem fixa. ID ausente gera ID determinístico por índice; ID presente inválido retorna null. ID repetido rejeita apenas a ocorrência posterior com `RECUSADO`/`DADO_INVALIDO` e erro `ID_REPETIDO`; o lote continua. IDs de itens estruturalmente inválidos não reservam IDs para deduplicação, mas seus valores fornecidos são considerados para evitar colisões de IDs gerados.
- **Justificativa:** Garantir comportamento determinístico, sem saída financeira parcial para erros de lote e sem perder despesas válidas por um ID repetido.
- **Regra:** RN-014. **Evidência:** correções 8, 17–18, 22–27, 33–44, 48, 51, 60–68 deste registro.

## AMB-015 — Precedência e motivos

- **Texto original:** A política contém regras sobrepostas.
- **Dúvida:** Qual motivo prevalece?
- **Decisão:** Aplicar a ordem da seção 8. Emitir um motivo principal e avisos separados. Duplicatas podem referenciar item recusado.
- **Justificativa:** Evitar resultados e consumo de teto dependentes de verificações implícitas.
- **Regra:** RN-015. **Evidência:** d-013.

## AMB-016 — Totais e status
- **Texto original / origem:** Schema de saída é definido pelo participante.
- **Dúvida:** Quais despesas entram em contagens e totais?
- **Decisão proposta:** `total_itens` e contagens incluem somente despesas estruturalmente válidas, incluindo IDs repetidos e duplicatas por conteúdo; despesas estruturalmente inválidas permanecem em `items`, mas ficam fora de contagens e totais. `total_solicitado` soma apenas valores arredondados de itens válidos que chegam ao cálculo de limites; recusados por regra de negócio, duplicatas, ignorados e inválidos são excluídos. `total_reembolsavel` soma pagamentos. `total_nao_reembolsavel = total_solicitado - total_reembolsavel`.
- **Justificativa:** Fazer o resumo refletir itens considerados na avaliação financeira e manter reconciliação dos totais definidos.
- **Regra:** RN-016/RN-018. **Evidência:** correções 3, 12, 25–29, 37, 42–50, 52.

## Registro das correções 1–68

As escolhas abaixo foram recolhidas durante a revisão conversacional e permanecem **propostas pendentes de aprovação oficial**. “Teste pendente” significa que o caso deve existir e passar na suíte automatizada; não afirma que já foi implementado ou executado.

| Correção | Decisão consolidada | Relação | Estado do teste |
|---:|---|---|---|
| 1 | Gerar ID quando o campo estiver ausente | RN-014, AC-014 | Pendente de inspeção/execução |
| 2 | Registrar requisito do Dia 2 como pendente; revisar ao recebê-lo | Seção 10 | Aguardando requisito |
| 3 | Excluir despesas inválidas e duplicatas dos totais financeiros | RN-016, AC-016 | Pendente de inspeção/execução |
| 4 | Manter interpretação conservadora para viagem/diárias; não inferir de texto | RN-005/RN-010, AC-005/010 | Pendente de inspeção/execução |
| 5 | Associar cada AC a teste identificável e só marcar validado após execução aprovada | Seção 11 | Pendente |
| 6 | Primeiro ID válido mantido; ocorrência posterior rejeitada no item e excluída dos totais | RN-007/RN-014 | Pendente |
| 7 | Manter itens inválidos na saída com status/motivo/erros; sem lista redundante | Schema de saída | Pendente |
| 8 | IDs gerados determinísticos por índice, evitando colisões com IDs fornecidos | RN-014 | Pendente |
| 9 | Manter Dia 2 como pendente até recebimento do requisito | Seção 10 | Aguardando requisito |
| 10 | Decisões continuam propostas até aprovação oficial | Cabeçalho | N/A |
| 11 | ACs no spec; casos completos de entrada/saída na suíte de testes separada | Seção 11 | Caminho/nome da suíte a confirmar no repositório |
| 12 | Total solicitado exclui inválidos, duplicatas, ignorados e recusados | RN-016 | Pendente |
| 13 | Rastrear AMB → RN → AC → teste; declarar ausência de relação direta quando aplicável | Seção 11 | Pendente |
| 14 | `spec.md` e `DECISIONS.md` têm versionamento independente, com relação explicada | Cabeçalhos | Aplicado nesta proposta |
| 15 | Propor `spec.md` v0.2 e preservar histórico de v0.1 | Cabeçalho | Pendente de aprovação |
| 16 | Usar status/motivo/justificativa/erros existentes; inválido DADO_INVALIDO, duplicata de conteúdo DUPLICATA | Schema/RN-014 | Pendente |
| 17 | IDs gerados verificam IDs fornecidos e gerados; colisão não aborta lote | RN-014 | Pendente |
| 18 | Colisão: `gerado-{índice}`, depois `gerado-{índice}-1`, `-2` etc. | RN-014 | Pendente |
| 19 | Recalcular exemplo conforme regras e identificar como esperado, não validado | Seção 9 | Pendente de execução |
| 20 | Dia 2 explicitamente pendente | Seção 10 | Aguardando requisito |
| 21 | Item estruturalmente inválido não reserva ID para deduplicação | RN-014 | Pendente |
| 22 | ID e conteúdo são critérios separados; decisão refinada pela correção 27 | RN-007 | Pendente |
| 23 | Gerar ID somente quando campo ausente; valor presente vazio/tipo errado é inválido | RN-014 | Pendente |
| 24 | Gerar ID para campo ausente mesmo se outro campo do item for inválido | RN-014 | Pendente |
| 25 | `total_itens`/contagens excluem estruturalmente inválidos | RN-016/RN-018 | Pendente |
| 26 | ID repetido tem precedência sobre duplicidade por conteúdo | RN-007/RN-014 | Pendente |
| 27 | `total_solicitado` só inclui itens válidos elegíveis antes dos limites; exclusões documentadas | RN-016 | Pendente |
| 28 | Contagens apenas de itens estruturalmente válidos | RN-016/RN-018 | Pendente |
| 29 | Resolver conflito favorecendo a regra de ID repetido sobre conteúdo duplicado | RN-007/RN-014 | Pendente |
| 30 | Rejeitar somente ocorrência posterior do ID repetido; continuar lote | RN-014 | Pendente |
| 31 | Emitir `versao_spec: "0.2"` em sucesso, falha e exemplos | Schema | Pendente |
| 32 | Normalizar ID com trim ASCII externo e comparação sem diferença de caixa | RN-007/RN-014 | Pendente |
| 33 | Preservar ID original na saída; normalizar somente para comparação | RN-014 | Pendente |
| 34 | Usar erro `ID_REPETIDO` em `erros`, mantendo motivo `DADO_INVALIDO` | RN-014 | Pendente |
| 35 | Remover `IDS_REPETIDOS` dos erros de lote | RN-014 | Pendente |
| 36 | Resumo conta apenas itens estruturalmente válidos | RN-016/RN-018 | Pendente |
| 37 | Caso de borda de IDs com espaços/caixa reflete normalização | RN-007 | Pendente |
| 38 | ID presente inválido retorna null; não gerar substituto | RN-014 | Pendente |
| 39 | Checagem de colisão de IDs gerados usa mesma normalização | RN-014 | Pendente |
| 40 | Validar estrutura, depois ID repetido, depois conteúdo duplicado, depois regras de negócio | RN-014/RN-015 | Pendente |
| 41 | Duplicata por conteúdo mantém valor solicitado arredondado, reembolso zero | RN-007/RN-016 | Pendente |
| 42 | Recusa por regra de negócio mantém valor solicitado arredondado, mas sai dos totais | RN-016 | Pendente |
| 43 | ID ausente gera sem erro; ID inválido usa `TIPO_OU_FORMATO_INVALIDO`; ID repetido usa `ID_REPETIDO` | RN-014 | Pendente |
| 44 | Manter nome `total_solicitado` e documentar a base elegível antes dos limites | RN-016 | Pendente |
| 45 | `total_nao_reembolsavel = total_solicitado - total_reembolsavel` | RN-016 | Pendente |
| 46 | ID repetido conta em `total_itens`/`recusados`, mas não em totais financeiros | RN-014/RN-016 | Pendente |
| 47 | Evitar colisão com IDs fornecidos inclusive em itens estruturalmente inválidos | RN-014 | Pendente |
| 48 | Valor válido zero/negativo conta em itens/status ignorados, mas não em totais financeiros | RN-008/RN-009/RN-016 | Pendente |
| 49 | Para zero/negativo, `valor_solicitado` e `valor_reembolsavel` são 0; preservar original válido | RN-008/RN-009 | Pendente |
| 50 | ID gerado usa índice original zero-based da lista completa | RN-014 | Pendente |
| 51 | Duplicata de conteúdo conta em `total_itens`/`ignorados`, mas não em totais financeiros | RN-007/RN-016 | Pendente |
| 52 | `duplicata_de_indice` aponta primeiro item estruturalmente válido com conteúdo, mesmo se recusado | RN-007 | Pendente |
| 53 | Fornecedor/descrição: trim ASCII externo, sem diferença de caixa, preservar espaços internos/acentos | RN-007 | Pendente |
| 54 | Aplicar NFC antes de comparar fornecedor/descrição; diferenças reais de acento permanecem | RN-007 | Pendente |
| 55 | Comparar valores de duplicata após arredondamento half-up a duas casas | RN-007/RN-009 | Pendente |
| 56 | `tem_nota_fiscal` não participa da chave de conteúdo duplicado | RN-007 | Pendente |
| 57 | Normalizar datas válidas para representação comum antes de comparar duplicatas | RN-007 | Pendente |
| 58 | Comparar categoria normalizada, não texto bruto | RN-007/RN-011 | Pendente |
| 59 | Registrar todos os erros estruturais em ordem fixa; recusar item uma vez | RN-014 | Pendente |
| 60 | Ordem de erros independe da ordem das chaves JSON | RN-014 | Pendente |
| 61 | Ordem começa por ID, segue campos obrigatórios do schema e termina nos opcionais | RN-014 | Pendente |
| 62 | Ignorar campos desconhecidos nas despesas; testar comportamento | RN-013/AC-013 | Pendente |
| 63 | Ignorar campos desconhecidos na raiz/envelope | RN-013/RN-014 | Pendente |
| 64 | Ignorar campos desconhecidos no envelope/raiz | RN-013/RN-014 | Pendente |
| 65 | Trocar automaticamente datas inicial/final válidas se invertidas | RN-006 | Pendente |
| 66 | Retornar no output o período corrigido usado | RN-006 | Pendente |
| 67 | Chaves JSON repetidas causam `JSON_INVALIDO` e rejeição do lote inteiro | RN-014/AC-019 | Pendente |
| 68 | Colaborador obrigatório incompleto causa `ENTRADA_INVALIDA` para o lote inteiro | RN-014/AC-020 | Pendente |

## Correção ainda não resolvida

**Correção 69 — período inválido:** ainda não foi escolhida uma opção para competência ausente/inválida, data inexistente ou datas incompatíveis com o mês de competência. A decisão já registrada para datas inicial/final invertidas e válidas permanece: trocar automaticamente e devolver o período corrigido. Esta correção não foi decidida nem aplicada por inferência.