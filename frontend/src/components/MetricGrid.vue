<script setup lang="ts">
import { computed, inject, type Ref } from 'vue'
import type { Target } from '../types'
const props=defineProps<{target:Target;latest:any;growth:any}>()
const trendRange=inject<Ref<24|168|720>>('trendRange')
const rangeLabel=computed(()=>trendRange?.value===24?'近 24 小时':trendRange?.value===720?'近 30 天':'近 7 天')
const metrics=computed(()=>props.target.target_type==='video'?[['view_count','播放量'],['like_count','点赞'],['coin_count','投币'],['favorite_count','收藏'],['reply_count','评论'],['danmaku_count','弹幕'],['online_count','在线']]:[['follower_count','粉丝'],['video_count','投稿'],['following_count','关注'],['last_submission_at','上次投稿']])
const format=(value:any)=>value==null||value==='—'?'—':new Intl.NumberFormat('zh-CN').format(Number(value))
const displayValue=(key:string)=>key==='last_submission_at'?(props.target.last_submission_at?new Date(props.target.last_submission_at).toLocaleString('zh-CN',{year:'numeric',month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit'}):'暂无投稿记录'):format(props.latest?.[key])
</script>
<template><section class="metric-section"><div class="metric-section-head"><strong>当前指标</strong><span>变化量统计：{{rangeLabel}} · 相对该范围首个采样点</span></div><div class="metric-grid"><div v-for="([key,label]) in metrics" :key="key" class="metric-card" :class="{dateMetric:key==='last_submission_at'}"><span class="metric-label">{{label}}</span><strong class="metric-value">{{displayValue(key)}}</strong><em v-if="key!=='last_submission_at'" class="metric-growth" :class="{negative:(growth?.[key]||0)<0, stable:(growth?.[key]||0)===0}"><b>{{(growth?.[key]||0)>0?'↑':(growth?.[key]||0)<0?'↓':'—'}}</b> {{(growth?.[key]||0)>0?'+':''}}{{format(growth?.[key]||0)}} <small>{{rangeLabel}}</small></em><em v-else class="metric-growth stable">最近一次成功采集</em></div></div></section></template>
