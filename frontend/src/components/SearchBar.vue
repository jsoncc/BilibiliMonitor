<script setup lang="ts">
defineProps<{ loading:boolean; value:string }>()
const emit=defineEmits<{(e:'update:value',value:string):void;(e:'search'):void}>()
</script>
<template><form class="search-shell" title="支持 BV、AV、UID、视频链接和 UP 主空间链接" @submit.prevent="emit('search')"><div class="search-icon">⌕</div><input :value="value" @input="emit('update:value',($event.target as HTMLInputElement).value)" placeholder="输入 BV / AV / UID / 视频链接 / 空间链接"/><span class="search-types">支持 BV / AV / UID</span><button class="primary-button" :disabled="loading">{{loading?'解析中…':'解析'}}</button></form></template>
