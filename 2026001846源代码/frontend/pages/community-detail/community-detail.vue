<template>
    <view class="detail-container">
    <!-- 社区头部信息 -->
    <view class="community-header">
      <view class="header-cover">
        <image 
          :src="community.cover_image || '../../static/equipment.png'" 
          mode="aspectFill" 
          class="cover-image"
        ></image>
        <view class="cover-gradient"></view>
      </view>

      <view class="header-content">
        <view class="community-basic">
          <image 
            :src="community.avatar || '../../static/GGbond.png'" 
            mode="aspectFill" 
            class="community-avatar"
          ></image>
          <view class="basic-info">
            <text class="community-name">{{ community.name }}</text>
            <view class="community-meta">
              <text class="meta-item">{{ community.category }}</text>
              <text class="meta-separator">·</text>
              <text class="meta-item">{{ community.address || '未知地址' }}</text>
            </view>
          </view>
        </view>

        <text class="community-desc">{{ community.description }}</text>

        <!-- 社区数据统计 -->
        <view class="community-stats">
          <view class="stat-box">
            <text class="stat-value">{{ community.current_members }}</text>
            <text class="stat-label">成员</text>
          </view>
          <view class="stat-box">
            <text class="stat-value">{{ community.post_count }}</text>
            <text class="stat-label">帖子</text>
          </view>
          <view class="stat-box">
            <text class="stat-value">{{ community.activity_score }}</text>
            <text class="stat-label">活跃度</text>
          </view>
        </view>

        <!-- 加入按钮 -->
        <view class="join-section">
          <view 
            class="join-btn" 
            :class="{ 'joined': community.is_joined }"
            @click="handleJoin"
          >
            <text class="join-text">{{ community.is_joined ? '已加入' : '加入社区' }}</text>
          </view>
          <view class="share-btn" @click="shareCommunity">
            <text class="share-icon">📤</text>
          </view>
        </view>

        <!-- 社区标签 -->
        <view class="community-tags" v-if="community.tags && community.tags.length > 0">
          <view 
            v-for="(tag, index) in community.tags" 
            :key="index"
            class="tag-item"
          >
            {{ tag }}
          </view>
        </view>
      </view>
    </view>

    <!-- 管理员列表 -->
    <view class="admins-section" v-if="community.admins && community.admins.length > 0">
      <text class="section-title">管理员</text>
      <scroll-view class="admins-scroll" scroll-x>
        <view class="admins-list">
          <view 
            v-for="(admin, index) in community.admins" 
            :key="index"
            class="admin-item"
          >
            <image 
              :src="admin.avatar || '../../static/avatar-3.png'" 
              mode="aspectFill" 
              class="admin-avatar"
            ></image>
            <text class="admin-name">{{ admin.name }}</text>
            <text class="admin-role">{{ getRoleName(admin.role) }}</text>
          </view>
        </view>
      </scroll-view>
    </view>

    <!-- 帖子分类Tab -->
    <view class="tabs-section">
      <view 
        v-for="(tab, index) in postTabs" 
        :key="index"
        class="tab-item"
        :class="{ 'active': currentTab === index }"
        @click="switchTab(index)"
      >
        <text class="tab-text">{{ tab.label }}</text>
        <view class="tab-dot" v-if="currentTab === index"></view>
      </view>
    </view>

    <!-- 帖子列表 -->
    <scroll-view 
      class="posts-scroll" 
      scroll-y 
      @scrolltolower="loadMorePosts"
      :lower-threshold="100"
    >
      <view class="posts-list">
        <view 
          v-for="(post, index) in posts" 
          :key="post.id"
          class="post-card"
        >
          <!-- 作者信息 -->
          <view class="post-author">
            <image 
              :src="normalizeAssetUrl(post.author_avatar, '../../static/avatar-1.png')" 
              mode="aspectFill" 
              class="author-avatar"
            ></image>
            <view class="author-info">
              <text class="author-name">{{ post.author_name }}</text>
              <text class="post-time">{{ formatTime(post.created_at) }}</text>
            </view>
            <view class="post-category">{{ post.category }}</view>
          </view>

          <!-- 帖子内容 -->
          <view class="post-content">
            <text class="post-title" v-if="post.title">{{ post.title }}</text>
            <text class="post-text">{{ post.content }}</text>
            <view class="post-images" v-if="post.images && post.images.length > 0">
              <image 
                v-for="(img, imgIndex) in post.images.slice(0, 3)" 
                :key="imgIndex"
                :src="normalizeAssetUrl(img)" 
                mode="aspectFill" 
                class="post-image"
                @click="previewImage(post.images, imgIndex)"
              ></image>
              <view 
                class="more-images" 
                v-if="post.images.length > 3"
                @click="previewImage(post.images, 0)"
              >
                <text class="more-text">+{{ post.images.length - 3 }}</text>
              </view>
            </view>
          </view>

          <!-- 互动数据 -->
          <view class="post-actions">
            <view class="action-item" @click="likePost(post)">
              <text class="action-icon">{{ post.is_liked ? '❤️' : '🤍' }}</text>
              <text class="action-count">{{ post.like_count }}</text>
            </view>
            <view class="action-item" @click="showComments(post)">
              <text class="action-icon">💬</text>
              <text class="action-count">{{ post.comment_count }}</text>
            </view>
            <view class="action-item" @click="sharePost(post)">
              <text class="action-icon">📤</text>
              <text class="action-count">{{ post.share_count || 0 }}</text>
            </view>
          </view>
        </view>

        <!-- 加载中 -->
        <view class="loading-more" v-if="loading">
          <text class="loading-text">加载中...</text>
        </view>

        <!-- 没有更多 -->
        <view class="no-more" v-if="!hasMore && posts.length > 0">
          <text class="no-more-text">已加载全部帖子</text>
        </view>

        <!-- 空状态 -->
        <view class="empty-state" v-if="posts.length === 0 && !loading">
          <text class="empty-icon">📝</text>
          <text class="empty-text">暂无帖子</text>
          <button class="empty-action" @click="showPostModal = true" v-if="community.is_joined">
            发布第一条帖子
          </button>
        </view>
      </view>
    </scroll-view>

    <!-- 悬浮发帖按钮 -->
    <view class="fab-post-btn" @click="showPostModal = true" v-if="community.is_joined">
      <text class="fab-icon">✍️</text>
      <text class="fab-text">发帖</text>
    </view>

    <!-- 发帖弹窗 -->
    <view class="modal-overlay" v-if="showPostModal" @click="showPostModal = false">
      <view class="post-modal" @click.stop>
        <view class="modal-header">
          <text class="modal-title">发布帖子</text>
          <view class="modal-close" @click="showPostModal = false">×</view>
        </view>

        <view class="modal-body">
          <input 
            class="post-title-input" 
            v-model="newPost.title" 
            placeholder="输入标题（可选）"
            maxlength="50"
          />
          <textarea 
            class="post-content-input" 
            v-model="newPost.content" 
            placeholder="分享你的想法..."
            maxlength="500"
          ></textarea>
          <text class="char-count">{{ (newPost.content || '').length }}/500</text>

          <view class="category-select">
            <text class="category-label">选择分类:</text>
            <view class="category-options">
              <view 
                v-for="(cat, index) in categoryOptions" 
                :key="index"
                class="category-option"
                :class="{ 'selected': newPost.category === cat.value }"
                @click="newPost.category = cat.value"
              >
                {{ cat.label }}
              </view>
            </view>
          </view>

          <view class="image-upload">
            <view class="upload-btn" @click="chooseImage">
              <text class="upload-icon">📷</text>
              <text class="upload-text">添加图片</text>
            </view>
            <view class="image-preview" v-if="newPost.images.length > 0">
              <view 
                v-for="(img, index) in newPost.images" 
                :key="index"
                class="preview-item"
              >
                <image :src="normalizeAssetUrl(img)" mode="aspectFill" class="preview-img"></image>
                <view class="preview-delete" @click="removeImage(index)">×</view>
              </view>
            </view>
          </view>
        </view>

        <view class="modal-footer">
          <view class="cancel-btn" @click="showPostModal = false">取消</view>
          <view class="submit-btn" @click="submitPost">发布</view>
        </view>
      </view>
    </view>

    <!-- 加入申请弹窗 -->
    <view class="modal-overlay" v-if="showJoinModal" @click="showJoinModal = false">
      <view class="join-modal" @click.stop>
        <view class="modal-header">
          <text class="modal-title">申请加入</text>
          <view class="modal-close" @click="showJoinModal = false">×</view>
        </view>

        <view class="modal-body">
          <text class="join-hint">请填写申请理由</text>
          <textarea 
            class="join-message-input" 
            v-model="joinMessage" 
            placeholder="简单介绍一下自己，说明想加入的原因..."
            maxlength="200"
          ></textarea>
          <text class="char-count">{{ (joinMessage || '').length }}/200</text>
        </view>

        <view class="modal-footer">
          <view class="cancel-btn" @click="showJoinModal = false">取消</view>
          <view class="submit-btn" @click="submitJoin">提交申请</view>
        </view>
      </view>
    </view>

    <!-- 评论弹窗 -->
    <view class="modal-overlay" v-if="showCommentModal" @click="showCommentModal = false">
      <view class="comment-modal" @click.stop>
        <view class="modal-header">
          <text class="modal-title">评论</text>
          <view class="modal-close" @click="showCommentModal = false">×</view>
        </view>

        <view class="modal-body">
          <view class="comments-list">
            <view 
              v-for="(comment, index) in comments" 
              :key="comment.id"
              class="comment-item"
            >
              <image 
                :src="normalizeAssetUrl(comment.author_avatar, '../../static/avatar-2.png')" 
                mode="aspectFill" 
                class="comment-avatar"
              ></image>
              <view class="comment-content">
                <view class="comment-header">
                  <text class="comment-author">{{ comment.author_name }}</text>
                  <text class="comment-time">{{ formatTime(comment.created_at) }}</text>
                </view>
                <text class="comment-text">{{ comment.content }}</text>
                <view class="comment-actions">
                  <view class="comment-action" @click="likeComment(comment)">
                    <text>{{ comment.is_liked ? '❤️' : '🤍' }}</text>
                    <text>{{ comment.like_count }}</text>
                  </view>
                  <view class="comment-action" @click="replyComment(comment)">
                    <text>💬 回复</text>
                  </view>
                </view>
              </view>
            </view>
          </view>

          <view class="comment-input-section">
            <input 
              class="comment-input" 
              v-model="newComment" 
              placeholder="写下你的评论..."
            />
            <view class="send-btn" @click="submitComment">发送</view>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import { API_HOST, getAssetURL, uploadFile } from '../../utils/request.js'

