<template>
  <view 
    class="optimized-navbar" 
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
      <view class="navbar-right">
        <view class="auth-buttons" v-if="showAuthButtons">
          <view class="auth-btn register-btn" @click="handleRegister">
            <text class="auth-btn-text">注册</text>
          </view>
          <view class="auth-btn login-btn" @click="handleLogin">
            <text class="auth-btn-text">登录</text>
          </view>
        </view>
        <view class="close-btn" v-else-if="showClose" @click="handleClose">
      <text class="close-icon">×</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  name: 'OptimizedNavbar',
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
    showAuthButtons: {
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
      navbarHeight: 40
    }
  },
  mounted() {
    this.getSystemInfo()
  },
  methods: {
    getSystemInfo() {
      const systemInfo = uni.getSystemInfoSync()
      this.statusBarHeight = this.safeAreaInsetTop ? (systemInfo.statusBarHeight || 0) : 0
      this.navbarHeight = this.statusBarHeight + 40
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
    },
    handleRegister() {
      uni.navigateTo({
        url: '/pages/user/login?mode=register',
        fail: () => {
          uni.switchTab({
            url: '/pages/user/login?mode=register',
            fail: () => {
              uni.reLaunch({
                url: '/pages/user/login?mode=register'
              })
            }
          })
        }
      })
    },
    handleLogin() {
      uni.navigateTo({
        url: '/pages/user/login?mode=login',
        fail: () => {
          uni.switchTab({
            url: '/pages/user/login?mode=login',
            fail: () => {
              uni.reLaunch({
                url: '/pages/user/login?mode=login'
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
.optimized-navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  background: #ffffff;
  z-index: 500;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.08);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  padding-top: constant(safe-area-inset-top);
  padding-top: env(safe-area-inset-top);
}

.navbar-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 40px;
  padding: 0 32rpx;
}

.navbar-left {
  width: 80rpx;
  height: 40px;
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
  background: #f8f9fa;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.back-btn:active {
  transform: scale(0.9);
  background: #e9ecef;
}

.back-icon {
  font-size: 48rpx;
  font-weight: bold;
  color: #2d3748;
  line-height: 1;
}

.navbar-center {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 40px;
}

.title-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4rpx;
}

.title-text {
  font-size: 36rpx;
  font-weight: 600;
  color: #1a202c;
  text-align: center;
  max-width: 400rpx;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  letter-spacing: 0.5rpx;
}

.subtitle-text {
  font-size: 22rpx;
  color: #718096;
  text-align: center;
  max-width: 400rpx;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  letter-spacing: 0.5rpx;
}

.navbar-right {
  width: auto;
  min-width: 80rpx;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 16rpx;
}

.auth-buttons {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.auth-btn {
  height: 64rpx;
  padding: 0 24rpx;
  border-radius: 32rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  user-select: none;
  -webkit-tap-highlight-color: transparent;
}

.register-btn {
  background: #f7fafc;
  border: 2rpx solid #e2e8f0;
}

.register-btn:active {
  transform: scale(0.95);
  background: #edf2f7;
}

.login-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  box-shadow: 0 4rpx 12rpx rgba(102, 126, 234, 0.3);
}

.login-btn:active {
  transform: scale(0.95);
  box-shadow: 0 2rpx 8rpx rgba(102, 126, 234, 0.3);
}

.auth-btn-text {
  font-size: 26rpx;
  font-weight: 500;
  letter-spacing: 0.5rpx;
}

.register-btn .auth-btn-text {
  color: #4a5568;
}

.login-btn .auth-btn-text {
  color: #ffffff;
}

.close-btn {
  width: 64rpx;
  height: 64rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: #f8f9fa;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  user-select: none;
  -webkit-tap-highlight-color: transparent;
}

.close-btn:active {
  transform: scale(0.9);
  background: #e9ecef;
}

.close-icon {
  font-size: 56rpx;
  font-weight: 300;
  color: #2d3748;
  line-height: 1;
}

@media screen and (max-width: 375px) {
  .navbar-content {
    padding: 0 20rpx;
  }
  
  .title-text {
    font-size: 32rpx;
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
  
  .auth-btn {
    height: 56rpx;
    padding: 0 20rpx;
  }
  
  .auth-btn-text {
    font-size: 24rpx;
  }
  
  .auth-buttons {
    gap: 12rpx;
  }
}

@media screen and (min-width: 415px) {
  .navbar-content {
    padding: 0 40rpx;
  }
  
  .title-text {
    font-size: 38rpx;
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
  
  .auth-btn {
    height: 72rpx;
    padding: 0 28rpx;
  }
  
  .auth-btn-text {
    font-size: 28rpx;
  }
  
  .auth-buttons {
    gap: 20rpx;
  }
}

@media screen and (orientation: landscape) {
  .navbar-content {
    padding: 0 60rpx;
    height: 36px;
  }
  
  .title-text {
    font-size: 32rpx;
  }
  
  .subtitle-text {
    font-size: 20rpx;
  }
  
  .navbar-left,
  .navbar-right {
    height: 36px;
  }
  
  .navbar-center {
    height: 36px;
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
  
  .auth-btn {
    height: 52rpx;
    padding: 0 20rpx;
  }
  
  .auth-btn-text {
    font-size: 24rpx;
  }
}
</style>