/* ===== PERFORMANCE OPTIMIZATION SYSTEM ===== */
/* Lazy loading, caching, and performance enhancements */

class PerformanceOptimizer {
    constructor() {
        this.lazyElements = new Map();
        this.cache = new Map();
        this.observers = new Map();
        this.bundleCache = new Map();
        this.performanceMetrics = {
            loadStart: performance.now(),
            chartLoads: [],
            cacheHits: 0,
            cacheMisses: 0
        };
        this.init();
    }

    init() {
        this.setupIntersectionObserver();
        this.setupPerformanceMonitoring();
        this.setupCacheSystem();
        this.setupBundleOptimization();
        console.log('🚀 Performance Optimizer initialized');
    }

    // Intersection Observer for lazy loading
    setupIntersectionObserver() {
        const observerOptions = {
            root: null,
            rootMargin: '50px', // Load 50px before element comes into view
            threshold: 0.1
        };

        this.intersectionObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    this.handleElementVisible(entry.target);
                }
            });
        }, observerOptions);

        console.log('👀 Intersection Observer ready');
    }

    // Register element for lazy loading
    registerLazyElement(elementId, loadCallback, priority = 'normal') {
        const element = document.getElementById(elementId);
        if (!element) {
            console.warn('⚠️ Lazy element not found:', elementId);
            return;
        }

        this.lazyElements.set(elementId, {
            element,
            loadCallback,
            priority,
            loaded: false,
            loading: false
        });

        this.intersectionObserver.observe(element);
        console.log(`📋 Registered lazy element: ${elementId} (${priority})`);
    }

    // Handle when element becomes visible
    handleElementVisible(element) {
        const elementId = element.id;
        const lazyData = this.lazyElements.get(elementId);
        
        if (!lazyData || lazyData.loaded || lazyData.loading) return;

        lazyData.loading = true;
        console.log(`👁️ Element visible, loading: ${elementId}`);

        // Add visual loading indicator
        this.showLazyLoadingIndicator(element);

        // Load with appropriate delay based on priority
        const delay = this.getPriorityDelay(lazyData.priority);
        
        setTimeout(() => {
            this.loadLazyElement(elementId);
        }, delay);
    }

    // Get delay based on priority
    getPriorityDelay(priority) {
        switch (priority) {
            case 'high': return 0;
            case 'normal': return 100;
            case 'low': return 300;
            default: return 100;
        }
    }

    // Show loading indicator for lazy element
    showLazyLoadingIndicator(element) {
        const indicator = document.createElement('div');
        indicator.className = 'lazy-loading-indicator';
        indicator.innerHTML = `
            <div class="d-flex align-items-center justify-content-center h-100" style="min-height: 200px;">
                <div class="text-center">
                    <div class="spinner-border text-primary mb-2" role="status">
                        <span class="visually-hidden">กำลังโหลด...</span>
                    </div>
                    <p class="text-muted mb-0">กำลังโหลดเนื้อหา...</p>
                </div>
            </div>
        `;
        
        // Add to element without clearing existing content
        element.style.position = 'relative';
        element.appendChild(indicator);
    }

    // Load lazy element
    async loadLazyElement(elementId) {
        const lazyData = this.lazyElements.get(elementId);
        if (!lazyData) return;

        const startTime = performance.now();

        try {
            // Remove loading indicator
            const indicator = lazyData.element.querySelector('.lazy-loading-indicator');
            if (indicator) indicator.remove();

            // Execute load callback
            await lazyData.loadCallback();
            
            lazyData.loaded = true;
            lazyData.loading = false;

            // Stop observing this element
            this.intersectionObserver.unobserve(lazyData.element);

            // Record performance metric
            const loadTime = performance.now() - startTime;
            this.performanceMetrics.chartLoads.push({
                elementId,
                loadTime,
                timestamp: Date.now()
            });

            console.log(`✅ Lazy loaded: ${elementId} (${loadTime.toFixed(2)}ms)`);

        } catch (error) {
            console.error(`❌ Lazy load failed: ${elementId}`, error);
            lazyData.loading = false;
            
            // Show error state
            this.showLazyLoadError(lazyData.element, error.message);
        }
    }

    // Show lazy load error
    showLazyLoadError(element, message) {
        const indicator = element.querySelector('.lazy-loading-indicator');
        if (indicator) {
            indicator.innerHTML = `
                <div class="alert alert-warning text-center m-3">
                    <i class="fas fa-exclamation-triangle mb-2"></i>
                    <p class="mb-2">ไม่สามารถโหลดเนื้อหาได้</p>
                    <small class="text-muted">${message}</small>
                    <br>
                    <button class="btn btn-sm btn-outline-warning mt-2" onclick="location.reload()">
                        <i class="fas fa-redo"></i> ลองใหม่
                    </button>
                </div>
            `;
        }
    }

    // Cache System
    setupCacheSystem() {
        // Memory cache with TTL
        this.memoryCache = new Map();
        this.cacheExpiry = new Map();
        
        // Default cache TTL: 5 minutes
        this.defaultTTL = 5 * 60 * 1000;
        
        console.log('🗄️ Cache system ready');
    }

    // Set cache with TTL
    setCache(key, data, ttl = null) {
        const expires = Date.now() + (ttl || this.defaultTTL);
        this.memoryCache.set(key, data);
        this.cacheExpiry.set(key, expires);
        
        // Clean up expired cache periodically
        this.scheduleCleanup();
        
        console.log(`💾 Cached: ${key} (TTL: ${ttl || this.defaultTTL}ms)`);
    }

    // Get from cache
    getCache(key) {
        const expires = this.cacheExpiry.get(key);
        
        if (!expires || Date.now() > expires) {
            // Expired or not found
            this.memoryCache.delete(key);
            this.cacheExpiry.delete(key);
            this.performanceMetrics.cacheMisses++;
            return null;
        }

        this.performanceMetrics.cacheHits++;
        return this.memoryCache.get(key);
    }

    // Clear cache
    clearCache(pattern = null) {
        if (pattern) {
            // Clear by pattern
            const regex = new RegExp(pattern);
            for (const key of this.memoryCache.keys()) {
                if (regex.test(key)) {
                    this.memoryCache.delete(key);
                    this.cacheExpiry.delete(key);
                }
            }
            console.log(`🗑️ Cache cleared (pattern: ${pattern})`);
        } else {
            // Clear all
            this.memoryCache.clear();
            this.cacheExpiry.clear();
            console.log('🗑️ All cache cleared');
        }
    }

    // Schedule cache cleanup
    scheduleCleanup() {
        if (this.cleanupTimer) return;

        this.cleanupTimer = setInterval(() => {
            this.cleanupExpiredCache();
        }, 60000); // Check every minute
    }

    // Clean up expired cache entries
    cleanupExpiredCache() {
        const now = Date.now();
        let cleaned = 0;

        for (const [key, expires] of this.cacheExpiry.entries()) {
            if (now > expires) {
                this.memoryCache.delete(key);
                this.cacheExpiry.delete(key);
                cleaned++;
            }
        }

        if (cleaned > 0) {
            console.log(`🧹 Cache cleanup: ${cleaned} expired entries removed`);
        }
    }

    // Bundle Optimization
    setupBundleOptimization() {
        // Preload critical resources
        this.preloadCriticalResources();
        
        // Setup resource hints
        this.setupResourceHints();
        
        console.log('📦 Bundle optimization ready');
    }

    // Preload critical resources
    preloadCriticalResources() {
        const criticalResources = [
            'https://cdn.jsdelivr.net/npm/apexcharts@latest',
            'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css'
        ];

        criticalResources.forEach(url => {
            const link = document.createElement('link');
            link.rel = 'preload';
            link.as = url.includes('.css') ? 'style' : 'script';
            link.href = url;
            document.head.appendChild(link);
        });

        console.log('⚡ Critical resources preloaded');
    }

    // Setup resource hints
    setupResourceHints() {
        // DNS prefetch for external domains
        const domains = [
            'cdn.jsdelivr.net',
            'cdnjs.cloudflare.com',
            'fonts.googleapis.com'
        ];

        domains.forEach(domain => {
            const link = document.createElement('link');
            link.rel = 'dns-prefetch';
            link.href = `//${domain}`;
            document.head.appendChild(link);
        });

        console.log('🔗 Resource hints added');
    }

    // Performance Monitoring
    setupPerformanceMonitoring() {
        // Monitor Core Web Vitals
        this.observeWebVitals();
        
        // Monitor custom metrics
        this.setupCustomMetrics();
        
        console.log('📊 Performance monitoring active');
    }

    // Observe Web Vitals
    observeWebVitals() {
        // Largest Contentful Paint (LCP)
        const lcpObserver = new PerformanceObserver((list) => {
            const entries = list.getEntries();
            const lastEntry = entries[entries.length - 1];
            console.log('📈 LCP:', lastEntry.startTime.toFixed(2) + 'ms');
            this.performanceMetrics.lcp = lastEntry.startTime;
        });

        try {
            lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] });
        } catch (e) {
            console.warn('⚠️ LCP observer not supported');
        }

        // First Input Delay (FID)
        const fidObserver = new PerformanceObserver((list) => {
            for (const entry of list.getEntries()) {
                console.log('📈 FID:', entry.processingStart - entry.startTime + 'ms');
                this.performanceMetrics.fid = entry.processingStart - entry.startTime;
            }
        });

        try {
            fidObserver.observe({ entryTypes: ['first-input'] });
        } catch (e) {
            console.warn('⚠️ FID observer not supported');
        }

        // Cumulative Layout Shift (CLS)
        let clsValue = 0;
        const clsObserver = new PerformanceObserver((list) => {
            for (const entry of list.getEntries()) {
                if (!entry.hadRecentInput) {
                    clsValue += entry.value;
                }
            }
            console.log('📈 CLS:', clsValue.toFixed(4));
            this.performanceMetrics.cls = clsValue;
        });

        try {
            clsObserver.observe({ entryTypes: ['layout-shift'] });
        } catch (e) {
            console.warn('⚠️ CLS observer not supported');
        }
    }

    // Setup custom metrics
    setupCustomMetrics() {
        // Track page load complete
        window.addEventListener('load', () => {
            const loadTime = performance.now() - this.performanceMetrics.loadStart;
            this.performanceMetrics.pageLoadTime = loadTime;
            console.log('📈 Page Load Time:', loadTime.toFixed(2) + 'ms');
        });

        // Track DOM content loaded
        document.addEventListener('DOMContentLoaded', () => {
            const domTime = performance.now() - this.performanceMetrics.loadStart;
            this.performanceMetrics.domContentLoaded = domTime;
            console.log('📈 DOM Content Loaded:', domTime.toFixed(2) + 'ms');
        });
    }

    // Get performance report
    getPerformanceReport() {
        const report = {
            ...this.performanceMetrics,
            cacheEfficiency: this.performanceMetrics.cacheHits / 
                           (this.performanceMetrics.cacheHits + this.performanceMetrics.cacheMisses) * 100,
            avgChartLoadTime: this.performanceMetrics.chartLoads.length > 0 
                           ? this.performanceMetrics.chartLoads.reduce((sum, load) => sum + load.loadTime, 0) / 
                             this.performanceMetrics.chartLoads.length 
                           : 0,
            memoryUsage: this.getMemoryUsage()
        };

        return report;
    }

    // Get memory usage
    getMemoryUsage() {
        if ('memory' in performance) {
            return {
                used: (performance.memory.usedJSHeapSize / 1024 / 1024).toFixed(2) + ' MB',
                total: (performance.memory.totalJSHeapSize / 1024 / 1024).toFixed(2) + ' MB',
                limit: (performance.memory.jsHeapSizeLimit / 1024 / 1024).toFixed(2) + ' MB'
            };
        }
        return null;
    }

    // Log performance report
    logPerformanceReport() {
        const report = this.getPerformanceReport();
        console.log('📊 Performance Report:', report);
        
        // Show performance summary in UI
        this.showPerformanceSummary(report);
    }

    // Show performance summary in UI
    showPerformanceSummary(report) {
        const summary = document.createElement('div');
        summary.className = 'alert alert-info position-fixed';
        summary.style.cssText = 'bottom: 20px; left: 20px; z-index: 9999; max-width: 300px; font-size: 0.8rem;';
        summary.innerHTML = `
            <h6><i class="fas fa-tachometer-alt"></i> Performance Summary</h6>
            <div class="row g-1">
                <div class="col-6">Page Load:</div>
                <div class="col-6">${report.pageLoadTime?.toFixed(0) || 'N/A'}ms</div>
                <div class="col-6">Cache Hit:</div>
                <div class="col-6">${report.cacheEfficiency?.toFixed(1) || '0'}%</div>
                <div class="col-6">Avg Chart:</div>
                <div class="col-6">${report.avgChartLoadTime?.toFixed(0) || '0'}ms</div>
            </div>
            <button class="btn btn-sm btn-outline-info mt-2 w-100" onclick="this.parentElement.remove()">
                Close
            </button>
        `;
        
        document.body.appendChild(summary);
        
        // Auto remove after 10 seconds
        setTimeout(() => {
            if (summary.parentNode) {
                summary.remove();
            }
        }, 10000);
    }

    // Utility: Debounce function calls
    debounce(func, wait) {
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

    // Utility: Throttle function calls
    throttle(func, limit) {
        let inThrottle;
        return function(...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }

    // Clean up resources
    destroy() {
        this.intersectionObserver?.disconnect();
        this.observers.clear();
        this.clearCache();
        if (this.cleanupTimer) {
            clearInterval(this.cleanupTimer);
        }
        console.log('🧹 Performance Optimizer cleaned up');
    }
}

// Initialize global performance optimizer
window.performanceOptimizer = new PerformanceOptimizer();

// Convenience functions for lazy loading charts
window.lazyLoadChart = (chartId, loadCallback, priority = 'normal') => {
    window.performanceOptimizer.registerLazyElement(chartId, loadCallback, priority);
};

window.cacheData = (key, data, ttl) => {
    window.performanceOptimizer.setCache(key, data, ttl);
};

window.getCachedData = (key) => {
    return window.performanceOptimizer.getCache(key);
};

// Show performance report (debug)
window.showPerformanceReport = () => {
    window.performanceOptimizer.logPerformanceReport();
};

// Auto-show performance report after page load (development mode)
window.addEventListener('load', () => {
    setTimeout(() => {
        if (window.location.hostname === 'localhost') {
            window.performanceOptimizer.logPerformanceReport();
        }
    }, 3000);
});

console.log('🚀 Performance Optimization System loaded');