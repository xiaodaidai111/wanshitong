<template>
  <view class="home-container">
    <!-- 顶部导航栏 -->
    <view class="home-navbar">
      <view class="navbar-content">
        <view class="logo-circle">
          <text class="logo-text">WS</text>
        </view>
        <view class="title-block">
          <text class="main-title">设备检修智能工作台</text>
          <text class="sub-title">多模态检索 · 智能问修 · 标准作业 · 知识沉淀</text>
        </view>
      </view>
    </view>

    <scroll-view class="home-scroll" scroll-y :show-scrollbar="false">

      <!-- Banner区域 -->
      <view class="banner-section">
        <swiper class="banner-swiper" circular autoplay interval="5000" duration="600" indicator-dots indicator-active-color="#2563EB" indicator-color="rgba(255,255,255,0.4)">
          <swiper-item v-for="(banner, index) in banners" :key="index">
            <view class="banner-item">
              <image :src="banner.image" mode="aspectFill" class="banner-img"></image>
              <view class="banner-overlay">
                <text class="banner-title">{{ banner.title }}</text>
                <text class="banner-sub">{{ banner.sub }}</text>
              </view>
            </view>
          </swiper-item>
        </swiper>
      </view>

      <!-- 搜索区域 -->
      <view class="search-section">
        <view class="search-box">
          <text class="search-icon">🔍</text>
          <input class="search-input" placeholder="输入故障现象、设备型号或检修问题" placeholder-class="search-placeholder" />
          <view class="search-btn">
            <text class="search-btn-text">检索</text>
          </view>
        </view>
        <view class="quick-tags">
          <view class="tag-item" v-for="tag in quickTags" :key="tag">
            <text>{{ tag }}</text>
          </view>
        </view>
      </view>

      <!-- 统计卡片 -->
      <view class="stats-section">
        <view class="stat-card stat-blue">
          <view class="stat-top-bar blue-bar"></view>
          <view class="stat-content">
            <view class="stat-icon-circle blue-icon-bg">
              <text class="stat-icon">📋</text>
            </view>
            <text class="stat-num">8</text>
            <text class="stat-label blue-label">今日任务</text>
          </view>
        </view>
        <view class="stat-card stat-red">
          <view class="stat-top-bar red-bar"></view>
          <view class="stat-content">
            <view class="stat-icon-circle red-icon-bg">
              <text class="stat-icon">⚠️</text>
            </view>
            <text class="stat-num">3</text>
            <text class="stat-label red-label">高风险</text>
          </view>
        </view>
        <view class="stat-card stat-orange">
          <view class="stat-top-bar orange-bar"></view>
          <view class="stat-content">
            <view class="stat-icon-circle orange-icon-bg">
              <text class="stat-icon">📝</text>
            </view>
            <text class="stat-num">12</text>
            <text class="stat-label orange-label">待审核案例</text>
          </view>
        </view>
        <view class="stat-card stat-green">
          <view class="stat-top-bar green-bar"></view>
          <view class="stat-content">
            <view class="stat-icon-circle green-icon-bg">
              <text class="stat-icon">📚</text>
            </view>
            <text class="stat-num">156</text>
            <text class="stat-label green-label">知识资源</text>
          </view>
        </view>
      </view>

      <!-- 核心功能 -->
      <view class="func-section">
        <view class="section-header">
          <text class="section-title">核心功能</text>
        </view>
        <view class="func-grid">
          <view class="func-card func-blue" @click="handleFuncClick('ask')">
            <view class="func-icon-wrap">
              <text class="func-icon">🤖</text>
            </view>
            <view class="func-text">
              <text class="func-name">一键问修</text>
              <text class="func-desc">AI智能问答</text>
            </view>
          </view>
          <view class="func-card func-green" @click="handleFuncClick('search')">
            <view class="func-icon-wrap">
              <text class="func-icon">🔍</text>
            </view>
            <view class="func-text">
              <text class="func-name">多模态检索</text>
              <text class="func-desc">文本/图片/型号</text>
            </view>
          </view>
          <view class="func-card func-orange" @click="handleFuncClick('standard')">
            <view class="func-icon-wrap">
              <text class="func-icon">📋</text>
            </view>
            <view class="func-text">
              <text class="func-name">标准作业</text>
              <text class="func-desc">合规检修流程</text>
            </view>
          </view>
          <view class="func-card func-purple" @click="handleFuncClick('case')">
            <view class="func-icon-wrap">
              <text class="func-icon">📚</text>
            </view>
            <view class="func-text">
              <text class="func-name">案例入库</text>
              <text class="func-desc">经验沉淀分享</text>
            </view>
          </view>
        </view>
      </view>

      <!-- 今日检修任务 -->
      <view class="section-card">
        <view class="section-header">
          <view class="section-header-left">
            <text class="header-icon">📋</text>
            <text class="section-title">今日检修任务</text>
          </view>
          <text class="section-more" @click="goToTasks">查看全部 ›</text>
        </view>
        <view class="task-list">
          <view class="task-item" v-for="(task, idx) in todayTasks" :key="idx">
            <view class="task-col-line" :class="task.lineClass"></view>
            <view class="task-content">
              <text class="task-title">{{ task.title }}</text>
              <text class="task-sub">{{ task.sub }}</text>
            </view>
            <view class="task-status" :class="task.statusClass">
              <text>{{ task.status }}</text>
            </view>
          </view>
        </view>
      </view>

      <!-- 风险告警 -->
      <view class="section-card">
        <view class="section-header">
          <view class="section-header-left">
            <text class="header-icon">⚠️</text>
            <text class="section-title">风险告警</text>
          </view>
          <text class="section-more" @click="goToAlerts">查看全部 ›</text>
        </view>
        <view class="alert-list">
          <view class="alert-item" v-for="(alert, idx) in riskAlerts" :key="idx">
            <view class="alert-col-line" :class="alert.lineClass"></view>
            <view class="alert-content">
              <text class="alert-title">{{ alert.title }}</text>
              <text class="alert-sub">{{ alert.sub }}</text>
            </view>
            <view class="alert-status" :class="alert.statusClass">
              <text>{{ alert.status }}</text>
            </view>
          </view>
        </view>
      </view>

      <!-- 知识沉淀动态 -->
      <view class="section-card">
        <view class="section-header">
          <view class="section-header-left">
            <text class="header-icon">📚</text>
            <text class="section-title">知识沉淀动态</text>
          </view>
          <text class="section-more" @click="goToKnowledge">查看全部 ›</text>
        </view>
        <view class="knowledge-list">
          <view class="knowledge-item" v-for="(item, idx) in knowledgeList" :key="idx">
            <view class="knowledge-icon-wrap" :class="item.iconClass">
              <text class="knowledge-icon">{{ item.icon }}</text>
            </view>
            <view class="knowledge-content">
              <text class="knowledge-title">{{ item.title }}</text>
              <text class="knowledge-sub">{{ item.sub }}</text>
            </view>
            <view class="knowledge-status" :class="item.statusClass">
              <text>{{ item.status }}</text>
            </view>
          </view>
        </view>
      </view>

      <!-- 现场经验共创 -->
      <view class="collab-section">
        <view class="collab-card" @click="goToCollab">
          <view class="collab-icon">💡</view>
          <view class="collab-content">
            <text class="collab-title">现场经验共创</text>
            <text class="collab-desc">分享检修案例，沉淀实战经验</text>
          </view>
          <text class="collab-arrow">›</text>
        </view>
      </view>

      <view class="bottom-space"></view>

    </scroll-view>

    <!-- 右下角机器人按钮 -->
    <view class="fab-container" @click.stop="toggleRobotMenu">
      <view class="fab-btn">
        <text class="fab-icon">🤖</text>
      </view>
    </view>

    <!-- 机器人菜单 -->
    <view class="robot-menu" v-if="showRobotMenu" @click.stop="showRobotMenu = false">
      <view class="robot-menu-overlay"></view>
      <view class="robot-options" @click.stop>
        <view class="robot-option" @click.stop="handleRobotAction('image')">
          <view class="robot-icon-circle bg-blue">
            <text>📷</text>
          </view>
          <text class="robot-option-text">上传故障图片</text>
        </view>
        <view class="robot-option" @click.stop="handleRobotAction('case')">
          <view class="robot-icon-circle bg-green">
            <text>📝</text>
          </view>
          <text class="robot-option-text">提交维修案例</text>
        </view>
        <view class="robot-option" @click.stop="handleRobotAction('note')">
          <view class="robot-icon-circle bg-orange">
            <text>📓</text>
          </view>
          <text class="robot-option-text">新增检修笔记</text>
        </view>
      </view>
    </view>

  </view>
