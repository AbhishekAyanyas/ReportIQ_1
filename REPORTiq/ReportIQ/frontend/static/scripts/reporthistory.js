// reporthistory.js - Enhanced Premium Version
document.addEventListener("DOMContentLoaded", async ()=>{
  const container = document.getElementById("historyCards");
  const loadingState = document.getElementById("loadingState");
  
  try {
    // Show loading
    if (loadingState) loadingState.style.display = 'block';
    
    const res = await fetch(CONFIG.ENDPOINTS.HISTORY);
    
    if (!res.ok) {
      throw new Error(`Failed to fetch history: ${res.status}`);
    }
    
    const json = await res.json();
    const history = json.history || json.reports || [];

    // Hide loading
    if (loadingState) loadingState.style.display = 'none';

    if (!history.length){
      container.innerHTML = `
        <div class="card empty" style="grid-column: 1/-1; background: linear-gradient(135deg, rgba(99,102,241,0.05), rgba(6,182,212,0.03)); border-color: rgba(99,102,241,0.2);">
          <div style="font-size: 80px; margin-bottom: 20px; opacity: 0.5; filter: drop-shadow(0 4px 12px rgba(99,102,241,0.3));">📭</div>
          <h3>No Reports Yet</h3>
          <p class="muted mt-8" style="max-width: 500px; margin-left: auto; margin-right: auto;">
            You haven't uploaded any datasets yet. Start your data analysis journey by uploading your first CSV or Excel file!
          </p>
          <a href="/" class="btn mt-16" style="padding: 14px 32px;">
            <span>📤</span>
            <span>Upload Your First Dataset</span>
          </a>
        </div>
      `;
      return;
    }

    // Define color schemes for variety
    const colorSchemes = [
      { bg: 'rgba(99,102,241,0.06)', border: 'rgba(99,102,241,0.2)', accent: '#6366f1' },
      { bg: 'rgba(6,182,212,0.06)', border: 'rgba(6,182,212,0.2)', accent: '#06b6d4' },
      { bg: 'rgba(16,185,129,0.06)', border: 'rgba(16,185,129,0.2)', accent: '#10b981' },
      { bg: 'rgba(245,158,11,0.06)', border: 'rgba(245,158,11,0.2)', accent: '#f59e0b' }
    ];

    // Display history cards (most recent first)
    container.innerHTML = history.slice().reverse().map((h, index) => {
      const date = h.timestamp ? new Date(h.timestamp).toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      }) : 'Unknown date';
      
      const fileExt = h.filename.split('.').pop().toUpperCase();
      const scheme = colorSchemes[index % colorSchemes.length];
      
      return `
        <div class="card history-card" style="background: linear-gradient(135deg, ${scheme.bg}, ${scheme.bg}00); border-color: ${scheme.border};">
          <div style="flex: 1;">
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
              <div style="font-size: 24px;">📄</div>
              <strong style="font-size: 16px; color: var(--text-primary);">${h.filename}</strong>
            </div>
            <div style="display: flex; align-items: center; gap: 8px; margin-top: 8px;">
              <span class="chip" style="background: ${scheme.bg}; border-color: ${scheme.border}; color: ${scheme.accent}; font-size: 11px;">
                ${h.report_id}
              </span>
              <span class="chip" style="background: ${scheme.bg}; border-color: ${scheme.border}; color: ${scheme.accent}; font-size: 11px;">
                ${fileExt}
              </span>
            </div>
            <small class="muted" style="display: block; margin-top: 8px;">
              <span style="opacity: 0.7;">🕒</span> ${date}
            </small>
          </div>
          <div style="text-align: right; display: flex; flex-direction: column; gap: 10px; align-items: flex-end;">
            <a class="btn" href="/visualizations?report_id=${h.report_id}" style="padding: 10px 20px; font-size: 14px;">
              <span>📊</span>
              <span>View Report</span>
            </a>
          </div>
        </div>
      `;
    }).join("");

    // Add animation to cards
    const cards = container.querySelectorAll('.history-card');
    cards.forEach((card, index) => {
      card.style.animation = `fadeIn 0.4s ease ${index * 0.05}s both`;
    });

  } catch(e){
    console.error("Failed to load history:", e);
    
    // Hide loading
    if (loadingState) loadingState.style.display = 'none';
    
    container.innerHTML = `
      <div class="card empty" style="grid-column: 1/-1; background: linear-gradient(135deg, rgba(239,68,68,0.05), rgba(239,68,68,0.02)); border-color: rgba(239,68,68,0.2);">
        <div style="font-size: 64px; margin-bottom: 20px; opacity: 0.5;">❌</div>
        <h3>Failed to Load History</h3>
        <p class="muted mt-8">There was an error loading your report history. Please check your connection and try again.</p>
        <div style="display: flex; gap: 12px; justify-content: center; margin-top: 24px;">
          <button class="btn" onclick="window.location.reload()">
            <span>🔄</span>
            <span>Refresh Page</span>
          </button>
          <a href="/" class="btn secondary">
            <span>🏠</span>
            <span>Go Home</span>
          </a>
        </div>
      </div>
    `;
  }
});
