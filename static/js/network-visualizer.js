// IoT Network Visualizer - D3.js Implementation

class NetworkVisualizer {
    constructor(containerId) {
        this.containerId = containerId;
        this.container = d3.select(`#${containerId}`);
        this.svg = null;
        this.simulation = null;
        this.nodes = [];
        this.links = [];
        this.selectedNode = null;
        this.showLabels = false;
        this.showRanges = false;
        this.zoomBehavior = null;
        this.highlightedPath = null;
        
        this.width = 0;
        this.height = 0;
        
        // Color scheme for different connectivity levels
        // Improved color palette with better contrast and more colors
        this.colorScale = d3.scaleOrdinal()
            .domain([0, 1, 2, 3, 4, 5, 6, 7, 8])
            .range([
                '#e74c3c',  // Red - Isolated (0 connections)
                '#f39c12',  // Orange - Very Low (1 connection)
                '#f1c40f',  // Yellow - Low (2 connections)  
                '#2ecc71',  // Green - Medium (3 connections)
                '#3498db',  // Blue - Good (4 connections)
                '#9b59b6',  // Purple - High (5 connections)
                '#e91e63',  // Pink - Very High (6 connections)
                '#795548',  // Brown - Extremely High (7 connections)
                '#607d8b'   // Blue Grey - Maximum (8+ connections)
            ]);
        
        this.initializeVisualization();
    }
    
    initializeVisualization() {
        // Clear any existing content
        this.container.selectAll('*').remove();
        
        // Get container dimensions
        const rect = this.container.node().getBoundingClientRect();
        this.width = rect.width;
        this.height = rect.height;
        
        // Create SVG
        this.svg = this.container.append('svg')
            .attr('class', 'network-svg')
            .attr('width', this.width)
            .attr('height', this.height);
        
        // Create zoom behavior
        this.zoomBehavior = d3.zoom()
            .scaleExtent([0.1, 10])
            .on('zoom', (event) => {
                this.svg.select('.zoom-group').attr('transform', event.transform);
            });
        
        this.svg.call(this.zoomBehavior);
        
        // Create main group for zooming
        this.mainGroup = this.svg.append('g')
            .attr('class', 'zoom-group');
        
        // Create groups for different elements
        this.linksGroup = this.mainGroup.append('g').attr('class', 'links');
        this.pathGroup = this.mainGroup.append('g').attr('class', 'path-links');
        this.rangesGroup = this.mainGroup.append('g').attr('class', 'ranges');
        this.nodesGroup = this.mainGroup.append('g').attr('class', 'nodes');
        this.labelsGroup = this.mainGroup.append('g').attr('class', 'labels');
        
        // Add tooltip
        this.tooltip = d3.select('body').append('div')
            .attr('class', 'tooltip')
            .style('opacity', 0);
    }
    
    loadNetworkData(data) {
        // Clear previous network data and visualization
        this.clearNetwork();
        
        this.nodes = data.nodes || [];
        this.links = data.links || [];
        
        if (this.nodes.length === 0) {
            this.showEmptyState();
            return;
        }
        
        this.createSimulation();
        this.renderNetwork();
        this.fitToView();
    }
    
    clearNetwork() {
        // Stop existing simulation
        if (this.simulation) {
            this.simulation.stop();
        }
        
        // Clear selected node
        this.selectedNode = null;
        
        // Remove all existing elements
        this.linksGroup.selectAll('*').remove();
        this.rangesGroup.selectAll('*').remove();
        this.nodesGroup.selectAll('*').remove();
        this.labelsGroup.selectAll('*').remove();
        
        // Clear data arrays
        this.nodes = [];
        this.links = [];
    }
    
    createSimulation() {
        // Create force simulation
        this.simulation = d3.forceSimulation(this.nodes)
            .force('link', d3.forceLink(this.links).id(d => d.id).distance(d => Math.min(d.distance * 0.5, 100)))
            .force('charge', d3.forceManyBody().strength(-300))
            .force('center', d3.forceCenter(this.width / 2, this.height / 2))
            .force('collision', d3.forceCollide().radius(d => Math.max(10, d.neighbors * 2 + 5)))
            .on('tick', () => this.updatePositions());
    }
    
    renderNetwork() {
        // Render links
        this.renderLinks();
        
        // Render range circles
        this.renderRangeCircles();
        
        // Render nodes
        this.renderNodes();
        
        // Render labels
        this.renderLabels();
    }
    
