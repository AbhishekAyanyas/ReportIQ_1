// feedback.js - Feedback System
document.addEventListener("DOMContentLoaded", () => {
  
  let selectedRating = 0;
  let selectedFeatures = [];
  
  const stars = document.querySelectorAll('.star');
  const ratingText = document.getElementById('ratingText');
  const feedbackTags = document.querySelectorAll('.feedback-tag');
  const submitBtn = document.getElementById('submitFeedback');
  const feedbackMessage = document.getElementById('feedbackMessage');
  const feedbackSuccess = document.getElementById('feedbackSuccess');
  const feedbackForm = document.getElementById('feedbackForm');

  // Rating system
  stars.forEach(star => {
    star.style.cursor = 'pointer';
    star.style.transition = 'all 0.2s';
    star.style.filter = 'grayscale(100%)';
    star.style.opacity = '0.4';
    
    star.addEventListener('mouseenter', function() {
      const rating = parseInt(this.dataset.rating);
      highlightStars(rating);
    });
    
    star.addEventListener('click', function() {
      selectedRating = parseInt(this.dataset.rating);
      highlightStars(selectedRating);
      updateRatingText(selectedRating);
    });
  });

  // Reset stars on mouse leave from container
  const ratingContainer = document.getElementById('ratingStars');
  ratingContainer?.addEventListener('mouseleave', () => {
    if (selectedRating > 0) {
      highlightStars(selectedRating);
    } else {
      resetStars();
    }
  });

  function highlightStars(rating) {
    stars.forEach((star, index) => {
      if (index < rating) {
        star.style.filter = 'grayscale(0%)';
        star.style.opacity = '1';
        star.style.transform = 'scale(1.2)';
      } else {
        star.style.filter = 'grayscale(100%)';
        star.style.opacity = '0.4';
        star.style.transform = 'scale(1)';
      }
    });
  }

  function resetStars() {
    stars.forEach(star => {
      star.style.filter = 'grayscale(100%)';
      star.style.opacity = '0.4';
      star.style.transform = 'scale(1)';
    });
  }

  function updateRatingText(rating) {
    const texts = {
      1: '😞 Poor - We need to improve',
      2: '😐 Fair - Could be better',
      3: '🙂 Good - Pretty satisfied',
      4: '😊 Very Good - Really liked it',
      5: '🤩 Excellent - Loved it!'
    };
    if (ratingText) {
      ratingText.textContent = texts[rating] || '';
      ratingText.style.color = rating >= 4 ? 'var(--success)' : rating >= 3 ? 'var(--warning)' : 'var(--danger)';
      ratingText.style.fontWeight = '600';
    }
  }

  // Feature tags
  feedbackTags.forEach(tag => {
    tag.style.cursor = 'pointer';
    
    tag.addEventListener('click', function() {
      const feature = this.dataset.feature;
      
      if (selectedFeatures.includes(feature)) {
        // Deselect
        selectedFeatures = selectedFeatures.filter(f => f !== feature);
        this.style.background = 'rgba(236,72,153,0.1)';
        this.style.borderColor = 'rgba(236,72,153,0.3)';
        this.style.color = 'var(--text-secondary)';
      } else {
        // Select
        selectedFeatures.push(feature);
        this.style.background = 'rgba(236,72,153,0.3)';
        this.style.borderColor = 'rgba(236,72,153,0.5)';
        this.style.color = '#ec4899';
        this.style.transform = 'scale(1.05)';
        
        setTimeout(() => {
          this.style.transform = 'scale(1)';
        }, 200);
      }
    });
  });

  // Submit feedback
  submitBtn?.addEventListener('click', async () => {
    // Validation
    if (selectedRating === 0) {
      alert('⚠️ Please select a rating before submitting');
      return;
    }

    // Disable button and show loading
    submitBtn.disabled = true;
    submitBtn.innerHTML = `
      <div class="loading" style="width: 16px; height: 16px; border-width: 2px;"></div>
      <span>Submitting...</span>
    `;

    // Prepare feedback data
    const feedbackData = {
      rating: selectedRating,
      features: selectedFeatures,
      message: feedbackMessage?.value || '',
      timestamp: new Date().toISOString(),
      page: 'dashboard'
    };

    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Here you would normally send to your backend:
      // const response = await fetch('/api/feedback', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify(feedbackData)
      // });

      // Log to console for now
      console.log('Feedback submitted:', feedbackData);
      
      // Show success message
      if (feedbackSuccess) {
        feedbackSuccess.style.display = 'block';
      }
      
      // Hide form
      if (feedbackForm) {
        feedbackForm.style.opacity = '0.5';
        feedbackForm.style.pointerEvents = 'none';
      }
      
      // Reset after 3 seconds
      setTimeout(() => {
        resetFeedbackForm();
      }, 3000);
      
    } catch (error) {
      console.error('Error submitting feedback:', error);
      alert('❌ Failed to submit feedback. Please try again.');
      
      // Re-enable button
      submitBtn.disabled = false;
      submitBtn.innerHTML = `
        <span>💬</span>
        <span>Submit Feedback</span>
      `;
    }
  });

  function resetFeedbackForm() {
    // Reset rating
    selectedRating = 0;
    resetStars();
    if (ratingText) ratingText.textContent = '';
    
    // Reset features
    selectedFeatures = [];
    feedbackTags.forEach(tag => {
      tag.style.background = 'rgba(236,72,153,0.1)';
      tag.style.borderColor = 'rgba(236,72,153,0.3)';
      tag.style.color = 'var(--text-secondary)';
    });
    
    // Reset message
    if (feedbackMessage) feedbackMessage.value = '';
    
    // Reset success message
    if (feedbackSuccess) feedbackSuccess.style.display = 'none';
    
    // Re-enable form
    if (feedbackForm) {
      feedbackForm.style.opacity = '1';
      feedbackForm.style.pointerEvents = 'auto';
    }
    
    // Reset button
    if (submitBtn) {
      submitBtn.disabled = false;
      submitBtn.innerHTML = `
        <span>💬</span>
        <span>Submit Feedback</span>
      `;
    }
  }

  // Store feedback locally for demo
  function storeFeedbackLocally(data) {
    try {
      const feedbacks = JSON.parse(localStorage.getItem('reportiq_feedback') || '[]');
      feedbacks.push(data);
      localStorage.setItem('reportiq_feedback', JSON.stringify(feedbacks));
    } catch (e) {
      console.error('Failed to store feedback locally:', e);
    }
  }
});
