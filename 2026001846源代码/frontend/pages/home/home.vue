<template>
  <view class="home-container">
    <SkeletonScreen v-if="pageLoading" :loading="true" />

    <view class="home-navbar" :style="{ paddingTop: statusBarHeight + 'px' }">
      <view class="home-navbar-content">
        <view class="brand">
          <image src="../../static/icon-home.png" class="brand-icon" mode="aspectFit" />
          <text class="brand-name">{{ brandTitle }}</text>
        </view>
      </view>
    </view>

    <view class="hero-card">
      <swiper class="banner-swiper" circular autoplay interval="5000" duration="600" indicator-dots indicator-active-color="#2563EB" indicator-color="rgba(255,255,255,0.48)">
        <swiper-item v-for="(banner, index) in banners" :key="index">
          <view class="banner-item" @tap="onBannerClick(banner)">
            <image :src="banner.image" mode="aspectFill" class="banner-img" />
            <view class="banner-shade"></view>
            <view class="banner-content">
              <text class="banner-kicker">{{ banner.kicker }}</text>
              <text class="banner-title">{{ banner.title }}</text>
              <text class="banner-sub">{{ banner.sub }}</text>
            </view>
          </view>
        </swiper-item>
      </swiper>
    </view>

    <view class="quick-grid">
      <view class="quick-item" @click="navigateTo('/pages/takeaway-expert/takeaway-expert')">
        <view class="quick-icon-wrap blue">
          <image src="../../static/assistant-search.png" class="quick-icon-img" mode="aspectFit" />
        </view>
        <text class="quick-name">智能检索</text>
        <text class="quick-desc">图文查故障</text>
      </view>
      <view class="quick-item" @click="navigateTo('/pages/health-manager/health-manager')">
        <view class="quick-icon-wrap green">
          <image src="../../static/assistant-maintenance.png" class="quick-icon-img" mode="aspectFit" />
        </view>
        <text class="quick-name">检修任务</text>
        <text class="quick-desc">进度可追踪</text>
      </view>
      <view class="quick-item" @click="navigateTo('/pages/restaurant-recommendation/restaurant-recommendation')">
        <view class="quick-icon-wrap amber">
          <image src="../../static/assistant-knowledge.png" class="quick-icon-img" mode="aspectFit" />
        </view>
        <text class="quick-name">知识库</text>
        <text class="quick-desc">经验可沉淀</text>
      </view>
    </view>

    <view class="panel">
      <view class="section-header">
        <text class="section-title">系统概览</text>
        <text class="section-link" @click="goToDashboard">详情</text>
      </view>
      <view class="overview-grid">
        <view class="overview-card" v-for="(stat, idx) in systemStats" :key="idx">
          <view class="stat-top">
            <text class="stat-dot" :style="{ background: stat.dotColor }"></text>
            <text class="stat-label">{{ stat.label }}</text>
          </view>
          <text class="stat-value">{{ stat.value }}</text>
        </view>
      </view>
    </view>

    <view class="panel">
      <view class="section-header">
        <view>
          <text class="section-title">今日任务</text>
          <text class="section-subtitle">{{ pendingTaskCount }} 项待处理</text>
        </view>
        <text class="section-link" @click="navigateTo('/pages/health-manager/health-manager')">全部</text>
      </view>
      <view class="task-list">
        <view class="task-item" v-for="(task, idx) in todayTasks.slice(0, 3)" :key="idx" @click="toggleTask(task)">
          <view class="task-check" :class="{ checked: task.done }">
            <text v-if="task.done">✓</text>
          </view>
          <view class="task-info">
            <text class="task-name" :class="{ done: task.done }">{{ task.name }}</text>
            <text class="task-meta">{{ task.device }} · {{ task.level }}</text>
          </view>
          <view class="status-tag" :style="{ background: task.statusBg, color: task.statusColor }">{{ task.status }}</view>
        </view>
      </view>
    </view>

    <view class="panel alert-panel" v-if="riskAlerts.length > 0">
      <view class="section-header">
        <view>
          <text class="section-title">风险告警</text>
          <text class="section-subtitle">{{ riskAlerts.length }} 项需要关注</text>
        </view>
      </view>
      <view class="alert-list">
        <view class="alert-item" v-for="(alert, idx) in riskAlerts.slice(0, 2)" :key="idx">
          <view class="alert-bar" :style="{ background: alert.levelColor }"></view>
          <view class="alert-info">
            <text class="alert-title">{{ alert.title }}</text>
            <text class="alert-desc">{{ alert.desc }}</text>
          </view>
          <view class="alert-tag" :style="{ background: alert.tagBg, color: alert.tagColor }">{{ alert.level }}</view>
        </view>
      </view>
    </view>

    <view class="panel">
      <view class="section-header">
        <text class="section-title">最新动态</text>
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
          <view class="kb-status-tag" :style="{ background: item.statusBg, color: item.statusColor }">{{ item.status }}</view>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import request from '../../utils/request.js'
