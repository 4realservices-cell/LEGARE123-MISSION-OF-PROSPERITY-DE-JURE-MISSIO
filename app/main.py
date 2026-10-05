from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db, engine, Base
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
)
from app.services.agent_registry import AgentRegistryService
from app.services.evidence_service import EvidenceService
from app.services.claim_evaluation import ClaimEvaluationService
from app.services.workflow_service import WorkflowService

app = FastAPI(
    title=settings.app_name,
    description="A human-in-the-loop multi-agent evidence orchestration framework based on 'Proof Before Claim'.",
    version="1.0.0",
)

# Create tables and seed data on startup
Base.metadata.create_all(bind=engine)
seed_session = None


@app.on_event("startup")
def startup_event():
    from app.database import SessionLocal
    global seed_session
    seed_session = SessionLocal()
    try:
        # Check if data already exists
        from app.database import AgentDB
        existing_agents = seed_session.query(AgentDB).count()
        if existing_agents == 0:
            seed_database(seed_session)
            print("Database seeded with sample data.")
    finally:
        if seed_session:
            seed_session.close()


# ============ Health & Status ============


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "environment": settings.environment,
        "service": settings.app_name,
    }


@app.get("/readiness")
def readiness_check():
    return {"status": "ready", "service": settings.app_name}


# ============ Admin Dashboard ============


