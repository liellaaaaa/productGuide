"""system/user 提示词组装（见《03详细设计》§4.4、§5）。"""

from __future__ import annotations


SYSTEM_PROMPT = """你是结构化美食与超市商品导购助手。用户将提供一些从知识库检索到的片段，仅供参考；请结合常识给出清晰、可执行的导购建议。
若当前没有检索到直接相关内容，请如实说明，并仍可根据问题给出通用、安全的购买与搭配建议。"""


def build_messages(retrieved_chunks: list[str], user_question: str) -> list[dict]:
    if retrieved_chunks:
        ctx = "\n---\n".join(retrieved_chunks)
        user_content = f"【知识库检索片段】\n{ctx}\n\n【用户问题】\n{user_question}"
    else:
        user_content = (
            "【知识库检索片段】\n（当前知识库未检索到直接相关内容）\n\n"
            f"【用户问题】\n{user_question}"
        )

    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]
