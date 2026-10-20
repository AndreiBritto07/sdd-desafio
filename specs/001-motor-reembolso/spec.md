# Spec — Motor de Cálculo de Reembolso

**Versão:** 0.2  
**Revisão documental:** 20/10/2026 — consolidação pós-Envelope 2  
**Estado:** contrato normativo consolidado; implementação Python e CLI existentes, com 35 testes aprovados na execução mais recente informada (20/10/2026). Cobertura integral de AC-001 a AC-036 ainda não demonstrada.

Esta versão incorpora as decisões da revisão e do Envelope 2 em um único contrato. As regras antigas substituídas estão identificadas em DECISIONS.md e não constituem comportamento alternativo.

A consolidação documental não representa aprovação oficial do avaliador nem, isoladamente, comprova implementação. A versão anterior deve permanecer no histórico do Git.

## 1. Problema e objetivo

Calcular o reembolso de um colaborador em um período, aplicando política externa e conversão cambial, explicando cada resultado e permitindo reconciliar os totais.

## 2. Escopo

Inclui:

- Validação de JSON, envelope, período e despesas.
- Identificação de IDs repetidos e duplicatas por conteúdo.
- Política por centro de custo, com fallback explícito.
- Conversão cambial com cotação da data ou anterior.
- Limites diários e mensais, reembolso parcial e exigência fiscal.
- Saída determinística, motivos, contagens e totais.
- Execução por CLI.

Não inclui:

- Pagamentos, autenticação ou interface gráfica.
- Consulta externa de política ou câmbio.
- Validação da autenticidade de notas fiscais.
- Inferência de viagem ou número de diárias por texto.
- Processamento de vários colaboradores no mesmo lote.
- Compensação de estornos.
- Histórico financeiro entre execuções.

Os limites mensais consideram as despesas do lote processado. Sem histórico externo, o motor não conhece reembolsos de execuções anteriores.

## 3. Fontes e precedência

1. Aplicar as decisões consolidadas nesta especificação.
2. Obter categorias, limites e periodicidades da política externa válida.
3. Aplicar as restrições específicas de CC-COMERCIAL/representacao e CC-ENG-PLATAFORMA/hospedagem.
4. Usar exclusivamente cambio.json para conversão.

Não manter dois modos implícitos, um anterior e outro posterior ao Envelope 2.

Os schemas físicos de `politica-v4.json` e `cambio.json` devem ser conferidos integralmente nos arquivos originais antes da implementação dos leitores. A inspeção visual anterior identificou, de forma preliminar, `versao`, `vigencia`, `moeda_base`, `padrao`, `centros_custo`, `nota_fiscal_obrigatoria_acima_de` e `acrescimo_em_viagem_percentual` na política, bem como `moeda_base`, `fonte`, `observacao` e `taxas` no câmbio. Esses nomes são observações técnicas, **não** uma definição exaustiva de schema, nem evidência de validação integral. Os caminhos são informados obrigatoriamente pelos argumentos `--politica` e `--cambio`, conforme RN-017.

## 4. Entrada

### 4.1 Envelope principal

| Campo | Tipo | Obrigatório |
|---|---|---|
| colaborador | objeto | Sim |
| colaborador.id | texto não vazio | Sim |
| colaborador.nome | texto não vazio | Sim |
| colaborador.centro_custo | texto não vazio | Sim |
| periodo | objeto | Sim |
| periodo.competencia | texto YYYY-MM | Sim |
| periodo.inicio | data YYYY-MM-DD | Sim |
| periodo.fim | data YYYY-MM-DD | Sim |
| despesas | lista | Sim; pode estar vazia |

### 4.2 Despesa

| Campo | Tipo | Regra |
|---|---|---|
| id | texto não vazio | Opcional; gerar somente quando ausente |
| data | data YYYY-MM-DD | Obrigatório |
| categoria | texto não vazio | Obrigatório |
| descricao | texto não vazio | Obrigatório |
| fornecedor | texto não vazio | Obrigatório |
| valor | número JSON decimal convencional | Obrigatório; RN-009/RN-023 |
| tem_nota_fiscal | booleano | Obrigatório |
| moeda | texto com três letras ASCII maiúsculas | Opcional; ausente significa BRL |

Strings obrigatórias compostas somente por espaços são inválidas.

Chaves são exatas e sensíveis a maiúsculas. Campos desconhecidos no envelope, colaborador, período e despesas são ignorados, sem influenciar cálculo ou duplicidade.

Datas não contêm hora ou fuso. Não aceitar formatos alternativos.

Booleanos não são números. Strings numéricas não substituem números JSON.

## 5. Saída

### 5.1 Sucesso

Objeto contendo:

- versao_spec: "0.2".
- colaborador: identificação recebida.
- periodo: período efetivamente usado, já corrigido se estava invertido.
- avisos: lista de códigos globais.
- items: um resultado por despesa, na ordem original.
- resumo: contagens e totais.

Índices são zero-based.

