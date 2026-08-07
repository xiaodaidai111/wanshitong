<template>
  <main class="app-shell" :class="{ collapsed: navCollapsed, 'auth-shell': !isAuthenticated }">
    <section v-if="!isAuthenticated" class="auth-gate">
      <div class="auth-visual">
        <div class="auth-grid" aria-hidden="true"></div>
        <div class="auth-brand">
          <img src="/static/yixiu-logo-full.png" alt="一修" />
          <span>设备检修知识检索与作业系统</span>
        </div>
        <div class="auth-intro">
          <p>面向工业现场的智能检修工作台</p>
          <h1>让每一次检修<br />都有依据、有流程、有沉淀</h1>
          <div class="auth-capabilities">
            <span><b>01</b>多模态故障检索</span>
            <span><b>02</b>标准化作业指导</span>
            <span><b>03</b>检修知识沉淀</span>
          </div>
        </div>
        <p class="auth-footnote">一修 · 智能设备检修知识服务平台</p>
      </div>
      <div class="auth-form-side">
        <form class="auth-card" @submit.prevent="authMode === 'login' ? login() : register()">
          <div class="auth-card-head">
            <p>{{ authMode === 'login' ? '欢迎回来' : '创建工作账号' }}</p>
            <h2>{{ authMode === 'login' ? '登录一修工作台' : '加入一修协作平台' }}</h2>
            <span>{{ authMode === 'login' ? '登录后进入设备检修综合工作台' : '完善基础信息后即可开始协同检修' }}</span>
          </div>
          <div class="auth-tabs" role="tablist">
            <button type="button" :class="{ active: authMode === 'login' }" @click="setAuthMode('login')">账号登录</button>
            <button type="button" :class="{ active: authMode === 'register' }" @click="setAuthMode('register')">注册账号</button>
          </div>
          <div class="auth-fields">
            <label v-if="authMode === 'register'">姓名<input v-model.trim="authForm.name" autocomplete="name" placeholder="请输入真实姓名" /></label>
            <label>账号<input v-model.trim="authForm.account" autocomplete="username" placeholder="请输入账号" /></label>
            <label>密码<input v-model="authForm.password" type="password" autocomplete="current-password" placeholder="请输入密码" /></label>
            <label v-if="authMode === 'register'">确认密码<input v-model="authForm.confirmPassword" type="password" autocomplete="new-password" placeholder="请再次输入密码" /></label>
          </div>
          <p v-if="authError" class="auth-error">{{ authError }}</p>
          <label v-if="authMode === 'login'" class="remember-row"><input v-model="authForm.remember" type="checkbox" />保持登录状态</label>
          <label v-else class="remember-row"><input v-model="authForm.agreed" type="checkbox" />我已阅读并同意平台使用规范</label>
          <button class="auth-submit" type="submit">{{ authMode === 'login' ? '进入工作台' : '完成注册并登录' }}</button>
          <div v-if="authMode === 'login'" class="demo-account"><span>默认演示账号</span><b>账号：yixiu</b><b>密码：Yixiu2026!</b></div>
        </form>
      </div>
    </section>
    <template v-else>
    <div v-if="showSplash" ref="bootScreenRef" class="boot-screen" aria-label="一修系统开屏动画">
      <div class="boot-grid" aria-hidden="true"></div>
      <div class="boot-flow flow-a" aria-hidden="true"></div>
      <div class="boot-flow flow-b" aria-hidden="true"></div>
      <section ref="bootMarkRef" class="boot-mark">
        <img ref="bootLogoRef" src="/static/yixiu-logo-full.png" alt="一修" />
      </section>
    </div>
    <aside class="side-nav">
      <button class="brand" type="button" @click="activePage = 'home'">
        <img ref="brandLogoRef" :src="navCollapsed ? '/static/yixiu-logo-icon.png' : '/static/yixiu-logo-full.png'" alt="一修" />
      </button>

      <nav>
        <button
          v-for="item in navItems"
          :key="item.key"
          type="button"
          :class="{ active: activePage === item.key }"
          @click="switchPage(item.key)"
        >
          <span class="nav-icon">
            <svg class="ui-icon" viewBox="0 0 24 24" aria-hidden="true">
              <path v-for="path in iconParts(item.icon)" :key="path" :d="path"></path>
            </svg>
          </span>
          <b v-if="!navCollapsed">{{ item.label }}</b>
        </button>
      </nav>

      <button class="collapse-btn" type="button" @click="navCollapsed = !navCollapsed">
        {{ navCollapsed ? '»' : '« 收起导航' }}
      </button>
    </aside>

    <section class="workspace">
      <header class="topbar">
        <div :class="['page-title-block', `title-${activePage}`]">
          <p class="breadcrumb">一修 / {{ currentNav.label }}</p>
          <h1>{{ currentNav.title }}</h1>
        </div>
        <form class="global-search" @submit.prevent="runGlobalSearch">
          <span>
            <svg class="ui-icon" viewBox="0 0 24 24" aria-hidden="true">
              <path v-for="path in iconParts('search')" :key="path" :d="path"></path>
            </svg>
          </span>
          <input v-model="globalKeyword" placeholder="搜索工单、设备、资料、联系人" />
          <button type="submit" aria-label="全局搜索">搜索</button>
        </form>
        <div class="work-strip">
          <span>待办 {{ overview.stats.pending }}</span>
          <span>待复检 {{ overview.stats.review }}</span>
          <span class="bad">高风险 {{ overview.stats.highRisk }}</span>
        </div>
        <button class="icon-button" type="button" @click="toast('暂无未读消息')" aria-label="消息提醒">
          <svg class="ui-icon" viewBox="0 0 24 24" aria-hidden="true">
            <path v-for="path in iconParts('bell')" :key="path" :d="path"></path>
          </svg>
        </button>
        <button class="user-chip" type="button" @click="activePage = 'profile'">
          <img :src="user.avatar" alt="" />
          <span>{{ user.name }}</span>
        </button>
        <button class="topbar-logout" type="button" @click="logout" title="安全退出当前账号">
          <svg class="ui-icon" viewBox="0 0 24 24" aria-hidden="true">
            <path d="M10 17l5-5-5-5"></path>
            <path d="M15 12H3"></path>
            <path d="M14 4h4a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2h-4"></path>
          </svg>
          <span>退出登录</span>
        </button>
      </header>

      <div class="content-shell" :style="{ '--operator-width': `${operatorWidth}px` }">
      <section class="page-scroll">
        <section v-if="activePage === 'home'" class="page-grid">
          <div class="welcome-card span-8">
            <div class="welcome-brand">
              <img src="/static/yixiu-logo-full.png" alt="一修系统 Logo" />
              <div>
                <p class="eyebrow">我的今日工作</p>
                <h2>{{ user.name }}，今天重点处理 {{ overview.stats.pending + overview.stats.inProgress + overview.stats.review }} 项检修工作</h2>
                <p>{{ nowText }}，{{ user.department }}。请优先确认高风险、即将逾期和待复检任务。</p>
              </div>
            </div>
            <div class="execution-summary">
              <div class="progress-ring" :style="{ '--progress': `${todayCompletion}%` }">
                <span><b>{{ todayCompletion }}%</b>今日完成率</span>
              </div>
              <div class="execution-copy">
                <strong>今日执行进度</strong>
                <p>已完成 {{ overview.stats.completed }} 项，仍有 {{ overview.stats.pending + overview.stats.inProgress + overview.stats.review }} 项需要推进。</p>
              </div>
              <div class="summary-metric"><b>{{ overview.stats.highRisk }}</b><span>高风险待确认</span></div>
              <div class="summary-metric"><b>{{ overview.stats.weekKnowledge }}</b><span>本周知识沉淀</span></div>
            </div>
            <div class="health-grid">
              <span>待接收：{{ overview.stats.pending }} 项</span>
              <span>进行中：{{ overview.stats.inProgress }} 项</span>
              <span>待复检：{{ overview.stats.review }} 项</span>
              <span>今日完成：{{ overview.stats.completed }} 项</span>
              <span>需确认：{{ overview.stats.highRisk }} 项高风险</span>
            </div>
            <div class="focus-tasks">
              <div class="focus-tasks-title"><b>今日重点</b><span>按风险与时限排序</span></div>
              <button v-for="task in priorityTasks.slice(0, 3)" :key="task.id" type="button" @click="openTask(task)">
                <span><b>{{ task.equipment_name }}</b><small>{{ task.fault_type }} · {{ task.current_step }}</small></span>
                <i :class="['badge', task.severity]">{{ severityText(task.severity) }}</i>
                <em>{{ task.progress }}%</em>
              </button>
            </div>
          </div>

          <div class="agent-card span-4">
            <div class="panel-head agent-card-head">
              <div><p class="eyebrow">器灵协作台</p><h3>六个智能体分工在线</h3></div>
              <small>点击切换</small>
            </div>
            <button v-for="agent in agents" :key="agent.id" :class="['agent-row', { active: selectedAgentId === agent.id }]" type="button" @click="focusAgent(agent)">
              <img :src="agent.avatar" :alt="agent.name" @error="handleAvatarError" />
              <span :class="['dot', agent.status]"></span>
              <div>
                <b>{{ agent.name }}</b>
                <small>{{ agent.role }} · {{ agent.lastResult || agent.duty }}</small>
              </div>
              <i>→</i>
            </button>
          </div>

          <section class="kpi-ribbon span-all" aria-label="核心运行指标">
            <button
              v-for="card in statCards.slice(0, 6)"
              :key="card.key"
              class="stat-card"
              type="button"
              @click="goStat(card)"
            >
              <span>{{ card.label }}</span>
              <b>{{ card.value }}</b>
              <small>{{ card.hint }}</small>
            </button>
          </section>

          <div class="panel home-task-panel span-8">
            <div class="section-title-row home-task-title">
              <div>
                <p class="eyebrow">今日任务摘要</p>
                <h3>需要处理的检修工单</h3>
              </div>
              <div class="task-title-actions"><span>{{ visibleTodayTasks.length }} 项任务</span><button class="ghost" type="button" @click="activePage = 'tasks'">查看全部 →</button></div>
            </div>
            <div class="home-task-list">
              <button v-for="task in visibleTodayTasks" :key="task.id" class="home-task-row" type="button" @click="openTask(task)">
                <span class="task-device-block">
                  <small>{{ task.workOrderNo }}</small>
                  <b>{{ task.equipment_name }}</b>
                  <em>{{ task.equipment_no }} · {{ task.equipment_model }}</em>
                </span>
                <span class="task-fault-block">
                  <small>故障类型</small>
                  <b>{{ task.fault_type }}</b>
                  <i :class="['badge', task.severity]">{{ severityText(task.severity) }}</i>
                </span>
                <span class="task-owner-block">
                  <i>{{ task.assignee_name.slice(0, 1) }}</i>
                  <span><small>负责人</small><b>{{ task.assignee_name }}</b></span>
                </span>
                <span class="task-progress-block">
                  <span><b>{{ statusText(task.status) }}</b><em>{{ task.progress }}%</em></span>
                  <i><u :style="{ width: `${task.progress}%` }"></u></i>
                  <small>{{ task.current_step }}</small>
                </span>
                <span class="row-arrow">→</span>
              </button>
            </div>
          </div>

          <div class="panel quick-panel span-4">
            <div class="section-title-row quick-panel-title"><div><p class="eyebrow">快捷入口</p><h3>常用操作</h3></div><span class="quiet-label">8 项</span></div>
            <div class="quick-grid home-quick-grid">
              <button v-for="item in quickActions" :key="item.label" :class="`quick-${item.tone}`" type="button" @click="runQuickAction(item)">
                <span class="quick-icon"><svg class="ui-icon" viewBox="0 0 24 24" aria-hidden="true"><path v-for="path in iconParts(item.icon)" :key="path" :d="path"></path></svg></span>
                <span class="quick-copy"><b>{{ item.label }}</b><small>{{ item.desc }}</small></span>
                <i>→</i>
              </button>
            </div>
          </div>

          <div class="panel alert-panel span-4">
            <div class="section-title-row">
              <div><p class="eyebrow">风险与异常</p><h3>需要关注的事项</h3></div>
              <span class="section-count">{{ alerts.length }} 项</span>
            </div>
            <div class="alert-list">
              <button v-for="alert in alerts" :key="alert.title" :class="`tone-${alert.tone}`" type="button" @click="runAlert(alert)">
                <span class="alert-icon">
                  <svg class="ui-icon" viewBox="0 0 24 24" aria-hidden="true"><path v-for="path in iconParts(alert.icon)" :key="path" :d="path"></path></svg>
                </span>
                <span class="alert-copy"><b>{{ alert.title }}</b><small>{{ alert.desc }}</small></span>
                <span class="alert-arrow">→</span>
              </button>
            </div>
          </div>

          <div class="panel analytics-panel span-8">
            <div class="panel-head">
              <div>
                <p class="eyebrow">数据分析</p>
                <h3>最近七天任务趋势与故障分布</h3>
              </div>
              <div class="chart-legend"><i></i>任务处理量 <span>近 7 天</span></div>
            </div>
            <div class="chart-wrap">
              <svg viewBox="0 0 700 260" aria-label="任务趋势">
                <defs>
                  <linearGradient id="barGradient" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#68a8c6"/><stop offset="1" stop-color="#b8d4de"/></linearGradient>
                  <linearGradient id="areaGradient" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#147b73" stop-opacity=".2"/><stop offset="1" stop-color="#147b73" stop-opacity="0"/></linearGradient>
                </defs>
                <line v-for="y in [44, 88, 132, 176, 220]" :key="y" x1="16" :y1="y" x2="676" :y2="y" class="chart-grid-line" />
                <polygon :points="`24,220 ${trendPoints} 624,220`" fill="url(#areaGradient)" />
                <g v-for="(value, index) in overview.trend" :key="index">
                  <rect :x="index * 100 + 8" :y="220 - value * 8" width="32" :height="value * 8" rx="8" fill="url(#barGradient)" />
                  <text :x="index * 100 + 24" y="246" text-anchor="middle" class="chart-label">{{ trendLabels[index] }}</text>
                  <circle :cx="index * 100 + 24" :cy="220 - value * 8" r="5" class="trend-dot" />
                </g>
                <polyline fill="none" stroke="#147b73" stroke-width="3" :points="trendPoints" />
              </svg>
              <div class="distribution">
                <div class="distribution-head"><b>故障构成</b><small>按案例占比</small></div>
                <span v-for="(item, index) in overview.faultDistribution" :key="item.label" :style="{ '--dist-color': faultColors[index] }">
                  <i></i><em>{{ item.label }}</em><strong>{{ item.value }}%</strong><b><u :style="{ width: `${item.value}%` }"></u></b>
                </span>
              </div>
            </div>
          </div>

          <div class="panel activity-panel span-5">
            <div class="section-title-row"><div><p class="eyebrow">工作轨迹</p><h3>最近使用记录</h3></div><span class="quiet-label">今天</span></div>
            <div class="activity-list">
              <button v-for="item in recentActivities" :key="item.raw" :class="`activity-${item.tone}`" type="button" @click="runRecentActivity(item)">
                <span class="activity-icon">
                  <svg class="ui-icon" viewBox="0 0 24 24" aria-hidden="true"><path v-for="path in iconParts(item.icon)" :key="path" :d="path"></path></svg>
                </span>
                <span><small>{{ item.action }}</small><b>{{ item.content }}</b></span>
                <i>→</i>
              </button>
            </div>
          </div>

          <div class="panel knowledge-recent-panel span-7">
            <div class="section-title-row"><div><p class="eyebrow">知识沉淀</p><h3>最近知识资料</h3></div><button class="text-link" type="button" @click="goStat({ page: 'knowledge', panel: 'library' })">查看资料库 →</button></div>
            <div class="knowledge-recent-grid">
              <button v-for="(item, index) in knowledge.slice(0, 4)" :key="item.id" :style="{ '--knowledge-accent': knowledgeColors[index] }" type="button" @click="openKnowledge(item)">
                <span class="knowledge-file-icon">{{ item.fileType || 'DOC' }}</span>
                <span class="knowledge-card-copy"><b>{{ item.title }}</b><small>{{ item.equipment }} · {{ item.updated_at }}</small><em>{{ item.type || item.category }}</em></span>
                <span class="citation-count">引用 {{ item.citations || 0 }}</span>
              </button>
            </div>
          </div>
        </section>

        <section v-else-if="activePage === 'search'" class="two-column search-workbench">
          <div class="panel search-input-panel">
            <div class="search-panel-heading">
              <span class="search-step">01</span>
              <div><p class="eyebrow">多模态输入</p><h3>填写设备与故障信息</h3><small>支持设备参数、现象描述、现场图片和维修资料组合检索</small></div>
            </div>
            <div class="form-grid">
              <label>设备名称<input v-model="searchForm.deviceName" placeholder="如：摩托车发动机总成" /></label>
              <label>设备型号<input v-model="searchForm.deviceModel" placeholder="如：CG-125" /></label>
              <label>故障代码<input v-model="searchForm.faultCode" placeholder="如：NOISE-02" /></label>
              <label>设备类别<select v-model="searchForm.category"><option>发动机</option><option>电气系统</option><option>液压系统</option><option>点火系统</option></select></label>
              <label>故障类型<select v-model="searchForm.faultType"><option>异响</option><option>过热</option><option>渗漏</option><option>点火故障</option></select></label>
              <label>检修等级<select v-model="searchForm.maintenanceLevel"><option>一级巡检</option><option>二级检修</option><option>三级大修</option></select></label>
              <label class="wide">故障现象<textarea v-model="searchForm.query" placeholder="描述现场现象、声音、报警、温度、图片观察结果"></textarea></label>
            </div>
            <div class="upload-zone search-upload-zone" @dragover.prevent @drop.prevent="addDroppedFiles">
              <input ref="searchFileInput" type="file" multiple accept="image/*,.pdf,.doc,.docx,.xls,.xlsx,.csv,.txt,.md,.mp4,.webm" @change="addFiles($event, 'search')" />
              <span class="upload-mark"><svg class="ui-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 16V4M7.5 8.5 12 4l4.5 4.5M5 14v4a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-4"></path></svg></span>
              <span class="upload-copy"><b>添加现场证据与检修资料</b><small>图片将进行视觉识别，文档用于跨模态知识匹配</small></span>
              <button type="button" @click="$refs.searchFileInput.click()">选择文件</button>
            </div>
            <div class="file-pills">
              <span v-for="file in searchFiles" :key="file.localId">
                <img v-if="file.type === '图片'" :src="file.url" :alt="file.name" />
                {{ file.name }} · {{ file.sizeText }} · {{ file.status }}<template v-if="file.progress"> {{ file.progress }}%</template>
                <button type="button" @click="removeSearchFile(file.localId)">删除</button>
              </span>
            </div>
            <div class="actions search-actions">
              <button class="primary" type="button" :disabled="loading.search" @click="runSearch">{{ loading.search ? '检索中...' : '开始智能检索' }}</button>
              <button type="button" @click="simulateVoice">{{ voiceListening ? '停止语音输入' : '语音输入故障描述' }}</button>
            </div>
          </div>

          <div class="panel search-analysis-panel" :class="{ ready: searchResult }">
            <div class="search-panel-heading compact-heading">
              <span class="search-step">02</span>
              <div><p class="eyebrow">智能分析结果</p><h3>{{ searchResult ? '故障研判摘要' : '等待检索分析' }}</h3><small>{{ searchResult ? '综合文本、设备参数与视觉线索生成' : '完成左侧信息后生成结构化判断' }}</small></div>
            </div>
            <template v-if="searchResult">
              <div class="analysis-summary"><span>研判结论</span><h3>{{ searchResult.phenomenonSummary }}</h3></div>
              <div class="analysis-grid">
                <span>风险等级：{{ severityText(searchResult.risk) }}</span>
                <span>置信度：{{ searchResult.confidence }}%</span>
                <span>建议：{{ searchResult.stopAdvice }}</span>
              </div>
              <div class="tag-line modality-line"><span v-for="mode in searchResult.modalities" :key="mode">{{ modalityText(mode) }}</span></div>
              <template v-if="searchResult.visualFindings?.length">
                <h4>图片识别线索</h4>
                <ul><li v-for="item in searchResult.visualFindings" :key="item">{{ item }}</li></ul>
              </template>
              <h4>可能原因</h4>
              <ul><li v-for="item in searchResult.causes" :key="item">{{ item }}</li></ul>
              <h4>推荐检查位置 / 工具</h4>
              <p>{{ searchResult.positions.join('、') }}；工具：{{ searchResult.tools.join('、') }}</p>
            </template>
            <div v-else class="empty search-empty-state">
              <span class="analysis-orbit"><i></i><i></i><i></i><b>AI</b></span>
              <h4>检索结果将在这里生成</h4>
              <p>系统会结合设备型号、故障现象和上传材料，给出风险、原因与检查建议。</p>
              <ol><li><b>1</b>完善故障描述</li><li><b>2</b>按需添加图片或资料</li><li><b>3</b>启动智能检索</li></ol>
            </div>
          </div>

          <div class="panel span-all search-results-panel">
            <div class="panel-head">
              <div>
                <p class="eyebrow">03 · 检索结果分类</p>
                <h3>维修手册、案例、SOP、安全规范与知识节点</h3>
                <small class="result-tab-hint">{{ resultTabHint }}</small>
              </div>
              <div class="tabs">
                <button v-for="tab in resultTabs" :key="tab" type="button" :class="{ active: resultTab === tab }" @click="selectResultTab(tab)">{{ tab }}<em>{{ resultCountFor(tab) }}</em></button>
              </div>
            </div>
            <div v-if="filteredResults.length" class="result-grid">
              <article v-for="item in filteredResults" :key="item.id" class="result-card">
                <div>
                  <b>{{ item.title }}</b>
                  <small>{{ item.type }} · {{ item.equipment }} · {{ item.model }} · 匹配度 {{ item.match }}%</small>
                  <p>{{ item.summary }}</p>
                </div>
                <div class="tag-line"><span v-for="tag in item.tags" :key="tag">{{ tag }}</span></div>
                <div class="card-actions">
                  <button type="button" @click="openKnowledge(item)">详情</button>
                  <button v-if="item.id !== 'recommendation-current'" type="button" @click="previewFile(files[0])">预览原文件</button>
                  <button type="button" @click="toast('已复制引用')">复制引用</button>
                  <button type="button" @click="createTaskFromSearch(item)">加入检修任务</button>
                </div>
              </article>
            </div>
            <div v-else class="result-filter-empty"><b>当前分类暂无匹配结果</b><span>可以切换到“全部”，或调整设备型号和故障描述后重新检索。</span><button type="button" @click="selectResultTab('全部')">查看全部结果</button></div>
          </div>

          <div class="panel span-all maintenance-advice-panel" v-if="searchResult">
            <div class="advice-heading"><div><p class="eyebrow">智能检修建议</p><h3>推荐作业路径</h3></div><span>{{ searchResult.suggestion.steps.length }} 个步骤</span></div>
            <div class="sop-list">
              <span v-for="(step, index) in searchResult.suggestion.steps" :key="step"><b>{{ index + 1 }}</b>{{ step }}</span>
            </div>
            <p class="advice-reference"><b>引用依据</b>{{ searchResult.references.slice(0, 3).map((item) => item.title).join('、') }}</p>
          </div>
        </section>

        <section v-else-if="activePage === 'tasks'" class="page-grid tasks-page">
          <div class="panel span-all task-nav-panel">
            <div class="panel-head">
              <div>
                <p class="eyebrow">检修任务</p>
                <h3>检修任务闭环中心</h3>
                <small>从任务接收、标准作业到复检验收与协作沟通</small>
              </div>
              <div class="tabs">
                <button v-for="tab in taskTabs" :key="tab.key" type="button" :class="{ active: taskPanel === tab.key }" @click="taskPanel = tab.key">{{ tab.label }}</button>
              </div>
            </div>
          </div>

          <template v-if="taskPanel === 'overview'">
            <button v-for="card in taskOverviewCards" :key="card.label" class="stat-card task-stat" type="button" @click="applyTaskMetric(card)">
              <span>{{ card.label }}</span><b>{{ card.value }}</b><small>{{ card.hint }}</small>
            </button>
            <div class="panel span-all task-analytics">
              <div class="panel-head">
                <div><p class="eyebrow">数据分析</p><h3>任务趋势、状态、风险、设备和人员负载</h3></div>
                <button type="button" @click="toast('已展开更多分析：平均检修时长、按时完成率、返工数量、高频故障设备')">查看更多分析</button>
              </div>
              <div class="analysis-cards">
                <section>
                  <div class="trend-card-head"><b>近 7 天任务趋势</b><span>累计 {{ taskTrendTotal }} 项</span></div>
                  <div class="trend-summary"><strong>{{ taskTrendData.at(-1) }}</strong><span>今日处理量</span><em :class="{ down: taskTrendChange < 0 }">{{ taskTrendChange >= 0 ? '↑' : '↓' }} {{ Math.abs(taskTrendChange) }} 较昨日</em></div>
                  <svg viewBox="0 0 320 176" aria-label="近7天任务趋势" class="task-trend-chart">
                    <defs><linearGradient id="taskTrendArea" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2f8794" stop-opacity=".28"/><stop offset="1" stop-color="#2f8794" stop-opacity=".02"/></linearGradient></defs>
                    <line v-for="y in [44, 84, 124]" :key="y" x1="28" :y1="y" x2="304" :y2="y" class="task-trend-grid" />
                    <polygon :points="taskTrendAreaPoints" fill="url(#taskTrendArea)" />
                    <polyline :points="taskTrendPoints" fill="none" stroke="#2f7f8f" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" />
                    <g v-for="(point, index) in taskTrendDots" :key="point.x">
                      <circle :cx="point.x" :cy="point.y" r="6" class="task-trend-dot" />
                      <text :x="point.x" :y="point.y - 12" text-anchor="middle" class="task-trend-value">{{ taskTrendData[index] }}</text>
                      <text :x="point.x" y="158" text-anchor="middle" class="task-trend-label">{{ trendLabels[index] }}</text>
                    </g>
                  </svg>
                </section>
                <section>
                  <b>任务状态占比</b>
                  <button v-for="item in taskStatusAnalysis" :key="item.key" type="button" class="bar-row" @click="filterTaskBy('status', item.key)">
                    <span>{{ item.label }}</span><i :style="{ width: `${item.percent}%` }"></i><em>{{ item.count }}</em>
                  </button>
                </section>
                <section>
                  <b>风险等级分布</b>
                  <button v-for="item in taskRiskAnalysis" :key="item.key" type="button" class="bar-row risk" @click="filterTaskBy('severity', item.key)">
                    <span>{{ item.label }}</span><i :class="item.key" :style="{ width: `${item.percent}%` }"></i><em>{{ item.count }}</em>
                  </button>
                </section>
                <section>
                  <b>设备类型与故障排行</b>
                  <button v-for="item in taskCategoryAnalysis" :key="item.key" type="button" class="chip-row" @click="filterTaskBy('category', item.key)">{{ item.label }} <em>{{ item.count }}</em></button>
                  <button v-for="item in faultRankAnalysis" :key="item.key" type="button" class="chip-row warm" @click="filterTaskBy('faultType', item.key)">{{ item.label }} <em>{{ item.count }}</em></button>
                </section>
              </div>
            </div>
            <div class="panel span-all priority-panel">
              <p class="eyebrow">重点任务</p>
              <div class="priority-list">
                <article v-for="task in priorityTasks" :key="task.id">
                  <header class="priority-task-top">
                    <div><small>{{ task.workOrderNo }}</small><b>{{ task.equipment_name }}</b></div>
                    <span><i :class="['badge', task.severity]">{{ severityText(task.severity) }}</i><em>{{ statusText(task.status) }}</em></span>
                  </header>
                  <p class="priority-task-desc">{{ task.description }}</p>
                  <div class="priority-task-meta">
                    <span><small>设备编号</small><b>{{ task.equipment_no }}</b></span>
                    <span><small>负责人</small><b>{{ task.assignee_name }}</b></span>
                    <span><small>协作人员</small><b>{{ task.collaborators?.join('、') || '待分配' }}</b></span>
                  </div>
                  <div class="priority-task-progress">
                    <div><span :style="{ width: `${task.progress}%` }"></span></div>
                    <b>{{ task.progress }}%</b>
                  </div>
                  <footer><span><small>当前步骤</small><b>{{ task.current_step }}</b><em>剩余 {{ remainingTime(task) }}</em></span><button type="button" @click="openTask(task)">查看详情 <i>→</i></button></footer>
                </article>
              </div>
            </div>
            <div class="panel span-all task-event-panel">
              <div class="task-event-heading"><div><p class="eyebrow">任务动态</p><h3>现场进展与节点记录</h3></div><span>{{ taskEvents.length }} 条记录</span></div>
              <div class="timeline task-events"><article v-for="event in taskEvents" :key="event.id"><i></i><time>{{ event.time }}</time><p>{{ event.text }}</p></article></div>
            </div>
          </template>

          <template v-if="taskPanel === 'manage'">
            <div class="panel span-all task-manage-panel">
              <div class="filters">
                <select v-model="taskFilters.status"><option value="all">全部状态</option><option value="pending">待处理</option><option value="in_progress">检修中</option><option value="review">待复检</option><option value="completed">已完成</option></select>
                <select v-model="taskFilters.severity"><option value="all">全部风险</option><option value="low">低</option><option value="medium">中</option><option value="high">高</option></select>
                <select v-model="taskFilters.category"><option value="all">全部设备类型</option><option v-for="item in taskCategoryAnalysis" :key="item.key" :value="item.key">{{ item.label }}</option></select>
                <select v-model="taskFilters.faultType"><option value="all">全部故障类型</option><option v-for="item in faultRankAnalysis" :key="item.key" :value="item.key">{{ item.label }}</option></select>
                <input v-model="taskFilters.keyword" placeholder="搜索设备/负责人/型号/协作人员" />
                <div class="view-switch"><button type="button" :class="{ active: taskView === 'table' }" @click="taskView = 'table'">表格</button><button type="button" :class="{ active: taskView === 'board' }" @click="taskView = 'board'">看板</button></div>
                <button class="primary" type="button" @click="showTaskForm = true">新建检修任务</button>
              </div>
              <div v-if="taskView === 'table'" class="table">
                <div class="tr head"><span>工单</span><span>设备</span><span>故障描述</span><span>风险</span><span>负责人</span><span>步骤</span><span>状态</span><span>操作</span></div>
                <div v-for="task in filteredTasks" :key="task.id" class="tr">
                  <span>{{ task.workOrderNo }}</span>
                  <span>{{ task.equipment_name }}<small>{{ task.equipment_model }}</small></span>
                  <span>{{ task.description }}</span>
                  <span><i :class="['badge', task.severity]">{{ severityText(task.severity) }}</i></span>
                  <span>{{ task.assignee_name }}</span>
                  <span>{{ task.current_step }} · {{ task.progress }}%</span>
                  <span>{{ statusText(task.status) }}</span>
                  <span class="inline-actions task-row-actions">
                    <button class="task-row-action detail" type="button" @click="openTask(task)"><span>查看</span><b>详情</b></button>
                    <button class="task-row-action flow" type="button" :disabled="task.status === 'completed'" @click="handleTaskPrimary(task)"><span>{{ task.status === 'review' ? '进入' : '任务' }}</span><b>{{ task.status === 'review' ? '复检' : '流转' }}</b></button>
                  </span>
                </div>
              </div>
              <div v-else class="task-board">
                <section v-for="column in taskBoardColumns" :key="column.key">
                  <h4>{{ column.label }} <small>{{ column.tasks.length }}</small></h4>
                  <article v-for="task in column.tasks" :key="task.id" @click="openTask(task)">
                    <b>{{ task.equipment_name }}</b>
                    <small>{{ task.workOrderNo }} · {{ task.fault_type }}</small>
                    <span><i :class="['badge', task.severity]">{{ severityText(task.severity) }}</i>{{ task.progress }}%</span>
                  </article>
                </section>
              </div>
            </div>
          </template>

          <template v-if="taskPanel === 'recheck'">
            <div class="panel span-all recheck-panel">
              <div class="recheck-heading"><div><p class="eyebrow">复检评估</p><h3>质量验收与闭环确认</h3></div><span>{{ recheckTasks.length }} 项待核查</span></div>
              <div class="recheck-grid">
                <article v-for="task in recheckTasks" :key="task.id" class="result-card recheck-card" :class="{ warning: recheckForms[task.id].result !== '通过' }">
                  <div class="recheck-card-head">
                    <span class="recheck-mark" aria-hidden="true">
                      <svg class="ui-icon" viewBox="0 0 24 24"><path v-for="path in iconParts('check')" :key="path" :d="path"></path></svg>
                    </span>
                    <div><b>{{ task.title }}</b><small>{{ task.equipment_name }} · {{ task.current_step }}</small></div>
                    <strong>{{ task.progress }}%</strong>
                  </div>
                  <div class="recheck-meta">
                    <span><small>工单编号</small><b>{{ task.workOrderNo }}</b></span>
                    <span><small>负责人</small><b>{{ task.assignee_name }}</b></span>
                    <span><small>当前状态</small><b>{{ statusText(task.status) }}</b></span>
                  </div>
                  <label class="recheck-field">
                    <span>验收结论</span>
                    <div class="recheck-select-wrap">
                      <select v-model="recheckForms[task.id].result"><option>通过</option><option>限期整改</option><option>返工</option><option>不通过</option></select>
                    </div>
                  </label>
                  <label class="recheck-field">
                    <span>复检记录</span>
                    <textarea v-model.trim="recheckForms[task.id].comment" placeholder="填写复测数据、安全检查结果和复检意见"></textarea>
                  </label>
                  <div class="recheck-card-footer">
                    <span><i></i>{{ recheckForms[task.id].comment ? '复检信息已填写' : '请核对数据后保存' }}</span>
                    <button class="primary" type="button" @click="saveRecheck(task)">保存复检结果</button>
                  </div>
                </article>
              </div>
            </div>
          </template>

          <template v-if="taskPanel === 'contacts'">
            <div class="panel span-all chat-workbench">
              <aside class="conversation-list">
                <div class="chat-search"><input v-model="contactKeyword" placeholder="搜索姓名、部门、设备专业、任务编号" /></div>
                <button v-for="session in filteredConversations" :key="session.id" type="button" :class="{ active: activeConversationId === session.id }" @click="activeConversationId = session.id">
                  <img :src="avatarFor(session.avatar, session.name)" :alt="session.name" @error="handleContactAvatarError($event, session.name)" />
                  <span><b>{{ session.name }}</b><small>{{ session.position }} · {{ session.lastMessage }}</small></span>
                  <i v-if="session.unread">{{ session.unread }}</i>
                </button>
              </aside>
              <section class="chat-main">
                <header class="chat-title">
                  <div>
                    <p class="eyebrow">{{ activeConversation?.taskNo || '检修协作' }}</p>
                    <h3>{{ activeConversation?.name }}</h3>
                  </div>
                  <span v-if="activeConversation?.risk" :class="['badge', activeConversation.risk]">{{ severityText(activeConversation.risk) }}</span>
                  <button type="button" @click="summarizeConversation">总结重点</button>
                  <button type="button" @click="requestSupport">请求支援</button>
                </header>
                <div class="chat-messages">
                  <article v-for="message in activeMessages" :key="message.id" :class="['message', message.mine ? 'mine' : 'peer']">
                    <img v-if="!message.mine" :src="avatarFor(activeConversation?.avatar, activeConversation?.name)" :alt="activeConversation?.name" @error="handleContactAvatarError($event, activeConversation?.name)" />
                    <div>
                      <p>{{ message.text }}</p>
                      <img v-if="message.attachment?.kind === 'image'" class="chat-image" :src="message.attachment.url" :alt="message.attachment.name" @click="previewChatAttachment(message.attachment)" />
                      <button v-if="message.attachment?.kind === 'file'" class="chat-file" type="button" @click="previewChatAttachment(message.attachment)"><b>{{ message.attachment.name }}</b><small>{{ message.attachment.size }}</small></button>
                      <audio v-if="message.attachment?.kind === 'audio'" :src="message.attachment.url" controls preload="metadata"></audio>
                      <button v-if="message.card" class="message-card" type="button" @click="openMessageCard(message.card)">
                        <b>{{ message.card.title }}</b><small>{{ message.card.desc }}</small>
                      </button>
                      <small>{{ message.time }}</small>
                    </div>
                  </article>
                </div>
                <form class="chat-compose" @submit.prevent="sendChatMessage(chatInput)">
                  <input ref="chatImageInput" class="visually-hidden" type="file" accept="image/*" multiple @change="addChatAttachments($event, 'image')" />
                  <input ref="chatFileInput" class="visually-hidden" type="file" multiple @change="addChatAttachments($event, 'file')" />
                  <button type="button" title="选择现场图片" @click="$refs.chatImageInput.click()">图片</button>
                  <button type="button" title="选择本地文件" @click="$refs.chatFileInput.click()">文件</button>
                  <button type="button" :class="{ recording: chatRecording }" @click="toggleChatRecording">{{ chatRecording ? `停止 ${chatRecordSeconds}s` : '语音' }}</button>
                  <button type="button" @click="openTaskPicker('send')">任务卡片</button>
                  <input v-model="chatInput" placeholder="输入协作消息，支持发送任务、文件、知识条目" />
                  <button class="primary" type="submit">发送</button>
                </form>
              </section>
              <aside class="collab-info">
                <img :src="avatarFor(activeConversation?.avatar, activeConversation?.name)" :alt="activeConversation?.name" @error="handleContactAvatarError($event, activeConversation?.name)" />
                <h3>{{ activeConversation?.name }}</h3>
                <p>{{ activeConversation?.position }} · {{ activeConversation?.department }}</p>
                <div class="detail-grid">
                  <span>专业：{{ activeConversation?.specialty }}</span>
                  <span>擅长设备：{{ activeConversation?.devices?.join('、') }}</span>
                  <span>当前任务：{{ activeConversation?.currentTask }}</span>
                  <span>工作负载：{{ activeConversation?.workload }}%</span>
                </div>
                <div class="collab-actions">
                  <button type="button" @click="openTaskPicker('assign')">添加到任务</button>
                  <button type="button" @click="requestSupport">请求专家支援</button>
                  <button type="button" @click="createCollaborationGroup">创建协作群</button>
                  <button type="button" @click="openTaskPicker('send')">发送任务资料</button>
                  <button type="button" :class="{ recording: chatRecording }" @click="toggleChatRecording">{{ chatRecording ? '结束录音' : '语音沟通' }}</button>
                </div>
              </aside>
            </div>
          </template>
        </section>

        <section v-else-if="activePage === 'knowledge'" class="page-grid">
          <div class="panel span-all knowledge-nav-panel">
            <div class="panel-head">
              <div>
                <p class="eyebrow">知识库</p>
                <h3>检修知识资产中心</h3>
                <small>连接知识网络、文件、技术资料与经验沉淀</small>
              </div>
              <div class="tabs">
                <button v-for="tab in knowledgeTabs" :key="tab.key" type="button" :class="{ active: knowledgePanel === tab.key }" @click="knowledgePanel = tab.key">{{ tab.label }}</button>
              </div>
            </div>
          </div>

          <div v-if="knowledgePanel === 'network'" class="panel span-all graph-panel">
            <div class="graph-toolbar">
              <div>
                <p class="eyebrow">知识图谱</p>
                <h3>设备、故障、资料与检修经验关系图谱</h3>
              </div>
              <label class="graph-search" :class="{ expanded: graphSearchExpanded || knowledgeKeyword }">
                <button class="graph-search-trigger" type="button" @click.prevent="openGraphSearch" aria-label="展开知识搜索">
                  <svg class="ui-icon" viewBox="0 0 24 24" aria-hidden="true">
                    <path v-for="path in iconParts('search')" :key="path" :d="path"></path>
                  </svg>
                </button>
                <input ref="graphSearchInput" v-model="knowledgeKeyword" placeholder="搜索设备、故障、零部件、SOP 节点" @focus="graphSearchExpanded = true" @keyup.enter="loadKnowledge" />
                <button v-if="knowledgeKeyword" class="graph-search-clear" type="button" @click.prevent="knowledgeKeyword = ''">×</button>
              </label>
              <div class="graph-controls">
                <select v-model="graphKindFilter">
                  <option value="all">全部类型</option>
                  <option v-for="item in graphLegend" :key="item.kind" :value="item.kind">{{ item.label }}</option>
                </select>
                <select v-model="graphDepth">
                  <option :value="1">一层关系</option>
                  <option :value="2">二层关系</option>
                  <option :value="3">三层关系</option>
                </select>
                <select v-model="graphRelationFilter">
                  <option value="all">全部关系</option>
                  <option v-for="item in graphRelationTypes" :key="item" :value="item">{{ item }}</option>
                </select>
                <select v-model="graphLayoutMode" @change="relayoutGraph">
                  <option value="force">力导向</option>
                  <option value="tree">树形</option>
                  <option value="circle">环形</option>
                </select>
                <button type="button" @click="graphShowLabels = !graphShowLabels">{{ graphShowLabels ? '隐藏标签' : '显示标签' }}</button>
                <button type="button" @click="resetGraphView">重置视图</button>
              </div>
            </div>
            <div class="knowledge-map">
              <div ref="mapCanvasRef" class="map-canvas" @pointermove="dragGraphNode" @pointerup="stopGraphDrag" @pointerleave="stopGraphDrag">
                <div class="graph-legend">
                  <span v-for="item in graphLegend" :key="item.kind"><i :class="item.kind"></i>{{ item.label }}</span>
                </div>
                <div class="graph-zoom">
                  <button type="button" @click="graphZoom = Math.min(graphZoom + 0.08, 1.35)">＋</button>
                  <input v-model.number="graphZoom" type="range" min="0.72" max="1.35" step="0.01" />
                  <button type="button" @click="graphZoom = Math.max(graphZoom - 0.08, 0.72)">－</button>
                </div>
                <svg class="map-lines" viewBox="0 0 820 520" aria-hidden="true">
                  <defs>
                    <marker id="graphArrow" markerWidth="8" markerHeight="8" refX="7" refY="3.5" orient="auto">
                      <path d="M0,0 L7,3.5 L0,7 Z" fill="#8ba9b6"></path>
                    </marker>
                    <filter id="graphGlow">
                      <feGaussianBlur stdDeviation="2.4" result="blur" />
                      <feMerge>
                        <feMergeNode in="blur" />
                        <feMergeNode in="SourceGraphic" />
                      </feMerge>
                    </filter>
                  </defs>
                  <line
                    v-for="edge in graphEdges"
                    :key="edge.id"
                    :class="{ faint: edge.faint }"
                    :x1="edge.x1"
                    :y1="edge.y1"
                    :x2="edge.x2"
                    :y2="edge.y2"
                    marker-end="url(#graphArrow)"
                  />
                  <text v-for="edge in graphEdges.filter((item) => !item.faint)" :key="`${edge.id}-label`" :x="(edge.x1 + edge.x2) / 2" :y="(edge.y1 + edge.y2) / 2 - 4">{{ edge.label }}</text>
                </svg>
                <div class="graph-stage" :style="{ transform: `scale(${graphZoom})` }">
                  <button class="graph-node center" type="button" @click="toast('一修知识中枢：统一连接检修资料、任务与经验')">
                    <span></span>
                    <b>一修</b>
                  </button>
                  <button
                    v-for="node in graphNodes"
                    :key="node.id"
                    type="button"
                    class="graph-node"
                    :class="[node.kind, { important: node.important, active: selectedGraphNode?.id === node.id, matched: node.matched, showLabel: graphShowLabels || node.important }]"
                    :style="{ left: `${node.x}%`, top: `${node.y}%` }"
                    @pointerdown.stop.prevent="startGraphDrag(node, $event)"
                    @click="selectGraphNode(node)"
                  >
                    <span></span>
                    <b>{{ node.label }}</b>
                  </button>
                </div>
              </div>
              <aside class="map-inspector">
                <p class="eyebrow">节点详情</p>
                <template v-if="selectedGraphNode">
                  <h3>{{ selectedGraphNode.label }}</h3>
                  <p>{{ selectedGraphNode.summary }}</p>
                  <div class="tag-line">
                    <span v-for="tag in selectedGraphNode.tags" :key="tag">{{ tag }}</span>
                  </div>
                  <button class="primary" type="button" @click="openKnowledge(selectedGraphNode.source)">查看关联资料</button>
                  <button type="button" @click="activePage = 'search'">从节点发起检索</button>
                </template>
                <div v-else class="empty">点击图谱节点查看关联资料、任务和检修建议。</div>
              </aside>
            </div>
          </div>

          <div v-if="knowledgePanel === 'files'" class="panel span-all file-manager">
            <div class="file-toolbar">
              <div>
                <p class="eyebrow">文件管理器</p>
                <h3>维修资料、现场图片、SOP、报告与版本文件</h3>
              </div>
              <input ref="fileManagerInput" type="file" multiple @change="addFiles($event, 'manager')" />
              <div class="file-actions">
                <button type="button" @click="toast('已新建资料文件夹')">新建文件夹</button>
                <button class="primary" type="button" @click="$refs.fileManagerInput.click()">上传资料</button>
              </div>
            </div>
            <div class="file-window">
              <aside class="file-sidebar">
                <button
                  v-for="folder in fileFolders"
                  :key="folder"
                  type="button"
                  :class="{ active: activeFolder === folder }"
                  @click="activeFolder = folder"
                >
                  <span>{{ folderIcon(folder) }}</span>{{ folder }}
                </button>
              </aside>
              <section class="file-desktop" @dragover.prevent @drop.prevent="addManagerDroppedFiles">
                <div class="file-pathbar">
                  <span>一修资料盘 / {{ activeFolder }}</span>
                  <input v-model="fileKeyword" placeholder="搜索文件名称、设备、型号" />
                  <select v-model="fileType"><option value="all">全部类型</option><option>PDF</option><option>Word</option><option>图片</option><option>视频</option><option>其他</option></select>
                  <button type="button" @click="fileView = fileView === 'table' ? 'card' : 'table'">{{ fileView === 'table' ? '图标视图' : '详细信息' }}</button>
                </div>
                <div v-if="filteredFiles.length === 0" class="empty">这里还没有匹配文件，可以拖拽文件到此处或点击上传资料。</div>
                <div v-else-if="fileView === 'card'" class="desktop-grid">
                  <button v-for="file in filteredFiles" :key="file.id" class="desktop-file" :class="{ selected: selectedFileRow === file.id }" type="button" @dblclick="previewFile(file)" @click="selectedFileRow = file.id">
                    <span class="file-icon" :class="fileIconClass(file)">{{ fileIcon(file) }}</span>
                    <b>{{ file.name }}</b>
                    <small>{{ file.type }} · {{ file.size }}</small>
                    <i>{{ file.parseStatus }}</i>
                  </button>
                </div>
                <div v-else class="table file-table">
                  <div class="tr head"><span>文件</span><span>分类</span><span>设备</span><span>上传</span><span>审核</span><span>解析</span><span>版本</span><span>操作</span></div>
                  <div v-for="file in filteredFiles" :key="file.id" class="tr">
                    <span>{{ file.name }}<small>{{ file.type }} · {{ file.size }}</small></span>
                    <span>{{ file.category }}</span>
                    <span>{{ file.equipment }} / {{ file.model }}</span>
                    <span>{{ file.uploader }}<small>{{ file.uploaded_at }}</small></span>
                    <span>{{ file.auditStatus }}</span>
                    <span>{{ file.parseStatus }}</span>
                    <span>{{ file.version }}</span>
                    <span class="inline-actions"><button type="button" @click="previewFile(file)">预览</button><button type="button" @click="toast('已收藏')">收藏</button></span>
                  </div>
                </div>
                <div class="file-statusbar">
                  <span>{{ filteredFiles.length }} 个项目</span>
                  <span>双击文件可预览，支持图片、PDF、视频和文本本地预览</span>
                </div>
              </section>
            </div>
          </div>

          <div v-if="knowledgePanel === 'library'" class="panel span-all knowledge-library-panel">
            <div class="library-heading">
              <div>
                <p class="eyebrow">技术资料库</p>
                <h3>检索可靠的设备检修知识</h3>
                <span>覆盖维修手册、历史案例、标准作业流程与安全规范</span>
              </div>
              <b>{{ filteredKnowledge.length }} 条资料</b>
            </div>
            <div class="filters library-searchbar">
              <span class="library-search-icon" aria-hidden="true">
                <svg class="ui-icon" viewBox="0 0 24 24"><path v-for="path in iconParts('search')" :key="path" :d="path"></path></svg>
              </span>
              <input v-model.trim="knowledgeKeyword" placeholder="输入设备、故障现象或资料名称" @keyup.enter="loadKnowledge" />
              <button type="button" @click="loadKnowledge">检索资料库</button>
            </div>
            <div v-if="filteredKnowledge.length" class="result-grid library-result-grid">
              <article v-for="(item, index) in filteredKnowledge" :key="item.id" class="result-card library-result-card" :style="{ '--library-index': index % 4 }">
                <div class="library-card-head">
                  <span class="library-type">{{ knowledgeTypeText(item) }}</span>
                  <span v-if="item.match" class="library-match">匹配度 {{ item.match }}%</span>
                </div>
                <h4>{{ item.title }}</h4>
                <div class="library-meta">
                  <span v-for="meta in knowledgeMetaParts(item)" :key="meta">{{ meta }}</span>
                </div>
                <div class="library-summary">
                  <p v-for="(line, lineIndex) in knowledgeSummaryLines(item)" :key="lineIndex">{{ line }}</p>
                </div>
                <div v-if="item.tags?.length" class="tag-line library-tags"><span v-for="tag in item.tags" :key="tag">{{ tag }}</span></div>
                <div class="library-card-footer">
                  <small>{{ item.updated_at ? `更新于 ${item.updated_at}` : '平台知识资料' }}<template v-if="item.citations"> · 引用 {{ item.citations }} 次</template></small>
                  <div class="card-actions"><button type="button" @click="openKnowledge(item)">查看详情</button><button class="primary" type="button" @click="searchFromKnowledge(item)">发起检索</button></div>
                </div>
              </article>
            </div>
            <div v-else class="library-empty"><b>未找到相关资料</b><span>请尝试更换设备型号、故障现象或资料名称</span></div>
          </div>

          <div v-if="knowledgePanel === 'update'" class="panel span-all">
            <p class="eyebrow">沉淀更新</p>
            <div class="form-grid">
              <label>知识标题<input v-model="knowledgeForm.title" placeholder="如：发动机异响复检案例" /></label>
              <label>资料类型<select v-model="knowledgeForm.type"><option>历史故障案例</option><option>维修手册</option><option>SOP</option><option>安全规范</option></select></label>
              <label>适用设备<input v-model="knowledgeForm.equipment" /></label>
              <label>设备型号<input v-model="knowledgeForm.model" /></label>
              <label>来源依据<input v-model="knowledgeForm.source" placeholder="工单号、手册章节或现场记录" /></label>
              <label>人工标签<input v-model="knowledgeForm.tagText" placeholder="使用逗号分隔，如：异响,气门,复测" /></label>
              <label class="wide">沉淀摘要<textarea v-model="knowledgeForm.summary" placeholder="描述故障现象、原因、处理方式、复检结论和引用依据"></textarea></label>
            </div>
            <button class="primary" type="button" @click="saveKnowledge">提交知识审核</button>
            <div class="knowledge-review-list">
              <article v-for="item in pendingKnowledge" :key="item.id" class="result-card">
                <div><b>{{ item.title }}</b><small>{{ item.equipment }} / {{ item.model }} · {{ knowledgeStatusText(item.status) }}</small><p>{{ item.summary }}</p></div>
                <label>人工修正<textarea v-model="knowledgeCorrections[item.id]" placeholder="核对并修正模型整理结果；无误可直接通过"></textarea></label>
                <div class="tag-line"><span v-for="tag in item.tags || []" :key="tag">{{ tag }}</span></div>
                <div class="card-actions"><button class="primary" type="button" @click="reviewKnowledge(item, 'approved')">审核入库</button><button type="button" @click="reviewKnowledge(item, 'rejected')">退回修改</button></div>
              </article>
            </div>
          </div>
        </section>

        <section v-else class="page-grid profile-page">
          <div class="profile-hero span-all">
            <img :src="user.avatar" alt="" @error="handleAvatarError" />
            <div>
              <p class="eyebrow">个人主页</p>
              <h2>{{ user.name }}</h2>
              <p>{{ user.role }} · {{ user.department }} · 工号 {{ user.employeeId }}</p>
              <div class="tag-line">
                <span v-for="tag in user.specialties" :key="tag">{{ tag }}</span><span>技能等级：{{ user.skillLevel }}</span>
              </div>
            </div>
            <button class="primary" type="button" @click="openProfileEditor">编辑资料</button>
          </div>

          <article v-for="section in profileSections" :key="section.key" class="profile-section" :class="[section.span, `profile-${section.key}`]">
            <div class="panel-head">
              <div>
                <p class="eyebrow">{{ section.group }}</p>
                <h3>{{ section.title }}</h3>
              </div>
              <button v-if="section.action" type="button" @click="runProfileAction(section)">{{ section.action }}</button>
            </div>
            <div class="profile-metrics" v-if="section.metrics">
              <span v-for="metric in section.metrics" :key="metric.label"><b>{{ metric.value }}</b>{{ metric.label }}</span>
            </div>
            <div class="profile-list">
              <button v-for="item in section.items" :key="item.title" type="button" @click="runProfileItem(item)">
                <b>{{ item.title }}</b>
                <small>{{ item.desc }}</small>
              </button>
            </div>
          </article>

          <div class="panel span-all agent-history-panel">
            <div class="panel-head">
              <div>
                <p class="eyebrow">智能体使用记录</p>
                <h3>最近协助我的器灵</h3>
              </div>
              <button type="button" @click="runAudit">查看核查建议</button>
            </div>
            <div class="agent-history">
              <article v-for="(agent, index) in agents.slice(0, 6)" :key="agent.id" :style="{ '--agent-index': index }">
                <div class="agent-history-avatar"><img :src="agent.avatar" :alt="agent.name" @error="handleAvatarError" /><i></i></div>
                <div class="agent-history-copy">
                  <span>{{ agent.role }}</span>
                  <b>{{ agent.name }}</b>
                  <small>{{ agent.lastResult }}</small>
                </div>
                <button type="button" @click="sendOperatorPrompt(agent.role)">查看记录 <i>→</i></button>
              </article>
            </div>
            <pre v-if="auditResult">{{ auditResult }}</pre>
          </div>
        </section>
      </section>

      <button class="panel-resizer" type="button" aria-label="拖动调整智能体面板宽度" title="拖动调整智能体面板宽度" @pointerdown="startOperatorResize">
        <span></span>
      </button>

      <aside class="operator-panel" aria-label="页面智能体对话">
        <div class="operator-head">
          <img class="operator-avatar" :src="operatorProfile.avatar" :alt="operatorProfile.name" @error="handleAvatarError" />
          <div>
            <p class="eyebrow">智能体协助</p>
            <h2>{{ operatorProfile.name }}</h2>
            <small class="operator-role">{{ operatorProfile.role }}</small>
          </div>
          <div class="operator-head-actions">
            <span :class="['operator-status', operatorProfile.status]">{{ operatorProfile.statusText }}</span>
            <div class="panel-size-actions" aria-label="智能体面板显示大小">
              <button type="button" title="缩小智能体面板" @click="resizeOperator(-40)">−</button>
              <button type="button" title="放大智能体面板" @click="resizeOperator(40)">＋</button>
            </div>
          </div>
        </div>

        <p class="operator-duty">{{ operatorProfile.duty }}</p>
        <p class="operator-slogan">{{ operatorProfile.slogan }}</p>

        <div class="chat-thread">
          <div class="bubble assistant">
            {{ operatorProfile.welcome }}
          </div>
          <div class="bubble user">
            {{ operatorProfile.sampleAsk }}
          </div>
          <div class="bubble assistant">
            {{ operatorProfile.sampleAnswer }}
          </div>
          <div v-for="message in currentOperatorMessages" :key="message.id" :class="['bubble', message.role]">
            {{ message.text }}
          </div>
          <button class="quick-card" type="button" @click="runOperatorPrimary">
            <span>
              <svg class="ui-icon" viewBox="0 0 24 24" aria-hidden="true">
                <path v-for="path in iconParts(operatorProfile.icon)" :key="path" :d="path"></path>
              </svg>
            </span>
            <div>
              <b>{{ operatorProfile.quickTitle }}</b>
              <small>{{ operatorProfile.quickDesc }}</small>
            </div>
            <i>→</i>
          </button>
        </div>

        <div class="operator-chips">
          <button v-for="action in operatorProfile.actions" :key="action" type="button" @click="sendOperatorPrompt(action)">
            {{ action }}
          </button>
        </div>

        <input ref="assistantFileInput" class="visually-hidden" type="file" multiple accept="image/*,.pdf,.doc,.docx,.txt,.md" @change="addFiles($event, 'assistant')" />
        <div class="assistant-input-tools">
          <button type="button" :class="{ active: assistantVoiceListening }" @click="toggleAssistantVoice">
            <svg class="ui-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3a3 3 0 0 0-3 3v6a3 3 0 0 0 6 0V6a3 3 0 0 0-3-3Z"></path><path d="M5 11a7 7 0 0 0 14 0M12 18v3M9 21h6"></path></svg>
            {{ assistantVoiceListening ? '正在听写，点击停止' : '语音转文字' }}
          </button>
          <button type="button" @click="$refs.assistantFileInput.click()">
            <svg class="ui-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h4l2-2h4l2 2h4v12H4Z"></path><circle cx="12" cy="13" r="3"></circle></svg>
            图片 / 资料识别
          </button>
        </div>
        <form class="ask-box" @submit.prevent="sendOperatorPrompt(operatorInput)">
          <input v-model="operatorInput" :placeholder="operatorProfile.placeholder" />
          <button type="submit" aria-label="发送消息" title="发送消息">
            <svg class="ui-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="m4 4 16 8-16 8 3-8-3-8Z"></path><path d="M7 12h13"></path></svg>
          </button>
        </form>
        <div v-if="assistantFiles.length" class="assistant-attachments">
          <span v-for="file in assistantFiles" :key="file.localId">
            <img v-if="file.type === '图片'" :src="file.url" :alt="file.name" />
            <i>{{ file.type }}</i>{{ file.name }} · {{ file.status }}
            <button type="button" @click="removeAssistantFile(file.localId)">×</button>
          </span>
        </div>
      </aside>
      </div>
    </section>

    <div v-if="selectedTask" class="modal" @click.self="selectedTask = null">
      <article class="modal-card task-modal-card">
        <button class="close" type="button" @click="selectedTask = null">×</button>
        <header class="task-modal-hero">
          <div><p class="eyebrow">任务详情与作业执行</p><h2>{{ selectedTask.title }}</h2><small>{{ selectedTask.workOrderNo }} · {{ selectedTask.equipment_name }} / {{ selectedTask.equipment_model }}</small></div>
          <span><i :class="['badge', selectedTask.severity]">{{ severityText(selectedTask.severity) }}</i><b>{{ statusText(selectedTask.status) }}</b></span>
        </header>
        <div class="task-modal-progress"><div><span :style="{ width: `${selectedTask.progress}%` }"></span></div><b>{{ selectedTask.progress }}%</b></div>
        <div class="detail-grid task-modal-stats">
          <span><small>设备编号</small><b>{{ selectedTask.equipment_no }}</b></span>
          <span><small>负责人</small><b>{{ selectedTask.assignee_name }}</b></span>
          <span><small>当前步骤</small><b>{{ selectedTask.current_step }}</b></span>
          <span><small>剩余时间</small><b>{{ remainingTime(selectedTask) }}</b></span>
        </div>
        <p class="task-modal-description">{{ selectedTask.description }}</p>
        <div class="task-modal-section-title"><span>标准作业步骤</span><small>{{ selectedTask.sop?.length || 0 }} 个步骤</small></div>
        <div class="sop-list executable-sop">
          <span v-for="(step, index) in selectedTask.sop" :key="`${stepTitle(step)}-${index}`" :class="{ completed: isTaskStepCompleted(selectedTask, index) }">
            <b>{{ isTaskStepCompleted(selectedTask, index) ? '✓' : index + 1 }}</b>
            <span><strong>{{ stepTitle(step) }}</strong><small v-if="stepDetail(step)">{{ stepDetail(step) }}</small></span>
            <button type="button" :disabled="isTaskStepCompleted(selectedTask, index)" @click="completeTaskStep(selectedTask, index)">{{ isTaskStepCompleted(selectedTask, index) ? '已完成' : '确认完成' }}</button>
          </span>
        </div>
        <div v-if="selectedTask.safety?.length" class="safety-reminders"><div><b>合规与安全提醒</b><small>操作前逐项确认</small></div><span v-for="item in selectedTask.safety" :key="item">{{ item }}</span></div>
        <div class="actions task-modal-actions">
          <button class="primary" type="button" @click="handleTaskPrimary(selectedTask)">{{ taskPrimaryLabel(selectedTask) }}</button>
          <button type="button" :disabled="selectedTask.status === 'pending'" @click="enterTaskRecheck(selectedTask)">进入复检</button>
          <button type="button" @click="previewTaskReport(selectedTask)">预览报告</button>
        </div>
      </article>
    </div>

    <div v-if="showTaskPicker" class="modal" @click.self="showTaskPicker = false">
      <article class="modal-card task-picker-card">
        <button class="close" type="button" @click="showTaskPicker = false">×</button>
        <p class="eyebrow">{{ taskPickerMode === 'assign' ? '添加协作人员' : '发送任务卡片' }}</p>
        <h2>{{ taskPickerMode === 'assign' ? `选择要加入 ${activeConversation?.name} 的任务` : '选择需要发送的检修任务' }}</h2>
        <div class="task-picker-list">
          <button v-for="task in tasks" :key="task.id" type="button" @click="selectTaskFromPicker(task)">
            <span><b>{{ task.workOrderNo }}</b><small>{{ task.equipment_name }} · {{ task.current_step }}</small></span>
            <i :class="['badge', task.severity]">{{ severityText(task.severity) }}</i><strong>{{ task.progress }}%</strong>
          </button>
        </div>
      </article>
    </div>

    <div v-if="reportTask" class="modal" @click.self="reportTask = null">
      <article class="modal-card task-report-card">
        <button class="close" type="button" @click="reportTask = null">×</button>
        <header><div><p class="eyebrow">检修报告预览</p><h2>{{ reportTask.title }}</h2><small>{{ reportTask.workOrderNo }} · 生成时间 {{ new Date().toLocaleString('zh-CN') }}</small></div><span :class="['badge', reportTask.severity]">{{ severityText(reportTask.severity) }}</span></header>
        <div class="report-summary"><span><small>设备</small><b>{{ reportTask.equipment_name }} / {{ reportTask.equipment_model }}</b></span><span><small>负责人</small><b>{{ reportTask.assignee_name }}</b></span><span><small>完成进度</small><b>{{ reportTask.progress }}%</b></span><span><small>当前结论</small><b>{{ statusText(reportTask.status) }}</b></span></div>
        <section><h3>故障与处置摘要</h3><p>{{ reportTask.description }}</p></section>
        <section><h3>标准作业记录</h3><ol><li v-for="(step, index) in reportTask.sop || []" :key="index"><b>{{ stepTitle(step) }}</b><span>{{ isTaskStepCompleted(reportTask, index) ? '已确认完成' : '待补充记录' }}</span></li></ol></section>
        <section v-if="reportTask.recheck"><h3>复检结论</h3><p>{{ reportTask.recheck.result }} · {{ reportTask.recheck.comment || '未填写补充说明' }}</p></section>
        <div class="actions"><button type="button" @click="windowPrint">打印 / 导出 PDF</button><button class="primary" type="button" @click="reportTask = null">完成预览</button></div>
      </article>
    </div>

    <div v-if="selectedFile" class="modal" @click.self="selectedFile = null">
      <article class="modal-card wide-modal">
        <button class="close" type="button" @click="selectedFile = null">×</button>
        <p class="eyebrow">文件预览</p>
        <h2>{{ selectedFile.name }}</h2>
        <div class="detail-grid">
          <span>类型：{{ selectedFile.type }}</span>
          <span>大小：{{ selectedFile.size }}</span>
          <span>版本：{{ selectedFile.version }}</span>
          <span>解析：{{ selectedFile.parseStatus }}</span>
        </div>
        <div class="preview-box">
          <img v-if="selectedFile.type === '图片' && selectedFile.url" :src="selectedFile.url" alt="" />
          <iframe v-else-if="selectedFile.type === 'PDF' && selectedFile.url" :src="selectedFile.url"></iframe>
          <video v-else-if="selectedFile.type === '视频' && selectedFile.url" :src="selectedFile.url" controls></video>
          <iframe v-else-if="['文本', 'Word', 'Excel', '其他'].includes(selectedFile.type) && selectedFile.url" :src="selectedFile.url"></iframe>
          <div v-else class="empty">该文件暂不支持在线预览或真实访问地址为空，请下载后查看或重新解析。</div>
        </div>
      </article>
    </div>

    <div v-if="selectedKnowledge" class="modal" @click.self="selectedKnowledge = null">
      <article class="modal-card knowledge-detail-card">
        <button class="close" type="button" @click="selectedKnowledge = null">×</button>
        <header><div><p class="eyebrow">知识详情</p><h2>{{ selectedKnowledge.title }}</h2></div><span>{{ knowledgeTypeText(selectedKnowledge) }}</span></header>
        <div class="knowledge-detail-meta"><span><small>适用设备</small><b>{{ selectedKnowledge.equipment || '通用检修设备' }}</b></span><span><small>型号</small><b>{{ selectedKnowledge.model || '通用型号' }}</b></span><span><small>来源</small><b>{{ selectedKnowledge.source || '一修知识库' }}</b></span><span><small>引用</small><b>{{ selectedKnowledge.citations || 0 }} 次</b></span></div>
        <section><h3>内容摘要</h3><ul><li v-for="(line, index) in knowledgeSummaryLines(selectedKnowledge)" :key="index">{{ line }}</li></ul></section>
        <div class="tag-line"><span v-for="tag in selectedKnowledge.tags || []" :key="tag">{{ tag }}</span></div>
        <div class="actions"><button type="button" @click="selectedKnowledge = null">关闭</button><button class="primary" type="button" @click="searchFromKnowledge(selectedKnowledge); selectedKnowledge = null">作为检索依据</button></div>
      </article>
    </div>

    <div v-if="showTaskForm" class="modal" @click.self="showTaskForm = false">
      <article class="modal-card">
        <button class="close" type="button" @click="showTaskForm = false">×</button>
        <p class="eyebrow">新建检修任务</p>
        <div class="form-grid">
          <label>设备名称<input v-model="taskForm.equipment_name" /></label>
          <label>设备编号<input v-model="taskForm.equipment_no" /></label>
          <label>设备型号<input v-model="taskForm.equipment_model" /></label>
          <label>风险等级<select v-model="taskForm.severity"><option value="low">低</option><option value="medium">中</option><option value="high">高</option></select></label>
          <label>负责人<input v-model="taskForm.assignee_name" /></label>
          <label>计划完成时间<input v-model="taskForm.due_at" /></label>
          <label class="wide">故障描述<textarea v-model="taskForm.description"></textarea></label>
        </div>
        <button class="primary" type="button" @click="submitTask">创建任务</button>
      </article>
    </div>

    <div v-if="showProfileEditor" class="modal profile-editor-modal" @click.self="showProfileEditor = false">
      <form class="modal-card profile-editor-card" @submit.prevent="saveProfile">
        <button class="close" type="button" @click="showProfileEditor = false">×</button>
        <header class="profile-editor-head">
          <img :src="profileDraft.avatar" alt="" @error="handleAvatarError" />
          <div><p class="eyebrow">个人资料</p><h2>完善检修信息</h2><span>资料将用于工单分配、协作联系和知识贡献署名</span></div>
        </header>
        <div class="form-grid profile-editor-grid">
          <label>姓名<input v-model.trim="profileDraft.name" maxlength="20" /></label>
          <label>工号<input v-model.trim="profileDraft.employeeId" maxlength="20" /></label>
          <label>岗位<input v-model.trim="profileDraft.role" maxlength="30" /></label>
          <label>所属班组<input v-model.trim="profileDraft.department" maxlength="30" /></label>
          <label>技能等级<select v-model="profileDraft.skillLevel"><option>初级</option><option>中级</option><option>高级</option><option>专家</option></select></label>
          <label>联系电话<input v-model.trim="profileDraft.phone" maxlength="20" placeholder="用于任务协作联系" /></label>
          <label class="wide">专业方向<input v-model.trim="profileDraft.specialtyText" placeholder="使用逗号分隔，如：发动机, 电气系统" /></label>
          <label class="wide">个人简介<textarea v-model.trim="profileDraft.bio" maxlength="160" placeholder="简要介绍检修经验与擅长领域"></textarea></label>
        </div>
        <p v-if="profileError" class="form-error">{{ profileError }}</p>
        <div class="profile-editor-actions"><button type="button" @click="showProfileEditor = false">取消</button><button class="primary" type="submit">保存资料</button></div>
      </form>
    </div>

    <div v-if="toastText" class="toast">{{ toastText }}</div>
    </template>
  </main>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { yixiuApi } from './src/api/yixiuWeb.js'
