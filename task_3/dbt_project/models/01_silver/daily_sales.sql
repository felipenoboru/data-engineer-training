{{ config(
    materialized='view',
    schema='silver',
    tags=['silver', 'fato'],
    description="View de vendas na camada silver."
) }}

SELECT
    _id,
    data,
    idsetor,
    codigo,
    ean,
    quantidade,
    valor_total,
    fl_produtopromocao,
    quant_cupom_fiscal,
    preco_unitario,
    ano,
    mes
FROM {{ source('bronze', 'daily_sales') }}
limit 1000;