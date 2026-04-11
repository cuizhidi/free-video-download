function pad2(n) {
  return String(n).padStart(2, "0");
}

function pad3(n) {
  return String(n).padStart(3, "0");
}

/** @param {number} seconds */
function formatSrtTime(seconds) {
  const s = Math.max(0, seconds);
  const h = Math.floor(s / 3600);
  const m = Math.floor((s % 3600) / 60);
  const sec = Math.floor(s % 60);
  const ms = Math.round((s % 1) * 1000);
  return `${pad2(h)}:${pad2(m)}:${pad2(sec)},${pad3(ms)}`;
}

/** @param {number} seconds */
function formatVttTime(seconds) {
  const s = Math.max(0, seconds);
  const h = Math.floor(s / 3600);
  const m = Math.floor((s % 3600) / 60);
  const sec = Math.floor(s % 60);
  const ms = Math.round((s % 1) * 1000);
  return `${pad2(h)}:${pad2(m)}:${pad2(sec)}.${pad3(ms)}`;
}

/**
 * @param {{ start: number, end?: number, text: string }[]} segments
 */
export function segmentsToSrt(segments) {
  const lines = [];
  let index = 1;
  for (const seg of segments) {
    const text = (seg.text || "").replace(/\r/g, "").trim();
    if (!text) continue;
    const start = seg.start ?? 0;
    const end = seg.end != null ? seg.end : start + 2;
    lines.push(String(index++));
    lines.push(`${formatSrtTime(start)} --> ${formatSrtTime(end)}`);
    lines.push(text);
    lines.push("");
  }
  return lines.join("\r\n");
}

/**
 * @param {{ start: number, end?: number, text: string }[]} segments
 */
export function segmentsToVtt(segments) {
  const lines = ["WEBVTT", ""];
  for (const seg of segments) {
    const text = (seg.text || "").replace(/\r/g, "").trim();
    if (!text) continue;
    const start = seg.start ?? 0;
    const end = seg.end != null ? seg.end : start + 2;
    lines.push(`${formatVttTime(start)} --> ${formatVttTime(end)}`);
    lines.push(text);
    lines.push("");
  }
  return lines.join("\r\n");
}

/**
 * @param {string} title
 * @param {string} [fallback]
 */
export function sanitizeFilename(title, fallback = "subtitles") {
  const s = (title || "")
    .replace(/[/\\:*?"<>|]+/g, "_")
    .replace(/\s+/g, " ")
    .trim()
    .slice(0, 100);
  return s || fallback;
}

export function downloadTextFile(filename, content, mime = "text/plain;charset=utf-8") {
  const blob = new Blob([content], { type: mime });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.rel = "noopener";
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 2500);
}
