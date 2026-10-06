from __future__ import annotations

import hashlib
from typing import Any, Dict, Sequence

from app.biometrics.base import BiometricProvider


class WebAuthnProvider(BiometricProvider):
    """A minimal WebAuthn-oriented provider implementation that does not require a browser runtime."""

    def generate_challenge(self, subject_id: str) -> str:
        return hashlib.sha256(f"webauthn:{subject_id}:sentinel-challenge".encode("utf-8")).hexdigest()

    def enroll(self, subject_id: str, sample: Any) -> Dict[str, Any]:
        template = self.generate_template(sample)
        return {
            "subject_id": subject_id,
            "provider": "webauthn",
            "template": template,
            "challenge": self.generate_challenge(subject_id),
        }

    def generate_template(self, sample: Any) -> Dict[str, Any]:
        if not isinstance(sample, (str, bytes, dict)):
            raise TypeError("WebAuthn template generation expects a string, bytes, or dict payload")
        serialized = str(sample).encode("utf-8")
        return {
            "template_hash": hashlib.sha256(serialized).hexdigest(),
            "method": "webauthn",
            "format": "protected-template",
        }

    def verify(self, subject_id: str, sample: Any, template: Dict[str, Any]) -> bool:
        generated = self.generate_template(sample)
        return generated["template_hash"] == template.get("template_hash") and subject_id is not None
