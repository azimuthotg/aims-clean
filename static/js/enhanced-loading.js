/* ===== ENHANCED LOADING STATES & UX FEEDBACK ===== */
/* Advanced loading states with better user experience */

class EnhancedLoader {
    constructor() {
        this.loadingStates = new Map();
        this.retryCounters = new Map();
        this.successQueue = new Map();
        this.successTimer = null;
        this.init();
    }

    init() {
        // Add global CSS for enhanced loading
        this.injectCSS();
        
        // Setup global error handler
        this.setupGlobalErrorHandler();
        
        // Setup retry functionality
        this.setupRetryHandlers();
    }

    injectCSS() {
        const style = document.createElement('style');
        style.textContent = `
            /* Enhanced Loading Animations */
            .enhanced-skeleton {
                background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
                background-size: 200% 100%;
                animation: enhanced-shimmer 1.5s infinite;
                border-radius: 8px;
                position: relative;
                overflow: hidden;
            }

            [data-theme="dark"] .enhanced-skeleton {
                background: linear-gradient(90deg, #404040 25%, #505050 50%, #404040 75%);
                background-size: 200% 100%;
            }

            @keyframes enhanced-shimmer {
                0% { background-position: 200% 0; }
                100% { background-position: -200% 0; }
            }

            /* Progress Loading Bar */
            .progress-loading {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                height: 3px;
                background: rgba(37, 99, 235, 0.1);
                z-index: 9999;
                overflow: hidden;
            }

            .progress-loading::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                height: 100%;
                background: linear-gradient(90deg, #2563eb, #3b82f6, #60a5fa, #93c5fd);
                animation: progress-slide 2s infinite;
                width: 30%;
            }

            @keyframes progress-slide {
                0% { transform: translateX(-100%); }
                100% { transform: translateX(400%); }
            }

            /* Enhanced Error States */
            .error-state-enhanced {
                padding: 40px 20px;
                text-align: center;
                background: linear-gradient(135deg, #fef2f2 0%, #fdf2f8 100%);
                border: 2px dashed #fca5a5;
                border-radius: 16px;
                position: relative;
                overflow: hidden;
            }

            [data-theme="dark"] .error-state-enhanced {
                background: linear-gradient(135deg, #2d1b1b 0%, #2d1a2d 100%);
                border-color: #7c3030;
            }

            .error-state-enhanced::before {
                content: '';
                position: absolute;
                top: -50%;
                left: -50%;
                width: 200%;
                height: 200%;
                background: radial-gradient(circle, rgba(239, 68, 68, 0.03) 0%, transparent 70%);
                animation: error-pulse 3s infinite;
            }

            @keyframes error-pulse {
                0%, 100% { opacity: 0.3; transform: scale(1); }
                50% { opacity: 0.1; transform: scale(1.1); }
            }

            /* Smart Loading Messages */
            .loading-message {
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 12px;
                padding: 16px;
                background: rgba(37, 99, 235, 0.05);
                border-left: 4px solid #2563eb;
                border-radius: 8px;
                margin-top: 16px;
                animation: fade-in-up 0.5s ease-out;
            }

            @keyframes fade-in-up {
                from {
                    opacity: 0;
                    transform: translateY(20px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }

            /* Retry Button Enhancement */
            .retry-btn {
                background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                color: white;
                font-weight: 600;
                transition: all 0.3s ease;
                position: relative;
                overflow: hidden;
            }

            .retry-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(239, 68, 68, 0.3);
            }

            .retry-btn::before {
                content: '';
                position: absolute;
                top: 0;
                left: -100%;
                width: 100%;
                height: 100%;
                background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
                transition: left 0.5s;
            }

            .retry-btn:hover::before {
                left: 100%;
            }

            /* Loading Success Animation */
            .loading-success {
                animation: success-bounce 0.6s ease-out;
            }

            @keyframes success-bounce {
                0% { opacity: 0; transform: scale(0.3) rotate(-10deg); }
                50% { opacity: 1; transform: scale(1.05) rotate(2deg); }
                100% { opacity: 1; transform: scale(1) rotate(0deg); }
            }

            /* Contextual Loading States */
            .chart-skeleton {
                height: 300px;
                display: flex;
                flex-direction: column;
                gap: 12px;
                padding: 20px;
            }

            .chart-skeleton .skeleton-title {
                height: 24px;
                width: 60%;
                margin-bottom: 20px;
            }

            .chart-skeleton .skeleton-chart-area {
                flex: 1;
                display: flex;
                align-items: end;
                gap: 8px;
            }

            .chart-skeleton .skeleton-bar {
                flex: 1;
                background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
                background-size: 200% 100%;
                animation: enhanced-shimmer 1.5s infinite;
                animation-delay: var(--delay, 0s);
            }

            .chart-skeleton .skeleton-legend {
                display: flex;
                justify-content: center;
                gap: 16px;
                margin-top: 16px;
            }

            .chart-skeleton .skeleton-legend-item {
                height: 16px;
                width: 80px;
                background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
                background-size: 200% 100%;
                animation: enhanced-shimmer 1.5s infinite;
                animation-delay: var(--delay, 0s);
            }
        `;
        document.head.appendChild(style);
    }

