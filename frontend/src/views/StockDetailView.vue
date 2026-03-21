<template>
  <div class="stock-detail">
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <el-icon class="is-loading"><Loading /></el-icon>
      <span>加载中...</span>
    </div>

    <template v-else-if="stockInfo">
      <!-- 股票信息头部 -->
      <el-card class="stock-header">
        <el-row :gutter="20">
          <el-col :span="8">
            <div class="stock-name">{{ stockInfo.name }}</div>
            <div class="stock-code">{{ stockInfo.code }}</div>
            <div class="stock-industry">{{ stockInfo.industry || '未知行业' }}</div>
          </el-col>
          <el-col :span="8">
            <div class="stock-price" :class="priceClass">
              {{ lastKline?.close?.toFixed(2) || '-' }}
            </div>
            <div class="stock-change" :class="priceClass">
              {{ formatChange(lastKline) }}
            </div>
          </el-col>
          <el-col :span="8">
            <div class="stock-indicators">
              <div class="indicator-item">
                <span class="label">今开</span>
                <span class="value">{{ lastKline?.open?.toFixed(2) || '-' }}</span>
              </div>
              <div class="indicator-item">
                <span class="label">最高</span>
                <span class="value">{{ lastKline?.high?.toFixed(2) || '-' }}</span>
              </div>
              <div class="indicator-item">
                <span class="label">最低</span>
                <span class="value">{{ lastKline?.low?.toFixed(2) || '-' }}</span>
              </div>
              <div class="indicator-item">
                <span class="label">成交量</span>
                <span class="value">{{ formatVolume(lastKline?.volume) }}</span>
              </div>
            </div>
          </el-col>
        </el-row>
      </el-card>

      <!-- K线图 -->
      <el-card class="chart-card">
        <template #header>
          <div class="card-header">
            <span>K线图表</span>
            <div class="chart-controls">
              <el-radio-group v-model="period" size="small">
                <el-radio-button label="日K">日K</el-radio-button>
                <el-radio-button label="周K">周K</el-radio-button>
                <el-radio-button label="月K">月K</el-radio-button>
              </el-radio-group>
              <el-checkbox v-model="showMA" label="MA5" />
              <el-checkbox v-model="showMA10" label="MA10" />
              <el-checkbox v-model="showMA20" label="MA20" />
              <el-checkbox v-model="showVolume" label="成交量" />
            </div>
          </div>
        </template>
        <KlineChart :data="klineData" height="500px" />
      </el-card>

      <!-- 技术指标 -->
      <el-card class="indicators-card">
        <template #header>
          <span>技术指标</span>
        </template>
        <el-row :gutter="20">
          <el-col :span="6">
            <div class="indicator-box">
              <div class="indicator-title">MACD</div>
              <div class="indicator-values">
                <span>DIF: {{ indicators.macd?.dif?.toFixed(2) || '-' }}</span>
                <span>DEA: {{ indicators.macd?.dea?.toFixed(2) || '-' }}</span>
                <span>MACD: {{ indicators.macd?.macd?.toFixed(2) || '-' }}</span>
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="indicator-box">
              <div class="indicator-title">KDJ</div>
              <div class="indicator-values">
                <span>K: {{ indicators.kdj?.k?.toFixed(2) || '-' }}</span>
                <span>D: {{ indicators.kdj?.d?.toFixed(2) || '-' }}</span>
                <span>J: {{ indicators.kdj?.j?.toFixed(2) || '-' }}</span>
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="indicator-box">
              <div class="indicator-title">RSI</div>
              <div class="indicator-values">
                <span>RSI6: {{ indicators.rsi?.rsi6?.toFixed(2) || '-' }}</span>
                <span>RSI12: {{ indicators.rsi?.rsi12?.toFixed(2) || '-' }}</span>
                <span>RSI24: {{ indicators.rsi?.rsi24?.toFixed(2) || '-' }}</span>
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="indicator-box">
              <div class="indicator-title">BOLL</div>
              <div class="indicator-values">
                <span>上轨: {{ indicators.boll?.upper?.toFixed(2) || '-' }}</span>
                <span>中轨: {{ indicators.boll?.middle?.toFixed(2) || '-' }}</span>
                <span>下轨: {{ indicators.boll?.lower?.toFixed(2) || '-' }}</span>
              </div>
            </div>
          </el-col>
        </el-row>
      </el-card>

      <!-- 基本面信息 -->
      <el-card class="financial-card" v-if="financialData">
        <template #header>
          <span>基本面信息</span>
        </template>
        <el-descriptions :column="4" border>
          <el-descriptions-item label="市盈率(PE)">{{ financialData.pe?.toFixed(2) || '-' }}</el-descriptions-item>
          <el-descriptions-item label="市净率(PB)">{{ financialData.pb?.toFixed(2) || '-' }}</el-descriptions-item>
          <el-descriptions-item label="总市值">{{ formatAmount(financialData.total_market) }}</el-descriptions-item>
          <el-descriptions-item label="流通市值">{{ formatAmount(financialData.float_market) }}</el-descriptions-item>
          <el-descriptions-item label="ROE">{{ financialData.roe ? financialData.roe.toFixed(2) + '%' : '-' }}</el-descriptions-item>
          <el-descriptions-item label="毛利率">{{ financialData.gross_margin ? financialData.gross_margin.toFixed(2) + '%' : '-' }}</el-descriptions-item>
          <el-descriptions-item label="净利率">{{ financialData.net_margin ? financialData.net_margin.toFixed(2) + '%' : '-' }}</el-descriptions-item>
          <el-descriptions-item label="营收增长">{{ financialData.revenue_growth ? financialData.revenue_growth.toFixed(2) + '%' : '-' }}</el-descriptions-item>
          <el-descriptions-item label="净利润增长">{{ financialData.net_profit_growth ? financialData.net_profit_growth.toFixed(2) + '%' : '-' }}</el-descriptions-item>
          <el-descriptions-item label="资产负债率">{{ financialData.debt_ratio ? financialData.debt_ratio.toFixed(2) + '%' : '-' }}</el-descriptions-item>
        </el-descriptions>
      </el-card>

      <!-- 操作按钮 -->
      <el-card class="actions-card">
        <el-button type="primary" @click="addToWatchlist">
          <el-icon><Star /></el-icon>
          加入自选
        </el-button>
        <el-button type="success" @click="showBuyDialog = true">
          <el-icon><ShoppingCart /></el-icon>
          记录买入
        </el-button>
      </el-card>
    </template>

    <el-empty v-else description="股票不存在" />

    <!-- 买入对话框 -->
    <el-dialog v-model="showBuyDialog" title="记录买入" width="400px">
      <el-form :model="buyForm" label-width="80px">
        <el-form-item label="买入日期">
          <el-date-picker v-model="buyForm.date" type="date" placeholder="选择日期" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item label="买入价格">
          <el-input-number v-model="buyForm.price" :precision="2" :step="0.01" />
        </el-form-item>
        <el-form-item label="买入数量">
          <el-input-number v-model="buyForm.quantity" :min="100" :step="100" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="buyForm.notes" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showBuyDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmBuy">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '@/api'
