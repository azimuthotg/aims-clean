/* ===== ADVANCED FILTERING SYSTEM ===== */
/* Comprehensive filtering with date ranges, multi-select, and persistence */

class AdvancedFilterManager {
    constructor() {
        this.filters = {
            dateRange: { start: null, end: null },
            faculties: [],
            levels: [],
            quickFilter: null,
            customYear: null
        };
        
        this.availableData = {
            years: [],
            faculties: [],
            levels: []
        };
        
        this.callbacks = [];
        this.storageKey = 'aims-filters';
        this.init();
    }

    init() {
        this.injectCSS();
        this.loadSavedFilters();
        this.setupEventListeners();
        console.log('✅ Advanced Filter Manager initialized');
    }

    injectCSS() {
        const style = document.createElement('style');
        style.textContent = `
            /* Advanced Filter Panel Styling */
            .filter-panel {
                background: linear-gradient(135deg, rgba(37, 99, 235, 0.05) 0%, rgba(59, 130, 246, 0.08) 100%);
                border: 2px solid rgba(37, 99, 235, 0.1);
                border-radius: 16px;
                padding: 24px;
                margin-bottom: 24px;
                box-shadow: 0 4px 20px rgba(37, 99, 235, 0.08);
                transition: all 0.3s ease;
            }

            .filter-panel:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 30px rgba(37, 99, 235, 0.15);
            }

            [data-theme="dark"] .filter-panel {
                background: linear-gradient(135deg, rgba(45, 45, 45, 0.8) 0%, rgba(60, 60, 60, 0.6) 100%);
                border-color: rgba(255, 255, 255, 0.1);
            }

            /* Filter Header */
            .filter-header {
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin-bottom: 20px;
                padding-bottom: 16px;
                border-bottom: 2px solid rgba(37, 99, 235, 0.1);
            }

            .filter-header h5 {
                margin: 0;
                color: #2563eb;
                font-weight: 600;
                display: flex;
                align-items: center;
                gap: 8px;
            }

            [data-theme="dark"] .filter-header h5 {
                color: #60a5fa;
            }

            .filter-toggle {
                background: none;
                border: none;
                color: #6b7280;
                font-size: 1.2rem;
                cursor: pointer;
                transition: all 0.2s ease;
                padding: 8px;
                border-radius: 6px;
            }

            .filter-toggle:hover {
                background: rgba(37, 99, 235, 0.1);
                color: #2563eb;
            }

            /* Filter Controls */
            .filter-controls {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                align-items: start;
            }

            @media (max-width: 768px) {
                .filter-controls {
                    grid-template-columns: 1fr;
                    gap: 16px;
                }
            }

            .filter-group {
                display: flex;
                flex-direction: column;
                gap: 8px;
            }

            .filter-label {
                font-weight: 600;
                color: #374151;
                font-size: 0.9rem;
                display: flex;
                align-items: center;
                gap: 6px;
            }

            [data-theme="dark"] .filter-label {
                color: #e5e7eb;
            }

            /* Date Range Picker */
            .date-range-container {
                position: relative;
            }

            .date-range-input {
                width: 100%;
                padding: 10px 16px;
                border: 2px solid #e5e7eb;
                border-radius: 8px;
                background: white;
                font-size: 0.9rem;
                transition: all 0.2s ease;
                cursor: pointer;
            }

            .date-range-input:hover {
                border-color: #2563eb;
            }

            .date-range-input:focus {
                outline: none;
                border-color: #2563eb;
                box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
            }

            [data-theme="dark"] .date-range-input {
                background: #374151;
                border-color: #4b5563;
                color: #e5e7eb;
            }

            /* Multi-Select Dropdown */
            .multi-select-container {
                position: relative;
            }

            .multi-select-trigger {
                width: 100%;
                padding: 10px 16px;
                border: 2px solid #e5e7eb;
                border-radius: 8px;
                background: white;
                cursor: pointer;
                display: flex;
                justify-content: space-between;
                align-items: center;
                min-height: 44px;
                transition: all 0.2s ease;
            }

            .multi-select-trigger:hover {
                border-color: #2563eb;
            }

            [data-theme="dark"] .multi-select-trigger {
                background: #374151;
                border-color: #4b5563;
                color: #e5e7eb;
            }

            .multi-select-dropdown {
                position: absolute;
                top: 100%;
                left: 0;
                right: 0;
                background: white;
                border: 2px solid #e5e7eb;
                border-top: none;
                border-radius: 0 0 8px 8px;
                max-height: 300px;
                overflow-y: auto;
                z-index: 1000;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
                display: none;
            }

            .multi-select-dropdown.show {
                display: block;
            }

            [data-theme="dark"] .multi-select-dropdown {
                background: #374151;
                border-color: #4b5563;
            }

            .multi-select-search {
                padding: 12px 16px;
                border-bottom: 1px solid #e5e7eb;
                position: sticky;
                top: 0;
                background: inherit;
                z-index: 1;
            }

            .multi-select-search input {
                width: 100%;
                padding: 8px 12px;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                font-size: 0.875rem;
            }

            [data-theme="dark"] .multi-select-search input {
                background: #4b5563;
                border-color: #6b7280;
                color: #e5e7eb;
            }

            .multi-select-actions {
                padding: 8px 16px;
                border-bottom: 1px solid #e5e7eb;
                display: flex;
                gap: 8px;
            }

            .multi-select-action {
                padding: 4px 8px;
                background: none;
                border: 1px solid #d1d5db;
                border-radius: 4px;
                font-size: 0.75rem;
                cursor: pointer;
                transition: all 0.2s ease;
            }

            .multi-select-action:hover {
                background: #f3f4f6;
            }

            .multi-select-options {
                max-height: 200px;
                overflow-y: auto;
            }

            .multi-select-option {
                padding: 10px 16px;
                display: flex;
                align-items: center;
                gap: 8px;
                cursor: pointer;
                transition: background-color 0.2s ease;
                font-size: 0.9rem;
            }

            .multi-select-option:hover {
                background: rgba(37, 99, 235, 0.05);
            }

            .multi-select-option.selected {
                background: rgba(37, 99, 235, 0.1);
                color: #2563eb;
                font-weight: 500;
            }

            [data-theme="dark"] .multi-select-option:hover {
                background: rgba(96, 165, 250, 0.1);
            }

            [data-theme="dark"] .multi-select-option.selected {
                background: rgba(96, 165, 250, 0.2);
                color: #60a5fa;
            }

            /* Quick Filter Buttons */
            .quick-filters {
                display: flex;
                flex-wrap: wrap;
                gap: 8px;
                margin-top: 8px;
            }

            .quick-filter-btn {
                padding: 6px 12px;
                background: white;
                border: 2px solid #e5e7eb;
                border-radius: 20px;
                font-size: 0.8rem;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.2s ease;
                display: flex;
                align-items: center;
                gap: 4px;
            }

            .quick-filter-btn:hover {
                border-color: #2563eb;
                background: rgba(37, 99, 235, 0.05);
            }

            .quick-filter-btn.active {
                background: #2563eb;
                border-color: #2563eb;
                color: white;
            }

            [data-theme="dark"] .quick-filter-btn {
                background: #374151;
                border-color: #4b5563;
                color: #e5e7eb;
            }

            [data-theme="dark"] .quick-filter-btn:hover {
                border-color: #60a5fa;
                background: rgba(96, 165, 250, 0.1);
            }

            /* Filter Actions */
            .filter-actions {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-top: 20px;
                padding-top: 16px;
                border-top: 1px solid rgba(37, 99, 235, 0.1);
            }

            .filter-actions-left {
                display: flex;
                gap: 8px;
            }

            .filter-actions-right {
                display: flex;
                gap: 8px;
            }

            .filter-btn {
                padding: 8px 16px;
                border: none;
                border-radius: 8px;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.2s ease;
                display: flex;
                align-items: center;
                gap: 6px;
                font-size: 0.9rem;
            }

            .filter-btn-primary {
                background: #2563eb;
                color: white;
            }

            .filter-btn-primary:hover {
                background: #1d4ed8;
                transform: translateY(-1px);
            }

            .filter-btn-secondary {
                background: #f3f4f6;
                color: #374151;
                border: 1px solid #d1d5db;
            }

            .filter-btn-secondary:hover {
                background: #e5e7eb;
            }

            .filter-btn-danger {
                background: #ef4444;
                color: white;
            }

            .filter-btn-danger:hover {
                background: #dc2626;
            }

            /* Filter Summary */
            .filter-summary {
                display: flex;
                align-items: center;
                gap: 8px;
                margin-top: 12px;
                font-size: 0.85rem;
                color: #6b7280;
            }

            .filter-tag {
                background: rgba(37, 99, 235, 0.1);
                color: #2563eb;
                padding: 4px 8px;
                border-radius: 12px;
                font-size: 0.75rem;
                font-weight: 500;
                display: flex;
                align-items: center;
                gap: 4px;
            }

            .filter-tag .remove {
                cursor: pointer;
                opacity: 0.7;
                transition: opacity 0.2s ease;
            }

            .filter-tag .remove:hover {
                opacity: 1;
            }

            /* Animation for filter panel */
            .filter-panel.collapsed .filter-controls {
                display: none;
            }

            .filter-panel.collapsed .filter-actions {
                display: none;
            }

            .filter-panel.collapsed .filter-summary {
                margin-top: 0;
            }

            /* Loading state for filters */
            .filter-loading {
                opacity: 0.6;
                pointer-events: none;
                position: relative;
            }

            .filter-loading::after {
                content: '';
                position: absolute;
                top: 50%;
                left: 50%;
                width: 20px;
                height: 20px;
                border: 2px solid #2563eb;
                border-top: 2px solid transparent;
                border-radius: 50%;
                animation: filter-spin 1s linear infinite;
                transform: translate(-50%, -50%);
            }

            @keyframes filter-spin {
                0% { transform: translate(-50%, -50%) rotate(0deg); }
                100% { transform: translate(-50%, -50%) rotate(360deg); }
            }
        `;
        document.head.appendChild(style);
    }

