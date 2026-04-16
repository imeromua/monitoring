<template>
  <div class="select-none">
    <!-- Дисплей введеного значення -->
    <div class="bg-tg-secondary rounded-2xl py-4 px-6 text-center mb-3">
      <span class="text-4xl font-light tracking-wider">
        {{ displayValue || '0.00' }}
      </span>
      <span class="text-tg-hint text-lg ml-1">грн</span>
    </div>

    <!-- Клавіатура -->
    <div class="grid grid-cols-3 gap-2">
      <button
        v-for="key in keys"
        :key="key"
        @click="press(key)"
        class="py-5 rounded-2xl bg-tg-secondary text-xl font-medium active:bg-tg-hint/30 transition-colors"
      >
        {{ key === 'del' ? '⌫' : key }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({ modelValue: { type: String, default: '' } })
const emit = defineEmits(['update:modelValue'])

const keys = ['1','2','3','4','5','6','7','8','9','.','0','del']

const displayValue = computed(() => props.modelValue)

function press(key) {
  let val = props.modelValue
  if (key === 'del') {
    val = val.slice(0, -1)
  } else if (key === '.' && val.includes('.')) {
    return
  } else if (val.includes('.') && val.split('.')[1]?.length >= 2) {
    // Не більше 2 знаків після коми
    return
  } else {
    if (val === '' && key === '.') val = '0'
    val += key
  }
  emit('update:modelValue', val)
}
</script>
