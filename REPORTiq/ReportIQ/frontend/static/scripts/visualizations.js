// visualizations.js - Enhanced Premium Version
document.addEventListener("DOMContentLoaded", async ()=>{
  const params = new URLSearchParams(window.location.search);
  const rid = params.get("report_id");
  const previews = document.getElementById("previews");
  const plotsDiv = document.getElementById("plots");
  const loadingState = document.getElementById("loadingState");
  const contentArea = document.getElementById("contentArea");

  if (!rid){
    if (loadingState) loadingState.style.display = 'none';
    if (contentArea) {
      contentArea.style.display = 'block';
      contentArea.innerHTML = `
        <div class="card empty">
          <div style="font-size: 64px; margin-bottom: 20px; opacity: 0.5;">📊</div>
          <h3>No Report Selected</h3>
          <p class="muted mt-8">Select a report from History or Dashboard to view its visualizations and charts</p>
          <div style="display: flex; gap: 12px; justify-content: center; margin-top: 24px;">
            <a href="/reporthistory" class="btn">
              <span>🕒</span>
              <span>Go to History</span>
            </a>
            <a href="/dashboard" class="btn secondary">
              <span>📊</span>
              <span>Dashboard</span>
            </a>
          </div>
        </div>
      `;
    }
    return;
  }

  try {
    // Show loading state
    if (loadingState) loadingState.style.display = 'block';
    if (contentArea) contentArea.style.display = 'none';

    // Load raw + cleaned preview frames
    if (previews){
      previews.innerHTML = `
        <div class="card" style="background: linear-gradient(135deg, rgba(99,102,241,0.06), rgba(99,102,241,0.03)); border-color: rgba(99,102,241,0.2);">
          <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
            <div style="font-size: 28px;">📄</div>
            <h4 style="color: var(--text-primary);">Raw Data Preview</h4>
          </div>
          <p class="muted" style="margin-bottom: 12px; font-size: 14px;">Original uploaded data before processing</p>
          <iframe class="preview-frame" 
                  src="/reports/${rid}/raw_data_preview.html" 
                  title="Raw data preview"
                  style="background: rgba(0,0,0,0.3);"></iframe>
        </div>
        <div class="card" style="background: linear-gradient(135deg, rgba(16,185,129,0.06), rgba(16,185,129,0.03)); border-color: rgba(16,185,129,0.2);">
          <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
            <div style="font-size: 28px;">✨</div>
            <h4 style="color: var(--text-primary);">Cleaned Data Preview</h4>
          </div>
          <p class="muted" style="margin-bottom: 12px; font-size: 14px;">Processed and cleaned data ready for analysis</p>
          <iframe class="preview-frame" 
                  src="/reports/${rid}/cleaned_data_preview.html"
                  title="Cleaned data preview"
                  style="background: rgba(0,0,0,0.3);"></iframe>
        </div>
      `;
    }

    // Fetch report metadata
    const res = await fetch(CONFIG.ENDPOINTS.REPORT(rid));
    
    if (!res.ok) {
      throw new Error(`Failed to load report: ${res.status}`);
    }
    
    const meta = await res.json();
    const plots = meta.plots || [];

    // Hide loading, show content
    if (loadingState) loadingState.style.display = 'none';
    if (contentArea) contentArea.style.display = 'block';

    if (plotsDiv) {
      if (plots.length === 0) {
        plotsDiv.innerHTML = `
          <div class="card empty" style="grid-column: 1/-1; background: linear-gradient(135deg, rgba(245,158,11,0.05), rgba(245,158,11,0.02)); border-color: rgba(245,158,11,0.2);">
            <div style="font-size: 64px; margin-bottom: 16px; opacity: 0.5;">📈</div>
            <h3>No Plots Generated</h3>
            <p class="muted mt-8">This report doesn't have any visualizations yet. Charts will be generated automatically during data processing.</p>
          </div>
        `;
      } else {
        plotsDiv.innerHTML = plots.map((p, index) => {
          const colors = [
            'rgba(99,102,241,0.2)',
            'rgba(6,182,212,0.2)',
            'rgba(16,185,129,0.2)',
            'rgba(245,158,11,0.2)'
          ];
          const borderColor = colors[index % colors.length];
          
          return `
            <div class="card" style="border-color: ${borderColor}; overflow: hidden; padding: 0;">
              <div style="padding: 16px; background: linear-gradient(135deg, ${borderColor}, transparent);">
                <h4 style="font-size: 14px; color: var(--text-primary); font-weight: 600;">${p.replace(/_/g, ' ').replace('.png', '')}</h4>
              </div>
              <img class="plot-img" 
                   src="/reports/${rid}/${p}" 
                   alt="${p}"
                   style="border-radius: 0; border: none; width: 100%; display: block;"
                   onerror="this.parentElement.innerHTML='<div style=padding:40px;text-align:center><p class=muted>❌ Failed to load chart</p></div>'">
            </div>
          `;
        }).join("");
      }
    }

  } catch (e){
    console.error("Failed to load report metadata:", e);
    
    if (loadingState) loadingState.style.display = 'none';
    
    if (contentArea) {
      contentArea.style.display = 'block';
      contentArea.innerHTML = `
        <div class="card empty">
          <div style="font-size: 64px; margin-bottom: 20px; opacity: 0.5;">❌</div>
          <h3>Failed to Load Visualizations</h3>
          <p class="muted mt-8">Unable to load report data. The report may not exist or there was a connection error.</p>
          <div style="display: flex; gap: 12px; justify-content: center; margin-top: 24px;">
            <button class="btn" onclick="window.location.reload()">
              <span>🔄</span>
              <span>Try Again</span>
            </button>
            <a href="/reporthistory" class="btn secondary">
              <span>🕒</span>
              <span>Back to History</span>
            </a>
          </div>
        </div>
      `;
    }
  }
});
