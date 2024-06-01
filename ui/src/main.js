import {LitElement, html, css} from 'lit';
import {customElement, state} from 'lit/decorators.js';
import wretch from 'wretch';

import '@spectrum-web-components/theme/sp-theme.js';
import '@spectrum-web-components/theme/src/themes.js';

import '@spectrum-web-components/button/sp-button.js';
import '@spectrum-web-components/progress-circle/sp-progress-circle.js';

import './main.css';

async function resourceExists(url) {
  try {
    const response = await wretch(url).head().res();
    return response.ok;
  } catch (error) {
    return false;
  }
}

function getCssSelector(element) {
  if (element.id) {
    return `#${element.id}`;
  }
  let selector = element.nodeName.toLowerCase();
  if (element.className) {
    selector += '.' + element.className.trim().replace(/\s+/g, '.');
  }
  let sib = element, nth = 1;
  while (sib = sib.previousElementSibling) {
    if (sib.nodeName.toLowerCase() === element.nodeName.toLowerCase()) {
      nth++;
    }
  }
  if (nth != 1) {
    selector += `:nth-of-type(${nth})`;
  }
  return selector;
}

function selectElement() {
  return new Promise((resolve) => {
    function addHighlight(event) {
      event.stopPropagation();
      event.preventDefault();
      const blockElement = event.target.closest('.block');
      if (!blockElement || !blockElement.classList) {
        return;
      }
      blockElement.classList.add('highlight');
    }
    
    function removeHighlight(event) {
      event.stopPropagation();
      event.preventDefault();
      const blockElement = event.target.closest('.block');
      if (!blockElement || !blockElement.classList) {
        return;
      }
      blockElement.classList.remove('highlight');
    }
    
    function handleSelection(event) {
      event.stopPropagation();
      event.preventDefault();
      const blockElement = event.target.closest('.block');
      if (!blockElement) {
        return;
      }
      removeEventListeners();
      document.querySelector('.highlight')?.classList.remove('highlight');
      resolve(blockElement);
    }
    
    function cancelSelection(event) {
      if (event.key === 'Escape') {
        removeEventListeners();
        document.querySelector('.highlight')?.classList.remove('highlight');
        resolve(null);
      }
    }
    
    function removeEventListeners() {
      document.removeEventListener('mouseover', addHighlight, true);
      document.removeEventListener('mouseout', removeHighlight, true);
      document.removeEventListener('click', handleSelection, true);
      document.removeEventListener('keydown', cancelSelection, true);
    }
    
    document.addEventListener('mouseover', addHighlight, true);
    document.addEventListener('mouseout', removeHighlight, true);
    document.addEventListener('click', handleSelection, true);
    document.addEventListener('keydown', cancelSelection, true);
  });
}

@customElement('mystique-overlay')
export class MystiqueOverlay extends LitElement {

  static styles = css`
    .container {
      display: flex;
      flex-direction: row;
      gap: 20px;
      align-items: end;
      transform: translate(-50%, 0);
      width: 80%;
      position: fixed;
      bottom: 25px;
      left: 50%;
      z-index: 1000;
      background-color: rgba(255, 255, 255, 0.8);
      box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
      border: 1px solid rgba(0, 0, 0, 0.2);
      border-radius: 5px;
      padding: 10px;
    }
    .left-panel {
      display: flex;
      flex-direction: column;
      align-items: start;
      justify-content: end;
      gap: 10px;
      width: 30%;
    }
    .selected-block {
      display: flex;
      flex-direction: row;
      flex-grow: 1;
      gap: 10px;
    }
    .selected-block div:nth-child(1) {
      display: inline;
      font-weight: bold;
    }
    .selected-block div:nth-child(2) {
      display: inline;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .buttons {
      display: flex;
      flex-direction: row;
      align-items: center;
      justify-content: end;
      gap: 10px;
    }
    .right-panel {
      display: flex;
      flex-direction: column;
      justify-content: end;
      gap: 10px;
      margin-left: 50px;
      width: 100%;
    }
    .status {
      display: flex;
      flex-direction: row;
      align-items: center;
      gap: 10px;
      width: 70%;
    }
    .status[hidden] {
      visibility: hidden;
    }
    .variations {
      display: flex;
      flex-direction: row;
      gap: 10px;
    }
  `;

  @state() accessor selectedElement = null;
  @state() accessor busy = false;
  @state() accessor statusMessage = 'Initializing...';
  @state() accessor variations = [];
  
