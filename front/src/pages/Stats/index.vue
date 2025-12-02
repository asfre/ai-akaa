<template>
    <div class="stats-container">
        <!-- 顶部导航 -->
        <div class="stats-header">
            <div class="header-left">
                <h2>数据统计</h2>
                <el-tag type="success">实时更新</el-tag>
            </div>
            <div class="header-actions">
                <el-button-group>
                    <el-button :type="timeRange === 'today' ? 'primary' : ''" @click="changeTimeRange('today')">
                        今日
                    </el-button>
                    <el-button :type="timeRange === 'week' ? 'primary' : ''" @click="changeTimeRange('week')">
                        本周
                    </el-button>
                    <el-button :type="timeRange === 'month' ? 'primary' : ''" @click="changeTimeRange('month')">
                        本月
                    </el-button>
                </el-button-group>
                <el-button @click="$router.push('/chat')" type="primary" class="back-btn">
                    <el-icon>
                        <ArrowLeft />
                    </el-icon>
                    返回聊天
                </el-button>
            </div>
        </div>

        <!-- 数据概览卡片 -->
        <div class="stats-overview">
            <el-row :gutter="20">
                <el-col :xs="12" :sm="6" v-for="stat in overviewStats" :key="stat.title">
                    <div class="stat-card" :style="{ borderLeftColor: stat.color }" @mouseenter="handleCardHover(stat)"
                        @mouseleave="handleCardLeave">
                        <div class="stat-icon" :style="{ backgroundColor: stat.color + '20' }">
                            <el-icon>
                                <component :is="stat.icon" />
                            </el-icon>
                        </div>
                        <div class="stat-content">
                            <div class="stat-value">{{ stat.value }}</div>
                            <div class="stat-title">{{ stat.title }}</div>
                            <div class="stat-trend" :class="stat.trend.type">
                                <el-icon>
                                    <SortUp v-if="stat.trend.type === 'up'" />
                                    <SortDown v-else />
                                </el-icon>
                                {{ stat.trend.value }}
                            </div>
                        </div>
                        <div class="stat-sparkline">
                            <div class="sparkline-bar" v-for="(point, index) in stat.sparkline" :key="index"
                                :style="{ height: point + '%' }"></div>
                        </div>
                    </div>
                </el-col>
            </el-row>
        </div>

        <!-- 图表区域 -->
        <div class="charts-section">
            <el-row :gutter="20">
                <!-- 调用次数趋势 -->
                <el-col :xs="24" :lg="12">
                    <div class="chart-card">
                        <div class="chart-header">
                            <h3>调用次数趋势</h3>
                            <el-tag size="small">实时</el-tag>
                        </div>
                        <div class="chart-container">
                            <div ref="usageChart" class="chart" style="height: 300px;"></div>
                        </div>
                    </div>
                </el-col>

                <!-- 用户分布 -->
                <el-col :xs="24" :lg="12">
                    <div class="chart-card">
                        <div class="chart-header">
                            <h3>用户分布</h3>
                            <el-tag size="small" type="success">今日</el-tag>
                        </div>
                        <div class="chart-container">
                            <div ref="userChart" class="chart" style="height: 300px;"></div>
                        </div>
                    </div>
                </el-col>

                <!-- 热门问题 -->
                <el-col :xs="24" :lg="12">
                    <div class="chart-card">
                        <div class="chart-header">
                            <h3>热门问题TOP10</h3>
                            <el-tag size="small" type="warning">热度</el-tag>
                        </div>
                        <div class="chart-container">
                            <div ref="hotQuestionsChart" class="chart" style="height: 350px;"></div>
                        </div>
                    </div>
                </el-col>

                <!-- 响应时间分布 -->
                <el-col :xs="24" :lg="12">
                    <div class="chart-card">
                        <div class="chart-header">
                            <h3>响应时间分布</h3>
                            <el-tag size="small" type="info">毫秒</el-tag>
                        </div>
                        <div class="chart-container">
                            <div ref="responseTimeChart" class="chart" style="height: 360px;"></div>
                        </div>
                    </div>
                </el-col>
            </el-row>
        </div>

        <!-- 实时数据流 -->
        <div class="realtime-section">
            <div class="section-header">
                <h3>实时数据流</h3>
                <div class="realtime-controls">
                    <el-switch v-model="realtimeEnabled" active-text="实时更新" inactive-text="暂停" />
                    <el-button size="small" @click="refreshData">
                        <el-icon>
                            <Refresh />
                        </el-icon>
                        刷新
                    </el-button>
                </div>
            </div>
            <div class="realtime-data">
                <div v-for="item in realtimeData" :key="item.id" class="realtime-item" :class="item.type">
                    <div class="item-avatar">
                        <el-avatar :size="32" :src="item.avatar" />
                    </div>
                    <div class="item-content">
                        <div class="item-message">{{ item.message }}</div>
                        <div class="item-time">{{ item.time }}</div>
                    </div>
                    <div class="item-badge" :class="item.type">
                        {{ item.type === 'user' ? '提问' : '回复' }}
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { ref, reactive, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'
import {
    ArrowLeft,
    Refresh,
    User,
    UserFilled,
    View,
    ChatDotRound,
    SortUp,
    SortDown,
    Clock,
    Star
} from '@element-plus/icons-vue'
import { statsApi } from '@/api/chat'

export default {
    name: 'StatsPage',
    components: {
        ArrowLeft,
        Refresh,
        User,
        UserFilled,
        View,
        ChatDotRound,
        SortUp,
        SortDown,
        Clock,
        Star
    },
    setup() {
        const router = useRouter()

        // 图表引用
        const usageChart = ref(null)
        const userChart = ref(null)
        const hotQuestionsChart = ref(null)
        const responseTimeChart = ref(null)

        // 响应式数据
        const timeRange = ref('today')
        const realtimeEnabled = ref(true)
        const overviewStats = ref([])
        const realtimeData = ref([])
        const usageTrendData = ref({ hours: [], values: [] })
        const userDistributionData = ref([])
        const hotQuestionsData = ref([])

        // 图表实例
        let usageChartInstance = null
        let userChartInstance = null
        let hotQuestionsChartInstance = null
        let responseTimeChartInstance = null

        // 定时器
        let dataUpdateTimer = null

        // 方法
        const changeTimeRange = async (range) => {
            timeRange.value = range
            await loadUsageTrend(range)
            refreshCharts()
        }

        const handleCardHover = (stat) => {
            // console.log('Hovering:', stat.title)
        }

        const handleCardLeave = () => {
            // 卡片离开效果
        }

        const refreshData = async () => {
            await loadOverviewData()
            await loadUsageTrend(timeRange.value)
            await loadUserDistribution()
            await loadHotQuestions()
            await loadRealtimeData()
            refreshCharts()

            ElMessage.success('数据已刷新')
        }

        const addRealtimeData = async () => {
            if (!realtimeEnabled.value) return
            await loadRealtimeData()
        }

        // 数据加载方法
        const loadOverviewData = async () => {
            try {
                const data = await statsApi.getOverview()
                if (data && data.length > 0) {
                    // 为数据添加图标和颜色
                    const icons = ['ChatDotRound', 'UserFilled', 'User', 'View']
                    const colors = ['#1890ff', '#52c41a', '#faad14', '#722ed1']

                    overviewStats.value = data.map((stat, index) => ({
                        ...stat,
                        icon: icons[index] || 'ChatDotRound',
                        color: colors[index] || '#1890ff'
                    }))
                } else {
                    // 如果API返回空数据，使用默认数据
                    overviewStats.value = getDefaultOverviewStats()
                }
            } catch (error) {
                console.error('加载概览数据失败:', error)
                ElMessage.error('加载数据失败')
                // 使用默认数据
                overviewStats.value = getDefaultOverviewStats()
            }
        }

        const getDefaultOverviewStats = () => {
            return [
                {
                    title: '总调用次数',
                    value: '12,458',
                    icon: 'ChatDotRound',
                    color: '#1890ff',
                    trend: { type: 'up', value: '+12.5%' },
                    sparkline: [45, 52, 38, 60, 48, 55, 42]
                },
                {
                    title: '活跃用户',
                    value: '2,847',
                    icon: 'UserFilled',
                    color: '#52c41a',
                    trend: { type: 'up', value: '+8.3%' },
                    sparkline: [30, 25, 35, 45, 40, 38, 42]
                },
                {
                    title: '在线人数',
                    value: '156',
                    icon: 'User',
                    color: '#faad14',
                    trend: { type: 'down', value: '-2.1%' },
                    sparkline: [60, 55, 58, 52, 54, 50, 48]
                },
                {
                    title: '游客人数',
                    value: '89',
                    icon: 'View',
                    color: '#722ed1',
                    trend: { type: 'up', value: '+15.7%' },
                    sparkline: [20, 25, 18, 30, 25, 28, 32]
                }
            ]
        }

        const loadUsageTrend = async (range = 'today') => {
            try {
                const data = await statsApi.getUsageTrend(range)
                usageTrendData.value = data
            } catch (error) {
                console.error('加载使用趋势失败:', error)
                // 使用默认数据
                usageTrendData.value = {
                    hours: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00', '23:59'],
                    values: [120, 200, 150, 80, 70, 110, 130]
                }
            }
        }

        const loadUserDistribution = async () => {
            try {
                const data = await statsApi.getUserDistribution()
                userDistributionData.value = data
            } catch (error) {
                console.error('加载用户分布失败:', error)
                // 使用默认数据
                userDistributionData.value = [
                    { name: "注册用户", value: 1847 },
                    { name: "VIP用户", value: 310 },
                    { name: "游客", value: 534 },
                    { name: "新用户", value: 156 }
                ]
            }
        }

        const loadHotQuestions = async () => {
            try {
                const data = await statsApi.getHotQuestions()
                hotQuestionsData.value = data
            } catch (error) {
                console.error('加载热门问题失败:', error)
                // 使用默认数据
                hotQuestionsData.value = [
                    { question: "Vue3学习指南", count: 123 },
                    { question: "Python入门教程", count: 98 },
                    { question: "机器学习基础", count: 87 },
                    { question: "React使用技巧", count: 76 },
                    { question: "CSS布局方法", count: 65 },
                    { question: "Node.js开发", count: 54 },
                    { question: "数据库优化", count: 43 },
                    { question: "算法学习路径", count: 32 },
                    { question: "项目部署指南", count: 21 },
                    { question: "性能优化技巧", count: 10 }
                ]
            }
        }

        const loadRealtimeData = async () => {
            try {
                const data = await statsApi.getRealtimeData()
                realtimeData.value = data
            } catch (error) {
                console.error('加载实时数据失败:', error)
                // 使用默认数据
                realtimeData.value = [
                    {
                        id: 1,
                        type: 'user',
                        avatar: '/src/assets/default_img.jpg',
                        message: '如何学习Vue3？',
                        time: '刚刚'
                    },
                    {
                        id: 2,
                        type: 'ai',
                        avatar: '',
                        message: '已回复关于Vue3的问题',
                        time: '2分钟前'
                    },
                    {
                        id: 3,
                        type: 'user',
                        avatar: '/src/assets/default_img.jpg',
                        message: '人工智能的发展趋势？',
                        time: '3分钟前'
                    },
                    {
                        id: 4,
                        type: 'ai',
                        avatar: '',
                        message: '已回复AI发展趋势问题',
                        time: '4分钟前'
                    }
                ]
            }
        }

        // 图表初始化方法
        const initUsageChart = () => {
            if (!usageChart.value) return

            usageChartInstance = echarts.init(usageChart.value)
            const option = {
                animation: true,
                animationDuration: 1000,
                tooltip: {
                    trigger: 'axis',
                    axisPointer: {
                        type: 'shadow'
                    }
                },
                grid: {
                    left: '3%',
                    right: '4%',
                    bottom: '3%',
                    containLabel: true
                },
                xAxis: {
                    type: 'category',
                    data: usageTrendData.value.hours,
                    axisLine: {
                        lineStyle: {
                            color: '#e8e8e8'
                        }
                    }
                },
                yAxis: {
                    type: 'value',
                    axisLine: {
                        show: false
                    },
                    axisTick: {
                        show: false
                    },
                    splitLine: {
                        lineStyle: {
                            color: '#f0f0f0'
                        }
                    }
                },
                series: [{
                    data: usageTrendData.value.values,
                    type: 'bar',
                    barWidth: '60%',
                    itemStyle: {
                        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                            { offset: 0, color: '#1890ff' },
                            { offset: 1, color: '#1890ff88' }
                        ]),
                        borderRadius: [4, 4, 0, 0]
                    },
                    emphasis: {
                        itemStyle: {
                            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                                { offset: 0, color: '#096dd9' },
                                { offset: 1, color: '#096dd988' }
                            ])
                        }
                    }
                }]
            }

            usageChartInstance.setOption(option)
        }

        const initUserChart = () => {
            if (!userChart.value) return

            userChartInstance = echarts.init(userChart.value)
            const option = {
                tooltip: {
                    trigger: 'item',
                    formatter: '{a} <br/>{b}: {c} ({d}%)'
                },
                legend: {
                    orient: 'vertical',
                    right: 10,
                    top: 'center',
                    margin: [100, 0, 0, 20],
                    data: userDistributionData.value.map(item => item.name)
                },
                series: [{
                    name: '用户分布',
                    type: 'pie',
                    radius: ['40%', '70%'],
                    avoidLabelOverlap: false,
                    itemStyle: {
                        borderRadius: 10,
                        borderColor: '#fff',
                        borderWidth: 2
                    },
                    label: {
                        show: false,
                        position: 'center'
                    },
                    emphasis: {
                        label: {
                            show: true,
                            fontSize: '18',
                            fontWeight: 'bold'
                        }
                    },
                    labelLine: {
                        show: false
                    },
                    data: userDistributionData.value.map((item, index) => ({
                        value: item.value,
                        name: item.name,
                        itemStyle: {
                            color: ['#1890ff', '#52c41a', '#faad14', '#722ed1'][index] || '#1890ff'
                        }
                    }))
                }]
            }

            userChartInstance.setOption(option)
        }

        const initHotQuestionsChart = () => {
            if (!hotQuestionsChart.value) return

            hotQuestionsChartInstance = echarts.init(hotQuestionsChart.value)
            const option = {
                tooltip: {
                    trigger: 'axis',
                    axisPointer: {
                        type: 'shadow'
                    }
                },
                grid: {
                    left: '3%',
                    right: '4%',
                    bottom: '3%',
                    containLabel: true
                },
                xAxis: {
                    type: 'value',
                    axisLine: {
                        show: false
                    },
                    axisTick: {
                        show: false
                    }
                },
                yAxis: {
                    type: 'category',
                    data: hotQuestionsData.value.map(item => item.question),
                    axisLine: {
                        lineStyle: {
                            color: '#e8e8e8'
                        }
                    }
                },
                series: [{
                    name: '提问次数',
                    type: 'bar',
                    data: hotQuestionsData.value.map(item => item.count),
                    itemStyle: {
                        color: new echarts.graphic.LinearGradient(1, 0, 0, 0, [
                            { offset: 0, color: '#faad14' },
                            { offset: 1, color: '#faad1488' }
                        ]),
                        borderRadius: [0, 4, 4, 0]
                    }
                }]
            }

            hotQuestionsChartInstance.setOption(option)
        }

        const initResponseTimeChart = () => {
            if (!responseTimeChart.value) return

            responseTimeChartInstance = echarts.init(responseTimeChart.value)
            const option = {
                tooltip: {
                    trigger: 'axis',
                    axisPointer: {
                        type: 'cross',
                        label: {
                            backgroundColor: '#6a7985'
                        }
                    }
                },
                legend: {
                    data: ['平均响应时间', '最大响应时间'],
                },
                grid: {
                    left: '3%',
                    right: '4%',
                    // bottom: '3%',
                    containLabel: true
                },
                xAxis: {
                    type: 'category',
                    boundaryGap: false,
                    data: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00']
                },
                yAxis: {
                    type: 'value',
                    name: '毫秒'
                },
                series: [
                    {
                        name: '平均响应时间',
                        type: 'line',
                        stack: 'Total',
                        smooth: true,
                        lineStyle: {
                            width: 3
                        },
                        showSymbol: false,
                        areaStyle: {
                            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                                { offset: 0, color: '#1890ff' },
                                { offset: 1, color: '#1890ff00' }
                            ])
                        },
                        emphasis: {
                            focus: 'series'
                        },
                        data: [120, 132, 101, 134, 90, 230]
                    },
                    {
                        name: '最大响应时间',
                        type: 'line',
                        stack: 'Total',
                        smooth: true,
                        lineStyle: {
                            width: 3
                        },
                        showSymbol: false,
                        areaStyle: {
                            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                                { offset: 0, color: '#52c41a' },
                                { offset: 1, color: '#52c41a00' }
                            ])
                        },
                        emphasis: {
                            focus: 'series'
                        },
                        data: [220, 182, 191, 234, 290, 330]
                    }
                ]
            }

            responseTimeChartInstance.setOption(option)
        }

        const initCharts = () => {
            // 初始化所有图表
            nextTick(() => {
                initUsageChart()
                initUserChart()
                initHotQuestionsChart()
                initResponseTimeChart()
            })
        }

        const refreshCharts = () => {
            // 刷新所有图表数据
            if (usageChartInstance) {
                const newData = usageTrendData.value.values
                usageChartInstance.setOption({
                    series: [{
                        data: newData
                    }]
                })
            }

            if (userChartInstance) {
                userChartInstance.setOption({
                    series: [{
                        data: userDistributionData.value.map((item, index) => ({
                            value: item.value,
                            name: item.name,
                            itemStyle: {
                                color: ['#1890ff', '#52c41a', '#faad14', '#722ed1'][index] || '#1890ff'
                            }
                        }))
                    }]
                })
            }

            if (hotQuestionsChartInstance) {
                hotQuestionsChartInstance.setOption({
                    yAxis: {
                        data: hotQuestionsData.value.map(item => item.question)
                    },
                    series: [{
                        data: hotQuestionsData.value.map(item => item.count)
                    }]
                })
            }
        }

        const startRealtimeUpdates = () => {
            dataUpdateTimer = setInterval(() => {
                if (realtimeEnabled.value) {
                    addRealtimeData()
                    refreshCharts()
                }
            }, 10000) // 每10秒更新一次
        }

        const stopRealtimeUpdates = () => {
            if (dataUpdateTimer) {
                clearInterval(dataUpdateTimer)
                dataUpdateTimer = null
            }
        }

        // 生命周期
        onMounted(async () => {
            await loadOverviewData()
            await loadUsageTrend('today')
            await loadUserDistribution()
            await loadHotQuestions()
            await loadRealtimeData()

            initCharts()
            startRealtimeUpdates()

            // 监听窗口大小变化，重新调整图表大小
            window.addEventListener('resize', () => {
                usageChartInstance?.resize()
                userChartInstance?.resize()
                hotQuestionsChartInstance?.resize()
                responseTimeChartInstance?.resize()
            })
        })

        onUnmounted(() => {
            stopRealtimeUpdates()

            // 销毁图表实例
            usageChartInstance?.dispose()
            userChartInstance?.dispose()
            hotQuestionsChartInstance?.dispose()
            responseTimeChartInstance?.dispose()

            // 移除事件监听
            window.removeEventListener('resize', () => { })
        })

        return {
            timeRange,
            realtimeEnabled,
            overviewStats,
            realtimeData,
            usageChart,
            userChart,
            hotQuestionsChart,
            responseTimeChart,
            changeTimeRange,
            handleCardHover,
            handleCardLeave,
            refreshData
        }
    }
}
</script>

