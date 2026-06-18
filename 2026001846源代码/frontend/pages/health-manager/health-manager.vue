<template>
  <view class="hm-page">
    <!-- 顶部导航栏 -->
    <view class="hm-navbar">
      <view class="hm-navbar-inner">
        <view class="hm-logo-circle">
          <text class="hm-logo-text">WS</text>
        </view>
        <view class="hm-title-block">
          <text class="hm-main-title">设备检修智能工作台</text>
          <text class="hm-sub-title">多模态检索 · 智能问修 · 标准作业 · 知识沉淀</text>
        </view>
      </view>
    </view>

    <!-- Tab栏 -->
    <view class="hm-tabs">
      <view
        v-for="(tab, idx) in tabs"
        :key="idx"
        class="hm-tab-item"
        :class="{ active: activeTab === idx }"
        @click="activeTab = idx"
      >
        <text class="hm-tab-text">{{ tab }}</text>
      </view>
    </view>

    <scroll-view class="hm-scroll" scroll-y :show-scrollbar="false">

      <!-- === TAB 0: 今日任务 === -->
      <view v-if="activeTab === 0" class="hm-content">
        
        <!-- 任务闭环率卡片 -->
        <view class="hm-closure-card">
          <view class="hm-closure-left">
            <text class="hm-closure-label">任务闭环率</text>
            <text class="hm-closure-value">85%</text>
            <text class="hm-closure-desc">实时统计 · 任务达成与闭环综合表现</text>
            <view class="hm-closure-badges">
              <view class="hm-badge hm-badge-orange">
                <text>⚠ 2项高风险</text>
              </view>
              <view class="hm-badge hm-badge-red">
                <text>⏱ 1项超时</text>
              </view>
            </view>
          </view>
          <view class="hm-closure-right">
            <view class="hm-ring-progress">
              <view class="hm-ring-outer">
                <view class="hm-ring-inner">
                  <text class="hm-ring-text">85%</text>
                </view>
              </view>
            </view>
          </view>
        </view>

        <!-- 统计卡片 -->
        <view class="hm-stats-grid">
          <view class="hm-stat-card">
            <view class="hm-stat-icon hm-icon-blue">
              <text>📋</text>
            </view>
            <text class="hm-stat-num">5</text>
            <text class="hm-stat-label">待处理</text>
          </view>
          <view class="hm-stat-card">
            <view class="hm-stat-icon hm-icon-orange">
              <text>🔧</text>
            </view>
            <text class="hm-stat-num">3</text>
            <text class="hm-stat-label">进行中</text>
          </view>
          <view class="hm-stat-card">
            <view class="hm-stat-icon hm-icon-gray">
              <text>✅</text>
            </view>
            <text class="hm-stat-num">4</text>
            <text class="hm-stat-label">待复检</text>
          </view>
          <view class="hm-stat-card">
            <view class="hm-stat-icon hm-icon-green">
              <text>🏁</text>
            </view>
            <text class="hm-stat-num">12</text>
            <text class="hm-stat-label">已完成</text>
          </view>
        </view>

        <!-- 搜索栏 -->
        <view class="hm-search-section">
          <view class="hm-search-box">
            <text>🔍</text>
            <input class="hm-search-input" placeholder="搜索设备/故障/负责人" placeholder-class="hm-search-placeholder" />
          </view>
          <view class="hm-filter-tags">
            <view class="hm-filter-tag" :class="{ active: filterHighRisk }" @click="filterHighRisk = !filterHighRisk">
              <text>高风险</text>
            </view>
            <view class="hm-filter-tag" :class="{ active: filterOvertime }" @click="filterOvertime = !filterOvertime">
              <text>超时</text>
            </view>
          </view>
        </view>

        <!-- 任务卡片列表 -->
        <view class="hm-task-list">
          <view class="hm-task-card" v-for="(task, idx) in taskList" :key="idx">
            <view class="hm-task-header">
              <view class="hm-task-type-tag" :class="'type-' + task.typeColor">
                <text>{{ task.taskType }}</text>
              </view>
              <text class="hm-task-title">{{ task.title }}</text>
              <view class="hm-task-status" :class="'status-' + task.statusColor">
                <text>{{ task.status }}</text>
              </view>
            </view>
            <view class="hm-task-tags">
              <view class="hm-chip" :class="'chip-' + task.equipmentColor">
                <text>📦 {{ task.equipment }}</text>
              </view>
              <view class="hm-chip chip-red">
                <text>🔥 {{ task.fault }}</text>
              </view>
            </view>
            <view class="hm-task-meta">
              <text class="hm-meta-item">⚡ {{ task.level }}</text>
              <text class="hm-meta-item" :class="'risk-' + task.riskColor">{{ task.risk }}</text>
              <text class="hm-meta-item">📥 {{ task.source }}</text>
              <text class="hm-meta-item">👤 {{ task.leader }}</text>
              <text class="hm-meta-item">⏰ {{ task.deadline }}</text>
            </view>
            <view class="hm-task-actions">
              <view class="hm-btn hm-btn-outline" @click="viewTaskDetail(task)">
                <text>查看详情</text>
              </view>
              <view class="hm-btn hm-btn-primary" @click="startTask(task)">
                <text>开始作业</text>
              </view>
            </view>
          </view>
        </view>

      </view>

      <!-- === TAB 1: 复检评估 === -->
      <view v-if="activeTab === 1" class="hm-content">
        
        <!-- 复检通过率卡片 -->
        <view class="hm-pass-rate-card">
          <view class="hm-pass-left">
            <text class="hm-pass-label">复检通过率</text>
            <view class="hm-pass-row">
              <text class="hm-pass-value">92%</text>
              <text class="hm-pass-trend">↑ 5%</text>
            </view>
            <view class="hm-pass-bar">
              <view class="hm-pass-bar-fill"></view>
            </view>
          </view>
        </view>

        <!-- 任务闭环趋势 -->
        <view class="hm-trend-card">
          <view class="hm-trend-header">
            <text class="hm-trend-title">任务闭环趋势</text>
            <view class="hm-trend-tabs">
              <view class="hm-trend-tab" :class="{ active: trendPeriod === '7' }" @click="trendPeriod = '7'">近7天</view>
              <view class="hm-trend-tab" :class="{ active: trendPeriod === '30' }" @click="trendPeriod = '30'">近30天</view>
            </view>
          </view>
          <view class="hm-trend-chart">
            <view class="hm-trend-bars">
              <view v-for="(item, idx) in trendData" :key="idx" class="hm-trend-bar-item">
                <view class="hm-trend-bar" :style="{ height: item.value + '%' }"></view>
                <text class="hm-trend-day">{{ item.day }}</text>
              </view>
            </view>
          </view>
        </view>

        <!-- 返工问题列表 -->
        <view class="hm-issue-card">
          <view class="hm-issue-header">
            <text class="hm-issue-title">返工问题列表</text>
            <text class="hm-issue-count">2项</text>
          </view>
          <view class="hm-issue-list">
            <view class="hm-issue-item" v-for="(issue, idx) in issueList" :key="idx">
              <view class="hm-issue-line" :class="'line-' + issue.lineColor"></view>
              <view class="hm-issue-content">
                <text class="hm-issue-name">{{ issue.name }}</text>
                <text class="hm-issue-desc">{{ issue.desc }}</text>
                <text class="hm-issue-meta">{{ issue.meta }}</text>
              </view>
              <view class="hm-issue-status" :class="'issue-' + issue.statusColor">
                <text>{{ issue.status }}</text>
              </view>
            </view>
          </view>
        </view>

        <!-- 风险解除情况 -->
        <view class="hm-risk-card">
          <view class="hm-risk-header">
            <text class="hm-risk-title">风险解除情况</text>
          </view>
          <view class="hm-risk-stats">
            <view class="hm-risk-stat-item">
              <text class="hm-risk-num red">8</text>
              <text class="hm-risk-label">风险总数</text>
            </view>
            <view class="hm-risk-stat-item">
              <text class="hm-risk-num orange">6</text>
              <text class="hm-risk-label">已解除</text>
            </view>
            <view class="hm-risk-stat-item">
              <text class="hm-risk-num green">75%</text>
              <text class="hm-risk-label">解除率</text>
            </view>
          </view>
          <view class="hm-risk-list">
            <view class="hm-risk-item" v-for="(risk, idx) in riskList" :key="idx">
              <view class="hm-risk-icon" :class="'risk-icon-' + risk.iconColor">
                <text>{{ risk.icon }}</text>
              </view>
              <view class="hm-risk-info">
                <text class="hm-risk-name">{{ risk.name }}</text>
                <text class="hm-risk-time">{{ risk.time }}</text>
              </view>
              <view class="hm-risk-status" :class="'risk-status-' + risk.statusColor">
                <text>{{ risk.status }}</text>
              </view>
            </view>
          </view>
        </view>

      </view>

      <!-- === TAB 2: 协同处理 === -->
      <view v-if="activeTab === 2" class="hm-content">
        
        <!-- 协作团队头部 -->
        <view class="hm-team-card">
          <view class="hm-team-info">
            <text class="hm-team-title">检修协作团队</text>
            <text class="hm-team-desc">设备检修知识作业系统 · 团队协作与实时沟通</text>
          </view>
          <view class="hm-team-status">
            <text class="hm-team-online">● 3人在线</text>
          </view>
        </view>

        <!-- 搜索框 -->
        <view class="hm-team-search">
          <text>🔍</text>
          <input class="hm-team-search-input" placeholder="搜索同事/岗位/设备" placeholder-class="hm-search-placeholder" />
        </view>

        <!-- 联系人列表 -->
        <view class="hm-contact-list">
          <view class="hm-contact-item" v-for="(contact, idx) in contactList" :key="idx" @click="goToChat(contact)">
            <view class="hm-contact-avatar" :class="'avatar-' + contact.avatarColor">
              <text>{{ contact.avatar }}</text>
            </view>
            <view class="hm-contact-status-dot" :class="'dot-' + contact.online"></view>
            <view class="hm-contact-content">
              <view class="hm-contact-name-row">
                <text class="hm-contact-name">{{ contact.name }}</text>
                <view class="hm-contact-role">
                  <text>{{ contact.role }}</text>
                </view>
              </view>
              <text class="hm-contact-equipment">{{ contact.equipment }}</text>
              <text class="hm-contact-message">{{ contact.message }}</text>
            </view>
            <view class="hm-contact-unread" v-if="contact.unread > 0">
              <text>{{ contact.unread }}</text>
            </view>
            <text class="hm-contact-arrow">›</text>
          </view>
        </view>

        <!-- 快捷协作入口 -->
        <view class="hm-collab-card">
          <view class="hm-collab-header">
            <text class="hm-collab-title">快捷协作入口</text>
          </view>
          <view class="hm-collab-grid">
            <view class="hm-collab-item" v-for="(item, idx) in collabList" :key="idx" @click="doCollab(item)">
              <view class="hm-collab-icon" :class="'collab-' + item.color">
                <text>{{ item.icon }}</text>
              </view>
              <text class="hm-collab-name">{{ item.name }}</text>
            </view>
          </view>
        </view>

      </view>

      <view class="hm-bottom-space"></view>
    </scroll-view>

    <!-- 右下角机器人按钮 -->
    <view class="hm-fab" @click.stop="toggleRobotMenu">
      <text class="hm-fab-icon">🤖</text>
    </view>

    <!-- 机器人菜单 -->
    <view class="hm-robot-menu" v-if="showRobotMenu" @click="showRobotMenu = false">
      <view class="hm-robot-options" @click.stop>
        <view class="hm-robot-opt" @click.stop="robotAction('ask')">
          <view class="hm-robot-icon-circle rb-blue"><text>🤖</text></view>
          <text class="hm-robot-text">问修助手</text>
        </view>
        <view class="hm-robot-opt" @click.stop="robotAction('steps')">
          <view class="hm-robot-icon-circle rb-green"><text>📋</text></view>
          <text class="hm-robot-text">生成排查步骤</text>
        </view>
        <view class="hm-robot-opt" @click.stop="robotAction('manual')">
          <view class="hm-robot-icon-circle rb-orange"><text>📘</text></view>
          <text class="hm-robot-text">查看相关手册</text>
        </view>
        <view class="hm-robot-opt" @click.stop="robotAction('report')">
          <view class="hm-robot-icon-circle rb-purple"><text>📝</text></view>
          <text class="hm-robot-text">生成检修报告</text>
        </view>
      </view>
    </view>

  </view>
