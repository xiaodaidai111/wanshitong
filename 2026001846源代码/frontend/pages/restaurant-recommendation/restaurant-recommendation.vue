<template>
  <view class="page-root">
    <!-- 顶部导航栏 -->
    <view class="kb-navbar" :style="{ paddingTop: statusBarHeight + 'px' }">
      <view class="kb-navbar-inner">
        <view class="kb-nav-left" @click="sideCollapsed = !sideCollapsed">
          <text class="kb-nav-menu">☰</text>
        </view>
        <view class="kb-nav-title">知识库</view>
        <view class="kb-nav-right"></view>
      </view>
    </view>

    <!-- 侧边栏遮罩 -->
    <view class="sidebar-mask" v-if="!sideCollapsed" @click="sideCollapsed = true"></view>

    <!-- 展开态：侧边栏 -->
    <view v-show="!sideCollapsed" class="sidebar">
      <view class="side-header">
        <text class="side-logo">📚</text>
        <text class="side-title">知识库</text>
        <view class="side-close" @click="sideCollapsed = true">
          <text class="side-close-icon">✕</text>
        </view>
      </view>
      <view class="side-tabs">
        <view v-for="(tab, i) in kbTabs" :key="i" class="side-tab" :class="{ active: currentKbTab === i }" @click="switchKbTab(i)">
          <text class="side-tab-icon">{{ tab.icon }}</text>
          <text class="side-tab-label">{{ tab.label }}</text>
        </view>
      </view>

    </view>

    <!-- 主内容区 -->
    <view class="main-area">
      <!-- 图谱搜索/筛选条 -->
      <view class="graph-toolbar" v-show="currentKbTab === 0">
        <view class="graph-search-wrap">
          <text class="graph-search-icon">🔍</text>
          <input class="graph-search-input" v-model="kbSearchText" placeholder="搜索节点..." />
          <text v-if="kbSearchText" class="graph-search-clear" @click="kbSearchText = ''">×</text>
        </view>
      </view>
      <!-- 知识网络 -->
      <view v-show="currentKbTab === 0" class="canvas-area">
        <canvas canvas-id="kbGraph" id="kbGraph" class="full-canvas"
          @touchstart="onGraphTouchStart" @touchmove="onGraphTouchMove" @touchend="onGraphTouchEnd"></canvas>
        <!-- 分类图例 -->
        <view class="graph-legend" v-if="showLegend">
          <view class="legend-header">
            <text class="legend-title">知识分类</text>
            <text class="legend-close" @click="showLegend = false">×</text>
          </view>
          <view v-for="(val, key) in categoryColors" :key="key" class="legend-item"
            :class="{ active: graphFilterCategory === key }" @click="graphFilterCategory = graphFilterCategory === key ? '' : key; drawGraph()">
            <view class="legend-color-bar" :style="{ background: val }"></view>
            <text class="legend-label">{{ key }}</text>
          </view>
          <view class="legend-item reset" v-if="graphFilterCategory" @click="graphFilterCategory = ''; drawGraph()">
            <text class="legend-label">✕ 清除筛选</text>
          </view>
        </view>
        <!-- 图例展开按钮 -->
        <view class="legend-toggle" v-if="!showLegend" @click="showLegend = true">
          <text class="legend-toggle-icon">☰</text>
        </view>
        <!-- 缩放控制 -->
        <view class="zoom-controls">
          <view class="zoom-btn" @click="graphZoomIn"><text class="zoom-text">+</text></view>
          <text class="zoom-label">{{ Math.round(graphDrag.scale * 100) }}%</text>
          <view class="zoom-btn" @click="graphZoomOut"><text class="zoom-text">−</text></view>
          <view class="zoom-divider"></view>
          <view class="zoom-btn reset" @click="graphReset"><text class="zoom-text reset-icon">⟲</text></view>
        </view>
        <!-- 节点详情浮窗 -->
        <view v-if="selectedNode" class="node-detail-float">
          <view class="ndf-head">
            <view class="ndf-icon-wrap" :style="{ background: categoryColors[selectedNode.category] || '#0F766E' }">
              <text class="ndf-icon">{{ selectedNode.icon }}</text>
            </view>
            <view class="ndf-title-area">
              <text class="ndf-title">{{ selectedNode.label }}</text>
              <view class="ndf-meta-row">
                <text class="ndf-cat">{{ selectedNode.category }}</text>
                <text class="ndf-status" v-if="selectedNode.reviewStatus"
                  :class="selectedNode.reviewStatus">{{ selectedNode.reviewStatus === 'approved' ? '已审核' : selectedNode.reviewStatus === 'pending' ? '待审核' : '已修正' }}</text>
              </view>
            </view>
            <text class="ndf-close" @click="selectedNode = null">×</text>
          </view>
          <text class="ndf-desc">{{ selectedNode.desc || '暂无描述' }}</text>
          <view class="ndf-tags">
            <text class="ndf-tag" v-for="(t, ti) in (selectedNode.tags || [])" :key="ti">{{ t }}</text>
          </view>
          <view class="ndf-conns">
            <text class="ndf-conn-label">关联节点：</text>
            <text class="ndf-conn-item" v-for="(c, ci) in getNodeConns(selectedNode)" :key="ci" @click="focusNode(c)">{{ c.label }}</text>
          </view>
          <view class="ndf-actions">
            <view class="ndf-action-btn" @click="goToKnowledgeDetail(selectedNode)">
              <text class="ndf-action-text">📄 查看详情</text>
            </view>
            <view class="ndf-action-btn" @click="highlightAdjacent(selectedNode)">
              <text class="ndf-action-text">🔗 高亮关联</text>
            </view>
            <view class="ndf-action-btn" @click="centerOnNode(selectedNode)">
              <text class="ndf-action-text">🎯 定位</text>
            </view>
          </view>
        </view>
      </view>
      <!-- 沉淀更新 -->
      <scroll-view v-show="currentKbTab === 3" scroll-y class="knowledge-workbench">
        <!-- 紧凑概要条 -->
        <view class="kw-summary-bar">
          <view class="kw-summary-item">
            <text class="kw-summary-num">{{ caseItems.length }}</text>
            <text class="kw-summary-label">已入库</text>
          </view>
          <view class="kw-summary-item">
            <text class="kw-summary-num warn">{{ pendingReviewItems.filter(i => i.status === 'pending').length }}</text>
            <text class="kw-summary-label">待审核</text>
          </view>
          <view class="kw-summary-item">
            <text class="kw-summary-num">{{ updateLogs.filter(i => i.type === 'corrected').length }}</text>
            <text class="kw-summary-label">已修正</text>
          </view>
          <view class="kw-summary-item">
            <text class="kw-summary-num">{{ kbNodes.length }}</text>
            <text class="kw-summary-label">知识节点</text>
          </view>
        </view>

        <!-- 审核入库队列（主体功能） -->
        <view class="kw-section">
          <view class="kw-section-head">
            <view>
              <text class="kw-section-title">审核入库队列</text>
              <text class="kw-section-sub">通过后自动进入案例库并同步知识图谱</text>
            </view>
            <text class="kw-section-count">{{ pendingReviewItems.filter(i => i.status === 'pending').length }} 条待处理</text>
          </view>
          <view v-if="pendingReviewItems.length === 0" class="kw-empty-hint">
            <text class="kw-empty-text">暂无待审核内容，提交案例后在此审核</text>
          </view>
          <view v-else class="review-list">
            <view class="review-card" v-for="item in pendingReviewItems" :key="item.id">
              <view class="review-main">
                <view class="review-title-row">
                  <text class="review-title">{{ item.title }}</text>
                  <text class="review-badge" :class="item.status">{{ getReviewStatusText(item.status) }}</text>
                </view>
                <text class="review-desc">{{ item.summary }}</text>
                <view class="review-meta">
                  <text>{{ item.equipmentCategory }}</text>
                  <text>{{ item.author }}</text>
                  <text>{{ item.submittedAt }}</text>
                </view>
                <view class="review-tags">
                  <text class="review-tag" v-for="tag in item.tags" :key="tag">{{ tag }}</text>
                </view>
              </view>
              <view class="review-actions" v-if="item.status === 'pending'">
                <view class="review-btn ghost" @click="rejectReviewItem(item)"><text>退回补充</text></view>
                <view class="review-btn primary" @click="approveReviewItem(item)"><text>审核入库</text></view>
              </view>
              <view class="review-actions" v-else>
                <view class="review-btn ghost" @click="openDocReader(item)"><text>查看内容</text></view>
              </view>
            </view>
          </view>
        </view>

        <!-- 快速提交案例 -->
        <view class="kw-section">
          <view class="kw-section-head" @click="showCaseForm = !showCaseForm">
            <view>
              <text class="kw-section-title">提交检修案例</text>
              <text class="kw-section-sub">故障案例、经验总结、作业复盘</text>
            </view>
            <text class="kw-toggle-arrow">{{ showCaseForm ? '∧' : '∨' }}</text>
          </view>
          <view v-if="showCaseForm" class="kw-form">
            <input class="kw-input" v-model="newCaseForm.title" placeholder="案例标题，如 CG-125热车熄火排查" />
            <view class="kw-row">
              <input class="kw-input" v-model="newCaseForm.equipmentCategory" placeholder="设备/系统" />
              <picker class="kw-picker" :range="caseSeverityOptions" range-key="label" @change="onSeverityChange">
                <view class="kw-picker-inner">{{ currentSeverityLabel }}</view>
              </picker>
            </view>
            <textarea class="kw-textarea" v-model="newCaseForm.summary" placeholder="填写故障现象、排查过程、处理结论" />
            <input class="kw-input" v-model="newCaseForm.tagsStr" placeholder="标签，逗号分隔" />
            <view class="kw-upload-line">
              <view class="kw-upload-box" @click="mockAttachEvidence">
                <text class="kw-upload-icon">+</text>
                <text class="kw-upload-text">{{ newCaseForm.evidenceName || '添加现场照片/检测数据' }}</text>
              </view>
              <view class="kw-submit" @click="submitCaseForReview"><text>提交审核</text></view>
            </view>
          </view>
          <view v-else class="kw-submit-entry" @click="showCaseForm = true">
            <text class="kw-submit-entry-text">+ 快速提交新案例</text>
          </view>
        </view>

        <!-- 大模型输出修正 -->
        <view class="kw-section">
          <view class="kw-section-head">
            <view>
              <text class="kw-section-title">模型输出修正</text>
              <text class="kw-section-sub">标注不适用内容，保存适配反馈</text>
            </view>
            <view class="kw-section-tag warn"><text>人工校准</text></view>
          </view>
          <view class="annotation-card">
            <view class="annotation-source">
              <text class="annotation-label">模型原输出</text>
              <text class="annotation-text">{{ modelCorrection.sampleOutput }}</text>
            </view>
            <view class="annotation-tools">
              <view
                class="annotation-chip"
                v-for="tag in correctionTags"
                :key="tag"
                :class="{ active: modelCorrection.tags.includes(tag) }"
                @click="toggleCorrectionTag(tag)"
              >
                <text>{{ tag }}</text>
              </view>
            </view>
            <textarea class="kw-textarea correction" v-model="modelCorrection.correctedText" placeholder="输入修正后的标准说法或引用依据" />
            <view class="annotation-footer">
              <text class="annotation-hint">标注：{{ modelCorrection.tags.length ? modelCorrection.tags.join('、') : '未标注' }}</text>
              <view class="kw-submit slim" @click="saveModelCorrection"><text>保存修正</text></view>
            </view>
          </view>
        </view>

        <!-- 更新记录 -->
        <view class="kw-section last">
          <view class="kw-section-head">
            <view>
              <text class="kw-section-title">更新记录</text>
              <text class="kw-section-sub">审核、修正和图谱同步可追踪</text>
            </view>
          </view>
          <view v-if="updateLogs.length === 0" class="kw-empty-hint">
            <text class="kw-empty-text">暂无更新记录</text>
          </view>
          <view v-else class="timeline">
            <view class="timeline-item" v-for="log in updateLogs" :key="log.id">
              <view class="timeline-dot" :class="log.type"></view>
              <view class="timeline-body">
                <text class="timeline-title">{{ log.title }}</text>
                <text class="timeline-desc">{{ log.desc }}</text>
                <text class="timeline-time">{{ log.time }}</text>
              </view>
            </view>
          </view>
        </view>
      </scroll-view>
      <!-- 文件管理器 -->
      <view v-show="currentKbTab === 1" class="file-explorer-area">
        <FileExplorer @open-reader="openFileReader" />
      </view>
      <!-- 技术资料库 -->
      <scroll-view v-show="currentKbTab === 2" scroll-y class="card-main-area tech-lib-area">
        <!-- 子筛选条 -->
        <view class="tech-filter-bar">
          <view class="tech-filter-item" :class="{ active: techTab === 1 }" @click="techTab = 1">
            <text class="tech-filter-label">设备手册</text>
            <text class="tech-filter-count">{{ manualItems.length }}</text>
          </view>
          <view class="tech-filter-item" :class="{ active: techTab === 2 }" @click="techTab = 2">
            <text class="tech-filter-label">故障案例</text>
            <text class="tech-filter-count">{{ caseItems.length }}</text>
          </view>
          <view class="tech-filter-item" :class="{ active: techTab === 3 }" @click="techTab = 3">
            <text class="tech-filter-label">常见问答</text>
            <text class="tech-filter-count">{{ qaItems.length }}</text>
          </view>
        </view>

        <!-- 设备手册 -->
        <view v-if="techTab === 1">
          <view v-for="item in manualItems" :key="'m'+item.id" class="tech-card" @click="openDocReader(item)">
            <view class="tech-card-dot" style="background:#60A5FA"></view>
            <view class="tech-card-body">
              <view class="tech-card-head">
                <text class="tech-card-title">{{ item.title }}</text>
                <text class="tech-card-tag tag-default">手册</text>
              </view>
              <text class="tech-card-desc">{{ item.source }} · {{ item.equipmentCategory || '' }}</text>
              <view class="tech-card-meta">
                <text class="tech-card-meta-item">{{ item.viewCount || 0 }} 次查看</text>
                <text class="tech-card-meta-item" v-if="item.rating">评分 {{ item.rating }}</text>
              </view>
            </view>
            <text class="tech-card-arrow">></text>
          </view>
          <view v-if="manualItems.length === 0" class="tech-empty">
            <text class="tech-empty-text">暂无设备手册</text>
          </view>
        </view>

        <!-- 故障案例 -->
        <view v-if="techTab === 2">
          <view v-for="item in caseItems" :key="'c'+item.id" class="tech-card" @click="openDocReader(item)">
            <view class="tech-card-dot" :style="{ background: item.severity === 'high' ? '#F87171' : item.severity === 'medium' ? '#FBBF24' : '#34D399' }"></view>
            <view class="tech-card-body">
              <view class="tech-card-head">
                <text class="tech-card-title">{{ item.title }}</text>
                <text class="tech-card-tag" :class="'tag-' + item.severity">{{ item.severity === 'high' ? '高' : item.severity === 'medium' ? '中' : '低' }}</text>
              </view>
              <text class="tech-card-desc">{{ item.summary || (item.content && item.content.slice(0, 60)) }}...</text>
              <view class="tech-card-meta">
                <text class="tech-card-meta-item">{{ item.equipmentCategory || '通用' }}</text>
                <text class="tech-card-meta-item">{{ item.viewCount || 0 }} 次查看</text>
                <text class="tech-card-meta-item" v-if="item.rating">评分 {{ item.rating }}</text>
              </view>
            </view>
            <text class="tech-card-arrow">></text>
          </view>
          <view v-if="caseItems.length === 0" class="tech-empty">
            <text class="tech-empty-text">暂无故障案例</text>
          </view>
        </view>

        <!-- 常见问答 -->
        <view v-if="techTab === 3">
          <view v-for="(item, i) in qaItems" :key="'q'+item.id" class="tech-qa-card" @click="item.expanded = !item.expanded">
            <view class="tech-qa-head">
              <text class="tech-qa-q">Q</text>
              <text class="tech-qa-question">{{ item.title }}</text>
              <text class="tech-qa-arrow">{{ item.expanded ? '∧' : '∨' }}</text>
            </view>
            <view class="tech-qa-body" v-if="item.expanded">
              <text class="tech-qa-a">A</text>
              <text class="tech-qa-answer">{{ item.content }}</text>
            </view>
          </view>
          <view v-if="qaItems.length === 0" class="tech-empty">
            <text class="tech-empty-text">暂无常见问答</text>
          </view>
        </view>
      </scroll-view>
    </view>

    <!-- 文件阅读器 -->
    <view class="reader-mask" v-if="docReader" @click="docReader = null">
      <view class="reader-panel" @click.stop>
        <view class="reader-header">
          <view class="reader-header-left">
            <text class="reader-back" @click="docReader = null">←</text>
            <text class="reader-title">{{ docReader.title }}</text>
          </view>
          <view class="reader-header-right">
            <text class="reader-fav" @click="docReader._fav = !docReader._fav">{{ docReader._fav ? '⭐' : '☆' }}</text>
            <text class="reader-close-btn" @click="docReader = null">✕</text>
          </view>
        </view>
        <view class="reader-meta-bar">
          <text class="reader-meta">📖 {{ docReader.source }}</text>
          <text class="reader-meta">🔧 {{ docReader.equipmentCategory || '通用' }}</text>
          <text class="reader-meta">⭐ {{ docReader.rating || 0 }}</text>
        </view>
        <view class="reader-tags" v-if="docReader.tags && docReader.tags.length">
          <text class="reader-tag" v-for="(t, i) in docReader.tags" :key="i">{{ t }}</text>
        </view>
        <scroll-view scroll-y class="reader-body">
          <text class="reader-content">{{ docReader.content }}</text>
        </scroll-view>
        <view class="reader-footer">
          <view class="reader-action" @click="docReader = null"><text>关闭</text></view>
          <view class="reader-action primary" v-if="!docReader._inKB" @click="docReader._inKB = true; uni.showToast({title:'已加入知识库',icon:'success'})"><text>📚 加入知识库</text></view>
          <view class="reader-action" @click="uni.showToast({title:'分享功能开发中',icon:'none'})"><text>📤 分享</text></view>
        </view>
      </view>
    </view>

    <!-- 添加节点弹窗 -->
    <view v-if="showAddNode" class="modal-mask" @click="showAddNode = false">
      <view class="modal-box" @click.stop="">
        <text class="modal-title">添加知识点</text>
        <input class="modal-input" v-model="newNode.label" placeholder="知识点名称" />
        <input class="modal-input" v-model="newNode.category" placeholder="分类（如 AI、编程）" />
        <textarea class="modal-textarea" v-model="newNode.desc" placeholder="描述..." />
        <input class="modal-input" v-model="newNode.tagsStr" placeholder="标签（逗号分隔）" />
        <view class="modal-btns">
          <view class="mbtn cancel" @click="showAddNode = false"><text class="mbtn-text">取消</text></view>
          <view class="mbtn confirm" @click="addKbNode"><text class="mbtn-text">添加</text></view>
        </view>
      </view>
    </view>

    <!-- 智能体面板（原样式） -->
    <view class="agent-card" :class="{ 'card-collapsed': isCollapsed }" @click.stop="">
      <view class="card-header" @click="togglePanel">
        <view class="header-main">
          <view class="avatar-group">
            <image src="../../static/assistant-knowledge.png" mode="aspectFit" class="agent-img"></image>
          </view>
          <view class="header-text">
            <text class="agent-title">知识库助手</text>
            <view class="agent-badge">
              <text class="badge-dot"></text>
              <text class="badge-text">探索中</text>
            </view>
          </view>
        </view>
        <view class="header-aside">
          <text :class="['toggle-arrow', isCollapsed ? 'up' : 'down']">›</text>
        </view>
      </view>
      <view v-show="!isCollapsed" class="card-body">
        <scroll-view class="chat-viewport" scroll-y="true" :scroll-into-view="scrollTop" scroll-with-animation>
          <view class="chat-bubble ai-bubble welcome-msg" id="msg-root">
            <text class="bubble-text">您好！我是知识库助手 📚\n\n我可以帮你：\n1. 检索设备手册和检修规范\n2. 查询历史故障案例和处理方案\n3. 推荐标准作业流程和安全要点\n\n请在下方输入你想查询的检修知识：</text>
            <view class="quick-suggestions">
              <view class="sugg-tag" @click="quickMessage('摩托车发动机启动困难怎么排查？')">启动困难排查</view>
              <view class="sugg-tag" @click="quickMessage('ZK-320配电柜过热有哪些相似案例？')">相似案例</view>
              <view class="sugg-tag" @click="quickMessage('检修作业前需要核对哪些安全项？')">安全核对</view>
              <view class="sugg-tag" @click="quickMessage('把当前知识网络中的关联节点解释一下')">图谱解释</view>
              <view class="sugg-tag" @click="quickMessage('如何把一线检修经验沉淀进知识库？')">经验沉淀</view>
            </view>
          </view>
          <block v-for="(msg, index) in chatHistory" :key="index">
            <view class="message-row" :class="msg.type">
              <view v-if="msg.type === 'expert'" class="message-avatar agent-avatar-wrap">
                <image src="../../static/assistant-knowledge.png" mode="aspectFit" class="avatar-img"></image>
              </view>
              <view class="message-content-box">
                <view v-if="msg.type === 'expert' && msg.thinkingSteps && msg.thinkingSteps.length" class="thought-process">
                  <view class="thought-header" @click="toggleMsgThinking(index)">
                    <text class="thought-label">思考过程</text>
                    <text class="thought-action">{{ msg.expanded ? '隐藏' : '查看' }}</text>
                  </view>
                  <view v-if="msg.expanded" class="thought-detail">
                    <view v-for="(step, si) in msg.thinkingSteps" :key="si" class="thought-step">
                      <text class="step-icon">•</text>
                      <text class="step-text">{{ step.content || step.step || '' }}</text>
                    </view>
                  </view>
                </view>
                <view class="chat-bubble" :class="msg.type + '-bubble'" :id="'msg-' + index">
                  <view v-if="msg.loading" class="pulse-loading">
                    <view class="dot"></view><view class="dot"></view><view class="dot"></view>
                  </view>
                  <text v-else class="bubble-text">{{ msg.message }}</text>
                </view>
              </view>
            </view>
          </block>
          <view id="chat-bottom-anchor" style="height: 40rpx;"></view>
        </scroll-view>
        <view class="composition-area">
          <view class="input-wrapper">
            <input type="text" v-model="userMessage" placeholder="输入检修知识或故障问题" class="neo-input" placeholder-class="input-placeholder" @confirm="sendMessage" @input="handleInput" />
            <view class="voice-btn" :class="{ active: isVoiceRecording || isVoiceTranscribing }" @click="toggleVoiceInput">
              <text class="voice-btn-text">{{ isVoiceRecording ? '停止' : (isVoiceTranscribing ? '识别中' : '语音') }}</text>
            </view>
            <view class="send-btn" :class="{ 'active': userMessage.trim() }" @click="sendMessage">
              <text class="send-text">发送</text>
            </view>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>
