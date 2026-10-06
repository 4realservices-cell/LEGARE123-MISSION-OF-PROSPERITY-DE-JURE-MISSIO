from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, Optional

try:
    import requests
except ImportError:  # pragma: no cover
    requests = None


class IPFSClient:
    """Lightweight IPFS client wrapper with an HTTP fallback for tests and local dev."""

    def __init__(self, endpoint: str = "http://127.0.0.1:5001", timeout: int = 10):
        self.endpoint = endpoint.rstrip("/")
        self.timeout = timeout

    def upload_json(self, payload: Dict[str, Any], pin: bool = True) -> Dict[str, str]:
        if requests is None:
            cid = hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()
            return {"cid": cid, "url": f"ipfs://{cid}", "pinned": pin}

        serialized = json.dumps(payload, sort_keys=True).encode("utf-8")
        response = requests.post(
            f"{self.endpoint}/api/v0/add?pin={str(pin).lower()}",
            files={"file": serialized},
            timeout=self.timeout,
        )
        response.raise_for_status()
        data = response.json()
        return {"cid": data.get("Hash", ""), "url": f"ipfs://{data.get('Hash', '')}", "pinned": pin}

    def pin(self, cid: str) -> Dict[str, Any]:
        if requests is None:
            return {"cid": cid, "pinned": True}
        response = requests.post(f"{self.endpoint}/api/v0/pin/add?arg={cid}", timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def cat(self, cid: str) -> Dict[str, Any]:
        if requests is None:
            return {"cid": cid, "payload": {}}
        response = requests.post(f"{self.endpoint}/api/v0/cat?arg={cid}", timeout=self.timeout)
        response.raise_for_status()
        return response.json()


__all__ = ["IPFSClient"]
