# T-001 --- Baseline técnico e evidências reproduzíveis

**Projeto:** Motor de Cálculo de Reembolso --- desafio SDD / Envelope 2\
**Tarefa:** T-001 --- Inspecionar projeto, schemas e suíte-base\
**Data das evidências de terminal:** 20/10/2026\
**Situação:** INSPEÇÃO CONCLUÍDA COM LIMITAÇÕES DOCUMENTADAS; encerramento formal depende da atualização do backlog e da conferência local\
**Natureza do registro:** observações provenientes das capturas de
terminal fornecidas pelo responsável; este relatório não declara
execução independente no repositório local.

## 1. Referências e escopo

-   Documentos normativos: `specs/001-motor-reembolso/spec.md` (v0.2),
    `DECISIONS.md`, `tasks.md`, `plan.md`.
-   Requisitos de referência da T-001: RN-017, RN-019 e RN-020.
-   Objetivo: registrar inventário, schemas observados, fixtures, stack,
    comando de execução previsto e baseline de testes, distinguindo
    evidências reais de verificações ainda pendentes.

## 2. Identificação do ambiente e do Git

  --------------------------------------------------------------------------------
  Informação                          Resultado observado
  ----------------------------------- --------------------------------------------
  Registro de data/hora no terminal   `2026-10-20 14:50:56 -0300`

  Shell / sistema                     Git Bash MINGW64 em Windows

  Branch                              `main`

  Commit-base (HEAD)                  `16d6c781e469a61586c282abe82a7a931cc69652`

  Python                              `3.11.0`

  Node.js                             `v22.13.1`

  Git                                 `2.47.1.windows.2`

  Arquivos versionados listados       21

  Diretório `src/`                    Ausente

  Diretório `tests/`                  Ausente

  Caminhos não rastreados no          `docs/`, `estrutura-local.txt`,
  `git status --short`                `exemplos/envelope/`
  --------------------------------------------------------------------------------

**Observação:** o estado do working tree não estava limpo, pois havia
caminhos não rastreados. Não há evidência de alterações versionadas
pendentes na captura desse comando. O commit-base foi identificado; não
foi criado novo commit durante esta inspeção.

### Comandos usados no inventário

``` bash
date '+%Y-%m-%d %H:%M:%S %z'
git branch --show-current
git rev-parse HEAD
git status --short
python --version
node --version
git --version
git ls-files
ls -la exemplos/envelope/
for pasta in src tests; do
  if [ -d "$pasta" ]; then
    echo "$pasta: EXISTE"
    find "$pasta" -type f
  else
    echo "$pasta: AUSENTE"
  fi
done
if [ -d tests ]; then
  python -m unittest discover -s tests -v
else
  echo "BASELINE: suite de testes ainda nao implementada."
fi
```

## 3. Baseline de testes

Saída registrada:

``` text
src: AUSENTE
tests: AUSENTE
BASELINE: suite de testes ainda nao implementada.
```

**Interpretação:** não havia suíte a executar no estado-base. O comando
de descoberta `unittest` foi condicionado à existência de `tests/`;
portanto, **não houve testes funcionais executados, aprovados ou
reprovados** nesta etapa. A ausência de suíte não é falha comprovada do
motor de reembolso.

## 4. Arquivos externos inspecionados

### 4.1 Política v4

**Caminho:** `exemplos/envelope/politica-v4.json`

Campos de raiz observados:

-   `versao` (texto; exemplo `v4`)
-   `vigencia` (texto de data; exemplo `2026-07-01`)
-   `moeda_base` (texto; exemplo `BRL`)
-   `padrao` (objeto com regras por categoria)
-   `centros_custo` (objeto com regras por centro de custo e categoria)
-   `nota_fiscal_obrigatoria_acima_de` (número; exemplo `100.0`)
-   `acrescimo_em_viagem_percentual` (número; exemplo `50`)

