import { customElement, property } from 'lit/decorators.js';
import { html, LitElement, css } from 'lit';
import { action, observable } from 'mobx';
import '@spectrum-web-components/icon/sp-icon.js';
import { SettingsIcon } from '@spectrum-web-components/icons-workflow';
import localforage from 'localforage';

class AppSettings {
  @observable accessor isDisplayingDebuggingInfo = false;
  @observable accessor isAutoSuggestEnabled = false;
  @observable accessor numberOfWordsToSuggest = 3;
  
  constructor() {
    this.loadSettings();
  }
  
  @action
  async setIsDisplayingDebuggingInfo(value) {
    this.isDisplayingDebuggingInfo = value;
    await this.saveSettings();
  }
  
  @action
  async setIsAutoSuggestEnabled(value) {
    this.isAutoSuggestEnabled = value;
    await this.saveSettings();
  }
  
  @action
  async setNumberOfWordsToSuggest(value) {
    this.numberOfWordsToSuggest = value;
    await this.saveSettings();
  }
  
  async saveSettings() {
    const settings = {
      isDisplayingDebuggingInfo: this.isDisplayingDebuggingInfo,
      isAutoSuggestEnabled: this.isAutoSuggestEnabled,
      numberOfWordsToSuggest: this.numberOfWordsToSuggest,
    };
    await localforage.setItem('appSettings', settings);
  }
  
  async loadSettings() {
    const settings = await localforage.getItem('appSettings');
    if (settings) {
      this.isDisplayingDebuggingInfo = settings.isDisplayingDebuggingInfo;
      this.isAutoSuggestEnabled = settings.isAutoSuggestEnabled;
      this.numberOfWordsToSuggest = settings.numberOfWordsToSuggest;
    }
  }
}

export const appSettings = new AppSettings();

@customElement('settings-button')
export class SettingsButton extends LitElement {
  @property({ type: Boolean }) accessor isOpen = false;
  
  static styles = css`
    .settings-button {
      position: fixed;
      bottom: 16px;
      left: 16px;
      background-color: white;
      color: black;
      border: none;
      border-radius: 50%;
      width: 48px;
      height: 48px;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      box-shadow: 0px 2px 10px rgba(0, 0, 0, 0.3);
      z-index: 1000;
      transition: transform 0.3s, background-color 0.3s;
    }

    .settings-button:hover {
      background-color: #f0f0f0;
    }

    .settings-button:active {
      transform: scale(0.95);
    }

    .settings-button sp-icon {
      color: gray;
    }

    .dialog-container {
      position: fixed;
      bottom: 80px;
      left: 16px;
      background-color: white;
      padding: 16px;
      box-shadow: 0px 2px 10px rgba(0, 0, 0, 0.3);
      border-radius: 8px;
      z-index: 1001;
      display: none;
    }

    .dialog-container.open {
      display: block;
    }

    .dialog-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .dialog-header h2 {
      margin: 0;
      font-size: 14px;
    }

    .close-button {
      background: none;
      border: none;
      font-size: 14px;
      cursor: pointer;
    }

    .dialog-content {
      margin-top: 16px;
    }

    .dialog-content label {
      display: block;
      margin-bottom: 8px;
      font-size: 12px;
    }

    .dialog-content input[type="number"] {
      width: 50px;
      font-size: 12px;
    }

    .dialog-content input[type="checkbox"] {
      margin-right: 8px;
    }
  `;
  
  constructor() {
    super();
    this.togglePopup = this.togglePopup.bind(this);
    this.closePopup = this.closePopup.bind(this);
    this.toggleDisplayingDebuggingInfo = this.toggleDisplayingDebuggingInfo.bind(this);
    this.toggleAutoSuggest = this.toggleAutoSuggest.bind(this);
    this.setNumberOfWordsToSuggest = this.setNumberOfWordsToSuggest.bind(this);
  }
  
  togglePopup() {
    this.isOpen = !this.isOpen;
  }
  
  closePopup() {
    this.isOpen = false;
  }
  
  toggleDisplayingDebuggingInfo(event) {
    appSettings.setIsDisplayingDebuggingInfo(event.target.checked);
  }
  
  toggleAutoSuggest(event) {
    appSettings.setIsAutoSuggestEnabled(event.target.checked);
  }
  
  setNumberOfWordsToSuggest(event) {
    const value = parseInt(event.target.value, 10);
    if (!isNaN(value)) {
      appSettings.setNumberOfWordsToSuggest(value);
    }
  }
  
  render() {
    console.log(`Rendering settings button with isOpen=${this.isOpen}, isDrawingDebuggingInfo=${appSettings.isDisplayingDebuggingInfo}, isAutoSuggestEnabled=${appSettings.isAutoSuggestEnabled}, numberOfWordsToSuggest=${appSettings.numberOfWordsToSuggest}`);
    
    return html`
      <div class="dialog-container ${this.isOpen ? 'open' : ''}">
        <div class="dialog-header">
          <h2>Settings</h2>
          <button class="close-button" @click=${this.closePopup}>&times;</button>
        </div>
        <div class="dialog-content">
          <label>
            <input type="checkbox" @change=${this.toggleDisplayingDebuggingInfo} .checked=${appSettings.isDisplayingDebuggingInfo}>
            Display Debugging Info
          </label>
          <label>
            <input type="checkbox" @change=${this.toggleAutoSuggest} .checked=${appSettings.isAutoSuggestEnabled}>
            Enable Auto-Suggest
          </label>
          <label>
            Number of Words to Suggest
            <input type="number" min="1" .value=${appSettings.numberOfWordsToSuggest} @input=${this.setNumberOfWordsToSuggest}>
          </label>
        </div>
      </div>
      <button class="settings-button" @click=${this.togglePopup}>
        <sp-icon size="m" style="color: gray;">${SettingsIcon()}</sp-icon>
      </button>
    `;
  }
}
