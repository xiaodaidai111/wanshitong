<template>
  <div ref="el" class="echart-root" :style="{ height }"></div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  option: { type: Object, required: true },
  height: { type: String, default: '260px' },
  // 若提供该字段，点击图表元素时会将该字段对应的值作为事件抛出
  clickField: { type: String, default: '' }
})
const emit = defineEmits(['click'])

const el = ref(null)
let chart = null
let resizeObserver = null

const render = () => {
  if (!chart) return
  chart.setOption(props.option, true)
}

onMounted(async () => {
  await nextTick()
  if (!el.value) return
  chart = echarts.init(el.value)
  chart.setOption(props.option, true)
  if (props.clickField) {
    chart.on('click', (params) => {
      if (!params) return
      const data = params.data || {}
      if (props.clickField in data) emit('click', data[props.clickField])
      else if (params.name) emit('click', params.name)
    })
  }
  // 容器尺寸变化时自适应（面板显隐、侧栏折叠等场景）
  resizeObserver = new ResizeObserver(() => chart && chart.resize())
  resizeObserver.observe(el.value)
})

watch(() => props.option, () => render(), { deep: true })

onBeforeUnmount(() => {
  if (resizeObserver) { resizeObserver.disconnect(); resizeObserver = null }
  if (chart) { chart.dispose(); chart = null }
})

defineExpose({ resize: () => chart && chart.resize() })
</script>

<style scoped>
.echart-root {
  width: 100%;
  min-height: 0;
}
</style>