</template>

<script>
export default {
  data() {
    return {
      showRobotMenu: false,
      banners: [
        { image: '../../static/industrial-banner-1.png', title: '多模态设备检修知识检索', sub: '摩托车发动机 / 故障图片 / 设备型号精准匹配' },
        { image: '../../static/industrial-banner-2.png', title: '标准化检修作业指引', sub: '设备检修知识作业系统 · 点火系统 · 燃油供给 · 机油润滑 · 异响排查' },
        { image: '../../static/industrial-banner-3.png', title: '一线案例知识沉淀', sub: '案例上传 · 审核入库 · 图谱更新' }
      ],
      quickTags: ['异响', '过热', '漏油', '振动', '报警'],
      todayTasks: [
        { title: 'ZK-320变频器过热故障', sub: '变频器 · 紧急检修', status: '待处理', lineClass: 'blue-line', statusClass: 'status-red-bg' },
        { title: 'CG-125发动机异响排查', sub: '发动机总成 · 优先处理', status: '处理中', lineClass: 'orange-line', statusClass: 'status-orange-bg' },
        { title: '起重机启动困难检修', sub: '电气系统 · 标准检修', status: '待处理', lineClass: 'yellow-line', statusClass: 'status-yellow-bg' }
      ],
      riskAlerts: [
        { title: '润滑不足风险', sub: '机油液位偏低，建议优先补充', status: '严重', lineClass: 'red-line', statusClass: 'status-red' },
        { title: '温度异常预警', sub: '变频器温度超过安全阈值', status: '警告', lineClass: 'orange-line', statusClass: 'status-orange' },
        { title: '手册版本更新', sub: '新版本检修手册已入库', status: '提示', lineClass: 'yellow-line', statusClass: 'status-yellow' }
      ],
      knowledgeList: [
        { icon: '📄', title: '维修手册入库', sub: '变频器检修标准作业流程', status: '已更新', iconClass: 'knowledge-blue', statusClass: 'status-blue' },
        { icon: '🔗', title: '知识图谱扩展', sub: '新增异响故障关联节点', status: '已扩展', iconClass: 'knowledge-green', statusClass: 'status-green-bg' },
        { icon: '📝', title: '案例待审核', sub: '现场案例上传，待质量审核', status: '待审核', iconClass: 'knowledge-orange', statusClass: 'status-orange-bg' }
      ]
    }
  },
  methods: {
    toggleRobotMenu() {
      this.showRobotMenu = !this.showRobotMenu
    },
    handleRobotAction(action) {
      this.showRobotMenu = false
      const actions = { image: '上传故障图片', case: '提交维修案例', note: '新增检修笔记' }
      uni.showToast({ title: actions[action] || '操作', icon: 'none' })
    },
    handleFuncClick(type) {
      const urls = {
        ask: '/pages/cooking-expert/cooking-expert',
        search: '/pages/takeaway-expert/takeaway-expert',
        standard: '/pages/health-manager/health-manager',
        case: '/pages/restaurant-recommendation/restaurant-recommendation'
      }
      uni.navigateTo({ url: urls[type] })
    },
    goToTasks() {
      uni.navigateTo({ url: '/pages/health-manager/health-manager' })
    },
    goToAlerts() {
      uni.showToast({ title: '功能开发中', icon: 'none' })
    },
    goToKnowledge() {
      uni.navigateTo({ url: '/pages/restaurant-recommendation/restaurant-recommendation' })
    },
    goToCollab() {
      uni.navigateTo({ url: '/pages/restaurant-recommendation/restaurant-recommendation' })
    }
  }
}
</script>

