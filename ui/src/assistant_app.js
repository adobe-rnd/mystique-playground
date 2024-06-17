import '@webcomponents/custom-elements';
import 'lit/polyfill-support.js';

import './assistant.js'

document.body.insertAdjacentElement('afterbegin', document.createElement('assistant-root'));

console.log('Mystique Assistant loaded');
