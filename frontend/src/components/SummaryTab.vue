<template>
  <div class="summary-tab">
    <div v-if="loading && !content" class="tab-loading">
      <span class="skeleton-block"></span>
      <span class="skeleton-block short"></span>
      <span class="skeleton-block"></span>
    </div>
    <div v-else-if="content" class="summary-content" v-html="renderedContent"></div>
    <div v-else class="tab-empty">暂无摘要内容</div>
  </div>
</template>

<script setup>
import { computed } from "vue";
import { marked } from "marked";

const props = defineProps({
  content: { type: String, default: "" },
  loading: { type: Boolean, default: false },
});

const renderedContent = computed(() => {
  if (!props.content) return "";
  return marked.parse(props.content, { breaks: true });
});
</script>

<style scoped>
.summary-tab {
  line-height: 1.8;
  color: var(--text-primary);
  font-size: 14px;
}

.summary-content {
  padding: 4px 0;
}

.summary-content :deep(p) {
  margin-bottom: 12px;
}

.summary-content :deep(strong) {
  color: var(--accent-blue);
}

.tab-loading {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.skeleton-block {
  display: block;
  height: 16px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 4px;
  width: 100%;
}

.skeleton-block.short {
  width: 65%;
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
