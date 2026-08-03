<template>
  <view class="yixiu-page">
    <view class="page-head">
      <text class="eyebrow">检索智能体</text>
      <text class="title">多模态检修知识检索</text>
      <text class="desc">输入设备型号和故障现象，生成手册匹配、相似案例、SOP 与核查要点。</text>
    </view>

    <view class="panel">
      <view class="field">
        <text class="label">设备型号</text>
        <input class="input" v-model="form.deviceModel" placeholder="例如 CG-125、ZK-320" />
      </view>
      <view class="field">
        <text class="label">故障现象</text>
        <textarea class="textarea" v-model="form.query" placeholder="描述现场现象、声音、报警、温度或图片观察结果" />
      </view>
      <view class="mode-row">
        <view v-for="mode in modes" :key="mode" class="mode-chip" :class="{ active: selectedModes.includes(mode) }" @tap="toggleMode(mode)">
          <text>{{ mode }}</text>
        </view>
      </view>
      <view class="primary-btn" @tap="runSearch">
        <text>{{ loading ? '检索中...' : '开始检索' }}</text>
      </view>
    </view>

    <view v-if="result" class="result-grid">
      <view class="result-card score-card">
        <text class="score-label">综合匹配</text>
        <text class="score-value">{{ result.match_score }}%</text>
        <text class="score-desc">{{ result.device_model }} · {{ result.modalities.join(' + ') }}</text>
      </view>

      <view class="result-card">
        <text class="card-title">匹配手册</text>
        <view v-for="manual in result.matched_manuals" :key="manual.title" class="item">
          <text class="item-title">{{ manual.title }}</text>
          <text class="item-desc">{{ manual.chapter }} · {{ manual.confidence }}</text>
        </view>
      </view>

      <view class="result-card">
        <text class="card-title">相似案例</text>
        <view v-for="item in result.similar_cases" :key="item.title" class="item">
          <text class="item-title">{{ item.title }}</text>
          <text class="item-desc">{{ item.similarity }} · {{ item.solution }}</text>
        </view>
      </view>

      <view class="result-card">
        <text class="card-title">推荐 SOP</text>
        <view v-for="(step, index) in result.recommended_sop" :key="step" class="step-row">
          <text class="step-index">{{ index + 1 }}</text>
          <text class="step-text">{{ step }}</text>
        </view>
      </view>

      <view class="result-card audit-card">
        <text class="card-title">核查提醒</text>
        <view class="audit-tags">
          <text v-for="item in result.audit.must_check" :key="item" class="audit-tag">{{ item }}</text>
        </view>
        <text class="item-desc">风险等级：{{ result.audit.risk_level }} · {{ result.audit.auditor }}</text>
      </view>
    </view>
  </view>
</template>

<script>
import request from '../../utils/request.js'

export default {
  data() {
    return {
      loading: false,
      modes: ['文本', '图片', '语音', '型号'],
      selectedModes: ['文本', '型号'],
      form: {
        deviceModel: 'CG-125',
        query: '发动机启动后异响，怠速不稳，热车后声音略有减轻'
      },
      result: null
    }
  },
  onLoad() {
    this.runSearch()
  },
  methods: {
    toggleMode(mode) {
      if (this.selectedModes.includes(mode)) {
        this.selectedModes = this.selectedModes.filter((item) => item !== mode)
      } else {
        this.selectedModes.push(mode)
      }
    },
    async runSearch() {
      if (this.loading) return
      this.loading = true
      try {
        const response = await request.post('/search', {
          query: this.form.query,
          device_model: this.form.deviceModel,
          image_url: this.selectedModes.includes('图片') ? 'demo-image' : ''
        }, { service: 'yixiu' })
        if (response && response.code === 200) {
          this.result = response.data
        }
      } catch (_error) {
        uni.showToast({ title: '检索服务暂不可用', icon: 'none' })
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.yixiu-page { min-height: 100vh; padding: 32rpx 32rpx 168rpx; background: #eef3f8; box-sizing: border-box; }
.page-head { padding: 32rpx; border-radius: 26rpx; background: linear-gradient(135deg, #0b1f33, #0f766e); color: #fff; }
.eyebrow, .title, .desc, .label, .card-title, .score-label, .score-value, .score-desc, .item-title, .item-desc, .step-text { display: block; }
.eyebrow { font-size: 22rpx; font-weight: 900; color: rgba(255,255,255,0.72); }
.title { margin-top: 10rpx; font-size: 42rpx; font-weight: 900; line-height: 1.2; }
.desc { margin-top: 14rpx; max-width: 760rpx; font-size: 24rpx; color: rgba(255,255,255,0.78); line-height: 1.6; }
.panel, .result-card { background: #fff; border: 1rpx solid #dbe4ef; border-radius: 22rpx; box-shadow: 0 8rpx 22rpx rgba(15,23,42,0.05); }
.panel { margin-top: 22rpx; padding: 26rpx; }
.field { margin-bottom: 18rpx; }
.label { margin-bottom: 10rpx; color: #0f172a; font-size: 24rpx; font-weight: 900; }
.input, .textarea { width: 100%; background: #f8fafc; border: 1rpx solid #dbe4ef; border-radius: 16rpx; padding: 18rpx; font-size: 25rpx; color: #0f172a; box-sizing: border-box; }
.input { height: 74rpx; }
.textarea { height: 150rpx; line-height: 1.6; }
.mode-row, .audit-tags { display: flex; flex-wrap: wrap; gap: 12rpx; }
.mode-chip, .audit-tag { padding: 10rpx 18rpx; border-radius: 999rpx; background: #f1f5f9; color: #475569; font-size: 22rpx; font-weight: 800; }
.mode-chip.active { background: #ccfbf1; color: #0f766e; }
.primary-btn { margin-top: 22rpx; padding: 22rpx; border-radius: 16rpx; background: #0f766e; color: #fff; text-align: center; font-size: 26rpx; font-weight: 900; }
.result-grid { margin-top: 22rpx; display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 18rpx; }
.result-card { min-width: 0; padding: 24rpx; }
.score-card { background: #0f172a; color: #fff; }
.score-label { font-size: 22rpx; color: rgba(255,255,255,0.68); font-weight: 800; }
.score-value { margin-top: 12rpx; font-size: 56rpx; font-weight: 900; line-height: 1; }
.score-desc { margin-top: 10rpx; font-size: 22rpx; color: rgba(255,255,255,0.74); }
.card-title { margin-bottom: 16rpx; color: #0f172a; font-size: 28rpx; font-weight: 900; }
.item { padding: 16rpx 0; border-top: 1rpx solid #edf2f7; }
.item:first-of-type { border-top: 0; }
.item-title { color: #0f172a; font-size: 24rpx; font-weight: 900; }
.item-desc { margin-top: 6rpx; color: #64748b; font-size: 21rpx; line-height: 1.5; }
.step-row { display: flex; gap: 14rpx; padding: 12rpx 0; }
.step-index { width: 40rpx; height: 40rpx; border-radius: 12rpx; background: #ecfdf5; color: #0f766e; display: flex; align-items: center; justify-content: center; font-size: 20rpx; font-weight: 900; flex-shrink: 0; }
.step-text { flex: 1; color: #334155; font-size: 23rpx; line-height: 1.45; }
.audit-card { grid-column: span 2; }
@media screen and (max-width: 720px) { .result-grid { grid-template-columns: 1fr; } .audit-card { grid-column: span 1; } }
</style>
