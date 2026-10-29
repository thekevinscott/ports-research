<script setup>
import { computed, onMounted, ref } from 'vue'

const props = defineProps({
  src: { type: String, required: true },
  by: { type: String, required: true },
  initialMeasure: { type: String, default: 'wall_minutes' },
  measures: { type: Array, default: null },
  reference: { type: String, default: null },
})
const REFERENCE_COLOR = '#1f1f1f'

const MEASURES = [
  ['wall_minutes', 'Wall time'],
  ['total_tokens', 'Tokens'],
  ['cost_usd', 'Cost'],
  ['file_count', 'Files'],
  ['loc', 'LOC'],
  ['diff_lines_changed', 'Diff lines'],
  ['embedding_distance', 'Embedding distance'],
  ['behavior_agreement_pct', 'Behaviour %'],
  ['api_agreement_pct', 'API %'],
]
const DIRECTIONS = [
  ['python→javascript', 'Python → TypeScript', '#5d85a0'],
  ['javascript→python', 'TypeScript → Python', '#e36836'],
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
const layout = LAYOUTS[props.by]
const twoLabels = layout.headers.length === 2

onMounted(async () => {
  if (props.reference) reference.value = await (await fetch(props.reference)).json()
  const response = await fetch(props.src)
  if (!response.ok) throw new Error(`${props.src}: HTTP ${response.status}`)
  const [header, ...lines] = (await response.text()).trim().split(/\r?\n/)
  const keys = header.split(',')
  rows.value = lines.map(line => Object.fromEntries(keys.map((key, index) => [key, line.split(',')[index]])))
  await new Promise(resolve => requestAnimationFrame(resolve))
  const strip = panel.value?.querySelector('.strip')
  if (!strip) return
  const observer = new ResizeObserver(() => { vw.value = strip.clientWidth || 800 })
  observer.observe(strip)
})

const choices = computed(() => MEASURES.filter(([key]) =>
  (props.measures ? props.measures.includes(key) : true) && rows.value.some(row => row[key] !== undefined && row[key] !== '')))
const percent = computed(() => selected.value.endsWith('_pct'))
function nice(value) {
  const power = 10 ** Math.floor(Math.log10(value))
  const step = [1, 2, 2.5, 4, 5, 10].find(candidate => candidate * power >= value)
  return step * power
}
const referenceValues = computed(() => DIRECTIONS.map(([direction]) => reference.value[direction]?.[selected.value] ?? null))
const maximum = computed(() => percent.value ? 100 : nice(Math.max(1e-9, ...referenceValues.value.filter(v => v !== null), ...rows.value.map(row => Number(row[selected.value]) || 0))))
function position(value) { return 8 + (Number(value) / maximum.value) * (vw.value - 16) }
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
  return Number.isInteger(value) ? String(value) : value.toFixed(0)
}
function series(direction, match) {
  const values = rows.value
    .filter(row => row.direction === direction && match(row))
    .map(row => ({ id: row.run_id, value: Number(row[selected.value]) }))
    .filter(row => row.value === row.value && row[selected.value] !== '')
  return { values, median: median(values.map(row => row.value)) }
}
const groups = computed(() => layout.groups.map(group => ({
  ...group,
  rows: group.rows.map(row => ({ ...row, series: DIRECTIONS.map(([direction]) => series(direction, row.match)) })),
})))
const ticks = [0, 0.25, 0.5, 0.75, 1]
const lanes = props.by === 'pooled' ? 24 : 4
const rowHeight = twoLabels ? 19 : props.by === 'pooled' ? 220 : 38
</script>

