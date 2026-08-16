<template>
  <view class="profile-page">
    <view class="hero-card">
      <view class="hero-top">
        <view class="avatar-wrap">
          <text class="avatar-text">张</text>
          <view class="status-dot"></view>
        </view>
        <view class="hero-info">
          <view class="name-row">
            <text class="user-name">张工</text>
            <text class="role-tag">检修工程师</text>
          </view>
          <text class="user-desc">动力设备检修一组 · 擅长发动机 / 电气系统</text>
          <text class="user-meta">工号 MX-2026-001 · 当前在线 · 今日负责 ZK-320 复检</text>
        </view>
      </view>

      <view class="hero-stats">
        <view v-for="item in identityStats" :key="item.label" class="hero-stat">
          <text class="stat-value">{{ item.value }}</text>
          <text class="stat-label">{{ item.label }}</text>
        </view>
      </view>
    </view>

    <view class="section-card">
      <view class="section-head">
        <view>
          <text class="section-title">今日任务概览</text>
          <text class="section-desc">聚合待处理、进行中、复检和高风险任务</text>
        </view>
        <view class="plain-btn" @tap="goTo('/pages/repair-tasks/repair-tasks', true)">任务中心</view>
      </view>
      <view class="task-grid">
        <view v-for="task in taskOverview" :key="task.label" class="task-box" :class="task.tone">
          <text class="task-value">{{ task.value }}</text>
          <text class="task-label">{{ task.label }}</text>
        </view>
      </view>
      <view class="current-task" @tap="goTo('/pages/task-detail/task-detail')">
        <view>
          <text class="current-title">当前重点工单</text>
          <text class="current-desc">ZK-320 配电柜过热检修 · 待完成复测确认</text>
        </view>
        <text class="arrow">›</text>
      </view>
    </view>

    <view class="section-card">
      <view class="section-head">
        <view>
          <text class="section-title">检修能力画像</text>
          <text class="section-desc">从检索、作业、安全、知识和复检维度评估</text>
        </view>
        <text class="score-badge">{{ abilityScore }} 分</text>
      </view>
      <view class="ability-list">
        <view v-for="item in abilityProfile" :key="item.label" class="ability-row">
          <text class="ability-label">{{ item.label }}</text>
          <view class="bar-track">
            <view class="bar-fill" :style="{ width: item.value + '%', background: item.color }"></view>
          </view>
          <text class="ability-value" :style="{ color: item.color }">{{ item.value }}%</text>
        </view>
      </view>
    </view>

    <view class="two-column">
      <view class="section-card compact-card">
        <view class="section-head tight">
          <text class="section-title">我的任务与记录</text>
          <text class="view-more" @tap="goTo('/pages/repair-tasks/repair-tasks', true)">全部</text>
        </view>
        <view class="list">
          <view v-for="item in taskRecords" :key="item.title" class="list-item">
            <view class="dot" :style="{ background: item.color }"></view>
            <view class="list-content">
              <text class="list-title">{{ item.title }}</text>
              <text class="list-desc">{{ item.desc }}</text>
            </view>
          </view>
        </view>
      </view>

      <view class="section-card compact-card">
        <view class="section-head tight">
          <text class="section-title">我的知识贡献</text>
          <text class="view-more" @tap="goTo('/pages/personal-center/my-uploads')">上传</text>
        </view>
        <view class="contribution-grid">
          <view v-for="item in contributions" :key="item.label" class="contribution-item">
            <text class="contribution-value">{{ item.value }}</text>
            <text class="contribution-label">{{ item.label }}</text>
          </view>
        </view>
        <view class="review-tip">
          <text class="review-title">待审核知识 2 条</text>
          <text class="review-desc">发动机异响案例、配电柜温升 SOP</text>
        </view>
      </view>
    </view>

    <view class="section-card">
      <view class="section-head">
        <view>
          <text class="section-title">核查与质量评分</text>
          <text class="section-desc">复核引用依据、作业合规、安全风险和报告完整度</text>
        </view>
        <view class="primary-btn" @tap="runAudit">{{ checking ? '核查中' : '开始核查' }}</view>
      </view>

      <view v-if="audit" class="audit-layout">
        <view class="audit-score" :class="{ passed: audit.passed }">
          <text class="audit-number">{{ audit.score }}</text>
          <text class="audit-label">{{ audit.passed ? '可提交演示' : '需要补齐' }}</text>
        </view>
        <view class="audit-list">
          <view v-for="item in audit.checklist" :key="item.item" class="audit-item">
            <text class="audit-dot" :class="{ ok: item.passed }">{{ item.passed ? '✓' : '!' }}</text>
            <text class="audit-text">{{ item.item }}</text>
          </view>
        </view>
      </view>
      <text v-if="audit" class="audit-suggestion">{{ audit.suggestion }}</text>
    </view>

    <view class="section-card">
      <view class="section-head tight">
        <text class="section-title">最近浏览</text>
        <text class="view-more" @tap="goTo('/pages/knowledge-base/knowledge-base', true)">知识库</text>
      </view>
      <view class="recent-list">
        <view v-for="item in recentViews" :key="item.title" class="recent-item" @tap="openRecent(item)">
          <view>
            <text class="recent-title">{{ item.title }}</text>
            <text class="recent-desc">{{ item.type }} · {{ item.time }}</text>
          </view>
          <text class="arrow">›</text>
        </view>
      </view>
    </view>

    <view class="section-card">
      <view class="section-head tight">
        <text class="section-title">常用工具入口</text>
      </view>
      <view class="tool-grid">
        <view v-for="tool in quickTools" :key="tool.label" class="tool-item" @tap="goTo(tool.path, tool.tabbar)">
          <view class="tool-icon" :style="{ background: tool.color }"></view>
          <text class="tool-label">{{ tool.label }}</text>
        </view>
      </view>
    </view>

    <view class="section-card settings-card">
      <view class="section-head tight">
        <text class="section-title">账号与系统设置</text>
      </view>
      <view class="settings-list">
        <view v-for="item in settings" :key="item.label" class="setting-item" @tap="handleSetting(item)">
          <text class="setting-label">{{ item.label }}</text>
          <text class="setting-desc">{{ item.desc }}</text>
          <text class="arrow">›</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import request from '../../utils/request.js'

