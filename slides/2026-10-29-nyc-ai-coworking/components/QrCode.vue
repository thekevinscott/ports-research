<script setup>
import { onMounted, ref } from 'vue'
import QRCode from 'qrcode'

const props = defineProps({
  url: { type: String, required: true },
  size: { type: Number, default: 260 },
})
const svg = ref('')
onMounted(async () => {
  svg.value = await QRCode.toString(props.url, { type: 'svg', margin: 1, width: props.size, color: { dark: '#17243a', light: '#ffffff00' } })
})
</script>

<template>
  <div class="qr" :style="{ width: `${size}px` }" v-html="svg" />
</template>

<style scoped>
.qr :deep(svg) { width: 100%; height: auto; display: block; }
</style>
