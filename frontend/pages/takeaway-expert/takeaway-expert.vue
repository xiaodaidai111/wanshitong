<template>
  <view class="page-container">
    <!-- 模式：拍照主界面 / 分析中 / 结果 -->
    <template v-if="currentMode === 'camera' || currentMode === 'analyzing' || currentMode === 'result'">
      <!-- ===== 模式：资料上传主界面 ===== -->
      <view class="section-mode" v-if="currentMode === 'camera'">

      <!-- 顶部头衔 -->
      <view class="hero-banner">
        <view class="hero-left">
          <image src="/static/safeguard.png" mode="aspectFill" class="hero-avatar"></image>
        </view>
        <view class="hero-right">
          <view class="hero-badge">多智能体协同</view>
          <text class="hero-name">资源生成智能体·知知</text>
          <text class="hero-tagline">上传课程资料，生成个性化学习资源</text>
        </view>
      </view>

      <!-- 拍照核心区域 -->
      <view class="shoot-section">
        <view class="shoot-card" @click="startAnalyzeFlow">
          <!-- SVG 相机图标 -->
          <view class="camera-icon-wrap">
            <text class="camera-fallback">📷</text>
          </view>
          <text class="shoot-label">上传课程截图 / 知识点图片</text>
          <text class="shoot-sub">点击选择资料，生成讲解、题库与导图</text>
          <view class="shoot-action-row">
            <view class="shoot-action-btn">
              <text class="shoot-action-text">立即开始</text>
            </view>
          </view>
        </view>
      </view>

      <!-- 功能卡片组 -->
      <view class="cards-group">
        <!-- 历史记录 -->
        <view class="func-card">
          <view class="card-header" @click="openHistory">
            <view class="card-title-box">
              <view class="card-dot orange-dot"></view>
              <text class="card-title">历史记录</text>
            </view>
            <text class="card-link">全部 ></text>
          </view>
          <view class="history-list">
            <view class="history-empty" v-if="historyList.length === 0">
              <text class="empty-hint">暂无记录，快去生成第一份学习资源吧</text>
            </view>
            <view class="history-item" v-for="(item, i) in historyList.slice(0, 2)" :key="i" @click="loadRecord(item)">
              <view class="history-icon-box" @click.stop="previewImage(item.image, item.name)">
                <image v-if="item.image" class="history-thumb" :src="item.image" mode="aspectFill"></image>
                <text v-else class="history-icon">😋</text>
              </view>
              <view class="history-info">
                <text class="history-name">{{ item.name }}</text>
                <text class="history-date">{{ item.date }}</text>
              </view>
              <view class="score-pill">
                {{ item.score }}分
              </view>
            </view>
          </view>
        </view>

        <!-- 功能网格 -->
        <view class="func-card">
          <view class="card-header">
            <view class="card-title-box">
              <view class="card-dot blue-dot"></view>
              <text class="card-title">更多功能</text>
            </view>
          </view>
          <view class="grid-row">
            <view class="grid-cell" v-for="item in quickFuncs" :key="item.label" @click="handleQuickFunc(item)">
              <view class="grid-icon-box" :style="{ background: item.bg }">
                <image v-if="item.icon.includes('.png')" :src="item.icon" class="grid-icon" mode="aspectFit"></image>
                <text v-else class="grid-emoji">{{ item.icon }}</text>
              </view>
              <text class="grid-label">{{ item.label }}</text>
            </view>
          </view>
        </view>
      </view>

    </view>

    <!-- ===== 模式：分析中 ===== -->
    <view class="section-mode center-mode" v-else-if="currentMode === 'analyzing'">
      <view class="analyzing-card">
        <view class="analyzing-ring">
          <view class="ring r1"></view>
          <view class="ring r2"></view>
          <view class="ring r3"></view>
          <text class="analyzing-emoji">🍊</text>
        </view>
        <text class="analyzing-title">智能体正在协作...</text>
        <text class="analyzing-sub">解析知识点 · 生成资源 · 校验内容安全</text>
        <view class="analyzing-dots">
          <view class="dot dot1"></view>
          <view class="dot dot2"></view>
          <view class="dot dot3"></view>
        </view>
      </view>
    </view>

    <!-- ===== 模式：结果 ===== -->
    <scroll-view scroll-y class="result-scroll" v-else-if="currentMode === 'result'">

      <!-- 结果 Header -->
      <view class="result-hero">
        <view class="result-hero-bg"></view>
        <view class="result-hero-content">
          <image class="result-food-img" :src="resultData.image || '/static/safeguard.png'" mode="aspectFill" @click="previewImage(resultData.image, resultData.name)"></image>
          <view class="result-meta">
            <text class="result-food-name">{{ resultData.name }}</text>
            <view class="result-score-ring" :style="{ borderColor: scoreColor }">
              <text class="result-score-num" :style="{ color: scoreColor }">{{ resultData.score }}</text>
              <text class="result-score-unit" :style="{ color: scoreColor }">分</text>
            </view>
            <view class="result-level-pill" :style="{ background: scoreLevelBg }">
              <text class="result-level-text">{{ scoreLevel }}</text>
            </view>
          </view>
        </view>
        <view class="health-insight-strip">
          <view class="health-insight-item" v-for="item in healthInsightMetrics" :key="item.label">
            <text class="health-insight-label">{{ item.label }}</text>
            <text class="health-insight-val" :class="item.level">{{ item.value }}</text>
          </view>
        </view>
      </view>

      <!-- 多维评估 -->
      <view class="result-section">
        <view class="section-head">
          <view class="section-accent"></view>
          <text class="section-title">资源生成进度</text>
        </view>
        <view class="dim-list">
          <view class="dim-item" v-for="(d, i) in resultData.dimensions" :key="i">
            <view class="dim-top">
              <text class="dim-name">{{ d.name }}</text>
              <text class="dim-val" :style="{ color: getDimensionColor(d.score) }">{{ d.score }}分</text>
            </view>
            <view class="dim-bar-track">
              <view class="dim-bar-fill" :style="{ width: d.score + '%', background: getDimensionColor(d.score) }"></view>
            </view>
          </view>
        </view>
      </view>

      <!-- 资源分析 -->
      <view class="result-section">
        <view class="section-head">
          <view class="section-accent"></view>
          <text class="section-title">学习资源清单</text>
        </view>
        <view class="nutrition-list">
          <view class="nutrition-item" v-for="(item, index) in resultData.nutrition" :key="index">
            <text class="nutrition-label">{{ item.name }}</text>
            <view class="nutrition-right">
              <text class="nutrition-value">{{ item.percent || item.score }}</text>
              <text class="nutrition-status" :class="item.status">{{ item.status }}</text>
            </view>
          </view>
        </view>
      </view>

      <!-- AI 学习辅导 -->
      <view class="result-section chat-section">
        <view class="section-head">
          <image src="/static/safeguard.png" class="section-avatar" mode="aspectFill"></image>
          <text class="section-title">智能辅导</text>
        </view>
        <view class="chat-area">
          <view
            v-for="(msg, idx) in resultChatList"
            :key="idx"
            class="chat-row"
            :class="msg.type === 'user' ? 'row-user' : 'row-agent'"
          >
            <view class="bubble" :class="msg.type === 'user' ? 'bubble-user' : 'bubble-agent'">
              <text class="bubble-text">{{ msg.text }}</text>
            </view>
          </view>
        </view>
        <view class="chat-input-row">
          <input
            class="chat-input"
            v-model="resultChatMsg"
            placeholder="向学习智能体提问..."
            @confirm="sendResultChat"
          />
          <view class="voice-btn" :class="{ active: isVoiceRecording || isVoiceTranscribing }" @click="toggleVoiceInput">
            <text class="voice-btn-text">{{ isVoiceRecording ? '停止' : (isVoiceTranscribing ? '识别中' : '语音') }}</text>
          </view>
          <view class="send-btn" @click="sendResultChat">
            <text class="send-arrow">➤</text>
          </view>
        </view>
      </view>

      <!-- 学习建议 -->
      <view class="result-section">
        <view class="section-head">
          <view class="section-accent"></view>
          <text class="section-title">学习建议</text>
        </view>
        <view class="suggestions-list">
          <view class="sug-item" v-for="(s, k) in resultData.suggestions" :key="k">
            <view class="sug-icon">💡</view>
            <text class="sug-text">{{ s }}</text>
          </view>
        </view>
      </view>

      <!-- 底部重测按钮 -->
      <view class="bottom-actions">
        <view class="retake-btn" @click="resetToCamera">
          <text class="retake-icon">🔄</text>
          <text class="retake-text">再测一次</text>
        </view>
      </view>

    </scroll-view>

    <!-- ===== 知识点查询弹窗 ===== -->
    <view class="modal-mask" v-if="calorieQueryMode" @click="calorieQueryMode = false"></view>
    <view class="modal-panel" :class="{ open: calorieQueryMode }">
      <view class="modal-header">
        <view class="modal-header-left" @click="calorieQueryMode = false">
          <text class="modal-back-icon">←</text>
        </view>
        <text class="modal-header-title">知识点查询</text>
        <view class="modal-header-right"></view>
      </view>

      <scroll-view scroll-y class="modal-content">
        <view class="calorie-query-content">
          <view class="query-input-section">
            <view class="input-wrapper">
              <input
                type="text"
                v-model="calorieQueryFood"
                placeholder="请输入知识点名称"
                class="query-input"
                @confirm="queryCalories"
              />
              <view class="query-btn" @click="queryCalories">
                <text class="query-btn-text">查询</text>
              </view>
            </view>
          </view>

          <view class="result-section" v-if="calorieQueryResult">
            <view class="food-info">
              <text class="food-name">{{ calorieQueryResult.name }}</text>
              <text class="calorie-value">{{ calorieQueryResult.calories }} 学习点</text>
            </view>
            <view class="nutrition-details">
              <view class="nutrition-item">
                <text class="nutrition-label">基础度</text>
                <text class="nutrition-value">{{ calorieQueryResult.protein }} 星</text>
              </view>
              <view class="nutrition-item">
                <text class="nutrition-label">实践度</text>
                <text class="nutrition-value">{{ calorieQueryResult.fat }} 星</text>
              </view>
              <view class="nutrition-item">
                <text class="nutrition-label">拓展度</text>
                <text class="nutrition-value">{{ calorieQueryResult.carbs }} 星</text>
              </view>
            </view>
          </view>

          <view class="common-foods">
            <text class="section-title">常见知识点</text>
            <view class="food-grid">
              <view class="food-item" v-for="food in commonFoods" :key="food.name" @click="selectCommonFood(food)">
                <text class="food-item-name">{{ food.name }}</text>
                <text class="food-item-calorie">{{ food.calories }} 学习点</text>
              </view>
            </view>
          </view>
        </view>
      </scroll-view>
    </view>

    <!-- ===== 设置弹窗 ===== -->
    <view class="modal-mask" v-if="settingsMode" @click="settingsMode = false"></view>
    <view class="modal-panel" :class="{ open: settingsMode }">
      <view class="modal-header">
        <view class="modal-header-left" @click="settingsMode = false">
          <text class="modal-back-icon">←</text>
        </view>
        <text class="modal-header-title">偏好设置</text>
        <view class="modal-header-right"></view>
      </view>

      <scroll-view scroll-y class="modal-content">
        <view class="settings-content">
          <view class="settings-section">
            <text class="section-title">🛡️ 学习目标</text>
            <view class="settings-list">
              <view class="setting-item">
                <text class="setting-label">目标类型</text>
                <view class="selector-row">
                  <view
                    class="selector-tag"
                    :class="{ active: preferences.goalType === '减肥' }"
                    @click="preferences.goalType = '减肥'"
                  >基础巩固</view>
                  <view
                    class="selector-tag"
                    :class="{ active: preferences.goalType === '增肌' }"
                    @click="preferences.goalType = '增肌'"
                  >项目实操</view>
                  <view
                    class="selector-tag"
                    :class="{ active: preferences.goalType === '维持' }"
                    @click="preferences.goalType = '维持'"
                  >考试冲刺</view>
                  <view
                    class="selector-tag"
                    :class="{ active: preferences.goalType === '增重' }"
                    @click="preferences.goalType = '增重'"
                  >论文拓展</view>
                </view>
              </view>
              <view class="setting-item">
                <text class="setting-label">每日学习目标 (分钟)</text>
                <input
                  type="number"
                  v-model="preferences.dailyCalorieGoal"
                  placeholder="请输入目标时长"
                  class="setting-input"
                />
              </view>
            </view>
          </view>

          <view class="settings-section">
            <text class="section-title">📚 学习偏好</text>
            <view class="settings-list">
              <view class="setting-item">
                <text class="setting-label">学习方式</text>
                <view class="selector-row">
                  <view
                    class="selector-tag"
                    :class="{ active: preferences.dietType === '均衡' }"
                    @click="preferences.dietType = '均衡'"
                  >讲练结合</view>
                  <view
                    class="selector-tag"
                    :class="{ active: preferences.dietType === '高蛋白' }"
                    @click="preferences.dietType = '高蛋白'"
                  >案例驱动</view>
                  <view
                    class="selector-tag"
                    :class="{ active: preferences.dietType === '低脂' }"
                    @click="preferences.dietType = '低脂'"
                  >图解优先</view>
                  <view
                    class="selector-tag"
                    :class="{ active: preferences.dietType === '低碳水' }"
                    @click="preferences.dietType = '低碳水'"
                  >代码实操</view>
                </view>
              </view>
              <view class="setting-item">
                <text class="setting-label">资源偏好</text>
                <view class="selector-row">
                  <view
                    class="selector-tag"
                    :class="{ active: preferences.flavor === '清淡' }"
                    @click="preferences.flavor = '清淡'"
                  >短文档</view>
                  <view
                    class="selector-tag"
                    :class="{ active: preferences.flavor === '微辣' }"
                    @click="preferences.flavor = '微辣'"
                  >短视频</view>
                  <view
                    class="selector-tag"
                    :class="{ active: preferences.flavor === '重口味' }"
                    @click="preferences.flavor = '重口味'"
                  >综合项目</view>
                </view>
              </view>
            </view>
          </view>

          <view class="settings-section">
            <text class="section-title">🚫 学习限制</text>
            <view class="settings-list">
              <view class="setting-item">
                <text class="setting-label">薄弱知识点</text>
                <input
                  type="text"
                  v-model="preferences.allergies"
                  placeholder="如：搜索算法、梯度下降"
                  class="setting-input"
                />
              </view>
              <view class="setting-item">
                <text class="setting-label">暂不推荐内容</text>
                <input
                  type="text"
                  v-model="preferences.avoidIngredients"
                  placeholder="如：高阶论文、长视频"
                  class="setting-input"
                />
              </view>
              <view class="setting-item">
                <text class="setting-label">低难度优先</text>
                <view class="switch-wrapper">
                  <switch v-model="preferences.lowOilSalt" class="small-switch"></switch>
                </view>
              </view>
              <view class="setting-item">
                <text class="setting-label">防幻觉校验</text>
                <view class="switch-wrapper">
                  <switch v-model="preferences.noSugar" class="small-switch"></switch>
                </view>
              </view>
            </view>
          </view>

          <view class="settings-section">
            <text class="section-title">⚙️ 通知设置</text>
            <view class="settings-list">
              <view class="setting-item">
                <text class="setting-label">学习提醒</text>
                <view class="switch-wrapper">
                  <switch v-model="preferences.notifications.healthReminder" class="small-switch"></switch>
                </view>
              </view>
              <view class="setting-item">
                <text class="setting-label">学习周报</text>
                <view class="switch-wrapper">
                  <switch v-model="preferences.notifications.weeklyReport" class="small-switch"></switch>
                </view>
              </view>
              <view class="setting-item">
                <text class="setting-label">每日总结</text>
                <view class="switch-wrapper">
                  <switch v-model="preferences.notifications.dailySummary" class="small-switch"></switch>
                </view>
              </view>
            </view>
          </view>

          <view class="settings-actions">
            <view class="save-btn" @click="savePreferences">
              <text class="save-btn-text">保存偏好</text>
            </view>
          </view>
        </view>
      </scroll-view>
    </view>

    <!-- ===== 手动输入弹窗 ===== -->
    <view class="modal-mask" v-if="manualInputMode" @click="manualInputMode = false"></view>
    <view class="modal-panel" :class="{ open: manualInputMode }">
      <view class="modal-header">
        <view class="modal-header-left" @click="manualInputMode = false">
          <text class="modal-back-icon">←</text>
        </view>
        <text class="modal-header-title">手动输入</text>
        <view class="modal-header-right"></view>
      </view>

      <scroll-view scroll-y class="modal-content">
        <view class="manual-input-content">
          <view class="input-section">
            <view class="input-group">
              <text class="group-title">📘 知识点基本信息</text>
              <view class="input-item">
                <text class="input-label">知识点名称</text>
                <input
                  type="text"
                  v-model="manualInputData.foodName"
                placeholder="请输入知识点名称"
                  class="manual-input"
                />
              </view>
              <view class="input-item">
                <text class="input-label">知识点描述</text>
                <textarea
                  v-model="manualInputData.description"
                  placeholder="请输入课程章节或学习目标（可选）"
                  class="manual-textarea"
                />
              </view>
            </view>

            <view class="input-group">
              <text class="group-title">🧩 资源属性</text>
              <view class="input-item">
                <text class="input-label">关联知识点</text>
                <input
                  type="text"
                  v-model="manualInputData.ingredients"
                  placeholder="如：图搜索、启发式函数"
                  class="manual-input"
                />
              </view>
              <view class="input-item">
                <text class="input-label">资源形式</text>
                <view class="selector-row">
                  <view
                    class="selector-tag"
                    :class="{ active: manualInputData.cookingMethod === '清蒸' }"
                    @click="manualInputData.cookingMethod = '清蒸'"
                  >讲解文档</view>
                  <view
                    class="selector-tag"
                    :class="{ active: manualInputData.cookingMethod === '水煮' }"
                    @click="manualInputData.cookingMethod = '水煮'"
                  >思维导图</view>
                  <view
                    class="selector-tag"
                    :class="{ active: manualInputData.cookingMethod === '炒制' }"
                    @click="manualInputData.cookingMethod = '炒制'"
                  >练习题库</view>
                  <view
                    class="selector-tag"
                    :class="{ active: manualInputData.cookingMethod === '煎炸' }"
                    @click="manualInputData.cookingMethod = '煎炸'"
                  >代码案例</view>
                  <view
                    class="selector-tag"
                    :class="{ active: manualInputData.cookingMethod === '红烧' }"
                    @click="manualInputData.cookingMethod = '红烧'"
                  >视频脚本</view>
                  <view
                    class="selector-tag"
                    :class="{ active: manualInputData.cookingMethod === '烧烤' }"
                    @click="manualInputData.cookingMethod = '烧烤'"
                  >拓展阅读</view>
                </view>
              </view>
              <view class="input-item">
                <text class="input-label">预计学习时长 (分钟)</text>
                <input
                  type="number"
                  v-model="manualInputData.weight"
                placeholder="请输入预计学习时长"
                  class="manual-input"
                />
              </view>
            </view>

            <view class="input-group">
              <text class="group-title">📦 生成属性</text>
              <view class="input-item">
                <text class="input-label">生成等待时长(分钟)</text>
                <input
                  type="number"
                  v-model="manualInputData.deliveryTime"
                placeholder="请输入生成等待时长"
                  class="manual-input"
                />
              </view>
              <view class="input-item">
                <text class="input-label">校验方式</text>
                <view class="selector-row">
                  <view
                    class="selector-tag"
                    :class="{ active: manualInputData.packageMaterial === '知识库引用' }"
                    @click="manualInputData.packageMaterial = '知识库引用'"
                  >知识库引用</view>
                  <view
                    class="selector-tag"
                    :class="{ active: manualInputData.packageMaterial === '来源标注' }"
                    @click="manualInputData.packageMaterial = '来源标注'"
                  >来源标注</view>
                  <view
                    class="selector-tag"
                    :class="{ active: manualInputData.packageMaterial === '教师审核' }"
                    @click="manualInputData.packageMaterial = '教师审核'"
                  >教师审核</view>
                  <view
                    class="selector-tag"
                    :class="{ active: manualInputData.packageMaterial === '题目回测' }"
                    @click="manualInputData.packageMaterial = '题目回测'"
                  >题目回测</view>
                  <view
                    class="selector-tag"
                    :class="{ active: manualInputData.packageMaterial === '同伴互评' }"
                    @click="manualInputData.packageMaterial = '同伴互评'"
                  >同伴互评</view>
                </view>
              </view>
              <view class="input-item">
                <text class="input-label">是否为易错知识点</text>
                <view class="switch-wrapper">
                  <switch v-model="manualInputData.perishable" class="small-switch"></switch>
                </view>
              </view>
            </view>
          </view>

          <view class="input-actions">
            <view class="reset-btn" @click="resetManualInput">
              <text class="reset-btn-text">重置</text>
            </view>
            <view class="submit-btn" @click="saveManualInput">
              <text class="submit-btn-text">保存</text>
            </view>
          </view>
        </view>
      </scroll-view>
    </view>

    <!-- ===== 学习周报弹窗 ===== -->
    <view class="modal-mask" v-if="weeklyReportMode" @click="weeklyReportMode = false"></view>
    <view class="modal-panel" :class="{ open: weeklyReportMode }">
      <view class="modal-header">
        <view class="modal-header-left" @click="weeklyReportMode = false">
          <text class="modal-back-icon">←</text>
        </view>
        <text class="modal-header-title">学习周报</text>
        <view class="modal-header-right"></view>
      </view>

      <scroll-view scroll-y class="modal-content">
        <view class="weekly-report-content">
          <view class="report-summary">
            <view class="summary-card">
              <text class="summary-title">本周学习时长</text>
              <text class="summary-value">{{ weeklyReportData.totalCalories }} 分钟</text>
            </view>
            <view class="summary-card">
              <text class="summary-title">日均学习时长</text>
              <text class="summary-value">{{ weeklyReportData.averageCalories }} 分钟</text>
            </view>
          </view>

          <view class="report-section">
            <text class="section-title">每日学习投入</text>
            <view class="calorie-chart">
              <view class="chart-container">
                <view class="chart-bar" v-for="(day, index) in weeklyReportData.days" :key="index">
                  <view class="bar-wrapper">
                    <view class="bar" :style="{ height: (day.calories / 120) * 100 + '%' }"></view>
                  </view>
                  <text class="bar-label">{{ day.day }}</text>
                  <text class="bar-value">{{ day.calories }} 分钟</text>
                </view>
              </view>
            </view>
          </view>

          <view class="report-section">
            <text class="section-title">资源使用分析</text>
            <view class="nutrition-chart">
              <view class="nutrition-item">
                <text class="nutrition-label">讲解文档</text>
                <text class="nutrition-value">{{ weeklyReportData.protein }} 次</text>
                <view class="nutrition-bar">
                  <view class="nutrition-fill protein" :style="{ width: (weeklyReportData.protein / 840) * 100 + '%' }"></view>
                </view>
              </view>
              <view class="nutrition-item">
                <text class="nutrition-label">实操案例</text>
                <text class="nutrition-value">{{ weeklyReportData.fat }} 次</text>
                <view class="nutrition-bar">
                  <view class="nutrition-fill fat" :style="{ width: (weeklyReportData.fat / 420) * 100 + '%' }"></view>
                </view>
              </view>
              <view class="nutrition-item">
                <text class="nutrition-label">拓展阅读</text>
                <text class="nutrition-value">{{ weeklyReportData.carbs }} 次</text>
                <view class="nutrition-bar">
                  <view class="nutrition-fill carbs" :style="{ width: (weeklyReportData.carbs / 2100) * 100 + '%' }"></view>
                </view>
              </view>
            </view>
          </view>

          <view class="report-section">
            <text class="section-title">学习建议</text>
            <view class="suggestions-list">
              <view class="suggestion-item" v-for="(suggestion, index) in weeklyReportData.suggestions" :key="index">
                <text class="suggestion-icon">💡</text>
                <text class="suggestion-text">{{ suggestion }}</text>
              </view>
            </view>
          </view>
        </view>
      </scroll-view>
    </view>

    <!-- ===== 历史记录抽屉 ===== -->
    <view class="drawer-mask" v-if="showHistory" @click="closeHistory"></view>
    <view class="drawer-panel" :class="{ open: showHistory }">
      <view class="drawer-handle"></view>
      <text class="drawer-title">📋 历史记录</text>
      <scroll-view scroll-y class="drawer-scroll">
        <view class="drawer-item" v-for="(item, i) in historyList" :key="i" @click="loadRecord(item)">
          <view class="drawer-icon-wrap" @click.stop="previewImage(item.image, item.name)">
            <image v-if="item.image" class="drawer-thumb" :src="item.image" mode="aspectFill"></image>
            <text v-else class="drawer-emoji">😋</text>
          </view>
          <view class="drawer-info">
            <text class="drawer-name">{{ item.name }}</text>
            <text class="drawer-date">{{ item.date }}</text>
          </view>
          <view class="score-pill" :style="{ background: getScoreBg(item.score), color: getScoreColor(item.score) }">
                {{ item.score }}分
          </view>
        </view>
        <view class="drawer-empty" v-if="historyList.length === 0">
          <text>暂无历史记录</text>
        </view>
      </scroll-view>
    </view>

    <!-- ===== 历史记录抽屉 ===== -->
    <view class="drawer-mask" v-if="showHistory" @click="closeHistory"></view>
    <view class="drawer-panel" :class="{ open: showHistory }">
      <view class="drawer-handle"></view>
      <text class="drawer-title">📋 历史记录</text>
      <scroll-view scroll-y class="drawer-scroll">
        <view class="drawer-item" v-for="(item, i) in historyList" :key="i" @click="loadRecord(item)">
          <view class="drawer-icon-wrap" @click.stop="previewImage(item.image, item.name)">
            <image v-if="item.image" class="drawer-thumb" :src="item.image" mode="aspectFill"></image>
            <text v-else class="drawer-emoji">😋</text>
          </view>
          <view class="drawer-info">
            <text class="drawer-name">{{ item.name }}</text>
            <text class="drawer-date">{{ item.date }}</text>
          </view>
          <view class="score-pill" :style="{ background: getScoreBg(item.score), color: getScoreColor(item.score) }">
                {{ item.score }}分
          </view>
        </view>
        <view class="drawer-empty" v-if="historyList.length === 0">
          <text>暂无历史记录</text>
        </view>
      </scroll-view>
    </view>
    </template>

  </view>