export default {
  data() {
    return {
      checking: false,
      agents: [],
      audit: null,
      identityStats: [
        { label: '今日任务', value: '6' },
        { label: '高风险项', value: '2' },
        { label: '知识贡献', value: '18' },
        { label: '核查评分', value: '92' }
      ],
      taskOverview: [
        { label: '待处理', value: 3, tone: 'blue' },
        { label: '进行中', value: 2, tone: 'teal' },
        { label: '待复检', value: 1, tone: 'amber' },
        { label: '高风险', value: 2, tone: 'red' }
      ],
      abilityProfile: [
        { label: '检索能力', value: 92, color: '#2563eb' },
        { label: '作业规范', value: 88, color: '#0f766e' },
        { label: '安全意识', value: 94, color: '#dc2626' },
        { label: '知识沉淀', value: 86, color: '#7c3aed' },
        { label: '复检质量', value: 90, color: '#0891b2' }
      ],
      taskRecords: [
        { title: 'ZK-320 配电柜过热检修', desc: '待复测 · 风险等级高', color: '#dc2626' },
        { title: 'DLI-001 点火系统复核', desc: '进行中 · 引用手册 3 条', color: '#2563eb' },
        { title: 'CG-125 发动机异响排查', desc: '已完成 · 报告已归档', color: '#0f766e' }
      ],
      contributions: [
        { label: '上传案例', value: 8 },
        { label: '现场图片', value: 24 },
        { label: 'SOP 文档', value: 5 },
        { label: '已入库', value: 13 }
      ],
      recentViews: [
        { title: '摩托车发动机维修手册', type: '维修手册', time: '刚刚' },
        { title: '点火系统故障排查 SOP', type: '标准流程', time: '10 分钟前' },
        { title: '发动机异响诊断案例', type: '故障案例', time: '1 小时前' }
      ],
      quickTools: [
        { label: '智能检索', path: '/pages/repair-search/repair-search', tabbar: true, color: '#2563eb' },
        { label: '任务中心', path: '/pages/repair-tasks/repair-tasks', tabbar: true, color: '#0f766e' },
        { label: '知识库', path: '/pages/knowledge-base/knowledge-base', tabbar: true, color: '#7c3aed' },
        { label: '我的上传', path: '/pages/personal-center/my-uploads', tabbar: false, color: '#d97706' },
        { label: '检修报告', path: '/pages/webview/webview', tabbar: false, color: '#0891b2' },
        { label: '帮助中心', path: '/pages/webview/webview', tabbar: false, color: '#475569' }
      ],
      settings: [
        { label: '人员档案', desc: '头像、岗位、班组与专长设备' },
        { label: '账号安全', desc: '登录状态、密码与设备管理' },
        { label: '消息设置', desc: '任务提醒、复检通知与审核反馈' },
        { label: '关于一修', desc: '系统说明、版本信息与演示材料' }
      ]
    }
  },
  computed: {
    abilityScore() {
      const total = this.abilityProfile.reduce((sum, item) => sum + item.value, 0)
      return Math.round(total / this.abilityProfile.length)
    }
  },
  onLoad() {
    this.loadAgents()
    this.runAudit()
  },
  methods: {
    async loadAgents() {
      try {
        const response = await request.get('/agents', { service: 'yixiu' })
        this.agents = response?.data?.agents || []
      } catch (_error) {
        this.agents = []
      }
    },
    async runAudit() {
      if (this.checking) return
      this.checking = true
      try {
        const response = await request.post('/audit', {
          references: true,
          safety_checked: true,
          measurements: true,
          retested: true,
          report_ready: true
        }, { service: 'yixiu' })
        if (response && response.code === 200) {
          this.audit = response.data
        }
      } catch (_error) {
        uni.showToast({ title: '核查服务暂不可用', icon: 'none' })
      } finally {
        this.checking = false
      }
    },
    goTo(path, tabbar = false) {
      if (tabbar) {
        uni.switchTab({ url: path })
        return
      }
      uni.navigateTo({ url: path })
    },
    openRecent(item) {
      uni.showToast({ title: `打开：${item.title}`, icon: 'none' })
    },
    handleSetting(item) {
      uni.showToast({ title: item.label, icon: 'none' })
    }
  }
}
</script>

