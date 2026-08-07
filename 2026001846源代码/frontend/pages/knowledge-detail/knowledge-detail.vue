<template>
  <view class="kd-container">
    <!-- 顶部导航 -->
    <view class="kd-header" :style="{ paddingTop: (statusBarHeight + 10) + 'px' }">
      <view class="header-back" @click="goBack"><text class="back-arrow">←</text></view>
      <text class="header-title">知识详情</text>
      <view class="header-actions">
        <text v-if="!isEditing" class="header-btn" @click="startEdit">✏️ 编辑</text>
        <text v-else class="header-btn preview-btn" @click="exitEdit">👁 预览</text>
        <text v-if="!isEditing" class="header-btn fav-btn" @click="toggleFav">{{ isFav ? '★' : '☆' }}</text>
      </view>
    </view>

    <!-- 编辑模式工具栏 -->
    <view v-if="isEditing" class="edit-toolbar">
      <view class="toolbar-left">
        <text class="save-status" :class="saveStatusClass">{{ saveStatusText }}</text>
      </view>
      <view class="toolbar-right">
        <text class="tool-btn" @click="insertFormat('heading')">H</text>
        <text class="tool-btn" @click="insertFormat('bold')">B</text>
        <text class="tool-btn" @click="insertFormat('list')">📋</text>
        <text class="tool-btn" @click="insertFormat('todo')">☑</text>
        <text class="tool-btn" @click="insertFormat('table')">📊</text>
        <text class="tool-btn" @click="saveNow">💾</text>
        <text class="tool-btn" @click="showVersions = true">📜</text>
        <text class="tool-btn" @click="showLinks = true">🔗</text>
      </view>
    </view>

    <scroll-view scroll-y class="kd-scroll" :class="{ 'edit-scroll': isEditing }">
      <!-- 标题区 -->
      <view class="title-section">
        <view class="title-top-row">
          <view class="title-cat" :class="'cat-' + (item.category || '通用')">{{ item.category || '知识条目' }}</view>
          <view v-if="item.status" class="title-status" :class="'status-' + item.status">
            {{ item.status === 'approved' ? '✅ 已审核' : item.status === 'pending' ? '⏳ 待审核' : '✏️ 已修正' }}
          </view>
          <view v-if="item.version" class="title-version">v{{ item.version }}</view>
        </view>
        <textarea v-if="isEditing" class="title-input" v-model="editTitle" placeholder="输入标题" auto-height />
        <text v-else class="title-text">{{ item.icon ? item.icon + ' ' : '' }}{{ item.title }}</text>
        <view class="title-meta">
          <text class="meta">📖 {{ item.source || '技术资料库' }}</text>
          <text class="meta">🕐 {{ item.updated_at || item.created_at || '未知时间' }}</text>
        </view>
      </view>

      <!-- 基本信息 -->
      <view class="info-card">
        <view v-if="isEditing" class="info-row edit-row">
          <text class="info-label">标题</text>
          <input class="info-input" v-model="editTitle" placeholder="知识标题" />
        </view>
        <view v-else class="info-row">
          <text class="info-label">适用设备</text>
          <text class="info-value">{{ item.equipment_category || item.equipment || '通用' }} {{ item.equipment_model || item.model || '' }}</text>
        </view>
        <view v-if="isEditing" class="info-row edit-row">
          <text class="info-label">设备类型</text>
          <input class="info-input" v-model="editEquipment" placeholder="设备类型" />
        </view>
        <view v-if="isEditing" class="info-row edit-row">
          <text class="info-label">设备型号</text>
          <input class="info-input" v-model="editModel" placeholder="设备型号" />
        </view>
        <view v-if="!isEditing" class="info-row">
          <text class="info-label">故障类型</text>
          <text class="info-value">{{ item.fault_type || item.type || '通用' }}</text>
        </view>
        <view v-if="!isEditing" class="info-row">
          <text class="info-label">引用来源</text>
          <text class="info-value">{{ item.source || '技术资料库' }}</text>
        </view>
        <view v-if="isEditing" class="info-row edit-row">
          <text class="info-label">标签</text>
          <input class="info-input" v-model="editTagsStr" placeholder="用逗号分隔标签" />
        </view>
        <view v-if="!isEditing" class="info-row">
          <text class="info-label">浏览/引用</text>
          <text class="info-value">👁 {{ item.view_count || 0 }} · 📎 {{ item.use_count || 0 }}</text>
        </view>
      </view>

      <!-- 处理方法 / 编辑器 -->
      <view class="content-card">
        <view class="card-header">
          <text class="card-icon">📝</text>
          <text class="card-title">{{ isEditing ? '编辑内容' : '处理方法' }}</text>
          <text v-if="isEditing" class="card-hint">支持 Markdown 格式</text>
        </view>
        <textarea
          v-if="isEditing"
          class="content-editor"
          v-model="editContent"
          placeholder="输入技术资料内容，支持 Markdown 格式（## 标题、**加粗**、- 列表、- [ ] 待办）"
          auto-height
          :maxlength="-1"
          @input="onContentInput"
        />
        <text v-else class="content-text">{{ item.content || '暂无内容' }}</text>
      </view>

      <!-- 标签 -->
      <view v-if="!isEditing && parsedTags.length" class="tags-card">
        <text class="card-title-small">相关标签</text>
        <view class="tags-row">
          <view class="tag-item" v-for="(tag, i) in parsedTags" :key="i">{{ tag }}</view>
        </view>
      </view>

      <!-- 关联任务（联动） -->
      <view v-if="!isEditing" class="related-card">
        <view class="card-header">
          <text class="card-icon">🔗</text>
          <text class="card-title">关联任务</text>
          <text v-if="links.length" class="card-link" @click="showLinks = true">管理</text>
        </view>
        <view class="related-list">
          <view v-if="taskLinks.length === 0 && relatedTasks.length === 0" class="empty-hint">
            <text class="empty-text">暂无关联任务</text>
            <text class="empty-action" @click="showLinks = true">+ 添加关联</text>
          </view>
          <view class="related-item" v-for="(r, i) in displayTasks" :key="i" @click="goTask(r.target_id || r.id)">
            <text class="related-title">{{ r.target_title || r.title }}</text>
            <view class="related-status" :style="{ background: getStatusBg(r.status), color: getStatusColor(r.status) }">
              {{ getStatusText(r.status) }}
            </view>
          </view>
        </view>
      </view>

      <!-- 引用知识（联动） -->
      <view v-if="!isEditing && knowledgeLinks.length" class="related-card">
        <view class="card-header">
          <text class="card-icon">📚</text>
          <text class="card-title">引用知识</text>
        </view>
        <view class="related-list">
          <view class="related-item" v-for="(r, i) in knowledgeLinks" :key="i" @click="goKnowledge(r.target_id)">
            <text class="related-title">📖 {{ r.target_title }}</text>
            <text class="related-arrow">→</text>
          </view>
        </view>
      </view>

      <!-- 操作按钮 -->
      <view v-if="!isEditing" class="action-bar">
        <view class="action-btn primary" @click="startEdit">✏️ 编辑内容</view>
        <view class="action-btn" @click="showVersions = true">📜 版本历史</view>
        <view class="action-btn" @click="showLinks = true">🔗 板块联动</view>
      </view>

      <view v-if="isEditing" class="action-bar">
        <view class="action-btn primary" @click="saveNow">💾 保存</view>
        <view class="action-btn" @click="submitForReview">📤 提交审核</view>
        <view class="action-btn danger" @click="exitEdit">取消</view>
      </view>

      <view style="height: 80rpx;"></view>
    </scroll-view>

    <!-- 版本历史弹窗 -->
    <view v-if="showVersions" class="popup-mask" @click="showVersions = false">
      <view class="popup-sheet" @click.stop>
        <view class="popup-header">
          <text class="popup-title">📜 版本历史</text>
          <text class="popup-close" @click="showVersions = false">✕</text>
        </view>
        <scroll-view scroll-y class="popup-body">
          <view v-if="versions.length === 0" class="empty-hint">
            <text class="empty-text">暂无版本记录</text>
          </view>
          <view
            v-for="ver in versions"
            :key="ver.id"
            class="version-item"
            :class="{ active: ver.version === item.version }"
          >
            <view class="version-main">
              <text class="version-num">v{{ ver.version }}</text>
              <text class="version-editor">{{ ver.editor_name || '系统' }}</text>
              <text class="version-time">{{ ver.created_at }}</text>
            </view>
            <text v-if="ver.change_summary" class="version-summary">{{ ver.change_summary }}</text>
            <view class="version-actions">
              <text class="version-btn" @click="viewVersion(ver)">👁 查看</text>
              <text class="version-btn restore" @click="restoreVersion(ver)">↩️ 恢复</text>
            </view>
          </view>
        </scroll-view>
      </view>
    </view>

    <!-- 版本内容查看弹窗 -->
    <view v-if="showVersionContent" class="popup-mask" @click="showVersionContent = false">
      <view class="popup-sheet large" @click.stop>
        <view class="popup-header">
          <text class="popup-title">📖 v{{ viewingVersion?.version }} 内容</text>
          <text class="popup-close" @click="showVersionContent = false">✕</text>
        </view>
        <scroll-view scroll-y class="popup-body">
          <text class="version-content-text">{{ viewingVersion?.content_snapshot || '无内容' }}</text>
        </scroll-view>
      </view>
    </view>

    <!-- 板块联动弹窗 -->
    <view v-if="showLinks" class="popup-mask" @click="showLinks = false">
      <view class="popup-sheet large" @click.stop>
        <view class="popup-header">
          <text class="popup-title">🔗 板块联动</text>
          <text class="popup-close" @click="showLinks = false">✕</text>
        </view>
        <scroll-view scroll-y class="popup-body">
          <!-- 关联任务 -->
          <view class="link-section">
            <text class="link-section-title">📋 关联检修任务</text>
            <view v-if="taskLinks.length === 0" class="empty-hint">
              <text class="empty-text">暂无关联任务</text>
            </view>
            <view v-for="link in taskLinks" :key="link.id" class="link-item">
              <text class="link-title">{{ link.target_title }}</text>
              <text class="link-remove" @click="removeLink(link)">✕</text>
            </view>
            <view class="link-add-row">
              <input class="link-input" v-model="newTaskId" placeholder="输入任务ID" />
              <input class="link-input" v-model="newTaskTitle" placeholder="任务标题" />
              <view class="link-add-btn" @click="addTaskLink">+ 关联</view>
            </view>
            <view v-if="availableTasks.length" class="link-suggest">
              <text class="suggest-label">可选任务：</text>
              <view class="suggest-list">
                <text
                  v-for="t in availableTasks.slice(0, 5)"
                  :key="t.id"
                  class="suggest-item"
                  @click="quickAddTask(t)"
                >{{ t.title?.slice(0, 20) || t.id }}</text>
              </view>
            </view>
          </view>

          <!-- 引用知识 -->
          <view class="link-section">
            <text class="link-section-title">📚 引用知识条目</text>
            <view v-if="knowledgeLinks.length === 0" class="empty-hint">
              <text class="empty-text">暂无引用</text>
            </view>
            <view v-for="link in knowledgeLinks" :key="link.id" class="link-item">
              <text class="link-title">📖 {{ link.target_title }}</text>
              <text class="link-remove" @click="removeLink(link)">✕</text>
            </view>
            <view class="link-add-row">
              <input class="link-input" v-model="newKnowledgeId" placeholder="知识ID" />
              <input class="link-input" v-model="newKnowledgeTitle" placeholder="知识标题" />
              <view class="link-add-btn" @click="addKnowledgeLink">+ 引用</view>
            </view>
          </view>

          <!-- AI 辅助 -->
          <view class="link-section">
            <text class="link-section-title">🤖 AI 辅助（和鸣）</text>
            <view class="ai-actions">
              <view class="ai-btn" @click="aiAssist('sop')">📋 从任务SOP生成骨架</view>
              <view class="ai-btn" @click="aiAssist('safety')">🔍 检查安全遗漏</view>
              <view class="ai-btn" @click="aiAssist('format')">✨ 规范化术语</view>
            </view>
            <view v-if="aiResult" class="ai-result">
              <text class="ai-result-text">{{ aiResult }}</text>
              <view v-if="aiResult && isEditing" class="ai-adopt-btn" @click="adoptAIResult">采纳</view>
            </view>
          </view>

          <!-- 提交审核 -->
          <view class="link-section">
            <text class="link-section-title">📤 沉淀为知识条目</text>
            <text class="link-desc">将编辑后的内容提交到知识审核队列，审核通过后成为新的知识条目。</text>
            <view class="ai-btn full" @click="submitForReview">📤 提交到知识审核队列</view>
          </view>
        </scroll-view>
      </view>
    </view>
  </view>
