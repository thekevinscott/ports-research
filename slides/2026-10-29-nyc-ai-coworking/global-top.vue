<script setup>
import { computed } from 'vue'
import { useNav } from '@slidev/client'
const { currentSlideRoute } = useNav()
const show = computed(() => {
  const fm = currentSlideRoute.value?.meta?.slide?.frontmatter
  return fm?.qr !== false && fm?.layout !== 'section'
})
</script>

<template>
  <QrCode v-if="show" class="slide-qr" url="https://thekevinscott.com/talks/2026/october/nyc-ai-coworking/slides/" :size="32" />
</template>
