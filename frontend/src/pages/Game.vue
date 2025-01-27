<template>
  <div id="app">
    <!-- Экран выбора сложности -->
    <div class="start-screen" v-if="!gameStarted">
      <h1>Word Guessing Game</h1>
      <!-- <div class="stats">
        <p>Streak: {{ streak }}</p>
      </div> -->
      <label>Choose Difficulty:</label>
      <div class="difficulty-options">
        <label>
          <input type="radio" value="easy" v-model="difficulty" /> Easy
        </label>
        <label>
          <input type="radio" value="medium" v-model="difficulty" /> Medium
        </label>
        <label>
          <input type="radio" value="hard" v-model="difficulty" /> Hard
        </label>
      </div>

      <button @click="startGame">Start Game</button>
    </div>

    <!-- Экран игры -->
    <div v-else class="game">
      <!-- Заголовок игрового экрана -->
      <div class="header">
        <h2>Streak: {{ streak }}</h2>
      </div>

      <!-- Индикатор загрузки -->
      <div v-if="isLoading" class="loading">
        <div class="spinner"></div>
        <p>Loading word...</p>
      </div>

      <!-- Игровая сетка -->
      <div v-else>
        <div class="board" :style="{ gridTemplateRows: `repeat(${rowSize}, 1fr)` }">
          <div
            v-for="(row, rowIndex) in grid"
            :key="rowIndex"
            class="row"
          >
            <div
              v-for="(cell, colIndex) in row"
              :key="colIndex"
              class="cell"
              :class="getCellClass(rowIndex, colIndex)"
            >
              {{ cell ? cell.letter : '' }}
            </div>
          </div>
        </div>

        <!-- Клавиатура -->
        <div class="keyboard">
          <div v-for="(row, rowIndex) in keyboard" :key="rowIndex" class="keyboard-row">
            <button
              v-for="key in row"
              :key="key"
              :class="['keyboard-button', getKeyClass(key), { 'key-pressed': isKeyPressed(key) }]"
              @click="handleKeyPress(key)"
            >
              {{ key }}
            </button>
          </div>
          <button class="backspace" @click="handleBackspace">Backspace</button>
        </div>

        <!-- Кнопка отправки догадки -->
        <button class="submit-button" @click="submitGuess" :disabled="currentGuess.length !== colSize">Submit</button>
      </div>
    </div>
  </div>
</template>

<script>
import Swal from 'sweetalert2'; // Импортируем SweetAlert2
import russianWords from '../assets/russian-words.json'; // Импортируем локальный список русских слов
import { useLanguageStore } from '../store/language.js' // Импортируем хранилище языка

