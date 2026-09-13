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
- `PATCH /api/targets/{id}/focus`：保存对象专注模式指标，正文为 `{"metrics":["view_count","three_combo_count"]}`；视频支持播放、互动、在线及三连总量，UP 主支持粉丝、投稿、关注。
- `GET /api/videos/{id}/trend?hours=24|168|720`：查询视频趋势，默认 168 小时，最多 720 小时；前端按单指标展示。
- `GET /api/uploaders/{id}/trend?hours=24|168|720`：查询 UP 主趋势，默认 168 小时，最多 720 小时；前端按单指标展示。
- `GET /api/media/image?url=...`：受限代理 B 站图片，统一使用 HTTPS、B 站图片域名白名单、10 秒超时和 8MB 大小限制；不允许代理其他域名。
- `GET /api/system/summary`：获取本地数据库容量、对象数量、视频/UP 主快照数量和存在最近错误的任务数。
- `GET /api/targets/{id}/logs?limit=20`：查询对象最近采集记录，`limit` 范围为 1–100。
- `GET /api/exports/targets/{id}?format=csv|json&hours=all|24|168|720`：即时导出单个对象的本地快照。
- `GET /api/exports?format=csv|json&hours=all|24|168|720`：即时导出全部当前与历史对象的本地快照。

前端趋势范围对应 24 小时、7 天和 30 天。响应包含真实采集时间点；无点或只有一个点时由前端显示原因和等待下一次采集提示。
- `GET /api/health`：检查服务状态。

对象响应包含 `last_success_at`、`last_error_at`、`next_collect_at`、`last_error`、`active` 和 `focus_metrics` 状态字段。UP 主当前与趋势数据包含粉丝、投稿数和关注数。

CSV 每行包含对象元信息、采集时间和指标；JSON 包含导出时间、范围、对象列表与快照数组。导出只读取本地 SQLite 数据，不会请求外部接口或保存临时导出文件。
