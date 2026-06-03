<template>
  <view class="home-container">
    <view class="home-navbar" :style="{ paddingTop: statusBarHeight + 'px' }">
      <view class="home-navbar-content">
        <view class="home-brand-block">
          <image src="../../static/icon-home.png" class="home-brand-icon" mode="aspectFit"></image>
          <text class="home-brand-name">{{ brandTitle }}</text>
        </view>
      </view>
    </view>
    <view class="home-content">
      <!-- 杞挱鍥惧尯鍩?-->
      <view class="banner-section">
        <swiper class="banner-swiper" circular autoplay interval="4000" duration="600" indicator-dots indicator-active-color="#667eea" indicator-color="rgba(255,255,255,0.4)">
          <swiper-item v-for="(banner, index) in banners" :key="index">
            <view class="banner-item" @tap="onBannerClick(banner)">
              <image :src="banner.image" mode="aspectFill" class="banner-img"></image>
              <view class="banner-overlay">
                <text class="banner-title">{{ banner.title }}</text>
                <text class="banner-sub">智学多智能体 · {{ banner.sub }}</text>
              </view>
            </view>
          </swiper-item>
        </swiper>
      </view>

    </view>

    <!-- 鍔熻兘鍏ュ彛 -->
    <view class="functions-section">
      <text class="section-title">核心功能</text>
      <view class="function-grid">
        <view
          v-for="(func, index) in functions"
          :key="index"
          class="feature-card"
          :class="func.bgClass"
          @click="navigateTo(func.path)"
        >
          <view class="feature-icon-wrap">
            <image v-if="func.image" :src="func.image" class="feature-icon-img" mode="aspectFit" />
            <text v-else class="feature-icon">{{ func.icon }}</text>
          </view>
          <text class="feature-name">{{ func.name }}</text>
          <text class="feature-desc">{{ func.desc }}</text>
        </view>
      </view>
    </view>

    <view class="bottom-section">
      <view class="community-header">
        <text class="community-title">学习共创</text>
        <view class="nearby-btn" @click="goToNearbyCommunities">
          <text class="nearby-icon">🧭</text>
          <text class="nearby-text">课程空间</text>
        </view>
      </view>

      <!-- Tab 閫夐」鍗?-->
      <view class="tabs-section">
        <view
          v-for="(tab, index) in tabs"
          :key="index"
          class="tab-item"
          :class="[getTabClass(tab.value), { 'active': currentTab === index }]"
          :style="getTabInlineStyle(tab.value, currentTab === index)"
          @click="switchTab(index)"
        >
          <text class="tab-text">{{ tab.label }}</text>
          <view class="tab-dot" v-if="currentTab === index"></view>
        </view>
      </view>

      <!-- 甯栧瓙鍒楄〃 -->
      <scroll-view
        class="posts-scroll"
        scroll-y="true"
        @scrolltolower="loadMorePosts"
        :lower-threshold="100"
      >
        <view class="posts-list">
          <view
            v-for="(post, index) in filteredPosts"
            :key="post.id"
            class="post-card"
          >
            <!-- 浣滆€呬俊鎭?-->
            <view class="post-author">
              <image :src="normalizeUserAvatar(post.author && post.author.avatar)" mode="aspectFill" class="author-avatar"></image>
              <view class="author-info">
                <text class="author-name">{{ post.author.name }}</text>
                <text class="post-time">{{ formatTime(post.createdAt) }}</text>
              </view>
              <view class="category-chip" :class="getCategoryClass(post.category)">
                {{ post.category }}
              </view>
            </view>

            <!-- 甯栧瓙鍐呭 -->
            <view class="post-content">
              <text class="post-text">{{ post.content }}</text>
              <image
                v-if="post.images && post.images.length > 0"
                :src="post.images[0]"
                mode="aspectFill"
                class="post-image"
              ></image>
            </view>

            <!-- 纰冲噺鎺掓暟鎹紙浠呯⒊瓒宠抗甯栧瓙鏄剧ず锛?-->
            <view class="carbon-stats" v-if="post.carbonSaved">
              <text class="carbon-stat-item">📈 掌握度 {{ post.carbonSaved }} 分</text>
              <text class="carbon-stat-item">+{{ post.carbonPoints }} 学习积分</text>
            </view>

            <!-- 浜掑姩鏁版嵁 -->
            <view class="post-actions">
              <view class="action-item" @click.stop="likePost(post)">
                <text class="action-icon">{{ post.isLiked ? '❤️' : '👍' }}</text>
                <text class="action-count">{{ post.likes }}</text>
              </view>
              <view class="action-item" @click.stop="commentPost(post)">
                <text class="action-icon">💬</text>
                <text class="action-count">{{ post.comments }}</text>
              </view>
              <view class="action-item" @click.stop="sharePost(post)">
                <text class="action-icon">📤</text>
                <text class="action-count">{{ post.shares }}</text>
              </view>
              <view class="action-item delete-action" v-if="canDeletePost(post)" @click.stop="deletePost(post)">
                <text class="delete-text">删除</text>
              </view>
            </view>
          </view>

          <!-- 鍔犺浇涓?-->
          <view class="loading-more" v-if="loading">
            <text class="loading-text">加载中...</text>
          </view>

          <!-- 娌℃湁鏇村 -->
          <view class="no-more" v-if="!hasMore && posts.length > 0">
            <text class="no-more-text">已加载全部内容</text>
          </view>

          <!-- 绌虹姸鎬?-->
          <view class="empty-state" v-if="filteredPosts.length === 0 && !loading">
            <text class="empty-icon">{{ currentTab === 3 ? '📈' : '📝' }}</text>
            <text class="empty-text">{{ currentTab === 3 ? '快来记录一次学习评估吧！' : '暂无内容，快来发布第一条学习笔记吧！' }}</text>
            <button class="empty-action" @click="showPostModal = true">
              {{ currentTab === 3 ? '记录评估' : '发布笔记' }}
            </button>
          </view>
        </view>
      </scroll-view>
    </view>

    <view class="fab-post-btn" @click="showPostModal = true">
      <text class="fab-icon">✍️</text>
      <text class="fab-text">发布</text>
    </view>

    <view class="modal-overlay" v-if="showPostModal" @click="showPostModal = false">
      <view class="post-modal" @click.stop>
        <!-- 鎷栨嫿鏉?-->
        <view class="modal-drag-bar"></view>

        <!-- 澶撮儴娓愬彉鍖?-->
        <view class="modal-header">
          <view class="modal-header-left">
            <image :src="normalizeUserAvatar(currentPostAuthor.avatar)" mode="aspectFill" class="modal-user-avatar"></image>
            <view class="modal-header-text">
              <text class="modal-user-name dynamic-modal-user-name">{{ currentPostAuthor.name }}</text>
              <text class="modal-user-name">AI导学员</text>
              <text class="modal-header-hint">分享你的学习资源与收获</text>
            </view>
          </view>
          <view class="modal-close-btn" @click="showPostModal = false">
            <text class="modal-close-icon">×</text>
          </view>
        </view>

        <!-- 鍐呭鍖?-->
        <view class="modal-body">
          <!-- 鍒嗙被閫夋嫨 - 鍥炬爣鍗＄墖 -->
          <view class="cat-row">
            <view
              v-for="(tab, index) in tabs"
              :key="index"
              class="cat-card"
              :class="[getTabClass(tab.value), { 'cat-active': newPost.category === tab.value }]"
              @click="newPost.category = tab.value"
            >
              <text class="cat-emoji">{{ tab.emoji }}</text>
              <text class="cat-label">{{ tab.label }}</text>
            </view>
          </view>

          <!-- 姝ｆ枃杈撳叆 -->
          <view class="content-input-wrap">
            <textarea
              class="content-textarea"
              v-model="newPost.content"
              :placeholder="currentTabPlaceholder"
              maxlength="500"
              auto-height
            />
            <text class="content-count">{{ (newPost.content || '').length }}/500</text>
          </view>

          <!-- 纰宠冻杩逛笓灞炴暟鎹?-->
          <view class="carbon-input-row" v-if="newPost.category === '学习评估'">
            <view class="carbon-input-icon">📈</view>
            <input
              class="carbon-input"
              v-model="newPost.carbonSaved"
              placeholder="输入本次掌握度，例如 85"
              type="number"
            />
          </view>

          <!-- 宸ュ叿鏍?-->
          <view class="toolbar-row">
            <view class="toolbar-btn" @click="chooseImage">
              <view class="tb-icon-wrap" :class="newPost.image ? 'tb-active' : ''">
                <svg class="camera-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                  <rect x="8" y="20" width="48" height="32" rx="4"/>
                  <circle cx="32" cy="36" r="8"/>
                  <path d="M20 20l3-6h18l3 6"/>
                  <circle cx="50" cy="26" r="2" fill="currentColor"/>
                </svg>
              </view>
              <text class="tb-label">{{ newPost.image ? '已选图片' : '添加图片' }}</text>
            </view>
            <!-- 棰勮灏忓浘 -->
            <view class="preview-thumb" v-if="newPost.image">
              <image :src="newPost.image" mode="aspectFill" class="thumb-img"></image>
              <view class="thumb-del" @click.stop="newPost.image = ''">×</view>
            </view>
          </view>
        </view>

        <view class="modal-footer">
          <view class="cancel-text" @click="showPostModal = false">取消</view>
          <view class="submit-pill" @click="submitPost">
            <text class="submit-text">发布</text>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import request, { getAssetURL, uploadFile } from '../../utils/request.js'

