export const mockUser = {
  name: '聪明的一修',
  avatar: '/static/avatar-1.png',
  department: '动力设备检修一组',
  role: '检修工程师'
}

export const mockAgents = [
  { id: 'tiangong', name: '天工｜综合智能中枢', avatar: '/static/agents/tiangong.png', role: '统筹调度', slogan: '百工相合，一修有序。', duty: '统筹检索、作业、知识、协作和核查智能体，汇总系统状态与风险。', status: 'online', lastResult: '完成今日任务优先级编排' },
  { id: 'guanwei', name: '观微｜智能检索 agent', avatar: '/static/agents/guanwei.png', role: '故障检索', slogan: '见微知因，循迹而寻。', duty: '发现设备故障线索，解析故障现象、型号、图片和维修文档。', status: 'online', lastResult: '完成 CG-125 异响检索，命中 6 条资料' },
  { id: 'zhiju', name: '执矩｜检修作业 agent', avatar: '/static/agents/zhiju.png', role: '作业执行', slogan: '依规而作，步步有据。', duty: '编排标准作业步骤，推进工单流转并提醒高风险安全确认。', status: 'online', lastResult: '为 ZK-320 过热工单生成 7 步作业流程' },
  { id: 'bowen', name: '博闻｜知识管理 agent', avatar: '/static/agents/bowen.png', role: '知识管理', slogan: '汇百工之识，成一修之典。', duty: '整理技术资料、维护知识网络、沉淀历史检修案例。', status: 'busy', lastResult: '3 条新资料等待沉淀审核' },
  { id: 'heming', name: '和鸣｜协作调度 agent', avatar: '/static/agents/heming.png', role: '协作调度', slogan: '同声相应，协力而行。', duty: '管理联系人、协调现场人员、发起专家支援与任务沟通。', status: 'online', lastResult: '已为高风险任务推荐安全负责人' },
  { id: 'mingjian', name: '明鉴｜复检核查 agent', avatar: '/static/agents/mingjian.png', role: '复检核查', slogan: '据实而验，明察无误。', duty: '执行复检评估、安全检查、质量核验和任务验收。', status: 'online', lastResult: '最近一次核查得分 96' }
]

export const mockTasks = [
  {
    id: 1,
    workOrderNo: 'YX-20260803-001',
    title: 'ZK-320 配电柜过热检修',
    equipment_name: '配电柜',
    equipment_no: 'PD-ZK-320-07',
    equipment_model: 'ZK-320',
    equipment_category: '电气系统',
    fault_code: 'E-001',
    fault_type: '过热',
    description: '运行温度异常升高，红外测温显示接触器区域超过 80℃。',
    severity: 'high',
    status: 'pending',
    assignee_name: '聪明的一修',
    collaborators: ['唐忆哲', '陈程'],
    current_step: '安全确认',
    progress: 18,
    due_at: '2026-08-03 18:00',
    created_at: '2026-08-03 09:30',
    image: '/static/industrial-banner-1.png',
    tools: ['红外测温仪', '万用表', '绝缘手套'],
    parts: ['接触器触点', '散热风扇'],
    safety: ['停电验电', '挂牌上锁', '二次确认'],
    sop: ['安全确认', '设备断电', '外观检查', '部件检测', '维修更换', '复测确认', '提交报告'],
    recheck: { status: 'waiting', result: '', comment: '' }
  },
  {
    id: 2,
    workOrderNo: 'YX-20260803-002',
    title: 'CG-125 发动机异响排查',
    equipment_name: '摩托车发动机总成',
    equipment_no: 'MTR-CG125-12',
    equipment_model: 'CG-125',
    equipment_category: '发动机',
    fault_code: 'NOISE-02',
    fault_type: '异响',
    description: '启动后气门区域有明显异响，热车后略有减轻。',
    severity: 'medium',
    status: 'in_progress',
    assignee_name: '王铭',
    collaborators: ['聪明的一修'],
    current_step: '部件检测',
    progress: 56,
    due_at: '2026-08-03 20:00',
    created_at: '2026-08-03 08:15',
    image: '/static/equipment.png',
    tools: ['塞尺', '扭矩扳手', '听诊器'],
    parts: ['正时链条张紧器', '气门调整垫片'],
    safety: ['停机冷却', '防误启动', '防烫伤'],
    sop: ['记录异响工况', '检查润滑状态', '测量气门间隙', '复核正时链条', '热车复测'],
    recheck: { status: 'waiting', result: '', comment: '' }
  },
  {
    id: 3,
    workOrderNo: 'YX-20260803-003',
    title: '液压千斤顶渗漏处理',
    equipment_name: '液压千斤顶',
    equipment_no: 'HY-YZ50-03',
    equipment_model: 'YZ-50T',
    equipment_category: '液压系统',
    fault_code: 'HYD-11',
    fault_type: '渗漏',
    description: '油封老化导致液压油渗漏，保压能力下降。',
    severity: 'medium',
    status: 'review',
    assignee_name: '陈程',
    collaborators: ['安全员赵宁'],
    current_step: '复测确认',
    progress: 86,
    due_at: '2026-08-04 10:00',
    created_at: '2026-08-02 14:20',
    image: '/static/industrial-banner-2.png',
    tools: ['压力表', '密封拆装工具'],
    parts: ['油封套件', '液压油'],
    safety: ['泄压操作', '防滑防污染'],
    sop: ['泄压', '拆检油封', '更换密封件', '补油排气', '保压复测'],
    recheck: { status: 'waiting', result: '', comment: '' }
  },
  {
    id: 4,
    workOrderNo: 'YX-20260802-009',
    title: '火花塞定期检查',
    equipment_name: '点火线圈',
    equipment_no: 'IGN-DLI-001',
    equipment_model: 'DLI-001',
    equipment_category: '点火系统',
    fault_code: '',
    fault_type: '定检',
    description: '按照维护计划检查火花塞间隙与绝缘状态。',
    severity: 'low',
    status: 'completed',
    assignee_name: '唐忆哲',
    collaborators: [],
    current_step: '归档',
    progress: 100,
    due_at: '2026-08-02 17:00',
    created_at: '2026-08-02 09:00',
    image: '/static/industrial-banner-3.png',
    tools: ['塞尺', '火花塞套筒'],
    parts: ['火花塞'],
    safety: ['停机冷却'],
    sop: ['拆卸', '间隙测量', '清洁或更换', '点火复测'],
    recheck: { status: 'passed', result: '通过', comment: '点火稳定' }
  }
]

