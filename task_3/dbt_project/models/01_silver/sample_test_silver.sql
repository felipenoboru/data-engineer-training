{{ config(
    materialized='view',
    schema='silver_data',
    tags=['silver', 'teste'],
    description="View de teste que retorna uma linha da tabela bruta cog-glueraw para validação da infraestrutura."
) }}

-- Este modelo cria uma view staging com apenas uma linha da tabela cog-glueraw
SELECT
    id_venda,
    produto,
    quantidade,
    preco_unitario,
    loja,
    metodo_pagamento,
    data_venda
FROM {{ source('cog_glueraw', 'cog-glueraw') }}
LIMIT 1;