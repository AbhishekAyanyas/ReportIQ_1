// ============================================================
// ReportIQ — main.js  (fixed: voice + summary)
// ============================================================

const API_BASE = window.location.origin;

// ── Upload ───────────────────────────────────────────────────
async function uploadFile() {
    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];
    if (!file) { showNotification('Please select a file', 'error'); return; }

    const formData = new FormData();
    formData.append('file', file);

    try {
        showLoading(true);
        const response = await fetch(`${API_BASE}/api/upload/`, { method: 'POST', body: formData });
        if (!response.ok) throw new Error('Upload failed');
        const data = await response.json();

        showNotification('File uploaded successfully!', 'success');
        localStorage.setItem('currentReportId', data.report_id);

        displayUploadResults(data);
        displayReportSummary(data);   // ← live summary update
    } catch (error) {
        console.error('Upload error:', error);
        showNotification('Upload failed. Please try again.', 'error');
    } finally {
        showLoading(false);
    }
}

function displayUploadResults(data) {
    const resultsDiv = document.getElementById('uploadResults');
    if (!resultsDiv) return;
    resultsDiv.innerHTML = `
        <div style="margin-top:1rem;padding:1rem;background:rgba(59,130,246,0.1);border-radius:12px;border:1px solid rgba(59,130,246,0.3);">
            <p style="color:#4CAF50;font-weight:700;margin-bottom:0.5rem;">✅ Upload Successful!</p>
            <p style="color:#94A3B8;font-size:0.9rem;"><b>Report ID:</b> ${data.report_id}</p>
            <p style="color:#94A3B8;font-size:0.9rem;"><b>Quality Score:</b> ${data.quality?.quality_score ?? 'N/A'}%</p>
            <p style="color:#94A3B8;font-size:0.9rem;"><b>Missing Values:</b> ${data.quality?.missing ?? 'N/A'}</p>
            <a href="/visualizations?id=${data.report_id}"
               style="display:inline-block;margin-top:0.75rem;padding:0.5rem 1rem;
                      background:linear-gradient(135deg,#3B82F6,#06B6D4);color:white;
                      border-radius:8px;font-size:0.9rem;text-decoration:none;">
               📊 View Visualizations
            </a>
        </div>`;
    resultsDiv.classList.remove('hidden');
}

// ── Live Report Summary (replaces placeholder) ───────────────
function displayReportSummary(data) {
    const card = document.getElementById('reportSummaryCard');
    if (!card) return;

    const q   = data.quality   || {};
    const meta = data.metadata || data.info || {};

    // Prefer dedicated fields, fall back gracefully
    const rows    = meta.rows    ?? q.total_rows    ?? '—';
    const cols    = meta.columns ?? q.total_columns ?? '—';
    const missing = q.missing    ?? q.missing_values ?? '—';
    const dupes   = q.duplicates ?? q.duplicate_rows ?? '—';
    const score   = q.quality_score ?? '—';
    const numCols = q.numeric_columns    ?? '—';
    const catCols = q.categorical_columns ?? '—';

    card.innerHTML = `
        <div class="card-header">
            <span class="card-icon">📋</span>
            <h3>Report Summary</h3>
        </div>
        <div style="display:flex;flex-direction:column;gap:0.65rem;margin-top:0.5rem;">
            ${summaryRow('📁', 'Report ID',   data.report_id, '#3B82F6')}
            ${summaryRow('📏', 'Rows',         rows,          '#06B6D4')}
            ${summaryRow('🗂',  'Columns',      cols,          '#8B5CF6')}
            ${summaryRow('🔢', 'Numeric cols', numCols,       '#F59E0B')}
            ${summaryRow('🔤', 'Category cols',catCols,       '#EC4899')}
            ${summaryRow('❓', 'Missing vals', missing,       '#EF4444')}
            ${summaryRow('♻', 'Duplicates',   dupes,         '#F97316')}
            ${summaryRow('🏅', 'Quality score',score !== '—' ? score + '%' : '—', '#4CAF50')}
        </div>
        <div style="margin-top:1rem;display:flex;gap:0.5rem;flex-wrap:wrap;">
            <a href="/visualizations?id=${data.report_id}"
               style="padding:0.4rem 0.9rem;background:rgba(59,130,246,0.2);color:#93C5FD;
                      border-radius:8px;font-size:0.82rem;text-decoration:none;border:1px solid rgba(59,130,246,0.4);">
               📊 Charts
            </a>
            <button onclick="loadVoiceSuggestions('${data.report_id}')"
               style="padding:0.4rem 0.9rem;background:rgba(6,182,212,0.2);color:#67E8F9;
                      border-radius:8px;font-size:0.82rem;border:1px solid rgba(6,182,212,0.4);cursor:pointer;">
               🎤 Voice Tips
            </button>
        </div>`;
}

