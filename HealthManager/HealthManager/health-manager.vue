<template>
  <view class="modern-health-page" :class="{'page-loaded': isLoaded}">
    <HealthManagerFab />

    <!-- 1. Header Section -->
    <view class="header-section stagger-1">
      <view class="user-profile">
        <view class="avatar-container">
          <image class="avatar" src="/static/healthymanager.png" mode="aspectFill"></image>
          <view class="online-dot"></view>
        </view>
        <view class="greeting">
          <text class="greeting-title">早上好，保持活力！✨</text>
          <text class="greeting-subtitle">今天也要好好照顾自己哦</text>
        </view>
      </view>
      <view class="notification-btn tap-effect">
        <image class="icon-bell" src="data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='%23334155' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9'/%3E%3Cpath d='M10.3 21a1.94 1.94 0 0 0 3.4 0'/%3E%3C/svg%3E"></image>
        <view class="red-dot"></view>
      </view>
    </view>

    <!-- 2. Dynamic Tabs -->
    <view class="tabs-container stagger-2">
      <view class="tabs-bg">
        <view class="tab-indicator" :style="{ left: activeTab * 33.33 + '%' }"></view>
        <view class="tab-item" :class="{ active: activeTab === 0 }" @click="switchTab(0)">
          <text>今日概览</text>
        </view>
        <view class="tab-item" :class="{ active: activeTab === 1 }" @click="switchTab(1)">
          <text>历史趋势</text>
        </view>
        <view class="tab-item" :class="{ active: activeTab === 2 }" @click="switchTab(2)">
          <text>健康干预</text>
        </view>
      </view>
    </view>

    <!-- 3. Tab Contents with Slide & Crossfade -->
    <view class="tab-content-wrapper">
      <!-- TAB 0: 今日概览 (Bento Box Layout) -->
      <view class="tab-content overview-tab" :class="{ 'content-active': activeTab === 0 }">
        
        <view class="bento-grid">
          <!-- Cardio Risk Radar Card (Large) -->
          <view class="bento-card cardio-card hover-glow tap-effect stagger-3">
            <view class="card-header">
              <view class="icon-box pulse-active">
                <text style="font-size:28rpx">🩺</text>
              </view>
              <text class="card-title">心血管与三高风险雷达</text>
            </view>
            <view class="card-body">
              <view class="value-row">
                <text class="main-val">低风险</text>
              </view>
              <view class="curve-mockup">
                <!-- CSS Based Curve Simulation -->
                <svg viewBox="0 0 100 20" preserveAspectRatio="none" style="width:100%; height:40rpx;">
                  <path d="M0 10 Q10 20 20 10 T40 10 T60 5 T80 15 T100 10" fill="none" class="animated-path" stroke="url(#mintGradient)" stroke-width="2" stroke-linecap="round"/>
                  <defs>
                    <linearGradient id="mintGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                      <stop offset="0%" stop-color="#34d399" />
                      <stop offset="100%" stop-color="#0284c7" />
                    </linearGradient>
                  </defs>
                </svg>
              </view>
              <text class="status-msg good-status">雷达监测：符合《健康中国2030》预期</text>
            </view>
          </view>

          <!-- BMI Card (Medium) -->
          <view class="bento-card sleep-card hover-glow tap-effect stagger-4">
            <view class="card-header">
              <view class="icon-box">
                <text style="font-size:28rpx">⚖️</text>
              </view>
              <text class="card-title">BMI 体重管理</text>
            </view>
            <view class="card-body">
              <view class="sleep-circle" style="display:flex; align-items:center; justify-content:center;">
                  <view style="text-align:center;">
                    <text class="inner-val">{{ bmi }}</text>
                    <text class="inner-unit" style="display:block; margin-top:8rpx;" :style="{color: bmiStatus.color}">{{ bmiStatus.text }}</text>
                  </view>
              </view>
              <text class="status-msg" style="text-align:center;">{{ bmiStatus.sub }}</text>
            </view>
          </view>

          <!-- Activity Rings Card (Large) -->
          <view class="bento-card activity-card hover-glow tap-effect stagger-5">
            <view class="card-header">
              <view class="icon-box">
                <image class="lucide-icon" src="data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='%23f97316' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M11.8 2H11a3 3 0 0 0-3 3v14a3 3 0 0 0 3 3h.8a3 3 0 0 0 3-3V5a3 3 0 0 0-3-3Z'/%3E%3Cpath d='M8 6H5a3 3 0 0 0-3 3v6a3 3 0 0 0 3 3h3'/%3E%3Cpath d='M16 6h3a3 3 0 0 1 3 3v6a3 3 0 0 1-3 3h-3'/%3E%3C/svg%3E"></image>
              </view>
              <text class="card-title">每日活动</text>
            </view>
            <view class="card-body activity-grid">
              <view class="act-item">
                <view class="act-bar-container">
                  <view class="act-bar fill-cal" :style="{ width: isLoaded ? '75%' : '0%' }"></view>
                </view>
                <text class="act-label">消耗 450kcal</text>
              </view>
              <view class="act-item">
                <view class="act-bar-container">
                  <view class="act-bar fill-step" :style="{ width: isLoaded ? '90%' : '0%' }"></view>
                </view>
                <text class="act-label">步数 9,200/1W</text>
              </view>
              <view class="act-item">
                <view class="act-bar-container">
                  <view class="act-bar fill-stand" :style="{ width: isLoaded ? '60%' : '0%' }"></view>
                </view>
                <text class="act-label">站立 8/12h</text>
              </view>
            </view>
          </view>
        </view> <!-- End Bento Grid -->

        <!-- Actionable Todo Cards (Medication, Water) -->
        <view class="todo-section stagger-6">
          <text class="section-title">今日待办健康</text>
          
          <view class="todo-card tap-effect" @click="toggleTodo(0)">
             <view class="todo-left">
                <view class="icon-wrap pill-icon hover-bounce">💊</view>
                <view class="todo-info">
                  <text class="info-title" :class="{ 'tx-del': todos[0].done }">服用综合维生素</text>
                  <text class="info-sub">早餐后 1粒</text>
                </view>
             </view>
             <view class="checkbox-wrap">
                <view class="custom-checkbox" :class="{ checked: todos[0].done }">
                  <text v-if="todos[0].done" class="check-mark">✓</text>
                </view>
             </view>
          </view>

          <view class="todo-card tap-effect" @click="toggleTodo(1)">
             <view class="todo-left">
                <view class="icon-wrap water-icon hover-float">💧</view>
                <view class="todo-info">
                  <text class="info-title" :class="{ 'tx-del': todos[1].done }">喝水打卡 (4/8 杯)</text>
                  <text class="info-sub">距离目标还差 800ml</text>
                </view>
             </view>
             <view class="checkbox-wrap">
                <view class="custom-checkbox" :class="{ checked: todos[1].done }">
                  <text v-if="todos[1].done" class="check-mark">✓</text>
                </view>
             </view>
          </view>
        </view>

      </view> <!-- End Tab 0 -->

      <!-- TAB 1: 历史趋势 (Trend Tab) -->
      <view class="tab-content trend-tab" :class="{ 'content-active': activeTab === 1 }">
        
        <!-- Report Period Switcher -->
        <view class="report-switcher stagger-3">
          <view class="switch-item tap-effect" :class="{ active: reportView === 'weekly' }" @click="reportView = 'weekly'">近七天</view>
          <view class="switch-item tap-effect" :class="{ active: reportView === 'monthly' }" @click="reportView = 'monthly'">近三月</view>
        </view>

        <view v-if="reportView === 'weekly'">
          <!-- Humanized Insight -->
          <view class="human-insight-card hover-glow stagger-4">
            <view class="insight-avatar-row">
              <image class="insight-avatar" src="/static/healthymanager.png" mode="aspectFill"></image>
              <view class="insight-bubble">
                <text class="bubble-text">这周睡眠质量比上周好多了！继续保持哦 🌙</text>
              </view>
            </view>
            <view class="insight-tags">
              <text class="tag positive">睡眠 +1.5h</text>
              <text class="tag warning">步数 -500</text>
            </view>
          </view>

          <!-- Weekly Trend Chart -->
          <view class="bento-card stagger-5">
            <view class="card-header">
              <view class="icon-box">
                <image class="lucide-icon" src="data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='%233b82f6' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M3 3v18h18'/%3E%3Cpath d='m19 9-5 5-4-4-3 3'/%3E%3C/svg%3E"></image>
              </view>
              <text class="card-title">近七天体重变化</text>
            </view>
            <view class="trend-chart-box">
              <view class="chart-bars-container">
                <view class="chart-col" v-for="(day, d) in weeklyTrend" :key="d">
                  <view class="chart-bar-fill" :style="{ height: isLoaded ? day.value + '%' : '0%' }"></view>
                  <text class="chart-day">{{ day.label }}</text>
                </view>
              </view>
            </view>
          </view>

          <!-- Actionable Advice -->
          <view class="action-card hover-glow tap-effect stagger-6" @click="acceptChallenge">
            <text class="action-title">💡 明日小建议</text>
            <text class="action-desc">数据显示您最近久坐较多。试着明天每工作1小时，起来接杯水走动一下？</text>
            <view class="challenge-btn">好的，我试试</view>
          </view>
        </view>

        <view v-if="reportView === 'monthly'">
          <!-- Annual Summary Banner -->
          <view class="annual-banner hover-glow tap-effect stagger-4" @click="showAnnualReport">
            <view class="banner-content">
              <text class="banner-title">✨ 2025 健康总结</text>
              <text class="banner-subtitle">点击查看您的健康里程碑</text>
            </view>
            <image class="lucide-icon" style="opacity:0.8" src="data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='%23ffffff' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M5 12h14'/%3E%3Cpath d='m12 5 7 7-7 7'/%3E%3C/svg%3E"></image>
          </view>

          <!-- Monthly Trend Box -->
          <view class="bento-grid" style="margin-bottom:0px;">
            <view class="bento-card cardio-card hover-glow stagger-5">
              <view class="card-header">
                <view class="icon-box"><text style="font-size:28rpx">📉</text></view>
                <text class="card-title">体重趋势</text>
              </view>
              <view class="chart-container-monthly">
                 <view class="month-bar-group" v-for="(m, i) in monthlyData" :key="'w'+i">
                   <view class="month-bar" :style="{ height: isLoaded ? m.value + '%' : '0%' }"></view>
                   <text class="month-label">{{ m.month }}</text>
                 </view>
              </view>
              <text class="status-msg good-status">总体呈现下降趋势，减轻 2.5kg</text>
            </view>

            <view class="bento-card activity-card hover-glow stagger-6">
              <view class="card-header">
                <view class="icon-box"><text style="font-size:28rpx">🏃</text></view>
                <text class="card-title">运动活跃度</text>
              </view>
              <view class="chart-container-monthly">
                 <view class="month-bar-group" v-for="(m, i) in monthlyActivity" :key="'a'+i">
                   <view class="month-bar activity" :style="{ height: isLoaded ? m.value + '%' : '0%' }"></view>
                   <text class="month-label">{{ m.month }}</text>
                 </view>
              </view>
              <text class="status-msg">12月运动量显著增加！</text>
            </view>
          </view>
        </view>
      </view> <!-- End Tab 1 -->

      <!-- TAB 2: 健康干预 (Intervention Tab) -->
      <view class="tab-content intervene-tab" :class="{ 'content-active': activeTab === 2 }">
        
        <!-- Dietary Decision Slider -->
        <view class="bento-card hover-glow stagger-3" style="padding: 24rpx 0;">
          <view class="card-header" style="padding: 0 32rpx;">
            <view class="icon-box">
              <text style="font-size:28rpx">🥗</text>
            </view>
            <view>
               <text class="card-title" style="display:block;">智能饮食推荐</text>
               <text style="font-size:20rpx; color:#94a3b8; font-weight: 500;">解决点餐困难 响应《国民营养计划》</text>
            </view>
          </view>
          
          <scroll-view scroll-x class="template-scroll" show-scrollbar="false">
            <view class="template-container">
              <view class="template-card tap-effect" v-for="(tpl, index) in goalTemplates" :key="index" @click="applyTemplate(tpl)">
                <text class="tpl-icon">{{ tpl.icon }}</text>
                <text class="tpl-name">{{ tpl.name }}</text>
                <text class="tpl-desc">{{ tpl.desc }}</text>
                <view class="tpl-btn">一键推荐菜谱/餐厅</view>
              </view>
            </view>
          </scroll-view>
        </view>

        <!-- Multi-Agent Hub -->
        <view class="bento-card hover-glow stagger-4">
          <view class="card-header">
            <view class="icon-box">
              <text style="font-size:28rpx">🤖</text>
            </view>
            <view>
              <text class="card-title" style="display:block;">多智能体专家联合会诊</text>
              <text style="font-size:20rpx; color:#94a3b8; font-weight: 500;">全方位分析与预防慢性疾病</text>
            </view>
          </view>
          <view class="agent-list" style="display:flex; flex-direction:column; gap:20rpx; margin-top:16rpx;">
            <view class="agent-item tap-effect" v-for="(agent, i) in agents" :key="i" style="display:flex; align-items:center; background:#f8fafc; padding:20rpx; border-radius:24rpx; gap:24rpx; transition:transform 0.2s;">
              <view class="agent-icon-box" :style="{background: agent.color + '20', color: agent.color}" style="width:80rpx; height:80rpx; border-radius:20rpx; display:flex; align-items:center; justify-content:center; font-size:40rpx;">
                {{ agent.icon }}
              </view>
              <view class="agent-info" style="flex:1;">
                <text style="display:block; font-size:28rpx; font-weight:700; color:#334155; margin-bottom:4rpx;">{{ agent.name }}</text>
                <text style="font-size:22rpx; color:#64748b; font-weight: 500;">{{ agent.role }}</text>
              </view>
              <view class="agent-status" :style="{color: agent.color, background: agent.color + '15'}" style="font-size:22rpx; font-weight:600; padding:8rpx 16rpx; border-radius:30rpx;">
                {{ agent.status }}
              </view>
            </view>
          </view>
        </view>

      </view> <!-- End Tab 2 -->

    </view> <!-- End Content Wrapper -->
  </view>