import KlineChart from '@/components/KlineChart.vue'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const stockInfo = ref(null)
const klineData = ref([])
const financialData = ref(null)
const realtimeQuote = ref(null)
const indicators = ref({
  macd: {},
  kdj: {},
  rsi: {},
  boll: {}
})

const period = ref('日K')
const showMA = ref(true)
const showMA10 = ref(true)
const showMA20 = ref(true)
const showVolume = ref(true)
const showBuyDialog = ref(false)

const buyForm = ref({
  date: new Date().toISOString().split('T')[0],
  price: 0,
  quantity: 100,
  notes: ''
})

const lastKline = computed(() => {
  return klineData.value[klineData.value.length - 1] || null
})

const priceClass = computed(() => {
  if (!lastKline.value) return ''
  return lastKline.value.change_pct >= 0 ? 'up' : 'down'
})

const formatChange = (kline) => {
  if (!kline) return '-'
  const change = kline.close - kline.open
  const pct = kline.change_pct || 0
  const sign = pct >= 0 ? '+' : ''
  return `${sign}${change.toFixed(2)} (${sign}${pct.toFixed(2)}%)`
}

const formatVolume = (vol) => {
  if (!vol) return '-'
  if (vol >= 100000000) return (vol / 100000000).toFixed(2) + '亿'
  if (vol >= 10000) return (vol / 10000).toFixed(2) + '万'
  return vol.toFixed(0)
}

