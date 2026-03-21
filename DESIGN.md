# A股智能选股跟踪系统 — 技术设计文档

## 一、项目定位

一套本地化运行的A股股票筛选、跟踪、回测、优化的闭环系统。

**核心目标：** 发现有效选股策略 → 跟踪验证 → 持续优化

---

## 二、系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        前端 (Web UI)                            │
│                   Vue 3 + Element Plus + ECharts               │
├─────────────────────────────────────────────────────────────────┤
│                        后端服务 (API)                           │
│                    FastAPI + Uvicorn (ASGI)                   │
├──────────────────┬──────────────────┬───────────────────────────┤
│   选股服务        │   回测服务       │   数据服务                │
│   策略执行        │   回测引擎       │   数据拉取/存储           │
├──────────────────┴──────────────────┴───────────────────────────┤
│                        数据层                                   │
│                    SQLite + Pandas                            │
├─────────────────────────────────────────────────────────────────┤
│                        数据源层                                 │
│              akshare (主) + pytdx (实时)                      │
└─────────────────────────────────────────────────────────────────┘
```

---

## 三、数据层设计

### 3.1 数据源策略

| 优先级 | 数据源 | 用途 | 说明 |
|--------|--------|------|------|
| **主数据源** | akshare | 历史数据、财务数据、资金流向、龙虎榜 | 数据全，覆盖广 |
| **实时补充** | pytdx | 当日实时行情 | 速度快，作为备份 |
| **兜底** | efinance | 特定数据补充 | 特定场景使用 |

### 3.2 本地存储

```
data/
├── stock.db              # SQLite 主数据库
├── cache/                # 缓存目录
│   ├── daily/           # 日线数据缓存
│   └── financial/       # 财务数据缓存
└── logs/                # 日志目录
```

### 3.3 数据库表结构

| 表名 | 用途 | 主要字段 |
|------|------|----------|
| `stocks` | 股票基础信息 | code, name, industry, market, list_date |
| `daily_kline` | 日线行情 | code, date, open, high, low, close, volume, amount |
| `financial` | 财务数据 | code, date, pe, pb, roe, revenue_growth, net_profit_growth |
| `money_flow` | 资金流向 | code, date, north_money, main_net_inflow |
| `watchlist` | 自选股/跟踪池 | id, code, status, added_date, notes |
| `positions` | 持仓记录 | id, code, buy_date, buy_price, quantity, status |
| `trades` | 交易日志 | id, date, action, code, price, quantity, reason |
| `strategies` | 策略定义 | id, name, type, params, description, enabled |
| `backtest_results` | 回测结果 | id, strategy_id, code, period, return_rate, sharpe, max_drawdown |
| `push_config` | 推送配置 | id, channel, webhook_url, push_rules, enabled |

---

## 四、核心功能模块

### 4.1 选股模块

**策略类型：**
- 技术面：均线金叉/死叉、MACD、量价突破、布林带、动量
- 基本面：PE、PB、ROE、净利润增速、营收增长
- 资金面：北向资金、主力净流入、换手率
- 组合策略：支持多条件叠加、权重配置

### 4.2 跟踪模块

- 自选股池管理
- 持仓记录（买入/卖出）
- 操作日志
- K线查看（均线、成交量）

### 4.3 回测模块

- 历史回测
- 策略对比
- 统计指标（收益率、夏普比率、最大回撤）
- 收益曲线可视化

### 4.4 策略优化

- 策略评分
- 参数调优
- 有效性分析

### 4.5 推送模块

- 钉钉机器人推送
- 定时推送（收盘后）
- 事件触发推送

---

## 五、技术栈

| 组件 | 技术选型 | 版本 |
|------|----------|------|
| **后端** | Python + FastAPI | 3.10+ |
| **数据库** | SQLite | - |
| **数据处理** | pandas + numpy | - |
| **数据获取** | akshare + pytdx + efinance | - |
| **前端** | Vue 3 + Vite | 3.x |
| **UI组件** | Element Plus | 2.x |
| **图表** | ECharts + klinecharts | - |
| **任务调度** | APScheduler | - |
| **推送** | requests | - |

---

## 六、项目目录结构

```
a-stock-system/
├── backend/                    # 后端
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI 入口
│   │   ├── config.py         # 配置管理
│   │   ├── database.py       # 数据库连接
│   │   ├── models/           # 数据模型
│   │   │   ├── __init__.py
│   │   │   ├── stock.py
│   │   │   ├── kline.py
│   │   │   ├── financial.py
│   │   │   ├── strategy.py
│   │   │   └── position.py
│   │   ├── schemas/          # Pydantic 模型
│   │   │   ├── __init__.py
│   │   │   └── stock.py
│   │   ├── routers/          # API 路由
│   │   │   ├── __init__.py
│   │   │   ├── stocks.py
│   │   │   ├── selection.py
│   │   │   ├── backtest.py
│   │   │   ├── strategy.py
│   │   │   ├── position.py
│   │   │   └── push.py
│   │   ├── services/         # 业务逻辑
│   │   │   ├── __init__.py
│   │   │   ├── data_service.py      # 数据服务
│   │   │   ├── selection_service.py # 选股服务
│   │   │   ├── backtest_service.py  # 回测服务
│   │   │   └── push_service.py      # 推送服务
│   │   └── tasks/            # 定时任务
│   │       ├── __init__.py
│   │       └── scheduler.py
│   ├── requirements.txt
│   └── run.sh                # 启动脚本
├── frontend/                  # 前端
│   ├── src/
│   │   ├── api/             # API 调用
│   │   ├── components/      # 组件
│   │   ├── views/           # 页面
│   │   ├── stores/          # 状态管理
│   │   ├── router/          # 路由
│   │   └── App.vue
│   ├── package.json
│   └── vite.config.js
├── data/                      # 数据目录
│   ├── stock.db
│   └── logs/
├── scripts/                   # 脚本
│   ├── init_db.py           # 初始化数据库
│   └── update_data.py       # 更新数据
├── tests/                     # 测试
└── README.md
```

---

## 七、实施计划

### Phase 1 — MVP (2-3周)
- [x] 数据层设计
- [ ] 数据获取 + 本地存储
- [ ] 基础选股功能
- [ ] Web界面基础框架
- [ ] 钉钉推送基础功能

### Phase 2 — 跟踪 (2-3周)
- [ ] 自选股池管理
- [ ] 持仓记录 + 交易日志
- [ ] K线展示
- [ ] 股票详情页

### Phase 3 — 回测 (2-3周)
- [ ] 回测引擎
- [ ] 回测结果展示
- [ ] 策略有效性评估
- [ ] 策略与持仓关联

### Phase 4 — 优化 (持续迭代)
- [ ] 策略参数优化
- [ ] 策略对比分析
- [ ] 趋势发现

---

## 八、版本记录

| 版本 | 日期 | 说明 |
|------|------|------|
| v0.1 | 2026-03-21 | 初始设计方案 |
