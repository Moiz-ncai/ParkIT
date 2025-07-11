/**
 * ParkIT Dashboard Application
 * Main application entry point and coordinator
 */

class ParkITApp {
    constructor() {
        this.version = '1.0.0';
        this.initialized = false;
        this.modules = {};
        this.config = {
            debug: true,
            autoRefresh: true,
            refreshInterval: 30000, // 30 seconds
            apiTimeout: 10000 // 10 seconds
        };
        
        console.log(`🚀 ParkIT Dashboard v${this.version} starting...`);
    }

    /**
     * Initialize the application
     */
    async init() {
        if (this.initialized) {
            console.warn('Application already initialized');
            return;
        }

        try {
            console.log('⚙️ Initializing ParkIT Dashboard...');
            
            // Show loading screen
            this.showLoadingScreen();
            
            // Wait for DOM to be ready
            if (document.readyState === 'loading') {
                await new Promise(resolve => {
                    document.addEventListener('DOMContentLoaded', resolve);
                });
            }
            
            // Initialize modules in sequence
            await this.initializeModules();
            
            // Setup global event handlers
            this.setupGlobalEventHandlers();
            
            // Start application
            await this.start();
            
            this.initialized = true;
            console.log('✅ ParkIT Dashboard initialized successfully');
            
        } catch (error) {
            console.error('❌ Application initialization failed:', error);
            this.showErrorScreen(error.message);
        }
    }

    /**
     * Initialize all application modules
     */
    async initializeModules() {
        const initSteps = [
            { name: 'API', action: () => this.initAPI() },
            { name: 'Dashboard', action: () => this.initDashboard() },
            { name: 'Charts', action: () => this.initCharts() },
            { name: 'UI Components', action: () => this.initUIComponents() }
        ];

        for (const step of initSteps) {
            try {
                console.log(`🔧 Initializing ${step.name}...`);
                await step.action();
                console.log(`✅ ${step.name} initialized`);
            } catch (error) {
                console.error(`❌ Failed to initialize ${step.name}:`, error);
                throw new Error(`${step.name} initialization failed: ${error.message}`);
            }
        }
    }

    /**
     * Initialize API module
     */
    async initAPI() {
        if (window.ParkITAPI) {
            await window.ParkITAPI.manager.initialize();
            this.modules.api = window.ParkITAPI;
        } else {
            throw new Error('API module not found');
        }
    }

    /**
     * Initialize dashboard module
     */
    async initDashboard() {
        if (window.DashboardManager) {
            // Dashboard manager will initialize itself
            this.modules.dashboard = window.DashboardManager;
        } else {
            throw new Error('Dashboard module not found');
        }
    }

    /**
     * Initialize charts module
     */
    async initCharts() {
        if (window.ChartsManager) {
            // Charts will initialize when API is ready
            this.modules.charts = window.ChartsManager;
        } else {
            console.warn('Charts module not found - charts will not be available');
        }
    }

    /**
     * Initialize UI components
     */
    async initUIComponents() {
        // Setup notification system
        this.setupNotificationSystem();
        
        // Setup modal system
        this.setupModalSystem();
        
        // Setup keyboard shortcuts
        this.setupKeyboardShortcuts();
        
        // Setup theme handling
        this.setupTheme();
    }

    /**
     * Start the application
     */
    async start() {
        // Hide loading screen
        setTimeout(() => {
            this.hideLoadingScreen();
        }, 1000);
        
        // Start any background processes
        this.startBackgroundProcesses();
        
        // Log startup complete
        console.log('🎉 ParkIT Dashboard is ready!');
        
        // Show welcome message in development
        if (this.config.debug) {
            this.showWelcomeMessage();
        }
    }

