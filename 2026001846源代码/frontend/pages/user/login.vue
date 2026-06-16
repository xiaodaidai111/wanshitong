<template>
  <view class="auth-page">
    <view class="home-navbar" :style="{ paddingTop: statusBarHeight + 'px' }">
      <view class="home-navbar-content">
        <view class="navbar-left" @click="handleBack">
          <view class="back-btn">
            <text class="back-icon">←</text>
          </view>
        </view>
        <view class="home-brand-block">
          <image src="../../static/icon-home.png" class="home-brand-icon" mode="aspectFit"></image>
          <text class="home-brand-name">{{ brandTitle }}</text>
        </view>
        <view class="navbar-right"></view>
      </view>
    </view>
    <view class="auth-container">
      <view class="auth-box">
        <view class="header-section">
          <text class="welcome-text">欢迎回来</text>
          <text class="subtitle-text">登录您的账户</text>
        </view>

        <view class="auth-tabs">
          <view class="tab-item" :class="{ active: !isRegister }" @click="isRegister = false">
            登录
          </view>
          <view class="tab-item" :class="{ active: isRegister }" @click="isRegister = true">
            注册
          </view>
        </view>

        <view v-if="!isRegister" class="form-content">
          <view class="input-field">
            <input class="uni-input" v-model="loginForm.phone" type="number" maxlength="11" placeholder="请输入手机号" />
          </view>
          <view class="input-field">
            <input class="uni-input" v-model="loginForm.password" type="password" placeholder="请输入密码" />
          </view>
          <view class="form-actions">
            <label class="check-box" @click="loginForm.remember = !loginForm.remember">
              <checkbox :checked="loginForm.remember" color="#4facfe" style="transform:scale(0.7)" />
              <text>记住登录</text>
            </label>
          </view>
          <button class="primary-btn" :loading="loading" @click="handleLogin">登录</button>
        </view>

        <view v-else class="form-content">
          <view class="input-field">
            <input
              class="uni-input"
              v-model="registerForm.name"
              type="text"
              placeholder="请输入昵称"
              @blur="checkUsernameAvailability"
            />
            <view class="input-status" v-if="usernameAvailable !== null">
              <text :class="usernameAvailable ? 'status-success' : 'status-error'">
                {{ usernameAvailable ? '✓ 用户名可用' : '✗ 用户名已被使用' }}
              </text>
            </view>
          </view>
          <view class="input-field">
            <input
              class="uni-input"
              v-model="registerForm.phone"
              type="number"
              maxlength="11"
              placeholder="请输入手机号"
              @blur="checkPhoneAvailability"
            />
            <view class="input-status" v-if="phoneAvailable !== null">
              <text :class="phoneAvailable ? 'status-success' : 'status-error'">
                {{ phoneAvailable ? '✓ 手机号可用' : '✗ 手机号已注册' }}
              </text>
            </view>
          </view>
          <view class="input-field">
            <input class="uni-input" v-model="registerForm.password" type="password" placeholder="请设置密码，至少6位" />
          </view>
          <view class="input-field">
            <input class="uni-input" v-model="registerForm.confirmPassword" type="password" placeholder="请再次输入密码" />
          </view>
          <view class="agreement-section">
            <checkbox :checked="registerForm.agreed" @click="registerForm.agreed = !registerForm.agreed" color="#4facfe" style="transform:scale(0.7)" />
            <text class="agreement-text">同意相关服务协议与用户隐私政策</text>
          </view>
          <button class="primary-btn" :loading="loading" @click="handleRegister">注册</button>
        </view>
    </view>
    </view>
    
    <view class="footer-note">
      <text>© 2026 设备检修知识作业系统</text>
    </view>
  </view>
</template>

<script>
import guestManager from '../../utils/guest.js'
import request from '../../utils/request.js'

