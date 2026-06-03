<template>
  <view class="my-uploads-container">
    <custom-navbar title="我的数据" :show-back="true" />
    <view class="content">
      <view class="tabs-container">
        <view 
          v-for="tab in tabs" 
          :key="tab.key" 
          class="tab-item"
          :class="{ active: currentTab === tab.key }"
          @click="switchTab(tab.key)"
        >
          <text class="tab-label">{{ tab.label }}</text>
          <view class="tab-badge" v-if="totalCount[tab.key] > 0">
            {{ totalCount[tab.key] }}
          </view>
        </view>
      </view>

      <view class="data-container">
        <view class="loading-container" v-if="loading">
          <view class="loading-spinner"></view>
          <text class="loading-text">正在加载...</text>
        </view>

        <view v-else-if="currentData.length === 0" class="empty-container">
          <text class="empty-icon">📭</text>
          <text class="empty-text">暂无数据</text>
        </view>

        <view v-else class="data-list">
          <view 
            v-for="item in currentData" 
            :key="item.id" 
            class="data-item"
            @click="handleItemClick(item)"
          >
            <view class="item-header">
              <text class="item-title">{{ getItemTitle(item) }}</text>
              <text class="item-date">{{ formatDate(item.created_at || item.visited_at) }}</text>
            </view>
            <view class="item-image-wrap" v-if="item.type === 'takeaway_analysis' && item.image" @click.stop="previewImage(item.image, getItemTitle(item))">
              <image class="item-image" :src="item.image" mode="aspectFill"></image>
              <view class="image-overlay">
                <text class="image-overlay-text">点击查看大图</text>
              </view>
            </view>
            <view class="item-content">
              <view class="item-details">
                <text class="detail-item" v-for="(value, key) in getItemDetails(item)" :key="key">
                  {{ key }}: {{ value }}
                </text>
              </view>
            </view>
          </view>
        </view>

        <view class="pagination" v-if="totalPages > 1">
          <button 
            class="page-btn" 
            :disabled="currentPage === 1"
            @click="changePage(currentPage - 1)"
          >
            上一页
          </button>
          <text class="page-info">{{ currentPage }} / {{ totalPages }}</text>
          <button 
            class="page-btn" 
            :disabled="currentPage === totalPages"
            @click="changePage(currentPage + 1)"
          >
            下一页
          </button>
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
      tabs: [
        { key: 'all', label: '全部' },
        { key: 'health_records', label: '健康记录' },
        { key: 'takeaway_analysis', label: '外卖分析' },
        { key: 'favorites', label: '收藏' },
        { key: 'browse_history', label: '浏览历史' }
      ],
      currentTab: 'all',
      loading: false,
      currentPage: 1,
      pageSize: 10,
      totalCount: {
        all: 0,
        health_records: 0,
        takeaway_analysis: 0,
        favorites: 0,
        browse_history: 0
      },
      allData: {
        health_records: [],
        takeaway_analysis: [],
        favorites: [],
        browse_history: []
      }
    }
  },
  computed: {
    currentData() {
      if (this.currentTab === 'all') {
        const allItems = []
        Object.keys(this.allData).forEach(key => {
          allItems.push(...this.allData[key].map(item => ({ ...item, type: key })))
        })
        return allItems.sort((a, b) => {
          const dateA = new Date(a.created_at || a.visited_at)
          const dateB = new Date(b.created_at || b.visited_at)
          return dateB - dateA
        })
      }
      return this.allData[this.currentTab] || []
    },
    totalPages() {
      const total = this.totalCount[this.currentTab]
      return Math.ceil(total / this.pageSize)
    }
  },
  async onLoad() {
    await this.loadData()
  },
  methods: {
    async loadData() {
      this.loading = true
      try {
        const res = await request.get('/api/user/my-uploads', {
          page: this.currentPage,
          page_size: this.pageSize,
          type: this.currentTab
        })

        if (res.code === 200) {
          const data = res.data
          
          if (this.currentTab === 'all') {
            this.allData.health_records = data.health_records || []
            this.allData.takeaway_analysis = data.takeaway_analysis || []
            this.allData.favorites = data.favorites || []
            this.allData.browse_history = data.browse_history || []
            
            this.totalCount.all = data.total.health_records + data.total.takeaway_analysis + 
                               data.total.favorites + data.total.browse_history
            this.totalCount.health_records = data.total.health_records
            this.totalCount.takeaway_analysis = data.total.takeaway_analysis
            this.totalCount.favorites = data.total.favorites
            this.totalCount.browse_history = data.total.browse_history
          } else {
            this.allData[this.currentTab] = data[this.currentTab] || []
            this.totalCount[this.currentTab] = data.total[this.currentTab]
          }
        }
      } catch (error) {
        console.error('加载数据失败:', error)
        uni.showToast({
          title: '加载失败',
          icon: 'none'
        })
      } finally {
        this.loading = false
      }
    },

    switchTab(tabKey) {
      if (this.currentTab === tabKey) return
      
      this.currentTab = tabKey
      this.currentPage = 1
      
      if (tabKey !== 'all') {
        this.loadData()
      }
    },

    changePage(page) {
      if (page < 1 || page > this.totalPages) return
      
      this.currentPage = page
      this.loadData()
    },

    getItemTitle(item) {
      if (item.type === 'health_records') {
        return `健康记录 - ${item.record_date}`
      } else if (item.type === 'takeaway_analysis') {
        return item.name || '外卖分析'
      } else if (item.type === 'favorites') {
        return item.title || '收藏'
      } else if (item.type === 'browse_history') {
        return item.title || '浏览记录'
      }
      return '未知数据'
    },

    getItemDetails(item) {
      if (item.type === 'health_records') {
        return {
          '卡路里': item.calories + ' kcal',
          '蛋白质': item.protein + 'g',
          '脂肪': item.fat + 'g',
          '碳水': item.carbs + 'g',
          '步数': item.steps,
          '饮水': item.water + 'ml'
        }
      } else if (item.type === 'takeaway_analysis') {
        return {
          '评分': item.score,
          '卡路里': item.calories + ' kcal',
          '蛋白质': item.protein + 'g',
          '脂肪': item.fat + 'g',
          '碳水': item.carbs + 'g'
        }
      } else if (item.type === 'favorites') {
        return {
          '类型': this.getTypeLabel(item.type),
          'ID': item.item_id
        }
      } else if (item.type === 'browse_history') {
        return {
          '类型': this.getTypeLabel(item.type)
        }
      }
      return {}
    },

    getTypeLabel(type) {
      const labels = {
        'restaurant': '餐厅',
        'recipe': '菜谱',
        'takeaway': '外卖',
        'health': '健康',
        'other': '其他'
      }
      return labels[type] || type
    },

    formatDate(dateStr) {
      if (!dateStr) return '--'
      
      const date = new Date(dateStr)
      const now = new Date()
      const diff = now - date
      
      const minutes = Math.floor(diff / 60000)
      const hours = Math.floor(diff / 3600000)
      const days = Math.floor(diff / 86400000)
      
      if (minutes < 1) return '刚刚'
      if (minutes < 60) return `${minutes}分钟前`
      if (hours < 24) return `${hours}小时前`
      if (days < 7) return `${days}天前`
      
      return `${date.getMonth() + 1}-${date.getDate()}`
    },

    handleItemClick(item) {
      uni.showModal({
        title: this.getItemTitle(item),
        content: JSON.stringify(this.getItemDetails(item), null, 2),
        showCancel: false
      })
    },

    previewImage(imageSrc, title) {
      if (!imageSrc) {
        uni.showToast({ title: '暂无图片', icon: 'none' });
        return;
      }
      uni.navigateTo({
        url: '/pages/image-viewer/image-viewer?src=' + encodeURIComponent(imageSrc) + '&title=' + encodeURIComponent(title || '订单图片')
      });
    }
  }
}
</script>

