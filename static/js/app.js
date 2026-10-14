// Master Application Controller
const App = {
  activeDocumentId: null,
  activeDocument: null,
  documents: [],
  currentTab: 'chat',

  async init() {
    this.bindGlobalEvents();
    ChatModule.init();
    FlashcardsModule.init();
    QuizModule.init();
    SummaryModule.init();
    PomodoroModule.init();
    AnalyticsModule.init();

    await this.loadSettingsInfo();
    await this.loadDocuments();
    this.switchTab('chat');
  },

  bindGlobalEvents() {
    // Tab Navigation
    document.querySelectorAll('.nav-tab-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const tab = btn.dataset.tab;
        this.switchTab(tab);
      });
    });

    // Document Selector in Header
    const docSelect = document.getElementById('header-doc-select');
    if (docSelect) {
      docSelect.addEventListener('change', (e) => {
        this.setActiveDocument(e.target.value);
      });
    }

    // Upload Modal Triggers
    const openUploadBtn = document.getElementById('open-upload-modal-btn');
    const closeUploadBtn = document.getElementById('close-upload-modal-btn');
    const uploadModal = document.getElementById('upload-modal');
    const dropZone = document.getElementById('file-drop-zone');
    const fileInput = document.getElementById('file-upload-input');
    const loadSamplesBtn = document.getElementById('load-samples-btn');
    const openTextModalBtn = document.getElementById('open-text-modal-btn');

    if (openUploadBtn) {
      openUploadBtn.addEventListener('click', () => uploadModal.classList.remove('hidden'));
    }
    if (closeUploadBtn) {
      closeUploadBtn.addEventListener('click', () => uploadModal.classList.add('hidden'));
    }

    if (fileInput) {
      fileInput.addEventListener('change', (e) => {
        if (e.target.files.length) this.handleFileUpload(e.target.files[0]);
      });
    }

    if (dropZone) {
      dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('border-indigo-500', 'bg-indigo-950/20');
      });
      dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('border-indigo-500', 'bg-indigo-950/20');
      });
      dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('border-indigo-500', 'bg-indigo-950/20');
        if (e.dataTransfer.files.length) this.handleFileUpload(e.dataTransfer.files[0]);
      });
    }

    if (loadSamplesBtn) {
      loadSamplesBtn.addEventListener('click', async () => {
        loadSamplesBtn.disabled = true;
        loadSamplesBtn.innerHTML = '<span class="inline-block animate-spin mr-1">↻</span> Loading...';
        try {
          const res = await API.loadSampleDocuments();
          this.showToast(`Loaded sample materials! 📚`, 'success');
          await this.loadDocuments();
        } catch (err) {
          this.showToast('Failed to load sample materials', 'error');
        } finally {
          loadSamplesBtn.disabled = false;
          loadSamplesBtn.innerHTML = '<i data-lucide="sparkles" class="w-4 h-4 mr-1"></i> Load Sample Notes';
          lucide.createIcons();
        }
      });
    }

    // Text Notes Upload Modal
    if (openTextModalBtn) {
      openTextModalBtn.addEventListener('click', () => {
        const m = document.getElementById('text-upload-modal');
        if (m) m.classList.remove('hidden');
      });
    }

    const saveTextBtn = document.getElementById('save-text-doc-btn');
    if (saveTextBtn) {
      saveTextBtn.addEventListener('click', async () => {
        const title = document.getElementById('text-doc-title').value.trim();
        const content = document.getElementById('text-doc-content').value.trim();
        if (!title || !content) {
          this.showToast('Please provide both title and content', 'warning');
          return;
        }

        saveTextBtn.disabled = true;
        saveTextBtn.textContent = 'Saving...';
        try {
          const res = await API.uploadText(title, content);
          this.showToast('Study notes created successfully!', 'success');
          document.getElementById('text-upload-modal').classList.add('hidden');
          document.getElementById('text-doc-title').value = '';
          document.getElementById('text-doc-content').value = '';
          await this.loadDocuments();
          this.setActiveDocument(res.document.id);
        } catch (err) {
          this.showToast(err.message || 'Failed to save notes', 'error');
        } finally {
          saveTextBtn.disabled = false;
          saveTextBtn.textContent = 'Save Notes';
        }
      });
    }

    // Settings save & verify buttons
    this.bindSettingsEvents();
  },

  bindSettingsEvents() {
    const saveBtn = document.getElementById('settings-save-btn');
    const verifyGeminiBtn = document.getElementById('verify-gemini-btn');
    const verifyOpenAIBtn = document.getElementById('verify-openai-btn');

    if (saveBtn) {
      saveBtn.addEventListener('click', async () => {
        const provider = document.querySelector('input[name="ai-provider"]:checked').value;
        const geminiKey = document.getElementById('settings-gemini-key').value.trim();
        const geminiModel = document.getElementById('settings-gemini-model').value;
        const openaiKey = document.getElementById('settings-openai-key').value.trim();
        const openaiModel = document.getElementById('settings-openai-model').value;

        try {
          await API.updateSettings({
            provider: provider,
            gemini_api_key: geminiKey,
            gemini_model: geminiModel,
            openai_api_key: openaiKey,
            openai_model: openaiModel
          });
          this.showToast('Settings saved successfully! ⚙️', 'success');
          await this.loadSettingsInfo();
        } catch (err) {
          this.showToast('Failed to save settings', 'error');
        }
      });
    }

    if (verifyGeminiBtn) {
      verifyGeminiBtn.addEventListener('click', async () => {
        const key = document.getElementById('settings-gemini-key').value.trim();
        const statusEl = document.getElementById('gemini-verify-status');
        statusEl.innerHTML = '<span class="text-indigo-400">Verifying Gemini key...</span>';
        try {
          const res = await API.verifyApiKey('gemini', key);
          if (res.valid) {
            statusEl.innerHTML = `<span class="text-emerald-400">✅ ${res.message}</span>`;
          } else {
            statusEl.innerHTML = `<span class="text-rose-400">❌ ${res.message}</span>`;
          }
        } catch (err) {
          statusEl.innerHTML = `<span class="text-rose-400">❌ Error: ${err.message}</span>`;
        }
      });
    }

    if (verifyOpenAIBtn) {
      verifyOpenAIBtn.addEventListener('click', async () => {
        const key = document.getElementById('settings-openai-key').value.trim();
        const statusEl = document.getElementById('openai-verify-status');
        statusEl.innerHTML = '<span class="text-indigo-400">Verifying OpenAI key...</span>';
        try {
          const res = await API.verifyApiKey('openai', key);
          if (res.valid) {
            statusEl.innerHTML = `<span class="text-emerald-400">✅ ${res.message}</span>`;
          } else {
            statusEl.innerHTML = `<span class="text-rose-400">❌ ${res.message}</span>`;
          }
        } catch (err) {
          statusEl.innerHTML = `<span class="text-rose-400">❌ Error: ${err.message}</span>`;
        }
      });
    }
  },

  async loadSettingsInfo() {
    try {
      const s = await API.getSettings();
      const badge = document.getElementById('header-ai-badge');
      if (badge) {
        if (s.provider === 'gemini') {
          badge.innerHTML = `<span class="w-2 h-2 rounded-full bg-violet-400 animate-pulse"></span> Google Gemini (${s.gemini_model})`;
          badge.className = 'flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-violet-950/60 border border-violet-700/60 text-violet-300';
        } else if (s.provider === 'openai') {
          badge.innerHTML = `<span class="w-2 h-2 rounded-full bg-sky-400 animate-pulse"></span> OpenAI (${s.openai_model})`;
          badge.className = 'flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-sky-950/60 border border-sky-700/60 text-sky-300';
        } else {
          badge.innerHTML = `<span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span> Smart Local Engine (Active)`;
          badge.className = 'flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-950/60 border border-emerald-700/60 text-emerald-300';
        }
      }

      // Populate Settings inputs if on settings view
      const radio = document.querySelector(`input[name="ai-provider"][value="${s.provider}"]`);
      if (radio) radio.checked = true;

      const geminiInput = document.getElementById('settings-gemini-key');
      if (geminiInput && s.gemini_api_key_masked) geminiInput.placeholder = `Configured: ${s.gemini_api_key_masked}`;

      const openaiInput = document.getElementById('settings-openai-key');
      if (openaiInput && s.openai_api_key_masked) openaiInput.placeholder = `Configured: ${s.openai_api_key_masked}`;

    } catch (err) {
      console.warn('Could not load settings:', err);
    }
  },

  async loadDocuments() {
    try {
      this.documents = await API.getDocuments();
      this.renderDocumentSelectors();
      this.renderDocumentsList();

      if (this.documents.length > 0 && !this.activeDocumentId) {
        this.setActiveDocument(this.documents[0].id);
      }
    } catch (err) {
      this.showToast('Failed to load documents list', 'error');
    }
  },

  setActiveDocument(docId) {
    this.activeDocumentId = docId;
    this.activeDocument = this.documents.find(d => d.id === docId) || null;

    // Update Header Selector
    const select = document.getElementById('header-doc-select');
    if (select) select.value = docId;

    // Update active label in chat & summary
    const docLabel = this.activeDocument ? this.activeDocument.filename : 'All Documents';
    document.querySelectorAll('.active-doc-label').forEach(el => el.textContent = docLabel);

    // Refresh active views
    if (this.currentTab === 'chat') {
      ChatModule.loadHistory();
    } else if (this.currentTab === 'flashcards') {
      FlashcardsModule.loadCards();
    } else if (this.currentTab === 'summary') {
      SummaryModule.loadSummary();
    }
  },

  renderDocumentSelectors() {
    const select = document.getElementById('header-doc-select');
    if (!select) return;

    if (this.documents.length === 0) {
      select.innerHTML = '<option value="">No documents loaded</option>';
      return;
    }

    select.innerHTML = this.documents.map(d => `
      <option value="${d.id}" ${this.activeDocumentId === d.id ? 'selected' : ''}>
        📄 ${d.filename} (${d.page_count}p)
      </option>
    `).join('');
  },

  renderDocumentsList() {
    const list = document.getElementById('docs-table-body');
    const empty = document.getElementById('docs-empty-state');
    if (!list) return;

    if (this.documents.length === 0) {
      list.innerHTML = '';
      if (empty) empty.classList.remove('hidden');
      return;
    }

    if (empty) empty.classList.add('hidden');

    list.innerHTML = this.documents.map(d => {
      const isSelected = this.activeDocumentId === d.id;
      const sizeKb = Math.round(d.file_size / 1024);
      return `
        <tr class="border-b border-slate-800 hover:bg-slate-800/40 transition-colors ${isSelected ? 'bg-indigo-950/20' : ''}">
          <td class="py-4 px-4">
            <div class="flex items-center gap-3">
              <div class="w-9 h-9 rounded-lg bg-indigo-950/70 border border-indigo-700/40 flex items-center justify-center text-indigo-400 flex-shrink-0">
                <i data-lucide="${d.file_type === 'pdf' ? 'file-text' : 'file-code'}" class="w-5 h-5"></i>
              </div>
              <div>
                <div class="font-semibold text-sm text-slate-100">${d.filename}</div>
                <div class="text-xs text-slate-400 line-clamp-1 max-w-sm">${d.summary || 'Uploaded study document'}</div>
              </div>
            </div>
          </td>
          <td class="py-4 px-4 text-xs font-mono text-slate-300">
            ${d.page_count} ${d.page_count === 1 ? 'page' : 'pages'}
          </td>
          <td class="py-4 px-4 text-xs font-mono text-slate-300">
            ${(d.word_count || 0).toLocaleString()} words
          </td>
          <td class="py-4 px-4 text-xs text-slate-400 font-mono">
            ${sizeKb > 0 ? sizeKb + ' KB' : '< 1 KB'}
          </td>
          <td class="py-4 px-4 text-right">
            <div class="flex items-center justify-end gap-2">
              <button class="px-3 py-1.5 rounded-lg text-xs font-medium bg-indigo-600/20 text-indigo-300 hover:bg-indigo-600 hover:text-white border border-indigo-500/40 transition-all cursor-pointer"
                      onclick="App.setActiveDocument('${d.id}'); App.switchTab('chat');">
                Study Now
              </button>
              <button class="p-1.5 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-rose-950/40 border border-transparent hover:border-rose-800/50 transition-all cursor-pointer"
                      title="Delete" onclick="App.deleteDoc('${d.id}', '${d.filename}')">
                <i data-lucide="trash-2" class="w-4 h-4"></i>
              </button>
            </div>
          </td>
        </tr>
      `;
    }).join('');

    lucide.createIcons();
  },

  async handleFileUpload(file) {
    const modal = document.getElementById('upload-modal');
    const statusEl = document.getElementById('upload-progress-text');
    if (statusEl) statusEl.textContent = `Processing "${file.name}" with PyPDF text extraction...`;

    try {
      const res = await API.uploadDocument(file);
      this.showToast(`Uploaded "${file.name}" successfully! 📄`, 'success');
      if (modal) modal.classList.add('hidden');
      await this.loadDocuments();
      this.setActiveDocument(res.document.id);
    } catch (err) {
      this.showToast(err.message || 'File upload failed', 'error');
    } finally {
      if (statusEl) statusEl.textContent = '';
      const input = document.getElementById('file-upload-input');
      if (input) input.value = '';
    }
  },

  async deleteDoc(id, filename) {
    if (confirm(`Are you sure you want to delete "${filename}"?`)) {
      try {
        await API.deleteDocument(id);
        this.showToast(`Deleted "${filename}"`, 'info');
        if (this.activeDocumentId === id) this.activeDocumentId = null;
        await this.loadDocuments();
      } catch (err) {
        this.showToast('Failed to delete document', 'error');
      }
    }
  },

  switchTab(tab) {
    this.currentTab = tab;

    // Update active nav styling
    document.querySelectorAll('.nav-tab-btn').forEach(btn => {
      const isSelected = btn.dataset.tab === tab;
      if (isSelected) {
        btn.classList.add('bg-indigo-600', 'text-white', 'shadow-md', 'shadow-indigo-600/30');
        btn.classList.remove('text-slate-400', 'hover:bg-slate-800', 'hover:text-slate-200');
      } else {
        btn.classList.remove('bg-indigo-600', 'text-white', 'shadow-md', 'shadow-indigo-600/30');
        btn.classList.add('text-slate-400', 'hover:bg-slate-800', 'hover:text-slate-200');
      }
    // Update mobile bottom nav items
    document.querySelectorAll('.mobile-nav-btn').forEach(btn => {
      const isSelected = btn.dataset.tab === tab;
      if (isSelected) {
        btn.classList.add('text-indigo-400');
        btn.classList.remove('text-slate-400');
      } else {
        btn.classList.remove('text-indigo-400');
        btn.classList.add('text-slate-400');
      }
    });

    // Toggle view containers
    document.querySelectorAll('.tab-view').forEach(view => {
      view.classList.add('hidden');
    });

    const activeView = document.getElementById(`view-${tab}`);
    if (activeView) activeView.classList.remove('hidden');

    // Close mobile drawer on switch
    this.toggleMobileSidebar(true);

    // Trigger tab specific loads
    if (tab === 'chat') {
      ChatModule.loadHistory();
    } else if (tab === 'flashcards') {
      FlashcardsModule.loadCards();
    } else if (tab === 'summary') {
      SummaryModule.loadSummary();
    } else if (tab === 'analytics') {
      AnalyticsModule.loadAnalytics();
    } else if (tab === 'settings') {
      this.loadSettingsInfo();
    }

    lucide.createIcons();
  },

  toggleMobileSidebar(forceClose = false) {
    const sidebar = document.getElementById('app-sidebar');
    const backdrop = document.getElementById('sidebar-backdrop');
    if (!sidebar) return;

    const isOpen = !sidebar.classList.contains('-translate-x-full');
    if (isOpen || forceClose) {
      sidebar.classList.add('-translate-x-full');
      if (backdrop) backdrop.classList.add('hidden');
    } else {
      sidebar.classList.remove('-translate-x-full');
      if (backdrop) backdrop.classList.remove('hidden');
    }
  },

  showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    const bgColors = {
      success: 'bg-emerald-950/90 border-emerald-600 text-emerald-200',
      error: 'bg-rose-950/90 border-rose-600 text-rose-200',
      warning: 'bg-amber-950/90 border-amber-600 text-amber-200',
      info: 'bg-indigo-950/90 border-indigo-600 text-indigo-200'
    };

    toast.className = `flex items-center gap-3 px-4 py-3 rounded-xl border shadow-xl backdrop-blur-md text-xs font-semibold animate-fade-in ${bgColors[type] || bgColors.info}`;
    toast.innerHTML = `<span>${message}</span>`;

    container.appendChild(toast);
    setTimeout(() => {
      toast.classList.add('opacity-0', 'transition-opacity');
      setTimeout(() => toast.remove(), 300);
    }, 3500);
  }
};

// Global startup
window.addEventListener('DOMContentLoaded', () => {
  App.init();
});

