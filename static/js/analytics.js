// Learning Analytics & Progress Visualizer
const AnalyticsModule = {
  activityChart: null,
  masteryChart: null,

  init() {
    // will be loaded when analytics tab is opened
  },

  async loadAnalytics() {
    try {
      const data = await API.getAnalytics();
      this.renderStats(data);
      this.renderCharts(data);
    } catch (err) {
      console.error('Error loading analytics:', err);
    }
  },

  renderStats(data) {
    document.getElementById('stat-study-time').textContent = `${data.total_study_minutes || 0}m`;
    document.getElementById('stat-total-reviews').textContent = data.total_reviews || 0;
    document.getElementById('stat-mastered-cards').textContent = data.mastered_flashcards || 0;
    document.getElementById('stat-quiz-avg').textContent = `${data.average_quiz_score || 0}%`;
    document.getElementById('stat-quizzes-taken').textContent = data.total_quizzes_taken || 0;
    document.getElementById('stat-total-docs').textContent = data.total_documents || 0;

    // Study Recommendation
    const recEl = document.getElementById('analytics-recommendation');
    if (recEl) {
      if (data.total_reviews < 5) {
        recEl.textContent = '💡 Recommendation: Review your Leitner flashcards to kickstart your spaced repetition retention curve!';
      } else if (data.average_quiz_score < 70 && data.total_quizzes_taken > 0) {
        recEl.textContent = '💡 Recommendation: Ask the AI Tutor in Exam Coach mode about your weaker topics before taking another quiz.';
      } else {
        recEl.textContent = '🔥 Excellent momentum! Your active recall score is strong. Keep up your daily study streak!';
      }
    }
  },

  renderCharts(data) {
    if (typeof Chart === 'undefined') return;

    // 1. Activity Bar Chart (Last 7 Days)
    const ctxActivity = document.getElementById('chart-activity');
    if (ctxActivity) {
      if (this.activityChart) this.activityChart.destroy();

      const dates = (data.recent_activity || []).map(r => r.study_date).reverse();
      const minutes = (data.recent_activity || []).map(r => Math.round(r.total_seconds / 60)).reverse();

      // If empty, supply placeholder dates
      const labels = dates.length ? dates : ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Today'];
      const values = minutes.length ? minutes : [15, 25, 40, 20, 50, 30, 45];

      this.activityChart = new Chart(ctxActivity, {
        type: 'bar',
        data: {
          labels: labels,
          datasets: [{
            label: 'Study Minutes',
            data: values,
            backgroundColor: 'rgba(99, 102, 241, 0.7)',
            borderColor: '#6366f1',
            borderWidth: 1,
            borderRadius: 6
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false }
          },
          scales: {
            y: {
              beginAtZero: true,
              grid: { color: 'rgba(255, 255, 255, 0.05)' },
              ticks: { color: '#94a3b8' }
            },
            x: {
              grid: { display: false },
              ticks: { color: '#94a3b8' }
            }
          }
        }
      });
    }

    // 2. Mastery Doughnut Chart
    const ctxMastery = document.getElementById('chart-mastery');
    if (ctxMastery) {
      if (this.masteryChart) this.masteryChart.destroy();

      const mastered = data.mastered_flashcards || 0;
      const learning = Math.max(0, (data.total_flashcards || 0) - mastered);

      this.masteryChart = new Chart(ctxMastery, {
        type: 'doughnut',
        data: {
          labels: ['Mastered (Box 4-5)', 'In Review (Box 1-3)'],
          datasets: [{
            data: [mastered || 1, learning || 1],
            backgroundColor: ['#10b981', '#6366f1'],
            borderWidth: 0
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'bottom',
              labels: { color: '#94a3b8', font: { size: 11 } }
            }
          },
          cutout: '75%'
        }
      });
    }
  }
};

