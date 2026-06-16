<template>
  <view class="kd-container">
    <!-- 顶部导航 -->
    <view class="kd-header" :style="{ paddingTop: (statusBarHeight + 10) + 'px' }">
      <view class="header-back" @click="goBack"><text class="back-arrow">←</text></view>
      <text class="header-title">知识详情</text>
      <view class="header-fav" @click="toggleFav">
        <text class="fav-icon">{{ isFav ? '★' : '☆' }}</text>
      </view>
    </view>

    <scroll-view scroll-y class="kd-scroll">
      <!-- 标题区 -->
      <view class="title-section">
        <view class="title-top-row">
          <view class="title-cat" :class="'cat-' + item.category">{{ item.category }}</view>
          <view v-if="item.reviewStatus" class="title-status" :class="'status-' + item.reviewStatus">
            {{ item.reviewStatus === 'approved' ? '✅ 已审核' : item.reviewStatus === 'pending' ? '⏳ 待审核' : '✏️ 已修正' }}
          </view>
        </view>
        <text class="title-text">{{ item.icon ? item.icon + ' ' : '' }}{{ item.title }}</text>
        <view class="title-meta">
          <text class="meta">📖 {{ item.source }}</text>
          <text class="meta">🕐 {{ item.updated_at || item.created_at || '未知时间' }}</text>
        </view>
      </view>

      <!-- 基本信息 -->
      <view class="info-card">
        <view class="info-row">
          <text class="info-label">适用设备</text>
          <text class="info-value">{{ item.equipment_category }} {{ item.equipment_model || '' }}</text>
        </view>
        <view class="info-row">
          <text class="info-label">故障类型</text>
          <text class="info-value">{{ item.fault_type || '通用' }}</text>
        </view>
        <view class="info-row">
          <text class="info-label">引用来源</text>
          <text class="info-value">{{ item.source }}</text>
        </view>
        <view class="info-row">
          <text class="info-label">浏览/引用</text>
          <text class="info-value">👁 {{ item.view_count }} · 📎 {{ item.use_count || 0 }}</text>
        </view>
        <view class="info-row">
          <text class="info-label">评分</text>
          <text class="info-value rating">⭐ {{ item.rating }}</text>
        </view>
      </view>

      <!-- 处理方法 -->
      <view class="content-card">
        <view class="card-header">
          <text class="card-icon">📝</text>
          <text class="card-title">处理方法</text>
        </view>
        <text class="content-text">{{ item.content }}</text>
      </view>

      <!-- 标签 -->
      <view class="tags-card" v-if="parsedTags.length">
        <text class="card-title-small">相关标签</text>
        <view class="tags-row">
          <view class="tag-item" v-for="(tag, i) in parsedTags" :key="i">{{ tag }}</view>
        </view>
      </view>

      <!-- 关联任务 -->
      <view class="related-card">
        <view class="card-header">
          <text class="card-icon">🔗</text>
          <text class="card-title">关联任务</text>
        </view>
        <view class="related-list">
          <view class="related-item" v-for="(r, i) in relatedTasks" :key="i" @click="goTask(r.id)">
            <text class="related-title">{{ r.title }}</text>
            <view class="related-status" :style="{ background: getStatusBg(r.status), color: getStatusColor(r.status) }">
              {{ getStatusText(r.status) }}
            </view>
          </view>
        </view>
      </view>

      <view style="height: 60rpx;"></view>
    </scroll-view>
  </view>
</template>

<script>
import request from '../../utils/request.js'

export default {
  data() {
    return {
      statusBarHeight: 0,
      itemId: 0,
      item: {},
      isFav: false,
      relatedTasks: [
        { id: 1, title: 'ZK-320配电柜过热检修', status: 'pending' },
        { id: 2, title: 'CG-125发动机异响排查', status: 'in_progress' },
      ]
    }
  },
  computed: {
    parsedTags() {
      if (!this.item.tags) return []
      try {
        return Array.isArray(this.item.tags) ? this.item.tags : JSON.parse(this.item.tags)
      } catch { return [] }
    }
  },
  onLoad(options) {
    this.statusBarHeight = uni.getSystemInfoSync().statusBarHeight || 0
    this.itemId = options.id
    this.loadDetail()
  },
  methods: {
    goBack() { uni.navigateBack() },
    toggleFav() { this.isFav = !this.isFav },
    goTask(id) { uni.navigateTo({ url: `/pages/task-detail/task-detail?id=${id}` }) },

    async loadDetail() {
      // 优先从 localStorage 读取图谱节点数据
      try {
        const cached = uni.getStorageSync('selectedGraphNode')
        if (cached) {
          const node = JSON.parse(cached)
          this.item = {
            id: node.id,
            title: node.title || node.label || '知识节点',
            category: node.category || '通用',
            icon: node.icon || '',
            content: node.desc || '暂无详细内容',
            source: '知识图谱',
            equipment_category: (node.tags && node.tags[0]) || '通用',
            fault_type: node.category || '',
            view_count: 0,
            use_count: 0,
            rating: 0,
            tags: JSON.stringify(node.tags || []),
            created_at: '',
            updated_at: '',
            reviewStatus: node.reviewStatus || '',
          }
          uni.removeStorageSync('selectedGraphNode')
          return
        }
      } catch (e) {}

      // 回退：从 API 获取
      try {
        const res = await request.get(`/api/maintenance-tasks/knowledge/${this.itemId}`)
        if (res.code === 200) { this.item = res.data }
      } catch (e) {
        this.item = {
          id: this.itemId, title: '摩托车发动机异响故障排查指南',
          content: '发动机异响是常见的故障现象，可能由气门间隙过大、链条磨损、轴承损坏等原因引起。\n\n排查步骤：\n1. 判断异响来源区域（上部/下部/前部/后部）\n2. 冷车与热车异响对比\n3. 使用听诊器定位具体部位\n4. 逐项检查可能原因\n\n注意事项：\n- 异响排查时发动机应处于怠速状态\n- 使用听诊器时注意安全距离\n- 记录异响频率和温度变化关系',
          category: '手册', equipment_category: '发动机', equipment_model: 'CG-125',
          fault_type: '异响', source: '摩托车发动机维修手册',
          view_count: 523, use_count: 89, rating: 4.8,
          tags: '["异响","排查","发动机","气门","链条","轴承"]',
          created_at: '2026-06-01', updated_at: '2026-06-08',
        }
      }
    },
    getStatusBg(s) { return { pending: '#FFFBEB', in_progress: '#EFF6FF', completed: '#F0FDF4' }[s] || '#F1F5F9' },
    getStatusColor(s) { return { pending: '#D97706', in_progress: '#2563EB', completed: '#16A34A' }[s] || '#6B7280' },
    getStatusText(s) { return { pending: '待处理', in_progress: '进行中', completed: '已完成' }[s] || s },
  }
}
</script>

