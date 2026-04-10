<template>
  <div class="keypoints-tab">
    <div v-if="loading && !points.length" class="tab-loading">
      <div class="skeleton-card" v-for="i in 4" :key="i">
        <span class="skeleton-line w50"></span>
        <span class="skeleton-line"></span>
      </div>
    </div>
    <div v-else-if="points.length" class="points-grid">
      <div
        v-for="(kp, idx) in points"
        :key="idx"
        class="point-card"
      >
        <div class="point-badge">{{ idx + 1 }}</div>
        <div class="point-body">
          <h4 class="point-title">{{ kp.point }}</h4>
          <p class="point-detail">{{ kp.detail }}</p>
        </div>
      </div>
    </div>
    <div v-else class="tab-empty">暂无知识要点</div>
  </div>
</template>

<script setup>
defineProps({
  points: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
});
</script>

<style scoped>
.points-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.point-card {
  display: flex;
  gap: 12px;
  padding: 16px;
  border-radius: var(--radius-md);
  background: var(--bg-secondary);
  border: 1px solid var(--border-light);
  transition: all 0.2s ease;
}

.point-card:hover {
  border-color: var(--accent-blue-border);
  box-shadow: var(--shadow-sm);
}

.point-badge {
  flex-shrink: 0;
  width: 28px;
  height: 28px;
  border-radius: var(--radius-sm);
  background: linear-gradient(135deg, #ede9fe, #dbeafe);
  color: #7c3aed;
  font-size: 12px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}

.point-body {
  flex: 1;
  min-width: 0;
}

.point-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.point-detail {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.6;
}

/* Loading & Empty */

.tab-loading {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
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

.skeleton-line.w50 {
  width: 50%;
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
  .points-grid,
  .tab-loading {
    grid-template-columns: 1fr;
  }
}
</style>
