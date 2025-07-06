// IoT Network Visualizer - Main Application Logic

class IoTNetworkApp {
    constructor() {
        this.visualizer = null;
        this.currentNetwork = null;
        this.currentStats = null;
        
        this.initializeApp();
    }
    
    initializeApp() {
        // Initialize the network visualizer
        this.visualizer = new NetworkVisualizer('networkVisualization');
        
        // Set up event listeners
        this.setupEventListeners();
        
        // Handle window resize
        window.addEventListener('resize', () => {
            this.visualizer.resize();
        });
    }
    
    setupEventListeners() {
        // Make functions available globally
        window.loadSampleNetwork = () => this.loadSampleNetwork();
        window.uploadNetwork = (input) => this.uploadNetwork(input);
        window.showGenerateModal = () => this.showGenerateModal();
        window.generateNetwork = () => this.generateNetwork();
        window.exportNetwork = () => this.exportNetwork();
        window.resetZoom = () => this.visualizer.resetZoom();
        window.toggleLabels = () => this.visualizer.toggleLabels();
        window.updateNodeDetails = (node) => this.updateNodeDetails(node);
    }
    
    async loadSampleNetwork() {
        try {
            this.showLoading();
            
            const response = await fetch('/load_sample');
            const data = await response.json();
            
            if (data.success) {
                await this.loadNetworkData();
                this.showToast('success', data.message);
                this.updateNetworkStats(data.stats);
            } else {
                this.showToast('error', data.error);
            }
        } catch (error) {
            this.showToast('error', 'Failed to load sample network');
            console.error('Error loading sample network:', error);
        } finally {
            this.hideLoading();
        }
    }
    
    async uploadNetwork(input) {
        const file = input.files[0];
        if (!file) return;
        
        const formData = new FormData();
        formData.append('file', file);
        
        try {
            this.showLoading();
            
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (data.success) {
                await this.loadNetworkData();
                this.showToast('success', data.message);
                this.updateNetworkStats(data.stats);
            } else {
                this.showToast('error', data.error);
            }
        } catch (error) {
            this.showToast('error', 'Failed to upload network file');
            console.error('Error uploading network:', error);
        } finally {
            this.hideLoading();
            input.value = ''; // Clear the input
        }
    }
    
    async loadNetworkData() {
        try {
            const response = await fetch('/api/network_data');
            const data = await response.json();
            
            if (response.ok) {
                this.currentNetwork = data;
                this.visualizer.loadNetworkData(data);
                this.clearNodeDetails(); // Clear node details when loading new network
            } else {
                throw new Error(data.error || 'Failed to load network data');
            }
        } catch (error) {
            console.error('Error loading network data:', error);
            throw error;
        }
    }
    
    showGenerateModal() {
        const modal = new bootstrap.Modal(document.getElementById('generateModal'));
        modal.show();
    }
    