const DEFAULT_POST_AUTHOR = {
  name: 'AI导学员',
  avatar: '../../static/avatar-1.png'
}

export default {
  data() {
    return {
      statusBarHeight: 0,
      brandTitle: '智学多智能体',
      brandSubtitle: '学生画像 · 资源生成 · 路径规划',
      todayBadgeText: '今日学习',
      userAvatar: '',
      currentPostAuthor: {
        name: DEFAULT_POST_AUTHOR.name,
        avatar: DEFAULT_POST_AUTHOR.avatar
      },
      eventHandlers: {
        authLogin: null,
        profileUpdated: null
      },
      feedRefreshTimer: null,
      carbonScore: 68,
      carbonProgress: 68,
      banners: [
        { image: '../../static/tweet-1.png', title: '人工智能导论课程知识库', sub: '课程资源输入', badge: '课程', url: '' },
        { image: '../../static/tweet-2.png', title: '对话式学生画像构建', sub: '随学随新', badge: '画像', url: '' },
        { image: '../../static/tweet-3.png', title: '多智能体协同生成学习资料', sub: '文档 · 题库 · 案例', badge: 'A3赛题', url: '' }
      ],
      functions: [
        {
          name: '实操案例',
          desc: '代码项目指导',
          icon: '🍳',
          image: '../../static/cooking-expert.png',
          bgClass: 'bg-cook',
          path: '/pages/cooking-expert/cooking-expert'
        },
        {
          name: '资源榜单',
          desc: '精选课程材料',
          icon: '🥗',
          image: '../../static/home-cuisine-ranking.png',
          bgClass: 'bg-recipe',
          path: '/pages/recipe-recommendation/recipe-recommendation'
        },
        {
          name: '学习路径',
          desc: '动态规划步骤',
          icon: '🍽️',
          image: '../../static/restaurant.png',
          bgClass: 'bg-rest',
          path: '/pages/restaurant-recommendation/restaurant-recommendation'
        },
        {
          name: '学生画像',
          desc: '掌握情况评估',
          icon: '💪',
          image: '../../static/health-management.png',
          bgClass: 'bg-health',
          path: '/pages/health-manager/health-manager'
        },
        {
          name: '资源生成',
          desc: '多模态资料生成',
          icon: '🥡',
          image: '../../static/takeaway-evaluation.png',
          bgClass: 'bg-takeaway',
          path: '/pages/takeaway-expert/takeaway-expert'
        },
        {
          name: 'MiniClaw',
          desc: '原系统助手',
          icon: '🤖',
          image: '../../static/openclaw.png',
          bgClass: 'bg-openclaw',
          path: '/pages/openclaw/openclaw'
        }
      ],
      tabs: [
        { label: '资源', value: '资源', emoji: '📚' },
        { label: '实操', value: '实操', emoji: '💻' },
        { label: '画像', value: '画像', emoji: '🧠' },
        { label: '学习评估', value: '学习评估', emoji: '📈' }
      ],
      currentTab: 0,
      posts: [],
      loading: false,
      hasMore: true,
      page: 1,
      showPostModal: false,
      newPost: {
        content: '',
        image: '',
        category: '资源',
        carbonSaved: ''
      }
    }
  },

  computed: {
    greetingText() {
      const hour = new Date().getHours()
      if (hour < 6) return '夜深了'
      if (hour < 12) return '早安'
      if (hour < 14) return '午安'
      if (hour < 18) return '下午好'
      return '晚上好'
    },
    filteredPosts() {
      const tabValue = this.tabs[this.currentTab].value
      return this.posts.filter(p => p.category === tabValue)
    },
    currentTabPlaceholder() {
      const placeholders = {
        '资源': '分享你生成的课程讲解、思维导图或阅读材料...',
        '实操': '分享你的代码案例、实践项目或调试过程...',
        '画像': '分享你的学习目标、知识短板或学习偏好...',
        '学习评估': '分享一次练习测试结果或学习反思...'
      }
      return placeholders[this.newPost.category] || '说点什么...'
    }
  },

  onLoad() {
    const systemInfo = uni.getSystemInfoSync()
    this.statusBarHeight = systemInfo.statusBarHeight || 0
    this.refreshCurrentPostAuthor()
    this.bindUserEvents()
    this.loadPosts()
    this.startFeedPolling()
  },

  onShow() {
    this.refreshCurrentPostAuthor()
    this.refreshLatestPosts()
    this.startFeedPolling()
  },

  onHide() {
    this.stopFeedPolling()
  },

  onUnload() {
    this.stopFeedPolling()
    this.unbindUserEvents()
  },

  methods: {
    bindUserEvents() {
      if (this.eventHandlers.authLogin && this.eventHandlers.profileUpdated) return

      this.eventHandlers.authLogin = () => {
        this.refreshCurrentPostAuthor()
      }
      this.eventHandlers.profileUpdated = (updatedUser) => {
        if (updatedUser && typeof updatedUser === 'object') {
          const localUser = uni.getStorageSync('user') || {}
          uni.setStorageSync('user', {
            ...localUser,
            ...updatedUser
          })
        }
        this.refreshCurrentPostAuthor()
      }

      uni.$on('auth:login-success', this.eventHandlers.authLogin)
      uni.$on('profile-updated', this.eventHandlers.profileUpdated)
    },

    unbindUserEvents() {
      if (this.eventHandlers.authLogin) {
        uni.$off('auth:login-success', this.eventHandlers.authLogin)
        this.eventHandlers.authLogin = null
      }

      if (this.eventHandlers.profileUpdated) {
        uni.$off('profile-updated', this.eventHandlers.profileUpdated)
        this.eventHandlers.profileUpdated = null
      }
    },

    normalizeUserAvatar(avatar) {
      if (!avatar) return DEFAULT_POST_AUTHOR.avatar

      const localPrefixes = ['../../', '../', '/static/', 'http://', 'https://', 'data:', 'blob:', 'file:']
      if (localPrefixes.some(prefix => avatar.startsWith(prefix))) {
        return avatar
      }

      return getAssetURL(avatar) || DEFAULT_POST_AUTHOR.avatar
    },

    refreshCurrentPostAuthor() {
      const user = uni.getStorageSync('user') || {}
      const profile = user.profile || {}
      const name = typeof user.name === 'string' ? user.name.trim() : ''
      const avatar = this.normalizeUserAvatar(user.avatar || user.avatar_url || profile.avatar || profile.avatar_url)

      this.currentPostAuthor = {
        id: user.id || user.user_id || profile.id,
        name: name || DEFAULT_POST_AUTHOR.name,
        avatar
      }
      this.userAvatar = avatar
    },

    onBannerClick(banner) {
      if (!banner.url) return
      uni.navigateTo({
        url: '/pages/webview/webview?url=' + encodeURIComponent(banner.url) + '&title=' + encodeURIComponent(banner.title)
      })
    },

    switchTab(index) {
      this.currentTab = index
      this.newPost.category = this.tabs[index].value
    },

    goToProfile() {
      uni.switchTab({ url: '/pages/personal-center/personal-center' })
    },

    goToNearbyCommunities() {
      uni.navigateTo({ url: '/pages/nearby-communities/nearby-communities' })
    },

    getCategoryClass(category) {
      const map = {
        '资源': 'chip-recommend',
        '实操': 'chip-cook',
        '画像': 'chip-health',
        '学习评估': 'chip-carbon'
      }
      return map[category] || ''
    },

    getTabClass(category) {
      const map = {
        '资源': 'theme-recommend',
        '实操': 'theme-cook',
        '画像': 'theme-health',
        '学习评估': 'theme-carbon'
      }
      return map[category] || ''
    },

    getTabInlineStyle(category, isActive) {
      return {}
    },

    navigateTo(path) {
      uni.switchTab({
        url: path,
        fail: () => uni.navigateTo({ url: path })
      })
    },

    getCurrentUserId() {
      const user = uni.getStorageSync('user') || {}
      return user.id || user.user_id || 1
    },

    normalizeHomePost(post) {
      const author = post.author || {}
      return {
        ...post,
        author: {
          id: author.id || post.user_id || post.author_id,
          name: author.name || post.author_name || DEFAULT_POST_AUTHOR.name,
          avatar: this.normalizeUserAvatar(author.avatar || post.author_avatar)
        },
        images: Array.isArray(post.images) ? post.images.map(image => this.normalizePostImage(image)) : [],
        likes: post.likes ?? post.like_count ?? 0,
        comments: post.comments ?? post.comment_count ?? 0,
        shares: post.shares ?? post.share_count ?? 0,
        isLiked: post.isLiked ?? post.is_liked ?? false,
        createdAt: post.createdAt || post.created_at || new Date().toISOString()
      }
    },

    normalizePostImage(image) {
      if (!image) return ''
      if (image.startsWith('http://') || image.startsWith('https://')) return image
      if (image.startsWith('../../') || image.startsWith('/static/') || image.startsWith('data:') || image.startsWith('blob:') || image.startsWith('file:')) return image
      return getAssetURL(image) || image
    },

    startFeedPolling() {
      if (this.feedRefreshTimer) return
      this.feedRefreshTimer = setInterval(() => {
        this.refreshLatestPosts()
      }, 5000)
    },

    stopFeedPolling() {
      if (!this.feedRefreshTimer) return
      clearInterval(this.feedRefreshTimer)
      this.feedRefreshTimer = null
    },

    async refreshLatestPosts() {
      if (this.loading) return
      try {
        const response = await request.get('/api/community/posts/feed', {
          data: {
            user_id: this.getCurrentUserId(),
            page: 1,
            page_size: Math.max(10, this.posts.length || 10)
          }
        })

        if (response.code === 200) {
          this.posts = (response.data.posts || []).map(post => this.normalizeHomePost(post))
          this.hasMore = 1 < response.data.total_pages
          this.page = 2
        }
      } catch (_error) {
        // Silent refresh should not interrupt reading.
      }
    },
    async loadPosts() {
      if (this.loading || !this.hasMore) return
      this.loading = true
      try {
        const response = await request.get('/api/community/posts/feed', {
          data: {
            user_id: this.getCurrentUserId(),
            page: this.page,
            page_size: 10
          }
        })

        if (response.code === 200) {
          const newPosts = (response.data.posts || []).map(post => this.normalizeHomePost(post))
          this.posts = this.page === 1 ? newPosts : [...this.posts, ...newPosts]
          this.hasMore = this.page < response.data.total_pages
          this.page++
        }
      } catch (_error) {
        uni.showToast({ title: '加载失败，请重试', icon: 'none' })
      } finally {
        this.loading = false
      }
    },

    loadMorePosts() {
      this.loadPosts()
    },

    generateMockPosts() {
      const now = Date.now()
      const allMock = [
        {
          id: now + 1,
          author: { name: 'AI导学员', avatar: '../../static/avatar-1.png' },
          category: '资源',
          content: '已生成《人工智能导论》搜索算法章节讲解文档，包含概念拆解、伪代码和典型例题。',
          images: ['../../static/food.png'],
          likes: 102,
          comments: 24,
          shares: 15,
          isLiked: false,
          createdAt: new Date(now - 2 * 3600000).toISOString()
        },
        {
          id: now + 2,
          author: { name: '实践项目助手', avatar: '../../static/avatar-1.png' },
          category: '实操',
          content: '今天完成了 A* 搜索路径规划实操案例，已整理输入数据、核心代码和测试步骤。',
          images: ['../../static/cookexpret.png'],
          likes: 178,
          comments: 56,
          shares: 34,
          isLiked: true,
          createdAt: new Date(now - 5 * 3600000).toISOString()
        },
        {
          id: now + 3,
          author: { name: '画像构建智能体', avatar: '../../static/avatar-2.png' },
          category: '画像',
          content: '学生画像更新：基础较好、偏好案例式学习、易错点集中在启发式函数设计。',
          images: [],
          likes: 256,
          comments: 78,
          shares: 91,
          isLiked: false,
          createdAt: new Date(now - 8 * 3600000).toISOString()
        },
        {
          id: now + 4,
          author: { name: '效果评估智能体', avatar: '../../static/avatar-3.png' },
          category: '学习评估',
          content: '本次搜索算法练习掌握度 86 分，建议补充图搜索与树搜索差异的针对性练习。',
          images: [],
          likes: 134,
          comments: 42,
          shares: 28,
          isLiked: false,
          carbonSaved: 86,
          carbonPoints: 12,
          createdAt: new Date(now - 1 * 3600000).toISOString()
        }
      ]

      return allMock.map(post => ({
        ...post,
        author: {
          ...(post.author || {}),
          avatar: this.normalizeUserAvatar(post.author && post.author.avatar)
        }
      }))
    },

    async likePost(post) {
      const previousLiked = post.isLiked
      const previousLikes = post.likes

      post.isLiked = !post.isLiked
      post.likes += post.isLiked ? 1 : -1

      try {
        const response = await request.post(`/api/community/posts/${post.id}/like`, {
          user_id: this.getCurrentUserId()
        })

        if (response.code === 200) {
          post.isLiked = response.data.is_liked
          post.likes = Math.max(0, previousLikes + (post.isLiked === previousLiked ? 0 : (post.isLiked ? 1 : -1)))
        }
      } catch (_error) {
        post.isLiked = previousLiked
        post.likes = previousLikes
        uni.showToast({ title: '操作失败，请重试', icon: 'none' })
      }
    },

    canDeletePost(post) {
      const currentUserId = Number(this.getCurrentUserId())
      const authorId = Number(post.author && post.author.id)
      return Boolean(currentUserId && authorId && currentUserId === authorId)
    },

    async deletePost(post) {
      const confirmed = await new Promise(resolve => {
        uni.showModal({
          title: '删除帖子',
          content: '确定删除这条帖子吗？',
          confirmText: '删除',
          confirmColor: '#ef4444',
          success: res => resolve(res.confirm),
          fail: () => resolve(false)
        })
      })

      if (!confirmed) return

      try {
        const response = await request.delete(`/api/community/posts/${post.id}`, {
          data: {
            user_id: this.getCurrentUserId()
          }
        })

        if (response.code !== 200) {
          throw new Error(response.message || 'delete failed')
        }

        this.posts = this.posts.filter(item => item.id !== post.id)
        uni.showToast({ title: '删除成功', icon: 'none' })
      } catch (error) {
        const message = error?.data?.message || error?.message || '删除失败，请重试'
        uni.showToast({ title: message, icon: 'none' })
      }
    },

    commentPost() {
      uni.showToast({ title: '评论功能开发中', icon: 'none' })
    },

    sharePost() {
      uni.showToast({ title: '分享功能开发中', icon: 'none' })
    },

    chooseImage() {
      uni.chooseImage({
        count: 1,
        sizeType: ['compressed'],
        sourceType: ['album', 'camera'],
        success: (res) => {
          this.newPost.image = res.tempFilePaths[0]
        }
      })
    },

    async uploadPostImage(filePath) {
      const uploadPaths = [
        '/api/community/upload-image',
        '/api/community/posts/upload-image'
      ]

      let lastError = null
      for (const path of uploadPaths) {
        try {
          const uploadRes = await uploadFile(path, filePath, 'image', {
            formData: {
              user_id: this.getCurrentUserId()
            }
          })
          if (uploadRes?.code === 200 && uploadRes?.data?.url) {
            return uploadRes.data.url
          }
          lastError = uploadRes
        } catch (error) {
          lastError = error
          if (error?.statusCode && error.statusCode !== 404) {
            break
          }
        }
      }

      throw lastError || new Error('upload failed')
    },

    async submitPost() {
      if (!this.newPost.content.trim()) {
        uni.showToast({ title: '请输入内容', icon: 'none' })
        return
      }

      let images = []
      if (this.newPost.image) {
        try {
          uni.showLoading({ title: '图片上传中', mask: true })
          images = [await this.uploadPostImage(this.newPost.image)]
        } catch (_error) {
          uni.showToast({ title: '图片未上传，已发布文字', icon: 'none' })
        } finally {
          uni.hideLoading()
        }
      }

      try {
        const response = await request.post('/api/community/posts/feed', {
          user_id: this.getCurrentUserId(),
          content: this.newPost.content,
          images,
          category: this.newPost.category,
          tags: this.newPost.carbonSaved ? [`carbon:${this.newPost.carbonSaved}`] : []
        })

        if (response.code !== 200) {
          throw new Error('publish failed')
        }

        if (this.newPost.category === '学习评估' && this.newPost.carbonSaved) {
          const carbonPoints = Math.ceil(parseInt(this.newPost.carbonSaved) / 10)
          this.carbonScore = Math.min(100, this.carbonScore + carbonPoints)
          this.carbonProgress = this.carbonScore
        }

        this.showPostModal = false
        this.newPost = {
          content: '',
          image: '',
          category: this.tabs[this.currentTab].value,
          carbonSaved: ''
        }
        this.page = 1
        this.hasMore = true
        await this.refreshLatestPosts()

        uni.showToast({ title: '发布成功', icon: 'none' })
      } catch (error) {
        const message = error?.data?.message || error?.message || '发布失败，请重试'
        uni.showToast({ title: message, icon: 'none' })
      }
    },
    formatTime(timestamp) {
      const now = new Date()
      const time = new Date(timestamp)
      const diff = now - time
      const minute = 60 * 1000
      const hour = 60 * minute
      const day = 24 * hour
      if (diff < minute) return '刚刚'
      if (diff < hour) return Math.floor(diff / minute) + '分钟前'
      if (diff < day) return Math.floor(diff / hour) + '小时前'
      if (diff < day * 7) return Math.floor(diff / day) + '天前'
      return time.toLocaleDateString('zh-CN')
    }
  }
}
</script>

