# Backlog de implementação — motor de reembolso

**Base:** `spec.md` v0.2 (proposta) e `DECISIONS.md` (decisões propostas).  
**Formato:** cada tarefa deve caber em um commit pequeno, independente sempre que possível. Os nomes de testes abaixo são identificadores sugeridos; adapte-os à convenção existente no repositório sem perder a cobertura descrita.  
**Estado:** especificação e decisões ainda precisam de aprovação formal. Não marcar critérios como concluídos sem executar os testes.

## Regras para concluir uma tarefa

- Fazer uma alteração focada e criar/atualizar testes automatizados junto com o código.
- Executar o teste indicado e os testes relacionados; registrar o resultado real.
- Não alterar regras de negócio fora do escopo da tarefa.
- Manter `spec.md`, `DECISIONS.md` e a matriz de rastreabilidade consistentes.

## Tarefas

### T-001 — Mapear a estrutura existente e executar a suíte-base
- **O que faz:** identificar linguagem, módulos, comandos, convenções e testes existentes; executar a suíte sem mudar comportamento e registrar o resultado-base.
- **Requisitos atendidos:** RN-017 (interface CLI, se já implementada); preparação para AC-001 a AC-021.
- **Critério de aceite:** a suíte-base é executada e o resultado real fica registrado; se houver falha pré-existente, ela é reproduzível e documentada. Não exige que a suíte esteja verde antes das alterações.

### T-002 — Criar fixtures reutilizáveis de entrada e saída
- **O que faz:** adicionar builders/fixtures mínimos para colaborador, período, despesas e respostas esperadas, seguindo o padrão de testes do projeto.
- **Requisitos atendidos:** AC-001 a AC-021, como suporte à cobertura automatizada.
- **Critério de aceite:** `test_fixtures_validas_podem_ser_carregadas` passa e os testes não dependem de copiar grandes blocos de JSON.

### T-003 — Validar o envelope JSON básico
- **O que faz:** validar a presença e os tipos dos campos de envelope definidos na spec, sem ainda implementar regras financeiras.
- **Requisitos atendidos:** RN-001, RN-002; AC-001.
- **Critério de aceite:** `test_entrada_valida_e_aceita` e `test_envelope_invalido_retorna_entrada_invalida` passam.

### T-004 — Rejeitar JSON malformado e chaves repetidas
- **O que faz:** detectar JSON sintaticamente inválido e chaves duplicadas em objetos JSON, rejeitando o lote inteiro sem resultado financeiro parcial.
- **Requisitos atendidos:** RN-001; AC-019; decisão 66.
- **Critério de aceite:** `test_json_malformado_retorna_json_invalido` e `test_chave_json_repetida_rejeita_lote_inteiro` passam.

### T-005 — Validar campos obrigatórios do colaborador
- **O que faz:** rejeitar o lote se qualquer campo obrigatório do colaborador estiver ausente, vazio ou com tipo incorreto.
- **Requisitos atendidos:** RN-002; AC-020; decisão 67.
- **Critério de aceite:** `test_colaborador_incompleto_retorna_entrada_invalida` passa para cada campo obrigatório e para ausência, vazio e tipo incorreto; nenhum resultado financeiro é retornado.

### T-006 — Ignorar campos desconhecidos do envelope e da despesa
- **O que faz:** aceitar campos extras não definidos, sem usá-los na validação, deduplicação ou cálculo.
- **Requisitos atendidos:** RN-001, RN-003; decisões 62 e 63.
- **Critério de aceite:** `test_campos_extras_no_envelope_sao_ignorados` e `test_campos_extras_na_despesa_nao_afetam_resultado` passam.

### T-007 — Validar tipos e formatos estruturais da despesa
- **O que faz:** validar campos obrigatórios, datas, categoria, descrição, fornecedor, valor numérico finito e booleano da nota fiscal; não aceitar booleano ou string como valor numérico.
- **Requisitos atendidos:** RN-003, RN-004; AC-002 a AC-005.
- **Critério de aceite:** `test_despesa_com_tipo_ou_formato_invalido_e_recusada` passa para cada campo e tipo inválido.

### T-008 — Retornar todos os erros estruturais em ordem determinística
- **O que faz:** acumular os erros estruturais aplicáveis em `erros`, seguindo a ordem fixa de campos e validações da spec, independentemente da ordem das chaves JSON.
- **Requisitos atendidos:** RN-004; decisões 59, 60 e 61.
- **Critério de aceite:** `test_erros_estruturais_sao_completos_e_ordenados` e `test_ordem_dos_erros_independe_da_ordem_json` passam.

