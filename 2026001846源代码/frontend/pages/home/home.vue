<template>
  <view class="home-container">
    <!-- 骨架屏 -->
    <SkeletonScreen v-if="pageLoading" :loading="true" />

    <!-- 自定义导航栏 -->
    <view class="home-navbar" :style="{ paddingTop: statusBarHeight + 'px' }">
      <view class="home-navbar-content">
        <view class="home-brand-block">
          <image src="../../static/icon-home.png" class="home-brand-icon" mode="aspectFit"></image>
          <text class="home-brand-name">{{ brandTitle }}</text>
        </view>
      </view>
    </view>

    <!-- 轮播图区域 -->
    <view class="banner-section">
      <swiper class="banner-swiper" circular autoplay interval="5000" duration="600" indicator-dots indicator-active-color="#2563EB" indicator-color="rgba(255,255,255,0.4)">
        <swiper-item v-for="(banner, index) in banners" :key="index">
          <view class="banner-item" @tap="onBannerClick(banner)">
            <image :src="banner.image" mode="aspectFill" class="banner-img"></image>
            <view class="banner-overlay">
              <text class="banner-title">{{ banner.title }}</text>
              <text class="banner-sub">{{ banner.sub }}</text>
            </view>
          </view>
        </swiper-item>
      </swiper>
    </view>

    <!-- 快捷功能入口 -->
    <view class="quick-functions">
      <view class="quick-grid">
        <view class="quick-item" @click="navigateTo('/pages/takeaway-expert/takeaway-expert')">
          <view class="quick-icon-wrap bg-blue">
            <image src="../../static/assistant-search.png" class="quick-icon-img" mode="aspectFit" />
          </view>
          <text class="quick-name">智能检索</text>
        </view>
        <view class="quick-item" @click="navigateTo('/pages/health-manager/health-manager')">
          <view class="quick-icon-wrap bg-green">
            <image src="../../static/assistant-maintenance.png" class="quick-icon-img" mode="aspectFit" />
          </view>
          <text class="quick-name">检修任务</text>
        </view>
        <view class="quick-item" @click="navigateTo('/pages/restaurant-recommendation/restaurant-recommendation')">
          <view class="quick-icon-wrap bg-purple">
            <image src="../../static/assistant-knowledge.png" class="quick-icon-img" mode="aspectFit" />
          </view>
          <text class="quick-name">知识库</text>
        </view>
      </view>
    </view>

    <!-- 系统概览 -->
    <view class="overview-section">
      <view class="section-header">
        <text class="section-title">系统概览</text>
        <text class="section-more" @click="goToDashboard">查看详情 ›</text>
      </view>
      <view class="overview-grid">
        <view class="overview-card" v-for="(stat, idx) in systemStats" :key="idx">
          <view class="stat-icon-wrap" :style="{ background: stat.bg }">
            <text class="stat-icon">{{ stat.icon }}</text>
          </view>
          <text class="stat-value">{{ stat.value }}</text>
          <text class="stat-label">{{ stat.label }}</text>
          <view class="stat-dot" :style="{ background: stat.dotColor }"></view>
        </view>
      </view>
    </view>

    <!-- 今日任务 -->
    <view class="task-section">
      <view class="section-header">
        <view class="section-header-left">
          <text class="section-title">📋 今日任务</text>
          <view class="task-badge">{{ todayTasks.filter(t => !t.done).length }} 项待处理</view>
        </view>
        <text class="section-more" @click="navigateTo('/pages/health-manager/health-manager')">全部任务 ›</text>
      </view>
      <view class="task-list">
        <view class="task-item" v-for="(task, idx) in todayTasks.slice(0, 3)" :key="idx" @click="toggleTask(task)">
          <view class="task-check" :class="{ checked: task.done }">
            <text v-if="task.done" class="check-mark">✓</text>
          </view>
          <view class="task-info">
            <text class="task-name" :class="{ 'task-done': task.done }">{{ task.name }}</text>
            <text class="task-meta">{{ task.device }} · {{ task.level }}</text>
          </view>
          <view class="task-status-tag" :style="{ background: task.statusBg, color: task.statusColor }">
            {{ task.status }}
          </view>
        </view>
      </view>
      <view class="task-more" v-if="todayTasks.length > 3" @click="navigateTo('/pages/health-manager/health-manager')">
        <text class="task-more-text">查看全部 {{ todayTasks.length }} 项任务</text>
      </view>
    </view>

    <!-- 风险告警 -->
    <view class="alert-section" v-if="riskAlerts.length > 0">
      <view class="section-header">
        <view class="section-header-left">
          <text class="section-title">⚠️ 风险告警</text>
          <view class="alert-badge">{{ riskAlerts.length }} 项</view>
        </view>
      </view>
      <view class="alert-list">
        <view class="alert-item" v-for="(alert, idx) in riskAlerts.slice(0, 2)" :key="idx">
          <view class="alert-level-bar" :style="{ background: alert.levelColor }"></view>
          <view class="alert-info">
            <text class="alert-title">{{ alert.title }}</text>
            <text class="alert-desc">{{ alert.desc }}</text>
          </view>
          <view class="alert-tag" :style="{ background: alert.tagBg, color: alert.tagColor }">
            {{ alert.level }}
          </view>
        </view>
      </view>
    </view>

    <!-- 最新动态 -->
    <view class="latest-section">
      <view class="section-header">
        <text class="section-title">📚 最新动态</text>
      </view>
      <view class="knowledge-list">
        <view class="knowledge-item" v-for="(item, idx) in knowledgeUpdates.slice(0, 3)" :key="idx">
          <view class="kb-icon-wrap" :style="{ background: item.iconBg }">
            <text class="kb-icon">{{ item.icon }}</text>
          </view>
          <view class="kb-info">
            <text class="kb-title">{{ item.title }}</text>
            <text class="kb-desc">{{ item.desc }}</text>
          </view>
          <view class="kb-status-tag" :style="{ background: item.statusBg, color: item.statusColor }">
            {{ item.status }}
          </view>
        </view>
      </view>
    </view>

  </view>
