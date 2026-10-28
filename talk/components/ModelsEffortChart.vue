<script setup>
import { computed, onMounted, ref } from 'vue'

const props = defineProps({
  initialMeasure: { type: String, default: 'wall_minutes' },
  showSetupFootnote: { type: Boolean, default: false },
})
const rows = ref([])
const setupCounts = ref(null)
const selected = ref(props.initialMeasure)
const choices = [
  ['wall_minutes', 'Wall time'],
  ['file_count', 'Files'],
  ['loc', 'LOC'],
  ['total_tokens', 'Tokens'],
]
const models = [
  ['claude-fable-5-1', 'Fable'],
  ['claude-opus-5-5', 'Opus'],
  ['claude-sonnet-5-5', 'Sonnet'],
  ['claude-haiku-5-5', 'Haiku'],
]
const efforts = ['low', 'medium', 'high']
const directions = ['python→javascript', 'javascript→python']

onMounted(async () => {
  const [response, countsResponse] = await Promise.all([
    fetch('/models-effort-runs.csv'),
    fetch('/models-effort-setup-counts.json'),
  ])
  if (!response.ok) throw new Error(`metrics CSV: HTTP ${response.status}`)
  if (!countsResponse.ok) throw new Error(`setup counts: HTTP ${countsResponse.status}`)
  const [header, ...lines] = (await response.text()).trim().split(/\r?\n/)
  const keys = header.split(',')
  rows.value = lines.map(line => Object.fromEntries(keys.map((key, index) => [key, line.split(',')[index]])))
  setupCounts.value = await countsResponse.json()
})

const maximum = computed(() => Math.max(1, ...rows.value.map(row => Number(row[selected.value]) || 0)))
function position(value) { return 8 + (Number(value) / maximum.value) * 188 }
function median(values) {
  if (!values.length) return null
  const sorted = [...values].sort((a, b) => a - b)
  const half = Math.floor(sorted.length / 2)
  return sorted.length % 2 ? sorted[half] : (sorted[half - 1] + sorted[half]) / 2
}
function formatted(value) {
  if (value === null) return '—'
  if (selected.value === 'total_tokens') return `${(value / 1_000_000).toFixed(1)}M`
  if (selected.value === 'wall_minutes') return `${value.toFixed(1)}m`
  return Number.isInteger(value) ? String(value) : value.toFixed(1)
}
const panels = computed(() => directions.map(direction => ({
  direction,
  groups: models.flatMap(([model, label]) => efforts.map(effort => {
    const selectedRows = rows.value.filter(row => row.direction === direction && row.model === model && row.effort === effort)
    const values = selectedRows.map(row => ({ id: row.run_id, value: Number(row[selected.value]) })).filter(row => Number.isFinite(row.value))
    return { key: `${model}-${effort}`, label, effort, n: selectedRows.length, values, median: median(values.map(row => row.value)) }
  })),
})))
</script>

<template>
  <div class="metrics">
    <div class="metric-tabs">
      <button v-for="[key, label] in choices" :key="key" :class="{ active: selected === key }" @click="selected = key">{{ label }}</button>
      <span>one dot = one run &nbsp;·&nbsp; tick = median</span>
    </div>
    <div v-if="rows.length" class="panels">
      <div v-for="panel in panels" :key="panel.direction" class="panel">
        <h3>{{ panel.direction === 'python→javascript' ? 'Python → JavaScript' : 'JavaScript → Python' }}</h3>
        <div v-for="group in panel.groups" :key="group.key" class="metric-row">
          <span class="model">{{ group.label }}</span>
          <span class="effort">{{ group.effort }}</span>
          <span class="n">n={{ group.n }}</span>
          <svg viewBox="0 0 205 26" aria-hidden="true">
            <line x1="8" x2="196" y1="13" y2="13" stroke="#d9e0e4" />
            <circle v-for="(run, index) in group.values" :key="run.id" :cx="position(run.value)" :cy="7 + (index % 4) * 4" r="2.4" :fill="group.effort === 'low' ? '#5d85a0' : group.effort === 'medium' ? '#e36836' : '#8f6ea5'" opacity=".75"><title>{{ run.id }}: {{ formatted(run.value) }}</title></circle>
            <line v-if="group.median !== null" :x1="position(group.median)" :x2="position(group.median)" y1="2" y2="24" stroke="#17243a" stroke-width="2.2" />
          </svg>
          <strong>{{ formatted(group.median) }}</strong>
        </div>
      </div>
    </div>
    <div v-else class="loading">Loading run measurements…</div>
    <div class="scale">0 <span>max {{ formatted(maximum) }} · {{ rows.length }} ports</span></div>
    <div v-if="showSetupFootnote && setupCounts" class="setup-footnote">
      <div>Prompt Dockerfile text changed: botbox 0.0.20 → 0.1.1 → 0.1.72.</div>
      <div>Fable low: {{ setupCounts['claude-fable-5-1'].low.before_236 }} before #236, {{ setupCounts['claude-fable-5-1'].low.after_236 }} after #236 (0.1.1); Fable high: {{ setupCounts['claude-fable-5-1'].high.before_236 }} before #236, {{ setupCounts['claude-fable-5-1'].high.after_236 }} after #236 (0.1.1).</div>
      <div>Opus high: {{ setupCounts['claude-opus-5-5'].high.before_236 }} before #236, {{ setupCounts['claude-opus-5-5'].high.after_241 }} after #241 (0.1.72); every other low / medium / high cell: all runs before #236.</div>
    </div>
  </div>
</template>

<style scoped>
.metrics { margin-top: -17px; }
.metric-tabs { display:flex; align-items:center; gap:6px; margin-bottom:9px; }
.metric-tabs button { border:1px solid #cdd6de; background:#fff; border-radius:16px; padding:4px 11px; font-size:12px; font-weight:700; color:#415369; cursor:pointer; }
.metric-tabs button.active { background:#17243a; color:#fff; border-color:#17243a; }
.metric-tabs span { margin-left:auto; color:#61718a; font-size:11px; }
.panels { display:grid; grid-template-columns:1fr 1fr; gap:20px; }
.panel { background:#fff; border:1px solid #dbe0e4; border-radius:7px; padding:7px 11px 9px; }
.panel h3 { font-size:14px; color:#17243a; margin:0 0 4px; }
.metric-row { display:grid; grid-template-columns:46px 42px 31px 1fr 48px; align-items:center; height:19.5px; gap:2px; font-size:10px; border-top:1px solid #eef0f1; }
.metric-row .model { font-weight:700; }
.metric-row .effort, .metric-row .n { color:#61718a; }
.metric-row svg { width:100%; height:20px; overflow:visible; }
.metric-row strong { text-align:right; font-size:10px; }
.loading { min-height:300px; display:grid; place-items:center; }
.scale { color:#61718a; font-size:10px; margin-top:6px; display:flex; justify-content:space-between; }
.setup-footnote { color:#61718a; font-size:9.5px; line-height:1.3; margin-top:7px; }
</style>
