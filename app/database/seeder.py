from sqlalchemy.orm import Session
from app.models import (
    AgentRegistration,
    EvidenceItem,
    WorkflowTemplate,
    WorkflowStep,
    AgentStatus,
    EvidenceStatus,
)
from app.services.agent_registry import AgentRegistryService
from app.services.evidence_service import EvidenceService
from app.services.workflow_service import WorkflowService
from datetime import datetime


def seed_database(db: Session) -> None:
    """
    Seed the database with sample agents, evidence, and workflows.
    """
    agent_service = AgentRegistryService(db)
    evidence_service = EvidenceService(db)
    workflow_service = WorkflowService(db)
    
    # Seed Agents
    agents = [
        AgentRegistration(
            agent_id="sentinel-audit",
            name="Sentinel Audit Agent",
            role="security_verifier",
            status=AgentStatus.ACTIVE,
            description="Validates evidence integrity and operational compliance.",
            capabilities=["verify_evidence", "audit_claims", "generate_reports"],
        ),
        AgentRegistration(
            agent_id="evidence-orchestrator",
            name="Evidence Orchestrator",
            role="evidence_manager",
            status=AgentStatus.ACTIVE,
            description="Coordinates claim checks and evidence collection.",
            capabilities=["collect_evidence", "organize_evidence", "track_lineage"],
        ),
        AgentRegistration(
            agent_id="human-oversight",
            name="Human Oversight Coordinator",
            role="governance_reviewer",
            status=AgentStatus.ACTIVE,
            description="Reviews exceptional scenarios and approves final interventions.",
            capabilities=["review_claims", "approve_interventions", "escalate_issues"],
        ),
    ]
    
    for agent in agents:
        existing = agent_service.get_agent(agent.agent_id)
        if not existing:
            agent_service.register_agent(agent)
    
    # Seed Evidence
    evidence_items = [
        EvidenceItem(
            evidence_id="ev-system-audit-001",
            source="system-audit-2026-10-05",
            content="System audit completed successfully. No critical defects detected. All services operational.",
            verified=True,
            status=EvidenceStatus.VERIFIED,
            submitted_by="sentinel-audit",
            verified_by="human-oversight",
            tags=["system", "audit", "compliance"],
        ),
        EvidenceItem(
            evidence_id="ev-telemetry-001",
            source="telemetry-dashboard-2026-10-05",
            content="Telemetry data shows stable health metrics across core services. CPU: 45%, Memory: 62%, Network: healthy.",
            verified=True,
            status=EvidenceStatus.VERIFIED,
            submitted_by="evidence-orchestrator",
            verified_by="sentinel-audit",
            tags=["telemetry", "health", "performance"],
        ),
        EvidenceItem(
            evidence_id="ev-security-scan-001",
            source="security-scanner-2026-10-05",
            content="Security scan complete. No vulnerabilities detected in core infrastructure.",
            verified=False,
            status=EvidenceStatus.PENDING,
            submitted_by="sentinel-audit",
            tags=["security", "scan", "infrastructure"],
        ),
    ]
    
    for evidence in evidence_items:
        existing = evidence_service.get_evidence(evidence.evidence_id)
        if not existing:
            evidence_service.add_evidence(evidence)
    
    # Seed Workflows
    workflows = [
        WorkflowTemplate(
            workflow_id="wf-claim-approval",
            name="Standard Claim Approval Workflow",
            description="Standard workflow for evaluating and approving claims with proof-before-claim enforcement.",
            steps=[
                WorkflowStep(
                    step_id="step-1",
                    name="Submit Claim",
                    description="Submit claim with required evidence references.",
                    required_role="user",
                    order=1,
                ),
                WorkflowStep(
                    step_id="step-2",
                    name="Verify Evidence",
                    description="Verify that all required evidence exists and is authentic.",
                    required_role="evidence_manager",
                    order=2,
                ),
                WorkflowStep(
                    step_id="step-3",
                    name="Audit Claim",
                    description="Audit the claim against verified evidence.",
                    required_role="security_verifier",
                    order=3,
                ),
                WorkflowStep(
                    step_id="step-4",
                    name="Human Review",
                    description="Final review and approval by human oversight.",
                    required_role="governance_reviewer",
                    order=4,
                ),
                WorkflowStep(
                    step_id="step-5",
                    name="Archive Claim",
                    description="Archive approved claim for historical record.",
                    required_role="evidence_manager",
                    order=5,
                ),
            ],
            created_at=datetime.utcnow(),
        ),
        WorkflowTemplate(
            workflow_id="wf-emergency-override",
            name="Emergency Override Workflow",
            description="Expedited workflow for emergency scenarios requiring immediate approval.",
            steps=[
                WorkflowStep(
                    step_id="step-1",
                    name="Submit Emergency Claim",
                    description="Submit emergency claim with justification.",
                    required_role="user",
                    order=1,
                ),
                WorkflowStep(
                    step_id="step-2",
                    name="Emergency Review",
                    description="Fast-track review by governance team.",
                    required_role="governance_reviewer",
                    order=2,
                ),
                WorkflowStep(
                    step_id="step-3",
                    name="Execute Override",
                    description="Execute the approved override action.",
                    required_role="security_verifier",
                    order=3,
                ),
            ],
            created_at=datetime.utcnow(),
        ),
    ]
    
    for workflow in workflows:
        existing = workflow_service.get_workflow(workflow.workflow_id)
        if not existing:
            workflow_service.create_workflow(workflow)
