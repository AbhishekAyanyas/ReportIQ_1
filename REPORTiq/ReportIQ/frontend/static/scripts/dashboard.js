// dashboard.js - Enhanced Premium Version
document.addEventListener("DOMContentLoaded", ()=>{

  // Elements
  const fileInput = document.querySelector("#fileInput");
  const uploadNow = document.querySelector("#uploadNow");
  const uploadMessage = document.querySelector("#uploadMessage");
  const uploaderBox = document.querySelector("#uploader");
  const recentReportsBody = document.querySelector("#recent_reports");
  const tableLoading = document.querySelector("#tableLoading");
  const recentTable = document.querySelector("#recentTable");
  const noReports = document.querySelector("#noReports");

  // Drag & Drop handlers with visual feedback
  if (uploaderBox) {
    uploaderBox.addEventListener("dragover", (e)=>{
      e.preventDefault();
      uploaderBox.classList.add("dragover");
    });

    uploaderBox.addEventListener("dragleave", ()=>{
      uploaderBox.classList.remove("dragover");
    });

    uploaderBox.addEventListener("drop", (e)=>{
      e.preventDefault();
      uploaderBox.classList.remove("dragover");
      const files = e.dataTransfer.files;
      if (files.length > 0) {
        fileInput.files = files;
        showMessage(`✓ Selected: ${files[0].name}`, "success");
      }
    });
  }

  // Message display helper
  function showMessage(text, type = "info") {
    if (!uploadMessage) return;
    uploadMessage.innerText = text;
    
    const colors = {
      success: "#10b981",
      error: "#ef4444",
      info: "#60a5fa",
      warning: "#f59e0b"
    };
    
    uploadMessage.style.color = colors[type] || colors.info;
  }

  // Load history and fill dashboard stats
  async function loadHistory() {
    if (!recentReportsBody) return;
    
    try {
      const res = await fetch(CONFIG.ENDPOINTS.HISTORY);
      if (!res.ok) throw new Error("History fetch failed");
      const json = await res.json();
      const history = json.history || json.reports || [];

      // Hide loading
      if (tableLoading) tableLoading.style.display = 'none';
      
      if (history.length === 0) {
        if (noReports) noReports.style.display = 'block';
        if (recentTable) recentTable.style.display = 'none';
      } else {
        if (noReports) noReports.style.display = 'none';
        if (recentTable) recentTable.style.display = 'table';

        // Fill recent table (latest 8)
        recentReportsBody.innerHTML = "";
        history.slice().reverse().slice(0,8).forEach(h=>{
          const date = h.timestamp ? new Date(h.timestamp).toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric'
          }) : '—';
          
          const tr = document.createElement("tr");
          tr.innerHTML = `
            <td><span class="chip" style="font-size: 11px;">${h.report_id}</span></td>
            <td><strong style="color: var(--text-primary);">📄 ${h.filename}</strong></td>
            <td>${date}</td>
            <td><a href="/visualizations?report_id=${h.report_id}" style="display: inline-flex; align-items: center; gap: 6px;">View Details <span style="font-size: 12px;">→</span></a></td>
          `;
          recentReportsBody.appendChild(tr);
        });
      }

      // Populate top stats
      document.getElementById("totalReports").innerText = history.length || 0;
      
      // Calculate most common file type
      const types = history.map(h => {
        const ext = h.filename.split('.').pop().toUpperCase();
        return ext;
      });
      
      const typeCount = types.reduce((acc, type) => {
        acc[type] = (acc[type] || 0) + 1;
        return acc;
      }, {});
      
      const mostType = Object.keys(typeCount).length > 0 
        ? Object.entries(typeCount).sort((a,b) => b[1] - a[1])[0][0]
        : "—";
      
      document.getElementById("mostType").innerText = mostType;
      document.getElementById("cleanPercent").innerText = history.length > 0 ? "95%" : "—";
      document.getElementById("errorsFixed").innerText = history.length > 0 ? Math.floor(history.length * 12) : "—";

    } catch(e){
      console.warn("Failed to load history", e);
      if (tableLoading) {
        tableLoading.innerHTML = `
          <div style="padding: 20px; text-align: center;">
            <p style="color: var(--danger); margin-bottom: 12px;">❌ Failed to load reports</p>
            <button class="btn secondary" onclick="window.location.reload()">Retry</button>
          </div>
        `;
      }
    }
  }

  // Enhanced Chart with gradient and styling
  function drawMiniChart(){
    const ctx = document.getElementById("miniChart");
    if (!ctx || typeof Chart === 'undefined') {
      console.warn("Chart.js not loaded or canvas not found");
      return;
    }
    
    try {
      // Create gradient for the chart
      const gradient = ctx.getContext('2d').createLinearGradient(0, 0, 0, 400);
      gradient.addColorStop(0, 'rgba(99, 102, 241, 0.4)');
      gradient.addColorStop(1, 'rgba(6, 182, 212, 0.05)');
      
      new Chart(ctx, {
        type: 'line',
        data: {
          labels: ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
          datasets: [{
            label: "Reports Uploaded",
            data: [2, 3, 4, 6, 7, 8, 5],
            borderColor: '#6366f1',
            backgroundColor: gradient,
            tension: 0.4,
            fill: true,
            pointRadius: 5,
            pointHoverRadius: 8,
            pointBackgroundColor: '#6366f1',
            pointBorderColor: '#ffffff',
            pointBorderWidth: 2,
            pointHoverBackgroundColor: '#818cf8',
            pointHoverBorderColor: '#ffffff',
            pointHoverBorderWidth: 3,
            borderWidth: 3
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: true,
          interaction: {
            intersect: false,
            mode: 'index'
          },
          plugins: {
            legend: {
              display: true,
              position: 'top',
              labels: {
                color: '#cbd5e1',
                font: {
                  size: 13,
                  weight: '600'
                },
                padding: 20,
                usePointStyle: true
              }
            },
            tooltip: {
              backgroundColor: 'rgba(15, 20, 35, 0.95)',
              titleColor: '#f8fafc',
              bodyColor: '#cbd5e1',
              borderColor: 'rgba(99, 102, 241, 0.3)',
              borderWidth: 1,
              padding: 12,
              displayColors: true,
              callbacks: {
                label: function(context) {
                  return ` ${context.parsed.y} reports`;
                }
              }
            }
          },
          scales: {
            y: {
              beginAtZero: true,
              grid: {
                color: 'rgba(255, 255, 255, 0.05)',
                drawBorder: false
              },
              ticks: {
                color: '#94a3b8',
                font: {
                  size: 12
                },
                padding: 10
              }
            },
            x: {
              grid: {
                color: 'rgba(255, 255, 255, 0.03)',
                drawBorder: false
              },
              ticks: {
                color: '#94a3b8',
                font: {
                  size: 12
                },
                padding: 10
              }
            }
          }
        }
      });
    } catch(e) {
      console.error("Failed to draw chart:", e);
    }
  }

  // Upload file with enhanced feedback
  async function uploadFile(file){
    if (!file) return;
    
    // Validate file type
    const validTypes = ['.csv', '.xls', '.xlsx'];
    const fileName = file.name.toLowerCase();
    const isValid = validTypes.some(type => fileName.endsWith(type));
    
    if (!isValid) {
      showMessage("❌ Please upload a CSV or Excel file", "error");
      return;
    }
    
    if (file.size > CONFIG.MAX_FILE_SIZE_MB * 1024 * 1024){
      showMessage(`❌ File too large (max ${CONFIG.MAX_FILE_SIZE_MB}MB)`, "error");
      return;
    }
    
    showMessage("⏳ Uploading...", "info");
    
    if (uploadNow) {
      uploadNow.disabled = true;
      uploadNow.innerHTML = `
        <div class="loading" style="width: 16px; height: 16px; border-width: 2px;"></div>
        <span>Uploading...</span>
      `;
    }

    const fd = new FormData();
    fd.append("file", file);

    try {
      const res = await fetch(CONFIG.ENDPOINTS.UPLOAD, {
        method: "POST",
        body: fd
      });
      
      if (!res.ok) throw new Error(`Upload failed: ${res.status}`);
      
      const json = await res.json();
      showMessage("✓ Upload complete! Processing data...", "success");
      
      // Reload history after successful upload
      setTimeout(async () => {
        await loadHistory();
        showMessage("✨ Ready! View results in Dashboard or Visualizations", "success");
        
        // Reset file input
        if (fileInput) fileInput.value = '';
      }, 1500);
      
    } catch(err){
      console.error("Upload error:", err);
      showMessage("✗ Upload failed. Please try again.", "error");
    } finally {
      if (uploadNow) {
        uploadNow.disabled = false;
        uploadNow.innerHTML = `
          <span>✨</span>
          <span>Upload Now</span>
        `;
      }
    }
  }

  // Wire file input change event
  fileInput?.addEventListener("change", (e)=>{
    const f = e.target.files[0];
    if (f){
      showMessage(`✓ Selected: ${f.name}`, "success");
    }
  });

  // Wire upload button
  uploadNow?.addEventListener("click", ()=>{
    const f = fileInput?.files?.[0];
    if (!f) {
      showMessage("⚠️ Please select a file first", "warning");
      return;
    }
    uploadFile(f);
  });

  // Initialize
  loadHistory();
  
  // Delay chart drawing to ensure Chart.js is loaded
  setTimeout(drawMiniChart, 100);

});