export const mockKnowledge = [
  { id: 'kb-001', title: '摩托车发动机维修手册', type: '维修手册', category: '维修手册', equipment: '摩托车发动机总成', model: 'CG-125', match: 96, updated_at: '2026-07-28', source: '维修手册 PDF', summary: '覆盖点火、燃油、润滑、气门机构和异响排查。', tags: ['发动机', '异响', '手册'], citations: 89, fileType: 'PDF', status: 'approved' },
  { id: 'kb-002', title: '配电柜过热故障检修流程', type: '标准作业流程 SOP', category: 'SOP', equipment: '配电柜', model: 'ZK-320', match: 92, updated_at: '2026-07-25', source: '标准作业库', summary: '包含停电验电、红外测温、触点检查、散热检查和复测标准。', tags: ['电气', '过热', 'SOP'], citations: 78, fileType: 'DOCX', status: 'approved' },
  { id: 'kb-003', title: '液压千斤顶油封渗漏案例', type: '历史故障案例', category: '案例', equipment: '液压千斤顶', model: 'YZ-50T', match: 88, updated_at: '2026-07-19', source: '现场案例', summary: '记录油封老化、保压下降和密封件替换过程。', tags: ['液压', '渗漏', '案例'], citations: 34, fileType: 'MD', status: 'pending' },
  { id: 'kb-004', title: '检修作业安全操作规范', type: '安全操作规范', category: '安全规范', equipment: '通用设备', model: 'ALL', match: 84, updated_at: '2026-07-12', source: '安全制度', summary: '说明停电验电、挂牌上锁、二次确认和现场隔离要求。', tags: ['安全', '规范', '复检'], citations: 120, fileType: 'PDF', status: 'approved' }
]

export const mockFiles = [
  { id: 'file-001', name: '摩托车发动机维修手册.pdf', type: 'PDF', category: '维修手册', folder: '发动机资料', size: '18.2 MB', equipment: '摩托车发动机总成', model: 'CG-125', uploader: '聪明的一修', uploaded_at: '2026-07-28 10:12', updated_at: '2026-07-30 11:30', auditStatus: '已通过', parseStatus: '解析成功', version: 'v1.2', knowledgeLinks: 8, downloads: 36, url: '/static/manuals/摩托车发动机维修手册.pdf', favorite: true },
  { id: 'file-002', name: 'ZK-320 配电柜过热 SOP.docx', type: 'Word', category: '标准作业流程', folder: '电气系统', size: '864 KB', equipment: '配电柜', model: 'ZK-320', uploader: '唐忆哲', uploaded_at: '2026-07-25 16:40', updated_at: '2026-07-25 16:40', auditStatus: '审核中', parseStatus: '解析中', version: 'v1.0', knowledgeLinks: 3, downloads: 12, url: '', favorite: false },
  { id: 'file-003', name: '液压千斤顶渗漏现场图.png', type: '图片', category: '现场图片', folder: '液压系统', size: '2.4 MB', equipment: '液压千斤顶', model: 'YZ-50T', uploader: '陈程', uploaded_at: '2026-07-19 09:18', updated_at: '2026-07-19 09:18', auditStatus: '已通过', parseStatus: '部分成功', version: 'v1.0', knowledgeLinks: 1, downloads: 5, url: '/static/industrial-banner-2.png', favorite: false }
]

