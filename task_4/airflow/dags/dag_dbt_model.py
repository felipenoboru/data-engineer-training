"""
DAG dbt_model: faz orquestração dos modelos dbt, lendo o manifest.json em /opt/airflow/dbt_project/target/manifest.json,
e cria dinamicamente as tasks BashOperator para cada modelo. Aplica remoção extra de prefixos para
que o nome final do modelo coincida com o que consta no dbt_project.yml.
"""

import json
from datetime import timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago

DBT_PATH = "/opt/airflow/dbt_project"
JSON_MANIFEST = f"{DBT_PATH}/target/manifest.json"

def remove_prefix(node: str) -> str:
    """
    Remove 'model.' e também o prefixo do projeto, se existir,
    de modo que o nome final do modelo seja somente 'sample_test_gold', etc.
    Ex.: 'model.dbt_sample_project.sample_test_gold' => 'sample_test_gold'
    """
    # 1. Remove "model." se estiver no início
    node = node.replace("model.", "")

    # 2. Se o projeto for 'dbt_sample_project', remova também
    if node.startswith("dbt_sample_project."):
        node = node.replace("dbt_sample_project.", "", 1)

    return node

def load_dbt_models_from_manifest():
    with open(JSON_MANIFEST, "r") as jf:
        data = json.load(jf)

    parent_map = data.get("parent_map", {})
    nodes = {}
    for node, parents in parent_map.items():
        if node.startswith("model."):
            node_clean = remove_prefix(node)
            parents_clean = []
            for p in parents:
                if p.startswith("model."):
                    parents_clean.append(remove_prefix(p))
            nodes[node_clean] = list(set(parents_clean))
    return nodes

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": days_ago(2),
    "retries": 0,
    "retry_delay": timedelta(minutes=5),
}

dag = DAG(
    dag_id="dag_dbt_model",
    description="DAG que cria tasks dbt dinamicamente (camadas Silver/Gold) lendo manifest.json.",
    schedule_interval="@daily",
    catchup=False,
    default_args=default_args,
    tags=["dbt", "silver", "gold"],
)

models_map = load_dbt_models_from_manifest()
tasks = {}

for model_name, model_parents in models_map.items():
    cmd = f"""
      cd {DBT_PATH} &&
      dbt deps --profiles-dir {DBT_PATH} &&
      dbt run --profiles-dir {DBT_PATH} --models {model_name}
    """
    task_id = model_name.replace(".", "_")
    task = BashOperator(
        task_id=task_id,
        bash_command=cmd,
        dag=dag,
    )
    tasks[model_name] = task

# Define dependências
for model_name, parents in models_map.items():
    for parent in parents:
        if parent in tasks:
            tasks[parent] >> tasks[model_name]
