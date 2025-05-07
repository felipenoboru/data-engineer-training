{{ config(
    materialized='table',
    schema='gold_data',
    file_format='parquet',
    parquet_compression='SNAPPY',
    tags=['gold', 'teste'],
    description="Tabela gold de teste que replica a linha da view silver para validação do pipeline e do formato Parquet."
) }}

-- Este modelo consome o modelo staging e cria uma tabela gold com a mesma linha
SELECT
    id_venda,
    produto,
    quantidade,
    preco_unitario,
    loja,
    metodo_pagamento,
    data_venda
FROM {{ ref('sample_test_silver') }};