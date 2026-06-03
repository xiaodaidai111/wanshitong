<template>
  <view class="recipe-recommendation-view">
    <view class="view-header">
      <view class="back-button" @click="goBack">
        <text class="back-icon">←</text>
      </view>
      <view class="header-decoration"></view>
      <view class="view-title">课程资源推荐榜</view>
      <view class="view-subtitle">智能推荐，适配每一次学习</view>
      <view class="favorites-button" @click="goToFavorites">
        <text class="favorites-icon">❤️</text>
      </view>
    </view>

    <view class="content-container">
      <!-- 菜品列表 -->
      <scroll-view class="recipes-scroll" scroll-y="true">
        <view class="recipes-list">
          <view
            v-for="(recipe, index) in currentRecipes"
            :key="recipe.id"
            class="recipe-card"
            @click="viewRecipeDetail(recipe)"
          >
            <view class="recipe-image-wrap">
              <image
                :src="getImageUrl(recipe.image)"
                mode="aspectFill"
                class="recipe-image"
                :lazy-load="true"
                @error="handleImageError"
              ></image>
              <view v-if="!recipe.is_liked" class="recipe-rank-badge" :class="'rank-' + (index + 1)">
                {{ index + 1 }}
              </view>
            </view>
            <view class="recipe-info">
              <view class="recipe-name">{{ recipe.name }}</view>
              <view class="recipe-rating">
                <view class="rating-stars">
                  <text
                    v-for="i in 5"
                    :key="i"
                    class="star"
                  :class="{ 'filled': i <= Math.round(recipe.avg_rating || 0) }"
                >
                  ★
                </text>
                </view>
                <text class="rating-text">{{ (recipe.avg_rating || 0).toFixed(1) }}分</text>
              </view>
              <view class="recipe-desc">{{ recipe.description }}</view>
              <view class="recipe-meta">
                <view class="recipe-difficulty" :class="'difficulty-' + (recipe.difficulty || '中等')">
                  {{ getDifficultyText(recipe.difficulty) }}
                </view>
                <view class="recipe-time">{{ recipe.cooking_time }}分钟</view>
                <view class="recipe-calories">{{ recipe.calories }}学习点</view>
              </view>
            </view>
          </view>
        </view>

        <!-- 空状态 -->
        <view class="empty-state" v-if="currentRecipes.length === 0 && !loading">
          <text class="empty-icon">🍽️</text>
          <text class="empty-text">暂无推荐资源</text>
        </view>
      </scroll-view>
    </view>

    <!-- 菜品详情弹窗 -->
    <view class="modal-overlay" v-if="showRecipeDetail" @click="showRecipeDetail = false">
      <view class="recipe-detail-modal" @click.stop>
        <view class="modal-drag-bar"></view>

        <view class="detail-header">
          <view class="detail-close-btn" @click="showRecipeDetail = false">
            <text class="close-icon">✕</text>
          </view>
        </view>

        <scroll-view class="detail-content" scroll-y="true">
          <image
            :src="getImageUrl(selectedRecipe.image)"
            mode="aspectFill"
            class="detail-image"
            :lazy-load="true"
            @error="handleImageError"
          ></image>

          <view class="detail-info">
            <view class="detail-name">{{ selectedRecipe.name }}</view>
            <view class="detail-description">{{ selectedRecipe.description }}</view>

            <view class="detail-meta">
              <view class="detail-meta-item">
                <text class="meta-label">学习时长</text>
                <text class="meta-value">{{ selectedRecipe.cooking_time }}分钟</text>
              </view>
              <view class="detail-meta-item">
                <text class="meta-label">难度</text>
                <text class="meta-value">{{ getDifficultyText(selectedRecipe.difficulty) }}</text>
              </view>
              <view class="detail-meta-item">
                <text class="meta-label">学习点</text>
                <text class="meta-value">{{ selectedRecipe.calories }}点</text>
              </view>
            </view>

            <view class="detail-rating">
              <view class="rating-stars">
                <text
                  v-for="i in 5"
                  :key="i"
                  class="star"
                  :class="{ 'filled': i <= Math.round(selectedRecipe.avg_rating) }"
                >
                  ★
                </text>
              </view>
              <text class="rating-text">{{ selectedRecipe.avg_rating.toFixed(1) }}分</text>
              <text class="rating-count">({{ selectedRecipe.rating_count }}人评分)</text>
            </view>

            <view class="detail-section">
              <view class="section-title">资源组成</view>
              <view class="ingredients-list">
                <view
                  v-for="(ingredient, idx) in getIngredients(selectedRecipe)"
                  :key="idx"
                  class="ingredient-item"
                >
                  <view class="ingredient-dot"></view>
                  <text class="ingredient-text">{{ ingredient }}</text>
                </view>
              </view>
            </view>

            <view class="detail-section">
              <view class="section-title">学习步骤</view>
              <view class="steps-list">
                <view
                  v-for="(step, idx) in getSteps(selectedRecipe)"
                  :key="idx"
                  class="step-item"
                >
                  <view class="step-number">{{ idx + 1 }}</view>
                  <text class="step-text">{{ step }}</text>
                </view>
              </view>
            </view>

            <view class="detail-section">
              <view class="section-title">学习反馈</view>
              <view class="comments-section">
                <view
                  v-for="(comment, idx) in recipeComments"
                  :key="idx"
                  class="comment-item"
                >
                  <view class="comment-header">
                    <image
                      :src="comment.user_avatar || '../../static/头像1.png'"
                      mode="aspectFill"
                      class="comment-avatar"
                    ></image>
                    <view class="comment-user-info">
                      <text class="comment-user-name">{{ comment.user_name }}</text>
                      <text class="comment-time">{{ formatTime(comment.created_at) }}</text>
                    </view>
                  </view>
                  <text class="comment-content">{{ comment.content }}</text>
                </view>

                <view class="load-more-comments" v-if="hasMoreComments" @click="loadMoreComments">
                  <text class="load-more-text">加载更多评论</text>
                </view>
              </view>
            </view>
          </view>
        </scroll-view>

        <view class="detail-footer">
          <view class="footer-action" @click="toggleLike(selectedRecipe)">
            <text class="footer-icon">{{ selectedRecipe.is_liked ? '❤️' : '🤍' }}</text>
            <text class="footer-text">{{ selectedRecipe.is_liked ? '已收藏' : '收藏' }}</text>
          </view>
          <view class="footer-action primary" @click="openCommentModal(selectedRecipe)">
            <text class="footer-icon">💬</text>
            <text class="footer-text">评价</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 评价模态框 -->
    <view class="modal-overlay" v-if="showCommentModal" @click="showCommentModal = false">
      <view class="comment-modal" @click.stop>
        <view class="modal-drag-bar"></view>
        <view class="modal-header">
          <text class="modal-title">写评价</text>
          <view class="modal-close-btn" @click="showCommentModal = false">
            <text class="close-icon">✕</text>
          </view>
        </view>
        <view class="modal-content">
          <view class="rating-section">
            <text class="rating-label">评分</text>
            <view class="rating-stars">
              <text
                v-for="i in 5"
                :key="i"
                class="star"
                :class="{ 'filled': i <= commentRating }"
                @click="commentRating = i"
              >
                ★
              </text>
            </view>
          </view>
          <view class="comment-section">
            <text class="comment-label">评价内容</text>
            <textarea
              v-model="commentContent"
              placeholder="请输入您的评价..."
              class="comment-input"
              rows="4"
            ></textarea>
          </view>
          <view class="modal-footer">
            <button class="cancel-btn" @click="showCommentModal = false">取消</button>
            <button class="submit-btn" @click="submitComment">提交评价</button>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import recipesData from '../../static/food/recipes.json';

