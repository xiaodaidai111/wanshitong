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
          <text class="greeting-title">早上好，开始今日个性化学习</text>
          <text class="greeting-subtitle">画像智能体为你持续更新学习状态</text>
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
          <text>历史趋势</text>
        </view>
        <view class="tab-item" :class="{ active: activeTab === 2 }" @click="switchTab(2)">
          <text>路径规划</text>
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
              <text class="card-title">知识掌握风险雷达</text>
            </view>
            <view class="card-body">
              <view class="value-row">
                <text class="main-val">{{ riskLevel }}</text>
              </view>
              <view class="curve-mockup">
                <!-- CSS Based Curve Simulation -->
                <svg viewBox="0 0 100 20" preserveAspectRatio="none" style="width:100%; height:40rpx;">
                  <path d="M0 10 Q10 20 20 10 T40 10 T60 5 T80 15 T100 10" fill="none" class="animated-path" :stroke="getRiskStroke()" stroke-width="2" stroke-linecap="round"/>
                  <defs>
                    <linearGradient id="mintGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                      <stop offset="0%" stop-color="#34d399" />
                      <stop offset="100%" stop-color="#0284c7" />
                    </linearGradient>
                    <linearGradient id="orangeGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                      <stop offset="0%" stop-color="#f59e0b" />
                      <stop offset="100%" stop-color="#f97316" />
                    </linearGradient>
                    <linearGradient id="redGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                      <stop offset="0%" stop-color="#ef4444" />
                      <stop offset="100%" stop-color="#dc2626" />
                    </linearGradient>
                  </defs>
                </svg>
              </view>
              <text class="status-msg" :style="{ color: riskStatus.color }">{{ riskStatus.text }}</text>
            </view>
          </view>

          <!-- 学习画像 Card (Medium) -->
          <view class="bento-card sleep-card hover-glow tap-effect stagger-4">
            <view class="card-header">
              <view class="icon-box">
                <text style="font-size:28rpx">⚖️</text>
              </view>
              <text class="card-title">学习画像维度</text>
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

          <!-- 今日学习卡片 (Large) -->
          <view class="bento-card activity-card hover-glow tap-effect stagger-5">
            <view class="card-header">
              <view class="icon-box">
                <text style="font-size:28rpx">🍎</text>
              </view>
              <text class="card-title">今日学习</text>
              <view class="add-btn-mini tap-effect" @click="showAddFoodModal = true" style="background:#10b981; color:white; padding:8rpx 20rpx; border-radius:20rpx; font-size:24rpx; font-weight:600;">+ </view>
            </view>
            <view class="card-body">
              <view v-if="foodRecords.length === 0" class="empty-state" style="padding:40rpx 0; text-align:center;">
                <text class="empty-text">今天还没有学习记录，点击"记录"添加</text>
              </view>
              <view v-else class="food-records-list">
                <view class="food-record-item tap-effect" v-for="(food, index) in foodRecords" :key="food.id">
                  <view class="food-record-left">
                    <view v-if="food.image" class="food-image">
                      <image :src="food.image" mode="aspectFill"></image>
                    </view>
                    <view v-else class="food-icon">
                      <text style="font-size:48rpx">{{ getFoodEmoji(food.name) }}</text>
                    </view>
                  </view>
                  <view class="food-record-content">
                    <text class="food-name">{{ food.name }}</text>
                    <text class="food-time">{{ food.time }}</text>
                    <text v-if="food.calories" class="food-calories">{{ food.calories }}分钟</text>
                  </view>
                  <view class="food-record-delete tap-effect" @click.stop="deleteFoodRecord(food.id)">
                    <text style="color:#ef4444; font-size:32rpx;">×</text>
                  </view>
                </view>
              </view>
            </view>
          </view>
        </view> <!-- End Bento Grid -->

        <!-- Actionable Todo Cards (Medication, Water) -->
        <view class="todo-section stagger-6">
          <view class="todo-header-row" style="display:flex; justify-content:space-between; align-items:center; margin-bottom:24rpx;">
            <text class="section-title" style="margin-bottom:0;">今日学习待办</text>
            <view class="add-btn-mini tap-effect" @click="showAddModal = true" style="background:#10b981; color:white; padding:8rpx 20rpx; border-radius:20rpx; font-size:24rpx; font-weight:600;">+ 新增</view>
          </view>

          <!-- Add Todo Input Area (Shown when showAddModal is true) -->
          <view v-if="showAddModal" class="add-todo-form hover-glow" style="background:white; border-radius:32rpx; padding:32rpx; margin-bottom:24rpx; box-shadow: 0 8rpx 32rpx rgba(15, 23, 42, 0.05);">
            <input v-model="newTodoTitle" placeholder="待办名称 (如 完成A*练习)" style="font-size:34rpx; border-bottom:1rpx solid #e2e8f0; padding:24rpx 0; margin-bottom:24rpx; height:80rpx; width:100%;"/>
            <input v-model="newTodoSub" placeholder="备注 (如 10道题)" style="font-size:30rpx; border-bottom:1rpx solid #e2e8f0; padding:24rpx 0; margin-bottom:32rpx; height:80rpx; width:100%;"/>
            <view style="display:flex; gap:20rpx;">
              <view class="tap-effect" @click="addTodo" style="flex:1; background:#10b981; color:white; text-align:center; padding:24rpx; border-radius:16rpx; font-size:28rpx; font-weight:700;">确认添加</view>
              <view class="tap-effect" @click="showAddModal = false" style="flex:1; background:#f1f5f9; color:#64748b; text-align:center; padding:24rpx; border-radius:16rpx; font-size:28rpx; font-weight:700;">取消</view>
            </view>
          </view>
          
          <view class="todo-card tap-effect" v-for="(todo, index) in todos" :key="todo.id" @click.stop="toggleTodo(index)">
             <view class="todo-left">
                <view class="todo-info">
                  <text class="info-title" :class="{ 'tx-del': todo.done }">{{ todo.title }}</text>
                  <text class="info-sub" v-if="todo.sub">{{ todo.sub }}</text>
                </view>
             </view>
             <view class="todo-right" style="display:flex; align-items:center; gap:24rpx;">
                <view class="checkbox-wrap">
                   <view class="custom-checkbox" :class="{ checked: todo.done }">
                     <text v-if="todo.done" class="check-mark">✓</text>
                   </view>
                </view>
                <view class="delete-btn tap-effect" @click.stop="deleteTodo(todo.id)" style="padding:10rpx;">
                  <text style="color:#ef4444; font-size:32rpx;">×</text>
                </view>
             </view>
          </view>
          
          <view v-if="todos.length === 0" class="empty-state" style="padding:60rpx 0;">
            <text class="empty-text">今天还没有学习待办，点击“新增”添加吧</text>
          </view>
        </view>

      </view> <!-- End Tab 0 -->

      <!-- TAB 1: 历史趋势 (Trend Tab) -->
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
              <image class="insight-avatar" src="/static/healthymanager.png" mode="aspectFill"></image>
              <view class="insight-bubble">
                <text class="bubble-text">这周搜索算法掌握度稳步上升！继续保持案例练习节奏</text>
              </view>
            </view>
            <view class="insight-tags">
              <text class="tag positive">讲解文档已完成</text>
              <text class="tag warning">实操练习需加强</text>
            </view>
          </view>

          <!-- Weekly Trend Chart -->
          <view class="bento-card stagger-5">
            <view class="card-header">
              <view class="icon-box">
                <text class="lucide-icon">📈</text>
              </view>
              <text class="card-title">近七天学习掌握度变化</text>
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
            <text class="action-desc">数据显示你的学习掌握度在上升。明天建议补充 A* 搜索启发式函数练习，并完成一组编程题。</text>
            <view class="challenge-btn">好的，我试试</view>
          </view>
        </view>

        <view v-if="reportView === 'monthly'">
          <!-- Annual Summary Banner -->
          <view class="annual-banner hover-glow tap-effect stagger-4" @click="showAnnualReport">
            <view class="banner-content">
              <text class="banner-title">2026 学习总结</text>
              <text class="banner-subtitle">点击查看你的课程成长里程碑</text>
            </view>
            <text class="lucide-icon banner-arrow" style="opacity:0.8">前往</text>
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
              <text class="status-msg good-status">总体呈现下降趋势，减重2.5kg</text>
            </view>

            <view class="bento-card activity-card hover-glow stagger-6">
              <view class="card-header">
                <view class="icon-box"><text style="font-size:28rpx">🍎</text></view>
                <text class="card-title">课程掌握程度</text>
              </view>
              <view class="chart-container-monthly">
                 <view class="month-bar-group" v-for="(m, i) in monthlyActivity" :key="'a'+i">
                   <view class="month-bar activity" :style="{ height: isLoaded ? m.value + '%' : '0%' }"></view>
                   <text class="month-label">{{ m.month }}</text>
                 </view>
              </view>
              <text class="status-msg good-status">本月人工智能导论掌握度显著提升！</text>
            </view>
          </view>
        </view>
      </view> <!-- End Tab 1 -->

      <!-- TAB 2: 路径规划 (Intervention Tab) -->
      <view class="tab-content intervene-tab" :class="{ 'content-active': activeTab === 2 }">
        
        <!-- Dietary Decision Slider -->
        <view class="bento-card hover-glow stagger-3" style="padding: 24rpx 0;">
          <view class="card-header" style="padding: 0 32rpx;">
            <view class="icon-box">
              <text style="font-size:28rpx">🥗</text>
            </view>
            <view>
               <text class="card-title" style="display:block;">个性化学习路径推荐</text>
               <text style="font-size:20rpx; color:#94a3b8; font-weight: 500;">学生画像驱动 · 资源精准推送</text>
            </view>
          </view>
          
          <view class="template-groups">
            <view class="template-group" v-for="(tpl, index) in goalTemplates" :key="index" :class="{ 'selected': selectedPlanIndex === index }">
              <view class="template-group-header">
                <view class="template-group-title">
                  <text class="template-group-icon">{{ tpl.icon }}</text>
                  <text class="template-group-name">{{ tpl.name }}</text>
                </view>
                <view v-if="selectedPlanIndex === index" class="selected-badge">
                  <text class="selected-badge-text">已选择</text>
                </view>
              </view>
              <view class="template-group-content">
                <text class="template-group-desc">{{ tpl.desc }}</text>
                <view class="template-group-actions">
                  <view class="template-view-btn tap-effect" @click="viewPlanDetail(tpl)">详情</view>
                  <view class="template-select-btn tap-effect" :class="{ 'selected': selectedPlanIndex === index }" @click="selectPlan(tpl, index)">
                    <text>{{ selectedPlanIndex === index ? '已选择' : '选择计划' }}</text>
                  </view>
                </view>
              </view>
            </view>
          </view>

          <view style="padding: 0 32rpx 32rpx;">
            <view class="custom-plan-btn tap-effect" @click="showCustomPlanModal = true">
              <text style="font-size:28rpx; font-weight:700; color:#0f172a;">✏️ 自定义学习计划</text>
              <text style="font-size:22rpx; color:#64748b; margin-top:4rpx;">根据个人需求自由设置</text>
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
            <text class="plan-desc-text">{{ selectedPlan.name }}方案将结合学生画像、课程知识库和练习反馈，帮助你{{ selectedPlan.desc }}。每日建议学习时长约{{ selectedPlan.totalCalories }}分钟，系统会持续推送讲解、题库、导图和实操资源。</text>
          </view>

          <view class="plan-nutrition-summary">
            <view class="nutrition-item nutrition-cal">
              <text class="nutrition-val">{{ selectedPlan.totalCalories }}</text>
              <text class="nutrition-label">目标时长</text>
            </view>
            <view class="nutrition-item nutrition-pro">
              <text class="nutrition-val">{{ selectedPlan.protein }}类</text>
              <text class="nutrition-label">讲解资源</text>
            </view>
            <view class="nutrition-item nutrition-carb">
              <text class="nutrition-val">{{ selectedPlan.carbs }}组</text>
              <text class="nutrition-label">练习任务</text>
            </view>
            <view class="nutrition-item nutrition-fat">
              <text class="nutrition-val">{{ selectedPlan.fat }}项</text>
              <text class="nutrition-label">实操案例</text>
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
                    <text class="dish-tag cal-tag">{{ dish.calories }}学习点</text>
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
              <text class="meta-chip-label">学习点</text>
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
              <text class="dish-section-title">学习步骤</text>
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
          <text class="custom-plan-title">✏️ 自定义学习计划</text>
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
            <text class="plan-desc-text">请根据你的专业、学习目标、知识基础和偏好填写信息。系统将结合学生画像智能生成个性化学习计划，并动态推荐文档、题库、案例和多模态资源。</text>
          </view>

          <view class="form-group">
            <text class="form-label">计划名称</text>
            <input v-model="customPlan.name" placeholder="如：我的AI导论冲刺计划" class="form-input" />
          </view>
          <view class="form-group">
            <text class="form-label">学习目标</text>
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
            <text class="form-label">每日目标时长 (分钟)</text>
            <input v-model="customPlan.calories" type="number" placeholder="如：90" class="form-input" />
          </view>
          <view class="form-group">
            <text class="form-label">学习环节</text>
            <view class="form-options">
              <view class="form-option meal-option" v-for="(m, mIdx) in mealOptions" :key="mIdx"
                :class="{ active: customPlan.meals.includes(m.value) }"
                @click="toggleMealOption(m.value)">
                <text class="form-option-text">{{ m.label }}</text>
              </view>
            </view>
          </view>
          <view class="form-group">
            <text class="form-label">学习偏好</text>
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
            <textarea v-model="customPlan.remark" placeholder="如：搜索算法薄弱、偏好图解和代码案例..." class="form-textarea" :maxlength="200"></textarea>
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
            <text style="font-size:28rpx; font-weight:600; color:white;">生成计划</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 学习记录弹窗 -->
    <view class="modal-overlay" v-if="showAddFoodModal" @click="showAddFoodModal = false">
      <view class="dish-detail-modal" @click.stop>
        <view class="modal-drag-bar"></view>
        <view class="dish-detail-header">
          <text class="dish-detail-name">📘 记录学习</text>
          <view class="dish-detail-close" @click="showAddFoodModal = false">
            <text style="font-size:28rpx; color:#64748b;">✕</text>
          </view>
        </view>
        <scroll-view class="dish-detail-content" scroll-y="true" :show-scrollbar="false" enhanced :bounces="true">
          <view class="form-group">
            <text class="form-label">学习内容</text>
            <input v-model="newFood.name" placeholder="请输入学习内容" class="form-input" />
          </view>
          <view class="form-group">
            <text class="form-label">学习时间</text>
            <input v-model="newFood.time" type="datetime-local" class="form-input" />
          </view>
          <view class="form-group">
            <text class="form-label">学习时长 (分钟)</text>
            <input v-model="newFood.calories" type="number" placeholder="请输入学习时长" class="form-input" />
          </view>
          <view class="form-group">
            <text class="form-label">备注</text>
            <textarea v-model="newFood.notes" placeholder="添加掌握度、错因或资源反馈" class="form-textarea" :maxlength="200"></textarea>
          </view>
          <view class="form-group">
            <text class="form-label">学习截图</text>
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
          <text class="health-tip-title">📘 学习小提示</text>
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
        '先用自然语言说清楚专业、课程目标和当前困惑，画像智能体会自动抽取学习特征',
        '生成资料后建议先看讲解文档，再做分层练习题，最后完成实操案例',
        '遇到抽象概念时，可以要求系统生成图解说明或短视频脚本',
        '对生成内容要查看知识库依据，避免大模型幻觉影响学习判断',
        '易错点会随练习结果动态更新，学习路径也会同步调整',
        '建议每次学习后记录掌握度，方便效果评估智能体优化资源推送',
        '代码类课程优先结合实操项目学习，比单纯阅读概念更容易形成迁移能力',
        '当练习正确率低于 70% 时，先回到前置知识点补齐基础'
      ],
      showHealthTipModal: false,
      currentHealthTip: '',
      agents: [
        { name: '画像构建智能体', role: '抽取专业、目标、基础、偏好、易错点', status: '更新中', icon: '🧠', color: '#10b981' },
        { name: '资源生成智能体', role: '生成讲解文档、题库、导图与案例', status: '待命', icon: '📚', color: '#3b82f6' },
        { name: '效果评估智能体', role: '分析练习结果并调整学习路径', status: '监测中', icon: '📈', color: '#f59e0b' }
      ],
      todos: [
        { id: 1, title: '完成搜索算法基础讲解', sub: '阅读 20 分钟', done: false },
        { id: 2, title: '完成 A* 搜索练习题', sub: '距离目标还差 5 题', done: false }
      ],
      showAddModal: false,
      newTodoTitle: '',
      newTodoSub: '',
      // 学习记录相关
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
          name: 'AI导论基础巩固计划', icon: '📚', desc: '按知识基础逐步补齐核心概念',
          totalCalories: 90, protein: 3, carbs: 2, fat: 1,
          meals: [
            {
              type: '课前预习', icon: '📘', calories: 20,
              dishes: [
                { name: 'AI基本概念讲解文档', image: '', calories: 8, cooking_time: 8, difficulty: '入门', ingredients: ['课程知识库', '学生画像', '关键概念'], steps: ['阅读核心定义', '标记陌生术语', '向辅导智能体追问例子'] },
                { name: '搜索算法可视化导图', image: '', calories: 6, cooking_time: 6, difficulty: '入门', ingredients: ['宽度优先搜索', '深度优先搜索', '启发式搜索'], steps: ['查看算法关系', '对比适用场景', '记录易混点'] },
                { name: 'AI伦理安全短案例', image: '', calories: 6, cooking_time: 6, difficulty: '入门', ingredients: ['内容安全', '防幻觉校验', '资源可信度'], steps: ['阅读案例', '指出风险点', '查看知识库依据'] }
              ]
            },
            {
              type: '课堂复盘', icon: '🧠', calories: 25,
              dishes: [
                { name: '课堂知识点摘要', image: '', calories: 10, cooking_time: 10, difficulty: '基础', ingredients: ['教师课件', '课程大纲', '课堂笔记'], steps: ['按章节生成摘要', '补充关键公式', '生成三条自测问题'] },
                { name: '概念辨析题库', image: '', calories: 8, cooking_time: 8, difficulty: '基础', ingredients: ['易错概念', '选择题', '判断题'], steps: ['完成10道题', '查看错因解析', '更新薄弱点画像'] },
                { name: '知识库依据核验', image: '', calories: 7, cooking_time: 7, difficulty: '基础', ingredients: ['课程知识库片段', '生成内容引用', '安全审核规则'], steps: ['查看引用来源', '标记无依据内容', '重新生成存疑段落'] }
              ]
            },
            {
              type: '练习训练', icon: '📝', calories: 25,
              dishes: [
                { name: '分层练习题包', image: '', calories: 12, cooking_time: 12, difficulty: '基础', ingredients: ['基础题', '进阶题', '错题追踪'], steps: ['先做基础题', '错题自动归因', '根据正确率调整难度'] },
                { name: '搜索算法手算练习', image: '', calories: 8, cooking_time: 8, difficulty: '基础', ingredients: ['图结构样例', '队列/栈过程', '路径结果'], steps: ['手推访问顺序', '对照标准答案', '记录出错步骤'] }
              ]
            },
            {
              type: '项目实操', icon: '💻', calories: 20,
              dishes: [
                { name: '最短路径小实验', image: '', calories: 12, cooking_time: 12, difficulty: '进阶', ingredients: ['Python示例', '图搜索数据', '测试用例'], steps: ['运行示例代码', '修改起终点', '解释输出路径'] },
                { name: '实操复盘卡片', image: '', calories: 8, cooking_time: 8, difficulty: '基础', ingredients: ['实验截图', '错误日志', '修复建议'], steps: ['记录运行结果', '总结关键收获', '同步到学生画像'] }
              ]
            }
          ]
        },
        {
          name: '搜索算法专项突破计划', icon: '🧭', desc: '围绕图搜索、启发式函数和 A* 算法强化训练',
          totalCalories: 100, protein: 2, carbs: 3, fat: 2,
          meals: [
            {
              type: '前置补齐', icon: '🧩', calories: 20,
              dishes: [
                { name: '图结构基础速查', image: '', calories: 8, cooking_time: 8, difficulty: '基础', ingredients: ['节点与边', '邻接表', '权重'], steps: ['阅读速查表', '完成概念连线', '确认前置掌握度'] },
                { name: 'BFS/DFS对比讲解', image: '', calories: 12, cooking_time: 12, difficulty: '基础', ingredients: ['搜索顺序', '数据结构', '适用场景'], steps: ['看对比图', '手推两个例子', '生成错题提醒'] }
              ]
            },
            {
              type: '专项训练', icon: '🎯', calories: 35,
              dishes: [
                { name: 'A*算法分步题', image: '', calories: 15, cooking_time: 15, difficulty: '进阶', ingredients: ['启发函数', '开放列表', '关闭列表'], steps: ['逐步计算f值', '选择下一个节点', '解释路径选择原因'] },
                { name: '启发式函数案例库', image: '', calories: 10, cooking_time: 10, difficulty: '进阶', ingredients: ['曼哈顿距离', '欧氏距离', '一致性'], steps: ['比较函数差异', '判断是否可采纳', '生成反例说明'] },
                { name: '错题归因训练', image: '', calories: 10, cooking_time: 10, difficulty: '基础', ingredients: ['错题记录', '错因标签', '补救资源'], steps: ['查看错题', '选择错因', '推送对应讲解'] }
              ]
            },
            {
              type: '项目实操', icon: '💻', calories: 30,
              dishes: [
                { name: '迷宫寻路代码案例', image: '', calories: 18, cooking_time: 18, difficulty: '进阶', ingredients: ['迷宫地图', 'A*代码模板', '路径可视化'], steps: ['运行模板', '替换启发函数', '截图对比结果'] },
                { name: '代码讲解生成', image: '', calories: 12, cooking_time: 12, difficulty: '基础', ingredients: ['源码片段', '变量说明', '执行流程'], steps: ['上传代码', '生成逐行解释', '提取面试问答'] }
              ]
            },
            {
              type: '效果评估', icon: '📈', calories: 15,
              dishes: [
                { name: '专项掌握度报告', image: '', calories: 8, cooking_time: 8, difficulty: '基础', ingredients: ['正确率', '完成时长', '知识点覆盖'], steps: ['查看雷达图', '确认达标项', '生成下一阶段计划'] },
                { name: '个性化复习包', image: '', calories: 7, cooking_time: 7, difficulty: '基础', ingredients: ['薄弱点', '同类题', '微课脚本'], steps: ['选择薄弱点', '生成复习包', '加入今日待办'] }
              ]
            }
          ]
        },
        {
          name: '大模型智能体拓展计划', icon: '🤖', desc: '面向竞赛作品展示的多智能体协同学习任务',
          totalCalories: 120, protein: 4, carbs: 2, fat: 2,
          meals: [
            {
              type: '主题导入', icon: '🚀', calories: 25,
              dishes: [
                { name: '多智能体架构讲解', image: '', calories: 12, cooking_time: 12, difficulty: '进阶', ingredients: ['画像智能体', '资源生成智能体', '评估智能体'], steps: ['阅读架构说明', '理解协作流程', '提炼展示话术'] },
                { name: '防幻觉机制卡片', image: '', calories: 13, cooking_time: 13, difficulty: '进阶', ingredients: ['知识库检索', '引用校验', '安全审核'], steps: ['查看机制图', '识别风险样例', '生成修正建议'] }
              ]
            },
            {
              type: '资源生成', icon: '📚', calories: 35,
              dishes: [
                { name: '五类资源生成演示', image: '', calories: 20, cooking_time: 20, difficulty: '进阶', ingredients: ['讲解文档', '题库', '导图', '案例', '学习脚本'], steps: ['输入知识点', '选择资源类型', '查看进度提示与结果'] },
                { name: '多模态资源样例', image: '', calories: 15, cooking_time: 15, difficulty: '基础', ingredients: ['图片素材', '课程文本', '语音讲解稿'], steps: ['上传课程图片', '生成图文解析', '补充语音脚本'] }
              ]
            },
            {
              type: '作品展示', icon: '🏁', calories: 40,
              dishes: [
                { name: '竞赛演示路径', image: '', calories: 18, cooking_time: 18, difficulty: '进阶', ingredients: ['学生画像', '资源生成', '路径规划', '效果评估'], steps: ['按演示顺序操作', '记录关键截图', '准备答辩说明'] },
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
        { id: 1, title: '准备本周课程资源清单', done: false },
        { id: 2, title: '查看系统推荐路径依据', done: false },
        { id: 3, title: '记录每日学习打卡', done: false },
        { id: 4, title: '每周查看学习效果变化', done: false }
      ],
      showPlanTodoAdd: false,
      newPlanTodoTitle: '',
      showDishDetail: false,
      selectedDish: {},
      showCustomPlanModal: false,
      customPlanTodos: [
        { id: 1, title: '确认专业课程与学习目标', done: false },
        { id: 2, title: '设定每日学习时长目标', done: false },
        { id: 3, title: '选择合适的学习环节', done: false },
        { id: 4, title: '记录学习偏好与薄弱点', done: false },
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
        { label: '基础巩固', icon: '📘', value: 'foundation' },
        { label: '项目实操', icon: '💻', value: 'practice' },
        { label: '考试冲刺', icon: '📝', value: 'exam' },
        { label: '论文拓展', icon: '🔍', value: 'research' }
      ],
      mealOptions: [
        { label: '课前预习', value: 'preview' },
        { label: '课堂复盘', value: 'review' },
        { label: '练习训练', value: 'practice' },
        { label: '项目实操', value: 'project' }
      ],
      dietPreferences: ['图解优先', '案例驱动', '代码实操', '题库训练', '短视频讲解', '拓展阅读', '低难度入门', '高阶挑战'],
      achievements: [
        { name: '画像完成', icon: '🧠', unlocked: true },
        { name: '七日连学', icon: '🔥', unlocked: true },
        { name: '题库达人', icon: '📝', unlocked: false },
        { name: '实操新星', icon: '💻', unlocked: false }
      ],
      // 学习掌握风险相关
      riskLevel: '低风险',
      riskScore: 0,
      riskStatus: { text: '画像监测：当前基础稳定，建议进入搜索算法专项训练', color: '#10b981' }
    }
  },
  computed: {
    bmi() {
      return '6维';
    },
    bmiStatus() {
      return { text: '画像完整', color: '#10b981', sub: '基础、目标、偏好、进度、易错点、资源反馈' };
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
    toggleTodo(index) {
      if (this.todos[index]) {
        this.todos[index].done = !this.todos[index].done;
        uni.vibrateShort && uni.vibrateShort();
      }
    },
    addTodo() {
      if (!this.newTodoTitle.trim()) {
        uni.showToast({ title: '请输入待办名称', icon: 'none' });
        return;
      }
      const newTodo = {
        id: Date.now(),
        title: this.newTodoTitle,
        sub: this.newTodoSub,
        done: false
      };
      this.todos.unshift(newTodo);
      this.newTodoTitle = '';
      this.newTodoSub = '';
      this.showAddModal = false;
      uni.showToast({ title: '添加成功', icon: 'success' });
    },
    deleteTodo(id) {
      uni.showModal({
        title: '确认删除',
        content: '确定要删除这项待办吗？',
        success: (res) => {
          if (res.confirm) {
            this.todos = this.todos.filter(t => t.id !== id);
            uni.showToast({ title: '已删除', icon: 'success' });
          }
        }
      });
    },
    acceptChallenge() {
      uni.showToast({ title: '已加入挑战！明天提醒你', icon: 'success' });
    },
    showAnnualReport() {
      uni.showModal({
        title: '年度总结',
        content: '这里将展示你的年度学习数据，包括掌握度趋势、资源使用分析、练习正确率变化等。（功能开发中）',
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
      uni.showToast({ title: '已应用「' + plan.name + '」计划', icon: 'success' });
      
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
      
      // 发送事件更新个人中心的学习计划
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
        '讲解': '📘', '文档': '📘', '导图': '🧭',
        '题': '📝', '练习': '📝', '错题': '🔁',
        '代码': '💻', '实操': '💻', '案例': '📚',
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
      if (cal <= 100) return '轻量资源，适合快速复盘';
      if (cal <= 200) return '讲练结合，日常学习之选';
      if (cal <= 350) return '项目导向，补充实践能力';
      if (time <= 10) return '快速学习，几分钟完成';
      if (time <= 20) return '步骤清晰，新手也能上手';
      return '深度学习，适合完整时段';
    },
    getHealthOverview(dish) {
      const cal = dish.calories || 0;
      const time = dish.cooking_time || 0;
      const diff = dish.difficulty || '简单';
      const ingCount = (dish.ingredients || []).length;
      let overview = '';
      if (cal <= 100) {
        overview += '这份资源很轻量，适合课前预习或课后快速复盘。';
      } else if (cal <= 200) {
        overview += '这份资源难度适中，讲解与练习搭配合理，适合日常学习。';
      } else if (cal <= 350) {
        overview += '这份资源更偏项目实操，适合补充实践能力。';
      } else {
        overview += '这份资源信息量较大，建议拆分学习并搭配练习题。';
      }
      if (time <= 10) {
        overview += '学习仅需' + time + '分钟，非常适合碎片时间。';
      } else if (time <= 20) {
        overview += '学习需' + time + '分钟，步骤清晰不复杂。';
      } else {
        overview += '需要' + time + '分钟深度学习，适合完整时段。';
      }
      overview += '共包含' + ingCount + '类资源，' + (diff === '简单' ? '难度较低，新手友好。' : '有一定挑战度，适合进阶学习。');
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
        uni.showToast({ title: '请输入有效的目标学习时长', icon: 'none' });
        return;
      }
      if (this.customPlan.meals.length === 0) {
        uni.showToast({ title: '请至少选择一项', icon: 'none' });
        return;
      }
      const goalMap = { foundation: '基础巩固', practice: '项目实操', exam: '考试冲刺', research: '论文拓展' };
      const goalIconMap = { foundation: '📘', practice: '💻', exam: '📝', research: '🔍' };
      const goal = this.customPlan.goal;
      const calories = parseInt(this.customPlan.calories);
      const protein = Math.max(1, this.customPlan.preferences.length || 2);
      const carbs = Math.max(1, this.customPlan.meals.length);
      const fat = this.customPlan.meals.includes('project') ? 2 : 1;
      const mealNameMap = { preview: '课前预习', review: '课堂复盘', practice: '练习训练', project: '项目实操' };
      const mealIconMap = { preview: '📘', review: '🧠', practice: '📝', project: '💻' };
      const resourceMap = {
        preview: [
          { name: '个性化预习讲解', difficulty: '入门', ingredients: ['课程知识库', '学生画像', '关键概念'], steps: ['生成预习摘要', '标记陌生概念', '加入今日待办'] },
          { name: '知识点导图', difficulty: '入门', ingredients: ['章节结构', '先修知识', '学习目标'], steps: ['查看导图', '补齐前置知识', '保存复盘问题'] }
        ],
        review: [
          { name: '课堂复盘报告', difficulty: '基础', ingredients: ['课堂笔记', '练习反馈', '易错点'], steps: ['整理重点', '生成错因', '更新画像'] },
          { name: '知识库依据核验', difficulty: '基础', ingredients: ['生成答案', '引用片段', '安全规则'], steps: ['核对依据', '标注存疑内容', '重新生成'] }
        ],
        practice: [
          { name: '分层练习题包', difficulty: '基础', ingredients: ['基础题', '进阶题', '错题'], steps: ['完成练习', '查看解析', '调整路径'] },
          { name: '错题重练包', difficulty: '基础', ingredients: ['错题记录', '同类题', '提示卡'], steps: ['重做错题', '比较结果', '确认掌握'] }
        ],
        project: [
          { name: '实操案例任务', difficulty: '进阶', ingredients: ['代码模板', '实验数据', '测试用例'], steps: ['运行案例', '修改参数', '提交复盘'] },
          { name: '项目讲解脚本', difficulty: '进阶', ingredients: ['项目目标', '代码片段', '答辩要点'], steps: ['生成脚本', '补充截图', '准备展示'] }
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
      uni.showToast({ title: '计划已生成！', icon: 'success' });
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
    // 学习记录相关方法
    addFoodRecord() {
      if (!this.newFood.name) {
        uni.showToast({ title: '请输入学习内容', icon: 'none' });
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
        content: '确定要删除这条学习记录吗？',
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
        '讲解': '📘', '阅读': '📖', '导图': '🧭', '练习': '📝',
        '题': '📝', '代码': '💻', '实操': '💻', '复盘': '🧠',
        '错题': '🔁', '报告': '📊', '案例': '📚', '项目': '🚀'
      };
      for (const [key, emoji] of Object.entries(foodEmojis)) {
        if (foodName.includes(key)) {
          return emoji;
        }
      }
      return '📘';
    },
    // 计算学习掌握风险等级
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
        if (recordName.includes('错') || recordName.includes('薄弱') || recordName.includes('不会') || recordName.includes('困难')) {
          weakPointCount += 1;
        } else if (recordName.includes('练习') || recordName.includes('题') || recordName.includes('实操') || recordName.includes('代码')) {
          practiceCount += 1;
        } else if (recordName.includes('复盘') || recordName.includes('阅读') || recordName.includes('讲解') || recordName.includes('导图')) {
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
        riskStatus = { text: '画像监测：当前基础稳定，建议进入专项训练', color: '#10b981' };
      } else if (riskScore < 60) {
        riskLevel = '中风险';
        riskStatus = { text: '画像监测：存在薄弱知识点，建议调整学习路径', color: '#f59e0b' };
      } else {
        riskLevel = '高风险';
        riskStatus = { text: '画像监测：掌握度偏低，建议回到前置知识点', color: '#ef4444' };
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
  max-height: 100vh;
  height: 100vh;
  background-color: #f0fdf4;
  padding: calc(44px + constant(safe-area-inset-top)) 32rpx calc(200rpx + constant(safe-area-inset-bottom)) 32rpx;
  padding: calc(44px + env(safe-area-inset-top)) 32rpx calc(200rpx + env(safe-area-inset-bottom)) 32rpx;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  overflow-x: hidden;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
  box-sizing: border-box;
  position: relative;
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
  font-size: 22rpx;
  color: #334155;
  font-weight: 700;
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

/* 学习记录样式 */
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

.agent-list {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
  margin-top: 16rpx;
  max-width: 100%;
  overflow: hidden;
}
.agent-item {
  display: flex;
  align-items: center;
  background: #f8fafc;
  padding: 20rpx;
  border-radius: 24rpx;
  gap: 24rpx;
  transition: transform 0.2s;
  max-width: 100%;
  overflow: hidden;
  word-break: break-word;
  overflow-wrap: break-word;
}
.agent-icon-box {
  width: 80rpx;
  height: 80rpx;
  min-width: 80rpx;
  border-radius: 20rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 40rpx;
}
.agent-info {
  flex: 1;
  min-width: 0;
  overflow: hidden;
}
.agent-status {
  font-size: 22rpx;
  font-weight: 600;
  padding: 8rpx 16rpx;
  border-radius: 30rpx;
  flex-shrink: 0;
  white-space: nowrap;
}

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
    max-width: 750px;
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
    max-width: 900px;
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

