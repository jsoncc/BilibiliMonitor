<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import type { MetricKey, Target } from '../types'
const props=defineProps<{target:Target;saving?:boolean}>()
const emit=defineEmits<{(e:'close'):void;(e:'save',metrics:string[]):void}>()
const selected=ref<string[]>([...(props.target.focus_metrics||[])])
watch(()=>props.target.id,()=>selected.value=[...(props.target.focus_metrics||[])])
const options=computed(()=>props.target.target_type==='video'?[['view_count','播放量'],['like_count','点赞'],['coin_count','投币'],['favorite_count','收藏'],['reply_count','评论'],['danmaku_count','弹幕'],['online_count','在线'],['three_combo_count','三连总量']]:[['follower_count','粉丝'],['video_count','投稿'],['following_count','关注']])
function toggle(key:string){selected.value=selected.value.includes(key)?selected.value.filter(item=>item!==key):[...selected.value,key]}
</script>
<template><div class="modal-backdrop"><div class="settings-modal focus-settings"><button class="modal-close icon-button" @click="emit('close')">×</button><span class="eyebrow">FOCUS MODE</span><h2>配置专注指标</h2><p>为“{{target.title||target.target_key}}”选择要在专注模式中保留的数据。</p><div class="focus-options"><button v-for="([key,label]) in options" :key="key" class="focus-option" :class="{selected:selected.includes(key)}" @click="toggle(key)"><span>{{label}}</span><small v-if="key==='three_combo_count'">点赞 + 投币 + 收藏</small><b>{{selected.includes(key)?'已选择':'选择'}}</b></button></div><p v-if="!selected.length" class="form-error">请至少选择一个指标。</p><div class="modal-actions"><button class="soft-button" @click="emit('close')">取消</button><button class="primary-button" :disabled="!selected.length||saving" @click="emit('save',selected)">{{saving?'保存中…':'保存配置'}}</button></div></div></div></template>
