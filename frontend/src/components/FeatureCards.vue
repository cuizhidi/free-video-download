<template>
  <section id="features" class="features">
    <div class="container">
      <h2 class="section-title">为什么选择我们</h2>
      <p class="section-subtitle">极简体验，强大内核</p>

      <div class="features-grid">
        <div v-for="f in features" :key="f.title" class="card feature-card">
          <span class="feature-icon">{{ f.icon }}</span>
          <h3 class="feature-title">{{ f.title }}</h3>
          <p class="feature-desc">{{ f.desc }}</p>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
const features = [
  {
    icon: "⚡",
    title: "极速解析",
    desc: "基于强大的开源引擎，秒级解析视频信息，支持 1000+ 平台自动识别。",
  },
  {
    icon: "🎯",
    title: "多格式选择",
    desc: "自由选择画质与格式——从 360p 到 4K 超清，MP4 / WebM 任你挑选。",
  },
  {
    icon: "🔒",
    title: "安全无忧",
    desc: "无需注册，不保留任何个人数据，下载文件 30 分钟后自动清理。",
  },
  {
    icon: "📱",
    title: "全端适配",
    desc: "响应式设计，手机、平板、电脑均可流畅使用，随时随地下载。",
  },
];
</script>

<style scoped>
.features {
  padding: var(--section-padding);
  background: var(--bg-primary);
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.feature-card {
  padding: 32px 24px;
  text-align: center;
}

.feature-icon {
  font-size: 36px;
  display: block;
  margin-bottom: 16px;
}

.feature-title {
  font-size: 16px;
  font-weight: 700;
  margin-bottom: 10px;
  color: var(--text-primary);
}

.feature-desc {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.7;
}

@media (max-width: 1024px) {
  .features-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 520px) {
  .features-grid {
    grid-template-columns: 1fr;
  }
}
</style>
