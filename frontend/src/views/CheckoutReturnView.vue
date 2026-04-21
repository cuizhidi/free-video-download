<template>
  <div class="return-page">
    <div class="return-card card">
      <template v-if="loading">
        <div class="return-icon loading-icon">⏳</div>
        <h2>正在确认支付结果...</h2>
      </template>

      <template v-else-if="status === 'complete'">
        <div class="return-icon success-icon">✓</div>
        <h2>支付成功！</h2>
        <p class="return-desc">你已成为 VIP 会员，享受全部高级功能。</p>
        <router-link to="/" class="btn-primary return-btn">返回首页</router-link>
      </template>

      <template v-else>
        <div class="return-icon error-icon">✗</div>
        <h2>支付未完成</h2>
        <p class="return-desc">{{ message || '支付过程中出现问题，请重试。' }}</p>
        <router-link to="/checkout" class="btn-primary return-btn">重新支付</router-link>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRoute } from "vue-router";
import { getSessionStatus } from "../api/payment.js";
import { refreshUser } from "../stores/auth.js";

const route = useRoute();

const loading = ref(true);
const status = ref("");
const message = ref("");

function sleep(ms) {
  return new Promise((r) => setTimeout(r, ms));
}

onMounted(async () => {
  const sessionId = route.query.session_id;
  if (!sessionId) {
    status.value = "error";
    message.value = "缺少支付信息";
    loading.value = false;
    return;
  }

  try {
    const data = await getSessionStatus(sessionId);
    status.value = data.status;

    if (data.status === "complete") {
      for (let i = 0; i < 5; i++) {
        const user = await refreshUser();
        if (user?.is_vip) break;
        await sleep(2000);
      }
    }
  } catch (e) {
    status.value = "error";
    message.value = e.message;
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.return-page {
  min-height: calc(100vh - var(--nav-height) - 120px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  background: var(--bg-secondary);
}

.return-card {
  text-align: center;
  padding: 48px 40px;
  max-width: 440px;
  width: 100%;
}

.return-icon {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  margin: 0 auto 20px;
}

.success-icon {
  background: #dcfce7;
  color: var(--color-success);
}

.error-icon {
  background: #fee2e2;
  color: var(--color-error);
}

.loading-icon {
  background: var(--accent-blue-light);
  color: var(--accent-blue);
}

.return-card h2 {
  font-size: 22px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.return-desc {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 24px;
}

.return-btn {
  display: inline-block;
  padding: 12px 32px;
  font-size: 15px;
  border-radius: var(--radius-md);
  text-decoration: none;
}
</style>
