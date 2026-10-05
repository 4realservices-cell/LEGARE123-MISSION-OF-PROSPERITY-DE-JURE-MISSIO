# LEGARE123 Mission of Prosperity - Complete Enterprise Edition

A production-ready, full-stack Python + React framework for human-in-the-loop evidence orchestration and claim validation, built on the principle of **"Proof Before Claim."**

## 🚀 Complete Feature Set

### Backend (Python/FastAPI)
- ✅ **JWT Authentication** - Secure token-based auth with bcrypt password hashing
- ✅ **Role-Based Access Control (RBAC)** - Admin, Operator, Viewer roles with fine-grained permissions
- ✅ **Audit Logging** - Immutable audit trail for compliance and security
- ✅ **Claim Timeline** - Complete event history for each claim
- ✅ **Evidence Management** - Verification pipeline with status tracking
- ✅ **Agent Lifecycle** - Registration, activation, pause, retirement
- ✅ **Workflow Engine** - Multi-step approval workflows
- ✅ **Database Agnostic** - SQLite for dev, PostgreSQL for production
- ✅ **API Documentation** - Auto-generated OpenAPI/Swagger docs

### Frontend (React + Vite)
- ✅ **Secure Login** - JWT token management and session persistence
- ✅ **Protected Routes** - Role-based access to UI components
- ✅ **Dashboard** - Real-time system overview and metrics
- ✅ **Claim Timeline UI** - Visual event history with actor tracking
- ✅ **Evidence Management** - Browse, filter, and manage evidence
- ✅ **Agent Management** - View and manage agent lifecycles
- ✅ **Permissions Panel** - Role and permission documentation
- ✅ **Responsive Design** - Works on desktop and mobile

### Database
- ✅ **SQLite** - Development (zero setup)
- ✅ **PostgreSQL** - Production (scalable)
- ✅ **Alembic Migrations** - Version-controlled schema changes
- ✅ **Audit Tables** - Immutable event logs
- ✅ **Claim Timeline Tables** - Event-sourced claim history

### Deployment
- ✅ **Docker Compose** - Local development with PostgreSQL
- ✅ **Dockerfile** - Container image for any cloud
- ✅ **Render Config** - One-click deploy to Render.com
- ✅ **Cloud Run Config** - GCP deployment manifest
- ✅ **Environment Config** - .env-based configuration

## 📋 Quick Start

### Backend Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API available at: http://localhost:8000
Docs: http://localhost:8000/docs

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

UI available at: http://localhost:5173

### With Docker Compose (PostgreSQL)
```bash
docker-compose up --build
```

API: http://localhost:8000
PostgreSQL: localhost:5432

## 🔐 Authentication & Authorization

### Default Seeded Users
- Admin: `admin` / `admin`
- Operator: `operator` / `operator`
- Viewer: `viewer` / `viewer`

### Login Flow
1. User submits username/password to `/api/v1/auth/token`
2. API validates credentials and returns JWT token
3. Frontend stores token in localStorage
4. All subsequent requests include token in `Authorization: Bearer <token>` header
5. Backend validates token and enforces role-based access

### Role Permissions

#### Admin
- Register new users
- Manage all agents, evidence, and claims
- Access audit logs
- Configure policies and permissions

#### Operator
- Register agents
- Submit and verify evidence
- Evaluate claims against evidence
- View audit logs for transparency

#### Viewer
- Read-only access to all resources
- Cannot create or modify anything
- Can view claim timelines and evidence trails

## 📊 Database Schema

### Users
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR UNIQUE NOT NULL,
    hashed_password VARCHAR NOT NULL,
    role ENUM('admin', 'operator', 'viewer'),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP
);
```

### Audit Logs
```sql
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    action VARCHAR NOT NULL,
    actor VARCHAR NOT NULL,
    target VARCHAR,
    details TEXT,
    timestamp TIMESTAMP
);
```

### Claim Audit Logs (Timeline)
```sql
CREATE TABLE claim_audit_logs (
    id SERIAL PRIMARY KEY,
    claim_id VARCHAR NOT NULL,
    action VARCHAR NOT NULL,
    actor VARCHAR NOT NULL,
    details TEXT,
    created_at TIMESTAMP
);
```

## 🔄 API Endpoints

### Authentication
- `POST /api/v1/auth/token` - Login (username/password)
- `POST /api/v1/auth/register` - Create new user (admin only)
- `GET /api/v1/auth/me` - Get current user info

### Agents
- `POST /api/v1/agents` - Register agent (admin/operator)
- `GET /api/v1/agents` - List agents (all)
- `GET /api/v1/agents/{id}` - Get agent (all)
- `PATCH /api/v1/agents/{id}` - Update agent (admin/operator)
- `POST /api/v1/agents/{id}/activate` - Activate agent (admin/operator)
- `POST /api/v1/agents/{id}/pause` - Pause agent (admin/operator)

### Evidence
- `POST /api/v1/evidence` - Submit evidence (admin/operator)
- `GET /api/v1/evidence` - List evidence (all)
- `GET /api/v1/evidence/{id}` - Get evidence (all)
- `POST /api/v1/evidence/{id}/verify` - Verify evidence (admin/operator)
- `POST /api/v1/evidence/{id}/reject` - Reject evidence (admin/operator)
- `PATCH /api/v1/evidence/{id}` - Update evidence (admin/operator)

### Claims
- `POST /api/v1/claims/evaluate` - Evaluate claim (admin/operator)
- `GET /api/v1/claims` - List claims (all)
- `GET /api/v1/claims/{id}` - Get claim (all)
- `GET /api/v1/claims/{id}/timeline` - Get claim timeline (all)
- `POST /api/v1/claims/{id}/archive` - Archive claim (admin/operator)

### Audit
- `GET /api/v1/audit` - List audit logs (admin/operator)

## 📈 Production Deployment

### Render.com
```bash
git push origin scaffold/core-framework
# Connect your Render account and deploy with render.yaml
```

### Google Cloud Run
```bash
docker build -t gcr.io/YOUR_PROJECT/legare123:latest .
docker push gcr.io/YOUR_PROJECT/legare123:latest
kubectl apply -f deployment/cloudrun.yaml
```

### Environment Variables
```
APP_NAME=LEGARE123
ENVIRONMENT=production
DATABASE_URL=postgresql://user:pass@host:5432/legare
JWT_SECRET=<generate-secure-key>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
CORS_ORIGINS=https://yourdomain.com
```

## 🧪 Testing

```bash
pytest tests/ -v
```

## 📚 Documentation

- [RBAC Guide](docs/RBAC_GUIDE.md) - Role-based access control and permissions
- [PostgreSQL Migration](docs/POSTGRES_MIGRATION.md) - Migrate from SQLite to PostgreSQL

## 📄 License

MIT

## 🤝 Contributing

Contributions welcome. Please ensure tests pass and follow the code style.