### 5.2 Resultado por despesa

| Campo | Tipo | Significado |
|---|---|---|
| indice | inteiro | Posição original |
| id | texto ou null | Original válido, gerado quando ausente ou null quando presente inválido |
| categoria_normalizada | texto ou null | Categoria após normalização, quando disponível |
| moeda | texto ou null | Moeda válida; BRL quando ausente |
| valor_original | número ou null | Valor original aceito pela validação monetária |
| valor_convertido | número ou null | Valor em BRL, antes das restrições; null quando não puder ser obtido |
| valor_solicitado | número | Valor convertido preservado para apresentação, ou zero quando indisponível |
| valor_reembolsavel | número | Valor efetivamente reembolsável em BRL |
| status | enum | APROVADO, PARCIAL, RECUSADO ou IGNORADO |
| motivos | lista de códigos | Fonte normativa dos motivos |
| motivo | código | Campo singular de compatibilidade |
| justificativa | texto não vazio | Explicação humana coerente |
| duplicata_de_indice | inteiro ou null | Índice canônico para duplicata por conteúdo |
| avisos | lista de códigos | Avisos do item |
| erros | lista de objetos | Objetos com campo e codigo |

valor_original é null quando a representação monetária recebida é inválida. Não arredondar uma entrada inválida para apresentá-la como aceita.

valor_convertido pode estar disponível mesmo quando outro campo invalida a despesa, desde que os dados necessários à conversão sejam válidos. Sua presença não torna a despesa elegível.

valor_solicitado por item é informativo. Sua soma indiscriminada não define total_solicitado; a base do total está em RN-016.

motivo corresponde ao primeiro código de motivos. Quando motivos estiver vazio em uma aprovação integral, usar DENTRO_DO_LIMITE.

### 5.3 Status

- APROVADO: item elegível cujo reembolso coincide com o valor convertido.
- PARCIAL: item elegível com reembolso positivo inferior ao valor convertido.
- RECUSADO: item inválido ou sem reembolso por regra de negócio.
- IGNORADO: duplicata por conteúdo.

Uma conversão válida que resulte em 0.00 é aceita. Se não houver outro impedimento, seu status é APROVADO, sem consumo de limite.

Valores originais zero ou negativos são inválidos por item, conforme Envelope 2. Não recebem o tratamento antigo de estorno ignorado.

### 5.4 Códigos de motivos

| Código | Aplicação |
|---|---|
| DADO_INVALIDO | Falha estrutural não monetária ou ID repetido |
| ENTRADA_INVALIDA | Valor/moeda inválidos ou conversão impossível por capacidade numérica |
| DUPLICATA | Duplicidade por conteúdo |
| CATEGORIA_NAO_PERMITIDA | Categoria ausente na política aplicável ou proibida |
| FORA_DA_COMPETENCIA | Data válida fora do período/competência |
| MOEDA_SEM_COTACAO | Sem cotação aplicável |
| NOTA_FISCAL_OBRIGATORIA_AUSENTE | Valor preliminar maior que 100.00 sem nota |
| LIMITE_DIARIO | Restrição pelo saldo diário |
| LIMITE_MENSAL | Restrição pelo saldo mensal |
| DENTRO_DO_LIMITE | Compatibilidade singular para aprovação sem restrições |

LIMITE_APLICADO, LIMITE_ESGOTADO, CATEGORIA_NAO_PREVISTA e NOTA_FISCAL_OBRIGATORIA não são códigos normativos desta revisão. Os resultados antigos devem ser migrados para o catálogo acima.

Erros estruturais usam:

- CAMPO_OBRIGATORIO.
- TIPO_OU_FORMATO_INVALIDO.
- ID_REPETIDO.

### 5.5 Resumo

| Campo | Definição |
|---|---|
| total_itens | Quantidade de despesas estruturalmente válidas |
| aprovados | Quantidade de APROVADO entre itens estruturalmente válidos |
| parciais | Quantidade de PARCIAL entre itens estruturalmente válidos |
| recusados | Quantidade de RECUSADO entre itens estruturalmente válidos |
| ignorados | Quantidade de IGNORADO entre itens estruturalmente válidos |
| total_original_convertido | Soma dos valores válidos convertíveis antes das restrições |
| total_solicitado | Base elegível definida em RN-016 |
| total_reembolsavel | Soma dos pagamentos calculados |
| total_nao_reembolsavel | total_solicitado - total_reembolsavel |
| totais_completos | Indica se foi possível obter o valor em BRL de todas as despesas |

Não usar os aliases total_bruto_convertido e total_nao_reembolsado.

Itens estruturalmente inválidos permanecem em items, mas não entram em total_itens nem nas contagens por status.

### 5.6 Escopo dos erros

