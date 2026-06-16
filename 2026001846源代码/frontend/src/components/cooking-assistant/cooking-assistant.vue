<template>
  <view class="cooking-assistant">
    <view class="cooking-header">
      <view class="header-info">
        <view class="recipe-icon">🔧</view>
        <view class="recipe-info">
          <text class="recipe-name">{{ recipeName }}</text>
          <text class="recipe-meta">{{ recipeMeta }}</text>
        </view>
      </view>
      <view class="header-actions">
        <view class="action-btn" @click="showIngredients">
          <text class="action-icon">📋</text>
        </view>
        <view class="action-btn" @click="showFoodScanner">
          <text class="action-icon">📷</text>
        </view>
        <view class="action-btn" @click="showQuestions">
          <text class="action-icon">�?/text>
        </view>
      </view>
    </view>

    <view class="cooking-progress">
      <view class="progress-info">
        <text class="progress-text">进度：{{ currentStep + 1 }}/{{ totalSteps }} �?/text>
        <view class="progress-bar">
          <view class="progress-fill" :style="{ width: progressPercent + '%' }"></view>
        </view>
      </view>
    </view>

    <view class="cooking-content">
      <view class="step-content">
        <view class="step-indicator">
          <view class="step-number">{{ currentStep + 1 }}</view>
          <view class="step-label">{{ currentStepTitle }}</view>
        </view>

        <view class="step-video" v-if="hasVideo">
          <view class="video-placeholder">
            <text class="video-icon">🎬</text>
            <text class="video-text">视频演示</text>
          </view>
          <view class="video-controls">
            <view class="control-btn" @click="toggleVideoPlay">
              <text>{{ isVideoPlaying ? '⏸️' : '▶️' }}</text>
            </view>
            <view class="control-btn" @click="replayVideo">
              <text>🔄</text>
            </view>
          </view>
        </view>

        <view class="step-description">
          <view class="description-label">📝 详细说明</view>
          <text class="description-text">{{ currentStepDescription }}</text>
        </view>

        <view class="step-timer">
          <view class="timer-display">
            <text class="timer-label">⏱️ 计时�?/text>
            <text class="timer-time">{{ formattedTime }}</text>
          </view>
          <view class="timer-controls">
            <view class="timer-btn" :class="{ active: isTimerRunning }" @click="toggleTimer">
              <text>{{ isTimerRunning ? '⏸️' : '▶️' }}</text>
            </view>
            <view class="timer-btn" @click="resetTimer">
              <text>🔄</text>
            </view>
          </view>
        </view>

        <view class="step-voice">
          <view class="voice-header">
            <text class="voice-icon">🎤</text>
            <text class="voice-label">语音指导</text>
          </view>
          <view class="voice-controls">
            <view class="voice-btn" :class="{ active: isVoicePlaying }" @click="toggleVoice">
              <text>{{ isVoicePlaying ? '⏸️' : '▶️' }}</text>
            </view>
            <view class="voice-btn" @click="replayVoice">
              <text>🔁</text>
            </view>
          </view>
          <view class="voice-status" v-if="isVoicePlaying">
            <text class="voice-wave">�?/text>
            <text class="voice-text">{{ currentVoiceText }}</text>
          </view>
        </view>

        <view class="step-heat">
          <view class="heat-header">
            <text class="heat-icon">📋</text>
            <text class="heat-label">操作规范</text>
          </view>
          <view class="heat-info">
            <view class="heat-level">
              <text class="heat-label-text">推荐扭矩：</text>
              <text class="heat-value">{{ heatLevel }}</text>
            </view>
            <view class="heat-time">
              <text class="heat-label-text">建议工时：</text>
              <text class="heat-value">{{ heatTime }}</text>
            </view>
          </view>
          <view class="heat-warning" v-if="heatWarning">
            <text class="warning-icon">⚠️</text>
            <text class="warning-text">{{ heatWarning }}</text>
          </view>
        </view>
      </view>

      <view class="ingredients-panel" v-if="showIngredientsPanel">
        <view class="panel-header">
          <text class="panel-title">📋 检修准备清单</text>
          <view class="panel-close" @click="hideIngredients">�?/view>
        </view>
        <view class="ingredients-list">
          <view 
            class="ingredient-item"
            v-for="(item, index) in ingredients"
            :key="index"
            :class="{ checked: item.checked }"
            @click="toggleIngredient(index)"
          >
            <view class="ingredient-checkbox">
              <text class="checkbox-icon" v-if="item.checked">�?/text>
            </view>
            <view class="ingredient-info">
              <text class="ingredient-name">{{ item.name }}</text>
              <text class="ingredient-amount">{{ item.amount }}</text>
            </view>
            <view class="ingredient-tag" :class="item.category">{{ item.category }}</view>
          </view>
        </view>
        <view class="ingredients-summary">
          <text class="summary-text">已完�?{{ checkedIngredients }}/{{ ingredients.length }} �?/text>
        </view>
      </view>

      <view class="food-scanner-panel" v-if="showScannerPanel">
        <view class="panel-header">
          <text class="panel-title">📷 故障识别</text>
          <view class="panel-close" @click="hideScanner">�?/view>
        </view>
        <view class="scanner-content">
          <view class="scanner-view">
            <view class="scanner-frame">
              <text class="scanner-hint">将设备放入框�?/text>
            </view>
          </view>
          <view class="scanner-actions">
            <view class="scanner-btn primary" @click="startScan">
              <text>📸 开始扫�?/text>
            </view>
            <view class="scanner-btn" @click="switchCamera">
              <text>🔄 切换摄像�?/text>
            </view>
          </view>
        </view>
        <view class="scanner-results" v-if="scanResults.length > 0">
          <view class="results-title">识别结果</view>
          <view 
            class="result-item"
            v-for="(result, index) in scanResults"
            :key="index"
          >
            <view class="result-icon">{{ result.icon }}</view>
            <view class="result-info">
              <text class="result-name">{{ result.name }}</text>
              <text class="result-confidence">置信度：{{ result.confidence }}%</text>
            </view>
            <view class="result-action" @click="viewRecipe(result)">
              <text>查看手册</text>
            </view>
          </view>
        </view>
      </view>

      <view class="questions-panel" v-if="showQuestionsPanel">
        <view class="panel-header">
          <text class="panel-title">�?故障问题解答</text>
          <view class="panel-close" @click="hideQuestions">�?/view>
        </view>
        <view class="questions-search">
          <input 
            type="text" 
            v-model="searchQuery"
            placeholder="搜索问题..."
            class="search-input"
          />
        </view>
        <view class="questions-list">
          <view 
            class="question-item"
            v-for="(question, index) in filteredQuestions"
            :key="index"
            @click="showQuestionDetail(question)"
          >
            <view class="question-icon">📌</view>
            <view class="question-content">
              <text class="question-title">{{ question.title }}</text>
              <text class="question-preview">{{ question.preview }}</text>
            </view>
            <view class="question-arrow">�?/view>
          </view>
        </view>
      </view>
    </view>

    <view class="cooking-footer">
      <view class="footer-btn prev-btn" :class="{ disabled: currentStep === 0 }" @click="prevStep">
        <text class="btn-icon">◀�?/text>
        <text class="btn-text">上一�?/text>
      </view>
      <view class="footer-actions">
        <view class="action-btn-small" @click="pauseCooking">
          <text>⏸️ 暂停</text>
        </view>
        <view class="action-btn-small" @click="finishCooking">
          <text>�?完成</text>
        </view>
      </view>
      <view class="footer-btn next-btn" :class="{ disabled: currentStep === totalSteps - 1 }" @click="nextStep">
        <text class="btn-text">下一�?/text>
        <text class="btn-icon">▶️</text>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  name: 'CookingAssistant',
  props: {
    recipeName: {
      type: String,
      default: '摩托车发动机检修'
    },
    recipeMeta: {
      type: String,
      default: '难度：⭐⭐ 工时：45分钟'
    },
    steps: {
      type: Array,
      default: () => []
    },
    ingredients: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      currentStep: 0,
      totalSteps: 5,
      isVideoPlaying: false,
      isTimerRunning: false,
      timerTime: 150,
      isVoicePlaying: false,
      currentVoiceText: '',
      heatLevel: '25-30 N·m',
      heatTime: '15-20分钟',
      heatWarning: '注意检查密封垫是否完好，避免漏油',
      showIngredientsPanel: false,
      showScannerPanel: false,
      showQuestionsPanel: false,
      scanResults: [],
      searchQuery: '',
      questions: [
        {
          title: '发动机异响怎么排查？',
          preview: '先判断异响来源部位...',
          solution: '先判断异响来源部位（气缸、曲轴箱、配气机构），再逐一检查相关部件的磨损和间隙情况。'
        },
        {
          title: '机油压力偏低怎么处理？',
          preview: '检查机油量和油质...',
          solution: '首先检查机油量和油质是否正常，再检查机油泵、机油滤清器和油道是否有堵塞或泄漏。'
        },
        {
          title: '点火系统故障怎么诊断？',
          preview: '检查火花塞和点火线圈...',
          solution: '依次检查火花塞积碳和间隙、点火线圈电阻值、高压线路连接情况，必要时更换损坏部件。'
        }
      ]
    }
  },
  computed: {
    progressPercent() {
      return ((this.currentStep + 1) / this.totalSteps) * 100
    },
    currentStepTitle() {
      return this.steps[this.currentStep]?.title || ''
    },
    currentStepDescription() {
      return this.steps[this.currentStep]?.description || ''
    },
    hasVideo() {
      return this.steps[this.currentStep]?.hasVideo || false
    },
    formattedTime() {
      const minutes = Math.floor(this.timerTime / 60)
      const seconds = this.timerTime % 60
      return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
    },
    checkedIngredients() {
      return this.ingredients.filter(item => item.checked).length
    },
    filteredQuestions() {
      if (!this.searchQuery) return this.questions
      return this.questions.filter(q => 
        q.title.includes(this.searchQuery) || q.preview.includes(this.searchQuery)
      )
    }
  },
  methods: {
    showIngredients() {
      this.showIngredientsPanel = true
      this.showScannerPanel = false
      this.showQuestionsPanel = false
    },
    
    hideIngredients() {
      this.showIngredientsPanel = false
    },
    
    showFoodScanner() {
      this.showScannerPanel = true
      this.showIngredientsPanel = false
      this.showQuestionsPanel = false
    },
    
    hideScanner() {
      this.showScannerPanel = false
    },
    
    showQuestions() {
      this.showQuestionsPanel = true
      this.showIngredientsPanel = false
      this.showScannerPanel = false
    },
    
    hideQuestions() {
      this.showQuestionsPanel = false
    },
    
    toggleIngredient(index) {
      this.ingredients[index].checked = !this.ingredients[index].checked
      this.$emit('ingredient-toggle', {
        index,
        checked: this.ingredients[index].checked
      })
    },
    
    toggleVideoPlay() {
      this.isVideoPlaying = !this.isVideoPlaying
      this.$emit('video-toggle', this.isVideoPlaying)
    },
    
    replayVideo() {
      this.isVideoPlaying = true
      this.$emit('video-replay')
    },
    
    toggleTimer() {
      if (this.isTimerRunning) {
        this.stopTimer()
      } else {
        this.startTimer()
      }
    },
    
    startTimer() {
      this.isTimerRunning = true
      this.timerInterval = setInterval(() => {
        if (this.timerTime > 0) {
          this.timerTime--
        } else {
          this.stopTimer()
          uni.showToast({
            title: '时间到！',
            icon: 'success'
          })
        }
      }, 1000)
      this.$emit('timer-start')
    },
    
    stopTimer() {
      this.isTimerRunning = false
      if (this.timerInterval) {
        clearInterval(this.timerInterval)
      }
      this.$emit('timer-stop')
    },
    
    resetTimer() {
      this.stopTimer()
      this.timerTime = 150
      this.$emit('timer-reset')
    },
    
    toggleVoice() {
      if (this.isVoicePlaying) {
        this.stopVoice()
      } else {
        this.playVoice()
      }
    },
    
    playVoice() {
      this.isVoicePlaying = true
      this.currentVoiceText = this.currentStepDescription
      this.$emit('voice-play', this.currentStepDescription)
      
      setTimeout(() => {
        this.stopVoice()
      }, 5000)
    },
    
    stopVoice() {
      this.isVoicePlaying = false
      this.currentVoiceText = ''
      this.$emit('voice-stop')
    },
    
    replayVoice() {
      this.playVoice()
    },
    
    startScan() {
      uni.showToast({
        title: '正在扫描...',
        icon: 'loading'
      })
      
      setTimeout(() => {
        this.scanResults = [
          {
            name: '气缸体',
            icon: '⚙️',
            confidence: 95,
            recipes: ['气缸研磨', '活塞更换', '缸垫更换']
          },
          {
            name: '点火线圈',
            icon: '⚡',
            confidence: 88,
            recipes: ['电阻检测', '火花塞更换']
          }
        ]
        
        uni.showToast({
          title: '扫描完成',
          icon: 'success'
        })
      }, 2000)
    },
    
    switchCamera() {
      uni.showToast({
        title: '切换摄像�?,
        icon: 'none'
      })
    },
    
    viewRecipe(result) {
      this.$emit('view-recipe', result)
    },
    
    showQuestionDetail(question) {
      uni.showModal({
        title: question.title,
        content: question.solution,
        showCancel: false,
        confirmText: '知道�?
      })
    },
    
    prevStep() {
      if (this.currentStep > 0) {
        this.currentStep--
        this.resetStepData()
      }
    },
    
    nextStep() {
      if (this.currentStep < this.totalSteps - 1) {
        this.currentStep++
        this.resetStepData()
      }
    },
    
    resetStepData() {
      this.stopTimer()
      this.timerTime = 150
      this.stopVoice()
      this.isVideoPlaying = false
    },
    
    pauseCooking() {
      this.$emit('pause')
    },
    
    finishCooking() {
      this.$emit('finish')
      uni.showToast({
        title: '检修完成！',
        icon: 'success'
      })
    }
  },
  beforeDestroy() {
    this.stopTimer()
  }
}
</script>

