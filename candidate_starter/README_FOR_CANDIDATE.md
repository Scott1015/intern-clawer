# 独立站整站采集笔试说明

你需要在给定轻量框架内完成一个独立站的完整商品采集链路，并按固定格式输出到本地 JSONL 文件。

请先 fork 仓库，在自己的 fork 中完成代码和 `output/` 数据结果；本地确认通过后，把代码和数据结果一起 push，并向原仓库提交 Pull Request。

本题不是只解析几个详情页。你需要实现：

1. 类目/列表入口处理。
2. 商品列表解析和商品 URL 发现。
3. 商品详情页解析。
4. SPU/SKC/SKU 三层数据输出。

## 你需要交付

- 修改后的 `candidate_spider.py`
- 如有必要，可以新增少量 helper 文件
- 运行后的 `output/product_list.jsonl`
- 运行后的 `output/spu.jsonl`
- 运行后的 `output/skc.jsonl`
- 运行后的 `output/sku.jsonl`
- 运行后的 `output/run_summary.json`
- 如有失败种子，保留 `output/errors.jsonl`

## 快速开始

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python run.py --spider-module candidate_spider --seeds seeds.json --output output
python validate_output.py --output output
```

你主要需要实现 `candidate_spider.py` 里的三个方法：

- `iter_category_seeds()`：返回要采集的类目/列表入口。默认直接使用 `seeds.json`。
- `parse_list()`：解析类目页/列表页，返回商品详情 seed 列表。
- `parse_product()`：解析商品详情页，返回 SPU/SKC/SKU。

如果目标站需要特殊请求头，可以修改 `default_headers`；如果目标站需要接口请求、分页或 cookie，也可以覆盖 `fetch_seed()` 或新增 helper。

## 重要要求

- 必须输出 `product_list.jsonl`，证明代码完成了商品发现。
- 必须输出 `spu.jsonl`、`skc.jsonl`、`sku.jsonl`。
- 输出必须是 JSONL，每行一条 JSON。
- 价格字段统一使用整数，单位为“分/cent/pence”，例如 `GBP 69.99` 输出 `6999`。
- 图片列表字段必须是 JSON 数组，不要写成字符串。
- SPU/SKC/SKU 的 ID 必须稳定，不能用随机数。
- SKU 必须能通过 `skc_id` 关联到 SKC，SKC 必须能通过 `spu_id` 关联到 SPU。
- 不能把商品数据写死为固定答案；解析逻辑应能处理从列表页发现的多个商品。
- 请求失败、商品下架、缺关键字段时，写入 `output/errors.jsonl` 或抛出明确错误，不要静默产出脏数据。

## 输出文件

运行 `run.py` 后会生成：

- `output/product_list.jsonl`：列表页发现的商品 seed。
- `output/spu.jsonl`
- `output/skc.jsonl`
- `output/sku.jsonl`
- `output/run_summary.json`
- `output/errors.jsonl`，仅当有失败时出现。

## 本地 demo

包内有一个静态示例，不访问网络，但完整模拟“类目页 -> 商品详情页”的链路：

```bash
python run.py --spider-module examples.static_shop_spider --seeds seeds.json --output output_demo
python validate_output.py --output output_demo
```

正式答题时请实现 `candidate_spider.py`，不要只提交 demo spider。