    // Smart Chart Skeleton
    showChartSkeleton(containerId, chartType = 'bar') {
        const container = document.getElementById(containerId);
        if (!container) return;

        this.loadingStates.set(containerId, 'loading');

        let skeletonHTML = '';
        
        if (chartType === 'bar') {
            skeletonHTML = `
                <div class="chart-skeleton">
                    <div class="enhanced-skeleton skeleton-title"></div>
                    <div class="skeleton-chart-area">
                        ${Array.from({length: 6}, (_, i) => `
                            <div class="skeleton-bar enhanced-skeleton" 
                                 style="height: ${Math.random() * 80 + 20}%; --delay: ${i * 0.1}s;"></div>
                        `).join('')}
                    </div>
                    <div class="skeleton-legend">
                        ${Array.from({length: 3}, (_, i) => `
                            <div class="skeleton-legend-item enhanced-skeleton" 
                                 style="--delay: ${i * 0.15}s;"></div>
                        `).join('')}
                    </div>
                    <div class="loading-message">
                        <i class="fas fa-chart-bar text-primary"></i>
                        <span>กำลังโหลดข้อมูลกราฟ...</span>
                    </div>
                </div>
            `;
        } else if (chartType === 'pie') {
            skeletonHTML = `
                <div class="chart-skeleton">
                    <div class="enhanced-skeleton skeleton-title"></div>
                    <div class="skeleton-chart-area" style="justify-content: center; align-items: center;">
                        <div class="enhanced-skeleton" style="width: 200px; height: 200px; border-radius: 50%;"></div>
                    </div>
                    <div class="skeleton-legend">
                        ${Array.from({length: 4}, (_, i) => `
                            <div class="skeleton-legend-item enhanced-skeleton" 
                                 style="--delay: ${i * 0.1}s;"></div>
                        `).join('')}
                    </div>
                    <div class="loading-message">
                        <i class="fas fa-chart-pie text-primary"></i>
                        <span>กำลังโหลดข้อมูลแผนภูมิ...</span>
                    </div>
                </div>
            `;
        }

        container.innerHTML = skeletonHTML;
        
        // Show progress bar
        this.showProgressBar();
        
        // Auto-hide progress bar after reasonable time
        setTimeout(() => {
            if (this.loadingStates.get(containerId) === 'loading') {
                this.hideProgressBar();
            }
        }, 5000);
    }

    // Enhanced Error Display
    showEnhancedError(containerId, errorType = 'network', customMessage = null) {
        const container = document.getElementById(containerId);
        if (!container) return;

        this.loadingStates.set(containerId, 'error');
        this.hideProgressBar();

        const retryCount = this.retryCounters.get(containerId) || 0;
        
        const errorMessages = {
            network: {
                icon: 'fas fa-wifi',
                title: 'ปัญหาการเชื่อมต่อ',
                message: 'กรุณาตรวจสอบการเชื่อมต่ออินเทอร์เน็ต',
                color: 'warning'
            },
            timeout: {
                icon: 'fas fa-clock',
                title: 'หมดเวลาการโหลด',
                message: 'การโหลดข้อมูลใช้เวลานานกว่าปกติ',
                color: 'info'
            },
            server: {
                icon: 'fas fa-server',
                title: 'ข้อผิดพลาดเซิร์ฟเวอร์',
                message: 'เซิร์ฟเวอร์กำลังประสบปัญหา กรุณาลองใหม่ภายหลัง',
                color: 'danger'
            },
            data: {
                icon: 'fas fa-database',
                title: 'ไม่พบข้อมูล',
                message: 'ไม่มีข้อมูลในช่วงเวลาที่เลือก',
                color: 'secondary'
            }
        };

        const error = errorMessages[errorType] || errorMessages.network;
        const finalMessage = customMessage || error.message;

        container.innerHTML = `
            <div class="error-state-enhanced">
                <div class="error-state-icon text-${error.color}" style="font-size: 3rem; margin-bottom: 16px;">
                    <i class="${error.icon}"></i>
                </div>
                <h5 class="text-${error.color} mb-3">${error.title}</h5>
                <p class="text-muted mb-4">${finalMessage}</p>
                
                ${retryCount > 0 ? `
                    <div class="alert alert-warning alert-sm mb-3">
                        <i class="fas fa-info-circle me-2"></i>
                        พยายามแล้ว ${retryCount} ครั้ง
                    </div>
                ` : ''}
                
                <div class="d-flex justify-content-center gap-2">
                    <button class="retry-btn" onclick="window.enhancedLoader.retry('${containerId}')">
                        <i class="fas fa-redo me-2"></i>
                        ลองใหม่
                    </button>
                    
                    ${retryCount > 2 ? `
                        <button class="btn btn-outline-secondary" onclick="window.enhancedLoader.reportIssue('${containerId}')">
                            <i class="fas fa-bug me-2"></i>
                            รายงานปัญหา
                        </button>
                    ` : ''}
                </div>
                
                <div class="mt-3">
                    <small class="text-muted">
                        <i class="fas fa-lightbulb me-1"></i>
                        หากปัญหาเกิดขึ้นซ้ำ ลองรีเฟรชหน้าเว็บ หรือติดต่อผู้ดูแลระบบ
                    </small>
                </div>
            </div>
        `;
    }

