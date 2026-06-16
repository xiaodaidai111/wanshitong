<template>
  <view class="takeout-assessment">
    <view class="assessment-header">
      <view class="header-icon">🔧</view>
      <view class="header-title">检修质量评估</view>
    </view>

    <view class="scan-section">
      <view class="scan-input-wrapper">
        <view class="scan-icon">📷</view>
        <input 
          type="text" 
          v-model="scanInput"
          placeholder="扫描或输入设备信�?.."
          class="scan-input"
          @confirm="handleScan"
        />
        <view class="scan-btn" @click="handleScan">
          <text class="scan-btn-text">扫描</text>
        </view>
      </view>
    </view>

    <view class="food-detail" v-if="foodData">
      <view class="food-image">
        <view class="image-placeholder">
          <text class="placeholder-icon">🔧</text>
          <text class="placeholder-text">{{ foodData.name }}</text>
        </view>
      </view>

      <view class="health-score-section">
        <view class="score-header">
          <text class="score-label">检修评分</text>
          <text class="score-value" :class="{ 'score-loading': isScoring }">{{ displayScore }}�?/text>
        </view>
        <view class="score-bar">
          <view class="score-fill" :style="{ width: displayScore + '%' }"></view>
          <view class="score-glow" :style="{ left: displayScore + '%' }"></view>
        </view>
        <view class="score-rating">
          <text class="rating-stars">{{ getRatingStars(displayScore) }}</text>
          <text class="rating-text">{{ getRatingText(displayScore) }}</text>
        </view>
        <view class="loading-pulse" v-if="isScoring">
          <view class="pulse-ring"></view>
          <view class="pulse-ring delay-1"></view>
          <view class="pulse-ring delay-2"></view>
        </view>
      </view>

      <view class="nutrition-section">
        <view class="section-title">检修维度分析</view>
        
        <view class="nutrition-item" v-for="(item, index) in foodData.nutrition" :key="index">
          <view class="nutrition-header">
            <text class="nutrition-icon">{{ item.icon }}</text>
            <text class="nutrition-name">{{ item.name }}</text>
            <text class="nutrition-value">{{ item.percent }}</text>
          </view>
          <view class="nutrition-bar">
            <view class="nutrition-fill" :style="{ width: item.percent + '%' }"></view>
          </view>
          <view class="nutrition-status" :class="item.level">
            <text class="status-icon">{{ getStatusIcon(item.level) }}</text>
            <text class="status-text">{{ item.level }}</text>
          </view>
          <view class="nutrition-warning" v-if="item.warning">
            <text class="warning-icon">⚠️</text>
            <text class="warning-text">{{ item.warning }}</text>
          </view>
        </view>
      </view>

      <view class="suggestions-section">
        <view class="section-title">💡 检修建议</view>
        <view class="suggestion-list">
          <view 
            class="suggestion-item"
            v-for="(suggestion, index) in foodData.suggestions"
            :key="index"
          >
            <text class="suggestion-bullet">�?/text>
            <text class="suggestion-text">{{ suggestion }}</text>
          </view>
        </view>
      </view>
    </view>

    <view class="alternatives-section" v-if="foodData && showAlternatives">
      <view class="section-header">
        <view class="section-icon">💡</view>
        <view class="section-title">检修优化方案</view>
      </view>
      <view class="original-food">
        <text class="original-label">原检修项：</text>
        <text class="original-name">{{ foodData.name }}</text>
        <text class="original-score">（检修评分：{{ foodData.score }}分）</text>
      </view>
      
      <view class="alternatives-list">
        <view 
          class="alternative-card"
          v-for="(alt, index) in alternatives"
          :key="index"
        >
          <view class="alternative-header">
            <view class="alternative-icon">{{ alt.icon }}</view>
            <view class="alternative-info">
              <text class="alternative-name">{{ alt.name }}</text>
              <view class="alternative-score">
                <text class="score-stars">{{ getRatingStars(alt.score) }}</text>
                <text class="score-value">{{ alt.score }}�?/text>
              </view>
            </view>
          </view>
          <view class="alternative-nutrition">
            <view class="nutrition-mini">
              <text class="mini-label">综合指数</text>
              <text class="mini-value">{{ alt.calories }}</text>
            </view>
            <view class="nutrition-mini">
              <text class="mini-label">合规率</text>
              <text class="mini-value">{{ alt.protein }}%</text>
            </view>
          </view>
          <view class="alternative-benefit">
            <text class="benefit-icon">�?/text>
            <text class="benefit-text">{{ alt.benefit }}</text>
          </view>
          <view class="alternative-action" @click="viewAlternativeDetail(alt)">
            <text class="action-text">查看详情</text>
          </view>
        </view>
      </view>
    </view>

    <view class="traceability-section" v-if="foodData && showTraceability">
      <view class="section-header">
        <view class="section-icon">🔍</view>
        <view class="section-title">部件来源追溯</view>
      </view>
      
      <view class="traceability-list">
        <view 
          class="traceability-card"
          v-for="(item, index) in foodData.traceability"
          :key="index"
        >
          <view class="traceability-header">
            <view class="traceability-icon">{{ item.icon }}</view>
            <view class="traceability-name">{{ item.name }}</view>
          </view>
          <view class="traceability-info">
            <view class="info-row">
              <text class="info-label">📍 供应商：</text>
              <text class="info-value">{{ item.supplier }}</text>
            </view>
            <view class="info-row">
              <text class="info-label">📅 生产日期�?/text>
              <text class="info-value">{{ item.productionDate }}</text>
            </view>
            <view class="info-row" v-if="item.batchNumber">
              <text class="info-label">🏷�?批次号：</text>
              <text class="info-value">{{ item.batchNumber }}</text>
            </view>
          </view>
          <view class="certifications" v-if="item.certifications && item.certifications.length > 0">
            <view class="cert-title">质量认证：</view>
            <view class="cert-list">
              <view 
                class="cert-item"
                v-for="(cert, certIndex) in item.certifications"
                :key="certIndex"
              >
                <text class="cert-text">{{ cert }}</text>
              </view>
            </view>
          </view>
          <view class="origin-info" v-if="item.origin">
            <view class="info-row">
              <text class="info-label">📍 原产地：</text>
              <text class="info-value">{{ item.origin }}</text>
            </view>
            <view class="info-row">
              <text class="info-label">🚛 运输方式�?/text>
              <text class="info-value">{{ item.transport }}</text>
            </view>
            <view class="info-row" v-if="item.storage">
              <text class="info-label">🌡�?储存条件�?/text>
              <text class="info-value">{{ item.storage }}</text>
            </view>
          </view>
          <view class="traceability-actions">
            <view class="action-btn" @click="viewTestReport(item)">
              <text class="btn-text">查看检测报�?/text>
            </view>
            <view class="action-btn" @click="viewTraceabilityCert(item)">
              <text class="btn-text">查看溯源证书</text>
            </view>
          </view>
        </view>
      </view>
    </view>

    <view class="action-tabs" v-if="foodData">
      <view 
        class="tab-item"
        :class="{ active: activeTab === tab }"
        v-for="tab in tabs"
        :key="tab"
        @click="switchTab(tab)"
      >
        <text class="tab-text">{{ tab }}</text>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  name: 'TakeoutAssessment',
  data() {
    return {
      scanInput: '',
      foodData: null,
      showAlternatives: false,
      showTraceability: false,
      activeTab: '检修维度',
      tabs: ['检修维度', '优化方案', '部件追溯'],
      alternatives: [],
      displayScore: 0,
      isScoring: false,
      sampleFoodData: {
        name: '摩托车发动机总成',
        score: 72,
        nutrition: [
          {
            icon: '🔥',
            name: '运行温度',
            value: 68,
            unit: '℃',
            percent: 68,
            level: '中等',
            warning: '温度偏高，建议检查冷却系统'
          },
          {
            icon: '⚡',
            name: '点火电压',
            value: 12,
            unit: 'V',
            percent: 83,
            level: '良好',
            warning: null
          },
          {
            icon: '🛢️',
            name: '机油状态',
            value: 65,
            unit: '%',
            percent: 65,
            level: '适中',
            warning: '建议尽快更换机油'
          },
          {
            icon: '⚙️',
            name: '气缸压力',
            value: 9,
            unit: 'bar',
            percent: 71,
            level: '适中',
            warning: null
          }
        ],
        suggestions: [
          '建议尽快更换机油，保持润滑效果',
          '检查冷却系统散热片是否堵塞',
          '定期清洗空气滤清器，每2000公里一次'
        ],
        traceability: [
          {
            icon: '⚙️',
            name: '气缸体',
            supplier: 'XX动力部件有限公司',
            productionDate: '2024-01-15',
            batchNumber: 'B20240115001',
            certifications: [
              'ISO9001质量管理体系认证',
              'IATF16949汽车行业质量认证',
              'CCC强制性产品认证'
            ],
            origin: '浙江省宁波市',
            transport: '专线物流',
            storage: '常温干燥'
          },
          {
            icon: '🔋',
            name: '火花塞',
            supplier: 'XX电气配件厂',
            productionDate: '2024-01-16',
            certifications: ['ISO14001环境管理体系认证'],
            origin: '广东省广州市',
            transport: '标准快递',
            storage: '常温防潮'
          }
        ]
      },
      sampleAlternatives: [
        {
          icon: '🔧',
          name: '全面检修方案',
          score: 92,
          calories: 120,
          protein: 95,
          benefit: '全面排查隐患，延长设备寿命'
        },
        {
          icon: '🛡️',
          name: '预防性维护方案',
          score: 85,
          calories: 80,
          protein: 88,
          benefit: '定期保养，降低故障率'
        },
        {
          icon: '📋',
          name: '标准化作业方案',
          score: 88,
          calories: 100,
          protein: 90,
          benefit: '按标准流程操作，确保合规'
        }
      ]
    }
  },
  methods: {
    handleScan() {
      uni.showLoading({
        title: '分析�?..',
        mask: true
      })
      
      setTimeout(() => {
        this.foodData = this.sampleFoodData
        this.alternatives = this.sampleAlternatives
        uni.hideLoading()
        this.startScoreAnimation()
      }, 800)
    },
    
    startScoreAnimation() {
      this.isScoring = true
      this.displayScore = 0
      const targetScore = this.foodData.score
      const duration = 1500
      const steps = 60
      const increment = targetScore / steps
      let currentStep = 0
      
      const timer = setInterval(() => {
        currentStep++
        const newScore = Math.min(Math.round(increment * currentStep), targetScore)
        this.displayScore = newScore
        
        if (currentStep >= steps) {
          clearInterval(timer)
          this.displayScore = targetScore
          setTimeout(() => {
            this.isScoring = false
            uni.showToast({
              title: '分析完成',
              icon: 'success'
            })
          }, 300)
        }
      }, duration / steps)
    },
    
    getRatingStars(score) {
      const stars = Math.floor(score / 20)
      return '�?.repeat(stars)
    },
    
    getRatingText(score) {
      if (score >= 90) return '优秀检修作业'
      if (score >= 75) return '良好检修作业'
      if (score >= 60) return '合格检修作业'
      if (score >= 40) return '需改进作业'
      return '不合格作业'
    },
    
    getStatusIcon(level) {
      const icons = {
        '良好': '�?,
        '适中': '�?,
        '中等': '�?,
        '偏高': '⚠️',
        '过高': '�?
      }
      return icons[level] || '�?
    },
    
    switchTab(tab) {
      this.activeTab = tab
      this.showAlternatives = tab === '优化方案'
      this.showTraceability = tab === '部件追溯'
      uni.vibrateShort()
    },
    
    viewAlternativeDetail(alt) {
      uni.showModal({
        title: alt.name,
        content: `检修评分：${alt.score}分\n综合指数：${alt.calories}\n合规率：${alt.protein}%\n\n${alt.benefit}`,
        showCancel: false,
        confirmText: '知道�?
      })
    },
    
    viewTestReport(item) {
      uni.showToast({
        title: '查看检测报�?,
        icon: 'none'
      })
    },
    
    viewTraceabilityCert(item) {
      uni.showToast({
        title: '查看溯源证书',
        icon: 'none'
      })
    }
  }
}
</script>

