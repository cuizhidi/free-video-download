<template>
  <section id="faq" class="faq">
    <div class="container">
      <h2 class="section-title">常见问题</h2>
      <p class="section-subtitle">关于 SaveAny 万能视频下载总结器的常见疑问</p>

      <div class="faq-list">
        <details
          v-for="(item, idx) in faqs"
          :key="idx"
          class="faq-item"
          :open="idx === 0"
        >
          <summary class="faq-question">
            <span class="faq-q-text">{{ item.q }}</span>
            <span class="faq-arrow">›</span>
          </summary>
          <div class="faq-answer">
            <p>{{ item.a }}</p>
          </div>
        </details>
      </div>
    </div>
  </section>
</template>

<script setup>
const faqs = [
  {
    q: "SaveAny 是什么？",
    a: "SaveAny 是一款免费的在线视频下载与 AI 智能总结工具。它支持从 YouTube、Bilibili、抖音、TikTok、Twitter/X、Instagram、小红书等 1000+ 平台下载视频，同时利用 AI 技术自动生成视频摘要、章节大纲、知识要点和思维导图，帮助用户高效获取视频核心内容。",
  },
  {
    q: "如何使用 SaveAny 下载视频？",
    a: "只需三步：第一步，复制你想下载的视频链接，粘贴到 SaveAny 的输入框中；第二步，点击「解析视频」按钮，系统会自动识别平台并解析视频信息；第三步，从可用格式列表中选择需要的画质（360p 到 4K），点击「开始下载」即可保存到本地。",
  },
  {
    q: "SaveAny 支持哪些视频平台？",
    a: "SaveAny 基于 yt-dlp 开源引擎，支持 YouTube、Bilibili（B站）、抖音、TikTok、Twitter/X、Instagram、小红书、微博、Vimeo、Facebook、Twitch 等 1000+ 视频平台。几乎覆盖了全球所有主流视频网站。",
  },
  {
    q: "SaveAny 是免费的吗？",
    a: "是的，SaveAny 的核心功能完全免费，包括视频下载和 AI 智能总结。免费版每日支持 3 次下载，最高 720p 画质。如需无限下载、4K 原画画质、批量下载、音频提取等高级功能，可升级会员版（¥9.9/月）。",
  },
  {
    q: "SaveAny 的 AI 智能总结功能怎么用？",
    a: "视频解析完成后，页面会自动展示 AI 分析面板。AI 会自动获取视频字幕或进行语音识别，然后生成视频摘要、章节大纲、关键知识点和思维导图。你还可以在 AI 问答标签页中就视频内容向 AI 提问，获得精准回答。整个过程无需额外操作。",
  },
  {
    q: "SaveAny 可以下载无水印的抖音视频吗？",
    a: "可以。SaveAny 对抖音有专门的下载模块，能够自动获取无水印版本的视频，而且无需提供 cookies 或登录信息，直接粘贴抖音视频链接即可下载。",
  },
  {
    q: "在手机上可以使用 SaveAny 吗？",
    a: "可以。SaveAny 采用响应式设计，在手机、平板和电脑上均可流畅使用。无需安装任何应用程序，直接通过浏览器访问 maxczd.com 即可使用全部功能。",
  },
  {
    q: "下载的视频安全吗？会保留我的数据吗？",
    a: "完全安全。SaveAny 无需注册即可使用，不保留任何用户个人数据。下载的视频文件会在 30 分钟后自动从服务器清理，充分保护你的隐私安全。",
  },
];
</script>

<style scoped>
.faq {
  padding: var(--section-padding);
  background: var(--bg-primary);
}

.faq-list {
  max-width: 760px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.faq-item {
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  background: var(--bg-card);
  overflow: hidden;
  transition: box-shadow 0.2s ease;
}

.faq-item:hover {
  box-shadow: var(--shadow-sm);
}

.faq-item[open] {
  box-shadow: var(--shadow-md);
  border-color: var(--accent-blue-border);
}

.faq-question {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 24px;
  cursor: pointer;
  font-weight: 600;
  font-size: 15px;
  color: var(--text-primary);
  list-style: none;
  user-select: none;
  transition: color 0.2s;
}

.faq-question::-webkit-details-marker {
  display: none;
}

.faq-question:hover {
  color: var(--accent-blue);
}

.faq-q-text {
  flex: 1;
  padding-right: 16px;
}

.faq-arrow {
  font-size: 20px;
  color: var(--text-muted);
  transition: transform 0.25s ease;
  flex-shrink: 0;
}

.faq-item[open] .faq-arrow {
  transform: rotate(90deg);
  color: var(--accent-blue);
}

.faq-answer {
  padding: 0 24px 20px;
  font-size: 14px;
  line-height: 1.8;
  color: var(--text-secondary);
}

.faq-answer p {
  margin: 0;
}

@media (max-width: 768px) {
  .faq-question {
    padding: 14px 16px;
    font-size: 14px;
  }

  .faq-answer {
    padding: 0 16px 16px;
    font-size: 13px;
  }
}
</style>
