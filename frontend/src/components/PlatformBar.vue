<template>
  <section id="platforms" class="platforms">
    <div class="container">
      <h2 class="section-title">支持平台</h2>
      <p class="section-subtitle">基于强大开源引擎，支持 1000+ 视频网站</p>

      <div class="platform-grid">
        <div
          v-for="p in platforms"
          :key="p.name"
          class="platform-chip"
        >
          <span class="chip-emoji">{{ p.emoji }}</span>
          <span class="chip-name">{{ p.name }}</span>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
const platforms = [
  { name: "YouTube",   emoji: "▶️"  },
  { name: "Bilibili",  emoji: "📺" },
  { name: "TikTok",    emoji: "🎵" },
  { name: "抖音",       emoji: "🎶" },
  { name: "X / Twitter", emoji: "🐦" },
  { name: "Instagram", emoji: "📷" },
  { name: "小红书",     emoji: "📕" },
  { name: "微博",       emoji: "🌐" },
  { name: "Vimeo",     emoji: "🎬" },
  { name: "Facebook",  emoji: "📘" },
  { name: "Twitch",    emoji: "🎮" },
  { name: "更多 1000+", emoji: "➕" },
];
</script>

<style scoped>
.platforms {
  padding: var(--section-padding);
  background: var(--bg-secondary);
}

.platform-grid {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 12px;
  max-width: 700px;
  margin: 0 auto;
}

.platform-chip {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: var(--radius-full);
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  font-size: 14px;
  color: var(--text-secondary);
  transition: all 0.2s;
}

.platform-chip:hover {
  border-color: var(--accent-blue-border);
  color: var(--accent-blue);
  background: var(--accent-blue-light);
}

.chip-emoji {
  font-size: 16px;
}

.chip-name {
  font-weight: 500;
}
</style>
