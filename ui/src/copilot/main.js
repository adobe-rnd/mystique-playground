import '@webcomponents/custom-elements';
import 'lit/polyfill-support.js';

import './copilot.js'

const copilotRoot = document.createElement('copilot-root');
document.body.insertAdjacentElement('afterbegin', copilotRoot);

function toggleCopilot() {
  console.log('Toggling copilot');
  copilotRoot.style.display = copilotRoot.style.display === 'none' ? 'block' : 'none';
}

window.addEventListener('toggleCopilot', () => {
  toggleCopilot();
});

console.log('Mystique Copilot loaded');
