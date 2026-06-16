<template>
  <view class="fp-mask" v-if="visible" @click="close">
    <view class="fp-panel" @click.stop>
      <view class="fp-header">
        <text class="fp-title">{{ title }}</text>
        <view class="fp-header-actions">
          <text class="fp-selected-count" v-if="selectedFiles.length">{{ selectedFiles.length }} 已选</text>
          <text class="fp-close" @click="close">✕</text>
        </view>
      </view>

      <!-- 搜索 -->
      <view class="fp-search">
        <text class="fp-search-icon">🔍</text>
        <input class="fp-search-input" v-model="searchText" placeholder="搜索文件..." />
      </view>

      <!-- 分类筛选 -->
      <scroll-view scroll-x class="fp-cats">
        <view class="fp-cats-inner">
          <view class="fp-cat" :class="{ active: !activeCat }" @click="activeCat = ''">全部</view>
          <view class="fp-cat" :class="{ active: activeCat === c }" v-for="c in categories" :key="c" @click="activeCat = c">{{ c }}</view>
        </view>
      </scroll-view>

      <!-- 文件列表 -->
      <scroll-view scroll-y class="fp-list">
        <view v-for="f in filteredFiles" :key="f.id" class="fp-item" :class="{ selected: isSelected(f.id) }" @click="toggleFile(f)">
          <view class="fp-item-icon-wrap" :style="{ background: getTypeBg(f.type) }">
            <text class="fp-item-icon">{{ getTypeIcon(f.type) }}</text>
          </view>
          <view class="fp-item-info">
            <text class="fp-item-name">{{ f.name }}</text>
            <text class="fp-item-meta">{{ f.category }} · {{ formatSize(f.size) }}</text>
          </view>
          <view class="fp-check">
            <text class="fp-check-icon">{{ isSelected(f.id) ? '☑' : '☐' }}</text>
          </view>
        </view>
        <view class="fp-empty" v-if="filteredFiles.length === 0">
          <text class="fp-empty-text">暂无文件</text>
        </view>
      </scroll-view>

      <!-- 底部按钮 -->
      <view class="fp-footer">
        <view class="fp-btn cancel" @click="close"><text>取消</text></view>
        <view class="fp-btn confirm" :class="{ disabled: selectedFiles.length === 0 }" @click="confirm">
          <text>确认选择 ({{ selectedFiles.length }})</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
const MOCK_FILES = [
  { id: 'f10', name: '摩托车发动机维修手册.pdf', type: 'pdf', size: 18432000, category: '手册' },
  { id: 'f11', name: 'ZK-320配电柜维护规范.pdf', type: 'pdf', size: 5242880, category: '手册' },
  { id: 'f12', name: '发动机异响现场照片.jpg', type: 'image', size: 2097152, category: '附件' },
  { id: 'f13', name: '配电柜过热红外图.jpg', type: 'image', size: 3145728, category: '附件' },
  { id: 'f14', name: '点火系统检查流程.docx', type: 'document', size: 1048576, category: '流程' },
  { id: 'f15', name: '2026年6月检修报告汇总.pdf', type: 'report', size: 4194304, category: '报告' },
  { id: 'f16', name: '液压系统泄漏排查视频.mp4', type: 'video', size: 52428800, category: '附件' },
  { id: 'f17', name: '万用表校准记录表.xlsx', type: 'document', size: 524288, category: '附件' },
]

