<template>
  <view 
    class="floating-ball"
    :class="{ 
      'floating-ball-dragging': isDragging,
      'floating-ball-expanded': isExpanded,
      'floating-ball-recording': isRecording
    }"
    :style="ballStyle"
    @touchstart="onTouchStart"
    @touchmove="onTouchMove"
    @touchend="onTouchEnd"
    @click="onClick"
    @longpress="onLongPress"
  >
    <view class="ball-content">
      <view class="ball-icon">{{ currentIcon }}</view>
      <view class="ball-pulse" v-if="isPulse"></view>
      <view class="ball-recording-wave" v-if="isRecording">
        <view class="wave wave-1"></view>
        <view class="wave wave-2"></view>
        <view class="wave wave-3"></view>
      </view>
    </view>
    
    <view class="ball-settings" v-if="showSettings">
      <view class="settings-item" @click.stop="toggleSize">
        <text class="settings-icon">📏</text>
        <text class="settings-label">大小</text>
      </view>
      <view class="settings-item" @click.stop="toggleOpacity">
        <text class="settings-icon">👁�?/text>
        <text class="settings-label">透明�?/text>
      </view>
      <view class="settings-item" @click.stop="toggleLock">
        <text class="settings-icon">{{ isLocked ? '🔒' : '🔓' }}</text>
        <text class="settings-label">{{ isLocked ? '解锁' : '锁定' }}</text>
      </view>
      <view class="settings-item" @click.stop="hideBall">
        <text class="settings-icon">�?/text>
        <text class="settings-label">隐藏</text>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  name: 'FloatingBall',
  props: {
    defaultIcon: {
      type: String,
      default: '🤖'
    },
    recordingIcon: {
      type: String,
      default: '🎤'
    },
    defaultSize: {
      type: Number,
      default: 80
    },
    defaultOpacity: {
      type: Number,
      default: 0.85
    },
    defaultPosition: {
      type: Object,
      default: () => ({
        x: 0,
        y: 0
      })
    },
    enableDrag: {
      type: Boolean,
      default: true
    },
    enableLongPress: {
      type: Boolean,
      default: true
    },
    enableDoubleClick: {
      type: Boolean,
      default: true
    }
  },
  data() {
    return {
      position: { ...this.defaultPosition },
      size: this.defaultSize,
      opacity: this.defaultOpacity,
      isDragging: false,
      isExpanded: false,
      isRecording: false,
      isPulse: true,
      isLocked: false,
      showSettings: false,
      startX: 0,
      startY: 0,
      lastClickTime: 0,
      longPressTimer: null
    }
  },
  computed: {
    currentIcon() {
      return this.isRecording ? this.recordingIcon : this.defaultIcon
    },
    ballStyle() {
      return {
        width: `${this.size}rpx`,
        height: `${this.size}rpx`,
        left: `${this.position.x}rpx`,
        top: `${this.position.y}rpx`,
        opacity: this.opacity
      }
    }
  },
  mounted() {
    this.initPosition()
    this.startPulseAnimation()
  },
  methods: {
    initPosition() {
      const systemInfo = uni.getSystemInfoSync()
      const screenWidth = systemInfo.screenWidth
      const screenHeight = systemInfo.screenHeight
      
      if (this.defaultPosition.x === 0 && this.defaultPosition.y === 0) {
        this.position = {
          x: screenWidth - this.size / 2 - 40,
          y: screenHeight - this.size / 2 - 40
        }
      }
    },
    
    onTouchStart(e) {
      if (!this.enableDrag || this.isLocked) return
      
      this.isDragging = true
      this.startX = e.touches[0].clientX
      this.startY = e.touches[0].clientY
      
      this.startLongPressTimer()
    },
    
    onTouchMove(e) {
      if (!this.isDragging || this.isLocked) return
      
      const deltaX = e.touches[0].clientX - this.startX
      const deltaY = e.touches[0].clientY - this.startY
      
      this.position.x += deltaX
      this.position.y += deltaY
      
      this.startX = e.touches[0].clientX
      this.startY = e.touches[0].clientY
      
      this.clearLongPressTimer()
    },
    
    onTouchEnd(e) {
      this.isDragging = false
      this.clearLongPressTimer()
      
      this.snapToEdge()
      this.vibrateFeedback()
    },
    
    onClick(e) {
      const currentTime = Date.now()
      const timeDiff = currentTime - this.lastClickTime
      
      if (timeDiff < 300 && this.enableDoubleClick) {
        this.onDoubleClick()
      } else {
        this.onSingleClick()
      }
      
      this.lastClickTime = currentTime
    },
    
    onSingleClick() {
      if (this.showSettings) {
        this.showSettings = false
        return
      }
      
      this.isExpanded = !this.isExpanded
      this.$emit('expand', this.isExpanded)
      
      if (this.isExpanded) {
        this.isPulse = false
      } else {
        this.isPulse = true
      }
    },
    
    onDoubleClick() {
      this.$emit('double-click')
      this.startVoiceInput()
    },
    
    onLongPress() {
      if (!this.enableLongPress || this.isLocked) return
      
      this.showSettings = !this.showSettings
      this.$emit('long-press', this.showSettings)
    },
    
    startLongPressTimer() {
      if (this.enableLongPress) {
        this.longPressTimer = setTimeout(() => {
          this.onLongPress()
        }, 800)
      }
    },
    
    clearLongPressTimer() {
      if (this.longPressTimer) {
        clearTimeout(this.longPressTimer)
        this.longPressTimer = null
      }
    },
    
    snapToEdge() {
      const systemInfo = uni.getSystemInfoSync()
      const screenWidth = systemInfo.screenWidth
      const screenHeight = systemInfo.screenHeight
      const margin = 40
      
      const centerX = this.position.x + this.size / 2
      
      if (centerX < screenWidth / 2) {
        this.position.x = margin
      } else {
        this.position.x = screenWidth - this.size - margin
      }
      
      if (this.position.y < margin) {
        this.position.y = margin
      }
      
      if (this.position.y > screenHeight - this.size - margin) {
        this.position.y = screenHeight - this.size - margin
      }
    },
    
    startPulseAnimation() {
      this.isPulse = true
    },
    
    stopPulseAnimation() {
      this.isPulse = false
    },
    
    startVoiceInput() {
      this.isRecording = !this.isRecording
      this.$emit('voice-input', this.isRecording)
      
      if (this.isRecording) {
        this.vibrateFeedback()
      }
    },
    
    stopVoiceInput() {
      this.isRecording = false
      this.$emit('voice-input', false)
    },
    
    toggleSize() {
      const sizes = [60, 80, 100, 120]
      const currentIndex = sizes.indexOf(this.size)
      const nextIndex = (currentIndex + 1) % sizes.length
      this.size = sizes[nextIndex]
      this.$emit('size-change', this.size)
      this.vibrateFeedback()
    },
    
    toggleOpacity() {
      const opacities = [0.5, 0.7, 0.85, 1.0]
      const currentIndex = opacities.indexOf(this.opacity)
      const nextIndex = (currentIndex + 1) % opacities.length
      this.opacity = opacities[nextIndex]
      this.$emit('opacity-change', this.opacity)
      this.vibrateFeedback()
    },
    
    toggleLock() {
      this.isLocked = !this.isLocked
      this.$emit('lock-change', this.isLocked)
      this.vibrateFeedback()
    },
    
    hideBall() {
      this.$emit('hide')
      this.vibrateFeedback()
    },
    
    vibrateFeedback() {
      uni.vibrateShort({
        success: () => {},
        fail: () => {}
      })
    },
    
    expand() {
      this.isExpanded = true
      this.isPulse = false
      this.$emit('expand', true)
    },
    
    collapse() {
      this.isExpanded = false
      this.isPulse = true
      this.$emit('expand', false)
    }
  }
}
</script>

