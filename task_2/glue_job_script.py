import sys
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrame
from pyspark.sql.functions import year, month, to_date, to_timestamp

# Configuração do Glue Job
sc = SparkContext()
glue_context = GlueContext(sc)
spark = glue_context.spark_session
job = Job(glue_context)
job.init("job-transform-daily-sales-silver", {})

# Caminhos e tabelas
source_db = "treinamento-db-mobiis-cog"
source_table = "daily_sales"
bucket_name = "mobiis-treinamento-nome-sobrenome"  # Substitua pelo seu bucket
catalog_db = "treinamento-db-mobiis-cog"  # Database onde as tabelas ficarão disponíveis no Athena

daily_sales_path = f"s3://{bucket_name}/silver/daily_sales/"
produtos_path = f"s3://{bucket_name}/silver/produtos/"

# Leitura da tabela de origem
df = glue_context.create_dynamic_frame.from_catalog(
    database=source_db,
    table_name=source_table
)

# Convertendo DynamicFrame para DataFrame para aplicar transformações
df_sales = df.toDF()

# Garantindo que a coluna 'data' esteja no formato de data (corrigindo erro de parsing)
df_sales = df_sales.withColumn("data", to_date(to_timestamp(df_sales["data"])))

# Removendo colunas desnecessárias (dia_semana e mes original em texto)
df_sales = df_sales.drop("dia_semana", "mes")

# Adicionando colunas de partição (ano e mes) a partir da coluna 'data'
df_sales = df_sales.withColumn("ano", year(df_sales["data"]))
df_sales = df_sales.withColumn("mes", month(df_sales["data"]))

# Transformação 1: Criar a tabela daily_sales
df_daily_sales = df_sales

# Gravação da tabela daily_sales na camada Silver e no Glue Catalog
df_daily_sales_dynamic = DynamicFrame.fromDF(df_daily_sales, glue_context, "df_daily_sales_dynamic")
glue_context.write_dynamic_frame.from_options(
    frame=df_daily_sales_dynamic,
    connection_type="s3",
    connection_options={
        "path": daily_sales_path,
        "partitionKeys": ["ano", "mes"],
        "catalogDatabase": catalog_db,
        "catalogTableName": "daily_sales",
        "updateBehavior": "UPDATE_IN_DATABASE"
    },
    format="parquet",
    format_options={"compression": "snappy"}
)

# Transformação 2: Criar a tabela produtos com valores distintos
df_produtos = df_sales.select("codigo", "ean", "descricao", "preco_unitario").distinct()

# Gravação da tabela produtos na camada Silver e no Glue Catalog
df_produtos_dynamic = DynamicFrame.fromDF(df_produtos, glue_context, "df_produtos_dynamic")
glue_context.write_dynamic_frame.from_options(
    frame=df_produtos_dynamic,
    connection_type="s3",
    connection_options={
        "path": produtos_path,
        "catalogDatabase": catalog_db,
        "catalogTableName": "produtos",
        "updateBehavior": "UPDATE_IN_DATABASE"
    },
    format="parquet",
    format_options={"compression": "snappy"}
)

# Commit do Job
job.commit()