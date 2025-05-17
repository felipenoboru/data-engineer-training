# 🧪 Projeto Hands-on: Pipeline com AWS S3, Glue e Athena (Camada Silver)

## 📑 Índice

1. [Objetivo](#objetivo)
2. [Pré-requisitos](#pré-requisitos)
3. [Etapas da Atividade](#etapas-da-atividade)
   - [1. Parâmetros Pessoais](#1-parâmetros-pessoais)
   - [2. Leitura da Tabela de Origem](#2-leitura-da-tabela-de-origem)
   - [3. Configurar Permissões no IAM](#3-configurar-permissões-no-iam)
   - [4. Criação do Glue Job para Silver](#4-criação-do-glue-job-para-silver)
   - [5. Execução e Validação](#5-execução-e-validação)
   - [6. Registro e Atualização no Glue Catalog](#6-registro-e-atualização-no-glue-catalog)
   - [7. Verificação Final dos Resultados](#7-verificação-final-dos-resultados)
4. [Boas Práticas](#boas-práticas)
5. [Extras](#extras)
6. [Exercício Adicional](#6-exercício-adicional)
7. [Resultado Esperado](#resultado-esperado)

---

## 📌 Objetivo

Construir um pipeline de dados usando **AWS Glue, S3 e Athena**, partindo da tabela de vendas `"treinamento-db-mobiis-cog"."daily_sales"` na camada Bronze. O objetivo é criar duas novas tabelas na camada Silver:

1. **Tabela `daily_sales`**: Uma versão da tabela original sem as colunas `dia_semana` e `mes`.
2. **Tabela `produtos`**: Uma tabela contendo os valores distintos de `codigo`, `ean`, `descricao` e `preco_unitario`.

Os resultados finais devem ser gravados na camada Silver, utilizando Glue Jobs para transformação e gravação.

---

## ✅ Pré-requisitos

- Conta AWS com permissões nos serviços: Glue, S3, Athena
- Tabela de origem: `"treinamento-db-mobiis-cog"."daily_sales"` (localizada na camada Bronze)
- Bucket S3 próprio (exemplo: `mobiis-treinamento-nome-sobrenome`)
- Glue Catalog configurado
- **Todos os nomes de objetos (buckets, tabelas, databases, paths) devem conter seu nome e sobrenome para evitar conflitos.**

---

## 🛠️ Etapas da Atividade

### 1. Parâmetros Pessoais

Antes de começar, defina um identificador único para seus objetos:

- **Exemplo:**  
  - Nome: João Silva  
  - Bucket: `mobiis-treinamento-joao-silva`
  - Database Glue: `silver_joao_silva`
  - Tabela Silver 1: `daily_sales_joao_silva`
  - Tabela Silver 2: `produtos_joao_silva`
  - Caminho S3 para `daily_sales`: `s3://mobiis-treinamento-joao-silva/silver/daily_sales/`
  - Caminho S3 para `produtos`: `s3://mobiis-treinamento-joao-silva/silver/produtos/`

> Substitua `joao-silva` pelo seu nome e sobrenome SEM espaços e SEM caracteres especiais.

---

### 2. Leitura da Tabela de Origem

A tabela de origem `"treinamento-db-mobiis-cog"."daily_sales"` possui milhões de registros.

**Exemplo de leitura com limite (Athena):**
```sql
SELECT * FROM "treinamento-db-mobiis-cog"."daily_sales"
LIMIT 100000;
```

---

### 3. Configurar Permissões no IAM

Antes de executar o Glue Job, é necessário configurar as permissões adequadas na role IAM associada ao Glue.

#### Passo 1: Criar ou Editar a Role IAM

1. Acesse o console da AWS e vá para o serviço **IAM**.
2. Crie uma nova role ou edite uma existente:
   - **Tipo de Serviço:** Escolha **Glue**.
   - **Permissões:** Adicione as seguintes políticas:
     - `AWSGlueServiceRole`: Permite que o Glue execute jobs e acesse o Glue Catalog.
     - `AmazonS3FullAccess` (ou restrinja ao bucket do aluno): Permite que o Glue leia e grave dados no S3.
     - `AmazonAthenaFullAccess`: Permite que o Glue interaja com o Athena, se necessário.
   - **Nome da Role:** `AWSGlueServiceRole-nome-sobrenome`.

3. Salve a role.

#### Passo 2: Verificar Permissões no Bucket S3

1. Acesse o console do S3 e localize o bucket do aluno.
2. Certifique-se de que a role criada tenha permissões de leitura e gravação no bucket.

---

### 4. Criação do Glue Job para Silver

#### Passo 1: Criar o Glue Job

- Acesse o serviço **AWS Glue > Jobs > Criar Job**.
- Preencha os campos do formulário conforme abaixo:

**Job Details:**
- **Name:** `job-transform-daily-sales-silver-nome-sobrenome`
- **IAM Role:** Selecione a role criada anteriormente (`AWSGlueServiceRole-nome-sobrenome`).
- **Type:** Spark
- **Glue Version:** Glue 5.0
- **Language:** Python 3
- **Worker Type:** G.1X
- **Number of Workers:** 2
- **Max Concurrent Runs:** 1
- **Temporary directory:** Informe um caminho temporário em S3, por exemplo: `s3://mobiis-treinamento-nome-sobrenome/temp/`

#### Passo 2: Adicionar o Script do Glue Job

Adicione o seguinte código ao Glue Job: /task_2/glue_job_script.py

⚠️ **Importante:**  
- Substitua `nome-sobrenome` pelo seu nome e sobrenome SEM espaços e SEM caracteres especiais.
- Configure o job com **número de workers > 1** para garantir paralelismo.

---

---

### 5. Registro e Atualização no Glue Catalog

Após a execução do Glue Job, é necessário garantir que as tabelas e suas partições estejam visíveis no Glue Catalog e no Athena. Você pode fazer isso de duas formas:

#### Opção A – Criar e executar um Glue Crawler

- **Name:** `crawler-silver-data-nome-sobrenome`
- **Fonte de dados:** S3
- **Caminho:** `s3://mobiis-treinamento-nome-sobrenome/silver/`
- **Destino:** Glue Data Catalog
- **Database:** `silver_nome_sobrenome`
- marque :Create a single schema for each S3 path 

#### Opção B – Atualizar partições diretamente no Athena

```sql
MSCK REPAIR TABLE silver_nome_sobrenome.daily_sales_nome_sobrenome;
```

### 6. Execução e Validação

#### Execução do Job
- Inicie o job pelo console.
- Aguarde a conclusão.

#### Validação dos Resultados

**Glue Catalog:**  
- Verifique se as novas tabelas foram criadas ou atualizadas na database da camada `silver_nome_sobrenome`.

**Athena:**  
- Execute as consultas:
  ```sql
  SELECT * FROM silver_nome_sobrenome.daily_sales LIMIT 10;
  ```

  ```sql
  SELECT * FROM silver_nome_sobrenome.produtos LIMIT 10;
  ```


---

### 7. Verificação Final dos Resultados

Após a execução do Glue Job e a atualização do Glue Catalog, verifique os seguintes pontos:

1. **No Glue Catalog:**
   - Confirme que as tabelas `daily_sales` e `produtos` foram criadas na database `silver_nome_sobrenome`.

2. **No Athena:**
   - Execute as consultas:
     ```sql
     SELECT * FROM silver_nome_sobrenome.daily_sales LIMIT 10;
     ```
     ```sql
     SELECT * FROM silver_nome_sobrenome.produtos LIMIT 10;
     ```

3. **No S3:**
   - Verifique se os dados foram gravados nos caminhos:
     - `s3://mobiis-treinamento-nome-sobrenome/silver/daily_sales/`
     - `s3://mobiis-treinamento-nome-sobrenome/silver/produtos/`

---

## 💡 Boas Práticas

- Sempre utilize **compressão Snappy** para melhor performance e custo.
- Use **partitionKeys** consistentes (ano/mes) para consultas otimizadas.
- Evite manter logs desnecessários: configure **retention policy** no CloudWatch.
- Utilize **monitoramento no Cost Explorer** se for testar com grandes volumes.

---

## 📎 Extras

- 🔗 [Documentação Glue Crawler](https://docs.aws.amazon.com/glue/latest/dg/add-crawler.html)
- 🔗 [Documentação Athena](https://docs.aws.amazon.com/athena/latest/ug/what-is.html)
- 🔗 [AWS Pricing - Athena](https://aws.amazon.com/athena/pricing/)
- 🔗 [AWS Pricing - S3](https://aws.amazon.com/s3/pricing/)

---

## 🧍️‍♂️ Exercício Adicional: Validação de Qualidade dos Dados (Data Quality)

A validação de qualidade dos dados é um passo essencial para garantir que os dados processados atendam aos requisitos de integridade e consistência. O **AWS Glue 5.0** oferece suporte nativo para a criação de regras de qualidade utilizando a linguagem **DQDL (Data Quality Definition Language)**.

### 🚀 Desafio: Crie suas próprias regras de validação

Utilize o exemplo abaixo como ponto de partida para criar um conjunto de regras de qualidade para os dados processados no pipeline:

```python
dq_ruleset = """
Rules = [
    IsComplete "preco_unitario",          # Garante que a coluna 'preco_unitario' não tenha valores nulos
    ColumnValues "preco_unitario" > 0,   # Garante que os valores de 'preco_unitario' sejam maiores que 0
    IsUnique "id_produto"                # Garante que os valores de 'id_produto' sejam únicos
]
"""
```

### 📘 Como funciona a linguagem DQDL?

A **DQDL (Data Quality Definition Language)** é uma linguagem declarativa usada para definir regras de qualidade de dados. Cada regra é composta por:

- **Nome da Regra:** Define o tipo de validação (ex.: `IsComplete`, `IsUnique`, `ColumnValues`).
- **Coluna Alvo:** Especifica a coluna que será validada.
- **Condição (Opcional):** Define critérios adicionais para validação (ex.: `> 0`).

#### Exemplos de Regras:
- `IsComplete "coluna"`: Verifica se a coluna não contém valores nulos.
- `IsUnique "coluna"`: Garante que os valores da coluna sejam únicos.
- `ColumnValues "coluna" > valor`: Valida se os valores da coluna atendem a uma condição específica.

### 📝 Tarefa

1. **Crie suas próprias regras de validação** para as tabelas `daily_sales` e `produtos`.  
   - Exemplo: Valide que `descricao` não seja nula e que `codigo` seja único.

2. **Implemente as regras no Glue Job** utilizando o recurso de validação de qualidade.

3. **Execute o Glue Job e, após a execução, acesse a aba "Data Quality" no console do Glue Job.**  
   - Verifique os resultados em **"Data quality result"** e confira o **score** de qualidade dos dados para cada regra aplicada.

4. **Teste e valide os resultados** no Glue Catalog e no Athena.

### 🔗 Recursos Úteis

- [Documentação Oficial do AWS Glue Data Quality](https://docs.aws.amazon.com/pt_br/glue/latest/dg/dqdl.html): Explore mais exemplos e detalhes sobre a linguagem DQDL.
- [AWS Glue Data Quality Ruleset](https://docs.aws.amazon.com/glue/latest/dg/data-quality-ruleset.html): Saiba como configurar e aplicar regras de qualidade no Glue.

---

💡 **Dica:** Aplique as regras de qualidade antes de gravar os dados na camada Silver para garantir que apenas dados válidos sejam processados.

---

## ✅ Resultado Esperado

- Tabelas `daily_sales` e `produtos` criadas na camada Silver.
- Dados disponíveis no Glue Catalog e Athena para consulta.
- Pipeline completo com leitura, transformação, validação e gravação.

---
