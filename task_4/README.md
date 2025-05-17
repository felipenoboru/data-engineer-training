# 🚀 Instruções para Projeto Airflow + DBT (Docker Compose)

## 📑 Índice
1. [Objetivo](#objetivo)  
2. [Pré-requisitos](#pré-requisitos)  
3. [Estrutura de Pastas](#estrutura-de-pastas)  
4. [Subindo o Airflow com Docker Compose](#subindo-o-airflow-com-docker-compose)  
5. [Criando uma DAG de Exemplo](#criando-uma-dag-de-exemplo)  
6. [Integração Airflow + DBT](#integração-airflow--dbt)  
7. [Verificação e Monitoramento](#verificação-e-monitoramento)  

---

## 📌 Objetivo
Este exercício tem o objetivo de validar seus conhecimentos em **Apache Airflow** e **DBT**.  
Você irá:
1. Subir uma instância **Airflow** local usando **Docker Compose**.  
2. Montar volumes para que a pasta `dags/` no host fique sincronizada com o contêiner.  
3. Criar uma **DAG** simples (ETL dummy) e executar.  
4. Desafio extra: orquestrar a execução dos seus modelos **DBT** dentro do Airflow, analisando agendamentos, logs e dependências.

---

## ✅ Pré-requisitos
- Docker Desktop ou Docker Engine + Docker Compose instalados.  
- Python 3.8+ (apenas se for testar DBT fora do contêiner).  
- Projeto DBT configurado (pode ser o projeto dos exercícios anteriores).  

---

## 📂 Estrutura de Pastas

```
task_4/
├── airflow/                # Diretório raiz do Airflow
│   ├── dags/               # <volume> Definições das DAGs
│   ├── plugins/            # <volume> Operadores / Hooks customizados
│   ├── logs/               # <volume> Logs gerados pelas tasks
│   ├── config/             # Arquivos extras de configuração (opcional)
│   ├── scripts/            # Scripts utilitários (pode conter shell ou python)
│   └── docker-compose.yml  # Stack Airflow (Webserver, Scheduler, DB, etc.)
└── README.md               # Este documento
```

Descrição rápida:  
- `dags/`: onde você colocará os arquivos `.py` das DAGs.  
- `plugins/`: permite adicionar operadores/hooks. Útil para integrar DBT ou S3, por exemplo.  
- `logs/`: volume para persistir logs fora do contêiner.  
- `config/`: use para um `airflow.cfg` customizado ou variáveis.  
- `scripts/`: scripts de inicialização ou helpers (por exemplo, instalar dependências extras).  
- `docker-compose.yml`: define serviços `webserver`, `scheduler`, `postgres`, entre outros.

---

## 🐳 Subindo o Airflow com Docker Compose

Antes de iniciar, exporte a variável `AIRFLOW_UID` (evita problemas de permissão de pastas
no host Linux/macOS):

```bash
export AIRFLOW_UID=$(id -u)
```
curl -LfO 'https://airflow.apache.org/docs/apache-airflow/2.10.5/docker-compose.yaml'

Dentro de `task_4/airflow/` execute:

```bash
# 1 ️⃣  Passo único de inicialização (cria metadados, conexões padrões etc.)
docker compose up airflow-init

# 2 ️⃣  Suba todo o stack em modo detached
docker compose up -d           # ou  docker compose up   (modo foreground)
```

Dicas úteis (retiradas do guia oficial):
- Para **parar** os serviços:  
  ```bash
  docker compose down
  ```
- Para parar **e** apagar volumes (reiniciar do zero):  
  ```bash
  docker compose down --volumes
  ```
- Desabilite DAGs de exemplo definindo a variável:
  ```bash
  AIRFLOW__CORE__LOAD_EXAMPLES=false
  ```
  (adicione no `docker-compose.yml` ou como `export`).
- Ver logs combinados:
  ```bash
  docker compose logs -f
  ```
- Atualize uma DAG: salve o arquivo em `airflow/dags/`; o scheduler recarrega a cada ~30 s.

Para maiores detalhes consulte:  
https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html

Acesse o Airflow UI em `http://localhost:8080`  
Usuário e senha padrões: `airflow / airflow` (override via variáveis no compose).

---

## 🏗️ Criando uma DAG de Exemplo

Crie o arquivo `airflow/dags/hello_dbt.py`:

```python
from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

default_args = {"owner": "airflow", "retries": 0}

with DAG(
    dag_id="hello_dbt",
    start_date=datetime(2025, 1, 1),
    schedule_interval=None,
    catchup=False,
    default_args=default_args,
    tags=["demo"],
) as dag:

    say_hello = BashOperator(
        task_id="say_hello",
        bash_command="echo 'Hello Airflow!'"
    )
```

Salve; o Airflow detectará a nova DAG automaticamente.

---

## 🔄 Integração Airflow + DBT

1. Copie (ou monte) seu projeto DBT em `airflow/scripts/dbt_project/`.  
2. Adicione uma task Bash no arquivo da DAG:

```python
run_dbt = BashOperator(
    task_id="run_dbt",
    bash_command="""
      cd /opt/airflow/scripts/dbt_project &&
      dbt deps &&
      dbt run --profiles-dir /opt/airflow/scripts/dbt_project
    """,
    env={"AWS_PROFILE": "mobiis", "AWS_DEFAULT_REGION": "us-east-2"},
)

say_hello >> run_dbt
```

3. Adicione `dbt-athena-community` ao `Dockerfile` custom ou instale dentro do contêiner usando um script em `scripts/`.

---

## 🔍 Verificação e Monitoramento

- **Logs**: clique na task dentro do Airflow UI e veja `Log`.  
- **Agendamento**: altere `schedule_interval` para `'@daily'` ou cron-like.  
- **Dependências**: visualize o *Graph View* para verificar a ordem de execução.  
- **DBT Docs**: rode `dbt docs generate` dentro da task e sirva em outra porta, se desejar.

> Pronto! Agora você tem um ambiente Airflow local, com DAGs versionadas em pasta, integração DBT e visibilidade completa via UI e logs.