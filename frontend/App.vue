<script>
export default {
  data() {
    return {
      systemInfo: null
    }
  },
  onLaunch() {
    console.log('App Launch')
    this.getSystemInfo()
    uni.switchTab({
      url: '/pages/home/home'
    })
  },
  onShow() {},
  onHide() {},
  methods: {
    getSystemInfo() {
      try {
        const info = uni.getSystemInfoSync()
        this.systemInfo = info
        uni.setStorageSync('systemInfo', info)
      } catch (e) {
        console.error('获取系统信息失败', e)
      }
    }
  }
}
</script>

<style lang="scss">
@import './static/global-zindex.css';

page {
  background-color: #f8f9fa;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
  font-size: 28rpx;
  color: #1a1a1a;
  line-height: 1.5;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

uni-page-wrapper {
  background: #f8f9fa;
  min-height: 100vh;
}

uni-page-body {
  padding-bottom: constant(safe-area-inset-bottom);
  padding-bottom: env(safe-area-inset-bottom);
  min-height: 100vh;
  box-sizing: border-box;
}

view, text {
  box-sizing: border-box;
}

image {
  display: block;
}

scroll-view {
  -webkit-overflow-scrolling: touch;
}

button {
  margin: 0;
  padding: 0;
  background: transparent;
  border: none;
  outline: none;
  font-family: inherit;
}

button::after {
  display: none;
}

input, textarea {
  font-family: inherit;
  outline: none;
}

.tap-effect {
  transition: all 0.2s ease;
}

.tap-effect:active {
  opacity: 0.7;
  transform: scale(0.98);
}

::-webkit-scrollbar {
  display: none;
  width: 0;
  height: 0;
  background: transparent;
}

@media screen and (max-width: 375px) {
  page {
    font-size: 26rpx;
  }
}

@media screen and (min-width: 414px) {
  page {
    font-size: 30rpx;
  }
}

@media screen and (min-width: 750px) {
  page {
    font-size: 32rpx;
  }
  
  uni-page-body {
    max-width: 750rpx;
    margin: 0 auto;
    box-shadow: 0 0 40rpx rgba(0, 0, 0, 0.1);
  }
}

@media screen and (orientation: landscape) {
  uni-page-body {
    max-width: none;
    box-shadow: none;
  }
}
</style>