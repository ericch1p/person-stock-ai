<template>
  <el-config-provider :locale="zhCn">
    <div class="app-container">
      <el-container>
        <!-- 侧边栏 -->
        <el-aside width="200px" class="sidebar">
          <div class="logo">
            <h2>📈 选股系统</h2>
          </div>
          <el-menu
            :default-active="$route.path"
            router
            class="sidebar-menu"
          >
            <el-menu-item index="/selection">
              <el-icon><Search /></el-icon>
              <span>选股</span>
            </el-menu-item>
            <el-menu-item index="/watchlist">
              <el-icon><Star /></el-icon>
              <span>自选股</span>
            </el-menu-item>
            <el-menu-item index="/positions">
              <el-icon><Box /></el-icon>
              <span>持仓</span>
            </el-menu-item>
            <el-menu-item index="/backtest">
              <el-icon><DataLine /></el-icon>
              <span>回测</span>
            </el-menu-item>
            <el-menu-item index="/strategies">
              <el-icon><Setting /></el-icon>
              <span>策略</span>
            </el-menu-item>
            <el-menu-item index="/push">
              <el-icon><Bell /></el-icon>
              <span>推送</span>
            </el-menu-item>
          </el-menu>
        </el-aside>

        <!-- 主内容 -->
        <el-container>
          <el-header class="header">
            <h1>{{ pageTitle }}</h1>
            <div class="header-actions">
              <el-button @click="refreshData" :loading="loading">
                <el-icon><Refresh /></el-icon>
                刷新数据
              </el-button>
            </div>
          </el-header>
          
          <el-main class="main-content">
            <router-view v-if="!loading" />
          </el-main>
        </el-container>
      </el-container>
    </div>
  </el-config-provider>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'

const route = useRoute()
const loading = ref(false)

const pageTitle = computed(() => {
  const titles = {
    '/selection': '股票筛选',
    '/watchlist': '自选股池',
    '/positions': '持仓管理',
    '/backtest': '策略回测',
    '/strategies': '策略管理',
    '/push': '推送配置'
  }
  return titles[route.path] || 'A股智能选股系统'
})

const refreshData = async () => {
  loading.value = true
  try {
    const response = await fetch('/api/stocks/update-all', { method: 'POST' })
    const data = await response.json()
    ElMessage.success(`数据更新完成：${data.count} 只股票`)
  } catch (error) {
    ElMessage.error('数据更新失败')
  } finally {
    loading.value = false
  }
}
</script>

<style lang="scss" scoped>
.app-container {
  height: 100vh;
}

.sidebar {
  background: #001529;
  
  .logo {
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(255, 255, 255, 0.05);
    
    h2 {
      color: #fff;
      margin: 0;
      font-size: 16px;
    }
  }
  
  .sidebar-menu {
    border-right: none;
    background: transparent;
    
    .el-menu-item {
      color: rgba(255, 255, 255, 0.7);
      
      &:hover, &.is-active {
        background: rgba(255, 255, 255, 0.1);
        color: #fff;
      }
    }
  }
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  border-bottom: 1px solid #e8e8e8;
  
  h1 {
    margin: 0;
    font-size: 18px;
  }
  
  .header-actions {
    display: flex;
    gap: 10px;
  }
}

.main-content {
  background: #f5f7fa;
  padding: 20px;
}
</style>