</template>

<script>
import request, { getAssetURL } from '../../utils/request.js'
import SkeletonScreen from '../../src/components/SkeletonScreen.vue'

export default {
  components: { SkeletonScreen },
  data() {
    return {
      statusBarHeight: 0,
      pageLoading: true,
      brandTitle: '设备检修知识作业系统',
      banners: [
        { image: '../../static/industrial-banner-1.png', title: '多模态设备检修知识检索', sub: '摩托车发动机 / 故障图片 / 设备型号精准匹配', url: '' },
        { image: '../../static/industrial-banner-2.png', title: '标准化检修作业指引', sub: '点火系统 · 燃油供给 · 机油润滑 · 异响排查', url: '' },
        { image: '../../static/industrial-banner-3.png', title: '一线案例知识沉淀', sub: '案例上传 · 审核入库 · 图谱更新', url: '' }
      ],
      systemStats: [
        { icon: '📡', label: '在线设备', value: '128', bg: '#EFF6FF', dotColor: '#16A34A' },
        { icon: '🔔', label: '待处理告警', value: '5', bg: '#FFF7ED', dotColor: '#EA580C' },
        { icon: '📝', label: '待审核案例', value: '12', bg: '#FFFBEB', dotColor: '#D97706' },
        { icon: '🔧', label: '今日任务', value: '8', bg: '#F0FDF4', dotColor: '#2563EB' }
      ],
      todayTasks: [
        { name: '摩托车发动机基础检修', device: '发动机总成', level: '二级检修', status: '进行中', statusBg: '#EFF6FF', statusColor: '#2563EB', done: false },
        { name: '点火系统检查', device: '火花塞/点火线圈', level: '一级检修', status: '待处理', statusBg: '#FFF7ED', statusColor: '#EA580C', done: false },
        { name: '燃油供给检查', device: '油路/化油器', level: '巡检', status: '待处理', statusBg: '#FFFBEB', statusColor: '#D97706', done: false },
        { name: '发动机异响排查', device: '气门/链条/轴承', level: '故障抢修', status: '未开始', statusBg: '#F3F4F6', statusColor: '#6B7280', done: false }
      ],
      riskAlerts: [
        { title: '润滑不足风险', desc: '机油液位偏低，建议优先补充并检查渗漏点', level: '严重', levelColor: '#DC2626', tagBg: '#FEF2F2', tagColor: '#DC2626' },
        { title: '点火系统复核', desc: '火花塞间隙超标，需复核点火时序', level: '警告', levelColor: '#EA580C', tagBg: '#FFF7ED', tagColor: '#EA580C' },
        { title: '手册版本校验', desc: '摩托车发动机维修手册 v1.0 已入库，建议核对适用范围', level: '提示', levelColor: '#D97706', tagBg: '#FFFBEB', tagColor: '#D97706' }
      ],
      knowledgeUpdates: [
        { icon: '📄', title: '摩托车发动机维修手册已入库', desc: '涵盖发动机结构、故障排查、标准作业流程', status: '已入库', iconBg: '#F0FDF4', statusBg: '#F0FDF4', statusColor: '#16A34A' },
        { icon: '🔗', title: '新增发动机异响知识节点', desc: '关联气门间隙、链条磨损、轴承磨损排查路径', status: '已更新', iconBg: '#EFF6FF', statusBg: '#EFF6FF', statusColor: '#2563EB' },
        { icon: '📝', title: '待审核现场案例', desc: '一线人员上传启动困难处置案例，待审核入库', status: '待审核', iconBg: '#FFFBEB', statusBg: '#FFFBEB', statusColor: '#D97706' }
      ]
    }
  },

  onLoad() {
    const systemInfo = uni.getSystemInfoSync()
    this.statusBarHeight = systemInfo.statusBarHeight || 0
    this.fetchOverviewData()
    setTimeout(() => { this.pageLoading = false }, 500)
  },

  methods: {
    goToDashboard() {
      uni.showToast({ title: '功能开发中', icon: 'none' })
    },

    onBannerClick(banner) {
      if (!banner.url) return
      uni.navigateTo({
        url: '/pages/webview/webview?url=' + encodeURIComponent(banner.url) + '&title=' + encodeURIComponent(banner.title)
      })
    },

    navigateTo(path) {
      const tabPages = [
        '/pages/home/home',
        '/pages/takeaway-expert/takeaway-expert',
        '/pages/health-manager/health-manager',
        '/pages/restaurant-recommendation/restaurant-recommendation',
        '/pages/personal-center/personal-center'
      ]
      if (tabPages.includes(path)) {
        uni.switchTab({ url: path })
      } else {
        uni.navigateTo({ url: path })
      }
    },

    toggleTask(task) {
      task.done = !task.done
    },

    async fetchOverviewData() {
      try {
        const response = await request.get('/api/dashboard/overview')
        if (response.code === 200 && response.data) {
          const data = response.data
          this.systemStats = [
            { icon: '📡', label: '在线设备', value: String(data.online_equipment || 0), bg: '#EFF6FF', dotColor: '#16A34A' },
            { icon: '🔔', label: '待处理告警', value: String(data.pending_alerts || 0), bg: '#FFF7ED', dotColor: '#EA580C' },
            { icon: '📝', label: '待审核案例', value: String(data.pending_reviews || 0), bg: '#FFFBEB', dotColor: '#D97706' },
            { icon: '🔧', label: '今日任务', value: String(data.today_tasks || 0), bg: '#F0FDF4', dotColor: '#2563EB' }
          ]
        }
      } catch (_error) {
        // 使用默认数据
      }
    }
  }
}
</script>

