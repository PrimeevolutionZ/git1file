// app.js
class Git1FileUI {
    constructor() {
        this.form           = document.getElementById('analyzeForm');
        this.sourceInput    = document.getElementById('source');
        this.formatSelect   = document.getElementById('format');
        this.compressSelect = document.getElementById('compress');
        this.outputSection  = document.getElementById('outputSection');
        this.statsSection   = document.getElementById('statsSection');
        this.output         = document.getElementById('output');
        this.statsGrid      = document.getElementById('statsGrid');
        this.copyBtn        = document.getElementById('copyBtn');
        this.downloadBtn    = document.getElementById('downloadBtn');
        this.tokenCount     = document.getElementById('tokenCount');
        this.spinner        = document.getElementById('spinner');
        this.btnText        = document.getElementById('btn-text');

        this.initEventListeners();
    }

    initEventListeners() {
        this.form.addEventListener('submit', (e) => this.handleSubmit(e));
        this.copyBtn.addEventListener('click', () => this.copyToClipboard());
        this.downloadBtn.addEventListener('click', () => this.downloadFile());
    }

    async handleSubmit(e) {
        e.preventDefault();
        const source   = this.sourceInput.value.trim();
        const format   = this.formatSelect.value;
        const compress = this.compressSelect.value === 'true';

        this.showLoading();
        this.hideResults();

        try {
            const res = await fetch('/api/v1/ingest', {
                method : 'POST',
                headers: { 'Content-Type': 'application/json' },
                body   : JSON.stringify({ source, format, compress })
            });
            if (!res.ok) throw new Error(await res.text());

            const content = await res.text();
            await this.fetchStats(source);
            this.displayOutput(content, format);

        } catch (err) {
            alert(err.message);
            console.error(err);
        } finally {
            this.hideLoading();
        }
    }

    async fetchStats(source) {
        try {
            const res = await fetch(`/api/v1/stats?source=${encodeURIComponent(source)}`);
            const stats = await res.json();
            this.displayStats(stats);
        } catch (err) {
            console.warn('Stats fetch failed:', err);
        }
    }

    displayStats(stats) {
        this.statsSection.classList.remove('hidden');
        this.statsGrid.innerHTML = `
            <div class="stat-card">
                <div class="stat-value">${stats.total_files}</div>
                <div class="stat-label">Files</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${(stats.total_characters / 1024).toFixed(1)}</div>
                <div class="stat-label">KB Size</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${stats.languages.length}</div>
                <div class="stat-label">Languages</div>
            </div>
            ${stats.languages.slice(0, 2).map(lang => `
                <div class="stat-card">
                    <div class="stat-value">${lang.files}</div>
                    <div class="stat-label">${lang.name}</div>
                </div>
            `).join('')}
        `;
    }

    displayOutput(content, format) {
        this.outputSection.classList.remove('hidden');
        this.output.textContent = content;
        this.estimateTokens(content);
        const repoName = new URLSearchParams(window.location.search).get('source')?.split('/').pop() || 'repository';
        this.downloadBtn.dataset.filename = `git1file-${repoName}.${format}`;
    }

    estimateTokens(content) {
        const tokens = Math.ceil(content.length / 4);
        this.tokenCount.textContent = tokens.toLocaleString();
    }

    async copyToClipboard() {
        try {
            await navigator.clipboard.writeText(this.output.textContent);
            this.copyBtn.textContent = '✅ Copied!';
            setTimeout(() => this.copyBtn.textContent = '📋 Copy', 2000);
        } catch (err) {
            alert('Copy failed. Copy manually.');
        }
    }

    downloadFile() {
        const filename = this.downloadBtn.dataset.filename || 'git1file-output.txt';
        const blob = new Blob([this.output.textContent], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        URL.revokeObjectURL(url);
    }

    showLoading() {
        this.spinner.classList.remove('hidden');
        this.btnText.textContent = 'Analyzing...';
        this.form.disabled = true;
    }

    hideLoading() {
        this.spinner.classList.add('hidden');
        this.btnText.textContent = 'Analyze Repository';
        this.form.disabled = false;
    }

    hideResults() {
        this.outputSection.classList.add('hidden');
        this.statsSection.classList.add('hidden');
    }
}

document.addEventListener('DOMContentLoaded', () => new Git1FileUI());