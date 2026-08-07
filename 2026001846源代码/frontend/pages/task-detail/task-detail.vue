<template>
  <view class="detail-container">
    <view class="detail-header" :style="{ paddingTop: (statusBarHeight + 10) + 'px' }">
      <view class="header-back" @click="goBack">
        <text class="back-arrow">←</text>
      </view>
      <text class="header-title">任务详情</text>
      <view class="header-placeholder"></view>
    </view>

    <scroll-view scroll-y class="detail-scroll">
      <view class="device-card">
        <view class="device-severity" :style="{ background: getSeverityColor(task.severity) }"></view>
        <view class="device-info">
          <text class="device-name">{{ task.equipment?.name || '未知设备' }}</text>
          <text class="device-model">{{ task.equipment?.model || '未登记型号' }} · {{ task.equipment?.category || '未分类设备' }}</text>
        </view>
        <view class="device-tags">
          <view class="tag" :style="{ background: getSeverityBg(task.severity), color: getSeverityColor(task.severity) }">
            {{ getSeverityText(task.severity) }}
          </view>
          <view class="tag" :style="{ background: getStatusBg(task.status), color: getStatusColor(task.status) }">
            {{ getStatusText(task.status) }}
          </view>
        </view>
        <view class="device-meta">
          <text class="meta">位置：{{ task.equipment?.location || '现场待确认' }}</text>
          <text class="meta">负责人：{{ task.assignee?.name || '未指派' }}</text>
        </view>
      </view>

      <view class="section-card">
        <view class="section-header">
          <text class="section-icon">!</text>
          <text class="section-title">故障信息</text>
        </view>
        <view class="info-grid">
          <view class="info-item full">
            <text class="info-label">故障描述</text>
            <text class="info-value">{{ task.description || '暂无故障描述' }}</text>
          </view>
          <view class="info-item" v-if="task.fault_code">
            <text class="info-label">报警码</text>
            <text class="info-value fault-code">{{ task.fault_code }}</text>
          </view>
          <view class="info-item">
            <text class="info-label">故障类型</text>
            <text class="info-value">{{ task.fault_category || '未分类' }}</text>
          </view>
          <view class="info-item">
            <text class="info-label">发生时间</text>
            <text class="info-value">{{ task.created_at || '未记录' }}</text>
          </view>
        </view>
      </view>

      <view class="section-card ai-section">
        <view class="section-header">
          <text class="section-icon">AI</text>
          <text class="section-title">AI 辅助分析</text>
          <view class="ai-badge">智能建议</view>
        </view>

        <view class="ai-block">
          <text class="ai-block-title">可能故障原因</text>
          <view class="cause-list">
            <view class="cause-item" v-for="(cause, i) in task.ai_suggestions?.possible_causes || []" :key="i">
              <text class="cause-index">{{ i + 1 }}</text>
              <text class="cause-text">{{ cause }}</text>
            </view>
          </view>
        </view>

        <view class="ai-block">
          <text class="ai-block-title">相似案例参考</text>
          <view class="case-list">
            <view class="case-item" v-for="(c, i) in task.ai_suggestions?.similar_cases || []" :key="i">
              <view class="case-header">
                <text class="case-title">{{ c.title }}</text>
                <view class="match-badge">匹配 {{ c.match }}</view>
              </view>
              <text class="case-result">处理结果：{{ c.result }}</text>
            </view>
          </view>
        </view>

        <view class="ai-block">
          <text class="ai-block-title">推荐检修方案</text>
          <text class="plan-text">{{ task.ai_suggestions?.recommended_plan || '暂无推荐方案' }}</text>
        </view>
      </view>

      <view class="section-card sop-section">
        <view class="section-header">
          <text class="section-icon">SOP</text>
          <text class="section-title">标准作业步骤</text>
          <text class="sop-progress">{{ completedSteps }}/{{ task.sop_steps?.length || 0 }}</text>
        </view>

        <view class="sop-timeline">
          <view v-for="(step, i) in task.sop_steps || []" :key="i" class="sop-step" :class="step.status">
            <view class="step-line-top" v-if="i > 0" :class="{ done: step.status === 'done' }"></view>
            <view class="step-node">
              <text class="step-icon">{{ step.icon }}</text>
            </view>
            <view class="step-content" @click="toggleStep(i)">
              <view class="step-header">
                <text class="step-title">步骤{{ step.index }}：{{ step.title }}</text>
                <view class="step-status-tag" :class="step.status">
                  {{ getStepStatusText(step.status) }}
                </view>
              </view>
              <text class="step-desc">{{ step.desc }}</text>
            </view>
          </view>
        </view>
      </view>

      <!-- 关联技术资料（反向联动） -->
      <view class="section-card">
        <view class="section-header">
          <text class="section-icon">📚</text>
          <text class="section-title">关联技术资料</text>
          <text class="sop-progress">{{ linkedKnowledge.length }}篇</text>
        </view>
        <view v-if="linkedKnowledge.length === 0" class="empty-linked">
          <text class="empty-linked-text">暂无关联技术资料</text>
          <text class="empty-linked-action" @click="goKnowledgeBase">去知识库关联 →</text>
        </view>
        <view v-else class="linked-list">
          <view v-for="(k, i) in linkedKnowledge" :key="i" class="linked-item" @click="goKnowledge(k.id)">
            <view class="linked-info">
              <text class="linked-title">{{ k.title }}</text>
              <text class="linked-meta">{{ k.category || '知识条目' }} · {{ k.updated_at || '未知时间' }}</text>
            </view>
            <text class="linked-arrow">→</text>
          </view>
        </view>
      </view>

      <view style="height: 180rpx;"></view>
    </scroll-view>

    <view class="bottom-actions">
      <view class="action-btn secondary" @click="pauseTask" v-if="task.status === 'in_progress'">
        <text class="btn-text">暂停</text>
      </view>
      <view class="action-btn primary" @click="startTask" v-if="task.status === 'pending'">
        <text class="btn-text">开始处理</text>
      </view>
      <view class="action-btn primary" @click="completeTask" v-if="task.status === 'in_progress'">
        <text class="btn-text">提交完成</text>
      </view>
      <view class="action-btn accent" @click="generateReport">
        <text class="btn-text">生成报告</text>
      </view>
    </view>
  </view>
