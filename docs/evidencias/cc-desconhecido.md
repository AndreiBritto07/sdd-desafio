# Evidência — Centro de custo desconhecido

**Data:** 20/10/2026  
**Cenário:** Envelope 2 — centro de custo não configurado na política externa  
**Centro de custo:** `CC-SUPORTE-N2`

## Execução

Comando:

```bash
python -m src calcular \
  --input exemplos/envelope/despesas-envelope-cc-desconhecido.json \
  --output resultado-cc-desconhecido.json \
  --politica exemplos/envelope/politica-v4.json \
  --cambio exemplos/envelope/cambio.json
```

## Resultado observado

- 4 despesas processadas.
- 2 aprovadas, 1 parcial e 1 recusada.
- Total original convertido: R$ 623,76.
- Total solicitado: R$ 433,76.
- Total reembolsável: R$ 373,76.
- Total não reembolsável: R$ 60,00.
- `totais_completos`: `true`.
- Aviso global: `VIAGEM_NAO_INFORMADA`.

## Regras observadas

O centro de custo `CC-SUPORTE-N2`, ausente das configurações específicas, recebeu os limites da política padrão.

A categoria `representacao` foi recusada por `CATEGORIA_NAO_PERMITIDA`. A hospedagem recebeu reembolso parcial limitado a R$ 250,00.

## Parecer

**Aprovado para o cenário executado.**

A evidência demonstra comportamento coerente com o fallback da política padrão e consistência aritmética dos totais apresentados. Não comprova, isoladamente, conformidade integral com a especificação ou com os demais cenários do Envelope 2.