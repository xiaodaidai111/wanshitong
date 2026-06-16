<template>
  <view class="personal-center-container">
    <view class="page-header">
      <view class="page-title">个人中心</view>
      <text class="page-subtitle">欢迎使用设备检修知识作业系统！</text>
    </view>

    <view class="main-content">
      <view class="content-wrapper">
        <!-- 用户信息卡片 -->
        <view class="user-profile-card">
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
                  <text v-else class="user-id">ID：{{ userInfo.id || '--' }}</text>
                </view>

                <text v-if="isLoggedIn && userInfo.bio" class="user-bio">{{ userInfo.bio }}</text>
                <text v-else-if="isGuest" class="user-bio">游客模式可体验功能，登录后保存专属数据</text>
                <text v-else class="user-bio">登录后可同步个人资料、检修记录和收藏资源</text>
              </view>
            </view>

            <view class="user-stats-bar">
              <view class="stat-item" :class="{ 'stat-disabled': !isLoggedIn }">
                <text class="stat-value" :class="{ 'stat-value-disabled': !isLoggedIn }">{{ userStats.totalAnalysis }}</text>
                <text class="stat-label">检索次数</text>
              </view>
              <view class="stat-divider"></view>
              <view class="stat-item" :class="{ 'stat-disabled': !isLoggedIn }">
                <text class="stat-value" :class="{ 'stat-value-disabled': !isLoggedIn }">{{ isLoggedIn ? userStats.healthScore : '--' }}</text>
                <text class="stat-label">检修评分</text>
              </view>
              <view class="stat-divider"></view>
              <view class="stat-item" :class="{ 'stat-disabled': !isLoggedIn }">
                <text class="stat-value" :class="{ 'stat-value-disabled': !isLoggedIn }">{{ isLoggedIn ? userStats.completedGoals : '--' }}</text>
                <text class="stat-label">本周任务</text>
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

        <!-- 检修数据全景 -->
        <view class="section-card">
          <view class="card-header">
            <text class="card-title">检修数据全景</text>
            <view v-if="isLoggedIn" class="trend-tag" :class="panorama.trend >= 0 ? 'up' : 'down'">
              <text>{{ panorama.trend >= 0 ? '较上周+' : '较上周' }}{{ Math.abs(panorama.trend) }}%</text>
            </view>
          </view>

          <view v-if="!isLoggedIn" class="empty-placeholder">
            <text class="empty-title">登录后查看检修数据</text>
            <text class="empty-desc">登录后可查看你的个性化检修评分、资源使用分析和检修趋势</text>
            <view class="empty-btn" @click="handleLogin">
              <text class="empty-btn-text">立即登录</text>
            </view>
          </view>

          <view v-else>
            <view class="score-row">
              <text class="score-number">{{ panoramaScore }}</text>
              <text class="score-unit">分</text>
              <text class="score-level" :class="scoreLevelClass">{{ scoreLevelText }}</text>
            </view>
            <text class="score-desc">综合检修画像与作业质量评分</text>

            <view class="dimension-bars">
              <view v-for="dim in dimensionList" :key="dim.key" class="dim-bar-item">
                <text class="dim-label">{{ dim.label }}</text>
                <view class="dim-bar-track">
                  <view class="dim-bar-fill" :style="{ width: dim.value + '%', background: dim.color }"></view>
                </view>
                <text class="dim-value" :style="{ color: dim.color }">{{ dim.value }}%</text>
              </view>
            </view>
          </view>
        </view>

        <!-- 检修计划 -->
        <view class="section-card">
          <view class="card-header">
            <text class="card-title">检修计划</text>
          </view>

          <view v-if="!isLoggedIn" class="empty-placeholder">
            <text class="empty-title">登录后查看检修计划</text>
            <text class="empty-desc">登录后可制定个性化检修计划，追踪每日完成情况</text>
            <view class="empty-btn" @click="handleLogin">
              <text class="empty-btn-text">立即登录</text>
            </view>
          </view>

          <view v-else>
            <view class="plan-row">
              <view class="plan-info">
                <text class="plan-name">{{ maintenancePlan.name || '发动机检修技能提升计划' }}</text>
                <text class="plan-meta">最近 7 天已记录 <text class="plan-days">{{ maintenancePlan.daysCompleted || 0 }}</text> 天</text>
              </view>
              <text class="plan-arrow">></text>
            </view>

            <view class="completion-bar-wrap">
              <view class="completion-top">
                <text class="completion-label">计划完成度</text>
                <text class="completion-pct">{{ completionRate }}%</text>
              </view>
              <view class="completion-track">
                <view class="completion-fill" :style="{ width: completionRate + '%' }"></view>
              </view>
              <view class="completion-bottom">
                <text class="completion-done">已完成 {{ maintenancePlan.daysCompleted || 0 }}/7 天</text>
                <text class="completion-tip">{{ completionEncourage }}</text>
              </view>
            </view>
          </view>
        </view>

        <!-- 快捷功能 — 列表式 -->
        <view class="section-card">
          <view class="card-header">
            <text class="card-title">快捷功能</text>
          </view>
          <view class="menu-list">
            <view class="menu-item" @click="handleQuickAction('search')">
              <view class="menu-dot" style="background:#2563eb"></view>
              <view class="menu-content">
                <text class="menu-name">智能检索</text>
                <text class="menu-desc">设备故障智能排查</text>
              </view>
              <text class="menu-arrow">></text>
            </view>
            <view class="menu-item" @click="handleQuickAction('knowledge')">
              <view class="menu-dot" style="background:#7c3aed"></view>
              <view class="menu-content">
                <text class="menu-name">知识库</text>
                <text class="menu-desc">检修资料与技术文档</text>
              </view>
              <text class="menu-arrow">></text>
            </view>
            <view class="menu-item" @click="handleQuickAction('task')">
              <view class="menu-dot" style="background:#0891b2"></view>
              <view class="menu-content">
                <text class="menu-name">任务中心</text>
                <text class="menu-desc">当日检修任务安排</text>
              </view>
              <text class="menu-arrow">></text>
            </view>
            <view class="menu-item" @click="handleQuickAction('record')">
              <view class="menu-dot" style="background:#0369a1"></view>
              <view class="menu-content">
                <text class="menu-name">检修记录</text>
                <text class="menu-desc">历史检修工单查看</text>
              </view>
              <text class="menu-arrow">></text>
            </view>
            <view class="menu-item" @click="handleQuickAction('stats')">
              <view class="menu-dot" style="background:#d97706"></view>
              <view class="menu-content">
                <text class="menu-name">数据统计</text>
                <text class="menu-desc">检修数据分析报表</text>
              </view>
              <text class="menu-arrow">></text>
            </view>
            <view class="menu-item" @click="handleQuickAction('favorites')">
              <view class="menu-dot" style="background:#e11d48"></view>
              <view class="menu-content">
                <text class="menu-name">我的收藏</text>
                <text class="menu-desc">收藏的知识与案例</text>
              </view>
              <text class="menu-arrow">></text>
            </view>
            <view class="menu-item" @click="handleQuickAction('history')">
              <view class="menu-dot" style="background:#64748b"></view>
              <view class="menu-content">
                <text class="menu-name">浏览历史</text>
                <text class="menu-desc">近期浏览记录</text>
              </view>
              <text class="menu-arrow">></text>
            </view>
            <view class="menu-item menu-item-last" @click="handleQuickAction('help')">
              <view class="menu-dot" style="background:#475569"></view>
              <view class="menu-content">
                <text class="menu-name">帮助中心</text>
                <text class="menu-desc">使用指南与常见问题</text>
              </view>
              <text class="menu-arrow">></text>
            </view>
          </view>
        </view>

        <!-- 最近浏览 -->
        <view class="section-card">
          <view class="card-header">
            <text class="card-title">最近浏览</text>
            <text class="view-more" @click="handleViewAllHistory">全部 ></text>
          </view>
          <view v-if="recentHistory.length > 0" class="menu-list">
            <view v-for="(item, index) in recentHistory" :key="index" class="menu-item" :class="{ 'menu-item-last': index === recentHistory.length - 1 }" @click="handleHistoryClick(item)">
              <view class="menu-dot" :style="{ background: item.dotColor }"></view>
              <view class="menu-content">
                <text class="menu-name">{{ item.title }}</text>
                <text class="menu-desc">{{ item.time }}</text>
              </view>
              <text class="menu-arrow">></text>
            </view>
          </view>
          <view v-else class="empty-hint">
            <text class="empty-hint-text">暂无浏览记录</text>
          </view>
        </view>

        <!-- 数据与服务 -->
        <view class="section-card">
          <view class="card-header">
            <text class="card-title">数据与服务</text>
          </view>
          <view class="menu-list">
            <view class="menu-item" @click="handleOpenMyData">
              <view class="menu-dot" style="background:#2563eb"></view>
              <view class="menu-content">
                <text class="menu-name">我的数据</text>
                <text class="menu-desc">检修记录、分析历史、收藏与浏览记录</text>
              </view>
              <text class="menu-arrow">></text>
            </view>
            <view class="menu-item menu-item-last" @click="handleEditProfile">
              <view class="menu-dot" style="background:#0891b2"></view>
              <view class="menu-content">
                <text class="menu-name">个人资料</text>
                <text class="menu-desc">昵称、头像、年龄、工龄、职称与简介</text>
              </view>
              <text class="menu-arrow">></text>
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
  { id: 1, name: '初出茅庐', icon: '🔧', description: '完成第一次设备检修记录', unlocked: false, gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' },
  { id: 2, name: '坚持不懈', icon: '🔥', description: '连续完成检修记录 7 天', unlocked: false, gradient: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)' },
  { id: 3, name: '检修能手', icon: '⚙️', description: '累计完成 30 次检修记录', unlocked: false, gradient: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)' },
  { id: 4, name: '规范标兵', icon: '✅', description: '连续 7 天按标准流程完成检修', unlocked: false, gradient: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)' },
  { id: 5, name: '质量先锋', icon: '🏆', description: '检修质量评分达到 90 分以上', unlocked: false, gradient: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)' },
  { id: 6, name: '安全卫士', icon: '🛡️', description: '连续 30 天无安全事故', unlocked: false, gradient: 'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)' },
  { id: 7, name: '效率之星', icon: '⚡', description: '检修效率提升超过 30%', unlocked: false, gradient: 'linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)' },
  { id: 8, name: '知识达人', icon: '📚', description: '完成全部设备知识考核', unlocked: false, gradient: 'linear-gradient(135deg, #cfd9df 0%, #e2ebf0 100%)' }
]

