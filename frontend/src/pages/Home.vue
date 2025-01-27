<script>
import { useAuthStore } from '../store/auth.js'
import { useRouter } from 'vue-router'
import { useLanguageStore } from '../store/language.js' // Импортируем хранилище языка

export default {
  setup() {
    const authStore = useAuthStore()
    const router = useRouter()
    const languageStore = useLanguageStore()

    return {
      authStore,
      router,
      languageStore
    }
  },
  methods: {
    async logout() {
      try {
        await this.authStore.logout(this.router)
      } catch (error) {
        console.error(error)
      }
    },
    goToGame() {
      this.router.push('/game');  // Переход в игру
    },
    changeLanguage(lang) {
      this.languageStore.setLanguage(lang)
    }
  },
  mounted() {
    this.authStore.fetchUser()
  }
}
</script>

<template>
  <div>
    <h1 v-if="!authStore.isAuthenticated">Welcome to the home page</h1>
    <div v-if="authStore.isAuthenticated">
      <h1>Word Guessing Game</h1>
      
      <!-- Выбор языка -->
      <div class="language-selection">
        <p>Choose Language:</p>
        <button 
          @click="changeLanguage('en')" 
          :class="{ active: languageStore.language === 'en' }"
        >
          English
        </button>
        <button 
          @click="changeLanguage('ru')" 
          :class="{ active: languageStore.language === 'ru' }"
        >
          Русский
        </button>
      </div>

      <p>Hi there {{ authStore.user?.username }}!</p>
      <p>You are logged in.</p>
      <button @click="logout">Logout</button>
      <button @click="goToGame">Play Game</button> <!-- Кнопка для игры -->
    </div>
    <p v-else>
      You are not logged in. <router-link to="/login">Login</router-link>
    </p>
  </div>
</template>

<style>
.language-selection {
  margin: 20px 0;
}

.language-selection button {
  padding: 10px 20px;
  margin: 0 10px;
  font-size: 16px;
  cursor: pointer;
  border: 2px solid #4a90e2;
  border-radius: 25px;
  background-color: white;
  color: #4a90e2;
  transition: background-color 0.3s ease, color 0.3s ease;
}

.language-selection button.active {
  background-color: #4a90e2;
  color: white;
}

.language-selection button:hover {
  background-color: #4a90e2;
  color: white;
}

button {
  padding: 10px 20px;
  font-size: 16px;
  cursor: pointer;
}

/* Остальные стили остаются без изменений */
</style>
