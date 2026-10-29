<script setup>
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { experiment, experiments, withBase } from './experiment.js'
import ExperimentTabs from './ExperimentTabs.vue'

const props = defineProps({
  src: { type: String, default: null },
  by: { type: String, default: null },
  sources: { type: Object, default: null },
  compact: { type: Boolean, default: false },
  initialMeasure: { type: String, default: 'wall_minutes' },
  measures: { type: Array, default: null },
  reference: { type: String, default: null },
  referenceLine: { type: Number, default: null },
})
const REFERENCE_COLOR = '#1f1f1f'

const MEASURES = [
  ['wall_minutes', 'Wall time'],
  ['total_tokens', 'Tokens'],
  ['cost_usd', 'Cost'],
  ['file_count', 'Files'],
  ['loc', 'LOC'],
  ['diff_lines_changed', 'Diff lines vs reference'],
  ['reference_diff_similarity_pct', 'Lines shared with reference %'],
  ['embedding_distance', 'Embedding distance'],
  ['behavior_agreement_pct', 'Behaviour %'],
  ['api_agreement_pct', 'API %'],
  ['ladder_ref_ratio', 'Parse time ÷ reference'],
]
const DIRECTIONS = [
  ['python→javascript', 'Python → TypeScript', '#5d85a0', 'handwritten TypeScript'],
  ['javascript→python', 'TypeScript → Python', '#e36836', 'handwritten Python'],
]
const LAYOUTS = {
  'model-effort': {
    headers: ['model', 'effort'],
    groups: [
      ['claude-fable-5-1', 'Fable'],
      ['claude-opus-5-5', 'Opus'],
      ['claude-sonnet-5-5', 'Sonnet'],
      ['claude-haiku-5-5', 'Haiku'],
    ].map(([model, label]) => ({
      label,
      rows: [['low', 'low'], ['medium', 'medium'], ['high', 'high'], ['xhigh', 'very high']].map(([effort, label]) => ({ key: `${model}-${effort}`, label, match: row => row.model === model && row.effort === effort })),
    })),
  },
  pooled: {
    headers: ['runs'],
    groups: [{ label: 'all', rows: [{ key: 'all', label: '', match: () => true }] }],
  },
  condition: {
    headers: ['tests seen'],
    groups: [
      ['none', 'no tests'],
      ['unit', 'unit'],
      ['source', 'source integration'],
      ['target', 'target integration'],
      ['unit + source', 'unit + source'],
      ['unit + target', 'unit + target'],
      ['source + target', 'source + target'],
      ['all', 'all three'],
    ].map(([condition, label]) => ({ label, rows: [{ key: condition, label: '', match: row => row.condition === condition }] })),
  },
}

const rows = ref([])
const reference = ref({})
const panel = ref(null)
const vw = ref(800)
const selected = ref(props.initialMeasure)
const shown = ref([true, true])
const active = computed(() => props.sources ? experiments[experiment.value] : null)
const currentSrc = computed(() => active.value ? props.sources[active.value.key] : props.src)
const currentBy = computed(() => active.value ? active.value.by : props.by)
const layout = computed(() => LAYOUTS[currentBy.value])
const twoLabels = computed(() => layout.value.headers.length === 2)

const cache = new Map()
async function fetchRows(src) {
  const response = await fetch(withBase(src))
  if (!response.ok) throw new Error(`${src}: HTTP ${response.status}`)
  const [header, ...lines] = (await response.text()).trim().split(/\r?\n/)
  const keys = header.split(',')
  return lines.map(line => Object.fromEntries(keys.map((key, index) => [key, line.split(',')[index]])))
}
function measure() { vw.value = panel.value?.querySelector('.strip')?.clientWidth || 800 }
let observer = null
async function load() {
  const src = currentSrc.value
  if (!cache.has(src)) cache.set(src, fetchRows(src))
  rows.value = await cache.get(src)
  range.value = null
  await nextTick()
  await new Promise(resolve => requestAnimationFrame(resolve))
  measure()
  if (!observer && panel.value) {
    observer = new ResizeObserver(measure)
    observer.observe(panel.value)
  }
}
watch(currentSrc, load)
onMounted(async () => {
  if (props.reference) reference.value = await (await fetch(withBase(props.reference))).json()
  await load()
})

