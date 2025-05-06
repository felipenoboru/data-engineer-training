# 🧪 Projeto Hands-on: Pipeline com AWS S3, Glue e Athena

## 📑 Índice

1. [Objetivo](#objetivo)
2. [Pré-requisitos](#pré-requisitos)
3. [Etapas da Atividade](#etapas-da-atividade)
   - [1. Criar o Glue Job](#1-criar-o-glue-job)
   - [2. Executar o Job](#2-executar-o-job)
   - [3. Validar Resultados](#3-validar-resultados)
   - [4. Registrar a tabela Gold no Glue Catalog](#4-registrar-a-tabela-gold-no-glue-catalog)
   - [5. Verificar e Configurar Permissões no IAM](#5-verificar-e-configurar-permissões-no-iam)
   - [6. Verificação Final dos Resultados](#6-verificação-final-dos-resultados)
4. [Boas Práticas](#boas-práticas)
5. [Extras](#extras)
6. [Resultado Esperado](#resultado-esperado)

---

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
- Tabelas previamente criadas no Glue Catalog:
  - `bronze_data.sample_bronze_data` (camada Bronze)
  - `silver_data.sample_data_partitioned` (camada Silver)
- Bucket S3 com estrutura de pastas: `bronze/`, `silver/`, `gold/`

---

## 🛠️ Etapas da Atividade

### 1. Criar o Glue Job

- Acesse o serviço **AWS Glue > Jobs > Criar Job**.
- Preencha os campos do formulário conforme abaixo:

**Job Details:**
- **Name:** `job-transform-silver-to-gold`
- **IAM Role:** Selecione uma role com as permissões necessárias para Glue, S3 e Glue Catalog.
- **Type:** Spark
- **Glue Version:** Glue 5.0
- **Language:** Python 3
- **Worker Type:** G.1X
- **Number of Workers:** 2
- **Max Concurrent Runs:** 1 (ou ajuste conforme sua necessidade)
- **Script file path:** Faça upload do script Python para um bucket S3 e informe o caminho aqui.
- **Temporary directory:** Informe um caminho temporário em S3, por exemplo: `s3://mobiis-treinamento-cognitivo/temp/`

**Observação:**  
Essas configurações garantem que o job utilize Spark 3.5 (Glue 5.0), Python 3, e execute em paralelo com 2 workers do tipo G.1X, conforme solicitado.

Adicione o seguinte código ao Glue Job:

```python
import sys
import boto3
import re
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrame

class GlueJobRunner:
    def __init__(self, job_name):
        self.args = {'JOB_NAME': job_name}
        self.sc = SparkContext()
        self.glue_context = GlueContext(self.sc)
        self.spark = self.glue_context.spark_session
        self.job = Job(self.glue_context)
        self.job.init(job_name, self.args)
        self.s3 = boto3.resource('s3')
        self.glue_client = boto3.client('glue')

    def clean_s3_path(self, s3_uri):
        """
        Limpa todos os objetos dentro do caminho S3 especificado.
        Ex: s3://bucket/path/ -> remove todos os objetos sob 'path/'
        """
        match = re.match(r"s3://([^/]+)/(.+)", s3_uri)
        if not match:
            raise ValueError("S3 URI inválido.")
        bucket_name, prefix = match.groups()
        bucket = self.s3.Bucket(bucket_name)
        bucket.objects.filter(Prefix=prefix).delete()

    def create_catalog_table(self, database, table_name, s3_path, columns, partitions):
        """
        Cria uma nova tabela no Glue Catalog.
        """
        self.glue_client.create_table(
            DatabaseName=database,
            TableInput={
                'Name': table_name,
                'StorageDescriptor': {
                    'Columns': columns,
                    'Location': s3_path,
                    'InputFormat': 'org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat',
                    'OutputFormat': 'org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat',
                    'SerdeInfo': {
                        'SerializationLibrary': 'org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe',
                        'Parameters': {'serialization.format': '1'}
                    },
                    'StoredAsSubDirectories': False
                },
                'PartitionKeys': partitions,
                'TableType': 'EXTERNAL_TABLE',
                'Parameters': {
                    'classification': 'parquet',
                    'compressionType': 'snappy',
                    'typeOfData': 'file'
                }
            }
        )

    def run(self):
        # Configurações
        source_db = "silver_data"
        source_table = "sample_data_partitioned"
        target_db = "gold_data"
        target_table = "sample_data_aggregated"
        target_path = "s3://mobiis-treinamento-cognitivo/gold/"

        # Limpa dados antigos no S3
        self.clean_s3_path(target_path)

        # Leitura da tabela particionada da camada Silver
        df = self.glue_context.create_dynamic_frame.from_catalog(
            database=source_db,
            table_name=source_table
        )

        # Transformação: calcula média salarial por idade, ativo, ano, mês
        df_transformed = df.toDF() \
            .groupBy("idade", "ativo", "ano", "mes") \
            .agg({"salario": "avg"}) \
            .withColumnRenamed("avg(salario)", "salario_medio")

        # Converte de volta para DynamicFrame
        df_transformed = DynamicFrame.fromDF(df_transformed, self.glue_context, "df_transformed")

        # Cria a tabela no Glue Catalog (caso ainda não exista)
        try:
            self.create_catalog_table(
                database=target_db,
                table_name=target_table,
                s3_path=target_path,
                columns=[
                    {"Name": "idade", "Type": "int"},
                    {"Name": "ativo", "Type": "boolean"},
                    {"Name": "salario_medio", "Type": "double"},
                ],
                partitions=[
                    {"Name": "ano", "Type": "int"},
                    {"Name": "mes", "Type": "int"}
                ]
            )
        except self.glue_client.exceptions.AlreadyExistsException:
            pass  # Tabela já existe

        # Escreve os dados no S3 e atualiza o catálogo Glue
        self.glue_context.write_dynamic_frame.from_options(
            frame=df_transformed,
            connection_type="s3",
            connection_options={
                "path": target_path,
                "partitionKeys": ["ano", "mes"],
                "enableUpdateCatalog": True,
                "updateBehavior": "UPDATE_IN_DATABASE",
                "database": target_db,
                "tableName": target_table
            },
            format="parquet",
            format_options={"compression": "snappy"}
        )

        self.job.commit()


if __name__ == "__main__":
    args = getResolvedOptions(sys.argv, ['JOB_NAME'])
    job_runner = GlueJobRunner(args['JOB_NAME'])
    job_runner.run()
```

⚠️ Configure o job com **número de workers > 1** para garantir paralelismo.

---

### 2. Executar o Job

- Inicie o job pelo console
- Aguarde a conclusão

---

### 3. Validar Resultados

#### ✅ Glue Catalog
- Verifique se a nova tabela foi criada ou atualizada na database da camada `gold_data`.

#### ✅ Athena
- Execute a consulta:
  ```sql
  SELECT * FROM gold_data.sample_data_partitioned LIMIT 10;
  ```

#### ✅ CloudWatch Logs
- Vá em **CloudWatch > Log groups**
- Acesse o grupo correspondente ao Glue Job
- Verifique se foram criados múltiplos **log streams** (um para cada executor/worker do Spark)

---

### 4. Registrar a tabela Gold no Glue Catalog

Após a execução do Glue Job, é necessário garantir que a tabela e suas partições estejam visíveis no Glue Catalog e no Athena. Você pode fazer isso de duas formas:

#### Opção A – Criar e executar um Glue Crawler

- Acesse o serviço **AWS Glue > Crawlers > Criar Crawler**.
- **Name:** `crawler-gold-data`
- **Fonte de dados:** S3
- **Caminho:** `s3://mobiis-treinamento-cognitivo/gold/`
- **Destino:** Glue Data Catalog
- **Database:** `gold_data`
- Execute o crawler para registrar a tabela e as partições no Glue Catalog.

#### Opção B – Atualizar partições diretamente no Athena

Se preferir, você pode atualizar as partições da tabela gold diretamente pelo Athena com o comando:

```sql
MSCK REPAIR TABLE gold_data.sample_data_aggregated;
```

---

### 5. Verificar e Configurar Permissões no IAM

Antes de executar o Glue Job, certifique-se de que a **IAM Role** associada ao job possui as permissões necessárias para acessar o S3 e o Glue Catalog.  
Inclua a seguinte policy na role utilizada pelo Glue Job:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "S3Access",
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::mobiis-treinamento-cognitivo",
                "arn:aws:s3:::mobiis-treinamento-cognitivo/*"
            ]
        },
        {
            "Sid": "GlueCatalogAccess",
            "Effect": "Allow",
            "Action": [
                "glue:CreateTable",
                "glue:UpdateTable",
                "glue:GetTable",
                "glue:GetTables",
                "glue:DeleteTable",
                "glue:GetDatabase",
                "glue:GetDatabases",
                "glue:CreateDatabase",
                "glue:UpdateDatabase",
                "glue:DeleteDatabase"
            ],
            "Resource": "*"
        }
    ]
}
```

> **Dica:**  
> Para adicionar a policy, acesse o console IAM, selecione a role usada pelo Glue Job, clique em "Adicionar permissões" e cole o JSON acima.

---

### 6. Verificação Final dos Resultados

Após a execução de todas as etapas, faça as seguintes verificações para garantir que o pipeline foi concluído com sucesso:

#### a) Verificar o conteúdo da camada Gold no Bucket S3

- Acesse o console do S3 e navegue até o bucket `mobiis-treinamento-cognitivo/gold/`.
- Confirme que existem arquivos Parquet organizados nas pastas de partição (`ano=` e `mes=`).
- Você também pode usar o comando abaixo para listar os arquivos via terminal:
  ```bash
  aws s3 ls s3://mobiis-treinamento-cognitivo/gold/ --recursive
  ```

#### b) Verificar os logs do job executado no CloudWatch

- Acesse o serviço **CloudWatch > Log groups**.
- Localize o log group correspondente ao seu Glue Job (`/aws-glue/jobs/output`).
- Verifique se há múltiplos log streams (um para cada worker) e se não há erros nos logs.

#### c) Verificar os resultados das tabelas no Glue Catalog

- Acesse o serviço **AWS Glue > Databases**.
- Confirme que a tabela `sample_data_aggregated` está presente na database `gold_data`.
- Verifique se as partições foram criadas corretamente.
- No Athena, execute uma consulta para visualizar os dados:
  ```sql
  SELECT * FROM gold_data.sample_data_aggregated LIMIT 10;
  ```

Se todos esses itens estiverem corretos, seu pipeline está funcionando de ponta a ponta!

---

## 💡 Boas Práticas

- Sempre utilize **compressão Snappy** para melhor performance e custo.
- Use **partitionKeys** consistentes (ano/mes) para consultas otimizadas.
- Evite manter logs desnecessários: configure **retention policy** no CloudWatch.
- Utilize **monitoramento no Cost Explorer** se for testar com grandes volumes.

---

## 📎 Extras

- 🔗 [Documentação Glue Job](https://docs.aws.amazon.com/glue/latest/dg/glue-jobs.html)
- 🔗 [Documentação CloudWatch Logs](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/WhatIsCloudWatchLogs.html)
- 🔗 [AWS Pricing - Glue](https://aws.amazon.com/glue/pricing/)
- 🔗 [AWS Pricing - Athena](https://aws.amazon.com/athena/pricing/)
- 🔗 [AWS Pricing - S3](https://aws.amazon.com/s3/pricing/)

---

## ✅ Resultado Esperado

- Nova tabela criada em `gold_data.sample_data_partitioned` no Glue Catalog.
- Dados disponíveis em Athena para consulta.
- Logs no CloudWatch separados por node (log stream por executor).
- Pipeline completo com leitura, transformação, gravação e observabilidade.

---