<style scoped>
.stats-container {
    min-height: 100vh;
    background: #f5f7fa;
    padding: 20px;
}

.stats-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
    background: #fff;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease;
}

.stats-header:hover {
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
    transform: translateY(-2px);
}

.header-left {
    display: flex;
    align-items: center;
    gap: 12px;
}

.header-left h2 {
    margin: 0;
    color: #1f2d3d;
    font-size: 24px;
}

.header-actions {
    display: flex;
    align-items: center;
    gap: 16px;
}

.back-btn {
    transition: all 0.3s ease;
}

.back-btn:hover {
    transform: translateX(-4px);
}

/* 数据概览卡片 */
.stats-overview {
    margin-bottom: 24px;
}

.stat-card {
    background: #fff;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    border-left: 4px solid;
    display: flex;
    align-items: center;
    gap: 16px;
    transition: all 0.3s ease;
    cursor: pointer;
    position: relative;
    overflow: hidden;
}

.stat-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.stat-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
    transition: left 0.5s;
}

.stat-card:hover::before {
    left: 100%;
}

.stat-icon {
    width: 60px;
    height: 60px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    transition: all 0.3s ease;
}

.stat-card:hover .stat-icon {
    transform: scale(1.1) rotate(5deg);
}

.stat-content {
    flex: 1;
}

