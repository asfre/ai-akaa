# AI 知识助理后台（AI Knowledge Assistant Admin）

## 🚀 项目概述

这是一个基于 Vue2 + Element UI 的轻量后台项目，功能类似"小型 ChatGPT 管理面板"：

- 用户可以输入问题并得到 AI 的回答
- 可以查看提问历史、统计问答次数
- 后台结构规范，后续可无缝扩展成 Vue3/TS 或接企业 API

## 🧱 技术栈基础

| 模块     | 技术                |
| -------- | ------------------- |
| 框架     | Vue2.x              |
| 组件库   | Element UI          |
| 状态管理 | Vuex                |
| 路由     | Vue Router          |
| 网络请求 | Axios               |
| 模拟接口 | Mock.js             |
| AI 接口  | AIapi               |
| 图表展示 | ECharts（后续阶段） |

```text
ai-knowledge-admin/
├── src/
│ ├── api/ # 所有接口封装
│ │ └── chat.js
│ ├── assets/ # 图片/图标等
│ ├── components/ # 通用组件
│ │ ├── ChatBox.vue # 聊天输入框
│ │ └── ChatMessage.vue # 单条消息组件
│ ├── mock/ # Mock 数据
│ │ └── chat.js
│ ├── pages/
│ │ ├── Chat/index.vue # 主聊天页
│ │ └── Stats/index.vue # 统计页（ECharts）
│ ├── router/
│ │ └── index.js
│ ├── store/
│ │ └── index.js
│ ├── utils/
│ │ └── request.js # Axios 封装
│ ├── App.vue
│ └── main.js
├── package.json
└── README.md
|__ vue.config.js # webpack配置文件
```

## 🧩 项目模块说明

### 1️⃣ 登录页（简单版）

- 模拟登录成功后保存 token 到 localStorage
- 登录成功后跳转 `/chat`

### 2️⃣ 聊天页

- 左侧显示历史记录（来自 Vuex 或 Mock）
- 右侧是对话区：用户输入问题，调用 AI 接口返回回答
- 每条消息封装为 ChatMessage 组件

**AI 请求结构：**

```javascript
await axios.post("/api/ask", { question });
```

**AI 响应结构：**

```javascript
{
  "answer": "这是模拟的 AI 回答，可以在这里接入真实接口。"
}
```

### 3️⃣ 统计页

### 用 ECharts 展示：

- 今日提问次数
  历史问题热度（条形图）
  AI 回复字数趋势

## 🧠 学习目标与收获

| 阶段                | 练习目标                           | 能力提升           |
| ------------------- | ---------------------------------- | ------------------ |
| 基础版（Mock 阶段） | 页面布局、Vue 组件通信、状态管理   | 巩固 Vue2 基础     |
| AI 接口阶段         | axios 请求、异步 loading、错误处理 | 学习调用 AI 接口   |
| 数据可视化阶段      | ECharts 图表封装                   | 掌握数据展示与优化 |
| 进阶版（持久化）    | 本地缓存 / IndexedDB 聊天记录      | 向真实产品靠拢     |
| 迁移版（Vue3）      | 思维过渡、Composition API 迁移     | 向现代框架演进     |

## 🧰 依赖清单

```bash
# 初始化项目（若使用 Vue CLI）
vue create ai-knowledge-admin

# 安装依赖
npm install element-ui axios mockjs echarts vuex@3 vue-router@3
在 main.js 中注册：
javascript
import Vue from 'vue'
import App from './App.vue'
import ElementUI from 'element-ui'
import 'element-ui/lib/theme-chalk/index.css'

import router from './router'
import store from './store'

Vue.use(ElementUI)
Vue.config.productionTip = false

new Vue({
  router,
  store,
  render: h => h(App)
}).$mount('#app')
```
