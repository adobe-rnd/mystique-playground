import {LitElement, html, css} from 'lit';
import {customElement, state} from 'lit/decorators.js';
import wretch from 'wretch';

import '@spectrum-web-components/theme/sp-theme.js';
import '@spectrum-web-components/theme/src/themes.js';

import '@spectrum-web-components/field-label/sp-field-label.js';
import '@spectrum-web-components/button/sp-button.js';
import '@spectrum-web-components/progress-circle/sp-progress-circle.js';
import '@spectrum-web-components/combobox/sp-combobox.js';
import '@spectrum-web-components/textfield/sp-textfield.js';

import './toolbox.css';
import {selectElement} from './selection';
import {generateCssSelector} from './dom';

function getUniqueCategories(strategies) {
  return strategies.reduce((acc, strategy) => {
    if (!acc.includes(strategy.category)) {
      acc.push(strategy.category);
    }
    return acc;
  }, []);
}

@customElement('mystique-overlay')
export class MystiqueOverlay extends LitElement {
  
  static styles = css`
    .container {
      display: flex;
      flex-direction: column;
      gap: 10px;
      align-items: start;
      transform: translate(-50%, 0);
      width: 100%;
      max-width: 800px;
      position: fixed;
      bottom: 25px;
      left: 50%;
      z-index: 1000;
      background-color: rgba(255, 255, 255, 1);
      box-shadow: 0 0 10px 10px rgba(0, 0, 0, 0.1);
      border: 1px solid rgba(0, 0, 0, 0.3);
      border-radius: 5px;
      padding: 20px;
    }

    .block-selection-panel {
      display: flex;
      flex-direction: row;
      align-items: end;
      gap: 10px;
      width: 100%;
    }

    .block-selection-panel sp-textfield {
      display: inline-block;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .form-panel {
      display: flex;
      flex-direction: column;
      justify-content: end;
      gap: 10px;
      width: 100%;
    }

    .field-container {
      display: flex;
      flex-direction: column;
    }

    sp-button {
      width: 100px;
    }
    
    sp-combobox {
      width: 100%;
    }
    
    sp-progress-circle[hidden] {
      display: none;
    }
    
    .status {
      display: flex;
      flex-direction: row;
      align-items: center;
      gap: 10px;
      width: 100%;
    }

    .status div:nth-child(1) {
      display: inline;
      font-weight: bold;
      flex-shrink: 0;
    }

    .status .status-message {
      display: inline-block;
      white-space: nowrap;
      overflow: hidden;
      width: 70%;
      text-overflow: ellipsis;
    }

    .generation-controls {
      display: flex;
      flex-direction: row;
      align-items: center;
      gap: 10px;
    }
  `;

  @state() accessor strategies = [];
  @state() accessor selectedCategory = null;
  @state() accessor selectedStrategy = null;
  
  @state() accessor selectedElement = null;
  @state() accessor prompt = '';
  
  @state() accessor busy = false;
  @state() accessor statusMessage = 'Ready!';
  
  async connectedCallback() {
    super.connectedCallback();
    await this.fetchStrategies();
  }
  
  async fetchStrategies() {
    this.strategies = await wretch('http://localhost:4000/getStrategies').get().json();
    if (this.strategies.length === 0) {
      console.error('No strategies found.');
      return;
    }
    if (getUniqueCategories(this.strategies).includes('Stable')) {
      this.selectedCategory = 'Stable';
    }
    console.debug('Strategies:', this.strategies);
  }
  
  getStrategiesByCategory(category) {
    return this.strategies.filter(strategy => strategy.category === category);
  }
  
  selectCategory(event) {
    this.selectedCategory = event.target.value;
    this.selectedStrategy = null;
    console.debug('Selected category:', this.selectedCategory);
  }
  
  selectStrategy(event) {
    this.selectedStrategy = event.target.value;
    console.debug('Selected strategy:', this.selectedStrategy);
  }
  
  setPrompt(event) {
    this.prompt = event.target.value;
  }
  
