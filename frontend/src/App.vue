<template>
  <div class="app-shell">
    <!-- Toast -->
    <Transition name="fade">
      <div
        v-if="toast.visible"
        class="toast"
        :class="toast.type === 'error' ? 'toast-error' : 'toast-success'"
      >
        {{ toast.message }}
      </div>
    </Transition>

    <NavBar @vip="handleVip" />

    <main class="main-content">
      <HeroSection
        v-model="url"
        :loading="parsing"
        @parse="handleParse"
      />

      <VideoResult
        :info="videoInfo"
        :downloading="downloading"
        @download="handleDownload"
      />

      <DownloadProgress
        :visible="showProgress"
        :status="progress.status"
        :percent="progress.percent"
        :speed="progress.speed"
        :eta="progress.eta"
        :filename="progress.filename"
        :error-message="progress.errorMessage"
        @retry="handleRetry"
      />

      <AISummaryPanel
        v-if="videoInfo"
        :video-info="videoInfo"
        :url="url"
      />

      <PlatformBar />
      <FeatureCards />
      <PricingSection />
    </main>

    <footer class="site-footer">
      <div class="container footer-inner">
        <p>&copy; {{ new Date().getFullYear() }} SaveAny &mdash; 万能视频下载工具</p>
        <p class="footer-disclaimer">
          本工具仅供个人学习和研究使用，请勿用于侵犯他人版权的行为。
        </p>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from "vue";
import { parseVideo, downloadVideo } from "./api/index.js";

import NavBar from "./components/NavBar.vue";
import HeroSection from "./components/HeroSection.vue";
import FeatureCards from "./components/FeatureCards.vue";
import VideoResult from "./components/VideoResult.vue";
import DownloadProgress from "./components/DownloadProgress.vue";
import PricingSection from "./components/PricingSection.vue";
import PlatformBar from "./components/PlatformBar.vue";
import AISummaryPanel from "./components/AISummaryPanel.vue";

const url = ref("");
const parsing = ref(false);
const videoInfo = ref(null);
const downloading = ref(false);
let currentSSE = null;

const progress = reactive({
  status: "idle",
  percent: 0,
  speed: "",
  eta: "",
  filename: "",
  errorMessage: "",
});

const showProgress = computed(
  () => downloading.value || progress.status === "done" || progress.status === "error"
);

const toast = reactive({ visible: false, message: "", type: "error" });
let toastTimer = null;

function showToast(msg, type = "error") {
  clearTimeout(toastTimer);
  toast.visible = true;
  toast.message = msg;
  toast.type = type;
  toastTimer = setTimeout(() => {
    toast.visible = false;
  }, 4000);
}

function resetProgress() {
  Object.assign(progress, {
    status: "idle",
    percent: 0,
    speed: "",
    eta: "",
    filename: "",
    errorMessage: "",
  });
}

function handleVip() {
  alert("会员系统即将上线，敬请期待！");
}

async function handleParse(inputUrl) {
  if (parsing.value) return;
  parsing.value = true;
  videoInfo.value = null;
  resetProgress();

  try {
    const res = await parseVideo(inputUrl);
    if (res.success && res.data) {
      videoInfo.value = res.data;
    } else {
      showToast(res.error || "解析失败");
    }
  } catch (e) {
    showToast(e.message || "解析失败，请检查链接");
  } finally {
    parsing.value = false;
  }
}

let lastFormatId = null;

function handleDownload(formatId) {
  if (downloading.value) return;
  downloading.value = true;
  lastFormatId = formatId;
  resetProgress();
  progress.status = "downloading";

  if (currentSSE) {
    currentSSE.close();
    currentSSE = null;
  }

  currentSSE = downloadVideo(url.value, formatId, {
    onProgress(data) {
      progress.status = data.status || "downloading";
      progress.percent = data.percent ?? progress.percent;
      progress.speed = data.speed || "";
      progress.eta = data.eta || "";
    },
    onComplete(data) {
      downloading.value = false;
      progress.status = "done";
      progress.percent = 100;
      progress.filename = data.filename || "";
      showToast("下载完成！点击保存到本地", "success");
    },
    onError(data) {
      downloading.value = false;
      progress.status = "error";
      progress.errorMessage = data.message || "下载失败";
      showToast(data.message || "下载失败", "error");
    },
  });
}

function handleRetry() {
  if (lastFormatId) {
    handleDownload(lastFormatId);
  }
}
</script>

<style scoped>
.app-shell {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background: var(--bg-primary);
}

.main-content {
  flex: 1;
}

.site-footer {
  padding: 28px 0;
  border-top: 1px solid var(--border-color);
  background: var(--bg-secondary);
}

.footer-inner {
  text-align: center;
  font-size: 13px;
  color: var(--text-muted);
}

.footer-disclaimer {
  margin-top: 4px;
  font-size: 12px;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(-10px);
}
</style>
