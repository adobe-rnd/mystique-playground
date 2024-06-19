import '@webcomponents/custom-elements';
import 'lit/polyfill-support.js';

import './assistant.js'

const assistantRoot = document.createElement('assistant-root');
document.body.insertAdjacentElement('afterbegin', assistantRoot);

function toggleAssistant() {
  console.log('Toggling assistant');
  assistantRoot.style.display = assistantRoot.style.display === 'none' ? 'block' : 'none';
}

window.addEventListener('toggleAssistant', () => {
  toggleAssistant();
});

console.log('Mystique Playground loaded');
