<template>
  <view class="mc-page mc-light">
    <view class="mc-header" :style="{ paddingTop: statusBarHeight + 'px' }">
      <view class="mc-header-inner">
        <view class="mc-header-left" @click="goBack">
          <text class="mc-back-icon">←</text>
        </view>
        <view class="mc-header-center">
          <view class="mc-avatar-wrap">
            <image class="mc-avatar" src="../../static/openclaw.png" mode="aspectFill" />
            <view class="mc-status-dot" :class="{ 'mc-online': !isProcessing }"></view>
          </view>
          <view class="mc-header-info">
            <text class="mc-title">MiniClaw</text>
            <text class="mc-subtitle" v-if="!isProcessing">在线</text>
            <text class="mc-subtitle mc-thinking" v-else>思考中...</text>
          </view>
        </view>
        <view class="mc-header-right">
          <view class="mc-icon-btn" @click="clearConversation">
            <text class="mc-icon-btn-text">✕</text>
          </view>
          <view class="mc-icon-btn" @click="toggleSettings">
            <text class="mc-icon-btn-text">⚙</text>
          </view>
        </view>
      </view>
    </view>

    <scroll-view class="mc-chat" scroll-y="true" :scroll-into-view="scrollIntoView" :scroll-with-animation="true">
      <view class="mc-messages">
        <view class="mc-welcome" v-if="showWelcome">
          <image class="mc-welcome-avatar" src="../../static/openclaw.png" mode="aspectFill" />
          <text class="mc-welcome-title">你好，我是 MiniClaw</text>
          <text class="mc-welcome-desc">本系统的智能助手，可以为你提供健康饮食相关帮助</text>

          <view class="mc-shortcuts">
            <view class="mc-shortcut" v-for="(s, si) in shortcuts" :key="si" @click="insertQuickAction(s.prompt)">
              <text class="mc-shortcut-icon">{{ s.icon }}</text>
              <text class="mc-shortcut-text">{{ s.name }}</text>
            </view>
          </view>
        </view>

        <view v-for="(msg, i) in messages" :key="i" :id="'msg-' + i" class="mc-msg" :class="[msg.role, msg.isError ? 'mc-msg-error' : '']">
          <view class="mc-msg-avatar" v-if="msg.role === 'assistant'">
            <image class="mc-msg-avatar-img" src="../../static/openclaw.png" mode="aspectFill" />
          </view>
          <view class="mc-msg-body">
            <view class="mc-bubble" :class="{ 'mc-bubble-error': msg.isError }">
              <text class="mc-bubble-text">{{ msg.content }}</text>
            </view>
            <view class="mc-msg-footer">
              <text class="mc-msg-time">{{ formatTime(msg.timestamp) }}</text>
              <text class="mc-msg-copy" v-if="msg.role === 'assistant'" @click="copyMessage(msg.content)">复制</text>
              <text class="mc-msg-copy" v-if="msg.isError" @click="retryLastMessage">重试</text>
            </view>
          </view>
        </view>

        <view class="mc-typing" v-if="isTyping">
          <view class="mc-msg-avatar">
            <image class="mc-msg-avatar-img" src="../../static/openclaw.png" mode="aspectFill" />
          </view>
          <view class="mc-typing-bubble">
            <view class="mc-typing-dots">
              <view class="mc-dot"></view>
              <view class="mc-dot"></view>
              <view class="mc-dot"></view>
            </view>
          </view>
        </view>

        <view class="mc-scroll-bottom" id="scroll-bottom"></view>
      </view>
    </scroll-view>

    <view v-if="false" class="mc-input-bar mc-input-bar-disabled">
      <view class="mc-input-wrap">
        <textarea
          class="mc-input"
          v-model="inputMessage"
          placeholder="输入消息..."
          :auto-height="true"
          :maxlength="2000"
          :show-confirm-bar="false"
          :adjust-position="true"
          :disabled="isUnderDevelopment"
          @focus="handleDisabledInput"
          @blur="onInputBlur"
          @confirm="sendMessage"
        />
      </view>
      <view
        class="mc-voice"
        :class="{ 'mc-voice-active': isVoiceRecording || isVoiceTranscribing, 'mc-control-disabled': isUnderDevelopment }"
        @click="toggleVoiceInput"
      >
        <text class="mc-voice-text">{{ isVoiceRecording ? '停止' : (isVoiceTranscribing ? '识别中' : '语音') }}</text>
      </view>
      <view class="mc-send" :class="{ 'mc-send-active': inputMessage.trim() && !isProcessing && !isUnderDevelopment, 'mc-control-disabled': isUnderDevelopment }" @click="sendMessage">
        <text class="mc-send-icon" v-if="!isProcessing">↑</text>
        <view class="mc-spinner" v-else></view>
      </view>
    </view>
    <view class="mc-dev-banner">
      <text class="mc-dev-banner-text">开发中</text>
    </view>

    <view class="mc-mask" v-if="showSettings" @click="toggleSettings"></view>
    <view class="mc-settings" :class="{ 'mc-settings-show': showSettings }">
      <view class="mc-settings-bar"></view>
      <view class="mc-settings-head">
        <text class="mc-settings-title">设置</text>
      </view>
      <scroll-view scroll-y="true" class="mc-settings-body">
        <view class="mc-setting-group">
          <view class="mc-setting-item">
            <text class="mc-setting-label">AI 模型</text>
            <picker :value="modelIndex" :range="modelOptions" @change="onModelChange">
              <view class="mc-setting-picker">
                <text class="mc-setting-value">{{ modelOptions[modelIndex] }}</text>
                <text class="mc-setting-arrow">›</text>
              </view>
            </picker>
          </view>
          <view class="mc-setting-item">
            <text class="mc-setting-label">温度</text>
            <view class="mc-setting-slider">
              <slider class="mc-slider" :value="temperature" :min="0" :max="100" :step="10" @change="onTemperatureChange" :activeColor="'#dc2626'" :backgroundColor="'#e5e7eb'" blockSize="14" />
              <text class="mc-setting-num">{{ temperature / 100 }}</text>
            </view>
          </view>
          <view class="mc-setting-item">
            <text class="mc-setting-label">最大令牌数</text>
            <input class="mc-setting-input" type="number" v-model="maxTokens" placeholder="2048" />
          </view>
        </view>

        <view class="mc-setting-group">
          <text class="mc-setting-label">系统提示词</text>
          <textarea class="mc-setting-area" v-model="systemPrompt" placeholder="自定义系统提示词..." :auto-height="true" />
        </view>
      </scroll-view>
      <view class="mc-settings-foot">
        <view class="mc-save-btn" @click="saveSettings">
          <text class="mc-save-text">保存</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import request from '../../utils/request.js';
