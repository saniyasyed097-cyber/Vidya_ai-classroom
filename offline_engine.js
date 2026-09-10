/**
 * VIDYA AI - Offline Linguistic & Storage Engine
 * Provides instant in-browser translation, phonetic guides, and IndexedDB caching
 * so the application functions 100% offline in rural tribal classrooms.
 */

class OfflineEngine {
  constructor() {
    this.isSimulatedOffline = false;
    this.db = null;
    this.initDatabase();

    // Embedded Offline Dictionaries (Hindi -> Tribal Languages)
    this.offlineDictionary = {
      gondi: {
        "नमस्ते": { trans: "सेवा जोहार", phonetic: "Sewa Johar" },
        "शुभ प्रभात": { trans: "सबेरे जोहार", phonetic: "Sabere Johar" },
        "बैठ जाओ": { trans: "कुंदुट", phonetic: "Kundut" },
        "खड़े हो जाओ": { trans: "तेड़सी नितुट", phonetic: "Tedsi Nitut" },
        "किताब": { trans: "पोथी", phonetic: "Pothi" },
        "किताब खोलो": { trans: "पोथी उघड़ कीम", phonetic: "Pothi Ughad Keem" },
        "सुनो": { trans: "केंजुट", phonetic: "Kenjut" },
        "लिखो": { trans: "लिखी कीम", phonetic: "Likhi Keem" },
        "पढ़ो": { trans: "वाचा कीम", phonetic: "Vaacha Keem" },
        "बहुत अच्छा": { trans: "बेसब बेशर", phonetic: "Besab Beshar" },
        "पौधा": { trans: "मरका", phonetic: "Marka" },
        "पौधे": { trans: "मरान", phonetic: "Maraan" },
        "पौधों": { trans: "मरान तेकी", phonetic: "Maraan teki" },
        "पेड़": { trans: "मरा", phonetic: "Maraa" },
        "पत्ती": { trans: "आकी", phonetic: "Aaki" },
        "पत्तियां": { trans: "आकीन", phonetic: "Aakeen" },
        "पत्ते": { trans: "आकीन", phonetic: "Aakeen" },
        "जड़": { trans: "वेर", phonetic: "Vehr" },
        "फूल": { trans: "पुंगार", phonetic: "Pungaar" },
        "फल": { trans: "पंज", phonetic: "Panj" },
        "बीज": { trans: "विज्जा", phonetic: "Vijja" },
        "पानी": { trans: "येर", phonetic: "Yer" },
        "जल": { trans: "येर", phonetic: "Yer" },
        "सूर्य": { trans: "पोरदु", phonetic: "Pordu" },
        "धूप": { trans: "पोरदु वेलंग", phonetic: "Pordu Velang" },
        "सूर्य का प्रकाश": { trans: "पोरदुना वेलंग", phonetic: "Porduna Velang" },
        "मिट्टी": { trans: "नली", phonetic: "Nalee" },
        "हवा": { trans: "वली", phonetic: "Valee" },
        "वर्षा": { trans: "पिरी", phonetic: "Piree" },
        "बारिश": { trans: "पिरी", phonetic: "Piree" },
        "बादल": { trans: "मिर", phonetic: "Mir" },
        "चाहिए": { trans: "पाइजे", phonetic: "Paije" },
        "और": { trans: "अन", phonetic: "An" },
        "के लिए": { trans: "संगे", phonetic: "Sange" },
        "बढ़ने": { trans: "वाड़ी कीने", phonetic: "Vaadee keene" },
        "होता है": { trans: "आंद", phonetic: "Aand" },
        "है": { trans: "आंद", phonetic: "Aand" },
        "हैं": { trans: "आंदुंग", phonetic: "Aandung" },
        "एक": { trans: "उंदी", phonetic: "Undi" },
        "दो": { trans: "रंड", phonetic: "Rand" },
        "तीन": { trans: "मूंद", phonetic: "Moond" },
        "चार": { trans: "नालंग", phonetic: "Naalang" },
        "पांच": { trans: "सयंग", phonetic: "Sayang" },
        "बच्चा": { trans: "पिला", phonetic: "Pila" },
        "बच्चे": { trans: "पिलांग", phonetic: "Pilaang" },
        "बच्चों": { trans: "पिलांग कुन", phonetic: "Pilaang kun" }
      },
      santhali: {
        "नमस्ते": { trans: "जोहार", phonetic: "Johar" },
        "शुभ प्रभात": { trans: "सेताः जोहार", phonetic: "Setaah Johar" },
        "बैठ जाओ": { trans: "दुब मे", phonetic: "Dub Me" },
        "किताब": { trans: "पुथी", phonetic: "Puthi" },
        "किताब खोलो": { trans: "पुथी झिज मे", phonetic: "Puthi Jhij Me" },
        "पौधा": { trans: "दारि", phonetic: "Daari" },
        "पौधे": { trans: "दारि को", phonetic: "Daari Ko" },
        "पौधों": { trans: "दारि को लागीद", phonetic: "Daari Ko Laageed" },
        "पेड़": { trans: "दारे", phonetic: "Daare" },
        "पत्ती": { trans: "साकाम", phonetic: "Saakaam" },
        "पत्तियां": { trans: "साकाम को", phonetic: "Saakaam Ko" },
        "जड़": { trans: "रेहेत", phonetic: "Rehet" },
        "फूल": { trans: "बाहा", phonetic: "Baaha" },
        "फल": { trans: "जो", phonetic: "Jo" },
        "पानी": { trans: "दाः", phonetic: "Daah" },
        "जल": { trans: "दाः", phonetic: "Daah" },
        "सूर्य": { trans: "सिंगी", phonetic: "Singi" },
        "सूर्य का प्रकाश": { trans: "सिंगी मार्शल", phonetic: "Singi Maarshal" },
        "मिट्टी": { trans: "हासा", phonetic: "Haasa" },
        "हवा": { trans: "होय", phonetic: "Hoy" },
        "वर्षा": { trans: "दाः जाड़ि", phonetic: "Daah Jaadi" },
        "चाहिए": { trans: "दरकार / लाकती", phonetic: "Laaktee" },
        "और": { trans: "आर", phonetic: "Aar" },
        "के लिए": { trans: "लागीद", phonetic: "Laageed" },
        "बढ़ने": { trans: "हाराः लागीद", phonetic: "Haaraah laageed" },
        "एक": { trans: "मित", phonetic: "Mit" },
        "दो": { trans: "बार", phonetic: "Baar" },
        "तीन": { trans: "पे", phonetic: "Peh" },
        "चार": { trans: "पोन", phonetic: "Pon" },
        "पांच": { trans: "मोड़े", phonetic: "Mode" }
      },
      bhili: {
        "नमस्ते": { trans: "राम राम / जोहार", phonetic: "Ram Ram / Johar" },
        "बैठ जाओ": { trans: "बेही जावो", phonetic: "Behi Jaavo" },
        "किताब खोलो": { trans: "चोपड़ी खोलो", phonetic: "Chopdi Kholo" },
        "पौधा": { trans: "छोड", phonetic: "Chhod" },
        "पौधे": { trans: "छोडिया", phonetic: "Chhodiya" },
        "पौधों": { trans: "छोडिया ने", phonetic: "Chhodiya ne" },
        "पेड़": { trans: "झाड़", phonetic: "Jhaad" },
        "पत्ती": { trans: "पानडु", phonetic: "Paandu" },
        "पत्तियां": { trans: "पांदड़ा", phonetic: "Paandada" },
        "पानी": { trans: "पाणी", phonetic: "Paani" },
        "सूर्य": { trans: "सूरज", phonetic: "Sooraj" },
        "सूर्य का प्रकाश": { trans: "सूरज नो उजास", phonetic: "Sooraj no Ujaas" },
        "मिट्टी": { trans: "माटी", phonetic: "Maati" },
        "हवा": { trans: "वायरो", phonetic: "Vaayaro" },
        "चाहिए": { trans: "जोवे", phonetic: "Jove" },
        "और": { trans: "ने", phonetic: "Ne" },
        "बढ़ने": { trans: "वधवा सारु", phonetic: "Vadhva saaru" },
        "एक": { trans: "एक", phonetic: "Ek" },
        "दो": { trans: "बे", phonetic: "Bey" }
      },
      telugu: {
        "नमस्ते": { trans: "నమస్కారం", phonetic: "Namaskaram" },
        "बैठ जाओ": { trans: "కూర్చోండి", phonetic: "Koorchondi" },
        "किताब खोलो": { trans: "పుస్తకం తెరవండి", phonetic: "Pustakam Teravandi" },
        "पौधा": { trans: "మొక్క", phonetic: "Mokka" },
        "पौधे": { trans: "మొక్కలు", phonetic: "Mokkalu" },
        "पौधों": { trans: "మొక్కలు ఎదగడానికి", phonetic: "Mokkalu Edagadaniki" },
        "पेड़": { trans: "చెట్టు", phonetic: "Chettu" },
        "पत्ती": { trans: "ఆకు", phonetic: "Aaku" },
        "पत्तियां": { trans: "ఆకులు", phonetic: "Aakulu" },
        "पानी": { trans: "నీరు", phonetic: "Neeru" },
        "जल": { trans: "నీరు", phonetic: "Neeru" },
        "सूर्य": { trans: "సూర్యుడు", phonetic: "Sooryudu" },
        "सूर्य का प्रकाश": { trans: "సూర్యరశ్మి", phonetic: "Sooryarashmi" },
        "चाहिए": { trans: "కావాలి", phonetic: "Kaavaali" },
        "और": { trans: "మరియు", phonetic: "Mariyu" },
        "बढ़ने": { trans: "ఎదగడానికి", phonetic: "Edagadaaniki" }
      },
      mundari: {
        "नमस्ते": { trans: "जोहार", phonetic: "Johar" },
        "पौधा": { trans: "दारु", phonetic: "Daaru" },
        "पौधे": { trans: "दारु को", phonetic: "Daaru Ko" },
        "पानी": { trans: "दाः", phonetic: "Daah" },
        "सूर्य": { trans: "सिंगी", phonetic: "Singi" },
        "चाहिए": { trans: "दरकार", phonetic: "Dorkaar" }
      },
      kurukh: {
        "नमस्ते": { trans: "जोहार", phonetic: "Johar" },
        "पौधा": { trans: "मन", phonetic: "Mann" },
        "पौधे": { trans: "मन गुठी", phonetic: "Mann Guthi" },
        "पानी": { trans: "अम्म", phonetic: "Amm" },
        "सूर्य": { trans: "बीड़ी", phonetic: "Beedi" },
        "चाहिए": { trans: "चाही", phonetic: "Chaahi" }
      }
    };

    // Pre-curated sentence pairs for offline instant response
    this.offlineCuratedPairs = {
      gondi: {
        "पौधों को बढ़ने के लिए पानी और सूर्य का प्रकाश चाहिए": {
          trans: "मरान तेकी वाड़ी कीने संगे येर अन पोरदु वेलंग पाइजे।",
          phonetic: "Maraan teki vaadee keene sange yer an pordu velang paije."
        },
        "पौधों को पानी चाहिए": {
          trans: "मरान तेकी येर पाइजे।",
          phonetic: "Maraan teki yer paije."
        },
        "जल ही जीवन है": {
          trans: "येरे जीवाना आंद।",
          phonetic: "Yere jeevana aand."
        },
        "सभी बच्चे अपनी किताब खोलें": {
          trans: "सब्बू पिलांग तंतना पोथी उघड़ कीम।",
          phonetic: "Sabbu pilaang tantna pothi ughad keem."
        },
        "नमस्ते बच्चों, आप कैसे हैं": {
          trans: "सेवा जोहार पिलांग, मीट बहके आंदिट?",
          phonetic: "Sewa johar pilaang, meet bahke aandit?"
        }
      },
      santhali: {
        "पौधों को बढ़ने के लिए पानी और सूर्य का प्रकाश चाहिए": {
          trans: "दारि को हाराः लागीद दाः आर सिंगी मार्शल लाकती मेनाः आ।",
          phonetic: "Daari ko haaraah laageed daah aar singi maarshal laaktee menaah aa."
        },
        "जल ही जीवन है": {
          trans: "दाः गे जीवन काना।",
          phonetic: "Daah ge jeevan kaana."
        }
      },
      bhili: {
        "पौधों को बढ़ने के लिए पानी और सूर्य का प्रकाश चाहिए": {
          trans: "छोडिया ने वधवा सारु पाणी ने सूरज नो उजास जोवे।",
          phonetic: "Chhodiya ne vadhva saaru paani ne sooraj no ujaas jove."
        }
      },
      telugu: {
        "पौधों को बढ़ने के लिए पानी और सूर्य का प्रकाश चाहिए": {
          trans: "మొక్కలు ఎదగడానికి నీరు మరియు సూర్యరశ్మి కావాలి.",
          phonetic: "Mokkalu edagadaaniki neeru mariyu sooryarashmi kaavaali."
        }
      }
    };
  }

