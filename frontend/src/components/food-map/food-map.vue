<template>
  <view class="food-map">
    <view class="map-header">
      <view class="search-bar">
        <view class="search-icon">🔍</view>
        <input 
          type="text" 
          v-model="searchQuery"
          placeholder="搜索餐厅或美�?.."
          class="search-input"
          @confirm="handleSearch"
        />
      </view>
    </view>

    <view class="category-filter">
      <view 
        class="filter-item"
        :class="{ active: activeCategory === category }"
        v-for="category in categories"
        :key="category"
        @click="selectCategory(category)"
      >
        <text class="filter-text">{{ category }}</text>
      </view>
    </view>

    <view class="map-container">
      <view class="map-placeholder">
        <view class="map-bg"></view>
        <view class="map-markers">
          <view 
            class="map-marker"
            v-for="(restaurant, index) in filteredRestaurants"
            :key="index"
            :class="{ active: selectedRestaurant === index }"
            :style="{ left: restaurant.x + '%', top: restaurant.y + '%' }"
            @click="selectRestaurant(index)"
          >
            <view class="marker-icon">📍</view>
            <view class="marker-info" v-if="selectedRestaurant === index">
              <text class="marker-name">{{ restaurant.name }}</text>
              <text class="marker-rating">�?{{ restaurant.rating }}</text>
              <text class="marker-price">¥{{ restaurant.price }}/�?/text>
            </view>
          </view>
        </view>
      </view>

      <view class="map-controls">
        <view class="control-btn" @click="locateUser">
          <text class="control-icon">📍</text>
        </view>
        <view class="control-btn" @click="refreshMap">
          <text class="control-icon">🔄</text>
        </view>
      </view>
    </view>

    <view class="restaurant-detail" v-if="selectedRestaurant !== null">
      <view class="detail-header">
        <view class="detail-close" @click="closeDetail">�?/view>
        <view class="detail-image-carousel">
          <view class="carousel-placeholder">
            <text class="carousel-icon">🍽�?/text>
            <text class="carousel-text">餐厅图片</text>
          </view>
        </view>
        <view class="detail-info">
          <view class="detail-name">{{ selectedRestaurantData.name }}</view>
          <view class="detail-rating">
            <text class="rating-stars">⭐⭐⭐⭐�?/text>
            <text class="rating-score">{{ selectedRestaurantData.rating }}�?/text>
            <text class="rating-count">{{ selectedRestaurantData.reviewCount }}条评�?/text>
          </view>
          <view class="detail-meta">
            <view class="meta-item">
              <text class="meta-icon">📍</text>
              <text class="meta-text">{{ selectedRestaurantData.location }}</text>
            </view>
            <view class="meta-item">
              <text class="meta-icon">📏</text>
              <text class="meta-text">距离{{ selectedRestaurantData.distance }}km</text>
            </view>
            <view class="meta-item">
              <text class="meta-icon">💰</text>
              <text class="meta-text">¥{{ selectedRestaurantData.price }}/�?/text>
            </view>
            <view class="meta-item">
              <text class="meta-icon">🕐</text>
              <text class="meta-text">{{ selectedRestaurantData.hours }}</text>
            </view>
          </view>
        </view>
      </view>

      <view class="detail-section">
        <view class="section-title">特色菜品</view>
        <view class="special-dishes">
          <view 
            class="dish-item"
            v-for="(dish, index) in selectedRestaurantData.dishes"
            :key="index"
          >
            <text class="dish-icon">{{ dish.icon }}</text>
            <text class="dish-name">{{ dish.name }}</text>
          </view>
        </view>
      </view>

      <view class="detail-section">
        <view class="section-title">用户评价</view>
        <view class="reviews-list">
          <view 
            class="review-item"
            v-for="(review, index) in selectedRestaurantData.reviews"
            :key="index"
          >
            <view class="review-header">
              <view class="review-avatar">{{ review.avatar }}</view>
              <view class="review-user">
                <text class="review-name">{{ review.name }}</text>
                <text class="review-rating">⭐⭐⭐⭐�?/text>
              </view>
            </view>
            <view class="review-content">{{ review.content }}</view>
          </view>
        </view>
      </view>

      <view class="detail-actions">
        <view class="action-btn secondary" @click="showRoute">
          <text class="btn-icon">🗺�?/text>
          <text class="btn-text">导航到这�?/text>
        </view>
        <view class="action-btn secondary" @click="callRestaurant">
          <text class="btn-icon">📞</text>
          <text class="btn-text">电话</text>
        </view>
        <view class="action-btn primary" @click="favoriteRestaurant">
          <text class="btn-icon">{{ isFavorited ? '❤️' : '🤍' }}</text>
          <text class="btn-text">{{ isFavorited ? '已收�? : '收藏' }}</text>
        </view>
      </view>
    </view>

    <view class="route-panel" v-if="showRoutePanel">
      <view class="route-header">
        <view class="route-title">🗺�?路线规划</view>
        <view class="route-close" @click="closeRoute">�?/view>
      </view>
      <view class="route-info">
        <view class="route-point">
          <text class="point-label">起点</text>
          <text class="point-value">我的位置</text>
        </view>
        <view class="route-arrow">�?/view>
        <view class="route-point">
          <text class="point-label">终点</text>
          <text class="point-value">{{ selectedRestaurantData?.name }}</text>
        </view>
      </view>
      <view class="travel-modes">
        <view 
          class="mode-item"
          :class="{ active: travelMode === mode }"
          v-for="mode in travelModes"
          :key="mode.type"
          @click="selectTravelMode(mode.type)"
        >
          <text class="mode-icon">{{ mode.icon }}</text>
          <text class="mode-label">{{ mode.label }}</text>
        </view>
      </view>
      <view class="route-details">
        <view 
          class="route-option"
          v-for="(route, index) in routes"
          :key="index"
          :class="{ active: selectedRoute === index }"
          @click="selectRoute(index)"
        >
          <view class="route-option-header">
            <text class="route-option-icon">{{ route.icon }}</text>
            <view class="route-option-info">
              <text class="route-option-name">{{ route.name }}</text>
              <text class="route-option-meta">{{ route.distance }} · {{ route.time }}</text>
            </view>
          </view>
          <view class="route-option-desc">{{ route.description }}</view>
          <view class="route-option-warning" v-if="route.warning">
            <text class="warning-icon">⚠️</text>
            <text class="warning-text">{{ route.warning }}</text>
          </view>
        </view>
      </view>
      <view class="route-actions">
        <view class="route-btn primary" @click="startNavigation">
          <text class="btn-icon">🚀</text>
          <text class="btn-text">开始导�?/text>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  name: 'FoodMap',
  data() {
    return {
      searchQuery: '',
      activeCategory: '全部',
      categories: ['全部', '火锅', '川菜', '粤菜', '日料', '西餐'],
      selectedRestaurant: null,
      showRoutePanel: false,
      travelMode: 'walk',
      selectedRoute: 0,
      isFavorited: false,
      travelModes: [
        { type: 'walk', icon: '🚶', label: '步行' },
        { type: 'drive', icon: '🚗', label: '驾车' },
        { type: 'bus', icon: '🚌', label: '公交' }
      ],
      restaurants: [
        {
          name: '海底捞火�?,
          rating: 4.9,
          reviewCount: 12000,
          price: 120,
          location: '万达广场4�?,
          distance: 1.2,
          hours: '10:00 - 22:00',
          category: '火锅',
          x: 30,
          y: 40,
          dishes: [
            { icon: '🍲', name: '番茄锅底' },
            { icon: '🥩', name: '肥牛�? },
            { icon: '🦐', name: '虾滑' }
          ],
          reviews: [
            {
              avatar: '👤',
              name: '张三',
              content: '服务非常好，食材新鲜，强烈推荐！',
              rating: 5
            },
            {
              avatar: '👤',
              name: '李四',
              content: '环境不错，就是排队时间有点长',
              rating: 5
            }
          ]
        },
        {
          name: '外婆�?,
          rating: 4.6,
          reviewCount: 8500,
          price: 60,
          location: '银泰百货3�?,
          distance: 2.5,
          hours: '11:00 - 21:30',
          category: '川菜',
          x: 60,
          y: 30,
          dishes: [
            { icon: '🍖', name: '外婆红烧�? },
            { icon: '🥬', name: '清炒时蔬' },
            { icon: '🍲', name: '西湖牛肉�? }
          ],
          reviews: [
            {
              avatar: '👤',
              name: '王五',
              content: '味道正宗，价格实�?,
              rating: 5
            }
          ]
        },
        {
          name: '星巴�?,
          rating: 4.8,
          reviewCount: 5000,
          price: 35,
          location: '步行�?,
          distance: 0.8,
          hours: '07:00 - 22:00',
          category: '西餐',
          x: 45,
          y: 65,
          dishes: [
            { icon: '�?, name: '拿铁' },
            { icon: '🧁', name: '提拉米苏' },
            { icon: '🥐', name: '牛角�? }
          ],
          reviews: [
            {
              avatar: '👤',
              name: '赵六',
              content: '环境舒适，适合办公',
              rating: 5
            }
          ]
        }
      ]
    }
  },
  computed: {
    filteredRestaurants() {
      let filtered = this.restaurants
      
      if (this.activeCategory !== '全部') {
        filtered = filtered.filter(r => r.category === this.activeCategory)
      }
      
      if (this.searchQuery) {
        filtered = filtered.filter(r => 
          r.name.includes(this.searchQuery) || 
          r.category.includes(this.searchQuery)
        )
      }
      
      return filtered
    },
    selectedRestaurantData() {
      return this.selectedRestaurant !== null ? this.restaurants[this.selectedRestaurant] : null
    },
    routes() {
      const restaurant = this.selectedRestaurantData
      if (!restaurant) return []
      
      if (this.travelMode === 'walk') {
        return [
          {
            icon: '🚶',
            name: '步行路线',
            distance: `${restaurant.distance}km`,
            time: '�?5分钟',
            description: '沿人民路向东 �?右转进入万达�?�?到达',
            warning: null
          }
        ]
      } else if (this.travelMode === 'drive') {
        return [
          {
            icon: '🚗',
            name: '驾车路线',
            distance: '3.5km',
            time: '�?0分钟',
            description: '沿人民路向东 �?右转进入万达�?�?到达',
            warning: '停车：万达地下停车场B2�?
          }
        ]
      } else {
        return [
          {
            icon: '🚌',
            name: '公交路线',
            distance: '4.2km',
            time: '�?5分钟',
            description: '乘坐101�?�?万达广场站下�?�?步行300�?,
            warning: null
          }
        ]
      }
    }
  },
  methods: {
    handleSearch() {
      uni.showToast({
        title: '搜索�?..',
        icon: 'loading'
      })
    },
    
    selectCategory(category) {
      this.activeCategory = category
      uni.vibrateShort()
    },
    
    selectRestaurant(index) {
      this.selectedRestaurant = index
      uni.vibrateShort()
    },
    
    closeDetail() {
      this.selectedRestaurant = null
    },
    
    locateUser() {
      uni.showToast({
        title: '定位�?..',
        icon: 'loading'
      })
    },
    
    refreshMap() {
      uni.showToast({
        title: '刷新�?..',
        icon: 'loading'
      })
    },
    
    showRoute() {
      this.showRoutePanel = true
    },
    
    closeRoute() {
      this.showRoutePanel = false
    },
    
    selectTravelMode(mode) {
      this.travelMode = mode
      this.selectedRoute = 0
      uni.vibrateShort()
    },
    
    selectRoute(index) {
      this.selectedRoute = index
      uni.vibrateShort()
    },
    
    startNavigation() {
      uni.showToast({
        title: '开始导�?,
        icon: 'success'
      })
    },
    
    callRestaurant() {
      uni.showToast({
        title: '拨打电话',
        icon: 'none'
      })
    },
    
    favoriteRestaurant() {
      this.isFavorited = !this.isFavorited
      uni.showToast({
        title: this.isFavorited ? '已收�? : '已取消收�?,
        icon: 'success'
      })
    }
  }
}
</script>

<style scoped>
.food-map {
  min-height: 100vh;
  background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
  padding: 32rpx;
  padding-bottom: 200rpx;
}

.map-header {
  margin-bottom: 24rpx;
}

.search-bar {
  display: flex;
  align-items: center;
  gap: 16rpx;
  background: white;
  border-radius: 48rpx;
  padding: 16rpx 24rpx;
  box-shadow: 0 4rpx 16rpx rgba(239, 68, 68, 0.1);
}

.search-icon {
  font-size: 32rpx;
}

.search-input {
  flex: 1;
  height: 64rpx;
  font-size: 28rpx;
  color: #1e293b;
  background: transparent;
  border: none;
  outline: none;
}

.search-input::placeholder {
  color: #9ca3af;
}

.category-filter {
  display: flex;
  gap: 16rpx;
  overflow-x: auto;
  padding: 8rpx 0 24rpx 0;
  margin-bottom: 24rpx;
}

.filter-item {
  flex-shrink: 0;
  padding: 16rpx 32rpx;
  background: white;
  border-radius: 48rpx;
  font-size: 26rpx;
  color: #64748b;
  font-weight: 500;
  box-shadow: 0 2rpx 8rpx rgba(239, 68, 68, 0.08);
  transition: all 0.3s;
}

.filter-item.active {
  background: linear-gradient(135deg, #ef4444 0%, #f87171 100%);
  color: white;
  box-shadow: 0 4rpx 12rpx rgba(239, 68, 68, 0.3);
}

.map-container {
  position: relative;
  width: 100%;
  height: 600rpx;
  background: white;
  border-radius: 32rpx;
  overflow: hidden;
  box-shadow: 0 8rpx 24rpx rgba(239, 68, 68, 0.15);
  margin-bottom: 24rpx;
}

.map-placeholder {
  width: 100%;
  height: 100%;
  position: relative;
}

.map-bg {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
  position: relative;
}

.map-bg::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: 
    linear-gradient(rgba(239, 68, 68, 0.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(239, 68, 68, 0.05) 1px, transparent 1px);
  background-size: 40rpx 40rpx;
}

.map-markers {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
}

.map-marker {
  position: absolute;
  transform: translate(-50%, -50%);
  cursor: pointer;
  transition: all 0.3s;
}

.marker-icon {
  font-size: 48rpx;
  filter: drop-shadow(0 4rpx 8rpx rgba(0, 0, 0, 0.2));
  animation: bounce 2s ease-in-out infinite;
}

@keyframes bounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10rpx);
  }
}

.map-marker.active .marker-icon {
  font-size: 56rpx;
  animation: none;
}

.marker-info {
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  background: white;
  border-radius: 16rpx;
  padding: 16rpx 20rpx;
  box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.15);
  white-space: nowrap;
  margin-bottom: 16rpx;
  animation: slideUp 0.3s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateX(-50%) translateY(20rpx);
  }
  to {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }
}

.marker-name {
  display: block;
  font-size: 26rpx;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 4rpx;
}

.marker-rating {
  display: block;
  font-size: 22rpx;
  color: #f59e0b;
  margin-bottom: 4rpx;
}

.marker-price {
  display: block;
  font-size: 22rpx;
  color: #64748b;
}

.map-controls {
  position: absolute;
  right: 24rpx;
  bottom: 24rpx;
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.control-btn {
  width: 80rpx;
  height: 80rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  border-radius: 50%;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.15);
  transition: all 0.2s;
}

.control-btn:active {
  transform: scale(0.95);
}

.control-icon {
  font-size: 36rpx;
}

.restaurant-detail {
  background: white;
  border-radius: 32rpx;
  padding: 32rpx;
  box-shadow: 0 8rpx 24rpx rgba(239, 68, 68, 0.15);
  margin-bottom: 24rpx;
}

.detail-header {
  margin-bottom: 32rpx;
}

.detail-close {
  position: absolute;
  top: 24rpx;
  right: 24rpx;
  width: 48rpx;
  height: 48rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f3f4f6;
  border-radius: 50%;
  font-size: 28rpx;
  color: #64748b;
  cursor: pointer;
}

.detail-image-carousel {
  width: 100%;
  height: 400rpx;
  background: linear-gradient(135deg, #1e293b 0%, #374151 100%);
  border-radius: 24rpx;
  margin-bottom: 24rpx;
  overflow: hidden;
  position: relative;
}

.carousel-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16rpx;
}

.carousel-icon {
  font-size: 80rpx;
}

.carousel-text {
  font-size: 28rpx;
  color: rgba(255, 255, 255, 0.7);
}

.detail-name {
  font-size: 36rpx;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 16rpx;
}

.detail-rating {
  display: flex;
  align-items: center;
  gap: 16rpx;
  margin-bottom: 24rpx;
}

.rating-stars {
  font-size: 28rpx;
}

.rating-score {
  font-size: 28rpx;
  font-weight: 700;
  color: #1e293b;
}

.rating-count {
  font-size: 24rpx;
  color: #64748b;
}

.detail-meta {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 12rpx;
}

.meta-icon {
  font-size: 28rpx;
}

.meta-text {
  font-size: 26rpx;
  color: #4b5563;
}

.detail-section {
  margin-bottom: 32rpx;
}

.section-title {
  font-size: 28rpx;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 16rpx;
}

.special-dishes {
  display: flex;
  gap: 16rpx;
  flex-wrap: wrap;
}

.dish-item {
  display: flex;
  align-items: center;
  gap: 8rpx;
  padding: 12rpx 20rpx;
  background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
  border-radius: 48rpx;
  font-size: 24rpx;
  color: #b91c1c;
  font-weight: 500;
}

.dish-icon {
  font-size: 28rpx;
}

.dish-name {
  font-size: 24rpx;
}

.reviews-list {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.review-item {
  padding: 20rpx;
  background: #f9fafb;
  border-radius: 16rpx;
}

.review-header {
  display: flex;
  align-items: center;
  gap: 16rpx;
  margin-bottom: 12rpx;
}

.review-avatar {
  font-size: 40rpx;
}

.review-user {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4rpx;
}

.review-name {
  font-size: 26rpx;
  font-weight: 600;
  color: #1e293b;
}

.review-rating {
  font-size: 22rpx;
}

.review-content {
  font-size: 24rpx;
  line-height: 1.6;
  color: #4b5563;
}

.detail-actions {
  display: flex;
  gap: 16rpx;
}

.action-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8rpx;
  padding: 20rpx 32rpx;
  border-radius: 24rpx;
  font-size: 26rpx;
  font-weight: 600;
  transition: all 0.2s;
}

.action-btn:active {
  transform: scale(0.98);
}

.action-btn.secondary {
  background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
  color: #b91c1c;
  box-shadow: 0 4rpx 12rpx rgba(239, 68, 68, 0.1);
}

.action-btn.primary {
  background: linear-gradient(135deg, #ef4444 0%, #f87171 100%);
  color: white;
  box-shadow: 0 4rpx 12rpx rgba(239, 68, 68, 0.3);
}

.btn-icon {
  font-size: 28rpx;
}

.btn-text {
  font-size: 26rpx;
}

.route-panel {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: white;
  border-radius: 32rpx 32rpx 0 0;
  padding: 32rpx;
  box-shadow: 0 -8rpx 32rpx rgba(0, 0, 0, 0.15);
  max-height: 80vh;
  overflow-y: auto;
  z-index: 2000;
}

.route-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32rpx;
}

.route-title {
  font-size: 32rpx;
  font-weight: 700;
  color: #1e293b;
}

.route-close {
  width: 48rpx;
  height: 48rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f3f4f6;
  border-radius: 50%;
  font-size: 28rpx;
  color: #64748b;
  cursor: pointer;
}

.route-info {
  display: flex;
  align-items: center;
  gap: 16rpx;
  margin-bottom: 32rpx;
  padding: 24rpx;
  background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
  border-radius: 24rpx;
}

.route-point {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}

.point-label {
  font-size: 22rpx;
  color: #b91c1c;
  font-weight: 600;
}

.point-value {
  font-size: 26rpx;
  color: #1e293b;
  font-weight: 600;
}

.route-arrow {
  font-size: 32rpx;
  color: #b91c1c;
}

.travel-modes {
  display: flex;
  gap: 16rpx;
  margin-bottom: 32rpx;
}

.mode-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8rpx;
  padding: 20rpx;
  background: #f9fafb;
  border-radius: 16rpx;
  border: 2rpx solid transparent;
  transition: all 0.3s;
}

.mode-item.active {
  background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
  border-color: #ef4444;
}

.mode-icon {
  font-size: 36rpx;
}

.mode-label {
  font-size: 24rpx;
  color: #4b5563;
  font-weight: 500;
}

.mode-item.active .mode-label {
  color: #b91c1c;
}

.route-details {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
  margin-bottom: 32rpx;
}

.route-option {
  padding: 24rpx;
  background: #f9fafb;
  border-radius: 20rpx;
  border: 2rpx solid transparent;
  transition: all 0.3s;
}

.route-option.active {
  background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
  border-color: #ef4444;
}

.route-option-header {
  display: flex;
  align-items: center;
  gap: 16rpx;
  margin-bottom: 12rpx;
}

.route-option-icon {
  font-size: 36rpx;
}

.route-option-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4rpx;
}

.route-option-name {
  font-size: 26rpx;
  font-weight: 600;
  color: #1e293b;
}

.route-option-meta {
  font-size: 24rpx;
  color: #64748b;
}

.route-option-desc {
  font-size: 24rpx;
  line-height: 1.6;
  color: #4b5563;
  margin-bottom: 12rpx;
}

.route-option-warning {
  display: flex;
  align-items: center;
  gap: 8rpx;
  padding: 12rpx;
  background: rgba(245, 158, 11, 0.1);
  border-radius: 12rpx;
}

.warning-icon {
  font-size: 24rpx;
}

.warning-text {
  font-size: 22rpx;
  color: #92400e;
}

.route-actions {
  display: flex;
}

.route-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12rpx;
  padding: 24rpx;
  border-radius: 24rpx;
  font-size: 28rpx;
  font-weight: 600;
  transition: all 0.2s;
}

.route-btn:active {
  transform: scale(0.98);
}

.route-btn.primary {
  background: linear-gradient(135deg, #ef4444 0%, #f87171 100%);
  color: white;
  box-shadow: 0 4rpx 12rpx rgba(239, 68, 68, 0.3);
}
</style>