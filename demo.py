"""
Demo: 在 Python 中调用 StepFun 的 Anthropic 兼容 API（模型: step-router-v1）

依赖安装：pip install anthropic
"""

import anthropic

# ======================== 配置区域 ========================

API_KEY = "3NppV7aT7TcVDoURp24nPpBivUf9iKglNq64XLxGJRSEcnGNotonJXtZySRCasc1J"
BASE_URL = "https://api.stepfun.com/step_plan"
MODEL = "step-router-v1"
TIMEOUT_MS = 3_000_000  # 3000 秒

# =========================================================


def get_text(response) -> str:
    """从 response 中提取纯文本（跳过 ThinkingBlock）"""
    parts = []
    for block in response.content:
        if block.type == "text":
            parts.append(block.text)
        elif block.type == "thinking":
            # 可选：打印思考过程
            # print(f"[思考] {block.thinking}")
            pass
    return "\n".join(parts)


# 创建客户端
client = anthropic.Anthropic(
    api_key=API_KEY,
    base_url=BASE_URL,
    timeout=TIMEOUT_MS / 1000.0,
)

# ---- 示例 1：简单对话 ----
print("=" * 50)
print("示例 1：简单问答")
print("=" * 50)

response = client.messages.create(
    model=MODEL,
    max_tokens=512,
    messages=[
        {"role": "user", "content": "用一句话介绍 Python 语言"}
    ],
)

print(get_text(response))
print()

# ---- 示例 2：带 system prompt 的对话 ----
print("=" * 50)
print("示例 2：带 system prompt")
print("=" * 50)

response = client.messages.create(
    model=MODEL,
    max_tokens=512,
    system="你是一个 Python 技术专家，回答要简洁专业。",
    messages=[
        {"role": "user", "content": "Python 的 GIL 是什么？用两句话说明。"}
    ],
)

print(get_text(response))
print()

# ---- 示例 3：多轮对话 ----
print("=" * 50)
print("示例 3：多轮对话")
print("=" * 50)

response = client.messages.create(
    model=MODEL,
    max_tokens=512,
    messages=[
        {"role": "user", "content": "1+1=?"},
        {"role": "assistant", "content": "2"},
        {"role": "user", "content": "那再乘以 3 呢？"},
    ],
)

print(get_text(response))
print()

# ---- 示例 4：流式输出 ----
print("=" * 50)
print("示例 4：流式输出 (stream)")
print("=" * 50)

with client.messages.stream(
    model=MODEL,
    max_tokens=512,
    messages=[
        {"role": "user", "content": "写一首关于编程的五言绝句"}
    ],
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)

print("\n")
print("[OK] 所有示例执行完毕！")