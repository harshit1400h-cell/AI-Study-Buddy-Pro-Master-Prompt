# AI Study Buddy Pro — Intelligent AI Learning Platform 🎓

**AI Study Buddy Pro** is a modern, full-stack, AI-powered learning web application designed to help students master any subject from textbooks, research papers, and lecture notes.

Built with a high-performance **FastAPI** backend and an ultra-modern, glassmorphic **Tailwind CSS + ES6+** frontend, the platform features multi-provider AI support (Google Gemini, OpenAI GPT, and a built-in Smart Local Pedagogical NLP Engine that works 100% offline out-of-the-box).

---

## 🌟 Key Features

### 1. 📚 Multi-Modal Document Ingestion & PyPDF Engine
- **PDF & Text Extraction**: Upload multi-page PDF textbooks, slide decks, markdown, or paste raw notes directly into the UI.
- **Page-Aware Chunking**: Intelligently chunks text while preserving page number boundaries for precise academic citations (`[Page X]`).
- **Pre-Loaded Sample Materials**: Comes pre-packaged with curated university-level study documents (*Deep Learning & Neural Networks*, *Cognitive Psychology & Memory Science*) for instant 1-click testing.

### 2. 💬 Context-Grounded AI Study Tutor (RAG Pipeline)
- **Multi-Persona Teaching**:
  - 🎓 **Academic Professor**: Thorough scholarly explanations, derivations, and formal definitions.
  - 💡 **Socratic Guide**: Thought-provoking hints and leading questions to help you arrive at the answer.
  - 🎈 **ELI5 Simplifier**: Intuitive everyday analogies with zero intimidating jargon.
  - 🎯 **Exam Coach**: High-yield exam traps, memory mnemonics, and rapid-fire tests.
- **Source Citations**: Every assistant response includes verifiable citation badges linking directly to source page excerpts.
- **Math & Code Rendering**: Native KaTeX formatting for equations (e.g., $\sigma(z) = \frac{1}{1 + e^{-z}}$) and syntax highlighting for code.

### 3. 🗂️ Smart Flashcards & Leitner Spaced Repetition
- **Automatic High-Yield Extraction**: Generates Q&A decks focused on foundational definitions and causal mechanisms.
- **3D Interactive Card UI**: Smooth flip card with keyboard shortcuts (`Space` to flip, `Arrow` keys to navigate).
- **Leitner Box Algorithm**: 5-tier mastery progression (`🔴 Hard` resets to Box 1, `🟡 Good` maintains, `🟢 Easy` advances to Box 2-5).
- **Audio Pronunciation**: Uses browser SpeechSynthesis for instant audio narration of cards.

### 4. 📝 Adaptive Exam & Quiz Simulator
- **Configurable Tests**: Choose question count (3 to 10) and difficulty levels (*Easy*, *Medium*, *Hard*).
- **Timed Assessment**: Live countdown timer and question jumper navigation pills.
- **Diagnostic Feedback**: Detailed score percentages, celebration confetti for $\ge 80\%$, and in-depth rationales for why options are correct or incorrect.

### 5. 🧠 Executive Summaries & Interactive Knowledge Graph
- **High-Yield TL;DR**: 2-3 sentence executive summary of complex chapters.
- **Key Takeaways & Exam Checklist**: High-priority bullet points and common exam pitfalls.
- **Vocabulary Glossary**: Filterable term definitions.
- **Dynamic SVG Mind Map**: Radial concept topology visualizing hierarchical relationships between topics.
- **Export Study Guide**: 1-click export to Markdown (`.md`).

### 6. ⏱️ Focus Pomodoro Timer & Ambient Sound Synthesizer
- **Web Audio API Sound Engine**: Real-time synthesized ambient sounds:
  - 🌧️ Soft Rainfall (filtered Brownian noise)
  - 🧘 432Hz Alpha Beat (calming harmonic binaural oscillations)
  - 📻 White Noise
