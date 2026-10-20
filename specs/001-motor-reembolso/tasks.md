# Backlog — Motor de Cálculo de Reembolso

**Base:** spec.md v0.2 e DECISIONS.md, revisão de 20/10/2026.  
**Estado:** tarefas não concluídas; execução deve ser comprovada.

Cada tarefa deve resultar em um commit focado.

Os nomes de testes abaixo são propostas. Ao inspecionar a suíte, adaptar os nomes à convenção real e registrar o caminho correspondente, sem perder a cobertura.

Não declarar um teste existente ou aprovado antes de verificá-lo.

## Regras de execução

- Seguir as regras consolidadas, sem implementar versões antigas conflitantes.
- Criar ou atualizar testes junto com o comportamento.
- Executar o aceite e os testes relacionados.
- Atualizar rastreabilidade quando necessário.
- Registrar falhas preexistentes sem apresentá-las como causadas pela alteração.
- Não marcar tarefa como concluída apenas por escrever código ou teste.

A numeração T-001 a T-047 é preservada. A ordem numérica não representa dependência obrigatória.

Antes de fixtures e leitores externos, concluir a inspeção de schemas da T-001. A CLI terá obrigatoriamente `--input`, `--output`, `--politica` e `--cambio` (CONS-008).

Para tarefas financeiras, implementar primeiro os fundamentos necessários: política, parser decimal, validação monetária e conversão.

## Tarefas

### T-001 — Inspecionar projeto, schemas e suíte-base

- Ação: identificar linguagem, módulos, CLI, testes, exemplos e schemas originais de politica-v4.json e cambio.json; executar a suíte-base.
- Referências: RN-017/019/020; preparação para todos os ACs.
- Aceite: registrar caminhos reais, comandos, estrutura dos arquivos externos e resultado-base; reproduzir eventuais falhas preexistentes.

### T-002 — Criar fixtures mínimas reutilizáveis

- Ação: criar fixtures de colaborador, período, despesas, política e câmbio conforme os schemas inspecionados.
- Referências: AC-001 a AC-036.
- Aceite: test_fixtures_validas_carregam passa; fixtures não introduzem campos inventados nem dependência da data atual.
- Dependência: T-001.

### T-003 — Validar envelope e período global

- Ação: validar raiz, colaborador como objeto, periodo e despesas; exigir competência e datas globais válidas no mesmo mês.
- Referências: RN-006/014; AC-006/020.
- Aceite: test_envelope_invalido_rejeita_lote e test_periodo_global_invalido_rejeita_lote passam, sem items/resumo.

### T-004 — Rejeitar JSON principal malformado ou com chaves repetidas

- Ação: detectar sintaxe inválida e chaves repetidas em qualquer objeto da entrada principal.
- Referências: RN-014; AC-019; correção 67.
- Aceite: test_json_malformado e test_chave_repetida_retornam_json_invalido passam sem resultado financeiro parcial.

### T-005 — Validar colaborador obrigatório

- Ação: exigir id, nome e centro_custo textuais e não vazios.
- Referências: RN-014; AC-020; correção 68.
- Aceite: test_colaborador_obrigatorio_invalido_rejeita_lote cobre ausência, vazio, espaços e tipo incorreto de cada campo.

### T-006 — Ignorar campos desconhecidos da entrada principal

- Ação: aceitar extras na raiz, colaborador, período e despesas sem influência funcional.
- Referências: RN-013; AC-013; correções 62–64.
- Aceite: test_extras_da_entrada_nao_alteram_resultado passa; tolerância não é aplicada implicitamente aos arquivos externos.

### T-007 — Validar estrutura das despesas

- Ação: validar objeto de despesa, data, categoria, descrição, fornecedor, valor e booleano fiscal conforme o contrato consolidado.
- Referências: RN-006/009/013/014/022/023; AC-006/009/013/027.
- Aceite: test_despesa_invalida_nao_interrompe_lote e test_booleano_fiscal_exige_booleano_real passam.
- Dependências: parser e validador monetário de T-036/T-037.

