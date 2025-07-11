/**
 * ParkIT Dashboard Main Module
 * Handles dashboard functionality, data updates, and user interactions
 */

class DashboardManager {
    constructor() {
        this.currentPlaza = null;
        this.updateInterval = null;
        this.updateFrequency = 30000; // 30 seconds
        this.isLoading = false;
        this.lastUpdate = null;
        
        // Bind methods
        this.init = this.init.bind(this);
        this.loadDashboardData = this.loadDashboardData.bind(this);
        this.updateMetrics = this.updateMetrics.bind(this);
        this.startAutoUpdate = this.startAutoUpdate.bind(this);
    }

    /**
     * Initialize dashboard
     */
    async init() {
        console.log('🚀 Initializing Dashboard...');
        
        try {
            // Wait for API to be ready
            await this.waitForAPI();
            
            // Load initial data
            await this.loadDashboardData();
            
            // Start auto-update
            this.startAutoUpdate();
            
            // Setup event listeners
            this.setupEventListeners();
            
            console.log('✅ Dashboard initialized successfully');
            
        } catch (error) {
            console.error('❌ Dashboard initialization failed:', error);
            this.showErrorMessage('Failed to initialize dashboard');
        }
    }

    /**
     * Wait for API to be ready
     */
    async waitForAPI() {
        let attempts = 0;
        const maxAttempts = 10;
        
        while (attempts < maxAttempts) {
            if (window.ParkITAPI && window.ParkITAPI.manager.initialized) {
                return true;
            }
            
            await new Promise(resolve => setTimeout(resolve, 500));
            attempts++;
        }
        
        throw new Error('API not available after maximum wait time');
    }

    /**
     * Load all dashboard data
     */
    async loadDashboardData() {
        if (this.isLoading) return;
        
        this.isLoading = true;
        this.showLoadingState();
        
        try {
            const api = window.ParkITAPI.get();
            
            // Load plazas first to get current plaza
            const plazasResult = await api.getPlazas();
            
            if (plazasResult.success && plazasResult.data.plazas.length > 0) {
                // Use first plaza as default
                this.currentPlaza = plazasResult.data.plazas[0];
                
                // Update plaza info in UI
                this.updatePlazaInfo(this.currentPlaza);
                
                // Load plaza-specific data
                await Promise.all([
                    this.updateMetrics(),
                    this.updateRecentActivity(),
                    this.updateSystemHealth()
                ]);
                
                this.lastUpdate = new Date();
                this.updateLastUpdatedTime();
                
            } else {
                throw new Error('No plazas available');
            }
            
        } catch (error) {
            console.error('Failed to load dashboard data:', error);
            this.showErrorMessage('Failed to load dashboard data');
        } finally {
            this.isLoading = false;
            this.hideLoadingState();
        }
    }

    /**
     * Update key metrics
     */
    async updateMetrics() {
        if (!this.currentPlaza) return;
        
        try {
            const api = window.ParkITAPI.get();
            const result = await api.getPlazaAvailability(this.currentPlaza.id);
            
            if (result.success) {
                const data = result.data;
                
                // Update metric cards
                this.updateElement('total-spots', data.total_spots);
                this.updateElement('occupied-spots', data.occupied_spots);
                this.updateElement('available-spots', data.available_spots);
                this.updateElement('occupancy-rate', `${data.occupancy_rate.toFixed(1)}%`);
                
                // Update changes (simulate with random values for demo)
                this.updateMetricChange('occupied-change', this.generateRandomChange());
                this.updateMetricChange('available-change', this.generateRandomChange());
                this.updateMetricChange('occupancy-change', this.generateRandomChange());
                
                // Update plaza info
                this.currentPlaza = { ...this.currentPlaza, ...data };
                
            } else {
                throw new Error(result.error || 'Failed to get plaza availability');
            }
            
        } catch (error) {
            console.error('Failed to update metrics:', error);
        }
    }

    /**
     * Update plaza information
     */
    updatePlazaInfo(plaza) {
        this.updateElement('plaza-name', plaza.name);
        this.updateElement('plaza-address', plaza.address);
        this.updateElement('current-username', 'Plaza Owner');
        this.updateElement('current-role', plaza.name);
    }

