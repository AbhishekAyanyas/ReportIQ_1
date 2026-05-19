// voice.js - Voice Query Functionality
document.addEventListener("DOMContentLoaded", () => {
  
  // Check if browser supports Speech Recognition
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  
  if (!SpeechRecognition) {
    console.warn("Speech Recognition not supported in this browser");
    const voiceBtn = document.getElementById('voiceBtn');
    if (voiceBtn) {
      voiceBtn.disabled = true;
      voiceBtn.innerHTML = '<span>❌</span><span>Voice not supported in this browser</span>';
    }
    return;
  }

  const recognition = new SpeechRecognition();
  recognition.continuous = false;
  recognition.lang = 'en-US';
  recognition.interimResults = false;
  recognition.maxAlternatives = 1;

  const voiceBtn = document.getElementById('voiceBtn');
  const stopVoiceBtn = document.getElementById('stopVoiceBtn');
  const voiceIcon = document.getElementById('voiceIcon');
  const voiceText = document.getElementById('voiceText');
  const voiceTranscript = document.getElementById('voiceTranscript');
  const transcriptText = document.getElementById('transcriptText');
  const voiceResponse = document.getElementById('voiceResponse');
  const responseText = document.getElementById('responseText');

  let isListening = false;

  // Start voice recognition
  voiceBtn?.addEventListener('click', () => {
    if (!isListening) {
      startListening();
    }
  });

  // Stop voice recognition
  stopVoiceBtn?.addEventListener('click', () => {
    if (isListening) {
      stopListening();
    }
  });

  function startListening() {
    try {
      recognition.start();
      isListening = true;
      
      // Update UI
      if (voiceBtn) {
        voiceBtn.style.background = 'linear-gradient(135deg, #ef4444, #f87171)';
        voiceBtn.style.animation = 'pulse 1.5s infinite';
      }
      if (voiceIcon) voiceIcon.textContent = '🎙️';
      if (voiceText) voiceText.textContent = 'Listening...';
      if (stopVoiceBtn) {
        stopVoiceBtn.style.display = 'inline-flex';
      }
      
      // Hide previous results
      if (voiceTranscript) voiceTranscript.style.display = 'none';
      if (voiceResponse) voiceResponse.style.display = 'none';
      
    } catch (error) {
      console.error('Error starting recognition:', error);
      showError('Failed to start voice recognition');
    }
  }

  function stopListening() {
    recognition.stop();
    resetUI();
  }

  function resetUI() {
    isListening = false;
    
    if (voiceBtn) {
      voiceBtn.style.background = 'linear-gradient(135deg, #8b5cf6, #a855f7)';
      voiceBtn.style.animation = 'none';
    }
    if (voiceIcon) voiceIcon.textContent = '🎤';
    if (voiceText) voiceText.textContent = 'Start Voice Query';
    if (stopVoiceBtn) {
      stopVoiceBtn.style.display = 'none';
    }
  }

  // Recognition event handlers
  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    console.log('Transcript:', transcript);
    
    // Show transcript
    if (transcriptText) transcriptText.textContent = transcript;
    if (voiceTranscript) voiceTranscript.style.display = 'block';
    
    // Process the query
    processVoiceQuery(transcript);
  };

  recognition.onerror = (event) => {
    console.error('Speech recognition error:', event.error);
    
    let errorMessage = 'Voice recognition error';
    switch(event.error) {
      case 'no-speech':
        errorMessage = 'No speech detected. Please try again.';
        break;
      case 'audio-capture':
        errorMessage = 'Microphone not accessible. Please check permissions.';
        break;
      case 'not-allowed':
        errorMessage = 'Microphone permission denied. Please enable it in browser settings.';
        break;
      default:
        errorMessage = `Error: ${event.error}`;
    }
    
    showError(errorMessage);
    resetUI();
  };

  recognition.onend = () => {
    resetUI();
  };

  // Process voice query
  async function processVoiceQuery(query) {
    const lowerQuery = query.toLowerCase();
    
    // Show processing state
    if (responseText) {
      responseText.innerHTML = '<div class="loading" style="display: inline-block; width: 20px; height: 20px; border-width: 2px;"></div> Processing your query...';
    }
    if (voiceResponse) voiceResponse.style.display = 'block';
    
    // Simulate processing delay
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    let response = generateResponse(lowerQuery);
    
    // Show response
    if (responseText) {
      responseText.textContent = response;
      
      // Text-to-speech
      speakResponse(response);
    }
  }

  // Generate intelligent responses based on query
  function generateResponse(query) {
    // Revenue related
    if (query.includes('revenue') || query.includes('sales') || query.includes('income')) {
      return "Based on your latest report, total revenue is $1.2M with 8% quarter-over-quarter growth. Top performing category is Electronics with $450K in sales.";
    }
    
    // Performance related
    if (query.includes('performance') || query.includes('metrics')) {
      return "Overall performance increased by 15%. Processing speed is at 92%, accuracy is 98%, and user satisfaction reached 95%. All metrics are above target.";
    }
    
    // Top products/items
    if (query.includes('top') && (query.includes('product') || query.includes('item') || query.includes('performing'))) {
      return "Top 3 performing products are: 1) Wireless Headphones ($125K), 2) Smart Watch ($98K), 3) Laptop Accessories ($76K). These account for 65% of total sales.";
    }
    
    // Customer related
    if (query.includes('customer') && (query.includes('satisfaction') || query.includes('feedback'))) {
      return "Customer satisfaction is at 92%, up 5% from last quarter. Positive feedback increased by 18%. Main praise points are fast processing and accurate insights.";
    }
    
    // Summary/overview
    if (query.includes('summary') || query.includes('overview') || query.includes('report')) {
      return "Here's your summary: You have 12 total reports analyzed. Most common format is CSV. Data cleaning success rate is 95% with 144 errors automatically fixed. Performance metrics are excellent across all categories.";
    }
    
    // Charts/visualization
    if (query.includes('chart') || query.includes('graph') || query.includes('visual')) {
      return "Your dashboard shows 5 visualizations including performance trends, revenue growth, and customer satisfaction metrics. All charts are available in the Visualizations section.";
    }
    
    // Upload related
    if (query.includes('upload') || query.includes('file') || query.includes('dataset')) {
      return "You can upload CSV or Excel files up to 50MB. Simply drag and drop your file or click to browse. Processing typically takes 30-60 seconds depending on file size.";
    }
    
    // Error/issue related
    if (query.includes('error') || query.includes('problem') || query.includes('issue')) {
      return "Your latest reports show 144 errors were automatically fixed during data cleaning. Common issues include missing values, duplicate entries, and formatting inconsistencies. All have been resolved.";
    }
    
    // Help/how to
    if (query.includes('help') || query.includes('how')) {
      return "I can help you with: checking revenue, viewing performance metrics, getting summaries, finding top products, or navigating the dashboard. Just ask me a question!";
    }
    
    // Default response
    return "I understood your query about: " + query + ". However, I need more specific data to provide accurate insights. Try asking about revenue, performance, top products, or request a summary report.";
  }

  // Text-to-speech
  function speakResponse(text) {
    if ('speechSynthesis' in window) {
      // Cancel any ongoing speech
      window.speechSynthesis.cancel();
      
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 0.9;
      utterance.pitch = 1;
      utterance.volume = 1;
      
      // Get available voices
      const voices = window.speechSynthesis.getVoices();
      // Try to use a good English voice
      const preferredVoice = voices.find(voice => 
        voice.lang.startsWith('en') && 
        (voice.name.includes('Google') || voice.name.includes('Microsoft'))
      ) || voices.find(voice => voice.lang.startsWith('en'));
      
      if (preferredVoice) {
        utterance.voice = preferredVoice;
      }
      
      window.speechSynthesis.speak(utterance);
    }
  }

  // Show error message
  function showError(message) {
    if (responseText) {
      responseText.textContent = message;
      responseText.style.color = 'var(--danger)';
    }
    if (voiceResponse) {
      voiceResponse.style.display = 'block';
      voiceResponse.style.borderColor = 'rgba(239,68,68,0.3)';
      voiceResponse.style.background = 'rgba(239,68,68,0.05)';
    }
    
    // Reset after 3 seconds
    setTimeout(() => {
      if (voiceResponse) voiceResponse.style.display = 'none';
    }, 3000);
  }

  // Load voices (for speech synthesis)
  if ('speechSynthesis' in window) {
    window.speechSynthesis.onvoiceschanged = () => {
      window.speechSynthesis.getVoices();
    };
  }
});

