import argparse
import json
from pathlib import Path
from typing import Any, Dict, List


REQUIRED = {
    "spu": [
        "platform",
        "version",
        "spu_id",
        "spu_product_title",
        "spu_detail_page_url",
        "spu_main_image_url",
        "spu_pic_list",
        "spu_discounted_price",
        "spu_currency_unit",
    ],
    "skc": [
        "platform",
        "version",
        "spu_id",
        "skc_id",
        "skc_color",
        "skc_product_title",
        "skc_detail_page_url",
        "skc_main_image_url",
        "skc_pic_list",
        "skc_discounted_price",
        "skc_currency_unit",
    ],
    "sku": [
        "platform",
        "version",
        "spu_id",
        "skc_id",
        "sku_id",
        "sku_size",
        "sku_image_url",
        "sku_discounted_price",
        "sku_currency_unit",
    ],
}


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    records = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path.name}:{line_no} is not valid JSON: {exc}") from exc
    return records


def is_blank(value: Any) -> bool:
    return value is None or value == "" or value == []


def check_required(kind: str, records: List[Dict[str, Any]], errors: List[str]):
    for index, record in enumerate(records, start=1):
        for field in REQUIRED[kind]:
            if field not in record or is_blank(record[field]):
                errors.append(f"{kind}.jsonl record {index}: missing required field {field}")


def check_prices(kind: str, records: List[Dict[str, Any]], errors: List[str]):
    price_field = {
        "spu": "spu_discounted_price",
        "skc": "skc_discounted_price",
        "sku": "sku_discounted_price",
    }[kind]
    through_field = {
        "spu": "spu_through_price",
        "skc": "skc_through_price",
        "sku": "sku_through_price",
    }[kind]
    for index, record in enumerate(records, start=1):
        value = record.get(price_field)
        if not isinstance(value, int) or value <= 0:
            errors.append(f"{kind}.jsonl record {index}: {price_field} must be positive integer cents")
        through = record.get(through_field)
        if through not in ("", None) and not isinstance(through, int):
            errors.append(f"{kind}.jsonl record {index}: {through_field} must be integer cents or empty")


def check_images(kind: str, records: List[Dict[str, Any]], errors: List[str]):
    list_field = "spu_pic_list" if kind == "spu" else "skc_pic_list" if kind == "skc" else None
    main_field = "spu_main_image_url" if kind == "spu" else "skc_main_image_url" if kind == "skc" else "sku_image_url"
    for index, record in enumerate(records, start=1):
        main_image = record.get(main_field)
        if not isinstance(main_image, str) or not main_image.startswith("http"):
            errors.append(f"{kind}.jsonl record {index}: {main_field} must be absolute http url")
        if list_field:
            images = record.get(list_field)
            if not isinstance(images, list) or not images:
                errors.append(f"{kind}.jsonl record {index}: {list_field} must be non-empty list")
            elif not all(isinstance(item, str) and item.startswith("http") for item in images):
                errors.append(f"{kind}.jsonl record {index}: all {list_field} values must be absolute http urls")


def check_currency(kind: str, records: List[Dict[str, Any]], errors: List[str]):
    field = f"{kind}_currency_unit"
    for index, record in enumerate(records, start=1):
        currency = record.get(field)
        if not isinstance(currency, str) or len(currency) != 3 or currency.upper() != currency:
            errors.append(f"{kind}.jsonl record {index}: {field} must be ISO-like 3-letter uppercase currency")


def check_references(spu, skc, sku, errors):
    spu_ids = {item.get("spu_id") for item in spu}
    skc_ids = {item.get("skc_id") for item in skc}
    for index, item in enumerate(skc, start=1):
        if item.get("spu_id") not in spu_ids:
            errors.append(f"skc.jsonl record {index}: spu_id not found in spu.jsonl")
    for index, item in enumerate(sku, start=1):
        if item.get("spu_id") not in spu_ids:
            errors.append(f"sku.jsonl record {index}: spu_id not found in spu.jsonl")
        if item.get("skc_id") not in skc_ids:
            errors.append(f"sku.jsonl record {index}: skc_id not found in skc.jsonl")


def check_duplicates(kind: str, records: List[Dict[str, Any]], id_field: str, errors: List[str]):
    seen = set()
    for index, item in enumerate(records, start=1):
        value = item.get(id_field)
        if value in seen:
            errors.append(f"{kind}.jsonl record {index}: duplicate {id_field}={value}")
        seen.add(value)


def check_product_list(records: List[Dict[str, Any]], errors: List[str]):
    for index, item in enumerate(records, start=1):
        if not item.get("product_url") and not item.get("fixture"):
            errors.append(f"product_list.jsonl record {index}: product_url or fixture is required")
        if not item.get("product_id") and not item.get("product_url"):
            errors.append(f"product_list.jsonl record {index}: product_id or product_url is required")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="output")
    parser.add_argument("--min-spu", type=int, default=1)
    parser.add_argument("--min-skc", type=int, default=1)
    parser.add_argument("--min-sku", type=int, default=1)
    parser.add_argument("--min-products", type=int, default=1)
    args = parser.parse_args()

    output_dir = Path(args.output)
    product_list = load_jsonl(output_dir / "product_list.jsonl")
    spu = load_jsonl(output_dir / "spu.jsonl")
    skc = load_jsonl(output_dir / "skc.jsonl")
    sku = load_jsonl(output_dir / "sku.jsonl")
    errors: List[str] = []

    if len(product_list) < args.min_products:
        errors.append(f"product_list count {len(product_list)} < min {args.min_products}")
    if len(spu) < args.min_spu:
        errors.append(f"spu count {len(spu)} < min {args.min_spu}")
    if len(skc) < args.min_skc:
        errors.append(f"skc count {len(skc)} < min {args.min_skc}")
    if len(sku) < args.min_sku:
        errors.append(f"sku count {len(sku)} < min {args.min_sku}")

    for kind, records in [("spu", spu), ("skc", skc), ("sku", sku)]:
        check_required(kind, records, errors)
        check_prices(kind, records, errors)
        check_images(kind, records, errors)
        check_currency(kind, records, errors)

    check_product_list(product_list, errors)
    check_duplicates("spu", spu, "spu_id", errors)
    check_duplicates("skc", skc, "skc_id", errors)
    check_duplicates("sku", sku, "sku_id", errors)
    check_references(spu, skc, sku, errors)

    if errors:
        print("VALIDATION FAILED")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    print("VALIDATION PASSED")
    print(json.dumps({"products": len(product_list), "spu": len(spu), "skc": len(skc), "sku": len(sku)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