    /**
     * Update recent activity
     */
    async updateRecentActivity() {
        try {
            const api = window.ParkITAPI.get();
            
            // For now, use mock data as the backend doesn't have activity endpoint
            let activities;
            if (api.generateMockActivity) {
                activities = api.generateMockActivity();
            } else {
                activities = this.generateMockActivity();
            }
            
            const activityContainer = document.getElementById('recent-activity');
            if (activityContainer) {
                activityContainer.innerHTML = activities.map(activity => `
                    <div class="activity-item">
                        <div class="activity-icon" style="background-color: ${activity.color}">
                            <i class="fas ${activity.icon}"></i>
                        </div>
                        <div class="activity-content">
                            <div class="activity-text">${activity.text}</div>
                            <div class="activity-time">${activity.time}</div>
                        </div>
                    </div>
                `).join('');
            }
            
        } catch (error) {
            console.error('Failed to update recent activity:', error);
        }
    }

    /**
     * Update system health
     */
    async updateSystemHealth() {
        try {
            const api = window.ParkITAPI.get();
            const apiStatus = api.getStatus ? api.getStatus() : { isOnline: true };
            
            // Update detection stats if available
            if (api.getDetectionStatus) {
                const detectionResult = await api.getDetectionStatus();
                if (detectionResult.success) {
                    const stats = detectionResult.data;
                    this.updateElement('vehicles-today', stats.vehicles_today || 127);
                    this.updateElement('avg-duration', `${stats.avg_duration || 2.3} hrs`);
                    this.updateElement('active-cameras', `${stats.active_cameras || 2} Active`);
                }
            }
            
            // Update health indicators based on API status
            this.updateHealthIndicators(apiStatus.isOnline);
            
        } catch (error) {
            console.error('Failed to update system health:', error);
        }
    }

    /**
     * Update health indicators
     */
    updateHealthIndicators(isOnline) {
        const healthItems = document.querySelectorAll('.health-status');
        
        healthItems.forEach(item => {
            if (isOnline) {
                item.className = 'health-status online';
                item.textContent = item.textContent.includes('2/2') ? '2/2 Active' : 'Online';
            } else {
                item.className = 'health-status offline';
                item.textContent = 'Offline';
            }
        });
        
        // Update overall health indicator
        const healthIndicator = document.querySelector('.health-indicator');
        if (healthIndicator) {
            if (isOnline) {
                healthIndicator.className = 'health-indicator excellent';
                healthIndicator.textContent = 'Excellent';
            } else {
                healthIndicator.className = 'health-indicator poor';
                healthIndicator.textContent = 'Poor';
            }
        }
    }