.stat-value {
    font-size: 28px;
    font-weight: bold;
    color: #1f2d3d;
    margin-bottom: 4px;
}

.stat-title {
    font-size: 14px;
    color: #8492a6;
    margin-bottom: 8px;
}

.stat-trend {
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 12px;
    font-weight: 500;
}

.stat-trend.up {
    color: #52c41a;
}

.stat-trend.down {
    color: #ff4d4f;
}

.stat-sparkline {
    display: flex;
    align-items: flex-end;
    gap: 2px;
    height: 40px;
    width: 60px;
}

.sparkline-bar {
    width: 4px;
    background: currentColor;
    border-radius: 2px;
    transition: all 0.3s ease;
}

.stat-card:hover .sparkline-bar {
    transform: scaleY(1.2);
}

/* 图表区域 */
.charts-section {
    margin-bottom: 24px;
}

.chart-card {
    background: #fff;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    margin-bottom: 20px;
    transition: all 0.3s ease;
    overflow: hidden;
}

.chart-card:hover {
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
    transform: translateY(-2px);
}

.chart-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 20px;
    border-bottom: 1px solid #f0f0f0;
}

.chart-header h3 {
    margin: 0;
    color: #1f2d3d;
    font-size: 16px;
}

.chart-container {
    padding: 20px;
}

