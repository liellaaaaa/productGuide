"""JSON Lines 交互日志（见《03详细设计》§4.6、§7）。"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


def append_record(
    log_path: Path,
    *,
    user_input: str,
    model_output: str,
    retrieval_summary: list[str] | str | None = None,
    model: str | None = None,
) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).isoformat()
    if isinstance(retrieval_summary, list):
        ret = retrieval_summary
    elif retrieval_summary:
        ret = retrieval_summary
    else:
        ret = []

    record: dict = {
        "ts": ts,
        "user_input": user_input,
        "model_output": model_output,
        "retrieval_summary": ret,
    }
    if model:
        record["model"] = model

    line = json.dumps(record, ensure_ascii=False) + "\n"
    with log_path.open("a", encoding="utf-8") as f:
        f.write(line)
