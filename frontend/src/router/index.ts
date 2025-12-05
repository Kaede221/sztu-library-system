import {
  createWebHistory,
  createRouter,
  type RouteRecordRaw,
} from "vue-router";
import { useUserStore } from "@/store/index.ts";

import HomeView from "@/views/Home/HomeView.vue";
import LoginPage from "@/views/Login/LoginPage.vue";
import LayoutContainer from "@/views/LayoutContainer.vue";
import UserList from "@/views/Users/UserList.vue";
import BookList from "@/views/Books/BookList.vue";
import SettingPage from "@/views/Other/SettingPage.vue";
import ProfilePage from "@/views/Other/ProfilePage.vue";

// 新增页面
import BorrowList from "@/views/Borrow/BorrowList.vue";
import CategoryList from "@/views/Category/CategoryList.vue";

const routes: RouteRecordRaw[] = [
  // 登录页面
  { path: "/login", component: LoginPage },
  {
    path: "/",
    component: LayoutContainer,
    children: [
      { path: "", component: HomeView },
      { path: "user", component: UserList },
      { path: "book", component: BookList },
      // 新增路由
      { path: "borrow", component: BorrowList },
      { path: "category", component: CategoryList },
      // 设置页面路由
      {
        path: "other",
        children: [
          {
            path: "setting",
            component: SettingPage,
          },
          {
            path: "user-profile",
            component: ProfilePage,
          },
        ],
      },
    ],
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// 创建路由守卫
router.beforeEach((to) => {
  // 在路由守卫内部获取用户信息，确保在Pinia安装后使用
  const userStore = useUserStore();

  // 判断当前是否登录了
  if (userStore.token) {
    // 有token的情况下，不允许前往登录页
    if (to.path === "/login") {
      return { path: "/" };
    }
    // 其他页面正常访问
    return true;
  } else {
    // 没有token的情况下，只允许访问登录页
    if (to.path === "/login") {
      return true;
    }
    // 其他页面重定向到登录页
    return { path: "/login" };
  }
});

export { router, routes };