@app.get("/admin")
def admin_dashboard():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>LEGARE123 - Admin Dashboard</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; color: #333; }
            header { background: #1a1a1a; color: #fff; padding: 20px 40px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
            .container { max-width: 1200px; margin: 0 auto; padding: 40px 20px; }
            .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 40px; }
            .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
            .card h3 { color: #1a1a1a; margin-bottom: 10px; }
            .card-value { font-size: 2em; font-weight: bold; color: #0066cc; }
            .card-label { font-size: 0.9em; color: #666; }
            .section { margin-bottom: 40px; }
            .section h2 { margin-bottom: 20px; color: #1a1a1a; border-bottom: 2px solid #0066cc; padding-bottom: 10px; }
            .table { width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
            .table th { background: #f5f5f5; padding: 12px; text-align: left; font-weight: 600; color: #333; }
            .table td { padding: 12px; border-top: 1px solid #eee; }
            .table tr:hover { background: #f9f9f9; }
            .status { padding: 4px 8px; border-radius: 4px; font-size: 0.85em; font-weight: 600; }
            .status.active { background: #d4edda; color: #155724; }
            .status.verified { background: #d4edda; color: #155724; }
            .status.pending { background: #fff3cd; color: #856404; }
            .status.approved { background: #d1ecf1; color: #0c5460; }
            .btn { display: inline-block; padding: 10px 20px; background: #0066cc; color: white; border: none; border-radius: 4px; cursor: pointer; text-decoration: none; margin-right: 10px; }
            .btn:hover { background: #0052a3; }
        </style>
    </head>
    <body>
        <header>
            <h1>LEGARE123 - Mission of Prosperity</h1>
            <p>Proof Before Claim - Admin Dashboard</p>
        </header>
        <div class="container">
            <div class="section">
                <h2>System Overview</h2>
                <div class="grid">
                    <div class="card">
                        <div class="card-value" id="agent-count">-</div>
                        <div class="card-label">Active Agents</div>
                    </div>
                    <div class="card">
                        <div class="card-value" id="evidence-count">-</div>
                        <div class="card-label">Evidence Items</div>
                    </div>
                    <div class="card">
                        <div class="card-value" id="claim-count">-</div>
                        <div class="card-label">Claims Processed</div>
                    </div>
                    <div class="card">
                        <div class="card-value" id="workflow-count">-</div>
                        <div class="card-label">Workflows</div>
                    </div>
                </div>
            </div>
            <div class="section">
                <h2>Agents</h2>
                <table class="table" id="agents-table">
                    <thead>
                        <tr>
                            <th>Agent ID</th>
                            <th>Name</th>
                            <th>Role</th>
                            <th>Status</th>
                            <th>Capabilities</th>
                        </tr>
                    </thead>
                    <tbody></tbody>
                </table>
            </div>
            <div class="section">
                <h2>Recent Evidence</h2>
                <table class="table" id="evidence-table">
                    <thead>
                        <tr>
                            <th>Evidence ID</th>
                            <th>Source</th>
                            <th>Status</th>
                            <th>Verified By</th>
                            <th>Tags</th>
                        </tr>
                    </thead>
                    <tbody></tbody>
                </table>
            </div>
            <div class="section">
                <h2>Recent Claims</h2>
                <table class="table" id="claims-table">
                    <thead>
                        <tr>
                            <th>Claim ID</th>
                            <th>Statement</th>
                            <th>Status</th>
                            <th>Approved</th>
                        </tr>
                    </thead>
                    <tbody></tbody>
                </table>
            </div>
        </div>
        <script>
            async function loadDashboard() {
                try {
                    const agentsRes = await fetch('/api/v1/agents');
                    const agents = await agentsRes.json();
                    document.getElementById('agent-count').textContent = agents.filter(a => a.status === 'active').length;
                    const agentsBody = document.querySelector('#agents-table tbody');
                    agents.slice(0, 5).forEach(agent => {
                        const row = agentsBody.insertRow();
                        row.innerHTML = `
                            <td>${agent.agent_id}</td>
                            <td>${agent.name}</td>
                            <td>${agent.role}</td>
                            <td><span class="status ${agent.status}">${agent.status}</span></td>
                            <td>${(agent.capabilities || []).join(', ')}</td>
                        `;
                    });
                } catch (e) { console.error('Error loading agents:', e); }
                
                try {
                    const evidenceRes = await fetch('/api/v1/evidence');
                    const evidence = await evidenceRes.json();
                    document.getElementById('evidence-count').textContent = evidence.length;
                    const evidenceBody = document.querySelector('#evidence-table tbody');
                    evidence.slice(0, 5).forEach(item => {
                        const row = evidenceBody.insertRow();
                        row.innerHTML = `
                            <td>${item.evidence_id}</td>
                            <td>${item.source}</td>
                            <td><span class="status ${item.status}">${item.status}</span></td>
                            <td>${item.verified_by || 'N/A'}</td>
                            <td>${(item.tags || []).join(', ')}</td>
                        `;
                    });
                } catch (e) { console.error('Error loading evidence:', e); }
                
                try {
                    const claimsRes = await fetch('/api/v1/claims');
                    const claims = await claimsRes.json();
                    document.getElementById('claim-count').textContent = claims.length;
                    const claimsBody = document.querySelector('#claims-table tbody');
                    claims.slice(0, 5).forEach(claim => {
                        const row = claimsBody.insertRow();
                        row.innerHTML = `
                            <td>${claim.claim_id}</td>
                            <td>${claim.statement.substring(0, 50)}...</td>
                            <td><span class="status ${claim.status}">${claim.status}</span></td>
                            <td>${claim.approved ? '✓ Yes' : '✗ No'}</td>
                        `;
                    });
                } catch (e) { console.error('Error loading claims:', e); }
                
                try {
                    const workflowsRes = await fetch('/api/v1/workflows');
                    const workflows = await workflowsRes.json();
                    document.getElementById('workflow-count').textContent = workflows.length;
                } catch (e) { console.error('Error loading workflows:', e); }
            }
            
            loadDashboard();
            setInterval(loadDashboard, 30000);
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


# ============ Agent Management ============


@app.post(f"{settings.api_prefix}/agents", response_model=AgentRegistration)
def register_agent(agent: AgentRegistration, db: Session = Depends(get_db)):
    service = AgentRegistryService(db)
    return service.register_agent(agent)


@app.get(f"{settings.api_prefix}/agents", response_model=list[AgentRegistration])
def list_agents(status: AgentStatus = None, db: Session = Depends(get_db)):
    service = AgentRegistryService(db)
    return service.list_agents(status)


@app.get(f"{settings.api_prefix}/agents/{{agent_id}}", response_model=AgentRegistration)
def get_agent(agent_id: str, db: Session = Depends(get_db)):
    service = AgentRegistryService(db)
    agent = service.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@app.patch(f"{settings.api_prefix}/agents/{{agent_id}}", response_model=AgentRegistration)
def update_agent(agent_id: str, update: AgentUpdate, db: Session = Depends(get_db)):
    service = AgentRegistryService(db)
    agent = service.update_agent(agent_id, update)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@app.post(f"{settings.api_prefix}/agents/{{agent_id}}/activate", response_model=AgentRegistration)
def activate_agent(agent_id: str, db: Session = Depends(get_db)):
    service = AgentRegistryService(db)
    agent = service.activate_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@app.post(f"{settings.api_prefix}/agents/{{agent_id}}/pause", response_model=AgentRegistration)
def pause_agent(agent_id: str, db: Session = Depends(get_db)):
    service = AgentRegistryService(db)
    agent = service.pause_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


# ============ Evidence Management ============


@app.post(f"{settings.api_prefix}/evidence", response_model=EvidenceItem)
def add_evidence(item: EvidenceItem, db: Session = Depends(get_db)):
    service = EvidenceService(db)
    return service.add_evidence(item)


@app.get(f"{settings.api_prefix}/evidence", response_model=list[EvidenceItem])
def list_evidence(status: EvidenceStatus = None, db: Session = Depends(get_db)):
    service = EvidenceService(db)
    return service.list_evidence(status)


@app.get(f"{settings.api_prefix}/evidence/{{evidence_id}}", response_model=EvidenceItem)
def get_evidence(evidence_id: str, db: Session = Depends(get_db)):
    service = EvidenceService(db)
    evidence = service.get_evidence(evidence_id)
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
    return evidence


@app.post(f"{settings.api_prefix}/evidence/{{evidence_id}}/verify")
def verify_evidence(evidence_id: str, verified_by: str, db: Session = Depends(get_db)):
    service = EvidenceService(db)
    if not service.verify_evidence(evidence_id, verified_by):
        raise HTTPException(status_code=404, detail="Evidence not found")
    return {"status": "verified", "evidence_id": evidence_id}


@app.post(f"{settings.api_prefix}/evidence/{{evidence_id}}/reject")
def reject_evidence(evidence_id: str, db: Session = Depends(get_db)):
    service = EvidenceService(db)
    if not service.reject_evidence(evidence_id):
        raise HTTPException(status_code=404, detail="Evidence not found")
    return {"status": "rejected", "evidence_id": evidence_id}


@app.patch(f"{settings.api_prefix}/evidence/{{evidence_id}}", response_model=EvidenceItem)
def update_evidence(evidence_id: str, update: EvidenceUpdate, db: Session = Depends(get_db)):
    service = EvidenceService(db)
    evidence = service.update_evidence(evidence_id, update)
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
    return evidence


# ============ Claim Evaluation (Proof Before Claim) ============


@app.post(f"{settings.api_prefix}/claims/evaluate", response_model=ClaimEvaluationResponse)
def evaluate_claim(req: ClaimEvaluationRequest, evaluator_id: str = None, db: Session = Depends(get_db)):
    service = ClaimEvaluationService(db)
    return service.evaluate_claim(req, evaluator_id)


@app.get(f"{settings.api_prefix}/claims/{{claim_id}}")
def get_claim(claim_id: str, db: Session = Depends(get_db)):
    service = ClaimEvaluationService(db)
    claim = service.get_claim(claim_id)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    return claim


@app.get(f"{settings.api_prefix}/claims", response_model=list[dict])
def list_claims(status: ClaimStatus = None, db: Session = Depends(get_db)):
    service = ClaimEvaluationService(db)
    return service.list_claims(status)


@app.post(f"{settings.api_prefix}/claims/{{claim_id}}/archive")
def archive_claim(claim_id: str, db: Session = Depends(get_db)):
    service = ClaimEvaluationService(db)
    if not service.archive_claim(claim_id):
        raise HTTPException(status_code=404, detail="Claim not found")
    return {"status": "archived", "claim_id": claim_id}


# ============ Workflow Management ============


@app.get(f"{settings.api_prefix}/workflows")
def list_workflows(db: Session = Depends(get_db)):
    service = WorkflowService(db)
    return service.list_workflows()


@app.get(f"{settings.api_prefix}/workflows/{{workflow_id}}")
def get_workflow(workflow_id: str, db: Session = Depends(get_db)):
    service = WorkflowService(db)
    workflow = service.get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow
