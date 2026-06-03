<template>
  <view class="map-recommendation-view" @touchmove.stop.prevent="">
    <!-- 地图底层容器 -->
    <view
      id="amap-container"
      class="amap-container"
      :markers="recommendationMarkers"
      :change:markers="amap.updateMarkers"
    ></view>

    <!-- 顶层遮罩与状态提示-->
    <view v-if="mapStatus === 'error'" class="map-status-mask">
      <view class="error-box">
        <view class="error-icon">🧭</view>
        <text class="error-msg">地图初始化受限</text>
        <text class="debug-hint">请检查网络连接或权限设置</text>
        <button class="retry-btn" @click="amap.retryLoad">尝试修复</button>
      </view>
    </view>

    <!-- 交互 Overlay -->
    <view class="overlay-container">
      <!-- 顶部位置信息 -->
      <view class="top-nav-blur">
        <view class="location-chip" @click="amap.relocate">
          <view class="loc-indicator">
            <view class="pulse-dot"></view>
          </view>
          <text class="loc-name">{{ currentLocationName || '探测课程学习空间...' }}</text>
          <text class="loc-refresh">刷新</text>
        </view>
      </view>

      <!-- 地图浮动工具 -->
      <view class="map-controls">
        <view class="ctrl-btn zoom-in" @click="amap.zoomIn">+</view>
        <view class="ctrl-btn zoom-out" @click="amap.zoomOut">-</view>
        <view class="ctrl-btn relocate" @click="amap.relocate">
          <image src="../../static/icons/food.png" mode="aspectFit" style="width: 40rpx; height: 40rpx;"></image>
        </view>
        <view class="ctrl-btn choose-loc" @click="amap.chooseLocation">
          <image src="../../static/icons/community.png" mode="aspectFit" style="width: 40rpx; height: 40rpx;"></image>
        </view>
        <view class="ctrl-btn preference-btn" @click="openPreferenceModal">
          <image src="../../static/icons/preference.png" mode="aspectFit" style="width: 40rpx; height: 40rpx;"></image>
        </view>
      </view>
    </view>

    <!-- 学习偏好设置弹窗 -->
    <view v-if="showPreferenceModal" class="preference-modal-mask" @click="closePreferenceModal">
      <view class="preference-container" @click.stop="">
        <view class="modal-header">
          <text class="modal-title">学习偏好记忆</text>
          <text class="close-icon" @click="closePreferenceModal">×</text>
        </view>
        <view class="modal-body">
          <view class="pref-section">
            <text class="section-title">学习习惯</text>
            <view class="tag-group">
              <view v-for="h in commonHabits" :key="h" 
                class="tag-item" :class="{'active': isHabitSelected(h)}"
                @click="toggleHabit(h)">{{ h }}</view>
            </view>
          </view>
          <view class="pref-section">
            <text class="section-title">偏好的资源类型</text>
            <view class="tag-group">
              <view v-for="c in commonCuisines" :key="c" 
                class="tag-item" :class="{'active': isCuisineSelected(c)}"
                @click="toggleCuisine(c)">{{ c }}</view>
            </view>
            <input v-model="customCuisine" class="pref-input mt-10" placeholder="其他资源类型..." @confirm="addCustomCuisine"/>
          </view>

          <view class="pref-section">
            <text class="section-title">其他备注</text>
            <textarea v-model="preferences.custom_notes" class="pref-textarea" placeholder="告诉路径智能体更多你的学习目标、基础和困惑..." />
          </view>
        </view>
        <view class="modal-footer">
          <button class="save-pref-btn" @click="savePreferences">让路径智能体记住我的偏好</button>
        </view>
      </view>
    </view>

    <!-- 智能体面板 -->
      <view class="agent-card" :class="{ 'card-collapsed': isCollapsed }" @click.stop="">
      <!-- 面板头部 -->
      <view class="card-header" @click="togglePanel">
        <view class="header-main">
          <view class="avatar-group">
            <view class="avatar-glow"></view>
            <image src="../../static/niceexpert.png" mode="aspectFit" class="agent-img"></image>
          </view>
          <view class="header-text">
            <text class="agent-title">路径规划智能体</text>
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

      <!-- 对话内容区域 -->
      <view v-show="!isCollapsed" class="card-body">
        <scroll-view 
          class="chat-viewport" 
          scroll-y="true" 
          :scroll-into-view="scrollTop"
          scroll-with-animation
        >
          <!-- 欢迎消息 -->
          <view class="chat-bubble ai-bubble welcome-msg" id="msg-root">
            <text class="bubble-text">您好！我是路径规划智能体，负责为你整合学生画像和课程资源。\n\n我可以帮你：\n1. 根据学习目标规划课程路径\n2. 按知识基础、偏好和进度推荐资源\n3. 动态调整文档、题库、案例的学习顺序\n\n请在下方输入你的学习目标，或点击快捷标签快速开始：</text>
            <view class="quick-suggestions">
              <view class="sugg-tag" @click="quickMessage('帮我规划人工智能导论一周学习路径')">一周学习路径</view>
              <view class="sugg-tag" @click="quickMessage('我搜索算法基础薄弱，先学什么？')">搜索算法补弱</view>
              <view class="sugg-tag" @click="quickMessage('推荐适合项目实操的课程资源')">项目实操推荐</view>
              <view class="sugg-tag" @click="quickMessage('生成题库训练顺序')">题库训练顺序</view>
              <view class="sugg-tag" @click="quickMessage('文档、视频和案例应该怎么搭配学习？')">资源搭配建议</view>
            </view>
          </view>
          <block v-for="(msg, index) in chatHistory" :key="index">
            <view class="message-row" :class="msg.type">
              <!-- 头像区域 -->
              <view v-if="msg.type === 'expert'" class="message-avatar agent-avatar-wrap">
                <image src="../../static/niceexpert.png" mode="aspectFit" class="avatar-img"></image>
              </view>

              <!-- 内容区域 -->
              <view class="message-content-box">
                <view v-if="msg.type === 'expert' && msg.thinkingSteps && msg.thinkingSteps.length" class="thought-process">
                  <view class="thought-header" @click="toggleMsgThinking(index)">
                    <text class="thought-label">React 思考过程</text>
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
                    <view class="dot"></view>
                    <view class="dot"></view>
                    <view class="dot"></view>
                  </view>
                  <text v-else class="bubble-text">{{ msg.message }}</text>
                </view>
              </view>
            </view>
          </block>
          <view id="chat-bottom-anchor" style="height: 40rpx;"></view>
        </scroll-view>

        <!-- 输入区域 -->
        <view class="composition-area">
          <view class="input-wrapper">
            <input 
              type="text" 
              v-model="userMessage" 
              placeholder="输入学习目标或知识短板"
              class="neo-input"
              placeholder-class="input-placeholder"
              @confirm="sendMessage"
              @input="handleInput"
            />
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
      commonCuisines: ['课程讲解文档', '知识点思维导图', '分层练习题', '拓展阅读材料', '代码实操案例', '项目任务书', '短视频脚本', '动画分镜', '错题复盘', '考试冲刺清单', '论文阅读清单', '课堂演示材料'],
      commonHabits: ['图解优先', '案例驱动', '代码实操', '题库训练', '短视频讲解', '先易后难', '高频复盘', '项目导向', '考试导向', '研究拓展', '碎片化学习', '长时段深学'],
      customCuisine: ''
    }
  },
  mounted() {
    this.initConversation();
    this.loadPreferences();
    this.initVoiceInput();
  },
  beforeDestroy() {
    clearTimeout(this.inputDebounceTimer);
    if (this.voiceInputController) {
      this.voiceInputController.destroy();
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
    }
  }
}
</script>