</template>

<script>
// 使用 Options API 以最大化兼容现有应用结构
import HealthManagerFab from '@/components/HealthManagerFab/HealthManagerFab.vue'

export default {
  components: {
    HealthManagerFab
  },
  data() {
    return {
      isLoaded: false,
      activeTab: 0,
      reportView: 'weekly',
      userInfo: {
        height: 175,
        weight: 68
      },
      agents: [
        { name: '营养学智能体', role: '膳食结构优化', status: '护航中', icon: '🥗', color: '#10b981' },
        { name: '运动学智能体', role: '心肺功能提升', status: '待命', icon: '🏃', color: '#3b82f6' },
        { name: '慢病管理智能体', role: '三高风险预警', status: '监测中', icon: '🩺', color: '#f59e0b' }
      ],
      todos: [
        { id: 1, done: false },
        { id: 2, done: false }
      ],
      weeklyTrend: [
        { label: '一', value: 60 },
        { label: '二', value: 80 },
        { label: '三', value: 45 },
        { label: '四', value: 90 },
        { label: '五', value: 70 },
        { label: '六', value: 50 },
        { label: '日', value: 75 }
      ],
      monthlyData: [
        { month: '10月', value: 80 },
        { month: '11月', value: 70 },
        { month: '12月', value: 60 }
      ],
      monthlyActivity: [
        { month: '10月', value: 40 },
        { month: '11月', value: 55 },
        { month: '12月', value: 85 }
      ],
      goalTemplates: [
        { name: '减脂塑形', icon: '🔥', desc: '低碳高蛋白，燃脂首选' },
        { name: '增肌强体', icon: '💪', desc: '高热量高蛋白，快速增肌' },
        { name: '均衡养生', icon: '🥗', desc: '均衡营养，保持健康活力' }
      ],
      achievements: [
        { name: '零基础', icon: '🌱', unlocked: true },
        { name: '七日连胜', icon: '🔥', unlocked: true },
        { name: '减脂达人', icon: '🏃', unlocked: false },
        { name: '早起冠军', icon: '☀️', unlocked: false }
      ]
    }
  },
  computed: {
    bmi() {
      const h = this.userInfo.height / 100;
      return (this.userInfo.weight / (h * h)).toFixed(1);
    },
    bmiStatus() {
      const bmi = parseFloat(this.bmi);
      if (bmi < 18.5) return { text: '体重过低', color: '#f59e0b', sub: '需加强营养补充' };
      if (bmi < 24) return { text: '标准健康', color: '#10b981', sub: '卫健委推荐区间' };
      if (bmi < 28) return { text: '超重预警', color: '#f97316', sub: '注意心血管风险' };
      return { text: '肥胖预警', color: '#ef4444', sub: '建议进行科学减重' };
    }
  },
  mounted() {
    // 触发进度条、圆环的缓动加载动画
    setTimeout(() => {
      this.isLoaded = true;
    }, 100);
  },
  methods: {
    switchTab(index) {
      if (this.activeTab !== index) {
        this.activeTab = index;
        uni.vibrateShort && uni.vibrateShort(); // Haptic feedback if available
      }
    },
    toggleTodo(index) {
      this.todos[index].done = !this.todos[index].done;
      uni.vibrateShort && uni.vibrateShort();
    },
    acceptChallenge() {
      uni.showToast({ title: '已加入挑战！明天提醒您', icon: 'success' });
    },
    showAnnualReport() {
      uni.showModal({
        title: '年度总结',
        content: '这里将展示您的年度健康数据，包括总步数、总消耗热量、体重变化曲线等。（功能开发中）',
        showCancel: false
      });
    },
    applyTemplate(tpl) {
      uni.showModal({
        title: '确认应用计划？',
        content: tpl.desc,
        success: (res) => {
          if (res.confirm) {
            uni.showToast({ title: '已应用' + tpl.name, icon: 'success' });
          }
        }
      });
    }
  }
}
</script>

