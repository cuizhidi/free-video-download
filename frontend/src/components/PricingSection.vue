<template>
  <section id="pricing" class="pricing">
    <div class="container">
      <h2 class="section-title">解锁全部能力</h2>
      <p class="section-subtitle">免费畅享核心功能，升级会员体验更多</p>

      <div class="pricing-grid">
        <!-- Free Tier -->
        <div class="card pricing-card">
          <div class="pricing-header">
            <h3 class="plan-name">免费版</h3>
            <div class="plan-price">
              <span class="price-amount">¥0</span>
              <span class="price-period">/永久</span>
            </div>
          </div>
          <ul class="plan-features">
            <li v-for="f in freePlan" :key="f.text" :class="{ disabled: !f.included }">
              <span class="check" :class="f.included ? 'yes' : 'no'">{{ f.included ? '✓' : '✗' }}</span>
              {{ f.text }}
            </li>
          </ul>
          <button class="btn-outline" disabled>当前方案</button>
        </div>

        <!-- Pro Tier -->
        <div class="card pricing-card pro">
          <div class="pro-badge">推荐</div>
          <div class="pricing-header">
            <h3 class="plan-name">会员版</h3>
            <div class="plan-price">
              <span class="price-amount pro-price">¥9.9</span>
              <span class="price-period">/月</span>
            </div>
          </div>
          <ul class="plan-features">
            <li v-for="f in proPlan" :key="f.text">
              <span class="check yes">✓</span>
              {{ f.text }}
            </li>
          </ul>
          <button class="btn-primary pro-btn" @click="handleUpgrade">立即升级</button>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
const freePlan = [
  { text: "每日 3 次下载", included: true },
  { text: "最高 720p 画质", included: true },
  { text: "支持主流平台", included: true },
  { text: "批量下载", included: false },
  { text: "4K / 原画画质", included: false },
  { text: "音频提取 (MP3)", included: false },
  { text: "字幕下载", included: false },
  { text: "去广告", included: false },
];

const proPlan = [
  { text: "无限次下载" },
  { text: "4K / 原画画质" },
  { text: "支持 1000+ 平台" },
  { text: "批量下载 & 播放列表" },
  { text: "音频提取 (MP3/M4A)" },
  { text: "字幕下载 (SRT/VTT)" },
  { text: "高速下载通道" },
  { text: "无广告体验" },
];

function handleUpgrade() {
  alert("会员系统即将上线，敬请期待！");
}
</script>

<style scoped>
.pricing {
  padding: var(--section-padding);
  background: var(--bg-secondary);
}

.pricing-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
  max-width: 760px;
  margin: 0 auto;
}

.pricing-card {
  padding: 36px 32px;
  position: relative;
  display: flex;
  flex-direction: column;
}

.pricing-card.pro {
  border-color: var(--accent-blue);
  box-shadow: 0 4px 20px rgba(37, 99, 235, 0.12);
}

.pro-badge {
  position: absolute;
  top: -1px;
  right: 24px;
  background: var(--accent-blue);
  color: #fff;
  font-size: 12px;
  font-weight: 700;
  padding: 4px 16px;
  border-radius: 0 0 8px 8px;
}

.pricing-header {
  margin-bottom: 28px;
}

.plan-name {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 8px;
  color: var(--text-primary);
}

.price-amount {
  font-size: 40px;
  font-weight: 800;
  color: var(--text-primary);
}

.pro-price {
  background: var(--accent-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.price-period {
  font-size: 14px;
  color: var(--text-muted);
  margin-left: 4px;
}

.plan-features {
  list-style: none;
  flex: 1;
  margin-bottom: 28px;
}

.plan-features li {
  font-size: 14px;
  padding: 7px 0;
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--text-secondary);
}

.plan-features li.disabled {
  opacity: 0.45;
}

.check {
  font-weight: 700;
  width: 20px;
  text-align: center;
  font-size: 13px;
}

.check.yes {
  color: var(--color-success);
}

.check.no {
  color: var(--color-error);
}

.btn-outline {
  width: 100%;
  padding: 12px;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
  background: transparent;
  color: var(--text-muted);
  font-size: 15px;
  font-weight: 600;
  cursor: default;
  font-family: inherit;
}

.pro-btn {
  width: 100%;
  padding: 13px;
  font-size: 15px;
  border-radius: var(--radius-md);
}

@media (max-width: 640px) {
  .pricing-grid {
    grid-template-columns: 1fr;
  }
}
</style>