</template>

<script>
export default {
  data() {
    return {
      activeTab: 0,
      tabs: ['今日任务', '复检评估', '协同处理'],
      filterHighRisk: false,
      filterOvertime: false,
      trendPeriod: '7',
      showRobotMenu: false,

      taskList: [
        {
          taskType: '其他', title: 'ZK-320 变频器过热故障检修', status: '待处理',
          equipment: '变频器', fault: '过热报警', level: '紧急检修', risk: '🚨 高风险',
          source: '智能检索生成', leader: '张工', deadline: '今日 18:00',
          typeColor: 'gray', statusColor: 'red', equipmentColor: 'blue', riskColor: 'red'
        },
        {
          taskType: '电气', title: 'CG-125 发动机异响排查', status: '处理中',
          equipment: '发动机总成', fault: '异响报警', level: '优先处理', risk: '⚠️ 中风险',
          source: '风险告警转入', leader: '李工', deadline: '今日 20:00',
          typeColor: 'blue', statusColor: 'orange', equipmentColor: 'green', riskColor: 'orange'
        },
        {
          taskType: '机械', title: '起重机启动困难检修', status: '待复检',
          equipment: '电气系统', fault: '启动故障', level: '标准检修', risk: '⚡ 低风险',
          source: '人工派发', leader: '王工', deadline: '明日 12:00',
          typeColor: 'orange', statusColor: 'gray', equipmentColor: 'blue', riskColor: 'green'
        },
        {
          taskType: '液压', title: '液压系统漏油处理', status: '待处理',
          equipment: '液压系统', fault: '漏油故障', level: '紧急检修', risk: '🚨 高风险',
          source: '案例复用', leader: '赵工', deadline: '今日 16:00',
          typeColor: 'purple', statusColor: 'red', equipmentColor: 'orange', riskColor: 'red'
        }
      ],

      trendData: [
        { day: '一', value: 60 }, { day: '二', value: 75 }, { day: '三', value: 55 },
        { day: '四', value: 80 }, { day: '五', value: 90 }, { day: '六', value: 85 },
        { day: '日', value: 70 }
      ],

      issueList: [
        { name: '变频器复位未完成', desc: '复位前安全确认缺失', meta: '设备: ZK-320 2小时前', status: '待处理', lineColor: 'red', statusColor: 'red' },
        { name: '接线端子松动', desc: '复检发现接线不牢', meta: '设备: CG-125 4小时前', status: '已解决', lineColor: 'orange', statusColor: 'green' }
      ],

      riskList: [
        { icon: '🔥', name: '轴承温度超标', time: '2小时前', status: '已解除', iconColor: 'red', statusColor: 'green' },
        { icon: '⚠️', name: '润滑不足', time: '3小时前', status: '已解除', iconColor: 'orange', statusColor: 'green' },
        { icon: '⚡', name: '接线松动', time: '5小时前', status: '待解除', iconColor: 'orange', statusColor: 'orange' }
      ],

      contactList: [
        { avatar: '张', avatarColor: 'blue', name: '张工', role: '电气检修', equipment: '负责设备: 变频器/配电柜', message: 'ZK-320 配电柜我可以协助复核温升', unread: 2, online: 'online' },
        { avatar: '李', avatarColor: 'green', name: '李工', role: '发动机检修', equipment: '负责设备: 发动机/传动系统', message: '异响任务建议先复核气门间隙', unread: 0, online: 'online' },
        { avatar: '王', avatarColor: 'orange', name: '王工', role: '质检验收', equipment: '负责设备: 全设备验收', message: '待验收任务先补齐复位前照片', unread: 1, online: 'online' },
        { avatar: '赵', avatarColor: 'purple', name: '赵工', role: '机械维修', equipment: '负责设备: 液压系统/密封件', message: '液压千斤顶油封型号我晚点发你', unread: 0, online: 'offline' }
      ],

      collabList: [
        { icon: '📋', name: '任务分配', color: 'blue' },
        { icon: '💬', name: '即时沟通', color: 'green' },
        { icon: '✅', name: '协同验收', color: 'orange' },
        { icon: '📤', name: '资源共享', color: 'purple' }
      ]
    }
  },
  methods: {
    viewTaskDetail(task) {
      uni.navigateTo({ url: '/pages/task-detail/task-detail' })
    },
    startTask(task) {
      uni.navigateTo({ url: '/pages/task-detail/task-detail' })
    },
    goToChat(contact) {
      uni.showToast({ title: '与' + contact.name + '聊天', icon: 'none' })
    },
    doCollab(item) {
      uni.showToast({ title: item.name, icon: 'none' })
    },
    toggleRobotMenu() {
      this.showRobotMenu = !this.showRobotMenu
    },
    robotAction(action) {
      this.showRobotMenu = false
      const actions = { ask: '问修助手', steps: '生成排查步骤', manual: '查看相关手册', report: '生成检修报告' }
      uni.showToast({ title: actions[action] || '操作', icon: 'none' })
    }
  }
}
</script>

