"""
Dedicated Douyin video parser & downloader.

Bypasses yt-dlp by calling Douyin's public API (iesdouyin.com) directly.
No cookies or login required.

Reference: rathodpratham-dev/douyin_video_downloader (MIT License, 2026)
"""

from __future__ import annotations

import base64
import json
import logging
import re
import time
import uuid
from hashlib import sha256
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import requests

DOWNLOAD_DIR = Path(__file__).parent / "downloads"
DOWNLOAD_DIR.mkdir(exist_ok=True)

logger = logging.getLogger("douyin")

_DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/json,*/*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Connection": "keep-alive",
    "Referer": "https://www.douyin.com/",
}

_MOBILE_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 "
        "Mobile/15E148 Safari/604.1"
    ),
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Referer": "https://www.douyin.com/",
}

_API_URL = "https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/"
_URL_RE = re.compile(r"https?://[^\s]+", re.IGNORECASE)
_RETRYABLE = {429, 500, 502, 503, 504}


class DouyinError(Exception):
    pass


# ──────────────────────────────────────────────
# URL detection
# ──────────────────────────────────────────────

def is_douyin_url(url: str) -> bool:
    """Return True if *url* points to a Douyin video."""
    host = urlparse(url).netloc.lower()
    return any(d in host for d in ("douyin.com", "iesdouyin.com"))


# ──────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────

def parse_video(url: str) -> dict:
    """Parse Douyin video metadata. Returns normalised dict compatible with
    the main VideoDownloader format."""
    session = requests.Session()
    session.headers.update(_DEFAULT_HEADERS)

    try:
        share_url = _extract_first_url(url)

        # Try extracting video ID directly from the URL first (long links)
        video_id = _try_extract_video_id(share_url)
        if video_id:
            resolved = share_url
        else:
            # Short link — resolve via 302 redirect
            resolved = _resolve_redirect(session, share_url)
            video_id = _try_extract_video_id(resolved)
            if not video_id:
                raise DouyinError("无法从链接中提取视频 ID，短链接可能已过期")

        item = _fetch_item_info(session, video_id, resolved)
        return _normalise(item, video_id)
    finally:
        session.close()


def download_video(url: str, format_id: str, progress_hook=None) -> str | None:
    """Download a Douyin video. *format_id* is the direct video URL encoded
    by `parse_video`.  Returns the local filename."""
    session = requests.Session()
    session.headers.update(_DEFAULT_HEADERS)

    file_id = str(uuid.uuid4())[:8]
    out_path = DOWNLOAD_DIR / f"{file_id}.mp4"
    temp_path = out_path.with_suffix(".mp4.part")

    try:
        with session.get(
            format_id,
            stream=True,
            timeout=(10, 60),
            allow_redirects=True,
        ) as resp:
            resp.raise_for_status()
            total = int(resp.headers.get("Content-Length") or 0)
            downloaded = 0
            with temp_path.open("wb") as fp:
                for chunk in resp.iter_content(65536):
                    if not chunk:
                        continue
                    fp.write(chunk)
                    downloaded += len(chunk)
                    if progress_hook:
                        progress_hook({
                            "status": "downloading",
                            "downloaded_bytes": downloaded,
                            "total_bytes": total,
                        })

        temp_path.replace(out_path)
        if progress_hook:
            progress_hook({"status": "finished"})
        return out_path.name
    except Exception:
        temp_path.unlink(missing_ok=True)
        raise
    finally:
        session.close()


# ──────────────────────────────────────────────
# Internal helpers
# ──────────────────────────────────────────────

def _extract_first_url(text: str) -> str:
    m = _URL_RE.search(text)
    if not m:
        raise DouyinError("输入中未找到有效链接")
    return m.group(0).strip().strip("\"'").rstrip(").,;!?")


def _resolve_redirect(session: requests.Session, share_url: str, retries: int = 3) -> str:
    last_err = None
    for attempt in range(1, retries + 1):
        try:
            resp = session.get(share_url, timeout=(10, 15), allow_redirects=True)
            resp.raise_for_status()
            if resp.url:
                return resp.url
        except requests.RequestException as e:
            last_err = e
            if attempt < retries:
                time.sleep(1.0 * (2 ** (attempt - 1)))
    raise DouyinError("无法解析抖音分享链接") from last_err


def _try_extract_video_id(url: str) -> str | None:
    """Try to extract a Douyin video ID from *url*. Returns None on failure."""
    parsed = urlparse(url)
    qs = parse_qs(parsed.query)

    for key in ("modal_id", "item_ids", "group_id", "aweme_id"):
        vals = qs.get(key)
        if vals:
            m = re.search(r"(\d{8,24})", vals[0])
            if m:
                return m.group(1)

    for pat in (r"/video/(\d{8,24})", r"/note/(\d{8,24})", r"/(\d{8,24})(?:/|$)"):
        m = re.search(pat, parsed.path)
        if m:
            return m.group(1)

    m = re.search(r"(\d{15,24})", url)
    if m:
        return m.group(1)

    return None


# ──── Item info fetching ────

def _fetch_item_info(session: requests.Session, video_id: str, resolved_url: str) -> dict:
    try:
        data = _api_get_json(session, _API_URL, params={"item_ids": video_id})
        items = data.get("item_list") or []
        if items:
            return items[0]
    except DouyinError:
        pass

    logger.info("Public API unavailable for %s, falling back to share page", video_id)
    return _fetch_from_share_page(session, video_id, resolved_url)


def _api_get_json(session: requests.Session, url: str, params: dict, retries: int = 3) -> dict:
    last_err = None
    for attempt in range(1, retries + 1):
        try:
            resp = session.get(url, params=params, timeout=(10, 30))
            if resp.status_code in _RETRYABLE:
                raise requests.HTTPError(f"HTTP {resp.status_code}", response=resp)
            resp.raise_for_status()
            if not resp.content:
                raise ValueError("Empty response")
            return resp.json()
        except (requests.RequestException, ValueError) as e:
            last_err = e
            if attempt < retries:
                time.sleep(1.0 * (2 ** (attempt - 1)))
    raise DouyinError("抖音 API 请求失败") from last_err


# ──── Share page fallback ────

def _fetch_from_share_page(session: requests.Session, video_id: str, resolved_url: str) -> dict:
    parsed = urlparse(resolved_url)
    if parsed.netloc and "iesdouyin.com" in parsed.netloc:
        share_url = resolved_url
    else:
        share_url = f"https://www.iesdouyin.com/share/video/{video_id}/"

    resp = session.get(share_url, headers=_MOBILE_HEADERS, timeout=(10, 30))
    resp.raise_for_status()
    html = resp.text or ""

    if _is_waf_challenge(html):
        if _solve_waf(session, html, share_url):
            resp = session.get(share_url, headers=_MOBILE_HEADERS, timeout=(10, 30))
            resp.raise_for_status()
            html = resp.text or ""

    router = _extract_router_data(html)
    if not router:
        raise DouyinError("无法从分享页提取视频数据")

    loader = router.get("loaderData", {})
    for node in loader.values():
        if not isinstance(node, dict):
            continue
        items = node.get("videoInfoRes", {}).get("item_list", [])
        if items and isinstance(items[0], dict):
            return items[0]

    raise DouyinError("分享页中未找到视频信息")


def _is_waf_challenge(html: str) -> bool:
    return "Please wait..." in html and "wci=" in html and "cs=" in html


def _solve_waf(session: requests.Session, html: str, page_url: str) -> bool:
    m = re.search(r'wci="([^"]+)"\s*,\s*cs="([^"]+)"', html)
    if not m:
        return False
    cookie_name, challenge_blob = m.groups()

    try:
        challenge = json.loads(_b64dec(challenge_blob).decode())
        prefix = _b64dec(challenge["v"]["a"])
        expected = _b64dec(challenge["v"]["c"]).hex()
    except (KeyError, ValueError, TypeError):
        return False

    solved = None
    for i in range(1_000_001):
        if sha256(prefix + str(i).encode()).hexdigest() == expected:
            solved = i
            break
    if solved is None:
        return False

    challenge["d"] = base64.b64encode(str(solved).encode()).decode()
    cookie_val = base64.b64encode(
        json.dumps(challenge, separators=(",", ":")).encode()
    ).decode()
    domain = urlparse(page_url).hostname or "www.iesdouyin.com"
    session.cookies.set(cookie_name, cookie_val, domain=domain, path="/")
    logger.info("Solved WAF challenge for %s", domain)
    return True


def _b64dec(value: str) -> bytes:
    s = value.replace("-", "+").replace("_", "/")
    s += "=" * (-len(s) % 4)
    return base64.b64decode(s)


def _extract_router_data(html: str) -> dict:
    marker = "window._ROUTER_DATA = "
    start = html.find(marker)
    if start < 0:
        return {}
    idx = start + len(marker)
    while idx < len(html) and html[idx].isspace():
        idx += 1
    if idx >= len(html) or html[idx] != "{":
        return {}

    depth = 0
    in_str = False
    escaped = False
    for cursor in range(idx, len(html)):
        ch = html[cursor]
        if in_str:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(html[idx: cursor + 1])
                except ValueError:
                    return {}
    return {}


# ──── Normalisation ────

def _normalise(item: dict, video_id: str) -> dict:
    """Convert Douyin API item_info into the same shape as VideoDownloader output."""
    title = item.get("desc") or f"douyin_{video_id}"
    video_meta = item.get("video", {})

    # Thumbnail
    thumbnail = ""
    for key in ("cover", "origin_cover", "dynamic_cover"):
        urls = video_meta.get(key, {}).get("url_list", [])
        if urls:
            thumbnail = urls[0]
            break

    duration = video_meta.get("duration", 0)
    if duration and duration > 1000:
        duration = duration // 1000

    stats = item.get("statistics", {})
    author = item.get("author", {})
    desc = title
    if len(desc) > 200:
        desc = desc[:200] + "..."

    # Video play URL (watermark removed)
    play_urls = video_meta.get("play_addr", {}).get("url_list", [])
    video_url = play_urls[0].replace("playwm", "play") if play_urls else ""

    width = video_meta.get("play_addr", {}).get("width") or video_meta.get("width", 0)
    height = video_meta.get("play_addr", {}).get("height") or video_meta.get("height", 0)

    formats = []
    if video_url:
        quality_label = f"{height}p" if height else "原画"
        formats.append({
            "format_id": video_url,
            "quality": quality_label,
            "ext": "mp4",
            "filesize": video_meta.get("play_addr", {}).get("data_size"),
            "has_video": True,
            "has_audio": True,
            "is_merged": True,
            "note": "无水印",
        })

    return {
        "title": title,
        "thumbnail": thumbnail,
        "duration": duration,
        "uploader": author.get("nickname", ""),
        "description": desc,
        "view_count": stats.get("play_count") or stats.get("digg_count"),
        "platform": {"name": "抖音", "icon": "douyin", "color": "#000000"},
        "formats": formats,
    }
