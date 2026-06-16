<template>
  <view class="profile-edit-container">
    <custom-navbar title="编辑个人信息" :show-back="true" />

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
        <!-- 基本信息 -->
        <view class="form-group-title">基本信息</view>

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
              {{ usernameAvailable ? '✓ 可用' : '✗ 已被使用' }}
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

        <!-- 检修岗位信息 -->
        <view class="form-group-title">检修岗位信息</view>

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
          <text class="form-label">资质证书</text>
          <input
            v-model="formData.certifications"
            class="form-input"
            placeholder="如: 电工证、高压作业证"
            maxlength="100"
          />
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
        employee_id: '',
        department: '',
        position: '',
        specialty: '',
        work_years: '',
        skill_level: '',
        certifications: '',
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
            employee_id: user.employee_id || '',
            department: user.department || '',
            position: user.position || '',
            specialty: user.specialty || '',
            work_years: user.work_years || user.height || '',
            skill_level: user.skill_level || '',
            certifications: user.certifications || '',
            bio: user.bio || ''
          }
          this.originalName = this.formData.name
          this.usernameAvailable = null
        }
      } catch (error) {
        console.error('加载用户资料失败:', error)
        uni.showToast({ title: '加载失败', icon: 'none' })
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
        this.usernameAvailable = res.code === 200 ? res.data.available : false
      } catch (e) {
        this.usernameAvailable = null
      } finally {
        this.checkingUsername = false
      }
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
        const baseURL = getBaseURL('tuantuan')
        const uploadRes = await new Promise((resolve, reject) => {
          uni.uploadFile({
            url: `${baseURL}/api/user/avatar`,
            filePath: filePath,
            name: 'avatar',
            header: {
              'Authorization': `Bearer ${uni.getStorageSync('token')}`
            },
            success: (res) => {
              try { resolve(JSON.parse(res.data)) } catch (e) { reject(e) }
            },
            fail: (err) => reject(err)
          })
        })
        uni.hideLoading()
        if (uploadRes.code === 200) {
          this.formData.avatar = uploadRes.data.avatar
          this.avatarPreview = null
          uni.showToast({ title: '上传成功', icon: 'success' })
        } else {
          this.avatarPreview = null
          uni.showToast({ title: uploadRes.message || '上传失败', icon: 'none' })
        }
      } catch (error) {
        uni.hideLoading()
        this.avatarPreview = null
        uni.showToast({ title: '上传失败', icon: 'none' })
      }
    },

    async handleSave() {
      if (!this.validateForm()) return

      const normalizedName = this.formData.name.trim()
      if (normalizedName !== (this.originalName || '').trim()) {
        await this.checkUsernameAvailability()
      }
      if (this.usernameAvailable === false) {
        uni.showToast({ title: '用户名已被使用', icon: 'none' })
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
          employee_id: this.formData.employee_id,
          department: this.formData.department,
          position: this.formData.position,
          specialty: this.formData.specialty,
          work_years: this.formData.work_years,
          skill_level: this.formData.skill_level,
          certifications: this.formData.certifications,
          bio: this.formData.bio
        })

        if (res.code === 200) {
          uni.hideLoading()
          uni.showToast({ title: '保存成功', icon: 'success' })

          // 同步到本地存储
          const user = uni.getStorageSync('user') || {}
          uni.setStorageSync('user', {
            ...user,
            name: normalizedName,
            avatar: this.formData.avatar,
            gender: this.formData.gender,
            age: this.formData.age,
            employee_id: this.formData.employee_id,
            department: this.formData.department,
            position: this.formData.position,
            specialty: this.formData.specialty,
            work_years: this.formData.work_years,
            skill_level: this.formData.skill_level,
            certifications: this.formData.certifications,
            bio: this.formData.bio
          })

          this.loading = false
          this.originalName = normalizedName
          this.usernameAvailable = true
          uni.$emit('profile-updated', user)

          setTimeout(() => uni.navigateBack(), 1500)
        } else {
          uni.hideLoading()
          this.loading = false
          uni.showToast({ title: res.message || '保存失败', icon: 'none' })
        }
      } catch (error) {
        uni.hideLoading()
        this.loading = false
        uni.showToast({ title: '保存失败', icon: 'none' })
      }
    },

    handleCancel() {
      uni.navigateBack()
    },

    validateForm() {
      if (!this.formData.name || this.formData.name.trim().length < 2) {
        uni.showToast({ title: '姓名至少2个字符', icon: 'none' })
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
.profile-edit-container {
  min-height: 100vh;
  background: linear-gradient(180deg, #ecfdf5 0%, #f0fdf4 30%, #f7f8fa 100%);
  padding: calc(var(--status-bar-height) + 160rpx) 32rpx 60rpx 32rpx;
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
}
.avatar { width: 100%; height: 100%; }
.avatar-mask {
  position: absolute;
  bottom: 0; left: 0; right: 0;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.6) 0%, transparent 100%);
  padding: 20rpx 0 12rpx;
  display: flex;
  align-items: flex-end;
  justify-content: center;
}
.avatar-mask-text { color: white; font-size: 22rpx; font-weight: 600; }
.avatar-preview {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
}
.preview-image { width: 100%; height: 100%; }
.avatar-tips {
  margin-top: 20rpx;
  font-size: 22rpx;
  color: #9ca3af;
  text-align: center;
}

.divider {
  height: 2rpx;
  background: linear-gradient(90deg, transparent 0%, #e5e7eb 20%, #e5e7eb 80%, transparent 100%);
  margin: 0 40rpx;
}

.form-section { padding: 40rpx 48rpx; }
.form-group-title {
  font-size: 28rpx;
  font-weight: 800;
  color: #2563eb;
  margin-bottom: 24rpx;
  margin-top: 8rpx;
  padding-left: 16rpx;
  border-left: 6rpx solid #2563eb;
}
.form-group-title:first-child { margin-top: 0; }
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
  letter-spacing: 2rpx;
}
.save-btn:active { transform: translateY(2rpx); }
.save-btn::after { border: none; }
.cancel-btn {
  width: 100%;
  height: 88rpx;
  background: transparent;
  color: #9ca3af;
  border: none;
  border-radius: 20rpx;
  font-size: 28rpx;
  font-weight: 600;
}
.cancel-btn:active { color: #6b7280; background: #f9fafb; }
.cancel-btn::after { border: none; }
</style>