import { createOverviewFromMock, mockAgents, mockUser } from './src/data/yixiuMock.js'

const navItems = [
  { key: 'home', label: '首页', title: '综合工作台', icon: 'dashboard' },
  { key: 'search', label: '智能检索', title: '多模态故障分析', icon: 'search' },
  { key: 'tasks', label: '检修任务', title: '工单与复检闭环', icon: 'wrench' },
  { key: 'knowledge', label: '知识库', title: '资料、文件与知识网络', icon: 'network' },
  { key: 'profile', label: '个人中心', title: '人员、记录与核查', icon: 'user' }
]

const iconPaths = {
  dashboard: ['M4 13h7V4H4v9Z', 'M13 20h7V4h-7v16Z', 'M4 20h7v-5H4v5Z'],
  search: ['M11 19a8 8 0 1 1 0-16 8 8 0 0 1 0 16Z', 'M21 21l-4.35-4.35'],
  wrench: ['M14.7 6.3a4 4 0 0 0-5 5L3.9 17.1a2 2 0 0 0 3 3l5.8-5.8a4 4 0 0 0 5-5l-2.9 2.9-2.1-2.1 2.9-2.9Z'],
  network: ['M6 8a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z', 'M18 22a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z', 'M18 8a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z', 'M8.6 6.5l6.8 10', 'M8.8 4.5h6.4'],
  user: ['M20 21a8 8 0 0 0-16 0', 'M12 13a5 5 0 1 0 0-10 5 5 0 0 0 0 10Z'],
  bell: ['M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9Z', 'M10 21h4'],
  cpu: ['M8 8h8v8H8z', 'M3 10h3', 'M3 14h3', 'M18 10h3', 'M18 14h3', 'M10 3v3', 'M14 3v3', 'M10 18v3', 'M14 18v3'],
  bot: ['M12 8V4', 'M7 8h10a4 4 0 0 1 4 4v3a5 5 0 0 1-5 5H8a5 5 0 0 1-5-5v-3a4 4 0 0 1 4-4Z', 'M9 13h.01', 'M15 13h.01', 'M9 17h6'],
  check: ['M20 6 9 17l-5-5'],
  tool: ['M21 3l-6 6', 'M14 4l6 6', 'M5 19l6-6']
}
const iconParts = (name) => iconPaths[name] || iconPaths.tool

