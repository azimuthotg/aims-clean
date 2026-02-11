/* Simple Student Dashboard Charts - Fixed Version */

document.addEventListener('DOMContentLoaded', function() {
    console.log('🎯 Loading Simple Student Dashboard Charts');
    
    // Wait for all dependencies to load
    setTimeout(() => {
        initializeCharts();
    }, 500);
});

function initializeCharts() {
    // Check if all required libraries are loaded
    if (typeof ApexCharts === 'undefined') {
        console.error('❌ ApexCharts not loaded');
        return;
    }
    
    if (typeof window.enhancedLoader === 'undefined') {
        console.warn('⚠️ Enhanced Loader not found, using basic loading');
        window.enhancedLoader = {
            showChartSkeleton: (id) => console.log('Loading chart:', id),
            prepareForChart: (id) => console.log('Preparing chart:', id),
            showSuccess: (id, msg) => console.log('Success:', id, msg),
            showEnhancedError: (id, type, msg) => console.error('Error:', id, type, msg)
        };
    }
    
    if (typeof window.registerChart === 'undefined') {
        window.registerChart = (id, chart) => console.log('Registered chart:', id);
    }
    
    if (typeof window.addChartExportButtons === 'undefined') {
        window.addChartExportButtons = (id, title) => console.log('Export buttons:', id, title);
    }
    
    // Initialize charts
    loadFacultyChart();
    loadGenderChart();
    loadLevelChart();  
    loadYearChart();
    
    // Initialize advanced filters if available
    if (typeof window.createAdvancedFilters === 'function') {
        try {
            const filterData = {
                years: window.availableYears || [],
                faculties: window.allFaculties || [],
                levels: window.allLevels || []
            };
            window.createAdvancedFilters('advanced-filter-container', filterData);
        } catch (error) {
            console.warn('⚠️ Could not initialize advanced filters:', error);
        }
    }
}

function loadFacultyChart() {
    if (typeof window.facultyLabels === 'undefined' || !window.facultyLabels.length) {
        console.warn('⚠️ Faculty data not found');
        return;
    }
    
    console.log('📊 Loading Faculty Chart...');
    window.enhancedLoader.showChartSkeleton('facultyChart', 'bar');
    
    setTimeout(() => {
        renderFacultyChart(window.facultyLabels, window.facultyData);
    }, 800);
}

function renderFacultyChart(labels, data) {
    const dynamicHeight = Math.min(800, Math.max(400, labels.length * 35 + 300));
    
    const options = {
        series: [{
            name: 'จำนวนนักศึกษา',
            data: data
        }],
        chart: {
            type: 'bar',
            height: dynamicHeight,
            toolbar: { show: false }
        },
        plotOptions: {
            bar: {
                borderRadius: 6,
                horizontal: true,
                distributed: true,
                barHeight: '80%'
            }
        },
        dataLabels: {
            enabled: true,
            style: { colors: ['#fff'], fontSize: '12px', fontWeight: 'bold' },
            formatter: function(val) { return val.toLocaleString() + ' คน'; }
        },
        xaxis: {
            categories: labels,
            title: { text: 'จำนวนนักศึกษา (คน)' },
            labels: { formatter: function(val) { return val.toLocaleString(); } }
        },
        yaxis: {
            title: { text: 'คณะ' },
            labels: {
                formatter: function(val) {
                    return val.length > 35 ? val.substring(0, 32) + '...' : val;
                }
            }
        },
        colors: ['#059669'],
        tooltip: { y: { formatter: function(val) { return val.toLocaleString() + ' คน'; } } },
        title: {
            text: 'การกระจายนักศึกษาตามคณะ',
            align: 'center',
            style: { fontSize: '16px', fontWeight: 'bold', color: '#059669' }
        }
    };
    
    window.enhancedLoader.prepareForChart('facultyChart');
    
    const chart = new ApexCharts(document.querySelector("#facultyChart"), options);
    chart.render().then(() => {
        window.enhancedLoader.showSuccess('facultyChart', 'โหลดข้อมูลคณะสำเร็จ');
        window.registerChart('facultyChart', chart);
        window.addChartExportButtons('facultyChart', 'นักศึกษาตามคณะ');
    }).catch((error) => {
        console.error('Faculty Chart Error:', error);
        window.enhancedLoader.showEnhancedError('facultyChart', 'data', 'ไม่สามารถโหลดข้อมูลคณะได้');
    });
}

function loadGenderChart() {
    if (typeof window.genderLabels === 'undefined' || !window.genderLabels.length) {
        console.warn('⚠️ Gender data not found');
        return;
    }
    
    console.log('📊 Loading Gender Chart...');
    window.enhancedLoader.showChartSkeleton('genderChart', 'pie');
    
    setTimeout(() => {
        renderGenderChart(window.genderLabels, window.genderData);
    }, 600);
}

