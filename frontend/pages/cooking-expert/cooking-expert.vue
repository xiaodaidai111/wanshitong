<template>
  <view class="cooking-expert-view">
    <view class="view-header">
      <view class="header-decoration"></view>
      <view class="view-title">AIGC实操案例助手</view>
      <view class="view-subtitle">把抽象知识变成可运行项目</view>
    </view>
    
    <view class="content-container">
      <view class="chef-section">
        <image src="../../static/cookexpret.png" mode="aspectFill" class="profile-avatar"></image>
        <view class="chef-dialogue-box">
          <view class="exp-container" style="margin-top: 0; padding-top: 0; border-top: none;">
            <view class="exp-header">
              <text class="exp-label">🌟 实操经验点(EXP)</text>
              <text class="exp-value">{{ cookingExp }} / {{ expToNextLevel }}</text>
            </view>
            <view class="exp-bar-bg">
              <view class="exp-bar-fill" :style="{ width: expProgress + '%' }"></view>
            </view>
            <text class="exp-level">当前等级: Lv.{{ currentLevel }}</text>
          </view>
        </view>
      </view>
      
      <!-- 聊天界面 -->
      <view class="chat-container">
        <view class="chat-header">
          <view class="chat-header-title">💬 智能对话</view>
          <view class="chat-header-actions">
            <view class="action-btn" @click="clearChat">🗑️</view>
          </view>
        </view>
        <scroll-view class="chat-history" scroll-y="true" :scroll-into-view="scrollTop">
          <view class="chat-message chef" id="msg-welcome">
            <view class="message-avatar">
              <image src="../../static/cookexpret.png" mode="aspectFill" class="avatar-img"></image>
            </view>
            <view class="message-content">
              <view class="message-text">欢迎使用实操案例助手！请输入课程知识点或项目目标，我会为你生成代码案例、步骤说明和练习建议。</view>
            </view>
          </view>
          <view v-for="(msg, index) in chatHistory" :key="index" :class="['chat-message', msg.type === 'user' ? 'user' : 'chef']" :id="'msg-' + index">
            <view v-if="msg.type === 'chef'" class="message-avatar">
              <image src="../../static/cookexpret.png" mode="aspectFill" class="avatar-img"></image>
            </view>
            <view class="message-content">
              <view class="message-text">
                <view v-if="msg.imageUrl" class="message-image-container" @click="previewImage(msg.imageUrl, '对话图片')">
                  <image :src="msg.imageUrl" mode="widthFix" class="message-image"></image>
                </view>
                <text v-if="msg.message" class="message-text-inner">{{ msg.message }}</text>
              </view>
              <view v-if="msg.expChange" class="exp-change-badge">+{{ msg.expChange }} EXP!</view>
            </view>
          </view>
        </scroll-view>
        <view class="chat-input-container">
          <view class="input-wrapper">
            <input type="text" v-model="userMessage" placeholder="输入知识点或实操问题..." class="chat-input" @confirm="sendMessage">
            <view class="input-actions">
              <view class="quick-action camera-icon" @click="chooseImage">
                <text class="camera-fallback">📷</text>
              </view>
              <view class="quick-action voice-action" :class="{ active: isVoiceRecording || isVoiceTranscribing }" @click="toggleVoiceInput">
                <text class="voice-action-text">{{ isVoiceRecording ? '停' : (isVoiceTranscribing ? '识' : '语') }}</text>
              </view>
              <view class="quick-action" @click="insertQuickText('怎么实现?')">💻</view>
              <view class="quick-action" @click="insertQuickText('推荐')">💡</view>
            </view>
          </view>
          <button class="send-btn" @click="sendMessage">
            <view class="send-icon">➤</view>
          </button>
        </view>
      </view>
      
      <!-- 实操案例综合区域 -->
      <view class="recipe-comprehensive-section">
        <view class="section-header">
          <view class="section-icon">📝</view>
          <view class="section-title">生成你的专属实操案例</view>
        </view>
        <view class="recipe-generator-section">
          <view class="form-container">
            <view class="form-group">
              <view class="form-label">核心知识点</view>
              <view class="input-with-icon">
                <view class="input-icon">📘</view>
                <input 
                  type="text" 
                  v-model="ingredient" 
                  placeholder="输入知识点，如：A*搜索算法" 
                  class="ingredient-input"
                >
              </view>
            </view>
            <view class="form-group">
              <view class="form-label">选择案例类型</view>
              <picker @change="onCuisineChange" :value="cuisineIndex" :range="cuisineOptions" class="cuisine-select">
                <view class="picker-wrapper">
                  <view class="picker-icon">💻</view>
                  <view class="picker-text">{{ cuisineOptions[cuisineIndex] || '选择菜系' }}</view>
                  <view class="picker-arrow">›</view>
                </view>
              </picker>
            </view>
            <button @click="generateRecipe" class="generate-btn" :class="{ 'is-loading': recipeGenerating }" :disabled="recipeGenerating">
              <view class="btn-icon">✨</view>
              <view class="btn-text">{{ recipeGenerating ? '正在生成实操案例' : '生成案例' }}</view>
            </button>
          </view>
        </view>
        
        <view class="recipe-result-section" v-if="showRecipe">
          <view class="recipe-header">
            <view class="recipe-icon">🍽️</view>
            <view class="recipe-name">{{ recipeName }}</view>
          </view>
          <view class="recipe-details">
            <view class="recipe-ingredients" v-if="recipeIngredients.length">
              <view class="steps-header">
                <view class="steps-icon">📚</view>
                <view class="steps-heading">前置知识</view>
              </view>
              <view class="ingredients-list">
                <view v-for="(item, index) in recipeIngredients" :key="'ingredient-' + index" class="ingredient-item">
                  <view class="ingredient-dot"></view>
                  <view class="ingredient-text">{{ item }}</view>
                </view>
              </view>
            </view>
            <view class="cooking-steps">
              <view class="steps-header">
                <view class="steps-icon">💻</view>
                <view class="steps-heading">实现步骤</view>
              </view>
              <view class="steps-list">
                <view v-for="(step, index) in recipeSteps" :key="index" class="step-item">
                  <view class="step-number">{{ index + 1 }}</view>
                  <view class="step-content">{{ step }}</view>
                </view>
              </view>
            </view>
            <view class="recipe-health" v-if="recipeNutrition || recipeTips">
              <view class="steps-header">
                <view class="steps-icon">💡</view>
                <view class="steps-heading">学习建议</view>
              </view>
              <view v-if="recipeNutrition" class="health-card">
                <view class="health-label">能力目标</view>
                <view class="health-text">{{ recipeNutrition }}</view>
              </view>
              <view v-if="recipeTips" class="health-card">
                <view class="health-label">防幻觉提示</view>
                <view class="health-text">{{ recipeTips }}</view>
              </view>
            </view>
          </view>
          <view class="recipe-footer">
            <button class="share-btn" @click="shareRecipe">
              <view class="btn-icon">📤</view>
              <view class="btn-text">分享案例</view>
            </button>
            <button class="save-btn" @click="saveRecipe">
              <view class="btn-icon">💾</view>
              <view class="btn-text">保存案例</view>
            </button>
          </view>
        </view>
      </view>
      


      <!-- 底部功能：课程资源推荐 (排行榜模式) -->
      <view class="seasonal-recipes-section">
        <view class="section-header">
          <view class="section-title">实操案例推荐排行榜</view>
          <view class="section-badge-light">TOP PICKS</view>
        </view>
        <view class="recipes-list">
          <view
            v-for="(recipe, index) in getTopRecipes()"
            :key="recipe.id"
            class="recipe-card"
            @click="selectSeasonalRecipe(recipe)"
          >
            <view class="recipe-image-wrap">
              <image
                :src="recipe.image ? '../../static/' + recipe.image : '../../static/food.png'"
                mode="aspectFill"
                class="recipe-image"
                :lazy-load="true"
              ></image>
              <view class="recipe-rank-badge" :class="'rank-' + (index + 1)">
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
                <text class="rating-text">{{ (recipe.avg_rating || 0).toFixed(1) }}⭐</text>
              </view>
              <view class="recipe-desc">{{ recipe.description }}</view>
              <view class="recipe-meta">
                <view class="recipe-difficulty" :class="'difficulty-' + (recipe.difficulty || '中等')">
                  {{ getDifficultyText(recipe.difficulty) }}
                </view>
                <view class="recipe-time">{{ recipe.cooking_time }}分钟</view>
                <view class="recipe-calories">{{ recipe.calories }}卡</view>
              </view>
            </view>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import request, { API_HOST } from '../../utils/request.js';
