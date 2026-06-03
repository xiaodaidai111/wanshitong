<template>
  <view class="personal-center-container">
    <view class="page-header">
      <view class="page-title">个人中心</view>
      <text class="page-subtitle">欢迎使用智学多智能体！</text>
    </view>

    <view class="main-content">
      <view class="content-wrapper">
        <view class="user-profile-card">
          <view class="profile-header-bg"></view>
          <view class="profile-body">
            <view class="user-profile-header">
              <view class="avatar-wrapper">
                <image :src="avatarSource" class="avatar" mode="aspectFill"></image>
                <view v-if="isLoggedIn" class="avatar-edit-btn" @click="handleEditProfile">编辑</view>
              </view>

              <view class="user-info-content">
                <view class="user-name-line">
                  <text class="user-name">{{ displayName }}</text>
                  <view v-if="isLoggedIn" class="user-badge">
                    <text>{{ levelText }}</text>
                  </view>
                  <view v-else-if="isGuest" class="guest-badge">
                    <text>游客</text>
                  </view>
                </view>

                <view class="user-action-area">
                  <view v-if="!isLoggedIn" class="auth-box" @click="handleLogin">
                    <text class="auth-text">立即登录</text>
                    <text class="auth-arrow">></text>
                  </view>
                  <text v-else class="user-id">用户 ID：{{ userInfo.id || '--' }}</text>
                </view>

                <text v-if="isLoggedIn && userInfo.bio" class="user-bio">{{ userInfo.bio }}</text>
                <text v-else-if="isGuest" class="user-bio">游客模式下可先体验功能，登录后会保存你的专属数据！</text>
           <text v-else class="user-bio">登录后可同步个人资料、学习记录和收藏资源！</text>
              </view>
            </view>

            <view class="user-stats-bar">
              <view class="stat-item">
                <text class="stat-value">{{ userStats.totalAnalysis }}</text>
                <text class="stat-label">分析次数</text>
              </view>
              <view class="stat-divider"></view>
              <view class="stat-item">
                <text class="stat-value">{{ isLoggedIn ? userStats.healthScore : '--' }}</text>
                <text class="stat-label">掌握评分</text>
              </view>
              <view class="stat-divider"></view>
              <view class="stat-item">
                <text class="stat-value">{{ isLoggedIn ? userStats.completedGoals : '--' }}</text>
                <text class="stat-label">本周打卡</text>
              </view>
            </view>
          </view>

          <view class="indicators-grid">
            <view v-for="item in indicatorList" :key="item.label" class="indicator-box">
              <text class="indicator-label">{{ item.label }}</text>
              <text class="indicator-value">{{ item.value }}</text>
            </view>
          </view>
        </view>

        <view class="glass-card panorama-card">
          <view class="card-header">
            <view class="card-title-box">
              <text class="card-title">学习数据全景</text>
            </view>
            <view v-if="isLoggedIn" class="trend-tag" :class="panorama.trend >= 0 ? 'up' : 'down'">
              <text>{{ panorama.trend >= 0 ? '较上周+' : '较上周' }}{{ Math.abs(panorama.trend) }}%</text>
            </view>
          </view>

          <!-- 游客模式：显示登录提示占位信息-->
          <view v-if="!isLoggedIn" class="panorama-guest-placeholder">
            <view class="placeholder-icon">🔒</view>
            <text class="placeholder-title">登录后查看学习数据</text>
            <text class="placeholder-desc">登录后可查看你的个性化掌握评分、资源使用分析和学习趋势</text>
            <view class="placeholder-login-btn" @click="handleLogin">
              <text>立即登录</text>
            </view>
          </view>

          <!-- 登录后：显示个性化健康数据 -->
          <view v-else>
            <view class="panorama-score-hero">
              <view class="score-summary">
                <text class="score-number-inline">{{ panoramaScore }}</text>
                <text class="score-unit-inline">分</text>
                <text class="score-level-text" :class="scoreLevelClass">{{ scoreLevelText }}</text>
                <text class="score-desc">综合学习画像与掌握表现评分</text>
              </view>
            </view>

            <view class="dimension-bars">
              <view v-for="dim in dimensionList" :key="dim.key" class="dim-bar-item">
                <view class="dim-bar-header">
                  <text class="dim-bar-label">{{ dim.label }}</text>
                  <text class="dim-bar-value" :style="{ color: dim.color }">{{ dim.value }}%</text>
                </view>
                <view class="dim-bar-track">
                  <view class="dim-bar-fill" :style="{ width: dim.value + '%', background: dim.gradient }"></view>
                </view>
              </view>
            </view>
          </view>
        </view>

        <view class="glass-card diet-card">
          <view class="card-header">
            <view class="card-title-box">
              <text class="card-title">当前学习计划</text>
            </view>
          </view>

          <!-- 游客模式：显示登录提示-->
          <view v-if="!isLoggedIn" class="panorama-guest-placeholder" style="padding: 40rpx 0;">
            <view class="placeholder-icon">🔒</view>
            <text class="placeholder-title">登录后查看学习计划</text>
            <text class="placeholder-desc">登录后可制定个性化学习计划，追踪每日完成情况</text>
            <view class="placeholder-login-btn" @click="handleLogin">
              <text>立即登录</text>
            </view>
          </view>

          <!-- 登录后：显示饮食计划数据 -->
          <view v-else>
            <view class="diet-content">
              <view class="plan-info-box">
                <text class="plan-title">{{ dietPlan.name || 'AI导论基础巩固计划' }}</text>
                <text class="plan-subtitle">最近 7 天已记录 <text class="days">{{ dietPlan.daysCompleted || 0 }}</text> 天</text>
              </view>
            </view>

            <view class="completion-section">
              <view class="completion-header">
                <text class="completion-label">计划完成度</text>
                <text class="completion-percentage">{{ completionRate }}%</text>
              </view>
              <view class="completion-progress-bar">
                <view class="completion-progress-fill" :style="{ width: completionRate + '%' }"></view>
              </view>
              <view class="completion-stats">
                <text class="completion-stats-text">已完成{{ dietPlan.daysCompleted || 0 }}/7 天</text>
                <text class="completion-encourage">{{ completionEncourage }}</text>
              </view>
            </view>
          </view>
        </view>

        <view class="glass-card achievements-card">
          <view class="card-header">
            <view class="card-title-box">
              <text class="card-title">勋章成就</text>
            </view>
            <text class="view-more" @click="handleViewAllAchievements">查看全部 ></text>
          </view>
          <view class="achievements-grid">
            <view
              v-for="achievement in achievementsPreview"
              :key="achievement.id || achievement.name"
              class="medal-item"
              :class="{ unlocked: achievement.unlocked }"
              @click="handleAchievementClick(achievement)"
            >
              <view class="medal-icon-wrap">
                <text class="medal-icon">{{ achievement.icon || '🏅' }}</text>
              </view>
              <text class="medal-name">{{ achievement.name }}</text>
              <view class="medal-status-dot" :class="{ active: achievement.unlocked }"></view>
            </view>
          </view>
        </view>

        <view class="glass-card services-card">
          <view class="card-header">
            <view class="card-title-box">
              <text class="card-title">数据与服务</text>
            </view>
          </view>
          <view class="service-list">
            <view class="service-list-item" @click="handleOpenMyData">
              <view>
                <text class="service-list-label">我的数据</text>
                <text class="service-list-desc">学习记录、分析历史、收藏与浏览记录</text>
              </view>
              <text class="service-list-arrow">></text>
            </view>
            <view class="service-list-item" @click="handleEditProfile">
              <view>
                <text class="service-list-label">个人资料</text>
                <text class="service-list-desc">昵称、头像、年龄、身高、体重与简介</text>
              </view>
              <text class="service-list-arrow">></text>
            </view>
          </view>
        </view>

        <view v-if="isLoggedIn || isGuest" class="footer-actions">
          <button class="sign-out-btn" @click="handleLogout">{{ isGuest ? '退出游客模式' : '退出当前账号' }}</button>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import request, { getAssetURL } from '../../utils/request.js'
