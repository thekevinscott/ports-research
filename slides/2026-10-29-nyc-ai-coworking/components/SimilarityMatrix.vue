<script setup>
import { computed, onMounted, ref } from 'vue'

const props = defineProps({
  src: { type: String, required: true },
  title: { type: String, default: '' },
  size: { type: Number, default: 420 },
  domain: { type: Array, default: () => [25, 85] },
})

const CONDITIONS = [
  ['neither', 'no tests', '#5d85a0'],
  ['unit tests', 'unit tests', '#e36836'],
  ['target integration tests', 'target integration', '#4f9d69'],
  ['both', 'both', '#7a5aa6'],
  ['reference', 'reference', '#1f1f1f'],
]
const RAMP = ['#eef5fd', '#86b6ef', '#3987e5', '#256abf', '#0d366b']

const data = ref(null)
onMounted(async () => {
  const response = await fetch(props.src)
  if (!response.ok) throw new Error(`${props.src}: HTTP ${response.status}`)
  data.value = await response.json()
})

const strip = 7
const gap = 3
const inset = strip + gap
const index = computed(() => Object.fromEntries((data.value?.items ?? []).map((item, i) => [item.id, i])))
const count = computed(() => data.value?.items.length ?? 1)
const cell = computed(() => (props.size - inset) / count.value)
function colour(value) {
  const [low, high] = props.domain
  const t = Math.min(1, Math.max(0, (value - low) / (high - low))) * (RAMP.length - 1)
  const i = Math.min(RAMP.length - 2, Math.floor(t))
  const f = t - i
  const mix = (a, b) => Math.round(parseInt(a, 16) * (1 - f) + parseInt(b, 16) * f)
  const hex = n => n.toString(16).padStart(2, '0')
  const [a, b] = [RAMP[i], RAMP[i + 1]]
  return `#${hex(mix(a.slice(1, 3), b.slice(1, 3)))}${hex(mix(a.slice(3, 5), b.slice(3, 5)))}${hex(mix(a.slice(5, 7), b.slice(5, 7)))}`
}
const swatch = Object.fromEntries(CONDITIONS.map(([key, , c]) => [key, c]))
const blocks = computed(() => {
  const items = data.value?.items ?? []
  const out = []
  items.forEach((item, i) => {
    const last = out[out.length - 1]
    if (last && last.condition === item.condition) last.end = i + 1
    else out.push({ condition: item.condition, start: i, end: i + 1 })
  })
  return out
})
const legendSteps = [25, 40, 55, 70, 85]
</script>

<template>
  <div class="matrix">
    <div v-if="title" class="title">{{ title }}</div>
    <svg v-if="data" :width="size + 100" :height="size + 8" :viewBox="`0 0 ${size + 100} ${size + 8}`">
      <g :transform="`translate(${inset}, ${inset})`">
        <rect v-for="[row, col, value] in data.cells" :key="row + col" :x="index[col] * cell" :y="index[row] * cell" :width="cell" :height="cell" :fill="colour(value)"><title>{{ row }} ↔ {{ col }}: {{ value }}%</title></rect>
        <g v-for="block in blocks" :key="block.condition">
          <rect :x="block.start * cell" :y="-inset" :width="(block.end - block.start) * cell - 1" :height="strip" :fill="swatch[block.condition]" />
          <rect :x="-inset" :y="block.start * cell" :width="strip" :height="(block.end - block.start) * cell - 1" :fill="swatch[block.condition]" />
          <line v-if="block.start" :x1="block.start * cell" :x2="block.start * cell" :y1="0" :y2="count * cell" stroke="#9aa3ab" stroke-width=".6" />
          <line v-if="block.start" :y1="block.start * cell" :y2="block.start * cell" :x1="0" :x2="count * cell" stroke="#9aa3ab" stroke-width=".6" />
        </g>
      </g>
      <g :transform="`translate(${size + 14}, ${inset})`">
        <text x="0" y="-4" class="key-title">similarity</text>
        <template v-for="(step, i) in legendSteps" :key="step">
          <rect x="0" :y="i * 14" width="12" height="12" :fill="colour(step)" />
          <text x="16" :y="i * 14 + 10" class="key">{{ step }}%</text>
        </template>
        <template v-for="([key, label, c], i) in CONDITIONS.filter(([k]) => blocks.some(b => b.condition === k))" :key="key">
          <rect x="0" :y="90 + i * 14" width="12" height="7" :fill="c" />
          <text x="16" :y="90 + i * 14 + 8" class="key">{{ label }}</text>
        </template>
      </g>
    </svg>
  </div>
</template>

<style scoped>
.matrix { display: inline-block; }
.title { font-size: 12px; font-weight: 600; color: #17243a; margin-bottom: 4px; }
.key, .key-title { font-size: 9px; fill: #61718a; }
.key-title { text-transform: uppercase; letter-spacing: .05em; }
</style>
