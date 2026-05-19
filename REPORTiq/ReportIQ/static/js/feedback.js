// ========== FEEDBACK SYSTEM ==========

// Global variable for current rating
window.currentRating = 0;

// Submit Feedback
async function submitFeedback(reportId) {
    try {
        const rating = window.currentRating;
        const comment = document.getElementById('feedbackComment')?.value || '';
        const category = document.getElementById('feedbackCategory')?.value || 'general';
        
        if (!rating || rating < 1 || rating > 5) {
            showNotification('Please select a rating (1-5 stars)', 'error');
            return;
        }
        
        if (!comment || comment.trim().length < 5) {
            showNotification('Please provide a comment (minimum 5 characters)', 'error');
            return;
        }
        
        showLoading(true);
        
        const response = await fetch(`${API_BASE}/api/feedback/submit`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                report_id: reportId,
                rating: rating,
                comment: comment,
                category: category
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to submit feedback');
        }
        
        const data = await response.json();
        
        showNotification('Feedback submitted successfully! Thank you! 🎉', 'success');
        
        // Reset form
        resetFeedbackForm();
        
        // Reload feedback for this report
        loadReportFeedback(reportId);
        
        return data;
        
    } catch (error) {
        console.error('Feedback submission error:', error);
        showNotification('Failed to submit feedback. Please try again.', 'error');
    } finally {
        showLoading(false);
    }
}

// Load Feedback for a Report
async function loadReportFeedback(reportId) {
    try {
        const response = await fetch(`${API_BASE}/api/feedback/report/${reportId}`);
        const data = await response.json();
        
        displayReportFeedback(data);
        
    } catch (error) {
        console.error('Error loading feedback:', error);
    }
}

// Display Report Feedback
function displayReportFeedback(data) {
    const container = document.getElementById('feedbackList');
    if (!container) return;
    
    if (data.feedbacks.length === 0) {
        container.innerHTML = '<p class="text-secondary text-center">No feedback yet. Be the first to share your thoughts!</p>';
        return;
    }
    
    // Update average rating
    const avgRatingElement = document.getElementById('averageRating');
    if (avgRatingElement) {
        avgRatingElement.innerHTML = `${data.average_rating.toFixed(1)} ⭐ <span class="text-secondary">(${data.total_feedbacks} reviews)</span>`;
    }
    
    // Display feedbacks
    container.innerHTML = data.feedbacks.map(feedback => `
        <div class="feedback-item">
            <div class="feedback-header">
                <div class="feedback-rating">
                    ${generateStars(feedback.rating)}
                </div>
                <span class="feedback-category badge-${feedback.category}">${feedback.category}</span>
            </div>
            <p class="feedback-comment">${escapeHtml(feedback.comment)}</p>
            <div class="feedback-footer">
                <span class="feedback-time">📅 ${feedback.timestamp}</span>
            </div>
        </div>
    `).join('');
}

// Generate Star Rating HTML
function generateStars(rating) {
    let stars = '';
    for (let i = 1; i <= 5; i++) {
        stars += i <= rating ? '⭐' : '☆';
    }
    return stars;
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Reset Feedback Form
function resetFeedbackForm() {
    const commentBox = document.getElementById('feedbackComment');
    const categorySelect = document.getElementById('feedbackCategory');
    
    if (commentBox) commentBox.value = '';
    if (categorySelect) categorySelect.value = 'general';
    
    // Reset star selection
    const stars = document.querySelectorAll('.star-rating .star');
    stars.forEach(star => {
        star.classList.remove('selected');
        star.textContent = '☆';
    });
    
    // Reset global rating
    window.currentRating = 0;
}

// Star Rating Click Handler
function setRating(rating) {
    window.currentRating = rating;
    
    const stars = document.querySelectorAll('.star-rating .star');
    stars.forEach((star, index) => {
        if (index < rating) {
            star.classList.add('selected');
            star.textContent = '⭐';
        } else {
            star.classList.remove('selected');
            star.textContent = '☆';
        }
    });
}

// Initialize Star Rating
function initStarRating() {
    const starContainer = document.querySelector('.star-rating');
    if (!starContainer) return;
    
    window.currentRating = 0;
    starContainer.innerHTML = '';
    
    for (let i = 1; i <= 5; i++) {
        const star = document.createElement('span');
        star.className = 'star';
        star.textContent = '☆';
        star.onclick = () => setRating(i);
        star.onmouseover = () => {
            // Highlight on hover
            const stars = starContainer.querySelectorAll('.star');
            stars.forEach((s, index) => {
                s.textContent = index < i ? '⭐' : '☆';
            });
        };
        starContainer.appendChild(star);
    }
    
    // Reset stars on mouse leave
    starContainer.onmouseleave = () => {
        const stars = starContainer.querySelectorAll('.star');
        stars.forEach((star, index) => {
            star.textContent = index < window.currentRating ? '⭐' : '☆';
        });
    };
}

// Toggle Feedback Section
function toggleFeedbackSection() {
    const section = document.getElementById('feedbackSection');
    if (section) {
        section.style.display = section.style.display === 'none' ? 'block' : 'none';
    }
}
