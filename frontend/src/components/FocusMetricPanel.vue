<script setup lang="ts">
import { computed, inject, type Ref } from 'vue'
import type { MetricKey, Target } from '../types'
import AnimatedMetricValue from './AnimatedMetricValue.vue'
const props=defineProps<{target:Target;latest:any;growth:any}>()
const emit=defineEmits<{(e:'configure'):void}>()
const trendRange=inject<Ref<24|168|720>>('trendRange')
const rangeLabel=computed(()=>trendRange?.value===24?'近 24 小时':trendRange?.value===720?'近 30 天':'近 7 天')
const labels:Record<MetricKey,string>={view_count:'播放量',like_count:'点赞',coin_count:'投币',favorite_count:'收藏',reply_count:'评论',danmaku_count:'弹幕',online_count:'在线',follower_count:'粉丝',video_count:'投稿',following_count:'关注',three_combo_count:'三连总量'}
const format=(value:any)=>value==null?'—':new Intl.NumberFormat('zh-CN').format(Number(value))
const isCombo=(key:string)=>key==='three_combo_count'
const value=(key:string)=>isCombo(key)?['like_count','coin_count','favorite_count'].reduce((total,field)=>total+Number(props.latest?.[field]||0),0):props.latest?.[key]
const change=(key:string)=>isCombo(key)?['like_count','coin_count','favorite_count'].reduce((total,field)=>total+Number(props.growth?.[field]||0),0):Number(props.growth?.[key]||0)
</script>
<template><section class="focus-section"><div class="metric-section-head"><div><strong>专注指标</strong><span>新快照到达时，数值会平滑更新</span></div><button v-if="target.id" class="soft-button" @click="emit('configure')">配置指标</button></div><div v-if="!target.focus_metrics?.length" class="focus-empty"><div><strong>还没有设置专注指标</strong><p>选择最关心的数据，进入专注模式后只看这些指标。</p></div><button v-if="target.id" class="primary-button" @click="emit('configure')">配置专注指标</button><span v-else>仅查看一次需先开始监控后才能保存专注配置。</span></div><div v-else class="metric-grid focus-grid"><div v-for="key in target.focus_metrics" :key="key" class="metric-card"><span class="metric-label">{{labels[key as MetricKey]}}</span><AnimatedMetricValue class="metric-value" :value="value(key)"/><em class="metric-growth" :class="{negative:change(key)<0,stable:change(key)===0}"><b>{{change(key)>0?'↑':change(key)<0?'↓':'—'}}</b> {{change(key)>0?'+':''}}{{format(change(key))}} <small>{{rangeLabel}}</small></em><small v-if="isCombo(key)" class="combo-hint">点赞 + 投币 + 收藏</small></div></div></section></template>
