/**
 * VIDYA AI - Automated Bilingual Worksheets & 3D Interactive Flashcards Engine
 * Generates interactive classroom activities and print-ready worksheets.
 */

class WorksheetsAndFlashcards {
  constructor() {
    this.currentFlashcards = [];
    this.currentFlashcardIndex = 0;
    this.activeWorksheet = null;
  }

  /**
   * Initializes Flashcard Deck from lesson data
   */
  initFlashcards(cards) {
    this.currentFlashcards = cards || [];
    this.currentFlashcardIndex = 0;
    this.renderCurrentFlashcard();

    // Event listeners
    const flipCardEl = document.getElementById('interactive-flashcard');
    const nextBtn = document.getElementById('next-flashcard-btn');
    const prevBtn = document.getElementById('prev-flashcard-btn');
    const flipBtn = document.getElementById('flip-card-action-btn');
    const listenBtn = document.getElementById('speak-flashcard-btn');

    flipCardEl?.addEventListener('click', () => this.toggleFlip());
    flipBtn?.addEventListener('click', () => this.toggleFlip());

    nextBtn?.onclick = () => {
      if (this.currentFlashcardIndex < this.currentFlashcards.length - 1) {
        this.currentFlashcardIndex++;
        this.renderCurrentFlashcard();
      }
    };

    prevBtn?.onclick = () => {
      if (this.currentFlashcardIndex > 0) {
        this.currentFlashcardIndex--;
        this.renderCurrentFlashcard();
      }
    };

    listenBtn?.onclick = (e) => {
      e.stopPropagation();
      const card = this.currentFlashcards[this.currentFlashcardIndex];
      if (card) {
        const textToSpeak = card.trans_gondi || card.trans_santhali || card.target || card.hi;
        speechManager.speakText(textToSpeak, 'hi-IN');
      }
    };
  }

  toggleFlip() {
    const cardEl = document.getElementById('interactive-flashcard');
    if (cardEl) {
      cardEl.classList.toggle('flipped');
    }
  }

  renderCurrentFlashcard() {
    const card = this.currentFlashcards[this.currentFlashcardIndex];
    const cardEl = document.getElementById('interactive-flashcard');
    const progressEl = document.getElementById('flashcard-progress-counter');
    const prevBtn = document.getElementById('prev-flashcard-btn');
    const nextBtn = document.getElementById('next-flashcard-btn');

    if (!card || !cardEl) return;

    // Reset flip state
    cardEl.classList.remove('flipped');

    // Update Counter
    if (progressEl) {
      progressEl.textContent = `कार्ड ${this.currentFlashcardIndex + 1} / ${this.currentFlashcards.length}`;
    }

    if (prevBtn) prevBtn.disabled = this.currentFlashcardIndex === 0;
    if (nextBtn) nextBtn.disabled = this.currentFlashcardIndex === this.currentFlashcards.length - 1;

    // Front: Hindi
    const frontIcon = document.getElementById('flashcard-front-icon');
    const frontWord = document.getElementById('flashcard-front-word');
    if (frontIcon) frontIcon.textContent = card.icon || '🌱';
    if (frontWord) frontWord.textContent = card.hi;

    // Back: Target Mother Tongue + Pronunciation
    const targetLang = window.currentSelectedLanguage || 'gondi';
    let targetWord = card[`trans_${targetLang}`] || card.target || card.trans_gondi || '---';

    const backWord = document.getElementById('flashcard-back-word');
    const backPhonetic = document.getElementById('flashcard-back-phonetic');

    if (backWord) backWord.textContent = targetWord;
    if (backPhonetic) backPhonetic.textContent = card.phonetic || `मातृभाषा: ${targetLang.toUpperCase()}`;
  }

