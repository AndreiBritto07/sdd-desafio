# Decisões — Motor de Cálculo de Reembolso

**Revisão documental:** 20/10/2026 — consolidação pós-Envelope 2  
**Relacionamento:** sustenta spec.md v0.2 e tasks.md desta revisão.  
**Estado:** decisões consolidadas para implementação; aprovação oficial e testes não presumidos.

O versionamento deste registro é independente da versão da especificação.

## 1. Critério de decisão

Aplicar a seguinte prioridade, definida pelo usuário:

1. Alinhamento com respostas e decisões anteriores.
2. Na ausência de conflito, opção recomendada.

Decisões posteriores explícitas substituem interpretações anteriores incompatíveis.

Não manter no contrato vigente duas regras contraditórias sob a justificativa de que uma está em adendo.

## 2. Ambiguidades originais consolidadas

| ID | Origem/dúvida | Decisão vigente | Relação |
|---|---|---|---|
| AMB-001 | Limite diário: por item ou agregado? | Agregar por colaborador, centro de custo, categoria e data; obter valor da política | RN-001; AC-001 |
| AMB-002 | Como distribuir o teto? | Ordem original; consumir somente reembolso efetivo | RN-002; AC-002 |
| AMB-003 | Igualdade com teto é parcial? | Igualdade é integral; cortar somente excedente | RN-003; AC-003 |
| AMB-004 | NF acima de 100: qual base? | Valor preliminar reembolsável após conversão e limites, estritamente maior que 100.00 | RN-004; AC-004 |
| AMB-005 | Como identificar viagem sem campo? | Não inferir; não ampliar limite; emitir aviso global | RN-005; AC-005 |
| AMB-006 | Competência, datas inválidas e inversão | Data individual inválida afeta item; período global inválido rejeita lote; inversão válida é corrigida | RN-006; AC-006/021 |
| AMB-007 | Duplicata por ID ou conteúdo? | Estrutura, ID e depois conteúdo; preservar canônico e normalizações definidas | RN-007; AC-007/036 |
| AMB-008 | Estorno negativo | No contrato consolidado, zero/negativo são inválidos por item; não compensar saldos | RN-008; AC-008 |
| AMB-009 | Valor original com três casas | Invalidar somente o item; aceitar inteiro/uma/duas casas; formatar saída com duas | RN-009; AC-009 |
| AMB-010 | Número de diárias ausente | Não extrair do texto; uma diária compartilhada por data | RN-010; AC-010 |
| AMB-011 | Caixa e categorias permitidas | Normalizar categoria por trim/caixa ASCII; categorias vêm da política | RN-011; AC-011 |
| AMB-012 | Fim de semana | Aplicar regras em todos os dias civis | RN-012; AC-012 |
| AMB-013 | Aliases de chaves e extras | Chaves exatas; extras ignorados na entrada principal | RN-013; AC-013 |
| AMB-014 | Falha individual aborta lote? | Somente falhas globais abortam; itens inválidos permanecem na saída | RN-014; AC-014/019/020 |
| AMB-015 | Qual motivo prevalece? | Lista normativa única e ordenada; campo singular por compatibilidade | RN-015; AC-015/032 |
| AMB-016 | Base dos totais e contagens | Separar bruto convertível, solicitado elegível e pagamento | RN-016/018; AC-016/018/031 |

A motivação comum é manter processamento determinístico, auditável e compatível com as decisões explícitas, sem inferências silenciosas.

## 3. Registro das correções 1–69

A numeração é preservada para rastrear a revisão anterior.

“Refinada” ou “substituída” identifica evolução da regra, não uma alternativa de execução.

