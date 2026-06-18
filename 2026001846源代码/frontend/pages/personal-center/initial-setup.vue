<template>
  <view class="initial-setup-container">
    <optimized-navbar title="初始设置" :show-back="false" />

    <view class="main-card">
      <view class="welcome-section">
        <view class="welcome-icon-wrap">
          <text class="welcome-icon">🔧</text>
        </view>
        <text class="welcome-title">欢迎来到一修</text>
        <text class="welcome-subtitle">完善个人信息，加入检修协作团队</text>
      </view>

      <view class="divider"></view>

      <view class="form-section">
        <view class="form-item">
          <text class="form-label">姓名</text>
          <input
            v-model="formData.name"
            class="form-input"
            placeholder="请输入真实姓名"
            maxlength="20"
            @blur="checkUsernameAvailability"
          />
          <view class="input-status" v-if="usernameAvailable !== null">
            <text :class="usernameAvailable ? 'status-success' : 'status-error'">
              {{ usernameAvailable ? '可用' : '已被使用' }}
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
            <text class="form-label">工号</text>
            <input
              v-model="formData.employee_id"
              class="form-input"
              placeholder="如: MX-2026-001"
              maxlength="20"
            />
          </view>
        </view>

        <view class="form-item">
          <text class="form-label">所属部门</text>
          <input
            v-model="formData.department"
            class="form-input"
            placeholder="如: 电气检修部"
            maxlength="30"
          />
        </view>

        <view class="form-item">
          <text class="form-label">岗位</text>
          <input
            v-model="formData.position"
            class="form-input"
            placeholder="如: 电气检修、发动机检修、质检验收"
            maxlength="30"
          />
        </view>

        <view class="form-item">
          <text class="form-label">擅长方向</text>
          <input
            v-model="formData.specialty"
            class="form-input"
            placeholder="如: 配电柜、温升异常、端子排查"
            maxlength="50"
          />
        </view>

        <view class="form-row">
          <view class="form-item form-item-half">
            <text class="form-label">检修工龄 (年)</text>
            <input
              v-model="formData.work_years"
              class="form-input"
              placeholder="如: 5"
              type="number"
              maxlength="2"
            />
          </view>
          <view class="form-item form-item-half">
            <text class="form-label">技能等级</text>
            <input
              v-model="formData.skill_level"
              class="form-input"
              placeholder="如: 高级技师"
              maxlength="20"
            />
          </view>
        </view>

        <view class="form-item">
          <text class="form-label">个人简介</text>
          <textarea
            v-model="formData.bio"
            class="form-textarea"
            placeholder="介绍一下自己的检修经验"
            maxlength="200"
          />
          <text class="char-count">{{ (formData.bio || '').length }}/200</text>
        </view>
      </view>

      <view class="divider"></view>

      <view class="action-buttons">
        <button class="complete-btn" :loading="loading" @click="handleComplete">完成设置</button>
        <button class="skip-btn" @click="handleSkip">跳过，稍后完善</button>
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
        employee_id: '',
        department: '',
        position: '',
        specialty: '',
        work_years: '',
        skill_level: '',
        bio: ''
      },
      genderOptions: [
        { label: '男', value: '男' },
        { label: '女', value: '女' }
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
        this.usernameAvailable = res.code === 200 ? res.data.available : false
      } catch (e) {
        this.usernameAvailable = null
      } finally {
        this.checkingUsername = false
      }
    },

    async handleComplete() {
      if (!this.validateForm()) return

      if (this.usernameAvailable === false) {
        uni.showToast({ title: '用户名已被使用', icon: 'none' })
        return
      }

      this.loading = true
      uni.showLoading({ title: '保存中...' })

      try {
        const res = await request.put('/api/user/profile', {
          name: this.formData.name,
          gender: this.formData.gender,
          age: this.formData.age,
          employee_id: this.formData.employee_id,
          department: this.formData.department,
          position: this.formData.position,
          specialty: this.formData.specialty,
          work_years: this.formData.work_years,
          skill_level: this.formData.skill_level,
          bio: this.formData.bio
        })

        if (res.code === 200) {
          const localUser = uni.getStorageSync('user') || {}
          uni.setStorageSync('user', {
            ...localUser,
            name: this.formData.name,
            gender: this.formData.gender,
            age: parseInt(this.formData.age) || null,
            employee_id: this.formData.employee_id,
            department: this.formData.department,
            position: this.formData.position,
            specialty: this.formData.specialty,
            work_years: this.formData.work_years,
            skill_level: this.formData.skill_level,
            bio: this.formData.bio
          })

          cache.setUserData(null) // 清除缓存，下次刷新
          uni.showToast({ title: '设置完成', icon: 'success' })
          uni.$emit('profile-updated')

          setTimeout(() => {
            uni.switchTab({ url: '/pages/personal-center/personal-center' })
          }, 800)
        }
      } catch (error) {
        uni.showToast({ title: '保存失败', icon: 'none' })
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
            uni.switchTab({ url: '/pages/personal-center/personal-center' })
          }
        }
      })
    },

    validateForm() {
      if (!this.formData.name || this.formData.name.trim().length < 2) {
        uni.showToast({ title: '姓名至少2个字', icon: 'none' })
        return false
      }
      if (this.formData.age && (this.formData.age < 1 || this.formData.age > 120)) {
        uni.showToast({ title: '请输入有效年龄', icon: 'none' })
        return false
      }
      if (this.formData.work_years && (this.formData.work_years < 0 || this.formData.work_years > 60)) {
        uni.showToast({ title: '请输入有效工龄', icon: 'none' })
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
}
.main-card {
  width: 100%;
  max-width: 680rpx;
  background: #ffffff;
  border-radius: 40rpx;
  box-shadow: 0 16rpx 48rpx rgba(16, 185, 129, 0.1), 0 4rpx 16rpx rgba(0, 0, 0, 0.04);
  overflow: hidden;
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
}
.welcome-icon { font-size: 60rpx; }
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
.form-section { padding: 40rpx 48rpx; }
.form-item {
  margin-bottom: 36rpx;
  position: relative;
}
.form-item:last-child { margin-bottom: 0; }
.form-row {
  display: flex;
  gap: 24rpx;
  margin-bottom: 36rpx;
}
.form-item-half { flex: 1; margin-bottom: 0; }
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
  box-sizing: border-box;
  line-height: 1.6;
}
.form-textarea:focus {
  border-color: #10b981;
  background: #ffffff;
}
.input-status {
  position: absolute;
  right: 28rpx;
  bottom: -24rpx;
  font-size: 20rpx;
  z-index: 10;
}
.status-success { color: #10b981; }
.status-error { color: #ef4444; }
.char-count {
  position: absolute;
  right: 28rpx;
  bottom: -30rpx;
  font-size: 22rpx;
  color: #9ca3af;
}
.radio-group { display: flex; gap: 20rpx; }
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
  letter-spacing: 2rpx;
}
.complete-btn:active { transform: translateY(2rpx); }
.complete-btn::after { border: none; }
.skip-btn {
  width: 100%;
  height: 88rpx;
  background: transparent;
  color: #9ca3af;
  border: none;
  border-radius: 20rpx;
  font-size: 28rpx;
  font-weight: 600;
}
.skip-btn:active { color: #6b7280; background: #f9fafb; }
.skip-btn::after { border: none; }
</style>
