# A股智能选股跟踪系统

本地化运行的A股股票筛选、跟踪、回测、优化的闭环系统。

## 功能特性

- 📊 **智能选股** - 技术面、基本面、资金面多维度筛选
- 🎯 **股票跟踪** - 自选股池、持仓管理、操作日志
- 📈 **策略回测** - 历史验证、收益分析、有效性评估
- 🔔 **钉钉推送** - 选股结果、持仓报告、定时提醒

## 技术栈

- **后端**: Python + FastAPI + SQLAlchemy + SQLite
- **前端**: Vue 3 + Element Plus + ECharts
- **数据源**: akshare + pytdx

## 快速开始

### 1. 安装后端依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 初始化数据库

```bash
cd ../scripts
python init_db.py
```

### 3. 启动后端服务

```bash
cd ../backend
uvicorn app.main:app --reload
```

后端服务地址: http://localhost:8000

### 4. 启动前端服务

```bash
cd frontend
npm install
npm run dev
```

前端地址: http://localhost:5173

### 5. 更新股票数据

```bash
cd scripts
python update_data.py
```

## 项目结构

```
a-stock-system/
├── backend/                 # 后端
│   ├── app/
│   │   ├── models/         # 数据模型
│   │   ├── schemas/        # Pydantic模型
│   │   ├── routers/       # API路由
│   │   ├── services/      # 业务逻辑
│   │   └── tasks/         # 定时任务
│   └── requirements.txt
├── frontend/                # 前端
│   ├── src/
│   │   ├── views/         # 页面组件
│   │   ├── api/           # API调用
│   │   └── router/        # 路由配置
│   └── package.json
├── data/                    # 数据目录
├── scripts/                  # 工具脚本
└── README.md
```

## 钉钉机器人配置

1. 在钉钉群中添加自定义机器人
2. 复制 Webhook 地址
3. 如启用加签，复制密钥
4. 在系统的「推送配置」页面添加配置

## 定时任务

- **16:00** - 每日更新行情数据
- **16:30** - 每日选股并推送
- **周一 09:00** - 发送每周持仓报告

## 许可证

MIT
