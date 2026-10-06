import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class DIDDocument:
    did: str
    method: str = "polygon"
    verification_method: str = "did:key"
    controller: Optional[str] = None
    services: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "@context": [
                "https://www.w3.org/ns/did/v1",
                "https://w3id.org/security/suites/jws-2020/v1",
            ],
            "id": self.did,
            "controller": self.controller or self.did,
            "verificationMethod": [
                {
                    "id": f"{self.did}#key-1",
                    "type": self.verification_method,
                    "controller": self.did,
                    "publicKeyMultibase": "z6MkhaXgBZDvotDkL5257faiztiGiU" + hashlib.sha256(self.did.encode()).hexdigest()[:32],
                }
            ],
            "authentication": [f"{self.did}#key-1"],
            "assertionMethod": [f"{self.did}#key-1"],
            "service": self.services,
        }


def generate_did(subject_id: str, method: str = "polygon") -> str:
    digest = hashlib.sha256(subject_id.encode("utf-8")).hexdigest()
    return f"did:{method}:{digest[:32]}"


def resolve_did(did: str) -> Dict[str, Any]:
    if not did or not did.startswith("did:"):
        raise ValueError("A DID must begin with 'did:'")
    method = did.split(":", 2)[1] if ":" in did else "unknown"
    doc = DIDDocument(did=did, method=method, controller=did, services=[{"id": f"{did}#ipfs", "type": "DecentralizedWebNode", "serviceEndpoint": ["https://ipfs.io"]}]).to_dict()
    return doc
