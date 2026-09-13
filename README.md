# BilibiliMonitor

本地轻量哔哩哔哩视频与 UP 主数据监控工具。后端自动采集快照，前端展示当前指标、趋势、采集记录，并支持 CSV/JSON 导出本地历史数据。

## 本地启动

### 后端

需要 Python 3.11+：

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item ..\.env.example ..\.env
uvicorn app.main:app --reload --port 8000
```

### 前端

```powershell
cd frontend
npm install
npm run dev
```

打开 http://localhost:5173 。后端 API 文档：http://localhost:8000/docs 。

完整项目文档见 `docs/README.md`，包括产品需求、技术架构、版本规划、当前状态、变更记录和测试计划。

## 使用 VS Code 启动

用 VS Code 打开项目根目录 `D:\projects\BilibiliMonitor`，按 `Ctrl+Shift+P`，执行“Tasks: Run Task”，选择 `BilibiliMonitor: 启动全部`。也可以打开“运行和调试”面板，选择同名配置后启动。

启动后访问 http://localhost:5173 。

公开接口可能受哔哩哔哩风控影响。项目当前监控 UP 主的粉丝、投稿数和关注数；如需为其他受限公开接口配置本地完整 Cookie，请填写根目录 `.env` 的 `BILIBILI_COOKIE`，不要提交或分享该文件。详见 [故障排查](docs/troubleshooting.md)。
