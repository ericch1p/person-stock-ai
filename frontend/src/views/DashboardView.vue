<template>
  <div class="dashboard">
    <!-- 顶部概览 -->
    <el-row :gutter="20" class="stat-row">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-title">总市值</div>
          <div class="stat-value" :class="profit >= 0 ? 'up' : 'down'">
            ¥{{ totalMarketValue.toLocaleString() }}
          </div>
          <div class="stat-hint">成本 {{ totalCost.toLocaleString() }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-title">持仓盈亏</div>
          <div class="stat-value" :class="profit >= 0 ? 'up' : 'down'">
            {{ profit >= 0 ? '+' : '' }}{{ profit.toLocaleString() }}
          </div>
          <div class="stat-hint" :class="profit >= 0 ? 'up' : 'down'">
            {{ profitRate >= 0 ? '+' : '' }}{{ profitRate.toFixed(2) }}%
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-title">今日收益</div>
          <div class="stat-value" :class="todayProfit >= 0 ? 'up' : 'down'">
            {{ todayProfit >= 0 ? '+' : '' }}{{ todayProfit.toLocaleString() }}
          </div>
          <div class="stat-hint" :class="todayProfit >= 0 ? 'up' : 'down'">
            {{ todayProfitRate >= 0 ? '+' : '' }}{{ todayProfitRate.toFixed(2) }}%
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-title">持仓数</div>
          <div class="stat-value">{{ positions.length }}</div>
          <div class="stat-hint">{{ watchlistCount }} 自选股</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20" class="chart-row">
      <el-col :span="16">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>持仓分布</span>
            </div>
          </template>
          <div ref="pieChartRef" class="pie-chart"></div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>收益排行</span>
            </div>
          </template>
          <el-table :data="topPerformers" stripe size="small" :show-header="false">
            <el-table-column prop="name" label="名称">
              <template #default="{ row }">
                <router-link :to="`/stock/${row.code}`" class="stock-link">
                  {{ row.name }}
                </router-link>
              </template>
            </el-table-column>
            <el-table-column prop="profit_rate" label="收益率" width="80" align="right">
              <template #default="{ row }">
                <span :class="row.profit_rate >= 0 ? 'up' : 'down'">
                  {{ row.profit_rate >= 0 ? '+' : '' }}{{ row.profit_rate?.toFixed(2) }}%
                </span>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <!-- 持仓明细 & 回测 -->
    <el-row :gutter="20" class="table-row">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>持仓明细</span>
              <router-link to="/positions" class="more-link">更多 →</router-link>
            </div>
          </template>
          <el-table :data="positions.slice(0, 5)" stripe size="small">
            <el-table-column prop="code" label="代码" width="90">
              <template #default="{ row }">
                <router-link :to="`/stock/${row.code}`" class="stock-link">
                  {{ row.code }}
                </router-link>
              </template>
            </el-table-column>
            <el-table-column prop="name" label="名称" width="80" />
            <el-table-column label="持仓" width="70" align="right">
              <template #default="{ row }">
                {{ row.shares }}
              </template>
            </el-table-column>
            <el-table-column label="盈亏" width="80" align="right">
              <template #default="{ row }">
                <span :class="row.profit >= 0 ? 'up' : 'down'">
                  {{ row.profit >= 0 ? '+' : '' }}{{ row.profit?.toFixed(0) }}
                </span>
              </template>
            </el-table-column>
            <el-table-column label="收益率" width="80" align="right">
              <template #default="{ row }">
                <span :class="row.profit_rate >= 0 ? 'up' : 'down'">
                  {{ row.profit_rate >= 0 ? '+' : '' }}{{ row.profit_rate?.toFixed(2) }}%
                </span>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>最近回测</span>
              <router-link to="/backtest" class="more-link">更多 →</router-link>
            </div>
          </template>
          <el-table :data="recentBacktests" stripe size="small">
            <el-table-column prop="created_at" label="时间" width="140">
              <template #default="{ row }">
                {{ row.created_at?.slice(0, 16) }}
              </template>
            </el-table-column>
            <el-table-column prop="strategy_name" label="策略" />
            <el-table-column label="收益" width="80" align="right">
              <template #default="{ row }">
                <span :class="row.total_return >= 0 ? 'up' : 'down'">
                  {{ row.total_return >= 0 ? '+' : '' }}{{ row.total_return?.toFixed(1) }}%
                </span>
              </template>
            </el-table-column>
            <el-table-column label="回撤" width="70" align="right">
              <template #default="{ row }">
                {{ row.max_drawdown?.toFixed(1) }}%
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import api from '@/api'

const pieChartRef = ref(null)
let pieChart = null
let refreshTimer = null

// 持仓数据
const positions = ref([])
const profitData = ref({})

// 自选股数量
const watchlistCount = ref(0)

// 回测历史
const recentBacktests = ref([])

// 加载数据
const loadData = async () => {
  try {
    const [positionsRes, watchlistRes, backtestRes] = await Promise.all([
      api.getPositions().catch(() => ({ items: [] })),
      api.getWatchlist().catch(() => ({ items: [] })),
      api.getBacktestResults({ limit: 5 }).catch(() => ({ items: [] }))
    ])
    
    positions.value = positionsRes.items || []
    watchlistCount.value = watchlistRes.items?.length || 0
    recentBacktests.value = backtestRes.items || []
    
    // 加载实时盈亏
    await loadProfitData()
  } catch (error) {
    console.error('加载数据失败:', error)
  }
}

const loadProfitData = async () => {
  try {
    const profit = await api.getPositionsProfit()
    profitData.value = profit
    
    // 更新持仓的盈亏信息
    if (profit.positions) {
      profit.positions.forEach(p => {
        const pos = positions.value.find(x => x.code === p.code)
        if (pos) {
          pos.market_value = p.market_value
          pos.profit = p.profit
          pos.profit_rate = p.profit_rate
        }
      })
    }
  } catch (e) {
    console.error('获取盈亏失败:', e)
  }
}

// 计算属性
const totalMarketValue = computed(() => {
  if (profitData.value.total_market_value) {
    return profitData.value.total_market_value
  }
  return positions.value.reduce((sum, p) => sum + (p.market_value || 0), 0)
})

const totalCost = computed(() => {
  if (profitData.value.total_cost) {
    return profitData.value.total_cost
  }
  return positions.value.reduce((sum, p) => sum + (p.cost || 0), 0)
})

const profit = computed(() => {
  if (profitData.value.total_profit !== undefined) {
    return profitData.value.total_profit
  }
  return totalMarketValue.value - totalCost.value
})

const profitRate = computed(() => {
  return totalCost.value > 0 ? (profit.value / totalCost.value * 100) : 0
})

const todayProfit = computed(() => {
  if (profitData.value.today_profit !== undefined) {
    return profitData.value.today_profit
  }
  return positions.value.reduce((sum, p) => sum + (p.today_profit || 0), 0)
})

const todayProfitRate = computed(() => {
  if (totalMarketValue.value > 0) {
    return (todayProfit.value / totalMarketValue.value * 100)
  }
  return 0
})

const topPerformers = computed(() => {
  return [...positions.value]
    .filter(p => p.profit_rate !== undefined)
    .sort((a, b) => b.profit_rate - a.profit_rate)
    .slice(0, 5)
})

// 饼图
const initPieChart = () => {
  if (!pieChartRef.value) return
  
  pieChart = echarts.init(pieChartRef.value)
  updatePieChart()
}

const updatePieChart = () => {
  if (!pieChart || positions.value.length === 0) return
  
  const data = positions.value
    .filter(p => p.market_value > 0)
    .map(p => ({
      name: p.name || p.code,
      value: p.market_value || 0
    }))
  
  if (data.length === 0) return
  
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: ¥{c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      top: 'middle'
    },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 10,
        borderColor: '#fff',
        borderWidth: 2
      },
      label: {
        show: false
      },
      emphasis: {
        label: {
          show: true,
          fontSize: 14,
          fontWeight: 'bold'
        }
      },
      data: data
    }]
  }
  
  pieChart.setOption(option)
}

