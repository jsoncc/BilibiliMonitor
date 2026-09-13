<script setup lang="ts">
import { onBeforeUnmount, ref, watch } from 'vue'
const props=withDefaults(defineProps<{value:number|null|undefined;prefix?:string;suffix?:string}>(),{prefix:'',suffix:''})
const displayed=ref(Number(props.value||0))
const moving=ref(false)
let frame=0
function format(value:number){return new Intl.NumberFormat('zh-CN').format(Math.round(value))}
watch(()=>props.value,(next,previous)=>{
  const target=Number(next||0),start=Number(previous??displayed.value??0)
  if(start===target){displayed.value=target;return}
  cancelAnimationFrame(frame);moving.value=true
  const startedAt=performance.now(),duration=650
  const tick=(timestamp:number)=>{const progress=Math.min((timestamp-startedAt)/duration,1);const eased=1-Math.pow(1-progress,3);displayed.value=start+(target-start)*eased;if(progress<1)frame=requestAnimationFrame(tick);else{displayed.value=target;moving.value=false}}
  frame=requestAnimationFrame(tick)
})
onBeforeUnmount(()=>cancelAnimationFrame(frame))
</script>
<template><strong class="animated-metric-value" :class="{moving}">{{value==null?'—':`${prefix}${format(displayed)}${suffix}`}}</strong></template>