Nas regras por categoria, observaram-se `limite` (número),
`periodicidade` (texto, exemplos `dia` e `diaria`) e `observacao` (texto
em caso específico). Categorias observadas: `alimentacao`,
`transporte_urbano`, `hospedagem`, `representacao`. Centros observados:
`CC-ENG-PLATAFORMA`, `CC-COMERCIAL`, `CC-ADM`.

**Compatibilidade observável:** `CC-COMERCIAL/representacao` contém
limite 300; `CC-ENG-PLATAFORMA/hospedagem` contém limite zero e
observação de não reembolso. A regra normativa de teto máximo de
representação e a proibição de hospedagem decorrem da
especificação/decisões, não apenas desses valores de exemplo.

### 4.2 Câmbio

**Caminho:** `exemplos/envelope/cambio.json`

Campos de raiz observados: `moeda_base` (texto), `fonte` (texto),
`observacao` (texto), `taxas` (objeto). `taxas` associa datas no formato
`YYYY-MM-DD` a objetos com moedas (exemplos `USD`, `EUR`) e cotações
numéricas.

Foram observadas 12 datas de cotação, de `2026-07-13` a `2026-07-28`,
sem continuidade em todos os dias civis. A regra de buscar cotação da
data ou a mais recente anterior é normativa e permanece inalterada.

**Limite da inspeção:** a observação dos campos e exemplos não comprova
integralmente quais campos adicionais seriam permitidos, quais campos
seriam obrigatórios em todas as variantes nem todas as restrições
semânticas de RN-019/RN-020.

## 5. Fixtures identificadas

  --------------------------------------------------------------------------------------------------------------------
  Arquivo                                                      Raiz               Despesas observadas Característica
  ------------------------------------------------------------ ---------------- --------------------- ----------------
  `exemplos/despesas-exemplo.json`                             objeto com                          14 Exemplo
                                                               `colaborador`,                         original, sem
                                                               `periodo`,                             campo `moeda`
                                                               `despesas`                             nos itens
                                                                                                      listados

  `exemplos/envelope/despesas-envelope.json`                   mesmo formato de                    10 Cenário Envelope
                                                               raiz                                   2, `moeda`
                                                                                                      presente em
                                                                                                      parte dos itens

  `exemplos/envelope/despesas-envelope-cc-desconhecido.json`   mesmo formato de                     4 Cenário de
                                                               raiz                                   centro de custo
                                                                                                      desconhecido,
                                                                                                      `moeda` presente
                                                                                                      em parte dos
                                                                                                      itens
  --------------------------------------------------------------------------------------------------------------------

Essas contagens e chaves foram produzidas por script de inspeção com
`json.load`. **Não foram calculados resultados financeiros esperados**,
nem verificado o comportamento de uma implementação inexistente.

## 6. Verificação JSON estrita: resultados

Foi executado um script Python que usou:

-   `json.loads` para sintaxe;
-   `object_pairs_hook` para rejeitar chaves repetidas;
-   `parse_float=Decimal` e `parse_int=Decimal` para leitura decimal
    exata;
-   `parse_constant` para rejeitar constantes não padronizadas.

Saída observada:

``` text
OK | exemplos/envelope/politica-v4.json | raiz=dict
OK | exemplos/envelope/cambio.json | raiz=dict
OK | exemplos/despesas-exemplo.json | raiz=dict
OK | exemplos/envelope/despesas-envelope.json | raiz=dict
OK | exemplos/envelope/despesas-envelope-cc-desconhecido.json | raiz=dict
```

**Conclusão limitada:** cinco arquivos foram lidos com sucesso, com raiz
objeto, sem chaves repetidas e sem constantes não padronizadas
detectadas pelo script. Isso **não** representa validação semântica
integral, teste de todos os requisitos, nem aprovação funcional.

### Procedimento reproduzível de verificação estrita

Executar na raiz do repositório, no Git Bash:

