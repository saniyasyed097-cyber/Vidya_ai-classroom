/**
 * VIDYA AI - Main Application Controller
 * Handles 5 Core Screens, Navigation, Fixed Hindi Source State, and Live Classroom Workflows.
 */

window.currentSelectedLanguage = 'gondi';
window.fixedSourceLanguage = 'hi';

class VidyaApp {
  constructor() {
    this.currentScreen = 'home';
    this.languages = {};
    this.lessons = [];
    this.activeLesson = null;
    this.history = [];
    this.isMicPressed = false;
  }

  async init() {
    console.log('🚀 Initializing VIDYA AI Classroom Web Application...');

    this.setupNavigation();
    this.setupOfflineMonitor();
    this.setupLanguageSelection();
    this.setupLiveClassroom();
    this.setupLessonMode();
    this.setupOfflineScreen();
    this.registerServiceWorker();

    // Initialize sub-modules
    if (typeof fileTranslator !== 'undefined') {
      fileTranslator.initEventListeners();
    }

    // Load initial data
    await this.loadLanguages();
    await this.loadLessons();
    this.updateLanguageBadges();

    // Default to home screen
    this.navigateTo('home');
  }

  setupNavigation() {
    // Top & Bottom Navigation links
    const navLinks = document.querySelectorAll('[data-target-screen]');
    navLinks.forEach(link => {
      link.addEventListener('click', (e) => {
        e.preventDefault();
        const target = link.getAttribute('data-target-screen');
        if (target) this.navigateTo(target);
      });
    });

    window.navigateToScreen = (screenName) => this.navigateTo(screenName);
  }

