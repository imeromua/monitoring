<template>
  <div class="flex flex-col min-h-screen pb-20">
    <div class="p-4">
      <h1 class="text-xl font-bold">Каталог</h1>
    </div>

    <div class="px-4 space-y-2">
      <!-- Якщо є ієрархія (division -> department) -->
      <template v-if="hasDivisions">
        <div v-for="division in divisions" :key="division.id">
          <button
            @click="toggleDivision(division.id)"
            class="w-full flex justify-between items-center py-3 px-4 rounded-xl bg-tg-secondary text-left active:opacity-70"
          >
            <span class="font-medium">{{ division.name }}</span>
            <span>{{ expanded.has(division.id) ? '▲' : '▼' }}</span>
          </button>

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
      </template>

      <!-- Плаский список якщо немає ієрархії -->
      <template v-else>
        <button
          v-for="cat in flatCategories"
          :key="cat.id"
          @click="goToCarousel(cat.id)"
          class="w-full text-left py-3 px-4 rounded-xl bg-tg-secondary text-sm active:opacity-70"
        >
          <span class="font-medium">{{ cat.name }}</span>
          <span class="text-tg-hint ml-2">({{ productCount(cat.id) }})</span>
        </button>

        <p v-if="flatCategories.length === 0" class="text-center text-tg-hint text-sm py-10">
          Каталог порожній. Завантажте товари через адмін-панель.
        </p>
      </template>
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

const hasDivisions = computed(() => divisions.value.length > 0)

// Плаский список: всі категорії без батьківських (root-рівень) сортовані за ім'am
const flatCategories = computed(() =>
  catalog.categories
    .filter((c) => c.parent_id === null || c.parent_id === undefined)
    .sort((a, b) => a.sort_order - b.sort_order || a.name.localeCompare(b.name, 'uk'))
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
