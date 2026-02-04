// Aura Link Main JavaScript

// ===== Toast Notification System =====
const NotificationSystem = {
    container: null,

    init() {
        // Create notification container if it doesn't exist
        if (!this.container) {
            this.container = document.createElement('div');
            this.container.id = 'notification-container';
            this.container.style.cssText = `
                position: fixed;
                top: 80px;
                right: 20px;
                z-index: 9999;
                min-width: 320px;
                max-width: 400px;
            `;
            document.body.appendChild(this.container);
        }
    },

    show(message, type = 'info', duration = 5000) {
        this.init();

        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;

        // Icon mapping
        const icons = {
            success: 'bi-check-circle-fill',
            error: 'bi-x-circle-fill',
            warning: 'bi-exclamation-triangle-fill',
            info: 'bi-info-circle-fill'
        };

        // Color mapping
        const colors = {
            success: '#198754',
            error: '#dc3545',
            warning: '#ffc107',
            info: '#0dcaf0'
        };

        notification.innerHTML = `
            <div style="
                background: linear-gradient(135deg, ${colors[type]}15 0%, ${colors[type]}25 100%);
                border-left: 4px solid ${colors[type]};
                border-radius: 8px;
                padding: 16px 20px;
                margin-bottom: 12px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                display: flex;
                align-items: center;
                animation: slideInRight 0.3s ease;
                backdrop-filter: blur(10px);
                color: #fff;
            ">
                <i class="bi ${icons[type]}" style="
                    font-size: 24px;
                    color: ${colors[type]};
                    margin-right: 12px;
                    flex-shrink: 0;
                "></i>
                <div style="flex: 1; font-size: 14px; line-height: 1.5;">
                    ${message}
                </div>
                <button onclick="this.parentElement.parentElement.remove()" style="
                    background: none;
                    border: none;
                    color: #999;
                    cursor: pointer;
                    font-size: 20px;
                    margin-left: 12px;
                    padding: 0;
                    line-height: 1;
                    flex-shrink: 0;
                ">&times;</button>
            </div>
        `;

        this.container.appendChild(notification);

        // Auto remove after duration
        if (duration > 0) {
            setTimeout(() => {
                notification.style.opacity = '0';
                notification.style.transition = 'opacity 0.3s ease';
                setTimeout(() => notification.remove(), 300);
            }, duration);
        }
    },

    success(message, duration = 5000) {
        this.show(message, 'success', duration);
    },

    error(message, duration = 7000) {
        this.show(message, 'error', duration);
    },

    warning(message, duration = 6000) {
        this.show(message, 'warning', duration);
    },

    info(message, duration = 5000) {
        this.show(message, 'info', duration);
    }
};

// Add animation keyframes
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
`;
document.head.appendChild(style);

// Make it globally accessible
window.notify = NotificationSystem;

// ===== Auto-show Django messages as notifications =====
document.addEventListener('DOMContentLoaded', function () {
    const djangoMessages = document.querySelectorAll('.django-messages .alert');
    djangoMessages.forEach(alert => {
        const text = alert.textContent.trim();

        if (alert.classList.contains('alert-success')) {
            notify.success(text);
        } else if (alert.classList.contains('alert-danger') || alert.classList.contains('alert-error')) {
            notify.error(text);
        } else if (alert.classList.contains('alert-warning')) {
            notify.warning(text);
        } else {
            notify.info(text);
        }

        // Hide the original Django message
        alert.style.display = 'none';
    });
});

// ===== Add smooth scrolling =====
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({ behavior: 'smooth' });
        }
    });
});
