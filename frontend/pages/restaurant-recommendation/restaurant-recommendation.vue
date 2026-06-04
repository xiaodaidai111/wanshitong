<template>
  <view class="page-root" :style="{ '--kb-status-bar-height': statusBarHeight + 'px' }">
    <view class="kb-top-nav">
      <view class="kb-nav-center">
        <text class="kb-nav-title">知识沉淀</text>
        <text class="kb-nav-subtitle">{{ kbTabs[currentKbTab].label }}</text>
      </view>
      <view class="kb-nav-hint">
        <text class="kb-nav-hint-text">双指缩放</text>
      </view>
    </view>
    <!-- 折叠态：图标栏 -->
    <view v-show="sideCollapsed" class="mini-bar">
      <view class="mb-toggle" @click="sideCollapsed = false">
        <text class="mb-toggle-icon">☰</text>
      </view>
      <view v-for="(tab, i) in kbTabs" :key="i" class="mb-item" :class="{ active: currentKbTab === i }" @click="switchKbTab(i); sideCollapsed = false">
        <text class="mb-icon">{{ tab.icon }}</text>
      </view>
    </view>
    <!-- 展开态：侧边栏 -->
    <view v-show="!sideCollapsed" class="sidebar">
      <view class="side-header">
        <text class="side-logo">🗂️</text>
        <text class="side-title">知识沉淀</text>
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
      <view class="side-add" @click="showAddNode = true">
        <text class="side-add-icon">+</text>
        <text class="side-add-text">添加知识点</text>
      </view>
    </view>

    <!-- 主内容区 -->
    <view class="main-area">
      <!-- 知识网络 -->
      <view v-show="currentKbTab === 0" class="canvas-area">
        <canvas canvas-id="kbGraph" id="kbGraph" class="full-canvas"
          @touchstart="onGraphTouchStart" @touchmove="onGraphTouchMove" @touchend="onGraphTouchEnd"></canvas>
        <view v-if="selectedNode" class="node-detail-float">
          <view class="ndf-head">
            <text class="ndf-title">{{ selectedNode.label }}</text>
            <text class="ndf-cat">{{ selectedNode.category }}</text>
            <text class="ndf-close" @click="selectedNode = null">×</text>
          </view>
          <text class="ndf-desc">{{ selectedNode.desc || '暂无描述' }}</text>
          <view class="ndf-tags">
            <text class="ndf-tag" v-for="(t, ti) in (selectedNode.tags || [])" :key="ti">{{ t }}</text>
          </view>
          <view class="ndf-conns">
            <text class="ndf-conn-label">关联：</text>
            <text class="ndf-conn-item" v-for="(c, ci) in getNodeConns(selectedNode)" :key="ci" @click="focusNode(c)">{{ c.label }}</text>
          </view>
        </view>
      </view>
      <!-- 思维导图 -->
      <view v-show="currentKbTab === 1" class="canvas-area">
        <canvas canvas-id="kbMind" id="kbMind" class="full-canvas"
          @touchstart="onMindTouchStart" @touchmove="onMindTouchMove" @touchend="onMindTouchEnd"></canvas>
        <view class="mind-controls">
          <view class="mc-btn" @click="expandAllMind"><text class="mc-text">全部展开</text></view>
          <view class="mc-btn" @click="collapseAllMind"><text class="mc-text">全部折叠</text></view>
        </view>
      </view>
      <!-- 知识卡片（主区大卡片） -->
      <scroll-view v-show="currentKbTab === 2" scroll-y class="card-main-area">
        <view v-for="(node, i) in filteredKbNodes" :key="i" class="kb-card-main" @click="selectNode(node)">
          <view class="kbc-icon-wrap"><text class="kbc-icon">{{ node.icon || '📄' }}</text></view>
          <view class="kbc-body">
            <view class="kbc-head">
              <text class="kbc-title">{{ node.label }}</text>
              <text class="kbc-cat">{{ node.category || '' }}</text>
            </view>
            <text class="kbc-desc">{{ node.desc || '' }}</text>
            <view class="kbc-tags">
              <text class="kbc-tag" v-for="(t, ti) in (node.tags || [])" :key="ti">{{ t }}</text>
            </view>
          </view>
        </view>
      </scroll-view>
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
            <image src="../../static/niceexpert.png" mode="aspectFit" class="agent-img"></image>
          </view>
          <view class="header-text">
            <text class="agent-title">藏典</text>
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
            <text class="bubble-text">您好！我是藏典，知识沉淀与更新助手。\n\n我负责整理设备资料库、检修案例库、经验总结、作业记录和检修知识图谱；一线人员上传案例后，可经审核纳入图谱，并支持手动标注与修正模型输出。\n\n请在下方输入你想整理或入库的设备知识：</text>
            <view class="quick-suggestions">
              <view class="sugg-tag" @click="quickMessage('整理ZK-320配电柜检修案例')">整理检修案例</view>
              <view class="sugg-tag" @click="quickMessage('生成变频器过热故障知识图谱')">生成知识图谱</view>
              <view class="sugg-tag" @click="quickMessage('补充泵站电机轴承异响经验总结')">经验总结入库</view>
              <view class="sugg-tag" @click="quickMessage('修正模型对故障原因的判断')">标注修正</view>
              <view class="sugg-tag" @click="quickMessage('构建设备型号与故障现象关联网络')">构建关联网络</view>
            </view>
          </view>
          <block v-for="(msg, index) in chatHistory" :key="index">
            <view class="message-row" :class="msg.type">
              <view v-if="msg.type === 'expert'" class="message-avatar agent-avatar-wrap">
                <image src="../../static/niceexpert.png" mode="aspectFit" class="avatar-img"></image>
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
            <input type="text" v-model="userMessage" placeholder="输入设备型号、故障现象或入库问题" class="neo-input" placeholder-class="input-placeholder" @confirm="sendMessage" @input="handleInput" />
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
import { API_HOST } from '../../utils/request.js';
import { createVoiceInputController } from '../../utils/voice-input.js';