<style scoped>
/* ===== 全局容器 ===== */
.home-container {
  min-height: 100vh;
  background: #F5F7FA !important;
  padding: 0 24rpx 200rpx;
  padding-bottom: calc(200rpx + constant(safe-area-inset-bottom));
  padding-bottom: calc(200rpx + env(safe-area-inset-bottom));
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  animation: fadeIn 0.6s ease-out;
  box-sizing: border-box;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20rpx); }
  to { opacity: 1; transform: translateY(0); }
}

/* ===== 导航栏 ===== */
.home-navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.98) 0%, rgba(255, 255, 255, 0.94) 100%);
  z-index: 500;
  backdrop-filter: blur(18rpx);
  -webkit-backdrop-filter: blur(18rpx);
  border-bottom: 1rpx solid rgba(229, 231, 235, 0.6);
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.06);
}

.home-navbar-content {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 44px;
  padding: 0 28rpx;
}

.home-brand-block {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.home-brand-icon {
  width: 64rpx;
  height: 64rpx;
}

.home-brand-name {
  font-size: 34rpx;
  font-weight: 800;
  color: #1F2937;
  letter-spacing: 0;
  line-height: 1.15;
  white-space: nowrap;
}

@keyframes slideInUp {
  from { opacity: 0; transform: translateY(40rpx); }
  to { opacity: 1; transform: translateY(0); }
}

/* ===== 轮播图 ===== */
.banner-section {
  margin-top: 180rpx;
  margin-bottom: 24rpx;
  border-radius: 16rpx;
  overflow: hidden;
  box-shadow: 0 8rpx 32rpx rgba(148, 163, 184, 0.15);
  animation: slideInUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) 0.15s both;
}

