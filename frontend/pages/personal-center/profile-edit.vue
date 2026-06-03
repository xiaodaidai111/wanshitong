<template>
  <view class="profile-edit-container">
    <custom-navbar title="编辑资料" :show-back="true" />

    <view class="main-card">
      <view class="avatar-section">
        <view class="avatar-wrapper" @click="handleChooseAvatar">
          <image :src="formData.avatar || '../../static/avatar-1.png'" class="avatar" mode="aspectFill"></image>
          <view class="avatar-mask">
            <text class="avatar-mask-text">更换头像</text>
          </view>
          <view class="avatar-preview" v-if="avatarPreview">
            <image :src="avatarPreview" class="preview-image" mode="aspectFill"></image>
          </view>
        </view>
        <view class="avatar-tips">
          <text>支持 JPG、PNG、GIF 格式，大小不超过 5MB</text>
        </view>
      </view>

      <view class="divider"></view>

      <view class="form-section">
        <view class="form-item">
          <viewtext class="form-label">用户名</viewtext>
          <input
            v-model="formData.name"
            class="form-input"
            placeholder="请输入用户名"
            maxlength="20"
            @blur="checkUsernameAvailability"
          />
          <view class="input-status" v-if="usernameAvailable !== null">
            <text :class="usernameAvailable ? 'status-success' : 'status-error'">
              {{ usernameAvailable ? '√ 用户名可用' : '× 用户名已被使用' }}
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
        <button class="save-btn" :loading="loading" @click="handleSave">保存修改</button>
        <button class="cancel-btn" @click="handleCancel">取消</button>
      </view>
    </view>
  </view>
</template>

<script>
import request from '../../utils/request.js'
import { getBaseURL } from '../../utils/request.js'
import CustomNavbar from '../../src/components/custom-navbar/custom-navbar.vue'

