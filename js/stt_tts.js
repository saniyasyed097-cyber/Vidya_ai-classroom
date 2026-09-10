/**
 * VIDYA AI - Speech-to-Text (STT) & Text-to-Speech (TTS) Manager
 * Provides Hindi voice capture and crystal-clear pronunciation audio playback.
 */

class SpeechManager {
  constructor() {
    this.recognition = null;
    this.isListening = false;
    this.onResultCallback = null;
    this.onStatusCallback = null;
    this.audioContext = null;

    this.initSpeechRecognition();
  }

  initSpeechRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      console.warn('[SpeechManager] Web Speech API not supported in this browser.');
      return;
    }

    try {
      this.recognition = new SpeechRecognition();
      this.recognition.lang = 'hi-IN'; // Source language fixed to Hindi
      this.recognition.continuous = false;
      this.recognition.interimResults = true;
      this.recognition.maxAlternatives = 1;

      this.recognition.onstart = () => {
        this.isListening = true;
        this.playBeep(440, 0.1); // Audio cue for listening start
        if (this.onStatusCallback) this.onStatusCallback('listening');
      };

      this.recognition.onresult = (event) => {
        let interimTranscript = '';
        let finalTranscript = '';

        for (let i = event.resultIndex; i < event.results.length; ++i) {
          if (event.results[i].isFinal) {
            finalTranscript += event.results[i][0].transcript;
          } else {
            interimTranscript += event.results[i][0].transcript;
          }
        }

        if (this.onResultCallback) {
          this.onResultCallback({
            final: finalTranscript.trim(),
            interim: interimTranscript.trim()
          });
        }
      };

      this.recognition.onerror = (event) => {
        console.warn('[SpeechManager] Speech recognition error:', event.error);
        this.isListening = false;
        if (this.onStatusCallback) this.onStatusCallback('error', event.error);
      };

      this.recognition.onend = () => {
        this.isListening = false;
        if (this.onStatusCallback) this.onStatusCallback('idle');
      };
    } catch (e) {
      console.error('[SpeechManager] Error creating SpeechRecognition:', e);
    }
  }

  startListening(onResult, onStatus) {
    this.onResultCallback = onResult;
    this.onStatusCallback = onStatus;

    if (!this.recognition) {
      this.initSpeechRecognition();
    }

    if (!this.recognition) {
      alert('Speech Recognition is not supported by your browser. Please use Google Chrome, Edge, or enter text manually.');
      return;
    }

    try {
      this.recognition.start();
    } catch (e) {
      console.warn('[SpeechManager] Could not start speech recognition:', e);
      try {
        this.recognition.stop();
        setTimeout(() => this.recognition.start(), 200);
      } catch (err) {}
    }
  }

  stopListening() {
    if (this.recognition && this.isListening) {
      try {
        this.recognition.stop();
        this.playBeep(330, 0.1); // Audio cue for listening end
      } catch (e) {}
    }
    this.isListening = false;
  }

  /**
   * High-clarity Text-to-Speech playback for Hindi and tribal phonetic pronunciation.
   */
  speakText(text, langCode = 'hi-IN') {
    if (!window.speechSynthesis) {
      console.warn('[SpeechManager] SpeechSynthesis not supported.');
      return;
    }

    // Cancel any ongoing speech
    window.speechSynthesis.cancel();

    const cleanText = (text || '').trim();
    if (!cleanText) return;

    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.lang = langCode;
    utterance.rate = 0.85; // Slightly slower pace for young children in classrooms
    utterance.pitch = 1.05; // Friendly, clear teacher tone

    // Try to pick a natural Indian accent voice if installed
    const voices = window.speechSynthesis.getVoices();
    const preferredVoice = voices.find(v => 
      (v.lang === 'hi-IN' || v.lang.startsWith('hi')) ||
      (v.lang.includes('IN') && !v.name.includes('English'))
    );
    if (preferredVoice) {
      utterance.voice = preferredVoice;
    }

    window.speechSynthesis.speak(utterance);
  }

  // Simple web audio feedback beep
  playBeep(freq = 440, duration = 0.1) {
    try {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (!AudioCtx) return;
      if (!this.audioContext) this.audioContext = new AudioCtx();
      if (this.audioContext.state === 'suspended') this.audioContext.resume();

      const osc = this.audioContext.createOscillator();
      const gain = this.audioContext.createGain();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(freq, this.audioContext.currentTime);
      gain.gain.setValueAtTime(0.08, this.audioContext.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.0001, this.audioContext.currentTime + duration);

      osc.connect(gain);
      gain.connect(this.audioContext.destination);
      osc.start();
      osc.stop(this.audioContext.currentTime + duration);
    } catch (e) {}
  }
}

const speechManager = new SpeechManager();
