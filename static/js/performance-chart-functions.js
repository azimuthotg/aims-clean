    // Performance-optimized chart loading functions for student dashboard
    
    function loadLevelChart(labels, data) {
        return new Promise((resolve, reject) => {
            window.enhancedLoader.showChartSkeleton('levelChart', 'pie');
            
            const cacheKey = 'level-chart-' + JSON.stringify({labels, data});
            const cached = window.getCachedData(cacheKey);
            
            if (cached) {
                console.log('📊 Using cached level chart data');
                setTimeout(() => {
                    renderLevelChart(labels, data);
                    resolve();
                }, 50);
            } else {
                setTimeout(() => {
                    try {
                        renderLevelChart(labels, data);
                        window.cacheData(cacheKey, {rendered: true}, 300000);
                        resolve();
                    } catch (error) {
                        reject(error);
                    }
                }, 600);
            }
        });
    }
    
    function renderLevelChart(labels, data) {
        const levelOptions = {
            series: data,
            chart: {
                type: 'donut',
                height: 250,
                toolbar: {
                    show: false
                }
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
            tooltip: {
                y: {
                    formatter: function(val) {
                        return val.toLocaleString() + ' คน';
                    }
                }
            },
            legend: {
                position: 'bottom',
                fontSize: '12px'
            },
            colors: ['#2563eb', '#059669', '#d97706', '#dc2626', '#8b5cf6']
        };
        
        window.enhancedLoader.prepareForChart('levelChart');
        
        const levelChart = new ApexCharts(document.querySelector("#levelChart"), levelOptions);
        levelChart.render().then(() => {
            window.enhancedLoader.showSuccess('levelChart', 'โหลดข้อมูลระดับการศึกษาสำเร็จ');
            window.registerChart('levelChart', levelChart);
            window.addChartExportButtons('levelChart', 'ระดับการศึกษา');
        }).catch((error) => {
            console.error('Level Chart Error:', error);
            window.enhancedLoader.showEnhancedError('levelChart', 'data', 'ไม่สามารถโหลดข้อมูลระดับการศึกษาได้');
        });
    }
    
    function loadYearChart(labels, data) {
        return new Promise((resolve, reject) => {
            window.enhancedLoader.showChartSkeleton('yearChart', 'line');
            
            const cacheKey = 'year-chart-' + JSON.stringify({labels, data});
            const cached = window.getCachedData(cacheKey);
            
            if (cached) {
                console.log('📊 Using cached year chart data');
                setTimeout(() => {
                    renderYearChart(labels, data);
                    resolve();
                }, 50);
            } else {
                setTimeout(() => {
                    try {
                        renderYearChart(labels, data);
                        window.cacheData(cacheKey, {rendered: true}, 300000);
                        resolve();
                    } catch (error) {
                        reject(error);
                    }
                }, 400);
            }
        });
    }
    
    function renderYearChart(labels, data) {
        const yearOptions = {
            series: [{
                name: 'จำนวนนักศึกษา',
                data: data
            }],
            chart: {
                type: 'line',
                height: 300,
                toolbar: {
                    show: false
                },
                zoom: {
                    enabled: false
                }
            },
            stroke: {
                curve: 'smooth',
                width: 3
            },
            markers: {
                size: 6,
                hover: {
                    size: 8
                }
            },
            xaxis: {
                categories: labels,
                title: {
                    text: 'ปีการศึกษา',
                    style: {
                        fontSize: '14px',
                        fontWeight: '600'
                    }
                }
            },
            yaxis: {
                title: {
                    text: 'จำนวนนักศึกษา (คน)',
                    style: {
                        fontSize: '14px',
                        fontWeight: '600'
                    }
                },
                labels: {
                    formatter: function(val) {
                        return val.toLocaleString();
                    }
                }
            },
            dataLabels: {
                enabled: true,
                formatter: function(val) {
                    return val.toLocaleString();
                },
                style: {
                    fontSize: '11px',
                    fontWeight: 'bold',
                    colors: ['#ffffff']
                },
                background: {
                    enabled: true,
                    foreColor: '#2563eb',
                    borderRadius: 4,
                    padding: 4
                }
            },
            grid: {
                show: true,
                borderColor: '#e0e6ed',
                strokeDashArray: 5
            },
            tooltip: {
                y: {
                    formatter: function(val) {
                        return val.toLocaleString() + ' คน';
                    }
                }
            },
            title: {
                text: 'แนวโน้มจำนวนนักศึกษาตามปีการศึกษา',
                align: 'center',
                style: {
                    fontSize: '16px',
                    fontWeight: 'bold',
                    color: '#2563eb'
                }
            },
            colors: ['#2563eb']
        };
        
        window.enhancedLoader.prepareForChart('yearChart');
        
        const yearChart = new ApexCharts(document.querySelector("#yearChart"), yearOptions);
        yearChart.render().then(() => {
            window.enhancedLoader.showSuccess('yearChart', 'โหลดข้อมูลปีการศึกษาสำเร็จ');
            window.registerChart('yearChart', yearChart);
            window.addChartExportButtons('yearChart', 'แนวโน้มตามปี');
        }).catch((error) => {
            console.error('Year Chart Error:', error);
            window.enhancedLoader.showEnhancedError('yearChart', 'data', 'ไม่สามารถโหลดข้อมูลปีการศึกษาได้');
        });
    }