    async generateNetwork() {
        const formData = {
            nodes: parseInt(document.getElementById('numNodes').value),
            width: parseInt(document.getElementById('mapWidth').value),
            height: parseInt(document.getElementById('mapHeight').value),
            min_range: parseInt(document.getElementById('minRange').value),
            max_range: parseInt(document.getElementById('maxRange').value)
        };
        
        // Validate inputs
        if (formData.min_range >= formData.max_range) {
            this.showToast('error', 'Minimum range must be less than maximum range');
            return;
        }
        
        try {
            this.showLoading();
            
            const response = await fetch('/api/generate_network', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });
            
            const data = await response.json();
            
            if (data.success) {
                await this.loadNetworkData();
                this.showToast('success', data.message);
                this.updateNetworkStats(data.stats);
                
                // Hide modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('generateModal'));
                modal.hide();
            } else {
                this.showToast('error', data.error);
            }
        } catch (error) {
            this.showToast('error', 'Failed to generate network');
            console.error('Error generating network:', error);
        } finally {
            this.hideLoading();
        }
    }
    
    async exportNetwork() {
        try {
            const response = await fetch('/api/export_network');
            
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'iot_network.json';
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                
                this.showToast('success', 'Network exported successfully');
            } else {
                const data = await response.json();
                this.showToast('error', data.error || 'Failed to export network');
            }
        } catch (error) {
            this.showToast('error', 'Failed to export network');
            console.error('Error exporting network:', error);
        }
    }
    
    updateNetworkStats(stats) {
        this.currentStats = stats;
        
        const statsContainer = document.getElementById('networkStats');
        
        if (!stats) {
            statsContainer.innerHTML = '<div class="text-center text-muted"><i class="fas fa-info-circle"></i> No network loaded</div>';
            return;
        }
        
        statsContainer.innerHTML = `
            <div class="stat-item">
                <span class="stat-label">Total Nodes</span>
                <span class="stat-value">${stats.total_nodes}</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">Total Connections</span>
                <span class="stat-value">${stats.total_connections}</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">Average Connections</span>
                <span class="stat-value">${stats.avg_connections}</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">Network Density</span>
                <span class="stat-value">${stats.network_density}</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">Isolated Nodes</span>
                <span class="stat-value">${stats.isolated_nodes}</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">Max Connections</span>
                <span class="stat-value">${stats.max_connections}</span>
            </div>
        `;
    }
    
    async updateNodeDetails(node) {
        try {
            const response = await fetch(`/api/node_details/${node.id}`);
            const data = await response.json();
            
            if (response.ok) {
                this.displayNodeDetails(data);
            } else {
                console.error('Error fetching node details:', data.error);
            }
        } catch (error) {
            console.error('Error fetching node details:', error);
        }
    }
    
    displayNodeDetails(nodeData) {
        const detailsContainer = document.getElementById('nodeDetails');
        
        let neighborsHtml = '';
        if (nodeData.neighbors && nodeData.neighbors.length > 0) {
            neighborsHtml = `
                <div class="node-detail-item">
                    <div class="node-detail-label">Neighbors (${nodeData.neighbors.length})</div>
                    <div class="neighbor-list">
                        ${nodeData.neighbors.map(neighbor => `
                            <div class="neighbor-item">
                                <strong>${neighbor.eui64}</strong><br>
                                Distance: ${neighbor.distance}, Range: ${neighbor.range}
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        } else {
            neighborsHtml = `
                <div class="node-detail-item">
                    <div class="node-detail-label">Neighbors</div>
                    <div class="node-detail-value text-muted">No connections (isolated node)</div>
                </div>
            `;
        }
        
        detailsContainer.innerHTML = `
            <div class="node-detail-item">
                <div class="node-detail-label">EUI-64 ID</div>
                <div class="node-detail-value"><code>${nodeData.eui64}</code></div>
            </div>
            <div class="node-detail-item">
                <div class="node-detail-label">Position</div>
                <div class="node-detail-value">(${nodeData.position.x.toFixed(1)}, ${nodeData.position.y.toFixed(1)})</div>
            </div>
            <div class="node-detail-item">
                <div class="node-detail-label">Communication Range</div>
                <div class="node-detail-value">${nodeData.range}</div>
            </div>
            <div class="node-detail-item">
                <div class="node-detail-label">Connections</div>
                <div class="node-detail-value">${nodeData.neighbor_count}</div>
            </div>
            ${neighborsHtml}
        `;
    }
    
    clearNodeDetails() {
        const detailsContainer = document.getElementById('nodeDetails');
        detailsContainer.innerHTML = `
            <div class="text-center text-muted">
                <i class="fas fa-mouse-pointer"></i> Click on a node to view details
            </div>
        `;
    }
    
    showToast(type, message) {
        const toast = document.getElementById('toast');
        const toastMessage = document.getElementById('toastMessage');
        
        // Set message
        toastMessage.textContent = message;
        
        // Set icon based on type
        const iconMap = {
            'success': 'fas fa-check-circle text-success',
            'error': 'fas fa-exclamation-circle text-danger',
            'info': 'fas fa-info-circle text-primary',
            'warning': 'fas fa-exclamation-triangle text-warning'
        };
        
        const icon = toast.querySelector('.toast-header i');
        icon.className = iconMap[type] || iconMap['info'];
        
        // Show toast
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
    }
    
    showLoading() {
        const visualization = document.getElementById('networkVisualization');
        
        // Remove existing loading overlay
        const existingOverlay = visualization.querySelector('.loading-overlay');
        if (existingOverlay) {
            existingOverlay.remove();
        }
        
        // Add loading overlay
        const loadingOverlay = document.createElement('div');
        loadingOverlay.className = 'loading-overlay';
        loadingOverlay.innerHTML = '<div class="loading-spinner"></div>';
        visualization.appendChild(loadingOverlay);
    }
    
    hideLoading() {
        const loadingOverlay = document.querySelector('.loading-overlay');
        if (loadingOverlay) {
            loadingOverlay.remove();
        }
    }
}

// Initialize the application when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new IoTNetworkApp();
});