<template>
  <div class="strips" :class="{ two: twoLabels, pooled: by === 'pooled' }">
    <div class="tabs">
      <button v-for="[key, label] in choices" :key="key" :class="{ active: selected === key }" @click.stop="selected = key">{{ label }}</button>
      <span>one dot = one run &nbsp;·&nbsp; tick = median</span>
    </div>
    <div v-if="rows.length" class="panel" ref="panel">
      <div class="row head">
        <span v-for="header in layout.headers" :key="header" class="label">{{ header }}</span>
        <span class="legend"><button v-for="([key, label, color], which) in DIRECTIONS" :key="key" :class="{ off: !shown[which] }" @click.stop="shown[which] = !shown[which]"><i :style="{ background: color }"></i>{{ label }}</button><span v-if="referenceValues.some(v => v !== null)" class="reference-key"><i></i>handwritten reference</span></span>
      </div>
      <div v-for="group in groups" :key="group.label" class="group">
        <span class="label group-label" :style="{ gridRow: `span ${group.rows.length}` }">{{ group.label }}</span>
        <template v-for="row in group.rows" :key="row.key">
          <span v-if="twoLabels" class="label sub">{{ row.label }}</span>
          <div class="strip"><svg :viewBox="`0 0 ${vw} ${rowHeight}`" :height="rowHeight" aria-hidden="true">
            <line v-for="tick in ticks" :key="tick" :x1="8 + tick * (vw - 16)" :x2="8 + tick * (vw - 16)" y1="0" :y2="rowHeight" stroke="#eceae4" />
            <template v-for="(run, which) in row.series" :key="which">
              <template v-if="shown[which]">
              <circle v-for="(point, index) in run.values" :key="point.id" :cx="position(point.value)" :cy="4 + ((index + which * 2) % lanes) * ((rowHeight - 8) / (lanes - 1))" r="2.4" :fill="DIRECTIONS[which][2]" opacity=".7"><title>{{ point.id }}: {{ formatted(point.value) }}</title></circle>
              <line v-if="run.median !== null" :x1="position(run.median)" :x2="position(run.median)" :y1="2" :y2="rowHeight - 2" :stroke="DIRECTIONS[which][2]" stroke-width="2.4" opacity=".85" />
              <line v-if="referenceValues[which] !== null" :x1="position(referenceValues[which])" :x2="position(referenceValues[which])" y1="0" :y2="rowHeight" :stroke="REFERENCE_COLOR" stroke-width="1.6" stroke-dasharray="3 2"><title>reference {{ DIRECTIONS[which][1] }}: {{ formatted(referenceValues[which]) }}</title></line>
              </template>
            </template>
          </svg></div>
        </template>
      </div>
      <div class="row axis">
        <span v-for="header in layout.headers" :key="header"></span>
        <div class="ticks">
          <span v-for="tick in ticks" :key="tick" :style="{ left: `calc(1% + ${tick} * 98%)` }" :class="{ first: tick === 0, last: tick === 1 }">{{ formatted(maximum * tick) }}</span>
        </div>
      </div>
    </div>
    <div v-else class="loading">Loading run measurements…</div>
  </div>
</template>

<style scoped>
.strips { margin-top: 6px; }
.tabs { display:flex; align-items:center; gap:6px; margin-bottom:9px; }
.tabs button { border:1px solid #cdd6de; background:#fff; border-radius:16px; padding:4px 11px; font-size:12px; font-weight:700; color:#415369; cursor:pointer; }
.tabs button.active { background:#17243a; color:#fff; border-color:#17243a; }
.tabs span { margin-left:auto; color:#61718a; font-size:11px; }
.panel { background:#fff; border:1px solid #dbe0e4; border-radius:7px; padding:2px 14px 4px; --cols: 118px 1fr; }
.strips.two .panel { --cols: 48px 50px 1fr; }
.row, .group { display:grid; grid-template-columns: var(--cols); align-items:center; column-gap:6px; font-size:10.5px; }
.group { border-top:1.5px solid #b9c3cc; }
.group .sub, .group .strip { border-top:1px solid #d9e0e4; }
.group .sub { align-self:stretch; display:flex; align-items:center; }
.group .strip { width:100%; }
.group svg { width:100%; overflow:visible; display:block; }
.label { font-weight:700; color:#17243a; }
.sub { font-weight:400; color:#61718a; }
.group-label { align-self:center; }
.head { height:18px; color:#61718a; }
.head .label { font-weight:700; font-size:10px; text-transform:uppercase; letter-spacing:.06em; color:#61718a; }
.legend { display:flex; gap:12px; padding-left:1%; }
.legend button { border:none; background:none; padding:0 4px; font:inherit; color:#17243a; cursor:pointer; }
.legend button.off { opacity:.35; text-decoration:line-through; }
.legend i { display:inline-block; width:8px; height:8px; border-radius:50%; margin-right:4px; vertical-align:-1px; }
.reference-key { padding:0 4px; color:#17243a; }
.reference-key i { width:0; height:10px; border-radius:0; border-left:2px dashed #1f1f1f; vertical-align:-2px; }
.axis { height:15px; }
.ticks { position:relative; height:14px; }
.ticks span { position:absolute; top:0; transform:translateX(-50%); font-size:10px; color:#61718a; white-space:nowrap; }
.ticks span.first { transform:none; }
.ticks span.last { transform:translateX(-100%); }
.loading { min-height:300px; display:grid; place-items:center; }
</style>
