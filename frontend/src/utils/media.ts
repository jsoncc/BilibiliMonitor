export function toMediaUrl(url?: string) {
  const value = (url || '').trim()
  if (!value) return ''
  if (value.startsWith('/api/media/image')) return value
  const normalized = value.startsWith('//') ? `https:${value}` : value.startsWith('http://') ? `https://${value.slice(7)}` : value
  try {
    const parsed = new URL(normalized)
    if (parsed.hostname.endsWith('hdslb.com')) return `/api/media/image?url=${encodeURIComponent(normalized)}`
  } catch { /* invalid image URLs are handled by the placeholder */ }
  return normalized
}