const MAP_API_BASE = `${API_HOST}:5000/map/api`;
const USER_API_BASE = `${API_HOST}:5000/api/user`;

export default {
  components: {
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
      apiBaseUrl: MAP_API_BASE,
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
      commonCuisines: ['检修手册', '设备说明书', '故障图片', '铭牌型号', '检修案例', '经验总结', '备件清单', '作业记录', '合规条款', '风险提醒', '复盘报告', '知识图谱'],
      commonHabits: ['案例驱动', '图文标注', '型号关联', '风险优先', '标准流程', '审核入库', '人工修正', '实时更新', '现场复盘', '经验沉淀', '跨模态检索', '合规校验'],
      customCuisine: '',
      kbTabs: [{ icon: '🌐', label: '检修图谱' }, { icon: '🧠', label: '故障链路' }, { icon: '📋', label: '沉淀卡片' }],
      currentKbTab: 0, kbSearchText: '', showAddNode: false, showSearch: false, selectedNode: null, sideCollapsed: false,
      statusBarHeight: 10,
      graphDrag: { startX: 0, startY: 0, offsetX: 0, offsetY: 0, dragging: false, scale: 1, pinchDist: 0 },
      mindDrag: { startX: 0, startY: 0, offsetX: 0, offsetY: 0, dragging: false, scale: 1, pinchDist: 0 },
      kbNodes: [
        { id: 1, label: 'ZK-320配电柜', category: '设备', icon: '⚡', desc: '低压配电柜设备资料、铭牌参数与检修规程。', tags: ['设备'], x: 200, y: 300 },
        { id: 2, label: '柜体过热', category: '故障现象', icon: '🌡️', desc: '柜内温升异常、端子发热、风道堵塞等常见现象。', tags: ['过热'], x: 100, y: 180 },
        { id: 3, label: '接线端子松动', category: '故障原因', icon: '🔩', desc: '端子松动导致接触电阻升高并引发局部过热。', tags: ['原因'], x: 80, y: 420 },
        { id: 4, label: '故障图片', category: '多模态证据', icon: '🖼️', desc: '现场照片、热成像图、铭牌截图等跨模态证据。', tags: ['图片'], x: 350, y: 180 },
        { id: 5, label: '检修手册', category: '资料库', icon: '📘', desc: '设备说明书、检修规程和厂家技术手册。', tags: ['手册'], x: 380, y: 420 },
        { id: 6, label: '标准作业票', category: '作业流程', icon: '📋', desc: '二级检修步骤、合规校验和复核记录。', tags: ['流程'], x: 150, y: 520 },
        { id: 7, label: '安全隔离', category: '合规要求', icon: '🛡️', desc: '停电验电、挂牌上锁、防护用品等安全要求。', tags: ['安全'], x: 50, y: 520 },
        { id: 8, label: '相似案例', category: '案例库', icon: '🧰', desc: '历史故障处置案例、经验总结和处理结论。', tags: ['案例'], x: 220, y: 80 },
        { id: 9, label: '备件清单', category: '资源', icon: '🔧', desc: '端子排、风扇、温控模块等备件规格。', tags: ['备件'], x: 400, y: 520 },
        { id: 10, label: '人工修正', category: '更新机制', icon: '✍️', desc: '人工标注与修正模型输出，审核后入库更新。', tags: ['沉淀'], x: 280, y: 580 }
      ],
      kbConnections: [
        { from: 1, to: 2 }, { from: 1, to: 4 }, { from: 1, to: 5 },
        { from: 2, to: 3 }, { from: 2, to: 7 }, { from: 2, to: 10 },
        { from: 3, to: 8 }, { from: 3, to: 5 },
        { from: 4, to: 8 }, { from: 6, to: 2 }, { from: 6, to: 10 },
        { from: 7, to: 3 }, { from: 9, to: 3 }, { from: 9, to: 1 }
      ],
      mindRoot: {
        id: 0, label: '设备检修知识体系', collapsed: false, children: [
          { id: 1, label: '设备资料库', collapsed: false, children: [
            { id: 6, label: '标准作业票', collapsed: false, children: [] },
            { id: 7, label: '安全隔离要求', collapsed: false, children: [] }
          ]},
          { id: 2, label: '故障案例库', collapsed: false, children: [
            { id: 3, label: '柜体过热', collapsed: false, children: [
              { id: 8, label: '相似案例', collapsed: false, children: [] },
              { id: 5, label: '检修手册', collapsed: false, children: [] }
            ]}
          ]},
          { id: 4, label: '多模态证据', collapsed: false, children: [] }
        ]
      },
      newNode: { label: '', category: '', desc: '', tagsStr: '' },
      nodeColors: ['#0F766E', '#14B8A6', '#0369A1', '#0EA5E9', '#06B6D4', '#10B981', '#8B5CF6', '#EC4899', '#F59E0B', '#EF4444'],
      graphAnimFrame: null,
      graphTime: 0,
      selectedNodePulse: 0,
      particleEffects: [],
    }
  },
  computed: {
    filteredKbNodes() {
      if (!this.kbSearchText.trim()) return this.kbNodes
      const kw = this.kbSearchText.trim().toLowerCase()
      return this.kbNodes.filter(n => n.label.toLowerCase().includes(kw) || (n.desc || '').toLowerCase().includes(kw))
    }
  },
  mounted() {
    this.initConversation();
    this.loadPreferences();
    this.initVoiceInput();
    this.loadKbData();
    const sys = uni.getSystemInfoSync();
    this.statusBarHeight = Math.max(sys.statusBarHeight || 0, 10);
  },
  onReady() {
    setTimeout(() => {
      this.drawGraph()
      this.drawMindMap()
      this.startGraphAnimation()
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
      // 当前地图智能体的后端不强制需要预创建会话，这里本地生成一个ID即可
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
        preferences: this.preferences
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
        console.log('真实定位:', this.currentLocation);
        console.log('发送给路径规划智能体:', requestPayload);

        const result = await uni.request({
          url: `${this.apiBaseUrl}/messages`,
          method: 'POST',
          header: { 'content-type': 'application/json' },
          data: requestPayload,
          timeout: 30000
        });
        
        const res = Array.isArray(result) ? result[1] : result;
        const payload = res?.data;
        let data = null;
        if (payload && typeof payload === 'object') {
          data = payload.data ?? payload;
        } else if (typeof payload === 'string') {
          try {
            const parsed = JSON.parse(payload);
            data = parsed?.data ?? parsed;
          } catch (e) {
            data = null;
          }
        }

        const history = this.chatHistory.filter(m => !m.loading);
        let thinkingSteps = Array.isArray(data?.thinking_process) ? data.thinking_process : [];
        let responseMsg = data?.response || '路径规划智能体正在思考中，请稍后再试...';
        console.log('路径规划接口完整返回:', data);
        console.log('高德POI数据:', data?.pois || []);
        this.recommendationMarkers = this.normalizePois(data?.pois);

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
        console.error('AI Link failed:', err);
        
        if (this.retryCount < this.maxRetries) {
          this.retryCount++;
          console.log(`Retrying... (${this.retryCount}/${this.maxRetries})`);
          await new Promise(resolve => setTimeout(resolve, 1000 * this.retryCount));
          return this.sendMessageWithRetry(userMsg);
        }
        
        const history = this.chatHistory.filter(m => !m.loading);
        
        let errorMsg = '由于信号干扰暂无法连接，请重新呼叫路径规划智能体';
        if (err.errMsg && err.errMsg.includes('timeout')) {
          errorMsg = '响应超时，请稍后再试';
        } else if (err.errMsg && err.errMsg.includes('network')) {
          errorMsg = '网络连接失败，请检查网络';
        }
        
        this.chatHistory = [
          ...history,
          { type: 'expert', message: errorMsg }
        ];
        this.recommendationMarkers = [];
        this.isSending = false;
        this.scrollToBottom();
      }
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
      try { const s = uni.getStorageSync('kb_data'); if (s) { const d = JSON.parse(s); if (d.nodes) this.kbNodes = d.nodes; if (d.connections) this.kbConnections = d.connections; if (d.mindRoot) this.mindRoot = d.mindRoot } } catch (e) {}
    },
    saveKbData() {
      try { uni.setStorageSync('kb_data', JSON.stringify({ nodes: this.kbNodes, connections: this.kbConnections, mindRoot: this.mindRoot })) } catch (e) {}
    },
    switchKbTab(i) {
      this.currentKbTab = i
      this.selectedNode = null
      if (i === 0) this.$nextTick(() => this.drawGraph())
      if (i === 1) this.$nextTick(() => this.drawMindMap())
    },
    selectNode(node) { this.selectedNode = node; this.currentKbTab = 0; this.$nextTick(() => this.drawGraph()) },
    getNodeConns(node) {
      const ids = this.kbConnections.filter(c => c.from === node.id || c.to === node.id).map(c => c.from === node.id ? c.to : c.from)
      return this.kbNodes.filter(n => ids.includes(n.id))
    },
    focusNode(node) { this.selectedNode = node; this.drawGraph() },
    _getTouchPos(e) {
      const t = e.touches && e.touches[0] ? e.touches[0] : (e.changedTouches && e.changedTouches[0] ? e.changedTouches[0] : null)
      if (!t) return null
      return { x: t.x || t.clientX || 0, y: t.y || t.clientY || 0 }
    },
    _getPinchDist(e) {
      if (!e.touches || e.touches.length < 2) return 0
      const a = e.touches[0], b = e.touches[1]
      const ax = a.x || a.clientX || 0
      const ay = a.y || a.clientY || 0
      const bx = b.x || b.clientX || 0
      const by = b.y || b.clientY || 0
      return Math.sqrt((ax - bx) ** 2 + (ay - by) ** 2)
    },
    onGraphTouchStart(e) {
      if (e.touches && e.touches.length >= 2) {
        this.graphDrag.pinchDist = this._getPinchDist(e); return
      }
      const t = this._getTouchPos(e); if (!t) return
      this.graphDrag.startX = t.x; this.graphDrag.startY = t.y; this.graphDrag.dragging = false
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
      if (!this.graphDrag.dragging) {
        const t = this._getTouchPos(e); if (!t) return
        let n = null, min = 60
        const s = this.graphDrag.scale
        this.kbNodes.forEach(nd => {
          const sx = nd.x * s + this.graphDrag.offsetX, sy = nd.y * s + this.graphDrag.offsetY
          const d = Math.sqrt((sx - t.x) ** 2 + (sy - t.y) ** 2)
          if (d < min) { min = d; n = nd }
        })
        if (n) { this.selectedNode = n; this.drawGraph() }
      }
      this.graphDrag.dragging = false
    },
    drawGraph() {
      const ctx = uni.createCanvasContext('kbGraph', this)
      uni.createSelectorQuery().in(this).select('#kbGraph').boundingClientRect(rect => {
        if (!rect) {
          return
        }
        const w = rect.width, h = rect.height
        ctx.clearRect(0, 0, w, h)

        const ox = this.graphDrag.offsetX, oy = this.graphDrag.offsetY, sc = this.graphDrag.scale
        const pulse = 0.5 + Math.sin(this.graphTime / 18) * 0.5

        ctx.setFillStyle('#F8FFFD')
        ctx.fillRect(0, 0, w, h)

        // 浅色 Obsidian 风格网格
        const grid = Math.max(24, 42 * sc)
        const gridX = ((ox % grid) + grid) % grid
        const gridY = ((oy % grid) + grid) % grid
        ctx.setStrokeStyle('rgba(15,118,110,0.08)')
        ctx.setLineWidth(1)
        for (let gx = gridX; gx < w; gx += grid) {
          ctx.beginPath(); ctx.moveTo(gx, 0); ctx.lineTo(gx, h); ctx.stroke()
        }
        for (let gy = gridY; gy < h; gy += grid) {
          ctx.beginPath(); ctx.moveTo(0, gy); ctx.lineTo(w, gy); ctx.stroke()
        }

        // 连线
        this.kbConnections.forEach(c => {
          const f = this.kbNodes.find(n => n.id === c.from)
          const t = this.kbNodes.find(n => n.id === c.to)
          if (f && t) {
            const fx = f.x * sc + ox, fy = f.y * sc + oy
            const tx = t.x * sc + ox, ty = t.y * sc + oy
            const isActive = this.selectedNode && (this.selectedNode.id === c.from || this.selectedNode.id === c.to)

            // 选中连线保留轻量发光效果
            if (isActive) {
              ctx.setStrokeStyle(`rgba(14,165,233,${0.18 + pulse * 0.12})`)
              ctx.setLineWidth(9 * sc)
              ctx.beginPath(); ctx.moveTo(fx, fy); ctx.lineTo(tx, ty); ctx.stroke()
            }

            ctx.setStrokeStyle(isActive ? '#0EA5E9' : 'rgba(20,184,166,0.26)')
            ctx.setLineWidth(isActive ? 2.4 * sc : 1.4 * sc)
            ctx.beginPath(); ctx.moveTo(fx, fy); ctx.lineTo(tx, ty); ctx.stroke()
          }
        })

        // 节点
        this.kbNodes.forEach(nd => {
          const x = nd.x * sc + ox, y = nd.y * sc + oy
          const sel = this.selectedNode && this.selectedNode.id === nd.id
          const r = (sel ? 34 : 24) * sc
          const color = this.nodeColors[nd.id % this.nodeColors.length]

          // 选中节点光晕
          if (sel) {
            ctx.beginPath()
            ctx.arc(x, y, r + (16 + pulse * 8) * sc, 0, Math.PI * 2)
            ctx.setFillStyle('rgba(14,165,233,0.14)')
            ctx.fill()
          }

          // 节点阴影
          ctx.beginPath()
          ctx.arc(x, y + 4 * sc, r, 0, Math.PI * 2)
          ctx.setFillStyle('rgba(15,23,42,0.12)')
          ctx.fill()

          // 节点本体
          ctx.beginPath()
          ctx.arc(x, y, r, 0, Math.PI * 2)
          ctx.setFillStyle(sel ? '#0EA5E9' : '#FFFFFF')
          ctx.fill()
          ctx.setStrokeStyle(sel ? '#0284C7' : color)
          ctx.setLineWidth(sel ? 3 * sc : 2 * sc)
          ctx.stroke()

          // 内层高光
          ctx.beginPath()
          ctx.arc(x, y, Math.max(2, r * 0.3), 0, Math.PI * 2)
          ctx.setFillStyle(sel ? 'rgba(255,255,255,0.28)' : 'rgba(14,165,233,0.08)')
          ctx.fill()

          // 节点文字
          ctx.setFillStyle(sel ? '#0369A1' : '#134E4A')
          ctx.setFontSize(Math.max(10, (sel ? 15 : 13) * sc))
          ctx.setTextAlign('center')
          ctx.setTextBaseline('middle')
          ctx.fillText(nd.label, x, y + r + 18 * sc)

          // 图标
          if (nd.icon) {
            ctx.setFillStyle(sel ? '#FFFFFF' : color)
            ctx.setFontSize(Math.max(12, 20 * sc))
            ctx.fillText(nd.icon, x, y)
          }
        })

        ctx.draw()
      }).exec()
    },

    startGraphAnimation() {
      if (this.graphAnimFrame) return
      const tick = () => {
        this.graphTime += 1
        if (this.currentKbTab === 0) this.drawGraph()
        this.graphAnimFrame = setTimeout(tick, 900)
      }
      this.graphAnimFrame = setTimeout(tick, 900)
    },

    stopGraphAnimation() {
      if (this.graphAnimFrame) {
        clearTimeout(this.graphAnimFrame)
        this.graphAnimFrame = null
      }
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
    addKbNode() {
      if (!this.newNode.label.trim()) { uni.showToast({ title: '请输入名称', icon: 'none' }); return }
      this.kbNodes.push({ id: Date.now(), label: this.newNode.label.trim(), category: this.newNode.category.trim() || '未分类', desc: this.newNode.desc.trim(), tags: this.newNode.tagsStr.split(/[,，]/).map(s => s.trim()).filter(Boolean), icon: '📄', x: 40 + Math.random() * 320, y: 80 + Math.random() * 420 })
      this.saveKbData(); this.drawGraph(); this.showAddNode = false; this.newNode = { label: '', category: '', desc: '', tagsStr: '' }; uni.showToast({ title: '添加成功', icon: 'success' })
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

/* 智能体卡片 - 静态知识助手 */
.agent-card {
  position: fixed;
  bottom: calc(80rpx + env(safe-area-inset-bottom));
  left: 30rpx;
  right: 30rpx;
  background: #ffffff;
  border-radius: 24rpx;
  box-shadow: 0 14rpx 40rpx rgba(15,23,42,0.12);
  pointer-events: auto;
  transition: transform 0.4s cubic-bezier(0.23, 1, 0.32, 1);
  overflow: hidden;
  z-index: 350;
  display: block !important;
  border: 1rpx solid #D8DEE9;
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
  background: #F8FAFC;
  border-bottom: 1rpx solid #E2E8F0;
  position: relative;
}

.card-header::after {
  display: none;
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
  position: relative;
  width: 88rpx;
  height: 88rpx;
  margin-right: 24rpx;
}

.agent-img {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: #fff;
  border: 1rpx solid #CBD5E1;
}

.header-text {
  display: flex;
  flex-direction: column;
}

.agent-title {
  font-size: 32rpx;
  font-weight: 700;
  color: #1E293B;
  letter-spacing: 0;
}

.agent-badge {
  display: flex;
  align-items: center;
  margin-top: 4rpx;
}

.badge-dot {
  width: 10rpx;
  height: 10rpx;
  background: #10B981;
  border-radius: 50%;
  margin-right: 8rpx;
  box-shadow: none;
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
  background: #FFFFFF;
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
}

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
.page-root { width: 100%; height: 100vh; position: relative; background: #F8FFFD; overflow: hidden; }

.kb-top-nav {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: calc(44px + var(--kb-status-bar-height));
  padding: var(--kb-status-bar-height) 28rpx 0;
  box-sizing: border-box;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255,255,255,0.96);
  border-bottom: 1rpx solid #D7F4EF;
  box-shadow: 0 6rpx 24rpx rgba(15,118,110,0.08);
  z-index: 80;
}

.kb-nav-center {
  min-width: 0;
  height: 44px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2rpx;
  text-align: center;
}

.kb-nav-title {
  font-size: 36rpx;
  font-weight: 800;
  color: #134E4A;
  line-height: 1.1;
}

.kb-nav-subtitle {
  font-size: 22rpx;
  color: #0EA5E9;
  line-height: 1.1;
}

.kb-nav-hint {
  position: absolute;
  right: 28rpx;
  bottom: 10rpx;
  flex-shrink: 0;
  padding: 10rpx 18rpx;
  border-radius: 999rpx;
  background: #F0FDFA;
  border: 1rpx solid #99F6E4;
}

.kb-nav-hint-text {
  font-size: 22rpx;
  color: #0F766E;
  font-weight: 600;
}

/* 折叠态图标栏 */
.mini-bar { position: absolute; top: calc(44px + var(--kb-status-bar-height)); left: 0; width: 80rpx; background: rgba(255,255,255,0.96); border-right: 1rpx solid #D7F4EF; border-bottom: 1rpx solid #D7F4EF; display: flex; flex-direction: column; align-items: center; padding-top: 16rpx; gap: 8rpx; z-index: 50; box-shadow: 4rpx 0 18rpx rgba(15,118,110,0.08); border-radius: 0 0 16rpx 0; }
.mb-toggle { width: 56rpx; height: 56rpx; border-radius: 12rpx; display: flex; align-items: center; justify-content: center; background: #F0FDFA; margin-bottom: 8rpx; }
.mb-toggle-icon { font-size: 28rpx; color: #0F766E; }
.mb-item { width: 56rpx; height: 56rpx; border-radius: 12rpx; display: flex; align-items: center; justify-content: center; }
.mb-item.active { background: rgba(14,165,233,0.12); }
.mb-icon { font-size: 28rpx; }

/* 展开态侧边栏 */
.sidebar { position: absolute; top: calc(44px + var(--kb-status-bar-height)); left: 0; width: 480rpx; background: rgba(255,255,255,0.97); border-right: 1rpx solid #D7F4EF; border-bottom: 1rpx solid #D7F4EF; display: flex; flex-direction: column; z-index: 50; box-shadow: 4rpx 0 20rpx rgba(15,118,110,0.08); border-radius: 0 0 16rpx 0; }

.side-header { padding: 24rpx 20rpx 16rpx; display: flex; align-items: center; gap: 10rpx; }
.side-logo { font-size: 32rpx; }
.side-title { font-size: 28rpx; font-weight: 700; color: #134E4A; letter-spacing: 0; flex: 1; }
.side-close { width: 44rpx; height: 44rpx; border-radius: 10rpx; display: flex; align-items: center; justify-content: center; background: #F0FDFA; }
.side-close-icon { font-size: 22rpx; color: #94A3B8; }

.side-tabs { padding: 0 16rpx; display: flex; flex-direction: column; gap: 6rpx; }
.side-tab { display: flex; align-items: center; gap: 12rpx; padding: 14rpx 16rpx; border-radius: 12rpx; transition: all 0.2s; }
.side-tab.active {
  background: rgba(14,165,233,0.08);
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

.side-add {
  margin: 12rpx 16rpx 16rpx;
  padding: 14rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8rpx;
  background: #F8FFFD;
  border-radius: 12rpx;
  border: 1rpx dashed #7DD3FC;
  transition: all 0.2s ease;
}

.side-add:active {
  background: #E0F2FE;
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
.main-area { width: 100%; height: calc(100% - 44px - var(--kb-status-bar-height)); position: absolute; left: 0; right: 0; bottom: 0; overflow: hidden; }
.canvas-area { width: 100%; height: 100%; position: relative; background: #F8FFFD; }
.full-canvas { width: 100%; height: 100%; }

/* 节点详情浮窗 */
.node-detail-float {
  position: absolute;
  bottom: 20rpx;
  left: 20rpx;
  right: 20rpx;
  background: rgba(255,255,255,0.96);
  border-radius: 16rpx;
  padding: 20rpx;
  box-shadow: 0 10rpx 30rpx rgba(15,118,110,0.12);
  z-index: 10;
  border: 1rpx solid #D7F4EF;
  animation: slideUpFloat 0.3s cubic-bezier(0.23, 1, 0.32, 1);
}

@keyframes slideUpFloat {
  from { transform: translateY(20rpx); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.ndf-head { display: flex; align-items: center; gap: 12rpx; margin-bottom: 8rpx; }
.ndf-title { font-size: 30rpx; font-weight: 700; color: #134E4A; }
.ndf-cat {
  font-size: 20rpx;
  color: #0EA5E9;
  background: rgba(14,165,233,0.08);
  padding: 4rpx 12rpx;
  border-radius: 8rpx;
  border: 1rpx solid rgba(14,165,233,0.18);
}
.ndf-close { font-size: 32rpx; color: #94A3B8; margin-left: auto; padding: 4rpx 8rpx; }
.ndf-desc { font-size: 24rpx; color: #64748B; line-height: 1.5; margin-bottom: 8rpx; }
.ndf-tags { display: flex; flex-wrap: wrap; gap: 8rpx; margin-bottom: 8rpx; }
.ndf-tag { font-size: 20rpx; color: #0F766E; background: rgba(15,118,110,0.08); padding: 4rpx 12rpx; border-radius: 8rpx; }
.ndf-conns { display: flex; flex-wrap: wrap; align-items: center; gap: 8rpx; }
.ndf-conn-label { font-size: 22rpx; color: #94A3B8; }
.ndf-conn-item { font-size: 22rpx; color: #0F766E; background: rgba(14,165,233,0.08); padding: 4rpx 12rpx; border-radius: 8rpx; }

/* 缩放控制 */
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
  background: #BFEFE7;
  opacity: 0;
  transition: opacity 0.3s ease;
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
</style>
