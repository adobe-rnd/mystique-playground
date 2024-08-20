import { LitElement, html, css } from 'lit';
import { customElement, state } from 'lit/decorators.js';
import wretch from 'wretch';

import '@spectrum-web-components/theme/sp-theme.js';
import '@spectrum-web-components/theme/src/themes.js';
import '@spectrum-web-components/textfield/sp-textfield.js';
import '@spectrum-web-components/combobox/sp-combobox.js';
import '@spectrum-web-components/field-label/sp-field-label.js';
import '@spectrum-web-components/button/sp-button.js';
import '@spectrum-web-components/dropzone/sp-dropzone.js';
import '@spectrum-web-components/link/sp-link.js';
import '@spectrum-web-components/illustrated-message/sp-illustrated-message.js';
import '@spectrum-web-components/progress-circle/sp-progress-circle.js';

import logo from './logo.png';
import dropzoneIcon from './dropzone-icon.svg';

const DEFAULT_INTENT = [
  'I want to create a landing page for my new business',
  'This page will be used to promote a new service',
  'Also, I want to collect leads from this page'].join('\n');

@customElement('web-creator-component')
class MyFirstComponent extends LitElement {
  
  static styles = css`
    html, body {
      margin: 0;
      padding: 0;
      height: 100%;
      display: flex;
      justify-content: center;
      align-items: center;
      background-color: #f0f0f0;
    }
    * {
      box-sizing: border-box;
    }
    .hidden-element {
      display: none;
    }
    .main-container {
      display: flex;
      flex-direction: column;
      align-items: start;
      margin: 0 auto;
      width: 50%;
      gap: 20px;
    }
    .header {
      display: grid;
      align-items: center;
      grid-template: "logo title" auto
                     "logo subtitle" auto / auto 1fr;
      width: 100%;
      border: 3px solid #f0f0f0;
      border-radius: 8px;
      background: repeating-linear-gradient(
          135deg,
          #fff 0,
          #fff 20px,
          #f0f0f0 40px,
          #f0f0f0 40px
      );
    }
    .header img {
      grid-area: logo;
      width: 150px;
      height: 150px;
    }
    .header .title {
      grid-area: title;
      font-size: 42px;
      font-weight: bold;
      align-self: end;
      text-shadow: -2px -2px 0 #fff, 2px -2px 0 #fff, -2px 2px 0 #fff, 2px 2px 0 #fff;
    }
    .title strong {
      color: #1d9271;
    }
    .header .subtitle {
      grid-area: subtitle;
      font-size: 22px;
      color: #666;
      align-self: start;
      text-shadow: -2px -2px 0 #fff, 2px -2px 0 #fff, -2px 2px 0 #fff, 2px 2px 0 #fff;
    }
    .subtitle strong {
      color: #0e70c0;
      font-size: 26px;
    }
    .section-title {
      font-size: 22px;
      font-weight: bold;
    }
    .section-description {
      font-size: 14px;
      color: #666;
    }
    .documents-container {
      display: flex;
      flex-direction: column;
      gap: 5px;
      width: 100%;
    }
    .documents-container .upload-container {
      display: flex;
      flex-direction: row;
      gap: 5px;
      width: 100%;
    }
    .upload-container sp-dropzone {
      border: 1px dashed #ccc;
      border-radius: 8px;
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      flex: 1;
    }
    .upload-container .file-list {
      display: flex;
      flex-direction: column;
      margin-top: 16px;
      max-width: 50%;
    }
    .file-list .file-item {
      padding: 8px;
      display: flex;
      flex-direction: row;
      align-items: center;
      justify-content: space-between;
      background-color: #f9f9f9;
      margin: 4px 0;
      border-radius: 10px;
      width: 100%;
    }
    .file-item button {
      background-color: #cd3131;
      color: #fff;
      border: none;
      border-radius: 4px;
      padding: 4px 8px;
      cursor: pointer;
      margin-left: 8px;
    }
    .inputs-container {
      display: flex;
      flex-direction: column;
      gap: 10px;
      width: 100%;
    }
    .inputs-container sp-textfield {
      width: 100%;
    }
    .inputs-container sp-combobox {
      width: 100%;
    }
    .inputs-container sp-textfield textarea {
      height: 100px;
    }
    .inputs-container sp-button {
      align-self: center;
      margin-top: 16px;
    }
    .results-container {
      width: 100%;
    }
    .results-container .status-list {
      margin-top: 16px;
      width: 100%;
      height: 120px;
      overflow-y: hidden;
      position: relative;
      padding: 8px;
      border: 1px solid #ccc;
      border-radius: 8px;
    }
    .status-list .status-item {
      display: flex;
      flex-direction: row;
      gap: 2px;
      align-items: center;
      justify-content: flex-start;
      padding: 2px;
    }
    .status-list sp-progress-circle {
      margin: 4px;
    }
    .buttons-container {
      display: flex;
      width: 100%;
      flex-direction: row;
      gap: 10px;
      justify-content: center;
      padding: 10px;
      margin-bottom: 10px;
    }
    .buttons-container sp-button {
      width: 150px;
    }
  `;
  
