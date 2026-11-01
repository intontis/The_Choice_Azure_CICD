
# The Choice — Azure CI/CD

An interactive, branching-choice web application built with Python, Flask and PostgreSQL, developed as a hands-on Azure DevOps and GitOps portfolio project.

## Overview

The Choice presents visitors with a sequence of decisions. Each answer determines the next question, and the completed answer path determines the prophecy revealed at the end of the journey.

The application uses anonymous visitor sessions and stores questions, options, journeys, responses and prophecy mappings in PostgreSQL.

## Features

- Branching question-and-answer journeys.
- Anonymous visitor sessions.
- PostgreSQL persistence for questions, options and responses.
- Path-based prophecy selection.
- Flask application using the application factory pattern.
- Matrix-inspired animated background using JavaScript Canvas.
- Automated tests using pytest.

## Technology Stack

| Area | Technology |
|---|---|
| Backend | Python, Flask |
| Database | PostgreSQL |
| Database driver | Psycopg 3 |
| Frontend | HTML, CSS, JavaScript |
| Testing | pytest |
| Version control | Git, GitHub |
| CI/CD (in development) | Azure Pipelines |
| Container registry (planned) | Azure Container Registry |
| Deployment (planned) | Kubernetes, AKS, Argo CD |

## Project Structure

```text
The_Choice_Azure_CICD/
│
├── app/
│   ├── routes/
│   ├── services/
│   ├── static/
│   ├── templates/
│   ├── __init__.py
│   └── db.py
│
├── db/
│   ├── schema.sql
│   └── seed.py
│
├── tests/
│
├── .gitignore
├── Architecture.md
├── Questions.md
├── requirements.txt
├── requirements-dev.txt
└── run.py
```

## Local Development

### Prerequisites

- Python 3.12
- PostgreSQL 16
- Git

### 1. Clone the repository

```bash
git clone https://github.com/intontis/The_Choice_Azure_CICD.git
cd The_Choice_Azure_CICD
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements-dev.txt
```

### 4. Configure environment variables

Create a local `.env` file in the project root:

```env
FLASK_SECRET_KEY=replace_with_a_secure_random_value

DB_HOST=127.0.0.1
DB_PORT=5432
DB_NAME=the_choice
DB_USER=the_choice_app
DB_PASSWORD=your_local_database_password
```

Never commit `.env` or other credentials to GitHub.

### 5. Initialize the database

After creating the PostgreSQL database and application user, apply the schema:

```bash
psql -h 127.0.0.1 -U the_choice_app -d the_choice -f db/schema.sql
```

Populate the database using the seed script:

```bash
export PGHOST=127.0.0.1
export PGPORT=5432
export PGDATABASE=the_choice
export PGUSER=the_choice_app

read -rsp "PostgreSQL password: " PGPASSWORD
echo
export PGPASSWORD

python db/seed.py

unset PGPASSWORD
```

### 6. Run the application

```bash
python run.py
```

Open the application at:

http://127.0.0.1:5000

## Running Tests

Run the test suite from the project root:

```bash
python -m pytest -q
```

The database connection integration test requires PostgreSQL to be available with the expected test database credentials.

## CI/CD and Deployment Roadmap

The project is being developed in stages:

1. **Azure Pipelines:** Automate dependency installation and pytest execution on GitHub changes.
2. **Azure Container Registry:** Build and publish application container images.
3. **GitOps:** Maintain Kubernetes deployment configuration in GitHub.
4. **Argo CD:** Synchronize Git configuration with the AKS cluster.
5. **Azure Kubernetes Service:** Run the containerized application.

The CI/CD and Kubernetes deployment stages are planned as part of the ongoing project.