<style scoped>
.cooking-assistant {
  min-height: 100vh;
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  padding: 32rpx;
}

.cooking-header {
  background: white;
  border-radius: 32rpx;
  padding: 32rpx;
  margin-bottom: 24rpx;
  box-shadow: 0 8rpx 24rpx rgba(245, 158, 11, 0.1);
}

.header-info {
  display: flex;
  align-items: center;
  gap: 24rpx;
  margin-bottom: 24rpx;
}

.recipe-icon {
  font-size: 64rpx;
  width: 100rpx;
  height: 100rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  border-radius: 24rpx;
}

.recipe-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}

.recipe-name {
  font-size: 36rpx;
  font-weight: 700;
  color: #1e293b;
}

.recipe-meta {
  font-size: 24rpx;
  color: #64748b;
}

.header-actions {
  display: flex;
  gap: 16rpx;
}

.action-btn {
  width: 72rpx;
  height: 72rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  border-radius: 16rpx;
  box-shadow: 0 4rpx 12rpx rgba(245, 158, 11, 0.15);
  transition: all 0.2s;
}

.action-btn:active {
  transform: scale(0.95);
}

.action-icon {
  font-size: 36rpx;
}

.cooking-progress {
  background: white;
  border-radius: 24rpx;
  padding: 24rpx 32rpx;
  margin-bottom: 24rpx;
  box-shadow: 0 4rpx 16rpx rgba(245, 158, 11, 0.08);
}

