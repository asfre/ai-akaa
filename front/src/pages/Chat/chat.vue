<template>
    <div class="chat-container">
        <!-- 顶部导航 -->
        <div class="chat-header">
            <h2>AI 知识助理</h2>
            <div class="header-actions">
                <el-button type="primary" @click="$router.push('/stats')" class="stats-btn">
                    <el-icon style="margin-right: 8px;">
                        <DataAnalysis />
                    </el-icon>
                    数据统计
                </el-button>
                <el-popover placement="bottom" :width="120" trigger="hover">
                    <template #default>
                        <div class="user-menu">
                            <div class="menu-item" @click="editPsw">
                                <el-icon>
                                    <Edit />
                                </el-icon>
                                <span>修改密码</span>
                            </div>
                            <div class="menu-item" @click="handleLogout">
                                <el-icon>
                                    <SwitchButton />
                                </el-icon>
                                <span>退出登录</span>
                            </div>
                        </div>
                    </template>
                    <template #reference>
                        <div class="user-avatar">
                            <img src="../../assets/default_img.jpg" />
                            <el-icon class="arrow-icon">
                                <ArrowDown />
                            </el-icon>
                        </div>
                    </template>
                </el-popover>
            </div>
        </div>

        <!-- 主内容区 -->
        <div class="chat-main">
            <!-- 左侧聊天列表 -->
            <div class="chat-sidebar">
                <div class="sidebar-header">
                    <h3>对话列表</h3>
                    <el-button type="primary" size="small" @click="createNewChat" class="new-chat-btn">
                        <el-icon>
                            <Plus />
                        </el-icon>
                        新对话
                    </el-button>
                </div>
                <div class="chat-list">
                    <div v-for="chat in chatList" :key="chat.id"
                        :class="['chat-item', { active: currentChat?.id === chat.id }]" @click="switchChat(chat.id)">
                        <el-icon>
                            <ChatDotRound />
                        </el-icon>
                        <span class="chat-title">{{ chat.title }}</span>
                        <el-icon name="red" class="delete-btn" @click.stop="deleteChat(chat.id)">
                            <Close />
                        </el-icon>
                    </div>
                </div>
            </div>

            <!-- 右侧聊天区域 -->
            <div class="chat-content">
                <div class="messages-container" ref="messagesContainer">
                    <div v-for="message in currentMessages" :key="message.id" :class="['message', message.type]">
                        <div class="message-avatar">
                            <img v-if="message.type === 'user'" src="../../assets/default_img.jpg" alt="用户" />
                            <div v-else class="ai-avatar">
                                <el-icon>
                                    <Star />
                                </el-icon>
                            </div>
                        </div>
                        <div class="message-content">
                            <div class="message-text">{{ message.content }}</div>
                            <div class="message-time">{{ message.time }}</div>
                        </div>
                    </div>
                </div>

                <!-- 输入区域 -->
                <div class="input-area">
                    <div class="input-tools">
                        <el-tooltip content="语音输入">
                            <el-button circle @click="toggleVoiceInput">
                                <el-icon>
                                    <Microphone />
                                </el-icon>
                            </el-button>
                        </el-tooltip>
                        <el-tooltip content="清除对话">
                            <el-button circle @click="clearMessages">
                                <el-icon>
                                    <Delete />
                                </el-icon>
                            </el-button>
                        </el-tooltip>
                    </div>
                    <div class="input-wrapper">
                        <el-input v-model="inputMessage" type="textarea" :rows="3" placeholder="输入您的问题..."
                            @keypress.enter.prevent="sendMessage"></el-input>
                        <el-button type="primary" @click="sendMessage" :loading="sending" class="send-btn">
                            <el-icon>
                                <Position />
                            </el-icon>
                            发送
                        </el-button>
                    </div>

                    <!-- 语音输入状态 -->
                    <div v-if="isRecording" class="voice-recording">
                        <div class="voice-animation">
                            <div class="voice-bar" v-for="n in 8" :key="n"></div>
                        </div>
                        <p>正在录音... 点击结束</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- 修改密码弹窗 -->
        <el-dialog v-model="dialogVisible" title="修改密码" width="400">
            <div class="password-form">
                <el-form :model="passwordForm" label-width="80px">
                    <el-form-item label="原密码">
                        <el-input type="password" v-model="passwordForm.oldPassword" placeholder="请输入原密码"></el-input>
                    </el-form-item>
                    <el-form-item label="新密码">
                        <el-input type="password" v-model="passwordForm.newPassword" placeholder="请输入新密码"></el-input>
                    </el-form-item>
                    <el-form-item label="确认密码">
                        <el-input type="password" v-model="passwordForm.confirmPassword"
                            placeholder="请再次输入新密码"></el-input>
                    </el-form-item>
                </el-form>
            </div>
            <template #footer>
                <div class="dialog-footer">
                    <el-button @click="dialogVisible = false">取消</el-button>
                    <el-button type="primary" @click="confirmEditPassword">
                        确认修改
                    </el-button>
                </div>
            </template>
        </el-dialog>
    </div>