import { createVoiceInputController } from '../../utils/voice-input.js';

const COOK_AGENT_BASE = `${API_HOST}:5000`;

export default {
  components: {
  },
  data() {
    return {
      ingredient: '',
      cuisineIndex: 0,
      cuisineOptions: ['算法案例', '编程实训', '概念讲解', '项目任务', '错题训练', '拓展阅读', '课堂演示', '考试复盘', '研究入门'],
      showRecipe: false,
      recipeName: '',
      recipeImage: '',
      recipeIngredients: [],
      recipeSteps: [],
      recipeNutrition: '',
      recipeTips: '',
      userMessage: '',
      imagePrompt: '',
      generatedImageUrl: '',
      chatHistory: [],
      scrollTop: '',
      seasonalRecipes: [],
      loading: false,
      recipeGenerating: false,
      isVoiceRecording: false,
      isVoiceTranscribing: false,
      voiceInputController: null,
      cookingExp: 0,
      currentLevel: 1,
      expToNextLevel: 100,
      allRecipes: []
    }
  },
  computed: {
    expProgress() {
      return Math.min(100, (this.cookingExp / this.expToNextLevel) * 100);
    }
  },
  mounted() {
    this.fetchUserExp();
    this.loadLocalRecipes();
    this.initVoiceInput();
  },
  beforeDestroy() {
    if (this.voiceInputController) {
      this.voiceInputController.destroy();
    }
  },
  methods: {
    initVoiceInput() {
      if (this.voiceInputController) return;

      this.voiceInputController = createVoiceInputController({
        service: 'tuantuan',
        onStateChange: ({ isRecording, isTranscribing }) => {
          this.isVoiceRecording = isRecording;
          this.isVoiceTranscribing = isTranscribing;
        },
        onTranscribed: (text) => {
          this.userMessage = this.userMessage.trim() ? `${this.userMessage.trim()} ${text}` : text;
          uni.showToast({ title: '语音已转文字', icon: 'none' });
        },
        onError: (error) => {
          const title = (error?.message || '语音输入失败').slice(0, 20);
          uni.showToast({ title, icon: 'none' });
        }
      });
    },

    sanitizePlainText(text) {
      if (text === null || text === undefined) return '';
      let t = String(text);
      // Remove common markdown artifacts but keep the actual content.
      t = t.replace(/```[\s\S]*?```/g, '');
      t = t.replace(/`([^`]+)`/g, '$1');
      t = t.replace(/\*\*([^*]+)\*\*/g, '$1');
      t = t.replace(/\*([^*]+)\*/g, '$1');
      t = t.replace(/#{1,6}\s+/g, '');
      t = t.replace(/\[([^\]]+)\]\([^)]+\)/g, '$1');
      // Remove remaining markdown symbols.
      t = t.replace(/[*_`#~]/g, '');
      // Normalize empty lines.
      t = t.replace(/\n{3,}/g, '\n\n');
      return t.trim();
    },
    formatAssistantContent(content) {
      if (content === null || content === undefined) return '';
      if (typeof content === 'string') {
        return this.sanitizePlainText(content);
      }
      if (Array.isArray(content)) {
        return content.map(item => this.sanitizePlainText(item)).filter(Boolean).join('\n');
      }
      if (typeof content === 'object') {
        if (content.raw_text) {
          return this.sanitizePlainText(content.raw_text);
        }

        const parts = [];
        if (content.title) {
          parts.push(this.sanitizePlainText(content.title));
        }
        if (content.content) {
          parts.push(this.sanitizePlainText(content.content));
        }
        if (Array.isArray(content.ingredients) && content.ingredients.length) {
          parts.push(`前置知识：\n${content.ingredients.map((item, index) => `${index + 1}. ${this.sanitizePlainText(item)}`).join('\n')}`);
        }
        if (Array.isArray(content.steps) && content.steps.length) {
          parts.push(`实现步骤：\n${content.steps.map((item, index) => `${index + 1}. ${this.sanitizePlainText(item)}`).join('\n')}`);
        }
        if (content.nutrition) {
          parts.push(`能力目标：${this.sanitizePlainText(content.nutrition)}`);
        }
        if (content.tips) {
          parts.push(`防幻觉提示：${this.sanitizePlainText(content.tips)}`);
        }
        if (content.suggestion) {
          parts.push(`建议：${this.sanitizePlainText(content.suggestion)}`);
        }
        if (content.description && !content.content) {
          parts.push(this.sanitizePlainText(content.description));
        }

        const merged = parts.filter(Boolean).join('\n\n').trim();
        return merged || this.sanitizePlainText(JSON.stringify(content));
      }

      return this.sanitizePlainText(String(content));
    },
    normalizeRecipeList(items) {
      if (!Array.isArray(items)) return [];
      return items
        .map(item => this.sanitizePlainText(item))
        .filter(Boolean);
    },
    extractNumberedLines(text) {
      const safeText = this.sanitizePlainText(text);
      if (!safeText) return [];

      return safeText
        .split(/\n+/)
        .map(line => line.trim())
        .filter(line => /^\d+[\.\、\)]\s*/.test(line))
        .map(line => line.replace(/^\d+[\.\、\)]\s*/, '').trim())
        .filter(Boolean);
    },
    applyRecipeResult(recipeContent) {
      if (!recipeContent || typeof recipeContent !== 'object') {
        return false;
      }

      const cuisine = this.cuisineOptions[this.cuisineIndex] || '算法案例';
      const fallbackName = `${this.ingredient || cuisine}智能实操案例`;

      this.recipeName = this.sanitizePlainText(recipeContent.name || fallbackName);
      this.recipeIngredients = this.normalizeRecipeList(recipeContent.ingredients);
      this.recipeSteps = this.normalizeRecipeList(recipeContent.steps);
      if (!this.recipeSteps.length) {
        this.recipeSteps = this.extractNumberedLines(recipeContent.raw_text || '');
      }
      this.recipeNutrition = this.sanitizePlainText(recipeContent.nutrition || '');
      this.recipeTips = this.sanitizePlainText(recipeContent.tips || '');

      const hasVisibleContent = Boolean(
        this.recipeName || this.recipeIngredients.length || this.recipeSteps.length ||
        this.recipeNutrition || this.recipeTips
      );

      if (!hasVisibleContent) {
        return false;
      }

      this.showRecipe = true;
      return true;
    },
    buildRecipeShareContent() {
      const sections = [`【${this.recipeName}】`];

      if (this.recipeIngredients.length) {
        sections.push(`前置知识：\n${this.recipeIngredients.map((item, index) => `${index + 1}. ${item}`).join('\n')}`);
      }
      if (this.recipeSteps.length) {
        sections.push(`实现步骤：\n${this.recipeSteps.map((step, index) => `${index + 1}. ${step}`).join('\n')}`);
      }
      if (this.recipeNutrition) {
        sections.push(`能力目标：${this.recipeNutrition}`);
      }
      if (this.recipeTips) {
        sections.push(`防幻觉提示：${this.recipeTips}`);
      }

      return sections.join('\n\n');
    },
    async loadLocalRecipes() {
      try {
        const recipesData = require('../../static/food/recipes.json');
        this.allRecipes = recipesData.recipes || [];
        this.seasonalRecipes = this.allRecipes.slice(0, 4).map(r => r.name);
      } catch (error) {
        console.error('加载本地菜品数据失败:', error);
      }
    },
    async fetchUserExp() {
      try {
        const userInfo = uni.getStorageSync('userInfo');
        if (userInfo && userInfo.id) {
          // 这里可以调用获取经验值的API
          // MOCK:
          this.cookingExp = userInfo.cookingExp || 0;
          this.updateLevel();
        }
      } catch (e) {
        console.error('获取经验失败', e);
      }
    },
    updateLevel() {
      this.currentLevel = Math.floor(this.cookingExp / 100) + 1;
      this.expToNextLevel = this.currentLevel * 100;
      uni.setStorageSync('userInfo', { ...uni.getStorageSync('userInfo'), cookingExp: this.cookingExp });
    },
    onCuisineChange(e) { this.cuisineIndex = e.detail.value; },
    scrollToBottom() {
      this.$nextTick(() => {
        this.scrollTop = 'msg-' + (this.chatHistory.length - 1);
      });
    },
    clearChat() {
      this.chatHistory = [];
      uni.showToast({ title: '聊天记录已清空', icon: 'success' });
    },
    insertQuickText(text) {
      this.userMessage = text;
    },
    async toggleVoiceInput() {
      this.initVoiceInput();

      try {
        await this.voiceInputController.toggleRecording();
      } catch (error) {
        const title = (error?.message || '语音输入失败').slice(0, 20);
        uni.showToast({ title, icon: 'none' });
      }
    },
    selectSeasonalRecipe(recipe) {
      if (typeof recipe === 'string') {
        this.ingredient = recipe;
      } else {
        this.ingredient = recipe.name;
      }
      this.generateRecipe();
      uni.showToast({ title: `已选择:${typeof recipe === 'string' ? recipe : recipe.name}`, icon: 'none' });
    },
    getRecipeEmoji(name) {
      const emojiMap = {
        '麻婆豆腐': '🌶️',
        '红烧排骨': '🍖',
        '炒娃娃菜': '🥬',
        '菠菜虾仁': '🦐',
        '豆角炒肉': '🫘',
        '辣椒炒肉': '🌶️',
        '青椒炒肉': '🫑'
      };
      return emojiMap[name] || '🍽️';
    },
    getTopRecipes() {
      return this.allRecipes.slice(0, 4);
    },
    getDifficultyText(difficulty) {
      const map = {
        '简单': '简单',
        '中等': '中等',
        '困难': '困难'
      };
      return map[difficulty] || '未知';
    },
    async chooseImage() {
      try {
        const [error, res] = await uni.chooseImage({
          count: 1,
          sizeType: ['compressed'],
          sourceType: ['album', 'camera']
        });
        
        if (error) {
          console.error("选择图片失败:", error);
          return;
        }

        if (res && res.tempFilePaths && res.tempFilePaths.length > 0) {
          const tempFilePath = res.tempFilePaths[0];
          this.uploadAndAnalyzeImage(tempFilePath);
        }
      } catch (err) {
        uni.showToast({ title: '选用图片失败', icon: 'none' });
      }
    },
    async uploadAndAnalyzeImage(filePath) {
      const userMsgIndex = this.chatHistory.length;
      this.chatHistory.push({ type: 'user', message: '📸 [图片]', imageUrl: filePath });
      const pendingIndex = this.chatHistory.length;
      this.chatHistory.push({ type: 'chef', message: '实操智能体正在分析你的资料，请稍候...' });
      this.scrollToBottom();
      this.loading = true;

      try {
        const userInfo = uni.getStorageSync('userInfo') || {};
        const token = uni.getStorageSync('token') || '';
        
        // 我们利用 uploadFile 上传文件，并获取响应
        uni.uploadFile({
          url: `${COOK_AGENT_BASE}/cook-agent/upload`,
          filePath: filePath,
          name: 'file',
          header: {
            'Authorization': token ? `Bearer ${token}` : ''
          },
          success: async (uploadRes) => {
             if(uploadRes.statusCode === 200) {
                const data = JSON.parse(uploadRes.data);
                   if (data.file_url) {
                   // 上传成功：用后端 URL 替换本地临时路径，确保后续可正常回显
                   const absoluteUrl = data.file_url.startsWith('http')
                     ? data.file_url
                     : (COOK_AGENT_BASE + data.file_url);
                   this.$set(this.chatHistory, userMsgIndex, {
                     ...this.chatHistory[userMsgIndex],
                     imageUrl: absoluteUrl
                   });
                   // 图片上传成功，将URL发送给分析接口
                   const response = await request.post('/cook-agent/chat', {
                      message: '请分析这张图片',
                        uploaded_file: data.file_url
                   }, { service: 'tuantuan' });

                   if (response && response.content) {
                      const analysisData = response.content;
                      let replyMsg = `【资料识别】\n`;
                      if (analysisData.objects && analysisData.objects.length) {
                        replyMsg += `发现了：${analysisData.objects.join(', ')}\n\n`;
                      }
                      replyMsg += `${analysisData.suggestion}\n\n${analysisData.description || ''}`;

                      const expChange = analysisData.exp_change || 0;
                      if (expChange > 0) {
                         this.cookingExp += expChange;
                         this.updateLevel();
                      }

                      // Update pending assistant bubble to ensure stable rendering.
                      const safeReply = this.formatAssistantContent(replyMsg);
                      this.$set(this.chatHistory, pendingIndex, {
                        type: 'chef',
                        message: safeReply,
                        expChange: expChange > 0 ? expChange : null
                      });
                   } else {
                     this.$set(this.chatHistory, pendingIndex, {
                       type: 'chef',
                       message: this.sanitizePlainText('智能体没有看清楚资料内容，重新上传一张更清晰的试试吧~')
                     });
                   }
                }
             } else {
                 this.$set(this.chatHistory, pendingIndex, {
                   type: 'chef',
                   message: this.sanitizePlainText('图片上传失败了，请稍后重试')
                 });
             }
             this.loading = false;
             this.scrollToBottom();
          },
          fail: (err) => {
             console.error('上传图片失败:', err);
             this.$set(this.chatHistory, pendingIndex, {
               type: 'chef',
               message: this.sanitizePlainText('网络错误，图片上传失败，请稍后重试')
             });
             this.loading = false;
             this.scrollToBottom();
          }
        });
      } catch (e) {
        uni.showToast({ title: '服务异常', icon: 'none' });
        this.loading = false;
      }
    },
    previewImage(imageSrc, title) {
      if (!imageSrc) return;
      uni.navigateTo({
        url: '/pages/image-viewer/image-viewer?src=' + encodeURIComponent(imageSrc) + '&title=' + encodeURIComponent(title || '图片')
      });
    },
    async sendMessage() {
      if (!this.userMessage.trim()) return;
      
      const userMsg = this.userMessage;
      this.chatHistory.push({ type: 'user', message: userMsg });
      this.userMessage = '';
      this.scrollToBottom();
      
      this.loading = true;
      const pendingIndex = this.chatHistory.length;
      this.chatHistory.push({ type: 'chef', message: '实操案例智能体正在生成回复，请稍候...' });

      try {
        console.log('发送消息到实操案例智能体', userMsg);
        const response = await request.post('/cook-agent/chat', {
          message: userMsg
        }, { service: 'tuantuan' });

        console.log('实操案例智能体响应', response);

        if (response && response.content) {
          // 如果响应包含图像生成，显示图片
          if (response.type === 'image_generation' && response.content && response.content.image_url) {
            this.$set(this.chatHistory, pendingIndex, {
              type: 'chef',
              message: '已为您生成图片',
              imageUrl: response.content.image_url
            });
          } else {
            // 普通文本回复
            this.$set(this.chatHistory, pendingIndex, {
              type: 'chef',
              message: this.formatAssistantContent(response.content)
            });
          }
        } else {
          this.$set(this.chatHistory, pendingIndex, {
            type: 'chef',
            message: this.sanitizePlainText('抱歉，我暂时无法回答这个问题，请稍后再试...')
          });
        }
      } catch (error) {
        console.error('API调用失败:', error);
        console.error('错误详情:', JSON.stringify(error));
        
        let errorMsg = '网络连接失败，请稍后重试...';
        if (error.statusCode === 404) {
          errorMsg = 'API地址错误，请检查后端服务是否启动...';
        } else if (error.statusCode === 500) {
          errorMsg = '服务器内部错误，请稍后重试...';
        } else if (error.errMsg) {
          errorMsg = `请求失败: ${error.errMsg}`;
        }
        
        this.$set(this.chatHistory, pendingIndex, {
          type: 'chef',
          message: this.sanitizePlainText(errorMsg)
        });
      } finally {
        this.loading = false;
        this.scrollToBottom();
      }
    },
    async generateRecipe() {
      if (this.recipeGenerating) {
        return;
      }

      if (!this.ingredient) {
        uni.showToast({ title: '请输入知识点', icon: 'none' });
        return;
      }
      
      this.loading = true;
      this.recipeGenerating = true;
      this.showRecipe = false;
      this.recipeName = '';
      this.recipeIngredients = [];
      this.recipeSteps = [];
      this.recipeNutrition = '';
      this.recipeTips = '';

      try {
        const cuisine = this.cuisineOptions[this.cuisineIndex] || '算法案例';
        console.log('生成实操案例请求:', { ingredient: this.ingredient, cuisine });
        
        const response = await request.post('/cook-agent/chat', {
          action: 'generate_recipe',
          ingredient: this.ingredient,
          cuisine: cuisine,
          message: `请围绕${this.ingredient}生成一个${cuisine}，包含前置知识、实现步骤、代码或伪代码、练习题和防幻觉校验建议`
        }, { service: 'tuantuan' });

        console.log('案例生成响应:', response);

        if (response && response.type === 'recipe' && response.content) {
          const applied = this.applyRecipeResult(response.content);
          if (!applied) {
            uni.showToast({ title: '案例数据不完整，请重试', icon: 'none' });
            return;
          }
          uni.showToast({ title: '案例生成成功！', icon: 'success' });
        } else {
          uni.showToast({ title: '案例生成失败', icon: 'none' });
        }
      } catch (error) {
        console.error('案例生成失败:', error);
        console.error('错误详情:', JSON.stringify(error));
        
        let errorMsg = '网络连接失败';
        if (error.statusCode === 404) {
          errorMsg = 'API地址错误，请检查后端服务是否启动...';
        } else if (error.statusCode === 500) {
          errorMsg = '服务器内部错误，请稍后重试...';
        } else if (error.errMsg) {
          errorMsg = `请求失败: ${error.errMsg}`;
        }
        
        uni.showToast({ title: errorMsg, icon: 'none' });
      } finally {
        this.loading = false;
        this.recipeGenerating = false;
      }
    },
    async generateImage() {
      if (!this.imagePrompt.trim()) {
        uni.showToast({ title: '请输入图片描述', icon: 'none' });
        return;
      }
      
      this.loading = true;

      try {
        console.log('生成图片请求:', this.imagePrompt);
        const response = await request.post('/cook-agent/chat', {
          message: this.imagePrompt
        }, { service: 'tuantuan' });

        console.log('图片生成响应:', response);

        if (response && response.type === 'image_generation' && response.content && response.content.image_url) {
          this.generatedImageUrl = response.content.image_url;
          uni.showToast({ title: '图片生成成功！', icon: 'success' });
        } else {
          uni.showToast({ title: '图片生成失败', icon: 'none' });
        }
      } catch (error) {
        console.error('图片生成失败:', error);
        console.error('错误详情:', JSON.stringify(error));
        
        let errorMsg = '图片生成失败';
        if (error.statusCode === 404) {
          errorMsg = 'API地址错误，请检查后端服务是否启动...';
        } else if (error.statusCode === 500) {
          errorMsg = '服务器内部错误，请稍后重试...';
        } else if (error.errMsg) {
          errorMsg = `请求失败: ${error.errMsg}`;
        }
        
        uni.showToast({ title: errorMsg, icon: 'none' });
      } finally {
        this.loading = false;
      }
    },
    downloadImage() {
      if (!this.generatedImageUrl) {
        uni.showToast({ title: '没有可下载的图片', icon: 'none' });
        return;
      }
      
      uni.downloadFile({
        url: this.generatedImageUrl,
        success: () => {
          uni.showToast({ title: '下载成功', icon: 'success' });
        },
        fail: (error) => {
          console.error('下载失败:', error);
          uni.showToast({ title: '下载失败', icon: 'none' });
        }
      });
    },
    shareRecipe() {
      if (!this.recipeName || !this.recipeSteps.length) {
        uni.showToast({ title: '没有可分享的案例', icon: 'none' });
        return;
      }
      
      const recipeContent = this.buildRecipeShareContent();
      
      uni.share({
        provider: 'weixin',
        scene: 'WXSceneSession',
        type: 1,
        summary: recipeContent,
        success: () => {
          uni.showToast({ title: '分享成功', icon: 'success' });
        },
        fail: (error) => {
          console.error('分享失败:', error);
          uni.showToast({ title: '分享失败，请稍后重试', icon: 'none' });
        }
      });
    },
    saveRecipe() {
      if (!this.recipeName || !this.recipeSteps.length) {
        uni.showToast({ title: '没有可保存的案例', icon: 'none' });
        return;
      }
      
      const recipe = {
        id: Date.now(),
        name: this.recipeName,
        ingredients: this.recipeIngredients,
        steps: this.recipeSteps,
        nutrition: this.recipeNutrition,
        tips: this.recipeTips,
        createdAt: new Date().toISOString()
      };
      
      try {
        const savedRecipes = uni.getStorageSync('savedRecipes') || [];
        savedRecipes.push(recipe);
        uni.setStorageSync('savedRecipes', savedRecipes);
        uni.showToast({ title: '案例保存成功', icon: 'success' });
      } catch (error) {
        console.error('保存失败:', error);
        uni.showToast({ title: '保存失败，请稍后重试', icon: 'none' });
      }
    }
  }
}
</script>