<script lang="renderjs" module="amap">
export default {
  data() {
    return {
      map: null,
      geolocation: null,
      geocoder: null,
      currentLocationMarker: null,
      activeRecommendationMarkers: [],
      latestRecommendationMarkers: []
    }
  },
  mounted() {
    this.initAMap();
  },
  methods: {
    initAMap() {
      if (typeof window !== 'undefined' && typeof window.AMap !== 'undefined') {
        window.AMap.securityJsCode = '04a6a123aef949bd34c9cc703dd4278c';
        this.setupMap();
      } else {
        this.injectAMapScript();
      }
    },
    injectAMapScript() {
      if (typeof document === 'undefined') {
        this.$ownerInstance.callMethod('setMapStatus', 'error');
        return;
      }

      const existingScript = document.querySelector('script[data-amap-sdk="true"]');
      if (existingScript) {
        if (typeof window !== 'undefined' && typeof window.AMap !== 'undefined') {
          window.AMap.securityJsCode = '04a6a123aef949bd34c9cc703dd4278c';
          this.setupMap();
        }
        return;
      }

      const script = document.createElement('script');
      script.type = 'text/javascript';
      script.setAttribute('data-amap-sdk', 'true');
      script.src = 'https://webapi.amap.com/maps?v=2.0&key=abc8273ceb24e25547ba0ff4168f6133';
      script.onload = () => {
        console.log('Script Injection Success');
        if (typeof window !== 'undefined' && typeof window.AMap !== 'undefined') {
          window.AMap.securityJsCode = '04a6a123aef949bd34c9cc703dd4278c';
        }
        this.setupMap();
      };
      script.onerror = (e) => {
        console.error('Script Injection Failure', e);
        this.$ownerInstance.callMethod('setMapStatus', 'error');
      };
      document.head.appendChild(script);
    },
    setupMap() {
      try {
        if (typeof window === 'undefined' || typeof window.AMap === 'undefined') {
          this.$ownerInstance.callMethod('setMapStatus', 'error');
          return;
        }
        const container = document.getElementById('amap-container');
        if (!container) return;

        this.map = new window.AMap.Map('amap-container', {
          zoom: 16,
          center: [114.332928, 30.508522],
          viewMode: '3D',
        pitch: 35, // 倾斜角
          resizeEnable: true
        });

        this.map.on('complete', () => {
          this.$ownerInstance.callMethod('setMapStatus', 'loaded');
          this.loadPlugins();
          this.renderRecommendationMarkers();
        });
      } catch (err) {
        this.$ownerInstance.callMethod('setMapStatus', 'error');
      }
    },
    loadPlugins() {
      window.AMap.plugin(['AMap.Geolocation', 'AMap.Geocoder', 'AMap.CitySearch'], () => {
        this.geocoder = new window.AMap.Geocoder({
          city: '全国',
          radius: 1000
        });

        this.geolocation = new window.AMap.Geolocation({
          enableHighAccuracy: true,
          timeout: 10000,
          maximumAge: 0,
          buttonPosition: 'RB',
          buttonOffset: new window.AMap.Pixel(20, 20),
          zoomToAccuracy: false,
          showButton: false,
          showMarker: false,
          showCircle: false,
          circleOptions: { strokeOpacity: 0, fillOpacity: 0, fillAlpha: 0 },
          GeoLocationFirst: true
        });
        
        this.map.addControl(this.geolocation);

        setTimeout(() => {
          this.locateWithGeolocation();
        }, 500);
      });
    },
    locateWithGeolocation() {
      if (!this.map || !this.geolocation) {
        console.warn('AMap geolocation is not ready, trying browser geolocation');
        this.locateWithBrowserGeolocation('amap_not_ready');
        return;
      }

      console.log('开始高德定位');
      this.geolocation.getCurrentPosition((status, result) => {
        if (status === 'complete' && result && result.position) {
          const lng = result.position.lng;
          const lat = result.position.lat;
          console.log('高德定位成功:', { lng, lat, result });
          this.applyLocatedPosition(lng, lat, 'amap');
          return;
        }

        console.warn('Geolocation failed, waiting for manual location:', status, result);
        this.locateWithBrowserGeolocation('amap_geolocation_failed');
      });
    },
    locateWithBrowserGeolocation(reason = '') {
      if (typeof navigator === 'undefined' || !navigator.geolocation) {
        console.warn('浏览器原生定位不可用:', reason);
        this.handleLocationUnavailable(reason || 'browser_geolocation_unavailable');
        return;
      }

      console.log('开始浏览器原生定位:', reason);
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const lng = position.coords.longitude;
          const lat = position.coords.latitude;
          console.log('浏览器原生定位成功:', {
            lng,
            lat,
            accuracy: position.coords.accuracy,
            position
          });
          this.applyLocatedPosition(lng, lat, 'browser');
        },
        (error) => {
          console.warn('浏览器原生定位失败:', {
            reason,
            code: error && error.code,
            message: error && error.message,
            error
          });
          this.handleLocationUnavailable(reason || 'browser_geolocation_failed');
        },
        {
          enableHighAccuracy: true,
          timeout: 12000,
          maximumAge: 0
        }
      );
    },
    applyLocatedPosition(lng, lat, source = '') {
      const lngNum = Number(lng);
      const latNum = Number(lat);
      if (!Number.isFinite(lngNum) || !Number.isFinite(latNum)) {
        console.warn('定位坐标无效:', { lng, lat, source });
        this.handleLocationUnavailable(`${source}_invalid_coords`);
        return;
      }

      const lngLat = [lngNum, latNum];
      this.setCurrentLocationMarker(lngLat);
      this.$ownerInstance.callMethod('updateLocation', { lng: lngNum, lat: latNum });

      if (this.geocoder) {
        this.geocoder.getAddress(lngLat, (geoStatus, geoResult) => {
          console.log('定位反向解析结果:', { geoStatus, geoResult, source });
          if (
            geoStatus === 'complete' &&
            geoResult &&
            geoResult.regeocode &&
            geoResult.regeocode.formattedAddress
          ) {
            this.$ownerInstance.callMethod(
              'updateLocationName',
              geoResult.regeocode.formattedAddress
            );
          } else {
            this.$ownerInstance.callMethod('updateLocationName', '');
          }
        });
      } else {
        this.$ownerInstance.callMethod('updateLocationName', '');
      }

      if (this.map) {
        this.map.setZoomAndCenter(16, lngLat, false, 600);
      }
    },
    handleLocationUnavailable(reason = '') {
      console.warn('定位不可用:', reason);
      this.$ownerInstance.callMethod('updateLocationName', '');
      this.$ownerInstance.callMethod('updateLocation', null);

      if (this.currentLocationMarker) {
        this.map.remove(this.currentLocationMarker);
        this.currentLocationMarker = null;
      }

      if (reason) {
        uni.showToast({
          title: '定位暂不可用，路径智能体会根据你的问题继续推荐',
          icon: 'none',
          duration: 2200
        });
      }
    },
    setCurrentLocationMarker(lngLat) {
      if (!this.map || !Array.isArray(lngLat)) return;

      if (this.currentLocationMarker) {
        this.map.remove(this.currentLocationMarker);
        this.currentLocationMarker = null;
      }

      this.currentLocationMarker = new window.AMap.Marker({
        position: lngLat,
        title: '当前位置',
        zIndex: 999,
        anchor: 'center',
        offset: new window.AMap.Pixel(-10, -10),
        content:
          '<div style="width:20px;height:20px;border-radius:50%;background:#1677ff;border:3px solid #ffffff;box-shadow:0 0 0 8px rgba(22,119,255,0.18),0 4px 12px rgba(22,119,255,0.25);"></div>'
      });

      this.map.add(this.currentLocationMarker);
    },
    centerOnLibrary() {
      this.handleLocationUnavailable();
      return;

      this.$ownerInstance.callMethod('updateLocationName', '武汉理工大学南湖校区图书馆');
      this.$ownerInstance.callMethod('updateLocation', {
        lng: libLngLat[0],
        lat: libLngLat[1]
      });

      this.setCurrentLocationMarker(libLngLat);
      this.map.setZoomAndCenter(16, libLngLat, false, 600);
    },
    relocate() {
      this.locateWithGeolocation();
    },
    retryWithIP(reason = '') {
      if (this.isIPPositioning) return;
      this.isIPPositioning = true;
      
      console.log('Attempting IP-based Positioning (CitySearch)... Reason:', reason);
      if (typeof AMap.CitySearch === 'undefined') {
        console.error('CitySearch plugin not loaded');
        this.handleLocationUnavailable(reason);
        return;
      }

      const citySearch = new AMap.CitySearch();
      citySearch.getLocalCity((status, result) => {
        if (status === 'complete' && result.info === 'OK' && result.bounds) {
          console.log('IP Location Success:', result);
          const center = result.bounds.getCenter();
          const isNearWuhan = center.getLng() > 113.5 && center.getLng() < 115.0 &&
                              center.getLat() > 29.5 && center.getLat() < 31.5;

          if (isNearWuhan) {
            this.handleLocationUnavailable(reason);
            return;
          }
          
          if (isNearWuhan) {
            const city = result.city || '未知城市';
            this.$ownerInstance.callMethod('updateLocationName', city + ' (IP定位)');
            this.map.setBounds(result.bounds);
            this.map.setZoom(13);
            
            if (reason) {
              uni.showToast({
                title: '精确地理定位受限，已切换到城市定位',
                icon: 'none',
                duration: 2500
              });
            }
          } else {
            console.warn('IP location not near Wuhan, falling back to default');
            this.handleLocationUnavailable(reason);
          }
        } else {
          console.error('IP Location Failed:', result);
          this.handleLocationUnavailable(reason);
        }
      });
    },
    fallbackToDefault(reason = '') {
      this.handleLocationUnavailable(reason);
      return;
      this.$ownerInstance.callMethod('updateLocationName', '武汉理工大学南湖校区图书馆(默认定位)');
      this.$ownerInstance.callMethod('updateLocation', {
        lng: 114.332928,
        lat: 30.508522
      });
      this.setCurrentLocationMarker([114.332928, 30.508522]);
      this.map.setCenter([114.332928, 30.508522]);
      this.map.setZoom(16);

      if (reason) {
        uni.showToast({
          title: '已默认定位至武汉理工大学南湖校区图书馆',
          icon: 'none',
          duration: 2500
        });
      }
    },
    chooseLocation() {
      if (!this.geocoder) return;

      const defaultText = '武汉市洪山区武汉理工大学南湖校区';
      const input = typeof window !== 'undefined' && typeof window.prompt === 'function'
        ? window.prompt('请输入地址', defaultText)
        : '';

      if (!input) return;

      this.geocoder.getLocation(input, (status, result) => {
        if (status === 'complete' && result.geocodes.length > 0) {
          const location = result.geocodes[0].location;
          const address = result.geocodes[0].formattedAddress;

          this.map.setCenter(location);
          this.map.setZoom(17);
          this.$ownerInstance.callMethod('updateLocationName', address);
          this.$ownerInstance.callMethod('updateLocation', {
            lng: location.lng,
            lat: location.lat
          });
          this.setCurrentLocationMarker([location.lng, location.lat]);
        } else {
          console.warn('manual address geocode failed');
        }
      });
      return;
      
      uni.showModal({
        title: '手动选择位置',
        editable: true,
        placeholderText: '请输入地址，如：武汉市洪山区武汉理工大学南湖校区',
        success: (res) => {
          if (res.confirm && res.content) {
            this.geocoder.getLocation(res.content, (status, result) => {
              if (status === 'complete' && result.geocodes.length > 0) {
                const location = result.geocodes[0].location;
                const address = result.geocodes[0].formattedAddress;
                
                this.map.setCenter(location);
                this.map.setZoom(17);
                this.$ownerInstance.callMethod('updateLocationName', address);
                this.$ownerInstance.callMethod('updateLocation', {
                  lng: location.lng,
                  lat: location.lat
                });
                this.setCurrentLocationMarker([location.lng, location.lat]);
                
                uni.showToast({
                  title: '位置已更新',
                  icon: 'success'
                });
              } else {
                uni.showToast({
                  title: '地址解析失败',
                  icon: 'none'
                });
              }
            });
          }
        }
      });
    },
    zoomIn() { 
      if (!this.map) return;
      this.map.setZoom(this.map.getZoom() + 1); 
    },
    zoomOut() { 
      if (!this.map) return;
      this.map.setZoom(this.map.getZoom() - 1); 
    },
    clearRecommendationMarkers() {
      if (!this.map) return;
      
      // 清除集群
      if (this.markerClusterer) {
        if (typeof this.markerClusterer.clearMarkers === 'function') {
          this.markerClusterer.clearMarkers();
        }
        this.markerClusterer = null;
      }
      
      // 清除标记
      if (this.activeRecommendationMarkers.length) {
        this.map.remove(this.activeRecommendationMarkers);
        this.activeRecommendationMarkers = [];
      }
    },
    renderRecommendationMarkers() {
      if (!this.map) return;

      this.clearRecommendationMarkers();
      if (!Array.isArray(this.latestRecommendationMarkers) || !this.latestRecommendationMarkers.length) {
        return;
      }

      // 加载标记集群插件
      this.createSimpleMarkers();
    },
    createSimpleMarkers() {
      if (!this.map || typeof window === 'undefined' || typeof window.AMap === 'undefined') {
        return;
      }

      const markers = this.latestRecommendationMarkers
        .filter((poi) => poi && poi.location && Number.isFinite(poi.location.lng) && Number.isFinite(poi.location.lat))
        .map((poi, index) => {
          const marker = new window.AMap.Marker({
            position: [poi.location.lng, poi.location.lat],
            title: poi.name || `POI ${index + 1}`,
            anchor: 'center',
            offset: new window.AMap.Pixel(-14, -14),
            content: `<div style="display:flex;align-items:center;justify-content:center;width:28px;height:28px;border-radius:50%;background:#ff7a45;color:#fff;border:2px solid #fff;box-shadow:0 4px 12px rgba(255,122,69,0.35);font-size:12px;font-weight:700;">${index + 1}</div>`,
            zIndex: 100 + index
          });

          if (typeof marker.setLabel === 'function' && poi.name) {
            marker.setLabel({
              direction: 'top',
              offset: new window.AMap.Pixel(0, -10),
              content: `<div style="padding:2px 6px;background:#fff;border:1px solid #eee;border-radius:4px;font-size:12px;color:#333;white-space:nowrap;">${poi.name}</div>`
            });
          }

          return marker;
        });

      if (!markers.length) {
        return;
      }

      this.map.add(markers);
      this.activeRecommendationMarkers = markers;
    },
    createMarkersWithCluster() {
      const markers = this.latestRecommendationMarkers.map((poi, index) => {
        // 创建自定义标记样式
        const marker = new AMap.Marker({
          position: [poi.location.lng, poi.location.lat],
          title: poi.name,
          icon: new AMap.Icon({
            size: new AMap.Size(36, 48), // 图标尺寸
            image: 'https://webapi.amap.com/theme/v1.3/markers/n/mark_b.png', // 标记图标
            imageOffset: new AMap.Pixel(0, -60) // 图标偏移
          }),
          label: {
            content: `<div style="padding: 6px 12px; background: rgba(255, 255, 255, 0.95); border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.15); font-size: 12px; border: 1px solid #f0f0f0; font-weight: 500;">${poi.name}</div>`,
            direction: 'top',
            offset: new AMap.Pixel(0, -60) // 标签偏移，避免遮挡标记
          },
          zIndex: 100 + index // 设置不同的z-index，避免完全重叠
        });
        
        // 添加点击事件
        marker.on('click', () => {
          // 可以在这里添加点击标记的逻辑
          console.log('点击了标记', poi.name);
        });
        
        return marker;
      });

      // 使用标记集群器，避免标记相互遮挡
      this.markerClusterer = new AMap.MarkerClusterer(this.map, markers, {
        gridSize: 80, // 网格大小，单位像素
        maxZoom: 18, // 最大缩放级别
        zoomOnClick: false, // 点击集群时不自动缩放
        renderClusterMarker: (context) => {
          // 自定义集群标记样式
          const count = context.count;
          const size = count < 10 ? 40 : count < 100 ? 50 : 60;
          
          return new AMap.Marker({
            position: context.center,
            icon: new AMap.Icon({
              size: new AMap.Size(size, size),
              image: 'https://webapi.amap.com/theme/v1.3/markers/n/mark_r.png',
              imageOffset: new AMap.Pixel(0, 0)
            }),
            label: {
              content: `<div style="padding: 4px 8px; background: rgba(255, 87, 34, 0.9); color: white; border-radius: ${size/2}px; font-size: ${size > 50 ? 14 : 12}px; font-weight: bold; width: ${size}px; height: ${size}px; display: flex; align-items: center; justify-content: center;">${count}</div>`,
              direction: 'center',
              offset: new AMap.Pixel(0, 0)
            }
          });
        }
      });

      this.activeRecommendationMarkers = markers;
      
      // 不自动缩放地图，保持当前缩放比例
      // 移除 map.setFitView 调用，避免地图来回缩放
    },
    updateMarkers(newValue) {
      this.latestRecommendationMarkers = Array.isArray(newValue) ? newValue : [];
      this.renderRecommendationMarkers();
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
  background-color: #0c0d0e;
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
  border: 1px solid rgba(255,255,255,0.3);
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
  background: #fa8c16;
  border-radius: 50%;
  box-shadow: 0 0 10rpx #fa8c16;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { transform: scale(1); opacity: 1; }
  70% { transform: scale(2.5); opacity: 0; }
  100% { transform: scale(1); opacity: 0; }
}

