<script setup>
import { computed, onMounted, ref } from 'vue'

const props = defineProps({
  src: { type: String, required: true },
  direction: { type: String, required: true },
  field: { type: String, default: 'pair_lines_median' },
  title: { type: String, default: '' },
  cell: { type: Number, default: 62 },
})

const MODELS = [
  ['claude-fable-5-1', 'Fable'],
  ['claude-opus-5-5', 'Opus'],
  ['claude-sonnet-5-5', 'Sonnet'],
  ['claude-haiku-5-5', 'Haiku'],
]
const EFFORTS = [['low', 'low'], ['medium', 'medium'], ['high', 'high'], ['xhigh', 'very high']]
const RAMP = ['#eef5fd', '#86b6ef', '#3987e5', '#256abf', '#0d366b']

const data = ref(null)
onMounted(async () => {
  const response = await fetch(props.src)
  if (!response.ok) throw new Error(`${props.src}: HTTP ${response.status}`)
  data.value = await response.json()
})

const cells = computed(() => (data.value ?? []).filter(row => row.direction === props.direction).map(row => ({
  row: MODELS.findIndex(([id]) => id === row.model),
  col: EFFORTS.findIndex(([id]) => id === row.effort),
  value: row[props.field],
  ...row,
})).filter(c => c.row >= 0 && c.col >= 0))
const span = computed(() => {
  const values = cells.value.map(c => c.value)
  return [Math.max(...values), Math.min(...values)]
})
function t(value) {
  const [low, high] = span.value
  return high === low ? 0 : Math.min(1, Math.max(0, (value - low) / (high - low)))
}
function colour(value) {
  const scaled = t(value) * (RAMP.length - 1)
  const i = Math.min(RAMP.length - 2, Math.floor(scaled))
  const f = scaled - i
  const mix = (a, b) => Math.round(parseInt(a, 16) * (1 - f) + parseInt(b, 16) * f)
  const hex = n => n.toString(16).padStart(2, '0')
  const [a, b] = [RAMP[i], RAMP[i + 1]]
  return `#${hex(mix(a.slice(1, 3), b.slice(1, 3)))}${hex(mix(a.slice(3, 5), b.slice(3, 5)))}${hex(mix(a.slice(5, 7), b.slice(5, 7)))}`
}
const left = 52
const top = 18
</script>

<template>
  <div class="block">
    <div v-if="title" class="title">{{ title }}</div>
    <svg v-if="data" :width="left + EFFORTS.length * cell" :height="top + MODELS.length * cell" :viewBox="`0 0 ${left + EFFORTS.length * cell} ${top + MODELS.length * cell}`">
      <text v-for="([id, label], i) in EFFORTS" :key="id" :x="left + (i + 0.5) * cell" :y="top - 6" class="label" text-anchor="middle">{{ label }}</text>
      <text v-for="([id, label], i) in MODELS" :key="id" :x="left - 6" :y="top + (i + 0.5) * cell + 4" class="label" text-anchor="end">{{ label }}</text>
      <g v-for="c in cells" :key="c.model + c.effort">
        <rect :x="left + c.col * cell + 1" :y="top + c.row * cell + 1" :width="cell - 2" :height="cell - 2" :fill="colour(c.value)" rx="3"><title>{{ c.model }} {{ c.effort }}: median {{ c.pair_lines_median }} diff lines between ports ({{ c.pair_pct_median }}% similar) over {{ c.pairs }} pairs of {{ c.ports }} ports; median {{ c.reference_lines_median }} lines vs the reference</title></rect>
        <text :x="left + (c.col + 0.5) * cell" :y="top + (c.row + 0.5) * cell + 5" class="value" text-anchor="middle" :fill="t(c.value) > 0.5 ? '#fff' : '#17243a'">{{ c.value }}</text>
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