### T-009 — Manter despesa estruturalmente inválida na saída
- **O que faz:** incluir a despesa inválida em `items`, com `RECUSADO`, motivo `DADO_INVALIDO`, erros e `id: null` quando o ID informado for inválido; excluí-la de contagens e totais.
- **Requisitos atendidos:** RN-004, RN-005; decisões 7, 25, 36, 38 e 59.
- **Critério de aceite:** `test_despesa_estruturalmente_invalida_permanece_em_items` e `test_despesa_invalida_nao_entra_em_resumo` passam.

### T-010 — Gerar ID somente quando o campo estiver ausente
- **O que faz:** gerar `gerado-{índice_original}` apenas quando a propriedade `id` não existir; ID presente vazio, só com espaços ou de tipo incorreto é inválido e não deve ser substituído.
- **Requisitos atendidos:** RN-005; decisões 1, 8, 23 e 38.
- **Critério de aceite:** `test_id_ausente_e_gerado` e `test_id_presente_invalido_nao_e_substituido` passam.

### T-011 — Garantir índice original e unicidade dos IDs gerados
- **O que faz:** usar índice zero-based da lista original e evitar colisões com todos os IDs fornecidos, inclusive em despesas estruturalmente inválidas, e com IDs já gerados; aplicar sufixos `-1`, `-2` etc.
- **Requisitos atendidos:** RN-005; decisões 8, 17, 18, 39, 47 e 50.
- **Critério de aceite:** `test_id_gerado_usa_indice_original` e `test_id_gerado_resolve_colisoes_com_sufixo` passam.

### T-012 — Normalizar IDs apenas para comparação
- **O que faz:** comparar IDs após remover espaços ASCII das extremidades e ignorar diferenças entre maiúsculas/minúsculas, preservando o ID original válido na saída.
- **Requisitos atendidos:** RN-005; decisões 32, 33, 37 e 39.
- **Critério de aceite:** `test_id_com_espacos_e_caixa_diferente_e_repetido` e `test_id_original_e_preservado_na_saida` passam.

### T-013 — Rejeitar ocorrências posteriores de ID repetido
- **O que faz:** manter a primeira despesa estruturalmente válida; marcar a ocorrência posterior como `RECUSADO`/`DADO_INVALIDO`, incluindo `ID_REPETIDO` em `erros`; continuar processando o lote.
- **Requisitos atendidos:** RN-006; decisões 6, 21, 26, 29, 30, 34, 35, 40 e 46.
- **Critério de aceite:** `test_id_repetido_recusa_somente_ocorrencia_posterior` e `test_id_repetido_nao_aborta_lote` passam.

### T-014 — Implementar arredondamento monetário half-up
- **O que faz:** centralizar o arredondamento de valores monetários para duas casas decimais usando half-up, sem depender do arredondamento binário padrão da linguagem.
- **Requisitos atendidos:** RN-007; decisão 55.
- **Critério de aceite:** `test_valores_monetarios_usam_half_up` passa para casos de empate, positivos e negativos conforme permitido pela spec.

### T-015 — Implementar regras de elegibilidade básica da despesa
- **O que faz:** aplicar regras para valor zero/negativo, estorno, competência, categoria e nota fiscal obrigatória, conforme precedência da spec.
- **Requisitos atendidos:** RN-008 a RN-012; AC correspondentes às regras de negócio.
- **Critério de aceite:** `test_regras_de_elegibilidade` passa com pelo menos um caso positivo e um negativo por regra.

### T-016 — Normalizar datas para comparação e validar competência
- **O que faz:** interpretar datas válidas, comparar datas normalizadas e garantir compatibilidade com a competência, sem inferir datas a partir de texto livre.
- **Requisitos atendidos:** RN-002, RN-009; decisões 57 e 64–65.
- **Critério de aceite:** `test_datas_validas_sao_normalizadas_para_comparacao` passa; `test_data_despesa_malformada_recusa_somente_item` e `test_data_despesa_inexistente_recusa_somente_item` confirmam que apenas o item inválido é recusado e o lote continua; `test_data_fora_da_competencia_recusa_somente_item` confirma `FORA_DA_COMPETENCIA` e processamento das demais despesas. Competência inválida e datas de início/fim do período inválidas permanecem bloqueadas até decisão específica.

