# VIDYA AI (विद्या AI) — Mother Tongue Learning Classroom Web Application

A specialized, teacher-centric classroom web application designed for bilingual and tribal primary education. It translates curriculum and live spoken instruction from **Hindi (Fixed Source Language)** into tribal and regional mother tongues (**Gondi, Santhali, Bhili, Telugu, Mundari, Kurukh**), with live voice translation, live file translation, automated bilingual worksheets, interactive 3D flashcards, and 100% offline capability.

---

## 🎯 Key Project Highlights & Features

1. **Fixed Source Language: Hindi (हिन्दी)**
   - Permanently locked source language as requested (`hi`).
   - Teachers speak or input curriculum in standard Hindi, which is mapped directly into local tribal student dialects.

2. **5 Classroom-Ready Screens (Matching the Hackathon PPT Methodology)**:
   - **Screen 1 — Teacher Home (`#home`)**: Dashboard with quick status, "Start Teaching" call to action, and quick cards.
   - **Screen 2 — Select Language (`#language`)**: Fixed Hindi source badge, target language selection (Gondi, Santhali, Bhili, Telugu, Mundari, Kurukh), dialect preview, and greeting notes.
   - **Screen 3 — Live Classroom (`#live`)**: Large interactive microphone button (tap/hold to speak), Web Speech API Hindi recognition, live waveform visualizer, bilingual response cards with Devanagari script + phonetic pronunciation guides, 🔊 audio playback, and classroom transcript logs.
   - **Screen 4 — Lesson Mode (`#lessons`)**: Class 1 to 5 and FLN modules (Science "Plants", EVS "Water Cycle", Math "Counting 1-10", FLN "Greetings"). Includes bilingual reading text, **📝 Automated Bilingual Worksheets** (Match columns, fill in blanks, MCQs with instant scoring and printable layout), and **🃏 3D Interactive Flip Flashcards**.
   - **Screen 5 — Offline Mode (`#offline`)**: PWA Service Worker caching, IndexedDB local database, **"Simulate Offline Mode" toggle** for instant demonstrations without internet, and downloadable lesson packages.

3. **📄 Live Document Translation Suite (`#file-translate`)**:
   - Upload `.pdf`, `.docx`, or `.txt` syllabus notes or classroom worksheets.
   - **Live Progressive Streaming Translation**: Animates sentences translating one-by-one with a real-time progress bar.
   - Side-by-side bilingual cards with individual audio play buttons.
   - 1-click **"Generate Bilingual Worksheet from this Document"** button.
   - 1-click **"Print / Save Bilingual Handout (PDF)"** for distributing physical copies in rural village schools.

4. **100% Offline Capability & Open Web**:
   - Zero proprietary paywall or required external API keys.
   - Dual-engine architecture: Automatically uses the FastAPI backend when available, and seamlessly switches to the client-side offline dictionary and IndexedDB engine when offline or when toggled in the UI.

5. **📚 Integrated Pralekha HuggingFace Offline Dataset (`srilakshmi-08/Pralekha-bucket`)**:
   - Ingests parallel corpora from HuggingFace Bucket `srilakshmi-08/Pralekha-bucket`.
   - Builds an offline SQLite database table (`pralekha_sentence_pairs`) with indexed parallel sentence alignment between Hindi, English, and Telugu.
   - Operates with **100% offline precision**, prioritizing local SQLite dataset lookup before falling back to rules/dictionaries.

---

## 🏗️ Architecture & Team Division