### T-008 — Ordenar todos os erros estruturais

- Ação: coletar erros na ordem id, data, categoria, descricao, fornecedor, valor, tem_nota_fiscal e moeda.
- Referências: RN-014; AC-014; correções 59–61.
- Aceite: test_ordem_dos_erros_independe_das_chaves passa com permutações da mesma entrada.

### T-009 — Manter inválidos na saída

- Ação: retornar um item por despesa; excluir estruturalmente inválidos de total_itens e contagens.
- Referências: RN-014/018; AC-014/018.
- Aceite: test_invalido_permanece_em_items e test_contagens_excluem_invalidos_estruturais passam.

### T-010 — Gerar ID somente quando ausente

- Ação: gerar ID ausente mesmo se outro campo estiver inválido; ID presente inválido retorna null.
- Referências: RN-014; AC-014; correções 1/23/24/38.
- Aceite: test_id_ausente_e_gerado e test_id_presente_invalido_nao_e_substituido passam.

### T-011 — Resolver colisões de IDs gerados

- Ação: usar índice original zero-based e sufixos; considerar todos os IDs fornecidos, inclusive de itens inválidos.
- Referências: RN-014; AC-014; correções 8/17/18/39/47/50.
- Aceite: test_id_gerado_usa_indice_original e test_id_gerado_resolve_colisoes passam.

### T-012 — Normalizar IDs somente para comparação

- Ação: aplicar trim ASCII externo e comparação sem caixa; preservar ID original válido.
- Referências: RN-007/014; AC-007/014; correções 32/33/37.
- Aceite: test_ids_equivalentes_por_caixa_e_espacos e test_id_original_preservado passam.

### T-013 — Recusar somente repetição posterior de ID

- Ação: manter primeiro ID estruturalmente válido; repetição usa DADO_INVALIDO e erro ID_REPETIDO.
- Referências: RN-007/014; AC-007; correções 6/21/26/30/34/46.
- Aceite: test_id_repetido_recusa_so_posterior e test_item_invalido_nao_reserva_id passam.

### T-014 — Centralizar half-up após conversão

- Ação: implementar quantização decimal exata do resultado convertido, sem normalizar valores originais inválidos.
- Referências: RN-009/021; AC-009/026.
- Aceite: test_half_up_em_empates passa; test_entrada_com_tres_casas_nao_e_arredondada confirma a separação.
- Dependência: T-036.

### T-015 — Implementar elegibilidade sem efeito em saldos

- Ação: avaliar categoria e período; registrar impedimentos em ordem; separar elegibilidade, cálculo preliminar e atualização de saldo.
- Referências: RN-006/011/015/019; AC-006/011/015.
- Aceite: test_inelegivel_nao_consume_saldo e test_categoria_e_periodo_tem_ordem_estavel passam.

### T-016 — Validar datas individuais e competência

- Ação: recusar somente item com data ausente/malformada/inexistente; distinguir data válida fora do período.
- Referências: RN-006; AC-006; correção 69.
- Aceite: test_data_invalida_afeta_so_item e test_data_fora_do_periodo_recusa_so_item passam; itens seguintes continuam.

### T-017 — Corrigir e retornar período invertido

- Ação: trocar inicio/fim somente quando ambos forem válidos e compatíveis com a competência.
- Referências: RN-006; AC-021; correções 65/66.
- Aceite: test_periodo_invertido_e_corrigido e test_saida_retorna_periodo_efetivo passam.

### T-018 — Construir chave de duplicidade por conteúdo

- Ação: combinar data, categoria normalizada, fornecedor/descrição normalizados, moeda efetiva e valor original válido.
- Referências: RN-007; AC-007/036; CONS-004.
- Aceite: test_chave_de_conteudo_normalizada e test_moedas_diferentes_nao_sao_duplicatas passam; NF e extras não alteram a chave.

### T-019 — Apontar canônico e ignorar duplicata

