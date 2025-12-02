import { http } from "@/utils/request";

/// 聊天相关 API
export const chatApi = {
  // 获取聊天列表
  async getChatList() {
    const response = await http.get("/chat/chats");
    return response || [];
  },

  // 创建新聊天
  async createChat(title = "新对话") {
    const response = await http.post("/chat/chats", { title });
    return response;
  },

  // 删除聊天
  async deleteChat(chatId) {
    const response = await http.delete(`/chat/chats/${chatId}`);
    return response;
  },

  // 发送消息
  async sendMessage(chatId, question) {
    const response = await http.post("/chat/message", {
      chat_id: chatId,
      question,
      timestamp: Date.now(),
    });
    return response;
  },

  // 获取聊天消息
  async getChatMessages(chatId) {
    const response = await http.get(`/chat/chats/${chatId}/messages`);
    return response.messages || [];
  },

  // 清空聊天记录
  async clearChatMessages(chatId) {
    const response = await http.delete(`/chat/chats/${chatId}/messages`);
    return response;
  },
};

// 用户相关 API
export const userApi = {
  // 登录
  async login(formData) {
    const response = await http.post("/auth/login", formData);
    return response;
  },

  // 修改密码
  async changePassword(oldPassword, newPassword) {
    const response = await http.put("/auth/password", {
      oldPassword,
      newPassword,
    });
    return response;
  },

  // 退出登录
  async logout() {
    const response = await http.post("/auth/logout");
    return response;
  },
};

// 统计相关 API
export const statsApi = {
  // 获取数据概览
  async getOverview() {
    try {
      const response = await http.get("/stats/overview");
      return response.data || [];
    } catch (error) {
      console.error("获取数据概览失败:", error);
      return [];
    }
  },

  // 获取调用趋势
  async getUsageTrend(timeRange = "today") {
    try {
      const response = await http.get("/stats/usage-trend", {
        params: { range: timeRange },
      });
      return response.data || { hours: [], values: [] };
    } catch (error) {
      console.error("获取调用趋势失败:", error);
      return { hours: [], values: [] };
    }
  },

  // 获取用户分布
  async getUserDistribution() {
    try {
      const response = await http.get("/stats/user-distribution");
      return response.data || [];
    } catch (error) {
      console.error("获取用户分布失败:", error);
      return [];
    }
  },

  // 获取热门问题
  async getHotQuestions() {
    try {
      const response = await http.get("/stats/hot-questions");
      return response.data || [];
    } catch (error) {
      console.error("获取热门问题失败:", error);
      return [];
    }
  },

  // 获取实时数据
  async getRealtimeData() {
    try {
      const response = await http.get("/stats/realtime");
      return response.data || [];
    } catch (error) {
      console.error("获取实时数据失败:", error);
      return [];
    }
  },
};
