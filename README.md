\# 📌 Collaborative Kanban Board Backend



Backend assíncrono para um sistema de gerenciamento de tarefas em estilo Kanban colaborativo. Desenvolvido com \*\*FastAPI\*\*, \*\*PostgreSQL\*\*, \*\*Redis\*\* e totalmente containerizado com \*\*Docker Compose\*\*.



\## 🚀 Tecnologias Utilizadas



\* \*\*Python 3.11\*\* / \*\*FastAPI\*\*: Criação da API RESTful assíncrona e WebSockets.

\* \*\*PostgreSQL\*\*: Banco de dados relacional para persistência dos quadros, cartões e usuários.

\* \*\*SQLAlchemy\*\*: ORM para modelagem e manipulação dos dados.

\* \*\*Redis\*\*: Cache de dados e Pub/Sub para notificações em tempo real.

\* \*\*JWT (JSON Web Tokens)\*\*: Autenticação e autorização seguras.

\* \*\*Docker \& Docker Compose\*\*: Gerenciamento de containers e ambiente de desenvolvimento isolado.



\## 🛠️ Arquitetura de Portas



Devido a possíveis conflitos em portas locais padrão, o ambiente Docker foi mapeado nas seguintes portas:



| Serviço | Porta Interna (Container) | Porta Externa (Host) |

| :--- | :--- | :--- |

| \*\*Backend (FastAPI)\*\* | 8000 | \*\*8002\*\* |

| \*\*PostgreSQL\*\* | 5432 | \*\*5434\*\* |

| \*\*Redis\*\* | 6379 | \*\*6380\*\* |



\---



\## 📋 Pré-requisitos



\* \[Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado e rodando.

\* \[Git](https://git-scm.com/) instalado.



\---



\## 🔧 Como Executar o Projeto



1\. \*\*Clone o repositório:\*\*

&#x20;  ```bash

&#x20;  git clone \[https://github.com/seu-usuario/kanban-colaborativo.git](https://github.com/seu-usuario/kanban-colaborativo.git)

&#x20;  cd kanban-colaborativo

