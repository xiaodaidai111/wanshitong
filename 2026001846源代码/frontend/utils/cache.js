class CacheManager {
  constructor() {
    this.cache = new Map()
    this.cacheConfig = {
      user: { ttl: 3600000 },
      indicators: { ttl: 900000 },
      panorama: { ttl: 900000 },
      dietPlan: { ttl: 1800000 },
      achievements: { ttl: 1800000 }
    }
  }

  set(key, value, ttl = 300000) {
    const item = {
      value,
      timestamp: Date.now(),
      ttl
    }
    this.cache.set(key, item)
    
    try {
      uni.setStorageSync(key, JSON.stringify(item))
    } catch (e) {
      console.warn('缓存存储失败:', e)
    }
  }

  get(key) {
    let item = this.cache.get(key)
    
    if (!item) {
      try {
        const stored = uni.getStorageSync(key)
        if (stored) {
          item = JSON.parse(stored)
          this.cache.set(key, item)
        }
      } catch (e) {
        console.warn('缓存读取失败:', e)
      }
    }
    
    if (!item) {
      return null
    }
    
    const now = Date.now()
    if (now - item.timestamp > item.ttl) {
      this.remove(key)
      return null
    }
    
    return item.value
  }

  remove(key) {
    this.cache.delete(key)
    try {
      uni.removeStorageSync(key)
    } catch (e) {
      console.warn('缓存删除失败:', e)
    }
  }

  clear() {
    this.cache.clear()
    try {
      uni.clearStorageSync()
    } catch (e) {
      console.warn('缓存清空失败:', e)
    }
  }

  clearExpired() {
    const now = Date.now()
    for (const [key, item] of this.cache.entries()) {
      if (now - item.timestamp > item.ttl) {
        this.remove(key)
      }
    }
  }

  setUserData(data) {
    this.set('user_profile', data, this.cacheConfig.user.ttl)
  }

  getUserData() {
    return this.get('user_profile')
  }

  setIndicators(data) {
    this.set('user_indicators', data, this.cacheConfig.indicators.ttl)
  }

  getIndicators() {
    return this.get('user_indicators')
  }

  setPanorama(data) {
    this.set('user_panorama', data, this.cacheConfig.panorama.ttl)
  }

  getPanorama() {
    return this.get('user_panorama')
  }

  setDietPlan(data) {
    this.set('user_diet_plan', data, this.cacheConfig.dietPlan.ttl)
  }

  getDietPlan() {
    return this.get('user_diet_plan')
  }

  setAchievements(data) {
    this.set('user_achievements', data, this.cacheConfig.achievements.ttl)
  }

  getAchievements() {
    return this.get('user_achievements')
  }

  clearUserData() {
    this.remove('user_profile')
    this.remove('user_indicators')
    this.remove('user_panorama')
    this.remove('user_diet_plan')
    this.remove('user_achievements')
  }
}

export default new CacheManager()
