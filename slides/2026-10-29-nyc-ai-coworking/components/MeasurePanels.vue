<script setup>
import { computed, onMounted, ref } from 'vue'

const props = defineProps({
  src: { type: String, required: true },
  by: { type: String, required: true },
  measures: { type: Array, required: true },
  reference: { type: String, default: null },
  referenceLine: { type: Number, default: null },
  width: { type: Number, default: 250 },
  height: { type: Number, default: 150 },
})

const LABELS = {
  wall_minutes: 'Wall time (min)',
  total_tokens: 'Tokens (M)',
  cost_usd: 'Cost (USD, list price)',
  file_count: 'Files',
  loc: 'LOC',
  diff_lines_changed: 'Diff lines vs reference',
  embedding_distance: 'Embedding distance',
  behavior_agreement_pct: 'Behaviour agreement (%)',
  api_agreement_pct: 'API agreement (%)',
  ladder_ref_ratio: 'Ladder time ÷ reference (1 = same speed)',
}
const DIRECTIONS = [
  ['python→javascript', 'Python → TypeScript', '#5d85a0'],
  ['javascript→python', 'TypeScript → Python', '#e36836'],
]
const CATEGORIES = {
  condition: {
    axis: 'tests seen',
    items: [
      ['none', 'none'], ['unit', 'unit'], ['source', 'source'], ['target', 'target'],
      ['unit + source', 'unit+src'], ['unit + target', 'unit+tgt'], ['source + target', 'src+tgt'], ['all', 'all'],
    ].map(([key, label]) => ({ key, label, match: row => row.condition === key })),
  },
  'condition-v1': {
    axis: 'tests seen',
    items: [['no tests', 'none'], ['source tests', 'source'], ['target tests', 'target'], ['both tests', 'both']]
      .map(([key, label]) => ({ key, label, match: row => row.condition === key })),
  },
  model: {
    axis: 'model',
    items: [['claude-fable-5-1', 'Fable'], ['claude-opus-5-5', 'Opus'], ['claude-sonnet-5-5', 'Sonnet'], ['claude-haiku-5-5', 'Haiku']]
      .map(([key, label]) => ({ key, label, match: row => row.model === key })),
  },
  effort: {
    axis: 'effort',
    items: [['low', 'low'], ['medium', 'medium'], ['high', 'high'], ['xhigh', 'very high']]
      .map(([key, label]) => ({ key, label, match: row => row.effort === key })),
  },
}

const rows = ref([])
const reference = ref({})
onMounted(async () => {
  if (props.reference) reference.value = await (await fetch(props.reference)).json()
  const response = await fetch(props.src)
  if (!response.ok) throw new Error(`${props.src}: HTTP ${response.status}`)
  const [header, ...lines] = (await response.text()).trim().split(/\r?\n/)
  const keys = header.split(',')
  rows.value = lines.map(line => Object.fromEntries(keys.map((key, index) => [key, line.split(',')[index]])))
})

const categories = CATEGORIES[props.by]
const pad = { left: 40, right: 8, top: 8, bottom: categories.items.length > 4 ? 30 : 20 }
const plotW = props.width - pad.left - pad.right
const plotH = props.height - pad.top - pad.bottom
const band = plotW / categories.items.length

function niceStep(value) {
  const power = 10 ** Math.floor(Math.log10(value))
  return [1, 2, 2.5, 5, 10].find(candidate => candidate * power >= value) * power
}
function scaled(measure, value) { return measure === 'total_tokens' ? Number(value) / 1e6 : Number(value) }
function median(values) {
  if (!values.length) return null
  const sorted = [...values].sort((a, b) => a - b)
  const half = Math.floor(sorted.length / 2)
  return sorted.length % 2 ? sorted[half] : (sorted[half - 1] + sorted[half]) / 2
}
function referenceFor(measure, direction) {
  if (props.referenceLine !== null) return props.referenceLine
  const value = reference.value[direction]?.[measure]
  return value === undefined ? null : scaled(measure, value)
}
const panels = computed(() => props.measures.map(measure => {
  const percent = measure.endsWith('_pct')
  const all = rows.value.map(row => row[measure]).filter(v => v !== undefined && v !== '').map(v => scaled(measure, v))
  const refs = DIRECTIONS.map(([direction]) => referenceFor(measure, direction)).filter(v => v !== null)
  const step = percent ? 25 : niceStep(Math.max(1e-9, ...all, ...refs) / 4)
  const max = percent ? 100 : step * Math.ceil(Math.max(1e-9, ...all, ...refs) / step)
  const y = value => pad.top + plotH - (value / max) * plotH
  const directions = DIRECTIONS.map(([direction, label, color]) => ({
    direction, label, color,
    reference: referenceFor(measure, direction),
    groups: categories.items.map((item, column) => {
      const points = rows.value
        .filter(row => row.direction === direction && item.match(row) && row[measure] !== undefined && row[measure] !== '')
        .map((row, i) => ({ id: row.run_id, value: scaled(measure, row[measure]), jitter: (((i * 7919) % 13) - 6) / 6 * band * 0.32 }))
      return { ...item, column, points, median: median(points.map(p => p.value)) }
    }),
  }))
  const ticks = Array.from({ length: Math.round(max / step) + 1 }, (_, i) => i * step)
  return { measure, label: LABELS[measure] ?? measure, max, y, ticks, directions, any: all.length > 0 }
}).filter(panel => panel.any))
function tick(value, measure) {
  if (measure === 'embedding_distance') return value.toFixed(3)
  if (measure === 'cost_usd') return `$${value.toFixed(value < 10 ? 2 : 0)}`
  if (value >= 1000) return `${(value / 1000).toFixed(value % 1000 ? 1 : 0)}k`
  return Number.isInteger(value) ? String(value) : value.toFixed(1).replace(/\.0$/, '')
}
</script>