export default {
  data() {
    return {
      tabs: [
        { name: '热门推荐', icon: '🔥', type: 'hot' },
        { name: '入门友好', icon: '🌱', type: 'beginner' },
        { name: '快速复盘', icon: '⚡', type: 'quick' },
        { name: '题库训练', icon: '💪', type: 'nutritious' },
        { name: '实操案例', icon: '💰', type: 'economical' },
        { name: '我的收藏', icon: '❤️', type: 'favorites' }
      ],
      currentTab: 0,
      currentRecipes: [],
      loading: false,
      hasMore: false,
      page: 1,
      pageSize: 10,
      showRecipeDetail: false,
      selectedRecipe: {},
      recipeComments: [],
      hasMoreComments: false,
      commentPage: 1,
      showCommentModal: false,
      commentContent: '',
      commentRating: 5,
      favoriteRecipes: [],
      allRecipes: [
        {
          id: 1,
          name: '人工智能导论：搜索算法讲解包',
          description: '覆盖状态空间、树搜索、图搜索与启发式搜索，适合零基础到进阶复盘。',
          image: 'food.png',
          avg_rating: 4.9,
          rating_count: 128,
          like_count: 1800,
          difficulty: '简单',
          cooking_time: 25,
          calories: 90,
          tags: ['入门友好', '题库训练'],
          ingredients: ['课程讲解文档', '知识点思维导图', '分层练习题'],
          steps: ['阅读搜索问题建模说明', '完成 BFS/DFS 对比题', '根据错题回看图搜索部分'],
          is_liked: false
        },
        {
          id: 2,
          name: 'A* 搜索算法代码实操案例',
          description: '从地图网格路径规划切入，提供伪代码、Python 示例和测试数据。',
          image: 'cookexpret.png',
          avg_rating: 4.8,
          rating_count: 96,
          like_count: 1420,
          difficulty: '中等',
          cooking_time: 40,
          calories: 120,
          tags: ['实操案例', '项目任务'],
          ingredients: ['启发式函数说明', 'Python 示例代码', '测试用例'],
          steps: ['理解 open/closed 集合', '实现优先队列搜索', '运行测试并分析路径结果'],
          is_liked: true
        },
        {
          id: 3,
          name: '机器学习基础错题训练包',
          description: '围绕过拟合、损失函数、梯度下降生成选择题、简答题和案例题。',
          image: 'safeguard.png',
          avg_rating: 4.7,
          rating_count: 88,
          like_count: 1210,
          difficulty: '中等',
          cooking_time: 30,
          calories: 100,
          tags: ['题库训练', '快速复盘'],
          ingredients: ['选择题', '简答题', '错因解析'],
          steps: ['先做基础选择题', '查看错因解析', '完成案例迁移题'],
          is_liked: false
        }
      ],
      mockComments: [
        {
          user_name: 'AI导学员',
          user_avatar: '../../static/avatar-1.png',
          content: '这份资源把搜索算法讲得很清楚，导图和题库搭配起来复盘效率很高。',
          created_at: new Date(Date.now() - 3600000 * 2).toISOString()
        },
        {
          user_name: '代码实操同学',
          user_avatar: '../../static/avatar-2.png',
          content: '作为新手，案例步骤很清晰，第一次就跑通了 A* 搜索代码。',
          created_at: new Date(Date.now() - 3600000 * 5).toISOString()
        },
        {
          user_name: '课程复盘员',
          user_avatar: '../../static/avatar-3.png',
          content: '讲解清晰，练习题和实操案例搭配合理，非常适合课后复盘，强烈推荐！',
          created_at: new Date(Date.now() - 3600000 * 8).toISOString()
        }
      ]
    }
  },
  
  computed: {
    currentListType() {
      return this.tabs[this.currentTab].type;
    }
  },
  
  onLoad() {
    this.currentRecipes = [...this.allRecipes];
    
    // 初始化收藏列表，将所有已标记为收藏的菜品添加到收藏列表中
    this.favoriteRecipes = this.allRecipes.filter(recipe => recipe.is_liked);
  },
  
  methods: {
    goBack() {
      uni.navigateBack({
        delta: 1
      });
    },
    
    goToFavorites() {
      // 找到"我的收藏"标签的索引
      const favoritesTabIndex = this.tabs.findIndex(tab => tab.type === 'favorites');
      if (favoritesTabIndex !== -1) {
        this.currentTab = favoritesTabIndex;
        this.filterRecipes();
      }
    },
    
    getImageUrl(imagePath) {
      if (!imagePath) {
        return '../../static/food.png';
      }
      if (imagePath.startsWith('http')) {
        return imagePath;
      }
      return '../../static/' + imagePath;
    },
    
    handleImageError(e) {
      console.warn('图片加载失败:', e);
      e.target.src = '../../static/food.png';
    },

    loadLocalRecipes() {
    },

    filterRecipes() {
      const listType = this.currentListType;
      let filtered = [...this.allRecipes];

      switch(listType) {
        case 'hot':
          filtered = filtered.filter(r => r.like_count > 1000);
          break;
        case 'beginner':
          filtered = filtered.filter(r => r.difficulty === '简单');
          break;
        case 'quick':
          filtered = filtered.filter(r => r.cooking_time <= 30);
          break;
        case 'nutritious':
          filtered = filtered.filter(r => r.tags.includes('题库训练'));
          break;
        case 'economical':
          filtered = filtered.filter(r => r.tags.includes('实操案例'));
          break;
        case 'favorites':
          filtered = [...this.favoriteRecipes];
          break;
      }

      this.currentRecipes = filtered;
      this.hasMore = false;
    },
    
    switchTab(index) {
      this.currentTab = index;
      this.filterRecipes();
    },
    
    loadRecipes() {
    },
    
    loadMoreRecipes() {
    },
    
    getListId() {
      return 1;
    },
    
    getDifficultyText(difficulty) {
      const map = {
        '简单': '简单',
        '中等': '中等',
        '困难': '困难'
      };
      return map[difficulty] || '未知';
    },
    
    getIngredients(recipe) {
      return recipe.ingredients || [];
    },
    
    getSteps(recipe) {
      return recipe.steps || [];
    },
    
    viewRecipeDetail(recipe) {
      this.selectedRecipe = recipe;
      this.showRecipeDetail = true;
      this.recipeComments = [...this.mockComments];
    },
    
    loadRecipeComments(recipeId) {
    },
    
    loadMoreComments() {
    },
    
    toggleLike(recipe) {
      recipe.is_liked = !recipe.is_liked;
      recipe.like_count += recipe.is_liked ? 1 : -1;
      
      if (recipe.is_liked) {
        // 检查是否已经在收藏列表中，避免重复添加
        const existingIndex = this.favoriteRecipes.findIndex(r => r.id === recipe.id);
        if (existingIndex === -1) {
          // 添加到收藏列表
          this.favoriteRecipes.push(recipe);
          uni.showToast({
            title: '已收藏 ❤️',
            icon: 'none',
            duration: 1200
          });
        } else {
          // 已经在收藏列表中，更新状态
          this.favoriteRecipes[existingIndex].is_liked = true;
          uni.showToast({
            title: '已收藏 ❤️',
            icon: 'none',
            duration: 1200
          });
        }
      } else {
        // 从收藏列表移除
        const index = this.favoriteRecipes.findIndex(r => r.id === recipe.id);
        if (index !== -1) {
          this.favoriteRecipes.splice(index, 1);
          uni.showToast({
            title: '已取消收藏',
            icon: 'none',
            duration: 1200
          });
        }
      }
      
      // 如果当前在收藏标签页，重新过滤以更新列表
      if (this.currentListType === 'favorites') {
        this.filterRecipes();
      }
    },
    
    shareRecipe(recipe) {
      uni.showToast({ title: '分享成功', icon: 'success' });
    },
    
    openCommentModal(recipe) {
      this.showCommentModal = true;
      this.commentContent = '';
      this.commentRating = 5;
    },
    
    submitComment() {
      if (!this.commentContent.trim()) {
        uni.showToast({ title: '请输入评价内容', icon: 'none' });
        return;
      }
      
      // 创建新评论
      const newComment = {
        user_name: '当前用户',
        user_avatar: '../../static/avatar-1.png',
        content: this.commentContent,
        rating: this.commentRating,
        created_at: new Date().toISOString()
      };
      
      // 添加到评价列表中
      this.recipeComments.unshift(newComment);
      
      // 更新菜品评分
      this.updateRecipeRating(this.commentRating);
      
      // 关闭模态框
      this.showCommentModal = false;
      
      // 显示成功提示
      uni.showToast({ title: '评价提交成功', icon: 'success' });
    },
    
    updateRecipeRating(newRating) {
      const recipe = this.selectedRecipe;
      if (!recipe) return;
      
      // 初始化评分数数据
      if (!recipe.avg_rating) {
        recipe.avg_rating = newRating;
        recipe.rating_count = 1;
      } else {
        // 计算新的平均评分
        const totalRating = recipe.avg_rating * recipe.rating_count;
        recipe.rating_count += 1;
        recipe.avg_rating = (totalRating + newRating) / recipe.rating_count;
      }
      
      // 更新所有菜品列表中的对应菜品评分
      const recipeIndex = this.currentRecipes.findIndex(r => r.id === recipe.id);
      if (recipeIndex !== -1) {
        this.currentRecipes[recipeIndex].avg_rating = recipe.avg_rating;
        this.currentRecipes[recipeIndex].rating_count = recipe.rating_count;
      }
    },
    

    
    formatTime(timestamp) {
      const now = new Date();
      const time = new Date(timestamp);
      const diff = now - time;
      const minute = 60 * 1000;
      const hour = 60 * minute;
      const day = 24 * hour;
      
      if (diff < minute) return '刚刚';
      if (diff < hour) return Math.floor(diff / minute) + '分钟前';
      if (diff < day) return Math.floor(diff / hour) + '小时前';
      if (diff < day * 7) return Math.floor(diff / day) + '天前';
      return time.toLocaleDateString('zh-CN');
    }
  }
}
</script>