    // Load saved filters from localStorage
    loadSavedFilters() {
        try {
            const saved = localStorage.getItem(this.storageKey);
            if (saved) {
                this.filters = { ...this.filters, ...JSON.parse(saved) };
                console.log('📂 Loaded saved filters:', this.filters);
            }
        } catch (error) {
            console.warn('⚠️ Error loading saved filters:', error);
        }
    }

    // Save filters to localStorage
    saveFilters() {
        try {
            localStorage.setItem(this.storageKey, JSON.stringify(this.filters));
            console.log('💾 Filters saved');
        } catch (error) {
            console.warn('⚠️ Error saving filters:', error);
        }
    }

    // Initialize data from page context
    setAvailableData(data) {
        this.availableData = { ...this.availableData, ...data };
        console.log('📊 Available data updated:', this.availableData);
    }

    // Create filter panel HTML
    createFilterPanel(containerId) {
        const container = document.getElementById(containerId);
        if (!container) {
            console.error('❌ Filter container not found:', containerId);
            return;
        }

        container.innerHTML = `
            <div class="filter-panel" id="advanced-filter-panel">
                <div class="filter-header">
                    <h5>
                        <i class="fas fa-filter"></i>
                        ตัวกรองข้อมูลขั้นสูง
                        <span class="badge bg-primary ms-2" id="filter-count">0</span>
                    </h5>
                    <button class="filter-toggle" id="filter-toggle" title="ซ่อน/แสดงตัวกรอง">
                        <i class="fas fa-chevron-up"></i>
                    </button>
                </div>

                <div class="filter-controls" id="filter-controls">
                    <div class="filter-group">
                        <label class="filter-label">
                            <i class="fas fa-calendar-range"></i>
                            ช่วงปีการศึกษา
                        </label>
                        <div class="date-range-container">
                            <input type="text" class="date-range-input" id="date-range-input" 
                                   placeholder="เลือกช่วงปีการศึกษา" readonly>
                        </div>
                        <div class="quick-filters">
                            <button class="quick-filter-btn" data-range="current">
                                <i class="fas fa-clock"></i> ปีปัจจุบัน
                            </button>
                            <button class="quick-filter-btn" data-range="recent">
                                <i class="fas fa-history"></i> 3 ปีล่าสุด
                            </button>
                            <button class="quick-filter-btn" data-range="all">
                                <i class="fas fa-infinity"></i> ทั้งหมด
                            </button>
                        </div>
                    </div>

                    <div class="filter-group">
                        <label class="filter-label">
                            <i class="fas fa-university"></i>
                            คณะ
                        </label>
                        <div class="multi-select-container">
                            <div class="multi-select-trigger" id="faculty-select-trigger">
                                <span class="selected-text">เลือกคณะ...</span>
                                <i class="fas fa-chevron-down"></i>
                            </div>
                            <div class="multi-select-dropdown" id="faculty-select-dropdown">
                                <div class="multi-select-search">
                                    <input type="text" placeholder="ค้นหาคณะ..." id="faculty-search">
                                </div>
                                <div class="multi-select-actions">
                                    <button class="multi-select-action" id="faculty-select-all">เลือกทั้งหมด</button>
                                    <button class="multi-select-action" id="faculty-clear-all">ล้างทั้งหมด</button>
                                </div>
                                <div class="multi-select-options" id="faculty-options"></div>
                            </div>
                        </div>
                        <div class="quick-filters">
                            <button class="quick-filter-btn" data-faculty-size="large">
                                <i class="fas fa-arrow-up"></i> คณะใหญ่ (500+ คน)
                            </button>
                            <button class="quick-filter-btn" data-faculty-size="medium">
                                <i class="fas fa-minus"></i> คณะกลาง (100-499 คน)
                            </button>
                            <button class="quick-filter-btn" data-faculty-size="small">
                                <i class="fas fa-arrow-down"></i> คณะเล็ก (<100 คน)
                            </button>
                        </div>
                    </div>

                    <div class="filter-group">
                        <label class="filter-label">
                            <i class="fas fa-graduation-cap"></i>
                            ระดับการศึกษา
                        </label>
                        <div class="multi-select-container">
                            <div class="multi-select-trigger" id="level-select-trigger">
                                <span class="selected-text">เลือกระดับการศึกษา...</span>
                                <i class="fas fa-chevron-down"></i>
                            </div>
                            <div class="multi-select-dropdown" id="level-select-dropdown">
                                <div class="multi-select-actions">
                                    <button class="multi-select-action" id="level-select-all">เลือกทั้งหมด</button>
                                    <button class="multi-select-action" id="level-clear-all">ล้างทั้งหมด</button>
                                </div>
                                <div class="multi-select-options" id="level-options"></div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="filter-actions">
                    <div class="filter-actions-left">
                        <button class="filter-btn filter-btn-primary" id="apply-filters">
                            <i class="fas fa-search"></i> กรองข้อมูล
                        </button>
                        <button class="filter-btn filter-btn-secondary" id="reset-filters">
                            <i class="fas fa-undo"></i> รีเซ็ต
                        </button>
                    </div>
                    <div class="filter-actions-right">
                        <button class="filter-btn filter-btn-secondary" id="save-preset">
                            <i class="fas fa-bookmark"></i> บันทึกการตั้งค่า
                        </button>
                        <button class="filter-btn filter-btn-danger" id="clear-all-filters">
                            <i class="fas fa-times"></i> ล้างทั้งหมด
                        </button>
                    </div>
                </div>

                <div class="filter-summary" id="filter-summary"></div>
            </div>
        `;

        this.setupFilterEvents();
        this.updateFilterDisplay();
    }

