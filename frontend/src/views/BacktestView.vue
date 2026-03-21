<template>
  <div class="backtest-view">
    <el-card>
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
          <el-button type="primary" @click="runBacktest" :loading="loading">运行回测</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <template v-if="result">
      <el-card class="mt-20">
        <template #header>
          <span>收益概览</span>
        </template>
        <StatsCard :stats="overviewStats" :span="6" />
      </el-card>
      
      <el-card class="mt-20">
        <template #header>
          <span>收益曲线</span>
        </template>
        <EquityCurve :data="equityData" :benchmark="benchmarkData" title="累计收益对比" />
      </el-card>
      
      <el-card class="mt-20">
        <template #header>
          <span>交易明细</span>
        </template>
        <el-table :data="result.details || []" stripe>
          <el-table-column prop="code" label="股票" width="100" />
          <el-table-column prop="name" label="名称" width="100" />
          <el-table-column prop="return_rate" label="收益率" width="100">
            <template #default="{ row }">
              <span :class="row.return_rate >= 0 ? 'up' : 'down'">
                {{ row.return_rate >= 0 ? '+' : '' }}{{ row.return_rate?.toFixed(2) }}%
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="max_drawdown" label="最大回撤" width="100">
            <template #default="{ row }">
              {{ row.max_drawdown?.toFixed(2) }}%
            </template>
          </el-table-column>
          <el-table-column prop="win_rate" label="胜率" width="100">
            <template #default="{ row }">
              {{ row.win_rate?.toFixed(1) }}%
            </template>
          </el-table-column>
          <el-table-column prop="total_trades" label="交易次数" width="100" />
          <el-table-column prop="sharpe" label="夏普比率" width="100">
            <template #default="{ row }">
              {{ row.sharpe?.toFixed(2) || '-' }}
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </template>
    
    <el-card class="mt-20">
      <template #header>
        <span>历史回测</span>
      </template>
      <el-table :data="history" stripe v-loading="loading">
        <el-table-column prop="created_at" label="时间" width="160" />
        <el-table-column prop="strategy_id" label="策略ID" width="80" />
        <el-table-column prop="start_date" label="开始" width="110" />
        <el-table-column prop="end_date" label="结束" width="110" />
        <el-table-column prop="total_return" label="收益率" width="100">
          <template #default="{ row }">
            <span :class="row.total_return >= 0 ? 'up' : 'down'">
              {{ row.total_return >= 0 ? '+' : '' }}{{ row.total_return?.toFixed(2) }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="max_drawdown" label="最大回撤" width="100">
          <template #default="{ row }">
            {{ row.max_drawdown?.toFixed(2) }}%
          </template>
        </el-table-column>
        <el-table-column prop="win_rate" label="胜率" width="80">
          <template #default="{ row }">
            {{ row.win_rate?.toFixed(1) }}%
          </template>
        </el-table-column>
        <el-table-column prop="sharpe" label="夏普" width="80">
          <template #default="{ row }">
            {{ row.sharpe?.toFixed(2) || '-' }}
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/api'
import StatsCard from '@/components/StatsCard.vue'
import EquityCurve from '@/components/EquityCurve.vue'

const loading = ref(false)
const strategies = ref([])
const result = ref(null)
const history = ref([])

const form = reactive({
  strategy_id: null,
  dateRange: [],
  initial_capital: 100000
})

const overviewStats = computed(() => {
  if (!result.value) return []
  const r = result.value
  return [
    { label: '总收益率', value: r.total_return?.toFixed(2) || 0, suffix: '%', type: r.total_return >= 0 ? 'profit' : 'loss', compare: r.excess_return },
    { label: '超额收益', value: r.excess_return?.toFixed(2) || 0, suffix: '%', type: r.excess_return >= 0 ? 'profit' : 'loss' },
    { label: '最大回撤', value: r.max_drawdown?.toFixed(2) || 0, suffix: '%', type: 'loss' },
    { label: '夏普比率', value: r.sharpe?.toFixed(2) || '0.00', type: 'neutral' }
  ]
})

const equityData = computed(() => {
  // 模拟收益曲线数据
  if (!result.value?.details?.length) return []
  const details = result.value.details
  return details.map((d, i) => ({
    date: d.code || `Stock ${i + 1}`,
    value: 1 + (d.return_rate || 0) / 100
  }))
})

const benchmarkData = computed(() => {
  if (!equityData.value.length) return []
  // 基准为0收益
  return equityData.value.map(d => ({ date: d.date, value: 1 }))
})

const loadStrategies = async () => {
  const res = await api.getStrategies()
  strategies.value = res.items || []
}

const loadHistory = async () => {
  const res = await api.getBacktestResults()
  history.value = res.items || []
}

const runBacktest = async () => {
  if (!form.strategy_id) {
    ElMessage.warning('请选择策略')
    return
  }
  loading.value = true
  try {
    const res = await api.runBacktest({
      strategy_id: form.strategy_id,
      start_date: form.dateRange[0],
      end_date: form.dateRange[1],
      initial_capital: form.initial_capital
    })
    result.value = res
    ElMessage.success('回测完成')
    loadHistory()
  } catch (e) {
    ElMessage.error('回测失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadStrategies()
  loadHistory()
  const end = new Date()
  const start = new Date()
  start.setFullYear(start.getFullYear() - 1)
  form.dateRange = [start.toISOString().split('T')[0], end.toISOString().split('T')[0]]
})
</script>

<style scoped>
.mt-20 { margin-top: 20px; }
.up { color: #ef5350; }
.down { color: #26a69a; }
</style>
