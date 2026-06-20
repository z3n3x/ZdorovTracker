<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { getPatientCalendar, type CalendarDayData } from '@/api'

const props = defineProps<{
    patientId: number
    selectedDate: string
}>()

const emit = defineEmits<{
    (e: 'update:selectedDate', value: string): void
}>()

// Текущий месяц для отображения
const currentMonth = ref(new Date().toISOString().substring(0, 7))
const calendarData = ref<Record<string, CalendarDayData>>({})

// Загрузка данных календаря
async function loadCalendar() {
    try {
        const data = await getPatientCalendar(props.patientId, currentMonth.value)
        calendarData.value = data.days
    } catch (error) {
        console.error('Ошибка загрузки календаря:', error)
    }
}

// Генерация дней для отображения
const calendarDays = computed(() => {
    const [year, month] = currentMonth.value.split('-').map(Number)
    const lastDay = new Date(year, month, 0)
    const daysInMonth = lastDay.getDate()

    const days = []

    for (let day = 1; day <= daysInMonth; day++) {
        const dateStr = `${currentMonth.value}-${String(day).padStart(2, '0')}`
        days.push({
            date: dateStr,
            day: day,
            tasks: calendarData.value[dateStr] || null
        })
    }

    return days
})

// Форматирование месяца
const monthName = computed(() => {
    const date = new Date(currentMonth.value + '-01')
    return date.toLocaleDateString('ru-RU', { month: 'long' })
})

// Выбор даты
function selectDate(date: string) {
    emit('update:selectedDate', date)
}

// Следим за изменением месяца
watch(currentMonth, () => {
    loadCalendar()
})

// Загружаем данные при монтировании
loadCalendar()
</script>

<template>
    <div class="calendar-container">
        <!-- Заголовок месяца -->
        <div class="month-header">
            <div class="month-title">{{ monthName }}</div>
        </div>

        <!-- Сетка дней -->
        <div class="days-grid">
            <div v-for="day in calendarDays" :key="day.date" class="day-cell"
                :class="{ selected: day.date === selectedDate }" @click="selectDate(day.date)">
                <!-- Число дня -->
                <div class="day-number">{{ day.day }}</div>

                <!-- Счетчик задач -->
                <div v-if="day.tasks && day.tasks.total_tasks > 0" class="task-counter">
                    <!-- 1-3 задачи: отображаем сердечки -->
                    <template v-if="day.tasks.total_tasks <= 3">
                        <img v-for="i in day.tasks.total_tasks" :key="i" src="/red-heart.svg" alt="❤"
                            class="heart-icon" />
                    </template>
                    <!-- >3 задач: формат "N × ❤" -->
                    <template v-else>
                        <div class="task-count">{{ day.tasks.total_tasks }}</div>
                        <div class="task-multiply">×</div>
                        <img src="/red-heart.svg" alt="❤" class="heart-icon" />
                    </template>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
.calendar-container {
    width: 860px;
    display: flex;
    flex-direction: column;
    gap: 28px;
}

.month-header {
    display: flex;
    align-items: center;
}

.month-title {
    font-family: 'Iosevka Charon', monospace;
    font-size: 20px;
    font-weight: 700;
    color: #000;
}

.days-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 15px;
}

.day-cell {
    width: 110px;
    height: 73px;
    background: white;
    border-radius: 29px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: flex-start;
    padding: 9px 0 14px 0;
    cursor: pointer;
    transition: all 0.2s;
    border: 4px solid transparent;
}

.day-cell:hover {
    background: #f9f9f9;
}

.day-cell.selected {
    border-color: #D2D2D2;
}

.day-number {
    font-family: 'Iosevka Charon', monospace;
    font-size: 16px;
    font-weight: 400;
    color: #808080;
    text-align: center;
    line-height: 38px;
}

.task-counter {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 2px;
}

.heart-icon {
    width: 13px;
    height: 12px;
}

.task-count {
    font-family: 'Iosevka Charon', monospace;
    font-size: 14px;
    font-weight: 700;
    color: #000;
}

.task-multiply {
    font-family: 'Iosevka Charon', monospace;
    font-size: 14px;
    font-weight: 700;
    color: #808080;
}
</style>