O código `ENTRADA_INVALIDA` pode aparecer em dois níveis sem equivalência de efeito: em `erro.codigo` na raiz, indica falha global de envelope, colaborador ou período e impede `items` e `resumo`; em `items[].motivos`, indica falha monetária, de moeda ou capacidade de conversão da despesa, que permanece em `items` com reembolso zero e não interrompe o lote. `DADO_INVALIDO` sinaliza falhas estruturais individuais não monetárias. Exemplo: colaborador sem `id` produz erro global `ENTRADA_INVALIDA`; despesa com `valor: 10.501` produz motivo individual `ENTRADA_INVALIDA`; despesa com `data: "2026-02-30"` produz `DADO_INVALIDO`. A distinção é feita pela posição do código na saída, não por novo alias.

### 5.7 Falha de lote

Formato:

```json
{
  "versao_spec": "0.2",
  "erro": {
    "codigo": "ENTRADA_INVALIDA",
    "mensagem": "Descrição do erro."
  }
}
```

Não retornar items nem resumo em falhas de lote.

Códigos:

- JSON_INVALIDO: JSON principal malformado ou com chaves repetidas.
- ENTRADA_INVALIDA: envelope, colaborador ou período global inválido.
- POLITICA_INVALIDA: política ausente, ilegível ou inválida.
- CAMBIO_INVALIDO: câmbio ausente, ilegível ou inválido.
- ERRO_IO: falha operacional de leitura da entrada principal ou escrita.

## 6. Regras de negócio

### RN-001 — Agregação diária

Obter limites da política validada.

Agregar limites diários por colaborador, centro de custo, categoria e data.

Valores como 60.00, 80.00 e 250.00 são parâmetros de fixtures quando presentes na política utilizada, nunca fallback implícito do motor.

### RN-002 — Distribuição sequencial

Processar despesas na ordem original.

Consumir cada saldo somente pelo valor efetivamente reembolsado.

Itens inválidos, duplicados, inelegíveis ou bloqueados por nota fiscal não consomem saldo.

### RN-003 — Fronteira e reembolso parcial

O valor preliminar é o menor entre:

- Valor convertido da despesa.
- Saldo diário, quando aplicável.
- Saldo mensal, quando aplicável.

Igualdade com o valor convertido é aprovação integral. Valor positivo inferior é parcial. Saldo zero pode resultar em recusa por limite.

### RN-004 — Obrigatoriedade fiscal

Exigir nota fiscal somente quando o valor preliminar reembolsável, após conversão e aplicação preliminar de todos os limites, for estritamente maior que 100.00 BRL.

Sem nota nesse caso:

- Reembolso zero.
- Motivo NOTA_FISCAL_OBRIGATORIA_AUSENTE.
- Nenhum consumo de saldo diário ou mensal.

Não verificar o limiar sobre o valor original bruto.

### RN-005 — Viagem

Não inferir viagem de descrição, hotel, aeroporto ou centro de custo.

Sem comprovação estruturada no contrato de entrada, não aplicar o acréscimo de 50%.

Emitir VIAGEM_NAO_INFORMADA em toda resposta de sucesso, inclusive lista vazia.

### RN-006 — Competência e datas

Usar a data da despesa.

O período é inclusivo: inicio <= data <= fim.

competencia deve representar um mês válido em YYYY-MM. inicio e fim devem ser datas reais em YYYY-MM-DD e pertencer ao mês da competência.

Se inicio e fim forem válidos, compatíveis com a competência e estiverem invertidos, trocá-los automaticamente e devolver o período corrigido.

Competência ou datas globais obrigatórias ausentes/inválidas rejeitam o lote com ENTRADA_INVALIDA.

Data de despesa ausente, malformada ou inexistente:

- Invalida somente a despesa.
- Usa DADO_INVALIDO.
- Registra CAMPO_OBRIGATORIO ou TIPO_OU_FORMATO_INVALIDO.
- Não interrompe o lote.

Data válida fora do período/competência:

- Recusa somente a despesa com FORA_DA_COMPETENCIA.
- Não consome limite.
- Não entra em total_solicitado.
- Pode entrar em total_original_convertido se for convertível.

Não corrigir nem reinterpretar datas individuais.

### RN-007 — Identidade e duplicidade

Validar estrutura antes de deduplicar.

Para comparar IDs, remover espaços ASCII das extremidades e ignorar diferença entre maiúsculas/minúsculas. Preservar o ID original válido na saída.

Primeiro ID estruturalmente válido é mantido. Ocorrência posterior:

- RECUSADO.
- motivos: [DADO_INVALIDO].
- erros contendo ID_REPETIDO.
- Sem abortar o lote.
- Conta em total_itens e recusados.
- Não entra em total_solicitado.

IDs de despesas estruturalmente inválidas não reservam identidade para deduplicação.

Entre IDs distintos, comparar conteúdo por:

- Data válida.
- Categoria normalizada.
- Fornecedor e descrição com NFC, trim ASCII externo e comparação sem diferença de caixa.
- Moeda efetiva.
- Valor original válido, em precisão monetária de duas casas.

Preservar espaços internos e diferenças reais de acento.

