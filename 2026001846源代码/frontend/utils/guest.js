import { getBaseURL } from './backend-config.js'

class GuestManager {
  constructor() {
    this.sessionId = null
    this.expiresAt = null
    this.isGuest = false
    this.loadGuestSession()
  }

  loadGuestSession() {
    try {
      const sessionData = uni.getStorageSync('guest_session')
      if (sessionData) {
        const { sessionId, expiresAt } = JSON.parse(sessionData)
        if (new Date(expiresAt) > new Date()) {
          this.sessionId = sessionId
          this.expiresAt = expiresAt
          this.isGuest = true
          console.log('游客会话已加载')
        } else {
          this.clearGuestSession()
        }
      }
    } catch (error) {
      console.error('加载游客会话失败:', error)
      this.clearGuestSession()
    }
  }

  saveGuestSession(sessionId, expiresAt) {
    try {
      const sessionData = JSON.stringify({ sessionId, expiresAt })
      uni.setStorageSync('guest_session', sessionData)
      this.sessionId = sessionId
      this.expiresAt = expiresAt
      this.isGuest = true
      console.log('游客会话已保存')
    } catch (error) {
      console.error('保存游客会话失败:', error)
    }
  }

  clearGuestSession() {
    try {
      uni.removeStorageSync('guest_session')
      this.sessionId = null
      this.expiresAt = null
      this.isGuest = false
      console.log('游客会话已清除')
    } catch (error) {
      console.error('清除游客会话失败:', error)
    }
  }

  async createGuestSession() {
    try {
      const baseURL = getBaseURL('tuantuan')
      const res = await new Promise((resolve, reject) => {
        uni.request({
          url: baseURL + '/api/auth/guest/create',
          method: 'POST',
          data: {
            device_info: {
              platform: uni.getSystemInfoSync().platform,
              system: uni.getSystemInfoSync().system,
              model: uni.getSystemInfoSync().model
            }
          },
          header: { 'Content-Type': 'application/json' },
          success: (r) => resolve(r.data),
          fail: reject
        })
      })

      if (res.code === 200) {
        const { session_id, expires_at } = res.data
        this.saveGuestSession(session_id, expires_at)
        return { success: true, session_id, expires_at }
      } else {
        console.error('创建游客会话失败:', res.message)
        return { success: false, message: res.message }
      }
    } catch (error) {
      console.error('创建游客会话异常:', error)
      return { success: false, message: '网络连接失败' }
    }
  }

  async verifyGuestSession() {
    if (!this.sessionId) {
      return { valid: false }
    }

    try {
      const baseURL = getBaseURL('tuantuan')
      const res = await new Promise((resolve, reject) => {
        uni.request({
          url: baseURL + `/api/auth/guest/verify?session_id=${this.sessionId}`,
          method: 'GET',
          header: { 'Content-Type': 'application/json' },
          success: (r) => resolve(r.data),
          fail: reject
        })
      })

      if (res.code === 200) {
        return { valid: true, ...(res.data || {}) }
      } else {
        this.clearGuestSession()
        return { valid: false }
      }
    } catch (error) {
      console.error('验证游客会话失败:', error)
      this.clearGuestSession()
      return { valid: false }
    }
  }

  async ensureGuestSession() {
    if (this.isGuest) {
      const verification = await this.verifyGuestSession()
      if (verification.valid) {
        return { success: true, session_id: this.sessionId }
      }
    }

    return await this.createGuestSession()
  }

  getSessionId() {
    return this.sessionId
  }

  isGuestUser() {
    return this.isGuest
  }

  getAuthHeader() {
    const token = uni.getStorageSync('token')
    if (token) {
      return { 'Authorization': `Bearer ${token}` }
    }

    if (this.isGuest) {
      return { 'X-Guest-Session': this.sessionId }
    }

    return {}
  }
}

const guestManager = new GuestManager()

export default guestManager
