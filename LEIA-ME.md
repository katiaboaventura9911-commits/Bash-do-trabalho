# Planilhas limpas para automação em Python

Para cada arquivo original, separei as abas que são **tabelas de dados reais** (uma linha de
cabeçalho + linhas de dados, sem células mescladas, sem fórmulas de painel) e gerei:

- um **.csv** por tabela (o formato mais simples e mais rápido de ler com `pandas.read_csv`)
- um **.xlsx único "LIMPO"** com todas as tabelas daquele arquivo, uma por aba, já formatado
  (cabeçalho em negrito, colunas com largura ajustada, painel congelado)

As abas que são **dashboards, pivôs ou formulários de conferência** (cheias de células soltas,
gráficos e fórmulas que só fazem sentido dentro do Excel) eu não converti — não são "tabelas" no
sentido que o pandas entende, e transformar elas força perda de informação. Elas continuam
intactas nos arquivos `.xlsm` originais.

## Dashboard_Logistica_Reversa_2026.xlsm → `dashboard_logistica_reversa/`

| Aba original | Virou | Linhas de dados |
|---|---|---|
| Base para INCORPORAR | `base_para_incorporar.csv` | 3 |
| COLAR A LOG REVERSA | `colar_log_reversa.csv` | 254 |
| VL06O | `vl06o.csv` | 28 |
| Hierarquia | `hierarquia.csv` | 100 |

Não convertidas (dashboards/formulários/pivôs, ficam só no `.xlsm` original): `CONFERÊNCIA`,
`Resumo`, `Papelão e Garrafeira, Reco e KA`, `Pivot_Base`.

## Retorno_Papelão_-_JULHO.xlsm → `retorno_papelao_julho/`

| Aba original | Virou | Linhas de dados |
|---|---|---|
| Base | `base.csv` | 1.628 |
| Consolidado total meses | `consolidado_total_meses.csv` | 7 |
| consolidado anos anteriores | `consolidado_anos_anteriores.csv` | 12 |
| Planilha3 (mapa BR ↔ C470) | `mapa_br_c470.csv` | 78 |

Não convertidas: `Resumo` (vazia), `Consolidado Mês` (dashboard), `Sinaleiro` (tabela de metas em
layout lado-a-lado, não tabular), `Planilha3` já incluída acima.

## O que foi ajustado em cada tabela

- Cabeçalhos convertidos para `snake_case` sem acento (ex.: `"% Caixas retornadas"` →
  `pct_caixas_retornadas`), para funcionar direto como nome de coluna em Python.
- Linhas 100% vazias no meio/fim da tabela foram removidas (nas abas originais elas existem só
  por causa da formatação condicional do Excel, não são dados).
- Datas e números foram lidos pelos valores já calculados da planilha (não pelas fórmulas).
- Todo o texto foi salvo em UTF-8 (abre certo com acento em qualquer ferramenta, inclusive Excel).

## Como ler em Python

```python
import pandas as pd

df = pd.read_csv("retorno_papelao_julho/base.csv")
# ou, se preferir todas as abas de uma vez:
todas = pd.read_excel("retorno_papelao_julho/retorno_papelao_julho_LIMPO.xlsx", sheet_name=None)
```

Cada `.csv` também pode ser aberto isoladamente — é o formato mais leve para um script que só
precisa de uma tabela específica.
