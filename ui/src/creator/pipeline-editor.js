import { LitElement, html, css } from 'lit';
import { customElement, state } from 'lit/decorators.js';
import { NodeEditor, ClassicPreset } from "rete";
import { AreaPlugin, AreaExtensions } from "rete-area-plugin";
import { MinimapExtra, MinimapPlugin } from "rete-minimap-plugin";
import { ConnectionPlugin, Presets as ConnectionPresets } from "rete-connection-plugin";
import { LitPlugin, Presets } from "@retejs/lit-plugin";

import '@spectrum-web-components/picker/sp-picker.js';
import '@spectrum-web-components/button/sp-button.js';
import '@spectrum-web-components/progress-circle/sp-progress-circle.js';

import { pipelineEditorStyles } from './pipeline-editor-styles.js';

import './side-rail.js';
import { fetchPipelineData, fetchPipelines, fetchStepsData } from './pipeline-api-client.js';

@customElement('pipeline-editor')
class PipelineEditor extends LitElement {
  static styles = pipelineEditorStyles;
  
  @state() accessor pipelineData = null;
  @state() accessor stepsData = null;
  @state() accessor pipelines = [];
  @state() accessor selectedPipeline = '';
  @state() accessor loading = false;
  @state() accessor selectedNodes = new Set(); // Property to store selected nodes
  @state() accessor sideRailCollapsed = true;
  
  socket = null;
  editor = null;
  area = null;
  
  async firstUpdated() {
    await this.fetchPipelines();
    await this.fetchStepsData();
    this.addEventListener('dragover', this.handleDragOver);
    this.addEventListener('drop', this.handleDrop);
  }
  
  async fetchPipelines() {
    this.pipelines = await fetchPipelines();
  }
  
  async fetchPipelineData() {
    if (!this.selectedPipeline) return;
    this.pipelineData = await fetchPipelineData(this.selectedPipeline);
  }
  
  async fetchStepsData() {
    this.stepsData = await fetchStepsData();
  }
  
  async initializeEditor() {
    if (!this.pipelineData || !this.stepsData) return;
    
    const container = this.renderRoot.querySelector('#editor-container');
    this.socket = new ClassicPreset.Socket("socket");
    
    this.editor = new NodeEditor();
    this.area = new AreaPlugin(container);
    
    const connection = new ConnectionPlugin();
    const render = new LitPlugin();
    
    // Define an inline selector using arrow functions to maintain correct context
    const selector = new (class extends AreaExtensions.Selector {
      add = (entity, accumulate) => {
        super.add(entity, accumulate);
        this.selectedNodes.add(entity);  // Use the context of the PipelineEditor component
        console.log('Added node:', entity);
      };
      remove = (entity) => {
        super.remove(entity);
        this.selectedNodes.delete(entity);  // Use the context of the PipelineEditor component
        console.log('Removed node:', entity);
      };
    })();
    
    // Bind the `selectedNodes` property to the selector
    selector.selectedNodes = this.selectedNodes;
    
    // Enable selectable nodes with the custom selector
    AreaExtensions.selectableNodes(this.area, selector, {
      accumulating: AreaExtensions.accumulateOnCtrl(),
    });
    
    const minimap = new MinimapPlugin({
      boundViewport: true
    });
    
    // Customize node rendering with different colors based on the type property
    render.addPreset(Presets.classic.setup({
      customize: {
        node(context) {
          let backgroundColor = '#ffffff'; // Default white color
          let borderColor = '#000000'; // Default black border color
          
          // Use the type property to determine node color
          const nodeType = context.payload.type || 'processing'; // Default to 'processing' if type is not defined
          
          // Set colors based on node type
          if (nodeType === 'input') {
            backgroundColor = '#4caf50'; // Green for input nodes
            borderColor = '#2e7d32'; // Dark green border
          } else if (nodeType === 'output') {
            backgroundColor = '#f44336'; // Red for output nodes
            borderColor = '#c62828'; // Dark red border
          } else if (nodeType === 'processing') {
            backgroundColor = '#2196f3'; // Blue for processing nodes
            borderColor = '#1565c0'; // Dark blue border
          } else if (nodeType === 'pipeline') {
            backgroundColor = '#ff9800'; // Orange for pipeline nodes
            borderColor = '#e65100'; // Dark orange border
          }
          
          // Return the custom node template
          return ({ emit }) => html`
           <rete-node
              data-node-id="${context.payload.id}"
              style="background-color: ${backgroundColor}; border-color: ${borderColor};"
              .data=${context.payload}
              .emit=${emit}>
                <!-- Customize node appearance if needed -->
            </rete-node>
          `;
        }
      }
    }));
    
    render.addPreset(Presets.minimap.setup({ size: 200 }));
    connection.addPreset(ConnectionPresets.classic.setup());
    
    this.editor.use(this.area);
    this.area.use(connection);
    this.area.use(render);
    
    AreaExtensions.simpleNodesOrder(this.area);
  }
  
