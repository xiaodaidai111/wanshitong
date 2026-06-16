<template>
  <view class="voice-btn-wrap">
    <view
      class="voice-btn"
      :class="{ 'voice-recording': isRecording, 'voice-transcribing': isTranscribing }"
      @touchstart.prevent="onTouchStart"
      @touchend.prevent="onTouchEnd"
      @touchcancel.prevent="onTouchCancel"
      @click="onClick"
    >
      <view class="voice-icon-wrap">
        <!-- 麦克风图标 -->
        <view class="mic-icon" v-if="!isRecording && !isTranscribing">
          <view class="mic-body"></view>
          <view class="mic-stand"></view>
        </view>
        <!-- 录音中波纹 -->
        <view class="recording-waves" v-if="isRecording">
          <view class="wave wave-1"></view>
          <view class="wave wave-2"></view>
          <view class="wave wave-3"></view>
          <view class="mic-body-sm"></view>
        </view>
        <!-- 转写中 -->
        <view class="transcribing-dots" v-if="isTranscribing">
          <view class="dot dot-1"></view>
          <view class="dot dot-2"></view>
          <view class="dot dot-3"></view>
        </view>
      </view>
    </view>
    <text class="voice-hint" v-if="showHint">
      {{ isRecording ? '松开结束' : isTranscribing ? '识别中...' : '按住说话' }}
    </text>
  </view>
</template>

<script>
import { createVoiceInputController } from '../../utils/voice-input.js'

export default {
  name: 'VoiceInputButton',
  props: {
    mode: { type: String, default: 'click' }, // 'click' | 'hold'
    service: { type: String, default: 'tuantuan' },
    showHint: { type: Boolean, default: true },
    maxDuration: { type: Number, default: 60000 }
  },
  data() {
    return {
      isRecording: false,
      isStopping: false,
      isTranscribing: false,
      controller: null
    }
  },
  mounted() {
    this.controller = createVoiceInputController({
      service: this.service,
      onStateChange: (state) => {
        this.isRecording = state.isRecording
        this.isStopping = state.isStopping
        this.isTranscribing = state.isTranscribing
        this.$emit('state-change', state)
      },
      onTranscribed: (text) => {
        this.$emit('result', text)
        uni.showToast({ title: '识别完成', icon: 'none', duration: 1000 })
      },
      onError: (error) => {
        this.$emit('error', error)
        uni.showToast({ title: error.message || '语音识别失败', icon: 'none' })
      }
    })
  },
  beforeUnmount() {
    if (this.controller) {
      this.controller.destroy()
    }
  },
  methods: {
    onClick() {
      if (this.mode !== 'click') return
      this.toggle()
    },
    onTouchStart() {
      if (this.mode !== 'hold') return
      this.start()
    },
    onTouchEnd() {
      if (this.mode !== 'hold') return
      this.stop()
    },
    onTouchCancel() {
      if (this.mode !== 'hold') return
      this.stop()
    },
    async toggle() {
      if (!this.controller) return
      try {
        await this.controller.toggleRecording()
      } catch (e) {
        // error handled in callback
      }
    },
    async start() {
      if (!this.controller) return
      try {
        await this.controller.startRecording()
      } catch (e) {
        // error handled in callback
      }
    },
    async stop() {
      if (!this.controller) return
      try {
        await this.controller.stopRecording()
      } catch (e) {
        // error handled in callback
      }
    }
  }
}
</script>

<style scoped>
.voice-btn-wrap {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8rpx;
}

.voice-btn {
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
  background: #14b8a6;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4rpx 16rpx rgba(20,184,166,0.3);
  transition: all 0.2s ease;
  cursor: pointer;
}

.voice-btn:active {
  transform: scale(0.92);
}

.voice-recording {
  background: linear-gradient(135deg, #EF4444, #DC2626);
  box-shadow: 0 4rpx 24rpx rgba(239, 68, 68, 0.4);
  animation: recording-pulse 1.2s ease-in-out infinite;
}

.voice-transcribing {
  background: #fbbf24;
  box-shadow: 0 4rpx 16rpx rgba(251,191,36,0.25);
}

@keyframes recording-pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.08); }
}

.voice-icon-wrap {
  width: 40rpx;
  height: 40rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 麦克风图标 */
.mic-icon {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4rpx;
}
.mic-body {
  width: 20rpx;
  height: 28rpx;
  background: #FFFFFF;
  border-radius: 10rpx;
}
.mic-stand {
  width: 28rpx;
  height: 12rpx;
  border: 3rpx solid #FFFFFF;
  border-top: none;
  border-radius: 0 0 14rpx 14rpx;
}

.mic-body-sm {
  width: 14rpx;
  height: 20rpx;
  background: #FFFFFF;
  border-radius: 7rpx;
  z-index: 2;
}

/* 录音波纹 */
.recording-waves {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}
.wave {
  position: absolute;
  border-radius: 50%;
  border: 2rpx solid rgba(255, 255, 255, 0.4);
  animation: wave-expand 1.5s ease-out infinite;
}
.wave-1 { width: 40rpx; height: 40rpx; animation-delay: 0s; }
.wave-2 { width: 56rpx; height: 56rpx; animation-delay: 0.3s; }
.wave-3 { width: 72rpx; height: 72rpx; animation-delay: 0.6s; }

@keyframes wave-expand {
  0% { opacity: 0.6; transform: scale(0.8); }
  100% { opacity: 0; transform: scale(1.4); }
}

/* 转写中动画 */
.transcribing-dots {
  display: flex;
  gap: 8rpx;
  align-items: center;
}
.dot {
  width: 10rpx;
  height: 10rpx;
  border-radius: 50%;
  background: #FFFFFF;
  animation: dot-bounce 1.2s ease-in-out infinite;
}
.dot-1 { animation-delay: 0s; }
.dot-2 { animation-delay: 0.2s; }
.dot-3 { animation-delay: 0.4s; }

@keyframes dot-bounce {
  0%, 60%, 100% { transform: translateY(0); }
  30% { transform: translateY(-10rpx); }
}

.voice-hint {
  font-size: 20rpx;
  color: #64748B;
  font-weight: 500;
}
</style>
