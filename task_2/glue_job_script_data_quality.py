from awsglue.context import GlueContext
from awsgluedq.transforms import EvaluateDataQuality
from pyspark.context import SparkContext

sc = SparkContext.getOrCreate()
glue_context = GlueContext(sc)
spark = glue_context.spark_session

# Carrega o DynamicFrame
input_dynamic_frame = glue_context.create_dynamic_frame.from_catalog(
    database="silver_nome_sobrenome",
    table_name="produtos"
)

# Define as regras de qualidade
dq_ruleset = """
Rules = [
    IsComplete "preco_unitario",
    ColumnValues "preco_unitario" > 0,
    IsUnique "id_produto"
]
"""

# Executa avaliação de qualidade
dq_result = EvaluateDataQuality().process_rows(
    frame=input_dynamic_frame,
    ruleset=dq_ruleset,
    publishing_options={
        "dataQualityEvaluationContext": "DQ_produtos_check",
        "enableDataQualityCloudWatchMetrics": True,
        "enableDataQualityResultsPublishing": True
    }
)

