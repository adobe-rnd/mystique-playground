import { customElement, state } from 'lit/decorators.js';
import { css, html, LitElement } from 'lit';
import { animate } from '@lit-labs/motion';
import {
  captureScreenshot,
  getIntersectedElements,
  getSmallestEnclosingElement
} from '../utils';
import wretch from 'wretch';
import { throttle } from 'lodash';
import '@spectrum-web-components/action-button/sp-action-button.js';
import '@spectrum-web-components/button/sp-button.js';
import '@spectrum-web-components/textfield/sp-textfield.js';
import '@spectrum-web-components/icon/sp-icon.js';
import { RevertIcon, MagicWandIcon, CopyIcon, CloseIcon } from '@spectrum-web-components/icons-workflow';
import { undoManager } from './undo';
import { authoringSession } from './session';
import { MobxLitElement } from '@adobe/lit-mobx';
import { appSettings } from './settings';
import { reaction } from 'mobx';
import {generateCssSelector, getElementHtml} from '../dom';

function getSuggestedPrompt(prompt, suggestion, numberOfWords) {
  const suggestions = suggestion ? suggestion.split(' ').slice(0, numberOfWords) : [];
  const trimmedPrompt = prompt.trim();
  return suggestions.length > 0 && prompt.endsWith(' ')
    ? `${trimmedPrompt} ${suggestions.join(' ')}`.trim()
    : '';
}

async function fetchSuggestion(prompt) {
  if (/\w+\s/.test(prompt)) {
    const url = 'http://localhost:4001/autocomplete';
    try {
      const response = await wretch(url)
        .post({ prompt })
        .json();
      return response.suggestion;
    } catch (error) {
      console.error('Error fetching suggestion:', error);
      return '';
    }
  }
  return '';
}

@customElement('prompt-component')
export class PromptComponent extends MobxLitElement {
  
  static styles = css`
    .prompt-dialog-container {
      display: flex;
      flex-direction: column;
      align-items: center;
      position: fixed;
      top: calc(50% - 200px);
      left: 50%;
      transform: translateX(-50%);
      z-index: 2000;
      padding: 20px;
      background-color: white;
      border-radius: 12px;
      box-shadow: 0 0 5px 5px rgba(0, 0, 0, 0.2);
      font-size: 1rem;
      font-family: 'Adobe Clean', 'Helvetica Neue', sans-serif;
    }

    .header {
      display: flex;
      flex-direction: row;
      justify-content: space-between;
      align-items: center;
      width: 100%;
      margin-bottom: 10px;
    }

    .header h2 {
      margin: 0;
      font-size: 1.2rem;
      font-weight: bold;
    }

    .prompt-container {
      display: flex;
      align-items: center;
      position: relative;
      flex: 1;
    }

    .prompt-container sp-textfield {
      border-radius: 4px;
      width: 550px;
      color: black;
      resize: none;
    }

    .suggestion {
      position: absolute;
      top: 1px;
      left: 1px;
      padding: 5px 11px;
      pointer-events: none;
      white-space: pre-wrap;
      font-family: monospace;
      color: rgba(0, 0, 0, 0.3);
      font-size: 0.8rem;
    }

    .balloon-container {
      display: flex;
      flex-direction: column;
      flex-wrap: wrap;
      justify-content: center;
      margin: 5px 0 20px 0;
      transition: all 0.3s ease;
    }

    .balloon {
      background-color: #ededed;
      color: black;
      border-radius: 10px;
      padding: 10px 15px;
      margin: 5px;
      font-size: 0.8rem;
      width: 500px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      transition: all 0.3s ease-in-out;
    }

    .balloon.label {
      background-color: white;
      cursor: pointer;
      padding: 5px 10px;
    }

    .balloon:not(.label):hover {
      background-color: #dddddd;
    }

    .balloon-text {
      flex-grow: 1;
      font-size: 1rem;
    }

    .button-container {
      display: flex;
      flex-direction: row;
      justify-content: space-between;
      margin-top: 20px;
      width: 100%;
      flex: 1;
    }

    sp-button.apply {
      justify-self: flex-end;
    }

    sp-button.copy {
      align-self: flex-end;
      justify-self: end;
    }

    sp-button.undo {
      justify-self: flex-start;
    }

    @keyframes rotate {
      0% {
        transform: rotate(0deg);
      }
      100% {
        transform: rotate(360deg);
      }
    }
  `;
  
  @state() accessor prompt = '';
  @state() accessor suggestion = '';
  @state() accessor isApplying = false;
  @state() accessor promptIdeas = [];
  @state() accessor isFetchingIdeas = false;
  
  constructor() {
    super();
    this.setupReactions();
  }
  
  setupReactions() {
    reaction(
      () => authoringSession.selectedRegions,
      this.handleSelectedRegionsChange.bind(this)
    );
  }
  
