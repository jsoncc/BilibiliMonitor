<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import type { MetricKey, Target } from '../types'
import AnimatedMetricValue from './AnimatedMetricValue.vue'

type Point = Record<string, number | string | null>
type ChangeWindow = { label: string; delta: number | null; percent: number | null; note: string }

const props = defineProps<{ target: Target; latest: any; growth: any }>()
const emit = defineEmits<{ (e: 'configure'): void }>()
const focusTrend = ref<{ points: Point[]; latest: Point | null }>({ points: [], latest: null })
const loading = ref(false)
const loadError = ref('')
let timer: number | undefined

const labels: Record<MetricKey, string> = {
  view_count: '播放量', like_count: '点赞', coin_count: '投币', favorite_count: '收藏',
  reply_count: '评论', danmaku_count: '弹幕', online_count: '在线', follower_count: '粉丝',
  video_count: '投稿', following_count: '关注', three_combo_count: '三连总量',
}
const isCombo = (key: string) => key === 'three_combo_count'
const metricValue = (point: Point | null | undefined, key: string): number | null => {
  if (!point) return null
  if (isCombo(key)) {
    const fields = ['like_count', 'coin_count', 'favorite_count']
    if (fields.some((field) => point[field] == null)) return null
    return fields.reduce((total, field) => total + Number(point[field]), 0)
  }
  return point[key] == null ? null : Number(point[key])
}
const metricPoints = (key: string) => focusTrend.value.points
  .filter((point) => metricValue(point, key) != null)
  .sort((a, b) => new Date(String(a.time)).getTime() - new Date(String(b.time)).getTime())
const format = (value: number | null) => value == null ? '—' : new Intl.NumberFormat('zh-CN').format(Math.abs(Math.round(value)))
const duration = (milliseconds: number) => {
  const minutes = Math.max(0, Math.round(milliseconds / 60000))
  if (minutes < 60) return `${minutes} 分钟`
  const hours = Math.round(minutes / 6) / 10
  if (hours < 48) return `${hours} 小时`
  return `${Math.round(hours / 2.4) / 10} 天`
}
const makeWindow = (key: string, label: string, hours: number | null): ChangeWindow => {
  const points = metricPoints(key)
  if (points.length < 2) return { label, delta: null, percent: null, note: '等待更多采样' }
  const latest = points[points.length - 1]
  const latestAt = new Date(String(latest.time)).getTime()
  const candidates = hours == null
    ? points.slice(-2)
    : points.filter((point) => new Date(String(point.time)).getTime() >= latestAt - hours * 3600000)
  if (candidates.length < 2) return { label, delta: null, percent: null, note: '等待更多采样' }
  const baseline = candidates[0]
  const baselineValue = metricValue(baseline, key)!
  const latestValue = metricValue(latest, key)!
  const delta = latestValue - baselineValue
  const elapsed = latestAt - new Date(String(baseline.time)).getTime()
  const complete = hours != null && elapsed >= hours * 3600000 * 0.95
  return {
    label,
    delta,
    percent: baselineValue === 0 ? null : delta / baselineValue * 100,
    note: hours == null ? `间隔 ${duration(elapsed)}` : complete ? '完整周期' : `实际记录 ${duration(elapsed)}`,
  }
}
const windows = (key: string) => [
  makeWindow(key, '本次采集', null),
  makeWindow(key, '近 24 小时', 24),
  makeWindow(key, '近 7 天', 168),
]
const current = (key: string) => metricValue(focusTrend.value.latest || props.latest, key)
const singleMetric = computed(() => props.target.focus_metrics?.length === 1)
const latestTime = computed(() => String(focusTrend.value.latest?.time || props.target.last_success_at || ''))
const updatedAt = computed(() => latestTime.value
  ? new Date(latestTime.value).toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit' })
  : '等待首次成功采集')
const freshness = computed(() => {
  if (props.target.last_error) return '采集异常'
  if (!latestTime.value) return '等待采集'
  const age = Date.now() - new Date(latestTime.value).getTime()
  return age > props.target.interval_seconds * 2500 ? '更新延迟' : '数据正常'
})
const direction = (delta: number | null) => delta == null ? 'empty' : delta > 0 ? 'positive' : delta < 0 ? 'negative' : 'stable'
const sign = (delta: number | null) => delta == null ? '' : delta > 0 ? '+' : delta < 0 ? '−' : ''
const percent = (value: number | null) => value == null ? '—' : `${value > 0 ? '+' : ''}${value.toFixed(Math.abs(value) >= 10 ? 1 : 2)}%`

async function loadTrend() {
  if (!props.target.id) return
  loading.value = true
  loadError.value = ''
  try {
    const group = props.target.target_type === 'video' ? 'videos' : 'uploaders'
    const response = await fetch(`/api/${group}/${props.target.id}/trend?hours=168`)
    const data = await response.json()
    if (!response.ok) throw Error(data.detail || '专注数据加载失败')
    focusTrend.value = data
  } catch (error: any) {
    loadError.value = error.message || '专注数据加载失败'
  } finally {
    loading.value = false
  }
}

watch(() => props.target.id, loadTrend)
onMounted(() => {
  loadTrend()
  timer = window.setInterval(loadTrend, 60000)
})
onUnmounted(() => {
  if (timer != null) window.clearInterval(timer)
})
</script>

<template>
  <section class="focus-section">
    <div class="focus-toolbar">
      <div><span class="eyebrow">LIVE FOCUS</span><h2>专注数据</h2><p>新快照到达时，数值会平滑更新</p></div>
      <button v-if="target.id" class="soft-button" @click="emit('configure')">配置指标</button>
    </div>
    <div v-if="!target.focus_metrics?.length" class="focus-empty">
      <div><strong>还没有设置专注指标</strong><p>选择最关心的数据，进入专注模式后只看这些指标。</p></div>
      <button v-if="target.id" class="primary-button" @click="emit('configure')">配置专注指标</button>
      <span v-else>仅查看一次需先开始监控后才能保存专注配置。</span>
    </div>
    <div v-else-if="loadError" class="focus-empty"><strong>{{ loadError }}</strong></div>
    <div v-else class="focus-grid" :class="{ single: singleMetric }">
      <article v-for="key in target.focus_metrics" :key="key" class="focus-card" :class="{ hero: singleMetric }">
        <header>
          <span class="focus-label"><i></i>{{ labels[key as MetricKey] }}</span>
          <span class="focus-status">{{ loading ? '更新中' : '实时快照' }}</span>
        </header>
        <div class="focus-card-body">
          <AnimatedMetricValue class="focus-value" :value="current(key)" />
          <small v-if="isCombo(key)" class="combo-hint">点赞 + 投币 + 收藏</small>
        </div>
        <div class="focus-windows">
          <div v-for="item in windows(key)" :key="item.label" class="focus-window">
            <span>{{ item.label }}</span>
            <strong :class="direction(item.delta)">{{ sign(item.delta) }}{{ format(item.delta) }}</strong>
            <b>{{ percent(item.percent) }}</b>
            <small>{{ item.note }}</small>
          </div>
        </div>
        <footer>
          <span class="focus-update"><i></i>最近成功采集：{{ updatedAt }}</span>
          <span>{{ freshness }} · {{ target.interval_seconds }} 秒/次</span>
        </footer>
      </article>
    </div>
  </section>
</template>
