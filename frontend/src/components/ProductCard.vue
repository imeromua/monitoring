<template>
  <div class="bg-tg-secondary rounded-2xl p-4">
    <div class="flex justify-between items-start mb-1">
      <span class="text-xs text-tg-hint"># {{ product.article_id }}</span>
      <span v-if="product.weight_label" class="text-xs bg-tg-bg px-2 py-0.5 rounded-full text-tg-hint">
        {{ product.weight_label }}
      </span>
    </div>
    <h2 class="text-lg font-bold leading-tight mb-3">{{ product.name }}</h2>
  </div>
</template>

<script setup>
defineProps({
  product: { type: Object, required: true },
})
</script>
