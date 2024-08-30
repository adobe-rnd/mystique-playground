import { LitElement, html, css } from 'lit';
import { customElement, state } from 'lit/decorators.js';
import { NodeEditor, ClassicPreset } from "rete";
import { AreaPlugin, AreaExtensions } from "rete-area-plugin";
import { ConnectionPlugin, Presets as ConnectionPresets } from "rete-connection-plugin";
import { LitPlugin, Presets } from "@retejs/lit-plugin";
import { AutoArrangePlugin, Presets as ArrangePresets } from "rete-auto-arrange-plugin";

import '@spectrum-web-components/picker/sp-picker.js';
import '@spectrum-web-components/button/sp-button.js';
import '@spectrum-web-components/progress-circle/sp-progress-circle.js';

import './side-rail.js';
import { fetchPipelineData, fetchPipelines, fetchStepsData } from './pipeline-client';

@customElement('pipeline-editor')
class PipelineEditor extends LitElement {
  static styles = css`
    #editorWrapper {
      display: grid;
      grid-template-rows: auto 1fr;
      gap: 10px;
      width: 100%;
      height: 100%;
    }

    #controls {
      display: flex;
      gap: 10px;
      align-items: center;
      margin-bottom: 10px;
    }

    #mainEditor {
      display: grid;
      grid-template-columns: 1fr 250px;
      gap: 20px;
      height: 100%;
    }

    #editor-container {
      border-radius: 5px;
      position: relative;
      height: 600px;
      overflow: hidden;
      border: 2px dashed #ccc;
    }

    #editor-container.drag-over {
      border-color: blue;
    }

    .progress-container, .center-message {
      display: flex;
      justify-content: center;
      align-items: center;
      width: 100%;
      height: 100%;
    }

    .warning {
      color: red;
      font-size: 14px;
      margin-top: 10px;
    }

    .icon {
      font-size: 48px;
      color: #888;
      margin-bottom: 10px;
    }
  `;
  
  @state() accessor pipelineData = null;
  @state() accessor stepsData = null;
  @state() accessor pipelines = [];
  @state() accessor selectedPipeline = '';
  @state() accessor loading = false;
  @state() accessor selectedNodes = new Set(); // Property to store selected nodes
  
  socket = null;
  editor = null;
  area = null;
  arrange = null;
  
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
    this.arrange = new AutoArrangePlugin();
    
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
    
    render.addPreset(Presets.classic.setup());
    connection.addPreset(ConnectionPresets.classic.setup());
    this.arrange.addPreset(ArrangePresets.classic.setup());
    
    this.editor.use(this.area);
    this.area.use(this.arrange);
    this.area.use(connection);
    this.area.use(render);
    
    AreaExtensions.simpleNodesOrder(this.area);
  }
  
  async createPipeline() {
    if (!this.editor) await this.initializeEditor();
    const nodesMap = new Map();
    
    for (const step of this.pipelineData.steps) {
      const stepDetails = this.stepsData.find(s => s.id === step.id);
      if (stepDetails) {
        const node = this.createNode(step, stepDetails, this.socket);
        nodesMap.set(step.id, node);
        await this.editor.addNode(node);
      }
    }
    
    for (const step of this.pipelineData.steps) {
      const node = nodesMap.get(step.id);
      
      // Ensure node exists before creating connections
      if (node) {
        Object.entries(step.inputs).forEach(([inputName, inputValue]) => {
          const [sourceNodeId, outputName] = inputValue.split('.');
          const sourceNode = nodesMap.get(sourceNodeId);
          
          // Validate source node and sockets before creating connections
          if (sourceNode) {
            const output = sourceNode.outputs[outputName];  // Use bracket notation to access output
            const input = node.inputs[inputName];  // Use bracket notation to access input
            
            if (output && input) {
              // Only add the connection if both input and output sockets exist
              this.editor.addConnection(new ClassicPreset.Connection(sourceNode, outputName, node, inputName));
            } else {
              console.warn(`Cannot find matching socket for input: ${inputName} or output: ${outputName}`);
            }
          }
        });
      }
    }
    
    this.loading = true;
    
    setTimeout(() => {
      this.autoArrange();
      setTimeout(() => {
        this.autoZoom();
        this.loading = false;
      }, 1000);
    }, 300);
  }
  
  async deletePipeline() {
    if (!this.editor) return;
    await this.editor.clear();
  }
  
  createNode(step, stepDetails, socket) {
    const maxNodeNameLength = 15;
    
    const nodeNameWithEllipsis = stepDetails.name.length > maxNodeNameLength
      ? `${stepDetails.name.slice(0, maxNodeNameLength)}...`
      : stepDetails.name;
    
    const node = new ClassicPreset.Node(nodeNameWithEllipsis);
    
    // Add inputs to the node
    for (const inputName of stepDetails.inputs || []) {
      // Ensure the socket exists for each input
      node.addInput(inputName, new ClassicPreset.Input(socket, inputName));
    }
    
    // Add outputs to the node
    for (const outputName of stepDetails.outputs || []) {
      // Ensure the socket exists for each output
      node.addOutput(outputName, new ClassicPreset.Output(socket, outputName));
    }
    
    return node;
  }
  
  autoZoom() {
    AreaExtensions.zoomAt(this.area, this.editor.getNodes());
  }
  
  async autoArrange() {
    const nodes = this.editor.getNodes();
    const grid = 250;
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
        const x = depth * grid;
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
        </div>
        <div id="mainEditor">
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
          <side-rail id="sideRail"></side-rail>
        </div>
      </div>
    `;
  }
}