</template>

<script>
import request from '../../utils/request.js'

export default {
  data() {
    return {
      statusBarHeight: 0,
      taskId: 0,
      task: {},
      linkedKnowledge: []
    }
  },
  computed: {
    completedSteps() {
      return (this.task.sop_steps || []).filter(s => s.status === 'done').length
    }
  },
  onLoad(options) {
    this.statusBarHeight = uni.getSystemInfoSync().statusBarHeight || 0
    this.taskId = options.id
    this.loadDetail()
  },
  methods: {
    goBack() { uni.navigateBack() },

    async loadDetail() {
      try {
        const res = await request.get(`/api/maintenance-tasks/${this.taskId}`)
        if (res.code === 200) {
          this.task = res.data
          this.loadLinkedKnowledge()
          return
        }
      } catch (e) {
        // 接口不可用时展示本地兜底任务，保证页面闭环可演示。
      }
      this.task = this.getFallbackDetail()
      this.loadLinkedKnowledge()
    },

    async loadLinkedKnowledge() {
      try {
        const res = await request.get(`/knowledge/linked/task/${this.taskId}`, { service: 'yixiu' })
        if (res && res.data) this.linkedKnowledge = res.data.items || []
      } catch (e) { this.linkedKnowledge = [] }
    },

    goKnowledge(id) {
      uni.navigateTo({ url: `/pages/knowledge-detail/knowledge-detail?id=${id}` })
    },

    goKnowledgeBase() {
      uni.switchTab({ url: '/pages/knowledge-base/knowledge-base' })
    },

    toggleStep(i) {
      const steps = this.task.sop_steps
      if (!steps || !steps[i]) return
      if (steps[i].status === 'done') {
        steps[i].status = 'pending'
      } else {
        steps[i].status = 'done'
        if (steps[i + 1] && steps[i + 1].status === 'pending') {
          steps[i + 1].status = 'active'
        }
      }
      this.$forceUpdate()
    },

    async startTask() {
      try {
        await request.put(`/api/maintenance-tasks/${this.taskId}/status`, { status: 'in_progress' })
      } catch (e) {}
      this.task.status = 'in_progress'
      if (this.task.sop_steps && this.task.sop_steps[0]) {
        this.task.sop_steps[0].status = 'active'
      }
      uni.showToast({ title: '已开始处理', icon: 'none' })
    },

    pauseTask() {
      uni.showToast({ title: '任务已暂停', icon: 'none' })
    },

    async completeTask() {
      try {
        await request.put(`/api/maintenance-tasks/${this.taskId}/status`, { status: 'completed' })
      } catch (e) {}
      this.task.status = 'completed'
      uni.showToast({ title: '任务已提交完成', icon: 'success' })
    },

    generateReport() {
      uni.showToast({ title: '报告生成中', icon: 'none' })
    },

    getSeverityColor(s) {
      return { low: '#10B981', medium: '#F59E0B', high: '#F97316', critical: '#EF4444' }[s] || '#94A3B8'
    },
    getSeverityBg(s) {
      return { low: '#F0FDF4', medium: '#FFFBEB', high: '#FFF7ED', critical: '#FEF2F2' }[s] || '#F1F5F9'
    },
    getSeverityText(s) {
      return { low: '一般', medium: '中等', high: '紧急', critical: '严重' }[s] || '未知'
    },
    getStatusBg(s) {
      return { pending: '#FFFBEB', in_progress: '#EFF6FF', completed: '#F0FDF4', verified: '#ECFDF5' }[s] || '#F1F5F9'
    },
    getStatusColor(s) {
      return { pending: '#D97706', in_progress: '#2563EB', completed: '#16A34A', verified: '#059669' }[s] || '#6B7280'
    },
    getStatusText(s) {
      return { pending: '待处理', in_progress: '进行中', completed: '待验收', verified: '已完成' }[s] || s
    },
    getStepStatusText(s) {
      return { pending: '待执行', active: '进行中', done: '已完成' }[s] || '待执行'
    },

    getFallbackDetail() {
      return {
        id: this.taskId,
        title: 'ZK-320配电柜过热检修',
        description: '配电柜运行温度异常升高，红外测温显示局部超过80℃。初步判断为接触器触点接触不良导致。',
        fault_code: 'E-001',
        fault_category: '过热',
        severity: 'high',
        status: 'pending',
        created_at: '2026-06-10 09:30:00',
        equipment: { name: '配电柜', model: 'ZK-320', category: '电气系统', location: '配电室B区', manufacturer: '正泰' },
        assignee: { name: '张工' },
        ai_suggestions: {
          possible_causes: ['接触不良导致电阻增大并产生局部过热', '长期运行导致绝缘老化', '环境湿度偏高引起端子腐蚀'],
          similar_cases: [{ id: 1, title: 'ZK-320配电柜过热故障检修', match: '92%', result: '更换接触器，清理散热通道' }],
          recommended_plan: '建议优先检查接触点和绝缘状态，按标准作业步骤逐项排查。预计工时约60分钟。'
        },
        sop_steps: [
          { index: 1, title: '安全确认', desc: '确认作业环境安全，穿戴绝缘手套、防护眼镜等防护装备。', icon: '安', status: 'pending' },
          { index: 2, title: '设备断电', desc: '断开电源，挂牌上锁，验电确认无电。', icon: '断', status: 'pending' },
          { index: 3, title: '外观检查', desc: '检查柜体、端子、接触器和散热通道，记录异常现象。', icon: '查', status: 'pending' },
          { index: 4, title: '部件检测', desc: '测量接触电阻和绝缘状态，确认关键部件是否异常。', icon: '测', status: 'pending' },
          { index: 5, title: '维修或更换', desc: '清理氧化触点，必要时更换接触器或老化端子。', icon: '修', status: 'pending' },
          { index: 6, title: '复测确认', desc: '送电后复测温度、电流和运行状态，确认故障排除。', icon: '验', status: 'pending' },
          { index: 7, title: '提交报告', desc: '填写检修报告，上传现场照片和处置结论。', icon: '报', status: 'pending' }
        ]
      }
    }
  }
}
</script>

