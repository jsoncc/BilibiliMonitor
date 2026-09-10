# API

启动后访问 `/docs` 查看 OpenAPI。

主要接口：

- `POST /api/targets/resolve`：解析视频或 UP 主输入。
- `POST /api/targets/preview`：获取搜索预览，不创建监控对象。
- `POST /api/targets`：创建或恢复监控对象。
- `POST /api/targets/view-once`：仅获取一次当前数据，不创建监控对象。
- `GET /api/targets`：获取当前监控对象。
- `GET /api/targets/history`：获取已停止监控的历史对象。
- `DELETE /api/targets/{id}`：停止监控但保留历史快照。
- `POST /api/targets/{id}/collect`：立即采集一次。
- `PATCH /api/targets/{id}/settings`：修改采集间隔。
- `GET /api/videos/{id}/trend`：查询视频趋势，默认 168 小时，最多 720 小时。
- `GET /api/uploaders/{id}/trend`：查询 UP 主趋势，默认 168 小时，最多 720 小时。
- `GET /api/health`：检查服务状态。

对象响应包含 `last_success_at`、`last_error_at`、`next_collect_at`、`last_error` 和 `active` 状态字段。
