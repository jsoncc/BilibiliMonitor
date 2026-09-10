# 数据模型

`targets` 保存视频或 UP 主监控对象；`video_snapshots` 保存视频指标；`uploader_snapshots` 保存账号指标；`collect_logs` 保存采集成功或失败记录。UP 主对象额外保存 `last_submission_at`，用于展示最近一次投稿时间，不参与数值趋势计算。所有表由 SQLAlchemy 启动时自动创建。
