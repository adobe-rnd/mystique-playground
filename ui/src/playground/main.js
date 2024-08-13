import '@webcomponents/custom-elements';
import 'lit/polyfill-support.js';

import './playground.js'

document.body.insertAdjacentElement('afterbegin', document.createElement('mystique-playground'));

console.log('Mystique Playground loaded');
