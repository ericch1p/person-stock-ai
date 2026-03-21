<template>
  <div class="positions-view">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>持仓管理</span>
          <el-button type="primary" @click="showAddDialog">
            <el-icon><Plus /></el-icon>
            记录买入
          </el-button>
        </div>
      </template>
      
      <el-table :data="positions" stripe v-loading="loading">
        <el-table-column prop="code" label="代码" width="100" />
        <el-table-column prop="name" label="名称" width="120" />
        <el-table-column prop="buy_date" label="买入日期" width="120" />
        <el-table-column prop="buy_price" label="买入价" width="100">
          <template #default="{ row }">
            {{ row.buy_price?.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="quantity" label="数量" width="100" />
        <el-table-column prop="buy_amount" label="买入金额" width="120">
          <template #default="{ row }">
            {{ row.buy_amount?.toFixed(2) }}
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
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useRoute } from 'vue-router'
import api from '@/api'

const route = useRoute()
const loading = ref(false)
const positions = ref([])
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
  } catch (error) {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
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

onMounted(loadData)
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