- **Cycle Tracker**: 25m Focus / 5m Short Break / 15m Long Break with completion chimes.
- **Session Logging**: Automatically saves completed study sessions into the learning analytics database.

### 7. 📊 Learning Analytics & Mastery Dashboard
- Visualizes study duration trends over the past 7 days using Chart.js.
- Tracks active recall retention and Leitner Box distribution.
- Generates dynamic study recommendations based on performance.

### 8. ⚙️ Multi-Provider AI Engine (Hybrid Cloud & Offline)
- **Zero-Setup Local Engine**: Works immediately without any API key required!
- **Google Gemini**: Integrates with `gemini-1.5-flash`, `gemini-2.0-flash`, and `gemini-1.5-pro`.
- **OpenAI**: Integrates with `gpt-4o-mini`, `gpt-4o`, and `gpt-3.5-turbo`.
- **Live Key Verification**: In-app test button to verify credentials instantly.

---

## 🏗️ Architecture & Tech Stack

```
├── app/
│   ├── config.py             # Settings and API key manager (.env, runtime config)
│   ├── database.py           # SQLite database schema, connections, repository CRUD
│   ├── pdf_processor.py      # PDF parser (PyPDF), text chunker, citation page tracker
│   ├── ai_service.py         # Multi-provider AI interface (Gemini, OpenAI, Local NLP)
│   ├── rag_engine.py         # TF-IDF / BM25 token retrieval with page citation ranking
│   ├── models.py             # Pydantic schemas for requests and responses
│   ├── sample_data.py        # University-level sample curriculum
│   └── routers/
│       ├── documents.py      # Uploads, file ingestion, sample loader
│       ├── chat.py           # AI Tutor endpoints with RAG context
│       ├── flashcards.py     # Flashcard generation & Leitner updates
│       ├── quizzes.py        # Quiz creation & diagnostic grading
│       ├── summaries.py      # TL;DR, glossary, and mind map endpoints
│       ├── analytics.py      # Progress tracking & session logs
│       └── settings.py       # AI Provider configuration & verification
├── static/
│   ├── css/style.css         # Glassmorphism, 3D card flips, SVG styling
│   ├── js/
│   │   ├── api.js            # Unified async fetch API client
│   │   ├── app.js            # Master state manager & view router
│   │   ├── chat.js           # AI Tutor chat controller & markdown renderer
│   │   ├── flashcards.js     # 3D flashcards & spaced repetition
│   │   ├── quiz.js           # Timed quiz runner & scoring
│   │   ├── summary.js        # Executive summary & SVG mind map
│   │   ├── pomodoro.js       # Pomodoro timer & Web Audio ambient generator
│   │   └── analytics.js      # Chart.js charts & stats
│   └── index.html            # Ultra-modern single page web application
├── main.py                   # FastAPI server entry point
├── test_app.py               # Complete automated integration test suite (13 tests)
├── requirements.txt          # Python dependencies
└── run.bat                   # 1-click Windows runner
```

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Application
```bash
python main.py
```
Or double-click `run.bat` on Windows.

### 3. Open in Browser
Navigate to:
```
http://127.0.0.1:8000
```

---

## 🧪 Automated Testing
Run the comprehensive 13-point integration test suite:
```bash
python test_app.py
```
**Tests Covered:**
- Server health check
- Sample study materials seeding
- Document listing & metadata
- Real PDF ingestion and page-by-page text chunking with PyPDF
- RAG context retrieval and page-level citation tagging
- Academic & Socratic AI Tutor persona responses
- Smart flashcards generation
- Leitner Box spaced repetition review promotion
- Adaptive quiz question generation
- Diagnostic quiz submission and grading
- Executive summary, glossary, and SVG mind map generation
- Focus session logging and analytics calculations
- Multi-provider settings verification

---

## 📄 License
MIT License. Built with ❤️ for students, lifelong learners, and educators worldwide.

