import { LitElement, html, css } from 'lit';
import { customElement, state } from 'lit/decorators.js';
import { NodeEditor, ClassicPreset } from "rete";
import { AreaPlugin, AreaExtensions } from "rete-area-plugin";
import { ConnectionPlugin, Presets as ConnectionPresets } from "rete-connection-plugin";
import { LitPlugin, Presets } from "@retejs/lit-plugin";
import { AutoArrangePlugin, Presets as ArrangePresets, ArrangeAppliers } from "rete-auto-arrange-plugin";

import '@spectrum-web-components/picker/sp-picker.js';

@customElement('pipeline-editor')
class PipelineEditor extends LitElement {
  static styles = css`
    #pipelineContainer {
      width: 100%;
      height: 600px;
      border: 1px solid #ccc;
      border-radius: 5px;
      position: relative;
    }
    #controls {
      margin-bottom: 10px;
      display: flex;
      gap: 10px;
    }
  `;
  
  @state() accessor pipelineData = null;
  @state() accessor stepsData = null;
  @state() accessor pipelines = [];
  @state() accessor selectedPipeline = '';
  
  socket = null;
  editor = null;
  area = null;
  arrange = null;
  
  async firstUpdated() {
    await this.fetchPipelines();
    this.selectedPipeline = this.pipelines[0]?.id || '';
    await this.fetchPipelineData();
    await this.fetchStepsData();
    await this.initializeEditor();
    await this.createPipeline();
  }
  
  async fetchPipelines() {
    const response = await fetch('http://localhost:4003/pipelines');
    this.pipelines = await response.json();
  }
  
  async fetchPipelineData() {
    const response = await fetch(`http://localhost:4003/pipeline/${this.selectedPipeline}`);
    this.pipelineData = await response.json();
  }
  
  async fetchStepsData() {
    const response = await fetch('http://localhost:4003/pipeline-steps');
    this.stepsData = await response.json();
  }
  
  async initializeEditor() {
    if (!this.pipelineData || !this.stepsData) return;
    
    const container = this.renderRoot.querySelector('#pipelineContainer');
    this.socket = new ClassicPreset.Socket("socket");
    
    this.editor = new NodeEditor();
    this.area = new AreaPlugin(container);
    this.arrange = new AutoArrangePlugin();
    
    const connection = new ConnectionPlugin();
    const render = new LitPlugin();
    
    AreaExtensions.selectableNodes(this.area, AreaExtensions.selector(), {
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
      Object.entries(step.inputs).forEach(([inputName, inputValue]) => {
        const [sourceNodeId, outputName] = inputValue.split('.');
        const sourceNode = nodesMap.get(sourceNodeId);
        console.log(`Connecting ${sourceNodeId}:${outputName} to ${step.id}:${inputName}`);
        if (sourceNode) {
          this.editor.addConnection(new ClassicPreset.Connection(sourceNode, outputName, node, inputName));
        }
      });
    }
    
    setTimeout(() => {
      this.autoArrange();
      setTimeout(() => {
        this.autoZoom();
      }, 1000);
    }, 200);
  }
 
  async deletePipeline() {
    await this.editor.clear();
  }
  
  createNode(step, stepDetails, socket) {
    const maxNodeNameLength = 15;
    
    const nodeNameWithEllipsis = stepDetails.name.length > maxNodeNameLength
      ? `${stepDetails.name.slice(0, maxNodeNameLength)}...`
      : stepDetails.name;
    
    const node = new ClassicPreset.Node(nodeNameWithEllipsis);
    
    // Create inputs based on the step details
    for (const inputName of stepDetails.inputs || []) {
      node.addInput(inputName, new ClassicPreset.Input(socket, inputName));
    }
    
    // Create outputs based on the step details
    for (const outputName of stepDetails.outputs || []) {
      node.addOutput(outputName, new ClassicPreset.Output(socket, outputName));
    }
    
    return node;
  }
  
  autoZoom() {
    AreaExtensions.zoomAt(this.area, this.editor.getNodes());
  }
  
  async autoArrange() {
    const nodes = this.editor.getNodes();
    const grid = 250; // Horizontal grid size (distance between columns)
    const margin = 50; // Vertical margin between nodes
    const positions = new Map(); // To store node positions
    const processedNodes = new Set(); // To keep track of arranged nodes
    const levels = new Map(); // To track which level each node belongs to
    
    // Helper function to find nodes without inputs (root nodes)
    const findRootNodes = () => {
      const connections = this.editor.getConnections();
      return nodes.filter(node => {
        const inputs = connections.filter(conn => conn.target === node.id);
        return inputs.length === 0;
      });
    };
    
    // Recursive function to arrange nodes
    const arrangeNode = (node, depth = 0) => {
      if (processedNodes.has(node.id)) return;
      processedNodes.add(node.id);
      
      // Assign the node to its level
      if (!levels.has(depth)) {
        levels.set(depth, []);
      }
      levels.get(depth).push(node);
      
      // Get output connections and arrange connected nodes
      const outputs = this.editor.getConnections().filter(conn => conn.source === node.id);
      for (const output of outputs) {
        const childNode = nodes.find(n => n.id === output.target);
        arrangeNode(childNode, depth + 1);
      }
    };
    
    // Start arranging from root nodes
    const rootNodes = findRootNodes();
    rootNodes.forEach(rootNode => arrangeNode(rootNode));
    
    // Calculate vertical positioning and apply positions
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
    
    // Apply the calculated positions
    for (const node of nodes) {
      const position = positions.get(node.id);
      await this.area.translate(node.id, position);
    }
  }
  
  async handlePipelineChange(event) {
    this.selectedPipeline = event.target.value;
    await this.fetchPipelineData();
    await this.deletePipeline();
    await this.createPipeline();
  }
  
  render() {
    return html`
      <div id="controls">
        <sp-button variant="secondary" @click=${this.autoZoom}>Auto Zoom</sp-button>
        <sp-button variant="secondary" @click=${this.autoArrange}>Auto Arrange</sp-button>
        <sp-picker label="Select Pipeline" @change=${this.handlePipelineChange}>
          ${this.pipelines.map(pipeline => html`
            <sp-menu-item value="${pipeline.id}" ?selected=${pipeline.id === this.selectedPipeline}>
              ${pipeline.name}
            </sp-menu-item>
          `)}
        </sp-picker>
      </div>
      <div id="pipelineContainer"></div>
    `;
  }
}