<style scoped>
.cooking-expert-view { 
  min-height: 100vh; 
  background: linear-gradient(135deg, #e8f4ff 0%, #d4e9ff 50%, #c5ddff 100%);
  padding: calc(44px + constant(safe-area-inset-top)) 32rpx 0 32rpx;
  padding: calc(44px + env(safe-area-inset-top)) 32rpx 0 32rpx;
  position: relative;
}

.view-header { 
  padding: 60rpx 0 40rpx; 
  text-align: center;
  position: relative;
  z-index: 1;
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
  gap: 32rpx; 
  margin: 0 auto; 
  padding-bottom: 120rpx;
  position: relative;
  z-index: 1;
}

.chef-section { 
  display: flex; 
  flex-direction: row; 
  align-items: center; 
  padding: 32rpx;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(248, 250, 252, 0.95) 100%);
  box-shadow: 0 8rpx 32rpx rgba(24, 144, 255, 0.15);
  backdrop-filter: blur(20px);
  position: relative;
  overflow: hidden;
}

.chef-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4rpx;
  background: linear-gradient(90deg, #1890ff 0%, #40a9ff 50%, #1890ff 100%);
}

.chef-image-wrapper {
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 24rpx;
}

.profile-avatar {
  width: 140rpx;
  height: 140rpx;
  border-radius: 50%;
  border: 4rpx solid white;
  box-shadow: 0 4rpx 16rpx rgba(24, 144, 255, 0.3);
  margin-right: 24rpx;
  flex-shrink: 0;
}

