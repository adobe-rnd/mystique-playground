import { LitElement, html, css } from 'lit';
import { customElement, state } from 'lit/decorators.js';
import { NodeEditor, ClassicPreset } from "rete";
import { AreaPlugin, AreaExtensions } from "rete-area-plugin";
import { ConnectionPlugin, Presets as ConnectionPresets } from "rete-connection-plugin";
import { LitPlugin, Presets } from "@retejs/lit-plugin";
import { AutoArrangePlugin, Presets as ArrangePresets, ArrangeAppliers } from "rete-auto-arrange-plugin";

import '@spectrum-web-components/picker/sp-picker.js';
import '@spectrum-web-components/button/sp-button.js';
import '@spectrum-web-components/progress-circle/sp-progress-circle.js';

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
    .warning {
      color: red;
      font-size: 14px;
      margin-top: 10px;
    }
    .center-message {
      display: flex;
      flex-direction: column;
      align-items: center;
      text-align: center;
    }
    .icon {
      font-size: 48px;
      color: #888;
      margin-bottom: 10px;
    }
    .progress-container {
      display: flex;
      justify-content: center;
      align-items: center;
      width: 100%;
      height: 100%;
    }
  `;
  
  @state() accessor pipelineData = null;
  @state() accessor stepsData = null;
  @state() accessor pipelines = [];
  @state() accessor selectedPipeline = '';
  @state() accessor loading = false;
  
  socket = null;
  editor = null;
  area = null;
  arrange = null;
  
  async firstUpdated() {
    await this.fetchPipelines();
    await this.fetchStepsData();
  }
  
  async fetchPipelines() {
    const response = await fetch('http://localhost:4003/pipelines');
    this.pipelines = await response.json();
  }
  
  async fetchPipelineData() {
    if (!this.selectedPipeline) return;
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
      Object.entries(step.inputs).forEach(([inputName, inputValue]) => {
        const [sourceNodeId, outputName] = inputValue.split('.');
        const sourceNode = nodesMap.get(sourceNodeId);
        if (sourceNode) {
          this.editor.addConnection(new ClassicPreset.Connection(sourceNode, outputName, node, inputName));
        }
      });
    }
    
    this.loading = true; // Show progress indicator
    
    setTimeout(() => {
      this.autoArrange();
      setTimeout(() => {
        this.autoZoom();
        this.loading = false; // Hide progress indicator
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
    
    for (const inputName of stepDetails.inputs || []) {
      node.addInput(inputName, new ClassicPreset.Input(socket, inputName));
    }
    
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
    const grid = 250;
    const margin = 50;
    const positions = new Map();
    const processedNodes = new Set();
    const levels = new Map();
    
    const findRootNodes = () => {
      const connections = this.editor.getConnections();
      return nodes.filter(node => {
        const inputs = connections.filter(conn => conn.target === node.id);
        return inputs.length === 0;
      });
    };
    
    const arrangeNode = (node, depth = 0) => {
      if (processedNodes.has(node.id)) return;
      processedNodes.add(node.id);
      
      if (!levels.has(depth)) {
        levels.set(depth, []);
      }
      levels.get(depth).push(node);
      
      const outputs = this.editor.getConnections().filter(conn => conn.source === node.id);
      for (const output of outputs) {
        const childNode = nodes.find(n => n.id === output.target);
        arrangeNode(childNode, depth + 1);
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
      await this.area.translate(node.id, position);
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
      <div id="pipelineContainer">
        ${this.loading ? html`
        <div class="progress-container">
          <sp-progress-circle size="large" indeterminate></sp-progress-circle>
        </div>
      ` : html`
        ${!this.selectedPipeline ? html`
          <div class="center-message">
            <div class="icon">⚠️</div>
            <div>Please select a pipeline to load.</div>
          </div>
        ` : ''}
      `}
      </div>
    `;
  }
}