.progress-info {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.progress-text {
  font-size: 26rpx;
  font-weight: 600;
  color: #374151;
}

.progress-bar {
  width: 100%;
  height: 16rpx;
  background: #e5e7eb;
  border-radius: 8rpx;
  overflow: hidden;
  box-shadow: inset 0 2rpx 4rpx rgba(0, 0, 0, 0.05);
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #f59e0b 0%, #fbbf24 100%);
  border-radius: 8rpx;
  transition: width 0.3s ease;
  box-shadow: 0 2rpx 8rpx rgba(245, 158, 11, 0.3);
}

.cooking-content {
  display: flex;
  flex-direction: column;
  gap: 24rpx;
}

.step-content {
  background: white;
  border-radius: 32rpx;
  padding: 32rpx;
  box-shadow: 0 8rpx 24rpx rgba(245, 158, 11, 0.1);
}

.step-indicator {
  display: flex;
  align-items: center;
  gap: 16rpx;
  margin-bottom: 24rpx;
  padding-bottom: 24rpx;
  border-bottom: 2rpx solid #f3f4f6;
}

.step-number {
  width: 64rpx;
  height: 64rpx;
  background: linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28rpx;
  font-weight: 700;
}

.step-label {
  font-size: 32rpx;
  font-weight: 700;
  color: #1e293b;
}

.step-video {
  margin-bottom: 24rpx;
}

.video-placeholder {
  width: 100%;
  height: 400rpx;
  background: linear-gradient(135deg, #1e293b 0%, #374151 100%);
  border-radius: 24rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16rpx;
  box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.15);
  position: relative;
  overflow: hidden;
}

.video-placeholder::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle at center, rgba(245, 158, 11, 0.1) 0%, transparent 70%);
  pointer-events: none;
}