.loc-name {
  font-size: 26rpx;
  color: #1a1a1a;
  font-weight: 500;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.loc-refresh {
  margin-left: 20rpx;
  font-size: 22rpx;
  color: #fa8c16;
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
  border-bottom: 1rpx solid #f0f0f0;
}

.modal-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
}

.close-icon {
  font-size: 40rpx;
  color: #999;
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
  color: #666;
  margin-bottom: 15rpx;
  display: block;
}

.pref-input {
  width: 100%;
  height: 80rpx;
  background: #f8f8f8;
  border-radius: 12rpx;
  padding: 0 20rpx;
  font-size: 26rpx;
  box-sizing: border-box;
}

.pref-textarea {
  width: 100%;
  height: 150rpx;
  background: #f8f8f8;
  border-radius: 12rpx;
  padding: 20rpx;
  font-size: 26rpx;
  box-sizing: border-box;
}

.mt-10 { margin-top: 10rpx; }

.tag-group {
  display: flex;
  flex-wrap: wrap;
  gap: 15rpx;
}

.tag-item {
  padding: 10rpx 25rpx;
  background: #f0f0f0;
  border-radius: 30rpx;
  font-size: 24rpx;
  color: #666;
  transition: all 0.2s;
}

.tag-item.active {
  background: #fa8c16;
  color: #fff;
}

