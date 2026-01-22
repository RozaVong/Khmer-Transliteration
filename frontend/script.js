// Configuration
const API_BASE_URL = (() => {
    // Detect environment and set appropriate API URL
    const hostname = window.location.hostname;
    const port = window.location.port;
    
    console.log(`📍 Detected: hostname=${hostname}, port=${port}`);
    
    if (hostname === 'localhost' && port === '3000') {
        // Local development with Docker
        return 'http://localhost:8001/api/v1';
    } else if (hostname === 'backend' || hostname.includes('backend')) {
        // Docker internal network
        return 'http://backend:8001/api/v1';
    } else {
        // Production or Nginx proxy
        return '/api/v1';
    }
})();

console.log(`🌐 Using API URL: ${API_BASE_URL}`);

let currentPredictionId = null;

// DOM Elements
const input = document.getElementById('input');
const output = document.getElementById('output');
const translateBtn = document.getElementById('translateBtn');
const clearBtn = document.getElementById('clearBtn');
const loading = document.getElementById('loading');
const progressText = document.getElementById('progressText');
const suggestionChips = document.querySelectorAll('.suggestion-chip');
const statusIndicator = document.getElementById('statusIndicator');
const detailsSection = document.getElementById('detailsSection');
const confidenceValue = document.getElementById('confidenceValue');
const wordCountValue = document.getElementById('wordCountValue');
const predictionId = document.getElementById('predictionId');
const breakdownContainer = document.getElementById('breakdownContainer');
const feedbackSection = document.getElementById('feedbackSection');
const ratingStars = document.querySelectorAll('.star');
const ratingText = document.getElementById('ratingText');
const feedbackComment = document.getElementById('feedbackComment');
const submitFeedback = document.getElementById('submitFeedback');

// Variables
let typingTimer;
const doneTypingInterval = 800;
let userRating = 0;



// Theme Management
const themeToggle = document.getElementById('themeToggle');
let currentTheme = localStorage.getItem('theme') || 'light';

function setTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    currentTheme = theme;
    localStorage.setItem('theme', theme);
    themeToggle.textContent = theme === 'dark' ? '☀️ Light' : '🌙 Dark';
}

function toggleTheme() {
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
}

// Initialize theme
setTheme(currentTheme);

// Theme toggle event
themeToggle.addEventListener('click', toggleTheme);

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    console.log('Frontend initialized');
    checkServerHealth();
    
    // Event Listeners
    input.addEventListener('input', handleInput);
    translateBtn.addEventListener('click', translate);
    clearBtn.addEventListener('click', clearAll);

    // Suggestion chips
    suggestionChips.forEach(chip => {
        chip.addEventListener('click', () => {
            const word = chip.getAttribute('data-word');
            input.value = word;
            translate();
        });
    });

    // Rating stars
    ratingStars.forEach(star => {
        star.addEventListener('click', () => {
            const rating = parseInt(star.getAttribute('data-rating'));
            setRating(rating);
        });
    });

    // Submit feedback
    submitFeedback.addEventListener('click', submitUserFeedback);
    
    // Auto-check health every 30 seconds
    setInterval(checkServerHealth, 30000);
});

// Handle Input
function handleInput() {
    clearTimeout(typingTimer);
    
    if (input.value.trim()) {
        typingTimer = setTimeout(translate, doneTypingInterval);
    } else {
        output.value = '';
        progressText.textContent = '';
        detailsSection.style.display = 'none';
        feedbackSection.style.display = 'none';
    }
}