import SkeletonScreen from '../../src/components/SkeletonScreen.vue'

export default {
  components: { SkeletonScreen },
  data() {
    return {
      statusBarHeight: 0,
      pageLoading: true,
      brandTitle: '一修',
      banners: [
        {
          image: '../../static/industrial-banner-1.png',
          kicker: '多模态检索',
          title: '设备故障快速定位',
          sub: '图片、型号、现象联合匹配检修知识',
          url: ''
        },
        {
          image: '../../static/industrial-banner-2.png',
          kicker: '标准化作业',
          title: '检修流程随手可查',
          sub: '点火、燃油、润滑、异响排查一屏掌握',
          url: ''
        },
        {
          image: '../../static/industrial-banner-3.png',
          kicker: '案例沉淀',
          title: '一线经验持续入库',
          sub: '现场案例上传、审核、复用形成闭环',
          url: ''
        }
      ],
      systemStats: [
        { label: '在线设备', value: '128', dotColor: '#16A34A' },
        { label: '待处理告警', value: '5', dotColor: '#EA580C' },
        { label: '待审核案例', value: '12', dotColor: '#D97706' },
        { label: '今日任务', value: '8', dotColor: '#2563EB' }
      ],
      todayTasks: [
        { name: '发动机基础检修', device: '发动机总成', level: '二级检修', status: '进行中', statusBg: '#EFF6FF', statusColor: '#2563EB', done: false },
        { name: '点火系统检查', device: '火花塞/点火线圈', level: '一级检修', status: '待处理', statusBg: '#FFF7ED', statusColor: '#EA580C', done: false },
        { name: '燃油供给检查', device: '油路/化油器', level: '巡检', status: '待处理', statusBg: '#FFFBEB', statusColor: '#D97706', done: false },
        { name: '发动机异响排查', device: '气门/链条/轴承', level: '故障抢修', status: '未开始', statusBg: '#F3F4F6', statusColor: '#6B7280', done: false }
      ],
      riskAlerts: [
        { title: '润滑不足风险', desc: '机油液位偏低，建议优先补充并检查渗漏点', level: '严重', levelColor: '#DC2626', tagBg: '#FEF2F2', tagColor: '#DC2626' },
        { title: '点火系统复核', desc: '火花塞间隙超标，需要复核点火时序', level: '警告', levelColor: '#EA580C', tagBg: '#FFF7ED', tagColor: '#EA580C' },
        { title: '手册版本校验', desc: '维修手册已入库，建议核对适用范围', level: '提示', levelColor: '#D97706', tagBg: '#FFFBEB', tagColor: '#D97706' }
      ],
      knowledgeUpdates: [
        { icon: '文', title: '发动机维修手册已入库', desc: '覆盖结构、故障排查、标准作业流程', status: '已入库', iconBg: '#F0FDF4', statusBg: '#F0FDF4', statusColor: '#16A34A' },
        { icon: '链', title: '新增异响知识节点', desc: '关联气门间隙、链条磨损、轴承磨损排查路径', status: '已更新', iconBg: '#EFF6FF', statusBg: '#EFF6FF', statusColor: '#2563EB' },
        { icon: '审', title: '现场案例待审核', desc: '一线人员上传启动困难处置案例', status: '待审核', iconBg: '#FFFBEB', statusBg: '#FFFBEB', statusColor: '#D97706' }
      ]
    }
  },
  computed: {
    pendingTaskCount() {
      return this.todayTasks.filter(task => !task.done).length
    }
  },
  onLoad() {
    const systemInfo = uni.getSystemInfoSync()
    this.statusBarHeight = systemInfo.statusBarHeight || 0
    this.fetchOverviewData()
    setTimeout(() => { this.pageLoading = false }, 400)
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
            { label: '在线设备', value: String(data.online_equipment || 0), dotColor: '#16A34A' },
            { label: '待处理告警', value: String(data.pending_alerts || 0), dotColor: '#EA580C' },
            { label: '待审核案例', value: String(data.pending_reviews || 0), dotColor: '#D97706' },
            { label: '今日任务', value: String(data.today_tasks || 0), dotColor: '#2563EB' }
          ]
        }
      } catch (_error) {
        // 保留本地演示数据，避免接口不可用时首页空白。
      }
    }
  }
}
</script>

