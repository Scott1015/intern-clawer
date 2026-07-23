# 输出字段规范

运行完成后，`output/` 目录应包含：

- `product_list.jsonl`
- `spu.jsonl`
- `skc.jsonl`
- `sku.jsonl`
- `run_summary.json`
- `errors.jsonl`，仅当存在失败时生成

JSONL 文件要求每行是一条 JSON。

## product_list.jsonl

列表页或接口中发现的商品详情 seed。

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| `product_url` | 是 | 商品详情页绝对 URL |
| `product_id` | 建议 | 商品稳定 ID |
| `product_name` | 建议 | 商品标题 |
| `category_id` | 建议 | 来源类目 ID |
| `category_name` | 建议 | 来源类目名称 |

## spu.jsonl

SPU 表示商品主粒度。

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| `platform` | 是 | 平台名，格式建议 `brand_region` |
| `version` | 是 | 运行批次，框架自动填充 |
| `spu_id` | 是 | 商品主 ID，必须稳定 |
| `spu_product_title` | 是 | 商品标题 |
| `spu_detail_page_url` | 是 | 商品详情页 URL |
| `spu_main_image_url` | 是 | 主图绝对 URL |
| `spu_pic_list` | 是 | 图片绝对 URL 数组 |
| `spu_discounted_price` | 是 | 当前价，整数分 |
| `spu_currency_unit` | 是 | 三位大写币种，如 `GBP` |
| `spu_brand_info` | 建议 | 品牌 |
| `spu_detail_description` | 建议 | 商品描述 |
| `spu_through_price` | 否 | 划线价，整数分或空 |

## skc.jsonl

SKC 通常表示颜色、款式或商品颜色粒度。

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| `platform` | 是 | 平台名 |
| `version` | 是 | 运行批次 |
| `spu_id` | 是 | 关联 SPU |
| `skc_id` | 是 | 颜色/款式 ID，必须稳定 |
| `skc_color` | 是 | 颜色名或款式名 |
| `skc_product_title` | 是 | 商品标题 |
| `skc_detail_page_url` | 是 | 颜色/款式详情页 URL |
| `skc_main_image_url` | 是 | SKC 主图绝对 URL |
| `skc_pic_list` | 是 | SKC 图片绝对 URL 数组 |
| `skc_discounted_price` | 是 | 当前价，整数分 |
| `skc_currency_unit` | 是 | 三位大写币种 |
| `skc_through_price` | 否 | 划线价，整数分或空 |

## sku.jsonl

SKU 通常表示尺码、规格或可购买最小粒度。

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| `platform` | 是 | 平台名 |
| `version` | 是 | 运行批次 |
| `spu_id` | 是 | 关联 SPU |
| `skc_id` | 是 | 关联 SKC |
| `sku_id` | 是 | SKU ID，必须稳定 |
| `sku_size` | 是 | 尺码；无尺码时填 `no size` |
| `sku_image_url` | 是 | SKU 图片绝对 URL |
| `sku_discounted_price` | 是 | 当前价，整数分 |
| `sku_currency_unit` | 是 | 三位大写币种 |
| `sku_through_price` | 否 | 划线价，整数分或空 |
| `sku_stock_status` | 否 | 库存状态 |
| `sku_stock_count` | 否 | 库存数 |

## 价格要求

- 一律输出整数分，不输出浮点数。
- `69.99` 输出 `6999`。
- 无划线价时，`*_through_price` 可以为空字符串或 `null`。
- 当前价 `*_discounted_price` 必须大于 0。

## ID 要求

- `spu_id` 应来自站点真实商品 ID；如果站点无显式 ID，可使用 canonical URL slug 或稳定 hash。
- `skc_id` 建议由 `spu_id + "_" + color_id` 组成。
- `sku_id` 建议由 `skc_id + "_" + size` 组成。
- 禁止使用随机数或当前时间拼 ID。
