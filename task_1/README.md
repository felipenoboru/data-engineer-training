# 🧪 Projeto Hands-on: Pipeline com AWS S3, Glue e Athena

Este guia apresenta os passos para construir um pipeline de dados simples utilizando serviços AWS como **S3**, **Glue** e **Athena**. O objetivo é simular uma arquitetura tipo "Medalhão", movendo dados de um estado bruto (**bronze**) para uma camada tratada (**silver**), com suporte a consultas SQL e organização de dados particionados.
## 📑 Índice

1. [Pré-requisitos](#pré-requisitos)
2. [Etapa 1: Armazenamento no Amazon S3](#etapa-1-armazenamento-no-amazon-s3)
3. [Etapa 2: Catalogação com AWS Glue](#etapa-2-catalogação-com-aws-glue)
4. [Etapa 3: Consulta com AWS Athena](#etapa-3-consulta-com-aws-athena)
5. [Etapa 4: Criação da Database e da Tabela Silver Particionada](#etapa-4-criação-da-database-e-da-tabela-silver-particionada)
6. [Etapa 5: Atualização de Metadados](#etapa-5-atualização-de-metadados)
7. [Resultado Esperado](#resultado-esperado)
8. [Etapa Opcional: Exemplos de Queries no Athena](#etapa-opcional-exemplos-de-queries-no-athena)
9. [Referências Oficiais AWS](#referências-oficiais-aws)
10. [Observações](#observações)

---

## ✅ Pré-requisitos

Antes de iniciar, verifique se você possui:

- Credenciais AWS configuradas localmente (`~/.aws/credentials`)
- AWS CLI instalada  
  👉 [Guia oficial de instalação](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html)
- Permissões suficientes para operar com S3, Glue e Athena
- Um arquivo `.csv` simples para teste

**Validação de ambiente:**

Se você utiliza múltiplos perfis AWS, defina o profile e a região padrão antes de executar comandos:

```bash
export AWS_PROFILE=mobiis
export AWS_DEFAULT_REGION=us-east-1
```

```bash
aws s3 ls
```

Você deve ver a lista de buckets disponíveis na conta.

---

## 📁 Etapa 1: Armazenamento no Amazon S3

### 1. Criar um novo bucket

> **Nota:** Utilize um nome de bucket único adicionando seu identificador (por exemplo, seu nome ou e-mail) ao final. Exemplo: `mobiis-treinamento-cognitivo-seunome`.  
> Iremos detalhar a escolha do nome do bucket em uma etapa futura.

```bash
aws s3 mb s3://mobiis-treinamento-cognitivo-seunome
```

### 2. Fazer upload de um arquivo BRONZE para o bucket

```bash
aws s3 cp sample_bronze_data.csv s3://mobiis-treinamento-cognitivo/bronze/sample_bronze_data/
```

### 3. Verificar se o arquivo foi enviado corretamente

```bash
aws s3 ls s3://mobiis-treinamento-cognitivo/bronze/sample_bronze_data
```

---

## 📊 Etapa 2: Catalogação com AWS Glue

### 4. Criar a database para a camada Bronze (caso ainda não exista)

> **Execute este comando diretamente no console do Athena** (Query Editor), pois é lá que as databases e tabelas do Data Catalog são criadas e gerenciadas.

```sql
CREATE DATABASE IF NOT EXISTS bronze_data;
```

### 5. Criar um Glue Crawler via Console

- **Name:** crawler-seunome
- **Fonte:** `s3://mobiis-treinamento-cognitivo/bronze/sample_bronze_data`
- **Destino:** Glue Data Catalog
- **Database:** `treinamento_db_mobiis_cog`

### 6. Executar o Crawler

Após a execução, verifique se a tabela `sample_bronze_data` foi criada corretamente no Glue Catalog, dentro do banco de dados `treinamento_db_mobiis_cog`.

---

## 🔎 Etapa 3: Consulta com AWS Athena

### 7. Consultar a tabela BRONZE

```sql
SELECT * FROM "treinamento_db_mobiis_cog"."sample_bronze_data";
```

---

## 🧱 Etapa 4: Criação da Database e da Tabela Silver Particionada

### 8. Criar a database para a camada Silver (caso ainda não exista)

```sql
CREATE DATABASE IF NOT EXISTS silver_data;
```

> **Nota:** O nome `silver_data` é uma sugestão para organizar as tabelas da camada Silver. Você pode ajustar conforme o padrão do seu projeto.

### 9. Criar a tabela particionada no Athena (camada Silver)

```sql
CREATE EXTERNAL TABLE silver_data.sample_data_partitioned (
  id  VARCHAR(20),
  idade INT,
  ativo BOOLEAN,
  salario DOUBLE,
  data_cadastro TIMESTAMP
)
PARTITIONED BY (
  ano  VARCHAR(20),
  mes  VARCHAR(20)
)
STORED AS PARQUET
LOCATION 's3://mobiis-treinamento-cognitivo/silver/'
TBLPROPERTIES (
  'parquet.compress' = 'SNAPPY'
);
```

### 10. Inserir dados na tabela particionada Silver

```sql
INSERT INTO silver_data.sample_data_partitioned
SELECT
  CAST(id AS VARCHAR(20)),
  CAST(idade AS INT),
  CAST(ativo AS BOOLEAN),
  CAST(salario AS DOUBLE),
  CAST(data_cadastro AS TIMESTAMP),
  CAST(year(CAST(data_cadastro AS TIMESTAMP)) AS VARCHAR(20)) AS ano,
  LPAD(CAST(month(CAST(data_cadastro AS TIMESTAMP)) AS VARCHAR(20)), 2, '0') AS mes
FROM "treinamento_db_mobiis_cog"."sample_bronze_data";
```

---

## 🔁 Etapa 5: Atualização de Metadados

### Opção A – Usar comando MSCK no Athena

```sql
MSCK REPAIR TABLE silver_data.sample_data_partitioned;
```

### Opção B – Criar novo Crawler para a camada Silver

- Fonte: `s3://mobiis-treinamento-cognitivo/silver/`
- Database: `silver_data`

---

## ✅ Resultado Esperado

Ao final do exercício, você deverá ter:

- 1 bucket no S3 com:
  - Pasta `/bronze/` contendo o arquivo original
  - Pasta `/silver/` com os dados transformados em Parquet particionado
- 1 Glue Crawler criado e executado com sucesso
- 2 databases visíveis no Athena:
  - `bronze_data` com 1 tabela CSV mapeada
  - `silver_data` com 1 tabela Parquet, compactada e particionada
- Tabelas consultáveis no Athena com performance otimizada

---

## ⭐ Etapa Opcional: Exemplos de Queries no Athena

### 1. Consulta simples: visualizar os primeiros registros

```sql
SELECT * FROM silver_data.sample_data_partitioned LIMIT 10;
```

### 2. Consulta com filtro: usuários ativos com salário acima de 5000

```sql
SELECT id, idade, salario, data_cadastro
FROM silver_data.sample_data_partitioned
WHERE ativo = true AND salario > 5000
ORDER BY salario DESC
LIMIT 10;
```

### 3. Consulta avançada: ranking de salários por ano usando window function

```sql
SELECT
  id,
  ano,
  mes,
  salario,
  RANK() OVER (PARTITION BY ano ORDER BY salario DESC) AS rank_salario_ano
FROM silver_data.sample_data_partitioned
ORDER BY ano, rank_salario_ano
LIMIT 20;
```

---

## 📚 Referências Oficiais AWS

- [AWS CLI – Comandos S3](https://docs.aws.amazon.com/cli/latest/reference/s3/index.html)
- [AWS Glue – Crawler](https://docs.aws.amazon.com/glue/latest/dg/add-crawler.html)
- [Athena – Preços](https://aws.amazon.com/athena/pricing/)
- [Glue – Preços](https://aws.amazon.com/glue/pricing/)
- [S3 – Preços](https://aws.amazon.com/s3/pricing/)

---

## 📝 Observações

- Para simular dados reais, utilize datasets públicos ou gere dados sintéticos com Pandas.
- Evite subir arquivos grandes em ambiente de testes — use amostras pequenas até o pipeline estar validado.
