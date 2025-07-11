/**
 * ParkIT Dashboard Charts Module
 * Handles all chart creation and data visualization
 */

class ChartsManager {
    constructor() {
        this.charts = {};
        this.defaultOptions = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        usePointStyle: true,
                        padding: 20,
                        font: {
                            size: 12,
                            family: 'Inter'
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#ffffff',
                    bodyColor: '#ffffff',
                    borderColor: 'rgba(59, 130, 246, 0.5)',
                    borderWidth: 1,
                    cornerRadius: 8,
                    displayColors: true,
                    titleFont: {
                        size: 13,
                        weight: 'bold'
                    },
                    bodyFont: {
                        size: 12
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        font: {
                            size: 11,
                            family: 'Inter'
                        },
                        color: '#6b7280'
                    }
                },
                y: {
                    grid: {
                        color: 'rgba(229, 231, 235, 0.5)',
                        borderDash: [2, 2]
                    },
                    ticks: {
                        font: {
                            size: 11,
                            family: 'Inter'
                        },
                        color: '#6b7280'
                    }
                }
            }
        };
    }

    /**
     * Initialize all charts
     */
    async initialize() {
        try {
            await this.createOccupancyChart();
            console.log('✅ Charts initialized successfully');
        } catch (error) {
            console.error('❌ Failed to initialize charts:', error);
        }
    }

    /**
     * Create real-time occupancy chart
     */
    async createOccupancyChart() {
        const canvas = document.getElementById('occupancy-chart');
        if (!canvas) {
            console.warn('Occupancy chart canvas not found');
            return;
        }

        // Show loading state
        this.showChartLoading(canvas);

        try {
            // Get occupancy data
            const api = window.ParkITAPI.get();
            const result = await api.getOccupancyHistory(1, '24h');
            
            if (!result.success) {
                throw new Error(result.error || 'Failed to load occupancy data');
            }

            const data = result.data;

            // Prepare chart data
            const labels = data.map(item => {
                const date = new Date(item.timestamp);
                return date.getHours() + ':00';
            });

            const occupancyData = data.map(item => item.occupancy_rate);
            const occupiedSpots = data.map(item => item.occupied_spots);
            const availableSpots = data.map(item => item.available_spots);

            // Create gradient
            const ctx = canvas.getContext('2d');
            const gradient = ctx.createLinearGradient(0, 0, 0, 300);
            gradient.addColorStop(0, 'rgba(59, 130, 246, 0.3)');
            gradient.addColorStop(1, 'rgba(59, 130, 246, 0.05)');

            // Destroy existing chart if it exists
            if (this.charts.occupancy) {
                this.charts.occupancy.destroy();
            }

            this.charts.occupancy = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [
                        {
                            label: 'Occupancy Rate (%)',
                            data: occupancyData,
                            borderColor: '#3b82f6',
                            backgroundColor: gradient,
                            borderWidth: 3,
                            fill: true,
                            tension: 0.4,
                            pointBackgroundColor: '#3b82f6',
                            pointBorderColor: '#ffffff',
                            pointBorderWidth: 2,
                            pointRadius: 4,
                            pointHoverRadius: 6
                        }
                    ]
                },
                options: {
                    ...this.defaultOptions,
                    plugins: {
                        ...this.defaultOptions.plugins,
                        title: {
                            display: false
                        },
                        tooltip: {
                            ...this.defaultOptions.plugins.tooltip,
                            callbacks: {
                                title: function(context) {
                                    return `Time: ${context[0].label}`;
                                },
                                label: function(context) {
                                    const dataIndex = context.dataIndex;
                                    const occupancy = occupancyData[dataIndex].toFixed(1);
                                    const occupied = occupiedSpots[dataIndex];
                                    const available = availableSpots[dataIndex];
                                    
                                    return [
                                        `Occupancy: ${occupancy}%`,
                                        `Occupied: ${occupied} spots`,
                                        `Available: ${available} spots`
                                    ];
                                }
                            }
                        }
                    },
                    scales: {
                        ...this.defaultOptions.scales,
                        y: {
                            ...this.defaultOptions.scales.y,
                            beginAtZero: true,
                            max: 100,
                            ticks: {
                                ...this.defaultOptions.scales.y.ticks,
                                callback: function(value) {
                                    return value + '%';
                                }
                            }
                        }
                    },
                    animation: {
                        duration: 1000,
                        easing: 'easeInOutQuart'
                    }
                }
            });

            this.hideChartLoading(canvas);

        } catch (error) {
            console.error('Failed to create occupancy chart:', error);
            this.showChartError(canvas, 'Failed to load occupancy data');
        }
    }

    /**
     * Create parking spots status chart (pie chart)
     */
    async createSpotsStatusChart(containerId = 'spots-status-chart') {
        const canvas = document.getElementById(containerId);
        if (!canvas) return;

        try {
            const api = window.ParkITAPI.get();
            const result = await api.getPlazaAvailability(1);
            
            if (!result.success) {
                throw new Error(result.error);
            }

            const data = result.data;
            const ctx = canvas.getContext('2d');

            // Destroy existing chart
            if (this.charts.spotsStatus) {
                this.charts.spotsStatus.destroy();
            }

            this.charts.spotsStatus = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: ['Occupied', 'Available'],
                    datasets: [{
                        data: [data.occupied_spots, data.available_spots],
                        backgroundColor: [
                            '#ef4444',
                            '#10b981'
                        ],
                        borderWidth: 0,
                        hoverOffset: 10
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                padding: 20,
                                usePointStyle: true,
                                font: {
                                    size: 12,
                                    family: 'Inter'
                                }
                            }
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    const label = context.label;
                                    const value = context.parsed;
                                    const total = data.total_spots;
                                    const percentage = ((value / total) * 100).toFixed(1);
                                    return `${label}: ${value} spots (${percentage}%)`;
                                }
                            }
                        }
                    },
                    cutout: '60%'
                }
            });

        } catch (error) {
            console.error('Failed to create spots status chart:', error);
        }
    }

    /**
     * Create hourly usage chart
     */
    async createHourlyUsageChart(containerId = 'hourly-usage-chart') {
        const canvas = document.getElementById(containerId);
        if (!canvas) return;

        // Generate mock hourly data
        const hourlyData = this.generateHourlyData();
        const ctx = canvas.getContext('2d');

        // Destroy existing chart
        if (this.charts.hourlyUsage) {
            this.charts.hourlyUsage.destroy();
        }

        this.charts.hourlyUsage = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: hourlyData.labels,
                datasets: [{
                    label: 'Average Occupancy',
                    data: hourlyData.data,
                    backgroundColor: 'rgba(59, 130, 246, 0.6)',
                    borderColor: '#3b82f6',
                    borderWidth: 1,
                    borderRadius: 4,
                    borderSkipped: false
                }]
            },
            options: {
                ...this.defaultOptions,
                plugins: {
                    ...this.defaultOptions.plugins,
                    legend: {
                        display: false
                    }
                },
                scales: {
                    ...this.defaultOptions.scales,
                    y: {
                        ...this.defaultOptions.scales.y,
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            ...this.defaultOptions.scales.y.ticks,
                            callback: function(value) {
                                return value + '%';
                            }
                        }
                    }
                }
            }
        });
    }

    /**
     * Update chart data
     */
    async updateChart(chartName) {
        switch (chartName) {
            case 'occupancy':
                await this.createOccupancyChart();
                break;
            case 'spotsStatus':
                await this.createSpotsStatusChart();
                break;
            case 'hourlyUsage':
                await this.createHourlyUsageChart();
                break;
        }
    }

    /**
     * Update all charts
     */
    async updateAllCharts() {
        const updatePromises = Object.keys(this.charts).map(chartName => 
            this.updateChart(chartName)
        );
        
        await Promise.all(updatePromises);
        console.log('📊 All charts updated');
    }

    /**
     * Show loading state for chart
     */
    showChartLoading(canvas) {
        const container = canvas.parentElement;
        let loadingElement = container.querySelector('.chart-loading');
        
        if (!loadingElement) {
            loadingElement = document.createElement('div');
            loadingElement.className = 'chart-loading';
            loadingElement.innerHTML = `
                <i class="fas fa-spinner-third"></i>
                <p>Loading chart data...</p>
            `;
            container.appendChild(loadingElement);
        }
        
        canvas.style.opacity = '0.3';
        loadingElement.style.display = 'block';
    }

    /**
     * Hide loading state for chart
     */
    hideChartLoading(canvas) {
        const container = canvas.parentElement;
        const loadingElement = container.querySelector('.chart-loading');
        
        if (loadingElement) {
            loadingElement.style.display = 'none';
        }
        
        canvas.style.opacity = '1';
    }

    /**
     * Show error state for chart
     */
    showChartError(canvas, message) {
        const container = canvas.parentElement;
        let errorElement = container.querySelector('.chart-error');
        
        if (!errorElement) {
            errorElement = document.createElement('div');
            errorElement.className = 'chart-error error-message';
            container.appendChild(errorElement);
        }
        
        errorElement.innerHTML = `
            <i class="fas fa-exclamation-triangle"></i>
            <span>${message}</span>
        `;
        
        canvas.style.opacity = '0.3';
        errorElement.style.display = 'flex';
    }

    /**
     * Generate mock hourly data
     */
    generateHourlyData() {
        const hours = [];
        const data = [];
        
        for (let i = 0; i < 24; i++) {
            hours.push(`${i.toString().padStart(2, '0')}:00`);
            
            // Simulate realistic parking patterns
            let occupancy;
            if (i >= 6 && i <= 9) {
                // Morning rush
                occupancy = 70 + Math.random() * 20;
            } else if (i >= 17 && i <= 20) {
                // Evening rush
                occupancy = 80 + Math.random() * 15;
            } else if (i >= 11 && i <= 14) {
                // Lunch time
                occupancy = 60 + Math.random() * 25;
            } else if (i >= 22 || i <= 5) {
                // Night time
                occupancy = 20 + Math.random() * 30;
            } else {
                // Regular hours
                occupancy = 45 + Math.random() * 30;
            }
            
            data.push(Math.min(95, Math.max(10, occupancy)));
        }
        
        return { labels: hours, data };
    }

    /**
     * Destroy all charts
     */
    destroyAllCharts() {
        Object.values(this.charts).forEach(chart => {
            if (chart && typeof chart.destroy === 'function') {
                chart.destroy();
            }
        });
        this.charts = {};
    }

    /**
     * Get chart instance
     */
    getChart(name) {
        return this.charts[name];
    }

    /**
     * Check if chart exists
     */
    hasChart(name) {
        return !!this.charts[name];
    }
}

// Global charts manager instance
const chartsManager = new ChartsManager();

// Initialize charts when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Wait for API to be ready
    setTimeout(() => {
        chartsManager.initialize();
    }, 1000);
});

// Export for global use
window.ChartsManager = chartsManager;

// Update charts when time range changes
document.addEventListener('change', (event) => {
    if (event.target.id === 'time-range') {
        chartsManager.updateChart('occupancy');
    }
});

// Listen for API health changes
window.addEventListener('api-health-change', (event) => {
    if (event.detail.isOnline) {
        // Refresh charts when API comes back online
        setTimeout(() => {
            chartsManager.updateAllCharts();
        }, 1000);
    }
}); 