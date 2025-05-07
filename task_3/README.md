# 🚀 Instruções para Projeto DBT + AWS Athena

## 📑 Índice

1. [Objetivo](#objetivo)
2. [Pré-requisitos](#pré-requisitos)
3. [Instalação das Dependências](#instalação-das-dependências)
4. [Estrutura de Pastas do Projeto DBT](#estrutura-de-pastas-do-projeto-dbt)
5. [Configuração do Profile DBT para Athena](#configuração-do-profile-dbt-para-athena)
6. [Modelos DBT](#modelos-dbt)
7. [Comandos DBT](#comandos-dbt)
8. [Verificação dos Objetos Criados no Athena](#verificação-dos-objetos-criados-no-athena)
9. [Documentação dos Modelos DBT](#documentação-dos-modelos-dbt)
10. [Observações](#observações)
11. [Desafio Extra: Construindo uma Query Analítica Avançada](#desafio-extra-construindo-uma-query-analítica-avançada)

---

## 📌 Objetivo

Este exercício tem como objetivo testar seus conhecimentos em DBT, Athena e modelagem de dados em camadas (silver e gold). Você irá criar um projeto DBT do zero, configurar a conexão com Athena, estruturar os diretórios e desenvolver modelos SQL para transformar dados da camada **silver** para a camada **gold**. O foco é garantir que toda a estrutura básica do DBT esteja pronta, permitindo que você pratique a criação dos modelos de transformação e a execução dos fluxos de dados.

---

## ✅ Pré-requisitos

Antes de iniciar, verifique se você possui:

- Python 3.8+ instalado
- Permissão para instalar pacotes Python (pip)
- Perfil AWS configurado em `~/.aws/credentials` com acesso ao Athena, Glue e S3
- Bucket S3 acessível: `s3://mobiis-treinamento-cognitivo`
- Databases já criados no Athena/Glue:
  - `treinamento-db-mobiis-cog` (tabela: `cog-glueraw`)
  - `silver_data` (para os modelos staging)
  - `gold_data` (para os modelos finais)

---

## 🛠️ Instalação das Dependências

Siga os passos abaixo para instalar o DBT e o adaptador do Athena usando `pip`:

1. **Crie e ative um ambiente virtual (opcional, mas recomendado):**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2. **Atualize o pip:**
   ```bash
   pip install --upgrade pip
   ```

3. **Instale o DBT com suporte ao Athena (adaptador oficial):**
   ```bash
   pip install dbt-athena-community
   ```

4. **Verifique a instalação:**
   ```bash
   dbt --version
   ```

---

## 📁 Estrutura de Pastas do Projeto DBT

A estrutura típica de um projeto DBT é:

```
dbt_project/
│
├── dbt_project.yml         # Configurações do projeto DBT
├── profiles.yml            # Configuração de conexão (deve estar em ~/.dbt/)
├── models/                 # Onde ficam os modelos SQL (transformações)
│   ├── staging/            # Modelos intermediários (silver)
│   │   └── stg_vendas.sql
│   └── gold/               # Modelos finais (gold)
│       └── fct_vendas.sql
├── seeds/                  # Dados estáticos (opcional)
├── macros/                 # Macros customizadas (opcional)
├── snapshots/              # Snapshots (opcional)
└── tests/                  # Testes customizados (opcional)
```

- **models/staging/**: modelos intermediários (camada silver)
- **models/gold/**: modelos finais (camada gold)
- **profiles.yml**: arquivo de configuração de conexão, deve estar em `~/.dbt/profiles.yml`

---

## 🔗 Configuração do Profile DBT para Athena

No arquivo `~/.dbt/profiles.yml`:

```yaml
athena:
  target: dev
  outputs:
    dev:
      type: athena
      s3_staging_dir: s3://mobiis-treinamento-cognitivo/dbt-athena-stage/
      region_name: us-east-2
      database: awsdatacatalog
      schema: dbt
      aws_profile_name: mobiis
      threads: 4
```

---

## 🏗️ Modelos DBT

### 1. Fonte (source)

A tabela de origem está em:

```sql
SELECT * FROM "treinamento-db-mobiis-cog"."cog-glueraw"
```

### 2. Staging (silver_data)

Crie um modelo em `models/staging/stg_vendas.sql`:

```sql
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
```

### 3. Gold (gold_data)

Crie um modelo em `models/gold/fct_vendas.sql`:

```sql
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
```

---

## 🛠️ Comandos DBT

Execute os comandos DBT a partir da raiz do projeto:

- **Compilar e executar todos os modelos:**
  ```bash
  dbt run
  ```
- **Executar apenas um modelo específico:**
  ```bash
  dbt run --select gold.fct_vendas
  ```
- **Executar modelos em paralelo:**
  ```bash
  dbt run --threads 4
  ```
- **Verificar status dos modelos:**
  ```bash
  dbt ls
  ```
- **Testar os modelos:**
  ```bash
  dbt test
  ```
- **Ver logs detalhados:**
  ```bash
  dbt run --debug
  ```

---

## ✅ Verificação dos Objetos Criados no Athena

Após rodar o DBT, verifique no Athena:

1. **Tabelas criadas:**
   - `silver_data.stg_vendas`
   - `gold_data.fct_vendas`

2. **Particionamento:**
   - As tabelas devem estar particionadas por `ano` e `mes` (verifique no Glue Catalog ou usando `SHOW PARTITIONS gold_data.fct_vendas;` no Athena).

3. **Consulta de validação:**
   ```sql
   SELECT * FROM gold_data.fct_vendas LIMIT 10;
   ```

4. **Verifique no Glue Catalog:**
   - As tabelas devem aparecer nas databases `silver_data` e `gold_data` com os metadados corretos.

5. **Formato e compactação dos dados:**
   - Os dados finais são gravados em formato **Parquet** com compactação, garantindo performance e economia de armazenamento.

---

## 📚 Documentação dos Modelos DBT

O DBT possui uma ferramenta integrada para gerar e visualizar a documentação dos modelos do seu projeto, incluindo descrições de tabelas, colunas, fontes e dependências.

### Como gerar e visualizar a documentação localmente:

1. **Gere a documentação:**
   ```bash
   dbt docs generate
   ```

2. **Inicie o servidor local para visualizar a documentação (porta 8001):**
   ```bash
   dbt docs serve --port 8001
   ```

3. **Acesse no navegador:**
   - O comando acima abrirá automaticamente a documentação em seu navegador padrão.
   - Caso não abra, acesse manualmente: [http://localhost:8001](http://localhost:8001)

> Assim, você pode explorar todos os modelos, dependências e descrições do seu projeto DBT de forma interativa!

---

## 📝 Observações

- Sempre valide se o profile DBT está correto e se o bucket S3 está acessível.
- Use o comando `dbt clean` para limpar artefatos antigos se necessário.
- Para mais informações, consulte a [documentação oficial do DBT Athena](https://docs.getdbt.com/reference/warehouse-setups/athena-setup).

---

## 🚀 Desafio Extra: Construindo uma Query Analítica Avançada

Agora que você já validou a infraestrutura e entendeu o fluxo DBT + Athena, proponha-se um desafio para praticar SQL analítico e modelagem de dados!

### 🏆 Desafio

**Crie um novo modelo DBT na camada gold que responda à seguinte pergunta:**

> **"Quais são os 3 produtos com maior receita total por loja e mês?"**

### Regras e Dicas

- Utilize as tabelas já existentes: `silver_data.stg_vendas` ou a tabela raw `"treinamento-db-mobiis-cog"."cog-glueraw"`.
- O modelo deve ser salvo em `models/02_gold/top3_produtos_por_loja_mes.sql`.
- O resultado deve conter as colunas: `loja`, `ano`, `mes`, `produto`, `receita_total`, `rank_produto`.
- Utilize funções de janela (`row_number`, `rank`, etc) para calcular o ranking dos produtos por receita dentro de cada loja/mês.
- Não esqueça de preencher o bloco `{{ config(...) }}` com as configurações de materialização, formato e descrição para enriquecer a documentação DBT.

### Exemplo de estrutura do modelo

```sql
{{ config(
    materialized='table',
    schema='gold_data',
    file_format='parquet',
    parquet_compression='SNAPPY',
    tags=['gold', 'desafio'],
    description="Top 3 produtos com maior receita total por loja e mês, usando funções analíticas."
) }}

with vendas as (
    select
        loja,
        produto,
        ano,
        mes,
        sum(quantidade * preco_unitario) as receita_total
    from {{ ref('stg_vendas') }}
    group by loja, produto, ano, mes
),
ranked as (
    select
        *,
        row_number() over (partition by loja, ano, mes order by receita_total desc) as rank_produto
    from vendas
)
select
    loja,
    ano,
    mes,
    produto,
    receita_total,
    rank_produto
from ranked
where rank_produto <= 3
```

### O que será avaliado

- Uso correto de funções analíticas (window functions)
- Clareza e documentação do modelo
- Organização e boas práticas DBT

> **Dica:** Gere a documentação DBT novamente após criar o modelo para visualizar a nova tabela e suas descrições!

---
