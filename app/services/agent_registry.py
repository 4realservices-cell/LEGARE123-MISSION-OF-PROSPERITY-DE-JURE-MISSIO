from app.models import AgentRecord


AGENT_REGISTRY = [
    AgentRecord(
        id="sentinel-audit",
        name="Sentinel Audit",
        role="Security verifier",
        status="active",
        description="Validates evidence integrity, risk state, and operational compliance.",
    ),
    AgentRecord(
        id="evidence-orchestrator",
        name="Evidence Orchestrator",
        role="Evidence manager",
        status="active",
        description="Coordinates claim checks, evidence collection, and traceability.",
    ),
    AgentRecord(
        id="human-oversight",
        name="Human Oversight",
        role="Governance reviewer",
        status="ready",
        description="Reviews exceptional scenarios and approves final interventions when needed.",
    ),
]


def list_agents() -> list[dict]:
    return [agent.model_dump() for agent in AGENT_REGISTRY]


def get_agent(agent_id: str | None) -> AgentRecord | None:
    if not agent_id:
        return None
    for agent in AGENT_REGISTRY:
        if agent.id == agent_id:
            return agent
    return None
