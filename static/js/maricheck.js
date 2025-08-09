/*!
 * Maricheck - Maritime Crew Management System
 * Custom JavaScript for enhanced user interactions
 */

(function() {
    'use strict';

    // Initialize when DOM is ready
    document.addEventListener('DOMContentLoaded', function() {
        initializeApp();
    });

    /**
     * Main initialization function
     */
    function initializeApp() {
        initializeAlerts();
        initializeFormValidation();
        initializeFileUploads();
        initializeTooltips();
        initializeLoadingStates();
        initializeCopyToClipboard();
        initializeFormAnimations();
    }

    /**
     * Auto-hide alerts after 5 seconds
     */
    function initializeAlerts() {
        const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
        
        alerts.forEach(function(alert) {
            // Add fade-in animation
            alert.classList.add('fade-in');
            
            // Auto-hide after 5 seconds
            setTimeout(function() {
                if (alert && alert.parentNode) {
                    alert.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
                    alert.style.opacity = '0';
                    alert.style.transform = 'translateY(-10px)';
                    
                    setTimeout(function() {
                        if (alert && alert.parentNode) {
                            alert.remove();
                        }
                    }, 500);
                }
            }, 5000);
        });
    }

    /**
     * Enhanced form validation with real-time feedback
     */
    function initializeFormValidation() {
        const forms = document.querySelectorAll('form');
        
        forms.forEach(function(form) {
            const inputs = form.querySelectorAll('input, select, textarea');
            
            inputs.forEach(function(input) {
                // Real-time validation on blur
                input.addEventListener('blur', function() {
                    validateField(this);
                });
                
                // Clear validation on focus
                input.addEventListener('focus', function() {
                    clearFieldValidation(this);
                });
            });
            
            // Enhanced form submission
            form.addEventListener('submit', function(e) {
                const submitBtn = form.querySelector('input[type="submit"], button[type="submit"]');
                if (submitBtn) {
                    addLoadingState(submitBtn);
                }
            });
        });
    }

    /**
     * Validate individual form field
     */
    function validateField(field) {
        const value = field.value.trim();
        const isRequired = field.hasAttribute('required') || field.classList.contains('required');
        
        // Email validation
        if (field.type === 'email' && value) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(value)) {
                showFieldError(field, 'Please enter a valid email address');
                return false;
            }
        }
        
        // Phone validation
        if (field.name && field.name.includes('phone') && value) {
            const phoneRegex = /^[\+]?[\d\s\-\(\)]{10,}$/;
            if (!phoneRegex.test(value)) {
                showFieldError(field, 'Please enter a valid phone number');
                return false;
            }
        }
        
        // Required field validation
        if (isRequired && !value) {
            showFieldError(field, 'This field is required');
            return false;
        }
        
        // If validation passes, show success
        if (value) {
            showFieldSuccess(field);
        }
        
        return true;
    }

    /**
     * Show field error state
     */
    function showFieldError(field, message) {
        field.classList.remove('is-valid');
        field.classList.add('is-invalid');
        
        // Remove existing feedback
        const existingFeedback = field.parentNode.querySelector('.invalid-feedback.custom');
        if (existingFeedback) {
            existingFeedback.remove();
        }
        
        // Add error message
        const feedback = document.createElement('div');
        feedback.className = 'invalid-feedback custom';
        feedback.textContent = message;
        field.parentNode.appendChild(feedback);
    }

    /**
     * Show field success state
     */
    function showFieldSuccess(field) {
        field.classList.remove('is-invalid');
        field.classList.add('is-valid');
        
        // Remove custom error feedback
        const existingFeedback = field.parentNode.querySelector('.invalid-feedback.custom');
        if (existingFeedback) {
            existingFeedback.remove();
        }
    }

    /**
     * Clear field validation state
     */
    function clearFieldValidation(field) {
        field.classList.remove('is-invalid', 'is-valid');
        
        const existingFeedback = field.parentNode.querySelector('.invalid-feedback.custom');
        if (existingFeedback) {
            existingFeedback.remove();
        }
    }

    /**
     * Enhanced file upload functionality
     */
    function initializeFileUploads() {
        const fileInputs = document.querySelectorAll('input[type="file"]');
        
        fileInputs.forEach(function(input) {
            input.addEventListener('change', function() {
                handleFileUpload(this);
            });
        });
    }

    /**
     * Handle file upload with validation and preview
     */
    function handleFileUpload(input) {
        const files = Array.from(input.files);
        const allowedTypes = input.getAttribute('accept');
        const maxSize = 16 * 1024 * 1024; // 16MB
        
        // Validate files
        const validFiles = files.filter(function(file) {
            // Size validation
            if (file.size > maxSize) {
                showFileError(input, `File "${file.name}" is too large. Maximum size is 16MB.`);
                return false;
            }
            
            // Type validation
            if (allowedTypes) {
                const allowed = allowedTypes.split(',').map(type => type.trim());
                const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
                if (!allowed.includes(fileExtension)) {
                    showFileError(input, `File "${file.name}" has an invalid type.`);
                    return false;
                }
            }
            
            return true;
        });
        
        if (validFiles.length > 0) {
            showFileSuccess(input, validFiles);
        }
    }

    /**
     * Show file upload error
     */
    function showFileError(input, message) {
        // Clear previous messages
        clearFileMessages(input);
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'file-error mt-2 alert alert-danger alert-sm';
        errorDiv.innerHTML = `<i class="fas fa-exclamation-triangle me-2"></i>${message}`;
        
        input.parentNode.appendChild(errorDiv);
        
        // Auto-remove after 5 seconds
        setTimeout(function() {
            if (errorDiv.parentNode) {
                errorDiv.remove();
            }
        }, 5000);
    }

    /**
     * Show file upload success
     */
    function showFileSuccess(input, files) {
        clearFileMessages(input);
        
        const successDiv = document.createElement('div');
        successDiv.className = 'file-success mt-2 alert alert-success alert-sm';
        
        const fileCount = files.length;
        const fileText = fileCount === 1 ? 'file' : 'files';
        successDiv.innerHTML = `<i class="fas fa-check me-2"></i>${fileCount} ${fileText} selected successfully`;
        
        input.parentNode.appendChild(successDiv);
    }

    /**
     * Clear file upload messages
     */
    function clearFileMessages(input) {
        const messages = input.parentNode.querySelectorAll('.file-error, .file-success');
        messages.forEach(msg => msg.remove());
    }

    /**
     * Initialize Bootstrap tooltips
     */
    function initializeTooltips() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"], [title]'));
        tooltipTriggerList.map(function(tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    /**
     * Add loading states to buttons and forms
     */
    function initializeLoadingStates() {
        // Add loading state to any button with data-loading attribute
        const loadingButtons = document.querySelectorAll('[data-loading]');
        
        loadingButtons.forEach(function(btn) {
            btn.addEventListener('click', function() {
                addLoadingState(this);
            });
        });
    }

    /**
     * Add loading state to button
     */
    function addLoadingState(button) {
        if (button.classList.contains('loading')) return;
        
        const originalText = button.innerHTML;
        const loadingText = button.getAttribute('data-loading') || 'Loading...';
        
        button.classList.add('loading');
        button.disabled = true;
        button.innerHTML = `<i class="fas fa-spinner fa-spin me-2"></i>${loadingText}`;
        
        // Store original text for potential restoration
        button.setAttribute('data-original-text', originalText);
    }

    /**
     * Remove loading state from button
     */
    function removeLoadingState(button) {
        const originalText = button.getAttribute('data-original-text');
        
        if (originalText) {
            button.innerHTML = originalText;
            button.disabled = false;
            button.classList.remove('loading');
            button.removeAttribute('data-original-text');
        }
    }

    /**
     * Copy to clipboard functionality
     */
    function initializeCopyToClipboard() {
        const copyButtons = document.querySelectorAll('[data-copy]');
        
        copyButtons.forEach(function(btn) {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                const textToCopy = this.getAttribute('data-copy') || this.textContent;
                copyToClipboard(textToCopy, this);
            });
        });
    }

    /**
     * Copy text to clipboard with visual feedback
     */
    function copyToClipboard(text, button) {
        if (navigator.clipboard) {
            navigator.clipboard.writeText(text).then(function() {
                showCopySuccess(button);
            }).catch(function() {
                fallbackCopyToClipboard(text, button);
            });
        } else {
            fallbackCopyToClipboard(text, button);
        }
    }

    /**
     * Fallback copy method for older browsers
     */
    function fallbackCopyToClipboard(text, button) {
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        try {
            document.execCommand('copy');
            showCopySuccess(button);
        } catch (err) {
            console.error('Copy failed:', err);
        }
        
        document.body.removeChild(textArea);
    }

    /**
     * Show copy success feedback
     */
    function showCopySuccess(button) {
        const originalContent = button.innerHTML;
        const originalClasses = button.className;
        
        button.innerHTML = '<i class="fas fa-check"></i>';
        button.className = button.className.replace(/btn-outline-\w+/, 'btn-success');
        
        setTimeout(function() {
            button.innerHTML = originalContent;
            button.className = originalClasses;
        }, 2000);
    }

    /**
     * Add smooth animations to form sections
     */
    function initializeFormAnimations() {
        const sections = document.querySelectorAll('.section-header');
        
        // Animate sections on scroll
        const observer = new IntersectionObserver(function(entries) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    entry.target.classList.add('slide-up');
                }
            });
        }, {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        });

        sections.forEach(function(section) {
            observer.observe(section);
        });
    }

    /**
     * Utility function to debounce events
     */
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

    /**
     * Format file size for display
     */
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    /**
     * Show notification toast
     */
    function showNotification(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');
        
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'danger' ? 'exclamation-triangle' : 'info-circle'} me-2"></i>
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        
        // Create toast container if it doesn't exist
        let toastContainer = document.querySelector('.toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
            document.body.appendChild(toastContainer);
        }
        
        toastContainer.appendChild(toast);
        
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
    }

    // Expose useful functions globally
    window.Maricheck = {
        showNotification: showNotification,
        addLoadingState: addLoadingState,
        removeLoadingState: removeLoadingState,
        copyToClipboard: copyToClipboard,
        formatFileSize: formatFileSize
    };

})();
