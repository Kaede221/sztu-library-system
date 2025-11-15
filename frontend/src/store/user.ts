import { defineStore } from "pinia";
import { ref } from "vue";

export const useUserStore = defineStore(
  "user-store",
  () => {
    const refresh_token = ref("");
    const token = ref("");
    const user = ref<IUser>({
      avatar: "",
      gender: "",
      id: -1,
      nickname: "",
      power: -1,
      school: "",
      stuCla: "",
      stuIsCheck: false,
      stuName: "",
      stuNum: "",
      stuPwd: "",
    });

    const setRefreshToken = (new_fresh_token: string) => {
      refresh_token.value = new_fresh_token;
    };

    const setToken = (newToken: string) => {
      token.value = newToken;
    };

    const setUser = (newUser: typeof user.value) => {
      user.value = newUser;
    };

    // 退出登录的方法
    const logoutUser = () => {
      setToken("");
      setRefreshToken("");
      setUser({
        avatar: "",
        gender: "",
        id: -1,
        nickname: "",
        power: -1,
        school: "",
        stuCla: "",
        stuIsCheck: false,
        stuName: "",
        stuNum: "",
        stuPwd: "",
      });
    };
    return {
      refresh_token,
      setRefreshToken,
      token,
      setToken,
      user,
      setUser,
      logoutUser,
    };
  },
  {
    persist: true,
  },
);
