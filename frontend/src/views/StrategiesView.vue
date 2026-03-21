<template>
  <div class="strategies-view">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>策略管理</span>
          <el-button type="primary" @click="showAddDialog">
            <el-icon><Plus /></el-icon>
            新建策略
          </el-button>
        </div>
      </template>
      
      <el-table :data="strategies" stripe v-loading="loading">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="策略名称" width="150" />
        <el-table-column prop="type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="typeColor(row.type)">{{ typeText(row.type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="win_rate" label="历史胜率" width="100">
          <template #default="{ row }">
            {{ row.win_rate ? row.win_rate.toFixed(1) + '%' : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="total_trades" label="交易次数" width="100" />
        <el-table-column prop="enabled" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.enabled ? 'success' : 'info'">
              {{ row.enabled ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="backtest(row)">回测</el-button>
            <el-button size="small" @click="edit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="remove(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑策略' : '新建策略'" width="500px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="策略名称">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="form.type">
            <el-option label="技术面" value="technical" />
            <el-option label="基本面" value="fundamental" />
            <el-option label="资金面" value="money" />
            <el-option label="组合策略" value="composite" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" />
        </el-form-item>
        <el-form-item label="启用">
          <el-switch v-model="form.enabled" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import api from '@/api'

const router = useRouter()
const loading = ref(false)
const strategies = ref([])
const dialogVisible = ref(false)
const isEdit = ref(false)

const form = reactive({
  id: null,
  name: '',
  type: 'technical',
  description: '',
  enabled: true
})

const typeColor = (type) => {
  const colors = { technical: 'primary', fundamental: 'success', money: 'warning', composite: 'info' }
  return colors[type] || 'info'
}

const typeText = (type) => {
  const texts = { technical: '技术面', fundamental: '基本面', money: '资金面', composite: '组合' }
  return texts[type] || type
}

const loadData = async () => {
  loading.value = true
  try {
    const res = await api.getStrategies({ enabled_only: false })
    strategies.value = res.items || []
  } catch (error) {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

const showAddDialog = () => {
  isEdit.value = false
  Object.assign(form, { id: null, name: '', type: 'technical', description: '', enabled: true })
  dialogVisible.value = true
}

const edit = (row) => {
  isEdit.value = true
  Object.assign(form, row)
  dialogVisible.value = true
}

const submit = async () => {
  try {
    if (isEdit.value) {
      await api.updateStrategy(form.id, form)
    } else {
      await api.createStrategy(form)
    }
    ElMessage.success('保存成功')
    dialogVisible.value = false
    loadData()
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

const backtest = (row) => {
  router.push({ path: '/backtest', query: { strategy_id: row.id } })
}

const remove = async (row) => {
  await api.deleteStrategy(row.id)
  ElMessage.success('删除成功')
  loadData()
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