    renderLinks() {
        const links = this.linksGroup.selectAll('.link')
            .data(this.links);
        
        // Remove old links
        links.exit().remove();
        
        // Add new links
        links.enter().append('line')
            .attr('class', 'link')
            .attr('stroke-width', d => Math.max(1, d.strength * 3));
    }
    
    renderRangeCircles() {
        const ranges = this.rangesGroup.selectAll('.range-circle')
            .data(this.nodes);
        
        // Remove old ranges
        ranges.exit().remove();
        
        // Add new ranges
        ranges.enter().append('circle')
            .attr('class', 'range-circle')
            .attr('r', d => d.range * 0.5) // Scale down the range for better visualization
            .attr('fill', 'none')
            .attr('stroke', '#007bff')
            .attr('stroke-dasharray', '3,3')
            .attr('opacity', 0);
    }
    
    renderNodes() {
        const nodes = this.nodesGroup.selectAll('.node')
            .data(this.nodes);
        
        // Remove old nodes
        nodes.exit().remove();
        
        // Add new nodes
        nodes.enter().append('circle')
            .attr('class', 'node')
            .attr('r', d => Math.max(8, d.neighbors * 2 + 5))
            .attr('fill', d => this.colorScale(Math.min(d.neighbors, 8)))
            .call(this.createDragBehavior())
            .on('click', (event, d) => this.selectNode(d))
            .on('mouseover', (event, d) => this.showTooltip(event, d))
            .on('mouseout', () => this.hideTooltip());
    }
    
    renderLabels() {
        const labels = this.labelsGroup.selectAll('.node-label')
            .data(this.nodes);
        
        // Remove old labels
        labels.exit().remove();
        
        // Add new labels
        labels.enter().append('text')
            .attr('class', 'node-label')
            .attr('text-anchor', 'middle')
            .attr('dy', -15)
            .text(d => d.eui64.split('-').slice(-2).join('-')) // Show last 2 bytes
            .style('font-size', '10px')
            .style('font-weight', 'bold')
            .style('fill', '#333')
            .style('opacity', this.showLabels ? 1 : 0);
    }
    
    updatePositions() {
        // Update link positions
        this.linksGroup.selectAll('.link')
            .attr('x1', d => d.source.x)
            .attr('y1', d => d.source.y)
            .attr('x2', d => d.target.x)
            .attr('y2', d => d.target.y);
        
        // Update node positions
        this.nodesGroup.selectAll('.node')
            .attr('cx', d => d.x)
            .attr('cy', d => d.y);
        
        // Update range circle positions
        this.rangesGroup.selectAll('.range-circle')
            .attr('cx', d => d.x)
            .attr('cy', d => d.y);
        
        // Update label positions
        this.labelsGroup.selectAll('.node-label')
            .attr('x', d => d.x)
            .attr('y', d => d.y);
        
        // Update path positions if a path is highlighted
        this.updatePathPosition();
    }
    
    createDragBehavior() {
        return d3.drag()
            .on('start', (event, d) => {
                if (!event.active) this.simulation.alphaTarget(0.3).restart();
                d.fx = d.x;
                d.fy = d.y;
            })
            .on('drag', (event, d) => {
                d.fx = event.x;
                d.fy = event.y;
            })
            .on('end', (event, d) => {
                if (!event.active) this.simulation.alphaTarget(0);
                d.fx = null;
                d.fy = null;
            });
    }
    
    selectNode(node) {
        // Clear previous selection
        this.nodesGroup.selectAll('.node').classed('selected', false);
        this.linksGroup.selectAll('.link').classed('highlighted', false);
        this.rangesGroup.selectAll('.range-circle').style('opacity', 0);
        
        // Select new node
        this.selectedNode = node;
        
        // Highlight selected node
        this.nodesGroup.selectAll('.node')
            .filter(d => d.id === node.id)
            .classed('selected', true);
        
        // Show range circle for selected node
        this.rangesGroup.selectAll('.range-circle')
            .filter(d => d.id === node.id)
            .style('opacity', 0.3);
        
        // Highlight connected links
        this.linksGroup.selectAll('.link')
            .filter(d => d.source.id === node.id || d.target.id === node.id)
            .classed('highlighted', true);
        
        // Update node details panel
        this.updateNodeDetails(node);
    }
    