### T-017 — Corrigir período invertido e devolver o período efetivo
- **O que faz:** para datas válidas e compatíveis com a competência, trocar início/fim quando `inicio > fim` e devolver no resultado as datas efetivamente usadas.
- **Requisitos atendidos:** RN-002; AC-021; decisões 64 e 65.
- **Critério de aceite:** `test_periodo_invertido_e_trocado_na_saida` passa; `test_periodo_ja_ordenado_permanece_igual` passa.

### T-018 — Comparar conteúdo para detectar despesas duplicadas
- **O que faz:** detectar duplicidade entre despesas estruturalmente válidas com IDs diferentes, comparando os campos definidos na spec: fornecedor/descrição com NFC, trim ASCII e comparação sem diferença de caixa; categoria normalizada; data normalizada; valor arredondado; ignorar `tem_nota_fiscal`.
- **Requisitos atendidos:** RN-006, RN-007; decisões 22, 26, 40, 53–58.
- **Critério de aceite:** `test_despesas_com_mesmo_conteudo_sao_duplicadas` e `test_campos_excluidos_nao_alteram_duplicidade` passam.

### T-019 — Marcar duplicidade de conteúdo e apontar item canônico
- **O que faz:** manter a primeira despesa estruturalmente válida como canônica; marcar a seguinte como `IGNORADO`/`DUPLICATA`, preencher `duplicata_de_indice` e zerar o reembolso.
- **Requisitos atendidos:** RN-006; decisões 16, 41, 51 e 52.
- **Critério de aceite:** `test_duplicata_aponta_primeiro_indice_valido` e `test_duplicata_tem_reembolso_zero` passam, inclusive quando o item canônico for recusado por regra de negócio.

### T-020 — Aplicar limites de reembolso
- **O que faz:** calcular valor reembolsável conforme limites por categoria e regras de limite esgotado/aplicado, sem gerar valor negativo ou superior ao solicitado.
- **Requisitos atendidos:** RN-010, RN-011; AC das regras de limite.
- **Critério de aceite:** `test_limite_categoria_aplica_reembolso_parcial` e `test_limite_esgotado_nao_reembolsa` passam.

### T-021 — Não inferir viagem ou diárias a partir de texto livre
- **O que faz:** não aplicar aumento de limite por viagem sem evidência estruturada; emitir aviso `VIAGEM_NAO_INFORMADA` em toda resposta de sucesso; para hotel, avisar quando diárias não forem informadas e não extrair noites da descrição.
- **Requisitos atendidos:** RN-013, RN-014; decisões 4 e 20.
- **Critério de aceite:** `test_aviso_viagem_presente_em_sucesso` e `test_descricao_nao_define_numero_de_diarias` passam.

### T-022 — Contabilizar uma diária por data para o mesmo colaborador
- **O que faz:** evitar contar mais de uma diária de hotel na mesma data para o mesmo colaborador, conforme regra da spec.
- **Requisitos atendidos:** RN-014.
- **Critério de aceite:** `test_hotel_nao_duplica_diaria_na_mesma_data` passa.

### T-023 — Preservar valores exibidos em despesas recusadas ou ignoradas
- **O que faz:** aplicar os campos monetários de saída definidos para despesas estruturalmente válidas recusadas por regra de negócio, duplicadas, zero ou negativas; manter `valor_original` quando aplicável e excluir os valores desses itens dos totais financeiros.
- **Requisitos atendidos:** RN-005 a RN-008; decisões 41, 42, 48 e 49.
- **Critério de aceite:** `test_despesa_recusada_preserva_solicitado_mas_nao_soma` e `test_valor_zero_ou_negativo_fica_zerado_no_resultado` passam.

### T-024 — Calcular resumo e contagens com o conjunto correto de itens
- **O que faz:** calcular `total_itens` e contagens de status apenas para despesas estruturalmente válidas; manter inválidas em `items`, mas fora das contagens e totais.
- **Requisitos atendidos:** RN-015; decisões 25, 28, 36, 46, 48 e 51.
- **Critério de aceite:** `test_total_itens_e_status_excluem_invalidas_estruturais` passa e a soma das contagens coincide com `total_itens`.

### T-025 — Calcular totais financeiros e invariantes
- **O que faz:** calcular `total_solicitado` somente para despesas válidas que chegam ao cálculo de elegibilidade antes dos limites; calcular `total_reembolsavel` pela soma dos pagamentos; calcular `total_nao_reembolsavel = total_solicitado - total_reembolsavel`.
- **Requisitos atendidos:** RN-015, RN-018; decisões 3, 12, 27, 44 e 45.
- **Critério de aceite:** `test_totais_excluem_recusadas_duplicadas_ignoradas_e_invalidas` e `test_invariantes_financeiros_do_resumo` passam.

