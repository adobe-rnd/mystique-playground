import '@webcomponents/custom-elements';
import 'lit/polyfill-support.js';

import './toolbox.js'

document.body.insertAdjacentElement('afterbegin', document.createElement('mystique-overlay'));

console.log('Mystique Toolbox loaded');
