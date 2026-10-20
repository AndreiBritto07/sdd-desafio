# Backlog de implementação: motor de reembolso

**Versão:** 0.2 · **Data:** 2026-10-20
**Base:** `spec.md` v0.2 e `DECISIONS.md` v0.2, ambos propostos.
**Regra:** cada tarefa cabe em um commit focado. Os nomes de teste são identificadores propostos e devem ser adaptados à convenção do repositório, sem perder cobertura.
**Estado:** nenhum critério é marcado como concluído sem execução real registrada.

## Regras para concluir uma tarefa

- Alteração focada, com testes escritos junto ao código.
- Executar o teste de aceite e os testes relacionados, e registrar o resultado real.
- Não alterar regras fora do escopo da tarefa.
- Manter `spec.md`, `DECISIONS.md` e a rastreabilidade (seção 11 da spec) consistentes.

## Pré-requisitos

- **Correção 69:** bloqueia apenas os casos de competência ausente ou inválida e de datas inexistentes em `periodo`, que ficam em T-015. A comparação inclusiva de T-015 e a inversão de T-014 são liberadas (RN-006).
- **Correção 70:** T-026 depende dela.
- **Correção 71:** T-018 depende dela.
- **Correção 72:** T-013 e T-016 dependem dela.
- **Correções 73 e 74:** T-006 depende delas.
- **Correção 75:** T-024 e T-026 seguem o escopo de totais definido em `DECISIONS.md`.

## Fundação

**T-001 — Mapear o repositório e executar a suíte-base**
- O que faz: identificar linguagem, módulos, comandos, convenções e testes existentes. Executar sem alterar comportamento.
- Refs: suporte a AC-001 a AC-021.
- Aceite: resultado-base registrado. Falhas pré-existentes são reproduzíveis e documentadas.

**T-002 — Fixtures reutilizáveis**
- O que faz: builders de colaborador, período, despesa e resposta esperada. Inclui os 14 itens do exemplo (spec §9).
- Refs: suporte a todos os ACs; base para T-030.
- Testes: `test_fixtures_validas_podem_ser_carregadas`.

## Contrato de entrada

**T-003 — Parser JSON estrito**
- O que faz: rejeitar JSON inválido e chave repetida em qualquer objeto, com `JSON_INVALIDO` e sem resultado parcial.
- Refs: RN-014; AC-019.
- Testes: `test_json_malformado_retorna_json_invalido`, `test_chave_json_repetida_rejeita_lote`.

**T-004 — Envelope e colaborador**
- O que faz: validar presença e tipo de `colaborador.id`, `nome` e `centro_custo`, além de `periodo` e `despesas`. Qualquer falha rejeita o lote com `ENTRADA_INVALIDA`.
- Refs: RN-014; AC-020.
- Testes: `test_colaborador_incompleto_rejeita_lote` (ausente, vazio, só espaços e tipo incorreto, em cada campo); `test_envelope_invalido_retorna_entrada_invalida`.

**T-005 — Chaves exatas, campos extras e booleano**
- O que faz: ignorar campos extras na raiz, no envelope e nas despesas. `tem_nota_fiscal` é obrigatório e booleano real: ausente gera `CAMPO_OBRIGATORIO`; `"false"` gera `TIPO_OU_FORMATO_INVALIDO`. Aliases não substituem campos.
- Refs: RN-013; AC-013.
- Testes: `test_chaves_exatas_e_booleano`, `test_campos_extras_sao_ignorados`.

**T-006 — Validação estrutural da despesa**
- O que faz: validar campos obrigatórios, datas, categoria, descrição, fornecedor e valor numérico finito. Registrar todos os erros em `erros`, em ordem fixa (spec §8, passo 6). String só com espaços gera `CAMPO_OBRIGATORIO` (correção 73). Data inexistente gera `TIPO_OU_FORMATO_INVALIDO` (correção 74).
- Refs: RN-014; AC-014.
- Testes: `test_entrada_invalida_por_item`, `test_erros_estruturais_ordenados`, `test_ordem_dos_erros_independe_da_ordem_json`, `test_string_so_espacos_e_campo_obrigatorio`, `test_data_inexistente_e_erro_estrutural`.

