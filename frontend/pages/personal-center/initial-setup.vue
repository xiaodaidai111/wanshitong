<template>
  <view class="initial-setup-container">
    <optimized-navbar title="初始设置" :show-back="false" />

    <view class="main-card">
      <view class="welcome-section">
        <view class="welcome-icon-wrap">
          <text class="welcome-icon">🥗</text>
        </view>
        <text class="welcome-title">欢迎来到膳食全周期系统</text>
        <text class="welcome-subtitle">完善个人信息，开启健康之旅</text>
      </view>

      <view class="divider"></view>

      <view class="form-section">
        <view class="form-item">
          <text class="form-label">用户名</text>
          <input
            v-model="formData.name"
            class="form-input"
            placeholder="请输入用户名"
            maxlength="20"
            @blur="checkUsernameAvailability"
          />
          <view class="input-status" v-if="usernameAvailable !== null">
            <text :class="usernameAvailable ? 'status-success' : 'status-error'">
              {{ usernameAvailable ? '用户名可用' : '用户名已被使用' }}
            </text>
          </view>
        </view>

        <view class="form-item">
          <text class="form-label">性别</text>
          <view class="radio-group">
            <view
              v-for="item in genderOptions"
              :key="item.value"
              class="radio-item"
              :class="{ active: formData.gender === item.value }"
              @click="formData.gender = item.value"
            >
              <text>{{ item.label }}</text>
            </view>
          </view>
        </view>

        <view class="form-row">
          <view class="form-item form-item-half">
            <text class="form-label">年龄</text>
            <input
              v-model="formData.age"
              class="form-input"
              placeholder="请输入年龄"
              type="number"
              maxlength="3"
            />
          </view>

          <view class="form-item form-item-half">
            <text class="form-label">身高 (cm)</text>
            <input
              v-model="formData.height"
              class="form-input"
              placeholder="请输入身高"
              type="digit"
              maxlength="3"
            />
          </view>
        </view>

        <view class="form-item">
          <text class="form-label">体重 (kg)</text>
          <input
            v-model="formData.weight"
            class="form-input"
            placeholder="请输入体重"
            type="digit"
            maxlength="3"
          />
        </view>

        <view class="form-item">
          <text class="form-label">个人简介</text>
          <textarea
            v-model="formData.bio"
            class="form-textarea"
            placeholder="介绍一下自己吧"
            maxlength="100"
          />
          <text class="char-count">{{ formData.bio.length }}/100</text>
        </view>
      </view>

      <view class="divider"></view>

      <view class="action-buttons">
        <button class="complete-btn" :loading="loading" @click="handleComplete">完成设置</button>
        <button class="skip-btn" @click="handleSkip">跳过，稍后完成</button>
      </view>
    </view>
  </view>
</template>

<script>
import request from '../../utils/request.js'
import cache from '../../utils/cache.js'
import OptimizedNavbar from '../../src/components/optimized-navbar/optimized-navbar.vue'