<style scoped>
/* ===== 棣栭〉瀵艰埅鏍?===== */
.home-navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  background: linear-gradient(180deg, rgba(247, 249, 252, 0.98) 0%, rgba(255, 255, 255, 0.94) 100%);
  z-index: 500;
  backdrop-filter: blur(18rpx);
  -webkit-backdrop-filter: blur(18rpx);
  border-bottom: 1rpx solid rgba(148, 163, 184, 0.16);
  box-shadow: 0 14rpx 38rpx rgba(15, 23, 42, 0.06);
}

.home-navbar-content {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 44px;
  padding: 0 28rpx;
  gap: 20rpx;
}

.home-brand-block {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.home-brand-icon {
  width: 64rpx;
  height: 64rpx;
}

.home-brand-name {
  font-size: 38rpx;
  font-weight: 800;
  color: #0f172a;
  letter-spacing: 0;
  line-height: 1.15;
  white-space: nowrap;
}



/* ===== 鍏ㄥ眬瀹瑰櫒 ===== */
.home-container {
  min-height: 100vh;
  background: #f0fdf4 !important;
  display: block;
  padding: 0 32rpx 200rpx 32rpx;
  padding-bottom: calc(200rpx + constant(safe-area-inset-bottom));
  padding-bottom: calc(200rpx + env(safe-area-inset-bottom));
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  animation: fadeIn 0.6s ease-out;
  box-sizing: border-box;
}

.home-content {
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20rpx);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* ===== 杞挱鍥惧姩鐢?==== */
.banner-section {
  animation: slideInUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) 0.1s both;
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(40rpx);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* ===== 鍔熻兘鍏ュ彛鍔ㄧ敾 ===== */
.functions-section {
  animation: slideInUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) 0.2s both;
}

