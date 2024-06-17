import { customElement, state } from 'lit/decorators.js';
import { css, html, LitElement } from 'lit';

import './prompt.js';
import './drawing.js';
import './settings.js';

@customElement('assistant-root')
export class AssistantRoot extends LitElement {
  render() {
    return html`
      <sp-theme theme="spectrum" color="light" scale="medium">
        <drawing-canvas></drawing-canvas>
        <prompt-component></prompt-component>
        <settings-button></settings-button>
      </sp-theme>
    `;
  }
}
