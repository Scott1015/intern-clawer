# PR 提交说明

拿到仓库地址后，请先 fork 本仓库到自己的 GitHub 账号。在自己的 fork 仓库里完成代码和数据输出，确认本地运行与校验通过后，把代码和 `output/` 数据结果一起 push 到自己的 fork，并向本仓库提交 Pull Request。

## 建议流程

```bash
git clone <your-fork-url>
cd intern-clawer
git checkout -b crawler-answer
cd candidate_starter
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python run.py --spider-module candidate_spider --seeds seeds.json --output output
python validate_output.py --output output
```

校验通过后提交：

```bash
cd ..
git status
git add candidate_starter/candidate_spider.py candidate_starter/output
git add <your-helper-files-if-any>
git commit -m "Complete crawler assignment"
git push origin crawler-answer
```

## PR 内容

PR 至少应包含：

- `candidate_starter/candidate_spider.py`
- 新增 helper 文件，如果有
- 对 `requirements.txt` 的必要修改，如果有新增依赖
- `candidate_starter/output/product_list.jsonl`
- `candidate_starter/output/spu.jsonl`
- `candidate_starter/output/skc.jsonl`
- `candidate_starter/output/sku.jsonl`
- `candidate_starter/output/run_summary.json`
- `candidate_starter/output/errors.jsonl`，如果存在失败

不要提交：

- `.venv/`
- `__pycache__/`
- `.pyc`
- 大型 HTML 抓包文件

## PR 描述模板

````markdown
## 运行命令

```bash
cd candidate_starter
python run.py --spider-module candidate_spider --seeds seeds.json --output output
python validate_output.py --output output
```

## 输出摘要

粘贴 `output/run_summary.json` 内容。

## 说明

- 商品发现方式：
- 详情数据来源：
- 已知限制：
````