.feature-card {
  animation: scaleIn 0.5s cubic-bezier(0.34, 1.56, 0.64, 1) both;
}

.feature-card:nth-child(1) { animation-delay: 0.3s; }
.feature-card:nth-child(2) { animation-delay: 0.35s; }
.feature-card:nth-child(3) { animation-delay: 0.4s; }
.feature-card:nth-child(4) { animation-delay: 0.45s; }
.feature-card:nth-child(5) { animation-delay: 0.5s; }

@keyframes scaleIn {
  from {
    opacity: 0;
    transform: scale(0.8);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.bottom-section {
  animation: slideInUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) 0.3s both;
}

.post-card {
  animation: fadeIn 0.5s ease-out both;
}

.post-card:nth-child(1) { animation-delay: 0.4s; }
.post-card:nth-child(2) { animation-delay: 0.45s; }
.post-card:nth-child(3) { animation-delay: 0.5s; }
.post-card:nth-child(4) { animation-delay: 0.55s; }
.post-card:nth-child(5) { animation-delay: 0.6s; }

/* ===== 椤堕儴闂€欏尯 ===== */
.header-section {
  position: relative;
  padding: 50rpx 30rpx 24rpx;
  background: linear-gradient(135deg, #1a7c54 0%, #2ea96f 50%, #4CCF87 100%);
  border-radius: 0 0 40rpx 40rpx;
  box-shadow: 0 8rpx 32rpx rgba(46, 169, 111, 0.25);
  margin-bottom: 20rpx;
}

.header-bg-gradient {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: radial-gradient(circle at 80% 20%, rgba(255,255,255,0.12) 0%, transparent 60%);
  border-radius: 0 0 40rpx 40rpx;
  pointer-events: none;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: relative;
  z-index: 1;
}

.greeting-box {
  flex: 1;
}

.greeting-text {
  font-size: 38rpx;
  font-weight: 800;
  color: #fff;
  display: block;
  margin-bottom: 8rpx;
  text-shadow: 0 2rpx 8rpx rgba(0,0,0,0.15);
}

.slogan-text {
  font-size: 22rpx;
  color: rgba(255,255,255,0.85);
  display: block;
}

.user-avatar {
  position: relative;
  width: 88rpx;
  height: 88rpx;
}

.avatar-ring {
  position: absolute;
  top: -4rpx; left: -4rpx; right: -4rpx; bottom: -4rpx;
  border: 3rpx solid rgba(255,255,255,0.6);
  border-radius: 50%;
}

.avatar-img {
  width: 88rpx;
  height: 88rpx;
  border-radius: 50%;
  border: 3rpx solid rgba(255,255,255,0.9);
}

/* 纰崇Н鍒嗘潯 */
.carbon-strip {
  display: flex;
  align-items: center;
  gap: 12rpx;
  margin-top: 24rpx;
  background: rgba(255,255,255,0.18);
  border-radius: 30rpx;
  padding: 14rpx 20rpx;
  position: relative;
  z-index: 1;
}

.carbon-icon {
  font-size: 28rpx;
}

.carbon-label {
  font-size: 22rpx;
  color: rgba(255,255,255,0.9);
  white-space: nowrap;
}

.carbon-bar {
  flex: 1;
  height: 10rpx;
  background: rgba(255,255,255,0.3);
  border-radius: 10rpx;
  overflow: hidden;
}

.carbon-fill {
  height: 100%;
  background: linear-gradient(90deg, #a8edca, #fff);
  border-radius: 10rpx;
  transition: width 0.8s ease;
}

.carbon-value {
  font-size: 22rpx;
  color: #fff;
  font-weight: bold;
  white-space: nowrap;
}

/* ===== 杞挱鍥?===== */
.banner-section {
  margin: 180rpx 0 32rpx;
  border-radius: 0;
  overflow: hidden;
  box-shadow: 0 16rpx 40rpx rgba(148, 163, 184, 0.1);
}

.banner-swiper {
  height: 380rpx;
  border-radius: 0;
}

.banner-item {
  width: 100%;
  height: 100%;
  position: relative;
  border-radius: 0;
  overflow: hidden;
}

.banner-img {
  width: 100%;
  height: 100%;
  border-radius: 0;
}

.banner-overlay {
  position: absolute;
  bottom: 0; left: 0; right: 0;
  padding: 80rpx 40rpx 32rpx;
  background: linear-gradient(to top, rgba(0,0,0,0.7) 0%, transparent 100%);
  display: flex;
  flex-direction: column;
  gap: 8rpx;
  border-radius: 0;
}

.banner-title {
  color: #fff;
  font-size: 38rpx;
  font-weight: 800;
  text-shadow: 0 2rpx 8rpx rgba(0,0,0,0.2);
}

.banner-sub {
  color: rgba(255,255,255,0.9);
  font-size: 24rpx;
  font-weight: 500;
}

/* ===== 鍔熻兘鍏ュ彛 ===== */
.functions-section {
  margin: 0 0 32rpx;
  background: white;
  border-radius: 40rpx;
  padding: 32rpx;
  box-shadow: 0 8rpx 32rpx rgba(148, 163, 184, 0.08);
  border: 1rpx solid rgba(226, 232, 240, 0.6);
}

.section-title {
  font-size: 32rpx;
  font-weight: 700;
  color: #0f172a;
  display: block;
  margin-bottom: 24rpx;
  letter-spacing: -0.5rpx;
}

.function-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20rpx;
}

@media screen and (min-width: 768px) {
  .function-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

.feature-card {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  padding: 32rpx 28rpx;
  border-radius: 32rpx;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  min-height: 200rpx;
  background: white;
  box-shadow: 0 2rpx 8rpx rgba(148, 163, 184, 0.06);
  position: relative;
  overflow: hidden;
  cursor: pointer;
}

.feature-card::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(248, 250, 252, 0.5) 0%, rgba(255, 255, 255, 0) 100%);
  opacity: 0;
  transition: opacity 0.3s ease;
  pointer-events: none;
}

.feature-card:hover {
  transform: translateY(-6rpx);
  box-shadow: 0 12rpx 32rpx rgba(148, 163, 184, 0.12);
  border-color: rgba(16, 185, 129, 0.3);
}

.feature-card:hover::after {
  opacity: 1;
}

.feature-card:active {
  transform: translateY(-2rpx) scale(0.98);
  box-shadow: 0 4rpx 16rpx rgba(148, 163, 184, 0.08);
}

.bg-cook     { background: white; border-color: rgba(251, 146, 60, 0.2); }
.bg-cook:hover { border-color: rgba(251, 146, 60, 0.4); }
.bg-cook .feature-icon-wrap { background: rgba(251, 146, 60, 0.08); }
.bg-cook:hover .feature-icon-wrap { background: rgba(251, 146, 60, 0.15); }

.bg-recipe   { background: white; border-color: rgba(234, 179, 8, 0.2); }
.bg-recipe:hover { border-color: rgba(234, 179, 8, 0.4); }
.bg-recipe .feature-icon-wrap { background: rgba(234, 179, 8, 0.08); }
.bg-recipe:hover .feature-icon-wrap { background: rgba(234, 179, 8, 0.15); }

.bg-rest     { background: white; border-color: rgba(34, 197, 94, 0.2); }
.bg-rest:hover { border-color: rgba(34, 197, 94, 0.4); }
.bg-rest .feature-icon-wrap { background: rgba(34, 197, 94, 0.08); }
.bg-rest:hover .feature-icon-wrap { background: rgba(34, 197, 94, 0.15); }

.bg-health   { background: white; border-color: rgba(59, 130, 246, 0.2); }
.bg-health:hover { border-color: rgba(59, 130, 246, 0.4); }
.bg-health .feature-icon-wrap { background: rgba(59, 130, 246, 0.08); }
.bg-health:hover .feature-icon-wrap { background: rgba(59, 130, 246, 0.15); }

.bg-takeaway { background: white; border-color: rgba(239, 68, 68, 0.2); }
.bg-takeaway:hover { border-color: rgba(239, 68, 68, 0.4); }
.bg-takeaway .feature-icon-wrap { background: rgba(239, 68, 68, 0.08); }
.bg-takeaway:hover .feature-icon-wrap { background: rgba(239, 68, 68, 0.15); }

.bg-openclaw { background: white; border-color: rgba(14, 165, 233, 0.2); }
.bg-openclaw:hover { border-color: rgba(14, 165, 233, 0.4); }
.bg-openclaw .feature-icon-wrap { background: rgba(14, 165, 233, 0.08); }
.bg-openclaw:hover .feature-icon-wrap { background: rgba(14, 165, 233, 0.15); }

.feature-icon-wrap {
  width: 96rpx;
  height: 96rpx;
  background: rgba(248, 250, 252, 0.8);
  border-radius: 28rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 24rpx;
  box-shadow: 0 2rpx 8rpx rgba(148, 163, 184, 0.08);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.feature-card:hover .feature-icon-wrap {
  transform: scale(1.08) rotate(5deg);
  box-shadow: 0 4rpx 16rpx rgba(148, 163, 184, 0.12);
}

.feature-icon {
  font-size: 52rpx;
  filter: drop-shadow(0 2rpx 4rpx rgba(0, 0, 0, 0.1));
}

.feature-icon-img {
  width: 68rpx;
  height: 68rpx;
  border-radius: 14rpx;
}

.feature-name {
  font-size: 32rpx;
  font-weight: 700;
  color: #1e293b;
  display: block;
  margin-bottom: 12rpx;
  letter-spacing: -0.5rpx;
  line-height: 1.3;
}

.feature-desc {
  font-size: 24rpx;
  color: #64748b;
  display: block;
  line-height: 1.6;
  font-weight: 500;
  letter-spacing: 0.2rpx;
}

.bottom-section {
  flex: 1;
  margin: 0 0 0;
  background: white;
  border-radius: 40rpx;
  padding: 32rpx;
  box-shadow: 0 16rpx 40rpx rgba(148, 163, 184, 0.1);
}

.community-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
}

.community-title {
  font-size: 32rpx;
  font-weight: 700;
  color: #0f172a;
}

.nearby-btn {
  display: flex;
  align-items: center;
  gap: 8rpx;
  background: #ffffff;
  padding: 12rpx 24rpx;
  border-radius: 24rpx;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.08);
  transition: all 0.3s;
  border: 1rpx solid rgba(0, 0, 0, 0.06);
}