<style scoped>
.hm-page {
  min-height: 100vh;
  background: #F5F7FA;
  font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Helvetica Neue", Arial, sans-serif;
}

/* 顶部导航栏 */
.hm-navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 112rpx;
  background: #FFFFFF;
  z-index: 500;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.04);
}

.hm-navbar-inner {
  display: flex;
  align-items: center;
  height: 100%;
  padding: 0 24rpx;
  gap: 16rpx;
}

.hm-logo-circle {
  width: 72rpx;
  height: 72rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, #3B82F6 0%, #60A5FA 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}

.hm-logo-text {
  font-size: 32rpx;
  font-weight: 700;
  color: #FFFFFF;
}

.hm-title-block {
  display: flex;
  flex-direction: column;
  gap: 4rpx;
}

.hm-main-title {
  font-size: 44rpx;
  font-weight: 700;
  color: #1F2937;
  line-height: 1.2;
}

.hm-sub-title {
  font-size: 15rpx;
  color: #3B82F6;
  font-weight: 500;
  line-height: 1.2;
  opacity: 0.8;
}

/* Tab栏 */
.hm-tabs {
  position: fixed;
  top: 100rpx;
  left: 0;
  right: 0;
  background: #FFFFFF;
  display: flex;
  border-bottom: 1rpx solid #EEF0F4;
  z-index: 499;
}

.hm-tab-item {
  flex: 1;
  padding: 18rpx 0;
  text-align: center;
  position: relative;
}

.hm-tab-item.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 40rpx;
  height: 4rpx;
  background: linear-gradient(90deg, #3B82F6, #2563EB);
  border-radius: 2rpx;
}

.hm-tab-text {
  font-size: 26rpx;
  font-weight: 600;
  color: #6B7280;
}

.hm-tab-item.active .hm-tab-text {
  color: #1F2937;
}

/* 滚动区域 */
.hm-scroll {
  padding-top: 168rpx;
  min-height: calc(100vh - 168rpx);
}

.hm-content {
  padding: 0 20rpx;
}

/* 任务闭环率卡片 */
.hm-closure-card {
  background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
  border-radius: 16rpx;
  padding: 20rpx 24rpx;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16rpx;
  margin-top: 8rpx;
  box-shadow: 0 6rpx 20rpx rgba(59, 130, 246, 0.3);
}

.hm-closure-left {
  flex: 1;
}

.hm-closure-label {
  font-size: 22rpx;
  color: rgba(255, 255, 255, 0.85);
  display: block;
}

.hm-closure-value {
  font-size: 56rpx;
  font-weight: 700;
  color: #FFFFFF;
  display: block;
  line-height: 1;
  margin: 6rpx 0;
}

.hm-closure-desc {
  font-size: 20rpx;
  color: rgba(255, 255, 255, 0.8);
  display: block;
  margin-bottom: 12rpx;
}

.hm-closure-badges {
  display: flex;
  gap: 10rpx;
}

.hm-badge {
  padding: 6rpx 12rpx;
  border-radius: 8rpx;
}

.hm-badge-orange {
  background: rgba(251, 191, 36, 0.25);
}

.hm-badge-red {
  background: rgba(239, 68, 68, 0.25);
}

.hm-badge text {
  font-size: 18rpx;
  color: #FFFFFF;
  font-weight: 600;
}

.hm-closure-right {
  flex-shrink: 0;
}

.hm-ring-progress {
  width: 96rpx;
  height: 96rpx;
}

.hm-ring-outer {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: conic-gradient(#FFFFFF 0deg, #FFFFFF 306deg, rgba(255,255,255,0.2) 306deg, rgba(255,255,255,0.2) 360deg);
  display: flex;
  align-items: center;
  justify-content: center;
}

.hm-ring-inner {
  width: 72rpx;
  height: 72rpx;
  border-radius: 50%;
  background: #2563EB;
  display: flex;
  align-items: center;
  justify-content: center;
}

.hm-ring-text {
  font-size: 20rpx;
  font-weight: 700;
  color: #FFFFFF;
}

/* 统计卡片 */
.hm-stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10rpx;
  margin-bottom: 16rpx;
}

.hm-stat-card {
  background: #FFFFFF;
  border-radius: 12rpx;
  padding: 14rpx 6rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.04);
}

