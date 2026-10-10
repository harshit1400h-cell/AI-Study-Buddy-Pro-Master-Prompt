// Adaptive Quiz Simulator Controller
const QuizModule = {
  currentQuiz: null,
  userAnswers: {}, // { question_id: "selected_string" }
  currentQuestionIndex: 0,
  timerInterval: null,
  secondsElapsed: 0,
  quizResult: null,

  init() {
    this.bindEvents();
  },

  bindEvents() {
    const startGenerateBtn = document.getElementById('quiz-open-generate-btn');
    const submitBtn = document.getElementById('quiz-submit-btn');
    const prevBtn = document.getElementById('quiz-prev-btn');
    const nextBtn = document.getElementById('quiz-next-btn');
    const retakeBtn = document.getElementById('quiz-retake-btn');
    const newQuizBtn = document.getElementById('quiz-new-btn');

    if (startGenerateBtn) {
      startGenerateBtn.addEventListener('click', () => this.showGenerateModal());
    }
    if (submitBtn) {
      submitBtn.addEventListener('click', () => this.submitQuiz());
    }
    if (prevBtn) {
      prevBtn.addEventListener('click', () => this.prevQuestion());
    }
    if (nextBtn) {
      nextBtn.addEventListener('click', () => this.nextQuestion());
    }
    if (retakeBtn) {
      retakeBtn.addEventListener('click', () => this.retakeCurrentQuiz());
    }
    if (newQuizBtn) {
      newQuizBtn.addEventListener('click', () => this.showGenerateModal());
    }

    // Difficulty radio styling
    document.querySelectorAll('input[name="quiz-diff"]').forEach(radio => {
      radio.addEventListener('change', () => {
        document.querySelectorAll('input[name="quiz-diff"]').forEach(r => {
          const lbl = r.closest('label');
          if (lbl) {
            lbl.classList.remove('border-indigo-500', 'bg-indigo-950/40');
            lbl.classList.add('border-slate-700', 'bg-slate-800');
          }
        });
        const activeLbl = radio.closest('label');
        if (activeLbl) {
          activeLbl.classList.remove('border-slate-700', 'bg-slate-800');
          activeLbl.classList.add('border-indigo-500', 'bg-indigo-950/40');
        }
      });
    });
  },

  showGenerateModal() {
    const modal = document.getElementById('generate-quiz-modal');
    if (modal) modal.classList.remove('hidden');
  },

  hideGenerateModal() {
    const modal = document.getElementById('generate-quiz-modal');
    if (modal) modal.classList.add('hidden');
  },

  async startNewQuiz(numQuestions = 5, difficulty = 'medium') {
    const modalBtn = document.getElementById('quiz-confirm-generate-btn');
    if (modalBtn) {
      modalBtn.disabled = true;
      modalBtn.innerHTML = '<span class="inline-block animate-spin mr-2">↻</span> Generating adaptive test...';
    }

    try {
      const res = await API.generateQuiz(App.activeDocumentId, null, numQuestions, difficulty);
      this.hideGenerateModal();
      this.loadQuiz(res.quiz);
      App.showToast(`Adaptive Quiz generated (${difficulty.toUpperCase()})! 🎯`, 'success');
    } catch (err) {
      App.showToast(err.message || 'Failed to generate quiz', 'error');
    } finally {
      if (modalBtn) {
        modalBtn.disabled = false;
        modalBtn.textContent = 'Start Assessment';
      }
    }
  },

  loadQuiz(quiz) {
    this.currentQuiz = quiz;
    this.userAnswers = {};
    this.currentQuestionIndex = 0;
    this.quizResult = null;
    this.secondsElapsed = 0;

    clearInterval(this.timerInterval);
    this.startTimer();

    // Toggle UI views
    document.getElementById('quiz-intro-state').classList.add('hidden');
    document.getElementById('quiz-results-state').classList.add('hidden');
    document.getElementById('quiz-active-state').classList.remove('hidden');

    document.getElementById('quiz-active-title').textContent = quiz.title;
    document.getElementById('quiz-active-diff').textContent = (quiz.difficulty || 'medium').toUpperCase();

    this.renderCurrentQuestion();
    this.renderQuestionNavPills();
  },

  startTimer() {
    const timerEl = document.getElementById('quiz-timer');
    this.timerInterval = setInterval(() => {
      this.secondsElapsed++;
      const mins = Math.floor(this.secondsElapsed / 60).toString().padStart(2, '0');
      const secs = (this.secondsElapsed % 60).toString().padStart(2, '0');
      if (timerEl) timerEl.textContent = `${mins}:${secs}`;
    }, 1000);
  },

  renderCurrentQuestion() {
    if (!this.currentQuiz || !this.currentQuiz.questions) return;
    const q = this.currentQuiz.questions[this.currentQuestionIndex];
    const total = this.currentQuiz.questions.length;

    document.getElementById('quiz-q-counter').textContent = `Question ${this.currentQuestionIndex + 1} of ${total}`;
    document.getElementById('quiz-question-text').textContent = q.question;

    const optionsContainer = document.getElementById('quiz-options-container');
    const selectedAnswer = this.userAnswers[q.id];

    optionsContainer.innerHTML = q.options.map((opt, idx) => {
      const letters = ['A', 'B', 'C', 'D', 'E'];
      const letter = letters[idx] || (idx + 1);
      const isSelected = selectedAnswer === opt;
      return `
        <button type="button"
                class="quiz-option-btn w-full text-left p-4 rounded-xl border transition-all flex items-start gap-3.5 cursor-pointer
                ${isSelected 
                  ? 'bg-indigo-600/20 border-indigo-500 text-white shadow-md shadow-indigo-500/10' 
                  : 'bg-slate-800/80 hover:bg-slate-800 border-slate-700 text-slate-200 hover:border-slate-600'}"
                onclick="QuizModule.selectOption(${q.id}, '${opt.replace(/'/g, "\\'")}')">
          <span class="w-7 h-7 rounded-lg flex items-center justify-center font-bold text-xs flex-shrink-0
                ${isSelected ? 'bg-indigo-600 text-white' : 'bg-slate-700 text-slate-300'}">
            ${letter}
          </span>
          <span class="text-sm font-medium leading-relaxed pt-0.5 flex-1">${opt}</span>
        </button>
      `;
    }).join('');

    // Update navigation button states
    const prevBtn = document.getElementById('quiz-prev-btn');
    const nextBtn = document.getElementById('quiz-next-btn');
    const submitBtn = document.getElementById('quiz-submit-btn');

    if (prevBtn) prevBtn.disabled = (this.currentQuestionIndex === 0);
    if (this.currentQuestionIndex === total - 1) {
      if (nextBtn) nextBtn.classList.add('hidden');
      if (submitBtn) submitBtn.classList.remove('hidden');
    } else {
      if (nextBtn) nextBtn.classList.remove('hidden');
      if (submitBtn) submitBtn.classList.add('hidden');
    }

    this.renderQuestionNavPills();
  },

  renderQuestionNavPills() {
    const container = document.getElementById('quiz-nav-pills');
    if (!container || !this.currentQuiz) return;

    container.innerHTML = this.currentQuiz.questions.map((q, idx) => {
      const isAnswered = Boolean(this.userAnswers[q.id]);
      const isCurrent = idx === this.currentQuestionIndex;
      return `
        <button class="w-8 h-8 rounded-lg text-xs font-bold transition-all
                ${isCurrent ? 'ring-2 ring-indigo-400 bg-indigo-600 text-white' : 
                  isAnswered ? 'bg-indigo-950 border border-indigo-500/50 text-indigo-300' : 'bg-slate-800 border border-slate-700 text-slate-400'}"
                onclick="QuizModule.jumpToQuestion(${idx})">
          ${idx + 1}
        </button>
      `;
    }).join('');
  },

  selectOption(questionId, optionText) {
    this.userAnswers[questionId] = optionText;
    this.renderCurrentQuestion();
  },

  jumpToQuestion(idx) {
    this.currentQuestionIndex = idx;
    this.renderCurrentQuestion();
  },

  nextQuestion() {
    if (this.currentQuestionIndex < this.currentQuiz.questions.length - 1) {
      this.currentQuestionIndex++;
      this.renderCurrentQuestion();
    }
  },

  prevQuestion() {
    if (this.currentQuestionIndex > 0) {
      this.currentQuestionIndex--;
      this.renderCurrentQuestion();
    }
  },

  async submitQuiz() {
    clearInterval(this.timerInterval);
    const answersPayload = Object.entries(this.userAnswers).map(([qid, ans]) => ({
      question_id: parseInt(qid) || qid,
      selected_option: ans
    }));

    const submitBtn = document.getElementById('quiz-submit-btn');
    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.innerHTML = '<span class="inline-block animate-spin mr-2">↻</span> Grading...';
    }

    try {
      const res = await API.submitQuiz(this.currentQuiz.id, answersPayload);
      this.quizResult = res;
      this.renderResults(res);
    } catch (err) {
      App.showToast(err.message || 'Failed to submit quiz', 'error');
    } finally {
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Submit Assessment';
      }
    }
  },

  renderResults(result) {
    document.getElementById('quiz-active-state').classList.add('hidden');
    const resView = document.getElementById('quiz-results-state');
    resView.classList.remove('hidden');

    const scorePct = result.score;
    document.getElementById('quiz-score-pct').textContent = `${scorePct}%`;
    document.getElementById('quiz-score-fraction').textContent = `${result.correct_count} of ${result.total_questions} correct`;

    const badge = document.getElementById('quiz-result-badge');
    if (scorePct >= 80) {
      badge.textContent = '🎉 Outstanding Mastery!';
      badge.className = 'px-3 py-1 rounded-full text-xs font-semibold bg-emerald-950 border border-emerald-500 text-emerald-300';
      // Trigger Confetti!
      if (typeof confetti === 'function') {
        confetti({ particleCount: 100, spread: 70, origin: { y: 0.6 } });
      }
    } else if (scorePct >= 60) {
      badge.textContent = '👍 Good Effort - Review Key Concepts';
      badge.className = 'px-3 py-1 rounded-full text-xs font-semibold bg-amber-950 border border-amber-500 text-amber-300';
    } else {
      badge.textContent = '📚 Needs Targeted Reinforcement';
      badge.className = 'px-3 py-1 rounded-full text-xs font-semibold bg-rose-950 border border-rose-500 text-rose-300';
    }

    // Render detailed explanation cards
    const reviewContainer = document.getElementById('quiz-review-cards');
    reviewContainer.innerHTML = result.graded_questions.map((q, idx) => `
      <div class="p-5 rounded-xl border ${q.is_correct ? 'bg-emerald-950/20 border-emerald-800/40' : 'bg-rose-950/20 border-rose-800/40'}">
        <div class="flex items-start justify-between gap-3 mb-2">
          <span class="text-xs font-bold ${q.is_correct ? 'text-emerald-400' : 'text-rose-400'} flex items-center gap-1.5">
            <i data-lucide="${q.is_correct ? 'check-circle' : 'x-circle'}" class="w-4 h-4"></i>
            Question ${idx + 1} • ${q.is_correct ? 'Correct' : 'Incorrect'}
          </span>
        </div>
        <p class="text-sm font-semibold text-slate-200 mb-3">${q.question}</p>
        
        <div class="space-y-1.5 text-xs mb-3 font-mono">
          <div class="p-2 rounded bg-slate-900/60 border border-slate-800 text-slate-300">
            <span class="text-slate-500">Your Answer:</span> 
            <span class="${q.is_correct ? 'text-emerald-400 font-bold' : 'text-rose-400 font-bold'}">
              ${q.user_choice || '(Unanswered)'}
            </span>
          </div>
          ${!q.is_correct ? `
            <div class="p-2 rounded bg-emerald-950/40 border border-emerald-800/50 text-emerald-300">
              <span class="text-emerald-500">Correct Answer:</span> <span class="font-bold">${q.correct_choice}</span>
            </div>
          ` : ''}
        </div>

        <div class="text-xs text-slate-300 bg-slate-900/70 p-3 rounded-lg border border-slate-800/80 leading-relaxed">
          <span class="font-bold text-indigo-300 block mb-1">💡 Pedagogical Explanation:</span>
          ${q.explanation}
        </div>
      </div>
    `).join('');

    lucide.createIcons();
  },

  retakeCurrentQuiz() {
    if (this.currentQuiz) {
      this.loadQuiz(this.currentQuiz);
    }
  }
};
