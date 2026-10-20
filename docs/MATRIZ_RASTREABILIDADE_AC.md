# Matriz de rastreabilidade — execução de 82 testes (20/10/2026)

**Origem da execução:** terminal apresentado pelo responsável: `python -m unittest discover -s tests -v` → `Ran 82 tests in 3.731s`, `OK`, sem `skipped`. A execução foi feita após gerar `resultado-envelope.json` pela CLI. **Não houve execução independente nesta auditoria.**

**Interpretação:** vínculos abaixo são extraídos dos nomes reais dos testes e das referências das tarefas; não equivalem a validação exaustiva de cada AC. Os testes sem prefixo AC também fazem parte dos 82 testes, mas nem todos foram atribuídos automaticamente a um AC. Tarefas documentais exigem evidência adicional.

| AC | RN (spec) | Tarefas relacionadas | Testes identificados | Situação |
|---|---|---|---|---|
| AC-001 | RN-001/002 | T-001, T-002, T-003, T-027, T-028, T-029, T-030, T-032, T-033, T-035, T-036, T-040, T-045, T-047 | `tests/test_criterios_complementares.py::test_ac001_limite_diario_na_ordem_72_50_e_38` | Evidência relacionada; abrangência integral não auditada |
| AC-002 | RN-002 | a conferir | `tests/test_criterios_complementares.py::test_ac002_ordem_invertida_38_e_72_50` | Evidência relacionada; abrangência integral não auditada |
| AC-003 | RN-003 | T-020 | `tests/test_lacunas_aceite.py::test_ac003_fronteiras_do_limite` | Evidência relacionada; abrangência integral não auditada |
| AC-004 | RN-004 | T-042 | `tests/test_auditoria_financeira.py::test_ac004_nota_fiscal_100_exato_nao_bloqueia` | Evidência relacionada; abrangência integral não auditada |
| AC-005 | RN-005 | T-021 | `tests/test_lacunas_aceite.py::test_ac005_viagem_textual_nao_amplia_limite`; `tests/test_lacunas_aceite.py::test_ac005_lista_vazia_mantem_aviso_e_totais` | Evidência relacionada; abrangência integral não auditada |
| AC-006 | RN-006 | T-003, T-007, T-015, T-016, T-036, T-037 | `tests/test_lacunas_aceite.py::test_ac006_periodo_inclusivo`; `tests/test_lacunas_aceite.py::test_ac006_data_invalida_nao_aborta_lote` | Evidência relacionada; abrangência integral não auditada |
| AC-007 | RN-007 | T-012, T-013, T-018, T-019 | `tests/test_criterios_complementares.py::test_ac007_id_repetido_e_identificacao`; `tests/test_lacunas_aceite.py::test_ac007_id_equivalente_casefold_trim_ascii`; `tests/test_lacunas_aceite.py::test_ac007_conteudo_duplicado_aponta_canonico_inelegivel` | Evidência relacionada; abrangência integral não auditada |
| AC-008 | RN-008 | T-037 | `tests/test_lacunas_aceite.py::test_ac008_zero_negativo_nao_compensam` | Evidência relacionada; abrangência integral não auditada |
| AC-009 | RN-009 | T-014, T-036 | `tests/test_lacunas_aceite.py::test_ac009_aceita_inteiro_uma_e_duas_casas`; `tests/test_lacunas_aceite.py::test_ac009_tres_casas_invalida_sem_arredondar` | Evidência relacionada; abrangência integral não auditada |
| AC-010 | RN-010 | T-022 | `tests/test_lacunas_aceite.py::test_ac010_hospedagens_compartilham_diaria`; `tests/test_lacunas_aceite.py::test_ac010_texto_duas_diarias_nao_multiplica_teto` | Evidência relacionada; abrangência integral não auditada |
| AC-011 | RN-011 | T-034 | `tests/test_lacunas_aceite.py::test_ac011_normalizacao_ascii_sem_aliases` | Evidência relacionada; abrangência integral não auditada |
| AC-012 | RN-012 | a conferir | `tests/test_lacunas_aceite.py::test_ac012_fim_de_semana_permitido` | Evidência relacionada; abrangência integral não auditada |
| AC-013 | RN-013 | T-006 | `tests/test_lacunas_aceite.py::test_ac013_extras_ignorados`; `tests/test_lacunas_aceite.py::test_ac013_booleano_estrito_e_chaves_exatas` | Evidência relacionada; abrangência integral não auditada |
| AC-014 | RN-014 | T-008, T-009, T-010, T-011, T-026 | `tests/test_lacunas_aceite.py::test_ac014_erro_estrutural_em_ordem_fixa`; `tests/test_lacunas_aceite.py::test_ac014_geracao_id_colisao_com_fornecido_invalido`; `tests/test_lacunas_aceite.py::test_ac014_id_presente_invalido_nao_gera_substituto`; `tests/test_lacunas_aceite.py::test_ac014_id_ausente_em_item_invalido_e_gerado` | Evidência relacionada; abrangência integral não auditada |
| AC-015 | RN-015 | T-043 | `tests/test_lacunas_aceite.py::test_ac015_motivos_sao_unicos_e_singular_primeiro` | Evidência relacionada; abrangência integral não auditada |
| AC-016 | RN-016 | T-023, T-025 | `tests/test_lacunas_aceite.py::test_ac016_recusa_somente_por_limite_conta_solicitado` | Evidência relacionada; abrangência integral não auditada |
| AC-017 | RN-017 | T-001, T-027, T-028, T-031, T-046 | `tests/test_criterios_complementares.py::test_ac017_cli_sucesso_e_erro_global`; `tests/test_lacunas_aceite.py::test_ac017_cli_argumento_obrigatorio_ausente_saida_2`; `tests/test_lacunas_aceite.py::test_ac017_cli_io_entrada_inexistente_saida_3`; `tests/test_lacunas_aceite.py::test_ac017_cli_escrita_invalida_saida_3` | Evidência relacionada; abrangência integral não auditada |
| AC-018 | RN-018 | T-024 | `tests/test_lacunas_aceite.py::test_ac018_contagens_excluem_invalidos_mas_incluem_duplicatas` | Evidência relacionada; abrangência integral não auditada |
| AC-019 | RN-014 | T-004 | `tests/test_lacunas_aceite.py::test_ac019_chaves_repetidas_em_objeto_aninhado` | Evidência relacionada; abrangência integral não auditada |
| AC-020 | RN-014 | T-005 | `tests/test_lacunas_aceite.py::test_ac020_colaborador_incompleto_rejeita_lote` | Evidência relacionada; abrangência integral não auditada |
| AC-021 | RN-006 | T-017, T-032 | `tests/test_lacunas_aceite.py::test_ac021_periodo_invertido_retornado` | Evidência relacionada; abrangência integral não auditada |
| AC-022 | RN-019 | T-001, T-033, T-045 | `tests/test_lacunas_aceite.py::test_ac022_politica_invalida_rejeitada_globalmente` | Evidência relacionada; abrangência integral não auditada |
| AC-023 | RN-020 | T-001, T-035, T-036 | `tests/test_auditoria_financeira.py::test_ac023_cotacao_duplicada_mesmo_valor_rejeitada`; `tests/test_auditoria_financeira.py::test_ac023_cambio_invalido_em_data_nao_utilizada`; `tests/test_lacunas_aceite.py::test_ac023_cambio_cientifico_rejeitado`; `tests/test_lacunas_aceite.py::test_ac023_cambio_string_zero_negativo_e_moeda_invalida`; `tests/test_lacunas_aceite.py::test_ac023_cambio_zeros_finais_permitidos` | Evidência relacionada; abrangência integral não auditada |
| AC-024 | RN-022 | T-038 | `tests/test_criterios_complementares.py::test_ac024_moeda_omitida_usa_brl`; `tests/test_criterios_complementares.py::test_ac024_moeda_minuscula_invalida`; `tests/test_lacunas_aceite.py::test_ac024_moeda_nula_invalida_item` | Evidência relacionada; abrangência integral não auditada |
| AC-025 | RN-022 | a conferir | `tests/test_lacunas_aceite.py::test_ac025_cotacao_exata_precede_anterior`; `tests/test_lacunas_aceite.py::test_ac025_cotacao_futura_nao_e_utilizada` | Evidência relacionada; abrangência integral não auditada |
| AC-026 | RN-021 | T-039 | `tests/test_criterios_complementares.py::test_ac026_arredondamento_meio_para_cima`; `tests/test_lacunas_aceite.py::test_ac026_conversao_arredondada_a_zero_valida` | Evidência relacionada; abrangência integral não auditada |
| AC-027 | RN-023 | a conferir | `tests/test_lacunas_aceite.py::test_ac027_teto_inclusivo_e_acima_rejeitado`; `tests/test_lacunas_aceite.py::test_ac027_cientifico_original_rejeitado` | Evidência relacionada; abrangência integral não auditada |
| AC-028 | RN-024 | a conferir | `tests/test_auditoria_financeira.py::test_ac028_limite_mensal_compartilhado`; `tests/test_lacunas_aceite.py::test_ac028_mensal_compartilhado_entre_dias` | Evidência relacionada; abrangência integral não auditada |
| AC-029 | RN-025 | a conferir | `tests/test_auditoria_financeira.py::test_ac029_nota_fiscal_100_01_bloqueia_sem_consumir_saldo`; `tests/test_lacunas_aceite.py::test_ac029_nota_fiscal_sobre_preliminar` | Evidência relacionada; abrangência integral não auditada |
| AC-030 | RN-022/026 | T-044 | `tests/test_criterios_complementares.py::test_ac030_sem_cotacao_nao_gera_reembolso`; `tests/test_lacunas_aceite.py::test_ac030_sem_cotacao_marca_incompleto_mas_continua`; `tests/test_lacunas_aceite.py::test_ac030_overflow_individual_nao_aborta_lote` | Evidência relacionada; abrangência integral não auditada |
| AC-031 | RN-016/026 | a conferir | `tests/test_auditoria_financeira.py::test_ac031_reconciliacao_de_bases`; `tests/test_lacunas_aceite.py::test_ac031_bruto_inclui_inelegivel_e_duplicata` | Evidência relacionada; abrangência integral não auditada |
| AC-032 | RN-015/026 | a conferir | `tests/test_lacunas_aceite.py::test_ac032_serializacao_monetaria_duas_casas` | Evidência relacionada; abrangência integral não auditada |
| AC-033 | RN-019 | a conferir | `tests/test_criterios_complementares.py::test_ac033_centro_desconhecido_usa_politica_padrao`; `tests/test_lacunas_aceite.py::test_ac033_categoria_ausente_na_politica_recusada` | Evidência relacionada; abrangência integral não auditada |
| AC-034 | RN-019 | T-041 | `tests/test_auditoria_financeira.py::test_ac034_representacao_politica_200_restringe_teto`; `tests/test_auditoria_financeira.py::test_ac034_representacao_politica_500_nao_supera_300`; `tests/test_lacunas_aceite.py::test_ac034_comercial_300_exato`; `tests/test_lacunas_aceite.py::test_ac034_representacao_sem_limite_diario_proprio` | Evidência relacionada; abrangência integral não auditada |
| AC-035 | RN-019 | a conferir | `tests/test_criterios_complementares.py::test_ac035_hospedagem_proibida_para_engenharia` | Evidência relacionada; abrangência integral não auditada |
| AC-036 | RN-007 | T-001, T-002, T-003, T-027, T-028, T-029, T-030, T-033, T-035, T-036, T-045, T-047 | `tests/test_auditoria_financeira.py::test_ac036_moedas_diferentes_nao_sao_duplicatas`; `tests/test_lacunas_aceite.py::test_ac036_moedas_diferentes_nao_duplicam` | Evidência relacionada; abrangência integral não auditada |

