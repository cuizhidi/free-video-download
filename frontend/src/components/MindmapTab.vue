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
        <button class="mm-btn" type="button" @click="openFullscreen" title="全屏">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
            <path d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3m0 18h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3"/>
          </svg>
        </button>
        <button class="mm-btn" type="button" @click="() => downloadSvg(false)" title="下载 SVG">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3"/>
          </svg>
        </button>
        <button class="mm-btn" type="button" @click="() => downloadPng(false)" title="下载高清 PNG">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
            <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
            <circle cx="8.5" cy="8.5" r="1.5"/>
            <path d="M21 15l-5-5L5 21"/>
          </svg>
        </button>
        <button class="mm-btn" type="button" @click="fitView" title="适应窗口">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
            <path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7"/>
          </svg>
        </button>
        <button class="mm-btn" type="button" @click="zoomIn" title="放大">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
            <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
            <line x1="11" y1="8" x2="11" y2="14"/><line x1="8" y1="11" x2="14" y2="11"/>
          </svg>
        </button>
        <button class="mm-btn" type="button" @click="zoomOut" title="缩小">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
            <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
            <line x1="8" y1="11" x2="14" y2="11"/>
          </svg>
        </button>
      </div>
      <svg ref="svgRef" class="mindmap-svg"></svg>
    </div>
    <div v-else class="tab-empty">暂无思维导图数据</div>

    <Teleport to="body">
      <div
        v-if="fullscreenOpen"
        class="mindmap-fs-overlay"
        role="dialog"
        aria-modal="true"
        aria-label="思维导图全屏"
        @click.self="closeFullscreen"
      >
        <div class="mindmap-fs-panel">
          <div class="mindmap-fs-toolbar">
            <button class="mm-btn mm-btn-text" type="button" @click="closeFullscreen" title="关闭 (Esc)">
              关闭
            </button>
            <span class="mm-fs-divider" />
            <button class="mm-btn" type="button" @click="() => downloadSvg(true)" title="下载 SVG">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3"/>
              </svg>
            </button>
            <button class="mm-btn" type="button" @click="() => downloadPng(true)" title="下载高清 PNG">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                <circle cx="8.5" cy="8.5" r="1.5"/>
                <path d="M21 15l-5-5L5 21"/>
              </svg>
            </button>
            <button class="mm-btn" type="button" @click="fitViewFs" title="适应窗口">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                <path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7"/>
              </svg>
            </button>
            <button class="mm-btn" type="button" @click="zoomInFs" title="放大">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
                <line x1="11" y1="8" x2="11" y2="14"/><line x1="8" y1="11" x2="14" y2="11"/>
              </svg>
            </button>
            <button class="mm-btn" type="button" @click="zoomOutFs" title="缩小">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
                <line x1="8" y1="11" x2="14" y2="11"/>
              </svg>
            </button>
          </div>
          <svg ref="svgFsRef" class="mindmap-fs-svg"></svg>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onBeforeUnmount, nextTick } from "vue";
import {
  exportMindmapSvg,
  exportMindmapPng,
} from "../utils/mindmapExport.js";

const props = defineProps({
  markdown: { type: String, default: "" },
  loading: { type: Boolean, default: false },
  /** Used for download filenames */
  exportBasename: { type: String, default: "mindmap" },
});

const svgRef = ref(null);
const svgFsRef = ref(null);
const fullscreenOpen = ref(false);

let markmapInstance = null;
let mmFs = null;
let Markmap = null;
let transformer = null;

function safeBase() {
  const s = (props.exportBasename || "mindmap")
    .replace(/[/\\:*?"<>|]+/g, "_")
    .trim()
    .slice(0, 80);
  return s || "mindmap";
}

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
    await markmapInstance.setData(root);
    markmapInstance.fit();
  } else {
    markmapInstance = Markmap.create(
      svgRef.value,
      {
        autoFit: true,
        duration: 300,
        maxWidth: 280,
      },
      root
    );
  }
}