    setupFilterEvents() {
        // Toggle filter panel
        const toggle = document.getElementById('filter-toggle');
        const panel = document.getElementById('advanced-filter-panel');
        if (toggle && panel) {
            toggle.addEventListener('click', () => {
                panel.classList.toggle('collapsed');
                const icon = toggle.querySelector('i');
                icon.className = panel.classList.contains('collapsed') 
                    ? 'fas fa-chevron-down' 
                    : 'fas fa-chevron-up';
            });
        }

        // Date range quick filters
        document.querySelectorAll('[data-range]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.setQuickDateRange(e.target.dataset.range);
            });
        });

        // Faculty size quick filters
        document.querySelectorAll('[data-faculty-size]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.setQuickFacultySize(e.target.dataset.facultySize);
            });
        });

        // Filter actions
        document.getElementById('apply-filters')?.addEventListener('click', () => {
            this.applyFilters();
        });

        document.getElementById('reset-filters')?.addEventListener('click', () => {
            this.resetFilters();
        });

        document.getElementById('clear-all-filters')?.addEventListener('click', () => {
            this.clearAllFilters();
        });

        document.getElementById('save-preset')?.addEventListener('click', () => {
            this.savePreset();
        });

        this.setupMultiSelect('faculty');
        this.setupMultiSelect('level');
    }

    setupMultiSelect(type) {
        const trigger = document.getElementById(`${type}-select-trigger`);
        const dropdown = document.getElementById(`${type}-select-dropdown`);
        const options = document.getElementById(`${type}-options`);
        const search = document.getElementById(`${type}-search`);
        const selectAll = document.getElementById(`${type}-select-all`);
        const clearAll = document.getElementById(`${type}-clear-all`);

        if (!trigger || !dropdown || !options) return;

        // Toggle dropdown
        trigger.addEventListener('click', () => {
            dropdown.classList.toggle('show');
            this.populateMultiSelectOptions(type);
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!trigger.contains(e.target) && !dropdown.contains(e.target)) {
                dropdown.classList.remove('show');
            }
        });

        // Search functionality
        if (search) {
            search.addEventListener('input', (e) => {
                this.filterMultiSelectOptions(type, e.target.value);
            });
        }

        // Select/Clear all
        selectAll?.addEventListener('click', () => {
            this.selectAllOptions(type);
        });

        clearAll?.addEventListener('click', () => {
            this.clearAllOptions(type);
        });
    }

    setupEventListeners() {
        // Listen for data updates from the page
        document.addEventListener('filterDataUpdate', (e) => {
            this.setAvailableData(e.detail);
        });
    }

    // Register callback for filter changes
    onFilterChange(callback) {
        this.callbacks.push(callback);
    }

    // Trigger all callbacks when filters change
    triggerFilterChange() {
        this.callbacks.forEach(callback => {
            try {
                callback(this.getActiveFilters());
            } catch (error) {
                console.error('❌ Filter callback error:', error);
            }
        });
    }

    // Get current active filters
    getActiveFilters() {
        return {
            ...this.filters,
            isActive: this.hasActiveFilters()
        };
    }

    // Check if any filters are active
    hasActiveFilters() {
        return (
            this.filters.dateRange.start ||
            this.filters.dateRange.end ||
            this.filters.faculties.length > 0 ||
            this.filters.levels.length > 0 ||
            this.filters.quickFilter
        );
    }

    // Apply current filters
    applyFilters() {
        console.log('🔍 Applying filters:', this.filters);
        this.saveFilters();
        this.updateFilterDisplay();
        this.triggerFilterChange();
        
        // Show loading state
        document.getElementById('advanced-filter-panel')?.classList.add('filter-loading');
        
        setTimeout(() => {
            document.getElementById('advanced-filter-panel')?.classList.remove('filter-loading');
        }, 500);
    }

    // Reset filters to saved state
    resetFilters() {
        this.loadSavedFilters();
        this.updateFilterDisplay();
        console.log('🔄 Filters reset');
    }

    // Clear all filters
    clearAllFilters() {
        this.filters = {
            dateRange: { start: null, end: null },
            faculties: [],
            levels: [],
            quickFilter: null,
            customYear: null
        };
        this.saveFilters();
        this.updateFilterDisplay();
        this.triggerFilterChange();
        console.log('🗑️ All filters cleared');
    }

    // Update filter display
    updateFilterDisplay() {
        this.updateFilterCount();
        this.updateFilterSummary();
        this.updateMultiSelectDisplay();
        this.updateQuickFilterButtons();
    }

    updateFilterCount() {
        const count = this.getActiveFilterCount();
        const badge = document.getElementById('filter-count');
        if (badge) {
            badge.textContent = count;
            badge.className = count > 0 ? 'badge bg-primary ms-2' : 'badge bg-secondary ms-2';
        }
    }

    getActiveFilterCount() {
        let count = 0;
        if (this.filters.dateRange.start || this.filters.dateRange.end) count++;
        if (this.filters.faculties.length > 0) count++;
        if (this.filters.levels.length > 0) count++;
        if (this.filters.quickFilter) count++;
        return count;
    }

    updateFilterSummary() {
        const summary = document.getElementById('filter-summary');
        if (!summary) return;

        const tags = [];
        
        // Date range tag
        if (this.filters.dateRange.start || this.filters.dateRange.end) {
            const start = this.filters.dateRange.start || 'ไม่จำกัด';
            const end = this.filters.dateRange.end || 'ไม่จำกัด';
            tags.push(`ปี: ${start} - ${end}`);
        }

        // Faculty tags
        if (this.filters.faculties.length > 0) {
            const count = this.filters.faculties.length;
            tags.push(`คณะ: ${count} รายการ`);
        }

        // Level tags
        if (this.filters.levels.length > 0) {
            const count = this.filters.levels.length;
            tags.push(`ระดับ: ${count} รายการ`);
        }

        // Quick filter tag
        if (this.filters.quickFilter) {
            tags.push(`ตัวกรองด่วน: ${this.filters.quickFilter}`);
        }

        summary.innerHTML = tags.length > 0 
            ? `<i class="fas fa-tags"></i> ${tags.map(tag => `<span class="filter-tag">${tag}</span>`).join('')}`
            : '<i class="fas fa-info-circle"></i> ไม่มีตัวกรองที่เปิดใช้งาน';
    }

    // Quick date range setters
    setQuickDateRange(type) {
        const currentYear = new Date().getFullYear() + 543; // Convert to Buddhist year
        
        switch (type) {
            case 'current':
                this.filters.dateRange = { start: currentYear, end: currentYear };
                break;
            case 'recent':
                this.filters.dateRange = { start: currentYear - 2, end: currentYear };
                break;
            case 'all':
                this.filters.dateRange = { start: null, end: null };
                break;
        }
        
        this.updateFilterDisplay();
    }

    // Quick faculty size filter
    setQuickFacultySize(size) {
        // This would need actual faculty data with student counts
        console.log('🏫 Faculty size filter:', size);
        this.filters.quickFilter = `faculty-${size}`;
        this.updateFilterDisplay();
    }

    // Save current filters as preset
    savePreset() {
        const name = prompt('ตั้งชื่อชุดตัวกรอง:', `ตัวกรอง ${new Date().toLocaleDateString('th-TH')}`);
        if (name) {
            const presets = JSON.parse(localStorage.getItem('aims-filter-presets') || '{}');
            presets[name] = { ...this.filters };
            localStorage.setItem('aims-filter-presets', JSON.stringify(presets));
            alert(`✅ บันทึกชุดตัวกรอง "${name}" แล้ว`);
        }
    }

    // Populate multi-select options
    populateMultiSelectOptions(type) {
        const container = document.getElementById(`${type}-options`);
        if (!container) return;

        const data = type === 'faculty' ? this.availableData.faculties : this.availableData.levels;
        const selected = this.filters[type === 'faculty' ? 'faculties' : 'levels'];

        container.innerHTML = data.map(item => {
            const isSelected = selected.includes(item.value || item);
            return `
                <div class="multi-select-option ${isSelected ? 'selected' : ''}" 
                     data-value="${item.value || item}">
                    <input type="checkbox" ${isSelected ? 'checked' : ''}>
                    <span>${item.label || item}</span>
                    ${item.count ? `<small class="ms-auto">${item.count.toLocaleString()} คน</small>` : ''}
                </div>
            `;
        }).join('');

        // Add click handlers
        container.querySelectorAll('.multi-select-option').forEach(option => {
            option.addEventListener('click', () => {
                this.toggleMultiSelectOption(type, option.dataset.value);
            });
        });
    }

    // Toggle multi-select option
    toggleMultiSelectOption(type, value) {
        const field = type === 'faculty' ? 'faculties' : 'levels';
        const index = this.filters[field].indexOf(value);
        
        if (index > -1) {
            this.filters[field].splice(index, 1);
        } else {
            this.filters[field].push(value);
        }
        
        this.populateMultiSelectOptions(type);
        this.updateMultiSelectDisplay(type);
    }

    // Update multi-select trigger display
    updateMultiSelectDisplay(type = null) {
        const types = type ? [type] : ['faculty', 'level'];
        
        types.forEach(t => {
            const trigger = document.getElementById(`${t}-select-trigger`);
            const text = trigger?.querySelector('.selected-text');
            if (!text) return;

            const field = t === 'faculty' ? 'faculties' : 'levels';
            const count = this.filters[field].length;
            
            if (count === 0) {
                text.textContent = `เลือก${t === 'faculty' ? 'คณะ' : 'ระดับการศึกษา'}...`;
            } else if (count === 1) {
                text.textContent = this.filters[field][0];
            } else {
                text.textContent = `เลือกแล้ว ${count} รายการ`;
            }
        });
    }

    // Select all options in multi-select
    selectAllOptions(type) {
        const field = type === 'faculty' ? 'faculties' : 'levels';
        const data = type === 'faculty' ? this.availableData.faculties : this.availableData.levels;
        
        this.filters[field] = data.map(item => item.value || item);
        this.populateMultiSelectOptions(type);
        this.updateMultiSelectDisplay(type);
    }

    // Clear all options in multi-select
    clearAllOptions(type) {
        const field = type === 'faculty' ? 'faculties' : 'levels';
        this.filters[field] = [];
        this.populateMultiSelectOptions(type);
        this.updateMultiSelectDisplay(type);
    }

    // Filter multi-select options by search term
    filterMultiSelectOptions(type, searchTerm) {
        const options = document.querySelectorAll(`#${type}-options .multi-select-option`);
        const term = searchTerm.toLowerCase();
        
        options.forEach(option => {
            const text = option.querySelector('span').textContent.toLowerCase();
            option.style.display = text.includes(term) ? 'flex' : 'none';
        });
    }

    // Update quick filter button states
    updateQuickFilterButtons() {
        document.querySelectorAll('.quick-filter-btn').forEach(btn => {
            btn.classList.remove('active');
        });

        // Highlight active quick filters based on current filters
        // This is a simplified version - you'd want more sophisticated logic
    }
}

// Initialize global filter manager
window.advancedFilterManager = new AdvancedFilterManager();

// Backward compatibility
window.createAdvancedFilters = (containerId, data = {}) => {
    window.advancedFilterManager.setAvailableData(data);
    window.advancedFilterManager.createFilterPanel(containerId);
};

console.log('✅ Advanced Filtering System loaded');