export const mockContacts = [
  { id: 1, name: '聪明的一修', avatar: '/static/avatar-1.png', position: '检修工程师', department: '动力设备检修一组', specialty: '发动机/电气', phone: '138-0000-1024', status: '在线', currentTask: 'ZK-320 过热检修', devices: ['CG-125', 'ZK-320'], workload: 72 },
  { id: 2, name: '唐忆哲', avatar: '/static/avatar-2.png', position: '复检人员', department: '质量复检组', specialty: '复检评估', phone: '138-0000-2048', status: '在线', currentTask: '火花塞定检复核', devices: ['DLI-001'], workload: 48 },
  { id: 3, name: '赵宁', avatar: '/static/avatar-3.png', position: '安全负责人', department: '安全管理部', specialty: '高风险作业', phone: '138-0000-4096', status: '忙碌', currentTask: '高风险作业确认', devices: ['配电柜', '液压系统'], workload: 83 }
]

export const mockOverview = {
  status: {
    system: '正常',
    backend: '在线',
    ai: '智能协助可用',
    rag: '可检索',
    knowledge: '156 条资料'
  },
  recent: [
    '检索：CG-125 发动机异响',
    '查看：配电柜过热 SOP',
    '上传：液压千斤顶现场图',
    '收藏：安全操作规范'
  ],
  trend: [9, 12, 8, 15, 18, 14, 20],
  faultDistribution: [
    { label: '过热', value: 32 },
    { label: '异响', value: 26 },
    { label: '渗漏', value: 18 },
    { label: '点火', value: 14 },
    { label: '其他', value: 10 }
  ]
}

export const mockSearchResult = {
  phenomenonSummary: '设备启动后出现异响并伴随怠速不稳，现象集中在发动机气门机构和点火系统。',
  causes: ['气门间隙异常', '正时链条张紧不足', '点火线圈接触不良', '润滑不足导致异常磨损'],
  parts: ['气门机构', '正时链条', '火花塞', '点火线圈'],
  risk: 'medium',
  confidence: 88,
  positions: ['气门室盖', '点火线圈插接件', '机油润滑回路'],
  methods: ['听诊定位', '间隙测量', '绝缘测试', '热车复测'],
  tools: ['塞尺', '万用表', '听诊器', '扭矩扳手'],
  safety: ['停机冷却后拆检', '防止误启动', '记录复测数据'],
  stopAdvice: '建议停机检查后再继续运行',
  references: mockKnowledge,
  suggestion: {
    diagnosis: '优先判断为气门间隙或正时链条张紧异常，需要结合点火系统状态复核。',
    preparation: ['确认设备编号和最近保养记录', '准备手册、工具和防护用品'],
    tools: ['塞尺', '万用表', '听诊器'],
    parts: ['气门调整垫片', '火花塞'],
    steps: ['记录异响工况', '拆检气门室盖', '测量气门间隙', '检查正时链条张紧器', '复装后热车复测'],
    risks: ['高温烫伤', '误启动', '紧固扭矩不足'],
    retest: ['怠速稳定性', '异响是否消除', '温升是否正常']
  }
}

export const createOverviewFromMock = () => {
  const pending = mockTasks.filter((task) => ['pending', 'in_progress'].includes(task.status)).length
  const review = mockTasks.filter((task) => task.status === 'review').length
  const completed = mockTasks.filter((task) => task.status === 'completed').length
  const highRisk = mockTasks.filter((task) => task.severity === 'high' || task.severity === 'critical').length
  return {
    ...mockOverview,
    stats: {
      todayNew: 3,
      pending,
      inProgress: mockTasks.filter((task) => task.status === 'in_progress').length,
      highRisk,
      review,
      completed,
      knowledgeTotal: mockKnowledge.length + 152,
      weekKnowledge: 9,
      onlineUsers: mockContacts.filter((contact) => contact.status === '在线').length
    },
    tasks: mockTasks,
    knowledge: mockKnowledge,
    files: mockFiles,
    agents: mockAgents
  }
}