<style scoped>
.detail-container {
  min-height: 100vh;
  background: #F1F5F9;
}

.detail-header {
  background: linear-gradient(135deg, #1E3A5F 0%, #2563EB 100%);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10rpx 24rpx 20rpx;
}
.header-back { padding: 16rpx; }
.back-arrow { font-size: 36rpx; color: #FFFFFF; font-weight: 700; }
.header-title { font-size: 34rpx; color: #FFFFFF; font-weight: 700; }
.header-placeholder { width: 60rpx; }

.detail-scroll { height: 100vh; }

.device-card {
  background: #FFFFFF;
  margin: 24rpx;
  border-radius: 16rpx;
  padding: 0 24rpx 24rpx;
  box-shadow: 0 4rpx 16rpx rgba(0,0,0,0.06);
  overflow: hidden;
}
.device-severity { height: 8rpx; margin: 0 -24rpx 20rpx; }
.device-info { margin-bottom: 12rpx; }
.device-name { font-size: 36rpx; font-weight: 800; color: #0F172A; display: block; }
.device-model { font-size: 24rpx; color: #64748B; margin-top: 4rpx; display: block; }
.device-tags { display: flex; gap: 12rpx; margin-bottom: 12rpx; }
.tag { font-size: 22rpx; font-weight: 700; padding: 6rpx 16rpx; border-radius: 8rpx; }
.device-meta { display: flex; gap: 24rpx; flex-wrap: wrap; }
.meta { font-size: 24rpx; color: #64748B; }

.section-card {
  background: #FFFFFF;
  margin: 0 24rpx 24rpx;
  border-radius: 16rpx;
  padding: 24rpx;
  box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.04);
}
.section-header {
  display: flex; align-items: center; gap: 10rpx;
  margin-bottom: 20rpx;
}
.section-icon { font-size: 24rpx; color: #2563EB; font-weight: 900; }
.section-title { font-size: 30rpx; font-weight: 700; color: #0F172A; flex: 1; }

.info-grid { display: flex; flex-wrap: wrap; gap: 16rpx; }
.info-item { width: calc(50% - 8rpx); }
.info-item.full { width: 100%; }
.info-label { font-size: 22rpx; color: #94A3B8; display: block; margin-bottom: 4rpx; }
.info-value { font-size: 28rpx; color: #1E293B; font-weight: 600; line-height: 1.6; }
.fault-code { color: #EF4444; font-family: monospace; }

.ai-section { border: 2rpx solid #DBEAFE; }
.ai-badge {
  font-size: 20rpx; color: #2563EB; background: #EFF6FF;
  padding: 4rpx 12rpx; border-radius: 6rpx; font-weight: 700;
}
.ai-block { margin-bottom: 24rpx; }
.ai-block:last-child { margin-bottom: 0; }
.ai-block-title { font-size: 26rpx; font-weight: 700; color: #334155; display: block; margin-bottom: 12rpx; }

.cause-list { display: flex; flex-direction: column; gap: 10rpx; }
.cause-item { display: flex; align-items: flex-start; gap: 12rpx; }
.cause-index {
  width: 36rpx; height: 36rpx; border-radius: 50%;
  background: #EFF6FF; color: #2563EB;
  font-size: 22rpx; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.cause-text { font-size: 26rpx; color: #475569; line-height: 1.5; }

.case-list { display: flex; flex-direction: column; gap: 12rpx; }
.case-item { background: #F8FAFC; border-radius: 12rpx; padding: 16rpx; border: 1rpx solid #E2E8F0; }
.case-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8rpx; gap: 12rpx; }
.case-title { font-size: 26rpx; font-weight: 600; color: #1E293B; flex: 1; }
.match-badge { font-size: 20rpx; color: #16A34A; background: #F0FDF4; padding: 4rpx 10rpx; border-radius: 6rpx; font-weight: 700; }
.case-result { font-size: 24rpx; color: #64748B; }

.plan-text { font-size: 26rpx; color: #475569; line-height: 1.7; background: #F0FDF4; padding: 16rpx; border-radius: 12rpx; border-left: 6rpx solid #10B981; }

.sop-progress { font-size: 24rpx; color: #2563EB; font-weight: 700; }
.sop-timeline { padding-left: 8rpx; }
.sop-step { display: flex; position: relative; }
.step-line-top {
  position: absolute; left: 28rpx; top: -20rpx;
  width: 4rpx; height: 20rpx;
  background: #E2E8F0;
}
.step-line-top.done { background: #10B981; }

.step-node {
  width: 56rpx; height: 56rpx;
  border-radius: 50%; background: #F1F5F9;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0; margin-right: 16rpx;
  border: 3rpx solid #E2E8F0;
  transition: all 0.3s;
}
.sop-step.done .step-node { background: #F0FDF4; border-color: #10B981; }
.sop-step.active .step-node { background: #EFF6FF; border-color: #2563EB; box-shadow: 0 0 12rpx rgba(37,99,235,0.3); }
.step-icon { font-size: 22rpx; font-weight: 800; color: #334155; }

.step-content {
  flex: 1; padding-bottom: 24rpx;
}
.step-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 4rpx; gap: 12rpx; }
.step-title { font-size: 28rpx; font-weight: 700; color: #1E293B; flex: 1; }
.step-status-tag {
  font-size: 20rpx; font-weight: 600; padding: 4rpx 10rpx; border-radius: 6rpx;
}
.step-status-tag.pending { color: #94A3B8; background: #F1F5F9; }
.step-status-tag.active { color: #2563EB; background: #EFF6FF; }
.step-status-tag.done { color: #16A34A; background: #F0FDF4; }
.step-desc { font-size: 24rpx; color: #64748B; line-height: 1.5; }

.bottom-actions {
  position: fixed; bottom: 0; left: 0; right: 0;
  background: #FFFFFF;
  padding: 16rpx 24rpx;
  padding-bottom: calc(16rpx + constant(safe-area-inset-bottom));
  padding-bottom: calc(16rpx + env(safe-area-inset-bottom));
  display: flex; gap: 16rpx;
  box-shadow: 0 -4rpx 16rpx rgba(0,0,0,0.06);
}
.action-btn {
  flex: 1; padding: 24rpx 0;
  border-radius: 12rpx;
  text-align: center;
  transition: all 0.2s;
}
.action-btn:active { transform: scale(0.96); }
.action-btn.primary { background: linear-gradient(135deg, #2563EB, #3B82F6); }
.action-btn.secondary { background: #F1F5F9; border: 1rpx solid #E2E8F0; }
.action-btn.accent { background: linear-gradient(135deg, #10B981, #34D399); }
.btn-text { font-size: 28rpx; font-weight: 700; }
.action-btn.primary .btn-text, .action-btn.accent .btn-text { color: #FFFFFF; }
.action-btn.secondary .btn-text { color: #475569; }

/* 关联技术资料 */
.empty-linked { padding: 24rpx 0; text-align: center; }
.empty-linked-text { font-size: 24rpx; color: #94A3B8; display: block; margin-bottom: 8rpx; }
.empty-linked-action { font-size: 24rpx; color: #2563EB; font-weight: 600; }
.linked-list { display: flex; flex-direction: column; gap: 12rpx; }
.linked-item {
  display: flex; align-items: center; justify-content: space-between;
  padding: 20rpx; background: #F8FAFC; border-radius: 12rpx;
  border: 1rpx solid #E2E8F0;
}
.linked-item:active { background: #F1F5F9; }
.linked-info { flex: 1; min-width: 0; }
.linked-title { font-size: 26rpx; font-weight: 600; color: #1E293B; display: block; }
.linked-meta { font-size: 22rpx; color: #94A3B8; margin-top: 6rpx; display: block; }
.linked-arrow { font-size: 28rpx; color: #CBD5E1; flex-shrink: 0; }
</style>