moeda participa da chave para impedir que 10.00 BRL e 10.00 USD sejam tratados como a mesma despesa.

tem_nota_fiscal e campos desconhecidos não participam.

Primeiro item estruturalmente válido com aquele conteúdo é canônico, mesmo se posteriormente recusado por regra de negócio.

Duplicata por conteúdo:

- IGNORADO.
- motivos: [DUPLICATA].
- Reembolso zero.
- duplicata_de_indice apontando ao canônico.
- Conta em total_itens e ignorados.
- Não entra em total_solicitado.
- Entra em total_original_convertido se convertível.

### RN-008 — Zero, negativos e estornos

Valor original zero ou negativo é inválido por item, com ENTRADA_INVALIDA.

Não compensar outras despesas nem aumentar saldo.

A regra anterior de IGNORADO/ESTORNO_NAO_PROCESSADO está substituída no contrato consolidado.

### RN-009 — Precisão do valor original

Aceitar somente número JSON decimal convencional, positivo, com no máximo duas casas decimais.

Aceitar números inteiros ou com uma casa. Na saída monetária, escrever duas casas.

Exemplos:

- 10 -> 10.00.
- 10.5 -> 10.50.
- 10.50 -> 10.50.
- 10.501 -> despesa inválida.
- "10.50" -> despesa inválida.
- 1.05e1 -> despesa inválida.

Não arredondar nem truncar um valor original inválido.

### RN-010 — Diárias

Não extrair número de diárias da descrição.

Na ausência de quantidade estruturada, considerar uma diária por data, compartilhada entre hospedagens do mesmo colaborador/data e sujeita à política aplicável.

Emitir DIARIAS_NAO_INFORMADAS para hospedagem estruturalmente válida, inclusive quando recusada por regra de negócio.

### RN-011 — Categoria

Remover espaços ASCII extremos e converter somente A-Z para a-z.

Não remover acentos nem criar aliases.

As categorias permitidas vêm da política aplicável, incluindo representacao quando configurada.

Não manter uma lista fixa restrita às três categorias do exemplo original.

### RN-012 — Dias civis

Aplicar regras em sábados, domingos e feriados, sem criar restrição de dia útil ausente na política.

### RN-013 — Chaves e campos desconhecidos

Chaves são exatas.

temNotaFiscal e TEM_NOTA_FISCAL não substituem tem_nota_fiscal.

tem_nota_fiscal aceita somente true ou false.

Ignorar campos desconhecidos da entrada principal, sem usá-los no cálculo ou na deduplicação.

A tolerância a campos extras da entrada principal não altera a validação estrita dos arquivos externos.

### RN-014 — Validação e IDs gerados

JSON principal inválido ou com chaves repetidas rejeita o lote com JSON_INVALIDO.

Envelope inválido ou colaborador obrigatório incompleto/inválido rejeita o lote com ENTRADA_INVALIDA.

Validar cada despesa individualmente e registrar todos os erros estruturais na ordem:

1. id.
2. data.
3. categoria.
4. descricao.
5. fornecedor.
6. valor.
7. tem_nota_fiscal.
8. moeda, quando presente.

A ordem dos erros independe da ordem das chaves recebidas.

ID ausente gera gerado-{indice_original}, mesmo se outro campo da despesa for inválido.

Evitar colisões normalizadas com todos os IDs textuais fornecidos, inclusive em despesas inválidas, e com IDs já gerados.

Em colisão, tentar gerado-{indice}-1, -2 e assim sucessivamente.

ID presente vazio, somente espaços ou de tipo incorreto é inválido, retorna null e não recebe substituto.

Item estruturalmente inválido permanece em items, mas fica fora de total_itens e contagens.

### RN-015 — Precedência e motivos

Aplicar o fluxo da seção 7.

Falha estrutural impede avaliação de elegibilidade e limites, mas não impede obter o valor convertido para o total original quando houver dados suficientes.

ID repetido prevalece sobre duplicidade de conteúdo.

Duplicata não recebe nova avaliação de elegibilidade.

Para itens que seguem à avaliação de negócio, ordenar motivos assim:

1. CATEGORIA_NAO_PERMITIDA.
2. FORA_DA_COMPETENCIA.
3. MOEDA_SEM_COTACAO ou ENTRADA_INVALIDA de conversão.
4. NOTA_FISCAL_OBRIGATORIA_AUSENTE.
5. LIMITE_DIARIO.
6. LIMITE_MENSAL.

Não repetir códigos.

Categoria e período podem registrar seus impedimentos independentemente. Sem elegibilidade ou conversão, não calcular motivos fiscais ou de limites.

Quando houver bloqueio fiscal após cálculo preliminar, manter também os motivos dos limites que efetivamente reduziram esse cálculo preliminar.

### RN-016 — Totais

total_original_convertido:

- Soma valores originais válidos convertidos para BRL.
- É calculado antes das restrições de reembolso.
- Inclui duplicatas, IDs repetidos e despesas inelegíveis, quando convertíveis.
- Não inclui valores impossíveis de obter em BRL.