export default {
  components: {
    OptimizedNavbar
  },
  data() {
    return {
      formData: {
        name: '',
        gender: '男',
        age: '',
        height: '',
        weight: '',
        bio: ''
      },
      genderOptions: [
        { label: '男', value: 'male' },
        { label: '女', value: 'female' }
      ],
      loading: false,
      checkingUsername: false,
      usernameAvailable: null
    }
  },

  methods: {
    async checkUsernameAvailability() {
      const name = this.formData.name.trim()
      if (name.length < 2) {
        this.usernameAvailable = null
        return
      }

      this.checkingUsername = true
      try {
        const res = await request.post('/api/auth/check-username', { name })

        if (res.code === 200) {
          this.usernameAvailable = res.data.available
        } else {
          this.usernameAvailable = false
        }
      } catch (e) {
        console.error('检查用户名失败:', e)
        this.usernameAvailable = null
      } finally {
        this.checkingUsername = false
      }
    },

    async handleComplete() {
      if (!this.validateForm()) {
        return
      }

      if (this.usernameAvailable === false) {
        uni.showToast({
          title: '用户名已被使用',
          icon: 'none'
        })
        return
      }

      this.loading = true
      uni.showLoading({ title: '保存中...' })

      try {
        const res = await request.put('/api/user/profile', {
          name: this.formData.name,
          gender: this.formData.gender,
          age: this.formData.age,
          height: this.formData.height,
          weight: this.formData.weight,
          bio: this.formData.bio
        })

        if (res.code === 200) {
          const userData = {
            profile: {
              id: uni.getStorageSync('user')?.id,
              name: this.formData.name,
              avatar: uni.getStorageSync('user')?.avatar,
              gender: this.formData.gender,
              age: parseInt(this.formData.age) || null,
              height: parseFloat(this.formData.height) || null,
              weight: parseFloat(this.formData.weight) || null,
              bio: this.formData.bio,
              level: 1,
              level_name: '新手'
            },
            panorama: {
              dimensions: {
                nutrition: 60,
                diversity: 55,
                sleep: 62,
                exercise: 58,
                environment: 57
              },
              trend: 0
            },
            dietPlan: { name: '均衡膳食计划', daysCompleted: 0, totalDays: 7 },
            dietDetail: { calories: 1800, protein: 65, carbs: 250, fat: 55 },
            achievements: [],
            recent_activities: []
          }
          cache.setUserData(userData)

          const localUser = uni.getStorageSync('user') || {}
          localUser.name = this.formData.name
          localUser.gender = this.formData.gender
          localUser.age = parseInt(this.formData.age) || null
          localUser.height = parseFloat(this.formData.height) || null
          localUser.weight = parseFloat(this.formData.weight) || null
          uni.setStorageSync('user', localUser)

          uni.showToast({
            title: '设置完成',
            icon: 'success'
          })

          uni.$emit('profile-updated')

          setTimeout(() => {
            uni.switchTab({
              url: '/pages/personal-center/personal-center'
            })
          }, 800)
        }
      } catch (error) {
        console.error('保存资料失败:', error)
        uni.showToast({
          title: '保存失败',
          icon: 'none'
        })
      } finally {
        this.loading = false
        uni.hideLoading()
      }
    },

    handleSkip() {
      uni.showModal({
        title: '提示',
        content: '您可以稍后在个人中心完善信息',
        success: (res) => {
          if (res.confirm) {
            uni.switchTab({
              url: '/pages/personal-center/personal-center'
            })
          }
        }
      })
    },

    validateForm() {
      if (!this.formData.name || this.formData.name.trim().length < 2) {
        uni.showToast({
          title: '用户名至少2个字',
          icon: 'none'
        })
        return false
      }

      if (this.formData.age && (this.formData.age < 1 || this.formData.age > 120)) {
        uni.showToast({
          title: '请输入有效年龄',
          icon: 'none'
        })
        return false
      }

      if (this.formData.height && (this.formData.height < 50 || this.formData.height > 250)) {
        uni.showToast({
          title: '请输入有效身高',
          icon: 'none'
        })
        return false
      }

      if (this.formData.weight && (this.formData.weight < 20 || this.formData.weight > 200)) {
        uni.showToast({
          title: '请输入有效体重',
          icon: 'none'
        })
        return false
      }

      return true
    }
  }
}
</script>

