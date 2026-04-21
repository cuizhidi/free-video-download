<template>
  <div class="account-page">
    <div class="account-container">
      <h1 class="account-title">账户设置</h1>

      <!-- Profile card -->
      <div class="card account-card">
        <h2 class="card-title">个人信息</h2>
        <div class="profile-row">
          <div class="avatar-wrapper" @click="triggerAvatarUpload">
            <img
              v-if="currentUser?.avatar_url"
              :src="currentUser.avatar_url"
              class="profile-avatar-img"
              alt="头像"
            />
            <div v-else class="profile-avatar">{{ userInitial }}</div>
            <div class="avatar-overlay">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
                <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/>
                <circle cx="12" cy="13" r="4"/>
              </svg>
            </div>
            <input
              ref="avatarInput"
              type="file"
              accept="image/jpeg,image/png,image/webp,image/gif"
              class="sr-only"
              @change="handleAvatarChange"
            />
          </div>
          <div class="profile-info">
            <div class="profile-name-row">
              <span class="profile-name">{{ currentUser?.name }}</span>
              <span v-if="isVip" class="user-type-badge vip">VIP 会员</span>
              <span v-else class="user-type-badge free">免费用户</span>
            </div>
            <span class="profile-email">{{ currentUser?.email }}</span>
            <div class="profile-meta">
              <span class="meta-item">登录方式：{{ providerLabel }}</span>
              <span v-if="isVip && currentUser?.vip_expire_at" class="meta-item">
                到期时间：{{ vipExpireDate }}
              </span>
              <span class="meta-item">注册时间：{{ registerDate }}</span>
            </div>
          </div>
        </div>
        <p v-if="avatarError" class="form-error">{{ avatarError }}</p>
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
            <p class="no-sub-hint">升级 VIP 解锁 4K 原画、无限下载、字幕导出等全部功能</p>
            <router-link to="/checkout" class="btn-primary upgrade-btn">升级 VIP</router-link>
          </div>
        </template>
      </div>

      <!-- Download history card -->
      <div class="card account-card">
        <h2 class="card-title">下载历史</h2>

        <div v-if="historyLoading" class="sub-loading">加载中...</div>

        <template v-else-if="history.items.length">
          <div class="history-list">
            <div
              v-for="item in history.items"
              :key="item.id"
              class="history-item"
            >
              <div class="history-thumb">
                <img
                  v-if="item.thumbnail"
                  :src="proxyThumb(item.thumbnail)"
                  alt=""
                  @error="(e) => e.target.style.display = 'none'"
                />
                <div v-else class="history-thumb-placeholder">
                  <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
                    <polygon points="10,8 16,12 10,16"/>
                  </svg>
                </div>
              </div>
              <div class="history-info">
                <span class="history-title">{{ item.video_title || '未知视频' }}</span>
                <div class="history-meta">
                  <span v-if="item.platform" class="history-platform">{{ item.platform }}</span>
                  <span v-if="item.quality" class="history-quality">{{ item.quality }}</span>
                  <span v-if="item.filesize" class="history-size">{{ formatFileSize(item.filesize) }}</span>
                  <span class="history-time">{{ formatDate(item.created_at) }}</span>
                </div>
              </div>
            </div>
          </div>

          <div v-if="history.total > history.items.length" class="history-more">
            <button class="btn-outline load-more-btn" @click="loadMoreHistory" :disabled="historyLoadingMore">
              {{ historyLoadingMore ? '加载中...' : '加载更多' }}
            </button>
          </div>
        </template>

        <template v-else>
          <div class="no-sub">
            <p>暂无下载记录</p>
            <router-link to="/" class="btn-outline upgrade-btn">去下载视频</router-link>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from "vue";
import { currentUser, isVip, refreshUser } from "../stores/auth.js";
import { getSubscription, createPortalSession } from "../api/payment.js";
import { uploadAvatar, fetchDownloadHistory } from "../api/auth.js";
import { useToast } from "../composables/useToast.js";

const { showToast } = useToast();

const subscription = ref(null);
const subLoading = ref(true);
const portalLoading = ref(false);
const avatarInput = ref(null);
const avatarError = ref("");

const history = reactive({ items: [], total: 0, page: 1 });
const historyLoading = ref(true);
const historyLoadingMore = ref(false);

const userInitial = computed(() => {
  return (currentUser.value?.name || "U").charAt(0).toUpperCase();
});

const providerLabel = computed(() => {
  const map = { email: "邮箱密码", google: "Google", github: "GitHub" };
  return map[currentUser.value?.auth_provider] || "邮箱密码";
});

const vipExpireDate = computed(() => {
  const d = currentUser.value?.vip_expire_at;
  if (!d) return "-";
  return new Date(d).toLocaleDateString("zh-CN", { year: "numeric", month: "long", day: "numeric" });
});

const registerDate = computed(() => {
  const d = currentUser.value?.created_at;
  if (!d) return "-";
  return new Date(d).toLocaleDateString("zh-CN", { year: "numeric", month: "long", day: "numeric" });
});

const planLabel = computed(() => {
  const map = { monthly: "月度会员", yearly: "年度会员" };
  return map[subscription.value?.plan_type] || "会员";
});

const statusLabel = computed(() => {
  const map = { active: "正常", trialing: "试用中", past_due: "待支付", canceled: "已取消" };
  return map[subscription.value?.status] || subscription.value?.status;
});

const periodEnd = computed(() => {
  if (!subscription.value?.current_period_end) return "-";
  return new Date(subscription.value.current_period_end).toLocaleDateString("zh-CN", {
    year: "numeric", month: "long", day: "numeric",
  });
});