.nearby-btn:active {
  transform: scale(0.95);
}

.nearby-icon {
  font-size: 28rpx;
}

.nearby-text {
  font-size: 24rpx;
  color: #374151;
  font-weight: 600;
}

.post-btn {
  background: linear-gradient(135deg, #10b981 0%, #0ea5e9 100%);
  color: white;
  padding: 16rpx 32rpx;
  border-radius: 30rpx;
  font-size: 26rpx;
  font-weight: 600;
  border: none;
  letter-spacing: 0.5rpx;
  box-shadow: 0 4rpx 12rpx rgba(16, 185, 129, 0.3);
  transition: all 0.3s ease;
  cursor: pointer;
}

.post-btn:hover {
  transform: translateY(-2rpx);
  box-shadow: 0 6rpx 16rpx rgba(16, 185, 129, 0.4);
}

.post-btn:active { 
  transform: scale(0.96);
  box-shadow: 0 2rpx 8rpx rgba(16, 185, 129, 0.3);
}

/* Tab 选项卡 */
.tabs-section {
  display: flex;
  gap: 16rpx;
  margin-bottom: 28rpx;
  padding: 0;
}

.tab-item {
  flex: 1;
  text-align: center;
  padding: 16rpx 12rpx;
  border-radius: 20rpx;
  background: #f8fafc;
  border: 2rpx solid #e2e8f0;
  transition: all 0.2s ease;
}

.tab-item.active {
  background: #10b981;
  border-color: #10b981;
}

.tab-text {
  font-size: 26rpx;
  color: #64748b;
  font-weight: 500;
}

.tab-item.active .tab-text {
  color: #ffffff;
  font-weight: 600;
}

.tab-dot {
  width: 8rpx;
  height: 8rpx;
  background: #10b981;
  border-radius: 50%;
  margin: 6rpx auto 0;
  box-shadow: 0 0 0 4rpx rgba(16, 185, 129, 0.2);
}

/* ===== 甯栧瓙鍒楄〃 ===== */
.posts-scroll {
  /* 绉婚櫎鍥哄畾楂樺害闄愬埗锛岃 scroll-view 鎴栬€呭鍣ㄨ窡闅忓唴瀹硅嚜鐒剁敓闀?*/
  /* 鎴栬€呭鏋滈渶瑕佸眬閮ㄦ粴鍔紝纭繚璁＄畻楂樺害姝ｇ‘銆傝繖閲屾敼涓哄唴瀹硅嚜閫傚簲浠ユ仮澶嶉〉闈笅婊戞劅 */
  min-height: 200rpx;
}

.posts-list {
  display: flex;
  flex-direction: column;
  gap: 24rpx;
  padding-bottom: 40rpx;
}

.post-card {
  background: #fafafa;
  border-radius: 32rpx;
  padding: 28rpx;
  position: relative;
  transition: all 0.3s ease;
  box-shadow: 0 4rpx 12rpx rgba(0,0,0,0.04);
  cursor: pointer;
}

.post-card:hover {
  transform: translateY(-2rpx);
  box-shadow: 0 8rpx 24rpx rgba(16, 185, 129, 0.12);
  border-color: #d1fae5;
}

.post-card:active {
  transform: scale(0.98);
}

.post-card:active {
  transform: scale(0.98);
}

/* 绉婚櫎 .carbon-card 鍙婂叾鐗规畩鏍峰紡浠ヤ繚鎸佷竴鑷存€?*/

.post-author {
  display: flex;
  align-items: center;
  gap: 16rpx;
  margin-bottom: 16rpx;
}

.author-avatar {
  width: 72rpx;
  height: 72rpx;
  border-radius: 50%;
  box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.06);
}

