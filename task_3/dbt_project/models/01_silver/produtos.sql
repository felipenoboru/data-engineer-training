{{ config(
    materialized='view',
    schema='silver',
    tags=['silver', 'dimensao'],
    description="View de produtos na camada silver."
) }}

SELECT
    codigo,
    ean,
    descricao,
    preco_unitario
FROM {{ source('bronze', 'produtos') }}