const DEMO_DASHBOARD_DATA = {
  profile: {
    id: 'MX-2026-001',
    name: '张工',
    avatar: '',
    bio: '设备检修工程师',
    gender: '男',
    age: 32,
    specialty: '电气检修',
    work_years: 8,
    level: 5,
    level_name: '高级检修员',
    height: 175,
    weight: 68
  },
  panorama: {
    dimensions: { safety: 92, quality: 88, efficiency: 84, knowledge: 90, compliance: 91 },
    trend: 12
  },
  maintenancePlan: {
    name: 'ZK-320配电柜复检提升计划',
    daysCompleted: 5,
    totalDays: 7
  },
  skillDetail: {
    safety_score: 92,
    quality_score: 88,
    efficiency_score: 84,
    compliance_score: 91
  },
  stats: {
    total_analysis: 36,
    health_records_count: 18,
    takeaway_analysis_count: 12,
    favorites_count: 9,
    browse_history_count: 42,
    completed_goals: 5
  },
  achievements: DEFAULT_ACHIEVEMENTS.map((item, index) => ({
    ...item,
    unlocked: index < 5
  }))
}

export default {
  data() {
    return {
      loading: false,
      dashboardRequestPromise: null,
      isLoggedIn: false,
      isGuest: false,
      eventHandlers: {
        authLogin: null,
        profileUpdated: null,
        maintenancePlanUpdated: null
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
        工种: '--',
        工龄: '--',
        等级: '--'
      },
      panorama: {
        dimensions: {
          safety: 60,
          quality: 55,
          efficiency: 62,
          knowledge: 58,
          compliance: 57
        },
        trend: 0
      },
      maintenancePlan: {
        name: '发动机检修技能提升计划',
        daysCompleted: 0,
        totalDays: 7
      },
      skillDetail: {
        safety_score: 85,
        quality_score: 78,
        efficiency_score: 72,
        compliance_score: 80
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
      },
      recentHistory: [
        { id: 1, title: '摩托车发动机维修手册', time: '刚刚', dotColor: '#2563eb' },
        { id: 2, title: '点火系统故障排查', time: '10分钟前', dotColor: '#7c3aed' },
        { id: 3, title: '发动机异响诊断案例', time: '1小时前', dotColor: '#0891b2' }
      ]
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
        { key: 'safety', label: '安全合规', value: d.safety || 0, color: '#10b981' },
        { key: 'quality', label: '作业质量', value: d.quality || 0, color: '#3b82f6' },
        { key: 'efficiency', label: '检修效率', value: d.efficiency || 0, color: '#8b5cf6' },
        { key: 'knowledge', label: '知识储备', value: d.knowledge || 0, color: '#f59e0b' },
        { key: 'compliance', label: '流程规范', value: d.compliance || 0, color: '#06b6d4' }
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
        completedGoals: this.stats.completed_goals || this.maintenancePlan.daysCompleted || 0
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
      return '开始你的检修计划吧'
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
      if (this.eventHandlers.authLogin && this.eventHandlers.profileUpdated && this.eventHandlers.maintenancePlanUpdated) return

      this.eventHandlers.authLogin = () => {
        this.checkLoginStatus()
      }
      this.eventHandlers.profileUpdated = () => {
        cache.clearUserData()
        this.checkLoginStatus()
      }
      this.eventHandlers.maintenancePlanUpdated = (planData) => {
        this.maintenancePlan = {
          name: planData.name,
          daysCompleted: planData.daysCompleted || 0,
          totalDays: planData.totalDays || 7
        }
        this.skillDetail = {
          safety_score: planData.safety_score || 85,
          quality_score: planData.quality_score || 78,
          efficiency_score: planData.efficiency_score || 72,
          compliance_score: planData.compliance_score || 80
        }
        this.completionRate = planData.completionRate || Math.round((planData.daysCompleted || 0) / 7 * 100)
      }

      uni.$on('auth:login-success', this.eventHandlers.authLogin)
      uni.$on('profile-updated', this.eventHandlers.profileUpdated)
      uni.$on('maintenance-plan-updated', this.eventHandlers.maintenancePlanUpdated)
    },
    unbindEvents() {
      if (!this.eventHandlers.authLogin || !this.eventHandlers.profileUpdated || !this.eventHandlers.maintenancePlanUpdated) return
      uni.$off('auth:login-success', this.eventHandlers.authLogin)
      uni.$off('profile-updated', this.eventHandlers.profileUpdated)
      uni.$off('maintenance-plan-updated', this.eventHandlers.maintenancePlanUpdated)
    },
    async checkLoginStatus() {
      const token = uni.getStorageSync('token')
      this.isLoggedIn = !!token
      this.isGuest = false

      if (!this.isLoggedIn) {
        this.isLoggedIn = true
        this.applyDashboardData(DEMO_DASHBOARD_DATA)
        return
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
          工种: localUser.bio || '未设置',
          工龄: localUser.height ? `${localUser.height} 年` : '--',
          等级: localUser.level_name || '新手'
        }
        this.panorama = {
          dimensions: { safety: 85, quality: 78, efficiency: 72, knowledge: 68, compliance: 80 },
          trend: 0
        }
        const savedPlan = uni.getStorageSync('selectedDietPlan')
        if (savedPlan) {
          this.maintenancePlan = {
            name: savedPlan.name || '发动机检修技能提升计划',
            daysCompleted: savedPlan.daysCompleted || 0,
            totalDays: savedPlan.totalDays || 7
          }
          this.skillDetail = {
            safety_score: savedPlan.safety_score || 85,
            quality_score: savedPlan.quality_score || 78,
            efficiency_score: savedPlan.efficiency_score || 72,
            compliance_score: savedPlan.compliance_score || 80
          }
          this.completionRate = savedPlan.completionRate || Math.round((savedPlan.daysCompleted || 0) / 7 * 100)
        } else {
          this.maintenancePlan = { name: '发动机检修技能提升计划', daysCompleted: 0, totalDays: 7 }
          this.skillDetail = { safety_score: 85, quality_score: 78, efficiency_score: 72, compliance_score: 80 }
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
        工种: profile.specialty || profile.bio || '检修人员',
        工龄: profile.work_years ? `${profile.work_years} 年` : '--',
        等级: profile.level_name || '新手'
      }

      this.panorama = data.panorama || this.panorama
      this.maintenancePlan = {
        ...this.maintenancePlan,
        ...(data.maintenancePlan || {})
      }
      this.skillDetail = {
        ...this.skillDetail,
        ...(data.skillDetail || {})
      }
      const totalDays = Number(this.maintenancePlan.totalDays || 7) || 7
      const daysCompleted = Number(this.maintenancePlan.daysCompleted || 0) || 0
      const completionRate = Number((data.maintenancePlan && data.maintenancePlan.completionRate) || data.completionRate)
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
    },
    handleQuickAction(type) {
      const actions = {
        search: { path: '/pages/takeaway-expert/takeaway-expert', tabbar: true },
        knowledge: { path: '/pages/restaurant-recommendation/restaurant-recommendation', tabbar: true },
        task: { path: '/pages/task-detail/task-detail', tabbar: false },
        record: { path: '/pages/health-manager/health-manager', tabbar: true },
        stats: { path: '/pages/personal-center/my-uploads', tabbar: false },
        favorites: { path: '/pages/restaurant-recommendation/restaurant-recommendation', tabbar: true },
        history: { path: '/pages/personal-center/my-uploads', tabbar: false },
        help: { path: '/pages/webview/webview?url=' + encodeURIComponent('https://www.example.com/help'), tabbar: false }
      }
      const action = actions[type]
      if (!action) return
      if (action.tabbar) {
        uni.switchTab({ url: action.path })
      } else {
        uni.navigateTo({ url: action.path })
      }
    },
    handleViewAllHistory() {
      uni.navigateTo({ url: '/pages/personal-center/my-uploads' })
    },
    handleHistoryClick(item) {
      uni.showToast({ title: '即将打开：' + item.title, icon: 'none' })
    }
  }
}
</script>

