<template>
  <view class="line-chart-wrap">
    <canvas canvas-id="lineCanvas" id="lineCanvas" type="2d" class="line-canvas"
      :style="{ width: width + 'px', height: height + 'px' }"></canvas>
  </view>
</template>

<script>
export default {
  name: 'LineChart',
  props: {
    width: { type: Number, default: 300 },
    height: { type: Number, default: 160 },
    labels: {
      type: Array,
      default: () => ['1月', '2月', '3月', '4月', '5月', '6月', '7月']
    },
    datasets: {
      type: Array,
      default: () => [
        { label: '检修次数', values: [12, 19, 8, 15, 22, 18, 25], color: '#3B82F6' },
        { label: '完成率', values: [10, 15, 7, 13, 20, 16, 24], color: '#10B981' }
      ]
    }
  },
  watch: {
    datasets: { handler() { this.draw() }, deep: true },
    labels: { handler() { this.draw() }, deep: true }
  },
  mounted() {
    this.$nextTick(() => setTimeout(() => this.draw(), 100))
  },
  methods: {
    draw() {
      const query = uni.createSelectorQuery().in(this)
      query.select('#lineCanvas')
        .fields({ node: true, size: true })
        .exec((res) => {
          if (!res || !res[0] || !res[0].node) return
          const canvas = res[0].node
          const ctx = canvas.getContext('2d')
          const dpr = uni.getSystemInfoSync().pixelRatio || 2
          const w = this.width
          const h = this.height
          canvas.width = w * dpr
          canvas.height = h * dpr
          ctx.scale(dpr, dpr)

          ctx.clearRect(0, 0, w, h)

          const padding = { top: 20, right: 16, bottom: 30, left: 36 }
          const chartW = w - padding.left - padding.right
          const chartH = h - padding.top - padding.bottom

          // 计算Y轴范围
          let maxVal = 0
          this.datasets.forEach(ds => {
            ds.values.forEach(v => { if (v > maxVal) maxVal = v })
          })
          maxVal = Math.ceil(maxVal * 1.2) || 10

          // 绘制网格线
          ctx.strokeStyle = '#F1F5F9'
          ctx.lineWidth = 1
          for (let i = 0; i <= 4; i++) {
            const y = padding.top + (chartH / 4) * i
            ctx.beginPath()
            ctx.moveTo(padding.left, y)
            ctx.lineTo(w - padding.right, y)
            ctx.stroke()

            // Y轴标签
            const val = Math.round(maxVal - (maxVal / 4) * i)
            ctx.fillStyle = '#94A3B8'
            ctx.font = '10px sans-serif'
            ctx.textAlign = 'right'
            ctx.fillText(String(val), padding.left - 6, y + 4)
          }

          // X轴标签
          const stepX = chartW / (this.labels.length - 1 || 1)
          ctx.fillStyle = '#94A3B8'
          ctx.font = '10px sans-serif'
          ctx.textAlign = 'center'
          this.labels.forEach((label, i) => {
            const x = padding.left + stepX * i
            ctx.fillText(label, x, h - 8)
          })

          // 绘制数据线
          this.datasets.forEach((ds) => {
            const points = ds.values.map((v, i) => ({
              x: padding.left + stepX * i,
              y: padding.top + chartH - (v / maxVal) * chartH
            }))

            // 填充区域
            ctx.beginPath()
            ctx.moveTo(points[0].x, padding.top + chartH)
            points.forEach(p => ctx.lineTo(p.x, p.y))
            ctx.lineTo(points[points.length - 1].x, padding.top + chartH)
            ctx.closePath()
            const gradient = ctx.createLinearGradient(0, padding.top, 0, padding.top + chartH)
            gradient.addColorStop(0, ds.color + '30')
            gradient.addColorStop(1, ds.color + '05')
            ctx.fillStyle = gradient
            ctx.fill()

            // 折线
            ctx.beginPath()
            points.forEach((p, i) => {
              if (i === 0) ctx.moveTo(p.x, p.y)
              else ctx.lineTo(p.x, p.y)
            })
            ctx.strokeStyle = ds.color
            ctx.lineWidth = 2.5
            ctx.lineJoin = 'round'
            ctx.lineCap = 'round'
            ctx.stroke()

            // 数据点
            points.forEach((p) => {
              ctx.beginPath()
              ctx.arc(p.x, p.y, 3, 0, Math.PI * 2)
              ctx.fillStyle = '#FFFFFF'
              ctx.fill()
              ctx.strokeStyle = ds.color
              ctx.lineWidth = 2
              ctx.stroke()
            })
          })
        })
    }
  }
}
</script>

<style scoped>
.line-chart-wrap {
  display: inline-block;
}
.line-canvas {
  display: block;
}
</style>