  async handleSelectedRegionsChange(selectedRegions) {
    console.log('Selected regions:', selectedRegions);
    
    if (selectedRegions.length === 0) {
      this.promptIdeas = [];
      return;
    }
    
    const selectedElements = getIntersectedElements(selectedRegions);
    if (selectedElements.length === 0) {
      this.promptIdeas = [];
      return;
    }
    
    const enclosingElement = getSmallestEnclosingElement(selectedElements);
    if (!enclosingElement) {
      this.promptIdeas = [];
      return;
    }
    
    const contextHtml = await getElementHtml(enclosingElement, false);
    
    this.isFetchingIdeas = true;
    try {
      const selector = generateCssSelector(enclosingElement);
      console.log(`Fetching suggestions for element with selector: ${selector}`);
      
      const data = await wretch('http://localhost:4001/suggest-prompts')
        .post({ context: contextHtml })
        .json();
      this.promptIdeas = data.suggestions;
      console.log('Prompt ideas:', this.promptIdeas);
    } catch (error) {
      console.error('Error fetching suggestions:', error);
    } finally {
      this.isFetchingIdeas = false;
    }
  }
  
  async handleApplyPrompt() {
    this.isApplying = true;
    this.suggestion = '';
    
    try {
      const intersectedElements = getIntersectedElements(authoringSession.selectedRegions);
      const enclosingElement = getSmallestEnclosingElement(intersectedElements);
      
      const originalHtml = enclosingElement.outerHTML;
      
      const contextHtml = await getElementHtml(enclosingElement, appSettings.isAddingInlinedStylesEnabled);
      console.log('Context HTML:', contextHtml);
      const selectionHtmls = await Promise.all(
        intersectedElements.map(element => getElementHtml(element, appSettings.isAddingInlinedStylesEnabled))
      );
      // selectionHtmls.forEach((html, index) => console.log(`Selection ${index} HTML:`, html));
      
      const screenshotUint8Array = await captureScreenshot(enclosingElement);
      
      const blob = new Blob([screenshotUint8Array], { type: 'image/png' });
      const screenshotDataUrl = await new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onloadend = () => resolve(reader.result);
        reader.onerror = reject;
        reader.readAsDataURL(blob);
      });
      
      console.log('Prompt:', authoringSession.prompt);
      console.log('Context HTML:', contextHtml.length);
      console.log('Selection HTML:', selectionHtmls.map(html => html.length).join(', '));
      console.log('Screenshot size:', screenshotUint8Array.length);
      
      const response = await wretch('http://localhost:4001/copilot')
        .post({
          context: contextHtml,
          selection: selectionHtmls,
          prompt: authoringSession.prompt,
          screenshot: appSettings.isSendingScreenshotsEnabled ? screenshotDataUrl : null
        })
        .json();
      