    // Success Animation with Queue System
    showSuccess(containerId, message = 'โหลดข้อมูลสำเร็จ') {
        const container = document.getElementById(containerId);
        if (!container) return;

        this.loadingStates.set(containerId, 'success');
        this.hideProgressBar();

        // Add success class for animation (but don't clear content)
        container.classList.add('loading-success');
        
        // Clean up retry counter
        this.retryCounters.delete(containerId);

        // Queue the success message to prevent stacking
        this.queueSuccessMessage(message);

        // Remove success animation class
        setTimeout(() => {
            container.classList.remove('loading-success');
        }, 600);
    }

    // Queue success messages to prevent stacking
    queueSuccessMessage(message) {
        const now = Date.now();
        this.successQueue.set(now, message);

        // Clear existing timer
        if (this.successTimer) {
            clearTimeout(this.successTimer);
        }

        // Debounce - wait 500ms for more messages
        this.successTimer = setTimeout(() => {
            this.showQueuedSuccessMessages();
        }, 500);
    }

    // Show all queued success messages as one
    showQueuedSuccessMessages() {
        if (this.successQueue.size === 0) return;

        const messages = Array.from(this.successQueue.values());
        this.successQueue.clear();
        
        let finalMessage;
        if (messages.length === 1) {
            finalMessage = messages[0];
        } else if (messages.length <= 3) {
            finalMessage = `โหลดข้อมูล ${messages.length} รายการสำเร็จ`;
        } else {
            finalMessage = `โหลดข้อมูลทั้งหมดสำเร็จ (${messages.length} กราฟ)`;
        }

        // Remove any existing success messages first
        const existingMessages = document.querySelectorAll('.alert.alert-success.position-fixed');
        existingMessages.forEach(msg => msg.remove());

        // Show single consolidated success message
        const successMessage = document.createElement('div');
        successMessage.className = 'alert alert-success alert-dismissible fade show position-fixed';
        successMessage.style.cssText = 'top: 20px; right: 20px; z-index: 10000; max-width: 350px;';
        successMessage.innerHTML = `
            <i class="fas fa-check-circle me-2"></i>
            <strong>สำเร็จ!</strong> ${finalMessage}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(successMessage);
        
        // Auto remove success message
        setTimeout(() => {
            if (successMessage.parentNode) {
                successMessage.remove();
            }
        }, 4000); // Longer duration for consolidated message
    }

    // Progress Bar
    showProgressBar() {
        let progressBar = document.getElementById('global-progress-bar');
        if (!progressBar) {
            progressBar = document.createElement('div');
            progressBar.id = 'global-progress-bar';
            progressBar.className = 'progress-loading';
            document.body.appendChild(progressBar);
        }
        progressBar.style.display = 'block';
    }

    hideProgressBar() {
        const progressBar = document.getElementById('global-progress-bar');
        if (progressBar) {
            progressBar.style.display = 'none';
        }
    }

    // Retry Logic
    retry(containerId) {
        const currentRetry = this.retryCounters.get(containerId) || 0;
        this.retryCounters.set(containerId, currentRetry + 1);
        
        // Show loading again
        this.showChartSkeleton(containerId);
        
        // Trigger a custom retry event that charts can listen to
        const retryEvent = new CustomEvent('chartRetry', {
            detail: { containerId, retryCount: currentRetry + 1 }
        });
        document.dispatchEvent(retryEvent);
        
        console.log(`🔄 Retry attempt ${currentRetry + 1} for container: ${containerId}`);
    }

    // Report Issue
    reportIssue(containerId) {
        const issueData = {
            containerId,
            retryCount: this.retryCounters.get(containerId) || 0,
            userAgent: navigator.userAgent,
            timestamp: new Date().toISOString(),
            url: window.location.href
        };
        
        console.log('🐛 Issue Report:', issueData);
        
        // Show feedback form or send to support
        this.showFeedbackModal(issueData);
    }

    showFeedbackModal(issueData) {
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">
                            <i class="fas fa-bug text-warning me-2"></i>
                            รายงานปัญหา
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <p>ขอบคุณที่ช่วยรายงานปัญหา ข้อมูลนี้จะช่วยเราปรับปรุงระบบ</p>
                        <textarea class="form-control" rows="3" placeholder="อธิบายปัญหาที่เกิดขึ้น (ไม่บังคับ)"></textarea>
                        <small class="text-muted mt-2">
                            ข้อมูลเทคนิค: ${issueData.containerId} | Retry: ${issueData.retryCount} | ${new Date().toLocaleString('th-TH')}
                        </small>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">ปิด</button>
                        <button type="button" class="btn btn-warning" onclick="this.closest('.modal').remove()">
                            <i class="fas fa-paper-plane me-1"></i> ส่งรายงาน
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
        
        // Clean up modal after hide
        modal.addEventListener('hidden.bs.modal', () => {
            modal.remove();
        });
    }

    setupGlobalErrorHandler() {
        // Catch unhandled chart errors
        window.addEventListener('error', (e) => {
            if (e.error && e.error.message && e.error.message.includes('chart')) {
                console.warn('🔥 Chart error detected:', e.error);
                // Could auto-show error state for failed charts
            }
        });

        // Catch network errors
        window.addEventListener('online', () => {
            this.showToast('เชื่อมต่ออินเทอร์เน็ตแล้ว', 'success');
        });
        
        window.addEventListener('offline', () => {
            this.showToast('ขาดการเชื่อมต่ออินเทอร์เน็ต', 'warning');
        });
    }

    setupRetryHandlers() {
        // Listen for chart retry events
        document.addEventListener('chartRetry', (e) => {
            const { containerId, retryCount } = e.detail;
            console.log(`📊 Chart retry for ${containerId}, attempt ${retryCount}`);
            
            // You can add custom retry logic here
            // For now, just simulate a reload after delay
            setTimeout(() => {
                if (Math.random() > 0.3) { // 70% success rate simulation
                    this.showSuccess(containerId, 'โหลดข้อมูลสำเร็จ');
                } else {
                    this.showEnhancedError(containerId, 'network');
                }
            }, 2000);
        });
    }

    showToast(message, type = 'info', duration = 3000) {
        // Remove existing toasts of the same type to prevent stacking
        const existingToasts = document.querySelectorAll(`.alert.alert-${type === 'success' ? 'success' : type === 'warning' ? 'warning' : 'info'}.position-fixed`);
        existingToasts.forEach(toast => {
            if (toast.style.bottom === '20px') { // Only remove bottom toasts, not top ones
                toast.remove();
            }
        });

        const toast = document.createElement('div');
        toast.className = `alert alert-${type === 'success' ? 'success' : type === 'warning' ? 'warning' : 'info'} alert-dismissible position-fixed fade show`;
        toast.style.cssText = 'bottom: 20px; right: 20px; z-index: 10000; max-width: 350px;';
        toast.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'warning' ? 'exclamation-triangle' : 'info-circle'} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            if (toast.parentNode) {
                toast.remove();
            }
        }, duration);
    }

    // Utility method to get loading state
    getLoadingState(containerId) {
        return this.loadingStates.get(containerId) || 'idle';
    }

    // Clear loading state and prepare for chart render
    prepareForChart(containerId) {
        const container = document.getElementById(containerId);
        if (container) {
            // Clear skeleton/loading content
            container.innerHTML = '';
            // Clear loading state
            this.clearLoadingState(containerId);
            this.hideProgressBar();
        }
    }

    // Clear loading state
    clearLoadingState(containerId) {
        this.loadingStates.delete(containerId);
        this.retryCounters.delete(containerId);
    }
}

// Initialize global enhanced loader
window.enhancedLoader = new EnhancedLoader();

// Backward compatibility functions
window.showSkeletonLoader = (containerId, chartType = 'bar') => {
    window.enhancedLoader.showChartSkeleton(containerId, chartType);
};

window.showErrorState = (containerId, message) => {
    window.enhancedLoader.showEnhancedError(containerId, 'network', message);
};

console.log('✅ Enhanced Loading System initialized');