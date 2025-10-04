// Main JavaScript file for Soccer Championship Manager

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Live match updates (if on match page)
    initializeLiveMatchUpdates();

    // Tournament bracket interactions
    initializeBracketInteractions();

    // Search functionality
    initializeSearch();

    // Form validation
    initializeFormValidation();
});

// Live Match Updates
function initializeLiveMatchUpdates() {
    const liveMatchElements = document.querySelectorAll('.live-match');
    
    liveMatchElements.forEach(function(element) {
        const matchId = element.dataset.matchId;
        if (matchId) {
            // Update match every 30 seconds
            setInterval(function() {
                updateLiveMatch(matchId, element);
            }, 30000);
        }
    });
}

function updateLiveMatch(matchId, element) {
    fetch(`/match/${matchId}/live-update`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
            'minute': element.querySelector('.live-minute').textContent,
            'home_score': element.querySelector('.home-score').textContent,
            'away_score': element.querySelector('.away-score').textContent
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateMatchDisplay(element, data);
        }
    })
    .catch(error => {
        console.error('Error updating live match:', error);
    });
}

function updateMatchDisplay(element, data) {
    const minuteElement = element.querySelector('.live-minute');
    const homeScoreElement = element.querySelector('.home-score');
    const awayScoreElement = element.querySelector('.away-score');
    
    if (minuteElement) minuteElement.textContent = data.minute;
    if (homeScoreElement) homeScoreElement.textContent = data.home_score;
    if (awayScoreElement) awayScoreElement.textContent = data.away_score;
}

// Tournament Bracket Interactions
function initializeBracketInteractions() {
    const bracketMatches = document.querySelectorAll('.bracket-match');
    
    bracketMatches.forEach(function(match) {
        match.addEventListener('click', function() {
            const matchId = this.dataset.matchId;
            if (matchId) {
                window.location.href = `/match/${matchId}`;
            }
        });
        
        // Add hover effect
        match.style.cursor = 'pointer';
    });
}

// Search Functionality
function initializeSearch() {
    const searchInput = document.querySelector('input[name="q"]');
    if (searchInput) {
        let searchTimeout;
        
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            const query = this.value.trim();
            
            if (query.length >= 2) {
                searchTimeout = setTimeout(function() {
                    performSearch(query);
                }, 300);
            }
        });
    }
}

function performSearch(query) {
    fetch(`/search?q=${encodeURIComponent(query)}`)
        .then(response => response.text())
        .then(html => {
            // Update search results if on search page
            const searchResults = document.querySelector('.search-results');
            if (searchResults) {
                searchResults.innerHTML = html;
            }
        })
        .catch(error => {
            console.error('Search error:', error);
        });
}

// Form Validation
function initializeFormValidation() {
    const forms = document.querySelectorAll('form[data-validate]');
    
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!validateForm(this)) {
                event.preventDefault();
            }
        });
    });
}

function validateForm(form) {
    let isValid = true;
    const requiredFields = form.querySelectorAll('[required]');
    
    requiredFields.forEach(function(field) {
        if (!field.value.trim()) {
            showFieldError(field, 'This field is required');
            isValid = false;
        } else {
            clearFieldError(field);
        }
    });
    
    // Validate email fields
    const emailFields = form.querySelectorAll('input[type="email"]');
    emailFields.forEach(function(field) {
        if (field.value && !isValidEmail(field.value)) {
            showFieldError(field, 'Please enter a valid email address');
            isValid = false;
        }
    });
    
    // Validate date fields
    const dateFields = form.querySelectorAll('input[type="date"]');
    dateFields.forEach(function(field) {
        if (field.value && !isValidDate(field.value)) {
            showFieldError(field, 'Please enter a valid date');
            isValid = false;
        }
    });
    
    return isValid;
}

function showFieldError(field, message) {
    clearFieldError(field);
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback d-block';
    errorDiv.textContent = message;
    
    field.classList.add('is-invalid');
    field.parentNode.appendChild(errorDiv);
}

function clearFieldError(field) {
    field.classList.remove('is-invalid');
    const errorDiv = field.parentNode.querySelector('.invalid-feedback');
    if (errorDiv) {
        errorDiv.remove();
    }
}

function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function isValidDate(dateString) {
    const date = new Date(dateString);
    return date instanceof Date && !isNaN(date);
}

// Utility Functions
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

function formatTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit'
    });
}

function formatDateTime(dateString) {
    return `${formatDate(dateString)} at ${formatTime(dateString)}`;
}

// Loading States
function showLoading(element) {
    element.innerHTML = '<div class="loading"></div>';
    element.disabled = true;
}

function hideLoading(element, originalText) {
    element.innerHTML = originalText;
    element.disabled = false;
}

// Confirmation Dialogs
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// Toast Notifications
function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toast-container') || createToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // Auto-remove after toast is hidden
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container position-fixed top-0 end-0 p-3';
    container.style.zIndex = '1055';
    document.body.appendChild(container);
    return container;
}

// Export functions for global use
window.SoccerChampionship = {
    showToast,
    confirmAction,
    formatDate,
    formatTime,
    formatDateTime,
    showLoading,
    hideLoading
};

