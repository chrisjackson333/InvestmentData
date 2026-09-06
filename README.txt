Portfolio Project: Investment Data Platform & Trade Signals API
What it is

A Python microservices platform that ingests market/portfolio data, processes it with PySpark, stores outputs in DynamoDB/Postgres, and exposes trade-signal APIs via API Gateway + Lambda, deployed on EKS.
Tech stack (aligned to JD)

    Python + FastAPI
    AWS Glue + PySpark
    AWS EKS + Docker
    API Gateway + Lambda
    DynamoDB + PostgreSQL + S3
    Kafka
    GitHub Actions CI/CD
    Terraform (basic)
    pytest (TDD)

Components to build

    Data Ingestion Pipeline
        Pull/mock market ticks + portfolio positions into S3
        Run Glue PySpark jobs for cleaning/aggregation

    Signal Engine Service (FastAPI on EKS)
        Generate simple signals (momentum, volatility threshold, rebalance triggers)
        Persist fast lookup state in DynamoDB, relational history in PostgreSQL

    Trade Signal API Layer
        Expose read/write endpoints through API Gateway
        Use Lambda for lightweight orchestration/auth/request validation

    Event Streaming
        Publish/consume signal.created and portfolio.rebalanced events via Kafka

    Security + Reliability
        IAM least privilege, input validation, rate limiting, retries, DLQ
        Metrics/logging/tracing dashboards

    Dev Workflow
        TDD with pytest
        GitHub PR workflow + CI (tests, lint, build, deploy)
        Scrum-style board (JIRA-style backlog/sprints in project docs)
        Architecture + runbook docs (Confluence-style markdown docs)

Why this fits the role

It directly demonstrates nearly every requirement: Python services, Glue/PySpark pipelines, EKS deployment, API Gateway/Lambda patterns, DynamoDB/Postgres integration, Kafka messaging, CI/CD on GitHub, Terraform basics, security/scalability, and strong documentation.