const choices = computed(() => MEASURES.filter(([key]) =>
  (props.measures ? props.measures.includes(key) : true) && rows.value.some(row => row[key] !== undefined && row[key] !== '')))
const percent = computed(() => selected.value.endsWith('_pct'))
function nice(value) {
  const power = 10 ** Math.floor(Math.log10(value))
  const step = [1, 2, 2.5, 4, 5, 10].find(candidate => candidate * power >= value)
  return step * power
}
const displayed = computed(() => rows.value.filter(row => layout.value.groups.some(group => group.rows.some(r => r.match(row)))))
const referenceValues = computed(() => DIRECTIONS.map(([direction]) => props.referenceLine ?? reference.value[direction]?.[selected.value] ?? null))
const extent = computed(() => {
  const values = [...referenceValues.value.filter(v => v !== null), ...displayed.value.map(row => row[selected.value]).filter(v => v !== undefined && v !== '').map(Number)]
  if (!values.length) return [0, 1]
  const [min, max] = [Math.min(...values), Math.max(...values)]
  if (max <= min) return [0, max || 1]
  const margin = (max - min) * 0.03
  return [min >= 0 ? Math.max(0, min - margin) : min - margin, max + margin]
})
const domainMax = computed(() => percent.value ? 100 : extent.value[1])
const range = ref(null)
const knob = ref(null)
watch(selected, () => { range.value = null })
watch(choices, list => { if (list.length && !list.some(([key]) => key === selected.value)) selected.value = list[0][0] })
const lo = computed(() => range.value?.[0] ?? extent.value[0])
const hi = computed(() => range.value?.[1] ?? extent.value[1])
function position(value) { return 8 + ((Number(value) - lo.value) / (hi.value - lo.value)) * (vw.value - 16) }
function visible(value) { return value >= lo.value && value <= hi.value }
function sliderX(value) { return 8 + (value / domainMax.value) * (vw.value - 16) }
function grab(which, event) {
  event.currentTarget.setPointerCapture(event.pointerId)
  knob.value = which
}
function slide(event) {
  if (!knob.value) return
  const rect = event.currentTarget.ownerSVGElement.getBoundingClientRect()
  const px = ((event.clientX - rect.left) / rect.width) * vw.value
  const value = Math.max(0, Math.min(domainMax.value, ((px - 8) / (vw.value - 16)) * domainMax.value))
  const gap = domainMax.value / 50
  range.value = knob.value === 'lo' ? [Math.min(value, hi.value - gap), hi.value] : [lo.value, Math.max(value, lo.value + gap)]
}
function median(values) {
  if (!values.length) return null
  const sorted = [...values].sort((a, b) => a - b)
  const half = Math.floor(sorted.length / 2)
  return sorted.length % 2 ? sorted[half] : (sorted[half - 1] + sorted[half]) / 2
}
function formatted(value) {
  if (value === null) return '—'
  if (selected.value === 'total_tokens') return `${(value / 1_000_000).toFixed(1)}M`
  if (selected.value === 'wall_minutes') return `${value.toFixed(1)} min`
  if (selected.value === 'cost_usd') return `$${value.toFixed(2)}`
  if (percent.value) return `${Math.round(value)}%`
  if (selected.value === 'embedding_distance') return value.toFixed(3)
  if (selected.value === 'ladder_ref_ratio') return value.toFixed(2)
  return Number.isInteger(value) ? String(value) : value.toFixed(0)
}
function series(direction, match) {
  const values = rows.value
    .filter(row => row.direction === direction && match(row) && row[selected.value] !== undefined && row[selected.value] !== '')
    .map(row => ({ id: row.run_id, value: Number(row[selected.value]) }))
    .filter(row => row.value === row.value)
  return { values, median: median(values.map(row => row.value)) }
}
const groups = computed(() => layout.value.groups.map(group => ({
  ...group,
  rows: group.rows.map(row => ({ ...row, series: DIRECTIONS.map(([direction]) => series(direction, row.match)) })),
})))
const ticks = computed(() => {
  const step = nice((hi.value - lo.value) / 5)
  const first = Math.ceil(lo.value / step) * step
  return Array.from({ length: Math.floor((hi.value - first) / step) + 1 }, (_, i) => first + i * step).map(value => (value - lo.value) / (hi.value - lo.value))
})
const lanes = computed(() => currentBy.value === 'pooled' ? 24 : 4)
const rowHeight = computed(() => twoLabels.value ? (props.compact ? 14 : 18) : currentBy.value === 'pooled' ? 220 : currentBy.value === 'condition' ? (props.compact ? 26 : 36) : 38)
</script>