// Global function for suggestion buttons
function askVoiceQuery(query) {
  const transcriptText = document.getElementById('transcriptText');
  const voiceTranscript = document.getElementById('voiceTranscript');
  
  if (transcriptText) transcriptText.textContent = query;
  if (voiceTranscript) voiceTranscript.style.display = 'block';
  
  // Process the query
  processVoiceQueryDirect(query);
}

async function processVoiceQueryDirect(query) {
  const voiceResponse = document.getElementById('voiceResponse');
  const responseText = document.getElementById('responseText');
  
  if (responseText) {
    responseText.innerHTML = '<div class="loading" style="display: inline-block; width: 20px; height: 20px; border-width: 2px;"></div> Processing...';
    responseText.style.color = 'var(--text-primary)';
  }
  if (voiceResponse) {
    voiceResponse.style.display = 'block';
    voiceResponse.style.borderColor = 'rgba(99,102,241,0.2)';
    voiceResponse.style.background = 'rgba(99,102,241,0.05)';
  }
  
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  const lowerQuery = query.toLowerCase();
  let response = generateResponseDirect(lowerQuery);
  
  if (responseText) {
    responseText.textContent = response;
  }
  
  // Text-to-speech
  if ('speechSynthesis' in window) {
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(response);
    utterance.rate = 0.9;
    window.speechSynthesis.speak(utterance);
  }
}

function generateResponseDirect(query) {
  if (query.includes('revenue')) {
    return "Total revenue is $1.2M with 8% quarter-over-quarter growth.";
  }
  if (query.includes('top') && query.includes('product')) {
    return "Top products: Wireless Headphones ($125K), Smart Watch ($98K), Laptop Accessories ($76K).";
  }
  if (query.includes('summary')) {
    return "You have 12 reports with 95% cleaning success rate and excellent performance metrics.";
  }
  return "Processing your query: " + query;
}

// Add pulse animation for recording button
const style = document.createElement('style');
style.textContent = `
  @keyframes pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.05); }
  }
`;
document.head.appendChild(style);
