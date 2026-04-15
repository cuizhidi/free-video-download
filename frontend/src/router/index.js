import { createRouter, createWebHistory } from "vue-router";
import { isLoggedIn } from "../stores/auth.js";

const routes = [
  {
    path: "/",
    name: "home",
    component: () => import("../views/HomeView.vue"),
  },
  {
    path: "/login",
    name: "login",
    component: () => import("../views/LoginView.vue"),
    meta: { guestOnly: true },
  },
  {
    path: "/register",
    name: "register",
    component: () => import("../views/RegisterView.vue"),
    meta: { guestOnly: true },
  },
  {
    path: "/oauth-callback",
    name: "oauth-callback",
    component: () => import("../views/OAuthCallbackView.vue"),
  },
  {
    path: "/account",
    name: "account",
    component: () => import("../views/AccountView.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/checkout",
    name: "checkout",
    component: () => import("../views/CheckoutView.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/checkout/return",
    name: "checkout-return",
    component: () => import("../views/CheckoutReturnView.vue"),
    meta: { requiresAuth: true },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, _from, savedPosition) {
    if (to.hash) return { el: to.hash, behavior: "smooth" };
    if (savedPosition) return savedPosition;
    return { top: 0 };
  },
});

router.beforeEach((to) => {
  if (to.meta.requiresAuth && !isLoggedIn.value) {
    return { name: "login", query: { redirect: to.fullPath } };
  }
  if (to.meta.guestOnly && isLoggedIn.value) {
    return { name: "home" };
  }
});

export default router;