<script>
import CustomNavbar from '../../src/components/custom-navbar/custom-navbar.vue';
import FileExplorer from '../../src/components/FileExplorer/FileExplorer.vue';
import request, { API_HOST } from '../../utils/request.js';
import { createVoiceInputController } from '../../utils/voice-input.js';

const USER_API_BASE = `${API_HOST}:5000/api/user`;

export default {
  components: {
    CustomNavbar,
    FileExplorer,
  },
  data() {
    return {
      userMessage: '',
      chatHistory: [],
      scrollTop: '',
      conversationId: '',
      isSending: false,
      isVoiceRecording: false,
      isVoiceTranscribing: false,
      voiceInputController: null,
      isCollapsed: true,
      currentLocationName: '',
      currentLocation: null,
      mapStatus: 'loaded',
      recommendationMarkers: [],
      activeRecommendationMarkers: [],
      typingText: '',
      isTyping: false,
      retryCount: 0,
      maxRetries: 3,
      inputDebounceTimer: null,
      showPreferenceModal: false,
      preferences: {
        favorite_cuisines: '',
        dietary_habits: '',
        custom_notes: ''
      },
      commonCuisines: ['课程讲解文档', '知识点思维导图', '分层练习题', '拓展阅读材料', '代码实操案例', '项目任务书', '短视频脚本', '动画分镜', '错题复盘', '考试冲刺清单', '论文阅读清单', '课堂演示材料'],
      commonHabits: ['图解优先', '案例驱动', '代码实操', '题库训练', '短视频讲解', '先易后难', '高频复盘', '项目导向', '考试导向', '研究拓展', '碎片化学习', '长时段深学'],
      customCuisine: '',
      kbTabs: [
        { icon: '🌐', label: '知识网络' },
        { icon: '📂', label: '文件管理' },
        { icon: '📗', label: '技术资料库' },
        { icon: '📝', label: '沉淀更新' },
      ],
      currentKbTab: 0, techTab: 1, kbSearchText: '', showAddNode: false, showSearch: false, selectedNode: null, sideCollapsed: true, showLabels: false,
      showLegend: true, graphFilterCategory: '',
      statusBarHeight: 0,
      graphDrag: { startX: 0, startY: 0, offsetX: 0, offsetY: 0, dragging: false, scale: 1, pinchDist: 0 },
      mindDrag: { startX: 0, startY: 0, offsetX: 0, offsetY: 0, dragging: false, scale: 1, pinchDist: 0 },
      kbNodes: [
        { id: 1, label: '摩托车发动机', category: '设备', icon: '🏍️', desc: '摩托车发动机总成，包含点火、燃油、润滑、配气等子系统。', tags: ['设备'], x: 200, y: 300 },
        { id: 2, label: '发动机启动困难', category: '故障现象', icon: '⚠️', desc: '发动机无法正常启动，可能涉及点火、燃油或压缩问题。', tags: ['启动'], x: 100, y: 180 },
        { id: 3, label: '点火系统检查', category: '检修流程', icon: '⚡', desc: '检查火花塞状态、点火线圈输出、线路连接和点火时序。', tags: ['点火'], x: 80, y: 420 },
        { id: 4, label: '故障图片', category: '多模态证据', icon: '🖼️', desc: '现场照片、火花塞状态图、油液状态图等跨模态证据。', tags: ['图片'], x: 350, y: 180 },
        { id: 5, label: '摩托车发动机维修手册', category: '检修手册', icon: '📘', desc: '摩托车发动机维修手册.pdf，涵盖结构认知、故障排查和标准作业。', tags: ['手册'], x: 380, y: 420, filePath: '/static/manuals/摩托车发动机维修手册.pdf', reviewStatus: 'approved' },
        { id: 6, label: '燃油供给检查', category: '检修流程', icon: '⛽', desc: '检查油路堵塞、滤清器状态、化油器/喷油器供给和泄漏风险。', tags: ['燃油'], x: 150, y: 520 },
        { id: 7, label: '机油与润滑', category: '检修流程', icon: '🛢️', desc: '机油液位检查、油质评估、润滑系统渗漏排查。', tags: ['润滑'], x: 50, y: 520 },
        { id: 8, label: '相似案例', category: '案例库', icon: '🧰', desc: '历史故障处置案例、经验总结和处理结论。', tags: ['案例'], x: 220, y: 80, reviewStatus: 'pending' },
        { id: 9, label: '发动机异响', category: '故障现象', icon: '🔊', desc: '异响可能来自气门间隙、链条磨损、轴承磨损或润滑不足。', tags: ['异响'], x: 400, y: 520 },
        { id: 10, label: '人工修正', category: '更新机制', icon: '✍️', desc: '人工标注与修正模型输出，审核后入库更新。', tags: ['沉淀'], x: 280, y: 580, reviewStatus: 'corrected' },
        { id: 11, label: 'ZK-320配电柜', category: '设备', icon: '⚡', desc: '电气检修对象，重点关注接触器、端子排、散热通道和绝缘状态。', tags: ['配电柜', '电气'], x: 560, y: 260 },
        { id: 12, label: '配电柜过热', category: '故障现象', icon: '🌡️', desc: '柜体或触点温升异常，可能由接触不良、过载、散热受阻引发。', tags: ['过热', '温升'], x: 560, y: 120 },
        { id: 13, label: '停电验电与挂牌上锁', category: '检修流程', icon: '🛡️', desc: '电气检修前置安全动作，包含隔离、验电、放电、挂牌和复核。', tags: ['安全', 'LOTO'], x: 620, y: 420 },
        { id: 14, label: '红外测温记录', category: '多模态证据', icon: '📷', desc: '热成像、测温照片和温度曲线可作为复检评估证据。', tags: ['图片', '测温'], x: 510, y: 500 },
        { id: 15, label: '复检评估', category: '更新机制', icon: '✅', desc: '检修完成后复核质量、风险闭环、记录完整性和知识沉淀价值。', tags: ['复检', '闭环'], x: 680, y: 580, reviewStatus: 'corrected' },
        { id: 16, label: '液压千斤顶', category: '设备', icon: '🏗️', desc: 'YZ-50T液压千斤顶，额定载荷50吨，用于重物顶升作业。', tags: ['液压', '千斤顶'], x: -300, y: 200 },
        { id: 17, label: '液压油泄漏', category: '故障现象', icon: '💧', desc: '液压油从油封、接头或缸体处渗漏，导致压力不足。', tags: ['泄漏', '液压'], x: -450, y: 100 },
        { id: 18, label: '密封件更换', category: '检修流程', icon: '🔧', desc: '拆卸旧密封件、清理密封面、安装新密封件并测试密封性。', tags: ['密封', '更换'], x: -400, y: 320 },
        { id: 19, label: '压力测试记录', category: '多模态证据', icon: '📊', desc: '液压系统压力测试数据、保压曲线和泄漏检测记录。', tags: ['压力', '测试'], x: -200, y: 350 },
        { id: 20, label: '液压系统维护手册', category: '检修手册', icon: '📘', desc: '液压千斤顶使用手册，涵盖安全须知、操作规程和维护保养。', tags: ['液压', '手册'], x: -150, y: 100, reviewStatus: 'approved' },
        { id: 21, label: '万用表', category: '设备', icon: '🔌', desc: 'UT61E数字万用表，用于电压、电流、电阻和通断检测。', tags: ['万用表', '检测'], x: 300, y: -200 },
        { id: 22, label: '电路断路故障', category: '故障现象', icon: '💥', desc: '电路中出现断路，导致设备无法通电或部分功能失效。', tags: ['断路', '电气'], x: 450, y: -100 },
        { id: 23, label: '绝缘电阻检测', category: '检修流程', icon: '📐', desc: '使用兆欧表测量设备绝缘电阻，判断绝缘状态是否合格。', tags: ['绝缘', '检测'], x: 500, y: -250 },
        { id: 24, label: '安全操作规程', category: '检修手册', icon: '📕', desc: '设备检修安全操作规程，包含LOTO、PPE、许可证制度等。', tags: ['安全', '规程'], x: -50, y: -180, reviewStatus: 'approved' },
        { id: 25, label: '预防性维护计划', category: '更新机制', icon: '📅', desc: '基于设备运行数据制定的定期维护计划和备件更换周期。', tags: ['预防', '计划'], x: -180, y: -50 },
        { id: 26, label: 'CG-125发动机', category: '设备', icon: '🏍️', desc: '本田CG-125单缸四冲程摩托车发动机，排量125cc。', tags: ['CG-125', '发动机'], x: 100, y: -300 },
        { id: 27, label: '火花塞积碳', category: '故障现象', icon: '🕯️', desc: '火花塞电极积碳严重导致点火不良，间隙偏大。', tags: ['火花塞', '积碳'], x: 200, y: -400 },
        { id: 28, label: '化油器清洗', category: '检修流程', icon: '🧴', desc: '拆卸化油器、清洗主量孔和怠速量孔、调整油面高度。', tags: ['化油器', '清洗'], x: -50, y: -400 },
        { id: 29, label: '检修报告模板', category: '检修手册', icon: '📋', desc: '标准化检修报告模板，包含设备信息、故障描述、处理过程和结论。', tags: ['报告', '模板'], x: -300, y: -200 },
        { id: 30, label: '设备巡检记录', category: '多模态证据', icon: '📝', desc: '日常巡检记录表，包含设备状态、温度、振动和声音检查结果。', tags: ['巡检', '记录'], x: -350, y: -50 }
      ],
      kbConnections: [
        { from: 1, to: 2 }, { from: 1, to: 3 }, { from: 1, to: 5 },
        { from: 1, to: 6 }, { from: 1, to: 7 }, { from: 1, to: 9 },
        { from: 2, to: 3 }, { from: 2, to: 6 }, { from: 2, to: 10 },
        { from: 3, to: 8 }, { from: 3, to: 5 },
        { from: 4, to: 8 }, { from: 5, to: 8 },
        { from: 6, to: 10 }, { from: 9, to: 3 }, { from: 9, to: 7 },
        { from: 11, to: 12 }, { from: 11, to: 13 }, { from: 12, to: 14 },
        { from: 12, to: 8 }, { from: 13, to: 15 }, { from: 14, to: 15 },
        { from: 15, to: 10 }, { from: 15, to: 8 },
        // 液压千斤顶相关
        { from: 16, to: 17 }, { from: 16, to: 18 }, { from: 16, to: 20 },
        { from: 17, to: 18 }, { from: 17, to: 19 }, { from: 18, to: 19 },
        { from: 19, to: 8 }, { from: 20, to: 8 },
        // 万用表相关
        { from: 21, to: 22 }, { from: 21, to: 23 }, { from: 22, to: 23 },
        { from: 22, to: 8 }, { from: 23, to: 15 },
        // 安全与维护
        { from: 24, to: 3 }, { from: 24, to: 13 }, { from: 24, to: 20 },
        { from: 25, to: 10 }, { from: 25, to: 15 }, { from: 25, to: 24 },
        // CG-125发动机相关
        { from: 26, to: 1 }, { from: 26, to: 27 }, { from: 26, to: 28 },
        { from: 27, to: 3 }, { from: 27, to: 8 }, { from: 28, to: 6 },
        { from: 28, to: 27 },
        // 报告与巡检
        { from: 29, to: 8 }, { from: 29, to: 24 },
        { from: 30, to: 14 }, { from: 30, to: 19 }, { from: 30, to: 25 }
      ],
      mindRoot: {
        id: 0, label: '设备检修知识体系', collapsed: false, children: [
          { id: 1, label: '发动机系统', collapsed: false, children: [
            { id: 2, label: '启动困难排查', collapsed: false, children: [] },
            { id: 9, label: '异响诊断', collapsed: false, children: [] },
            { id: 3, label: '点火系统检查', collapsed: false, children: [] }
          ]},
          { id: 6, label: '燃油供给系统', collapsed: false, children: [] },
          { id: 7, label: '润滑系统', collapsed: false, children: [] },
          { id: 5, label: '维修手册', collapsed: false, children: [
            { id: 8, label: '历史案例', collapsed: false, children: [] }
          ]}
        ]
      },
      newNode: { label: '', category: '', desc: '', tagsStr: '' },
      // 设备手册
      manualItems: [
        { id: 'm1', title: '摩托车发动机维修手册', source: '本田技术文档', equipmentCategory: '发动机', tags: ['发动机', 'CG-125', '维修'], content: '本手册涵盖摩托车发动机的结构认知、日常维护、故障排查和标准作业流程。\n\n第一章 发动机结构\n1.1 气缸体与活塞组\n气缸体是发动机的核心部件，承受高温高压。活塞在气缸内往复运动，通过连杆将直线运动转化为旋转运动。\n\n1.2 配气机构\n配气机构控制进排气门的开闭时序，直接影响发动机的充气效率和排放性能。气门间隙的标准值为0.05-0.10mm。\n\n1.3 点火系统\n点火系统由火花塞、点火线圈、ECU组成。火花塞电极间隙标准值为0.6-0.7mm。', viewCount: 523, rating: 4.8, updatedAt: '2026-06-08' },
        { id: 'm2', title: 'ZK-320配电柜维护规范', source: '正泰技术文档', equipmentCategory: '电气系统', tags: ['配电柜', 'ZK-320', '维护'], content: 'ZK-320配电柜维护规范\n\n一、巡检要点\n1. 检查柜体外观，无变形、腐蚀\n2. 检查指示灯状态\n3. 使用红外测温仪检测各接点温度\n4. 正常运行温度不应超过65℃', viewCount: 312, rating: 4.6, updatedAt: '2026-06-05' },
        { id: 'm3', title: '液压千斤顶使用手册', source: '上海液压', equipmentCategory: '液压系统', tags: ['液压', '千斤顶', '安全'], content: 'YZ-50T液压千斤顶使用手册\n\n一、安全须知\n1. 使用前检查液压油位\n2. 确认承载不超过额定载荷50T\n3. 使用平整坚实的地面', viewCount: 189, rating: 4.5, updatedAt: '2026-06-01' },
      ],
      // 故障案例
      caseItems: [
        { id: 'c1', title: 'CG-125发动机启动困难排查', source: '一线检修案例', equipmentCategory: '发动机', tags: ['启动困难', '点火', '燃油'], severity: 'medium', content: '故障现象：发动机启动困难，多次打火才能启动，启动后怠速不稳。\n\n排查过程：\n1. 检查火花塞 → 电极积碳严重\n2. 检查点火线圈 → 次级线圈电阻偏高\n3. 检查燃油供给 → 化油器油面偏低\n\n处理方案：更换火花塞、点火线圈、浮子针阀。', viewCount: 456, rating: 4.9, updatedAt: '2026-06-08' },
        { id: 'c2', title: 'ZK-320配电柜过热故障处理', source: '一线检修案例', equipmentCategory: '电气系统', tags: ['过热', '接触器', '配电柜'], severity: 'high', content: '故障现象：配电柜运行温度异常，红外测温显示A相接触器触点温度达85℃。\n\n处理方案：打磨触点、更换老化触点、清理散热通道。', viewCount: 378, rating: 4.8, updatedAt: '2026-06-05' },
        { id: 'c3', title: '液压千斤顶漏油故障', source: '一线检修案例', equipmentCategory: '液压系统', tags: ['漏油', '密封', '液压'], severity: 'medium', content: '故障现象：液压千斤顶使用时油封处渗漏液压油。\n\n处理方案：更换全套密封件，打磨缸体内壁划痕。', viewCount: 234, rating: 4.6, updatedAt: '2026-06-02' },
      ],
      // 常见问答
      qaItems: [
        { id: 'q1', title: '发动机异响有哪些常见原因？', content: '发动机异响的常见原因包括：\n1. 气门间隙过大 → 产生"哒哒"声\n2. 链条磨损松弛 → 产生"哗哗"声\n3. 轴承损坏 → 产生"嗡嗡"声\n4. 活塞环磨损 → 产生"嘶嘶"声\n5. 润滑不足 → 产生干摩擦声', tags: ['异响', '发动机'], expanded: false },
        { id: 'q2', title: '配电柜过热如何紧急处理？', content: '配电柜过热紧急处理步骤：\n1. 立即降低负载\n2. 持续监测温度变化\n3. 如温度持续上升超过90℃，立即停电\n4. 停电后挂牌上锁\n5. 定位热点并修复', tags: ['过热', '配电柜'], expanded: false },
        { id: 'q3', title: '如何正确使用万用表检测电路故障？', content: '万用表检测电路故障步骤：\n1. 选择正确的量程和档位\n2. 测量前先确认万用表工作正常\n3. 电压测量：并联接入\n4. 电阻测量：断电状态下测量\n5. 通断检测：蜂鸣档快速判断', tags: ['万用表', '检测'], expanded: false },
        { id: 'q4', title: '检修作业前需要做哪些安全准备？', content: '检修作业安全准备清单：\n1. 穿戴个人防护装备\n2. 确认工作许可证已签发\n3. 断开电源并验电确认\n4. 挂牌上锁（LOTO）\n5. 设置安全隔离区\n6. 确认至少两人在场', tags: ['安全', 'LOTO'], expanded: false },
      ],
      // 文件阅读器
      docReader: null,
      showCaseForm: false,
      caseSeverityOptions: [
        { label: '一般', value: 'low' },
        { label: '中等', value: 'medium' },
        { label: '高风险', value: 'high' }
      ],
      newCaseForm: {
        title: '',
        equipmentCategory: '',
        severity: 'medium',
        summary: '',
        tagsStr: '',
        evidenceName: ''
      },
      pendingReviewItems: [
        {
          id: 'r1',
          title: '发动机热车后怠速熄火复盘',
          source: '一线检修案例',
          equipmentCategory: '发动机',
          tags: ['怠速熄火', '热车', '化油器'],
          severity: 'medium',
          summary: '热车后怠速逐步下降并熄火，现场排查发现怠速量孔轻微堵塞，清洗后恢复稳定。',
          content: '故障现象：热车运行 10 分钟后怠速下降并熄火。\n\n排查过程：检查火花塞、进气管密封和化油器怠速量孔。\n\n处理结论：清洗怠速量孔，复核混合比螺钉位置，热车复测 15 分钟无异常。',
          status: 'pending',
          author: '华东一线组',
          submittedAt: '2026-06-14 09:20'
        },
        {
          id: 'r2',
          title: '配电柜接触器触点烧蚀经验总结',
          source: '经验总结',
          equipmentCategory: '电气系统',
          tags: ['触点烧蚀', '温升', '接触器'],
          severity: 'high',
          summary: '红外测温发现 A 相触点温升异常，拆检存在烧蚀，建议纳入接触器温升巡检规则。',
          content: '经验总结：红外温度超过同柜其他相 20℃ 以上时，应优先检查触点压力、氧化层和接线紧固状态。',
          status: 'pending',
          author: '北区检修班',
          submittedAt: '2026-06-14 10:05'
        }
      ],
      correctionTags: ['无依据', '不适用现场', '安全风险', '参数错误', '需补充引用'],
      modelCorrection: {
        sampleOutput: '建议直接拆卸点火线圈并更换总成，随后尝试启动发动机。',
        correctedText: '应先断电确认安全状态，再依次检查火花塞间隙、点火线圈电阻和线路连接；只有检测结果异常时才更换对应部件。',
        tags: ['安全风险', '需补充引用']
      },
      updateLogs: [
        { id: 'u1', type: 'approved', title: '摩托车发动机维修手册已入库', desc: '形成检修手册节点，关联启动困难、点火系统检查等知识点。', time: '2026-06-13 18:30' },
        { id: 'u2', type: 'review', title: '一线检修案例进入审核队列', desc: '发动机热车后怠速熄火复盘等待审核。', time: '2026-06-14 09:20' },
        { id: 'u3', type: 'corrected', title: '模型输出完成一次人工修正', desc: '标注安全风险和引用缺失，生成适配反馈。', time: '2026-06-14 10:18' }
      ],
      categoryColors: {
        '设备': '#0F766E', '故障现象': '#E8453C', '检修流程': '#0284C7',
        '多模态证据': '#7C3AED', '检修手册': '#0891B2', '案例库': '#D97706',
        '更新机制': '#DB2777'
      },
      graphAnimTimer: null,
      graphTime: 0,
      canvasW: 375,
      canvasH: 600,
    }
  },
  computed: {
    filteredKbNodes() {
      let nodes = this.kbNodes
      if (this.kbSearchText.trim()) {
        const kw = this.kbSearchText.trim().toLowerCase()
        nodes = nodes.filter(n => n.label.toLowerCase().includes(kw) || (n.desc || '').toLowerCase().includes(kw))
      }
      return nodes
    },
    nodeMap() {
      const map = {}
      this.kbNodes.forEach(n => { map[n.id] = n })
      return map
    },
    graphCategories() {
      return Object.keys(this.categoryColors)
    },
    filteredGraphNodes() {
      if (!this.graphFilterCategory) return this.kbNodes
      return this.kbNodes.filter(n => n.category === this.graphFilterCategory)
    },
    currentSeverityLabel() {
      const match = this.caseSeverityOptions.find(item => item.value === this.newCaseForm.severity)
      return match ? match.label : '中等'
    },
    knowledgeStats() {
      const approved = this.caseItems.length
      const pending = this.pendingReviewItems.filter(item => item.status === 'pending').length
      const rejected = this.pendingReviewItems.filter(item => item.status === 'rejected').length
      const corrections = this.updateLogs.filter(item => item.type === 'corrected').length
      const graphUpdates = this.updateLogs.filter(item => item.type === 'approved' || item.type === 'graph').length
      const totalReviewed = approved + rejected
      const approvedRate = totalReviewed ? Math.round((approved / totalReviewed) * 100) : 100
      return {
        approvedRate,
        graphUpdates,
        cards: [
          { label: '已沉淀案例', value: approved },
          { label: '待审核内容', value: pending },
          { label: '人工修正', value: corrections },
          { label: '知识节点', value: this.kbNodes.length }
        ]
      }
    },
    myUploadItems() {
      const user = uni.getStorageSync('user') || {}
      const userName = user.name || user.username || '当前一线人员'
      // 从审核队列中筛选当前用户提交的内容
      const items = this.pendingReviewItems.filter(item => item.author === userName)
      // 也把已入库的案例（来源为当前用户）加进来
      const approvedItems = this.caseItems
        .filter(item => item.source === '一线人员上传' || item.source === '审核入库')
        .map(item => ({
          ...item,
          status: 'approved',
          submittedAt: item.updatedAt || ''
        }))
      // 合并去重，审核队列优先
      const seenIds = new Set(items.map(i => i.id))
      const merged = [...items]
      approvedItems.forEach(a => {
        if (!seenIds.has(a.id)) merged.push(a)
      })
      return merged
    }
  },
  mounted() {
    this.initConversation();
    this.loadPreferences();
    this.initVoiceInput();
    this.loadKbData();
    const sys = uni.getSystemInfoSync();
    this.statusBarHeight = sys.statusBarHeight || 0;
  },
  onReady() {
    setTimeout(() => {
      this.startGraphAnimation()
      this.drawGraph()
    }, 800)
  },
  beforeDestroy() {
    clearTimeout(this.inputDebounceTimer)
    this.stopGraphAnimation()
    if (this.voiceInputController) {
      this.voiceInputController.destroy()
    }
  },
  methods: {
    initVoiceInput() {
      if (this.voiceInputController) return;

      this.voiceInputController = createVoiceInputController({
        service: 'tuantuan',
        onStateChange: ({ isRecording, isTranscribing }) => {
          this.isVoiceRecording = isRecording;
          this.isVoiceTranscribing = isTranscribing;
        },
        onTranscribed: (text) => {
          this.userMessage = this.userMessage.trim() ? `${this.userMessage.trim()} ${text}` : text;
          uni.showToast({ title: '语音已转文字', icon: 'none' });
        },
        onError: (error) => {
          const title = (error?.message || '语音输入失败').slice(0, 20);
          uni.showToast({ title, icon: 'none' });
        }
      });
    },

    togglePanel() {
      this.isCollapsed = !this.isCollapsed;
    },
    toggleMsgThinking(index) {
      this.$set(this.chatHistory, index, {
        ...this.chatHistory[index],
        expanded: !this.chatHistory[index].expanded
      });
    },
    quickMessage(text) {
      this.userMessage = text;
      this.sendMessage();
    },
    handleInput(e) {
      clearTimeout(this.inputDebounceTimer);
      this.inputDebounceTimer = setTimeout(() => {
        console.log('User input:', e.detail.value);
      }, 300);
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
    scrollToBottom() {
      this.$nextTick(() => {
        setTimeout(() => {
          this.scrollTop = ''; // 先重置
            this.scrollTop = 'chat-bottom-anchor';
          });
        }, 150); // 增加延时确保渲染和高度计算完成
    },
    async initConversation() {
      // 知识库问答使用本地会话 ID 追踪多轮上下文
      if (!this.conversationId) {
        this.conversationId = `${Date.now()}_${Math.random().toString(16).slice(2)}`;
      }
    },
    updateLocationName(name) {
      this.currentLocationName = this.normalizeLocationName(name);
    },
    updateLocation(position) {
      this.currentLocation = position;
    },
    hasRealtimeLocation() {
      const lng = Number(this.currentLocation?.lng);
      const lat = Number(this.currentLocation?.lat);
      return Number.isFinite(lng) && Number.isFinite(lat);
    },
    isNearbyQuery(text) {
      return /附近|周边|旁边|周围/.test(String(text || ''));
    },
    normalizeLocationName(name) {
      const text = String(name || '').trim();
      if (!text) return '';
      if (text.includes('当前位置')) return '';
      if (text.includes('定位中')) return '';
      if (text.includes('探测地理位置')) return '';
      if (text.includes('获取位置')) return '';
      if (text.includes('IP定位')) return '';
      if (text.includes('默认定位')) return '';
      return text;
    },
    buildAgentRequestPayload(userMsg) {
      const payload = {
        conversation_id: this.conversationId,
        message: userMsg,
        preferences: this.preferences,
        knowledge_context: this.buildKnowledgeAgentContext()
      };
      const locationName = this.normalizeLocationName(this.currentLocationName);
      const hasRealtimeLocation = this.hasRealtimeLocation();
      if (locationName) {
        payload.location = locationName;
      }
      if (hasRealtimeLocation) {
        payload.location_coords = this.currentLocation;
      }
      return payload;
    },
    setMapStatus(status) {
      this.mapStatus = status;
    },
    normalizePois(pois) {
      if (!Array.isArray(pois)) return [];
      return pois
        .map((poi) => {
          const lng = Number(poi?.location?.lng);
          const lat = Number(poi?.location?.lat);
          if (!Number.isFinite(lng) || !Number.isFinite(lat) || !poi?.name) {
            return null;
          }
          return {
            id: poi.id || `${poi.name}_${lng}_${lat}`,
            name: poi.name,
            address: poi.address || '',
            location: { lng, lat },
            tel: poi.tel || '',
            type: poi.type || ''
          };
        })
        .filter(Boolean);
    },
    async sendMessage() {
      if (!this.userMessage.trim() || this.isSending) return;
      
      const userMsg = this.userMessage.trim();
      this.chatHistory = [...this.chatHistory, { type: 'user', message: userMsg }];
      this.userMessage = '';
      this.isSending = true;
      this.isCollapsed = false;
      this.retryCount = 0;
      this.scrollToBottom();

      const loadingMsgIndex = this.chatHistory.length;
      this.chatHistory = [...this.chatHistory, { type: 'expert', message: '', loading: true }];
      this.scrollToBottom();

      await this.sendMessageWithRetry(userMsg);
    },
    async sendMessageWithRetry(userMsg) {
      try {
        const requestPayload = this.buildAgentRequestPayload(userMsg);
        const history = this.chatHistory.filter(m => !m.loading);
        const data = await this.askKnowledgeAgent(requestPayload);
        let thinkingSteps = Array.isArray(data?.thinking_process) ? data.thinking_process : [
          { content: '读取当前知识网络、设备手册、故障案例、常见问答和沉淀更新内容' },
          { content: data?.source === 'rag' ? '优先使用知识图谱 RAG 检索' : 'RAG 不可用，使用统一 AI 结合页面上下文回答' }
        ];
        let responseMsg = data?.response || '知识库助手正在整理答案，请稍后再试...';

        this.chatHistory = [
          ...history,
          {
            type: 'expert',
            message: responseMsg,
            thinkingSteps: thinkingSteps,
            expanded: false
          }
        ];
        
        this.scrollToBottom();
        this.isSending = false;
      } catch (err) {
        console.error('Knowledge agent failed:', err);
        
        if (this.retryCount < this.maxRetries) {
          this.retryCount++;
          console.log(`Retrying... (${this.retryCount}/${this.maxRetries})`);
          await new Promise(resolve => setTimeout(resolve, 1000 * this.retryCount));
          return this.sendMessageWithRetry(userMsg);
        }
        
        const history = this.chatHistory.filter(m => !m.loading);
        
        let errorMsg = '暂时无法连接知识库助手，请稍后重试';
        if (err.errMsg && err.errMsg.includes('timeout')) {
          errorMsg = '响应超时，请稍后再试';
        } else if (err.errMsg && err.errMsg.includes('network')) {
          errorMsg = '网络连接失败，请检查网络';
        }
        
        this.chatHistory = [
          ...history,
          { type: 'expert', message: errorMsg }
        ];
        this.isSending = false;
        this.scrollToBottom();
      }
    },
    buildKnowledgeAgentContext() {
      return {
        page: '知识库',
        active_tab: this.kbTabs[this.currentKbTab]?.label || '知识网络',
        selected_node: this.selectedNode ? {
          label: this.selectedNode.label,
          category: this.selectedNode.category,
          desc: this.selectedNode.desc,
          tags: this.selectedNode.tags,
          related: this.getNodeConns(this.selectedNode).map(node => node.label)
        } : null,
        graph_nodes: this.kbNodes.map(node => ({
          label: node.label,
          category: node.category,
          desc: node.desc,
          tags: node.tags,
          review_status: node.reviewStatus
        })),
        manuals: this.manualItems.map(item => ({
          title: item.title,
          source: item.source,
          equipment: item.equipmentCategory,
          tags: item.tags,
          content: item.content
        })),
        cases: this.caseItems.map(item => ({
          title: item.title,
          source: item.source,
          equipment: item.equipmentCategory,
          severity: item.severity,
          tags: item.tags,
          content: item.content
        })),
        qa: this.qaItems.map(item => ({
          question: item.title,
          answer: item.content,
          tags: item.tags
        })),
        pending_reviews: this.pendingReviewItems.slice(0, 5).map(item => ({
          title: item.title,
          type: item.type,
          equipment: item.equipmentCategory,
          summary: item.summary,
          status: item.status
        })),
        corrections: this.updateLogs.filter(item => item.type === 'corrected').slice(0, 5),
        update_logs: this.updateLogs.slice(0, 5)
      };
    },
    async askKnowledgeAgent(payload) {
      const context = payload.knowledge_context;
      const contextText = JSON.stringify(context, null, 2);
      const questionWithContext = `请基于以下知识库页面内容回答问题。\n\n页面内容：\n${contextText}\n\n用户问题：${payload.message}`;
      try {
        const rag = await request.post('/api/rag/query', {
          question: questionWithContext,
          mode: 'hybrid'
        }, { service: 'tuantuan', timeout: 45000 });
        if (rag && rag.code === 200 && rag.data && rag.data.answer) {
          return {
            source: 'rag',
            response: rag.data.answer,
            thinking_process: [
              { content: '已读取当前知识库页面上下文' },
              { content: '已通过知识图谱 RAG 检索相关手册、案例与问答' }
            ]
          };
        }
      } catch (e) {
        console.warn('RAG fallback to unified chat:', e);
      }

      const ai = await request.post('/openclaw/chat', {
        conversation_id: payload.conversation_id,
        message: payload.message,
        system_prompt: `你是知识库助手。请只围绕当前设备检修知识库、知识网络、手册、故障案例、常见问答、审核沉淀和人工修正内容回答。\n\n当前页面上下文：\n${contextText}`,
        temperature: 0.3,
        max_tokens: 1000
      }, { service: 'tuantuan', timeout: 45000 });
      if (ai && ai.code === 200 && ai.data && ai.data.response) {
        return {
          source: 'openclaw',
          response: ai.data.response,
          thinking_process: [
            { content: 'RAG 服务不可用或无返回，已切换统一 AI 模型' },
            { content: '已注入当前知识库页面上下文' }
          ]
        };
      }
      throw new Error(ai?.message || '知识库问答失败');
    },
    focusOnPoi(poi) {
    },
    openPreferenceModal() {
      this.showPreferenceModal = true;
    },
    closePreferenceModal() {
      this.showPreferenceModal = false;
    },
    isCuisineSelected(c) {
      return this.preferences.favorite_cuisines.split(',').includes(c);
    },
    toggleCuisine(c) {
      let list = this.preferences.favorite_cuisines ? this.preferences.favorite_cuisines.split(',') : [];
      if (list.includes(c)) {
        list = list.filter(i => i !== c);
      } else {
        list.push(c);
      }
      this.preferences.favorite_cuisines = list.filter(i => i).join(',');
    },
    addCustomCuisine() {
      if (!this.customCuisine.trim()) return;
      this.toggleCuisine(this.customCuisine.trim());
      this.customCuisine = '';
    },
    isHabitSelected(h) {
      return this.preferences.dietary_habits.split(',').includes(h);
    },
    toggleHabit(h) {
      let list = this.preferences.dietary_habits ? this.preferences.dietary_habits.split(',') : [];
      if (list.includes(h)) {
        list = list.filter(i => i !== h);
      } else {
        list.push(h);
      }
      this.preferences.dietary_habits = list.filter(i => i).join(',');
    },
    async loadPreferences() {
      try {
        const token = uni.getStorageSync('token');
        if (!token) return;

        const result = await uni.request({
          url: `${USER_API_BASE}/preferences`,
          method: 'GET',
          header: { 'Authorization': `Bearer ${token}` }
        });
        const res = Array.isArray(result) ? result[1] : result;
        if (res?.data?.code === 200) {
          this.preferences = res.data.data;
        }
      } catch (err) {
        console.error('Failed to load preferences:', err);
      }
    },
    async savePreferences() {
      try {
        const token = uni.getStorageSync('token');
        if (!token) {
          uni.showToast({ title: '请先登录', icon: 'none' });
          return;
        }

        const result = await uni.request({
          url: `${USER_API_BASE}/preferences`,
          method: 'POST',
          header: { 
            'Authorization': `Bearer ${token}`,
            'content-type': 'application/json'
          },
          data: this.preferences
        });
        
        const res = Array.isArray(result) ? result[1] : result;
        if (res?.data?.code === 200) {
          uni.showToast({ title: '路径智能体已记住你的偏好', icon: 'success' });
          this.closePreferenceModal();
        } else {
          uni.showToast({ title: '保存失败', icon: 'none' });
        }
      } catch (err) {
        console.error('Failed to save preferences:', err);
        uni.showToast({ title: '网络错误', icon: 'none' });
      }
    },

    // 知识库方法
    loadKbData() {
      try {
        const s = uni.getStorageSync('kb_data')
        if (s) {
          const d = JSON.parse(s)
          if (d.nodes) this.kbNodes = d.nodes
          if (d.connections) this.kbConnections = d.connections
          if (d.mindRoot) this.mindRoot = d.mindRoot
          if (d.caseItems) this.caseItems = d.caseItems
          if (d.pendingReviewItems) this.pendingReviewItems = d.pendingReviewItems
          if (d.updateLogs) this.updateLogs = d.updateLogs
        }
      } catch (e) {}
    },
    saveKbData() {
      try {
        uni.setStorageSync('kb_data', JSON.stringify({
          nodes: this.kbNodes,
          connections: this.kbConnections,
          mindRoot: this.mindRoot,
          caseItems: this.caseItems,
          pendingReviewItems: this.pendingReviewItems,
          updateLogs: this.updateLogs
        }))
      } catch (e) {}
    },
    switchKbTab(i) {
      this.currentKbTab = i
      this.selectedNode = null
      this.showLabels = false
      if (i === 0) {
        this.$nextTick(() => {
          this.graphReset()
        })
      }
    },
    openDocReader(item) {
      this.docReader = { ...item, _fav: false, _inKB: false }
    },
    openFileReader(file) {
      this.docReader = {
        title: file.name,
        source: file.uploader,
        equipmentCategory: file.equipmentName || '',
        tags: file.tags || [],
        content: file.readContent || '暂无预览内容。此文件需要下载后使用对应应用程序打开。\n\n文件信息：\n- 类型：' + (file.ext || file.type).toUpperCase() + '\n- 大小：' + this.formatFileSize(file.size) + '\n- 上传人：' + file.uploader + '\n- 更新时间：' + file.updateTime,
        rating: 0,
        _fav: false,
        _inKB: file.inKnowledgeBase || false,
      }
    },
    formatFileSize(bytes) {
      if (!bytes) return '--'
      if (bytes < 1048576) return (bytes / 1024).toFixed(0) + ' KB'
      return (bytes / 1048576).toFixed(1) + ' MB'
    },
    selectNode(node) { this.selectedNode = node; this.currentKbTab = 0; this.$nextTick(() => this.drawGraph()) },
    getNodeConns(node) {
      const nMap = this.nodeMap
      return this.kbConnections
        .filter(c => c.from === node.id || c.to === node.id)
        .map(c => nMap[c.from === node.id ? c.to : c.from])
        .filter(Boolean)
    },
    focusNode(node) { this.selectedNode = node; this.drawGraph() },
    graphZoomIn() { this.graphDrag.scale = Math.min(3, this.graphDrag.scale * 1.25); this.drawGraph() },
    graphZoomOut() { this.graphDrag.scale = Math.max(0.3, this.graphDrag.scale / 1.25); this.drawGraph() },
    graphReset() {
      // 重新归零节点坐标
      if (this.kbNodes.length > 0) {
        let sumX = 0, sumY = 0
        this.kbNodes.forEach(nd => { sumX += nd.x; sumY += nd.y })
        const cx = sumX / this.kbNodes.length, cy = sumY / this.kbNodes.length
        this.kbNodes.forEach(nd => { nd.x -= cx; nd.y -= cy })
      }
      this.graphDrag.scale = 1; this.graphDrag.offsetX = 0; this.graphDrag.offsetY = 0
      this.selectedNode = null; this.showLabels = false; this.graphFilterCategory = ''
      this.drawGraph()
    },
    goToKnowledgeDetail(node) {
      const nodeData = {
        id: node.id,
        title: node.label,
        category: node.category,
        icon: node.icon,
        desc: node.desc,
        tags: node.tags,
        reviewStatus: node.reviewStatus
      }
      uni.setStorageSync('selectedGraphNode', JSON.stringify(nodeData))
      uni.navigateTo({
        url: `/pages/knowledge-detail/knowledge-detail?id=${node.id}&title=${encodeURIComponent(node.label)}`,
        fail: (err) => {
          console.error('导航失败:', err)
          uni.showToast({ title: '页面跳转失败', icon: 'none' })
        }
      })
    },
    highlightAdjacent(node) {
      this.selectedNode = node
      this.drawGraph()
    },
    centerOnNode(node) {
      this.graphDrag.offsetX = -node.x * this.graphDrag.scale
      this.graphDrag.offsetY = -node.y * this.graphDrag.scale
      this.selectedNode = node
      this.drawGraph()
    },
    mindZoomIn() { this.mindDrag.scale = Math.min(3, this.mindDrag.scale * 1.25); this.drawMindMap() },
    mindZoomOut() { this.mindDrag.scale = Math.max(0.3, this.mindDrag.scale / 1.25); this.drawMindMap() },
    _getTouchPos(e) {
      const t = e.touches && e.touches[0] ? e.touches[0] : (e.changedTouches && e.changedTouches[0] ? e.changedTouches[0] : null)
      if (!t) return null
      return { x: t.x || t.clientX || 0, y: t.y || t.clientY || 0 }
    },
    _getPinchDist(e) {
      if (!e.touches || e.touches.length < 2) return 0
      const a = e.touches[0], b = e.touches[1]
      return Math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2)
    },
    onGraphTouchStart(e) {
      if (e.touches && e.touches.length >= 2) {
        this.graphDrag.pinchDist = this._getPinchDist(e); return
      }
      const t = this._getTouchPos(e); if (!t) return
      this.graphDrag.startX = t.x; this.graphDrag.startY = t.y; this.graphDrag.dragging = false
      this._touchStartTime = Date.now()
    },
    onGraphTouchMove(e) {
      if (e.touches && e.touches.length >= 2) {
        const dist = this._getPinchDist(e)
        if (this.graphDrag.pinchDist > 0) {
          const ratio = dist / this.graphDrag.pinchDist
          this.graphDrag.scale = Math.max(0.3, Math.min(3, this.graphDrag.scale * ratio))
          this.graphDrag.pinchDist = dist
          this.drawGraph()
        }
        return
      }
      const t = this._getTouchPos(e); if (!t) return
      const dx = t.x - this.graphDrag.startX, dy = t.y - this.graphDrag.startY
      if (Math.abs(dx) > 8 || Math.abs(dy) > 8) this.graphDrag.dragging = true
      if (this.graphDrag.dragging) {
        this.graphDrag.offsetX += dx; this.graphDrag.offsetY += dy
        this.graphDrag.startX = t.x; this.graphDrag.startY = t.y
        this.drawGraph()
      }
    },
    onGraphTouchEnd(e) {
      this.graphDrag.pinchDist = 0
      const touchDuration = Date.now() - (this._touchStartTime || 0)
      // 短按（<300ms）或非拖拽状态都视为点击
      const isTap = !this.graphDrag.dragging || touchDuration < 300
      if (isTap) {
        const t = this._getTouchPos(e); if (!t) return
        let n = null, min = 60
        const s = this.graphDrag.scale
        const sys = uni.getSystemInfoSync()
        const cw = this.canvasW || sys.windowWidth || 375
        const ch = this.canvasH || (sys.windowHeight * 0.6) || 600
        const cx = cw / 2, cy = ch / 2
        this.kbNodes.forEach(nd => {
          const sx = nd.x * s + cx + this.graphDrag.offsetX
          const sy = nd.y * s + cy + this.graphDrag.offsetY
          const r = 28 * s + 12  // 节点半径 + 容差
          const d = Math.sqrt((sx - t.x) ** 2 + (sy - t.y) ** 2)
          if (d < r && d < min) { min = d; n = nd }
        })
        if (n) {
          // 单击节点 → 存储数据并跳转详情
          this.selectedNode = n
          this.showLabels = true
          this.drawGraph()
          this.goToKnowledgeDetail(n)
        } else {
          this.selectedNode = null
          this.showLabels = false
          this.drawGraph()
        }
      }
      this.graphDrag.dragging = false
    },
    _hexToRgba(hex, alpha) {
      const r = parseInt(hex.slice(1, 3), 16), g = parseInt(hex.slice(3, 5), 16), b = parseInt(hex.slice(5, 7), 16)
      return `rgba(${r},${g},${b},${alpha})`
    },
    drawGraph() {
      const ctx = uni.createCanvasContext('kbGraph', this)
      uni.createSelectorQuery().in(this).select('#kbGraph').boundingClientRect(rect => {
        const sys = uni.getSystemInfoSync()
        const w = (rect && rect.width) || sys.windowWidth || 375
        const h = (rect && rect.height) || (sys.windowHeight * 0.6) || 600
        this.canvasW = w; this.canvasH = h
        ctx.clearRect(0, 0, w, h)
        const ox = this.graphDrag.offsetX, oy = this.graphDrag.offsetY, sc = this.graphDrag.scale
        const cx = w / 2, cy = h / 2
        const nMap = this.nodeMap

        // 计算每个节点的连接度
        const degreeMap = {}
        this.kbNodes.forEach(nd => { degreeMap[nd.id] = 0 })
        this.kbConnections.forEach(c => {
          if (degreeMap[c.from] !== undefined) degreeMap[c.from]++
          if (degreeMap[c.to] !== undefined) degreeMap[c.to]++
        })

        // 搜索匹配函数
        const searchKw = (this.kbSearchText || '').trim().toLowerCase()
        const matchSearch = (nd) => {
          if (!searchKw) return true
          return nd.label.toLowerCase().includes(searchKw) ||
            (nd.desc || '').toLowerCase().includes(searchKw) ||
            (nd.tags || []).some(t => t.toLowerCase().includes(searchKw))
        }

        // 判断节点是否应变暗
        const isNodeDimmed = (nd) => {
          const sel = this.selectedNode
          const cat = this.graphFilterCategory
          // 分类筛选
          if (cat && nd.category !== cat) return true
          // 搜索
          if (searchKw && !matchSearch(nd)) return true
          // 选中节点的邻居逻辑
          if (sel && sel.id !== nd.id && !this._isAdjacent(nd.id)) return true
          return false
        }

        // 浅色渐变背景
        const bgGrad = ctx.createLinearGradient(0, 0, 0, h)
        bgGrad.addColorStop(0, '#F8FAFF')
        bgGrad.addColorStop(1, '#F0F4FA')
        ctx.setFillStyle(bgGrad)
        ctx.fillRect(0, 0, w, h)

        // 浅灰网格线
        ctx.setStrokeStyle('rgba(0,0,0,0.03)')
        ctx.setLineWidth(1)
        const gridGap = 60 * sc
        for (let gx = ox % gridGap; gx < w; gx += gridGap) {
          ctx.beginPath(); ctx.moveTo(gx, 0); ctx.lineTo(gx, h); ctx.stroke()
        }
        for (let gy = oy % gridGap; gy < h; gy += gridGap) {
          ctx.beginPath(); ctx.moveTo(0, gy); ctx.lineTo(w, gy); ctx.stroke()
        }

        const sx = (nd) => nd.x * sc + cx + ox
        const sy = (nd) => nd.y * sc + cy + oy

        // ── 连线 ──
        this.kbConnections.forEach((c) => {
          const fNode = nMap[c.from], tNode = nMap[c.to]
          if (!fNode || !tNode) return
          const fx = sx(fNode), fy = sy(fNode), tx = sx(tNode), ty = sy(tNode)

          const sel = this.selectedNode
          const isActive = sel && (sel.id === c.from || sel.id === c.to)
          const catFilter = this.graphFilterCategory
          const bothMatchCat = (!catFilter) || (fNode.category === catFilter && tNode.category === catFilter)
          const bothMatchSearch = !searchKw || (matchSearch(fNode) && matchSearch(tNode))
          const dimmed = (sel && !isActive) || (catFilter && !bothMatchCat) || (searchKw && !bothMatchSearch)

          // 微弧线（中点偏移）
          const mx = (fx + tx) / 2, my = (fy + ty) / 2
          const dx = tx - fx, dy = ty - fy
          const dist = Math.sqrt(dx * dx + dy * dy) || 1
          const curvature = 0.08
          const cpx = mx + (-dy / dist) * dist * curvature
          const cpy = my + (dx / dist) * dist * curvature

          if (isActive) {
            // 发光效果：先画粗的半透明线
            ctx.setStrokeStyle(this._hexToRgba('#0EA5E9', 0.25))
            ctx.setLineWidth(6 * sc)
            ctx.beginPath(); ctx.moveTo(fx, fy); ctx.quadraticCurveTo(cpx, cpy, tx, ty); ctx.stroke()
          }

          ctx.setStrokeStyle(dimmed ? 'rgba(0,0,0,0.03)' : isActive ? '#0EA5E9' : 'rgba(0,0,0,0.08)')
          ctx.setLineWidth(isActive ? 2.5 * sc : 1.2 * sc)
          ctx.beginPath(); ctx.moveTo(fx, fy); ctx.quadraticCurveTo(cpx, cpy, tx, ty); ctx.stroke()

          // 小箭头（非变暗时）
          if (!dimmed && sc > 0.4) {
            const arrowLen = 8 * sc
            const t = 0.55
            // 曲线中点切线方向
            const ax = 2 * (1 - t) * (cpx - fx) + 2 * t * (tx - cpx)
            const ay = 2 * (1 - t) * (cpy - fy) + 2 * t * (ty - cpy)
            const al = Math.sqrt(ax * ax + ay * ay) || 1
            const px = fx + (1 - t) * (1 - t) * (cpx - fx) * 2 + 2 * (1 - t) * t * (cpx - fx) + t * t * (tx - fx)
            // 简化：直接用参数方程求中点
            const mt = (1 - t) * (1 - t) * fx + 2 * (1 - t) * t * cpx + t * t * tx
            const my2 = (1 - t) * (1 - t) * fy + 2 * (1 - t) * t * cpy + t * t * ty
            const angle = Math.atan2(ay, ax)
            ctx.setFillStyle(isActive ? '#0EA5E9' : 'rgba(0,0,0,0.12)')
            ctx.beginPath()
            ctx.moveTo(mt + Math.cos(angle) * arrowLen, my2 + Math.sin(angle) * arrowLen)
            ctx.lineTo(mt + Math.cos(angle + 2.5) * arrowLen * 0.6, my2 + Math.sin(angle + 2.5) * arrowLen * 0.6)
            ctx.lineTo(mt + Math.cos(angle - 2.5) * arrowLen * 0.6, my2 + Math.sin(angle - 2.5) * arrowLen * 0.6)
            ctx.closePath(); ctx.fill()
          }
        })

        // ── 节点 ──
        this.kbNodes.forEach(nd => {
          const x = sx(nd), y = sy(nd)
          const sel = this.selectedNode && this.selectedNode.id === nd.id
          const color = this.categoryColors[nd.category] || '#0F766E'
          const dimmed = isNodeDimmed(nd)
          const deg = degreeMap[nd.id] || 1
          const baseR = Math.min(28, 18 + deg * 2)
          const r = (sel ? baseR + 4 : baseR) * sc

          // 选中外圈光晕
          if (sel) {
            for (let g = 3; g >= 1; g--) {
              ctx.beginPath(); ctx.arc(x, y, r + (4 + g * 4) * sc, 0, Math.PI * 2)
              ctx.setFillStyle(this._hexToRgba(color, 0.04 * g)); ctx.fill()
            }
            ctx.beginPath(); ctx.arc(x, y, r + 4 * sc, 0, Math.PI * 2)
            ctx.setFillStyle(this._hexToRgba(color, 0.15)); ctx.fill()
          }

          // 搜索匹配的非选中节点发光
          if (!sel && !dimmed && searchKw && matchSearch(nd)) {
            ctx.beginPath(); ctx.arc(x, y, r + 6 * sc, 0, Math.PI * 2)
            ctx.setFillStyle(this._hexToRgba('#FBBF24', 0.18)); ctx.fill()
          }

          // 节点阴影
          if (!dimmed) {
            ctx.setFillStyle('rgba(0,0,0,0.06)')
            ctx.beginPath(); ctx.arc(x + 1 * sc, y + 2 * sc, r, 0, Math.PI * 2); ctx.fill()
          }

          // 节点圆形背景（渐变）
          ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI * 2)
          if (dimmed) {
            ctx.setFillStyle('#F1F5F9')
          } else {
            const nodeGrad = ctx.createLinearGradient(x - r, y - r, x + r, y + r)
            nodeGrad.addColorStop(0, '#FFFFFF')
            nodeGrad.addColorStop(1, this._hexToRgba(color, 0.06))
            ctx.setFillStyle(nodeGrad)
          }
          ctx.fill()
          ctx.setStrokeStyle(dimmed ? '#E2E8F0' : color)
          ctx.setLineWidth(sel ? 3 * sc : 2 * sc)
          ctx.stroke()

          // 图标
          if (nd.icon) {
            ctx.setFontSize(Math.max(14, (sel ? 22 : 18) * sc))
            ctx.setTextAlign('center'); ctx.setTextBaseline('middle')
            ctx.setFillStyle(dimmed ? '#CBD5E1' : '#334155')
            ctx.fillText(nd.icon, x, y - 1 * sc)
          }

          // 标签（带背景底色）— 默认隐藏，选中/搜索时显示
          const label = nd.label
          const shouldShowLabel = this.showLabels || sel || !!searchKw || (!dimmed && !!this.selectedNode)
          const labelY = y + r + 6 * sc
          if (shouldShowLabel) {
            ctx.setFontSize(Math.max(10, 12 * sc))
            ctx.setTextAlign('center'); ctx.setTextBaseline('top')
            if (!dimmed) {
              const lw = ctx.measureText ? ctx.measureText(label).width : label.length * 12 * sc
              ctx.setFillStyle('rgba(255,255,255,0.85)')
              this._roundRect(ctx, x - lw / 2 - 6 * sc, labelY - 2 * sc, lw + 12 * sc, 18 * sc, 4 * sc)
              ctx.fill()
            }
            ctx.setFillStyle(dimmed ? '#CBD5E1' : '#1E293B')
            ctx.fillText(label, x, labelY)
          }

          // 分类小标签
          if (!dimmed && sc > 0.4 && shouldShowLabel) {
            const cat = nd.category
            ctx.setFontSize(Math.max(8, 9 * sc))
            const tw = ctx.measureText ? ctx.measureText(cat).width : cat.length * 9 * sc
            const tagW = tw + 14 * sc, tagH = 18 * sc, tagX = x - tagW / 2, tagY = labelY + 20 * sc
            ctx.setFillStyle(this._hexToRgba(color, 0.1))
            ctx.beginPath()
            this._roundRect(ctx, tagX, tagY, tagW, tagH, 6 * sc); ctx.fill()
            ctx.setStrokeStyle(this._hexToRgba(color, 0.2))
            ctx.setLineWidth(1)
            ctx.beginPath()
            this._roundRect(ctx, tagX, tagY, tagW, tagH, 6 * sc); ctx.stroke()
            ctx.setFillStyle(color)
            ctx.setTextAlign('center'); ctx.setTextBaseline('middle')
            ctx.fillText(cat, x, tagY + tagH / 2)
          }

          // 审核状态角标
          if (!dimmed && nd.reviewStatus) {
            const badgeColors = { approved: '#10B981', pending: '#F59E0B', corrected: '#EF4444' }
            const badgeColor = badgeColors[nd.reviewStatus] || '#94A3B8'
            const bx = x + r * 0.7, by = y - r * 0.7
            ctx.beginPath(); ctx.arc(bx, by, 5 * sc, 0, Math.PI * 2)
            ctx.setFillStyle(badgeColor); ctx.fill()
            ctx.setStrokeStyle('#FFFFFF'); ctx.setLineWidth(1.5 * sc); ctx.stroke()
          }
        })

        ctx.draw()
      }).exec()
    },

    _roundRect(ctx, x, y, w, h, r) {
      r = Math.min(r, w / 2, h / 2)
      ctx.moveTo(x + r, y)
      ctx.arcTo(x + w, y, x + w, y + h, r)
      ctx.arcTo(x + w, y + h, x, y + h, r)
      ctx.arcTo(x, y + h, x, y, r)
      ctx.arcTo(x, y, x + w, y, r)
      ctx.closePath()
    },

    _isAdjacent(nodeId) {
      if (!this.selectedNode) return false
      const selId = this.selectedNode.id
      return this.kbConnections.some(c =>
        (c.from === selId && c.to === nodeId) || (c.to === selId && c.from === nodeId)
      )
    },

    startGraphAnimation() {
      // 将节点坐标归零到原点（画布中心）
      if (this.kbNodes.length > 0) {
        let sumX = 0, sumY = 0
        this.kbNodes.forEach(nd => { sumX += nd.x; sumY += nd.y })
        const cx = sumX / this.kbNodes.length, cy = sumY / this.kbNodes.length
        this.kbNodes.forEach(nd => { nd.x -= cx; nd.y -= cy })
      }
      this._forceVx = {}
      this._forceVy = {}
      this.kbNodes.forEach(nd => { this._forceVx[nd.id] = 0; this._forceVy[nd.id] = 0 })
      this._forceStep = 0
      this._forceTimer = setInterval(() => { this._stepForce() }, 50)
    },

    stopGraphAnimation() {
      if (this._forceTimer) { clearInterval(this._forceTimer); this._forceTimer = null }
    },

    _stepForce() {
      const nodes = this.kbNodes
      const conns = this.kbConnections
      const nMap = this.nodeMap
      const vx = this._forceVx, vy = this._forceVy
      const fx = {}, fy = {}
      nodes.forEach(nd => { fx[nd.id] = 0; fy[nd.id] = 0 })

      // 斥力
      for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
          const a = nodes[i], b = nodes[j]
          let dx = a.x - b.x, dy = a.y - b.y
          let d = Math.sqrt(dx * dx + dy * dy) || 1
          let f = Math.min(6000 / (d * d), 6)
          fx[a.id] += (dx / d) * f; fy[a.id] += (dy / d) * f
          fx[b.id] -= (dx / d) * f; fy[b.id] -= (dy / d) * f
        }
      }

      // 连线引力
      conns.forEach(c => {
        const a = nMap[c.from], b = nMap[c.to]
        if (!a || !b) return
        let dx = b.x - a.x, dy = b.y - a.y
        let d = Math.sqrt(dx * dx + dy * dy) || 1
        let f = (d - 160) * 0.006
        fx[a.id] += (dx / d) * f; fy[a.id] += (dy / d) * f
        fx[b.id] -= (dx / d) * f; fy[b.id] -= (dy / d) * f
      })

      // 中心引力
      nodes.forEach(nd => { fx[nd.id] -= nd.x * 0.001; fy[nd.id] -= nd.y * 0.001 })

      // 更新位置
      let totalMove = 0
      nodes.forEach(nd => {
        vx[nd.id] = ((vx[nd.id] || 0) + fx[nd.id]) * 0.55
        vy[nd.id] = ((vy[nd.id] || 0) + fy[nd.id]) * 0.55
        vx[nd.id] = Math.max(-6, Math.min(6, vx[nd.id]))
        vy[nd.id] = Math.max(-6, Math.min(6, vy[nd.id]))
        nd.x += vx[nd.id]; nd.y += vy[nd.id]
        totalMove += Math.abs(vx[nd.id]) + Math.abs(vy[nd.id])
      })

      this._forceStep++
      this.drawGraph()
      if (this._forceStep >= 180 || totalMove < 0.3) this.stopGraphAnimation()
    },
    onMindTouchStart(e) {
      if (e.touches && e.touches.length >= 2) {
        this.mindDrag.pinchDist = this._getPinchDist(e); return
      }
      const t = this._getTouchPos(e); if (!t) return
      this.mindDrag.startX = t.x; this.mindDrag.startY = t.y; this.mindDrag.dragging = false
    },
    onMindTouchMove(e) {
      if (e.touches && e.touches.length >= 2) {
        const dist = this._getPinchDist(e)
        if (this.mindDrag.pinchDist > 0) {
          const ratio = dist / this.mindDrag.pinchDist
          this.mindDrag.scale = Math.max(0.3, Math.min(3, this.mindDrag.scale * ratio))
          this.mindDrag.pinchDist = dist
          this.drawMindMap()
        }
        return
      }
      const t = this._getTouchPos(e); if (!t) return
      const dx = t.x - this.mindDrag.startX, dy = t.y - this.mindDrag.startY
      if (Math.abs(dx) > 8 || Math.abs(dy) > 8) this.mindDrag.dragging = true
      if (this.mindDrag.dragging) {
        this.mindDrag.offsetX += dx; this.mindDrag.offsetY += dy
        this.mindDrag.startX = t.x; this.mindDrag.startY = t.y
        this.drawMindMap()
      }
    },
    onMindTouchEnd(e) { this.mindDrag.pinchDist = 0; this.mindDrag.dragging = false },
    drawMindMap() {
      if (!this.mindRoot) return; const ctx = uni.createCanvasContext('kbMind', this)
      uni.createSelectorQuery().in(this).select('#kbMind').boundingClientRect(rect => {
        if (!rect) return; const w = rect.width, h = rect.height; ctx.clearRect(0, 0, w, h)
        this._mindScale = this.mindDrag.scale
        this._drawNode(ctx, this.mindRoot, 30 + this.mindDrag.offsetX, h / 2 + this.mindDrag.offsetY, 0)
        ctx.draw()
      }).exec()
    },
    _drawNode(ctx, node, x, y, depth) {
      if (!node) return
      const sc = this._mindScale || 1
      const tw = (node.label.length * 14 + 24) * sc, nh = 32 * sc
      const colors = ['#0F766E', '#14B8A6', '#0369A1', '#0EA5E9', '#06B6D4'], color = colors[depth % colors.length]
      const r = 12 * sc
      ctx.beginPath(); ctx.moveTo(x + r, y - nh / 2); ctx.lineTo(x + tw - r, y - nh / 2); ctx.arc(x + tw - r, y - nh / 2 + r, r, -Math.PI / 2, 0); ctx.lineTo(x + tw, y + nh / 2 - r); ctx.arc(x + tw - r, y + nh / 2 - r, r, 0, Math.PI / 2); ctx.lineTo(x + r, y + nh / 2); ctx.arc(x + r, y + nh / 2 - r, r, Math.PI / 2, Math.PI); ctx.lineTo(x, y - nh / 2 + r); ctx.arc(x + r, y - nh / 2 + r, r, Math.PI, -Math.PI / 2); ctx.closePath()
      if (depth === 0) { ctx.setFillStyle(color); ctx.fill(); ctx.setFillStyle('#fff') } else { ctx.setFillStyle('#fff'); ctx.fill(); ctx.setStrokeStyle(color); ctx.setLineWidth(2 * sc); ctx.stroke(); ctx.setFillStyle('#0F766E') }
      ctx.setFontSize(Math.max(8, (depth === 0 ? 14 : 12) * sc)); ctx.setTextAlign('center')
      ctx.fillText(node.label, x + tw / 2, y + 4 * sc)
      if (node.children && !node.collapsed) {
        const cnt = node.children.length; let sy = y - (cnt * 44 * sc) / 2 + 22 * sc, cx = x + tw + 40 * sc
        node.children.forEach((child, i) => {
          const cy = sy + i * 44 * sc
          ctx.beginPath(); ctx.moveTo(x + tw, y); ctx.bezierCurveTo(x + tw + 20 * sc, y, cx - 20 * sc, cy, cx, cy)
          ctx.setStrokeStyle('rgba(15,118,110,0.25)'); ctx.setLineWidth(1.5 * sc); ctx.stroke()
          this._drawNode(ctx, child, cx, cy, depth + 1)
        })
      }
      if (node.children && node.children.length > 0 && node.collapsed) { ctx.setFillStyle('#0F766E'); ctx.setFontSize(16 * sc); ctx.fillText('+', x + tw + 10 * sc, y + 4 * sc) }
    },
    expandAllMind() { this._setCol(this.mindRoot, false); this.drawMindMap() },
    collapseAllMind() { this._setCol(this.mindRoot, true); if (this.mindRoot) this.mindRoot.collapsed = false; this.drawMindMap() },
    _setCol(n, v) { if (!n) return; n.collapsed = v; if (n.children) n.children.forEach(c => this._setCol(c, v)) },
    onSeverityChange(e) {
      const index = Number(e.detail.value || 0)
      this.newCaseForm.severity = this.caseSeverityOptions[index]?.value || 'medium'
    },
    mockAttachEvidence() {
      this.newCaseForm.evidenceName = this.newCaseForm.evidenceName || '现场照片_检测数据.zip'
      uni.showToast({ title: '已添加模拟附件', icon: 'success' })
    },
    submitCaseForReview() {
      const title = this.newCaseForm.title.trim()
      const summary = this.newCaseForm.summary.trim()
      if (!title || !summary) {
        uni.showToast({ title: '请填写标题和内容', icon: 'none' })
        return
      }
      const tags = this.newCaseForm.tagsStr.split(/[,，]/).map(s => s.trim()).filter(Boolean)
      const item = {
        id: `r${Date.now()}`,
        title,
        source: '一线人员上传',
        equipmentCategory: this.newCaseForm.equipmentCategory.trim() || '通用设备',
        tags: tags.length ? tags : ['待补充标签'],
        severity: this.newCaseForm.severity,
        summary,
        content: `故障/经验描述：${summary}\n\n附件：${this.newCaseForm.evidenceName || '暂无附件'}\n\n审核建议：补充来源、现象、排查过程和处理结论后纳入知识图谱。`,
        status: 'pending',
        author: this.getCurrentUserName(),
        submittedAt: this.formatNow()
      }
      this.pendingReviewItems.unshift(item)
      this.prependUpdateLog('review', '新检修内容已提交审核', `${item.title} 已进入审核入库队列。`)
      this.resetCaseForm()
      this.saveKbData()
      uni.showToast({ title: '已提交审核', icon: 'success' })
    },
    resetCaseForm() {
      this.newCaseForm = {
        title: '',
        equipmentCategory: '',
        severity: 'medium',
        summary: '',
        tagsStr: '',
        evidenceName: ''
      }
    },
    approveReviewItem(item) {
      item.status = 'approved'
      const caseItem = {
        id: `c${Date.now()}`,
        title: item.title,
        source: item.source || '审核入库',
        equipmentCategory: item.equipmentCategory,
        tags: item.tags,
        severity: item.severity,
        summary: item.summary,
        content: item.content || item.summary,
        viewCount: 0,
        rating: 5,
        updatedAt: this.formatDate()
      }
      this.caseItems.unshift(caseItem)
      this.addGraphNodeFromReview(item)
      this.prependUpdateLog('approved', '审核通过并同步知识图谱', `${item.title} 已纳入案例库，并生成案例库节点。`)
      this.saveKbData()
      this.$nextTick(() => this.drawGraph())
      uni.showToast({ title: '已审核入库', icon: 'success' })
    },
    rejectReviewItem(item) {
      item.status = 'rejected'
      this.prependUpdateLog('rejected', '内容已退回补充', `${item.title} 需要补充检测依据或处理结论。`)
      this.saveKbData()
      uni.showToast({ title: '已退回补充', icon: 'none' })
    },
    addGraphNodeFromReview(item) {
      const count = this.kbNodes.length
      const angle = count * 0.72
      const radius = 120 + count * 18
      const newId = Date.now()
      const caseHub = this.kbNodes.find(node => node.category === '案例库')
      const equipmentNode = this.kbNodes.find(node => item.equipmentCategory && node.label.includes(item.equipmentCategory))
      this.kbNodes.push({
        id: newId,
        label: item.title,
        category: '案例库',
        icon: '🧰',
        desc: item.summary,
        tags: item.tags,
        x: Math.cos(angle) * radius,
        y: Math.sin(angle) * radius,
        reviewStatus: 'approved'
      })
      if (caseHub) this.kbConnections.push({ from: caseHub.id, to: newId })
      if (equipmentNode) this.kbConnections.push({ from: equipmentNode.id, to: newId })
    },
    toggleCorrectionTag(tag) {
      const index = this.modelCorrection.tags.indexOf(tag)
      if (index >= 0) this.modelCorrection.tags.splice(index, 1)
      else this.modelCorrection.tags.push(tag)
    },
    saveModelCorrection() {
      const text = this.modelCorrection.correctedText.trim()
      if (!text) {
        uni.showToast({ title: '请填写修正内容', icon: 'none' })
        return
      }
      const newId = Date.now()
      const correctionHub = this.kbNodes.find(node => node.label === '人工修正')
      this.kbNodes.push({
        id: newId,
        label: `模型修正-${this.formatDate()}`,
        category: '更新机制',
        icon: '✍️',
        desc: text,
        tags: this.modelCorrection.tags.length ? [...this.modelCorrection.tags] : ['人工修正'],
        x: 260 + Math.random() * 80,
        y: 560 + Math.random() * 60,
        reviewStatus: 'corrected'
      })
      if (correctionHub) this.kbConnections.push({ from: correctionHub.id, to: newId })
      this.prependUpdateLog('corrected', '模型输出已人工修正', `标注：${this.modelCorrection.tags.join('、') || '人工修正'}。`)
      this.saveKbData()
      this.$nextTick(() => this.drawGraph())
      uni.showToast({ title: '修正已保存', icon: 'success' })
    },
    prependUpdateLog(type, title, desc) {
      this.updateLogs.unshift({
        id: `u${Date.now()}${Math.random().toString(16).slice(2, 6)}`,
        type,
        title,
        desc,
        time: this.formatNow()
      })
    },
    getReviewStatusText(status) {
      if (status === 'approved') return '已入库'
      if (status === 'rejected') return '待补充'
      return '待审核'
    },
    getCurrentUserName() {
      const user = uni.getStorageSync('user') || {}
      return user.name || user.username || '当前一线人员'
    },
    getUploadStatusText(status) {
      const map = { pending: '审核中', approved: '已入库', rejected: '待补充' }
      return map[status] || '未知'
    },
    getUploadProgressWidth(status) {
      const map = { pending: '60%', approved: '100%', rejected: '40%' }
      return map[status] || '0%'
    },
    formatDate() {
      const d = new Date()
      const m = String(d.getMonth() + 1).padStart(2, '0')
      const day = String(d.getDate()).padStart(2, '0')
      return `${d.getFullYear()}-${m}-${day}`
    },
    formatNow() {
      const d = new Date()
      const h = String(d.getHours()).padStart(2, '0')
      const m = String(d.getMinutes()).padStart(2, '0')
      return `${this.formatDate()} ${h}:${m}`
    },
    addKbNode() {
      if (!this.newNode.label.trim()) { uni.showToast({ title: '请输入名称', icon: 'none' }); return }
      const catIcons = { '设备': '🔧', '故障现象': '⚠️', '检修流程': '📋', '多模态证据': '🖼️', '检修手册': '📘', '案例库': '🧰', '更新机制': '✍️' }
      const cat = this.newNode.category.trim() || '未分类'
      const count = this.kbNodes.length
      const angle = count * 0.8, radius = 80 + count * 25
      this.kbNodes.push({
        id: Date.now(), label: this.newNode.label.trim(), category: cat,
        desc: this.newNode.desc.trim(),
        tags: this.newNode.tagsStr.split(/[,，]/).map(s => s.trim()).filter(Boolean),
        icon: catIcons[cat] || '📄',
        x: Math.cos(angle) * radius, y: Math.sin(angle) * radius
      })
      this.saveKbData(); this.drawGraph(); this.showAddNode = false
      this.newNode = { label: '', category: '', desc: '', tagsStr: '' }
      uni.showToast({ title: '添加成功', icon: 'success' })
    },
  }
}
</script>
<style scoped>
page {
  width: 100%;
  height: 100%;
  overflow: hidden;
}

