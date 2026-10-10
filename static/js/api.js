// AI Study Buddy Pro - API Client
const API = {
  baseUrl: '',

  async request(endpoint, options = {}) {
    const defaultHeaders = {
      'Accept': 'application/json',
    };

    if (!(options.body instanceof FormData)) {
      defaultHeaders['Content-Type'] = 'application/json';
    }

    const config = {
      ...options,
      headers: {
        ...defaultHeaders,
        ...(options.headers || {})
      }
    };

    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`, config);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || data.message || `Request failed with status ${response.status}`);
      }

      return data;
    } catch (error) {
      console.error(`API Error on [${endpoint}]:`, error);
      throw error;
    }
  },

  // Documents
  async getDocuments() {
    return this.request('/api/documents');
  },

  async getDocument(id) {
    return this.request(`/api/documents/${id}`);
  },

  async deleteDocument(id) {
    return this.request(`/api/documents/${id}`, { method: 'DELETE' });
  },

  async uploadDocument(file) {
    const formData = new FormData();
    formData.append('file', file);
    return this.request('/api/documents/upload', {
      method: 'POST',
      body: formData
    });
  },

  async uploadText(title, content) {
    return this.request('/api/documents/upload-text', {
      method: 'POST',
      body: JSON.stringify({ title, content })
    });
  },

  async loadSampleDocuments() {
    return this.request('/api/documents/load-samples', { method: 'POST' });
  },

  // Chat
  async sendChatMessage(message, documentId, persona = 'academic') {
    return this.request('/api/chat/send', {
      method: 'POST',
      body: JSON.stringify({ message, document_id: documentId, persona })
    });
  },

  async getChatHistory(documentId) {
    const query = documentId ? `?document_id=${documentId}` : '';
    return this.request(`/api/chat/history${query}`);
  },

  async clearChatHistory(documentId) {
    const query = documentId ? `?document_id=${documentId}` : '';
    return this.request(`/api/chat/clear${query}`, { method: 'DELETE' });
  },

  // Flashcards
  async getFlashcards(deckTitle, documentId) {
    const params = new URLSearchParams();
    if (deckTitle) params.append('deck_title', deckTitle);
    if (documentId) params.append('document_id', documentId);
    return this.request(`/api/flashcards?${params.toString()}`);
  },

  async generateFlashcards(documentId, deckTitle, count = 8) {
    return this.request('/api/flashcards/generate', {
      method: 'POST',
      body: JSON.stringify({ document_id: documentId, deck_title: deckTitle, count })
    });
  },

  async reviewFlashcard(cardId, rating) {
    return this.request('/api/flashcards/review', {
      method: 'POST',
      body: JSON.stringify({ card_id: cardId, rating })
    });
  },

  async deleteFlashcard(cardId) {
    return this.request(`/api/flashcards/${cardId}`, { method: 'DELETE' });
  },

  // Quizzes
  async getQuizzes() {
    return this.request('/api/quizzes');
  },

  async getQuiz(id) {
    return this.request(`/api/quizzes/${id}`);
  },

  async generateQuiz(documentId, title, numQuestions = 5, difficulty = 'medium') {
    return this.request('/api/quizzes/generate', {
      method: 'POST',
      body: JSON.stringify({ document_id: documentId, title, num_questions: numQuestions, difficulty })
    });
  },

  async submitQuiz(quizId, answers) {
    return this.request('/api/quizzes/submit', {
      method: 'POST',
      body: JSON.stringify({ quiz_id: quizId, answers })
    });
  },

  // Summaries
  async generateSummary(documentId) {
    return this.request('/api/summaries/generate', {
      method: 'POST',
      body: JSON.stringify({ document_id: documentId })
    });
  },

  async getSummary(documentId) {
    return this.request(`/api/summaries/${documentId}`);
  },

  // Analytics
  async getAnalytics() {
    return this.request('/api/analytics');
  },

  async logStudySession(sessionType, durationSeconds, notes = '') {
    return this.request('/api/analytics/session', {
      method: 'POST',
      body: JSON.stringify({ session_type: sessionType, duration_seconds: durationSeconds, notes })
    });
  },

  // Settings
  async getSettings() {
    return this.request('/api/settings');
  },

  async updateSettings(settingsData) {
    return this.request('/api/settings', {
      method: 'POST',
      body: JSON.stringify(settingsData)
    });
  },

  async verifyApiKey(provider, apiKey) {
    return this.request('/api/settings/verify', {
      method: 'POST',
      body: JSON.stringify({ provider, api_key: apiKey })
    });
  }
};