<template>
  <div class="strips" :class="{ two: twoLabels, pooled: currentBy === 'pooled' }">
    <div class="tabs">
      <template v-if="choices.length > 1"><button v-for="[key, label] in choices" :key="key" :class="{ active: selected === key }" @click.stop="selected = key">{{ label }}</button></template>
      <ExperimentTabs v-if="active" />
    </div>
    <div v-if="rows.length" class="panel" ref="panel">
      <div class="row head">
        <span v-for="header in layout.headers" :key="header" class="label">{{ header }}</span>
        <span class="legend"><button v-for="([key, label, color], which) in DIRECTIONS" :key="key" :class="{ off: !shown[which] }" @click.stop="shown[which] = !shown[which]"><i :style="{ background: color }"></i>{{ label }}</button><template v-if="referenceLine === null"><span v-for="([key, , color, target], which) in DIRECTIONS" :key="key + target" v-show="referenceValues[which] !== null" class="reference-key"><i :style="{ borderColor: color }"></i>{{ target }}</span></template></span>
      </div>
      <div v-for="group in groups" :key="group.label" class="group">
        <span class="label group-label" :style="{ gridRow: `span ${group.rows.length}` }">{{ group.label }}</span>
        <template v-for="row in group.rows" :key="row.key">
          <span v-if="twoLabels" class="label sub">{{ row.label }}</span>
          <div class="strip"><svg :viewBox="`0 0 ${vw} ${rowHeight}`" :height="rowHeight" aria-hidden="true">
            <line v-for="tick in ticks" :key="tick" :x1="8 + tick * (vw - 16)" :x2="8 + tick * (vw - 16)" y1="0" :y2="rowHeight" stroke="#eceae4" />
            <template v-for="(run, which) in row.series" :key="which">
              <template v-if="shown[which]">
              <template v-for="(point, index) in run.values" :key="point.id"><circle v-if="visible(point.value)" :cx="position(point.value)" :cy="4 + ((index + which * 2) % lanes) * ((rowHeight - 8) / (lanes - 1))" r="2.4" :fill="DIRECTIONS[which][2]" opacity=".7"><title>{{ point.id }}: {{ formatted(point.value) }}</title></circle></template>
              <line v-if="run.median !== null && visible(run.median)" :x1="position(run.median)" :x2="position(run.median)" :y1="2" :y2="rowHeight - 2" :stroke="DIRECTIONS[which][2]" stroke-width="2.4" opacity=".85" />
              <line v-if="referenceValues[which] !== null && visible(referenceValues[which])" :x1="position(referenceValues[which])" :x2="position(referenceValues[which])" y1="0" :y2="rowHeight" :stroke="referenceLine === null ? DIRECTIONS[which][2] : REFERENCE_COLOR" stroke-width="1.6" stroke-dasharray="3 2"><title>{{ DIRECTIONS[which][3] }}: {{ formatted(referenceValues[which]) }}</title></line>
              </template>
            </template>
          </svg></div>
        </template>
      </div>
      <div class="row axis">
        <span v-for="header in layout.headers" :key="header"></span>
        <div class="ticks">
          <span v-for="tick in ticks" :key="tick" :style="{ left: `calc(1% + ${tick} * 98%)` }" :class="{ first: tick < 0.04, last: tick > 0.96 }">{{ formatted(lo + (hi - lo) * tick) }}</span>
        </div>
      </div>
      <div class="row slider">
        <span v-for="header in layout.headers" :key="header"></span>
        <div class="strip"><svg :viewBox="`0 0 ${vw} 18`" height="18" aria-hidden="true">
          <line :x1="8" :x2="vw - 8" y1="9" y2="9" class="track" />
          <line :x1="sliderX(lo)" :x2="sliderX(hi)" y1="9" y2="9" class="selected" />
          <circle v-for="which in ['lo', 'hi']" :key="which" :cx="sliderX(which === 'lo' ? lo : hi)" cy="9" r="6" class="knob"
            @pointerdown.stop.prevent="grab(which, $event)" @pointermove.stop="slide" @pointerup.stop="knob = null" @pointercancel.stop="knob = null" />
        </svg></div>
      </div>
    </div>
    <div v-if="rows.length" class="note">one dot = one run &nbsp;·&nbsp; tick = median</div>
    <div v-else class="loading">Loading run measurements…</div>
  </div>