function renderGenderChart(labels, data) {
    const options = {
        series: data,
        chart: {
            type: 'donut',
            height: 250,
            toolbar: { show: false }
        },
        labels: labels,
        plotOptions: {
            pie: {
                donut: {
                    size: '60%',
                    labels: {
                        show: true,
                        total: {
                            show: true,
                            label: 'รวม',
                            formatter: function (w) {
                                const total = w.globals.seriesTotals.reduce((a, b) => a + b, 0);
                                return total.toLocaleString();
                            }
                        }
                    }
                }
            }
        },
        dataLabels: {
            enabled: true,
            formatter: function (val, opts) {
                const value = opts.w.config.series[opts.seriesIndex];
                return value.toLocaleString();
            }
        },
        tooltip: { y: { formatter: function(val) { return val.toLocaleString() + ' คน'; } } },
        legend: { position: 'bottom', fontSize: '12px' },
        colors: ['#2563eb', '#dc2626', '#d97706']
    };
    
    window.enhancedLoader.prepareForChart('genderChart');
    
    const chart = new ApexCharts(document.querySelector("#genderChart"), options);
    chart.render().then(() => {
        window.enhancedLoader.showSuccess('genderChart', 'โหลดข้อมูลเพศสำเร็จ');
        window.registerChart('genderChart', chart);
        window.addChartExportButtons('genderChart', 'สัดส่วนตามเพศ');
    }).catch((error) => {
        console.error('Gender Chart Error:', error);
        window.enhancedLoader.showEnhancedError('genderChart', 'data', 'ไม่สามารถโหลดข้อมูลเพศได้');
    });
}

function loadLevelChart() {
    if (typeof window.levelLabels === 'undefined' || !window.levelLabels.length) {
        console.warn('⚠️ Level data not found');
        return;
    }
    
    console.log('📊 Loading Level Chart...');
    window.enhancedLoader.showChartSkeleton('levelChart', 'pie');
    
    setTimeout(() => {
        renderLevelChart(window.levelLabels, window.levelData);
    }, 400);
}

function renderLevelChart(labels, data) {
    const options = {
        series: data,
        chart: {
            type: 'donut',
            height: 250,
            toolbar: { show: false }
        },
        labels: labels,
        plotOptions: {
            pie: {
                donut: {
                    size: '60%',
                    labels: {
                        show: true,
                        total: {
                            show: true,
                            label: 'รวม',
                            formatter: function (w) {
                                const total = w.globals.seriesTotals.reduce((a, b) => a + b, 0);
                                return total.toLocaleString();
                            }
                        }
                    }
                }
            }
        },
        dataLabels: {
            enabled: true,
            formatter: function (val) {
                return Math.round(val) + '%';
            }
        },
        tooltip: { y: { formatter: function(val) { return val.toLocaleString() + ' คน'; } } },
        legend: { position: 'bottom', fontSize: '12px' },
        colors: ['#dc2626', '#0891b2', '#d97706', '#059669']
    };
    
    window.enhancedLoader.prepareForChart('levelChart');
    
    const chart = new ApexCharts(document.querySelector("#levelChart"), options);
    chart.render().then(() => {
        window.enhancedLoader.showSuccess('levelChart', 'โหลดข้อมูลระดับการศึกษาสำเร็จ');
        window.registerChart('levelChart', chart);
        window.addChartExportButtons('levelChart', 'ระดับการศึกษา');
    }).catch((error) => {
        console.error('Level Chart Error:', error);
        window.enhancedLoader.showEnhancedError('levelChart', 'data', 'ไม่สามารถโหลดข้อมูลระดับการศึกษาได้');
    });
}

function loadYearChart() {
    if (typeof window.yearLabels === 'undefined' || !window.yearLabels.length) {
        console.warn('⚠️ Year data not found');
        return;
    }
    
    console.log('📊 Loading Year Chart...');
    window.enhancedLoader.showChartSkeleton('yearChart', 'line');
    
    setTimeout(() => {
        renderYearChart(window.yearLabels, window.yearData);
    }, 200);
}

function renderYearChart(labels, data) {
    const options = {
        series: [{
            name: 'จำนวนนักศึกษา',
            data: data
        }],
        chart: {
            type: 'line',
            height: 300,
            toolbar: { show: false },
            zoom: { enabled: false }
        },
        stroke: { curve: 'smooth', width: 3 },
        markers: { size: 6, hover: { size: 8 } },
        xaxis: {
            categories: labels,
            title: { text: 'ปีการศึกษา' }
        },
        yaxis: {
            title: { text: 'จำนวนนักศึกษา (คน)' },
            labels: { formatter: function(val) { return val.toLocaleString(); } }
        },
        dataLabels: {
            enabled: true,
            formatter: function(val) { return val.toLocaleString(); },
            style: { fontSize: '11px', fontWeight: 'bold', colors: ['#ffffff'] },
            background: { enabled: true, foreColor: '#2563eb', borderRadius: 4, padding: 4 }
        },
        grid: { show: true, borderColor: '#e0e6ed', strokeDashArray: 5 },
        tooltip: { y: { formatter: function(val) { return val.toLocaleString() + ' คน'; } } },
        title: {
            text: 'แนวโน้มจำนวนนักศึกษาตามปีการศึกษา',
            align: 'center',
            style: { fontSize: '16px', fontWeight: 'bold', color: '#2563eb' }
        },
        colors: ['#2563eb']
    };
    
    window.enhancedLoader.prepareForChart('yearChart');
    
    const chart = new ApexCharts(document.querySelector("#yearChart"), options);
    chart.render().then(() => {
        window.enhancedLoader.showSuccess('yearChart', 'โหลดข้อมูลปีการศึกษาสำเร็จ');
        window.registerChart('yearChart', chart);
        window.addChartExportButtons('yearChart', 'แนวโน้มตามปี');
    }).catch((error) => {
        console.error('Year Chart Error:', error);
        window.enhancedLoader.showEnhancedError('yearChart', 'data', 'ไม่สามารถโหลดข้อมูลปีการศึกษาได้');
    });
}

console.log('✅ Student Dashboard Simple Script loaded');