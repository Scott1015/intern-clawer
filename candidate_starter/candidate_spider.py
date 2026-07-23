import json
import re

from framework import BaseSpider, CrawlResult
from framework.models import money_to_cents


def parse_attrs(tag_text):
    """提取标签属性助手函数"""
    return dict(re.findall(r'([\w-]+)="([^"]*)"', tag_text))


class CandidateSpider(BaseSpider):
    platform = "demo_shop_gb"

    default_headers = {
        **BaseSpider.default_headers,
        "referer": "https://example.test",
    }

    def iter_category_seeds(self, input_seeds):
        """返回类目种子输入"""
        return input_seeds

    def parse_list(self, html_text, seed, final_url):
        """
        解析商品列表页，提取商品卡片链接及 Fixture 信息
        """
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
        """
        解析商品详情页，拆分为 SPU / SKC / SKU 三层结构
        """
        # 1. 从网页中寻找 __PRODUCT_DATA__ 脚本里的 JSON 数据
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

        # 2. 构建 SPU 层数据 (主商品)
        spu = [
            {
                "spu_id": product["id"],
                "spu_product_title": product["title"],
                "spu_detail_page_url": product["url"],
                "spu_main_image_url": main_images[0] if main_images else "",
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

        # 3. 构建 SKC (颜色) 与 SKU (规格/尺码) 层数据
        for color in colors:
            skc_id = f'{product["id"]}_{color["id"]}'
            images = color.get("images") or main_images

            # 生成 SKC
            skc.append(
                {
                    "spu_id": product["id"],
                    "skc_id": skc_id,
                    "skc_color": color["name"],
                    "skc_product_title": product["title"],
                    "skc_detail_page_url": f'{product["url"]}?color={color["id"]}',
                    "skc_main_image_url": images[0] if images else "",
                    "skc_pic_list": images,
                    "skc_through_price": original_price,
                    "skc_discounted_price": price,
                    "skc_currency_unit": product["currency"],
                }
            )

            # 生成 SKU (按尺码拆分)
            sizes = color.get("sizes") or ["no size"]
            for size in sizes:
                sku.append(
                    {
                        "spu_id": product["id"],
                        "skc_id": skc_id,
                        "sku_id": f"{skc_id}_{size}",
                        "sku_size": size,
                        "sku_image_url": images[0] if images else "",
                        "sku_through_price": original_price,
                        "sku_discounted_price": price,
                        "sku_currency_unit": product["currency"],
                    }
                )

        return CrawlResult(spu=spu, skc=skc, sku=sku)

    @staticmethod
    def price_to_cents(value):
        return money_to_cents(value)