const COMMUNITY_API_BASE = `${API_HOST}:5000/api/community`

export default {
  data() {
    return {
      communityId: null,
      community: {},
      posts: [],
      comments: [],
      currentTab: 0,
      loading: false,
      hasMore: true,
      page: 1,
      uploadingImages: false,
      showPostModal: false,
      showJoinModal: false,
      showCommentModal: false,
      currentPost: null,
      
      newPost: {
        title: '',
        content: '',
        category: 'general',
        images: []
      },
      
      joinMessage: '',
      newComment: '',
      
      postTabs: [
        { label: '全部', value: 'all' },
        { label: '讨论', value: 'discussion' },
        { label: '分享', value: 'share' },
        { label: '问答', value: 'question' }
      ],
      
      categoryOptions: [
        { label: '综合', value: 'general' },
        { label: '讨论', value: 'discussion' },
        { label: '分享', value: 'share' },
        { label: '问答', value: 'question' }
      ]
    }
  },

  onLoad(options) {
    this.communityId = options.id;
    this.loadCommunityDetail();
    this.loadPosts();
  },

  methods: {
    normalizeAssetUrl(assetPath, fallback = '') {
      if (!assetPath) return fallback
      if (assetPath.startsWith('http://') || assetPath.startsWith('https://')) {
        return assetPath
      }
      if (assetPath.startsWith('../../') || assetPath.startsWith('/static/')) {
        return assetPath
      }
      return getAssetURL(assetPath) || fallback
    },

    async loadCommunityDetail() {
      try {
        const response = await uni.request({
          url: `${COMMUNITY_API_BASE}/${this.communityId}`,
          method: 'GET',
          data: {
            user_id: 1
          }
        });

        if (response.data.code === 200) {
          this.community = response.data.data;
          if (this.community.tags && typeof this.community.tags === 'string') {
            this.community.tags = JSON.parse(this.community.tags);
          }
        }
      } catch (error) {
        console.error('加载社区详情失败:', error);
        uni.showToast({
          title: '加载失败',
          icon: 'none'
        });
      }
    },

    async loadPosts() {
      if (this.loading || !this.hasMore) return;
      
      this.loading = true;
      try {
        const params = {
          user_id: 1,
          page: this.page,
          page_size: 10
        };

        if (this.currentTab > 0) {
          params.category = this.postTabs[this.currentTab].value;
        }

        const response = await uni.request({
          url: `${COMMUNITY_API_BASE}/${this.communityId}/posts`,
          method: 'GET',
          data: params
        });

        if (response.data.code === 200) {
          const newPosts = (response.data.data.posts || []).map(post => ({
            ...post,
            images: Array.isArray(post.images) ? post.images : []
          }));
          if (this.page === 1) {
            this.posts = newPosts;
          } else {
            this.posts = [...this.posts, ...newPosts];
          }
          
          this.hasMore = this.page < response.data.data.total_pages;
          this.page++;
        }
      } catch (error) {
        console.error('加载帖子失败:', error);
      } finally {
        this.loading = false;
      }
    },

    loadMorePosts() {
      this.loadPosts();
    },

    switchTab(index) {
      this.currentTab = index;
      this.page = 1;
      this.hasMore = true;
      this.posts = [];
      this.loadPosts();
    },

    handleJoin() {
      if (this.community.is_joined) {
        uni.showToast({
          title: '您已经是成员',
          icon: 'none'
        });
        return;
      }

      if (this.community.join_type === 'open') {
        this.joinCommunity();
      } else {
        this.showJoinModal = true;
      }
    },

    async joinCommunity() {
      try {
        const response = await uni.request({
          url: `${COMMUNITY_API_BASE}/${this.communityId}/join`,
          method: 'POST',
          data: {
            user_id: 1,
            message: this.joinMessage
          }
        });

        if (response.data.code === 200) {
          if (response.data.data.status === 'approved') {
            this.community.is_joined = true;
            this.community.current_members++;
            uni.showToast({
              title: '加入成功',
              icon: 'success'
            });
          } else {
            uni.showToast({
              title: '申请已提交，等待审核',
              icon: 'none'
            });
          }
          this.showJoinModal = false;
        }
      } catch (error) {
        console.error('加入失败:', error);
        uni.showToast({
          title: '操作失败',
          icon: 'none'
        });
      }
    },

    submitJoin() {
      if (!this.joinMessage.trim()) {
        uni.showToast({
          title: '请填写申请理由',
          icon: 'none'
        });
        return;
      }
      this.joinCommunity();
    },

    async chooseImage() {
      if (this.uploadingImages) return;

      const chooseResult = await new Promise((resolve, reject) => {
        uni.chooseImage({
          count: 9 - this.newPost.images.length,
          sizeType: ['compressed'],
          sourceType: ['album', 'camera'],
          success: resolve,
          fail: reject
        });
      }).catch(() => null);

      if (!chooseResult || !Array.isArray(chooseResult.tempFilePaths) || chooseResult.tempFilePaths.length === 0) {
        return;
      }

      this.uploadingImages = true;
      uni.showLoading({
        title: '图片上传中',
        mask: true
      });

      try {
        const uploadedUrls = [];
        for (const filePath of chooseResult.tempFilePaths) {
          const uploadRes = await uploadFile('/api/community/upload-image', filePath, 'image');
          if (uploadRes?.code !== 200 || !uploadRes?.data?.url) {
            throw new Error('upload failed');
          }
          uploadedUrls.push(uploadRes.data.url);
        }
        this.newPost.images = [...this.newPost.images, ...uploadedUrls];
      } catch (error) {
        console.error('上传帖子图片失败:', error);
        uni.showToast({
          title: '图片上传失败',
          icon: 'none'
        });
      } finally {
        uni.hideLoading();
        this.uploadingImages = false;
      }
    },

    removeImage(index) {
      this.newPost.images.splice(index, 1);
    },

    async submitPost() {
      if (this.uploadingImages) {
        uni.showToast({
          title: '图片上传中，请稍后',
          icon: 'none'
        });
        return;
      }

      if (!this.newPost.content.trim()) {
        uni.showToast({
          title: '请输入内容',
          icon: 'none'
        });
        return;
      }

      try {
        const response = await uni.request({
          url: `${COMMUNITY_API_BASE}/${this.communityId}/posts`,
          method: 'POST',
          data: {
            user_id: 1,
            title: this.newPost.title,
            content: this.newPost.content,
            images: this.newPost.images,
            category: this.newPost.category
          }
        });

        if (response.data.code === 200) {
          uni.showToast({
            title: '发布成功',
            icon: 'success'
          });
          this.showPostModal = false;
          this.newPost = {
            title: '',
            content: '',
            category: 'general',
            images: []
          };
          this.page = 1;
          this.hasMore = true;
          this.posts = [];
          this.loadPosts();
        }
      } catch (error) {
        console.error('发布失败:', error);
        uni.showToast({
          title: '发布失败',
          icon: 'none'
        });
      }
    },

    async likePost(post) {
      try {
        const response = await uni.request({
          url: `${COMMUNITY_API_BASE}/posts/${post.id}/like`,
          method: 'POST',
          data: {
            user_id: 1
          }
        });

        if (response.data.code === 200) {
          post.is_liked = response.data.data.is_liked;
          post.like_count += post.is_liked ? 1 : -1;
        }
      } catch (error) {
        console.error('点赞失败:', error);
      }
    },

    async showComments(post) {
      this.currentPost = post;
      await this.loadComments(post.id);
      this.showCommentModal = true;
    },

    async loadComments(postId) {
      try {
        const response = await uni.request({
          url: `${COMMUNITY_API_BASE}/posts/${postId}/comments`,
          method: 'GET',
          data: {
            user_id: 1
          }
        });

        if (response.data.code === 200) {
          this.comments = response.data.data.comments;
        }
      } catch (error) {
        console.error('加载评论失败:', error);
      }
    },

    async submitComment() {
      if (!this.newComment.trim()) {
        uni.showToast({
          title: '请输入评论',
          icon: 'none'
        });
        return;
      }

      try {
        const response = await uni.request({
          url: `${COMMUNITY_API_BASE}/posts/${this.currentPost.id}/comments`,
          method: 'POST',
          data: {
            user_id: 1,
            content: this.newComment
          }
        });

        if (response.data.code === 200) {
          this.newComment = '';
          this.loadComments(this.currentPost.id);
          this.currentPost.comment_count++;
        }
      } catch (error) {
        console.error('评论失败:', error);
        uni.showToast({
          title: '评论失败',
          icon: 'none'
        });
      }
    },

    async likeComment(comment) {
      try {
        await uni.request({
          url: `${COMMUNITY_API_BASE}/comments/${comment.id}/like`,
          method: 'POST',
          data: {
            user_id: 1
          }
        });
        comment.is_liked = !comment.is_liked;
        comment.like_count += comment.is_liked ? 1 : -1;
      } catch (error) {
        console.error('点赞失败:', error);
      }
    },

    replyComment(comment) {
      this.newComment = `@${comment.author_name} `;
    },

    sharePost(post) {
      uni.showToast({
        title: '分享功能开发中',
        icon: 'none'
      });
    },

    shareCommunity() {
      uni.showToast({
        title: '分享功能开发中',
        icon: 'none'
      });
    },

    previewImage(images, current) {
      uni.previewImage({
        urls: (images || []).map(img => this.normalizeAssetUrl(img)).filter(Boolean),
        current: current
      });
    },

    getRoleName(role) {
      const roleMap = {
        'owner': '创建者',
        'admin': '管理员',
        'moderator': '版主'
      };
      return roleMap[role] || role;
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
.detail-container {
  min-height: 100vh;
  background: #F8FAFC;
  padding-bottom: 120rpx;
}

/* 社区头部 */
.community-header {
  background: white;
  margin-bottom: 24rpx;
}

.header-cover {
  position: relative;
  height: 320rpx;
}

.cover-image {
  width: 100%;
  height: 100%;
}

.cover-gradient {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 120rpx;
  background: linear-gradient(to top, rgba(255,255,255,1) 0%, transparent 100%);
}

.header-content {
  padding: 32rpx;
  position: relative;
  margin-top: -80rpx;
}

.community-basic {
  display: flex;
  align-items: flex-end;
  gap: 20rpx;
  margin-bottom: 24rpx;
}

.community-avatar {
  width: 120rpx;
  height: 120rpx;
  border-radius: 50%;
  border: 4rpx solid white;
  box-shadow: 0 4rpx 16rpx rgba(0,0,0,0.1);
}

.basic-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8rpx;
  padding-bottom: 20rpx;
}

.community-name {
  font-size: 36rpx;
  font-weight: 800;
  color: #0f172a;
}

.community-meta {
  display: flex;
  align-items: center;
  gap: 8rpx;
}

.meta-item {
  font-size: 24rpx;
  color: #64748b;
}

.meta-separator {
  color: #cbd5e1;
}

.community-desc {
  font-size: 28rpx;
  color: #475569;
  line-height: 1.6;
  margin-bottom: 24rpx;
  display: block;
}

/* 社区数据统计 */
.community-stats {
  display: flex;
  gap: 32rpx;
  margin-bottom: 24rpx;
  padding: 24rpx;
  background: #F8FAFC;
  border-radius: 24rpx;
}

.stat-box {
  flex: 1;
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}

.stat-value {
  font-size: 36rpx;
  font-weight: 800;
  color: #0f172a;
}

.stat-label {
  font-size: 24rpx;
  color: #64748b;
}

/* 加入按钮 */
.join-section {
  display: flex;
  gap: 16rpx;
  margin-bottom: 24rpx;
}

.join-btn {
  flex: 1;
  background: linear-gradient(135deg, #10b981, #0ea5e9);
  color: white;
  padding: 24rpx;
  border-radius: 32rpx;
  text-align: center;
  font-size: 30rpx;
  font-weight: 700;
  box-shadow: 0 8rpx 24rpx rgba(16, 185, 129, 0.3);
  transition: all 0.3s;
}

.join-btn.joined {
  background: #94a3b8;
  box-shadow: none;
}

.join-text {
  color: white;
}

.share-btn {
  width: 100rpx;
  background: #F1F5F9;
  border-radius: 32rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36rpx;
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
  font-size: 24rpx;
  font-weight: 500;
}

/* 管理模块*/
.admins-section {
  background: white;
  padding: 24rpx 32rpx;
  margin-bottom: 24rpx;
}

.section-title {
  font-size: 28rpx;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 20rpx;
  display: block;
}

.admins-scroll {
  white-space: nowrap;
}

.admins-list {
  display: flex;
  gap: 24rpx;
}

.admin-item {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  gap: 8rpx;
}

.admin-avatar {
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
}

.admin-name {
  font-size: 24rpx;
  color: #334155;
  font-weight: 600;
}

.admin-role {
  font-size: 20rpx;
  color: #94a3b8;
}

/* Tab选项卡*/
.tabs-section {
  background: white;
  padding: 20rpx 32rpx;
  display: flex;
  gap: 32rpx;
  border-bottom: 2rpx solid #F1F5F9;
}

.tab-item {
  position: relative;
  padding: 16rpx 0;
  transition: all 0.3s;
}

.tab-item.active .tab-text {
  color: #10b981;
  font-weight: 700;
}

.tab-text {
  font-size: 28rpx;
  color: #64748b;
  font-weight: 500;
}

.tab-dot {
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 40rpx;
  height: 6rpx;
  background: #10b981;
  border-radius: 6rpx;
}

/* 帖子列表 */
.posts-scroll {
  height: calc(100vh - 800rpx);
}

.posts-list {
  padding: 24rpx 32rpx;
  display: flex;
  flex-direction: column;
  gap: 24rpx;
}

.post-card {
  background: white;
  border-radius: 32rpx;
  padding: 28rpx;
  box-shadow: 0 4rpx 16rpx rgba(0,0,0,0.06);
}

.post-author {
  display: flex;
  align-items: center;
  gap: 16rpx;
  margin-bottom: 20rpx;
}

.author-avatar {
  width: 72rpx;
  height: 72rpx;
  border-radius: 50%;
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
}

.post-category {
  background: #F1F5F9;
  color: #64748b;
  padding: 6rpx 16rpx;
  border-radius: 16rpx;
  font-size: 22rpx;
  font-weight: 600;
}

.post-content {
  margin-bottom: 20rpx;
}

.post-title {
  font-size: 30rpx;
  font-weight: 700;
  color: #0f172a;
  display: block;
  margin-bottom: 12rpx;
}

.post-text {
  font-size: 28rpx;
  color: #334155;
  line-height: 1.7;
  display: block;
  margin-bottom: 16rpx;
}

.post-images {
  display: flex;
  gap: 12rpx;
  flex-wrap: wrap;
}

.post-image {
  width: 200rpx;
  height: 200rpx;
  border-radius: 16rpx;
}

.more-images {
  width: 200rpx;
  height: 200rpx;
  background: rgba(0,0,0,0.5);
  border-radius: 16rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 32rpx;
  font-weight: 700;
}

.post-actions {
  display: flex;
  gap: 32rpx;
  padding-top: 20rpx;
  border-top: 2rpx solid #F1F5F9;
}

.action-item {
  display: flex;
  align-items: center;
  gap: 10rpx;
}

.action-icon {
  font-size: 32rpx;
}

.action-count {
  font-size: 24rpx;
  color: #64748b;
  font-weight: 600;
}

/* 悬浮按钮 */
.fab-post-btn {
  position: fixed;
  right: 40rpx;
  bottom: 160rpx;
  width: 120rpx;
  height: 120rpx;
  background: linear-gradient(135deg, #10b981, #0ea5e9);
  border-radius: 60rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  box-shadow: 0 12rpx 32rpx rgba(16, 185, 129, 0.4);
  z-index: 998;
}

.fab-icon {
  font-size: 40rpx;
  margin-bottom: 2rpx;
}

.fab-text {
  font-size: 20rpx;
  color: white;
  font-weight: 800;
}

/* 弹窗样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(15, 23, 42, 0.5);
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.post-modal, .join-modal, .comment-modal {
  width: 85%;
  max-width: 640rpx;
  background: white;
  border-radius: 32rpx;
  overflow: hidden;
  box-shadow: 0 16rpx 40rpx rgba(0,0,0,0.2);
}

.comment-modal {
  height: 80vh;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24rpx 32rpx;
  border-bottom: 2rpx solid #F1F5F9;
}

.modal-title {
  font-size: 32rpx;
  font-weight: 700;
  color: #0f172a;
}

.modal-close {
  width: 56rpx;
  height: 56rpx;
  background: #F1F5F9;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28rpx;
  color: #64748b;
}

.modal-body {
  padding: 32rpx;
  max-height: 60vh;
  overflow-y: auto;
}

.post-title-input {
  width: 100%;
  font-size: 30rpx;
  padding: 20rpx;
  border: 2rpx solid #E2E8F0;
  border-radius: 20rpx;
  margin-bottom: 20rpx;
  box-sizing: border-box;
}

.post-content-input {
  width: 100%;
  font-size: 28rpx;
  padding: 20rpx;
  border: 2rpx solid #E2E8F0;
  border-radius: 20rpx;
  min-height: 200rpx;
  box-sizing: border-box;
  line-height: 1.6;
}

.char-count {
  text-align: right;
  font-size: 22rpx;
  color: #94a3b8;
  margin-top: 8rpx;
  display: block;
}

.category-select {
  margin: 24rpx 0;
}

.category-label {
  font-size: 26rpx;
  color: #334155;
  font-weight: 600;
  display: block;
  margin-bottom: 16rpx;
}

.category-options {
  display: flex;
  gap: 12rpx;
  flex-wrap: wrap;
}

.category-option {
  padding: 12rpx 24rpx;
  background: #F1F5F9;
  border-radius: 20rpx;
  font-size: 24rpx;
  color: #64748b;
  transition: all 0.3s;
}

.category-option.selected {
  background: linear-gradient(135deg, #10b981, #0ea5e9);
  color: white;
}

.image-upload {
  margin-top: 24rpx;
}

.upload-btn {
  display: flex;
  align-items: center;
  gap: 12rpx;
  padding: 20rpx 32rpx;
  background: #F1F5F9;
  border-radius: 20rpx;
  width: fit-content;
}

.upload-icon {
  font-size: 32rpx;
}

.upload-text {
  font-size: 26rpx;
  color: #64748b;
}

.image-preview {
  display: flex;
  gap: 12rpx;
  margin-top: 16rpx;
  flex-wrap: wrap;
}

.preview-item {
  position: relative;
  width: 120rpx;
  height: 120rpx;
}

.preview-img {
  width: 100%;
  height: 100%;
  border-radius: 12rpx;
}

.preview-delete {
  position: absolute;
  top: -8rpx;
  right: -8rpx;
  width: 36rpx;
  height: 36rpx;
  background: #ef4444;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 24rpx;
  font-weight: 700;
}

.join-hint {
  font-size: 26rpx;
  color: #334155;
  display: block;
  margin-bottom: 16rpx;
}

.join-message-input {
  width: 100%;
  font-size: 28rpx;
  padding: 20rpx;
  border: 2rpx solid #E2E8F0;
  border-radius: 20rpx;
  min-height: 150rpx;
  box-sizing: border-box;
}

.modal-footer {
  display: flex;
  gap: 16rpx;
  padding: 20rpx 32rpx;
  border-top: 2rpx solid #F1F5F9;
}

.cancel-btn, .submit-btn {
  flex: 1;
  padding: 24rpx;
  border-radius: 24rpx;
  text-align: center;
  font-size: 28rpx;
  font-weight: 600;
}

.cancel-btn {
  background: #F1F5F9;
  color: #64748b;
}

.submit-btn {
  background: linear-gradient(135deg, #10b981, #0ea5e9);
  color: white;
}

/* 评论列表 */
.comments-list {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 24rpx;
}

.comment-item {
  display: flex;
  gap: 16rpx;
}

.comment-avatar {
  width: 64rpx;
  height: 64rpx;
  border-radius: 50%;
}

.comment-content {
  flex: 1;
}

.comment-header {
  display: flex;
  align-items: center;
  gap: 12rpx;
  margin-bottom: 8rpx;
}

.comment-author {
  font-size: 26rpx;
  font-weight: 700;
  color: #0f172a;
}

.comment-time {
  font-size: 22rpx;
  color: #94a3b8;
}

.comment-text {
  font-size: 26rpx;
  color: #334155;
  line-height: 1.6;
  display: block;
  margin-bottom: 12rpx;
}

.comment-actions {
  display: flex;
  gap: 24rpx;
}

.comment-action {
  display: flex;
  align-items: center;
  gap: 6rpx;
  font-size: 24rpx;
  color: #64748b;
}

.comment-input-section {
  display: flex;
  gap: 12rpx;
  padding: 20rpx 0;
  border-top: 2rpx solid #F1F5F9;
}

.comment-input {
  flex: 1;
  padding: 16rpx 20rpx;
  background: #F1F5F9;
  border-radius: 24rpx;
  font-size: 26rpx;
}

.send-btn {
  padding: 16rpx 32rpx;
  background: linear-gradient(135deg, #10b981, #0ea5e9);
  color: white;
  border-radius: 24rpx;
  font-size: 26rpx;
  font-weight: 600;
}

/* 加载和空状态*/
.loading-more, .no-more {
  text-align: center;
  padding: 40rpx 0;
}

.loading-text, .no-more-text {
  font-size: 24rpx;
  color: #94a3b8;
}

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

.empty-action {
  background: linear-gradient(135deg, #10b981, #0ea5e9);
  color: white;
  padding: 20rpx 48rpx;
  border-radius: 40rpx;
  font-size: 28rpx;
  font-weight: 700;
  border: none;
}
</style>
