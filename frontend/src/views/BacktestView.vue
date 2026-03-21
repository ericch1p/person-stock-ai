<template>
  <div class="backtest-view">
    <el-row :gutter="20">
      <!-- 左侧：回测配置和结果 -->
      <el-col :span="16">
        <el-card class="config-card">
          <template #header>
            <span>策略回测</span>
          </template>
          
          <el-form :model="form" inline>
            <el-form-item label="策略">
              <el-select v-model="form.strategy_id" placeholder="请选择" style="width: 200px">
                <el-option v-for="s in strategies" :key="s.id" :label="s.name" :value="s.id" />
              </el-select>
            </el-form-item>
            <el-form-item label="回测区间">
              <el-date-picker v-model="form.dateRange" type="daterange" range-separator="至" start-placeholder="开始" end-placeholder="结束" format="YYYY-MM-DD" value-format="YYYY-MM-DD" style="width: 260px" />
            </el-form-item>
            <el-form-item label="初始资金">
              <el-input-number v-model="form.initial_capital" :min="10000" :step="10000" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="runBacktest" :loading="running">
                <el-icon><VideoPlay /></el-icon>
                开始回测
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>

        <!-- 回测结果 -->
        <el-card v-if="result" class="result-card">
          <template #header>
            <div class="card-header">
              <span>回测结果</span>
              <el-button size="small" @click="saveResult" v-if="!result.id">保存结果</el-button>
            </div>
          </template>
          
          <!-- 收益曲线图 -->
          <div ref="chartRef" class="equity-chart"></div>
          
          <!-- 统计指标 -->
          <el-row :gutter="20" class="stats-row">
            <el-col :span="6">
              <div class="stat-item">
                <div class="stat-label">总收益率</div>
                <div class="stat-value" :class="result.total_return >= 0 ? 'up' : 'down'">
                  {{ result.total_return >= 0 ? '+' : '' }}{{ result.total_return?.toFixed(2) }}%
                </div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-item">
                <div class="stat-label">年化收益率</div>
                <div class="stat-value" :class="result.annual_return >= 0 ? 'up' : 'down'">
                  {{ result.annual_return >= 0 ? '+' : '' }}{{ result.annual_return?.toFixed(2) }}%
                </div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-item">
                <div class="stat-label">最大回撤</div>
                <div class="stat-value down">{{ result.max_drawdown?.toFixed(2) }}%</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-item">
                <div class="stat-label">夏普比率</div>
                <div class="stat-value">{{ result.sharpe_ratio?.toFixed(2) }}</div>
              </div>
            </el-col>
          </el-row>
          
          <el-row :gutter="20" class="stats-row">
            <el-col :span="6">
              <div class="stat-item">
                <div class="stat-label">盈利次数</div>
                <div class="stat-value up">{{ result.win_count }}</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-item">
                <div class="stat-label">亏损次数</div>
                <div class="stat-value down">{{ result.lose_count }}</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-item">
                <div class="stat-label">胜率</div>
                <div class="stat-value">{{ result.win_rate?.toFixed(1) }}%</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-item">
                <div class="stat-label">盈亏比</div>
                <div class="stat-value">{{ result.profit_loss_ratio?.toFixed(2) }}</div>
              </div>
            </el-col>
          </el-row>
          
          <!-- 交易记录 -->
          <h4>交易记录</h4>
          <el-table :data="result.trades || []" stripe size="small" max-height="300">
            <el-table-column prop="date" label="日期" width="100" />
            <el-table-column prop="code" label="代码" width="90" />
            <el-table-column prop="name" label="名称" width="80" />
            <el-table-column label="类型" width="60">
              <template #default="{ row }">
                <el-tag :type="row.type === 'buy' ? 'success' : 'danger'" size="small">
                  {{ row.type === 'buy' ? '买' : '卖' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="价格" width="80" align="right">
              <template #default="{ row }">
                {{ row.price?.toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column label="数量" width="70" align="right">
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
          </el-table>
        </el-card>
      </el-col>

      <!-- 右侧：回测历史 -->
      <el-col :span="8">
        <el-card>
          <template #header>
            <span>回测历史</span>
          </template>
          <el-table :data="history" stripe v-loading="loadingHistory">
            <el-table-column prop="created_at" label="时间" width="140">
              <template #default="{ row }">
                {{ row.created_at?.slice(0, 16) }}
              </template>
            </el-table-column>
            <el-table-column prop="strategy_name" label="策略" />
            <el-table-column label="收益" width="70" align="right">
              <template #default="{ row }">
                <span :class="row.total_return >= 0 ? 'up' : 'down'" class="clickable" @click="loadResult(row)">
                  {{ row.total_return >= 0 ? '+' : '' }}{{ row.total_return?.toFixed(1) }}%
                </span>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="60">
              <template #default="{ row }">
                <el-button size="small" type="danger" @click="deleteResult(row.id)" :icon="Delete" circle />
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import { Delete, VideoPlay } from '@element-plus/icons-vue'
import api from '@/api'

const form = ref({
  strategy_id: null,
  dateRange: [],
  initial_capital: 100000
})

const strategies = ref([])
const running = ref(false)
const result = ref(null)
const history = ref([])
const loadingHistory = ref(false)
const chartRef = ref(null)
let chart = null

// 加载策略列表
const loadStrategies = async () => {
  try {
    const res = await api.getStrategies({ limit: 100 })
    strategies.value = res.items || []
    
    // 设置默认日期范围（最近一年）
    const end = new Date()
    const start = new Date()
    start.setFullYear(start.getFullYear() - 1)
    form.value.dateRange = [
      start.toISOString().slice(0, 10),
      end.toISOString().slice(0, 10)
    ]
  } catch (error) {
    console.error('加载策略失败:', error)
  }
}

// 加载回测历史
const loadHistory = async () => {
  loadingHistory.value = true
  try {
    const res = await api.getBacktestResults({ limit: 50 })
    history.value = res.items || []
  } catch (error) {
    ElMessage.error('加载历史失败')
  } finally {
    loadingHistory.value = false
  }
}

// 运行回测
const runBacktest = async () => {
  if (!form.value.strategy_id) {
    ElMessage.warning('请选择策略')
    return
  }
  if (!form.value.dateRange || form.value.dateRange.length !== 2) {
    ElMessage.warning('请选择回测区间')
    return
  }
  
  running.value = true
  try {
    const data = {
      strategy_id: form.value.strategy_id,
      start_date: form.value.dateRange[0],
      end_date: form.value.dateRange[1],
      initial_capital: form.value.initial_capital
    }
    
    const res = await api.runBacktest(data)
    result.value = res
    await nextTick()
    initChart()
    
    ElMessage.success('回测完成')
    loadHistory()
  } catch (error) {
    ElMessage.error('回测失败: ' + (error.message || '未知错误'))
  } finally {
    running.value = false
  }
}

// 保存结果
const saveResult = async () => {
  if (!result.value) return
  try {
    result.value.strategy_id = form.value.strategy_id
    await api.saveBacktestResult(result.value)
    ElMessage.success('已保存')
    result.value.saved = true
    loadHistory()
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

// 加载历史结果
const loadResult = (row) => {
  result.value = row
  nextTick(() => initChart())
}

// 删除结果
const deleteResult = async (id) => {
  try {
    await api.deleteBacktestResult(id)
    ElMessage.success('已删除')
    loadHistory()
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

// 初始化图表
const initChart = () => {
  if (!chartRef.value || !result.value?.equity_curve) return
  
  if (chart) {
    chart.dispose()
  }
  
  chart = echarts.init(chartRef.value)
  
  const dates = result.value.equity_curve.map(d => d.date)
  const values = result.value.equity_curve.map(d => d.value)
  
  const option = {
    tooltip: {
      trigger: 'axis'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: dates,
      boundaryGap: false
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        formatter: '{value}%'
      }
    },
    series: [{
      name: '收益率',
      type: 'line',
      smooth: true,
      symbol: 'none',
      data: values,
      areaStyle: {
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(239, 83, 80, 0.5)' },
            { offset: 1, color: 'rgba(239, 83, 80, 0.05)' }
          ]
        }
      },
      lineStyle: {
        color: '#ef5350'
      }
    }]
  }
  
  chart.setOption(option)
}

onMounted(() => {
  loadStrategies()
  loadHistory()
})

window.addEventListener('resize', () => {
  if (chart) {
    chart.resize()
  }
})
</script>

<style scoped>
.backtest-view {
  padding: 20px;
}
.config-card {
  margin-bottom: 20px;
}
.result-card {
  margin-bottom: 20px;
}
.equity-chart {
  height: 300px;
  margin-bottom: 20px;
}
.stats-row {
  margin-bottom: 20px;
}
.stat-item {
  text-align: center;
  padding: 10px;
  background: #f5f7fa;
  border-radius: 8px;
}
.stat-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 5px;
}
.stat-value {
  font-size: 20px;
  font-weight: bold;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.clickable {
  cursor: pointer;
}
.clickable:hover {
  text-decoration: underline;
}
.up {
  color: #ef5350;
}
.down {
  color: #26a69a;
}
h4 {
  margin: 15px 0 10px;
  color: #303133;
}
</style>