import cache from '../../utils/cache.js'
import guestManager from '../../utils/guest.js'

const DEFAULT_ACHIEVEMENTS = [
  { id: 1, name: '初次记录', icon: '🌱', description: '完成第一次学习记录', unlocked: false },
  { id: 2, name: '一周坚持', icon: '🔥', description: '连续记录 7 天', unlocked: false },
  { id: 3, name: '题库达人', icon: '💪', description: '累计完成 30 次练习记录', unlocked: false },
  { id: 4, name: '路径稳定', icon: '🥗', description: '连续 7 天学习达标', unlocked: false }
]

export default {
  data() {
    return {
      loading: false, // 始终为false，不显示加载动画
      dashboardRequestPromise: null,
      isLoggedIn: false,
      isGuest: false,
      eventHandlers: {
        authLogin: null,
        profileUpdated: null,
        dietPlanUpdated: null
      },
      userInfo: {
        id: '',
        name: '',
        avatar: '',
        bio: '',
        level: 1,
        level_name: '新手'
      },
      indicators: {
        性别: '--',
        年龄: '--',
        身高: '--',
        体重: '--',
        BMI: '--'
      },
      panorama: {
        dimensions: {
          nutrition: 60,
          diversity: 55,
          sleep: 62,
          exercise: 58,
          environment: 57
        },
        trend: 0
      },
      dietPlan: {
        name: 'AI导论基础巩固计划',
        daysCompleted: 0,
        totalDays: 7
      },
      dietDetail: {
        calories: 1800,
        protein: 65,
        carbs: 250,
        fat: 55
      },
      completionRate: 0,
      achievements: DEFAULT_ACHIEVEMENTS,
      stats: {
        total_analysis: 0,
        health_records_count: 0,
        takeaway_analysis_count: 0,
        favorites_count: 0,
        browse_history_count: 0,
        completed_goals: 0
      }
    }
  },
  computed: {
    avatarSource() {
      return getAssetURL(this.userInfo.avatar) || '../../static/avatar-1.png'
    },
    displayName() {
      if (this.isLoggedIn) return this.userInfo.name || '学习用户'
      if (this.isGuest) return '游客体验'
      return '未登录用户'
    },
    levelText() {
      return `${this.userInfo.level_name || 'Lv'} ${this.userInfo.level || 1}`
    },
    indicatorList() {
      return Object.keys(this.indicators).map((label) => ({ label, value: this.indicators[label] }))
    },
    dimensionList() {
      const d = this.panorama.dimensions || {}
      return [
        { key: 'nutrition', label: '基础掌握', value: d.nutrition || 0, color: '#10b981', gradient: 'linear-gradient(90deg, #10b981, #34d399)' },
        { key: 'diversity', label: '资源多样', value: d.diversity || 0, color: '#3b82f6', gradient: 'linear-gradient(90deg, #3b82f6, #60a5fa)' },
        { key: 'sleep', label: '睡眠质量', value: d.sleep || 0, color: '#8b5cf6', gradient: 'linear-gradient(90deg, #8b5cf6, #a78bfa)' },
        { key: 'exercise', label: '运动达标', value: d.exercise || 0, color: '#f59e0b', gradient: 'linear-gradient(90deg, #f59e0b, #fbbf24)' },
        { key: 'environment', label: '学习习惯', value: d.environment || 0, color: '#06b6d4', gradient: 'linear-gradient(90deg, #06b6d4, #22d3ee)' }
      ]
    },
    panoramaScore() {
      const list = this.dimensionList
      if (!list.length) return 0
      const total = list.reduce((sum, item) => sum + Number(item.value || 0), 0)
      return Math.round(total / list.length)
    },
    scoreLevelText() {
      if (this.panoramaScore >= 90) return '优秀'
      if (this.panoramaScore >= 75) return '良好'
      if (this.panoramaScore >= 60) return '稳定'
      return '待提升'
    },
    scoreLevelClass() {
      if (this.panoramaScore >= 90) return 'level-excellent'
      if (this.panoramaScore >= 75) return 'level-good'
      if (this.panoramaScore >= 60) return 'level-normal'
      return 'level-low'
    },
    userStats() {
      return {
        totalAnalysis: this.stats.total_analysis || 0,
        healthScore: this.panoramaScore,
        completedGoals: this.stats.completed_goals || this.dietPlan.daysCompleted || 0
      }
    },
    achievementsPreview() {
      return (this.achievements || DEFAULT_ACHIEVEMENTS).slice(0, 4)
    },
    completionEncourage() {
      const rate = this.completionRate
      if (rate >= 100) return '太棒了！计划已完成'
      if (rate >= 80) return '加油！即将完成目标'
      if (rate >= 50) return '坚持就是胜利！'
      if (rate >= 20) return '好的开始，继续保持'
      return '开始你的学习计划吧'
    }
  },
  async onLoad() {
    this.bindEvents()
    await this.checkLoginStatus()
  },
  async onShow() {
    await this.checkLoginStatus()
  },
  onUnload() {
    this.unbindEvents()
  },
  onPullDownRefresh() {
    this.checkLoginStatus().finally(() => {
      uni.stopPullDownRefresh()
    })
  },
  methods: {
    bindEvents() {
      if (this.eventHandlers.authLogin && this.eventHandlers.profileUpdated && this.eventHandlers.dietPlanUpdated) return

      this.eventHandlers.authLogin = () => {
        this.checkLoginStatus()
      }
      this.eventHandlers.profileUpdated = () => {
        cache.clearUserData()
        this.checkLoginStatus()
      }
      this.eventHandlers.dietPlanUpdated = (planData) => {
        this.dietPlan = {
          name: planData.name,
          daysCompleted: planData.daysCompleted || 0,
          totalDays: planData.totalDays || 7
        }
        this.dietDetail = {
          calories: planData.calories || 1800,
          protein: planData.protein || 65,
          carbs: planData.carbs || 250,
          fat: planData.fat || 55
        }
        this.completionRate = planData.completionRate || Math.round((planData.daysCompleted || 0) / 7 * 100)
      }

      uni.$on('auth:login-success', this.eventHandlers.authLogin)
      uni.$on('profile-updated', this.eventHandlers.profileUpdated)
      uni.$on('diet-plan-updated', this.eventHandlers.dietPlanUpdated)
    },
    unbindEvents() {
      if (!this.eventHandlers.authLogin || !this.eventHandlers.profileUpdated || !this.eventHandlers.dietPlanUpdated) return
      uni.$off('auth:login-success', this.eventHandlers.authLogin)
      uni.$off('profile-updated', this.eventHandlers.profileUpdated)
      uni.$off('diet-plan-updated', this.eventHandlers.dietPlanUpdated)
    },
    async checkLoginStatus() {
      const token = uni.getStorageSync('token')
      this.isLoggedIn = !!token
      this.isGuest = !token && guestManager.isGuestUser()

      if (!this.isLoggedIn && !this.isGuest) {
        this.applyDashboardData(null)
        return
      }

      if (!this.isLoggedIn && this.isGuest) {
        await this.ensureGuestSession()
      }

      await this.loadDashboardData()
    },
    async ensureGuestSession() {
      const result = await guestManager.ensureGuestSession()
      if (!result.success) {
        this.isGuest = false
      }
    },
    async loadDashboardData() {
      // 立即应用缓存数据，不显示加载动画
      const cachedData = cache.getUserData()
      if (cachedData) {
        this.applyDashboardData(cachedData)
      }

      if (this.dashboardRequestPromise) {
        return this.dashboardRequestPromise
      }

      this.dashboardRequestPromise = (async () => {
        try {
          const res = await request.get('/api/user/dashboard')
          if (res.code === 200) {
            cache.setUserData(res.data)
            this.applyDashboardData(res.data)
          }
        } catch (error) {
          console.error('加载数据失败:', error)
        } finally {
          this.dashboardRequestPromise = null
        }
      })()

      return this.dashboardRequestPromise
    },
    applyDashboardData(data) {
      if (!data) {
        const localUser = uni.getStorageSync('user') || {}
        this.userInfo = {
          id: localUser.id || '',
          name: localUser.name || '',
          avatar: localUser.avatar || '',
          bio: localUser.bio || '',
          level: localUser.level || 1,
          level_name: localUser.level_name || '新手'
        }
        this.indicators = {
          性别: localUser.gender || '--',
          年龄: localUser.age ? `${localUser.age} 岁` : '--',
          身高: localUser.height ? `${localUser.height} cm` : '--',
          体重: localUser.weight ? `${localUser.weight} kg` : '--',
          BMI: this.calculateBMI(localUser.height, localUser.weight)
        }
        this.panorama = {
          dimensions: { nutrition: 60, diversity: 55, sleep: 62, exercise: 58, environment: 57 },
          trend: 0
        }
        // 读取本地保存的饮食计划
        const savedPlan = uni.getStorageSync('selectedDietPlan')
        if (savedPlan) {
          this.dietPlan = { 
            name: savedPlan.name || 'AI导论基础巩固计划', 
            daysCompleted: savedPlan.daysCompleted || 0, 
            totalDays: savedPlan.totalDays || 7 
          }
          this.dietDetail = { 
            calories: savedPlan.calories || 1800, 
            protein: savedPlan.protein || 65, 
            carbs: savedPlan.carbs || 250, 
            fat: savedPlan.fat || 55 
          }
          this.completionRate = savedPlan.completionRate || Math.round((savedPlan.daysCompleted || 0) / 7 * 100)
        } else {
          this.dietPlan = { name: 'AI导论基础巩固计划', daysCompleted: 0, totalDays: 7 }
          this.dietDetail = { calories: 1800, protein: 65, carbs: 250, fat: 55 }
          this.completionRate = 0
        }
        this.achievements = DEFAULT_ACHIEVEMENTS
        this.stats = {
          total_analysis: 0,
          health_records_count: 0,
          takeaway_analysis_count: 0,
          favorites_count: 0,
          browse_history_count: 0,
          completed_goals: 0
        }
        return
      }

      const profile = data.profile || {}
      this.userInfo = {
        id: profile.id || '',
        name: profile.name || '',
        avatar: profile.avatar || '',
        bio: profile.bio || '',
        level: profile.level || 1,
        level_name: profile.level_name || '新手'
      }

      this.indicators = {
        性别: profile.gender || '--',
        年龄: profile.age ? `${profile.age} 岁` : '--',
        身高: profile.height ? `${profile.height} cm` : '--',
        体重: profile.weight ? `${profile.weight} kg` : '--',
        BMI: this.calculateBMI(profile.height, profile.weight)
      }

      this.panorama = data.panorama || this.panorama
      this.dietPlan = {
        ...this.dietPlan,
        ...(data.dietPlan || {})
      }
      this.dietDetail = {
        ...this.dietDetail,
        ...(data.dietDetail || {})
      }
      const totalDays = Number(this.dietPlan.totalDays || 7) || 7
      const daysCompleted = Number(this.dietPlan.daysCompleted || 0) || 0
      const completionRate = Number((data.dietPlan && data.dietPlan.completionRate) || data.completionRate)
      this.completionRate = Number.isFinite(completionRate)
        ? completionRate
        : Math.round(daysCompleted / totalDays * 100)
      this.achievements = (data.achievements && data.achievements.length) ? data.achievements : DEFAULT_ACHIEVEMENTS
      this.stats = data.stats || this.stats

      const localUser = uni.getStorageSync('user') || {}
      uni.setStorageSync('user', {
        ...localUser,
        ...profile
      })
    },
    calculateBMI(height, weight) {
      const h = Number(height)
      const w = Number(weight)
      if (!h || !w || h <= 0 || w <= 0) return '--'
      const bmi = w / Math.pow(h / 100, 2)
      return bmi.toFixed(1)
    },
    handleLogin() {
      uni.navigateTo({
        url: '/pages/user/login?redirect=' + encodeURIComponent('/pages/personal-center/personal-center')
      })
    },
    handleEditProfile() {
      if (!this.isLoggedIn) {
        uni.showToast({ title: '请先登录', icon: 'none' })
        return
      }
      uni.navigateTo({ url: '/pages/personal-center/profile-edit' })
    },
    handleViewAllAchievements() {
      if (!this.isLoggedIn) {
        uni.showToast({ title: '登录后可查看完整成就列表', icon: 'none' })
        return
      }
      uni.navigateTo({ url: '/pages/personal-center/achievements' })
    },
    handleOpenMyData() {
      if (!this.isLoggedIn) {
        uni.showToast({ title: '登录后可查看完整数据', icon: 'none' })
        return
      }
      uni.navigateTo({ url: '/pages/personal-center/my-uploads' })
    },
    handleAchievementClick(achievement) {
      uni.showModal({
        title: achievement.name,
        content: achievement.description || '继续使用并记录更多数据，就能逐步解锁它！',
        showCancel: false
      })
    },
    handleLogout() {
      if (this.isGuest) {
        guestManager.clearGuestSession()
        cache.clearUserData()
        this.isGuest = false
        this.applyDashboardData(null)
        uni.showToast({ title: '已退出游客模式', icon: 'success' })
        return
      }

      uni.showModal({
        title: '退出登录',
        content: '确认退出当前账号吗？',
        success: (res) => {
          if (!res.confirm) return
          uni.removeStorageSync('token')
          uni.removeStorageSync('user')
          cache.clearUserData()
          this.isLoggedIn = false
          this.applyDashboardData(null)
          uni.showToast({ title: '已退出登录', icon: 'success' })
        }
      })
    }
  }
}
</script>