.avatar-img {
  width: 100%;
  height: 100%;
  border-radius: 50%;
}

.chef-image-container {
  position: relative;
  z-index: 2;
}

.chef-image { 
  width: 200rpx; 
  height: 200rpx; 
  border: 6rpx solid white;
  box-shadow: 0 8rpx 24rpx rgba(24, 144, 255, 0.3);
  animation: pulse 3s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); box-shadow: 0 8rpx 24rpx rgba(24, 144, 255, 0.3); }
  50% { transform: scale(1.02); box-shadow: 0 12rpx 32rpx rgba(24, 144, 255, 0.4); }
}

.chef-badge {
  position: absolute;
  bottom: -8rpx;
  right: -8rpx;
  width: 64rpx;
  height: 64rpx;
  background: linear-gradient(135deg, #1890ff 0%, #40a9ff 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32rpx;
  box-shadow: 0 4rpx 12rpx rgba(24, 144, 255, 0.4);
  border: 4rpx solid white;
}

.chef-decoration {
  position: absolute;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
}

.decoration-circle {
  position: absolute;
  border-radius: 50%;
  background: linear-gradient(135deg, rgba(24, 144, 255, 0.1) 0%, rgba(64, 169, 255, 0.05) 100%);
  animation: rotate 20s linear infinite;
}

.circle-1 {
  width: 280rpx;
  height: 280rpx;
  top: -40rpx;
  left: -40rpx;
}

.circle-2 {
  width: 240rpx;
  height: 240rpx;
  top: -20rpx;
  right: -20rpx;
  animation-delay: -7s;
}

.circle-3 {
  width: 200rpx;
  height: 200rpx;
  bottom: -30rpx;
  left: 50%;
  transform: translateX(-50%);
  animation-delay: -14s;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.chef-dialogue-box { 
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  padding: 28rpx 32rpx;
  border-radius: 20rpx;
  flex: 1;
  border: 2rpx solid rgba(24, 144, 255, 0.1);
  box-shadow: 0 4rpx 12rpx rgba(24, 144, 255, 0.08);
}

.exp-container {
  margin-top: 16rpx;
  padding-top: 16rpx;
  border-top: 1rpx dashed rgba(24, 144, 255, 0.2);
}

.exp-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8rpx;
}

.exp-label {
  font-size: 24rpx;
  font-weight: 600;
  color: #ff9800;
}

.exp-value {
  font-size: 22rpx;
  color: #64748b;
}

.exp-bar-bg {
  height: 12rpx;
  background: #e2e8f0;
  border-radius: 6rpx;
  overflow: hidden;
  margin-bottom: 8rpx;
}

.exp-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #fbbf24 0%, #f59e0b 100%);
  border-radius: 6rpx;
  transition: width 0.5s ease-out;
}

