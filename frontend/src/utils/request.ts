import axios from "axios";
import { useUserStore } from "@/store/user.ts";
import { ElMessage } from "element-plus";
import { router } from "@/router/index.js";

// 创建axios示例
const request = axios.create({
  timeout: 5000,
});

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    const userStore = useUserStore();
    if (userStore.token) {
      config.headers.Authorization = userStore.token;
    }
    return config;
  },
  (error) => {
    console.log(error);
    return Promise.reject(error);
  },
);

// 响应拦截器
request.interceptors.response.use(
  async (response) => {
    const res = response.data;
    if (res.success) {
      return res;
    } else {
      // ! 根据状态码 判断一些特殊情况
      if (res.code === 10003) {
        // @ts-ignore
        ElMessage.error("登录已过期, 请重新登录");
        const userStore = useUserStore();
        userStore.logoutUser();
        await router.replace("/login");
      }
      // 其他都是错误
      return Promise.reject({
        message: res.message || "Error",
        status: res.code,
      });
    }
  },
  (err) => {
    return Promise.reject(err);
  },
);

// 配置默认的请求属性
request.defaults.headers.post["Content-Type"] = "application/json";

// 获取请求工具
export const getRequest = () => {
  // TODO 设置项目请求基地址
  request.defaults.baseURL = "";
  return request;
};