export default {
  data() {
    return {
      gameStarted: false,
      difficulty: 'easy', // Выбранная сложность
      rowSize: 8, // Количество попыток (по умолчанию для easy)
      colSize: 5, // Длина слова (по умолчанию для easy)
      wordToGuess: '', // Загаданное слово
      currentGuess: '', // Текущая догадка
      grid: [], // Игровая сетка
      keyboard: [], // Клавиатура будет динамически изменяться
      usedKeys: {}, // Статус использованных клавиш
      currentRowIndex: 0, // Индекс текущей строки
      validatedRows: [], // Отметки валидированных строк
      pressedKeys: new Set(), // Нажатые клавиши
      isLoading: false, // Индикатор загрузки
      streak: 0, // Количество подряд отгаданных слов
      languageStore: null, // Ссылка на хранилище языка
      languageConfig: { // Конфигурация языков
        en: {
          keyboardLayout: [
            ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
            ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
            ['Z', 'X', 'C', 'V', 'B', 'N', 'M']
          ],
          difficultyConfig: {
            easy: { minLength: 4, maxLength: 6, attempts: 8 },
            medium: { minLength: 6, maxLength: 8, attempts: 6 },
            hard: { minLength: 8, maxLength: 10, attempts: 4 }
          },
          api: {
            generateWord: 'https://random-word-api.herokuapp.com/word',
            validateWord: 'https://api.dictionaryapi.dev/api/v2/entries/en/'
          }
        },
        ru: {
          keyboardLayout: [
            ['Й', 'Ц', 'У', 'К', 'Е', 'Н', 'Г', 'Ш', 'Щ', 'З', 'Х', 'Ъ'],
            ['Ф', 'Ы', 'В', 'А', 'П', 'Р', 'О', 'Л', 'Д', 'Ж', 'Э'],
            ['Я', 'Ч', 'С', 'М', 'И', 'Т', 'Ь', 'Б', 'Ю']
          ],
          difficultyConfig: {
            easy: { minLength: 3, maxLength: 5, attempts: 8 },
            medium: { minLength: 6, maxLength: 8, attempts: 6 },
            hard: { minLength: 8, maxLength: 10, attempts: 4 }
          },
          api: {
            generateWord: '', // Пусто, используем локальный список
            validateWord: '' // Пусто, используем локальный список
          }
        }
      }
    };
  },
  mounted() {
    this.languageStore = useLanguageStore()
    window.addEventListener('keydown', this.handleKeyboardInput)
    // Загрузка сохранённых данных
    const savedStreak = localStorage.getItem('streak')
    if (savedStreak) this.streak = parseInt(savedStreak)

    // Установка клавиатуры при монтировании
    this.setKeyboard()
  },
  beforeUnmount() {
    window.removeEventListener('keydown', this.handleKeyboardInput)
    // Сохранение данных
    localStorage.setItem('streak', this.streak)
  },
  watch: {
    // Следим за изменением языка
    'languageStore.language'(newLang) {
      this.setKeyboard()
      if (this.gameStarted) {
        this.resetGame()
        this.startGame()
      }
    }
  },
  methods: {
    setKeyboard() {
      const lang = this.languageStore.language
      this.keyboard = this.languageConfig[lang].keyboardLayout
    },

    // Метод для запуска игры
    async startGame() {
      this.gameStarted = true
      this.isLoading = true // Показываем индикатор загрузки

      // Получаем конфигурацию выбранного языка
      const langConfig = this.languageConfig[this.languageStore.language]

      // Получаем конфигурацию выбранной сложности
      const config = langConfig.difficultyConfig[this.difficulty]

      // Выбираем случайную длину слова в заданном диапазоне
      const wordLength = this.getRandomInt(config.minLength, config.maxLength)

      // Устанавливаем количество строк (попыток) и столбцов (длину слова)
      this.rowSize = config.attempts
      this.colSize = wordLength

      // Устанавливаем клавиатуру
      this.keyboard = langConfig.keyboardLayout

      try {
        // Генерируем слово для угадывания через API выбранного языка или локальный список
        this.wordToGuess = await this.generateWord(this.colSize).then(word => word.toUpperCase())

        // Инициализируем игровую сетку
        this.grid = Array.from({ length: this.rowSize }, () => Array(this.colSize).fill(null))
        this.validatedRows = Array.from({ length: this.rowSize }, () => false)
        this.currentGuess = ''
        this.currentRowIndex = 0
        this.usedKeys = {}
      } catch (error) {
        Swal.fire({
          icon: 'error',
          title: 'Error',
          text: this.languageStore.language === 'en' ? 'Failed to start the game. Please try again.' : 'Не удалось запустить игру. Пожалуйста, попробуйте ещё раз.',
        })
        this.resetGame()
      } finally {
        this.isLoading = false // Скрываем индикатор загрузки
      }
    },

    // Вспомогательный метод для получения случайного числа между min и max (включительно)
    getRandomInt(min, max) {
      return Math.floor(Math.random() * (max - min + 1)) + min
    },

    // Метод для генерации слова через API выбранного языка или локальный список
    async generateWord(size) {
      const lang = this.languageStore.language
      if (lang === 'en') {
        // Используем API для английских слов
        try {
          const langConfig = this.languageConfig[lang]
          const response = await fetch(`${langConfig.api.generateWord}?number=1&length=${size}`)
          if (!response.ok) {
            throw new Error(`API error: ${response.statusText}`)
          }

          const data = await response.json()
          if (data.length > 0) {
            return data[0]
          } else {
            throw new Error('No word returned from API.')
          }
        } catch (error) {
          console.error('Error fetching word from API:', error)
          throw new Error('Unable to fetch word from API.')
        }
      } else if (lang === 'ru') {
        // Используем локальный список для русского языка
        const filteredWords = russianWords.filter(word => word.length === size)
        if (filteredWords.length === 0) {
          throw new Error('No words found for the specified length.')
        }
        const randomIndex = this.getRandomInt(0, filteredWords.length - 1)
        return filteredWords[randomIndex].toUpperCase()
      }
    },

    // Обработчик нажатий на клавиатуру
    handleKeyboardInput(event) {
      const key = event.key.toUpperCase()
      if (key === 'BACKSPACE') {
        this.handleBackspace()
      } else if (this.keyboard.flat().includes(key)) {
        this.handleKeyPress(key)
      } else if (key === 'ENTER') {
        this.submitGuess()
      }
    },

    // Обработчик нажатия на клавиши
    handleKeyPress(key) {
      if (this.currentGuess.length < this.colSize && this.currentRowIndex < this.rowSize) {
        this.currentGuess += key
        this.grid[this.currentRowIndex][this.currentGuess.length - 1] = { letter: key, status: '' }
        this.pressedKeys.add(key)
        setTimeout(() => this.pressedKeys.delete(key), 200)
      }
    },

    // Обработчик Backspace
    handleBackspace() {
      if (this.currentGuess.length > 0) {
        const lastIndex = this.currentGuess.length - 1
        this.currentGuess = this.currentGuess.slice(0, -1)
        this.grid[this.currentRowIndex][lastIndex] = null
      }
    },

    // Метод для отправки догадки
    async submitGuess() {
      if (this.currentGuess.length === this.colSize) {
        const isValid = await this.isValidWord(this.currentGuess)
        if (!isValid) {
          Swal.fire({
            icon: 'error',
            title: this.languageStore.language === 'en' ? 'Invalid Word' : 'Недопустимое слово',
            text: this.languageStore.language === 'en' ? 'The word does not exist!' : 'Слово не существует!',
          })
          this.currentGuess = ''
          this.grid[this.currentRowIndex] = Array(this.colSize).fill(null)
          return
        }

        const lang = this.languageStore.language

        let wordArray = Array.from(this.wordToGuess)
        let guessArray = Array.from(this.currentGuess)
        let letterCounts = {}

        if (lang === 'ru') {
          // Нормализация к верхнему регистру для русского языка
          wordArray = wordArray.map(letter => letter.toUpperCase())
          guessArray = guessArray.map(letter => letter.toUpperCase())
        }

        // Подсчитываем количество каждой буквы в загаданном слове
        wordArray.forEach(letter => {
          letterCounts[letter] = (letterCounts[letter] || 0) + 1
        })

        // Массив для статусов каждой буквы в догадке
        const statuses = Array(this.colSize).fill('absent')

        // Первый проход: проверка точных совпадений (correct)
        for (let i = 0; i < this.colSize; i++) {
          if (guessArray[i] === wordArray[i]) {
            statuses[i] = 'correct'
            letterCounts[guessArray[i]]--
          }
        }

        // Второй проход: проверка присутствия букв (present)
        for (let i = 0; i < this.colSize; i++) {
          if (statuses[i] === 'correct') continue
          const currentLetter = guessArray[i]
          if (wordArray.includes(currentLetter) && letterCounts[currentLetter] > 0) {
            statuses[i] = 'present'
            letterCounts[currentLetter]--
          }
        }

        // Обновляем usedKeys с учётом приоритета статусов
        for (let i = 0; i < this.colSize; i++) {
          const status = statuses[i]
          const letter = guessArray[i]
          if (status === 'correct') {
            // Если уже 'correct', оставляем его
            this.usedKeys[letter] = 'correct'
          } else if (status === 'present') {
            // Если уже 'correct', не изменяем
            if (this.usedKeys[letter] !== 'correct') {
              this.usedKeys[letter] = 'present'
            }
          } else if (status === 'absent') {
            // Только если буква ещё не была отмечена как 'correct' или 'present'
            if (!['correct', 'present'].includes(this.usedKeys[letter])) {
              this.usedKeys[letter] = 'absent'
            }
          }
        }

        // Обновляем сетку с результатами
        for (let i = 0; i < this.colSize; i++) {
          this.grid[this.currentRowIndex][i] = {
            letter: guessArray[i],
            status: statuses[i]
          }
        }

        this.validatedRows[this.currentRowIndex] = true
        this.animateMatchedLetters()

        // Проверка догадки до очистки с паузой
        if (this.currentGuess.toUpperCase() === this.wordToGuess.toUpperCase()) {
          this.streak += 1 // Увеличиваем стрик
          await this.delay(500) // Пауза 0.5 секунды
          Swal.fire({
            icon: 'success',
            title: this.languageStore.language === 'en' ? 'Congratulations!' : 'Поздравляем!',
            text: this.languageStore.language === 'en' ? 'You guessed the word!' : 'Вы угадали слово!',
          })
          this.resetGame() // Сбрасываем текущую игру
          this.startGame() // Начинаем новый раунд
          return // Прекратить дальнейшее выполнение
        }

        // Переходим к следующей строке
        this.currentGuess = ''
        this.currentRowIndex++
        if (this.currentRowIndex >= this.rowSize) {
          await this.delay(500) // Пауза 0.5 секунды
          Swal.fire({
            icon: 'info',
            title: this.languageStore.language === 'en' ? 'Game Over' : 'Игра окончена',
            text: this.languageStore.language === 'en' ? `The word was: ${this.wordToGuess}` : `Загаданное слово: ${this.wordToGuess}`,
          })
          this.streak = 0 // Сбрасываем стрик
          this.resetGame() // Сбрасываем текущую игру
        }
      }
    },

    // Метод для сброса игры
    resetGame() {
      this.gameStarted = false
      this.wordToGuess = ''
      this.currentGuess = ''
      this.grid = []
      this.usedKeys = {}
      this.currentRowIndex = 0
      this.validatedRows = []
      this.pressedKeys = new Set()
    },

    // Метод для анимации совпавших букв (можно реализовать по желанию)
    animateMatchedLetters() {
      // Логика анимации
    },

    // Метод для получения класса для ячейки
    getCellClass(rowIndex, colIndex) {
      if (!this.validatedRows[rowIndex]) return ''
      const cell = this.grid[rowIndex][colIndex]
      if (!cell) return ''
      return cell.status
    },

    // Метод для получения класса для клавиши
    getKeyClass(key) {
      return this.usedKeys[key] || ''
    },

    // Метод для проверки, нажата ли клавиша
    isKeyPressed(key) {
      return this.pressedKeys.has(key)
    },

    // Метод для проверки существования слова через API или локальный список
    async isValidWord(word) {
      const lang = this.languageStore.language
      if (lang === 'en') {
        try {
          const langConfig = this.languageConfig[lang]
          const response = await fetch(`${langConfig.api.validateWord}${word.toLowerCase()}`)
          return response.ok
        } catch (error) {
          console.error('Error fetching word:', error)
          return false
        }
      } else if (lang === 'ru') {
        // Проверка наличия слова в локальном списке
        return russianWords.includes(word.toLowerCase())
      }
    },

    // Метод для добавления паузы
    delay(ms) {
      return new Promise(resolve => setTimeout(resolve, ms))
    }
  }
}
</script>