total_solicitado:

- Soma valores convertidos de despesas estruturalmente válidas, não duplicadas e sem ID repetido.
- Exige categoria permitida, período válido e conversão disponível.
- Exclui despesas bloqueadas pela exigência de nota fiscal.
- Usa o valor convertido antes da redução por limites.
- Inclui o valor de uma despesa elegível cujo saldo diário ou mensal esteja esgotado.

Uma recusa exclusivamente por limite não é recusa por inelegibilidade e não deve desaparecer da base solicitada.

total_reembolsavel soma os valores efetivamente reembolsados.

total_nao_reembolsavel = total_solicitado - total_reembolsavel.

A diferença entre total_original_convertido e total_reembolsavel não deve ser publicada com o nome total_nao_reembolsavel, pois pertence a outra base.

### RN-017 — CLI e determinismo

Contrato obrigatório para a implementação (forma executável Python já observada):

```bash
calcular --input entrada.json --output resultado.json --politica politica-v4.json --cambio cambio.json
```

Os quatro argumentos `--input`, `--output`, `--politica` e `--cambio` são obrigatórios e recebem caminhos de arquivos. Não há descoberta automática, fallback de caminhos ou política/câmbio embutidos. Ausência de argumento obrigatório é erro global de uso, com saída 2 e sem resultado financeiro. A invocação implementada e observada é `python -m src calcular`, preservando os quatro argumentos obrigatórios. A verificação de todos os códigos de saída e cenários de I/O continua sujeita à rastreabilidade de AC-017.

Códigos de saída:

- 0: lote processado, inclusive com recusas individuais.
- 2: entrada global, política ou câmbio inválidos.
- 3: erro operacional de I/O da entrada principal ou escrita.

Política/câmbio ausentes ou ilegíveis mantêm seus códigos semânticos POLITICA_INVALIDA/CAMBIO_INVALIDO e saída 2.

Não misturar logs com resultado JSON.

Se não for possível gravar a saída, informar erro no canal de erro e retornar 3.

Mesmos arquivos de entrada, política e câmbio devem produzir o mesmo resultado financeiro.

### RN-018 — Contagens e invariantes

Cada despesa gera um objeto em items.

total_itens conta somente despesas estruturalmente válidas, inclusive IDs repetidos e duplicatas por conteúdo.

Invariantes:

- aprovados + parciais + recusados + ignorados = total_itens.
- total_reembolsavel = soma de valor_reembolsavel de items.
- total_nao_reembolsavel = total_solicitado - total_reembolsavel.
- 0 <= total_reembolsavel <= total_solicitado <= total_original_convertido.
- Reembolso individual nunca é negativo.
- Reembolso individual nunca supera o valor convertido disponível.

### RN-019 — Política externa e exceções

Ler exclusivamente o arquivo de política indicado por `--politica` (fixture do Envelope 2: `politica-v4.json`).

Arquivo ausente, ilegível, JSON inválido, chaves repetidas ou estrutura obrigatória inválida: POLITICA_INVALIDA, sem resultado financeiro.

Obter categorias, limites e periodicidades da política validada.

Centro de custo desconhecido usa a política padrao. Categoria ausente na política aplicável recebe CATEGORIA_NAO_PERMITIDA.

Não usar política padrão inventada se o arquivo estiver inválido.

Para CC-COMERCIAL/representacao:

- A categoria precisa ser permitida pela política aplicável.
- O teto diário absoluto é 300.00 BRL.
- O limite diário efetivo é o menor entre o limite diário aplicável da política, quando existente, e 300.00.
- Política inferior prevalece.
- Política superior nunca amplia o teto.
- Outros limites aplicáveis, inclusive mensais, continuam valendo.
- Se a categoria estiver permitida sem limite diário próprio, o teto de 300.00 continua aplicável.

Para CC-ENG-PLATAFORMA/hospedagem:

- Não reembolsar.
- Usar CATEGORIA_NAO_PERMITIDA.
- A restrição prevalece mesmo se a configuração genérica permitir hospedagem.

### RN-020 — Validação do câmbio

Ler exclusivamente o arquivo de câmbio indicado por `--cambio` (fixture do Envelope 2: `cambio.json`).

Arquivo ausente, ilegível, vazio, JSON inválido, chaves repetidas, estrutura inválida ou qualquer cotação inválida: CAMBIO_INVALIDO.

Validar todos os registros, mesmo os não usados pelo lote.

Exigir:

- Data real em YYYY-MM-DD.
- Código de moeda com exatamente três letras ASCII maiúsculas.
- Cotação numérica, positiva e finita.
- Representação decimal convencional, sem string numérica ou notação científica.
- Estrutura exata do schema original, sem campos inesperados ou obrigatórios ausentes.
- Ausência de repetição da chave moeda+data.

Cotação duplicada invalida o arquivo mesmo quando os valores são iguais ou numericamente equivalentes.