async function renderMapFullscreen() {
  if (!fullscreenOpen.value || !props.markdown || !svgFsRef.value) return;

  await loadMarkmap();
  const { root } = transformer.transform(props.markdown);

  if (mmFs) {
    await mmFs.setData(root);
    await mmFs.fit();
  } else {
    mmFs = Markmap.create(
      svgFsRef.value,
      {
        autoFit: true,
        duration: 300,
        maxWidth: 520,
      },
      root
    );
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

function fitViewFs() {
  mmFs?.fit();
}

function zoomInFs() {
  mmFs?.rescale(1.25);
}

function zoomOutFs() {
  mmFs?.rescale(0.8);
}

function activeInstance(preferFullscreen) {
  if (preferFullscreen && fullscreenOpen.value && mmFs) return mmFs;
  if (!preferFullscreen && markmapInstance) return markmapInstance;
  if (fullscreenOpen.value && mmFs) return mmFs;
  return markmapInstance;
}

async function downloadSvg(preferFullscreen) {
  const mm = activeInstance(preferFullscreen);
  if (!mm) return;
  const base = safeBase();
  await exportMindmapSvg(mm, `${base}.svg`);
}

async function downloadPng(preferFullscreen) {
  const mm = activeInstance(preferFullscreen);
  if (!mm) return;
  const base = safeBase();
  const ok = await exportMindmapPng(mm, `${base}.png`);
  if (!ok) {
    window.alert("导出 PNG 失败，请尝试下载 SVG 矢量图。");
  }
}

async function openFullscreen() {
  fullscreenOpen.value = true;
  await nextTick();
  await renderMapFullscreen();
}

function closeFullscreen() {
  if (mmFs) {
    mmFs.destroy();
    mmFs = null;
  }
  fullscreenOpen.value = false;
}

function onKeydown(e) {
  if (e.key === "Escape" && fullscreenOpen.value) {
    closeFullscreen();
  }
}

watch(
  () => props.markdown,
  async (val) => {
    if (val) {
      await nextTick();
      await renderMap();
      if (fullscreenOpen.value) {
        await renderMapFullscreen();
      }
    }
  }
);

onMounted(() => {
  window.addEventListener("keydown", onKeydown);
  if (props.markdown) renderMap();
});

onBeforeUnmount(() => {
  window.removeEventListener("keydown", onKeydown);
  if (markmapInstance) {
    markmapInstance.destroy?.();
    markmapInstance = null;
  }
  if (mmFs) {
    mmFs.destroy?.();
    mmFs = null;
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
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 4px;
  max-width: calc(100% - 20px);
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
  flex-shrink: 0;
}

.mm-btn-text {
  width: auto;
  padding: 0 12px;
  font-size: 12px;
  font-weight: 600;
  font-family: inherit;
}

.mm-btn:hover {
  color: var(--accent-blue);
  border-color: var(--accent-blue-border);
  background: var(--accent-blue-light);
}

.mm-fs-divider {
  width: 1px;
  height: 20px;
  background: var(--border-color);
  align-self: center;
  margin: 0 2px;
}

.mindmap-svg {
  width: 100%;
  height: 420px;
  display: block;
}

/* Fullscreen */

.mindmap-fs-overlay {
  position: fixed;
  inset: 0;
  z-index: 10000;
  background: rgba(15, 23, 42, 0.55);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
  box-sizing: border-box;
}

.mindmap-fs-panel {
  position: relative;
  width: min(96vw, 1280px);
  height: min(88vh, 920px);
  background: #fefefe;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  overflow: hidden;
  border: 1px solid var(--border-color);
}

.mindmap-fs-toolbar {
  position: absolute;
  top: 12px;
  right: 12px;
  z-index: 10;
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  align-items: center;
  gap: 6px;
  max-width: calc(100% - 24px);
}

.mindmap-fs-svg {
  width: 100%;
  height: 100%;
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