  async connectedCallback() {
    super.connectedCallback();
    await this.updateVariations();
  }
  
  async updateVariations() {
    const existingVariationsPromises = [];
    for (let i = 0; i < 10; i++) {
      const url = `/generated/style${i}.css`;
      existingVariationsPromises.push(resourceExists(url).then(exists => (exists ? url : null)));
    }
    const existingVariationsResults = await Promise.all(existingVariationsPromises);
    this.variations = existingVariationsResults.filter(url => url !== null);
  }
  
  async select() {
    this.selectedElement = await selectElement();
    console.debug(getCssSelector(this.selectedElement));
  }
  
  reset() {
    this.selectedElement = null;
  }
  
  generate() {
    this.busy = true;
    
    const variationIndex = this.variations.length;
    console.debug(`Generating variation ${variationIndex}...`);
    
    const originalUrl = 'https://main--wknd--hlxsites.hlx.live/';
    const previewUrl = 'http://localhost:3000/';
    const projectDir = '/Users/tsaplin/Work/Sources/mystique-wknd';
    
    const url = 'http://localhost:4000/generate'
      + '?originalUrl=' + encodeURIComponent(originalUrl)
      + '&previewUrl=' + encodeURIComponent(previewUrl)
      + '&projectDir=' + encodeURIComponent(projectDir)
      + '&selector=' + encodeURIComponent(getCssSelector(this.selectedElement))
      + '&variationIndex=' + variationIndex;
    
    const eventSource = new EventSource(url);
    
    eventSource.onmessage = async (event) => {
      this.statusMessage = event.data;
      if(event.data === 'Done.') {
        await this.updateVariations();
        this.busy = false;
        eventSource.close();
      }
      console.debug('Received message:', event.data);
    };
    eventSource.onerror = (error) => {
      console.error('Stream connection failed:', error);
      eventSource.close();
    };
  }
  
  async deleteAllStyles() {
    this.busy = true;
    this.statusMessage = 'Deleting all generated styles...';
    const projectDir = '/Users/tsaplin/Work/Sources/mystique-wknd';
    await wretch('http://localhost:4000/deleteGeneratedStyles?projectDir=' + encodeURIComponent(projectDir)).get().res();
    await this.updateVariations();
    this.statusMessage = 'All generated styles have been deleted.';
    this.busy = false;
  }
  
  toggleStyle(i) {
    this.disableAllStyles();
    const stylesheet = document.createElement('link');
    stylesheet.id = `style${i}`;
    stylesheet.rel = 'stylesheet';
    stylesheet.href = `/generated/style${i}.css`;
    document.head.appendChild(stylesheet);
  }
  
  disableAllStyles() {
    for (let i = 0; i < 10; i++) {
      const stylesheet = document.getElementById(`style${i}`);
      if (stylesheet) {
        document.head.removeChild(stylesheet);
      }
    }
  }
  
  render() {
    return html`
        <sp-theme theme="spectrum" color="light" scale="medium">
          <div class="container">
            <div class="left-panel">
              <div class="selected-block">
                <div>Selected block: </div>
                <div>${this.selectedElement ? getCssSelector(this.selectedElement) : 'none'}</div>
              </div>
              <div class="buttons">
                <sp-button variant="primary" @click=${() => this.select()} ?disabled=${!!this.selectedElement}>Select</sp-button>
                <sp-button variant="primary" @click=${() => this.reset()} ?disabled=${!this.selectedElement}>Reset</sp-button>
              </div>
            </div>
            <div class="right-panel">
              <div class="status" ?hidden=${!this.busy}>
                <sp-progress-circle
                        label="Generating..."
                        indeterminate
                        size="s">
                </sp-progress-circle>
                <div>${this.statusMessage}</div>
              </div>
              <div class="variations">
                <sp-button variant="primary" @click=${() => this.generate()} ?disabled=${!this.selectedElement || this.busy}>Generate</sp-button>
                ${this.variations.map((url, i) => html`
                  <sp-button variant="cta" @click=${() => this.toggleStyle(i)}>Variation ${i}</sp-button>
                `)}
                <sp-button variant="cta" @click=${() => this.disableAllStyles()}>Original</sp-button>
                <sp-button variant="secondary" @click=${() => this.updateVariations()}>Refresh</sp-button>
                <sp-button variant="negative" @click=${() => this.deleteAllStyles()} ?disabled=${this.busy}>Delete All</sp-button>
              </div>
          </div>
        </sp-theme>
    `;
  }
}
