import { ref } from 'vue'

export const experiments = [
  { key: 'models-effort', label: 'Models × effort', by: 'model-effort' },
  { key: 'tests', label: 'Tests experiment', by: 'condition' },
]
export const experiment = ref(0)

export const withBase = (path) => path.startsWith('/') ? import.meta.env.BASE_URL.replace(/\/$/, '') + path : path
