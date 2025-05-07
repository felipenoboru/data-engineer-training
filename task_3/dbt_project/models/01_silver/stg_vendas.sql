-- models/staging/stg_vendas.sql
with base as (
    select
        id_venda,
        produto,
        quantidade,
        preco_unitario,
        loja,
        metodo_pagamento,
        data_venda,
        year(data_venda) as ano,
        month(data_venda) as mes
    from "treinamento-db-mobiis-cog"."cog-glueraw"
)
select * from base