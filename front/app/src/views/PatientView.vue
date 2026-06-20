<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import {
    getPatientSchedule,
    completeTask,
    saveWellbeing,
    type TaskWithCompletion,
} from '@/api'
import { useUserStore } from '@/stores/user'
import AppHeader from '@/components/AppHeader.vue'
import CalendarView from '@/components/CalendarView.vue'

const router = useRouter()
const userStore = useUserStore()

if (!userStore.user || userStore.user.role !== 'patient') {
    router.push('/')
}

const patientId = userStore.user!.id

// Состояние
const selectedDate = ref(new Date().toISOString().split('T')[0])
const tasks = ref<TaskWithCompletion[]>([])
const wellbeingText = ref('')
const loading = ref(false)

// Загрузка расписания на выбранную дату
async function loadSchedule() {
    loading.value = true
    try {
        const data = await getPatientSchedule(patientId, selectedDate.value)
        tasks.value = data.tasks
        wellbeingText.value = data.wellbeing?.text || ''
    } catch (error) {
        console.error('Ошибка загрузки расписания:', error)
    } finally {
        loading.value = false
    }
}

// Отметить задачу как выполненную
async function markTaskCompleted(taskId: number) {
    try {
        await completeTask(patientId, taskId, selectedDate.value)
        await loadSchedule()
    } catch (error) {
        console.error('Ошибка отметки задачи:', error)
    }
}

// Сохранить самочувствие
async function saveWellbeingLog() {
    try {
        await saveWellbeing(patientId, selectedDate.value, wellbeingText.value)
    } catch (error) {
        console.error('Ошибка сохранения самочувствия:', error)
    }
}

// Следим за изменением даты
watch(selectedDate, () => {
    loadSchedule()
})

onMounted(() => {
    loadSchedule()
})
</script>

<template>
    <div class="patient-page">
        <!-- Header -->
        <header class="header">
            <AppHeader title="ЗдоровТрекер"
                subtitle="Здесь вы можете наблюдать календарь с расписанием приема медикаментов, а также отмечать принятие препаратов и описывать свое самочувствие (в правой части экрана)" />
            <button @click="userStore.logout(); router.push('/')" class="logout-btn">Выйти</button>
        </header>

        <!-- Main Content -->
        <div class="main-content">
            <!-- Левая часть: Календарь -->
            <div class="calendar-section">
                <CalendarView :patient-id="patientId" v-model:selected-date="selectedDate" />
            </div>

            <!-- Правая часть: Задачи и самочувствие -->
            <div class="right-section">
                <div v-if="loading" class="loading">Загрузка...</div>

                <div v-else class="content-container">
                    <!-- Задачи -->
                    <div class="tasks-section">
                        <h3>Задачи на {{ selectedDate }}</h3>

                        <div v-if="tasks.length === 0" class="no-tasks">
                            На этот день задач нет
                        </div>

                        <div v-else class="tasks-list">
                            <div v-for="task in tasks" :key="task.id" class="task-item"
                                :class="{ completed: task.is_completed }">
                                <input type="checkbox" :checked="task.is_completed" @change="markTaskCompleted(task.id)"
                                    class="task-checkbox" />
                                <div class="task-content">
                                    <div class="task-text">{{ task.text }}</div>
                                    <div v-if="task.is_completed" class="task-time">
                                        ✓ Выполнено в {{ new Date(task.completed_at!).toLocaleTimeString('ru-RU', {
                                        hour: '2-digit', minute: '2-digit' }) }}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Самочувствие -->
                    <div class="wellbeing-section">
                        <h3>Самочувствие</h3>
                        <textarea v-model="wellbeingText" placeholder="Опишите ваше самочувствие за этот день..."
                            @blur="saveWellbeingLog" class="wellbeing-textarea"></textarea>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
.patient-page {
    min-height: 100vh;
    background: #E5E5E5;
    font-family: 'Iosevka Charon', monospace;
    padding: 0;
    position: relative;
}

/* Header */
.header {
    position: relative;
    padding: 53px 106px 0 106px;
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 40px;
}

.logout-btn {
    padding: 8px 16px;
    background: #AF2F2F;
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-family: inherit;
    font-size: 14px;
    flex-shrink: 0;
    margin-top: 8px;
}

/* Main Content */
.main-content {
    display: flex;
    gap: 40px;
    padding: 82px 106px 0 106px;
    min-height: calc(100vh - 171px);
}

/* Calendar Section */
.calendar-section {
    flex: 0 0 860px;
}

/* Right Section */
.right-section {
    flex: 1;
    min-width: 678px;
    max-width: 678px;
    height: 670px;
    background: #C9C9C9;
    border: 4px solid #D2D2D2;
    border-radius: 29px;
    padding: 30px;
    overflow-y: auto;
}

.loading {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: #808080;
    font-size: 18px;
}

.content-container {
    display: flex;
    flex-direction: column;
    gap: 30px;
}

/* Tasks Section */
.tasks-section {
    background: white;
    border-radius: 16px;
    padding: 20px;
}

.tasks-section h3 {
    font-size: 20px;
    font-weight: 700;
    color: #000;
    margin: 0 0 20px 0;
}

.no-tasks {
    text-align: center;
    color: #808080;
    padding: 40px;
    font-size: 16px;
}

.tasks-list {
    display: flex;
    flex-direction: column;
    gap: 15px;
}

.task-item {
    display: flex;
    gap: 15px;
    padding: 15px;
    border: 1px solid #e0e0e0;
    border-radius: 12px;
    transition: all 0.2s;
}

.task-item.completed {
    background: #f1f8f4;
    border-color: #6AB97F;
}

.task-checkbox {
    width: 24px;
    height: 24px;
    cursor: pointer;
    margin-top: 2px;
}

.task-content {
    flex: 1;
}

.task-text {
    font-size: 16px;
    margin-bottom: 5px;
    color: #000;
}

.task-time {
    color: #6AB97F;
    font-size: 14px;
}

/* Wellbeing Section */
.wellbeing-section {
    background: white;
    border-radius: 16px;
    padding: 20px;
}

.wellbeing-section h3 {
    font-size: 20px;
    font-weight: 700;
    color: #000;
    margin: 0 0 15px 0;
}

.wellbeing-textarea {
    width: 100%;
    min-height: 120px;
    padding: 12px;
    border: 1px solid #D2D2D2;
    border-radius: 8px;
    font-family: inherit;
    font-size: 14px;
    resize: vertical;
}

.wellbeing-textarea:focus {
    outline: none;
    border-color: #6AB97F;
}
</style>