export default {
  data() {
    return {
      statusBarHeight: 0,
      brandTitle: '设备检修知识作业系统',
      isRegister: false,
      loading: false,
      loginForm: {
        phone: '',
        password: '',
        remember: false
      },
      registerForm: {
        name: '',
        phone: '',
        password: '',
        confirmPassword: '',
        agreed: false
      },
      redirectUrl: '',
      checkingUsername: false,
      checkingPhone: false,
      usernameAvailable: null,
      phoneAvailable: null,
      redirectUrl: ''
    }
  },
  onLoad(options) {
    const systemInfo = uni.getSystemInfoSync()
    this.statusBarHeight = systemInfo.statusBarHeight || 0
    if (options.redirect) {
      this.redirectUrl = decodeURIComponent(options.redirect)
    }
    
    this.ensureGuestSession()
  },
  methods: {
    async ensureGuestSession() {
      const result = await guestManager.ensureGuestSession()
      if (result.success) {
        console.log('游客会话已创建', result.session_id)
      }
    },

    async checkUsernameAvailability() {
      const name = this.registerForm.name.trim()
      if (name.length < 2) {
        this.usernameAvailable = null
        return
      }

      this.checkingUsername = true
      try {
        const res = await request.post('/api/auth/check-username', { name })
        this.usernameAvailable = res.code === 200 ? res.data.available : false
      } catch (e) {
        console.error('检查用户名失败:', e)
        this.usernameAvailable = null
      } finally {
        this.checkingUsername = false
      }
    },

    async checkPhoneAvailability() {
      const phone = this.registerForm.phone.trim()
      if (phone.length !== 11) {
        this.phoneAvailable = null
        return
      }

      this.checkingPhone = true
      try {
        const res = await request.post('/api/auth/check-phone', { phone })
        this.phoneAvailable = res.code === 200 ? !res.data.registered : false
      } catch (e) {
        console.error('检查手机号失败:', e)
        this.phoneAvailable = null
      } finally {
        this.checkingPhone = false
      }
    },

    async handleLogin() {
      if (!this.loginForm.phone || !this.loginForm.password) {
        uni.showToast({ title: '手机号和密码不能为空', icon: 'none' })
        return
      }

      this.loading = true
      try {
        const res = await request.post('/api/auth/login', {
          phone: this.loginForm.phone,
          password: this.loginForm.password
        })
        const { code, data, message } = res || {}

        if (code === 200) {
          uni.setStorageSync('token', data.token)
          uni.setStorageSync('user', data.user)
          guestManager.clearGuestSession()
          uni.$emit('auth:login-success')

          uni.showToast({ title: '登录成功' })
          setTimeout(() => {
            const user = data.user || {}
            const isFirstLogin = !user.name || !user.gender || !user.age || !user.height || !user.weight

            if (this.redirectUrl) {
              uni.redirectTo({ url: this.redirectUrl })
            } else if (isFirstLogin) {
              uni.reLaunch({ url: '/pages/personal-center/initial-setup' })
            } else {
              uni.navigateBack({
                delta: 1,
                fail: () => {
                  uni.switchTab({
                    url: '/pages/home/home',
                    fail: () => {
                      uni.reLaunch({ url: '/pages/home/home' })
                    }
                  })
                }
              })
            }
          }, 500)
        } else {
          uni.showToast({ title: message || '登录失败', icon: 'none' })
        }
      } catch (e) {
        uni.showToast({ title: '服务异常', icon: 'none' })
      } finally {
        this.loading = false
      }
    },

    async handleRegister() {
      if (!this.registerForm.agreed) {
        uni.showToast({ title: '请先同意协议', icon: 'none' })
        return
      }

      const { name, phone, password, confirmPassword } = this.registerForm
      if (!name || !phone || !password || !confirmPassword) {
        uni.showToast({ title: '请填写完整信息', icon: 'none' })
        return
      }
      if (password.length < 6) {
        uni.showToast({ title: '密码至少6位', icon: 'none' })
        return
      }
      if (password !== confirmPassword) {
        uni.showToast({ title: '两次输入的密码不一致', icon: 'none' })
        return
      }
      if (this.usernameAvailable === false) {
        uni.showToast({ title: '用户名已被使用', icon: 'none' })
        return
      }
      if (this.phoneAvailable === false) {
        uni.showToast({ title: '手机号已注册', icon: 'none' })
        return
      }

      this.loading = true
      try {
        const res = await request.post('/api/auth/register', { name, phone, password })
        if (res.code === 200) {
          uni.showToast({ title: '注册成功' })
          setTimeout(() => { this.isRegister = false }, 1000)
        } else {
          uni.showToast({ title: res.message || '注册失败', icon: 'none' })
        }
      } catch (e) {
        uni.showToast({ title: '注册异常', icon: 'none' })
      } finally {
        this.loading = false
      }
    },

    handleBack() {
      uni.navigateBack({
        delta: 1,
        fail: () => {
          uni.switchTab({
            url: '/pages/home/home',
            fail: () => {
              uni.reLaunch({ url: '/pages/home/home' })
            }
          })
        }
      })
    }
  }
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  background: #f0fdf4 !important;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0 32rpx 40rpx 32rpx;
  padding-top: calc(var(--status-bar-height) + 88rpx);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
  animation: fadeIn 0.6s ease-out;
}

