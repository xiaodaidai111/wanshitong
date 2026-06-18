<template>
  <view class="kb-page">
    <!-- ========== 顶部导航栏 ========== -->
    <view class="kb-navbar" :style="{ paddingTop: statusBarHeight + 'px' }">
      <view class="kb-navbar-inner">
        <view class="kb-navbar-left">
          <view class="kb-logo-circle" @click="toggleSidebar">
            <text class="kb-logo-text">WS</text>
          </view>
          <view class="kb-title-block">
            <text class="kb-main-title">设备检修智能工作台</text>
            <text class="kb-sub-title">多模态检索 · 智能问修 · 标准作业 · 知识沉淀</text>
          </view>
        </view>
      </view>
    </view>

    <scroll-view class="kb-scroll" scroll-y :show-scrollbar="false">

      <!-- ========== 搜索栏 + 功能按钮 ========== -->
      <view class="kb-action-row">
        <view class="kb-search-wrap">
          <text class="kb-search-icon">🔍</text>
          <input
            class="kb-search-input"
            v-model="searchText"
            placeholder="搜索设备、故障现象、检修流程、手册章节或案例"
            @confirm="handleSearch"
          />
        </view>
        <view class="kb-action-btns">
          <view class="kb-action-btn" @click="handleUpload">
            <text class="kb-action-icon">📤</text>
            <text class="kb-action-text">上传资料</text>
          </view>
          <view class="kb-action-btn primary" @click="handleGenerateGraph">
            <text class="kb-action-icon">🗺️</text>
            <text class="kb-action-text">生成图谱</text>
          </view>
        </view>
      </view>

      <!-- ========== 分类标签（横向滚动） ========== -->
      <scroll-view class="kb-tabs-scroll" scroll-x :show-scrollbar="false">
        <view class="kb-tabs">
          <view
            v-for="tab in topTabs"
            :key="tab.key"
            class="kb-tab-item"
            :class="{ active: activeTab === tab.key }"
            @click="handleTabChange(tab.key)"
          >
            <text class="kb-tab-text">{{ tab.name }}</text>
          </view>
        </view>
      </scroll-view>

      <!-- ========== 知识统计卡片 ========== -->
      <view class="kb-stats-wrap">
        <view class="kb-stats-grid">
          <view class="kb-stat-card stat-blue" v-for="s in statsList" :key="s.label">
            <text class="kb-stat-icon">{{ s.icon }}</text>
            <text class="kb-stat-num">{{ s.num }}</text>
            <text class="kb-stat-label">{{ s.label }}</text>
          </view>
        </view>
      </view>

      <!-- ========== 筛选栏（横向 chip） ========== -->
      <view class="kb-filter-row">
        <view class="kb-filter-group" v-for="(fg, fi) in filterGroups" :key="fi">
          <text class="kb-filter-title">{{ fg.title }}</text>
          <scroll-view class="kb-filter-scroll" scroll-x :show-scrollbar="false">
            <view class="kb-filter-chips">
              <view
                v-for="opt in fg.options"
                :key="opt.key"
                class="kb-filter-chip"
                :class="{ active: fg.active === opt.key }"
                @click="fg.active = opt.key"
              >
                <text class="kb-filter-chip-text">{{ opt.name }}</text>
              </view>
            </view>
          </scroll-view>
        </view>
      </view>

      <!-- ========== 知识图谱区域 ========== -->
      <view class="kb-graph-section">
        <view class="kb-section-head">
          <view class="kb-section-title-wrap">
            <text class="kb-section-icon">🕸️</text>
            <text class="kb-section-title">知识图谱</text>
          </view>
          <text class="kb-section-sub">摩托车发动机启动困难</text>
        </view>

        <!-- 图例 -->
        <view class="kb-graph-legend">
          <view
            v-for="cat in graphLegend"
            :key="cat.key"
            class="kb-legend-item"
          >
            <view class="kb-legend-dot" :style="{ background: cat.color }"></view>
            <text class="kb-legend-text">{{ cat.name }}</text>
          </view>
        </view>

        <!-- 图谱画布（可左右上下滑动） -->
        <view class="kb-graph-canvas-wrap">
          <scroll-view class="kb-graph-canvas-scroll" scroll-x scroll-y :show-scrollbar="false">
            <view class="kb-graph-canvas">
              <!-- 连线 -->
              <view
                v-for="(line, li) in graphLines"
                :key="'line-' + li"
                class="kb-graph-line"
                :style="getLineStyle(line)"
              ></view>
              <!-- 节点 -->
              <view
                v-for="node in graphNodes"
                :key="'node-' + node.id"
                class="kb-graph-node"
                :class="{ active: selectedNode && selectedNode.id === node.id }"
                :style="getNodeStyle(node)"
                @click="selectNode(node)"
              >
                <view class="kb-graph-node-icon" :style="{ background: node.color }">
                  <text class="kb-graph-node-emoji">{{ node.icon }}</text>
                </view>
                <text class="kb-graph-node-label">{{ node.shortLabel || node.label }}</text>
              </view>
            </view>
          </scroll-view>
          <view class="kb-graph-tip" v-if="!selectedNode">
            <text class="kb-graph-tip-text">👆 点击图谱节点查看详情</text>
          </view>
        </view>
      </view>

      <!-- ========== 节点详情面板 ========== -->
      <view class="kb-detail-section" v-if="selectedNode">
        <view class="kb-detail-head">
          <view class="kb-detail-icon-wrap" :style="{ background: selectedNode.color + '20' }">
            <text class="kb-detail-icon" :style="{ color: selectedNode.color }">{{ selectedNode.icon }}</text>
          </view>
          <view class="kb-detail-title-wrap">
            <text class="kb-detail-title">{{ selectedNode.label }}</text>
            <view class="kb-detail-meta">
              <text class="kb-detail-cat" :style="{ background: selectedNode.color + '20', color: selectedNode.color }">
                {{ selectedNode.category }}
              </text>
              <text class="kb-detail-status" v-if="selectedNode.status" :class="selectedNode.status">
                {{ statusText(selectedNode.status) }}
              </text>
            </view>
          </view>
        </view>

        <view class="kb-detail-grid">
          <view class="kb-detail-cell">
            <text class="kb-detail-cell-title">📋 节点类型</text>
            <text class="kb-detail-cell-value">{{ selectedNode.type || '核心知识点' }}</text>
          </view>
          <view class="kb-detail-cell">
            <text class="kb-detail-cell-title">🔧 关联设备</text>
            <view class="kb-detail-tags">
              <text
                v-for="(eq, i) in selectedNode.equipment"
                :key="i"
                class="kb-detail-tag"
              >{{ eq }}</text>
            </view>
          </view>
          <view class="kb-detail-cell full">
            <text class="kb-detail-cell-title">🔍 检查方法</text>
            <text class="kb-detail-cell-desc">{{ selectedNode.checkMethod }}</text>
          </view>
          <view class="kb-detail-cell">
            <text class="kb-detail-cell-title">📐 标准参数</text>
            <view class="kb-param-list">
              <view
                v-for="(p, i) in selectedNode.params"
                :key="i"
                class="kb-param-item"
              >
                <text class="kb-param-name">{{ p.name }}</text>
                <text class="kb-param-value">{{ p.value }}</text>
              </view>
            </view>
          </view>
          <view class="kb-detail-cell">
            <text class="kb-detail-cell-title">📄 知识来源</text>
            <view class="kb-source-list">
              <text
                v-for="(s, i) in selectedNode.sources"
                :key="i"
                class="kb-source-item"
              >{{ s }}</text>
            </view>
          </view>
          <view class="kb-detail-cell" v-if="selectedNode.similarCases && selectedNode.similarCases.length">
            <text class="kb-detail-cell-title">🧰 相似案例</text>
            <view class="kb-case-list">
              <view
                v-for="(c, i) in selectedNode.similarCases"
                :key="i"
                class="kb-case-item"
              >
                <text class="kb-case-item-title">{{ c.title }}</text>
                <text class="kb-case-item-match">匹配度 {{ c.match }}</text>
              </view>
            </view>
          </view>
        </view>

        <view class="kb-detail-actions">
          <view class="kb-detail-action primary" @click="handleViewDetail">
            <text>📄 查看完整</text>
          </view>
          <view class="kb-detail-action" @click="handleApplyTask">
            <text>🔧 应用到任务</text>
          </view>
        </view>
      </view>

      <!-- 底部留白给 tabbar 和悬浮按钮 -->
      <view class="kb-bottom-space"></view>
    </scroll-view>

    <!-- ========== 右下角知识库助手悬浮入口 ========== -->
    <view class="kb-fab" @click.stop="showAssistant = !showAssistant">
      <text class="kb-fab-icon">🤖</text>
    </view>

    <!-- ========== 助手抽屉 ========== -->
    <view class="kb-drawer-mask" v-if="showAssistant" @click="showAssistant = false">
      <view class="kb-drawer" @click.stop>
        <view class="kb-drawer-handle"></view>
        <view class="kb-drawer-head">
          <view class="kb-drawer-title-wrap">
            <text class="kb-drawer-title">知识库助手</text>
            <text class="kb-drawer-subtitle">AI 辅助检索与沉淀</text>
          </view>
          <view class="kb-drawer-close" @click="showAssistant = false">
            <text class="kb-drawer-close-icon">×</text>
          </view>
        </view>

        <view class="kb-drawer-grid">
          <view class="kb-drawer-item" @click="onAssistantAction('search')">
            <view class="kb-drawer-icon bg-blue">
              <text>🔍</text>
            </view>
            <text class="kb-drawer-item-title">检索手册</text>
            <text class="kb-drawer-item-desc">查找设备维修规范</text>
          </view>
          <view class="kb-drawer-item" @click="onAssistantAction('mindmap')">
            <view class="kb-drawer-icon bg-green">
              <text>🧠</text>
            </view>
            <text class="kb-drawer-item-title">生成思维导图</text>
            <text class="kb-drawer-item-desc">一键生成知识图谱</text>
          </view>
          <view class="kb-drawer-item" @click="onAssistantAction('organize')">
            <view class="kb-drawer-icon bg-orange">
              <text>📑</text>
            </view>
            <text class="kb-drawer-item-title">整理知识点</text>
            <text class="kb-drawer-item-desc">自动归类与去重</text>
          </view>
          <view class="kb-drawer-item" @click="onAssistantAction('upload')">
            <view class="kb-drawer-icon bg-purple">
              <text>📥</text>
            </view>
            <text class="kb-drawer-item-title">上传案例入库</text>
            <text class="kb-drawer-item-desc">沉淀一线经验</text>
          </view>
        </view>

        <view class="kb-drawer-tip">
          <text class="kb-drawer-tip-text">💡 点击图标即可快速调用对应能力</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      statusBarHeight: 0,
      searchText: '',
      activeTab: 'all',
      topTabs: [
        { key: 'all', name: '全部' },
        { key: 'device', name: '设备' },
        { key: 'fault', name: '故障现象' },
        { key: 'manual', name: '检修手册' },
        { key: 'sop', name: '检修流程' },
        { key: 'case', name: '案例库' },
        { key: 'multimodal', name: '多模态证据' },
        { key: 'update', name: '知识更新' }
      ],
      statsList: [
        { icon: '📘', num: 12, label: '维修手册', color: '#3B82F6' },
        { icon: '📕', num: 36, label: '故障案例', color: '#EF4444' },
        { icon: '📋', num: 18, label: '标准流程', color: '#0891B2' },
        { icon: '🕸️', num: 156, label: '知识节点', color: '#7C3AED' },
        { icon: '⏳', num: 4, label: '待审核', color: '#F59E0B' }
      ],
      filterGroups: [
        {
          title: '知识类型',
          active: 'all',
          options: [
            { key: 'all', name: '全部' },
            { key: 'device', name: '设备' },
            { key: 'fault', name: '故障现象' },
            { key: 'manual', name: '检修手册' },
            { key: 'sop', name: '检修流程' },
            { key: 'case', name: '案例库' }
          ]
        },
        {
          title: '设备系统',
          active: 'all',
          options: [
            { key: 'all', name: '全部' },
            { key: 'engine', name: '发动机' },
            { key: 'electrical', name: '电气' },
            { key: 'hydraulic', name: '液压' },
            { key: 'mechanical', name: '机械' }
          ]
        },
        {
          title: '知识状态',
          active: 'all',
          options: [
            { key: 'all', name: '全部' },
            { key: 'approved', name: '已审核' },
            { key: 'pending', name: '待审核' },
            { key: 'updated', name: '已更新' }
          ]
        }
      ],
      graphLegend: [
        { key: 'device', name: '设备', color: '#0F766E' },
        { key: 'fault', name: '故障现象', color: '#E8453C' },
        { key: 'cause', name: '故障原因', color: '#D97706' },
        { key: 'sop', name: '检修流程', color: '#0284C7' },
        { key: 'manual', name: '手册章节', color: '#0891B2' },
        { key: 'case', name: '相似案例', color: '#7C3AED' }
      ],
      graphNodes: [
        {
          id: 1,
          label: '摩托车发动机',
          shortLabel: '发动机',
          category: '设备',
          icon: '🏍️',
          color: '#0F766E',
          x: 280,
          y: 240,
          type: '设备节点',
          equipment: ['CG-125', '发动机总成'],
          checkMethod: '通过外观、声音、振动和运行参数综合判断发动机整体状态。',
          params: [
            { name: '运行温度', value: '≤ 90℃' },
            { name: '怠速转速', value: '1400 ± 50 r/min' },
            { name: '缸压', value: '≥ 1.0 MPa' }
          ],
          sources: ['《摩托车发动机维修手册》v2.1', '《CG-125技术规范》'],
          similarCases: [
            { title: 'CG-125启动困难排查案例', match: '92%' }
          ],
          status: 'approved'
        },
        {
          id: 2,
          label: '启动困难',
          shortLabel: '启动困难',
          category: '故障现象',
          icon: '⚠️',
          color: '#E8453C',
          x: 80,
          y: 80,
          type: '故障现象',
          equipment: ['CG-125', '发动机'],
          checkMethod: '通过打火反应、启动机电流、燃油供给和点火状态综合判断。',
          params: [
            { name: '启动电流', value: '30-80A' }
          ],
          sources: ['现场案例库', '故障排查SOP'],
          similarCases: [
            { title: '化油器堵塞导致启动困难', match: '88%' },
            { title: '点火线圈失效启动困难', match: '85%' }
          ],
          status: 'approved'
        },
        {
          id: 3,
          label: '火花塞积碳',
          shortLabel: '火花塞',
          category: '故障原因',
          icon: '🕯️',
          color: '#D97706',
          x: 280,
          y: 80,
          type: '故障原因',
          equipment: ['CG-125', '点火系统'],
          checkMethod: '拆下火花塞观察电极颜色，使用塞尺测量间隙是否在 0.6-0.7mm。',
          params: [
            { name: '电极间隙', value: '0.6-0.7mm' },
            { name: '电极颜色', value: '浅棕为正常' }
          ],
          sources: ['《CG-125维修手册》第3章'],
          similarCases: [
            { title: '火花塞积碳引起启动困难', match: '95%' }
          ],
          status: 'approved'
        },
        {
          id: 4,
          label: '化油器堵塞',
          shortLabel: '化油器',
          category: '故障原因',
          icon: '🧴',
          color: '#D97706',
          x: 480,
          y: 80,
          type: '故障原因',
          equipment: ['CG-125', '燃油系统'],
          checkMethod: '拆检化油器，检查主量孔、怠速量孔和浮子室油面高度。',
          params: [
            { name: '浮子室油面', value: '25 ± 1mm' }
          ],
          sources: ['《CG-125维修手册》第4章'],
          similarCases: [
            { title: '化油器主量孔堵塞案例', match: '90%' }
          ],
          status: 'pending'
        },
        {
          id: 5,
          label: '点火系统检查',
          shortLabel: '点火检查',
          category: '检修流程',
          icon: '⚡',
          color: '#0284C7',
          x: 80,
          y: 360,
          type: '标准SOP',
          equipment: ['CG-125', '点火系统'],
          checkMethod: '按 SOP 顺序检查火花塞、点火线圈、高压线和触发线圈。',
          params: [
            { name: '火花强度', value: '≥ 8mm 跳火' },
            { name: '初级电阻', value: '0.5-1.0 Ω' }
          ],
          sources: ['《点火系统SOP-IS-001》'],
          similarCases: [],
          status: 'approved'
        },
        {
          id: 6,
          label: '燃油供给检查',
          shortLabel: '燃油检查',
          category: '检修流程',
          icon: '⛽',
          color: '#0284C7',
          x: 280,
          y: 400,
          type: '标准SOP',
          equipment: ['CG-125', '燃油系统'],
          checkMethod: '检查油路畅通性、化油器油面、油泵输出和泄漏点。',
          params: [
            { name: '供油压力', value: '2.5-3.5 kPa' }
          ],
          sources: ['《燃油系统SOP-FS-002》'],
          similarCases: [],
          status: 'approved'
        },
        {
          id: 7,
          label: 'CG-125 点火章节',
          shortLabel: '点火手册',
          category: '手册章节',
          icon: '📘',
          color: '#0891B2',
          x: 480,
          y: 360,
          type: '手册引用',
          equipment: ['CG-125'],
          checkMethod: '参见手册第3.2节"点火系统故障排查"完整流程。',
          params: [
            { name: '页码', value: 'P.42-58' }
          ],
          sources: ['《摩托车发动机维修手册》'],
          similarCases: [],
          status: 'approved'
        },
        {
          id: 8,
          label: '现场启动困难案例',
          shortLabel: '案例#C-2031',
          category: '相似案例',
          icon: '🧰',
          color: '#7C3AED',
          x: 680,
          y: 240,
          type: '现场案例',
          equipment: ['CG-125'],
          checkMethod: '现场案例记录的处理过程与结论。',
          params: [
            { name: '处置时长', value: '45 分钟' }
          ],
          sources: ['一线检修案例库'],
          similarCases: [],
          status: 'pending'
        }
      ],
      graphLines: [
        { from: 1, to: 2 },
        { from: 1, to: 5 },
        { from: 1, to: 6 },
        { from: 2, to: 3 },
        { from: 2, to: 4 },
        { from: 5, to: 3 },
        { from: 5, to: 7 },
        { from: 6, to: 4 },
        { from: 3, to: 8 },
        { from: 4, to: 8 },
        { from: 7, to: 5 },
        { from: 8, to: 2 }
      ],
      selectedNode: null,
      showAssistant: false
    }
  },
  mounted() {
    const sys = uni.getSystemInfoSync()
    this.statusBarHeight = sys.statusBarHeight || 0
  },
  methods: {
    toggleSidebar() {
      uni.showToast({ title: '侧边栏菜单', icon: 'none' })
    },
    handleSearch() {
      uni.showToast({ title: '搜索：' + this.searchText, icon: 'none' })
    },
    handleUpload() {
      uni.showToast({ title: '上传资料', icon: 'none' })
    },
    handleGenerateGraph() {
      uni.showToast({ title: '生成图谱中...', icon: 'none' })
    },
    handleTabChange(key) {
      this.activeTab = key
    },
    selectNode(node) {
      this.selectedNode = node
    },
    getNodeStyle(node) {
      return {
        left: node.x + 'rpx',
        top: node.y + 'rpx'
      }
    },
    getLineStyle(line) {
      const from = this.graphNodes.find(n => n.id === line.from)
      const to = this.graphNodes.find(n => n.id === line.to)
      if (!from || !to) return {}
      const x1 = from.x + 40
      const y1 = from.y + 40
      const x2 = to.x + 40
      const y2 = to.y + 40
      const dx = x2 - x1
      const dy = y2 - y1
      const length = Math.sqrt(dx * dx + dy * dy)
      const angle = Math.atan2(dy, dx) * 180 / Math.PI
      return {
        left: x1 + 'rpx',
        top: y1 + 'rpx',
        width: length + 'rpx',
        transform: `rotate(${angle}deg)`
      }
    },
    statusText(status) {
      const map = { approved: '已审核', pending: '待审核', updated: '已更新' }
      return map[status] || status
    },
    handleViewDetail() {
      uni.navigateTo({ url: '/pages/knowledge-detail/knowledge-detail' })
    },
    handleApplyTask() {
      uni.showToast({ title: '已关联到检修任务', icon: 'none' })
    },
    onAssistantAction(action) {
      const names = { search: '检索手册', mindmap: '生成思维导图', organize: '整理知识点', upload: '上传案例入库' }
      uni.showToast({ title: names[action] || '操作', icon: 'none' })
      this.showAssistant = false
    }
  }
}
</script>

