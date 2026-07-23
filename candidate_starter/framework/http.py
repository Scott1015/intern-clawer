from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional


@dataclass
class SimpleResponse:
    status_code: int
    url: str
    text: str
    headers: Dict[str, str]


class HttpClient:
    def __init__(self, timeout: int = 30, impersonate: str = "chrome131"):
        self.timeout = timeout
        self.impersonate = impersonate

    def get(self, url: str, headers: Optional[Dict[str, str]] = None, **kwargs) -> SimpleResponse:
        headers = headers or {}
        try:
            from curl_cffi import requests

            response = requests.get(
                url,
                headers=headers,
                timeout=kwargs.get("timeout", self.timeout),
                impersonate=kwargs.get("impersonate", self.impersonate),
                verify=kwargs.get("verify", False),
                allow_redirects=True,
            )
        except ImportError:
            import requests

            response = requests.get(
                url,
                headers=headers,
                timeout=kwargs.get("timeout", self.timeout),
                verify=kwargs.get("verify", False),
                allow_redirects=True,
            )
        return SimpleResponse(
            status_code=response.status_code,
            url=str(response.url),
            text=response.text,
            headers=dict(response.headers),
        )

    def from_fixture(self, fixture_path: str, base_dir: Path) -> SimpleResponse:
        path = Path(fixture_path)
        if not path.is_absolute():
            path = base_dir / path
        return SimpleResponse(
            status_code=200,
            url=path.as_uri(),
            text=path.read_text(encoding="utf-8"),
            headers={"content-type": "text/html; charset=utf-8"},
        )