function summaryRow(icon, label, value, color) {
    return `
        <div style="display:flex;justify-content:space-between;align-items:center;
                    padding:0.4rem 0.6rem;background:rgba(255,255,255,0.04);border-radius:8px;">
            <span style="color:#94A3B8;font-size:0.88rem;">${icon} ${label}</span>
            <span style="color:${color};font-weight:700;font-size:0.88rem;">${value}</span>
        </div>`;
}

// ── Dashboard stats ──────────────────────────────────────────
async function loadDashboardStats() {
    try {
        const response = await fetch(`${API_BASE}/api/history/statistics`);
        const data = await response.json();
        updateDashboardStats(data);
    } catch (error) {
        console.error('Error loading statistics:', error);
    }
}

function updateDashboardStats(stats) {
    const set = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val; };
    set('totalReports',      stats.total_reports);
    set('completedReports',  stats.completed_reports);
    set('processingReports', stats.processing_reports);
    set('failedReports',     stats.failed_reports);

    const rate = stats.success_rate ?? 0;
    set('successRate', rate + '%');
    const bar = document.getElementById('successRateBar');
    if (bar) bar.style.width = rate + '%';

    updateRecentActivity(stats.recent_activity || []);
}

function updateRecentActivity(activities) {
    const list = document.getElementById('recentActivityList');
    if (!list) return;
    if (!activities.length) { list.innerHTML = '<div class="activity-item" style="color:#94A3B8;">No recent activity</div>'; return; }
    list.innerHTML = activities.map(a => `
        <div class="activity-item">
            <div style="font-size:1.4rem;">${a.status === 'completed' ? '✅' : '⏳'}</div>
            <div style="flex:1;">
                <div style="color:white;font-weight:500;font-size:0.9rem;">Report ${a.report_id}</div>
                <div style="color:#94A3B8;font-size:0.82rem;margin-top:0.2rem;">${a.created_at}</div>
            </div>
            <span class="status-badge status-${a.status}">${a.status}</span>
        </div>`).join('');
}

// ── History / table ──────────────────────────────────────────
async function loadReportHistory() {
    try {
        const response = await fetch(`${API_BASE}/api/history/history`);
        const data = await response.json();
        displayReports(data.reports || []);
    } catch (error) {
        console.error('Error loading history:', error);
    }
}

