from dataclasses import asdict, dataclass, field, is_dataclass
from typing import Any, Dict, List, Optional


def money_to_cents(value: Any) -> Optional[int]:
    if value in ("", None):
        return None
    if isinstance(value, str):
        value = value.strip().replace(",", "").replace("£", "").replace("$", "").replace("€", "")
    return round(float(value) * 100)


def to_plain_dict(record: Any) -> Dict[str, Any]:
    if is_dataclass(record):
        record = asdict(record)
    if not isinstance(record, dict):
        raise TypeError(f"record must be dict or dataclass, got {type(record)!r}")
    return dict(record)


@dataclass
class SpuRecord:
    spu_id: str
    spu_product_title: str
    spu_detail_page_url: str
    spu_main_image_url: str
    spu_pic_list: List[str]
    spu_discounted_price: int
    spu_currency_unit: str
    spu_brand_info: str = ""
    spu_detail_description: str = ""
    spu_through_price: Optional[int] = None
    spu_stock_status: str = ""
    spu_stock_count: str = ""
    spu_category: Any = None
    platform: str = ""
    version: str = ""
    expand_info: Any = ""


@dataclass
class SkcRecord:
    spu_id: str
    skc_id: str
    skc_color: str
    skc_product_title: str
    skc_detail_page_url: str
    skc_main_image_url: str
    skc_pic_list: List[str]
    skc_discounted_price: int
    skc_currency_unit: str
    skc_through_price: Optional[int] = None
    skc_stock_status: str = ""
    skc_stock_count: str = ""
    skc_detail_description: str = ""
    platform: str = ""
    version: str = ""
    expand_info: Any = ""


@dataclass
class SkuRecord:
    spu_id: str
    skc_id: str
    sku_id: str
    sku_size: str
    sku_image_url: str
    sku_discounted_price: int
    sku_currency_unit: str
    sku_product_title: str = ""
    sku_through_price: Optional[int] = None
    sku_stock_status: str = ""
    sku_stock_count: str = ""
    sku_attrs: List[Dict[str, Any]] = field(default_factory=list)
    platform: str = ""
    version: str = ""
    expand_info: Any = ""


@dataclass
class CrawlResult:
    spu: List[Any] = field(default_factory=list)
    skc: List[Any] = field(default_factory=list)
    sku: List[Any] = field(default_factory=list)
