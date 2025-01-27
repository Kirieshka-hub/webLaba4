<template>
  <div id="app">
    <div class="start-screen" v-if="!gameStarted">
      <label for="row-size">Number of rows:</label>
      <select v-model="rowSize" id="row-size">
        <option v-for="size in [4, 5, 6, 7, 8]" :key="size" :value="size">{{ size }}</option>
      </select>

      <label for="col-size">Number of letters per row:</label>
      <select v-model="colSize" id="col-size">
        <option v-for="size in [4, 5, 6, 7, 8]" :key="size" :value="size">{{ size }}</option>
      </select>

      <button @click="startGame">Start Game</button>
    </div>

    <div v-else class="game">
      <div class="board">
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
            {{ cell }}
          </div>
        </div>
      </div>

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

      <button @click="submitGuess" :disabled="currentGuess.length !== colSize">Submit</button>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      gameStarted: false,
      rowSize: 6,
      colSize: 6,
      wordToGuess: '',
      currentGuess: '',
      grid: [],
      keyboard: [
        ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
        ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
        ['Z', 'X', 'C', 'V', 'B', 'N', 'M']
      ],
      usedKeys: {},
      currentRowIndex: 0,
      validatedRows: [],
      matchedPositions: new Set(),
      pressedKeys: new Set(),
    };
  },
  mounted() {
    window.addEventListener('keydown', this.handleKeyboardInput);
  },
  beforeUnmount() {
    window.removeEventListener('keydown', this.handleKeyboardInput);
  },
  methods: {
    startGame() {
      this.gameStarted = true;
      this.wordToGuess = this.generateWord(this.colSize);
      this.grid = Array.from({ length: this.rowSize }, () => Array(this.colSize).fill(''));
      this.validatedRows = Array(this.rowSize).fill(false);
    },
    generateWord(size) {
      const words = ['APPLE', 'GRAPE', 'HOUSE', 'TABLE', 'CLOCK', 'CHAIR', 'PLANE', 'SCHOOL', 'BRICK', 'SOCK'];
      return words.find(word => word.length === size);
    },
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
    handleKeyPress(key) {
      if (this.currentGuess.length < this.colSize) {
        this.currentGuess += key;
        this.grid[this.currentRowIndex][this.currentGuess.length - 1] = key;
        this.pressedKeys.add(key);
        setTimeout(() => this.pressedKeys.delete(key), 200);
      }
    },
    handleBackspace() {
      if (this.currentGuess.length > 0) {
        const lastIndex = this.currentGuess.length - 1;
        this.currentGuess = this.currentGuess.slice(0, -1);
        this.grid[this.currentRowIndex][lastIndex] = '';
      }
    },
    async submitGuess() {
      if (this.currentGuess.length === this.colSize) {
        const isValid = await this.isValidWord(this.currentGuess);
        if (!isValid) {
          alert('Слово не существует!');
          this.currentGuess = '';
          this.grid[this.currentRowIndex] = Array(this.colSize).fill('');
          return;
        }

        const wordArray = Array.from(this.wordToGuess);
        const guessArray = Array.from(this.currentGuess);
        const tempWordArray = [...wordArray];

        // Очищаем совпадения для текущей строки
        this.matchedPositions.clear();
        const usedIndices = new Set();
        
        // Считаем сколько букв осталось в слове
        const letterCounts = this.getLetterCounts(wordArray); 
        const guessLetterCounts = this.getLetterCounts(guessArray); 

        // Точное совпадение (зелёный)
        for (let i = 0; i < this.colSize; i++) {
          if (guessArray[i] === tempWordArray[i]) {
            this.usedKeys[guessArray[i]] = 'correct'; // Задаем для этой буквы статус 'correct'
            this.matchedPositions.add(i); // Запоминаем индекс угаданной буквы
            usedIndices.add(i); // Запоминаем использованные буквы
            tempWordArray[i] = null; // Убираем букву из временного массива
            letterCounts[guessArray[i]]--; // Уменьшаем счетчик для этой буквы
          }
        }

        // Частичное совпадение (жёлтый)
        for (let i = 0; i < this.colSize; i++) {
          if (!this.matchedPositions.has(i)) {
            const char = guessArray[i];

            // Проверяем, есть ли буква в слове и не исчерпаны ли все такие буквы
            if (letterCounts[char] > 0 && guessLetterCounts[char] > 0) {
              this.usedKeys[char] = 'present'; // Задаем для этой буквы статус 'present' (жёлтый)
              letterCounts[char]--; // Уменьшаем количество оставшихся таких букв
              guessLetterCounts[char]--; // Уменьшаем количество таких букв в текущем слове
            } else {
              this.usedKeys[char] = 'absent'; // Если буква не в слове, делаем её серой
            }
          }
        }

        this.validatedRows[this.currentRowIndex] = true;
        this.animateMatchedLetters();
        this.currentGuess = '';
        this.currentRowIndex++;
      }
    },

    animateMatchedLetters() {
      // Логика анимации
    },
    getCellClass(rowIndex, colIndex) {
      if (!this.validatedRows[rowIndex]) return '';
      const char = this.grid[rowIndex][colIndex];
      if (!char) return '';
      if (char === this.wordToGuess[colIndex]) return 'correct';
      if (this.wordToGuess.includes(char) && !this.matchedPositions.has(colIndex)) return 'present';
      return 'absent';
    },
    getKeyClass(key) {
      return this.usedKeys[key] || '';
    },
    isKeyPressed(key) {
      return this.pressedKeys.has(key);
    },
    async isValidWord(word) {
      try {
        const response = await fetch(`https://api.dictionaryapi.dev/api/v2/entries/en/${word.toLowerCase()}`);
        return response.ok;
      } catch (error) {
        console.error('Error fetching word:', error);
        return false;
      }
    },

    // Считаем, сколько раз каждая буква встречается в слове
    getLetterCounts(wordArray) {
      const counts = {};
      wordArray.forEach(letter => {
        counts[letter] = (counts[letter] || 0) + 1;
      });
      return counts;
    },
  }
};
</script>

<style>
#app {
  font-family: Arial, sans-serif;
  text-align: center;
  padding: 20px;
}

.start-screen {
  margin-bottom: 20px;
}

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
  width: 40px;
  height: 40px;
  border: 1px solid #ddd;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 20px;
  transition: background-color 0.3s ease, transform 0.2s ease;
}

.cell.correct {
  background-color: green;
  color: white;
  animation: correct-animation 0.5s ease;
}

.cell.present {
  background-color: yellow;
  color: black;
  animation: present-animation 0.5s ease;
}

.cell.absent {
  background-color: gray;
  color: white;
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

button {
  padding: 10px;
  font-size: 16px;
  cursor: pointer;
}

button.correct {
  background-color: green;
  color: white;
}

button.present {
  background-color: yellow;
  color: black;
}

button.absent {
  background-color: gray;
  color: white;
}

button.backspace {
  margin-left: 200px;
  background-color: #ff4d4d;
  color: white;
  font-weight: bold;
  width: 100px;
}

.keyboard-button {
  transition: transform 0.1s ease, background-color 0.1s ease;
}

.keyboard-button.key-pressed {
  transform: scale(0.95);
  background-color: #ccc;
}
</style>
