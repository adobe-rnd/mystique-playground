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
          let nodeColor = '#ffffff'; // Default white color
          
          // Use the type property to determine node color
          const nodeType = context.payload.type || 'processing'; // Default to 'processing' if type is not defined
          
          // Set colors based on node type
          if (nodeType === 'input') {
            nodeColor = '#4caf50'; // Green for input nodes
          } else if (nodeType === 'output') {
            nodeColor = '#f44336'; // Red for output nodes
          } else if (nodeType === 'processing') {
            nodeColor = '#2196f3'; // Blue for processing nodes
          }
          
          // Return the custom node template
          return ({ emit }) => html`
                    <rete-node style="background-color: ${nodeColor}" .data=${context.payload} .emit=${emit}>
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
    // this.area.use(minimap);
    
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
      const stepDetails = this.stepsData.find(s => s.id === step.type);
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
          
          // Check if the input comes from the global inputs
          if (inputValue.startsWith("inputs.")) {
            sourceNodeId = inputValue; // Directly use inputValue as it already contains the global input node identifier
            outputName = inputName; // The output from the global input node will have the same name as the input
          } else {
            // If not a global input, split as usual
            [sourceNodeId, outputName] = inputValue.split('.');
          }
          
          const sourceNode = nodesMap.get(sourceNodeId);
          
          if (sourceNode) {
            const output = sourceNode.outputs[outputName];
            const input = node.inputs[inputName];
            
            if (output && input) {
              this.editor.addConnection(new ClassicPreset.Connection(sourceNode, outputName, node, inputName));
            } else {
              console.warn(`Cannot find matching socket for input: ${inputName} or output: ${outputName}`);
            }
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
    
    node.type = 'processing'; // Add type property
    return node;
  }
  
  async deletePipeline() {
    if (!this.editor) return;
    await this.editor.clear();
  }
  
  autoZoom() {
    AreaExtensions.zoomAt(this.area, this.editor.getNodes());
  }
  
  async autoArrange() {
    const nodes = this.editor.getNodes();
    const grid = 300;
    const margin = 50;
    const positions = new Map();
    const processedNodes = new Set();
    const levels = new Map();
    
    const findRootNodes = () => {
      const connections = this.editor.getConnections();
      return nodes.filter(node => {
        if (!node) return false; // Ensure the node is defined
        const inputs = connections.filter(conn => conn.target === node.id);
        return inputs.length === 0;
      });
    };
    
    const arrangeNode = (node, depth = 0) => {
      if (!node || processedNodes.has(node.id)) return; // Check if node is defined and not already processed
      processedNodes.add(node.id);
      
      if (!levels.has(depth)) {
        levels.set(depth, []);
      }
      levels.get(depth).push(node);
      
      const outputs = this.editor.getConnections().filter(conn => conn.source === node.id);
      for (const output of outputs) {
        const childNode = nodes.find(n => n && n.id === output.target); // Ensure childNode is defined
        if (childNode) arrangeNode(childNode, depth + 1);
      }
    };
    
    const rootNodes = findRootNodes();
    rootNodes.forEach(rootNode => arrangeNode(rootNode));
    
    for (let [depth, nodesAtDepth] of levels.entries()) {
      const totalHeight = (nodesAtDepth.length - 1) * (grid + margin);
      let currentY = -totalHeight / 2;
      
      for (const node of nodesAtDepth) {
        const x = depth * grid + (node.type === 'input' ? -grid/2 : node.type === 'output' ? grid/2 : 0);
        const y = currentY;
        positions.set(node.id, { x, y });
        currentY += grid + margin;
      }
    }
    
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