  // Initialize IndexedDB
  initDatabase() {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open('VidyaAI_Classroom_DB', 2);

      request.onupgradeneeded = (event) => {
        const db = event.target.result;
        if (!db.objectStoreNames.contains('offline_lessons')) {
          db.createObjectStore('offline_lessons', { keyPath: 'id' });
        }
        if (!db.objectStoreNames.contains('translation_history')) {
          db.createObjectStore('translation_history', { autoIncrement: true });
        }
        if (!db.objectStoreNames.contains('custom_vocabulary')) {
          db.createObjectStore('custom_vocabulary', { autoIncrement: true });
        }
      };

      request.onsuccess = (event) => {
        this.db = event.target.result;
        console.log('[OfflineEngine] IndexedDB initialized successfully.');
        resolve(this.db);
      };

      request.onerror = (event) => {
        console.warn('[OfflineEngine] IndexedDB error:', event.target.error);
        resolve(null);
      };
    });
  }

  // Check if system is effectively offline (actual offline or simulated)
  isOffline() {
    return this.isSimulatedOffline || !navigator.onLine;
  }

  setSimulatedOffline(status) {
    this.isSimulatedOffline = status;
    console.log(`[OfflineEngine] Simulate Offline Mode: ${status}`);
  }

  /**
   * Translates Hindi text offline using pure client-side dictionary & grammatical rules.
   */
  translateOffline(hindiText, targetLang = 'gondi') {
    targetLang = (targetLang || 'gondi').toLowerCase();
    const cleanText = (hindiText || '').trim();
    if (!cleanText) {
      return {
        source_text: '',
        translated_text: '',
        pronunciation: '',
        target_lang: targetLang,
        confidence: 1.0,
        is_offline: true
      };
    }

    const bareKey = cleanText.replace(/[।\.!?]/g, '').trim();

    // 1. Curated sentence lookup
    if (this.offlineCuratedPairs[targetLang] && this.offlineCuratedPairs[targetLang][bareKey]) {
      const match = this.offlineCuratedPairs[targetLang][bareKey];
      return {
        source_text: cleanText,
        translated_text: match.trans,
        pronunciation: match.phonetic,
        target_lang: targetLang,
        confidence: 0.98,
        engine: 'offline_curated_pair',
        is_offline: true
      };
    }

    // 2. Tokenized dictionary mapping
    const langDict = this.offlineDictionary[targetLang] || this.offlineDictionary['gondi'];
    const tokens = cleanText.match(/[\u0900-\u097F]+|[A-Za-z]+|[0-9]+|[^\s\w]/g) || [cleanText];

    const translatedTokens = [];
    const phoneticTokens = [];
    const matchedVocab = [];

    let i = 0;
    while (i < tokens.length) {
      // 2-word phrase check
      if (i + 1 < tokens.length) {
        const p2 = `${tokens[i]} ${tokens[i+1]}`;
        if (langDict[p2]) {
          translatedTokens.push(langDict[p2].trans);
          phoneticTokens.push(langDict[p2].phonetic);
          matchedVocab.push({ hi: p2, target: langDict[p2].trans, phonetic: langDict[p2].phonetic });
          i += 2;
          continue;
        }
      }

      const tok = tokens[i];
      if (langDict[tok]) {
        translatedTokens.push(langDict[tok].trans);
        phoneticTokens.push(langDict[tok].phonetic);
        matchedVocab.push({ hi: tok, target: langDict[tok].trans, phonetic: langDict[tok].phonetic });
      } else {
        translatedTokens.push(tok);
        phoneticTokens.push(tok);
      }
      i++;
    }

    let translated = translatedTokens.join(' ').replace(/\s+([।,;!?\.])/g, '$1').trim();
    let phonetics = phoneticTokens.join(' ').replace(/\s+([।,;!?\.])/g, '$1').trim();

    return {
      source_text: cleanText,
      translated_text: translated,
      pronunciation: phonetics,
      target_lang: targetLang,
      confidence: 0.88,
      engine: 'offline_client_dictionary',
      is_offline: true,
      vocabulary_highlight: matchedVocab
    };
  }

  // Save lesson to IndexedDB for offline access
  async saveLessonOffline(lesson) {
    if (!this.db) return false;
    return new Promise((resolve) => {
      try {
        const tx = this.db.transaction('offline_lessons', 'readwrite');
        const store = tx.objectStore('offline_lessons');
        store.put(lesson);
        tx.oncomplete = () => resolve(true);
        tx.onerror = () => resolve(false);
      } catch (e) {
        resolve(false);
      }
    });
  }

  // Retrieve all cached lessons
  async getOfflineLessons() {
    if (!this.db) return [];
    return new Promise((resolve) => {
      try {
        const tx = this.db.transaction('offline_lessons', 'readonly');
        const store = tx.objectStore('offline_lessons');
        const req = store.getAll();
        req.onsuccess = () => resolve(req.result || []);
        req.onerror = () => resolve([]);
      } catch (e) {
        resolve([]);
      }
    });
  }

  // Save history item locally
  async recordOfflineHistory(item) {
    if (!this.db) return;
    try {
      const tx = this.db.transaction('translation_history', 'readwrite');
      const store = tx.objectStore('translation_history');
      store.add({ ...item, timestamp: Date.now() });
    } catch (e) {}
  }
}

const offlineEngine = new OfflineEngine();
