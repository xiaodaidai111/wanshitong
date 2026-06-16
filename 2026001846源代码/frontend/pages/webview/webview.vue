<template>
  <view class="webview-container">
    <view class="nav-bar">
      <view class="nav-back" @tap="goBack">
        <text class="back-icon">←</text>
      </view>
      <text class="nav-title">{{ pageTitle }}</text>
      <view class="nav-placeholder"></view>
    </view>
    <web-view :src="webUrl" class="webview-content"></web-view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      webUrl: '',
      pageTitle: ''
    };
  },
  onLoad(options) {
    if (options.url) {
      this.webUrl = decodeURIComponent(options.url);
    }
    if (options.title) {
      this.pageTitle = decodeURIComponent(options.title);
    }
  },
  methods: {
    goBack() {
      uni.navigateBack();
    }
  }
};
</script>

<style scoped>
.webview-container {
  width: 100%;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #fff;
}

.nav-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 88rpx;
  padding: 0 20rpx;
  padding-top: var(--status-bar-height, 44rpx);
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  flex-shrink: 0;
}

.nav-back {
  width: 60rpx;
  height: 60rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.back-icon {
  font-size: 36rpx;
  color: #fff;
}

.nav-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #fff;
  flex: 1;
  text-align: center;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  padding: 0 10rpx;
}

.nav-placeholder {
  width: 60rpx;
}

.webview-content {
  flex: 1;
}
</style>