.modal-footer {
  padding: 30rpx;
  border-top: 1rpx solid #f0f0f0;
}

.save-pref-btn {
  width: 100%;
  height: 88rpx;
  background: linear-gradient(135deg, #fa8c16, #ffa940);
  color: #fff;
  border-radius: 44rpx;
  font-size: 30rpx;
  font-weight: bold;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 智能体卡片 - 高端样式重构 */
.agent-card {
  position: fixed;
  bottom: calc(80rpx + env(safe-area-inset-bottom));
  left: 30rpx;
  right: 30rpx;
  background: #ffffff;
  border-radius: 40rpx;
  box-shadow: 0 16rpx 48rpx rgba(0,0,0,0.25), 0 0 0 1rpx rgba(250, 140, 22, 0.1);
  pointer-events: auto;
  transition: transform 0.4s cubic-bezier(0.23, 1, 0.32, 1);
  overflow: hidden;
  z-index: 350;
  display: block !important;
  border: 2rpx solid rgba(250, 140, 22, 0.08);
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
  background: linear-gradient(135deg, #ffffff 0%, #fafafa 100%);
  border-bottom: 1rpx solid rgba(250, 140, 22, 0.1);
  position: relative;
}

.card-header::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 40rpx;
  right: 40rpx;
  height: 2rpx;
  background: linear-gradient(90deg, transparent 0%, rgba(250, 140, 22, 0.3) 50%, transparent 100%);
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

.avatar-glow {
  position: absolute;
  top: -4rpx; left: -4rpx; right: -4rpx; bottom: -4rpx;
  background: linear-gradient(135deg, #fa8c16, #ffa940);
  border-radius: 50%;
  opacity: 0.3;
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
  color: #1f1f1f;
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
  background: #52c41a;
  border-radius: 50%;
  margin-right: 8rpx;
}

.badge-text {
  font-size: 20rpx;
  color: #8c8c8c;
  text-transform: uppercase;
  font-weight: 600;
}

.toggle-arrow {
  font-size: 40rpx;
  color: #bfbfbf;
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
  background: linear-gradient(180deg, #ffffff 0%, #fafafa 100%);
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
  background: linear-gradient(90deg, transparent 0%, rgba(250, 140, 22, 0.1) 50%, transparent 100%);
}

.chat-viewport::-webkit-scrollbar {
  width: 6rpx;
}

.chat-viewport::-webkit-scrollbar-track {
  background: transparent;
  border-radius: 3rpx;
}

.chat-viewport::-webkit-scrollbar-thumb {
  background: linear-gradient(to bottom, #fa8c16, #ff7a45);
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
  box-shadow: 0 4rpx 12rpx rgba(0,0,0,0.1), 0 0 0 1rpx rgba(250, 140, 22, 0.1);
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
  border: 1rpx solid rgba(250, 140, 22, 0.2);
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
  color: #1f1f1f;
  border: 1rpx solid rgba(24, 144, 255, 0.15) !important;
  border-radius: 32rpx 32rpx 32rpx 0 !important;
  box-shadow: 0 4rpx 16rpx rgba(24, 144, 255, 0.08) !important;
}

.user-bubble {
  background: linear-gradient(135deg, #fa8c16 0%, #ff7a45 100%) !important;
  color: white !important;
  align-self: flex-end;
  border-radius: 32rpx 32rpx 0 32rpx !important;
  box-shadow: 0 8rpx 24rpx rgba(250, 140, 22, 0.25) !important;
  margin-right: 0;
  border: 1rpx solid rgba(255,255,255,0.15);
  box-sizing: border-box;
  max-width: 100%;
}

.ai-bubble {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  color: #262626;
  align-self: flex-start;
  border-radius: 32rpx 32rpx 32rpx 0;
  box-shadow: 0 4rpx 20rpx rgba(24, 144, 255, 0.06);
  border: 1rpx solid rgba(24, 144, 255, 0.1);
}

.welcome-msg {
  background: linear-gradient(135deg, rgba(250, 140, 22, 0.08) 0%, rgba(255, 122, 69, 0.05) 100%);
  border: 1rpx solid rgba(250, 140, 22, 0.15);
  margin-top: 20rpx;
  box-shadow: 0 4rpx 16rpx rgba(250, 140, 22, 0.1), inset 0 1rpx 0 rgba(255,255,255,0.6);
  max-width: calc(100% - 80rpx);
  box-sizing: border-box;
}

.quick-suggestions {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
  margin-top: 28rpx;
}

.sugg-tag {
  background: linear-gradient(135deg, #ffffff 0%, #fafafa 100%);
  padding: 12rpx 24rpx;
  border-radius: 32rpx;
  font-size: 22rpx;
  color: #fa8c16;
  border: 1rpx solid rgba(250, 140, 22, 0.25);
  box-shadow: 0 2rpx 8rpx rgba(250, 140, 22, 0.1), inset 0 1rpx 0 rgba(255,255,255,0.8);
  transition: all 0.2s ease;
  cursor: pointer;
}

.sugg-tag:active {
  transform: scale(0.95);
  background: linear-gradient(135deg, #fa8c16 0%, #ff7a45 100%);
  color: white;
  border-color: #fa8c16;
  box-shadow: 0 4rpx 12rpx rgba(250, 140, 22, 0.3), inset 0 1rpx 0 rgba(255,255,255,0.3);
}

/* 思考过程*/
.thought-process {
  margin-bottom: 16rpx;
  background: linear-gradient(135deg, rgba(82, 196, 26, 0.06) 0%, rgba(82, 196, 26, 0.03) 100%);
  border-radius: 20rpx;
  padding: 16rpx 24rpx;
  width: 90%;
  border: 1rpx solid rgba(82, 196, 26, 0.15);
  box-shadow: 0 2rpx 12rpx rgba(82, 196, 26, 0.08), inset 0 1rpx 0 rgba(255,255,255,0.5);
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
  color: #595959; 
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8rpx;
}

.thought-label::before {
  content: '';
  width: 8rpx;
  height: 8rpx;
  background: #52c41a;
  border-radius: 50%;
  display: inline-block;
}

.thought-action { 
  font-size: 20rpx; 
  color: #52c41a;
  font-weight: 500;
  padding: 4rpx 12rpx;
  background: rgba(82, 196, 26, 0.1);
  border-radius: 16rpx;
  transition: all 0.2s ease;
}

.thought-action:active {
  background: rgba(82, 196, 26, 0.2);
  transform: scale(0.95);
}

.thought-detail {
  margin-top: 16rpx;
  border-top: 1px dashed rgba(82, 196, 26, 0.2);
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
  color: #52c41a;
  margin-top: 4rpx;
  flex-shrink: 0;
}

.step-text { 
  font-size: 22rpx; 
  color: #595959;
  line-height: 1.6;
  flex: 1;
}

/* 输入框*/
.composition-area {
  padding: 30rpx 2.5% 40rpx;
  background: linear-gradient(to top, #ffffff 0%, #fafafa 100%);
  border-top: 1rpx solid rgba(250, 140, 22, 0.08);
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
  background: linear-gradient(90deg, transparent 0%, rgba(250, 140, 22, 0.2) 50%, transparent 100%);
}

.input-wrapper {
  background: linear-gradient(135deg, #f5f5f7 0%, #f0f0f2 100%);
  border-radius: 48rpx;
  padding: 12rpx 12rpx 12rpx 40rpx;
  display: flex;
  align-items: center;
  border: 2rpx solid transparent;
  transition: all 0.3s ease;
  box-shadow: inset 0 2rpx 8rpx rgba(0,0,0,0.03), 0 2rpx 8rpx rgba(0,0,0,0.04);
}

.input-wrapper:focus-within {
  border-color: rgba(250, 140, 22, 0.4);
  background: #ffffff;
  box-shadow: 0 4rpx 16rpx rgba(250, 140, 22, 0.15), inset 0 2rpx 8rpx rgba(0,0,0,0.02);
}

.neo-input {
  flex: 1;
  height: 80rpx;
  font-size: 28rpx;
  color: #1f1f1f;
  background: transparent;
}

.voice-btn {
  min-width: 120rpx;
  height: 80rpx;
  margin-right: 12rpx;
  border-radius: 40rpx;
  background: #fff7e6;
  border: 1rpx solid rgba(250, 140, 22, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.voice-btn.active {
  background: linear-gradient(135deg, #fa8c16 0%, #ff7a45 100%);
  box-shadow: 0 6rpx 20rpx rgba(250, 140, 22, 0.25);
}

.voice-btn-text {
  font-size: 22rpx;
  color: #fa8c16;
  font-weight: 700;
}

.voice-btn.active .voice-btn-text {
  color: #fff;
}

.send-btn {
  width: 108rpx;
  height: 80rpx;
  background: linear-gradient(135deg, #d9d9d9 0%, #bfbfbf 100%);
  border-radius: 40rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s cubic-bezier(0.23, 1, 0.32, 1);
  box-shadow: 0 4rpx 12rpx rgba(0,0,0,0.1);
}

.send-btn.active {
  background: linear-gradient(135deg, #fa8c16 0%, #ff7a45 100%);
  box-shadow: 0 6rpx 20rpx rgba(250, 140, 22, 0.35);
  transform: scale(1.02);
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
  color: #434343;
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
  background: radial-gradient(circle, rgba(250, 140, 22, 0.15) 0%, transparent 70%);
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
  color: #1f1f1f;
  font-size: 48rpx;
  letter-spacing: -2rpx;
}

.ctrl-btn.relocate {
  background: #ffffff;
}

.ctrl-btn.relocate:active {
  background: #f0f0f0;
}

.ctrl-btn.relocate:active image {
  filter: brightness(0) invert(1);
}

.ctrl-btn.choose-loc {
  background: #ffffff;
}

.ctrl-btn.choose-loc:active {
  background: #f0f0f0;
}

.ctrl-btn.choose-loc:active image {
  filter: brightness(0) invert(1);
}

.ctrl-btn.preference-btn {
  background: #ffffff;
}

.ctrl-btn.preference-btn:active {
  background: #f0f0f0;
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
  border: 5rpx solid #f0f0f0;
  border-top-color: #fa8c16;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.status-tip {
  margin-top: 24rpx;
  font-size: 28rpx;
  color: #1f1f1f;
  font-weight: 500;
}

.status-subtip {
  margin-top: 12rpx;
  font-size: 24rpx;
  color: #8c8c8c;
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
  background: #fa8c16;
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
</style>
