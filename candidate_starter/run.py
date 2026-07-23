import argparse
import importlib
import json
from datetime import datetime
from pathlib import Path

from framework.exporter import JsonlExporter


def load_spider(module_name: str, class_name: str):
    module = importlib.import_module(module_name)
    return getattr(module, class_name)


def append_error(output_dir: Path, item):
    with (output_dir / "errors.jsonl").open("a", encoding="utf-8") as file_obj:
        file_obj.write(json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n")


def product_key(seed):
    return seed.get("product_url") or seed.get("product_id") or seed.get("fixture")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--spider-module", default="candidate_spider")
    parser.add_argument("--spider-class", default="CandidateSpider")
    parser.add_argument("--seeds", default="seeds.json")
    parser.add_argument("--output", default="output")
    parser.add_argument("--version", default="")
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()

    project_dir = Path(__file__).resolve().parent
    output_dir = project_dir / args.output
    output_dir.mkdir(parents=True, exist_ok=True)
    errors_file = output_dir / "errors.jsonl"
    if errors_file.exists():
        errors_file.unlink()
    input_seeds = json.loads((project_dir / args.seeds).read_text(encoding="utf-8"))

    version = args.version or datetime.now().strftime("%Y%m%d %H:%M")
    spider_cls = load_spider(args.spider_module, args.spider_class)
    spider = spider_cls(project_dir=str(project_dir))
    category_seeds = list(spider.iter_category_seeds(input_seeds))

    summary = {
        "platform": spider.platform,
        "version": version,
        "category_seed_count": len(category_seeds),
        "product_seed_count": 0,
        "success_count": 0,
        "failed_count": 0,
        "spu_count": 0,
        "skc_count": 0,
        "sku_count": 0,
    }

    with JsonlExporter(str(output_dir)) as exporter:
        product_seeds = []
        seen_products = set()

        for seed in category_seeds:
            try:
                response = spider.fetch_seed(seed)
                if response.status_code != 200:
                    raise RuntimeError(f"unexpected list status_code={response.status_code}")
                discovered = spider.parse_list(response.text, seed, response.url)
                if not discovered:
                    raise RuntimeError("parse_list returned no product seeds")
                for product_seed in discovered:
                    key = product_key(product_seed)
                    if not key or key in seen_products:
                        continue
                    seen_products.add(key)
                    product_seed.setdefault("category_id", seed.get("category_id", ""))
                    product_seed.setdefault("category_name", seed.get("category_name", ""))
                    product_seeds.append(product_seed)
            except Exception as exc:
                summary["failed_count"] += 1
                append_error(
                    output_dir,
                    {
                        "stage": "list",
                        "seed": seed,
                        "error": repr(exc),
                    },
                )

        if args.limit:
            product_seeds = product_seeds[: args.limit]
        summary["product_seed_count"] = len(product_seeds)
        exporter.write_many("product_list", product_seeds)

        for seed in product_seeds:
            try:
                response = spider.fetch_seed(seed)
                if response.status_code != 200:
                    raise RuntimeError(f"unexpected detail status_code={response.status_code}")
                result = spider.parse_product(response.text, seed, response.url)
                result = spider.normalize_result(result, version)
                if not result.spu or not result.skc or not result.sku:
                    raise RuntimeError("empty spu/skc/sku result")
                exporter.write_many("spu", result.spu)
                exporter.write_many("skc", result.skc)
                exporter.write_many("sku", result.sku)
                summary["success_count"] += 1
                summary["spu_count"] += len(result.spu)
                summary["skc_count"] += len(result.skc)
                summary["sku_count"] += len(result.sku)
            except Exception as exc:
                summary["failed_count"] += 1
                append_error(
                    output_dir,
                    {
                        "stage": "detail",
                        "seed": seed,
                        "error": repr(exc),
                    },
                )

    (output_dir / "run_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if summary["failed_count"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