/* 核心布局 */
.map-recommendation-view {
  width: 100%;
  height: 100vh;
  position: relative;
  background-color: #F0FDFA;
  overflow: hidden;
  padding-top: 0;
}

.amap-container {
  width: 100%;
  height: 100%;
  z-index: 1;
}

/* 磨砂玻璃层容器*/
.overlay-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 10;
  pointer-events: none;
}

/* 顶部状态条 */
.top-nav-blur {
  padding: calc(80rpx + constant(safe-area-inset-top)) 30rpx 20rpx;
  padding: calc(80rpx + env(safe-area-inset-top)) 30rpx 20rpx;
  pointer-events: auto;
}

.location-chip {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(15px);
  -webkit-backdrop-filter: blur(15px);
  padding: 16rpx 30rpx;
  border-radius: 50rpx;
  display: inline-flex;
  align-items: center;
  box-shadow: 0 8rpx 32rpx rgba(0,0,0,0.08);
  border: 1px solid #99F6E4;
  max-width: 85%;
}

.loc-indicator {
  width: 24rpx;
  height: 24rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16rpx;
}

.pulse-dot {
  width: 12rpx;
  height: 12rpx;
  background: #0F766E;
  border-radius: 50%;
  box-shadow: 0 0 10rpx #0F766E;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { transform: scale(1); opacity: 1; }
  70% { transform: scale(2.5); opacity: 0; }
  100% { transform: scale(1); opacity: 0; }
}

