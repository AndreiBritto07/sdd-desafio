# T-001 --- Baseline técnico e evidências reproduzíveis

**Projeto:** Motor de Cálculo de Reembolso --- desafio SDD / Envelope 2\
**Tarefa:** T-001 --- Inspecionar projeto, schemas e suíte-base\
**Data das evidências de terminal:** 20/10/2026\
**Situação:** EM ANDAMENTO --- não concluída\
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

**Decisão de status:** T-001 permanece **EM ANDAMENTO**, não concluída.
O registro deste relatório não comprova por si só a validação integral
de RN-019/RN-020. A ausência de CLI implementada deve ser registrada
como baseline, não tratada como teste funcional reprovado.

### Próximas ações

1.  Revisar e adicionar este relatório em
    `docs/evidencias/T-001-baseline.md`.
2.  Realizar inspeção/validação semântica dos schemas de política e
    câmbio contra RN-019/RN-020, separando campos efetivamente presentes
    de restrições normativas.
3.  Confirmar que o relatório reflete o estado do repositório no momento
    do commit de evidências; não adicionar `desktop.ini` ou
    `estrutura-local.txt` por acidente.
4.  Registrar a evidência no Git em commit focado de T-001.
5.  Reavaliar formalmente o aceite da T-001; só então iniciar T-002 e
    implementação.

**Não foi realizado commit ou push por este relatório.**
