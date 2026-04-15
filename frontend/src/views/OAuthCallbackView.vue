<template>
  <div class="auth-page">
    <div class="auth-card card" style="text-align: center; padding: 48px 36px">
      <div class="auth-brand" style="justify-content: center; margin-bottom: 24px">
        <span class="brand-logo">▶</span>
        <span class="brand-name">SaveAny</span>
      </div>
      <p v-if="error" class="form-error" style="font-size: 15px">{{ error }}</p>
      <p v-else style="color: var(--text-secondary)">登录中，请稍候...</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { setAuth } from "../stores/auth.js";
import { useToast } from "../composables/useToast.js";

const router = useRouter();
const { showToast } = useToast();
const error = ref("");

onMounted(() => {
  const params = new URLSearchParams(window.location.search);
  const accessToken = params.get("access_token");
  const refreshToken = params.get("refresh_token");
  const userJson = params.get("user");

  if (!accessToken || !refreshToken || !userJson) {
    error.value = "登录失败，缺少认证信息";
    return;
  }

  try {
    const user = JSON.parse(userJson);
    setAuth({ access_token: accessToken, refresh_token: refreshToken, user });
    showToast("登录成功", "success");
    router.replace("/");
  } catch {
    error.value = "登录信息解析失败";
  }
});
</script>

<style scoped>
.auth-page {
  min-height: calc(100vh - var(--nav-height) - 120px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  background: var(--bg-secondary);
}

.auth-card {
  width: 100%;
  max-width: 420px;
}

.auth-brand {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.brand-logo {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: var(--accent-blue);
  color: #fff;
  font-size: 14px;
}

.brand-name {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
}

.form-error {
  color: var(--color-error);
}
</style>
