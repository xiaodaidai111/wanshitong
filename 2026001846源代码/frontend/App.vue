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
  background-color: #E5EAF1;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
  font-size: 28rpx;
  color: #1a1a1a;
  line-height: 1.5;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

uni-page-wrapper {
  background: #E5EAF1;
  min-height: 100vh;
}

uni-page-body {
  padding-bottom: constant(safe-area-inset-bottom);
  padding-bottom: env(safe-area-inset-bottom);
  min-height: 100vh;
  box-sizing: border-box;
}

view,
text {
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

input,
textarea {
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

@media screen and (min-width: 768px) {
  page {
    font-size: 28rpx;
    background:
      radial-gradient(circle at 22% 18%, rgba(37, 99, 235, 0.12), transparent 28%),
      linear-gradient(135deg, #E2E8F0 0%, #F8FAFC 48%, #DBEAFE 100%);
  }

  uni-page-wrapper {
    background: transparent;
    min-height: 100vh;
    padding: 24px 0;
    box-sizing: border-box;
  }

  uni-page-body {
    max-width: 430px;
    min-height: calc(100vh - 48px);
    margin: 0 auto;
    overflow: hidden;
    border-radius: 34px;
    box-shadow: 0 26px 72px rgba(15, 23, 42, 0.22);
    background: #EEF3F8;
  }
}

@media screen and (orientation: landscape) and (max-width: 767px) {
  uni-page-body {
    max-width: none;
    box-shadow: none;
    border-radius: 0;
  }
}
</style>
