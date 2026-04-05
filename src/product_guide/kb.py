"""Chroma 持久化与 top-k 检索（见《03详细设计》§4.2、§6）。"""

from __future__ import annotations

from typing import Any

import chromadb
from chromadb.config import Settings

from product_guide.config import COLLECTION_NAME, Config


def _client(chroma_path: str) -> chromadb.PersistentClient:
    return chromadb.PersistentClient(
        path=chroma_path,
        settings=Settings(anonymized_telemetry=False),
    )


def get_or_create_collection_for_path(chroma_path: str):
    """按持久化路径打开/创建集合（便于 stats 等仅依赖 Chroma 的场景）。"""
    client = _client(chroma_path)
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"description": "美食/超市导购知识库"},
    )


def get_or_create_collection(cfg: Config):
    return get_or_create_collection_for_path(cfg.chroma_path)


def list_stored_document_ids(chroma_path: str) -> list[str]:
    """返回当前集合中全部文档 id（与 ingest 写入的 id 一致）。"""
    collection = get_or_create_collection_for_path(chroma_path)
    res = collection.get(include=[])
    ids = res.get("ids") or []
    return sorted(ids, key=str)


def query(cfg: Config, text: str, n_results: int) -> list[str]:
    """对用户问题做相似度检索，返回文档文本列表。"""
    collection = get_or_create_collection(cfg)
    result = collection.query(
        query_texts=[text],
        n_results=n_results,
    )
    docs = result.get("documents") or []
    if not docs or not docs[0]:
        return []
    return list(docs[0])


def upsert(
    cfg: Config,
    ids: list[str],
    documents: list[str],
    metadatas: list[dict[str, Any]] | None = None,
) -> None:
    collection = get_or_create_collection(cfg)
    kwargs: dict[str, Any] = {"ids": ids, "documents": documents}
    if metadatas is not None:
        kwargs["metadatas"] = metadatas
    collection.upsert(**kwargs)
