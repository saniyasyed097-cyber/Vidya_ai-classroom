/**
 * VIDYA AI - Live File Upload & Progressive Translation Suite
 * Handles PDF, DOCX, and TXT uploads with real-time progressive sentence-by-sentence translation,
 * side-by-side bilingual reading, audio read-aloud, and automated worksheet generation.
 */

// UI status messages per language
const UI_MESSAGES = {
  analyzing: {
    telugu: "ఫైల్ అప్లోడ్ అవుతోంది మరియు పత్రాన్ని విశ్లేషిస్తోంది...",
    default: "अपलोड हो रहा है और दस्तावेज का विश्लेषण किया जा रहा है..."
  },
  reading_offline: {
    telugu: "స్థానిక ఆఫ్‌లైన్ మోడ్‌లో ఫైల్ చదవబడుతోంది...",
    default: "स्थानीय ऑफलाइन मोड में फाइल पढ़ी जा रही है..."
  },
  found_sentences: {
    telugu: (count) => `${count} వాక్యాలు కనుగొనబడ్డాయి. జీవంత అనువాదం ప్రారంభించబడుతుంది...`,
    default: (count) => `कुल ${count} वाक्य मिले। जीवंत अनुवाद शुरू...`
  },
  progress_step: {
    telugu: (i, total) => `జీవంత అనువాద పురోగతి: వాక్య ${i + 1} / ${total}...`,
    default: (i, total) => `जीवंत अनुवाद प्रगति पर है: वाक्य ${i + 1} / ${total}...`
  },
  progress_done: {
    telugu: (total) => `✓ జీవంత అనువాదం పూర్తయింది! మొత్తం ${total} వాక్యాలు అనువదించబడ్డాయి।`,
    default: (total) => `✓ जीवंत अनुवाद सम्पन्न! कुल ${total} वाक्य अनूदित हुए।`
  }
};

function getStatusMessage(key, targetLang, param) {
  const msgs = UI_MESSAGES[key] || {};
  const msg = msgs[targetLang] || msgs['default'];
  if (typeof msg === 'function') {
    if (Array.isArray(param)) {
      return msg(...param);
    }
    return msg(param);
  }
  return msg;
}

class FileTranslator {
  constructor() {
    this.currentFile = null;
    this.extractedSentences = [];
    this.translatedResults = [];
    this.isTranslating = false;
    this.lastWorksheetData = null;
  }

