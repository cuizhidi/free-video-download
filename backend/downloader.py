import os
import uuid
import re
import yt_dlp
from pathlib import Path

import douyin_downloader

DOWNLOAD_DIR = Path(__file__).parent / "downloads"
DOWNLOAD_DIR.mkdir(exist_ok=True)

PLATFORM_MAP = {
    "youtube":     {"name": "YouTube",   "icon": "youtube",    "color": "#FF0000"},
    "bilibili":    {"name": "Bilibili",  "icon": "bilibili",   "color": "#00A1D6"},
    "tiktok":      {"name": "TikTok",    "icon": "tiktok",     "color": "#000000"},
    "douyin":      {"name": "抖音",       "icon": "douyin",     "color": "#000000"},
    "twitter":     {"name": "X/Twitter", "icon": "twitter",    "color": "#1DA1F2"},
    "instagram":   {"name": "Instagram", "icon": "instagram",  "color": "#E4405F"},
    "xiaohongshu": {"name": "小红书",     "icon": "xiaohongshu","color": "#FF2442"},
    "weibo":       {"name": "微博",       "icon": "weibo",      "color": "#E6162D"},
    "vimeo":       {"name": "Vimeo",     "icon": "vimeo",      "color": "#1AB7EA"},
}


class VideoDownloader:

    def parse_video(self, url: str) -> dict:
        if douyin_downloader.is_douyin_url(url):
            return douyin_downloader.parse_video(url)

        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            "no_color": True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            raw_info = ydl.extract_info(url, download=False)
        return self._normalize_video_info(raw_info)

    def download_video(self, url: str, format_id: str, progress_hook=None) -> str:
        if douyin_downloader.is_douyin_url(url):
            return douyin_downloader.download_video(url, format_id, progress_hook)

        file_id = str(uuid.uuid4())[:8]
        output_template = str(DOWNLOAD_DIR / f"{file_id}.%(ext)s")

        ydl_opts = {
            "format": format_id,
            "outtmpl": output_template,
            "quiet": True,
            "no_warnings": True,
            "merge_output_format": "mp4",
        }
        if progress_hook:
            ydl_opts["progress_hooks"] = [progress_hook]

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        for f in DOWNLOAD_DIR.iterdir():
            if f.stem.startswith(file_id):
                return f.name
        return None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _normalize_video_info(self, raw: dict) -> dict:
        formats = self._filter_and_sort_formats(raw.get("formats") or [])
        desc = raw.get("description") or ""
        if len(desc) > 200:
            desc = desc[:200] + "..."
        return {
            "title": raw.get("title", "未知标题"),
            "thumbnail": raw.get("thumbnail", ""),
            "duration": raw.get("duration", 0),
            "uploader": raw.get("uploader", ""),
            "description": desc,
            "view_count": raw.get("view_count"),
            "platform": self._detect_platform(raw),
            "formats": formats,
        }

    def _detect_platform(self, raw: dict) -> dict:
        extractor = (raw.get("extractor_key") or raw.get("extractor") or "").lower()
        for key, meta in PLATFORM_MAP.items():
            if key in extractor:
                return meta
        return {"name": "其他", "icon": "default", "color": "#666666"}

    def _filter_and_sort_formats(self, raw_formats: list) -> list:
        audio_only = [
            f for f in raw_formats
            if (f.get("acodec") or "none") != "none"
            and (f.get("vcodec") or "none") == "none"
        ]
        best_audio = max(
            audio_only,
            key=lambda f: f.get("abr") or f.get("tbr") or 0,
            default=None,
        )

        result = []
        seen_qualities = set()

        for f in raw_formats:
            has_video = (f.get("vcodec") or "none") != "none"
            has_audio = (f.get("acodec") or "none") != "none"

            if not has_video:
                continue

            height = f.get("height") or 0
            if height < 144:
                continue

            note = (f.get("format_note") or "").lower()
            if "storyboard" in note:
                continue

            quality_label = f"{height}p"
            if quality_label in seen_qualities:
                continue
            seen_qualities.add(quality_label)

            is_merged = has_video and has_audio

            if is_merged:
                format_id = f["format_id"]
            elif best_audio:
                format_id = f"{f['format_id']}+{best_audio['format_id']}"
            else:
                format_id = f["format_id"]

            filesize = f.get("filesize") or f.get("filesize_approx")

            result.append({
                "format_id": format_id,
                "quality": quality_label,
                "ext": "mp4",
                "filesize": filesize,
                "has_video": True,
                "has_audio": is_merged or best_audio is not None,
                "is_merged": is_merged,
                "note": f.get("format_note") or "",
            })

        result.sort(
            key=lambda x: int(re.sub(r"\D", "", x["quality"]) or "0"),
            reverse=True,
        )
        return result
