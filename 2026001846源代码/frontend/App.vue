<template>
  <main class="app-shell" :class="{ collapsed: navCollapsed }">
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
        <div>
          <p class="breadcrumb">一修 / {{ currentNav.label }}</p>
          <h1>{{ currentNav.title }}</h1>
        </div>
        <label class="global-search">
          <span>
            <svg class="ui-icon" viewBox="0 0 24 24" aria-hidden="true">
              <path v-for="path in iconParts('search')" :key="path" :d="path"></path>
            </svg>
          </span>
          <input v-model="globalKeyword" placeholder="搜索工单、设备、资料、联系人" />
        </label>
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
      </header>

      <div class="content-shell">
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
            <div class="health-grid">
              <span>待接收：{{ overview.stats.pending }} 项</span>
              <span>进行中：{{ overview.stats.inProgress }} 项</span>
              <span>待复检：{{ overview.stats.review }} 项</span>
              <span>今日完成：{{ overview.stats.completed }} 项</span>
              <span>需确认：{{ overview.stats.highRisk }} 项高风险</span>
            </div>
          </div>

          <div class="agent-card span-4">
            <p class="eyebrow">智能体状态</p>
            <div v-for="agent in agents" :key="agent.id" class="agent-row">
              <img :src="agent.avatar" :alt="agent.name" @error="handleAvatarError" />
              <span :class="['dot', agent.status]"></span>
              <div>
                <b>{{ agent.name }}</b>
                <small>{{ agent.role }} · {{ agent.lastResult || agent.duty }}</small>
              </div>
            </div>
          </div>

          <button
            v-for="card in statCards"
            :key="card.key"
            class="stat-card"
            type="button"
            @click="goStat(card)"
          >
            <span>{{ card.label }}</span>
            <b>{{ card.value }}</b>
            <small>{{ card.hint }}</small>
          </button>

          <div class="panel span-8">
            <div class="panel-head">
              <div>
                <p class="eyebrow">今日任务摘要</p>
                <h3>需要处理的检修工单</h3>
              </div>
              <button class="ghost" type="button" @click="activePage = 'tasks'">进入任务</button>
            </div>
            <div class="table compact">
              <div class="tr head">
                <span>工单</span><span>设备</span><span>故障</span><span>风险</span><span>负责人</span><span>状态</span><span>进度</span>
              </div>
              <button v-for="task in visibleTodayTasks" :key="task.id" class="tr" type="button" @click="openTask(task)">
                <span>{{ task.workOrderNo }}</span>
                <span>{{ task.equipment_name }} / {{ task.equipment_no }}</span>
                <span>{{ task.fault_type }}</span>
                <span><i :class="['badge', task.severity]">{{ severityText(task.severity) }}</i></span>
                <span>{{ task.assignee_name }}</span>
                <span>{{ statusText(task.status) }}</span>
                <span>{{ task.progress }}%</span>
              </button>
            </div>
          </div>

          <div class="panel span-4">
            <p class="eyebrow">快捷入口</p>
            <div class="quick-grid">
              <button v-for="item in quickActions" :key="item.label" type="button" @click="runQuickAction(item)">{{ item.label }}</button>
            </div>
          </div>

          <div class="panel span-5">
            <p class="eyebrow">风险与异常提醒</p>
            <div class="alert-list">
              <button v-for="alert in alerts" :key="alert.title" type="button" @click="runAlert(alert)">
                <b>{{ alert.title }}</b>
                <small>{{ alert.desc }}</small>
              </button>
            </div>
          </div>

          <div class="panel span-7">
            <div class="panel-head">
              <div>
                <p class="eyebrow">数据分析</p>
                <h3>最近七天任务趋势与故障分布</h3>
              </div>
            </div>
            <div class="chart-wrap">
              <svg viewBox="0 0 700 240" aria-label="任务趋势">
                <polyline fill="none" stroke="#111110" stroke-width="3" :points="trendPoints" />
                <g v-for="(value, index) in overview.trend" :key="index">
                  <rect :x="index * 92 + 18" :y="220 - value * 8" width="36" :height="value * 8" rx="6" fill="#C5BFB9" />
                </g>
              </svg>
              <div class="distribution">
                <span v-for="item in overview.faultDistribution" :key="item.label">
                  <b :style="{ width: `${item.value}%` }"></b>{{ item.label }} {{ item.value }}%
                </span>
              </div>
            </div>
          </div>

          <div class="panel span-6">
            <p class="eyebrow">最近使用记录</p>
            <button v-for="item in overview.recent" :key="item" type="button" class="history-row">{{ item }}</button>
          </div>

          <div class="panel span-6">
            <p class="eyebrow">最近知识资料</p>
            <button v-for="item in knowledge.slice(0, 4)" :key="item.id" type="button" class="history-row" @click="openKnowledge(item)">
              {{ item.title }} · {{ item.type || item.category }}
            </button>
          </div>
        </section>

        <section v-else-if="activePage === 'search'" class="two-column">
          <div class="panel">
            <p class="eyebrow">多模态输入</p>
            <div class="form-grid">
              <label>设备名称<input v-model="searchForm.deviceName" placeholder="如：摩托车发动机总成" /></label>
              <label>设备型号<input v-model="searchForm.deviceModel" placeholder="如：CG-125" /></label>
              <label>故障代码<input v-model="searchForm.faultCode" placeholder="如：NOISE-02" /></label>
              <label>设备类别<select v-model="searchForm.category"><option>发动机</option><option>电气系统</option><option>液压系统</option><option>点火系统</option></select></label>
              <label>故障类型<select v-model="searchForm.faultType"><option>异响</option><option>过热</option><option>渗漏</option><option>点火故障</option></select></label>
              <label class="wide">故障现象<textarea v-model="searchForm.query" placeholder="描述现场现象、声音、报警、温度、图片观察结果"></textarea></label>
            </div>
            <div class="upload-zone" @dragover.prevent @drop.prevent="addDroppedFiles">
              <input ref="searchFileInput" type="file" multiple @change="addFiles($event, 'search')" />
              <button type="button" @click="$refs.searchFileInput.click()">上传现场图片 / 零部件图片 / 维修文档</button>
              <span>支持组合检索，上传文件会显示状态并可删除</span>
            </div>
            <div class="file-pills">
              <span v-for="file in searchFiles" :key="file.localId">
                {{ file.name }} · {{ file.sizeText }} · {{ file.status }}
                <button type="button" @click="removeSearchFile(file.localId)">删除</button>
              </span>
            </div>
            <div class="actions">
              <button class="primary" type="button" :disabled="loading.search" @click="runSearch">{{ loading.search ? '检索中...' : '开始智能检索' }}</button>
              <button type="button" @click="simulateVoice">语音输入故障描述</button>
            </div>
          </div>

          <div class="panel">
            <p class="eyebrow">智能分析结果</p>
            <template v-if="searchResult">
              <h3>{{ searchResult.phenomenonSummary }}</h3>
              <div class="analysis-grid">
                <span>风险等级：{{ severityText(searchResult.risk) }}</span>
                <span>置信度：{{ searchResult.confidence }}%</span>
                <span>建议：{{ searchResult.stopAdvice }}</span>
              </div>
              <h4>可能原因</h4>
              <ul><li v-for="item in searchResult.causes" :key="item">{{ item }}</li></ul>
              <h4>推荐检查位置 / 工具</h4>
              <p>{{ searchResult.positions.join('、') }}；工具：{{ searchResult.tools.join('、') }}</p>
            </template>
            <div v-else class="empty">填写故障信息后执行检索，结果会明确标注为“智能分析结果”。</div>
          </div>

          <div class="panel span-all">
            <div class="panel-head">
              <div>
                <p class="eyebrow">检索结果分类</p>
                <h3>维修手册、案例、SOP、安全规范与知识节点</h3>
              </div>
              <div class="tabs">
                <button v-for="tab in resultTabs" :key="tab" type="button" :class="{ active: resultTab === tab }" @click="resultTab = tab">{{ tab }}</button>
              </div>
            </div>
            <div class="result-grid">
              <article v-for="item in filteredResults" :key="item.id" class="result-card">
                <div>
                  <b>{{ item.title }}</b>
                  <small>{{ item.type }} · {{ item.equipment }} · {{ item.model }} · 匹配度 {{ item.match }}%</small>
                  <p>{{ item.summary }}</p>
                </div>
                <div class="tag-line"><span v-for="tag in item.tags" :key="tag">{{ tag }}</span></div>
                <div class="card-actions">
                  <button type="button" @click="openKnowledge(item)">详情</button>
                  <button type="button" @click="previewFile(files[0])">预览原文件</button>
                  <button type="button" @click="toast('已复制引用')">复制引用</button>
                  <button type="button" @click="createTaskFromSearch(item)">加入检修任务</button>
                </div>
              </article>
            </div>
          </div>

          <div class="panel span-all" v-if="searchResult">
            <p class="eyebrow">智能检修建议</p>
            <div class="sop-list">
              <span v-for="(step, index) in searchResult.suggestion.steps" :key="step"><b>{{ index + 1 }}</b>{{ step }}</span>
            </div>
            <p>引用依据：{{ searchResult.references.slice(0, 3).map((item) => item.title).join('、') }}</p>
          </div>
        </section>

        <section v-else-if="activePage === 'tasks'" class="page-grid">
          <div class="panel span-all">
            <div class="panel-head">
              <div>
                <p class="eyebrow">检修任务</p>
                <h3>今日概览 / 任务管理 / 复检评估 / 联系人</h3>
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
                  <b>近 7 天任务趋势</b>
                  <svg viewBox="0 0 260 110" aria-label="近7天任务趋势">
                    <polyline :points="taskTrendPoints" fill="none" stroke="#2f7f8f" stroke-width="4" stroke-linecap="round" />
                    <circle v-for="point in taskTrendDots" :key="point.x" :cx="point.x" :cy="point.y" r="4" fill="#2f7f8f" />
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
            <div class="panel span-7">
              <p class="eyebrow">重点任务</p>
              <div class="priority-list">
                <article v-for="task in priorityTasks" :key="task.id">
                  <div><b>{{ task.workOrderNo }} · {{ task.equipment_name }}</b><small>{{ task.equipment_no }} · {{ task.description }}</small></div>
                  <span><i :class="['badge', task.severity]">{{ severityText(task.severity) }}</i>{{ statusText(task.status) }}</span>
                  <small>负责人：{{ task.assignee_name }} / 协作：{{ task.collaborators?.join('、') || '待分配' }}</small>
                  <small>步骤：{{ task.current_step }} / 剩余：{{ remainingTime(task) }} / 进度 {{ task.progress }}%</small>
                  <button type="button" @click="openTask(task)">查看详情</button>
                </article>
              </div>
            </div>
            <div class="panel span-5">
              <p class="eyebrow">任务动态</p>
              <div class="timeline task-events"><span v-for="event in taskEvents" :key="event.id"><b>{{ event.time }}</b>{{ event.text }}</span></div>
            </div>
          </template>

          <template v-if="taskPanel === 'manage'">
            <div class="panel span-all">
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
                  <span class="inline-actions">
                    <button type="button" @click="openTask(task)">详情</button>
                    <button type="button" @click="advanceTask(task)">流转</button>
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
            <div class="panel span-all">
              <p class="eyebrow">复检评估</p>
              <div class="recheck-grid">
                <article v-for="task in recheckTasks" :key="task.id" class="result-card">
                  <b>{{ task.title }}</b>
                  <small>{{ task.equipment_name }} · {{ task.current_step }}</small>
                  <select v-model="recheckForms[task.id].result"><option>通过</option><option>限期整改</option><option>返工</option><option>不通过</option></select>
                  <textarea v-model="recheckForms[task.id].comment" placeholder="复测数据、安全检查结果、复检意见"></textarea>
                  <button class="primary" type="button" @click="saveRecheck(task)">保存复检结果</button>
                </article>
              </div>
            </div>
          </template>

          <template v-if="taskPanel === 'contacts'">
            <div class="panel span-all chat-workbench">
              <aside class="conversation-list">
                <div class="chat-search"><input v-model="contactKeyword" placeholder="搜索姓名、部门、设备专业、任务编号" /></div>
                <button v-for="session in filteredConversations" :key="session.id" type="button" :class="{ active: activeConversationId === session.id }" @click="activeConversationId = session.id">
                  <img :src="session.avatar" alt="" @error="handleAvatarError" />
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
                  <button type="button" @click="sendChatMessage('请聪明的一修总结聊天重点')">总结重点</button>
                  <button type="button" @click="sendChatMessage('发起技术支援请求')">请求支援</button>
                </header>
                <div class="chat-messages">
                  <article v-for="message in activeMessages" :key="message.id" :class="['message', message.mine ? 'mine' : 'peer']">
                    <img v-if="!message.mine" :src="activeConversation?.avatar" alt="" @error="handleAvatarError" />
                    <div>
                      <p>{{ message.text }}</p>
                      <button v-if="message.card" class="message-card" type="button" @click="openMessageCard(message.card)">
                        <b>{{ message.card.title }}</b><small>{{ message.card.desc }}</small>
                      </button>
                      <small>{{ message.time }}</small>
                    </div>
                  </article>
                </div>
                <form class="chat-compose" @submit.prevent="sendChatMessage(chatInput)">
                  <button type="button" @click="sendChatMessage('发送检修图片：现场温度记录')">图片</button>
                  <button type="button" @click="sendChatMessage('发送维修手册：配电柜过热故障检修流程')">文件</button>
                  <button type="button" @click="sendChatMessage('发送语音消息：请确认安全隔离')">语音</button>
                  <button type="button" @click="sendTaskCard">任务卡片</button>
                  <input v-model="chatInput" placeholder="输入协作消息，支持发送任务、文件、知识条目" />
                  <button class="primary" type="submit">发送</button>
                </form>
              </section>
              <aside class="collab-info">
                <img :src="activeConversation?.avatar" alt="" @error="handleAvatarError" />
                <h3>{{ activeConversation?.name }}</h3>
                <p>{{ activeConversation?.position }} · {{ activeConversation?.department }}</p>
                <div class="detail-grid">
                  <span>专业：{{ activeConversation?.specialty }}</span>
                  <span>擅长设备：{{ activeConversation?.devices?.join('、') }}</span>
                  <span>当前任务：{{ activeConversation?.currentTask }}</span>
                  <span>工作负载：{{ activeConversation?.workload }}%</span>
                </div>
                <div class="collab-actions">
                  <button type="button" @click="toast('已添加到当前任务')">添加到任务</button>
                  <button type="button" @click="sendChatMessage('请求专家支援：请协助判断故障原因')">请求专家支援</button>
                  <button type="button" @click="toast('已创建协作群')">创建协作群</button>
                  <button type="button" @click="sendTaskCard">发送任务资料</button>
                  <button type="button" @click="toast('已准备语音沟通入口')">语音沟通</button>
                </div>
              </aside>
            </div>
          </template>
        </section>

        <section v-else-if="activePage === 'knowledge'" class="page-grid">
          <div class="panel span-all">
            <div class="panel-head">
              <div>
                <p class="eyebrow">知识库</p>
                <h3>知识网络 / 文件管理 / 技术资料库 / 沉淀更新</h3>
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

          <div v-if="knowledgePanel === 'library'" class="panel span-all">
            <div class="filters">
              <input v-model="knowledgeKeyword" placeholder="搜索维修手册、案例、SOP、安全规范" @keyup.enter="loadKnowledge" />
              <button type="button" @click="loadKnowledge">检索资料库</button>
            </div>
            <div class="result-grid">
              <article v-for="item in filteredKnowledge" :key="item.id" class="result-card">
                <b>{{ item.title }}</b><small>{{ item.type || item.category }} · {{ item.equipment }} · {{ item.model }}</small>
                <p>{{ item.summary || item.content }}</p>
                <div class="tag-line"><span v-for="tag in item.tags || []" :key="tag">{{ tag }}</span></div>
                <div class="card-actions"><button type="button" @click="openKnowledge(item)">详情</button><button type="button" @click="activePage = 'search'">发起检索</button></div>
              </article>
            </div>
          </div>

          <div v-if="knowledgePanel === 'update'" class="panel span-all">
            <p class="eyebrow">沉淀更新</p>
            <div class="form-grid">
              <label>知识标题<input v-model="knowledgeForm.title" placeholder="如：发动机异响复检案例" /></label>
              <label>资料类型<select v-model="knowledgeForm.type"><option>历史故障案例</option><option>维修手册</option><option>SOP</option><option>安全规范</option></select></label>
              <label>适用设备<input v-model="knowledgeForm.equipment" /></label>
              <label>设备型号<input v-model="knowledgeForm.model" /></label>
              <label class="wide">沉淀摘要<textarea v-model="knowledgeForm.summary" placeholder="描述故障现象、原因、处理方式、复检结论和引用依据"></textarea></label>
            </div>
            <button class="primary" type="button" @click="saveKnowledge">提交知识审核</button>
          </div>
        </section>

        <section v-else class="page-grid profile-page">
          <div class="profile-hero span-all">
            <img :src="user.avatar" alt="" @error="handleAvatarError" />
            <div>
              <p class="eyebrow">个人主页</p>
              <h2>{{ user.name }}</h2>
              <p>{{ user.role }} · {{ user.department }} · 工号 YX-0824</p>
              <div class="tag-line">
                <span>发动机</span><span>电气系统</span><span>高风险作业确认</span><span>技能等级：高级</span>
              </div>
            </div>
            <button class="primary" type="button" @click="toast('已打开个人资料编辑')">编辑资料</button>
          </div>

          <article v-for="section in profileSections" :key="section.key" class="profile-section" :class="section.span">
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

          <div class="panel span-all">
            <div class="panel-head">
              <div>
                <p class="eyebrow">智能体使用记录</p>
                <h3>最近协助我的器灵</h3>
              </div>
              <button type="button" @click="runAudit">查看核查建议</button>
            </div>
            <div class="agent-history">
              <article v-for="agent in agents.slice(0, 6)" :key="agent.id">
                <img :src="agent.avatar" :alt="agent.name" @error="handleAvatarError" />
                <div>
                  <b>{{ agent.name }}</b>
                  <small>{{ agent.role }} · {{ agent.lastResult }}</small>
                </div>
                <button type="button" @click="sendOperatorPrompt(agent.role)">查看结果</button>
              </article>
            </div>
            <pre v-if="auditResult">{{ auditResult }}</pre>
          </div>
        </section>
      </section>

      <aside class="operator-panel" aria-label="页面智能体对话">
        <div class="operator-head">
          <img class="operator-avatar" :src="operatorProfile.avatar" :alt="operatorProfile.name" @error="handleAvatarError" />
          <div>
            <p class="eyebrow">智能体协助</p>
            <h2>{{ operatorProfile.name }}</h2>
            <small class="operator-role">{{ operatorProfile.role }}</small>
          </div>
          <span :class="['operator-status', operatorProfile.status]">{{ operatorProfile.statusText }}</span>
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

        <form class="ask-box" @submit.prevent="sendOperatorPrompt(operatorInput)">
          <input v-model="operatorInput" :placeholder="operatorProfile.placeholder" />
          <button type="submit">➤</button>
        </form>
      </aside>
      </div>
    </section>

    <div v-if="selectedTask" class="modal" @click.self="selectedTask = null">
      <article class="modal-card">
        <button class="close" type="button" @click="selectedTask = null">×</button>
        <p class="eyebrow">任务详情与作业执行</p>
        <h2>{{ selectedTask.title }}</h2>
        <div class="detail-grid">
          <span>工单：{{ selectedTask.workOrderNo }}</span>
          <span>设备：{{ selectedTask.equipment_name }} / {{ selectedTask.equipment_model }}</span>
          <span>风险：{{ severityText(selectedTask.severity) }}</span>
          <span>负责人：{{ selectedTask.assignee_name }}</span>
        </div>
        <p>{{ selectedTask.description }}</p>
        <h3>标准作业步骤</h3>
        <div class="sop-list">
          <span v-for="(step, index) in selectedTask.sop" :key="step"><b>{{ index + 1 }}</b>{{ step }}</span>
        </div>
        <div class="actions">
          <button type="button" @click="advanceTask(selectedTask)">开始/流转</button>
          <button type="button" @click="taskPanel = 'recheck'; activePage = 'tasks'; selectedTask = null">进入复检</button>
          <button type="button" @click="toast('已生成检修报告预览')">预览报告</button>
        </div>
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
      <article class="modal-card">
        <button class="close" type="button" @click="selectedKnowledge = null">×</button>
        <p class="eyebrow">知识详情</p>
        <h2>{{ selectedKnowledge.title }}</h2>
        <p>{{ selectedKnowledge.summary || selectedKnowledge.content }}</p>
        <div class="tag-line"><span v-for="tag in selectedKnowledge.tags || []" :key="tag">{{ tag }}</span></div>
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

    <div v-if="toastText" class="toast">{{ toastText }}</div>
  </main>
