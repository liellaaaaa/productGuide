# productGuide

美食/超市商品导购助手（Python CLI + Chroma RAG + 豆包 Ark）。

## 仓库结构（简要）

| 路径 | 作用 |
|------|------|
| `src/product_guide/` | 可安装包：CLI、Chroma 封装、入库、Ark 流式调用、JSON 日志 |
| `data/` | **源数据**（如 `items.json`），体量小，可拷贝真实业务数据并纳入版本库 |
| `chroma_db/`（默认） | **向量库持久化目录**（Chroma），由 `ingest` 生成；已在 `.gitignore`，不提交 |
| `logs/` | JSON Lines 交互日志（默认 `./logs/session.jsonl`） |
| `config.local.env.example` | 本地密钥模板；复制为 `config.local.env`（已忽略） |

**数据与向量库对齐**：检索只读 Chroma。更新 `data/items.json` 后需重新执行 `ingest`。可用下列命令核对 id 是否一致（**不需要** `ARK_API_KEY`）：

```bash
python -m product_guide stats --data data/items.json
```

## 环境

- Python ≥ 3.10  
- 依赖：`requirements.txt` 与 `pyproject.toml` 已对齐（含 `chromadb`、`volcengine-python-sdk[ark]`、`python-dotenv`）。  
- 安装：`pip install -e .` 或 `pip install -r requirements.txt`

## 配置与密钥

1. 复制 `config.local.env.example` 为 **`config.local.env`**，填写 `ARK_API_KEY`。  
2. **`config.local.env` 已加入 `.gitignore`，勿提交。**  
3. 若已设置系统环境变量 `ARK_API_KEY`，其优先级**高于**文件中的值（`python-dotenv` 默认不覆盖已有环境变量）。  
4. 可选：通过环境变量 `PRODUCT_GUIDE_ENV_FILE` 指定其它 `.env` 文件路径；或在命令行使用  
   `python -m product_guide --env-file PATH chat ...`（`--env-file` 须写在子命令前）。

## 运行

```bash
# 1. 将 data 源数据写入 Chroma（向量库）
python -m product_guide ingest

# 2. 可选：核对 JSON 与 Chroma 文档 id
python -m product_guide stats --data data/items.json

# 3. 对话（需有效 ARK_API_KEY）
python -m product_guide chat -q "乳糖不耐早餐想喝点什么？有植物基推荐吗？"
```

向量库目录默认 `./chroma_db`，日志默认 `./logs/session.jsonl`，详见 `config.local.env.example` 注释。

## 基于示例 `data/items.json` 的提问示例

以下问题与当前示例条目（燕麦奶、全麦吐司、希腊酸奶）及字段（乳糖不耐、低糖、早餐、素食、轻食等）对应，便于验证检索 + 生成链路：

1. 乳糖不耐又想喝点什么，早餐有什么植物基饮品推荐？  
2. 全麦吐司价格多少？适合关注控糖的人吗？  
3. 想凑一顿简单早餐：燕麦奶和全麦吐司怎么搭配比较合理？  
4. 有没有高蛋白、适合搭配水果的乳品可以当轻食？  
5. 标注「素食」的商品有哪些，适合早餐场景吗？
