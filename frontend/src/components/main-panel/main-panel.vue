<template>
  <view 
    class="main-panel"
    :class="{ 
      'main-panel-expanded': isExpanded,
      'main-panel-collapsed': !isExpanded
    }"
    v-if="isExpanded"
  >
    <view class="panel-header">
      <view class="panel-title">
        <text class="title-icon">🤖</text>
        <text class="title-text">智能助手</text>
      </view>
      <view class="panel-actions">
        <view class="action-btn" @click="toggleInputMode">
          <text class="action-icon">{{ inputMode === 'text' ? '📝' : '🎤' }}</text>
        </view>
        <view class="action-btn" @click="collapse">
          <text class="action-icon">�?/text>
        </view>
      </view>
    </view>
    
    <view class="panel-content">
      <view class="module-grid">
        <view 
          class="module-card"
          :class="{ 'module-card-active': activeModule === 'cooking' }"
          @click="selectModule('cooking')"
        >
          <view class="module-icon cooking-icon">👨‍�?/view>
          <view class="module-info">
            <text class="module-title">厨艺辅助</text>
            <text class="module-desc">菜谱指导 · 食材识别 · 语音助手</text>
          </view>
          <view class="module-arrow">�?/view>
        </view>
        
        <view 
          class="module-card"
          :class="{ 'module-card-active': activeModule === 'food' }"
          @click="selectModule('food')"
        >
          <view class="module-icon food-icon">🗺�?/view>
          <view class="module-info">
            <text class="module-title">美食推荐</text>
            <text class="module-desc">附近美食 · 路线导航 · 用户评价</text>
          </view>
          <view class="module-arrow">�?/view>
        </view>
        
        <view 
          class="module-card"
          :class="{ 'module-card-active': activeModule === 'takeout' }"
          @click="selectModule('takeout')"
        >
          <view class="module-icon takeout-icon">🍱</view>
          <view class="module-info">
            <text class="module-title">外卖评估</text>
            <text class="module-desc">营养分析 · 健康评分 · 替代方案</text>
          </view>
          <view class="module-arrow">�?/view>
        </view>
        
        <view 
          class="module-card"
          :class="{ 'module-card-active': activeModule === 'health' }"
          @click="selectModule('health')"
        >
          <view class="module-icon health-icon">💊</view>
          <view class="module-info">
            <text class="module-title">健康管理</text>
            <text class="module-desc">数据仪表�?· 目标设定 · 健康报告</text>
          </view>
          <view class="module-arrow">�?/view>
        </view>
        
        <view 
          class="module-card settings-card"
          @click="openSettings"
        >
          <view class="module-icon settings-icon">⚙️</view>
          <view class="module-info">
            <text class="module-title">设置</text>
            <text class="module-desc">个性化配置 · 偏好设置</text>
          </view>
          <view class="module-arrow">�?/view>
        </view>
      </view>
      
      <view class="input-section" v-if="showInput">
        <view class="input-wrapper" :class="{ 'input-voice-mode': inputMode === 'voice' }">
          <view class="input-icon">
            {{ inputMode === 'text' ? '📝' : '🎤' }}
          </view>
          <input 
            v-if="inputMode === 'text'"
            type="text"
            v-model="inputText"
            placeholder="输入指令或问�?.."
            class="text-input"
            @confirm="sendInput"
          />
          <view v-else class="voice-input">
            <view class="voice-wave" v-if="isRecording">
              <view class="wave-bar"></view>
              <view class="wave-bar"></view>
              <view class="wave-bar"></view>
              <view class="wave-bar"></view>
              <view class="wave-bar"></view>
            </view>
            <text v-else class="voice-hint">点击开始语音输�?/text>
          </view>
          <view class="input-actions">
            <view class="action-btn-small" @click="clearInput">
              <text class="action-icon-small">�?/text>
            </view>
            <view class="action-btn-small send-btn" @click="sendInput">
              <text class="action-icon-small">�?/text>
            </view>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import { createVoiceInputController } from '../../utils/voice-input.js'

