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
import React, { useState, useEffect } from 'react';
import axios from 'axios';

export default function SentinelDashboard() {
  const [biometrics, setBiometrics] = useState([]);
  const [anchors, setAnchors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [wsConnected, setWsConnected] = useState(false);
  const [error, setError] = useState(null);

  const API_BASE = process.env.REACT_APP_API_URL || "http://localhost:8000/api/v1/sentinel";
  const WS_URL = process.env.REACT_APP_WS_URL || "ws://localhost:8000/api/v1/sentinel/ws";

  // Initial REST fetch for data hydration
  useEffect(() => {
    async function hydrateData() {
      try {
        setLoading(true);
        const [bioRes, anchorRes] = await Promise.all([
          axios.get(`${API_BASE}/biometrics/streams`),
          axios.get(`${API_BASE}/spatial-xr/anchors`)
        ]);
        setBiometrics(bioRes.data);
        setAnchors(anchorRes.data);
        setError(null);
      } catch (err) {
        setError("Failed to synchronize initial telemetry feeds via REST.");
      } finally {
        setLoading(false);
      }
    }

    hydrateData();
  }, [API_BASE]);

  // WebSocket connection for real-time telemetry streaming
  useEffect(() => {
    let socket;
    let reconnectTimer;

    function connectWebSocket() {
      socket = new WebSocket(WS_URL);

      socket.onopen = () => {
        setWsConnected(true);
      };

      socket.onmessage = (event) => {
        try {
          const packet = JSON.parse(event.data);
          if (packet.type === 'BIOMETRIC_UPDATE') {
            setBiometrics((prev) => [packet.data, ...prev.slice(0, 49)]);
          } else if (packet.type === 'ANCHOR_UPDATE') {
            setAnchors((prev) => [packet.data, ...prev.slice(0, 49)]);
          }
        } catch (e) {
          console.error("Malformed telemetry packet received:", e);
        }
      };

      socket.onerror = () => {
        setWsConnected(false);
      };

      socket.onclose = () => {
        setWsConnected(false);
        // Attempt reconnection after 5 seconds
        reconnectTimer = setTimeout(connectWebSocket, 5000);
      };
    }

    connectWebSocket();

    return () => {
      if (socket) socket.close();
      if (reconnectTimer) clearTimeout(reconnectTimer);
    };
  }, [WS_URL]);

  if (loading && biometrics.length === 0) {
    return (
      <div className="flex h-screen items-center justify-center bg-slate-950 text-cyan-400 font-mono">
        Initializing Sentinel Telemetry Matrix...
      </div>
    );
  }

  return (
    <div className="p-6 bg-slate-950 text-slate-100 min-h-screen">
      {/* Header with Live Status Indicator */}
      <header className="mb-8 border-b border-slate-800 pb-4 flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold tracking-wider text-cyan-400">SENTINEL ECOSYSTEM v1.2.0</h1>
          <p className="text-sm text-slate-400">Proof Before Claim — Real-Time Command & Telemetry Matrix</p>
        </div>
        <div className="flex items-center space-x-2 bg-slate-900 px-3 py-1.5 rounded-full border border-slate-800">
          <span className={`h-2.5 w-2.5 rounded-full animate-pulse ${wsConnected ? 'bg-emerald-400' : 'bg-amber-400'}`} />
          <span className="text-xs font-mono text-slate-300">
            {wsConnected ? 'WS Stream Active' : 'Polling / Reconnecting'}
          </span>
        </div>
      </header>

      {error && (
        <div className="mb-6 p-4 bg-red-950/50 border border-red-800 text-red-300 rounded-lg text-sm">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Biometric Telemetry Panel */}
        <section className="bg-slate-900 border border-slate-800 rounded-lg p-5 shadow-xl">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-semibold text-emerald-400">Biometric Telemetry Streams</h2>
            <span className="text-xs font-mono bg-emerald-950 text-emerald-300 px-2.5 py-1 rounded border border-emerald-800">
              {biometrics.length} Records
            </span>
          </div>
          <div className="space-y-3 max-h-[500px] overflow-y-auto pr-1">
            {biometrics.length === 0 ? (
              <p className="text-sm text-slate-500 text-center py-8">No biometric streams recorded yet.</p>
            ) : (
              biometrics.map((item) => (
                <div key={item.telemetry_id} className="p-3.5 bg-slate-950 rounded-md border border-slate-800 flex justify-between items-center transition hover:border-slate-700">
                  <div>
                    <p className="font-mono text-xs text-cyan-300">{item.telemetry_id}</p>
                    <p className="text-xs text-slate-400 mt-0.5">Agent: {item.agent_id}</p>
                  </div>
                  <div className="text-right">
                    <span className={`text-xs px-2.5 py-1 rounded font-mono ${item.verified ? 'bg-emerald-950 text-emerald-300 border border-emerald-800' : 'bg-amber-950 text-amber-300 border border-amber-800'}`}>
                      Score: {Number(item.trust_score).toFixed(2)}
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
        </section>

        {/* Spatial XR Anchors Panel */}
        <section className="bg-slate-900 border border-slate-800 rounded-lg p-5 shadow-xl">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-semibold text-purple-400">Spatial XR Anchors</h2>
            <span className="text-xs font-mono bg-purple-950 text-purple-300 px-2.5 py-1 rounded border border-purple-800">
              {anchors.length} Anchors
            </span>
          </div>
          <div className="space-y-3 max-h-[500px] overflow-y-auto pr-1">
            {anchors.length === 0 ? (
              <p className="text-sm text-slate-500 text-center py-8">No spatial anchors detected.</p>
            ) : (
              anchors.map((anchor) => (
                <div key={anchor.anchor_id} className="p-3.5 bg-slate-950 rounded-md border border-slate-800 flex justify-between items-center transition hover:border-slate-700">
                  <div>
                    <p className="font-mono text-xs text-purple-300">{anchor.anchor_id}</p>
                    <p className="text-xs text-slate-400 mt-0.5">Session: {anchor.session_id}</p>
                  </div>
                  <div className="text-right font-mono text-xs text-slate-300 bg-slate-900 px-2 py-1 rounded border border-slate-800">
                    X: {anchor.coordinate_vector?.x ?? 0} | Y: {anchor.coordinate_vector?.y ?? 0} | Z: {anchor.coordinate_vector?.z ?? 0}
                  </div>
                </div>
              ))
            )}
          </div>
        </section>
      </div>
    </div>
  );
}
