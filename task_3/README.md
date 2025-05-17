# 🚀 Instruções para Projeto DBT + AWS Athena

## 📑 Índice

1. [Objetivo](#objetivo)
2. [Pré-requisitos](#pré-requisitos)
3. [Instalação das Dependências](#instalação-das-dependências)
4. [Estrutura de Pastas do Projeto DBT](#estrutura-de-pastas-do-projeto-dbt)
5. [Configuração do Profile DBT para Athena](#configuração-do-profile-dbt-para-athena)
6. [Configuração dos Schemas por Camada](#configuração-dos-schemas-por-camada)
7. [Modelos DBT: Star Schema](#modelos-dbt-star-schema)
8. [Comandos DBT](#comandos-dbt)
9. [Verificação dos Objetos Criados no Athena](#verificação-dos-objetos-criados-no-athena)
10. [Documentação dos Modelos DBT](#documentação-dos-modelos-dbt)
11. [Observações](#observações)
12. [Desafio: Criação do Star Schema](#desafio-criação-do-star-schema)
13. [Desafio: Testes de Qualidade de Dados com DBT](#desafio-testes-de-qualidade-de-dados-com-dbt)

---

## 📌 Objetivo

Este exercício tem como objetivo testar seus conhecimentos em DBT, Athena e modelagem dimensional (Star Schema). Você irá criar um projeto DBT do zero, configurar a conexão com Athena, estruturar os diretórios e desenvolver modelos SQL para transformar dados da camada **silver** em um Star Schema na camada **gold**. O foco é garantir que toda a estrutura básica do DBT esteja pronta, permitindo que você pratique a criação de modelos de fato e dimensão, além de executar fluxos de dados.

---

## ✅ Pré-requisitos

Antes de iniciar, verifique se você possui:

- Python 3.8+ instalado
- Permissão para instalar pacotes Python (pip)
- Perfil AWS configurado em `~/.aws/credentials` com acesso ao Athena, Glue e S3
- Bucket S3 acessível: `s3://mobiis-treinamento-cognitivo`
- Databases já criados no Athena/Glue:
  - `bronze_nome_sobrenome` (camada bronze)
  - `silver_nome_sobrenome` (com as tabelas: `daily_sales` e `produtos`)
  - `gold_nome_sobrenome` (para os modelos finais)

---

## 🛠️ Instalação das Dependências

Siga os passos abaixo para instalar o DBT, o adaptador do Athena e as dependências do projeto:

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

4. **Adicione o pacote dbt_utils ao arquivo `packages.yml` do projeto:**
   ```yaml
   # packages.yml
   packages:
     - package: dbt-labs/dbt_utils
       version: [">=1.0.0", "<2.0.0"]
   ```

5. **Atualize as dependências do DBT:**
   ```bash
   dbt deps
   ```

6. **Verifique a instalação:**
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
├── packages.yml            # Dependências do projeto DBT (ex: dbt_utils)
├── profiles.yml            # Configuração de conexão (deve estar em ~/.dbt/)
├── models/                 # Onde ficam os modelos SQL (transformações)
│   ├── 00_bronze/          # Modelos e schema da camada bronze
│   │   └── schema.yml
│   ├── 01_silver/          # Modelos e schema da camada silver
│   │   └── schema.yml
│   └── 02_gold/            # Modelos e schema da camada gold
│       └── schema.yml
├── seeds/                  # Dados estáticos (opcional)
├── macros/                 # Macros customizadas (opcional)
├── snapshots/              # Snapshots (opcional)
└── tests/                  # Testes customizados (opcional)
```

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
      schema: dbt_nome_sobrenome
      aws_profile_name: mobiis
      threads: 4
```

> Substitua `dbt_nome_sobrenome` pelo seu schema de destino.

---

## 🗂️ Configuração dos Schemas por Camada

Cada camada do seu projeto deve ter seu próprio arquivo `schema.yml` para documentação e testes.

### Exemplo para a camada bronze (`models/00_bronze/schema.yml`):

```yaml
version: 2

sources:
  - name: bronze
    schema: bronze_nome_sobrenome  # Altere para o schema correto da camada bronze
    description: Camada bronze do projeto, dados brutos.
    tables:
      - name: produtos
        description: Tabela bruta de produtos.
      - name: daily_sales
        description: Tabela bruta de vendas.
```

### Exemplo para a camada silver (`models/01_silver/schema.yml`):

```yaml
version: 2

models:
  - name: silver
    schema: silver_nome_sobrenome  # Altere para o schema correto da camada silver
    description: Camada silver do projeto, views intermediárias.
    tables:
      - name: produtos
        description: View de produtos na camada silver.
        columns:
          - name: codigo
            description: Código do produto.
          - name: ean
            description: Código EAN do produto.
          - name: descricao
            description: Descrição do produto.
          - name: preco_unitario
            description: Preço unitário do produto.
      - name: daily_sales
        description: View de vendas na camada silver.
        columns:
          - name: _id
            description: Identificador único da venda.
          - name: data
            description: Data da venda.
          - name: idsetor
            description: Identificador do setor.
          - name: codigo
            description: Código do produto (chave para dimensão produto).
          - name: ean
            description: Código EAN do produto.
          - name: descricao
            description: Descrição do produto.
          - name: quantidade
            description: Quantidade de itens vendidos.
          - name: valor_total
            description: Valor total da venda.
          - name: fl_produtopromocao
            description: Flag indicando se o produto estava em promoção.
          - name: quant_cupom_fiscal
            description: Quantidade de cupons fiscais.
          - name: preco_unitario
            description: Preço unitário do produto.
          - name: ano
            description: Ano da venda.
          - name: mes
            description: Mês da venda.
```

### Exemplo para a camada gold (`models/02_gold/schema.yml`):

```yaml
version: 2

models:
  - name: dim_produto
    description: Dimensão de produtos.
    columns:
      - name: descricao
        tests:
          - not_null

  - name: fct_vendas
    description: Fato de vendas.
    columns:
      - name: valor_total
        tests:
          - not_null
```

> **IMPORTANTE:**  
> Cada aluno deve alterar o valor de `schema:` para o seu schema/database correto no Glue/Athena, conforme o padrão do seu ambiente.

---

## ⚠️ Sobre a Materialização das Tabelas Silver

Antes de criar os modelos gold (star schema), **é obrigatório que as tabelas `produtos` e `daily_sales` estejam previamente disponíveis na camada silver**.  
Ou seja, você deve garantir que existam modelos DBT em `task_3/dbt_project/models/01_silver/` que criem essas tabelas no seu schema silver, utilizando as fontes brutas ou bronze como origem.

> **Atenção:** Para este exercício, **NÃO materialize como `table`**.  
> Utilize o tipo `view` para os modelos da camada silver, conforme exemplo abaixo:

Exemplo de modelo para a view `produtos` na silver:

```sql
-- filepath: models/01_silver/produtos.sql
{{ config(
    materialized='view',
    schema='silver_nome_sobrenome',
    tags=['silver', 'dimensao'],
    description="View de produtos na camada silver."
) }}

SELECT
    codigo,
    ean,
    descricao,
    preco_unitario
FROM {{ source('bronze', 'produtos') }}
```

Exemplo de modelo para a view `daily_sales` na silver:

```sql
-- filepath: models/01_silver/daily_sales.sql
{{ config(
    materialized='view',
    schema='silver_nome_sobrenome',
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
```

---

## 🏗️ Modelos DBT: Star Schema

O desafio é criar um **Star Schema** na camada gold, utilizando as tabelas da camada silver como origem.

### 1. Dimensão Produto

Crie o modelo `models/02_gold/dim_produto.sql`:

```sql
-- filepath: models/02_gold/dim_produto.sql
{{ config(
    materialized='table',
    schema='gold_nome_sobrenome',
    file_format='parquet',
    parquet_compression='SNAPPY',
    tags=['gold', 'dimensao'],
    description="Dimensão de produtos, derivada da tabela silver de produtos, com surrogate key.",
    incremental_strategy='insert_overwrite'
) }}

SELECT
    {{ dbt_utils.generate_surrogate_key(['codigo', 'ean']) }} AS sk_produto,
    codigo,
    ean,
    descricao,
    preco_unitario
FROM {{ ref('produtos') }}
```

### 2. Fato Vendas

Crie o modelo `models/02_gold/fct_vendas.sql`:

```sql
-- filepath: models/02_gold/fct_vendas.sql
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
```

> O parâmetro `incremental_strategy='insert_overwrite'` garante que a tabela seja sobrescrita a cada execução, evitando duplicados na camada gold.

---

## 🛠️ Comandos DBT

Execute os comandos DBT a partir da raiz do projeto:

- **Instalar/atualizar dependências do projeto:**
  ```bash
  dbt deps
  ```
- **Compilar, testar e executar todos os modelos (recomendado):**
  ```bash
  dbt build
  ```
- **Compilar e executar todos os modelos:**
  ```bash
  dbt run
  ```
- **Executar apenas um modelo específico:**
  ```bash
  dbt run --select fct_vendas
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
   - `dbt_nome_sobrenome_gold.dim_produto`
   - `dbt_nome_sobrenome_gold.fct_vendas`

2. **Consulta de validação:**
   ```sql
   SELECT * FROM dbt_nome_sobrenome_gold.fct_vendas LIMIT 10;
   SELECT * FROM dbt_nome_sobrenome_gold.dim_produto LIMIT 10;
   ```

3. **Verifique no Glue Catalog:**
   - As tabelas devem aparecer na database `dbt_nome_sobrenome_gold` com os metadados corretos.

4. **Formato e compactação dos dados:**
   - Os dados finais são gravados em formato **Parquet** com compactação SNAPPY.

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

## 🚀 Desafio: Testes de Qualidade de Dados com DBT

Além de construir o Star Schema, seu desafio agora é **implementar testes de qualidade de dados utilizando o DBT** na camada gold.

### O que fazer

1. **Crie testes automáticos para os modelos gold:**
   - **Dimensão Produto (`dim_produto`):**  
     - Verifique que todos os produtos possuem descrição (`descricao` não pode ser nulo).
   - **Fato Vendas (`fct_vendas`):**  
     - Verifique que o campo `valor_total` é sempre maior que zero.

2. **Onde criar os testes:**
   - Crie arquivos de teste SQL na pasta `task_3/dbt_project/tests/`.
   - Siga as boas práticas do DBT, utilizando arquivos `.sql` para testes customizados e arquivos `.yml` para testes genéricos de coluna.

3. **Exemplo de teste genérico (schema.yml):**
   - Defina os testes de coluna no arquivo de schema YAML dos modelos gold (ex: `models/02_gold/schema.yml`):

   ```yaml
   version: 2

   models:
     - name: dim_produto
       columns:
         - name: descricao
           tests:
             - not_null

     - name: fct_vendas
       columns:
         - name: valor_total
           tests:
             - not_null
   ```

4. **Exemplo de teste customizado (arquivo SQL em `tests/`):**

   - Crie um arquivo, por exemplo, `tests/test_produto_sem_descricao.sql`:

   ```sql
   -- filepath: task_3/dbt_project/tests/test_produto_sem_descricao.sql
   SELECT *
   FROM {{ ref('dim_produto') }}
   WHERE descricao IS NULL
   ```

   - E outro para testar valores negativos em `valor_total`:

   ```sql
   -- filepath: task_3/dbt_project/tests/test_valor_total_positivo.sql
   SELECT *
   FROM {{ ref('fct_vendas') }}
   WHERE valor_total <= 0
   ```

   > Se o teste retornar linhas, o DBT irá marcar o teste como falho.

5. **Crie seus próprios testes!**
   - Pense em regras de negócio da sua empresa ou experiências anteriores e implemente outros testes relevantes.
   - Exemplo: testar se não há meses futuros na fato, se o campo `quantidade` é sempre positivo, etc.

6. **Simule um teste que pode falhar:**
   - Por exemplo, crie um teste para garantir que `quantidade > 10` (sabendo que pode haver vendas com quantidade menor):

   ```sql
   -- filepath: task_3/dbt_project/tests/test_quantidade_maior_que_10.sql
   SELECT *
   FROM {{ ref('fct_vendas') }}
   WHERE quantidade <= 10
   ```

   - Execute `dbt test` e observe o resultado de falha, analisando o log e aprendendo a interpretar os erros.

---

### Como executar os testes

- Para rodar todos os testes:
  ```bash
  dbt test
  ```

- Para rodar apenas um teste específico:
  ```bash
  dbt test --select test_nome_do_teste
  ```

---

> **Dica:** Os testes de dados são fundamentais para garantir a confiabilidade do seu pipeline.  
> Consulte exemplos e boas práticas na [documentação oficial de testes do DBT](https://docs.getdbt.com/docs/build/data-tests) e do [dbt-utils](https://hub.getdbt.com/dbt-labs/dbt_utils/latest/).

---
