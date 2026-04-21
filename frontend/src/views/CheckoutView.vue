<template>
  <div class="checkout-page">
    <div class="checkout-container">
      <div class="checkout-header">
        <router-link to="/" class="back-link">&larr; 返回首页</router-link>
        <h1 class="checkout-title">升级 VIP 会员</h1>
        <p class="checkout-subtitle">选择套餐，解锁全部功能</p>
      </div>

      <!-- Plan selection -->
      <div v-if="!clientSecret" class="plan-selection">
        <div
          class="plan-card card"
          :class="{ selected: selectedPlan === 'monthly' }"
          @click="selectedPlan = 'monthly'"
        >
          <div class="plan-info">
            <h3>月度会员</h3>
            <div class="plan-price">¥9.9<span>/月</span></div>
          </div>
          <div class="plan-check">
            <span v-if="selectedPlan === 'monthly'" class="check-icon">✓</span>
          </div>
        </div>

        <div
          class="plan-card card"
          :class="{ selected: selectedPlan === 'yearly' }"
          @click="selectedPlan = 'yearly'"
        >
          <div class="plan-badge">省 ¥19.8</div>
          <div class="plan-info">
            <h3>年度会员</h3>
            <div class="plan-price">¥99<span>/年</span></div>
            <p class="plan-note">相当于 ¥8.25/月</p>
          </div>
          <div class="plan-check">
            <span v-if="selectedPlan === 'yearly'" class="check-icon">✓</span>
          </div>
        </div>

        <button
          class="btn-primary checkout-btn"
          :disabled="loading"
          @click="handleCheckout"
        >
          {{ loading ? "正在创建订单..." : "继续支付" }}
        </button>

        <p v-if="error" class="form-error">{{ error }}</p>
      </div>

      <!-- Embedded Stripe Checkout -->
      <div v-if="clientSecret" id="checkout-embed" ref="checkoutRef"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from "vue";
import { useRouter } from "vue-router";
import { isLoggedIn } from "../stores/auth.js";
import { createCheckoutSession, fetchConfig } from "../api/payment.js";
import { loadStripe } from "@stripe/stripe-js";

const router = useRouter();

const selectedPlan = ref("monthly");
const loading = ref(false);
const error = ref("");
const clientSecret = ref("");
const checkoutRef = ref(null);

let stripePromise = null;
let checkoutInstance = null;

onMounted(async () => {
  if (!isLoggedIn.value) {
    router.replace("/login?redirect=/checkout");
    return;
  }
  const config = await fetchConfig();
  if (config.stripe_publishable_key) {
    stripePromise = loadStripe(config.stripe_publishable_key);
  }
});

onUnmounted(() => {
  if (checkoutInstance) {
    checkoutInstance.destroy();
  }
});

async function handleCheckout() {
  if (loading.value) return;
  error.value = "";
  loading.value = true;

  try {
    const data = await createCheckoutSession(selectedPlan.value);
    clientSecret.value = data.client_secret;

    const stripe = await stripePromise;
    if (!stripe) {
      error.value = "Stripe 初始化失败，请检查配置";
      loading.value = false;
      return;
    }

    await new Promise((r) => setTimeout(r, 50));

    const result = await stripe.createEmbeddedCheckoutPage({ clientSecret: clientSecret.value });
    checkoutInstance = result;
    result.mount("#checkout-embed");
  } catch (e) {
    error.value = e.message;
    clientSecret.value = "";
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.checkout-page {
  min-height: calc(100vh - var(--nav-height) - 120px);
  background: var(--bg-secondary);
  padding: 40px 20px;
}

.checkout-container {
  max-width: 520px;
  margin: 0 auto;
}

.checkout-header {
  text-align: center;
  margin-bottom: 32px;
}

.back-link {
  display: inline-block;
  margin-bottom: 16px;
  font-size: 13px;
  color: var(--text-muted);
  text-decoration: none;
}

.back-link:hover {
  color: var(--accent-blue);
}

.checkout-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 6px;
}

.checkout-subtitle {
  font-size: 14px;
  color: var(--text-muted);
}

.plan-selection {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.plan-card {
  display: flex;
  align-items: center;
  padding: 20px 24px;
  cursor: pointer;
  border: 2px solid var(--border-color);
  transition: all 0.2s;
  position: relative;
}

.plan-card.selected {
  border-color: var(--accent-blue);
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.plan-badge {
  position: absolute;
  top: -1px;
  right: 16px;
  background: var(--color-success);
  color: #fff;
  font-size: 11px;
  font-weight: 700;
  padding: 3px 10px;
  border-radius: 0 0 6px 6px;
}

.plan-info {
  flex: 1;
}

.plan-info h3 {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.plan-price {
  font-size: 28px;
  font-weight: 800;
  color: var(--text-primary);
}

.plan-price span {
  font-size: 14px;
  font-weight: 400;
  color: var(--text-muted);
}

.plan-note {
  font-size: 12px;
  color: var(--color-success);
  margin-top: 2px;
}

.plan-check {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: 2px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.plan-card.selected .plan-check {
  border-color: var(--accent-blue);
  background: var(--accent-blue);
}

.check-icon {
  color: #fff;
  font-size: 14px;
  font-weight: 700;
}

.checkout-btn {
  width: 100%;
  padding: 14px;
  font-size: 16px;
  border-radius: var(--radius-md);
  margin-top: 8px;
}

.checkout-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.form-error {
  color: var(--color-error);
  font-size: 13px;
  text-align: center;
  margin-top: 8px;
}

#checkout-embed {
  min-height: 400px;
}
</style>