<style scoped>
/* ===== 全局容器 ===== */
.home-container {
  min-height: 100vh;
  background: #F5F7FA;
  font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Helvetica Neue", Arial, sans-serif;
}

.home-scroll {
  min-height: 100vh;
}

/* ===== 导航栏 ===== */
.home-navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 112rpx;
  background: #FFFFFF;
  z-index: 500;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.04);
}

.navbar-content {
  display: flex;
  align-items: center;
  height: 100%;
  padding: 0 24rpx;
  gap: 16rpx;
}

.logo-circle {
  width: 72rpx;
  height: 72rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, #3B82F6 0%, #60A5FA 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.logo-text {
  font-size: 32rpx;
  font-weight: 700;
  color: #FFFFFF;
}

.title-block {
  display: flex;
  flex-direction: column;
  gap: 4rpx;
}

.main-title {
  font-size: 44rpx;
  font-weight: 700;
  color: #1F2937;
  line-height: 1.2;
}

.sub-title {
  font-size: 15rpx;
  color: #3B82F6;
  font-weight: 500;
  line-height: 1.2;
  opacity: 0.8;
}

/* ===== Banner区域 ===== */
.banner-section {
  padding-top: 168rpx;
  padding-left: 24rpx;
  padding-right: 24rpx;
  padding-bottom: 20rpx;
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
}