<template>
  <div v-if="rows.length" class="panels">
    <div class="grid" :style="{ gridTemplateColumns: `90px repeat(${panels.length}, ${width}px)` }">
      <span></span>
      <span v-for="panel in panels" :key="panel.measure" class="measure">{{ panel.label }}</span>
      <template v-for="(direction, which) in DIRECTIONS" :key="direction[0]">
        <span class="direction" :style="{ color: direction[2] }">{{ direction[1] }}</span>
        <svg v-for="panel in panels" :key="panel.measure" :width="width" :height="height" :viewBox="`0 0 ${width} ${height}`">
          <g v-for="t in panel.ticks" :key="t">
            <line :x1="pad.left" :x2="pad.left + plotW" :y1="panel.y(t)" :y2="panel.y(t)" stroke="#e6e3dc" />
            <text :x="pad.left - 5" :y="panel.y(t) + 3" class="tick" text-anchor="end">{{ tick(t, panel.measure) }}</text>
          </g>
          <line v-if="panel.directions[which].reference !== null" :x1="pad.left" :x2="pad.left + plotW" :y1="panel.y(panel.directions[which].reference)" :y2="panel.y(panel.directions[which].reference)" stroke="#1f1f1f" stroke-width="1.4" stroke-dasharray="4 3" />
          <text v-if="panel.directions[which].reference !== null" :x="pad.left + plotW" :y="panel.y(panel.directions[which].reference) - 3" class="ref" text-anchor="end">reference</text>
          <g v-for="group in panel.directions[which].groups" :key="group.key">
            <circle v-for="point in group.points" :key="point.id" :cx="pad.left + (group.column + 0.5) * band + point.jitter" :cy="panel.y(point.value)" r="3" :fill="direction[2]" opacity=".6"><title>{{ point.id }}: {{ point.value }}</title></circle>
            <line v-if="group.median !== null" :x1="pad.left + (group.column + 0.15) * band" :x2="pad.left + (group.column + 0.85) * band" :y1="panel.y(group.median)" :y2="panel.y(group.median)" :stroke="direction[2]" stroke-width="2.2" />
            <text :x="pad.left + (group.column + 0.5) * band" :y="pad.top + plotH + 12" class="cat" :class="{ tilt: categories.items.length > 4 }" :transform="categories.items.length > 4 ? `rotate(-30 ${pad.left + (group.column + 0.5) * band} ${pad.top + plotH + 12})` : ''" :text-anchor="categories.items.length > 4 ? 'end' : 'middle'">{{ group.label }}</text>
          </g>
          <line :x1="pad.left" :x2="pad.left + plotW" :y1="pad.top + plotH" :y2="pad.top + plotH" stroke="#b9c3cc" />
        </svg>
      </template>
    </div>
    <div class="key">one dot = one run &nbsp;·&nbsp; bar = median &nbsp;·&nbsp; dashed = handwritten reference</div>
  </div>
</template>

<style scoped>
.panels { font-family: inherit; }
.grid { display: grid; align-items: center; column-gap: 10px; row-gap: 2px; }
.measure { font-size: 12px; font-weight: 600; color: #17243a; padding-left: 40px; }
.direction { font-size: 12px; font-weight: 600; text-align: right; padding-right: 4px; }
.tick, .cat, .ref { font-size: 9.5px; fill: #61718a; }
.ref { font-size: 8.5px; fill: #1f1f1f; }
.key { margin-top: 4px; font-size: 10.5px; color: #61718a; }
</style>