<style scoped>
/* ==========================================================
   Modern "Personal Health Center" UI (Bento + Glassmorphism)
   Author: UI/UX Expert AI
   Theme: Mint Green & Ocean Blue Gradient, Bright/Clean White
========================================================== */

/* 1. Global Page Style */
.modern-health-page {
  min-height: 100vh;
  background-color: #F8FAFC; /* Warm Slate Gray */
  padding: 100rpx 32rpx 200rpx 32rpx;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  overflow-x: hidden;
}

/* 2. Header Section */
.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 48rpx;
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 24rpx;
}

.avatar-container {
  position: relative;
  width: 96rpx;
  height: 96rpx;
  border-radius: 50%;
  padding: 4rpx; /* border space */
  background: linear-gradient(135deg, #10b981 0%, #0ea5e9 100%);
}

.avatar {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background-color: white;
  border: 4rpx solid white;
}

.online-dot {
  position: absolute;
  bottom: 4rpx;
  right: 4rpx;
  width: 20rpx;
  height: 20rpx;
  background-color: #10b981; /* Emerald */
  border: 4rpx solid white;
  border-radius: 50%;
}

.greeting {
  display: flex;
  flex-direction: column;
}

.greeting-title {
  font-size: 36rpx;
  font-weight: 700;
  color: #0f172a;
  letter-spacing: -0.5rpx;
}

.greeting-subtitle {
  font-size: 24rpx;
  color: #64748b;
  margin-top: 4rpx;
}

.notification-btn {
  position: relative;
  width: 80rpx;
  height: 80rpx;
  background-color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8rpx 24rpx rgba(148, 163, 184, 0.15); /* Soft drop shadow */
}

.icon-bell {
  width: 44rpx;
  height: 44rpx;
}

.red-dot {
  position: absolute;
  top: 20rpx;
  right: 22rpx;
  width: 12rpx;
  height: 12rpx;
  background-color: #ef4444; /* Red 500 */
  border-radius: 50%;
  border: 2rpx solid white;
}

/* 3. Dynamic Tabs */
.tabs-container {
  margin-bottom: 40rpx;
}

.tabs-bg {
  position: relative;
  display: flex;
  background-color: #e2e8f0; /* Slate 200 */
  border-radius: 999px;
  padding: 8rpx;
  box-shadow: inset 0 2rpx 4rpx rgba(0,0,0,0.05); /* Inner subtle shadow */
}

.tab-indicator {
  position: absolute;
  top: 8rpx;
  bottom: 8rpx;
  width: 33.33%;
  background-color: white;
  border-radius: 999px;
  box-shadow: 0 4rpx 12rpx rgba(15, 23, 42, 0.08);
  transition: left 0.4s cubic-bezier(0.34, 1.56, 0.64, 1); /* Bouncy slide easing */
}

.tab-item {
  flex: 1;
  text-align: center;
  padding: 16rpx 0;
  z-index: 1; /* Above indicator */
  position: relative;
}

.tab-item text {
  font-size: 26rpx;
  font-weight: 600;
  color: #64748b;
  transition: color 0.3s;
}

.tab-item.active text {
  color: #0f172a;
}

/* 4. Tab Content Sliding & Crossfade */
.tab-content-wrapper {
  position: relative;
}

.tab-content {
  display: none;
  opacity: 0;
  transform: translateY(20rpx);
  transition: all 0.4s ease;
}

.content-active {
  display: block; /* Vue v-if completely destroys DOM, display:none allows pure CSS transitions (or use transition-group). We use v-if implicitly by managing classes, but here we just use display none/block toggle */
  animation: tabFadeIn 0.5s forwards cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes tabFadeIn {
  from { opacity: 0; transform: translateY(30rpx) scale(0.98); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}

/* 5. Bento Grid Layout */
.bento-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-auto-rows: minMax(min-content, max-content);
  gap: 24rpx;
  margin-bottom: 40rpx;
}

.bento-card {
  background: white;
  border-radius: 40rpx; /* 3xl large corners */
  padding: 32rpx;
  box-shadow: 0 16rpx 40rpx rgba(148, 163, 184, 0.1); /* Soft, large diffuse shadow */
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

/* Hover Micro-interactions (Visible on PC/Web, degrade gracefully on Mobile) */
@media (hover: hover) {
  .hover-glow:hover {
    transform: translateY(-4rpx) scale(1.02);
    box-shadow: 0 24rpx 48rpx rgba(16, 185, 129, 0.15); /* Mint green tint shadow */
  }
}

/* Active Tap Effect (for Mobile) */
.tap-effect:active {
  transform: scale(0.96);
  transition: transform 0.1s ease;
}

/* Bento Card Elements */
.card-header {
  display: flex;
  align-items: center;
  gap: 16rpx;
  margin-bottom: 24rpx;
}

.icon-box {
  width: 56rpx;
  height: 56rpx;
  background-color: #f1f5f9;
  border-radius: 16rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.lucide-icon {
  width: 32rpx;
  height: 32rpx;
}

.lucide-icon.large { width: 96rpx; height: 96rpx; margin-bottom: 20rpx; opacity: 0.5; }

.card-title {
  font-size: 28rpx;
  font-weight: 700;
  color: #334155;
}

/* Specific Cards Layout */
.cardio-card {
  grid-column: span 2;
  background: linear-gradient(135deg, #ffffff 0%, #f0fdf4 100%); /* Slight green literal tint */
}

.sleep-card {
  grid-column: span 1;
}

.activity-card {
  grid-column: span 1;
  background: linear-gradient(135deg, #ffffff 0%, #fff7ed 100%); /* Slight orange tint */
}

.value-row { display: flex; align-items: baseline; gap: 8rpx; }
.main-val { font-size: 64rpx; font-weight: 800; color: #0f172a; line-height: 1; }
.unit { font-size: 28rpx; font-weight: 600; color: #94a3b8; }

.status-msg { font-size: 22rpx; color: #64748b; font-weight: 500; margin-top: 16rpx; display: block; }
.good-status { color: #10b981; }

/* SVG Curve Animation */
.curve-mockup { width: 100%; margin: 16rpx 0; }
.animated-path {
  stroke-dasharray: 200;
  stroke-dashoffset: 200;
  animation: drawLine 2s ease-out forwards 0.5s;
}
@keyframes drawLine { to { stroke-dashoffset: 0; } }

/* Pulse Animation for Heart rate */
@keyframes heartPulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.15); }
  100% { transform: scale(1); }
}
.pulse-active image { animation: heartPulse 1.5s infinite ease-in-out; }

/* Circular Progress for Sleep */
.sleep-circle {
  position: relative;
  width: 140rpx;
  height: 140rpx;
  margin: 0 auto;
}
.circle-progress {
  width: 100%; height: 100%; border-radius: 50%;
  transition: background 1.5s cubic-bezier(0.4, 0, 0.2, 1);
}
.circle-inner {
  position: absolute; top: 10rpx; left: 10rpx; right: 10rpx; bottom: 10rpx;
  background: white; border-radius: 50%;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  box-shadow: inset 0 4rpx 10rpx rgba(0,0,0,0.05);
}
.inner-val { font-size: 36rpx; font-weight: 800; color: #0f172a; line-height: 1; }
.inner-unit { font-size: 20rpx; color: #94a3b8; font-weight: 600; }

/* Activity Progress Bars */
.activity-grid { display: flex; flex-direction: column; gap: 20rpx; }
.act-item { display: flex; flex-direction: column; gap: 8rpx; }
.act-bar-container { width: 100%; height: 16rpx; background: #e2e8f0; border-radius: 8rpx; overflow: hidden; }
.act-bar { height: 100%; border-radius: 8rpx; transition: width 1.5s cubic-bezier(0.22, 1, 0.36, 1); }
.fill-cal { background-color: #f97316; } /* Orange */
.fill-step { background-color: #10b981; } /* Emerald */
.fill-stand { background-color: #0ea5e9; } /* Sky Blue */
.act-label { font-size: 20rpx; font-weight: 600; color: #64748b; }

/* 6. Actionable Todo Cards (Glassmorphic) */
.todo-section { margin-top: 16rpx; }
.section-title { font-size: 32rpx; font-weight: 700; color: #0f172a; margin-bottom: 24rpx; display: block; }

.todo-card {
  background: rgba(255, 255, 255, 0.7); /* Glassmorphism base */
  backdrop-filter: blur(16px);
  border: 2rpx solid rgba(255, 255, 255, 0.5);
  border-radius: 32rpx;
  padding: 32rpx;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24rpx;
  box-shadow: 0 8rpx 32rpx rgba(15, 23, 42, 0.05);
  transition: all 0.2s ease;
}

.todo-left { display: flex; align-items: center; gap: 24rpx; }

.icon-wrap {
  width: 80rpx; height: 80rpx; border-radius: 20rpx;
  display: flex; align-items: center; justify-content: center; font-size: 36rpx;
}
.pill-icon { background-color: #fce7f3; color: #db2777; }
.water-icon { background-color: #e0f2fe; color: #0284c7; }

@keyframes float { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-4rpx); } }
.hover-float { animation: float 3s ease-in-out infinite; }
@keyframes pop { 50% { transform: scale(1.1); } }
.hover-bounce { animation: pop 2s ease-in-out infinite; }

.todo-info { display: flex; flex-direction: column; gap: 4rpx; }
.info-title { font-size: 30rpx; font-weight: 700; color: #334155; transition: color 0.3s; }
.info-sub { font-size: 24rpx; color: #94a3b8; font-weight: 500; }
.tx-del { text-decoration: line-through; color: #cbd5e1; }

.checkbox-wrap { padding: 10rpx; }
.custom-checkbox {
  width: 48rpx; height: 48rpx; border-radius: 12rpx;
  border: 4rpx solid #cbd5e1; background-color: transparent;
  display: flex; align-items: center; justify-content: center;
  transition: all 0.2s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.custom-checkbox.checked {
  background-color: #10b981; border-color: #10b981;
  transform: scale(1.1); /* Pop effect on check */
}
.check-mark { color: white; font-weight: bold; font-size: 28rpx; }

/* Placeholder Tabs */
.empty-state {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  padding: 100rpx 0; opacity: 0.8;
}
.empty-text { margin-top: 24rpx; font-size: 28rpx; color: #94a3b8; font-weight: 500; }

/* ===== TAB 1: History Trend Styles ===== */
.report-switcher {
  display: flex; background: white; border-radius: 20rpx; padding: 10rpx;
  margin-bottom: 32rpx; box-shadow: 0 4rpx 16rpx rgba(15,23,42,0.05);
}
.switch-item {
  flex: 1; text-align: center; padding: 16rpx; border-radius: 16rpx;
  font-size: 26rpx; color: #64748b; font-weight: 500; transition: all 0.3s;
}
.switch-item.active { background: #eff6ff; color: #3b82f6; font-weight: 700; }

.human-insight-card {
  background: white; border-radius: 32rpx; padding: 32rpx; margin-bottom: 24rpx;
  box-shadow: 0 12rpx 32rpx rgba(15,23,42,0.05); transition: all 0.3s;
}
.insight-avatar-row { display: flex; align-items: flex-start; gap: 24rpx; margin-bottom: 24rpx; }
.insight-avatar { width: 96rpx; height: 96rpx; border-radius: 50%; border: 4rpx solid #e0e7ff; }
.insight-bubble {
  flex: 1; background: #f8fafc; border-radius: 0 32rpx 32rpx 32rpx; padding: 24rpx;
}
.bubble-text { font-size: 28rpx; color: #334155; line-height: 1.5; font-weight: 500;}
.insight-tags { display: flex; gap: 16rpx; }
.tag { font-size: 22rpx; padding: 8rpx 20rpx; border-radius: 30rpx; font-weight: 600; }
.tag.positive { background: #dcfce7; color: #166534; }
.tag.warning { background: #fef3c7; color: #b45309; }

.trend-chart-box { height: 280rpx; margin-top: 16rpx; }
.chart-bars-container { display: flex; height: 100%; align-items: flex-end; justify-content: space-between; padding-top: 20rpx;}
.chart-col { display: flex; flex-direction: column; align-items: center; gap: 16rpx; flex: 1; height: 100%; justify-content: flex-end; }
.chart-bar-fill { width: 24rpx; background: #e2e8f0; border-radius: 12rpx; transition: height 1s cubic-bezier(0.16, 1, 0.3, 1); }
.chart-col:nth-child(odd) .chart-bar-fill { background: #3b82f6; }
.chart-day { font-size: 22rpx; color: #64748b; font-weight: 500;}

.action-card {
  background: linear-gradient(135deg, #3b82f6 0%, #1e40af 100%);
  border-radius: 32rpx; padding: 32rpx; margin-bottom: 32rpx; color: white;
  box-shadow: 0 16rpx 32rpx rgba(37,99,235,0.2);
}
.action-title { font-size: 32rpx; font-weight: bold; margin-bottom: 16rpx; display: block; }
.action-desc { font-size: 26rpx; opacity: 0.9; margin-bottom: 32rpx; display: block; line-height: 1.6; }
.challenge-btn {
  background: white; color: #1e3a8a; text-align: center; padding: 20rpx;
  border-radius: 20rpx; font-weight: 700; font-size: 28rpx;
}

.annual-banner {
  background: linear-gradient(135deg, #f59e0b 0%, #ea580c 100%);
  padding: 32rpx; border-radius: 32rpx; margin-bottom: 24rpx;
  display: flex; justify-content: space-between; align-items: center;
  color: white; box-shadow: 0 16rpx 32rpx rgba(245, 158, 11, 0.25);
}
.banner-title { font-size: 32rpx; font-weight: bold; margin-bottom: 8rpx; display: block; }
.banner-subtitle { font-size: 24rpx; opacity: 0.9; }

.chart-container-monthly {
  height: 200rpx; display: flex; align-items: flex-end; justify-content: space-around; margin: 24rpx 0;
}
.month-bar-group { display: flex; flex-direction: column; align-items: center; gap: 12rpx; height: 100%; justify-content: flex-end; }
.month-bar { width: 48rpx; background: #93c5fd; border-radius: 12rpx; transition: height 1s cubic-bezier(0.16, 1, 0.3, 1);}
.month-bar.activity { background: #34d399; }
.month-label { font-size: 24rpx; color: #64748b; font-weight: 500;}

/* ===== TAB 2: Interventions / Goals ===== */
.template-scroll { width: 100%; white-space: nowrap; margin-bottom: 10rpx; }
.template-container { display: flex; gap: 24rpx; padding: 10rpx 32rpx 32rpx 32rpx; }
.template-card {
  display: inline-flex; flex-direction: column; background: #f8fafc;
  width: 280rpx; padding: 24rpx; border-radius: 32rpx; border: 4rpx solid transparent;
  box-shadow: 0 8rpx 20rpx rgba(15,23,42,0.04); transition: transform 0.2s;
}
.template-card:active { border-color: #3b82f6; transform: scale(0.96); }
.tpl-icon { font-size: 48rpx; margin-bottom: 16rpx;}
.tpl-name { font-size: 30rpx; font-weight: 800; color: #0f172a; margin-bottom: 8rpx; }
.tpl-desc { font-size: 22rpx; color: #64748b; white-space: normal; line-height: 1.4; margin-bottom: 24rpx; flex: 1; }
.tpl-btn { background: #eff6ff; color: #3b82f6; font-size: 24rpx; font-weight: 700; text-align: center; padding: 16rpx; border-radius: 16rpx;}

.badge-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 24rpx; margin-top: 16rpx;}
.badge-item { display: flex; flex-direction: column; align-items: center; gap: 12rpx; }
.badge-icon-box {
  width: 100rpx; height: 100rpx; border-radius: 50%; background: #fefce8; border: 4rpx solid #fef08a;
  display: flex; align-items: center; justify-content: center; box-shadow: 0 8rpx 16rpx rgba(250,204,21,0.2);
}
.badge-icon { font-size: 48rpx; }
.badge-name { font-size: 22rpx; font-weight: 600; color: #334155; text-align: center; }
.badge-item.locked .badge-icon-box { background: #f1f5f9; border-color: #e2e8f0; filter: grayscale(1); box-shadow: none; opacity: 0.5;}
.badge-item.locked .badge-name { color: #94a3b8; }

/* 7. Advanced Staggered Animations */
.stagger-1 { opacity: 0; animation: fadeInUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) 0.05s forwards; }
.stagger-2 { opacity: 0; animation: fadeInUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) 0.1s forwards; }
.stagger-3 { opacity: 0; animation: fadeInUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) 0.15s forwards; }
.stagger-4 { opacity: 0; animation: fadeInUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) 0.2s forwards; }
.stagger-5 { opacity: 0; animation: fadeInUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) 0.25s forwards; }
.stagger-6 { opacity: 0; animation: fadeInUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) 0.3s forwards; }

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(40rpx); }
  to { opacity: 1; transform: translateY(0); }
}
</style>