### T-026 — Montar saída estável e incluir versão da especificação
- **O que faz:** retornar `versao_spec: "0.2"` em sucesso e em erros de lote quando a estrutura de resposta se aplicar; preservar ordem original de `items` e incluir avisos, resultado e resumo conforme contrato.
- **Requisitos atendidos:** RN-016; decisão 31.
- **Critério de aceite:** `test_versao_spec_e_ordem_dos_items` passa para sucesso e erro de lote.

### T-027 — Implementar contrato da CLI e códigos de saída
- **O que faz:** suportar `calcular --input <arquivo> --output <arquivo>`, gravar saída no destino e distinguir sucesso, entrada inválida e erro de I/O pelos códigos definidos.
- **Requisitos atendidos:** RN-017.
- **Critério de aceite:** `test_cli_calcular_input_output` e `test_cli_codigos_de_saida` passam para códigos 0, 2 e 3.

### T-028 — Tratar erros de leitura e escrita da CLI
- **O que faz:** produzir erro operacional claro quando o arquivo de entrada não puder ser lido ou a saída não puder ser gravada, sem apresentar sucesso falso.
- **Requisitos atendidos:** RN-017.
- **Critério de aceite:** `test_cli_arquivo_entrada_inexistente` e `test_cli_destino_sem_permissao` passam.

### T-029 — Transformar exemplos da spec em testes de regressão
- **O que faz:** adicionar testes automatizados para os exemplos normativos da spec e recalcular os resultados esperados conforme as decisões registradas.
- **Requisitos atendidos:** AC-001 a AC-021; decisões 19 e 5.
- **Critério de aceite:** `test_exemplos_spec_v02` passa; os valores esperados são conferidos por cálculo/teste, não rotulados como validados antes da execução.

### T-030 — Completar a matriz de rastreabilidade
- **O que faz:** mapear cada ambiguidade/decisão relevante para RN, AC e teste automatizado, indicando explicitamente quando não houver relação direta.
- **Requisitos atendidos:** seção de rastreabilidade de `spec.md`; decisão 13.
- **Critério de aceite:** `test_matriz_rastreabilidade_completa` ou verificação equivalente confirma que cada AC possui teste identificado e que referências inexistentes são detectadas.

### T-031 — Atualizar documentação de uso e exemplos da CLI
- **O que faz:** documentar pré-requisitos, comando CLI, formato de entrada/saída, códigos de saída, avisos e como executar os testes.
- **Requisitos atendidos:** RN-017 e critérios de entrega da spec.
- **Critério de aceite:** os comandos documentados são executados em ambiente limpo e `test_documentacao_cli` (ou checklist automatizado equivalente) passa.

### T-032 — Executar suíte completa e registrar evidências
- **O que faz:** executar todos os testes após a implementação, corrigir regressões dentro do escopo e registrar comandos/resultados sem declarar testes não executados.
- **Requisitos atendidos:** AC-001 a AC-021; RN-018.
- **Critério de aceite:** a suíte completa passa; os invariantes de resumo passam; nenhuma AC fica sem teste ou com resultado não registrado.

## Pendências de especificação fora das tarefas executáveis

- **Correção 69 (parcialmente resolvida):** data de despesa ausente/malformada/inexistente recusa somente o item como `DADO_INVALIDO`; data válida fora da competência recusa somente o item como `FORA_DA_COMPETENCIA`; em ambos os casos, o lote continua. Implementar e testar conforme RN-006. Permanecem pendentes competência ausente/inválida e datas de início/fim do período ausentes, inválidas ou inexistentes.
- **Requisito do Dia 2:** recebido no envelope da Política v4; seus requisitos ainda precisam ser incorporados de forma integrada na próxima versão da spec e nas tarefas correspondentes.
- **Aprovação:** `spec.md` v0.2 e `DECISIONS.md` permanecem propostas até aprovação formal.

## Definição de pronto

Uma tarefa está concluída quando a alteração cabe em um commit focado, o teste de aceite indicado foi executado e passou, os testes relacionados continuam passando e a documentação/rastreabilidade foi atualizada quando necessário. Não marcar tarefa como concluída apenas por ter escrito o teste ou o código.
