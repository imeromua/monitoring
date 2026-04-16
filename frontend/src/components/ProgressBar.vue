<template>
  <div class="mt-1">
    <div class="flex justify-between text-xs text-tg-hint mb-1">
      <span>{{ current }} з {{ total }}</span>
      <span>{{ percent }}%</span>
    </div>
    <div class="w-full h-1.5 bg-tg-secondary rounded-full overflow-hidden">
      <div
        class="h-full bg-tg-button rounded-full transition-all duration-300"
        :style="{ width: percent + '%' }"
      />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  current: { type: Number, default: 0 },
  total: { type: Number, default: 1 },
})

const percent = computed(() =>
  props.total > 0 ? Math.round((props.current / props.total) * 100) : 0
)
</script>