</template>

<script>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
    DataAnalysis, Edit, SwitchButton, ArrowDown, Plus,
    ChatDotRound, Close, Star, Microphone, Delete, Position
} from '@element-plus/icons-vue'
import { chatApi, userApi } from '@/api/chat'

export default {
    name: 'ChatPage',
    components: {
        DataAnalysis, Edit, SwitchButton, ArrowDown, Plus,
        ChatDotRound, Close, Star, Microphone, Delete, Position
    },
    setup() {
        const router = useRouter()
        const messagesContainer = ref(null)

        // 响应式数据
        const dialogVisible = ref(false)
        const inputMessage = ref('')
        const sending = ref(false)
        const isRecording = ref(false)
        const currentChat = ref(null)

        const passwordForm = reactive({
            oldPassword: '',
            newPassword: '',
            confirmPassword: ''
        })

        // 聊天数据
        const chatList = ref([])
        const currentMessages = ref([])

        // 方法
        const loadChatList = async () => {
            try {
                // console.log('🔄 开始加载聊天列表...')
                const response = await chatApi.getChatList()
                // console.log('📋 聊天列表响应:', response)

                // 处理不同的响应格式
                if (Array.isArray(response)) {
                    chatList.value = response.map(chat => ({
                        id: chat.id,
                        title: chat.title,
                        createTime: chat.createTime || chat.created_at
                    }))
                } else if (response.success && Array.isArray(response.data)) {
                    chatList.value = response.data
                } else {
                    chatList.value = []
                }

                // console.log('✅ 处理后的聊天列表:', chatList.value)

                // 如果有聊天列表且没有当前聊天，自动切换到第一个
                if (chatList.value.length > 0 && !currentChat.value) {
                    await switchChat(chatList.value[0].id)
                }
            } catch (error) {
                console.error('❌ 加载聊天列表失败:', error)
                chatList.value = [] // 确保是数组
            }
        }

        const createNewChat = async () => {
            try {
                // console.log('🆕 创建新对话...')
                const response = await chatApi.createChat()
                // console.log('创建对话响应:', response)

                if (response.success) {
                    const newChat = {
                        id: response.chat_id,
                        title: response.title || '新对话',
                        createTime: new Date().toLocaleDateString()
                    }

                    chatList.value.unshift(newChat)
                    await switchChat(response.chat_id)
                    ElMessage.success('新对话已创建')
                } else {
                    ElMessage.error(response.message || '创建对话失败')
                }
            } catch (error) {
                console.error('❌ 创建对话失败:', error)
                ElMessage.error('创建对话失败: ' + (error.response?.data?.detail || error.message))
            }
        }

        const switchChat = async (chatId) => {
            try {
                // console.log(`🔄 切换到聊天: ${chatId}`)
                const chat = chatList.value.find(chat => chat.id === chatId)
                if (!chat) {
                    console.error('聊天不存在:', chatId)
                    return
                }

                currentChat.value = chat
                // console.log('📨 加载聊天消息...')
                const response = await chatApi.getChatMessages(chatId)
                // console.log('消息响应:', response)

                // 处理消息数据格式
                let messages = []
                if (response.success && Array.isArray(response.messages)) {
                    messages = response.messages
                } else if (Array.isArray(response)) {
                    messages = response
                }

                currentMessages.value = messages.map(msg => ({
                    id: msg.id,
                    type: msg.role === 'user' ? 'user' : 'ai',
                    content: msg.content,
                    time: msg.created_at || new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
                }))

                // console.log('✅ 处理后的消息:', currentMessages.value)

                nextTick(() => {
                    scrollToBottom()
                })
            } catch (error) {
                console.error('❌ 加载消息失败:', error)
                ElMessage.error('加载消息失败: ' + (error.response?.data?.detail || error.message))
                currentMessages.value = [] // 清空消息避免显示错误数据
            }
        }

        const deleteChat = async (chatId) => {
            try {
                await ElMessageBox.confirm('确定要删除这个对话吗？', '提示', {
                    type: 'warning'
                })

                // console.log(`🗑️ 删除聊天: ${chatId}`)
                const response = await chatApi.deleteChat(chatId)
                // console.log('删除响应:', response)

                if (response.success) {
                    const index = chatList.value.findIndex(chat => chat.id === chatId)
                    if (index > -1) {
                        chatList.value.splice(index, 1)
                    }
                    if (currentChat.value?.id === chatId) {
                        currentChat.value = null
                        currentMessages.value = []
                    }
                    ElMessage.success('删除成功')
                } else {
                    ElMessage.error(response.message || '删除失败')
                }
            } catch (error) {
                if (error !== 'cancel') {
                    console.error('❌ 删除聊天失败:', error)
                    ElMessage.error('删除失败: ' + (error.response?.data?.detail || error.message))
                }
            }
        }

        const sendMessage = async () => {
            if (!inputMessage.value.trim()) {
                ElMessage.warning('请输入消息内容')
                return
            }

            // console.log('📤 发送消息:', inputMessage.value)

            // 如果没有当前聊天，先创建一个
            if (!currentChat.value) {
                // console.log('没有当前聊天，先创建新对话')
                await createNewChat()
                if (!currentChat.value) {
                    ElMessage.error('创建对话失败，无法发送消息')
                    return
                }
            }

            const userMessage = {
                id: Date.now(),
                type: 'user',
                content: inputMessage.value,
                time: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
            }

            currentMessages.value.push(userMessage)
            const messageContent = inputMessage.value
            inputMessage.value = ''
            sending.value = true

            scrollToBottom()

            try {
                // console.log(`发送消息到聊天 ${currentChat.value.id}`)
                const response = await chatApi.sendMessage(currentChat.value.id, messageContent)
                // console.log('发送消息响应:', response)

                if (response.success) {
                    const aiMessage = {
                        id: response.message_id || Date.now() + 1,
                        type: 'ai',
                        content: response.answer,
                        time: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
                    }
                    currentMessages.value.push(aiMessage)

                    // 更新聊天标题（如果是新对话）
                    if (currentChat.value.title === '新对话' || currentChat.value.title.includes('新对话')) {
                        const newTitle = messageContent.slice(0, 10) + (messageContent.length > 10 ? '...' : '')
                        currentChat.value.title = newTitle

                        // 更新聊天列表中的标题
                        const chatIndex = chatList.value.findIndex(chat => chat.id === currentChat.value.id)
                        if (chatIndex > -1) {
                            chatList.value[chatIndex].title = newTitle
                        }
                    }

                    // ElMessage.success('消息发送成功')
                } else {
                    ElMessage.error(response.message || '发送消息失败')
                    // 移除用户消息因为发送失败
                    currentMessages.value = currentMessages.value.filter(msg => msg.id !== userMessage.id)
                }
            } catch (error) {
                console.error('❌ 发送消息失败:', error)
                ElMessage.error('发送消息失败: ' + (error.response?.data?.detail || error.message))
                // 移除用户消息因为发送失败
                currentMessages.value = currentMessages.value.filter(msg => msg.id !== userMessage.id)
            } finally {
                sending.value = false
                scrollToBottom()
            }
        }

        const toggleVoiceInput = () => {
            isRecording.value = !isRecording.value
            if (isRecording.value) {
                ElMessage.info('开始录音...')
                // 这里可以集成真实的语音识别API
            } else {
                ElMessage.info('录音结束')
                // 处理语音识别结果
            }
        }

        const clearMessages = async () => {
            try {
                if (currentMessages.value.length === 0) {
                    ElMessage.info('当前没有消息可清除')
                    return
                }

                await ElMessageBox.confirm('确定要清空当前对话吗？', '提示', {
                    type: 'warning'
                })

                if (currentChat.value) {
                    // 调用后端API清空消息
                    try {
                        await chatApi.clearChatMessages(currentChat.value.id)
                    } catch (error) {
                        console.warn('清空后端消息失败:', error)
                    }
                }

                currentMessages.value = []
                ElMessage.success('已清空对话')
            } catch {
                // 用户取消
            }
        }

        const scrollToBottom = () => {
            if (messagesContainer.value) {
                nextTick(() => {
                    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
                })
            }
        }

        const editPsw = () => {
            dialogVisible.value = true
        }

        const confirmEditPassword = async () => {
            // 密码验证逻辑
            if (!passwordForm.oldPassword || !passwordForm.newPassword || !passwordForm.confirmPassword) {
                ElMessage.error('请填写完整信息')
                return
            }
            if (passwordForm.newPassword !== passwordForm.confirmPassword) {
                ElMessage.error('两次输入的密码不一致')
                return
            }

            try {
                const response = await userApi.changePassword(
                    passwordForm.oldPassword,
                    passwordForm.newPassword
                )

                if (response.success) {
                    ElMessage.success('密码修改成功')
                    dialogVisible.value = false
                    // 清空表单
                    Object.assign(passwordForm, {
                        oldPassword: '',
                        newPassword: '',
                        confirmPassword: ''
                    })
                } else {
                    ElMessage.error(response.message || '密码修改失败')
                }
            } catch (error) {
                // ElMessage.error('密码修改失败: ' + (error.response?.data?.detail || error.message))
            }
        }

        const handleLogout = async () => {
            try {
                await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
                    type: 'warning'
                })

                try {
                    await userApi.logout()
                } catch (error) {
                    console.warn('退出登录API调用失败:', error)
                }

                localStorage.removeItem('auth_token')
                localStorage.removeItem('user_info')
                ElMessage.success('已退出登录')
                router.push('/login')
            } catch {
                // 用户取消退出
            }
        }

        // 生命周期
        onMounted(() => {
            // console.log('🚀 ChatPage 组件挂载')
            loadChatList()
        })

        return {
            dialogVisible,
            inputMessage,
            sending,
            isRecording,
            currentChat,
            passwordForm,
            chatList,
            currentMessages,
            messagesContainer,
            createNewChat,
            switchChat,
            deleteChat,
            sendMessage,
            toggleVoiceInput,
            clearMessages,
            editPsw,
            confirmEditPassword,
            handleLogout,
            loadChatList // 暴露出来用于调试
        }
    }
}
</script>