import { createVoiceInputController } from '../../utils/voice-input.js';

export default {
  data() {
    return {
      messages: [],
      inputMessage: '',
      isTyping: false,
      scrollIntoView: '',
      showSettings: false,
      isInputFocused: false,
      isVoiceRecording: false,
      isVoiceTranscribing: false,
      voiceInputController: null,
      modelIndex: 0,
      modelOptions: ['DeepSeek Chat', 'DeepSeek Reasoner'],
      modelIds: ['deepseek-chat', 'deepseek-reasoner'],
      temperature: 70,
      maxTokens: 2048,
      systemPrompt: '你是 MiniClaw，本系统的智能助手。你主要负责围绕健康饮食系统为用户提供帮助，包括健康管理、烹饪专家、外卖评估、餐厅推荐和用户中心等功能说明与建议。请优先从本系统的能力和场景出发回答问题。',
      config: null,
      statusBarHeight: 0,
      systemBarHeight: 0,
      conversationId: null,
      isProcessing: false,
      isUnderDevelopment: true,
      shortcuts: [
        { icon: '💬', name: '智能对话', prompt: '我们来聊聊天吧，介绍一下你自己' },
        { icon: '🧠', name: '知识问答', prompt: '帮我解答一些健康饮食方面的问题' },
        { icon: '📊', name: '数据分析', prompt: '帮我分析一下' },
        { icon: '📝', name: '内容总结', prompt: '请总结一下以下内容' },
        { icon: '💡', name: '智能建议', prompt: '给我一些建议' },
        { icon: '🍳', name: '健康食谱', prompt: '推荐一道健康食谱' }
      ]
    }
  },

  computed: {
    showWelcome() {
      return this.messages.length === 0 || (this.messages.length === 1 && this.messages[0].role === 'assistant');
    }
  },

  onLoad() {
    this.loadSettings();
    this.loadConfig();
    this.getSystemInfo();
    this.loadMessages();
    this.generateConversationId();
    this.initVoiceInput();
  },

  onReady() {
    this.setSystemInfo();
    this.scrollToBottom();
  },

  onUnload() {
    if (this.voiceInputController) {
      this.voiceInputController.destroy();
    }
    this.saveMessages();
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
          this.inputMessage = this.inputMessage.trim() ? `${this.inputMessage.trim()} ${text}` : text;
          uni.showToast({ title: '语音已转文字', icon: 'none' });
        },
        onError: (error) => {
          const title = (error?.message || '语音输入失败').slice(0, 20);
          uni.showToast({ title, icon: 'none' });
        }
      });
    },

    goBack() {
      uni.navigateBack({ delta: 1 });
    },



    generateConversationId() {
      const storedId = uni.getStorageSync('miniclaw_conversation_id');
      if (storedId) {
        this.conversationId = storedId;
      } else {
        this.conversationId = 'conv_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        uni.setStorageSync('miniclaw_conversation_id', this.conversationId);
      }
    },

    loadMessages() {
      try {
        const stored = uni.getStorageSync('miniclaw_messages_' + this.conversationId);
        if (stored && Array.isArray(stored) && stored.length > 0) {
          this.messages = stored;
        } else {
          this.addWelcomeMessage();
        }
      } catch (e) {
        this.addWelcomeMessage();
      }
    },

    saveMessages() {
      try {
        uni.setStorageSync('miniclaw_messages_' + this.conversationId, this.messages);
      } catch (e) {}
    },

    addWelcomeMessage() {
      this.messages.push({
        role: 'assistant',
        content: '你好！我是 MiniClaw，本系统的智能助手，可以结合健康管理、烹饪专家、外卖评估和餐厅推荐等功能为你提供帮助。',
        timestamp: new Date().toISOString()
      });
      this.saveMessages();
    },

    clearConversation() {
      uni.showModal({
        title: '清空对话',
        content: '确定要清空当前对话吗？',
        confirmColor: '#ff5c5c',
        success: (res) => {
          if (res.confirm) {
            this.messages = [];
            this.generateConversationId();
            this.addWelcomeMessage();
            this.scrollToBottom();
          }
        }
      });
    },

    getSystemInfo() {
      const info = uni.getSystemInfoSync();
      this.statusBarHeight = info.statusBarHeight || 0;
      this.systemBarHeight = info.safeAreaInsets?.bottom || 0;
    },

    setSystemInfo() {
      const info = uni.getSystemInfoSync();
      this.statusBarHeight = info.statusBarHeight || 0;
      this.systemBarHeight = info.safeAreaInsets?.bottom || 0;
    },

    async sendMessage() {
      if (this.isUnderDevelopment) {
        uni.showToast({ title: '开发中', icon: 'none' });
        return;
      }
      const text = this.inputMessage.trim();
      if (!text || this.isProcessing) return;
      if (text.length > 2000) {
        uni.showToast({ title: '消息过长', icon: 'none' });
        return;
      }

      this.messages.push({ role: 'user', content: text, timestamp: new Date().toISOString() });
      const userInput = text;
      this.inputMessage = '';
      this.isProcessing = true;
      this.isTyping = true;
      this.scrollToBottom();
      this.saveMessages();

      try {
        const response = await this.callOpenClawAPI(userInput);
        if (!response || typeof response !== 'string') throw new Error('无效响应');
        this.messages.push({ role: 'assistant', content: response, timestamp: new Date().toISOString() });
        this.saveMessages();
      } catch (error) {
        this.messages.push({
          role: 'assistant',
          content: '请求失败：' + (error.message || '请检查网络后重试'),
          timestamp: new Date().toISOString(),
          isError: true
        });
        this.saveMessages();
        uni.showToast({ title: '请求失败', icon: 'none' });
      } finally {
        this.isProcessing = false;
        this.isTyping = false;
        this.scrollToBottom();
      }
    },

    async callOpenClawAPI(message) {
      const response = await request.post('/openclaw/chat', {
        message: message,
        model: this.modelIds[this.modelIndex],
        temperature: this.temperature / 100,
        max_tokens: this.maxTokens,
        system_prompt: this.systemPrompt
      });
      if (response.code === 200 && response.data) return response.data.response;
      throw new Error(response.message || 'API 返回错误');
    },

    async loadConfig() {
      try {
        const response = await request.get('/openclaw/config');
        if (response.code === 200 && response.data) {
          this.config = response.data;
          this.maxTokens = response.data.max_tokens || 2048;
          this.temperature = (response.data.temperature || 0.7) * 100;
          this.systemPrompt = response.data.system_prompt || this.systemPrompt;
          const idx = this.modelIds.indexOf(response.data.default_model || 'deepseek-chat');
          if (idx !== -1) this.modelIndex = idx;
        }
      } catch (e) {}
    },

    async saveConfig() {
      try {
        await request.put('/openclaw/config', {
          default_model: this.modelIds[this.modelIndex],
          max_tokens: this.maxTokens,
          temperature: this.temperature / 100,
          system_prompt: this.systemPrompt
        });
        uni.showToast({ title: '已保存', icon: 'success' });
      } catch (e) {
        uni.showToast({ title: '保存失败', icon: 'none' });
      }
    },

    scrollToBottom() {
      this.$nextTick(() => { setTimeout(() => { this.scrollIntoView = 'scroll-bottom'; }, 100); });
    },

    retryLastMessage() {
      if (this.messages.length < 2) return;
      const last = this.messages[this.messages.length - 1];
      if (last.role === 'assistant' && last.isError) {
        this.messages.pop();
        const prev = this.messages[this.messages.length - 1];
        if (prev && prev.role === 'user') {
          this.inputMessage = prev.content;
          this.saveMessages();
        }
      }
    },

    copyMessage(content) {
      uni.setClipboardData({ data: content, success: () => { uni.showToast({ title: '已复制', icon: 'success', duration: 1000 }); } });
    },

    formatTime(timestamp) {
      const diff = Date.now() - new Date(timestamp).getTime();
      const m = 60000, h = 3600000, d = 86400000;
      if (diff < m) return '刚刚';
      if (diff < h) return Math.floor(diff / m) + '分钟前';
      if (diff < d) return Math.floor(diff / h) + '小时前';
      return new Date(timestamp).toLocaleDateString('zh-CN');
    },

    onInputBlur() {
      setTimeout(() => { this.isInputFocused = false; }, 200);
    },

    handleDisabledInput() {
      if (this.isUnderDevelopment) {
        uni.showToast({ title: '开发中', icon: 'none' });
        return;
      }
      this.isInputFocused = true;
    },

    async toggleVoiceInput() {
      if (this.isUnderDevelopment) {
        uni.showToast({ title: '开发中', icon: 'none' });
        return;
      }
      this.initVoiceInput();

      try {
        await this.voiceInputController.toggleRecording();
      } catch (error) {
        const title = (error?.message || '语音输入失败').slice(0, 20);
        uni.showToast({ title, icon: 'none' });
      }
    },

    toggleSettings() {
      this.showSettings = !this.showSettings;
    },

    onModelChange(e) { this.modelIndex = e.detail.value; },
    onTemperatureChange(e) { this.temperature = e.detail.value; },

    insertQuickAction(action) {
      if (this.isUnderDevelopment) {
        uni.showToast({ title: '开发中', icon: 'none' });
        return;
      }
      this.inputMessage = action;
    },

    async saveSettings() {
      await this.saveConfig();
      this.saveLocalSettings();
      this.showSettings = false;
    },

    saveLocalSettings() {
      uni.setStorageSync('miniclaw_settings', {
        modelIndex: this.modelIndex,
        temperature: this.temperature,
        maxTokens: this.maxTokens,
        systemPrompt: this.systemPrompt
      });
    },

    loadSettings() {
      const s = uni.getStorageSync('miniclaw_settings');
      if (s) {
        this.modelIndex = s.modelIndex || 0;
        this.temperature = s.temperature || 70;
        this.maxTokens = s.maxTokens || 2048;
        this.systemPrompt = s.systemPrompt || this.systemPrompt;
      }
    }
  }
}
</script>