.author-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6rpx;
}

.author-name {
  font-size: 28rpx;
  font-weight: 700;
  color: #0f172a;
}

.post-time {
  font-size: 22rpx;
  color: #94a3b8;
  font-weight: 500;
}

/* 鍒嗙被 chip */
.category-chip {
  font-size: 22rpx;
  padding: 6rpx 16rpx;
  border-radius: 24rpx;
  font-weight: 700;
}
.chip-recommend { background: #fff7ed; color: #ea580c; }
.chip-cook      { background: #fff7ed; color: #c2410c; }
.chip-health    { background: #f0fdf4; color: #15803d; }
.chip-carbon    { background: #f0fdf4; color: #166534; }

.post-content {
  margin-bottom: 16rpx;
}

.post-text {
  font-size: 28rpx;
  color: #334155;
  line-height: 1.7;
  display: block;
  margin-bottom: 16rpx;
  font-weight: 500;
}

.post-image {
  width: 100%;
  height: 300rpx;
  border-radius: 20rpx;
  object-fit: cover;
  box-shadow: 0 4rpx 12rpx rgba(0,0,0,0.08);
}

/* 纰冲噺鎺掓暟鎹?*/
.carbon-stats {
  display: flex;
  gap: 24rpx;
  background: rgba(16, 185, 129, 0.1);
  border-radius: 20rpx;
  padding: 16rpx 20rpx;
  margin-bottom: 16rpx;
  border: 1.5rpx solid rgba(16, 185, 129, 0.2);
}

.carbon-stat-item {
  font-size: 24rpx;
  color: #166534;
  font-weight: 700;
}

.post-actions {
  display: flex;
  gap: 32rpx;
  padding-top: 16rpx;
  border-top: 2rpx solid #f1f5f9;
}

.action-item {
  display: flex;
  align-items: center;
  gap: 10rpx;
  padding: 10rpx 16rpx;
  border-radius: 20rpx;
  transition: all 0.2s;
  cursor: pointer;
}

.action-item:hover {
  background: #f1f5f9;
  transform: scale(1.05);
}

.action-item:active { 
  background: #e2e8f0;
  transform: scale(0.95);
}

.action-icon { font-size: 32rpx; }
.action-count { font-size: 24rpx; color: #64748b; font-weight: 600; }
.delete-action {
  margin-left: auto;
}
.delete-text {
  font-size: 24rpx;
  color: #ef4444;
  font-weight: 700;
}

/* 鍔犺浇涓?*/
.loading-more, .no-more {
  text-align: center;
  padding: 32rpx 0;
}

.loading-text, .no-more-text {
  font-size: 24rpx;
  color: #94a3b8;
  font-weight: 500;
}

/* 绌虹姸鎬?*/
.empty-state {
  text-align: center;
  padding: 100rpx 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 24rpx;
}

.empty-icon { font-size: 100rpx; }
.empty-text { font-size: 28rpx; color: #94a3b8; font-weight: 500; }

.empty-action {
  background: linear-gradient(135deg, #10b981, #0ea5e9);
  color: white;
  padding: 20rpx 48rpx;
  border-radius: 40rpx;
  font-size: 28rpx;
  font-weight: 700;
  border: none;
  box-shadow: 0 8rpx 24rpx rgba(16, 185, 129, 0.3);
  transition: all 0.3s;
}

.empty-action:active {
  transform: scale(0.96);
}

.fab-post-btn {
  position: fixed;
  right: 40rpx;
  bottom: 160rpx; /* 閬垮紑搴曢儴 TabBar */
  width: 120rpx;
  height: 120rpx;
  background: #ffffff;
  border-radius: 60rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  box-shadow: 0 12rpx 32rpx rgba(0, 0, 0, 0.12);
  z-index: 998;
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  border: 4rpx solid rgba(0, 0, 0, 0.06);
}

.fab-post-btn:active {
  transform: scale(0.9) translateY(4rpx);
  box-shadow: 0 4rpx 12rpx rgba(16, 185, 129, 0.3);
}

.fab-icon {
  font-size: 40rpx;
  margin-bottom: 2rpx;
}

.fab-text {
  font-size: 20rpx;
  color: #374151;
  font-weight: 800;
  letter-spacing: 2rpx;
}

.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(15, 23, 42, 0.5);
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  justify-content: flex-end;
  z-index: 2000;
  padding-right: 0;
}

.post-modal {
  width: 85%;
  max-width: 640rpx;
  height: 100vh;
  max-height: 100vh;
  background: linear-gradient(180deg, #f0f9ff 0%, #ffffff 100%);
  border-radius: 48rpx 0 0 48rpx;
  display: flex;
  flex-direction: column;
  box-shadow: -16rpx 0 40rpx rgba(14, 165, 233, 0.2);
  animation: slideInRight 0.4s cubic-bezier(0.16, 1, 0.3, 1);
  border-left: 3rpx solid rgba(14, 165, 233, 0.3);
  overflow: hidden;
}

@keyframes slideInRight {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

/* 鎷栨嫿鏉?*/
.modal-drag-bar {
  width: 60rpx;
  height: 6rpx;
  background: linear-gradient(90deg, #0ea5e9, #38bdf8);
  border-radius: 6rpx;
  margin: 24rpx auto 12rpx;
  flex-shrink: 0;
  box-shadow: 0 2rpx 8rpx rgba(14, 165, 233, 0.3);
}

/* 澶撮儴 */
.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24rpx 32rpx 24rpx;
  border-bottom: 2rpx solid rgba(14, 165, 233, 0.15);
  flex-shrink: 0;
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
}

.modal-header-left {
  display: flex;
  align-items: center;
  gap: 20rpx;
}

.modal-user-avatar {
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
  border: 4rpx solid #0ea5e9;
  box-shadow: 0 4rpx 16rpx rgba(14, 165, 233, 0.3);
}

.modal-header-text {
  display: flex;
  flex-direction: column;
  gap: 6rpx;
}

.modal-header-text .modal-user-name:not(.dynamic-modal-user-name) {
  display: none;
}

.modal-user-name {
  font-size: 30rpx;
  font-weight: 800;
  color: #0c4a6e;
}

.modal-header-hint {
  font-size: 22rpx;
  color: #0ea5e9;
  font-weight: 600;
}

.modal-close-btn {
  width: 64rpx;
  height: 64rpx;
  background: linear-gradient(135deg, #0ea5e9, #38bdf8);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
  box-shadow: 0 4rpx 12rpx rgba(14, 165, 233, 0.3);
}

.modal-close-btn:active {
  transform: scale(0.9);
  background: linear-gradient(135deg, #0284c7, #0ea5e9);
}

.modal-close-icon {
  font-size: 28rpx;
  color: #ffffff;
}

/* 鍐呭鍖?*/
.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 28rpx 32rpx;
  display: flex;
  flex-direction: column;
  gap: 24rpx;
}

/* 鍒嗙被鍗＄墖 */
.cat-row {
  display: flex;
  gap: 20rpx;
}

.cat-card {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10rpx;
  padding: 20rpx 12rpx;
  border-radius: 24rpx;
  background: #f8fafc;
  border: 2rpx solid #e0f2fe;
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  cursor: pointer;
}

.cat-card.theme-recommend {
  background: linear-gradient(180deg, rgba(255, 247, 237, 0.96) 0%, rgba(255, 237, 213, 0.92) 100%);
  border-color: rgba(249, 115, 22, 0.20);
}

.cat-card.theme-cook {
  background: linear-gradient(180deg, rgba(254, 252, 232, 0.96) 0%, rgba(254, 249, 195, 0.92) 100%);
  border-color: rgba(234, 179, 8, 0.20);
}

.cat-card.theme-health {
  background: linear-gradient(180deg, rgba(240, 253, 244, 0.96) 0%, rgba(220, 252, 231, 0.92) 100%);
  border-color: rgba(34, 197, 94, 0.18);
}

.cat-card.theme-carbon {
  background: linear-gradient(180deg, rgba(236, 253, 245, 0.96) 0%, rgba(209, 250, 229, 0.92) 100%);
  border-color: rgba(16, 185, 129, 0.18);
}

.cat-card:hover {
  transform: translateY(-2rpx);
  box-shadow: 0 4rpx 12rpx rgba(14, 165, 233, 0.15);
  border-color: #0ea5e9;
}

.cat-card:active {
  transform: scale(0.96);
}

.cat-active {
  background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%);
  border-color: #0ea5e9;
  box-shadow: 0 4rpx 16rpx rgba(14, 165, 233, 0.25);
}

.cat-emoji { font-size: 36rpx; }

.cat-label {
  font-size: 22rpx;
  color: #64748b;
  font-weight: 600;
}

.cat-card.theme-recommend .cat-label { color: #c2410c; }
.cat-card.theme-cook .cat-label { color: #a16207; }
.cat-card.theme-health .cat-label { color: #15803d; }
.cat-card.theme-carbon .cat-label { color: #047857; }

.cat-active .cat-label {
  color: #0369a1;
  font-weight: 800;
}

/* 姝ｆ枃杈撳叆 */
.content-input-wrap {
  position: relative;
  background: #ffffff;
  border-radius: 24rpx;
  padding: 24rpx;
  border: 2rpx solid #e0f2fe;
  transition: all 0.3s;
  box-shadow: 0 2rpx 8rpx rgba(14, 165, 233, 0.05);
}

.content-input-wrap:focus-within {
  border-color: #0ea5e9;
  background: #f0f9ff;
  box-shadow: 0 0 0 4rpx rgba(14, 165, 233, 0.15);
}

.content-textarea {
  width: 100%;
  font-size: 28rpx;
  color: #0c4a6e;
  min-height: 180rpx;
  line-height: 1.7;
  box-sizing: border-box;
  background: transparent;
  font-weight: 500;
}

.content-count {
  display: block;
  text-align: right;
  font-size: 22rpx;
  color: #0ea5e9;
  margin-top: 12rpx;
  font-weight: 600;
}

/* 纰宠冻杩硅緭鍏?*/
.carbon-input-row {
  display: flex;
  align-items: center;
  gap: 16rpx;
  background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%);
  border-radius: 20rpx;
  padding: 20rpx 24rpx;
  border: 2rpx solid #0ea5e9;
  box-shadow: 0 4rpx 12rpx rgba(14, 165, 233, 0.15);
}

.carbon-input-icon { font-size: 32rpx; }

.carbon-input {
  flex: 1;
  font-size: 28rpx;
  color: #0369a1;
  font-weight: 600;
}

/* 宸ュ叿鏍?*/
.toolbar-row {
  display: flex;
  align-items: center;
  gap: 24rpx;
}

.toolbar-btn {
  display: flex;
  align-items: center;
  gap: 12rpx;
}

.tb-icon-wrap {
  width: 72rpx;
  height: 72rpx;
  background: #e0f2fe;
  border-radius: 20rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
  border: 2rpx solid #bae6fd;
}

.tb-icon-wrap:active {
  transform: scale(0.9);
}

.tb-active { 
  background: linear-gradient(135deg, #0ea5e9, #38bdf8);
  border-color: #0ea5e9;
  box-shadow: 0 4rpx 16rpx rgba(14, 165, 233, 0.3);
}


.tb-icon { font-size: 32rpx; }

.tb-label {
  font-size: 24rpx;
  color: #64748b;
  font-weight: 600;
}

.preview-thumb {
  position: relative;
  width: 88rpx;
  height: 88rpx;
  border-radius: 16rpx;
  overflow: visible;
  margin-left: 12rpx;
}

.thumb-img {
  width: 88rpx;
  height: 88rpx;
  border-radius: 16rpx;
  box-shadow: 0 4rpx 12rpx rgba(14, 165, 233, 0.2);
  border: 2rpx solid #e0f2fe;
}

.thumb-del {
  position: absolute;
  top: -12rpx;
  right: -12rpx;
  width: 36rpx;
  height: 36rpx;
  background: linear-gradient(135deg, #ef4444, #dc2626);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24rpx;
  color: #fff;
  line-height: 1;
  box-shadow: 0 4rpx 12rpx rgba(239, 68, 68, 0.4);
}

.modal-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20rpx 32rpx 48rpx;
  border-top: 2rpx solid rgba(14, 165, 233, 0.15);
  flex-shrink: 0;
  background: linear-gradient(180deg, #ffffff 0%, #f0f9ff 100%);
}

.cancel-text {
  font-size: 28rpx;
  color: #64748b;
  padding: 16rpx 24rpx;
  font-weight: 600;
  transition: color 0.2s;
}

.cancel-text:active {
  color: #0ea5e9;
}

.submit-pill {
  background: linear-gradient(135deg, #0ea5e9, #38bdf8);
  border-radius: 48rpx;
  padding: 24rpx 72rpx;
  box-shadow: 0 8rpx 24rpx rgba(14, 165, 233, 0.35);
  transition: all 0.3s;
  cursor: pointer;
  border: 2rpx solid rgba(255, 255, 255, 0.3);
}

.submit-pill:hover {
  transform: translateY(-2rpx);
  box-shadow: 0 12rpx 32rpx rgba(14, 165, 233, 0.45);
}

.submit-pill:active { 
  transform: scale(0.96);
  box-shadow: 0 4rpx 12rpx rgba(14, 165, 233, 0.35);
}

.submit-text {
  font-size: 30rpx;
  color: #fff;
  font-weight: 800;
}

/* ===== 鍝嶅簲寮忚缃?===== */
/* 灏忓睆骞曡缃?*/
@media screen and (max-width: 375px) {
  .home-container {
    padding: calc(60rpx + constant(safe-area-inset-top)) 24rpx 180rpx 24rpx;
    padding: calc(60rpx + env(safe-area-inset-top)) 24rpx 180rpx 24rpx;
  }
  
  .banner-swiper {
    height: 320rpx;
  }
  
  .banner-title {
    font-size: 32rpx;
  }
  
  .banner-sub {
    font-size: 22rpx;
  }
  
  .function-grid {
    gap: 16rpx;
  }
  
  .feature-card {
    padding: 28rpx 24rpx;
    min-height: 180rpx;
  }
  
  .feature-icon-wrap {
    width: 84rpx;
    height: 84rpx;
  }
  
  .feature-icon {
    font-size: 48rpx;
  }
  
  .feature-icon-img {
    width: 60rpx;
    height: 60rpx;
  }
  
  .feature-name {
    font-size: 28rpx;
  }
  
  .feature-desc {
    font-size: 22rpx;
  }
  
  .section-title {
    font-size: 28rpx;
  }
  
  .post-card {
    padding: 24rpx;
  }
  
  .post-text {
    font-size: 26rpx;
  }
  
  .post-modal {
    width: 90%;
    max-width: 580rpx;
  }
}

/* 涓瓑灞忓箷璁惧 */
@media screen and (min-width: 376px) and (max-width: 414px) {
  .home-container {
    padding: calc(70rpx + constant(safe-area-inset-top)) 28rpx 190rpx 28rpx;
    padding: calc(70rpx + env(safe-area-inset-top)) 28rpx 190rpx 28rpx;
  }
  
  .banner-swiper {
    height: 360rpx;
  }
  
  .feature-card {
    padding: 30rpx 26rpx;
    min-height: 190rpx;
  }
  
  .feature-icon-wrap {
    width: 90rpx;
    height: 90rpx;
  }
  
  .feature-icon {
    font-size: 50rpx;
  }
  
  .feature-icon-img {
    width: 64rpx;
    height: 64rpx;
  }
  
  .post-modal {
    width: 85%;
    max-width: 620rpx;
  }
}

/* 澶у睆骞曡缃?*/
@media screen and (min-width: 415px) {
  .home-container {
    padding: calc(80rpx + constant(safe-area-inset-top)) 32rpx 200rpx 32rpx;
    padding: calc(80rpx + env(safe-area-inset-top)) 32rpx 200rpx 32rpx;
  }
  
  .banner-swiper {
    height: 380rpx;
  }
  
  .function-grid {
    gap: 24rpx;
  }
  
  .feature-card {
    padding: 32rpx 28rpx;
    min-height: 200rpx;
  }
  
  .feature-icon-wrap {
    width: 96rpx;
    height: 96rpx;
  }
  
  .feature-icon {
    font-size: 52rpx;
  }
  
  .feature-icon-img {
    width: 68rpx;
    height: 68rpx;
  }
  
  .feature-name {
    font-size: 32rpx;
  }
  
  .feature-desc {
    font-size: 24rpx;
  }
  
  .post-modal {
    width: 80%;
    max-width: 640rpx;
  }
}

/* 妯睆閫傞厤 */
@media screen and (orientation: landscape) {
  .home-container {
    padding: calc(40rpx + constant(safe-area-inset-top)) 32rpx 120rpx 32rpx;
    padding: calc(40rpx + env(safe-area-inset-top)) 32rpx 120rpx 32rpx;
  }
  
  .banner-swiper {
    height: 280rpx;
  }
  
  .function-grid {
    grid-template-columns: repeat(4, 1fr);
  }
  
  .feature-card {
    min-height: 160rpx;
    padding: 24rpx 20rpx;
  }
  
  .feature-icon-wrap {
    width: 76rpx;
    height: 76rpx;
  }
  
  .feature-icon {
    font-size: 44rpx;
  }
  
  .feature-icon-img {
    width: 56rpx;
    height: 56rpx;
  }
  
  .feature-name {
    font-size: 26rpx;
  }
  
  .feature-desc {
    font-size: 20rpx;
  }
  
  .posts-scroll {
    height: calc(100vh - 450rpx);
  }
  
  .post-modal {
    width: 60%;
    max-width: 560rpx;
  }
}

/* 楂樺垎杈ㄧ巼璁惧浼樺寲 */
@media screen and (min-width: 768px) {
  .home-container {
    max-width: 750rpx;
    margin: 0 auto;
  }
  
  .function-grid {
    grid-template-columns: repeat(4, 1fr);
  }
  
  .feature-card {
    min-height: 180rpx;
  }
  
  .posts-list {
    gap: 28rpx;
  }
  
  .post-modal {
    width: 70%;
    max-width: 700rpx;
  }
}
</style>
