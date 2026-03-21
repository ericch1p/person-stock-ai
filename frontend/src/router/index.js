import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/selection'
  },
  {
    path: '/selection',
    name: 'Selection',
    component: () => import('@/views/SelectionView.vue')
  },
  {
    path: '/watchlist',
    name: 'Watchlist',
    component: () => import('@/views/WatchlistView.vue')
  },
  {
    path: '/positions',
    name: 'Positions',
    component: () => import('@/views/PositionsView.vue')
  },
  {
    path: '/backtest',
    name: 'Backtest',
    component: () => import('@/views/BacktestView.vue')
  },
  {
    path: '/strategies',
    name: 'Strategies',
    component: () => import('@/views/StrategiesView.vue')
  },
  {
    path: '/push',
    name: 'Push',
    component: () => import('@/views/PushView.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