<style scoped>
.chat-container {
    height: 100vh;
    display: flex;
    flex-direction: column;
    background: #f5f7fa;
    overflow-y: hidden;
}

.chat-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 24px;
    height: 64px;
    background: #fff;
    border-bottom: 1px solid #e6e6e6;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease;
}

.header-actions {
    display: flex;
    align-items: center;
    gap: 16px;
}

.stats-btn {
    transition: all 0.3s ease;
}

.stats-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(24, 144, 255, 0.3);
}

.user-avatar {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px;
    border-radius: 24px;
    cursor: pointer;
    transition: all 0.3s ease;
}

.user-avatar:hover {
    background: rgba(24, 144, 255, 0.1);
    transform: scale(1.05);
}

.user-avatar img {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    border: 2px solid #e6e6e6;
    transition: all 0.3s ease;
}

.user-avatar:hover img {
    border-color: #1890ff;
    transform: rotate(10deg);
}

.arrow-icon {
    transition: transform 0.3s ease;
}

.user-avatar:hover .arrow-icon {
    transform: rotate(180deg);
}

.user-menu {
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.menu-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 12px;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.3s ease;
}

.menu-item:hover {
    background: #f0f7ff;
    color: #1890ff;
    transform: translateX(4px);
}

.chat-main {
    flex: 1;
    display: flex;
    overflow: hidden;
}

