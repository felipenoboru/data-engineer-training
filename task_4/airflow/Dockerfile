FROM apache/airflow:2.9.0

USER root

# 1. Conceder permissões ao /opt/airflow
RUN chmod -R a+rwX /opt/airflow

# 2. Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
 && apt-get clean && rm -rf /var/lib/apt/lists/*

# 3. Instalar o AWS CLI v2 (como root)
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
    && unzip awscliv2.zip \
    && ./aws/install -i /usr/local/aws-cli -b /usr/local/bin \
    && rm -rf awscliv2.zip ./aws

# (Opcional) Ajustar permissões extras, se necessário
RUN chmod -R a+rx /usr/local/aws-cli

# Criar diretório para dbt_project e conceder permissões
RUN mkdir -p /opt/airflow/dbt_project/target \
    && chmod -R a+rwX /opt/airflow/dbt_project

# 4. Mudar para o usuário airflow para instalar libs Python via pip
USER airflow

# 5. Instalar dbt-athena-community (e outras dependências, se quiser)
RUN pip install --no-cache-dir dbt-athena-community

# Se tiver requirements.txt:
# COPY requirements.txt /tmp/requirements.txt
# RUN pip install --no-cache-dir -r /tmp/requirements.txt