<style scoped>
page {
  background-color: #F0F4F8;
}

.kb-page {
  min-height: 100vh;
  background: #F0F4F8;
  font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Helvetica Neue", Arial, sans-serif;
}

/* ========== 顶部导航栏 ========== */
.kb-navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  background: #FFFFFF;
  z-index: 500;
  box-shadow: 0 2rpx 12rpx rgba(15, 23, 42, 0.06);
}

.kb-navbar-inner {
  display: flex;
  align-items: center;
  height: 100rpx;
  padding: 0 28rpx;
}

.kb-navbar-left {
  display: flex;
  align-items: center;
  gap: 18rpx;
  flex: 1;
  min-width: 0;
}

.kb-logo-circle {
  width: 76rpx;
  height: 76rpx;
  border-radius: 20rpx;
  background: linear-gradient(135deg, #3B82F6 0%, #10B981 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 4rpx 14rpx rgba(59, 130, 246, 0.3);
}

.kb-logo-text {
  font-size: 28rpx;
  font-weight: 800;
  color: #FFFFFF;
  letter-spacing: 1rpx;
}

.kb-title-block {
  display: flex;
  flex-direction: column;
  gap: 6rpx;
  min-width: 0;
  flex: 1;
}

.kb-main-title {
  font-size: 32rpx;
  font-weight: 700;
  color: #0F172A;
  line-height: 1.2;
  letter-spacing: -0.5rpx;
}

.kb-sub-title {
  font-size: 20rpx;
  color: #475569;
  font-weight: 400;
  line-height: 1.2;
  opacity: 0.9;
}

/* ========== 滚动区 ========== */
.kb-scroll {
  padding-top: calc(100rpx + env(safe-area-inset-top, 44px));
  min-height: 100vh;
  box-sizing: border-box;
}

/* ========== 搜索与功能按钮 ========== */
.kb-action-row {
  padding: 24rpx 28rpx;
  background: #FFFFFF;
  margin-bottom: 18rpx;
}

.kb-search-wrap {
  display: flex;
  align-items: center;
  background: #F8FAFC;
  border-radius: 24rpx;
  padding: 24rpx 28rpx;
  margin-bottom: 20rpx;
  border: 2rpx solid #E2E8F0;
}

.kb-search-icon {
  font-size: 34rpx;
  margin-right: 16rpx;
  color: #64748B;
  flex-shrink: 0;
}

.kb-search-input {
  flex: 1;
  font-size: 28rpx;
  color: #0F172A;
  background: transparent;
  min-width: 0;
  line-height: 1.5;
}

.kb-action-btns {
  display: flex;
  gap: 16rpx;
}

.kb-action-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10rpx;
  padding: 24rpx 18rpx;
  background: rgba(59, 130, 246, 0.08);
  border: 2rpx solid rgba(59, 130, 246, 0.15);
  border-radius: 16rpx;
  box-sizing: border-box;
}