</template>

<style scoped>
.strips { margin-top: 3px; }
.tabs { display:flex; align-items:center; gap:6px; margin-bottom:6px; }
.tabs button { border:1px solid #cdd6de; background:#fff; border-radius:16px; padding:4px 11px; font-size:12px; font-weight:700; color:#415369; cursor:pointer; }
.tabs button.active { background:#17243a; color:#fff; border-color:#17243a; }
.note { text-align:right; color:#61718a; font-size:9.5px; margin-top:3px; }
.panel { background:#fff; border:1px solid #dbe0e4; border-radius:7px; padding:2px 14px 4px; --cols: 118px 1fr; }
.strips.two .panel { --cols: 48px 50px 1fr; }
.row, .group { display:grid; grid-template-columns: var(--cols); align-items:center; column-gap:6px; font-size:10.5px; line-height:1.3; }
.group { border-top:1.5px solid #b9c3cc; }
.group .sub, .group .strip { border-top:1px solid #d9e0e4; }
.group .sub { align-self:stretch; display:flex; align-items:center; }
.group .strip { width:100%; }
.group svg { width:100%; overflow:visible; display:block; }
.label { font-weight:700; color:#17243a; }
.sub { font-weight:400; color:#61718a; }
.group-label { align-self:center; }
.head { min-height:18px; color:#61718a; }
.head .label { font-weight:700; font-size:10px; text-transform:uppercase; letter-spacing:.06em; color:#61718a; }
.legend { display:flex; flex-wrap:wrap; gap:2px 12px; padding-left:1%; }
.legend button { border:none; background:none; padding:0 4px; font:inherit; color:#17243a; cursor:pointer; white-space:nowrap; }
.legend button.off { opacity:.35; text-decoration:line-through; }
.legend i { display:inline-block; width:8px; height:8px; border-radius:50%; margin-right:4px; vertical-align:-1px; }
.reference-key { padding:0 4px; color:#17243a; white-space:nowrap; }
.reference-key i { width:0; height:10px; border-radius:0; border-left:2px dashed #1f1f1f; vertical-align:-2px; }
.axis { height:15px; }
.slider { height:18px; }
.slider svg { width:100%; display:block; overflow:visible; }
.slider .track { stroke:#e4e3de; stroke-width:4; stroke-linecap:round; }
.slider .selected { stroke:#94a3b8; stroke-width:4; stroke-linecap:round; }
.slider .knob { fill:#fff; stroke:#334155; stroke-width:1.5; cursor:ew-resize; touch-action:none; }
.ticks { position:relative; height:14px; }
.ticks span { position:absolute; top:0; transform:translateX(-50%); font-size:10px; color:#61718a; white-space:nowrap; }
.ticks span.first { transform:none; }
.ticks span.last { transform:translateX(-100%); }
.loading { min-height:300px; display:grid; place-items:center; }
</style>
