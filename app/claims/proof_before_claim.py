import hashlib
import json
from typing import Any, Dict, Optional

from app.chain.revocation import RevocationRegistry
from app.identity.did import resolve_did, generate_did
from app.identity.vc import verify_verifiable_presentation


class ProofBeforeClaimService:
    """Business logic gate enforcing Proof Before Claim."""

    def __init__(self, revocation_registry: Optional[RevocationRegistry] = None):
        self.revocation_registry = revocation_registry or RevocationRegistry()

    def _audit_hash(self, claim: Dict[str, Any]) -> str:
        canonical = json.dumps(claim, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def evaluate(self, claim: Dict[str, Any], verifiable_presentation: Dict[str, Any]) -> Dict[str, Any]:
        holder = verifiable_presentation.get("holder")
        proof = verifiable_presentation.get("proof")
        if not holder or not proof:
            return {"accepted": False, "reason": "Proof is missing the holder or proof payload.", "audit_hash": self._audit_hash(claim)}

        did_document = resolve_did(holder)
        if not verify_verifiable_presentation(verifiable_presentation, did_document=did_document):
            return {"accepted": False, "reason": "Cryptographic proof verification failed.", "audit_hash": self._audit_hash(claim)}

        protected_template_hash = claim.get("protected_template_hash")
        if not protected_template_hash:
            return {"accepted": False, "reason": "Missing protected template hash for the subject.", "audit_hash": self._audit_hash(claim)}

        if self.revocation_registry.is_revoked(protected_template_hash):
            return {"accepted": False, "reason": "Protected template has been revoked.", "audit_hash": self._audit_hash(claim)}

        return {
            "accepted": True,
            "reason": "Proof verified and revocation registry check passed.",
            "audit_hash": self._audit_hash(claim),
            "holder_did": holder,
            "proof_type": proof.get("type"),
        }
