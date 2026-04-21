<template>
  <section v-if="videoInfo" class="ai-panel">
    <div class="container">
      <div class="card ai-card">
        <!-- Header -->
        <div class="ai-header">
          <div class="ai-header-left">
            <span class="ai-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
                <path d="M12 2a4 4 0 0 1 4 4v1a3 3 0 0 1 3 3v1a2 2 0 0 1-2 2h-1v3a4 4 0 0 1-8 0v-3H7a2 2 0 0 1-2-2v-1a3 3 0 0 1 3-3V6a4 4 0 0 1 4-4z"/>
                <circle cx="9" cy="10" r="1" fill="currentColor"/>
                <circle cx="15" cy="10" r="1" fill="currentColor"/>
              </svg>
            </span>
            <h3 class="ai-title">AI 智能分析</h3>
          </div>
          <div class="ai-header-right">
            <span v-if="quota && !quota.is_vip && !quotaExceeded" class="quota-badge">
              今日 {{ quota.used }}/{{ quota.limit }} 次
            </span>
            <span v-else-if="quota && quota.is_vip" class="quota-badge vip-quota">
              VIP 无限次
            </span>

            <template v-if="quotaExceeded && !started">
              <router-link to="/checkout" class="btn-primary ai-start-btn upgrade-btn">
                升级 VIP 解锁无限分析
              </router-link>
            </template>
            <template v-else>
              <button
                v-if="!started"
                class="btn-primary ai-start-btn"
                @click="startAnalysis"
                :disabled="loading"
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                  <polygon points="5,3 19,12 5,21"/>
                </svg>
                开始分析
              </button>
              <span v-else-if="loading" class="ai-status loading">
                <span class="dot-loader"></span>
                {{ statusText }}
              </span>
              <span v-else class="ai-status done">分析完成</span>
            </template>
          </div>
        </div>

        <!-- Tab Navigation (only shown after started) -->
        <div v-if="started" class="ai-tabs-nav">
          <button
            v-for="tab in tabs"
            :key="tab.key"
            class="tab-btn"
            :class="{ active: activeTab === tab.key }"
            @click="activeTab = tab.key"
          >
            {{ tab.label }}
          </button>
        </div>

        <!-- Tab Content -->
        <div v-if="started" class="ai-tabs-content">
          <SummaryTab
            v-show="activeTab === 'summary'"
            :content="summaryData.summary"
            :loading="loading"
          />
          <ChapterTab
            v-show="activeTab === 'chapters'"
            :chapters="summaryData.chapters"
            :loading="loading"
          />
          <KeyPointsTab
            v-show="activeTab === 'keypoints'"
            :points="summaryData.key_points"
            :loading="loading"
          />
          <TranscriptTab
            v-show="activeTab === 'transcript'"
            :segments="subtitleData.segments"
            :source="subtitleData.source"
            :language="subtitleData.language"
            :loading="subtitleLoading"
            :video-title="videoInfo?.title || ''"
          />
          <MindmapTab
            v-show="activeTab === 'mindmap'"
            :markdown="summaryData.mindmap"
            :loading="loading"
            :export-basename="videoInfo?.title || 'mindmap'"
          />
          <AIChatTab
            v-show="activeTab === 'chat'"
            :transcript="subtitleData.full_text"
            :title="videoInfo.title"
          />
        </div>

        <!-- Error -->
        <div v-if="errorMsg" class="ai-error">
          <span>{{ errorMsg }}</span>
          <button class="retry-btn" @click="startAnalysis">重试</button>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from "vue";
import { checkAIStatus, extractSubtitle, streamSummarize, fetchAIQuota } from "../api/ai.js";

import SummaryTab from "./SummaryTab.vue";
import ChapterTab from "./ChapterTab.vue";
import KeyPointsTab from "./KeyPointsTab.vue";
import TranscriptTab from "./TranscriptTab.vue";
import MindmapTab from "./MindmapTab.vue";
import AIChatTab from "./AIChatTab.vue";

const props = defineProps({
  videoInfo: { type: Object, default: null },
  url: { type: String, default: "" },
});

const quota = ref(null);
const quotaExceeded = computed(() =>
  quota.value && !quota.value.is_vip && quota.value.used >= quota.value.limit
);

