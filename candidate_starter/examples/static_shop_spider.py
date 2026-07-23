import json
import re

from framework import BaseSpider, CrawlResult
from framework.models import money_to_cents


def parse_attrs(tag_text):
    return dict(re.findall(r'([\w-]+)="([^"]*)"', tag_text))


class CandidateSpider(BaseSpider):
    platform = "demo_shop_gb"

    def parse_list(self, html_text, seed, final_url):
        product_seeds = []
        for match in re.finditer(r'<a\s+([^>]*class="product-card"[^>]*)>(.*?)</a>', html_text, re.S):
            attrs = parse_attrs(match.group(1))
            product_seeds.append(
                {
                    "product_id": attrs.get("data-product-id", ""),
                    "product_url": attrs.get("href", ""),
                    "product_name": attrs.get("data-product-name", re.sub(r"<.*?>", "", match.group(2)).strip()),
                    "fixture": attrs.get("data-fixture", ""),
                    "category_id": seed.get("category_id", ""),
                    "category_name": seed.get("category_name", ""),
                }
            )
        return product_seeds

    def parse_product(self, html_text, seed, final_url):
        match = re.search(
            r'<script id="__PRODUCT_DATA__" type="application/json">(.*?)</script>',
            html_text,
            re.S,
        )
        if not match:
            raise ValueError("product data script not found")
        product = json.loads(match.group(1))
        price = money_to_cents(product["price"])
        original_price = money_to_cents(product.get("original_price"))

        colors = product.get("colors") or []
        main_images = colors[0]["images"] if colors else []
        spu = [
            {
                "spu_id": product["id"],
                "spu_product_title": product["title"],
                "spu_detail_page_url": product["url"],
                "spu_main_image_url": main_images[0],
                "spu_pic_list": main_images,
                "spu_through_price": original_price,
                "spu_discounted_price": price,
                "spu_currency_unit": product["currency"],
                "spu_detail_description": product.get("description", ""),
                "spu_brand_info": product.get("brand", ""),
            }
        ]

        skc = []
        sku = []
        for color in colors:
            skc_id = f'{product["id"]}_{color["id"]}'
            images = color.get("images") or main_images
            skc.append(
                {
                    "spu_id": product["id"],
                    "skc_id": skc_id,
                    "skc_color": color["name"],
                    "skc_product_title": product["title"],
                    "skc_detail_page_url": f'{product["url"]}?color={color["id"]}',
                    "skc_main_image_url": images[0],
                    "skc_pic_list": images,
                    "skc_through_price": original_price,
                    "skc_discounted_price": price,
                    "skc_currency_unit": product["currency"],
                }
            )
            sizes = color.get("sizes") or ["no size"]
            for size in sizes:
                sku.append(
                    {
                        "spu_id": product["id"],
                        "skc_id": skc_id,
                        "sku_id": f"{skc_id}_{size}",
                        "sku_size": size,
                        "sku_image_url": images[0],
                        "sku_through_price": original_price,
                        "sku_discounted_price": price,
                        "sku_currency_unit": product["currency"],
                    }
                )

        return CrawlResult(spu=spu, skc=skc, sku=sku)
