{{ config(
    materialized='table',
    schema='gold',
    file_format='parquet',
    parquet_compression='SNAPPY',
    tags=['gold', 'dimensao'],
    description="Dimensão de produtos, derivada da tabela silver de produtos, com surrogate key."
) }}

SELECT
    {{ dbt_utils.generate_surrogate_key(['codigo', 'ean']) }} AS sk_produto,
    codigo,
    ean,
    descricao,
    preco_unitario
FROM {{ ref('produtos') }}