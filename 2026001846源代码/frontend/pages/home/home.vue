<template>
  <view class="home-page">
    <view class="browser-shell">
      <view class="browser-topbar">
        <view class="window-dots">
          <text class="dot red"></text>
          <text class="dot amber"></text>
          <text class="dot green"></text>
        </view>
        <view class="address-bar">
          <text class="lock">一修</text>
          <text class="address">yixiu.local / A1 设备检修知识检索与作业系统</text>
        </view>
        <view class="top-actions">
          <text class="top-action" @tap="navigateTo(routes.search)">检索</text>
          <text class="top-action primary" @tap="navigateTo(routes.audit)">核查</text>
        </view>
      </view>

      <view class="workspace">
        <view class="sidebar">
          <view class="brand-block">
            <image src="../../static/equipment.png" class="brand-icon" mode="aspectFit" />
            <view>
              <text class="brand-name">一修</text>
              <text class="brand-subtitle">浏览器式检修工作台</text>
            </view>
          </view>

          <view class="side-section" v-for="group in moduleTree" :key="group.title">
            <text class="side-title">{{ group.title }}</text>
            <view
              v-for="item in group.children"
              :key="item.name"
              class="side-item"
              :class="{ active: item.primary }"
              @tap="navigateTo(item.path)"
            >
              <text class="side-icon">{{ item.icon }}</text>
              <view class="side-copy">
                <text class="side-name">{{ item.name }}</text>
                <text class="side-desc">{{ item.short }}</text>
              </view>
            </view>
          </view>
        </view>

        <scroll-view scroll-y class="main-scroll">
          <view class="main-content">
            <view class="hero-strip">
              <view>
                <text class="hero-kicker">China Software Cup A1</text>
                <text class="hero-title">保留原功能板块的一修网页版分级架构</text>
                <text class="hero-desc">
                  将原系统的检索、任务、知识、社区、个人中心、详情承载等能力拆分为清晰层级，并统一包裹到一修设备检修业务语义中。
                </text>
              </view>
              <view class="hero-actions">
                <view class="action-button main" @tap="navigateTo(routes.search)">进入多模态检索</view>
                <view class="action-button" @tap="navigateTo(routes.tasks)">进入任务工作台</view>
              </view>
            </view>

            <view class="metric-grid">
              <view v-for="item in stats" :key="item.label" class="metric-card">
                <text class="metric-value">{{ item.value }}</text>
                <text class="metric-label">{{ item.label }}</text>
              </view>
            </view>

            <view class="section route-section">
              <view class="section-head">
                <view>
                  <text class="section-kicker">技术路线</text>
                  <text class="section-title">从原系统到一修网页版的实现链路</text>
                </view>
                <text class="section-badge">uni-app H5 · Flask · RAG · 多智能体</text>
              </view>

              <view class="route-lane">
                <view v-for="step in technicalRoute" :key="step.name" class="route-step">
                  <text class="route-index">{{ step.index }}</text>
                  <view class="route-copy">
                    <text class="route-name">{{ step.name }}</text>
                    <text class="route-desc">{{ step.desc }}</text>
                    <text class="route-stack">{{ step.stack }}</text>
                  </view>
                </view>
              </view>
            </view>

            <view class="section module-section">
              <view class="section-head">
                <view>
                  <text class="section-kicker">分级板块图</text>
                  <text class="section-title">原系统功能拆分后一修架构</text>
                </view>
                <text class="section-badge">保留原板块 · 重构为浏览器样式</text>
              </view>

              <view class="hierarchy-map">
                <view class="root-node">
                  <text class="root-title">一修平台</text>
                  <text class="root-subtitle">设备检修知识检索与作业系统</text>
                </view>
                <view class="module-columns">
                  <view v-for="group in moduleTree" :key="group.title" class="module-column">
                    <view class="column-head">
                      <text class="column-index">{{ group.index }}</text>
                      <view>
                        <text class="column-title">{{ group.title }}</text>
                        <text class="column-desc">{{ group.desc }}</text>
                      </view>
                    </view>
                    <view class="child-list">
                      <view
                        v-for="item in group.children"
                        :key="item.name"
                        class="child-node"
                        :class="{ primary: item.primary }"
                        @tap="navigateTo(item.path)"
                      >
                        <text class="child-icon">{{ item.icon }}</text>
                        <view class="child-copy">
                          <text class="child-name">{{ item.name }}</text>
                          <text class="child-origin">{{ item.origin }}</text>
                          <text class="child-desc">{{ item.desc }}</text>
                        </view>
                      </view>
                    </view>
                  </view>
                </view>
              </view>
            </view>

            <view class="lower-grid">
              <view class="section">
                <view class="section-head compact">
                  <view>
                    <text class="section-kicker">原板块迁移</text>
                    <text class="section-title">独立入口清单</text>
                  </view>
                </view>
                <view class="legacy-grid">
                  <view
                    v-for="item in legacyModules"
                    :key="item.name"
                    class="legacy-card"
                    @tap="navigateTo(item.path)"
                  >
                    <text class="legacy-tag">{{ item.layer }}</text>
                    <text class="legacy-name">{{ item.name }}</text>
                    <text class="legacy-desc">{{ item.desc }}</text>
                    <text class="legacy-path">{{ item.path }}</text>
                  </view>
                </view>
              </view>

              <view class="section">
                <view class="section-head compact">
                  <view>
                    <text class="section-kicker">今日现场</text>
                    <text class="section-title">任务与核查</text>
                  </view>
                  <text class="section-link" @tap="navigateTo(routes.tasks)">全部</text>
                </view>
                <view class="task-list">
                  <view v-for="task in tasks" :key="task.title" class="task-card">
                    <view class="task-line" :class="task.level"></view>
                    <view class="task-main">
                      <text class="task-title">{{ task.title }}</text>
                      <text class="task-meta">{{ task.device }} · {{ task.place }}</text>
                    </view>
                    <text class="task-state" :class="task.level">{{ task.state }}</text>
                  </view>
                </view>

                <view class="agent-panel">
                  <view v-for="agent in agents" :key="agent.name" class="agent-card">
                    <image :src="agent.avatar" class="agent-avatar" mode="aspectFill" />
                    <view>
                      <text class="agent-name">{{ agent.name }}</text>
                      <text class="agent-duty">{{ agent.duty }}</text>
                    </view>
                  </view>
                </view>
              </view>
            </view>
          </view>
        </scroll-view>
      </view>
    </view>
  </view>