/* 左侧边栏 */
.chat-sidebar {
    width: 280px;
    background: #fff;
    border-right: 1px solid #e6e6e6;
    display: flex;
    flex-direction: column;
    transition: all 0.3s ease;
}

.sidebar-header {
    padding: 16px;
    border-bottom: 1px solid #e6e6e6;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.new-chat-btn {
    transition: all 0.3s ease;
}

.new-chat-btn:hover {
    transform: scale(1.05);
}

.chat-list {
    flex: 1;
    overflow-y: auto;
    padding: 8px;
}

.chat-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 12px;
    margin-bottom: 4px;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.3s ease;
    position: relative;
}

.chat-item:hover {
    background: #f5f7fa;
    transform: translateX(4px);
}

.chat-item.active {
    background: #e6f7ff;
    border-left: 3px solid #1890ff;
}

.chat-title {
    flex: 1;
    font-size: 14px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.delete-btn {
    opacity: 0.8;
    transition: all 0.3s ease;
}

.chat-item:hover .delete-btn {
    opacity: 1;
}

.delete-btn:hover {
    color: #ff4d4f;
    transform: scale(1.2);
}

/* 右侧聊天区域 */
.chat-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    background: #fff;
}

.messages-container {
    flex: 1;
    padding: 20px;
    overflow-y: auto;
    background: #fafafa;
}

