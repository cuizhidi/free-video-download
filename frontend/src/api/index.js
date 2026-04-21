import { getToken } from "../stores/auth.js";

const API_BASE = "/api";

function _authHeaders() {
  const t = getToken();
  return t ? { Authorization: `Bearer ${t}` } : {};
}

export async function parseVideo(url) {
  const res = await fetch(
    `${API_BASE}/parse?url=${encodeURIComponent(url)}`,
    { headers: _authHeaders() },
  );
  if (!res.ok) {
    const err = await res.json().catch(() => null);
    throw new Error(
      err?.detail?.error || err?.detail || "解析失败，请稍后重试"
    );
  }
  return res.json();
}

export function downloadVideo(url, formatId, { onProgress, onComplete, onError }) {
  const sse = new EventSource(
    `${API_BASE}/download?url=${encodeURIComponent(url)}&format_id=${encodeURIComponent(formatId)}`
  );

  sse.addEventListener("progress", (e) => {
    onProgress?.(JSON.parse(e.data));
  });

  sse.addEventListener("complete", (e) => {
    const data = JSON.parse(e.data);
    sse.close();
    onComplete?.(data);
  });

  sse.addEventListener("error", (e) => {
    const data = e.data ? JSON.parse(e.data) : { message: "连接中断，请重试" };
    sse.close();
    onError?.(data);
  });

  sse.onerror = () => {
    sse.close();
    onError?.({ message: "连接中断，请重试" });
  };

  return sse;
}

export function getFileUrl(filename) {
  return `${API_BASE}/file/${filename}`;
}

export function formatFileSize(bytes) {
  if (!bytes) return "未知";
  const units = ["B", "KB", "MB", "GB"];
  let i = 0;
  let size = bytes;
  while (size >= 1024 && i < units.length - 1) {
    size /= 1024;
    i++;
  }
  return `${size.toFixed(1)} ${units[i]}`;
}

export function formatDuration(seconds) {
  if (!seconds) return "--:--";
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.floor(seconds % 60);
  const pad = (n) => String(n).padStart(2, "0");
  return h > 0 ? `${h}:${pad(m)}:${pad(s)}` : `${m}:${pad(s)}`;
}
