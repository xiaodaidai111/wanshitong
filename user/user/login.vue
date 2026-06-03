<template>
  <view class="auth-page">
    <view class="auth-box">
      <!-- 品牌标题 -->
      <view class="header-section">
        <text class="brand-name">膳食全周期系统</text>
        <text class="page-title">{{ isRegister ? '账号注册' : '账号登录' }}</text>
      </view>

      <!-- 选项卡 -->
      <view class="auth-tabs">
        <view class="tab-item" :class="{ active: !isRegister }" @click="isRegister = false">
          登录
        </view>
        <view class="tab-item" :class="{ active: isRegister }" @click="isRegister = true">
          注册
        </view>
      </view>

      <!-- 登录表单 -->
      <view v-if="!isRegister" class="form-content">
        <view class="input-field">
          <input class="uni-input" v-model="loginForm.phone" type="number" maxlength="11" placeholder="请输入手机号" />
        </view>
        <view class="input-field">
          <input class="uni-input" v-model="loginForm.password" type="password" placeholder="请输入密码" />
        </view>
        <view class="form-actions">
          <label class="check-box" @click="loginForm.remember = !loginForm.remember">
            <checkbox :checked="loginForm.remember" color="#10b981" style="transform:scale(0.7)" />
            <text>记住登录</text>
          </label>
        </view>
        <button class="primary-btn" :loading="loading" @click="handleLogin">登录</button>
      </view>

        <!-- 注册表单 -->
        <view v-else class="form-content">
          <view class="input-field">
            <input class="uni-input" v-model="registerForm.name" type="text" placeholder="请输入昵称" />
          </view>
          <view class="input-field">
            <input class="uni-input" v-model="registerForm.phone" type="number" maxlength="11" placeholder="请输入手机号" />
          </view>
          <view class="input-field">
            <input class="uni-input" v-model="registerForm.password" type="password" placeholder="请设置密码(至少6位)" />
          </view>
          <view class="input-field">
            <input class="uni-input" v-model="registerForm.confirmPassword" type="password" placeholder="请再次输入密码" />
          </view>
        <view class="agreement-section">
          <checkbox :checked="registerForm.agreed" @click="registerForm.agreed = !registerForm.agreed" color="#10b981" style="transform:scale(0.7)" />
          <text class="agreement-text">同意相关服务协议与用户隐私政策</text>
        </view>
        <button class="primary-btn" :loading="loading" @click="handleRegister">注册</button>
      </view>
    </view>
    
    <view class="footer-note">
      <text>© 2026 膳食全周期系统</text>
    </view>
  </view>
</template>

<script>
const BASE_URL = 'http://127.0.0.1:5000'

export default {
  data() {
    return {
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
      }
    }
  },
  methods: {
    async handleLogin() {
      if (!this.loginForm.phone || !this.loginForm.password) {
        uni.showToast({ title: '手机号和密码不能为空', icon: 'none' })
        return
      }
      this.loading = true
      try {
        const res = await new Promise((resolve, reject) => {
          uni.request({
            url: `${BASE_URL}/api/auth/login`,
            method: 'POST',
            header: { 'Content-Type': 'application/json' },
            data: { phone: this.loginForm.phone, password: this.loginForm.password },
            success: resolve,
            fail: reject
          })
        })
        const { code, data, message } = res.data || {}
        if (code === 200) {
          uni.setStorageSync('token', data.token)
          uni.setStorageSync('user', data.user)
          uni.showToast({ title: '登录成功' })
          setTimeout(() => uni.switchTab({ url: '/pages/home/home' }), 500)
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
      if (!name || !phone || !password) {
        uni.showToast({ title: '请填写完整', icon: 'none' })
        return
      }
      if (password !== confirmPassword) {
        uni.showToast({ title: '两次输入的密码不一致', icon: 'none' })
        return
      }
      this.loading = true
      try {
        const res = await new Promise((resolve, reject) => {
          uni.request({
            url: `${BASE_URL}/api/auth/register`,
            method: 'POST',
            header: { 'Content-Type': 'application/json' },
            data: { name, phone, password },
            success: resolve,
            fail: reject
          })
        })
        if (res.data.code === 200) {
          uni.showToast({ title: '注册成功' })
          setTimeout(() => { this.isRegister = false }, 1000)
        } else {
          uni.showToast({ title: res.data.message || '注册失败', icon: 'none' })
        }
      } catch (e) {
        uni.showToast({ title: '注册异常', icon: 'none' })
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  background-color: #f7f8fa;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40rpx;
  font-family: -apple-system, sans-serif;
}

.auth-box {
  width: 100%;
  max-width: 600rpx;
  background-color: #ffffff;
  border-radius: 16rpx;
  padding: 60rpx 40rpx;
  box-shadow: 0 4rpx 20rpx rgba(0,0,0,0.05);
}

.header-section {
  margin-bottom: 60rpx;
  text-align: center;
}

.brand-name {
  font-size: 40rpx;
  font-weight: bold;
  color: #333;
  display: block;
}

.page-title {
  font-size: 28rpx;
  color: #999;
  margin-top: 10rpx;
  display: block;
}

.auth-tabs {
  display: flex;
  border-bottom: 2rpx solid #eee;
  margin-bottom: 40rpx;
}

.tab-item {
  flex: 1;
  text-align: center;
  padding: 20rpx 0;
  font-size: 30rpx;
  color: #666;
  position: relative;
}

.tab-item.active {
  color: #10b981;
  font-weight: bold;
}

.tab-item.active::after {
  content: "";
  position: absolute;
  bottom: -2rpx;
  left: 20%;
  right: 20%;
  height: 4rpx;
  background-color: #10b981;
}

.form-content {
  display: flex;
  flex-direction: column;
  gap: 30rpx;
}

.input-field {
  position: relative;
  background-color: #f9f9f9;
  border: 2rpx solid #e8e8e8;
  border-radius: 12rpx;
  height: 96rpx;
  display: flex;
  align-items: center;
  padding: 0 28rpx;
  transition: all 0.3s ease;
}

.input-field:focus-within {
  border-color: #10b981;
  background-color: #ffffff;
  box-shadow: 0 0 0 4rpx rgba(16, 185, 129, 0.1);
}

.uni-input {
  width: 100%;
  height: 100%;
  font-size: 30rpx;
  color: #333;
  padding-right: 28rpx;
  box-sizing: border-box;
}

.uni-input::placeholder {
  color: #bfbfbf;
}

.form-actions {
  display: flex;
  justify-content: flex-start;
  font-size: 24rpx;
  color: #999;
}

.check-box {
  display: flex;
  align-items: center;
  gap: 10rpx;
}

.agreement-section {
  display: flex;
  align-items: flex-start;
  gap: 10rpx;
  font-size: 22rpx;
  color: #999;
}

.agreement-text {
  flex: 1;
  line-height: 1.5;
}

.primary-btn {
  width: 100%;
  height: 96rpx;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  border: none;
  border-radius: 12rpx;
  font-size: 34rpx;
  font-weight: bold;
  margin-top: 20rpx;
  box-shadow: 0 4rpx 12rpx rgba(16, 185, 129, 0.3);
  transition: all 0.3s ease;
}

.primary-btn:active {
  transform: translateY(2rpx);
  box-shadow: 0 2rpx 8rpx rgba(16, 185, 129, 0.3);
}

.primary-btn::after {
  border: none;
}

.footer-note {
  margin-top: 60rpx;
  font-size: 20rpx;
  color: #ccc;
}
</style>