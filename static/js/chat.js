// AI Study Tutor Chat Controller
const ChatModule = {
  activePersona: 'academic',
  isThinking: false,

  init() {
    this.bindEvents();
    this.renderPromptSuggestions();
  },

  bindEvents() {
    const input = document.getElementById('chat-input');
    const sendBtn = document.getElementById('chat-send-btn');
    const personaBtns = document.querySelectorAll('.persona-btn');
    const clearBtn = document.getElementById('chat-clear-btn');

    if (sendBtn) {
      sendBtn.addEventListener('click', () => this.sendMessage());
    }

    if (input) {
      input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
          e.preventDefault();
          this.sendMessage();
        }
      });
    }

    personaBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        personaBtns.forEach(b => b.classList.remove('bg-indigo-600', 'text-white', 'border-indigo-500'));
        btn.classList.add('bg-indigo-600', 'text-white', 'border-indigo-500');
        this.activePersona = btn.dataset.persona;
        App.showToast(`Switched tutor persona to: ${btn.textContent.trim()}`, 'info');
      });
    });

    if (clearBtn) {
      clearBtn.addEventListener('click', async () => {
        if (confirm('Clear chat history for this study material?')) {
          await API.clearChatHistory(App.activeDocumentId);
          this.loadHistory();
          App.showToast('Chat history cleared', 'success');
        }
      });
    }
  },

  promptSuggestions: [
    { label: "💡 Explain Core Idea", prompt: "Explain the central concept and main mechanism introduced in this material in simple terms." },
    { label: "🎯 Common Exam Traps", prompt: "What are the most common exam mistakes, tricky edge cases, and exam questions on this topic?" },
    { label: "🍎 Real-World Analogy", prompt: "Can you provide a vivid, memorable real-world analogy to help me conceptualize this process?" },
    { label: "❓ Challenge Question", prompt: "Ask me a challenging diagnostic question about this text to test my active recall." }
  ],

  renderPromptSuggestions() {
    const container = document.getElementById('chat-suggestions');
    if (!container) return;
    container.innerHTML = this.promptSuggestions.map(s => `
      <button class="suggestion-chip px-3 py-1.5 rounded-full text-xs font-medium bg-slate-800 hover:bg-indigo-900/60 text-slate-300 hover:text-indigo-200 border border-slate-700 hover:border-indigo-500/50 transition-all cursor-pointer whitespace-nowrap"
              onclick="ChatModule.usePrompt('${s.prompt.replace(/'/g, "\\'")}')">
        ${s.label}
      </button>
    `).join('');
  },

  usePrompt(promptText) {
    const input = document.getElementById('chat-input');
    if (input) {
      input.value = promptText;
      input.focus();
    }
  },

  async loadHistory() {
    const chatContainer = document.getElementById('chat-messages');
    if (!chatContainer) return;

    chatContainer.innerHTML = '<div class="flex justify-center p-8"><div class="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500"></div></div>';

    try {
      const messages = await API.getChatHistory(App.activeDocumentId);
      chatContainer.innerHTML = '';

      if (!messages || messages.length === 0) {
        this.renderWelcomeMessage();
        return;
      }

      messages.forEach(msg => this.appendMessageUI(msg.role, msg.content, msg.citations, msg.persona));
      this.scrollToBottom();
    } catch (err) {
      chatContainer.innerHTML = '<div class="text-rose-400 p-4 text-center">Failed to load conversation history.</div>';
    }
  },

  renderWelcomeMessage() {
    const chatContainer = document.getElementById('chat-messages');
    if (!chatContainer) return;

    chatContainer.innerHTML = `
      <div class="p-6 rounded-2xl bg-slate-800/60 border border-slate-700/60 text-center my-6 max-w-xl mx-auto animate-fade-in">
        <div class="w-14 h-14 rounded-2xl bg-gradient-to-tr from-indigo-600 to-violet-500 flex items-center justify-center mx-auto mb-4 shadow-lg shadow-indigo-500/20">
          <i data-lucide="bot" class="w-8 h-8 text-white"></i>
        </div>
        <h3 class="text-lg font-bold text-white mb-2">Welcome to your AI Study Tutor!</h3>
        <p class="text-sm text-slate-300 leading-relaxed mb-4">
          I am grounded directly in your uploaded study material. Ask me to break down difficult concepts, provide Socratic hints, clarify equations, or grill you for upcoming exams!
        </p>
        <div class="text-xs text-indigo-400 bg-indigo-950/40 border border-indigo-800/40 rounded-lg p-2.5">
          ✨ Tip: Switch personas above (Academic, Socratic, ELI5, or Exam Coach) to tailor my teaching style to your study goals!
        </div>
      </div>
    `;
    lucide.createIcons();
  },

  async sendMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    if (!message || this.isThinking) return;

    input.value = '';
    this.appendMessageUI('user', message);
    this.scrollToBottom();

    this.showThinkingIndicator();

    try {
      const result = await API.sendChatMessage(message, App.activeDocumentId, this.activePersona);
      this.removeThinkingIndicator();
      this.appendMessageUI('assistant', result.reply, result.citations, this.activePersona, result.provider);
      this.scrollToBottom();
    } catch (error) {
      this.removeThinkingIndicator();
      this.appendMessageUI('assistant', `⚠️ Sorry, an error occurred: ${error.message}. Please verify your settings or try again.`, []);
      this.scrollToBottom();
    }
  },

  appendMessageUI(role, content, citations = [], persona = 'academic', provider = 'AI Tutor') {
    const chatContainer = document.getElementById('chat-messages');
    if (!chatContainer) return;

    // Remove welcome message if present
    const welcome = chatContainer.querySelector('.animate-fade-in');
    if (welcome && chatContainer.children.length === 1) {
      chatContainer.innerHTML = '';
    }

    const isUser = role === 'user';
    const messageEl = document.createElement('div');
    messageEl.className = `flex gap-3 mb-6 animate-fade-in ${isUser ? 'justify-end' : 'justify-start'}`;

    let parsedHtml = content;
    if (!isUser && typeof marked !== 'undefined') {
      try {
        parsedHtml = marked.parse(content);
      } catch (e) {
        parsedHtml = content;
      }
    } else {
      parsedHtml = `<p class="whitespace-pre-wrap">${content}</p>`;
    }

    let citationsHtml = '';
    if (citations && citations.length > 0) {
      citationsHtml = `
        <div class="mt-4 pt-3 border-t border-slate-700/60">
          <div class="text-xs font-semibold text-slate-400 mb-2 flex items-center gap-1.5">
            <i data-lucide="bookmark" class="w-3.5 h-3.5 text-indigo-400"></i>
            Source Citations (${citations.length})
          </div>
          <div class="flex flex-wrap gap-2">
            ${citations.map(c => `
              <div class="group relative inline-block">
                <span class="inline-flex items-center gap-1 text-xs px-2.5 py-1 rounded-md bg-indigo-950/70 border border-indigo-700/50 text-indigo-300 font-mono cursor-help hover:bg-indigo-900/80 transition-colors">
                  <i data-lucide="file-text" class="w-3 h-3"></i>
                  Page ${c.page}
                </span>
                <div class="hidden group-hover:block absolute bottom-full mb-2 left-0 w-64 p-2.5 bg-slate-900 border border-slate-700 text-slate-300 text-xs rounded-lg shadow-xl z-50 pointer-events-none">
                  <div class="font-bold text-indigo-300 mb-1">Page ${c.page} Excerpt:</div>
                  "${c.snippet}"
                </div>
              </div>
            `).join('')}
          </div>
        </div>
      `;
    }

    if (isUser) {
      messageEl.innerHTML = `
        <div class="max-w-2xl bg-indigo-600 text-white rounded-2xl rounded-tr-sm px-5 py-3.5 shadow-md">
          <div class="text-sm">${parsedHtml}</div>
        </div>
        <div class="w-9 h-9 rounded-xl bg-indigo-500/20 border border-indigo-500/40 flex items-center justify-center text-indigo-300 flex-shrink-0">
          <i data-lucide="user" class="w-5 h-5"></i>
        </div>
      `;
    } else {
      messageEl.innerHTML = `
        <div class="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 to-violet-600 flex items-center justify-center text-white flex-shrink-0 shadow-md shadow-indigo-600/30">
          <i data-lucide="sparkles" class="w-5 h-5"></i>
        </div>
        <div class="max-w-3xl flex-1 bg-slate-800/90 border border-slate-700/70 rounded-2xl rounded-tl-sm px-6 py-4 shadow-md text-slate-200">
          <div class="flex items-center justify-between gap-2 mb-2 pb-2 border-b border-slate-700/50 text-xs">
            <span class="font-bold text-indigo-300 flex items-center gap-1.5">
              <span>AI Study Buddy</span>
              <span class="text-[10px] uppercase tracking-wider px-2 py-0.5 rounded-full bg-slate-700 text-slate-300 font-normal">
                ${persona}
              </span>
            </span>
            <span class="text-[11px] text-slate-400 font-mono flex items-center gap-1">
              <span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
              ${provider}
            </span>
          </div>
          <div class="prose prose-invert prose-sm max-w-none prose-headings:text-slate-100 prose-p:leading-relaxed prose-pre:bg-slate-900 prose-pre:border prose-pre:border-slate-700/80">
            ${parsedHtml}
          </div>
          ${citationsHtml}
        </div>
      `;
    }

    chatContainer.appendChild(messageEl);
    lucide.createIcons();

    // Trigger KaTeX rendering if available
    if (typeof renderMathInElement !== 'undefined') {
      try {
        renderMathInElement(messageEl, {
          delimiters: [
            { left: '$$', right: '$$', display: true },
            { left: '$', right: '$', display: false }
          ]
        });
      } catch (e) {}
    }
  },

  showThinkingIndicator() {
    this.isThinking = true;
    const chatContainer = document.getElementById('chat-messages');
    if (!chatContainer) return;

    const thinkingEl = document.createElement('div');
    thinkingEl.id = 'thinking-indicator';
    thinkingEl.className = 'flex gap-3 mb-6 animate-fade-in items-center';
    thinkingEl.innerHTML = `
      <div class="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 to-violet-600 flex items-center justify-center text-white flex-shrink-0 shadow-md">
        <i data-lucide="sparkles" class="w-5 h-5 animate-pulse"></i>
      </div>
      <div class="bg-slate-800/80 border border-slate-700/60 rounded-2xl rounded-tl-sm px-5 py-3 text-slate-400 text-xs flex items-center gap-2">
        <span>AI Tutor is formulating your response...</span>
        <div class="flex gap-1">
          <span class="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce" style="animation-delay: 0ms"></span>
          <span class="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce" style="animation-delay: 150ms"></span>
          <span class="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce" style="animation-delay: 300ms"></span>
        </div>
      </div>
    `;
    chatContainer.appendChild(thinkingEl);
    lucide.createIcons();
    this.scrollToBottom();
  },

  removeThinkingIndicator() {
    this.isThinking = false;
    const el = document.getElementById('thinking-indicator');
    if (el) el.remove();
  },

  scrollToBottom() {
    const chatContainer = document.getElementById('chat-messages');
    if (chatContainer) {
      chatContainer.scrollTop = chatContainer.scrollHeight;
    }
  }
};