export default {
  name: 'MainPanel',
  props: {
    isExpanded: {
      type: Boolean,
      default: false
    },
    defaultModule: {
      type: String,
      default: ''
    }
  },
  data() {
    return {
      activeModule: this.defaultModule,
      inputMode: 'text',
      inputText: '',
      isRecording: false,
      isTranscribing: false,
      voiceInputController: null,
      showInput: false
    }
  },
  watch: {
    isExpanded(newVal) {
      if (newVal) {
        this.showInput = true
      }
    }
  },
  beforeDestroy() {
    if (this.voiceInputController) {
      this.voiceInputController.destroy()
    }
  },
  methods: {
    initVoiceInput() {
      if (this.voiceInputController) return

      this.voiceInputController = createVoiceInputController({
        service: 'tuantuan',
        onStateChange: ({ isRecording, isTranscribing }) => {
          this.isRecording = isRecording
          this.isTranscribing = isTranscribing
        },
        onTranscribed: (text) => {
          this.inputText = this.inputText.trim() ? `${this.inputText.trim()} ${text}` : text
          this.inputMode = 'text'
          uni.showToast({ title: 'Voice converted', icon: 'none' })
        },
        onError: (error) => {
          const title = (error?.message || 'Voice input failed').slice(0, 20)
          uni.showToast({ title, icon: 'none' })
        }
      })
    },
    collapse() {
      this.$emit('collapse')
    },
    
    selectModule(module) {
      this.activeModule = module
      this.$emit('select-module', module)
      
      uni.vibrateShort({
        success: () => {},
        fail: () => {}
      })
    },
    
    openSettings() {
      this.$emit('open-settings')
    },
    
    async toggleInputMode() {
      if (this.inputMode === 'voice' && (this.isRecording || this.isTranscribing)) {
        await this.toggleVoiceRecording()
        return
      }

      this.inputMode = this.inputMode === 'text' ? 'voice' : 'text'
      this.$emit('input-mode-change', this.inputMode)
      
      if (this.inputMode === 'voice') {
        await this.toggleVoiceRecording()
      }
    },
    async toggleVoiceRecording() {
      this.initVoiceInput()

      try {
        if (this.isRecording) {
          this.$emit('voice-stop')
        } else {
          this.$emit('voice-start')
        }
        await this.voiceInputController.toggleRecording()
      } catch (error) {
        const title = (error?.message || 'Voice input failed').slice(0, 20)
        uni.showToast({ title, icon: 'none' })
        this.inputMode = 'text'
      }
    },
    sendInput() {
      if (this.inputMode === 'voice') {
        this.toggleVoiceRecording()
        return
      }

      if (!this.inputText.trim()) {
        return
      }
      
      const message = this.inputText
      
      this.$emit('send-message', {
        mode: 'text',
        message: message
      })
      
      this.inputText = ''
      this.showInput = false
      
      uni.vibrateShort({
        success: () => {},
        fail: () => {}
      })
    },
    
    clearInput() {
      this.inputText = ''
      this.$emit('clear-input')
    }
  }
}
</script>

<style scoped>
.main-panel {
  position: fixed;
  z-index: 9998;
  background: white;
  border-radius: 32rpx;
  box-shadow: 0 16rpx 48rpx rgba(0, 0, 0, 0.15);
  overflow: hidden;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.main-panel-expanded {
  width: 680rpx;
  max-height: 80vh;
}

.main-panel-collapsed {
  width: 0;
  height: 0;
  opacity: 0;
  pointer-events: none;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 32rpx;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-bottom: 1rpx solid #e2e8f0;
}

.panel-title {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.title-icon {
  font-size: 36rpx;
}

.title-text {
  font-size: 32rpx;
  font-weight: 700;
  color: #1e293b;
}

.panel-actions {
  display: flex;
  gap: 16rpx;
}

.action-btn {
  width: 64rpx;
  height: 64rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  border-radius: 16rpx;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.06);
  transition: all 0.2s;
}

.action-btn:active {
  transform: scale(0.95);
  background: #f8fafc;
}

.action-icon {
  font-size: 32rpx;
}

.panel-content {
  padding: 32rpx;
  max-height: calc(80vh - 120rpx);
  overflow-y: auto;
}

.module-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 20rpx;
}

