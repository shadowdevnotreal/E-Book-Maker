/**
 * Toast Notification System
 * Beautiful, animated toast notifications for user feedback
 */

class ToastNotification {
    constructor() {
        this.container = null;
        this.init();
    }

    init() {
        // Create toast container
        this.container = document.createElement('div');
        this.container.id = 'toast-container';
        this.container.className = 'toast-container';
        document.body.appendChild(this.container);
    }

    /**
     * Show a toast notification
     * @param {string} message - The message to display
     * @param {string} type - Type: 'success', 'error', 'warning', 'info'
     * @param {number} duration - Duration in milliseconds (default: 4000)
     */
    show(message, type = 'info', duration = 4000) {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;

        // Icon based on type
        const icons = {
            success: '✓',
            error: '✕',
            warning: '⚠',
            info: 'ℹ'
        };

        toast.innerHTML = `
            <div class="toast-icon">${icons[type] || icons.info}</div>
            <div class="toast-content">
                <div class="toast-message">${message}</div>
            </div>
            <button class="toast-close" onclick="this.parentElement.remove()">×</button>
        `;

        // Add to container
        this.container.appendChild(toast);

        // Trigger animation
        setTimeout(() => toast.classList.add('toast-show'), 10);

        // Auto remove after duration
        if (duration > 0) {
            setTimeout(() => this.remove(toast), duration);
        }

        return toast;
    }

    remove(toast) {
        toast.classList.remove('toast-show');
        toast.classList.add('toast-hide');
        setTimeout(() => toast.remove(), 300);
    }

    // Convenience methods
    success(message, duration) {
        return this.show(message, 'success', duration);
    }

    error(message, duration) {
        return this.show(message, 'error', duration);
    }

    warning(message, duration) {
        return this.show(message, 'warning', duration);
    }

    info(message, duration) {
        return this.show(message, 'info', duration);
    }

    // Loading toast with manual dismiss
    loading(message) {
        return this.show(message, 'info', 0); // 0 = no auto dismiss
    }

    // Update an existing toast
    update(toast, message, type = null) {
        const messageEl = toast.querySelector('.toast-message');
        if (messageEl) {
            messageEl.textContent = message;
        }
        if (type) {
            toast.className = `toast toast-${type} toast-show`;
            const icons = {
                success: '✓',
                error: '✕',
                warning: '⚠',
                info: 'ℹ'
            };
            const iconEl = toast.querySelector('.toast-icon');
            if (iconEl) {
                iconEl.textContent = icons[type] || icons.info;
            }
        }
    }

    // Clear all toasts
    clearAll() {
        const toasts = this.container.querySelectorAll('.toast');
        toasts.forEach(toast => this.remove(toast));
    }
}

// Create global instance
window.Toast = new ToastNotification();

// Convenience global functions
window.showToast = (message, type, duration) => window.Toast.show(message, type, duration);
window.toastSuccess = (message, duration) => window.Toast.success(message, duration);
window.toastError = (message, duration) => window.Toast.error(message, duration);
window.toastWarning = (message, duration) => window.Toast.warning(message, duration);
window.toastInfo = (message, duration) => window.Toast.info(message, duration);
window.toastLoading = (message) => window.Toast.loading(message);