<style scoped>
.recipe-recommendation-view {
  min-height: 100vh;
  background: linear-gradient(135deg, #e8f4ff 0%, #d4e9ff 50%, #c5ddff 100%);
  padding: calc(44px + constant(safe-area-inset-top)) 32rpx 0 32rpx;
  padding: calc(44px + env(safe-area-inset-top)) 32rpx 0 32rpx;
}

.view-header {
  padding: 60rpx 0 40rpx;
  text-align: center;
  position: relative;
}

.back-button {
  position: absolute;
  top: 60rpx;
  left: 0;
  width: 64rpx;
  height: 64rpx;
  background: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4rpx 16rpx rgba(24, 144, 255, 0.15);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  z-index: 10;
}

.back-button:active {
  transform: scale(0.9);
  box-shadow: 0 2rpx 8rpx rgba(24, 144, 255, 0.2);
}

.back-icon {
  font-size: 32rpx;
  font-weight: 700;
  color: #0c4a6e;
  line-height: 1;
}

.favorites-button {
  position: absolute;
  top: 60rpx;
  right: 0;
  width: 64rpx;
  height: 64rpx;
  background: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4rpx 16rpx rgba(24, 144, 255, 0.15);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  z-index: 10;
}

.favorites-button:active {
  transform: scale(0.9);
  box-shadow: 0 2rpx 8rpx rgba(24, 144, 255, 0.2);
}

.favorites-icon {
  font-size: 32rpx;
  line-height: 1;
}

.header-decoration {
  position: absolute;
  top: -100rpx;
  right: -100rpx;
  width: 400rpx;
  height: 400rpx;
  background: radial-gradient(circle, rgba(24, 144, 255, 0.1) 0%, transparent 70%);
  animation: float 6s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0) scale(1); }
  50% { transform: translateY(-20rpx) scale(1.05); }
}

