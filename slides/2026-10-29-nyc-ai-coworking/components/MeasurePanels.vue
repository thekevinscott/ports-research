<script setup>
import { computed, onMounted, ref } from 'vue'
import { withBase } from './experiment.js'

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
  reference_diff_similarity_pct: 'Lines shared with reference (%)',
  embedding_distance: 'Embedding distance',
  behavior_agreement_pct: 'Behaviour agreement (%)',
  api_agreement_pct: 'API agreement (%)',
  ladder_ref_ratio: 'Ladder time ÷ reference (1 = same speed)',
}
const DIRECTIONS = [
  ['python→javascript', 'Python → TypeScript', '#5d85a0', 'handwritten TypeScript'],
  ['javascript→python', 'TypeScript → Python', '#e36836', 'handwritten Python'],
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
  if (props.reference) reference.value = await (await fetch(withBase(props.reference))).json()
  const response = await fetch(withBase(props.src))
  if (!response.ok) throw new Error(`${props.src}: HTTP ${response.status}`)
  const [header, ...lines] = (await response.text()).trim().split(/\r?\n/)
  const keys = header.split(',')
  rows.value = lines.map(line => Object.fromEntries(keys.map((key, index) => [key, line.split(',')[index]])))
})

const categories = CATEGORIES[props.by]
const pad = { left: 52, right: 8, top: 8, bottom: categories.items.length > 4 ? 30 : 20 }
const uid = Math.random().toString(36).slice(2, 8)
const ranges = ref({})
const knob = ref(null)
function grab(measure, which, event) {
  event.currentTarget.setPointerCapture(event.pointerId)
  knob.value = { measure, which }
}
function slide(panel, event) {
  if (!knob.value || knob.value.measure !== panel.measure) return
  const rect = event.currentTarget.ownerSVGElement.getBoundingClientRect()
  const py = ((event.clientY - rect.top) / rect.height) * props.height
  const value = Math.max(0, Math.min(panel.domainMax, ((pad.top + plotH - py) / plotH) * panel.domainMax))
  const gap = panel.domainMax / 50
  const [lo, hi] = [panel.lo, panel.hi]
  ranges.value = { ...ranges.value, [panel.measure]: knob.value.which === 'lo' ? [Math.min(value, hi - gap), hi] : [lo, Math.max(value, lo + gap)] }
}
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
  const domainStep = percent ? 25 : niceStep(Math.max(1e-9, ...all, ...refs) / 4)
  const domainMax = percent ? 100 : domainStep * Math.ceil(Math.max(1e-9, ...all, ...refs) * 1.06 / domainStep)
  const extentMin = Math.min(...all, ...refs)
  const extentMax = Math.max(...all, ...refs)
  const margin = (extentMax - extentMin) * 0.06
  const [lo, hi] = ranges.value[measure] ?? (extentMax > extentMin ? [Math.max(0, extentMin - margin), extentMax + margin] : [0, domainMax])
  const step = niceStep((hi - lo) / 4)
  const y = value => pad.top + plotH - ((value - lo) / (hi - lo)) * plotH
  const sliderY = value => pad.top + plotH - (value / domainMax) * plotH
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
  const first = Math.ceil(lo / step) * step
  const ticks = Array.from({ length: Math.floor((hi - first) / step) + 1 }, (_, i) => first + i * step)
  return { measure, label: LABELS[measure] ?? measure, lo, hi, domainMax, y, sliderY, ticks, directions, any: all.length > 0 }
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
          <defs><clipPath :id="`clip-${uid}-${panel.measure}-${which}`"><rect :x="pad.left - 1" :y="pad.top - 4" :width="plotW + 2" :height="plotH + 8" /></clipPath></defs>
          <g class="y-slider">
            <line x1="8" x2="8" :y1="pad.top" :y2="pad.top + plotH" class="track" />
            <line x1="8" x2="8" :y1="panel.sliderY(panel.hi)" :y2="panel.sliderY(panel.lo)" class="selected" />
            <circle v-for="which2 in ['lo', 'hi']" :key="which2" cx="8" :cy="panel.sliderY(which2 === 'lo' ? panel.lo : panel.hi)" r="5" class="knob"
              @pointerdown.stop.prevent="grab(panel.measure, which2, $event)" @pointermove.stop="slide(panel, $event)" @pointerup.stop="knob = null" @pointercancel.stop="knob = null" />
          </g>
          <g v-for="t in panel.ticks" :key="t">
            <line :x1="pad.left" :x2="pad.left + plotW" :y1="panel.y(t)" :y2="panel.y(t)" stroke="#e6e3dc" />
            <text :x="pad.left - 5" :y="panel.y(t) + 3" class="tick" text-anchor="end">{{ tick(t, panel.measure) }}</text>
          </g>
          <g :clip-path="`url(#clip-${uid}-${panel.measure}-${which})`">
          <line v-if="panel.directions[which].reference !== null" :x1="pad.left" :x2="pad.left + plotW" :y1="panel.y(panel.directions[which].reference)" :y2="panel.y(panel.directions[which].reference)" stroke="#1f1f1f" stroke-width="1.4" stroke-dasharray="4 3" />
          <text v-if="panel.directions[which].reference !== null" :x="pad.left + plotW" :y="panel.y(panel.directions[which].reference) - 3" class="ref" text-anchor="end">{{ referenceLine === null ? direction[3] : 'reference' }}</text>
          <g v-for="group in panel.directions[which].groups" :key="group.key">
            <circle v-for="point in group.points" :key="point.id" :cx="pad.left + (group.column + 0.5) * band + point.jitter" :cy="panel.y(point.value)" r="3" :fill="direction[2]" opacity=".6"><title>{{ point.id }}: {{ point.value }}</title></circle>
            <line v-if="group.median !== null" :x1="pad.left + (group.column + 0.15) * band" :x2="pad.left + (group.column + 0.85) * band" :y1="panel.y(group.median)" :y2="panel.y(group.median)" stroke="#1f1f1f" stroke-width="4.6" stroke-linecap="round" />
            <line v-if="group.median !== null" :x1="pad.left + (group.column + 0.15) * band" :x2="pad.left + (group.column + 0.85) * band" :y1="panel.y(group.median)" :y2="panel.y(group.median)" :stroke="direction[2]" stroke-width="2.4" stroke-linecap="round" />
          </g>
          </g>
          <g v-for="group in panel.directions[which].groups" :key="`label-${group.key}`">
            <text :x="pad.left + (group.column + 0.5) * band" :y="pad.top + plotH + 12" class="cat" :class="{ tilt: categories.items.length > 4 }" :transform="categories.items.length > 4 ? `rotate(-30 ${pad.left + (group.column + 0.5) * band} ${pad.top + plotH + 12})` : ''" :text-anchor="categories.items.length > 4 ? 'end' : 'middle'">{{ group.label }}</text>
          </g>
          <line :x1="pad.left" :x2="pad.left + plotW" :y1="pad.top + plotH" :y2="pad.top + plotH" stroke="#b9c3cc" />
        </svg>
      </template>
    </div>
    <div class="key">one dot = one run &nbsp;·&nbsp; bar = median &nbsp;·&nbsp; dashed = the handwritten version in the target language</div>
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
.y-slider .track { stroke: #e4e3de; stroke-width: 4; stroke-linecap: round; }
.y-slider .selected { stroke: #94a3b8; stroke-width: 4; stroke-linecap: round; }
.y-slider .knob { fill: #fff; stroke: #334155; stroke-width: 1.5; cursor: ns-resize; touch-action: none; }
</style>
