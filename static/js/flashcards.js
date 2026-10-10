// Smart Flashcards & Leitner Spaced Repetition Controller
const FlashcardsModule = {
  cards: [],
  currentIndex: 0,
  isFlipped: false,
  activeDeck: 'all',

  init() {
    this.bindEvents();
    this.setupKeyboardShortcuts();
  },

  bindEvents() {
    const cardContainer = document.getElementById('flashcard-card');
    const flipBtn = document.getElementById('fc-flip-btn');
    const prevBtn = document.getElementById('fc-prev-btn');
    const nextBtn = document.getElementById('fc-next-btn');
    const speakBtn = document.getElementById('fc-speak-btn');
    const generateBtn = document.getElementById('fc-generate-btn');
    const deckSelect = document.getElementById('fc-deck-select');

    if (cardContainer) {
      cardContainer.addEventListener('click', () => this.toggleFlip());
    }
    if (flipBtn) {
      flipBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        this.toggleFlip();
      });
    }
    if (prevBtn) {
      prevBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        this.prevCard();
      });
    }
    if (nextBtn) {
      nextBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        this.nextCard();
      });
    }
    if (speakBtn) {
      speakBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        this.speakCurrentCard();
      });
    }
    if (generateBtn) {
      generateBtn.addEventListener('click', () => this.showGenerateModal());
    }
    if (deckSelect) {
      deckSelect.addEventListener('change', (e) => {
        this.activeDeck = e.target.value;
        this.loadCards();
      });
    }

    // Rating buttons
    document.querySelectorAll('.fc-rate-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const rating = btn.dataset.rating;
        this.rateCurrentCard(rating);
      });
    });
  },

  setupKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
      // Only when flashcards view is active and not typing in an input
      const view = document.getElementById('view-flashcards');
      if (!view || view.classList.contains('hidden')) return;
      if (['INPUT', 'TEXTAREA'].includes(document.activeElement.tagName)) return;

      if (e.code === 'Space') {
        e.preventDefault();
        this.toggleFlip();
      } else if (e.code === 'ArrowRight') {
        e.preventDefault();
        this.nextCard();
      } else if (e.code === 'ArrowLeft') {
        e.preventDefault();
        this.prevCard();
      } else if (e.key === '1') {
        this.rateCurrentCard('hard');
      } else if (e.key === '2') {
        this.rateCurrentCard('good');
      } else if (e.key === '3') {
        this.rateCurrentCard('easy');
      }
    });
  },

  async loadCards() {
    try {
      this.cards = await API.getFlashcards(this.activeDeck === 'all' ? null : this.activeDeck, App.activeDocumentId);
      this.currentIndex = 0;
      this.isFlipped = false;
      this.updateDeckDropdown();
      this.renderCurrentCard();
    } catch (err) {
      App.showToast('Failed to load flashcards', 'error');
    }
  },

  updateDeckDropdown() {
    const select = document.getElementById('fc-deck-select');
    if (!select) return;
    const decks = Array.from(new Set(this.cards.map(c => c.deck_title).filter(Boolean)));
    
    let html = '<option value="all">📚 All Decks</option>';
    decks.forEach(d => {
      html += `<option value="${d}" ${this.activeDeck === d ? 'selected' : ''}>${d}</option>`;
    });
    select.innerHTML = html;
  },

  renderCurrentCard() {
    const cardEl = document.getElementById('flashcard-card');
    const emptyState = document.getElementById('fc-empty-state');
    const controls = document.getElementById('fc-controls');
    const counter = document.getElementById('fc-counter');
    const progressBar = document.getElementById('fc-progress');
    const frontText = document.getElementById('fc-front-text');
    const backText = document.getElementById('fc-back-text');
    const boxBadge = document.getElementById('fc-box-badge');
    const diffBadge = document.getElementById('fc-diff-badge');

    if (!this.cards || this.cards.length === 0) {
      if (cardEl) cardEl.classList.add('hidden');
      if (controls) controls.classList.add('hidden');
      if (emptyState) emptyState.classList.remove('hidden');
      if (counter) counter.textContent = '0 / 0';
      return;
    }

    if (emptyState) emptyState.classList.add('hidden');
    if (cardEl) cardEl.classList.remove('hidden');
    if (controls) controls.classList.remove('hidden');

    const card = this.cards[this.currentIndex];
    this.isFlipped = false;
    const inner = document.getElementById('flashcard-inner');
    if (inner) inner.classList.remove('is-flipped');

    if (frontText) frontText.textContent = card.front;
    if (backText) backText.textContent = card.back;
    if (counter) counter.textContent = `${this.currentIndex + 1} / ${this.cards.length}`;

    if (progressBar) {
      const pct = ((this.currentIndex + 1) / this.cards.length) * 100;
      progressBar.style.width = `${pct}%`;
    }

    if (boxBadge) {
      const box = card.box || 1;
      const boxColors = ['bg-rose-900/60 text-rose-300 border-rose-700', 'bg-amber-900/60 text-amber-300 border-amber-700', 'bg-sky-900/60 text-sky-300 border-sky-700', 'bg-emerald-900/60 text-emerald-300 border-emerald-700', 'bg-purple-900/60 text-purple-300 border-purple-700'];
      boxBadge.className = `px-2.5 py-0.5 rounded-full text-xs font-semibold border ${boxColors[Math.min(box - 1, 4)]}`;
      boxBadge.textContent = `Leitner Box ${box} (Tier ${box}/5)`;
    }

    if (diffBadge) {
      diffBadge.textContent = (card.difficulty || 'medium').toUpperCase();
    }

    lucide.createIcons();
  },

  toggleFlip() {
    if (!this.cards.length) return;
    this.isFlipped = !this.isFlipped;
    const inner = document.getElementById('flashcard-inner');
    if (inner) {
      if (this.isFlipped) {
        inner.classList.add('is-flipped');
      } else {
        inner.classList.remove('is-flipped');
      }
    }
  },

  nextCard() {
    if (!this.cards.length) return;
    this.currentIndex = (this.currentIndex + 1) % this.cards.length;
    this.renderCurrentCard();
  },

  prevCard() {
    if (!this.cards.length) return;
    this.currentIndex = (this.currentIndex - 1 + this.cards.length) % this.cards.length;
    this.renderCurrentCard();
  },

  async rateCurrentCard(rating) {
    if (!this.cards.length) return;
    const card = this.cards[this.currentIndex];

    try {
      await API.reviewFlashcard(card.id, rating);
      
      // Local optimistic update
      if (rating === 'easy') {
        card.box = Math.min(5, (card.box || 1) + 1);
        App.showToast('Promoted to next Leitner Box! 🚀', 'success');
      } else if (rating === 'good') {
        card.box = Math.min(5, Math.max(2, card.box || 1));
        App.showToast('Reinforced memory! 👍', 'info');
      } else {
        card.box = 1;
        App.showToast('Reset to Box 1 for review 🔁', 'warning');
      }

      // Automatically advance to next card after short delay
      setTimeout(() => {
        this.nextCard();
      }, 300);
    } catch (err) {
      App.showToast('Failed to record card review', 'error');
    }
  },

  speakCurrentCard() {
    if (!this.cards.length || !('speechSynthesis' in window)) {
      App.showToast('Speech synthesis not supported on this browser', 'info');
      return;
    }
    const card = this.cards[this.currentIndex];
    const textToSpeak = this.isFlipped ? card.back : card.front;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(textToSpeak);
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    window.speechSynthesis.speak(utterance);
    App.showToast('🔊 Audio playing...', 'info');
  },

  showGenerateModal() {
    const modal = document.getElementById('generate-cards-modal');
    if (modal) modal.classList.remove('hidden');
  },

  hideGenerateModal() {
    const modal = document.getElementById('generate-cards-modal');
    if (modal) modal.classList.add('hidden');
  },

  async submitGenerate(count) {
    const btn = document.getElementById('fc-submit-generate-btn');
    if (btn) {
      btn.disabled = true;
      btn.innerHTML = '<span class="inline-block animate-spin mr-2">↻</span> Generating high-yield cards...';
    }

    try {
      const res = await API.generateFlashcards(App.activeDocumentId, null, count);
      App.showToast(`Generated ${res.count} flashcards successfully! 🎉`, 'success');
      this.hideGenerateModal();
      await this.loadCards();
    } catch (err) {
      App.showToast(err.message || 'Generation failed', 'error');
    } finally {
      if (btn) {
        btn.disabled = false;
        btn.textContent = 'Generate Deck';
      }
    }
  }
};

