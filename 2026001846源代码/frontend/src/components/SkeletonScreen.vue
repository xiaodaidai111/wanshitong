<template>
  <view class="skeleton-wrap" v-if="loading">
    <!-- 导航栏骨架 -->
    <view class="sk-navbar">
      <view class="sk-avatar sk-shine"></view>
      <view class="sk-title sk-shine"></view>
    </view>

    <!-- 轮播图骨架 -->
    <view class="sk-banner sk-shine" v-if="showBanner"></view>

    <!-- 概览卡片骨架 -->
    <view class="sk-overview" v-if="showOverview">
      <view class="sk-stat-card" v-for="i in 4" :key="i">
        <view class="sk-icon sk-shine"></view>
        <view class="sk-number sk-shine"></view>
        <view class="sk-label sk-shine"></view>
      </view>
    </view>

    <!-- 功能入口骨架 -->
    <view class="sk-functions" v-if="showFunctions">
      <view class="sk-section-title sk-shine"></view>
      <view class="sk-func-grid">
        <view class="sk-func-card" v-for="i in 5" :key="i">
          <view class="sk-func-icon sk-shine"></view>
          <view class="sk-func-name sk-shine"></view>
          <view class="sk-func-desc sk-shine"></view>
        </view>
      </view>
    </view>

    <!-- 列表骨架 -->
    <view class="sk-list" v-if="showList">
      <view class="sk-section-title sk-shine"></view>
      <view class="sk-list-item" v-for="i in 3" :key="i">
        <view class="sk-item-left">
          <view class="sk-avatar-sm sk-shine"></view>
          <view class="sk-item-info">
            <view class="sk-line-long sk-shine"></view>
            <view class="sk-line-short sk-shine"></view>
          </view>
        </view>
        <view class="sk-item-content">
          <view class="sk-line-full sk-shine"></view>
          <view class="sk-line-80 sk-shine"></view>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  name: 'SkeletonScreen',
  props: {
    loading: { type: Boolean, default: true },
    showBanner: { type: Boolean, default: true },
    showOverview: { type: Boolean, default: true },
    showFunctions: { type: Boolean, default: true },
    showList: { type: Boolean, default: true }
  }
}
</script>

<style scoped>
.skeleton-wrap {
  padding: 0 32rpx;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* 闪光动画 */
.sk-shine {
  background: linear-gradient(90deg, #F1F5F9 25%, #E2E8F0 37%, #F1F5F9 63%);
  background-size: 200% 100%;
  animation: shimmer 1.4s ease-in-out infinite;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* 导航栏骨架 */
.sk-navbar {
  display: flex;
  align-items: center;
  gap: 16rpx;
  padding: 120rpx 0 24rpx;
}
.sk-avatar {
  width: 64rpx;
  height: 64rpx;
  border-radius: 50%;
}
.sk-title {
  width: 240rpx;
  height: 36rpx;
  border-radius: 8rpx;
}

/* 轮播图骨架 */
.sk-banner {
  width: 100%;
  height: 320rpx;
  border-radius: 16rpx;
  margin-bottom: 24rpx;
}

/* 概览卡片骨架 */
.sk-overview {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16rpx;
  margin-bottom: 24rpx;
}
.sk-stat-card {
  background: #FFFFFF;
  border-radius: 16rpx;
  padding: 24rpx 12rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10rpx;
}
.sk-icon {
  width: 48rpx;
  height: 48rpx;
  border-radius: 12rpx;
}
.sk-number {
  width: 56rpx;
  height: 36rpx;
  border-radius: 8rpx;
}
.sk-label {
  width: 64rpx;
  height: 20rpx;
  border-radius: 6rpx;
}

/* 功能入口骨架 */
.sk-functions {
  background: #FFFFFF;
  border-radius: 16rpx;
  padding: 32rpx;
  margin-bottom: 24rpx;
}
.sk-section-title {
  width: 160rpx;
  height: 32rpx;
  border-radius: 8rpx;
  margin-bottom: 24rpx;
}
.sk-func-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20rpx;
}
.sk-func-card {
  padding: 32rpx 28rpx;
  border-radius: 16rpx;
  border: 1rpx solid #E5E7EB;
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}
.sk-func-icon {
  width: 80rpx;
  height: 80rpx;
  border-radius: 16rpx;
}
.sk-func-name {
  width: 120rpx;
  height: 28rpx;
  border-radius: 8rpx;
}
.sk-func-desc {
  width: 160rpx;
  height: 20rpx;
  border-radius: 6rpx;
}

/* 列表骨架 */
.sk-list {
  background: #FFFFFF;
  border-radius: 16rpx;
  padding: 32rpx;
  margin-bottom: 24rpx;
}
.sk-list-item {
  padding: 20rpx 0;
  border-bottom: 1rpx solid #F1F5F9;
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}
.sk-list-item:last-child {
  border-bottom: none;
}
.sk-item-left {
  display: flex;
  align-items: center;
  gap: 16rpx;
}
.sk-avatar-sm {
  width: 56rpx;
  height: 56rpx;
  border-radius: 50%;
}
.sk-item-info {
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}
.sk-line-long {
  width: 180rpx;
  height: 24rpx;
  border-radius: 6rpx;
}
.sk-line-short {
  width: 120rpx;
  height: 18rpx;
  border-radius: 6rpx;
}
.sk-item-content {
  display: flex;
  flex-direction: column;
  gap: 10rpx;
  padding-left: 72rpx;
}
.sk-line-full {
  width: 100%;
  height: 20rpx;
  border-radius: 6rpx;
}
.sk-line-80 {
  width: 80%;
  height: 20rpx;
  border-radius: 6rpx;
}
</style>
