import hashlib
from typing import Sequence


class CancellableBiometricTemplate:
    """Generates a deterministic, revocable protected template from a biometric vector."""

    def __init__(self, salt: str = "sentinel-biometric-salt"):
        self.salt = salt

    def _normalize_vector(self, biometric_vector: Sequence[float]) -> str:
        return ":".join(str(float(value)) for value in biometric_vector)

    def generate_template(self, biometric_vector: Sequence[float], subject_id: str) -> dict:
        canonical = f"{subject_id}:{self.salt}:{self._normalize_vector(biometric_vector)}"
        protected_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        return {
            "subject_id": subject_id,
            "protected_template_hash": protected_hash,
            "revocable": True,
            "method": "cancellable-transform",
        }

    def rotate_template(self, biometric_vector: Sequence[float], subject_id: str, old_salt: str | None = None) -> dict:
        salt = old_salt or self.salt
        canonical = f"{subject_id}:{salt}:{self._normalize_vector(biometric_vector)}"
        protected_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        return {
            "subject_id": subject_id,
            "protected_template_hash": protected_hash,
            "revocable": True,
            "method": "cancellable-transform",
            "rotated": True,
        }