.video-icon {
  font-size: 80rpx;
}

.video-text {
  font-size: 28rpx;
  color: #64748b;
}

.video-controls {
  display: flex;
  justify-content: center;
  gap: 24rpx;
  margin-top: 16rpx;
}

.control-btn {
  width: 80rpx;
  height: 80rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  border-radius: 50%;
  font-size: 36rpx;
  box-shadow: 0 4rpx 12rpx rgba(245, 158, 11, 0.15);
  transition: all 0.2s;
}

.control-btn:active {
  transform: scale(0.95);
}

.step-description {
  margin-bottom: 24rpx;
}

.description-label {
  font-size: 24rpx;
  font-weight: 600;
  color: #64748b;
  margin-bottom: 12rpx;
}

.description-text {
  font-size: 28rpx;
  line-height: 1.6;
  color: #374151;
}

.step-timer {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  border-radius: 20rpx;
  padding: 24rpx;
  margin-bottom: 24rpx;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.timer-display {
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}

.timer-label {
  font-size: 24rpx;
  color: #92400e;
  font-weight: 600;
}

.timer-time {
  font-size: 48rpx;
  font-weight: 700;
  color: #1e293b;
  font-family: 'Courier New', monospace;
}

.timer-controls {
  display: flex;
  gap: 16rpx;
}

.timer-btn {
  width: 64rpx;
  height: 64rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  border-radius: 50%;
  font-size: 32rpx;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.1);
  transition: all 0.2s;
}

