<template>
  <view class="modern-health-page" :class="{'page-loaded': isLoaded}">
    <HealthManagerFab :page-context="maintenanceAgentContext" />

    <!-- 1. Header Section -->
    <view class="header-section stagger-1">
      <view class="user-profile">
        <view class="avatar-container">
          <image class="avatar" src="/static/assistant-maintenance.png" mode="aspectFill"></image>
        </view>
        <view class="greeting">
          <text class="greeting-title">早上好，开始今日标准作业</text>
          <text class="greeting-subtitle">司南为你规划检修路线、推送标准流程并动态提醒风险节点</text>
        </view>
      </view>
      <view class="notification-btn tap-effect" @click="showHealthTip">
        <text class="icon-bell">提醒</text>
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
          <text>复检评估</text>
        </view>
        <view class="tab-item" :class="{ active: activeTab === 2 }" @click="switchTab(2)">
          <text>联系人</text>
        </view>
      </view>
    </view>

    <!-- 3. Tab Contents with Slide & Crossfade -->
    <view class="tab-content-wrapper">
      <!-- TAB 0: 今日概览 (Bento Box Layout) -->
      <view class="tab-content overview-tab" :class="{ 'content-active': activeTab === 0 }">
        
        <view class="execution-section stagger-3">
          <view class="execution-header">
            <view>
              <text class="section-title execution-title">检修任务工作台</text>
              <text class="execution-subtitle">{{ taskCompletionOverview.healthLabel }}</text>
            </view>
            <view class="execution-actions-row">
              <view class="execution-add tap-effect" @click="showAddModal = !showAddModal">
                <text class="execution-add-text">{{ showAddModal ? '收起' : '新增' }}</text>
              </view>
              <view class="execution-refresh tap-effect" @click="loadTasks">
                <text class="execution-refresh-text">{{ taskLoading ? '同步中' : '刷新' }}</text>
              </view>
            </view>
          </view>

          <view v-if="showAddModal" class="task-add-form">
            <input class="task-add-input" v-model="newTaskTitle" placeholder="任务名称，如：完成配电柜二级检修" />
            <input class="task-add-input" v-model="newTaskDescription" placeholder="故障描述 / 检修要求" />
            <input class="task-add-input" v-model="newTaskAssignee" placeholder="负责人，如：聪明的一修" />
            <view class="task-add-actions">
              <view class="task-add-confirm tap-effect" @click="addTask">加入任务列表</view>
              <view class="task-add-cancel tap-effect" @click="showAddModal = false">取消</view>
            </view>
          </view>

          <view class="execution-overview">
            <view class="overview-head">
              <view>
                <text class="overview-label">任务闭环率</text>
                <text class="overview-value">{{ taskCompletionOverview.completionRate }}%</text>
              </view>
              <view class="overview-badge" :class="{ warning: taskCompletionOverview.overdue > 0 || taskCompletionOverview.highRisk > 0 }">
                <text>{{ taskCompletionOverview.overdue > 0 || taskCompletionOverview.highRisk > 0 ? '需关注' : '进度稳定' }}</text>
              </view>
            </view>
            <view class="overview-track">
              <view class="overview-track-fill" :style="{ width: taskCompletionOverview.completionRate + '%' }"></view>
            </view>
            <view class="execution-stats">
              <view
                class="execution-stat"
                v-for="stat in taskMetrics"
                :key="stat.key"
                @click="switchTaskTab(stat.filterKey)"
              >
                <view class="execution-stat-icon" :style="{ background: stat.bg, color: stat.color }">
                  <text>{{ stat.icon }}</text>
                </view>
                <text class="execution-stat-num">{{ stat.count }}</text>
                <text class="execution-stat-label">{{ stat.label }}</text>
              </view>
            </view>
          </view>

          <view class="execution-tools">
            <view class="execution-search">
              <text class="execution-search-icon">⌕</text>
              <input
                class="execution-search-input"
                v-model="taskKeyword"
                placeholder="搜索设备 / 故障 / 负责人"
                placeholder-class="execution-search-placeholder"
              />
            </view>
            <view class="execution-filter tap-effect" @click="showTaskFilterTip">
              <text class="execution-filter-icon">筛选</text>
            </view>
          </view>

          <view class="execution-tabs">
            <view
              v-for="tab in taskTabs"
              :key="tab.key"
              class="execution-tab"
              :class="{ active: currentTaskStatus === tab.key }"
              @click="switchTaskTab(tab.key)"
            >
              <text class="execution-tab-text">{{ tab.label }}</text>
            </view>
          </view>

          <view class="execution-list">
            <view
              v-for="task in visibleTasks"
              :key="task.id"
              class="execution-card tap-effect"
              :class="'severity-' + (task.severity || 'medium')"
              @click="goTaskDetail(task.id)"
            >
              <view class="execution-card-top">
                <view class="execution-title-wrap">
                  <text class="execution-card-title">{{ task.title }}</text>
                  <text class="execution-equipment">{{ task.equipment_name }} · {{ task.equipment_model || '未登记型号' }}</text>
                </view>
                <view class="execution-status" :style="{ background: getStatusBg(task.status), color: getStatusColor(task.status) }">
                  {{ getStatusText(task.status) }}
                </view>
              </view>
              <text class="execution-desc">{{ task.description }}</text>
              <view v-if="task.status === 'in_progress'" class="execution-progress">
                <view class="execution-progress-bar" :style="{ width: getTaskProgress(task) + '%' }"></view>
              </view>
              <view class="execution-card-bottom">
                <view class="execution-meta-group">
                  <text class="execution-meta">位置 {{ getTaskLocation(task) }}</text>
                  <view class="execution-assignee">
                    <view class="execution-assignee-avatar" :style="{ background: getAssigneeAvatarBg(task) }">
                      <image v-if="getAssigneeAvatar(task)" :src="getAssigneeAvatar(task)" class="execution-assignee-img" mode="aspectFill"></image>
                      <text v-else>{{ getAssigneeInitial(task) }}</text>
                    </view>
                    <text class="execution-meta">负责人 {{ getAssigneeName(task) }}</text>
                  </view>
                  <text class="execution-meta">截止 {{ getTaskDeadline(task) }}</text>
                </view>
                <text class="execution-severity" :style="{ background: getSeverityBg(task.severity), color: getSeverityColor(task.severity) }">
                  {{ getSeverityText(task.severity) }}
                </text>
              </view>
              <view class="execution-actions">
                <view class="execution-action secondary" @click.stop="goTaskDetail(task.id)">
                  <text>查看</text>
                </view>
                <view class="execution-action primary" @click.stop="goTaskDetail(task.id)">
                  <text>{{ getTaskActionText(task.status) }}</text>
                </view>
              </view>
            </view>

            <view v-if="filteredTasks.length > 3" class="execution-more tap-effect" @click="taskListExpanded = !taskListExpanded">
              <text>{{ taskListExpanded ? '收起任务' : '查看更多任务' }}</text>
            </view>

            <view v-if="filteredTasks.length === 0" class="execution-empty">
              <text class="execution-empty-icon">📋</text>
              <text class="execution-empty-text">暂无{{ currentTaskLabel }}任务</text>
            </view>
          </view>
        </view>

      </view> <!-- End Tab 0 -->

      <!-- TAB 1: 复检评估 (Trend Tab) -->
      <view class="tab-content trend-tab" :class="{ 'content-active': activeTab === 1 }">
        
        <!-- Report Period Switcher -->
        <view class="report-switcher stagger-3">
          <view class="switch-item tap-effect" :class="{ active: reportView === 'weekly' }" @click="reportView = 'weekly'"><text>近七天</text></view>
          <view class="switch-item tap-effect" :class="{ active: reportView === 'monthly' }" @click="reportView = 'monthly'"><text>近三月</text></view>
        </view>

        <view v-if="reportView === 'weekly'">
          <!-- Humanized Insight -->
          <view class="human-insight-card hover-glow stagger-4">
            <view class="insight-avatar-row">
              <image class="insight-avatar" src="/static/assistant-maintenance.png" mode="aspectFill"></image>
              <view class="insight-bubble">
                <text class="bubble-text">这周标准作业完成度稳步上升！继续保持现场复盘节奏</text>
              </view>
            </view>
            <view class="insight-tags">
              <text class="tag positive">作业流程已完成</text>
              <text class="tag warning">风险复核需加强</text>
            </view>
          </view>

          <!-- Weekly Trend Chart -->
          <view class="bento-card stagger-5">
            <view class="card-header">
              <view class="icon-box">
                <text class="lucide-icon">📈</text>
              </view>
              <text class="card-title">近七天复检质量变化</text>
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
            <text class="action-desc">数据显示你的复检质量在上升。明天建议补充过热故障复核照片，并完成一次停电验电记录检查。</text>
            <view class="challenge-btn">好的，我试试</view>
          </view>
        </view>

        <view v-if="reportView === 'monthly'">
          <!-- Annual Summary Banner -->
          <view class="annual-banner hover-glow tap-effect stagger-4" @click="showAnnualReport">
            <view class="banner-content">
              <text class="banner-title">2026 检修总结</text>
              <text class="banner-subtitle">点击查看你的检修质量里程碑</text>
            </view>
            <text class="lucide-icon banner-arrow" style="opacity:0.8">前往</text>
          </view>

          <!-- Monthly Trend Box -->
          <view class="bento-grid" style="margin-bottom:0px;">
            <view class="bento-card cardio-card hover-glow stagger-5">
              <view class="card-header">
                <view class="icon-box"><text style="font-size:28rpx">📉</text></view>
                <text class="card-title">闭环率趋势</text>
              </view>
              <view class="chart-container-monthly">
                 <view class="month-bar-group" v-for="(m, i) in monthlyData" :key="'w'+i">
                   <view class="month-bar" :style="{ height: isLoaded ? m.value + '%' : '0%' }"></view>
                   <text class="month-label">{{ m.month }}</text>
                 </view>
              </view>
              <text class="status-msg good-status">总体闭环率持续提升，流程缺口减少</text>
            </view>

            <view class="bento-card activity-card hover-glow stagger-6">
              <view class="card-header">
                <view class="icon-box"><text style="font-size:28rpx">🍎</text></view>
                <text class="card-title">作业合规程度</text>
              </view>
              <view class="chart-container-monthly">
                 <view class="month-bar-group" v-for="(m, i) in monthlyActivity" :key="'a'+i">
                   <view class="month-bar activity" :style="{ height: isLoaded ? m.value + '%' : '0%' }"></view>
                   <text class="month-label">{{ m.month }}</text>
                 </view>
              </view>
              <text class="status-msg good-status">本月检修作业合规度显著提升！</text>
            </view>
          </view>
        </view>
      </view> <!-- End Tab 1 -->

      <!-- TAB 2: 联系人协作 -->
      <view class="tab-content intervene-tab" :class="{ 'content-active': activeTab === 2 }">

        <view class="collab-card stagger-3" v-if="!contactChatOpen">
          <view class="collab-header">
            <view>
              <text class="collab-title">检修协作联系人</text>
              <text class="collab-subtitle">任务沟通、现场支援与验收协同</text>
            </view>
            <view class="collab-online-pill">
              <text>{{ onlineContactCount }} 人在线</text>
            </view>
          </view>

          <view class="collab-search">
            <text class="collab-search-icon">⌕</text>
            <input
              class="collab-search-input"
              v-model="contactKeyword"
              placeholder="搜索同事 / 岗位 / 擅长方向"
              placeholder-class="collab-placeholder"
            />
          </view>

          <view class="contact-list">
            <view
              class="contact-item tap-effect"
              v-for="contact in filteredContacts"
              :key="contact.id"
              :class="{ active: activeContactId === contact.id }"
              @click="openContactChat(contact.id)"
            >
              <view class="contact-avatar" :style="{ background: contact.bg }">
                <text>{{ contact.avatar }}</text>
                <view class="contact-status-dot" :class="contact.status"></view>
              </view>
              <view class="contact-main">
                <view class="contact-name-row">
                  <text class="contact-name">{{ contact.name }}</text>
                  <text class="contact-role">{{ contact.role }}</text>
                </view>
                <text class="contact-skill">{{ contact.skill }}</text>
                <text class="contact-last">{{ contact.lastMessage }}</text>
              </view>
              <view class="contact-meta">
                <text class="contact-time">{{ contact.time }}</text>
                <view v-if="contact.unread" class="contact-unread">
                  <text>{{ contact.unread }}</text>
                </view>
              </view>
            </view>
          </view>
        </view>

        <view class="chat-page stagger-3" v-if="contactChatOpen && activeContact">
          <view class="chat-topbar">
            <view class="chat-back tap-effect" @click="backToContacts">
              <text>‹</text>
            </view>
            <view class="chat-peer">
              <text class="chat-peer-name">{{ activeContact.name }}</text>
              <text class="chat-peer-status">{{ activeContact.role }} · {{ getContactStatusText(activeContact.status) }}</text>
            </view>
            <view class="chat-top-actions">
              <view class="chat-top-action tap-effect" @click="callContact(activeContact)">
                <text>呼叫</text>
              </view>
              <view class="chat-top-action primary tap-effect" @click="assignContact(activeContact)">
                <text>协作</text>
              </view>
            </view>
          </view>

          <scroll-view class="chat-scroll" scroll-y :show-scrollbar="false">
            <view class="chat-profile-strip">
              <view class="contact-avatar chat-avatar" :style="{ background: activeContact.bg }">
                <text>{{ activeContact.avatar }}</text>
                <view class="contact-status-dot" :class="activeContact.status"></view>
              </view>
              <view class="chat-profile-main">
                <text class="chat-profile-skill">{{ activeContact.skill }}</text>
                <text class="chat-profile-hint">可协助任务沟通、现场支援和结果验收</text>
              </view>
            </view>

            <view class="quick-message-row chat-quick-row">
              <view
                class="quick-message tap-effect"
                v-for="msg in quickMessages"
                :key="msg"
                @click="messageDraft = msg"
              >
                <text>{{ msg }}</text>
              </view>
            </view>

            <view class="message-thread chat-thread">
              <view
                class="message-bubble"
                v-for="(msg, index) in activeContact.messages"
                :key="index"
                :class="{ mine: msg.mine }"
              >
                <text>{{ msg.text }}</text>
              </view>
            </view>
          </scroll-view>

          <view class="chat-input-bar">
            <input
              class="message-input chat-input"
              v-model="messageDraft"
              placeholder="输入消息..."
              placeholder-class="collab-placeholder"
              confirm-type="send"
              @confirm="sendContactMessage"
            />
            <view class="message-send tap-effect" @click="sendContactMessage">
              <text>发送</text>
            </view>
          </view>
        </view>

      </view> <!-- End Tab 2 -->

    </view> <!-- End Content Wrapper -->

    <!-- 计划详情弹窗 -->
    <view class="modal-overlay" v-if="showPlanDetail" @click="showPlanDetail = false">
      <view class="plan-detail-modal" @click.stop>
        <view class="modal-drag-bar"></view>
        <view class="plan-detail-header">
          <view class="plan-detail-title-row">
            <view class="plan-detail-icon-wrap">
              <text class="plan-detail-icon">{{ selectedPlan.icon }}</text>
            </view>
            <view class="plan-detail-title-text">
              <text class="plan-detail-name">{{ selectedPlan.name }}</text>
              <text class="plan-detail-desc">{{ selectedPlan.desc }}</text>
            </view>
          </view>
          <view class="plan-detail-close" @click="showPlanDetail = false">
            <text style="font-size:28rpx; color:#64748b;">✕</text>
          </view>
        </view>

        <scroll-view class="plan-detail-content" scroll-y="true" :show-scrollbar="false" enhanced :bounces="true">
          <view class="plan-desc-section">
            <view class="plan-desc-header">
              <view class="plan-desc-icon-wrap">
                <text style="font-size:24rpx;">📋</text>
              </view>
              <text class="plan-desc-title">计划说明</text>
            </view>
            <text class="plan-desc-text">{{ selectedPlan.name }}方案将结合设备画像、检修知识库和作业反馈，帮助你{{ selectedPlan.desc }}。每日建议作业时长约{{ selectedPlan.totalCalories }}分钟，系统会持续推送手册、案例、流程和风险复核清单。</text>
          </view>

          <view class="plan-nutrition-summary">
            <view class="nutrition-item nutrition-cal">
              <text class="nutrition-val">{{ selectedPlan.totalCalories }}</text>
              <text class="nutrition-label">目标时长</text>
            </view>
            <view class="nutrition-item nutrition-pro">
              <text class="nutrition-val">{{ selectedPlan.protein }}类</text>
              <text class="nutrition-label">手册资料</text>
            </view>
            <view class="nutrition-item nutrition-carb">
              <text class="nutrition-val">{{ selectedPlan.carbs }}组</text>
              <text class="nutrition-label">作业任务</text>
            </view>
            <view class="nutrition-item nutrition-fat">
              <text class="nutrition-val">{{ selectedPlan.fat }}项</text>
              <text class="nutrition-label">检修案例</text>
            </view>
          </view>

          <view class="meal-section" v-for="(meal, mIdx) in selectedPlan.meals" :key="mIdx">
            <view class="meal-section-header">
              <view class="meal-type-badge">
                <text class="meal-type-icon">{{ meal.icon }}</text>
                <text class="meal-type-name">{{ meal.type }}</text>
              </view>
              <view class="meal-calories-badge">
                <text class="meal-calories-text">{{ meal.calories }}分钟</text>
              </view>
            </view>
            <view class="meal-dishes">
              <view class="dish-card" v-for="(dish, dIdx) in meal.dishes" :key="dIdx" @click="viewDishDetail(dish)">
                <view class="dish-card-left">
                  <view class="dish-emoji-badge">{{ getDishEmoji(dish.name) }}</view>
                </view>
                <view class="dish-card-body">
                  <text class="dish-name">{{ dish.name }}</text>
                  <text class="dish-health-desc">{{ getHealthDesc(dish) }}</text>
                  <view class="dish-tags-row">
                    <text class="dish-tag cal-tag">{{ dish.calories }}作业点</text>
                    <text class="dish-tag time-tag">{{ dish.cooking_time }}min</text>
                    <text class="dish-tag diff-tag">{{ dish.difficulty }}</text>
                  </view>
                </view>
                <view class="dish-card-arrow">
                  <text style="font-size:24rpx; color:#cbd5e1;">›</text>
                </view>
              </view>
            </view>
          </view>

          <view class="plan-todo-section">
            <view class="plan-todo-header">
              <view class="plan-desc-header">
                <view class="plan-desc-icon-wrap plan-todo-icon-wrap">
                  <text style="font-size:24rpx;">✅</text>
                </view>
                <text class="plan-desc-title">执行待办</text>
              </view>
              <view class="plan-todo-add-btn tap-effect" @click="showPlanTodoAdd = true">
                <text style="font-size:24rpx; color:#10b981; font-weight:700;">+ 添加</text>
              </view>
            </view>
            <view v-if="showPlanTodoAdd" class="plan-todo-add-form">
              <input v-model="newPlanTodoTitle" placeholder="输入待办事项..." class="plan-todo-input" />
              <view class="plan-todo-add-actions">
                <view class="plan-todo-add-confirm tap-effect" @click="addPlanTodo">确认</view>
                <view class="plan-todo-add-cancel tap-effect" @click="showPlanTodoAdd = false; newPlanTodoTitle = ''">取消</view>
              </view>
            </view>
            <view class="plan-todo-list">
              <view class="plan-todo-item" v-for="(todo, tIdx) in planTodos" :key="todo.id" @click="togglePlanTodo(tIdx)">
                <view class="plan-todo-checkbox" :class="{ checked: todo.done }">
                  <text v-if="todo.done" class="check-mark">✓</text>
                </view>
                <text class="plan-todo-text" :class="{ 'tx-del': todo.done }">{{ todo.title }}</text>
                <view class="plan-todo-delete tap-effect" @click.stop="deletePlanTodo(todo.id)">
                  <text style="font-size:24rpx; color:#cbd5e1;">×</text>
                </view>
              </view>
            </view>
            <view v-if="planTodos.length === 0" class="plan-todo-empty">
              <text class="plan-todo-empty-text">暂无待办事项，点击添加"创建</text>
            </view>
          </view>
          <view style="height: 20rpx;"></view>
        </scroll-view>

        <view class="plan-detail-footer">
          <view class="plan-apply-btn tap-effect" @click="applyPlan(selectedPlan)">
            <text style="font-size:28rpx; font-weight:700; color:white;">应用此计划</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 资源详情弹窗 -->
    <view class="modal-overlay" v-if="showDishDetail" @click="showDishDetail = false">
      <view class="dish-detail-modal" @click.stop>
        <view class="modal-drag-bar"></view>
        <view class="dish-detail-header">
          <view class="dish-detail-header-left">
            <view class="dish-detail-emoji">{{ getDishEmoji(selectedDish.name) }}</view>
            <text class="dish-detail-name">{{ selectedDish.name }}</text>
          </view>
          <view class="dish-detail-close" @click="showDishDetail = false">
            <text style="font-size:28rpx; color:#64748b;">✕</text>
          </view>
        </view>
        <scroll-view class="dish-detail-content" scroll-y="true" :show-scrollbar="false" enhanced :bounces="true">
          <view class="dish-health-overview">
            <text class="dish-overview-text">{{ getHealthOverview(selectedDish) }}</text>
          </view>
          <view class="dish-meta-row">
            <view class="dish-meta-chip meta-cal">
              <text class="meta-chip-val">{{ selectedDish.calories }}</text>
              <text class="meta-chip-label">作业点</text>
            </view>
            <view class="dish-meta-chip meta-time">
              <text class="meta-chip-val">{{ selectedDish.cooking_time }}</text>
              <text class="meta-chip-label">分钟</text>
            </view>
            <view class="dish-meta-chip meta-diff">
              <text class="meta-chip-val">{{ selectedDish.difficulty }}</text>
              <text class="meta-chip-label">难度</text>
            </view>
          </view>
          <view class="dish-section">
            <view class="dish-section-header">
              <view class="section-icon-wrap section-icon-ingredient">
                <text style="font-size:24rpx;">🥬</text>
              </view>
              <text class="dish-section-title">资源清单</text>
            </view>
            <view class="dish-ingredients">
              <view class="dish-ingredient-item" v-for="(ing, iIdx) in selectedDish.ingredients" :key="iIdx">
                <view class="ingredient-dot"></view>
                <text class="ingredient-text">{{ ing }}</text>
              </view>
            </view>
          </view>
          <view class="dish-section">
            <view class="dish-section-header">
              <view class="section-icon-wrap section-icon-step">
                <text style="font-size:24rpx;">🧑‍💻</text>
              </view>
              <text class="dish-section-title">作业步骤</text>
            </view>
            <view class="dish-steps">
              <view class="dish-step-item" v-for="(step, sIdx) in selectedDish.steps" :key="sIdx">
                <view class="step-num">{{ sIdx + 1 }}</view>
                <text class="step-text">{{ step }}</text>
              </view>
            </view>
          </view>
        </scroll-view>
      </view>
    </view>

    <!-- 自定义计划弹窗-->
    <view class="modal-overlay" v-if="showCustomPlanModal" @click="showCustomPlanModal = false">
      <view class="custom-plan-modal" @click.stop>
        <view class="modal-drag-bar"></view>
        <view class="custom-plan-header">
          <text class="custom-plan-title">✏️ 自定义作业计划</text>
          <view class="custom-plan-close" @click="showCustomPlanModal = false">
            <text style="font-size:32rpx; color:#64748b;">✕</text>
          </view>
        </view>
        <scroll-view class="custom-plan-content" scroll-y="true" :show-scrollbar="false" enhanced :bounces="true">
          <view class="custom-plan-desc-section">
            <view class="plan-desc-header">
              <view class="plan-desc-icon-wrap custom-desc-icon-wrap">
                <text style="font-size:24rpx;">💡</text>
              </view>
              <text class="plan-desc-title">填写指南</text>
            </view>
            <text class="plan-desc-text">请根据设备型号、故障现象、检修等级和现场约束填写信息。系统将结合设备画像智能生成标准作业计划，并动态推荐手册、案例、流程和多模态资料。</text>
          </view>

          <view class="form-group">
            <text class="form-label">计划名称</text>
            <input v-model="customPlan.name" placeholder="如：ZK-320过热检修计划" class="form-input" />
          </view>
          <view class="form-group">
            <text class="form-label">检修目标</text>
            <view class="form-options">
              <view class="form-option" v-for="(goal, gIdx) in planGoals" :key="gIdx"
                :class="{ active: customPlan.goal === goal.value }"
                @click="customPlan.goal = goal.value">
                <text class="form-option-icon">{{ goal.icon }}</text>
                <text class="form-option-text">{{ goal.label }}</text>
              </view>
            </view>
          </view>
          <view class="form-group">
            <text class="form-label">每日作业时长 (分钟)</text>
            <input v-model="customPlan.calories" type="number" placeholder="如：90" class="form-input" />
          </view>
          <view class="form-group">
            <text class="form-label">作业环节</text>
            <view class="form-options">
              <view class="form-option meal-option" v-for="(m, mIdx) in mealOptions" :key="mIdx"
                :class="{ active: customPlan.meals.includes(m.value) }"
                @click="toggleMealOption(m.value)">
                <text class="form-option-text">{{ m.label }}</text>
              </view>
            </view>
          </view>
          <view class="form-group">
            <text class="form-label">检修偏好</text>
            <view class="form-options wrap">
              <view class="form-option tag-option" v-for="(pref, pIdx) in dietPreferences" :key="pIdx"
                :class="{ active: customPlan.preferences.includes(pref) }"
                @click="togglePreference(pref)">
                <text class="form-option-text">{{ pref }}</text>
              </view>
            </view>
          </view>
          <view class="form-group">
            <text class="form-label">备注</text>
            <textarea v-model="customPlan.remark" placeholder="如：柜体过热、偏好图文流程和风险复核清单..." class="form-textarea" :maxlength="200"></textarea>
          </view>

          <view class="plan-todo-section">
            <view class="plan-todo-header">
              <view class="plan-desc-header">
                <view class="plan-desc-icon-wrap plan-todo-icon-wrap">
                  <text style="font-size:24rpx;">✅</text>
                </view>
                <text class="plan-desc-title">准备待办</text>
              </view>
              <view class="plan-todo-add-btn tap-effect" @click="showCustomTodoAdd = true">
                <text style="font-size:24rpx; color:#10b981; font-weight:700;">+ 添加</text>
              </view>
            </view>
            <view v-if="showCustomTodoAdd" class="plan-todo-add-form">
              <input v-model="newCustomTodoTitle" placeholder="输入待办事项..." class="plan-todo-input" />
              <view class="plan-todo-add-actions">
                <view class="plan-todo-add-confirm tap-effect" @click="addCustomTodo">确认</view>
                <view class="plan-todo-add-cancel tap-effect" @click="showCustomTodoAdd = false; newCustomTodoTitle = ''">取消</view>
              </view>
            </view>
            <view class="plan-todo-list">
              <view class="plan-todo-item" v-for="(todo, tIdx) in customPlanTodos" :key="todo.id" @click="toggleCustomTodo(tIdx)">
                <view class="plan-todo-checkbox" :class="{ checked: todo.done }">
                  <text v-if="todo.done" class="check-mark">✓</text>
                </view>
                <text class="plan-todo-text" :class="{ 'tx-del': todo.done }">{{ todo.title }}</text>
                <view class="plan-todo-delete tap-effect" @click.stop="deleteCustomTodo(todo.id)">
                  <text style="font-size:24rpx; color:#cbd5e1;">×</text>
                </view>
              </view>
            </view>
            <view v-if="customPlanTodos.length === 0" class="plan-todo-empty">
              <text class="plan-todo-empty-text">暂无待办事项，点击添加"创建</text>
            </view>
          </view>
          <view style="height: 20rpx;"></view>
        </scroll-view>
        <view class="custom-plan-footer">
          <view class="custom-plan-cancel tap-effect" @click="showCustomPlanModal = false">
            <text style="font-size:28rpx; font-weight:600; color:#64748b;">取消</text>
          </view>
          <view class="custom-plan-confirm tap-effect" @click="saveCustomPlan">
            <text style="font-size:28rpx; font-weight:600; color:white;">生成方案</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 检修记录弹窗 -->
    <view class="modal-overlay" v-if="showAddFoodModal" @click="showAddFoodModal = false">
      <view class="dish-detail-modal" @click.stop>
        <view class="modal-drag-bar"></view>
        <view class="dish-detail-header">
          <text class="dish-detail-name">📘 记录检修</text>
          <view class="dish-detail-close" @click="showAddFoodModal = false">
            <text style="font-size:28rpx; color:#64748b;">✕</text>
          </view>
        </view>
        <scroll-view class="dish-detail-content" scroll-y="true" :show-scrollbar="false" enhanced :bounces="true">
          <view class="form-group">
            <text class="form-label">检修内容</text>
            <input v-model="newFood.name" placeholder="请输入检修内容" class="form-input" />
          </view>
          <view class="form-group">
            <text class="form-label">检修时间</text>
            <input v-model="newFood.time" type="datetime-local" class="form-input" />
          </view>
          <view class="form-group">
            <text class="form-label">检修时长 (分钟)</text>
            <input v-model="newFood.calories" type="number" placeholder="请输入检修时长" class="form-input" />
          </view>
          <view class="form-group">
            <text class="form-label">备注</text>
            <textarea v-model="newFood.notes" placeholder="添加掌握度、错因或资源反馈" class="form-textarea" :maxlength="200"></textarea>
          </view>
          <view class="form-group">
            <text class="form-label">检修照片</text>
            <view class="image-upload-section">
              <view v-if="newFood.image" class="uploaded-image">
                <image :src="newFood.image" mode="aspectFill"></image>
                <view class="remove-image-btn tap-effect" @click="newFood.image = ''">
                  <text style="color:#ef4444; font-size:28rpx;">×</text>
                </view>
              </view>
              <view v-else class="upload-btn tap-effect" @click="uploadImage">
                <text style="font-size:48rpx;">📷</text>
                <text style="font-size:24rpx; color:#64748b; margin-top:16rpx;">点击上传截图</text>
              </view>
            </view>
          </view>
        </scroll-view>
        <view class="custom-plan-footer">
          <view class="custom-plan-cancel tap-effect" @click="showAddFoodModal = false; resetNewFood()">
            <text style="font-size:28rpx; font-weight:600; color:#64748b;">取消</text>
          </view>
          <view class="custom-plan-confirm tap-effect" @click="addFoodRecord">
            <text style="font-size:28rpx; font-weight:600; color:white;">保存记录</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 健康知识提示弹窗 -->
    <view class="modal-overlay" v-if="showHealthTipModal" @click="showHealthTipModal = false">
      <view class="health-tip-modal" @click.stop>
        <view class="modal-drag-bar"></view>
        <view class="health-tip-header">
          <text class="health-tip-title">📘 检修小提示</text>
          <view class="health-tip-close" @click="showHealthTipModal = false">
            <text style="font-size:28rpx; color:#64748b;">✕</text>
          </view>
        </view>
        <view class="health-tip-content">
          <text class="health-tip-text">{{ currentHealthTip }}</text>
        </view>
        <view class="health-tip-footer">
          <view class="health-tip-btn tap-effect" @click="showHealthTipModal = false">
            <text style="font-size:28rpx; font-weight:700; color:white;">我知道了</text>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import request from '../../utils/request.js'
