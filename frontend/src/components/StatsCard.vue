<template>
  <div class="stats-cards">
    <el-row :gutter="20">
      <el-col :span="span" v-for="(stat, index) in stats" :key="index">
        <div class="stat-card" :class="stat.type">
          <div class="stat-label">{{ stat.label }}</div>
          <div class="stat-value">
            <span class="number">{{ stat.value }}</span>
            <span class="suffix" v-if="stat.suffix">{{ stat.suffix }}</span>
          </div>
          <div class="stat-compare" v-if="stat.compare !== undefined">
            <span :class="stat.compare >= 0 ? 'up' : 'down'">
              {{ stat.compare >= 0 ? '↑' : '↓' }} {{ Math.abs(stat.compare).toFixed(2) }}{{ stat.compareSuffix || '' }}
            </span>
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
defineProps({
  stats: { type: Array, default: () => [] },
  span: { type: Number, default: 6 }
})
</script>

<style scoped>
.stats-cards { margin-bottom: 20px; }
.stat-card {
  background: #fff;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}
.stat-card.profit .stat-value { color: #ef5350; }
.stat-card.loss .stat-value { color: #26a69a; }
.stat-card.neutral .stat-value { color: #409eff; }
.stat-label { font-size: 13px; color: #909399; margin-bottom: 8px; }
.stat-value { font-size: 24px; font-weight: bold; }
.stat-value .suffix { font-size: 14px; margin-left: 2px; }
.stat-compare { font-size: 12px; margin-top: 4px; }
.up { color: #ef5350; }
.down { color: #26a69a; }
</style>
