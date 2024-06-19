import { customElement } from 'lit/decorators.js';
import { css, html, LitElement } from 'lit';

import './prompt.js';
import './drawing.js';
import './settings.js';

import '@spectrum-web-components/theme/sp-theme.js';
import '@spectrum-web-components/theme/src/themes.js';

import '@spectrum-web-components/styles/scale-medium.css';
import '@spectrum-web-components/styles/typography.css';

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
