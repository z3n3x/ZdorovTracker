<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
    getDoctorPatients,
    getPatientDashboard,
    createTask,
    type User,
    type TaskWithCompletions,
    type WellbeingLog
} from '@/api'
import { useUserStore } from '@/stores/user'
import AppHeader from '@/components/AppHeader.vue'

const router = useRouter()
const userStore = useUserStore()

if (!userStore.user || userStore.user.role !== 'doctor') {
    router.push('/')
}

const doctorId = userStore.user!.id

// Состояние
const patients = ref<User[]>([])
const selectedPatient = ref<User | null>(null)
const tasks = ref<TaskWithCompletions[]>([])
const wellbeingLogs = ref<WellbeingLog[]>([])
const loading = ref(false)

// Форма создания задачи
const newTaskText = ref('')
const newTaskDates = ref<string[]>([])
const showTaskForm = ref(false)

// Загрузка списка пациентов
async function loadPatients() {
    try {
        patients.value = await getDoctorPatients(doctorId)
    } catch (error) {
        console.error('Ошибка загрузки пациентов:', error)
    }
}

// Выбор пациента и загрузка его данных
async function selectPatient(patient: User) {
    selectedPatient.value = patient
    await loadPatientDashboard()
}

// Загрузка дашборда пациента
async function loadPatientDashboard() {
    if (!selectedPatient.value) return

    loading.value = true
    try {
        const data = await getPatientDashboard(doctorId, selectedPatient.value.id)
        tasks.value = data.tasks
        wellbeingLogs.value = data.wellbeing_logs
    } catch (error) {
        console.error('Ошибка загрузки дашборда:', error)
    } finally {
        loading.value = false
    }
}

// Создание задачи
async function createNewTask() {
    if (!selectedPatient.value || !newTaskText.value || newTaskDates.value.length === 0) {
        alert('Заполните все поля')
        return
    }

    try {
        await createTask(
            doctorId,
            selectedPatient.value.id,
            newTaskText.value,
            newTaskDates.value
        )

        // Сбрасываем форму
        newTaskText.value = ''
        newTaskDates.value = []
        showTaskForm.value = false

        // Перезагружаем данные
        await loadPatientDashboard()
    } catch (error) {
        console.error('Ошибка создания задачи:', error)
        alert('Ошибка создания задачи')
    }
}

// Добавление даты в список
function addDate(date: string) {
    if (!newTaskDates.value.includes(date)) {
        newTaskDates.value.push(date)
        newTaskDates.value.sort()
    }
}

// Удаление даты из списка
function removeDate(date: string) {
    newTaskDates.value = newTaskDates.value.filter(d => d !== date)
}

onMounted(() => {
    loadPatients()
})
</script>

<template>
    <div class="doctor-page">
        <!-- Header -->
        <header class="header">
            <AppHeader title="ЗдоровТрекер"
                subtitle="В данном разделе вы можете видеть всех ваших пациентов на данный момент, а также назначать задачи для принятия препаратов и следить за их самочувствием (в правой части экрана)" />
            <button @click="userStore.logout(); router.push('/')" class="logout-btn">Выйти</button>
        </header>

        <!-- Main Content -->
        <div class="main-content">
            <!-- Левая часть: Список пациентов -->
            <div class="patients-section">
                <h2 class="section-title">Под наблюдением</h2>

                <div class="patients-list">
                    <div v-for="patient in patients" :key="patient.id" class="patient-item"
                        :class="{ active: selectedPatient?.id === patient.id }" @click="selectPatient(patient)">
                        <div class="patient-icon">
                            <svg width="50" height="40" viewBox="0 0 50 40" fill="none"
                                xmlns="http://www.w3.org/2000/svg">
                                <path
                                    d="M25 22C29.42 22 33 18.42 33 14C33 9.58 29.42 6 25 6C20.58 6 17 9.58 17 14C17 18.42 20.58 22 25 22ZM25 26C18.66 26 9 28.68 9 34V38H41V34C41 28.68 31.34 26 25 26Z"
                                    fill="white" />
                            </svg>
                        </div>
                        <div class="patient-name">{{ patient.name }}</div>
                    </div>
                </div>
            </div>

            <!-- Правая часть: Дашборд пациента -->
            <div class="dashboard-section">
                <div v-if="!selectedPatient" class="no-selection">
                    Выберите пациента из списка слева
                </div>

                <div v-else class="dashboard-content">
                    <div class="patient-header">
                        <h3>{{ selectedPatient.name }}</h3>
                        <button @click="showTaskForm = !showTaskForm" class="add-task-btn">
                            {{ showTaskForm ? 'Отмена' : '+ Новая задача' }}
                        </button>
                    </div>

                    <!-- Форма создания задачи -->
                    <div v-if="showTaskForm" class="task-form">
                        <div class="form-group">
                            <label>Текст задачи:</label>
                            <textarea v-model="newTaskText" placeholder="Например: Принять 5г антидепрессанта"
                                class="task-text-input"></textarea>
                        </div>

                        <div class="form-group">
                            <label>Даты выполнения:</label>
                            <input type="date"
                                @change="addDate(($event.target as HTMLInputElement).value); ($event.target as HTMLInputElement).value = ''"
                                class="date-picker" />
                            <div class="selected-dates">
                                <div v-for="date in newTaskDates" :key="date" class="date-tag">
                                    {{ date }}
                                    <span @click="removeDate(date)" class="remove-date">×</span>
                                </div>
                            </div>
                        </div>

                        <button @click="createNewTask" class="create-btn">Создать задачу</button>
                    </div>

                    <!-- Задачи -->
                    <div v-if="loading" class="loading">Загрузка...</div>

                    <div v-else class="tasks-container">
                        <h4>Назначенные задачи</h4>
                        <div v-if="tasks.length === 0" class="no-tasks">
                            Задач пока нет
                        </div>
                        <div v-else class="tasks-list">
                            <div v-for="task in tasks" :key="task.id" class="task-card">
                                <div class="task-text">{{ task.text }}</div>
                                <div class="task-dates">
                                    <div v-for="date in task.dates" :key="date" class="task-date" :class="{
                                        completed: task.completions[date]?.is_completed,
                                        missed: !task.completions[date]?.is_completed && new Date(date) < new Date()
                                    }">
                                        {{ date }}
                                        <span v-if="task.completions[date]?.is_completed" class="completion-time">
                                            ✓ {{ new
                                                Date(task.completions[date].completed_at).toLocaleTimeString('ru-RU', {
                                                    hour: '2-digit', minute: '2-digit'
                                                }) }}
                                        </span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Самочувствие пациента -->
                        <h4>Самочувствие пациента</h4>
                        <div v-if="wellbeingLogs.length === 0" class="no-logs">
                            Записей о самочувствии нет
                        </div>
                        <div v-else class="wellbeing-logs">
                            <div v-for="log in wellbeingLogs" :key="log.id" class="wellbeing-log">
                                <div class="log-date">{{ log.date }}</div>
                                <div class="log-text">{{ log.text }}</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