onMounted(async () => {
  try {
    quota.value = await fetchAIQuota();
  } catch { /* ignore */ }
});

const tabs = [
  { key: "summary", label: "视频摘要" },
  { key: "chapters", label: "章节大纲" },
  { key: "keypoints", label: "知识要点" },
  { key: "transcript", label: "字幕文本" },
  { key: "mindmap", label: "思维导图" },
  { key: "chat", label: "AI 问答" },
];

const activeTab = ref("summary");
const started = ref(false);
const loading = ref(false);
const subtitleLoading = ref(false);
const errorMsg = ref("");
const phase = ref("");

const subtitleData = reactive({
  segments: [],
  full_text: "",
  language: "",
  source: "",
});

const summaryData = reactive({
  summary: "",
  chapters: [],
  key_points: [],
  mindmap: "",
});

let currentController = null;

const statusText = computed(() => {
  if (phase.value === "subtitle") return "正在提取字幕...";
  if (phase.value === "summarize") return "AI 正在分析中...";
  return "处理中...";
});

async function startAnalysis() {
  if (loading.value) return;

  errorMsg.value = "";
  started.value = true;
  loading.value = true;
  subtitleLoading.value = true;

  try {
    const status = await checkAIStatus();
    if (!status.available) {
      errorMsg.value = "AI 服务未配置，请在 backend/.env 中设置 AI_API_KEY 后重启服务";
      loading.value = false;
      subtitleLoading.value = false;
      return;
    }

    phase.value = "subtitle";
    const subRes = await extractSubtitle(props.url);
    if (subRes.success && subRes.data) {
      Object.assign(subtitleData, subRes.data);
    } else {
      throw new Error("字幕提取返回数据异常");
    }
    subtitleLoading.value = false;

    phase.value = "summarize";
    await runSummarize();
    fetchAIQuota().then((q) => (quota.value = q)).catch(() => {});
  } catch (e) {
    errorMsg.value = e.message || "分析失败";
    loading.value = false;
    subtitleLoading.value = false;
    fetchAIQuota().then((q) => (quota.value = q)).catch(() => {});
  }
}

function runSummarize() {
  return new Promise((resolve, reject) => {
    let accumulated = "";

    if (currentController) {
      currentController.abort();
    }

    currentController = streamSummarize(
      {
        transcript: subtitleData.full_text,
        title: props.videoInfo?.title || "",
        language: subtitleData.language || "zh",
      },
      {
        onChunk(text) {
          accumulated += text;
          tryParseSummary(accumulated);
        },
        onDone(fullContent) {
          const final = fullContent || accumulated;
          tryParseSummary(final);
          if (!summaryData.summary && final) {
            errorMsg.value = "AI 返回内容无法解析为结构化数据，可能需要增大 AI_MAX_TOKENS 或更换模型";
            console.warn("[AI] Unparseable response:", final.slice(0, 500));
          } else if (!summaryData.summary && !final) {
            errorMsg.value = "AI 未返回任何内容，模型可能将所有 token 用于推理。请在 .env 中增大 AI_MAX_TOKENS 或更换非推理模型";
          }
          loading.value = false;
          phase.value = "";
          resolve();
        },
        onError(msg) {
          errorMsg.value = msg;
          loading.value = false;
          phase.value = "";
          reject(new Error(msg));
        },
      }
    );
  });
}

function tryParseSummary(raw) {
  if (!raw) return;

  // Strip markdown code fences and <think> reasoning blocks
  let cleaned = raw
    .replace(/<think>[\s\S]*?<\/think>/g, "")
    .replace(/```json\s*/g, "")
    .replace(/```\s*/g, "");

  const jsonStr = extractJSON(cleaned);
  if (!jsonStr) return;

  try {
    const parsed = JSON.parse(jsonStr);
    if (parsed.summary) summaryData.summary = parsed.summary;
    if (parsed.chapters) summaryData.chapters = parsed.chapters;
    if (parsed.key_points) summaryData.key_points = parsed.key_points;
    if (parsed.mindmap) summaryData.mindmap = parsed.mindmap;
  } catch {
    // JSON not yet complete, this is expected during streaming
  }
}