// Translate Function (EXACTLY like Colab)
async function translate() {
    const text = input.value.trim();
    
    if (!text) {
        showToast('Please enter some text to translate', 'warning');
        return;
    }
    
    // Show loading
    loading.style.display = 'flex';
    output.value = '';
    progressText.textContent = `Translating...`;
    detailsSection.style.display = 'none';
    feedbackSection.style.display = 'none';
    
    // Split into words
    const words = text.split(/\s+/).filter(w => w.length > 0);
    
    if (words.length === 0) {
        loading.style.display = 'none';
        return;
    }
    
    progressText.textContent = `Translating ${words.length} word(s)...`;
    
    const translatedWords = [];
    const wordDetails = [];
    let totalConfidence = 0;
    
    // Translate each word one by one (like Colab)
    for (let i = 0; i < words.length; i++) {
        const word = words[i];
        progressText.textContent = `Translating word ${i + 1} of ${words.length}: "${word}"`;
        
        try {
            const response = await fetch(`${API_BASE_URL}/translate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text: word })
            });
            
            if (response.ok) {
                const data = await response.json();
                translatedWords.push(data.translation);
                wordDetails.push({
                    input: word,
                    translation: data.translation,
                    confidence: data.average_confidence
                });
                totalConfidence += data.average_confidence;
                currentPredictionId = data.prediction_id;
                
                // Update output WITHOUT spaces (like Colab)
                output.value = translatedWords.join('');
            } else {
                // Handle API errors
                const errorData = await response.json();
                translatedWords.push(`[Error: ${word}]`);
                wordDetails.push({
                    input: word,
                    translation: `[Error]`,
                    confidence: 0
                });
                output.value = translatedWords.join('');
                console.error('API Error:', errorData);
            }
        } catch (error) {
            console.error('Network error:', error);
            translatedWords.push(`[Network Error: ${word}]`);
            wordDetails.push({
                input: word,
                translation: `[Error]`,
                confidence: 0
            });
            output.value = translatedWords.join('');
        }
    }
    
    // Calculate average confidence
    const avgConfidence = wordDetails.length > 0 ? totalConfidence / wordDetails.length : 0;
    
    // Update details
    updateDetails(wordDetails, avgConfidence);
    
    // Hide loading
    loading.style.display = 'none';
    progressText.textContent = `✅ Translated ${words.length} word(s)`;
    
    showToast('Translation completed!', 'success');
}

// Update Details Section
function updateDetails(wordDetails, avgConfidence) {
    if (wordDetails.length === 0) return;
    
    // Show details section
    detailsSection.style.display = 'block';

    // Show feedback section only if we have a prediction ID
    if (currentPredictionId) {
        feedbackSection.style.display = 'block';
    }
    
    // Update summary
    confidenceValue.textContent = `${avgConfidence.toFixed(1)}%`;
    wordCountValue.textContent = wordDetails.length;
    predictionId.textContent = currentPredictionId ? currentPredictionId.substring(0, 8) + '...' : 'N/A';
    
    // Update word breakdown
    breakdownContainer.innerHTML = '';
    
    wordDetails.forEach(detail => {
        const wordCard = document.createElement('div');
        wordCard.className = 'word-card';
        
        const confidenceColor = detail.confidence >= 80 ? '#10b981' : 
                              detail.confidence >= 60 ? '#f59e0b' : '#ef4444';
        
        wordCard.innerHTML = `
            <div class="word-english">${detail.input}</div>
            <div class="word-khmer">${detail.translation}</div>
            <div class="confidence-bar">
                <div class="confidence-fill" style="width: ${detail.confidence}%; background: ${confidenceColor};"></div>
            </div>
            <div style="text-align: right; font-size: 0.8em; color: #64748b; margin-top: 5px;">
                ${detail.confidence.toFixed(1)}%
            </div>
        `;
        
        breakdownContainer.appendChild(wordCard);
    });
}

// Clear All
function clearAll() {
    input.value = '';
    output.value = '';
    progressText.textContent = '';
    detailsSection.style.display = 'none';
    feedbackSection.style.display = 'none';
    showToast('Cleared all fields', 'info');
}

// Check Server Health
async function checkServerHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        
        if (response.ok) {
            const data = await response.json();
            
            if (data.status === 'healthy') {
                statusIndicator.innerHTML = '✅ Server Running - Type to translate!';
                statusIndicator.style.background = 'linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(5, 150, 105, 0.1))';
                statusIndicator.style.color = '#065f46';
                statusIndicator.style.borderColor = 'rgba(16, 185, 129, 0.3)';
            } else if (data.status === 'degraded') {
                statusIndicator.innerHTML = '⚠️ Server Degraded - Some features may not work';
                statusIndicator.style.background = 'linear-gradient(135deg, rgba(245, 158, 11, 0.1), rgba(217, 119, 6, 0.1))';
                statusIndicator.style.color = '#92400e';
                statusIndicator.style.borderColor = 'rgba(245, 158, 11, 0.3)';
            } else {
                statusIndicator.innerHTML = '❌ Server Unhealthy - Please check backend';
                statusIndicator.style.background = 'linear-gradient(135deg, rgba(239, 68, 68, 0.1), rgba(220, 38, 38, 0.1))';
                statusIndicator.style.color = '#991b1b';
                statusIndicator.style.borderColor = 'rgba(239, 68, 68, 0.3)';
            }
        } else {
            statusIndicator.innerHTML = '❌ Server Unavailable - Please check backend';
            statusIndicator.style.background = 'linear-gradient(135deg, rgba(239, 68, 68, 0.1), rgba(220, 38, 38, 0.1))';
            statusIndicator.style.color = '#991b1b';
            statusIndicator.style.borderColor = 'rgba(239, 68, 68, 0.3)';
        }
    } catch (error) {
        console.error('Health check failed:', error);
        statusIndicator.innerHTML = '❌ Cannot connect to server';
        statusIndicator.style.background = 'linear-gradient(135deg, rgba(239, 68, 68, 0.1), rgba(220, 38, 38, 0.1))';
        statusIndicator.style.color = '#991b1b';
        statusIndicator.style.borderColor = 'rgba(239, 68, 68, 0.3)';
    }
}

// Toast Notification
function showToast(message, type = 'info') {
    // Remove existing toast
    const existingToast = document.querySelector('.toast');
    if (existingToast) {
        existingToast.remove();
    }
    
    // Create toast
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = message;
    
    // Style based on type
    const colors = {
        success: '#10b981',
        error: '#ef4444',
        warning: '#f59e0b',
        info: '#3b82f6'
    };
    
    toast.style.position = 'fixed';
    toast.style.bottom = '20px';
    toast.style.right = '20px';
    toast.style.padding = '12px 20px';
    toast.style.background = colors[type] || colors.info;
    toast.style.color = 'white';
    toast.style.borderRadius = '8px';
    toast.style.fontWeight = '600';
    toast.style.zIndex = '1000';
    toast.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(20px)';
    toast.style.transition = 'all 0.3s ease';
    
    document.body.appendChild(toast);
    
    // Animate in
    setTimeout(() => {
        toast.style.opacity = '1';
        toast.style.transform = 'translateY(0)';
    }, 10);
    
    // Remove after 3 seconds
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(20px)';
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }, 3000);
}

// Set Rating
function setRating(rating) {
    userRating = rating;

    // Update star display
    ratingStars.forEach((star, index) => {
        if (index < rating) {
            star.style.color = '#fbbf24';
            star.style.transform = 'scale(1.2)';
        } else {
            star.style.color = '#d1d5db';
            star.style.transform = 'scale(1)';
        }
    });

    // Update text
    const texts = ['Poor', 'Fair', 'Good', 'Very Good', 'Excellent'];
    ratingText.textContent = `${rating} star${rating > 1 ? 's' : ''} - ${texts[rating - 1]}`;
}

// Submit Feedback
async function submitUserFeedback() {
    if (!currentPredictionId) {
        showToast('No translation to rate', 'warning');
        return;
    }

    if (userRating === 0) {
        showToast('Please select a rating', 'warning');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/feedback`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                prediction_id: currentPredictionId,
                rating: userRating,
                comment: feedbackComment.value.trim() || null
            })
        });

        if (response.ok) {
            const data = await response.json();
            showToast('Thank you for your feedback!', 'success');
            // Reset
            setRating(0);
            feedbackComment.value = '';
            feedbackSection.style.display = 'none';
        } else {
            const errorData = await response.json();
            showToast(errorData.detail || 'Failed to submit feedback', 'error');
        }
    } catch (error) {
        console.error('Feedback submission error:', error);
        showToast('Failed to submit feedback', 'error');
    }
}

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Ctrl+Enter to translate
    if (e.ctrlKey && e.key === 'Enter') {
        e.preventDefault();
        translate();
    }

    // Escape to clear
    if (e.key === 'Escape' && document.activeElement === input) {
        clearAll();
    }
});

// Test API connection on startup
async function testApiConnection() {
    console.log('Testing API connection...');
    const testUrls = [
        'http://localhost:8001/api/v1/health',
        'http://backend:8001/api/v1/health'
    ];
    
    for (const url of testUrls) {
        try {
            const response = await fetch(url, { timeout: 5000 });
            if (response.ok) {
                console.log(`✅ API accessible at: ${url}`);
                return url.replace('/health', '');
            }
        } catch (error) {
            console.log(`❌ Cannot connect to: ${url}`);
        }
    }
    console.log('⚠️ No API endpoint accessible');
    return 'http://localhost:8001/api/v1';
}

// Optional: Auto-detect API endpoint on startup
document.addEventListener('DOMContentLoaded', async () => {
    const detectedApi = await testApiConnection();
    console.log(`Using API: ${detectedApi}`);
});