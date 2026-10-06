from abc import ABC, abstractmethod
from typing import Any, Dict, List, Sequence


class BiometricProvider(ABC):
    """Abstract biometric provider for device, edge, or sensor input."""

    @abstractmethod
    def enroll(self, subject_id: str, sample: Any) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def verify(self, subject_id: str, sample: Any, template: Dict[str, Any]) -> bool:
        raise NotImplementedError

    @abstractmethod
    def generate_template(self, sample: Any) -> Dict[str, Any]:
        raise NotImplementedError
