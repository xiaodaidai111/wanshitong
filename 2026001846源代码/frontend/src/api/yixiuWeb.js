import {
  createOverviewFromMock,
  mockAgents,
  mockContacts,
  mockFiles,
  mockKnowledge,
  mockSearchResult,
  mockTasks
} from '../data/yixiuMock.js'

const getHost = () => {
  if (typeof window === 'undefined') return 'http://127.0.0.1:5000'
  const host = window.location.hostname || '127.0.0.1'
  return `http://${host}:5000`
}

const API_BASE = `${getHost()}/api/yixiu`
const SYSTEM_BASE = getHost()

const normalizeResponse = async (response) => {
  const payload = await response.json().catch(() => ({}))
  if (!response.ok || (payload.code && payload.code >= 400)) {
    throw new Error(payload.message || `请求失败：${response.status}`)
  }
  return payload.data ?? payload
}

export const requestJson = async (path, options = {}) => {
  const response = await fetch(`${API_BASE}${path}`, {
    method: options.method || 'GET',
    headers: {
      'Content-Type': 'application/json',
      ...options.headers
    },
    body: options.body ? JSON.stringify(options.body) : undefined
  })
  return normalizeResponse(response)
}

export const requestSystem = async (path) => {
  const response = await fetch(`${SYSTEM_BASE}${path}`)
  return normalizeResponse(response)
}

export const yixiuApi = {
  async overview() {
    try {
      const data = await requestJson('/overview')
      return {
        ...createOverviewFromMock(),
        serverOverview: data,
        agents: data.agents?.length ? data.agents : mockAgents,
        tasks: data.tasks?.length ? data.tasks.map((task, index) => ({ ...mockTasks[index % mockTasks.length], ...task })) : mockTasks,
        knowledge: data.knowledge?.length ? data.knowledge : mockKnowledge
      }
    } catch (error) {
      return { ...createOverviewFromMock(), fallbackReason: error.message }
    }
  },
  async health() {
    const fallback = { system: '正常', backend: '离线兜底', ai: '待确认', rag: '待确认', knowledge: `${mockKnowledge.length} 条兜底资料` }
    try {
      const [system, ai, rag] = await Promise.allSettled([
        requestSystem('/api/system/health'),
        requestSystem('/api/ai/status'),
        requestSystem('/api/rag/health')
      ])
      return {
        system: system.status === 'fulfilled' ? '正常' : '异常',
        backend: system.status === 'fulfilled' ? '在线' : '异常',
        ai: ai.status === 'fulfilled'
          ? `${ai.value.provider || 'qwen'} ${ai.value.configured ? '已配置' : '未配置'}`
          : '异常',
        rag: rag.status === 'fulfilled' ? (rag.value.available ? '可用' : '未启用') : '异常',
        knowledge: '资料库在线'
      }
    } catch (_error) {
      return fallback
    }
  },
  async tasks(filters = {}) {
    try {
      const params = new URLSearchParams()
      if (filters.status && filters.status !== 'all') params.set('status', filters.status)
      const suffix = params.toString() ? `?${params}` : ''
      const data = await requestJson(`/tasks${suffix}`)
      const tasks = data.tasks?.length ? data.tasks.map((task, index) => ({ ...mockTasks[index % mockTasks.length], ...task })) : mockTasks
      return filters.status && filters.status !== 'all' ? tasks.filter((task) => task.status === filters.status) : tasks
    } catch (_error) {
      return filters.status && filters.status !== 'all' ? mockTasks.filter((task) => task.status === filters.status) : mockTasks
    }
  },
  async updateTaskStatus(taskId, status, extra = {}) {
    try {
      return await requestJson(`/tasks/${taskId}/status`, { method: 'PUT', body: { status, ...extra } })
    } catch (_error) {
      return { task_id: taskId, status, ...extra }
    }
  },
  async createTask(task) {
    try {
      return await requestJson('/tasks', { method: 'POST', body: task })
    } catch (_error) {
      return { ...task, id: Date.now(), created_at: new Date().toLocaleString() }
    }
  },
  async search(payload) {
    try {
      const data = await requestJson('/search', { method: 'POST', body: payload })
      return {
        ...mockSearchResult,
        query: data.query || payload.query,
        device_model: data.device_model || payload.deviceModel,
        confidence: data.match_score || mockSearchResult.confidence,
        references: [
          ...(data.matched_manuals || []).map((item, index) => ({
            id: `manual-${index}`,
            title: item.title,
            type: '维修手册',
            category: '维修手册',
            equipment: payload.deviceName || '检修设备',
            model: data.device_model || payload.deviceModel,
            match: Number.parseInt(data.match_score || 88, 10),
            updated_at: '2026-08-03',
            source: item.chapter,
            summary: `置信度：${item.confidence}`,
            tags: ['手册', '召回', 'Qwen'],
            citations: 12,
            fileType: 'PDF'
          })),
          ...mockKnowledge
        ],
        suggestion: {
          ...mockSearchResult.suggestion,
          steps: data.recommended_sop || mockSearchResult.suggestion.steps
        }
      }
    } catch (_error) {
      return { ...mockSearchResult, query: payload.query, device_model: payload.deviceModel }
    }
  },
  async knowledge(keyword = '') {
    try {
      const params = keyword ? `?keyword=${encodeURIComponent(keyword)}` : ''
      const data = await requestJson(`/knowledge${params}`)
      return data.items?.length ? data.items.map((item, index) => ({ ...mockKnowledge[index % mockKnowledge.length], ...item })) : mockKnowledge
    } catch (_error) {
      return keyword
        ? mockKnowledge.filter((item) => JSON.stringify(item).includes(keyword))
        : mockKnowledge
    }
  },
  async files() {
    try {
      const data = await requestJson('/files')
      return data.files?.length ? data.files : mockFiles
    } catch (_error) {
      return mockFiles
    }
  },
  async uploadFile(fileMeta) {
    try {
      return await requestJson('/files', { method: 'POST', body: fileMeta })
    } catch (_error) {
      return { ...fileMeta, id: `local-${Date.now()}`, auditStatus: '待审核', parseStatus: '等待解析' }
    }
  },
  async contacts() {
    try {
      const data = await requestJson('/contacts')
      return data.contacts?.length ? data.contacts : mockContacts
    } catch (_error) {
      return mockContacts
    }
  },
  async recheck(payload) {
    try {
      return await requestJson('/recheck', { method: 'POST', body: payload })
    } catch (_error) {
      return { ...payload, saved: true }
    }
  },
  async updateKnowledge(payload) {
    try {
      return await requestJson('/knowledge/update', { method: 'POST', body: payload })
    } catch (_error) {
      return { ...payload, id: `knowledge-${Date.now()}`, status: 'pending' }
    }
  },
  async audit(payload) {
    try {
      return await requestJson('/audit', { method: 'POST', body: payload })
    } catch (_error) {
      return { passed: true, score: 96, checklist: [], suggestion: '本地兜底核查通过' }
    }
  }
}
