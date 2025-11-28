import { defineStore } from "pinia";
import { ref, computed } from "vue";

// 默认用户信息
const defaultUser: IUser = {
  id: -1,
  username: "",
  email: "",
  full_name: null,
  role: "user",
  is_active: false,
  created_at: "",
  updated_at: "",
};

export const useUserStore = defineStore(
  "user-store",
  () => {
    // Token
    const token = ref("");

    // 用户信息
    const user = ref<IUser>({ ...defaultUser });

    // 计算属性：是否已登录
    const isLoggedIn = computed(() => !!token.value && user.value.id !== -1);

    // 计算属性：是否是管理员
    const isAdmin = computed(() => user.value.role === "admin");

    // 设置Token
    const setToken = (newToken: string) => {
      token.value = newToken;
    };

    // 设置用户信息
    const setUser = (newUser: IUser) => {
      user.value = newUser;
    };

    // 退出登录
    const logoutUser = () => {
      token.value = "";
      user.value = { ...defaultUser };
    };

    // 更新用户部分信息
    const updateUserInfo = (partialUser: Partial<IUser>) => {
      user.value = { ...user.value, ...partialUser };
    };

    return {
      token,
      user,
      isLoggedIn,
      isAdmin,
      setToken,
      setUser,
      logoutUser,
      updateUserInfo,
    };
  },
  {
    persist: true,
  },
);