/* ===== 首页导航 ===== */
.home-navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  background: linear-gradient(180deg, rgba(247, 249, 252, 0.98) 0%, rgba(255, 255, 255, 0.94) 100%);
  z-index: 500;
  backdrop-filter: blur(18rpx);
  -webkit-backdrop-filter: blur(18rpx);
  border-bottom: 1rpx solid rgba(148, 163, 184, 0.16);
  box-shadow: 0 14rpx 38rpx rgba(15, 23, 42, 0.06);
}

.home-navbar-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 44px;
  padding: 0 28rpx;
}

.home-brand-block {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.home-brand-icon {
  width: 64rpx;
  height: 64rpx;
}

.home-brand-name {
  font-size: 38rpx;
  font-weight: 800;
  color: #0f172a;
  letter-spacing: 0;
  line-height: 1.15;
  white-space: nowrap;
}

.navbar-left {
  width: 80rpx;
  height: 44px;
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

.navbar-right {
  width: 80rpx;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: flex-end;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20rpx);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.auth-container {
  width: 100%;
  max-width: 600rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.auth-box {
  width: 100%;
  background-color: #ffffff;
  border-radius: 32rpx;
  padding: 60rpx 48rpx;
  box-shadow: 0 8rpx 32rpx rgba(0, 0, 0, 0.06);
  animation: fadeInUp 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(40rpx);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.header-section {
  margin-bottom: 48rpx;
  text-align: center;
}

.welcome-text {
  font-size: 48rpx;
  font-weight: bold;
  color: #1a202c;
  display: block;
  margin-bottom: 12rpx;
  letter-spacing: 1rpx;
}

.subtitle-text {
  font-size: 28rpx;
  color: #718096;
  display: block;
  letter-spacing: 0.5rpx;
}

.auth-tabs {
  display: flex;
  border-bottom: 2rpx solid #e2e8f0;
  margin-bottom: 48rpx;
  background: #ffffff;
  border-radius: 16rpx 16rpx 0 0;
  padding: 8rpx 0;
}

.tab-item {
  flex: 1;
  text-align: center;
  padding: 28rpx 0;
  font-size: 32rpx;
  color: #718096;
  position: relative;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
}

.tab-item:active {
  transform: scale(0.98);
}

.tab-item.active {
  color: #4facfe;
  font-weight: 600;
}

.tab-item.active::after {
  content: "";
  position: absolute;
  bottom: -10rpx;
  left: 25%;
  right: 25%;
  height: 4rpx;
  background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
  border-radius: 2rpx;
}

.form-content {
  display: flex;
  flex-direction: column;
  gap: 32rpx;
}

.input-field {
  position: relative;
  background-color: #f7fafc;
  border: 2rpx solid #e2e8f0;
  border-radius: 20rpx;
  height: 100rpx;
  display: flex;
  align-items: center;
  padding: 0 32rpx;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.input-field:focus-within {
  border-color: #4facfe;
  background-color: #ffffff;
  box-shadow: 0 0 0 4rpx rgba(79, 172, 254, 0.1);
}

.uni-input {
  width: 100%;
  height: 100%;
  font-size: 30rpx;
  color: #1a202c;
  box-sizing: border-box;
  letter-spacing: 0.5rpx;
}

.uni-input::placeholder {
  color: #a0aec0;
}

.input-status {
  position: absolute;
  right: 32rpx;
  bottom: -28rpx;
  font-size: 20rpx;
  z-index: 10;
}

.status-success {
  color: #48bb78;
}

.status-error {
  color: #f56565;
}

.form-actions {
  display: flex;
  justify-content: flex-start;
  font-size: 24rpx;
  color: #718096;
}

.check-box {
  display: flex;
  align-items: center;
  gap: 12rpx;
  cursor: pointer;
  transition: all 0.3s ease;
}

.check-box:active {
  transform: scale(0.98);
}

.agreement-section {
  display: flex;
  align-items: flex-start;
  gap: 12rpx;
  font-size: 24rpx;
  color: #718096;
}

.agreement-text {
  flex: 1;
  line-height: 1.6;
}

.primary-btn {
  width: 100%;
  height: 100rpx;
  background: linear-gradient(135deg, #10b981 0%, #34d399 100%);
  color: white;
  border: none;
  border-radius: 20rpx;
  font-size: 34rpx;
  font-weight: 600;
  margin-top: 16rpx;
  box-shadow: 0 8rpx 24rpx rgba(16, 185, 129, 0.35);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  letter-spacing: 1rpx;
}

.primary-btn:active {
  transform: translateY(2rpx) scale(0.98);
  box-shadow: 0 4rpx 16rpx rgba(16, 185, 129, 0.35);
}

.primary-btn::after {
  border: none;
}

.footer-note {
  margin-top: 60rpx;
  font-size: 22rpx;
  color: #a0aec0;
  letter-spacing: 0.5rpx;
}

@media (max-width: 750rpx) {
  .auth-box {
    padding: 48rpx 32rpx;
  }

  .welcome-text {
    font-size: 42rpx;
  }

  .subtitle-text {
    font-size: 26rpx;
  }

  .input-field {
    height: 92rpx;
  }

  .primary-btn {
    height: 92rpx;
    font-size: 32rpx;
  }
}

@media (max-width: 600rpx) {
  .auth-page {
    padding: 0 24rpx 32rpx 24rpx;
  }

  .auth-box {
    padding: 40rpx 24rpx;
  }

  .welcome-text {
    font-size: 38rpx;
  }
  
  .home-navbar-content {
    padding: 0 24rpx;
  }
  
  .home-brand-name {
    font-size: 34rpx;
  }
  
  .home-brand-icon {
    width: 56rpx;
    height: 56rpx;
  }
  
  .navbar-left,
  .navbar-right {
    width: 60rpx;
    height: 44px;
  }
  
  .back-btn {
    width: 56rpx;
    height: 56rpx;
  }
  
  .back-icon {
    font-size: 44rpx;
  }
}

/* 大屏幕设置*/
@media screen and (min-width: 768px) {
  .auth-container {
    max-width: 750rpx;
    margin: 0 auto;
  }
}

/* 横屏适配 */
@media screen and (orientation: landscape) {
  .auth-page {
    padding: 0 32rpx 20rpx 32rpx;
  }

  .auth-box {
    padding: 40rpx 32rpx;
  }

  .welcome-text {
    font-size: 36rpx;
  }

  .subtitle-text {
    font-size: 24rpx;
  }

  .input-field {
    height: 84rpx;
  }

  .primary-btn {
    height: 84rpx;
    font-size: 30rpx;
  }

  .home-navbar-content {
    height: 44px;
  }

  .navbar-left,
  .navbar-right {
    height: 44px;
  }

  .home-brand-name {
    font-size: 32rpx;
  }

  .home-brand-icon {
    width: 52rpx;
    height: 52rpx;
  }

  .back-btn {
    width: 52rpx;
    height: 52rpx;
  }

  .back-icon {
    font-size: 40rpx;
  }
}
</style>
