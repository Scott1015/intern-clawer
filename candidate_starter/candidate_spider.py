from framework import BaseSpider, CrawlResult
from framework.models import money_to_cents


class CandidateSpider(BaseSpider):
    platform = "replace_with_platform_region"

    # Add site-specific headers here when needed.
    default_headers = {
        **BaseSpider.default_headers,
        "referer": "replace_with_site_homepage",
    }

    def iter_category_seeds(self, input_seeds):
        """
        Return category/list-page seeds.

        You may use seeds.json directly, or fetch homepage/navigation here and
        generate category seeds dynamically.
        """
        return input_seeds

    def parse_list(self, html_text, seed, final_url):
        """
        Parse a category/list/search page and return product detail seeds.

        Return a list like:
        [
            {
                "product_id": "...",
                "product_url": "https://...",
                "product_name": "...",
                "category_id": seed.get("category_id", ""),
                "category_name": seed.get("category_name", "")
            }
        ]
        """
        raise NotImplementedError("Please implement list-page product discovery")

    def parse_product(self, html_text, seed, final_url):
        """
        Parse one product detail page.

        Return:
            CrawlResult(spu=[...], skc=[...], sku=[...])

        See examples/static_shop_spider.py for a small runnable reference.
        """
        raise NotImplementedError("Please implement product parsing logic")

    @staticmethod
    def price_to_cents(value):
        return money_to_cents(value)
