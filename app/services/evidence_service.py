from typing import Any

from app.services.agent_registry import get_agent


def evaluate_claim(claim: str, evidence: list[str], agent_id: str | None = None) -> dict[str, Any]:
    normalized_claim = claim.strip().lower()
    normalized_evidence = [item.strip().lower() for item in evidence if isinstance(item, str) and item.strip()]

    agent = get_agent(agent_id)
    evidence_coverage = 0

    for item in normalized_evidence:
        if item and normalized_claim in item:
            evidence_coverage += 1
        elif any(keyword in item for keyword in normalized_claim.split() if len(keyword) > 3):
            evidence_coverage += 1

    has_proof = len(normalized_evidence) > 0 and evidence_coverage > 0

    result = {
        "claim": claim,
        "agent_id": agent_id,
        "agent": agent.model_dump() if agent else None,
        "status": "verified" if has_proof else "rejected",
        "proof_before_claim": has_proof,
        "evidence_count": len(normalized_evidence),
        "evidence_coverage": evidence_coverage,
        "message": (
            "The claim is supported by sufficient evidence and can proceed."
            if has_proof
            else "The claim is rejected until evidence is added that supports it."
        ),
    }
    return result
