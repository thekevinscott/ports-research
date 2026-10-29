<script setup>
import { onMounted, ref, watch } from 'vue'
import embed from 'vega-embed'

const props = defineProps({
  srcs: { type: Array, required: true },
  panels: { type: Array, default: null },
  rename: { type: Object, default: () => ({}) },
  collapse: { type: Boolean, default: false },
  width: { type: Number, default: 220 },
  height: { type: Number, default: 130 },
  fontSize: { type: Number, default: 11 },
})
const el = ref(null)

const LABELS = [[/python → javascript\*?/g, 'Python → TypeScript'], [/javascript → python\*?/g, 'TypeScript → Python']]
function relabel(text) {
  let out = props.rename[text] ?? text
  for (const [pattern, replacement] of LABELS) out = out.replace(pattern, replacement)
  return out
}

function keepLayer(layer) {
  const type = typeof layer.mark === 'string' ? layer.mark : layer.mark?.type
  if (type === 'text') return false
  if (type === 'rule' && layer.encoding?.y?.field === 'level') return false
  return true
}

function restyle(layer) {
  const mark = typeof layer.mark === 'string' ? { type: layer.mark } : { ...layer.mark }
  const enc = layer.encoding ?? {}
  if (mark.type === 'point') Object.assign(mark, { stroke: '#5d85a0', fill: '#5d85a0', fillOpacity: 0.45, size: 60, strokeWidth: 1.5 })
  if (mark.type === 'tick') Object.assign(mark, { color: '#17243a', thickness: 2.5, size: 26 })
  if (mark.type === 'rule' && enc.y2) Object.assign(mark, { color: '#5d85a0', opacity: 0.2, strokeWidth: 8 })
  if (mark.type === 'rule' && !enc.y2) Object.assign(mark, { color: '#e36836', strokeDash: [4, 3] })
  layer.mark = mark
  delete enc.shape
  if (enc.x) {
    enc.x = { ...enc.x, axis: { labelAngle: 0, labelExpr: "split(replace(datum.label, ' + ', '+'), ' ')", title: null } }
    if (props.collapse) {
      const band = props.width / 1.6
      enc.x.scale = { domain: ['all runs'], paddingInner: 0, paddingOuter: 0.3 }
      enc.x.sort = ['all runs']
      if (enc.xOffset) enc.xOffset = { field: 'jitter', type: 'quantitative', scale: { domain: [-1, 1], range: [band * 0.2, band * 0.8] } }
    }
  }
  if (enc.y?.axis) enc.y.axis = { ...enc.y.axis, labelFontSize: props.fontSize, titleFontSize: props.fontSize }
}

async function render() {
  const specs = await Promise.all(props.srcs.map(async (src) => {
    const response = await fetch(src)
    if (!response.ok) throw new Error(`${src}: HTTP ${response.status}`)
    return response.json()
  }))
  const datasets = Object.assign({}, ...specs.map(spec => spec.datasets ?? {}))
  const panels = specs.flatMap((spec) => {
    const items = spec.concat ?? spec.hconcat ?? [spec]
    return items.map((panel) => {
      const copy = JSON.parse(JSON.stringify(panel))
      if (!copy.data && spec.data) copy.data = spec.data
      const title = typeof copy.title === 'string' ? copy.title : copy.title?.text ?? ''
      copy.title = { text: relabel(title), anchor: 'start', color: '#17243a', fontSize: props.fontSize + 1, fontWeight: 600 }
      copy.width = props.width
      copy.height = props.height
      copy.layer = (copy.layer ?? []).filter(keepLayer)
      for (const layer of copy.layer) restyle(layer)
      if (props.collapse) copy.transform = [...(copy.transform ?? []), { calculate: "'all runs'", as: 'condition' }, { calculate: 'random() * 2 - 1', as: 'jitter' }]
      return { title, spec: copy }
    })
  })
  const kept = props.panels ? props.panels.map(name => panels.find(p => p.title === name)?.spec).filter(Boolean) : panels.map(p => p.spec)
  const spec = {
    $schema: 'https://vega.github.io/schema/vega-lite/v5.json',
    background: 'transparent',
    datasets,
    hconcat: kept,
    spacing: 18,
    config: {
      font: 'ui-sans-serif, system-ui, sans-serif',
      axis: { labelColor: '#61718a', titleColor: '#61718a', domainColor: '#dbe0e4', tickColor: '#dbe0e4', gridColor: '#eceae4', labelFontSize: props.fontSize, titleFontSize: props.fontSize },
      view: { stroke: null },
    },
  }
  if (el.value) await embed(el.value, spec, { actions: false, renderer: 'svg' })
}

onMounted(render)
watch(() => [props.srcs, props.panels, props.collapse], render, { deep: true })
</script>

<template>
  <div ref="el" class="vega-chart" />
</template>
