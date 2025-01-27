<template>
  <div id="app">
    <!-- Экран выбора сложности -->
    <div class="start-screen" v-if="!gameStarted">
      <h1>Word Guessing Game</h1>
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

export default {
  data() {
    return {
      gameStarted: false,
      difficulty: 'easy', // Выбранная сложность
      rowSize: 8, // Количество попыток (по умолчанию для easy)
      colSize: 6, // Длина слова (по умолчанию для easy)
      wordToGuess: '', // Загаданное слово
      currentGuess: '', // Текущая догадка
      grid: [], // Игровая сетка
      keyboard: [
        ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
        ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
        ['Z', 'X', 'C', 'V', 'B', 'N', 'M']
      ],
      usedKeys: {}, // Статус использованных клавиш
      currentRowIndex: 0, // Индекс текущей строки
      validatedRows: [], // Отметки валидированных строк
      pressedKeys: new Set(), // Нажатые клавиши
      isLoading: false, // Индикатор загрузки
      difficultyConfig: { // Конфигурация уровней сложности
        easy: {
          minLength: 4,
          maxLength: 6,
          attempts: 8
        },
        medium: {
          minLength: 6,
          maxLength: 8,
          attempts: 6
        },
        hard: {
          minLength: 8,
          maxLength: 10,
          attempts: 4
        }
      }
    };
  },
  mounted() {
    window.addEventListener('keydown', this.handleKeyboardInput);
  },
  beforeUnmount() {
    window.removeEventListener('keydown', this.handleKeyboardInput);
  },
  methods: {
    // Метод для запуска игры
    async startGame() {
      this.gameStarted = true;
      this.isLoading = true; // Показываем индикатор загрузки

      // Получаем конфигурацию выбранного уровня сложности
      const config = this.difficultyConfig[this.difficulty];

      // Выбираем случайную длину слова в заданном диапазоне
      const wordLength = this.getRandomInt(config.minLength, config.maxLength);

      // Устанавливаем количество строк (попыток) и столбцов (длину слова)
      this.rowSize = config.attempts;
      this.colSize = wordLength;

      try {
        // Генерируем слово для угадывания
        this.wordToGuess = await this.generateWord(this.colSize).then(word => word.toUpperCase());

        // Инициализируем игровую сетку
        this.grid = Array.from({ length: this.rowSize }, () => Array(this.colSize).fill(null));
        this.validatedRows = Array.from({ length: this.rowSize }, () => false);
        this.currentGuess = '';
        this.currentRowIndex = 0;
        this.usedKeys = {};
      } catch (error) {
        Swal.fire({
          icon: 'error',
          title: 'Error',
          text: 'Failed to start the game. Please try again.',
        });
        this.resetGame();
      } finally {
        this.isLoading = false; // Скрываем индикатор загрузки
      }
    },

    // Вспомогательный метод для получения случайного числа между min и max (включительно)
    getRandomInt(min, max) {
      return Math.floor(Math.random() * (max - min + 1)) + min;
    },

    // Метод для генерации слова через Django прокси
    async generateWord(size) {
      try {
        const response = await fetch(`/api/random-word/?size=${size}`);
        const data = await response.json();

        if (data.word) {
          return data.word;
        } else {
          throw new Error(data.error || 'No word returned.');
        }
      } catch (error) {
        console.error('Error fetching word from backend:', error);

        // Резервный вариант — использование локальных слов
        const fallbackWords = {
          4: ['TREE', 'GAME', 'PLAY'],
          5: ['APPLE', 'GRAPE', 'HOUSE'],
          6: ['SCHOOL', 'DOUBLE', 'COOKER'],
          7: ['PROGRAM', 'BARRIER', 'NETWORK'],
          8: ['COMPUTER', 'LANGUAGE', 'KEYBOARD'],
          9: ['LANGUAGE', 'HARDWARE', 'FIREWALL'],
          10: ['DEVELOPMENT', 'INTERACTIVE', 'FUNCTIONAL']
        };

        const words = fallbackWords[size];
        if (words && words.length > 0) {
          return words[Math.floor(Math.random() * words.length)];
        } else {
          throw new Error('No fallback words available.');
        }
      }
    },

    // Обработчик нажатий на клавиатуру
    handleKeyboardInput(event) {
      const key = event.key.toUpperCase();
      if (key === 'BACKSPACE') {
        this.handleBackspace();
      } else if (this.keyboard.flat().includes(key)) {
        this.handleKeyPress(key);
      } else if (key === 'ENTER') {
        this.submitGuess();
      }
    },

    // Обработчик нажатия на клавиши
    handleKeyPress(key) {
      if (this.currentGuess.length < this.colSize && this.currentRowIndex < this.rowSize) {
        this.currentGuess += key;
        this.grid[this.currentRowIndex][this.currentGuess.length - 1] = { letter: key, status: '' };
        this.pressedKeys.add(key);
        setTimeout(() => this.pressedKeys.delete(key), 200);
      }
    },

    // Обработчик Backspace
    handleBackspace() {
      if (this.currentGuess.length > 0) {
        const lastIndex = this.currentGuess.length - 1;
        this.currentGuess = this.currentGuess.slice(0, -1);
        this.grid[this.currentRowIndex][lastIndex] = null;
      }
    },

    // Метод для отправки догадки
    async submitGuess() {
      if (this.currentGuess.length === this.colSize) {
        const isValid = await this.isValidWord(this.currentGuess);
        if (!isValid) {
          Swal.fire({
            icon: 'error',
            title: 'Invalid Word',
            text: 'The word does not exist!',
          });
          this.currentGuess = '';
          this.grid[this.currentRowIndex] = Array(this.colSize).fill(null);
          return;
        }

        const wordArray = Array.from(this.wordToGuess);
        const guessArray = Array.from(this.currentGuess);
        const letterCounts = {};

        // Подсчитываем количество каждой буквы в загаданном слове
        wordArray.forEach(letter => {
          letterCounts[letter] = (letterCounts[letter] || 0) + 1;
        });

        // Массив для статусов каждой буквы в догадке
        const statuses = Array(this.colSize).fill('absent');

        // Первый проход: проверка точных совпадений (correct)
        for (let i = 0; i < this.colSize; i++) {
          if (guessArray[i] === wordArray[i]) {
            statuses[i] = 'correct';
            letterCounts[guessArray[i]]--;
          }
        }

        // Второй проход: проверка присутствия букв (present)
        for (let i = 0; i < this.colSize; i++) {
          if (statuses[i] === 'correct') continue;
          const currentLetter = guessArray[i];
          if (wordArray.includes(currentLetter) && letterCounts[currentLetter] > 0) {
            statuses[i] = 'present';
            letterCounts[currentLetter]--;
          }
        }

        // Обновляем usedKeys с учётом приоритета статусов
        for (let i = 0; i < this.colSize; i++) {
          const status = statuses[i];
          const letter = guessArray[i];
          if (status === 'correct') {
            // Если уже 'correct', оставляем его
            this.usedKeys[letter] = 'correct';
          } else if (status === 'present') {
            // Если уже 'correct', не изменяем
            if (this.usedKeys[letter] !== 'correct') {
              this.usedKeys[letter] = 'present';
            }
          } else if (status === 'absent') {
            // Только если буква ещё не была отмечена как 'correct' или 'present'
            if (!['correct', 'present'].includes(this.usedKeys[letter])) {
              this.usedKeys[letter] = 'absent';
            }
          }
        }

        // Обновляем сетку с результатами
        for (let i = 0; i < this.colSize; i++) {
          this.grid[this.currentRowIndex][i] = {
            letter: guessArray[i],
            status: statuses[i]
          };
        }

        this.validatedRows[this.currentRowIndex] = true;
        this.animateMatchedLetters();

        // Проверка догадки до очистки с паузой
        if (this.currentGuess.toUpperCase() === this.wordToGuess.toUpperCase()) {
          await this.delay(500); // Пауза 0.5 секунды
          Swal.fire({
            icon: 'success',
            title: 'Congratulations!',
            text: 'You guessed the word!',
          });
          this.resetGame();
          return; // Прекратить дальнейшее выполнение
        }

        this.currentGuess = '';
        this.currentRowIndex++;
        if (this.currentRowIndex >= this.rowSize) {
          await this.delay(500); // Пауза 0.5 секунды
          Swal.fire({
            icon: 'info',
            title: 'Game Over',
            text: `The word was: ${this.wordToGuess}`,
          });
          this.resetGame();
        }
      }
    },

    // Метод для сброса игры
    resetGame() {
      this.gameStarted = false;
      this.wordToGuess = '';
      this.currentGuess = '';
      this.grid = [];
      this.usedKeys = {};
      this.currentRowIndex = 0;
      this.validatedRows = [];
      this.matchedPositions = new Set();
      this.pressedKeys = new Set();
    },

    // Метод для анимации совпавших букв (можно реализовать по желанию)
    animateMatchedLetters() {
      // Логика анимации
    },

    // Метод для получения класса для ячейки
    getCellClass(rowIndex, colIndex) {
      if (!this.validatedRows[rowIndex]) return '';
      const cell = this.grid[rowIndex][colIndex];
      if (!cell) return '';
      return cell.status;
    },

    // Метод для получения класса для клавиши
    getKeyClass(key) {
      return this.usedKeys[key] || '';
    },

    // Метод для проверки, нажата ли клавиша
    isKeyPressed(key) {
      return this.pressedKeys.has(key);
    },

    // Метод для проверки существования слова через API
    async isValidWord(word) {
      try {
        const response = await fetch(`https://api.dictionaryapi.dev/api/v2/entries/en/${word.toLowerCase()}`);
        return response.ok;
      } catch (error) {
        console.error('Error fetching word:', error);
        return false;
      }
    },

    // Метод для добавления паузы
    delay(ms) {
      return new Promise(resolve => setTimeout(resolve, ms));
    }
  }
};
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
</style>