function extractJSON(text) {
  let searchFrom = 0;
  while (searchFrom < text.length) {
    const start = text.indexOf("{", searchFrom);
    if (start < 0) return null;

    let depth = 0;
    let inStr = false;
    let escaped = false;
    let matchEnd = -1;

    for (let i = start; i < text.length; i++) {
      const ch = text[i];
      if (inStr) {
        if (escaped) { escaped = false; continue; }
        if (ch === "\\") { escaped = true; continue; }
        if (ch === '"') { inStr = false; }
        continue;
      }
      if (ch === '"') { inStr = true; continue; }
      if (ch === "{") depth++;
      else if (ch === "}") {
        depth--;
        if (depth === 0) { matchEnd = i; break; }
      }
    }

    if (matchEnd < 0) return null;

    const candidate = text.slice(start, matchEnd + 1);
    try {
      JSON.parse(candidate);
      return candidate;
    } catch {
      // This brace pair wasn't valid JSON; try the next { occurrence
      searchFrom = start + 1;
    }
  }
  return null;
}
</script>

<style scoped>
.ai-panel {
  padding: 0 0 40px;
}

.ai-card {
  padding: 28px;
}

.ai-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.ai-header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.ai-header-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.quota-badge {
  font-size: 11px;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: var(--radius-full);
  background: var(--bg-secondary);
  color: var(--text-muted);
  border: 1px solid var(--border-color);
  white-space: nowrap;
}

.quota-badge.vip-quota {
  background: linear-gradient(135deg, #fffbeb, #fef3c7);
  color: #92400e;
  border-color: #fde68a;
}

.upgrade-btn {
  text-decoration: none;
  background: linear-gradient(135deg, #f59e0b, #d97706);
}

.upgrade-btn:hover {
  background: linear-gradient(135deg, #d97706, #b45309);
}

.ai-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: var(--radius-sm);
  background: linear-gradient(135deg, #ede9fe, #dbeafe);
  color: #7c3aed;
}

.ai-title {
  font-size: 17px;
  font-weight: 700;
  color: var(--text-primary);
}

.ai-start-btn {
  padding: 10px 24px;
  font-size: 14px;
  border-radius: var(--radius-full);
  gap: 6px;
}

.ai-status {
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.ai-status.loading {
  color: var(--accent-blue);
}

.ai-status.done {
  color: var(--color-success);
  font-weight: 600;
}

.dot-loader {
  display: inline-flex;
  gap: 4px;
}

.dot-loader::before,
.dot-loader::after {
  content: "";
  display: inline-block;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--accent-blue);
  animation: dot-pulse 1.2s ease-in-out infinite;
}

.dot-loader::after {
  animation-delay: 0.4s;
}

@keyframes dot-pulse {
  0%, 100% { opacity: 0.3; transform: scale(0.8); }
  50% { opacity: 1; transform: scale(1); }
}

/* Tabs */

.ai-tabs-nav {
  display: flex;
  gap: 4px;
  border-bottom: 1px solid var(--border-color);
  margin-bottom: 20px;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

.tab-btn {
  padding: 10px 18px;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s ease;
  font-family: inherit;
}

.tab-btn:hover {
  color: var(--text-primary);
  background: var(--bg-secondary);
}

.tab-btn.active {
  color: var(--accent-blue);
  border-bottom-color: var(--accent-blue);
  font-weight: 600;
}

.ai-tabs-content {
  min-height: 200px;
}

/* Error */

.ai-error {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  margin-top: 16px;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: var(--radius-md);
  color: var(--color-error);
  font-size: 13px;
}

.retry-btn {
  padding: 6px 16px;
  font-size: 12px;
  font-weight: 600;
  background: var(--color-error);
  color: #fff;
  border: none;
  border-radius: var(--radius-full);
  cursor: pointer;
  white-space: nowrap;
  font-family: inherit;
}

.retry-btn:hover {
  opacity: 0.9;
}

@media (max-width: 768px) {
  .ai-card {
    padding: 20px;
  }

  .tab-btn {
    padding: 8px 14px;
    font-size: 12px;
  }
}
</style>