.module-card {
  display: flex;
  align-items: center;
  gap: 20rpx;
  padding: 24rpx;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-radius: 24rpx;
  border: 2rpx solid transparent;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
}

.module-card:active {
  transform: scale(0.98);
}

.module-card-active {
  background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%);
  border-color: #3b82f6;
  box-shadow: 0 4rpx 16rpx rgba(59, 130, 246, 0.2);
}

.module-icon {
  width: 88rpx;
  height: 88rpx;
  border-radius: 20rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 44rpx;
  flex-shrink: 0;
}

.cooking-icon {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
}

.food-icon {
  background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
}

.takeout-icon {
  background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%);
}

.health-icon {
  background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%);
}

.settings-icon {
  background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
}

.module-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}

.module-title {
  font-size: 28rpx;
  font-weight: 700;
  color: #1e293b;
}

.module-desc {
  font-size: 22rpx;
  color: #64748b;
  line-height: 1.4;
}

.module-arrow {
  font-size: 32rpx;
  color: #94a3b8;
  transition: all 0.3s;
}

.module-card-active .module-arrow {
  color: #3b82f6;
  transform: translateX(8rpx);
}

.input-section {
  margin-top: 32rpx;
  padding-top: 32rpx;
  border-top: 1rpx solid #e2e8f0;
}

.input-wrapper {
  display: flex;
  align-items: center;
  gap: 16rpx;
  background: #f8fafc;
  border-radius: 48rpx;
  padding: 8rpx 8rpx 8rpx 24rpx;
  border: 2rpx solid #e2e8f0;
  transition: all 0.3s;
}

.input-wrapper:focus-within {
  border-color: #3b82f6;
  background: white;
  box-shadow: 0 0 0 4rpx rgba(59, 130, 246, 0.1);
}

.input-icon {
  font-size: 32rpx;
  width: 48rpx;
  text-align: center;
}

.text-input {
  flex: 1;
  height: 72rpx;
  font-size: 26rpx;
  color: #1e293b;
  background: transparent;
  border: none;
  outline: none;
}

.text-input::placeholder {
  color: #94a3b8;
}

.voice-input {
  flex: 1;
  height: 72rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.voice-wave {
  display: flex;
  align-items: center;
  gap: 4rpx;
  height: 100%;
}

.wave-bar {
  width: 8rpx;
  background: linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%);
  border-radius: 4rpx;
  animation: wave 0.5s ease-in-out infinite;
}

.wave-bar:nth-child(1) {
  height: 40%;
  animation-delay: 0s;
}

.wave-bar:nth-child(2) {
  height: 70%;
  animation-delay: 0.1s;
}

.wave-bar:nth-child(3) {
  height: 100%;
  animation-delay: 0.2s;
}

.wave-bar:nth-child(4) {
  height: 60%;
  animation-delay: 0.3s;
}

.wave-bar:nth-child(5) {
  height: 40%;
  animation-delay: 0.4s;
}

@keyframes wave {
  0%, 100% {
    transform: scaleY(0.5);
  }
  50% {
    transform: scaleY(1);
  }
}

.voice-hint {
  font-size: 24rpx;
  color: #94a3b8;
}

.input-actions {
  display: flex;
  gap: 12rpx;
}

.action-btn-small {
  width: 56rpx;
  height: 56rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  border-radius: 50%;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.06);
  transition: all 0.2s;
}

.action-btn-small:active {
  transform: scale(0.95);
}

.action-icon-small {
  font-size: 28rpx;
  color: #64748b;
}

.send-btn {
  background: linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%);
}

.send-btn .action-icon-small {
  color: white;
}

@media (min-width: 768px) {
  .module-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1024px) {
  .main-panel-expanded {
    width: 800rpx;
  }
  
  .module-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