.exp-level {
  font-size: 20rpx;
  color: #94a3b8;
}

.dialogue-header {
  display: flex;
  align-items: center;
  gap: 12rpx;
  margin-bottom: 12rpx;
}

.dialogue-label { 
  font-weight: 700; 
  color: #1890ff; 
  font-size: 28rpx;
}

.dialogue-status {
  width: 16rpx;
  height: 16rpx;
  border-radius: 50%;
  background: #52c41a;
  box-shadow: 0 0 0 4rpx rgba(82, 196, 26, 0.2);
}

.dialogue-status.online {
  animation: status-pulse 2s ease-in-out infinite;
}

@keyframes status-pulse {
  0%, 100% { box-shadow: 0 0 0 4rpx rgba(82, 196, 26, 0.2); }
  50% { box-shadow: 0 0 0 8rpx rgba(82, 196, 26, 0.4); }
}

.dialogue-text { 
  color: #334155; 
  line-height: 1.6; 
  font-size: 26rpx;
}

.chat-container { 
  width: 100%; 
  display: flex; 
  flex-direction: column; 
  background: white; 
  border-radius: 32rpx; 
  overflow: visible; /* 改为 visible 以允许气泡阴影溢出显示*/
  position: relative;
  z-index: 100;
  box-shadow: 0 8rpx 32rpx rgba(24, 144, 255, 0.12);
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24rpx 32rpx;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-bottom: 1rpx solid #e2e8f0;
}

