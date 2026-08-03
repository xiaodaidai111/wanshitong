const PUBLIC_API_HOST = 'http://47.95.202.36:6000'

const getDefaultApiHost = () => {
  if (typeof window !== 'undefined' && window.location?.hostname) {
    const hostname = window.location.hostname
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
      return 'http://127.0.0.1'
    }
    return `http://${hostname}`
  }

  return PUBLIC_API_HOST
}

export const API_HOST = getDefaultApiHost()

const getBackendURL = (path = '') => {
  if (API_HOST === PUBLIC_API_HOST) {
    return `${API_HOST}${path}`
  }
  return `${API_HOST}:5000${path}`
}

const DEFAULT_BACKEND_URLS = {
  tuantuan: getBackendURL(),
  takeout: getBackendURL('/takeout'),
  yixiu: getBackendURL('/api/yixiu'),
  maintenance: getBackendURL('/api/maintenance-tasks'),
  repair: getBackendURL('/api/yixiu')
}

const normalizeBaseURL = (url) => {
  if (!url) return ''
  return url.endsWith('/') ? url.slice(0, -1) : url
}

export const getBaseURL = (service = 'tuantuan') => {
  let urls = { ...DEFAULT_BACKEND_URLS }
  try {
    const stored = uni.getStorageSync('backend_urls')
    if (stored) {
      const parsed = typeof stored === 'string' ? JSON.parse(stored) : stored
      if (parsed && typeof parsed === 'object') {
        urls = { ...urls, ...parsed }
      }
    }
  } catch (e) {
    // ignore invalid local overrides
  }

  return normalizeBaseURL(urls[service] || urls.tuantuan)
}

export const BACKEND = DEFAULT_BACKEND_URLS