  async createPipeline() {
    if (!this.editor) await this.initializeEditor();
    const nodesMap = new Map();
    
    // Step 1: Add input nodes
    for (const [inputName, inputValue] of Object.entries(this.pipelineData.inputs)) {
      const inputNode = this.createInputNode(inputName, inputValue, this.socket);
      nodesMap.set(`inputs.${inputName}`, inputNode);
      await this.editor.addNode(inputNode);
    }
    
    // Step 2: Add output nodes
    for (const [outputName, outputValue] of Object.entries(this.pipelineData.outputs)) {
      const outputNode = this.createOutputNode(outputName, outputValue, this.socket);
      nodesMap.set(`outputs.${outputName}`, outputNode);
      await this.editor.addNode(outputNode);
    }
    
    // Step 3: Add pipeline step nodes
    for (const step of this.pipelineData.steps) {
      const stepDetails = this.stepsData.find(s => s.type === step.type || s.type === step?.config?.pipeline_id);
      if (stepDetails) {
        const node = this.createNode(step, stepDetails, this.socket);
        nodesMap.set(step.id, node);
        await this.editor.addNode(node);
      }
    }
    
    // Step 4: Create connections from input nodes to processing step nodes
    for (const step of this.pipelineData.steps) {
      const node = nodesMap.get(step.id);
      
      if (node) {
        Object.entries(step.inputs).forEach(([inputName, inputValue]) => {
          let sourceNodeId, outputName;
          
          console.log('step:', step.type, 'input:', inputName, 'value:', inputValue);
          
          // Check if the input comes from the global inputs
          if (inputValue.startsWith("inputs.")) {
            sourceNodeId = inputValue; // Directly use inputValue as it already contains the global input node identifier
            outputName = inputValue.split('.')[1]; // Extract the output name from the global input
            console.log('Input1:', inputName, sourceNodeId, outputName);
          } else {
            // If not a global input, split as usual
            [sourceNodeId, outputName] = inputValue.split('.');
            console.log('Input2:', inputName, sourceNodeId, outputName);
          }
          
          const sourceNode = nodesMap.get(sourceNodeId);
          
          if (sourceNode) {
            const output = sourceNode.outputs[outputName];
            const input = node.inputs[inputName];
            
            if (output && input) {
              this.editor.addConnection(new ClassicPreset.Connection(sourceNode, outputName, node, inputName));
            } else {
              console.warn(`Cannot find matching socket for input: ${inputName} or output: ${outputName}`);
              console.log('Source Node:', sourceNode);
              console.log('Target Node:', node);
            }
          } else {
            console.warn(`Cannot find source node with ID: ${sourceNodeId}`);
          }
        });
      }
    }
    
    // Step 5: Create connections for output nodes
    for (const [outputName, outputValue] of Object.entries(this.pipelineData.outputs)) {
      const [sourceNodeId, outputPort] = outputValue.split('.');
      console.log('Output:', outputName, sourceNodeId, outputPort);
      const sourceNode = nodesMap.get(sourceNodeId);
      const outputNode = nodesMap.get(`outputs.${outputName}`);
      
      console.log('Source Node:', sourceNode);
      console.log('Output Node:', outputNode);
      
      if (sourceNode && outputNode) {
        this.editor.addConnection(new ClassicPreset.Connection(sourceNode, outputPort, outputNode, outputName));
      }
    }
    
    // Step 6: Auto arrange and zoom
    this.loading = true;
    setTimeout(() => {
      this.autoArrange();
      setTimeout(() => {
        this.autoZoom();
        this.loading = false;
      }, 1000);
    }, 300);
  }
  
  createInputNode(inputName, inputValue, socket) {
    const node = new ClassicPreset.Node(inputName);
    node.customData = { value: inputValue }; // Store the input value for use
    node.addOutput(inputName, new ClassicPreset.Output(socket, inputName));
    node.type = 'input'; // Add type property
    return node;
  }
  
  createOutputNode(outputName, outputValue, socket) {
    const node = new ClassicPreset.Node(outputName);
    node.addInput(outputName, new ClassicPreset.Input(socket, outputName));
    node.type = 'output'; // Add type property
    return node;
  }
  