.banner-swiper {
  height: 320rpx;
  border-radius: 16rpx;
}

.banner-item {
  width: 100%;
  height: 100%;
  position: relative;
  border-radius: 16rpx;
  overflow: hidden;
}

.banner-img {
  width: 100%;
  height: 100%;
  border-radius: 16rpx;
}

.banner-overlay {
  position: absolute;
  bottom: 0; left: 0; right: 0;
  padding: 60rpx 32rpx 24rpx;
  background: linear-gradient(to top, rgba(0,0,0,0.7) 0%, transparent 100%);
  display: flex;
  flex-direction: column;
  gap: 8rpx;
  border-radius: 0 0 16rpx 16rpx;
}

.banner-title {
  color: #fff;
  font-size: 34rpx;
  font-weight: 800;
  text-shadow: 0 2rpx 8rpx rgba(0,0,0,0.2);
}

.banner-sub {
  color: rgba(255,255,255,0.9);
  font-size: 22rpx;
  font-weight: 500;
}

/* ===== 快捷功能入口 ===== */
.quick-functions {
  margin-bottom: 24rpx;
  animation: slideInUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) 0.2s both;
}

.quick-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16rpx;
}

.quick-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12rpx;
  padding: 24rpx 12rpx;
  background: #FFFFFF;
  border-radius: 16rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.06);
  border: 1rpx solid #E5E7EB;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.quick-item:active {
  transform: scale(0.95);
  box-shadow: 0 4rpx 16rpx rgba(37, 99, 235, 0.15);
}

