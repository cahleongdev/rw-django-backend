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

## Prerequisites

- Python 3.x
- Docker and Docker Compose
- PostgreSQL (if running locally)
- Redis (if running locally)

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd reportwell-api
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set up environment variables:
   Create a `.env` file in the root directory based on the `.env.example` file.

## Running the Application

1. Start the development server:

```bash
$ docker compose up -d
$ python manage.py rqworker --job-class django_tasks.backends.rq.Job --with-scheduler &
$ python manage.py runserver
```

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
