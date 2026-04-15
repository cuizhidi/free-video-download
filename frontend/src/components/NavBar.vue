<template>
  <nav class="navbar">
    <div class="container nav-inner">
      <router-link to="/" class="nav-brand" title="SaveAny - 万能视频下载总结器">
        <span class="brand-logo" role="img" aria-label="SaveAny">▶</span>
        <span class="brand-name">SaveAny</span>
        <span class="brand-tag">万能视频下载总结器</span>
      </router-link>

      <div class="nav-links" :class="{ open: mobileOpen }">
        <router-link to="/#features" @click="mobileOpen = false">功能特性</router-link>
        <router-link to="/#pricing" @click="mobileOpen = false">套餐价格</router-link>
        <router-link to="/#platforms" @click="mobileOpen = false">支持平台</router-link>
        <router-link to="/#faq" @click="mobileOpen = false">常见问题</router-link>
      </div>

      <div class="nav-actions">
        <template v-if="isLoggedIn">
          <span v-if="isVip" class="vip-badge">VIP</span>
          <button v-else class="nav-vip" @click="handleUpgrade">
            <span class="vip-icon">☆</span> 开通 VIP
          </button>
          <div class="user-menu" ref="menuRef">
            <button class="user-avatar-btn" @click="showMenu = !showMenu">
              {{ userInitial }}
            </button>
            <Transition name="dropdown">
              <div v-if="showMenu" class="user-dropdown">
                <div class="dropdown-header">
                  <span class="dropdown-name">{{ currentUser?.name }}</span>
                  <span class="dropdown-email">{{ currentUser?.email }}</span>
                </div>
                <div class="dropdown-divider"></div>
                <router-link to="/account" class="dropdown-item" @click="showMenu = false">账户设置</router-link>
                <button class="dropdown-item logout" @click="handleLogout">退出登录</button>
              </div>
            </Transition>
          </div>
        </template>
        <template v-else>
          <router-link to="/login" class="nav-login">登录</router-link>
          <router-link to="/register" class="nav-register-btn">注册</router-link>
        </template>
      </div>

      <button class="mobile-toggle" @click="mobileOpen = !mobileOpen" aria-label="菜单">
        <span></span><span></span><span></span>
      </button>
    </div>
  </nav>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue";
import { useRouter } from "vue-router";
import { isLoggedIn, currentUser, isVip } from "../stores/auth.js";
import { logout } from "../api/auth.js";

const router = useRouter();
const mobileOpen = ref(false);
const showMenu = ref(false);
const menuRef = ref(null);

const userInitial = computed(() => {
  const name = currentUser.value?.name || "";
  return name.charAt(0).toUpperCase();
});

function handleUpgrade() {
  router.push("/checkout");
}

function handleLogout() {
  logout();
  showMenu.value = false;
  router.push("/");
}

function onClickOutside(e) {
  if (menuRef.value && !menuRef.value.contains(e.target)) {
    showMenu.value = false;
  }
}

onMounted(() => document.addEventListener("click", onClickOutside));
onUnmounted(() => document.removeEventListener("click", onClickOutside));
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
  text-decoration: none;
}

.nav-links a:hover {
  color: var(--text-primary);
}

/* ---- Auth actions ---- */

.nav-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}

.nav-login {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
  text-decoration: none;
  transition: color 0.2s;
}

.nav-login:hover {
  color: var(--accent-blue);
}

.nav-register-btn {
  padding: 7px 18px;
  border-radius: var(--radius-full);
  background: var(--accent-blue);
  color: #fff;
  font-size: 13px;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.2s;
}

.nav-register-btn:hover {
  background: var(--accent-blue-hover);
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

.vip-badge {
  padding: 4px 12px;
  border-radius: var(--radius-full);
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: #fff;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 1px;
}

/* ---- User menu ---- */

.user-menu {
  position: relative;
}

.user-avatar-btn {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  border: 2px solid var(--accent-blue);
  background: var(--accent-blue-light);
  color: var(--accent-blue);
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  font-family: inherit;
}

.user-avatar-btn:hover {
  background: var(--accent-blue);
  color: #fff;
}

.user-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  width: 220px;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  box-shadow: var(--shadow-lg);
  overflow: hidden;
  z-index: 200;
}

.dropdown-header {
  padding: 14px 16px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.dropdown-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.dropdown-email {
  font-size: 12px;
  color: var(--text-muted);
}

.dropdown-divider {
  height: 1px;
  background: var(--border-color);
}

.dropdown-item {
  display: block;
  width: 100%;
  padding: 10px 16px;
  font-size: 13px;
  color: var(--text-secondary);
  background: none;
  border: none;
  text-align: left;
  cursor: pointer;
  font-family: inherit;
  transition: background 0.15s;
  text-decoration: none;
}

.dropdown-item:hover {
  background: var(--bg-secondary);
  color: var(--accent-blue);
}

.dropdown-item.logout:hover {
  color: var(--color-error);
}

/* ---- Dropdown transition ---- */

.dropdown-enter-active,
.dropdown-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}

/* ---- Mobile ---- */

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

  .nav-actions {
    display: none;
  }

  .mobile-toggle {
    display: flex;
    margin-left: auto;
  }
}
</style>
