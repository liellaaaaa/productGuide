"""结构化数据入库：解析 → 写入 Chroma（见《03详细设计》§4.3、§6）。"""

from __future__ import annotations

import json
from pathlib import Path

from product_guide.config import Config
from product_guide.kb import upsert


def stable_row_id(item: dict, index: int) -> str:
    """与 run_ingest 写入 Chroma 的 id 规则一致。"""
    return str(item.get("id", f"row-{index}"))


def expected_ids_from_items(items: list[dict]) -> list[str]:
    return [stable_row_id(item, i) for i, item in enumerate(items)]


def load_items_from_json(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and "items" in data:
        return list(data["items"])
    raise ValueError(f"不支持的 JSON 结构: {path}")


def item_to_document(item: dict) -> str:
    """将单条结构化记录拼成可检索文本（可按业务扩展字段）。"""
    parts = []
    for key in ("name", "category", "price", "desc", "tags"):
        if key in item and item[key]:
            parts.append(f"{key}: {item[key]}")
    if not parts:
        return json.dumps(item, ensure_ascii=False)
    return "\n".join(parts)


def run_ingest(cfg: Config, data_path: Path) -> int:
    items = load_items_from_json(data_path)
    ids: list[str] = []
    documents: list[str] = []
    metadatas: list[dict] = []

    for i, item in enumerate(items):
        sid = stable_row_id(item, i)
        ids.append(sid)
        documents.append(item_to_document(item))
        metadatas.append({"source": data_path.name, "id": sid})

    if ids:
        upsert(cfg, ids=ids, documents=documents, metadatas=metadatas)
    return len(ids)
