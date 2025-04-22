# 🧪 Projeto Hands-on: Pipeline com AWS S3, Glue e Athena

Este guia apresenta os passos para construir um pipeline de dados simples utilizando serviços AWS como **S3**, **Glue** e **Athena**. O objetivo é simular uma arquitetura tipo "Medalhão", movendo dados de um estado bruto (raw) para uma camada tratada (silver), com suporte a consultas SQL e organização de dados particionados.

---

## ✅ Pré-requisitos

Antes de iniciar, verifique se você possui:

- Credenciais AWS configuradas localmente (`~/.aws/credentials`)
- AWS CLI instalada  
  👉 [Guia oficial de instalação](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html)
- Permissões suficientes para operar com S3, Glue e Athena
- Um arquivo `.csv` simples para teste

**Validação de ambiente:**

```bash
aws s3 ls
```

Você deve ver a lista de buckets disponíveis na conta.

---

## 📁 Etapa 1: Armazenamento no Amazon S3

### 1. Criar um novo bucket

```bash
aws s3 mb s3://nome-do-seu-bucket
```

### 2. Fazer upload de um arquivo RAW para o bucket

```bash
aws s3 cp caminho/para/arquivo.csv s3://nome-do-seu-bucket/raw/
```

### 3. Verificar se o arquivo foi enviado corretamente

```bash
aws s3 ls s3://nome-do-seu-bucket/raw/
```

---

## 📊 Etapa 2: Catalogação com AWS Glue

### 4. Criar um Glue Crawler via Console

- **Fonte**: `s3://nome-do-seu-bucket/raw/`
- **Destino**: Glue Data Catalog
- **Database**: `raw_data`

### 5. Executar o Crawler

Após a execução, verifique se a tabela foi criada corretamente no Glue Catalog.

---

## 🔎 Etapa 3: Consulta com AWS Athena

### 6. Consultar a tabela RAW

```sql
SELECT * FROM raw_data.nome_da_tabela;
```

---

## 🧱 Etapa 4: Criação da Tabela Silver Particionada

### 7. Criar a tabela particionada no Athena (camada Silver)

```sql
CREATE TABLE silver_data.sample_data (
  id STRING,
  idade INT,
  ativo BOOLEAN,
  salario DOUBLE,
  data_cadastro TIMESTAMP
)
PARTITIONED BY (
  ano STRING,
  mes STRING
)
STORED AS PARQUET
LOCATION 's3://nome-do-seu-bucket/silver/'
TBLPROPERTIES (
  'parquet.compress' = 'SNAPPY'
);
```

### 8. Inserir dados da camada RAW para a Silver

```sql
INSERT INTO silver_data.sample_data
SELECT
  id,
  idade,
  ativo,
  salario,
  data_cadastro,
  '2025' AS ano,
  '04' AS mes
FROM raw_data.nome_da_tabela;
```

---

## 🔁 Etapa 5: Atualização de Metadados

### Opção A – Criar novo Crawler para a camada Silver

- Fonte: `s3://nome-do-seu-bucket/silver/`
- Database: `silver_data`

### Opção B – Usar comando MSCK no Athena

```sql
MSCK REPAIR TABLE silver_data.sample_data;
```

---

## ✅ Resultado Esperado

Ao final do exercício, você deverá ter:

- 1 bucket no S3 com:
  - Pasta `/raw/` contendo o arquivo original
  - Pasta `/silver/` com os dados transformados em Parquet particionado
- 1 Glue Crawler criado e executado com sucesso
- 2 databases visíveis no Athena:
  - `raw_data` com 1 tabela CSV mapeada
  - `silver_data` com 1 tabela Parquet, compactada e particionada
- Tabelas consultáveis no Athena com performance otimizada

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