// 自动刷新
const startAutoRefresh = () => {
  stopAutoRefresh()
  refreshTimer = setInterval(() => {
    loadProfitData()
  }, 30000)
}

const stopAutoRefresh = () => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
}

onMounted(async () => {
  await loadData()
  await nextTick()
  initPieChart()
  startAutoRefresh()
})

onUnmounted(() => {
  stopAutoRefresh()
  if (pieChart) {
    pieChart.dispose()
  }
})

window.addEventListener('resize', () => {
  if (pieChart) {
    pieChart.resize()
  }
})
</script>

<style scoped>
.dashboard {
  padding: 20px;
  background: #f5f7fa;
  min-height: calc(100vh - 60px);
}

.stat-row {
  margin-bottom: 20px;
}

.stat-card {
  text-align: center;
}

.stat-title {
  font-size: 14px;
  color: #909399;
  margin-bottom: 10px;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
}

.stat-hint {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}

.chart-row {
  margin-bottom: 20px;
}

.table-row {
  margin-bottom: 20px;
}

.pie-chart {
  height: 280px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.more-link {
  color: #409eff;
  text-decoration: none;
  font-size: 14px;
}

.more-link:hover {
  text-decoration: underline;
}

.stock-link {
  color: #409eff;
  text-decoration: none;
}

.stock-link:hover {
  text-decoration: underline;
}

.up {
  color: #ef5350;
}

.down {
  color: #26a69a;
}
</style>