<style scoped>
/* 基础布局 */
.personal-center-container {
  min-height: 100vh;
  background: #f5f6fa;
  padding-top: env(safe-area-inset-top);
}

.page-header { padding: 40rpx; background: linear-gradient(135deg, #0F766E, #0EA5E9); border-radius: 0 0 60rpx 60rpx; color: white; text-align: center; }
.page-title { font-size: 52rpx; font-weight: 800; letter-spacing: 2rpx; margin-bottom: 8rpx; }
.page-subtitle { font-size: 24rpx; opacity: 0.9; line-height: 1.6; }

.content-wrapper {
  padding: 0 32rpx;
  margin-top: 8rpx;
  padding-bottom: env(safe-area-inset-bottom);
}

/* 用户信息卡片 */
.user-profile-card {
  background: #ffffff;
  border-radius: 20rpx;
  overflow: hidden;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.06);
  margin-bottom: 20rpx;
}

.profile-body {
  padding: 32rpx;
}

.user-profile-header {
  display: flex;
  align-items: center;
  gap: 24rpx;
}

.avatar-wrapper {
  position: relative;
  flex-shrink: 0;
}

.avatar {
  width: 112rpx;
  height: 112rpx;
  border-radius: 50%;
  background: #e2e8f0;
}

.avatar-edit-btn {
  position: absolute;
  bottom: 0;
  right: -4rpx;
  background: #2563eb;
  color: #ffffff;
  font-size: 18rpx;
  padding: 4rpx 12rpx;
  border-radius: 8rpx;
  font-weight: 600;
}

.user-info-content {
  flex: 1;
  min-width: 0;
}

.user-name-line {
  display: flex;
  align-items: center;
  gap: 10rpx;
  margin-bottom: 6rpx;
}

.user-name {
  font-size: 34rpx;
  font-weight: 700;
  color: #1e293b;
}

.user-badge {
  background: #eff6ff;
  color: #2563eb;
  font-size: 18rpx;
  padding: 3rpx 10rpx;
  border-radius: 6rpx;
  font-weight: 600;
}

.guest-badge {
  background: #f1f5f9;
  color: #64748b;
  font-size: 18rpx;
  padding: 3rpx 10rpx;
  border-radius: 6rpx;
  font-weight: 600;
}

.user-action-area {
  margin-bottom: 4rpx;
}

.auth-box {
  display: inline-flex;
  align-items: center;
  gap: 4rpx;
  background: #eff6ff;
  padding: 8rpx 20rpx;
  border-radius: 8rpx;
}

.auth-text {
  font-size: 24rpx;
  color: #2563eb;
  font-weight: 600;
}

.auth-arrow {
  font-size: 22rpx;
  color: #2563eb;
}

.user-id {
  font-size: 22rpx;
  color: #94a3b8;
}

.user-bio {
  font-size: 22rpx;
  color: #64748b;
  line-height: 1.5;
  display: block;
}

.user-stats-bar {
  display: flex;
  align-items: center;
  margin-top: 24rpx;
  padding-top: 24rpx;
  border-top: 1rpx solid #f1f5f9;
}

.stat-item {
  flex: 1;
  text-align: center;
}

.stat-item.stat-disabled .stat-value {
  color: #cbd5e1;
}

.stat-item.stat-disabled .stat-label {
  color: #94a3b8;
}

.stat-divider {
  width: 1rpx;
  height: 32rpx;
  background: #e2e8f0;
}

.stat-value {
  font-size: 32rpx;
  font-weight: 700;
  color: #1e293b;
  display: block;
  margin-bottom: 2rpx;
}

.stat-value-disabled {
  color: #cbd5e1 !important;
}

.stat-label {
  font-size: 20rpx;
  color: #94a3b8;
}

.indicators-grid {
  display: flex;
  background: #f8fafc;
  padding: 16rpx 0;
  border-top: 1rpx solid #f1f5f9;
}

.indicator-box {
  flex: 1;
  text-align: center;
}

.indicator-label {
  font-size: 18rpx;
  color: #94a3b8;
  display: block;
  margin-bottom: 2rpx;
}

.indicator-value {
  font-size: 24rpx;
  color: #475569;
  font-weight: 600;
}

/* 通用卡片 */
.section-card {
  background: #ffffff;
  border-radius: 20rpx;
  padding: 28rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.04);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24rpx;
}

