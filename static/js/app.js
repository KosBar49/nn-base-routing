// IoT Network Visualizer - Main Application Logic

class IoTNetworkApp {
    constructor() {
        this.visualizer = null;
        this.currentNetwork = null;
        this.currentStats = null;
        this.currentPath = null;
        
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
        window.findPath = () => this.findPath();
        window.clearPath = () => this.clearPath();
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
                this.populateNodeSelectors(); // Populate path finder dropdowns
                this.clearPath(); // Clear any existing path
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
            max_range: parseInt(document.getElementById('maxRange').value)
        };
        
        // Validate inputs
        if (formData.max_range <= 0) {
            this.showToast('error', 'Maximum range must be greater than 0');
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
    
    populateNodeSelectors() {
        const sourceInput = document.getElementById('sourceNode');
        const destinationInput = document.getElementById('destinationNode');
        const sourceDatalist = document.getElementById('sourceNodeOptions');
        const destinationDatalist = document.getElementById('destinationNodeOptions');
        
        // Clear existing options
        sourceDatalist.innerHTML = '';
        destinationDatalist.innerHTML = '';
        
        if (!this.currentNetwork || !this.currentNetwork.nodes) {
            sourceInput.disabled = true;
            destinationInput.disabled = true;
            document.getElementById('findPathBtn').disabled = true;
            return;
        }
        
        // Populate datalists with node data
        this.currentNetwork.nodes.forEach(node => {
            const optionText = `${node.eui64} (${node.neighbors} connections)`;
            
            const sourceOption = document.createElement('option');
            sourceOption.value = node.eui64;
            sourceOption.textContent = optionText;
            sourceDatalist.appendChild(sourceOption);
            
            const destOption = document.createElement('option');
            destOption.value = node.eui64;
            destOption.textContent = optionText;
            destinationDatalist.appendChild(destOption);
        });
        
        // Enable inputs
        sourceInput.disabled = false;
        destinationInput.disabled = false;
        
        // Add input listeners to enable/disable find button and validate nodes
        const updateFindButton = () => {
            const sourceValue = this.getValidNodeId(sourceInput.value);
            const destValue = this.getValidNodeId(destinationInput.value);
            
            // Update input styling based on validity
            this.updateInputValidation(sourceInput, sourceValue);
            this.updateInputValidation(destinationInput, destValue);
            
            document.getElementById('findPathBtn').disabled = !sourceValue || !destValue || sourceValue === destValue;
        };
        
        // Remove any existing listeners to prevent duplicates
        sourceInput.removeEventListener('input', updateFindButton);
        destinationInput.removeEventListener('input', updateFindButton);
        
        sourceInput.addEventListener('input', updateFindButton);
        destinationInput.addEventListener('input', updateFindButton);
    }
    
    getValidNodeId(inputValue) {
        if (!inputValue || !this.currentNetwork || !this.currentNetwork.nodes) {
            return null;
        }
        
        // Check if input value exactly matches a node ID
        const exactMatch = this.currentNetwork.nodes.find(node => node.eui64 === inputValue);
        if (exactMatch) {
            return inputValue;
        }
        
        // Check if input value is a partial match or contains the node ID
        const partialMatch = this.currentNetwork.nodes.find(node => 
            inputValue.includes(node.eui64) || node.eui64.includes(inputValue)
        );
        
        if (partialMatch && inputValue.length >= 8) { // Require at least 8 characters for partial match
            return partialMatch.eui64;
        }
        
        return null;
    }
    
    updateInputValidation(input, isValid) {
        if (!input.value) {
            // No input - neutral state
            input.classList.remove('is-valid', 'is-invalid');
        } else if (isValid) {
            // Valid input
            input.classList.remove('is-invalid');
            input.classList.add('is-valid');
        } else {
            // Invalid input
            input.classList.remove('is-valid');
            input.classList.add('is-invalid');
        }
    }
    
    async findPath() {
        const sourceInput = document.getElementById('sourceNode').value;
        const destinationInput = document.getElementById('destinationNode').value;
        
        // Validate and get actual node IDs
        const sourceId = this.getValidNodeId(sourceInput);
        const destinationId = this.getValidNodeId(destinationInput);
        
        if (!sourceId || !destinationId) {
            this.showToast('error', 'Please enter valid source and destination nodes');
            return;
        }
        
        if (sourceId === destinationId) {
            this.showToast('error', 'Source and destination must be different nodes');
            return;
        }
        
        try {
            this.showLoading();
            
            const response = await fetch('/api/find_path', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    source: sourceId,
                    destination: destinationId
                })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                this.currentPath = data;
                this.displayPathResult(data);
                
                if (data.reachable && this.visualizer.highlightPath) {
                    this.visualizer.highlightPath(data.path_indices);
                }
                
                this.showToast('success', data.reachable ? 
                    `Path found: ${data.hop_count} hops, distance ${data.distance}` : 
                    'No path found between selected nodes');
            } else {
                this.showToast('error', data.error);
            }
        } catch (error) {
            this.showToast('error', 'Failed to find path');
            console.error('Error finding path:', error);
        } finally {
            this.hideLoading();
        }
    }
    
    displayPathResult(pathData) {
        const resultContainer = document.getElementById('pathResult');
        const clearBtn = document.getElementById('clearPathBtn');
        
        if (!pathData.reachable) {
            resultContainer.innerHTML = `
                <div class="alert alert-warning">
                    <i class="fas fa-exclamation-triangle"></i>
                    <strong>No Path Found</strong><br>
                    No route exists between the selected nodes.
                </div>
            `;
        } else {
            const pathNodes = pathData.path.map((nodeId, index) => {
                const isFirst = index === 0;
                const isLast = index === pathData.path.length - 1;
                const icon = isFirst ? 'fas fa-play' : (isLast ? 'fas fa-flag-checkered' : 'fas fa-circle');
                const className = isFirst ? 'text-success' : (isLast ? 'text-danger' : 'text-primary');
                
                return `<span class="${className}"><i class="${icon}"></i> ${nodeId.substring(0, 8)}...</span>`;
            }).join(' → ');
            
            resultContainer.innerHTML = `
                <div class="alert alert-success">
                    <i class="fas fa-check-circle"></i>
                    <strong>Path Found!</strong><br>
                    <small><strong>Distance:</strong> ${pathData.distance} hops</small><br>
                    <small><strong>Nodes:</strong> ${pathData.path.length}</small>
                </div>
                <div class="path-visualization">
                    <strong>Route:</strong><br>
                    <div class="path-nodes">${pathNodes}</div>
                </div>
            `;
        }
        
        resultContainer.style.display = 'block';
        clearBtn.style.display = 'inline-block';
    }
    
    clearPath() {
        this.currentPath = null;
        
        // Clear UI elements
        document.getElementById('pathResult').style.display = 'none';
        document.getElementById('clearPathBtn').style.display = 'none';
        
        const sourceInput = document.getElementById('sourceNode');
        const destinationInput = document.getElementById('destinationNode');
        
        sourceInput.value = '';
        destinationInput.value = '';
        
        // Remove validation classes
        sourceInput.classList.remove('is-valid', 'is-invalid');
        destinationInput.classList.remove('is-valid', 'is-invalid');
        
        document.getElementById('findPathBtn').disabled = true;
        
        // Clear path visualization
        if (this.visualizer && this.visualizer.clearPath) {
            this.visualizer.clearPath();
        }
    }
}

// Initialize the application when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new IoTNetworkApp();
});