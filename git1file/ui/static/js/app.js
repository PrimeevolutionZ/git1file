class Git1FileUI {
    constructor() {
        this.form               = document.getElementById('analyzeForm');
        this.sourceInput        = document.getElementById('source');
        this.formatSelect       = document.getElementById('format');
        this.modeSelect         = document.getElementById('mode');
        this.includeMarkdownCb  = document.getElementById('includeMarkdown');
        this.outputSection      = document.getElementById('outputSection');
        this.statsSection       = document.getElementById('statsSection');
        this.output             = document.getElementById('output');
        this.statsGrid          = document.getElementById('statsGrid');
        this.copyBtn            = document.getElementById('copyBtn');
        this.downloadBtn        = document.getElementById('downloadBtn');
        this.tokenCount         = document.getElementById('tokenCount');
        this.spinner            = document.getElementById('spinner');
        this.btnText            = document.getElementById('btn-text');
        this.analyzeButton      = document.getElementById('analyzeButton');

        // Markdown elements
        this.markdownInfo       = document.getElementById('markdownInfo');
        this.markdownCount      = document.getElementById('markdownCount');
        this.markdownSize       = document.getElementById('markdownSize');
        this.downloadMarkdownBtn = document.getElementById('downloadMarkdownBtn');
        this.includeMarkdownBtn  = document.getElementById('includeMarkdownBtn');

        this.stats = null;
        this.outputContent = null;

        console.log('Git1FileUI initialized');
        console.log('Form:', this.form);
        console.log('Source input:', this.sourceInput);
        console.log('Format select:', this.formatSelect);
        console.log('Mode select:', this.modeSelect);
        console.log('Button:', this.analyzeButton);


        if (!this.sourceInput) {
            console.error('FATAL: source input not found!');
            alert('Critical error: form elements not found. Check HTML structure.');
            return;
        }

        this.form.addEventListener('submit', (e) => {
            console.log('Form submit triggered!');
            this.handleSubmit(e);
        });

        this.copyBtn.addEventListener('click', this.copyToClipboard.bind(this));
        this.downloadBtn.addEventListener('click', this.downloadOutput.bind(this));

        // Markdown event listeners
        if (this.downloadMarkdownBtn) {
            this.downloadMarkdownBtn.addEventListener('click', this.downloadMarkdownFiles.bind(this));
        }
        if (this.includeMarkdownBtn) {
            this.includeMarkdownBtn.addEventListener('click', this.includeMarkdownInAnalysis.bind(this));
        }

        // Add event listener for calculating stats on input change
        this.sourceInput.addEventListener('input', this.calculateStatsDebounced.bind(this));
        this.modeSelect.addEventListener('change', this.calculateStatsDebounced.bind(this));
    }

    // Debounce function to limit API calls
    calculateStatsDebounced(e) {
        clearTimeout(this.timeout);
        if (this.sourceInput.value.length < 3) {
             this.hideStats();
             return;
        }

        this.timeout = setTimeout(() => {
            this.calculateStats();
        }, 500);
    }

    async calculateStats() {
        const source = this.sourceInput.value;
        const mode = this.modeSelect.value;

        if (!source) {
            this.hideStats();
            return;
        }

        try {
            const url = `/api/v1/stats?source=${encodeURIComponent(source)}&mode=${mode}`;
            const response = await fetch(url);

            if (!response.ok) {
                if (response.status === 400) {
                     this.hideStats();
                     return;
                }
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const stats = await response.json();
            this.updateStatsUI(stats);

        } catch (error) {
            console.error("Error fetching stats:", error);
            this.hideStats();
        }
    }

    async handleSubmit(e) {
        console.log('handleSubmit called!');
        e.preventDefault();

        this.hideResults();
        this.hideStats();
        this.showLoading();

        const source = this.sourceInput.value;
        const format = this.formatSelect.value;
        const mode = this.modeSelect.value;
        const includeMarkdown = this.includeMarkdownCb.checked;

        console.log('Submitting:', { source, format, mode, includeMarkdown }); // 🔧 DEBUG

        try {
            const response = await fetch('/api/v1/ingest', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    source: source,
                    format: format,
                    mode: mode,
                    include_markdown: includeMarkdown,
                    compress: true
                })
            });

            console.log('Response status:', response.status); // 🔧 DEBUG

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || `Server responded with status: ${response.status}`);
            }

            this.outputContent = await response.text();
            this.renderOutput(this.outputContent, format);
            this.showResults();
            this.calculateStats();

        } catch (error) {
            console.error('Submit error:', error); // 🔧 DEBUG
            this.showError(error.message);
        } finally {
            this.hideLoading();
        }
    }

    renderOutput(content, format) {
        this.output.querySelector('code').textContent = content;
        this.tokenCount.textContent = this.estimateTokens(content);

        const filename = `git1file_output.${format === 'plain' ? 'txt' : format}`;
        this.downloadBtn.setAttribute('data-filename', filename);
        this.downloadBtn.setAttribute('data-content', content);
    }

    copyToClipboard() {
        const content = this.output.querySelector('code').textContent;
        if (content) {
            navigator.clipboard.writeText(content).then(() => {
                this.copyBtn.textContent = '✅ Copied!';
                setTimeout(() => {
                    this.copyBtn.textContent = '📋 Copy';
                }, 1500);
            }).catch(err => {
                this.showError('Failed to copy text: ' + err);
            });
        }
    }

    downloadOutput() {
        const filename = this.downloadBtn.getAttribute('data-filename');
        const content = this.downloadBtn.getAttribute('data-content');

        if (filename && content) {
            const blob = new Blob([content], { type: 'text/plain' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            a.click();
            URL.revokeObjectURL(url);
        }
    }

    async downloadMarkdownFiles() {
        const source = this.sourceInput.value;
        const format = this.formatSelect.value;

        this.downloadMarkdownBtn.disabled = true;
        this.downloadMarkdownBtn.textContent = 'Downloading...';

        try {
            const response = await fetch('/api/v1/ingest/markdown', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    source: source,
                    format: format,
                    mode: this.modeSelect.value,
                    compress: false
                })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || `Server responded with status: ${response.status}`);
            }

            const content = await response.text();
            const filename = `git1file_markdown.${format === 'plain' ? 'txt' : format}`;

            const blob = new Blob([content], { type: 'text/plain' });
            const blobUrl = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = blobUrl;
            a.download = filename;
            a.click();
            URL.revokeObjectURL(blobUrl);

            this.downloadMarkdownBtn.textContent = '✅ Downloaded!';
            setTimeout(() => {
                this.downloadMarkdownBtn.textContent = '📥 Download Markdown Files';
                this.downloadMarkdownBtn.disabled = false;
            }, 2000);

        } catch (err) {
            this.showError('Failed to download markdown: ' + err.message);
            this.downloadMarkdownBtn.textContent = '📥 Download Markdown Files';
            this.downloadMarkdownBtn.disabled = false;
        }
    }

    includeMarkdownInAnalysis() {
        this.includeMarkdownCb.checked = true;
        // 🔧 FIX: Используем HTMLFormElement.requestSubmit() вместо dispatchEvent
        if (this.form.requestSubmit) {
            this.form.requestSubmit();
        } else {
            // Fallback для старых браузеров
            this.form.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
        }
    }

    showLoading() {
        this.spinner.classList.remove('hidden');
        this.btnText.textContent = 'Analyzing...';
        this.analyzeButton.disabled = true;
    }

    hideLoading() {
        this.spinner.classList.add('hidden');
        this.btnText.textContent = 'Analyze Repository';
        this.analyzeButton.disabled = false;
    }

    hideResults() {
        this.outputSection.classList.add('hidden');
        this.statsSection.classList.add('hidden');
        this.markdownInfo.classList.add('hidden');
        this.output.querySelector('code').textContent = '';
        this.tokenCount.textContent = '0';
    }

    showResults() {
        this.outputSection.classList.remove('hidden');
    }

    showStats() {
        this.statsSection.classList.remove('hidden');
    }

    hideStats() {
        this.statsSection.classList.add('hidden');
    }

    showError(message) {
        console.error('Git1File Error:', message);
        alert('Error: ' + message);
    }

    updateStatsUI(stats) {
        this.stats = stats;
        const totalFiles = stats.total_files || 0;
        const totalChars = stats.total_characters || 0;
        const markdownFiles = stats.markdown_files || 0;
        const markdownChars = stats.markdown_characters || 0;
        const gitBranch = stats.git_branch || 'N/A';
        const gitCommit = stats.git_commit ? stats.git_commit.substring(0, 7) : 'N/A';

        const langStatsHtml = stats.languages.map(lang => `
            <div class="stat-item">
                <span class="stat-value">${lang.files}</span>
                <span class="stat-label">${lang.name} Files</span>
            </div>
        `).join('');

        this.statsGrid.innerHTML = `
            <div class="stat-item">
                <span class="stat-value">${totalFiles}</span>
                <span class="stat-label">Total Files</span>
            </div>
            <div class="stat-item">
                <span class="stat-value">${this.formatSize(totalChars)}</span>
                <span class="stat-label">Total Size</span>
            </div>
            <div class="stat-item">
                <span class="stat-value">${gitBranch}</span>
                <span class="stat-label">Git Branch</span>
            </div>
            <div class="stat-item">
                <span class="stat-value">${gitCommit}</span>
                <span class="stat-label">Git Commit</span>
            </div>
            ${langStatsHtml}
        `;

        if (markdownFiles > 0) {
            this.markdownCount.textContent = markdownFiles;
            this.markdownSize.textContent = this.formatSize(markdownChars);
            this.markdownInfo.classList.remove('hidden');
        } else {
            this.markdownInfo.classList.add('hidden');
        }

        this.showStats();
    }

    formatSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    estimateTokens(content) {
        return Math.ceil(content.length / 4).toLocaleString();
    }
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        console.log('DOM loaded, initializing Git1FileUI');
        if (!window.git1fileUI) {
            window.git1fileUI = new Git1FileUI();
        }
    });
} else {
    // DOM уже загружен
    console.log('DOM already loaded, initializing immediately');
    if (!window.git1fileUI) {
        window.git1fileUI = new Git1FileUI();
    }
}