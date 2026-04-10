<template>
  <section class="hero">
    <div class="container hero-content">
      <div class="hero-badge">
        <span class="badge-dot"></span>
        支持 1000+ 平台，永久免费使用
      </div>

      <h1 class="hero-title">
        万能视频下载器，<span class="title-accent">一键保存</span>
      </h1>

      <p class="hero-subtitle">
        粘贴视频链接，智能解析，支持多种清晰度下载。YouTube、Bilibili、抖音、TikTok…<br />
        随时随地，想下就下
      </p>

      <div class="input-box">
        <div class="input-wrapper">
          <svg class="input-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71" />
            <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71" />
          </svg>
          <input
            ref="urlInput"
            v-model="localUrl"
            type="url"
            class="url-input"
            placeholder="粘贴视频链接，例如 https://www.youtube.com/watch?v=..."
            @keydown.enter="handleParse"
            :disabled="loading"
          />
          <button
            v-if="localUrl"
            class="clear-btn"
            @click="localUrl = ''"
            title="清空"
          >&times;</button>
        </div>
        <button
          class="btn-primary parse-btn"
          @click="handleParse"
          :disabled="loading || !localUrl.trim()"
        >
          <span v-if="loading" class="spinner"></span>
          <svg v-else class="btn-search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <circle cx="11" cy="11" r="8" />
            <path d="m21 21-4.35-4.35" />
          </svg>
          {{ loading ? '解析中…' : '解析视频' }}
        </button>
      </div>

      <div class="quick-links">
        <span class="quick-label">试试：</span>
        <button
          v-for="link in quickLinks"
          :key="link.name"
          class="quick-link"
          @click="fillUrl(link.url)"
        >{{ link.name }}</button>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, watch } from "vue";

const props = defineProps({
  modelValue: { type: String, default: "" },
  loading: { type: Boolean, default: false },
});
const emit = defineEmits(["update:modelValue", "parse"]);

const localUrl = ref(props.modelValue);
const urlInput = ref(null);

const quickLinks = [
  { name: "YouTube",   url: "https://www.youtube.com/watch?v=dQw4w9WgXcQ" },
  { name: "Bilibili",  url: "https://www.bilibili.com/video/BV1uT4y1P7CX" },
  { name: "Twitter/X", url: "https://x.com/elonmusk/status/1800000000000000000" },
];

watch(() => props.modelValue, (v) => { localUrl.value = v; });
watch(localUrl, (v) => emit("update:modelValue", v));

function handleParse() {
  if (!localUrl.value.trim() || props.loading) return;
  emit("parse", localUrl.value.trim());
}

function fillUrl(url) {
  localUrl.value = url;
}
</script>

<style scoped>
.hero {
  padding: 64px 0 40px;
  background: var(--bg-primary);
}

.hero-content {
  text-align: center;
  max-width: 720px;
  margin: 0 auto;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 16px;
  border-radius: var(--radius-full);
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  color: #16a34a;
  font-size: 13px;
  font-weight: 500;
  margin-bottom: 24px;
}

.badge-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #22c55e;
  flex-shrink: 0;
}

.hero-title {
  font-size: 42px;
  font-weight: 800;
  line-height: 1.25;
  margin-bottom: 16px;
  color: var(--text-primary);
  letter-spacing: -0.5px;
}

.title-accent {
  background: linear-gradient(135deg, #2563eb, #1e90ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-subtitle {
  color: var(--text-secondary);
  font-size: 16px;
  line-height: 1.7;
  margin-bottom: 36px;
}

.input-box {
  display: flex;
  align-items: center;
  gap: 0;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  background: var(--bg-primary);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
  transition: border-color 0.2s;
}

.input-box:focus-within {
  border-color: var(--accent-blue);
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.input-wrapper {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0 16px;
}

.input-icon {
  width: 20px;
  height: 20px;
  color: var(--text-muted);
  flex-shrink: 0;
}

.url-input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  color: var(--text-primary);
  font-size: 15px;
  padding: 14px 0;
  font-family: inherit;
}

.url-input::placeholder {
  color: var(--text-muted);
}

.clear-btn {
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  font-size: 18px;
  padding: 4px 8px;
  border-radius: 4px;
  transition: color 0.2s;
  line-height: 1;
}

.clear-btn:hover {
  color: var(--text-primary);
}

.parse-btn {
  flex-shrink: 0;
  border-radius: 0 var(--radius-lg) var(--radius-lg) 0;
  padding: 14px 28px;
  font-size: 15px;
  white-space: nowrap;
  height: 100%;
}

.btn-search-icon {
  width: 18px;
  height: 18px;
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

.quick-links {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: 16px;
  flex-wrap: wrap;
}

.quick-label {
  font-size: 13px;
  color: var(--text-muted);
}

.quick-link {
  font-size: 13px;
  color: var(--text-secondary);
  background: none;
  border: none;
  cursor: pointer;
  padding: 2px 4px;
  font-family: inherit;
  transition: color 0.2s;
}

.quick-link:hover {
  color: var(--accent-blue);
}

@media (max-width: 768px) {
  .hero {
    padding: 40px 0 24px;
  }

  .hero-title {
    font-size: 26px;
  }

  .hero-subtitle {
    font-size: 14px;
    margin-bottom: 24px;
  }

  .hero-subtitle br {
    display: none;
  }

  .input-box {
    flex-direction: column;
    border-radius: var(--radius-md);
  }

  .input-wrapper {
    width: 100%;
    border-bottom: 1px solid var(--border-color);
  }

  .parse-btn {
    width: 100%;
    border-radius: 0 0 var(--radius-md) var(--radius-md);
    padding: 12px;
  }
}
</style>
