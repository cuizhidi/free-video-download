<template>
  <div class="mindmap-tab">
    <div v-if="loading && !markdown" class="tab-loading">
      <div class="skeleton-mindmap">
        <span class="skeleton-circle"></span>
        <div class="skeleton-branches">
          <span class="skeleton-branch"></span>
          <span class="skeleton-branch short"></span>
          <span class="skeleton-branch"></span>
        </div>
      </div>
    </div>
    <div v-else-if="markdown" class="mindmap-wrapper">
      <div class="mindmap-toolbar">
        <button class="mm-btn" @click="fitView" title="适应窗口">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
            <path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7"/>
          </svg>
        </button>
        <button class="mm-btn" @click="zoomIn" title="放大">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
            <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
            <line x1="11" y1="8" x2="11" y2="14"/><line x1="8" y1="11" x2="14" y2="11"/>
          </svg>
        </button>
        <button class="mm-btn" @click="zoomOut" title="缩小">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
            <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
            <line x1="8" y1="11" x2="14" y2="11"/>
          </svg>
        </button>
      </div>
      <svg ref="svgRef" class="mindmap-svg"></svg>
    </div>
    <div v-else class="tab-empty">暂无思维导图数据</div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onBeforeUnmount, nextTick } from "vue";

const props = defineProps({
  markdown: { type: String, default: "" },
  loading: { type: Boolean, default: false },
});

const svgRef = ref(null);
let markmapInstance = null;
let Markmap = null;
let transformer = null;

async function loadMarkmap() {
  if (Markmap) return;
  const [viewModule, libModule] = await Promise.all([
    import("markmap-view"),
    import("markmap-lib"),
  ]);
  Markmap = viewModule.Markmap;
  transformer = new libModule.Transformer();
}

async function renderMap() {
  if (!props.markdown || !svgRef.value) return;

  await loadMarkmap();

  const { root } = transformer.transform(props.markdown);

  if (markmapInstance) {
    markmapInstance.setData(root);
    markmapInstance.fit();
  } else {
    markmapInstance = Markmap.create(svgRef.value, {
      autoFit: true,
      duration: 300,
      maxWidth: 240,
    }, root);
  }
}

function fitView() {
  markmapInstance?.fit();
}

function zoomIn() {
  markmapInstance?.rescale(1.25);
}

function zoomOut() {
  markmapInstance?.rescale(0.8);
}

watch(
  () => props.markdown,
  async (val) => {
    if (val) {
      await nextTick();
      renderMap();
    }
  }
);

onMounted(() => {
  if (props.markdown) renderMap();
});

onBeforeUnmount(() => {
  if (markmapInstance) {
    markmapInstance.destroy?.();
    markmapInstance = null;
  }
});
</script>

<style scoped>
.mindmap-wrapper {
  position: relative;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  background: #fefefe;
  overflow: hidden;
}

.mindmap-toolbar {
  position: absolute;
  top: 10px;
  right: 10px;
  z-index: 10;
  display: flex;
  gap: 4px;
}

.mm-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  cursor: pointer;
  color: var(--text-secondary);
  transition: all 0.2s;
}

.mm-btn:hover {
  color: var(--accent-blue);
  border-color: var(--accent-blue-border);
  background: var(--accent-blue-light);
}

.mindmap-svg {
  width: 100%;
  height: 420px;
  display: block;
}

/* Loading */

.tab-loading {
  display: flex;
  justify-content: center;
  padding: 60px 0;
}

.skeleton-mindmap {
  display: flex;
  align-items: center;
  gap: 24px;
}

.skeleton-circle {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

.skeleton-branches {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.skeleton-branch {
  height: 12px;
  width: 140px;
  border-radius: 4px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

.skeleton-branch.short {
  width: 100px;
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