``` bash
python - <<'PY'
import json
from decimal import Decimal
from pathlib import Path

arquivos = [
    "exemplos/envelope/politica-v4.json",
    "exemplos/envelope/cambio.json",
    "exemplos/despesas-exemplo.json",
    "exemplos/envelope/despesas-envelope.json",
    "exemplos/envelope/despesas-envelope-cc-desconhecido.json",
]

def sem_chaves_repetidas(pares):
    resultado = {}
    for chave, valor in pares:
        if chave in resultado:
            raise ValueError(f"Chave JSON repetida: {chave}")
        resultado[chave] = valor
    return resultado

for nome in arquivos:
    try:
        texto = Path(nome).read_text(encoding="utf-8")
        dados = json.loads(
            texto,
            parse_float=Decimal,
            parse_int=Decimal,
            object_pairs_hook=sem_chaves_repetidas,
            parse_constant=lambda valor: (_ for _ in ()).throw(
                ValueError(f"Constante JSON invalida: {valor}")
            ),
        )
        print(f"OK | {nome} | raiz={type(dados).__name__}")
    except (OSError, ValueError) as erro:
        print(f"ERRO | {nome} | {erro}")
PY
```

## 7. Escolha técnica aprovada

O responsável aprovou explicitamente:

  -----------------------------------------------------------------------
  Responsabilidade                    Escolha
  ----------------------------------- -----------------------------------
  Linguagem                           Python 3.11

  Cálculo decimal                     `decimal.Decimal`

  Parser JSON                         Biblioteca padrão `json`,
                                      configurada para chaves repetidas,
                                      lexemas numéricos e constantes

  Testes                              `unittest`

  Argumentos CLI                      `argparse`

  Dependências externas               Nenhuma
  -----------------------------------------------------------------------

**Motivação:** ferramentas já disponíveis, precisão decimal,
possibilidade de detecção de chaves repetidas e testes sem instalações
adicionais.

**Contrato de CLI preservado:** quatro argumentos explícitos `--input`,
`--output`, `--politica`, `--cambio`. A forma executável concreta
**ainda não existe** e será definida quando o código for criado. Exemplo
de invocação futuro, **não executável no baseline**:
`python -m <modulo_a_definir> --input ... --output ... --politica ... --cambio ...`.

Esta aprovação é **técnica**, não altera requisitos, limites, fórmulas,
critérios de aceite ou decisões de negócio.

## 8. Avaliação formal de T-001

  -----------------------------------------------------------------------
  Critério                            Avaliação
  ----------------------------------- -----------------------------------
  Inventário de arquivos e ambiente   Comprovado pelas capturas

  Identificação de fixtures           Comprovada pelas capturas

  Inspeção dos campos e estruturas    Comprovada para os exemplos
  observáveis                         exibidos

  Verificação estrita de              Comprovada nos cinco arquivos
  sintaxe/duplicidade JSON

  Stack definida e aprovada           Concluído por decisão explícita

  Baseline da suíte                   Comprovada ausência de `tests/`;
                                      nenhum teste funcional executado

  Validação semântica integral dos    **Não comprovada**
  schemas externos

  Comando real de execução da CLI     **Não existente ainda**

  Registro persistido no repositório  **Pendente de inclusão/commit pelo
  e commit de evidência               responsável**
  -----------------------------------------------------------------------

**Avaliação de status:** os critérios de **inspeção** da T-001 estão atendidos pelas evidências observadas, com limitações documentadas. O encerramento formal depende de atualizar o backlog e versionar esta revisão. Não foi demonstrada validação semântica integral de RN-019/RN-020, que deverá ser testada nas tarefas de implementação dos leitores. A ausência de CLI e suíte no baseline não é falha funcional.

### Próximas ações