.quick-icon-wrap {
  width: 96rpx;
  height: 96rpx;
  border-radius: 20rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.bg-blue { background: linear-gradient(135deg, #DBEAFE, #BFDBFE); }
.bg-green { background: linear-gradient(135deg, #D1FAE5, #A7F3D0); }
.bg-purple { background: linear-gradient(135deg, #E9D5FF, #D8B4FE); }
.bg-orange { background: linear-gradient(135deg, #FED7AA, #FDBA74); }

.quick-icon-img {
  width: 64rpx;
  height: 64rpx;
  border-radius: 12rpx;
}

.quick-name {
  font-size: 24rpx;
  font-weight: 600;
  color: #374151;
  text-align: center;
}

/* ===== 通用 Section Header ===== */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
}

.section-header-left {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.section-title {
  font-size: 30rpx;
  font-weight: 700;
  color: #1F2937;
}

.section-more {
  font-size: 24rpx;
  color: #6B7280;
  font-weight: 500;
  padding: 8rpx 16rpx;
  background: #F3F4F6;
  border-radius: 8rpx;
}

.section-more:active {
  background: #E5E7EB;
}

/* ===== 系统概览 ===== */
.overview-section {
  margin-bottom: 24rpx;
  background: #FFFFFF;
  border-radius: 16rpx;
  padding: 24rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.06);
  border: 1rpx solid #E5E7EB;
  animation: slideInUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) 0.25s both;
}

.overview-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12rpx;
}

.overview-card {
  background: linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 100%);
  border-radius: 12rpx;
  padding: 20rpx 8rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8rpx;
  border: 1rpx solid #E5E7EB;
  box-shadow: 0 1rpx 4rpx rgba(0,0,0,0.04);
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;
}

.overview-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4rpx;
  border-radius: 12rpx 12rpx 0 0;
}

.overview-card:nth-child(1)::before { background: linear-gradient(90deg, #10B981, #34D399); }
.overview-card:nth-child(2)::before { background: linear-gradient(90deg, #F59E0B, #FBBF24); }
.overview-card:nth-child(3)::before { background: linear-gradient(90deg, #3B82F6, #60A5FA); }
.overview-card:nth-child(4)::before { background: linear-gradient(90deg, #8B5CF6, #A78BFA); }

.stat-icon-wrap {
  width: 48rpx;
  height: 48rpx;
  border-radius: 10rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-icon { font-size: 26rpx; }
.stat-value {
  font-size: 36rpx;
  font-weight: 800;
  color: #0F172A;
  font-variant-numeric: tabular-nums;
  letter-spacing: -1rpx;
}
.stat-label {
  font-size: 18rpx;
  color: #64748B;
  font-weight: 600;
  letter-spacing: 0.5rpx;
}
.stat-dot {
  width: 8rpx;
  height: 8rpx;
  border-radius: 50%;
  position: absolute;
  top: 10rpx;
  right: 10rpx;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.6; transform: scale(1.3); }
}

/* ===== 今日任务 ===== */
.task-section {
  background: #FFFFFF;
  border-radius: 16rpx;
  padding: 24rpx;
  margin-bottom: 24rpx;
  border: 1rpx solid #E5E7EB;
  box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.04);
  position: relative;
  overflow: hidden;
  animation: slideInUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) 0.3s both;
}

.task-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  bottom: 0;
  width: 4rpx;
  background: linear-gradient(180deg, #3B82F6, #10B981);
}

.task-badge {
  font-size: 20rpx;
  padding: 4rpx 12rpx;
  background: #EFF6FF;
  color: #2563EB;
  border-radius: 8rpx;
  font-weight: 600;
}

.alert-badge {
  font-size: 20rpx;
  padding: 4rpx 12rpx;
  background: #FEF2F2;
  color: #DC2626;
  border-radius: 8rpx;
  font-weight: 600;
}

.task-list {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

.task-item {
  display: flex;
  align-items: center;
  gap: 16rpx;
  padding: 16rpx;
  background: linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 100%);
  border-radius: 12rpx;
  border: 1rpx solid #E2E8F0;
  transition: all 0.2s ease;
}

.task-item:active {
  transform: scale(0.98);
  background: #E2E8F0;
}

.task-check {
  width: 36rpx;
  height: 36rpx;
  border-radius: 8rpx;
  border: 2rpx solid #D1D5DB;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all 0.2s;
}

.task-check.checked {
  background: #16A34A;
  border-color: #16A34A;
}

.check-mark { color: #FFFFFF; font-size: 22rpx; font-weight: 700; }

.task-info { flex: 1; }
.task-name { font-size: 26rpx; font-weight: 600; color: #1F2937; display: block; }
.task-name.task-done { text-decoration: line-through; color: #9CA3AF; }
.task-meta { font-size: 20rpx; color: #6B7280; display: block; margin-top: 4rpx; }

.task-status-tag {
  font-size: 18rpx;
  padding: 4rpx 12rpx;
  border-radius: 6rpx;
  font-weight: 600;
  flex-shrink: 0;
}

.task-more {
  margin-top: 16rpx;
  padding: 12rpx;
  text-align: center;
  background: #F8FAFC;
  border-radius: 8rpx;
  border: 1rpx dashed #D1D5DB;
}

.task-more:active {
  background: #F1F5F9;
}

.task-more-text {
  font-size: 24rpx;
  color: #6B7280;
  font-weight: 500;
}

/* ===== 风险告警 ===== */
.alert-section {
  background: #FFFFFF;
  border-radius: 16rpx;
  padding: 24rpx;
  margin-bottom: 24rpx;
  border: 1rpx solid #E5E7EB;
  box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.04);
  position: relative;
  overflow: hidden;
  animation: slideInUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) 0.35s both;
}

.alert-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  bottom: 0;
  width: 4rpx;
  background: linear-gradient(180deg, #EF4444, #F59E0B);
}

.alert-list {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

.alert-item {
  display: flex;
  align-items: center;
  gap: 16rpx;
  padding: 16rpx;
  background: linear-gradient(135deg, #FFFBFB 0%, #FFF7ED 100%);
  border-radius: 12rpx;
  border: 1rpx solid #FEE2E2;
  transition: all 0.2s ease;
}

.alert-item:active {
  transform: scale(0.98);
}

.alert-level-bar {
  width: 6rpx;
  height: 44rpx;
  border-radius: 3rpx;
  flex-shrink: 0;
  box-shadow: 0 0 6rpx currentColor;
}

.alert-info { flex: 1; }
.alert-title { font-size: 26rpx; font-weight: 600; color: #1F2937; display: block; }
.alert-desc { font-size: 20rpx; color: #6B7280; display: block; margin-top: 4rpx; }

.alert-tag {
  font-size: 18rpx;
  padding: 4rpx 12rpx;
  border-radius: 6rpx;
  font-weight: 600;
  flex-shrink: 0;
}

/* ===== 最新动态 ===== */
.latest-section {
  background: #FFFFFF;
  border-radius: 16rpx;
  padding: 24rpx;
  margin-bottom: 24rpx;
  border: 1rpx solid #E5E7EB;
  box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.04);
  position: relative;
  overflow: hidden;
  animation: slideInUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) 0.4s both;
}

.latest-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  bottom: 0;
  width: 4rpx;
  background: linear-gradient(180deg, #8B5CF6, #06B6D4);
}

.knowledge-list {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

.knowledge-item {
  display: flex;
  align-items: center;
  gap: 16rpx;
  padding: 16rpx;
  background: linear-gradient(135deg, #F8FAFC 0%, #F0F9FF 100%);
  border-radius: 12rpx;
  border: 1rpx solid #E0F2FE;
  transition: all 0.2s ease;
}

.knowledge-item:active {
  transform: scale(0.98);
  background: #E0F2FE;
}

.kb-icon-wrap {
  width: 44rpx;
  height: 44rpx;
  border-radius: 10rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.kb-icon { font-size: 22rpx; }
.kb-info { flex: 1; }
.kb-title { font-size: 26rpx; font-weight: 600; color: #1F2937; display: block; }
.kb-desc { font-size: 20rpx; color: #6B7280; display: block; margin-top: 4rpx; }

.kb-status-tag {
  font-size: 18rpx;
  padding: 4rpx 12rpx;
  border-radius: 6rpx;
  font-weight: 600;
  flex-shrink: 0;
}

/* ===== 响应式设置 ===== */
@media screen and (max-width: 375px) {
  .home-container {
    padding: 0 16rpx 180rpx;
  }

  .banner-section {
    margin-top: 160rpx;
  }

  .banner-swiper {
    height: 280rpx;
  }

  .quick-icon-wrap {
    width: 80rpx;
    height: 80rpx;
  }

  .quick-icon-img {
    width: 52rpx;
    height: 52rpx;
  }

  .quick-name {
    font-size: 22rpx;
  }

  .overview-grid {
    gap: 8rpx;
  }

  .overview-card {
    padding: 16rpx 6rpx;
  }

  .stat-value {
    font-size: 32rpx;
  }
}

@media screen and (min-width: 415px) {
  .home-container {
    padding: 0 32rpx 200rpx;
  }

  .banner-section {
    margin-top: 200rpx;
  }

  .banner-swiper {
    height: 360rpx;
  }

  .quick-grid {
    gap: 20rpx;
  }

  .quick-icon-wrap {
    width: 104rpx;
    height: 104rpx;
  }

  .quick-icon-img {
    width: 72rpx;
    height: 72rpx;
  }

  .quick-name {
    font-size: 26rpx;
  }

  .overview-grid {
    gap: 16rpx;
  }
}

@media screen and (orientation: landscape) {
  .home-container {
    padding: 0 32rpx 120rpx;
  }

  .banner-section {
    margin-top: 120rpx;
  }

  .banner-swiper {
    height: 260rpx;
  }

  .quick-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media screen and (min-width: 768px) {
  .home-container {
    max-width: 750rpx;
    margin: 0 auto;
  }

  .quick-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}
</style>