</template>

<script>
import request from '../../utils/request.js'

export default {
  data() {
    return {
      statusBarHeight: 0,
      itemId: 0,
      item: {},
      isFav: false,
      isEditing: false,
      editTitle: '',
      editContent: '',
      editEquipment: '',
      editModel: '',
      editTagsStr: '',
      saveStatusText: '',
      saveStatusClass: '',
      autoSaveTimer: null,
      versions: [],
      links: [],
      availableTasks: [],
      relatedTasks: [
        { id: 1, title: 'ZK-320配电柜过热检修', status: 'pending' },
        { id: 2, title: 'CG-125发动机异响排查', status: 'in_progress' },
      ],
      showVersions: false,
      showVersionContent: false,
      viewingVersion: null,
      showLinks: false,
      newTaskId: '',
      newTaskTitle: '',
      newKnowledgeId: '',
      newKnowledgeTitle: '',
      aiResult: '',
      presenceTimer: null,
    }
  },
  computed: {
    parsedTags() {
      if (!this.item.tags) return []
      try {
        return Array.isArray(this.item.tags) ? this.item.tags : JSON.parse(this.item.tags)
      } catch { return [] }
    },
    taskLinks() {
      return this.links.filter(l => l.link_type === 'task')
    },
    knowledgeLinks() {
      return this.links.filter(l => l.link_type === 'knowledge')
    },
    displayTasks() {
      if (this.taskLinks.length) return this.taskLinks
      return this.relatedTasks
    }
  },
  onLoad(options) {
    this.statusBarHeight = uni.getSystemInfoSync().statusBarHeight || 0
    this.itemId = options.id
    this.loadDetail()
  },
  onUnload() {
    this.stopPresence()
  },
  methods: {
    goBack() {
      if (this.isEditing) {
        uni.showModal({
          title: '提示',
          content: '正在编辑中，是否退出？未保存的内容将丢失。',
          success: (res) => { if (res.confirm) { this.exitEdit(false); uni.navigateBack() } }
        })
      } else {
        uni.navigateBack()
      }
    },
    toggleFav() { this.isFav = !this.isFav },
    goTask(id) { uni.navigateTo({ url: `/pages/task-detail/task-detail?id=${id}` }) },
    goKnowledge(id) {
      uni.navigateTo({ url: `/pages/knowledge-detail/knowledge-detail?id=${id}` })
    },

    async loadDetail() {
      try {
        const cached = uni.getStorageSync('selectedGraphNode')
        if (cached) {
          const node = JSON.parse(cached)
          this.item = {
            id: node.id, title: node.title || node.label || '知识节点',
            category: node.category || '通用', icon: node.icon || '',
            content: node.desc || '暂无详细内容', source: '知识图谱',
            equipment_category: (node.tags && node.tags[0]) || '通用',
            fault_type: node.category || '', view_count: 0, use_count: 0,
            tags: JSON.stringify(node.tags || []), created_at: '', updated_at: '',
            status: node.reviewStatus || '',
          }
          uni.removeStorageSync('selectedGraphNode')
          this.loadVersions()
          this.loadLinks()
          return
        }
      } catch (e) {}

      try {
        const res = await request.get('/knowledge', { service: 'yixiu' })
        if (res && res.data && res.data.items) {
          const found = res.data.items.find(it => String(it.id) === String(this.itemId))
          if (found) {
            this.item = found
            this.loadVersions()
            this.loadLinks()
            return
          }
        }
      } catch (e) {}

      try {
        const res = await request.get(`/api/maintenance-tasks/knowledge/${this.itemId}`)
        if (res && res.code === 200) { this.item = res.data; return }
      } catch (e) {}

      this.item = {
        id: this.itemId, title: '技术资料',
        content: '暂无内容，点击编辑添加。',
        category: '手册', equipment_category: '通用', source: '技术资料库',
        view_count: 0, use_count: 0, tags: '[]', created_at: '', updated_at: '',
      }
    },

    startEdit() {
      this.isEditing = true
      this.editTitle = this.item.title || ''
      this.editContent = this.item.content || ''
      this.editEquipment = this.item.equipment_category || this.item.equipment || ''
      this.editModel = this.item.equipment_model || this.item.model || ''
      const tags = this.parsedTags
      this.editTagsStr = Array.isArray(tags) ? tags.join(', ') : ''
      this.saveStatusText = '未保存'
      this.saveStatusClass = 'unsaved'
      this.startPresence()
    },

    exitEdit(confirmExit = true) {
      if (confirmExit && this.editContent !== (this.item.content || '')) {
        uni.showModal({
          title: '提示', content: '有未保存的修改，确定退出？',
          success: (res) => { if (res.confirm) { this.isEditing = false; this.stopPresence() } }
        })
      } else {
        this.isEditing = false
        this.stopPresence()
      }
    },

    onContentInput() {
      this.saveStatusText = '编辑中...'
      this.saveStatusClass = 'editing'
      if (this.autoSaveTimer) clearTimeout(this.autoSaveTimer)
      this.autoSaveTimer = setTimeout(() => { this.saveContent(true) }, 1500)
    },

    saveNow() {
      if (this.autoSaveTimer) { clearTimeout(this.autoSaveTimer); this.autoSaveTimer = null }
      this.saveContent(false)
    },

    async saveContent(isAuto) {
      const content = this.editContent.trim()
      if (!content) {
        uni.showToast({ title: '内容不能为空', icon: 'none' })
        return
      }
      this.saveStatusText = '保存中...'
      this.saveStatusClass = 'saving'
      try {
        const tags = this.editTagsStr.split(',').map(t => t.trim()).filter(Boolean)
        const res = await request.put(`/knowledge/${this.itemId}/content`, {
          title: this.editTitle, content: content,
          equipment: this.editEquipment, model: this.editModel,
          tags: tags, editor_name: '当前用户',
          change_summary: isAuto ? '自动保存' : '手动保存',
        }, { service: 'yixiu' })
        if (res && res.data) {
          this.item = { ...this.item, ...res.data }
          this.saveStatusText = isAuto ? '已自动保存' : '已保存'
          this.saveStatusClass = 'saved'
          if (!isAuto) uni.showToast({ title: '保存成功', icon: 'success' })
          this.loadVersions()
        }
      } catch (e) {
        this.saveStatusText = '保存失败'
        this.saveStatusClass = 'error'
        uni.showToast({ title: '保存失败', icon: 'none' })
      }
    },

    insertFormat(type) {
      const prefix = { heading: '## ', bold: '**加粗**', list: '- ', todo: '- [ ] ', table: '\n| 设备 | 参数 | 检测值 |\n|------|------|--------|\n|  |  |  |\n' }
      this.editContent += prefix[type] || ''
      this.onContentInput()
    },

    async loadVersions() {
      try {
        const res = await request.get(`/knowledge/${this.itemId}/versions`, { service: 'yixiu' })
        if (res && res.data) this.versions = res.data.versions || []
      } catch (e) { this.versions = [] }
    },

    viewVersion(ver) {
      this.viewingVersion = ver
      this.showVersionContent = true
    },

    async restoreVersion(ver) {
      uni.showModal({
        title: '恢复版本', content: `确定恢复到 v${ver.version}？当前内容将被替换。`,
        success: async (res) => {
          if (!res.confirm) return
          try {
            const r = await request.post(`/knowledge/${this.itemId}/versions/${ver.id}/restore`, {}, { service: 'yixiu' })
            if (r && r.data) {
              uni.showToast({ title: '已恢复', icon: 'success' })
              this.item.content = ver.content_snapshot
              this.item.title = ver.title_snapshot
              this.item.version = r.data.new_version
              this.showVersions = false
              this.loadVersions()
            }
          } catch (e) { uni.showToast({ title: '恢复失败', icon: 'none' }) }
        }
      })
    },

    async loadLinks() {
      try {
        const res = await request.get(`/knowledge/${this.itemId}/links`, { service: 'yixiu' })
        if (res && res.data) this.links = res.data.links || []
      } catch (e) { this.links = [] }
      try {
        const res = await request.get('/tasks', { service: 'yixiu' })
        if (res && res.data) this.availableTasks = (res.data.tasks || []).slice(0, 10)
      } catch (e) { this.availableTasks = [] }
    },

    async addTaskLink() {
      if (!this.newTaskId) { uni.showToast({ title: '请输入任务ID', icon: 'none' }); return }
      try {
        await request.post(`/knowledge/${this.itemId}/links`, {
          link_type: 'task', target_id: this.newTaskId,
          target_title: this.newTaskTitle || this.newTaskId,
        }, { service: 'yixiu' })
        this.newTaskId = ''; this.newTaskTitle = ''
        this.loadLinks()
        uni.showToast({ title: '关联成功', icon: 'success' })
      } catch (e) { uni.showToast({ title: '关联失败', icon: 'none' }) }
    },

    quickAddTask(task) {
      this.newTaskId = task.id
      this.newTaskTitle = task.title || task.equipment_name || '检修任务'
      this.addTaskLink()
    },

    async addKnowledgeLink() {
      if (!this.newKnowledgeId) { uni.showToast({ title: '请输入知识ID', icon: 'none' }); return }
      try {
        await request.post(`/knowledge/${this.itemId}/links`, {
          link_type: 'knowledge', target_id: this.newKnowledgeId,
          target_title: this.newKnowledgeTitle || this.newKnowledgeId,
        }, { service: 'yixiu' })
        this.newKnowledgeId = ''; this.newKnowledgeTitle = ''
        this.loadLinks()
        uni.showToast({ title: '引用成功', icon: 'success' })
      } catch (e) { uni.showToast({ title: '引用失败', icon: 'none' }) }
    },

    async removeLink(link) {
      uni.showModal({
        title: '移除关联', content: '确定移除此关联？',
        success: async (res) => {
          if (!res.confirm) return
          try {
            await request.delete(`/knowledge/${this.itemId}/links/${link.id}`, { service: 'yixiu' })
            this.loadLinks()
            uni.showToast({ title: '已移除', icon: 'none' })
          } catch (e) { uni.showToast({ title: '移除失败', icon: 'none' }) }
        }
      })
    },

    async submitForReview() {
      if (this.isEditing) {
        await this.saveContent(false)
      }
      try {
        const tags = this.editTagsStr ? this.editTagsStr.split(',').map(t => t.trim()).filter(Boolean) : this.parsedTags
        const res = await request.post('/knowledge/update', {
          title: this.editTitle || this.item.title,
          summary: (this.editContent || this.item.content || '').slice(0, 200),
          content: this.editContent || this.item.content,
          equipment: this.editEquipment || this.item.equipment_category,
          model: this.editModel || this.item.equipment_model,
          tags: tags, source: '技术资料库编辑提交',
        }, { service: 'yixiu' })
        if (res && res.data) {
          uni.showModal({ title: '提交成功', content: '内容已提交到知识审核队列，审核通过后将成为新的知识条目。', showCancel: false })
          this.showLinks = false
        }
      } catch (e) { uni.showToast({ title: '提交失败', icon: 'none' }) }
    },

    aiAssist(type) {
      const content = this.editContent || this.item.content || ''
      if (type === 'sop') {
        this.aiResult = '建议骨架：\n\n## 安全确认\n- [ ] 停机断电\n- [ ] 验电挂牌\n\n## 故障记录\n- [ ] 记录故障现象\n- [ ] 拍摄现场图片\n\n## 检测步骤\n- [ ] 测量关键参数\n- [ ] 对比手册标准\n\n## 维修处置\n- [ ] 执行更换/调整\n- [ ] 记录工具和部件\n\n## 复测验收\n- [ ] 恢复防护\n- [ ] 试运行确认'
      } else if (type === 'safety') {
        const missing = []
        if (!content.includes('断电') && !content.includes('停机')) missing.push('缺少安全隔离（停机断电）步骤')
        if (!content.includes('验电')) missing.push('缺少验电确认')
        if (!content.includes('复测') && !content.includes('试运行')) missing.push('缺少复测/试运行确认')
        this.aiResult = missing.length ? '检测到以下安全遗漏：\n' + missing.map(m => '⚠️ ' + m).join('\n') : '✅ 内容中已包含关键安全步骤，未发现明显遗漏。'
      } else if (type === 'format') {
        this.aiResult = '规范化建议：\n1. 将"看看"改为"检查"\n2. 将"弄一下"改为"调整"\n3. 将"坏了"改为"存在故障"\n4. 建议补充扭矩值和测量单位'
      }
    },

    adoptAIResult() {
      if (this.aiResult) {
        this.editContent += '\n\n' + this.aiResult
        this.onContentInput()
        this.aiResult = ''
        uni.showToast({ title: '已采纳', icon: 'success' })
      }
    },

    startPresence() {
      this.reportPresence()
      this.presenceTimer = setInterval(() => this.reportPresence(), 15000)
    },

    stopPresence() {
      if (this.presenceTimer) { clearInterval(this.presenceTimer); this.presenceTimer = null }
    },

    async reportPresence() {
      try {
        await request.post(`/knowledge/${this.itemId}/presence`, {
          user_id: 'current-user', user_name: '当前用户',
        }, { service: 'yixiu' })
      } catch (e) {}
    },

    getStatusBg(s) { return { pending: '#FFFBEB', in_progress: '#EFF6FF', completed: '#F0FDF4' }[s] || '#F1F5F9' },
    getStatusColor(s) { return { pending: '#D97706', in_progress: '#2563EB', completed: '#16A34A' }[s] || '#6B7280' },
    getStatusText(s) { return { pending: '待处理', in_progress: '进行中', completed: '已完成' }[s] || s || '未知' },
  }
}
</script>