.card-title {
  font-size: 30rpx;
  font-weight: 700;
  color: #1e293b;
}

.view-more {
  font-size: 24rpx;
  color: #2563eb;
  font-weight: 600;
}

.trend-tag {
  padding: 4rpx 14rpx;
  border-radius: 6rpx;
  font-size: 20rpx;
  font-weight: 600;
}

.trend-tag.up {
  background: #ecfdf5;
  color: #059669;
}

.trend-tag.down {
  background: #fef2f2;
  color: #dc2626;
}

/* 检修数据全景 */
.score-row {
  display: flex;
  align-items: baseline;
  gap: 6rpx;
  margin-bottom: 4rpx;
}

.score-number {
  font-size: 56rpx;
  font-weight: 700;
  color: #1e293b;
}

.score-unit {
  font-size: 24rpx;
  color: #94a3b8;
  font-weight: 500;
  margin-right: 12rpx;
}

.score-level {
  font-size: 28rpx;
  font-weight: 700;
}

.level-excellent {
  color: #059669;
}

.level-good {
  color: #3b82f6;
}

.level-normal {
  color: #f59e0b;
}

.level-low {
  color: #ef4444;
}

.score-desc {
  font-size: 22rpx;
  color: #94a3b8;
  margin-bottom: 24rpx;
}

