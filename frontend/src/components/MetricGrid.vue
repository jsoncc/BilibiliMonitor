<script setup lang="ts">
import { computed, inject, type Ref } from 'vue'
import type { Target } from '../types'
const props=defineProps<{target:Target;latest:any;growth:any}>()
const trendRange=inject<Ref<24|168|720>>('trendRange')
const rangeLabel=computed(()=>trendRange?.value===24?'近 24 小时':trendRange?.value===720?'近 30 天':'近 7 天')
const metrics=computed(()=>props.target.target_type==='video'?[['view_count','播放量'],['like_count','点赞'],['coin_count','投币'],['favorite_count','收藏'],['reply_count','评论'],['danmaku_count','弹幕'],['online_count','在线']]:[['follower_count','粉丝'],['video_count','投稿'],['following_count','关注']])
const format=(value:any)=>value==null||value==='—'?'—':new Intl.NumberFormat('zh-CN').format(Number(value))
</script>
<template><section class="metric-section"><div class="metric-section-head"><strong>当前指标</strong><span>变化量统计：{{rangeLabel}} · 相对该范围首个采样点</span></div><div class="metric-grid"><div v-for="([key,label]) in metrics" :key="key" class="metric-card"><span class="metric-label">{{label}}</span><strong class="metric-value">{{format(latest?.[key])}}</strong><em class="metric-growth" :class="{negative:(growth?.[key]||0)<0, stable:(growth?.[key]||0)===0}"><b>{{(growth?.[key]||0)>0?'↑':(growth?.[key]||0)<0?'↓':'—'}}</b> {{(growth?.[key]||0)>0?'+':''}}{{format(growth?.[key]||0)}} <small>{{rangeLabel}}</small></em></div></div></section></template>