Não rejeitar zeros finais: 5.4200 e 5.42 representam o mesmo valor.

Códigos sintaticamente válidos, mas não suportados pelo arquivo/contrato de câmbio, não criam suporte cambial implicitamente. A despesa dependente de moeda sem cotação recebe MOEDA_SEM_COTACAO.

Não impor quantidade arbitrária de casas à cotação. Se não for possível processá-la com exatidão e segurança, rejeitar o arquivo.

### RN-021 — Conversão e exibição

Usar aritmética decimal exata ou racional equivalente.

Não usar ponto flutuante binário nem arredondar a cotação antes da multiplicação.

Converter cada despesa individualmente. Aplicar half-up a duas casas ao resultado em BRL e então trabalhar com centavos inteiros.

Exemplos de resultados de conversão:

- 10.125 -> 10.13.
- 0.005 -> 0.01.

Esses números intermediários não são exemplos de valores originais aceitos com três casas.

Separar a cotação exata de sua exibição. Exibir cotação com duas casas, usando half-up quando necessário, sem reutilizar o valor exibido no cálculo.

Conversão que arredonde para 0.00 é válida.

Conversão impossível por capacidade numérica:

- Afeta somente a despesa.
- Usa ENTRADA_INVALIDA.
- Reembolso zero.
- totais_completos=false.

### RN-022 — Moeda e seleção da cotação

moeda ausente significa BRL.

Quando presente, exigir exatamente três letras ASCII maiúsculas. Não normalizar usd ou Usd para USD.

null, vazio, espaços, tipo incorreto ou formato inválido invalidam somente a despesa com ENTRADA_INVALIDA.

Para BRL, não consultar cotação individual. A validação global de cambio.json continua obrigatória.

Para moeda estrangeira:

1. Preferir a cotação da data da despesa.
2. Na ausência, usar a cotação anterior mais recente da mesma moeda.
3. Não impor horizonte máximo fixo.
4. Nunca usar cotação futura.

Sem cotação aplicável, usar MOEDA_SEM_COTACAO, reembolso zero e continuar o lote.

### RN-023 — Teto e validade do valor

Valor original máximo: 1.000.000.000.000,00, inclusive, na moeda declarada.

O teto não se aplica ao valor convertido em BRL.

Ausência, null, string, booleano, zero, negativo, notação científica, mais de duas casas ou valor acima do teto invalidam somente a despesa com ENTRADA_INVALIDA.

A validação deve preservar o lexema numérico original para identificar notação científica e excesso de casas.

### RN-024 — Limites simultâneos

Converter antes de aplicar limites.

Limites diários agregam por colaborador, centro de custo, categoria e data.

Limites mensais agregam por colaborador, categoria e mês-calendário, independentemente do centro de custo.

Quando diário e mensal se aplicarem, usar o menor saldo.

Adicionar LIMITE_DIARIO quando o saldo diário for inferior ao valor convertido; adicionar LIMITE_MENSAL quando o saldo mensal for inferior ao valor convertido.

Atualizar ambos somente depois da verificação fiscal, usando o valor efetivamente reembolsado.

### RN-025 — Avaliação fiscal e motivos múltiplos

Calcular limites sem consumir saldo.

Avaliar a nota sobre o valor preliminar.

Se o valor preliminar for maior que 100.00 e não houver nota, zerar o reembolso.

Depois de definir o pagamento final, atualizar os saldos.

motivos é lista de códigos únicos na ordem de RN-015.

### RN-026 — Completude e serialização

Se não for possível determinar um valor convertido válido para qualquer despesa, excluí-la dos totais monetários e usar totais_completos=false.

Isso inclui valor original inválido, moeda inválida, ausência de cotação ou dados necessários à conversão inválidos.

Outros defeitos estruturais não impedem, por si só, o cálculo do bruto convertido quando valor, moeda e demais dados necessários forem válidos.

Se todos os valores puderem ser determinados, totais_completos=true.

Lista vazia resulta em totais zero e totais_completos=true, após validar os arquivos globais obrigatórios.

Campos monetários de saída são números JSON, nunca strings, escritos com exatamente duas casas decimais.

Exemplos: 0.00, 10.50, 300.00.

A formatação deve ser verificada no texto serializado; um parser JSON pode descartar zeros finais.

## 7. Ordem de processamento

1. Ler e fazer parsing estrito da entrada principal.
2. Validar envelope e colaborador.
3. Validar competência e período; corrigir inversão válida.
4. Carregar e validar integralmente a política.
5. Carregar e validar integralmente o câmbio.
6. Preparar o conjunto de IDs fornecidos para evitar colisões.
7. Gerar IDs ausentes e validar a estrutura de cada despesa.
8. Determinar, quando possível, o valor convertido para o total original, independentemente da elegibilidade.
9. Para itens estruturalmente válidos, verificar ID repetido.
10. Para IDs não repetidos, verificar duplicidade por conteúdo.
11. Avaliar categoria e período dos itens não duplicados.
12. Exigir conversão disponível antes do cálculo de reembolso.
13. Calcular os saldos diário e mensal e o valor preliminar.
14. Verificar a exigência de nota fiscal.
15. Definir pagamento, motivos e status.
16. Consumir os saldos somente pelo pagamento final.
17. Calcular contagens, totais e completude.
18. Serializar a saída preservando a ordem dos itens.

