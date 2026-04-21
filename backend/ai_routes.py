"""
AI-related API routes.

Mounted as a separate APIRouter to follow the open-closed principle —
existing app.py routes remain untouched.
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Optional

from fastapi import APIRouter, Depends, Query, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from subtitle_extractor import extract_subtitle
from ai_service import summarize_stream, chat_stream, check_api_available, test_api_connection
from database import get_db
from deps import get_optional_user, check_and_increment_usage, get_usage_quota
from models import User

logger = logging.getLogger("ai_routes")

router = APIRouter(prefix="/api/ai", tags=["AI"])


# ── Request models ───────────────────────────────────────

class SummarizeRequest(BaseModel):
    transcript: str
    title: str
    language: str = "zh"


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    transcript: str
    title: str
    messages: list[ChatMessage]


# ── Routes ───────────────────────────────────────────────

@router.get("/status")
async def ai_status():
    """Check whether the AI service is available."""
    available = check_api_available()
    return {"available": available}


@router.get("/check")
async def ai_check():
    """Test actual API connectivity and return diagnostics."""
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, test_api_connection)
    return result


@router.get("/quota")
async def ai_quota(
    request: Request,
    user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    """Return AI analysis usage quota for the current user/IP."""
    return get_usage_quota("ai_analysis", user, request, db)


@router.get("/subtitle")
async def get_subtitle(url: str = Query(..., description="Video page URL")):
    """Extract subtitle / transcript for a video (SSE with heartbeats).

    Whisper transcription for long videos can take 5-20+ minutes.
    Regular HTTP would timeout via proxies / browsers, so we stream
    periodic heartbeat events to keep the connection alive.
    """

    async def event_stream():
        loop = asyncio.get_event_loop()
        queue: asyncio.Queue = asyncio.Queue()

        def _run():
            try:
                result = extract_subtitle(url)
                loop.call_soon_threadsafe(queue.put_nowait, ("done", result))
            except Exception as e:
                logger.exception("Subtitle extraction failed")
                loop.call_soon_threadsafe(
                    queue.put_nowait, ("error", f"字幕提取失败: {str(e)[:200]}")
                )

        loop.run_in_executor(None, _run)

        while True:
            try:
                event_type, data = await asyncio.wait_for(queue.get(), timeout=10)
                if event_type == "done":
                    yield _sse("done", {"success": True, "data": data})
                    break
                elif event_type == "error":
                    yield _sse("error", {"success": False, "error": data})
                    break
            except asyncio.TimeoutError:
                yield _sse("heartbeat", {})

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.post("/summarize")
async def summarize_video(
    req: SummarizeRequest,
    request: Request,
    user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    """Stream a structured AI summary of the video content (SSE)."""
    if not check_api_available():
        raise HTTPException(
            status_code=503,
            detail={"success": False, "error": "AI 服务未配置，请在 .env 中设置 AI_API_KEY"},
        )

    check_and_increment_usage("ai_analysis", user, request, db)

    async def event_stream():
        loop = asyncio.get_event_loop()
        queue: asyncio.Queue = asyncio.Queue()
        accumulated = ""

        def _run_summarize():
            try:
                for chunk in summarize_stream(req.transcript, req.title, req.language):
                    loop.call_soon_threadsafe(queue.put_nowait, ("chunk", chunk))
                loop.call_soon_threadsafe(queue.put_nowait, ("done", ""))
            except Exception as e:
                logger.exception("Summarize stream error")
                loop.call_soon_threadsafe(
                    queue.put_nowait, ("error", str(e)[:200])
                )

        loop.run_in_executor(None, _run_summarize)

        while True:
            try:
                event_type, data = await asyncio.wait_for(queue.get(), timeout=120)
            except asyncio.TimeoutError:
                yield _sse("ping", {})
                continue

            if event_type == "chunk":
                accumulated += data
                yield _sse("chunk", {"content": data})
            elif event_type == "done":
                yield _sse("done", {"full_content": accumulated})
                break
            elif event_type == "error":
                yield _sse("error", {"message": data})
                break

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.post("/chat")
async def chat_with_video(
    req: ChatRequest,
    request: Request,
    user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    """Stream an AI chat response about video content (SSE)."""
    if not check_api_available():
        raise HTTPException(
            status_code=503,
            detail={"success": False, "error": "AI 服务未配置，请在 .env 中设置 AI_API_KEY"},
        )

    check_and_increment_usage("ai_analysis", user, request, db)

    messages = [{"role": m.role, "content": m.content} for m in req.messages]

    async def event_stream():
        loop = asyncio.get_event_loop()
        queue: asyncio.Queue = asyncio.Queue()
        accumulated = ""

        def _run_chat():
            try:
                for chunk in chat_stream(req.transcript, req.title, messages):
                    loop.call_soon_threadsafe(queue.put_nowait, ("chunk", chunk))
                loop.call_soon_threadsafe(queue.put_nowait, ("done", ""))
            except Exception as e:
                logger.exception("Chat stream error")
                loop.call_soon_threadsafe(
                    queue.put_nowait, ("error", str(e)[:200])
                )

        loop.run_in_executor(None, _run_chat)

        while True:
            try:
                event_type, data = await asyncio.wait_for(queue.get(), timeout=120)
            except asyncio.TimeoutError:
                yield _sse("ping", {})
                continue

            if event_type == "chunk":
                accumulated += data
                yield _sse("chunk", {"content": data})
            elif event_type == "done":
                yield _sse("done", {"full_content": accumulated})
                break
            elif event_type == "error":
                yield _sse("error", {"message": data})
                break

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ── Helpers ──────────────────────────────────────────────

def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"
