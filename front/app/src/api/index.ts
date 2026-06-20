import axios from 'axios'

// ============= КОНФИГУРАЦИЯ =============

const API_BASE_URL = 'http://localhost:5000/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// ============= ИНТЕРФЕЙСЫ =============

export interface User {
  id: number
  name: string
  role: 'patient' | 'doctor'
}

export interface Task {
  id: number
  doctor_id: number
  patient_id: number
  text: string
  dates: string[] // ["2024-01-15", "2024-01-16"]
  created_at: string
}

export interface TaskWithCompletion extends Task {
  is_completed: boolean
  completed_at: string | null
}

export interface TaskCompletion {
  id: number
  task_id: number
  date: string
  is_completed: boolean
  completed_at: string | null
}

export interface WellbeingLog {
  id: number
  patient_id: number
  date: string
  text: string
}

export interface ScheduleResponse {
  date: string
  tasks: TaskWithCompletion[]
  wellbeing: WellbeingLog | null
}

export interface CalendarDayData {
  total_tasks: number
  completed_tasks: number
  task_ids: number[]
}

export interface CalendarResponse {
  month: string
  days: Record<string, CalendarDayData> // { "2024-01-15": { total_tasks: 3, ... } }
}

export interface TaskCompletionMap {
  [date: string]: TaskCompletion
}

export interface TaskWithCompletions extends Task {
  completions: TaskCompletionMap
}

export interface DashboardResponse {
  tasks: TaskWithCompletions[]
  wellbeing_logs: WellbeingLog[]
}

// ============= ОБЩИЕ (AUTH / USERS) =============

export async function getUsers(): Promise<User[]> {
  const response = await api.get<User[]>('/users')
  return response.data
}

// ============= ПАЦИЕНТ =============

/**
 * Получить расписание пациента на конкретную дату
 */
export async function getPatientSchedule(
  patientId: number,
  date: string, // "YYYY-MM-DD"
): Promise<ScheduleResponse> {
  const response = await api.get<ScheduleResponse>(`/patients/${patientId}/schedule`, {
    params: { date },
  })
  return response.data
}

/**
 * Получить сводку календаря за месяц
 */
export async function getPatientCalendar(
  patientId: number,
  month: string, // "YYYY-MM"
): Promise<CalendarResponse> {
  const response = await api.get<CalendarResponse>(`/patients/${patientId}/calendar`, {
    params: { month },
  })
  return response.data
}

/**
 * Отметить задачу как выполненную
 */
export async function completeTask(
  patientId: number,
  taskId: number,
  date: string,
): Promise<TaskCompletion> {
  const response = await api.post<TaskCompletion>(
    `/patients/${patientId}/tasks/${taskId}/complete`,
    null,
    { params: { date } },
  )
  return response.data
}

/**
 * Сохранить самочувствие пациента за день
 */
export async function saveWellbeing(
  patientId: number,
  date: string,
  text: string,
): Promise<WellbeingLog> {
  const response = await api.post<WellbeingLog>(`/patients/${patientId}/wellbeing`, { date, text })
  return response.data
}

// ============= ВРАЧ =============

/**
 * Получить список пациентов врача
 */
export async function getDoctorPatients(doctorId: number): Promise<User[]> {
  const response = await api.get<User[]>(`/doctors/${doctorId}/patients`)
  return response.data
}

/**
 * Получить дашборд пациента (все задачи + самочувствие)
 */
export async function getPatientDashboard(
  doctorId: number,
  patientId: number,
): Promise<DashboardResponse> {
  const response = await api.get<DashboardResponse>(
    `/doctors/${doctorId}/patients/${patientId}/dashboard`,
  )
  return response.data
}

/**
 * Создать новую задачу для пациента
 */
export async function createTask(
  doctorId: number,
  patientId: number,
  text: string,
  dates: string[],
): Promise<Task> {
  const response = await api.post<Task>(`/doctors/${doctorId}/tasks`, {
    patient_id: patientId,
    text,
    dates,
  })
  return response.data
}
