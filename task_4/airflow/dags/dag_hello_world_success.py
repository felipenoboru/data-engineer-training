"""
DAG de exemplo que **sempre** finaliza com sucesso.
Executa a cada 30 min e imprime o horário local em três tarefas sequenciais.
"""

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import pendulum

local_tz = pendulum.local_timezone()

default_args = {
    "owner": "airflow",
    "retries": 0,
    "depends_on_past": False,
}

def _print_time(step: str):
    now = datetime.now(tz=local_tz).strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{step}] Current local time: {now}")

with DAG(
    dag_id="dag_hello_world_success",
    description="DAG de teste que sempre conclui com sucesso.",
    default_args=default_args,
    start_date=datetime(2025, 1, 1, tzinfo=local_tz),
    schedule_interval="*/30 * * * *",   # a cada 30 min
    catchup=False,
    tags=["demo", "success"],
) as dag:

    start = PythonOperator(task_id="start",   python_callable=_print_time, op_kwargs={"step": "start"})
    middle = PythonOperator(task_id="middle", python_callable=_print_time, op_kwargs={"step": "middle"})
    end = PythonOperator(task_id="end",       python_callable=_print_time, op_kwargs={"step": "end"})

    start >> middle >> end