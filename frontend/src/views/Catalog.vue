<template>
  <div class="flex flex-col min-h-screen pb-20">
    <div class="p-4">
      <h1 class="text-xl font-bold">Каталог</h1>
    </div>

    <!-- Дерево: Відділ -->
    <div class="px-4 space-y-2">
      <div v-for="division in divisions" :key="division.id">
        <button
          @click="toggleDivision(division.id)"
          class="w-full flex justify-between items-center py-3 px-4 rounded-xl bg-tg-secondary text-left active:opacity-70"
        >
          <span class="font-medium">{{ division.name }}</span>
          <span>{{ expanded.has(division.id) ? '▲' : '▼' }}</span>
        </button>

        <!-- Департаменти -->
        <div v-if="expanded.has(division.id)" class="ml-4 mt-1 space-y-1">
          <button
            v-for="dep in getDepartments(division.id)"
            :key="dep.id"
            @click="goToCarousel(dep.id)"
            class="w-full text-left py-2 px-4 rounded-xl bg-tg-bg border border-tg-hint/20 text-sm active:opacity-70"
          >
            {{ dep.name }}
            <span class="text-tg-hint ml-1">({{ productCount(dep.id) }})</span>
          </button>
        </div>
      </div>
    </div>

    <TabBar />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useCatalogStore } from '@/stores/catalog'
import TabBar from '@/components/TabBar.vue'

const router = useRouter()
const catalog = useCatalogStore()
const expanded = ref(new Set())

const divisions = computed(() =>
  catalog.categories.filter((c) => c.level === 'division')
)

function getDepartments(divisionId) {
  return catalog.categories.filter(
    (c) => c.parent_id === divisionId && c.level === 'department'
  )
}

function productCount(catId) {
  return (catalog.productsByCategory[catId] || []).length
}

function toggleDivision(id) {
  if (expanded.value.has(id)) expanded.value.delete(id)
  else expanded.value.add(id)
}

function goToCarousel(catId) {
  router.push({ name: 'Carousel', params: { categoryId: catId } })
}
</script>
