 SELECT *
   FROM {{ ref('fct_vendas') }}
   WHERE valor_total <= 0