## Lacunas e cautelas

- T-039: lacuna histórica de 82 testes; na versão de 84 testes há injeção controlada de `InvalidOperation` (não overflow natural).
- T-041: lacuna histórica de 82 testes; na versão de 84 testes há cenário mensal sem limite diário configurado.
- T-001: inspeção do baseline comprovada, sem confundir com validação semântica integral de RN-019/RN-020.
- T-030/T-045/T-047: matriz criada para revisão; concluir somente após verificar cada expectativa e os critérios de pronto das tarefas.
- Testes verdes demonstram as asserções executadas, não todos os caminhos possíveis.

## Complemento de rastreabilidade — execução de 84 testes

| Critério | Tarefa | Evidência adicionada | Alcance demonstrado |
|---|---|---|---|
| AC-030 | T-039 | `test_ac030_overflow_individual_nao_aborta_lote` | Falha numérica **simulada** na conversão individual; recusa, totais incompletos e continuidade do lote. Não prova overflow espontâneo |
| AC-034 | T-041 | `test_ac034_representacao_sem_limite_diario_proprio` | Representação comercial com política mensal: teto diário R$ 300,00 e aplicação conjunta com limite mensal |

Execução local **informada pelo responsável**: `Ran 84 tests in 3.687s`, `OK` (20/10/2026). A matriz continua sendo evidência parcial de rastreabilidade, não auditoria exaustiva de todos os subcritérios.