| Correção | Consolidação vigente |
|---|---|
| 1 | Gerar ID quando ausente |
| 2 | Envelope 2 incorporado ao contrato único |
| 3 | Inválidos e duplicatas não entram em total_solicitado; bruto convertível segue RN-016 |
| 4 | Não inferir viagem/diárias de texto |
| 5 | Validar AC somente após execução real de teste |
| 6 | Manter primeiro ID estruturalmente válido; recusar repetição posterior |
| 7 | Manter itens inválidos em items, com erros e motivos |
| 8 | Gerar ID determinístico por índice, evitando colisões |
| 9 | Substituída: Envelope 2 já recebido e incorporado documentalmente |
| 10 | Consolidação não equivale a aprovação oficial |
| 11 | ACs no spec; fixtures completas e testes na suíte |
| 12 | Refinada: solicitado exclui inelegíveis, duplicados e inválidos; recusa exclusiva por limite permanece na base |
| 13 | Rastrear decisão -> RN -> AC -> teste; não inventar relações |
| 14 | Versionamento independente de spec e decisões |
| 15 | Manter spec v0.2 e preservar versão anterior no Git |
| 16 | Manter campos de resultado; motivos passa a ser fonte normativa |
| 17 | Colisão de ID gerado é resolvida sem abortar lote |
| 18 | Usar gerado-{indice}, depois sufixos -1, -2 etc. |
| 19 | Recalcular exemplos; não declarar resultados testados sem execução |
| 20 | Substituída: Envelope 2 não está mais pendente de recebimento |
| 21 | Item estruturalmente inválido não reserva ID para deduplicação |
| 22 | Separar repetição de ID e duplicidade por conteúdo |
| 23 | ID presente inválido não é substituído |
| 24 | Gerar ID ausente mesmo quando outro campo estiver inválido |
| 25 | total_itens exclui itens estruturalmente inválidos |
| 26 | ID repetido precede comparação por conteúdo |
| 27 | total_solicitado usa base elegível antes da redução por limites |
| 28 | Contagens excluem itens estruturalmente inválidos |
| 29 | Repetição de ID prevalece sobre conteúdo duplicado |
| 30 | Repetição de ID recusa somente ocorrência posterior |
| 31 | Emitir versao_spec "0.2" em sucesso e falha |
| 32 | Comparar IDs com trim ASCII externo e sem diferença de caixa |
| 33 | Preservar ID original válido na saída |
| 34 | ID repetido usa DADO_INVALIDO e erro ID_REPETIDO |
| 35 | Não usar IDS_REPETIDOS como erro de lote |
| 36 | Resumo conta somente itens estruturalmente válidos |
| 37 | Testar IDs equivalentes por espaços e caixa |
| 38 | ID presente inválido retorna null |
| 39 | Colisão de ID gerado usa a mesma normalização |
| 40 | Validar estrutura, ID, conteúdo e depois elegibilidade |
| 41 | Duplicata preserva valor convertido informativo e reembolsa zero |
| 42 | Recusa mantém valor informativo, mas só inelegibilidade exclui da base solicitada; bruto tem base própria |
| 43 | ID ausente não gera erro; inválido e repetido têm códigos específicos |
| 44 | Preservar nome total_solicitado e explicitar sua base |
| 45 | total_nao_reembolsavel = total_solicitado - total_reembolsavel |
| 46 | ID repetido conta como recusado válido, sem entrar no solicitado |
| 47 | Evitar colisão com IDs fornecidos até em despesas inválidas |
| 48 | Substituída: zero/negativo agora são inválidos por item |
| 49 | Refinada: valor original inválido não é normalizado como aceito; reembolso zero |
| 50 | Usar índice zero-based da lista original completa |
| 51 | Duplicata conta como ignorada válida, sem entrar no solicitado |
| 52 | Referenciar primeiro canônico estruturalmente válido, mesmo se inelegível |
| 53 | Fornecedor/descrição: trim externo e comparação sem caixa; preservar espaços internos/acentos |
| 54 | Aplicar NFC antes de comparar fornecedor/descrição |
| 55 | Refinada: entrada original precisa ter até duas casas; half-up aplica-se à conversão |
| 56 | tem_nota_fiscal não participa da chave de conteúdo |
| 57 | Comparar datas válidas em representação comum |
| 58 | Comparar categoria normalizada |
| 59 | Registrar todos os erros estruturais |
| 60 | Ordem dos erros independe da ordem das chaves |
| 61 | Ordem: ID, obrigatórios na ordem do schema, opcionais |
| 62 | Ignorar campos desconhecidos nas despesas |
| 63 | Ignorar campos desconhecidos no envelope |
| 64 | Manter tolerância a extras da entrada principal; não estender aos schemas externos |
| 65 | Corrigir automaticamente período válido invertido |
| 66 | Retornar período corrigido usado no cálculo |
| 67 | Chaves repetidas na entrada principal causam JSON_INVALIDO |
| 68 | Colaborador obrigatório incompleto/inválido causa ENTRADA_INVALIDA global |
| 69 | Data individual inválida afeta item; data válida fora do período afeta elegibilidade; período global inválido rejeita lote |

Os vínculos funcionais estão nas AMBs, no registro E2 e na matriz AC/RN do spec. As tarefas apontam para essas mesmas referências.

## 4. Registro do Envelope 2

Os identificadores E2 preservam o registro anterior e não equivalem à numeração das perguntas conversacionais.