.chart {
    width: 100%;
}

/* 实时数据流 */
.realtime-section {
    background: #fff;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    overflow: hidden;
}

.section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 20px;
    border-bottom: 1px solid #f0f0f0;
}

.section-header h3 {
    margin: 0;
    color: #1f2d3d;
}

.realtime-controls {
    display: flex;
    align-items: center;
    gap: 12px;
}

.realtime-data {
    max-height: 400px;
    overflow-y: auto;
    padding: 0;
}

.realtime-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 16px 20px;
    border-bottom: 1px solid #f8f9fa;
    transition: all 0.3s ease;
    animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
    from {
        opacity: 0;
        transform: translateX(-20px);
    }

    to {
        opacity: 1;
        transform: translateX(0);
    }
}

.realtime-item:hover {
    background: #f8f9fa;
    transform: translateX(4px);
}

.realtime-item:last-child {
    border-bottom: none;
}

.realtime-item.user {
    border-left: 3px solid #1890ff;
}

.realtime-item.ai {
    border-left: 3px solid #52c41a;
}

.item-avatar {
    flex-shrink: 0;
}

.item-content {
    flex: 1;
}

.item-message {
    color: #1f2d3d;
    margin-bottom: 4px;
    line-height: 1.4;
}

.item-time {
    font-size: 12px;
    color: #8492a6;
}

.item-badge {
    padding: 4px 8px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 500;
}

.item-badge.user {
    background: #e6f7ff;
    color: #1890ff;
}

.item-badge.ai {
    background: #f6ffed;
    color: #52c41a;
}

/* 响应式设计 */
@media (max-width: 768px) {
    .stats-container {
        padding: 12px;
    }

    .stats-header {
        flex-direction: column;
        gap: 16px;
        align-items: stretch;
    }

    .header-actions {
        justify-content: space-between;
    }

    .stat-card {
        padding: 16px;
    }

    .stat-value {
        font-size: 24px;
    }
}
</style>