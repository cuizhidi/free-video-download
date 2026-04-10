from dotenv import load_dotenv
load_dotenv()

import asyncio
import json
import os
import time
from contextlib import asynccontextmanager
from pathlib import Path
from urllib.parse import urlparse

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse, Response
from fastapi.staticfiles import StaticFiles

from downloader import VideoDownloader, DOWNLOAD_DIR

TEMP_FILE_MAX_AGE = 30 * 60  # 30 minutes

downloader = VideoDownloader()


def cleanup_old_files():
    """Remove temp files older than TEMP_FILE_MAX_AGE seconds."""
    now = time.time()
    for f in DOWNLOAD_DIR.iterdir():
        if f.is_file() and now - f.stat().st_mtime > TEMP_FILE_MAX_AGE:
            f.unlink(missing_ok=True)


async def periodic_cleanup():
    """Background task: clean temp files every 10 minutes."""
    while True:
        await asyncio.sleep(600)
        cleanup_old_files()


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(periodic_cleanup())
    yield
    task.cancel()


app = FastAPI(title="Free Video Download API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ------------------------------------------------------------------
# API Routes
# ------------------------------------------------------------------

@app.get("/api/parse")
async def parse_video(url: str = Query(..., description="Video page URL")):
    """Parse video info without downloading."""
    try:
        loop = asyncio.get_event_loop()
        info = await loop.run_in_executor(None, downloader.parse_video, url)
        return {"success": True, "data": info}
    except Exception as e:
        error_msg = str(e)
        lower_msg = error_msg.lower()
        if "Unsupported URL" in error_msg:
            code = "UNSUPPORTED"
            msg = "暂不支持该平台，请检查链接"
        elif "Video unavailable" in error_msg or "not available" in lower_msg:
            code = "NOT_FOUND"
            msg = "视频不存在或已被删除"
        elif "login" in lower_msg or "sign in" in lower_msg:
            code = "AUTH_REQUIRED"
            msg = "该视频需要登录才能访问"
        elif "cookie" in lower_msg or "fresh cookies" in lower_msg:
            code = "COOKIES_NEEDED"
            msg = "该平台需要浏览器 cookies 才能访问，请联系管理员配置"
        elif "geo" in lower_msg or "country" in lower_msg:
            code = "GEO_BLOCKED"
            msg = "该视频在当前地区不可用"
        elif "无法" in error_msg or "未找到" in error_msg:
            code = "PARSE_FAILED"
            msg = error_msg
        else:
            code = "PARSE_FAILED"
            msg = "解析失败，请检查链接是否正确"
        raise HTTPException(status_code=400, detail={"success": False, "error": msg, "error_code": code})


@app.get("/api/download")
async def download_video(
    url: str = Query(...),
    format_id: str = Query(...),
):
    """Download video with SSE progress updates."""

    async def event_stream():
        queue: asyncio.Queue = asyncio.Queue()
        loop = asyncio.get_event_loop()
        is_direct_url = format_id.startswith("http")
        needs_merge = not is_direct_url and "+" in format_id
        download_phase = {"current": 0}  # 0=video, 1=audio for merge scenarios

        def progress_hook(d):
            if d["status"] == "downloading":
                total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
                downloaded = d.get("downloaded_bytes") or 0
                raw_pct = (downloaded / total * 100) if total else 0

                if needs_merge:
                    phase = download_phase["current"]
                    percent = round(raw_pct * 0.45 + phase * 45, 1)
                else:
                    percent = round(raw_pct * 0.9, 1)

                speed = d.get("_speed_str", "").strip()
                eta = d.get("_eta_str", "").strip()
                loop.call_soon_threadsafe(
                    queue.put_nowait,
                    ("progress", {"status": "downloading", "percent": min(percent, 95), "speed": speed, "eta": eta}),
                )
            elif d["status"] == "finished":
                if needs_merge and download_phase["current"] == 0:
                    download_phase["current"] = 1
                    loop.call_soon_threadsafe(
                        queue.put_nowait,
                        ("progress", {"status": "downloading", "percent": 45}),
                    )
                else:
                    loop.call_soon_threadsafe(
                        queue.put_nowait,
                        ("progress", {"status": "processing", "percent": 95}),
                    )

        def do_download():
            return downloader.download_video(url, format_id, progress_hook)

        async def run_download():
            try:
                filename = await loop.run_in_executor(None, do_download)
                if filename:
                    filepath = DOWNLOAD_DIR / filename
                    filesize = filepath.stat().st_size if filepath.exists() else 0
                    await queue.put(("complete", {"status": "done", "filename": filename, "filesize": filesize}))
                else:
                    await queue.put(("error", {"status": "error", "message": "下载完成但未找到文件"}))
            except Exception as e:
                await queue.put(("error", {"status": "error", "message": str(e)[:200]}))

        task = asyncio.create_task(run_download())

        while True:
            try:
                event, data = await asyncio.wait_for(queue.get(), timeout=30)
                yield f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"
                if event in ("complete", "error"):
                    break
            except asyncio.TimeoutError:
                yield "event: ping\ndata: {}\n\n"

        await task

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.get("/api/proxy-image")
async def proxy_image(url: str = Query(..., description="Image URL to proxy")):
    """Proxy an image to bypass Referer restrictions."""
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise HTTPException(status_code=400, detail="Invalid URL")

    import urllib.request

    loop = asyncio.get_event_loop()

    def fetch():
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": f"{parsed.scheme}://{parsed.netloc}/",
        })
        with urllib.request.urlopen(req, timeout=10) as resp:
            content_type = resp.headers.get("Content-Type", "image/jpeg")
            data = resp.read()
        return data, content_type

    try:
        data, content_type = await loop.run_in_executor(None, fetch)
        return Response(
            content=data,
            media_type=content_type,
            headers={"Cache-Control": "public, max-age=3600"},
        )
    except Exception:
        raise HTTPException(status_code=502, detail="Failed to fetch image")


@app.get("/api/file/{filename}")
async def get_file(filename: str):
    """Serve a downloaded file."""
    filepath = DOWNLOAD_DIR / filename
    if not filepath.exists() or not filepath.is_file():
        raise HTTPException(status_code=404, detail="文件不存在或已过期")
    return FileResponse(
        path=str(filepath),
        filename=filename,
        media_type="application/octet-stream",
    )


# ------------------------------------------------------------------
# AI Routes (video summarization, chat, subtitles)
# ------------------------------------------------------------------

from ai_routes import router as ai_router  # noqa: E402
app.include_router(ai_router)


# ------------------------------------------------------------------
# Production: serve Vue frontend static files
# ------------------------------------------------------------------

FRONTEND_DIST = Path(__file__).parent.parent / "frontend" / "dist"
if FRONTEND_DIST.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIST), html=True), name="static")