**T-007 — Despesa estruturalmente inválida na saída**
- O que faz: manter a despesa inválida em `items` com `RECUSADO`, motivo `DADO_INVALIDO`, `erros` preenchidos e `id: null` quando o ID informado for inválido. Excluí-la de `recusados`, `total_itens` e totais.
- Refs: RN-014, RN-018; AC-014.
- Testes: `test_despesa_invalida_permanece_em_items`, `test_despesa_invalida_fora_do_resumo`.

## Identificadores

**T-008 — Gerar ID somente quando ausente**
- O que faz: gerar `gerado-{índice}` apenas quando `id` não existe. ID presente inválido resulta em `id: null`, sem substituto.
- Refs: RN-014; AC-014.
- Testes: `test_id_ausente_e_gerado`, `test_id_presente_invalido_nao_e_substituido`.

**T-009 — Unicidade dos IDs gerados**
- O que faz: usar o índice zero-based da lista completa. Evitar colisão com todos os IDs fornecidos (inclusive de itens inválidos) e com IDs já gerados. Sufixos `-1`, `-2` etc.
- Refs: RN-014; AC-014.
- Testes: `test_id_gerado_usa_indice_original`, `test_id_gerado_resolve_colisoes_com_sufixo`.

**T-010 — ID repetido e normalização de ID**
- O que faz: comparar IDs com trim ASCII e sem diferença de caixa, preservando o ID original na saída. A ocorrência posterior é `RECUSADO` com motivo `ID_REPETIDO` e `erros` vazio. O lote continua.
- Refs: RN-007, RN-014; AC-014.
- Testes: `test_id_repetido_recusa_somente_ocorrencia_posterior`, `test_id_com_espacos_e_caixa_diferente_e_repetido`, `test_id_original_e_preservado_na_saida`.

## Valores e categoria

**T-011 — Arredondamento half-up**
- O que faz: centralizar o arredondamento monetário a duas casas, metade para cima, sem depender do arredondamento binário padrão da linguagem.
- Refs: RN-009; AC-009.
- Testes: `test_arredondamento_half_up` (empates, positivos e 0,004).

**T-012 — Normalização de categoria**
- O que faz: trim ASCII e A-Z para a-z no campo `categoria`. Aceitos apenas `alimentacao`, `transporte_urbano` e `hospedagem`. Sem aliases.
- Refs: RN-011; AC-011.
- Testes: `test_normalizacao_categoria`.

**T-013 — Valor zero e negativo**
- O que faz: negativo: `IGNORADO` com motivo `ESTORNO_NAO_PROCESSADO`. Zero: `IGNORADO` com motivo `VALOR_ZERO`. Solicitado e reembolsável zerados. Fora da deduplicação (correção 72).
- Refs: RN-008; AC-008, AC-009.
- Testes: `test_estorno_nao_processado`, `test_valor_zero_ou_negativo_fica_zerado_no_resultado`.

## Período

**T-014 — Inversão de período**
- O que faz: quando `inicio` e `fim` são datas válidas e `inicio > fim`, trocar e devolver o período corrigido. Não trata datas inexistentes nem competência ausente (correção 69).
- Refs: RN-006; AC-021.
- Testes: `test_periodo_invertido_e_corrigido`, `test_periodo_ja_ordenado_permanece_igual`.

**T-015 — Competência inclusiva**
- O que faz: aceitar `inicio <= data <= fim` e recusar com `FORA_DA_COMPETENCIA` quando a data estiver fora do intervalo.
- Refs: RN-006; AC-006.
- Bloqueio parcial: casos de competência ausente ou inválida, datas inexistentes em `periodo` e incompatibilidade com o mês dependem da correção 69. Não implementar esses casos antes da decisão. A comparação inclusiva está liberada.
- Testes: `test_competencia_inclusiva`.

## Regras de negócio

