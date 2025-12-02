// src/utils/request.js
import axios from "axios";
import { ElMessage } from "element-plus";
import router from "@/router";

// 创建 axios 实例
// const request = axios.create({
//   baseURL: "http://localhost:8000/api", // 后端 API 地址
//   timeout: 30000, // 增加超时时间
//   headers: {
//     "Content-Type": "application/json",
//   },
// });
const request = axios.create({
  baseURL: "http://localhost:8000/api", // 确保这个端口和你的后端一致
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
  },
});

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    // console.log("🚀 发送请求:", config.method?.toUpperCase(), config.url);

    // 添加 token 到请求头
    const token = localStorage.getItem("auth_token");
    if (token) {
      config.headers.Authorization = token; // 直接使用token，不加Bearer
    }
    return config;
  },
  (error) => {
    console.error("❌ 请求拦截器错误:", error);
    return Promise.reject(error);
  }
);

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    // console.log("✅ 请求成功:", response.config.url, response.data);
    return response.data; // 直接返回数据
  },
  (error) => {
    console.error("❌ 请求失败:", error.response?.status, error.response?.data);

    const { response } = error;

    if (response) {
      switch (response.status) {
        case 401:
          ElMessage.error("用户名或密码错误");
          // localStorage.removeItem("auth_token");
          // localStorage.removeItem("user_info");
          break;
        case 500:
          ElMessage.error("服务器内部错误，请检查后端服务");
          break;
        default:
          ElMessage.error(response.data?.detail || "请求失败");
      }
    } else {
      ElMessage.error("网络连接失败，请检查后端服务是否启动");
    }

    return Promise.reject(error);
  }
);

// 通用请求方法
export const http = {
  get(url, params = {}) {
    return request.get(url, { params });
  },

  post(url, data = {}) {
    return request.post(url, data);
  },

  put(url, data = {}) {
    return request.put(url, data);
  },

  delete(url) {
    return request.delete(url);
  },
};

export default request;
