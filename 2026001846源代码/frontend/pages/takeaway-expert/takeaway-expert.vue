﻿﻿﻿<template>
  <view class="page-container">
    <!-- 模式：拍照主界面 / 分析中 / 结果 -->
    <template v-if="currentMode === 'camera' || currentMode === 'analyzing' || currentMode === 'result'">
      <!-- ===== 模式：多模态知识检索主界面 ===== -->
      <view class="section-mode" v-if="currentMode === 'camera'">

      <!-- 助手头像区 -->
      <view class="hero-banner">
        <view class="hero-top-row">
          <view class="hero-avatar-wrap">
            <image src="/static/assistant-search.png" mode="aspectFill" class="hero-avatar"></image>
            <view class="hero-status-dot"></view>
          </view>
          <view class="hero-info">
            <text class="hero-name">检修知识检索助手</text>
            <view class="hero-tags">
              <text class="hero-tag">文本检索</text>
              <text class="hero-tag">图片识别</text>
              <text class="hero-tag">型号匹配</text>
            </view>
          </view>
        </view>
        <text class="hero-desc">精准匹配检修手册、相似案例、标准作业流程与工具备件清单</text>
      </view>

      <!-- 语音唤醒区 -->
      <view class="wake-card">
        <view class="wake-header">
          <view class="wake-title-row">
            <text class="wake-icon">🎙️</text>
            <text class="wake-title">语音唤醒</text>
            <view class="wake-status" :class="{ active: wakeListening }">
              <view class="wake-dot"></view>
              <text class="wake-status-text">{{ wakeListening ? '聆听中...' : '已关闭' }}</text>
            </view>
          </view>
          <view class="wake-switch" :class="{ on: wakeEnabled }" @click="toggleWakeEnabled">
            <view class="wake-switch-thumb"></view>
          </view>
        </view>
        <view class="wake-body" v-if="wakeEnabled">
          <text class="wake-hint">说出以下提示词即可快速操作：</text>
          <view class="wake-chips">
            <view v-for="w in wakeWords" :key="w.id" class="wake-chip" :class="{ hit: wakeListening }" @click="executeWakeAction(w.action)">
              <text class="wake-chip-key">"{{ w.keyword }}"</text>
              <text class="wake-chip-desc">{{ w.desc }}</text>
            </view>
          </view>
        </view>
      </view>

      <!-- 检索输入区 -->
      <view class="source-card">
        <view class="card-header">
          <view class="card-title-box">
            <view class="card-dot blue-dot"></view>
            <text class="card-title">检修信息输入</text>
          </view>
          <text class="card-link">文本 / 故障图片 / 设备型号</text>
        </view>

        <!-- 已选图片预览 -->
        <view class="pending-image-bar" v-if="uploadedImage">
          <image class="pending-image-thumb" :src="uploadedImage" mode="aspectFill" @click="previewImage(uploadedImage, '已选图片')"></image>
          <text class="pending-image-name">已选故障图片</text>
          <view class="pending-image-remove" @click="clearPendingImage">
            <text>✕</text>
          </view>
        </view>

        <!-- 主输入框 + 语音 -->
        <view class="source-prompt-box">
          <textarea
            class="source-prompt"
            v-model="resourceRequest.need"
            placeholder="输入故障描述：设备型号、故障现象、需要的资料类型..."
          />
          <view class="source-voice-row">
            <view class="source-voice-btn" :class="{ active: isSearchVoiceRecording || isSearchVoiceTranscribing }" @click="toggleSearchVoiceInput">
              <view class="source-mic-icon">
                <view class="mic-bar"></view>
                <view class="mic-arc"></view>
              </view>
              <text class="source-voice-text">{{ isSearchVoiceRecording ? '松开结束' : (isSearchVoiceTranscribing ? '识别中...' : '语音输入') }}</text>
            </view>
          </view>
        </view>

        <!-- 开始检索按钮 -->
        <view class="search-main-btn" @click="confirmStartSearch">
          <text class="search-main-btn-text">开始检索</text>
        </view>

        <!-- 详细输入折叠开关 -->
        <view class="detail-toggle" @click="showDetailInputs = !showDetailInputs">
          <text class="detail-toggle-text">详细输入</text>
          <text class="detail-toggle-arrow">{{ showDetailInputs ? '▲' : '▼' }}</text>
        </view>

        <!-- 详细输入折叠区域 -->
        <view class="detail-panel" v-if="showDetailInputs">
          <view class="detail-dropzone" @click="chooseImage">
            <text class="detail-dropzone-icon">📷</text>
            <text class="detail-dropzone-text">上传故障图片</text>
          </view>

          <view class="equip-model-row">
            <text class="equip-label">设备型号</text>
            <input class="equip-input" v-model="resourceRequest.deviceModel" placeholder="如 ZK-320、MTR-90、AC-500" />
          </view>

          <view class="device-category-row">
            <view class="card-header">
              <view class="card-title-box">
                <view class="card-dot purple-dot"></view>
                <text class="card-title">设备类型</text>
              </view>
              <text class="card-link">快速选择</text>
            </view>
            <view class="device-category-grid">
              <view v-for="cat in deviceCategories" :key="cat.name" class="device-category-card"
                :style="{ background: cat.color, borderColor: cat.borderColor }"
                @click="handleDeviceCategoryClick(cat)">
                <text class="device-category-icon">{{ cat.icon }}</text>
                <text class="device-category-name">{{ cat.name }}</text>
                <text class="device-category-devices">{{ cat.devices.join('、') }}</text>
              </view>
            </view>
          </view>

          <view class="hot-search-row">
            <text class="hot-search-label">🔥 热门搜索</text>
            <view class="hot-search-tags">
              <view v-for="tag in hotSearchTags" :key="tag.id" class="hot-search-tag" @click="handleHotSearchClick(tag)">
                <text>{{ tag.name }}</text>
              </view>
            </view>
          </view>

          <view class="repair-level-row">
            <text class="equip-label">检修等级</text>
            <view class="level-chips">
              <view v-for="lv in repairLevels" :key="lv.value"
                class="level-chip" :class="{ active: resourceRequest.repairLevel === lv.value }"
                @click="resourceRequest.repairLevel = lv.value">
                <text>{{ lv.label }}</text>
              </view>
            </view>
          </view>

          <view class="resource-chip-row">
            <view class="resource-type-item" v-for="type in resourceTypes" :key="type.name" @click="handleResourceTypeClick(type)">
              <text class="resource-type-icon">{{ type.icon }}</text>
              <text class="resource-type-name">{{ type.name }}</text>
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
              <text class="empty-hint">暂无记录，快去完成第一次检修知识检索吧</text>
            </view>
            <view class="history-item" v-for="(item, i) in historyList.slice(0, 2)" :key="i" @click="loadRecord(item)">
              <view class="history-icon-box" @click.stop="previewImage(item.image, item.name)">
                <image v-if="item.image" class="history-thumb" :src="item.image" mode="aspectFill"></image>
                <text v-else class="history-icon">📘</text>
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
              <text class="card-title">快捷检索</text>
            </view>
          </view>
          <view class="quick-func-list">
            <view class="quick-func-item" v-for="item in quickFuncs" :key="item.label" @click="handleQuickFunc(item)">
              <view class="quick-func-icon" :style="{ background: item.bg }">
                <image v-if="item.icon.includes('.png')" :src="item.icon" class="quick-func-img" mode="aspectFit"></image>
                <text v-else class="quick-func-emoji">{{ item.icon }}</text>
              </view>
              <view class="quick-func-info">
                <text class="quick-func-name">{{ item.label }}</text>
                <text class="quick-func-desc">{{ item.desc }}</text>
              </view>
              <text class="quick-func-arrow">›</text>
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
        <text class="analyzing-title">正在进行多模态知识检索...</text>
        <text class="analyzing-sub">语义解析 · 图片匹配 · 型号识别 · 手册调取</text>
        <view class="analyzing-dots">
          <view class="dot dot1"></view>
          <view class="dot dot2"></view>
          <view class="dot dot3"></view>
        </view>
        
        <!-- 检索进度指示 -->
        <view class="analysis-progress">
          <view v-for="step in analysisSteps" :key="step.id" class="analysis-step"
            :class="{ active: step.active, done: step.done }">
            <view class="step-icon-wrap">
              <text class="step-icon">{{ step.icon }}</text>
              <view v-if="step.done" class="step-check">✓</view>
            </view>
            <view class="step-info">
              <text class="step-title">{{ step.title }}</text>
              <text class="step-desc">{{ step.desc }}</text>
            </view>
            <view class="step-status">
              <text v-if="step.done" class="status-done">完成</text>
              <text v-else-if="step.active" class="status-active">进行中</text>
              <text v-else class="status-wait">等待</text>
            </view>
          </view>
        </view>
      </view>
    </view>

    <!-- ===== 模式：结果 ===== -->
    <scroll-view scroll-y class="result-scroll" v-else-if="currentMode === 'result'">
      <view class="retrieval-report">
        <view class="report-header">
          <view class="report-back-btn" @click="goBackToSearch">
            <text class="back-icon">←</text>
          </view>
          <view class="report-title-block">
            <text class="report-kicker">多模态检索结果</text>
            <text class="report-title">{{ resultData.name }}</text>
            <text class="report-desc">{{ resultData.analysisText }}</text>
            <voice-output-button :text="getReportSpeechText()" service="tuantuan" :show-label="true" label="播报摘要" @error="onTtsError" />
          </view>
          <view class="match-panel">
            <text class="match-label">综合匹配</text>
            <text class="match-score">{{ resultData.score }}%</text>
            <text class="match-status">{{ scoreLevel }}</text>
          </view>
        </view>

        <view class="query-summary">
          <view class="query-item" v-for="item in (resultData.querySummary || [])" :key="item.label">
            <text class="query-label">{{ item.label }}</text>
            <text class="query-value">{{ item.value }}</text>
          </view>
        </view>

        <view class="evidence-strip">
          <view class="evidence-card" v-for="item in (resultData.evidence || [])" :key="item.label">
            <view class="evidence-top">
              <text class="evidence-icon">{{ item.icon }}</text>
              <text class="evidence-status" :class="item.level">{{ item.status }}</text>
            </view>
            <text class="evidence-label">{{ item.label }}</text>
            <text class="evidence-value">{{ item.value }}</text>
          </view>
        </view>

        <view class="result-section">
          <view class="section-head">
            <view class="section-accent"></view>
            <text class="section-title">匹配手册与条款</text>
            <voice-output-button :text="getManualsSpeechText()" service="tuantuan" :show-label="false" @error="onTtsError" />
          </view>
          <view class="manual-list">
            <view class="manual-card" v-for="manual in (resultData.manuals || [])" :key="manual.title">
              <view class="manual-icon">📕</view>
              <view class="manual-body">
                <view class="manual-row">
                  <text class="manual-title">{{ manual.title }}</text>
                  <text class="confidence-chip">{{ manual.confidence }}</text>
                </view>
                <text class="manual-desc">{{ manual.desc }}</text>
                <view class="manual-tags">
                  <text class="manual-tag" v-for="tag in manual.tags" :key="tag">{{ tag }}</text>
                </view>
              </view>
            </view>
          </view>
        </view>

        <view class="result-section">
          <view class="section-head">
            <view class="section-accent"></view>
            <text class="section-title">相似案例</text>
            <voice-output-button :text="getCasesSpeechText()" service="tuantuan" :show-label="false" @error="onTtsError" />
          </view>
          <view class="case-list">
            <view class="case-card" v-for="item in (resultData.cases || [])" :key="item.title">
              <view class="case-head">
                <text class="case-title">{{ item.title }}</text>
                <text class="case-chip">{{ item.similarity }}</text>
              </view>
              <text class="case-desc">{{ item.desc }}</text>
              <view class="case-meta-row">
                <text class="case-meta">{{ item.reason }}</text>
                <text class="case-meta">{{ item.action }}</text>
              </view>
            </view>
          </view>
        </view>

        <view class="result-section">
          <view class="section-head">
            <view class="section-accent"></view>
            <text class="section-title">推荐标准作业流程</text>
            <voice-output-button :text="getWorkflowsSpeechText()" service="tuantuan" :show-label="false" @error="onTtsError" />
          </view>
          <view class="workflow-list">
            <view class="workflow-step" v-for="(step, index) in (resultData.workflows || [])" :key="step.title">
              <view class="step-index">{{ index + 1 }}</view>
              <view class="step-body">
                <view class="step-title-row">
                  <text class="step-title">{{ step.title }}</text>
                  <text class="step-state" :class="step.level">{{ step.state }}</text>
                </view>
                <text class="step-desc">{{ step.desc }}</text>
                <text class="step-check">合规校验：{{ step.check }}</text>
              </view>
            </view>
          </view>
        </view>

        <view class="result-section">
          <view class="section-head">
            <view class="section-accent"></view>
            <text class="section-title">知识图谱关联</text>
          </view>
          <view class="graph-link-list">
            <view class="graph-link" v-for="link in (resultData.graphLinks || [])" :key="link.name">
              <text class="graph-dot"></text>
              <text class="graph-name">{{ link.name }}</text>
              <text class="graph-relation">{{ link.relation }}</text>
            </view>
          </view>
        </view>

        <view class="result-section correction-section">
          <view class="section-head">
            <view class="section-accent"></view>
            <text class="section-title">人工复核与知识沉淀</text>
          </view>
          <view class="correction-grid">
            <view class="correction-card" v-for="item in (resultData.corrections || [])" :key="item.title">
              <text class="correction-title">{{ item.title }}</text>
              <text class="correction-desc">{{ item.desc }}</text>
            </view>
          </view>
        </view>

        <view class="result-section chat-section">
          <view class="section-head">
            <image src="/static/assistant-search.png" class="section-avatar" mode="aspectFill"></image>
            <text class="section-title">继续追问</text>
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
              placeholder="继续追问：例如下一步先查点火还是燃油？"
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

        <view class="bottom-actions">
          <view class="retake-btn secondary" @click="resetToCamera">
            <text class="retake-text">重新检索</text>
          </view>
          <view class="retake-btn" @click="navigateToKnowledgeGraph">
            <text class="retake-text">查看知识图谱</text>
          </view>
        </view>
      </view>
    </scroll-view>

    <!-- ===== 知识点查询弹窗 ===== -->
    <view class="modal-mask" v-if="kbQueryMode" @click="kbQueryMode = false"></view>
    <view class="modal-panel" :class="{ open: kbQueryMode }">
      <view class="modal-header">
        <view class="modal-header-left" @click="kbQueryMode = false">
          <text class="modal-back-icon">←</text>
        </view>
        <text class="modal-header-title">检修资料查询</text>
        <view class="modal-header-right"></view>
      </view>

      <scroll-view scroll-y class="modal-content">
        <view class="calorie-query-content">
          <view class="query-input-section">
            <view class="input-wrapper">
              <input
                type="text"
                v-model="kbQueryKeyword"
                placeholder="请输入设备型号、故障现象或资料名称"
                class="query-input"
                @confirm="queryCalories"
              />
              <view class="query-btn" @click="queryCalories">
                <text class="query-btn-text">查询</text>
              </view>
            </view>
          </view>

          <view class="result-section" v-if="kbQueryResult">
            <view class="food-info">
              <text class="food-name">{{ kbQueryResult.name }}</text>
              <text class="calorie-value">{{ kbQueryResult.related }} 条关联</text>
            </view>
            <view class="nutrition-details">
              <view class="nutrition-item">
                <text class="nutrition-label">资料覆盖</text>
                <text class="nutrition-value">{{ kbQueryResult.coverage }} 星</text>
              </view>
              <view class="nutrition-item">
                <text class="nutrition-label">案例匹配</text>
                <text class="nutrition-value">{{ kbQueryResult.match }} 星</text>
              </view>
              <view class="nutrition-item">
                <text class="nutrition-label">作业关联</text>
                <text class="nutrition-value">{{ kbQueryResult.cases }} 星</text>
              </view>
            </view>
          </view>

          <view class="common-foods">
            <text class="section-title">常见检修对象</text>
            <view class="food-grid">
              <view class="food-item" v-for="food in commonDevices" :key="food.name" @click="selectCommonFood(food)">
                <text class="food-item-name">{{ food.name }}</text>
                <text class="food-item-calorie">{{ food.related }} 条关联</text>
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
            <text class="section-title">🛡️ 检修目标</text>
            <view class="settings-list">
              <view class="setting-item">
                <text class="setting-label">目标类型</text>
                <view class="selector-row">
                  <view
                    class="selector-tag"
                    :class="{ active: preferences.goalType === '基础巩固' }"
                    @click="preferences.goalType = '基础巩固'"
                  >快速定位</view>
                  <view
                    class="selector-tag"
                    :class="{ active: preferences.goalType === '项目实操' }"
                    @click="preferences.goalType = '项目实操'"
                  >标准作业</view>
                  <view
                    class="selector-tag"
                    :class="{ active: preferences.goalType === '考试冲刺' }"
                    @click="preferences.goalType = '考试冲刺'"
                  >风险复核</view>
                  <view
                    class="selector-tag"
                    :class="{ active: preferences.goalType === '论文拓展' }"
                    @click="preferences.goalType = '论文拓展'"
                  >经验沉淀</view>
                </view>
              </view>
              <view class="setting-item">
                <text class="setting-label">每日检修目标 (分钟)</text>
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
            <text class="section-title">📚 检索偏好</text>
            <view class="settings-list">
              <view class="setting-item">
                <text class="setting-label">检修方式</text>
                <view class="selector-row">
                  <view
                    class="selector-tag"
                    :class="{ active: preferences.dietType === '讲练结合' }"
                    @click="preferences.dietType = '讲练结合'"
                  >手册优先</view>
                  <view
                    class="selector-tag"
                    :class="{ active: preferences.dietType === '案例驱动' }"
                    @click="preferences.dietType = '案例驱动'"
                  >案例驱动</view>
                  <view
                    class="selector-tag"
                    :class="{ active: preferences.dietType === '图解优先' }"
                    @click="preferences.dietType = '图解优先'"
                  >图解优先</view>
                  <view
                    class="selector-tag"
                    :class="{ active: preferences.dietType === '代码实操' }"
                    @click="preferences.dietType = '代码实操'"
                  >流程复核</view>
                </view>
              </view>
              <view class="setting-item">
                <text class="setting-label">资源偏好</text>
                <view class="selector-row">
                  <view
                    class="selector-tag"
                    :class="{ active: preferences.flavor === '短文档' }"
                    @click="preferences.flavor = '短文档'"
                  >短文档</view>
                  <view
                    class="selector-tag"
                    :class="{ active: preferences.flavor === '短视频' }"
                    @click="preferences.flavor = '短视频'"
                  >短视频</view>
                  <view
                    class="selector-tag"
                    :class="{ active: preferences.flavor === '综合项目' }"
                    @click="preferences.flavor = '综合项目'"
                  >综合项目</view>
                </view>
              </view>
            </view>
          </view>

          <view class="settings-section">
            <text class="section-title">🚫 检修约束</text>
            <view class="settings-list">
              <view class="setting-item">
                <text class="setting-label">重点故障</text>
                <input
                  type="text"
                  v-model="preferences.allergies"
                  placeholder="如：柜体过热、轴承异响"
                  class="setting-input"
                />
              </view>
              <view class="setting-item">
                <text class="setting-label">暂不推荐内容</text>
                <input
                  type="text"
                  v-model="preferences.avoidIngredients"
                  placeholder="如：无关型号、过期资料"
                  class="setting-input"
                />
              </view>
              <view class="setting-item">
                <text class="setting-label">标准流程优先</text>
                <view class="switch-wrapper">
                  <switch
                    :checked="preferences.lowOilSalt"
                    class="small-switch"
                    @change="setSwitchValue(preferences, 'lowOilSalt', $event)"
                  ></switch>
                </view>
              </view>
              <view class="setting-item">
                <text class="setting-label">防幻觉校验</text>
                <view class="switch-wrapper">
                  <switch
                    :checked="preferences.noSugar"
                    class="small-switch"
                    @change="setSwitchValue(preferences, 'noSugar', $event)"
                  ></switch>
                </view>
              </view>
            </view>
          </view>

          <view class="settings-section">
            <text class="section-title">⚙️ 通知设置</text>
            <view class="settings-list">
              <view class="setting-item">
                <text class="setting-label">检修提醒</text>
                <view class="switch-wrapper">
                  <switch
                    :checked="preferences.notifications.healthReminder"
                    class="small-switch"
                    @change="setSwitchValue(preferences.notifications, 'healthReminder', $event)"
                  ></switch>
                </view>
              </view>
              <view class="setting-item">
                <text class="setting-label">检修周报</text>
                <view class="switch-wrapper">
                  <switch
                    :checked="preferences.notifications.weeklyReport"
                    class="small-switch"
                    @change="setSwitchValue(preferences.notifications, 'weeklyReport', $event)"
                  ></switch>
                </view>
              </view>
              <view class="setting-item">
                <text class="setting-label">每日总结</text>
                <view class="switch-wrapper">
                  <switch
                    :checked="preferences.notifications.dailySummary"
                    class="small-switch"
                    @change="setSwitchValue(preferences.notifications, 'dailySummary', $event)"
                  ></switch>
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
              <text class="group-title">📘 检修对象基本信息</text>
              <view class="input-item">
                <text class="input-label">设备型号或故障现象</text>
                <input
                  type="text"
                  v-model="manualInputData.foodName"
                placeholder="请输入设备型号或故障现象"
                  class="manual-input"
                />
              </view>
              <view class="input-item">
                <text class="input-label">现场描述</text>
                <textarea
                  v-model="manualInputData.description"
                  placeholder="请输入故障现象、检修等级或现场约束（可选）"
                  class="manual-textarea"
                />
              </view>
            </view>

            <view class="input-group">
              <text class="group-title">🧩 资源属性</text>
              <view class="input-item">
                <text class="input-label">关联资料</text>
                <input
                  type="text"
                  v-model="manualInputData.ingredients"
                  placeholder="如：检修手册、热成像图、历史案例"
                  class="manual-input"
                />
              </view>
              <view class="input-item">
                <text class="input-label">资料形式</text>
                <view class="selector-row">
                  <view
                    class="selector-tag"
                    :class="{ active: manualInputData.cookingMethod === '讲解文档' }"
                    @click="manualInputData.cookingMethod = '讲解文档'"
                  >检修手册</view>
                  <view
                    class="selector-tag"
                    :class="{ active: manualInputData.cookingMethod === '思维导图' }"
                    @click="manualInputData.cookingMethod = '思维导图'"
                  >故障图谱</view>
                  <view
                    class="selector-tag"
                    :class="{ active: manualInputData.cookingMethod === '相似案例' }"
                    @click="manualInputData.cookingMethod = '相似案例'"
                  >相似案例</view>
                  <view
                    class="selector-tag"
                    :class="{ active: manualInputData.cookingMethod === '代码案例' }"
                    @click="manualInputData.cookingMethod = '代码案例'"
                  >作业流程</view>
                  <view
                    class="selector-tag"
                    :class="{ active: manualInputData.cookingMethod === '视频脚本' }"
                    @click="manualInputData.cookingMethod = '视频脚本'"
                  >风险清单</view>
                  <view
                    class="selector-tag"
                    :class="{ active: manualInputData.cookingMethod === '拓展阅读' }"
                    @click="manualInputData.cookingMethod = '拓展阅读'"
                  >风险清单</view>
                </view>
              </view>
              <view class="input-item">
                <text class="input-label">预计检修时长 (分钟)</text>
                <input
                  type="number"
                  v-model="manualInputData.weight"
                placeholder="请输入预计检修时长"
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
                  <switch
                    :checked="manualInputData.perishable"
                    class="small-switch"
                    @change="setSwitchValue(manualInputData, 'perishable', $event)"
                  ></switch>
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

    <!-- ===== 检修周报弹窗 ===== -->
    <view class="modal-mask" v-if="weeklyReportMode" @click="weeklyReportMode = false"></view>
    <view class="modal-panel" :class="{ open: weeklyReportMode }">
      <view class="modal-header">
        <view class="modal-header-left" @click="weeklyReportMode = false">
          <text class="modal-back-icon">←</text>
        </view>
        <text class="modal-header-title">检修周报</text>
        <view class="modal-header-right"></view>
      </view>

      <scroll-view scroll-y class="modal-content">
        <view class="weekly-report-content">
          <view class="report-summary">
            <view class="summary-card">
              <text class="summary-title">本周检修时长</text>
              <text class="summary-value">{{ weeklyReportData.totalCalories }} 分钟</text>
            </view>
            <view class="summary-card">
              <text class="summary-title">日均检修时长</text>
              <text class="summary-value">{{ weeklyReportData.averageCalories }} 分钟</text>
            </view>
          </view>

          <view class="report-section">
            <text class="section-title">每日检修投入</text>
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
                <text class="nutrition-label">风险记录</text>
                <text class="nutrition-value">{{ weeklyReportData.carbs }} 次</text>
                <view class="nutrition-bar">
                  <view class="nutrition-fill carbs" :style="{ width: (weeklyReportData.carbs / 2100) * 100 + '%' }"></view>
                </view>
              </view>
            </view>
          </view>

          <view class="report-section">
            <text class="section-title">检修建议</text>
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
            <text v-else class="drawer-emoji">📘</text>
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
import VoiceOutputButton from '../../src/components/VoiceOutputButton.vue';