function displayReports(reports) {
    const tbody = document.getElementById('reportsTableBody');
    if (!tbody) return;
    if (!reports.length) { tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;color:#94A3B8;">No reports found</td></tr>'; return; }
    tbody.innerHTML = reports.map((r, i) => `
        <tr>
            <td>${i + 1}</td>
            <td>${r.report_id}</td>
            <td>${new Date().toLocaleDateString()}</td>
            <td><span class="status-badge status-completed">Completed</span></td>
            <td>
                <button class="action-btn" onclick="viewReport('${r.report_id}')" title="View">👁️</button>
                <button class="action-btn" onclick="downloadReport('${r.report_id}')" title="Download">⬇️</button>
                <button class="action-btn" onclick="deleteReport('${r.report_id}')" title="Delete">🗑️</button>
            </td>
        </tr>`).join('');
}

function viewReport(id) { window.location.href = `/report?id=${id}`; }

async function downloadReport(reportId) {
    try {
        showNotification('Preparing download...', 'info');
        const link = document.createElement('a');
        link.href = `${API_BASE}/api/report/download/${reportId}`;
        link.download = `report_${reportId}.zip`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        showNotification('Download started!', 'success');
    } catch (e) { showNotification('Download failed.', 'error'); }
}

async function deleteReport(reportId) {
    if (!confirm('⚠️ Delete this report? This cannot be undone.')) return;
    try {
        showLoading(true);
        const res = await fetch(`${API_BASE}/api/report/delete/${reportId}`, { method: 'DELETE' });
        const data = await res.json();
        if (data.success) {
            showNotification('Report deleted!', 'success');
            setTimeout(() => loadReportHistory(), 800);
        } else throw new Error(data.message);
    } catch (e) { showNotification('Delete failed.', 'error'); }
    finally { showLoading(false); }
}

// ── Visualizations ───────────────────────────────────────────
async function loadVisualizations() {
    const id = new URLSearchParams(window.location.search).get('id') || localStorage.getItem('currentReportId');
    if (!id) { showNotification('No report ID found', 'error'); return; }
    try {
        const res = await fetch(`${API_BASE}/api/report/${id}`);
        const data = await res.json();
        displayVisualizations(data);
    } catch (e) { showNotification('Failed to load visualizations', 'error'); }
}

function displayVisualizations(data) {
    const container = document.getElementById('visualizationsContainer');
    if (!container) return;
    if (data.plots && data.plots.length) {
        container.innerHTML = data.plots.map(p => `
            <div class="chart-card">
                <div class="chart-title">📊 ${p.replace('_hist.png','').replace(/_/g,' ')}</div>
                <img src="/reports/${data.report_id}/${p}" alt="${p}" style="width:100%;border-radius:8px;">
            </div>`).join('');
    }
    displayDataPreviews(data.report_id);
}

function displayDataPreviews(reportId) {
    ['rawDataPreview','cleanDataPreview'].forEach((elId, i) => {
        const el = document.getElementById(elId);
        if (!el) return;
        const file = i === 0 ? 'raw_data_preview.html' : 'cleaned_data_preview.html';
        fetch(`/reports/${reportId}/${file}`)
            .then(r => r.text())
            .then(html => { el.innerHTML = `<div style="overflow-x:auto;">${html}</div>`; })
            .catch(() => {});
    });
}

// ── Voice Query — FIXED ──────────────────────────────────────
/*
  Root cause of "Voice recognition error":
  1. webkitSpeechRecognition only works on Chrome over HTTPS or localhost.
  2. If mic permission is blocked, it throws 'not-allowed'.
  3. Even when it works, the transcribed text was never sent to the backend.

  Fix:
  - Graceful fallback: if SpeechRecognition unavailable, hide mic button,
    let user type the query instead.
  - processVoiceQuery() now actually calls /api/voice/ask with the report_id.
  - Mic button gives visual feedback (🔴 listening / 🎤 idle).
  - All errors shown as friendly messages, never crash.
*/

let _recognition = null;
let _isListening  = false;

function initVoiceRecognition() {
    const SpeechAPI = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechAPI) {
        // Browser doesn't support — hide mic, show type-only hint
        const btn = document.getElementById('voiceStartBtn');
        if (btn) {
            btn.textContent = '⌨️ Type & Send';
            btn.onclick = () => submitVoiceQuery();
        }
        const hint = document.getElementById('voiceHint');
        if (hint) hint.textContent = 'Voice not supported in this browser — type your query and press Send.';
        return;
    }

    _recognition = new SpeechAPI();
    _recognition.continuous    = false;
    _recognition.interimResults = false;
    _recognition.lang           = 'en-IN';   // Indian English; change to 'hi-IN' for Hindi

    _recognition.onstart = () => {
        _isListening = true;
        const btn = document.getElementById('voiceStartBtn');
        if (btn) { btn.textContent = '🔴 Listening...'; btn.style.background = '#EF4444'; }
        showNotification('🎤 Listening... speak now', 'info');
    };

    _recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        const inp = document.getElementById('voiceInput');
        if (inp) inp.value = transcript;
        submitVoiceQuery(transcript);
    };

    _recognition.onerror = (event) => {
        _isListening = false;
        resetMicBtn();
        const msgs = {
            'not-allowed':  '🔒 Mic permission blocked. Allow microphone in browser settings.',
            'no-speech':    '🔇 No speech detected. Try again.',
            'network':      '🌐 Network error during voice recognition.',
            'audio-capture':'🎤 No microphone found.',
        };
        showNotification(msgs[event.error] || `Voice error: ${event.error}`, 'error');
        setVoiceResult(`⚠️ ${msgs[event.error] || 'Voice error: ' + event.error}`);
    };

    _recognition.onend = () => {
        _isListening = false;
        resetMicBtn();
    };
}

function resetMicBtn() {
    const btn = document.getElementById('voiceStartBtn');
    if (btn) { btn.textContent = '🎤 Start'; btn.style.background = ''; }
}

function startVoiceRecognition() {
    if (!_recognition) { submitVoiceQuery(); return; }   // type-only fallback
    if (_isListening) { _recognition.stop(); return; }
    try { _recognition.start(); }
    catch (e) { showNotification('Could not start microphone: ' + e.message, 'error'); }
}