| ID | Decisão vigente | Relação |
|---|---|---|
| E2-001 | Repetição moeda+data invalida cambio.json, mesmo com valores iguais | RN-020; AC-023 |
| E2-002 | Cotação ausente, não numérica ou não positiva invalida arquivo | RN-020; AC-023 |
| E2-003 | Data cambial real e moeda com três letras ASCII maiúsculas | RN-020; AC-023 |
| E2-004 | Schema cambial estrito, sem extras/obrigatórios ausentes | RN-020; AC-023 |
| E2-005 | Não inventar suporte a moeda; sem cotação aplicável, recusar somente despesa | RN-020/022; AC-030 |
| E2-006 | Validar todos os registros cambiais, inclusive não usados | RN-020; AC-023 |
| E2-007 | Câmbio ausente/vazio/inválido causa CAMBIO_INVALIDO | RN-020; AC-023 |
| E2-008 | Moeda ausente assume BRL; presente inválida afeta item | RN-022; AC-024 |
| E2-009 | Não normalizar caixa da moeda | RN-022; AC-024 |
| E2-010 | BRL não exige lookup individual; validação global do câmbio continua obrigatória | RN-022; AC-024 |
| E2-011 | Valor ausente/inválido/zero/negativo invalida somente despesa | RN-023; AC-008/027 |
| E2-012 | Valor deve ser número JSON, nunca string numérica | RN-023; AC-027 |
| E2-013 | Notação científica é proibida no valor original | RN-023; AC-027 |
| E2-014 | JSON usa ponto decimal; sintaxe malformada rejeita lote | RN-014/023; AC-019/027 |
| E2-015 | Valor fora da capacidade numérica afeta somente item | RN-023; AC-027 |
| E2-016 | Teto original inclusivo de 1.000.000.000.000,00 | RN-023; AC-027 |
| E2-017 | Teto aplica-se à moeda original, não ao BRL convertido | RN-023; AC-027 |
| E2-018 | Overflow de conversão afeta item e marca totais incompletos | RN-021/026; AC-030 |
| E2-019 | Conversão válida arredondada a zero é aceita, sem consumir saldo | RN-021; AC-026 |
| E2-020 | Converter e aplicar half-up por despesa | RN-021; AC-026 |
| E2-021 | Depois da conversão, usar centavos inteiros | RN-021; AC-026 |
| E2-022 | Usar decimal/racional exato, sem ponto flutuante binário | RN-021; AC-026 |
| E2-023 | Cotação não aceita string, notação científica, zero ou negativo | RN-020; AC-023 |
| E2-024 | Cotação admite precisão variável, desde que exata e segura | RN-020/021; AC-023/026 |
| E2-025 | Zeros finais não alteram valor nem a regra moeda+data | RN-020/021; AC-023/026 |
| E2-026 | Aceitar zeros finais; normalizar apenas exibição | RN-021; AC-026/032 |
| E2-027 | Exibir cotações com duas casas e ponto decimal | RN-021; AC-032 |
| E2-028 | Separar cotação interna exata da exibição | RN-021; AC-026 |
| E2-029 | Campos monetários são números JSON serializados com duas casas | RN-026; AC-032 |
| E2-030 | Motivos múltiplos, únicos e ordenados; diário antes de mensal | RN-015/025; AC-015/032 |
| E2-031 | JSON principal malformado/repetido causa JSON_INVALIDO global | RN-014; AC-019 |
| E2-032 | Período global inválido rejeita lote; data individual inválida não | RN-006; AC-006 |
| E2-033 | Política ausente/ilegível/inválida causa POLITICA_INVALIDA | RN-019; AC-022 |
| E2-034 | Centro desconhecido usa padrao; categoria ausente não reembolsa | RN-019; AC-033 |
| E2-035 | Limites diário e mensal usam menor saldo e ordem original | RN-024; AC-028 |
| E2-036 | Bruto convertível tem base distinta do solicitado; falhas de conversão tornam totais incompletos | RN-016/026; AC-030/031 |
| E2-037 | NF depende do preliminar >100.00; bloqueio não consome saldo | RN-004/025; AC-004/029 |
| E2-038 | Representação comercial tem teto absoluto 300.00, redutível pela política; hospedagem em CC-ENG-PLATAFORMA é proibida | RN-019; AC-034/035 |

## 5. Consolidação desta revisão

### CONS-001 — Representação comercial

**Origem:** escolha final C do usuário.

**Decisão:** para CC-COMERCIAL/representacao, usar o menor entre o limite diário da política, quando existente, e 300.00 BRL.