export default {
  components: {
    VoiceOutputButton
  },
  data() {
    return {
      currentMode: 'camera',
      kbQueryMode: false,
      kbQueryKeyword: '',
      kbQueryResult: null,
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
      resourceRequest: {
        major: '',
        course: '',
        weakness: '',
        need: '摩托车发动机启动困难，怠速不稳伴有异响，需要检索维修手册、相似案例和标准检修流程。',
        deviceModel: '',
        repairLevel: '二级检修'
      },
      repairLevels: [
        { label: '巡检', value: '巡检' },
        { label: '一级检修', value: '一级检修' },
        { label: '二级检修', value: '二级检修' },
        { label: '故障抢修', value: '故障抢修' }
      ],
      resourceTypes: [
        { icon: '📄', name: '检修手册', desc: '调取设备说明书、检修规程和故障处理条款' },
        { icon: '🖼️', name: '故障图片匹配', desc: '对故障照片、铭牌和现场截图做跨模态匹配' },
        { icon: '🧾', name: '相似案例', desc: '检索历史检修案例、经验总结和处理结论' },
        { icon: '🧰', name: '工具备件', desc: '推荐工具清单、备件规格和安全防护要求' },
        { icon: '⚠️', name: '风险提醒', desc: '提示停电验电、挂牌上锁等合规风险点' },
        { icon: '📋', name: '作业流程', desc: '关联标准化检修步骤和复核节点' }
      ],
      hotSearchTags: [
        { id: 1, name: '发动机异响', device: '摩托车发动机', fault: '发动机异响', level: '二级检修' },
        { id: 2, name: '启动困难', device: 'ZK-320', fault: '启动困难、怠速不稳', level: '故障抢修' },
        { id: 3, name: '电路故障', device: 'MTR-90', fault: '电路短路、报警灯亮', level: '一级检修' },
        { id: 4, name: '过热排查', device: 'AC-500', fault: '柜体过热、温升异常', level: '巡检' }
      ],
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
          '本周检修资料使用节奏稳定，继续保持',
          '检修手册与风险复核搭配较好，有助于巩固流程',
          '现场案例使用偏少，建议补充处置记录',
          '风险记录适中，适合当前作业阶段'
        ]
      },
      uploadedImage: '',
      analysisTip: '正在分析...',
      resultChatMsg: '',
      isVoiceRecording: false,
      isVoiceTranscribing: false,
      voiceInputController: null,
      isSearchVoiceRecording: false,
      isSearchVoiceTranscribing: false,
      searchVoiceController: null,
      showDetailInputs: false,
      showHistory: false,
      resultChatList: [],
      resultData: {
        name: '', score: 0, calories: 0,
        macros: { protein: '', fat: '', carbs: '' },
        dimensions: [], suggestions: [],
        analysisText: '',
        nutrition: [],
        querySummary: [],
        evidence: [],
        manuals: [],
        cases: [],
        workflows: [],
        graphLinks: [],
        corrections: []
      },
      historyList: [],
      loading: false,
      quickFuncs: [
        { icon: '/static/icons/inspection-report.png', label: '检修报告', desc: '查看本周检修统计与资源使用分析', bg: 'linear-gradient(135deg,#f0f9e8,#c6e8b3)' },
        { icon: '🧾', label: '案例检索', desc: '搜索历史检修案例与处置经验', bg: 'linear-gradient(135deg,#fef3c7,#fde68a)' },
        { icon: '/static/icons/settings.png', label: '设置', desc: '调整检索偏好与通知设置', bg: 'linear-gradient(135deg,#f0e6ff,#e0ccff)' }
      ],
      commonDevices: [
        { name: '摩托车发动机', related: 100, coverage: 5, match: 5, cases: 6 },
        { name: '点火系统', related: 85, coverage: 4, match: 4, cases: 5 },
        { name: '燃油供给系统', related: 80, coverage: 4, match: 4, cases: 4 },
        { name: '机油润滑系统', related: 75, coverage: 3, match: 4, cases: 4 },
        { name: '气门机构', related: 70, coverage: 3, match: 3, cases: 3 },
        { name: '传动链条', related: 65, coverage: 3, match: 3, cases: 3 }
      ],
      deviceCategories: [
        {
          name: '电气设备',
          icon: '⚡',
          devices: ['ZK-320', 'MTR-90', 'AC-500'],
          color: 'linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)',
          borderColor: '#fed7aa'
        },
        {
          name: '机械设备',
          icon: '⚙️',
          devices: ['YH-800', 'ZX-200', 'SY-150'],
          color: 'linear-gradient(135deg, #e0e5ec 0%, #d9d9d9 100%)',
          borderColor: '#cbd5e1'
        },
        {
          name: '空调系统',
          icon: '❄️',
          devices: ['AC-500', 'AC-300', 'FC-200'],
          color: 'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)',
          borderColor: '#a5f3fc'
        },
        {
          name: '动力系统',
          icon: '🚀',
          devices: ['发动机', '变速箱', '传动系统'],
          color: 'linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%)',
          borderColor: '#fecaca'
        }
      ],
      analysisSteps: [
        { id: 1, title: '语义解析', desc: '解析故障描述', icon: '文', done: false, active: false },
        { id: 2, title: '图片匹配', desc: '对比故障图片', icon: '图', done: false, active: false },
        { id: 3, title: '型号识别', desc: '识别设备型号', icon: '型', done: false, active: false },
        { id: 4, title: '知识检索', desc: '检索检修知识', icon: '知', done: false, active: false },
        { id: 5, title: '生成报告', desc: '整理检索结果', icon: '报', done: false, active: false }
      ],
      currentAnalysisStep: 0,
      // 提示词唤醒
      wakeEnabled: false,
      wakeListening: false,
      wakeWords: [
        { id: 1, keyword: '开始检索', action: 'search', desc: '唤醒后自动开始检索' },
        { id: 2, keyword: '查手册', action: 'manual', desc: '检索检修手册' },
        { id: 3, keyword: '查案例', action: 'case', desc: '检索相似案例' },
        { id: 4, keyword: '查流程', action: 'workflow', desc: '检索标准作业流程' },
        { id: 5, keyword: '拍照分析', action: 'camera', desc: '打开拍照识别' }
      ],
      wakeCheckTimer: null,
      wakeController: null
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
      if (s >= 90) return '高度适配检修画像';
      if (s >= 75) return '适配当前检修目标';
      if (s >= 60) return '可继续优化';
      if (s >= 40) return '需补充上下文';
      return '不建议直接使用';
    },
    healthInsightMetrics() {
      return [
        { label: '事实校验', ...this.getOilRiskMetric() },
        { label: '难度适配', ...this.getSaltRiskMetric() },
        { label: '资源类型', ...this.getVegetableMetric() },
        { label: '画像匹配', ...this.getBalanceMetric() }
      ];
    }
  },

  onLoad() {
    this.loadHistoryFromServer();
    this.initVoiceInput();
    this.initSearchVoiceInput();
  },

  onUnload() {
    if (this.voiceInputController) {
      this.voiceInputController.destroy();
    }
    if (this.searchVoiceController) {
      this.searchVoiceController.destroy();
    }
    this.stopWakeListening();
  },

  methods: {
    setSwitchValue(target, key, event) {
      target[key] = Boolean(event.detail.value);
    },

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
      if (this.hasKeyword(text, ['缺少引用', '未校验', '幻觉', '事实风险', '来源不足'])) {
        return { value: '需复核', level: 'risk-high' };
      }
      if (this.hasKeyword(text, ['知识库引用', '来源标注', '教师审核', '题目回测', '通过'])) {
        return { value: '通过', level: 'risk-low' };
      }
      return { value: '待校验', level: 'risk-mid' };
    },

    getSaltRiskMetric() {
      const text = this.getResultKeywords();
      if (this.hasKeyword(text, ['过难', '高阶论文', '基础要求较高', '需补充'])) {
        return { value: '偏高', level: 'risk-high' };
      }
      if (this.hasKeyword(text, ['基础巩固', '先易后难', '分层', '适配'])) {
        return { value: '适配', level: 'risk-low' };
      }
      return { value: '中等', level: 'risk-mid' };
    },

    getVegetableMetric() {
      const text = this.getResultKeywords();
      if (this.hasKeyword(text, ['检修手册', '故障图谱', '相似案例', '作业流程', '风险清单', '视频脚本'])) {
        return { value: '丰富', level: 'risk-low' };
      }
      if (this.hasKeyword(text, ['单一', '只有', '待生成'])) {
        return { value: '偏少', level: 'risk-high' };
      }
      return { value: '一般', level: 'risk-mid' };
    },

    getBalanceMetric() {
      const score = Number(this.resultData.score) || 0;
      const text = this.getResultKeywords();
      if (score >= 80 || this.hasKeyword(text, ['适配', '画像适配', '作业路径'])) {
        return { value: '较高', level: 'risk-low' };
      }
      if (score < 60 || this.hasKeyword(text, ['不适配', '需补充上下文', '偏高', '过难'])) {
        return { value: '需补充', level: 'risk-high' };
      }
      return { value: '中等', level: 'risk-mid' };
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
    chooseImage() {
      uni.chooseImage({
        count: 1,
        sourceType: ['camera', 'album'],
        success: (res) => {
          this.uploadedImage = res.tempFilePaths[0];
          uni.showToast({ title: '图片已选择', icon: 'success', duration: 1000 });
        }
      });
    },

    clearPendingImage() {
      this.uploadedImage = '';
    },

    async confirmStartSearch() {
      if (this.uploadedImage) {
        await this.startImageAnalysis();
      } else {
        this.generateFromProfileInput();
      }
    },

    async startImageAnalysis() {
      this.currentMode = 'analyzing';
      this.loading = true;
      try {
        const analysisResponse = await this.uploadAndAnalyzeImage(this.uploadedImage);
        if (analysisResponse) {
          const nowTs = Date.now();
          const resources = this.normalizeGeneratedResources(analysisResponse.nutrition);
          const fitScore = Number(analysisResponse.score) || 88;

          this.resultData = {
            name: analysisResponse.name || 'ZK-320配电柜：过热故障检修资料包',
            image: this.uploadedImage,
            score: fitScore,
            calories: resources.length,
            macros: {
              protein: '手册+图谱',
              fat: '案例+流程',
              carbs: '复核计划'
            },
            analysisText: `本次资料包依据设备型号、故障现象、检修等级和现场约束生成，检修适配度为${fitScore}分，已附带知识库引用与风险复核建议。`,
            dimensions: analysisResponse.dimensions || [
              { name: '设备画像匹配', score: 92, val: '已完成', color: '#52c41a' },
              { name: '知识库检索', score: 88, val: '已引用', color: '#52c41a' },
              { name: '多资源生成', score: 90, val: '5类资源', color: '#52c41a' },
              { name: '质量评测', score: 84, val: '风险复核', color: '#faad14' },
              { name: '作业路径规划', score: 86, val: '已接入', color: '#52c41a' }
            ],
            suggestions: analysisResponse.suggestions || [
              '建议先核对设备铭牌与手册版本，再按标准作业票执行排查。',
              '对生成内容进行知识库引用校验，降低大模型幻觉风险',
              '把风险复核项加入作业路径，下一轮根据处置记录自动补齐薄弱环节。'
            ],
            nutrition: resources
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
            nutrition: this.resultData.nutrition,
            date: this.formatHistoryDate(nowTs),
            ts: nowTs
          };
          this.historyList = [record, ...(this.historyList || [])];
          this.historyList.sort((a, b) => (b.ts || 0) - (a.ts || 0));

          this.resultChatList = [
            {
              type: 'agent',
              text: this.truncatePlainText(
                '生成完成：' + this.resultData.name + '的检修适配度为' + this.resultData.score + '分。' + (this.resultData.suggestions[0] || ''),
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
    },

    generateFromProfileInput() {
      const nowTs = Date.now();
      const need = this.resourceRequest.need || '需要检索检修手册、相似案例和标准化作业流程';
      const modelMatch = need.match(/设备型号\s*([A-Za-z0-9-]+)/) || need.match(/型号\s*([A-Za-z0-9-]+)/);
      const faultMatch = need.match(/(.+?)(故障|过热|异响|报警|漏油|失效|异常)/);
      const inferredDevice = need.includes('摩托车发动机') ? '摩托车发动机' : 'ZK-320';
      const deviceType = this.resourceRequest.deviceModel || this.resourceRequest.major || (modelMatch ? modelMatch[1] : inferredDevice);
      const repairLevel = this.resourceRequest.repairLevel || this.resourceRequest.course || '二级检修';
      const faultDesc = this.resourceRequest.weakness || (faultMatch ? faultMatch[0] : '柜体过热并伴随异响');
      const topic = faultDesc.split(/[，,、]/).filter(Boolean)[0] || deviceType;

      this.currentMode = 'analyzing';
      this.startAnalysisProgress();

      setTimeout(() => {
        this.resultData = {
          name: `${deviceType}：${topic}检修知识检索结果`,
          image: '/static/assistant-search.png',
          score: 91,
          calories: 6,
          macros: {
            protein: '手册+案例',
            fat: '流程+风险',
            carbs: '备件+记录'
          },
          analysisText: `已根据设备型号“${deviceType}”、检修等级“${repairLevel}”、故障描述“${faultDesc}”和输入信息“${need}”完成多模态知识检索，并匹配检修手册、相似案例和标准作业流程。`,
          querySummary: [
            { label: '设备对象', value: deviceType },
            { label: '故障现象', value: faultDesc },
            { label: '检修等级', value: repairLevel },
            { label: '输入模态', value: '文本 + 设备对象 + 可扩展图片证据' }
          ],
          evidence: [
            { icon: '📝', label: '文本语义', value: '启动困难、怠速不稳、异响', status: '已解析', level: 'ok' },
            { icon: '🏷️', label: '设备识别', value: deviceType, status: '已匹配', level: 'ok' },
            { icon: '🖼️', label: '图片证据', value: '待上传故障照片/铭牌截图', status: '待补充', level: 'warn' },
            { icon: '📚', label: '知识来源', value: '维修手册 + 相似案例 + 图谱节点', status: '已关联', level: 'ok' }
          ],
          dimensions: [
            { name: '语义检索匹配度', score: 94, val: '文本/图片/型号', color: '#52c41a' },
            { name: '手册覆盖度', score: 96, val: '检修规程+说明书', color: '#52c41a' },
            { name: '案例相似度', score: 88, val: '历史案例', color: '#52c41a' },
            { name: '合规风险识别', score: 86, val: '需复核', color: '#faad14' },
            { name: '作业流程关联', score: 90, val: '已接入', color: '#52c41a' }
          ],
          suggestions: [
            '优先阅读”摩托车发动机维修手册”，核对点火系统、燃油供给和润滑状态。',
            '进入现场作业前确认熄火冷却、防护用品到位，检查燃油泄漏风险。',
            '检修完成后上传处置照片与经验总结，审核后沉淀进知识图谱。'
          ],
          nutrition: [
            { name: '维修手册', percent: '摩托车发动机维修手册.pdf', status: '完成' },
            { name: '故障图片匹配', percent: '发动机异响视觉特征', status: '完成' },
            { name: '相似检修案例', percent: '启动困难+怠速不稳+异响', status: '完成' },
            { name: '工具备件清单', percent: '火花塞/扳手/机油/防护用品', status: '完成' },
            { name: '标准作业流程', percent: '二级检修步骤化指引', status: '完成' },
            { name: '风险与合规提醒', percent: '燃油泄漏+熄火冷却+复核', status: '完成' }
          ],
          manuals: [
            {
              title: '摩托车发动机维修手册.pdf',
              confidence: '96%',
              desc: '命中发动机启动困难、怠速不稳、异响和润滑检查相关内容，建议作为本次检修的主引用资料。',
              tags: ['已入库', 'PDF', '主手册']
            },
            {
              title: '点火系统检查条款',
              confidence: '91%',
              desc: '与启动困难、怠速异常高度相关，优先检查火花塞、点火线圈和线路连接。',
              tags: ['点火', '启动困难']
            },
            {
              title: '机油与润滑保养条款',
              confidence: '87%',
              desc: '与发动机异响、温升和磨损风险相关，需确认油位、油品状态和泄漏情况。',
              tags: ['润滑', '异响']
            }
          ],
          cases: [
            {
              title: '案例 A：冷机启动困难并伴随怠速波动',
              similarity: '89%',
              desc: '历史案例显示火花塞积碳、点火线圈输出不稳和燃油滤清堵塞均可能触发相似现象。',
              reason: '相似原因：点火/供油异常',
              action: '处置：清洁火花塞并复测点火'
            },
            {
              title: '案例 B：热机后发动机异响加重',
              similarity: '82%',
              desc: '相似案例中润滑不足和气门间隙异常是主要风险源，需先排除机油状态问题。',
              reason: '相似原因：润滑不足',
              action: '处置：检查油位与气门间隙'
            }
          ],
          workflows: [
            { title: '安全确认', state: '必做', level: 'warn', desc: '确认熄火、冷却、通风，远离明火并佩戴防护用品。', check: '防护用品、冷却状态、燃油泄漏' },
            { title: '外观与油液检查', state: '进行中', level: 'active', desc: '检查机油液位、油品状态、外部漏油和异常磨损痕迹。', check: '照片留存、油位记录' },
            { title: '点火系统检查', state: '推荐', level: 'ok', desc: '检查火花塞、点火线圈、点火线路与连接可靠性。', check: '点火测试结果' },
            { title: '燃油供给检查', state: '推荐', level: 'ok', desc: '检查燃油滤清、油路堵塞、喷油/化油器供给状态。', check: '泄漏确认、供油状态' },
            { title: '异响定位与复核', state: '需复核', level: 'warn', desc: '区分外部附件噪声与发动机本体噪声，记录工况。', check: '怠速/加速/热机复测' }
          ],
          graphLinks: [
            { name: '摩托车发动机', relation: '专业检修对象' },
            { name: '摩托车发动机维修手册.pdf', relation: '主资料来源' },
            { name: '点火系统检查', relation: '推荐流程' },
            { name: '燃油供给检查', relation: '推荐流程' },
            { name: '发动机异响', relation: '故障现象' },
            { name: '机油与润滑', relation: '保养项目' }
          ],
          corrections: [
            { title: '人工确认故障原因', desc: '检修人员可将实际原因标记为点火、供油、润滑或机械磨损。' },
            { title: '上传现场案例', desc: '处置照片、检测数值和复盘结论可审核后沉淀到知识图谱。' },
            { title: '修正模型输出', desc: '若推荐流程不适用，可手动标注并形成系统适配反馈。' }
          ]
        };

        const record = {
          ...this.resultData,
          date: this.formatHistoryDate(nowTs),
          ts: nowTs
        };
        this.historyList = [record, ...(this.historyList || [])].sort((a, b) => (b.ts || 0) - (a.ts || 0));
        this.resultChatList = [
          {
            type: 'agent',
            text: `已完成${deviceType}检修知识检索：包含检修手册、故障图片匹配、相似案例、工具备件、标准作业流程和风险提醒。`
          }
        ];
        this.currentMode = 'result';
      }, 6000);
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
    navigateToKnowledgeGraph() {
      uni.switchTab({
        url: '/pages/restaurant-recommendation/restaurant-recommendation',
        fail: () => uni.navigateTo({ url: '/pages/restaurant-recommendation/restaurant-recommendation' })
      });
    },

    normalizeGeneratedResources(rawResources) {
      const defaults = [
        { name: '检修手册', percent: '规程条款', status: '完成' },
        { name: '故障图片匹配', percent: '视觉特征', status: '完成' },
        { name: '相似案例', percent: '处置结论', status: '完成' },
        { name: '工具备件', percent: '清单规格', status: '完成' },
        { name: '标准作业流程', percent: '步骤化指引', status: '完成' },
        { name: '风险提醒', percent: '合规校验', status: '待复核' }
      ];
      if (!Array.isArray(rawResources) || rawResources.length === 0) return defaults;

      const legacyKeyMap = {
        calories: '检修手册',
        protein: '故障图片匹配',
        fat: '相似案例',
        carbs: '标准作业流程'
      };

      return rawResources.map((item, index) => ({
        name: item.name || legacyKeyMap[item.key] || defaults[index]?.name || '检修资源',
        percent: item.percent || item.value || defaults[index]?.percent || '已生成',
        status: item.status || '完成'
      }));
    },

    async sendResultChat() {
      if (!this.resultChatMsg.trim()) return;
      const msg = this.resultChatMsg;
      this.resultChatList.push({ type: 'user', text: msg });
      this.resultChatMsg = '';
      try {
        const pendingIndex = this.resultChatList.length;
        this.resultChatList.push({ type: 'agent', text: '正在生成回复，请稍候...' });

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

    initSearchVoiceInput() {
      if (this.searchVoiceController) return;

      this.searchVoiceController = createVoiceInputController({
        service: 'tuantuan',
        onStateChange: ({ isRecording, isTranscribing }) => {
          this.isSearchVoiceRecording = isRecording;
          this.isSearchVoiceTranscribing = isTranscribing;
        },
        onTranscribed: (text) => {
          this.resourceRequest.need = this.resourceRequest.need.trim()
            ? `${this.resourceRequest.need.trim()} ${text}`
            : text;
          uni.showToast({ title: '语音已转文字', icon: 'none' });
        },
        onError: (error) => {
          const title = (error?.message || '语音输入失败').slice(0, 20);
          uni.showToast({ title, icon: 'none' });
        }
      });
    },

    async toggleSearchVoiceInput() {
      this.initSearchVoiceInput();

      try {
        await this.searchVoiceController.toggleRecording();
      } catch (error) {
        const title = (error?.message || '语音输入失败').slice(0, 20);
        uni.showToast({ title, icon: 'none' });
      }
    },

    getReportSpeechText() {
      const parts = [];
      if (this.resultData.name) parts.push(`检索结果：${this.resultData.name}`);
      if (this.resultData.analysisText) parts.push(this.sanitizePlainText(this.resultData.analysisText));
      if (this.resultData.score) parts.push(`综合匹配度：${this.resultData.score}%`);
      const suggestions = this.resultData.suggestions || [];
      if (suggestions.length > 0) parts.push('检修建议：' + suggestions.map(s => this.sanitizePlainText(s)).join('；'));
      return parts.join('。');
    },

    getManualsSpeechText() {
      const manuals = this.resultData.manuals || [];
      if (manuals.length === 0) return '';
      const parts = ['匹配到以下检修手册和条款：'];
      manuals.forEach((m, i) => {
        parts.push(`第${i + 1}项，${m.title}，匹配度${m.confidence}。${this.sanitizePlainText(m.desc)}`);
      });
      return parts.join('');
    },

    getCasesSpeechText() {
      const cases = this.resultData.cases || [];
      if (cases.length === 0) return '';
      const parts = ['找到以下相似案例：'];
      cases.forEach((c, i) => {
        parts.push(`案例${i + 1}，${c.title}，相似度${c.similarity}。${this.sanitizePlainText(c.desc)}`);
      });
      return parts.join('');
    },

    getWorkflowsSpeechText() {
      const workflows = this.resultData.workflows || [];
      if (workflows.length === 0) return '';
      const parts = ['推荐标准作业流程如下：'];
      workflows.forEach((w, i) => {
        parts.push(`第${i + 1}步，${w.title}，状态${w.state}。${this.sanitizePlainText(w.desc)}`);
      });
      return parts.join('');
    },

    onTtsError(error) {
      const title = (error?.message || '语音播放失败').slice(0, 20);
      uni.showToast({ title, icon: 'none' });
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
        url: '/pages/image-viewer/image-viewer?src=' + encodeURIComponent(imageSrc) + '&title=' + encodeURIComponent(title || '检修资料')
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
      if (!this.kbQueryKeyword.trim()) {
        uni.showToast({ title: '请输入设备型号或故障现象', icon: 'none' });
        return;
      }

      const food = this.commonDevices.find(f => f.name.includes(this.kbQueryKeyword));
      if (food) {
        this.kbQueryResult = food;
      } else {
        this.kbQueryResult = {
          name: this.kbQueryKeyword,
          related: 100,
          coverage: 5.0,
          match: 3.0,
          carbs: 15.0
        };
      }
    },

    selectCommonFood(food) {
      this.kbQueryKeyword = food.name;
      this.kbQueryResult = food;
    },

    handleQuickFunc(item) {
      if (item.label === '检修报告') {
        this.weeklyReportMode = true;
      } else if (item.label === '案例检索') {
        this.resourceRequest.need = '需要检索相似检修案例、历史处置经验和故障处理结论。';
        this.showDetailInputs = true;
        uni.showToast({ title: '已填入案例检索条件', icon: 'none' });
      } else if (item.label === '设置') {
        this.settingsMode = true;
      }
    },

    handleResourceTypeClick(type) {
      const typeMap = {
        '检修手册': '检修手册',
        '故障图片匹配': '故障图片匹配',
        '相似案例': '相似案例',
        '工具备件': '工具备件清单',
        '风险提醒': '风险提醒',
        '作业流程': '标准作业流程'
      };
      const need = `${typeMap[type.name]}：${type.desc}`;
      this.resourceRequest.need = need;
      uni.showToast({ title: `已选择：${type.name}`, icon: 'success' });
    },

    handleDeviceCategoryClick(cat) {
      this.resourceRequest.deviceModel = cat.devices[0];
      this.resourceRequest.need = `需要检索${cat.name}相关的检修手册、相似案例和标准作业流程。`;
      uni.showToast({ title: `已选择：${cat.name}`, icon: 'success' });
    },

    goBackToSearch() {
      this.currentMode = 'camera';
      this.resetAnalysisProgress();
    },

    handleHotSearchClick(tag) {
      this.resourceRequest.deviceModel = tag.device;
      this.resourceRequest.repairLevel = tag.level;
      this.resourceRequest.need = `${tag.device}出现${tag.fault}，需要检索检修手册、相似案例和标准作业流程。`;
      uni.showToast({ title: '已填充检索条件', icon: 'success' });
    },

    startAnalysisProgress() {
      this.currentAnalysisStep = 0;
      this.analysisSteps.forEach(step => {
        step.done = false;
        step.active = false;
      });
      
      const updateStep = () => {
        if (this.currentAnalysisStep > 0) {
          this.analysisSteps[this.currentAnalysisStep - 1].done = true;
          this.analysisSteps[this.currentAnalysisStep - 1].active = false;
        }
        if (this.currentAnalysisStep < this.analysisSteps.length) {
          this.analysisSteps[this.currentAnalysisStep].active = true;
          this.currentAnalysisStep++;
          setTimeout(updateStep, 1200);
        }
      };
      updateStep();
    },

    resetAnalysisProgress() {
      this.currentAnalysisStep = 0;
      this.analysisSteps.forEach(step => {
        step.done = false;
        step.active = false;
      });
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
      const weights = {
        profile: 30,
        knowledgeContext: 25,
        resourceType: 25,
        qualityControl: 20
      };

      const profileScore = data.description ? 90 : 70;
      const knowledgeContextScore = data.ingredients ? 92 : 65;

      let resourceScore = 72;
      const foundationalResources = ['检修手册', '故障图谱', '讲解文档', '思维导图'];
      const practiceResources = ['相似案例', '作业流程'];
      const extendedResources = ['风险清单', '视频脚本'];

      if (foundationalResources.includes(data.cookingMethod)) resourceScore = 92;
      else if (practiceResources.includes(data.cookingMethod)) resourceScore = 88;
      else if (extendedResources.includes(data.cookingMethod)) resourceScore = 82;

      let qualityScore = 76;
      if (data.deliveryTime && parseInt(data.deliveryTime) > 0) {
        const time = parseInt(data.deliveryTime);
        qualityScore = time <= 5 ? 88 : time <= 15 ? 82 : 74;
      }
      if (['知识库引用', '来源标注', '人工审核', '风险复核', '教师审核', '题目回测'].includes(data.packageMaterial)) qualityScore += 10;
      if (data.perishable) qualityScore += 4;

      const score = Math.round(
        (profileScore * weights.profile +
         knowledgeContextScore * weights.knowledgeContext +
         resourceScore * weights.resourceType +
         Math.min(100, qualityScore) * weights.qualityControl) / 100
      );

      return Math.min(100, Math.max(0, score));
    },

    generateSuggestions(data, score) {
      const suggestions = [];

      if (data.cookingMethod === '作业流程' || data.cookingMethod === '风险清单') {
        suggestions.push('该资料对现场信息要求较高，建议先补充设备型号、故障照片和检修等级');
      }

      if (data.perishable && data.deliveryTime && parseInt(data.deliveryTime) > 30) {
        suggestions.push('该故障属于高风险场景，建议缩短生成链路并加强风险复核');
      }

      if (data.packageMaterial === '人工审核' || data.packageMaterial === '风险复核') {
        suggestions.push('该资料已标记为人工审核优先，建议在发布前保留来源依据');
      }

      if (score < 60) {
        suggestions.push('该资料适配度较低，建议补充设备型号、故障现象和现场约束后重新生成');
      } else if (score >= 80) {
        suggestions.push('该资料检修适配度较高，可以加入标准作业路径继续使用');
      }

      return suggestions.length > 0 ? suggestions : ['建议结合设备画像继续优化检修资料推送'];
    },

    saveManualInput() {
      if (!this.manualInputData.foodName.trim()) {
        uni.showToast({ title: '请输入设备型号或故障现象', icon: 'none' });
        return;
      }

      const nowTs = Date.now();
      const score = this.calculateHealthScore(this.manualInputData);
      const savedData = {
        ...this.manualInputData,
        score,
        suggestions: this.generateSuggestions(this.manualInputData, score),
        savedAt: nowTs,
        date: this.formatHistoryDate(nowTs)
      };

      let savedList = uni.getStorageSync('manualLearningResourceList') || [];
      savedList.push(savedData);
      uni.setStorageSync('manualLearningResourceList', savedList);

      uni.showToast({ title: '保存成功', icon: 'success' });
      this.resetManualInput();
      this.manualInputMode = false;
    },

    savePreferences() {
      uni.showToast({ title: '偏好已保存', icon: 'success' });
      uni.setStorageSync('userPreferences', this.preferences);
    },

    // ── 语音唤醒功能 ──
    toggleWakeEnabled() {
      this.wakeEnabled = !this.wakeEnabled
      if (this.wakeEnabled) {
        this.startWakeListening()
      } else {
        this.stopWakeListening()
      }
    },

    startWakeListening() {
      if (this.wakeListening) return
      this.wakeListening = true
      this._doWakeListen()
    },

    stopWakeListening() {
      this.wakeListening = false
      if (this.wakeCheckTimer) {
        clearTimeout(this.wakeCheckTimer)
        this.wakeCheckTimer = null
      }
    },

    async _doWakeListen() {
      if (!this.wakeListening || !this.wakeEnabled) return
      try {
        const controller = createVoiceInputController({
          service: 'tuantuan',
          onStateChange: () => {},
          onTranscribed: (text) => {
            this.checkWakeWord(text)
          },
          onError: () => {}
        })
        // 录制 3 秒后自动停止并检查
        await controller.startRecording()
        setTimeout(async () => {
          try { await controller.stopRecording() } catch (e) {}
          // 下一轮监听
          if (this.wakeListening && this.wakeEnabled) {
            this.wakeCheckTimer = setTimeout(() => this._doWakeListen(), 500)
          }
        }, 3000)
      } catch (e) {
        // 出错后稍等再重试
        if (this.wakeListening && this.wakeEnabled) {
          this.wakeCheckTimer = setTimeout(() => this._doWakeListen(), 2000)
        }
      }
    },

    checkWakeWord(text) {
      if (!text) return
      const cleaned = text.replace(/[\s，。！？、]/g, '').toLowerCase()
      for (const w of this.wakeWords) {
        if (cleaned.includes(w.keyword.toLowerCase())) {
          uni.showToast({ title: `🎤 已唤醒："${w.keyword}"`, icon: 'none', duration: 1500 })
          this.executeWakeAction(w.action)
          return
        }
      }
    },

    executeWakeAction(action) {
      switch (action) {
        case 'search':
          this.confirmStartSearch()
          break
        case 'manual':
          this.resourceRequest.need = '需要检索检修手册、设备说明书和检修规程条款。'
          this.confirmStartSearch()
          break
        case 'case':
          this.resourceRequest.need = '需要检索相似检修案例、历史处置经验和故障处理结论。'
          this.confirmStartSearch()
          break
        case 'workflow':
          this.resourceRequest.need = '需要检索标准检修作业流程、合规校验和安全操作步骤。'
          this.confirmStartSearch()
          break
        case 'camera':
          this.chooseImage()
          break
        default:
          break
      }
    }
  }
}
</script>

<style scoped>
/* ===== 全局 ===== */
.page-container {
  min-height: 100vh;
  background: #f0fdfa;
  padding-top: calc(44px + constant(safe-area-inset-top));
  padding-top: calc(44px + env(safe-area-inset-top));
}

.section-mode {
  display: flex;
  flex-direction: column;
}

/* ===== HERO BANNER ===== */
.hero-banner {
  background: linear-gradient(135deg, #99f6e4 0%, #a7f3d0 100%);
  margin: 24rpx 32rpx 0;
  border-radius: 32rpx;
  padding: 36rpx 32rpx 32rpx;
  display: flex;
  flex-direction: column;
  gap: 18rpx;
  position: relative;
  overflow: hidden;
}

.hero-banner::before {
  content: '';
  position: absolute;
  top: -80rpx;
  right: -40rpx;
  width: 260rpx;
  height: 260rpx;
  background: radial-gradient(circle, rgba(255,255,255,0.2) 0%, transparent 70%);
  border-radius: 50%;
}

.hero-top-row {
  display: flex;
  align-items: center;
  gap: 24rpx;
}

.hero-avatar-wrap {
  position: relative;
  flex-shrink: 0;
}

.hero-avatar {
  width: 96rpx;
  height: 96rpx;
  border-radius: 24rpx;
  display: block;
  box-shadow: 0 8rpx 24rpx rgba(0,0,0,0.15);
}

.hero-status-dot {
  position: absolute;
  bottom: -2rpx;
  right: -2rpx;
  width: 20rpx;
  height: 20rpx;
  background: #6ee7b7;
  border-radius: 50%;
  border: 4rpx solid #99f6e4;
}

.hero-info {
  flex: 1;
  min-width: 0;
}

.hero-name {
  font-size: 34rpx;
  font-weight: 800;
  color: #134e4a;
  display: block;
}

.hero-tags {
  display: flex;
  gap: 10rpx;
  margin-top: 12rpx;
  flex-wrap: wrap;
}

.hero-tag {
  font-size: 20rpx;
  color: #115e59;
  padding: 4rpx 14rpx;
  border-radius: 8rpx;
  background: rgba(255,255,255,0.5);
  font-weight: 500;
}

.hero-desc {
  font-size: 22rpx;
  color: #5f7a78;
  line-height: 1.6;
}

/* ===== 检索输入区 ===== */
.source-card {
  background: #ffffff;
  margin: 20rpx 32rpx 0;
  border-radius: 28rpx;
  padding: 32rpx;
  box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.04);
}

/* 已选图片预览条 */
.pending-image-bar {
  display: flex;
  align-items: center;
  gap: 16rpx;
  padding: 16rpx;
  margin-bottom: 16rpx;
  background: #ccfbf1;
  border-radius: 16rpx;
}

.pending-image-thumb {
  width: 80rpx;
  height: 80rpx;
  border-radius: 12rpx;
  flex-shrink: 0;
}

.pending-image-name {
  flex: 1;
  font-size: 24rpx;
  color: #115e59;
  font-weight: 600;
}

.pending-image-remove {
  width: 48rpx;
  height: 48rpx;
  border-radius: 50%;
  background: rgba(0,0,0,0.06);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.pending-image-remove text {
  font-size: 24rpx;
  color: #5f7a78;
}

.source-prompt-box {
  margin-top: 16rpx;
  background: #f5fffe;
  border-radius: 20rpx;
  border: 2rpx solid #d1fae5;
  padding: 24rpx;
}

.source-prompt {
  width: 100%;
  min-height: 120rpx;
  font-size: 28rpx;
  color: #134e4a;
  line-height: 1.6;
}

.source-voice-row {
  display: flex;
  justify-content: flex-end;
  margin-top: 12rpx;
}

.source-voice-btn {
  display: inline-flex;
  align-items: center;
  gap: 10rpx;
  padding: 10rpx 24rpx;
  border-radius: 24rpx;
  background: #f0fdfa;
  border: 1rpx solid #d1fae5;
  transition: all 0.2s ease;
}

.source-voice-btn:active {
  transform: scale(0.95);
}

.source-voice-btn.active {
  background: #14b8a6;
  border-color: transparent;
  animation: voice-pulse 1.2s ease-in-out infinite;
}

@keyframes voice-pulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(30,41,59,0.2); }
  50% { box-shadow: 0 0 0 12rpx rgba(30,41,59,0.08); }
}

.source-mic-icon {
  position: relative;
  width: 28rpx;
  height: 28rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.mic-bar {
  width: 14rpx;
  height: 20rpx;
  background: #5f7a78;
  border-radius: 7rpx;
}

.source-voice-btn.active .mic-bar {
  background: #fff;
}

.mic-arc {
  position: absolute;
  bottom: 2rpx;
  width: 22rpx;
  height: 10rpx;
  border: 3rpx solid #5f7a78;
  border-top: none;
  border-radius: 0 0 11rpx 11rpx;
}

.source-voice-btn.active .mic-arc {
  border-color: #fff;
}

.source-voice-text {
  font-size: 22rpx;
  color: #5f7a78;
  font-weight: 600;
}

.source-voice-btn.active .source-voice-text {
  color: #fff;
}

/* 主检索按钮 */
.search-main-btn {
  margin-top: 20rpx;
  height: 88rpx;
  border-radius: 20rpx;
  background: #14b8a6;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.search-main-btn:active {
  transform: scale(0.98);
  background: #0d9488;
}

.search-main-btn-text {
  font-size: 30rpx;
  font-weight: 700;
  color: #fff;
  letter-spacing: 2rpx;
}

/* 详细输入折叠开关 */
.detail-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8rpx;
  margin-top: 16rpx;
  padding: 14rpx 0;
}

.detail-toggle-text {
  font-size: 24rpx;
  color: #9ca3af;
  font-weight: 500;
}

.detail-toggle-arrow {
  font-size: 20rpx;
  color: #d1d5db;
}

/* 详细输入折叠面板 */
.detail-panel {
  margin-top: 8rpx;
  padding-top: 20rpx;
  border-top: 1rpx solid #f0fdfa;
}

.detail-dropzone {
  display: flex;
  align-items: center;
  gap: 12rpx;
  padding: 20rpx 24rpx;
  border: 2rpx dashed #d1fae5;
  border-radius: 16rpx;
  background: #f5fffe;
  margin-bottom: 20rpx;
  transition: all 0.2s ease;
}

.detail-dropzone:active {
  border-color: #9ca3af;
  background: #f0fdfa;
}

.detail-dropzone-icon {
  font-size: 36rpx;
}

.detail-dropzone-text {
  font-size: 26rpx;
  color: #475569;
  font-weight: 600;
}

.resource-chip-row {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
  margin-top: 20rpx;
}

.resource-type-item {
  display: inline-flex;
  align-items: center;
  gap: 8rpx;
  padding: 12rpx 18rpx;
  border-radius: 12rpx;
  background: #f0fdfa;
}

.resource-type-icon {
  font-size: 24rpx;
}

.resource-type-name {
  font-size: 22rpx;
  color: #475569;
  font-weight: 600;
}

/* ===== 功能卡片组 ===== */
.cards-group {
  padding: 24rpx 32rpx 40rpx;
  display: flex;
  flex-direction: column;
  gap: 24rpx;
}

.func-card {
  background: #ffffff;
  border-radius: 28rpx;
  padding: 32rpx;
  box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.04);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24rpx;
  padding-bottom: 20rpx;
  border-bottom: 1rpx solid #f0fdfa;
}

.card-title-box {
  display: flex;
  align-items: center;
  gap: 12rpx;
}

.card-dot {
  width: 12rpx;
  height: 12rpx;
  border-radius: 4rpx;
}
.orange-dot { background: #f59e0b; }
.blue-dot   { background: #3b82f6; }
.purple-dot { background: #8b5cf6; }

.card-title {
  font-size: 30rpx;
  font-weight: 800;
  color: #14b8a6;
}

.card-link { font-size: 24rpx; color: #94a3b8; font-weight: 500; }

/* 历史列表 */
.history-empty {
  padding: 24rpx 0;
  text-align: center;
}
.empty-hint { font-size: 24rpx; color: #94a3b8; }

.history-item {
  display: flex;
  align-items: center;
  gap: 16rpx;
  padding: 20rpx;
  background: #f5fffe;
  border-radius: 16rpx;
  margin-bottom: 12rpx;
}
.history-item:last-child { margin-bottom: 0; }

.history-icon-box {
  width: 64rpx;
  height: 64rpx;
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  border-radius: 16rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  box-shadow: 0 4rpx 12rpx rgba(249, 115, 22, 0.15);
}
.history-icon { font-size: 32rpx; }
.history-thumb {
  width: 64rpx;
  height: 64rpx;
  border-radius: 16rpx;
}

.history-info { flex: 1; }
.history-name { font-size: 26rpx; color: #14b8a6; font-weight: 700; display: block; }
.history-date { font-size: 20rpx; color: #94a3b8; display: block; margin-top: 6rpx; }

.score-pill {
  font-size: 22rpx;
  font-weight: 700;
  padding: 8rpx 20rpx;
  border-radius: 100rpx;
}

/* 快捷功能列表 */
.quick-func-list {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.quick-func-item {
  display: flex;
  align-items: center;
  gap: 20rpx;
  padding: 20rpx 24rpx;
  border-radius: 20rpx;
  background: #f5fffe;
  transition: all 0.15s ease;
}

.quick-func-item:active {
  transform: scale(0.98);
  background: #f0fdfa;
}

.quick-func-icon {
  width: 80rpx;
  height: 80rpx;
  border-radius: 22rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 6rpx 16rpx rgba(0,0,0,0.08);
}

.quick-func-img {
  width: 48rpx;
  height: 48rpx;
}

.quick-func-emoji {
  font-size: 36rpx;
}

.quick-func-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 6rpx;
}

.quick-func-name {
  font-size: 28rpx;
  font-weight: 700;
  color: #14b8a6;
}

.quick-func-desc {
  font-size: 22rpx;
  color: #64748b;
  line-height: 1.4;
}

.quick-func-arrow {
  font-size: 36rpx;
  color: #94a3b8;
  flex-shrink: 0;
  font-weight: 300;
}

/* ===== 分析中 ===== */
.center-mode {
  min-height: 100vh;
  align-items: center;
  justify-content: center;
  background: linear-gradient(180deg, #f0f4f8 0%, #e0e7ff 100%);
}

.analyzing-card {
  background: #ffffff;
  border-radius: 40rpx;
  padding: 80rpx 60rpx;
  margin: 40rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  box-shadow: 0 16rpx 48rpx rgba(0,0,0,0.08);
  border: 1rpx solid rgba(255,255,255,0.8);
}

.analyzing-ring {
  position: relative;
  width: 240rpx;
  height: 240rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 48rpx;
}

.ring {
  position: absolute;
  border-radius: 50%;
  border: 4rpx solid rgba(59,130,246,0.15);
  animation: spin-ring 3s linear infinite;
}
.r1 { width: 240rpx; height: 240rpx; border-top-color: #5eead4; }
.r2 { width: 200rpx; height: 200rpx; border-right-color: #14b8a6; animation-duration: 2s; animation-direction: reverse; }
.r3 { width: 160rpx; height: 160rpx; border-bottom-color: #64748b; animation-duration: 1.5s; }

.analyzing-emoji {
  font-size: 80rpx;
  animation: bounce 1s infinite alternate;
  position: relative;
  z-index: 2;
}

.analyzing-title {
  font-size: 36rpx;
  font-weight: 800;
  color: #14b8a6;
  margin-bottom: 16rpx;
}

.analyzing-sub {
  font-size: 24rpx;
  color: #64748b;
  margin-bottom: 40rpx;
}

.analyzing-dots { display: flex; gap: 20rpx; }
.dot {
  width: 20rpx; height: 20rpx; border-radius: 50%; background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
  animation: dot-flash 1.2s infinite;
  box-shadow: 0 4rpx 12rpx rgba(34, 197, 94, 0.3);
}
.dot2 { animation-delay: 0.2s; }
.dot3 { animation-delay: 0.4s; }

/* ===== 设备类型快速选择 ===== */
.device-category-row {
  margin-top: 20rpx;
  padding: 0;
}

.device-category-row .card-header {
  padding: 0 0 16rpx 0;
}

.device-category-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16rpx;
}

.device-category-card {
  display: flex;
  flex-direction: column;
  gap: 8rpx;
  padding: 20rpx 16rpx;
  border-radius: 20rpx;
  border: 1rpx solid;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.device-category-card:active {
  transform: scale(0.98);
  box-shadow: 0 8rpx 24rpx rgba(0,0,0,0.1);
}

.device-category-icon {
  font-size: 32rpx;
}

.device-category-name {
  font-size: 26rpx;
  font-weight: 700;
  color: #14b8a6;
}

.device-category-devices {
  font-size: 20rpx;
  color: #64748b;
  line-height: 1.4;
}

/* ===== 检索进度指示 ===== */
.analysis-progress {
  width: 100%;
  margin-top: 40rpx;
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.analysis-step {
  display: flex;
  align-items: center;
  gap: 16rpx;
  padding: 16rpx 20rpx;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-radius: 16rpx;
  border: 1rpx solid #e2e8f0;
  transition: all 0.3s ease;
}

.analysis-step.active {
  background: linear-gradient(135deg, #eff6ff 0%, #e0e8d8 100%);
  border-color: #d5e0d0;
  box-shadow: 0 4rpx 12rpx rgba(59, 130, 246, 0.15);
}

.analysis-step.done {
  background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
  border-color: #bbf7d0;
}

.step-icon-wrap {
  position: relative;
  width: 48rpx;
  height: 48rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #e2e8f0;
  border-radius: 12rpx;
  flex-shrink: 0;
}

.analysis-step.active .step-icon-wrap {
  background: linear-gradient(135deg, #5eead4 0%, #14b8a6 100%);
  box-shadow: 0 4rpx 12rpx rgba(59, 130, 246, 0.3);
}

.analysis-step.done .step-icon-wrap {
  background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
}

.step-icon {
  font-size: 24rpx;
}

.step-check {
  position: absolute;
  top: -6rpx;
  right: -6rpx;
  width: 24rpx;
  height: 24rpx;
  font-size: 16rpx;
  font-weight: 800;
  color: #fff;
  background: #16a34a;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2rpx solid #fff;
}

.step-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4rpx;
}

.step-title {
  font-size: 24rpx;
  font-weight: 700;
  color: #94a3b8;
}

.analysis-step.active .step-title {
  color: #1e40af;
}

.analysis-step.done .step-title {
  color: #15803d;
}

.step-desc {
  font-size: 20rpx;
  color: #94a3b8;
}

.analysis-step.active .step-desc,
.analysis-step.done .step-desc {
  color: #64748b;
}

.step-status {
  flex-shrink: 0;
}

.status-done {
  font-size: 20rpx;
  font-weight: 700;
  color: #15803d;
  background: #bbf7d0;
  padding: 6rpx 14rpx;
  border-radius: 100rpx;
}

.status-active {
  font-size: 20rpx;
  font-weight: 700;
  color: #1e40af;
  background: #d5e0d0;
  padding: 6rpx 14rpx;
  border-radius: 100rpx;
}

.status-wait {
  font-size: 20rpx;
  color: #94a3b8;
  background: #e2e8f0;
  padding: 6rpx 14rpx;
  border-radius: 100rpx;
}

/* ===== 结果 ===== */
.result-scroll {
  height: 100vh;
}

.result-hero {
  position: relative;
  background: linear-gradient(145deg, #0d9488 0%, #5eead4 70%, #64748b 100%);
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

/* ===== 检索报告 ===== */
.retrieval-report {
  padding-bottom: 40rpx;
}

.report-header {
  background: linear-gradient(135deg, #0d9488 0%, #5eead4 70%, #64748b 100%);
  padding: 40rpx 32rpx;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 24rpx;
  position: relative;
  overflow: hidden;
  z-index: 100;
}

.report-back-btn {
  position: absolute;
  top: 20rpx;
  left: 20rpx;
  width: 56rpx;
  height: 56rpx;
  background: rgba(255,255,255,0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(10px);
  border: 1rpx solid rgba(255,255,255,0.3);
  transition: all 0.2s ease;
}

.report-back-btn:active {
  background: rgba(255,255,255,0.3);
  transform: scale(0.95);
}

.back-icon {
  font-size: 32rpx;
  color: #fff;
  font-weight: 700;
}

.report-title-block {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12rpx;
  padding-left: 70rpx;
}

.report-title-block .voice-play-btn {
  align-self: flex-start;
  margin-top: 4rpx;
}

.report-kicker {
  font-size: 22rpx;
  color: rgba(255,255,255,0.8);
  font-weight: 600;
}

.report-title {
  font-size: 36rpx;
  font-weight: 800;
  color: #fff;
}

.report-desc {
  font-size: 24rpx;
  color: rgba(255,255,255,0.85);
  line-height: 1.5;
}

.match-panel {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8rpx;
  background: rgba(255,255,255,0.15);
  border-radius: 24rpx;
  padding: 20rpx 24rpx;
  border: 1rpx solid rgba(255,255,255,0.2);
}

.match-label {
  font-size: 20rpx;
  color: rgba(255,255,255,0.8);
}

.match-score {
  font-size: 48rpx;
  font-weight: 900;
  color: #fff;
  line-height: 1;
}

.match-status {
  font-size: 20rpx;
  color: #FEF3C7;
  font-weight: 700;
}

/* 查询摘要 */
.query-summary {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
  padding: 24rpx 32rpx;
  background: linear-gradient(135deg, #f0f9ff 0%, #ecfeff 100%);
}

.query-item {
  display: flex;
  align-items: center;
  gap: 8rpx;
  background: #fff;
  padding: 12rpx 20rpx;
  border-radius: 20rpx;
  border: 1rpx solid #d5e0d0;
}

.query-label {
  font-size: 22rpx;
  color: #64748b;
  font-weight: 500;
}

.query-value {
  font-size: 22rpx;
  color: #14b8a6;
  font-weight: 600;
}

/* 证据条 */
.evidence-strip {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12rpx;
  padding: 24rpx 32rpx;
  background: #fff;
}

.evidence-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8rpx;
  padding: 20rpx 12rpx;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-radius: 20rpx;
  border: 1rpx solid #e2e8f0;
}

.evidence-top {
  display: flex;
  align-items: center;
  gap: 6rpx;
}

.evidence-icon {
  font-size: 24rpx;
}

.evidence-status {
  font-size: 18rpx;
  font-weight: 700;
}

.evidence-status.risk-low { color: #059669; }
.evidence-status.risk-mid { color: #d97706; }
.evidence-status.risk-high { color: #dc2626; }

.evidence-label {
  font-size: 18rpx;
  color: #64748b;
}

.evidence-value {
  font-size: 24rpx;
  color: #14b8a6;
  font-weight: 800;
}

/* 手册列表 */
.manual-list {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.manual-card {
  display: flex;
  gap: 20rpx;
  padding: 20rpx;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-radius: 20rpx;
  border: 1rpx solid #e2e8f0;
}

.manual-icon {
  width: 64rpx;
  height: 64rpx;
  font-size: 36rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #e0e8d8 0%, #d5e0d0 100%);
  border-radius: 16rpx;
  flex-shrink: 0;
}

.manual-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 10rpx;
}

.manual-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16rpx;
}

.manual-title {
  font-size: 28rpx;
  font-weight: 700;
  color: #14b8a6;
}

.confidence-chip {
  font-size: 20rpx;
  font-weight: 700;
  color: #059669;
  background: #d1fae5;
  padding: 6rpx 16rpx;
  border-radius: 100rpx;
  flex-shrink: 0;
}

.manual-desc {
  font-size: 24rpx;
  color: #64748b;
  line-height: 1.5;
}

.manual-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8rpx;
}

.manual-tag {
  font-size: 20rpx;
  color: #475569;
  background: #e2e8f0;
  padding: 4rpx 12rpx;
  border-radius: 100rpx;
}

/* 案例列表 */
.case-list {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.case-card {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
  padding: 20rpx;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-radius: 20rpx;
  border: 1rpx solid #e2e8f0;
}

.case-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16rpx;
}

.case-title {
  font-size: 28rpx;
  font-weight: 700;
  color: #14b8a6;
}

.case-chip {
  font-size: 20rpx;
  font-weight: 700;
  color: #7c3aed;
  background: #ede9fe;
  padding: 6rpx 16rpx;
  border-radius: 100rpx;
  flex-shrink: 0;
}

.case-desc {
  font-size: 24rpx;
  color: #64748b;
  line-height: 1.5;
}

.case-meta-row {
  display: flex;
  gap: 20rpx;
}

.case-meta {
  font-size: 22rpx;
  color: #475569;
  background: #f1f5f9;
  padding: 8rpx 16rpx;
  border-radius: 12rpx;
}

/* 工作流程 */
.workflow-list {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.workflow-step {
  display: flex;
  gap: 20rpx;
  padding: 20rpx;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-radius: 20rpx;
  border: 1rpx solid #e2e8f0;
}

.step-index {
  width: 56rpx;
  height: 56rpx;
  font-size: 28rpx;
  font-weight: 800;
  color: #fff;
  background: linear-gradient(135deg, #5eead4 0%, #14b8a6 100%);
  border-radius: 16rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 4rpx 12rpx rgba(37, 99, 235, 0.3);
}

.step-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 10rpx;
}

.step-title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16rpx;
}

.step-title {
  font-size: 28rpx;
  font-weight: 700;
  color: #14b8a6;
}

.step-state {
  font-size: 20rpx;
  font-weight: 700;
  padding: 6rpx 16rpx;
  border-radius: 100rpx;
  flex-shrink: 0;
}

.step-state.risk-low { color: #059669; background: #d1fae5; }
.step-state.risk-mid { color: #d97706; background: #fef3c7; }
.step-state.risk-high { color: #dc2626; background: #fee2e2; }

.step-desc {
  font-size: 24rpx;
  color: #64748b;
  line-height: 1.5;
}

.step-check {
  font-size: 22rpx;
  color: #475569;
  background: #e2e8f0;
  padding: 8rpx 16rpx;
  border-radius: 12rpx;
  align-self: flex-start;
}

/* 知识图谱关联 */
.graph-link-list {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

.graph-link {
  display: flex;
  align-items: center;
  gap: 12rpx;
  padding: 16rpx 20rpx;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-radius: 16rpx;
  border: 1rpx solid #e2e8f0;
}

.graph-dot {
  width: 12rpx;
  height: 12rpx;
  background: linear-gradient(135deg, #5eead4 0%, #14b8a6 100%);
  border-radius: 50%;
  flex-shrink: 0;
}

.graph-name {
  flex: 1;
  font-size: 26rpx;
  color: #14b8a6;
  font-weight: 600;
}

.graph-relation {
  font-size: 22rpx;
  color: #64748b;
  background: #e2e8f0;
  padding: 6rpx 14rpx;
  border-radius: 100rpx;
}

/* 人工复核 */
.correction-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16rpx;
}

.correction-card {
  display: flex;
  flex-direction: column;
  gap: 10rpx;
  padding: 20rpx;
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  border-radius: 20rpx;
  border: 1rpx solid #fcd34d;
}

.correction-title {
  font-size: 26rpx;
  font-weight: 700;
  color: #115e59;
}

.correction-desc {
  font-size: 22rpx;
  color: #a16207;
  line-height: 1.5;
}

/* 结果卡片 */
.result-section {
  background: #FFFFFF;
  margin: 0 24rpx 20rpx;
  border-radius: 12rpx;
  padding: 28rpx;
  box-shadow: 0 4rpx 16rpx rgba(0,0,0,0.04);
}

.section-head {
  display: flex;
  align-items: center;
  gap: 14rpx;
  margin-bottom: 24rpx;
  padding-bottom: 16rpx;
  border-bottom: 1rpx solid #E5E7EB;
}

.section-head .voice-play-btn {
  margin-left: auto;
  flex-shrink: 0;
}

.section-accent {
  width: 8rpx;
  height: 36rpx;
  background: linear-gradient(180deg, #14b8a6, #5eead4);
  border-radius: 8rpx;
}

.section-title {
  font-size: 30rpx;
  font-weight: 800;
  color: #1F2937;
}

.section-avatar {
  width: 52rpx;
  height: 52rpx;
  border-radius: 50%;
  display: block;
}

/* 多维评估 */
.dim-list { display: flex; flex-direction: column; gap: 20rpx; }

.dim-item {}

.dim-top {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10rpx;
}

.dim-name { font-size: 26rpx; color: #6B7280; }
.dim-val  { font-size: 26rpx; font-weight: bold; }

.dim-bar-track {
  height: 12rpx;
  background: #E5E7EB;
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
  background: #f0fdfa;
  color: #115e59;
  border-top-left-radius: 6rpx;
}

.bubble-user {
  background: linear-gradient(135deg, #14b8a6, #5eead4, #0d9488);
  color: #fff;
  border-top-right-radius: 6rpx;
}

.bubble-text { display: block; }

.chat-input-row {
  display: flex;
  gap: 14rpx;
  align-items: center;
  background: #f5fffe;
  border-radius: 16rpx;
  padding: 10rpx 10rpx 10rpx 20rpx;
  border: 1rpx solid #d1fae5;
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
  background: #F3F4F6;
  border-radius: 32rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  border: 1rpx solid #E5E7EB;
}

.voice-btn.active {
  background: linear-gradient(135deg, #5eead4, #0d9488);
  border-color: transparent;
}

.voice-btn-text {
  font-size: 22rpx;
  color: #5eead4;
  font-weight: 600;
}

.voice-btn.active .voice-btn-text {
  color: #fff;
}

.send-btn {
  width: 64rpx;
  height: 64rpx;
  background: #14b8a6;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4rpx 12rpx rgba(30,41,59,0.2);
  flex-shrink: 0;
}

.send-arrow { font-size: 26rpx; color: #fff; }

/* 资源清单 */
.nutrition-list { display: flex; flex-direction: column; gap: 16rpx; }

.nutrition-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16rpx 0;
  border-bottom: 1rpx solid #E5E7EB;
}

.nutrition-item:last-child { border-bottom: none; }

.nutrition-label { font-size: 26rpx; color: #6B7280; }

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

/* 检修建议 */
.suggestions-list { display: flex; flex-direction: column; gap: 16rpx; }

.sug-item {
  display: flex;
  gap: 16rpx;
  align-items: flex-start;
  background: #F8FAFC;
  border-radius: 16rpx;
  padding: 16rpx 20rpx;
}

.sug-icon { font-size: 28rpx; flex-shrink: 0; }
.sug-text { font-size: 26rpx; color: #4B5563; line-height: 1.6; flex: 1; }

/* 底部按钮 */
.bottom-actions {
  padding: 10rpx 30rpx 60rpx;
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.retake-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 14rpx;
  background: linear-gradient(135deg, #14b8a6, #0d9488);
  border-radius: 40rpx;
  padding: 28rpx;
  box-shadow: 0 8rpx 24rpx rgba(37,99,235,0.35);
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
  border-bottom: 1rpx solid #E5E7EB;
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
  color: #1F2937;
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
  color: #1F2937;
  text-align: center;
  padding: 16rpx 0 20rpx;
}

.drawer-scroll { flex: 1; padding: 0 30rpx 30rpx; }

.drawer-item {
  display: flex;
  align-items: center;
  gap: 20rpx;
  padding: 24rpx 0;
  border-bottom: 1rpx solid #E5E7EB;
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

/* ===== 资料查询样式 ===== */
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
  color: #1F2937;
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
  border-bottom: 1rpx solid #E5E7EB;
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
  color: #1F2937;
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
  background: #FFFFFF;
  border-radius: 8rpx;
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
  color: #1F2937;
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
  border-bottom: 1rpx solid #E5E7EB;
}

.setting-item:last-child {
  border-bottom: none;
}

.setting-label {
  font-size: 28rpx;
  color: #1F2937;
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

/* ===== 检修周报样式 ===== */
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
  color: #1F2937;
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
  background: #F8FAFC;
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
  color: #1F2937;
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
  color: #5eead4;
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

/* ===== 设备型号 & 检修等级 ===== */
.equip-model-row, .repair-level-row { margin-top: 16rpx; }
.equip-label { font-size: 24rpx; color: #5f7a78; font-weight: 600; display: block; margin-bottom: 8rpx; }
.equip-input {
  width: 100%;
  height: 72rpx;
  background: #f5fffe;
  border: 2rpx solid #d1fae5;
  border-radius: 12rpx;
  padding: 0 20rpx;
  font-size: 26rpx;
  color: #134e4a;
  box-sizing: border-box;
}
.level-chips { display: flex; gap: 12rpx; flex-wrap: wrap; }
.level-chip {
  padding: 10rpx 24rpx;
  background: #f0fdfa;
  border: 2rpx solid transparent;
  border-radius: 12rpx;
  font-size: 24rpx;
  color: #5f7a78;
}
.level-chip.active {
  background: #14b8a6;
  border-color: #14b8a6;
  color: #fff;
  font-weight: 600;
}

/* ===== 热门搜索 ===== */
.hot-search-row { margin-top: 20rpx; }
.hot-search-label { font-size: 22rpx; color: #9CA3AF; font-weight: 500; display: block; margin-bottom: 12rpx; }
.hot-search-tags { display: flex; gap: 12rpx; flex-wrap: wrap; }
.hot-search-tag {
  padding: 10rpx 20rpx;
  background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%);
  border: 2rpx solid #FCD34D;
  border-radius: 20rpx;
  font-size: 22rpx;
  color: #92400E;
  font-weight: 500;
  transition: all 0.2s ease;
}
.hot-search-tag:active {
  transform: scale(0.96);
  background: linear-gradient(135deg, #FDE68A 0%, #FBBF24 100%);
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

/* ===== 语音唤醒 ===== */
.wake-card {
  background: #ffffff;
  margin: 16rpx 32rpx 0;
  border-radius: 28rpx;
  padding: 28rpx 32rpx;
  box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.04);
  border: 2rpx solid #d1fae5;
}

.wake-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.wake-title-row {
  display: flex;
  align-items: center;
  gap: 12rpx;
  flex: 1;
}

.wake-icon { font-size: 32rpx; }

.wake-title {
  font-size: 30rpx;
  font-weight: 800;
  color: #14b8a6;
}

.wake-status {
  display: flex;
  align-items: center;
  gap: 6rpx;
  margin-left: 12rpx;
}

.wake-dot {
  width: 12rpx;
  height: 12rpx;
  border-radius: 50%;
  background: #cbd5e1;
}

.wake-status.active .wake-dot {
  background: #22c55e;
  box-shadow: 0 0 8rpx rgba(34,197,94,0.5);
  animation: wake-pulse 1.5s ease-in-out infinite;
}

@keyframes wake-pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(1.4); }
}

.wake-status-text {
  font-size: 22rpx;
  color: #94a3b8;
  font-weight: 500;
}

.wake-status.active .wake-status-text {
  color: #22c55e;
  font-weight: 700;
}

.wake-switch {
  width: 88rpx;
  height: 48rpx;
  border-radius: 24rpx;
  background: #cbd5e1;
  padding: 4rpx;
  transition: background 0.3s ease;
  flex-shrink: 0;
}

.wake-switch.on {
  background: linear-gradient(135deg, #14b8a6, #22c55e);
}

.wake-switch-thumb {
  width: 40rpx;
  height: 40rpx;
  border-radius: 50%;
  background: #ffffff;
  box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.15);
  transition: transform 0.3s ease;
}

.wake-switch.on .wake-switch-thumb {
  transform: translateX(40rpx);
}

.wake-body {
  margin-top: 20rpx;
  padding-top: 20rpx;
  border-top: 1rpx solid #f0fdfa;
}

.wake-hint {
  font-size: 24rpx;
  color: #64748b;
  display: block;
  margin-bottom: 16rpx;
}

.wake-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
}

.wake-chip {
  display: flex;
  flex-direction: column;
  gap: 4rpx;
  padding: 14rpx 20rpx;
  background: linear-gradient(135deg, #f0fdfa 0%, #ccfbf1 100%);
  border: 2rpx solid #99f6e4;
  border-radius: 16rpx;
  transition: all 0.2s ease;
}

.wake-chip:active {
  transform: scale(0.95);
  background: linear-gradient(135deg, #ccfbf1 0%, #99f6e4 100%);
}

.wake-chip.hit {
  animation: chip-hit 0.3s ease;
}

@keyframes chip-hit {
  0% { transform: scale(1); }
  50% { transform: scale(1.05); box-shadow: 0 4rpx 16rpx rgba(20,184,166,0.3); }
  100% { transform: scale(1); }
}

.wake-chip-key {
  font-size: 26rpx;
  font-weight: 700;
  color: #0d9488;
}

.wake-chip-desc {
  font-size: 20rpx;
  color: #64748b;
}
</style>