.view-title {
  font-size: 48rpx;
  color: #1a365d;
  font-weight: 800;
  letter-spacing: 2rpx;
  text-shadow: 0 2rpx 8rpx rgba(24, 144, 255, 0.2);
  margin-bottom: 12rpx;
}

.view-subtitle {
  font-size: 24rpx;
  color: #5a7ca5;
  font-weight: 400;
  letter-spacing: 1rpx;
}

.content-container {
  display: flex;
  flex-direction: column;
  gap: 24rpx;
  margin: 0 auto;
  padding-bottom: 120rpx;
}

.recipes-scroll {
  min-height: 600rpx;
}

.recipes-list {
  display: flex;
  flex-direction: column;
  gap: 24rpx;
}

.recipe-card {
  display: flex;
  flex-direction: row;
  background: white;
  border-radius: 24rpx;
  overflow: hidden;
  box-shadow: 0 6rpx 24rpx rgba(24, 144, 255, 0.12);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
}

.recipe-card:active {
  transform: scale(0.98);
  box-shadow: 0 4rpx 16rpx rgba(24, 144, 255, 0.15);
}

.recipe-image-wrap {
  position: relative;
  width: 240rpx;
  height: 240rpx;
  flex-shrink: 0;
  overflow: hidden;
}

.recipe-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  background: #f1f5f9;
  transition: transform 0.3s ease;
}

