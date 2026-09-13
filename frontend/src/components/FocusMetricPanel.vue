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
const singleMetric=computed(()=>props.target.focus_metrics?.length===1)
const updatedAt=computed(()=>props.target.last_success_at?new Date(props.target.last_success_at).toLocaleString('zh-CN',{month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit'}):'等待首次成功采集')
</script>
<template><section class="focus-section"><div class="focus-toolbar"><div><span class="eyebrow">LIVE FOCUS</span><h2>专注数据</h2><p>新快照到达时，数值会平滑更新</p></div><button v-if="target.id" class="soft-button" @click="emit('configure')">配置指标</button></div><div v-if="!target.focus_metrics?.length" class="focus-empty"><div><strong>还没有设置专注指标</strong><p>选择最关心的数据，进入专注模式后只看这些指标。</p></div><button v-if="target.id" class="primary-button" @click="emit('configure')">配置专注指标</button><span v-else>仅查看一次需先开始监控后才能保存专注配置。</span></div><div v-else class="focus-grid" :class="{single:singleMetric}"><article v-for="key in target.focus_metrics" :key="key" class="focus-card" :class="{hero:singleMetric}"><header><span class="focus-label"><i></i>{{labels[key as MetricKey]}}</span><span class="focus-status">实时快照</span></header><div class="focus-card-body"><div><AnimatedMetricValue class="focus-value" :value="value(key)"/><small v-if="isCombo(key)" class="combo-hint">点赞 + 投币 + 收藏</small></div><div class="focus-context"><span>本周期变化</span><strong :class="{negative:change(key)<0,stable:change(key)===0}">{{change(key)>0?'↑ +':change(key)<0?'↓ ':''}}{{format(Math.abs(change(key)))}}</strong><small>{{rangeLabel}} · 对比周期首个采样点</small></div></div><footer><span class="focus-update"><i></i>最近成功采集：{{updatedAt}}</span><span v-if="change(key)>0" class="focus-positive">持续增长</span><span v-else-if="change(key)<0" class="focus-negative">数值下降</span><span v-else class="focus-neutral">暂无变化</span></footer></article></div></section></template>
