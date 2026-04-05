"""环境变量、本地配置文件与默认路径（见《03详细设计》§4.1）。"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

DEFAULT_CHROMA_PATH = "./chroma_db"
DEFAULT_LOG_PATH = "./logs/session.jsonl"
DEFAULT_ARK_MODEL = "doubao-seed-2-0-lite-260215"
DEFAULT_TOP_K = 5
COLLECTION_NAME = "food_retail_guide"


@dataclass(frozen=True)
class Config:
    ark_api_key: str
    chroma_path: str
    log_path: str
    ark_model: str
    top_k: int


def apply_local_env(env_file: Path | None = None) -> Path | None:
    """
    从单个 .env 格式文件加载键值到进程环境（不覆盖已存在的环境变量）。
    返回实际加载的文件路径；未加载任何文件时返回 None。
    """
    chosen: Path | None = None
    if env_file is not None:
        if env_file.is_file():
            chosen = env_file
    else:
        override = os.environ.get("PRODUCT_GUIDE_ENV_FILE")
        candidates: list[str] = []
        if override:
            candidates.append(override)
        candidates.extend(["config.local.env", ".env"])
        for raw in candidates:
            p = Path(raw)
            if p.is_file():
                chosen = p
                break
    if chosen is not None:
        load_dotenv(chosen, override=False)
    return chosen


def load_chroma_path(env_file: Path | None = None) -> str:
    """仅解析本地 env 与 CHROMA_PATH，不要求 ARK_API_KEY（供 stats / 对齐检查）。"""
    apply_local_env(env_file)
    return os.environ.get("CHROMA_PATH", DEFAULT_CHROMA_PATH)


def load_config(env_file: Path | None = None) -> Config:
    apply_local_env(env_file)
    key = os.environ.get("ARK_API_KEY")
    if not key or not str(key).strip():
        raise RuntimeError(
            "缺少 ARK_API_KEY：请设置环境变量，或复制 config.local.env.example 为 "
            "config.local.env 并填入密钥（该文件已加入 .gitignore）"
        )

    return Config(
        ark_api_key=str(key).strip(),
        chroma_path=os.environ.get("CHROMA_PATH", DEFAULT_CHROMA_PATH),
        log_path=os.environ.get("LOG_PATH", DEFAULT_LOG_PATH),
        ark_model=os.environ.get("ARK_MODEL", DEFAULT_ARK_MODEL),
        top_k=int(os.environ.get("TOP_K", str(DEFAULT_TOP_K))),
    )