- Ação: manter primeiro canônico estruturalmente válido, inclusive se inelegível; duplicata reembolsa zero e referencia o índice.
- Referências: RN-007; AC-007; correções 51/52.
- Aceite: test_duplicata_aponta_canonico_inelegivel e test_duplicata_nao_consome_saldo passam.

### T-020 — Calcular resultado preliminar por limites

- Ação: calcular menor valor entre convertido e saldos aplicáveis, sem consumir saldo nesta etapa.
- Referências: RN-003/024; AC-003/028.
- Aceite: test_fronteiras_do_limite e test_calculo_preliminar_nao_altera_saldo passam.

### T-021 — Não inferir viagem ou diárias

- Ação: emitir VIAGEM_NAO_INFORMADA em todo sucesso e DIARIAS_NAO_INFORMADAS na hospedagem válida; não interpretar texto.
- Referências: RN-005/010; AC-005/010.
- Aceite: test_texto_nao_amplia_limite e test_sucesso_vazio_contem_aviso_viagem passam.

### T-022 — Compartilhar diária por data

- Ação: impedir multiplicação do limite diário de hospedagem pelo número de despesas da mesma data.
- Referências: RN-010; AC-010.
- Aceite: test_hospedagens_compartilham_limite_da_data passa com política explícita na fixture.

### T-023 — Preservar valores informativos sem confundir totais

- Ação: preencher valor_original aceito, valor_convertido e valor_solicitado conforme o contrato, inclusive em recusas/duplicatas convertíveis.
- Referências: RN-007/016/026; AC-016/031/032; CONS-005/006.
- Aceite: test_recusa_convertivel_preserva_valor e test_valor_original_invalido_retorna_null passam.

### T-024 — Calcular contagens

- Ação: contar somente itens estruturalmente válidos, incluindo repetição de ID e duplicata por conteúdo.
- Referências: RN-018; AC-018.
- Aceite: test_contagens_particionam_itens_validos passa com itens válidos, inválidos, repetidos e duplicados.

### T-025 — Calcular solicitado, reembolso e diferença

- Ação: usar a base elegível definida em RN-016; incluir recusa exclusiva por limite; excluir bloqueio fiscal e inelegibilidades.
- Referências: RN-016; AC-016/031; CONS-002.
- Aceite: test_recusa_por_limite_permanece_no_solicitado e test_nao_reembolsavel_e_solicitado_menos_pagamento passam.

### T-026 — Montar saída estável e versão

- Ação: retornar versao_spec "0.2", período efetivo, todos os itens em ordem e campos definidos.
- Referências: RN-014/017/018/026; AC-014/017/018/032.
- Aceite: test_saida_preserva_ordem_e_versao passa para sucesso e falha global.

### T-027 — Implementar contrato e códigos da CLI

- Ação: preservar calcular --input/--output e exigir `--politica` e `--cambio` além de `--input` e `--output`, conforme CONS-008.
- Referências: RN-017; AC-017.
- Aceite: test_cli_codigos_0_2_3 e test_cli_quatro_argumentos_obrigatorios passam; política/câmbio inválidos usam erro semântico e código 2.

### T-028 — Tratar I/O da entrada principal e escrita

- Ação: informar falha operacional sem falso sucesso e sem misturar logs no JSON.
- Referências: RN-017; AC-017.
- Aceite: test_cli_entrada_inexistente e test_cli_falha_de_escrita passam com código 3.

### T-029 — Recalcular a fixture original

- Ação: inspecionar os 14 itens originais e substituir expectativas antigas incompatíveis com Envelope 2.
- Referências: seção 9 do spec; AC-001 a AC-036 conforme aplicáveis.
- Aceite: test_fixture_original_contrato_consolidado passa; resultados esperados são revisados sem reutilizar o quadro antigo como gabarito.

### T-030 — Completar rastreabilidade original

- Ação: ligar AMB-001 a AMB-016 e AC-001 a AC-021 aos testes reais; corrigir referências de correções.
- Referências: seção 10 do spec; CONS-007.
- Aceite: verificação documental confirma IDs existentes e nenhum AC dessa faixa sem teste identificado.