  @state() accessor files = [];
  @state() accessor websiteUrl = '';
  @state() accessor recipe = 'Standard';
  @state() accessor intent = DEFAULT_INTENT;
  @state() accessor statuses = [];
  @state() accessor jobId = '';
  @state() accessor jobStatus = null;
  
  intentChanged(event) {
    this.intent = event.target.value;
  }
  
  handleFileChange(event) {
    const newFiles = Array.from(event.target.files);
    this.files = [...this.files, ...newFiles];
    this.clearFileInput();
  }
  
  handleDrop(event) {
    event.preventDefault();
    event.stopPropagation();
    const newFiles = Array.from(event.dataTransfer.files);
    this.files = [...this.files, ...newFiles];
    this.removeDragData(event);
  }
  
  handleDragOver(event) {
    event.preventDefault();
    event.stopPropagation();
    event.target.classList.add('dragover');
  }
  
  handleDragLeave(event) {
    event.preventDefault();
    event.stopPropagation();
    event.target.classList.remove('dragover');
  }
  
  removeDragData(event) {
    event.dataTransfer.clearData();
    event.target.classList.remove('dragover');
  }
  
  removeFile(event, index) {
    event.stopPropagation();
    this.files = this.files.filter((_, i) => i !== index);
    this.clearFileInput();
  }
  
  handleRecipeChange(event) {
    this.recipe = event.target.value
  }
  
  handleUrlChange(event) {
    this.websiteUrl = event.target.value;
  }
  
  isGenerateDisabled() {
    return this.files.length === 0 || !this.websiteUrl || this.jobStatus === 'processing';
  }
  
  async generate() {
    this.statuses = [];
    this.jobStatus = null;
    
    if (this.files.length === 0 && !this.websiteUrl) {
      this.addStatus('No files or URL to process.');
      return;
    }
    
    this.addStatus('Uploading data...');
    const formData = new FormData();
    this.files.forEach(file => formData.append('files', file));
    formData.append('intent', this.intent);
    formData.append('websiteUrl', this.websiteUrl);
    
    try {
      const result = await wretch('http://localhost:4003/generate')
        .body(formData)
        .post()
        .json();
      console.log(result);
      this.jobId = result.job_id;
      this.checkJobStatus(result.job_id);
      this.scrollToBottomPage(); // Scroll to bottom when result is revealed
    } catch (error) {
      console.error('Error uploading data:', error);
      this.addStatus('Error uploading data.');
    }
  }
  
  clearFileInput() {
    const fileInput = this.shadowRoot.querySelector('input[type="file"]');
    fileInput.value = '';
  }
  
