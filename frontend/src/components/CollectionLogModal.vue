<script setup lang="ts">
import type { Target } from '../types'

defineProps<{ target: Target; logs: Array<{ id: number; captured_at: string; status: string; message: string }>; loading?: boolean }>()
const emit = defineEmits<{ (event: 'close'): void }>()
const time = (value?: string) => value ? new Date(value).toLocaleString('zh-CN', { hour12: false }) : '暂无'
</script>

<template>
  <div class="modal-backdrop">
    <section class="settings-modal log-modal" role="dialog" aria-modal="true" aria-label="采集记录">
      <button class="modal-close icon-button" aria-label="关闭" @click="emit('close')">×</button>
      <span class="eyebrow">COLLECTION HEALTH</span>
      <h2>采集记录</h2>
      <p class="log-target">{{ target.title || target.target_key }} · 最近 20 条</p>
      <div class="health-summary">
        <span>最近成功：<b>{{ time(target.last_success_at) }}</b></span>
        <span>下次采集：<b>{{ time(target.next_collect_at) }}</b></span>
        <span v-if="target.last_error" class="health-error">最近错误：{{ target.last_error }}</span>
      </div>
      <div v-if="loading" class="log-empty">正在读取采集记录…</div>
      <div v-else-if="!logs.length" class="log-empty">暂无采集记录</div>
      <div v-else class="log-list">
        <article v-for="log in logs" :key="log.id" class="log-item" :class="log.status">
          <div><b>{{ log.status === 'success' ? '采集成功' : '采集失败' }}</b><time>{{ time(log.captured_at) }}</time></div>
          <p>{{ log.message || '—' }}</p>
        </article>
      </div>
    </section>
  </div>
</template>
