<template>
  <div>
    <h2>Register</h2>
    <form @submit.prevent="register">
      <div>
        <label for="username">Username:</label>
        <input 
          v-model="username" 
          id="username" 
          type="text" 
          required 
          minlength="3" 
          maxlength="150"
          @input="resetMessages"
        />
      </div>
      <div>
        <label for="email">Email:</label>
        <input 
          v-model="email" 
          id="email" 
          type="email" 
          required 
          @input="resetMessages"
        />
      </div>
      <div>
        <label for="password">Password:</label>
        <input 
          v-model="password" 
          id="password" 
          type="password" 
          required 
          @input="resetMessages"
        />
      </div>
      <button type="submit">Register</button>
      <button type="button" @click="goToLogin">Login</button>
    </form>
    <p v-if="error" class="error">{{ error }}</p>
    <p v-if="success" class="success">{{ success }}</p>
  </div>
</template>

<script>
import { getCSRFToken } from '../store/auth'

export default {
  data() {
    return {
      username: '',  // Новое поле для username
      email: '',
      password: '',
      error: '',
      success: ''
    }
  },
  methods: {
    resetMessages() {
      this.error = ''
      this.success = ''
    },
    goToLogin(){
      this.$router.push('/login');
    },
    async register() {
      try {
        const response = await fetch('http://localhost:8000/api/register', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
          },
          body: JSON.stringify({
            username: this.username,  // Отправляем username
            email: this.email,
            password: this.password
          }),
          credentials: 'include'
        })
        const data = await response.json()
        if (response.ok) {
          this.success = 'Registration successful! Please log in.'
          setTimeout(() => {
            this.$router.push('/login')
          }, 1000)
        } else {
          this.error = data.error || 'Registration failed'
        }
      } catch (err) {
        this.error = 'An error occurred during registration: ' + err
      }
    }
  }
}
</script>

<style scoped>
.error {
  color: red;
}
.success {
  color: green;
}
</style>
