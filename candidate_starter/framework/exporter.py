import json
from pathlib import Path
from typing import Iterable, Mapping


class JsonlExporter:
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.files = {
            "product_list": (self.output_dir / "product_list.jsonl").open("w", encoding="utf-8"),
            "spu": (self.output_dir / "spu.jsonl").open("w", encoding="utf-8"),
            "skc": (self.output_dir / "skc.jsonl").open("w", encoding="utf-8"),
            "sku": (self.output_dir / "sku.jsonl").open("w", encoding="utf-8"),
        }

    def write_many(self, kind: str, records: Iterable[Mapping]):
        file_obj = self.files[kind]
        for record in records:
            file_obj.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")

    def close(self):
        for file_obj in self.files.values():
            file_obj.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
