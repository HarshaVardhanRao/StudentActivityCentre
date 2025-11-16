// Modern Interactions and Enhancements for MITS SAC Hub
// Author: SAC Development Team
// Version: 1.0.0

(function() {
    'use strict';

    // Wait for DOM to be ready
    document.addEventListener('DOMContentLoaded', function() {
        initializeModernFeatures();
    });

    function initializeModernFeatures() {
        // Initialize all modern interaction features
        setupSmoothScrolling();
        setupFormEnhancements();
        setupLoadingStates();
        setupNotificationSystem();
        setupAccessibilityFeatures();
        setupPerformanceOptimizations();
        setupAnalytics();
    }

    // Smooth Scrolling for Better UX
    function setupSmoothScrolling() {
        // Enhanced smooth scrolling with easing
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function(e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    const headerOffset = 80; // Account for sticky navbar
                    const elementPosition = target.getBoundingClientRect().top;
                    const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

                    window.scrollTo({
                        top: offsetPosition,
                        behavior: 'smooth'
                    });
                }
            });
        });

        // Smart navbar hiding on scroll
        let lastScrollTop = 0;
        const navbar = document.querySelector('.navbar');
        if (navbar) {
            window.addEventListener('scroll', function() {
                const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
                
                if (scrollTop > lastScrollTop && scrollTop > 100) {
                    // Scrolling down & past threshold
                    navbar.style.transform = 'translateY(-100%)';
                } else {
                    // Scrolling up
                    navbar.style.transform = 'translateY(0)';
                }
                lastScrollTop = scrollTop <= 0 ? 0 : scrollTop;
            }, { passive: true });
        }
    }

    // Enhanced Form Interactions
    function setupFormEnhancements() {
        // Auto-resize textareas
        document.querySelectorAll('textarea').forEach(textarea => {
            textarea.addEventListener('input', function() {
                this.style.height = 'auto';
                this.style.height = (this.scrollHeight) + 'px';
            });
        });

        // Form validation feedback
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', function(e) {
                const requiredFields = this.querySelectorAll('[required]');
                let isValid = true;

                requiredFields.forEach(field => {
                    if (!field.value.trim()) {
                        isValid = false;
                        showFieldError(field, 'This field is required');
                    } else {
                        clearFieldError(field);
                    }
                });

                if (!isValid) {
                    e.preventDefault();
                    showNotification('Please fill in all required fields', 'error');
                }
            });
        });

        // Real-time validation for common fields
        document.querySelectorAll('input[type="email"]').forEach(input => {
            input.addEventListener('blur', function() {
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (this.value && !emailRegex.test(this.value)) {
                    showFieldError(this, 'Please enter a valid email address');
                } else {
                    clearFieldError(this);
                }
            });
        });
    }

    // Loading States and Progress Indicators
    function setupLoadingStates() {
        // Enhanced button loading states
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', function() {
                const submitBtn = this.querySelector('button[type="submit"], input[type="submit"]');
                if (submitBtn) {
                    const originalText = submitBtn.innerHTML;
                    submitBtn.innerHTML = '<span class="loading"><span class="spinner"></span> Processing...</span>';
                    submitBtn.disabled = true;
                    
                    // Reset after timeout (fallback)
                    setTimeout(() => {
                        submitBtn.innerHTML = originalText;
                        submitBtn.disabled = false;
                    }, 30000);
                }
            });
        });

        // Page loading indicator
        let loadingTimeout;
        function showPageLoader() {
            clearTimeout(loadingTimeout);
            const loader = document.createElement('div');
            loader.className = 'page-loader';
            loader.innerHTML = `
                <div class="loader-content">
                    <div class="loading-spinner"></div>
                    <p>Loading...</p>
                </div>
            `;
            document.body.appendChild(loader);

            // Auto-hide after 10 seconds
            loadingTimeout = setTimeout(() => {
                hidePageLoader();
            }, 10000);
        }

        function hidePageLoader() {
            const loader = document.querySelector('.page-loader');
            if (loader) {
                loader.style.opacity = '0';
                setTimeout(() => loader.remove(), 300);
            }
        }

        // Show loader for navigation clicks
        document.querySelectorAll('a:not([href^="#"]):not([href^="mailto"]):not([href^="tel"])').forEach(link => {
            link.addEventListener('click', function(e) {
                if (!this.target || this.target === '_self') {
                    showPageLoader();
                }
            });
        });

        // Hide loader when page loads
        window.addEventListener('load', hidePageLoader);
    }

    // Modern Notification System
    function setupNotificationSystem() {
        // Create notification container
        if (!document.querySelector('.notification-container')) {
            const container = document.createElement('div');
            container.className = 'notification-container';
            document.body.appendChild(container);
        }

        // Auto-dismiss existing alerts
        setTimeout(() => {
            document.querySelectorAll('.alert').forEach(alert => {
                fadeOutElement(alert);
            });
        }, 5000);
    }

    // Global notification function
    window.showNotification = function(message, type = 'info', duration = 5000) {
        const container = document.querySelector('.notification-container');
        if (!container) return;

        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        
        const icons = {
            success: '✅',
            error: '❌',
            warning: '⚠️',
            info: 'ℹ️'
        };

        notification.innerHTML = `
            <div class="notification-content">
                <span class="notification-icon">${icons[type] || icons.info}</span>
                <span class="notification-message">${message}</span>
                <button class="notification-close" onclick="this.parentElement.parentElement.remove()">×</button>
            </div>
        `;

        container.appendChild(notification);

        // Animate in
        setTimeout(() => notification.classList.add('notification-show'), 10);

        // Auto-dismiss
        if (duration > 0) {
            setTimeout(() => {
                fadeOutElement(notification);
            }, duration);
        }
    };

    // Accessibility Enhancements
    function setupAccessibilityFeatures() {
        // Keyboard navigation for custom dropdowns
        document.querySelectorAll('.dropdown-btn').forEach(btn => {
            btn.addEventListener('keydown', function(e) {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    this.click();
                }
            });
        });

        // Focus management for modals
        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('show', function() {
                const firstFocusable = this.querySelector('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
                if (firstFocusable) {
                    firstFocusable.focus();
                }
            });
        });

        // Skip links for better accessibility
        if (!document.querySelector('.skip-link')) {
            const skipLink = document.createElement('a');
            skipLink.className = 'skip-link';
            skipLink.href = '#main-content';
            skipLink.textContent = 'Skip to main content';
            document.body.insertBefore(skipLink, document.body.firstChild);
        }

        // Announce page changes to screen readers
        const announcer = document.createElement('div');
        announcer.className = 'sr-announcer';
        announcer.setAttribute('aria-live', 'polite');
        announcer.setAttribute('aria-atomic', 'true');
        document.body.appendChild(announcer);
    }

    // Performance Optimizations
    function setupPerformanceOptimizations() {
        // Lazy load images
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.src;
                        img.classList.remove('lazy');
                        imageObserver.unobserve(img);
                    }
                });
            });

            document.querySelectorAll('img[data-src]').forEach(img => {
                imageObserver.observe(img);
            });
        }

        // Debounce scroll events
        let scrollTimer;
        const originalScrollHandler = window.onscroll;
        window.onscroll = function(e) {
            clearTimeout(scrollTimer);
            scrollTimer = setTimeout(() => {
                if (originalScrollHandler) originalScrollHandler(e);
            }, 16); // ~60fps
        };

        // Optimize animations for reduced motion preference
        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
            document.documentElement.style.setProperty('--transition-fast', '0.01ms');
            document.documentElement.style.setProperty('--transition-normal', '0.01ms');
            document.documentElement.style.setProperty('--transition-slow', '0.01ms');
        }
    }

    // Basic Analytics (Privacy-Friendly)
    function setupAnalytics() {
        // Track page views (without personal data)
        if (typeof analytics === 'undefined') {
            window.analytics = {
                track: function(event, properties) {
                    console.log('Analytics:', event, properties);
                    // Here you could send to your analytics service
                    // Make sure to respect user privacy and GDPR compliance
                }
            };
        }

        // Track common interactions
        document.addEventListener('click', function(e) {
            const target = e.target;
            if (target.matches('.btn, .nav-link, .feature-card')) {
                analytics.track('interaction', {
                    type: 'click',
                    element: target.className,
                    text: target.textContent.trim().substring(0, 50)
                });
            }
        });

        // Track form submissions
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', function() {
                analytics.track('form_submit', {
                    form_id: this.id || 'unnamed',
                    action: this.action || window.location.pathname
                });
            });
        });
    }

    // Utility Functions
    function showFieldError(field, message) {
        clearFieldError(field);
        field.classList.add('field-error');
        
        const error = document.createElement('div');
        error.className = 'field-error-message';
        error.textContent = message;
        
        field.parentNode.insertBefore(error, field.nextSibling);
    }

    function clearFieldError(field) {
        field.classList.remove('field-error');
        const errorMsg = field.parentNode.querySelector('.field-error-message');
        if (errorMsg) {
            errorMsg.remove();
        }
    }

    function fadeOutElement(element) {
        element.style.opacity = '0';
        element.style.transform = 'translateY(-10px)';
        setTimeout(() => {
            if (element.parentNode) {
                element.remove();
            }
        }, 300);
    }

    // Dark mode toggle (optional feature)
    function setupDarkMode() {
        const darkModeBtn = document.createElement('button');
        darkModeBtn.className = 'dark-mode-toggle';
        darkModeBtn.innerHTML = '🌓';
        darkModeBtn.setAttribute('aria-label', 'Toggle dark mode');
        
        darkModeBtn.addEventListener('click', function() {
            document.body.classList.toggle('dark-mode');
            const isDark = document.body.classList.contains('dark-mode');
            localStorage.setItem('darkMode', isDark);
            this.innerHTML = isDark ? '☀️' : '🌓';
        });

        // Check for saved preference
        if (localStorage.getItem('darkMode') === 'true') {
            document.body.classList.add('dark-mode');
            darkModeBtn.innerHTML = '☀️';
        }

        // Add to navbar or appropriate location
        const navbar = document.querySelector('.navbar .container');
        if (navbar) {
            navbar.appendChild(darkModeBtn);
        }
    }

    // Initialize optional features
    // Uncomment the next line if you want dark mode
    // setupDarkMode();

    // Export utilities for global use
    window.SacHub = {
        showNotification: window.showNotification,
        fadeOut: fadeOutElement,
        analytics: window.analytics
    };

    console.log('🎓 MITS SAC Hub - Modern interactions loaded successfully!');
})();