// Called with a transcript string OR reads the text input
async function submitVoiceQuery(transcript) {
    const inp = document.getElementById('voiceInput');
    const query = transcript || (inp ? inp.value.trim() : '');
    if (!query) { showNotification('Please type or speak a query first.', 'error'); return; }

    // Get report_id — prefer URL param, then localStorage
    const reportId =
        new URLSearchParams(window.location.search).get('id') ||
        localStorage.getItem('currentReportId');

    if (!reportId) {
        setVoiceResult('⚠️ No report loaded. Please upload a file first.');
        showNotification('Upload a file before querying.', 'error');
        return;
    }

    setVoiceResult('⏳ Processing...');

    try {
        const res = await fetch(`${API_BASE}/api/voice/ask`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ report_id: reportId, query })
        });

        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.detail || `HTTP ${res.status}`);
        }

        const data = await res.json();
        setVoiceResult(data.answer || 'No answer returned.');
        showNotification('Query answered ✅', 'success');

    } catch (e) {
        console.error('Voice query error:', e);
        setVoiceResult(`❌ Error: ${e.message}`);
        showNotification('Query failed: ' + e.message, 'error');
    }
}

function setVoiceResult(text) {
    const box = document.getElementById('voiceResult');
    if (box) { box.textContent = text; box.style.display = 'block'; }
}

// Load smart suggestions for the loaded report
async function loadVoiceSuggestions(reportId) {
    const id = reportId || new URLSearchParams(window.location.search).get('id') || localStorage.getItem('currentReportId');
    if (!id) return;
    try {
        const res = await fetch(`${API_BASE}/api/voice/suggestions/${id}`);
        const data = await res.json();
        const box = document.getElementById('voiceSuggestions');
        if (!box || !data.suggestions) return;
        box.innerHTML = data.suggestions.map(s =>
            `<span onclick="document.getElementById('voiceInput').value='${s}'"
                  style="display:inline-block;margin:0.25rem;padding:0.3rem 0.7rem;
                         background:rgba(59,130,246,0.15);color:#93C5FD;border-radius:20px;
                         font-size:0.8rem;cursor:pointer;border:1px solid rgba(59,130,246,0.3);"
                  title="Click to use this query">
               ${s}
             </span>`).join('');
        box.style.display = 'block';
    } catch (e) { console.error('Suggestions error:', e); }
}

// ── Feedback ─────────────────────────────────────────────────
async function submitFeedback(reportId, rating, comment, category = 'general') {
    if (!rating || rating < 1 || rating > 5) { showNotification('Select a rating (1-5)', 'error'); return; }
    if (!comment || comment.trim().length < 5) { showNotification('Comment too short (min 5 chars)', 'error'); return; }
    try {
        showLoading(true);
        const res = await fetch(`${API_BASE}/api/feedback/submit`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ report_id: reportId, rating, comment, category })
        });
        if (!res.ok) throw new Error('Submit failed');
        showNotification('Feedback submitted! 🎉', 'success');
        resetFeedbackForm();
        loadReportFeedback(reportId);
    } catch (e) { showNotification('Feedback failed.', 'error'); }
    finally { showLoading(false); }
}

async function loadReportFeedback(reportId) {
    try {
        const res = await fetch(`${API_BASE}/api/feedback/report/${reportId}`);
        const data = await res.json();
        displayReportFeedback(data);
    } catch (e) { console.error('Feedback load error:', e); }
}

function displayReportFeedback(data) {
    const container = document.getElementById('feedbackList');
    if (!container) return;
    if (!data.feedbacks.length) { container.innerHTML = '<p style="color:#94A3B8;text-align:center;">No feedback yet.</p>'; return; }
    const avg = document.getElementById('averageRating');
    if (avg) avg.textContent = `${data.average_rating.toFixed(1)} ⭐`;
    container.innerHTML = data.feedbacks.map(f => `
        <div class="feedback-item">
            <div>${generateStars(f.rating)}</div>
            <p style="color:#CBD5E1;margin:0.4rem 0;">${escapeHtml(f.comment)}</p>
            <span style="color:#64748B;font-size:0.8rem;">📅 ${f.timestamp}</span>
        </div>`).join('');
}

function generateStars(r) { return Array.from({length:5},(_,i) => i<r ? '⭐' : '☆').join(''); }
function escapeHtml(t) { const d = document.createElement('div'); d.textContent = t; return d.innerHTML; }

function resetFeedbackForm() {
    const c = document.getElementById('feedbackComment'); if (c) c.value = '';
    const s = document.getElementById('feedbackCategory'); if (s) s.value = 'general';
    document.querySelectorAll('.star-rating .star').forEach(s => { s.classList.remove('selected'); s.textContent = '☆'; });
    window.currentRating = 0;
}