Se a política permitir a categoria sem definir limite diário próprio, o teto de 300.00 continua aplicável.

A categoria precisa estar permitida. Não usar a exceção para autorizar categoria ausente.

**Justificativa:** 300.00 é teto máximo, não autorização para ampliar limite inferior.

**Relação:** RN-019; AC-034; T-041.

### CONS-002 — Nomes e bases dos totais

**Origem:** preservar os quatro nomes escolhidos pelo usuário.

**Decisão:**

- total_original_convertido: bruto convertível antes das restrições.
- total_solicitado: base elegível antes da redução por limites.
- total_reembolsavel: pagamento final.
- total_nao_reembolsavel: solicitado menos pagamento.

Remover total_bruto_convertido e total_nao_reembolsado.

Uma recusa exclusivamente por saldo esgotado permanece na base solicitada.

**Justificativa:** manter a identidade previamente escolhida sem confundir bases distintas.

**Relação:** RN-016/026; AC-016/031; T-025/T-044.

### CONS-003 — Catálogo de motivos

**Origem:** necessidade de tornar implementável a lista ordenada de motivos.

**Decisão:** usar o catálogo único do spec, com LIMITE_DIARIO e LIMITE_MENSAL para as duas restrições.

Preservar motivo singular por compatibilidade; motivos é a fonte normativa.

DENTRO_DO_LIMITE é usado no singular quando a lista está vazia.

**Justificativa:** eliminar aliases e representar limites simultâneos sem perder informação.

**Relação:** RN-015/025; AC-015/032; T-043.

### CONS-004 — Moeda na duplicidade

**Origem:** introdução de moedas diferentes pelo Envelope 2.

**Decisão:** incluir moeda efetiva e valor original válido na chave de conteúdo.

**Justificativa:** mesmo número em moedas diferentes não comprova duplicidade.

**Relação:** RN-007; AC-036; T-018.

### CONS-005 — Exibição e valor inválido

**Decisão:** valores aceitos inteiros ou com uma casa são exibidos com duas. Valores originais com mais de duas casas são inválidos, sem arredondamento de entrada.

valor_original inválido retorna null; o erro informa a falha.

Cotação preserva precisão interna e usa duas casas apenas na exibição.

**Justificativa:** formatação não deve transformar entrada inválida em valor aparentemente aceito.

**Relação:** RN-009/021/023/026; AC-009/026/027/032; T-036/T-037/T-039/T-043.

### CONS-006 — Completude independente da elegibilidade

**Decisão:** obter o valor convertido para o bruto sempre que houver dados suficientes, mesmo se a despesa for inelegível ou tiver outro defeito estrutural.

Se não for possível obter o valor em BRL, excluir a despesa dos totais monetários e marcar totais_completos=false.

**Justificativa:** recusa não significa automaticamente impossibilidade de conversão.

**Relação:** RN-016/026; AC-030/031; T-044.

### CONS-007 — Rastreabilidade

**Decisão:** corrigir todas as referências das tarefas para os IDs realmente existentes.

Exemplos:

- JSON repetido: correção 67.
- Colaborador inválido: correção 68.
- Inversão do período: correção 65.
- Retorno do período corrigido: correção 66.

**Relação:** matriz AC/RN do spec; T-030/T-045.

## 6. Regras substituídas

Não implementar como alternativas vigentes:

| Regra anterior | Regra vigente |
|---|---|
| NF sobre valor original bruto | NF sobre preliminar após limites |
| Arredondar valor original com mais de duas casas | Invalidar somente a despesa |
| Zero/negativo como ignorado ou estorno | ENTRADA_INVALIDA individual |
| Categorias fixas do exemplo | Categorias da política |
| Apenas motivo singular | motivos normativo e singular compatível |
| Política pode elevar representação acima de 300.00 | Teto absoluto 300.00 |
| Toda recusa sai da base solicitada | Somente inelegibilidade; recusa exclusiva por limite permanece |
| Bruto menos pagamento como total_nao_reembolsavel | Solicitado menos pagamento |
| Período global inválido ainda sem decisão | ENTRADA_INVALIDA global |
| Quadro antigo de 14 itens como resultado vigente | Recalcular após inspeção da fixture original |

## 7. Pendências e evidências

Pendências técnicas:

- Conferir schemas originais da política e do câmbio.
- Inspecionar CLI e suíte reais.
- Implementar e executar testes.
- Registrar resultados e atualizar rastreabilidade.

Nenhum teste foi declarado aprovado por esta revisão documental.

Nenhuma pendência técnica autoriza reabrir silenciosamente decisões já tomadas.