# 数据模型

`targets` 保存视频或 UP 主监控对象；`video_snapshots` 保存视频指标；`uploader_snapshots` 保存账号指标；`collect_logs` 保存采集成功或失败记录。UP 主快照包含粉丝、投稿数和关注数，不采集最近投稿日期。旧本地数据库中曾存在的投稿日期列会被保留但不再读写；所有当前表由 SQLAlchemy 启动时自动创建。

快照永久保留。SQLite 使用 WAL 模式，运行时可能在 `data/` 下出现同名的 `-wal`、`-shm` 文件，它们属于数据库的一部分，不应单独删除。
