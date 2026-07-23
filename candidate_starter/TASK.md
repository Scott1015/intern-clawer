# 笔试任务

## 目标

请完成一个独立站整站商品采集 spider，把 `seeds.json` 中给出的首页、类目页或集合页作为入口，采集出商品列表，并对商品详情页输出 SPU/SKC/SKU 三层数据。

## 目标站点

- 平台名：`replace_with_platform_region`
- 站点地址：`replace_with_site_homepage`
- 起始入口：见 `seeds.json`

## 必须实现

- `iter_category_seeds()`：确认采集入口，可以直接使用 `seeds.json`，也可以从首页解析导航生成类目入口。
- `parse_list()`：解析列表页或列表 API，发现商品详情页；如果有分页，需要处理至少前 2 页或题目要求页数。
- `parse_product()`：解析详情页，输出 SPU/SKC/SKU。

## 必采字段

详见仓库根目录的 `DATA_FORMAT.md`。也可以直接运行 `python validate_output.py --output output` 查看缺失字段。

## 采集范围

- 列表层必须输出 `product_list.jsonl`。
- 详情层必须采集商品标题、详情页 URL、主图、多图、品牌、描述、价格、币种。
- 必须按颜色/款式输出 SKC。
- 必须按尺码/规格输出 SKU；如果商品无尺码，输出一个 `sku_size = "no size"` 的 SKU。
- 库存字段能获取则输出，获取不到可以留空。

## 时间建议

建议 3-4 小时内完成。优先保证链路完整、数据结构正确、字段稳定、解析逻辑清晰，再考虑覆盖更多类目或边界情况。
