
# 🧪 Projeto Hands-on: Pipeline com AWS S3, Glue e Athena

## 📌 Objetivo

Nesta atividade, vamos construir um **pipeline de dados** utilizando **AWS Glue, S3 e Athena**, realizando:

- Leitura de dados particionados via **Athena**
- Transformação com **AWS Glue + Spark**
- Escrita em uma nova camada **Gold** no S3
- Verificação dos resultados no **Glue Catalog**, **Athena**, e **CloudWatch Logs**

O foco é praticar paralelismo e boas práticas de execução distribuída com **Glue Spark Jobs**, observando custo, desempenho e organização de logs.

---

## ✅ Pré-requisitos

- Conta AWS com permissões nos serviços:
  - Glue
  - S3
  - Athena
  - CloudWatch
- Tabela previamente criada no Glue Catalog (particionada por ano/mês)
- Bucket S3 com estrutura de pastas: `raw/`, `silver/`, `gold/`

---

## 🛠️ Etapas da Atividade

### 1. Criar o Glue Job (via Console)

- Acesse o serviço **AWS Glue > Jobs > Criar Job**
- Tipo: **Spark**
- Linguagem: **Python (PySpark)**
- Fonte de dados: **Athena (via Glue Catalog)**
- Destino: **S3 - camada gold**

Exemplo de código de transformação:

```python
import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Leitura da tabela particionada
df = glueContext.create_dynamic_frame.from_catalog(
    database="raw_data",
    table_name="nome_da_tabela",
    transformation_ctx="df"
)

# Transformações (exemplo simples)
df_transformed = df

# Escrita na camada GOLD (parquet particionado)
glueContext.write_dynamic_frame.from_options(
    frame=df_transformed,
    connection_type="s3",
    connection_options={
        "path": "s3://meu-bucket/gold/",
        "partitionKeys": ["ano", "mes"]
    },
    format="parquet",
    format_options={"compression": "snappy"},
    transformation_ctx="df_write"
)

job.commit()
```

⚠️ Configure o job com **número de workers > 1** para garantir paralelismo.

---

### 2. Executar o Job

- Inicie o job pelo console
- Aguarde a conclusão

---

### 3. Validar resultados

#### ✅ Glue Catalog
- Verifique se a nova tabela foi criada ou atualizada na database da camada `gold`

#### ✅ Athena
- Execute a consulta:
  ```sql
  SELECT * FROM gold_data.nome_da_tabela LIMIT 10;
  ```

#### ✅ CloudWatch Logs
- Vá em **CloudWatch > Log groups**
- Acesse o grupo correspondente ao Glue Job
- Verifique se foram criados múltiplos **log streams** (um para cada executor/worker do Spark)

---

## 💡 Boas Práticas

- Sempre utilize **compressão Snappy** para melhor performance e custo
- Use **partitionKeys** consistentes (ano/mes) para consultas otimizadas
- Evite manter logs desnecessários: configure **retention policy** no CloudWatch
- Utilize **monitoramento no Cost Explorer** se for testar com grandes volumes

---

## 📎 Extras

- 🔗 [Documentação Glue Job](https://docs.aws.amazon.com/glue/latest/dg/glue-jobs.html)
- 🔗 [Documentação CloudWatch Logs](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/WhatIsCloudWatchLogs.html)
- 🔗 [AWS Pricing - Glue](https://aws.amazon.com/glue/pricing/)
- 🔗 [AWS Pricing - Athena](https://aws.amazon.com/athena/pricing/)
- 🔗 [AWS Pricing - S3](https://aws.amazon.com/s3/pricing/)

---

## ✅ Resultado Esperado

- Nova tabela criada em `gold_data` no Glue Catalog
- Dados disponíveis em Athena para consulta
- Logs no CloudWatch separados por node (log stream por executor)
- Pipeline completo com leitura, transformação, gravação e observabilidade

---