Não executar verificações dependentes de dados indisponíveis. Uma falha de conversão não impede registrar inelegibilidade de categoria/período quando esses dados forem válidos.

## 8. Critérios de aceite

Os identificadores abaixo descrevem testes requeridos. Não representam testes já existentes ou executados.

| AC | Resultado verificável | RN |
|---|---|---|
| AC-001 | Com limite diário 60.00, despesas 72.50 e 38.00 pagam 60.00 e 0.00 | RN-001/002 |
| AC-002 | Invertendo a ordem, 38.00 e 72.50 pagam 38.00 e 22.00 | RN-002 |
| AC-003 | Fronteiras 59.99/60.00/60.01 pagam 59.99/60.00/60.00 sob limite 60.00 | RN-003 |
| AC-004 | Sem nota, preliminar 100.00 não bloqueia; 100.01 bloqueia sem consumir saldo | RN-004 |
| AC-005 | Texto de viagem não amplia limite; sucesso contém VIAGEM_NAO_INFORMADA | RN-005 |
| AC-006 | Limites do período são inclusivos; data inválida afeta só o item; período global inválido rejeita lote | RN-006 |
| AC-007 | ID repetido e duplicata por conteúdo têm comportamentos distintos e referência canônica correta | RN-007 |
| AC-008 | Zero e negativo invalidam somente a despesa, sem compensar saldos | RN-008 |
| AC-009 | Inteiro e uma/duas casas são aceitos; mais de duas casas não são arredondadas | RN-009 |
| AC-010 | Texto “2 diárias” não duplica limite; hospedagens compartilham a diária da data | RN-010 |
| AC-011 | Categoria normaliza espaços/caixa ASCII; permissão vem da política, sem aliases | RN-011 |
| AC-012 | Fim de semana não causa recusa adicional | RN-012 |
| AC-013 | Chaves são exatas, booleanos são reais e campos desconhecidos não afetam cálculo | RN-013 |
| AC-014 | Todos os erros estruturais são ordenados; IDs ausentes/ inválidos/colidentes seguem o contrato | RN-014 |
| AC-015 | Motivos são únicos e ordenados; ID repetido precede conteúdo duplicado | RN-015 |
| AC-016 | Totais usam suas bases distintas, incluindo recusa exclusiva por limite na base solicitada | RN-016 |
| AC-017 | CLI exige os quatro argumentos, distingue processamento, erro global e I/O, sem logs no JSON | RN-017 |
| AC-018 | Contagens e invariantes financeiros são satisfeitos | RN-018 |
| AC-019 | Chave JSON repetida na entrada principal rejeita lote com JSON_INVALIDO | RN-014 |
| AC-020 | Colaborador obrigatório incompleto rejeita lote com ENTRADA_INVALIDA | RN-014 |
| AC-021 | Período válido invertido é corrigido e retornado | RN-006 |
| AC-022 | Política válida é carregada; ausência/invalidade retorna POLITICA_INVALIDA | RN-019 |
| AC-023 | Qualquer registro cambial inválido ou moeda+data repetidos rejeita cambio.json | RN-020 |
| AC-024 | Moeda ausente assume BRL; usd/Usd/null/tipo incorreto invalidam somente o item | RN-022 |
| AC-025 | Cotação exata precede anterior; cotação futura nunca é usada | RN-022 |
| AC-026 | Conversão exata usa half-up por despesa; exibição não altera a cotação interna | RN-021 |
| AC-027 | Teto original é inclusivo; notação científica e valores inválidos afetam somente o item | RN-023 |
| AC-028 | Limites diário/mensal usam menor saldo e consomem só o pagamento final | RN-024 |
| AC-029 | Bloqueio fiscal após limites zera pagamento sem consumir nenhum saldo | RN-025 |
| AC-030 | Falha individual de conversão preserva item, continua lote e marca totais incompletos | RN-022/026 |
| AC-031 | Bruto inclui convertíveis inelegíveis; solicitado usa base elegível; não reembolsável é solicitado menos pagamento | RN-016/026 |
| AC-032 | Motivos não se repetem e números monetários são serializados com duas casas | RN-015/026 |
| AC-033 | CC desconhecido usa padrao; categoria ausente é recusada | RN-019 |
| AC-034 | Em representação comercial, política 200.00 limita a 200.00 e política 500.00 limita a 300.00 | RN-019 |
| AC-035 | Hospedagem em CC-ENG-PLATAFORMA não reembolsa mesmo com permissão genérica | RN-019 |
| AC-036 | Valores iguais em moedas diferentes não constituem duplicata por conteúdo | RN-007 |