```
TEACHER (Classroom)
        │
        ▼
 ┌──────────────────────────────────────────────┐
 │     VIDYA AI Web Application (PWA)           │  ← App Frontend (Your Work)
 └───────┬──────────────────────────────┬───────┘
         │                              │
  [Online / Server Mode]        [Offline / Rural Mode]
         │                              │
         ▼                              ▼
 ┌───────────────────────────┐   ┌──────────────────────────┐
 │   FastAPI Python Server   │   │  Client-Side Engine      │
 │   (localhost:8000)        │   │  - Service Worker Caching│
 ├───────────────────────────┤   │  - IndexedDB Lessons     │
 │ • /api/translate          │   │  - Offline Tribal Dict   │
 │ • /api/translate/file     │   │  - Web Speech STT & TTS  │
 │ • /api/worksheets/generate│   │  - Client Flashcards     │
 │ • /api/lessons            │   └──────────────────────────┘
 │ • /api/pralekha/stats     │
 │ • IndicTrans2 API Bridge  │
 └─────────────┬─────────────┘
               │
               ▼
 ┌───────────────────────────┐
 │ Pralekha HF SQLite DB     │  ← Offline Dataset Database (srilakshmi-08/Pralekha-bucket)
 └───────────────────────────┘
```

### Team Role Division:
- **App Team (You)**: Web UI, 5 screens, navigation, microphone voice capture, live file upload suite, audio playback, automated worksheets, 3D flashcards, IndexedDB & ServiceWorker offline caching.
- **Backend Team**: FastAPI server, SQLite database, file segmentation, REST API endpoints.
- **AI Team**: IndicTrans2 model checkpoint, Hindi -> Tribal language dataset fine-tuning, vocabulary expansion.

---

## 🚀 How to Run the Application

### Option A: 1-Click Launch on Windows
Double-click `run.bat` or run PowerShell `run.ps1`. This launches the server on `http://localhost:8000` and automatically opens your default browser.

### Option B: Command Line Launch
```bash
# Navigate to the project directory
cd C:\Users\syedj\.gemini\antigravity\scratch\vidya-ai-classroom

# Start the FastAPI server with Python
py -m uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload
```

Open your browser at:
👉 **`http://localhost:8000`**

### Running the Automated Test Suite:
```bash
py test_app.py
```

---

## 🧪 Demonstration & Presentation Steps (For Evaluators & Judges)

1. **Teacher Home Screen**:
   - Open `http://localhost:8000`. Point out the header showing **🔒 स्रोत: हिन्दी (Fixed)** and the active target dialect pill.
2. **Language Selection**:
   - Click "भाषा (Language)". Show the locked Hindi badge and select **गोंडी (Gondi)** or **संथाली (Santhali)**. Notice the greeting and regional metadata update instantly.
3. **Live Classroom Speech Translation**:
   - Click "लाइव कक्षा (Live)".
   - Tap the microphone 🎤 and speak Hindi (or click one of the quick preset buttons, like *"पौधों को पानी चाहिए"*).
   - Watch the bilingual translation appear with Devanagari script, Latin phonetic pronunciation guide, and audio playback.
4. **Live File Translation**:
   - Click "दस्तावेज (File)" and click the sample button **"🌱 कक्षा 3 विज्ञान (पौधे)"** or drag-and-drop a `.txt`/`.pdf`/`.docx` file.
   - Observe the **live streaming progressive translation** with progress percentage, audio listen buttons, and the **"Generate Bilingual Worksheet"** button.
5. **Lesson Mode & Interactive Worksheets / Flashcards**:
   - Click "पाठ (Lessons)" and open **"पौधे और उनका जीवन (Class 3 Science)"**.
   - Switch to **"अभ्यास पत्र (Worksheet)"**: Answer the MCQs and fill-in-the-blanks, click "Check Answers", or click "Print PDF" to show how rural schools can print physical handouts.
   - Switch to **"फ़्लैशकार्ड (Flashcards)"**: Click the 3D card to flip between Hindi and Tribal mother tongue with audio.
6. **Offline Mode Verification**:
   - Go to "ऑफ़लाइन (Offline)" and flip the **"Simulate Offline Mode"** toggle.
   - Notice the status pill turns red ("🔴 ऑफ़लाइन").
   - Go back to Live Classroom or Lessons — everything continues to translate and function instantly inside the browser with zero network!