</template>

<script>
import request from '../../utils/request.js'

const ROUTES = {
  home: '/pages/home/home',
  search: '/pages/repair-search/repair-search',
  tasks: '/pages/repair-tasks/repair-tasks',
  knowledge: '/pages/knowledge-base/knowledge-base',
  audit: '/pages/yixiu-profile/yixiu-profile',
  legacySearch: '/pages/takeaway-expert/takeaway-expert',
  legacyTask: '/pages/health-manager/health-manager',
  legacyRecommend: '/pages/restaurant-recommendation/restaurant-recommendation',
  legacyRecipe: '/pages/recipe-recommendation/recipe-recommendation',
  legacyExpert: '/pages/cooking-expert/cooking-expert',
  personal: '/pages/personal-center/personal-center',
  uploads: '/pages/personal-center/my-uploads',
  profile: '/pages/personal-center/profile-edit',
  achievements: '/pages/personal-center/achievements',
  setup: '/pages/personal-center/initial-setup',
  login: '/pages/user/login',
  openclaw: '/pages/openclaw/openclaw',
  communities: '/pages/nearby-communities/nearby-communities',
  taskDetail: '/pages/task-detail/task-detail',
  knowledgeDetail: '/pages/knowledge-detail/knowledge-detail',
  webview: '/pages/webview/webview'
}

