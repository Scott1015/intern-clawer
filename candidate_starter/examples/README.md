# Demo

静态 demo 用于确认框架可运行，不代表正式题目答案。

它模拟完整链路：

1. 从 `examples/fixtures/category.html` 解析商品列表。
2. 发现两个商品详情 seed。
3. 读取两个商品详情 fixture。
4. 输出 `product_list.jsonl`、`spu.jsonl`、`skc.jsonl`、`sku.jsonl`。

```bash
python run.py --spider-module examples.static_shop_spider --seeds seeds.json --output output_demo
python validate_output.py --output output_demo
```

正式答题时，请实现根目录下的 `candidate_spider.py`。