</template>

<script setup>
import { computed, nextTick, onMounted, reactive, ref } from 'vue'
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

const activePage = ref('home')
const showSplash = ref(true)
const bootScreenRef = ref(null)
const bootMarkRef = ref(null)
const bootLogoRef = ref(null)
const brandLogoRef = ref(null)
const navCollapsed = ref(false)
const globalKeyword = ref('')
const currentNav = computed(() => navItems.find((item) => item.key === activePage.value) || navItems[0])
const user = reactive({ ...mockUser })
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
const nowText = ref('')
const overview = reactive(createOverviewFromMock())
const systemStatus = reactive({ ...overview.status })
const tasks = ref([])
const knowledge = ref([])
const files = ref([])
const contacts = ref([])
const agents = ref(normalizeAgentList(overview.agents))
const loading = reactive({ search: false })
const selectedTask = ref(null)
const selectedFile = ref(null)
const selectedKnowledge = ref(null)
const toastText = ref('')
const auditResult = ref('')

const searchForm = reactive({ deviceName: '摩托车发动机总成', deviceModel: 'CG-125', faultCode: 'NOISE-02', category: '发动机', faultType: '异响', query: '启动后气门区域有明显异响，热车后略有减轻，怠速不稳。' })
const searchFiles = ref([])
const searchResult = ref(null)
const resultTab = ref('全部')
const resultTabs = ['全部', '维修手册', '历史故障案例', '标准作业流程 SOP', '安全操作规范', '推荐检修方案']

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
const knowledgeForm = reactive({ title: '', type: '历史故障案例', equipment: '', model: '', summary: '' })
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
const operatorProfile = computed(() => operatorProfiles[operatorKey.value] || operatorProfiles.home)

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
  { title: '高风险工单', desc: `${tasks.value.filter((task) => task.severity === 'high').length} 个任务需要二次确认`, action: () => goStat({ page: 'tasks', panel: 'manage', severity: 'high' }) },
  { title: '待复检任务', desc: `${tasks.value.filter((task) => task.status === 'review').length} 个任务等待复测数据`, action: () => goStat({ page: 'tasks', panel: 'recheck' }) },
  { title: '知识审核异常', desc: '1 份资料解析部分成功，请人工复核', action: () => goStat({ page: 'knowledge', panel: 'files' }) },
  { title: 'AI 服务状态', desc: systemStatus.ai, action: () => activePage.value = 'profile' }
])
const quickActions = [
  { label: '发起智能检索', action: () => activePage.value = 'search' },
  { label: '新建检修任务', action: () => { activePage.value = 'tasks'; taskPanel.value = 'manage'; showTaskForm.value = true } },
  { label: '上传维修资料', action: () => { activePage.value = 'knowledge'; knowledgePanel.value = 'files' } },
  { label: '查看高风险任务', action: () => goStat({ page: 'tasks', panel: 'manage', severity: 'high' }) },
  { label: '进入复检评估', action: () => goStat({ page: 'tasks', panel: 'recheck' }) },
  { label: '查看知识网络', action: () => goStat({ page: 'knowledge', panel: 'network' }) },
  { label: '联系现场负责人', action: () => goStat({ page: 'tasks', panel: 'contacts' }) },
  { label: '个人检修记录', action: () => activePage.value = 'profile' }
]
const trendPoints = computed(() => overview.trend.map((value, index) => `${index * 100 + 24},${220 - value * 8}`).join(' '))

