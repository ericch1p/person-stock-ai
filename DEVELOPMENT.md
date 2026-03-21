# 开发流程规范

## 核心原则
**每一项代码修改必须经过测试才能提交。**

---

## 开发流程

### 1. 创建功能分支
```bash
git checkout -b feature/功能名称
# 例如: git checkout -b feature/kline-chart
```

### 2. 开发与本地测试
- 编写代码
- **必须测试通过**:
  - Python模块: `python -c "from app.module import something; print('OK')"`
  - 完整启动: `cd backend && python -m uvicorn app.main:app --port 8000`
  - 前端: `cd frontend && npm run dev`

### 3. 提交代码
```bash
git add .
git commit -m "feat: 描述"
```

### 4. 推送到远程
```bash
git push -u origin feature/功能名称
```

---

## 测试检查清单

### 后端测试
- [ ] 语法检查: `python -m py_compile app/xxx.py`
- [ ] 模块导入: `python -c "from app.xxx import xxx"`
- [ ] 服务启动: `uvicorn app.main:app --port 8000`
- [ ] API测试: `curl http://localhost:8000/health`

### 前端测试
- [ ] 依赖安装: `npm install`
- [ ] 编译检查: `npm run build` (可选)
- [ ] 开发服务器: `npm run dev`
- [ ] 浏览器访问: http://localhost:5173

### 提交前检查
- [ ] 代码已测试通过
- [ ] 无语法错误
- [ ] 无遗留的调试代码(console.log, print等)
- [ ] commit信息清晰描述改动

---

## 常用命令

### 启动后端
```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 启动前端
```bash
cd frontend
npm run dev
```

### 查看日志
```bash
# 后端日志
cat backend.log

# 前端日志
cat frontend.log
```

### 重启服务
```bash
# 杀掉进程
pkill -f uvicorn
pkill -f vite

# 重新启动
cd backend && python -m uvicorn app.main:app --port 8000 &
cd frontend && npm run dev &
```

---

## Git 工作流

```
main (稳定分支)
    │
    ├── feature/kline-chart (新功能)
    ├── feature/equity-curve (新功能)
    └── fix/bug-fix (修复)
```

### 合并不冲突时
```bash
git checkout main
git merge feature/功能名
git push
```

---

## 注意事项

1. **不要直接在 main 分支开发**
2. **测试通过后再 commit**
3. **保持 commit 粒度适中** (一个功能一个commit)
4. **网络问题时可先 commit，后续再 push**
