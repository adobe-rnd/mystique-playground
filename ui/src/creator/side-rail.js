import {css, html, LitElement} from 'lit';
import {customElement, state} from 'lit/decorators.js';
import {fetchStepsData} from './pipeline-client';

@customElement('side-rail')
class SideRail extends LitElement {
  static styles = css`
    .side-rail {
      width: 100%;
      height: 100%;
      background-color: #f3f3f3;
      border-bottom: 1px solid #ccc;
      display: flex;
      flex-direction: column;
    }
    .tabs {
      display: flex;
      border-bottom: 1px solid #ddd;
    }
    .tab {
      padding: 10px;
      cursor: pointer;
      border-right: 1px solid #ddd;
      flex: 1;
      text-align: center;
    }
    .tab:last-child {
      border-right: none;
    }
    .tab.active {
      background-color: #e0e0e0;
      font-weight: bold;
    }
    .tab-content {
      flex-grow: 1;
      padding: 10px;
      overflow-y: auto;
    }
    .step {
      padding: 8px;
      margin: 5px 0;
      background-color: white;
      border: 1px solid #ccc;
      cursor: grab;
    }
  `;
  
  @state() accessor activeTab = 'create';
  @state() accessor steps = [];
  @state() accessor isLoading = true;
  @state() accessor error = '';
  
  // Fetch data when the component is first updated
  async firstUpdated() {
    this.fetchSteps();
  }
  
  async fetchSteps() {
    this.isLoading = true; // Start loading state
    this.error = ''; // Clear any previous error
    
    try {
      this.steps = await fetchStepsData(); // Update the state with fetched data
    } catch (error) {
      console.error('Error fetching steps:', error);
      this.error = 'Failed to load steps data'; // Set an error message
    } finally {
      this.isLoading = false; // Stop loading state
    }
  }
  
  handleTabChange(tab) {
    this.activeTab = tab;
  }
  
  handleDragStart(event, step) {
    event.dataTransfer.setData('step-id', step.id);
  }
  
  render() {
    return html`
      <div class="side-rail">
        <div class="tabs">
          <div class="tab ${this.activeTab === 'create' ? 'active' : ''}" @click=${() => this.handleTabChange('create')}>
            Create
          </div>
          <div class="tab ${this.activeTab === 'properties' ? 'active' : ''}" @click=${() => this.handleTabChange('properties')}>
            Properties
          </div>
        </div>
        <div class="tab-content">
          ${this.isLoading ? html`<div>Loading steps...</div>` : this.renderTabContent()}
          ${this.error ? html`<div class="error">${this.error}</div>` : ''}
        </div>
      </div>
    `;
  }
  
  renderTabContent() {
    switch (this.activeTab) {
      case 'create':
        return html`
          ${this.steps.map(
            (step) => html`
              <div class="step" draggable="true" @dragstart=${(e) => this.handleDragStart(e, step)}>
                ${step.name}
              </div>
            `
          )}
        `;
      case 'properties':
        return html`<div>No properties available for the selected pipeline.</div>`;
      default:
        return html`<div>Select a tab to view its content.</div>`;
    }
  }
}
