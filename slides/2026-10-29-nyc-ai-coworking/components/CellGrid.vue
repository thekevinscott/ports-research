<script setup>
import { computed, ref, watch } from 'vue'
import { experiment, experiments, withBase } from './experiment.js'

const props = defineProps({
  sources: { type: Object, required: true },
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
const UNIT = [['off', 'no unit tests'], ['on', 'unit tests']]
const INTEGRATION = [['none', 'none'], ['source', 'source'], ['target', 'target'], ['both', 'both']]
const CONDITION = {
  'off:none': 'none', 'off:source': 'source', 'off:target': 'target', 'off:both': 'source + target',
  'on:none': 'unit', 'on:source': 'unit + source', 'on:target': 'unit + target', 'on:both': 'all',
}
const LAYOUTS = {
  'models-effort': { rows: MODELS, cols: EFFORTS, key: row => `${row.model}:${row.effort}`, at: (r, c) => `${r}:${c}` },
  tests: { rows: UNIT, cols: INTEGRATION, key: row => row.condition, at: (r, c) => CONDITION[`${r}:${c}`] },
}
const RAMP = ['#eef5fd', '#86b6ef', '#3987e5', '#256abf', '#0d366b']

const active = computed(() => experiments[experiment.value].key)
const layout = computed(() => LAYOUTS[active.value])
const cache = new Map()
const data = ref(null)
async function load() {
  const src = props.sources[active.value]
  if (!cache.has(src)) {
    const response = await fetch(withBase(src))
    if (!response.ok) throw new Error(`${src}: HTTP ${response.status}`)
    cache.set(src, await response.json())
  }
  data.value = cache.get(src)
}
watch(active, load, { immediate: true })

const cells = computed(() => {
  const { rows, cols, key, at } = layout.value
  const byKey = new Map((data.value ?? []).filter(row => row.direction === props.direction).map(row => [key(row), row]))
  return rows.flatMap(([r], row) => cols.map(([c], col) => {
    const found = byKey.get(at(r, c))
    return found ? { row, col, value: found[props.field], ...found } : null
  })).filter(Boolean)
})
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
const left = computed(() => active.value === 'tests' ? 84 : 52)
const top = 18
</script>

<template>
  <div class="block">
    <div v-if="title" class="title">{{ title }}</div>
    <svg v-if="data" :width="left + layout.cols.length * cell" :height="top + layout.rows.length * cell" :viewBox="`0 0 ${left + layout.cols.length * cell} ${top + layout.rows.length * cell}`">
      <text v-for="([id, label], i) in layout.cols" :key="id" :x="left + (i + 0.5) * cell" :y="top - 6" class="label" text-anchor="middle">{{ label }}</text>
      <text v-for="([id, label], i) in layout.rows" :key="id" :x="left - 6" :y="top + (i + 0.5) * cell + 4" class="label" text-anchor="end">{{ label }}</text>
      <g v-for="c in cells" :key="c.row + ':' + c.col">
        <rect :x="left + c.col * cell + 1" :y="top + c.row * cell + 1" :width="cell - 2" :height="cell - 2" :fill="colour(c.value)" rx="3"><title>{{ c.model }} {{ c.effort ?? c.condition }}: median {{ c.pair_lines_median }} diff lines between ports ({{ c.pair_pct_median }}% similar) over {{ c.pairs }} pairs of {{ c.ports }} ports; median {{ c.reference_lines_median }} lines vs the reference</title></rect>
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
