<script setup>
import { experiment, experiments } from './experiment.js'
</script>

<template>
  <span class="experiments"><button v-for="(entry, index) in experiments" :key="entry.key" :class="{ active: experiment === index }" @click.stop="experiment = index">{{ entry.label }}</button></span>
</template>

<style scoped>
.experiments { display:inline-flex; gap:2px; padding:3px; margin-left:auto; background:#e6ebf1; border-radius:9px; }
.experiments button { outline:none; border:none; background:none; border-radius:6px; padding:4px 11px; font-size:11px; font-weight:800; letter-spacing:.06em; text-transform:uppercase; color:#61718a; cursor:pointer; }
.experiments button.active { background:#fff; color:#17243a; box-shadow:0 1px 2px rgba(23,36,58,.18); }
</style>
