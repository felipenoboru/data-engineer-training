# Treinamento de Engenharia de Dados

Este repositório contém o material do treinamento prático para aspirantes a engenheiros de dados. Ele aborda tópicos essenciais como ingestão de dados, transformação, armazenamento, orquestração e fluxos de trabalho baseados em nuvem. Ideal para iniciantes e profissionais de nível intermediário que desejam desenvolver habilidades práticas em engenharia de dados moderna.

Este arquivo descreve o conteúdo ministrado no treinamento de Engenharia de Dados. Neste repositório, você encontrará as ferramentas necessárias para implementação e demonstração durante as aulas.

---

## Conteúdo Programático

### Dia 1: Foco em AWS

#### Conceitos Fundamentais
- **Engenharia de Dados**: Organização, segurança e escalabilidade.
- **Extração de Dados**: Melhores práticas e ferramentas.
- **Data Driven**:
  - Principais características de uma cultura orientada a dados.
  - Como aplicar o conceito de Data Driven em uma empresa.
- **Ambiente Big Data**:
  - Melhores práticas:
    - Armazenar dados de forma otimizada: Utilize formatos compactados e colunares, como Parquet, para melhorar o desempenho de consultas e reduzir custos.
    - Particionamento: Particione os dados no S3 com base em colunas frequentemente usadas em filtros para reduzir o volume de dados escaneados durante consultas.

#### Armazenamento
- **Amazon S3**:
  - Classes de armazenamento: [Documentação](https://aws.amazon.com/pt/s3/storage-classes/)
  - Criação de buckets.
  - Nomenclatura de buckets.
  - Controle de acesso.
  - Versionamento.
  - Tags.
  - Criptografia.
  - Políticas de bucket.
  - Configuração de ciclo de vida.
- **Amazon DynamoDB**:
  - Introdução e casos de uso.

#### Catálogo de Dados
- **AWS Glue Data Catalog**:
  - Glue Crawler:
    - Classificadores.
  - Banco de Dados no Glue.

#### Processamento de Dados
- **AWS Glue ETL Job** (Prática):
  - Visual ETL.
  - Scripts.
  - Detalhes do Job:
    - IAM Role.
    - Versão do Glue: [Glue 5.0](https://docs.aws.amazon.com/glue/latest/dg/release-notes.html).
    - Tipo de worker.
    - Auto Scale.
    - Número de workers solicitados.
    - Job Bookmark.
    - Propriedades avançadas.
    - Bibliotecas:
      - Como adicionar novas bibliotecas.
    - Parâmetros do Job.
  - Qualidade de Dados (DQ).
  - Pandas + Spark: [Artigo](https://towardsdatascience.com/run-pandas-as-fast-as-spark-f5eefe780c45).
  - Partições e paralelismo.
  - Como a AWS cobra pelo Glue?

#### Consultas
- **AWS Athena** (Prática):
  - Configuração do console:
    - Bucket para resultados de consultas.
  - Bancos de dados e tabelas.
  - Limitações do Athena em relação a bancos de dados tradicionais.
  - Benefícios do Athena em relação a bancos de dados tradicionais.
  - Partições e paralelismo.
  - Como a AWS cobra pelo Athena?

#### Monitoramento
- **AWS CloudWatch**:
  - Grupos de logs.
  - Métricas.
  - Alertas.

#### Criptografia
- **AWS KMS**:
  - Chaves gerenciadas pela AWS.
  - Chaves gerenciadas pelo cliente.

#### Gestão de Acessos
- **AWS IAM**:
  - Usuários.
  - Roles.
  - Políticas.

#### Controle de Custos
- **AWS Cost Explorer**:
  - Análise de custos por serviço.
  - Dimensões de custo.

---

### Dia 2: Foco em Ferramentas de Terceiros

#### Conceitos Fundamentais
- **Camadas de Dados**:
  - Bronze, Silver e Gold.
- **Dados Sensíveis (PII)**:
  - Identificação e proteção de dados pessoais.

#### Orquestração
- **Apache Airflow** (Prática):
  - DAGs.
  - Tasks.
  - Operadores.
  - Bibliotecas.
  - Plugins.
  - Schedulers.
  - Gestão de senhas.
  - Conexões.
  - Arquitetura (worker, scheduler, executor, etc.).

#### Transformação de Dados
- **DBT (Data Build Tool)** (Prática):
  - Modelos:
    - Fontes de dados.
  - Macros.
  - Variáveis.
  - Configurações:
    - Projeto DBT.
    - Profiles:
      - Configuração com Athena.
      - Threads.
  - Comandos úteis:
    - `dbt run`.
  - Documentação do DBT:
    - Como gerar.
    - O que é exibido.

---

### Tópicos Adicionais
- **Data Lakehouse**:
  - Conceito e benefícios.
  - Diferenças entre Data Lake e Data Warehouse.
- **Governança de Dados**:
  - Catálogo de dados.
  - Linhagem de dados.
  - Controle de acesso baseado em políticas.
- **Automação de Pipelines**:
  - Ferramentas e estratégias.
- **Testes em Pipelines de Dados**:
  - Testes unitários e de integração.
  - Ferramentas como Great Expectations.
