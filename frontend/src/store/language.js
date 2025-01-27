// src/store/language.js
import { defineStore } from 'pinia'

export const useLanguageStore = defineStore('language', {
  state: () => ({
    language: 'en', // По умолчанию английский
  }),
  actions: {
    setLanguage(lang) {
      this.language = lang
    }
  }
})