.banner-overlay {
  position: absolute;
  bottom: 0; left: 0; right: 0;
  padding: 60rpx 32rpx 24rpx;
  background: linear-gradient(to top, rgba(0,0,0,0.7) 0%, transparent 100%);
}

.banner-title {
  color: #fff;
  font-size: 32rpx;
  font-weight: 700;
  display: block;
  margin-bottom: 8rpx;
}

.banner-sub {
  color: rgba(255,255,255,0.9);
  font-size: 22rpx;
  font-weight: 500;
}

/* ===== 搜索区域 ===== */
.search-section {
  padding: 0 24rpx 20rpx;
}

.search-box {
  display: flex;
  align-items: center;
  background: #FFFFFF;
  border-radius: 16rpx;
  padding: 20rpx 24rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.04);
  border: 1rpx solid #EEF0F4;
  margin-bottom: 16rpx;
}

.search-icon {
  font-size: 28rpx;
  margin-right: 12rpx;
}

.search-input {
  flex: 1;
  font-size: 26rpx;
  color: #1F2937;
}

.search-placeholder {
  color: #9CA3AF;
}

.search-btn {
  background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
  padding: 14rpx 28rpx;
  border-radius: 12rpx;
}

.search-btn-text {
  font-size: 26rpx;
  color: #FFFFFF;
  font-weight: 600;
}

.quick-tags {
  display: flex;
  gap: 12rpx;
}

.tag-item {
  padding: 10rpx 20rpx;
  background: rgba(59, 130, 246, 0.1);
  border-radius: 20rpx;
}

.tag-item text {
  font-size: 24rpx;
  color: #2563EB;
  font-weight: 500;
}

/* ===== 统计卡片 ===== */
.stats-section {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16rpx;
  padding: 0 24rpx 20rpx;
}

.stat-card {
  background: #FFFFFF;
  border-radius: 16rpx;
  overflow: hidden;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.04);
}

.stat-top-bar {
  height: 6rpx;
}

