<script setup lang="ts">
import { computed } from 'vue'
import type { Target } from '../types'
const props=defineProps<{target:Target;latest:any;growth:any}>()
const metrics=computed(()=>props.target.target_type==='video'?[['view_count','播放量'],['like_count','点赞'],['coin_count','投币'],['favorite_count','收藏'],['reply_count','评论'],['danmaku_count','弹幕'],['online_count','在线']]:[['follower_count','粉丝'],['video_count','投稿'],['following_count','关注']])
const format=(value:any)=>value==null||value==='—'?'—':new Intl.NumberFormat('zh-CN').format(Number(value))
</script>
<template><div class="metric-grid"><div v-for="([key,label]) in metrics" :key="key" class="metric-card"><span>{{label}}</span><strong>{{format(latest?.[key])}}</strong><em :class="{negative:(growth?.[key]||0)<0}">{{(growth?.[key]||0)>0?'+':''}}{{format(growth?.[key]||0)}}</em></div></div></template>