const filteredResults = computed(() => {
  const list = searchResult.value?.references || []
  if (resultTab.value === '全部') return list
  return list.filter((item) => item.type === resultTab.value || item.category === resultTab.value)
})
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
  return taskTrendData.value.map((value, index) => ({ x: 18 + index * 36, y: 96 - value / max * 74 }))
})
const taskTrendPoints = computed(() => taskTrendDots.value.map((point) => `${point.x},${point.y}`).join(' '))
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
    items: ['高风险提醒：开启', '复检提醒：开启', '默认任务视图：今日概览', '文件预览：在线预览优先'].map((text) => ({ title: text, desc: '可在个人设置中调整' }))
  }
])
const recheckTasks = computed(() => tasks.value.filter((task) => ['review', 'completed'].includes(task.status) || task.progress >= 80))
const departments = computed(() => [...new Set(contacts.value.map((item) => item.department))])
const filteredContacts = computed(() => contacts.value.filter((contact) => {
  const keywordOk = !contactKeyword.value || JSON.stringify(contact).includes(contactKeyword.value)
  const deptOk = contactDepartment.value === 'all' || contact.department === contactDepartment.value
  return keywordOk && deptOk
}))
const conversations = computed(() => [
  { id: 'task-room-1', name: 'ZK-320 过热检修群', avatar: '/static/agents/heming.png', position: '任务群组', department: '动力设备检修一组', specialty: '高风险任务协作', devices: ['配电柜', 'ZK-320'], currentTask: 'ZK-320 配电柜过热检修', workload: 78, lastMessage: '已上传红外测温图片', unread: 3, taskNo: 'YX-20260803-001', risk: 'high' },
  ...contacts.value.map((contact, index) => ({
    id: index === 0 ? 'expert-1' : `contact-${contact.id}`,
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
const graphNodes = computed(() => {
  const keyword = knowledgeKeyword.value.trim()
  const rawNodes = knowledge.value.flatMap((item, index) => [
    { id: `${item.id}-equipment`, label: item.equipment || '通用设备', kind: 'equipment', source: item, level: 1 },
    { id: `${item.id}-model`, label: item.model || '通用型号', kind: 'model', source: item, level: 1 },
    { id: `${item.id}-part`, label: item.tags?.[0] || '关键部件', kind: 'part', source: item, level: 2 },
    { id: `${item.id}-fault`, label: item.tags?.[1] || item.category || item.type, kind: 'fault', source: item, level: 1 },
    { id: `${item.id}-cause`, label: item.summary?.slice(0, 8) || '故障原因', kind: 'cause', source: item, level: 2 },
    { id: `${item.id}-method`, label: item.type?.includes('安全') ? '安全检查' : '检测方法', kind: 'method', source: item, level: 2 },
    { id: `${item.id}-solution`, label: item.category || '检修方案', kind: 'solution', source: item, level: 2 },
    { id: `${item.id}-sop`, label: item.type?.includes('SOP') ? item.title : '标准步骤', kind: 'sop', source: item, level: 2 },
    { id: `${item.id}-risk`, label: item.tags?.includes('安全') ? '作业风险' : '安全风险', kind: 'risk', source: item, level: 3 },
    { id: `${item.id}-case`, label: item.type?.includes('案例') ? item.title : '历史案例', kind: 'case', source: item, level: 3 },
    { id: `${item.id}-doc`, label: item.title, kind: 'doc', source: item, level: 1 }
  ])
    .filter((node) => node.level <= graphDepth.value)
    .filter((node) => graphKindFilter.value === 'all' || node.kind === graphKindFilter.value)
    .slice(0, graphDepth.value === 1 ? 16 : graphDepth.value === 2 ? 28 : 42)

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
  contacts.value = contactData
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
  if (item.page) goStat({ page: item.page, panel: item.panel })
  else toast(item.title)
}
const sendChatMessage = (text) => {
  const value = String(text || '').trim()
  if (!value || !activeConversation.value) return
  chatMessages.value.push({ id: `msg-${Date.now()}`, conversationId: activeConversation.value.id, mine: true, text: value, time: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }) })
  chatInput.value = ''
}
const sendTaskCard = () => {
  const task = tasks.value[0]
  if (!task || !activeConversation.value) return
  chatMessages.value.push({
    id: `card-${Date.now()}`,
    conversationId: activeConversation.value.id,
    mine: true,
    text: '发送任务卡片，请协作人员查看当前进度。',
    time: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }),
    card: { type: 'task', title: task.workOrderNo, desc: `${task.equipment_name} · ${task.current_step} · ${task.progress}%` }
  })
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
  window.setTimeout(() => { toastText.value = '' }, 1800)
}
const statusClass = (value) => String(value).includes('异常') || String(value).includes('离线') ? 'bad' : 'ok'
const severityText = (value) => ({ low: '低风险', medium: '中风险', high: '高风险', critical: '严重风险' }[value] || value || '中风险')
const statusText = (value) => ({ pending: '待处理', in_progress: '检修中', review: '待复检', completed: '已完成', paused: '已暂停', rejected: '已退回', overdue: '已逾期' }[value] || value || '待处理')
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
  url: URL.createObjectURL(file),
  status: '待上传',
  parseStatus: '等待解析',
  auditStatus: '待审核',
  version: 'v1.0',
  uploaded_at: new Date().toLocaleString('zh-CN'),
  uploader: user.name
})
const addFiles = async (event, target) => {
  const selected = Array.from(event.target.files || []).map(toFileMeta)
  if (target === 'search') {
    searchFiles.value.push(...selected.map((file) => ({ ...file, status: '已加入检索' })))
  } else {
    for (const file of selected) {
      const folder = activeFolder.value === '全部文件' ? '现场图片' : activeFolder.value
      const saved = await yixiuApi.uploadFile({ ...file, category: folder, folder, uploader: user.name })
      files.value.unshift({ ...file, ...saved, id: saved.id || file.localId, url: file.url || saved.url, category: saved.category || folder, folder: saved.folder || folder, status: '上传成功', parseStatus: saved.parseStatus || '等待解析' })
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
    const saved = await yixiuApi.uploadFile({ ...file, category: folder, folder, uploader: user.name })
    files.value.unshift({ ...file, ...saved, id: saved.id || file.localId, url: file.url || saved.url, category: saved.category || folder, folder: saved.folder || folder, status: '上传成功', parseStatus: saved.parseStatus || '等待解析' })
  }
  if (selected.length) toast(`已拖入 ${selected.length} 个文件`)
}
const removeSearchFile = (localId) => {
  searchFiles.value = searchFiles.value.filter((file) => file.localId !== localId)
}
const simulateVoice = () => {
  searchForm.query = `${searchForm.query} 语音补充：设备热车后异响减轻，复测时需要记录转速和温度。`
}
const runSearch = async () => {
  loading.search = true
  try {
    searchResult.value = await yixiuApi.search({ ...searchForm, files: searchFiles.value, query: searchForm.query })
    toast('智能检索完成')
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
  tasks.value.unshift({ ...created, collaborators: [], sop: ['安全确认', '故障记录', '部件检测', '复测提交'] })
  showTaskForm.value = false
  toast('检修任务创建成功')
}
const advanceTask = async (task) => {
  const next = task.status === 'pending' ? 'in_progress' : task.status === 'in_progress' ? 'review' : task.status === 'review' ? 'completed' : 'completed'
  await yixiuApi.updateTaskStatus(task.id, next, { operator: user.name })
  task.status = next
  task.progress = next === 'in_progress' ? Math.max(task.progress, 45) : next === 'review' ? 86 : 100
  task.current_step = next === 'in_progress' ? '作业执行' : next === 'review' ? '复测确认' : '归档'
  toast(`任务已流转为：${statusText(next)}`)
}
const saveRecheck = async (task) => {
  const form = recheckForms[task.id]
  const saved = await yixiuApi.recheck({ task_id: task.id, ...form, reviewer: user.name })
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
  const saved = await yixiuApi.updateKnowledge({ ...knowledgeForm, tags: ['沉淀', '复检', '检修案例'] })
  knowledge.value.unshift(saved)
  Object.assign(knowledgeForm, { title: '', type: '历史故障案例', equipment: '', model: '', summary: '' })
  toast('知识条目已进入审核队列')
}
const runAudit = async () => {
  const result = await yixiuApi.audit({ references: true, safety_checked: true, measurements: true, retested: true, report_ready: true })
  auditResult.value = JSON.stringify(result, null, 2)
}

const runOperatorPrimary = () => {
  if (activePage.value === 'home') return toast('已生成今日检修简报')
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

const sendOperatorPrompt = (prompt) => {
  const value = String(prompt || '').trim()
  if (!value) return
  operatorInput.value = ''
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
  toast(`${operatorProfile.value.name}已收到：${value}`)
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
  updateClock()
  window.setInterval(updateClock, 1000)
  playBootAnimation()
  window.setTimeout(() => { refreshAll() }, 260)
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
.topbar { height: 72px; display: grid; grid-template-columns: minmax(190px, 1fr) 360px auto 38px auto; align-items: center; gap: 14px; padding: 0 22px; border-bottom: 1px solid #ddd8d3; background: linear-gradient(180deg, #fbfaf8, #f4f2ef); }
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
.quick-card { width: 100%; display: grid; grid-template-columns: 34px minmax(0, 1fr) auto; align-items: center; gap: 10px; padding: 12px; border: 1px solid #ddd8d3; border-radius: 14px; background: #fbfaf8; text-align: left; }
.quick-card > span { width: 34px; height: 34px; display: grid; place-items: center; border-radius: 11px; background: #111110; color: #EEECEA; }
.quick-card small { display: block; margin-top: 4px; color: #706D6D; font-size: 12px; line-height: 1.35; }
.quick-card i { font-style: normal; color: #706D6D; }
.operator-chips { display: flex; flex-wrap: wrap; gap: 8px; }
.operator-chips button { min-height: 32px; padding: 6px 10px; border-radius: 999px; background: #fbfaf8; font-size: 12px; }
.ask-box { display: grid; grid-template-columns: minmax(0, 1fr) 40px; gap: 8px; padding: 8px; border: 1px solid #111110; border-radius: 16px; background: #fbfaf8; }
.ask-box input { min-width: 0; border: 0; outline: 0; background: transparent; color: #111110; }
.ask-box button { width: 40px; height: 40px; padding: 0; border-radius: 50%; background: #111110; color: #EEECEA; }
@media (max-width: 1280px) {
  .topbar { grid-template-columns: minmax(180px, 1fr) 280px auto auto; }
  .work-strip { display: none; }
  .span-8, .span-7, .span-6, .span-5, .span-4 { grid-column: 1 / -1; }
  .two-column { grid-template-columns: 1fr; }
  .content-shell { height: auto; grid-template-columns: 1fr; }
  .page-scroll { height: auto; }
  .operator-panel { min-height: 420px; border-left: 0; border-top: 1px solid #ddd8d3; }
}
</style>
