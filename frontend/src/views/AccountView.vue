<template>
  <div class="account-page">
    <div class="account-container">
      <h1 class="account-title">账户设置</h1>

      <!-- Profile card -->
      <div class="card account-card">
        <h2 class="card-title">个人信息</h2>
        <div class="profile-row">
          <div class="profile-avatar">{{ userInitial }}</div>
          <div class="profile-info">
            <span class="profile-name">{{ currentUser?.name }}</span>
            <span class="profile-email">{{ currentUser?.email }}</span>
            <span class="profile-provider">
              登录方式：{{ providerLabel }}
            </span>
          </div>
        </div>
      </div>

      <!-- Subscription card -->
      <div class="card account-card">
        <h2 class="card-title">会员订阅</h2>

        <div v-if="subLoading" class="sub-loading">加载中...</div>

        <template v-else-if="subscription?.has_subscription">
          <div class="sub-status">
            <span class="sub-badge active">VIP 会员</span>
            <span class="sub-plan">{{ planLabel }}</span>
          </div>
          <div class="sub-details">
            <div class="sub-row">
              <span class="sub-label">状态</span>
              <span class="sub-value" :class="'status-' + subscription.status">
                {{ statusLabel }}
              </span>
            </div>
            <div class="sub-row">
              <span class="sub-label">到期时间</span>
              <span class="sub-value">{{ periodEnd }}</span>
            </div>
            <div v-if="subscription.cancel_at_period_end" class="sub-row">
              <span class="sub-label">续订</span>
              <span class="sub-value status-canceled">将在到期后取消</span>
            </div>
          </div>
          <button class="btn-outline manage-btn" @click="openPortal" :disabled="portalLoading">
            {{ portalLoading ? '跳转中...' : '管理订阅' }}
          </button>
        </template>

        <template v-else>
          <div class="no-sub">
            <p>你还没有订阅任何套餐</p>
            <router-link to="/checkout" class="btn-primary upgrade-btn">升级 VIP</router-link>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { currentUser } from "../stores/auth.js";
import { getSubscription, createPortalSession } from "../api/payment.js";
import { useToast } from "../composables/useToast.js";

const { showToast } = useToast();

const subscription = ref(null);
const subLoading = ref(true);
const portalLoading = ref(false);

const userInitial = computed(() => {
  return (currentUser.value?.name || "U").charAt(0).toUpperCase();
});

const providerLabel = computed(() => {
  const map = { email: "邮箱密码", google: "Google", github: "GitHub" };
  return map[currentUser.value?.auth_provider] || "邮箱密码";
});

const planLabel = computed(() => {
  const map = { monthly: "月度会员", yearly: "年度会员" };
  return map[subscription.value?.plan_type] || "会员";
});

const statusLabel = computed(() => {
  const map = {
    active: "正常",
    trialing: "试用中",
    past_due: "待支付",
    canceled: "已取消",
  };
  return map[subscription.value?.status] || subscription.value?.status;
});

const periodEnd = computed(() => {
  if (!subscription.value?.current_period_end) return "-";
  return new Date(subscription.value.current_period_end).toLocaleDateString("zh-CN", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
});

onMounted(async () => {
  try {
    subscription.value = await getSubscription();
  } catch {
    subscription.value = { has_subscription: false };
  } finally {
    subLoading.value = false;
  }
});

async function openPortal() {
  portalLoading.value = true;
  try {
    const data = await createPortalSession();
    window.location.href = data.url;
  } catch (e) {
    showToast(e.message, "error");
  } finally {
    portalLoading.value = false;
  }
}
</script>

<style scoped>
.account-page {
  min-height: calc(100vh - var(--nav-height) - 120px);
  background: var(--bg-secondary);
  padding: 40px 20px;
}

.account-container {
  max-width: 600px;
  margin: 0 auto;
}

.account-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 24px;
}

.account-card {
  padding: 28px;
  margin-bottom: 16px;
}

.card-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 20px;
}

.profile-row {
  display: flex;
  align-items: center;
  gap: 16px;
}

.profile-avatar {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: var(--accent-blue-light);
  color: var(--accent-blue);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  font-weight: 700;
  flex-shrink: 0;
}

.profile-info {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.profile-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.profile-email {
  font-size: 13px;
  color: var(--text-muted);
}

.profile-provider {
  font-size: 12px;
  color: var(--text-muted);
}

/* Subscription */

.sub-loading {
  color: var(--text-muted);
  font-size: 14px;
}

.sub-status {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}

.sub-badge {
  padding: 4px 12px;
  border-radius: var(--radius-full);
  font-size: 12px;
  font-weight: 700;
}

.sub-badge.active {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: #fff;
}

.sub-plan {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}

.sub-details {
  margin-bottom: 20px;
}

.sub-row {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid var(--border-color);
}

.sub-row:last-child {
  border-bottom: none;
}

.sub-label {
  font-size: 13px;
  color: var(--text-muted);
}

.sub-value {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}

.status-active {
  color: var(--color-success);
}

.status-past_due {
  color: var(--color-warning);
}

.status-canceled {
  color: var(--color-error);
}

.manage-btn {
  width: 100%;
  padding: 10px;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
  background: transparent;
  color: var(--text-secondary);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  font-family: inherit;
  transition: all 0.2s;
}

.manage-btn:hover {
  background: var(--bg-secondary);
  border-color: var(--text-muted);
}

.manage-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.no-sub {
  text-align: center;
  padding: 16px 0;
}

.no-sub p {
  font-size: 14px;
  color: var(--text-muted);
  margin-bottom: 16px;
}

.upgrade-btn {
  display: inline-block;
  padding: 10px 32px;
  font-size: 14px;
  border-radius: var(--radius-md);
  text-decoration: none;
}
</style>