**T-016 — Deduplicação por conteúdo**
- O que faz: entre IDs diferentes e valores positivos, comparar data normalizada, categoria normalizada, fornecedor e descrição (NFC, trim ASCII externo, sem diferença de caixa) e valor arredondado a duas casas. Ignorar `tem_nota_fiscal` e campos extras.
- Refs: RN-007; AC-007.
- Testes: `test_duplicata_conteudo_com_ids_diferentes`, `test_campos_excluidos_nao_alteram_duplicidade`, `test_fornecedor_com_caixa_diferente_e_duplicata`.

**T-017 — Canônico e duplicata**
- O que faz: o primeiro item válido com o conteúdo é canônico, mesmo se depois for recusado. As cópias são `IGNORADO` com motivo `DUPLICATA`, com reembolso zero e `duplicata_de_indice` apontando para o canônico.
- Refs: RN-007; AC-007.
- Testes: `test_duplicata_aponta_canonico`, `test_canonico_recusado_nao_paga_copia`, `test_item_invalido_nao_vira_canonico`.

**T-018 — Precedência de motivos**
- O que faz: aplicar a ordem da spec §8 (correção 71). Um motivo principal por item.
- Refs: RN-015; AC-015.
- Testes: `test_precedencia_motivos`, `test_fora_da_competencia_prevalece_sobre_nota`.

**T-019 — Nota fiscal obrigatória**
- O que faz: exigir nota quando o valor original positivo, antes de arredondar e limitar, for estritamente maior que R$ 100.
- Refs: RN-004; AC-004.
- Testes: `test_nota_fiscal_acima_de_100`, `test_100_004_sem_nota_e_recusado`.

**T-020 — Dias civis e categoria fora da política**
- O que faz: aplicar as regras a sábados, domingos e feriados, sem restrição de dias úteis. Recusar com `CATEGORIA_NAO_PREVISTA` categorias fora do vocabulário.
- Refs: RN-011, RN-012; AC-011, AC-012.
- Testes: `test_fim_de_semana_aplica_regras`, `test_categoria_nao_prevista_recusa`.

**T-021 — Limites diários**
- O que faz: agregar por colaborador, data e categoria. Consumir o saldo na ordem de entrada. Igualdade ao teto é integral. Saldo zero recusa com `LIMITE_ESGOTADO`.
- Refs: RN-001, RN-002, RN-003; AC-001, AC-002, AC-003.
- Testes: `test_agregacao_diaria_alimentacao`, `test_distribuicao_teto_ordem_entrada`, `test_fronteira_limite_alimentacao`.

**T-022 — Viagem sem acréscimo**
- O que faz: não aplicar acréscimo de 50% por viagem. Emitir `VIAGEM_NAO_INFORMADA` em `avisos` do envelope, em todo sucesso, inclusive com lista vazia.
- Refs: RN-005; AC-005.
- Testes: `test_viagem_nao_aplica_acrescimo`, `test_aviso_viagem_presente_em_sucesso`.

**T-023 — Diárias de hospedagem**
- O que faz: considerar uma diária por data e colaborador, compartilhada entre hospedagens. Limite de R$ 250. Emitir `DIARIAS_NAO_INFORMADAS` em `items[].avisos` de cada hospedagem estruturalmente válida. Não extrair número de texto livre.
- Refs: RN-010; AC-010.
- Testes: `test_diarias_nao_extraidas_do_texto`, `test_hotel_nao_duplica_diaria_na_mesma_data`.

## Saída e totais

**T-024 — Valores preservados em itens não elegíveis**
- O que faz: manter `valor_solicitado` arredondado em itens recusados por regra e em duplicatas, sem contá-los nos totais. Seguir o escopo de totais da correção 75.
- Refs: RN-016; AC-016.
- Testes: `test_despesa_recusada_preserva_solicitado_mas_nao_soma`, `test_totais_excluem_nao_elegiveis`.

**T-025 — Resumo e contagens**
- O que faz: `total_itens`, `aprovados`, `parciais`, `recusados` e `ignorados` contam apenas itens estruturalmente válidos. A soma das contagens é igual a `total_itens`.
- Refs: RN-016, RN-018; AC-016, AC-018.
- Testes: `test_total_itens_e_status_excluem_invalidas_estruturais`, `test_contagens_particionam_itens_validos`.