<style scoped>
.profile-page {
  min-height: 100vh;
  padding: 32rpx 32rpx 168rpx;
  background: #eef3f8;
  box-sizing: border-box;
}

.hero-card,
.section-card {
  background: #ffffff;
  border: 1rpx solid #dbe4ef;
  border-radius: 20rpx;
  box-shadow: 0 8rpx 22rpx rgba(15, 23, 42, 0.05);
}

.hero-card {
  padding: 30rpx;
  background: linear-gradient(135deg, #172033, #0f766e);
  color: #ffffff;
}

.hero-top {
  display: flex;
  align-items: center;
  gap: 22rpx;
}

.avatar-wrap {
  position: relative;
  width: 104rpx;
  height: 104rpx;
  border-radius: 28rpx;
  background: rgba(255, 255, 255, 0.16);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.avatar-text {
  font-size: 44rpx;
  font-weight: 900;
}

.status-dot {
  position: absolute;
  right: 6rpx;
  bottom: 6rpx;
  width: 18rpx;
  height: 18rpx;
  border-radius: 50%;
  background: #22c55e;
  border: 4rpx solid #172033;
}

.hero-info {
  flex: 1;
  min-width: 0;
}

.name-row {
  display: flex;
  align-items: center;
  gap: 12rpx;
  flex-wrap: wrap;
}

.user-name,
.section-title,
.stat-value,
.task-value,
.ability-label,
.list-title,
.contribution-value,
.review-title,
.audit-number,
.recent-title,
.tool-label,
.setting-label {
  display: block;
}

.user-name {
  font-size: 42rpx;
  font-weight: 900;
  line-height: 1.2;
}

.role-tag {
  padding: 6rpx 12rpx;
  border-radius: 999rpx;
  background: rgba(255, 255, 255, 0.16);
  color: rgba(255, 255, 255, 0.88);
  font-size: 21rpx;
  font-weight: 800;
}

.user-desc,
.user-meta {
  display: block;
  margin-top: 8rpx;
  color: rgba(255, 255, 255, 0.78);
  font-size: 23rpx;
  line-height: 1.5;
}

.hero-stats {
  margin-top: 26rpx;
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12rpx;
}

.hero-stat {
  padding: 18rpx 12rpx;
  border-radius: 16rpx;
  background: rgba(255, 255, 255, 0.12);
  text-align: center;
}

.stat-value {
  font-size: 34rpx;
  font-weight: 900;
}

.stat-label {
  display: block;
  margin-top: 4rpx;
  font-size: 20rpx;
  color: rgba(255, 255, 255, 0.72);
}

.section-card {
  margin-top: 20rpx;
  padding: 26rpx;
}

.section-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 20rpx;
  margin-bottom: 22rpx;
}

.section-head.tight {
  align-items: center;
  margin-bottom: 18rpx;
}

.section-title {
  color: #0f172a;
  font-size: 30rpx;
  font-weight: 900;
}

.section-desc {
  display: block;
  margin-top: 8rpx;
  color: #64748b;
  font-size: 22rpx;
  line-height: 1.5;
}

.plain-btn,
.primary-btn {
  min-height: 48rpx;
  padding: 12rpx 20rpx;
  border-radius: 14rpx;
  font-size: 23rpx;
  font-weight: 900;
  flex-shrink: 0;
}

.plain-btn {
  background: #eff6ff;
  color: #2563eb;
}

.primary-btn {
  background: #0f766e;
  color: #ffffff;
}

.task-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14rpx;
}

