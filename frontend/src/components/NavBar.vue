<template>
  <nav class="navbar">
    <div class="container nav-inner">
      <a href="/" class="nav-brand" title="SaveAny - 万能视频下载总结器">
        <span class="brand-logo" role="img" aria-label="SaveAny">▶</span>
        <span class="brand-name">SaveAny</span>
        <span class="brand-tag">万能视频下载总结器</span>
      </a>

      <div class="nav-links" :class="{ open: mobileOpen }">
        <a href="#features" @click="mobileOpen = false">功能特性</a>
        <a href="#pricing" @click="mobileOpen = false">套餐价格</a>
        <a href="#platforms" @click="mobileOpen = false">支持平台</a>
        <a href="#faq" @click="mobileOpen = false">常见问题</a>
      </div>

      <button class="nav-vip" @click="$emit('vip')">
        <span class="vip-icon">☆</span> 开通 VIP
      </button>

      <button class="mobile-toggle" @click="mobileOpen = !mobileOpen" aria-label="菜单">
        <span></span><span></span><span></span>
      </button>
    </div>
  </nav>
</template>

<script setup>
import { ref } from "vue";
defineEmits(["vip"]);
const mobileOpen = ref(false);
</script>

<style scoped>
.navbar {
  position: sticky;
  top: 0;
  z-index: 100;
  background: var(--bg-primary);
  border-bottom: 1px solid var(--border-color);
  height: var(--nav-height);
}

.nav-inner {
  display: flex;
  align-items: center;
  height: 100%;
  gap: 32px;
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
  text-decoration: none;
  color: inherit;
}

.brand-logo {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  border-radius: 10px;
  background: var(--accent-blue);
  color: #fff;
  font-size: 14px;
}

.brand-name {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
}

.brand-tag {
  font-size: 12px;
  color: var(--accent-blue);
  background: var(--accent-blue-light);
  padding: 2px 8px;
  border-radius: var(--radius-full);
  font-weight: 500;
}

.nav-links {
  display: flex;
  gap: 28px;
  margin-left: auto;
}

.nav-links a {
  font-size: 14px;
  color: var(--text-secondary);
  font-weight: 500;
  transition: color 0.2s;
}

.nav-links a:hover {
  color: var(--text-primary);
}

.nav-vip {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 7px 18px;
  border-radius: var(--radius-full);
  border: 1px solid var(--accent-blue);
  background: transparent;
  color: var(--accent-blue);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  font-family: inherit;
  flex-shrink: 0;
}

.nav-vip:hover {
  background: var(--accent-blue-light);
}

.vip-icon {
  font-size: 14px;
}

.mobile-toggle {
  display: none;
  flex-direction: column;
  gap: 4px;
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
}

.mobile-toggle span {
  display: block;
  width: 20px;
  height: 2px;
  background: var(--text-primary);
  border-radius: 1px;
  transition: 0.2s;
}

@media (max-width: 768px) {
  .nav-links {
    display: none;
    position: absolute;
    top: var(--nav-height);
    left: 0;
    right: 0;
    flex-direction: column;
    background: var(--bg-primary);
    border-bottom: 1px solid var(--border-color);
    padding: 16px 24px;
    gap: 16px;
    box-shadow: var(--shadow-md);
  }

  .nav-links.open {
    display: flex;
  }

  .nav-vip {
    display: none;
  }

  .mobile-toggle {
    display: flex;
    margin-left: auto;
  }
}
</style>
