"""火山 Ark 流式调用（见《01需求文档》FR-3、《03详细设计》§4.5）。"""

from __future__ import annotations

from collections.abc import Iterator

from volcenginesdkarkruntime import Ark

from product_guide.config import Config


def stream_chat(cfg: Config, messages: list[dict]) -> Iterator[str]:
    client = Ark(api_key=cfg.ark_api_key)
    stream = client.chat.completions.create(
        model=cfg.ark_model,
        messages=messages,
        stream=True,
    )
    for chunk in stream:
        choices = getattr(chunk, "choices", None) or []
        if not choices:
            continue
        delta = getattr(choices[0], "delta", None)
        if delta is None:
            continue
        content = getattr(delta, "content", None)
        if not content:
            continue
        yield content
