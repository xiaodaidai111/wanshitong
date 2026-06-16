<template>
  <view class="achievements-container">
    <custom-navbar title="成就系统" :show-back="true" />
    <view class="content">
      <view class="stats-section">
        <view class="stat-card">
          <text class="stat-value">{{ unlockedCount }}</text>
          <text class="stat-label">已解锁</text>
        </view>
        <view class="stat-card">
          <text class="stat-value">{{ totalCount }}</text>
          <text class="stat-label">总成就</text>
        </view>
        <view class="stat-card">
          <text class="stat-value">{{ progress }}%</text>
          <text class="stat-label">完成率</text>
        </view>
      </view>

      <view class="achievements-list">
        <view
          v-for="achievement in achievements"
          :key="achievement.id"
          class="achievement-item"
          :class="{ unlocked: achievement.unlocked }"
          @click="handleAchievementClick(achievement)"
        >
          <view class="achievement-icon">
            <text class="icon-text">{{ achievement.icon }}</text>
          </view>
          <view class="achievement-info">
            <view class="achievement-header">
              <text class="achievement-name">{{ achievement.name }}</text>
              <view class="achievement-status" :class="{ unlocked: achievement.unlocked }">
                <text>{{ achievement.unlocked ? '已解锁' : '未解锁' }}</text>
              </view>
            </view>
            <text class="achievement-desc">{{ achievement.description }}</text>
            <text class="achievement-date" v-if="achievement.unlocked">
              解锁时间：{{ achievement.unlockedAt }}
            </text>
          </view>
          <view class="achievement-arrow">
            <text class="arrow-icon">→</text>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import request from '../../utils/request.js'
import CustomNavbar from '../../src/components/custom-navbar/custom-navbar.vue'

export default {
  components: {
    CustomNavbar
  },
  data() {
    return {
      achievements: [],
      loading: true
    }
  },

  computed: {
    totalCount() {
      return this.achievements.length
    },
    unlockedCount() {
      return this.achievements.filter(a => a.unlocked).length
    },
    progress() {
      if (this.totalCount === 0) return 0
      return Math.round((this.unlockedCount / this.totalCount) * 100)
    }
  },

  async onLoad() {
    await this.loadAchievements()
  },

  methods: {
    async loadAchievements() {
      this.loading = true
      try {
        const res = await request.get('/api/health/achievements')

        if (res.code === 200) {
          this.achievements = res.data.achievements || []
        }
      } catch (error) {
        console.error('加载成就失败:', error)
        uni.showToast({
          title: '加载失败',
          icon: 'none'
        })
      } finally {
        this.loading = false
      }
    },

    handleBack() {
      uni.navigateBack()
    },

    handleAchievementClick(achievement) {
      uni.showModal({
        title: achievement.name,
        content: achievement.description + (achievement.unlocked ? `\n\n解锁时间：${achievement.unlockedAt}` : ''),
        showCancel: false
      })
    }
  }
}
</script>

<style scoped>
.achievements-container {
  min-height: 100vh;
  background: #f0f4f8;
  padding-top: calc(var(--status-bar-height) + 140rpx);
}

.content {
  padding: 30rpx;
}

.stats-section {
  display: flex;
  gap: 20rpx;
  margin-bottom: 30rpx;
}

.stat-card {
  flex: 1;
  background: white;
  border-radius: 24rpx;
  padding: 30rpx 20rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.04);
}

.stat-value {
  font-size: 48rpx;
  font-weight: 800;
  color: #4facfe;
  margin-bottom: 10rpx;
}

.stat-label {
  font-size: 24rpx;
  color: #64748b;
  font-weight: 500;
}

.achievements-list {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.achievement-item {
  background: white;
  border-radius: 24rpx;
  padding: 30rpx;
  display: flex;
  align-items: center;
  gap: 20rpx;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.03);
  transition: all 0.3s ease;
}

.achievement-item:active {
  transform: scale(0.98);
}

.achievement-item.unlocked {
  background: linear-gradient(135deg, #fffbeb, #fef3c7);
  border: 2rpx solid #fbbf24;
}

.achievement-item:not(.unlocked) {
  opacity: 0.55;
  filter: grayscale(0.8);
}

.achievement-icon {
  width: 100rpx;
  height: 100rpx;
  border-radius: 50%;
  background: #f1f5f9;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.unlocked .achievement-icon {
  background: linear-gradient(135deg, #fbbf24, #f59e0b);
  box-shadow: 0 6rpx 16rpx rgba(245, 158, 11, 0.3);
}

.icon-text {
  font-size: 48rpx;
}

.achievement-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 10rpx;
}

.achievement-header {
  display: flex;
  align-items: center;
  gap: 15rpx;
}

.achievement-name {
  font-size: 30rpx;
  font-weight: 700;
  color: #1e293b;
}

.achievement-status {
  padding: 4rpx 16rpx;
  border-radius: 20rpx;
  font-size: 20rpx;
  font-weight: 600;
  background: #f1f5f9;
  color: #94a3b8;
}

.achievement-status.unlocked {
  background: linear-gradient(135deg, #fbbf24, #f59e0b);
  color: white;
}

.achievement-desc {
  font-size: 24rpx;
  color: #64748b;
  line-height: 1.5;
}

.achievement-date {
  font-size: 22rpx;
  color: #94a3b8;
}

.achievement-arrow {
  width: 40rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.arrow-icon {
  font-size: 32rpx;
  color: #cbd5e1;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
}

.loading-spinner {
  width: 80rpx;
  height: 80rpx;
  border: 4rpx solid #f3f3f3;
  border-top: 4rpx solid #4facfe;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.loading-text {
  margin-top: 30rpx;
  color: #64748b;
  font-size: 28rpx;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>
