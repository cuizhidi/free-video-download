<template>
  <div class="transcript-tab">
    <!-- Meta bar -->
    <div v-if="segments.length" class="transcript-meta">
      <span class="meta-badge" v-if="source">
        {{ sourceLabel }}
      </span>
      <span class="meta-badge" v-if="language">
        {{ language }}
      </span>
      <div class="search-box">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
          <circle cx="11" cy="11" r="8"/>
          <line x1="21" y1="21" x2="16.65" y2="16.65"/>
        </svg>
        <input
          v-model="searchQuery"
          type="text"
          placeholder="搜索字幕内容..."
          class="search-input"
        />
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading && !segments.length" class="tab-loading">
      <div class="skeleton-line" v-for="i in 6" :key="i"></div>
    </div>

    <!-- Segment list -->
    <div v-else-if="filteredSegments.length" class="segment-list">
      <div
        v-for="(seg, idx) in filteredSegments"
        :key="idx"
        class="segment-item"
      >
        <span class="segment-time">{{ formatTime(seg.start) }}</span>
        <span class="segment-text" v-html="highlightText(seg.text)"></span>
      </div>
    </div>

    <!-- Empty -->
    <div v-else-if="searchQuery" class="tab-empty">
      未找到匹配 "{{ searchQuery }}" 的内容
    </div>
    <div v-else class="tab-empty">暂无字幕数据</div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";

const props = defineProps({
  segments: { type: Array, default: () => [] },
  source: { type: String, default: "" },
  language: { type: String, default: "" },
  loading: { type: Boolean, default: false },
});

const searchQuery = ref("");

const sourceLabel = computed(() => {
  const map = {
    subtitle: "手动字幕",
    auto_caption: "自动字幕",
    whisper: "AI 语音识别",
  };
  return map[props.source] || props.source;
});

const filteredSegments = computed(() => {
  if (!searchQuery.value.trim()) return props.segments;
  const q = searchQuery.value.toLowerCase();
  return props.segments.filter((seg) =>
    seg.text.toLowerCase().includes(q)
  );
});

function formatTime(seconds) {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.floor(seconds % 60);
  const pad = (n) => String(n).padStart(2, "0");
  return h > 0 ? `${h}:${pad(m)}:${pad(s)}` : `${pad(m)}:${pad(s)}`;
}

function highlightText(text) {
  if (!searchQuery.value.trim()) return escapeHtml(text);
  const q = searchQuery.value.trim();
  const escaped = escapeHtml(text);
  const regex = new RegExp(`(${escapeRegex(q)})`, "gi");
  return escaped.replace(regex, '<mark class="highlight">$1</mark>');
}

function escapeHtml(str) {
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

function escapeRegex(str) {
  return str.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}
</script>

<style scoped>
.transcript-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.meta-badge {
  font-size: 11px;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: var(--radius-full);
  background: var(--accent-blue-light);
  color: var(--accent-blue);
  border: 1px solid var(--accent-blue-border);
}

.search-box {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-left: auto;
  padding: 6px 12px;
  border-radius: var(--radius-full);
  border: 1px solid var(--border-color);
  background: var(--bg-secondary);
  color: var(--text-muted);
  transition: border-color 0.2s;
}

.search-box:focus-within {
  border-color: var(--accent-blue);
}

.search-input {
  border: none;
  outline: none;
  background: transparent;
  font-size: 12px;
  color: var(--text-primary);
  width: 160px;
  font-family: inherit;
}

.search-input::placeholder {
  color: var(--text-muted);
}

.segment-list {
  max-height: 400px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.segment-item {
  display: flex;
  gap: 12px;
  padding: 8px 12px;
  border-radius: var(--radius-sm);
  transition: background 0.15s;
}

.segment-item:hover {
  background: var(--bg-secondary);
}

.segment-time {
  flex-shrink: 0;
  font-size: 12px;
  font-weight: 600;
  color: var(--accent-blue);
  font-variant-numeric: tabular-nums;
  min-width: 52px;
  padding-top: 1px;
}

.segment-text {
  font-size: 13px;
  color: var(--text-primary);
  line-height: 1.6;
}

.segment-text :deep(.highlight) {
  background: #fef08a;
  color: inherit;
  padding: 0 2px;
  border-radius: 2px;
}

/* Loading & Empty */

.tab-loading {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.skeleton-line {
  height: 14px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 4px;
  width: 100%;
}

.skeleton-line:nth-child(even) {
  width: 80%;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.tab-empty {
  text-align: center;
  padding: 40px 0;
  color: var(--text-muted);
  font-size: 13px;
}

@media (max-width: 768px) {
  .search-input {
    width: 120px;
  }
}
</style>