1. Substituir a versão local deste relatório e executar `git diff --check`.
2. Conferir o texto vigente da T-001 em `tasks.md` e, se mantido o aceite de inspeção, registrar seu encerramento formal com referência a este relatório.
3. Versionar a revisão em commit focado; não adicionar `desktop.ini` ou `estrutura-local.txt`.
4. Prosseguir com T-002 apenas após a conferência do commit. A validação integral de RN-019/RN-020 e os testes funcionais pertencem às tarefas de implementação e teste, não são resultados da T-001.

**Histórico de Git:** a versão inicial do relatório foi commitada e enviada em `6aad0c8` (`docs(T-001): registra baseline tecnico e evidencias`). Esta revisão ainda não foi commitada nem enviada pelo assistente.

## 9. Evidências adicionais — verificações selecionadas dos schemas

Após o commit inicial do baseline, foram executados dois scripts diagnósticos temporários no Git Bash, com `json.loads`, `Decimal`, detecção de chaves repetidas e validações selecionadas de campos. As capturas apresentaram os seguintes resultados:

### Política — `exemplos/envelope/politica-v4.json`

```text
=== VALIDACAO DA POLITICA ===
OK: verificacoes selecionadas da politica
AVISO: conformidade integral com RN-019 ainda nao comprovada
```

O script verificou, entre outros aspectos, raiz como objeto, `versao` igual a `v4`, data de vigência interpretável, moeda-base `BRL`, objetos `padrao` e `centros_custo`, regras com limites numéricos não negativos e finitos, periodicidades entre `dia`, `diaria` e `mes`, tipo de `observacao` quando presente, limite de representação comercial não superior a 300, e campos numéricos de nota fiscal e acréscimo não negativos.

**Escopo:** são verificações selecionadas sobre o arquivo observado, não um validador normativo completo. A lista de periodicidades aceita pelo script é uma hipótese diagnóstica, não uma nova decisão de negócio. Não se demonstrou rejeição de todos os formatos e campos inválidos possíveis.

### Câmbio — `exemplos/envelope/cambio.json`

```text
=== VALIDACAO DO CAMBIO ===
OK: verificacoes selecionadas do cambio
AVISO: conformidade integral com RN-020 ainda nao comprovada
```

O script verificou raiz como objeto, moeda-base `BRL`, tipos textuais de `fonte` e `observacao`, `taxas` como objeto não vazio, datas ISO interpretáveis e canônicas, objetos de moedas não vazios, códigos de moeda não vazios e cotações `Decimal` positivas e finitas, além de rejeição de chaves repetidas no parser.

**Escopo:** não foram testadas todas as variantes de erros exigidas pela RN-020, nem a lógica de seleção da cotação mais recente anterior. Não existe implementação do leitor nem suíte de testes funcionais.

### Resultado conjunto e conclusão do aceite da T-001

| Evidência exigida na T-001 | Situação observada |
|---|---|
| Caminhos reais e inventário | Registrados |
| Comandos e resultados-base | Registrados |
| Estruturas físicas dos arquivos externos | Inspecionadas e documentadas |
| Verificação além de `json.tool` | Cinco leituras estritas e duas verificações selecionadas concluídas |
| Stack | Aprovada: Python 3.11, `Decimal`, `json`, `unittest`, `argparse` |
| Suíte-base | Ausente; não há falhas funcionais preexistentes a reproduzir |
| Evidência persistida | Versão inicial commitada em `6aad0c8`; revisão atual depende de commit |
| Validação semântica integral e testes de produção | Não demonstrados; permanecem para as tarefas correspondentes |

**Parecer:** a finalidade de inspeção e diagnóstico da T-001 foi cumprida com limitações explicitadas. A ausência de uma CLI e de uma suíte-base foi observada, não encoberta. É defensável encerrar a T-001 **como tarefa de inspeção**, desde que a revisão seja versionada e o backlog seja atualizado de forma rastreável; não é defensável declarar RN-019/RN-020 integralmente validados ou testes funcionais aprovados.