<style scoped>
.floating-ball {
  position: fixed;
  z-index: 9999;
  border-radius: 50%;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  box-shadow: 0 8rpx 24rpx rgba(99, 102, 241, 0.4);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: visible;
  cursor: pointer;
  user-select: none;
  -webkit-user-select: none;
  -webkit-touch-callout: none;
}

.floating-ball-dragging {
  transform: scale(0.9);
  box-shadow: 0 12rpx 32rpx rgba(99, 102, 241, 0.5);
}

.floating-ball-expanded {
  transform: scale(1.1);
  box-shadow: 0 12rpx 40rpx rgba(99, 102, 241, 0.5);
}

.floating-ball-recording {
  background: linear-gradient(135deg, #ef4444 0%, #f87171 100%);
  box-shadow: 0 8rpx 24rpx rgba(239, 68, 68, 0.4);
}

.ball-content {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.ball-icon {
  font-size: 48rpx;
  z-index: 2;
  transition: all 0.3s;
}

.ball-pulse {
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(99, 102, 241, 0.3) 0%, transparent 70%);
  animation: pulse 3s ease-in-out infinite;
  z-index: 1;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    opacity: 0.5;
  }
  50% {
    transform: scale(1.2);
    opacity: 0.8;
  }
}

.ball-recording-wave {
  position: absolute;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
  z-index: 1;
}

.wave {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  border-radius: 50%;
  border: 2rpx solid rgba(255, 255, 255, 0.5);
  animation: wave 1.5s ease-out infinite;
}

.wave-1 {
  width: 100%;
  height: 100%;
  animation-delay: 0s;
}

.wave-2 {
  width: 120%;
  height: 120%;
  animation-delay: 0.5s;
}

.wave-3 {
  width: 140%;
  height: 140%;
  animation-delay: 1s;
}

@keyframes wave {
  0% {
    transform: translate(-50%, -50%) scale(0.5);
    opacity: 1;
  }
  100% {
    transform: translate(-50%, -50%) scale(1.5);
    opacity: 0;
  }
}

.ball-settings {
  position: absolute;
  bottom: 120%;
  right: 0;
  background: white;
  border-radius: 24rpx;
  padding: 16rpx;
  box-shadow: 0 8rpx 32rpx rgba(0, 0, 0, 0.15);
  min-width: 200rpx;
  animation: slideUp 0.3s ease-out;
  z-index: 10000;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20rpx);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.settings-item {
  display: flex;
  align-items: center;
  gap: 16rpx;
  padding: 16rpx 20rpx;
  border-radius: 16rpx;
  transition: all 0.2s;
}

.settings-item:active {
  background: #f3f4f6;
  transform: scale(0.98);
}

.settings-icon {
  font-size: 32rpx;
  width: 48rpx;
  text-align: center;
}

.settings-label {
  font-size: 26rpx;
  color: #374151;
  font-weight: 500;
}
</style>