.loc-name {
  font-size: 26rpx;
  color: #134E4A;
  font-weight: 500;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.loc-refresh {
  margin-left: 20rpx;
  font-size: 22rpx;
  color: #0F766E;
  font-weight: bold;
}

/* 偏好设置按钮与弹窗样式*/
.preference-btn {
  margin-top: 15rpx;
  background: rgba(255, 255, 255, 0.9) !important;
  box-shadow: 0 4rpx 12rpx rgba(0,0,0,0.15) !important;
}

.pref-icon {
  font-size: 32rpx;
}

.preference-modal-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  z-index: 2000;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(5px);
}

.preference-container {
  width: 85%;
  background: #fff;
  border-radius: 30rpx;
  overflow: hidden;
  animation: slideUp 0.3s ease-out;
  display: flex;
  flex-direction: column;
  max-height: 80vh;
  border: 2rpx solid #99F6E4;
}

@keyframes slideUp {
  from { transform: translateY(100rpx); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.modal-header {
  padding: 30rpx;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1rpx solid #E2E8F0;
  background: linear-gradient(135deg, #F0FDFA, #FFFFFF);
}

.modal-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #134E4A;
}

.close-icon {
  font-size: 40rpx;
  color: #94A3B8;
  padding: 10rpx;
}

.modal-body {
  padding: 30rpx;
  overflow-y: auto;
}

.pref-section {
  margin-bottom: 30rpx;
}

.section-title {
  font-size: 28rpx;
  color: #64748B;
  margin-bottom: 15rpx;
  display: block;
}

.pref-input {
  width: 100%;
  height: 80rpx;
  background: #F0FDFA;
  border-radius: 12rpx;
  padding: 0 20rpx;
  font-size: 26rpx;
  box-sizing: border-box;
  border: 1rpx solid #99F6E4;
}

.pref-textarea {
  width: 100%;
  height: 150rpx;
  background: #F0FDFA;
  border-radius: 12rpx;
  padding: 20rpx;
  font-size: 26rpx;
  box-sizing: border-box;
  border: 1rpx solid #99F6E4;
}

.mt-10 { margin-top: 10rpx; }

.tag-group {
  display: flex;
  flex-wrap: wrap;
  gap: 15rpx;
}

.tag-item {
  padding: 10rpx 25rpx;
  background: #F0FDFA;
  border-radius: 30rpx;
  font-size: 24rpx;
  color: #64748B;
  transition: all 0.2s;
  border: 1rpx solid #99F6E4;
}

.tag-item.active {
  background: #0F766E;
  color: #fff;
  border-color: #0F766E;
}

.modal-footer {
  padding: 30rpx;
  border-top: 1rpx solid #E2E8F0;
}

.save-pref-btn {
  width: 100%;
  height: 88rpx;
  background: linear-gradient(135deg, #0F766E, #14B8A6);
  color: #fff;
  border-radius: 44rpx;
  font-size: 30rpx;
  font-weight: bold;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 智能体卡片 - Trust Teal 配色方案 */
.agent-card {
  position: fixed;
  bottom: calc(80rpx + env(safe-area-inset-bottom));
  left: 30rpx;
  right: 30rpx;
  background: #ffffff;
  border-radius: 40rpx;
  box-shadow: 0 16rpx 48rpx rgba(0,0,0,0.12), 0 0 0 1rpx rgba(15, 118, 110, 0.08);
  pointer-events: auto;
  transition: transform 0.4s cubic-bezier(0.23, 1, 0.32, 1);
  overflow: hidden;
  z-index: 350;
  display: block !important;
  border: 1rpx solid #E2E8F0;
}

.card-collapsed {
  max-height: 140rpx !important;
  transform: translateY(0);
}

.card-header {
  padding: 30rpx 40rpx;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(135deg, #F0FDFA 0%, #E6F7F5 50%, #FFFFFF 100%);
  border-bottom: 1rpx solid #E2E8F0;
  position: relative;
}

.card-header::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 4rpx;
  background: linear-gradient(90deg, #0F766E, #14B8A6, #0EA5E9, #0369A1);
  background-size: 200% 100%;
  animation: gradientShift 3s ease infinite;
}

@keyframes gradientShift {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}

.header-main {
  display: flex;
  align-items: center;
}

.avatar-group {
  width: 80rpx;
  height: 80rpx;
  margin-right: 20rpx;
  border-radius: 50%;
  overflow: hidden;
  border: 3rpx solid #99F6E4;
  flex-shrink: 0;
}

.agent-img {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: #fff;
}

.header-text {
  display: flex;
  flex-direction: column;
}

.agent-title {
  font-size: 32rpx;
  font-weight: 700;
  color: #134E4A;
  letter-spacing: 1rpx;
}

.agent-badge {
  display: flex;
  align-items: center;
  margin-top: 4rpx;
}

.badge-dot {
  width: 10rpx;
  height: 10rpx;
  background: linear-gradient(135deg, #10B981, #0EA5E9);
  border-radius: 50%;
  margin-right: 8rpx;
  box-shadow: 0 0 8rpx rgba(14, 165, 233, 0.6);
  animation: dotPulse 2s ease infinite;
}

@keyframes dotPulse {
  0%, 100% { transform: scale(1); box-shadow: 0 0 8rpx rgba(14, 165, 233, 0.6); }
  50% { transform: scale(1.2); box-shadow: 0 0 12rpx rgba(14, 165, 233, 0.8); }
}

.badge-text {
  font-size: 20rpx;
  color: #64748B;
  text-transform: uppercase;
  font-weight: 600;
}

.toggle-arrow {
  font-size: 40rpx;
  color: #94A3B8;
  transition: transform 0.3s;
}

.toggle-arrow.up { transform: rotate(90deg); }
.toggle-arrow.down { transform: rotate(-90deg); }

/* 对话 */
.card-body {
  height: 60vh;
  display: flex;
  flex-direction: column;
  max-height: 900rpx;
  overflow: hidden;
}

.chat-viewport {
  flex: 1;
  padding: 20rpx 2.5% 60rpx;
  overflow-y: auto;
  overflow-x: hidden;
  -webkit-overflow-scrolling: touch;
  scroll-behavior: smooth;
  background: linear-gradient(180deg, #FFFFFF 0%, #F0FDFA 100%);
  position: relative;
  z-index: 1;
  box-sizing: border-box;
  width: 100%;
  min-height: 0;
}

.chat-viewport::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1rpx;
  background: linear-gradient(90deg, transparent 0%, rgba(15, 118, 110, 0.1) 50%, transparent 100%);
}

.chat-viewport::-webkit-scrollbar {
  width: 6rpx;
}

.chat-viewport::-webkit-scrollbar-track {
  background: transparent;
  border-radius: 3rpx;
}

.chat-viewport::-webkit-scrollbar-thumb {
  background: linear-gradient(to bottom, #0F766E, #14B8A6, #0EA5E9);
  border-radius: 3rpx;
  opacity: 0.6;
  box-shadow: inset 0 1rpx 2rpx rgba(0,0,0,0.1);
}

.chat-viewport::-webkit-scrollbar-thumb:hover {
  opacity: 1;
  box-shadow: inset 0 1rpx 2rpx rgba(0,0,0,0.15);
}

.message-row {
  margin-bottom: 24rpx;
  display: flex;
  flex-direction: row;
  align-items: flex-start;
  gap: 20rpx;
  animation: fadeInUp 0.3s ease-out;
  position: relative;
  max-width: 100%;
  overflow-x: hidden;
  overflow-y: visible;
}

.message-row.user {
  flex-direction: row-reverse;
  justify-content: flex-start; /* 改为 flex-start配合 row-reverse 实现右对齐*/
}

.message-avatar {
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
  border: 4rpx solid #fff;
  box-shadow: 0 4rpx 12rpx rgba(0,0,0,0.1), 0 0 0 1rpx rgba(15, 118, 110, 0.1);
  overflow: hidden;
  flex-shrink: 0;
  background: #fff;
  position: relative;
}

.message-avatar::after {
  content: '';
  position: absolute;
  top: -2rpx;
  left: -2rpx;
  right: -2rpx;
  bottom: -2rpx;
  border-radius: 50%;
  border: 1rpx solid rgba(15, 118, 110, 0.2);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.message-avatar:hover::after {
  opacity: 1;
}

.agent-avatar-wrap {
  margin-right: 0;
}

.avatar-img {
  width: 100%;
  height: 100%;
}

.message-content-box {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  max-width: 75%;
}

.user .message-content-box {
  align-items: flex-end;
  max-width: 80%;
  margin-right: 1.5%;
}

.chat-bubble {
  max-width: 100%;
  padding: 24rpx 30rpx;
  font-size: 28rpx;
  line-height: 1.6;
  border-radius: 32rpx;
  position: relative;
  word-wrap: break-word;
  word-break: break-word;
  white-space: pre-wrap;
  overflow-wrap: break-word;
  box-shadow: 0 8rpx 20rpx rgba(0,0,0,0.08), inset 0 1rpx 0 rgba(255,255,255,0.2);
  z-index: 5;
  border: 1rpx solid rgba(0,0,0,0.04);
  box-sizing: border-box;
}

.expert-bubble {
  background: rgba(255, 255, 255, 0.8) !important;
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  color: #134E4A;
  border: 1rpx solid #99F6E4 !important;
  border-radius: 32rpx 32rpx 32rpx 0 !important;
  box-shadow: 0 4rpx 16rpx rgba(15, 118, 110, 0.08) !important;
}

.user-bubble {
  background: linear-gradient(135deg, #0F766E 0%, #0EA5E9 50%, #0369A1 100%) !important;
  background-size: 200% 200% !important;
  animation: bubbleGradient 3s ease infinite !important;
  color: white !important;
  align-self: flex-end;
  border-radius: 32rpx 32rpx 0 32rpx !important;
  box-shadow: 0 8rpx 24rpx rgba(14, 165, 233, 0.3) !important;
  margin-right: 0;
  border: 1rpx solid rgba(255,255,255,0.2);
  box-sizing: border-box;
  max-width: 100%;
}

@keyframes bubbleGradient {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}

.ai-bubble {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  color: #134E4A;
  align-self: flex-start;
  border-radius: 32rpx 32rpx 32rpx 0;
  box-shadow: 0 4rpx 20rpx rgba(15, 118, 110, 0.06);
  border: 1rpx solid #99F6E4;
}

.welcome-msg {
  background: linear-gradient(135deg, rgba(15, 118, 110, 0.06) 0%, rgba(14, 165, 233, 0.04) 50%, rgba(3, 105, 161, 0.02) 100%);
  border: 1rpx solid rgba(14, 165, 233, 0.2);
  margin-top: 20rpx;
  box-shadow: 0 4rpx 16rpx rgba(14, 165, 233, 0.08), inset 0 1rpx 0 rgba(255,255,255,0.8);
  max-width: calc(100% - 80rpx);
  box-sizing: border-box;
  position: relative;
  overflow: hidden;
}

.welcome-msg::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(14, 165, 233, 0.1), transparent);
  animation: shimmer 3s infinite;
}

@keyframes shimmer {
  0% { left: -100%; }
  100% { left: 100%; }
}

.quick-suggestions {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
  margin-top: 28rpx;
}

.sugg-tag {
  background: linear-gradient(135deg, #F0FDFA 0%, #FFFFFF 100%);
  padding: 12rpx 24rpx;
  border-radius: 32rpx;
  font-size: 22rpx;
  color: #0F766E;
  border: 1rpx solid #E2E8F0;
  box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.06), inset 0 1rpx 0 rgba(255,255,255,0.8);
  transition: all 0.3s cubic-bezier(0.23, 1, 0.32, 1);
  cursor: pointer;
  position: relative;
  overflow: hidden;
}

.sugg-tag::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(14, 165, 233, 0.15), transparent);
  transition: left 0.5s ease;
}

.sugg-tag:hover::before {
  left: 100%;
}

.sugg-tag:active {
  transform: scale(0.95);
  background: linear-gradient(135deg, #0F766E 0%, #0EA5E9 50%, #0369A1 100%);
  color: white;
  border-color: transparent;
  box-shadow: 0 4rpx 12rpx rgba(14, 165, 233, 0.4), inset 0 1rpx 0 rgba(255,255,255,0.3);
}

/* 思考过程*/
.thought-process {
  margin-bottom: 16rpx;
  background: linear-gradient(135deg, rgba(15, 118, 110, 0.06) 0%, rgba(20, 184, 166, 0.03) 100%);
  border-radius: 20rpx;
  padding: 16rpx 24rpx;
  width: 90%;
  border: 1rpx solid #99F6E4;
  box-shadow: 0 2rpx 12rpx rgba(15, 118, 110, 0.08), inset 0 1rpx 0 rgba(255,255,255,0.5);
  animation: fadeInLeft 0.3s ease-out;
}

@keyframes fadeInLeft {
  from {
    opacity: 0;
    transform: translateX(-20rpx);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.thought-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  user-select: none;
}

.thought-label {
  font-size: 22rpx;
  color: #134E4A;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8rpx;
}

.thought-label::before {
  content: '';
  width: 8rpx;
  height: 8rpx;
  background: #14B8A6;
  border-radius: 50%;
  display: inline-block;
}

.thought-action {
  font-size: 20rpx;
  color: #0F766E;
  font-weight: 500;
  padding: 4rpx 12rpx;
  background: rgba(15, 118, 110, 0.1);
  border-radius: 16rpx;
  transition: all 0.2s ease;
}

.thought-action:active {
  background: rgba(15, 118, 110, 0.2);
  transform: scale(0.95);
}

.thought-detail {
  margin-top: 16rpx;
  border-top: 1px dashed #99F6E4;
  padding-top: 16rpx;
  animation: slideDown 0.3s ease-out;
}

@keyframes slideDown {
  from {
    opacity: 0;
    max-height: 0;
  }
  to {
    opacity: 1;
    max-height: 500rpx;
  }
}

.thought-step {
  display: flex;
  margin-top: 12rpx;
  align-items: flex-start;
}

.step-icon {
  font-size: 16rpx;
  margin-right: 12rpx;
  color: #14B8A6;
  margin-top: 4rpx;
  flex-shrink: 0;
}

.step-text {
  font-size: 22rpx;
  color: #134E4A;
  line-height: 1.6;
  flex: 1;
}

/* 输入框*/
.composition-area {
  padding: 30rpx 2.5% 40rpx;
  background: linear-gradient(to top, #FFFFFF 0%, #F0FDFA 100%);
  border-top: 1rpx solid #99F6E4;
  position: relative;
  box-sizing: border-box;
  width: 100%;
}

.composition-area::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2rpx;
  background: linear-gradient(90deg, transparent 0%, rgba(15, 118, 110, 0.2) 50%, transparent 100%);
}

.input-wrapper {
  background: linear-gradient(135deg, #F0FDFA 0%, #E6F7F5 100%);
  border-radius: 48rpx;
  padding: 12rpx 12rpx 12rpx 40rpx;
  display: flex;
  align-items: center;
  border: 2rpx solid transparent;
  transition: all 0.3s ease;
  box-shadow: inset 0 2rpx 8rpx rgba(0,0,0,0.03), 0 2rpx 8rpx rgba(0,0,0,0.04);
}

.input-wrapper:focus-within {
  border-color: #0EA5E9;
  background: #ffffff;
  box-shadow: 0 4rpx 16rpx rgba(14, 165, 233, 0.2), inset 0 2rpx 8rpx rgba(0,0,0,0.02);
  animation: inputFocusPulse 2s ease infinite;
}

@keyframes inputFocusPulse {
  0%, 100% { box-shadow: 0 4rpx 16rpx rgba(14, 165, 233, 0.2), inset 0 2rpx 8rpx rgba(0,0,0,0.02); }
  50% { box-shadow: 0 4rpx 20rpx rgba(14, 165, 233, 0.3), inset 0 2rpx 8rpx rgba(0,0,0,0.02); }
}

.neo-input {
  flex: 1;
  height: 80rpx;
  font-size: 28rpx;
  color: #134E4A;
  background: transparent;
}

.voice-btn {
  min-width: 120rpx;
  height: 80rpx;
  margin-right: 12rpx;
  border-radius: 40rpx;
  background: #E6F7F5;
  border: 1rpx solid #99F6E4;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.voice-btn.active {
  background: linear-gradient(135deg, #0F766E 0%, #14B8A6 100%);
  box-shadow: 0 6rpx 20rpx rgba(15, 118, 110, 0.25);
}

.voice-btn-text {
  font-size: 22rpx;
  color: #0F766E;
  font-weight: 700;
}

.voice-btn.active .voice-btn-text {
  color: #fff;
}

.send-btn {
  width: 108rpx;
  height: 80rpx;
  background: linear-gradient(135deg, #D1D5DB 0%, #9CA3AF 100%);
  border-radius: 40rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s cubic-bezier(0.23, 1, 0.32, 1);
  box-shadow: 0 4rpx 12rpx rgba(0,0,0,0.1);
}

.send-btn.active {
  background: linear-gradient(135deg, #0F766E 0%, #0EA5E9 50%, #0369A1 100%);
  background-size: 200% 200%;
  animation: sendBtnGradient 3s ease infinite;
  box-shadow: 0 6rpx 20rpx rgba(14, 165, 233, 0.4);
  transform: scale(1.02);
}

@keyframes sendBtnGradient {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}

.send-btn:active {
  transform: scale(0.95);
}

.send-text {
  color: #fff;
  font-size: 24rpx;
  font-weight: 700;
  letter-spacing: 1rpx;
}

/* 地图工具 */
.map-controls {
  position: absolute;
  right: 30rpx;
  top: calc(200rpx + constant(safe-area-inset-top));
  top: calc(200rpx + env(safe-area-inset-top));
  display: flex;
  flex-direction: column;
  gap: 24rpx;
  pointer-events: auto;
}

.ctrl-btn {
  width: 88rpx;
  height: 88rpx;
  background: #ffffff;
  border-radius: 24rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 44rpx;
  color: #134E4A;
  box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.1);
  border: none;
  transition: all 0.3s cubic-bezier(0.23, 1, 0.32, 1);
  cursor: pointer;
  position: relative;
  overflow: hidden;
}

.ctrl-btn::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  background: radial-gradient(circle, rgba(15, 118, 110, 0.15) 0%, transparent 70%);
  border-radius: 50%;
  transform: translate(-50%, -50%);
  transition: width 0.4s ease, height 0.4s ease;
}

.ctrl-btn:active::before {
  width: 200%;
  height: 200%;
}

.ctrl-btn:active {
  transform: scale(0.92);
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.15);
  background: rgba(255, 255, 255, 1);
}

.ctrl-btn.zoom-in,
.ctrl-btn.zoom-out {
  font-weight: 700;
  color: #134E4A;
  font-size: 48rpx;
  letter-spacing: -2rpx;
}

.ctrl-btn.relocate {
  background: #ffffff;
}

.ctrl-btn.relocate:active {
  background: #F0FDFA;
}

.ctrl-btn.relocate:active image {
  filter: brightness(0) invert(1);
}

.ctrl-btn.choose-loc {
  background: #ffffff;
}

.ctrl-btn.choose-loc:active {
  background: #F0FDFA;
}

.ctrl-btn.choose-loc:active image {
  filter: brightness(0) invert(1);
}

.ctrl-btn.preference-btn {
  background: #ffffff;
}

.ctrl-btn.preference-btn:active {
  background: #F0FDFA;
}

.ctrl-btn.preference-btn:active image {
  filter: brightness(0) invert(1);
}

/* 状态遮罩*/
.map-status-mask {
  position: absolute;
  top: 0; left: 0; width: 100%; height: 100%;
  z-index: 1000; /* 提升层级，确保在加载时覆盖一切*/
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
}

.spinner {
  width: 70rpx;
  height: 70rpx;
  border: 5rpx solid #E2E8F0;
  border-top-color: #0F766E;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.status-tip {
  margin-top: 24rpx;
  font-size: 28rpx;
  color: #134E4A;
  font-weight: 500;
}

.status-subtip {
  margin-top: 12rpx;
  font-size: 24rpx;
  color: #64748B;
}

@keyframes spin { to { transform: rotate(360deg); } }

.pulse-loading {
  display: flex;
  gap: 8rpx;
  padding: 10rpx 0;
}

.pulse-loading .dot {
  width: 12rpx;
  height: 12rpx;
  background: #0F766E;
  border-radius: 50%;
  opacity: 0.6;
  animation: dotPulse 1.4s infinite;
}

.pulse-loading .dot:nth-child(2) { animation-delay: 0.2s; }
.pulse-loading .dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes dotPulse { 0%, 100% { transform: scale(0.8); opacity: 0.5; } 50% { transform: scale(1.2); opacity: 1; } }

/* ===== 响应式设置===== */
/* 小屏幕设置*/
@media screen and (max-width: 375px) {
  .top-nav-blur {
    padding: calc(75rpx + constant(safe-area-inset-top)) 20rpx 15rpx;
    padding: calc(75rpx + env(safe-area-inset-top)) 20rpx 15rpx;
  }

  .map-controls {
    right: 20rpx;
    top: calc(180rpx + constant(safe-area-inset-top));
    top: calc(180rpx + env(safe-area-inset-top));
  }

  .ctrl-btn {
    width: 72rpx;
    height: 72rpx;
    font-size: 36rpx;
  }

  .agent-card {
    left: 20rpx;
    right: 20rpx;
  }

  .agent-img {
    width: 72rpx;
    height: 72rpx;
  }

  .agent-title {
    font-size: 28rpx;
  }

  .chat-bubble {
    font-size: 26rpx;
    padding: 24rpx 32rpx;
  }

  /* 消息布局响应式优化*/
  .message-row {
    margin-bottom: 20rpx;
    gap: 16rpx;
    max-width: 100%;
    overflow-x: hidden;
    overflow-y: visible;
  }
}

/* 中等屏幕设备 */
@media screen and (min-width: 376px) and (max-width: 414px) {
  .top-nav-blur {
    padding: calc(78rpx + constant(safe-area-inset-top)) 25rpx 18rpx;
    padding: calc(78rpx + env(safe-area-inset-top)) 25rpx 18rpx;
  }

  .map-controls {
    right: 25rpx;
    top: calc(190rpx + constant(safe-area-inset-top));
    top: calc(190rpx + env(safe-area-inset-top));
  }

  .agent-card {
    left: 25rpx;
    right: 25rpx;
  }

  /* 消息布局响应式优化*/
  .message-row {
    margin-bottom: 24rpx;
    gap: 18rpx;
    max-width: 100%;
    overflow-x: hidden;
    overflow-y: visible;
  }
}

/* 大屏幕设置*/
@media screen and (min-width: 415px) {
  .top-nav-blur {
    padding: calc(80rpx + constant(safe-area-inset-top)) 30rpx 20rpx;
    padding: calc(80rpx + env(safe-area-inset-top)) 30rpx 20rpx;
  }

  .map-controls {
    right: 30rpx;
    top: calc(200rpx + constant(safe-area-inset-top));
    top: calc(200rpx + env(safe-area-inset-top));
  }

  .agent-card {
    left: 30rpx;
    right: 30rpx;
  }

  /* 消息布局响应式优化*/
  .message-row {
    margin-bottom: 28rpx;
    gap: 20rpx;
    max-width: 100%;
    overflow-x: hidden;
    overflow-y: visible;
  }
}

/* 横屏适配 */
@media screen and (orientation: landscape) {
  .top-nav-blur {
    padding: calc(60rpx + constant(safe-area-inset-top)) 25rpx 15rpx;
    padding: calc(60rpx + env(safe-area-inset-top)) 25rpx 15rpx;
  }

  .map-controls {
    right: 25rpx;
    top: calc(160rpx + constant(safe-area-inset-top));
    top: calc(160rpx + env(safe-area-inset-top));
  }

  .ctrl-btn {
    width: 64rpx;
    height: 64rpx;
    font-size: 32rpx;
  }

  .agent-card {
    left: 25rpx;
    right: 25rpx;
    bottom: calc(140rpx + env(safe-area-inset-bottom));
  }

  .card-body {
    height: 50vh;
    max-height: 700rpx;
    overflow: hidden;
  }

  /* 消息布局横屏优化 */
  .chat-bubble {
    font-size: 26rpx;
    padding: 20rpx 28rpx;
  }

  .message-row {
    margin-bottom: 20rpx;
    gap: 16rpx;
    max-width: 100%;
    overflow-x: hidden;
    overflow-y: visible;
  }
}

/* ========== 左侧边栏 + 主内容布局 ========== */
.page-root { width: 100%; height: 100vh; display: flex; flex-direction: column; background: #F0FDFA; overflow: hidden; }

/* 折叠态图标栏 */
.mini-bar { position: absolute; top: 0; left: 0; width: 80rpx; background: #fff; border-right: 1rpx solid #99F6E4; border-bottom: 1rpx solid #99F6E4; display: flex; flex-direction: column; align-items: center; padding-top: 16rpx; gap: 8rpx; z-index: 50; box-shadow: 2rpx 0 12rpx rgba(15,118,110,0.05); border-radius: 0 0 16rpx 0; }
.mb-toggle { width: 56rpx; height: 56rpx; border-radius: 12rpx; display: flex; align-items: center; justify-content: center; background: #F0FDFA; margin-bottom: 8rpx; }
.mb-toggle-icon { font-size: 28rpx; color: #0F766E; }
.mb-item { width: 56rpx; height: 56rpx; border-radius: 12rpx; display: flex; align-items: center; justify-content: center; }
.mb-item.active { background: rgba(37,99,235,0.1); }
.mb-divider { width: 32rpx; height: 2rpx; background: #E2E8F0; margin: 8rpx auto; }
.mb-icon { font-size: 28rpx; }

/* 顶部导航栏 */
.kb-navbar {
  position: relative; z-index: 100; width: 100%;
  background: #FFFFFF;
  box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.06);
  border-bottom: 1rpx solid #E2E8F0;
}
.kb-navbar-inner {
  display: flex; align-items: center; justify-content: space-between;
  height: 88rpx; padding: 0 24rpx;
}
.kb-nav-left { width: 64rpx; height: 64rpx; display: flex; align-items: center; justify-content: center; }
.kb-nav-menu { font-size: 36rpx; color: #334155; }
.kb-nav-title { font-size: 34rpx; font-weight: 700; color: #0F172A; letter-spacing: 2rpx; }
.kb-nav-right { width: 64rpx; height: 64rpx; display: flex; align-items: center; justify-content: center; }
.kb-nav-add { font-size: 40rpx; color: #334155; font-weight: 300; }

/* 侧边栏遮罩 */
.sidebar-mask {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0,0,0,0.3); z-index: 90;
}

/* 展开态侧边栏 */
.sidebar { position: absolute; top: 0; left: 0; width: 340rpx; background: #FFFFFF; border-right: 1rpx solid #99F6E4; border-bottom: 1rpx solid #99F6E4; display: flex; flex-direction: column; z-index: 95; box-shadow: 2rpx 0 12rpx rgba(15,118,110,0.05); border-radius: 0 0 16rpx 0; }

.side-header { padding: 24rpx 20rpx 16rpx; display: flex; align-items: center; gap: 10rpx; }
.side-logo { font-size: 32rpx; }
.side-title { font-size: 28rpx; font-weight: 700; color: #134E4A; letter-spacing: 2rpx; flex: 1; }
.side-close { width: 44rpx; height: 44rpx; border-radius: 10rpx; display: flex; align-items: center; justify-content: center; background: #F0FDFA; }
.side-close-icon { font-size: 22rpx; color: #94A3B8; }

.side-tabs { padding: 0 16rpx; display: flex; flex-direction: column; gap: 6rpx; }
.side-tab { display: flex; align-items: center; gap: 12rpx; padding: 14rpx 16rpx; border-radius: 12rpx; transition: all 0.2s; }
.side-tab.active {
  background: linear-gradient(135deg, rgba(15,118,110,0.08) 0%, rgba(14,165,233,0.04) 100%);
  border-left: 4rpx solid #0EA5E9;
  padding-left: 12rpx;
}
.side-tab-icon { font-size: 26rpx; }
.side-tab-label { font-size: 24rpx; color: #64748B; transition: all 0.2s; }
.side-tab.active .side-tab-label { color: #0F766E; font-weight: 600; }

.side-search { margin: 12rpx 16rpx; display: flex; align-items: center; gap: 8rpx; background: #F0FDFA; border-radius: 12rpx; padding: 10rpx 14rpx; border: 1rpx solid #99F6E4; }
.side-search-icon { font-size: 22rpx; flex-shrink: 0; color: #0F766E; }
.side-search-input { flex: 1; font-size: 22rpx; color: #134E4A; }

.side-divider { height: 1rpx; background: #99F6E4; margin: 8rpx 16rpx; }

.side-list { flex: 1; padding: 8rpx 10rpx; }
.side-node { display: flex; align-items: center; gap: 12rpx; padding: 14rpx 12rpx; border-radius: 12rpx; margin-bottom: 4rpx; transition: all 0.15s; }
.side-node.active { background: rgba(15,118,110,0.06); }
.sn-dot { width: 10rpx; height: 10rpx; border-radius: 50%; flex-shrink: 0; }
.sn-info { flex: 1; overflow: hidden; }
.sn-label { font-size: 24rpx; color: #134E4A; font-weight: 500; display: block; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.sn-cat { font-size: 18rpx; color: #94A3B8; margin-top: 2rpx; display: block; }
.side-empty { padding: 40rpx 0; text-align: center; }
.side-empty-text { font-size: 22rpx; color: #94A3B8; }

/* 知识分类板块 */
.side-section {
  margin: 8rpx 16rpx 12rpx;
  padding: 0;
}
.side-section-title {
  font-size: 20rpx;
  color: #94A3B8;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1rpx;
  display: block;
  margin-bottom: 12rpx;
  padding: 0 4rpx;
}
.cat-list {
  display: flex;
  flex-direction: column;
  gap: 4rpx;
}
.cat-item {
  display: flex;
  align-items: center;
  gap: 12rpx;
  padding: 12rpx 12rpx;
  border-radius: 10rpx;
  transition: all 0.2s;
  cursor: pointer;
}
.cat-item:active {
  background: #F1F5F9;
}
.cat-item.active {
  background: #EFF6FF;
}
.cat-icon-sm {
  width: 40rpx;
  height: 40rpx;
  border-radius: 10rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.cat-emoji { font-size: 22rpx; }
.cat-name {
  font-size: 24rpx;
  color: #475569;
  font-weight: 500;
  flex: 1;
}
.cat-item.active .cat-name {
  color: #2563EB;
  font-weight: 700;
}
.cat-count {
  font-size: 20rpx;
  color: #94A3B8;
  background: #F1F5F9;
  padding: 2rpx 10rpx;
  border-radius: 10rpx;
  font-weight: 600;
}

.side-add {
  margin: 12rpx 16rpx 16rpx;
  padding: 14rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8rpx;
  background: linear-gradient(135deg, #F0FDFA, #E6F7F5);
  border-radius: 12rpx;
  border: 1rpx dashed #0EA5E9;
  transition: all 0.2s ease;
}

.side-add:active {
  background: linear-gradient(135deg, #0F766E, #0EA5E9);
  border-style: solid;
  transform: scale(0.98);
}

.side-add:active .side-add-icon,
.side-add:active .side-add-text {
  color: #fff;
}

.side-add-icon {
  font-size: 26rpx;
  color: #0F766E;
  font-weight: 600;
  transition: color 0.2s ease;
}

.side-add-text {
  font-size: 22rpx;
  color: #0F766E;
  font-weight: 500;
  transition: color 0.2s ease;
}

/* 主内容区 */
.main-area { flex: 1; width: 100%; display: flex; flex-direction: column; overflow: hidden; min-height: 0; }
.file-explorer-area { flex: 1; width: 100%; display: flex; flex-direction: column; overflow: hidden; }

/* 节点详情浮窗 */
.node-detail-float {
  position: absolute;
  bottom: 20rpx;
  left: 20rpx;
  right: 20rpx;
  background: #fff;
  border-radius: 16rpx;
  padding: 20rpx;
  box-shadow: 0 8rpx 32rpx rgba(0,0,0,0.12);
  z-index: 10;
  border: 1rpx solid #E2E8F0;
  animation: slideUpFloat 0.3s cubic-bezier(0.23, 1, 0.32, 1);
}

@keyframes slideUpFloat {
  from { transform: translateY(20rpx); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.ndf-head { display: flex; align-items: center; gap: 12rpx; margin-bottom: 8rpx; }
.ndf-title { font-size: 30rpx; font-weight: 700; color: #0F766E; }
.ndf-cat {
  font-size: 20rpx;
  color: #0EA5E9;
  background: linear-gradient(135deg, rgba(14,165,233,0.1), rgba(3,105,161,0.05));
  padding: 4rpx 12rpx;
  border-radius: 8rpx;
  border: 1rpx solid rgba(14,165,233,0.2);
}
.ndf-close { font-size: 32rpx; color: #94A3B8; margin-left: auto; padding: 4rpx 8rpx; }
.ndf-desc { font-size: 24rpx; color: #64748B; line-height: 1.5; margin-bottom: 8rpx; }
.ndf-tags { display: flex; flex-wrap: wrap; gap: 8rpx; margin-bottom: 8rpx; }
.ndf-tag { font-size: 20rpx; color: #0F766E; background: rgba(15,118,110,0.08); padding: 4rpx 12rpx; border-radius: 8rpx; }
.ndf-conns { display: flex; flex-wrap: wrap; align-items: center; gap: 8rpx; }
.ndf-conn-label { font-size: 22rpx; color: #94A3B8; }
.ndf-conn-item { font-size: 22rpx; color: #0F766E; background: rgba(15,118,110,0.08); padding: 4rpx 12rpx; border-radius: 8rpx; }

/* 缩放控制 */
.zoom-controls {
  position: absolute;
  bottom: 80rpx;
  right: 16rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4rpx;
  background: #fff;
  border-radius: 16rpx;
  padding: 8rpx;
  box-shadow: 0 4rpx 16rpx rgba(0,0,0,0.1);
  z-index: 10;
  border: 1rpx solid #E2E8F0;
}

.zoom-btn {
  width: 56rpx;
  height: 56rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #F0FDFA, #E6F7F5);
  border-radius: 10rpx;
  transition: all 0.2s ease;
}

.zoom-btn:active {
  background: linear-gradient(135deg, #0F766E, #14B8A6);
  transform: scale(0.95);
}

.zoom-btn:active .zoom-text {
  color: #fff;
}

.zoom-text {
  font-size: 32rpx;
  color: #0F766E;
  font-weight: 700;
  line-height: 1;
  transition: color 0.2s ease;
}

.zoom-label {
  font-size: 18rpx;
  color: #64748B;
  padding: 2rpx 0;
  font-weight: 500;
}

/* 思维导图控制 */
.mind-controls {
  position: absolute;
  bottom: 20rpx;
  left: 20rpx;
  right: 20rpx;
  display: flex;
  gap: 12rpx;
}

.mc-btn {
  flex: 1;
  padding: 12rpx;
  text-align: center;
  background: linear-gradient(135deg, #fff, #F0FDFA);
  border-radius: 12rpx;
  box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.08);
  border: 1rpx solid #E2E8F0;
  transition: all 0.2s ease;
}

.mc-btn:active {
  background: linear-gradient(135deg, #0F766E, #14B8A6);
  box-shadow: 0 4rpx 16rpx rgba(14,165,233,0.3);
  transform: translateY(-2rpx);
}

.mc-btn:active .mc-text {
  color: #fff;
}

.mc-text {
  font-size: 24rpx;
  color: #0F766E;
  font-weight: 500;
  transition: color 0.2s ease;
}

/* 主区大卡片 */
.card-main-area { flex: 1; padding: 16rpx; }
.knowledge-workbench {
  flex: 1;
  padding: 20rpx 18rpx 180rpx;
  box-sizing: border-box;
  background: #F8FAFC;
}
.kw-summary-bar { display: flex; gap: 12rpx; margin-bottom: 18rpx; }
.kw-summary-item { flex: 1; padding: 18rpx 10rpx; border-radius: 14rpx; background: #FFFFFF; border: 1rpx solid #E2E8F0; text-align: center; }
.kw-summary-num { display: block; font-size: 32rpx; color: #0F766E; font-weight: 800; }
.kw-summary-num.warn { color: #D97706; }
.kw-summary-label { display: block; font-size: 20rpx; color: #64748B; margin-top: 4rpx; }
.kw-toggle-arrow { font-size: 28rpx; color: #94A3B8; padding: 4rpx 8rpx; }
.kw-submit-entry { padding: 20rpx; text-align: center; background: #F8FAFC; border-radius: 12rpx; border: 2rpx dashed #CBD5E1; }
.kw-submit-entry-text { font-size: 26rpx; color: #0F766E; font-weight: 600; }
.kw-empty-hint { padding: 40rpx 0; text-align: center; }
.kw-empty-text { font-size: 24rpx; color: #94A3B8; }
.kw-section { padding: 22rpx; margin-bottom: 18rpx; border-radius: 18rpx; background: #FFFFFF; border: 1rpx solid #E2E8F0; box-shadow: 0 4rpx 16rpx rgba(15, 23, 42, 0.04); }
.kw-section.last { margin-bottom: 40rpx; }
.kw-section-head { display: flex; align-items: flex-start; justify-content: space-between; gap: 18rpx; margin-bottom: 18rpx; }
.kw-section-title { display: block; font-size: 30rpx; font-weight: 800; color: #0F172A; }
.kw-section-sub { display: block; font-size: 22rpx; color: #64748B; margin-top: 6rpx; line-height: 1.45; }
.kw-section-count { flex-shrink: 0; font-size: 22rpx; color: #D97706; background: #FFFBEB; border: 1rpx solid #FDE68A; padding: 8rpx 12rpx; border-radius: 10rpx; }
.kw-section-tag { flex-shrink: 0; padding: 8rpx 12rpx; border-radius: 10rpx; background: #ECFDF5; border: 1rpx solid #A7F3D0; }
.kw-section-tag text { font-size: 22rpx; color: #047857; font-weight: 700; }
.kw-section-tag.warn { background: #FFF7ED; border-color: #FED7AA; }
.kw-section-tag.warn text { color: #C2410C; }
.kw-form { display: flex; flex-direction: column; gap: 14rpx; }
.kw-row { display: flex; gap: 12rpx; }
.kw-input,
.kw-picker-inner,
.kw-textarea { width: 100%; box-sizing: border-box; background: #F8FAFC; border: 1rpx solid #E2E8F0; border-radius: 12rpx; color: #0F172A; font-size: 25rpx; }
.kw-input { height: 76rpx; padding: 0 18rpx; }
.kw-picker { width: 180rpx; flex-shrink: 0; }
.kw-picker-inner { height: 76rpx; display: flex; align-items: center; justify-content: center; color: #0F766E; font-weight: 700; }
.kw-textarea { min-height: 160rpx; padding: 18rpx; line-height: 1.6; }
.kw-textarea.correction { margin-top: 14rpx; }
.kw-upload-line { display: flex; gap: 12rpx; align-items: center; }
.kw-upload-box { flex: 1; min-width: 0; height: 76rpx; border-radius: 12rpx; border: 1rpx dashed #94A3B8; background: #F8FAFC; display: flex; align-items: center; justify-content: center; gap: 10rpx; padding: 0 14rpx; }
.kw-upload-icon { font-size: 30rpx; color: #0F766E; font-weight: 800; }
.kw-upload-text { font-size: 23rpx; color: #475569; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.kw-submit { width: 160rpx; height: 76rpx; border-radius: 12rpx; background: linear-gradient(135deg, #0F766E, #0284C7); display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.kw-submit.slim { width: 140rpx; height: 66rpx; }
.kw-submit text { font-size: 25rpx; color: #FFFFFF; font-weight: 800; }
.review-list { display: flex; flex-direction: column; gap: 14rpx; }
.review-card { padding: 18rpx; border-radius: 14rpx; background: #F8FAFC; border: 1rpx solid #E2E8F0; }
.review-title-row { display: flex; align-items: center; gap: 12rpx; margin-bottom: 8rpx; }
.review-title { flex: 1; min-width: 0; font-size: 27rpx; font-weight: 800; color: #0F172A; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.review-badge { flex-shrink: 0; padding: 4rpx 10rpx; border-radius: 8rpx; font-size: 20rpx; font-weight: 700; color: #D97706; background: #FFFBEB; }
.review-badge.approved { color: #047857; background: #ECFDF5; }
.review-badge.rejected { color: #BE123C; background: #FFF1F2; }
.review-desc { display: block; font-size: 23rpx; line-height: 1.55; color: #475569; }
.review-meta { display: flex; flex-wrap: wrap; gap: 14rpx; margin-top: 10rpx; }
.review-meta text { font-size: 20rpx; color: #94A3B8; }
.review-tags { display: flex; flex-wrap: wrap; gap: 8rpx; margin-top: 12rpx; }
.review-tag { font-size: 20rpx; color: #0F766E; background: rgba(15,118,110,0.08); padding: 4rpx 10rpx; border-radius: 8rpx; }
.review-actions { display: flex; gap: 12rpx; margin-top: 16rpx; }
.review-btn { flex: 1; height: 64rpx; border-radius: 10rpx; display: flex; align-items: center; justify-content: center; }
.review-btn text { font-size: 24rpx; font-weight: 700; }
.review-btn.ghost { background: #FFFFFF; border: 1rpx solid #CBD5E1; }
.review-btn.ghost text { color: #475569; }
.review-btn.primary { background: #0F766E; }
.review-btn.primary text { color: #FFFFFF; }
.annotation-card { padding: 18rpx; border-radius: 14rpx; background: #F8FAFC; border: 1rpx solid #E2E8F0; }
.annotation-label { display: block; font-size: 21rpx; color: #64748B; margin-bottom: 8rpx; }
.annotation-text { display: block; font-size: 25rpx; line-height: 1.65; color: #0F172A; padding: 16rpx; border-radius: 12rpx; background: #FFFFFF; border-left: 6rpx solid #F59E0B; }
.annotation-tools { display: flex; flex-wrap: wrap; gap: 10rpx; margin-top: 16rpx; }
.annotation-chip { padding: 8rpx 14rpx; border-radius: 18rpx; background: #FFFFFF; border: 1rpx solid #CBD5E1; }
.annotation-chip text { font-size: 22rpx; color: #64748B; }
.annotation-chip.active { background: #FFF7ED; border-color: #FDBA74; }
.annotation-chip.active text { color: #C2410C; font-weight: 700; }
.annotation-footer { display: flex; align-items: center; gap: 12rpx; margin-top: 14rpx; }
.annotation-hint { flex: 1; min-width: 0; font-size: 22rpx; color: #64748B; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.timeline { display: flex; flex-direction: column; gap: 16rpx; }
.timeline-item { display: flex; gap: 14rpx; }
.timeline-dot { width: 18rpx; height: 18rpx; border-radius: 50%; margin-top: 9rpx; background: #94A3B8; flex-shrink: 0; }
.timeline-dot.approved,
.timeline-dot.graph { background: #10B981; }
.timeline-dot.review { background: #F59E0B; }
.timeline-dot.corrected { background: #DB2777; }
.timeline-dot.rejected { background: #EF4444; }
.timeline-body { flex: 1; padding-bottom: 16rpx; border-bottom: 1rpx solid #F1F5F9; }
.timeline-title { display: block; font-size: 25rpx; font-weight: 800; color: #0F172A; }
.timeline-desc { display: block; font-size: 22rpx; color: #64748B; line-height: 1.5; margin-top: 6rpx; }
.timeline-time { display: block; font-size: 20rpx; color: #94A3B8; margin-top: 6rpx; }
.kb-card-main {
  display: flex;
  gap: 16rpx;
  background: #fff;
  border-radius: 16rpx;
  padding: 24rpx;
  margin-bottom: 12rpx;
  box-shadow: 0 1rpx 8rpx rgba(0,0,0,0.04);
  border: 1rpx solid #E2E8F0;
  transition: all 0.3s cubic-bezier(0.23, 1, 0.32, 1);
  position: relative;
  overflow: hidden;
}

.kb-card-main::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4rpx;
  background: linear-gradient(90deg, #0F766E, #14B8A6, #0EA5E9, #0369A1);
  background-size: 200% 100%;
  opacity: 0;
  transition: opacity 0.3s ease;
  animation: gradientShift 3s ease infinite;
}

.kb-card-main:hover::before,
.kb-card-main:active::before {
  opacity: 1;
}

.kb-card-main:active {
  background: #F0FDFA;
  box-shadow: 0 2rpx 12rpx rgba(14,165,233,0.12);
  transform: translateY(-2rpx);
}
.kbc-icon-wrap { width: 72rpx; height: 72rpx; border-radius: 16rpx; background: rgba(15,118,110,0.08); display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.kbc-icon { font-size: 36rpx; }
.kbc-body { flex: 1; }
.kbc-head { display: flex; align-items: center; gap: 10rpx; margin-bottom: 6rpx; }
.kbc-title { font-size: 28rpx; font-weight: 600; color: #134E4A; }
.kbc-cat { font-size: 20rpx; color: #0F766E; background: rgba(15,118,110,0.08); padding: 2rpx 10rpx; border-radius: 6rpx; }
.kbc-desc { font-size: 24rpx; color: #64748B; line-height: 1.5; }
.kbc-tags { display: flex; flex-wrap: wrap; gap: 6rpx; margin-top: 8rpx; }
.kbc-tag { font-size: 20rpx; color: #0F766E; background: rgba(15,118,110,0.06); padding: 2rpx 10rpx; border-radius: 6rpx; }

/* 弹窗 */
.modal-mask { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; z-index: 999; }
.modal-box {
  width: 85%;
  background: #fff;
  border-radius: 20rpx;
  padding: 32rpx;
  border: 1rpx solid #E2E8F0;
  box-shadow: 0 16rpx 48rpx rgba(0,0,0,0.15);
  animation: modalAppear 0.3s cubic-bezier(0.23, 1, 0.32, 1);
}

@keyframes modalAppear {
  from { transform: scale(0.9) translateY(20rpx); opacity: 0; }
  to { transform: scale(1) translateY(0); opacity: 1; }
}

.modal-title {
  font-size: 32rpx;
  font-weight: 700;
  color: #0F766E;
  text-align: center;
  margin-bottom: 24rpx;
  background: linear-gradient(135deg, #0F766E, #0EA5E9);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.modal-input {
  background: #F0FDFA;
  border-radius: 12rpx;
  padding: 14rpx 20rpx;
  font-size: 26rpx;
  margin-bottom: 16rpx;
  border: 1rpx solid #E2E8F0;
  transition: all 0.2s ease;
}

.modal-input:focus {
  border-color: #0EA5E9;
  box-shadow: 0 0 0 3rpx rgba(14,165,233,0.1);
}

.modal-textarea {
  background: #F0FDFA;
  border-radius: 12rpx;
  padding: 14rpx 20rpx;
  font-size: 26rpx;
  margin-bottom: 16rpx;
  height: 120rpx;
  width: 100%;
  border: 1rpx solid #E2E8F0;
  box-sizing: border-box;
  transition: all 0.2s ease;
}

.modal-textarea:focus {
  border-color: #0EA5E9;
  box-shadow: 0 0 0 3rpx rgba(14,165,233,0.1);
}

.modal-btns { display: flex; gap: 16rpx; margin-top: 8rpx; }

.mbtn {
  flex: 1;
  padding: 14rpx;
  text-align: center;
  border-radius: 12rpx;
  transition: all 0.2s ease;
}

.mbtn.cancel {
  background: #F1F5F9;
}

.mbtn.cancel:active {
  background: #E2E8F0;
}

.mbtn.confirm {
  background: linear-gradient(135deg, #0F766E, #0EA5E9, #0369A1);
  background-size: 200% 200%;
  animation: btnGradient 3s ease infinite;
}

@keyframes btnGradient {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}

.mbtn.confirm:active {
  transform: scale(0.98);
  box-shadow: 0 4rpx 12rpx rgba(14,165,233,0.3);
}

.mbtn-text { font-size: 26rpx; }
.mbtn.cancel .mbtn-text { color: #64748B; }
.mbtn.confirm .mbtn-text { color: #fff; font-weight: 600; }

/* 浮动 Agent 样式已移除，使用原 agent-card 样式 */

/* ── 知识网络增强样式 ── */
.canvas-area { flex: 1; width: 100%; position: relative; background: #F8FAFF; }
.full-canvas { width: 100%; height: 100%; }

/* 图谱搜索/筛选工具栏 */
.graph-toolbar {
  flex-shrink: 0; background: #FFFFFF; padding: 12rpx 16rpx 8rpx;
  border-bottom: 1rpx solid #F1F5F9;
}
.graph-search-wrap {
  display: flex; align-items: center; gap: 10rpx;
  background: #F8FAFC; border-radius: 24rpx;
  padding: 8rpx 20rpx; margin-bottom: 10rpx;
  border: 1rpx solid #E2E8F0;
}
.graph-search-icon { font-size: 24rpx; }
.graph-search-input {
  flex: 1; height: 48rpx; font-size: 24rpx;
  color: #1E293B; background: transparent;
}
.graph-search-clear {
  font-size: 28rpx; color: #94A3B8;
  padding: 4rpx 8rpx; cursor: pointer;
}
.graph-filter-scroll { white-space: nowrap; }
.graph-filter-chips { display: inline-flex; gap: 10rpx; }
.filter-chip {
  display: inline-flex; align-items: center; gap: 6rpx;
  padding: 6rpx 16rpx; border-radius: 20rpx;
  background: #F8FAFC; border: 1rpx solid #E2E8F0;
  cursor: pointer; transition: all 0.2s ease;
}
.filter-chip:active { background: #F1F5F9; }
.filter-chip.active {
  background: rgba(14,165,233,0.08); border-color: rgba(14,165,233,0.3);
}
.filter-chip-dot { width: 12rpx; height: 12rpx; border-radius: 3rpx; flex-shrink: 0; }
.filter-chip-text { font-size: 20rpx; color: #64748B; white-space: nowrap; }
.filter-chip.active .filter-chip-text { color: #0EA5E9; font-weight: 600; }

/* 分类图例 */
.graph-legend {
  position: absolute; top: 16rpx; left: 16rpx;
  background: #FFFFFF; border-radius: 12rpx; padding: 14rpx 16rpx; z-index: 10;
  border: 1rpx solid #E2E8F0; min-width: 180rpx;
  box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.06);
}
.legend-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 10rpx; }
.legend-title { font-size: 20rpx; color: #94A3B8; font-weight: 600; }
.legend-close { font-size: 26rpx; color: #CBD5E1; padding: 4rpx 8rpx; cursor: pointer; }
.legend-item {
  display: flex; align-items: center; gap: 10rpx; margin-bottom: 4rpx;
  padding: 6rpx 10rpx; border-radius: 8rpx; cursor: pointer; transition: all 0.2s ease;
}
.legend-item:active { background: #F8FAFC; }
.legend-item.active { background: rgba(14,165,233,0.08); }
.legend-item.reset { margin-top: 8rpx; border-top: 1rpx solid #F1F5F9; padding-top: 10rpx; }
.legend-color-bar { width: 18rpx; height: 18rpx; border-radius: 4rpx; flex-shrink: 0; }
.legend-label { font-size: 20rpx; color: #475569; }
.legend-item.active .legend-label { color: #0EA5E9; font-weight: 600; }
.legend-toggle {
  position: absolute; top: 16rpx; left: 16rpx;
  background: #FFFFFF; border-radius: 12rpx; padding: 12rpx 16rpx; z-index: 10;
  border: 1rpx solid #E2E8F0; cursor: pointer;
  box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.06);
}
.legend-toggle-icon { font-size: 28rpx; color: #64748B; }

/* 节点详情浮窗 */
.node-detail-float {
  position: absolute; bottom: 20rpx; left: 20rpx; right: 20rpx;
  background: #FFFFFF; border-radius: 16rpx; padding: 24rpx;
  box-shadow: 0 4rpx 24rpx rgba(0,0,0,0.08); z-index: 10;
  border: 1rpx solid #E2E8F0;
  animation: slideUpFloat 0.25s ease;
}
@keyframes slideUpFloat { from { transform: translateY(16rpx); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
.ndf-head { display: flex; align-items: center; gap: 14rpx; margin-bottom: 10rpx; }
.ndf-icon-wrap { width: 48rpx; height: 48rpx; border-radius: 12rpx; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.ndf-icon { font-size: 24rpx; }
.ndf-title-area { flex: 1; min-width: 0; }
.ndf-title { font-size: 28rpx; font-weight: 600; color: #1E293B; display: block; }
.ndf-meta-row { display: flex; align-items: center; gap: 10rpx; margin-top: 4rpx; }
.ndf-cat { font-size: 20rpx; color: #64748B; background: #F1F5F9; padding: 2rpx 10rpx; border-radius: 6rpx; }
.ndf-status { font-size: 18rpx; padding: 2rpx 8rpx; border-radius: 6rpx; font-weight: 500; }
.ndf-status.approved { color: #10B981; background: rgba(16,185,129,0.08); }
.ndf-status.pending { color: #D97706; background: rgba(217,119,6,0.08); }
.ndf-status.corrected { color: #EF4444; background: rgba(239,68,68,0.08); }
.ndf-close { font-size: 32rpx; color: #CBD5E1; margin-left: auto; padding: 4rpx 8rpx; }
.ndf-desc { font-size: 24rpx; color: #64748B; line-height: 1.6; margin-bottom: 10rpx; }
.ndf-tags { display: flex; flex-wrap: wrap; gap: 8rpx; margin-bottom: 10rpx; }
.ndf-tag { font-size: 20rpx; color: #475569; background: #F1F5F9; padding: 4rpx 14rpx; border-radius: 8rpx; }
.ndf-conns { display: flex; flex-wrap: wrap; align-items: center; gap: 8rpx; }
.ndf-conn-label { font-size: 22rpx; color: #94A3B8; }
.ndf-conn-item { font-size: 22rpx; color: #475569; background: #F8FAFC; padding: 4rpx 14rpx; border-radius: 8rpx; border: 1rpx solid #E2E8F0; }
.ndf-conn-item:active { background: #F1F5F9; }
.ndf-actions { display: flex; gap: 12rpx; margin-top: 14rpx; padding-top: 14rpx; border-top: 1rpx solid #F1F5F9; }
.ndf-action-btn { flex: 1; padding: 14rpx; text-align: center; background: #F8FAFC; border-radius: 10rpx; border: 1rpx solid #E2E8F0; }
.ndf-action-btn:active { background: #F1F5F9; }
.ndf-action-text { font-size: 24rpx; color: #475569; font-weight: 500; }

/* 缩放控制 */
.zoom-controls {
  position: absolute; bottom: 80rpx; right: 16rpx;
  display: flex; flex-direction: column; align-items: center; gap: 4rpx;
  background: #FFFFFF; border-radius: 12rpx; padding: 8rpx;
  box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.08); z-index: 10;
  border: 1rpx solid #E2E8F0;
}
.zoom-btn { width: 52rpx; height: 52rpx; display: flex; align-items: center; justify-content: center; background: #F8FAFC; border-radius: 8rpx; transition: all 0.2s ease; }
.zoom-btn:active { background: #E2E8F0; transform: scale(0.95); }
.zoom-text { font-size: 30rpx; color: #475569; font-weight: 700; line-height: 1; }
.zoom-label { font-size: 18rpx; color: #94A3B8; padding: 2rpx 0; font-weight: 500; }
.zoom-divider { width: 32rpx; height: 1rpx; background: #E2E8F0; margin: 4rpx auto; }
.zoom-btn.reset { background: #F0FDFA; }
.zoom-btn.reset:active { background: #CCFBF1; }
.reset-icon { font-size: 26rpx; }

/* ── 设备手册/故障案例/问答样式 ── */
.section-list-header { display: flex; align-items: center; justify-content: space-between; padding: 20rpx 24rpx 12rpx; }
.section-list-title { font-size: 30rpx; font-weight: 700; color: #0F172A; }
.section-list-count { font-size: 22rpx; color: #94A3B8; }
.section-empty { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 80rpx 40rpx; }
.section-empty-icon { font-size: 64rpx; margin-bottom: 16rpx; }
.section-empty-text { font-size: 26rpx; color: #94A3B8; }

/* 手册卡片 */
.kb-doc-card { display: flex; align-items: center; gap: 16rpx; padding: 20rpx 24rpx; margin: 0 16rpx 12rpx; background: #FFFFFF; border-radius: 16rpx; border: 1rpx solid #E2E8F0; }
.kb-doc-icon-wrap { width: 72rpx; height: 72rpx; border-radius: 14rpx; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.kb-doc-icon { font-size: 32rpx; }
.kb-doc-info { flex: 1; min-width: 0; }
.kb-doc-title { font-size: 28rpx; font-weight: 600; color: #0F172A; display: block; margin-bottom: 4rpx; }
.kb-doc-meta { font-size: 22rpx; color: #94A3B8; display: block; margin-bottom: 6rpx; }
.kb-doc-tags { display: flex; gap: 6rpx; }
.kb-doc-tag { font-size: 18rpx; color: #0F766E; background: rgba(15,118,110,0.08); padding: 2rpx 10rpx; border-radius: 6rpx; }
.kb-doc-arrow { font-size: 32rpx; color: #CBD5E1; }

/* 案例卡片 */
.kb-case-card { display: flex; gap: 0; margin: 0 16rpx 12rpx; background: #FFFFFF; border-radius: 16rpx; border: 1rpx solid #E2E8F0; overflow: hidden; }
.kb-case-severity { width: 8rpx; flex-shrink: 0; }
.kb-case-body { flex: 1; padding: 20rpx 24rpx; }
.kb-case-title { font-size: 28rpx; font-weight: 600; color: #0F172A; display: block; margin-bottom: 6rpx; }
.kb-case-desc { font-size: 22rpx; color: #64748B; line-height: 1.5; display: block; margin-bottom: 8rpx; }
.kb-case-meta-row { display: flex; gap: 16rpx; }
.kb-case-meta { font-size: 20rpx; color: #94A3B8; }

/* 问答卡片 */
.kb-qa-card { margin: 0 16rpx 12rpx; background: #FFFFFF; border-radius: 16rpx; border: 1rpx solid #E2E8F0; overflow: hidden; }
.kb-qa-question { display: flex; align-items: center; gap: 12rpx; padding: 20rpx 24rpx; }
.kb-qa-icon { width: 40rpx; height: 40rpx; border-radius: 10rpx; background: #0EA5E9; color: #FFFFFF; font-size: 22rpx; font-weight: 700; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.kb-qa-icon.a { background: #10B981; }
.kb-qa-qtext { flex: 1; font-size: 26rpx; font-weight: 600; color: #0F172A; }
.kb-qa-arrow { font-size: 24rpx; color: #94A3B8; }
.kb-qa-answer { display: flex; gap: 12rpx; padding: 0 24rpx 20rpx; }
.kb-qa-atext { flex: 1; font-size: 24rpx; color: #475569; line-height: 1.6; white-space: pre-wrap; }

/* ── 文件阅读器 ── */
.reader-mask {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0,0,0,0.5); z-index: 200;
  display: flex; align-items: flex-end; justify-content: center;
}
.reader-panel {
  width: 100%; max-height: 90vh; background: #FFFFFF;
  border-radius: 24rpx 24rpx 0 0; display: flex; flex-direction: column;
  animation: slideUpReader 0.3s ease;
}
@keyframes slideUpReader { from { transform: translateY(100%); } to { transform: translateY(0); } }
.reader-header { display: flex; align-items: center; justify-content: space-between; padding: 20rpx 24rpx; border-bottom: 1rpx solid #E2E8F0; }
.reader-header-left { display: flex; align-items: center; gap: 12rpx; flex: 1; min-width: 0; }
.reader-back { font-size: 32rpx; color: #64748B; }
.reader-title { font-size: 30rpx; font-weight: 700; color: #0F172A; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.reader-header-right { display: flex; align-items: center; gap: 16rpx; }
.reader-fav { font-size: 32rpx; }
.reader-close-btn { font-size: 32rpx; color: #94A3B8; }
.reader-meta-bar { display: flex; gap: 20rpx; padding: 12rpx 24rpx; border-bottom: 1rpx solid #F1F5F9; }
.reader-meta { font-size: 22rpx; color: #94A3B8; }
.reader-tags { display: flex; flex-wrap: wrap; gap: 8rpx; padding: 12rpx 24rpx; }
.reader-tag { font-size: 20rpx; color: #0F766E; background: rgba(15,118,110,0.08); padding: 4rpx 14rpx; border-radius: 8rpx; }
.reader-body { flex: 1; padding: 24rpx; max-height: 50vh; }
.reader-content { font-size: 26rpx; color: #334155; line-height: 1.8; white-space: pre-wrap; }
.reader-footer { display: flex; gap: 12rpx; padding: 16rpx 24rpx; border-top: 1rpx solid #E2E8F0; }
.reader-action { flex: 1; padding: 16rpx; text-align: center; border-radius: 12rpx; background: #F1F5F9; font-size: 26rpx; color: #475569; }
.reader-action:active { background: #E2E8F0; }
.reader-action.primary { background: #60A5FA; color: #FFFFFF; }

/* 技术资料库 */
.tech-lib-area { padding: 0 24rpx; }
.tech-filter-bar {
  display: flex;
  gap: 0;
  padding: 20rpx 0 16rpx;
  position: sticky;
  top: 0;
  background: #F5F6FA;
  z-index: 10;
}
.tech-filter-item {
  flex: 1;
  text-align: center;
  padding: 14rpx 0;
  border-bottom: 4rpx solid transparent;
  transition: all 0.2s;
}
.tech-filter-bar {
  display: flex;
  gap: 0;
  padding: 20rpx 0 16rpx;
  position: sticky;
  top: 0;
  background: #FAFBFF;
  z-index: 10;
}
.tech-filter-item {
  flex: 1;
  text-align: center;
  padding: 14rpx 0;
  border-bottom: 4rpx solid transparent;
  transition: all 0.2s;
}
.tech-filter-item.active {
  border-bottom-color: #60A5FA;
}
.tech-filter-label {
  font-size: 26rpx;
  color: #94A3B8;
  font-weight: 500;
}
.tech-filter-item.active .tech-filter-label {
  color: #1E40AF;
  font-weight: 700;
}
.tech-filter-count {
  display: inline-block;
  font-size: 18rpx;
  color: #94A3B8;
  background: #F1F5F9;
  padding: 2rpx 10rpx;
  border-radius: 6rpx;
  margin-left: 6rpx;
}
.tech-filter-item.active .tech-filter-count {
  background: #DBEAFE;
  color: #3B82F6;
}
.tech-card {
  display: flex;
  align-items: flex-start;
  gap: 16rpx;
  padding: 24rpx 20rpx;
  background: #FFFFFF;
  border-radius: 16rpx;
  margin-bottom: 12rpx;
  box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.04);
}
.tech-card:active {
  background: #F8FAFC;
}
.tech-card-dot {
  width: 10rpx;
  height: 10rpx;
  border-radius: 50%;
  flex-shrink: 0;
  margin-top: 14rpx;
}
.tech-card-body {
  flex: 1;
  min-width: 0;
}
.tech-card-head {
  display: flex;
  align-items: center;
  gap: 10rpx;
  margin-bottom: 6rpx;
}
.tech-card-title {
  font-size: 28rpx;
  font-weight: 600;
  color: #1E293B;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.tech-card-tag {
  font-size: 18rpx;
  padding: 3rpx 10rpx;
  border-radius: 6rpx;
  font-weight: 600;
  flex-shrink: 0;
  background: #DBEAFE;
  color: #2563EB;
}
.tech-card-tag.tag-high {
  background: #FEE2E2;
  color: #DC2626;
}
.tech-card-tag.tag-medium {
  background: #FEF3C7;
  color: #D97706;
}
.tech-card-tag.tag-low {
  background: #D1FAE5;
  color: #059669;
}
.tech-card-desc {
  font-size: 24rpx;
  color: #6B7280;
  line-height: 1.5;
  margin-bottom: 8rpx;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.tech-card-meta {
  display: flex;
  gap: 16rpx;
}
.tech-card-meta-item {
  font-size: 20rpx;
  color: #9CA3AF;
}
.tech-card-arrow {
  font-size: 28rpx;
  color: #CBD5E1;
  flex-shrink: 0;
  margin-top: 8rpx;
}
.tech-qa-card {
  background: #FFFFFF;
  border-radius: 16rpx;
  margin-bottom: 12rpx;
  overflow: hidden;
  box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.04);
}
.tech-qa-card:active {
  background: #F8FAFC;
}
.tech-qa-head {
  display: flex;
  align-items: center;
  gap: 12rpx;
  padding: 24rpx 20rpx;
}
.tech-qa-q {
  width: 44rpx;
  height: 44rpx;
  line-height: 44rpx;
  text-align: center;
  background: #60A5FA;
  color: #FFFFFF;
  font-size: 24rpx;
  font-weight: 700;
  border-radius: 10rpx;
  flex-shrink: 0;
}
.tech-qa-question {
  flex: 1;
  font-size: 28rpx;
  font-weight: 600;
  color: #1E293B;
  line-height: 1.4;
}
.tech-qa-arrow {
  font-size: 24rpx;
  color: #9CA3AF;
  flex-shrink: 0;
}
.tech-qa-body {
  display: flex;
  gap: 12rpx;
  padding: 0 20rpx 24rpx;
  border-top: 1rpx solid #F1F5F9;
}
.tech-qa-a {
  width: 44rpx;
  height: 44rpx;
  line-height: 44rpx;
  text-align: center;
  background: #EFF6FF;
  color: #3B82F6;
  font-size: 24rpx;
  font-weight: 700;
  border-radius: 10rpx;
  flex-shrink: 0;
}
.tech-qa-answer {
  flex: 1;
  font-size: 26rpx;
  color: #374151;
  line-height: 1.7;
  white-space: pre-wrap;
  padding-top: 4rpx;
}
.tech-empty {
  padding: 48rpx 0;
  text-align: center;
}
.tech-empty-text {
  font-size: 26rpx;
  color: #9CA3AF;
}
</style>