<style scoped>
.takeout-assessment {
  min-height: 100vh;
  background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
  padding: 32rpx;
  padding-bottom: 200rpx;
}

.assessment-header {
  text-align: center;
  margin-bottom: 32rpx;
}

.header-icon {
  font-size: 64rpx;
  margin-bottom: 16rpx;
}

.header-title {
  font-size: 36rpx;
  font-weight: 700;
  color: #065f46;
}

.scan-section {
  margin-bottom: 32rpx;
}

.scan-input-wrapper {
  display: flex;
  align-items: center;
  gap: 16rpx;
  background: white;
  border-radius: 48rpx;
  padding: 8rpx 8rpx 8rpx 24rpx;
  box-shadow: 0 4rpx 16rpx rgba(16, 185, 129, 0.1);
}

.scan-icon {
  font-size: 32rpx;
}

.scan-input {
  flex: 1;
  height: 72rpx;
  font-size: 28rpx;
  color: #1e293b;
  background: transparent;
  border: none;
  outline: none;
}

.scan-input::placeholder {
  color: #9ca3af;
}

.scan-btn {
  padding: 16rpx 32rpx;
  background: linear-gradient(135deg, #10b981 0%, #34d399 100%);
  border-radius: 40rpx;
  box-shadow: 0 4rpx 12rpx rgba(16, 185, 129, 0.3);
}

.scan-btn-text {
  font-size: 26rpx;
  font-weight: 600;
  color: white;
}

.food-detail {
  background: white;
  border-radius: 32rpx;
  padding: 32rpx;
  box-shadow: 0 8rpx 24rpx rgba(16, 185, 129, 0.15);
  margin-bottom: 24rpx;
}

.food-image {
  width: 100%;
  height: 400rpx;
  background: linear-gradient(135deg, #1e293b 0%, #374151 100%);
  border-radius: 24rpx;
  margin-bottom: 32rpx;
  overflow: hidden;
}

.image-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16rpx;
}

.placeholder-icon {
  font-size: 80rpx;
}

.placeholder-text {
  font-size: 28rpx;
  color: rgba(255, 255, 255, 0.7);
}

.health-score-section {
  margin-bottom: 32rpx;
  position: relative;
}

.score-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16rpx;
}

