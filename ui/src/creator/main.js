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
import '@spectrum-web-components/tabs/sp-tabs.js';
import '@spectrum-web-components/tabs/sp-tab.js';

import './pipeline-editor.js';

import logo from './logo.png';
import dropzoneIcon from './dropzone-icon.svg';

const DEFAULT_INTENT = [
  'I plan to create a landing page for my new business to effectively promote a new service offering.',
  'The primary goals of this page are to engage visitors, highlight the service’s key benefits, and strategically capture leads for future follow-up.'
].join('\n');

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
    .tabs-container {
      width: 100%;
      display: flex;
      justify-content: center;
    }

    .tab-content {
      display: none;
      width: 100%;
    }

    .tab-content.active {
      display: block;
    }
    .hidden-element {
      display: none !important;
    }
    .main-container {
      display: flex;
      flex-direction: column;
      align-items: start;
      margin: 0 auto;
      width: 60%;
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
    .footer {
      display: flex;
      justify-content: center;
      align-items: center;
      padding: 20px;
      background-color: #f0f0f0;
      border-top: 1px solid #ccc
    }
    .footer sp-link {
      font-size: 14px;
      color: #666;
    }
    .section-title {
      font-size: 22px;
      font-weight: bold;
      margin-top: 20px;
    }
    .section-description {
      font-size: 14px;
      color: #666;
      margin-top: -5px;
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
    .upload-container {
      margin-top: 5px;
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
      display: flex;
      flex-direction: column;
      gap: 10px;
    }
    .results-container .status-list {
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
      padding: 25px;
      margin-bottom: 10px;
    }
    .buttons-container sp-button {
      width: 150px;
    }
    
    .generated-pages-list {
      display: grid;
      width: 100%;
      grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
      gap: 20px;
      padding: 20px 0;
    }
    
    .generated-page-item {
      background: white;
      border: 1px solid #ddd;
      border-radius: 8px;
      overflow: hidden;
      display: flex;
      height: 300px;
      flex-direction: column;
      position: relative;
    }

    .generated-page-item .buttons {
      display: flex;
      flex-direction: row;
      padding: 10px;
      justify-content: end;
      background: rgba(0, 0, 0, 0.1);
      position: absolute;
      width: 100%;
      bottom: 0;
      gap: 10px;
    }
    
    iframe {
      width: 100%;
      height: 100%;
      border: none;
    }

    .no-history-message {
      padding: 20px;
      text-align: center;
      color: #666;
    }

    pipeline-editor {
      margin: 15px 0;
    }
  `;
  
  @state() accessor files = [];
  @state() accessor websiteUrl = '';
  @state() accessor recipe = '';
  @state() accessor recipeOptions = [];
  @state() accessor intent = DEFAULT_INTENT;
  @state() accessor messages = [];
  @state() accessor jobId = '';
  @state() accessor status = null;
  @state() accessor activeTab = 'new-page';
  @state() accessor generatedPages = [];
  
  connectedCallback() {
    super.connectedCallback();
    this.fetchRecipes();
    this.fetchGeneratedPages();
  }
  
  setActiveTab(tab) {
    this.activeTab = tab;
  }
  
  fetchRecipes() {
    wretch('http://localhost:4003/recipes')
      .get()
      .json()
      .then((recipes) => {
        this.recipeOptions = recipes;
        if (recipes.length > 0) {
          this.recipe = recipes[0].id;
        }
      });
  }
  
  fetchGeneratedPages() {
    wretch('http://localhost:4003/generated')
      .get()
      .json()
      .then((pages) => {
        this.generatedPages = pages;
      })
      .catch((error) => {
        console.error('Error fetching generated pages:', error);
      });
  }
  
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
    const selectedRecipeName = event.target.value;
    const selectedRecipe = this.recipeOptions.find(recipe => recipe.name === selectedRecipeName);
    this.recipe = selectedRecipe ? selectedRecipe.id : '';
  }
  
  handleUrlChange(event) {
    this.websiteUrl = event.target.value;
  }
  
  isGenerateDisabled() {
    return this.files.length === 0 || !this.websiteUrl || this.status === 'processing' || this.recipe === '';
  }
  
  getRecipeName() {
    const selectedRecipe = this.recipeOptions.find(recipe => recipe.id === this.recipe);
    return selectedRecipe ? selectedRecipe.name : '';
  }
  
  async generate() {
    this.messages = [];
    this.status = null;
    
    if (this.files.length === 0 && !this.websiteUrl) {
      this.addMessage('No files or URL to process.');
      return;
    }
    
    this.addMessage('Uploading data...');
    const formData = new FormData();
    this.files.forEach(file => formData.append('files', file));
    formData.append('intent', this.intent);
    formData.append('websiteUrl', this.websiteUrl);
    formData.append('recipe', this.recipe);
    
    try {
      const result = await wretch('http://localhost:4003/generate')
        .body(formData)
        .post()
        .json();
      console.log(result);
      this.jobId = result.job_id;
      this.checkJobStatus(result.job_id);
      this.scrollToBottomPage();
    } catch (error) {
      console.error('Error uploading data:', error);
      this.addMessage('Error uploading data.');
    }
  }
  
  clearFileInput() {
    const fileInput = this.shadowRoot.querySelector('input[type="file"]');
    fileInput.value = '';
  }
  
  checkJobStatus(job_id) {
    this.addMessage('Waiting for job to start...');
    const eventSource = new EventSource(`http://localhost:4003/status/${job_id}`);
    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log('Job update:', data);
      for (const update of data.updates) {
        if (update.message) {
          this.addMessage(update.message);
        }
      }
      if (data.status === 'completed') {
        this.addMessage('Job completed successfully!');
        this.status = 'completed';
      } else if (data.status === 'error') {
        this.addMessage('Job failed with an error!');
        this.status = 'error';
      } else {
        this.status = 'processing';
      }
      if (data.status === 'completed' || data.status === 'error') {
        eventSource.close();
      }
    };
  }
  
  addMessage(message) {
    this.messages = [...this.messages, message];
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
  
  previewMarkup(jobId) {
    window.open(`http://localhost:4003/preview/${jobId}`, '_blank');
  }
  
  deletePage(pageId) {
    wretch(`http://localhost:4003/delete-generated/${pageId}`)
      .delete()
      .json()
      .then(() => {
        this.fetchGeneratedPages();
      })
      .catch((error) => {
        console.error('Error deleting generated page:', error);
      });
  }
  
  renderNewPageGeneration() {
    return html`
      <div class="tab-content ${this.activeTab === 'new-page' ? 'active' : ''}">
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
        <div class="inputs-container">
          <div class="section-title">Step 4: Choose the Cooking Recipe</div>
          <div class="section-description">Select the recipe that best suits your needs. Each recipe will generate a different layout and content structure for your landing page.</div>
          <sp-combobox placeholder="Select a recipe" .value=${this.getRecipeName()} @change="${this.handleRecipeChange}">
            ${this.recipeOptions.map((recipe) => html`
              <sp-menu-item value="${recipe.name}">${recipe.name}</sp-menu-item>
            `)}
          </sp-combobox>
        </div>
        <div class="results-container ${this.status === null ? 'hidden-element' : ''}">
          <div class="section-title">Relax and Wait for the Magic to Happen</div>
          <div class="section-description">Monitor the progress of your job and preview the generated markup for your new landing page.</div>
          <div class="status-list">
            ${this.messages.map((status, index) => html`
              <div class="status-item">
                ${(this.status && (this.status !== 'completed' && this.status !== 'error') && index === this.messages.length - 1) ? html`
                  <sp-progress-circle indeterminate size="s"></sp-progress-circle>
                ` : ''}
                ${status}
              </div>
            `)}
          </div>
        </div>
        <div class="buttons-container">
          <sp-button variant="primary" size="L" @click="${this.generate}" ?disabled="${this.isGenerateDisabled()}">Generate</sp-button>
          <sp-button variant="accent" size="L" @click="${() => this.previewMarkup(this.jobId)}" ?disabled="${this.status !== 'completed'}">Preview</sp-button>
        </div>
      </div>
    `;
  }
  
  renderHistoryTab() {
    return html`
      <div class="tab-content ${this.activeTab === 'history' ? 'active' : ''}">
        <div class="inputs-container">
          <div class="section-title">Generated Pages</div>
          <div class="section-description">View a list of all the web pages that have been generated using the Mystique Web Creator.</div>
          ${this.generatedPages.length > 0 ? html`
            <div class="generated-pages-list">
              ${this.generatedPages.map((page) => html`
                <div class="generated-page-item">
                  <iframe src="http://localhost:4003/preview/${page}" width="100%" scrolling="no"></iframe>
                  <div class="buttons">
                    <sp-button variant="accent" size="S" @click="${() => this.previewMarkup(page)}">Preview</sp-button>
                    <sp-button variant="negative" size="S" @click="${() => this.deletePage(page)}">Delete</sp-button>
                  </div>
                </div>
              `)}
            </div>
          ` : html`
            <div class="no-history-message">
              No generated pages found. Start by generating a new page!
            </div>
          `}
        </div>
      </div>
    `;
  }
  
  renderPipelinesTab() {
    return html`
      <div class="tab-content ${this.activeTab === 'pipeline-editor' ? 'active' : ''}">
        <div class="inputs-container">
          <div class="section-title">Generative Pipelines</div>
          <div class="section-description">Define the pipeline for generating web pages from uploaded documents.</div>
          <pipeline-editor></pipeline-editor>
        </div>
      </div>
    `;
  }
  
  render() {
    return html`
      <sp-theme theme="spectrum" color="light" scale="medium">
        <div class="main-container">
          <div class="header">
            <img src="${logo}" alt="Logo" height="200">
            <div class="title">Mystique <strong>Web Creator</strong></div>
            <div class="subtitle">Instantly convert <strong>your ideas</strong> into fully-fledged <strong>web pages</strong></div>
          </div>
          <div class="tabs-container">
            <sp-tabs selected="${this.activeTab}">
              <sp-tab label="Generate" value="new-page" @click="${() => this.setActiveTab('new-page')}"></sp-tab>
              <sp-tab label="Generated Pages" value="history" @click="${() => this.setActiveTab('history')}"></sp-tab>
              <sp-tab label="Pipelines" value="pipeline-editor" @click="${() => this.setActiveTab('pipeline-editor')}"></sp-tab>
            </sp-tabs>
          </div>
          ${this.renderNewPageGeneration()}
          ${this.renderHistoryTab()}
          ${this.renderPipelinesTab()}
        </div>
        <div class="footer">
          <sp-link href="https://www.adobe.com" target="_blank">Powered by Adobe</sp-link>
        </div>
      </sp-theme>
    `;
  }
}

export { MyFirstComponent };