<style>
/* Общие стили */
#app {
  font-family: Arial, sans-serif;
  text-align: center;
  padding: 20px;
}

/* Экран выбора сложности */
.start-screen {
  margin-bottom: 20px;
}

.stats {
  margin-bottom: 10px;
  font-size: 18px;
}

.difficulty-options {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin: 10px 0;
}

.start-screen label {
  font-size: 18px;
}

button {
  padding: 10px 20px;
  font-size: 16px;
  cursor: pointer;
}

.submit-button {
  margin-top: 20px;
  padding: 10px 30px;
  font-size: 18px;
}

/* Игровая сетка */
.board {
  display: grid;
  gap: 10px;
  margin: 20px auto;
  justify-content: center;
}

.row {
  display: flex;
}

.cell {
  width: 50px;
  height: 50px;
  border: 2px solid #ddd;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 24px;
  text-transform: uppercase;
  font-weight: bold;
  transition: background-color 0.3s ease, transform 0.2s ease;
}

.cell.correct {
  background-color: #6aaa64;
  color: white;
  border-color: #6aaa64;
  animation: correct-animation 0.5s ease;
}

.cell.present {
  background-color: #c9b458;
  color: white;
  border-color: #c9b458;
  animation: present-animation 0.5s ease;
}

.cell.absent {
  background-color: #787c7e;
  color: white;
  border-color: #787c7e;
}