.recipe-card:active .recipe-image {
  transform: scale(1.05);
}

.recipe-info {
  flex: 1;
  padding: 20rpx 24rpx;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 12rpx;
  min-width: 0;
}

.recipe-name {
  font-size: 30rpx;
  font-weight: 700;
  color: #1e293b;
  line-height: 1.4;
  letter-spacing: 0.5rpx;
  margin-bottom: 8rpx;
}

.recipe-rating {
  display: flex;
  align-items: center;
  gap: 8rpx;
  margin-bottom: 12rpx;
}

.recipe-rating .rating-stars {
  display: flex;
  gap: 2rpx;
}

.recipe-rating .star {
  font-size: 20rpx;
  opacity: 0.3;
}

.recipe-rating .star.filled {
  opacity: 1;
  color: #ffb800;
}

.recipe-rating .rating-text {
  font-size: 22rpx;
  font-weight: 600;
  color: #ea580c;
}

.recipe-desc {
  font-size: 24rpx;
  color: #64748b;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.recipe-meta {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.recipe-difficulty {
  font-size: 22rpx;
  font-weight: 600;
  padding: 4rpx 16rpx;
  border-radius: 8rpx;
}

.recipe-difficulty.difficulty-简单{
  color: #16a34a;
  background: #f0fdf4;
}

