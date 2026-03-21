import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000
})

// 响应拦截
api.interceptors.response.use(
  response => response.data,
  error => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

export default {
  // 股票
  getStocks: (params) => api.get('/stocks/', { params }),
  getStock: (code) => api.get(`/stocks/${code}`),
  getKline: (code, params) => api.get(`/stocks/${code}/kline`, { params }),
  updateStocks: () => api.post('/stocks/update-all'),
  
  // 实时行情
  getRealtimeQuote: (codes) => api.post('/stocks/realtime', { codes }),
  
  // 选股
  runSelection: (criteria) => api.post('/selection/run', criteria),
  getSelectionStrategies: () => api.get('/selection/strategies'),
  
  // 策略
  getStrategies: (params) => api.get('/strategies/', { params }),
  getStrategy: (id) => api.get(`/strategies/${id}`),
  createStrategy: (data) => api.post('/strategies/', data),
  updateStrategy: (id, data) => api.put(`/strategies/${id}`, data),
  deleteStrategy: (id) => api.delete(`/strategies/${id}`),
  
  // 回测
  runBacktest: (data) => api.post('/backtest/run', data),
  getBacktestResults: (params) => api.get('/backtest/results', { params }),
  
  // 持仓
  getPositions: (params) => api.get('/positions/', { params }),
  getPositionsProfit: () => api.get('/positions/profit'),
  createPosition: (data) => api.post('/positions/', data),
  updatePosition: (id, data) => api.put(`/positions/${id}`, data),
  
  // 自选股
  getWatchlist: (params) => api.get('/watchlist/', { params }),
  addToWatchlist: (data) => api.post('/watchlist/', data),
  
  // 交易日志
  getTrades: (params) => api.get('/trades/', { params }),
  
  // 推送
  getPushConfigs: (params) => api.get('/push/configs', { params }),
  createPushConfig: (data) => api.post('/push/configs', data),
  updatePushConfig: (id, data) => api.put(`/push/configs/${id}`, data)
}
