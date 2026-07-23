# 独立站整站采集实战题

这是一个独立站商品采集练习仓库。拿到仓库地址后，请先 fork 到自己的 GitHub 账号下，在自己的 fork 仓库中完成指定站点的采集代码和数据输出。确认本地运行与校验通过后，把代码和 `output/` 数据结果一起 push 到自己的 fork，并向本仓库提交 Pull Request。

本题目标不是只解析几个商品详情页，而是完成一条可运行的采集链路：

1. 从给定的首页、类目页或集合页入口开始。
2. 解析列表页，发现商品详情页。
3. 支持必要的翻页、接口分页或下一页逻辑。
4. 解析商品详情页，产出 SPU/SKC/SKU 三层商品数据。
5. 按本仓库规定的 JSONL 格式输出到本地 `output/` 目录。

## 仓库结构

- `candidate_starter/TASK.md`：具体任务要求。
- `candidate_starter/candidate_spider.py`：主要答题文件。
- `candidate_starter/run.py`：统一运行入口。
- `candidate_starter/validate_output.py`：本地输出校验脚本。
- `candidate_starter/framework/`：轻量框架代码。
- `candidate_starter/examples/`：离线 demo，用于理解完整链路。
- `DATA_FORMAT.md`：输出字段规范。
- `SUBMISSION.md`：PR 提交要求。

## 从拿到题目到提交 PR

1. 收到本仓库地址后，先点击 GitHub 页面右上角的 Fork，把仓库复制到自己的 GitHub 账号下。
2. Clone 自己 fork 后的仓库到本地，不要直接在本仓库提交代码。
3. 在自己的仓库里新建答题分支，例如 `crawler-answer`。
4. 根据指定站点修改 `candidate_starter/seeds.json` 和 `candidate_starter/candidate_spider.py`，完成整站商品采集逻辑。
5. 在本地运行采集任务，确认生成 `candidate_starter/output/` 数据结果。
6. 运行校验脚本，确认输出格式通过。
7. 把采集代码、必要的 helper 文件、依赖变更和 `candidate_starter/output/` 数据结果一起提交并 push 到自己的 fork 仓库。
8. 从自己的 fork 仓库向本仓库提交 Pull Request，作为最终答案。

## 快速开始

```bash
git clone <your-fork-url>
cd intern-clawer
git checkout -b crawler-answer
cd candidate_starter
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python run.py --spider-module examples.static_shop_spider --seeds seeds.json --output output_demo
python validate_output.py --output output_demo
```

demo 通过后，实现 `candidate_spider.py`：

```bash
python run.py --spider-module candidate_spider --seeds seeds.json --output output
python validate_output.py --output output
```

## PR 需要包含

请提交一个 Pull Request，至少包含：

- 采集代码：`candidate_starter/candidate_spider.py`
- 如有必要，可以新增 helper 文件
- 数据结果：`candidate_starter/output/product_list.jsonl`
- 数据结果：`candidate_starter/output/spu.jsonl`
- 数据结果：`candidate_starter/output/skc.jsonl`
- 数据结果：`candidate_starter/output/sku.jsonl`
- 运行摘要：`candidate_starter/output/run_summary.json`
- 如果存在失败：`candidate_starter/output/errors.jsonl`
- PR 描述中写清楚运行命令和输出摘要

## 基本要求

- 必须实现列表页商品发现，产出 `product_list.jsonl`。
- 必须实现详情页解析，产出 `spu.jsonl`、`skc.jsonl`、`sku.jsonl`。
- 价格必须使用整数分，例如 `69.99` 输出 `6999`。
- 图片 URL 必须是绝对 URL。
- 图片列表字段必须是 JSON 数组。
- ID 必须稳定，不能使用随机数或当前时间。
- 代码不能只针对 demo 或单个商品硬编码。

详细字段见 [DATA_FORMAT.md](DATA_FORMAT.md)，提交要求见 [SUBMISSION.md](SUBMISSION.md)。
