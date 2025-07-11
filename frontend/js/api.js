/**
 * ParkIT Dashboard API Client
 * Handles all communication with the ParkIT backend API
 */

class ParkITAPI {
    constructor() {
        this.baseURL = 'http://localhost:8000';
        this.timeout = 10000; // 10 seconds
        this.isOnline = false;
        this.lastHealthCheck = 0;
        this.healthCheckInterval = 30000; // 30 seconds
        
        // Start periodic health checks
        this.startHealthChecks();
    }

    /**
     * Generic API request handler
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        
        const defaultOptions = {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            timeout: this.timeout
        };

        const config = { ...defaultOptions, ...options };

        try {
            // Create AbortController for timeout
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), config.timeout);

            const response = await fetch(url, {
                ...config,
                signal: controller.signal
            });

            clearTimeout(timeoutId);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            return { success: true, data };

        } catch (error) {
            console.error(`API request failed: ${endpoint}`, error);
            return { 
                success: false, 
                error: error.message || 'Network error'
            };
        }
    }

    /**
     * Health check endpoint
     */
    async healthCheck() {
        try {
            const result = await this.request('/health');
            this.isOnline = result.success;
            this.lastHealthCheck = Date.now();
            
            // Update UI health indicator
            this.updateHealthStatus();
            
            return result;
        } catch (error) {
            this.isOnline = false;
            this.updateHealthStatus();
            return { success: false, error: error.message };
        }
    }

    /**
     * Get all plazas
     */
    async getPlazas() {
        return await this.request('/plazas');
    }

    /**
     * Get specific plaza by ID
     */
    async getPlaza(plazaId) {
        return await this.request(`/plazas/${plazaId}`);
    }

    /**
     * Get plaza availability
     */
    async getPlazaAvailability(plazaId) {
        return await this.request(`/plazas/${plazaId}/availability`);
    }

    /**
     * Create new plaza
     */
    async createPlaza(plazaData) {
        return await this.request('/plazas', {
            method: 'POST',
            body: JSON.stringify(plazaData)
        });
    }

    /**
     * Update plaza
     */
    async updatePlaza(plazaId, plazaData) {
        return await this.request(`/plazas/${plazaId}`, {
            method: 'PUT',
            body: JSON.stringify(plazaData)
        });
    }

    /**
     * Get parking spots for a plaza
     */
    async getPlazaSpots(plazaId) {
        return await this.request(`/plazas/${plazaId}/spots`);
    }

    /**
     * Update spot status
     */
    async updateSpotStatus(spotId, status) {
        return await this.request(`/spots/${spotId}/status`, {
            method: 'PUT',
            body: JSON.stringify({ status })
        });
    }

    /**
     * Get historical occupancy data
     */
    async getOccupancyHistory(plazaId, timeRange = '24h') {
        return await this.request(`/plazas/${plazaId}/occupancy/history?range=${timeRange}`);
    }

    /**
     * Get detection service status
     */
    async getDetectionStatus() {
        return await this.request('/detection/status');
    }

    /**
     * Get analytics data
     */
    async getAnalytics(plazaId, timeRange = '7d') {
        return await this.request(`/plazas/${plazaId}/analytics?range=${timeRange}`);
    }

    /**
     * Start periodic health checks
     */
    startHealthChecks() {
        // Initial health check
        this.healthCheck();
        
        // Set up periodic checks
        setInterval(() => {
            const now = Date.now();
            if (now - this.lastHealthCheck > this.healthCheckInterval) {
                this.healthCheck();
            }
        }, this.healthCheckInterval);
    }

    /**
     * Update health status in UI
     */
    updateHealthStatus() {
        const statusElement = document.getElementById('system-status');
        const statusDot = statusElement?.querySelector('.status-dot');
        const statusText = statusElement?.querySelector('span:last-child');

        if (statusDot && statusText) {
            if (this.isOnline) {
                statusDot.className = 'status-dot online';
                statusText.textContent = 'System Online';
            } else {
                statusDot.className = 'status-dot offline';
                statusText.textContent = 'System Offline';
            }
        }

        // Trigger custom event for other components
        window.dispatchEvent(new CustomEvent('api-health-change', {
            detail: { isOnline: this.isOnline }
        }));
    }

    /**
     * Get connection status
     */
    getStatus() {
        return {
            isOnline: this.isOnline,
            lastHealthCheck: this.lastHealthCheck,
            baseURL: this.baseURL
        };
    }
}

/**
 * Mock data for development/fallback
 */
