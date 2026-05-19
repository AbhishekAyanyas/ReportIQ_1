/* REPORTiq Frontend JavaScript */

const API_BASE = window.location.hostname === 'localhost' 
    ? 'http://localhost:8000/api'
    : '/api';

console.log('REPORTiq Frontend initialized. API Base:', API_BASE);

// DOM Elements
const voiceFileInput = document.getElementById('voiceFile');
const reportFileInput = document.getElementById('reportFile');
const uploadVoiceBtn = document.getElementById('uploadVoiceBtn');
const uploadReportBtn = document.getElementById('uploadReportBtn');
const responseOut = document.getElementById('responseOut');

// Voice Upload Handler
if (uploadVoiceBtn) {
    uploadVoiceBtn.addEventListener('click', async () => {
        if (!voiceFileInput.files.length) {
            showAlert('Please select a voice file', 'error');
            return;
        }

        const file = voiceFileInput.files[0];
        await uploadFile(file, 'voice', 'Voice');
    });
}

// Report Upload Handler
if (uploadReportBtn) {
    uploadReportBtn.addEventListener('click', async () => {
        if (!reportFileInput.files.length) {
            showAlert('Please select a report file', 'error');
            return;
        }

        const file = reportFileInput.files[0];
        await uploadFile(file, 'reports', 'Report');
    });
}

// Generic Upload Function
async function uploadFile(file, type, label) {
    try {
        // Show loading state
        setResponseOutput('Uploading ' + label.toLowerCase() + '...');
        
        const formData = new FormData();
        formData.append('file', file);

        const endpoint = type === 'voice' ? '/voice/upload' : '/reports/upload-report';
        const url = `${API_BASE}${endpoint}`;

        console.log('Uploading to:', url);

        const response = await fetch(url, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        
        if (data.status === 'success') {
            showAlert(`${label} uploaded successfully!`, 'success');
            setResponseOutput(JSON.stringify(data, null, 2));
            
            // Clear file input
            if (type === 'voice') {
                voiceFileInput.value = '';
            } else {
                reportFileInput.value = '';
            }
        } else {
            showAlert(`Error uploading ${label.toLowerCase()}`, 'error');
            setResponseOutput(JSON.stringify(data, null, 2));
        }
    } catch (error) {
        console.error('Upload error:', error);
        showAlert(`Error: ${error.message}`, 'error');
        setResponseOutput(`Error: ${error.message}`);
    }
}

// Drag and Drop Support
function setupDragAndDrop(input, dropArea) {
    if (!dropArea) return;

    dropArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropArea.classList.add('drag-over');
    });

    dropArea.addEventListener('dragleave', () => {
        dropArea.classList.remove('drag-over');
    });

    dropArea.addEventListener('drop', (e) => {
        e.preventDefault();
        dropArea.classList.remove('drag-over');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            input.files = files;
        }
    });
}

// Setup drag and drop if elements exist
const voiceDropArea = document.getElementById('voiceDropArea');
const reportDropArea = document.getElementById('reportDropArea');
setupDragAndDrop(voiceFileInput, voiceDropArea);
setupDragAndDrop(reportFileInput, reportDropArea);

// Helper Functions
function setResponseOutput(message) {
    if (responseOut) {
        responseOut.textContent = message;
    }
}

function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;
    
    const container = document.querySelector('.main-content') || document.body;
    container.insertBefore(alertDiv, container.firstChild);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// Check Backend Status on Load
async function checkBackendStatus() {
    try {
        const response = await fetch(`${API_BASE.replace('/api', '')}/health`);
        if (response.ok) {
            console.log('✓ Backend is online');
        }
    } catch (error) {
        console.warn('⚠ Backend may be offline:', error.message);
        showAlert('Backend connection status: Checking...', 'warning');
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    checkBackendStatus();
    console.log('Frontend ready');
});