.kb-action-btn.primary {
  background: linear-gradient(135deg, #10B981 0%, #059669 100%);
  border: 2rpx solid #10B981;
  box-shadow: 0 4rpx 14rpx rgba(16, 185, 129, 0.3);
}

.kb-action-icon {
  font-size: 32rpx;
}

.kb-action-text {
  font-size: 26rpx;
  font-weight: 700;
  color: #3B82F6;
  white-space: nowrap;
}

.kb-action-btn.primary .kb-action-text {
  color: #FFFFFF;
}

/* ========== 分类标签 ========== */
.kb-tabs-scroll {
  background: #FFFFFF;
  white-space: nowrap;
  width: 100%;
  padding: 8rpx 0 0;
  border-bottom: 2rpx solid #F1F5F9;
  margin-bottom: 18rpx;
  box-sizing: border-box;
}

.kb-tabs {
  display: inline-flex;
  align-items: center;
  padding: 0 20rpx;
  gap: 8rpx;
}

.kb-tab-item {
  padding: 24rpx 18rpx;
  position: relative;
  display: inline-block;
  flex-shrink: 0;
}

.kb-tab-text {
  font-size: 28rpx;
  color: #64748B;
  font-weight: 500;
  white-space: nowrap;
}

.kb-tab-item.active .kb-tab-text {
  color: #3B82F6;
  font-weight: 700;
}

.kb-tab-item.active::after {
  content: '';
  position: absolute;
  bottom: 4rpx;
  left: 50%;
  transform: translateX(-50%);
  width: 56rpx;
  height: 6rpx;
  background: linear-gradient(135deg, #3B82F6 0%, #60A5FA 100%);
  border-radius: 4rpx;
}

/* ========== 知识统计卡片 ========== */
.kb-stats-wrap {
  padding: 0 28rpx;
  margin-bottom: 22rpx;
}

.kb-stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 14rpx;
}

.kb-stat-card {
  background: #FFFFFF;
  border-radius: 18rpx;
  padding: 24rpx 14rpx;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 10rpx;
  box-shadow: 0 2rpx 12rpx rgba(15, 23, 42, 0.05);
  box-sizing: border-box;
  position: relative;
}

.kb-stat-card.stat-blue { border-top: 5rpx solid #3B82F6; }
.kb-stat-card.stat-red { border-top: 5rpx solid #EF4444; }
.kb-stat-card.stat-cyan { border-top: 5rpx solid #0891B2; }
.kb-stat-card.stat-purple { border-top: 5rpx solid #7C3AED; }
.kb-stat-card.stat-orange { border-top: 5rpx solid #F59E0B; }

.kb-stat-icon {
  font-size: 36rpx;
  line-height: 1;
}

.kb-stat-num {
  font-size: 40rpx;
  font-weight: 800;
  color: #0F172A;
  line-height: 1.1;
  letter-spacing: -1rpx;
}

.kb-stat-label {
  font-size: 22rpx;
  color: #64748B;
  font-weight: 500;
  white-space: nowrap;
}

/* ========== 筛选栏（横向 chip） ========== */
.kb-filter-row {
  margin: 0 28rpx 22rpx;
  background: #FFFFFF;
  border-radius: 18rpx;
  padding: 24rpx 20rpx;
  box-shadow: 0 2rpx 12rpx rgba(15, 23, 42, 0.05);
  box-sizing: border-box;
}

.kb-filter-group {
  margin-bottom: 20rpx;
}

.kb-filter-group:last-child {
  margin-bottom: 0;
}

.kb-filter-title {
  font-size: 24rpx;
  color: #475569;
  font-weight: 600;
  margin-bottom: 14rpx;
  padding-left: 8rpx;
  letter-spacing: 0.5rpx;
}

.kb-filter-scroll {
  white-space: nowrap;
}

.kb-filter-chips {
  display: inline-flex;
  gap: 12rpx;
}

.kb-filter-chip {
  padding: 14rpx 24rpx;
  background: #F8FAFC;
  border-radius: 40rpx;
  border: 2rpx solid #E2E8F0;
  flex-shrink: 0;
  box-sizing: border-box;
}

.kb-filter-chip.active {
  background: linear-gradient(135deg, #3B82F6 0%, #60A5FA 100%);
  border-color: #3B82F6;
  box-shadow: 0 4rpx 12rpx rgba(59, 130, 246, 0.3);
}

.kb-filter-chip-text {
  font-size: 25rpx;
  color: #475569;
  font-weight: 500;
  white-space: nowrap;
}

.kb-filter-chip.active .kb-filter-chip-text {
  color: #FFFFFF;
  font-weight: 700;
}

/* ========== 知识图谱区域 ========== */
.kb-graph-section {
  margin: 0 24rpx 20rpx;
  background: #FFFFFF;
  border-radius: 16rpx;
  padding: 20rpx;
  box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.04);
}

.kb-section-head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  margin-bottom: 16rpx;
  padding-bottom: 12rpx;
  border-bottom: 1rpx solid #F3F4F6;
}

.kb-section-title-wrap {
  display: flex;
  align-items: center;
  gap: 8rpx;
}

.kb-section-icon {
  font-size: 30rpx;
}

.kb-section-title {
  font-size: 30rpx;
  font-weight: 700;
  color: #1F2937;
}

.kb-section-sub {
  font-size: 24rpx;
  color: #6B7280;
}

/* 图例 */
.kb-graph-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
  margin-bottom: 16rpx;
  padding: 12rpx 16rpx;
  background: #F8FAFC;
  border-radius: 10rpx;
}

.kb-legend-item {
  display: flex;
  align-items: center;
  gap: 6rpx;
}

.kb-legend-dot {
  width: 16rpx;
  height: 16rpx;
  border-radius: 50%;
  flex-shrink: 0;
}

.kb-legend-text {
  font-size: 22rpx;
  color: #6B7280;
  white-space: nowrap;
}

/* 图谱画布 */
.kb-graph-canvas-wrap {
  position: relative;
  background: linear-gradient(135deg, #F0F9FF 0%, #F0FDF4 100%);
  border-radius: 12rpx;
  border: 1rpx solid #E0E7FF;
}

.kb-graph-canvas-scroll {
  width: 100%;
  height: 500rpx;
}

.kb-graph-canvas {
  position: relative;
  width: 800rpx;
  height: 520rpx;
}

.kb-graph-line {
  position: absolute;
  height: 3rpx;
  background: #CBD5E1;
  transform-origin: 0 50%;
  border-radius: 2rpx;
}

.kb-graph-node {
  position: absolute;
  width: 100rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6rpx;
  cursor: pointer;
}

.kb-graph-node-icon {
  width: 72rpx;
  height: 72rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.08);
  border: 4rpx solid #FFFFFF;
  transition: transform 0.2s;
}

.kb-graph-node.active .kb-graph-node-icon {
  transform: scale(1.2);
  box-shadow: 0 8rpx 24rpx rgba(59, 130, 246, 0.35);
  border-color: #3B82F6;
}

.kb-graph-node-emoji {
  font-size: 32rpx;
}

.kb-graph-node-label {
  font-size: 22rpx;
  font-weight: 600;
  color: #334155;
  text-align: center;
  background: rgba(255, 255, 255, 0.95);
  padding: 4rpx 8rpx;
  border-radius: 8rpx;
  white-space: nowrap;
  box-shadow: 0 2rpx 4rpx rgba(0, 0, 0, 0.04);
}

.kb-graph-tip {
  position: absolute;
  bottom: 16rpx;
  right: 20rpx;
  background: rgba(59, 130, 246, 0.1);
  padding: 10rpx 16rpx;
  border-radius: 20rpx;
}

.kb-graph-tip-text {
  font-size: 22rpx;
  color: #3B82F6;
  font-weight: 500;
}

/* ========== 节点详情面板 ========== */
.kb-detail-section {
  margin: 0 24rpx 20rpx;
  background: #FFFFFF;
  border-radius: 16rpx;
  padding: 20rpx;
  box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.04);
}

.kb-detail-head {
  display: flex;
  align-items: center;
  gap: 16rpx;
  margin-bottom: 20rpx;
  padding-bottom: 16rpx;
  border-bottom: 1rpx solid #E5E7EB;
}

.kb-detail-icon-wrap {
  width: 88rpx;
  height: 88rpx;
  border-radius: 20rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.kb-detail-icon {
  font-size: 44rpx;
}

.kb-detail-title-wrap {
  flex: 1;
  min-width: 0;
}

.kb-detail-title {
  font-size: 32rpx;
  font-weight: 700;
  color: #1F2937;
  display: block;
  margin-bottom: 8rpx;
}

.kb-detail-meta {
  display: flex;
  gap: 10rpx;
  flex-wrap: wrap;
}

.kb-detail-cat {
  font-size: 22rpx;
  padding: 6rpx 14rpx;
  border-radius: 8rpx;
  font-weight: 600;
}

.kb-detail-status {
  font-size: 22rpx;
  padding: 6rpx 14rpx;
  border-radius: 8rpx;
  font-weight: 600;
}

.kb-detail-status.approved { background: rgba(16, 185, 129, 0.12); color: #059669; }
.kb-detail-status.pending { background: rgba(245, 158, 11, 0.12); color: #D97706; }
.kb-detail-status.updated { background: rgba(59, 130, 246, 0.12); color: #2563EB; }

/* 详情网格 */
.kb-detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14rpx;
  margin-bottom: 20rpx;
}

.kb-detail-cell {
  background: #F8FAFC;
  padding: 16rpx;
  border-radius: 12rpx;
}

.kb-detail-cell.full {
  grid-column: 1 / -1;
}

.kb-detail-cell-title {
  font-size: 24rpx;
  font-weight: 700;
  color: #374151;
  display: block;
  margin-bottom: 10rpx;
}

.kb-detail-cell-value {
  font-size: 26rpx;
  color: #1F2937;
  font-weight: 500;
}

.kb-detail-cell-desc {
  font-size: 24rpx;
  color: #475569;
  line-height: 1.6;
}

.kb-detail-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8rpx;
}

.kb-detail-tag {
  font-size: 22rpx;
  padding: 6rpx 12rpx;
  background: rgba(59, 130, 246, 0.1);
  color: #3B82F6;
  border-radius: 6rpx;
  font-weight: 500;
}

.kb-param-list {
  display: flex;
  flex-direction: column;
  gap: 6rpx;
}

.kb-param-item {
  display: flex;
  justify-content: space-between;
  padding: 8rpx 0;
  border-bottom: 1rpx dashed #E5E7EB;
  font-size: 24rpx;
}

.kb-param-item:last-child {
  border-bottom: none;
}

.kb-param-name {
  color: #6B7280;
}

.kb-param-value {
  color: #3B82F6;
  font-weight: 600;
}

.kb-source-list {
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}

.kb-source-item {
  font-size: 24rpx;
  color: #475569;
  padding-left: 20rpx;
  position: relative;
  line-height: 1.4;
}

.kb-source-item::before {
  content: '📄';
  position: absolute;
  left: -2rpx;
  font-size: 20rpx;
}

.kb-case-list {
  display: flex;
  flex-direction: column;
  gap: 10rpx;
}

.kb-case-item {
  padding: 12rpx;
  background: rgba(124, 58, 237, 0.06);
  border-radius: 8rpx;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.kb-case-item-title {
  font-size: 24rpx;
  color: #1F2937;
  font-weight: 500;
  flex: 1;
  margin-right: 8rpx;
}

.kb-case-item-match {
  font-size: 22rpx;
  color: #7C3AED;
  font-weight: 700;
  flex-shrink: 0;
}

.kb-detail-actions {
  display: flex;
  gap: 12rpx;
}

.kb-detail-action {
  flex: 1;
  padding: 20rpx 0;
  text-align: center;
  background: #F3F4F6;
  border-radius: 12rpx;
  font-size: 26rpx;
  font-weight: 600;
  color: #475569;
}

.kb-detail-action.primary {
  background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
  color: #FFFFFF;
}

.kb-bottom-space {
  height: 200rpx;
}

/* ========== 右下角悬浮入口 ========== */
.kb-fab {
  position: fixed;
  right: 28rpx;
  bottom: 180rpx;
  width: 112rpx;
  height: 112rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8rpx 28rpx rgba(59, 130, 246, 0.5);
  z-index: 600;
}

.kb-fab-icon {
  font-size: 52rpx;
}

/* ========== 助手抽屉 ========== */
.kb-drawer-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(15, 23, 42, 0.5);
  z-index: 999;
  display: flex;
  align-items: flex-end;
}

.kb-drawer {
  width: 100%;
  background: #FFFFFF;
  border-radius: 28rpx 28rpx 0 0;
  padding: 0 24rpx 60rpx;
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.kb-drawer-handle {
  width: 80rpx;
  height: 8rpx;
  background: #E5E7EB;
  border-radius: 6rpx;
  margin: 20rpx auto 8rpx;
}

.kb-drawer-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8rpx 0 20rpx;
  border-bottom: 1rpx solid #F3F4F6;
}

.kb-drawer-title-wrap {
  display: flex;
  flex-direction: column;
  gap: 6rpx;
}

.kb-drawer-title {
  font-size: 34rpx;
  font-weight: 700;
  color: #1F2937;
}

.kb-drawer-subtitle {
  font-size: 24rpx;
  color: #6B7280;
}

.kb-drawer-close {
  width: 64rpx;
  height: 64rpx;
  border-radius: 50%;
  background: #F5F7FA;
  display: flex;
  align-items: center;
  justify-content: center;
}

.kb-drawer-close-icon {
  font-size: 36rpx;
  color: #6B7280;
  font-weight: 600;
}

.kb-drawer-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16rpx;
  padding-top: 10rpx;
}

.kb-drawer-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 28rpx 20rpx;
  background: #F8FAFC;
  border-radius: 20rpx;
  gap: 10rpx;
}

.kb-drawer-icon {
  width: 88rpx;
  height: 88rpx;
  border-radius: 24rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 44rpx;
  margin-bottom: 6rpx;
}

.bg-blue { background: rgba(59, 130, 246, 0.15); }
.bg-green { background: rgba(16, 185, 129, 0.15); }
.bg-orange { background: rgba(245, 158, 11, 0.15); }
.bg-purple { background: rgba(124, 58, 237, 0.15); }

.kb-drawer-item-title {
  font-size: 28rpx;
  font-weight: 700;
  color: #1F2937;
}

.kb-drawer-item-desc {
  font-size: 24rpx;
  color: #6B7280;
  text-align: center;
}

.kb-drawer-tip {
  background: rgba(59, 130, 246, 0.06);
  padding: 18rpx 24rpx;
  border-radius: 12rpx;
  margin-top: 8rpx;
}

.kb-drawer-tip-text {
  font-size: 24rpx;
  color: #3B82F6;
  font-weight: 500;
}
</style>