  navigateTo(screenId) {
    const screens = document.querySelectorAll('.app-screen');
    screens.forEach(s => {
      s.classList.remove('active-screen');
      s.classList.add('hidden');
    });

    const activeEl = document.getElementById(`screen-${screenId}`);
    if (activeEl) {
      activeEl.classList.remove('hidden');
      activeEl.classList.add('active-screen');
      this.currentScreen = screenId;
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    // Update bottom nav active state
    const bottomNavBtns = document.querySelectorAll('.bottom-nav-btn');
    bottomNavBtns.forEach(btn => {
      if (btn.getAttribute('data-target-screen') === screenId) {
        btn.classList.add('nav-active');
      } else {
        btn.classList.remove('nav-active');
      }
    });

    console.log(`[Navigation] Navigated to screen: ${screenId}`);
  }

  setupOfflineMonitor() {
    const offlinePill = document.getElementById('network-status-indicator');
    const simulateToggle = document.getElementById('simulate-offline-toggle');

    const updateStatus = () => {
      const isOff = offlineEngine.isOffline();
      if (offlinePill) {
        if (isOff) {
          offlinePill.className = 'status-pill status-offline';
          offlinePill.innerHTML = '<span class="pulse-dot"></span> 🔴 ऑफ़लाइन मोड (Offline Mode)';
        } else {
          offlinePill.className = 'status-pill status-offline';
          offlinePill.innerHTML = '<span class="pulse-dot"></span> 🔴 ऑफ़लाइन फ्रेमवर्क (Offline)';
        }
      }
    };

    window.addEventListener('online', updateStatus);
    window.addEventListener('offline', updateStatus);

    simulateToggle?.addEventListener('change', (e) => {
      offlineEngine.setSimulatedOffline(e.target.checked);
      updateStatus();
    });

    updateStatus();
  }

  async loadLanguages() {
    try {
      if (!offlineEngine.isOffline()) {
        const res = await fetch('/api/languages');
        if (res.ok) {
          const data = await res.json();
          this.languages = data.targets;
          return;
        }
      }
    } catch (e) {
      console.warn('[VidyaApp] Could not fetch languages from backend, using defaults.');
    }

    // Default target language metadata
    this.languages = {
      gondi: {
        code: "gon",
        name: "Gondi",
        native_name: "गोंडी (Gōndi)",
        regions: "Madhya Pradesh, Chhattisgarh, Maharashtra, Telangana",
        greeting: "सेवा जोहार (Sewa Johar)"
      },
      santhali: {
        code: "sat",
        name: "Santhali",
        native_name: "संथाली (Santali)",
        regions: "Jharkhand, Odisha, West Bengal, Bihar",
        greeting: "जोहार (Johar)"
      },
      bhili: {
        code: "bhi",
        name: "Bhili",
        native_name: "भीली (Bhili)",
        regions: "Rajasthan, Madhya Pradesh, Gujarat, Maharashtra",
        greeting: "राम राम सा / जोहार"
      },
      telugu: {
        code: "tel",
        name: "Telugu",
        native_name: "తెలుగు (Telugu)",
        regions: "Telangana & Andhra Pradesh (Agency Areas)",
        greeting: "నమస్కారం"
      },
      mundari: {
        code: "mun",
        name: "Mundari",
        native_name: "मुंडारी (Mundari)",
        regions: "Jharkhand, Odisha",
        greeting: "जोहार"
      },
      kurukh: {
        code: "kru",
        name: "Kurukh",
        native_name: "कुड़ुख़ (Oraon)",
        regions: "Jharkhand, Chhattisgarh",
        greeting: "जोहार"
      }
    };
  }

  setupLanguageSelection() {
    const langCards = document.querySelectorAll('.language-option-card');
    const continueBtn = document.getElementById('confirm-language-btn');
    const sampleGreetingEl = document.getElementById('selected-lang-greeting-preview');

    langCards.forEach(card => {
      card.addEventListener('click', () => {
        langCards.forEach(c => c.classList.remove('selected'));
        card.classList.add('selected');
        const lang = card.getAttribute('data-lang');
        window.currentSelectedLanguage = lang;

        // Update greeting preview
        if (this.languages[lang] && sampleGreetingEl) {
          sampleGreetingEl.innerHTML = `
            <strong>अभिवादन (Greeting):</strong> ${this.languages[lang].greeting} <br>
            <small>क्षेत्र: ${this.languages[lang].regions}</small>
          `;
        }
        this.updateLanguageBadges();
      });
    });

    continueBtn?.addEventListener('click', () => {
      this.updateLanguageBadges();
      this.navigateTo('live');
    });
  }

  updateLanguageBadges() {
    const lang = window.currentSelectedLanguage || 'gondi';
    const info = this.languages[lang] || { native_name: lang };

    // Update all target lang badges across screens
    document.querySelectorAll('.active-target-lang-label').forEach(el => {
      el.textContent = info.native_name || lang;
    });

    const headerTargetPill = document.getElementById('header-target-language-pill');
    if (headerTargetPill) {
      headerTargetPill.textContent = `लक्ष्य: ${info.native_name || lang}`;
    }
  }

  setupLiveClassroom() {
    const micBtn = document.getElementById('mic-action-btn');
    const micStatus = document.getElementById('mic-status-label');
    const waveform = document.getElementById('audio-waveform-visualizer');
    const textInput = document.getElementById('live-hindi-text-input');
    const sendBtn = document.getElementById('send-live-text-btn');
    const playAudioBtn = document.getElementById('play-last-translation-audio-btn');

    // Microphone: Toggle or Hold
    const startMic = () => {
      if (this.isMicPressed) return;
      this.isMicPressed = true;
      micBtn?.classList.add('recording-active');
      waveform?.classList.remove('hidden');
      if (micStatus) micStatus.textContent = '🎤 शिक्षक बोल रहे हैं (सुन रहे हैं... Speak in Hindi)';

      speechManager.startListening(
        (transcriptObj) => {
          if (transcriptObj.interim && textInput) {
            textInput.value = transcriptObj.interim;
          }
          if (transcriptObj.final) {
            if (textInput) textInput.value = transcriptObj.final;
            this.handleTeacherSpeech(transcriptObj.final);
          }
        },
        (status, err) => {
          if (status === 'idle') {
            stopMic();
          }
        }
      );
    };

    const stopMic = () => {
      if (!this.isMicPressed) return;
      this.isMicPressed = false;
      micBtn?.classList.remove('recording-active');
      waveform?.classList.add('hidden');
      if (micStatus) micStatus.textContent = 'बोलने के लिए दबाएं (Tap or Hold to Speak Hindi)';
      speechManager.stopListening();
    };

    // Click / Touch handlers for mic
    micBtn?.addEventListener('click', () => {
      if (this.isMicPressed) {
        stopMic();
      } else {
        startMic();
      }
    });

    // Text input submission
    sendBtn?.addEventListener('click', () => {
      const text = textInput?.value?.trim();
      if (text) {
        this.handleTeacherSpeech(text);
      }
    });

    textInput?.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        const text = textInput?.value?.trim();
        if (text) {
          this.handleTeacherSpeech(text);
        }
      }
    });

    // Preset quick teacher classroom phrases
    document.querySelectorAll('.preset-phrase-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const phrase = btn.getAttribute('data-phrase');
        if (phrase) {
          if (textInput) textInput.value = phrase;
          this.handleTeacherSpeech(phrase);
        }
      });
    });

    // Audio replay button
    playAudioBtn?.addEventListener('click', () => {
      const lastTransEl = document.getElementById('live-translated-text-content');
      if (lastTransEl && lastTransEl.textContent) {
        speechManager.speakText(lastTransEl.textContent, 'hi-IN');
      }
    });
  }

  async handleTeacherSpeech(hindiText) {
    if (!hindiText || !hindiText.trim()) return;
    const cleanText = hindiText.trim();
    const targetLang = window.currentSelectedLanguage || 'gondi';

    const sourceEl = document.getElementById('live-teacher-said-content');
    const transEl = document.getElementById('live-translated-text-content');
    const phoneticEl = document.getElementById('live-pronunciation-guide-content');
    const vocabTagsEl = document.getElementById('live-vocab-tags-container');
    const resultCard = document.getElementById('live-translation-card');

    if (sourceEl) sourceEl.textContent = cleanText;
    if (transEl) transEl.textContent = 'अनुवाद हो रहा है... (Translating...)';
    if (resultCard) resultCard.classList.remove('hidden');

    let translationResult = null;

    // 1. Try server translation if not offline
    if (!offlineEngine.isOffline()) {
      try {
        const response = await fetch('/api/translate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            text: cleanText,
            source_language: 'hi', // Fixed to Hindi
            target_language: targetLang,
            session_id: 'live_classroom'
          })
        });

        if (response.ok) {
          translationResult = await response.json();
        }
      } catch (e) {
        console.warn('[VidyaApp] Backend failed, falling back to offline engine:', e);
      }
    }

    // 2. Client-Side Offline Engine Fallback
    if (!translationResult) {
      translationResult = offlineEngine.translateOffline(cleanText, targetLang);
    }

    // Update UI
    if (transEl) transEl.textContent = translationResult.translated_text;
    if (phoneticEl) {
      phoneticEl.textContent = translationResult.pronunciation ? `🗣️ उच्चारण: ${translationResult.pronunciation}` : '';
    }

    // Highlight vocab tags
    if (vocabTagsEl) {
      vocabTagsEl.innerHTML = '';
      const vocabs = translationResult.vocabulary_highlight || [];
      vocabs.forEach(v => {
        const tag = document.createElement('span');
        tag.className = 'vocab-tag';
        tag.textContent = `${v.hi} = ${v.target} (${v.phonetic || ''})`;
        vocabTagsEl.appendChild(tag);
      });
    }

    // Automatically speak the translated text for students!
    speechManager.speakText(translationResult.translated_text, 'hi-IN');

    // Add to reel history
    this.addLiveHistory(translationResult);
  }

  addLiveHistory(item) {
    this.history.unshift(item);
    if (this.history.length > 20) this.history.pop();

    const reelContainer = document.getElementById('classroom-transcript-reel');
    if (!reelContainer) return;

    const row = document.createElement('div');
    row.className = 'transcript-item';
    row.innerHTML = `
      <div class="transcript-meta">
        <span>⏰ ${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}</span>
        <button class="small-play-btn" title="पुनः सुनें">🔊</button>
      </div>
      <div class="transcript-hindi"><strong>शिक्षक:</strong> ${this.escapeHtml(item.source_text)}</div>
      <div class="transcript-tribal"><strong>मातृभाषा:</strong> ${this.escapeHtml(item.translated_text)}</div>
      ${item.pronunciation ? `<div class="transcript-phonetic">(${this.escapeHtml(item.pronunciation)})</div>` : ''}
    `;

    row.querySelector('.small-play-btn').addEventListener('click', () => {
      speechManager.speakText(item.translated_text, 'hi-IN');
    });

    reelContainer.prepend(row);
  }

  async loadLessons() {
    try {
      if (!offlineEngine.isOffline()) {
        const res = await fetch('/api/lessons');
        if (res.ok) {
          const data = await res.json();
          this.lessons = data.lessons || [];
          // Pre-cache lessons to IndexedDB for offline access
          for (let l of this.lessons) {
            await offlineEngine.saveLessonOffline(l);
          }
          this.renderLessonsGrid();
          return;
        }
      }
    } catch (e) {
      console.warn('[VidyaApp] Could not fetch lessons from server, checking local cache.');
    }

    // Load from IndexedDB offline storage
    this.lessons = await offlineEngine.getOfflineLessons();
    this.renderLessonsGrid();
  }

  setupLessonMode() {
    // Grade Filter tabs
    const gradeTabs = document.querySelectorAll('.grade-filter-tab');
    gradeTabs.forEach(tab => {
      tab.addEventListener('click', () => {
        gradeTabs.forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        const filter = tab.getAttribute('data-grade');
        this.renderLessonsGrid(filter);
      });
    });

    // Back to lesson grid button
    document.getElementById('back-to-lessons-btn')?.addEventListener('click', () => {
      document.getElementById('single-lesson-view')?.classList.add('hidden');
      document.getElementById('lessons-browser-view')?.classList.remove('hidden');
    });

    // Read full lesson aloud
    document.getElementById('listen-full-lesson-btn')?.addEventListener('click', () => {
      if (this.activeLesson) {
        const targetLang = window.currentSelectedLanguage || 'gondi';
        const fullText = this.activeLesson.sentences.map(s => s.trans[targetLang] || s.hi).join(' ');
        speechManager.speakText(fullText, 'hi-IN');
      }
    });

    // Tab switcher between Reading, Worksheets, Flashcards
    const lessonSubTabs = document.querySelectorAll('.lesson-sub-tab');
    lessonSubTabs.forEach(tab => {
      tab.addEventListener('click', () => {
        lessonSubTabs.forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        const tabTarget = tab.getAttribute('data-tab-target');

        document.getElementById('tab-bilingual-reading')?.classList.add('hidden');
        document.getElementById('tab-bilingual-worksheet')?.classList.add('hidden');
        document.getElementById('tab-bilingual-flashcards')?.classList.add('hidden');

        const activeContent = document.getElementById(`tab-${tabTarget}`);
        if (activeContent) activeContent.classList.remove('hidden');
      });
    });
  }

  renderLessonsGrid(gradeFilter = 'all') {
    const grid = document.getElementById('curriculum-lessons-grid');
    if (!grid) return;
    grid.innerHTML = '';

    const filtered = (gradeFilter === 'all')
      ? this.lessons
      : this.lessons.filter(l => l.grade.includes(gradeFilter) || l.badge.toLowerCase().includes(gradeFilter.toLowerCase()));

    filtered.forEach(lesson => {
      const card = document.createElement('div');
      card.className = 'lesson-card';
      card.innerHTML = `
        <div class="lesson-card-icon">${lesson.icon || '📖'}</div>
        <div class="lesson-card-badge">${lesson.badge}</div>
        <h4 class="lesson-card-title">${this.escapeHtml(lesson.title_hi)}</h4>
        <p class="lesson-card-summary">${this.escapeHtml(lesson.summary_hi || '')}</p>
        <div class="lesson-card-footer">
          <span class="lesson-count-tag">${lesson.sentences.length} द्विभाषी वाक्य</span>
          <button class="open-lesson-btn btn btn-sm btn-primary">पाठ खोलें →</button>
        </div>
      `;

      card.querySelector('.open-lesson-btn').addEventListener('click', () => {
        this.openLessonDetail(lesson);
      });

      grid.appendChild(card);
    });
  }

  openLessonDetail(lesson) {
    this.activeLesson = lesson;
    document.getElementById('lessons-browser-view')?.classList.add('hidden');
    const detailView = document.getElementById('single-lesson-view');
    if (detailView) detailView.classList.remove('hidden');

    const titleEl = document.getElementById('active-lesson-title');
    const badgeEl = document.getElementById('active-lesson-badge');
    const sentencesContainer = document.getElementById('lesson-bilingual-sentences-container');

    if (titleEl) titleEl.textContent = lesson.title_hi;
    if (badgeEl) badgeEl.textContent = `${lesson.grade} | ${lesson.subject}`;

    const targetLang = window.currentSelectedLanguage || 'gondi';

    // Render Sentences
    if (sentencesContainer) {
      sentencesContainer.innerHTML = '';
      lesson.sentences.forEach((s, idx) => {
        const transText = s.trans[targetLang] || s.trans['gondi'] || s.hi;
        const phonetic = s.phonetic ? (s.phonetic[targetLang] || s.phonetic['gondi'] || '') : '';

        const row = document.createElement('div');
        row.className = 'lesson-sentence-row';
        row.innerHTML = `
          <div class="sentence-number">${idx + 1}</div>
          <div class="sentence-content">
            <div class="hi-text">${this.escapeHtml(s.hi)}</div>
            <div class="tg-text">${this.escapeHtml(transText)}</div>
            ${phonetic ? `<div class="ph-text">🗣️ उच्चारण: <em>${this.escapeHtml(phonetic)}</em></div>` : ''}
          </div>
          <button class="listen-sentence-btn" title="सुनें">🔊</button>
        `;

        row.querySelector('.listen-sentence-btn').addEventListener('click', () => {
          speechManager.speakText(transText, 'hi-IN');
        });

        sentencesContainer.appendChild(row);
      });
    }

    // Initialize Flashcards
    if (typeof worksheetsEngine !== 'undefined') {
      worksheetsEngine.initFlashcards(lesson.flashcards || []);
      // Render Lesson Worksheet
      if (lesson.worksheet) {
        worksheetsEngine.renderWorksheet({
          title: `अभ्यास पत्र: ${lesson.title_hi}`,
          target_language: targetLang.toUpperCase(),
          match_words: lesson.worksheet.questions.find(q => q.type === 'match')?.pairs || [],
          fill_in_the_blanks: lesson.worksheet.questions.filter(q => q.type === 'blank').map(b => ({
            question_hi: b.q_hi,
            target_hint: b.hint,
            answer: b.answer
          })),
          multiple_choice: lesson.worksheet.questions.filter(q => q.type === 'mcq').map(m => ({
            question_hi: m.q_hi,
            question_target: m.q_target,
            options: m.options,
            correct_index: m.answer
          }))
        });
      }
    }
  }

  setupOfflineScreen() {
    const downloadAllBtn = document.getElementById('download-all-offline-btn');
    const storageStatsEl = document.getElementById('offline-storage-stats');

    const updateStats = async () => {
      const lessons = await offlineEngine.getOfflineLessons();
      if (storageStatsEl) {
        storageStatsEl.innerHTML = `
          <strong>सहेजे गए पाठ (Cached Lessons):</strong> ${lessons.length} पाठ तैयार<br>
          <strong>ऑफलाइन शब्दकोश (Offline Vocabulary):</strong> 6 भाषाएँ (गोंडी, संथाली, भीली, तेलुगु, मुंडारी, कुड़ुख़)<br>
          <strong>नेटवर्क स्थिति:</strong> ${offlineEngine.isOffline() ? '🔴 ऑफ़लाइन (Zero Internet Required)' : '🟢 ऑनलाइन'}
        `;
      }
    };

    downloadAllBtn?.addEventListener('click', async () => {
      downloadAllBtn.textContent = '📥 डाउनलोड हो रहा है...';
      await this.loadLessons();
      downloadAllBtn.textContent = '✓ सभी पाठ सफलतापूर्वक डाउनलोड हुए!';
      await updateStats();
      setTimeout(() => {
        downloadAllBtn.textContent = '📥 सभी पाठ ऑफ़लाइन डाउनलोड करें';
      }, 3000);
    });

    updateStats();
  }

  registerServiceWorker() {
    if ('serviceWorker' in navigator) {
      window.addEventListener('load', () => {
        navigator.serviceWorker.register('./sw.js')
          .then(reg => console.log('[VidyaApp] PWA Service Worker registered:', reg.scope))
          .catch(err => console.warn('[VidyaApp] Service Worker registration failed:', err));
      });
    }
  }

  escapeHtml(str) {
    if (!str) return '';
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }
}

// Instantiate on DOM load
window.addEventListener('DOMContentLoaded', () => {
  window.vidyaApp = new VidyaApp();
  window.vidyaApp.init();
});
