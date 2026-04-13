"""
AI service module — OpenAI-compatible API integration (DeepSeek, SiliconFlow, etc.).

Provides:
- summarize_stream(): structured video summary (SSE streaming)
- chat_stream(): multi-turn Q&A about video content (SSE streaming)

Configure via environment variables in .env:
  AI_BASE_URL  — API base URL (default: https://api.siliconflow.cn/v1)
  AI_API_KEY   — API key (required)
  AI_MODEL     — model name (default: deepseek-ai/DeepSeek-V3)
  AI_MAX_TOKENS — max output tokens (default: 16384; increase for reasoning models)
"""

from __future__ import annotations

import logging
import os
from typing import Generator

import httpx
from openai import OpenAI

logger = logging.getLogger("ai_service")

_MAX_TRANSCRIPT_CHARS = 60000

_SUMMARIZE_SYSTEM_PROMPT = """\
你是一位专业的视频内容分析师。用户会提供一段视频的字幕/转录文本，你需要对视频内容进行全面分析。

请严格按照以下JSON格式输出，不要输出任何JSON之外的内容：

{
  "summary": "使用 Markdown 格式的视频摘要（见下方详细说明）",
  "chapters": [
    {
      "title": "章节标题",
      "start_time": "对应的大致起始时间(如 00:00)",
      "summary": "该章节的核心内容概括，1-2句话"
    }
  ],
  "key_points": [
    {
      "point": "知识要点标题",
      "detail": "详细说明，2-3句话"
    }
  ],
  "mindmap": "# 视频主题标题\\n## 一级主题1\\n### 二级要点1\\n### 二级要点2\\n## 一级主题2\\n### 二级要点1\\n### 二级要点2"
}

要求：
1. summary 字段必须使用 Markdown 格式，用 ## 标题将内容分为多个段落，用 **加粗** 强调关键术语，用列表 - 列举核心要点，总字数 200-400 字。示例结构：
   "## 视频概述\\n简要介绍...\\n\\n## 核心内容\\n- **要点1**：说明...\\n- **要点2**：说明...\\n\\n## 总结\\n结论..."
   注意：在JSON字符串中，换行必须写成 \\n
2. chapters 按视频时间线划分，至少3个章节，根据字幕时间戳推断大致时间
3. key_points 提取5-10个核心知识点
4. mindmap 用Markdown层级标题格式输出，用于生成思维导图，层级不超过4级
5. 如果视频语言非中文，请用中文输出分析结果
6. 确保输出是合法的JSON格式"""

_CHAT_SYSTEM_PROMPT = """\
你是一位智能视频助手。用户会基于一段视频内容向你提问，你需要根据视频的字幕/转录文本来回答。

你的回答要求：
1. 基于视频内容准确回答，如果视频中没有相关信息，请如实说明
2. 回答简洁清晰，使用中文
3. 如有必要可以引用视频中的具体内容或时间点
4. 保持友好和专业的语气"""


def _get_config() -> tuple[str, str, str]:
    """Return (base_url, api_key, model) from environment."""
    base_url = os.getenv("AI_BASE_URL", "").strip()
    api_key = os.getenv("AI_API_KEY", "").strip()
    model = os.getenv("AI_MODEL", "").strip()

    # Backward compat: fall back to legacy DEEPSEEK_* vars
    if not api_key:
        api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    if not base_url:
        base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.siliconflow.cn/v1").strip()
    if not model:
        model = os.getenv("DEEPSEEK_MODEL", "deepseek-ai/DeepSeek-V3").strip()

    return base_url, api_key, model


def _get_client() -> tuple[OpenAI, str]:
    """Return (client, model_name)."""
    base_url, api_key, model = _get_config()
    if not api_key:
        raise RuntimeError("未配置 AI API Key，请在 .env 中设置 AI_API_KEY 或 DEEPSEEK_API_KEY")
    http_client = httpx.Client(verify=False, timeout=120.0)
    client = OpenAI(api_key=api_key, base_url=base_url, http_client=http_client)
    return client, model


def _truncate_transcript(transcript: str) -> str:
    if len(transcript) <= _MAX_TRANSCRIPT_CHARS:
        return transcript
    return transcript[:_MAX_TRANSCRIPT_CHARS] + "\n\n[注意：转录文本过长，已截取前部分内容]"


def summarize_stream(
    transcript: str,
    title: str,
    language: str = "zh",
) -> Generator[str, None, None]:
    """Stream a structured video summary. Yields raw text chunks."""
    client, model = _get_client()
    transcript = _truncate_transcript(transcript)

    user_content = (
        f"视频标题：{title}\n"
        f"视频语言：{language}\n\n"
        f"以下是视频的字幕/转录文本：\n\n{transcript}"
    )

    max_tokens = int(os.getenv("AI_MAX_TOKENS", "16384"))
    logger.info("Calling AI API: base_url=%s, model=%s, max_tokens=%d", client.base_url, model, max_tokens)

    stream = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": _SUMMARIZE_SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
        stream=True,
        temperature=0.3,
        max_tokens=max_tokens,
    )

    content_chunks = 0
    for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content:
            content_chunks += 1
            yield chunk.choices[0].delta.content
    logger.info("Summarize stream finished: %d content chunks yielded", content_chunks)


def chat_stream(
    transcript: str,
    title: str,
    messages: list[dict],
) -> Generator[str, None, None]:
    """Stream an AI chat response about video content. Yields raw text chunks."""
    client, model = _get_client()
    transcript = _truncate_transcript(transcript)

    system_msg = (
        f"{_CHAT_SYSTEM_PROMPT}\n\n"
        f"--- 视频信息 ---\n"
        f"标题：{title}\n\n"
        f"字幕/转录文本：\n{transcript}"
    )

    api_messages = [{"role": "system", "content": system_msg}]
    for msg in messages:
        api_messages.append({
            "role": msg.get("role", "user"),
            "content": msg.get("content", ""),
        })

    max_tokens = int(os.getenv("AI_MAX_TOKENS", "16384"))

    stream = client.chat.completions.create(
        model=model,
        messages=api_messages,
        stream=True,
        temperature=0.5,
        max_tokens=max_tokens,
    )

    for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content


def check_api_available() -> bool:
    """Check if AI API key is configured."""
    _, api_key, _ = _get_config()
    return bool(api_key)


def test_api_connection() -> dict:
    """Test actual connectivity to the AI API. Returns diagnostic info."""
    base_url, api_key, model = _get_config()
    result = {
        "configured": bool(api_key),
        "base_url": base_url,
        "model": model,
        "connected": False,
        "error": None,
    }
    if not api_key:
        result["error"] = "未配置 API Key"
        return result
    try:
        client, model = _get_client()
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "hi"}],
            max_tokens=5,
        )
        result["connected"] = True
        result["test_response"] = resp.choices[0].message.content if resp.choices else ""
    except Exception as e:
        err_msg = str(e)[:300]
        if "<!DOCTYPE html>" in err_msg or "blocked" in err_msg.lower():
            result["error"] = f"API 被网络防火墙拦截，请更换网络或配置代理。当前 base_url: {base_url}"
        else:
            result["error"] = f"API 连接失败: {err_msg}"
    return result
