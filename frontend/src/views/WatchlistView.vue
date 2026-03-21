<template>
  <div class="watchlist-view">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>自选股池</span>
          <el-button type="primary" @click="refresh">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>
      
      <el-table :data="watchlist" stripe v-loading="loading">
        <el-table-column prop="code" label="代码" width="100" />
        <el-table-column prop="name" label="名称" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)">{{ statusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="select_date" label="选入日期" width="120" />
        <el-table-column prop="notes" label="备注" min-width="200" show-overflow-tooltip />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="toPosition(row)">买入</el-button>
            <el-button size="small" type="danger" @click="remove(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'
import api from '@/api'

const router = useRouter()
const loading = ref(false)
const watchlist = ref([])

const statusType = (status) => {
  const types = { watch: 'info', hold: 'success', sell: 'warning', abandon: 'danger' }
  return types[status] || 'info'
}

const statusText = (status) => {
  const texts = { watch: '观察', hold: '持仓', sell: '已卖出', abandon: '放弃' }
  return texts[status] || status
}

const loadData = async () => {
  loading.value = true
  try {
    const res = await api.getWatchlist()
    watchlist.value = res.items || []
  } catch (error) {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

const refresh = () => loadData()

const toPosition = (stock) => {
  router.push({ path: '/positions', query: { code: stock.code, name: stock.name } })
}

const remove = async (stock) => {
  ElMessage.info('删除功能待实现')
}

onMounted(loadData)
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