<style scoped>
.home-container {
  min-height: 100vh;
  padding: 0 24rpx 176rpx;
  background: #EEF3F8;
  box-sizing: border-box;
}

.home-navbar {
  position: sticky;
  top: 0;
  z-index: 50;
  margin: 0 -24rpx;
  background: rgba(248, 250, 252, 0.92);
  border-bottom: 1rpx solid rgba(203, 213, 225, 0.68);
  backdrop-filter: blur(18rpx);
  -webkit-backdrop-filter: blur(18rpx);
}

.home-navbar-content {
  height: 96rpx;
  padding: 0 24rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.brand {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.brand-icon {
  width: 64rpx;
  height: 64rpx;
  border-radius: 18rpx;
}

.brand-name,
.banner-kicker,
.banner-title,
.banner-sub,
.quick-name,
.quick-desc,
.section-title,
.section-subtitle,
.section-link,
.stat-label,
.stat-value,
.task-name,
.task-meta,
.status-tag,
.alert-title,
.alert-desc,
.alert-tag,
.kb-title,
.kb-desc,
.kb-status-tag {
  display: block;
}

.brand-name {
  color: #0F172A;
  font-size: 36rpx;
  font-weight: 800;
  line-height: 1.1;
}

.hero-card {
  margin-top: 24rpx;
  border-radius: 28rpx;
  overflow: hidden;
  box-shadow: 0 18rpx 42rpx rgba(15, 23, 42, 0.12);
}

.banner-swiper {
  height: 340rpx;
}

.banner-item {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.banner-img,
.banner-shade {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
}

.banner-shade {
  background: linear-gradient(180deg, rgba(15, 23, 42, 0.08) 0%, rgba(15, 23, 42, 0.76) 100%);
}

.banner-content {
  position: absolute;
  left: 28rpx;
  right: 28rpx;
  bottom: 34rpx;
}

.banner-kicker {
  width: fit-content;
  margin-bottom: 14rpx;
  padding: 8rpx 16rpx;
  border-radius: 999rpx;
  background: rgba(255, 255, 255, 0.2);
  color: #FFFFFF;
  font-size: 21rpx;
  font-weight: 700;
}

.banner-title {
  color: #FFFFFF;
  font-size: 38rpx;
  font-weight: 800;
  line-height: 1.18;
}

.banner-sub {
  margin-top: 10rpx;
  color: rgba(255, 255, 255, 0.88);
  font-size: 23rpx;
  line-height: 1.45;
}

.quick-grid {
  margin-top: 24rpx;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16rpx;
}

.quick-item {
  min-width: 0;
  padding: 22rpx 12rpx 20rpx;
  border-radius: 22rpx;
  background: #FFFFFF;
  border: 1rpx solid rgba(203, 213, 225, 0.72);
  box-shadow: 0 8rpx 20rpx rgba(15, 23, 42, 0.05);
  display: flex;
  flex-direction: column;
  align-items: center;
}

.quick-item:active,
.task-item:active,
.knowledge-item:active {
  transform: scale(0.98);
}

.quick-icon-wrap {
  width: 78rpx;
  height: 78rpx;
  border-radius: 22rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.quick-icon-wrap.blue { background: #E0F2FE; }
.quick-icon-wrap.green { background: #DCFCE7; }
.quick-icon-wrap.amber { background: #FEF3C7; }

.quick-icon-img {
  width: 52rpx;
  height: 52rpx;
}

.quick-name {
  margin-top: 14rpx;
  color: #0F172A;
  font-size: 24rpx;
  font-weight: 800;
  text-align: center;
}

.quick-desc {
  margin-top: 6rpx;
  color: #64748B;
  font-size: 19rpx;
  text-align: center;
}

.panel {
  margin-top: 24rpx;
  padding: 24rpx;
  border-radius: 26rpx;
  background: #FFFFFF;
  border: 1rpx solid rgba(203, 213, 225, 0.72);
  box-shadow: 0 10rpx 24rpx rgba(15, 23, 42, 0.05);
}

.section-header {
  margin-bottom: 20rpx;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16rpx;
}

.section-title {
  color: #0F172A;
  font-size: 30rpx;
  font-weight: 800;
  line-height: 1.2;
}

.section-subtitle {
  margin-top: 6rpx;
  color: #64748B;
  font-size: 21rpx;
}

.section-link {
  flex-shrink: 0;
  padding: 8rpx 16rpx;
  border-radius: 999rpx;
  background: #F1F5F9;
  color: #2563EB;
  font-size: 22rpx;
  font-weight: 700;
}

.overview-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14rpx;
}

.overview-card {
  min-height: 128rpx;
  padding: 18rpx;
  border-radius: 20rpx;
  background: #F8FAFC;
  border: 1rpx solid #E2E8F0;
}

.stat-top {
  display: flex;
  align-items: center;
  gap: 8rpx;
}

.stat-dot {
  width: 12rpx;
  height: 12rpx;
  border-radius: 50%;
  flex-shrink: 0;
}

.stat-label {
  color: #64748B;
  font-size: 21rpx;
  font-weight: 700;
}

.stat-value {
  margin-top: 18rpx;
  color: #0F172A;
  font-size: 42rpx;
  font-weight: 900;
  line-height: 1;
  font-variant-numeric: tabular-nums;
}

.task-list,
.alert-list,
.knowledge-list {
  display: flex;
  flex-direction: column;
  gap: 14rpx;
}

.task-item,
.alert-item,
.knowledge-item {
  display: flex;
  align-items: center;
  gap: 14rpx;
  padding: 18rpx;
  border-radius: 20rpx;
  background: #F8FAFC;
  border: 1rpx solid #E2E8F0;
}

.task-check {
  width: 38rpx;
  height: 38rpx;
  border-radius: 12rpx;
  border: 2rpx solid #CBD5E1;
  color: #FFFFFF;
  background: #FFFFFF;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-size: 22rpx;
  font-weight: 900;
}

.task-check.checked {
  border-color: #16A34A;
  background: #16A34A;
}

.task-info,
.alert-info,
.kb-info {
  flex: 1;
  min-width: 0;
}

.task-name,
.alert-title,
.kb-title {
  color: #0F172A;
  font-size: 25rpx;
  font-weight: 800;
  line-height: 1.35;
}

.task-name.done {
  color: #94A3B8;
  text-decoration: line-through;
}

.task-meta,
.alert-desc,
.kb-desc {
  margin-top: 6rpx;
  color: #64748B;
  font-size: 20rpx;
  line-height: 1.35;
}

.status-tag,
.alert-tag,
.kb-status-tag {
  flex-shrink: 0;
  padding: 6rpx 12rpx;
  border-radius: 999rpx;
  font-size: 18rpx;
  font-weight: 800;
}

.alert-panel {
  border-color: #FED7AA;
}

.alert-bar {
  width: 7rpx;
  height: 54rpx;
  border-radius: 999rpx;
  flex-shrink: 0;
}

.kb-icon-wrap {
  width: 48rpx;
  height: 48rpx;
  border-radius: 14rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.kb-icon {
  color: #0F172A;
  font-size: 20rpx;
  font-weight: 900;
}

@media screen and (min-width: 768px) {
  .home-container {
    max-width: 430px;
    margin: 0 auto;
    min-height: 100vh;
  }

  .home-navbar {
    left: 50%;
    right: auto;
    width: 430px;
    margin-left: -215px;
  }
}

@media screen and (max-width: 360px) {
  .home-container {
    padding-left: 18rpx;
    padding-right: 18rpx;
  }

  .banner-swiper {
    height: 310rpx;
  }

  .quick-grid {
    gap: 12rpx;
  }

  .quick-desc {
    display: none;
  }
}
</style>