export default {
  name: 'FilePicker',
  props: {
    visible: { type: Boolean, default: false },
    title: { type: String, default: '选择文件' },
    multiple: { type: Boolean, default: true },
    files: { type: Array, default: () => MOCK_FILES },
  },
  data() {
    return {
      searchText: '',
      activeCat: '',
      selectedFiles: [],
      categories: ['手册', '案例', '流程', '附件', '报告'],
    }
  },
  computed: {
    filteredFiles() {
      let list = this.files.filter(f => f.type !== 'folder')
      if (this.activeCat) list = list.filter(f => f.category === this.activeCat)
      if (this.searchText) {
        const kw = this.searchText.toLowerCase()
        list = list.filter(f => f.name.toLowerCase().includes(kw))
      }
      return list
    }
  },
  watch: {
    visible(v) { if (v) this.selectedFiles = [] }
  },
  methods: {
    close() { this.$emit('close') },
    isSelected(id) { return this.selectedFiles.some(f => f.id === id) },
    toggleFile(f) {
      if (this.isSelected(f.id)) {
        this.selectedFiles = this.selectedFiles.filter(x => x.id !== f.id)
      } else {
        if (!this.multiple) this.selectedFiles = []
        this.selectedFiles.push(f)
      }
    },
    confirm() {
      this.$emit('select', this.selectedFiles)
      this.close()
    },
    getTypeIcon(type) {
      return { pdf: '📕', image: '🖼️', video: '🎬', document: '📝', report: '📊' }[type] || '📄'
    },
    getTypeBg(type) {
      return { pdf: '#FEF2F2', image: '#F0FDF4', video: '#FDF2F8', document: '#FFFBEB', report: '#F5F3FF' }[type] || '#F1F5F9'
    },
    formatSize(bytes) {
      if (!bytes) return '--'
      if (bytes < 1048576) return (bytes / 1024).toFixed(0) + ' KB'
      return (bytes / 1048576).toFixed(1) + ' MB'
    },
  }
}
</script>

<style scoped>
.fp-mask { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); z-index: 3000; display: flex; align-items: flex-end; }
.fp-panel { width: 100%; max-height: 80vh; background: #FFFFFF; border-radius: 24rpx 24rpx 0 0; display: flex; flex-direction: column; }
.fp-header { display: flex; justify-content: space-between; align-items: center; padding: 24rpx; border-bottom: 1rpx solid #F1F5F9; }
.fp-title { font-size: 32rpx; font-weight: 700; color: #0F172A; }
.fp-header-actions { display: flex; align-items: center; gap: 16rpx; }
.fp-selected-count { font-size: 24rpx; color: #2563EB; font-weight: 600; }
.fp-close { font-size: 32rpx; color: #94A3B8; padding: 8rpx; }
.fp-search { display: flex; align-items: center; margin: 16rpx 24rpx; background: #F1F5F9; border-radius: 24rpx; padding: 0 16rpx; height: 64rpx; }
.fp-search-icon { font-size: 24rpx; margin-right: 8rpx; }
.fp-search-input { flex: 1; font-size: 26rpx; }
.fp-cats { padding: 0 24rpx 12rpx; white-space: nowrap; }
.fp-cats-inner { display: inline-flex; gap: 10rpx; }
.fp-cat { padding: 8rpx 20rpx; border-radius: 20rpx; background: #F1F5F9; font-size: 24rpx; color: #64748B; }
.fp-cat.active { background: #EFF6FF; color: #2563EB; font-weight: 600; }
.fp-list { flex: 1; padding: 0 24rpx; max-height: 50vh; }
.fp-item { display: flex; align-items: center; gap: 14rpx; padding: 16rpx 0; border-bottom: 1rpx solid #F1F5F9; }
.fp-item.selected { background: #EFF6FF; margin: 0 -24rpx; padding: 16rpx 24rpx; }
.fp-item-icon-wrap { width: 48rpx; height: 48rpx; border-radius: 12rpx; display: flex; align-items: center; justify-content: center; }
.fp-item-icon { font-size: 24rpx; }
.fp-item-info { flex: 1; min-width: 0; }
.fp-item-name { font-size: 28rpx; font-weight: 600; color: #1E293B; display: block; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.fp-item-meta { font-size: 22rpx; color: #94A3B8; }
.fp-check { padding: 4rpx; }
.fp-check-icon { font-size: 28rpx; color: #2563EB; }
.fp-empty { padding: 60rpx 0; text-align: center; }
.fp-empty-text { font-size: 28rpx; color: #94A3B8; }
.fp-footer { display: flex; gap: 16rpx; padding: 16rpx 24rpx; padding-bottom: calc(16rpx + constant(safe-area-inset-bottom)); padding-bottom: calc(16rpx + env(safe-area-inset-bottom)); border-top: 1rpx solid #F1F5F9; }
.fp-btn { flex: 1; padding: 20rpx; border-radius: 12rpx; text-align: center; font-size: 28rpx; font-weight: 600; }
.fp-btn.cancel { background: #F1F5F9; color: #64748B; }
.fp-btn.confirm { background: #2563EB; color: #FFFFFF; }
.fp-btn.confirm.disabled { opacity: 0.5; }
</style>
