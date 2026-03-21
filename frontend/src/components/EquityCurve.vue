<template>
  <div class="equity-curve">
    <div ref="chartRef" class="chart-container"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  data: { type: Array, default: () => [] },
  benchmark: { type: Array, default: () => [] },
  title: { type: String, default: '收益曲线' }
})

const chartRef = ref(null)
let chart = null

const initChart = () => {
  if (!chartRef.value) return
  chart = echarts.init(chartRef.value)
  window.addEventListener('resize', () => chart?.resize())
}

const updateChart = () => {
  if (!chart) return
  
  const dates = props.data.map(d => d.date)
  const equity = props.data.map(d => d.value)
  const benchmark = props.benchmark.map(d => d.value)
  
  const option = {
    backgroundColor: '#fff',
    title: { text: props.title, left: 'center', textStyle: { fontSize: 14 } },
    tooltip: {
      trigger: 'axis',
      formatter: (params) => {
        let res = params[0].axisValue + '<br/>'
        params.forEach(p => {
          const color = p.seriesName === '策略收益' ? '#409eff' : '#909399'
          const value = p.value?.toFixed(2) || 0
          const pct = ((p.value - 1) * 100).toFixed(2) + '%'
          res += `<span style="color:${color}">${p.seriesName}: ${value} (${pct})</span><br/>`
        })
        return res
      }
    },
    legend: {
      data: ['策略收益', '基准收益'],
      top: 30
    },
    grid: { left: '10%', right: '10%', top: '20%', bottom: '15%' },
    xAxis: {
      type: 'category',
      data: dates,
      axisLabel: { fontSize: 10 }
    },
    yAxis: {
      type: 'value',
      axisLabel: { formatter: (v) => (v * 100).toFixed(0) + '%' },
      splitLine: { lineStyle: { type: 'dashed', opacity: 0.3 } }
    },
    dataZoom: [
      { type: 'inside', start: 0, end: 100 },
      { type: 'slider', start: 0, end: 100 }
    ],
    series: [
      {
        name: '策略收益',
        type: 'line',
        data: equity,
        smooth: true,
        lineStyle: { width: 2, color: '#409eff' },
        areaStyle: { color: 'rgba(64, 158, 255, 0.1)' }
      },
      {
        name: '基准收益',
        type: 'line',
        data: benchmark,
        smooth: true,
        lineStyle: { width: 1, color: '#909399', type: 'dashed' }
      }
    ]
  }
  
  chart.setOption(option)
}

watch(() => props.data, updateChart, { deep: true })

onMounted(() => {
  setTimeout(() => {
    initChart()
    updateChart()
  }, 100)
})

onUnmounted(() => chart?.dispose())
</script>

<style scoped>
.equity-curve { width: 100%; }
.chart-container { width: 100%; height: 350px; }
</style>