### T-031 — Documentar execução da CLI

- Ação: documentar pré-requisitos, os quatro argumentos obrigatórios, comandos reais, códigos e estrutura da saída consolidada.
- Referências: RN-017; AC-017.
- Aceite: executar os comandos documentados em ambiente limpo ou registrar precisamente impedimento reproduzível.

### T-032 — Executar regressão do contrato consolidado

- Ação: executar testes das regras originais já adaptadas ao Envelope 2, sem reintroduzir expectativas substituídas.
- Referências: AC-001 a AC-021.
- Aceite: registrar comando, resultado e falhas; somente marcar concluída com os testes correspondentes aprovados.

### T-033 — Ler e validar política externa

- Ação: implementar o schema real da política, validar limites/periodicidades e rejeitar arquivo ausente, ilegível ou inválido.
- Referências: RN-019; AC-022.
- Aceite: test_politica_valida e test_politica_invalida_sem_resultado_financeiro passam.
- Dependência: T-001.

### T-034 — Aplicar fallback e categorias da política

- Ação: centro desconhecido usa padrao; categoria ausente é recusada individualmente.
- Referências: RN-011/019; AC-011/033.
- Aceite: test_cc_desconhecido_usa_padrao e test_categoria_ausente_na_politica_recusa_item passam.

### T-035 — Ler e validar câmbio integralmente

- Ação: implementar schema real e validar todos os registros, datas, moedas, valores e duplicatas moeda+data.
- Referências: RN-020; AC-023.
- Aceite: test_cambio_invalido_rejeita_arquivo e test_cotacao_duplicada_mesmo_valor_rejeita passam, inclusive para registros não usados.
- Dependências: T-001/T-036.

### T-036 — Implementar parser decimal exato

- Ação: preservar lexemas, detectar notação científica e casas originais; usar decimal/racional exato e aceitar zeros finais nas cotações.
- Referências: RN-009/020/021/023; AC-009/023/026/027.
- Aceite: test_parser_preserva_lexema e test_cotacao_com_zeros_finais_e_aceita passam sem ponto flutuante binário.

### T-037 — Validar valor original e teto

- Ação: aceitar valor positivo convencional com até duas casas e teto inclusivo na moeda original.
- Referências: RN-008/009/023; AC-008/009/027.
- Aceite: test_valor_original_valido e test_valor_original_invalido_afeta_so_item cobrem ausência, null, booleano, string, zero, negativo, três casas, científico e teto.

### T-038 — Selecionar moeda e cotação

- Ação: assumir BRL quando ausente; validar moeda presente; preferir data exata, senão anterior mais recente; nunca futura.
- Referências: RN-022; AC-024/025/030.
- Aceite: test_brl_sem_lookup_individual, test_cotacao_anterior e test_cotacao_futura_nao_e_usada passam.

### T-039 — Converter por despesa

- Ação: multiplicar exatamente, aplicar half-up ao resultado em BRL e converter em centavos; tratar conversão zero e overflow individual.
- Referências: RN-021; AC-026/030.
- Aceite: test_conversao_half_up_por_item, test_conversao_arredondada_a_zero e test_overflow_nao_aborta_lote passam.

### T-040 — Agregar e consumir limites diários/mensais

- Ação: manter chaves definidas, processar em ordem original e consumir ambos os saldos pelo reembolso final.
- Referências: RN-001/002/024; AC-001/002/028.
- Aceite: test_limites_simultaneos e test_saldos_consumidos_so_pelo_pagamento passam.

### T-041 — Aplicar teto de representação comercial

- Ação: respeitar permissão da categoria e usar teto diário efetivo mínimo entre política e 300.00; manter limite mensal aplicável.
- Referências: RN-019; AC-034; E2-038/CONS-001.
- Aceite: test_representacao_politica_inferior_e_superior passa para 200.00/300.00/500.00 e para categoria ausente ou permitida sem limite diário próprio.