.chat-header-title {
  font-size: 28rpx;
  font-weight: 600;
  color: #334155;
}

.chat-header-actions {
  display: flex;
  gap: 16rpx;
}

.action-btn {
  width: 48rpx;
  height: 48rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28rpx;
  background: white;
  border-radius: 12rpx;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.06);
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn:active {
  transform: scale(0.95);
}

.chat-history { 
  flex: 1; 
  padding: 32rpx 2.5% 32rpx 2.5%;
  min-height: 400rpx;
  max-height: 500rpx;
  overflow-y: auto;
  box-sizing: border-box;
  width: 100%;
}

.chat-message { 
  display: flex;
  margin-bottom: 24rpx;
  animation: slideIn 0.3s ease-out;
  position: relative;
  max-width: 100%;
  overflow: visible;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(20rpx);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.chat-message.user {
  flex-direction: row-reverse;
  justify-content: flex-start;
}

.message-avatar {
  width: 64rpx;
  height: 64rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, #1890ff 0%, #40a9ff 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32rpx;
  flex-shrink: 0;
  border: 4rpx solid #fff;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.1);
}

.chat-message.chef .message-avatar {
  margin-right: 20rpx;
}

.chat-message.user .message-avatar {
  margin-left: 20rpx;
}

.message-content {
  max-width: 75%;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.chat-message.user .message-content {
  align-items: flex-end;
  max-width: 80%;
  margin-right: 1.5%;
}

.message-text { 
  padding: 20rpx 24rpx; 
  border-radius: 20rpx; 
  font-size: 26rpx; 
  line-height: 1.6; 
  word-wrap: break-word; 
  word-break: break-word;
  white-space: pre-wrap;
  overflow-wrap: break-word;
  box-shadow: 0 6rpx 16rpx rgba(0, 0, 0, 0.08);
  position: relative;
  z-index: 10;
  box-sizing: border-box;
  max-width: 100%;
}

.message-text-inner{
  display: block;
}

.exp-change-badge {
  display: inline-block;
  margin-top: 8rpx;
  padding: 4rpx 16rpx;
  background: rgba(245, 158, 11, 0.1);
  color: #d97706;
  font-size: 22rpx;
  font-weight: 600;
  border-radius: 20rpx;
  border: 1rpx solid rgba(245, 158, 11, 0.3);
  animation: bounceIn 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  align-self: flex-start;
}

.chat-message.user .exp-change-badge {
  align-self: flex-end;
}

@keyframes bounceIn {
  0% { transform: scale(0.5); opacity: 0; }
  100% { transform: scale(1); opacity: 1; }
}

.message-image-container {
  margin-bottom: 12rpx;
  width: 100%;
}

.message-image {
  width: 100%;
  max-width: 600rpx;
  height: auto;
  border-radius: 12rpx;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.08);
  display: block;
}

.chat-message.user .message-text {
  background: linear-gradient(135deg, #1890ff 0%, #40a9ff 100%);
  color: white;
  border-radius: 24rpx 24rpx 0 24rpx;
  box-shadow: 0 4rpx 16rpx rgba(24, 144, 255, 0.25);
  border: 1rpx solid rgba(255,255,255,0.1);
  box-sizing: border-box;
  max-width: 100%;
}

.chat-message.chef .message-text {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  color: #1e293b;
  border-radius: 24rpx 24rpx 24rpx 0;
  box-shadow: 0 4rpx 16rpx rgba(24, 144, 255, 0.08);
  border: 1rpx solid rgba(24, 144, 255, 0.1);
}

.chat-input-container { 
  display: flex; 
  padding: 24rpx 2.5%;
  background: white;
  border-top: 1rpx solid #f1f5f9;
  gap: 16rpx;
  box-sizing: border-box;
  width: 100%;
}

.input-wrapper {
  flex: 1;
  display: flex;
  align-items: center;
  background: #f8fafc;
  border-radius: 48rpx;
  padding: 8rpx 8rpx 8rpx 24rpx;
  border: 2rpx solid #e2e8f0;
  transition: all 0.2s;
}

.input-wrapper:focus-within {
  border-color: #1890ff;
  box-shadow: 0 0 0 4rpx rgba(24, 144, 255, 0.1);
  background: white;
}

.chat-input { 
  flex: 1;
  height: 64rpx;
  font-size: 26rpx;
  color: #334155;
  background: transparent;
  border: none;
  outline: none;
}

.chat-input::placeholder {
  color: #94a3b8;
}

.input-actions {
  display: flex;
  gap: 8rpx;
  margin-right: 12rpx;
}

.quick-action {
  width: 48rpx;
  height: 48rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28rpx;
  background: white;
  border-radius: 50%;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.06);
  cursor: pointer;
  transition: all 0.2s;
}

.quick-action:active {
  transform: scale(0.9);
}

.camera-icon {
  color: #1890ff;
}

.voice-action {
  min-width: 48rpx;
  background: #eff6ff;
  color: #2563eb;
}

.voice-action.active {
  background: #2563eb;
}

.voice-action-text {
  font-size: 22rpx;
  font-weight: 700;
  color: inherit;
}

.voice-action.active .voice-action-text {
  color: white;
}

.camera-svg {
  width: 28rpx;
  height: 28rpx;
}

.camera-fallback {
  font-size: 28rpx;
  color: #ffffff;
  font-weight: 700;
  line-height: 1;
}

.send-btn { 
  width: 80rpx;
  height: 80rpx;
  background: linear-gradient(135deg, #1890ff 0%, #40a9ff 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4rpx 16rpx rgba(24, 144, 255, 0.3);
  border: none;
  transition: all 0.2s;
}

.send-btn:active {
  transform: scale(0.95);
}

.send-icon {
  font-size: 32rpx;
  color: white;
  margin-left: 4rpx;
}

.recipe-comprehensive-section { 
  background: white; 
  border-radius: 32rpx;
  box-shadow: 0 8rpx 32rpx rgba(24, 144, 255, 0.12);
  overflow: hidden;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 16rpx;
  padding: 32rpx;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-bottom: 1rpx solid #e2e8f0;
}

.section-icon {
  font-size: 36rpx;
  width: 64rpx;
  height: 64rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%);
  border-radius: 16rpx;
}

.section-title {
  font-size: 32rpx;
  font-weight: 700;
  color: #1e293b;
  flex: 1;
}

.section-badge {
  padding: 8rpx 16rpx;
  background: linear-gradient(135deg, #ef4444 0%, #f87171 100%);
  color: white;
  font-size: 20rpx;
  font-weight: 600;
  letter-spacing: 1rpx;
}

.recipe-generator-section { 
  padding: 32rpx;
}

.form-container { 
  display: flex; 
  flex-direction: column; 
  gap: 24rpx;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

.form-label {
  font-size: 24rpx;
  font-weight: 600;
  color: #64748b;
  margin-left: 4rpx;
}

.input-with-icon {
  display: flex;
  align-items: center;
  background: #f8fafc;
  border-radius: 16rpx;
  padding: 8rpx 16rpx;
  border: 2rpx solid #e2e8f0;
  transition: all 0.2s;
}

.input-with-icon:focus-within {
  border-color: #1890ff;
  box-shadow: 0 0 0 4rpx rgba(24, 144, 255, 0.1);
  background: white;
}

.input-icon {
  font-size: 28rpx;
  margin-right: 12rpx;
}

.ingredient-input {
  flex: 1;
  height: 72rpx;
  font-size: 26rpx;
  color: #334155;
  background: transparent;
  border: none;
  outline: none;
}

.ingredient-input::placeholder {
  color: #94a3b8;
}

.cuisine-select {
  width: 100%;
}

.picker-wrapper {
  display: flex;
  align-items: center;
  background: #f8fafc;
  border-radius: 16rpx;
  padding: 16rpx 20rpx;
  border: 2rpx solid #e2e8f0;
  transition: all 0.2s;
}

.picker-wrapper:active {
  border-color: #1890ff;
  background: white;
}

.picker-icon {
  font-size: 28rpx;
  margin-right: 12rpx;
}

.picker-text {
  flex: 1;
  font-size: 26rpx;
  color: #334155;
}

.picker-arrow {
  font-size: 20rpx;
  color: #94a3b8;
}

.generate-btn {
  height: 88rpx;
  background: linear-gradient(135deg, #1890ff 0%, #40a9ff 100%);
  color: white;
  font-size: 30rpx;
  font-weight: 700;
  margin-top: 16rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12rpx;
  box-shadow: 0 8rpx 24rpx rgba(24, 144, 255, 0.3);
  border: none;
  transition: all 0.3s;
}

.generate-btn:active {
  transform: scale(0.98);
  box-shadow: 0 4rpx 12rpx rgba(24, 144, 255, 0.3);
}

.generate-btn.is-loading,
.generate-btn[disabled] {
  opacity: 0.88;
  box-shadow: 0 4rpx 12rpx rgba(24, 144, 255, 0.18);
}

.btn-icon {
  font-size: 32rpx;
}

.btn-text {
  font-size: 30rpx;
}

.recipe-result-section { 
  padding: 32rpx;
  border-top: 1rpx solid #f1f5f9;
}

.recipe-header {
  display: flex;
  align-items: center;
  gap: 16rpx;
  margin-bottom: 24rpx;
}

.recipe-icon {
  font-size: 40rpx;
  width: 72rpx;
  height: 72rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  border-radius: 16rpx;
}

.recipe-name { 
  font-size: 36rpx; 
  color: #1e293b; 
  font-weight: 800;
  flex: 1;
}

.recipe-details {
  display: flex;
  flex-direction: column;
  gap: 24rpx;
}

.recipe-ingredients,
.recipe-health,
.cooking-steps {
  background: #f8fafc;
  border-radius: 20rpx;
  padding: 24rpx;
}

.ingredients-list {
  display: flex;
  flex-direction: column;
  gap: 14rpx;
}

.ingredient-item {
  display: flex;
  align-items: flex-start;
  gap: 12rpx;
}

.ingredient-dot {
  width: 14rpx;
  height: 14rpx;
  border-radius: 50%;
  background: #1890ff;
  margin-top: 12rpx;
  flex-shrink: 0;
}

.ingredient-text {
  flex: 1;
  font-size: 26rpx;
  color: #475569;
  line-height: 1.6;
}

.health-card {
  background: white;
  border-radius: 16rpx;
  padding: 20rpx;
  box-shadow: 0 2rpx 8rpx rgba(24, 144, 255, 0.06);
}

.health-card + .health-card {
  margin-top: 16rpx;
}

.health-label {
  font-size: 24rpx;
  font-weight: 700;
  color: #1890ff;
  margin-bottom: 8rpx;
}

.health-text {
  font-size: 26rpx;
  color: #475569;
  line-height: 1.6;
  white-space: pre-wrap;
}

.dish-image-container {
  position: relative;
  width: 100%;
  overflow: hidden;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.08);
}

.dish-image { 
  width: 100%; 
  height: 360rpx;
  background: #f1f5f9;
}

.image-overlay {
  position: absolute;
  top: 16rpx;
  right: 16rpx;
}

.overlay-tag {
  padding: 8rpx 16rpx;
  background: linear-gradient(135deg, rgba(24, 144, 255, 0.95) 0%, rgba(64, 169, 255, 0.95) 100%);
  color: white;
  font-size: 20rpx;
  font-weight: 600;
  backdrop-filter: blur(10px);
  box-shadow: 0 4rpx 12rpx rgba(24, 144, 255, 0.3);
}

.steps-header {
  display: flex;
  align-items: center;
  gap: 12rpx;
  margin-bottom: 20rpx;
}

.steps-icon {
  font-size: 32rpx;
}

.steps-heading { 
  font-size: 28rpx; 
  font-weight: 700;
  color: #334155;
}

.steps-list {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.step-item {
  display: flex;
  gap: 16rpx;
  align-items: flex-start;
}

.step-number {
  width: 40rpx;
  height: 40rpx;
  background: linear-gradient(135deg, #1890ff 0%, #40a9ff 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22rpx;
  font-weight: 700;
  flex-shrink: 0;
  margin-top: 2rpx;
}

.step-content {
  flex: 1;
  font-size: 26rpx;
  color: #475569;
  line-height: 1.6;
}

.recipe-footer {
  display: flex;
  gap: 16rpx;
  margin-top: 32rpx;
  padding-top: 24rpx;
  border-top: 1rpx solid #f1f5f9;
}

.share-btn {
  flex: 1;
  height: 80rpx;
  background: linear-gradient(135deg, #10b981 0%, #34d399 100%);
  color: white;
  font-size: 28rpx;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12rpx;
  box-shadow: 0 4rpx 16rpx rgba(16, 185, 129, 0.3);
  border: none;
  border-radius: 16rpx;
  transition: all 0.3s;
}

.share-btn:active {
  transform: scale(0.98);
  box-shadow: 0 2rpx 8rpx rgba(16, 185, 129, 0.3);
}

.save-btn {
  flex: 1;
  height: 80rpx;
  background: linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%);
  color: white;
  font-size: 28rpx;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12rpx;
  box-shadow: 0 4rpx 16rpx rgba(245, 158, 11, 0.3);
  border: none;
  border-radius: 16rpx;
  transition: all 0.3s;
}

.save-btn:active {
  transform: scale(0.98);
  box-shadow: 0 2rpx 8rpx rgba(245, 158, 11, 0.3);
}

.seasonal-recipes-section { 
  background: white; 
  border-radius: 32rpx;
  padding: 32rpx;
  box-shadow: 0 8rpx 32rpx rgba(24, 144, 255, 0.12);
}

.section-badge-light {
  padding: 6rpx 16rpx;
  background: #f1f5f9;
  color: #64748b;
  font-size: 20rpx;
  font-weight: 700;
  border-radius: 8rpx;
  letter-spacing: 1rpx;
}

.ranking-list {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.ranking-item {
  display: flex;
  align-items: center;
  padding: 24rpx;
  background: #f8fafc;
  border-radius: 20rpx;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.04);
}

.ranking-item:active {
  background: #f1f5f9;
  transform: scale(0.98);
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.08);
}

.ranking-item:hover {
  transform: translateY(-2rpx);
  box-shadow: 0 4rpx 16rpx rgba(24, 144, 255, 0.1);
}

.ranking-image {
  width: 100rpx;
  height: 100rpx;
  border-radius: 16rpx;
  margin-right: 20rpx;
  flex-shrink: 0;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.08);
  object-fit: cover;
}

.ranking-num {
  width: 50rpx;
  height: 50rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28rpx;
  font-weight: 800;
  color: #94a3b8;
  margin-right: 24rpx;
  background: #fff;
  border-radius: 12rpx;
}

.ranking-num.top-1 {
  background: linear-gradient(135deg, #ffd700 0%, #ffae00 100%);
  color: white;
  box-shadow: 0 4rpx 12rpx rgba(255, 174, 0, 0.3);
}

.ranking-num.top-2 {
  background: linear-gradient(135deg, #c0c0c0 0%, #a0a0a0 100%);
  color: white;
  box-shadow: 0 4rpx 12rpx rgba(160, 160, 160, 0.3);
}

.ranking-num.top-3 {
  background: linear-gradient(135deg, #cd7f32 0%, #b87333 100%);
  color: white;
  box-shadow: 0 4rpx 12rpx rgba(184, 115, 51, 0.3);
}

.ranking-info {
  flex: 1;
}

.ranking-name {
  font-size: 28rpx;
  color: #334155;
  font-weight: 700;
  margin-bottom: 8rpx;
  display: block;
}

.ranking-desc {
  font-size: 22rpx;
  color: #64748b;
  line-height: 1.4;
  margin-bottom: 8rpx;
  display: block;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  overflow: hidden;
  text-overflow: ellipsis;
}

.ranking-meta {
  display: flex;
  gap: 16rpx;
  margin-bottom: 8rpx;
}

.meta-text {
  font-size: 20rpx;
  color: #94a3b8;
  font-weight: 500;
}

.ranking-status-bar {
  height: 6rpx;
  background: #e2e8f0;
  border-radius: 3rpx;
  width: 200rpx;
  overflow: hidden;
}

.status-fill {
  height: 100%;
  background: linear-gradient(90deg, #1890ff 0%, #40a9ff 100%);
  border-radius: 3rpx;
}

.ranking-arrow {
  margin-left: 24rpx;
  font-size: 22rpx;
  color: #1890ff;
  font-weight: 600;
  background: rgba(24, 144, 255, 0.1);
  padding: 6rpx 16rpx;
  border-radius: 20rpx;
}

/* 家常菜推荐榜样式 */
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

.recipe-difficulty.difficulty-简单 {
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

/* 响应式设置*/
@media screen and (max-width: 375px) {
  .chat-message {
    margin-bottom: 20rpx;
  }
  
  .message-content {
    max-width: 70%;
  }
  
  .chat-message.user .message-content {
    max-width: 75%;
  }
  
  .message-text {
    font-size: 24rpx;
    padding: 18rpx 22rpx;
  }
  
  .message-avatar {
    width: 56rpx;
    height: 56rpx;
  }
}

@media screen and (min-width: 376px) and (max-width: 414px) {
  .chat-message {
    margin-bottom: 24rpx;
  }
  
  .message-content {
    max-width: 72%;
  }
  
  .chat-message.user .message-content {
    max-width: 78%;
  }
}

@media screen and (min-width: 415px) {
  .chat-message {
    margin-bottom: 28rpx;
  }
  
  .message-content {
    max-width: 75%;
  }
  
  .chat-message.user .message-content {
    max-width: 80%;
  }
}

@media screen and (orientation: landscape) {
  .chat-history {
    max-height: 400rpx;
  }
  
  .chat-message {
    margin-bottom: 20rpx;
  }
  
  .message-text {
    font-size: 24rpx;
    padding: 16rpx 20rpx;
  }
}
</style>