<style scoped>
.initial-setup-container {
  min-height: 100vh;
  background: linear-gradient(180deg, #ecfdf5 0%, #f0fdf4 30%, #f7f8fa 100%);
  padding: calc(var(--status-bar-height) + 120rpx) 32rpx 60rpx 32rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  animation: fadeIn 0.6s ease-out;
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

.main-card {
  width: 100%;
  max-width: 680rpx;
  background: #ffffff;
  border-radius: 40rpx;
  box-shadow: 0 16rpx 48rpx rgba(16, 185, 129, 0.1), 0 4rpx 16rpx rgba(0, 0, 0, 0.04);
  overflow: hidden;
  animation: slideInUp 0.7s cubic-bezier(0.16, 1, 0.3, 1) 0.1s both;
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(40rpx);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.welcome-section {
  text-align: center;
  padding: 60rpx 48rpx 40rpx;
}

.welcome-icon-wrap {
  width: 120rpx;
  height: 120rpx;
  background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
  border-radius: 36rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 28rpx;
  box-shadow: 0 8rpx 24rpx rgba(16, 185, 129, 0.15);
  animation: scaleIn 0.6s cubic-bezier(0.34, 1.56, 0.64, 1) 0.3s both;
}

@keyframes scaleIn {
  from {
    opacity: 0;
    transform: scale(0.6);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.welcome-icon {
  font-size: 60rpx;
}

.welcome-title {
  font-size: 40rpx;
  font-weight: 800;
  color: #065f46;
  display: block;
  margin-bottom: 12rpx;
  letter-spacing: 1rpx;
  line-height: 1.4;
}

.welcome-subtitle {
  font-size: 26rpx;
  color: #6b7280;
  display: block;
  font-weight: 500;
}

.divider {
  height: 2rpx;
  background: linear-gradient(90deg, transparent 0%, #e5e7eb 20%, #e5e7eb 80%, transparent 100%);
  margin: 0 40rpx;
}

.form-section {
  padding: 40rpx 48rpx;
}

.form-item {
  margin-bottom: 36rpx;
  position: relative;
}

.form-item:last-child {
  margin-bottom: 0;
}

.form-row {
  display: flex;
  gap: 24rpx;
  margin-bottom: 36rpx;
}

.form-item-half {
  flex: 1;
  margin-bottom: 0;
}

.form-label {
  display: block;
  font-size: 26rpx;
  color: #374151;
  margin-bottom: 16rpx;
  font-weight: 700;
  letter-spacing: 0.5rpx;
}

.form-input {
  width: 100%;
  height: 88rpx;
  border: 2rpx solid #e5e7eb;
  border-radius: 20rpx;
  padding: 0 28rpx;
  font-size: 28rpx;
  background: #f9fafb;
  transition: all 0.3s ease;
  box-sizing: border-box;
}

.form-input:focus {
  border-color: #10b981;
  background: #ffffff;
  box-shadow: 0 0 0 6rpx rgba(16, 185, 129, 0.08);
}

.form-textarea {
  width: 100%;
  min-height: 160rpx;
  border: 2rpx solid #e5e7eb;
  border-radius: 20rpx;
  padding: 24rpx 28rpx;
  font-size: 28rpx;
  background: #f9fafb;
  resize: none;
  transition: all 0.3s ease;
  box-sizing: border-box;
  line-height: 1.6;
}

.form-textarea:focus {
  border-color: #10b981;
  background: #ffffff;
  box-shadow: 0 0 0 6rpx rgba(16, 185, 129, 0.08);
}

.input-status {
  position: absolute;
  right: 28rpx;
  bottom: -24rpx;
  font-size: 20rpx;
  z-index: 10;
}

.status-success {
  color: #10b981;
}

.status-error {
  color: #ef4444;
}

.char-count {
  position: absolute;
  right: 28rpx;
  bottom: -30rpx;
  font-size: 22rpx;
  color: #9ca3af;
}

.radio-group {
  display: flex;
  gap: 20rpx;
}

.radio-item {
  flex: 1;
  height: 88rpx;
  border: 2rpx solid #e5e7eb;
  border-radius: 20rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28rpx;
  color: #6b7280;
  background: #f9fafb;
  transition: all 0.3s ease;
  font-weight: 600;
}

.radio-item.active {
  border-color: #10b981;
  background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
  color: #065f46;
  box-shadow: 0 4rpx 12rpx rgba(16, 185, 129, 0.15);
}

.action-buttons {
  padding: 8rpx 48rpx 48rpx;
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.complete-btn {
  width: 100%;
  height: 96rpx;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  border: none;
  border-radius: 20rpx;
  font-size: 32rpx;
  font-weight: 800;
  box-shadow: 0 8rpx 24rpx rgba(16, 185, 129, 0.3);
  transition: all 0.3s ease;
  letter-spacing: 2rpx;
}

.complete-btn:active {
  transform: translateY(2rpx);
  box-shadow: 0 4rpx 12rpx rgba(16, 185, 129, 0.25);
}

.complete-btn::after {
  border: none;
}

.skip-btn {
  width: 100%;
  height: 88rpx;
  background: transparent;
  color: #9ca3af;
  border: none;
  border-radius: 20rpx;
  font-size: 28rpx;
  font-weight: 600;
  transition: all 0.3s ease;
}

.skip-btn:active {
  color: #6b7280;
  background: #f9fafb;
}

.skip-btn::after {
  border: none;
}

@media screen and (max-width: 375px) {
  .initial-setup-container {
    padding: calc(var(--status-bar-height) + 100rpx) 24rpx 40rpx 24rpx;
  }

  .welcome-section {
    padding: 48rpx 32rpx 32rpx;
  }

  .welcome-title {
    font-size: 36rpx;
  }

  .form-section {
    padding: 32rpx;
  }

  .action-buttons {
    padding: 8rpx 32rpx 40rpx;
  }
}

@media screen and (min-width: 768px) {
  .initial-setup-container {
    padding-top: calc(var(--status-bar-height) + 140rpx);
  }

  .main-card {
    max-width: 600rpx;
  }
}
</style>
