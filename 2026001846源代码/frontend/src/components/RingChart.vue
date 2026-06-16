<template>
  <view class="ring-chart-wrap">
    <canvas canvas-id="ringCanvas" id="ringCanvas" type="2d" class="ring-canvas"
      :style="{ width: size + 'px', height: size + 'px' }"></canvas>
    <view class="ring-center" :style="{ width: (size * 0.55) + 'px', height: (size * 0.55) + 'px' }">
      <text class="ring-value">{{ centerValue }}</text>
      <text class="ring-label">{{ centerLabel }}</text>
    </view>
  </view>
</template>

<script>
export default {
  name: 'RingChart',
  props: {
    size: { type: Number, default: 120 },
    data: {
      type: Array,
      default: () => [
        { value: 85, color: '#10B981', label: '正常' },
        { value: 10, color: '#F59E0B', label: '告警' },
        { value: 3, color: '#EF4444', label: '故障' },
        { value: 2, color: '#94A3B8', label: '离线' }
      ]
    },
    lineWidth: { type: Number, default: 10 },
    centerLabel: { type: String, default: '在线率' }
  },
  computed: {
    centerValue() {
      const total = this.data.reduce((s, d) => s + d.value, 0)
      const normal = this.data[0]?.value || 0
      return total > 0 ? Math.round((normal / total) * 100) + '%' : '0%'
    }
  },
  watch: {
    data: { handler() { this.draw() }, deep: true }
  },
  mounted() {
    this.$nextTick(() => setTimeout(() => this.draw(), 100))
  },
  methods: {
    draw() {
      const query = uni.createSelectorQuery().in(this)
      query.select('#ringCanvas')
        .fields({ node: true, size: true })
        .exec((res) => {
          if (!res || !res[0] || !res[0].node) return
          const canvas = res[0].node
          const ctx = canvas.getContext('2d')
          const dpr = uni.getSystemInfoSync().pixelRatio || 2
          const w = this.size
          canvas.width = w * dpr
          canvas.height = w * dpr
          ctx.scale(dpr, dpr)

          const cx = w / 2
          const cy = w / 2
          const r = (w - this.lineWidth) / 2 - 2
          const total = this.data.reduce((s, d) => s + d.value, 0)
          if (total === 0) return

          ctx.clearRect(0, 0, w, w)

          let startAngle = -Math.PI / 2
          this.data.forEach((item) => {
            const sweep = (item.value / total) * Math.PI * 2
            ctx.beginPath()
            ctx.arc(cx, cy, r, startAngle, startAngle + sweep)
            ctx.strokeStyle = item.color
            ctx.lineWidth = this.lineWidth
            ctx.lineCap = 'round'
            ctx.stroke()
            startAngle += sweep
          })
        })
    }
  }
}
</script>

<style scoped>
.ring-chart-wrap {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}
.ring-canvas {
  display: block;
}
.ring-center {
  position: absolute;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
.ring-value {
  font-size: 36rpx;
  font-weight: 800;
  color: #0F172A;
}
.ring-label {
  font-size: 20rpx;
  color: #64748B;
  font-weight: 500;
  margin-top: 2rpx;
}
</style>