import HealthManagerFab from '@/src/components/HealthManagerFab/HealthManagerFab.vue'

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
      healthTips: [
        '先用自然语言说清楚设备型号、故障现象、检修等级和现场约束，司南会自动抽取作业特征',
        '开始作业前建议先看检修手册，再核对相似案例，最后执行标准流程',
        '遇到复杂故障时，可以要求系统生成图文排查链路或风险复核清单',
        '对生成内容要查看知识库依据，避免大模型幻觉影响现场判断',
        '高频故障点会随检修结果动态更新，作业路径也会同步调整',
        '建议每次检修后记录合规评分，方便司南优化流程推送',
        '现场检修优先结合历史案例和标准作业票，比单纯阅读手册更容易闭环',
        '当合规评分低于 70 分时，先回到安全确认、验电和复核节点补齐记录'
      ],
      showHealthTipModal: false,
      currentHealthTip: '',
      contactKeyword: '',
      activeContactId: 1,
      contactChatOpen: false,
      messageDraft: '',
      quickMessages: ['需要现场支援', '请协助确认故障原因', '麻烦验收一下', '已上传现场照片'],
      contacts: [
        {
          id: 1,
          name: '聪明的一修',
          role: '电气检修',
          avatar: '泽',
          bg: '#eff6ff',
          status: 'online',
          skill: '配电柜、温升异常、端子排查',
          lastMessage: 'ZK-320 配电柜我可以协助复核温升。',
          time: '刚刚',
          unread: 2,
          messages: [
            { text: 'ZK-320 配电柜我可以协助复核温升。', mine: false },
            { text: '收到，我先把红外测温照片同步给你。', mine: true }
          ]
        },
        {
          id: 2,
          name: '李志勇',
          role: '发动机检修',
          avatar: '李',
          bg: '#ecfdf5',
          status: 'online',
          skill: '发动机异响、点火系统、气门间隙',
          lastMessage: '异响任务建议先复核气门间隙。',
          time: '5分钟前',
          unread: 0,
          messages: [
            { text: '异响任务建议先复核气门间隙。', mine: false },
            { text: '我看完手册后再同步检查结果。', mine: true }
          ]
        },
        {
          id: 3,
          name: '唐忆罗',
          role: '质检验收',
          avatar: '罗',
          bg: '#fff7ed',
          status: 'busy',
          skill: '验收复核、作业票、合规评分',
          lastMessage: '待验收任务先补齐复位前照片。',
          time: '18分钟前',
          unread: 1,
          messages: [
            { text: '待验收任务先补齐复位前照片。', mine: false }
          ]
        },
        {
          id: 4,
          name: '陈程',
          role: '机械维修',
          avatar: '程',
          bg: '#f5f3ff',
          status: 'offline',
          skill: '液压系统、密封件、更换调试',
          lastMessage: '液压千斤顶油封型号我晚点发你。',
          time: '1小时前',
          unread: 0,
          messages: [
            { text: '液压千斤顶油封型号我晚点发你。', mine: false }
          ]
        }
      ],
      taskTabs: [
        { label: '全部', key: 'all' },
        { label: '待处理', key: 'pending' },
        { label: '进行中', key: 'in_progress' },
        { label: '待验收', key: 'completed' },
        { label: '已完成', key: 'verified' }
      ],
      currentTaskStatus: 'pending',
      taskKeyword: '',
      taskListExpanded: false,
      tasks: [],
      taskLoading: false,
      showAddModal: false,
      newTaskTitle: '',
      newTaskDescription: '',
      newTaskAssignee: '',
      // 检修记录相关
      showAddFoodModal: false,
      newFood: {
        name: '',
        time: '',
        calories: '',
        notes: '',
        image: ''
      },
      foodRecords: [],
      weeklyTrend: [
        { label: '一', value: 75 },
        { label: '二', value: 82 },
        { label: '三', value: 68 },
        { label: '四', value: 90 },
        { label: '五', value: 85 },
        { label: '六', value: 78 },
        { label: '日', value: 88 }
      ],
      monthlyData: [
        { month: '10月', value: 80 },
        { month: '11月', value: 70 },
        { month: '12月', value: 60 }
      ],
      monthlyActivity: [
        { month: '10月', value: 70 },
        { month: '11月', value: 78 },
        { month: '12月', value: 85 }
      ],
      goalTemplates: [
        {
          name: '配电柜标准检修计划', icon: '📚', desc: '按设备状态逐步完成标准检修流程',
          totalCalories: 90, protein: 3, carbs: 2, fat: 1,
          meals: [
            {
              type: '作业准备', icon: '📘', calories: 20,
              dishes: [
                { name: '配电柜检修手册摘要', image: '', calories: 8, cooking_time: 8, difficulty: '入门', ingredients: ['设备资料库', '设备画像', '关键部件'], steps: ['阅读安全条款', '标记关键风险', '向问修智能体追问细节'] },
                { name: '过热故障排查图谱', image: '', calories: 6, cooking_time: 6, difficulty: '入门', ingredients: ['端子松动', '风道堵塞', '负载异常'], steps: ['查看故障链路', '对比适用场景', '记录易漏项'] },
                { name: '安全合规短案例', image: '', calories: 6, cooking_time: 6, difficulty: '入门', ingredients: ['挂牌上锁', '防幻觉校验', '资料可信度'], steps: ['阅读案例', '指出风险点', '查看知识库依据'] }
              ]
            },
            {
              type: '流程复核', icon: '🧠', calories: 25,
              dishes: [
                { name: '作业票要点摘要', image: '', calories: 10, cooking_time: 10, difficulty: '基础', ingredients: ['作业票模板', '检修规程', '现场记录'], steps: ['按步骤生成摘要', '补充关键复核项', '生成三条安全确认问题'] },
                { name: '故障原因辨析清单', image: '', calories: 8, cooking_time: 8, difficulty: '基础', ingredients: ['易漏原因', '判断项', '复核项'], steps: ['完成10项检查', '查看原因解析', '更新薄弱点画像'] },
                { name: '知识库依据核验', image: '', calories: 7, cooking_time: 7, difficulty: '基础', ingredients: ['检修知识库片段', '生成内容引用', '安全审核规则'], steps: ['查看引用来源', '标记无依据内容', '重新生成存疑段落'] }
              ]
            },
            {
              type: '现场执行', icon: '📝', calories: 25,
              dishes: [
                { name: '分级检修任务包', image: '', calories: 12, cooking_time: 12, difficulty: '基础', ingredients: ['基础检查', '进阶排查', '问题追踪'], steps: ['先做安全确认', '问题自动归因', '根据结果调整流程'] },
                { name: '端子温升复核记录', image: '', calories: 8, cooking_time: 8, difficulty: '基础', ingredients: ['热成像图', '测温过程', '复核结果'], steps: ['记录测温顺序', '对照标准阈值', '记录异常步骤'] }
              ]
            },
            {
              type: '结果闭环', icon: '💻', calories: 20,
              dishes: [
                { name: '复位前安全确认', image: '', calories: 12, cooking_time: 12, difficulty: '进阶', ingredients: ['复位清单', '现场照片', '测试记录'], steps: ['核对复位条件', '补充确认照片', '解释处置结论'] },
                { name: '检修复盘卡片', image: '', calories: 8, cooking_time: 8, difficulty: '基础', ingredients: ['现场照片', '异常记录', '修复建议'], steps: ['记录处置结果', '总结关键收获', '同步到设备画像'] }
              ]
            }
          ]
        },
        {
          name: '过热故障专项排查计划', icon: '🧭', desc: '围绕温升异常、端子松动和风道堵塞强化排查',
          totalCalories: 100, protein: 2, carbs: 3, fat: 2,
          meals: [
            {
              type: '前置核对', icon: '🧩', calories: 20,
              dishes: [
                { name: '设备铭牌速查', image: '', calories: 8, cooking_time: 8, difficulty: '基础', ingredients: ['设备型号', '额定参数', '运行环境'], steps: ['阅读速查表', '完成参数核对', '确认前置条件'] },
                { name: '过热/异响对比讲解', image: '', calories: 12, cooking_time: 12, difficulty: '基础', ingredients: ['故障现象', '排查顺序', '适用场景'], steps: ['看对比图', '推演两个案例', '生成风险提醒'] }
              ]
            },
            {
              type: '专项排查', icon: '🎯', calories: 35,
              dishes: [
                { name: '温升异常分步排查', image: '', calories: 15, cooking_time: 15, difficulty: '进阶', ingredients: ['测温记录', '负载电流', '端子状态'], steps: ['逐步核对温升', '选择下一个检查点', '解释故障路径原因'] },
                { name: '相似检修案例库', image: '', calories: 10, cooking_time: 10, difficulty: '进阶', ingredients: ['端子松动', '风道堵塞', '接触电阻'], steps: ['比较案例差异', '判断是否匹配', '生成反例说明'] },
                { name: '问题归因训练', image: '', calories: 10, cooking_time: 10, difficulty: '基础', ingredients: ['检修记录', '原因标签', '补救资源'], steps: ['查看异常记录', '选择原因', '推送对应手册'] }
              ]
            },
            {
              type: '现场实操', icon: '💻', calories: 30,
              dishes: [
                { name: '配电柜过热处置案例', image: '', calories: 18, cooking_time: 18, difficulty: '进阶', ingredients: ['现场照片', '作业票模板', '处理结论'], steps: ['运行检查清单', '替换设备参数', '截图对比结果'] },
                { name: '作业记录自动总结', image: '', calories: 12, cooking_time: 12, difficulty: '基础', ingredients: ['记录片段', '变量说明', '执行流程'], steps: ['上传记录', '生成逐项解释', '提取复盘问答'] }
              ]
            },
            {
              type: '质量评估', icon: '📈', calories: 15,
              dishes: [
                { name: '专项合规度报告', image: '', calories: 8, cooking_time: 8, difficulty: '基础', ingredients: ['合规率', '完成时长', '流程覆盖'], steps: ['查看雷达图', '确认达标项', '生成下一阶段计划'] },
                { name: '个性化整改包', image: '', calories: 7, cooking_time: 7, difficulty: '基础', ingredients: ['薄弱点', '同类案例', '讲解脚本'], steps: ['选择薄弱点', '生成整改包', '加入今日待办'] }
              ]
            }
          ]
        },
        {
          name: '检修知识沉淀演示计划', icon: '🤖', desc: '面向竞赛作品展示的多智能体协同检修任务',
          totalCalories: 120, protein: 4, carbs: 2, fat: 2,
          meals: [
            {
              type: '主题导入', icon: '🚀', calories: 25,
              dishes: [
                { name: '多智能体架构讲解', image: '', calories: 12, cooking_time: 12, difficulty: '进阶', ingredients: ['司南', '墨灵', '藏典'], steps: ['阅读架构说明', '理解协作流程', '提炼展示话术'] },
                { name: '防幻觉机制卡片', image: '', calories: 13, cooking_time: 13, difficulty: '进阶', ingredients: ['知识库检索', '引用校验', '安全审核'], steps: ['查看机制图', '识别风险样例', '生成修正建议'] }
              ]
            },
            {
              type: '资料生成', icon: '📚', calories: 35,
              dishes: [
                { name: '五类检修资料生成演示', image: '', calories: 20, cooking_time: 20, difficulty: '进阶', ingredients: ['检修手册', '风险清单', '图谱', '案例', '作业脚本'], steps: ['输入设备故障', '选择资料类型', '查看进度提示与结果'] },
                { name: '多模态检修资料样例', image: '', calories: 15, cooking_time: 15, difficulty: '基础', ingredients: ['故障图片', '检修文本', '语音讲解稿'], steps: ['上传现场图片', '生成图文解析', '补充语音脚本'] }
              ]
            },
            {
              type: '作品展示', icon: '🏁', calories: 40,
              dishes: [
                { name: '竞赛演示路径', image: '', calories: 18, cooking_time: 18, difficulty: '进阶', ingredients: ['设备画像', '资料生成', '路径规划', '效果评估'], steps: ['按演示顺序操作', '记录关键截图', '准备答辩说明'] },
                { name: '答辩问答卡片', image: '', calories: 12, cooking_time: 12, difficulty: '基础', ingredients: ['赛题要求', '创新点', '安全策略'], steps: ['生成常见问题', '补充技术亮点', '形成答辩卡片'] },
                { name: '功能完整性自检', image: '', calories: 10, cooking_time: 10, difficulty: '基础', ingredients: ['5类资源', '6维画像', '知识库依据'], steps: ['逐项检查', '标记缺口', '安排下一轮优化'] }
              ]
            }
          ]
        }
      ],
      showPlanDetail: false,
      selectedPlan: {},
      selectedPlanIndex: -1,
      planTodos: [
        { id: 1, title: '准备本周检修资料清单', done: false },
        { id: 2, title: '查看系统推荐路径依据', done: false },
        { id: 3, title: '记录每日检修打卡', done: false },
        { id: 4, title: '每周查看检修质量变化', done: false }
      ],
      showPlanTodoAdd: false,
      newPlanTodoTitle: '',
      showDishDetail: false,
      selectedDish: {},
      showCustomPlanModal: false,
      customPlanTodos: [
        { id: 1, title: '确认设备型号与检修目标', done: false },
        { id: 2, title: '设定每日检修时长目标', done: false },
        { id: 3, title: '选择合适的作业环节', done: false },
        { id: 4, title: '记录检修偏好与薄弱点', done: false },
        { id: 5, title: '开始执行并连续复盘一周', done: false }
      ],
      showCustomTodoAdd: false,
      newCustomTodoTitle: '',
      customPlan: {
        name: '',
        goal: 'foundation',
        calories: '90',
        meals: ['preview', 'review', 'practice'],
        preferences: [],
        remark: ''
      },
      planGoals: [
        { label: '快速定位', icon: '📘', value: 'foundation' },
        { label: '现场处置', icon: '💻', value: 'practice' },
        { label: '风险复核', icon: '📝', value: 'exam' },
        { label: '经验沉淀', icon: '🔍', value: 'research' }
      ],
      mealOptions: [
        { label: '作业准备', value: 'preview' },
        { label: '流程复核', value: 'review' },
        { label: '现场执行', value: 'practice' },
        { label: '结果闭环', value: 'project' }
      ],
      dietPreferences: ['图解优先', '案例驱动', '流程复核', '风险清单', '短视频讲解', '手册优先', '标准流程', '高风险提醒'],
      achievements: [
        { name: '画像完成', icon: '🧠', unlocked: true },
        { name: '七日连修', icon: '🔥', unlocked: true },
        { name: '案例达人', icon: '📝', unlocked: false },
        { name: '实操新星', icon: '💻', unlocked: false }
      ],
      // 检修质量风险相关
      riskLevel: '低风险',
      riskScore: 0,
      riskStatus: { text: '画像监测：当前流程稳定，建议进入过热故障专项排查', color: '#10b981' }
    }
  },
  computed: {
    bmi() {
      return '6维';
    },
    bmiStatus() {
      return { text: '画像完整', color: '#10b981', sub: '基础、目标、偏好、进度、易错点、资源反馈' };
    },
    filteredTasks() {
      const keyword = this.taskKeyword.trim().toLowerCase();
      return this.tasks.filter(task => {
        const statusMatched = this.currentTaskStatus === 'all' || task.status === this.currentTaskStatus;
        if (!statusMatched) return false;
        if (!keyword) return true;
        return [
          task.title,
          task.description,
          task.equipment_name,
          task.equipment_model,
          task.assignee_name,
          task.fault_code
        ].some(value => String(value || '').toLowerCase().includes(keyword));
      });
    },
    visibleTasks() {
      return this.taskListExpanded ? this.filteredTasks : this.filteredTasks.slice(0, 3);
    },
    activeTaskCount() {
      return this.tasks.filter(t => t.status !== 'verified').length;
    },
    highRiskTaskCount() {
      return this.tasks.filter(t => ['high', 'critical'].includes(t.severity)).length;
    },
    filteredContacts() {
      const keyword = this.contactKeyword.trim().toLowerCase();
      if (!keyword) return this.contacts;
      return this.contacts.filter(contact => [
        contact.name,
        contact.role,
        contact.skill,
        contact.lastMessage
      ].some(value => String(value || '').toLowerCase().includes(keyword)));
    },
    activeContact() {
      return this.contacts.find(contact => contact.id === this.activeContactId) || this.contacts[0];
    },
    onlineContactCount() {
      return this.contacts.filter(contact => contact.status === 'online').length;
    },
    currentTaskLabel() {
      const tab = this.taskTabs.find(item => item.key === this.currentTaskStatus);
      return tab ? tab.label : '';
    },
    taskMetrics() {
      return [
        { label: '总任务', key: 'total', filterKey: 'all', count: this.tasks.length, icon: '📋', color: '#0f172a', bg: '#f8fafc' },
        { label: '待处理', key: 'pending', filterKey: 'pending', count: this.tasks.filter(t => t.status === 'pending').length, icon: '🕒', color: '#d97706', bg: '#fffbeb' },
        { label: '进行中', key: 'in_progress', filterKey: 'in_progress', count: this.tasks.filter(t => t.status === 'in_progress').length, icon: '🔧', color: '#2563eb', bg: '#eff6ff' },
        { label: '待验收', key: 'completed', filterKey: 'completed', count: this.tasks.filter(t => t.status === 'completed').length, icon: '🧾', color: '#16a34a', bg: '#ecfdf5' },
        { label: '已完成', key: 'verified', filterKey: 'verified', count: this.tasks.filter(t => t.status === 'verified').length, icon: '✅', color: '#059669', bg: '#ecfdf5' },
        { label: '高风险/超时', key: 'risk', filterKey: 'all', count: this.highRiskTaskCount + this.overdueTaskCount, icon: '⚠️', color: '#dc2626', bg: '#fef2f2' }
      ];
    },
    taskCompletionOverview() {
      const total = this.tasks.length;
      const verified = this.tasks.filter(t => t.status === 'verified').length;
      const completed = this.tasks.filter(t => t.status === 'completed').length;
      const inProgress = this.tasks.filter(t => t.status === 'in_progress').length;
      const pending = this.tasks.filter(t => t.status === 'pending').length;
      const completionRate = total ? Math.round((verified / total) * 100) : 0;
      const acceptanceRate = total ? Math.round(((verified + completed) / total) * 100) : 0;
      let healthLabel = '暂无任务数据，刷新后查看完整状况';
      if (total && completionRate >= 80) healthLabel = '多数任务已完成闭环，保持验收节奏';
      else if (total && acceptanceRate >= 60) healthLabel = '任务推进良好，重点处理待验收记录';
      else if (total) healthLabel = '仍有任务待推进，建议优先处理高风险与超时项';
      return {
        total,
        verified,
        completed,
        inProgress,
        pending,
        overdue: this.overdueTaskCount,
        highRisk: this.highRiskTaskCount,
        completionRate,
        acceptanceRate,
        healthLabel
      };
    },
    maintenanceAgentContext() {
      const overview = this.taskCompletionOverview;
      return {
        page: '检修任务',
        active_tab: ['今日概览', '复检评估', '联系人'][this.activeTab] || '今日概览',
        current_filter: this.currentTaskLabel || '全部',
        overview,
        metrics: this.taskMetrics.map(item => ({
          label: item.label,
          count: item.count
        })),
        visible_tasks: this.visibleTasks.map(task => ({
          title: task.title,
          description: task.description,
          equipment: `${task.equipment_name || ''} ${task.equipment_model || ''}`.trim(),
          status: this.getStatusText(task.status),
          severity: this.getSeverityText(task.severity),
          assignee: this.getAssigneeName(task),
          deadline: this.getTaskDeadline(task)
        })),
        selected_plan: this.selectedPlan ? {
          name: this.selectedPlan.name,
          desc: this.selectedPlan.desc,
          total_minutes: this.selectedPlan.totalCalories,
          meals: (this.selectedPlan.meals || []).map(meal => ({
            type: meal.type,
            minutes: meal.calories,
            items: (meal.dishes || []).map(dish => dish.name)
          }))
        } : null
      };
    },
    overdueTaskCount() {
      return this.tasks.filter(t => this.isTaskOverdue(t)).length;
    }
  },
  mounted() {
    // 触发进度条、圆环的缓动加载动画
    setTimeout(() => {
      this.isLoaded = true;
      // 计算初始风险等级
      this.calculateRiskLevel();
    }, 100);
    
    // 读取已保存的计划选择
    const savedPlanIndex = uni.getStorageSync('selectedPlanIndex');
    if (savedPlanIndex !== undefined && savedPlanIndex !== '') {
      this.selectedPlanIndex = savedPlanIndex;
    }
    this.loadTasks();
  },
  methods: {
    getRiskStroke() {
      if (this.riskLevel === '低风险') return 'url(#mintGradient)'
      if (this.riskLevel === '中风险') return 'url(#orangeGradient)'
      return 'url(#redGradient)'
    },
    switchTab(index) {
      if (this.activeTab !== index) {
        this.activeTab = index;
        uni.vibrateShort && uni.vibrateShort(); // Haptic feedback if available
      }
    },
    switchTaskTab(key) {
      this.currentTaskStatus = key;
      this.taskListExpanded = false;
    },
    selectContact(id) {
      this.activeContactId = id;
      const contact = this.contacts.find(item => item.id === id);
      if (contact) contact.unread = 0;
    },
    openContactChat(id) {
      this.selectContact(id);
      this.contactChatOpen = true;
      this.messageDraft = '';
    },
    backToContacts() {
      this.contactChatOpen = false;
      this.messageDraft = '';
    },
    sendContactMessage() {
      const text = this.messageDraft.trim();
      const contact = this.activeContact;
      if (!text || !contact) {
        uni.showToast({ title: '请输入消息内容', icon: 'none' });
        return;
      }
      contact.messages.push({ text, mine: true });
      contact.lastMessage = text;
      contact.time = '刚刚';
      contact.unread = 0;
      this.messageDraft = '';
      uni.showToast({ title: '消息已发送', icon: 'success' });
    },
    callContact(contact) {
      uni.showToast({ title: '正在呼叫' + contact.name, icon: 'none' });
    },
    assignContact(contact) {
      uni.showToast({ title: '已邀请' + contact.name + '协作', icon: 'success' });
    },
    getContactStatusText(status) {
      return { online: '在线', busy: '忙碌', offline: '离线' }[status] || '未知';
    },
    showTaskFilterTip() {
      uni.showToast({ title: '可通过上方搜索快速筛选', icon: 'none' });
    },
    async loadTasks() {
      if (this.taskLoading) return;
      this.taskLoading = true;
      try {
        const res = await request.get('/api/maintenance-tasks/');
        if (res && res.code === 200 && res.data) {
          this.tasks = res.data.tasks || [];
        } else {
          this.tasks = this.getFallbackTasks();
        }
      } catch (e) {
        this.tasks = this.getFallbackTasks();
      } finally {
        this.taskLoading = false;
      }
    },
    goTaskDetail(id) {
      uni.navigateTo({ url: `/pages/task-detail/task-detail?id=${id}` });
    },
    getSeverityColor(severity) {
      return { low: '#10b981', medium: '#f59e0b', high: '#f97316', critical: '#ef4444' }[severity] || '#64748b';
    },
    getSeverityBg(severity) {
      return { low: '#ecfdf5', medium: '#fffbeb', high: '#fff7ed', critical: '#fef2f2' }[severity] || '#f1f5f9';
    },
    getSeverityText(severity) {
      return { low: '一般', medium: '中等', high: '紧急', critical: '严重' }[severity] || '未知';
    },
    getStatusBg(status) {
      return { pending: '#fffbeb', in_progress: '#eff6ff', completed: '#ecfdf5', verified: '#ecfdf5' }[status] || '#f1f5f9';
    },
    getStatusColor(status) {
      return { pending: '#d97706', in_progress: '#2563eb', completed: '#16a34a', verified: '#16a34a' }[status] || '#64748b';
    },
    getStatusText(status) {
      return { pending: '待处理', in_progress: '进行中', completed: '待验收', verified: '已完成' }[status] || status;
    },
    formatTaskTime(time) {
      if (!time) return '';
      return String(time).replace(/T/g, ' ').replace(/:\d{2}$/, '').slice(0, 16);
    },
    getTaskLocation(task) {
      return task.location || task.equipment_location || '现场待确认';
    },
    getTaskDeadline(task) {
      if (task.end_time) return this.formatTaskTime(task.end_time);
      if (task.start_time) return this.formatTaskTime(task.start_time);
      const time = this.formatTaskTime(task.created_at);
      return time ? time.slice(5) : '今日 18:00';
    },
    getAssigneeName(task) {
      const name = task.assignee_name || task.assignee?.name || '';
      const nameMap = {
        '张工': '聪明的一修',
        '李工': '李志勇',
        '王工': '唐忆罗',
        '赵工': '陈程'
      };
      return nameMap[name] || name || '未指派';
    },
    getAssigneeAvatar(task) {
      return task.assignee_avatar || task.assignee?.avatar || '';
    },
    getAssigneeInitial(task) {
      const name = this.getAssigneeName(task);
      return name && name !== '未指派' ? name.slice(-1) : '待';
    },
    getAssigneeAvatarBg(task) {
      const colors = {
        '聪明的一修': 'linear-gradient(135deg, #2563eb, #38bdf8)',
        '李志勇': 'linear-gradient(135deg, #0f766e, #34d399)',
        '唐忆罗': 'linear-gradient(135deg, #7c3aed, #c084fc)',
        '陈程': 'linear-gradient(135deg, #ea580c, #fbbf24)'
      };
      return colors[this.getAssigneeName(task)] || 'linear-gradient(135deg, #64748b, #94a3b8)';
    },
    getTaskProgress(task) {
      if (task.progress !== undefined) return Math.max(0, Math.min(100, Number(task.progress) || 0));
      return task.status === 'in_progress' ? 45 : 0;
    },
    getTaskActionText(status) {
      return { pending: '开始处理', in_progress: '继续处理', completed: '验收', verified: '查看报告' }[status] || '处理';
    },
    isTaskOverdue(task) {
      if (!task.created_at || ['completed', 'verified'].includes(task.status)) return false;
      const created = new Date(String(task.created_at).replace(/-/g, '/')).getTime();
      if (!created) return false;
      return Date.now() - created > 24 * 60 * 60 * 1000;
    },
    getFallbackTasks() {
      return [
        { id: 1, title: 'ZK-320配电柜过热检修', equipment_name: '配电柜', equipment_model: 'ZK-320', fault_code: 'E-001', description: '配电柜运行温度异常升高，红外测温显示局部超过80℃', severity: 'high', status: 'pending', assignee_name: '聪明的一修', assignee_avatar: '', created_at: '2026-06-10 09:30:00' },
        { id: 2, title: 'CG-125发动机异响排查', equipment_name: '摩托车发动机总成', equipment_model: 'CG-125', fault_code: 'E-002', description: '发动机启动后气门区域有明显异响，热车后略有减轻', severity: 'medium', status: 'in_progress', assignee_name: '李志勇', assignee_avatar: '', created_at: '2026-06-10 08:15:00' },
        { id: 3, title: '火花塞定期检查', equipment_name: '点火线圈', equipment_model: 'DLI-001', fault_code: '', description: '按维护计划对火花塞进行定期检查与间隙调整', severity: 'low', status: 'pending', assignee_name: '唐忆罗', assignee_avatar: '', created_at: '2026-06-10 07:00:00' },
        { id: 4, title: '液压千斤顶漏油处理', equipment_name: '液压千斤顶', equipment_model: 'YZ-50T', fault_code: 'E-003', description: '千斤顶油封老化导致液压油渗漏', severity: 'medium', status: 'in_progress', assignee_name: '陈程', assignee_avatar: '', created_at: '2026-06-09 13:30:00' },
        { id: 5, title: '发动机二级检修', equipment_name: '摩托车发动机总成', equipment_model: 'CG-125', fault_code: '', description: '按90天维护周期进行发动机二级检修', severity: 'low', status: 'completed', assignee_name: '聪明的一修', assignee_avatar: '', created_at: '2026-06-08 08:00:00' }
      ];
    },
    addTask() {
      const title = this.newTaskTitle.trim();
      if (!title) {
        uni.showToast({ title: '请输入任务名称', icon: 'none' });
        return;
      }
      const newTask = {
        id: Date.now(),
        title,
        equipment_name: '现场设备',
        equipment_model: '待确认型号',
        fault_code: '',
        description: this.newTaskDescription.trim() || '待补充故障描述与检修要求',
        severity: 'medium',
        status: 'pending',
        assignee_name: this.newTaskAssignee.trim() || '未指派',
        created_at: new Date().toISOString()
      };
      this.tasks.unshift(newTask);
      this.currentTaskStatus = 'pending';
      this.taskListExpanded = true;
      this.newTaskTitle = '';
      this.newTaskDescription = '';
      this.newTaskAssignee = '';
      this.showAddModal = false;
      uni.showToast({ title: '已加入任务列表', icon: 'success' });
    },
    acceptChallenge() {
      uni.showToast({ title: '已加入挑战！明天提醒你', icon: 'success' });
    },
    showAnnualReport() {
      uni.showModal({
        title: '年度总结',
        content: '这里将展示你的年度检修数据，包括质量趋势、资料使用分析、合规率变化等。（功能开发中）',
        showCancel: false
      });
    },
    applyTemplate(tpl) {
      uni.showModal({
        title: '确认应用计划？',
        content: tpl.desc,
        success: (res) => {
          if (res.confirm) {
            uni.showToast({ title: '已应用「' + tpl.name + '」', icon: 'success' });
          }
        }
      });
    },
    viewPlanDetail(tpl) {
      this.selectedPlan = tpl;
      this.showPlanDetail = true;
    },
    viewDishDetail(dish) {
      this.selectedDish = dish;
      this.showDishDetail = true;
    },
    applyPlan(plan) {
      this.showPlanDetail = false;
      uni.showToast({ title: '已应用「' + plan.name + '」方案', icon: 'success' });
      
      // 保存选择的计划到本地存储
      const planData = {
        name: plan.name,
        daysCompleted: 1,
        totalDays: 7,
        calories: plan.totalCalories,
        protein: plan.protein,
        carbs: plan.carbs,
        fat: plan.fat,
        completionRate: 15 // 初始完成度15%
      };
      uni.setStorageSync('selectedDietPlan', planData);
      
      // 发送事件更新个人中心的作业计划
      uni.$emit('diet-plan-updated', planData);
    },
    selectPlan(plan, index) {
      this.selectedPlanIndex = index;
      
      // 计算完成度（基于当前时间模拟）
      const completionRate = Math.floor(Math.random() * 40) + 20; // 20-60%之间的随机完成度
      
      const planData = {
        name: plan.name,
        daysCompleted: Math.floor(completionRate / 100 * 7),
        totalDays: 7,
        calories: plan.totalCalories,
        protein: plan.protein,
        carbs: plan.carbs,
        fat: plan.fat,
        completionRate: completionRate
      };
      
      // 保存到本地存储
      uni.setStorageSync('selectedDietPlan', planData);
      uni.setStorageSync('selectedPlanIndex', index);
      
      // 发送事件更新个人中心
      uni.$emit('diet-plan-updated', planData);
      
      uni.showToast({ title: '已选择「' + plan.name + '」', icon: 'success' });
    },
    getImageUrl(imagePath) {
      if (!imagePath) {
        return '../../static/food.png';
      }
      if (imagePath.startsWith('http')) {
        return imagePath;
      }
      return '../../static/' + imagePath;
    },
    handleImageError(e) {
      e.target.src = '../../static/food.png';
    },
    getDishEmoji(name) {
      const emojiMap = {
        '手册': '📘', '文档': '📘', '导图': '🧭', '图谱': '🧭',
        '清单': '📝', '排查': '📝', '风险': '⚠️',
        '流程': '💻', '实操': '💻', '案例': '📚',
        '报告': '📊', '评估': '📈', '展示': '🏁',
        '智能体': '🤖', '项目': '🚀'
      };
      for (const [key, emoji] of Object.entries(emojiMap)) {
        if (name.includes(key)) {
          return emoji;
        }
      }
      return '📘';
    },
    getHealthDesc(dish) {
      const cal = dish.calories || 0;
      const time = dish.cooking_time || 0;
      if (cal <= 100) return '轻量资料，适合快速复盘';
      if (cal <= 200) return '手册结合案例，日常检修之选';
      if (cal <= 350) return '现场导向，补充实践能力';
      if (time <= 10) return '快速核对，几分钟完成';
      if (time <= 20) return '步骤清晰，新手也能上手';
      return '深度检修，适合完整时段';
    },
    getHealthOverview(dish) {
      const cal = dish.calories || 0;
      const time = dish.cooking_time || 0;
      const diff = dish.difficulty || '简单';
      const ingCount = (dish.ingredients || []).length;
      let overview = '';
      if (cal <= 100) {
        overview += '这份资料很轻量，适合作业前核对或作业后快速复盘。';
      } else if (cal <= 200) {
        overview += '这份资料难度适中，手册与案例搭配合理，适合日常检修。';
      } else if (cal <= 350) {
        overview += '这份资料更偏现场实操，适合补充实践能力。';
      } else {
        overview += '这份资料信息量较大，建议拆分执行并搭配风险复核。';
      }
      if (time <= 10) {
        overview += '核对仅需' + time + '分钟，非常适合碎片时间。';
      } else if (time <= 20) {
        overview += '检修需' + time + '分钟，步骤清晰不复杂。';
      } else {
        overview += '需要' + time + '分钟深度检修，适合完整时段。';
      }
      overview += '共包含' + ingCount + '类资料，' + (diff === '简单' ? '难度较低，新手友好。' : '有一定挑战度，适合进阶作业。');
      return overview;
    },
    toggleMealOption(value) {
      const idx = this.customPlan.meals.indexOf(value);
      if (idx > -1) {
        this.customPlan.meals.splice(idx, 1);
      } else {
        this.customPlan.meals.push(value);
      }
    },
    togglePreference(pref) {
      const idx = this.customPlan.preferences.indexOf(pref);
      if (idx > -1) {
        this.customPlan.preferences.splice(idx, 1);
      } else {
        this.customPlan.preferences.push(pref);
      }
    },
    saveCustomPlan() {
      if (!this.customPlan.name.trim()) {
        uni.showToast({ title: '请输入计划名称', icon: 'none' });
        return;
      }
      if (!this.customPlan.calories || parseInt(this.customPlan.calories) <= 0) {
        uni.showToast({ title: '请输入有效的目标检修时长', icon: 'none' });
        return;
      }
      if (this.customPlan.meals.length === 0) {
        uni.showToast({ title: '请至少选择一项', icon: 'none' });
        return;
      }
      const goalMap = { foundation: '快速定位', practice: '现场处置', exam: '风险复核', research: '经验沉淀' };
      const goalIconMap = { foundation: '📘', practice: '💻', exam: '📝', research: '🔍' };
      const goal = this.customPlan.goal;
      const calories = parseInt(this.customPlan.calories);
      const protein = Math.max(1, this.customPlan.preferences.length || 2);
      const carbs = Math.max(1, this.customPlan.meals.length);
      const fat = this.customPlan.meals.includes('project') ? 2 : 1;
      const mealNameMap = { preview: '作业准备', review: '流程复核', practice: '现场执行', project: '结果闭环' };
      const mealIconMap = { preview: '📘', review: '🧠', practice: '📝', project: '💻' };
      const resourceMap = {
        preview: [
          { name: '个性化作业准备', difficulty: '入门', ingredients: ['检修知识库', '设备画像', '关键部件'], steps: ['生成准备摘要', '标记风险点', '加入今日待办'] },
          { name: '故障链路图谱', difficulty: '入门', ingredients: ['故障结构', '前置检查', '检修目标'], steps: ['查看图谱', '补齐前置资料', '保存复盘问题'] }
        ],
        review: [
          { name: '流程复核报告', difficulty: '基础', ingredients: ['作业记录', '复核反馈', '易漏点'], steps: ['整理重点', '生成原因', '更新画像'] },
          { name: '知识库依据核验', difficulty: '基础', ingredients: ['生成答案', '引用片段', '安全规则'], steps: ['核对依据', '标注存疑内容', '重新生成'] }
        ],
        practice: [
          { name: '分级检修任务包', difficulty: '基础', ingredients: ['基础检查', '进阶排查', '问题记录'], steps: ['完成检查', '查看解析', '调整路径'] },
          { name: '问题复核包', difficulty: '基础', ingredients: ['异常记录', '同类案例', '提示卡'], steps: ['重做复核', '比较结果', '确认闭环'] }
        ],
        project: [
          { name: '现场案例任务', difficulty: '进阶', ingredients: ['作业模板', '现场数据', '测试记录'], steps: ['执行案例', '修改参数', '提交复盘'] },
          { name: '检修讲解脚本', difficulty: '进阶', ingredients: ['作业目标', '记录片段', '答辩要点'], steps: ['生成脚本', '补充截图', '准备展示'] }
        ]
      };
      const meals = this.customPlan.meals.map((m) => {
        const mealMinutes = Math.round(calories / this.customPlan.meals.length);
        const dishes = (resourceMap[m] || resourceMap.preview).map((r, idx) => ({
          ...r,
          image: '',
          calories: Math.max(5, Math.round(mealMinutes / 2) - idx * 2),
          cooking_time: Math.max(5, Math.round(mealMinutes / 2) - idx * 2)
        }));
        return { type: mealNameMap[m], icon: mealIconMap[m], calories: mealMinutes, dishes };
      });
      const newPlan = {
        name: this.customPlan.name,
        icon: goalIconMap[goal],
        desc: (goalMap[goal] || '自定义') + ' · ' + calories + '分钟/天',
        totalCalories: calories,
        protein: protein,
        carbs: carbs,
        fat: fat,
        meals: meals
      };
      this.goalTemplates.push(newPlan);
      this.showCustomPlanModal = false;
      this.customPlan = {
        name: '',
        goal: 'foundation',
        calories: '90',
        meals: ['preview', 'review', 'practice'],
        preferences: [],
        remark: ''
      };
      uni.showToast({ title: '方案已生成！', icon: 'success' });
    },
    togglePlanTodo(index) {
      if (this.planTodos[index]) {
        this.planTodos[index].done = !this.planTodos[index].done;
        uni.vibrateShort && uni.vibrateShort();
      }
    },
    addPlanTodo() {
      if (!this.newPlanTodoTitle.trim()) {
        uni.showToast({ title: '请输入待办内容', icon: 'none' });
        return;
      }
      this.planTodos.push({
        id: Date.now(),
        title: this.newPlanTodoTitle,
        done: false
      });
      this.newPlanTodoTitle = '';
      this.showPlanTodoAdd = false;
      uni.showToast({ title: '已添加', icon: 'success' });
    },
    deletePlanTodo(id) {
      this.planTodos = this.planTodos.filter(t => t.id !== id);
      uni.showToast({ title: '已删除', icon: 'success' });
    },
    toggleCustomTodo(index) {
      if (this.customPlanTodos[index]) {
        this.customPlanTodos[index].done = !this.customPlanTodos[index].done;
        uni.vibrateShort && uni.vibrateShort();
      }
    },
    addCustomTodo() {
      if (!this.newCustomTodoTitle.trim()) {
        uni.showToast({ title: '请输入待办内容', icon: 'none' });
        return;
      }
      this.customPlanTodos.push({
        id: Date.now(),
        title: this.newCustomTodoTitle,
        done: false
      });
      this.newCustomTodoTitle = '';
      this.showCustomTodoAdd = false;
      uni.showToast({ title: '已添加', icon: 'success' });
    },
    deleteCustomTodo(id) {
      this.customPlanTodos = this.customPlanTodos.filter(t => t.id !== id);
      uni.showToast({ title: '已删除', icon: 'success' });
    },
    showHealthTip() {
      const randomIndex = Math.floor(Math.random() * this.healthTips.length);
      this.currentHealthTip = this.healthTips[randomIndex];
      this.showHealthTipModal = true;
    },
    // 检修记录相关方法
    addFoodRecord() {
      if (!this.newFood.name) {
        uni.showToast({ title: '请输入检修内容', icon: 'none' });
        return;
      }
      if (!this.newFood.time) {
        this.newFood.time = new Date().toISOString().slice(0, 16);
      }
      const foodRecord = {
        id: Date.now(),
        name: this.newFood.name,
        time: this.newFood.time,
        calories: this.newFood.calories,
        notes: this.newFood.notes,
        image: this.newFood.image
      };
      this.foodRecords.unshift(foodRecord);
      this.showAddFoodModal = false;
      this.resetNewFood();
      // 更新风险等级
      this.calculateRiskLevel();
      uni.showToast({ title: '记录添加成功', icon: 'success' });
    },
    deleteFoodRecord(id) {
      uni.showModal({
        title: '确认删除？',
        content: '确定要删除这条检修记录吗？',
        success: (res) => {
          if (res.confirm) {
            this.foodRecords = this.foodRecords.filter(food => food.id !== id);
            this.calculateRiskLevel();
            uni.showToast({ title: '记录已删除', icon: 'success' });
          }
        }
      });
    },
    uploadImage() {
      uni.chooseImage({
        count: 1,
        sizeType: ['compressed'],
        sourceType: ['album', 'camera'],
        success: (res) => {
          this.newFood.image = res.tempFilePaths[0];
        }
      });
    },
    resetNewFood() {
      this.newFood = {
        name: '',
        time: '',
        calories: '',
        notes: '',
        image: ''
      };
    },
    getFoodEmoji(foodName) {
      const foodEmojis = {
        '手册': '📘', '阅读': '📖', '导图': '🧭', '图谱': '🧭',
        '排查': '📝', '流程': '💻', '实操': '💻', '复盘': '🧠',
        '问题': '🔁', '报告': '📊', '案例': '📚', '项目': '🚀'
      };
      for (const [key, emoji] of Object.entries(foodEmojis)) {
        if (foodName.includes(key)) {
          return emoji;
        }
      }
      return '📘';
    },
    // 计算检修质量风险等级
    calculateRiskLevel() {
      let riskScore = 0;

      const today = new Date().toISOString().split('T')[0];
      const todayFoods = this.foodRecords.filter(food => food.time.startsWith(today));

      let totalMinutes = 0;
      let weakPointCount = 0;
      let practiceCount = 0;
      let reviewCount = 0;

      todayFoods.forEach(food => {
        if (food.calories) {
          totalMinutes += parseInt(food.calories);
        }

        const recordName = food.name.toLowerCase();
        if (recordName.includes('异常') || recordName.includes('薄弱') || recordName.includes('风险') || recordName.includes('困难')) {
          weakPointCount += 1;
        } else if (recordName.includes('排查') || recordName.includes('流程') || recordName.includes('实操') || recordName.includes('处置')) {
          practiceCount += 1;
        } else if (recordName.includes('复盘') || recordName.includes('阅读') || recordName.includes('手册') || recordName.includes('图谱')) {
          reviewCount += 1;
        }
      });

      if (totalMinutes < 30) {
        riskScore += 25;
      } else if (totalMinutes < 60) {
        riskScore += 10;
      }

      if (weakPointCount >= 3) {
        riskScore += 25;
      } else if (weakPointCount >= 1) {
        riskScore += 10;
      }

      if (practiceCount === 0 || reviewCount === 0) {
        riskScore += 15;
      }

      if (this.bmi === '6维') {
        riskScore = Math.max(0, riskScore - 10);
      }

      // 6. 确定风险等级
      let riskLevel, riskStatus;
      if (riskScore < 30) {
        riskLevel = '低风险';
        riskStatus = { text: '画像监测：当前流程稳定，建议进入专项排查', color: '#10b981' };
      } else if (riskScore < 60) {
        riskLevel = '中风险';
        riskStatus = { text: '画像监测：存在薄弱检修环节，建议调整作业路径', color: '#f59e0b' };
      } else {
        riskLevel = '高风险';
        riskStatus = { text: '画像监测：复检质量偏低，建议回到安全确认和前置检查', color: '#ef4444' };
      }
      
      // 更新状态
      this.riskLevel = riskLevel;
      this.riskScore = riskScore;
      this.riskStatus = riskStatus;
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

/* 0. Global Reset */
view, text, image, input, textarea, scroll-view {
  box-sizing: border-box;
}

/* 1. Global Page Style */
.modern-health-page {
  min-height: 100vh;
  background-color: #EEF3F8;
  padding: 72rpx 24rpx calc(216rpx + constant(safe-area-inset-bottom));
  padding: 72rpx 24rpx calc(216rpx + env(safe-area-inset-bottom));
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  overflow-x: hidden;
  overflow-y: visible;
  -webkit-overflow-scrolling: touch;
  box-sizing: border-box;
  position: relative;
}

/* 2. Header Section */
.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 18rpx;
  margin: 0 -24rpx 40rpx;
  padding: 36rpx 24rpx 30rpx;
  background: rgba(248, 250, 252, 0.92);
  border-bottom: 1rpx solid rgba(203, 213, 225, 0.68);
  backdrop-filter: blur(18rpx);
  -webkit-backdrop-filter: blur(18rpx);
  position: relative;
  top: auto;
  z-index: 50;
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 16rpx;
  flex: 1;
  min-width: 0;
}

.avatar-container {
  position: relative;
  width: 64rpx;
  height: 64rpx;
  border-radius: 18rpx;
  overflow: hidden;
  flex-shrink: 0;
}

.avatar {
  width: 100%;
  height: 100%;
  border-radius: 18rpx;
  display: block;
}

.greeting {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.greeting-title {
  font-size: 31rpx;
  font-weight: 800;
  color: #0f172a;
  letter-spacing: 0;
  line-height: 1.18;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.greeting-subtitle {
  font-size: 20rpx;
  color: #64748b;
  margin-top: 6rpx;
  line-height: 1.24;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.notification-btn {
  position: relative;
  width: auto;
  height: 48rpx;
  min-width: 86rpx;
  padding: 0 18rpx;
  background-color: #ECFDF5;
  border-radius: 999rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: none;
  flex-shrink: 0;
}

.icon-bell {
  font-size: 22rpx;
  color: #047857;
  font-weight: 800;
}

.red-dot {
  position: absolute;
  top: 8rpx;
  right: 12rpx;
  width: 10rpx;
  height: 10rpx;
  background-color: #ef4444; /* Red 500 */
  border-radius: 50%;
  border: 2rpx solid white;
}

/* 3. Dynamic Tabs */
.tabs-container {
  margin-bottom: 24rpx;
}

.tabs-bg {
  position: relative;
  display: flex;
  background-color: #E2E8F0; /* Slate 200 */
  border-radius: 999px;
  padding: 6rpx;
  box-shadow: inset 0 2rpx 4rpx rgba(0,0,0,0.05); /* Inner subtle shadow */
}

.tab-indicator {
  position: absolute;
  top: 6rpx;
  bottom: 6rpx;
  width: 33.33%;
  background-color: white;
  border-radius: 999px;
  box-shadow: 0 4rpx 12rpx rgba(15, 23, 42, 0.08);
  transition: left 0.4s cubic-bezier(0.34, 1.56, 0.64, 1); /* Bouncy slide easing */
}

.tab-item {
  flex: 1;
  text-align: center;
  padding: 14rpx 0;
  z-index: 1; /* Above indicator */
  position: relative;
}

.tab-item text {
  font-size: 24rpx;
  font-weight: 800;
  color: #64748b;
  transition: color 0.3s;
}

.tab-item.active text {
  color: #0f172a;
}

/* 健康知识提示弹窗 */
.health-tip-modal {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 85%;
  max-width: 500rpx;
  background-color: white;
  border-radius: 32rpx;
  box-shadow: 0 20rpx 40rpx rgba(0, 0, 0, 0.15);
  overflow: hidden;
  animation: modalSlideIn 0.3s ease-out;
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: translate(-50%, -60%);
  }
  to {
    opacity: 1;
    transform: translate(-50%, -50%);
  }
}

.health-tip-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 32rpx;
  border-bottom: 1rpx solid #e2e8f0;
}

.health-tip-title {
  font-size: 32rpx;
  font-weight: 700;
  color: #0f172a;
}

.health-tip-content {
  padding: 40rpx 32rpx;
  min-height: 200rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.health-tip-text {
  font-size: 28rpx;
  line-height: 1.6;
  color: #334155;
  text-align: center;
}

.health-tip-footer {
  padding: 0 32rpx 32rpx;
}

.health-tip-btn {
  width: 100%;
  background: linear-gradient(135deg, #10b981 0%, #0ea5e9 100%);
  padding: 24rpx;
  border-radius: 16rpx;
  text-align: center;
  box-shadow: 0 4rpx 12rpx rgba(16, 185, 129, 0.3);
  transition: all 0.3s ease;
}

.health-tip-btn:active {
  transform: translateY(2rpx);
  box-shadow: 0 2rpx 8rpx rgba(16, 185, 129, 0.2);
}

/* 4. Tab Content Sliding & Crossfade */
.tab-content-wrapper {
  position: relative;
  overflow: hidden;
  max-width: 100%;
}

.tab-content {
  display: none;
  opacity: 0;
  transform: translateY(20rpx);
  transition: all 0.4s ease;
  max-width: 100%;
  overflow: hidden;
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
  border-radius: 40rpx;
  padding: 32rpx;
  box-shadow: 0 16rpx 40rpx rgba(148, 163, 184, 0.1);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  max-width: 100%;
  word-break: break-word;
  overflow-wrap: break-word;
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
  font-size: 24rpx;
  color: #10b981;
  font-weight: 700;
  line-height: 1;
}

.lucide-icon.large { font-size: 48rpx; margin-bottom: 20rpx; opacity: 0.5; }

.banner-arrow {
  color: #ffffff;
}

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

.task-dashboard-card {
  grid-column: 1 / -1;
  background: linear-gradient(135deg, #ffffff 0%, #eef6ff 52%, #ecfdf5 100%);
}

.task-dashboard-main {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 18rpx;
}

.dashboard-label {
  display: block;
  font-size: 22rpx;
  color: #64748b;
  font-weight: 700;
}

.dashboard-value {
  display: block;
  margin-top: 8rpx;
  font-size: 68rpx;
  color: #0f172a;
  font-weight: 900;
  line-height: 1;
}

.dashboard-badge {
  flex-shrink: 0;
  border-radius: 999rpx;
  background: #ecfdf5;
  color: #16a34a;
  padding: 10rpx 18rpx;
  border: 1rpx solid #bbf7d0;
}

.dashboard-badge.warning {
  background: #fef2f2;
  color: #dc2626;
  border-color: #fecaca;
}

.dashboard-badge text {
  font-size: 22rpx;
  font-weight: 800;
}

.task-dashboard-track {
  height: 16rpx;
  background: #dbeafe;
  border-radius: 999rpx;
  overflow: hidden;
  margin: 22rpx 0;
}

.task-dashboard-fill {
  height: 100%;
  border-radius: 999rpx;
  background: linear-gradient(90deg, #2563eb, #10b981);
  transition: width 0.45s ease;
}

.task-dashboard-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 14rpx;
}

.dashboard-metric {
  min-width: 0;
  background: rgba(255, 255, 255, 0.74);
  border: 1rpx solid rgba(226, 232, 240, 0.9);
  border-radius: 18rpx;
  padding: 18rpx 10rpx;
  text-align: center;
}

.dashboard-metric-icon {
  display: block;
  font-size: 30rpx;
  line-height: 1;
}

.dashboard-metric-num {
  display: block;
  margin-top: 8rpx;
  font-size: 34rpx;
  color: #0f172a;
  font-weight: 900;
  line-height: 1;
}

.dashboard-metric-label {
  display: block;
  margin-top: 8rpx;
  font-size: 21rpx;
  color: #64748b;
  font-weight: 700;
}

.dashboard-status {
  margin-top: 18rpx;
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

/* 检修记录样式 */
.food-records-list { display: flex; flex-direction: column; gap: 16rpx; }
.food-record-item { display: flex; align-items: center; gap: 16rpx; padding: 20rpx; background: #f8fafc; border-radius: 16rpx; transition: all 0.2s; }
.food-record-item:active { background: #f1f5f9; }
.food-record-left { flex-shrink: 0; }
.food-image { width: 80rpx; height: 80rpx; border-radius: 12rpx; overflow: hidden; }
.food-image image { width: 100%; height: 100%; }
.food-icon { width: 80rpx; height: 80rpx; border-radius: 12rpx; background: #e2e8f0; display: flex; align-items: center; justify-content: center; }
.food-record-content { flex: 1; }
.food-name { font-size: 28rpx; font-weight: 700; color: #334155; display: block; margin-bottom: 4rpx; }
.food-time { font-size: 22rpx; color: #94a3b8; display: block; margin-bottom: 4rpx; }
.food-calories { font-size: 24rpx; font-weight: 600; color: #f97316; display: block; }
.food-record-delete { width: 48rpx; height: 48rpx; display: flex; align-items: center; justify-content: center; border-radius: 12rpx; transition: background 0.2s; }
.food-record-delete:active { background: #fef2f2; }

/* 图片上传样式 */
.image-upload-section { margin-top: 16rpx; }
.upload-btn { width: 100%; height: 200rpx; border: 2rpx dashed #cbd5e1; border-radius: 16rpx; display: flex; flex-direction: column; align-items: center; justify-content: center; background: #f8fafc; transition: all 0.2s; }
.upload-btn:active { background: #f1f5f9; border-color: #94a3b8; }
.uploaded-image { position: relative; width: 100%; height: 200rpx; border-radius: 16rpx; overflow: hidden; }
.uploaded-image image { width: 100%; height: 100%; }
.remove-image-btn { position: absolute; top: 12rpx; right: 12rpx; width: 48rpx; height: 48rpx; background: rgba(255, 255, 255, 0.9); border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.1); }

/* 表单样式 */
.form-group { margin-bottom: 32rpx; }
.form-label { display: block; font-size: 26rpx; font-weight: 600; color: #334155; margin-bottom: 12rpx; }
.form-input { width: 100%; height: 80rpx; border: 2rpx solid #e2e8f0; border-radius: 12rpx; padding: 0 24rpx; font-size: 26rpx; color: #334155; transition: all 0.2s; }
.form-input:focus { border-color: #10b981; outline: none; box-shadow: 0 0 0 4rpx rgba(16, 185, 129, 0.1); }
.form-textarea { width: 100%; height: 160rpx; border: 2rpx solid #e2e8f0; border-radius: 12rpx; padding: 20rpx 24rpx; font-size: 26rpx; color: #334155; resize: none; transition: all 0.2s; }
.form-textarea:focus { border-color: #10b981; outline: none; box-shadow: 0 0 0 4rpx rgba(16, 185, 129, 0.1); }

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

/* 执行任务板块 */
.execution-section {
  margin-top: 28rpx;
  background: #ffffff;
  border: 1rpx solid #e5e7eb;
  border-radius: 28rpx;
  padding: 26rpx;
  box-shadow: 0 8rpx 26rpx rgba(15, 23, 42, 0.05);
}

.execution-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20rpx;
  margin-bottom: 20rpx;
}

.execution-title { margin-bottom: 4rpx; }

.execution-subtitle {
  display: block;
  font-size: 22rpx;
  color: #64748b;
  line-height: 1.45;
}

.execution-actions-row {
  display: flex;
  align-items: center;
  gap: 12rpx;
  flex-shrink: 0;
}

.execution-add {
  background: #10b981;
  border: 1rpx solid #059669;
  border-radius: 999rpx;
  padding: 10rpx 20rpx;
}

.execution-add-text {
  font-size: 22rpx;
  color: #ffffff;
  font-weight: 700;
}

.execution-refresh {
  flex-shrink: 0;
  background: #eff6ff;
  border: 1rpx solid #bfdbfe;
  border-radius: 999rpx;
  padding: 10rpx 20rpx;
}

.execution-refresh-text {
  font-size: 22rpx;
  color: #2563eb;
  font-weight: 700;
}

.task-add-form {
  background: #f8fafc;
  border: 1rpx solid #e2e8f0;
  border-radius: 22rpx;
  padding: 22rpx;
  margin-bottom: 18rpx;
}

.task-add-input {
  width: 100%;
  height: 76rpx;
  background: #ffffff;
  border: 1rpx solid #e2e8f0;
  border-radius: 14rpx;
  padding: 0 20rpx;
  margin-bottom: 14rpx;
  font-size: 26rpx;
  color: #0f172a;
  box-sizing: border-box;
}

.task-add-actions {
  display: flex;
  gap: 14rpx;
}

.task-add-confirm,
.task-add-cancel {
  flex: 1;
  border-radius: 14rpx;
  padding: 18rpx;
  text-align: center;
  font-size: 26rpx;
  font-weight: 700;
}

.task-add-confirm {
  background: #10b981;
  color: #ffffff;
}

.task-add-cancel {
  background: #e2e8f0;
  color: #475569;
}

.execution-overview {
  background: linear-gradient(135deg, #f8fafc 0%, #eef6ff 52%, #ecfdf5 100%);
  border: 1rpx solid #dbeafe;
  border-radius: 22rpx;
  padding: 22rpx;
  margin-bottom: 18rpx;
  box-shadow: 0 6rpx 18rpx rgba(15, 23, 42, 0.04);
}

.overview-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 18rpx;
}

.overview-label {
  display: block;
  font-size: 22rpx;
  color: #64748b;
  font-weight: 700;
}

.overview-value {
  display: block;
  margin-top: 8rpx;
  font-size: 58rpx;
  color: #0f172a;
  font-weight: 900;
  line-height: 1;
}

.overview-badge {
  flex-shrink: 0;
  border-radius: 999rpx;
  background: #ecfdf5;
  color: #16a34a;
  padding: 10rpx 18rpx;
  border: 1rpx solid #bbf7d0;
}

.overview-badge.warning {
  background: #fef2f2;
  color: #dc2626;
  border-color: #fecaca;
}

.overview-badge text {
  font-size: 22rpx;
  font-weight: 800;
}

.overview-track {
  height: 14rpx;
  background: #dbeafe;
  border-radius: 999rpx;
  overflow: hidden;
  margin: 20rpx 0 18rpx;
}

.overview-track-fill {
  height: 100%;
  border-radius: 999rpx;
  background: linear-gradient(90deg, #2563eb, #10b981);
  transition: width 0.45s ease;
}

.execution-integrity {
  background: linear-gradient(135deg, #f8fafc 0%, #ecfdf5 100%);
  border: 1rpx solid #dbeafe;
  border-radius: 22rpx;
  padding: 22rpx;
  margin-bottom: 18rpx;
  box-shadow: 0 6rpx 18rpx rgba(15, 23, 42, 0.04);
}

.integrity-main {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.integrity-icon-wrap {
  width: 68rpx;
  height: 68rpx;
  border-radius: 18rpx;
  background: #dcfce7;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.integrity-icon {
  font-size: 34rpx;
}

.integrity-copy {
  flex: 1;
  min-width: 0;
}

.integrity-title {
  display: block;
  font-size: 28rpx;
  color: #0f172a;
  font-weight: 800;
  line-height: 1.25;
}

.integrity-desc {
  display: block;
  margin-top: 6rpx;
  font-size: 22rpx;
  color: #64748b;
  line-height: 1.4;
}

.integrity-rate {
  min-width: 96rpx;
  text-align: right;
  flex-shrink: 0;
}

.integrity-rate-num {
  display: block;
  font-size: 38rpx;
  color: #10b981;
  font-weight: 900;
  line-height: 1;
}

.integrity-rate-label {
  display: block;
  margin-top: 6rpx;
  font-size: 20rpx;
  color: #64748b;
  font-weight: 700;
}

.integrity-progress {
  height: 12rpx;
  background: #dbeafe;
  border-radius: 999rpx;
  overflow: hidden;
  margin: 20rpx 0 18rpx;
}

.integrity-progress-bar {
  height: 100%;
  border-radius: 999rpx;
  background: linear-gradient(90deg, #2563eb, #10b981);
  transition: width 0.45s ease;
}

.integrity-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12rpx;
}

.integrity-mini {
  min-width: 0;
  background: rgba(255, 255, 255, 0.72);
  border: 1rpx solid rgba(226, 232, 240, 0.8);
  border-radius: 16rpx;
  padding: 14rpx 8rpx;
  text-align: center;
}

.integrity-mini-icon {
  display: block;
  font-size: 28rpx;
  line-height: 1;
}

.integrity-mini-num {
  display: block;
  margin-top: 8rpx;
  font-size: 30rpx;
  color: #0f172a;
  font-weight: 900;
  line-height: 1;
}

.integrity-mini-label {
  display: block;
  margin-top: 8rpx;
  font-size: 20rpx;
  color: #64748b;
  font-weight: 700;
}

.execution-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12rpx;
}

.execution-stat {
  position: relative;
  background: #f8fafc;
  border: 1rpx solid #eef2f7;
  border-radius: 18rpx;
  padding: 18rpx 6rpx 16rpx;
  text-align: center;
  overflow: hidden;
}

.execution-stat-icon {
  width: 46rpx;
  height: 46rpx;
  border-radius: 14rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 10rpx;
}

.execution-stat-icon text {
  font-size: 24rpx;
  line-height: 1;
}

.execution-stat-dot {
  width: 12rpx;
  height: 12rpx;
  border-radius: 50%;
  margin: 0 auto 8rpx;
}

.execution-stat-num {
  display: block;
  font-size: 34rpx;
  font-weight: 800;
  color: #0f172a;
  line-height: 1;
}

.execution-stat-label {
  display: block;
  margin-top: 8rpx;
  font-size: 20rpx;
  color: #64748b;
  font-weight: 600;
}

.execution-tools {
  display: flex;
  align-items: center;
  gap: 14rpx;
  margin-bottom: 18rpx;
}

.execution-search {
  flex: 1;
  height: 72rpx;
  border-radius: 18rpx;
  background: #f8fafc;
  border: 1rpx solid #e2e8f0;
  display: flex;
  align-items: center;
  gap: 10rpx;
  padding: 0 20rpx;
  min-width: 0;
}

.execution-search-icon {
  flex-shrink: 0;
  color: #94a3b8;
  font-size: 28rpx;
  font-weight: 800;
}

.execution-search-input {
  flex: 1;
  height: 72rpx;
  min-width: 0;
  font-size: 24rpx;
  color: #0f172a;
}

.execution-search-placeholder {
  color: #94a3b8;
  font-size: 24rpx;
}

.execution-filter {
  height: 72rpx;
  min-width: 96rpx;
  padding: 0 18rpx;
  border-radius: 18rpx;
  background: #eff6ff;
  border: 1rpx solid #bfdbfe;
  display: flex;
  align-items: center;
  justify-content: center;
}

.execution-filter-icon {
  font-size: 23rpx;
  color: #2563eb;
  font-weight: 800;
}

.execution-tabs {
  display: flex;
  gap: 8rpx;
  background: #f1f5f9;
  border-radius: 18rpx;
  padding: 6rpx;
  margin-bottom: 20rpx;
  overflow-x: auto;
}

.execution-tab {
  flex: 0 0 auto;
  text-align: center;
  border-radius: 14rpx;
  padding: 14rpx 20rpx;
}

.execution-tab.active {
  background: #2563eb;
  box-shadow: 0 6rpx 16rpx rgba(37, 99, 235, 0.18);
}

.execution-tab-text {
  font-size: 24rpx;
  color: #64748b;
  font-weight: 700;
}

.execution-tab.active .execution-tab-text { color: #fff; }

.execution-list {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.execution-card {
  position: relative;
  background: #fff;
  border-radius: 20rpx;
  padding: 22rpx 22rpx 22rpx 28rpx;
  border: 1rpx solid #e2e8f0;
  box-shadow: 0 3rpx 12rpx rgba(15, 23, 42, 0.04);
  overflow: hidden;
}

.execution-card::before {
  content: '';
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  width: 8rpx;
  background: #f59e0b;
}

.execution-card.severity-low::before { background: #3b82f6; }
.execution-card.severity-medium::before { background: #f59e0b; }
.execution-card.severity-high::before { background: #f97316; }
.execution-card.severity-critical::before { background: #ef4444; }

.execution-card:active {
  transform: scale(0.99);
}

.execution-card-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 14rpx;
  margin-bottom: 10rpx;
}

.execution-title-wrap {
  flex: 1;
  min-width: 0;
}

.execution-card-title {
  display: block;
  font-size: 28rpx;
  color: #0f172a;
  font-weight: 800;
  line-height: 1.35;
  word-break: break-word;
}

.execution-severity,
.execution-status {
  flex-shrink: 0;
  border-radius: 999rpx;
  padding: 6rpx 14rpx;
  font-size: 20rpx;
  font-weight: 800;
}

.execution-equipment {
  display: block;
  font-size: 22rpx;
  color: #2563eb;
  font-weight: 700;
  margin-top: 8rpx;
}

.execution-desc {
  display: block;
  font-size: 23rpx;
  color: #64748b;
  line-height: 1.45;
  margin-bottom: 16rpx;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.execution-progress {
  height: 10rpx;
  background: #e2e8f0;
  border-radius: 999rpx;
  overflow: hidden;
  margin-bottom: 16rpx;
}

.execution-progress-bar {
  height: 100%;
  border-radius: 999rpx;
  background: linear-gradient(90deg, #2563eb, #10b981);
}

.execution-card-bottom {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 14rpx;
  margin-bottom: 16rpx;
}

.execution-meta-group {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 6rpx;
}

.execution-assignee {
  display: inline-flex;
  align-items: center;
  gap: 8rpx;
  min-width: 0;
}

.execution-assignee-avatar {
  width: 36rpx;
  height: 36rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  flex-shrink: 0;
  box-shadow: 0 4rpx 10rpx rgba(15, 23, 42, 0.12);
}

.execution-assignee-avatar text {
  color: #ffffff;
  font-size: 18rpx;
  font-weight: 800;
}

.execution-assignee-img {
  width: 100%;
  height: 100%;
  display: block;
}

.execution-meta {
  font-size: 21rpx;
  color: #64748b;
  font-weight: 600;
  line-height: 1.35;
}

.execution-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12rpx;
}

.execution-action {
  height: 60rpx;
  border-radius: 14rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.execution-action text {
  font-size: 24rpx;
  font-weight: 800;
}

.execution-action.secondary {
  background: #f8fafc;
  border: 1rpx solid #e2e8f0;
}

.execution-action.secondary text { color: #475569; }

.execution-action.primary {
  background: #2563eb;
  box-shadow: 0 6rpx 14rpx rgba(37, 99, 235, 0.2);
}

.execution-action.primary text { color: #ffffff; }

.execution-more {
  height: 68rpx;
  border-radius: 16rpx;
  background: #f8fafc;
  border: 1rpx solid #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.execution-more text {
  font-size: 24rpx;
  color: #2563eb;
  font-weight: 800;
}

.execution-empty {
  padding: 38rpx 0;
  text-align: center;
}

.execution-empty-icon {
  display: block;
  font-size: 42rpx;
  margin-bottom: 8rpx;
}

.execution-empty-text {
  font-size: 24rpx;
  color: #94a3b8;
}

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
.insight-avatar { width: 96rpx; height: 96rpx; border-radius: 50%; display: block; }
.insight-bubble {
  flex: 1; background: #f8fafc; border-radius: 32rpx 32rpx 32rpx 0; padding: 24rpx;
}
.bubble-text { font-size: 28rpx; color: #334155; line-height: 1.5; font-weight: 500;}
.insight-tags { display: flex; gap: 16rpx; }
.tag { font-size: 22rpx; padding: 8rpx 20rpx; border-radius: 30rpx; font-weight: 600; }
.tag.positive { background: #dcfce7; color: #166534; }
.tag.warning { background: #fef3c7; color: #b45309; }

.trend-chart-box { height: 280rpx; margin-top: 16rpx; }
.chart-bars-container { display: flex; height: 100%; align-items: flex-end; justify-content: space-between; padding-top: 20rpx;}
.chart-col { display: flex; flex-direction: column; align-items: center; gap: 16rpx; flex: 1; height: 100%; justify-content: flex-end; }
.chart-bar-fill { width: 24rpx; background: #d1fae5; border-radius: 12rpx; transition: height 1s cubic-bezier(0.16, 1, 0.3, 1); }
.chart-col:nth-child(odd) .chart-bar-fill { background: #10b981; }
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
.template-scroll {
  width: 100%;
  white-space: nowrap;
  margin-bottom: 10rpx;
  overflow: hidden;
}
.template-container {
  display: flex;
  gap: 24rpx;
  padding: 10rpx 32rpx 32rpx 32rpx;
  max-width: 100%;
}
.template-card {
  display: inline-flex;
  flex-direction: column;
  background: #f8fafc;
  width: 280rpx;
  min-width: 280rpx;
  max-width: 280rpx;
  padding: 24rpx;
  border-radius: 32rpx;
  border: 4rpx solid transparent;
  box-shadow: 0 8rpx 20rpx rgba(15,23,42,0.04);
  transition: transform 0.2s;
  overflow: hidden;
  word-break: break-word;
  overflow-wrap: break-word;
}
.template-card:active { border-color: #3b82f6; transform: scale(0.96); }
.tpl-icon { font-size: 48rpx; margin-bottom: 16rpx;}
.tpl-name { font-size: 30rpx; font-weight: 800; color: #0f172a; margin-bottom: 8rpx; }
.tpl-desc { font-size: 22rpx; color: #64748b; white-space: normal; line-height: 1.4; margin-bottom: 24rpx; flex: 1; }
.tpl-btn { background: #eff6ff; color: #3b82f6; font-size: 24rpx; font-weight: 700; text-align: center; padding: 16rpx; border-radius: 16rpx;}

.badge-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 24rpx; margin-top: 16rpx; max-width: 100%; overflow: hidden; }
.badge-item { display: flex; flex-direction: column; align-items: center; gap: 12rpx; }
.badge-icon-box {
  width: 100rpx; height: 100rpx; border-radius: 50%; background: #fefce8; border: 4rpx solid #fef08a;
  display: flex; align-items: center; justify-content: center; box-shadow: 0 8rpx 16rpx rgba(250,204,21,0.2);
}
.badge-icon { font-size: 48rpx; }
.badge-name { font-size: 22rpx; font-weight: 600; color: #334155; text-align: center; }
.badge-item.locked .badge-icon-box { background: #f1f5f9; border-color: #e2e8f0; filter: grayscale(1); box-shadow: none; opacity: 0.5;}
.badge-item.locked .badge-name { color: #94a3b8; }

/* ===== TAB 2: 联系人协作 ===== */
.collab-card,
.message-card {
  background: #fff;
  border: 1rpx solid #e5e7eb;
  border-radius: 28rpx;
  padding: 28rpx;
  margin-bottom: 24rpx;
  box-shadow: 0 8rpx 24rpx rgba(15, 23, 42, 0.05);
}

.collab-header,
.message-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20rpx;
  margin-bottom: 22rpx;
}

.collab-title,
.message-title {
  display: block;
  font-size: 32rpx;
  color: #0f172a;
  font-weight: 800;
  line-height: 1.25;
}

.collab-subtitle,
.message-subtitle {
  display: block;
  margin-top: 6rpx;
  font-size: 22rpx;
  color: #64748b;
  font-weight: 600;
}

.collab-online-pill {
  flex-shrink: 0;
  background: #ecfdf5;
  border: 1rpx solid #bbf7d0;
  border-radius: 999rpx;
  padding: 10rpx 18rpx;
}

.collab-online-pill text {
  font-size: 22rpx;
  color: #047857;
  font-weight: 800;
}

.collab-search {
  height: 76rpx;
  border-radius: 18rpx;
  background: #f8fafc;
  border: 1rpx solid #e2e8f0;
  display: flex;
  align-items: center;
  gap: 12rpx;
  padding: 0 22rpx;
  margin-bottom: 20rpx;
}

.collab-search-icon {
  color: #94a3b8;
  font-size: 30rpx;
  font-weight: 800;
}

.collab-search-input,
.message-input {
  flex: 1;
  min-width: 0;
  height: 72rpx;
  font-size: 25rpx;
  color: #0f172a;
}

.collab-placeholder {
  color: #94a3b8;
  font-size: 24rpx;
}

.contact-list {
  display: flex;
  flex-direction: column;
  gap: 14rpx;
}

.contact-item {
  display: flex;
  align-items: center;
  gap: 18rpx;
  border: 1rpx solid #e5e7eb;
  border-radius: 22rpx;
  padding: 18rpx;
  background: #fff;
}

.contact-item.active {
  border-color: #93c5fd;
  background: #eff6ff;
}

.contact-avatar {
  position: relative;
  width: 76rpx;
  height: 76rpx;
  border-radius: 22rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.contact-avatar text {
  font-size: 30rpx;
  color: #1f2937;
  font-weight: 800;
}

.contact-status-dot {
  position: absolute;
  right: -2rpx;
  bottom: -2rpx;
  width: 18rpx;
  height: 18rpx;
  border: 4rpx solid #fff;
  border-radius: 50%;
  background: #94a3b8;
}

.contact-status-dot.online { background: #22c55e; }
.contact-status-dot.busy { background: #f59e0b; }
.contact-status-dot.offline { background: #94a3b8; }

.contact-main {
  flex: 1;
  min-width: 0;
}

.contact-name-row {
  display: flex;
  align-items: center;
  gap: 12rpx;
  margin-bottom: 6rpx;
}

.contact-name {
  font-size: 28rpx;
  color: #0f172a;
  font-weight: 800;
}

.contact-role {
  font-size: 20rpx;
  color: #2563eb;
  background: #dbeafe;
  border-radius: 999rpx;
  padding: 4rpx 12rpx;
  font-weight: 700;
}

.contact-skill,
.contact-last {
  display: block;
  font-size: 22rpx;
  color: #64748b;
  line-height: 1.35;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.contact-last {
  margin-top: 6rpx;
  color: #94a3b8;
}

.contact-meta {
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 10rpx;
}

.contact-time {
  font-size: 20rpx;
  color: #94a3b8;
  font-weight: 600;
}

.contact-unread {
  min-width: 34rpx;
  height: 34rpx;
  padding: 0 8rpx;
  border-radius: 999rpx;
  background: #ef4444;
  display: flex;
  align-items: center;
  justify-content: center;
}

.contact-unread text {
  font-size: 20rpx;
  color: #fff;
  font-weight: 800;
}

.message-actions {
  display: flex;
  gap: 10rpx;
  flex-shrink: 0;
}

.message-action {
  height: 56rpx;
  min-width: 86rpx;
  border-radius: 14rpx;
  background: #f8fafc;
  border: 1rpx solid #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.message-action.primary {
  background: #2563eb;
  border-color: #2563eb;
}

.message-action text {
  font-size: 23rpx;
  color: #475569;
  font-weight: 800;
}

.message-action.primary text { color: #fff; }

.quick-message-row {
  display: flex;
  gap: 10rpx;
  overflow-x: auto;
  padding-bottom: 16rpx;
  margin-bottom: 12rpx;
}

.quick-message {
  flex-shrink: 0;
  border-radius: 999rpx;
  background: #f1f5f9;
  padding: 10rpx 18rpx;
}

.quick-message text {
  font-size: 22rpx;
  color: #475569;
  font-weight: 700;
}

.message-thread {
  background: #f8fafc;
  border-radius: 20rpx;
  padding: 18rpx;
  display: flex;
  flex-direction: column;
  gap: 12rpx;
  margin-bottom: 16rpx;
}

.message-bubble {
  max-width: 82%;
  align-self: flex-start;
  background: #fff;
  border: 1rpx solid #e2e8f0;
  border-radius: 18rpx 18rpx 18rpx 6rpx;
  padding: 14rpx 18rpx;
}

.message-bubble.mine {
  align-self: flex-end;
  background: #2563eb;
  border-color: #2563eb;
  border-radius: 18rpx 18rpx 6rpx 18rpx;
}

.message-bubble text {
  font-size: 24rpx;
  color: #334155;
  line-height: 1.45;
}

.message-bubble.mine text { color: #fff; }

.message-input-row {
  display: flex;
  align-items: center;
  gap: 12rpx;
}

.message-input {
  background: #f8fafc;
  border: 1rpx solid #e2e8f0;
  border-radius: 16rpx;
  padding: 0 18rpx;
}

.message-send {
  width: 100rpx;
  height: 72rpx;
  border-radius: 16rpx;
  background: #2563eb;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.message-send text {
  font-size: 24rpx;
  color: #fff;
  font-weight: 800;
}

.chat-page {
  min-height: 900rpx;
  background: #f4f6f8;
  border-radius: 28rpx;
  overflow: hidden;
  border: 1rpx solid #e5e7eb;
  display: flex;
  flex-direction: column;
  box-shadow: 0 8rpx 24rpx rgba(15, 23, 42, 0.05);
}

.chat-topbar {
  height: 108rpx;
  padding: 0 22rpx;
  background: #fff;
  border-bottom: 1rpx solid #e5e7eb;
  display: flex;
  align-items: center;
  gap: 18rpx;
}

.chat-back {
  width: 58rpx;
  height: 58rpx;
  border-radius: 50%;
  background: #f1f5f9;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.chat-back text {
  font-size: 50rpx;
  color: #334155;
  line-height: 1;
  transform: translateY(-2rpx);
}

.chat-peer {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 4rpx;
}

.chat-peer-name {
  font-size: 31rpx;
  color: #0f172a;
  font-weight: 800;
  line-height: 1.2;
}

.chat-peer-status {
  font-size: 21rpx;
  color: #64748b;
  font-weight: 600;
}

.chat-top-actions {
  display: flex;
  gap: 8rpx;
  flex-shrink: 0;
}

.chat-top-action {
  height: 52rpx;
  padding: 0 16rpx;
  border-radius: 14rpx;
  background: #f8fafc;
  border: 1rpx solid #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chat-top-action.primary {
  background: #2563eb;
  border-color: #2563eb;
}

.chat-top-action text {
  font-size: 22rpx;
  color: #475569;
  font-weight: 800;
}

.chat-top-action.primary text { color: #fff; }

.chat-scroll {
  flex: 1;
  min-height: 620rpx;
  max-height: 760rpx;
  padding: 20rpx 22rpx 0;
  box-sizing: border-box;
}

.chat-profile-strip {
  display: flex;
  align-items: center;
  gap: 16rpx;
  background: #fff;
  border: 1rpx solid #e5e7eb;
  border-radius: 20rpx;
  padding: 18rpx;
  margin-bottom: 18rpx;
}

.chat-avatar {
  width: 72rpx;
  height: 72rpx;
  border-radius: 20rpx;
}

.chat-profile-main {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 6rpx;
}

.chat-profile-skill {
  font-size: 24rpx;
  color: #0f172a;
  font-weight: 800;
  line-height: 1.35;
}

.chat-profile-hint {
  font-size: 21rpx;
  color: #64748b;
  font-weight: 600;
}

.chat-quick-row {
  padding-bottom: 8rpx;
  margin-bottom: 10rpx;
}

.chat-thread {
  background: transparent;
  border-radius: 0;
  padding: 8rpx 2rpx 28rpx;
  margin-bottom: 0;
}

.chat-input-bar {
  display: flex;
  align-items: center;
  gap: 12rpx;
  padding: 18rpx 22rpx;
  background: #fff;
  border-top: 1rpx solid #e5e7eb;
}

.chat-input {
  height: 76rpx;
  background: #f8fafc;
  border-radius: 38rpx;
  padding: 0 24rpx;
}

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

/* ===== Custom Plan Button ===== */
.custom-plan-btn {
  background: linear-gradient(135deg, #f0fdf4 0%, #ecfdf5 100%);
  border: 3rpx dashed #86efac;
  border-radius: 24rpx;
  padding: 28rpx 32rpx;
  display: flex;
  flex-direction: column;
  gap: 8rpx;
  transition: all 0.2s;
  max-width: 100%;
  overflow: hidden;
  word-break: break-word;
  overflow-wrap: break-word;
}
.custom-plan-btn:active {
  transform: scale(0.97);
  background: linear-gradient(135deg, #dcfce7 0%, #d1fae5 100%);
  border-color: #10b981;
}

/* ===== Modal Overlay ===== */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(15, 23, 42, 0.45);
  backdrop-filter: blur(12px);
  display: flex;
  align-items: flex-end;
  z-index: 2000;
  overflow: hidden;
}

.modal-drag-bar {
  width: 64rpx;
  height: 6rpx;
  background: #e2e8f0;
  border-radius: 6rpx;
  margin: 20rpx auto 8rpx;
}

/* ===== Plan Detail Modal ===== */
.plan-detail-modal {
  width: 100%;
  max-width: 100%;
  height: 88vh;
  max-height: 88vh;
  background: #fafbfc;
  border-radius: 40rpx 40rpx 0 0;
  display: flex;
  flex-direction: column;
  animation: slideUp 0.35s cubic-bezier(0.16, 1, 0.3, 1);
  overflow: hidden;
}

@keyframes slideUp {
  from { transform: translateY(100%); }
  to { transform: translateY(0); }
}

.plan-detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8rpx 36rpx 20rpx;
  background: white;
  border-radius: 40rpx 40rpx 0 0;
}

.plan-detail-title-row {
  display: flex;
  align-items: center;
  gap: 20rpx;
}

.plan-detail-icon-wrap {
  width: 80rpx;
  height: 80rpx;
  border-radius: 24rpx;
  background: linear-gradient(135deg, #f0fdf4, #ecfdf5);
  display: flex;
  align-items: center;
  justify-content: center;
}

.plan-detail-icon {
  font-size: 40rpx;
}

.plan-detail-title-text {
  display: flex;
  flex-direction: column;
  gap: 4rpx;
}

.plan-detail-name {
  font-size: 34rpx;
  font-weight: 800;
  color: #0f172a;
  line-height: 1.2;
}

.plan-detail-desc {
  font-size: 22rpx;
  color: #94a3b8;
  font-weight: 500;
  line-height: 1.4;
}

.plan-detail-close {
  width: 60rpx;
  height: 60rpx;
  background: #f1f5f9;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

/* ===== Dish Detail Modal ===== */

.plan-nutrition-summary {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16rpx;
  margin-bottom: 36rpx;
  max-width: 100%;
  overflow: hidden;
}

.nutrition-item {
  background: white;
  border-radius: 20rpx;
  padding: 20rpx 8rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6rpx;
  box-shadow: 0 2rpx 12rpx rgba(15, 23, 42, 0.04);
}

.nutrition-val {
  font-size: 30rpx;
  font-weight: 800;
  color: #0f172a;
  line-height: 1;
}

.nutrition-label {
  font-size: 18rpx;
  color: #94a3b8;
  font-weight: 500;
}

.nutrition-cal .nutrition-val { color: #f97316; }
.nutrition-pro .nutrition-val { color: #3b82f6; }
.nutrition-carb .nutrition-val { color: #f59e0b; }
.nutrition-fat .nutrition-val { color: #ef4444; }

.meal-section {
  margin-bottom: 28rpx;
}

.meal-section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16rpx;
}

.meal-type-badge {
  display: flex;
  align-items: center;
  gap: 10rpx;
  background: white;
  padding: 8rpx 20rpx;
  border-radius: 16rpx;
  box-shadow: 0 2rpx 8rpx rgba(15, 23, 42, 0.04);
}

.meal-type-icon {
  font-size: 28rpx;
}

.meal-type-name {
  font-size: 26rpx;
  font-weight: 700;
  color: #0f172a;
}

.meal-calories-badge {
  background: #f0fdf4;
  padding: 8rpx 20rpx;
  border-radius: 16rpx;
}

.meal-calories-text {
  font-size: 22rpx;
  color: #059669;
  font-weight: 700;
}

.meal-dishes {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

.dish-card {
  display: flex;
  align-items: center;
  gap: 20rpx;
  background: white;
  border-radius: 20rpx;
  padding: 24rpx;
  box-shadow: 0 2rpx 12rpx rgba(15, 23, 42, 0.04);
  transition: all 0.2s;
  max-width: 100%;
  overflow: hidden;
  word-break: break-word;
  overflow-wrap: break-word;
}

.dish-card:active {
  transform: scale(0.98);
  box-shadow: 0 4rpx 20rpx rgba(16, 185, 129, 0.1);
}

.dish-card-left {
  flex-shrink: 0;
}

.dish-emoji-badge {
  width: 88rpx;
  height: 88rpx;
  border-radius: 22rpx;
  background: #f8fafc;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 40rpx;
}

.dish-card-body {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}

.dish-name {
  font-size: 28rpx;
  font-weight: 700;
  color: #0f172a;
  line-height: 1.3;
}

.dish-health-desc {
  font-size: 22rpx;
  color: #64748b;
  font-weight: 500;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.dish-tags-row {
  display: flex;
  gap: 10rpx;
  flex-wrap: wrap;
}

.dish-tag {
  font-size: 20rpx;
  font-weight: 600;
  padding: 4rpx 14rpx;
  border-radius: 8rpx;
  line-height: 1.5;
}

.dish-tag.cal-tag {
  color: #ea580c;
  background: #fff7ed;
}

.dish-tag.time-tag {
  color: #3b82f6;
  background: #eff6ff;
}

.dish-tag.diff-tag {
  color: #059669;
  background: #f0fdf4;
}

.dish-card-arrow {
  flex-shrink: 0;
  width: 40rpx;
  height: 40rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.plan-detail-footer {
  padding: 20rpx 36rpx;
  padding-bottom: calc(20rpx + env(safe-area-inset-bottom));
  background: white;
  border-top: 1rpx solid #f1f5f9;
}

.plan-apply-btn {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  border-radius: 16rpx;
  padding: 22rpx;
  text-align: center;
  box-shadow: 0 6rpx 20rpx rgba(16, 185, 129, 0.25);
}

/* ===== Dish Detail Modal ===== */
.dish-detail-modal {
  width: 100%;
  max-width: 100%;
  height: 82vh;
  max-height: 82vh;
  background: #fafbfc;
  border-radius: 40rpx 40rpx 0 0;
  display: flex;
  flex-direction: column;
  animation: slideUp 0.35s cubic-bezier(0.16, 1, 0.3, 1);
  overflow: hidden;
}

.dish-detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8rpx 36rpx 20rpx;
  background: white;
  border-radius: 40rpx 40rpx 0 0;
}

.dish-detail-header-left {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.dish-detail-emoji {
  width: 72rpx;
  height: 72rpx;
  border-radius: 20rpx;
  background: #f8fafc;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36rpx;
}

.dish-detail-name {
  font-size: 34rpx;
  font-weight: 800;
  color: #0f172a;
  line-height: 1.2;
}

.dish-detail-close {
  width: 60rpx;
  height: 60rpx;
  background: #f1f5f9;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.dish-health-overview {
  background: linear-gradient(135deg, #f0fdf4 0%, #ecfdf5 100%);
  border-radius: 20rpx;
  padding: 24rpx;
  margin-bottom: 24rpx;
  border-left: 6rpx solid #10b981;
  max-width: 100%;
  overflow: hidden;
  word-break: break-word;
  overflow-wrap: break-word;
}

.dish-overview-text {
  font-size: 26rpx;
  color: #334155;
  line-height: 1.8;
  font-weight: 500;
}

.dish-meta-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16rpx;
  margin-bottom: 32rpx;
  max-width: 100%;
  overflow: hidden;
}

.dish-meta-chip {
  background: white;
  border-radius: 16rpx;
  padding: 20rpx 12rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6rpx;
  box-shadow: 0 2rpx 12rpx rgba(15, 23, 42, 0.04);
}

.meta-chip-val {
  font-size: 30rpx;
  font-weight: 800;
  line-height: 1;
}

.meta-chip-label {
  font-size: 20rpx;
  color: #94a3b8;
  font-weight: 500;
}

.meta-cal .meta-chip-val { color: #ea580c; }
.meta-time .meta-chip-val { color: #3b82f6; }
.meta-diff .meta-chip-val { color: #059669; }

.dish-section {
  margin-bottom: 28rpx;
}

.dish-section-header {
  display: flex;
  align-items: center;
  gap: 12rpx;
  margin-bottom: 16rpx;
}

.section-icon-wrap {
  width: 44rpx;
  height: 44rpx;
  border-radius: 12rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.section-icon-ingredient {
  background: #f0fdf4;
}

.section-icon-step {
  background: #eff6ff;
}

.dish-section-title {
  font-size: 28rpx;
  font-weight: 700;
  color: #0f172a;
}

.dish-ingredients {
  background: white;
  border-radius: 20rpx;
  padding: 8rpx 24rpx;
  box-shadow: 0 2rpx 12rpx rgba(15, 23, 42, 0.04);
  max-width: 100%;
  overflow: hidden;
  word-break: break-word;
  overflow-wrap: break-word;
}

.dish-ingredient-item {
  display: flex;
  align-items: center;
  gap: 16rpx;
  padding: 16rpx 0;
  border-bottom: 1rpx solid #f8fafc;
}

.dish-ingredient-item:last-child {
  border-bottom: none;
}

.ingredient-dot {
  width: 10rpx;
  height: 10rpx;
  background: linear-gradient(135deg, #10b981, #34d399);
  border-radius: 50%;
  flex-shrink: 0;
}

.ingredient-text {
  font-size: 26rpx;
  color: #334155;
  line-height: 1.5;
}

.dish-steps {
  display: flex;
  flex-direction: column;
  gap: 0;
  background: white;
  border-radius: 20rpx;
  padding: 8rpx 24rpx;
  box-shadow: 0 2rpx 12rpx rgba(15, 23, 42, 0.04);
  max-width: 100%;
  overflow: hidden;
  word-break: break-word;
  overflow-wrap: break-word;
}

.dish-step-item {
  display: flex;
  gap: 20rpx;
  padding: 20rpx 0;
  border-bottom: 1rpx solid #f8fafc;
  align-items: flex-start;
}

.dish-step-item:last-child {
  border-bottom: none;
}

.step-num {
  width: 44rpx;
  height: 44rpx;
  background: linear-gradient(135deg, #10b981, #34d399);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22rpx;
  font-weight: 700;
  border-radius: 12rpx;
  flex-shrink: 0;
}

.step-text {
  flex: 1;
  font-size: 26rpx;
  color: #334155;
  line-height: 1.7;
  padding-top: 6rpx;
}

/* ===== Custom Plan Modal ===== */
.custom-plan-modal {
  width: 100%;
  max-width: 100%;
  height: 88vh;
  max-height: 88vh;
  background: #fafbfc;
  border-radius: 40rpx 40rpx 0 0;
  display: flex;
  flex-direction: column;
  animation: slideUp 0.35s cubic-bezier(0.16, 1, 0.3, 1);
  overflow: hidden;
}

.custom-plan-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8rpx 36rpx 20rpx;
  background: white;
  border-radius: 40rpx 40rpx 0 0;
}

.custom-plan-title {
  font-size: 34rpx;
  font-weight: 800;
  color: #0f172a;
}

.custom-plan-close {
  width: 60rpx;
  height: 60rpx;
  background: #f1f5f9;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.form-group {
  margin-bottom: 28rpx;
}

.form-label {
  font-size: 26rpx;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 14rpx;
  display: block;
}

.form-input {
  width: 100%;
  max-width: 100%;
  height: 84rpx;
  background: white;
  border: 2rpx solid #e2e8f0;
  border-radius: 14rpx;
  padding: 0 24rpx;
  font-size: 28rpx;
  color: #0f172a;
  box-sizing: border-box;
  transition: border-color 0.2s;
}

.form-input:focus {
  border-color: #10b981;
}

.form-textarea {
  width: 100%;
  max-width: 100%;
  height: 140rpx;
  background: white;
  border: 2rpx solid #e2e8f0;
  border-radius: 14rpx;
  padding: 20rpx 24rpx;
  font-size: 28rpx;
  color: #0f172a;
  box-sizing: border-box;
  line-height: 1.6;
  transition: border-color 0.2s;
}

.form-textarea:focus {
  border-color: #10b981;
}

.form-options {
  display: flex;
  gap: 12rpx;
  flex-wrap: wrap;
}

.form-options.wrap {
  flex-wrap: wrap;
}

.form-option {
  display: flex;
  align-items: center;
  gap: 8rpx;
  background: white;
  border: 2rpx solid #e2e8f0;
  border-radius: 14rpx;
  padding: 14rpx 22rpx;
  transition: all 0.2s;
}

.form-option.active {
  background: #f0fdf4;
  border-color: #10b981;
  box-shadow: 0 2rpx 8rpx rgba(16, 185, 129, 0.15);
}

.form-option-icon {
  font-size: 26rpx;
}

.form-option-text {
  font-size: 24rpx;
  font-weight: 600;
  color: #64748b;
}

.form-option.active .form-option-text {
  color: #059669;
}

.meal-option {
  flex: 1;
  justify-content: center;
  min-width: 0;
}

.tag-option {
  padding: 10rpx 20rpx;
}

.custom-plan-footer {
  display: flex;
  gap: 16rpx;
  padding: 20rpx 36rpx;
  padding-bottom: calc(20rpx + env(safe-area-inset-bottom));
  background: white;
  border-top: 1rpx solid #f1f5f9;
}

.custom-plan-cancel {
  flex: 1;
  background: #f1f5f9;
  border-radius: 14rpx;
  padding: 22rpx;
  text-align: center;
}

.custom-plan-confirm {
  flex: 2;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  border-radius: 14rpx;
  padding: 22rpx;
  text-align: center;
  box-shadow: 0 6rpx 20rpx rgba(16, 185, 129, 0.25);
}

/* ===== Plan Description Section ===== */
.plan-desc-section,
.custom-plan-desc-section {
  background: linear-gradient(135deg, #f0fdf4 0%, #ecfdf5 100%);
  border-radius: 20rpx;
  padding: 24rpx;
  margin-bottom: 28rpx;
  border-left: 6rpx solid #10b981;
  max-width: 100%;
  overflow: hidden;
  word-break: break-word;
  overflow-wrap: break-word;
}

.custom-plan-desc-section {
  background: linear-gradient(135deg, #eff6ff 0%, #f0f9ff 100%);
  border-left-color: #3b82f6;
}

.plan-desc-header {
  display: flex;
  align-items: center;
  gap: 12rpx;
  margin-bottom: 14rpx;
}

.plan-desc-icon-wrap {
  width: 44rpx;
  height: 44rpx;
  border-radius: 12rpx;
  background: rgba(16, 185, 129, 0.15);
  display: flex;
  align-items: center;
  justify-content: center;
}

.custom-desc-icon-wrap {
  background: rgba(59, 130, 246, 0.15);
}

.plan-todo-icon-wrap {
  background: rgba(16, 185, 129, 0.15);
}

.plan-desc-title {
  font-size: 26rpx;
  font-weight: 700;
  color: #0f172a;
}

.plan-desc-text {
  font-size: 24rpx;
  color: #475569;
  line-height: 1.8;
  font-weight: 500;
}

/* ===== Plan Todo Section ===== */
.plan-todo-section {
  background: white;
  border-radius: 20rpx;
  padding: 24rpx;
  margin-top: 28rpx;
  box-shadow: 0 2rpx 12rpx rgba(15, 23, 42, 0.04);
  max-width: 100%;
  overflow: hidden;
  word-break: break-word;
  overflow-wrap: break-word;
}

.plan-todo-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
}

.plan-todo-add-btn {
  padding: 8rpx 20rpx;
  background: #f0fdf4;
  border-radius: 20rpx;
  border: 2rpx solid #bbf7d0;
}

.plan-todo-add-form {
  background: #f8fafc;
  border-radius: 16rpx;
  padding: 20rpx;
  margin-bottom: 16rpx;
  max-width: 100%;
  overflow: hidden;
}

.plan-todo-input {
  width: 100%;
  max-width: 100%;
  height: 72rpx;
  background: white;
  border: 2rpx solid #e2e8f0;
  border-radius: 12rpx;
  padding: 0 20rpx;
  font-size: 26rpx;
  color: #0f172a;
  box-sizing: border-box;
  margin-bottom: 16rpx;
}

.plan-todo-add-actions {
  display: flex;
  gap: 12rpx;
}

.plan-todo-add-confirm {
  flex: 1;
  background: #10b981;
  color: white;
  text-align: center;
  padding: 14rpx;
  border-radius: 12rpx;
  font-size: 24rpx;
  font-weight: 600;
}

.plan-todo-add-cancel {
  flex: 1;
  background: #f1f5f9;
  color: #64748b;
  text-align: center;
  padding: 14rpx;
  border-radius: 12rpx;
  font-size: 24rpx;
  font-weight: 600;
}

.plan-todo-list {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.plan-todo-item {
  display: flex;
  align-items: center;
  gap: 16rpx;
  padding: 20rpx 0;
  border-bottom: 1rpx solid #f1f5f9;
  transition: background 0.2s;
}

.plan-todo-item:last-child {
  border-bottom: none;
}

.plan-todo-checkbox {
  width: 40rpx;
  height: 40rpx;
  border-radius: 10rpx;
  border: 3rpx solid #cbd5e1;
  background-color: transparent;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all 0.2s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.plan-todo-checkbox.checked {
  background-color: #10b981;
  border-color: #10b981;
  transform: scale(1.1);
}

.plan-todo-text {
  flex: 1;
  font-size: 26rpx;
  color: #334155;
  font-weight: 500;
  line-height: 1.5;
  transition: all 0.3s;
}

.plan-todo-delete {
  width: 48rpx;
  height: 48rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  border-radius: 12rpx;
  transition: background 0.2s;
}

.plan-todo-delete:active {
  background: #fef2f2;
}

.plan-todo-empty {
  padding: 40rpx 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.plan-todo-empty-text {
  font-size: 24rpx;
  color: #94a3b8;
  font-weight: 500;
}

/* ===== Scroll View Optimization ===== */
.plan-detail-content,
.dish-detail-content,
.custom-plan-content {
  flex: 1;
  padding: 24rpx 36rpx 16rpx;
  overflow: hidden;
  max-width: 100%;
  word-break: break-word;
  overflow-wrap: break-word;
}

/* ===== Responsive ===== */
@media screen and (max-width: 375px) {
  .modern-health-page {
    padding-left: 20rpx;
    padding-right: 20rpx;
  }
  .plan-nutrition-summary {
    grid-template-columns: repeat(2, 1fr);
  }
  .dish-meta-row {
    grid-template-columns: repeat(3, 1fr);
  }
  .badge-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .plan-detail-content,
  .dish-detail-content,
  .custom-plan-content {
    padding: 20rpx 24rpx 12rpx;
  }
  .plan-detail-header,
  .dish-detail-header,
  .custom-plan-header {
    padding: 8rpx 24rpx 16rpx;
  }
  .plan-detail-footer,
  .custom-plan-footer {
    padding: 16rpx 24rpx;
    padding-bottom: calc(16rpx + env(safe-area-inset-bottom));
  }
  .nutrition-val {
    font-size: 26rpx;
  }
  .dish-emoji-badge {
    width: 72rpx;
    height: 72rpx;
    font-size: 32rpx;
  }
  .plan-desc-section,
  .custom-plan-desc-section {
    padding: 20rpx;
  }
  .plan-todo-section {
    padding: 20rpx;
  }
  .template-card {
    width: 240rpx;
    min-width: 240rpx;
    max-width: 240rpx;
  }
  .bento-card {
    padding: 24rpx;
  }
}

@media screen and (min-width: 376px) and (max-width: 414px) {
  .template-card {
    width: 260rpx;
    min-width: 260rpx;
    max-width: 260rpx;
  }
}

@media screen and (min-width: 768px) {
  .modern-health-page {
    max-width: 430px;
    margin: 0 auto;
  }
  .plan-detail-modal,
  .custom-plan-modal {
    max-width: 600px;
    margin: 0 auto;
    border-radius: 40rpx 40rpx 0 0;
  }
  .dish-detail-modal {
    max-width: 600px;
    margin: 0 auto;
    border-radius: 40rpx 40rpx 0 0;
  }
}

@media screen and (min-width: 1024px) {
  .modern-health-page {
    max-width: 430px;
    margin: 0 auto;
  }
}

/* ===== Template Groups ===== */
.template-groups {
  display: flex;
  flex-direction: column;
  gap: 24rpx;
  padding: 0 32rpx;
  margin-bottom: 32rpx;
}

.template-group {
  background: white;
  border-radius: 24rpx;
  padding: 28rpx;
  box-shadow: 0 4rpx 16rpx rgba(15, 23, 42, 0.05);
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.template-group:active {
  transform: scale(0.98);
  box-shadow: 0 2rpx 8rpx rgba(15, 23, 42, 0.1);
}

.template-group-header {
  display: flex;
  align-items: center;
  gap: 16rpx;
  margin-bottom: 20rpx;
  padding-bottom: 16rpx;
  border-bottom: 1rpx solid #f1f5f9;
}

.template-group-icon {
  font-size: 40rpx;
  flex-shrink: 0;
}

.template-group-name {
  font-size: 30rpx;
  font-weight: 700;
  color: #0f172a;
}

.template-group-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.template-meal-list {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
  flex: 1;
}

.template-meal-item {
  display: flex;
  align-items: center;
  gap: 6rpx;
  background: #f8fafc;
  padding: 8rpx 14rpx;
  border-radius: 12rpx;
}

.meal-type-icon {
  font-size: 22rpx;
}

.meal-type-name {
  font-size: 22rpx;
  color: #64748b;
  font-weight: 500;
}

.template-view-btn {
  background: #f1f5f9;
  color: #64748b;
  padding: 10rpx 20rpx;
  border-radius: 12rpx;
  font-size: 20rpx;
  font-weight: 600;
  flex-shrink: 0;
  transition: all 0.2s;
}

.template-view-btn:active {
  transform: scale(0.96);
  background: #e2e8f0;
}

.template-group-actions {
  display: flex;
  gap: 12rpx;
  align-items: center;
}

.template-select-btn {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  padding: 10rpx 24rpx;
  border-radius: 12rpx;
  font-size: 20rpx;
  font-weight: 600;
  flex-shrink: 0;
  box-shadow: 0 2rpx 8rpx rgba(16, 185, 129, 0.2);
  transition: all 0.2s;
}

.template-select-btn.selected {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  box-shadow: 0 2rpx 8rpx rgba(59, 130, 246, 0.2);
}

.template-select-btn:active {
  transform: scale(0.96);
}

.template-group-title {
  display: flex;
  align-items: center;
  gap: 16rpx;
  flex: 1;
}

.template-group-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16rpx;
  margin-bottom: 16rpx;
  padding-bottom: 16rpx;
  border-bottom: 1rpx solid #f1f5f9;
}

.template-group-desc {
  font-size: 24rpx;
  color: #64748b;
  font-weight: 500;
  flex: 1;
  line-height: 1.5;
}

.template-group-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16rpx;
}

.template-group.selected {
  border: 2rpx solid #10b981;
  box-shadow: 0 4rpx 20rpx rgba(16, 185, 129, 0.15);
}

.selected-badge {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  padding: 6rpx 14rpx;
  border-radius: 20rpx;
  flex-shrink: 0;
}

.selected-badge-text {
  color: white;
  font-size: 18rpx;
  font-weight: 700;
}

/* Hide old meal list styles */
.template-meal-list,
.template-meal-item,
.meal-type-icon,
.meal-type-name {
  display: none;
}
</style>