const formatAmount = (val) => {
  if (!val) return '-'
  if (val >= 100000000) return (val / 100000000).toFixed(2) + '亿'
  if (val >= 10000) return (val / 10000).toFixed(2) + '万'
  return val.toFixed(2)
}

const loadStockInfo = async () => {
  loading.value = true
  try {
    const code = route.params.code
    const [info, kline, financial] = await Promise.all([
      api.getStock(code),
      api.getKline(code, { limit: 120 }),
      api.get(`/financial/${code}`).catch(() => null)
    ])
    
    stockInfo.value = info
    klineData.value = (kline.items || []).map(k => ({
      date: k.date,
      open: k.open,
      high: k.high,
      low: k.low,
      close: k.close,
      volume: k.volume
    }))
    financialData.value = financial
    
    // 获取实时行情
    await loadRealtimeQuote()
    
    // 计算技术指标
    calculateIndicators()
    
    // 设置买入价格
    if (lastKline.value) {
      buyForm.value.price = lastKline.value.close
    }
  } catch (error) {
    console.error('加载失败:', error)
    ElMessage.error('加载股票信息失败')
  } finally {
    loading.value = false
  }
}

const loadRealtimeQuote = async () => {
  try {
    const quotes = await api.getRealtimeQuote([route.params.code])
    if (quotes && quotes.length > 0) {
      realtimeQuote.value = quotes[0]
    }
  } catch (e) {
    console.error('获取实时行情失败:', e)
  }
}

let refreshTimer = null
const refreshSeconds = 15

const startAutoRefresh = () => {
  stopAutoRefresh()
  refreshTimer = setInterval(() => {
    loadRealtimeQuote()
  }, refreshSeconds * 1000)
}

const stopAutoRefresh = () => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
}

onUnmounted(() => {
  stopAutoRefresh()
})

const calculateIndicators = () => {
  if (klineData.value.length < 20) return
  
  const closes = klineData.value.map(k => k.close)
  
  // MACD
  indicators.value.macd = calculateMACD(closes)
  
  // KDJ
  indicators.value.kdj = calculateKDJ(klineData.value)
  
  // RSI
  indicators.value.rsi = calculateRSI(closes)
  
  // BOLL
  indicators.value.boll = calculateBOLL(closes)
}

const calculateMACD = (prices, fast=12, slow=26, signal=9) => {
  const ema = (data, period) => {
    const k = 2 / (period + 1)
    let ema = data[0]
    return data.map(v => {
      ema = v * k + ema * (1 - k)
      return ema
    })
  }
  
  const emaFast = ema(prices, fast)
  const emaSlow = ema(prices, slow)
  const dif = dif = emaFast.map((v, i) => v - emaSlow[i])
  const dea = ema(dif, signal)
  const macd = dif.map((v, i) => (v - dea[i]) * 2)
  
  return {
    dif: dif[dif.length - 1],
    dea: dea[dea.length - 1],
    macd: macd[macd.length - 1]
  }
}

const calculateKDJ = (klines, n=9, m1=3, m2=3) => {
  const closes = klines.map(k => k.close)
  const highs = klines.map(k => k.high)
  const lows = klines.map(k => k.low)
  
  const rsv = []
  for (let i = n - 1; i < closes.length; i++) {
    const high = Math.max(...highs.slice(i - n + 1, i + 1))
    const low = Math.min(...lows.slice(i - n + 1, i + 1))
    rsv.push((closes[i] - low) / (high - low) * 100)
  }
  
  let k = 50, d = 50
  const kValues = [], dValues = []
  
  for (const r of rsv) {
    k = (2/3) * k + (1/3) * r
    d = (2/3) * d + (1/3) * k
    kValues.push(k)
    dValues.push(d)
  }
  
  return {
    k: kValues[kValues.length - 1],
    d: dValues[dValues.length - 1],
    j: 3 * kValues[kValues.length - 1] - 2 * dValues[dValues.length - 1]
  }
}