function setRating(r) {
    window.currentRating = r;
    document.querySelectorAll('.star-rating .star').forEach((s, i) => {
        s.classList.toggle('selected', i < r);
        s.textContent = i < r ? '⭐' : '☆';
    });
}

function initStarRating() {
    const container = document.querySelector('.star-rating');
    if (!container) return;
    window.currentRating = 0;
    for (let i = 1; i <= 5; i++) {
        const s = document.createElement('span');
        s.className = 'star'; s.textContent = '☆';
        s.onclick = () => setRating(i);
        s.onmouseover = () => document.querySelectorAll('.star-rating .star').forEach((x,j) => x.textContent = j<i?'⭐':'☆');
        container.appendChild(s);
    }
    container.onmouseleave = () => document.querySelectorAll('.star-rating .star').forEach((x,j) => x.textContent = j<window.currentRating?'⭐':'☆');
}

// ── Search / filter ──────────────────────────────────────────
function searchReports() {
    const term = (document.getElementById('searchInput')?.value || '').toLowerCase();
    document.querySelectorAll('#reportsTableBody tr').forEach(r => { r.style.display = r.textContent.toLowerCase().includes(term) ? '' : 'none'; });
}

function filterReports(status) {
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    event.target.classList.add('active');
    document.querySelectorAll('#reportsTableBody tr').forEach(r => {
        const badge = r.querySelector('.status-badge');
        r.style.display = (!badge || status === 'all' || badge.textContent.toLowerCase() === status) ? '' : 'none';
    });
}

// ── Utilities ────────────────────────────────────────────────
function showLoading(show) { const l = document.getElementById('loader'); if (l) l.style.display = show ? 'block' : 'none'; }

function showNotification(message, type = 'info') {
    const colors = { success:'#4CAF50', error:'#F44336', info:'#2196F3', warning:'#FF9800' };
    const n = document.createElement('div');
    n.textContent = message;
    n.style.cssText = `position:fixed;top:20px;right:20px;padding:0.9rem 1.4rem;
        background:${colors[type]||colors.info};color:white;border-radius:10px;
        box-shadow:0 4px 14px rgba(0,0,0,0.35);z-index:9999;font-size:0.9rem;
        animation:slideIn 0.3s ease;max-width:320px;word-break:break-word;`;
    document.body.appendChild(n);
    setTimeout(() => { n.style.animation = 'slideOut 0.3s ease'; setTimeout(() => n.remove(), 300); }, 3500);
}

function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) { const fn = document.getElementById('fileName'); if (fn) fn.textContent = file.name; }
}

// ── Init ─────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    initVoiceRecognition();

    const path = window.location.pathname;
    if (path.includes('reporthistory')) loadReportHistory();
    else if (path.includes('visualizations')) loadVisualizations();
    else if (path.includes('dashboard')) {
        loadDashboardStats();
        setInterval(loadDashboardStats, 30000);

        // If a report was previously uploaded, restore summary
        const savedId = localStorage.getItem('currentReportId');
        if (savedId) {
            fetch(`${API_BASE}/api/report/${savedId}`)
                .then(r => r.ok ? r.json() : null)
                .then(data => { if (data) displayReportSummary({ report_id: savedId, quality: data.quality || {}, metadata: data.metadata || {} }); })
                .catch(() => {});
            loadVoiceSuggestions(savedId);
        }
    }

    const fi = document.getElementById('fileInput');
    if (fi) fi.addEventListener('change', handleFileSelect);

    const ua = document.querySelector('.upload-area');
    if (ua) {
        ua.addEventListener('dragover',  e => { e.preventDefault(); ua.style.borderColor = 'var(--primary-blue)'; });
        ua.addEventListener('dragleave', e => { e.preventDefault(); ua.style.borderColor = 'var(--border-color)'; });
        ua.addEventListener('drop', e => {
            e.preventDefault(); ua.style.borderColor = 'var(--border-color)';
            if (e.dataTransfer.files.length && fi) { fi.files = e.dataTransfer.files; handleFileSelect({ target: fi }); }
        });
        ua.addEventListener('click', () => fi && fi.click());
    }

    // Enter key on voice input
    const vi = document.getElementById('voiceInput');
    if (vi) vi.addEventListener('keydown', e => { if (e.key === 'Enter') submitVoiceQuery(); });
});

// CSS animations
const _style = document.createElement('style');
_style.textContent = `
@keyframes slideIn  { from { transform:translateX(110%);opacity:0; } to { transform:translateX(0);opacity:1; } }
@keyframes slideOut { from { transform:translateX(0);opacity:1; } to { transform:translateX(110%);opacity:0; } }
`;
document.head.appendChild(_style);