<style scoped>
.mc-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
  transition: background 0.3s ease;
}

/* ===== Light ===== */
.mc-light { background: #f8f9fa; }
.mc-light .mc-header { background: #fff; border-bottom: 1rpx solid #f0f0f0; }
.mc-light .mc-back-icon { color: #64748b; }
.mc-light .mc-title { color: #0f172a; }
.mc-light .mc-subtitle { color: #94a3b8; }
.mc-light .mc-subtitle.mc-thinking { color: #dc2626; }
.mc-light .mc-icon-btn { background: #f1f5f9; }
.mc-light .mc-icon-btn-text { color: #64748b; }
.mc-light .mc-chat { background: #f8f9fa; }
.mc-light .mc-welcome-title { color: #0f172a; }
.mc-light .mc-welcome-desc { color: #94a3b8; }
.mc-light .mc-shortcut { background: #fff; border: 1rpx solid #e5e7eb; }
.mc-light .mc-shortcut:active { background: #f9fafb; border-color: #d1d5db; }
.mc-light .mc-shortcut-text { color: #475569; }
.mc-light .mc-bubble { background: #fff; border: 1rpx solid #e5e7eb; }
.mc-light .mc-msg.user .mc-bubble { background: rgba(220,38,38,0.06); border-color: rgba(220,38,38,0.18); }
.mc-light .mc-bubble-text { color: #334155; }
.mc-light .mc-msg-time { color: #cbd5e1; }
.mc-light .mc-msg-copy { color: #94a3b8; }
.mc-light .mc-msg-copy:active { color: #dc2626; }
.mc-light .mc-typing-bubble { background: #fff; border: 1rpx solid #e5e7eb; }
.mc-light .mc-dot { background: #dc2626; }
.mc-light .mc-bubble-error { background: #fef2f2; border-color: #fecaca; }
.mc-light .mc-input-bar { background: #fff; border-top: 1rpx solid #f0f0f0; }
.mc-light .mc-input-wrap { background: #f1f5f9; border: 1rpx solid #e5e7eb; }
.mc-light .mc-input-wrap.mc-input-focused { border-color: #dc2626; }
.mc-light .mc-input { color: #0f172a; }
.mc-light .mc-voice { background: #f1f5f9; border: 1rpx solid #e5e7eb; }
.mc-light .mc-voice-text { color: #dc2626; }
.mc-light .mc-voice-active { background: #fee2e2; border-color: #fca5a5; }
.mc-light .mc-send { background: #e5e7eb; }
.mc-light .mc-send-active { background: #dc2626; box-shadow: 0 2rpx 12rpx rgba(220,38,38,0.25); }
.mc-light .mc-dev-banner { background: #fff7ed; border-top: 1rpx solid #fed7aa; }
.mc-light .mc-dev-banner-text { color: #c2410c; }
.mc-light .mc-settings { background: #f8f9fa; }
.mc-light .mc-settings-bar { background: #cbd5e1; }
.mc-light .mc-settings-title { color: #0f172a; }
.mc-light .mc-setting-group { background: #fff; border: 1rpx solid #e5e7eb; }
.mc-light .mc-setting-label { color: #334155; }
.mc-light .mc-setting-picker { background: #f1f5f9; }
.mc-light .mc-setting-value { color: #dc2626; }
.mc-light .mc-setting-arrow { color: #94a3b8; }
.mc-light .mc-setting-num { color: #dc2626; }
.mc-light .mc-setting-input { color: #334155; background: #f1f5f9; }
.mc-light .mc-setting-area { color: #334155; background: #f1f5f9; }
.mc-light .mc-save-btn { background: #dc2626; }

/* ===== Header ===== */
.mc-header { flex-shrink: 0; transition: background 0.3s ease; }
.mc-header-inner { display: flex; align-items: center; justify-content: space-between; padding: 0 24rpx; height: 96rpx; }
.mc-header-left { width: 72rpx; }
.mc-back-icon { font-size: 36rpx; font-weight: 300; line-height: 1; }
.mc-header-center { flex: 1; display: flex; align-items: center; gap: 14rpx; justify-content: center; }
.mc-avatar-wrap { position: relative; }
.mc-avatar { width: 44rpx; height: 44rpx; border-radius: 50%; }
.mc-status-dot { position: absolute; bottom: 0; right: 0; width: 14rpx; height: 14rpx; border-radius: 50%; background: #3f3f46; border: 2rpx solid #161820; transition: all 0.3s; }
.mc-light .mc-status-dot { border-color: #fff; }
.mc-status-dot.mc-online { background: #22c55e; box-shadow: 0 0 6rpx rgba(34,197,94,0.5); }
.mc-header-info { display: flex; flex-direction: column; gap: 2rpx; }
.mc-title { font-size: 28rpx; font-weight: 700; letter-spacing: 0.5rpx; transition: color 0.3s; }
.mc-subtitle { font-size: 20rpx; transition: color 0.3s; }
.mc-subtitle.mc-thinking { animation: pulse 1.5s ease-in-out infinite; }
@keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.4; } }
.mc-header-right { display: flex; gap: 10rpx; width: 140rpx; justify-content: flex-end; }
.mc-icon-btn { width: 56rpx; height: 56rpx; border-radius: 50%; display: flex; align-items: center; justify-content: center; transition: all 0.2s; }
.mc-icon-btn:active { transform: scale(0.9); }
.mc-icon-btn-text { font-size: 22rpx; }

/* ===== Chat ===== */
.mc-chat { flex: 1; min-height: 0; transition: background 0.3s; }
.mc-messages { padding: 20rpx 24rpx; display: flex; flex-direction: column; gap: 20rpx; }

/* ===== Welcome ===== */
.mc-welcome { display: flex; flex-direction: column; align-items: center; padding: 48rpx 16rpx 24rpx; animation: fadeUp 0.4s ease; }
@keyframes fadeUp { from { opacity: 0; transform: translateY(16rpx); } to { opacity: 1; transform: translateY(0); } }
.mc-welcome-avatar { width: 100rpx; height: 100rpx; border-radius: 50%; margin-bottom: 24rpx; }
.mc-welcome-title { font-size: 34rpx; font-weight: 700; margin-bottom: 8rpx; transition: color 0.3s; }
.mc-welcome-desc { font-size: 24rpx; margin-bottom: 36rpx; transition: color 0.3s; }
.mc-shortcuts { display: flex; flex-wrap: wrap; gap: 16rpx; justify-content: center; }
.mc-shortcut { display: flex; align-items: center; gap: 10rpx; padding: 18rpx 24rpx; border-radius: 40rpx; transition: all 0.2s; }
.mc-shortcut:active { transform: scale(0.95); }
.mc-shortcut-icon { font-size: 28rpx; }
.mc-shortcut-text { font-size: 24rpx; font-weight: 500; transition: color 0.3s; }

/* ===== Messages ===== */
.mc-msg { display: flex; gap: 14rpx; animation: fadeUp 0.25s ease; }
.mc-msg.user { flex-direction: row-reverse; }
.mc-msg-error { animation: shake 0.35s ease; }
@keyframes shake { 0%,100% { transform: translateX(0); } 25% { transform: translateX(-6rpx); } 75% { transform: translateX(6rpx); } }
.mc-msg-avatar { width: 52rpx; height: 52rpx; border-radius: 14rpx; overflow: hidden; flex-shrink: 0; margin-top: 2rpx; }
.mc-msg-avatar-img { width: 100%; height: 100%; }
.mc-msg-body { max-width: 82%; display: flex; flex-direction: column; }
.mc-bubble { border-radius: 18rpx 18rpx 18rpx 4rpx; padding: 20rpx 24rpx; transition: all 0.2s; }
.mc-msg.user .mc-bubble { border-radius: 18rpx 18rpx 4rpx 18rpx; }
.mc-bubble-text { font-size: 27rpx; line-height: 1.7; word-wrap: break-word; white-space: pre-wrap; transition: color 0.3s; }
.mc-msg-footer { display: flex; align-items: center; gap: 14rpx; margin-top: 6rpx; padding: 0 6rpx; }
.mc-msg.user .mc-msg-footer { justify-content: flex-end; }
.mc-msg-time { font-size: 20rpx; transition: color 0.3s; }
.mc-msg-copy { font-size: 20rpx; padding: 2rpx 6rpx; border-radius: 6rpx; transition: color 0.2s; }

/* ===== Typing ===== */
.mc-typing { display: flex; align-items: flex-start; gap: 14rpx; animation: fadeUp 0.2s ease; }
.mc-typing-bubble { border-radius: 18rpx 18rpx 18rpx 4rpx; padding: 18rpx 24rpx; transition: all 0.2s; }
.mc-typing-dots { display: flex; gap: 6rpx; align-items: center; }
.mc-dot { width: 10rpx; height: 10rpx; border-radius: 50%; animation: bounce 1.4s infinite ease-in-out both; transition: background 0.3s; }
.mc-dot:nth-child(1) { animation-delay: -0.32s; }
.mc-dot:nth-child(2) { animation-delay: -0.16s; }
@keyframes bounce { 0%,80%,100% { transform: scale(0.4); opacity: 0.4; } 40% { transform: scale(1); opacity: 1; } }
.mc-scroll-bottom { height: 1rpx; }

/* ===== Input ===== */
.mc-input-bar { display: flex; align-items: flex-end; gap: 14rpx; padding: 14rpx 24rpx; padding-bottom: calc(14rpx + env(safe-area-inset-bottom)); flex-shrink: 0; transition: all 0.3s; }
.mc-input-bar-disabled { padding-bottom: 12rpx; }
.mc-input-wrap { flex: 1; border-radius: 22rpx; padding: 4rpx; transition: all 0.2s; }
.mc-input-wrap.mc-input-focused { box-shadow: 0 0 0 3rpx rgba(255,92,92,0.1); }
.mc-input { font-size: 27rpx; min-height: 68rpx; max-height: 220rpx; line-height: 1.5; padding: 14rpx 18rpx; transition: color 0.3s; }
.mc-voice { min-width: 92rpx; height: 68rpx; padding: 0 18rpx; border-radius: 20rpx; display: flex; align-items: center; justify-content: center; flex-shrink: 0; transition: all 0.2s; background: #f1f5f9; border: 1rpx solid #e5e7eb; }
.mc-voice-text { font-size: 22rpx; font-weight: 600; }
.mc-voice-active { transform: scale(0.98); }
.mc-send { width: 68rpx; height: 68rpx; border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-shrink: 0; transition: all 0.2s; }
.mc-send:active { transform: scale(0.9); }
.mc-control-disabled { opacity: 0.55; }
.mc-send-icon { font-size: 30rpx; color: #fff; font-weight: 600; line-height: 1; }
.mc-spinner { width: 28rpx; height: 28rpx; border: 3rpx solid rgba(255,255,255,0.3); border-top-color: #fff; border-radius: 50%; animation: spin 0.7s linear infinite; }
.mc-dev-banner { display: flex; align-items: center; justify-content: center; padding: 24rpx 24rpx calc(24rpx + env(safe-area-inset-bottom)); }
.mc-dev-banner-text { font-size: 24rpx; font-weight: 600; letter-spacing: 2rpx; }
@keyframes spin { to { transform: rotate(360deg); } }

/* ===== Settings ===== */
.mc-mask { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); backdrop-filter: blur(4px); z-index: 100; animation: fadeIn 0.2s; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
.mc-settings { position: fixed; bottom: 0; left: 0; right: 0; border-radius: 32rpx 32rpx 0 0; z-index: 101; transform: translateY(100%); transition: transform 0.35s cubic-bezier(0.32,0.72,0,1); max-height: 80vh; display: flex; flex-direction: column; }
.mc-settings-show { transform: translateY(0); }
.mc-settings-bar { width: 48rpx; height: 6rpx; border-radius: 3rpx; margin: 14rpx auto 0; transition: background 0.3s; }
.mc-settings-head { display: flex; align-items: center; justify-content: space-between; padding: 20rpx 28rpx 14rpx; }
.mc-settings-title { font-size: 30rpx; font-weight: 700; transition: color 0.3s; }
.mc-icon-btn-sm { width: 48rpx; height: 48rpx; border-radius: 50%; display: flex; align-items: center; justify-content: center; transition: all 0.2s; }
.mc-icon-btn-sm:active { transform: scale(0.9); }
.mc-settings-body { flex: 1; overflow-y: auto; padding: 14rpx 24rpx; display: flex; flex-direction: column; gap: 20rpx; }
.mc-setting-group { border-radius: 18rpx; padding: 20rpx; display: flex; flex-direction: column; gap: 18rpx; transition: all 0.2s; }
.mc-setting-item { display: flex; align-items: center; justify-content: space-between; gap: 16rpx; }
.mc-setting-label { font-size: 26rpx; font-weight: 500; transition: color 0.3s; }
.mc-setting-picker { display: flex; align-items: center; gap: 6rpx; padding: 10rpx 16rpx; border-radius: 10rpx; transition: all 0.2s; }
.mc-setting-value { font-size: 24rpx; font-weight: 500; transition: color 0.3s; }
.mc-setting-arrow { font-size: 22rpx; transition: color 0.3s; }
.mc-setting-slider { display: flex; align-items: center; gap: 14rpx; flex: 1; max-width: 320rpx; }
.mc-slider { flex: 1; }
.mc-setting-num { font-size: 24rpx; font-weight: 600; width: 50rpx; text-align: right; transition: color 0.3s; }
.mc-setting-input { font-size: 24rpx; border-radius: 10rpx; padding: 10rpx 16rpx; text-align: right; width: 180rpx; transition: all 0.2s; }
.mc-setting-area { font-size: 24rpx; border-radius: 10rpx; padding: 16rpx; min-height: 120rpx; line-height: 1.6; width: 100%; box-sizing: border-box; transition: all 0.2s; }
.mc-switch { width: 80rpx; height: 40rpx; border-radius: 20rpx; position: relative; transition: background 0.3s; padding: 3rpx; }
.mc-switch-thumb { width: 34rpx; height: 34rpx; border-radius: 50%; background: #fff; box-shadow: 0 1rpx 4rpx rgba(0,0,0,0.15); transition: transform 0.3s cubic-bezier(0.34,1.56,0.64,1); }
.mc-switch-on .mc-switch-thumb { transform: translateX(40rpx); }
.mc-settings-foot { padding: 14rpx 24rpx; padding-bottom: calc(14rpx + env(safe-area-inset-bottom)); }
.mc-save-btn { border-radius: 18rpx; padding: 22rpx 0; display: flex; align-items: center; justify-content: center; transition: all 0.2s; }
.mc-save-btn:active { transform: scale(0.97); }
.mc-save-text { font-size: 27rpx; color: #fff; font-weight: 600; }
</style>
