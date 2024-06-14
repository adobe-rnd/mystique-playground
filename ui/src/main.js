import {LitElement, html, css} from 'lit';
import {customElement, state} from 'lit/decorators.js';
import wretch from 'wretch';

import '@spectrum-web-components/theme/sp-theme.js';
import '@spectrum-web-components/theme/src/themes.js';

import '@spectrum-web-components/button/sp-button.js';
import '@spectrum-web-components/progress-circle/sp-progress-circle.js';
import '@spectrum-web-components/combobox/sp-combobox.js';

import './main.css';
import {getCssSelector} from './utils';
import {selectElement} from './selection';

@customElement('mystique-overlay')
export class MystiqueOverlay extends LitElement {
  
  static styles = css`
    .container {
      display: flex;
      flex-direction: row;
      gap: 20px;
      align-items: end;
      transform: translate(-50%, 0);
      width: 70%;
      position: fixed;
      bottom: 25px;
      left: 50%;
      z-index: 1000;
      background-color: rgba(255, 255, 255, 0.8);
      box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
      border: 1px solid rgba(0, 0, 0, 0.3);
      border-radius: 5px;
      padding: 10px;
    }

    .left-panel {
      display: flex;
      flex-direction: column;
      align-items: start;
      justify-content: end;
      gap: 10px;
      width: 40%;
    }

    .selected-block {
      display: flex;
      flex-direction: row;
      flex-grow: 1;
      gap: 10px;
      width: 100%;
      overflow: hidden;
    }

    .selected-block div:nth-child(1) {
      display: inline;
      font-weight: bold;
      flex-shrink: 0;
    }

    .selected-block div:nth-child(2) {
      display: inline-block;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .selection-controls {
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
      width: 60%;
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

    .generation-controls sp-combobox {
      width: 300px;
    }
  `;

  @state() accessor strategies = [];
  @state() accessor selectedStrategy = null;
  
  @state() accessor selectedElement = null;
  
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
    console.debug('Strategies:', this.strategies);
    this.selectedStrategy = this.strategies[0].name;
  }
  
  selectStrategy(event) {
    this.selectedStrategy = event.target.value;
    console.debug('Selected strategy:', this.selectedStrategy);
  }
  
  async select() {
    this.style.display = 'none';
    this.selectedElement = await selectElement();
    this.style.display = null;
    console.debug(getCssSelector(this.selectedElement));
  }
  
  reset() {
    this.selectedElement = null;
  }
  
  generate() {
    this.busy = true;

    const selectedStrategyId = this.strategies.find(strategy => strategy.name === this.selectedStrategy).id;
    
    const url = 'http://localhost:4000/generate' +
      '?selector=' + encodeURIComponent(getCssSelector(this.selectedElement)) +
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
          window.open('http://localhost:4001?variationId=' + payload + '&cacheBuster=' + Date.now(), '_blank');
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
            <div class="left-panel">
              <div class="selected-block">
                <div>Selected block: </div>
                <div>${this.selectedElement ? getCssSelector(this.selectedElement) : 'none'}</div>
              </div>
              <div class="selection-controls">
                <sp-button variant="primary" @click=${() => this.select()} ?disabled=${!!this.selectedElement}>Select</sp-button>
                <sp-button variant="primary" @click=${() => this.reset()} ?disabled=${!this.selectedElement}>Reset</sp-button>
              </div>
            </div>
            <div class="right-panel">
              <div class="status">
                <div>Status:</div>
                <sp-progress-circle label="Generating..." indeterminate size="s" ?hidden=${!this.busy}></sp-progress-circle>
                <div class="status-message">${this.statusMessage}</div>
              </div>
              <div class="generation-controls">
                <sp-button variant="primary" @click=${() => this.generate()} ?disabled=${!this.selectedElement || !this.selectedStrategy || this.busy}>Generate</sp-button>
                <sp-combobox value=${this.selectedStrategy} @change=${this.selectStrategy}>
                  ${this.strategies.map(strategy => html`
                    <sp-menu-item value="${strategy.id}">${strategy.name}</sp-menu-item>
                  `)}
                </sp-picker>
              </div>
          </div>
        </sp-theme>
    `;
  }
}
