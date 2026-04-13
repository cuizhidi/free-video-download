"""
Subtitle extraction module.

Strategy (3-level fallback):
1. yt-dlp manual subtitles
2. yt-dlp automatic captions (YouTube ASR, etc.)
3. faster-whisper local transcription (lazy-loaded)

Douyin videos skip steps 1-2 and go directly to whisper.
"""

from __future__ import annotations

import logging
import re
import uuid
from collections import OrderedDict
from pathlib import Path
from threading import Lock
from typing import Optional

import yt_dlp

from douyin_downloader import is_douyin_url

logger = logging.getLogger("subtitle_extractor")

DOWNLOAD_DIR = Path(__file__).parent / "downloads"
DOWNLOAD_DIR.mkdir(exist_ok=True)

_LANG_PRIORITY = ["zh-Hans", "zh-CN", "zh", "zh-Hant", "en", "en-US", "ja", "ko"]

_cache: OrderedDict[str, dict] = OrderedDict()
_CACHE_MAX = 50
_cache_lock = Lock()

_whisper_model = None
_whisper_lock = Lock()


def _get_whisper_model():
    """Lazy-load faster-whisper model on first use."""
    global _whisper_model
    if _whisper_model is not None:
        return _whisper_model
    with _whisper_lock:
        if _whisper_model is not None:
            return _whisper_model
        try:
            from faster_whisper import WhisperModel
            logger.info("Loading faster-whisper model (tiny, cpu, int8)…")
            _whisper_model = WhisperModel("tiny", device="cpu", compute_type="int8")
            logger.info("faster-whisper model loaded.")
        except ImportError:
            raise RuntimeError(
                "faster-whisper 未安装。请执行: pip install faster-whisper"
            )
    return _whisper_model


def _cache_get(url: str) -> Optional[dict]:
    with _cache_lock:
        if url in _cache:
            _cache.move_to_end(url)
            return _cache[url]
    return None


def _cache_set(url: str, data: dict):
    with _cache_lock:
        _cache[url] = data
        _cache.move_to_end(url)
        while len(_cache) > _CACHE_MAX:
            _cache.popitem(last=False)


def extract_subtitle(url: str) -> dict:
    """
    Extract subtitle / transcript for a video URL.

    Returns:
        {
            "segments": [{"start": float, "end": float, "text": str}, ...],
            "full_text": str,
            "language": str,
            "source": "subtitle" | "auto_caption" | "whisper",
        }
    """
    cached = _cache_get(url)
    if cached is not None:
        return cached

    if is_douyin_url(url):
        result = _transcribe_via_whisper(url)
        _cache_set(url, result)
        return result

    sub_result = _extract_ytdlp_subtitles(url)
    if sub_result:
        _cache_set(url, sub_result)
        return sub_result

    result = _transcribe_via_whisper(url)
    _cache_set(url, result)
    return result


def _extract_ytdlp_subtitles(url: str) -> Optional[dict]:
    """Try to extract subtitles using yt-dlp (manual then automatic)."""
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "noplaylist": True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
    except Exception as e:
        logger.warning("yt-dlp extract_info failed for subtitles: %s", e)
        return None

    manual_subs = info.get("subtitles") or {}
    auto_subs = info.get("automatic_captions") or {}

    for source_label, sub_dict in [("subtitle", manual_subs), ("auto_caption", auto_subs)]:
        lang, sub_entries = _pick_best_lang(sub_dict)
        if not sub_entries:
            continue

        sub_url = _pick_best_format_url(sub_entries)
        if not sub_url:
            continue

        try:
            segments = _download_and_parse_subtitle(sub_url, ydl)
            if segments:
                full_text = " ".join(seg["text"] for seg in segments)
                return {
                    "segments": segments,
                    "full_text": full_text,
                    "language": lang,
                    "source": source_label,
                }
        except Exception as e:
            logger.warning("Failed to parse subtitle (%s/%s): %s", source_label, lang, e)

    return None


def _pick_best_lang(sub_dict: dict) -> tuple[str, list]:
    """Pick the best language track from subtitle dict."""
    for lang in _LANG_PRIORITY:
        if lang in sub_dict:
            return lang, sub_dict[lang]

    for key in sub_dict:
        if key.startswith("zh"):
            return key, sub_dict[key]
    for key in sub_dict:
        if key.startswith("en"):
            return key, sub_dict[key]

    if sub_dict:
        first_key = next(iter(sub_dict))
        return first_key, sub_dict[first_key]

    return "", []


