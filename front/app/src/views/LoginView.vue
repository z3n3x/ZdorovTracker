<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getUsers, type User } from '@/api'
import { useUserStore } from '@/stores/user'
import AppHeader from '@/components/AppHeader.vue'

const router = useRouter()
const userStore = useUserStore()

const users = ref<User[]>([])
const loading = ref(true)

async function loadUsers() {
  try {
    users.value = await getUsers()
  } catch (error) {
    console.error('Ошибка загрузки пользователей:', error)
  } finally {
    loading.value = false
  }
}

function selectUser(user: User) {
  userStore.setUser(user)

  if (user.role === 'patient') {
    router.push('/patient')
  } else {
    router.push('/doctor')
  }
}

onMounted(() => {
  if (userStore.user) {
    if (userStore.user.role === 'patient') {
      router.push('/patient')
    } else {
      router.push('/doctor')
    }
  } else {
    loadUsers()
  }
})
</script>

<template>
  <div class="login-page">
    <!-- Header -->
    <header class="header">
      <AppHeader title="ЗдоровТрекер"
        subtitle="Удобный сервис для учёта принимаемых лекарств и отслеживания динамики самочувствия." />
    </header>

    <!-- Main Content -->
    <main class="main-content">
      <h1 class="title">Выберите вашу роль</h1>

      <div v-if="loading" class="loading">
        <div class="spinner"></div>
      </div>

      <div v-else class="cards-row">
        <div v-for="user in users" :key="user.id" class="role-card""
          @click=" selectUser(user)">
          <div class="role-text">
            {{ user.role === 'doctor' ? 'Я врач' : 'Я пациент' }}
          </div>
        </div>
      </div>
    </main>

    <!-- Footer -->
    <footer class="footer">
      <span>Сделано с </span>
      <img src="/red-heart.svg" alt="❤" class="heart-icon" />
      <span> - Беляевым И.Д.</span>
    </footer>
  </div>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  background: #E5E5E5;
  display: flex;
  flex-direction: column;
  row-gap: 289px;
  align-items: flex-start;
  justify-content: center;
  padding: 0;
  position: relative;
  font-family: 'Iosevka Charon', monospace;
}

/* Header */
.header {
  padding: 53px 106px 0 106px;
  width: 100%;
}

/* Main Content */
.main-content {
  min-height: 213px;
  display: flex;
  flex-direction: column;
  row-gap: 45px;
  width: 100%;
  align-items: center;
  justify-content: center;
}

.title {
  font-family: 'Iosevka Charon', monospace;
  font-size: 32px;
  font-weight: 700;
  color: #000;
  margin: 0;
  text-align: left;
  min-height: 41px;
}

.loading {
  display: flex;
  justify-content: center;
  padding: 40px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #AF2F2F;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }

  100% {
    transform: rotate(360deg);
  }
}

.cards-row {
  display: flex;
  flex-direction: row;
  column-gap: 30px;
  align-items: center;
  justify-content: flex-start;
}

.role-card {
  min-width: 260px;
  min-height: 127px;
  background: white;
  display: flex;
  flex-direction: row;
  align-items: flex-end;
  justify-content: flex-start;
  padding: 78px 58px 17px 37px;
  border: 4px solid #d2d2d200;
  border-radius: 29px;
  cursor: pointer;
  transition: all 0.4s ease;
  box-sizing: border-box;
}

.role-card:hover {
  border: 4px solid #D2D2D2;
}

.role-text {
  font-family: 'Iosevka Charon', monospace;
  font-size: 16px;
  font-weight: 400;
  color: #808080;
  text-align: left;
}

/* Footer */
.footer {
  width: 100%;
  min-height: 20px;
  display: flex;
  flex-direction: row;
  column-gap: 6px;
  align-items: center;
  justify-content: center;
  padding: 0 50px;
  font-family: 'Iosevka Charon', monospace;
  font-size: 16px;
  font-weight: 400;
  color: #808080;
}

.heart-icon {
  width: 13px;
  height: 12px;
}
</style>