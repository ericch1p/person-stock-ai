<template>
  <div class="push-view">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>钉钉推送配置</span>
          <el-button type="primary" @click="showAddDialog">
            <el-icon><Plus /></el-icon>
            添加配置
          </el-button>
        </div>
      </template>
      
      <el-table :data="configs" stripe v-loading="loading">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="配置名称" width="150" />
        <el-table-column prop="channel" label="渠道" width="100">
          <template #default="{ row }">
            <el-tag>{{ row.channel === 'dingtalk' ? '钉钉' : row.channel }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="webhook_url" label="Webhook" min-width="200" show-overflow-tooltip />
        <el-table-column prop="enabled" label="状态" width="80">
          <template #default="{ row }">
            <el-switch v-model="row.enabled" @change="toggleEnabled(row)" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button size="small" @click="test(row)">测试</el-button>
            <el-button size="small" type="danger" @click="remove(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 添加对话框 -->
    <el-dialog v-model="dialogVisible" title="添加钉钉配置" width="500px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="配置名称">
          <el-input v-model="form.name" placeholder="如：我的钉钉" />
        </el-form-item>
        <el-form-item label="Webhook地址">
          <el-input v-model="form.webhook_url" type="textarea" :rows="2" placeholder="https://oapi.dingtalk.com/robot/send?access_token=xxx" />
        </el-form-item>
        <el-form-item label="加签密钥">
          <el-input v-model="form.secret" placeholder="密钥，用于签名校验（可选）" />
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
import api from '@/api'

const loading = ref(false)
const configs = ref([])
const dialogVisible = ref(false)

const form = reactive({
  name: '',
  channel: 'dingtalk',
  webhook_url: '',
  secret: '',
  enabled: true
})

const loadData = async () => {
  loading.value = true
  try {
    const res = await api.getPushConfigs({ enabled_only: false })
    configs.value = res.items || []
  } catch (error) {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

const showAddDialog = () => {
  Object.assign(form, { name: '', channel: 'dingtalk', webhook_url: '', secret: '', enabled: true })
  dialogVisible.value = true
}

const submit = async () => {
  try {
    await api.createPushConfig(form)
    ElMessage.success('保存成功')
    dialogVisible.value = false
    loadData()
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

const toggleEnabled = async (row) => {
  try {
    await api.updatePushConfig(row.id, { enabled: row.enabled ? 1 : 0 })
    ElMessage.success(row.enabled ? '已启用' : '已禁用')
  } catch (error) {
    ElMessage.error('操作失败')
    row.enabled = !row.enabled
  }
}

const test = async (row) => {
  ElMessage.info('测试消息发送功能开发中...')
}

const remove = async (row) => {
  ElMessage.info('删除功能开发中...')
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