.message {
    display: flex;
    margin-bottom: 20px;
    animation: messageSlide 0.3s ease-out;
}

@keyframes messageSlide {
    from {
        opacity: 0;
        transform: translateY(20px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.message.user {
    flex-direction: row-reverse;
}

.message-avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    overflow: hidden;
    margin: 0 12px;
}

.message.user .message-avatar {
    margin: 0 0 0 12px;
}

.message-avatar img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.ai-avatar {
    width: 100%;
    height: 100%;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
}

.message-content {
    max-width: 70%;
    background: #fff;
    padding: 12px 16px;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease;
}

.message.user .message-content {
    background: #1890ff;
    color: white;
}

.message-content:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.message-text {
    line-height: 1.5;
}

.message-time {
    font-size: 12px;
    color: #999;
    margin-top: 4px;
}

.message.user .message-time {
    color: rgba(255, 255, 255, 0.8);
}

/* 输入区域 */
.input-area {
    padding: 20px;
    border-top: 1px solid #e6e6e6;
    background: #fff;
}

.input-tools {
    display: flex;
    gap: 8px;
    margin-bottom: 12px;
}

.input-wrapper {
    display: flex;
    gap: 12px;
    align-items: flex-end;
}

.input-wrapper :deep(.el-textarea) {
    flex: 1;
}

.send-btn {
    height: 72px;
    transition: all 0.3s ease;
}

.send-btn:hover:not(.is-disabled) {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(24, 144, 255, 0.3);
}

/* 语音输入 */
.voice-recording {
    text-align: center;
    padding: 20px;
    background: #f5f7fa;
    border-radius: 8px;
    margin-top: 12px;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0% {
        background: #f5f7fa;
    }

    50% {
        background: #e6f7ff;
    }

    100% {
        background: #f5f7fa;
    }
}

.voice-animation {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 2px;
    height: 40px;
    margin-bottom: 8px;
}

.voice-bar {
    width: 4px;
    height: 20px;
    background: #1890ff;
    border-radius: 2px;
    animation: voiceWave 1.2s ease-in-out infinite;
}

.voice-bar:nth-child(1) {
    animation-delay: 0s;
}

.voice-bar:nth-child(2) {
    animation-delay: 0.1s;
}

.voice-bar:nth-child(3) {
    animation-delay: 0.2s;
}

.voice-bar:nth-child(4) {
    animation-delay: 0.3s;
}

.voice-bar:nth-child(5) {
    animation-delay: 0.4s;
}

.voice-bar:nth-child(6) {
    animation-delay: 0.5s;
}

.voice-bar:nth-child(7) {
    animation-delay: 0.6s;
}

.voice-bar:nth-child(8) {
    animation-delay: 0.7s;
}

@keyframes voiceWave {

    0%,
    100% {
        transform: scaleY(1);
    }

    50% {
        transform: scaleY(2);
    }
}

/* 响应式设计 */
@media (max-width: 768px) {
    .chat-sidebar {
        width: 100%;
        position: absolute;
        z-index: 1000;
        transform: translateX(-100%);
    }

    .chat-sidebar.open {
        transform: translateX(0);
    }
}
</style>