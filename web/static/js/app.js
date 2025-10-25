// E-Book Maker - Main JavaScript

// Utility Functions
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

function formatDate(timestamp) {
    const date = new Date(timestamp * 1000);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}

// Check Dependencies
async function checkDependencies() {
    try {
        const response = await fetch('/api/check-dependencies');
        const data = await response.json();

        updateStatusIndicator('pandoc-status', data.dependencies.pandoc);
        updateStatusIndicator('wkhtmltopdf-status', data.dependencies.wkhtmltopdf);
        updateStatusIndicator('latex-status', data.dependencies.pdflatex);
    } catch (error) {
        console.error('Error checking dependencies:', error);
    }
}

function updateStatusIndicator(elementId, installed) {
    const element = document.getElementById(elementId);
    if (!element) return;

    if (installed) {
        element.textContent = '✓ Installed';
        element.style.color = '#10b981';
    } else {
        element.textContent = '✗ Not Found';
        element.style.color = '#ef4444';
    }
}

// Load Recent Files
async function loadRecentFiles(fileType) {
    try {
        const response = await fetch(`/api/list-files/${fileType}`);
        const data = await response.json();

        const listElement = document.getElementById(`${fileType}-list`);
        if (!listElement) return;

        if (data.files && data.files.length > 0) {
            // Sort by modified date (newest first)
            data.files.sort((a, b) => b.modified - a.modified);

            // Take only the 5 most recent
            const recentFiles = data.files.slice(0, 5);

            listElement.innerHTML = recentFiles.map(file => `
                <div class="file-item">
                    <div>
                        <div class="file-name">${file.name}</div>
                        <div class="file-info">${formatFileSize(file.size)} • ${formatDate(file.modified)}</div>
                    </div>
                    <a href="/api/download/${file.path}" class="btn btn-small btn-primary" download>Download</a>
                </div>
            `).join('');
        } else {
            listElement.innerHTML = '<p style="color: #6b7280; text-align: center; padding: 20px;">No files yet</p>';
        }
    } catch (error) {
        console.error(`Error loading ${fileType} files:`, error);
        const listElement = document.getElementById(`${fileType}-list`);
        if (listElement) {
            listElement.innerHTML = '<p style="color: #ef4444; text-align: center; padding: 20px;">Error loading files</p>';
        }
    }
}

// Show Notification
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;

    const styles = {
        position: 'fixed',
        top: '20px',
        right: '20px',
        padding: '15px 20px',
        borderRadius: '8px',
        boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
        zIndex: '1000',
        maxWidth: '300px',
        animation: 'slideIn 0.3s ease-out'
    };

    const colors = {
        success: { bg: '#d1fae5', color: '#065f46' },
        error: { bg: '#fee2e2', color: '#991b1b' },
        warning: { bg: '#fef3c7', color: '#92400e' },
        info: { bg: '#dbeafe', color: '#1e40af' }
    };

    Object.assign(notification.style, styles);
    notification.style.backgroundColor = colors[type].bg;
    notification.style.color = colors[type].color;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Add animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }

    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Progress Bar Utility
function updateProgressBar(percent) {
    const progressFill = document.getElementById('progress-fill');
    if (progressFill) {
        progressFill.style.width = percent + '%';
    }
}

function updateProgressText(text) {
    const progressText = document.getElementById('progress-text');
    if (progressText) {
        progressText.textContent = text;
    }
}

// Form Validation
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return false;

    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;

    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            isValid = false;
            field.style.borderColor = '#ef4444';
        } else {
            field.style.borderColor = '#e5e7eb';
        }
    });

    return isValid;
}

// File Upload Helper
function createFilePreview(file) {
    return new Promise((resolve, reject) => {
        if (file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = (e) => resolve(e.target.result);
            reader.onerror = reject;
            reader.readAsDataURL(file);
        } else {
            resolve(null);
        }
    });
}

// Download Helper
function downloadFile(url, filename) {
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// API Helper
async function apiRequest(endpoint, options = {}) {
    try {
        const response = await fetch(endpoint, {
            ...options,
            headers: {
                ...options.headers,
            }
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Request failed');
        }

        return data;
    } catch (error) {
        console.error('API Request Error:', error);
        throw error;
    }
}

// Debounce Helper
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Initialize tooltips (if needed)
function initTooltips() {
    const tooltipTriggers = document.querySelectorAll('[data-tooltip]');
    tooltipTriggers.forEach(trigger => {
        trigger.addEventListener('mouseenter', (e) => {
            const tooltip = document.createElement('div');
            tooltip.className = 'tooltip';
            tooltip.textContent = e.target.dataset.tooltip;
            tooltip.style.cssText = `
                position: absolute;
                background: #1f2937;
                color: white;
                padding: 8px 12px;
                border-radius: 6px;
                font-size: 0.875rem;
                z-index: 1000;
                pointer-events: none;
            `;
            document.body.appendChild(tooltip);

            const rect = e.target.getBoundingClientRect();
            tooltip.style.left = rect.left + 'px';
            tooltip.style.top = (rect.top - tooltip.offsetHeight - 5) + 'px';

            e.target.addEventListener('mouseleave', () => {
                tooltip.remove();
            }, { once: true });
        });
    });
}

// Page Load
document.addEventListener('DOMContentLoaded', () => {
    // Initialize tooltips
    initTooltips();

    // Add file info styling to head
    const fileInfoStyle = document.createElement('style');
    fileInfoStyle.textContent = `
        .file-info-display {
            margin-top: 15px;
        }
        .file-info {
            color: #6b7280;
            font-size: 0.875rem;
        }
    `;
    document.head.appendChild(fileInfoStyle);
});

// Export functions for use in templates
window.ebookMaker = {
    formatFileSize,
    formatDate,
    checkDependencies,
    loadRecentFiles,
    showNotification,
    updateProgressBar,
    updateProgressText,
    validateForm,
    createFilePreview,
    downloadFile,
    apiRequest,
    debounce
};
