import { customElement, state } from 'lit/decorators.js';
import { css, html, LitElement } from 'lit';
import {getCssSelector, getElementHtmlWithStyles, getIntersectedElements, getSmallestEnclosingElement} from './utils';
import wretch from 'wretch';
import { throttle } from 'lodash';
import '@spectrum-web-components/icon/sp-icon.js';
import { UndoIcon, MagicWandIcon } from '@spectrum-web-components/icons-workflow';
import { undoManager } from './undo';
import { authoringSession } from './session';
import { MobxLitElement } from '@adobe/lit-mobx';
import { appSettings } from './settings';

function getSuggestedPrompt(prompt, suggestion, numberOfWords) {
  const suggestions = suggestion ? suggestion.split(' ').slice(0, numberOfWords) : [];
  const trimmedPrompt = prompt.trim();
  return suggestions.length > 0 && prompt.endsWith(' ')
    ? `${trimmedPrompt} ${suggestions.join(' ')}`.trim()
    : '';
}

async function fetchSuggestion(prompt) {
  if (/\w+\s/.test(prompt)) {
    const url = 'http://localhost:4002/autocomplete';
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
    .prompt-container {
      display: flex;
      align-items: center;
      position: fixed;
      bottom: 25px;
      left: 50%;
      transform: translateX(-50%);
      z-index: 2000;
      padding: 10px;
      background-color: rgba(0, 0, 0, 0.1);
      border-radius: 12px;
      box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
    }

    .textarea-container {
      display: flex;
      align-items: center;
      position: relative;
      flex: 1;
    }

    textarea {
      box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
      border: 3px solid rgba(0, 0, 0, 0.1);
      border-radius: 8px;
      padding: 15px;
      width: 400px;
      height: 96px;
      transition: all 0.3s ease-in-out;
      font-size: 1.5rem;
      line-height: 1.5rem;
      font-weight: bold;
      font-family: monospace;
      color: rgba(0, 0, 0, 0.8);
      resize: none;
    }

    textarea:focus {
      outline: none;
      border-color: #3b8edb;
    }

    textarea::placeholder {
      opacity: 0.7;
    }

    textarea:disabled {
      background-color: #eeeeee;
      color: #666666;
      cursor: not-allowed;
    }

    .suggestion {
      position: absolute;
      padding: 15px;
      pointer-events: none;
      white-space: pre-wrap;
      top: 3px;
      left: 3px;
      font-size: 1.5rem;
      line-height: 1.5rem;
      font-weight: bold !important;
      font-family: monospace;
      color: rgba(0, 0, 0, 0.3);
      width: 400px;
      height: 96px;
    }

    button {
      box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
      border: 2px solid transparent;
      border-radius: 50%;
      width: 48px;
      height: 48px;
      font-weight: bold;
      font-size: 1.2em;
      color: white;
      background-color: #ff5733;
      cursor: pointer;
      transition: all 0.3s ease-in-out;
      display: flex;
      align-items: center;
      justify-content: center;
      margin: 0 5px;
    }

    button:hover {
      background-color: #c13b24;
    }

    button:disabled {
      background-color: #cccccc;
      cursor: not-allowed;
    }

    .apply-button {
      background-color: #3b8edb;
    }

    .apply-button:hover {
      background-color: #1a64a2;
    }

    .apply-button:disabled {
      background-color: #cccccc;
      cursor: not-allowed;
    }

    .applying {
      animation: rotate 1s linear infinite;
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
  
  async handleApplyPrompt() {
    this.isApplying = true;
    this.suggestion = '';
    
    const intersectedElements = getIntersectedElements(authoringSession.selectedRegions);
    const enclosingElement = getSmallestEnclosingElement(intersectedElements);
    
    const originalHtml = enclosingElement.outerHTML;
    
    const contextHtml = await getElementHtmlWithStyles(enclosingElement);
    const selectionHtmls = await Promise.all(
      intersectedElements.map(element => getElementHtmlWithStyles(element))
    );
    
    console.log('Prompt:', authoringSession.prompt);
    console.log('Context HTML:', contextHtml.length);
    console.log('Selection HTML:', selectionHtmls.map(html => html.length).join(', '));
    
    wretch('http://localhost:4002/assistant')
      .post({
        context: contextHtml,
        selection: selectionHtmls,
        prompt: authoringSession.prompt
      })
      .json()
      .then((data) => {
        const receivedHtml = data.html;
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = receivedHtml;
        const newElement = tempDiv.firstElementChild;
        
        if (newElement) {
          const selector = getCssSelector(enclosingElement);
          
          if (selector) {
            undoManager.addEntry(
              `document.querySelector('${selector}').outerHTML = \`${originalHtml}\`;`,
              authoringSession.prompt,
              authoringSession.selectedRegions
            );
            
            const elementToReplace = document.querySelector(selector);
            if (elementToReplace) {
              elementToReplace.replaceWith(newElement);
              authoringSession.setPrompt('');
              authoringSession.setSelectedRegions([]);
              this.suggestion = '';
            } else {
              console.error('Could not find element to replace using selector:', selector);
            }
          } else {
            console.error('Could not generate a unique selector for the element');
          }
        } else {
          console.error('Received HTML does not contain a valid element');
        }
      })
      .catch((error) => {
        console.error('Error replacing the element:', error);
      })
      .finally(() => {
        this.isApplying = false;
        this.requestUpdate();
      });
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
    const textarea = event.target;
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
  
  renderUndoButton() {
    return html`
      <button @click=${this.handleUndoButtonClick} ?disabled=${!undoManager.canUndo}>
        <sp-icon size="s" style="color: white;">${UndoIcon()}</sp-icon>
      </button>
    `;
  }
  
  renderApplyButton() {
    return html`
      <button class="apply-button ${this.isApplying ? 'applying' : ''}" @click=${this.handleApplyPrompt} ?disabled=${this.isApplying || !authoringSession.prompt || !authoringSession.selectedRegions.length}>
        <sp-icon size="s" style="color: white;" disabled=${this.isApplying}>${MagicWandIcon()}</sp-icon>
      </button>
    `;
  }
  
  render() {
    const suggestedPrompt = getSuggestedPrompt(authoringSession.prompt, this.suggestion, appSettings.numberOfWordsToSuggest);
    
    return html`
      <div class="prompt-container">
        ${this.renderUndoButton()}
        <div class="textarea-container">
          <textarea
            placeholder="What do you want me to do?"
            @input=${this.handleInputChange}
            @keydown=${this.handleKeyDown}
            .value=${authoringSession.prompt}
            ?disabled=${this.isApplying}
          ></textarea>
          ${suggestedPrompt ? html`<div class="suggestion">${suggestedPrompt}</div>` : ''}
        </div>
        ${this.renderApplyButton()}
      </div>
    `;
  }
}