.score-label {
  font-size: 28rpx;
  font-weight: 600;
  color: #065f46;
}

.score-value {
  font-size: 48rpx;
  font-weight: 700;
  color: #059669;
  transition: transform 0.1s ease;
}

.score-value.score-loading {
  animation: scoreBounce 0.1s ease-in-out;
}

@keyframes scoreBounce {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.score-bar {
  width: 100%;
  height: 20rpx;
  background: #e5e7eb;
  border-radius: 10rpx;
  overflow: hidden;
  margin-bottom: 16rpx;
  position: relative;
}

.score-fill {
  height: 100%;
  background: linear-gradient(90deg, #10b981 0%, #34d399 100%);
  border-radius: 10rpx;
  transition: width 0.05s linear;
  box-shadow: 0 2rpx 8rpx rgba(16, 185, 129, 0.3);
  position: relative;
}

.score-fill::after {
  content: '';
  position: absolute;
  right: 0;
  top: 0;
  height: 100%;
  width: 20rpx;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.5));
  animation: shimmer 0.5s infinite;
}

@keyframes shimmer {
  0% { opacity: 0.5; }
  50% { opacity: 1; }
  100% { opacity: 0.5; }
}

.score-glow {
  position: absolute;
  top: 50%;
  transform: translate(-50%, -50%);
  width: 30rpx;
  height: 30rpx;
  background: radial-gradient(circle, rgba(16, 185, 129, 0.6) 0%, transparent 70%);
  border-radius: 50%;
  transition: left 0.05s linear;
  pointer-events: none;
}

