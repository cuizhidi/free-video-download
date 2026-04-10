<template>
  <div class="chapter-tab">
    <div v-if="loading && !chapters.length" class="tab-loading">
      <div class="skeleton-card" v-for="i in 3" :key="i">
        <span class="skeleton-line w40"></span>
        <span class="skeleton-line"></span>
      </div>
    </div>
    <div v-else-if="chapters.length" class="chapter-list">
      <div
        v-for="(ch, idx) in chapters"
        :key="idx"
        class="chapter-item"
      >
        <div class="chapter-index">{{ String(idx + 1).padStart(2, '0') }}</div>
        <div class="chapter-body">
          <div class="chapter-header">
            <h4 class="chapter-title">{{ ch.title }}</h4>
            <span v-if="ch.start_time" class="chapter-time">{{ ch.start_time }}</span>
          </div>
          <p class="chapter-summary">{{ ch.summary }}</p>
        </div>
      </div>
    </div>
    <div v-else class="tab-empty">暂无章节大纲</div>
  </div>
</template>

<script setup>
defineProps({
  chapters: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
});
</script>

<style scoped>
.chapter-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.chapter-item {
  display: flex;
  gap: 16px;
  padding: 16px;
  border-radius: var(--radius-md);
  background: var(--bg-secondary);
  border: 1px solid var(--border-light);
  transition: all 0.2s ease;
}

.chapter-item:hover {
  border-color: var(--accent-blue-border);
  box-shadow: var(--shadow-sm);
}

.chapter-index {
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--accent-blue);
  color: #fff;
  font-size: 13px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chapter-body {
  flex: 1;
  min-width: 0;
}

.chapter-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 6px;
}

.chapter-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.chapter-time {
  flex-shrink: 0;
  font-size: 12px;
  font-weight: 500;
  color: var(--accent-blue);
  background: var(--accent-blue-light);
  padding: 2px 10px;
  border-radius: var(--radius-full);
}

.chapter-summary {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.6;
}

/* Loading & Empty */

.tab-loading {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.skeleton-card {
  padding: 16px;
  border-radius: var(--radius-md);
  background: var(--bg-secondary);
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.skeleton-line {
  display: block;
  height: 14px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 4px;
  width: 100%;
}

.skeleton-line.w40 {
  width: 40%;
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
</style>