  /**
   * Renders Interactive / Printable Bilingual Worksheet
   */
  renderWorksheet(worksheetData) {
    this.activeWorksheet = worksheetData;
    const container = document.getElementById('worksheet-content-area');
    if (!container) return;

    const title = worksheetData.title || 'द्विभाषी अभ्यास पत्र (Bilingual Classroom Worksheet)';
    const targetLang = worksheetData.target_language || 'गोंडी (Gondi)';

    let html = `
      <div class="printable-worksheet-header">
        <div class="worksheet-meta-row">
          <div><strong>विद्या AI प्राथमिक विद्यालय</strong> (Vidya AI Primary Classroom)</div>
          <div><strong>मातृभाषा:</strong> ${targetLang} | <strong>स्रोत:</strong> हिन्दी</div>
        </div>
        <div class="worksheet-student-fields">
          <span>विद्यार्थी का नाम: _______________________</span>
          <span>कक्षा: ________</span>
          <span>दिनांक: ________</span>
        </div>
        <h3 class="worksheet-title">${title}</h3>
      </div>
    `;

    // 1. Match the Following Section
    if (worksheetData.match_words && worksheetData.match_words.length > 0) {
      html += `
        <div class="worksheet-section">
          <h4>भाग 1: सही जोड़ी बनाओ (Match Hindi with Mother Tongue)</h4>
          <p class="section-instruction">हिन्दी शब्द को उसकी मातृभाषा के सही शब्द से मिलाएं:</p>
          <div class="matching-grid">
            <div class="matching-col-left">
              <strong>कॉलम 'अ' (हिन्दी)</strong>
              ${worksheetData.match_words.map((item, idx) => `
                <div class="match-item-left" data-index="${idx}">
                  ${idx + 1}. ${item.hindi}
                </div>
              `).join('')}
            </div>
            <div class="matching-col-right">
              <strong>कॉलम 'ब' (${targetLang})</strong>
              ${worksheetData.match_words.map((item, idx) => `
                <div class="match-item-right" data-index="${idx}">
                  (${String.fromCharCode(65 + idx)}) ${item.target} ${item.phonetic ? `<em>(${item.phonetic})</em>` : ''}
                </div>
              `).join('')}
            </div>
          </div>
        </div>
      `;
    }

    // 2. Fill in the Blanks Section
    if (worksheetData.fill_in_the_blanks && worksheetData.fill_in_the_blanks.length > 0) {
      html += `
        <div class="worksheet-section">
          <h4>भाग 2: रिक्त स्थान भरें (Fill in the Blanks)</h4>
          <ol class="blanks-list">
            ${worksheetData.fill_in_the_blanks.map((b, idx) => `
              <li class="blank-item">
                <span class="blank-question">${b.question_hi}</span>
                <span class="blank-hint">संकेत: ${b.target_hint || ''}</span>
                <input type="text" class="worksheet-input" placeholder="उत्तर लिखें..." data-answer="${b.answer}">
              </li>
            `).join('')}
          </ol>
        </div>
      `;
    }

    // 3. Multiple Choice Questions
    if (worksheetData.multiple_choice && worksheetData.multiple_choice.length > 0) {
      html += `
        <div class="worksheet-section">
          <h4>भाग 3: सही उत्तर चुनिए (Multiple Choice Questions)</h4>
          ${worksheetData.multiple_choice.map((mcq, qIdx) => `
            <div class="mcq-box" data-correct="${mcq.correct_index}">
              <p class="mcq-q-hi"><strong>प्रश्न ${qIdx + 1}:</strong> ${mcq.question_hi}</p>
              ${mcq.question_target ? `<p class="mcq-q-target"><em>${mcq.question_target}</em></p>` : ''}
              <div class="mcq-options">
                ${mcq.options.map((opt, oIdx) => `
                  <label class="mcq-option-label">
                    <input type="radio" name="mcq_${qIdx}" value="${oIdx}">
                    <span>${opt}</span>
                  </label>
                `).join('')}
              </div>
            </div>
          `).join('')}
        </div>
      `;
    }

    // Interactive Action Buttons
    html += `
      <div class="worksheet-action-bar no-print">
        <button id="check-worksheet-answers-btn" class="btn btn-primary">
          ✓ उत्तर जांचें (Check Answers)
        </button>
        <button id="print-worksheet-btn" class="btn btn-secondary">
          🖨️ अभ्यास पत्र प्रिंट करें (Print PDF)
        </button>
      </div>
      <div id="worksheet-score-badge" class="worksheet-score-badge hidden no-print"></div>
    `;

    container.innerHTML = html;

    // Attach Action Listeners
    document.getElementById('check-worksheet-answers-btn')?.addEventListener('click', () => {
      this.gradeWorksheet();
    });

    document.getElementById('print-worksheet-btn')?.addEventListener('click', () => {
      window.print();
    });
  }

  gradeWorksheet() {
    let score = 0;
    let total = 0;

    // Grade MCQs
    const mcqBoxes = document.querySelectorAll('.mcq-box');
    mcqBoxes.forEach((box) => {
      total++;
      const correct = parseInt(box.dataset.correct, 10);
      const selected = box.querySelector('input[type="radio"]:checked');
      if (selected && parseInt(selected.value, 10) === correct) {
        score++;
        box.classList.add('correct-answer');
        box.classList.remove('wrong-answer');
      } else {
        box.classList.add('wrong-answer');
        box.classList.remove('correct-answer');
      }
    });

    // Grade Blanks
    const blanks = document.querySelectorAll('.worksheet-input');
    blanks.forEach((input) => {
      total++;
      const expected = (input.dataset.answer || '').trim();
      const val = (input.value || '').trim();
      if (val && expected && val === expected) {
        score++;
        input.classList.add('input-correct');
      } else {
        input.classList.add('input-wrong');
      }
    });

    const scoreBadge = document.getElementById('worksheet-score-badge');
    if (scoreBadge) {
      scoreBadge.classList.remove('hidden');
      scoreBadge.innerHTML = `
        🎉 <strong>शाबाश! (Great Effort!)</strong> कुल अंक: ${score} / ${total}
        <p>बच्चों ने मातृभाषा और हिन्दी के सहयोग से बहुत अच्छा सीखा!</p>
      `;
    }
  }
}

const worksheetsEngine = new WorksheetsAndFlashcards();
window.renderWorksheetView = (data) => worksheetsEngine.renderWorksheet(data);