<style scoped>
.kd-container { min-height: 100vh; background: #F1F5F9; }

.kd-header {
  background: linear-gradient(135deg, #1E3A5F 0%, #2563EB 100%);
  display: flex; align-items: center; justify-content: space-between;
  padding: 10rpx 24rpx 20rpx;
}
.header-back { padding: 16rpx; }
.back-arrow { font-size: 36rpx; color: #FFFFFF; font-weight: 700; }
.header-title { font-size: 34rpx; color: #FFFFFF; font-weight: 700; }
.header-fav { padding: 16rpx; }
.fav-icon { font-size: 36rpx; color: #FBBF24; }

.kd-scroll { height: 100vh; }

/* 标题区 */
.title-section {
  background: #FFFFFF; margin: 24rpx; border-radius: 16rpx;
  padding: 24rpx; box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.04);
}
.title-cat {
  font-size: 22rpx; font-weight: 700; padding: 4rpx 14rpx;
  border-radius: 8rpx; display: inline-block; margin-bottom: 12rpx;
}
.title-top-row { display: flex; align-items: center; gap: 12rpx; margin-bottom: 12rpx; }
.title-status {
  font-size: 20rpx; font-weight: 600; padding: 4rpx 12rpx;
  border-radius: 8rpx;
}
.status-approved { background: #F0FDF4; color: #16A34A; }
.status-pending { background: #FFFBEB; color: #D97706; }
.status-corrected { background: #FEF2F2; color: #EF4444; }
.cat-手册 { background: #EFF6FF; color: #2563EB; }
.cat-案例 { background: #FFF7ED; color: #EA580C; }
.cat-流程 { background: #F0FDF4; color: #16A34A; }
.cat-问答 { background: #FDF2F8; color: #DB2777; }
.title-text { font-size: 36rpx; font-weight: 800; color: #0F172A; display: block; margin-bottom: 12rpx; }
.title-meta { display: flex; gap: 24rpx; }
.meta { font-size: 24rpx; color: #94A3B8; }

/* 信息卡片 */
.info-card {
  background: #FFFFFF; margin: 0 24rpx 24rpx; border-radius: 16rpx;
  padding: 24rpx; box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.04);
}
.info-row {
  display: flex; justify-content: space-between; align-items: center;
  padding: 14rpx 0; border-bottom: 1rpx solid #F1F5F9;
}
.info-row:last-child { border-bottom: none; }
.info-label { font-size: 26rpx; color: #94A3B8; }
.info-value { font-size: 26rpx; color: #1E293B; font-weight: 600; }
.info-value.rating { color: #F59E0B; }

/* 内容卡片 */
.content-card, .tags-card, .related-card {
  background: #FFFFFF; margin: 0 24rpx 24rpx; border-radius: 16rpx;
  padding: 24rpx; box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.04);
}
.card-header { display: flex; align-items: center; gap: 10rpx; margin-bottom: 16rpx; }
.card-icon { font-size: 28rpx; }
.card-title { font-size: 30rpx; font-weight: 700; color: #0F172A; }
.card-title-small { font-size: 26rpx; font-weight: 700; color: #475569; margin-bottom: 12rpx; display: block; }
.content-text { font-size: 28rpx; color: #334155; line-height: 1.8; white-space: pre-wrap; }

/* 标签 */
.tags-row { display: flex; flex-wrap: wrap; gap: 10rpx; }
.tag-item {
  font-size: 24rpx; color: #2563EB; background: #EFF6FF;
  padding: 8rpx 20rpx; border-radius: 20rpx; font-weight: 600;
}

/* 关联任务 */
.related-list { display: flex; flex-direction: column; gap: 12rpx; }
.related-item {
  display: flex; justify-content: space-between; align-items: center;
  padding: 16rpx; background: #F8FAFC; border-radius: 12rpx;
  border: 1rpx solid #E2E8F0;
}
.related-title { font-size: 26rpx; font-weight: 600; color: #1E293B; flex: 1; }
.related-status {
  font-size: 20rpx; font-weight: 700; padding: 4rpx 14rpx; border-radius: 8rpx;
}
</style>