.dimension-bars {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.dim-bar-item {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.dim-label {
  font-size: 24rpx;
  color: #475569;
  font-weight: 500;
  width: 120rpx;
  flex-shrink: 0;
}

.dim-bar-track {
  flex: 1;
  height: 12rpx;
  background: #f1f5f9;
  border-radius: 6rpx;
  overflow: hidden;
}

.dim-bar-fill {
  height: 100%;
  border-radius: 6rpx;
  transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1);
}

.dim-value {
  font-size: 24rpx;
  font-weight: 700;
  width: 80rpx;
  text-align: right;
  flex-shrink: 0;
}

/* 空状态提示 */
.empty-placeholder {
  text-align: center;
  padding: 32rpx 0;
}

.empty-title {
  font-size: 28rpx;
  font-weight: 600;
  color: #1e293b;
  display: block;
  margin-bottom: 8rpx;
}

.empty-desc {
  font-size: 22rpx;
  color: #94a3b8;
  display: block;
  margin-bottom: 24rpx;
}

.empty-btn {
  display: inline-block;
  background: #2563eb;
  padding: 16rpx 40rpx;
  border-radius: 10rpx;
}

.empty-btn-text {
  color: #ffffff;
  font-size: 26rpx;
  font-weight: 600;
}

/* 检修计划 */
.plan-row {
  display: flex;
  align-items: center;
  gap: 16rpx;
  padding-bottom: 20rpx;
  margin-bottom: 20rpx;
  border-bottom: 1rpx solid #f1f5f9;
}

.plan-info {
  flex: 1;
  min-width: 0;
}

.plan-name {
  font-size: 28rpx;
  font-weight: 700;
  color: #1e293b;
  display: block;
  margin-bottom: 4rpx;
}

.plan-meta {
  font-size: 22rpx;
  color: #94a3b8;
}

.plan-days {
  font-weight: 700;
  color: #2563eb;
  font-size: 26rpx;
}

.plan-arrow {
  font-size: 28rpx;
  color: #cbd5e1;
  flex-shrink: 0;
}

.completion-bar-wrap {
  background: #f8fafc;
  border-radius: 12rpx;
  padding: 20rpx;
}

.completion-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12rpx;
}

