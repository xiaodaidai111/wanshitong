<template>
  <view class="bar-chart-container">
    <view class="chart-title">{{ title || '数据图表' }}</view>
    <view class="chart-bars">
      <view v-for="(value, index) in normalizedData" :key="index" class="bar-item">
        <view class="bar-label">{{ labels[index] || `数据${index+1}` }}</view>
        <view class="bar-wrapper">
          <view class="bar weight-bar" :style="{ height: value + '%' }"></view>
        </view>
        <view class="bar-value">{{ data[index] }}{{ unit || '' }}</view>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  name: 'BarChart',
  props: {
    data: {
      type: Array,
      default: () => []
    },
    labels: {
      type: Array,
      default: () => []
    },
    title: {
      type: String,
      default: ''
    },
    unit: {
      type: String,
      default: ''
    }
  },
  computed: {
    normalizedData() {
      if (!this.data || this.data.length === 0) return [];
      
      // 找到最大值和最小值，进行归一化处�?      const max = Math.max(...this.data);
      const min = Math.min(...this.data);
      const range = max - min || 1; // 避免除以0
      
      // 归一化到0-100的范围，并添加一些padding
      return this.data.map(value => {
        const normalized = ((value - min) / range) * 80 + 10;
        return Math.min(Math.max(normalized, 0), 100);
      });
    }
  }
}
</script>

<style scoped>
/* 柱状图容�?*/
.bar-chart-container {
  width: 100%;
  padding: 20rpx;
  background-color: #fafafa;
  border-radius: 12rpx;
  height: 100%;
  display: flex;
  flex-direction: column;
}

/* 图表标题 */
.chart-title {
  font-size: 28rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 20rpx;
  text-align: center;
}

/* 图表柱状区域 */
.chart-bars {
  display: flex;
  justify-content: space-around;
  align-items: flex-end;
  height: calc(100% - 50rpx);
  min-height: 300rpx;
  padding: 0 20rpx;
}

/* 柱状�?*/
.bar-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
}

/* 柱状标签 */
.bar-label {
  margin-bottom: 10rpx;
  font-size: 24rpx;
  color: #666;
  text-align: center;
  min-height: 30rpx;
}

/* 柱状容器 */
.bar-wrapper {
  width: 40rpx;
  flex: 1;
  min-height: 200rpx;
  background-color: #f0f0f0;
  border-radius: 8rpx;
  position: relative;
  overflow: hidden;
  margin-bottom: 10rpx;
}

/* 柱状�?*/
.bar.weight-bar {
  width: 100%;
  background: linear-gradient(180deg, #36a2eb 0%, #4bc0c0 100%);
  position: absolute;
  bottom: 0;
  transition: height 0.5s ease;
  border-radius: 8rpx;
}

/* 柱状�?*/
.bar-value {
  font-size: 24rpx;
  color: #36a2eb;
  font-weight: 500;
}

/* 不同类型柱状条样�?*/
.bar {
  position: absolute;
  bottom: 0;
  width: 100%;
  border-radius: 8rpx 8rpx 0 0;
  transition: height 0.5s ease;
}

.protein-bar {
  background-color: #1890ff;
}

.carb-bar {
  background-color: #52c41a;
}

.fat-bar {
  background-color: #fa8c16;
}

/* 响应式设�?*/
@media (max-width: 768px) {
  .bar-chart-container {
    padding: 15rpx;
  }
  
  .chart-bars {
    padding: 0 10rpx;
  }
  
  .bar-wrapper {
    width: 30rpx;
  }
  
  .bar-label {
    font-size: 22rpx;
  }
  
  .bar-value {
    font-size: 20rpx;
  }
}
</style>