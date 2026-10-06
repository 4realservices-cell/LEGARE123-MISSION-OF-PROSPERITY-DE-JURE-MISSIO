import hashlib
import json
from dataclasses import dataclass
from typing import Any, Dict, Optional


def _canonical_json(data: Dict[str, Any]) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


@dataclass
class VerifiablePresentation:
    holder: str
    attributes: Dict[str, Any]
    proof: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "@context": ["https://www.w3.org/2018/credentials/v1"],
            "type": ["VerifiablePresentation"],
            "holder": self.holder,
            "verifiableCredential": self.attributes,
            "proof": self.proof,
        }


def create_verifiable_presentation(holder_did: str, attributes: Dict[str, Any], nonce: str = "sentinel-proof") -> VerifiablePresentation:
    payload = {"holder": holder_did, "attributes": attributes, "nonce": nonce}
    signature = hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()
    proof = {
        "type": "Ed25519Signature2020",
        "created": "2026-10-06T00:00:00Z",
        "verificationMethod": f"{holder_did}#key-1",
        "nonce": nonce,
        "signature": signature,
    }
    return VerifiablePresentation(holder=holder_did, attributes=attributes, proof=proof)


def verify_verifiable_presentation(vp: Dict[str, Any], did_document: Optional[Dict[str, Any]] = None) -> bool:
    if not isinstance(vp, dict):
        return False
    if "holder" not in vp or "proof" not in vp:
        return False
    proof = vp.get("proof")
    if not isinstance(proof, dict):
        return False
    required_keys = {"type", "verificationMethod", "signature", "nonce"}
    if not required_keys.issubset(proof.keys()):
        return False
    if did_document and vp.get("holder") != did_document.get("id"):
        return False
    attributes = vp.get("verifiableCredential", vp.get("attributes", {}))
    payload = {"holder": vp.get("holder"), "attributes": attributes, "nonce": proof.get("nonce")}
    expected_signature = hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()
    return proof.get("signature") == expected_signature
