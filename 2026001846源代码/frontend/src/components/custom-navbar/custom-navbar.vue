<template>
  <view 
    class="custom-navbar" 
    :style="{ height: navbarHeight + 'px', paddingTop: statusBarHeight + 'px' }"
  >
    <view class="navbar-content">
      <view class="navbar-left" @click="handleBack">
        <view class="back-btn" v-if="showBack">
          <text class="back-icon">←</text>
        </view>
      </view>
      <view class="navbar-center">
        <view class="title-section">
          <text class="title-text">{{ title }}</text>
          <text class="subtitle-text" v-if="subtitle">{{ subtitle }}</text>
        </view>
      </view>
      <view class="navbar-right" @click="handleClose">
        <view class="close-btn" v-if="showClose">
          <text class="close-icon">×</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  name: 'CustomNavbar',
  props: {
    title: {
      type: String,
      default: ''
    },
    subtitle: {
      type: String,
      default: ''
    },
    showBack: {
      type: Boolean,
      default: true
    },
    showClose: {
      type: Boolean,
      default: false
    },
    showBrand: {
      type: Boolean,
      default: false
    },
    closeUrl: {
      type: String,
      default: ''
    },
    safeAreaInsetTop: {
      type: Boolean,
      default: true
    }
  },
  data() {
    return {
      statusBarHeight: 0,
      navbarHeight: 36
    }
  },
  mounted() {
    this.getSystemInfo()
  },
  methods: {
    getSystemInfo() {
      const systemInfo = uni.getSystemInfoSync()
      this.statusBarHeight = this.safeAreaInsetTop ? (systemInfo.statusBarHeight || 0) : 0
      this.navbarHeight = this.statusBarHeight + 36
    },
    handleBack() {
      uni.navigateBack({
        delta: 1,
        fail: () => {
          uni.switchTab({
            url: '/pages/home/home',
            fail: () => {
              uni.reLaunch({
                url: '/pages/home/home'
              })
            }
          })
        }
      })
    },
    handleClose() {
      if (this.closeUrl) {
        uni.navigateTo({
          url: this.closeUrl,
          fail: () => {
            uni.switchTab({
              url: this.closeUrl,
              fail: () => {
                uni.reLaunch({
                  url: this.closeUrl
                })
              }
            })
          }
        })
      } else {
        uni.navigateBack({
          delta: 1,
          fail: () => {
            uni.switchTab({
              url: '/pages/home/home',
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
}
</script>

<style scoped>
.custom-navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
  z-index: 500;
  box-shadow: 0 2rpx 12rpx rgba(16, 185, 129, 0.1);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  padding-top: constant(safe-area-inset-top);
  padding-top: env(safe-area-inset-top);
}

.navbar-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 36px;
  padding: 0 30rpx;
}

.navbar-left {
  width: 80rpx;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  cursor: pointer;
  user-select: none;
  -webkit-tap-highlight-color: transparent;
}

.back-btn {
  width: 64rpx;
  height: 64rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: rgba(6, 95, 70, 0.1);
  backdrop-filter: blur(10rpx);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.back-btn:active {
  transform: scale(0.9);
  background: rgba(6, 95, 70, 0.2);
}

.back-icon {
  font-size: 48rpx;
  font-weight: bold;
  color: #065f46;
  line-height: 1;
}

.navbar-center {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 36px;
}

.title-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4rpx;
}

.title-text {
  font-size: 34rpx;
  font-weight: 600;
  color: #065f46;
  text-align: center;
  max-width: 400rpx;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  letter-spacing: 1rpx;
  text-shadow: 0 1rpx 2rpx rgba(6, 95, 70, 0.1);
}

.subtitle-text {
  font-size: 22rpx;
  color: rgba(6, 95, 70, 0.85);
  text-align: center;
  max-width: 400rpx;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  letter-spacing: 0.5rpx;
}

.navbar-right {
  width: 80rpx;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  cursor: pointer;
  user-select: none;
  -webkit-tap-highlight-color: transparent;
}

.close-btn {
  width: 64rpx;
  height: 64rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: rgba(6, 95, 70, 0.1);
  backdrop-filter: blur(10rpx);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.close-btn:active {
  transform: scale(0.9);
  background: rgba(6, 95, 70, 0.2);
}

.close-icon {
  font-size: 56rpx;
  font-weight: 300;
  color: #065f46;
  line-height: 1;
}

@media screen and (max-width: 375px) {
  .navbar-content {
    padding: 0 20rpx;
  }
  
  .title-text {
    font-size: 30rpx;
    max-width: 300rpx;
  }
  
  .subtitle-text {
    font-size: 20rpx;
    max-width: 300rpx;
  }
  
  .back-icon {
    font-size: 44rpx;
  }
  
  .close-icon {
    font-size: 52rpx;
  }
  
  .back-btn,
  .close-btn {
    width: 56rpx;
    height: 56rpx;
  }
}

@media screen and (min-width: 415px) {
  .navbar-content {
    padding: 0 40rpx;
  }
  
  .title-text {
    font-size: 36rpx;
    max-width: 450rpx;
  }
  
  .subtitle-text {
    font-size: 24rpx;
    max-width: 450rpx;
  }
  
  .back-icon {
    font-size: 52rpx;
  }
  
  .close-icon {
    font-size: 60rpx;
  }
}

@media screen and (orientation: landscape) {
  .navbar-content {
    padding: 0 60rpx;
    height: 32px;
  }
  
  .title-text {
    font-size: 30rpx;
  }
  
  .subtitle-text {
    font-size: 20rpx;
  }
  
  .navbar-left,
  .navbar-right {
    height: 32px;
  }
  
  .navbar-center {
    height: 32px;
  }
  
  .back-btn,
  .close-btn {
    width: 52rpx;
    height: 52rpx;
  }
  
  .back-icon {
    font-size: 44rpx;
  }
  
  .close-icon {
    font-size: 52rpx;
  }
}
</style>