<template>
  <div class="stock-detail">
    <el-page-header @back="goBack" :content="stockName || stockCode" />
    
    <el-row :gutter="20" class="mt-20">
      <el-col :span="16">
        <el-card>
          <KlineChart :stock-code="stockCode" :stock-name="stockName" />
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card class="info-card">
          <template #header>
            <span>基本信息</span>
          </template>
          <el-descriptions :column="1" border size="small">
            <el-descriptions-item label="股票代码">{{ stockInfo.code }}</el-descriptions-item>
            <el-descriptions-item label="股票名称">{{ stockInfo.name }}</el-descriptions-item>
            <el-descriptions-item label="所属行业">{{ stockInfo.industry || '-' }}</el-descriptions-item>
            <el-descriptions-item label="市场">{{ stockInfo.market || '-' }}</el-descriptions-item>
          </el-descriptions>
        </el-card>
        
        <el-card class="info-card mt-20" v-if="financial">
          <template #header>
            <span>财务指标</span>
          </template>
          <el-descriptions :column="1" border size="small">
            <el-descriptions-item label="市盈率(PE)">{{ financial.pe?.toFixed(2) || '-' }}</el-descriptions-item>
            <el-descriptions-item label="市净率(PB)">{{ financial.pb?.toFixed(2) || '-' }}</el-descriptions-item>
            <el-descriptions-item label="净资产收益率(ROE)">{{ financial.roe ? financial.roe.toFixed(2) + '%' : '-' }}</el-descriptions-item>
            <el-descriptions-item label="净利润增速">{{ financial.net_profit_growth ? financial.net_profit_growth.toFixed(2) + '%' : '-' }}</el-descriptions-item>
            <el-descriptions-item label="营收增速">{{ financial.revenue_growth ? financial.revenue_growth.toFixed(2) + '%' : '-' }}</el-descriptions-item>
          </el-descriptions>
        </el-card>
        
        <el-card class="info-card mt-20">
          <template #header>
            <span>操作</span>
          </template>
          <el-button type="primary" @click="addToWatch">加入自选</el-button>
          <el-button type="success" @click="showBuyDialog = true">记录买入</el-button>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 买入对话框 -->
    <el-dialog v-model="showBuyDialog" title="记录买入" width="400px">
      <el-form :model="buyForm" label-width="100px">
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
        <el-button @click="showBuyDialog = false">取消</el-button>
        <el-button type="primary" @click="submitBuy">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '@/api'
import KlineChart from '@/components/KlineChart.vue'

const route = useRoute()
const router = useRouter()

const stockCode = route.params.code || route.query.code
const stockName = route.params.name || route.query.name

const stockInfo = ref({})
const financial = ref(null)
const showBuyDialog = ref(false)

const buyForm = reactive({
  code: stockCode,
  name: stockName,
  buy_date: new Date().toISOString().split('T')[0],
  buy_price: 0,
  quantity: 100,
  notes: ''
})

const loadStockInfo = async () => {
  try {
    const res = await api.getStock(stockCode)
    stockInfo.value = res || { code: stockCode, name: stockName }
  } catch (e) {
    stockInfo.value = { code: stockCode, name: stockName }
  }
}

const goBack = () => router.back()

const addToWatch = async () => {
  try {
    await api.addToWatchlist({ code: stockCode, name: stockName })
    ElMessage.success('已添加自选')
  } catch (e) {
    ElMessage.error('添加失败')
  }
}

const submitBuy = async () => {
  try {
    await api.createPosition(buyForm)
    ElMessage.success('记录成功')
    showBuyDialog.value = false
  } catch (e) {
    ElMessage.error('记录失败')
  }
}

onMounted(loadStockInfo)
</script>

<style scoped>
.mt-20 { margin-top: 20px; }
.info-card { font-size: 13px; }
</style>
