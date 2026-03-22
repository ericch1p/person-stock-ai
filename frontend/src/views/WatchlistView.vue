<template>
  <div class="watchlist-view">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>自选股池</span>
          <div>
            <el-button type="warning" @click="syncData" :loading="syncing" size="small">
              <el-icon><Refresh /></el-icon>
              同步数据
            </el-button>
            <el-button type="primary" @click="showAddDialog = true" size="small">
              <el-icon><Plus /></el-icon>
              添加
            </el-button>
          <div>
            <el-tag v-if="marketSummary" :class="marketSummary.change >= 0 ? 'up' : 'down'">
              {{ marketSummary.change >= 0 ? '↑' : '↓' }} {{ Math.abs(marketSummary.change).toFixed(2) }}%
            </el-tag>
            <el-button type="info" @click="refreshQuotes" :loading="refreshing" size="small" style="margin-left: 10px">
              <el-icon><Refresh /></el-icon>
            </el-button>
            <el-switch v-model="autoRefresh" active-text="自动" @change="toggleAutoRefresh" style="margin-left: 10px" />
          </div>
        </div>
      </template>
      
      <el-table :data="watchlistWithQuote" stripe v-loading="loading">
        <el-table-column prop="code" label="代码" width="100">
          <template #default="{ row }">
            <router-link :to="`/stock/${row.code}?name=${encodeURIComponent(row.name)}`" class="stock-link">
              {{ row.code }}
            </router-link>
          </template>
        </el-table-column>
        <el-table-column prop="name" label="名称" width="100">
          <template #default="{ row }">
            <router-link :to="`/stock/${row.code}?name=${encodeURIComponent(row.name)}`" class="stock-link">
              {{ row.name }}
            </router-link>
          </template>
        </el-table-column>
        <el-table-column label="现价" width="100" align="right">
          <template #default="{ row }">
            <span :class="row.change_pct >= 0 ? 'up' : 'down'" class="price">
              {{ row.price?.toFixed(2) || '-' }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="涨跌幅" width="100" align="right">
          <template #default="{ row }">
            <span :class="row.change_pct >= 0 ? 'up' : 'down'" class="change">
              {{ row.change_pct >= 0 ? '+' : '' }}{{ row.change_pct?.toFixed(2) || 0 }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column label="涨跌额" width="100" align="right">
          <template #default="{ row }">
            <span :class="row.change >= 0 ? 'up' : 'down'">
              {{ row.change >= 0 ? '+' : '' }}{{ row.change?.toFixed(2) || 0 }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="成交量" width="100" align="right">
          <template #default="{ row }">
            {{ formatVolume(row.volume) }}
          </template>
        </el-table-column>
        <el-table-column label="换手率" width="80" align="right">
          <template #default="{ row }">
            {{ row.turnover?.toFixed(1) || '-' }}%
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small">{{ statusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="select_date" label="关注日期" width="110" />
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" @click="toKline(row)">K线</el-button>
            <el-button size="small" type="success" @click="toBuy(row)">买入</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="refresh-info" v-if="lastRefresh">
        最后刷新: {{ lastRefresh }}
      </div>
    </el-card>

    <!-- 添加自选股对话框 -->
    <el-dialog v-model="showAddDialog" title="添加自选股" width="400px">
      <el-form :model="addForm" label-width="80px">
        <el-form-item label="股票代码">
          <el-input v-model="addForm.code" placeholder="如: 600519" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="addForm.notes" type="textarea" placeholder="选填" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="addToWatchlist">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import { Plus } from '@element-plus/icons-vue'
import api from '@/api'

const router = useRouter()
const loading = ref(false)
const refreshing = ref(false)
const syncing = ref(false)
const watchlist = ref([])
const quotes = ref({})
const showAddDialog = ref(false)
const addForm = ref({ code: '', notes: '' })
const lastRefresh = ref('')
const autoRefresh = ref(true)
let refreshTimer = null
const refreshSeconds = 30

const watchlistWithQuote = computed(() => {
  return watchlist.value.map(item => ({
    ...item,
    ...quotes.value[item.code]
  }))
})

const marketSummary = computed(() => {
  const prices = Object.values(quotes.value)
  if (prices.length === 0) return null
  const avgChange = prices.reduce((sum, q) => sum + (q.change_pct || 0), 0) / prices.length
  return { change: avgChange }
})

const statusType = (status) => {
  const types = { watch: 'info', hold: 'success', sell: 'warning', abandon: 'danger' }
  return types[status] || 'info'
}

const statusText = (status) => {
  const texts = { watch: '观察', hold: '持仓', sell: '已卖出', abandon: '放弃' }
  return texts[status] || status
}

const formatVolume = (vol) => {
  if (!vol) return '-'
  if (vol >= 100000000) return (vol / 100000000).toFixed(2) + '亿'
  if (vol >= 10000) return (vol / 10000).toFixed(0) + '万'
  return vol.toFixed(0)
}

const loadWatchlist = async () => {
  loading.value = true
  try {
    const res = await api.getWatchlist()
    watchlist.value = res.items || []
  } catch (error) {
    ElMessage.error('加载自选股失败')
  } finally {
    loading.value = false
  }
}

const loadQuotes = async () => {
  if (watchlist.value.length === 0) return
  
  refreshing.value = true
  try {
    const codes = watchlist.value.map(w => w.code)
    const res = await api.getRealtimeQuote(codes)
    
    const quotesDict = {}
    res.forEach(q => {
      quotesDict[q.code] = q
    })
    quotes.value = quotesDict
    lastRefresh.value = new Date().toLocaleTimeString()
  } catch (error) {
    console.error('获取行情失败:', error)
  } finally {
    refreshing.value = false
  }
}

const refreshQuotes = () => loadQuotes()

const syncData = async () => {
  syncing.value = true
  try {
    ElMessage.info('开始同步数据，请稍候...')
    const res = await api.post('/watchlist/sync')
    if (res.success) {
      ElMessage.success(`同步完成: 成功${res.success}个，失败${res.failed}个`)
      await loadWatchlist()
      await loadQuotes()
    } else {
      ElMessage.error(res.message || '同步失败')
    }
  } catch (error) {
    ElMessage.error('同步失败')
  } finally {
    syncing.value = false
  }
}

const addToWatchlist = async () => {
  if (!addForm.value.code) {
    ElMessage.warning('请输入股票代码')
    return
  }
  
  try {
    const code = addForm.value.code.replace(/\s/g, '')
    await api.addToWatchlist({
      code: code,
      name: code,  // 后端会根据代码获取名称
      notes: addForm.value.notes
    })
    ElMessage.success('添加成功')
    showAddDialog.value = false
    addForm.value = { code: '', notes: '' }
    await loadWatchlist()
    await loadQuotes()
  } catch (error) {
    ElMessage.error('添加失败')
  }
}

const toggleAutoRefresh = () => {
  if (autoRefresh.value) {
    startAutoRefresh()
  } else {
    stopAutoRefresh()
  }
}

const startAutoRefresh = () => {
  stopAutoRefresh()
  if (autoRefresh.value) {
    refreshTimer = setInterval(() => {
      loadQuotes()
    }, refreshSeconds * 1000)
  }
}

const stopAutoRefresh = () => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
}

const toKline = (stock) => {
  router.push(`/stock/${stock.code}?name=${encodeURIComponent(stock.name)}`)
}

const toBuy = (stock) => {
  router.push({ path: '/positions', query: { code: stock.code, name: stock.name } })
}

onMounted(async () => {
  await loadWatchlist()
  await loadQuotes()
  startAutoRefresh()
})

onUnmounted(() => {
  stopAutoRefresh()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.stock-link {
  color: #409eff;
  text-decoration: none;
}
.stock-link:hover {
  text-decoration: underline;
}
.price {
  font-weight: bold;
  font-size: 15px;
}
.change {
  font-weight: bold;
}
.up {
  color: #ef5350;
}
.down {
  color: #26a69a;
}
.refresh-info {
  margin-top: 10px;
  text-align: right;
  font-size: 12px;
  color: #909399;
}
</style>