.loading-pulse {
  position: absolute;
  right: 32rpx;
  top: 50%;
  transform: translateY(-50%);
  width: 60rpx;
  height: 60rpx;
}

.pulse-ring {
  position: absolute;
  width: 100%;
  height: 100%;
  border: 4rpx solid #10b981;
  border-radius: 50%;
  animation: pulse 1s ease-out infinite;
}

.pulse-ring.delay-1 {
  animation-delay: 0.33s;
}

.pulse-ring.delay-2 {
  animation-delay: 0.66s;
}

@keyframes pulse {
  0% {
    transform: scale(0.5);
    opacity: 1;
  }
  100% {
    transform: scale(1.5);
    opacity: 0;
  }
}

.score-rating {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.rating-stars {
  font-size: 32rpx;
}

.rating-text {
  font-size: 26rpx;
  font-weight: 600;
  color: #059669;
}

.nutrition-section {
  margin-bottom: 32rpx;
}

.section-title {
  font-size: 28rpx;
  font-weight: 700;
  color: #065f46;
  margin-bottom: 24rpx;
}

.nutrition-item {
  padding: 24rpx;
  background: #f0fdf4;
  border-radius: 20rpx;
  margin-bottom: 20rpx;
  border: 2rpx solid rgba(16, 185, 129, 0.1);
}

.nutrition-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16rpx;
}