  checkJobStatus(job_id) {
    this.addStatus('Waiting for job to start...');
    this.jobStatus = 'processing';
    const eventSource = new EventSource(`http://localhost:4003/status/${job_id}`);
    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log('Job update:', data);
      if (data.message) {
        this.addStatus(data.message);
      } else if (data.status === 'completed') {
        this.addStatus('Job completed successfully!');
      } else if (data.status === 'error') {
        this.addStatus('Job failed.');
      }
      if (data.status) {
        this.jobStatus = data.status;
      }
      if (data.status === 'completed' || data.status === 'error') {
        eventSource.close();
      }
    };
  }
  
  addStatus(message) {
    this.statuses = [...this.statuses, message];
    this.scrollToBottom();
  }
  
  scrollToBottom() {
    setTimeout(() => {
      const statusList = this.shadowRoot.querySelector('.status-list');
      statusList.scrollTop = statusList.scrollHeight;
    }, 300);
  }
  
  scrollToBottomPage() {
    setTimeout(() => {
      window.scrollTo(0, document.body.scrollHeight);
    }, 300);
  }
  
  previewMarkup() {
    window.open(`http://localhost:4003/preview/${this.jobId}`, '_blank');
  }
  
  render() {
    console.log('JOB status:', this.jobStatus);
    return html`
      <sp-theme theme="spectrum" color="light" scale="medium">
        <div class="main-container">
          <div class="header">
            <img src="${logo}" alt="Logo" height="200">
            <div class="title">Mystique <strong>Web Creator</strong></div>
            <div class="subtitle">Instantly convert <strong>your ideas</strong> into fully-fledged <strong>web pages</strong></div>
          </div>
          <div class="documents-container">
            <div class="section-title">Step 1: Upload Your Documents</div>
            <div class="section-description">Begin by uploading the documents you wish to use for generating a customized landing page.</div>
            <div class="upload-container">
              <sp-dropzone
                      id="dropzone-1"
                      @dragover=${this.handleDragOver}
                      @dragleave=${this.handleDragLeave}
                      @drop=${this.handleDrop}
              >
                <sp-illustrated-message heading="Drag and Drop Your Files">
                  <img src="${dropzoneIcon}" alt="Dropzone Icon" width="100">
                </sp-illustrated-message>
                <div>
                  <label for="file-input">
                    <sp-link
                            href="javascript:;"
                            onclick="this.parentElement.nextElementSibling.click()"
                    >
                      Select a File
                    </sp-link>
                    from your computer
                  </label>
                  <input type="file" id="file-input" style="display: none" @change=${this.handleFileChange} multiple />
                </div>
              </sp-dropzone>
              <div class="file-list">
                ${this.files.map((file, index) => html`
                  <div class="file-item">
                    ${file.name}
                    <button @click=${(e) => this.removeFile(e, index)}>Remove</button>
                  </div>
                `)}
              </div>
            </div>
          </div>
          <div class="inputs-container">
            <div class="section-title">Step 2: Describe Your Intent</div>
            <div class="section-description">Describe the purpose and goals of your new webpage to help guide the design and content generation process.</div>
            <sp-textfield multiline rows=5 placeholder="Enter your intent" .value=${this.intent} @input="${this.intentChanged}">
              <sp-field-label slot="label">Intent</sp-field-label>
            </sp-textfield>
          </div>
          <div class="inputs-container">
            <div class="section-title">Step 3: Provide a Reference Website URL to Copy the Design</div>
            <div class="section-description">Enter the URL of a website that you would like to emulate. We will use this site as a design reference to create a visually similar landing page.</div>
            <sp-textfield placeholder="Enter website URL" .value=${this.websiteUrl} @input="${this.handleUrlChange}">
              <sp-field-label slot="label">Website URL</sp-field-label>
            </sp-textfield>
          </div>
          <div class="inputs-container" style="display: none">
            <div class="section-title">Step 4: Choose the Cooking Recipe</div>
            <div class="section-description">Select the recipe that best suits your needs. Each recipe will generate a different layout and content structure for your landing page.</div>
            <sp-combobox placeholder="Select a recipe" .value=${this.recipe} @input="${this.handleRecipeChange}">
              <sp-menu-item value="standard">Standard</sp-menu-item>
            </sp-combobox>
          </div>
          <div class="results-container ${this.jobStatus === null ? 'hidden-element' : ''}">
            <div class="section-title">Relax and Wait for the Magic to Happen</div>
            <div class="section-description">Monitor the progress of your job and preview the generated markup for your new landing page.</div>
            <div class="status-list">
              ${this.statuses.map((status, index) => html`
                <div class="status-item">
                  ${(this.jobStatus && (this.jobStatus !== 'completed' && this.jobStatus !== 'error') && index === this.statuses.length - 1) ? html`
                  <sp-progress-circle indeterminate size="s"></sp-progress-circle>
                ` : ''}
                  ${status}
                </div>
              `)}
            </div>
          </div>
          <div class="buttons-container">
            <sp-button variant="primary" size="L" @click="${this.generate}" ?disabled="${this.isGenerateDisabled()}">Generate</sp-button>
            <sp-button variant="accent" size="L" @click="${this.previewMarkup}" ?disabled="${this.jobStatus !== 'completed'}">Preview</sp-button>
          </div>
        </div>
      </sp-theme>
    `;
  }
}

export { MyFirstComponent };
