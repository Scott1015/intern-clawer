from pathlib import Path
from typing import Any, Dict, Iterable, List

from .http import HttpClient
from .models import CrawlResult, to_plain_dict


class BaseSpider:
    platform = "replace_with_platform_region"
    default_headers: Dict[str, str] = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "accept-language": "en-US,en;q=0.9",
        "user-agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/131.0.0.0 Safari/537.36"
        ),
    }
    timeout = 30
    impersonate = "chrome131"

    def __init__(self, project_dir: str):
        self.project_dir = Path(project_dir)
        self.http = HttpClient(timeout=self.timeout, impersonate=self.impersonate)

    def iter_category_seeds(self, input_seeds: List[Dict[str, Any]]) -> Iterable[Dict[str, Any]]:
        """
        Return category/list-page seeds to crawl.

        The default implementation uses seeds.json directly. Candidates may override
        this method when a site needs navigation discovery from the homepage.
        """
        return input_seeds

    def fetch_seed(self, seed: Dict[str, Any]):
        if seed.get("fixture"):
            return self.http.from_fixture(seed["fixture"], self.project_dir)
        url = seed.get("category_url") or seed.get("list_url") or seed.get("product_url")
        if not url:
            raise ValueError("seed must contain category_url, list_url, product_url, or fixture")
        return self.http.get(
            url,
            headers=self.default_headers,
            timeout=self.timeout,
            impersonate=self.impersonate,
        )

    def parse_list(self, html_text: str, seed: Dict[str, Any], final_url: str) -> List[Dict[str, Any]]:
        """
        Parse a category/list/search page and return product detail seeds.

        Each returned dict should contain product_url or fixture. Recommended fields:
        product_id, product_url, product_name, category_id, category_name.
        """
        raise NotImplementedError("Implement CandidateSpider.parse_list()")

    def parse_product(self, html_text: str, seed: Dict[str, Any], final_url: str) -> CrawlResult:
        raise NotImplementedError("Implement CandidateSpider.parse_product()")

    def normalize_result(self, result: Any, version: str) -> CrawlResult:
        if isinstance(result, tuple) and len(result) == 3:
            result = CrawlResult(spu=result[0], skc=result[1], sku=result[2])
        if not isinstance(result, CrawlResult):
            raise TypeError("parse_product must return CrawlResult or (spu, skc, sku)")

        return CrawlResult(
            spu=[self._normalize_record(item, version) for item in result.spu],
            skc=[self._normalize_record(item, version) for item in result.skc],
            sku=[self._normalize_record(item, version) for item in result.sku],
        )

    def _normalize_record(self, record: Any, version: str) -> Dict[str, Any]:
        data = to_plain_dict(record)
        data.setdefault("platform", self.platform)
        data.setdefault("version", version)
        data.setdefault("expand_info", "")
        return data
