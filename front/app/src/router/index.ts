import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '@/views/LoginView.vue'
import PatientView from '@/views/PatientView.vue'
import DoctorView from '@/views/DoctorView.vue'
import { useUserStore } from '@/stores/user'

const router = createRouter({
  history: createWebHistory('/'),
  routes: [
    {
      path: '/',
      name: 'login',
      component: LoginView,
    },
    {
      path: '/patient',
      name: 'patient',
      component: PatientView,
      meta: { requiresPatient: true },
    },
    {
      path: '/doctor',
      name: 'doctor',
      component: DoctorView,
      meta: { requiresDoctor: true },
    },
  ],
})

router.beforeEach((to, _from, next) => {
  const userStore = useUserStore()

  if (to.meta.requiresPatient && userStore.user?.role !== 'patient') {
    next('/')
  } else if (to.meta.requiresDoctor && userStore.user?.role !== 'doctor') {
    next('/')
  } else {
    next()
  }
})

export default router
