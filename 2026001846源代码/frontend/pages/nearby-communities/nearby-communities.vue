<template>
  <view class="nearby-container">
    <!-- 顶部搜索 -->
    <view class="search-section">
      <view class="search-bar">
        <text class="search-icon">🔍</text>
        <input 
          class="search-input" 
          placeholder="搜索社区名称或简介"
          @confirm="handleSearch"
        />
        <view class="search-btn" @click="handleSearch">搜索</view>
      </view>
    </view>

    <!-- 筛选栏 -->
    <view class="filter-section">
      <scroll-view class="filter-scroll" scroll-x>
        <view class="filter-tabs">
          <view 
            v-for="(filter, index) in filters" 
            :key="index"
            class="filter-tab"
            :class="{ 'active': currentFilter === index }"
            @click="switchFilter(index)"
          >
            <text class="filter-text">{{ filter.label }}</text>
          </view>
        </view>
      </scroll-view>
    </view>

    <!-- 排序选项 -->
    <view class="sort-section">
      <view class="sort-options">
        <view 
          v-for="(sort, index) in sortOptions" 
          :key="index"
          class="sort-item"
          :class="{ 'active': currentSort === index }"
          @click="switchSort(index)"
        >
          <text class="sort-text">{{ sort.label }}</text>
          <text class="sort-icon" v-if="currentSort === index">✓</text>
        </view>
      </view>
    </view>

    <!-- 社区列表 -->
    <scroll-view 
      class="communities-scroll" 
      scroll-y 
      @scrolltolower="loadMore"
      :lower-threshold="100"
    >
      <view class="communities-list">
        <view 
          v-for="(community, index) in communities" 
          :key="community.id"
          class="community-card"
          @click="goToDetail(community.id)"
        >
          <!-- 社区封面 -->
          <view class="community-cover">
            <image 
              :src="community.cover_image || '../../static/equipment.png'" 
              mode="aspectFill" 
              class="cover-image"
            ></image>
            <view class="cover-overlay">
              <view class="community-category">{{ community.category }}</view>
              <view class="distance-badge" v-if="community.distance">
                {{ community.distance }}km
              </view>
            </view>
          </view>

          <!-- 社区信息 -->
          <view class="community-info">
            <view class="info-header">
              <image 
                :src="community.avatar || '../../static/GGbond.png'" 
                mode="aspectFill" 
                class="community-avatar"
              ></image>
              <view class="info-main">
                <text class="community-name">{{ community.name }}</text>
                <text class="community-desc">{{ community.description }}</text>
              </view>
              <view class="join-status" v-if="community.is_joined">
                <text class="joined-text">已加入</text>
              </view>
            </view>

            <!-- 社区数据 -->
            <view class="community-stats">
              <view class="stat-item">
                <text class="stat-icon">👥</text>
                <text class="stat-text">{{ community.current_members }}/{{ community.max_members }}</text>
              </view>
              <view class="stat-item">
                <text class="stat-icon">📝</text>
                <text class="stat-text">{{ community.post_count }}帖子</text>
              </view>
              <view class="stat-item">
                <text class="stat-icon">🔥</text>
                <text class="stat-text">{{ community.activity_score }}活跃</text>
              </view>
            </view>

            <!-- 成员进度 -->
            <view class="member-progress">
              <view class="progress-bar">
                <view 
                  class="progress-fill" 
                  :style="{ width: community.member_percentage + '%' }"
                ></view>
              </view>
              <text class="progress-text">{{ community.member_percentage }}%</text>
            </view>

            <!-- 标签 -->
            <view class="community-tags" v-if="community.tags && community.tags.length > 0">
              <view 
                v-for="(tag, tagIndex) in community.tags.slice(0, 3)" 
                :key="tagIndex"
                class="tag-item"
              >
                {{ tag }}
              </view>
            </view>

            <!-- 操作按钮 -->
          </view>
        </view>

        <!-- 加载中-->
        <view class="loading-more" v-if="loading">
          <text class="loading-text">加载中...</text>
        </view>

        <!-- 没有更多 -->
        <view class="no-more" v-if="!hasMore && communities.length > 0">
          <text class="no-more-text">已加载全部社区</text>
        </view>

        <!-- 空状态 -->
        <view class="empty-state" v-if="communities.length === 0 && !loading">
          <text class="empty-icon">🏘️</text>
          <text class="empty-text">附近暂无社区</text>
          <text class="empty-hint">换个位置或搜索条件试试</text>
        </view>
      </view>
    </scroll-view>
  </view>
</template>

<script>
import { API_HOST } from '../../utils/request.js'

const COMMUNITY_API_BASE = `${API_HOST}:5000/api/community`