<style scoped>
.kd-container { min-height: 100vh; background: #F1F5F9; }

.kd-header {
  background: linear-gradient(135deg, #1E3A5F 0%, #2563EB 100%);
  display: flex; align-items: center; justify-content: space-between;
  padding: 10rpx 24rpx 20rpx;
}
.header-back { padding: 16rpx; }
.back-arrow { font-size: 36rpx; color: #FFFFFF; font-weight: 700; }
.header-title { font-size: 34rpx; color: #FFFFFF; font-weight: 700; }
.header-actions { display: flex; align-items: center; gap: 16rpx; }
.header-btn { font-size: 26rpx; color: #FFFFFF; padding: 10rpx 20rpx; border-radius: 12rpx; background: rgba(255,255,255,0.15); font-weight: 600; }
.header-btn:active { background: rgba(255,255,255,0.25); }
.fav-btn { font-size: 36rpx; padding: 6rpx 16rpx; }

.edit-toolbar {
  display: flex; justify-content: space-between; align-items: center;
  padding: 12rpx 24rpx; background: #FFFFFF;
  border-bottom: 1rpx solid #E2E8F0;
}
.toolbar-left { flex: 1; }
.toolbar-right { display: flex; gap: 8rpx; flex-wrap: wrap; }
.save-status { font-size: 22rpx; font-weight: 600; }
.save-status.unsaved { color: #94A3B8; }
.save-status.editing { color: #F59E0B; }
.save-status.saving { color: #2563EB; }
.save-status.saved { color: #16A34A; }
.save-status.error { color: #EF4444; }
.tool-btn {
  font-size: 26rpx; padding: 8rpx 16rpx; border-radius: 10rpx;
  background: #F1F5F9; color: #334155; font-weight: 700; min-width: 56rpx; text-align: center;
}
.tool-btn:active { background: #E2E8F0; }

.kd-scroll { height: 100vh; }
.kd-scroll.edit-scroll { height: calc(100vh - 100rpx); }

.title-section {
  background: #FFFFFF; margin: 24rpx; border-radius: 16rpx;
  padding: 24rpx; box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.04);
}
.title-cat {
  font-size: 22rpx; font-weight: 700; padding: 4rpx 14rpx;
  border-radius: 8rpx; display: inline-block; margin-bottom: 12rpx;
}
.title-top-row { display: flex; align-items: center; gap: 12rpx; margin-bottom: 12rpx; flex-wrap: wrap; }
.title-status { font-size: 20rpx; font-weight: 600; padding: 4rpx 12rpx; border-radius: 8rpx; }
.title-version { font-size: 20rpx; font-weight: 700; color: #6366F1; background: #EEF2FF; padding: 4rpx 12rpx; border-radius: 8rpx; }
.status-approved { background: #F0FDF4; color: #16A34A; }
.status-pending { background: #FFFBEB; color: #D97706; }
.status-corrected { background: #FEF2F2; color: #EF4444; }
.cat-手册 { background: #EFF6FF; color: #2563EB; }
.cat-案例 { background: #FFF7ED; color: #EA580C; }
.cat-流程 { background: #F0FDF4; color: #16A34A; }
.cat-问答 { background: #FDF2F8; color: #DB2777; }
.cat-通用 { background: #F1F5F9; color: #475569; }
.cat-知识条目 { background: #F1F5F9; color: #475569; }
.title-text { font-size: 36rpx; font-weight: 800; color: #0F172A; display: block; margin-bottom: 12rpx; }
.title-input {
  font-size: 34rpx; font-weight: 800; color: #0F172A; width: 100%;
  border: 2rpx solid #E2E8F0; border-radius: 12rpx; padding: 16rpx; margin-bottom: 12rpx; box-sizing: border-box;
}
.title-meta { display: flex; gap: 24rpx; }
.meta { font-size: 24rpx; color: #94A3B8; }

.info-card {
  background: #FFFFFF; margin: 0 24rpx 24rpx; border-radius: 16rpx;
  padding: 24rpx; box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.04);
}
.info-row {
  display: flex; justify-content: space-between; align-items: center;
  padding: 14rpx 0; border-bottom: 1rpx solid #F1F5F9;
}
.info-row:last-child { border-bottom: none; }
.info-label { font-size: 26rpx; color: #94A3B8; flex-shrink: 0; }
.info-value { font-size: 26rpx; color: #1E293B; font-weight: 600; text-align: right; }
.info-row.edit-row { flex-direction: column; align-items: stretch; gap: 8rpx; }
.info-input {
  font-size: 26rpx; color: #1E293B; width: 100%;
  border: 2rpx solid #E2E8F0; border-radius: 10rpx; padding: 12rpx 16rpx; box-sizing: border-box;
}

.content-card, .tags-card, .related-card {
  background: #FFFFFF; margin: 0 24rpx 24rpx; border-radius: 16rpx;
  padding: 24rpx; box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.04);
}
.card-header { display: flex; align-items: center; gap: 10rpx; margin-bottom: 16rpx; }
.card-icon { font-size: 28rpx; }
.card-title { font-size: 30rpx; font-weight: 700; color: #0F172A; flex: 1; }
.card-hint { font-size: 22rpx; color: #94A3B8; }
.card-link { font-size: 24rpx; color: #2563EB; font-weight: 600; }
.card-title-small { font-size: 26rpx; font-weight: 700; color: #475569; margin-bottom: 12rpx; display: block; }
.content-text { font-size: 28rpx; color: #334155; line-height: 1.8; white-space: pre-wrap; }
.content-editor {
  font-size: 28rpx; color: #1E293B; line-height: 1.8; width: 100%;
  border: 2rpx solid #E2E8F0; border-radius: 12rpx; padding: 20rpx;
  min-height: 400rpx; box-sizing: border-box; white-space: pre-wrap;
}

.tags-row { display: flex; flex-wrap: wrap; gap: 10rpx; }
.tag-item {
  font-size: 24rpx; color: #2563EB; background: #EFF6FF;
  padding: 8rpx 20rpx; border-radius: 20rpx; font-weight: 600;
}

.related-list { display: flex; flex-direction: column; gap: 12rpx; }
.related-item {
  display: flex; justify-content: space-between; align-items: center;
  padding: 16rpx; background: #F8FAFC; border-radius: 12rpx;
  border: 1rpx solid #E2E8F0;
}
.related-item:active { background: #F1F5F9; }
.related-title { font-size: 26rpx; font-weight: 600; color: #1E293B; flex: 1; }
.related-arrow { font-size: 28rpx; color: #94A3B8; }
.related-status { font-size: 20rpx; font-weight: 700; padding: 4rpx 14rpx; border-radius: 8rpx; }
.empty-hint { display: flex; align-items: center; gap: 16rpx; padding: 20rpx 0; }
.empty-text { font-size: 24rpx; color: #94A3B8; }
.empty-action { font-size: 24rpx; color: #2563EB; font-weight: 600; }

.action-bar { display: flex; gap: 16rpx; padding: 0 24rpx; margin-bottom: 24rpx; }
.action-btn {
  flex: 1; text-align: center; padding: 22rpx; border-radius: 14rpx;
  background: #FFFFFF; color: #334155; font-size: 26rpx; font-weight: 700;
  border: 2rpx solid #E2E8F0;
}
.action-btn:active { background: #F8FAFC; }
.action-btn.primary { background: #2563EB; color: #FFFFFF; border-color: #2563EB; }
.action-btn.danger { color: #EF4444; border-color: #FECACA; }

.popup-mask {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.5); z-index: 999;
  display: flex; align-items: flex-end;
}
.popup-sheet {
  width: 100%; max-height: 70vh; background: #FFFFFF;
  border-radius: 24rpx 24rpx 0 0; display: flex; flex-direction: column;
}
.popup-sheet.large { max-height: 80vh; }
.popup-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 24rpx; border-bottom: 1rpx solid #E2E8F0;
}
.popup-title { font-size: 32rpx; font-weight: 700; color: #0F172A; }
.popup-close { font-size: 36rpx; color: #94A3B8; padding: 8rpx 16rpx; }
.popup-body { padding: 24rpx; max-height: 60vh; }

.version-item {
  padding: 20rpx; border-radius: 12rpx; background: #F8FAFC;
  margin-bottom: 12rpx; border: 2rpx solid transparent;
}
.version-item.active { border-color: #2563EB; background: #EFF6FF; }
.version-main { display: flex; align-items: center; gap: 12rpx; flex-wrap: wrap; }
.version-num { font-size: 26rpx; font-weight: 800; color: #2563EB; }
.version-editor { font-size: 24rpx; color: #334155; }
.version-time { font-size: 22rpx; color: #94A3B8; }
.version-summary { display: block; font-size: 22rpx; color: #64748B; margin-top: 8rpx; }
.version-actions { display: flex; gap: 16rpx; margin-top: 12rpx; }
.version-btn { font-size: 24rpx; color: #2563EB; padding: 8rpx 20rpx; border-radius: 8rpx; background: #EFF6FF; font-weight: 600; }
.version-btn.restore { color: #EA580C; background: #FFF7ED; }
.version-content-text { font-size: 28rpx; color: #334155; line-height: 1.8; white-space: pre-wrap; }

.link-section { margin-bottom: 32rpx; }
.link-section-title { font-size: 28rpx; font-weight: 700; color: #0F172A; display: block; margin-bottom: 12rpx; }
.link-desc { font-size: 24rpx; color: #64748B; line-height: 1.6; display: block; margin-bottom: 16rpx; }
.link-item {
  display: flex; justify-content: space-between; align-items: center;
  padding: 16rpx; background: #F8FAFC; border-radius: 10rpx; margin-bottom: 8rpx;
  border: 1rpx solid #E2E8F0;
}
.link-title { font-size: 26rpx; color: #1E293B; font-weight: 600; flex: 1; }
.link-remove { font-size: 28rpx; color: #EF4444; padding: 8rpx 16rpx; }
.link-add-row { display: flex; gap: 8rpx; margin-top: 12rpx; }
.link-input {
  flex: 1; font-size: 24rpx; border: 2rpx solid #E2E8F0; border-radius: 10rpx;
  padding: 12rpx; min-width: 0;
}
.link-add-btn {
  font-size: 24rpx; color: #FFFFFF; background: #2563EB;
  padding: 12rpx 20rpx; border-radius: 10rpx; font-weight: 700; white-space: nowrap;
}
.link-suggest { margin-top: 12rpx; }
.suggest-label { font-size: 22rpx; color: #94A3B8; }
.suggest-list { display: flex; flex-wrap: wrap; gap: 8rpx; margin-top: 8rpx; }
.suggest-item {
  font-size: 22rpx; color: #2563EB; background: #EFF6FF;
  padding: 8rpx 16rpx; border-radius: 8rpx; font-weight: 600;
}

.ai-actions { display: flex; flex-direction: column; gap: 12rpx; }
.ai-btn {
  font-size: 26rpx; color: #7C3AED; background: #F5F3FF;
  padding: 20rpx; border-radius: 12rpx; font-weight: 600; text-align: center;
  border: 2rpx solid #DDD6FE;
}
.ai-btn.full { width: 100%; }
.ai-btn:active { background: #EDE9FE; }
.ai-result {
  margin-top: 16rpx; padding: 16rpx; background: #F8FAFC;
  border-radius: 12rpx; border: 1rpx solid #E2E8F0;
}
.ai-result-text { font-size: 24rpx; color: #334155; line-height: 1.7; white-space: pre-wrap; }
.ai-adopt-btn {
  margin-top: 12rpx; font-size: 24rpx; color: #FFFFFF; background: #16A34A;
  padding: 12rpx; border-radius: 10rpx; text-align: center; font-weight: 700;
}
</style>
