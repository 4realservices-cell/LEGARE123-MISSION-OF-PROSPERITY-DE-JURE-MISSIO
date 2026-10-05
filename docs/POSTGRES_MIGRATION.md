# Database migration to PostgreSQL
## Prerequisites
- PostgreSQL 13+
- psycopg2-binary installed (included in requirements.txt)

## Migration Steps

### 1. Set up PostgreSQL
```bash
docker run -d \
  --name legare-db \
  -e POSTGRES_DB=legare \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  postgres:16-alpine
```

### 2. Update .env
```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/legare
```

### 3. Run Alembic migrations
```bash
alembic upgrade head
```

### 4. Verify connection
The app will automatically create tables on startup if they don't exist.

## Rolling back
```bash
alembic downgrade base
```
