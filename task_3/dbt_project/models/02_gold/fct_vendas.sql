{{ config(
    materialized='table',
    schema='gold_nome_sobrenome',
    file_format='parquet',
    parquet_compression='SNAPPY',
    tags=['gold', 'fato'],
    description="Fato de vendas, derivada da tabela silver de vendas, referenciando a dimensão produto por surrogate key.",
    incremental_strategy='insert_overwrite'
) }}

WITH dim_produto AS (
    SELECT
        codigo,
        ean,
        {{ dbt_utils.generate_surrogate_key(['codigo', 'ean']) }} AS sk_produto
    FROM {{ ref('produtos') }}
)

SELECT
    ds._id AS id_venda,
    ds.data,
    ds.idsetor,
    dp.sk_produto,
    ds.quantidade,
    ds.valor_total,
    ds.fl_produtopromocao,
    ds.quant_cupom_fiscal,
    ds.preco_unitario,
    ds.ano,
    ds.mes
FROM {{ ref('daily_sales') }} ds
LEFT JOIN dim_produto dp
    ON ds.codigo = dp.codigo AND ds.ean = dp.ean