const calculateRSI = (prices, periods = [6, 12, 24]) => {
  const rsi = {}
  
  for (const period of periods) {
    let gains = 0, losses = 0
    for (let i = 1; i < period; i++) {
      const diff = prices[i] - prices[i-1]
      if (diff > 0) gains += diff
      else losses -= diff
    }
    
    const avgGain = gains / period
    const avgLoss = losses / period
    const rs = avgLoss === 0 ? 100 : avgGain / avgLoss
    rsi[`rsi${period}`] = 100 - (100 / (1 + rs))
  }
  
  return rsi
}

const calculateBOLL = (prices, period=20, std=2) => {
  const ma = prices.slice(-period).reduce((a, b) => a + b) / period
  const variance = prices.slice(-period).reduce((sum, p) => sum + Math.pow(p - ma, 2), 0) / period
  const stdDev = Math.sqrt(variance)
  
  return {
    upper: ma + stdDev * std,
    middle: ma,
    lower: ma - stdDev * std
  }
}

const addToWatchlist = async () => {
  try {
    await api.addToWatchlist({
      code: stockInfo.value.code,
      name: stockInfo.value.name,
      status: 'watch',
      select_date: new Date().toISOString().split('T')[0]
    })
    ElMessage.success('已加入自选股')
  } catch (error) {
    ElMessage.error('添加失败')
  }
}

const confirmBuy = async () => {
  try {
    await api.createPosition({
      code: stockInfo.value.code,
      name: stockInfo.value.name,
      buy_date: buyForm.value.date,
      buy_price: buyForm.value.price,
      quantity: buyForm.value.quantity,
      notes: buyForm.value.notes
    })
    ElMessage.success('买入记录已保存')
    showBuyDialog.value = false
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

onMounted(() => {
  loadStockInfo()
  startAutoRefresh()
})

onUnmounted(() => {
  stopAutoRefresh()
})

watch(() => route.params.code, () => {
  loadStockInfo()
})
</script>

<style scoped>
.stock-detail {
  padding: 20px;
}

.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
  color: #999;
}

.loading-container .el-icon {
  margin-right: 10px;
  font-size: 24px;
}

.stock-header {
  margin-bottom: 20px;
}

.stock-name {
  font-size: 24px;
  font-weight: bold;
}

.stock-code {
  color: #666;
  font-size: 14px;
  margin-top: 5px;
}

.stock-industry {
  color: #999;
  font-size: 12px;
  margin-top: 5px;
}

.stock-price {
  font-size: 36px;
  font-weight: bold;
  text-align: center;
}

.stock-price.up { color: #f56c6c; }
.stock-price.down { color: #67c23a; }

.stock-change {
  text-align: center;
  font-size: 16px;
  margin-top: 5px;
}

.stock-change.up { color: #f56c6c; }
.stock-change.down { color: #67c23a; }

.stock-indicators {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.indicator-item {
  display: flex;
  flex-direction: column;
}

.indicator-item .label {
  color: #999;
  font-size: 12px;
}

.indicator-item .value {
  font-size: 14px;
  font-weight: 500;
}

.chart-card {
  margin-bottom: 20px;
}

.chart-controls {
  display: flex;
  gap: 15px;
  align-items: center;
}

.indicators-card {
  margin-bottom: 20px;
}

.indicator-box {
  background: #f5f7fa;
  padding: 15px;
  border-radius: 4px;
}

.indicator-title {
  font-weight: bold;
  margin-bottom: 10px;
  color: #409eff;
}

.indicator-values {
  display: flex;
  flex-direction: column;
  gap: 5px;
  font-size: 12px;
  font-family: monospace;
}

.financial-card,
.actions-card {
  margin-bottom: 20px;
}
</style>
 