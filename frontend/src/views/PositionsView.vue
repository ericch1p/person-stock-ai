<template>
  <div class="positions-view">
    <!-- 收益概览 -->
    <el-row :gutter="20" class="mb-20" v-if="profitData.positions?.length">
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-label">总市值</div>
          <div class="stat-value">¥{{ profitData.total_value?.toFixed(2) }}</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-label">总成本</div>
          <div class="stat-value">¥{{ profitData.total_cost?.toFixed(2) }}</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card" :class="profitData.total_profit >= 0 ? 'profit' : 'loss'">
          <div class="stat-label">总盈亏</div>
          <div class="stat-value">
            {{ profitData.total_profit >= 0 ? '+' : '' }}{{ profitData.total_profit?.toFixed(2) }}
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card" :class="profitData.total_profit_pct >= 0 ? 'profit' : 'loss'">
          <div class="stat-label">收益率</div>
          <div class="stat-value">
            {{ profitData.total_profit_pct >= 0 ? '+' : '' }}{{ profitData.total_profit_pct?.toFixed(2) }}%
          </div>
        </div>
      </el-col>
    </el-row>

    <el-card>
      <template #header>
        <div class="card-header">
          <span>持仓管理</span>
          <div>
            <el-button type="info" @click="refreshProfit" :loading="refreshing">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
            <el-switch v-model="autoRefresh" active-text="自动刷新" inactive-text="" @change="toggleAutoRefresh" style="margin-left: 10px" />
            <span v-if="autoRefresh" class="refresh-hint">每{{ refreshSeconds }}秒</span>
            <el-button type="primary" @click="showAddDialog">
              <el-icon><Plus /></el-icon>
              记录买入
            </el-button>
          </div>
        </div>
      </template>
      
      <el-table :data="profitData.positions || []" stripe v-loading="loading">
        <el-table-column prop="code" label="代码" width="100">
          <template #default="{ row }">
            <router-link :to="`/stock/${row.code}?name=${encodeURIComponent(row.name)}`">
              {{ row.code }}
            </router-link>
          </template>
        </el-table-column>
        <el-table-column prop="name" label="名称" width="120" />
        <el-table-column prop="buy_date" label="买入日期" width="110" />
        <el-table-column prop="buy_price" label="买入价" width="90">
          <template #default="{ row }">
            {{ row.buy_price?.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="current_price" label="现价" width="90">
          <template #default="{ row }">
            <span :class="row.current_change >= 0 ? 'up' : 'down'">
              {{ row.current_price?.toFixed(2) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="current_change" label="涨跌幅" width="90">
          <template #default="{ row }">
            <span :class="row.current_change >= 0 ? 'up' : 'down'">
              {{ row.current_change >= 0 ? '+' : '' }}{{ row.current_change?.toFixed(2) }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="quantity" label="数量" width="80" />
        <el-table-column prop="profit" label="盈亏" width="100">
          <template #default="{ row }">
            <span :class="row.profit >= 0 ? 'up' : 'down'">
              {{ row.profit >= 0 ? '+' : '' }}{{ row.profit?.toFixed(2) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="profit_pct" label="收益率" width="100">
          <template #default="{ row }">
            <span :class="row.profit_pct >= 0 ? 'up' : 'down'">
              {{ row.profit_pct >= 0 ? '+' : '' }}{{ row.profit_pct?.toFixed(2) }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="profit_loss" label="盈亏" width="100">
          <template #default="{ row }">
            <span :class="(row.profit_loss || 0) >= 0 ? 'up' : 'down'">
              {{ (row.profit_loss || 0) >= 0 ? '+' : '' }}{{ row.profit_loss?.toFixed(2) || 0 }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="profit_loss_pct" label="收益率" width="100">
          <template #default="{ row }">
            <span :class="(row.profit_loss_pct || 0) >= 0 ? 'up' : 'down'">
              {{ (row.profit_loss_pct || 0) >= 0 ? '+' : '' }}{{ row.profit_loss_pct?.toFixed(2) || 0 }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 'open' ? 'success' : 'info'">
              {{ row.status === 'open' ? '持仓' : '已平' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button v-if="row.status === 'open'" size="small" type="danger" @click="sell(row)">
              卖出
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 买入对话框 -->
    <el-dialog v-model="addDialogVisible" title="记录买入" width="400px">
      <el-form :model="buyForm" label-width="100px">
        <el-form-item label="股票代码">
          <el-input v-model="buyForm.code" />
        </el-form-item>
        <el-form-item label="股票名称">
          <el-input v-model="buyForm.name" />
        </el-form-item>
        <el-form-item label="买入日期">
          <el-date-picker v-model="buyForm.buy_date" type="date" format="YYYY-MM-DD" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item label="买入价格">
          <el-input-number v-model="buyForm.buy_price" :precision="2" />
        </el-form-item>
        <el-form-item label="买入数量">
          <el-input-number v-model="buyForm.quantity" :step="100" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="buyForm.notes" type="textarea" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitBuy">确定</el-button>
      </template>
    </el-dialog>
    
    <!-- 卖出对话框 -->
    <el-dialog v-model="sellDialogVisible" title="记录卖出" width="400px">
      <el-form :model="sellForm" label-width="100px">
        <el-form-item label="股票">
          <span>{{ sellForm.name }} ({{ sellForm.code }})</span>
        </el-form-item>
        <el-form-item label="卖出日期">
          <el-date-picker v-model="sellForm.sell_date" type="date" format="YYYY-MM-DD" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item label="卖出价格">
          <el-input-number v-model="sellForm.sell_price" :precision="2" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="sellForm.notes" type="textarea" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="sellDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitSell">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useRoute } from 'vue-router'
import api from '@/api'

const route = useRoute()
const loading = ref(false)
const refreshing = ref(false)
const positions = ref([])
const profitData = ref({})
const autoRefresh = ref(true)
const refreshSeconds = ref(30)
let refreshTimer = null
const addDialogVisible = ref(false)
const sellDialogVisible = ref(false)

const buyForm = reactive({
  code: '',
  name: '',
  buy_date: new Date().toISOString().split('T')[0],
  buy_price: 0,
  quantity: 100,
  notes: ''
})

const sellForm = reactive({
  id: null,
  code: '',
  name: '',
  sell_date: new Date().toISOString().split('T')[0],
  sell_price: 0,
  notes: ''
})

const loadData = async () => {
  loading.value = true
  try {
    const res = await api.getPositions()
    positions.value = res.items || []
    await refreshProfit()
  } catch (error) {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

const refreshProfit = async () => {
  refreshing.value = true
  try {
    const res = await api.getPositionsProfit()
    profitData.value = res || {}
  } catch (error) {
    console.error('获取盈亏失败:', error)
  } finally {
    refreshing.value = false
  }
}

const showAddDialog = () => {
  buyForm.code = route.query.code || ''
  buyForm.name = route.query.name || ''
  addDialogVisible.value = true
}

const submitBuy = async () => {
  try {
    await api.createPosition(buyForm)
    ElMessage.success('记录成功')
    addDialogVisible.value = false
    loadData()
  } catch (error) {
    ElMessage.error('记录失败')
  }
}

const sell = (row) => {
  sellForm.id = row.id
  sellForm.code = row.code
  sellForm.name = row.name
  sellForm.sell_price = row.buy_price
  sellDialogVisible.value = true
}

const submitSell = async () => {
  try {
    await api.updatePosition(sellForm.id, {
      sell_date: sellForm.sell_date,
      sell_price: sellForm.sell_price,
      notes: sellForm.notes
    })
    ElMessage.success('卖出记录成功')
    sellDialogVisible.value = false
    loadData()
  } catch (error) {
    ElMessage.error('记录失败')
  }
}

onMounted(() => {
  loadData()
  startAutoRefresh()
})

onUnmounted(() => {
  stopAutoRefresh()
})

const startAutoRefresh = () => {
  stopAutoRefresh()
  if (autoRefresh.value) {
    refreshTimer = setInterval(() => {
      refreshProfit()
    }, refreshSeconds.value * 1000)
  }
}

const stopAutoRefresh = () => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
}

const toggleAutoRefresh = () => {
  if (autoRefresh.value) {
    startAutoRefresh()
  } else {
    stopAutoRefresh()
  }
}
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.up { color: #f56c6c; }
.down { color: #67c23a; }
</style>

<style scoped>
.stat-card {
  background: #fff;
  border-radius: 8px;
  padding: 16px;
  text-align: center;
}
.stat-card.profit .stat-value { color: #ef5350; }
.stat-card.loss .stat-value { color: #26a69a; }
.stat-label { font-size: 13px; color: #909399; margin-bottom: 8px; }
.stat-value { font-size: 24px; font-weight: bold; }
.mb-20 { margin-bottom: 20px; }
.up { color: #ef5350; }
.down { color: #26a69a; }
.refresh-hint {
  font-size: 12px;
  color: #909399;
  margin-left: 5px;
}
</style>
