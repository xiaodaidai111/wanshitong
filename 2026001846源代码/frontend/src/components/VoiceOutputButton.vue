<template>
  <view
    class="voice-play-btn"
    :class="{ 'is-playing': isPlaying, 'is-loading': isSynthesizing }"
    @click="handleClick"
  >
    <view class="speaker-icon">
      <!-- 喇叭主体 -->
      <view class="speaker-body"></view>
      <!-- 静音状态 -->
      <view class="speaker-mute" v-if="!isPlaying && !isSynthesizing">
        <view class="mute-line"></view>
      </view>
      <!-- 播放中声波 -->
      <view class="speaker-waves" v-if="isPlaying">
        <view class="speaker-wave wave-sm"></view>
        <view class="speaker-wave wave-md"></view>
      </view>
      <!-- 加载中 -->
      <view class="loading-dots" v-if="isSynthesizing">
        <view class="ldot ldot-1"></view>
        <view class="ldot ldot-2"></view>
        <view class="ldot ldot-3"></view>
      </view>
    </view>
    <text class="voice-play-label" v-if="showLabel">
      {{ isPlaying ? '播放中' : isSynthesizing ? '合成中' : label }}
    </text>
  </view>
</template>

<script>
import { createVoiceOutputController } from '../../utils/speech-output.js'

export default {
  name: 'VoiceOutputButton',
  props: {
    text: { type: String, default: '' },
    service: { type: String, default: 'tuantuan' },
    voice: { type: String, default: 'zhichu' },
    showLabel: { type: Boolean, default: false },
    label: { type: String, default: '语音播报' }
  },
  data() {
    return {
      isPlaying: false,
      isSynthesizing: false,
      controller: null
    }
  },
  watch: {
    text() {
      if (this.isPlaying) {
        this.controller?.stop()
      }
    }
  },
  mounted() {
    this.controller = createVoiceOutputController({
      service: this.service,
      voice: this.voice,
      onStateChange: (state) => {
        this.isPlaying = state.isPlaying
        this.isSynthesizing = state.isSynthesizing
        this.$emit('state-change', state)
      },
      onError: (error) => {
        this.$emit('error', error)
        uni.showToast({ title: (error.message || '语音播放失败').slice(0, 20), icon: 'none' })
      }
    })
  },
  beforeUnmount() {
    this.controller?.destroy()
  },
  methods: {
    async handleClick() {
      if (this.isSynthesizing) return

      if (this.isPlaying) {
        this.controller?.stop()
        return
      }

      if (!this.text?.trim()) {
        uni.showToast({ title: '没有可播放的内容', icon: 'none' })
        return
      }

      try {
        await this.controller?.speak(this.text)
      } catch (e) {
        // handled in onError callback
      }
    },
    stop() {
      this.controller?.stop()
    }
  }
}
</script>

<style scoped>
.voice-play-btn {
  display: inline-flex;
  align-items: center;
  gap: 8rpx;
  padding: 8rpx 16rpx;
  border-radius: 16rpx;
  background: #ccfbf1;
  border: 1rpx solid #99f6e4;
  transition: all 0.2s ease;
  cursor: pointer;
}

.voice-play-btn:active {
  transform: scale(0.94);
}

.voice-play-btn.is-playing {
  background: rgba(16, 185, 129, 0.12);
  border-color: rgba(16, 185, 129, 0.3);
}

.voice-play-btn.is-loading {
  background: rgba(245, 158, 11, 0.1);
  border-color: rgba(245, 158, 11, 0.25);
}

.speaker-icon {
  position: relative;
  width: 32rpx;
  height: 32rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.speaker-body {
  width: 14rpx;
  height: 14rpx;
  background: #14b8a6;
  border-radius: 3rpx;
  position: relative;
}

.is-playing .speaker-body {
  background: #34d399;
}

.is-loading .speaker-body {
  background: #fbbf24;
}

/* 喇叭口 */
.speaker-body::after {
  content: '';
  position: absolute;
  right: -8rpx;
  top: -4rpx;
  width: 0;
  height: 0;
  border-top: 11rpx solid transparent;
  border-bottom: 11rpx solid transparent;
  border-left: 8rpx solid #14b8a6;
}

.is-playing .speaker-body::after {
  border-left-color: #34d399;
}

.is-loading .speaker-body::after {
  border-left-color: #fbbf24;
}

/* 静音线 */
.speaker-mute {
  position: absolute;
  right: -4rpx;
  bottom: -2rpx;
}
.mute-line {
  width: 20rpx;
  height: 3rpx;
  background: #94A3B8;
  transform: rotate(-45deg);
  border-radius: 2rpx;
}

/* 声波动画 */
.speaker-waves {
  position: absolute;
  right: -12rpx;
  top: 50%;
  transform: translateY(-50%);
}
.speaker-wave {
  position: absolute;
  border-right: 3rpx solid #34d399;
  border-radius: 0 50% 50% 0;
  top: 50%;
  transform: translateY(-50%);
}
.wave-sm {
  width: 8rpx;
  height: 14rpx;
  right: 0;
  animation: wave-sm-anim 1s ease-in-out infinite;
}
.wave-md {
  width: 12rpx;
  height: 22rpx;
  right: 6rpx;
  animation: wave-md-anim 1s ease-in-out infinite 0.2s;
}

@keyframes wave-sm-anim {
  0%, 100% { opacity: 0.3; }
  50% { opacity: 1; }
}
@keyframes wave-md-anim {
  0%, 100% { opacity: 0.2; }
  50% { opacity: 0.8; }
}

/* 加载中动画 */
.loading-dots {
  position: absolute;
  right: -14rpx;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  gap: 4rpx;
}
.ldot {
  width: 5rpx;
  height: 5rpx;
  border-radius: 50%;
  background: #F59E0B;
  animation: ldot-bounce 1s ease-in-out infinite;
}
.ldot-1 { animation-delay: 0s; }
.ldot-2 { animation-delay: 0.15s; }
.ldot-3 { animation-delay: 0.3s; }

@keyframes ldot-bounce {
  0%, 60%, 100% { transform: translateY(0); }
  30% { transform: translateY(-6rpx); }
}

.voice-play-label {
  font-size: 22rpx;
  color: #14b8a6;
  font-weight: 500;
}

.is-playing .voice-play-label {
  color: #34d399;
}

.is-loading .voice-play-label {
  color: #fbbf24;
}
</style>