.task-box {
  min-height: 112rpx;
  padding: 18rpx;
  border-radius: 16rpx;
  box-sizing: border-box;
}

.task-box.blue { background: #eff6ff; color: #2563eb; }
.task-box.teal { background: #ecfdf5; color: #0f766e; }
.task-box.amber { background: #fffbeb; color: #b45309; }
.task-box.red { background: #fef2f2; color: #dc2626; }

.task-value {
  font-size: 38rpx;
  font-weight: 900;
}

.task-label {
  display: block;
  margin-top: 4rpx;
  font-size: 22rpx;
  font-weight: 800;
}

.current-task,
.recent-item,
.setting-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18rpx;
}

.current-task {
  margin-top: 18rpx;
  padding: 20rpx;
  border-radius: 16rpx;
  background: #f8fafc;
  border: 1rpx solid #e2e8f0;
}

.current-title,
.current-desc,
.list-desc,
.review-desc,
.recent-desc,
.setting-desc {
  display: block;
}

.current-title {
  color: #0f172a;
  font-size: 25rpx;
  font-weight: 900;
}

.current-desc {
  margin-top: 6rpx;
  color: #64748b;
  font-size: 22rpx;
}

.arrow {
  color: #94a3b8;
  font-size: 42rpx;
  line-height: 1;
  flex-shrink: 0;
}

.score-badge {
  padding: 10rpx 16rpx;
  border-radius: 999rpx;
  background: #ecfdf5;
  color: #0f766e;
  font-size: 23rpx;
  font-weight: 900;
}

.ability-list {
  display: flex;
  flex-direction: column;
  gap: 18rpx;
}

.ability-row {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.ability-label {
  width: 128rpx;
  color: #334155;
  font-size: 24rpx;
  font-weight: 800;
  flex-shrink: 0;
}

.bar-track {
  flex: 1;
  height: 14rpx;
  border-radius: 999rpx;
  background: #e2e8f0;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: 999rpx;
}

.ability-value {
  width: 72rpx;
  text-align: right;
  font-size: 23rpx;
  font-weight: 900;
  flex-shrink: 0;
}

.two-column {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 20rpx;
}

.compact-card {
  min-width: 0;
}

.view-more {
  color: #2563eb;
  font-size: 23rpx;
  font-weight: 900;
}

.list {
  display: flex;
  flex-direction: column;
  gap: 14rpx;
}

.list-item {
  display: flex;
  gap: 14rpx;
  padding: 16rpx;
  border-radius: 14rpx;
  background: #f8fafc;
}

.dot {
  width: 12rpx;
  height: 12rpx;
  margin-top: 10rpx;
  border-radius: 50%;
  flex-shrink: 0;
}

.list-content {
  min-width: 0;
}

.list-title {
  color: #0f172a;
  font-size: 24rpx;
  font-weight: 900;
}

.list-desc {
  margin-top: 6rpx;
  color: #64748b;
  font-size: 21rpx;
}

.contribution-grid,
.tool-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12rpx;
}

.contribution-item {
  padding: 18rpx 10rpx;
  border-radius: 14rpx;
  background: #f8fafc;
  text-align: center;
}

.contribution-value {
  color: #0f172a;
  font-size: 32rpx;
  font-weight: 900;
}

.contribution-label {
  display: block;
  margin-top: 4rpx;
  color: #64748b;
  font-size: 20rpx;
}

.review-tip {
  margin-top: 14rpx;
  padding: 18rpx;
  border-radius: 14rpx;
  background: #fffbeb;
}

.review-title {
  color: #92400e;
  font-size: 24rpx;
  font-weight: 900;
}

.review-desc {
  margin-top: 6rpx;
  color: #b45309;
  font-size: 21rpx;
}

.audit-layout {
  display: grid;
  grid-template-columns: 220rpx minmax(0, 1fr);
  gap: 20rpx;
}

.audit-score {
  padding: 24rpx;
  border-radius: 18rpx;
  background: #fef2f2;
  color: #dc2626;
  text-align: center;
}

.audit-score.passed {
  background: #ecfdf5;
  color: #0f766e;
}

.audit-number {
  font-size: 60rpx;
  font-weight: 900;
  line-height: 1;
}

.audit-label {
  display: block;
  margin-top: 10rpx;
  font-size: 21rpx;
  font-weight: 900;
}

.audit-list {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

.audit-item {
  display: flex;
  align-items: center;
  gap: 12rpx;
}

.audit-dot {
  width: 36rpx;
  height: 36rpx;
  border-radius: 50%;
  background: #fee2e2;
  color: #dc2626;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20rpx;
  font-weight: 900;
  flex-shrink: 0;
}

.audit-dot.ok {
  background: #ccfbf1;
  color: #0f766e;
}

.audit-text {
  color: #334155;
  font-size: 23rpx;
}

.audit-suggestion {
  display: block;
  margin-top: 18rpx;
  color: #475569;
  font-size: 23rpx;
  line-height: 1.6;
}

.recent-list,
.settings-list {
  display: flex;
  flex-direction: column;
}

.recent-item,
.setting-item {
  min-height: 72rpx;
  padding: 18rpx 0;
  border-bottom: 1rpx solid #edf2f7;
}

.recent-item:last-child,
.setting-item:last-child {
  border-bottom: none;
}

.recent-title {
  color: #0f172a;
  font-size: 25rpx;
  font-weight: 900;
}

.recent-desc,
.setting-desc {
  margin-top: 6rpx;
  color: #64748b;
  font-size: 21rpx;
}

.tool-grid {
  grid-template-columns: repeat(6, minmax(0, 1fr));
}

.tool-item {
  min-height: 116rpx;
  padding: 18rpx 10rpx;
  border-radius: 16rpx;
  background: #f8fafc;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10rpx;
}

.tool-icon {
  width: 26rpx;
  height: 26rpx;
  border-radius: 9rpx;
}

.tool-label {
  color: #334155;
  font-size: 22rpx;
  font-weight: 900;
  text-align: center;
}

.settings-card {
  margin-bottom: 20rpx;
}

.setting-item {
  position: relative;
  padding-right: 42rpx;
  align-items: flex-start;
}

.setting-item .arrow {
  position: absolute;
  right: 0;
  top: 22rpx;
}

.setting-label {
  color: #0f172a;
  font-size: 25rpx;
  font-weight: 900;
}

@media screen and (max-width: 840px) {
  .hero-stats,
  .task-grid,
  .contribution-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .two-column,
  .audit-layout {
    grid-template-columns: 1fr;
  }

  .tool-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}
</style>