.blue-bar { background: linear-gradient(90deg, #3B82F6, #60A5FA); }
.red-bar { background: linear-gradient(90deg, #EF4444, #F87171); }
.orange-bar { background: linear-gradient(90deg, #F59E0B, #FBBF24); }
.green-bar { background: linear-gradient(90deg, #10B981, #34D399); }

.stat-content {
  padding: 24rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-icon-circle {
  width: 64rpx;
  height: 64rpx;
  border-radius: 16rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 12rpx;
}

.blue-icon-bg { background: rgba(59, 130, 246, 0.12); }
.red-icon-bg { background: rgba(239, 68, 68, 0.12); }
.orange-icon-bg { background: rgba(245, 158, 11, 0.12); }
.green-icon-bg { background: rgba(16, 185, 129, 0.12); }

.stat-icon {
  font-size: 28rpx;
}

.stat-num {
  font-size: 48rpx;
  font-weight: 700;
  color: #1F2937;
  line-height: 1;
}

.stat-label {
  font-size: 22rpx;
  font-weight: 600;
  margin-top: 4rpx;
}

.blue-label { color: #2563EB; }
.red-label { color: #DC2626; }
.orange-label { color: #D97706; }
.green-label { color: #059669; }

/* ===== 核心功能 ===== */
.func-section {
  padding: 20rpx 24rpx;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
}

.section-header-left {
  display: flex;
  align-items: center;
  gap: 8rpx;
}

.header-icon {
  font-size: 28rpx;
}

.section-title {
  font-size: 28rpx;
  font-weight: 700;
  color: #1F2937;
}

.section-more {
  font-size: 24rpx;
  color: #6B7280;
  font-weight: 500;
}

.func-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16rpx;
}

.func-card {
  background: #FFFFFF;
  border-radius: 16rpx;
  padding: 24rpx;
  display: flex;
  align-items: center;
  gap: 16rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.04);
}

.func-icon-wrap {
  width: 80rpx;
  height: 80rpx;
  border-radius: 20rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.func-blue .func-icon-wrap { background: linear-gradient(135deg, rgba(59, 130, 246, 0.15), rgba(59, 130, 246, 0.08)); }
.func-green .func-icon-wrap { background: linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(16, 185, 129, 0.08)); }
.func-orange .func-icon-wrap { background: linear-gradient(135deg, rgba(245, 158, 11, 0.15), rgba(245, 158, 11, 0.08)); }
.func-purple .func-icon-wrap { background: linear-gradient(135deg, rgba(139, 92, 246, 0.15), rgba(139, 92, 246, 0.08)); }

.func-icon {
  font-size: 36rpx;
}

.func-text {
  flex: 1;
}

.func-name {
  font-size: 26rpx;
  font-weight: 700;
  color: #1F2937;
  display: block;
}

.func-desc {
  font-size: 22rpx;
  color: #6B7280;
  display: block;
  margin-top: 4rpx;
}

/* ===== 通用卡片样式 ===== */
.section-card {
  background: #FFFFFF;
  border-radius: 16rpx;
  padding: 24rpx;
  margin: 0 24rpx 20rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.04);
}

/* ===== 今日检修任务 ===== */
.task-list {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.task-item {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.task-col-line {
  width: 6rpx;
  height: 48rpx;
  border-radius: 3rpx;
}

.blue-line { background: #3B82F6; }
.orange-line { background: #F59E0B; }
.yellow-line { background: #D97706; }

.task-content {
  flex: 1;
}

.task-title {
  font-size: 26rpx;
  font-weight: 600;
  color: #1F2937;
  display: block;
}

.task-sub {
  font-size: 22rpx;
  color: #6B7280;
  display: block;
  margin-top: 4rpx;
}

.task-status {
  padding: 8rpx 16rpx;
  border-radius: 10rpx;
}

.status-red-bg { background: rgba(239, 68, 68, 0.12); }
.status-red-bg text { color: #DC2626; }

.status-orange-bg { background: rgba(245, 158, 11, 0.12); }
.status-orange-bg text { color: #D97706; }

.status-yellow-bg { background: rgba(234, 179, 8, 0.12); }
.status-yellow-bg text { color: #CA8A04; }

.task-status text {
  font-size: 22rpx;
  font-weight: 600;
}

/* ===== 风险告警 ===== */
.alert-list {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.alert-item {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.alert-col-line {
  width: 6rpx;
  height: 48rpx;
  border-radius: 3rpx;
}

.red-line { background: #EF4444; }

.alert-content {
  flex: 1;
}

.alert-title {
  font-size: 26rpx;
  font-weight: 600;
  color: #1F2937;
  display: block;
}

.alert-sub {
  font-size: 22rpx;
  color: #6B7280;
  display: block;
  margin-top: 4rpx;
}

.alert-status {
  padding: 8rpx 16rpx;
  border-radius: 10rpx;
}

.status-red { background: rgba(239, 68, 68, 0.12); }
.status-red text { color: #DC2626; }

.status-orange { background: rgba(245, 158, 11, 0.12); }
.status-orange text { color: #D97706; }

.status-yellow { background: rgba(234, 179, 8, 0.12); }
.status-yellow text { color: #CA8A04; }

.alert-status text {
  font-size: 22rpx;
  font-weight: 600;
}

/* ===== 知识沉淀动态 ===== */
.knowledge-list {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.knowledge-item {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.knowledge-icon-wrap {
  width: 56rpx;
  height: 56rpx;
  border-radius: 12rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.knowledge-blue { background: rgba(59, 130, 246, 0.12); }
.knowledge-green { background: rgba(16, 185, 129, 0.12); }
.knowledge-orange { background: rgba(245, 158, 11, 0.12); }

.knowledge-icon {
  font-size: 24rpx;
}

.knowledge-content {
  flex: 1;
}

.knowledge-title {
  font-size: 26rpx;
  font-weight: 600;
  color: #1F2937;
  display: block;
}

.knowledge-sub {
  font-size: 22rpx;
  color: #6B7280;
  display: block;
  margin-top: 4rpx;
}

.knowledge-status {
  padding: 8rpx 16rpx;
  border-radius: 10rpx;
}

.status-blue { background: rgba(59, 130, 246, 0.12); }
.status-blue text { color: #2563EB; }

.status-green-bg { background: rgba(16, 185, 129, 0.12); }
.status-green-bg text { color: #059669; }

.knowledge-status text {
  font-size: 22rpx;
  font-weight: 600;
}

/* ===== 现场经验共创 ===== */
.collab-section {
  padding: 0 24rpx 20rpx;
}

.collab-card {
  background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%);
  border-radius: 16rpx;
  padding: 24rpx;
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.collab-icon {
  font-size: 40rpx;
}

.collab-content {
  flex: 1;
}

.collab-title {
  font-size: 28rpx;
  font-weight: 700;
  color: #92400E;
  display: block;
}

.collab-desc {
  font-size: 22rpx;
  color: #B45309;
  display: block;
  margin-top: 4rpx;
}

.collab-arrow {
  font-size: 40rpx;
  color: #92400E;
}

/* ===== 底部留白 ===== */
.bottom-space {
  height: 180rpx;
}

/* ===== 右下角机器人按钮 ===== */
.fab-container {
  position: fixed;
  right: 32rpx;
  bottom: 160rpx;
  z-index: 500;
}

.fab-btn {
  width: 100rpx;
  height: 100rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8rpx 24rpx rgba(59, 130, 246, 0.4);
}

.fab-icon {
  font-size: 48rpx;
}

/* ===== 机器人菜单 ===== */
.robot-menu {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 999;
  display: flex;
  justify-content: flex-end;
  align-items: flex-end;
  padding: 0 32rpx 260rpx 0;
}

.robot-menu-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.35);
}

.robot-options {
  position: relative;
  background: #FFFFFF;
  border-radius: 16rpx;
  padding: 12rpx;
  box-shadow: 0 12rpx 40rpx rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  gap: 8rpx;
  min-width: 300rpx;
}

.robot-option {
  display: flex;
  align-items: center;
  gap: 16rpx;
  padding: 16rpx 20rpx;
  background: #F5F7FA;
  border-radius: 12rpx;
}

.robot-icon-circle {
  width: 48rpx;
  height: 48rpx;
  border-radius: 12rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.bg-blue { background: rgba(59, 130, 246, 0.15); }
.bg-green { background: rgba(16, 185, 129, 0.15); }
.bg-orange { background: rgba(245, 158, 11, 0.15); }

.robot-option-text {
  font-size: 26rpx;
  color: #374151;
  font-weight: 600;
}
</style>
