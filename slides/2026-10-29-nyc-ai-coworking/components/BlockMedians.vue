<script setup>
import { computed, onMounted, ref } from 'vue'

const props = defineProps({
  src: { type: String, required: true },
  title: { type: String, default: '' },
  cell: { type: Number, default: 62 },
  measure: { type: String, default: 'lines' },
  domain: { type: Array, default: null },
})

const LABELS = {
  neither: 'no tests',
  'unit tests': 'unit',
  'target integration tests': 'target',
  both: 'both',
  reference: 'reference',
}
const RAMP = ['#eef5fd', '#86b6ef', '#3987e5', '#256abf', '#0d366b']

const data = ref(null)
onMounted(async () => {
  const response = await fetch(props.src)
  if (!response.ok) throw new Error(`${props.src}: HTTP ${response.status}`)
  data.value = await response.json()
})

const span = computed(() => {
  if (props.domain) return props.domain
  const values = cells.value.map(c => c.value)
  return props.measure === 'lines' ? [Math.max(...values), Math.min(...values)] : [Math.min(...values), Math.max(...values)]
})
function colour(value) {
  const [low, high] = span.value
  const t = Math.min(1, Math.max(0, (value - low) / (high - low))) * (RAMP.length - 1)
  const i = Math.min(RAMP.length - 2, Math.floor(t))
  const f = t - i
  const mix = (a, b) => Math.round(parseInt(a, 16) * (1 - f) + parseInt(b, 16) * f)
  const hex = n => n.toString(16).padStart(2, '0')
  const [a, b] = [RAMP[i], RAMP[i + 1]]
  return `#${hex(mix(a.slice(1, 3), b.slice(1, 3)))}${hex(mix(a.slice(3, 5), b.slice(3, 5)))}${hex(mix(a.slice(5, 7), b.slice(5, 7)))}`
}
function textColour(value) {
  const [low, high] = span.value
  return (value - low) / (high - low) > 0.5 ? '#fff' : '#17243a'
}
const groups = computed(() => data.value?.groups ?? [])
const n = computed(() => groups.value.length)
const cells = computed(() => (data.value?.cells ?? []).map(([a, b, pct, lines, count]) => ({
  row: groups.value.indexOf(a), col: groups.value.indexOf(b), value: props.measure === 'lines' ? lines : pct, pct, lines, count, a, b,
})))
const rows = computed(() => groups.value.filter((_, i) => cells.value.some(c => c.row === i)))
const left = 64
const top = 18
</script>

<template>
  <div class="block">
    <div v-if="title" class="title">{{ title }}</div>
    <svg v-if="data" :width="left + n * cell" :height="top + rows.length * cell" :viewBox="`0 0 ${left + n * cell} ${top + rows.length * cell}`">
      <text v-for="(group, i) in groups" :key="'c' + group" :x="left + (i + 0.5) * cell" :y="top - 6" class="label" text-anchor="middle">{{ LABELS[group] }}</text>
      <text v-for="group in rows" :key="'r' + group" :x="left - 6" :y="top + (groups.indexOf(group) + 0.5) * cell + 4" class="label" text-anchor="end">{{ LABELS[group] }}</text>
      <g v-for="c in cells" :key="c.a + c.b">
        <rect :x="left + c.col * cell + 1" :y="top + c.row * cell + 1" :width="cell - 2" :height="cell - 2" :fill="colour(c.value)" rx="3"><title>{{ c.a }} ↔ {{ c.b }}: median {{ c.lines }} diff lines, {{ c.pct }}% similar, over {{ c.count }} pairs</title></rect>
        <text :x="left + (c.col + 0.5) * cell" :y="top + (c.row + 0.5) * cell + 5" class="value" text-anchor="middle" :fill="textColour(c.value)">{{ c.value }}</text>
      </g>
    </svg>
  </div>
</template>

<style scoped>
.block { display: inline-block; }
.title { font-size: 12px; font-weight: 600; color: #17243a; margin-bottom: 2px; }
.label { font-size: 10px; fill: #61718a; }
.value { font-size: 14px; font-weight: 600; }
</style>
