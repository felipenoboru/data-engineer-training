# 🛠️ Guia de Instalação do Ambiente de Engenharia de Dados

Este documento contém todas as instruções necessárias para configurar o ambiente local com os seguintes componentes:

- Python 3.11.6  
- Ambiente virtual (venv)  
- AWS CLI com perfil `mobiis`  
- Docker e Docker Compose  
- DBT com adaptador para Athena  
- Visual Studio Code (VS Code)  

---

## 📋 Sumário

1. [Pré-requisitos Gerais](#pré-requisitos-gerais)  
2. [Instalação do Python 3.11.6 + Virtual Environment](#instalação-do-python-3116--virtual-environment)  
3. [Instalação do Visual Studio Code](#instalação-do-visual-studio-code)  
4. [Configuração da AWS CLI e Perfil `mobiis`](#configuração-da-aws-cli-e-perfil-mobiis)  
5. [Instalação do Docker e Docker Compose](#instalação-do-docker-e-docker-compose)  
6. [Instalação do DBT (Athena Adapter)](#instalação-do-dbt-athena-adapter)  
7. [Comandos para Validação](#comandos-para-validação)  
8. [Referências e Links Úteis](#referências-e-links-úteis)

---

## ✅ Pré-requisitos Gerais

- Conexão com a internet.  
- Conta AWS com permissões para usar serviços S3, Glue, Athena e IAM.  
- Permissões administrativas para instalar softwares.  

---

## 🐍 Instalação do Python 3.11.6 + Virtual Environment

### 🔽 1. Instalar Python 3.11.6

- **Mac**:
  - Acesse: [https://www.python.org/downloads/](https://www.python.org/downloads/)
  - Siga o instalador e, depois, confirme no terminal:
    ```bash
    python3 --version
    ```

- **Windows**:
  - Baixe em: [https://www.python.org/downloads/windows/](https://www.python.org/downloads/windows/)
  - **Importante**: Marque a opção `Add Python to PATH`.
  - Valide no prompt:
    ```bash
    python --version
    ```

### ⚙️ 2. Criar e Ativar Ambiente Virtual

- **Mac/Linux**:
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```

- **Windows**:
  ```bash
  python -m venv .venv
  .venv\Scripts\activate
  ```

> Após a ativação, o prompt deve exibir `(.venv)` indicando que o ambiente está ativo.

---

## 💻 Instalação do Visual Studio Code

O Visual Studio Code (VS Code) é o editor recomendado para desenvolvimento neste treinamento.

### 🔽 1. Instalar VS Code

- **Mac**:  
  Baixe e instale: [VS Code para Mac](https://code.visualstudio.com/download)

- **Windows**:  
  Baixe e instale: [VS Code para Windows](https://code.visualstudio.com/download)

### 🧩 2. Extensões recomendadas

Após instalar o VS Code, abra o editor e instale as seguintes extensões para uma melhor experiência:

- **Python** (Microsoft)
- **Docker** (Microsoft)
- **AWS Toolkit** (Amazon Web Services)
- **DBT** (se disponível)
- **GitHub Copilot** (opcional)

Para instalar extensões, pressione `Ctrl+Shift+X` (Windows/Linux) ou `Cmd+Shift+X` (Mac) e busque pelo nome da extensão.

---

## ☁️ Configuração da AWS CLI e Perfil `mobiis`

### 🔧 1. Instalar AWS CLI

- **Mac** (via Homebrew):
  ```bash
  brew install awscli
  ```
  - Alternativamente, baixe o instalador: [Instalador AWS CLI para Mac](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2-mac.html)

- **Windows**:
  - Baixe: [Instalador AWS CLI v2 para Windows](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2-windows.html)

### 🧾 2. Configurar Perfil `mobiis`

Execute o seguinte comando:

```bash
aws configure --profile mobiis
```

Informe:
- Access Key  
- Secret Key  
- Região padrão: `us-east-2`  
- Formato de saída: `json`

> Para acesso direto ao console AWS no navegador:  
> [https://381491981944.signin.aws.amazon.com/console](https://381491981944.signin.aws.amazon.com/console)

---

## 🐳 Instalação do Docker e Docker Compose

### 📦 1. Instalar Docker Desktop

- **Mac**:  
  Baixe e instale: [Docker Desktop for Mac](https://www.docker.com/products/docker-desktop/)

- **Windows**:  
  Baixe: [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/)  
  > **Importante**: habilite o suporte ao **WSL2** durante a instalação.

### 🔍 2. Verificar Docker Compose

Docker Desktop já inclui o **Docker Compose (v2+)**. Para verificar:

```bash
docker compose version
```

> Caso deseje atualizar ou instalar separadamente: [Documentação oficial do Docker Compose](https://docs.docker.com/compose/install/)

---

## 📊 Instalação do DBT (Athena Adapter)

### 📌 1. Ativar o ambiente virtual (se ainda não ativado)

```bash
source .venv/bin/activate  # Mac/Linux
.venv\Scripts\activate   # Windows
```

### 📥 2. Instalar DBT com adaptador para Athena

```bash
pip install dbt-athena-community
```

### ✅ 3. Verificar instalação

```bash
dbt --version
```

> Para uso avançado, veja a [Documentação Oficial do DBT](https://docs.getdbt.com/)

---

### 🌐 Definição de Variáveis de Ambiente

Para garantir que o perfil AWS seja utilizado corretamente, defina as variáveis de ambiente:

- **Mac/Linux:**
  ```bash
  export AWS_PROFILE=mobiis
  export AWS_DEFAULT_REGION=us-east-2
  ```
- **Windows (PowerShell)**:
  ```powershell
  $env:AWS_PROFILE="mobiis"
  $env:AWS_DEFAULT_REGION="us-east-2"
  ```

---

## ✅ Comandos para Validação

Após concluir as instalações, execute os comandos abaixo para validar:

```bash
# Verificar Python
python --version         # ou python3 --version (Mac)

# Verificar AWS CLI
aws --version

# Verificar Docker
docker --version
docker compose version

# Verificar DBT
dbt --version

# Testar credenciais AWS
aws s3 ls
```

Se ocorrer algum erro, revise os passos ou consulte as documentações indicadas abaixo.

---

## 🔗 Referências e Links Úteis

| Ferramenta     | Link Oficial                                               |
|----------------|------------------------------------------------------------|
| Python         | [https://www.python.org](https://www.python.org)           |
| AWS CLI        | [https://aws.amazon.com/cli/](https://aws.amazon.com/cli/) |
| Docker         | [https://www.docker.com](https://www.docker.com)           |
| DBT            | [https://docs.getdbt.com](https://docs.getdbt.com)         |
| VS Code        | [https://code.visualstudio.com](https://code.visualstudio.com) |

---

Você está agora com um ambiente completo e funcional para realizar atividades de engenharia de dados com Python 3.11.6, AWS CLI, Docker, DBT, Visual Studio Code e o adaptador para Athena.
