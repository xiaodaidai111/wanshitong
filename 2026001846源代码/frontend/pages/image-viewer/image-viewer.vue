<template>
  <view class="image-viewer-page">
    <view class="viewer-header" :style="{ paddingTop: statusBarHeight + 'px' }">
      <view class="header-bar">
        <view class="back-btn" @click="goBack">
          <text class="back-icon">←</text>
        </view>
        <text class="header-title">{{ title || '查看图片' }}</text>
        <view class="header-right"></view>
      </view>
    </view>

    <view class="viewer-body">
      <movable-area class="movable-area" v-if="imageSrc">
        <movable-view
          class="movable-view"
          direction="all"
          :scale="true"
          :scale-min="0.5"
          :scale-max="5"
          :scale-value="scaleValue"
          @scale="onScale"
          @change="onChange"
        >
          <image
            class="preview-image"
            :src="imageSrc"
            mode="widthFix"
            @load="onImageLoad"
            @error="onImageError"
            :style="{ width: imageDisplayWidth + 'rpx' }"
          ></image>
        </movable-view>
      </movable-area>

      <view class="loading-container" v-if="loading && !loadError">
        <view class="loading-spinner"></view>
        <text class="loading-text">图片加载中...</text>
      </view>

      <view class="error-container" v-if="loadError">
        <text class="error-icon">⚠️</text>
        <text class="error-text">图片加载失败</text>
        <view class="retry-btn" @click="retryLoad">
          <text class="retry-text">点击重试</text>
        </view>
      </view>
    </view>

    <view class="viewer-footer">
      <view class="zoom-controls">
        <view class="zoom-btn" @click="zoomOut">
          <text class="zoom-icon">−</text>
        </view>
        <text class="zoom-text">{{ Math.round(scaleValue * 100) }}%</text>
        <view class="zoom-btn" @click="zoomIn">
          <text class="zoom-icon">+</text>
        </view>
        <view class="zoom-divider"></view>
        <view class="zoom-btn" @click="resetZoom">
          <text class="zoom-reset-icon">↺</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      imageSrc: '',
      title: '',
      statusBarHeight: 0,
      scaleValue: 1,
      imageDisplayWidth: 750,
      loading: true,
      loadError: false,
      originalWidth: 0,
      originalHeight: 0
    }
  },
  onLoad(options) {
    const systemInfo = uni.getSystemInfoSync()
    this.statusBarHeight = systemInfo.statusBarHeight || 0

    if (options.src) {
      this.imageSrc = decodeURIComponent(options.src)
    }
    if (options.title) {
      this.title = decodeURIComponent(options.title)
    }
  },
  methods: {
    onImageLoad(e) {
      this.loading = false
      this.loadError = false
      if (e && e.detail && e.detail.width) {
        this.originalWidth = e.detail.width
        this.originalHeight = e.detail.height
        const screenWidth = uni.getSystemInfoSync().windowWidth
        const imageWidthPx = Math.min(screenWidth, e.detail.width)
        this.imageDisplayWidth = Math.round(imageWidthPx * 2)
      }
    },
    onImageError() {
      this.loading = false
      this.loadError = true
    },
    retryLoad() {
      this.loadError = false
      this.loading = true
      this.scaleValue = 1
      const src = this.imageSrc
      this.imageSrc = ''
      this.$nextTick(() => {
        this.imageSrc = src
      })
    },
    onScale(e) {
      if (e && e.detail) {
        this.scaleValue = e.detail.scale
      }
    },
    onChange(e) {
      if (e && e.detail && e.detail.scale !== undefined) {
        this.scaleValue = e.detail.scale
      }
    },
    zoomIn() {
      this.scaleValue = Math.min(5, this.scaleValue + 0.25)
    },
    zoomOut() {
      this.scaleValue = Math.max(0.5, this.scaleValue - 0.25)
    },
    resetZoom() {
      this.scaleValue = 1
    },
    goBack() {
      uni.navigateBack({
        delta: 1,
        fail: () => {
          uni.switchTab({
            url: '/pages/takeaway-expert/takeaway-expert',
            fail: () => {
              uni.reLaunch({
                url: '/pages/home/home'
              })
            }
          })
        }
      })
    }
  }
}
</script>

<style scoped>
.image-viewer-page {
  width: 100vw;
  height: 100vh;
  background: #000;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.viewer-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(10px);
}

.header-bar {
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20rpx;
}

.back-btn {
  width: 64rpx;
  height: 64rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.15);
}

.back-btn:active {
  background: rgba(255, 255, 255, 0.3);
}

.back-icon {
  font-size: 48rpx;
  font-weight: bold;
  color: #fff;
  line-height: 1;
}

.header-title {
  flex: 1;
  text-align: center;
  font-size: 32rpx;
  color: #fff;
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin: 0 20rpx;
}

.header-right {
  width: 64rpx;
}

.viewer-body {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  padding-top: calc(44px + var(--status-bar-height, 0px));
  padding-bottom: 120rpx;
}

.movable-area {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.movable-view {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 100%;
  min-height: 100%;
}

.preview-image {
  width: 750rpx;
  display: block;
}

.loading-container {
  position: absolute;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.loading-spinner {
  width: 64rpx;
  height: 64rpx;
  border: 4rpx solid rgba(255, 255, 255, 0.2);
  border-top-color: #4CCF87;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text {
  margin-top: 20rpx;
  font-size: 26rpx;
  color: rgba(255, 255, 255, 0.7);
}

.error-container {
  position: absolute;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.error-icon {
  font-size: 80rpx;
  margin-bottom: 20rpx;
}

.error-text {
  font-size: 28rpx;
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 30rpx;
}

.retry-btn {
  padding: 16rpx 48rpx;
  background: rgba(76, 207, 135, 0.8);
  border-radius: 40rpx;
}

.retry-btn:active {
  background: rgba(76, 207, 135, 1);
}

.retry-text {
  font-size: 26rpx;
  color: #fff;
  font-weight: 600;
}

.viewer-footer {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 100;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(10px);
  padding: 20rpx 0;
  padding-bottom: calc(20rpx + env(safe-area-inset-bottom));
}

.zoom-controls {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 32rpx;
}

.zoom-btn {
  width: 72rpx;
  height: 72rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.15);
}

.zoom-btn:active {
  background: rgba(255, 255, 255, 0.3);
}

.zoom-icon {
  font-size: 40rpx;
  color: #fff;
  font-weight: bold;
  line-height: 1;
}

.zoom-reset-icon {
  font-size: 36rpx;
  color: #fff;
  line-height: 1;
}

.zoom-text {
  font-size: 26rpx;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 600;
  min-width: 80rpx;
  text-align: center;
}

.zoom-divider {
  width: 1rpx;
  height: 40rpx;
  background: rgba(255, 255, 255, 0.2);
}
</style>
