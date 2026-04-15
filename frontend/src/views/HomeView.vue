<template>
  <div>
    <HeroSection v-model="url" :loading="parsing" @parse="handleParse" />

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

    <AISummaryPanel v-if="videoInfo" :video-info="videoInfo" :url="url" />

    <PlatformBar />
    <FeatureCards />
    <PricingSection />
    <FAQSection />
  </div>
</template>

<script setup>
import { ref, reactive, computed } from "vue";
import { parseVideo, downloadVideo } from "../api/index.js";
import { useToast } from "../composables/useToast.js";

import HeroSection from "../components/HeroSection.vue";
import VideoResult from "../components/VideoResult.vue";
import DownloadProgress from "../components/DownloadProgress.vue";
import PlatformBar from "../components/PlatformBar.vue";
import FeatureCards from "../components/FeatureCards.vue";
import PricingSection from "../components/PricingSection.vue";
import AISummaryPanel from "../components/AISummaryPanel.vue";
import FAQSection from "../components/FAQSection.vue";

const { showToast } = useToast();

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
  () =>
    downloading.value ||
    progress.status === "done" ||
    progress.status === "error",
);

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
  if (lastFormatId) handleDownload(lastFormatId);
}
</script>