export default {
  data() {
    return {
      routes: ROUTES,
      stats: [
        { label: '在线设备', value: '128' },
        { label: '待处理工单', value: '8' },
        { label: '高风险项', value: '3' },
        { label: '知识条目', value: '156' }
      ],
      moduleTree: [
        {
          index: '01',
          title: '一修核心业务',
          desc: 'A1 赛题主链路',
          children: [
            {
              icon: '检',
              name: '多模态检修知识检索',
              short: '文本/图片/型号联合检索',
              desc: '承接原智能检索能力，面向设备故障、手册、案例和 SOP 统一召回。',
              origin: '新主入口 · 原智能检索能力升级',
              path: ROUTES.search,
              primary: true
            },
            {
              icon: '工',
              name: '检修任务工作台',
              short: '工单、风险、SOP',
              desc: '承接原任务/健康管理式流程，转成检修任务、风险等级和作业闭环。',
              origin: '新主入口 · 原任务板块升级',
              path: ROUTES.tasks,
              primary: true
            },
            {
              icon: '知',
              name: '检修知识库',
              short: '手册/案例/图谱',
              desc: '承接原推荐与资料沉淀能力，形成检修知识库和图谱化沉淀入口。',
              origin: '新主入口 · 原知识推荐能力升级',
              path: ROUTES.knowledge,
              primary: true
            },
            {
              icon: '核',
              name: '项目核查中心',
              short: '智能体与结果核查',
              desc: '新增核查视角，集中展示多智能体职责、报告完整性和交付检查。',
              origin: '新主入口 · A1 核查能力',
              path: ROUTES.audit,
              primary: true
            }
          ]
        },
        {
          index: '02',
          title: '原功能板块',
          desc: '保留并拆开',
          children: [
            {
              icon: '搜',
              name: '原智能问答/识别板块',
              short: '旧检索入口',
              desc: '保留原智能识别与问答页面，作为历史兼容和功能对照入口。',
              origin: '原页面 · takeaway-expert',
              path: ROUTES.legacySearch
            },
            {
              icon: '流',
              name: '原流程管理板块',
              short: '旧任务入口',
              desc: '保留原多标签任务管理页，便于查看旧流程如何迁移到检修工单。',
              origin: '原页面 · health-manager',
              path: ROUTES.legacyTask
            },
            {
              icon: '荐',
              name: '原推荐板块',
              short: '旧推荐入口',
              desc: '保留原推荐页，拆为知识推荐和检修方案推荐的历史来源。',
              origin: '原页面 · restaurant-recommendation',
              path: ROUTES.legacyRecommend
            },
            {
              icon: '专',
              name: '原专家/方案板块',
              short: '旧专家入口',
              desc: '保留原专家与方案生成页，后续可继续迁移成检修专家助手。',
              origin: '原页面 · cooking-expert / recipe',
              path: ROUTES.legacyExpert
            }
          ]
        },
        {
          index: '03',
          title: '协作与账户',
          desc: '用户和现场协同',
          children: [
            {
              icon: '社',
              name: '现场协作社区',
              short: '附近社区/详情',
              desc: '保留原社区能力，用作检修现场协作、经验交流和专家支援。',
              origin: '原页面 · nearby/community',
              path: ROUTES.communities
            },
            {
              icon: '人',
              name: '个人中心',
              short: '账号/上传/成果',
              desc: '保留原账户、资料、成果、上传记录等用户侧能力。',
              origin: '原页面 · personal-center',
              path: ROUTES.personal
            },
            {
              icon: '录',
              name: '我的上传',
              short: '现场资料记录',
              desc: '保留原上传记录页，用作检修图片、报告、案例沉淀记录。',
              origin: '原页面 · my-uploads',
              path: ROUTES.uploads
            }
          ]
        },
        {
          index: '04',
          title: '支撑页面',
          desc: '详情与承载',
          children: [
            {
              icon: '详',
              name: '任务详情',
              short: '工单详情承载',
              desc: '保留原任务详情页，用于检修步骤、处理记录和验收信息展示。',
              origin: '原页面 · task-detail',
              path: ROUTES.taskDetail
            },
            {
              icon: '档',
              name: '知识详情',
              short: '资料详情承载',
              desc: '保留原知识详情页，用于手册条款、案例详情和图谱节点展示。',
              origin: '原页面 · knowledge-detail',
              path: ROUTES.knowledgeDetail
            },
            {
              icon: '器',
              name: 'WebView 与工具页',
              short: '外部内容承载',
              desc: '保留原 WebView、OpenClaw、登录等支撑页面，作为系统基础设施。',
              origin: '原页面 · webview/openclaw/user',
              path: ROUTES.webview
            }
          ]
        }
      ],
      agents: [
        { name: '检索智能体', duty: '理解故障输入并召回资料', avatar: '../../static/assistant-search.png' },
        { name: '作业智能体', duty: '生成标准流程与安全提醒', avatar: '../../static/assistant-maintenance.png' },
        { name: '知识智能体', duty: '审核案例并同步知识图谱', avatar: '../../static/assistant-knowledge.png' },
        { name: '核查智能体', duty: '复核合规性和结果质量', avatar: '../../static/repair-expert.png' }
      ],
      tasks: [
        {
          title: 'CG-125 发动机异响排查',
          device: '发动机总成',
          place: '一号工位',
          state: '进行中',
          level: 'blue'
        },
        {
          title: '点火系统复核',
          device: '火花塞 / 点火线圈',
          place: '二号工位',
          state: '高风险',
          level: 'red'
        },
        {
          title: '燃油供给检查',
          device: '油路 / 化油器',
          place: '三号工位',
          state: '待处理',
          level: 'amber'
        }
      ],
      technicalRoute: [
        {
          index: '前端',
          name: '浏览器工作台',
          desc: '保留 uni-app 页面体系，主交付目标切到 H5，使用桌面端侧边栏、顶部地址栏、内容分栏和模块地图。',
          stack: 'Vue3 / uni-app / H5 / responsive layout'
        },
        {
          index: '接口',
          name: '一修统一编排层',
          desc: '新增 yixiu 后端蓝图，把原任务、知识、AI 能力收束成 overview、search、tasks、knowledge、audit 等网页接口。',
          stack: 'Flask / Blueprint / REST API'
        },
        {
          index: '智能',
          name: '多智能体作业链',
          desc: '按检索、作业、知识、协作、核查拆分智能体职责，让赛题要求能在页面和接口中直接呈现。',
          stack: 'retrieval agent / procedure agent / audit agent'
        },
        {
          index: '知识',
          name: '设备检修知识底座',
          desc: '将摩托车发动机手册、故障案例、SOP 和核查规则沉淀为检修知识库，并优先接入 RAG 检索路径。',
          stack: 'maintenance_knowledge_base.json / RAG / knowledge graph'
        },
        {
          index: '验收',
          name: '网页化核查闭环',
          desc: '通过构建、接口脚本和浏览器断言确认首页、主页面、旧板块入口和接口链路可运行。',
          stack: 'npm build:h5 / API check / browser check'
        }
      ]
    }
  },
  computed: {
    legacyModules() {
      return this.moduleTree
        .flatMap((group) => group.children.map((item) => ({ ...item, layer: group.title })))
        .filter((item) => !item.primary)
    }
  },
  onLoad() {
    this.loadOverview()
  },
  methods: {
    async loadOverview() {
      try {
        const response = await request.get('/overview', { service: 'yixiu' })
        if (!response || response.code !== 200 || !response.data) return

        const data = response.data
        if (data.stats) {
          this.stats = [
            { label: '在线设备', value: String(data.stats.online_equipment || 0) },
            { label: '待处理工单', value: String(data.stats.pending_tasks || 0) },
            { label: '高风险项', value: String(data.stats.high_risk_items || 0) },
            { label: '知识条目', value: String(data.stats.knowledge_items || 0) }
          ]
        }
        if (Array.isArray(data.tasks) && data.tasks.length) {
          this.tasks = data.tasks.slice(0, 3).map((task) => ({
            title: task.title,
            device: `${task.equipment_name || '设备'} ${task.equipment_model || ''}`.trim(),
            place: task.fault_code || '现场工位',
            state: this.getStatusText(task.status),
            level: this.getSeverityTone(task.severity)
          }))
        }
      } catch (_error) {
        // 演示时接口不可用也保留本地数据，避免首页空白。
      }
    },
    getStatusText(status) {
      const map = {
        pending: '待处理',
        in_progress: '进行中',
        completed: '待验收',
        verified: '已闭环',
        rejected: '需返工'
      }
      return map[status] || '待处理'
    },
    getSeverityTone(severity) {
      if (severity === 'high' || severity === 'critical') return 'red'
      if (severity === 'low') return 'blue'
      return 'amber'
    },
    navigateTo(path) {
      if (!path) return
      const tabPages = [
        ROUTES.home,
        ROUTES.search,
        ROUTES.tasks,
        ROUTES.knowledge,
        ROUTES.audit
      ]
      if (tabPages.includes(path)) {
        uni.switchTab({ url: path })
      } else {
        uni.navigateTo({ url: path })
      }
    }
  }
}
</script>