<style scoped>
.my-uploads-container {
  min-height: 100vh;
  background: #f5f5f5;
  padding-top: calc(var(--status-bar-height) + 140rpx);
}

.content {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 100rpx);
}

.tabs-container {
  display: flex;
  background: white;
  padding: 0 20rpx;
  border-bottom: 1px solid #e0e0e0;
  position: sticky;
  top: 0;
  z-index: 10;
}

.tab-item {
  flex: 1;
  height: 88rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  transition: all 0.3s ease;
}

.tab-item.active {
  color: #10b981;
  font-weight: 600;
}

.tab-item.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 60rpx;
  height: 4rpx;
  background: #10b981;
  border-radius: 2rpx;
}

.tab-label {
  font-size: 28rpx;
}

.tab-badge {
  position: absolute;
  top: 10rpx;
  right: 20rpx;
  background: #ef4444;
  color: white;
  font-size: 20rpx;
  padding: 2rpx 8rpx;
  border-radius: 10rpx;
  min-width: 32rpx;
  text-align: center;
}

.data-container {
  flex: 1;
  overflow-y: auto;
  padding: 20rpx;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 120rpx 0;
}

.loading-spinner {
  width: 64rpx;
  height: 64rpx;
  border: 6rpx solid #f1f5f9;
  border-top-color: #10b981;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text {
  margin-top: 24rpx;
  font-size: 24rpx;
  color: #64748b;
}

.empty-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 120rpx 0;
}

.empty-icon {
  font-size: 120rpx;
  margin-bottom: 24rpx;
}

.empty-text {
  font-size: 28rpx;
  color: #94a3b8;
}

.data-list {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.data-item {
  background: white;
  border-radius: 20rpx;
  padding: 24rpx;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.data-item:active {
  transform: scale(0.98);
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.1);
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16rpx;
}

.item-title {
  font-size: 30rpx;
  font-weight: 600;
  color: #1e293b;
}

.item-date {
  font-size: 22rpx;
  color: #94a3b8;
}

.item-image-wrap {
  position: relative;
  margin-bottom: 16rpx;
  border-radius: 12rpx;
  overflow: hidden;
}

.item-image {
  width: 100%;
  height: 300rpx;
  display: block;
}

.image-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 12rpx 20rpx;
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.5));
  display: flex;
  align-items: flex-end;
  justify-content: flex-end;
}

.image-overlay-text {
  font-size: 22rpx;
  color: rgba(255, 255, 255, 0.9);
  background: rgba(0, 0, 0, 0.3);
  padding: 6rpx 16rpx;
  border-radius: 20rpx;
}

.item-content {
  background: #f8fafc;
  border-radius: 12rpx;
  padding: 16rpx;
}

.item-details {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
}

.detail-item {
  font-size: 24rpx;
  color: #64748b;
  background: white;
  padding: 8rpx 16rpx;
  border-radius: 8rpx;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 24rpx;
  padding: 40rpx 0;
}

.page-btn {
  padding: 16rpx 32rpx;
  background: #10b981;
  color: white;
  border: none;
  border-radius: 12rpx;
  font-size: 26rpx;
  font-weight: 600;
}

.page-btn:disabled {
  background: #cbd5e1;
  color: #94a3b8;
}

.page-btn::after {
  border: none;
}

.page-info {
  font-size: 26rpx;
  color: #64748b;
  font-weight: 600;
}
</style>