    /**
     * Setup global event handlers
     */
    setupGlobalEventHandlers() {
        // Handle window resize
        window.addEventListener('resize', this.debounce(() => {
            this.handleWindowResize();
        }, 250));
        
        // Handle online/offline status
        window.addEventListener('online', () => {
            console.log('🌐 Connection restored');
            this.handleConnectionChange(true);
        });
        
        window.addEventListener('offline', () => {
            console.log('📴 Connection lost');
            this.handleConnectionChange(false);
        });
        
        // Handle page visibility changes
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                console.log('👁️ Page hidden - pausing updates');
                this.handlePageHidden();
            } else {
                console.log('👁️ Page visible - resuming updates');
                this.handlePageVisible();
            }
        });
        
        // Handle errors
        window.addEventListener('error', (event) => {
            console.error('💥 Global error:', event.error);
            this.handleGlobalError(event.error);
        });
        
        // Handle unhandled promise rejections
        window.addEventListener('unhandledrejection', (event) => {
            console.error('💥 Unhandled promise rejection:', event.reason);
            this.handleGlobalError(event.reason);
        });
    }

    /**
     * Setup notification system
     */
    setupNotificationSystem() {
        // Create notification container if it doesn't exist
        if (!document.getElementById('notification-container')) {
            const container = document.createElement('div');
            container.id = 'notification-container';
            container.className = 'notification-container';
            document.body.appendChild(container);
        }
        
        // Setup notification panel toggle
        const notificationBtn = document.querySelector('.notification-btn');
        if (notificationBtn) {
            notificationBtn.addEventListener('click', () => {
                this.toggleNotificationPanel();
            });
        }
    }

    /**
     * Setup modal system
     */
    setupModalSystem() {
        // Close modals on outside click
        document.addEventListener('click', (event) => {
            if (event.target.classList.contains('modal-overlay')) {
                this.closeAllModals();
            }
        });
        
        // Close modals on escape key
        document.addEventListener('keydown', (event) => {
            if (event.key === 'Escape') {
                this.closeAllModals();
            }
        });
    }

    /**
     * Setup keyboard shortcuts
     */
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (event) => {
            // Ctrl/Cmd + R: Refresh dashboard
            if ((event.ctrlKey || event.metaKey) && event.key === 'r') {
                event.preventDefault();
                this.refreshDashboard();
            }
            
            // Ctrl/Cmd + D: Toggle debug mode
            if ((event.ctrlKey || event.metaKey) && event.key === 'd') {
                event.preventDefault();
                this.toggleDebugMode();
            }
            
            // F11: Toggle fullscreen
            if (event.key === 'F11') {
                event.preventDefault();
                this.toggleFullscreen();
            }
        });
    }

    /**
     * Setup theme handling
     */
    setupTheme() {
        // Check for saved theme preference or default to light theme
        const savedTheme = localStorage.getItem('parkIT-theme');
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        
        const theme = savedTheme || (prefersDark ? 'dark' : 'light');
        this.setTheme(theme);
        
        // Listen for system theme changes
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
            if (!localStorage.getItem('parkIT-theme')) {
                this.setTheme(e.matches ? 'dark' : 'light');
            }
        });
    }

    /**
     * Start background processes
     */
    startBackgroundProcesses() {
        // Performance monitoring
        this.startPerformanceMonitoring();
        
        // Connection monitoring
        this.startConnectionMonitoring();
    }

    /**
     * Handle window resize
     */
    handleWindowResize() {
        // Trigger chart redraws if needed
        if (this.modules.charts) {
            // Charts.js handles resize automatically with responsive: true
        }
        
        // Handle mobile sidebar
        const sidebar = document.querySelector('.sidebar');
        if (sidebar && window.innerWidth > 768) {
            sidebar.classList.remove('open');
        }
    }

    /**
     * Handle connection changes
     */
    handleConnectionChange(isOnline) {
        if (isOnline) {
            // Try to reconnect to real API
            if (this.modules.api) {
                this.modules.api.manager.switchToReal();
            }
            
            // Refresh dashboard data
            this.refreshDashboard();
            
            // Show success notification
            this.showNotification('Connection restored', 'success');
        } else {
            // Switch to mock data
            if (this.modules.api) {
                this.modules.api.manager.switchToMock();
            }
            
            // Show warning notification
            this.showNotification('Connection lost - using cached data', 'warning');
        }
    }

    /**
     * Handle page hidden
     */
    handlePageHidden() {
        if (this.modules.dashboard) {
            this.modules.dashboard.stopAutoUpdate();
        }
    }

    /**
     * Handle page visible
     */
    handlePageVisible() {
        if (this.modules.dashboard) {
            this.modules.dashboard.startAutoUpdate();
            this.modules.dashboard.refresh();
        }
    }

    /**
     * Handle global errors
     */
    handleGlobalError(error) {
        // Log error
        console.error('Global error handler:', error);
        
        // Show user-friendly error message
        this.showNotification('An error occurred. Please refresh the page.', 'error');
        
        // In production, you might want to send errors to a logging service
        if (!this.config.debug) {
            // Send to error tracking service
        }
    }

    /**
     * Refresh dashboard
     */
    async refreshDashboard() {
        console.log('🔄 Refreshing dashboard...');
        
        if (this.modules.dashboard) {
            await this.modules.dashboard.refresh();
        }
        
        if (this.modules.charts) {
            await this.modules.charts.updateAllCharts();
        }
    }

    /**
     * Show notification
     */
    showNotification(message, type = 'info', duration = 5000) {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-${this.getNotificationIcon(type)}"></i>
                <span>${message}</span>
            </div>
            <button class="notification-close">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        const container = document.getElementById('notification-container');
        if (container) {
            container.appendChild(notification);
            
            // Auto-remove after duration
            setTimeout(() => {
                notification.remove();
            }, duration);
            
            // Manual close
            const closeBtn = notification.querySelector('.notification-close');
            closeBtn.addEventListener('click', () => {
                notification.remove();
            });
        }
    }

    /**
     * Get icon for notification type
     */
    getNotificationIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    }

    /**
     * Utility: Show loading screen
     */
    showLoadingScreen() {
        const loadingScreen = document.getElementById('loading-screen');
        if (loadingScreen) {
            loadingScreen.style.display = 'flex';
        }
    }

    /**
     * Utility: Hide loading screen
     */
    hideLoadingScreen() {
        const loadingScreen = document.getElementById('loading-screen');
        if (loadingScreen) {
            loadingScreen.style.opacity = '0';
            setTimeout(() => {
                loadingScreen.style.display = 'none';
            }, 300);
        }
    }

    /**
     * Show error screen
     */
    showErrorScreen(message) {
        const app = document.getElementById('app');
        if (app) {
            app.innerHTML = `
                <div class="error-screen">
                    <div class="error-content">
                        <i class="fas fa-exclamation-triangle fa-3x"></i>
                        <h2>Application Error</h2>
                        <p>${message}</p>
                        <button onclick="location.reload()" class="btn btn-primary">
                            <i class="fas fa-refresh"></i>
                            Reload Application
                        </button>
                    </div>
                </div>
            `;
        }
    }

    /**
     * Show welcome message
     */
    showWelcomeMessage() {
        console.log(`
🎉 Welcome to ParkIT Dashboard!

🔧 Development Mode Active
📊 Real-time data updates enabled
🎨 Professional UI ready

🎮 Keyboard Shortcuts:
- Ctrl/Cmd + R: Refresh dashboard
- Ctrl/Cmd + D: Toggle debug mode
- F11: Toggle fullscreen

📡 API Status: ${this.modules.api.manager.isUsingMock() ? 'Mock Data' : 'Live Backend'}
        `);
    }

    /**
     * Toggle debug mode
     */
    toggleDebugMode() {
        this.config.debug = !this.config.debug;
        console.log(`🐛 Debug mode ${this.config.debug ? 'enabled' : 'disabled'}`);
    }

    /**
     * Start performance monitoring
     */
    startPerformanceMonitoring() {
        // Monitor memory usage periodically
        setInterval(() => {
            if (performance.memory) {
                const memory = performance.memory;
                const used = Math.round(memory.usedJSHeapSize / 1048576);
                const limit = Math.round(memory.jsHeapSizeLimit / 1048576);
                
                if (this.config.debug) {
                    console.log(`📊 Memory: ${used}MB / ${limit}MB`);
                }
                
                // Warn if memory usage is high
                if (used / limit > 0.8) {
                    console.warn('⚠️ High memory usage detected');
                }
            }
        }, 60000); // Every minute
    }

    /**
     * Start connection monitoring
     */
    startConnectionMonitoring() {
        setInterval(async () => {
            if (this.modules.api) {
                const api = this.modules.api.get();
                if (api.healthCheck) {
                    const result = await api.healthCheck();
                    if (!result.success && !this.modules.api.manager.isUsingMock()) {
                        console.warn('🔴 API health check failed');
                    }
                }
            }
        }, 30000); // Every 30 seconds
    }

    /**
     * Utility: Debounce function
     */
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

    /**
     * Toggle fullscreen
     */
    toggleFullscreen() {
        if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen();
        } else {
            document.exitFullscreen();
        }
    }

    /**
     * Set theme
     */
    setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('parkIT-theme', theme);
    }

    /**
     * Close all modals
     */
    closeAllModals() {
        const modals = document.querySelectorAll('.modal-overlay');
        modals.forEach(modal => {
            modal.classList.remove('active');
        });
    }

    /**
     * Toggle notification panel
     */
    toggleNotificationPanel() {
        const panel = document.querySelector('.notification-panel');
        if (panel) {
            panel.classList.toggle('open');
        }
    }

    /**
     * Get application status
     */
    getStatus() {
        return {
            version: this.version,
            initialized: this.initialized,
            modules: Object.keys(this.modules),
            config: this.config,
            performance: performance.memory ? {
                used: Math.round(performance.memory.usedJSHeapSize / 1048576),
                limit: Math.round(performance.memory.jsHeapSizeLimit / 1048576)
            } : null
        };
    }
}

// Create global app instance
const parkITApp = new ParkITApp();

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        parkITApp.init();
    });
} else {
    parkITApp.init();
}

// Export for global access
window.ParkITApp = parkITApp;

// Add some helpful console methods for development
if (window.console) {
    window.console.parkIT = () => {
        console.log('ParkIT Dashboard Status:', parkITApp.getStatus());
    };
} 