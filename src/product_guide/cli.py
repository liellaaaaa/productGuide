"""CLI 入口与子命令（见《03详细设计》§4.7、§10）。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from product_guide import __version__
from product_guide.ark_client import stream_chat
from product_guide.config import COLLECTION_NAME, load_chroma_path, load_config
from product_guide.ingest import (
    expected_ids_from_items,
    load_items_from_json,
    run_ingest,
)
from product_guide.json_log import append_record
from product_guide.kb import list_stored_document_ids, query
from product_guide.prompt import build_messages


def _cmd_chat(cfg, question: str | None) -> int:
    if question is None:
        try:
            question = input("问题: ").strip()
        except EOFError:
            return 0
    if not question:
        print("未输入问题。", file=sys.stderr)
        return 1

    chunks = query(cfg, question, n_results=cfg.top_k)
    messages = build_messages(chunks, question)

    parts: list[str] = []
    try:
        for piece in stream_chat(cfg, messages):
            print(piece, end="", flush=True)
            parts.append(piece)
    except Exception as e:  # noqa: BLE001 — CLI 层统一打印
        print(file=sys.stderr)
        print(f"Ark 调用失败: {e}", file=sys.stderr)
        return 1

    print()
    full = "".join(parts)
    append_record(
        Path(cfg.log_path),
        user_input=question,
        model_output=full,
        retrieval_summary=chunks,
        model=cfg.ark_model,
    )
    return 0


def _cmd_stats(env_file: Path | None, data_file: Path | None) -> int:
    """查看 Chroma 中条目；可选与 data 下 JSON 的 id 列表对齐检查（无需 ARK_API_KEY）。"""
    chroma_path = load_chroma_path(env_file)
    ids = list_stored_document_ids(chroma_path)
    print(f"Chroma 持久化路径: {chroma_path}")
    print(f"集合名: {COLLECTION_NAME}")
    print(f"条数: {len(ids)}")
    if ids:
        print("文档 id:", ", ".join(ids))
    else:
        print("提示: 集合为空，请先执行: python -m product_guide ingest")

    if data_file is not None:
        if not data_file.is_file():
            print(f"数据文件不存在，跳过对齐: {data_file}", file=sys.stderr)
            return 1
        items = load_items_from_json(data_file)
        expected = set(expected_ids_from_items(items))
        actual = set(ids)
        only_file = sorted(expected - actual)
        only_chroma = sorted(actual - expected)
        print()
        print(f"对齐文件: {data_file.resolve()}")
        print(f"  JSON 期望 id 数: {len(expected)}")
        if only_file:
            print(f"  仅在 JSON 中（未入库或 id 不一致）: {', '.join(only_file)}")
        if only_chroma:
            print(f"  仅在 Chroma 中（可能来自旧 ingest 或其它来源）: {', '.join(only_chroma)}")
        if not only_file and not only_chroma and expected:
            print("  与当前 JSON 的 id 集合一致。")
    return 0


def _cmd_ingest(cfg, data_file: Path) -> int:
    if not data_file.is_file():
        print(f"数据文件不存在: {data_file}", file=sys.stderr)
        return 1
    n = run_ingest(cfg, data_file)
    print(f"已入库 {n} 条。")
    return 0


def main(argv: list[str] | None = None) -> None:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        "--env-file",
        type=Path,
        default=None,
        metavar="PATH",
        help="本地 .env 格式配置；不配则依次尝试 $PRODUCT_GUIDE_ENV_FILE、config.local.env、.env",
    )

    # --env-file 仅挂在主解析器，用法：product_guide --env-file PATH chat ...
    parser = argparse.ArgumentParser(
        prog="product_guide",
        description="美食/超市商品导购助手（CLI + RAG）",
        parents=[common],
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p_chat = sub.add_parser("chat", help="检索并流式导购")
    p_chat.add_argument("-q", "--question", help="单次提问（缺省则交互读入一行）")

    p_ingest = sub.add_parser("ingest", help="将 data 下 JSON 写入 Chroma（向量库由 Chroma 持久化）")
    p_ingest.add_argument(
        "data_file",
        type=Path,
        nargs="?",
        default=Path("data/items.json"),
        help="数据文件路径（默认 data/items.json）",
    )

    p_stats = sub.add_parser(
        "stats",
        help="查看 Chroma 中条目数量与 id；可选与 JSON 对齐（不需要 ARK_API_KEY）",
    )
    p_stats.add_argument(
        "--data",
        type=Path,
        default=None,
        dest="data_file",
        metavar="PATH",
        help="若指定，则与 data/items.json 等同结构文件比对 id 是否一致",
    )

    args = parser.parse_args(argv)

    if args.command == "stats":
        raise SystemExit(_cmd_stats(args.env_file, args.data_file))

    try:
        cfg = load_config(env_file=args.env_file)
    except RuntimeError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)

    if args.command == "chat":
        raise SystemExit(_cmd_chat(cfg, args.question))
    if args.command == "ingest":
        raise SystemExit(_cmd_ingest(cfg, args.data_file))

    raise SystemExit(1)
