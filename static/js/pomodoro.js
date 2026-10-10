// Pomodoro Focus Timer with Web Audio Synthesizer
const PomodoroModule = {
  modes: {
    focus: 25 * 60,
    shortBreak: 5 * 60,
    longBreak: 15 * 60
  },
  currentMode: 'focus',
  timeLeft: 25 * 60,
  isRunning: false,
  timerInterval: null,
  
  // Web Audio Context & Generators
  audioCtx: null,
  noiseNode: null,
  gainNode: null,
  activeAmbient: 'none',

  init() {
    this.bindEvents();
    this.updateDisplay();
  },

  bindEvents() {
    const playBtn = document.getElementById('pomo-play-btn');
    const resetBtn = document.getElementById('pomo-reset-btn');
    const skipBtn = document.getElementById('pomo-skip-btn');
    const modeTabs = document.querySelectorAll('.pomo-mode-tab');
    const ambientSelect = document.getElementById('pomo-ambient-select');

    if (playBtn) playBtn.addEventListener('click', () => this.toggleTimer());
    if (resetBtn) resetBtn.addEventListener('click', () => this.resetTimer());
    if (skipBtn) skipBtn.addEventListener('click', () => this.skipMode());

    modeTabs.forEach(tab => {
      tab.addEventListener('click', () => {
        modeTabs.forEach(t => t.classList.remove('bg-indigo-600', 'text-white'));
        tab.classList.add('bg-indigo-600', 'text-white');
        this.switchMode(tab.dataset.mode);
      });
    });

    if (ambientSelect) {
      ambientSelect.addEventListener('change', (e) => {
        this.setAmbientSound(e.target.value);
      });
    }
  },

  switchMode(mode) {
    this.pauseTimer();
    this.currentMode = mode;
    this.timeLeft = this.modes[mode] || 25 * 60;
    this.updateDisplay();
  },

  toggleTimer() {
    if (this.isRunning) {
      this.pauseTimer();
    } else {
      this.startTimer();
    }
  },

  startTimer() {
    this.isRunning = true;
    const playBtn = document.getElementById('pomo-play-btn');
    if (playBtn) {
      playBtn.innerHTML = '<i data-lucide="pause" class="w-6 h-6"></i>';
      lucide.createIcons();
    }

    if (this.activeAmbient !== 'none') {
      this.playAmbientAudio();
    }

    this.timerInterval = setInterval(() => {
      if (this.timeLeft > 0) {
        this.timeLeft--;
        this.updateDisplay();
      } else {
        this.onTimerComplete();
      }
    }, 1000);
  },

  pauseTimer() {
    this.isRunning = false;
    clearInterval(this.timerInterval);
    const playBtn = document.getElementById('pomo-play-btn');
    if (playBtn) {
      playBtn.innerHTML = '<i data-lucide="play" class="w-6 h-6"></i>';
      lucide.createIcons();
    }
    this.stopAmbientAudio();
  },

  resetTimer() {
    this.pauseTimer();
    this.timeLeft = this.modes[this.currentMode];
    this.updateDisplay();
  },

  skipMode() {
    if (this.currentMode === 'focus') {
      this.switchMode('shortBreak');
    } else {
      this.switchMode('focus');
    }
  },

  async onTimerComplete() {
    this.pauseTimer();
    this.playChime();

    if (this.currentMode === 'focus') {
      App.showToast('🎉 Focus session completed! Great work!', 'success');
      // Log session
      try {
        await API.logStudySession('pomodoro', this.modes.focus, 'Pomodoro 25-minute focus cycle');
      } catch (e) {}
      this.switchMode('shortBreak');
    } else {
      App.showToast('Break is over! Time to focus! 🚀', 'info');
      this.switchMode('focus');
    }
  },

  updateDisplay() {
    const mins = Math.floor(this.timeLeft / 60).toString().padStart(2, '0');
    const secs = (this.timeLeft % 60).toString().padStart(2, '0');
    const text = `${mins}:${secs}`;

    const timeEl = document.getElementById('pomo-time-display');
    const circle = document.getElementById('pomo-circle-progress');
    const headerPill = document.getElementById('header-pomo-pill');

    if (timeEl) timeEl.textContent = text;
    if (headerPill) headerPill.textContent = text;

    if (circle) {
      const total = this.modes[this.currentMode];
      const fraction = this.timeLeft / total;
      const circumference = 2 * Math.PI * 120;
      circle.style.strokeDashoffset = circumference * (1 - fraction);
    }
  },

  // Audio Synthesizer via Web Audio API
  initAudio() {
    if (!this.audioCtx) {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      this.audioCtx = new AudioCtx();
    }
    if (this.audioCtx.state === 'suspended') {
      this.audioCtx.resume();
    }
  },

  setAmbientSound(type) {
    this.activeAmbient = type;
    if (this.isRunning) {
      this.stopAmbientAudio();
      if (type !== 'none') {
        this.playAmbientAudio();
      }
    }
  },

  playAmbientAudio() {
    this.initAudio();
    this.stopAmbientAudio();

    if (this.activeAmbient === 'rain' || this.activeAmbient === 'whitenoise') {
      // Generate Pink/Brown Noise buffer
      const bufferSize = this.audioCtx.sampleRate * 2;
      const noiseBuffer = this.audioCtx.createBuffer(1, bufferSize, this.audioCtx.sampleRate);
      const output = noiseBuffer.getChannelData(0);
      let b0 = 0, b1 = 0, b2 = 0;
      for (let i = 0; i < bufferSize; i++) {
        const white = Math.random() * 2 - 1;
        b0 = 0.99886 * b0 + white * 0.0555179;
        b1 = 0.99332 * b1 + white * 0.0750759;
        b2 = 0.96900 * b2 + white * 0.1538520;
        output[i] = (b0 + b1 + b2 + white * 0.5362) * 0.04;
      }

      const whiteNoise = this.audioCtx.createBufferSource();
      whiteNoise.buffer = noiseBuffer;
      whiteNoise.loop = true;

      // Filter for rainfall feel
      const filter = this.audioCtx.createBiquadFilter();
      filter.type = 'lowpass';
      filter.frequency.value = (this.activeAmbient === 'rain') ? 800 : 1500;

      this.gainNode = this.audioCtx.createGain();
      this.gainNode.gain.value = 0.3;

      whiteNoise.connect(filter);
      filter.connect(this.gainNode);
      this.gainNode.connect(this.audioCtx.destination);
      whiteNoise.start();
      this.noiseNode = whiteNoise;

    } else if (this.activeAmbient === 'binaural') {
      // 432Hz Calm Harmonic Sine Waves
      const osc1 = this.audioCtx.createOscillator();
      const osc2 = this.audioCtx.createOscillator();
      osc1.type = 'sine';
      osc2.type = 'sine';
      osc1.frequency.value = 216; // A3 harmonic
      osc2.frequency.value = 226; // 10Hz Alpha difference

      this.gainNode = this.audioCtx.createGain();
      this.gainNode.gain.value = 0.08;

      osc1.connect(this.gainNode);
      osc2.connect(this.gainNode);
      this.gainNode.connect(this.audioCtx.destination);
      osc1.start();
      osc2.start();
      this.noiseNode = { stop: () => { osc1.stop(); osc2.stop(); } };
    }
  },

  stopAmbientAudio() {
    if (this.noiseNode) {
      try { this.noiseNode.stop(); } catch (e) {}
      this.noiseNode = null;
    }
  },

  playChime() {
    this.initAudio();
    const osc = this.audioCtx.createOscillator();
    const gain = this.audioCtx.createGain();
    osc.type = 'triangle';
    osc.frequency.setValueAtTime(587.33, this.audioCtx.currentTime); // D5
    osc.frequency.exponentialRampToValueAtTime(880, this.audioCtx.currentTime + 0.3); // A5

    gain.gain.setValueAtTime(0.5, this.audioCtx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, this.audioCtx.currentTime + 1.2);

    osc.connect(gain);
    gain.connect(this.audioCtx.destination);
    osc.start();
    osc.stop(this.audioCtx.currentTime + 1.2);
  }
};