Cada AC deve ser associado a um teste real quando a suíte for inspecionada. Os nomes de testes em tasks.md são nomes propostos, não evidências de execução.

## 9. Exemplos de referência

### 9.1 Limite diário

Fixture: alimentação permitida, limite diário 60.00, sem limite mensal restritivo.

Duas despesas distintas, elegíveis, de 72.50 e 38.00:

- Reembolsos: 60.00 e 0.00.
- total_original_convertido: 110.50.
- total_solicitado: 110.50.
- total_reembolsavel: 60.00.
- total_nao_reembolsavel: 50.50.

A segunda despesa permanece na base solicitada porque a recusa decorre exclusivamente do limite.

### 9.2 Categoria proibida

Despesa BRL válida de 40.00 em categoria proibida:

- total_original_convertido: 40.00.
- total_solicitado: 0.00.
- total_reembolsavel: 0.00.
- total_nao_reembolsavel: 0.00.
- Motivo: CATEGORIA_NAO_PERMITIDA.

O bruto e o solicitado têm bases diferentes por decisão explícita.

### 9.3 Nota fiscal e limite

Despesa válida de 150.00 sem nota:

- Com saldo aplicável 80.00: preliminar 80.00, reembolso 80.00; não há bloqueio fiscal.
- Com saldo aplicável 120.00: preliminar 120.00, reembolso 0.00; nenhum saldo é consumido.

### 9.4 Representação comercial

Com categoria permitida:

- Limite diário da política 200.00: teto efetivo 200.00.
- Limite diário da política 300.00: teto efetivo 300.00.
- Limite diário da política 500.00: teto efetivo 300.00.

### 9.5 Precisão

- Valor original 33.333: inválido por item.
- Valor original 33.3: aceito e exibido como 33.30.
- Cotação 5.4200: aceita; cálculo usa exatamente 5.42.
- Cotação 5.425: cálculo usa exatamente 5.425; exibição 5.43.

O quadro antigo dos 14 itens não é mantido como gabarito desta revisão: contém expectativas anteriores incompatíveis com as novas validações. A fixture original deve ser reprocessada e seus resultados registrados após inspeção dos arquivos reais.

## 10. Rastreabilidade e entrega

Manter o encadeamento:

AMB/decisão -> RN -> AC -> tarefa -> teste real -> resultado de execução.

DECISIONS.md registra origem, substituições e refinamentos.

tasks.md mantém tarefas pequenas, critérios verificáveis e nenhuma conclusão presumida.

## 11. Pendências reais

- Conferir integralmente os schemas originais de `politica-v4.json` e `cambio.json`; os campos observados em capturas de terminal ainda não constituem validação semântica completa.
- Reproduzir e registrar o inventário local e a ausência ou presença de implementação e suíte, vinculando comandos, resultados e commit-base à T-001.
- A CLI executável `python -m src calcular` já foi observada com os quatro argumentos obrigatórios; conferir os demais casos de AC-017, inclusive falhas de I/O e argumento ausente.
- Auditar a implementação existente do contrato consolidado contra todos os critérios, incluindo cenários de borda ainda sem teste específico.
- Executar testes e recalcular a fixture original.
- Registrar evidências antes de marcar ACs ou tarefas como concluídos.

Não há pendência de decisão sobre período global inválido ou sobre o teto de representação comercial: ambos estão definidos nesta versão.

## Registro de execução — 20/10/2026 (não normativo)

A execução local demonstrada utilizou `python -m src calcular` com `--input`, `--output`, `--politica` e `--cambio`, usando os arquivos oficiais em `exemplos/envelope/`. Após gerar `resultado-envelope.json`, o comando `python -m unittest discover -s tests -v` apresentou `Ran 16 tests` e `OK`, sem skips ou falhas na última captura.

Este registro não modifica RN-001 a RN-026 nem AC-001 a AC-036. A correspondência integral entre os 36 critérios, os testes executados e suas evidências ainda requer matriz de rastreabilidade. A existência de implementação não equivale à comprovação de todas as regras em todos os casos de borda.


## Registro complementar de execução — 20/10/2026 (não normativo)

Após os marcos históricos de 16 e 25 testes, o responsável executou `python -m unittest discover -s tests -v` e informou `Ran 35 tests in 1.373s` e `OK`, com 35 testes aprovados, zero falhas e zero ignorados. A suíte inclui dez testes em `tests/test_criterios_complementares.py`, que exercitam cenários de AC-001, AC-002, AC-007, AC-017, AC-024, AC-026, AC-030, AC-033 e AC-035. O primeiro teste complementar de CLI falhou por um problema na fixture do teste, que foi corrigido; a nova execução completa passou.

Este registro não modifica RN-001 a RN-026, AC-001 a AC-036 nem decisões vigentes. Ainda falta uma matriz de cobertura integral com todos os cenários normativos, inclusive cotação em notação científica (RN-020/AC-023) e caminhos de erro operacional da CLI (RN-017/AC-017).
