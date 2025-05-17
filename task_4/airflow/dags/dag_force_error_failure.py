"""
DAG de exemplo que **falha** propositalmente na segunda tarefa.
Executa a cada 30 min para testar tratamento de falhas e alertas.
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

def ok_task(step: str):
    now = datetime.now(tz=local_tz).strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{step}] Current local time: {now}")

def fail_task():
    raise RuntimeError("Erro intencional para fins de teste 🚨")

with DAG(
    dag_id="dag_force_error_failure",
    description="DAG que falha propositalmente na task middle_fail.",
    default_args=default_args,
    start_date=datetime(2025, 1, 1, tzinfo=local_tz),
    schedule_interval="*/30 * * * *",
    catchup=False,
    tags=["demo", "failure"],
) as dag:

    start = PythonOperator(task_id="start",        python_callable=ok_task,   op_kwargs={"step": "start"})
    middle_fail = PythonOperator(task_id="middle_fail", python_callable=fail_task)
    end = PythonOperator(task_id="end",            python_callable=ok_task,   op_kwargs={"step": "end"},
                         trigger_rule="all_done")  # executa mesmo se a anterior falhar

    start >> middle_fail >> end