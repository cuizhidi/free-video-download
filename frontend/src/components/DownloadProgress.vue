<template>
  <section v-if="visible" class="progress-section">
    <div class="container">
      <div class="card progress-card">
        <div class="progress-header">
          <span class="progress-status-icon">{{ statusIcon }}</span>
          <span class="progress-status-text">{{ statusText }}</span>
        </div>

        <div class="progress-bar-wrapper">
          <div class="progress-bar">
            <div
              class="progress-fill"
              :style="{ width: percent + '%' }"
              :class="{ done: status === 'done', error: status === 'error' }"
            ></div>
          </div>
          <span class="progress-percent">{{ percent.toFixed(1) }}%</span>
        </div>

        <div class="progress-details" v-if="status === 'downloading'">
          <span v-if="speed">速度: {{ speed }}</span>
          <span v-if="eta">剩余: {{ eta }}</span>
        </div>

        <div v-if="status === 'done' && filename" class="progress-done">
          <a :href="fileUrl" class="btn-primary save-btn" download>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" width="18" height="18">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
              <polyline points="7 10 12 15 17 10"/>
              <line x1="12" y1="15" x2="12" y2="3"/>
            </svg>
            保存到本地
          </a>
        </div>

        <div v-if="status === 'error'" class="progress-error">
          <p>{{ errorMessage }}</p>
          <button class="btn-primary retry-btn" @click="$emit('retry')">重试</button>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed } from "vue";
import { getFileUrl } from "../api/index.js";

const props = defineProps({
  visible: { type: Boolean, default: false },
  status: { type: String, default: "idle" },
  percent: { type: Number, default: 0 },
  speed: { type: String, default: "" },
  eta: { type: String, default: "" },
  filename: { type: String, default: "" },
  errorMessage: { type: String, default: "" },
});

defineEmits(["retry"]);

const fileUrl = computed(() => (props.filename ? getFileUrl(props.filename) : "#"));

const statusIcon = computed(() => {
  const map = { downloading: "⏬", processing: "⚙️", done: "✅", error: "❌" };
  return map[props.status] || "⏳";
});

const statusText = computed(() => {
  const map = {
    downloading: "正在下载...",
    processing: "正在合并处理...",
    done: "下载完成！",
    error: "下载失败",
  };
  return map[props.status] || "准备中...";
});
</script>

<style scoped>
.progress-section {
  padding: 0 0 32px;
}

.progress-card {
  padding: 24px 28px;
}

.progress-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
}

.progress-status-icon {
  font-size: 20px;
}

.progress-status-text {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}

.progress-bar-wrapper {
  display: flex;
  align-items: center;
  gap: 14px;
}

.progress-bar {
  flex: 1;
  height: 8px;
  border-radius: 4px;
  background: var(--bg-secondary);
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 4px;
  background: var(--accent-blue);
  transition: width 0.4s ease;
  position: relative;
}

.progress-fill::after {
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  animation: shimmer 1.5s infinite;
}

.progress-fill.done {
  background: var(--color-success);
}
.progress-fill.done::after { animation: none; }

.progress-fill.error {
  background: var(--color-error);
}
.progress-fill.error::after { animation: none; }

@keyframes shimmer {
  from { transform: translateX(-100%); }
  to { transform: translateX(100%); }
}

.progress-percent {
  font-size: 14px;
  font-weight: 700;
  color: var(--accent-blue);
  min-width: 52px;
  text-align: right;
}

.progress-details {
  display: flex;
  gap: 24px;
  margin-top: 10px;
  font-size: 13px;
  color: var(--text-secondary);
}

.progress-done {
  margin-top: 18px;
  text-align: center;
}

.save-btn {
  padding: 12px 40px;
  font-size: 15px;
  text-decoration: none;
  border-radius: var(--radius-full);
}

.progress-error {
  margin-top: 14px;
  text-align: center;
}

.progress-error p {
  color: var(--color-error);
  font-size: 14px;
  margin-bottom: 12px;
}

.retry-btn {
  padding: 10px 28px;
  border-radius: var(--radius-full);
}
</style>
