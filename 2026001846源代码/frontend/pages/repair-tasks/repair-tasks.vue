<template>
  <view class="yixiu-page">
    <view class="page-head">
      <text class="eyebrow">作业智能体</text>
      <text class="title">检修任务工作台</text>
      <text class="desc">按风险、状态和负责人组织作业流程，让检修从发现问题到复测归档形成闭环。</text>
    </view>

    <view class="summary-grid">
      <view v-for="item in metrics" :key="item.label" class="summary-card">
        <text class="summary-value">{{ item.value }}</text>
        <text class="summary-label">{{ item.label }}</text>
      </view>
    </view>

    <view class="filter-row">
      <view v-for="tab in tabs" :key="tab.key" class="filter-chip" :class="{ active: status === tab.key }" @tap="setStatus(tab.key)">
        <text>{{ tab.label }}</text>
      </view>
    </view>

    <view class="task-list">
      <view v-for="task in tasks" :key="task.id" class="task-card" :class="'severity-' + task.severity">
        <view class="task-top">
          <view class="task-main">
            <text class="task-title">{{ task.title }}</text>
            <text class="task-desc">{{ task.description }}</text>
          </view>
          <text class="status-badge">{{ getStatusText(task.status) }}</text>
        </view>
        <view class="task-meta-row">
          <text>{{ task.equipment_name }} {{ task.equipment_model }}</text>
          <text>负责人 {{ task.assignee_name }}</text>
          <text>{{ getSeverityText(task.severity) }}</text>
        </view>
        <view class="sop-preview">
          <view v-for="step in sopSteps" :key="step" class="sop-step">
            <text>{{ step }}</text>
          </view>
        </view>
      </view>
      <view v-if="tasks.length === 0" class="empty">暂无对应状态的检修任务</view>
    </view>
  </view>
</template>

<script>
import request from '../../utils/request.js'

export default {
  data() {
    return {
      status: '',
      tabs: [
        { key: '', label: '全部' },
        { key: 'pending', label: '待处理' },
        { key: 'in_progress', label: '进行中' },
        { key: 'completed', label: '待验收' }
      ],
      tasks: [],
      sopSteps: ['安全确认', '故障记录', '部件检测', '复测提交']
    }
  },
  computed: {
    metrics() {
      const highRisk = this.tasks.filter((task) => task.severity === 'high' || task.severity === 'critical').length
      const running = this.tasks.filter((task) => task.status === 'in_progress').length
      const closed = this.tasks.filter((task) => task.status === 'completed' || task.status === 'verified').length
      return [
        { label: '任务总数', value: this.tasks.length },
        { label: '高风险', value: highRisk },
        { label: '进行中', value: running },
        { label: '待验收', value: closed }
      ]
    }
  },
  onLoad() {
    this.loadTasks()
  },
  methods: {
    setStatus(status) {
      this.status = status
      this.loadTasks()
    },
    async loadTasks() {
      try {
        const url = this.status ? `/tasks?status=${encodeURIComponent(this.status)}` : '/tasks'
        const response = await request.get(url, { service: 'yixiu' })
        this.tasks = response?.data?.tasks || []
      } catch (_error) {
        this.tasks = []
        uni.showToast({ title: '任务服务暂不可用', icon: 'none' })
      }
    },
    getStatusText(status) {
      const map = { pending: '待处理', in_progress: '进行中', completed: '待验收', verified: '已闭环', rejected: '需返工' }
      return map[status] || '待处理'
    },
    getSeverityText(severity) {
      const map = { low: '低风险', medium: '中风险', high: '高风险', critical: '严重风险' }
      return map[severity] || '中风险'
    }
  }
}
</script>

<style scoped>
.yixiu-page { min-height: 100vh; padding: 32rpx 32rpx 168rpx; background: #eef3f8; box-sizing: border-box; }
.page-head { padding: 32rpx; border-radius: 26rpx; background: linear-gradient(135deg, #102a43, #2563eb); color: #fff; }
.eyebrow, .title, .desc, .summary-value, .summary-label, .task-title, .task-desc { display: block; }
.eyebrow { font-size: 22rpx; font-weight: 900; color: rgba(255,255,255,0.72); }
.title { margin-top: 10rpx; font-size: 42rpx; font-weight: 900; line-height: 1.2; }
.desc { margin-top: 14rpx; max-width: 760rpx; font-size: 24rpx; color: rgba(255,255,255,0.78); line-height: 1.6; }
.summary-grid { margin-top: 22rpx; display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 16rpx; }
.summary-card, .task-card { background: #fff; border: 1rpx solid #dbe4ef; box-shadow: 0 8rpx 22rpx rgba(15,23,42,0.05); }
.summary-card { padding: 22rpx; border-radius: 18rpx; text-align: center; }
.summary-value { color: #0f172a; font-size: 40rpx; font-weight: 900; }
.summary-label { color: #64748b; font-size: 21rpx; font-weight: 800; }
.filter-row { margin-top: 22rpx; display: flex; gap: 12rpx; flex-wrap: wrap; }
.filter-chip { padding: 12rpx 20rpx; border-radius: 999rpx; background: #fff; color: #475569; border: 1rpx solid #dbe4ef; font-size: 23rpx; font-weight: 900; }
.filter-chip.active { background: #dbeafe; color: #1d4ed8; }
.task-list { margin-top: 20rpx; display: flex; flex-direction: column; gap: 16rpx; }
.task-card { border-radius: 20rpx; padding: 24rpx; border-left: 8rpx solid #d97706; }
.task-card.severity-high, .task-card.severity-critical { border-left-color: #dc2626; }
.task-card.severity-low { border-left-color: #2563eb; }
.task-top, .task-meta-row, .sop-preview { display: flex; gap: 14rpx; }
.task-top { align-items: flex-start; justify-content: space-between; }
.task-main { flex: 1; min-width: 0; }
.task-title { color: #0f172a; font-size: 28rpx; font-weight: 900; }
.task-desc { margin-top: 8rpx; color: #64748b; font-size: 22rpx; line-height: 1.5; }
.status-badge { padding: 8rpx 16rpx; border-radius: 999rpx; background: #ecfdf5; color: #0f766e; font-size: 21rpx; font-weight: 900; flex-shrink: 0; }
.task-meta-row { margin-top: 16rpx; flex-wrap: wrap; color: #475569; font-size: 21rpx; }
.sop-preview { margin-top: 18rpx; flex-wrap: wrap; }
.sop-step { padding: 8rpx 14rpx; border-radius: 12rpx; background: #f8fafc; color: #334155; font-size: 20rpx; font-weight: 800; }
.empty { padding: 50rpx; text-align: center; color: #94a3b8; font-size: 24rpx; }
@media screen and (max-width: 720px) { .summary-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
</style>
