export type Target = { id:number; target_type:string; target_key:string; title:string; description:string; cover_url:string; owner_uid?:string; interval_seconds:number; last_collected_at?:string; last_success_at?:string; last_error_at?:string; next_collect_at?:string; last_error:string; active:boolean }
export type MetricKey = 'view_count'|'like_count'|'coin_count'|'favorite_count'|'reply_count'|'danmaku_count'|'online_count'|'follower_count'|'video_count'|'following_count'
export type TrendRange = 24|168|720