<style scoped>
.home-page {
  --paper: #EEECEA;
  --paper-soft: #F7F5F1;
  --paper-card: #FFFEFA;
  --ink: #111110;
  --ink-soft: #484336;
  --muted: #706D6D;
  --line: #D8D2CA;
  --line-dark: rgba(238, 236, 234, 0.12);
  --gold: #B88A44;
  --gold-soft: #F3E5CC;
  --sage: #6F8067;
  --sage-soft: #E5E9DF;
  --terracotta: #B76345;
  --terracotta-soft: #F4E0D8;
  min-height: 100vh;
  padding: 28rpx;
  background:
    linear-gradient(90deg, rgba(17, 17, 16, 0.045) 1px, transparent 1px),
    linear-gradient(180deg, rgba(17, 17, 16, 0.045) 1px, transparent 1px),
    var(--paper);
  background-size: 46rpx 46rpx;
  box-sizing: border-box;
}

.browser-shell {
  min-height: calc(100vh - 56rpx);
  border: 1rpx solid var(--line);
  border-radius: 24rpx;
  overflow: hidden;
  background: var(--paper-soft);
  box-shadow: 0 28rpx 80rpx rgba(17, 17, 16, 0.16);
}

.browser-topbar,
.workspace,
.window-dots,
.address-bar,
.top-actions,
.brand-block,
.side-item,
.section-head,
.column-head,
.child-node,
.task-card,
.agent-card {
  display: flex;
  align-items: center;
}

