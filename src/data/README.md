# data 目录说明

- **`items.json`**：示例/可拷贝的真实结构化商品数据（体量小，可版本管理）。字段约定见仓库根目录 `README.md`。
- **与 Chroma 的关系**：运行时检索使用的是 **Chroma 持久化库**（默认 `./chroma_db`，见 `CHROMA_PATH`），不是直接读本目录。请将本目录 JSON 视为**源数据**，通过命令同步入库：

  ```bash
  python -m product_guide ingest
  python -m product_guide stats --data data/items.json
  ```

  第二条用于核对「JSON 中的 id」与「Chroma 中已入库文档 id」是否一致。

- **更新流程**：编辑 `items.json` → 再执行 `ingest`（当前实现对相同 id 为 upsert，可覆盖旧向量）。