.completion-label {
  font-size: 24rpx;
  font-weight: 600;
  color: #475569;
}

.completion-pct {
  font-size: 30rpx;
  font-weight: 700;
  color: #059669;
}

.completion-track {
  height: 12rpx;
  background: #e2e8f0;
  border-radius: 6rpx;
  overflow: hidden;
  margin-bottom: 12rpx;
}

.completion-fill {
  height: 100%;
  background: #059669;
  border-radius: 6rpx;
  transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1);
}

.completion-bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.completion-done {
  font-size: 22rpx;
  color: #64748b;
}

.completion-tip {
  font-size: 22rpx;
  color: #059669;
  font-weight: 600;
}

/* 列表式菜单 */
.menu-list {
  display: flex;
  flex-direction: column;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 20rpx;
  padding: 22rpx 0;
  border-bottom: 1rpx solid #f1f5f9;
}

.menu-item:active {
  background: #f8fafc;
}

.menu-item-last {
  border-bottom: none;
}

.menu-dot {
  width: 10rpx;
  height: 10rpx;
  border-radius: 50%;
  flex-shrink: 0;
}

.menu-content {
  flex: 1;
  min-width: 0;
}

.menu-name {
  font-size: 28rpx;
  font-weight: 600;
  color: #1e293b;
  display: block;
  margin-bottom: 2rpx;
}

.menu-desc {
  font-size: 22rpx;
  color: #94a3b8;
  display: block;
}

.menu-arrow {
  font-size: 26rpx;
  color: #cbd5e1;
  flex-shrink: 0;
}

/* 空提示 */
.empty-hint {
  padding: 32rpx 0;
  text-align: center;
}

.empty-hint-text {
  font-size: 24rpx;
  color: #94a3b8;
}

/* 底部按钮 */
.footer-actions {
  margin: 40rpx 0 48rpx;
}

.sign-out-btn {
  width: 100%;
  height: 88rpx;
  line-height: 88rpx;
  background: #ffffff;
  color: #ef4444;
  border-radius: 16rpx;
  font-size: 28rpx;
  font-weight: 600;
  border: 1rpx solid #fee2e2;
}
</style>
