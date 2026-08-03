<template>
  <view class="yixiu-page">
    <view class="page-head">
      <text class="eyebrow">核查智能体</text>
      <text class="title">一修项目核查中心</text>
      <text class="desc">面向软件杯 A1 答辩，检查多智能体分工、检修闭环、知识依据和报告完整性。</text>
    </view>

    <view class="agent-grid">
      <view v-for="agent in agents" :key="agent.id" class="agent-card">
        <text class="agent-name">{{ agent.name }}</text>
        <text class="agent-role">{{ agent.role }}</text>
        <text class="agent-duty">{{ agent.duty }}</text>
      </view>
    </view>

    <view class="audit-panel">
      <view class="audit-head">
        <view>
          <text class="section-title">最终核查</text>
          <text class="section-desc">按 A1 赛题演示闭环自动检查。</text>
        </view>
        <view class="audit-btn" @tap="runAudit">{{ checking ? '核查中' : '开始核查' }}</view>
      </view>

      <view v-if="audit" class="audit-result">
        <view class="score-box" :class="{ passed: audit.passed }">
          <text class="score">{{ audit.score }}</text>
          <text class="score-label">{{ audit.passed ? '可提交演示' : '需要补齐' }}</text>
        </view>
        <view class="check-list">
          <view v-for="item in audit.checklist" :key="item.item" class="check-item">
            <text class="check-dot" :class="{ ok: item.passed }">{{ item.passed ? '✓' : '!' }}</text>
            <text class="check-text">{{ item.item }}</text>
          </view>
        </view>
        <text class="suggestion">{{ audit.suggestion }}</text>
      </view>
    </view>

    <view class="doc-panel">
      <text class="section-title">提交材料索引</text>
      <view class="doc-list">
        <view v-for="doc in docs" :key="doc.name" class="doc-item">
          <text class="doc-name">{{ doc.name }}</text>
          <text class="doc-desc">{{ doc.desc }}</text>
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
      docs: [
        { name: 'A1-yixiu-web-plan.md', desc: '赛题匹配、多智能体分工和核查清单' },
        { name: 'maintenance_knowledge_base.json', desc: '一修设备检修知识库数据源' },
        { name: 'H5 构建产物', desc: 'dist/build/h5，可作为网页版部署产物' }
      ]
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
    }
  }
}
</script>

<style scoped>
.yixiu-page { min-height: 100vh; padding: 32rpx 32rpx 168rpx; background: #eef3f8; box-sizing: border-box; }
.page-head { padding: 32rpx; border-radius: 26rpx; background: linear-gradient(135deg, #1f2937, #0f766e); color: #fff; }
.eyebrow, .title, .desc, .agent-name, .agent-role, .agent-duty, .section-title, .section-desc, .score, .score-label, .suggestion, .doc-name, .doc-desc { display: block; }
.eyebrow { font-size: 22rpx; font-weight: 900; color: rgba(255,255,255,0.72); }
.title { margin-top: 10rpx; font-size: 42rpx; font-weight: 900; line-height: 1.2; }
.desc { margin-top: 14rpx; max-width: 760rpx; font-size: 24rpx; color: rgba(255,255,255,0.78); line-height: 1.6; }
.agent-grid { margin-top: 22rpx; display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 16rpx; }
.agent-card, .audit-panel, .doc-panel { background: #fff; border: 1rpx solid #dbe4ef; border-radius: 20rpx; box-shadow: 0 8rpx 22rpx rgba(15,23,42,0.05); }
.agent-card { min-width: 0; padding: 22rpx; }
.agent-name { color: #0f172a; font-size: 26rpx; font-weight: 900; }
.agent-role { margin-top: 8rpx; color: #0f766e; font-size: 21rpx; font-weight: 900; }
.agent-duty { margin-top: 12rpx; color: #64748b; font-size: 21rpx; line-height: 1.5; }
.audit-panel, .doc-panel { margin-top: 20rpx; padding: 26rpx; }
.audit-head { display: flex; align-items: flex-start; justify-content: space-between; gap: 18rpx; }
.section-title { color: #0f172a; font-size: 30rpx; font-weight: 900; }
.section-desc { margin-top: 8rpx; color: #64748b; font-size: 22rpx; }
.audit-btn { padding: 14rpx 22rpx; border-radius: 14rpx; background: #0f766e; color: #fff; font-size: 23rpx; font-weight: 900; flex-shrink: 0; }
.audit-result { margin-top: 24rpx; display: grid; grid-template-columns: 220rpx minmax(0, 1fr); gap: 20rpx; align-items: stretch; }
.score-box { border-radius: 18rpx; padding: 24rpx; background: #fef2f2; color: #dc2626; text-align: center; }
.score-box.passed { background: #ecfdf5; color: #0f766e; }
.score { font-size: 58rpx; font-weight: 900; line-height: 1; }
.score-label { margin-top: 10rpx; font-size: 21rpx; font-weight: 900; }
.check-list { display: flex; flex-direction: column; gap: 12rpx; }
.check-item { display: flex; align-items: center; gap: 12rpx; }
.check-dot { width: 36rpx; height: 36rpx; border-radius: 50%; background: #fee2e2; color: #dc2626; display: flex; align-items: center; justify-content: center; font-size: 20rpx; font-weight: 900; flex-shrink: 0; }
.check-dot.ok { background: #ccfbf1; color: #0f766e; }
.check-text { color: #334155; font-size: 23rpx; }
.suggestion { grid-column: span 2; color: #475569; font-size: 23rpx; }
.doc-list { margin-top: 18rpx; display: flex; flex-direction: column; gap: 12rpx; }
.doc-item { padding: 18rpx; border-radius: 16rpx; background: #f8fafc; border: 1rpx solid #e2e8f0; }
.doc-name { color: #0f172a; font-size: 24rpx; font-weight: 900; }
.doc-desc { margin-top: 6rpx; color: #64748b; font-size: 21rpx; }
@media screen and (max-width: 840px) { .agent-grid { grid-template-columns: 1fr; } .audit-result { grid-template-columns: 1fr; } .suggestion { grid-column: span 1; } }
</style>
