from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db, SessionLocal, Base, engine
from app.database.seeder import seed_database
from app.models import (
    AgentRegistration,
    AgentUpdate,
    EvidenceItem,
    EvidenceUpdate,
    ClaimEvaluationRequest,
    ClaimEvaluationResponse,
    AgentStatus,
    EvidenceStatus,
    ClaimStatus,
    UserCreate,
    UserLogin,
    Token,
)
from app.services.agent_registry import AgentRegistryService
from app.services.evidence_service import EvidenceService
from app.services.claim_evaluation import ClaimEvaluationService
from app.services.workflow_service import WorkflowService
from app.services.audit_service import audit_service
from app.services.user_service import UserService
from app.auth import authenticate_user, create_access_token, get_current_user, require_roles, get_password_hash

app = FastAPI(
    title=settings.app_name,
    description="A human-in-the-loop multi-agent evidence orchestration framework based on 'Proof Before Claim'.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)


@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    try:
        from app.database import AgentDB
        existing_agents = db.query(AgentDB).count()
        if existing_agents == 0:
            seed_database(db)
            print("Database seeded with sample data.")
    finally:
        db.close()


@app.get("/health")
def health_check():
    return {"status": "healthy", "environment": settings.environment, "service": settings.app_name}


@app.get("/readiness")
def readiness_check():
    return {"status": "ready", "service": settings.app_name}


@app.get("/admin")
def admin_dashboard():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>LEGARE123 - Admin Dashboard</title>
        <style>
            * { box-sizing: border-box; }
            body { font-family: Arial, sans-serif; background: #101828; color: #e5e7eb; margin: 0; }
            .container { max-width: 1200px; margin: 0 auto; padding: 30px 20px; }
            .header { background: linear-gradient(135deg, #0f172a, #111827); padding: 20px 0; border-bottom: 1px solid #334155; }
            .title { font-size: 2rem; font-weight: bold; }
            .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; margin-top: 20px; }
            .card { background: #111827; border: 1px solid #334155; border-radius: 12px; padding: 20px; }
            .metric { font-size: 2rem; font-weight: bold; color: #60a5fa; }
            .section { margin-top: 30px; }
            table { width: 100%; border-collapse: collapse; margin-top: 15px; }
            th, td { border-bottom: 1px solid #334155; padding: 8px 10px; text-align: left; }
            .badge { padding: 4px 8px; border-radius: 999px; font-size: 12px; background: #1d4ed8; }
        </style>
    </head>
    <body>
      <div class="header">
        <div class="container">
          <div class="title">LEGARE123 - Mission of Prosperity</div>
          <div>Proof Before Claim Admin Dashboard</div>
        </div>
      </div>
      <div class="container">
        <div class="grid">
          <div class="card"><div class="metric" id="agents">0</div><div>Active Agents</div></div>
          <div class="card"><div class="metric" id="evidence">0</div><div>Evidence Items</div></div>
          <div class="card"><div class="metric" id="claims">0</div><div>Claims</div></div>
          <div class="card"><div class="metric" id="workflows">0</div><div>Workflows</div></div>
        </div>
        <div class="section">
          <h2>Agents</h2>
          <table id="agent-table"><thead><tr><th>ID</th><th>Name</th><th>Role</th><th>Status</th></tr></thead><tbody></tbody></table>
        </div>
      </div>
      <script>
        async function loadStats() {
          const [agentsRes, evidenceRes, claimsRes, workflowsRes] = await Promise.all([
            fetch('/api/v1/agents'),
            fetch('/api/v1/evidence'),
            fetch('/api/v1/claims'),
            fetch('/api/v1/workflows')
          ]);
          const agents = await agentsRes.json();
          const evidence = await evidenceRes.json();
          const claims = await claimsRes.json();
          const workflows = await workflowsRes.json();
          document.getElementById('agents').textContent = agents.length;
          document.getElementById('evidence').textContent = evidence.length;
          document.getElementById('claims').textContent = claims.length;
          document.getElementById('workflows').textContent = workflows.length;
          const rows = agents.map(a => `<tr><td>${a.agent_id}</td><td>${a.name}</td><td>${a.role}</td><td><span class="badge">${a.status}</span></td></tr>`).join('');
          document.querySelector('#agent-table tbody').innerHTML = rows;
        }
        loadStats();
      </script>
    </body>
    </html>
    """
    return html_content


@app.post(f"{settings.api_prefix}/auth/register", response_model=dict)
def register_user(user: UserCreate, db: Session = Depends(get_db), current_user=Depends(require_roles("admin"))):
    existing = db.query(UserDB).filter(UserDB.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    service = UserService(db)
    hashed_password = get_password_hash(user.password)
    created = service.create_user(user, hashed_password)
    return {"message": "User created successfully", "user": created.dict()}


@app.post(f"{settings.api_prefix}/auth/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token({"sub": user.username, "role": user.role.value})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get(f"{settings.api_prefix}/auth/me")
def read_users_me(current_user=Depends(get_current_user)):
    return {"username": current_user.username, "role": current_user.role.value}


@app.get(f"{settings.api_prefix}/audit")
def list_audit_logs(db: Session = Depends(get_db), current_user=Depends(require_roles("admin", "operator"))):
    return [entry.dict() for entry in audit_service.get_audit_logs(db)]


@app.post(f"{settings.api_prefix}/agents", response_model=AgentRegistration)
def register_agent(agent: AgentRegistration, db: Session = Depends(get_db), current_user=Depends(require_roles("admin", "operator"))):
    service = AgentRegistryService(db)
    audit_service.log_action(db, current_user.username, "register_agent", agent.agent_id, f"Registered agent {agent.name}")
    return service.register_agent(agent)


@app.get(f"{settings.api_prefix}/agents", response_model=list[AgentRegistration])
def list_agents(status: AgentStatus = None, db: Session = Depends(get_db), current_user=Depends(require_roles("admin", "operator", "viewer"))):
    service = AgentRegistryService(db)
    return service.list_agents(status)


@app.get(f"{settings.api_prefix}/agents/{{agent_id}}", response_model=AgentRegistration)
def get_agent(agent_id: str, db: Session = Depends(get_db), current_user=Depends(require_roles("admin", "operator", "viewer"))):
    service = AgentRegistryService(db)
    agent = service.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@app.patch(f"{settings.api_prefix}/agents/{{agent_id}}", response_model=AgentRegistration)
def update_agent(agent_id: str, update: AgentUpdate, db: Session = Depends(get_db), current_user=Depends(require_roles("admin", "operator"))):
    service = AgentRegistryService(db)
    agent = service.update_agent(agent_id, update)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    audit_service.log_action(db, current_user.username, "update_agent", agent_id, f"Updated agent {agent_id}")
    return agent


@app.post(f"{settings.api_prefix}/agents/{{agent_id}}/activate", response_model=AgentRegistration)
def activate_agent(agent_id: str, db: Session = Depends(get_db), current_user=Depends(require_roles("admin", "operator"))):
    service = AgentRegistryService(db)
    agent = service.activate_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    audit_service.log_action(db, current_user.username, "activate_agent", agent_id, f"Activated agent {agent_id}")
    return agent


@app.post(f"{settings.api_prefix}/agents/{{agent_id}}/pause", response_model=AgentRegistration)
def pause_agent(agent_id: str, db: Session = Depends(get_db), current_user=Depends(require_roles("admin", "operator"))):
    service = AgentRegistryService(db)
    agent = service.pause_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    audit_service.log_action(db, current_user.username, "pause_agent", agent_id, f"Paused agent {agent_id}")
    return agent


@app.post(f"{settings.api_prefix}/evidence", response_model=EvidenceItem)
def add_evidence(item: EvidenceItem, db: Session = Depends(get_db), current_user=Depends(require_roles("admin", "operator"))):
    service = EvidenceService(db)
    audit_service.log_action(db, current_user.username, "add_evidence", item.evidence_id, item.content)
    return service.add_evidence(item)


@app.get(f"{settings.api_prefix}/evidence", response_model=list[EvidenceItem])
def list_evidence(status: EvidenceStatus = None, db: Session = Depends(get_db), current_user=Depends(require_roles("admin", "operator", "viewer"))):
    service = EvidenceService(db)
    return service.list_evidence(status)


@app.get(f"{settings.api_prefix}/evidence/{{evidence_id}}", response_model=EvidenceItem)
def get_evidence(evidence_id: str, db: Session = Depends(get_db), current_user=Depends(require_roles("admin", "operator", "viewer"))):
    service = EvidenceService(db)
    evidence = service.get_evidence(evidence_id)
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
    return evidence


@app.post(f"{settings.api_prefix}/evidence/{{evidence_id}}/verify")
def verify_evidence(evidence_id: str, verified_by: str, db: Session = Depends(get_db), current_user=Depends(require_roles("admin", "operator"))):
    service = EvidenceService(db)
    if not service.verify_evidence(evidence_id, verified_by):
        raise HTTPException(status_code=404, detail="Evidence not found")
    audit_service.log_action(db, current_user.username, "verify_evidence", evidence_id, f"Verified evidence {evidence_id} by {verified_by}")
    return {"status": "verified", "evidence_id": evidence_id}


@app.post(f"{settings.api_prefix}/evidence/{{evidence_id}}/reject")
def reject_evidence(evidence_id: str, db: Session = Depends(get_db), current_user=Depends(require_roles("admin", "operator"))):
    service = EvidenceService(db)
    if not service.reject_evidence(evidence_id):
        raise HTTPException(status_code=404, detail="Evidence not found")
    audit_service.log_action(db, current_user.username, "reject_evidence", evidence_id, f"Rejected evidence {evidence_id}")
    return {"status": "rejected", "evidence_id": evidence_id}


@app.patch(f"{settings.api_prefix}/evidence/{{evidence_id}}", response_model=EvidenceItem)
def update_evidence(evidence_id: str, update: EvidenceUpdate, db: Session = Depends(get_db), current_user=Depends(require_roles("admin", "operator"))):
    service = EvidenceService(db)
    evidence = service.update_evidence(evidence_id, update)
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
    audit_service.log_action(db, current_user.username, "update_evidence", evidence_id, f"Updated evidence {evidence_id}")
    return evidence


@app.post(f"{settings.api_prefix}/claims/evaluate", response_model=ClaimEvaluationResponse)
def evaluate_claim(req: ClaimEvaluationRequest, evaluator_id: str = None, db: Session = Depends(get_db), current_user=Depends(require_roles("admin", "operator"))):
    service = ClaimEvaluationService(db)
    response = service.evaluate_claim(req, evaluator_id or current_user.username)
    audit_service.log_action(db, current_user.username, "evaluate_claim", req.claim_id, response.reason)
    audit_service.log_claim_timeline(db, req.claim_id, current_user.username, "evaluate_claim", response.reason)
    return response


@app.get(f"{settings.api_prefix}/claims/{{claim_id}}")
def get_claim(claim_id: str, db: Session = Depends(get_db), current_user=Depends(require_roles("admin", "operator", "viewer"))):
    service = ClaimEvaluationService(db)
    claim = service.get_claim(claim_id)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    return claim


@app.get(f"{settings.api_prefix}/claims", response_model=list[dict])
def list_claims(status: ClaimStatus = None, db: Session = Depends(get_db), current_user=Depends(require_roles("admin", "operator", "viewer"))):
    service = ClaimEvaluationService(db)
    return service.list_claims(status)


@app.get(f"{settings.api_prefix}/claims/{{claim_id}}/timeline")
def claim_timeline(claim_id: str, db: Session = Depends(get_db), current_user=Depends(require_roles("admin", "operator", "viewer"))):
    events = audit_service.get_claim_timeline(db, claim_id)
    return [{
        "id": event.id,
        "claim_id": event.claim_id,
        "action": event.action,
        "actor": event.actor,
        "details": event.details,
        "created_at": event.created_at.isoformat(),
    } for event in events]


@app.post(f"{settings.api_prefix}/claims/{{claim_id}}/archive")
def archive_claim(claim_id: str, db: Session = Depends(get_db), current_user=Depends(require_roles("admin", "operator"))):
    service = ClaimEvaluationService(db)
    if not service.archive_claim(claim_id):
        raise HTTPException(status_code=404, detail="Claim not found")
    audit_service.log_action(db, current_user.username, "archive_claim", claim_id, f"Archived claim {claim_id}")
    return {"status": "archived", "claim_id": claim_id}


@app.get(f"{settings.api_prefix}/workflows")
def list_workflows(db: Session = Depends(get_db), current_user=Depends(require_roles("admin", "operator", "viewer"))):
    service = WorkflowService(db)
    return service.list_workflows()


@app.get(f"{settings.api_prefix}/workflows/{{workflow_id}}")
def get_workflow(workflow_id: str, db: Session = Depends(get_db), current_user=Depends(require_roles("admin", "operator", "viewer"))):
    service = WorkflowService(db)
    workflow = service.get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow
