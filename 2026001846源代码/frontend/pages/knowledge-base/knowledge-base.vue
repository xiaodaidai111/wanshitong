<template>
  <view class="yixiu-page">
    <view class="page-head">
      <text class="eyebrow">知识智能体</text>
      <text class="title">检修知识库与图谱沉淀</text>
      <text class="desc">统一管理设备、故障、部件、手册、案例和核查规则，为多模态检索提供依据。</text>
    </view>

    <view class="search-panel">
      <input class="search-input" v-model="keyword" placeholder="搜索手册、故障、部件或核查规则" @confirm="loadKnowledge" />
      <view class="search-btn" @tap="loadKnowledge">检索</view>
    </view>

    <view class="knowledge-grid">
      <view v-for="item in items" :key="item.id" class="knowledge-card">
        <view class="card-top">
          <text class="card-title">{{ item.title }}</text>
          <text class="card-type">{{ item.category || '知识条目' }}</text>
        </view>
        <text class="card-desc">{{ getContent(item) }}</text>
        <view class="tag-row">
          <text v-for="tag in getTags(item)" :key="tag" class="tag">{{ tag }}</text>
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
      keyword: '',
      items: []
    }
  },
  onLoad() {
    this.loadKnowledge()
  },
  methods: {
    async loadKnowledge() {
      try {
        const url = this.keyword ? `/knowledge?keyword=${encodeURIComponent(this.keyword)}` : '/knowledge'
        const response = await request.get(url, { service: 'yixiu' })
        this.items = response?.data?.items || []
      } catch (_error) {
        this.items = []
        uni.showToast({ title: '知识库服务暂不可用', icon: 'none' })
      }
    },
    getTags(item) {
      if (Array.isArray(item.keywords)) return item.keywords.slice(0, 5)
      if (typeof item.tags === 'string') {
        try {
          const parsed = JSON.parse(item.tags)
          return Array.isArray(parsed) ? parsed.slice(0, 5) : []
        } catch (_error) {
          return item.tags.split(',').slice(0, 5)
        }
      }
      return [item.fault_type, item.equipment_category].filter(Boolean).slice(0, 5)
    },
    getContent(item) {
      if (Array.isArray(item.content)) return item.content[0] || ''
      return item.content || item.source || item.fault_type || '已纳入一修检修知识库'
    }
  }
}
</script>

<style scoped>
.yixiu-page { min-height: 100vh; padding: 32rpx 32rpx 168rpx; background: #eef3f8; box-sizing: border-box; }
.page-head { padding: 32rpx; border-radius: 26rpx; background: linear-gradient(135deg, #0f172a, #7c3aed); color: #fff; }
.eyebrow, .title, .desc, .card-title, .card-desc { display: block; }
.eyebrow { font-size: 22rpx; font-weight: 900; color: rgba(255,255,255,0.72); }
.title { margin-top: 10rpx; font-size: 42rpx; font-weight: 900; line-height: 1.2; }
.desc { margin-top: 14rpx; max-width: 760rpx; font-size: 24rpx; color: rgba(255,255,255,0.78); line-height: 1.6; }
.search-panel { margin-top: 22rpx; display: flex; gap: 14rpx; padding: 18rpx; border-radius: 20rpx; background: #fff; border: 1rpx solid #dbe4ef; }
.search-input { flex: 1; min-width: 0; height: 68rpx; padding: 0 18rpx; border-radius: 14rpx; background: #f8fafc; color: #0f172a; font-size: 24rpx; }
.search-btn { width: 128rpx; height: 68rpx; border-radius: 14rpx; background: #0f766e; color: #fff; display: flex; align-items: center; justify-content: center; font-size: 24rpx; font-weight: 900; }
.knowledge-grid { margin-top: 20rpx; display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16rpx; }
.knowledge-card { min-width: 0; padding: 24rpx; border-radius: 20rpx; background: #fff; border: 1rpx solid #dbe4ef; box-shadow: 0 8rpx 22rpx rgba(15,23,42,0.05); }
.card-top { display: flex; align-items: flex-start; justify-content: space-between; gap: 12rpx; }
.card-title { flex: 1; color: #0f172a; font-size: 27rpx; font-weight: 900; line-height: 1.35; }
.card-type { padding: 7rpx 12rpx; border-radius: 999rpx; background: #f3e8ff; color: #7c3aed; font-size: 19rpx; font-weight: 900; flex-shrink: 0; }
.card-desc { margin-top: 14rpx; color: #475569; font-size: 22rpx; line-height: 1.55; }
.tag-row { margin-top: 16rpx; display: flex; flex-wrap: wrap; gap: 10rpx; }
.tag { padding: 7rpx 12rpx; border-radius: 10rpx; background: #f8fafc; color: #334155; font-size: 20rpx; font-weight: 800; }
@media screen and (max-width: 720px) { .knowledge-grid { grid-template-columns: 1fr; } }
</style>