    updateNodeDetails(node) {
        // This will be called by the main app
        if (window.updateNodeDetails) {
            window.updateNodeDetails(node);
        }
    }
    
    showTooltip(event, node) {
        const tooltip = this.tooltip;
        
        tooltip.transition()
            .duration(200)
            .style('opacity', 1);
        
        tooltip.html(`
            <strong>EUI-64:</strong> ${node.eui64}<br>
            <strong>Position:</strong> (${node.x.toFixed(1)}, ${node.y.toFixed(1)})<br>
            <strong>Range:</strong> ${node.range}<br>
            <strong>Connections:</strong> ${node.neighbors}
        `)
            .style('left', (event.pageX + 10) + 'px')
            .style('top', (event.pageY - 28) + 'px');
    }
    
    hideTooltip() {
        this.tooltip.transition()
            .duration(200)
            .style('opacity', 0);
    }
    
    toggleLabels() {
        this.showLabels = !this.showLabels;
        
        this.labelsGroup.selectAll('.node-label')
            .transition()
            .duration(300)
            .style('opacity', this.showLabels ? 1 : 0);
    }
    
    toggleRanges() {
        this.showRanges = !this.showRanges;
        
        if (this.showRanges) {
            this.rangesGroup.selectAll('.range-circle')
                .transition()
                .duration(300)
                .style('opacity', 0.2);
        } else {
            this.rangesGroup.selectAll('.range-circle')
                .transition()
                .duration(300)
                .style('opacity', 0);
        }
    }
    
    fitToView() {
        if (this.nodes.length === 0) return;
        
        const bounds = this.getBounds();
        const width = bounds.maxX - bounds.minX;
        const height = bounds.maxY - bounds.minY;
        
        const midX = (bounds.minX + bounds.maxX) / 2;
        const midY = (bounds.minY + bounds.maxY) / 2;
        
        const scale = Math.min(
            0.8 * this.width / width,
            0.8 * this.height / height,
            2
        );
        
        const translate = [
            this.width / 2 - scale * midX,
            this.height / 2 - scale * midY
        ];
        
        this.svg.transition()
            .duration(750)
            .call(this.zoomBehavior.transform,
                d3.zoomIdentity.translate(translate[0], translate[1]).scale(scale));
    }
    
    getBounds() {
        const xs = this.nodes.map(d => d.x);
        const ys = this.nodes.map(d => d.y);
        
        return {
            minX: Math.min(...xs),
            maxX: Math.max(...xs),
            minY: Math.min(...ys),
            maxY: Math.max(...ys)
        };
    }
    
    resetZoom() {
        this.svg.transition()
            .duration(750)
            .call(this.zoomBehavior.transform, d3.zoomIdentity);
    }
    
    showEmptyState() {
        this.container.selectAll('*').remove();
        
        this.container.append('div')
            .attr('class', 'text-center p-5')
            .html(`
                <i class="fas fa-network-wired fa-3x text-muted mb-3"></i>
                <h4 class="text-muted">No Network Loaded</h4>
                <p class="text-muted">Upload a network file or load a sample to get started</p>
            `);
    }
    
    showLoading() {
        this.container.append('div')
            .attr('class', 'loading-overlay')
            .html('<div class="loading-spinner"></div>');
    }
    
    hideLoading() {
        this.container.select('.loading-overlay').remove();
    }
    
    resize() {
        const rect = this.container.node().getBoundingClientRect();
        this.width = rect.width;
        this.height = rect.height;
        
        if (this.svg) {
            this.svg.attr('width', this.width).attr('height', this.height);
        }
        
        if (this.simulation) {
            this.simulation.force('center', d3.forceCenter(this.width / 2, this.height / 2));
            this.simulation.alpha(0.3).restart();
        }
    }
    