  async selectBlock() {
    this.style.display = 'none';
    this.selectedElement = await selectElement();
    this.style.display = null;
    console.debug(generateCssSelector(this.selectedElement));
  }
  
  isGenerateEnabled() {
    return this.selectedElement && this.selectedStrategy;
  }
  
  generate() {
    this.busy = true;

    const selectedStrategyId = this.strategies.find(strategy => strategy.name === this.selectedStrategy).id;
    
    const url = 'http://localhost:4000/generate' +
      '?url=' + encodeURIComponent(window.location.href) +
      '&prompt=' + encodeURIComponent(this.prompt) +
      '&selector=' + encodeURIComponent(generateCssSelector(this.selectedElement)) +
      '&strategy=' + selectedStrategyId;
    
    const eventSource = new EventSource(url);
    
    eventSource.onmessage = async (event) => {
      const { action, payload } = JSON.parse(event.data);
      console.debug('Received message:', action, payload);
      switch (action) {
        case 'done':
          this.statusMessage = 'Success!';
          this.busy = false;
          eventSource.close();
          window.open('http://localhost:4000?variationId=' + payload + '&t=' + Date.now(), '_blank');
          break;
        case 'error':
          console.error('Received message:', payload);
          this.statusMessage = 'Error: ' + payload;
          this.busy = false;
          eventSource.close();
          break;
        case 'progress':
          this.statusMessage = payload;
          break;
        default:
          console.error('Unknown action:', action);
      }
    };

    eventSource.onerror = (error) => {
      console.error('Stream connection failed:', error);
      eventSource.close();
    };
  }
  
  render() {
    return html`
        <sp-theme theme="spectrum" color="light" scale="medium">
          <div class="container">
            <div class="block-selection-panel">
              <div class="field-container" style="flex-grow: 1">
                <sp-field-label>Selected element</sp-field-label>
                <sp-textfield .value=${this.selectedElement ? generateCssSelector(this.selectedElement) : ''} style="width: 100%"></sp-textfield>
              </div>
              <sp-button variant="primary" @click=${() => this.selectBlock()} ?disabled=${this.busy}>Select</sp-button>
            </div>
            <div class="form-panel">
              <div class="generation-controls">
                <div style="display: flex; flex-grow: 1; flex-direction: column; gap: 10px">
                  <div style="display: flex; flex-direction: row; gap: 10px; align-items: end">
                    <div class="field-container" style="width: 200px; flex: 0 0 auto">
                      <sp-field-label>Category</sp-field-label>
                      <sp-combobox value=${this.selectedCategory} @change=${this.selectCategory}>
                        ${getUniqueCategories(this.strategies).map(category => html`
                          <sp-menu-item value="${category}">${category}</sp-menu-item>
                        `)}
                      </sp-combobox>
                    </div>
                    <div class="field-container" style="flex-grow: 1">
                      <sp-field-label>Strategy</sp-field-label>
                      <sp-combobox value=${this.selectedStrategy} @change=${this.selectStrategy}>
                        ${this.getStrategiesByCategory(this.selectedCategory).map(strategy => html`
                          <sp-menu-item value="${strategy.id}">${strategy.name}</sp-menu-item>
                        `)}
                      </sp-combobox>
                    </div>
                    <sp-button variant="primary" ?pending=${this.busy} @click=${this.generate} ?disabled=${!this.isGenerateEnabled()}>Generate</sp-button>
                  </div>
                  <div class="field-container" style="flex-grow: 1">
                    <sp-field-label>Prompt</sp-field-label>
                    <sp-textfield
                        placeholder="Optional prompt for the AI model"
                        multiline
                        rows="3"
                        style="width: 100%"
                        @input=${this.setPrompt}
                        .value=${this.prompt}
                    ></sp-textfield>
                  </div>
                </div>
              </div>
            </div>
            <div class="status">
              <div>Status:</div>
              <div class="status-message">${this.statusMessage}</div>
            </div>
          </div>
        </sp-theme>
    `;
  }
}