      this.replaceElementWithNewContent(response.html, enclosingElement, originalHtml);
    } catch (error) {
      console.error('Error during handleApplyPrompt:', error);
    } finally {
      this.isApplying = false;
      this.requestUpdate();
    }
  }
  
  replaceElementWithNewContent(receivedHtml, enclosingElement, originalHtml) {
    const selector = generateCssSelector(enclosingElement);
    const elementToReplace = document.querySelector(selector);
    
    if (elementToReplace && !['body', 'html'].includes(elementToReplace.tagName.toLowerCase())) {
      
      undoManager.addEntry(
        `document.querySelector('${selector}').outerHTML = \`${originalHtml}\`;`,
        `document.querySelector('${selector}').outerHTML = \`${receivedHtml}\`;`,
        authoringSession.prompt,
        authoringSession.selectedRegions
      );
      
      elementToReplace.outerHTML = receivedHtml;
      authoringSession.setPrompt('');
      authoringSession.setSelectedRegions([]);
      this.suggestion = '';

    } else {
      console.error('Could not generate a unique selector for the element');
    }
  }
  
  throttledFetchSuggestion = throttle(async (prompt) => {
    this.suggestion = await fetchSuggestion(prompt);
  }, 300);
  
  handleInputChange(event) {
    authoringSession.setPrompt(event.target.value);
    this.suggestion = '';
    if (appSettings.isAutoSuggestEnabled) {
      this.throttledFetchSuggestion(authoringSession.prompt);
    }
  }
  
  handleKeyDown(event) {
    const textarea = event.target.shadowRoot.querySelector('textarea');
    const cursorAtEnd = textarea.selectionStart === textarea.value.length;
    
    if (event.key === 'Tab' && this.suggestion && cursorAtEnd && authoringSession.prompt.endsWith(' ')) {
      event.preventDefault();
      const suggestedPrompt = getSuggestedPrompt(authoringSession.prompt, this.suggestion, appSettings.numberOfWordsToSuggest);
      authoringSession.setPrompt(suggestedPrompt);
      this.suggestion = '';
    }
  }
  
  handleUndoButtonClick() {
    undoManager.undo();
  }
  
  handleBalloonClick(promptIdea) {
    authoringSession.setPrompt(promptIdea);
  }
  
  renderPromptIdeasAndStatus() {
    const renderLoadingMessage = () => html`<div class="balloon label">Generating improvement ideas...</div>`;
    const renderPromptIdea = (idea) => html`
      <div class="balloon" @click=${() => this.handleBalloonClick(idea)} ${animate()}>${idea}</div>`;
    const renderNoSelectionMessage = () => html`<div class="balloon label">Please make a selection to view improvement ideas</div>`;
    const renderApplyingStatus = () => html`<div class="balloon label">Casting a spell...</div>`;
    
    return html`
      <div class="balloon-container" ${animate()}>
        ${this.isFetchingIdeas
      ? renderLoadingMessage()
      : this.isApplying
        ? renderApplyingStatus()
        : this.promptIdeas.length > 0
          ? html`<div class="balloon label">Here are some ideas you can try: </div>${this.promptIdeas.map(renderPromptIdea)}`
          : renderNoSelectionMessage()
    }
      </div>`;
  }
  
  renderUndoButton() {
    return html`
      <sp-button class="undo" @click=${this.handleUndoButtonClick} variant="negative" ?disabled=${!undoManager.canUndo}>
        <sp-icon slot="icon" size="s">${RevertIcon()}</sp-icon>
        Undo
      </sp-button>
    `;
  }
  
  renderApplyButton() {
    return html`
      <sp-button class="apply" @click=${this.handleApplyPrompt} variant="accent" ?pending=${this.isApplying} ?disabled=${this.isApplying || !authoringSession.prompt || !authoringSession.selectedRegions.length}>
        <sp-icon slot="icon" size="m">${MagicWandIcon()}</sp-icon>
        Try It Out
      </sp-button>
    `;
  }
  
  renderCopyButton() {
    return html`
      <sp-button class="copy" variant="primary" @click=${() => navigator.clipboard.writeText(undoManager.getFullApplyCode())} ?disabled=${!undoManager.canUndo}>
        <sp-icon slot="icon" size="s">${CopyIcon()}</sp-icon>
        Copy Experiment
      </sp-button>
    `;
  }
  
  firstUpdated() {
    this.makeDraggable();
    setTimeout(() => this.makeSuggestionDivSameAsTextArea(), 0);
  }

  makeSuggestionDivSameAsTextArea() {
    const textArea = this.shadowRoot.querySelector('sp-textfield').shadowRoot.querySelector('textarea');
    const suggestionDiv = this.shadowRoot.querySelector('.suggestion');
    suggestionDiv.style.fontSize = getComputedStyle(textArea).fontSize;
    suggestionDiv.style.fontFamily = getComputedStyle(textArea).fontFamily;
    suggestionDiv.style.lineHeight = getComputedStyle(textArea).lineHeight;
    suggestionDiv.style.padding = getComputedStyle(textArea).padding;
    suggestionDiv.style.margin = getComputedStyle(textArea).margin;
    suggestionDiv.style.width = getComputedStyle(textArea).width;
    suggestionDiv.style.height = getComputedStyle(textArea).height;
  }
  
  makeDraggable() {
    const promptContainer = this.shadowRoot.querySelector('.prompt-dialog-container');
    let isDragging = false;
    let offsetX, offsetY;
    
    promptContainer.addEventListener('mousedown', (e) => {
      console.log(e.target.tagName);
      if (e.target.tagName === 'SP-TEXTFIELD') {
        return;
      }
      isDragging = true;
      offsetX = e.clientX - promptContainer.getBoundingClientRect().left;
      offsetY = e.clientY - promptContainer.getBoundingClientRect().top;
      document.addEventListener('mousemove', onMouseMove);
      document.addEventListener('mouseup', onMouseUp);
    });
    
    const onMouseMove = (e) => {
      if (isDragging) {
        promptContainer.style.left = `${e.clientX - offsetX}px`;
        promptContainer.style.top = `${e.clientY - offsetY}px`;
        promptContainer.style.transform = 'translateX(0)';
      }
    };
    
    const onMouseUp = () => {
      isDragging = false;
      this.shadowRoot.querySelector('sp-textfield').focus();
      document.removeEventListener('mousemove', onMouseMove);
      document.removeEventListener('mouseup', onMouseUp);
    };
  }
  
  handleCloseButtonClick() {
    window.dispatchEvent(new CustomEvent('toggleCopilot'));
    authoringSession.setPrompt('');
    authoringSession.setSelectedRegions([]);
  }
  
  render() {
    const suggestedPrompt = getSuggestedPrompt(authoringSession.prompt, this.suggestion, appSettings.numberOfWordsToSuggest);
    
    return html`
      <div class="prompt-dialog-container">
        <div class="header">
          <h2>Mystique Copilot</h2>
          <sp-action-button quiet @click=${this.handleCloseButtonClick}>
            <sp-icon slot="icon" size="s">${CloseIcon()}</sp-icon>
          </sp-action-button>
        </div>
        ${this.renderPromptIdeasAndStatus()}
        <div class="prompt-container">
          <sp-textfield
            placeholder="How can I help you?"
            multiline
            rows="4"
            @input=${this.handleInputChange}
            @keydown=${this.handleKeyDown}
            .value=${authoringSession.prompt}
            ?disabled=${this.isApplying}
          ></sp-textfield>
          <div class="suggestion">${suggestedPrompt}</div>
        </div>
        <div class="button-container">
          ${this.renderUndoButton()}
          ${this.renderCopyButton()}
          ${this.renderApplyButton()}
        </div>
      </div>
    `;
  }
}