.timer-btn:active {
  transform: scale(0.95);
}

.timer-btn.active {
  background: linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%);
}

.step-voice {
  background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%);
  border-radius: 20rpx;
  padding: 24rpx;
  margin-bottom: 24rpx;
}

.voice-header {
  display: flex;
  align-items: center;
  gap: 12rpx;
  margin-bottom: 16rpx;
}

.voice-icon {
  font-size: 32rpx;
}

.voice-label {
  font-size: 26rpx;
  font-weight: 600;
  color: #0369a1;
}

.voice-controls {
  display: flex;
  gap: 16rpx;
  margin-bottom: 16rpx;
}

.voice-btn {
  width: 64rpx;
  height: 64rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  border-radius: 50%;
  font-size: 32rpx;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.1);
  transition: all 0.2s;
}

.voice-btn:active {
  transform: scale(0.95);
}

.voice-btn.active {
  background: linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%);
}

.voice-status {
  display: flex;
  align-items: center;
  gap: 12rpx;
  padding: 16rpx;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 16rpx;
}

.voice-wave {
  font-size: 32rpx;
  animation: wave 1s ease-in-out infinite;
}

@keyframes wave {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.2);
  }
}

.voice-text {
  font-size: 24rpx;
  color: #0369a1;
  flex: 1;
}