const AUTH_ACCOUNTS_KEY = 'yixiu-web-accounts'
const AUTH_SESSION_KEY = 'yixiu-web-session'
const PROFILE_KEY = 'yixiu-web-profile'
const CONTACT_DIRECTORY_KEY = 'yixiu-web-contact-directory'
const defaultProfile = {
  ...mockUser,
  employeeId: 'YX-0824',
  skillLevel: '高级',
  phone: '138-0000-1024',
  specialties: ['发动机', '电气系统', '高风险作业确认'],
  bio: '专注动力设备检修、故障分析与标准作业执行。'
}
const defaultAccount = { account: 'yixiu', password: 'Yixiu2026!', name: '聪明的一修', profile: defaultProfile }
const readStorage = (key, fallback) => {
  try { return JSON.parse(localStorage.getItem(key)) ?? fallback } catch { return fallback }
}
const savedSession = readStorage(AUTH_SESSION_KEY, null) || (() => { try { return JSON.parse(sessionStorage.getItem(AUTH_SESSION_KEY)) } catch { return null } })()
const isAuthenticated = ref(Boolean(savedSession?.account))
const currentAccount = ref(savedSession?.account || '')
const authMode = ref('login')
const authError = ref('')
const authForm = reactive({ name: '', account: savedSession?.account || 'yixiu', password: '', confirmPassword: '', remember: true, agreed: false })
const showProfileEditor = ref(false)
const profileError = ref('')
const profileDraft = reactive({ ...defaultProfile, specialtyText: defaultProfile.specialties.join('，') })

const activePage = ref('home')
const showSplash = ref(true)
const bootScreenRef = ref(null)
const bootMarkRef = ref(null)
const bootLogoRef = ref(null)
const brandLogoRef = ref(null)
const navCollapsed = ref(false)
const operatorWidth = ref(Math.min(520, Math.max(300, Number(localStorage.getItem('yixiu-operator-width')) || 360)))
const assistantVoiceListening = ref(false)
let assistantSpeechRecognition = null
let stopOperatorResize = null
let clockTimer = null
let toastTimer = null
const globalKeyword = ref('')
const currentNav = computed(() => navItems.find((item) => item.key === activePage.value) || navItems[0])
const initialRegisteredAccount = readStorage(AUTH_ACCOUNTS_KEY, []).find((item) => item.account === savedSession?.account)
const initialProfile = savedSession?.account === defaultAccount.account ? readStorage(PROFILE_KEY, {}) : initialRegisteredAccount?.profile || {}
const user = reactive({ ...defaultProfile, ...initialProfile })
const agentProfileMap = Object.fromEntries(mockAgents.map((agent) => [agent.id, agent]))
const legacyAgentMap = {
  retrieval: 'guanwei',
  procedure: 'zhiju',
  knowledge: 'bowen',
  collaboration: 'heming',
  audit: 'mingjian'
}
function resolveAgentId(agent = {}) {
  if (agentProfileMap[agent.id]) return agent.id
  if (legacyAgentMap[agent.id]) return legacyAgentMap[agent.id]
  const name = `${agent.name || ''}${agent.duty || ''}`
  if (name.includes('检索') || name.includes('故障')) return 'guanwei'
  if (name.includes('作业') || name.includes('工单') || name.includes('流程')) return 'zhiju'
  if (name.includes('知识') || name.includes('资料') || name.includes('图谱')) return 'bowen'
  if (name.includes('协作') || name.includes('联络') || name.includes('联系人')) return 'heming'
  if (name.includes('核查') || name.includes('复检') || name.includes('验收')) return 'mingjian'
  return 'tiangong'
}
function normalizeAgentList(list = []) {
  const merged = (Array.isArray(list) && list.length ? list : mockAgents).map((agent) => {
    const id = resolveAgentId(agent)
    const profile = agentProfileMap[id]
    return { ...profile, ...agent, id, name: profile.name, avatar: profile.avatar, role: profile.role, slogan: profile.slogan, duty: profile.duty }
  })
  mockAgents.forEach((profile) => {
    if (!merged.some((agent) => agent.id === profile.id)) merged.push(profile)
  })
  return merged
}
const handleAvatarError = (event) => {
  event.target.src = '/static/agents/tiangong.png'
}
const avatarPalette = ['#dcefed', '#e9e2f7', '#f8e7d2', '#dce9f6', '#e3efdb']
const avatarFallback = (name = '一修') => {
  const label = String(name || '一修').replace(/[^\u4e00-\u9fa5A-Za-z0-9]/g, '').slice(-2) || '一修'
  const color = avatarPalette[[...label].reduce((sum, char) => sum + char.charCodeAt(0), 0) % avatarPalette.length]
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="96" height="96"><rect width="96" height="96" rx="48" fill="${color}"/><circle cx="48" cy="40" r="18" fill="#fff" opacity=".92"/><path d="M18 88c3-21 15-31 30-31s27 10 30 31" fill="#fff" opacity=".92"/><text x="48" y="46" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#145f5a">${label}</text></svg>`
  return `data:image/svg+xml;charset=UTF-8,${encodeURIComponent(svg)}`
}
const avatarFor = (avatar, name) => avatar && !String(avatar).includes('undefined') ? avatar : avatarFallback(name)
const handleContactAvatarError = (event, name) => { event.target.src = avatarFallback(name) }
const nowText = ref('')
const overview = reactive(createOverviewFromMock())
const systemStatus = reactive({ ...overview.status })
const tasks = ref([])
const knowledge = ref([])
const files = ref([])
const contacts = ref([])
const agents = ref(normalizeAgentList(overview.agents))
const loading = reactive({ search: false })
const voiceListening = ref(false)
let speechRecognition = null
const selectedTask = ref(null)
const selectedFile = ref(null)
const selectedKnowledge = ref(null)
const toastText = ref('')
const auditResult = ref('')
const selectedAgentId = ref('')
const operatorMessages = ref([])

const searchForm = reactive({ deviceName: '摩托车发动机总成', deviceModel: 'CG-125', faultCode: 'NOISE-02', category: '发动机', faultType: '异响', maintenanceLevel: '二级检修', query: '启动后气门区域有明显异响，热车后略有减轻，怠速不稳。' })
const searchFiles = ref([])
const assistantFiles = ref([])
const searchResult = ref(null)
const resultTab = ref('全部')
const resultTabs = ['全部', '维修手册', '历史故障案例', '标准作业流程 SOP', '安全操作规范', '推荐检修方案']
const resultTabCopy = {
  '全部': '汇总展示与当前故障最相关的知识资料和检修建议',
  '维修手册': '查看设备结构、参数标准和厂家检修说明',
  '历史故障案例': '参考相似现象、原因判断和现场处置记录',
  '标准作业流程 SOP': '按标准步骤执行检查、拆装、复测和验收',
  '安全操作规范': '核对作业许可、风险隔离和安全确认要求',
  '推荐检修方案': '根据当前多模态分析结果生成建议作业路径'
}

const taskPanel = ref('overview')
const taskTabs = [{ key: 'overview', label: '今日概览' }, { key: 'manage', label: '任务管理' }, { key: 'recheck', label: '复检评估' }, { key: 'contacts', label: '联系人' }]
const taskFilters = reactive({ status: 'all', severity: 'all', category: 'all', faultType: 'all', assignee: 'all', overdue: 'all', keyword: '' })
const taskView = ref('table')
const showTaskForm = ref(false)
const taskForm = reactive({ equipment_name: '', equipment_no: '', equipment_model: '', severity: 'medium', assignee_name: user.name, due_at: '', description: '' })
const recheckForms = reactive({})
const contactKeyword = ref('')
const contactDepartment = ref('all')
const activeConversationId = ref('task-room-1')
const chatInput = ref('')
const chatRecording = ref(false)
const chatRecordSeconds = ref(0)
const showTaskPicker = ref(false)
const taskPickerMode = ref('send')
const reportTask = ref(null)
let chatRecorder = null
let chatRecordStream = null
let chatRecordTimer = null
let chatRecordChunks = []
const chatObjectUrls = new Set()
const chatMessages = ref([
  { id: 'm1', conversationId: 'task-room-1', mine: false, text: 'ZK-320 配电柜温度仍偏高，建议先确认接触器触点和散热风道。', time: '09:42', card: { type: 'task', title: 'YX-20260803-001', desc: '配电柜过热检修 · 高风险' } },
  { id: 'm2', conversationId: 'task-room-1', mine: true, text: '已完成停电验电，准备上传红外测温图片。', time: '09:45' },
  { id: 'm3', conversationId: 'expert-1', mine: false, text: '发动机异响优先复核气门间隙，热车前后各记录一次。', time: '10:15', card: { type: 'knowledge', title: '发动机异响排查知识条目', desc: '气门机构、正时链条、润滑状态' } }
])

const knowledgePanel = ref('network')
const knowledgeTabs = [{ key: 'network', label: '知识网络' }, { key: 'files', label: '文件管理' }, { key: 'library', label: '技术资料库' }, { key: 'update', label: '沉淀更新' }]
const knowledgeKeyword = ref('')
const graphSearchExpanded = ref(false)
const graphSearchInput = ref(null)
const graphKindFilter = ref('all')
const graphDepth = ref(2)
const graphZoom = ref(1)
const graphShowLabels = ref(false)
const graphLayoutMode = ref('force')
const graphRelationFilter = ref('all')
const graphRelationTypes = ['包含', '对应', '导致', '检测', '形成方案', '引用', '提示风险', '沉淀案例', '支撑']
const graphNodePositions = reactive({})
const graphDragging = ref(null)
const mapCanvasRef = ref(null)
const fileKeyword = ref('')
const fileType = ref('all')
const fileView = ref('card')
const activeFolder = ref('全部文件')
const selectedFileRow = ref('')
const selectedGraphNode = ref(null)
const knowledgeForm = reactive({ title: '', type: '历史故障案例', equipment: '', model: '', source: '', tagText: '', summary: '' })
const knowledgeCorrections = reactive({})
const operatorInput = ref('')

const operatorProfiles = {
  home: {
    ...agentProfileMap.tiangong,
    icon: 'dashboard',
    status: 'online',
    statusText: '在线',
    welcome: '我是天工，负责统筹其他器灵，帮你盯住今日任务、系统状态和高风险异常。',
    sampleAsk: '帮我看一下今天优先处理什么？',
    sampleAnswer: '建议先处理高风险配电柜过热工单，再推进待复检任务，同时关注文件解析异常。',
    quickTitle: '生成今日检修简报',
    quickDesc: '汇总任务、风险、知识更新和智能体状态',
    placeholder: '询问今日任务、风险或系统状态',
    actions: ['查看高风险', '任务简报', '系统状态', '知识更新']
  },
  search: {
    ...agentProfileMap.guanwei,
    icon: 'search',
    status: 'online',
    statusText: '在线',
    welcome: '我是观微，输入故障描述、设备型号或上传图片后，我会查找线索、召回资料并生成引用依据。',
    sampleAsk: 'CG-125 发动机热车后异响怎么查？',
    sampleAnswer: '优先检查气门间隙、正时链条张紧器和点火连接，并记录热车复测数据。',
    quickTitle: '执行一次智能检索',
    quickDesc: '汇总故障线索、参考资料和可转任务建议',
    placeholder: '描述故障现象或资料需求',
    actions: ['开始检索', '生成检修建议', '查看引用', '创建任务']
  },
  tasks: {
    ...agentProfileMap.zhiju,
    icon: 'wrench',
    status: 'online',
    statusText: '在线',
    welcome: '我是执矩，负责把检修流程拆成可执行步骤，提醒安全要求并推进工单闭环。',
    sampleAsk: '把当前任务推进到复检阶段。',
    sampleAnswer: '可以。高风险步骤需要二次确认，完成检测记录后再进入复检评估。',
    quickTitle: '打开任务管理',
    quickDesc: '查看工单、筛选风险、执行状态流转',
    placeholder: '输入任务操作或复检意见',
    actions: ['新建任务', '流转任务', '进入复检', '联系人']
  },
  contacts: {
    ...agentProfileMap.heming,
    icon: 'user',
    status: 'online',
    statusText: '在线',
    welcome: '我是和鸣，负责联系人管理、人员协调、专家支援和任务沟通。',
    sampleAsk: '帮我找一个电气安全负责人。',
    sampleAnswer: '建议联系赵宁，他当前负责高风险作业确认，可加入 ZK-320 过热检修任务。',
    quickTitle: '协调现场支援',
    quickDesc: '筛选联系人、发起消息并加入协作任务',
    placeholder: '输入人员、部门或支援需求',
    actions: ['搜索联系人', '请求支援', '添加至任务', '查看协作记录']
  },
  recheck: {
    ...agentProfileMap.mingjian,
    icon: 'check',
    status: 'online',
    statusText: '在线',
    welcome: '我是明鉴，负责复检评估、安全检查、质量核验和任务验收。',
    sampleAsk: '这个任务复检不通过怎么处理？',
    sampleAnswer: '需要记录不通过原因和整改要求，并自动退回检修状态，保留复检数据。',
    quickTitle: '执行复检核查',
    quickDesc: '核对复测数据、安全结果和最终验收意见',
    placeholder: '输入复检意见或验收问题',
    actions: ['保存复检', '退回返工', '查看标准', '生成验收意见']
  },
  knowledge: {
    ...agentProfileMap.bowen,
    icon: 'network',
    status: 'busy',
    statusText: '处理中',
    welcome: '我是博闻，负责整理技术资料、维护知识网络，并把有效检修经验沉淀成系统知识。',
    sampleAsk: '这份维修资料能不能加入知识库？',
    sampleAnswer: '需要先通过文件审核和解析，确认设备、型号、故障、SOP 与原始文件一致。',
    quickTitle: '进入文件管理',
    quickDesc: '上传资料、预览文件、查看解析与审核状态',
    placeholder: '询问资料、文件解析或知识沉淀',
    actions: ['文件管理', '知识网络', '提交沉淀', '资料检索']
  },
  profile: {
    ...agentProfileMap.mingjian,
    icon: 'check',
    status: 'online',
    statusText: '在线',
    welcome: '我是明鉴，会帮你检查项目是否满足设备检修、知识检索、作业闭环和多智能体要求。',
    sampleAsk: '检查一下当前项目能不能答辩。',
    sampleAnswer: '当前已具备工作台、智能检索、任务闭环、知识管理和复检核查能力，文件权限与审核流程还可继续深化。',
    quickTitle: '运行交付核查',
    quickDesc: '检查页面完整性、业务闭环和演示材料准备情况',
    placeholder: '询问个人记录、核查或交付问题',
    actions: ['运行核查', '个人记录', '退出登录', '项目说明']
  }
}

const operatorKey = computed(() => {
  if (activePage.value === 'tasks' && taskPanel.value === 'contacts') return 'contacts'
  if (activePage.value === 'tasks' && taskPanel.value === 'recheck') return 'recheck'
  return activePage.value
})
const operatorProfile = computed(() => {
  const contextual = operatorProfiles[operatorKey.value] || operatorProfiles.home
  const selected = selectedAgentId.value ? agentProfileMap[selectedAgentId.value] : null
  if (!selected) return contextual
  return {
    ...contextual,
    ...selected,
    status: selected.status || 'online',
    statusText: selected.status === 'busy' ? '处理中' : '在线',
    welcome: `我是${selected.name}，${selected.duty}`
  }
})
const currentOperatorMessages = computed(() => operatorMessages.value.filter((message) => message.page === activePage.value))
const todayCompletion = computed(() => {
  const total = overview.stats.pending + overview.stats.inProgress + overview.stats.review + overview.stats.completed
  return Math.round(overview.stats.completed / Math.max(total, 1) * 100)
})

const statCards = computed(() => [
  { key: 'today', label: '今日新增任务', value: overview.stats.todayNew, hint: '点击进入任务管理', page: 'tasks', panel: 'manage' },
  { key: 'pending', label: '待处理任务', value: overview.stats.pending, hint: '自动筛选待处理', page: 'tasks', panel: 'manage', status: 'pending' },
  { key: 'progress', label: '进行中任务', value: overview.stats.inProgress, hint: '查看检修中工单', page: 'tasks', panel: 'manage', status: 'in_progress' },
  { key: 'risk', label: '高风险任务', value: overview.stats.highRisk, hint: '优先处理', page: 'tasks', panel: 'manage', severity: 'high' },
  { key: 'review', label: '待复检任务', value: overview.stats.review, hint: '进入复检评估', page: 'tasks', panel: 'recheck' },
  { key: 'done', label: '已完成任务', value: overview.stats.completed, hint: '查看归档', page: 'tasks', panel: 'manage', status: 'completed' },
  { key: 'kb', label: '知识库资料总量', value: overview.stats.knowledgeTotal, hint: '进入技术资料库', page: 'knowledge', panel: 'library' },
  { key: 'week', label: '本周新增知识', value: overview.stats.weekKnowledge, hint: '进入沉淀更新', page: 'knowledge', panel: 'update' },
  { key: 'users', label: '在线协作人员', value: overview.stats.onlineUsers, hint: '查看联系人', page: 'tasks', panel: 'contacts' }
])

const visibleTodayTasks = computed(() => tasks.value.slice(0, 6))
const alerts = computed(() => [
  { title: '高风险工单', desc: `${tasks.value.filter((task) => task.severity === 'high').length} 个任务需要二次确认`, tone: 'danger', icon: 'bell', action: () => goStat({ page: 'tasks', panel: 'manage', severity: 'high' }) },
  { title: '待复检任务', desc: `${tasks.value.filter((task) => task.status === 'review').length} 个任务等待复测数据`, tone: 'amber', icon: 'check', action: () => goStat({ page: 'tasks', panel: 'recheck' }) },
  { title: '知识审核异常', desc: '1 份资料解析部分成功，请人工复核', tone: 'violet', icon: 'network', action: () => goStat({ page: 'knowledge', panel: 'files' }) },
  { title: '智能服务状态', desc: systemStatus.ai, tone: 'teal', icon: 'cpu', action: () => activePage.value = 'profile' }
])
const quickActions = [
  { label: '发起智能检索', desc: '检索故障与资料', icon: 'search', tone: 'blue', action: () => activePage.value = 'search' },
  { label: '新建检修任务', desc: '创建现场工单', icon: 'wrench', tone: 'teal', action: () => { activePage.value = 'tasks'; taskPanel.value = 'manage'; showTaskForm.value = true } },
  { label: '上传维修资料', desc: '补充知识文件', icon: 'network', tone: 'violet', action: () => { activePage.value = 'knowledge'; knowledgePanel.value = 'files' } },
  { label: '查看高风险任务', desc: '优先确认风险', icon: 'bell', tone: 'amber', action: () => goStat({ page: 'tasks', panel: 'manage', severity: 'high' }) },
  { label: '进入复检评估', desc: '核对复测结果', icon: 'check', tone: 'blue', action: () => goStat({ page: 'tasks', panel: 'recheck' }) },
  { label: '查看知识网络', desc: '浏览知识关系', icon: 'network', tone: 'teal', action: () => goStat({ page: 'knowledge', panel: 'network' }) },
  { label: '联系现场负责人', desc: '发起协作沟通', icon: 'user', tone: 'violet', action: () => goStat({ page: 'tasks', panel: 'contacts' }) },
  { label: '个人检修记录', desc: '查看工作档案', icon: 'dashboard', tone: 'amber', action: () => activePage.value = 'profile' }
]
const trendPoints = computed(() => overview.trend.map((value, index) => `${index * 100 + 24},${220 - value * 8}`).join(' '))
const trendLabels = ['周一', '周二', '周三', '周四', '周五', '周六', '今天']
const faultColors = ['#e15d50', '#e69a35', '#387dc2', '#8d68c7', '#6f8992']
const knowledgeColors = ['#4f82c4', '#8b67c7', '#dc8a35', '#2b9383']
const recentActivities = computed(() => {
  const styles = {
    检索: { icon: 'search', tone: 'blue' },
    查看: { icon: 'network', tone: 'violet' },
    上传: { icon: 'tool', tone: 'amber' },
    收藏: { icon: 'check', tone: 'teal' }
  }
  return overview.recent.map((raw) => {
    const [action = '记录', ...rest] = raw.split(/[：:]/)
    return { raw, action, content: rest.join('：').trim() || raw, ...(styles[action] || { icon: 'dashboard', tone: 'blue' }) }
  })
})
const runRecentActivity = (item) => {
  if (item.action === '检索') {
    activePage.value = 'search'
    searchForm.query = item.content
    return
  }
  if (item.action === '上传') return goStat({ page: 'knowledge', panel: 'files' })
  knowledgeKeyword.value = item.content.replace(/\s*SOP$/i, '')
  goStat({ page: 'knowledge', panel: 'library' })
}