class MockAPI {
    constructor() {
        this.isOnline = true;
        this.mockData = {
            plazas: [
                {
                    id: 1,
                    name: 'Downtown Plaza',
                    address: '123 Main Street, Downtown',
                    total_spots: 150,
                    available_spots: 23,
                    occupied_spots: 127,
                    occupancy_rate: 84.67
                },
                {
                    id: 2,
                    name: 'Mall Parking',
                    address: '456 Shopping Center Blvd',
                    total_spots: 300,
                    available_spots: 87,
                    occupied_spots: 213,
                    occupancy_rate: 71.00
                },
                {
                    id: 3,
                    name: 'Airport Parking',
                    address: '789 Airport Way',
                    total_spots: 500,
                    available_spots: 234,
                    occupied_spots: 266,
                    occupancy_rate: 53.20
                }
            ],
            occupancyHistory: this.generateMockOccupancyData(),
            recentActivity: this.generateMockActivity(),
            detectionStats: {
                total_detections: 1247,
                detection_fps: 7.2,
                active_cameras: 2,
                vehicles_today: 127,
                avg_duration: 2.3
            }
        };
    }

    async healthCheck() {
        return { success: true, data: { status: 'healthy', timestamp: new Date().toISOString() } };
    }

    async getPlazas() {
        return { success: true, data: { plazas: this.mockData.plazas } };
    }

    async getPlaza(plazaId) {
        const plaza = this.mockData.plazas.find(p => p.id === parseInt(plazaId));
        return { success: true, data: plaza };
    }

    async getPlazaAvailability(plazaId) {
        const plaza = this.mockData.plazas.find(p => p.id === parseInt(plazaId));
        return { 
            success: true, 
            data: {
                plaza_id: plaza.id,
                total_spots: plaza.total_spots,
                available_spots: plaza.available_spots,
                occupied_spots: plaza.occupied_spots,
                occupancy_rate: plaza.occupancy_rate
            }
        };
    }

    async getOccupancyHistory(plazaId, timeRange) {
        return { success: true, data: this.mockData.occupancyHistory };
    }

    async getDetectionStatus() {
        return { success: true, data: this.mockData.detectionStats };
    }

    generateMockOccupancyData() {
        const data = [];
        const now = new Date();
        
        for (let i = 23; i >= 0; i--) {
            const time = new Date(now.getTime() - (i * 60 * 60 * 1000));
            const baseOccupancy = 50 + Math.sin((i / 24) * Math.PI * 2) * 30;
            const occupancy = Math.max(10, Math.min(95, baseOccupancy + (Math.random() - 0.5) * 20));
            
            data.push({
                timestamp: time.toISOString(),
                occupancy_rate: occupancy,
                occupied_spots: Math.round((occupancy / 100) * 150),
                available_spots: Math.round(((100 - occupancy) / 100) * 150)
            });
        }
        
        return data;
    }

    generateMockActivity() {
        const activities = [
            { type: 'vehicle_enter', text: 'Vehicle detected entering spot A-23', time: '2 minutes ago', icon: 'fa-car', color: '#10b981' },
            { type: 'vehicle_exit', text: 'Spot B-15 became available', time: '5 minutes ago', icon: 'fa-check-circle', color: '#2563eb' },
            { type: 'detection', text: 'Camera 1 detected 3 vehicles', time: '7 minutes ago', icon: 'fa-video', color: '#f59e0b' },
            { type: 'vehicle_enter', text: 'Vehicle detected entering spot C-08', time: '12 minutes ago', icon: 'fa-car', color: '#10b981' },
            { type: 'system', text: 'Detection service restarted', time: '1 hour ago', icon: 'fa-robot', color: '#6b7280' }
        ];
        
        return activities;
    }
}

/**
 * API Manager - automatically switches between real and mock API
 */
class APIManager {
    constructor() {
        this.realAPI = new ParkITAPI();
        this.mockAPI = new MockAPI();
        this.useMock = false;
        this.initialized = false;
    }

    async initialize() {
        if (this.initialized) return;

        // Try real API first
        const healthCheck = await this.realAPI.healthCheck();
        
        if (healthCheck.success) {
            this.useMock = false;
            console.log('✅ Connected to real ParkIT backend');
        } else {
            this.useMock = true;
            console.log('⚠️ Backend unavailable, using mock data');
        }

        this.initialized = true;
    }

    getAPI() {
        return this.useMock ? this.mockAPI : this.realAPI;
    }

    async switchToMock() {
        this.useMock = true;
        console.log('🔄 Switched to mock API');
    }

    async switchToReal() {
        const healthCheck = await this.realAPI.healthCheck();
        if (healthCheck.success) {
            this.useMock = false;
            console.log('🔄 Switched to real API');
            return true;
        }
        return false;
    }

    isUsingMock() {
        return this.useMock;
    }
}

// Global API instance
const apiManager = new APIManager();

// Initialize API when DOM is loaded
document.addEventListener('DOMContentLoaded', async () => {
    await apiManager.initialize();
});

// Export for use in other modules
window.ParkITAPI = {
    manager: apiManager,
    get: () => apiManager.getAPI()
}; 