onMounted(async () => {
  refreshUser();

  try {
    subscription.value = await getSubscription();
  } catch {
    subscription.value = { has_subscription: false };
  } finally {
    subLoading.value = false;
  }

  try {
    const res = await fetchDownloadHistory(1);
    history.items = res.items;
    history.total = res.total;
    history.page = 1;
  } catch {
    // ignore
  } finally {
    historyLoading.value = false;
  }
});

function triggerAvatarUpload() {
  avatarInput.value?.click();
}

async function handleAvatarChange(e) {
  const file = e.target.files?.[0];
  if (!file) return;
  avatarError.value = "";
  try {
    const user = await uploadAvatar(file);
    const { updateUser } = await import("../stores/auth.js");
    updateUser(user);
    showToast("头像更新成功", "success");
  } catch (err) {
    avatarError.value = err.message;
  }
  e.target.value = "";
}

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

async function loadMoreHistory() {
  historyLoadingMore.value = true;
  try {
    const nextPage = history.page + 1;
    const res = await fetchDownloadHistory(nextPage);
    history.items.push(...res.items);
    history.total = res.total;
    history.page = nextPage;
  } catch {
    showToast("加载失败", "error");
  } finally {
    historyLoadingMore.value = false;
  }
}

function proxyThumb(url) {
  if (!url) return "";
  return `/api/proxy-image?url=${encodeURIComponent(url)}`;
}

function formatFileSize(bytes) {
  if (!bytes) return "";
  if (bytes < 1024) return bytes + " B";
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
  if (bytes < 1024 * 1024 * 1024) return (bytes / (1024 * 1024)).toFixed(1) + " MB";
  return (bytes / (1024 * 1024 * 1024)).toFixed(2) + " GB";
}

function formatDate(iso) {
  if (!iso) return "";
  const d = new Date(iso);
  const now = new Date();
  const diff = now - d;
  if (diff < 60000) return "刚刚";
  if (diff < 3600000) return Math.floor(diff / 60000) + " 分钟前";
  if (diff < 86400000) return Math.floor(diff / 3600000) + " 小时前";
  if (diff < 604800000) return Math.floor(diff / 86400000) + " 天前";
  return d.toLocaleDateString("zh-CN", { month: "short", day: "numeric" });
}
</script>

<style scoped>
.account-page {
  min-height: calc(100vh - var(--nav-height) - 120px);
  background: var(--bg-secondary);
  padding: 40px 20px;
}

.account-container {
  max-width: 640px;
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

/* ---- Profile ---- */

.profile-row {
  display: flex;
  align-items: flex-start;
  gap: 18px;
}

.avatar-wrapper {
  position: relative;
  width: 64px;
  height: 64px;
  flex-shrink: 0;
  border-radius: 50%;
  cursor: pointer;
  overflow: hidden;
}

.profile-avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 50%;
}

.profile-avatar {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: var(--accent-blue-light);
  color: var(--accent-blue);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: 700;
}

.avatar-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  opacity: 0;
  transition: opacity 0.2s;
  border-radius: 50%;
}

.avatar-wrapper:hover .avatar-overlay {
  opacity: 1;
}

.profile-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.profile-name-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.profile-name {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
}

.user-type-badge {
  font-size: 11px;
  font-weight: 700;
  padding: 3px 10px;
  border-radius: var(--radius-full);
  white-space: nowrap;
}

.user-type-badge.vip {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: #fff;
}

.user-type-badge.free {
  background: var(--bg-secondary);
  color: var(--text-muted);
  border: 1px solid var(--border-color);
}

.profile-email {
  font-size: 13px;
  color: var(--text-muted);
}

.profile-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 6px 16px;
  margin-top: 4px;
}

.meta-item {
  font-size: 12px;
  color: var(--text-muted);
}

.form-error {
  color: var(--color-error);
  font-size: 12px;
  margin-top: 10px;
}

/* ---- Subscription ---- */

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

.status-active { color: var(--color-success); }
.status-past_due { color: var(--color-warning); }
.status-canceled { color: var(--color-error); }

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
  margin-bottom: 6px;
}

.no-sub-hint {
  font-size: 12px;
  margin-bottom: 16px;
}

.upgrade-btn {
  display: inline-block;
  padding: 10px 32px;
  font-size: 14px;
  border-radius: var(--radius-md);
  text-decoration: none;
}

/* ---- Download History ---- */

.history-list {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.history-item {
  display: flex;
  gap: 14px;
  padding: 12px;
  border-radius: var(--radius-sm);
  transition: background 0.15s;
}

.history-item:hover {
  background: var(--bg-secondary);
}

.history-thumb {
  width: 80px;
  height: 50px;
  flex-shrink: 0;
  border-radius: 6px;
  overflow: hidden;
  background: var(--bg-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
}

.history-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.history-thumb-placeholder {
  color: var(--text-muted);
  opacity: 0.4;
}

.history-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
  flex: 1;
}

.history-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.history-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 4px 10px;
  font-size: 11px;
  color: var(--text-muted);
}

.history-platform {
  padding: 1px 6px;
  background: var(--accent-blue-light);
  color: var(--accent-blue);
  border-radius: var(--radius-full);
  font-weight: 600;
}

.history-quality {
  font-weight: 600;
}

.history-more {
  margin-top: 16px;
  text-align: center;
}

.load-more-btn {
  padding: 8px 24px;
  font-size: 13px;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  font-family: inherit;
  transition: all 0.2s;
}

.load-more-btn:hover {
  background: var(--bg-secondary);
}

.load-more-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

@media (max-width: 768px) {
  .profile-row {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }

  .profile-name-row {
    justify-content: center;
  }

  .profile-meta {
    justify-content: center;
  }

  .history-thumb {
    width: 60px;
    height: 38px;
  }
}
</style>
