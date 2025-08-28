# ReportWell API

A Django-based REST API backend service with WebSocket support for real-time communication.

## Features

- Django REST Framework for API endpoints
- WebSocket support using Django Channels
- PostgreSQL database
- Docker containerization
- JWT authentication
- Redis for caching and WebSocket support
- [Django Tasks for background tasks](https://github.com/RealOrangeOne/django-tasks)
- **LocalStack integration** for local AWS service emulation

## Prerequisites

- Python 3.x
- Docker and Docker Compose
- PostgreSQL (if running locally)
- Redis (if running locally)

## Quick Start

### 1. Set up environment variables

**For LocalStack (Recommended for Development):**

```bash
cp env.localstack .env
```

**For Real AWS:**

```bash
cp env.aws .env
# Edit .env and fill in your AWS credentials
```

### 2. Start the application

```bash
docker-compose up --build
```

This will start:

- Django web application
- PostgreSQL database
- Redis
- LocalStack (AWS services emulator)

### 3. Access the application

- **Django**: http://localhost:8000
- **LocalStack**: http://localhost:4566
- **Health Check**: http://localhost:8000/health/

## LocalStack Integration

This project automatically detects whether AWS credentials are available:

- **With AWS credentials**: Uses real AWS services
- **Without AWS credentials**: Automatically switches to LocalStack

LocalStack provides mock AWS services locally:

- **S3**: File storage and presigned URLs
- **DynamoDB**: NoSQL database for notifications

## Development

- The project uses Black for code formatting
- isort for keeping dependencies clean
- Flake8 for linting
- Pre-commit hooks for code quality checks

## Restoring the PostgreSQL Database from a .sql Dump

This section provides step-by-step instructions for restoring your PostgreSQL database from a `.sql` dump file using Docker and Django. This is useful if you need to reset your development environment or migrate data.

#### 1. Copy the SQL Dump File into the PostgreSQL Container

Replace `EXAMPLE_SQL_DUMP.sql` with your actual file name if different.

```bash
docker cp ~/Downloads/EXAMPLE_SQL_DUMP.sql reportwell-api-db-1:/tmp/EXAMPLE_SQL_DUMP.sql
```

#### 2. Run Django Migrations to Create the Schema

```bash
python manage.py migrate
```

#### 3. Temporarily Disable Foreign Key Constraints and Restore the Data

```bash
docker exec rw-django-backend-db-1 pg_restore -U postgres -d reportwelldb /tmp/reportwell.sql
```

#### 4. Re-enable Foreign Key Constraints

```bash
docker exec reportwell-api-db-1 psql -U postgres -d reportwelldb -c "SET session_replication_role = 'origin';"
```

### Notes

- Make sure your Docker container name (`reportwell-api-db-1`) matches your running container.
- If your SQL dump includes schema (CREATE TABLE statements), you may not need to run migrations before restoring.
- If you encounter errors, check the order of these steps and ensure your dump file is compatible with your database schema.
