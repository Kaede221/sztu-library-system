import axios from "axios";
import { useUserStore } from "@/store/user";
import { ElMessage } from "element-plus";
import { router } from "@/router/index";

// API基础地址
const BASE_URL = "http://127.0.0.1:8000";

// 创建axios实例
const request = axios.create({
  baseURL: BASE_URL,
  timeout: 10000,
});

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    const userStore = useUserStore();
    if (userStore.token) {
      // 使用Bearer Token认证
      config.headers.Authorization = `Bearer ${userStore.token}`;
    }
    return config;
  },
  (error) => {
    console.error("请求错误:", error);
    return Promise.reject(error);
  },
);

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    // 直接返回响应数据
    return response.data;
  },
  async (error) => {
    const { response } = error;

    if (response) {
      const { status, data } = response;

      // 处理不同的HTTP状态码
      switch (status) {
        case 401:
          // 未授权，清除用户信息并跳转到登录页
          // @ts-ignore
          ElMessage.error(data?.detail || "登录已过期，请重新登录");
          const userStore = useUserStore();
          userStore.logoutUser();
          await router.replace("/login");
          break;
        case 403:
          // @ts-ignore
          ElMessage.error(data?.detail || "权限不足");
          break;
        case 404:
          // @ts-ignore
          ElMessage.error(data?.detail || "请求的资源不存在");
          break;
        case 400:
          // @ts-ignore
          ElMessage.error(data?.detail || "请求参数错误");
          break;
        case 500:
          // @ts-ignore
          ElMessage.error("服务器内部错误");
          break;
        default:
          // @ts-ignore
          ElMessage.error(data?.detail || "请求失败");
      }
    } else {
      // 网络错误或请求被取消
      // @ts-ignore
      ElMessage.error("网络错误，请检查网络连接");
    }

    return Promise.reject(error);
  },
);

// 配置默认的请求属性
request.defaults.headers.post["Content-Type"] = "application/json";

// 获取请求工具
export const getRequest = () => {
  return request;
};

export default request;
