<template>
  <view class="auth-page">
    <view class="auth-box">
      <!-- 品牌标题 (与登录页一致) -->
      <view class="header-section">
        <text class="brand-name">膳食全周期系统</text>
        <text class="page-title">加入健康社区</text>
      </view>

      <!-- 注册表单 -->
      <view class="form-content">
        <view class="input-field">
          <input class="uni-input" v-model="form.name" type="text" placeholder="请输入昵称" />
        </view>
        <view class="input-field">
          <input class="uni-input" v-model="form.phone" type="number" maxlength="11" placeholder="请输入手机号" />
        </view>
        <view class="input-field">
          <input class="uni-input" v-model="form.password" type="password" placeholder="请设置密码(至少6位)" />
        </view>
        <view class="input-field">
          <input class="uni-input" v-model="form.confirmPassword" type="password" placeholder="请再次输入密码" />
        </view>
        
        <view class="agreement-section">
          <checkbox :checked="agreed" @click="agreed = !agreed" color="#10b981" style="transform:scale(0.7)" />
          <text class="agreement-text">同意《用户服务协议》与《个人隐私政策》</text>
        </view>
        
        <button class="primary-btn" :loading="loading" @click="onRegister">立即注册</button>
        
        <view class="back-login" @click="goLogin">
          <text>已有账号？去登录</text>
        </view>
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
      loading: false,
      agreed: false,
      form: {
        name: '',
        phone: '',
        password: '',
        confirmPassword: ''
      }
    }
  },
  methods: {
    goLogin() {
      uni.navigateTo({ url: '/pages/user/login' })
    },
    async onRegister() {
      if (!this.agreed) {
        uni.showToast({ title: '请先阅读并同意协议', icon: 'none' })
        return
      }
      const { name, phone, password, confirmPassword } = this.form
      if (!name || !phone || !password) {
        uni.showToast({ title: '填写信息不完整', icon: 'none' })
        return
      }
      if (password !== confirmPassword) {
        uni.showToast({ title: '密码校验失败', icon: 'none' })
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
          uni.showToast({ title: '注册完成' })
          setTimeout(() => this.goLogin(), 1000)
        } else {
          uni.showToast({ title: res.data.message || '注册失败', icon: 'none' })
        }
      } catch (e) {
        uni.showToast({ title: '网络连接超时', icon: 'none' })
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

.back-login {
  text-align: center;
  margin-top: 20rpx;
  font-size: 26rpx;
  color: #10b981;
}

.footer-note {
  margin-top: 60rpx;
  font-size: 20rpx;
  color: #ccc;
}
</style>