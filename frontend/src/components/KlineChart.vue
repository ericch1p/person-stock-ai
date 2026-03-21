<template>
  <div class="kline-chart">
    <div ref="chartRef" class="chart-container"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  data: {
    type: Array,
    default: () => []
  },
  height: {
    type: String,
    default: '500px'
  }
})

const chartRef = ref(null)
let chart = null

const initChart = () => {
  if (!chartRef.value) return
  
  chart = echarts.init(chartRef.value)
  updateChart()
}

const updateChart = () => {
  if (!chart || !props.data.length) return
  
  // 处理数据
  const dates = props.data.map(d => d.date)
  const volumes = props.data.map(d => ({
    value: d.volume,
    itemStyle: {
      color: d.close >= d.open ? '#ef5350' : '#26a69a'
    }
  }))
  
  // K线数据 [open, close, low, high]
  const klineData = props.data.map(d => [d.open, d.close, d.low, d.high])
  
  // 计算均线
  const ma5 = calculateMA(5, props.data)
  const ma10 = calculateMA(10, props.data)
  const ma20 = calculateMA(20, props.data)
  
  const option = {
    backgroundColor: '#fff',
    animation: false,
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      },
      formatter: (params) => {
        const kline = params.find(p => p.seriesType === 'candlestick')
        if (!kline) return ''
        const [open, close, low, high] = kline.data
        const date = kline.axisValue
        const color = close >= open ? '#ef5350' : '#26a69a'
        return `
          <div style="font-family: monospace;">
            <div style="font-weight: bold; margin-bottom: 5px;">${date}</div>
            <div>开盘: <span style="color: ${color}">${open.toFixed(2)}</span></div>
            <div>收盘: <span style="color: ${color}">${close.toFixed(2)}</span></div>
            <div>最低: ${low.toFixed(2)}</div>
            <div>最高: ${high.toFixed(2)}</div>
          </div>
        `
      }
    },
    grid: [
      { left: '10%', right: '8%', top: '10%', height: '50%' },
      { left: '10%', right: '8%', top: '65%', height: '20%' }
    ],
    xAxis: [
      {
        type: 'category',
        data: dates,
        gridIndex: 0,
        axisLabel: { show: false },
        axisLine: { lineStyle: { color: '#ddd' } }
      },
      {
        type: 'category',
        data: dates,
        gridIndex: 1,
        axisLabel: { fontSize: 10 },
        axisLine: { lineStyle: { color: '#ddd' } }
      }
    ],
    yAxis: [
      {
        scale: true,
        gridIndex: 0,
        splitLine: { lineStyle: { color: '#eee' } },
        axisLabel: { fontSize: 10 }
      },
      {
        scale: true,
        gridIndex: 1,
        splitNumber: 2,
        splitLine: { lineStyle: { color: '#eee' } },
        axisLabel: { fontSize: 10, formatter: (val) => {
          if (val >= 10000) return (val/10000).toFixed(0) + '万'
          return val.toFixed(0)
        }}
      }
    ],
    dataZoom: [
      {
        type: 'inside',
        xAxisIndex: [0, 1],
        start: 70,
        end: 100
      },
      {
        type: 'slider',
        xAxisIndex: [0, 1],
        bottom: 5,
        start: 70,
        end: 100
      }
    ],
    series: [
      {
        name: 'K线',
        type: 'candlestick',
        xAxisIndex: 0,
        yAxisIndex: 0,
        data: klineData,
        itemStyle: {
          color: '#ef5350',
          color0: '#26a69a',
          borderColor: '#ef5350',
          borderColor0: '#26a69a'
        }
      },
      {
        name: 'MA5',
        type: 'line',
        xAxisIndex: 0,
        yAxisIndex: 0,
        data: ma5,
        smooth: true,
        symbol: 'none',
        lineStyle: { color: '#f44336', width: 1 }
      },
      {
        name: 'MA10',
        type: 'line',
        xAxisIndex: 0,
        yAxisIndex: 0,
        data: ma10,
        smooth: true,
        symbol: 'none',
        lineStyle: { color: '#ff9800', width: 1 }
      },
      {
        name: 'MA20',
        type: 'line',
        xAxisIndex: 0,
        yAxisIndex: 0,
        data: ma20,
        smooth: true,
        symbol: 'none',
        lineStyle: { color: '#2196f3', width: 1 }
      },
      {
        name: '成交量',
        type: 'bar',
        xAxisIndex: 1,
        yAxisIndex: 1,
        data: volumes,
        barWidth: '60%'
      }
    ]
  }
  
  chart.setOption(option)
}

const calculateMA = (dayCount, data) => {
  const result = []
  for (let i = 0; i < data.length; i++) {
    if (i < dayCount - 1) {
      result.push('-')
      continue
    }
    let sum = 0
    for (let j = 0; j < dayCount; j++) {
      sum += data[i - j].close
    }
    result.push((sum / dayCount).toFixed(2))
  }
  return result
}

const resizeChart = () => {
  chart?.resize()
}

onMounted(() => {
  nextTick(() => {
    initChart()
    window.addEventListener('resize', resizeChart)
  })
})

onUnmounted(() => {
  window.removeEventListener('resize', resizeChart)
  chart?.dispose()
})

watch(() => props.data, () => {
  updateChart()
}, { deep: true })

defineExpose({ resizeChart })
</script>

<style scoped>
.kline-chart {
  width: 100%;
}
.chart-container {
  width: 100%;
  height: v-bind(height);
}
</style>
