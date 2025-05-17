# 🧪 Projeto Hands-on: Pipeline com AWS S3, Glue e Athena

Este guia apresenta os passos para construir um pipeline de dados simples utilizando serviços AWS como **S3**, **Glue** e **Athena**. O objetivo é simular uma arquitetura tipo "Medalhão", movendo dados de um estado bruto (**bronze**) para uma camada tratada (**silver**), com suporte a consultas SQL e organização de dados particionados.

---

## 📑 Índice

1. [Pré-requisitos](#pré-requisitos)
2. [Etapa 1: Armazenamento no Amazon S3](#etapa-1-armazenamento-no-amazon-s3)
3. [Etapa 2: Catalogação com AWS Glue](#etapa-2-catalogação-com-aws-glue)
4. [Etapa 3: Consulta com AWS Athena](#etapa-3-consulta-com-aws-athena)
5. [Etapa 4: Criação da Database e da Tabela Silver Particionada](#etapa-4-criação-da-database-e-da-tabela-silver-particionada)
6. [Etapa 5: Atualização de Metadados](#etapa-5-atualização-de-metadados)
7. [Etapa 6: Verificar o DDL da Tabela no Athena](#etapa-6-verificar-o-ddl-da-tabela-no-athena)
8. [Resultado Esperado](#resultado-esperado)
9. [Referências Oficiais AWS](#referências-oficiais-aws)

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
export AWS_DEFAULT_REGION=us-east-2
```

```bash
aws s3 ls
```

Você deve ver a lista de buckets disponíveis na conta.

---

## 📁 Etapa 1: Armazenamento no Amazon S3

### 1. Criar um novo bucket

> **Nota:** Utilize um nome de bucket único adicionando seu identificador (seu nome e sobrenome, sem espaços ou caracteres especiais).  
> Exemplo: `mobiis-treinamento-joao-silva`.

```bash
aws s3 mb s3://mobiis-treinamento-nome-sobrenome
```

### 2. Fazer upload de um arquivo BRONZE para o bucket

```bash
aws s3 cp sample_bronze_data.csv s3://mobiis-treinamento-nome-sobrenome/bronze/sample_bronze_data/
```

### 3. Verificar se o arquivo foi enviado corretamente

```bash
aws s3 ls s3://mobiis-treinamento-nome-sobrenome/bronze/sample_bronze_data
```

---

## 📊 Etapa 2: Catalogação com AWS Glue

### Criar um Glue Crawler

#### Passo a Passo para Criar o Crawler:

1. **Acesse o serviço AWS Glue > Crawlers > Criar Crawler.**

2. **Step 1: Set crawler properties**
   - **Name:** `crawler-bronze-nome-sobrenome`
   - **Description:** Crawler para a camada Bronze do aluno.
   - **Create IAM Role:** Selecione a opção **Create new IAM role** e nomeie como `AWSGlueServiceRole-nome-sobrenome`.

3. **Step 2: Choose data sources and classifiers**
   - **Data source:** Escolha **S3**.
   - **Include path:** Informe o caminho do bucket Bronze do aluno, por exemplo:  
     `s3://mobiis-treinamento-nome-sobrenome/bronze/sample_bronze_data/`
   - **Classifiers:** Deixe como padrão (nenhum adicional).

4. **Step 3: Configure security settings**
   - **IAM Role:** Certifique-se de que a role criada no Step 1 está selecionada.
   - **Encryption:** Deixe como padrão.

5. **Step 4: Set output and scheduling**
   - **Database:** Escolha ou crie a database Bronze do aluno, por exemplo: `bronze_nome_sobrenome`.
   - **Crawler schedule:** Escolha a opção **Run on demand** (executar sob demanda).  
     > **Nota:** O Crawler Schedule define quando o Crawler será executado. A opção "On demand" significa que ele será executado manualmente, sempre que necessário.

6. **Step 5: Review and create**
   - Revise as configurações e clique em **Create Crawler**.

#### Após criar o Crawler:
- Execute o **Run Crawler**.
- A execução leva cerca de **1 minuto** para ser concluída.
- O resultado esperado é:  
  - **1 table change**
  - **0 partition changes**

---

## 🔎 Etapa 3: Consulta com AWS Athena

### 7. Consultar a tabela BRONZE

```sql
SELECT * FROM "bronze_nome_sobrenome"."sample_bronze_data";
```

---

## 🧱 Etapa 4: Criação da Database e da Tabela Silver Particionada

### 8. Criar a database para a camada Silver (caso ainda não exista)

```sql
CREATE DATABASE IF NOT EXISTS silver_nome_sobrenome;
```

### 9. Criar a tabela particionada no Athena (camada Silver)

```sql
CREATE EXTERNAL TABLE silver_nome_sobrenome.sample_data_partitioned (
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
LOCATION 's3://mobiis-treinamento-nome-sobrenome/silver/'
TBLPROPERTIES (
  'parquet.compress' = 'SNAPPY'
);
```

---

## 🔁 Etapa 5: Atualização de Metadados

### Inserir dados na tabela particionada Silver

```sql
INSERT INTO silver_nome_sobrenome.sample_data_partitioned
SELECT
  CAST(id AS VARCHAR(20)),
  CAST(idade AS INT),
  CAST(ativo AS BOOLEAN),
  CAST(salario AS DOUBLE),
  CAST(data_cadastro AS TIMESTAMP),
  CAST(year(CAST(data_cadastro AS TIMESTAMP)) AS VARCHAR(20)) AS ano,
  LPAD(CAST(month(CAST(data_cadastro AS TIMESTAMP)) AS VARCHAR(20)), 2, '0') AS mes
FROM "bronze_nome_sobrenome"."sample_bronze_data";
```

### Atualizar partições no Athena

```sql
MSCK REPAIR TABLE silver_nome_sobrenome.sample_data_partitioned;
```

---

## 🛠️ Etapa 6: Verificar o DDL da Tabela no Athena

1. No console do Athena, localize a tabela `silver_nome_sobrenome.sample_data_partitioned`.
2. Clique nos **três pontinhos** ao lado do nome da tabela.
3. Selecione a opção **"Generate table DDL"**.
4. O DDL da tabela será exibido. Verifique se o `LOCATION` está correto, apontando para o bucket do aluno.

---

## ⭐ Etapa Opcional: Exemplos de Queries no Athena

### 1. Consulta simples: visualizar os primeiros registros

```sql
SELECT * FROM silver_nome_sobrenome.sample_data_partitioned
LIMIT 10;
```

### 2. Consulta com filtro: usuários ativos com salário acima de 5000

```sql
SELECT id, idade, salario, data_cadastro
FROM silver_nome_sobrenome.sample_data_partitioned
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
FROM silver_nome_sobrenome.sample_data_partitioned
ORDER BY ano, rank_salario_ano
LIMIT 20;
```

### 4. Consulta agregada: média de salários por ano e mês

```sql
SELECT
  ano,
  mes,
  ROUND(AVG(salario), 2) AS media_salario
FROM silver_nome_sobrenome.sample_data_partitioned
GROUP BY ano, mes
ORDER BY ano, mes;
```

### 5. Consulta com contagem: número de usuários ativos por ano

```sql
SELECT
  ano,
  COUNT(*) AS total_ativos
FROM silver_nome_sobrenome.sample_data_partitioned
WHERE ativo = true
GROUP BY ano
ORDER BY ano;
```

---

Essas consultas são exemplos práticos para explorar os dados na tabela Silver. Substitua `silver_nome_sobrenome` pelo nome correto da sua tabela no Athena.

---

## ✅ Resultado Esperado

Ao final do exercício, você deverá ter:

- 1 bucket no S3 com:
  - Pasta `/bronze/` contendo o arquivo original
  - Pasta `/silver/` com os dados transformados em Parquet particionado
- 2 Glue Crawlers criados e executados com sucesso
- 2 databases visíveis no Athena:
  - `bronze_nome_sobrenome` com 1 tabela CSV mapeada
  - `silver_nome_sobrenome` com 1 tabela Parquet, compactada e particionada
- Tabelas consultáveis no Athena com performance otimizada

---

## 📚 Referências Oficiais AWS

- [AWS CLI – Comandos S3](https://docs.aws.amazon.com/cli/latest/reference/s3/index.html)
- [AWS Glue – Crawler](https://docs.aws.amazon.com/glue/latest/dg/add-crawler.html)
- [Athena – Preços](https://aws.amazon.com/athena/pricing/)
- [Glue – Preços](https://aws.amazon.com/glue/pricing/)
- [S3 – Preços](https://aws.amazon.com/s3/pricing/)

---