### T-042 — Aplicar nota fiscal depois dos limites

- Ação: avaliar preliminar >100.00; sem nota, zerar pagamento sem consumir saldos; manter motivos de redução preliminar aplicáveis.
- Referências: RN-004/025; AC-004/029.
- Aceite: test_nf_sobre_preliminar e test_bloqueio_fiscal_nao_consome_saldos passam para abaixo/igual/acima de 100.00.

### T-043 — Consolidar motivos e serialização

- Ação: usar catálogo único, lista ordenada sem duplicações, singular compatível e números monetários com duas casas no texto JSON.
- Referências: RN-015/025/026; AC-015/032; CONS-003/005.
- Aceite: test_motivos_multiplos_ordenados e test_json_monetario_tem_duas_casas passam; verificar texto serializado e não apenas valores parseados.

### T-044 — Calcular bruto convertido e completude

- Ação: somar convertíveis antes das restrições, inclusive duplicatas/inelegíveis; excluir impossíveis de converter e marcar incompletude.
- Referências: RN-016/026; AC-030/031; CONS-002/006.
- Aceite: test_bruto_inclui_convertiveis_inelegiveis e test_falha_de_conversao_marca_totais_incompletos passam com invariantes.

### T-045 — Fechar rastreabilidade e hospedagem proibida

- Ação: cobrir AC-022 a AC-036, implementar/confirmar a proibição de hospedagem em CC-ENG-PLATAFORMA e atualizar a matriz completa.
- Referências: RN-019 a RN-026; AC-022 a AC-036; E2-038/CONS-007.
- Aceite: test_hospedagem_eng_plataforma_proibida passa mesmo com permissão genérica; cada AC novo aponta para teste real.
- Observação: se a alteração funcional e a documentação não couberem em um commit focado, registrar uma subtarefa identificada antes da execução.

### T-046 — Documentar política, câmbio e novos totais

- Ação: documentar schemas reais após T-001, os quatro argumentos obrigatórios, erros globais, códigos de motivos e bases dos quatro totais.
- Referências: RN-016/017/019/020/026; AC-017/022/023/031/032.
- Aceite: exemplo executável usa arquivos reais válidos; documentação não contém aliases removidos nem parâmetros de CLI inventados.

### T-047 — Executar suíte final e registrar evidências

- Ação: executar testes unitários, integração e regressão; conferir documentação e invariantes.
- Referências: AC-001 a AC-036.
- Aceite: todos os ACs têm teste identificado e aprovado; comandos e resultados reais estão registrados; não existem regras antigas conflitantes nos três documentos.

## Matriz de execução dos critérios de aceite

Os 36 critérios AC-001 a AC-036 devem ser rastreados na implementação por: `AC | RN | T | arquivo::teste | comando | resultado | evidência/commit`. Os nomes de testes previstos nas tarefas são hipóteses de planejamento, não testes já existentes. Até execução registrada, cada resultado é **NÃO EXECUTADO**. T-030 e T-045 devem completar os vínculos com caminhos reais; T-047 só poderá ser concluída após execução e evidências.

## Definição de pronto

Uma tarefa está concluída quando:

- A alteração é focada.
- O teste de aceite foi executado e passou.
- Os testes relacionados continuam passando.
- A rastreabilidade foi atualizada quando necessário.
- O resultado real foi registrado.

Uma implementação entregue exige T-047 concluída. Esta revisão documental não conclui tarefas de implementação.

## Pendências atuais

- Inspecionar repositório, schemas externos e suíte.
- Implementar o contrato consolidado.
- Recalcular a fixture original.
- Executar testes e registrar evidências.

Não há pendência de decisão sobre:

- Teto absoluto de 300.00 para representação comercial.
- Tratamento individual de data inválida.
- Rejeição global de período obrigatório inválido.
- Formatação de valores aceitos com duas casas.
- Exigência fiscal sobre o valor preliminar reembolsável.