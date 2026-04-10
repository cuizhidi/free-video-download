const API_BASE = "/api/ai";

/**
 * Check if AI service is available (DEEPSEEK_API_KEY configured).
 */
export async function checkAIStatus() {
  const res = await fetch(`${API_BASE}/status`);
  if (!res.ok) return { available: false };
  return res.json();
}

/**
 * Extract subtitle / transcript for a video URL.
 */
export async function extractSubtitle(url) {
  const res = await fetch(
    `${API_BASE}/subtitle?url=${encodeURIComponent(url)}`
  );
  if (!res.ok) {
    const err = await res.json().catch(() => null);
    throw new Error(
      err?.detail?.error || err?.detail || "字幕提取失败，请稍后重试"
    );
  }
  return res.json();
}

/**
 * Stream AI video summary via SSE (POST with fetch + ReadableStream).
 *
 * @param {object} params - { transcript, title, language }
 * @param {object} callbacks - { onChunk(text), onDone(fullContent), onError(msg) }
 * @returns {AbortController} - call .abort() to cancel
 */
export function streamSummarize(params, { onChunk, onDone, onError }) {
  const controller = new AbortController();

  fetch(`${API_BASE}/summarize`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
    signal: controller.signal,
  })
    .then((res) => {
      if (!res.ok) {
        return res.json().then((err) => {
          throw new Error(err?.detail?.error || "AI 总结请求失败");
        });
      }
      return _readSSE(res.body, { onChunk, onDone, onError });
    })
    .catch((err) => {
      if (err.name !== "AbortError") {
        onError?.(err.message || "AI 总结请求失败");
      }
    });

  return controller;
}

/**
 * Stream AI chat response via SSE (POST with fetch + ReadableStream).
 *
 * @param {object} params - { transcript, title, messages }
 * @param {object} callbacks - { onChunk(text), onDone(fullContent), onError(msg) }
 * @returns {AbortController} - call .abort() to cancel
 */
export function streamChat(params, { onChunk, onDone, onError }) {
  const controller = new AbortController();

  fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
    signal: controller.signal,
  })
    .then((res) => {
      if (!res.ok) {
        return res.json().then((err) => {
          throw new Error(err?.detail?.error || "AI 问答请求失败");
        });
      }
      return _readSSE(res.body, { onChunk, onDone, onError });
    })
    .catch((err) => {
      if (err.name !== "AbortError") {
        onError?.(err.message || "AI 问答请求失败");
      }
    });

  return controller;
}

/**
 * Parse SSE stream from a ReadableStream (fetch body).
 * Handles event: and data: lines that may arrive across chunk boundaries.
 */
async function _readSSE(body, { onChunk, onDone, onError }) {
  const reader = body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let currentEvent = "";

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });

      const parts = buffer.split("\n");
      buffer = parts.pop() || "";

      for (const line of parts) {
        if (line.startsWith("event: ")) {
          currentEvent = line.slice(7).trim();
        } else if (line.startsWith("data: ")) {
          const raw = line.slice(6);
          if (!raw || raw === "{}") continue;
          try {
            const data = JSON.parse(raw);
            if (currentEvent === "chunk") {
              onChunk?.(data.content || "");
            } else if (currentEvent === "done") {
              onDone?.(data.full_content || "");
              return;
            } else if (currentEvent === "error") {
              onError?.(data.message || "未知错误");
              return;
            }
          } catch {
            // ignore malformed JSON
          }
        } else if (line === "") {
          // empty line = event boundary in SSE, keep currentEvent
        }
      }
    }

    // Stream ended without explicit done/error event
    if (!currentEvent || currentEvent === "chunk") {
      onError?.("AI 响应流意外中断");
    }
  } catch (err) {
    if (err.name !== "AbortError") {
      onError?.(err.message || "读取 AI 响应失败");
    }
  }
}