**T-026 — Totais financeiros e invariantes**
- O que faz: `total_solicitado` = soma de `valor_solicitado` de `APROVADO` e `PARCIAL` (correção 70). `total_reembolsavel` = soma dos pagamentos. `total_nao_reembolsavel` = diferença. Verificar que nenhum pagamento é negativo nem maior que o solicitado.
- Refs: RN-016, RN-018; AC-016, AC-018.
- Testes: `test_invariantes_financeiros`.

**T-027 — Saída estável**
- O que faz: `versao_spec: "0.2"` em sucesso e em falha de lote. `colaborador` e `periodo` (já corrigido) incluídos. Ordem original de `items`.
- Refs: spec §4.2 e §4.3; suporte a AC-016 e AC-018.
- Testes: `test_versao_spec_e_ordem_dos_items`, `test_saida_de_sucesso_contem_periodo_corrigido`.

## CLI

**T-028 — Contrato da CLI**
- O que faz: `calcular --input <arquivo> --output <arquivo>`. Códigos `0`, `2` e `3`. Logs fora do JSON de resultado.
- Refs: RN-017; AC-017.
- Testes: `test_cli_codigos_de_saida`, `test_cli_calcular_input_output`, `test_mesma_entrada_mesma_saida` (determinismo de RN-017).

**T-029 — Erros de leitura e escrita**
- O que faz: erro operacional claro quando a entrada não pode ser lida ou a saída não pode ser gravada, sem sucesso falso. Em `ERRO_IO`, nenhum arquivo de saída é gravado e a mensagem vai para stderr. Em falha de lote, nenhum arquivo de saída parcial.
- Refs: RN-017; AC-017; spec §4.3.
- Testes: `test_cli_arquivo_entrada_inexistente`, `test_cli_destino_sem_permissao`, `test_falha_de_lote_nao_grava_saida_parcial`.

## Verificação

**T-030 — Exemplo da spec como regressão**
- O que faz: transformar os 14 itens da spec §9 em teste de regressão. Comparar com a execução real.
- Refs: suporte a AC-001 a AC-021; spec §9.
- Testes: `test_exemplo_spec_v02`. Os valores são conferidos pela execução e não são marcados como validados antes dela.

**T-031 — Matriz de rastreabilidade**
- O que faz: confirmar que cada AC tem teste identificado e que referências inexistentes são detectadas. Confirmar que os IDs de tarefa citados na spec §11 existem neste backlog e que a spec §11 lista os mesmos testes deste documento.
- Refs: spec §11; AMB-001 a AMB-016.
- Testes: `test_matriz_rastreabilidade_completa` ou verificação equivalente.

**T-032 — Documentação de uso**
- O que faz: pré-requisitos, comando CLI, formato de entrada e saída, códigos de saída, avisos e como executar os testes.
- Refs: RN-017.
- Aceite: comandos documentados executados em ambiente limpo.

**T-033 — Suíte completa**
- O que faz: executar todos os testes, corrigir regressões dentro do escopo e registrar comandos e resultados.
- Refs: AC-001 a AC-021; RN-018.
- Aceite: suíte completa passa; nenhum AC sem teste ou sem resultado registrado.

## Pendências fora das tarefas

- **Correção 69:** competência ausente ou inválida, datas inexistentes e incompatibilidade com o mês. Não implementar política definitiva antes da decisão.
- **Correção 75:** escopo de totais definido (ver `DECISIONS.md`). T-024 e T-026 seguem esse escopo, sem renomear campos.
- **Dia 2:** requisito não recebido. Revisar `spec.md` e acrescentar tarefas quando chegar.
- **Aprovação:** `spec.md` e `DECISIONS.md` seguem propostos até aprovação formal.

## Definição de pronto

A tarefa está concluída quando a alteração cabe em um commit focado, o teste de aceite passou, os testes relacionados continuam passando e a rastreabilidade foi atualizada. Escrever o teste ou o código não basta.