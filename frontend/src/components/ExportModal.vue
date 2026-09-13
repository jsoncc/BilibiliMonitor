<script setup lang="ts">
import { computed, ref } from 'vue'
import type { Target } from '../types'

const props = defineProps<{ target?: Target | null; all?: boolean; exporting?: boolean }>()
const emit = defineEmits<{
  (event: 'close'): void
  (event: 'export', options: { format: 'csv' | 'json'; hours: 'all' | '24' | '168' | '720' }): void
}>()

const format = ref<'csv' | 'json'>('csv')
const hours = ref<'all' | '24' | '168' | '720'>('all')
const title = computed(() => props.all ? '导出全部监控数据' : `导出：${props.target?.title || props.target?.target_key || ''}`)
</script>

<template>
  <div class="modal-backdrop">
    <section class="settings-modal export-modal" role="dialog" aria-modal="true" aria-label="导出数据">
      <button class="modal-close icon-button" aria-label="关闭" @click="emit('close')">×</button>
      <span class="eyebrow">DATA EXPORT</span>
      <h2>{{ title }}</h2>
      <p>导出仅读取本地快照，不会请求哔哩哔哩接口，也不会生成项目内副本。</p>
      <label>文件格式</label>
      <div class="segmented form-segmented">
        <button :class="{ selected: format === 'csv' }" @click="format = 'csv'">CSV</button>
        <button :class="{ selected: format === 'json' }" @click="format = 'json'">JSON</button>
      </div>
      <label>历史范围</label>
      <select v-model="hours">
        <option value="all">全部历史</option>
        <option value="24">最近 24 小时</option>
        <option value="168">最近 7 天</option>
        <option value="720">最近 30 天</option>
      </select>
      <div class="modal-actions">
        <button class="soft-button" :disabled="exporting" @click="emit('close')">取消</button>
        <button class="primary-button" :disabled="exporting" @click="emit('export', { format, hours })">{{ exporting ? '正在准备…' : '下载文件' }}</button>
      </div>
    </section>
  </div>
</template>