.step-heat {
  background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
  border-radius: 20rpx;
  padding: 24rpx;
  margin-bottom: 24rpx;
  border: 2rpx solid rgba(239, 68, 68, 0.1);
  box-shadow: 0 4rpx 12rpx rgba(239, 68, 68, 0.08);
}

.heat-header {
  display: flex;
  align-items: center;
  gap: 12rpx;
  margin-bottom: 16rpx;
}

.heat-icon {
  font-size: 32rpx;
}

.heat-label {
  font-size: 26rpx;
  font-weight: 600;
  color: #b91c1c;
}

.heat-info {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
  margin-bottom: 16rpx;
}

.heat-level,
.heat-time {
  display: flex;
  justify-content: space-between;
}

.heat-label-text {
  font-size: 24rpx;
  color: #7f1d1d;
}

.heat-value {
  font-size: 24rpx;
  font-weight: 600;
  color: #b91c1c;
}

.heat-warning {
  display: flex;
  align-items: center;
  gap: 12rpx;
  padding: 16rpx;
  background: rgba(185, 28, 28, 0.1);
  border-radius: 16rpx;
}

.warning-icon {
  font-size: 28rpx;
}

.warning-text {
  font-size: 24rpx;
  color: #7f1d1d;
  flex: 1;
}

.ingredients-panel,
.food-scanner-panel,
.questions-panel {
  background: white;
  border-radius: 32rpx;
  padding: 32rpx;
  box-shadow: 0 8rpx 24rpx rgba(245, 158, 11, 0.1);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24rpx;
  padding-bottom: 24rpx;
  border-bottom: 2rpx solid #f3f4f6;
}

.panel-title {
  font-size: 32rpx;
  font-weight: 700;
  color: #1e293b;
}

.panel-close {
  width: 48rpx;
  height: 48rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f3f4f6;
  border-radius: 50%;
  font-size: 28rpx;
  color: #64748b;
}

.ingredients-list {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.ingredient-item {
  display: flex;
  align-items: center;
  gap: 16rpx;
  padding: 20rpx;
  background: #f9fafb;
  border-radius: 16rpx;
  transition: all 0.2s;
}

.ingredient-item:active {
  transform: scale(0.98);
}

.ingredient-item.checked {
  background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%);
}

.ingredient-checkbox {
  width: 40rpx;
  height: 40rpx;
  background: white;
  border-radius: 8rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.06);
}

.checkbox-icon {
  font-size: 24rpx;
  color: #10b981;
}

.ingredient-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4rpx;
}

.ingredient-name {
  font-size: 28rpx;
  font-weight: 600;
  color: #1e293b;
}

.ingredient-amount {
  font-size: 24rpx;
  color: #64748b;
}

.ingredient-tag {
  padding: 8rpx 16rpx;
  border-radius: 12rpx;
  font-size: 22rpx;
  font-weight: 600;
}

.ingredient-tag.meat {
  background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
  color: #b91c1c;
}

.ingredient-tag.vegetable {
  background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%);
  color: #059669;
}

.ingredient-tag.spice {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  color: #92400e;
}

.ingredients-summary {
  text-align: center;
  padding-top: 24rpx;
  border-top: 2rpx solid #f3f4f6;
}

.summary-text {
  font-size: 24rpx;
  color: #64748b;
}

.scanner-content {
  margin-bottom: 24rpx;
}