export default {
  data() {
    return {
      searchKeyword: '',
      currentFilter: 0,
      currentSort: 0,
      communities: [],
      loading: false,
      hasMore: true,
      page: 1,
      userLocation: null,
      
      filters: [
        { label: '全部', value: 'all' },
        { label: '健康', value: 'health' },
        { label: '检修', value: 'repair' },
        { label: '保养', value: 'maintenance' },
        { label: '环保', value: 'environment' },
        { label: '案例', value: 'cases' }
      ],
      
      sortOptions: [
        { label: '距离最近', value: 'distance' },
        { label: '成员最多', value: 'members' },
        { label: '最活跃', value: 'activity' }
      ]
    }
  },

  onLoad() {
    this.getUserLocation();
  },

  methods: {
    async getUserLocation() {
      try {
        const location = await this.getLocation();
        this.userLocation = location;
        this.loadCommunities();
      } catch (error) {
        console.error('获取位置失败:', error);
        uni.showToast({
          title: '获取位置失败,使用默认位置',
          icon: 'none'
        });
        this.userLocation = { lat: 39.9042, lon: 116.4074 };
        this.loadCommunities();
      }
    },

    getLocation() {
      return new Promise((resolve, reject) => {
        uni.getLocation({
          type: 'gcj02',
          success: (res) => {
            resolve({
              lat: res.latitude,
              lon: res.longitude
            });
          },
          fail: (err) => {
            reject(err);
          }
        });
      });
    },

    async loadCommunities() {
      if (this.loading || !this.hasMore) return;
      
      this.loading = true;
      try {
        const params = {
          lat: this.userLocation.lat,
          lon: this.userLocation.lon,
          sort_by: this.sortOptions[this.currentSort].value,
          page: this.page,
          page_size: 10
        };

        if (this.currentFilter > 0) {
          params.category = this.filters[this.currentFilter].value;
        }

        const response = await uni.request({
          url: `${COMMUNITY_API_BASE}/nearby`,
          method: 'GET',
          data: params
        });

        if (response.data.code === 200) {
          const newCommunities = response.data.data.communities;
          if (this.page === 1) {
            this.communities = newCommunities;
          } else {
            this.communities = [...this.communities, ...newCommunities];
          }
          
          this.hasMore = this.page < response.data.data.total_pages;
          this.page++;
        } else {
          uni.showToast({
            title: response.data.message || '加载失败',
            icon: 'none'
          });
        }
      } catch (error) {
        console.error('加载社区失败:', error);
        uni.showToast({
          title: '网络错误，请重试',
          icon: 'none'
        });
      } finally {
        this.loading = false;
      }
    },

    loadMore() {
      this.loadCommunities();
    },

    handleSearch() {
      if (!this.searchKeyword.trim()) {
        this.loadCommunities();
        return;
      }

      this.searchCommunities();
    },

    async searchCommunities() {
      this.loading = true;
      try {
        const params = {
          keyword: this.searchKeyword,
          page: 1,
          page_size: 20
        };

        if (this.currentFilter > 0) {
          params.category = this.filters[this.currentFilter].value;
        }

        const response = await uni.request({
          url: `${COMMUNITY_API_BASE}/search`,
          method: 'GET',
          data: params
        });

        if (response.data.code === 200) {
          this.communities = response.data.data.communities;
          this.hasMore = false;
        } else {
          uni.showToast({
            title: response.data.message || '搜索失败',
            icon: 'none'
          });
        }
      } catch (error) {
        console.error('搜索失败:', error);
        uni.showToast({
          title: '网络错误，请重试',
          icon: 'none'
        });
      } finally {
        this.loading = false;
      }
    },

    switchFilter(index) {
      this.currentFilter = index;
      this.page = 1;
      this.hasMore = true;
      this.communities = [];
      
      if (this.searchKeyword) {
        this.searchCommunities();
      } else {
        this.loadCommunities();
      }
    },

    switchSort(index) {
      this.currentSort = index;
      this.page = 1;
      this.hasMore = true;
      this.communities = [];
      this.loadCommunities();
    },

    goToDetail(communityId) {
      uni.navigateTo({
        url: `/pages/community-detail/community-detail?id=${communityId}`
      });
    }
  }
}
</script>

<style scoped>
.nearby-container {
  min-height: 100vh;
  background: #F8FAFC;
  padding-bottom: 120rpx;
}

/* 搜索区块*/
.search-section {
  background: white;
  padding: 24rpx 32rpx;
  box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.06);
}

.search-bar {
  display: flex;
  align-items: center;
  background: #F1F5F9;
  border-radius: 32rpx;
  padding: 16rpx 24rpx;
  gap: 16rpx;
}

.search-icon {
  font-size: 32rpx;
}

.search-input {
  flex: 1;
  font-size: 28rpx;
  color: #334155;
}

