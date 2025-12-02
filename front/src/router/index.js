import { createRouter, createWebHistory } from "vue-router";

// 使用懒加载导入组件
const Chat = () => import("@/pages/Chat/chat.vue");
const Login = () => import("@/pages/Login/index.vue");
const Stats = () => import("@/pages/Stats/index.vue");

const routes = [
  { path: "/", redirect: "/chat" },
  { path: "/login", component: Login, meta: { title: "登录" } },
  { path: "/chat", component: Chat, meta: { title: "聊天室" } },
  { path: "/stats", component: Stats, meta: { title: "数据统计" } },
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL), // 创建一个基于 HTML5 History 模式的路由实例，（xxx）是携带参数
  routes,
});

router.beforeEach((to, from, next) => {
  // 统一使用 auth_token
  const token = localStorage.getItem("auth_token");
  if (to.path !== "/login" && !token) {
    next("/login");
    return;
  }

  // 如果已经有token且访问登录页，重定向到聊天页
  if (to.path === "/login" && token) {
    next("/chat");
    return;
  }

  next();
});

export default router;