<style scoped>
.personal-center-container { min-height: 100vh; background: #f0f4f8; padding-top: env(safe-area-inset-top); }
.page-header { padding: 40rpx; background: linear-gradient(135deg, #86efac, #34d399); border-radius: 0 0 60rpx 60rpx; color: white; text-align: center; }
.page-title { font-size: 52rpx; font-weight: 800; letter-spacing: 2rpx; margin-bottom: 8rpx; }
.page-subtitle { font-size: 24rpx; opacity: 0.9; line-height: 1.6; }
.content-wrapper { padding: 0 32rpx; margin-top: -80rpx; }
.user-profile-card { background: #ffffff; border-radius: 40rpx; overflow: hidden; box-shadow: 0 20rpx 60rpx rgba(0,0,0,0.05); margin-bottom: 32rpx; }
.profile-header-bg { height: 160rpx; background: rgba(255,255,255,0.1); }
.profile-body { padding: 0 40rpx 40rpx 40rpx; margin-top: -60rpx; }
.user-profile-header { display: flex; align-items: center; gap: 32rpx; margin-top: -60rpx; padding: 0 10rpx; }
.avatar-wrapper { position: relative; flex-shrink: 0; }
.avatar { width: 140rpx; height: 140rpx; border-radius: 70rpx; border: 6rpx solid white; box-shadow: 0 12rpx 32rpx rgba(0,0,0,0.12); background: #f8fafc; }
.avatar-edit-btn { position: absolute; bottom: 4rpx; right: 4rpx; background: #4facfe; color: white; font-size: 18rpx; padding: 6rpx 14rpx; border-radius: 12rpx; border: 4rpx solid white; font-weight: 700; }
.user-info-content { flex: 1; display: flex; flex-direction: column; gap: 10rpx; }
.user-name-line { display: flex; align-items: center; gap: 16rpx; flex-wrap: wrap; }
.user-name { font-size: 40rpx; font-weight: 800; color: #1e293b; }
.user-badge, .guest-badge { color: white; font-size: 18rpx; padding: 4rpx 12rpx; border-radius: 8rpx; font-weight: 800; }
.user-badge { background: linear-gradient(135deg, #fbbf24, #f59e0b); }
.guest-badge { background: linear-gradient(135deg, #94a3b8, #64748b); }
.user-action-area { display: flex; align-items: center; }
.auth-box { display: flex; align-items: center; gap: 8rpx; background: rgba(79, 172, 254, 0.08); padding: 10rpx 24rpx; border-radius: 100rpx; }
.auth-text, .auth-arrow { font-size: 26rpx; color: #4facfe; font-weight: 700; }
.user-id { font-size: 24rpx; color: #94a3b8; font-weight: 500; }
.user-bio { font-size: 22rpx; color: #64748b; line-height: 1.6; }
.user-stats-bar { display: flex; justify-content: space-between; align-items: center; margin-top: 40rpx; padding: 32rpx 20rpx 0; border-top: 1px solid #f1f5f9; }
.stat-item { flex: 1; text-align: center; }
.stat-divider { width: 1px; height: 40rpx; background: #f1f5f9; }
.stat-value { font-size: 36rpx; font-weight: 700; color: #1e293b; display: block; margin-bottom: 4rpx; }
.stat-label { font-size: 20rpx; color: #64748b; font-weight: 500; }
.indicators-grid { display: flex; background: #f8fafc; padding: 20rpx 0; }
.indicator-box { flex: 1; display: flex; flex-direction: column; align-items: center; gap: 4rpx; }
.indicator-label { font-size: 18rpx; color: #94a3b8; font-weight: 600; }
.indicator-value { font-size: 24rpx; color: #334155; font-weight: 700; }
.glass-card { background: white; border-radius: 40rpx; padding: 40rpx; margin-bottom: 32rpx; box-shadow: 0 8rpx 24rpx rgba(0,0,0,0.03); border: 1px solid rgba(255,255,255,0.8); }
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 32rpx; gap: 20rpx; }
.card-title-box { display: flex; align-items: center; gap: 12rpx; }
.card-title { font-size: 32rpx; font-weight: 700; color: #1e293b; }
.trend-tag { padding: 6rpx 16rpx; border-radius: 100rpx; font-size: 20rpx; font-weight: 700; }
.trend-tag.up { background: #ecfdf5; color: #059669; }
.trend-tag.down { background: #fef2f2; color: #dc2626; }
.panorama-score-hero { display: flex; align-items: center; gap: 32rpx; margin-bottom: 36rpx; padding: 28rpx; background: linear-gradient(135deg, #f0f9ff, #ecfdf5); border-radius: 28rpx; }
.score-summary { display: flex; align-items: baseline; gap: 8rpx; flex-wrap: wrap; }
.score-number-inline { font-size: 56rpx; font-weight: 800; color: #1e293b; }
.score-unit-inline { font-size: 24rpx; color: #64748b; font-weight: 600; margin-right: 16rpx; }
.score-level-text { font-size: 32rpx; font-weight: 800; }
.score-level-text.level-excellent { color: #059669; }
.score-level-text.level-good { color: #3b82f6; }
.score-level-text.level-normal { color: #f59e0b; }
.score-level-text.level-low { color: #ef4444; }
.score-desc { font-size: 22rpx; color: #94a3b8; font-weight: 500; width: 100%; margin-top: 4rpx; }
.dimension-bars { display: flex; flex-direction: column; gap: 20rpx; }
.dim-bar-item { display: flex; flex-direction: column; gap: 8rpx; }
.dim-bar-header { display: flex; justify-content: space-between; align-items: center; }
.dim-bar-label { font-size: 24rpx; color: #475569; font-weight: 600; }
.dim-bar-value { font-size: 24rpx; font-weight: 800; }
.dim-bar-track { height: 12rpx; background: #f1f5f9; border-radius: 6rpx; overflow: hidden; }
.dim-bar-fill { height: 100%; border-radius: 6rpx; transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1); }
/* 游客模式占位信息样式 */
.panorama-guest-placeholder { display: flex; flex-direction: column; align-items: center; padding: 60rpx 40rpx; text-align: center; }
.placeholder-icon { font-size: 80rpx; margin-bottom: 24rpx; opacity: 0.6; }
.placeholder-title { font-size: 32rpx; font-weight: 700; color: #1e293b; margin-bottom: 16rpx; }
.placeholder-desc { font-size: 24rpx; color: #64748b; line-height: 1.6; margin-bottom: 32rpx; }
.placeholder-login-btn { background: linear-gradient(135deg, #4facfe, #00f2fe); padding: 20rpx 48rpx; border-radius: 100rpx; }
.placeholder-login-btn text { color: white; font-size: 28rpx; font-weight: 700; }
.diet-content { display: flex; justify-content: space-between; align-items: center; background: #f0f9ff; padding: 32rpx; border-radius: 32rpx; margin-bottom: 24rpx; }
.plan-title { font-size: 30rpx; font-weight: 700; color: #0369a1; display: block; margin-bottom: 4rpx; }
.plan-subtitle { font-size: 22rpx; color: #60a5fa; }
.days { font-weight: 800; color: #2563eb; font-size: 28rpx; margin: 0 4rpx; }
/* Completion Section Styles */
.completion-section {
  background: linear-gradient(135deg, #f0fdf4 0%, #ecfdf5 100%);
  border-radius: 24rpx;
  padding: 28rpx;
  border: 1rpx solid #bbf7d0;
}

.completion-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16rpx;
}

.completion-label {
  font-size: 26rpx;
  font-weight: 700;
  color: #166534;
}

.completion-percentage {
  font-size: 36rpx;
  font-weight: 800;
  color: #16a34a;
}

.completion-progress-bar {
  height: 16rpx;
  background: #dcfce7;
  border-radius: 8rpx;
  overflow: hidden;
  margin-bottom: 16rpx;
}

.completion-progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #22c55e 0%, #16a34a 100%);
  border-radius: 8rpx;
  transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1);
}

.completion-stats {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.completion-stats-text {
  font-size: 22rpx;
  color: #15803d;
  font-weight: 500;
}

.completion-encourage {
  font-size: 22rpx;
  color: #22c55e;
  font-weight: 600;
}

/* Hide old diet detail styles */
.diet-detail-section,
.diet-detail-row,
.diet-detail-item,
.detail-num,
.detail-unit,
.detail-label,
.detail-divider {
  display: none;
}
.achievements-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 24rpx; }
.medal-item { display: flex; flex-direction: column; align-items: center; gap: 10rpx; padding: 20rpx 8rpx; border-radius: 24rpx; background: #f8fafc; position: relative; }
.medal-item.unlocked { background: linear-gradient(135deg, #fffbeb, #fef3c7); }
.medal-item:not(.unlocked) { opacity: 0.5; filter: grayscale(1); }
.medal-icon-wrap { width: 80rpx; height: 80rpx; border-radius: 50%; display: flex; align-items: center; justify-content: center; background: #e2e8f0; }
.medal-item.unlocked .medal-icon-wrap { background: linear-gradient(135deg, #fbbf24, #f59e0b); box-shadow: 0 6rpx 16rpx rgba(245, 158, 11, 0.3); }
.medal-icon { font-size: 36rpx; }
.medal-name { font-size: 20rpx; font-weight: 700; color: #475569; text-align: center; }
.medal-status-dot { width: 12rpx; height: 12rpx; border-radius: 50%; background: #cbd5e1; }
.medal-status-dot.active { background: #f59e0b; box-shadow: 0 0 8rpx rgba(245, 158, 11, 0.5); }
.view-more { font-size: 24rpx; color: #4facfe; font-weight: 600; }
.service-list { display: flex; flex-direction: column; }
.service-list-item { display: flex; justify-content: space-between; align-items: center; padding: 28rpx 16rpx; border-bottom: 1px solid #f1f5f9; }
.service-list-item:last-child { border-bottom: none; }
.service-list-label { display: block; font-size: 28rpx; font-weight: 600; color: #334155; margin-bottom: 8rpx; }
.service-list-desc { display: block; font-size: 22rpx; color: #94a3b8; line-height: 1.5; }
.service-list-arrow { font-size: 28rpx; color: #cbd5e1; font-weight: 400; }
.footer-actions { margin: 60rpx 0 40rpx; }
.sign-out-btn { width: 100%; height: 96rpx; line-height: 96rpx; background: #fff1f2; color: #e11d48; border-radius: 28rpx; font-size: 30rpx; font-weight: 700; border: none; }
</style>