.browser-topbar {
  height: 72rpx;
  padding: 0 22rpx;
  gap: 18rpx;
  background: var(--ink);
  border-bottom: 1rpx solid var(--line-dark);
  box-sizing: border-box;
}

.window-dots {
  gap: 10rpx;
  flex-shrink: 0;
}

.dot {
  width: 18rpx;
  height: 18rpx;
  border-radius: 50%;
}

.dot.red { background: #ef4444; }
.dot.amber { background: #f59e0b; }
.dot.green { background: #22c55e; }

.address-bar {
  flex: 1;
  min-width: 0;
  height: 42rpx;
  padding: 0 16rpx;
  gap: 12rpx;
  border-radius: 999rpx;
  background: rgba(238, 236, 234, 0.08);
  color: var(--paper);
}

.lock {
  flex-shrink: 0;
  color: #E8C98F;
  font-size: 20rpx;
  font-weight: 900;
}

.address {
  overflow: hidden;
  color: #C5BFB9;
  font-size: 20rpx;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.top-actions {
  gap: 10rpx;
  flex-shrink: 0;
}

.top-action,
.section-badge,
.section-link {
  border-radius: 999rpx;
  font-weight: 800;
}

.top-action {
  padding: 9rpx 16rpx;
  background: rgba(238, 236, 234, 0.08);
  color: var(--paper);
  font-size: 20rpx;
}

.top-action.primary {
  background: var(--gold);
  color: var(--ink);
}

.workspace {
  align-items: stretch;
  min-height: calc(100vh - 128rpx);
}

.sidebar {
  width: 312rpx;
  flex-shrink: 0;
  padding: 24rpx 18rpx 34rpx;
  background: var(--ink);
  color: var(--paper);
  box-sizing: border-box;
}

.brand-block {
  gap: 14rpx;
  padding: 16rpx 14rpx 24rpx;
  border-bottom: 1rpx solid var(--line-dark);
}

.brand-icon {
  width: 56rpx;
  height: 56rpx;
  border-radius: 16rpx;
  background: var(--paper);
}

.brand-name,
.brand-subtitle,
.side-title,
.side-name,
.side-desc,
.hero-kicker,
.hero-title,
.hero-desc,
.metric-value,
.metric-label,
.section-kicker,
.section-title,
.column-index,
.column-title,
.column-desc,
.child-name,
.child-origin,
.child-desc,
.legacy-tag,
.legacy-name,
.legacy-desc,
.legacy-path,
.task-title,
.task-meta,
.task-state,
.agent-name,
.agent-duty {
  display: block;
}

.brand-name {
  color: var(--paper-card);
  font-size: 30rpx;
  font-weight: 900;
}

.brand-subtitle {
  margin-top: 4rpx;
  color: #C5BFB9;
  font-size: 18rpx;
}

.side-section {
  margin-top: 22rpx;
}

.side-title {
  padding: 0 12rpx 10rpx;
  color: #8D8780;
  font-size: 18rpx;
  font-weight: 900;
}

.side-item {
  gap: 12rpx;
  min-width: 0;
  padding: 13rpx 12rpx;
  border-radius: 14rpx;
}

.side-item.active {
  background: rgba(184, 138, 68, 0.18);
}

.side-icon {
  width: 38rpx;
  height: 38rpx;
  line-height: 38rpx;
  border-radius: 11rpx;
  background: rgba(238, 236, 234, 0.13);
  color: #E8C98F;
  text-align: center;
  font-size: 18rpx;
  font-weight: 900;
  flex-shrink: 0;
}

.side-copy {
  min-width: 0;
}

.side-name {
  color: var(--paper-card);
  font-size: 21rpx;
  font-weight: 800;
}

.side-desc {
  margin-top: 2rpx;
  overflow: hidden;
  color: #B9B1A8;
  font-size: 17rpx;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.main-scroll {
  flex: 1;
  min-width: 0;
  height: calc(100vh - 128rpx);
}

.main-content {
  padding: 28rpx;
  box-sizing: border-box;
}

.hero-strip {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 24rpx;
  padding: 34rpx;
  border-radius: 22rpx;
  color: #ffffff;
  background:
    linear-gradient(135deg, rgba(17, 17, 16, 0.76), rgba(72, 67, 54, 0.58)),
    url('../../static/industrial-banner-1.png') center/cover;
}

.hero-kicker {
  color: #E8C98F;
  font-size: 20rpx;
  font-weight: 900;
}

.hero-title {
  margin-top: 12rpx;
  max-width: 820rpx;
  font-size: 44rpx;
  line-height: 1.15;
  font-weight: 900;
}

.hero-desc {
  margin-top: 14rpx;
  max-width: 900rpx;
  color: rgba(255, 255, 255, 0.82);
  font-size: 23rpx;
  line-height: 1.65;
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
  justify-content: flex-end;
  flex-shrink: 0;
}

.action-button {
  padding: 15rpx 22rpx;
  border: 1rpx solid rgba(255, 255, 255, 0.32);
  border-radius: 14rpx;
  color: #ffffff;
  font-size: 21rpx;
  font-weight: 900;
}

.action-button.main {
  border-color: #ffffff;
  background: #ffffff;
  color: #0f766e;
}

.metric-grid {
  margin-top: 18rpx;
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14rpx;
}

.metric-card,
.section {
  background: var(--paper-card);
  border: 1rpx solid var(--line);
  box-shadow: 0 8rpx 22rpx rgba(17, 17, 16, 0.05);
}

.metric-card {
  min-width: 0;
  padding: 24rpx 18rpx;
  border-radius: 18rpx;
}

.metric-value {
  color: var(--ink);
  font-size: 38rpx;
  font-weight: 900;
}

.metric-label {
  margin-top: 6rpx;
  color: var(--muted);
  font-size: 20rpx;
  font-weight: 800;
}

.section {
  margin-top: 18rpx;
  padding: 24rpx;
  border-radius: 20rpx;
}

.route-section {
  background: var(--ink);
  border-color: #2A2824;
  color: var(--paper);
}

.route-section .section-kicker {
  color: #E8C98F;
}

.route-section .section-title {
  color: var(--paper-card);
}

.route-lane {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 12rpx;
}

.route-step {
  position: relative;
  min-width: 0;
  padding: 18rpx;
  border: 1rpx solid rgba(238, 236, 234, 0.15);
  border-radius: 16rpx;
  background: rgba(72, 67, 54, 0.34);
}

.route-step::after {
  content: '';
  position: absolute;
  top: 34rpx;
  right: -13rpx;
  width: 13rpx;
  height: 1rpx;
  background: rgba(232, 201, 143, 0.55);
}

.route-step:last-child::after {
  display: none;
}

.route-index,
.route-name,
.route-desc,
.route-stack {
  display: block;
}

.route-index {
  width: fit-content;
  padding: 5rpx 10rpx;
  border-radius: 999rpx;
  color: var(--ink);
  background: #E8C98F;
  font-size: 17rpx;
  font-weight: 900;
}

.route-name {
  margin-top: 14rpx;
  color: var(--paper-card);
  font-size: 23rpx;
  line-height: 1.3;
  font-weight: 900;
}

.route-desc {
  margin-top: 8rpx;
  color: #C5BFB9;
  font-size: 18rpx;
  line-height: 1.5;
}

.route-stack {
  margin-top: 12rpx;
  color: #E8C98F;
  font-size: 16rpx;
  line-height: 1.35;
}

.section-head {
  justify-content: space-between;
  gap: 18rpx;
  margin-bottom: 20rpx;
}

.section-head.compact {
  align-items: flex-start;
}

.section-kicker {
  color: var(--gold);
  font-size: 19rpx;
  font-weight: 900;
}

.section-title {
  margin-top: 5rpx;
  color: var(--ink);
  font-size: 30rpx;
  line-height: 1.25;
  font-weight: 900;
}

.section-badge,
.section-link {
  flex-shrink: 0;
  padding: 8rpx 15rpx;
  color: var(--ink-soft);
  background: var(--gold-soft);
  font-size: 20rpx;
}

.hierarchy-map {
  padding: 22rpx;
  border-radius: 18rpx;
  background:
    linear-gradient(90deg, rgba(17, 17, 16, 0.045) 1px, transparent 1px),
    linear-gradient(180deg, rgba(17, 17, 16, 0.045) 1px, transparent 1px),
    var(--paper-soft);
  background-size: 34rpx 34rpx;
}

.root-node {
  width: 360rpx;
  margin: 0 auto 28rpx;
  padding: 22rpx;
  border-radius: 18rpx;
  text-align: center;
  color: #ffffff;
  background: linear-gradient(135deg, var(--ink), var(--ink-soft));
  box-shadow: 0 14rpx 26rpx rgba(17, 17, 16, 0.18);
}

.root-title {
  display: block;
  font-size: 34rpx;
  font-weight: 900;
}

.root-subtitle {
  display: block;
  margin-top: 7rpx;
  color: rgba(255, 255, 255, 0.78);
  font-size: 20rpx;
}

.module-columns {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14rpx;
  align-items: start;
}

.module-column {
  min-width: 0;
  position: relative;
  padding: 16rpx;
  border: 1rpx solid var(--line);
  border-radius: 18rpx;
  background: rgba(255, 254, 250, 0.9);
}

.module-column::before {
  content: '';
  position: absolute;
  top: -28rpx;
  left: 50%;
  width: 1rpx;
  height: 28rpx;
  background: #B9B1A8;
}

.column-head {
  gap: 12rpx;
  padding-bottom: 14rpx;
  border-bottom: 1rpx solid var(--line);
}

.column-index {
  width: 48rpx;
  height: 48rpx;
  line-height: 48rpx;
  border-radius: 13rpx;
  color: #ffffff;
  background: var(--gold);
  text-align: center;
  font-size: 19rpx;
  font-weight: 900;
  flex-shrink: 0;
}

.column-title {
  color: var(--ink);
  font-size: 24rpx;
  font-weight: 900;
}

.column-desc {
  margin-top: 3rpx;
  color: var(--muted);
  font-size: 18rpx;
}

.child-list {
  margin-top: 14rpx;
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

.child-node {
  align-items: flex-start;
  gap: 12rpx;
  min-width: 0;
  padding: 14rpx;
  border-radius: 15rpx;
  border: 1rpx solid var(--line);
  background: var(--paper-card);
}

.child-node.primary {
  border-color: #D9B46B;
  background: #FBF2E3;
}

.child-icon {
  width: 40rpx;
  height: 40rpx;
  line-height: 40rpx;
  border-radius: 12rpx;
  color: var(--ink);
  background: var(--gold-soft);
  text-align: center;
  font-size: 18rpx;
  font-weight: 900;
  flex-shrink: 0;
}

.child-copy {
  min-width: 0;
}

.child-name {
  color: var(--ink);
  font-size: 22rpx;
  font-weight: 900;
  line-height: 1.3;
}

.child-origin {
  margin-top: 5rpx;
  color: var(--gold);
  font-size: 17rpx;
  font-weight: 800;
}

.child-desc {
  margin-top: 6rpx;
  color: var(--muted);
  font-size: 18rpx;
  line-height: 1.45;
}

.lower-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.18fr) minmax(360rpx, 0.82fr);
  gap: 18rpx;
}

.legacy-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14rpx;
}

.legacy-card {
  min-width: 0;
  padding: 18rpx;
  border: 1rpx solid var(--line);
  border-radius: 16rpx;
  background: var(--paper-soft);
}

.legacy-tag {
  width: fit-content;
  padding: 5rpx 10rpx;
  border-radius: 999rpx;
  color: var(--ink-soft);
  background: var(--sage-soft);
  font-size: 17rpx;
  font-weight: 900;
}

.legacy-name {
  margin-top: 12rpx;
  color: var(--ink);
  font-size: 24rpx;
  line-height: 1.35;
  font-weight: 900;
}

.legacy-desc {
  margin-top: 8rpx;
  color: var(--ink-soft);
  font-size: 19rpx;
  line-height: 1.5;
}

.legacy-path {
  margin-top: 12rpx;
  overflow: hidden;
  color: #8D8780;
  font-size: 16rpx;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.task-list,
.agent-panel {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

.task-card {
  padding: 16rpx;
  border-radius: 16rpx;
  background: var(--paper-soft);
  border: 1rpx solid var(--line);
}

.task-line {
  width: 8rpx;
  height: 62rpx;
  border-radius: 999rpx;
  flex-shrink: 0;
}

.task-line.blue { background: var(--sage); }
.task-line.red { background: var(--terracotta); }
.task-line.amber { background: var(--gold); }

.task-main {
  flex: 1;
  min-width: 0;
  margin-left: 14rpx;
}

.task-title {
  color: var(--ink);
  font-size: 23rpx;
  font-weight: 900;
}

.task-meta {
  margin-top: 5rpx;
  color: var(--muted);
  font-size: 18rpx;
}

.task-state {
  flex-shrink: 0;
  margin-left: 10rpx;
  padding: 6rpx 12rpx;
  border-radius: 999rpx;
  font-size: 18rpx;
  font-weight: 900;
}

.task-state.blue { background: var(--sage-soft); color: #4E5E48; }
.task-state.red { background: var(--terracotta-soft); color: var(--terracotta); }
.task-state.amber { background: var(--gold-soft); color: #8A6631; }

.agent-panel {
  margin-top: 18rpx;
  padding-top: 18rpx;
  border-top: 1rpx solid var(--line);
}

.agent-card {
  gap: 12rpx;
  padding: 13rpx;
  border-radius: 15rpx;
  background: var(--paper-soft);
}

.agent-avatar {
  width: 48rpx;
  height: 48rpx;
  border-radius: 13rpx;
  flex-shrink: 0;
}

.agent-name {
  color: var(--ink);
  font-size: 21rpx;
  font-weight: 900;
}

.agent-duty {
  margin-top: 3rpx;
  color: var(--muted);
  font-size: 18rpx;
}

@media screen and (max-width: 1180px) {
  .workspace {
    flex-direction: column;
  }

  .sidebar {
    width: auto;
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 12rpx;
  }

  .brand-block {
    grid-column: 1 / -1;
  }

  .side-section {
    margin-top: 0;
  }

  .main-scroll {
    height: auto;
  }

  .module-columns {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .route-lane {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .route-step::after {
    display: none;
  }

  .lower-grid {
    grid-template-columns: 1fr;
  }
}

@media screen and (max-width: 640px) {
  .home-page {
    padding: 18rpx;
  }

  .browser-topbar {
    height: auto;
    padding: 16rpx;
    flex-wrap: wrap;
  }

  .window-dots {
    display: none;
  }

  .top-actions {
    width: 100%;
    justify-content: flex-end;
  }

  .sidebar,
  .metric-grid,
  .route-lane,
  .module-columns,
  .legacy-grid {
    grid-template-columns: 1fr;
  }

  .hero-strip {
    display: block;
    padding: 26rpx;
  }

  .hero-title {
    font-size: 36rpx;
  }

  .hero-actions {
    justify-content: flex-start;
    margin-top: 20rpx;
  }

  .root-node {
    width: auto;
  }

  .section-head {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