export default {
  components: {
    CustomNavbar
  },
  data() {
    return {
      formData: {
        name: '',
        avatar: '',
        gender: '男',
        age: '',
        height: '',
        weight: '',
        bio: ''
      },
      genderOptions: [
        { label: '男', value: '男' },
        { label: '女', value: '女' }
      ],
      loading: false,
      avatarPreview: null,
      originalName: '',
      checkingUsername: false,
      usernameAvailable: null
    }
  },

  async onLoad() {
    await this.loadUserProfile()
  },

  methods: {
    async loadUserProfile() {
      try {
        const res = await request.get('/api/user/profile')

        if (res.code === 200) {
          const user = res.data.user
          this.formData = {
            name: user.name || '',
            avatar: user.avatar || '',
            gender: user.gender || '男',
            age: user.age || '',
            height: user.height || '',
            weight: user.weight || '',
            bio: user.bio || ''
          }
          this.originalName = this.formData.name
          this.usernameAvailable = null
        }
      } catch (error) {
        console.error('加载用户资料失败:', error)
        uni.showToast({
          title: '加载失败',
          icon: 'none'
        })
      }
    },

    async checkUsernameAvailability() {
      const name = this.formData.name.trim()
      if (name.length < 2) {
        this.usernameAvailable = null
        return
      }

      if (name === (this.originalName || '').trim()) {
        this.usernameAvailable = true
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

    handleBack() {
      uni.navigateBack()
    },

    handleChooseAvatar() {
      uni.chooseImage({
        count: 1,
        sizeType: ['compressed'],
        sourceType: ['album', 'camera'],
        success: (res) => {
          const tempFilePath = res.tempFilePaths[0]

          this.avatarPreview = tempFilePath

          this.uploadAvatar(tempFilePath)
        }
      })
    },

    async uploadAvatar(filePath) {
      uni.showLoading({ title: '上传中...' })

      try {
        const uploadRes = await new Promise((resolve, reject) => {
          const baseURL = getBaseURL('tuantuan')
          uni.uploadFile({
            url: `${baseURL}/api/user/avatar`,
            filePath: filePath,
            name: 'avatar',
            header: {
              'Authorization': `Bearer ${uni.getStorageSync('token')}`
            },
            success: (res) => {
              try {
                const data = JSON.parse(res.data)
                resolve(data)
              } catch (e) {
                reject(e)
              }
            },
            fail: (err) => {
              reject(err)
            }
          })
        })

        uni.hideLoading()

        if (uploadRes.code === 200) {
          this.formData.avatar = uploadRes.data.avatar
          this.avatarPreview = null
          uni.showToast({
            title: '上传成功',
            icon: 'success'
          })
        } else {
          this.avatarPreview = null
          uni.showToast({
            title: uploadRes.message || '上传失败',
            icon: 'none'
          })
        }
      } catch (error) {
        uni.hideLoading()
        console.error('上传头像失败:', error)
        this.avatarPreview = null
        uni.showToast({
          title: '上传失败',
          icon: 'none'
        })
      }
    },

    async handleSave() {
      if (!this.validateForm()) {
        return
      }

      const normalizedName = this.formData.name.trim()
      if (normalizedName !== (this.originalName || '').trim()) {
        await this.checkUsernameAvailability()
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
          name: normalizedName,
          avatar: this.formData.avatar,
          gender: this.formData.gender,
          age: this.formData.age,
          height: this.formData.height,
          weight: this.formData.weight,
          bio: this.formData.bio
        })

        if (res.code === 200) {
          uni.hideLoading()
          uni.showToast({
            title: '保存成功',
            icon: 'success'
          })

          const user = uni.getStorageSync('user') || {}
          user.name = normalizedName
          user.avatar = this.formData.avatar
          user.gender = this.formData.gender
          user.age = this.formData.age
          user.height = this.formData.height
          user.weight = this.formData.weight
          user.bio = this.formData.bio
          uni.setStorageSync('user', user)

          this.loading = false
          this.originalName = normalizedName
          this.usernameAvailable = true
          // 通知首页和个人中心：本地用户资料已经更新，可以实时回填展示
          uni.$emit('profile-updated', user)

          setTimeout(() => {
            uni.navigateBack()
          }, 1500)
        } else {
          uni.hideLoading()
          this.loading = false
          uni.showToast({
            title: res.message || '保存失败',
            icon: 'none'
          })
        }
      } catch (error) {
        uni.hideLoading()
        this.loading = false
        console.error('保存资料失败:', error)
        uni.showToast({
          title: '保存失败',
          icon: 'none'
        })
      }
    },

    handleCancel() {
      uni.navigateBack()
    },

    validateForm() {
      if (!this.formData.name || this.formData.name.trim().length < 2) {
        uni.showToast({
          title: '用户名至少2个字符',
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
.profile-edit-container {
  min-height: 100vh;
  background: linear-gradient(180deg, #ecfdf5 0%, #f0fdf4 30%, #f7f8fa 100%);
  padding: calc(var(--status-bar-height) + 160rpx) 32rpx 60rpx 32rpx;
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

.avatar-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 56rpx 48rpx 40rpx;
}

.avatar-wrapper {
  position: relative;
  width: 180rpx;
  height: 180rpx;
  border-radius: 50%;
  overflow: hidden;
  box-shadow: 0 8rpx 32rpx rgba(16, 185, 129, 0.2);
  border: 6rpx solid #d1fae5;
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

.avatar {
  width: 100%;
  height: 100%;
}

.avatar-mask {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.6) 0%, transparent 100%);
  padding: 20rpx 0 12rpx;
  display: flex;
  align-items: flex-end;
  justify-content: center;
}

.avatar-mask-text {
  color: white;
  font-size: 22rpx;
  font-weight: 600;
}

.avatar-preview {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
}

.preview-image {
  width: 100%;
  height: 100%;
}

.avatar-tips {
  margin-top: 20rpx;
  font-size: 22rpx;
  color: #9ca3af;
  text-align: center;
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

.form-input-disabled {
  background: #f3f4f6;
  color: #9ca3af;
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

.form-hint {
  display: block;
  font-size: 22rpx;
  color: #9ca3af;
  margin-top: 10rpx;
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

.save-btn {
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

.save-btn:active {
  transform: translateY(2rpx);
  box-shadow: 0 4rpx 12rpx rgba(16, 185, 129, 0.25);
}

.save-btn::after {
  border: none;
}

.cancel-btn {
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

.cancel-btn:active {
  color: #6b7280;
  background: #f9fafb;
}

.cancel-btn::after {
  border: none;
}

@media screen and (max-width: 375px) {
  .profile-edit-container {
    padding: calc(var(--status-bar-height) + 100rpx) 24rpx 40rpx 24rpx;
  }

  .avatar-section {
    padding: 40rpx 32rpx 32rpx;
  }

  .form-section {
    padding: 32rpx;
  }

  .action-buttons {
    padding: 8rpx 32rpx 40rpx;
  }
}

@media screen and (min-width: 768px) {
  .profile-edit-container {
    padding-top: calc(var(--status-bar-height) + 140rpx);
  }

  .main-card {
    max-width: 600rpx;
  }
}
</style>