    highlightPath(pathIndices) {
        if (!pathIndices || pathIndices.length < 2) {
            this.clearPath();
            return;
        }
        
        this.highlightedPath = pathIndices;
        
        // Clear existing path highlights
        this.pathGroup.selectAll('*').remove();
        
        // Create path links
        const pathLinks = [];
        for (let i = 0; i < pathIndices.length - 1; i++) {
            const sourceIndex = pathIndices[i];
            const targetIndex = pathIndices[i + 1];
            
            pathLinks.push({
                source: this.nodes[sourceIndex],
                target: this.nodes[targetIndex],
                index: i
            });
        }
        
        // Draw path links
        this.pathGroup.selectAll('.path-link')
            .data(pathLinks)
            .enter().append('line')
            .attr('class', 'path-link')
            .attr('x1', d => d.source.x)
            .attr('y1', d => d.source.y)
            .attr('x2', d => d.target.x)
            .attr('y2', d => d.target.y)
            .attr('stroke', '#ff6b35')
            .attr('stroke-width', 4)
            .attr('stroke-dasharray', '10,5')
            .style('opacity', 0)
            .transition()
            .duration(300)
            .delay((d, i) => i * 100)
            .style('opacity', 0.8);
        
        // Highlight path nodes
        this.nodesGroup.selectAll('.node')
            .style('stroke', (d, i) => {
                if (pathIndices.includes(i)) {
                    if (i === pathIndices[0]) return '#28a745'; // Green for source
                    if (i === pathIndices[pathIndices.length - 1]) return '#dc3545'; // Red for destination
                    return '#ff6b35'; // Orange for intermediate nodes
                }
                return '#fff';
            })
            .style('stroke-width', (d, i) => pathIndices.includes(i) ? 3 : 1);
        
        // Add path direction arrows
        this.pathGroup.selectAll('.path-arrow')
            .data(pathLinks)
            .enter().append('path')
            .attr('class', 'path-arrow')
            .attr('d', d => {
                const dx = d.target.x - d.source.x;
                const dy = d.target.y - d.source.y;
                const length = Math.sqrt(dx * dx + dy * dy);
                const arrowLength = 10;
                const arrowWidth = 6;
                
                // Position arrow at 80% of the link length
                const t = 0.8;
                const x = d.source.x + t * dx;
                const y = d.source.y + t * dy;
                
                // Calculate arrow direction
                const angle = Math.atan2(dy, dx);
                const x1 = x - arrowLength * Math.cos(angle - Math.PI / 6);
                const y1 = y - arrowLength * Math.sin(angle - Math.PI / 6);
                const x2 = x - arrowLength * Math.cos(angle + Math.PI / 6);
                const y2 = y - arrowLength * Math.sin(angle + Math.PI / 6);
                
                return `M ${x} ${y} L ${x1} ${y1} M ${x} ${y} L ${x2} ${y2}`;
            })
            .attr('stroke', '#ff6b35')
            .attr('stroke-width', 2)
            .attr('fill', 'none')
            .style('opacity', 0)
            .transition()
            .duration(300)
            .delay((d, i) => i * 100 + 150)
            .style('opacity', 0.9);
    }
    
    clearPath() {
        this.highlightedPath = null;
        
        // Remove path highlights
        this.pathGroup.selectAll('*')
            .transition()
            .duration(300)
            .style('opacity', 0)
            .remove();
        
        // Reset node styles
        this.nodesGroup.selectAll('.node')
            .transition()
            .duration(300)
            .style('stroke', '#fff')
            .style('stroke-width', 1);
    }
    
    updatePathPosition() {
        if (!this.highlightedPath) return;
        
        // Update path link positions
        this.pathGroup.selectAll('.path-link')
            .attr('x1', d => d.source.x)
            .attr('y1', d => d.source.y)
            .attr('x2', d => d.target.x)
            .attr('y2', d => d.target.y);
        
        // Update arrow positions
        this.pathGroup.selectAll('.path-arrow')
            .attr('d', d => {
                const dx = d.target.x - d.source.x;
                const dy = d.target.y - d.source.y;
                const arrowLength = 10;
                
                const t = 0.8;
                const x = d.source.x + t * dx;
                const y = d.source.y + t * dy;
                
                const angle = Math.atan2(dy, dx);
                const x1 = x - arrowLength * Math.cos(angle - Math.PI / 6);
                const y1 = y - arrowLength * Math.sin(angle - Math.PI / 6);
                const x2 = x - arrowLength * Math.cos(angle + Math.PI / 6);
                const y2 = y - arrowLength * Math.sin(angle + Math.PI / 6);
                
                return `M ${x} ${y} L ${x1} ${y1} M ${x} ${y} L ${x2} ${y2}`;
            });
    }
}

// Export for use in other scripts
window.NetworkVisualizer = NetworkVisualizer;