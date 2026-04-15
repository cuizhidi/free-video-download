<template>
  <div class="app-shell">
    <Transition name="fade">
      <div
        v-if="toast.visible"
        class="toast"
        :class="toast.type === 'error' ? 'toast-error' : 'toast-success'"
      >
        {{ toast.message }}
      </div>
    </Transition>

    <NavBar />

    <main class="main-content">
      <router-view />
    </main>

    <footer class="site-footer">
      <div class="container footer-inner">
        <p>&copy; {{ new Date().getFullYear() }} <a href="/" title="SaveAny 万能视频下载总结器">SaveAny</a> &mdash; 万能视频下载总结器</p>
        <p class="footer-disclaimer">
          本工具仅供个人学习和研究使用，请勿用于侵犯他人版权的行为。
          <br />支持 YouTube、Bilibili、抖音、TikTok、Twitter/X、Instagram 等 1000+ 平台视频下载与 AI 智能总结。
        </p>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { useToast } from "./composables/useToast.js";
import NavBar from "./components/NavBar.vue";

const { toast } = useToast();
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

.footer-inner a {
  color: var(--text-muted);
  text-decoration: none;
  font-weight: 600;
}

.footer-inner a:hover {
  color: var(--accent-blue);
}

.footer-disclaimer {
  margin-top: 4px;
  font-size: 12px;
  line-height: 1.8;
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
