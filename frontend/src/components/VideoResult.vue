<template>
  <section v-if="info" class="result">
    <div class="container">
      <div class="card result-card">
        <!-- Video Meta -->
        <div class="video-meta">
          <div class="thumb-wrapper">
            <img
              v-if="info.thumbnail"
              :src="proxyThumb(info.thumbnail)"
              :alt="info.title"
              class="thumb"
              @error="thumbError"
            />
            <div v-else class="thumb thumb-placeholder">
              <span>No Image</span>
            </div>
            <span class="duration-badge" v-if="info.duration">
              {{ formatDuration(info.duration) }}
            </span>
          </div>

          <div class="meta-text">
            <h3 class="video-title">{{ info.title }}</h3>
            <div class="meta-row">
              <span class="uploader" v-if="info.uploader">{{ info.uploader }}</span>
              <span class="platform-badge" v-if="info.platform">{{ info.platform.name }}</span>
              <span class="view-count" v-if="info.view_count">{{ formatViews(info.view_count) }}</span>
            </div>
            <p class="video-desc" v-if="info.description">{{ info.description }}</p>
          </div>
        </div>

        <!-- Format Selection -->
        <div class="format-section">
          <h4 class="format-heading">
            <svg class="heading-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 3v1m0 16v1m8.66-13.66l-.71.71M4.05 19.07l-.71.71M21 12h-1M4 12H3m16.95 7.07l-.71-.71M4.05 4.93l-.71-.71"/>
            </svg>
            选择清晰度和格式
          </h4>

          <div class="format-grid">
            <label
              v-for="(f, idx) in info.formats"
              :key="f.format_id"
              class="format-card"
              :class="{ active: selectedId === f.format_id }"
            >
              <input
                type="radio"
                :value="f.format_id"
                v-model="selectedId"
                class="sr-only"
              />
              <span class="format-icon">
                <svg v-if="f.has_audio" viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
                  <rect x="2" y="4" width="20" height="16" rx="3" opacity="0.15"/>
                  <polygon points="10,8 16,12 10,16" />
                </svg>
                <svg v-else viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
                  <rect x="2" y="4" width="20" height="16" rx="3" opacity="0.15"/>
                  <rect x="8" y="9" width="8" height="6" rx="1" opacity="0.6"/>
                </svg>
              </span>
              <span class="format-info">
                <span class="format-main">
                  {{ f.quality }}
                  <template v-if="idx === 0 && f.has_audio"> 最佳 (视频+音频合并)</template>
                  <template v-else-if="!f.has_audio"> MP4 (仅视频, {{ formatFileSize(f.filesize) }})</template>
                  <template v-else> MP4 ({{ formatFileSize(f.filesize) }})</template>
                </span>
                <span class="format-sub">
                  MP4 · {{ f.has_audio ? '含音频' : '仅视频' }}
                </span>
              </span>
            </label>
          </div>

          <!-- Download Button -->
          <div class="download-bar">
            <button
              class="btn-primary download-btn"
              :disabled="!selectedId || downloading"
              @click="handleDownload"
            >
              <span v-if="downloading" class="spinner"></span>
              <span v-else class="dl-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" width="18" height="18">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                  <polyline points="7 10 12 15 17 10"/>
                  <line x1="12" y1="15" x2="12" y2="3"/>
                </svg>
              </span>
              {{ downloading ? '下载中，请稍候...' : '开始下载' }}
            </button>
            <span class="selected-hint" v-if="selectedId">
              已选择: {{ selectedFormatLabel }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, watch, computed } from "vue";
import { formatFileSize, formatDuration } from "../api/index.js";

const props = defineProps({
  info: { type: Object, default: null },
  downloading: { type: Boolean, default: false },
});
const emit = defineEmits(["download"]);

const selectedId = ref(null);

watch(
  () => props.info,
  (v) => {
    if (v?.formats?.length) {
      selectedId.value = v.formats[0].format_id;
    } else {
      selectedId.value = null;
    }
  },
  { immediate: true }
);