.recipe-difficulty.difficulty-中等 {
  color: #ea580c;
  background: #fff7ed;
}

.recipe-difficulty.difficulty-困难 {
  color: #dc2626;
  background: #fef2f2;
}

.recipe-time {
  font-size: 22rpx;
  color: #64748b;
}

.recipe-calories {
  font-size: 22rpx;
  color: #64748b;
}

.recipe-rank-badge {
  position: absolute;
  top: 12rpx;
  left: 12rpx;
  width: 48rpx;
  height: 48rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24rpx;
  font-weight: 800;
  color: #94a3b8;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 12rpx;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.1);
  z-index: 1;
}

.recipe-rank-badge.rank-1 {
  background: linear-gradient(135deg, #ffd700 0%, #ffae00 100%);
  color: white;
  box-shadow: 0 4rpx 12rpx rgba(255, 174, 0, 0.4);
}

.recipe-rank-badge.rank-2 {
  background: linear-gradient(135deg, #c0c0c0 0%, #a0a0a0 100%);
  color: white;
  box-shadow: 0 4rpx 12rpx rgba(160, 160, 160, 0.4);
}

.recipe-rank-badge.rank-3 {
  background: linear-gradient(135deg, #cd7f32 0%, #b87333 100%);
  color: white;
  box-shadow: 0 4rpx 12rpx rgba(184, 115, 51, 0.4);
}

.empty-state {
  text-align: center;
  padding: 100rpx 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 24rpx;
}

.empty-icon {
  font-size: 100rpx;
}

.empty-text {
  font-size: 28rpx;
  color: #94a3b8;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(15, 23, 42, 0.5);
  backdrop-filter: blur(10px);
  display: flex;
  align-items: flex-end;
  z-index: 2000;
}

.recipe-detail-modal {
  width: 100%;
  height: 90vh;
  background: white;
  border-radius: 48rpx 48rpx 0 0;
  display: flex;
  flex-direction: column;
  box-shadow: 0 -16rpx 40rpx rgba(14, 165, 233, 0.2);
  animation: slideUp 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes slideUp {
  from {
    transform: translateY(100%);
  }
  to {
    transform: translateY(0);
  }
}

.modal-drag-bar {
  width: 60rpx;
  height: 6rpx;
  background: linear-gradient(90deg, #0ea5e9, #38bdf8);
  border-radius: 6rpx;
  margin: 24rpx auto 12rpx;
}

.detail-header {
  display: flex;
  justify-content: flex-end;
  padding: 0 32rpx;
}

.detail-close-btn {
  width: 64rpx;
  height: 64rpx;
  background: linear-gradient(135deg, #0ea5e9, #38bdf8);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
}

.detail-close-btn:active {
  transform: scale(0.9);
}

.close-icon {
  font-size: 28rpx;
  color: white;
}

.detail-content {
  flex: 1;
  overflow-y: auto;
}

.detail-image {
  width: 100%;
  height: 500rpx;
  object-fit: cover;
  background: #f1f5f9;
}

.detail-image[mode="aspectFill"] {
  object-fit: cover;
}

.detail-info {
  padding: 32rpx;
}

.detail-name {
  font-size: 40rpx;
  font-weight: 800;
  color: #0c4a6e;
  margin-bottom: 16rpx;
}

.detail-description {
  font-size: 26rpx;
  color: #64748b;
  line-height: 1.6;
  margin-bottom: 24rpx;
}

.detail-meta {
  display: flex;
  gap: 24rpx;
  margin-bottom: 24rpx;
  padding: 20rpx;
  background: #f8fafc;
  border-radius: 16rpx;
}

.detail-meta-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8rpx;
}

.meta-label {
  font-size: 22rpx;
  color: #94a3b8;
}

.meta-value {
  font-size: 28rpx;
  color: #0c4a6e;
  font-weight: 700;
}

.detail-rating {
  display: flex;
  align-items: center;
  gap: 12rpx;
  margin-bottom: 32rpx;
  padding: 20rpx;
  background: linear-gradient(135deg, #fff7ed 0%, #ffedd5 100%);
  border-radius: 16rpx;
}

.rating-stars {
  display: flex;
  gap: 4rpx;
}

.star {
  font-size: 28rpx;
  opacity: 0.3;
}

.star.filled {
  opacity: 1;
}

.rating-text {
  font-size: 28rpx;
  font-weight: 700;
  color: #ea580c;
}

.rating-count {
  font-size: 22rpx;
  color: #94a3b8;
}

.detail-section {
  margin-bottom: 32rpx;
}

.section-title {
  font-size: 32rpx;
  font-weight: 700;
  color: #0c4a6e;
  margin-bottom: 20rpx;
}

.ingredients-list {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.ingredient-item {
  display: flex;
  align-items: center;
  gap: 12rpx;
}

.ingredient-dot {
  width: 8rpx;
  height: 8rpx;
  background: #0ea5e9;
  border-radius: 50%;
}

.ingredient-text {
  font-size: 26rpx;
  color: #334155;
  line-height: 1.6;
}

.steps-list {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.step-item {
  display: flex;
  gap: 16rpx;
}

.step-number {
  width: 40rpx;
  height: 40rpx;
  background: linear-gradient(135deg, #0ea5e9, #38bdf8);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22rpx;
  font-weight: 700;
  border-radius: 12rpx;
  flex-shrink: 0;
}

.step-text {
  flex: 1;
  font-size: 26rpx;
  color: #334155;
  line-height: 1.6;
}

.comments-section {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.comment-item {
  padding: 20rpx;
  background: #f8fafc;
  border-radius: 16rpx;
}

.comment-header {
  display: flex;
  align-items: center;
  gap: 12rpx;
  margin-bottom: 12rpx;
}

.comment-avatar {
  width: 60rpx;
  height: 60rpx;
  border-radius: 50%;
}

.comment-user-info {
  display: flex;
  flex-direction: column;
  gap: 4rpx;
}

.comment-user-name {
  font-size: 26rpx;
  font-weight: 600;
  color: #0c4a6e;
}

.comment-time {
  font-size: 22rpx;
  color: #94a3b8;
}

.comment-content {
  font-size: 26rpx;
  color: #334155;
  line-height: 1.6;
}

.load-more-comments {
  text-align: center;
  padding: 20rpx;
  background: #f0f9ff;
  border-radius: 12rpx;
  cursor: pointer;
}

.load-more-text {
  font-size: 24rpx;
  color: #0ea5e9;
  font-weight: 600;
}

.detail-footer {
  display: flex;
  gap: 16rpx;
  padding: 24rpx 32rpx;
  border-top: 2rpx solid #f1f5f9;
  background: white;
}

.footer-action {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8rpx;
  padding: 16rpx;
  background: #f8fafc;
  border-radius: 16rpx;
  transition: all 0.2s;
}

.footer-action:active {
  transform: scale(0.95);
}

.footer-action.primary {
  background: linear-gradient(135deg, #0ea5e9, #38bdf8);
}

.footer-icon {
  font-size: 32rpx;
}

.footer-text {
  font-size: 22rpx;
  font-weight: 600;
  color: #64748b;
}

.footer-action.primary .footer-text {
  color: white;
}

.comment-modal {
  width: 100%;
  max-height: 70vh;
  background: white;
  border-radius: 48rpx 48rpx 0 0;
  display: flex;
  flex-direction: column;
  box-shadow: 0 -16rpx 40rpx rgba(14, 165, 233, 0.2);
  animation: slideUp 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24rpx 32rpx;
  border-bottom: 2rpx solid #f1f5f9;
}

.modal-title {
  font-size: 32rpx;
  font-weight: 700;
  color: #0c4a6e;
}

.modal-close-btn {
  width: 56rpx;
  height: 56rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.3s;
}

.modal-close-btn:active {
  background: #f1f5f9;
}

.modal-content {
  padding: 32rpx;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 24rpx;
}

.rating-section {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.rating-label {
  font-size: 28rpx;
  font-weight: 600;
  color: #0c4a6e;
}

.rating-section .rating-stars {
  display: flex;
  gap: 16rpx;
}

.rating-section .star {
  font-size: 40rpx;
  opacity: 0.3;
  cursor: pointer;
  transition: all 0.3s;
}

.rating-section .star.filled {
  opacity: 1;
  color: #ffb800;
  transform: scale(1.1);
}

.comment-section {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
  flex: 1;
}

.comment-label {
  font-size: 28rpx;
  font-weight: 600;
  color: #0c4a6e;
}

.comment-input {
  flex: 1;
  padding: 20rpx;
  border: 2rpx solid #e2e8f0;
  border-radius: 16rpx;
  font-size: 26rpx;
  color: #334155;
  resize: none;
  min-height: 200rpx;
}

.comment-input::placeholder {
  color: #94a3b8;
}

.modal-footer {
  display: flex;
  gap: 16rpx;
  margin-top: 16rpx;
}

.cancel-btn,
.submit-btn {
  flex: 1;
  padding: 20rpx;
  border-radius: 16rpx;
  font-size: 28rpx;
  font-weight: 600;
  transition: all 0.3s;
}

.cancel-btn {
  background: #f8fafc;
  color: #64748b;
  border: none;
}

.submit-btn {
  background: linear-gradient(135deg, #0ea5e9, #38bdf8);
  color: white;
  border: none;
}

.cancel-btn:active,
.submit-btn:active {
  transform: scale(0.95);
}

@media screen and (max-width: 375px) {
  .recipe-image-wrap {
    width: 200rpx;
    height: 200rpx;
  }

  .recipe-name {
    font-size: 26rpx;
  }

  .detail-name {
    font-size: 36rpx;
  }

  .detail-image {
    height: 400rpx;
  }
}

@media screen and (min-width: 376px) and (max-width: 414px) {
  .detail-image {
    height: 450rpx;
  }
}

@media screen and (min-width: 415px) {
  .detail-image {
    height: 500rpx;
  }
}

@media screen and (min-width: 768px) {
  .recipe-image-wrap {
    width: 280rpx;
    height: 280rpx;
  }
}

@media screen and (orientation: landscape) {
  .recipe-detail-modal {
    height: 80vh;
  }

  .detail-image {
    height: 400rpx;
  }
}
</style>