.nutrition-icon {
  font-size: 32rpx;
}

.nutrition-name {
  font-size: 26rpx;
  font-weight: 600;
  color: #065f46;
  flex: 1;
}

.nutrition-value {
  font-size: 26rpx;
  font-weight: 700;
  color: #059669;
}

.nutrition-bar {
  width: 100%;
  height: 12rpx;
  background: #e5e7eb;
  border-radius: 6rpx;
  overflow: hidden;
  margin-bottom: 12rpx;
}

.nutrition-fill {
  height: 100%;
  border-radius: 6rpx;
  transition: width 0.5s ease;
}

.nutrition-fill.良好 {
  background: linear-gradient(90deg, #10b981 0%, #34d399 100%);
}

.nutrition-fill.适中 {
  background: linear-gradient(90deg, #f59e0b 0%, #fbbf24 100%);
}

.nutrition-fill.中等 {
  background: linear-gradient(90deg, #f59e0b 0%, #fbbf24 100%);
}

.nutrition-fill.偏高 {
  background: linear-gradient(90deg, #f97316 0%, #fb923c 100%);
}

.nutrition-fill.过高 {
  background: linear-gradient(90deg, #ef4444 0%, #f87171 100%);
}

.nutrition-status {
  display: flex;
  align-items: center;
  gap: 8rpx;
  margin-bottom: 12rpx;
}

.status-icon {
  font-size: 24rpx;
}

.status-text {
  font-size: 24rpx;
  font-weight: 600;
}

.nutrition-status.良好 .status-text {
  color: #059669;
}

.nutrition-status.适中 .status-text {
  color: #d97706;
}

.nutrition-status.中等 .status-text {
  color: #d97706;
}

.nutrition-status.偏高 .status-text {
  color: #ea580c;
}

.nutrition-status.过高 .status-text {
  color: #dc2626;
}

.nutrition-warning {
  display: flex;
  align-items: center;
  gap: 8rpx;
  padding: 12rpx;
  background: rgba(234, 88, 12, 0.1);
  border-radius: 12rpx;
}

.warning-icon {
  font-size: 24rpx;
}

.warning-text {
  font-size: 22rpx;
  color: #9a3412;
  flex: 1;
}

.suggestions-section {
  margin-bottom: 32rpx;
}

.suggestion-list {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.suggestion-item {
  display: flex;
  align-items: flex-start;
  gap: 12rpx;
  padding: 16rpx;
  background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
  border-radius: 16rpx;
}

.suggestion-bullet {
  font-size: 24rpx;
  color: #059669;
  font-weight: 700;
}

.suggestion-text {
  font-size: 26rpx;
  line-height: 1.6;
  color: #064e3b;
  flex: 1;
}

.alternatives-section {
  background: white;
  border-radius: 32rpx;
  padding: 32rpx;
  box-shadow: 0 8rpx 24rpx rgba(16, 185, 129, 0.15);
  margin-bottom: 24rpx;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 16rpx;
  margin-bottom: 24rpx;
}

.section-icon {
  font-size: 32rpx;
}

.original-food {
  padding: 20rpx;
  background: #f0fdf4;
  border-radius: 16rpx;
  margin-bottom: 24rpx;
}

.original-label {
  font-size: 24rpx;
  color: #065f46;
}

.original-name {
  font-size: 26rpx;
  font-weight: 600;
  color: #065f46;
  margin: 0 8rpx;
}

.original-score {
  font-size: 24rpx;
  color: #059669;
}

.alternatives-list {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.alternative-card {
  padding: 24rpx;
  background: #f0fdf4;
  border-radius: 20rpx;
  border: 2rpx solid rgba(16, 185, 129, 0.1);
}

.alternative-header {
  display: flex;
  align-items: center;
  gap: 16rpx;
  margin-bottom: 16rpx;
}

.alternative-icon {
  font-size: 48rpx;
}

.alternative-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}

.alternative-name {
  font-size: 28rpx;
  font-weight: 700;
  color: #065f46;
}

.alternative-score {
  display: flex;
  align-items: center;
  gap: 12rpx;
}

.score-stars {
  font-size: 24rpx;
}

.score-value {
  font-size: 26rpx;
  font-weight: 700;
  color: #059669;
}

.alternative-nutrition {
  display: flex;
  gap: 24rpx;
  margin-bottom: 16rpx;
}

.nutrition-mini {
  display: flex;
  flex-direction: column;
  gap: 4rpx;
}

.mini-label {
  font-size: 22rpx;
  color: #64748b;
}

.mini-value {
  font-size: 24rpx;
  font-weight: 600;
  color: #065f46;
}

.alternative-benefit {
  display: flex;
  align-items: center;
  gap: 8rpx;
  padding: 12rpx;
  background: rgba(16, 185, 129, 0.1);
  border-radius: 12rpx;
  margin-bottom: 16rpx;
}

.benefit-icon {
  font-size: 24rpx;
}

.benefit-text {
  font-size: 24rpx;
  color: #047857;
  flex: 1;
}

.alternative-action {
  text-align: center;
  padding: 16rpx;
  background: linear-gradient(135deg, #10b981 0%, #34d399 100%);
  border-radius: 16rpx;
}

.action-text {
  font-size: 26rpx;
  font-weight: 600;
  color: white;
}

.traceability-section {
  background: white;
  border-radius: 32rpx;
  padding: 32rpx;
  box-shadow: 0 8rpx 24rpx rgba(16, 185, 129, 0.15);
  margin-bottom: 24rpx;
}

.traceability-list {
  display: flex;
  flex-direction: column;
  gap: 24rpx;
}

.traceability-card {
  padding: 24rpx;
  background: #f0fdf4;
  border-radius: 20rpx;
  border: 2rpx solid rgba(16, 185, 129, 0.1);
}

.traceability-header {
  display: flex;
  align-items: center;
  gap: 16rpx;
  margin-bottom: 20rpx;
}

.traceability-icon {
  font-size: 48rpx;
}

.traceability-name {
  font-size: 28rpx;
  font-weight: 700;
  color: #065f46;
}

.traceability-info {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
  margin-bottom: 20rpx;
}

.info-row {
  display: flex;
  align-items: center;
  gap: 8rpx;
}

.info-label {
  font-size: 24rpx;
  color: #64748b;
}

.info-value {
  font-size: 24rpx;
  font-weight: 600;
  color: #065f46;
}

.certifications {
  margin-bottom: 20rpx;
}

.cert-title {
  font-size: 24rpx;
  font-weight: 600;
  color: #065f46;
  margin-bottom: 12rpx;
}

.cert-list {
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}

.cert-item {
  padding: 12rpx;
  background: rgba(16, 185, 129, 0.1);
  border-radius: 12rpx;
}

.cert-text {
  font-size: 22rpx;
  color: #047857;
}

.origin-info {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
  padding: 16rpx;
  background: rgba(16, 185, 129, 0.05);
  border-radius: 12rpx;
  margin-bottom: 20rpx;
}

.traceability-actions {
  display: flex;
  gap: 16rpx;
}

.action-btn {
  flex: 1;
  text-align: center;
  padding: 16rpx;
  background: linear-gradient(135deg, #10b981 0%, #34d399 100%);
  border-radius: 16rpx;
}

.btn-text {
  font-size: 24rpx;
  font-weight: 600;
  color: white;
}

.action-tabs {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  background: white;
  box-shadow: 0 -4rpx 16rpx rgba(0, 0, 0, 0.1);
  z-index: 9999;
}

.tab-item {
  flex: 1;
  text-align: center;
  padding: 24rpx;
  font-size: 26rpx;
  color: #64748b;
  font-weight: 500;
  border-bottom: 4rpx solid transparent;
  transition: all 0.3s;
}

.tab-item.active {
  color: #059669;
  border-bottom-color: #10b981;
  font-weight: 600;
}

.tab-text {
  font-size: 26rpx;
}
</style>