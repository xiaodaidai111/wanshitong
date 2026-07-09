import guestManager from './guest.js'
export { API_HOST, BACKEND, getBaseURL } from './backend-config.js'
import { getBaseURL } from './backend-config.js'

const buildRequestUrl = (baseURL, path) => {
  if (!path) return baseURL
  if (path.startsWith('http://') || path.startsWith('https://')) return path
  return baseURL + path
}

const request = (config) => {
  const baseURL = getBaseURL(config.service || 'tuantuan')

  return new Promise((resolve, reject) => {
    uni.request({
      url: buildRequestUrl(baseURL, config.url),
      method: config.method || 'GET',
      data: config.data || {},
      timeout: config.timeout || 30000,
      header: {
        'Content-Type': 'application/json',
        ...config.header,
        ...guestManager.getAuthHeader()
      },
      success: (res) => {
        if (res.statusCode === 401) {
          try {
            uni.removeStorageSync('token')
            uni.removeStorageSync('user')
          } catch (e) {}
          reject(res)
          return
        }

        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data)
          return
        }

        reject(res)
      },
      fail: (error) => {
        console.log('request failed:', error)
        reject(error)
      }
    })
  })
}

request.get = (url, config = {}) => {
  return request({
    url,
    method: 'GET',
    ...config
  })
}

request.post = (url, data, config = {}) => {
  return request({
    url,
    method: 'POST',
    data,
    ...config
  })
}

request.put = (url, data, config = {}) => {
  return request({
    url,
    method: 'PUT',
    data,
    ...config
  })
}

request.delete = (url, config = {}) => {
  return request({
    url,
    method: 'DELETE',
    ...config
  })
}

export const uploadFile = (url, filePath, name = 'file', config = {}) => {
  const baseURL = getBaseURL(config.service || 'tuantuan')

  return new Promise((resolve, reject) => {
    uni.uploadFile({
      url: buildRequestUrl(baseURL, url),
      filePath,
      name,
      formData: config.formData || {},
      timeout: config.timeout || 60000,
      header: {
        ...config.header,
        ...guestManager.getAuthHeader()
      },
      success: (res) => {
        let parsedData = res.data
        if (typeof res.data === 'string') {
          try {
            parsedData = JSON.parse(res.data)
          } catch (e) {
            parsedData = res.data
          }
        }

        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(parsedData)
          return
        }

        reject({
          ...res,
          data: parsedData
        })
      },
      fail: (error) => {
        console.log('upload failed:', error)
        reject(error)
      }
    })
  })
}

request.uploadFile = uploadFile

export const getAssetURL = (assetPath) => {
  if (!assetPath) return ''
  if (assetPath.startsWith('http://') || assetPath.startsWith('https://')) {
    return assetPath
  }
  return getBaseURL() + assetPath
}

export default request