  createNode(step, stepDetails, socket) {
    const maxNodeNameLength = 15;
    
    const nodeNameWithEllipsis = stepDetails.name.length > maxNodeNameLength
      ? `${stepDetails.name.slice(0, maxNodeNameLength)}...`
      : stepDetails.name;
    
    const node = new ClassicPreset.Node(nodeNameWithEllipsis);
    
    // Add inputs to the node
    for (const inputName of stepDetails.inputs || []) {
      node.addInput(inputName, new ClassicPreset.Input(socket, inputName));
    }
    
    // Add outputs to the node
    for (const outputName of stepDetails.outputs || []) {
      node.addOutput(outputName, new ClassicPreset.Output(socket, outputName));
    }
    
    node.type = step.type === 'pipeline' ? 'pipeline' : 'processing'; // Add type property
    return node;
  }
  
  async deletePipeline() {
    if (!this.editor) return;
    await this.editor.clear();
  }
  
  autoZoom() {
    AreaExtensions.zoomAt(this.area, this.editor.getNodes());
  }
  
  calculateNodeLevelsBFS(processingNodes, inputNodes) {
    const levels = new Map(); // Store the maximum depth level of each node
    const queue = []; // Queue to process nodes in BFS order
    
    const nodes = this.editor.getNodes();
    
    // Start with root processing nodes (nodes with no incoming connections from other processing nodes)
    const findRootProcessingNodes = () => {
      const connections = this.editor.getConnections();
      return processingNodes.filter(node => {
        // Get incoming connections to this node
        const inputs = connections.filter(conn => conn.target === node.id);
        // Check if all incoming connections come from input nodes
        return inputs.every(conn => inputNodes.some(inputNode => inputNode.id === conn.source));
      });
    };
    
    const rootProcessingNodes = findRootProcessingNodes();
    
    // Initialize queue with root processing nodes and set their initial levels to 0
    rootProcessingNodes.forEach(rootNode => {
      levels.set(rootNode.id, 0); // Root nodes have level 0
      queue.push(rootNode);
    });
    
    // Perform BFS to calculate levels for all processing nodes
    while (queue.length > 0) {
      const currentNode = queue.shift(); // Dequeue the next node
      const currentLevel = levels.get(currentNode.id);
      
      // Get all children of the current node
      const outputs = this.editor.getConnections().filter(conn => conn.source === currentNode.id);
      
      outputs.forEach(output => {
        const childNode = nodes.find(n => n && n.id === output.target);
        if (childNode) {
          const existingLevel = levels.get(childNode.id);
          
          // If the child node already has a level, take the maximum of the existing and new levels
          const newLevel = currentLevel + 1;
          if (existingLevel === undefined || newLevel > existingLevel) {
            levels.set(childNode.id, newLevel); // Update level for the child node
            queue.push(childNode); // Enqueue child node for further processing
          }
        }
      });
    }
    
    return levels;
  }
  
  async autoArrange() {
    const nodes = this.editor.getNodes();
    const gridX = 400; // Horizontal space between nodes
    const inputOutputMargin = 50; // Margin between input/output nodes and processing nodes
    const processingMargin = 100; // Margin between processing nodes
    const positions = new Map();
    
    // Separate nodes into input, output, and processing types
    const inputNodes = nodes.filter(node => node.type === 'input');
    const outputNodes = nodes.filter(node => node.type === 'output');
    const processingNodes = nodes.filter(node => node.type === 'processing' || node.type === 'pipeline');
    
    // Function to get the real height of a node by querying the DOM
    const getNodeHeight = (node) => {
      const element = this.renderRoot.querySelector(`[data-node-id="${node.id}"]`); // Use the data attribute to find the element
      return element ? element.offsetHeight : 150; // Default height if element is not found
    };
    
    // Function to arrange nodes vertically in a column with real heights
    const arrangeVerticallyWithHeights = (nodesToArrange, xPosition) => {
      const totalHeight = nodesToArrange.reduce((sum, node) => sum + getNodeHeight(node), 0)
        + (nodesToArrange.length - 1) * inputOutputMargin;
      let currentY = -totalHeight / 2;
      for (const node of nodesToArrange) {
        const nodeHeight = getNodeHeight(node);
        positions.set(node.id, { x: xPosition, y: currentY });
        currentY += nodeHeight + inputOutputMargin; // Add some margin between nodes
      }
    };
    
    // Align input nodes vertically on the left
    arrangeVerticallyWithHeights(inputNodes, -gridX);
    
    // Use the new BFS function to calculate node levels
    const levels = this.calculateNodeLevelsBFS(processingNodes, inputNodes);
    
    // Arrange processing nodes based on their calculated levels
    const nodesByDepth = Array.from(levels.entries()).reduce((acc, [id, depth]) => {
      if (!acc[depth]) acc[depth] = [];
      acc[depth].push(nodes.find(n => n && n.id === id));
      return acc;
    }, {});
    
    // Determine the maximum depth of all processing nodes
    const maxDepth = Math.max(...Array.from(levels.values()));
    
    // Position processing nodes based on their levels
    for (let [depth, nodesAtDepth] of Object.entries(nodesByDepth)) {
      const xPosition = depth * gridX; // Position nodes horizontally by their depth
      const totalHeight = nodesAtDepth.reduce((sum, node) => sum + getNodeHeight(node), 0)
        + processingMargin * (nodesAtDepth.length - 1); // Add margin between nodes
      let currentY = -totalHeight / 2;
      
      for (const node of nodesAtDepth) {
        const nodeHeight = getNodeHeight(node);
        positions.set(node.id, { x: xPosition, y: currentY });
        currentY += nodeHeight + processingMargin; // Add some margin between nodes
      }
    }
    
    // Dynamically position output nodes just beyond the maximum depth of processing nodes
    const outputXPosition = (maxDepth) * gridX; // One step beyond the maximum processing depth
    arrangeVerticallyWithHeights(outputNodes, outputXPosition);
    
    // Apply calculated positions to nodes
    for (const node of nodes) {
      const position = positions.get(node.id);
      if (position) {
        await this.area.translate(node.id, position);
      }
    }
  }
  
