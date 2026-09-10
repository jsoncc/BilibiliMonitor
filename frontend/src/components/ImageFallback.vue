<script setup lang="ts">
import { ref, watch } from 'vue'
import { toMediaUrl } from '../utils/media'

const props = defineProps<{ src?: string; alt?: string; kind?: 'cover' | 'avatar' }>()
const failed = ref(false)
watch(() => props.src, () => { failed.value = false })
</script>

<template>
  <span class="image-fallback" :class="kind || 'cover'">
    <img v-if="toMediaUrl(src) && !failed" :src="toMediaUrl(src)" :alt="alt || ''" @error="failed = true">
    <span v-else class="image-placeholder">▧</span>
  </span>
</template>