const recommendationResult = computed(() => searchResult.value ? {
  id: 'recommendation-current',
  title: `${searchForm.deviceModel || searchForm.deviceName} ${searchForm.faultType}推荐检修方案`,
  type: '推荐检修方案',
  category: '推荐检修方案',
  equipment: searchForm.deviceName,
  model: searchForm.deviceModel,
  match: searchResult.value.confidence || 88,
  summary: `${searchResult.value.stopAdvice || '结合现场安全要求逐项检查'}；共 ${searchResult.value.suggestion?.steps?.length || 0} 个建议步骤。`,
  tags: ['智能研判', searchForm.faultType, searchForm.maintenanceLevel]
} : null)
const filterResultsByTab = (tab) => {
  const list = searchResult.value?.references || []
  if (tab === '推荐检修方案') return recommendationResult.value ? [recommendationResult.value] : []
  if (tab === '全部') return recommendationResult.value ? [...list, recommendationResult.value] : list
  const aliases = {
    '维修手册': ['维修手册'],
    '历史故障案例': ['历史故障案例', '案例'],
    '标准作业流程 SOP': ['标准作业流程 SOP', '标准作业流程', 'SOP'],
    '安全操作规范': ['安全操作规范', '安全规范']
  }
  return list.filter((item) => aliases[tab]?.some((name) => item.type === name || item.category === name))
}
const filteredResults = computed(() => filterResultsByTab(resultTab.value))
const resultTabHint = computed(() => resultTabCopy[resultTab.value])
const resultCountFor = (tab) => filterResultsByTab(tab).length
const selectResultTab = (tab) => {
  resultTab.value = tab
  const count = resultCountFor(tab)
  toast(searchResult.value ? `已切换至${tab}，共 ${count} 条结果` : `已选择${tab}，请先执行智能检索`)
}
const filteredTasks = computed(() => tasks.value.filter((task) => {
  const keyword = taskFilters.keyword.trim()
  const statusOk = taskFilters.status === 'all' || task.status === taskFilters.status
  const severityOk = taskFilters.severity === 'all' || task.severity === taskFilters.severity
  const categoryOk = taskFilters.category === 'all' || task.equipment_category === taskFilters.category
  const faultTypeOk = taskFilters.faultType === 'all' || task.fault_type === taskFilters.faultType
  const assigneeOk = taskFilters.assignee === 'all' || task.assignee_name === taskFilters.assignee || task.collaborators?.includes(taskFilters.assignee)
  const overdueOk = taskFilters.overdue === 'all' || (taskFilters.overdue === 'yes' ? isTaskOverdue(task) : !isTaskOverdue(task))
  const keywordOk = !keyword || JSON.stringify(task).includes(keyword)
  return statusOk && severityOk && categoryOk && faultTypeOk && assigneeOk && overdueOk && keywordOk
}))
const taskOverviewCards = computed(() => [
  { label: '今日任务总数', value: tasks.value.length, hint: '全部任务', filter: {} },
  { label: '待接收任务', value: tasks.value.filter((task) => task.status === 'pending').length, hint: '等待接收', filter: { status: 'pending' } },
  { label: '待处理任务', value: tasks.value.filter((task) => ['pending', 'in_progress'].includes(task.status)).length, hint: '需推进', filter: { status: 'pending' } },
  { label: '检修中任务', value: tasks.value.filter((task) => task.status === 'in_progress').length, hint: '现场处理中', filter: { status: 'in_progress' } },
  { label: '待复检任务', value: tasks.value.filter((task) => task.status === 'review').length, hint: '等待验收', filter: { status: 'review' } },
  { label: '已完成任务', value: tasks.value.filter((task) => task.status === 'completed').length, hint: '今日归档', filter: { status: 'completed' } },
  { label: '高风险任务', value: tasks.value.filter((task) => task.severity === 'high').length, hint: '优先确认', filter: { severity: 'high' } },
  { label: '已逾期任务', value: tasks.value.filter(isTaskOverdue).length, hint: '需要协调', filter: { overdue: 'yes' } },
  { label: '今日完成率', value: `${Math.round(tasks.value.filter((task) => task.status === 'completed').length / Math.max(tasks.value.length, 1) * 100)}%`, hint: '按任务数计算' },
  { label: '复检通过率', value: '92%', hint: '近 7 天' }
])
const countBy = (list, getter) => {
  const map = new Map()
  list.forEach((item) => {
    const key = getter(item) || '未分类'
    map.set(key, (map.get(key) || 0) + 1)
  })
  return [...map.entries()].map(([key, count]) => ({ key, label: key, count, percent: Math.round(count / Math.max(list.length, 1) * 100) }))
}
const taskStatusAnalysis = computed(() => countBy(tasks.value, (task) => task.status).map((item) => ({ ...item, label: statusText(item.key) })))
const taskRiskAnalysis = computed(() => countBy(tasks.value, (task) => task.severity).map((item) => ({ ...item, label: severityText(item.key) })))
const taskCategoryAnalysis = computed(() => countBy(tasks.value, (task) => task.equipment_category).slice(0, 5))
const faultRankAnalysis = computed(() => countBy(tasks.value, (task) => task.fault_type).sort((a, b) => b.count - a.count).slice(0, 5))
const taskTrendData = computed(() => overview.trend?.length ? overview.trend.slice(0, 7) : [3, 4, 2, 5, 4, 6, tasks.value.length])
const taskTrendDots = computed(() => {
  const max = Math.max(...taskTrendData.value, 1)
  return taskTrendData.value.map((value, index) => ({ x: 34 + index * 44, y: 124 - value / max * 76 }))
})
const taskTrendPoints = computed(() => taskTrendDots.value.map((point) => `${point.x},${point.y}`).join(' '))
const taskTrendAreaPoints = computed(() => `34,132 ${taskTrendPoints.value} ${taskTrendDots.value.at(-1)?.x || 298},132`)
const taskTrendTotal = computed(() => taskTrendData.value.reduce((total, value) => total + Number(value || 0), 0))
const taskTrendChange = computed(() => Number(taskTrendData.value.at(-1) || 0) - Number(taskTrendData.value.at(-2) || 0))
const priorityTasks = computed(() => tasks.value.filter((task) => task.severity === 'high' || task.status === 'review' || isTaskOverdue(task) || task.progress < 25).slice(0, 5))
const taskEvents = computed(() => tasks.value.flatMap((task, index) => [
  { id: `${task.id}-create`, time: task.created_at, text: `${task.title} 已创建，负责人 ${task.assignee_name}` },
  { id: `${task.id}-step`, time: task.due_at, text: `${task.equipment_name} 当前步骤：${task.current_step}，进度 ${task.progress}%` },
  ...(task.status === 'review' ? [{ id: `${task.id}-review`, time: task.due_at, text: `${task.title} 已提交复检，等待复测数据` }] : []),
  ...(index === 0 ? [{ id: `${task.id}-risk`, time: task.created_at, text: `${task.title} 已标记为重点任务，需确认安全措施` }] : [])
]).slice(0, 10))
const taskBoardColumns = computed(() => ['pending', 'in_progress', 'review', 'completed'].map((key) => ({ key, label: statusText(key), tasks: filteredTasks.value.filter((task) => task.status === key) })))
const myTasks = computed(() => tasks.value.filter((item) => item.assignee_name === user.name || item.collaborators?.includes(user.name)))
const profileSections = computed(() => [
  {
    key: 'work',
    group: '我的工作',
    title: '当前与我相关的任务',
    span: 'span-6',
    action: '进入检修任务',
    page: 'tasks',
    panel: 'manage',
    metrics: [
      { label: '待我接收', value: tasks.value.filter((task) => task.assignee_name === user.name && task.status === 'pending').length },
      { label: '由我负责', value: tasks.value.filter((task) => task.assignee_name === user.name).length },
      { label: '我参与', value: myTasks.value.length }
    ],
    items: myTasks.value.slice(0, 3).map((task) => ({ title: task.title, desc: `${task.equipment_name} · ${statusText(task.status)} · ${task.progress}%`, page: 'tasks', panel: 'manage' }))
  },
  {
    key: 'schedule',
    group: '我的日程',
    title: '近期检修安排',
    span: 'span-6',
    action: '查看任务日程',
    page: 'tasks',
    panel: 'overview',
    items: tasks.value.slice(0, 4).map((task) => ({ title: task.due_at, desc: `${task.title} · ${task.current_step}`, page: 'tasks', panel: 'overview' }))
  },
  {
    key: 'archive',
    group: '我的检修档案',
    title: '长期工作经历',
    span: 'span-4',
    metrics: [
      { label: '参与设备', value: new Set(myTasks.value.map((task) => task.equipment_name)).size },
      { label: '故障类型', value: new Set(myTasks.value.map((task) => task.fault_type)).size }
    ],
    items: ['执行过的 SOP：12 个', '更换过的零部件：18 类', '典型案例：3 条'].map((text) => ({ title: text, desc: '来自已完成检修报告' }))
  },
  {
    key: 'files',
    group: '我的资料',
    title: '上传、收藏和最近使用',
    span: 'span-4',
    action: '进入知识库文件',
    page: 'knowledge',
    panel: 'files',
    items: files.value.slice(0, 4).map((file) => ({ title: file.name, desc: `${file.auditStatus} · ${file.parseStatus}`, page: 'knowledge', panel: 'files' }))
  },
  {
    key: 'contribution',
    group: '我的知识贡献',
    title: '案例沉淀与资料引用',
    span: 'span-4',
    action: '继续完善',
    page: 'knowledge',
    panel: 'update',
    metrics: [
      { label: '已通过', value: knowledge.value.filter((item) => item.status === 'approved').length },
      { label: '审核中', value: knowledge.value.filter((item) => item.status !== 'approved').length }
    ],
    items: knowledge.value.slice(0, 3).map((item) => ({ title: item.title, desc: `引用 ${item.citations || 0} 次 · ${item.status === 'approved' ? '已通过' : '待完善'}`, page: 'knowledge', panel: 'update' }))
  },
  {
    key: 'collaboration',
    group: '我的协作',
    title: '常用联系人和支援请求',
    span: 'span-4',
    action: '联系人员',
    page: 'tasks',
    panel: 'contacts',
    items: contacts.value.slice(0, 3).map((contact) => ({ title: contact.name, desc: `${contact.position} · ${contact.specialty}`, page: 'tasks', panel: 'contacts' }))
  },
  {
    key: 'messages',
    group: '我的消息',
    title: '业务通知',
    span: 'span-4',
    items: [
      { title: '任务分配', desc: 'ZK-320 配电柜过热检修等待接收', page: 'tasks', panel: 'manage' },
      { title: '复检通知', desc: '液压千斤顶渗漏处理等待复测数据', page: 'tasks', panel: 'recheck' },
      { title: '文件审核', desc: '一份 SOP 资料需要补充适用设备', page: 'knowledge', panel: 'files' }
    ]
  },
  {
    key: 'growth',
    group: '能力与成长',
    title: '个人能力积累',
    span: 'span-4',
    metrics: [
      { label: '完成率', value: '94%' },
      { label: '复检通过率', value: '92%' },
      { label: '平均处理', value: '3.4h' }
    ],
    items: ['培训记录：高压安全作业', '资格：电气检修高级', '擅长：发动机/电气'].map((text) => ({ title: text, desc: '个人能力档案' }))
  },
  {
    key: 'settings',
    group: '账号与偏好',
    title: '提醒和界面设置',
    span: 'span-4',
    items: [
      { title: '账号资料与安全', desc: `当前登录：${currentAccount.value || '未登录'}`, action: 'edit-profile' },
      { title: '高风险提醒：开启', desc: '重要风险变化将及时提醒' },
      { title: '复检提醒：开启', desc: '待复检任务进入队列后提醒' },
      { title: '退出当前账号', desc: '安全返回登录页面', action: 'logout' }
    ]
  }
])
const recheckTasks = computed(() => tasks.value.filter((task) => ['review', 'completed'].includes(task.status) || task.progress >= 80))
const pendingKnowledge = computed(() => knowledge.value.filter((item) => item.status === 'pending' && item.reviewable))
const departments = computed(() => [...new Set(contacts.value.map((item) => item.department))])
const filteredContacts = computed(() => contacts.value.filter((contact) => {
  const keywordOk = !contactKeyword.value || JSON.stringify(contact).includes(contactKeyword.value)
  const deptOk = contactDepartment.value === 'all' || contact.department === contactDepartment.value
  return keywordOk && deptOk
}))
const conversations = computed(() => [
  { id: 'task-room-1', name: 'ZK-320 过热检修群', avatar: '/static/agents/heming.png', position: '任务群组', department: '动力设备检修一组', specialty: '高风险任务协作', devices: ['配电柜', 'ZK-320'], currentTask: 'ZK-320 配电柜过热检修', workload: 78, lastMessage: '已上传红外测温图片', unread: 3, taskNo: 'YX-20260803-001', risk: 'high' },
  ...contacts.value.map((contact, index) => ({
    id: String(contact.id || '').startsWith('local-group-') ? `contact-${contact.id}` : index === 0 ? 'expert-1' : `contact-${contact.id}`,
    name: contact.name,
    avatar: contact.avatar,
    position: contact.position,
    department: contact.department,
    specialty: contact.specialty,
    devices: contact.devices,
    currentTask: contact.currentTask,
    workload: contact.workload,
    lastMessage: index === 0 ? '已给出异响排查建议' : '等待现场反馈',
    unread: index === 1 ? 1 : 0,
    taskNo: contact.currentTask,
    risk: index === 2 ? 'high' : 'medium'
  }))
])
const filteredConversations = computed(() => conversations.value.filter((item) => !contactKeyword.value || JSON.stringify(item).includes(contactKeyword.value)))
const activeConversation = computed(() => conversations.value.find((item) => item.id === activeConversationId.value) || conversations.value[0])
const activeMessages = computed(() => chatMessages.value.filter((item) => item.conversationId === activeConversation.value?.id))
const graphPositions = [
  [12, 18], [31, 12], [55, 14], [76, 18], [88, 39], [78, 64],
  [57, 78], [34, 76], [14, 61], [9, 39], [25, 48], [46, 35],
  [63, 43], [43, 58], [66, 63], [30, 31], [52, 22], [72, 30]
]
const layoutPoint = (index, total) => {
  if (graphLayoutMode.value === 'circle') {
    const angle = Math.PI * 2 * index / Math.max(total, 1)
    return [50 + Math.cos(angle) * 36, 50 + Math.sin(angle) * 34]
  }
  if (graphLayoutMode.value === 'tree') {
    const level = Math.floor(index / 7)
    return [14 + (index % 7) * 12, 22 + level * 20]
  }
  return graphPositions[index % graphPositions.length]
}
const graphKindMeta = {
  equipment: { text: '设备', important: true },
  model: { text: '设备型号' },
  part: { text: '零部件' },
  fault: { text: '故障现象', important: true },
  cause: { text: '故障原因' },
  method: { text: '检测方法' },
  solution: { text: '检修方案' },
  sop: { text: 'SOP', important: true },
  risk: { text: '安全风险' },
  case: { text: '历史案例' },
  doc: { text: '技术资料', important: true }
}
const graphLegend = Object.entries(graphKindMeta).map(([kind, meta]) => ({ kind, label: meta.text }))
const cleanGraphLabel = (value, fallback) => {
  const text = String(value || fallback || '').replace(/[\[\]{}"']/g, '').replace(/\s+/g, ' ').trim()
  return text.length > 12 ? `${text.slice(0, 12)}…` : text
}
const graphNodes = computed(() => {
  const keyword = knowledgeKeyword.value.trim()
  const graphKnowledge = knowledge.value.filter((item) => !item.status || item.status === 'approved' || item.status === '已通过')
  const expandedNodes = graphKnowledge.flatMap((item) => [
    { id: `${item.id}-equipment`, label: cleanGraphLabel(item.equipment, '通用设备'), kind: 'equipment', source: item, level: 1 },
    { id: `${item.id}-model`, label: cleanGraphLabel(item.model, '通用型号'), kind: 'model', source: item, level: 1 },
    { id: `${item.id}-part`, label: cleanGraphLabel(item.tags?.[0], '关键部件'), kind: 'part', source: item, level: 2 },
    { id: `${item.id}-fault`, label: cleanGraphLabel(item.tags?.[1] || item.category || item.type, '故障现象'), kind: 'fault', source: item, level: 1 },
    { id: `${item.id}-cause`, label: cleanGraphLabel(knowledgeSummaryLines(item)[0], '故障原因'), kind: 'cause', source: item, level: 2 },
    { id: `${item.id}-method`, label: item.type?.includes('安全') ? '安全检查' : '检测方法', kind: 'method', source: item, level: 2 },
    { id: `${item.id}-solution`, label: item.category || '检修方案', kind: 'solution', source: item, level: 2 },
    { id: `${item.id}-sop`, label: cleanGraphLabel(item.type?.includes('SOP') ? item.title : '标准步骤'), kind: 'sop', source: item, level: 2 },
    { id: `${item.id}-risk`, label: item.tags?.includes('安全') ? '作业风险' : '安全风险', kind: 'risk', source: item, level: 3 },
    { id: `${item.id}-case`, label: item.type?.includes('案例') ? item.title : '历史案例', kind: 'case', source: item, level: 3 },
    { id: `${item.id}-doc`, label: cleanGraphLabel(item.title, '技术资料'), kind: 'doc', source: item, level: 1 }
  ])
    .filter((node) => node.level <= graphDepth.value)
    .filter((node) => graphKindFilter.value === 'all' || node.kind === graphKindFilter.value)
  const seen = new Set()
  const rawNodes = expandedNodes.filter((node) => {
    const key = `${node.kind}-${node.label}`
    if (seen.has(key)) return false
    seen.add(key)
    return true
  }).slice(0, graphDepth.value === 1 ? 14 : graphDepth.value === 2 ? 24 : 34)

  return rawNodes.map((node, index) => {
    const [defaultX, defaultY] = layoutPoint(index, rawNodes.length)
    const fixed = graphNodePositions[node.id]
    const meta = graphKindMeta[node.kind] || graphKindMeta.doc
    return {
      ...node,
      x: fixed?.x ?? defaultX,
      y: fixed?.y ?? defaultY,
      kindText: meta.text,
      important: Boolean(meta.important),
      summary: node.source?.summary || node.source?.content || '该节点已关联设备、故障现象、维修资料和检修任务，可继续展开查看上下游依据。',
      tags: node.source?.tags?.length ? node.source.tags : [meta.text, node.source?.model || '通用型号', node.source?.type || '知识条目'],
      matched: keyword ? JSON.stringify(node).includes(keyword) || JSON.stringify(node.source || {}).includes(keyword) : false
    }
  })
})
const graphEdges = computed(() => {
  const radial = graphNodes.value.map((node, index) => ({
    id: `edge-${node.id}`,
    x1: 410,
    y1: 260,
    x2: Math.round(node.x / 100 * 820),
    y2: Math.round(node.y / 100 * 520),
    faint: selectedGraphNode.value && selectedGraphNode.value.id !== node.id && node.source?.id !== selectedGraphNode.value.source?.id,
    label: graphRelationTypes[index % graphRelationTypes.length]
  })).filter((edge) => graphRelationFilter.value === 'all' || edge.label === graphRelationFilter.value)
  const mesh = graphNodes.value.slice(0, -1).map((node, index) => {
    const next = graphNodes.value[index + 1]
    return {
      id: `mesh-${node.id}-${next.id}`,
      x1: Math.round(node.x / 100 * 820),
      y1: Math.round(node.y / 100 * 520),
      x2: Math.round(next.x / 100 * 820),
      y2: Math.round(next.y / 100 * 520),
      faint: true
    }
  })
  return [...radial, ...mesh]
})
const filteredKnowledge = computed(() => {
  if (!knowledgeKeyword.value) return knowledge.value
  return knowledge.value.filter((item) => JSON.stringify(item).includes(knowledgeKeyword.value))
})
const filteredFiles = computed(() => files.value.filter((file) => {
  const keywordOk = !fileKeyword.value || JSON.stringify(file).includes(fileKeyword.value)
  const typeOk = fileType.value === 'all' || file.type === fileType.value
  const folderOk = activeFolder.value === '全部文件' || file.folder === activeFolder.value || file.category === activeFolder.value
  return keywordOk && typeOk && folderOk
}))
const fileFolders = computed(() => {
  const fixed = ['全部文件', '维修手册', '标准作业流程', '现场图片', '检修报告', '复检报告', '其他技术资料']
  const dynamic = files.value.map((file) => file.folder || file.category).filter(Boolean)
  return [...new Set([...fixed, ...dynamic])]
})

const getAccounts = () => {
  const stored = readStorage(AUTH_ACCOUNTS_KEY, [])
  return [defaultAccount, ...stored.filter((item) => item.account !== defaultAccount.account)]
}
const profileToContact = (profile, account = currentAccount.value) => ({
  id: `account-${account || profile.employeeId}`,
  account,
  name: profile.name,
  avatar: profile.avatar || '',
  position: profile.role || '检修人员',
  department: profile.department || '待分配班组',
  specialty: (profile.specialties || []).join(' / ') || '设备检修',
  devices: profile.specialties || [],
  currentTask: '暂无在办任务',
  workload: 0,
  status: '在线',
  employeeId: profile.employeeId,
  phone: profile.phone || ''
})
const syncProfileContact = (profile, account = currentAccount.value) => {
  if (!profile?.name || !account) return
  const directory = readStorage(CONTACT_DIRECTORY_KEY, [])
  const contact = profileToContact(profile, account)
  const index = directory.findIndex((item) => item.account === account || item.employeeId === contact.employeeId)
  if (index >= 0) directory[index] = { ...directory[index], ...contact }
  else directory.push(contact)
  localStorage.setItem(CONTACT_DIRECTORY_KEY, JSON.stringify(directory))
  const liveIndex = contacts.value.findIndex((item) => item.id === contact.id)
  if (liveIndex >= 0) contacts.value[liveIndex] = contact
  else contacts.value.push(contact)
  void yixiuApi.upsertContact(contact).catch(() => {})
}
const setAuthMode = (mode) => {
  authMode.value = mode
  authError.value = ''
  authForm.password = ''
  authForm.confirmPassword = ''
}
const applyAccountProfile = (account) => {
  const savedProfile = account.account === defaultAccount.account ? readStorage(PROFILE_KEY, {}) : account.profile || {}
  Object.assign(user, defaultProfile, savedProfile, { name: savedProfile.name || account.name || defaultProfile.name })
}
const startWorkspace = async () => {
  updateClock()
  if (!clockTimer) clockTimer = window.setInterval(updateClock, 1000)
  showSplash.value = true
  await nextTick()
  playBootAnimation()
  window.setTimeout(() => { refreshAll() }, 260)
}
const login = async () => {
  const accountName = authForm.account.trim()
  if (!accountName || !authForm.password) return (authError.value = '请输入账号和密码')
  const account = getAccounts().find((item) => item.account === accountName)
  if (!account || account.password !== authForm.password) return (authError.value = '账号或密码不正确，请重新输入')
  applyAccountProfile(account)
  const session = JSON.stringify({ account: account.account, loginAt: Date.now() })
  localStorage.removeItem(AUTH_SESSION_KEY)
  sessionStorage.removeItem(AUTH_SESSION_KEY)
  if (authForm.remember) localStorage.setItem(AUTH_SESSION_KEY, session)
  else sessionStorage.setItem(AUTH_SESSION_KEY, session)
  currentAccount.value = account.account
  authError.value = ''
  isAuthenticated.value = true
  authForm.password = ''
  await startWorkspace()
}
const register = async () => {
  const name = authForm.name.trim()
  const accountName = authForm.account.trim()
  if (!name || !accountName || !authForm.password || !authForm.confirmPassword) return (authError.value = '请完整填写注册信息')
  if (!/^[A-Za-z0-9_]{4,20}$/.test(accountName)) return (authError.value = '账号需为 4—20 位字母、数字或下划线')
  if (authForm.password.length < 8) return (authError.value = '密码至少需要 8 位')
  if (authForm.password !== authForm.confirmPassword) return (authError.value = '两次输入的密码不一致')
  if (!authForm.agreed) return (authError.value = '请先同意平台使用规范')
  if (getAccounts().some((item) => item.account === accountName)) return (authError.value = '该账号已存在，请直接登录')
  const profile = { ...defaultProfile, name, employeeId: `YX-${String(Date.now()).slice(-6)}` }
  const accounts = readStorage(AUTH_ACCOUNTS_KEY, [])
  accounts.push({ account: accountName, password: authForm.password, name, profile })
  localStorage.setItem(AUTH_ACCOUNTS_KEY, JSON.stringify(accounts))
  sessionStorage.removeItem(AUTH_SESSION_KEY)
  localStorage.setItem(AUTH_SESSION_KEY, JSON.stringify({ account: accountName, loginAt: Date.now() }))
  currentAccount.value = accountName
  Object.assign(user, profile)
  syncProfileContact(profile, accountName)
  authError.value = ''
  isAuthenticated.value = true
  await startWorkspace()
}
const logout = () => {
  if (assistantSpeechRecognition) assistantSpeechRecognition.stop()
  if (speechRecognition) speechRecognition.stop()
  assistantSpeechRecognition = null
  speechRecognition = null
  assistantVoiceListening.value = false
  voiceListening.value = false
  localStorage.removeItem(AUTH_SESSION_KEY)
  sessionStorage.removeItem(AUTH_SESSION_KEY)
  isAuthenticated.value = false
  currentAccount.value = ''
  activePage.value = 'home'
  showSplash.value = false
  authMode.value = 'login'
  authForm.account = 'yixiu'
  authForm.password = ''
  authForm.confirmPassword = ''
  showProfileEditor.value = false
  showTaskForm.value = false
  selectedTask.value = null
  selectedFile.value = null
  selectedKnowledge.value = null
  selectedAgentId.value = ''
  releaseFileUrls(assistantFiles.value)
  releaseFileUrls(searchFiles.value)
  assistantFiles.value = []
  searchFiles.value = []
  operatorInput.value = ''
  chatInput.value = ''
  authError.value = ''
}
const openProfileEditor = () => {
  Object.assign(profileDraft, user, { specialtyText: (user.specialties || []).join('，') })
  profileError.value = ''
  showProfileEditor.value = true
}
const saveProfile = () => {
  if (!profileDraft.name || !profileDraft.employeeId || !profileDraft.role || !profileDraft.department) {
    profileError.value = '姓名、工号、岗位和所属班组不能为空'
    return
  }
  const specialties = profileDraft.specialtyText.split(/[,，]/).map((item) => item.trim()).filter(Boolean).slice(0, 5)
  if (!specialties.length) return (profileError.value = '请至少填写一个专业方向')
  const saved = {
    name: profileDraft.name,
    avatar: profileDraft.avatar || defaultProfile.avatar,
    employeeId: profileDraft.employeeId,
    role: profileDraft.role,
    department: profileDraft.department,
    skillLevel: profileDraft.skillLevel,
    phone: profileDraft.phone,
    specialties,
    bio: profileDraft.bio
  }
  Object.assign(user, saved)
  if (currentAccount.value === defaultAccount.account) localStorage.setItem(PROFILE_KEY, JSON.stringify(saved))
  if (currentAccount.value && currentAccount.value !== defaultAccount.account) {
    const accounts = readStorage(AUTH_ACCOUNTS_KEY, [])
    const index = accounts.findIndex((item) => item.account === currentAccount.value)
    if (index >= 0) {
      accounts[index] = { ...accounts[index], name: saved.name, profile: saved }
      localStorage.setItem(AUTH_ACCOUNTS_KEY, JSON.stringify(accounts))
    }
  }
  taskForm.assignee_name = user.name
  syncProfileContact(saved)
  showProfileEditor.value = false
  toast('个人资料已保存并同步')
}

const updateClock = () => {
  nowText.value = new Intl.DateTimeFormat('zh-CN', { dateStyle: 'full', timeStyle: 'medium' }).format(new Date())
}

const refreshAll = async () => {
  const [overviewData, healthData, taskData, knowledgeData, fileData, contactData] = await Promise.all([
    yixiuApi.overview(),
    yixiuApi.health(),
    yixiuApi.tasks(),
    yixiuApi.knowledge(),
    yixiuApi.files(),
    yixiuApi.contacts()
  ])
  Object.assign(overview, overviewData)
  Object.assign(systemStatus, healthData)
  tasks.value = taskData
  knowledge.value = knowledgeData
  files.value = fileData
  const localDirectory = readStorage(CONTACT_DIRECTORY_KEY, [])
  contacts.value = [...contactData]
  localDirectory.forEach((contact) => {
    const index = contacts.value.findIndex((item) => item.id === contact.id || item.employeeId === contact.employeeId)
    if (index >= 0) contacts.value[index] = { ...contacts.value[index], ...contact }
    else contacts.value.push(contact)
  })
  agents.value = normalizeAgentList(overviewData.agents)
  initRecheckForms()
}

const initRecheckForms = () => {
  tasks.value.forEach((task) => {
    if (!recheckForms[task.id]) recheckForms[task.id] = { result: task.recheck?.result || '通过', comment: task.recheck?.comment || '' }
  })
}

const switchPage = (key) => {
  activePage.value = key
  selectedAgentId.value = ''
}
const runGlobalSearch = () => {
  const keyword = globalKeyword.value.trim()
  if (!keyword) return toast('请输入工单、设备、资料或联系人关键词')
  const matchedTask = tasks.value.some((item) => JSON.stringify(item).includes(keyword))
  const matchedKnowledge = knowledge.value.some((item) => JSON.stringify(item).includes(keyword))
  const matchedContact = contacts.value.some((item) => JSON.stringify(item).includes(keyword))
  if (matchedTask) {
    activePage.value = 'tasks'
    taskPanel.value = 'manage'
    taskFilters.keyword = keyword
    return toast(`已定位相关检修任务：${keyword}`)
  }
  if (matchedKnowledge) {
    activePage.value = 'knowledge'
    knowledgePanel.value = 'library'
    knowledgeKeyword.value = keyword
    return toast(`已定位相关知识资料：${keyword}`)
  }
  if (matchedContact) {
    activePage.value = 'tasks'
    taskPanel.value = 'contacts'
    contactKeyword.value = keyword
    return toast(`已定位相关联系人：${keyword}`)
  }
  activePage.value = 'search'
  searchForm.query = keyword
  toast('未找到直接匹配，已转入智能检索')
}
const focusAgent = (agent) => {
  selectedAgentId.value = agent.id
  operatorMessages.value.push({
    id: `agent-${Date.now()}`,
    page: activePage.value,
    role: 'assistant',
    text: `${agent.name}已接入当前页面。${agent.lastResult || agent.duty}`
  })
}
const openGraphSearch = async () => {
  graphSearchExpanded.value = true
  await nextTick()
  graphSearchInput.value?.focus()
}
const resetGraphView = () => {
  graphZoom.value = 1
  graphKindFilter.value = 'all'
  graphDepth.value = 2
  graphShowLabels.value = false
  selectedGraphNode.value = null
  Object.keys(graphNodePositions).forEach((key) => delete graphNodePositions[key])
}
const relayoutGraph = () => {
  Object.keys(graphNodePositions).forEach((key) => delete graphNodePositions[key])
  selectedGraphNode.value = null
}
const startGraphDrag = (node, event) => {
  graphDragging.value = node.id
  event.currentTarget.setPointerCapture?.(event.pointerId)
}
const dragGraphNode = (event) => {
  if (!graphDragging.value || !mapCanvasRef.value) return
  const rect = mapCanvasRef.value.getBoundingClientRect()
  const x = Math.min(94, Math.max(6, (event.clientX - rect.left) / rect.width * 100))
  const y = Math.min(92, Math.max(8, (event.clientY - rect.top) / rect.height * 100))
  graphNodePositions[graphDragging.value] = { x, y }
}
const stopGraphDrag = () => {
  graphDragging.value = null
}
const isTaskOverdue = (task) => task.status !== 'completed' && new Date(task.due_at).getTime() < Date.now()
const remainingTime = (task) => {
  const diff = new Date(task.due_at).getTime() - Date.now()
  if (diff <= 0) return '已逾期'
  const hours = Math.ceil(diff / 3600000)
  return hours > 24 ? `${Math.ceil(hours / 24)}天` : `${hours}小时`
}
const applyTaskMetric = (card) => {
  taskPanel.value = 'manage'
  Object.assign(taskFilters, { status: 'all', severity: 'all', category: 'all', faultType: 'all', assignee: 'all', overdue: 'all', keyword: '' }, card.filter || {})
}
const filterTaskBy = (type, value) => {
  taskPanel.value = 'manage'
  if (type === 'status') taskFilters.status = value
  if (type === 'severity') taskFilters.severity = value
  if (type === 'category') taskFilters.category = value
  if (type === 'faultType') taskFilters.faultType = value
}
const goStat = (card) => {
  activePage.value = card.page || 'home'
  if (card.panel) {
    if (card.page === 'tasks') taskPanel.value = card.panel
    if (card.page === 'knowledge') knowledgePanel.value = card.panel
  }
  if (card.status) taskFilters.status = card.status
  if (card.severity) taskFilters.severity = card.severity
}
const runQuickAction = (item) => item.action()
const runAlert = (alert) => alert.action()
const runProfileAction = (section) => {
  if (section.page) goStat({ page: section.page, panel: section.panel })
  else toast('已打开个人设置')
}
const runProfileItem = (item) => {
  if (item.action === 'edit-profile') return openProfileEditor()
  if (item.action === 'logout') return logout()
  if (item.page) goStat({ page: item.page, panel: item.panel })
  else toast(item.title)
}
const sendChatMessage = (text) => {
  const value = String(text || '').trim()
  if (!value || !activeConversation.value) return
  const message = { id: `msg-${Date.now()}`, conversationId: activeConversation.value.id, mine: true, text: value, time: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }) }
  chatMessages.value.push(message)
  void yixiuApi.sendConversationMessage(message.conversationId, { ...message, sender_id: currentAccount.value, sender_name: user.name }).catch(() => {})
  chatInput.value = ''
}
const pushAttachmentMessage = (attachment, text) => {
  if (!activeConversation.value) return
  const message = { id: `attachment-${Date.now()}-${Math.random()}`, conversationId: activeConversation.value.id, mine: true, text, attachment, time: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }) }
  chatMessages.value.push(message)
  const portableAttachment = { kind: attachment.kind, name: attachment.name, size: attachment.size, type: attachment.type, duration: attachment.duration || 0 }
  void yixiuApi.sendConversationMessage(message.conversationId, { ...message, attachment: portableAttachment, sender_id: currentAccount.value, sender_name: user.name, message_type: attachment.kind }).catch(() => {})
}
const readableSize = (size = 0) => size > 1024 * 1024 ? `${(size / 1024 / 1024).toFixed(1)} MB` : `${Math.max(1, Math.round(size / 1024))} KB`
const addChatAttachments = (event, kind) => {
  const selected = [...(event.target.files || [])]
  selected.forEach((file) => {
    const url = URL.createObjectURL(file)
    chatObjectUrls.add(url)
    pushAttachmentMessage({ kind, name: file.name, size: readableSize(file.size), type: file.type, url, rawFile: file }, kind === 'image' ? '发送现场图片' : '发送检修资料')
  })
  event.target.value = ''
}
const previewChatAttachment = (attachment) => {
  selectedFile.value = { id: `chat-${Date.now()}`, name: attachment.name, type: attachment.kind === 'image' ? '图片' : attachment.type?.includes('pdf') ? 'PDF' : '其他', size: attachment.size, version: '会话附件', parseStatus: '本地文件', url: attachment.url }
}
const stopChatRecording = () => {
  if (chatRecorder?.state === 'recording') chatRecorder.stop()
}
const toggleChatRecording = async () => {
  if (chatRecording.value) return stopChatRecording()
  if (!navigator.mediaDevices?.getUserMedia || typeof MediaRecorder === 'undefined') return toast('当前浏览器不支持录音，请使用最新版 Chrome')
  try {
    chatRecordStream = await navigator.mediaDevices.getUserMedia({ audio: true })
    chatRecordChunks = []
    chatRecorder = new MediaRecorder(chatRecordStream)
    chatRecorder.ondataavailable = (event) => { if (event.data.size) chatRecordChunks.push(event.data) }
    chatRecorder.onstop = () => {
      const blob = new Blob(chatRecordChunks, { type: chatRecorder.mimeType || 'audio/webm' })
      const url = URL.createObjectURL(blob)
      chatObjectUrls.add(url)
      pushAttachmentMessage({ kind: 'audio', name: `语音消息-${Date.now()}.webm`, size: readableSize(blob.size), type: blob.type, url, duration: chatRecordSeconds.value }, `语音消息 ${chatRecordSeconds.value} 秒`)
      chatRecordStream?.getTracks().forEach((track) => track.stop())
      chatRecording.value = false
      window.clearInterval(chatRecordTimer)
      chatRecordTimer = null
      chatRecordSeconds.value = 0
    }
    chatRecorder.start(250)
    chatRecording.value = true
    chatRecordSeconds.value = 0
    chatRecordTimer = window.setInterval(() => { chatRecordSeconds.value += 1 }, 1000)
  } catch (error) {
    toast(error.name === 'NotAllowedError' ? '麦克风权限未开启，请在浏览器地址栏允许录音' : '无法启动录音设备')
  }
}
const openTaskPicker = (mode = 'send') => { taskPickerMode.value = mode; showTaskPicker.value = true }
const sendTaskCard = (task = tasks.value[0]) => {
  if (!task || !activeConversation.value) return
  const message = {
    id: `card-${Date.now()}`,
    conversationId: activeConversation.value.id,
    mine: true,
    text: '发送任务卡片，请协作人员查看当前进度。',
    time: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }),
    card: { type: 'task', title: task.workOrderNo, desc: `${task.equipment_name} · ${task.current_step} · ${task.progress}%` }
  }
  chatMessages.value.push(message)
  void yixiuApi.sendConversationMessage(message.conversationId, { ...message, sender_id: currentAccount.value, sender_name: user.name, message_type: 'task-card' }).catch(() => {})
}
const selectTaskFromPicker = (task) => {
  if (taskPickerMode.value === 'assign') {
    const collaborator = activeConversation.value?.name
    task.collaborators = [...new Set([...(task.collaborators || []), collaborator].filter(Boolean))]
    sendChatMessage(`协作邀请：已将 ${collaborator} 加入任务 ${task.workOrderNo}`)
    toast('协作人员已加入任务')
  } else sendTaskCard(task)
  showTaskPicker.value = false
}
const summarizeConversation = () => {
  const recent = activeMessages.value.slice(-6).map((item) => item.text).filter(Boolean)
  const focus = recent.length ? recent.join('；') : '当前会话暂无有效消息'
  chatMessages.value.push({ id: `summary-${Date.now()}`, conversationId: activeConversation.value.id, mine: false, text: `协作重点：${focus.slice(0, 180)}。建议明确负责人、下一步动作与复测时间。`, time: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }) })
}
const requestSupport = () => {
  const task = tasks.value.find((item) => item.workOrderNo === activeConversation.value?.taskNo) || tasks.value.find((item) => item.severity === 'high')
  sendChatMessage(`专家支援请求：${task?.workOrderNo || '当前检修任务'} 需要协助判断故障原因，请携带检测结论反馈。`)
  toast('支援请求已发送到当前协作会话')
}
const createCollaborationGroup = () => {
  const source = activeConversation.value
  const id = `local-group-${Date.now()}`
  contacts.value.unshift({ id, name: `${source?.name || '检修'}协作群`, avatar: '', position: '临时协作群', department: source?.department || user.department, specialty: source?.specialty || '检修协作', devices: source?.devices || [], currentTask: source?.currentTask || '待关联任务', workload: 0, status: '在线' })
  activeConversationId.value = `contact-${id}`
  chatMessages.value.push({ id: `group-${Date.now()}`, conversationId: activeConversationId.value, mine: false, text: `协作群已创建。创建人：${user.name}，请先发送任务卡片并明确分工。`, time: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }) })
  toast('协作群已创建并打开')
}
const openMessageCard = (card) => {
  if (card.type === 'task') return goStat({ page: 'tasks', panel: 'manage' })
  if (card.type === 'knowledge') return goStat({ page: 'knowledge', panel: 'network' })
  toast(card.title)
}
const openTask = (task) => {
  selectedTask.value = task
}
const openKnowledge = (item) => {
  selectedKnowledge.value = item
}
const selectGraphNode = (node) => {
  selectedGraphNode.value = node
}
const previewFile = (file) => {
  if (!file) return toast('暂无可预览文件')
  selectedFileRow.value = file.id
  selectedFile.value = file
}
const toast = (text) => {
  toastText.value = text
  if (toastTimer) window.clearTimeout(toastTimer)
  toastTimer = window.setTimeout(() => {
    toastText.value = ''
    toastTimer = null
  }, 1800)
}
const statusClass = (value) => String(value).includes('异常') || String(value).includes('离线') ? 'bad' : 'ok'
const severityText = (value) => ({ low: '低风险', medium: '中风险', high: '高风险', critical: '严重风险' }[value] || value || '中风险')
const statusText = (value) => ({ pending: '待处理', in_progress: '检修中', review: '待复检', completed: '已完成', paused: '已暂停', rejected: '已退回', overdue: '已逾期' }[value] || value || '待处理')
const knowledgeStatusText = (value) => ({ pending: '待人工审核', approved: '已审核入库', rejected: '已退回修改' }[value] || value || '待人工审核')
const modalityText = (value) => ({ text: '文本描述', equipment_model: '设备型号', image: '故障图片', document: '维修文档', file: '现场附件' }[value] || value)
const cleanKnowledgePart = (value) => String(value ?? '').replace(/^\s*[.。·]{1,}\s*$/, '').trim()
const knowledgeTypeText = (item) => cleanKnowledgePart(item.type || item.category) || '检修知识'
const knowledgeMetaParts = (item) => [...new Set([
  cleanKnowledgePart(item.equipment),
  cleanKnowledgePart(item.model),
  cleanKnowledgePart(item.source),
  cleanKnowledgePart(item.fileType)
].filter(Boolean))]
const flattenKnowledgeText = (value) => {
  if (Array.isArray(value)) return value.flatMap(flattenKnowledgeText)
  if (value && typeof value === 'object') return Object.values(value).flatMap(flattenKnowledgeText)
  const text = cleanKnowledgePart(value)
  if (!text) return []
  if (/^[\[{]/.test(text)) {
    try { return flattenKnowledgeText(JSON.parse(text)) } catch { /* 使用普通文本继续处理 */ }
  }
  return text
    .replace(/^\s*[\["']+|[\]"']+\s*$/g, '')
    .split(/(?:"\s*,\s*"|\n+)/)
    .map((part) => part.replace(/^\s*["']|["']\s*$/g, '').trim())
    .filter(Boolean)
}
const knowledgeSummaryLines = (item) => {
  const lines = flattenKnowledgeText(item.summary || item.content)
  return lines.length ? lines.slice(0, 4) : ['该资料已纳入一修知识库，可查看详情或作为智能检索依据。']
}
const searchFromKnowledge = (item) => {
  const equipment = cleanKnowledgePart(item.equipment)
  const model = cleanKnowledgePart(item.model)
  if (equipment) searchForm.deviceName = equipment
  if (model && model !== 'ALL') searchForm.deviceModel = model
  searchForm.query = `${item.title} ${knowledgeSummaryLines(item)[0]}`.trim()
  activePage.value = 'search'
  resultTab.value = '全部'
}
const stepTitle = (step) => typeof step === 'string' ? step : step?.title || '检修步骤'
const stepDetail = (step) => typeof step === 'object' ? step?.detail || '' : ''
const isTaskStepCompleted = (task, index) => (task.completedSteps || []).includes(index)
const folderIcon = (folder) => ({
  全部文件: '▦',
  维修手册: '▣',
  标准作业流程: '✓',
  现场图片: '◉',
  检修报告: '▤',
  复检报告: '◎',
  其他技术资料: '□'
}[folder] || '□')
const fileIconClass = (file) => ({
  PDF: 'pdf',
  Word: 'doc',
  Excel: 'sheet',
  图片: 'image',
  视频: 'video',
  文本: 'text'
}[file.type] || 'other')
const fileIcon = (file) => ({
  PDF: 'PDF',
  Word: 'DOC',
  Excel: 'XLS',
  图片: 'IMG',
  视频: 'MP4',
  文本: 'TXT'
}[file.type] || 'FILE')
const inferFileType = (file) => {
  const name = file.name.toLowerCase()
  const mime = file.type || ''
  if (mime.includes('image') || /\.(png|jpe?g|gif|webp|bmp)$/i.test(name)) return '图片'
  if (mime.includes('pdf') || name.endsWith('.pdf')) return 'PDF'
  if (mime.includes('video') || /\.(mp4|webm|ogg|mov)$/i.test(name)) return '视频'
  if (mime.includes('word') || /\.(docx?|wps)$/i.test(name)) return 'Word'
  if (mime.includes('excel') || /\.(xlsx?|csv)$/i.test(name)) return 'Excel'
  if (mime.includes('text') || /\.(txt|md|log)$/i.test(name)) return '文本'
  return '其他'
}

const toFileMeta = (file) => ({
  localId: `${file.name}-${file.lastModified}-${Math.random()}`,
  name: file.name,
  size: `${Math.max(file.size / 1024, 1).toFixed(1)} KB`,
  rawSize: file.size,
  sizeText: `${Math.max(file.size / 1024, 1).toFixed(1)} KB`,
  type: inferFileType(file),
  rawType: file.type,
  raw: file,
  url: URL.createObjectURL(file),
  status: '待上传',
  parseStatus: '等待解析',
  auditStatus: '待审核',
  version: 'v1.0',
  uploaded_at: new Date().toLocaleString('zh-CN'),
  uploader: user.name
})
const releaseFileUrl = (file) => {
  if (file?.url?.startsWith('blob:')) URL.revokeObjectURL(file.url)
}
const releaseFileUrls = (list = []) => list.forEach(releaseFileUrl)
const addFiles = async (event, target) => {
  const selected = Array.from(event.target.files || []).map(toFileMeta)
  if (target === 'search') {
    searchFiles.value.push(...selected.map((file) => ({ ...file, status: '已加入检索' })))
  } else if (target === 'assistant') {
    assistantFiles.value.push(...selected.map((file) => ({ ...file, status: '待发送' })))
  } else {
    for (const file of selected) {
      const folder = activeFolder.value === '全部文件' ? '现场图片' : activeFolder.value
      try {
        file.status = '上传中'
        const saved = await yixiuApi.uploadFile(file.raw, { category: folder, folder, uploader: user.name, equipment: '', model: '', purpose: 'knowledge' }, (progress) => { file.progress = progress })
        files.value.unshift({ ...file, ...saved, id: saved.id || file.localId, url: saved.url || file.url, category: saved.category || folder, folder: saved.folder || folder, status: '上传成功', parseStatus: saved.parseStatus || '等待解析' })
      } catch (error) {
        file.status = '上传失败'
        toast(error.message)
      }
    }
    toast(`已上传 ${selected.length} 个文件`)
  }
  event.target.value = ''
}
const addDroppedFiles = (event) => {
  searchFiles.value.push(...Array.from(event.dataTransfer.files || []).map((file) => ({ ...toFileMeta(file), status: '已加入检索' })))
}
const addManagerDroppedFiles = async (event) => {
  const selected = Array.from(event.dataTransfer.files || []).map(toFileMeta)
  for (const file of selected) {
    const folder = activeFolder.value === '全部文件' ? '现场图片' : activeFolder.value
    try {
      file.status = '上传中'
      const saved = await yixiuApi.uploadFile(file.raw, { category: folder, folder, uploader: user.name, purpose: 'knowledge' }, (progress) => { file.progress = progress })
      files.value.unshift({ ...file, ...saved, id: saved.id || file.localId, url: saved.url || file.url, category: saved.category || folder, folder: saved.folder || folder, status: '上传成功', parseStatus: saved.parseStatus || '等待解析' })
    } catch (error) {
      file.status = '上传失败'
      toast(error.message)
    }
  }
  if (selected.length) toast(`已拖入 ${selected.length} 个文件`)
}
const removeSearchFile = (localId) => {
  releaseFileUrl(searchFiles.value.find((file) => file.localId === localId))
  searchFiles.value = searchFiles.value.filter((file) => file.localId !== localId)
}
const removeAssistantFile = (localId) => {
  releaseFileUrl(assistantFiles.value.find((file) => file.localId === localId))
  assistantFiles.value = assistantFiles.value.filter((file) => file.localId !== localId)
}
const resizeOperator = (delta) => {
  operatorWidth.value = Math.min(520, Math.max(300, operatorWidth.value + delta))
  localStorage.setItem('yixiu-operator-width', String(operatorWidth.value))
}
const startOperatorResize = (event) => {
  event.preventDefault()
  const startX = event.clientX
  const startWidth = operatorWidth.value
  const onMove = (moveEvent) => {
    operatorWidth.value = Math.min(520, Math.max(300, startWidth + startX - moveEvent.clientX))
  }
  const onUp = () => {
    localStorage.setItem('yixiu-operator-width', String(operatorWidth.value))
    document.body.classList.remove('resizing-panel')
    document.removeEventListener('pointermove', onMove)
    document.removeEventListener('pointerup', onUp)
    stopOperatorResize = null
  }
  document.body.classList.add('resizing-panel')
  document.addEventListener('pointermove', onMove)
  document.addEventListener('pointerup', onUp)
  stopOperatorResize = onUp
}
const toggleAssistantVoice = () => {
  const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition
  if (!Recognition) return toast('当前浏览器不支持语音识别，请使用新版 Chrome 或 Edge')
  if (assistantVoiceListening.value && assistantSpeechRecognition) {
    assistantSpeechRecognition.stop()
    return
  }
  const original = operatorInput.value.trim()
  assistantSpeechRecognition = new Recognition()
  assistantSpeechRecognition.lang = 'zh-CN'
  assistantSpeechRecognition.continuous = true
  assistantSpeechRecognition.interimResults = true
  assistantSpeechRecognition.onstart = () => { assistantVoiceListening.value = true; toast('正在将现场语音转换为文字') }
  assistantSpeechRecognition.onresult = (voiceEvent) => {
    const transcript = Array.from(voiceEvent.results).map((result) => result[0].transcript).join('')
    operatorInput.value = `${original}${original && transcript ? '；' : ''}${transcript}`
  }
  assistantSpeechRecognition.onerror = (voiceEvent) => toast(voiceEvent.error === 'not-allowed' ? '请允许浏览器使用麦克风' : '语音识别中断，请重试')
  assistantSpeechRecognition.onend = () => { assistantVoiceListening.value = false; assistantSpeechRecognition = null }
  assistantSpeechRecognition.start()
}
const simulateVoice = () => {
  const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition
  if (!Recognition) return toast('当前浏览器不支持语音识别，请使用新版 Chrome 或 Edge')
  if (voiceListening.value && speechRecognition) {
    speechRecognition.stop()
    return
  }
  speechRecognition = new Recognition()
  speechRecognition.lang = 'zh-CN'
  speechRecognition.continuous = true
  speechRecognition.interimResults = true
  const original = searchForm.query.trim()
  speechRecognition.onstart = () => { voiceListening.value = true; toast('正在识别现场语音') }
  speechRecognition.onresult = (event) => {
    const transcript = Array.from(event.results).map((result) => result[0].transcript).join('')
    searchForm.query = `${original}${original && transcript ? '；' : ''}${transcript}`
  }
  speechRecognition.onerror = (event) => toast(event.error === 'not-allowed' ? '请允许浏览器使用麦克风' : '语音识别中断，请重试')
  speechRecognition.onend = () => { voiceListening.value = false; speechRecognition = null }
  speechRecognition.start()
}
const runSearch = async () => {
  loading.search = true
  try {
    for (const file of searchFiles.value.filter((item) => !item.id)) {
      file.status = '上传中'
      try {
        const saved = await yixiuApi.uploadFile(file.raw, { purpose: 'search', category: '多模态检索', folder: '检索附件', uploader: user.name, equipment: searchForm.deviceName, model: searchForm.deviceModel }, (progress) => { file.progress = progress })
        Object.assign(file, saved, { raw: file.raw, localId: file.localId, status: '解析完成', progress: 100 })
      } catch (error) {
        file.status = '上传失败'
        throw error
      }
    }
    searchResult.value = await yixiuApi.search({ ...searchForm, fileIds: searchFiles.value.map((file) => file.id).filter(Boolean), query: searchForm.query })
    toast('智能检索完成')
  } catch (error) {
    toast(error.message || '智能检索失败')
  } finally {
    loading.search = false
  }
}
const createTaskFromSearch = async (item) => {
  const created = await yixiuApi.createTask({
    title: `${searchForm.deviceModel} ${searchForm.faultType}检修任务`,
    deviceName: searchForm.deviceName,
    deviceModel: searchForm.deviceModel,
    faultType: searchForm.faultType,
    description: searchForm.query,
    severity: searchResult.value?.risk || 'medium',
    assignee_name: user.name,
    sop: searchResult.value?.suggestion?.steps || [],
    tools: searchResult.value?.suggestion?.tools || [],
    safety: searchResult.value?.suggestion?.risks || [],
    references: [item.title]
  })
  tasks.value.unshift({ ...created, workOrderNo: created.workOrderNo || `YX-${Date.now()}`, progress: 0, current_step: '待接收', collaborators: [] })
  toast('已从检索结果创建检修任务')
}
const submitTask = async () => {
  const created = await yixiuApi.createTask(taskForm)
  tasks.value.unshift({ ...created, collaborators: [], sop: created.sop?.length ? created.sop : ['安全确认', '故障记录', '部件检测', '复测提交'] })
  showTaskForm.value = false
  toast('检修任务创建成功')
}
const advanceTask = async (task) => {
  const next = task.status === 'pending' ? 'in_progress' : task.status === 'in_progress' ? 'review' : task.status === 'review' ? 'completed' : 'completed'
  try { await yixiuApi.updateTaskStatus(task.id, next, { operator: user.name }) } catch (_error) { /* local-first fallback; server interface remains available */ }
  task.status = next
  task.progress = next === 'in_progress' ? Math.max(task.progress, 45) : next === 'review' ? 86 : 100
  task.current_step = next === 'in_progress' ? '作业执行' : next === 'review' ? '复测确认' : '归档'
  toast(`任务已流转为：${statusText(next)}`)
}
const taskPrimaryLabel = (task) => ({ pending: '接收并开始任务', in_progress: '提交复检', review: '打开复检评估', completed: '查看归档报告' }[task?.status] || '处理任务')
const handleTaskPrimary = async (task) => {
  if (!task) return
  if (task.status === 'review') return enterTaskRecheck(task)
  if (task.status === 'completed') return previewTaskReport(task)
  if (task.status === 'in_progress' && (task.completedSteps?.length || 0) < (task.sop?.length || 0)) {
    return toast(`还有 ${(task.sop?.length || 0) - (task.completedSteps?.length || 0)} 个作业步骤未确认`)
  }
  await advanceTask(task)
}
const enterTaskRecheck = (task) => {
  if (!task || task.status === 'pending') return toast('任务接收并完成作业步骤后才能进入复检')
  if (task.status === 'in_progress' && (task.completedSteps?.length || 0) < (task.sop?.length || 0)) return toast('请先完成全部标准作业步骤')
  if (task.status === 'in_progress') {
    task.status = 'review'
    task.progress = Math.max(task.progress || 0, 86)
    task.current_step = '复测确认'
  }
  taskPanel.value = 'recheck'
  activePage.value = 'tasks'
  selectedTask.value = null
  nextTick(() => document.querySelector('.recheck-panel')?.scrollIntoView({ behavior: 'smooth', block: 'start' }))
}
const previewTaskReport = (task) => { reportTask.value = task; selectedTask.value = null }
const windowPrint = () => window.print()
const saveRecheck = async (task) => {
  const form = recheckForms[task.id]
  let saved
  try { saved = await yixiuApi.recheck({ task_id: task.id, ...form, reviewer: user.name }) } catch (_error) {
    saved = { ...form, reviewer: user.name, reviewed_at: new Date().toISOString(), next_status: form.result === '通过' ? 'completed' : 'in_progress' }
  }
  task.recheck = saved
  task.status = saved.next_status
  task.current_step = saved.next_status === 'completed' ? '归档' : '返工整改'
  task.progress = saved.next_status === 'completed' ? 100 : 62
  toast('复检结果已保存')
}
const loadKnowledge = async () => {
  knowledge.value = await yixiuApi.knowledge(knowledgeKeyword.value)
}
const saveKnowledge = async () => {
  try {
    const tags = knowledgeForm.tagText.split(/[,，]/).map((item) => item.trim()).filter(Boolean)
    const saved = await yixiuApi.updateKnowledge({ ...knowledgeForm, tags: tags.length ? tags : ['沉淀', '检修案例'] })
    knowledge.value.unshift(saved)
    Object.assign(knowledgeForm, { title: '', type: '历史故障案例', equipment: '', model: '', source: '', tagText: '', summary: '' })
    toast('知识条目已进入人工审核队列')
  } catch (error) {
    toast(error.message || '知识提交失败')
  }
}
const reviewKnowledge = async (item, status) => {
  try {
    const saved = await yixiuApi.reviewKnowledge(item.id, { status, correction: knowledgeCorrections[item.id] || '', tags: item.tags || [], reviewer: user.name })
    Object.assign(item, saved)
    toast(status === 'approved' ? '审核通过，已同步知识状态' : '已退回修改')
  } catch (error) {
    toast(error.message || '审核保存失败')
  }
}
const completeTaskStep = async (task, index) => {
  try {
    let saved
    try { saved = await yixiuApi.completeTaskStep(task.id, index, { evidence: `由${user.name}确认` }) } catch (_error) {
      const completedSteps = [...new Set([...(task.completedSteps || []), index])]
      const progress = Math.min(100, Math.round(completedSteps.length / Math.max(task.sop?.length || 1, 1) * 86))
      saved = { completedSteps, progress, status: completedSteps.length >= (task.sop?.length || 1) ? 'review' : 'in_progress' }
    }
    task.completedSteps = saved.completedSteps
    task.progress = saved.progress
    task.status = saved.status
    task.current_step = saved.status === 'review' ? '等待复检' : stepTitle(task.sop[index + 1])
    toast(saved.status === 'review' ? '作业步骤完成，任务已进入复检' : '步骤完成并已保存')
  } catch (error) {
    toast(error.message || '步骤保存失败')
  }
}
const runAudit = async () => {
  const result = await yixiuApi.audit({ references: true, safety_checked: true, measurements: true, retested: true, report_ready: true })
  auditResult.value = JSON.stringify(result, null, 2)
}

const runOperatorPrimary = () => {
  if (activePage.value === 'home') {
    operatorMessages.value.push({
      id: `brief-${Date.now()}`,
      page: 'home',
      role: 'assistant',
      text: `今日共 ${tasks.value.length} 项任务，高风险 ${tasks.value.filter((task) => task.severity === 'high').length} 项，待复检 ${tasks.value.filter((task) => task.status === 'review').length} 项。建议先处理高风险和已逾期工单。`
    })
    return toast('今日检修简报已生成')
  }
  if (activePage.value === 'search') return runSearch()
  if (activePage.value === 'tasks') {
    taskPanel.value = 'manage'
    return toast('已打开任务管理')
  }
  if (activePage.value === 'knowledge') {
    knowledgePanel.value = 'files'
    return toast('已打开文件管理')
  }
  return runAudit()
}

const sendOperatorPrompt = async (prompt) => {
  const value = String(prompt || '').trim()
  if (!value && !assistantFiles.value.length) return
  if (value.includes('退出登录')) return logout()
  const sourcePage = activePage.value
  operatorMessages.value.push({ id: `user-${Date.now()}`, page: sourcePage, role: 'user', text: value || '请分析已上传的现场资料', attachments: assistantFiles.value.map((file) => file.name) })
  operatorInput.value = ''
  if (assistantFiles.value.length) {
    try {
      for (const file of assistantFiles.value.filter((item) => !item.id)) {
        file.status = '上传中'
        const saved = await yixiuApi.uploadFile(file.raw, { purpose: 'assistant', category: '智能问修', folder: '问修附件', uploader: user.name }, (progress) => { file.progress = progress })
        Object.assign(file, saved, { raw: file.raw, localId: file.localId, status: '分析完成' })
      }
      const response = await yixiuApi.assistantChat({ message: value, fileIds: assistantFiles.value.map((file) => file.id).filter(Boolean), agent: operatorProfile.value.name, page: sourcePage })
      operatorMessages.value.push({ id: `assistant-${Date.now()}`, page: sourcePage, role: 'assistant', text: `${response.response}\n引用：${(response.references || []).join('、')}` })
      releaseFileUrls(assistantFiles.value)
      assistantFiles.value = []
      return toast('已完成图文联合分析')
    } catch (error) {
      return toast(error.message || '附件分析失败')
    }
  }
  if (value.includes('高风险')) return goStat({ page: 'tasks', panel: 'manage', severity: 'high' })
  if (value.includes('开始检索') || value.includes('检索建议')) return runSearch()
  if (value.includes('创建任务') || value.includes('新建任务')) {
    activePage.value = 'tasks'
    taskPanel.value = 'manage'
    showTaskForm.value = true
    return
  }
  if (value.includes('流转任务')) {
    const task = filteredTasks.value[0]
    if (task) return advanceTask(task)
    return toast('暂无可流转任务')
  }
  if (value.includes('复检')) {
    activePage.value = 'tasks'
    taskPanel.value = 'recheck'
    return
  }
  if (value.includes('联系人')) {
    activePage.value = 'tasks'
    taskPanel.value = 'contacts'
    return
  }
  if (value.includes('文件管理')) {
    activePage.value = 'knowledge'
    knowledgePanel.value = 'files'
    return
  }
  if (value.includes('知识网络')) {
    activePage.value = 'knowledge'
    knowledgePanel.value = 'network'
    return
  }
  if (value.includes('提交沉淀')) {
    activePage.value = 'knowledge'
    knowledgePanel.value = 'update'
    return
  }
  if (value.includes('运行核查')) return runAudit()
  if (value.includes('个人记录')) {
    activePage.value = 'profile'
    return
  }
  try {
    const response = await yixiuApi.assistantChat({ message: value, fileIds: [], agent: operatorProfile.value.name, page: sourcePage })
    operatorMessages.value.push({ id: `assistant-${Date.now()}`, page: sourcePage, role: 'assistant', text: response.response })
    toast(`${operatorProfile.value.name}已结合当前数据给出建议`)
  } catch (error) {
    toast(error.message || '智能体暂时无法响应')
  }
}

const playBootAnimation = async () => {
  await nextTick()
  await new Promise((resolve) => window.requestAnimationFrame(resolve))
  const screen = bootScreenRef.value
  const mark = bootMarkRef.value
  const bootLogo = bootLogoRef.value
  const brandLogo = brandLogoRef.value
  if (!screen || !mark || !bootLogo || !brandLogo || !mark.animate || !screen.animate) {
    window.setTimeout(() => { showSplash.value = false }, 1400)
    return
  }

  const from = mark.getBoundingClientRect()
  const to = brandLogo.getBoundingClientRect()
  const fromCenterX = from.left + from.width / 2
  const fromCenterY = from.top + from.height / 2
  const toCenterX = to.left + to.width / 2
  const toCenterY = to.top + to.height / 2
  const dx = Math.round(toCenterX - fromCenterX)
  const dy = Math.round(toCenterY - fromCenterY)
  const scale = Number((to.width / bootLogo.getBoundingClientRect().width).toFixed(3))

  const markMotion = mark.animate([
    { opacity: 0, transform: 'translate3d(0, 18px, 0) scale(.96)', offset: 0 },
    { opacity: 1, transform: 'translate3d(0, 0, 0) scale(1)', offset: .26 },
    { opacity: 1, transform: `translate3d(${Math.round(dx * .72)}px, ${Math.round(dy * .62 - 18)}px, 0) scale(${Math.min(scale + .1, 1)})`, offset: .76 },
    { opacity: 1, transform: `translate3d(${dx}px, ${dy}px, 0) scale(${scale})`, offset: 1 }
  ], {
    duration: 1580,
    delay: 900,
    easing: 'cubic-bezier(.18,.84,.18,1)',
    fill: 'forwards'
  })

  const screenFade = screen.animate([
    { opacity: 1 },
    { opacity: 1, offset: .86 },
    { opacity: 0 }
  ], {
    duration: 2800,
    easing: 'ease',
    fill: 'forwards'
  })

  await Promise.allSettled([markMotion.finished, screenFade.finished])
  showSplash.value = false
}

onMounted(async () => {
  if (isAuthenticated.value) {
    const account = getAccounts().find((item) => item.account === currentAccount.value)
    if (!account) logout()
    else {
      applyAccountProfile(account)
      await startWorkspace()
    }
  } else showSplash.value = false
})
onBeforeUnmount(() => {
  if (clockTimer) window.clearInterval(clockTimer)
  if (toastTimer) window.clearTimeout(toastTimer)
  if (speechRecognition) speechRecognition.stop()
  if (assistantSpeechRecognition) assistantSpeechRecognition.stop()
  if (stopOperatorResize) stopOperatorResize()
  if (chatRecordTimer) window.clearInterval(chatRecordTimer)
  if (chatRecorder?.state === 'recording') chatRecorder.stop()
  chatRecordStream?.getTracks().forEach((track) => track.stop())
  chatObjectUrls.forEach((url) => URL.revokeObjectURL(url))
  releaseFileUrls(searchFiles.value)
  releaseFileUrls(assistantFiles.value)
})
</script>

<style scoped>
:global(*) { box-sizing: border-box; }
:global(body) { margin: 0; min-width: 1180px; background: #EEECEA; color: #111110; font-family: "Microsoft YaHei", "PingFang SC", system-ui, sans-serif; }
button, input, textarea, select { font: inherit; }
button { cursor: pointer; }
.ui-icon { width: 18px; height: 18px; display: block; fill: none; stroke: currentColor; stroke-width: 1.9; stroke-linecap: round; stroke-linejoin: round; }
.app-shell { min-height: 100vh; display: grid; grid-template-columns: 250px minmax(0, 1fr); background: #EEECEA; }
.app-shell.collapsed { grid-template-columns: 82px minmax(0, 1fr); }
.boot-screen { position: fixed; inset: 0; z-index: 100; display: grid; place-items: center; overflow: hidden; background: #fffdf9; contain: layout paint; }
.boot-grid { position: absolute; inset: -12%; background:
  linear-gradient(90deg, rgba(17,17,16,.045) 1px, transparent 1px),
  linear-gradient(0deg, rgba(17,17,16,.035) 1px, transparent 1px),
  radial-gradient(circle at 50% 46%, rgba(17,17,16,.045), transparent 35%);
  background-size: 48px 48px, 48px 48px, auto; opacity: .8; transform: scale(1.05); }
.boot-flow { position: absolute; height: 1px; width: 36vw; background: linear-gradient(90deg, transparent, rgba(17,17,16,.16), transparent); opacity: 0; animation: bootFlow 1.4s linear .44s both; }
.boot-flow.flow-a { top: 39%; left: 12%; }
.boot-flow.flow-b { top: 57%; right: 10%; animation-delay: .7s; }
.boot-mark { position: relative; display: grid; place-items: center; will-change: transform, opacity; backface-visibility: hidden; }
.boot-mark img { position: relative; z-index: 2; width: 300px; height: 126px; object-fit: contain; border-radius: 12px; opacity: 0; animation: bootLogoIn .72s ease .18s forwards; will-change: opacity, transform; }
@keyframes bootLogoIn { from { opacity: 0; transform: scale(.985); } to { opacity: 1; transform: scale(1); } }
@keyframes bootFlow { 0% { opacity: 0; transform: translate3d(-16vw,0,0); } 18% { opacity: .55; } 100% { opacity: 0; transform: translate3d(16vw,0,0); } }.side-nav { display: flex; flex-direction: column; gap: 18px; padding: 18px 14px; border-right: 1px solid #ddd8d3; background: linear-gradient(180deg, #fbfaf8, #f4f2ef); }
.brand, .side-nav nav button, .collapse-btn { width: 100%; border: 0; border-radius: 12px; background: transparent; color: #484336; }
.brand { display: grid; place-items: center; min-height: 88px; padding: 6px 4px; overflow: visible; }
.brand img { display: block; width: 176px; height: 74px; object-fit: contain; border-radius: 12px; background: transparent; filter: drop-shadow(0 8px 12px rgba(17,17,16,.05)); }
.app-shell.collapsed .brand { width: 54px; min-height: 76px; padding: 6px 0; justify-self: center; }
.app-shell.collapsed .brand img { width: 50px; height: 50px; object-fit: contain; object-position: center; transform: none; }
.side-nav nav b { display: block; }
.side-nav nav { display: grid; gap: 8px; }
.side-nav nav button { display: flex; align-items: center; gap: 12px; min-height: 42px; padding: 0 12px; font-weight: 800; }
.nav-icon { width: 26px; height: 26px; display: grid; place-items: center; flex-shrink: 0; border-radius: 9px; background: rgba(17,17,16,.05); color: #484336; }
.side-nav nav button.active, .side-nav nav button:hover { background: #111110; color: #EEECEA; }
.side-nav nav button.active .nav-icon, .side-nav nav button:hover .nav-icon { background: rgba(238,236,234,.12); color: #EEECEA; }
.collapse-btn { margin-top: auto; min-height: 38px; background: #EEECEA; }
.workspace { min-width: 0; display: flex; flex-direction: column; }
.topbar { height: 72px; display: grid; grid-template-columns: minmax(190px, 1fr) 360px auto 38px auto auto; align-items: center; gap: 14px; padding: 0 22px; border-bottom: 1px solid #ddd8d3; background: linear-gradient(180deg, #fbfaf8, #f4f2ef); }
.content-shell { height: calc(100vh - 72px); min-height: 0; display: grid; grid-template-columns: minmax(0, 1fr) 360px; }
.breadcrumb, .eyebrow { margin: 0; color: #706D6D; font-size: 12px; font-weight: 800; }
h1, h2, h3, h4, p { margin: 0; }
h1 { margin-top: 4px; font-size: 20px; }
.global-search { height: 40px; display: flex; align-items: center; gap: 8px; padding: 0 12px; border: 1px solid #ddd8d3; border-radius: 14px; background: #fbfaf8; }
.global-search input, .form-grid input, .form-grid textarea, .form-grid select, .filters input, .filters select, .recheck-grid textarea, .recheck-grid select { width: 100%; border: 1px solid #ddd8d3; border-radius: 10px; background: #fbfaf8; color: #111110; outline: 0; }
.global-search input { border: 0; background: transparent; }
.work-strip { display: flex; gap: 8px; white-space: nowrap; }
.work-strip span, .badge, .tag-line span { padding: 5px 9px; border-radius: 999px; background: #EEECEA; color: #484336; font-size: 12px; font-weight: 800; }
.work-strip .bad { background: #f4dfda; color: #8f3f2d; }
.icon-button, .user-chip { border: 1px solid #ddd8d3; background: #fbfaf8; border-radius: 12px; color: #111110; }
.icon-button { width: 38px; height: 38px; display: grid; place-items: center; padding: 0; }
.user-chip { display: flex; align-items: center; gap: 8px; padding: 5px 10px; }
.topbar-logout { min-height: 38px; display: inline-flex; align-items: center; justify-content: center; gap: 7px; padding: 0 13px; border: 1px solid #ead8d3; border-radius: 11px; background: #fff8f6; color: #974936; font-weight: 800; white-space: nowrap; transition: transform .18s, border-color .18s, background .18s, box-shadow .18s; }
.topbar-logout .ui-icon { width: 17px; height: 17px; }
.topbar-logout:hover { transform: translateY(-1px); border-color: #dbaea2; background: #fff1ed; box-shadow: 0 7px 16px rgba(151,73,54,.1); }
.topbar-logout:focus-visible { outline: 3px solid rgba(151,73,54,.16); outline-offset: 2px; }
.user-chip img, .contact-card img, .profile-card img { width: 30px; height: 30px; border-radius: 50%; object-fit: cover; }
.page-scroll { min-height: 0; overflow: auto; padding: 22px; }
.page-grid { display: grid; grid-template-columns: repeat(12, minmax(0, 1fr)); gap: 16px; }
.span-all { grid-column: 1 / -1; }
.span-8 { grid-column: span 8; }
.span-7 { grid-column: span 7; }
.span-6 { grid-column: span 6; }
.span-5 { grid-column: span 5; }
.span-4 { grid-column: span 4; }
.panel, .welcome-card, .agent-card, .stat-card, .profile-card { border: 1px solid #ddd8d3; border-radius: 14px; background: #fbfaf8; box-shadow: 0 14px 30px rgba(17,17,16,.04); }
.panel, .welcome-card, .agent-card, .profile-card { padding: 18px; }
.welcome-brand { display: grid; grid-template-columns: 300px minmax(0, 1fr); gap: 24px; align-items: center; }
.welcome-brand img { width: 300px; height: 142px; object-fit: contain; padding: 0; border: 0; border-radius: 18px; background: transparent; filter: drop-shadow(0 18px 26px rgba(17,17,16,.1)); }
.welcome-card h2 { margin: 8px 0; font-size: 28px; }
.health-grid, .analysis-grid, .detail-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px; margin-top: 16px; }
.health-grid span, .analysis-grid span, .detail-grid span { padding: 10px; border-radius: 10px; background: #f4f2ef; color: #484336; font-size: 13px; }
.agent-row { display: grid; grid-template-columns: 64px 9px minmax(0, 1fr); align-items: center; gap: 10px; padding: 10px 0; border-bottom: 1px solid #EEECEA; }
.agent-row img { width: 64px; height: 64px; border-radius: 50%; object-fit: cover; box-shadow: 0 10px 18px rgba(17,17,16,.08); }
.agent-row small, .result-card small, .contact-card small, .tr small { display: block; margin-top: 4px; color: #706D6D; font-size: 12px; }
.dot { width: 9px; height: 9px; margin-top: 5px; border-radius: 50%; background: #706D6D; }
.dot.online { background: #4f8062; }
.dot.busy { background: #b88a44; }
.stat-card { min-height: 116px; padding: 16px; text-align: left; }
.task-stat { min-height: 88px; padding: 12px; }
.task-stat b { margin: 6px 0; font-size: 24px; }
.stat-card span, .stat-card small { display: block; color: #706D6D; }
.stat-card b { display: block; margin: 10px 0; font-size: 30px; }
.panel-head, .filters, .actions, .card-actions, .inline-actions { display: flex; align-items: center; justify-content: space-between; gap: 10px; }
.table { display: grid; gap: 3px; overflow: auto; }
.tr { display: grid; grid-template-columns: 1.05fr 1.2fr 1.8fr .75fr .8fr 1fr .8fr 1.15fr; gap: 10px; align-items: center; width: 100%; min-width: 980px; padding: 11px 12px; border: 0; border-radius: 10px; background: transparent; color: #111110; text-align: left; }
.compact .tr { grid-template-columns: 1.1fr 1.5fr .8fr .75fr .8fr .75fr .6fr; min-width: 780px; }
.tr.head { background: #EEECEA; color: #706D6D; font-size: 12px; font-weight: 900; }
.tr:not(.head):hover { background: #f4f2ef; }
.badge.high { background: #f4dfda; color: #8f3f2d; }
.badge.medium { background: #efe5d5; color: #694b22; }
.badge.low { background: #e6ebe3; color: #425744; }
.quick-grid, .result-grid, .contact-grid, .recheck-grid, .file-cards { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; }
.quick-grid button, .history-row, .alert-list button { min-height: 42px; border: 1px solid #ddd8d3; border-radius: 10px; background: #f4f2ef; color: #111110; text-align: left; padding: 10px; }
.alert-list { display: grid; gap: 10px; margin-top: 12px; }
.alert-list small { display: block; margin-top: 4px; color: #706D6D; }
.chart-wrap { display: grid; grid-template-columns: minmax(0, 1fr) 190px; gap: 16px; align-items: center; }
.chart-wrap svg { width: 100%; height: 250px; border-radius: 12px; background: linear-gradient(#ddd8d3 1px, transparent 1px), #fbfaf8; background-size: 100% 25%; }
.distribution { display: grid; gap: 10px; }
.distribution span { display: grid; gap: 5px; color: #706D6D; font-size: 12px; }
.distribution b { height: 8px; border-radius: 99px; background: #111110; }
.two-column { display: grid; grid-template-columns: minmax(0, 1fr) 420px; gap: 16px; }
.form-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }
.form-grid label { display: grid; gap: 6px; color: #484336; font-size: 13px; font-weight: 800; }
.form-grid .wide { grid-column: 1 / -1; }
.form-grid input, .form-grid select { height: 40px; padding: 0 10px; }
textarea { min-height: 96px; resize: vertical; padding: 10px; }
.upload-zone { margin-top: 14px; padding: 18px; border: 1px dashed #C5BFB9; border-radius: 12px; background: #f4f2ef; text-align: center; }
.upload-zone input, .panel-head input[type=file] { display: none; }
button, .ghost { border: 1px solid #ddd8d3; border-radius: 10px; background: #fbfaf8; color: #111110; padding: 8px 12px; }
.primary { border-color: #111110; background: #111110; color: #EEECEA; }
button:disabled { opacity: .55; cursor: not-allowed; }
.file-pills, .tag-line { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px; }
.file-pills span { padding: 8px 10px; border-radius: 999px; background: #EEECEA; font-size: 12px; }
.result-card, .contact-card { display: grid; gap: 10px; padding: 14px; border: 1px solid #ddd8d3; border-radius: 12px; background: #fff; }
.sop-list, .timeline { display: grid; gap: 9px; margin-top: 12px; }
.sop-list span, .timeline span, .load-row { display: flex; align-items: center; gap: 10px; padding: 10px; border-radius: 10px; background: #f4f2ef; }
.sop-list b { width: 24px; height: 24px; display: grid; place-items: center; border-radius: 8px; background: #111110; color: #EEECEA; }
.tabs { display: flex; flex-wrap: wrap; gap: 8px; }
.tabs button.active { background: #111110; color: #EEECEA; }
.filters { margin-bottom: 14px; align-items: stretch; }
.filters input, .filters select, .recheck-grid textarea, .recheck-grid select { min-height: 40px; padding: 0 10px; }
.load-row { justify-content: space-between; }
.load-row b { height: 8px; max-width: 55%; border-radius: 99px; background: #111110; }
.task-analytics { background: linear-gradient(180deg, #fbfffe, #f4faf7); }
.analysis-cards { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; margin-top: 12px; }
.analysis-cards section { min-height: 172px; display: grid; align-content: start; gap: 8px; padding: 12px; border: 1px solid #dce9e5; border-radius: 12px; background: #fffdfa; }
.analysis-cards svg { width: 100%; height: 112px; border-radius: 10px; background: linear-gradient(#eef5f3 1px, transparent 1px); background-size: 100% 25%; }
.bar-row, .chip-row { min-height: 28px; display: grid; grid-template-columns: 68px minmax(0, 1fr) 24px; align-items: center; gap: 8px; padding: 4px 0; border: 0; background: transparent; text-align: left; }
.bar-row i { height: 8px; border-radius: 999px; background: #2f7f8f; }
.bar-row i.high { background: #c95f5a; }
.bar-row i.medium { background: #d79542; }
.bar-row i.low { background: #6c9b72; }
.chip-row { grid-template-columns: minmax(0, 1fr) 28px; padding: 6px 8px; border-radius: 10px; background: #edf6f4; color: #294f52; }
.chip-row.warm { background: #f8eddf; color: #7a4b1f; }
.priority-list { display: grid; gap: 10px; margin-top: 12px; }
.priority-list article { display: grid; grid-template-columns: minmax(0, 1.5fr) 110px minmax(0, 1fr) minmax(0, 1fr) auto; gap: 10px; align-items: center; padding: 12px; border: 1px solid #ddd8d3; border-radius: 12px; background: #fffdfa; }
.priority-list small { color: #706D6D; }
.task-events span { border-left: 3px solid #2f7f8f; }
.view-switch { display: inline-flex; gap: 4px; padding: 4px; border: 1px solid #ddd8d3; border-radius: 999px; background: #f4f2ef; }
.view-switch button { min-height: 28px; padding: 4px 10px; border-radius: 999px; }
.view-switch button.active { background: #111110; color: #EEECEA; }
.task-board { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; }
.task-board section { min-height: 360px; display: grid; align-content: start; gap: 10px; padding: 12px; border-radius: 14px; background: #f4f8f6; }
.task-board h4 { display: flex; justify-content: space-between; margin: 0; }
.task-board article { display: grid; gap: 6px; padding: 12px; border: 1px solid #dce9e5; border-radius: 12px; background: #fffdfa; cursor: pointer; }
.task-board article small { color: #706D6D; }
.contact-card img, .profile-card img { width: 58px; height: 58px; }
.chat-workbench { min-height: 680px; display: grid; grid-template-columns: 25% minmax(0, 1fr) 25%; gap: 0; padding: 0; overflow: hidden; }
.conversation-list, .collab-info { min-width: 0; padding: 14px; background: #f3faf9; }
.conversation-list { display: grid; align-content: start; gap: 8px; border-right: 1px solid #d7e8e5; }
.chat-search input { width: 100%; height: 40px; padding: 0 12px; border: 1px solid #d7e8e5; border-radius: 12px; background: #fffdfa; }
.conversation-list button { min-height: 66px; display: grid; grid-template-columns: 44px minmax(0, 1fr) auto; align-items: center; gap: 9px; padding: 8px; border: 0; background: transparent; text-align: left; }
.conversation-list button.active, .conversation-list button:hover { background: #fffdfa; box-shadow: 0 10px 22px rgba(47,127,143,.08); }
.conversation-list img { width: 44px; height: 44px; border-radius: 50%; object-fit: cover; }
.conversation-list small, .chat-title small, .collab-info p { display: block; color: #6b7d7c; }
.conversation-list i { min-width: 22px; height: 22px; display: grid; place-items: center; border-radius: 50%; background: #c95f5a; color: #fff; font-style: normal; font-size: 12px; }
.chat-main { min-width: 0; display: grid; grid-template-rows: auto minmax(0, 1fr) auto; background: #fffdfa; }
.chat-title { min-height: 72px; display: flex; align-items: center; gap: 10px; justify-content: space-between; padding: 12px 16px; border-bottom: 1px solid #d7e8e5; }
.chat-title h3 { margin-top: 2px; }
.chat-messages { min-height: 0; overflow: auto; display: grid; align-content: start; gap: 12px; padding: 18px; background: radial-gradient(circle, rgba(47,127,143,.08) 1px, transparent 1px), #fbfffe; background-size: 22px 22px; }
.message { display: flex; gap: 8px; max-width: 78%; }
.message.mine { justify-self: end; }
.message img { width: 36px; height: 36px; border-radius: 50%; object-fit: cover; }
.message > div { display: grid; gap: 6px; padding: 10px 12px; border-radius: 14px; background: #edf6f4; color: #213d3f; }
.message.mine > div { background: #dff1f5; color: #1f4650; }
.message small { color: #6b7d7c; }
.message-card { display: grid; gap: 3px; min-width: 220px; padding: 10px; border: 1px solid #cfe1de; border-radius: 10px; background: rgba(255,255,255,.78); text-align: left; }
.chat-compose { display: grid; grid-template-columns: repeat(4, auto) minmax(0, 1fr) auto; gap: 8px; padding: 12px; border-top: 1px solid #d7e8e5; background: #fffdfa; }
.chat-compose input { min-width: 0; height: 40px; padding: 0 12px; border: 1px solid #d7e8e5; border-radius: 12px; background: #fbfffe; }
.collab-info { display: grid; align-content: start; gap: 12px; border-left: 1px solid #d7e8e5; }
.collab-info > img { width: 74px; height: 74px; border-radius: 50%; object-fit: cover; }
.collab-actions { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px; }
.graph-panel { overflow: hidden; background: #fbfaf8; }
.graph-toolbar, .file-toolbar { display: grid; grid-template-columns: minmax(0, 1fr) auto auto; gap: 12px; align-items: center; margin-bottom: 14px; }
.graph-search { width: 46px; height: 46px; display: grid; grid-template-columns: 34px minmax(0, 1fr) 26px; align-items: center; gap: 6px; padding: 5px; border: 1px solid #ddd8d3; border-radius: 999px; background: #fffdfa; overflow: hidden; transition: width .34s ease, border-color .24s ease, box-shadow .24s ease; }
.graph-search.expanded, .graph-search:focus-within { width: min(420px, 42vw); border-color: #B88A44; box-shadow: 0 16px 28px rgba(17,17,16,.07); }
.graph-search-trigger, .graph-search-clear { width: 34px; height: 34px; display: grid; place-items: center; padding: 0; border: 0; border-radius: 50%; background: #111110; color: #EEECEA; }
.graph-search-clear { width: 26px; height: 26px; background: #EEECEA; color: #484336; }
.graph-search input { min-width: 0; width: 100%; border: 0; outline: 0; background: transparent; opacity: 0; color: #111110; transition: opacity .18s ease .1s; }
.graph-search.expanded input, .graph-search:focus-within input { opacity: 1; }
.graph-controls { display: flex; flex-wrap: wrap; justify-content: flex-end; gap: 8px; }
.graph-controls select, .graph-controls button { height: 38px; border: 1px solid #ddd8d3; border-radius: 999px; background: #fffdfa; color: #111110; padding: 0 10px; }
.knowledge-map { display: grid; grid-template-columns: minmax(0, 1fr) 310px; gap: 14px; }
.map-canvas { position: relative; min-height: 620px; border-radius: 18px; overflow: hidden; background:
  radial-gradient(circle at 50% 50%, rgba(78,125,151,.12), transparent 30%),
  linear-gradient(90deg, rgba(84,98,112,.08) 1px, transparent 1px),
  linear-gradient(0deg, rgba(84,98,112,.07) 1px, transparent 1px),
  #f8fbfc; background-size: auto, 28px 28px, 28px 28px, auto; box-shadow: inset 0 0 0 1px #dde5e8; }
.graph-stage { position: absolute; inset: 0; transform-origin: center; transition: transform .24s ease; }
.graph-legend { position: absolute; left: 14px; top: 14px; z-index: 4; display: flex; flex-wrap: wrap; max-width: 72%; gap: 7px; }
.graph-legend span { display: inline-flex; align-items: center; gap: 5px; padding: 5px 8px; border: 1px solid #dbe3e6; border-radius: 999px; background: rgba(255,255,255,.82); color: #52616b; font-size: 11px; font-weight: 800; }
.graph-legend i { width: 9px; height: 9px; border-radius: 50%; }
.graph-zoom { position: absolute; right: 14px; top: 14px; z-index: 4; display: flex; align-items: center; gap: 6px; padding: 6px; border: 1px solid #dbe3e6; border-radius: 999px; background: rgba(255,255,255,.88); }
.graph-zoom button { width: 28px; height: 28px; padding: 0; border-radius: 50%; }
.graph-zoom input { width: 90px; }
.map-lines { position: absolute; inset: 0; width: 100%; height: 100%; z-index: 1; }
.map-lines line { stroke: rgba(93,128,148,.42); stroke-width: 1.2; transition: opacity .18s ease, stroke .18s ease; }
.map-lines line.faint { stroke: rgba(122,137,146,.2); stroke-width: .8; }
.map-lines text { fill: #748991; font-size: 10px; paint-order: stroke; stroke: rgba(248,251,252,.9); stroke-width: 4px; stroke-linejoin: round; pointer-events: none; }
.graph-node { position: absolute; z-index: 2; transform: translate(-50%, -50%); width: 34px; height: 34px; display: grid; place-items: center; padding: 0; border: 0; border-radius: 50%; background: transparent; text-align: center; }
.graph-node span { width: 18px; height: 18px; display: block; border: 3px solid rgba(255,255,255,.9); border-radius: 50%; background: #7d95a8; box-shadow: 0 6px 14px rgba(79,95,107,.16); transition: transform .18s ease, box-shadow .18s ease, outline .18s ease; }
.graph-node.important span { width: 18px; height: 18px; }
.graph-node b { position: absolute; left: 50%; top: calc(100% + 4px); transform: translateX(-50%); max-width: 112px; padding: 3px 7px; border-radius: 999px; background: rgba(255,255,255,.9); color: #29333a; box-shadow: 0 6px 16px rgba(79,95,107,.1); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-size: 11px; opacity: 0; pointer-events: none; transition: opacity .16s ease; }
.graph-node.showLabel b, .graph-node:hover b, .graph-node.active b, .graph-node.matched b { opacity: 1; }
.graph-node.center { left: 50%; top: 50%; width: 76px; height: 76px; z-index: 3; }
.graph-node.center span { width: 52px; height: 52px; background: #2f5f88; border-width: 5px; box-shadow: 0 0 0 10px rgba(47,95,136,.1), 0 14px 28px rgba(47,95,136,.18); }
.graph-node.center b { opacity: 1; top: 100%; font-size: 12px; }
.graph-node.active span, .graph-node:hover span, .graph-node.matched span { transform: scale(1.35); outline: 7px solid rgba(184,138,68,.16); box-shadow: 0 12px 26px rgba(184,138,68,.24); }
.graph-node.equipment span, .graph-legend i.equipment { background: #3f7fa7; }
.graph-node.model span, .graph-legend i.model { background: #8fc0d6; }
.graph-node.part span, .graph-legend i.part { background: #45aeb0; }
.graph-node.fault span, .graph-legend i.fault { background: #d79542; }
.graph-node.cause span, .graph-legend i.cause { background: #cf6d45; }
.graph-node.method span, .graph-legend i.method { background: #8b879f; }
.graph-node.solution span, .graph-legend i.solution { background: #6c9b72; }
.graph-node.sop span, .graph-legend i.sop { background: #2f5f88; }
.graph-node.risk span, .graph-legend i.risk { background: #c95f5a; }
.graph-node.case span, .graph-legend i.case { background: #9a7858; }
.graph-node.doc span, .graph-legend i.doc { background: #7d95a8; }
.map-inspector { display: grid; align-content: start; gap: 12px; padding: 16px; border: 1px solid #ddd8d3; border-radius: 16px; background: linear-gradient(180deg, #fffdfa, #f4f2ef); }
.map-inspector p { color: #484336; line-height: 1.65; }
.file-manager input[type=file] { display: none; }
.file-toolbar { grid-template-columns: minmax(0, 1fr) 1px auto; }
.file-actions { display: flex; justify-content: flex-end; gap: 8px; }
.file-window { min-height: 620px; display: grid; grid-template-columns: 230px minmax(0, 1fr); border: 1px solid #ddd8d3; border-radius: 16px; overflow: hidden; background: #fffdfa; }
.file-sidebar { display: grid; align-content: start; gap: 6px; padding: 14px; border-right: 1px solid #ddd8d3; background: #f4f2ef; }
.file-sidebar button { display: flex; align-items: center; justify-content: flex-start; gap: 10px; min-height: 40px; border: 0; background: transparent; text-align: left; }
.file-sidebar button.active, .file-sidebar button:hover { background: #111110; color: #EEECEA; }
.file-sidebar span { width: 24px; height: 24px; display: grid; place-items: center; border-radius: 8px; background: rgba(255,255,255,.74); color: #111110; font-weight: 900; }
.file-desktop { min-width: 0; display: grid; grid-template-rows: auto minmax(0, 1fr) auto; gap: 12px; padding: 14px; background:
  radial-gradient(circle, rgba(17,17,16,.07) 1px, transparent 1px),
  #fffdfa; background-size: 22px 22px; }
.file-pathbar { display: grid; grid-template-columns: minmax(180px, 1fr) minmax(180px, 280px) 140px auto; gap: 8px; align-items: center; padding: 8px; border: 1px solid #ddd8d3; border-radius: 12px; background: rgba(251,250,248,.92); }
.file-pathbar span { color: #484336; font-size: 13px; font-weight: 900; }
.file-pathbar input, .file-pathbar select { min-width: 0; height: 36px; padding: 0 10px; border: 1px solid #ddd8d3; border-radius: 10px; background: #fff; }
.desktop-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); align-content: start; gap: 14px; padding: 4px; overflow: auto; }
.desktop-file { min-height: 142px; display: grid; justify-items: center; align-content: center; gap: 7px; padding: 12px; border: 1px solid transparent; background: rgba(255,253,250,.72); text-align: center; }
.desktop-file:hover, .desktop-file.selected { border-color: #B88A44; background: rgba(239,229,213,.82); }
.desktop-file b { width: 100%; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-size: 13px; }
.desktop-file small, .desktop-file i { color: #706D6D; font-size: 11px; font-style: normal; }
.file-icon { width: 60px; height: 54px; display: grid; place-items: center; border-radius: 12px; background: #EEECEA; color: #111110; font-size: 13px; font-weight: 900; box-shadow: inset 0 -10px 0 rgba(17,17,16,.05); }
.file-icon.pdf { background: #f4dfda; color: #8f3f2d; }
.file-icon.doc, .file-icon.text { background: #efe5d5; color: #694b22; }
.file-icon.sheet { background: #e6ebe3; color: #425744; }
.file-icon.image { background: #dfeff1; color: #245a61; }
.file-icon.video { background: #e8e6df; color: #111110; }
.file-table .tr { min-width: 1040px; }
.file-statusbar { display: flex; align-items: center; justify-content: space-between; gap: 12px; padding: 9px 12px; border: 1px solid #ddd8d3; border-radius: 12px; background: rgba(251,250,248,.92); color: #706D6D; font-size: 12px; }
.graph { min-height: 360px; display: flex; flex-wrap: wrap; align-content: center; justify-content: center; gap: 14px; border-radius: 14px; background: radial-gradient(circle, #EEECEA 1px, transparent 1px), #fbfaf8; background-size: 24px 24px; }
.graph button { border-radius: 999px; }
.graph .equipment { padding: 18px 24px; background: #111110; color: #EEECEA; }
.graph .fault { background: #EEECEA; }
.graph .doc, .graph .sop { background: #fff; }
.empty { padding: 28px; border-radius: 12px; background: #f4f2ef; color: #706D6D; text-align: center; }
.profile-card { display: grid; place-items: start; gap: 12px; }
.profile-hero { display: grid; grid-template-columns: 88px minmax(0, 1fr) auto; align-items: center; gap: 18px; padding: 20px; border: 1px solid #ddd8d3; border-radius: 16px; background: linear-gradient(180deg, #fffdfa, #f4f2ef); box-shadow: 0 14px 30px rgba(17,17,16,.04); }
.profile-hero img { width: 88px; height: 88px; border-radius: 50%; object-fit: cover; }
.profile-hero h2 { margin: 4px 0; font-size: 28px; }
.profile-section { display: grid; gap: 14px; padding: 16px; border: 1px solid #ddd8d3; border-radius: 14px; background: #fbfaf8; box-shadow: 0 14px 30px rgba(17,17,16,.04); }
.profile-metrics { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 8px; }
.profile-metrics span { display: grid; gap: 4px; padding: 10px; border-radius: 10px; background: #f4f2ef; color: #706D6D; font-size: 12px; }
.profile-metrics b { color: #111110; font-size: 22px; }
.profile-list { display: grid; gap: 8px; }
.profile-list button { min-height: 48px; display: grid; gap: 4px; text-align: left; background: #fffdfa; }
.profile-list small { color: #706D6D; }
.agent-history { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px; }
.agent-history article { display: grid; grid-template-columns: 48px minmax(0, 1fr) auto; align-items: center; gap: 10px; padding: 12px; border: 1px solid #ddd8d3; border-radius: 12px; background: #fffdfa; }
.agent-history img { width: 48px; height: 48px; border-radius: 50%; object-fit: cover; }
.agent-history small { display: block; margin-top: 4px; color: #706D6D; }
pre { white-space: pre-wrap; padding: 12px; border-radius: 12px; background: #111110; color: #EEECEA; }
.modal { position: fixed; inset: 0; display: grid; place-items: center; padding: 24px; background: rgba(17,17,16,.42); z-index: 20; }
.modal-card { position: relative; width: min(760px, 96vw); max-height: 88vh; overflow: auto; display: grid; gap: 14px; padding: 22px; border-radius: 16px; background: #fbfaf8; }
.wide-modal { width: min(980px, 96vw); }
.close { position: absolute; top: 12px; right: 12px; width: 34px; height: 34px; padding: 0; }
.preview-box { min-height: 360px; display: grid; place-items: center; border: 1px solid #ddd8d3; border-radius: 12px; overflow: hidden; background: #f4f2ef; }
.preview-box img, .preview-box iframe { width: 100%; height: 520px; object-fit: contain; border: 0; }
.toast { position: fixed; right: 22px; bottom: 22px; padding: 12px 16px; border-radius: 12px; background: #111110; color: #EEECEA; z-index: 30; }
.operator-panel { min-height: 0; display: flex; flex-direction: column; gap: 16px; padding: 22px 20px; border-left: 1px solid #ddd8d3; background: linear-gradient(180deg, #f4f2ef, #EEECEA); }
.operator-head { display: grid; grid-template-columns: 76px minmax(0, 1fr) auto; align-items: center; gap: 12px; }
.operator-avatar { width: 76px; height: 76px; border-radius: 50%; object-fit: cover; box-shadow: 0 16px 28px rgba(17,17,16,.12); }
.operator-head h2 { margin-top: 5px; font-size: 22px; }
.operator-role { display: inline-flex; margin-top: 7px; padding: 4px 8px; border-radius: 999px; background: #EEECEA; color: #484336; font-size: 12px; font-weight: 900; }
.operator-status { flex-shrink: 0; padding: 6px 10px; border-radius: 999px; background: #e6ebe3; color: #425744; font-size: 12px; font-weight: 900; }
.operator-status.busy { background: #efe5d5; color: #694b22; }
.operator-duty { color: #706D6D; font-size: 13px; line-height: 1.6; }
.operator-slogan { padding: 10px 12px; border-radius: 12px; background: #fbfaf8; color: #484336; font-size: 13px; font-weight: 900; }
.chat-thread { flex: 1; min-height: 0; display: flex; flex-direction: column; gap: 12px; overflow: auto; padding-right: 2px; }
.bubble { max-width: 88%; padding: 12px 14px; border-radius: 14px; color: #484336; background: #fbfaf8; font-size: 13px; line-height: 1.55; }
.bubble.user { align-self: flex-end; background: #111110; color: #EEECEA; }
.bubble.assistant { align-self: flex-start; }
.visually-hidden { position: absolute !important; width: 1px !important; height: 1px !important; padding: 0 !important; margin: -1px !important; overflow: hidden !important; clip: rect(0, 0, 0, 0) !important; white-space: nowrap !important; border: 0 !important; }
.file-pills img { width: 34px; height: 34px; border-radius: 7px; object-fit: cover; vertical-align: middle; margin-right: 6px; }
.modality-line { margin: 10px 0; }
.ask-box .attach-button { flex: 0 0 34px; width: 34px; padding: 0; font-size: 20px; }
.assistant-attachments { display: flex; flex-wrap: wrap; gap: 6px; padding-top: 8px; }
.assistant-attachments span { display: inline-flex; align-items: center; gap: 5px; max-width: 100%; padding: 5px 8px; border-radius: 8px; background: #edf6f5; color: #285f5b; font-size: 11px; }
.assistant-attachments button { border: 0; padding: 0 2px; background: transparent; color: #a44735; }
.executable-sop > span { align-items: flex-start; }
.executable-sop > span > span { display: grid; flex: 1; gap: 3px; padding: 0; background: transparent; }
.executable-sop > span > span small { color: var(--muted); line-height: 1.55; }
.executable-sop > span > button { margin-left: auto; white-space: nowrap; }
.executable-sop > span.completed { background: #eef7f2; color: #376958; }
.safety-reminders { display: grid; gap: 7px; margin-top: 14px; padding: 13px; border: 1px solid #ead8ba; border-radius: 10px; background: #fff9ef; }
.safety-reminders span { color: #765b2c; font-size: 13px; }
.knowledge-review-list { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; margin-top: 18px; }
.knowledge-review-list textarea { width: 100%; min-height: 86px; margin-top: 6px; padding: 10px; border: 1px solid var(--line); border-radius: 9px; resize: vertical; }
.quick-card { width: 100%; display: grid; grid-template-columns: 34px minmax(0, 1fr) auto; align-items: center; gap: 10px; padding: 12px; border: 1px solid #ddd8d3; border-radius: 14px; background: #fbfaf8; text-align: left; }
.quick-card > span { width: 34px; height: 34px; display: grid; place-items: center; border-radius: 11px; background: #111110; color: #EEECEA; }
.quick-card small { display: block; margin-top: 4px; color: #706D6D; font-size: 12px; line-height: 1.35; }
.quick-card i { font-style: normal; color: #706D6D; }
.operator-chips { display: flex; flex-wrap: wrap; gap: 8px; }
.operator-chips button { min-height: 32px; padding: 6px 10px; border-radius: 999px; background: #fbfaf8; font-size: 12px; }
.ask-box { display: grid; grid-template-columns: minmax(0, 1fr) 40px; gap: 8px; padding: 8px; border: 1px solid #111110; border-radius: 16px; background: #fbfaf8; }
.ask-box input { min-width: 0; border: 0; outline: 0; background: transparent; color: #111110; }
.ask-box button { width: 40px; height: 40px; padding: 0; border-radius: 50%; background: #111110; color: #EEECEA; }

/* Web 端视觉基线：克制的工业色、清晰边界和稳定的信息层级。 */
:global(:root) {
  --ink: #172328;
  --muted: #68787e;
  --line: #dbe3e5;
  --surface: #ffffff;
  --surface-soft: #f4f7f7;
  --canvas: #edf2f3;
  --teal: #16766f;
  --teal-dark: #0f5854;
  --amber: #c8872e;
  --danger: #b44c43;
  --blue: #3979b8;
  --violet: #8062b5;
  --coral: #d86657;
}
:global(body) { background: radial-gradient(circle at 82% 6%, rgba(75,137,181,.08), transparent 30%), var(--canvas); color: var(--ink); font-family: "Segoe UI", "Microsoft YaHei", "PingFang SC", system-ui, sans-serif; }
.app-shell { grid-template-columns: 220px minmax(0, 1fr); background: var(--canvas); }
.app-shell.collapsed { grid-template-columns: 76px minmax(0, 1fr); }
.side-nav { gap: 22px; padding: 18px 12px; border-right: 0; background: #15262d; box-shadow: 8px 0 30px rgba(20, 38, 45, .08); }
.brand { min-height: 78px; border: 1px solid rgba(255,255,255,.08); background: rgba(255,255,255,.96); }
.brand img { width: 160px; height: 64px; filter: none; }
.side-nav nav { gap: 6px; }
.side-nav nav button { min-height: 44px; border-radius: 9px; color: #c8d3d6; font-weight: 700; letter-spacing: .02em; }
.nav-icon { background: rgba(255,255,255,.07); color: #aac0c4; }
.side-nav nav button.active { background: #f7faf9; color: #153a3c; box-shadow: 0 8px 18px rgba(0,0,0,.16); }
.side-nav nav button:hover:not(.active) { background: rgba(255,255,255,.08); color: #fff; }
.side-nav nav button.active .nav-icon { background: #dcefed; color: var(--teal); }
.collapse-btn { background: rgba(255,255,255,.07); color: #c8d3d6; }
.topbar { height: 76px; grid-template-columns: minmax(180px, 1fr) minmax(280px, 410px) auto 38px auto auto; border-bottom-color: var(--line); background: rgba(255,255,255,.96); }
.page-title-block { --title-accent: var(--teal); position: relative; align-self: center; min-width: 230px; max-width: 420px; padding: 8px 15px 8px 18px; overflow: hidden; border: 1px solid color-mix(in srgb, var(--title-accent) 22%, #dfe8e8); border-radius: 11px; background: linear-gradient(105deg, color-mix(in srgb, var(--title-accent) 10%, #fff), rgba(255,255,255,.94) 72%); box-shadow: 0 5px 14px rgba(31,55,63,.045); }
.page-title-block::before { content: ""; position: absolute; inset: 0 auto 0 0; width: 5px; background: var(--title-accent); }
.page-title-block::after { content: ""; position: absolute; top: -26px; right: -12px; width: 84px; height: 84px; border-radius: 50%; background: color-mix(in srgb, var(--title-accent) 9%, transparent); pointer-events: none; }
.page-title-block.title-home { --title-accent: var(--teal); }
.page-title-block.title-search { --title-accent: var(--blue); }
.page-title-block.title-tasks { --title-accent: var(--amber); }
.page-title-block.title-knowledge { --title-accent: var(--violet); }
.page-title-block.title-profile { --title-accent: var(--coral); }
.page-title-block .breadcrumb { position: relative; z-index: 1; color: color-mix(in srgb, var(--title-accent) 82%, #33494e); font-size: 10px; }
.page-title-block h1 { position: relative; z-index: 1; margin-top: 2px; font-size: 19px; }
.content-shell { height: calc(100vh - 76px); grid-template-columns: minmax(0, 1fr) 320px; }
.breadcrumb, .eyebrow { color: var(--teal); letter-spacing: .08em; }
h1 { color: var(--ink); font-size: 21px; letter-spacing: .02em; }
.global-search { border-color: var(--line); border-radius: 10px; background: var(--surface-soft); transition: border-color .18s, box-shadow .18s; }
.global-search:focus-within { border-color: #82aaa7; box-shadow: 0 0 0 3px rgba(22,118,111,.1); }
.global-search button { min-height: 28px; padding: 4px 10px; border: 0; border-radius: 7px; background: var(--teal); color: #fff; font-size: 12px; }
.global-search button { min-width: 46px; white-space: nowrap; }
.work-strip span, .badge, .tag-line span { background: #e9eff0; color: #41545a; }
.icon-button, .user-chip { border-color: var(--line); background: var(--surface); }
.page-scroll { padding: 20px; }
.page-grid { gap: 14px; }
.panel, .welcome-card, .agent-card, .stat-card, .profile-card { border-color: var(--line); border-radius: 12px; background: var(--surface); box-shadow: 0 8px 24px rgba(31, 55, 63, .055); }
.welcome-card { position: relative; overflow: hidden; border-top: 3px solid var(--teal); }
.welcome-brand { grid-template-columns: 220px minmax(0, 1fr); gap: 20px; }
.welcome-brand img { width: 220px; height: 112px; filter: none; }
.welcome-card h2 { color: var(--ink); font-size: 25px; line-height: 1.35; }
.welcome-card p { color: var(--muted); line-height: 1.65; }
.execution-summary { display: grid; grid-template-columns: 74px minmax(0, 1fr) 108px 108px; align-items: center; gap: 14px; margin-top: 14px; padding: 12px 14px; border: 1px solid #d9e8e6; border-radius: 11px; background: #f4f9f8; }
.progress-ring { --progress: 0%; width: 64px; height: 64px; display: grid; place-items: center; border-radius: 50%; background: conic-gradient(var(--teal) var(--progress), #d9e6e5 0); }
.progress-ring::before { content: ""; grid-area: 1 / 1; width: 50px; height: 50px; border-radius: 50%; background: #fff; }
.progress-ring span { z-index: 1; grid-area: 1 / 1; display: grid; color: var(--muted); font-size: 9px; text-align: center; }
.progress-ring b { color: var(--ink); font-size: 15px; }
.execution-copy strong { color: var(--ink); font-size: 14px; }
.execution-copy p { margin-top: 4px; font-size: 12px; }
.summary-metric { display: grid; gap: 3px; padding-left: 12px; border-left: 1px solid #cedfdd; }
.summary-metric b { color: var(--ink); font-size: 22px; }
.summary-metric span { color: var(--muted); font-size: 11px; }
.health-grid { grid-template-columns: repeat(5, minmax(0, 1fr)); }
.health-grid span, .analysis-grid span, .detail-grid span { background: var(--surface-soft); color: #53656b; }
.focus-tasks { display: grid; gap: 6px; margin-top: 12px; }
.focus-tasks-title { display: flex; align-items: center; justify-content: space-between; color: var(--ink); font-size: 13px; }
.focus-tasks-title span { color: var(--muted); font-size: 11px; }
.focus-tasks button { display: grid; grid-template-columns: minmax(0, 1fr) auto 42px; align-items: center; gap: 8px; min-height: 40px; padding: 7px 9px; border-color: #e2e8e9; background: #fbfcfc; text-align: left; }
.focus-tasks button:hover { border-color: #a8c5c2; background: #f1f8f7; }
.focus-tasks button span { display: flex; align-items: baseline; gap: 7px; min-width: 0; }
.focus-tasks button small { overflow: hidden; color: var(--muted); font-size: 11px; text-overflow: ellipsis; white-space: nowrap; }
.focus-tasks button em { color: var(--muted); font-size: 11px; font-style: normal; text-align: right; }
.agent-card { align-self: start; }
.agent-card-head { margin-bottom: 6px; }
.agent-card-head h3 { margin-top: 5px; font-size: 16px; }
.agent-card-head > small { color: var(--muted); font-size: 11px; }
.agent-row { grid-template-columns: 40px 8px minmax(0, 1fr) auto; width: 100%; gap: 8px; padding: 8px 6px; border: 0; border-bottom: 1px solid #edf1f2; border-radius: 8px; background: transparent; color: var(--ink); text-align: left; }
.agent-row:hover, .agent-row.active { background: #edf6f5; }
.agent-row img { width: 40px; height: 40px; box-shadow: none; }
.agent-row i { color: #91a0a5; font-style: normal; }
.agent-row small { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.kpi-ribbon { display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)); gap: 10px; }
.stat-card { min-width: 0; min-height: 106px; border-top: 3px solid #9cb7b5; }
.stat-card:nth-child(4) { border-top-color: var(--danger); }
.stat-card:nth-child(5) { border-top-color: var(--amber); }
.stat-card:nth-child(1) { border-top-color: var(--blue); }
.stat-card:nth-child(2) { border-top-color: var(--amber); }
.stat-card:nth-child(3) { border-top-color: var(--teal); }
.stat-card:nth-child(6) { border-top-color: var(--violet); }
.stat-card:nth-child(1) b { color: var(--blue); }
.stat-card:nth-child(2) b, .stat-card:nth-child(5) b { color: #a96c20; }
.stat-card:nth-child(3) b { color: var(--teal); }
.stat-card:nth-child(4) b { color: var(--danger); }
.stat-card:nth-child(6) b { color: var(--violet); }
.stat-card:hover { transform: translateY(-2px); border-color: #aac3c1; box-shadow: 0 12px 25px rgba(31, 55, 63, .09); }
.stat-card span, .stat-card small { color: var(--muted); }
.stat-card b { color: var(--ink); font-size: 28px; }
.quick-grid button, .history-row, .alert-list button { border-color: var(--line); background: var(--surface-soft); }
.quick-grid button:hover, .history-row:hover, .alert-list button:hover { border-color: #a6c5c2; background: #edf6f5; }
.quick-grid button:nth-child(4n+1) { border-left: 3px solid var(--blue); }
.quick-grid button:nth-child(4n+2) { border-left: 3px solid var(--teal); }
.quick-grid button:nth-child(4n+3) { border-left: 3px solid var(--violet); }
.quick-grid button:nth-child(4n) { border-left: 3px solid var(--amber); }
.home-task-panel, .quick-panel { align-self: stretch; }
.home-task-title, .quick-panel-title { margin-bottom: 12px; }
.task-title-actions { display: flex; align-items: center; gap: 9px; }
.task-title-actions > span { padding: 5px 9px; border-radius: 999px; background: #edf3f4; color: var(--muted); font-size: 11px; font-weight: 800; }
.task-title-actions .ghost { border-color: #cddadd; background: #fff; color: var(--teal-dark); font-size: 12px; font-weight: 800; }
.home-task-list { display: grid; gap: 8px; }
.home-task-row { display: grid; grid-template-columns: minmax(210px, 1.45fr) minmax(105px, .7fr) minmax(105px, .65fr) minmax(130px, .9fr) 20px; align-items: center; gap: 12px; min-height: 76px; padding: 10px 11px; border: 1px solid #e2e9ea; border-radius: 11px; background: #fbfcfc; color: var(--ink); text-align: left; }
.home-task-row:hover { transform: translateY(-2px); border-color: #b7cdcf; background: #f7fbfb; box-shadow: 0 8px 18px rgba(31,55,63,.07); }
.task-device-block, .task-fault-block, .task-progress-block { display: grid; gap: 3px; min-width: 0; }
.task-device-block small { color: var(--teal); font-size: 10px; font-weight: 800; letter-spacing: .03em; }
.task-device-block b { overflow: hidden; font-size: 14px; text-overflow: ellipsis; white-space: nowrap; }
.task-device-block em { overflow: hidden; color: var(--muted); font-size: 10px; font-style: normal; text-overflow: ellipsis; white-space: nowrap; }
.task-fault-block { justify-items: start; }
.task-fault-block small, .task-owner-block small, .task-progress-block small { color: #859399; font-size: 10px; }
.task-fault-block > b { font-size: 13px; }
.task-fault-block .badge { margin-top: 1px; padding: 3px 7px; font-size: 9px; font-style: normal; }
.task-owner-block { display: grid; grid-template-columns: 34px minmax(0, 1fr); align-items: center; gap: 8px; min-width: 0; }
.task-owner-block > i { width: 34px; height: 34px; display: grid; place-items: center; border-radius: 10px; background: #e4f0ef; color: var(--teal); font-size: 13px; font-style: normal; font-weight: 900; }
.task-owner-block > span { display: grid; gap: 3px; min-width: 0; }
.task-owner-block b { overflow: hidden; font-size: 12px; text-overflow: ellipsis; white-space: nowrap; }
.task-progress-block > span { display: flex; align-items: center; justify-content: space-between; gap: 7px; }
.task-progress-block > span b { font-size: 12px; }
.task-progress-block > span em { color: var(--teal); font-size: 10px; font-style: normal; font-weight: 900; }
.task-progress-block > i { width: 100%; height: 5px; overflow: hidden; border-radius: 999px; background: #e5ecec; }
.task-progress-block > i u { display: block; height: 100%; border-radius: inherit; background: linear-gradient(90deg, var(--blue), var(--teal)); text-decoration: none; }
.row-arrow { color: #94a2a7; font-size: 16px; }
.quick-panel { background: linear-gradient(155deg, #fff 0%, #fbfcfc 70%, #f3f8f8 100%); }
.home-quick-grid { gap: 9px; }
.home-quick-grid button { display: grid; grid-template-columns: 38px minmax(0, 1fr) auto; align-items: center; gap: 9px; min-height: 72px; padding: 9px 10px; border: 1px solid #e0e8e9; border-left: 1px solid #e0e8e9 !important; background: rgba(255,255,255,.86); text-align: left; }
.home-quick-grid button:hover { transform: translateY(-2px); border-color: #bdd0d2; background: #fff; box-shadow: 0 8px 17px rgba(31,55,63,.07); }
.quick-icon { width: 38px; height: 38px; display: grid; place-items: center; border-radius: 11px; }
.quick-copy { display: grid; gap: 3px; min-width: 0; }
.quick-copy b { overflow: hidden; color: var(--ink); font-size: 12px; text-overflow: ellipsis; white-space: nowrap; }
.quick-copy small { overflow: hidden; color: var(--muted); font-size: 9px; text-overflow: ellipsis; white-space: nowrap; }
.home-quick-grid button > i { color: #96a4a9; font-style: normal; }
.quick-blue .quick-icon { background: #e2edf8; color: var(--blue); }
.quick-teal .quick-icon { background: #dff1ef; color: var(--teal); }
.quick-violet .quick-icon { background: #eee8f7; color: var(--violet); }
.quick-amber .quick-icon { background: #faecd8; color: #b57526; }
.chart-wrap svg { background: linear-gradient(#e5ebec 1px, transparent 1px), #fbfcfc; }
.chart-wrap polyline { stroke: var(--teal); }
.chart-wrap rect { fill: #a9c3c1; }
.distribution b, .load-row b { background: var(--teal); }
.primary, .tabs button.active, .view-switch button.active { border-color: var(--teal-dark); background: var(--teal-dark); color: #fff; }
button { transition: background-color .18s, border-color .18s, color .18s, transform .18s, box-shadow .18s; }
.operator-panel { gap: 14px; padding: 20px 18px; border-left-color: var(--line); background: #f2f6f6; }
.operator-avatar { width: 64px; height: 64px; border: 3px solid #fff; box-shadow: 0 8px 20px rgba(22, 60, 64, .14); }
.operator-head { grid-template-columns: 64px minmax(0, 1fr) auto; }
.operator-head h2 { color: var(--ink); font-size: 20px; }
.operator-role, .operator-slogan, .bubble, .quick-card, .operator-chips button { background: #fff; }
.operator-slogan { border-left: 3px solid var(--teal); color: #465b60; }
.bubble.user { background: var(--teal-dark); color: #fff; }
.quick-card { border-color: #ccdcda; }
.quick-card > span, .ask-box button { background: var(--teal-dark); color: #fff; }
.ask-box { border-color: #9bb9b7; background: #fff; }
.toast { background: #153438; color: #fff; }

/* 首页下半区：用颜色表达状态，而不是单纯堆叠灰色卡片。 */
.section-title-row { display: flex; align-items: flex-start; justify-content: space-between; gap: 14px; margin-bottom: 14px; }
.section-title-row h3 { margin-top: 5px; color: var(--ink); font-size: 19px; }
.section-count, .quiet-label { padding: 5px 9px; border-radius: 999px; background: #edf3f4; color: #66777d; font-size: 11px; font-weight: 800; }
.alert-panel { position: relative; overflow: hidden; background: linear-gradient(160deg, #ffffff 0%, #fbfcfc 66%, #f2f7f7 100%); }
.alert-panel, .analytics-panel { align-self: start; }
.alert-panel::before, .analytics-panel::before, .activity-panel::before, .knowledge-recent-panel::before { content: ""; position: absolute; top: 0; left: 18px; right: 18px; height: 3px; border-radius: 0 0 4px 4px; background: linear-gradient(90deg, var(--coral), var(--amber)); }
.analytics-panel, .activity-panel, .knowledge-recent-panel { position: relative; overflow: hidden; }
.analytics-panel::before { background: linear-gradient(90deg, var(--blue), var(--teal), var(--violet)); }
.activity-panel::before { background: linear-gradient(90deg, var(--blue), #63a9cb); }
.knowledge-recent-panel::before { background: linear-gradient(90deg, var(--violet), var(--teal)); }
.alert-list { height: auto; grid-auto-rows: minmax(82px, auto); align-content: start; gap: 9px; margin-top: 0; }
.alert-list button { position: relative; display: grid; grid-template-columns: 42px minmax(0, 1fr) auto; align-items: center; gap: 11px; min-height: 82px; padding: 11px 12px; overflow: visible; border: 1px solid transparent; background: #f6f8f8; }
.alert-list button:hover { transform: translateX(3px); box-shadow: 0 8px 18px rgba(31,55,63,.08); }
.alert-icon { width: 40px; height: 40px; display: grid; place-items: center; border-radius: 11px; }
.alert-copy { display: grid; align-content: center; gap: 4px; min-width: 0; overflow: visible; }
.alert-copy b { color: var(--ink); font-size: 14px; line-height: 1.35; }
.alert-copy small { display: block; margin-top: 0; overflow: visible; color: var(--muted); line-height: 1.45; text-overflow: clip; white-space: normal; }
.alert-arrow { color: #91a1a6; font-size: 16px; }
.tone-danger { border-color: #f0d8d5 !important; background: #fff7f6 !important; }
.tone-danger .alert-icon { background: #fbe3e0; color: var(--danger); }
.tone-amber { border-color: #f0e0c8 !important; background: #fffbf4 !important; }
.tone-amber .alert-icon { background: #f9ecd6; color: #b67625; }
.tone-violet { border-color: #e3dbf0 !important; background: #faf8ff !important; }
.tone-violet .alert-icon { background: #eee8f7; color: var(--violet); }
.tone-teal { border-color: #d5e8e5 !important; background: #f5fbfa !important; }
.tone-teal .alert-icon { background: #dff1ef; color: var(--teal); }
.chart-legend { display: flex; align-items: center; gap: 7px; color: #4f6268; font-size: 11px; }
.chart-legend i { width: 9px; height: 9px; border-radius: 50%; background: var(--teal); }
.chart-legend span { margin-left: 5px; padding: 4px 8px; border-radius: 999px; background: #eef4f5; color: #75858a; }
.analytics-panel .chart-wrap { grid-template-columns: minmax(0, 1fr) 210px; gap: 22px; margin-top: 8px; }
.analytics-panel .chart-wrap svg { height: 270px; border: 1px solid #e4ebec; background: linear-gradient(180deg, #fbfdfe, #f7fafb); }
.chart-grid-line { stroke: #dfe8ea; stroke-width: 1; stroke-dasharray: 4 6; }
.chart-label { fill: #75858a; font-size: 11px; }
.trend-dot { fill: #fff; stroke: var(--teal); stroke-width: 3px; }
.distribution { align-content: center; gap: 15px; }
.distribution-head { display: flex; justify-content: space-between; align-items: baseline; padding-bottom: 4px; border-bottom: 1px solid #e6ecee; }
.distribution-head b { height: auto; background: transparent; color: var(--ink); font-size: 14px; }
.distribution-head small { color: var(--muted); }
.distribution span { grid-template-columns: 10px minmax(0, 1fr) auto; grid-template-areas: "dot label value" ". bar bar"; gap: 5px 7px; color: var(--muted); }
.distribution span > i { grid-area: dot; width: 8px; height: 8px; align-self: center; border-radius: 50%; background: var(--dist-color); }
.distribution span > em { grid-area: label; font-style: normal; }
.distribution span > strong { grid-area: value; color: var(--ink); font-size: 12px; }
.distribution span > b { grid-area: bar; width: 100%; height: 6px; overflow: hidden; border-radius: 999px; background: #edf1f2; }
.distribution span > b > u { display: block; height: 100%; border-radius: inherit; background: var(--dist-color); text-decoration: none; }
.activity-list { display: grid; gap: 9px; }
.activity-list button { display: grid; grid-template-columns: 42px minmax(0, 1fr) auto; align-items: center; gap: 11px; min-height: 67px; padding: 10px 12px; border: 1px solid #e1e8ea; border-radius: 11px; background: #fbfcfc; text-align: left; }
.activity-list button:hover { transform: translateY(-2px); border-color: #b9cdd1; box-shadow: 0 9px 18px rgba(31,55,63,.07); }
.activity-icon { width: 40px; height: 40px; display: grid; place-items: center; border-radius: 11px; }
.activity-list button > span:nth-child(2) { display: grid; gap: 3px; min-width: 0; }
.activity-list small { color: var(--muted); font-size: 11px; }
.activity-list b { overflow: hidden; color: var(--ink); font-size: 14px; text-overflow: ellipsis; white-space: nowrap; }
.activity-list button > i { color: #91a1a6; font-style: normal; }
.activity-blue .activity-icon { background: #e3eef8; color: var(--blue); }
.activity-violet .activity-icon { background: #eee8f7; color: var(--violet); }
.activity-amber .activity-icon { background: #faecd8; color: #b57526; }
.activity-teal .activity-icon { background: #dff1ef; color: var(--teal); }
.text-link { border: 0; background: transparent; color: var(--teal); font-size: 12px; font-weight: 800; }
.knowledge-recent-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; }
.knowledge-recent-grid button { position: relative; display: grid; grid-template-columns: 48px minmax(0, 1fr); gap: 11px; min-height: 118px; padding: 13px; overflow: hidden; border: 1px solid #e0e7e9; border-radius: 12px; background: linear-gradient(145deg, #fff, #fafcfc); text-align: left; }
.knowledge-recent-grid button::after { content: ""; position: absolute; left: 0; top: 0; bottom: 0; width: 4px; background: var(--knowledge-accent); }
.knowledge-recent-grid button:hover { transform: translateY(-2px); border-color: color-mix(in srgb, var(--knowledge-accent) 42%, #dce5e7); box-shadow: 0 10px 20px rgba(31,55,63,.075); }
.knowledge-file-icon { width: 48px; height: 54px; display: grid; place-items: center; border-radius: 8px 8px 12px 8px; background: color-mix(in srgb, var(--knowledge-accent) 14%, #fff); color: var(--knowledge-accent); font-size: 10px; font-weight: 900; letter-spacing: .04em; }
.knowledge-card-copy { display: grid; align-content: start; gap: 5px; min-width: 0; }
.knowledge-card-copy b { overflow: hidden; color: var(--ink); font-size: 14px; text-overflow: ellipsis; white-space: nowrap; }
.knowledge-card-copy small { overflow: hidden; color: var(--muted); font-size: 11px; text-overflow: ellipsis; white-space: nowrap; }
.knowledge-card-copy em { justify-self: start; padding: 3px 7px; border-radius: 999px; background: color-mix(in srgb, var(--knowledge-accent) 10%, #fff); color: var(--knowledge-accent); font-size: 10px; font-style: normal; font-weight: 800; }
.citation-count { position: absolute; right: 12px; bottom: 10px; color: #839297; font-size: 10px; }

/* 检修任务页：统一页头、数据看板、筛选工具栏和复检卡片。 */
.task-nav-panel { position: relative; overflow: hidden; padding: 20px 22px; border-top: 4px solid var(--blue) !important; background: linear-gradient(120deg, #fff, #f5f9fc) !important; }
.task-nav-panel::after { content: "MAINTENANCE WORKFLOW"; position: absolute; right: 22px; bottom: 7px; color: rgba(58,111,158,.045); font-size: 27px; font-weight: 900; letter-spacing: .08em; pointer-events: none; }
.task-nav-panel h3 { margin-top: 5px; color: var(--ink); font-size: 20px; }
.task-nav-panel small { display: block; margin-top: 6px; color: var(--muted); font-size: 11px; }
.task-nav-panel .tabs { position: relative; z-index: 1; padding: 5px; border: 1px solid #d8e3e8; border-radius: 11px; background: rgba(255,255,255,.84); }
.task-nav-panel .tabs button { min-height: 34px; border: 0; background: transparent; color: #52666c; font-size: 11px; font-weight: 800; }
.task-nav-panel .tabs button.active { background: var(--teal-dark); color: #fff; box-shadow: 0 6px 14px rgba(20,82,80,.16); }
.tasks-page > .task-stat { grid-column: span 2; min-height: 112px; padding: 15px; }
.tasks-page > .task-stat span { min-height: 34px; line-height: 1.45; }
.tasks-page > .task-stat small { line-height: 1.45; }
.task-analytics { overflow: hidden; padding: 22px; border-top: 3px solid var(--teal) !important; background: linear-gradient(160deg, #fff, #f5faf9) !important; }
.task-analytics .panel-head > button { border-color: #cbdcda; background: #fff; color: var(--teal-dark); font-size: 11px; font-weight: 800; }
.task-analytics .analysis-cards { grid-template-columns: 1.15fr .9fr .9fr 1.2fr; align-items: stretch; gap: 13px; }
.task-analytics .analysis-cards section { min-height: 275px; padding: 15px; border-color: #dde7e7; background: rgba(255,255,255,.9); box-shadow: 0 6px 16px rgba(31,55,63,.035); }
.task-analytics .analysis-cards section > b { padding-bottom: 10px; border-bottom: 1px solid #e7eded; color: #2e4348; font-size: 13px; }
.task-analytics .analysis-cards section:last-child { grid-template-columns: repeat(2, minmax(0, 1fr)); align-content: start; }
.task-analytics .analysis-cards section:last-child > b { grid-column: 1 / -1; }
.task-analytics .chip-row { min-height: 34px; }
.task-analytics .analysis-cards svg { height: 180px; }
.trend-card-head { display: flex; align-items: center; justify-content: space-between; gap: 10px; padding-bottom: 9px; border-bottom: 1px solid #e7eded; }
.trend-card-head > b { color: #2e4348; font-size: 13px; }
.trend-card-head > span { padding: 4px 8px; border-radius: 999px; background: #e7f3f1; color: var(--teal-dark); font-size: 10px; font-weight: 800; }
.trend-summary { display: grid; grid-template-columns: auto 1fr auto; align-items: end; gap: 7px; padding: 4px 2px 0; }
.trend-summary strong { color: #183f46; font-size: 25px; line-height: 1; }
.trend-summary span { color: var(--muted); font-size: 10px; }
.trend-summary em { padding: 4px 7px; border-radius: 7px; background: #e7f4ee; color: #3e7d61; font-size: 9px; font-style: normal; font-weight: 800; }
.trend-summary em.down { background: #faece9; color: #ad554b; }
.task-analytics .analysis-cards .task-trend-chart { height: 166px; overflow: visible; border: 0; background: linear-gradient(180deg, rgba(235,246,245,.55), rgba(255,255,255,0)); }
.task-trend-grid { stroke: #dce8e8; stroke-width: 1; stroke-dasharray: 4 5; }
.task-trend-dot { fill: #fff; stroke: #2f7f8f; stroke-width: 4; }
.task-trend-value { fill: #235f69; font-size: 10px; font-weight: 800; }
.task-trend-label { fill: #73868b; font-size: 9px; }
.tasks-page .priority-list { grid-template-columns: 1fr; gap: 11px; }
.tasks-page .priority-list article { position: relative; display: grid; grid-template-columns: minmax(0, 1.2fr) minmax(0, 1.5fr) minmax(0, 1.15fr); grid-template-areas: "head desc meta" "progress progress foot"; align-items: center; gap: 12px 18px; min-width: 0; min-height: 146px; padding: 17px 18px 15px 20px; overflow: hidden; border-color: #dce6e5; background: linear-gradient(110deg, #fff, #f8fbfa); box-shadow: 0 7px 18px rgba(29,59,62,.045); }
.tasks-page .priority-list article::before { content: ""; position: absolute; inset: 0 auto 0 0; width: 4px; background: linear-gradient(var(--teal), var(--blue)); }
.priority-task-top { grid-area: head; display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; }
.priority-task-top > div { display: grid; gap: 3px; min-width: 0; }
.priority-task-top > div small { color: #789096; font-size: 9px; font-weight: 800; letter-spacing: .04em; }
.priority-task-top > div b { overflow: hidden; color: #203a40; font-size: 15px; text-overflow: ellipsis; white-space: nowrap; }
.priority-task-top > span { display: flex; align-items: center; gap: 7px; flex: 0 0 auto; }
.priority-task-top > span em { color: #52686d; font-size: 10px; font-style: normal; font-weight: 800; }
.priority-task-desc { grid-area: desc; min-height: 0; margin: 0; padding: 4px 18px; border-right: 1px solid #e5eceb; border-left: 1px solid #e5eceb; color: #64757a; font-size: 10px; line-height: 1.65; }
.priority-task-meta { grid-area: meta; display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 7px; }
.priority-task-meta > span { display: grid; gap: 3px; min-width: 0; padding: 8px 9px; border: 1px solid #e4ebea; border-radius: 9px; background: rgba(255,255,255,.82); }
.priority-task-meta small { color: #87969a; font-size: 8px; }
.priority-task-meta b { overflow: hidden; color: #374e53; font-size: 9px; text-overflow: ellipsis; white-space: nowrap; }
.priority-task-progress { grid-area: progress; display: grid; grid-template-columns: 1fr auto; align-items: center; gap: 9px; }
.priority-task-progress > div { height: 7px; overflow: hidden; border-radius: 999px; background: #e6eeee; }
.priority-task-progress > div span { display: block; height: 100%; border-radius: inherit; background: linear-gradient(90deg, var(--teal), #55a79c); }
.priority-task-progress > b { color: var(--teal-dark); font-size: 10px; }
.tasks-page .priority-list article > footer { grid-area: foot; display: flex; align-items: flex-end; justify-content: space-between; gap: 10px; padding-top: 10px; border-top: 1px solid #e6eceb; }
.tasks-page .priority-list article > footer > span { display: grid; gap: 2px; min-width: 0; }
.tasks-page .priority-list article > footer small { color: #89979a; font-size: 8px; }
.tasks-page .priority-list article > footer b { color: #334b50; font-size: 10px; }
.tasks-page .priority-list article > footer em { color: #a16d31; font-size: 8px; font-style: normal; }
.tasks-page .priority-list article > footer button { min-height: 34px; padding: 7px 11px; border-color: #cfe0de; background: #f2f8f7; color: var(--teal-dark); font-size: 10px; font-weight: 800; }
.tasks-page .priority-list article > footer button i { margin-left: 5px; font-style: normal; }
.task-modal-card { width: min(900px, 96vw); gap: 16px; padding: 0 24px 22px; border: 1px solid #dce7e6; border-radius: 18px; background: #f8fbfa; box-shadow: 0 26px 70px rgba(16,37,43,.2); }
.task-modal-card .close { z-index: 3; top: 15px; right: 16px; border-color: rgba(255,255,255,.35); background: rgba(255,255,255,.14); color: #fff; }
.task-modal-hero { position: sticky; top: 0; z-index: 2; display: flex; align-items: center; justify-content: space-between; gap: 20px; margin: 0 -24px; padding: 22px 64px 20px 24px; border-radius: 18px 18px 0 0; background: linear-gradient(120deg, #164f52, #207b75 62%, #3e8995); color: #fff; box-shadow: 0 8px 18px rgba(24,80,81,.14); }
.task-modal-hero .eyebrow { color: #bde5df; }
.task-modal-hero h2 { margin: 5px 0; color: #fff; font-size: 23px; }
.task-modal-hero small { color: rgba(255,255,255,.76); }
.task-modal-hero > span { display: flex; align-items: center; gap: 9px; }
.task-modal-hero > span b { padding: 6px 10px; border-radius: 999px; background: rgba(255,255,255,.14); font-size: 11px; }
.task-modal-progress { display: grid; grid-template-columns: 1fr auto; align-items: center; gap: 12px; padding: 2px 2px 0; }
.task-modal-progress > div { height: 9px; overflow: hidden; border-radius: 999px; background: #dfe9e8; }
.task-modal-progress > div span { display: block; height: 100%; border-radius: inherit; background: linear-gradient(90deg, var(--teal), #69b3a9); }
.task-modal-progress > b { color: var(--teal-dark); font-size: 12px; }
.task-modal-stats { grid-template-columns: repeat(4, minmax(0, 1fr)); margin-top: 0; }
.task-modal-stats span { display: grid; gap: 5px; padding: 11px 12px; border: 1px solid #dde7e6; background: #fff; }
.task-modal-stats small { color: #87979a; font-size: 9px; }
.task-modal-stats b { overflow: hidden; color: #30494e; font-size: 11px; text-overflow: ellipsis; white-space: nowrap; }
.task-modal-description { padding: 13px 15px; border-left: 4px solid var(--blue); border-radius: 0 10px 10px 0; background: #eef5f8; color: #4f646a; line-height: 1.7; }
.task-modal-section-title { display: flex; align-items: center; justify-content: space-between; padding-bottom: 9px; border-bottom: 1px solid #dfe8e7; }
.task-modal-section-title span { color: #243e43; font-size: 16px; font-weight: 900; }
.task-modal-section-title small { padding: 4px 8px; border-radius: 999px; background: #e4f1ef; color: var(--teal-dark); font-weight: 800; }
.task-modal-card .executable-sop { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 9px; }
.task-modal-card .executable-sop > span { min-height: 76px; padding: 11px 12px; border: 1px solid #e0e7e6; border-radius: 11px; background: #fff; }
.task-modal-card .executable-sop > span > b { background: #dceeed; color: var(--teal-dark); }
.task-modal-card .executable-sop > span > button { min-height: 34px; border-color: #d1dfde; background: #f5f9f8; color: var(--teal-dark); font-size: 10px; }
.task-modal-card .safety-reminders { grid-template-columns: minmax(165px, .7fr) repeat(3, minmax(0, 1fr)); align-items: center; padding: 14px; background: linear-gradient(100deg, #fff8ec, #fffdf9); }
.task-modal-card .safety-reminders > div { display: grid; gap: 3px; }
.task-modal-card .safety-reminders > div small { color: #9a7440; font-size: 9px; }
.task-modal-card .safety-reminders > span { padding: 7px 9px; border-radius: 8px; background: rgba(255,255,255,.75); text-align: center; }
.task-modal-actions { position: sticky; bottom: 0; z-index: 2; margin: 0 -24px -22px; padding: 14px 24px; border-top: 1px solid #dbe5e4; border-radius: 0 0 18px 18px; background: rgba(255,255,255,.96); box-shadow: 0 -8px 18px rgba(37,57,62,.06); }
.task-modal-actions button { min-width: 150px; min-height: 42px; font-weight: 800; }
.task-modal-actions .primary { background: linear-gradient(90deg, var(--teal-dark), var(--teal)); color: #fff; }
.task-manage-panel { padding: 20px; border-top: 3px solid var(--teal) !important; }
.task-manage-panel .filters { display: grid; grid-template-columns: repeat(4, minmax(120px, 1fr)) minmax(200px, 1.35fr) auto auto; gap: 9px; align-items: center; padding: 12px; border: 1px solid #dfe8e8; border-radius: 12px; background: #f5f9f8; }
.task-manage-panel .filters > select, .task-manage-panel .filters > input, .task-manage-panel .filters > button { width: 100%; height: 42px; min-height: 42px; }
.task-manage-panel .filters > select, .task-manage-panel .filters > input { border-color: #d3dfe0; background: #fff; font-size: 11px; }
.task-manage-panel .view-switch { height: 42px; flex-wrap: nowrap; padding: 3px; }
.task-manage-panel .view-switch button { width: auto; min-width: 52px; height: 34px; white-space: nowrap; }
.task-manage-panel .filters > .primary { min-width: 104px; white-space: nowrap; }
.task-manage-panel .table { margin-top: 15px; gap: 5px; }
.task-manage-panel .tr { min-height: 64px; border: 1px solid transparent; }
.task-manage-panel .tr:not(.head):nth-child(odd) { background: #f8fbfb; }
.task-manage-panel .tr:not(.head):hover { border-color: #c9dcda; background: #eef7f5; }
.task-manage-panel .tr.head { min-height: 44px; background: #eaf1f2; color: #52666b; }
.recheck-panel { position: relative; overflow: hidden; padding: 26px; border-top: 4px solid var(--violet) !important; background: linear-gradient(145deg, #fff 0%, #fbfafd 62%, #f6fafb 100%) !important; }
.recheck-panel::after { content: ""; position: absolute; right: -90px; top: -120px; width: 280px; height: 280px; border-radius: 50%; background: radial-gradient(circle, rgba(126,91,174,.12), transparent 68%); pointer-events: none; }
.recheck-heading { position: relative; z-index: 1; display: flex; align-items: flex-start; justify-content: space-between; gap: 18px; margin-bottom: 22px; padding-bottom: 17px; border-bottom: 1px solid #e4e3eb; }
.recheck-heading h3 { margin-top: 5px; color: var(--ink); font-size: 22px; }
.recheck-heading > span { padding: 7px 12px; border: 1px solid #dfd4eb; border-radius: 999px; background: #f4eff9; color: var(--violet); font-size: 11px; font-weight: 900; white-space: nowrap; }
.recheck-panel .recheck-grid { position: relative; z-index: 1; gap: 18px; }
.recheck-panel .recheck-card { --recheck-accent: var(--violet); position: relative; min-height: 410px; grid-template-rows: auto auto auto 1fr auto; gap: 16px; padding: 21px; overflow: hidden; border-color: #dfe3e8; border-radius: 15px; background: rgba(255,255,255,.96); box-shadow: 0 9px 24px rgba(45,50,70,.06); transition: transform .2s, border-color .2s, box-shadow .2s; }
.recheck-panel .recheck-card.warning { --recheck-accent: var(--amber); }
.recheck-panel .recheck-card::before { content: ""; position: absolute; inset: 0 auto 0 0; width: 5px; background: linear-gradient(180deg, var(--recheck-accent), color-mix(in srgb, var(--recheck-accent) 58%, var(--blue))); }
.recheck-panel .recheck-card:hover { transform: translateY(-2px); border-color: color-mix(in srgb, var(--recheck-accent) 32%, #dfe3e8); box-shadow: 0 15px 31px rgba(45,50,70,.09); }
.recheck-card-head { display: grid; grid-template-columns: 44px minmax(0, 1fr) auto; align-items: center; gap: 13px; }
.recheck-mark { width: 44px; height: 44px; display: grid; place-items: center; border-radius: 12px; background: color-mix(in srgb, var(--recheck-accent) 12%, #fff); color: var(--recheck-accent); }
.recheck-mark .ui-icon { width: 21px; height: 21px; }
.recheck-card-head > div { min-width: 0; display: grid; gap: 5px; }
.recheck-card-head b { overflow: hidden; color: #233b40; font-size: 17px; line-height: 1.4; text-overflow: ellipsis; white-space: nowrap; }
.recheck-card-head small { overflow: hidden; color: var(--muted); font-size: 11px; text-overflow: ellipsis; white-space: nowrap; }
.recheck-card-head strong { padding: 6px 9px; border-radius: 8px; background: #eef5f4; color: var(--teal); font-size: 12px; }
.recheck-meta { display: grid; grid-template-columns: 1.25fr 1fr 1fr; gap: 8px; }
.recheck-meta > span { min-width: 0; display: grid; gap: 4px; padding: 9px 10px; border: 1px solid #e3eaeb; border-radius: 9px; background: #f8fafa; }
.recheck-meta small { color: #829195; font-size: 9px; }
.recheck-meta b { overflow: hidden; color: #344c51; font-size: 11px; text-overflow: ellipsis; white-space: nowrap; }
.recheck-field { display: grid; gap: 7px; color: #465d62; font-size: 11px; font-weight: 900; }
.recheck-select-wrap { position: relative; }
.recheck-select-wrap::after { content: "⌄"; position: absolute; right: 13px; top: 50%; color: #60777c; font-size: 18px; line-height: 1; transform: translateY(-58%); pointer-events: none; }
.recheck-panel .recheck-select-wrap select { height: 44px; padding: 0 40px 0 13px; border-color: #dbe4e5; border-radius: 10px; appearance: none; background: #f9fbfb; color: #263f44; font-weight: 800; cursor: pointer; }
.recheck-panel textarea { min-height: 90px; padding: 11px 13px; border-color: #dbe4e5; border-radius: 10px; background: #f9fbfb; color: #263f44; line-height: 1.6; resize: vertical; }
.recheck-panel select:focus, .recheck-panel textarea:focus { border-color: color-mix(in srgb, var(--recheck-accent) 48%, #dbe4e5); box-shadow: 0 0 0 3px color-mix(in srgb, var(--recheck-accent) 10%, transparent); background: #fff; }
.recheck-card-footer { display: flex; align-items: center; justify-content: space-between; gap: 14px; padding-top: 14px; border-top: 1px solid #e5ebec; }
.recheck-card-footer > span { display: flex; align-items: center; gap: 7px; color: #7a8c90; font-size: 10px; }
.recheck-card-footer > span i { width: 7px; height: 7px; border-radius: 50%; background: var(--recheck-accent); box-shadow: 0 0 0 4px color-mix(in srgb, var(--recheck-accent) 11%, transparent); }
.recheck-panel .recheck-card-footer .primary { min-width: 132px; min-height: 40px; border: 0; border-radius: 9px; background: linear-gradient(135deg, var(--teal-dark), var(--teal)); color: #fff; box-shadow: 0 7px 15px rgba(17,102,95,.16); }

/* 检索分类和检修建议：点击有计数、有空态，建议改为可扫读步骤卡。 */
.result-tab-hint { display: block; margin-top: 7px; color: var(--muted); font-size: 11px; }
.search-results-panel .tabs button { display: inline-flex; align-items: center; gap: 6px; }
.search-results-panel .tabs button em { min-width: 18px; height: 18px; display: grid; place-items: center; border-radius: 999px; background: #edf2f3; color: #718187; font-size: 9px; font-style: normal; }
.search-results-panel .tabs button.active em { background: rgba(255,255,255,.18); color: #fff; }
.result-filter-empty { min-height: 190px; display: grid; place-items: center; align-content: center; gap: 9px; margin-top: 18px; border: 1px dashed #cad9da; border-radius: 14px; background: #f7fafb; text-align: center; }
.result-filter-empty b { color: #33494e; font-size: 15px; }
.result-filter-empty span { color: var(--muted); font-size: 11px; }
.result-filter-empty button { border-color: #bcd2cf; background: #fff; color: var(--teal); font-size: 11px; font-weight: 800; }
.maintenance-advice-panel { overflow: hidden; padding: 22px 24px; border-top: 4px solid var(--amber) !important; background: linear-gradient(145deg, #fff, #fffcf7) !important; }
.advice-heading { display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; margin-bottom: 16px; }
.advice-heading h3 { margin-top: 5px; color: var(--ink); font-size: 18px; }
.advice-heading > span { padding: 6px 10px; border-radius: 999px; background: #faecd7; color: #a76a1e; font-size: 10px; font-weight: 900; }
.maintenance-advice-panel .sop-list { position: relative; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; counter-reset: step; }
.maintenance-advice-panel .sop-list span { position: relative; min-height: 86px; align-items: flex-start; padding: 15px; border: 1px solid #e7e1d8; background: #fff; color: #3e5055; line-height: 1.55; box-shadow: 0 6px 15px rgba(61,50,34,.035); }
.maintenance-advice-panel .sop-list b { flex: 0 0 30px; width: 30px; height: 30px; border-radius: 10px; background: linear-gradient(145deg, #d38c33, #b86d1e); color: #fff; box-shadow: 0 5px 10px rgba(184,109,30,.18); }
.advice-reference { display: flex; align-items: baseline; gap: 10px; margin-top: 16px; padding: 12px 14px; border-radius: 10px; background: #f6f2ec; color: #6f6254; font-size: 11px; line-height: 1.6; }
.advice-reference b { flex: 0 0 auto; color: #9a611d; }

/* 任务动态：紧凑时间轴，避免重复灰色条目拉长页面。 */
.task-event-panel { max-height: 560px; display: flex; flex-direction: column; overflow: hidden; background: linear-gradient(160deg, #fff 0%, #f7fbfb 100%); }
.task-event-heading { display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; padding-bottom: 13px; border-bottom: 1px solid #e1e9ea; }
.task-event-heading h3 { margin-top: 5px; color: var(--ink); font-size: 17px; }
.task-event-heading > span { padding: 5px 9px; border-radius: 999px; background: #e8f3f2; color: var(--teal); font-size: 10px; font-weight: 900; }
.task-events { position: relative; gap: 0; margin: 0; padding: 8px 4px 8px 2px; overflow: auto; }
.task-events::before { content: ""; position: absolute; left: 11px; top: 20px; bottom: 20px; width: 1px; background: linear-gradient(#7db5b0, #d7e6e5); }
.task-events article { position: relative; display: grid; grid-template-columns: 18px 112px minmax(0, 1fr); align-items: start; gap: 9px; min-height: 72px; padding: 11px 9px 11px 0; border-bottom: 1px solid #edf1f2; }
.task-events article:last-child { border-bottom: 0; }
.task-events article > i { position: relative; z-index: 1; width: 9px; height: 9px; margin: 5px 0 0 7px; border: 2px solid #fff; border-radius: 50%; background: var(--teal); box-shadow: 0 0 0 3px #d9eeeb; }
.task-events article:nth-child(3n+2) > i { background: var(--amber); box-shadow: 0 0 0 3px #f6ead8; }
.task-events article:nth-child(3n) > i { background: var(--blue); box-shadow: 0 0 0 3px #e0ebf5; }
.task-events time { color: #52666b; font-family: ui-monospace, "Cascadia Code", monospace; font-size: 11px; font-weight: 800; line-height: 1.5; }
.task-events p { color: #30464b; font-size: 12px; line-height: 1.65; }
.task-events article:hover { background: linear-gradient(90deg, transparent, #f0f7f6); }

/* 知识库页头与图谱工具栏。 */
.knowledge-nav-panel { overflow: hidden; padding: 20px 22px; border-top: 4px solid var(--teal) !important; background: linear-gradient(120deg, #fff 0%, #f5faf9 70%, #eef6f5 100%) !important; }
.knowledge-nav-panel::after { content: "KNOWLEDGE ASSET CENTER"; position: absolute; right: 22px; bottom: 7px; color: rgba(21,89,85,.055); font-size: 28px; font-weight: 900; letter-spacing: .08em; pointer-events: none; }
.knowledge-nav-panel { position: relative; }
.knowledge-nav-panel h3 { margin-top: 5px; color: var(--ink); font-size: 20px; }
.knowledge-nav-panel small { display: block; margin-top: 6px; color: var(--muted); font-size: 11px; }
.knowledge-nav-panel .tabs { position: relative; z-index: 1; padding: 5px; border: 1px solid #d7e5e3; border-radius: 11px; background: rgba(255,255,255,.82); }
.knowledge-nav-panel .tabs button { min-height: 34px; border: 0; background: transparent; color: #53676c; font-size: 11px; font-weight: 800; }
.knowledge-nav-panel .tabs button.active { background: var(--teal-dark); color: #fff; box-shadow: 0 6px 13px rgba(20,82,80,.17); }
.graph-panel { border-top: 3px solid var(--blue) !important; background: linear-gradient(180deg, #fff, #f8fbfc) !important; }
.graph-toolbar { grid-template-columns: minmax(260px, 1fr) 300px !important; gap: 14px 18px !important; margin: -18px -18px 16px !important; padding: 18px 18px 15px; border-bottom: 1px solid #dfe8ea; background: linear-gradient(135deg, #f6faf9, #f4f7fb); }
.graph-toolbar h3 { margin-top: 5px; color: var(--ink); font-size: 18px; }
.graph-search, .graph-search.expanded, .graph-search:focus-within { width: 300px; height: 42px; border-color: #cbdadc; border-radius: 11px; background: #fff; box-shadow: 0 6px 16px rgba(31,55,63,.055); }
.graph-search-trigger { border-radius: 9px; background: var(--teal-dark); }
.graph-search input { opacity: 1; color: var(--ink); font-size: 11px; }
.graph-controls { grid-column: 1 / -1; display: grid; grid-template-columns: repeat(4, minmax(130px, 1fr)) auto auto; gap: 9px; justify-content: stretch; padding-top: 13px; border-top: 1px solid #dfe8e8; }
.graph-controls select, .graph-controls button { width: 100%; height: 38px; border-color: #d2dfe0; border-radius: 9px; background: #fff; color: #3c5358; font-size: 11px; font-weight: 700; }
.graph-controls select:hover, .graph-controls button:hover { border-color: #8fb4b1; background: #edf6f5; }
.knowledge-map { gap: 18px; }
.map-canvas { border: 1px solid #dce7e8; box-shadow: inset 0 0 40px rgba(49,91,105,.035); }

/* 个人中心：按信息类型分色，并把设置项横向展开，消除底部大块空白。 */
.profile-page { align-items: start; }
.profile-section { --profile-accent: var(--teal); position: relative; align-content: start; overflow: hidden; padding: 20px; border-color: #dce5e6; background: linear-gradient(155deg, #fff 0%, #fbfcfc 100%); box-shadow: 0 9px 24px rgba(31,55,63,.06); }
.profile-section::before { content: ""; position: absolute; inset: 0 0 auto; height: 4px; background: var(--profile-accent); }
.profile-archive { --profile-accent: var(--blue); }
.profile-files { --profile-accent: var(--violet); }
.profile-contribution { --profile-accent: var(--amber); }
.profile-collaboration { --profile-accent: #2f8c83; }
.profile-messages { --profile-accent: #d16a62; }
.profile-growth { --profile-accent: #6f7eb8; }
.profile-settings { --profile-accent: #65777c; grid-column: 1 / -1; }
.profile-section .panel-head { align-items: flex-start; }
.profile-section .panel-head h3 { margin-top: 5px; color: var(--ink); font-size: 18px; line-height: 1.35; }
.profile-section .panel-head > button { border-color: color-mix(in srgb, var(--profile-accent) 32%, #dce5e6); background: color-mix(in srgb, var(--profile-accent) 8%, #fff); color: var(--profile-accent); font-size: 11px; font-weight: 800; }
.profile-metrics { gap: 10px; }
.profile-metrics span { min-height: 76px; align-content: center; padding: 12px; border: 1px solid color-mix(in srgb, var(--profile-accent) 16%, #e6ecec); background: color-mix(in srgb, var(--profile-accent) 7%, #fff); color: #6c7b80; }
.profile-metrics b { color: var(--profile-accent); font-size: 25px; }
.profile-list { gap: 9px; }
.profile-list button { position: relative; min-height: 72px; padding: 12px 13px 12px 18px; border-color: #e0e7e8; background: rgba(255,255,255,.9); }
.profile-list button::before { content: ""; position: absolute; left: 0; top: 12px; bottom: 12px; width: 3px; border-radius: 0 3px 3px 0; background: color-mix(in srgb, var(--profile-accent) 72%, #fff); }
.profile-list button::after { content: "→"; position: absolute; right: 13px; top: 50%; color: #9aa7ab; font-size: 13px; transform: translateY(-50%); }
.profile-list button:hover { transform: translateY(-2px); border-color: color-mix(in srgb, var(--profile-accent) 35%, #dce5e6); background: color-mix(in srgb, var(--profile-accent) 4%, #fff); box-shadow: 0 8px 16px rgba(31,55,63,.06); }
.profile-list b { padding-right: 24px; color: #273d42; font-size: 14px; }
.profile-list small { padding-right: 24px; color: #7a898e; font-size: 11px; }
.profile-settings .profile-list { grid-template-columns: repeat(4, minmax(0, 1fr)); }
.profile-settings .profile-list button { min-height: 82px; }

/* 智能检索：把表单、证据和研判组织成一套清晰的检修工作台。 */
.search-workbench { grid-template-columns: minmax(580px, 1.35fr) minmax(390px, .9fr); gap: 18px; align-items: start; }
.search-workbench > .panel { position: relative; overflow: hidden; }
.search-input-panel, .search-analysis-panel { min-height: 650px; padding: 24px; }
.search-input-panel::before, .search-analysis-panel::before, .search-results-panel::before { content: ""; position: absolute; inset: 0 0 auto; height: 4px; }
.search-input-panel::before { background: linear-gradient(90deg, var(--teal), #39a79c 58%, #82c7bd); }
.search-analysis-panel::before { background: linear-gradient(90deg, var(--blue), var(--violet)); }
.search-results-panel::before { background: linear-gradient(90deg, var(--amber), #e5b45d, var(--teal)); }
.search-panel-heading { display: grid; grid-template-columns: 42px minmax(0, 1fr); gap: 12px; align-items: start; margin-bottom: 20px; }
.search-panel-heading h3 { margin-top: 4px; color: var(--ink); font-size: 18px; }
.search-panel-heading small { display: block; margin-top: 5px; color: var(--muted); font-size: 11px; line-height: 1.55; }
.search-step { width: 42px; height: 42px; display: grid; place-items: center; border-radius: 13px; background: linear-gradient(145deg, #dff2ef, #eff9f7); color: var(--teal-dark); font-size: 12px; font-weight: 900; box-shadow: inset 0 0 0 1px #c8e2de; }
.compact-heading .search-step { background: linear-gradient(145deg, #e4eef9, #f1effa); color: var(--violet); box-shadow: inset 0 0 0 1px #d9dced; }
.search-workbench .form-grid { gap: 15px 16px; }
.search-workbench .form-grid label { gap: 7px; color: #33494e; font-size: 12px; letter-spacing: .02em; }
.search-workbench .form-grid input, .search-workbench .form-grid select, .search-workbench .form-grid textarea { border-color: #d8e2e3; background: #fbfdfd; transition: border-color .18s, background .18s, box-shadow .18s; }
.search-workbench .form-grid input, .search-workbench .form-grid select { height: 46px; padding: 0 13px; }
.search-workbench .form-grid textarea { min-height: 112px; padding: 13px; line-height: 1.65; }
.search-workbench .form-grid input:focus, .search-workbench .form-grid select:focus, .search-workbench .form-grid textarea:focus { border-color: #75aaa5; background: #fff; box-shadow: 0 0 0 3px rgba(22,118,111,.09); }
.search-upload-zone { display: grid; grid-template-columns: 46px minmax(0, 1fr) auto; align-items: center; gap: 13px; margin-top: 18px; padding: 15px 16px; border: 1px dashed #9fbfbc; background: linear-gradient(135deg, #f1f8f7, #fbfdfd); text-align: left; }
.upload-mark { width: 46px; height: 46px; display: grid; place-items: center; border-radius: 13px; background: #dcefed; color: var(--teal); }
.upload-mark .ui-icon { width: 22px; height: 22px; }
.upload-copy { display: grid; gap: 4px; min-width: 0; }
.upload-copy b { color: var(--ink); font-size: 13px; }
.upload-copy small { color: var(--muted); font-size: 10px; }
.search-upload-zone > button { border-color: #bdd4d1; background: #fff; color: var(--teal-dark); font-size: 12px; font-weight: 800; }
.search-upload-zone > button:hover { border-color: var(--teal); background: #e8f5f3; }
.search-workbench .file-pills span { display: inline-flex; align-items: center; gap: 7px; border: 1px solid #d5e5e3; background: #edf7f5; color: #34595a; }
.search-workbench .file-pills img { width: 28px; height: 28px; border-radius: 7px; object-fit: cover; }
.search-workbench .file-pills button { padding: 3px 6px; border: 0; background: transparent; color: var(--danger); font-size: 10px; }
.search-actions { margin-top: 18px; padding-top: 15px; border-top: 1px solid #e5ebec; }
.search-actions button { min-height: 44px; padding: 9px 17px; font-size: 13px; font-weight: 800; }
.search-actions .primary { min-width: 148px; box-shadow: 0 9px 18px rgba(19,91,87,.16); }
.search-analysis-panel { display: flex; flex-direction: column; background: linear-gradient(160deg, #fff 0%, #fbfcff 58%, #f4f7fb 100%); }
.search-analysis-panel.ready { background: linear-gradient(160deg, #fff 0%, #f8fbfb 100%); }
.search-analysis-panel > template + * { min-width: 0; }
.analysis-summary { margin-bottom: 14px; padding: 15px; border: 1px solid #d9e5e7; border-left: 4px solid var(--blue); border-radius: 11px; background: #fff; }
.analysis-summary span { color: var(--blue); font-size: 10px; font-weight: 900; letter-spacing: .08em; }
.analysis-summary h3 { margin-top: 6px; font-size: 17px; line-height: 1.55; }
.search-analysis-panel .analysis-grid { grid-template-columns: 1fr; margin-top: 0; }
.search-analysis-panel .analysis-grid span { border: 1px solid #e1e8ea; background: rgba(255,255,255,.82); }
.search-analysis-panel h4 { margin: 16px 0 7px; color: var(--ink); font-size: 13px; }
.search-analysis-panel ul { margin: 0; padding-left: 20px; color: #4d6268; line-height: 1.75; }
.search-analysis-panel > p { color: #4d6268; line-height: 1.7; }
.search-empty-state { flex: 1; min-height: 470px; display: grid; place-items: center; align-content: center; gap: 12px; padding: 32px; border: 1px solid #e1e7ed; border-radius: 16px; background: radial-gradient(circle at 50% 36%, rgba(63,126,178,.08), transparent 34%), rgba(255,255,255,.72); text-align: center; }
.search-empty-state h4 { margin: 4px 0 0; font-size: 17px; }
.search-empty-state p { max-width: 330px; color: var(--muted); font-size: 12px; line-height: 1.7; }
.search-empty-state ol { display: grid; grid-template-columns: repeat(3, auto); gap: 10px; margin: 6px 0 0; padding: 0; list-style: none; }
.search-empty-state li { display: flex; align-items: center; gap: 5px; padding: 7px 9px; border: 1px solid #dce5ea; border-radius: 999px; background: #fff; color: #596c72; font-size: 10px; }
.search-empty-state li b { width: 17px; height: 17px; display: grid; place-items: center; border-radius: 50%; background: #e4edf7; color: var(--blue); }
.analysis-orbit { position: relative; width: 96px; height: 96px; display: grid; place-items: center; border: 1px solid #cbdbe7; border-radius: 50%; background: rgba(255,255,255,.88); box-shadow: 0 14px 30px rgba(48,88,121,.1); }
.analysis-orbit::before { content: ""; position: absolute; inset: 12px; border: 1px dashed #b4cbdc; border-radius: 50%; }
.analysis-orbit b { width: 46px; height: 46px; display: grid; place-items: center; z-index: 1; border-radius: 15px; background: linear-gradient(145deg, var(--blue), var(--violet)); color: #fff; font-size: 15px; }
.analysis-orbit i { position: absolute; width: 8px; height: 8px; border-radius: 50%; background: var(--teal); box-shadow: 0 0 0 4px #dff0ee; }
.analysis-orbit i:nth-child(1) { top: 10px; left: 44px; }
.analysis-orbit i:nth-child(2) { right: 8px; bottom: 24px; background: var(--amber); box-shadow: 0 0 0 4px #f9ead4; }
.analysis-orbit i:nth-child(3) { left: 8px; bottom: 24px; background: var(--violet); box-shadow: 0 0 0 4px #ece7f6; }
.search-results-panel { margin-top: 2px; padding: 22px 24px; background: linear-gradient(180deg, #fff, #fbfcfc); }
.search-results-panel .panel-head { align-items: flex-end; }
.search-results-panel .panel-head h3 { margin-top: 5px; color: var(--ink); font-size: 18px; }
.search-results-panel .tabs { justify-content: flex-end; }
.search-results-panel .tabs button { min-height: 36px; border-color: #dbe3e4; background: #fff; color: #4a5d62; font-size: 11px; }
.search-results-panel .tabs button.active { border-color: var(--teal-dark); background: var(--teal-dark); color: #fff; }
.search-results-panel .result-grid { margin-top: 18px; }
.search-results-panel .result-card { border-color: #dfe7e8; background: #fff; box-shadow: 0 7px 18px rgba(31,55,63,.045); }
.search-results-panel .result-card:hover { transform: translateY(-2px); border-color: #b6cecc; box-shadow: 0 12px 24px rgba(31,55,63,.08); }

/* 主工作区与智能体面板可调宽度，五个一级页面共用。 */
.content-shell { grid-template-columns: minmax(0, 1fr) 10px var(--operator-width, 360px); }
.panel-resizer { position: relative; z-index: 4; width: 10px; min-width: 10px; height: 100%; padding: 0; border: 0; border-radius: 0; background: #e6edef; cursor: col-resize; touch-action: none; }
.panel-resizer::before { content: ""; position: absolute; inset: 0 -5px; }
.panel-resizer span { position: absolute; left: 3px; top: 50%; width: 4px; height: 54px; border-radius: 999px; background: #9bb1b5; transform: translateY(-50%); transition: height .18s, background .18s; }
.panel-resizer:hover span, :global(body.resizing-panel) .panel-resizer span { height: 90px; background: var(--teal); }
:global(body.resizing-panel) { cursor: col-resize; user-select: none; }
.operator-panel { min-width: 300px; max-width: 520px; overflow: hidden; background: linear-gradient(180deg, #f4f8f8 0%, #edf3f3 100%); }
.operator-head { grid-template-columns: 64px minmax(0, 1fr) auto; align-items: start; }
.operator-head-actions { display: grid; justify-items: end; gap: 8px; }
.panel-size-actions { display: flex; gap: 4px; }
.panel-size-actions button { width: 28px; height: 28px; padding: 0; border: 1px solid #cad8da; border-radius: 8px; background: #fff; color: var(--teal-dark); font-size: 18px; line-height: 1; }
.panel-size-actions button:hover { border-color: var(--teal); background: #eaf5f4; }
.operator-duty { color: #3f555a; font-size: 14px; line-height: 1.72; }
.operator-slogan { border: 1px solid #d7e5e5; border-left: 4px solid var(--teal); color: #244146; font-size: 14px; line-height: 1.55; box-shadow: 0 5px 14px rgba(28, 74, 78, .045); }
.chat-thread { gap: 13px; padding: 3px 6px 6px 1px; scrollbar-color: #9db0b3 transparent; }
.bubble { max-width: 92%; padding: 13px 15px; border: 1px solid #dce7e8; border-radius: 16px 16px 16px 5px; color: #1e3439; background: #fff; font-size: 14.5px; font-weight: 500; line-height: 1.72; white-space: pre-wrap; box-shadow: 0 6px 15px rgba(28, 62, 68, .055); }
.bubble.user { border-color: var(--teal-dark); border-radius: 16px 16px 5px 16px; background: var(--teal-dark); color: #fff; }
.quick-card { background: #fff; box-shadow: 0 5px 14px rgba(28, 62, 68, .04); }
.operator-chips button { border-color: #cedbdc; color: #27464a; font-size: 12.5px; }
.assistant-input-tools { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px; }
.assistant-input-tools button { min-height: 40px; display: flex; align-items: center; justify-content: center; gap: 7px; padding: 8px 10px; border: 1px solid #c9dadb; border-radius: 11px; background: #fff; color: #29565a; font-size: 12.5px; font-weight: 800; }
.assistant-input-tools button:hover, .assistant-input-tools button.active { border-color: var(--teal); background: #e6f4f2; color: var(--teal-dark); }
.assistant-input-tools .ui-icon { width: 18px; height: 18px; }
.ask-box { grid-template-columns: minmax(0, 1fr) 42px; align-items: center; min-height: 58px; padding: 8px 8px 8px 14px; border: 1px solid #97b6b5; border-radius: 15px; box-shadow: 0 7px 18px rgba(28, 62, 68, .055); }
.ask-box input { height: 40px; color: #1d3438; font-size: 14px; }
.ask-box input::placeholder { color: #7d9094; opacity: 1; }
.ask-box button { width: 42px; height: 42px; display: grid; place-items: center; border-radius: 12px; }
.ask-box button .ui-icon { width: 19px; height: 19px; }
.assistant-attachments { max-height: 126px; overflow: auto; }
.assistant-attachments span { min-height: 38px; background: #fff; border: 1px solid #d7e5e5; color: #314d51; }
.assistant-attachments span img { width: 30px; height: 30px; border-radius: 7px; object-fit: cover; }
.assistant-attachments span i { padding: 2px 5px; border-radius: 5px; background: #e6f3f2; color: var(--teal); font-size: 9px; font-style: normal; font-weight: 900; }

/* 登录与注册：独立门禁页面，不依赖业务接口，避免影响现有服务连接。 */
.app-shell.auth-shell { display: block; min-width: 0; background: #f3f7f7; }
.auth-gate { min-height: 100vh; display: grid; grid-template-columns: minmax(520px, 1.08fr) minmax(460px, .92fr); background: #f5f8f8; }
.auth-visual { position: relative; min-height: 100vh; overflow: hidden; display: flex; flex-direction: column; justify-content: space-between; padding: 52px 64px 44px; background: linear-gradient(145deg, #0d4d4b 0%, #126c66 50%, #1b8278 100%); color: #fff; }
.auth-visual::before { content: ""; position: absolute; width: 540px; height: 540px; right: -170px; bottom: -170px; border: 1px solid rgba(255,255,255,.2); border-radius: 50%; box-shadow: 0 0 0 72px rgba(255,255,255,.035), 0 0 0 144px rgba(255,255,255,.025); }
.auth-grid { position: absolute; inset: 0; opacity: .2; background-image: linear-gradient(rgba(255,255,255,.18) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,.18) 1px, transparent 1px); background-size: 52px 52px; mask-image: linear-gradient(135deg, #000, transparent 78%); }
.auth-brand, .auth-intro, .auth-footnote { position: relative; z-index: 1; }
.auth-brand { display: flex; align-items: center; gap: 18px; font-size: 14px; letter-spacing: .08em; }
.auth-brand img { width: 170px; height: 72px; padding: 6px 10px; object-fit: contain; border-radius: 14px; background: rgba(255,255,255,.94); }
.auth-intro { max-width: 650px; margin: auto 0; }
.auth-intro > p { margin-bottom: 18px; color: #bce7e1; font-size: 14px; font-weight: 800; letter-spacing: .12em; }
.auth-intro h1 { margin: 0; color: #fff; font-size: clamp(42px, 4vw, 68px); line-height: 1.24; letter-spacing: -.04em; }
.auth-capabilities { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; margin-top: 48px; }
.auth-capabilities span { display: grid; gap: 10px; padding: 18px; border: 1px solid rgba(255,255,255,.18); border-radius: 14px; background: rgba(255,255,255,.08); backdrop-filter: blur(8px); font-size: 13px; }
.auth-capabilities b { color: #9fe0d8; font-size: 11px; letter-spacing: .12em; }
.auth-footnote { color: rgba(255,255,255,.65); font-size: 12px; }
.auth-form-side { display: grid; place-items: center; padding: 48px; background: radial-gradient(circle at 85% 12%, rgba(26,130,120,.1), transparent 28%), #f5f8f8; }
.auth-card { width: min(460px, 100%); display: grid; gap: 22px; padding: 38px; border: 1px solid #d8e4e4; border-radius: 24px; background: rgba(255,255,255,.94); box-shadow: 0 28px 70px rgba(30,68,72,.13); }
.auth-card-head p { color: var(--teal); font-size: 13px; font-weight: 900; letter-spacing: .1em; }
.auth-card-head h2 { margin: 8px 0; color: #17363a; font-size: 28px; }
.auth-card-head span { color: #71858a; font-size: 13px; }
.auth-tabs { display: grid; grid-template-columns: 1fr 1fr; padding: 4px; border-radius: 12px; background: #edf3f3; }
.auth-tabs button { min-height: 42px; border: 0; background: transparent; color: #6e8286; font-weight: 800; }
.auth-tabs button.active { background: #fff; color: var(--teal-dark); box-shadow: 0 5px 14px rgba(35,74,78,.09); }
.auth-fields { display: grid; gap: 15px; }
.auth-fields label { display: grid; gap: 7px; color: #344d52; font-size: 12px; font-weight: 800; }
.auth-fields input { width: 100%; height: 48px; padding: 0 14px; border: 1px solid #d4e0e1; border-radius: 11px; outline: 0; color: #18363a; background: #fbfdfd; }
.auth-fields input:focus { border-color: #6ca9a3; box-shadow: 0 0 0 3px rgba(22,118,111,.1); background: #fff; }
.remember-row { display: flex; align-items: center; gap: 8px; color: #647a7f; font-size: 12px; }
.remember-row input { accent-color: var(--teal); }
.auth-error, .form-error { padding: 10px 12px; border: 1px solid #f0c7c0; border-radius: 9px; background: #fff4f2; color: #a84437; font-size: 12px; }
.auth-submit { min-height: 50px; border: 0; border-radius: 12px; background: linear-gradient(135deg, #125f5b, #178178); color: #fff; font-weight: 900; box-shadow: 0 10px 22px rgba(18,95,91,.2); }
.auth-submit:hover { transform: translateY(-1px); box-shadow: 0 14px 26px rgba(18,95,91,.25); }
.demo-account { display: grid; grid-template-columns: 1fr auto; gap: 6px 14px; padding: 13px 15px; border: 1px dashed #c9d9d9; border-radius: 11px; background: #f3f8f7; color: #496267; font-size: 11px; }
.demo-account span { grid-column: 1 / -1; color: var(--teal); font-weight: 900; }
.demo-account b { font-weight: 700; }

/* 个人资料编辑。 */
.profile-editor-card { width: min(780px, 94vw); overflow: hidden; padding: 0; border: 1px solid #d4e2e2; background: #fff; }
.profile-editor-head { display: grid; grid-template-columns: 72px minmax(0, 1fr); gap: 16px; align-items: center; padding: 26px 30px; background: linear-gradient(135deg, #e7f4f2, #f7faf9 65%, #eef2f8); }
.profile-editor-head img { width: 72px; height: 72px; border: 4px solid #fff; border-radius: 50%; object-fit: cover; box-shadow: 0 8px 20px rgba(31,75,79,.13); }
.profile-editor-head h2 { margin: 5px 0; color: #18383c; font-size: 24px; }
.profile-editor-head span { color: #708388; font-size: 12px; }
.profile-editor-grid { padding: 26px 30px 8px; gap: 16px; }
.profile-editor-grid label { color: #385055; font-size: 12px; font-weight: 800; }
.profile-editor-grid input, .profile-editor-grid select, .profile-editor-grid textarea { border-color: #d7e2e3; background: #fbfdfd; }
.profile-editor-grid textarea { min-height: 92px; }
.profile-editor-card .form-error { margin: 0 30px; }
.profile-editor-actions { display: flex; justify-content: flex-end; gap: 10px; padding: 18px 30px 24px; }
.profile-editor-actions button { min-width: 104px; }

/* 智能体使用记录：用角色色和信息层级替代重复的平铺框。 */
.agent-history-panel { position: relative; overflow: hidden; padding: 24px; border-color: #d7e4e4; background: linear-gradient(150deg, #fff 0%, #f8fbfb 100%); }
.agent-history-panel::before { content: ""; position: absolute; inset: 0 0 auto; height: 4px; background: linear-gradient(90deg, var(--teal), var(--blue), var(--violet), var(--amber)); }
.agent-history-panel .panel-head h3 { margin-top: 5px; color: #203c41; font-size: 21px; }
.agent-history { grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; margin-top: 6px; }
.agent-history article { --agent-color: #16766f; position: relative; min-height: 142px; grid-template-columns: 58px minmax(0, 1fr); grid-template-rows: 1fr auto; align-items: start; gap: 12px 14px; padding: 18px; overflow: hidden; border-color: color-mix(in srgb, var(--agent-color) 22%, #dce5e6); border-radius: 16px; background: linear-gradient(145deg, color-mix(in srgb, var(--agent-color) 7%, #fff), #fff 72%); box-shadow: 0 8px 20px rgba(31,55,63,.055); }
.agent-history article:nth-child(2), .agent-history article:nth-child(5) { --agent-color: #387bb4; }
.agent-history article:nth-child(3), .agent-history article:nth-child(6) { --agent-color: #8a66b4; }
.agent-history article:nth-child(4) { --agent-color: #c27c2e; }
.agent-history article::after { content: counter(agent-card, decimal-leading-zero); counter-increment: agent-card; position: absolute; right: 14px; top: 12px; color: color-mix(in srgb, var(--agent-color) 18%, transparent); font-size: 30px; font-weight: 900; }
.agent-history { counter-reset: agent-card; }
.agent-history-avatar { position: relative; grid-row: 1 / span 2; }
.agent-history-avatar img { width: 58px; height: 58px; border: 3px solid #fff; box-shadow: 0 7px 16px rgba(31,55,63,.12); }
.agent-history-avatar i { position: absolute; right: 1px; bottom: 2px; width: 12px; height: 12px; border: 2px solid #fff; border-radius: 50%; background: #35a772; }
.agent-history-copy { min-width: 0; display: grid; gap: 4px; padding-right: 22px; }
.agent-history-copy > span { color: var(--agent-color); font-size: 10px; font-weight: 900; letter-spacing: .08em; }
.agent-history-copy b { color: #20373c; font-size: 15px; line-height: 1.35; }
.agent-history-copy small { margin: 2px 0 0; overflow: visible; color: #6e8085; font-size: 11px; line-height: 1.55; }
.agent-history article > button { grid-column: 2; display: flex; align-items: center; justify-content: space-between; min-height: 34px; padding: 7px 10px; border-color: color-mix(in srgb, var(--agent-color) 25%, #dce5e6); background: #fff; color: var(--agent-color); font-size: 11px; font-weight: 800; }
.agent-history article > button i { font-style: normal; }
.agent-history article:hover { transform: translateY(-2px); box-shadow: 0 13px 25px rgba(31,55,63,.09); }

/* 技术资料库：清晰呈现资料属性、摘要和检索入口。 */
.knowledge-library-panel { position: relative; overflow: hidden; padding: 24px; border-top: 4px solid var(--violet); background: linear-gradient(145deg, #fff 0%, #fbfcfe 58%, #f7fbfa 100%); }
.knowledge-library-panel::after { content: ""; position: absolute; right: -70px; top: -90px; width: 230px; height: 230px; border-radius: 50%; background: radial-gradient(circle, rgba(126,91,174,.11), transparent 68%); pointer-events: none; }
.library-heading { position: relative; z-index: 1; display: flex; align-items: flex-start; justify-content: space-between; gap: 24px; margin-bottom: 18px; }
.library-heading > div { display: grid; gap: 5px; }
.library-heading h3 { color: #1d373c; font-size: 22px; }
.library-heading span { color: var(--muted); font-size: 12px; }
.library-heading > b { padding: 7px 12px; border: 1px solid #ded5eb; border-radius: 999px; background: #f5f0fa; color: #75549e; font-size: 12px; white-space: nowrap; }
.library-searchbar { position: relative; z-index: 1; display: grid; grid-template-columns: 42px minmax(0, 1fr) auto; align-items: center; gap: 0; margin-bottom: 22px; padding: 5px; border: 1px solid #d7e2e3; border-radius: 14px; background: #fff; box-shadow: 0 8px 20px rgba(31,55,63,.055); }
.library-search-icon { width: 42px; height: 42px; display: grid; place-items: center; color: #71858a; }
.library-search-icon .ui-icon { width: 20px; height: 20px; }
.library-searchbar input { min-width: 0; height: 42px; padding: 0 8px; border: 0; background: transparent; color: #233d42; outline: 0; }
.library-searchbar button { min-width: 116px; min-height: 42px; padding: 0 18px; border: 0; border-radius: 10px; background: linear-gradient(135deg, #176f69, #268d85); color: #fff; font-weight: 900; box-shadow: 0 7px 15px rgba(23,111,105,.18); }
.library-searchbar:focus-within { border-color: #8ab4b0; box-shadow: 0 0 0 3px rgba(22,118,111,.09), 0 9px 22px rgba(31,55,63,.06); }
.library-result-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }
.library-result-card { --card-accent: var(--violet); position: relative; min-height: 330px; grid-template-rows: auto auto auto 1fr auto auto; gap: 12px; padding: 20px; overflow: hidden; border-color: #dce5e6; border-radius: 15px; background: rgba(255,255,255,.94); box-shadow: 0 8px 24px rgba(31,55,63,.055); transition: transform .2s, border-color .2s, box-shadow .2s; }
.library-result-card:nth-child(4n + 2) { --card-accent: var(--blue); }
.library-result-card:nth-child(4n + 3) { --card-accent: var(--amber); }
.library-result-card:nth-child(4n + 4) { --card-accent: var(--teal); }
.library-result-card::before { content: ""; position: absolute; inset: 0 auto 0 0; width: 4px; background: var(--card-accent); }
.library-result-card:hover { transform: translateY(-3px); border-color: color-mix(in srgb, var(--card-accent) 35%, #dce5e6); box-shadow: 0 15px 30px rgba(31,55,63,.09); }
.library-card-head { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
.library-type { padding: 5px 9px; border-radius: 7px; background: color-mix(in srgb, var(--card-accent) 11%, #fff); color: color-mix(in srgb, var(--card-accent) 82%, #263c42); font-size: 11px; font-weight: 900; }
.library-match { color: var(--teal); font-size: 11px; font-weight: 900; }
.library-result-card h4 { color: #21393e; font-size: 18px; line-height: 1.45; }
.library-meta { display: flex; flex-wrap: wrap; gap: 6px; min-height: 25px; }
.library-meta span { padding: 4px 8px; border: 1px solid #dde6e7; border-radius: 999px; background: #f7faf9; color: #64787d; font-size: 10px; }
.library-summary { display: grid; align-content: start; gap: 8px; padding: 13px 14px; border-radius: 11px; background: #f6f8f8; }
.library-summary p { position: relative; padding-left: 13px; color: #43585d; font-size: 13px; line-height: 1.7; }
.library-summary p::before { content: ""; position: absolute; left: 0; top: .72em; width: 5px; height: 5px; border-radius: 50%; background: var(--card-accent); }
.library-tags { gap: 6px; }
.library-tags span { background: color-mix(in srgb, var(--card-accent) 8%, #f4f7f7); color: #586b70; }
.library-card-footer { display: flex; align-items: flex-end; justify-content: space-between; gap: 14px; padding-top: 13px; border-top: 1px solid #e5ebec; }
.library-card-footer > small { color: #849297; font-size: 10px; }
.library-card-footer .card-actions { flex-wrap: nowrap; margin: 0; }
.library-card-footer .card-actions button { min-height: 36px; padding: 7px 13px; border-radius: 9px; font-size: 12px; font-weight: 800; white-space: nowrap; }
.library-card-footer .card-actions .primary { border-color: var(--teal); background: var(--teal); color: #fff; }
.library-empty { min-height: 260px; display: grid; place-content: center; gap: 8px; text-align: center; border: 1px dashed #cad8d9; border-radius: 14px; background: #f8fbfa; color: #708287; }
.library-empty b { color: #2d484d; font-size: 17px; }
.library-empty span { font-size: 12px; }

/* 任务操作：用轻量双层信息按钮替代突兀的竖排文字。 */
.task-row-actions { justify-content: flex-start; gap: 7px; }
.task-row-action { min-width: 58px; min-height: 48px; display: grid; place-content: center; gap: 1px; padding: 6px 10px; border: 1px solid #d5e2e1; border-radius: 11px; background: #fff; color: #466065; box-shadow: 0 4px 12px rgba(31,69,75,.04); line-height: 1.05; transition: transform .18s, border-color .18s, box-shadow .18s; }
.task-row-action span { color: #89999c; font-size: 9px; font-weight: 700; }
.task-row-action b { color: inherit; font-size: 11px; }
.task-row-action.detail { border-color: #d5e4e2; color: #176e68; background: linear-gradient(150deg, #fff, #f4fbfa); }
.task-row-action.flow { border-color: #e7dcc9; color: #96601c; background: linear-gradient(150deg, #fff, #fff9ef); }
.task-row-action:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 8px 16px rgba(31,69,75,.09); }
.task-row-action:disabled { opacity: .42; cursor: not-allowed; }

/* 协作通信：附件、语音与人员信息保持清晰层级。 */
.conversation-list img, .message > img, .collab-info > img { background: #e9f3f1; border: 2px solid rgba(255,255,255,.92); box-shadow: 0 4px 12px rgba(25,78,75,.12); }
.chat-compose button { min-height: 38px; padding: 7px 11px; border-color: #d5e2e1; border-radius: 10px; background: #f7fbfa; color: #36575b; font-weight: 800; }
.chat-compose button.recording, .collab-actions button.recording { border-color: #e6a19c; background: #fff0ef; color: #b3443d; animation: recordingPulse 1.2s infinite; }
@keyframes recordingPulse { 50% { box-shadow: 0 0 0 5px rgba(194,70,62,.08); } }
.message .chat-image { width: min(260px, 100%); max-height: 210px; display: block; margin: 6px 0; border-radius: 12px; object-fit: cover; cursor: zoom-in; }
.message .chat-file { min-width: 230px; display: grid; gap: 3px; padding: 11px 13px; border: 1px solid #d4e3e1; border-radius: 11px; background: #fff; text-align: left; }
.message audio { width: 250px; max-width: 100%; height: 38px; margin-top: 6px; }
.collab-actions button { min-height: 46px; padding: 9px; border-radius: 11px; background: rgba(255,255,255,.86); font-weight: 800; }

.task-picker-card { width: min(680px, 94vw); }
.task-picker-list { display: grid; gap: 9px; max-height: 56vh; overflow: auto; }
.task-picker-list > button { display: grid; grid-template-columns: minmax(0,1fr) auto 52px; align-items: center; gap: 12px; min-height: 72px; padding: 13px 15px; border-color: #dce6e5; border-radius: 12px; background: #fbfdfd; text-align: left; }
.task-picker-list > button span { display: grid; gap: 4px; }
.task-picker-list > button small { color: #718387; }
.task-picker-list > button strong { color: var(--teal-dark); text-align: right; }

.task-report-card { width: min(820px, 95vw); max-height: 88vh; overflow: auto; }
.task-report-card > header { display: flex; justify-content: space-between; gap: 20px; padding: 4px 44px 16px 0; border-bottom: 1px solid #dce6e5; }
.task-report-card header small { display: block; margin-top: 5px; color: #718387; }
.report-summary, .knowledge-detail-meta { display: grid; grid-template-columns: repeat(4, minmax(0,1fr)); gap: 9px; }
.report-summary span, .knowledge-detail-meta span { display: grid; gap: 4px; padding: 12px; border-radius: 10px; background: #f3f8f7; }
.report-summary small, .knowledge-detail-meta small { color: #7a8b8f; font-size: 10px; }
.task-report-card section { padding: 15px; border: 1px solid #e0e7e6; border-radius: 12px; background: #fff; }
.task-report-card section h3 { margin-bottom: 9px; color: #1d4f50; }
.task-report-card ol { display: grid; gap: 7px; padding: 0; list-style: none; }
.task-report-card li { display: flex; justify-content: space-between; gap: 15px; padding: 9px 11px; border-radius: 8px; background: #f6f8f8; }
.task-report-card li span { color: #6c7d80; }

.knowledge-detail-card { width: min(760px, 94vw); gap: 16px; }
.knowledge-detail-card > header { display: flex; align-items: flex-start; justify-content: space-between; gap: 18px; padding-right: 40px; }
.knowledge-detail-card > header > span { padding: 6px 10px; border-radius: 999px; background: #eee8f6; color: #72539a; font-size: 11px; font-weight: 900; }
.knowledge-detail-card section { padding: 16px 18px; border-left: 4px solid var(--violet); border-radius: 11px; background: #f7f7fa; }
.knowledge-detail-card section h3 { margin-bottom: 9px; }
.knowledge-detail-card section ul { display: grid; gap: 7px; padding-left: 18px; color: #40565a; line-height: 1.7; }

/* 图谱降噪：保留可拖拽与筛选，但减少重复节点和标签碰撞。 */
.map-canvas { background-color: #f8fbfb; background-image: linear-gradient(rgba(91,132,142,.075) 1px, transparent 1px), linear-gradient(90deg, rgba(91,132,142,.075) 1px, transparent 1px), radial-gradient(circle at 50% 50%, rgba(31,120,115,.07), transparent 48%); }
.graph-node b { max-width: 132px; padding: 4px 8px; border: 1px solid rgba(214,226,226,.8); color: #30464b; font-weight: 800; }
.graph-node.center b { padding: 5px 12px; color: #174f55; }
.map-inspector { border-top: 4px solid var(--teal); background: linear-gradient(180deg, #fffdfa, #f8fbfa); }

@media print {
  body * { visibility: hidden !important; }
  .task-report-card, .task-report-card * { visibility: visible !important; }
  .task-report-card { position: fixed; inset: 0; width: 100%; max-height: none; box-shadow: none; }
  .task-report-card .close, .task-report-card .actions { display: none !important; }
}

@media (max-width: 1160px) {
  .topbar { grid-template-columns: minmax(180px, 1fr) 280px 38px auto auto; }
  .work-strip { display: none; }
  .span-8, .span-7, .span-6, .span-5, .span-4 { grid-column: 1 / -1; }
  .two-column { grid-template-columns: 1fr; }
  .content-shell { height: auto; grid-template-columns: 1fr; }
  .panel-resizer { display: none; }
  .page-scroll { height: auto; }
  .operator-panel { min-height: 420px; border-left: 0; border-top: 1px solid #ddd8d3; }
}
@media (max-width: 980px) {
  .topbar { grid-template-columns: minmax(180px, 1fr) minmax(220px, 1fr) 38px auto; }
  .user-chip { display: none; }
  .topbar-logout span { display: none; }
  .topbar-logout { width: 38px; padding: 0; }
}
@media (max-width: 1450px) {
  .health-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); }
  .execution-summary { grid-template-columns: 64px minmax(0, 1fr) 94px; }
  .execution-summary .summary-metric:last-child { display: none; }
  .home-task-panel, .quick-panel { grid-column: 1 / -1; }
  .home-quick-grid { grid-template-columns: repeat(4, minmax(0, 1fr)); }
}
@media (max-width: 1250px) {
  .home-quick-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .home-task-row { grid-template-columns: minmax(180px, 1.35fr) 100px 100px minmax(120px, .8fr) 18px; gap: 9px; }
}
@media (max-width: 1300px) {
  .topbar { grid-template-columns: minmax(180px, 1fr) minmax(220px, 320px) 38px auto; }
  .topbar .work-strip, .topbar .user-chip { display: none; }
  .library-result-grid { grid-template-columns: 1fr; }
  .recheck-panel .recheck-grid { grid-template-columns: 1fr; }
}
</style>
<style scoped src="./src/styles/yixiu-refinement.css"></style>
