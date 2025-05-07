{{ config(
    materialized='table',
    schema='gold_data',
    file_format='parquet',
    parquet_compression='SNAPPY'
) }}

-- models/gold/fct_vendas.sql
with vendas as (
    select * from {{ ref('stg_vendas') }}
)
select
    produto,
    loja,
    ano,
    mes,
    sum(quantidade) as total_vendido,
    sum(quantidade * preco_unitario) as receita_total,
    count(distinct id_venda) as num_vendas
from vendas
group by produto, loja, ano, mes