.hm-stat-icon {
  width: 44rpx;
  height: 44rpx;
  border-radius: 10rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 6rpx;
}

.hm-icon-blue { background: rgba(59, 130, 246, 0.12); }
.hm-icon-orange { background: rgba(245, 158, 11, 0.12); }
.hm-icon-gray { background: rgba(107, 114, 128, 0.12); }
.hm-icon-green { background: rgba(16, 185, 129, 0.12); }

.hm-stat-icon text {
  font-size: 20rpx;
}

.hm-stat-num {
  font-size: 30rpx;
  font-weight: 700;
  color: #1F2937;
  line-height: 1;
}

.hm-stat-label {
  font-size: 18rpx;
  color: #6B7280;
  font-weight: 500;
  margin-top: 4rpx;
}

/* 搜索栏 */
.hm-search-section {
  background: #FFFFFF;
  border-radius: 12rpx;
  padding: 14rpx 16rpx;
  margin-bottom: 16rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.04);
}

.hm-search-box {
  display: flex;
  align-items: center;
  background: #F5F7FA;
  border-radius: 10rpx;
  padding: 10rpx 16rpx;
  gap: 10rpx;
  margin-bottom: 12rpx;
}

.hm-search-box text {
  font-size: 26rpx;
}

.hm-search-input {
  flex: 1;
  font-size: 26rpx;
  color: #1F2937;
}

