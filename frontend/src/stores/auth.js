import { reactive, computed } from "vue";

const TOKEN_KEY = "sv_access_token";
const REFRESH_KEY = "sv_refresh_token";
const USER_KEY = "sv_user";

const state = reactive({
  token: localStorage.getItem(TOKEN_KEY) || null,
  refreshToken: localStorage.getItem(REFRESH_KEY) || null,
  user: JSON.parse(localStorage.getItem(USER_KEY) || "null"),
});

export const isLoggedIn = computed(() => !!state.token);
export const currentUser = computed(() => state.user);
export const isVip = computed(() => !!state.user?.is_vip);

export function setAuth({ access_token, refresh_token, user }) {
  state.token = access_token;
  state.refreshToken = refresh_token;
  state.user = user;
  localStorage.setItem(TOKEN_KEY, access_token);
  localStorage.setItem(REFRESH_KEY, refresh_token);
  localStorage.setItem(USER_KEY, JSON.stringify(user));
}

export function updateUser(user) {
  state.user = user;
  localStorage.setItem(USER_KEY, JSON.stringify(user));
}

export function clearAuth() {
  state.token = null;
  state.refreshToken = null;
  state.user = null;
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(REFRESH_KEY);
  localStorage.removeItem(USER_KEY);
}

export function getToken() {
  return state.token;
}

export function getRefreshToken() {
  return state.refreshToken;
}