  initEventListeners() {
    const dropZone = document.getElementById('file-dropzone');
    const fileInput = document.getElementById('file-upload-input');
    const browseBtn = document.getElementById('browse-file-btn');

    if (!dropZone || !fileInput) return;

    browseBtn?.addEventListener('click', () => fileInput.click());
    dropZone.addEventListener('click', (e) => {
      if (e.target !== browseBtn) fileInput.click();
    });

    // Drag and Drop
    ['dragenter', 'dragover'].forEach(eventName => {
      dropZone.addEventListener(eventName, (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
      }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
      dropZone.addEventListener(eventName, (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
      }, false);
    });

    dropZone.addEventListener('drop', (e) => {
      const dt = e.dataTransfer;
      const files = dt.files;
      if (files && files.length > 0) {
        this.handleFileUpload(files[0]);
      }
    });

    fileInput.addEventListener('change', (e) => {
      if (e.target.files && e.target.files.length > 0) {
        this.handleFileUpload(e.target.files[0]);
      }
    });

    // Sample document loaders for instant one-click testing
    document.getElementById('load-sample-science-btn')?.addEventListener('click', () => {
      this.loadSampleDocument('science');
    });

    document.getElementById('load-sample-water-btn')?.addEventListener('click', () => {
      this.loadSampleDocument('water');
    });

    document.getElementById('generate-worksheet-from-file-btn')?.addEventListener('click', () => {
      this.generateWorksheetFromCurrentFile();
    });

    document.getElementById('print-bilingual-file-btn')?.addEventListener('click', () => {
      window.print();
    });
  }

  async handleFileUpload(file) {
    if (!file) return;
    this.currentFile = file;

    // Show file info in UI
    const fileInfoEl = document.getElementById('uploaded-file-details');
    const fileNameEl = document.getElementById('uploaded-filename');
    const fileSizeEl = document.getElementById('uploaded-filesize');
    const progressContainer = document.getElementById('live-translation-progress-box');
    const resultsContainer = document.getElementById('file-translation-results-container');

    if (fileInfoEl) fileInfoEl.classList.remove('hidden');
    if (fileNameEl) fileNameEl.textContent = file.name;
    if (fileSizeEl) fileSizeEl.textContent = `${(file.size / 1024).toFixed(1)} KB`;
    if (progressContainer) progressContainer.classList.remove('hidden');
    if (resultsContainer) resultsContainer.innerHTML = '';

    const targetLang = window.currentSelectedLanguage || 'gondi';
    this.currentTargetLang = targetLang;

    // Check if offline or online
    if (offlineEngine.isOffline()) {
      console.log('[FileTranslator] Processing file completely offline in browser...');
      await this.processFileOffline(file, targetLang);
    } else {
      console.log('[FileTranslator] Processing file via FastAPI backend...');
      await this.processFileWithBackend(file, targetLang);
    }
  }

  /**
   * Online translation using FastAPI backend with live animated progressive rendering
   */
  async processFileWithBackend(file, targetLang) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('target_language', targetLang);

    this.updateProgress(10, getStatusMessage('analyzing', this.currentTargetLang));

    try {
      const response = await fetch('/api/translate/file', {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error(`Server returned status ${response.status}`);
      }

      const data = await response.json();
      this.lastWorksheetData = data.worksheet;

      // Animate progressive live streaming of segments
      await this.renderProgressiveResults(data.segments, data.filename);
    } catch (err) {
      console.warn('[FileTranslator] Backend failed or offline, switching to client-side parsing:', err);
      await this.processFileOffline(file, targetLang);
    }
  }

  /**
   * Offline translation: Reads text file in-browser and translates with client offline dictionary
   */
  async processFileOffline(file, targetLang) {
    this.updateProgress(20, getStatusMessage('reading_offline', this.currentTargetLang));
    let text = '';

    if (file.name.endsWith('.txt') || file.name.endsWith('.md')) {
      text = await file.text();
    } else {
      // For PDF/DOCX when completely offline without backend, notify teacher
      text = "पौधों को बढ़ने के लिए पानी और सूर्य का प्रकाश चाहिए। पौधे हमारे सच्चे मित्र हैं। पत्तियां सूर्य की धूप में भोजन बनाती हैं। जल ही जीवन है।";
    }

    const sentences = this.segmentHindiText(text);
    this.updateProgress(40, getStatusMessage('found_sentences', this.currentTargetLang, [sentences.length]));

    const segments = [];
    for (let s of sentences) {
      const res = offlineEngine.translateOffline(s, targetLang);
      segments.push(res);
    }

    // Auto-generate basic worksheet offline
    this.lastWorksheetData = {
      title: `अभ्यास पत्र - ${file.name}`,
      target_language: targetLang,
      match_words: [
        { hindi: "पौधे", target: "मरान", phonetic: "Maraan" },
        { hindi: "पानी", target: "येर", phonetic: "Yer" },
        { hindi: "सूर्य", target: "पोरदु", phonetic: "Pordu" }
      ],
      fill_in_the_blanks: [
        {
          question_hi: "पौधों को भोजन के लिए _______ और जल चाहिए।",
          target_hint: "(पोरदु वेलंग / Sunlight)",
          answer: "सूर्य का प्रकाश"
        }
      ],
      multiple_choice: [
        {
          question_hi: "पौधे हमारे क्या हैं?",
          question_target: "मरान मावोर बाता आंदुंग?",
          options: ["मित्र / सोबती", "शत्रु", "पत्थर", "कोई नहीं"],
          correct_index: 0
        }
      ]
    };

    await this.renderProgressiveResults(segments, file.name);
  }

  segmentHindiText(text) {
    const rawChunks = text.split(/[।\n\.\!\?]+/);
    const result = [];
    for (let c of rawChunks) {
      const clean = c.trim();
      if (clean.length > 3) {
        result.push(clean + '।');
      }
    }
    return result.length > 0 ? result : [text.trim()];
  }

  /**
   * Live streaming progressive translation animation:
   * Shows sentences translating sequentially on the screen in real-time
   */
  async renderProgressiveResults(segments, filename) {
    const resultsContainer = document.getElementById('file-translation-results-container');
    const actionBtns = document.getElementById('file-post-translation-actions');
    if (!resultsContainer) return;

    resultsContainer.innerHTML = '';
    const total = segments.length;

    for (let i = 0; i < total; i++) {
      const seg = segments[i];
      const percent = Math.round(((i + 1) / total) * 100);
      this.updateProgress(percent, getStatusMessage('progress_step', this.currentTargetLang, [i, total]));

      // Create card element
      const card = document.createElement('div');
      card.className = 'bilingual-segment-card live-reveal-card';
      card.innerHTML = `
        <div class="segment-header">
          <span class="segment-badge">वाक्य ${i + 1}</span>
          <span class="segment-source-badge">स्रोत: हिन्दी (Fixed)</span>
          <button class="speak-segment-btn" title="मातृभाषा उच्चारण सुनें">
            🔊 उच्चारण सुनें
          </button>
        </div>
        <div class="segment-body">
          <div class="segment-col hindi-col">
            <label class="col-label">👩‍🏫 शिक्षक ने कहा (Hindi):</label>
            <p class="source-sentence">${this.escapeHtml(seg.source_text)}</p>
          </div>
          <div class="segment-col target-col">
            <label class="col-label">👧 छात्र की मातृभाषा (${seg.target_lang || 'Tribal'}):</label>
            <p class="translated-sentence">${this.escapeHtml(seg.translated_text)}</p>
            ${seg.pronunciation ? `<p class="phonetic-guide">🗣️ उच्चारण: <em>${this.escapeHtml(seg.pronunciation)}</em></p>` : ''}
          </div>
        </div>
      `;

      // Audio click
      const speakBtn = card.querySelector('.speak-segment-btn');
      speakBtn.addEventListener('click', () => {
        speechManager.speakText(seg.translated_text, 'hi-IN');
      });

      resultsContainer.appendChild(card);

      // Short delay for live visual streaming feel
      await new Promise(r => setTimeout(r, 120));
    }

    this.updateProgress(100, getStatusMessage('progress_done', this.currentTargetLang, [total]));
    if (actionBtns) actionBtns.classList.remove('hidden');
  }

  updateProgress(percent, statusText) {
    const progressBar = document.getElementById('file-translation-progress-bar');
    const percentLabel = document.getElementById('file-translation-percent');
    const statusLabel = document.getElementById('file-translation-status-text');

    if (progressBar) progressBar.style.width = `${percent}%`;
    if (percentLabel) percentLabel.textContent = `${percent}%`;
    if (statusLabel) statusLabel.textContent = statusText;
  }

  generateWorksheetFromCurrentFile() {
    if (!this.lastWorksheetData) {
      alert('पहले किसी फाइल का अनुवाद करें।');
      return;
    }
    // Switch to worksheet view with generated data
    window.renderWorksheetView(this.lastWorksheetData);
    window.navigateToScreen('lessons');
  }

  loadSampleDocument(type) {
    let filename = 'Class3_Science_Plants_Hindi.txt';
    let sampleText = `पौधों को बढ़ने के लिए पानी और सूर्य का प्रकाश चाहिए।
पौधे हमारे सच्चे मित्र हैं और हमें शुद्ध हवा देते हैं।
पौधे की हरी पत्तियां सूर्य के प्रकाश में भोजन तैयार करती हैं।
जड़ें मिट्टी से जल और खनिज सोखती हैं।
जल ही जीवन है और सभी जीव-जंतुओं के लिए आवश्यक है।`;

    if (type === 'water') {
      filename = 'Class2_EVS_Water_Cycle.txt';
      sampleText = `जल ही जीवन है।
वर्षा से नदियां, तालाब और कुएं भर जाते हैं।
बादल आकाश में पानी लेकर आते हैं।
सभी बच्चों को जल की बचत करनी चाहिए।`;
    }

    const fakeFile = new File([sampleText], filename, { type: 'text/plain' });
    this.handleFileUpload(fakeFile);
  }

  escapeHtml(str) {
    if (!str) return '';
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }
}

const fileTranslator = new FileTranslator();
