<template>
  <div class="backtest-view">
    <el-card>
      <template #header>
        <span>策略回测</span>
      </template>
      
      <el-form :model="form" label-width="120px">
        <el-form-item label="选择策略">
          <el-select v-model="form.strategy_id" placeholder="请选择策略">
            <el-option v-for="s in strategies" :key="s.id" :label="s.name" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="回测区间">
          <el-date-picker v-model="form.dateRange" type="daterange" range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期" format="YYYY-MM-DD" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item label="初始资金">
          <el-input-number v-model="form.initial_capital" :min="10000" :step="10000" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="runBacktest" :loading="loading">运行回测</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <el-card v-if="result" class="result-card">
      <template #header>
        <span>回测结果</span>
      </template>
      
      <el-row :gutter="20">
        <el-col :span="6">
          <el-statistic title="总收益率" :value="result.total_return" suffix="%">
            <template #prefix>
              <span :class="result.total_return >= 0 ? 'up' : 'down'">
                {{ result.total_return >= 0 ? '↑' : '↓' }}
              </span>
            </template>
          </el-statistic>
        </el-col>
        <el-col :span="6">
          <el-statistic title="最大回撤" :value="result.max_drawdown" suffix="%" />
        </el-col>
        <el-col :span="6">
          <el-statistic title="夏普比率" :value="result.sharpe?.toFixed(2) || 0" />
        </el-col>
        <el-col :span="6">
          <el-statistic title="胜率" :value="result.win_rate" suffix="%" />
        </el-col>
      </el-row>
      
      <el-divider />
      
      <el-table :data="result.details || []" stripe>
        <el-table-column prop="code" label="股票代码" width="100" />
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
        <el-table-column prop="total_trades" label="交易次数" width="100" />
        <el-table-column prop="win_rate" label="胜率" width="100">
          <template #default="{ row }">
            {{ row.win_rate?.toFixed(1) }}%
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <el-card class="history-card">
      <template #header>
        <span>历史回测记录</span>
      </template>
      
      <el-table :data="history" stripe v-loading="loading">
        <el-table-column prop="created_at" label="回测时间" width="180" />
        <el-table-column prop="strategy_id" label="策略ID" width="100" />
        <el-table-column prop="start_date" label="开始日期" width="120" />
        <el-table-column prop="end_date" label="结束日期" width="120" />
        <el-table-column prop="total_return" label="收益率" width="100">
          <template #default="{ row }">
            <span :class="row.total_return >= 0 ? 'up' : 'down'">
              {{ row.total_return >= 0 ? '+' : '' }}{{ row.total_return?.toFixed(2) }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="win_rate" label="胜率" width="100">
          <template #default="{ row }">
            {{ row.win_rate?.toFixed(1) }}%
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/api'

const loading = ref(false)
const strategies = ref([])
const result = ref(null)
const history = ref([])

const form = reactive({
  strategy_id: null,
  dateRange: [],
  initial_capital: 100000
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
  } catch (error) {
    ElMessage.error('回测失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadStrategies()
  loadHistory()
  
  // 默认回测区间
  const end = new Date()
  const start = new Date()
  start.setFullYear(start.getFullYear() - 1)
  form.dateRange = [start.toISOString().split('T')[0], end.toISOString().split('T')[0]]
})
</script>

<style scoped>
.result-card, .history-card {
  margin-top: 20px;
}
.up { color: #f56c6c; }
.down { color: #67c23a; }
</style>