.scanner-view {
  width: 100%;
  height: 500rpx;
  background: linear-gradient(135deg, #1e293b 0%, #374151 100%);
  border-radius: 24rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 24rpx;
}

.scanner-frame {
  width: 80%;
  height: 80%;
  border: 4rpx dashed rgba(255, 255, 255, 0.5);
  border-radius: 24rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.scanner-hint {
  font-size: 28rpx;
  color: rgba(255, 255, 255, 0.7);
}

.scanner-actions {
  display: flex;
  gap: 16rpx;
}

.scanner-btn {
  flex: 1;
  height: 80rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  border-radius: 16rpx;
  font-size: 28rpx;
  font-weight: 600;
  color: #1e293b;
  box-shadow: 0 4rpx 12rpx rgba(245, 158, 11, 0.15);
  transition: all 0.2s;
}

.scanner-btn:active {
  transform: scale(0.98);
}

.scanner-btn.primary {
  background: linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%);
}

.scanner-results {
  border-top: 2rpx solid #f3f4f6;
  padding-top: 24rpx;
}

.results-title {
  font-size: 28rpx;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 16rpx;
}

.result-item {
  display: flex;
  align-items: center;
  gap: 16rpx;
  padding: 20rpx;
  background: #f9fafb;
  border-radius: 16rpx;
  margin-bottom: 12rpx;
}

.result-icon {
  font-size: 48rpx;
}

.result-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4rpx;
}

.result-name {
  font-size: 28rpx;
  font-weight: 600;
  color: #1e293b;
}

.result-confidence {
  font-size: 24rpx;
  color: #64748b;
}

.result-action {
  padding: 12rpx 24rpx;
  background: linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%);
  border-radius: 12rpx;
  font-size: 24rpx;
  font-weight: 600;
  color: white;
}

.questions-search {
  margin-bottom: 24rpx;
}

.search-input {
  width: 100%;
  height: 80rpx;
  padding: 0 32rpx;
  background: #f9fafb;
  border-radius: 16rpx;
  font-size: 28rpx;
  color: #1e293b;
  border: 2rpx solid #e5e7eb;
}

.questions-list {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.question-item {
  display: flex;
  align-items: center;
  gap: 16rpx;
  padding: 20rpx;
  background: #f9fafb;
  border-radius: 16rpx;
  transition: all 0.2s;
}

.question-item:active {
  transform: scale(0.98);
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
}

.question-icon {
  font-size: 32rpx;
}

.question-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4rpx;
}

.question-title {
  font-size: 26rpx;
  font-weight: 600;
  color: #1e293b;
}

.question-preview {
  font-size: 24rpx;
  color: #64748b;
}

.question-arrow {
  font-size: 32rpx;
  color: #9ca3af;
}

.cooking-footer {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: white;
  padding: 24rpx 32rpx;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 -4rpx 16rpx rgba(0, 0, 0, 0.1);
}

.footer-btn {
  display: flex;
  align-items: center;
  gap: 12rpx;
  padding: 16rpx 32rpx;
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  border-radius: 24rpx;
  font-size: 28rpx;
  font-weight: 600;
  color: #1e293b;
  box-shadow: 0 4rpx 12rpx rgba(245, 158, 11, 0.15);
  transition: all 0.2s;
}

.footer-btn:active {
  transform: scale(0.98);
}

.footer-btn.disabled {
  opacity: 0.5;
  pointer-events: none;
}

.btn-icon {
  font-size: 32rpx;
}

.btn-text {
  font-size: 28rpx;
}

.footer-actions {
  display: flex;
  gap: 16rpx;
}

.action-btn-small {
  padding: 16rpx 24rpx;
  background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%);
  border-radius: 16rpx;
  font-size: 24rpx;
  font-weight: 600;
  color: #0369a1;
  box-shadow: 0 4rpx 12rpx rgba(59, 130, 246, 0.15);
  transition: all 0.2s;
}

.action-btn-small:active {
  transform: scale(0.98);
}
</style>
