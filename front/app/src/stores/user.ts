import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { User } from '@/api'

export const useUserStore = defineStore('user', () => {
  const user = ref<User | null>(null)

  function setUser(u: User) {
    user.value = u
    // Сохраняем в localStorage
    localStorage.setItem('user', JSON.stringify(u))
  }

  function loadUser() {
    const saved = localStorage.getItem('user')
    if (saved) {
      user.value = JSON.parse(saved)
    }
  }

  function logout() {
    user.value = null
    localStorage.removeItem('user')
  }

  return { user, setUser, loadUser, logout }
})
