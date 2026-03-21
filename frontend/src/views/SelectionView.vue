<template>
  <div class="selection-view">
    <!-- 选股条件 -->
    <el-card class="criteria-card">
      <template #header>
        <div class="card-header">
          <span>选股条件</span>
          <el-button type="primary" @click="runSelection" :loading="loading">
            <el-icon><Search /></el-icon>
            执行选股
          </el-button>
        </div>
      </template>
      
      <el-form :model="criteria" label-width="120px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-divider content-position="left">技术面</el-divider>
            <el-form-item label="均线金叉">
              <el-switch v-model="criteria.ma_golden_cross" />
            </el-form-item>
            <el-form-item label="均线多头">
              <el-switch v-model="criteria.ma_bullish_arrangement" />
            </el-form-item>
            <el-form-item label="MACD金叉">
              <el-switch v-model="criteria.macd_golden_cross" />
            </el-form-item>
            <el-form-item label="放量突破">
              <el-switch v-model="criteria.volume_breakout" />
            </el-form-item>
          </el-col>
          
          <el-col :span="12">
            <el-divider content-position="left">基本面</el-divider>
            <el-form-item label="PE范围">
              <el-input-number v-model="criteria.pe_min" :min="0" :step="5" style="width: 100px" />
              <span class="ml-5 mr-5">~</span>
              <el-input-number v-model="criteria.pe_max" :min="0" :step="5" style="width: 100px" />
            </el-form-item>
            <el-form-item label="ROE下限(%)">
              <el-input-number v-model="criteria.roe_min" :min="0" :max="100" :step="1" />
            </el-form-item>
            <el-form-item label="营收增速(%)">
              <el-input-number v-model="criteria.revenue_growth_min" :min="0" :step="5" />
            </el-form-item>
            <el-form-item label="净利润增速(%)">
              <el-input-number v-model="criteria.net_profit_growth_min" :min="0" :step="5" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row>
          <el-col :span="24">
            <el-form-item label="其他">
              <el-checkbox v-model="criteria.exclude_st">排除ST股票</el-checkbox>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
    </el-card>
    
    <!-- 选股结果 -->
    <el-card class="result-card">
      <template #header>
        <div class="card-header">
          <span>选股结果</span>
          <span v-if="results.length">共 {{ results.length }} 只</span>
        </div>
      </template>
      
      <el-table :data="results" stripe style="width: 100%" v-loading="loading">
        <el-table-column prop="code" label="代码" width="100" />
        <el-table-column prop="name" label="名称" width="100" />
        <el-table-column prop="industry" label="行业" width="120" />
        <el-table-column prop="close" label="现价" width="80">
          <template #default="{ row }">
            {{ row.close?.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="change_pct" label="涨跌幅" width="100">
          <template #default="{ row }">
            <span :class="row.change_pct >= 0 ? 'up' : 'down'">
              {{ row.change_pct >= 0 ? '+' : '' }}{{ row.change_pct?.toFixed(2) }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="pe" label="PE" width="80">
          <template #default="{ row }">
            {{ row.pe?.toFixed(1) || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="roe" label="ROE" width="80">
          <template #default="{ row }">
            {{ row.roe ? row.roe.toFixed(1) + '%' : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="match_score" label="匹配度" width="80">
          <template #default="{ row }">
            <el-tag type="success">{{ row.match_score?.toFixed(0) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="match_reasons" label="匹配原因" min-width="200">
          <template #default="{ row }">
            <el-tag v-for="reason in row.match_reasons" :key="reason" size="small" class="mr-5">
              {{ reason }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="addToWatch(row)">加自选</el-button>
            <el-button size="small" type="primary" @click="showKline(row)">K线</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '@/api'

const router = useRouter()

const loading = ref(false)
const results = ref([])

const criteria = reactive({
  exclude_st: true,
  ma_golden_cross: false,
  ma_bullish_arrangement: false,
  macd_golden_cross: false,
  volume_breakout: false,
  pe_min: null,
  pe_max: null,
  roe_min: null,
  revenue_growth_min: null,
  net_profit_growth_min: null
})

const runSelection = async () => {
  loading.value = true
  try {
    // 清理空值
    const params = {}
    Object.keys(criteria).forEach(key => {
      if (criteria[key] !== null && criteria[key] !== false && criteria[key] !== '') {
        params[key] = criteria[key]
      }
    })
    
    const res = await api.runSelection(params)
    results.value = res.items || []
    ElMessage.success(`选股完成，共 ${results.value.length} 只股票符合条件`)
  } catch (error) {
    ElMessage.error('选股失败')
  } finally {
    loading.value = false
  }
}

const addToWatch = async (stock) => {
  try {
    await api.addToWatchlist({
      code: stock.code,
      name: stock.name,
      select_date: new Date().toISOString().split('T')[0]
    })
    ElMessage.success('已添加到自选股')
  } catch (error) {
    ElMessage.error('添加失败')
  }
}

const showKline = (stock) => {
  router.push(`/stock/${stock.code}?name=${encodeURIComponent(stock.name)}`)
}
</script>

<style lang="scss" scoped>
.selection-view {
  .criteria-card {
    margin-bottom: 20px;
  }
  
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .up {
    color: #f56c6c;
  }
  
  .down {
    color: #67c23a;
  }
  
  .ml-5 {
    margin-left: 5px;
  }
  
  .mr-5 {
    margin-right: 5px;
  }
}
</style>