def _pick_best_format_url(entries: list[dict]) -> Optional[str]:
    """Pick the best subtitle format URL (prefer srv1/json3/vtt/srt)."""
    preferred_exts = ["json3", "srv1", "vtt", "srt"]
    for ext in preferred_exts:
        for entry in entries:
            if entry.get("ext") == ext:
                return entry.get("url")
    if entries:
        return entries[0].get("url")
    return None


def _download_and_parse_subtitle(sub_url: str, ydl: yt_dlp.YoutubeDL) -> list[dict]:
    """Download subtitle content and parse into segments."""
    import urllib.request

    req = urllib.request.Request(sub_url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    })
    with urllib.request.urlopen(req, timeout=15) as resp:
        content = resp.read().decode("utf-8", errors="replace")

    if sub_url.endswith(".json3") or "json3" in sub_url:
        return _parse_json3(content)
    elif sub_url.endswith(".srv1") or "srv1" in sub_url:
        return _parse_srv1(content)
    else:
        return _parse_srt_vtt(content)


def _parse_json3(content: str) -> list[dict]:
    """Parse YouTube json3 subtitle format."""
    import json
    data = json.loads(content)
    events = data.get("events", [])
    segments = []
    for event in events:
        segs = event.get("segs")
        if not segs:
            continue
        text = "".join(s.get("utf8", "") for s in segs).strip()
        if not text or text == "\n":
            continue
        start_ms = event.get("tStartMs", 0)
        dur_ms = event.get("dDurationMs", 0)
        segments.append({
            "start": round(start_ms / 1000, 2),
            "end": round((start_ms + dur_ms) / 1000, 2),
            "text": text,
        })
    return segments


def _parse_srv1(content: str) -> list[dict]:
    """Parse YouTube srv1 (XML timedtext) format."""
    import xml.etree.ElementTree as ET
    root = ET.fromstring(content)
    segments = []
    for elem in root.iter("text"):
        text = (elem.text or "").strip()
        if not text:
            continue
        start = float(elem.get("start", 0))
        dur = float(elem.get("dur", 0))
        text = re.sub(r"<[^>]+>", "", text)
        text = text.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
        text = text.replace("&#39;", "'").replace("&quot;", '"')
        segments.append({
            "start": round(start, 2),
            "end": round(start + dur, 2),
            "text": text,
        })
    return segments


def _parse_srt_vtt(content: str) -> list[dict]:
    """Parse SRT or VTT subtitle format."""
    content = re.sub(r"WEBVTT.*?\n\n", "", content, count=1)
    pattern = re.compile(
        r"(?:\d+\s*\n)?"
        r"(\d{1,2}:\d{2}:\d{2}[.,]\d{3})\s*-->\s*(\d{1,2}:\d{2}:\d{2}[.,]\d{3})"
        r"\s*\n([\s\S]*?)(?=\n\n|\n\d+\s*\n|\Z)",
        re.MULTILINE,
    )
    segments = []
    for m in pattern.finditer(content):
        start = _ts_to_seconds(m.group(1))
        end = _ts_to_seconds(m.group(2))
        text = re.sub(r"<[^>]+>", "", m.group(3)).strip()
        if text:
            segments.append({"start": start, "end": end, "text": text})
    return segments


def _ts_to_seconds(ts: str) -> float:
    """Convert 'HH:MM:SS,mmm' or 'HH:MM:SS.mmm' to seconds."""
    ts = ts.replace(",", ".")
    parts = ts.split(":")
    h, m = int(parts[0]), int(parts[1])
    s = float(parts[2])
    return round(h * 3600 + m * 60 + s, 2)


def _transcribe_via_whisper(url: str) -> dict:
    """Download audio and transcribe with faster-whisper."""
    audio_path = _download_audio(url)
    try:
        model = _get_whisper_model()
        segments_iter, info = model.transcribe(
            str(audio_path),
            beam_size=5,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=500),
        )
        segments = []
        for seg in segments_iter:
            segments.append({
                "start": round(seg.start, 2),
                "end": round(seg.end, 2),
                "text": seg.text.strip(),
            })
        full_text = " ".join(s["text"] for s in segments)
        return {
            "segments": segments,
            "full_text": full_text,
            "language": info.language or "unknown",
            "source": "whisper",
        }
    finally:
        audio_path.unlink(missing_ok=True)


def _download_audio(url: str) -> Path:
    """Download audio-only stream using yt-dlp."""
    file_id = str(uuid.uuid4())[:8]
    out_path = DOWNLOAD_DIR / f"audio_{file_id}.%(ext)s"
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": str(out_path),
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "128",
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    for f in DOWNLOAD_DIR.iterdir():
        if f.stem.startswith(f"audio_{file_id}"):
            return f

    raise RuntimeError("音频下载失败，未找到输出文件")