.doctor-page {
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
}

/* Main Content */
.main-content {
    display: flex;
    gap: 40px;
    padding: 171px 106px 0 106px;
    min-height: calc(100vh - 171px);
}

/* Patients Section */
.patients-section {
    flex: 0 0 800px;
}

.section-title {
    font-size: 20px;
    font-weight: 700;
    color: #000;
    margin: 0 0 20px 0;
}

.patients-list {
    display: flex;
    flex-direction: column;
    gap: 15px;
}

.patient-item {
    display: flex;
    align-items: center;
    gap: 20px;
    padding: 20px;
    background: white;
    border-radius: 29px;
    cursor: pointer;
    transition: all 0.3s ease;
    border: 4px solid transparent;
}

.patient-item:hover {
    border: 4px solid #D2D2D2;
}

.patient-item.active {
    border: 4px solid #D2D2D2;
}

.patient-icon {
    width: 50px;
    height: 40px;
    background: #808080;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.patient-name {
    font-size: 16px;
    font-weight: 400;
    color: #808080;
}

/* Dashboard Section */
.dashboard-section {
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

.no-selection {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: #808080;
    font-size: 18px;
}

.dashboard-content {
    display: flex;
    flex-direction: column;
    gap: 20px;
}

.patient-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
}

.patient-header h3 {
    font-size: 24px;
    font-weight: 700;
    color: #000;
    margin: 0;
}

.add-task-btn {
    padding: 10px 20px;
    background: #6AB97F;
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-family: inherit;
    font-size: 14px;
    font-weight: 600;
}

/* Task Form */
.task-form {
    background: white;
    padding: 20px;
    border-radius: 16px;
    margin-bottom: 20px;
}

.form-group {
    margin-bottom: 20px;
}

.form-group label {
    display: block;
    margin-bottom: 8px;
    font-weight: 600;
    color: #000;
}

.task-text-input {
    width: 100%;
    min-height: 80px;
    padding: 10px;
    border: 1px solid #D2D2D2;
    border-radius: 8px;
    font-family: inherit;
    font-size: 14px;
    resize: vertical;
}

.date-picker {
    padding: 8px;
    border: 1px solid #D2D2D2;
    border-radius: 8px;
    margin-bottom: 10px;
    font-family: inherit;
}

.selected-dates {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}

.date-tag {
    background: #E3F2FD;
    padding: 6px 12px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 14px;
}

.remove-date {
    cursor: pointer;
    font-weight: bold;
    color: #AF2F2F;
}

.create-btn {
    padding: 10px 20px;
    background: #6AB97F;
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-family: inherit;
    font-size: 14px;
    font-weight: 600;
}

/* Tasks Container */
.tasks-container {
    display: flex;
    flex-direction: column;
    gap: 20px;
}

.tasks-container h4 {
    font-size: 18px;
    font-weight: 700;
    color: #000;
    margin: 0;
}

.tasks-list {
    display: flex;
    flex-direction: column;
    gap: 15px;
}

.task-card {
    background: white;
    padding: 15px;
    border-radius: 12px;
}

.task-text {
    font-size: 16px;
    font-weight: 600;
    margin-bottom: 10px;
    color: #000;
}

.task-dates {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}

.task-date {
    background: #F5F5F5;
    padding: 6px 10px;
    border: 1px solid #D2D2D2;
    border-radius: 6px;
    font-size: 13px;
    color: #000;
}

.task-date.completed {
    background: #E8F5E9;
    border-color: #6AB97F;
}

.task-date.missed {
    background: #FFEBEE;
    border-color: #AF2F2F;
}

.completion-time {
    display: block;
    font-size: 11px;
    color: #6AB97F;
    margin-top: 4px;
}

/* Wellbeing Logs */
.wellbeing-logs {
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.wellbeing-log {
    background: white;
    padding: 12px;
    border-radius: 10px;
}

.log-date {
    font-weight: 600;
    margin-bottom: 6px;
    color: #808080;
    font-size: 13px;
}

.log-text {
    line-height: 1.5;
    color: #000;
    font-size: 14px;
}

.loading {
    text-align: center;
    padding: 40px;
    color: #808080;
}

.no-tasks,
.no-logs {
    text-align: center;
    color: #808080;
    padding: 20px;
    font-size: 14px;
}
</style>