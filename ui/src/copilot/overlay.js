import { customElement, state } from 'lit/decorators.js';
import { ref, createRef } from 'lit/directives/ref.js';
import { css, html, LitElement } from 'lit';

@customElement('pipeline-editor')
export class PipelineEditor extends LitElement {
  static styles = css`
    #pipelineContainer {
      position: relative;
      width: 100%;
      height: 600px;
      border: 1px solid #ccc;
    }
    .pipeline-node {
      position: absolute;
      padding: 10px;
      background-color: #444;
      color: #fff;
      border-radius: 5px;
      cursor: grab;
      z-index: 2;
    }
    .pipeline-node-header {
      font-weight: bold;
      margin-bottom: 5px;
    }
    .pipeline-connection {
      stroke: #888;
      stroke-width: 2;
      fill: none;
    }
  `;
  
  @state() pipelineData = {
    id: 'experimental_pipeline',
    name: 'Experimental Pipeline',
    description: 'This pipeline is used to test experimental features.',
    steps: [
      { id: 'process_uploaded_files', inputs: {} },
      { id: 'fetch_html_and_screenshot', inputs: {} },
      { id: 'generate_image_captions', inputs: { images: 'process_uploaded_files.images' } },
      {
        id: 'generate_bootstrap_page_html',
        inputs: {
          text_content: 'process_uploaded_files.text_content',
          images: 'process_uploaded_files.images',
          captions: 'generate_image_captions',
          screenshot: 'fetch_html_and_screenshot.screenshot',
        },
      },
      {
        id: 'create_page_from_html',
        inputs: {
          html: 'generate_bootstrap_page_html',
          images: 'process_uploaded_files.images',
        },
      },
    ],
  };
  
  containerRef = createRef();
  
  firstUpdated() {
    this.renderNodes();
    this.renderConnections();
    this.enableDragging();
  }
  
  renderNodes() {
    const container = this.containerRef.value;
    if (container) {
      this.pipelineData.steps.forEach((step, index) => {
        const nodeElement = document.createElement('div');
        nodeElement.className = 'pipeline-node';
        nodeElement.id = `node-${step.id}`;
        nodeElement.style.top = `${index * 120}px`;
        nodeElement.style.left = '50px';
        
        nodeElement.innerHTML = `
          <div class="pipeline-node-header">${step.id}</div>
          <div>${step.inputs ? JSON.stringify(step.inputs) : 'No Inputs'}</div>
        `;
        
        container.appendChild(nodeElement);
      });
    }
  }
  
  renderConnections() {
    const container = this.containerRef.value;
    if (container) {
      const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
      svg.setAttribute('id', 'pipeline-connections');
      container.appendChild(svg);
      
      this.pipelineData.steps.forEach((step) => {
        for (const [inputKey, inputValue] of Object.entries(step.inputs || {})) {
          const sourceNodeId = inputValue.split('.')[0];
          const sourceNode = container.querySelector(`#node-${sourceNodeId}`);
          const targetNode = container.querySelector(`#node-${step.id}`);
          if (sourceNode && targetNode) {
            this.createConnection(svg, sourceNode, targetNode);
          }
        }
      });
    }
  }
  
  createConnection(svg, sourceNode, targetNode) {
    const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    const sourceRect = sourceNode.getBoundingClientRect();
    const targetRect = targetNode.getBoundingClientRect();
    
    line.setAttribute('x1', `${sourceRect.right}`);
    line.setAttribute('y1', `${sourceRect.top + sourceRect.height / 2}`);
    line.setAttribute('x2', `${targetRect.left}`);
    line.setAttribute('y2', `${targetRect.top + targetRect.height / 2}`);
    line.classList.add('pipeline-connection');
    
    svg.appendChild(line);
  }
  
  enableDragging() {
    const nodes = this.shadowRoot.querySelectorAll('.pipeline-node');
    nodes.forEach((node) => {
      node.addEventListener('mousedown', this.dragStart.bind(this));
    });
  }
  
  dragStart(event) {
    event.preventDefault();
    const target = event.target;
    const node = target.closest('.pipeline-node');
    if (!node) return;
    
    let offsetX = event.clientX - node.offsetLeft;
    let offsetY = event.clientY - node.offsetTop;
    
    const drag = (moveEvent) => {
      node.style.left = `${moveEvent.clientX - offsetX}px`;
      node.style.top = `${moveEvent.clientY - offsetY}px`;
      this.updateConnections();
    };
    
    const stopDrag = () => {
      document.removeEventListener('mousemove', drag);
      document.removeEventListener('mouseup', stopDrag);
    };
    
    document.addEventListener('mousemove', drag);
    document.addEventListener('mouseup', stopDrag);
  }
  
  updateConnections() {
    const container = this.containerRef.value;
    const svg = container.querySelector('svg');
    if (svg) {
      while (svg.firstChild) {
        svg.removeChild(svg.firstChild);
      }
      this.renderConnections();
    }
  }
  
  render() {
    return html`
      <div id="pipelineContainer" ${ref(this.containerRef)}></div>
    `;
  }
}