  async handlePipelineChange(event) {
    this.selectedPipeline = event.target.value;
    if (!this.selectedPipeline) {
      alert('Please select a pipeline to load.');
      return;
    }
    await this.deletePipeline();
    await this.fetchPipelineData();
    await this.createPipeline();
  }
  
  handleDragOver(event) {
    event.preventDefault();
    this.renderRoot.querySelector('#editor-container').classList.add('drag-over');
  }
  
  handleDrop(event) {
    event.preventDefault();
    this.renderRoot.querySelector('#editor-container').classList.remove('drag-over');
    
    const stepId = event.dataTransfer.getData('step-id');
    const stepDetails = this.stepsData.find((step) => step.id === stepId);
    
    if (stepDetails) {
      const node = this.createNode({ id: stepId }, stepDetails, this.socket);
      this.editor.addNode(node);
    }
  }
  
  toggleSideRail() {
    this.sideRailCollapsed = !this.sideRailCollapsed;
  }
  
  async deleteSelectedNodes() {
    if (!this.selectedNodes || this.selectedNodes.size === 0) {
      alert('No nodes selected for deletion.');
      return;
    }
    
    // Delete all connections related to each selected node
    Array.from(this.selectedNodes).forEach((node) => {
      console.log('Deleting node:', node);
      const connectionsToRemove = this.editor.getConnections().filter(conn =>
        conn.source === node.id || conn.target === node.id
      );
      
      // Remove all related connections
      connectionsToRemove.forEach(conn => {
        console.log('Removing connection:', conn);
        this.editor.removeConnection(conn.id);
      });
      
      // Now remove the node
      this.editor.removeNode(node.id);
    });
    
    this.selectedNodes.clear(); // Clear selection after deletion
  }
  
  render() {
    return html`
      <div id="editorWrapper">
        <div id="controls">
          <sp-button variant="secondary" @click=${this.autoZoom}>Auto Zoom</sp-button>
          <sp-button variant="secondary" @click=${this.autoArrange}>Auto Arrange</sp-button>
          <sp-button variant="secondary" @click=${this.deleteSelectedNodes}>Delete Selected</sp-button>
          <sp-picker label="Select Pipeline" @change=${this.handlePipelineChange}>
            ${this.pipelines.map(
      (pipeline) => html`
                <sp-menu-item value="${pipeline.id}" ?selected=${pipeline.id === this.selectedPipeline}>
                  ${pipeline.name}
                </sp-menu-item>
              `
    )}
          </sp-picker>
          <sp-button
                  id="collapseButton"
                  variant="secondary"
                  @click=${this.toggleSideRail}>
            ${this.sideRailCollapsed ? 'Expand Side Panel' : 'Collapse Side Panel'}
          </sp-button>
        </div>
        <div id="mainEditor" class=${this.sideRailCollapsed ? 'expanded' : ''}>
          <div id="editor-container">
            ${this.loading
      ? html`
                <div class="progress-container">
                  <sp-progress-circle size="large" indeterminate></sp-progress-circle>
                </div>
              `
      : html`
                ${!this.selectedPipeline
        ? html`
                    <div class="center-message">
                      <div class="icon">⚠️</div>
                      <div>Please select a pipeline to load.</div>
                    </div>
                  `
        : ''}
              `}
          </div>
          <div id="sideRail" class=${this.sideRailCollapsed ? 'collapsed' : ''}>
            <side-rail></side-rail>
          </div>
        </div>
      </div>
    `;
  }
}