@keyframes correct-animation {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.2);
  }
  100% {
    transform: scale(1);
  }
}

@keyframes present-animation {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.2);
  }
  100% {
    transform: scale(1);
  }
}

/* Клавиатура */
.keyboard {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 20px;
}

.keyboard-row {
  display: flex;
  gap: 5px;
  justify-content: center;
}

.keyboard-button {
  padding: 10px 15px;
  font-size: 16px;
  cursor: pointer;
  border: none;
  border-radius: 4px;
  background-color: #d3d6da;
  color: black;
  transition: transform 0.1s ease, background-color 0.1s ease;
}

.keyboard-button.correct {
  background-color: #6aaa64;
  color: white;
}

.keyboard-button.present {
  background-color: #c9b458;
  color: white;
}

.keyboard-button.absent {
  background-color: #787c7e;
  color: white;
}

.keyboard-button.key-pressed {
  transform: scale(0.95);
  background-color: #bfbfbf;
}

/* Кнопка Backspace */
.backspace {
  margin: 10px auto;
  background-color: #ff4d4d;
  color: white;
  font-weight: bold;
  width: 120px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.backspace:hover {
  background-color: #ff1a1a;
}

/* Кнопка Submit */
.submit-button {
  padding: 10px 30px;
  font-size: 18px;
  background-color: #1a73e8;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.submit-button:disabled {
  background-color: #a6c8ff;
  cursor: not-allowed;
}

.submit-button:hover:not(:disabled) {
  background-color: #1669c1;
}

/* Индикатор загрузки */
.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
}

.spinner {
  border: 8px solid #f3f3f3;
  border-top: 8px solid #1a73e8;
  border-radius: 50%;
  width: 60px;
  height: 60px;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Заголовок игрового экрана */
.header {
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
}

.stats p {
  margin: 0 15px;
  font-size: 18px;
}
</style>