.hm-search-placeholder {
  color: #9CA3AF;
}

.hm-filter-tags {
  display: flex;
  gap: 12rpx;
}

.hm-filter-tag {
  padding: 10rpx 20rpx;
  background: rgba(239, 68, 68, 0.1);
  border-radius: 20rpx;
  border: 2rpx solid transparent;
}

.hm-filter-tag.active {
  background: rgba(239, 68, 68, 0.15);
  border-color: rgba(239, 68, 68, 0.3);
}

.hm-filter-tag text {
  font-size: 24rpx;
  color: #DC2626;
  font-weight: 600;
}

/* 任务卡片列表 */
.hm-task-list {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

.hm-task-card {
  background: #FFFFFF;
  border-radius: 12rpx;
  padding: 14rpx 16rpx;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.04);
  border-left: 4rpx solid #3B82F6;
}

.hm-task-header {
  display: flex;
  align-items: flex-start;
  gap: 8rpx;
  margin-bottom: 8rpx;
}

.hm-task-type-tag {
  padding: 4rpx 10rpx;
  border-radius: 6rpx;
  flex-shrink: 0;
}

.type-gray { background: rgba(107, 114, 128, 0.12); }
.type-gray text { color: #4B5563; }
.type-blue { background: rgba(59, 130, 246, 0.12); }
.type-blue text { color: #2563EB; }
.type-orange { background: rgba(245, 158, 11, 0.12); }
.type-orange text { color: #D97706; }
.type-purple { background: rgba(139, 92, 246, 0.12); }
.type-purple text { color: #7C3AED; }

.hm-task-type-tag text {
  font-size: 18rpx;
  font-weight: 600;
}

.hm-task-title {
  flex: 1;
  font-size: 24rpx;
  font-weight: 700;
  color: #1F2937;
  line-height: 1.3;
}

.hm-task-status {
  padding: 4rpx 10rpx;
  border-radius: 6rpx;
  flex-shrink: 0;
}

.status-red { background: rgba(239, 68, 68, 0.12); }
.status-red text { color: #DC2626; }
.status-orange { background: rgba(245, 158, 11, 0.12); }
.status-orange text { color: #D97706; }
.status-gray { background: rgba(107, 114, 128, 0.12); }
.status-gray text { color: #4B5563; }

.hm-task-status text {
  font-size: 18rpx;
  font-weight: 600;
}

.hm-task-tags {
  display: flex;
  gap: 8rpx;
  margin-bottom: 8rpx;
}

.hm-chip {
  padding: 4rpx 10rpx;
  border-radius: 6rpx;
}

.chip-blue { background: rgba(59, 130, 246, 0.1); }
.chip-blue text { color: #2563EB; }
.chip-green { background: rgba(16, 185, 129, 0.1); }
.chip-green text { color: #059669; }
.chip-orange { background: rgba(245, 158, 11, 0.1); }
.chip-orange text { color: #D97706; }
.chip-red { background: rgba(239, 68, 68, 0.1); }
.chip-red text { color: #DC2626; }

.hm-chip text {
  font-size: 20rpx;
  font-weight: 500;
}

.hm-task-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 6rpx 16rpx;
  padding: 8rpx 0;
  border-top: 1rpx solid #F3F4F6;
  border-bottom: 1rpx solid #F3F4F6;
  margin-bottom: 10rpx;
}

.hm-meta-item {
  font-size: 20rpx;
  color: #6B7280;
}

.risk-red { color: #DC2626; }
.risk-orange { color: #D97706; }
.risk-green { color: #059669; }

.hm-task-actions {
  display: flex;
  gap: 12rpx;
}

.hm-btn {
  flex: 1;
  padding: 10rpx 0;
  border-radius: 8rpx;
  text-align: center;
}

.hm-btn-outline {
  background: #F5F7FA;
  border: 1rpx solid #E5E7EB;
}

.hm-btn-outline text {
  font-size: 22rpx;
  color: #374151;
  font-weight: 600;
}

.hm-btn-primary {
  background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
}

.hm-btn-primary text {
  font-size: 22rpx;
  color: #FFFFFF;
  font-weight: 600;
}

/* === TAB 1: 复检评估 === */

/* 复检通过率卡片 */
.hm-pass-rate-card {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(34, 197, 94, 0.05) 100%);
  border-radius: 12rpx;
  padding: 18rpx 20rpx;
  margin-bottom: 16rpx;
  margin-top: 8rpx;
}

.hm-pass-left {
  flex: 1;
}

.hm-pass-label {
  font-size: 22rpx;
  color: #6B7280;
  display: block;
  margin-bottom: 6rpx;
}

.hm-pass-row {
  display: flex;
  align-items: baseline;
  gap: 10rpx;
  margin-bottom: 12rpx;
}

.hm-pass-value {
  font-size: 48rpx;
  font-weight: 700;
  color: #059669;
}

.hm-pass-trend {
  font-size: 22rpx;
  color: #059669;
  font-weight: 600;
}

.hm-pass-bar {
  height: 12rpx;
  background: rgba(16, 185, 129, 0.2);
  border-radius: 6rpx;
  overflow: hidden;
}

.hm-pass-bar-fill {
  height: 100%;
  width: 92%;
  background: linear-gradient(90deg, #10B981, #34D399);
  border-radius: 6rpx;
}

/* 任务闭环趋势 */
.hm-trend-card {
  background: #FFFFFF;
  border-radius: 12rpx;
  padding: 18rpx 20rpx;
  margin-bottom: 16rpx;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.04);
}

.hm-trend-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16rpx;
}

.hm-trend-title {
  font-size: 26rpx;
  font-weight: 700;
  color: #1F2937;
}

.hm-trend-tabs {
  display: flex;
  gap: 8rpx;
}

.hm-trend-tab {
  padding: 8rpx 20rpx;
  border-radius: 12rpx;
  background: #F5F7FA;
}

.hm-trend-tab.active {
  background: #3B82F6;
}

.hm-trend-tab text {
  font-size: 22rpx;
  font-weight: 600;
  color: #6B7280;
}

.hm-trend-tab.active text {
  color: #FFFFFF;
}

.hm-trend-chart {
  height: 200rpx;
}

.hm-trend-bars {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  height: 100%;
  padding-top: 40rpx;
}

.hm-trend-bar-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8rpx;
  width: 12%;
}

.hm-trend-bar {
  width: 100%;
  background: linear-gradient(180deg, #3B82F6 0%, #60A5FA 100%);
  border-radius: 8rpx 8rpx 0 0;
  min-height: 8rpx;
}

.hm-trend-day {
  font-size: 20rpx;
  color: #6B7280;
}

/* 返工问题列表 */
.hm-issue-card {
  background: #FFFFFF;
  border-radius: 12rpx;
  padding: 18rpx 20rpx;
  margin-bottom: 16rpx;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.04);
}

.hm-issue-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14rpx;
}

.hm-issue-title {
  font-size: 26rpx;
  font-weight: 700;
  color: #1F2937;
}

.hm-issue-count {
  font-size: 22rpx;
  color: #6B7280;
  font-weight: 500;
}

.hm-issue-list {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

.hm-issue-item {
  display: flex;
  align-items: flex-start;
  gap: 12rpx;
  padding: 12rpx;
  background: #F9FAFB;
  border-radius: 10rpx;
}

.hm-issue-line {
  width: 6rpx;
  height: 48rpx;
  border-radius: 3rpx;
  flex-shrink: 0;
}

.line-red { background: #EF4444; }
.line-orange { background: #F59E0B; }

.hm-issue-content {
  flex: 1;
}

.hm-issue-name {
  font-size: 26rpx;
  font-weight: 700;
  color: #1F2937;
  display: block;
  margin-bottom: 4rpx;
}

.hm-issue-desc {
  font-size: 22rpx;
  color: #6B7280;
  display: block;
  margin-bottom: 4rpx;
}

.hm-issue-meta {
  font-size: 20rpx;
  color: #9CA3AF;
  display: block;
}

.hm-issue-status {
  padding: 8rpx 14rpx;
  border-radius: 10rpx;
  flex-shrink: 0;
}

.issue-red { background: rgba(239, 68, 68, 0.12); }
.issue-red text { color: #DC2626; }
.issue-green { background: rgba(16, 185, 129, 0.12); }
.issue-green text { color: #059669; }

.hm-issue-status text {
  font-size: 22rpx;
  font-weight: 600;
}

/* 风险解除情况 */
.hm-risk-card {
  background: #FFFFFF;
  border-radius: 12rpx;
  padding: 18rpx 20rpx;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.04);
}

.hm-risk-header {
  margin-bottom: 14rpx;
}

.hm-risk-title {
  font-size: 26rpx;
  font-weight: 700;
  color: #1F2937;
}

.hm-risk-stats {
  display: flex;
  justify-content: space-around;
  padding: 14rpx 0;
  border-bottom: 1rpx solid #F3F4F6;
  margin-bottom: 14rpx;
}

.hm-risk-stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.hm-risk-num {
  font-size: 40rpx;
  font-weight: 700;
}

.hm-risk-num.red { color: #DC2626; }
.hm-risk-num.orange { color: #D97706; }
.hm-risk-num.green { color: #059669; }

.hm-risk-label {
  font-size: 22rpx;
  color: #6B7280;
  margin-top: 4rpx;
}

.hm-risk-list {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.hm-risk-item {
  display: flex;
  align-items: center;
  gap: 16rpx;
  padding: 16rpx;
  background: #F9FAFB;
  border-radius: 12rpx;
}

.hm-risk-icon {
  width: 48rpx;
  height: 48rpx;
  border-radius: 12rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.risk-icon-red { background: rgba(239, 68, 68, 0.12); }
.risk-icon-orange { background: rgba(245, 158, 11, 0.12); }

.hm-risk-icon text {
  font-size: 24rpx;
}

.hm-risk-info {
  flex: 1;
}

.hm-risk-name {
  font-size: 26rpx;
  font-weight: 600;
  color: #1F2937;
  display: block;
}

.hm-risk-time {
  font-size: 22rpx;
  color: #9CA3AF;
  display: block;
}

.hm-risk-status {
  padding: 8rpx 14rpx;
  border-radius: 10rpx;
}

.risk-status-green { background: rgba(16, 185, 129, 0.12); }
.risk-status-green text { color: #059669; }
.risk-status-orange { background: rgba(245, 158, 11, 0.12); }
.risk-status-orange text { color: #D97706; }

.hm-risk-status text {
  font-size: 22rpx;
  font-weight: 600;
}

/* === TAB 2: 协同处理 === */

/* 协作团队头部 */
.hm-team-card {
  background: linear-gradient(135deg, #1E3A5F 0%, #2563EB 100%);
  border-radius: 12rpx;
  padding: 18rpx 20rpx;
  margin-bottom: 16rpx;
  margin-top: 8rpx;
}

.hm-team-info {
  flex: 1;
}

.hm-team-title {
  font-size: 26rpx;
  font-weight: 700;
  color: #FFFFFF;
  display: block;
  margin-bottom: 6rpx;
}

.hm-team-desc {
  font-size: 20rpx;
  color: rgba(255, 255, 255, 0.8);
  display: block;
}

.hm-team-status {
  text-align: right;
}

.hm-team-online {
  font-size: 22rpx;
  color: #34D399;
  font-weight: 600;
}

/* 搜索框 */
.hm-team-search {
  display: flex;
  align-items: center;
  background: #FFFFFF;
  border-radius: 12rpx;
  padding: 14rpx 18rpx;
  gap: 10rpx;
  margin-bottom: 16rpx;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.04);
}

.hm-team-search text {
  font-size: 26rpx;
}

.hm-team-search-input {
  flex: 1;
  font-size: 26rpx;
  color: #1F2937;
}

/* 联系人列表 */
.hm-contact-list {
  display: flex;
  flex-direction: column;
  gap: 10rpx;
  margin-bottom: 16rpx;
}

.hm-contact-item {
  display: flex;
  align-items: center;
  gap: 12rpx;
  background: #FFFFFF;
  border-radius: 12rpx;
  padding: 14rpx 16rpx;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.04);
}

.hm-contact-avatar {
  width: 60rpx;
  height: 60rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.avatar-blue { background: linear-gradient(135deg, #3B82F6, #60A5FA); }
.avatar-green { background: linear-gradient(135deg, #10B981, #34D399); }
.avatar-orange { background: linear-gradient(135deg, #F59E0B, #FBBF24); }
.avatar-purple { background: linear-gradient(135deg, #8B5CF6, #A78BFA); }

.hm-contact-avatar text {
  font-size: 28rpx;
  font-weight: 700;
  color: #FFFFFF;
}

.hm-contact-status-dot {
  position: absolute;
  bottom: 4rpx;
  right: 4rpx;
  width: 16rpx;
  height: 16rpx;
  border-radius: 50%;
  border: 3rpx solid #FFFFFF;
}

.dot-online { background: #10B981; }
.dot-offline { background: #9CA3AF; }

.hm-contact-content {
  flex: 1;
  min-width: 0;
}

.hm-contact-name-row {
  display: flex;
  align-items: center;
  gap: 12rpx;
  margin-bottom: 6rpx;
}

.hm-contact-name {
  font-size: 28rpx;
  font-weight: 700;
  color: #1F2937;
}

.hm-contact-role {
  padding: 4rpx 10rpx;
  background: rgba(59, 130, 246, 0.1);
  border-radius: 8rpx;
}

.hm-contact-role text {
  font-size: 20rpx;
  color: #2563EB;
  font-weight: 500;
}

.hm-contact-equipment {
  font-size: 22rpx;
  color: #6B7280;
  display: block;
  margin-bottom: 4rpx;
}

.hm-contact-message {
  font-size: 22rpx;
  color: #9CA3AF;
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.hm-contact-unread {
  background: #EF4444;
  width: 36rpx;
  height: 36rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.hm-contact-unread text {
  font-size: 20rpx;
  color: #FFFFFF;
  font-weight: 600;
}

.hm-contact-arrow {
  font-size: 36rpx;
  color: #D1D5DB;
}

/* 快捷协作入口 */
.hm-collab-card {
  background: #FFFFFF;
  border-radius: 12rpx;
  padding: 18rpx 20rpx;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.04);
}

.hm-collab-header {
  margin-bottom: 14rpx;
}

.hm-collab-title {
  font-size: 26rpx;
  font-weight: 700;
  color: #1F2937;
}

.hm-collab-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10rpx;
}

.hm-collab-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6rpx;
  padding: 12rpx 0;
  background: #F9FAFB;
  border-radius: 10rpx;
}

.hm-collab-icon {
  width: 56rpx;
  height: 56rpx;
  border-radius: 14rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.collab-blue { background: rgba(59, 130, 246, 0.12); }
.collab-green { background: rgba(16, 185, 129, 0.12); }
.collab-orange { background: rgba(245, 158, 11, 0.12); }
.collab-purple { background: rgba(139, 92, 246, 0.12); }

.hm-collab-icon text {
  font-size: 28rpx;
}

.hm-collab-name {
  font-size: 22rpx;
  color: #374151;
  font-weight: 500;
}

/* 底部留白 */
.hm-bottom-space {
  height: 160rpx;
}

/* 右下角机器人按钮 */
.hm-fab {
  position: fixed;
  right: 32rpx;
  bottom: 160rpx;
  width: 100rpx;
  height: 100rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8rpx 24rpx rgba(59, 130, 246, 0.4);
  z-index: 500;
}

.hm-fab-icon {
  font-size: 48rpx;
}

/* 机器人菜单 */
.hm-robot-menu {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.35);
  z-index: 999;
  display: flex;
  justify-content: flex-end;
  align-items: flex-end;
  padding: 0 32rpx 260rpx 0;
}

.hm-robot-options {
  background: #FFFFFF;
  border-radius: 16rpx;
  padding: 12rpx;
  box-shadow: 0 12rpx 40rpx rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  gap: 8rpx;
  min-width: 320rpx;
}

.hm-robot-opt {
  display: flex;
  align-items: center;
  gap: 16rpx;
  padding: 18rpx 20rpx;
  background: #F5F7FA;
  border-radius: 12rpx;
}

.hm-robot-icon-circle {
  width: 52rpx;
  height: 52rpx;
  border-radius: 14rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.rb-blue { background: rgba(59, 130, 246, 0.15); }
.rb-green { background: rgba(16, 185, 129, 0.15); }
.rb-orange { background: rgba(245, 158, 11, 0.15); }
.rb-purple { background: rgba(139, 92, 246, 0.15); }

.hm-robot-icon-circle text {
  font-size: 28rpx;
}

.hm-robot-text {
  font-size: 26rpx;
  color: #374151;
  font-weight: 600;
}
</style>