const selectedFormatLabel = computed(() => {
  if (!props.info?.formats || !selectedId.value) return "";
  const f = props.info.formats.find((x) => x.format_id === selectedId.value);
  if (!f) return "";
  return `${f.quality} ${f.has_audio ? "(视频+音频合并)" : "(仅视频)"}`;
});

function handleDownload() {
  if (!selectedId.value) return;
  emit("download", selectedId.value);
}

function proxyThumb(url) {
  if (!url) return "";
  return `/api/proxy-image?url=${encodeURIComponent(url)}`;
}

function thumbError(e) {
  e.target.style.display = "none";
}

function formatViews(n) {
  if (!n) return "";
  if (n >= 10000) return `${(n / 10000).toFixed(1)}万`;
  return String(n);
}
</script>

<style scoped>
.result {
  padding: 24px 0 40px;
}

.result-card {
  padding: 28px;
}

/* ---- Video Meta ---- */

.video-meta {
  display: flex;
  gap: 24px;
  margin-bottom: 28px;
}

.thumb-wrapper {
  position: relative;
  flex-shrink: 0;
  width: 280px;
  border-radius: var(--radius-md);
  overflow: hidden;
  background: var(--bg-secondary);
}

.thumb {
  width: 100%;
  aspect-ratio: 16 / 9;
  object-fit: cover;
  display: block;
}

.thumb-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
  font-size: 13px;
}

.duration-badge {
  position: absolute;
  bottom: 8px;
  right: 8px;
  background: rgba(0, 0, 0, 0.75);
  color: #fff;
  font-size: 12px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 4px;
}

.meta-text {
  flex: 1;
  min-width: 0;
}

.video-title {
  font-size: 18px;
  font-weight: 700;
  line-height: 1.5;
  margin-bottom: 8px;
  color: var(--text-primary);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.meta-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
  flex-wrap: wrap;
}

.uploader {
  font-size: 14px;
  color: var(--text-secondary);
}

.platform-badge {
  display: inline-block;
  font-size: 11px;
  font-weight: 600;
  padding: 2px 10px;
  border-radius: var(--radius-full);
  background: var(--accent-blue-light);
  color: var(--accent-blue);
  border: 1px solid var(--accent-blue-border);
}

.view-count {
  font-size: 13px;
  color: var(--text-muted);
}

.view-count::before {
  content: "👁 ";
}

.video-desc {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* ---- Format Selection ---- */

.format-section {
  border-top: 1px solid var(--border-color);
  padding-top: 24px;
}

.format-heading {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 16px;
  color: var(--text-primary);
}

.heading-icon {
  width: 18px;
  height: 18px;
  color: var(--text-muted);
}

.format-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
  margin-bottom: 20px;
}

.format-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
  background: var(--bg-secondary);
  cursor: pointer;
  transition: all 0.2s ease;
}

.format-card:hover {
  border-color: var(--accent-blue-border);
  background: var(--accent-blue-light);
}

.format-card.active {
  border-color: var(--accent-blue);
  background: var(--accent-blue-light);
  box-shadow: 0 0 0 1px var(--accent-blue);
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
}

.format-icon {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--accent-blue);
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
}

.format-card.active .format-icon {
  background: var(--accent-blue);
  color: #fff;
  border-color: var(--accent-blue);
}

.format-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.format-main {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.format-sub {
  font-size: 12px;
  color: var(--text-muted);
}

/* ---- Download Bar ---- */

.download-bar {
  display: flex;
  align-items: center;
  gap: 16px;
}

.download-btn {
  flex: 0 0 auto;
  padding: 13px 36px;
  font-size: 15px;
  border-radius: var(--radius-full);
}

.dl-icon {
  display: flex;
}

.selected-hint {
  font-size: 13px;
  color: var(--text-muted);
}

.spinner {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* ---- Responsive ---- */

@media (max-width: 768px) {
  .video-meta {
    flex-direction: column;
  }

  .thumb-wrapper {
    width: 100%;
  }

  .format-grid {
    grid-template-columns: 1fr;
  }

  .download-bar {
    flex-direction: column;
    align-items: stretch;
  }

  .download-btn {
    width: 100%;
  }

  .selected-hint {
    text-align: center;
  }
}
</style>