.search-btn {
  background: linear-gradient(135deg, #10b981, #0ea5e9);
  color: white;
  padding: 12rpx 32rpx;
  border-radius: 24rpx;
  font-size: 26rpx;
  font-weight: 600;
}

/* 筛选栏 */
.filter-section {
  background: white;
  padding: 20rpx 0;
  border-bottom: 2rpx solid #F1F5F9;
}

.filter-scroll {
  white-space: nowrap;
}

.filter-tabs {
  display: flex;
  padding: 0 32rpx;
  gap: 16rpx;
}

.filter-tab {
  display: inline-block;
  padding: 12rpx 28rpx;
  background: #F1F5F9;
  border-radius: 24rpx;
  transition: all 0.3s;
}

.filter-tab.active {
  background: linear-gradient(135deg, #10b981, #0ea5e9);
  color: white;
}

.filter-text {
  font-size: 26rpx;
  font-weight: 500;
}

/* 排序选项 */
.sort-section {
  background: white;
  padding: 20rpx 32rpx;
  border-bottom: 2rpx solid #F1F5F9;
}

.sort-options {
  display: flex;
  gap: 32rpx;
}

.sort-item {
  display: flex;
  align-items: center;
  gap: 8rpx;
  padding: 8rpx 0;
  transition: all 0.3s;
}

.sort-item.active {
  color: #10b981;
  font-weight: 600;
}

.sort-text {
  font-size: 26rpx;
  color: #64748b;
}

.sort-item.active .sort-text {
  color: #10b981;
}

.sort-icon {
  font-size: 20rpx;
}

/* 社区列表 */
.communities-scroll {
  height: calc(100vh - 280rpx);
}

.communities-list {
  padding: 24rpx 32rpx;
  display: flex;
  flex-direction: column;
  gap: 24rpx;
}

.community-card {
  background: white;
  border-radius: 32rpx;
  overflow: hidden;
  box-shadow: 0 4rpx 16rpx rgba(0,0,0,0.06);
  transition: all 0.3s;
}

.community-card:active {
  transform: scale(0.98);
}

/* 社区封面 */
.community-cover {
  position: relative;
  height: 300rpx;
}

.cover-image {
  width: 100%;
  height: 100%;
}

.cover-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(to bottom, rgba(0,0,0,0.1) 0%, transparent 50%, rgba(0,0,0,0.3) 100%);
  display: flex;
  justify-content: space-between;
  padding: 20rpx;
}

.community-category {
  background: rgba(16, 185, 129, 0.9);
  color: white;
  padding: 8rpx 20rpx;
  border-radius: 20rpx;
  font-size: 22rpx;
  font-weight: 600;
}

.distance-badge {
  background: rgba(255, 255, 255, 0.95);
  color: #0f172a;
  padding: 8rpx 20rpx;
  border-radius: 20rpx;
  font-size: 22rpx;
  font-weight: 600;
  box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.1);
}

/* 社区信息 */
.community-info {
  padding: 24rpx;
}

.info-header {
  display: flex;
  align-items: flex-start;
  gap: 16rpx;
  margin-bottom: 20rpx;
}

.community-avatar {
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
  border: 3rpx solid #E2E8F0;
}

.info-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}

.community-name {
  font-size: 32rpx;
  font-weight: 700;
  color: #0f172a;
  display: block;
}

.community-desc {
  font-size: 24rpx;
  color: #64748b;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.join-status {
  background: linear-gradient(135deg, #10b981, #0ea5e9);
  padding: 8rpx 20rpx;
  border-radius: 20rpx;
}

.joined-text {
  color: white;
  font-size: 22rpx;
  font-weight: 600;
}

/* 社区数据 */
.community-stats {
  display: flex;
  gap: 24rpx;
  margin-bottom: 16rpx;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 8rpx;
}

.stat-icon {
  font-size: 28rpx;
}

.stat-text {
  font-size: 24rpx;
  color: #64748b;
  font-weight: 500;
}

/* 成员进度样式*/
.member-progress {
  display: flex;
  align-items: center;
  gap: 16rpx;
  margin-bottom: 16rpx;
}

.progress-bar {
  flex: 1;
  height: 8rpx;
  background: #E2E8F0;
  border-radius: 8rpx;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #10b981, #0ea5e9);
  border-radius: 8rpx;
  transition: width 0.3s;
}

.progress-text {
  font-size: 22rpx;
  color: #64748b;
  font-weight: 600;
  white-space: nowrap;
}

/* 标签 */
.community-tags {
  display: flex;
  gap: 12rpx;
  flex-wrap: wrap;
}

.tag-item {
  background: #F1F5F9;
  color: #475569;
  padding: 8rpx 20rpx;
  border-radius: 16rpx;
  font-size: 22rpx;
  font-weight: 500;
}

/* 加载状态*/
.loading-more, .no-more {
  text-align: center;
  padding: 40rpx 0;
}

.loading-text, .no-more-text {
  font-size: 24rpx;
  color: #94a3b8;
  font-weight: 500;
}

/* 空状态样式*/
.empty-state {
  text-align: center;
  padding: 120rpx 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 24rpx;
}

.empty-icon {
  font-size: 120rpx;
}

.empty-text {
  font-size: 28rpx;
  color: #64748b;
  font-weight: 600;
}

.empty-hint {
  font-size: 24rpx;
  color: #94a3b8;
}
</style>
