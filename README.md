# Legare123 Mission of Prosperity - De Jure Mission API

A complete, production-ready Python framework for human-in-the-loop evidence orchestration and claim validation, built on the principle of **"Proof Before Claim."**

## Key Features

### 1. **SQLite Persistence**
- Full database persistence with SQLAlchemy ORM
- Automatic schema generation and seeding on startup
- Support for agents, evidence, claims, and workflows

### 2. **Agent Lifecycle Management**
- Register, activate, pause, and retire agents
- Agent capabilities tracking
- Role-based access control support
- Agent status transitions (registered → active → paused → retired)

### 3. **Evidence Verification Pipeline**
- Submit evidence with metadata (source, content, tags)
- Verify evidence through designated verifiers
- Track evidence lineage and verification chain
- Evidence status tracking (pending → verified → rejected → archived)

### 4. **Proof-Before-Claim Enforcement**
- Core validation logic that rejects unverified evidence
- Claims can only be approved if ALL required evidence is verified
- Claim status transitions (submitted → under_review → approved/rejected → archived)

### 5. **Admin Dashboard**
- Real-time web dashboard at `/admin`
- System overview with metrics
- Agent management interface
- Evidence and claim tracking
- Live data refresh every 30 seconds

### 6. **Workflow Management**
- Predefined workflow templates
- Multi-step claim approval workflows
- Emergency override workflows
- Extensible workflow engine

## Installation & Setup

```bash
# Clone the repo
git clone https://github.com/4realservices-cell/LEGARE123-MISSION-OF-PROSPERITY-DE-JURE-MISSIO.git
cd LEGARE123-MISSION-OF-PROSPERITY-DE-JURE-MISSIO

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Running Tests

```bash
pytest tests/ -v
```

## API Endpoints

### Health & Status
- `GET /health` - Health check
- `GET /readiness` - Readiness probe
- `GET /admin` - Admin dashboard (HTML)

### Agents
- `POST /api/v1/agents` - Register new agent
- `GET /api/v1/agents` - List all agents
- `GET /api/v1/agents/{agent_id}` - Get agent details
- `PATCH /api/v1/agents/{agent_id}` - Update agent
- `POST /api/v1/agents/{agent_id}/activate` - Activate agent
- `POST /api/v1/agents/{agent_id}/pause` - Pause agent

### Evidence
- `POST /api/v1/evidence` - Submit evidence
- `GET /api/v1/evidence` - List all evidence
- `GET /api/v1/evidence/{evidence_id}` - Get evidence details
- `POST /api/v1/evidence/{evidence_id}/verify` - Verify evidence
- `POST /api/v1/evidence/{evidence_id}/reject` - Reject evidence
- `PATCH /api/v1/evidence/{evidence_id}` - Update evidence

### Claims (Proof Before Claim)
- `POST /api/v1/claims/evaluate` - Submit and evaluate claim
- `GET /api/v1/claims` - List all claims
- `GET /api/v1/claims/{claim_id}` - Get claim details
- `POST /api/v1/claims/{claim_id}/archive` - Archive claim

### Workflows
- `GET /api/v1/workflows` - List all workflows
- `GET /api/v1/workflows/{workflow_id}` - Get workflow details

## Example: Submit & Evaluate a Claim

```bash
# 1. View seeded evidence
curl http://localhost:8000/api/v1/evidence

# 2. Submit a claim with verified evidence (will be approved)
curl -X POST http://localhost:8000/api/v1/claims/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "claim_id": "claim-001",
    "statement": "System audit shows no critical defects.",
    "required_evidence_ids": ["ev-system-audit-001"],
    "submitted_by": "user-123"
  }'

# 3. Submit a claim with unverified evidence (will be rejected)
curl -X POST http://localhost:8000/api/v1/claims/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "claim_id": "claim-002",
    "statement": "System is secure.",
    "required_evidence_ids": ["ev-security-scan-001"],
    "submitted_by": "user-123"
  }'
```

## Database Schema

### Agents Table
- `agent_id` (PK): Unique identifier
- `name`, `role`, `status`, `description`
- `capabilities`: JSON array
- `created_at`, `updated_at`: Timestamps

### Evidence Table
- `evidence_id` (PK): Unique identifier
- `source`, `content`: Evidence data
- `verified`, `status`: Verification state
- `submitted_by`, `verified_by`: User references
- `tags`: JSON array for categorization
- `created_at`, `updated_at`: Timestamps

### Claims Table
- `claim_id` (PK): Unique identifier
- `statement`: Claim text
- `status`, `approved`: Claim state
- `reason`: Evaluation reason
- `required_evidence_ids`: JSON array
- `submitted_by`, `evaluated_by`: User references
- `created_at`, `evaluated_at`: Timestamps

### Workflows Table
- `workflow_id` (PK): Unique identifier
- `name`, `description`: Workflow metadata
- `steps`: JSON array of workflow steps
- `created_at`, `updated_at`: Timestamps

## Seeded Sample Data

The application automatically seeds with:
- **3 agents**: Sentinel Audit, Evidence Orchestrator, Human Oversight
- **3 evidence items**: System audit (verified), telemetry (verified), security scan (pending)
- **2 workflows**: Standard claim approval, emergency override

## Docker Deployment

```bash
# Build container
docker build -t legare123:latest .

# Run container
docker run -p 8000:8000 -e ENVIRONMENT=production legare123:latest
```

## License
MIT
