<script>
import { useAuthStore } from '../store/auth.js'
import { useRouter } from 'vue-router'

export default {
  setup() {
    const authStore = useAuthStore()
    const router = useRouter()

    return {
      authStore, router
    }
  },
  methods: {
    async logout() {
      try {
        await this.authStore.logout(this.$router)
      } catch (error) {
        console.error(error)
      }
    },
    goToGame() {
      this.router.push('/game');  // Переход в игру
    }
  },
  async mounted() {
    await this.authStore.fetchUser()
  }
}
</script>

<template>
  <h1 v-if="!authStore.isAuthenticated">Welcome to the home page</h1>
  <div v-if="authStore.isAuthenticated">
    <h1>Word Guessing Game</h1>
    <!-- <div class="search-container">
      <input type="text" v-model="searchQuery" placeholder="Search for players..." />
      <button @click="searchPlayers">Search</button>
    </div> -->
    <p>Hi there {{ authStore.user?.username }}!</p>
    <p>You are logged in.</p>
    <button @click="logout">Logout</button>
    <button @click="goToGame">Play Game</button> <!-- Кнопка для игры -->
  </div>
  <p v-else>
    You are not logged in. <router-link to="/login">Login</router-link>
  </p>
</template>

<style>
.search-container input[type="text"] {
  width: 300px;
  padding: 10px 15px;
  font-size: 16px;
  border: 1px solid #ccc;
  border-radius: 25px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  outline: none;
  transition: all 0.3s ease;
}

.search-container input[type="text"]:focus {
  border-color: #4a90e2;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
}

.search-container button {
  margin-left: 10px;
  padding: 10px 20px;
  font-size: 16px;
  color: white;
  background-color: #4a90e2;
  border: none;
  border-radius: 25px;
  cursor: pointer;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.search-container button:hover {
  background-color: #357abd;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
}

.search-container button:active {
  transform: scale(0.98);
}
</style>