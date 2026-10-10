// Mind Map & Executive Summary Controller
const SummaryModule = {
  currentSummary: null,

  init() {
    this.bindEvents();
  },

  bindEvents() {
    const genBtn = document.getElementById('sum-generate-btn');
    const exportBtn = document.getElementById('sum-export-btn');

    if (genBtn) {
      genBtn.addEventListener('click', () => this.generateFreshSummary());
    }
    if (exportBtn) {
      exportBtn.addEventListener('click', () => this.exportStudyGuide());
    }
  },

  async loadSummary() {
    if (!App.activeDocumentId) return;
    const container = document.getElementById('sum-content');
    if (!container) return;

    try {
      const res = await API.getSummary(App.activeDocumentId);
      this.currentSummary = res.summary;
      this.renderSummary(res.summary);
    } catch (err) {
      console.warn('Could not auto-fetch summary, user can generate it:', err);
    }
  },

  async generateFreshSummary() {
    if (!App.activeDocumentId) {
      App.showToast('Please select a document first', 'warning');
      return;
    }
    const genBtn = document.getElementById('sum-generate-btn');
    if (genBtn) {
      genBtn.disabled = true;
      genBtn.innerHTML = '<span class="inline-block animate-spin mr-2">↻</span> Synthesizing study guide...';
    }

    try {
      const res = await API.generateSummary(App.activeDocumentId);
      this.currentSummary = res.summary;
      this.renderSummary(res.summary);
      App.showToast('Executive study guide generated! 🧠', 'success');
    } catch (err) {
      App.showToast(err.message || 'Failed to generate summary', 'error');
    } finally {
      if (genBtn) {
        genBtn.disabled = false;
        genBtn.textContent = 'Regenerate Guide';
      }
    }
  },

  renderSummary(data) {
    if (!data) return;

    // TL;DR
    const tldrEl = document.getElementById('sum-tldr');
    if (tldrEl) tldrEl.textContent = data.tldr || 'No summary available.';

    // Key Takeaways
    const takeawaysEl = document.getElementById('sum-takeaways');
    if (takeawaysEl && data.key_takeaways) {
      takeawaysEl.innerHTML = data.key_takeaways.map(t => `
        <li class="flex items-start gap-2.5 text-sm text-slate-300">
          <i data-lucide="check" class="w-4 h-4 text-emerald-400 mt-1 flex-shrink-0"></i>
          <span>${t}</span>
        </li>
      `).join('');
    }

    // Cheat Sheet
    const cheatEl = document.getElementById('sum-cheatsheet');
    if (cheatEl && data.cheat_sheet) {
      cheatEl.innerHTML = data.cheat_sheet.map(c => `
        <div class="p-3 rounded-lg bg-slate-900/60 border border-slate-800 text-xs text-slate-300 font-mono flex items-start gap-2">
          <span class="text-amber-400 font-bold">⚡</span>
          <span>${c}</span>
        </div>
      `).join('');
    }

    // Glossary
    const glossaryEl = document.getElementById('sum-glossary');
    if (glossaryEl && data.glossary) {
      glossaryEl.innerHTML = data.glossary.map(g => `
        <div class="p-4 rounded-xl bg-slate-800/60 border border-slate-700/60 hover:border-indigo-500/50 transition-colors">
          <div class="font-bold text-sm text-indigo-300 mb-1 flex items-center gap-2">
            <i data-lucide="book" class="w-4 h-4 text-indigo-400"></i>
            ${g.term}
          </div>
          <div class="text-xs text-slate-300 leading-relaxed">${g.definition}</div>
        </div>
      `).join('');
    }

    // Mind Map SVG rendering
    this.renderMindMapSVG(data.mind_map);
    lucide.createIcons();
  },

  renderMindMapSVG(nodes) {
    const svg = document.getElementById('mindmap-svg');
    if (!svg || !nodes || nodes.length === 0) return;

    // Simple layout calculation
    const width = 800;
    const height = 450;
    const centerX = width / 2;
    const centerY = height / 2;

    const root = nodes.find(n => n.parent === null) || nodes[0];
    const children = nodes.filter(n => n.parent === root.id);

    let linksHtml = '';
    let nodesHtml = '';

    // Render Root Node
    nodesHtml += `
      <g class="mindmap-node" transform="translate(${centerX}, ${centerY})">
        <rect x="-100" y="-25" width="200" height="50" rx="25" fill="#4f46e5" stroke="#818cf8" stroke-width="2" />
        <text x="0" y="5" fill="#ffffff" font-size="13" font-weight="bold" text-anchor="middle">${root.label}</text>
      </g>
    `;

    // Render 1st-level Child Nodes in a radial/ellipse pattern
    const angleStep = (2 * Math.PI) / Math.max(1, children.length);
    const radiusX = 260;
    const radiusY = 150;

    children.forEach((child, i) => {
      const angle = i * angleStep;
      const childX = centerX + radiusX * Math.cos(angle);
      const childY = centerY + radiusY * Math.sin(angle);

      // Curved link
      linksHtml += `
        <path d="M ${centerX} ${centerY} Q ${(centerX + childX)/2} ${(centerY + childY)/2 - 20} ${childX} ${childY}"
              class="mindmap-link" fill="none" stroke="#6366f1" stroke-width="2" />
      `;

      nodesHtml += `
        <g class="mindmap-node" transform="translate(${childX}, ${childY})">
          <rect x="-80" y="-20" width="160" height="40" rx="12" fill="#1e293b" stroke="#64748b" stroke-width="1.5" />
          <text x="0" y="5" fill="#e2e8f0" font-size="11" font-weight="600" text-anchor="middle">${child.label.substring(0, 20)}</text>
        </g>
      `;

      // Sub-children
      const subChildren = nodes.filter(n => n.parent === child.id);
      subChildren.forEach((sub, subIdx) => {
        const subOffset = (subIdx - (subChildren.length - 1) / 2) * 50;
        const subX = childX + (Math.cos(angle) > 0 ? 90 : -90);
        const subY = childY + subOffset;

        linksHtml += `
          <line x1="${childX}" y1="${childY}" x2="${subX}" y2="${subY}" stroke="#475569" stroke-width="1.5" stroke-dasharray="2" />
        `;

        nodesHtml += `
          <g class="mindmap-node" transform="translate(${subX}, ${subY})">
            <rect x="-60" y="-14" width="120" height="28" rx="8" fill="#0f172a" stroke="#334155" stroke-width="1" />
            <text x="0" y="4" fill="#94a3b8" font-size="10" text-anchor="middle">${sub.label.substring(0, 16)}</text>
          </g>
        `;
      });
    });

    svg.setAttribute('viewBox', `0 0 ${width} ${height}`);
    svg.innerHTML = linksHtml + nodesHtml;
  },

  exportStudyGuide() {
    if (!this.currentSummary) {
      App.showToast('No summary loaded to export', 'warning');
      return;
    }

    const s = this.currentSummary;
    let md = `# Study Guide: ${s.title || 'Document'}\n\n`;
    md += `## Executive TL;DR\n${s.tldr}\n\n`;
    md += `## Key Takeaways\n` + (s.key_takeaways || []).map(t => `- ${t}`).join('\n') + '\n\n';
    md += `## Exam Cheat Sheet\n` + (s.cheat_sheet || []).map(c => `- ${c}`).join('\n') + '\n\n';
    md += `## Key Terms & Definitions\n` + (s.glossary || []).map(g => `### ${g.term}\n${g.definition}`).join('\n\n');

    const blob = new Blob([md], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${(s.title || 'Study_Guide').replace(/\s+/g, '_')}_Study_Guide.md`;
    a.click();
    URL.revokeObjectURL(url);
    App.showToast('Study Guide downloaded as Markdown! 📥', 'success');
  }
};