</template>

<script>
import request, { uploadFile } from '../../utils/request.js';
import { createVoiceInputController } from '../../utils/voice-input.js';

export default {
  components: {
  },
  data() {
    return {
      currentMode: 'camera',
      calorieQueryMode: false,
      calorieQueryFood: '',
      calorieQueryResult: null,
      settingsMode: false,
      preferences: {
        goalType: '考试冲刺',
        dailyCalorieGoal: 90,
        dietType: '讲练结合',
        flavor: '短文档',
        allergies: '',
        avoidIngredients: '',
        lowOilSalt: true,
        noSugar: false,
        notifications: {
          healthReminder: true,
          weeklyReport: true,
          dailySummary: false
        }
      },
      manualInputMode: false,
      manualInputData: {
        foodName: '',
        description: '',
        ingredients: '',
        cookingMethod: '',
        weight: '',
        deliveryTime: '',
        packageMaterial: '',
        perishable: false
      },
      weeklyReportMode: false,
      weeklyReportData: {
        totalCalories: 560,
        averageCalories: 80,
        protein: 4,
        fat: 5,
        carbs: 6,
        days: [
          { day: '周一', calories: 80, protein: 4, fat: 5, carbs: 6 },
          { day: '周二', calories: 75, protein: 4, fat: 4, carbs: 5 },
          { day: '周三', calories: 90, protein: 5, fat: 5, carbs: 6 },
          { day: '周四', calories: 70, protein: 3, fat: 4, carbs: 5 },
          { day: '周五', calories: 95, protein: 5, fat: 6, carbs: 7 },
          { day: '周六', calories: 65, protein: 3, fat: 4, carbs: 5 },
          { day: '周日', calories: 90, protein: 5, fat: 5, carbs: 6 }
        ],
        suggestions: [
          '本周学习资源使用节奏稳定，继续保持',
          '讲解文档与练习题搭配较好，有助于巩固基础',
          '实操案例使用偏少，建议补充代码任务',
          '拓展阅读适中，适合当前学习阶段'
        ]
      },
      uploadedImage: '',
      analysisTip: '正在分析...',
      resultChatMsg: '',
      isVoiceRecording: false,
      isVoiceTranscribing: false,
      voiceInputController: null,
      showHistory: false,
      resultChatList: [],
      resultData: {
        name: '', score: 0, calories: 0,
        macros: { protein: '', fat: '', carbs: '' },
        dimensions: [], suggestions: [],
        analysisText: '',
        nutrition: []
      },
      historyList: [],
      loading: false,
      quickFuncs: [
        { icon: '/static/icons/manual-input.png', label: '输入知识点', bg: 'linear-gradient(135deg,#e6f7ff,#b3d9ff)' },
        { icon: '/static/icons/diet-report.png', label: '资源报告', bg: 'linear-gradient(135deg,#f0f9e8,#c6e8b3)' },
        { icon: '/static/icons/calorie-search.png', label: '题库生成', bg: 'linear-gradient(135deg,#fff0e0,#ffd9b3)' },
        { icon: '/static/icons/settings.png', label: '设置', bg: 'linear-gradient(135deg,#f0e6ff,#e0ccff)' }
      ],
      commonFoods: [
        { name: '搜索算法', calories: 80, protein: 3, fat: 5, carbs: 4 },
        { name: 'A*算法', calories: 90, protein: 4, fat: 5, carbs: 5 },
        { name: '神经网络', calories: 95, protein: 4, fat: 4, carbs: 6 },
        { name: '梯度下降', calories: 75, protein: 3, fat: 4, carbs: 5 },
        { name: '大模型智能体', calories: 100, protein: 5, fat: 5, carbs: 6 },
        { name: 'AI伦理安全', calories: 60, protein: 2, fat: 3, carbs: 4 }
      ]
    }
  },

  computed: {
    scoreColor() {
      const s = this.resultData.score;
      if (s >= 80) return '#389e0d';
      if (s >= 60) return '#d46b08';
      return '#cf1322';
    },
    scoreLevelBg() {
      const s = this.resultData.score;
      if (s >= 80) return 'rgba(56,158,13,0.12)';
      if (s >= 60) return 'rgba(212,107,8,0.12)';
      return 'rgba(207,19,34,0.12)';
    },
    scoreLevel() {
      const s = this.resultData.score;
      if (s >= 90) return '高度适配画像';
      if (s >= 75) return '适配当前学习目标';
      if (s >= 60) return '可继续优化';
      if (s >= 40) return '需补充上下文';
      return '不建议直接使用';
    },
    healthInsightMetrics() {
      return [
        { label: '事实校验', value: '通过', level: 'risk-low' },
        { label: '画像匹配', value: '较高', level: 'risk-low' },
        { label: '资源类型', value: '5类', level: 'risk-mid' },
        { label: '生成状态', value: '完成', level: 'risk-low' }
      ];
    }
  },

  onLoad() {
    this.loadHistoryFromServer();
    this.initVoiceInput();
  },

  onUnload() {
    if (this.voiceInputController) {
      this.voiceInputController.destroy();
    }
  },

  methods: {
    getResultKeywords() {
      const sections = [
        this.resultData.name,
        this.resultData.analysisText,
        ...(this.resultData.suggestions || []),
        ...(this.resultData.dimensions || []).map(item => `${item.name}${item.val || ''}`),
        ...(this.resultData.nutrition || []).map(item => `${item.name || ''}${item.level || ''}${item.warning || ''}`)
      ];
      return sections.filter(Boolean).join(' ');
    },

    hasKeyword(text, keywords) {
      return keywords.some(keyword => text.includes(keyword));
    },

    getOilRiskMetric() {
      const text = this.getResultKeywords();
      if (this.hasKeyword(text, ['油炸', '炸', '煎炸', '烧烤', '红油', '肥肉', '油脂含量较高', '脂肪偏高'])) {
        return { value: '偏高', level: 'risk-high' };
      }
      if (this.hasKeyword(text, ['清蒸', '水煮', '凉拌', '少油', '低脂'])) {
        return { value: '较低', level: 'risk-low' };
      }
      return { value: '适中', level: 'risk-mid' };
    },

    getSaltRiskMetric() {
      const text = this.getResultKeywords();
      if (this.hasKeyword(text, ['咸', '高盐', '重口', '酱油', '腌制', '卤', '钠', '盐分'])) {
        return { value: '偏咸', level: 'risk-high' };
      }
      if (this.hasKeyword(text, ['清淡', '少盐', '低盐'])) {
        return { value: '清淡', level: 'risk-low' };
      }
      return { value: '适中', level: 'risk-mid' };
    },

    getVegetableMetric() {
      const text = this.getResultKeywords();
      if (this.hasKeyword(text, ['沙拉', '蔬菜', '青菜', '西兰花', '番茄', '黄瓜', '生菜', '菠菜', '菌菇'])) {
        return { value: '充足', level: 'risk-low' };
      }
      if (this.hasKeyword(text, ['肉', '炸鸡', '汉堡', '盖饭', '炒饭', '面', '粉'])) {
        return { value: '偏少', level: 'risk-high' };
      }
      return { value: '一般', level: 'risk-mid' };
    },

    getBalanceMetric() {
      const score = Number(this.resultData.score) || 0;
      const text = this.getResultKeywords();
      if (score >= 80 || this.hasKeyword(text, ['适配', '搭配合理', '画像适配'])) {
        return { value: '较均衡', level: 'risk-low' };
      }
      if (score < 60 || this.hasKeyword(text, ['搭配清淡蔬果', '不均衡', '偏高', '过高'])) {
        return { value: '需搭配', level: 'risk-high' };
      }
      return { value: '基本均衡', level: 'risk-mid' };
    },

    initVoiceInput() {
      if (this.voiceInputController) return;

      this.voiceInputController = createVoiceInputController({
        service: 'tuantuan',
        onStateChange: ({ isRecording, isTranscribing }) => {
          this.isVoiceRecording = isRecording;
          this.isVoiceTranscribing = isTranscribing;
        },
        onTranscribed: (text) => {
          this.resultChatMsg = this.resultChatMsg.trim() ? `${this.resultChatMsg.trim()} ${text}` : text;
          uni.showToast({ title: '语音已转文字', icon: 'none' });
        },
        onError: (error) => {
          const title = (error?.message || '语音输入失败').slice(0, 20);
          uni.showToast({ title, icon: 'none' });
        }
      });
    },

    sanitizePlainText(text) {
      if (text === null || text === undefined) return '';
      let t = String(text);
      t = t.replace(/```[\s\S]*?```/g, '');
      t = t.replace(/`([^`]+)`/g, '$1');
      t = t.replace(/\*\*([^*]+)\*\*/g, '$1');
      t = t.replace(/\*([^*]+)\*/g, '$1');
      t = t.replace(/#{1,6}\s+/g, '');
      t = t.replace(/\[([^\]]+)\]\([^)]+\)/g, '$1');
      t = t.replace(/[*_`#~]/g, '');
      t = t.replace(/\n{3,}/g, '\n\n');
      return t.trim();
    },
    truncatePlainText(text, maxChars = 200) {
      const t = this.sanitizePlainText(text);
      if (!t) return '';
      if (t.length <= maxChars) return t;
      return t.slice(0, Math.max(0, maxChars - 1)) + '…';
    },
    formatHistoryDate(ts) {
      try {
        const d = new Date(ts || Date.now());
        const pad = (n) => String(n).padStart(2, '0');
        return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`;
      } catch {
        return '';
      }
    },
    async loadHistoryFromServer() {
      try {
        const res = await request.get('/api/user/my-uploads', {
          page: 1,
          page_size: 10,
          type: 'takeaway_analysis'
        });
        if (res && res.code === 200 && res.data && Array.isArray(res.data.takeaway_analysis)) {
          const mapped = res.data.takeaway_analysis.map((item) => ({
            ...item,
            ts: new Date(item.created_at || item.record_date || Date.now()).getTime(),
            date: this.formatHistoryDate(new Date(item.created_at || item.record_date || Date.now()).getTime()),
            macros: {
              protein: item.protein !== undefined ? `${item.protein}g` : '',
              fat: item.fat !== undefined ? `${item.fat}g` : '',
              carbs: item.carbs !== undefined ? `${item.carbs}g` : ''
            },
            analysisText: item.analysis_text || ''
          }));
          mapped.sort((a, b) => (b.ts || 0) - (a.ts || 0));
          this.historyList = mapped;
        }
      } catch (e) {
      }
    },
    async startAnalyzeFlow() {
      uni.chooseImage({
        count: 1,
        sourceType: ['camera', 'album'],
        success: async (res) => {
          this.uploadedImage = res.tempFilePaths[0];
          this.currentMode = 'analyzing';
          this.loading = true;
          try {
            const analysisResponse = await this.uploadAndAnalyzeImage(this.uploadedImage);
            if (analysisResponse) {
              const nowTs = Date.now();
              const nutrition = analysisResponse.nutrition || [];
              const caloriesItem = nutrition.find(item => item.key === 'calories');
              const proteinItem = nutrition.find(item => item.key === 'protein');
              const fatItem = nutrition.find(item => item.key === 'fat');
              const carbsItem = nutrition.find(item => item.key === 'carbs');

              this.resultData = {
                name: analysisResponse.name || '人工智能导论：搜索算法资源包',
                image: this.uploadedImage,
                score: analysisResponse.score || 75,
                calories: caloriesItem ? caloriesItem.value : 500,
                macros: {
                  protein: proteinItem ? `${proteinItem.value}${proteinItem.unit}` : '25g',
                  fat: fatItem ? `${fatItem.value}${fatItem.unit}` : '15g',
                  carbs: carbsItem ? `${carbsItem.value}${carbsItem.unit}` : '40g'
                },
                analysisText: `本次资源包与学生画像的适配度为${analysisResponse.score || 88}分。`,
                dimensions: analysisResponse.dimensions || [
                  { name: '课程讲解文档', score: 92, val: '已生成', color: '#52c41a' },
                  { name: '知识点思维导图', score: 88, val: '已生成', color: '#52c41a' },
                  { name: '分层练习题库', score: 85, val: '已生成', color: '#52c41a' },
                  { name: '实操案例材料', score: 80, val: '待完善', color: '#faad14' }
                ],
                suggestions: analysisResponse.suggestions || ['建议先学习图搜索与树搜索区别，再完成 A* 搜索代码实操', '对生成内容进行知识库引用校验，降低大模型幻觉风险'],
                nutrition: analysisResponse.nutrition || [
                  { name: '讲解文档', percent: 'Markdown', status: '完成' },
                  { name: '思维导图', percent: '章节结构', status: '完成' },
                  { name: '练习题', percent: '选择/简答/编程', status: '完成' },
                  { name: '视频脚本', percent: '分镜草案', status: '待生成' }
                ]
              };
              const record = {
                name: this.resultData.name,
                image: this.resultData.image,
                score: this.resultData.score,
                calories: this.resultData.calories,
                macros: this.resultData.macros,
                analysisText: this.resultData.analysisText,
                dimensions: this.resultData.dimensions,
                suggestions: this.resultData.suggestions,
                date: this.formatHistoryDate(nowTs),
                ts: nowTs
              };
              this.historyList = [record, ...(this.historyList || [])];
              this.historyList.sort((a, b) => (b.ts || 0) - (a.ts || 0));

              this.resultChatList = [
                {
                  type: 'agent',
                  text: this.truncatePlainText(
                    '生成完成：' + this.resultData.name + '的画像适配度为' + this.resultData.score + '分。' + (this.resultData.suggestions[0] || ''),
                    200
                  )
                }
              ];
              this.currentMode = 'result';
            } else {
              throw new Error('分析失败');
            }
          } catch (error) {
            uni.showToast({ title: '分析失败，请重试', icon: 'none' });
            this.currentMode = 'camera';
          } finally {
            this.loading = false;
          }
        }
      });
    },

    async uploadAndAnalyzeImage(filePath) {
      const data = await uploadFile('/api/takeaway/health/analyze/image', filePath, 'image_data', {
        service: 'tuantuan',
        timeout: 60000
      });
      if (data && data.code === 200 && data.data) {
        return data.data;
      }
      throw new Error(data?.message || '数据格式不正确');
    },

    async sendResultChat() {
      if (!this.resultChatMsg.trim()) return;
      const msg = this.resultChatMsg;
      this.resultChatList.push({ type: 'user', text: msg });
      this.resultChatMsg = '';
      try {
        const pendingIndex = this.resultChatList.length;
        this.resultChatList.push({ type: 'agent', text: '学习智能体正在回复，请稍候...' });

        const response = await request.post('/api/chat', { message: msg }, { service: 'takeout' });
        if (response && response.code === 0 && response.data && response.data.reply) {
          this.$set(this.resultChatList, pendingIndex, {
            type: 'agent',
            text: this.truncatePlainText(response.data.reply, 200)
          });
        } else {
          this.$set(this.resultChatList, pendingIndex, {
            type: 'agent',
            text: this.truncatePlainText('抱歉，我暂时无法回答这个问题', 200)
          });
        }
      } catch (error) {
        let errorMsg = '网络连接失败，请稍后重试';
        if (error.statusCode === 404) errorMsg = 'API地址错误，请检查后端服务';
        else if (error.statusCode === 500) errorMsg = '服务器内部错误，请稍后重试';
        const pendingIndex = Math.max(0, this.resultChatList.length - 1);
        if (this.resultChatList[pendingIndex] && this.resultChatList[pendingIndex].type === 'agent') {
          this.$set(this.resultChatList, pendingIndex, { type: 'agent', text: this.truncatePlainText(errorMsg, 200) });
        } else {
          this.resultChatList.push({ type: 'agent', text: this.truncatePlainText(errorMsg, 200) });
        }
      }
    },

    async toggleVoiceInput() {
      this.initVoiceInput();

      try {
        await this.voiceInputController.toggleRecording();
      } catch (error) {
        const title = (error?.message || '语音输入失败').slice(0, 20);
        uni.showToast({ title, icon: 'none' });
      }
    },

    resetToCamera() { this.currentMode = 'camera'; },
    openHistory() { this.showHistory = true; },
    closeHistory() { this.showHistory = false; },
    loadRecord(item) { this.resultData = item; this.currentMode = 'result'; this.showHistory = false; },
    previewImage(imageSrc, title) {
      if (!imageSrc) {
        uni.showToast({ title: '暂无图片', icon: 'none' });
        return;
      }
      uni.navigateTo({
        url: '/pages/image-viewer/image-viewer?src=' + encodeURIComponent(imageSrc) + '&title=' + encodeURIComponent(title || '订单图片')
      });
    },

    getScoreColor(s) {
      if (s >= 80) return '#389e0d';
      if (s >= 60) return '#d46b08';
      return '#cf1322';
    },
    getScoreBg(s) {
      if (s >= 80) return 'rgba(56,158,13,0.1)';
      if (s >= 60) return 'rgba(212,107,8,0.1)';
      return 'rgba(207,19,34,0.1)';
    },
    getDimensionColor(score) {
      if (score >= 80) return '#389e0d';
      if (score >= 60) return '#d46b08';
      return '#cf1322';
    },

    queryCalories() {
      if (!this.calorieQueryFood.trim()) {
        uni.showToast({ title: '请输入知识点名称', icon: 'none' });
        return;
      }

      const food = this.commonFoods.find(f => f.name.includes(this.calorieQueryFood));
      if (food) {
        this.calorieQueryResult = food;
      } else {
        this.calorieQueryResult = {
          name: this.calorieQueryFood,
          calories: 100,
          protein: 5.0,
          fat: 3.0,
          carbs: 15.0
        };
      }
    },

    selectCommonFood(food) {
      this.calorieQueryFood = food.name;
      this.calorieQueryResult = food;
    },

    handleQuickFunc(item) {
      if (item.label === '知识点查询') {
        this.calorieQueryMode = true;
      } else if (item.label === '输入知识点') {
        this.manualInputMode = true;
      } else if (item.label === '资源报告') {
        this.weeklyReportMode = true;
      } else if (item.label === '设置') {
        this.settingsMode = true;
      }
    },

    resetManualInput() {
      this.manualInputData = {
        foodName: '',
        description: '',
        ingredients: '',
        cookingMethod: '',
        weight: '',
        deliveryTime: '',
        packageMaterial: '',
        perishable: false
      };
    },

    calculateHealthScore(data) {
      let score = 0;
      const weights = {
        nutritionBalance: 30,
        ingredientQuality: 25,
        cookingMethod: 25,
        deliveryImpact: 20
      };

      let nutritionScore = 0;
      if (data.calories && data.protein && data.fat && data.carbs) {
        const calories = parseFloat(data.calories);
        const protein = parseFloat(data.protein);
        const fat = parseFloat(data.fat);
        const carbs = parseFloat(data.carbs);

        if (calories > 0) {
          const proteinRatio = (protein * 4) / calories;
          const fatRatio = (fat * 9) / calories;
          const carbsRatio = (carbs * 4) / calories;

          if (proteinRatio >= 0.15 && proteinRatio <= 0.3) nutritionScore += 30;
          else if (proteinRatio >= 0.1 && proteinRatio <= 0.35) nutritionScore += 20;
          else nutritionScore += 10;

          if (fatRatio >= 0.2 && fatRatio <= 0.35) nutritionScore += 30;
          else if (fatRatio >= 0.15 && fatRatio <= 0.4) nutritionScore += 20;
          else nutritionScore += 10;

          if (carbsRatio >= 0.4 && carbsRatio <= 0.6) nutritionScore += 40;
          else if (carbsRatio >= 0.3 && carbsRatio <= 0.7) nutritionScore += 30;
          else nutritionScore += 20;
        }
      }

      let cookingScore = 100;
      const healthyMethods = ['讲解文档', '思维导图'];
      const mediumMethods = ['练习题库', '视频脚本'];
      const unhealthyMethods = ['代码案例', '拓展阅读'];

      if (healthyMethods.includes(data.cookingMethod)) cookingScore = 90;
      else if (mediumMethods.includes(data.cookingMethod)) cookingScore = 65;
      else if (unhealthyMethods.includes(data.cookingMethod)) cookingScore = 40;

      let deliveryScore = 100;
      if (data.deliveryTime && parseInt(data.deliveryTime) > 0) {
        const time = parseInt(data.deliveryTime);
        const isPerishable = data.perishable;
        const packageSafe = ['知识库引用', '来源标注', '教师审核', '题目回测', '同伴互评'].includes(data.packageMaterial);

        if (isPerishable && time > 30) deliveryScore = Math.max(50, 100 - (time - 30) * 2);
        else if (!packageSafe && time > 45) deliveryScore = Math.max(70, 100 - (time - 45));
      }

      score = Math.round(
        (nutritionScore * weights.nutritionBalance +
         80 * weights.ingredientQuality +
         cookingScore * weights.cookingMethod +
         deliveryScore * weights.deliveryImpact) / 100
      );

      return Math.min(100, Math.max(0, score));
    },

    generateSuggestions(data, score) {
      const suggestions = [];

      if (data.cookingMethod === '代码案例' || data.cookingMethod === '拓展阅读') {
        suggestions.push('该资源对基础要求较高，建议先补充讲解文档或思维导图');
      }

      if (data.perishable && data.deliveryTime && parseInt(data.deliveryTime) > 30) {
        suggestions.push('该知识点属于易错内容，建议缩短生成链路并加强题目回测');
      }

      if (data.packageMaterial === '教师审核') {
        suggestions.push('该资源已标记为教师审核优先，建议在发布前保留来源依据');
      }

      if (score < 60) {
        suggestions.push('该资源适配度较低，建议补充课程上下文和学生画像信息后重新生成');
      } else if (score >= 80) {
        suggestions.push('该资源画像适配度较高，可以加入学习路径继续使用');
      }

      return suggestions.length > 0 ? suggestions : ['建议结合学生画像继续优化资源推送'];
    },

    saveManualInput() {
      if (!this.manualInputData.foodName.trim()) {
        uni.showToast({ title: '请输入知识点名称', icon: 'none' });
        return;
      }

      const nowTs = Date.now();
      const savedData = {
        ...this.manualInputData,
        savedAt: nowTs,
        date: this.formatHistoryDate(nowTs)
      };

      let savedList = uni.getStorageSync('manualFoodList') || [];
      savedList.push(savedData);
      uni.setStorageSync('manualFoodList', savedList);

      uni.showToast({ title: '保存成功', icon: 'success' });
      this.resetManualInput();
      this.manualInputMode = false;
    },

    savePreferences() {
      uni.showToast({ title: '偏好已保存', icon: 'success' });
      uni.setStorageSync('userPreferences', this.preferences);
    }
  }
}
</script>

<style scoped>
/* ===== 全局 ===== */
.page-container {
  min-height: 100vh;
  background: #f0fdf4;
  padding-top: calc(44px + constant(safe-area-inset-top));
  padding-top: calc(44px + env(safe-area-inset-top));
}

.section-mode {
  display: flex;
  flex-direction: column;
}

/* ===== HERO BANNER ===== */
.hero-banner {
  background: #fff;
  margin: 24rpx 24rpx 0;
  border-radius: 28rpx;
  padding: 28rpx 28rpx;
  display: flex;
  align-items: center;
  gap: 24rpx;
  box-shadow: 0 4rpx 20rpx rgba(0,0,0,0.05);
  border: 1rpx solid #e8f5ee;
}

.hero-left { flex-shrink: 0; }

.hero-avatar {
  width: 88rpx;
  height: 88rpx;
  border-radius: 50%;
  border: 3rpx solid #d1fae5;
  box-shadow: 0 4rpx 12rpx rgba(46,169,111,0.15);
}

.hero-right {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}

.hero-badge {
  display: inline-flex;
  align-self: flex-start;
  background: #ecfdf5;
  color: #2ea96f;
  font-size: 20rpx;
  padding: 6rpx 16rpx;
  border-radius: 20rpx;
  font-weight: bold;
  border: 1rpx solid #a7f3d0;
}

.hero-name {
  font-size: 30rpx;
  font-weight: 800;
  color: #1a2c20;
  display: block;
}

.hero-tagline {
  font-size: 22rpx;
  color: #888;
  display: block;
  line-height: 1.5;
}

/* ===== 拍照区域 ===== */
.shoot-section {
  padding: 20rpx 24rpx 0;
}

.shoot-card {
  background: #fff;
  border-radius: 28rpx;
  padding: 48rpx 0 36rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  box-shadow: 0 4rpx 20rpx rgba(0,0,0,0.05);
  border: 2rpx dashed #a7f3d0;
  transition: transform 0.15s;
}

.shoot-card:active { transform: scale(0.98); }

.camera-icon-wrap {
  width: 160rpx;
  height: 160rpx;
  background: #f0fdf4;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 28rpx;
  border: 3rpx solid #d1fae5;
  box-shadow: 0 8rpx 24rpx rgba(46,169,111,0.12);
}

.camera-svg {
  width: 80rpx;
  height: 80rpx;
}

.camera-fallback {
  font-size: 48rpx;
  color: #2ea96f;
  font-weight: 700;
}

.shoot-label {
  font-size: 30rpx;
  font-weight: 800;
  color: #1a2c20;
  margin-bottom: 8rpx;
}

.shoot-sub {
  font-size: 22rpx;
  color: #aaa;
  margin-bottom: 24rpx;
}

.shoot-action-row {
  margin-top: 4rpx;
}

.shoot-action-btn {
  background: linear-gradient(135deg, #2ea96f, #4CCF87);
  border-radius: 40rpx;
  padding: 18rpx 60rpx;
  box-shadow: 0 6rpx 20rpx rgba(46,169,111,0.3);
}

.shoot-action-text {
  font-size: 28rpx;
  color: #fff;
  font-weight: bold;
}

/* ===== 功能卡片组 ===== */
.cards-group {
  padding: 24rpx 30rpx 40rpx;
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.func-card {
  background: #fff;
  border-radius: 24rpx;
  padding: 26rpx;
  box-shadow: 0 4rpx 16rpx rgba(0,0,0,0.04);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
  padding-bottom: 16rpx;
  border-bottom: 1rpx solid #f5f5f5;
}

.card-title-box {
  display: flex;
  align-items: center;
  gap: 12rpx;
}

.card-dot {
  width: 14rpx;
  height: 14rpx;
  border-radius: 50%;
}
.orange-dot { background: #fa8c16; }
.blue-dot   { background: #1890ff; }

.card-title {
  font-size: 28rpx;
  font-weight: 800;
  color: #1a2c20;
}

.card-link { font-size: 24rpx; color: #aaa; }

/* 历史列表 */
.history-empty {
  padding: 20rpx 0;
  text-align: center;
}
.empty-hint { font-size: 24rpx; color: #ccc; }

.history-item {
  display: flex;
  align-items: center;
  gap: 16rpx;
  padding: 16rpx;
  background: #fafafa;
  border-radius: 16rpx;
  margin-bottom: 12rpx;
}
.history-item:last-child { margin-bottom: 0; }

.history-icon-box {
  width: 60rpx;
  height: 60rpx;
  background: #fff7e6;
  border-radius: 14rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}
.history-icon { font-size: 32rpx; }
.history-thumb {
  width: 60rpx;
  height: 60rpx;
  border-radius: 14rpx;
}

.history-info { flex: 1; }
.history-name { font-size: 26rpx; color: #333; font-weight: 600; display: block; }
.history-date { font-size: 20rpx; color: #bbb; display: block; margin-top: 4rpx; }

.score-pill {
  font-size: 22rpx;
  font-weight: bold;
  padding: 6rpx 18rpx;
  border-radius: 20rpx;
}

/* 网格 */
.grid-row {
  display: flex;
  justify-content: space-around;
}

.grid-cell {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12rpx;
}

.grid-icon-box {
  width: 88rpx;
  height: 88rpx;
  border-radius: 24rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 6rpx 16rpx rgba(0,0,0,0.08);
  transition: transform 0.15s ease, opacity 0.15s ease;
}
.grid-emoji { font-size: 38rpx; }
.grid-icon { width: 60rpx; height: 60rpx; transition: transform 0.15s ease, opacity 0.15s ease; }
.grid-label { font-size: 22rpx; color: #666; }
.grid-cell:active .grid-icon-box {
  transform: scale(0.9);
  opacity: 0.75;
}

/* ===== 分析中 ===== */
.center-mode {
  min-height: 100vh;
  align-items: center;
  justify-content: center;
}

.analyzing-card {
  background: #fff;
  border-radius: 40rpx;
  padding: 60rpx 50rpx;
  margin: 40rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  box-shadow: 0 12rpx 48rpx rgba(0,0,0,0.08);
}

.analyzing-ring {
  position: relative;
  width: 200rpx;
  height: 200rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 40rpx;
}

.ring {
  position: absolute;
  border-radius: 50%;
  border: 4rpx solid rgba(46,169,111,0.2);
  animation: spin-ring 3s linear infinite;
}
.r1 { width: 200rpx; height: 200rpx; border-top-color: #4CCF87; }
.r2 { width: 160rpx; height: 160rpx; border-right-color: #2ea96f; animation-duration: 2s; animation-direction: reverse; }
.r3 { width: 120rpx; height: 120rpx; border-bottom-color: #95de64; animation-duration: 1.5s; }

.analyzing-emoji {
  font-size: 72rpx;
  animation: bounce 1s infinite alternate;
  position: relative;
  z-index: 2;
}

.analyzing-title {
  font-size: 34rpx;
  font-weight: 800;
  color: #1d6f3a;
  margin-bottom: 12rpx;
}

.analyzing-sub {
  font-size: 24rpx;
  color: #999;
  margin-bottom: 32rpx;
}

.analyzing-dots { display: flex; gap: 16rpx; }
.dot {
  width: 16rpx; height: 16rpx; border-radius: 50%; background: #4CCF87;
  animation: dot-flash 1.2s infinite;
}
.dot2 { animation-delay: 0.2s; }
.dot3 { animation-delay: 0.4s; }

/* ===== 结果 ===== */
.result-scroll {
  height: 100vh;
}

.result-hero {
  position: relative;
  background: linear-gradient(145deg, #1d6f3a 0%, #2ea96f 70%, #4CCF87 100%);
  padding: 40rpx 30rpx 0;
  border-radius: 0 0 48rpx 48rpx;
  box-shadow: 0 12rpx 32rpx rgba(46,169,111,0.2);
  margin-bottom: 24rpx;
}

.result-hero-bg {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: radial-gradient(circle at 80% 20%, rgba(255,255,255,0.12) 0%, transparent 60%);
  pointer-events: none;
  border-radius: 0 0 48rpx 48rpx;
}

.result-hero-content {
  display: flex;
  gap: 28rpx;
  align-items: flex-start;
  margin-bottom: 28rpx;
  position: relative;
  z-index: 1;
}

.result-food-img {
  width: 200rpx;
  height: 200rpx;
  border-radius: 24rpx;
  border: 4rpx solid rgba(255,255,255,0.5);
  flex-shrink: 0;
  box-shadow: 0 8rpx 24rpx rgba(0,0,0,0.2);
}

.result-meta {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

.result-food-name {
  font-size: 34rpx;
  font-weight: 800;
  color: #fff;
  display: block;
  line-height: 1.4;
}

.result-score-ring {
  display: inline-flex;
  align-items: baseline;
  background: rgba(255,255,255,0.95);
  border: 4rpx solid;
  border-radius: 20rpx;
  padding: 8rpx 20rpx;
  align-self: flex-start;
  gap: 4rpx;
  box-shadow: 0 4rpx 12rpx rgba(0,0,0,0.1);
}

.result-score-num {
  font-size: 48rpx;
  font-weight: 900;
  line-height: 1;
}

.result-score-unit {
  font-size: 22rpx;
  font-weight: bold;
}

.result-level-pill {
  display: inline-flex;
  align-items: center;
  background: rgba(255,255,255,0.9);
  border-radius: 20rpx;
  padding: 8rpx 20rpx;
  align-self: flex-start;
}

.result-level-text {
  font-size: 24rpx;
  font-weight: bold;
  color: #333;
}

.health-insight-strip {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12rpx;
  padding-bottom: 30rpx;
}

.health-insight-item {
  min-width: 0;
  background: rgba(255,255,255,0.16);
  border: 1rpx solid rgba(255,255,255,0.24);
  border-radius: 18rpx;
  padding: 14rpx 8rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8rpx;
}

.health-insight-label {
  font-size: 20rpx;
  color: rgba(255,255,255,0.78);
  line-height: 1.2;
}

.health-insight-val {
  font-size: 24rpx;
  color: #fff;
  font-weight: 800;
  line-height: 1.2;
}

.health-insight-val.risk-low { color: #eafff2; }
.health-insight-val.risk-mid { color: #fff7d6; }
.health-insight-val.risk-high { color: #ffe1d6; }

/* 结果卡片 */
.result-section {
  background: #fff;
  margin: 0 24rpx 20rpx;
  border-radius: 24rpx;
  padding: 28rpx;
  box-shadow: 0 4rpx 16rpx rgba(0,0,0,0.04);
}

.section-head {
  display: flex;
  align-items: center;
  gap: 14rpx;
  margin-bottom: 24rpx;
  padding-bottom: 16rpx;
  border-bottom: 1rpx solid #f5f5f5;
}

.section-accent {
  width: 8rpx;
  height: 36rpx;
  background: linear-gradient(180deg, #2ea96f, #4CCF87);
  border-radius: 8rpx;
}

.section-title {
  font-size: 30rpx;
  font-weight: 800;
  color: #1a2c20;
}

.section-avatar {
  width: 52rpx;
  height: 52rpx;
  border-radius: 50%;
  border: 2rpx solid #e8f5e9;
}

/* 多维评估 */
.dim-list { display: flex; flex-direction: column; gap: 20rpx; }

.dim-item {}

.dim-top {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10rpx;
}

.dim-name { font-size: 26rpx; color: #555; }
.dim-val  { font-size: 26rpx; font-weight: bold; }

.dim-bar-track {
  height: 12rpx;
  background: #f0f0f0;
  border-radius: 12rpx;
  overflow: hidden;
}

.dim-bar-fill {
  height: 100%;
  border-radius: 12rpx;
  transition: width 0.8s ease;
}

/* AI 对话 */
.chat-section {}

.chat-area {
  min-height: 160rpx;
  max-height: 360rpx;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 16rpx;
  margin-bottom: 20rpx;
}

.chat-row {
  display: flex;
}

.row-agent { justify-content: flex-start; }
.row-user  { justify-content: flex-end; }

.bubble {
  max-width: 80%;
  padding: 16rpx 22rpx;
  border-radius: 24rpx;
  font-size: 26rpx;
  line-height: 1.6;
}

.bubble-agent {
  background: #f0fdf4;
  color: #1a2c20;
  border-top-left-radius: 6rpx;
  border: 1rpx solid #d1fae5;
}

.bubble-user {
  background: linear-gradient(135deg, #2ea96f, #4CCF87);
  color: #fff;
  border-top-right-radius: 6rpx;
}

.bubble-text { display: block; }

.chat-input-row {
  display: flex;
  gap: 14rpx;
  align-items: center;
  background: #f5f9f5;
  border-radius: 40rpx;
  padding: 10rpx 10rpx 10rpx 20rpx;
}

.chat-input {
  flex: 1;
  height: 60rpx;
  font-size: 26rpx;
  color: #333;
}

.voice-btn {
  min-width: 112rpx;
  height: 64rpx;
  padding: 0 18rpx;
  background: #e8f5ee;
  border-radius: 32rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  border: 1rpx solid #b7ebc6;
}

.voice-btn.active {
  background: linear-gradient(135deg, #2ea96f, #4CCF87);
  border-color: transparent;
}

.voice-btn-text {
  font-size: 22rpx;
  color: #2ea96f;
  font-weight: 600;
}

.voice-btn.active .voice-btn-text {
  color: #fff;
}

.send-btn {
  width: 64rpx;
  height: 64rpx;
  background: linear-gradient(135deg, #2ea96f, #4CCF87);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4rpx 12rpx rgba(46,169,111,0.3);
  flex-shrink: 0;
}

.send-arrow { font-size: 26rpx; color: #fff; }

/* 营养分析 */
.nutrition-list { display: flex; flex-direction: column; gap: 16rpx; }

.nutrition-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16rpx 0;
  border-bottom: 1rpx solid #f0f0f0;
}

.nutrition-item:last-child { border-bottom: none; }

.nutrition-label { font-size: 26rpx; color: #555; }

.nutrition-right {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.nutrition-value { font-size: 26rpx; font-weight: bold; color: #333; }

.nutrition-status {
  font-size: 22rpx;
  padding: 4rpx 12rpx;
  border-radius: 12rpx;
  font-weight: bold;
}

.nutrition-status.low { background: #fff7e6; color: #fa8c16; }

.nutrition-status.ok { background: #f6ffed; color: #52c41a; }

.nutrition-status.high { background: #fff1f0; color: #ff4d4f; }

/* 营养建议 */
.suggestions-list { display: flex; flex-direction: column; gap: 16rpx; }

.sug-item {
  display: flex;
  gap: 16rpx;
  align-items: flex-start;
  background: #f9fdf9;
  border-radius: 16rpx;
  padding: 16rpx 20rpx;
}

.sug-icon { font-size: 28rpx; flex-shrink: 0; }
.sug-text { font-size: 26rpx; color: #444; line-height: 1.6; flex: 1; }

/* 底部按钮 */
.bottom-actions {
  padding: 10rpx 30rpx 60rpx;
}

.retake-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 14rpx;
  background: linear-gradient(135deg, #1d6f3a, #2ea96f);
  border-radius: 40rpx;
  padding: 28rpx;
  box-shadow: 0 8rpx 24rpx rgba(46,169,111,0.35);
}

.retake-icon { font-size: 36rpx; }
.retake-text { font-size: 30rpx; color: #fff; font-weight: bold; }

/* ===== 弹窗样式 ===== */
.modal-mask {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.45);
  z-index: 2000;
  animation: fade-in 0.3s ease;
}

.modal-panel {
  position: fixed;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 80vh;
  background: #fff;
  z-index: 2001;
  border-radius: 40rpx 40rpx 0 0;
  transform: translateY(100%);
  transition: transform 0.32s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  flex-direction: column;
  box-shadow: 0 -8rpx 32rpx rgba(0,0,0,0.1);
}

.modal-panel.open {
  transform: translateY(0);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24rpx 30rpx;
  background: #fff;
  box-shadow: 0 2rpx 10rpx rgba(0,0,0,0.05);
  border-bottom: 1rpx solid #f0f0f0;
}

.modal-header-left, .modal-header-right {
  width: 80rpx;
}

.modal-back-icon {
  font-size: 36rpx;
  color: #333;
  font-weight: bold;
}

.modal-header-title {
  font-size: 32rpx;
  font-weight: 800;
  color: #1a2c20;
}

.modal-content {
  flex: 1;
  padding: 20rpx;
  overflow-y: auto;
  box-sizing: border-box;
  width: 100%;
}

@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* ===== 历史抽屉 ===== */
.drawer-mask {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.45);
  z-index: 2000;
}

.drawer-panel {
  position: fixed;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 72vh;
  background: #fff;
  z-index: 2001;
  border-radius: 40rpx 40rpx 0 0;
  transform: translateY(100%);
  transition: transform 0.32s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  flex-direction: column;
}

.open { transform: translateY(0); }

.drawer-handle {
  width: 72rpx;
  height: 8rpx;
  background: #e0e0e0;
  border-radius: 8rpx;
  margin: 24rpx auto 4rpx;
}

.drawer-title {
  font-size: 32rpx;
  font-weight: 800;
  color: #1a2c20;
  text-align: center;
  padding: 16rpx 0 20rpx;
}

.drawer-scroll { flex: 1; padding: 0 30rpx 30rpx; }

.drawer-item {
  display: flex;
  align-items: center;
  gap: 20rpx;
  padding: 24rpx 0;
  border-bottom: 1rpx solid #f5f5f5;
}

.drawer-icon-wrap {
  width: 72rpx;
  height: 72rpx;
  background: #fff8e8;
  border-radius: 18rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.drawer-thumb {
  width: 72rpx;
  height: 72rpx;
  border-radius: 18rpx;
}

.drawer-emoji { font-size: 36rpx; }

.drawer-info { flex: 1; }
.drawer-name { font-size: 28rpx; font-weight: 600; color: #222; display: block; margin-bottom: 6rpx; }
.drawer-date { font-size: 22rpx; color: #bbb; display: block; }

.drawer-empty {
  text-align: center;
  padding: 60rpx;
  color: #ccc;
  font-size: 26rpx;
}

/* ===== 热量查询样式 ===== */
.calorie-query-content {
  padding: 30rpx;
}

.query-input-section {
  margin-bottom: 40rpx;
}

.input-wrapper {
  display: flex;
  gap: 16rpx;
  align-items: center;
}

.query-input {
  flex: 1;
  height: 80rpx;
  background: #f5f7f5;
  border-radius: 40rpx;
  padding: 0 30rpx;
  font-size: 28rpx;
  color: #333;
}

.query-btn {
  padding: 0 40rpx;
  height: 80rpx;
  background: linear-gradient(135deg, #ffd591, #ffa940);
  border-radius: 40rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4rpx 12rpx rgba(255,169,64,0.3);
}

.query-btn-text {
  font-size: 28rpx;
  font-weight: 600;
  color: #fff;
}

.food-info {
  background: #fff;
  border-radius: 24rpx;
  padding: 30rpx;
  box-shadow: 0 4rpx 16rpx rgba(0,0,0,0.04);
  margin-bottom: 24rpx;
  text-align: center;
}

.food-name {
  font-size: 32rpx;
  font-weight: 800;
  color: #1a2c20;
  margin-bottom: 16rpx;
  display: block;
}

.calorie-value {
  font-size: 48rpx;
  font-weight: 900;
  color: #ff7a45;
  display: block;
}

.nutrition-details {
  background: #fff;
  border-radius: 24rpx;
  padding: 30rpx;
  box-shadow: 0 4rpx 16rpx rgba(0,0,0,0.04);
}

.nutrition-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16rpx 0;
  border-bottom: 1rpx solid #f5f5f5;
}

.nutrition-item:last-child {
  border-bottom: none;
}

.nutrition-label {
  font-size: 26rpx;
  color: #555;
}

.nutrition-value {
  font-size: 26rpx;
  font-weight: 600;
  color: #1a2c20;
}

.common-foods {
  margin-top: 40rpx;
}

.food-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20rpx;
}

.food-item {
  background: #fff;
  border-radius: 20rpx;
  padding: 24rpx;
  box-shadow: 0 4rpx 12rpx rgba(0,0,0,0.04);
  text-align: center;
  transition: transform 0.2s;
}

.food-item:active {
  transform: scale(0.98);
}

.food-item-name {
  font-size: 26rpx;
  font-weight: 600;
  color: #1a2c20;
  margin-bottom: 8rpx;
  display: block;
}

.food-item-calorie {
  font-size: 24rpx;
  color: #ff7a45;
  display: block;
}

/* ===== 设置样式 ===== */
.settings-content {
  padding: 30rpx;
}

.settings-section {
  margin-bottom: 40rpx;
}

.settings-list {
  background: #fff;
  border-radius: 24rpx;
  box-shadow: 0 4rpx 16rpx rgba(0,0,0,0.04);
  overflow: hidden;
}

.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24rpx 30rpx;
  border-bottom: 1rpx solid #f5f5f5;
}

.setting-item:last-child {
  border-bottom: none;
}

.setting-label {
  font-size: 28rpx;
  color: #1a2c20;
}

.switch-wrapper {
  display: flex;
  align-items: center;
}

.settings-actions {
  margin-top: 60rpx;
}

.save-btn {
  background: linear-gradient(135deg, #d3adf7, #9254de);
  border-radius: 40rpx;
  padding: 24rpx;
  text-align: center;
  box-shadow: 0 6rpx 20rpx rgba(146,84,222,0.3);
}

.save-btn-text {
  font-size: 30rpx;
  font-weight: 600;
  color: #fff;
}

/* ===== 手动输入样式 ===== */
.manual-input-content {
  padding: 0;
  width: 100%;
  box-sizing: border-box;
}

.input-section {
  margin-bottom: 30rpx;
  width: 100%;
  box-sizing: border-box;
}

.input-item {
  margin-bottom: 16rpx;
  width: 100%;
  box-sizing: border-box;
}

.input-item:last-child {
  margin-bottom: 0;
}

.input-label {
  display: block;
  font-size: 24rpx;
  color: #555;
  margin-bottom: 10rpx;
  font-weight: 600;
}

.manual-input {
  width: 100%;
  height: 72rpx;
  background: #f5f7f5;
  border-radius: 14rpx;
  padding: 0 20rpx;
  font-size: 26rpx;
  color: #333;
  border: 1rpx solid #e8e8e8;
  box-sizing: border-box;
}

.input-actions {
  display: flex;
  gap: 20rpx;
}

.reset-btn {
  flex: 1;
  background: #f5f7f5;
  border-radius: 40rpx;
  padding: 24rpx;
  text-align: center;
  border: 1rpx solid #e8e8e8;
}

.reset-btn-text {
  font-size: 28rpx;
  font-weight: 600;
  color: #666;
}

.submit-btn {
  flex: 1;
  background: linear-gradient(135deg, #bae7ff, #69c0ff);
  border-radius: 40rpx;
  padding: 24rpx;
  text-align: center;
  box-shadow: 0 6rpx 20rpx rgba(105,192,255,0.3);
}

.submit-btn-text {
  font-size: 28rpx;
  font-weight: 600;
  color: #fff;
}

/* ===== 饮食周报样式 ===== */
.weekly-report-content {
  padding: 30rpx;
}

.report-summary {
  display: flex;
  gap: 20rpx;
  margin-bottom: 40rpx;
}

.summary-card {
  flex: 1;
  background: #fff;
  border-radius: 24rpx;
  padding: 30rpx;
  text-align: center;
  box-shadow: 0 4rpx 16rpx rgba(0,0,0,0.04);
}

.summary-title {
  font-size: 26rpx;
  color: #555;
  margin-bottom: 12rpx;
  display: block;
}

.summary-value {
  font-size: 36rpx;
  font-weight: 800;
  color: #1a2c20;
  display: block;
}

.report-section {
  margin-bottom: 40rpx;
}

.calorie-chart {
  background: #fff;
  border-radius: 24rpx;
  padding: 30rpx;
  box-shadow: 0 4rpx 16rpx rgba(0,0,0,0.04);
}

.chart-container {
  display: flex;
  justify-content: space-around;
  align-items: flex-end;
  height: 300rpx;
  margin-top: 20rpx;
}

.chart-bar {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
}

.bar-wrapper {
  width: 40rpx;
  height: 200rpx;
  background: #f5f7f5;
  border-radius: 20rpx;
  overflow: hidden;
  margin-bottom: 12rpx;
  display: flex;
  align-items: flex-end;
}

.bar {
  width: 100%;
  background: linear-gradient(180deg, #b7eb8f, #73d13d);
  border-radius: 20rpx 20rpx 0 0;
  transition: height 0.5s ease;
}

.bar-label {
  font-size: 22rpx;
  color: #555;
  margin-bottom: 4rpx;
}

.bar-value {
  font-size: 20rpx;
  color: #888;
}

.nutrition-chart {
  background: #fff;
  border-radius: 24rpx;
  padding: 30rpx;
  box-shadow: 0 4rpx 16rpx rgba(0,0,0,0.04);
}

.nutrition-bar {
  width: 100%;
  height: 12rpx;
  background: #f5f7f5;
  border-radius: 6rpx;
  overflow: hidden;
  margin-top: 8rpx;
}

.nutrition-fill {
  height: 100%;
  border-radius: 6rpx;
  transition: width 0.5s ease;
}

.nutrition-fill.protein {
  background: linear-gradient(90deg, #bae7ff, #69c0ff);
}

.nutrition-fill.fat {
  background: linear-gradient(90deg, #ffd591, #ffa940);
}

.nutrition-fill.carbs {
  background: linear-gradient(90deg, #ffadd2, #ff85c0);
}

.suggestions-list {
  background: #fff;
  border-radius: 24rpx;
  padding: 30rpx;
  box-shadow: 0 4rpx 16rpx rgba(0,0,0,0.04);
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.suggestion-item {
  display: flex;
  gap: 16rpx;
  align-items: flex-start;
  padding: 16rpx;
  background: #f9fdf9;
  border-radius: 16rpx;
}

.suggestion-icon {
  font-size: 28rpx;
  flex-shrink: 0;
}

.suggestion-text {
  font-size: 26rpx;
  color: #444;
  line-height: 1.6;
  flex: 1;
}

/* ===== 手动输入新增样式 ===== */
.input-group {
  margin-bottom: 20rpx;
  background: #fff;
  border-radius: 16rpx;
  padding: 20rpx;
  box-shadow: 0 4rpx 16rpx rgba(0,0,0,0.04);
  box-sizing: border-box;
  width: 100%;
}

.group-title {
  font-size: 24rpx;
  font-weight: 700;
  color: #1a2c20;
  margin-bottom: 12rpx;
  display: block;
}

.input-row {
  display: flex;
  gap: 12rpx;
  width: 100%;
  box-sizing: border-box;
}

.input-item.half {
  flex: 1;
  min-width: 0;
  box-sizing: border-box;
}

.manual-textarea {
  width: 100%;
  height: 90rpx;
  background: #f5f7f5;
  border-radius: 14rpx;
  padding: 14rpx 18rpx;
  font-size: 24rpx;
  color: #333;
  border: 1rpx solid #e8e8e8;
  box-sizing: border-box;
}

.selector-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10rpx;
}

.selector-tag {
  padding: 10rpx 20rpx;
  background: #f5f7f5;
  border-radius: 28rpx;
  font-size: 22rpx;
  color: #666;
  border: 2rpx solid transparent;
  transition: all 0.3s;
}

.selector-tag.active {
  background: #e8f5ee;
  color: #2ea96f;
  border-color: #2ea96f;
}

/* ===== 设置页面新增样式 ===== */
.setting-input {
  width: 100%;
  height: 80rpx;
  background: #f5f7f5;
  border-radius: 20rpx;
  padding: 0 30rpx;
  font-size: 28rpx;
  color: #333;
  border: 1rpx solid #e8e8e8;
}

.small-switch {
  transform: scale(0.75);
}

/* ===== 动画 ===== */
@keyframes pulse {
  0%   { opacity: 0.5; transform: scale(1); }
  100% { opacity: 0; transform: scale(1.5); }
}

@keyframes spin-ring {
  from { transform: rotate(0deg); }
  to   { transform: rotate(360deg); }
}

@keyframes bounce {
  from { transform: translateY(0); }
  to   { transform: translateY(-16rpx); }
}

@keyframes dot-flash {
  0%, 80%, 100% { opacity: 0.2; transform: scale(0.8); }
  40%           { opacity: 1; transform: scale(1); }
}
</style>
