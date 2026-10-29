<script setup>
import { computed } from 'vue'
import { useNav } from '@slidev/client'
const { currentSlideRoute } = useNav()
const show = computed(() => currentSlideRoute.value?.meta?.slide?.frontmatter?.qr !== false)
</script>

<template>
  <QrCode v-if="show" class="slide-qr" url="https://thekevinscott.com/talks/2026/october/nyc-ai-coworking/slides/" :size="32" />
</template>
