<template>
  <div class="login">
    <h1>Login</h1>
    <form @submit.prevent="login">
      <div>
        <label for="email">Email:</label>
        <input 
          v-model="email" 
          id="email" 
          type="text" 
          required
          @input="resetError"
        >
      </div>
      <div>
        <label for="password">Password:</label>
        <input 
          v-model="password" 
          id="password" 
          type="password" 
          required
          @input="resetError"
        >
      </div>
      <button type="submit">Login</button>
      <button type="button" @click="goToRegister">Register</button> <!-- Добавлен type="button" -->
    </form>
    <p v-if="error" class="error">{{ error }}</p>
  </div>
</template>
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
  data() {
    return {
      email: "",
      password: "",
      error: ""
    }
  },
  methods: {
    async login(){
      await this.authStore.login(this.email, this.password, this.$router)
      if (!this.authStore.isAuthenticated){
        this.error = 'Login failed. Please check your credentials.'
      }
    },
    resetError(){
      this.error = ""
    },
    goToRegister(){
      this.$router.push('/register'); // Используем this.$router
    }
  }
}
</script>