    /**
     * Start auto-update timer
     */
    startAutoUpdate() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }
        
        this.updateInterval = setInterval(async () => {
            if (!this.isLoading) {
                await this.updateMetrics();
                await this.updateSystemHealth();
                this.lastUpdate = new Date();
                this.updateLastUpdatedTime();
            }
        }, this.updateFrequency);
        
        console.log(`🔄 Auto-update started (every ${this.updateFrequency / 1000}s)`);
    }

    /**
     * Stop auto-update timer
     */
    stopAutoUpdate() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
            console.log('⏹️ Auto-update stopped');
        }
    }

    /**
     * Manual refresh
     */
    async refresh() {
        console.log('🔄 Manual refresh triggered');
        
        // Add visual feedback
        const refreshBtn = document.getElementById('refresh-btn');
        if (refreshBtn) {
            const icon = refreshBtn.querySelector('i');
            icon.classList.add('fa-spin');
            
            setTimeout(() => {
                icon.classList.remove('fa-spin');
            }, 1000);
        }
        
        await this.loadDashboardData();
        
        // Update charts
        if (window.ChartsManager) {
            window.ChartsManager.updateAllCharts();
        }
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Refresh button
        const refreshBtn = document.getElementById('refresh-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.refresh());
        }
        
        // Sidebar toggle (mobile)
        const sidebarToggle = document.getElementById('sidebar-toggle');
        const sidebar = document.querySelector('.sidebar');
        
        if (sidebarToggle && sidebar) {
            sidebarToggle.addEventListener('click', () => {
                sidebar.classList.toggle('open');
            });
        }
        
        // Navigation items
        const navItems = document.querySelectorAll('.nav-item');
        navItems.forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                this.switchPage(item.dataset.page);
            });
        });
        
        // API health change listener
        window.addEventListener('api-health-change', (event) => {
            this.updateHealthIndicators(event.detail.isOnline);
        });
        
        // Page visibility change
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.stopAutoUpdate();
            } else {
                this.startAutoUpdate();
                this.refresh();
            }
        });
    }

    /**
     * Switch between dashboard pages
     */
    switchPage(pageId) {
        // Update navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        
        document.querySelector(`[data-page="${pageId}"]`).classList.add('active');
        
        // Update page content
        document.querySelectorAll('.page-content').forEach(page => {
            page.classList.remove('active');
        });
        
        const targetPage = document.getElementById(`${pageId}-page`);
        if (targetPage) {
            targetPage.classList.add('active');
        }
        
        // Update page title
        const titles = {
            'dashboard': 'Dashboard Overview',
            'parking-spots': 'Parking Spots',
            'analytics': 'Analytics',
            'detection': 'Detection System',
            'settings': 'Settings'
        };
        
        this.updateElement('page-title', titles[pageId] || 'Dashboard');
    }

    /**
     * Utility: Update element text content
     */
    updateElement(id, value) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        }
    }

    /**
     * Update metric change indicators
     */
    updateMetricChange(id, change) {
        const element = document.getElementById(id);
        if (element) {
            const isPositive = change.startsWith('+');
            element.textContent = change;
            element.className = `metric-change ${isPositive ? 'positive' : 'negative'}`;
        }
    }

    /**
     * Update last updated time
     */
    updateLastUpdatedTime() {
        const element = document.getElementById('last-updated');
        if (element && this.lastUpdate) {
            const timeStr = this.lastUpdate.toLocaleTimeString('en-US', {
                hour12: false,
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
            });
            element.textContent = `Last updated: ${timeStr}`;
        }
    }

    /**
     * Show loading state
     */
    showLoadingState() {
        const loadingScreen = document.getElementById('loading-screen');
        if (loadingScreen) {
            loadingScreen.style.opacity = '1';
            loadingScreen.style.visibility = 'visible';
        }
    }

    /**
     * Hide loading state
     */
    hideLoadingState() {
        const loadingScreen = document.getElementById('loading-screen');
        if (loadingScreen) {
            loadingScreen.style.opacity = '0';
            setTimeout(() => {
                loadingScreen.style.visibility = 'hidden';
            }, 300);
        }
    }

    /**
     * Show error message
     */
    showErrorMessage(message) {
        console.error('Dashboard Error:', message);
        
        // You could implement a toast notification system here
        // For now, just log to console
    }

    /**
     * Generate random change for demo
     */
    generateRandomChange() {
        const change = (Math.random() - 0.5) * 10;
        const sign = change >= 0 ? '+' : '';
        return `${sign}${change.toFixed(1)}%`;
    }

    /**
     * Generate mock activity data
     */
    generateMockActivity() {
        const now = new Date();
        const activities = [
            {
                type: 'vehicle_enter',
                text: 'Vehicle detected entering spot A-23',
                time: this.getRelativeTime(now, 2),
                icon: 'fa-car',
                color: '#10b981'
            },
            {
                type: 'vehicle_exit',
                text: 'Spot B-15 became available',
                time: this.getRelativeTime(now, 5),
                icon: 'fa-check-circle',
                color: '#2563eb'
            },
            {
                type: 'detection',
                text: 'Camera 1 detected 3 vehicles',
                time: this.getRelativeTime(now, 7),
                icon: 'fa-video',
                color: '#f59e0b'
            },
            {
                type: 'vehicle_enter',
                text: 'Vehicle detected entering spot C-08',
                time: this.getRelativeTime(now, 12),
                icon: 'fa-car',
                color: '#10b981'
            },
            {
                type: 'system',
                text: 'Detection service restarted',
                time: this.getRelativeTime(now, 60),
                icon: 'fa-robot',
                color: '#6b7280'
            }
        ];
        
        return activities;
    }

    /**
     * Get relative time string
     */
    getRelativeTime(now, minutesAgo) {
        if (minutesAgo < 60) {
            return `${minutesAgo} minutes ago`;
        } else {
            const hours = Math.floor(minutesAgo / 60);
            return `${hours} hour${hours > 1 ? 's' : ''} ago`;
        }
    }

    /**
     * Cleanup method
     */
    destroy() {
        this.stopAutoUpdate();
        console.log('🧹 Dashboard cleanup completed');
    }
}

// Global dashboard manager instance
const dashboardManager = new DashboardManager();

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    dashboardManager.init();
});

// Export for global use
window.DashboardManager = dashboardManager; 