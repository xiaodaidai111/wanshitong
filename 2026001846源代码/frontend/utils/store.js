// 状态管理工具，使用UniApp的storage API实现持久化存储

const STORE_KEY = 'app_state'

// 初始状态
const initialState = {
  token: '',
  userName: '',
  aratar: ''
}

// 获取状态
const getState = () => {
  try {
    const stateStr = uni.getStorageSync(STORE_KEY)
    if (stateStr) {
      return JSON.parse(stateStr)
    }
  } catch (e) {
    console.error('获取状态失败:', e)
  }
  return {...initialState}
}

// 设置状态
const setState = (newState) => {
  try {
    const currentState = getState()
    const state = {...currentState, ...newState}
    uni.setStorageSync(STORE_KEY, JSON.stringify(state))
  } catch (e) {
    console.error('设置状态失败:', e)
  }
}

// 状态操作方法
export const userStore = {
  // 获取token
  get token() {
    return getState().token
  },
  
  // 获取userName
  get userName() {
    return getState().userName
  },
  
  // 获取aratar
  get aratar() {
    return getState().aratar
  },
  
  // 设置token
  settoken(newToken) {
    setState({ token: newToken })
  },
  
  // 设置userName
  setUserName(newUserName) {
    setState({ userName: newUserName })
  },
  
  // 设置aratar
  setAratar(newAratar) {
    setState({ aratar: newAratar })
  },
  
  // 移除所有状态
  removeToken() {
    setState(initialState)
  }
}