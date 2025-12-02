<template>
    <div class="login-container">
        <div class="login-form">
            <h2>AI 知识助理后台</h2>
            <el-form>
                <el-form-item>
                    <el-input v-model="form.username" placeholder="用户名" prefix-icon="User" @keyup.enter="handleLogin">
                    </el-input>
                </el-form-item>
                <el-form-item><el-input v-model="form.password" type="password" placeholder="密码" prefix-icon="Lock"
                        @keyup.enter="handleLogin">
                    </el-input>
                </el-form-item>
                <el-form-item>
                    <el-button type="primary" style="width: 100%;" @click="handleLogin" :loading="loading"
                        :disabled="!form.username || !form.password">
                        {{ loading ? '登录中...' : '登录' }}
                    </el-button>
                </el-form-item>
            </el-form>
            <div class="debug-info">
                <p style="font-size: 20px;font-weight: bold;margin-bottom: 10px;">调试信息：</p>
                <p>用户名: {{ form.username || 'xxx' }}</p>
                <p>密码长度: {{ form.password.length || 0 }}</p>
                <p>状态: {{ debugInfo || '正常' }}</p>
            </div>
            <p class="tip">提示：用户名: admin 密码: admin123 或 用户名: user 密码: user123</p>
        </div>
    </div>
</template>

<script>
import { userApi } from '@/api/chat'
import { ElMessage } from 'element-plus'
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

export default {
    name: 'LoginPage',
    setup() {
        const form = reactive({
            username: '',
            password: ''
        })
        const loading = ref(false)
        const debugInfo = ref('')
        const router = useRouter()

        const handleLogin = async () => {
            if (!form.username || !form.password) {
                ElMessage.error('请输入用户名和密码')
                return
            }

            loading.value = true
            debugInfo.value = '开始登录...'

            try {
                // console.log('🔑 开始登录请求:', form.username)
                debugInfo.value = '发送登录请求...'

                const response = await userApi.login({
                    username: form.username,
                    password: form.password
                })

                // console.log('✅ 登录响应:', response)
                debugInfo.value = '登录成功，处理响应...'
                // console.log(121, response)
                if (response.success) {
                    localStorage.setItem('auth_token', response.token)
                    localStorage.setItem('user_info', JSON.stringify({
                        id: response.user_id,
                        username: response.username
                    }))

                    debugInfo.value = '跳转到聊天页面...'
                    ElMessage.success('登录成功！')
                    router.push('/chat')
                } else {
                    debugInfo.value = '登录失败: ' + (response.message || '未知错误')
                    ElMessage.error(response.message || '登录失败')
                }
            } catch (error) {
                console.error('❌ 登录错误:', error)
                debugInfo.value = `错误: ${error.response?.status || '未知状态'} - ${error.response?.data?.detail || error.message}`
            } finally {
                loading.value = false
            }
        }

        return {
            form,
            loading,
            debugInfo,
            handleLogin
        }
    }
}
</script>

<style scoped>
.login-container {
    height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-form {
    width: 400px;
    padding: 40px;
    background: white;
    border-radius: 8px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.login-form h2 {
    text-align: center;
    margin-bottom: 30px;
    color: #333;
}

.tip {
    text-align: center;
    color: #999;
    font-size: 12px;
    margin-top: 20px;
}

.debug-info {
    margin-top: 15px;
    padding: 10px;
    background: #f5f5f5;
    border-radius: 4px;
    font-size: 12px;
    color: #666;
}

.debug-info p {
    margin: 2px 0;
}
</style>