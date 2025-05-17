"""
DAG que executa um projeto DBT utilizando o adaptador oficial
`dbt-athena` (https://github.com/dbt-labs/dbt-athena).

Pré-requisitos:
• O projeto DBT deve estar montado no contêiner em /opt/airflow/dbt_project/
  (ex.: volume "./dbt_project/:/opt/airflow/dbt_project/").
• A imagem precisa conter a lib `dbt-athena-community` instalada
  (via Dockerfile custom ou pip install no entrypoint).
• Variáveis AWS (`AWS_PROFILE`, `AWS_DEFAULT_REGION`, credenciais)
  devem estar disponíveis no contêiner.
"""

from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime
import pendulum

TZ = pendulum.local_timezone()

DEFAULT_ARGS = {"owner": "airflow", "retries": 0, "depends_on_past": False}

with DAG(
    dag_id="dbt_athena_run",
    description="Executa dbt build com o adaptador dbt-athena.",
    start_date=datetime(2025, 1, 1, tzinfo=TZ),
    schedule_interval="@daily",
    catchup=False,
    default_args=DEFAULT_ARGS,
    tags=["dbt", "athena"],
) as dag:

    dbt_deps = BashOperator(
        task_id="dbt_deps",
        bash_command="""
          cd /opt/airflow/dbt_project/ &&
          dbt deps
        """,
    )

    dbt_build = BashOperator(
        task_id="dbt_build",
        bash_command="""
          cd /opt/airflow/dbt_project/ &&
          dbt build --profiles-dir /opt/airflow/dbt_project/
        """,
    )

    dbt_docs = BashOperator(
        task_id="dbt_docs_generate",
        bash_command="""
          cd /opt/airflow/dbt_project/ &&
          dbt docs generate --profiles-dir /opt/airflow/dbt_project/
        """,
    )

    dbt_deps >> dbt_build >> dbt_docs