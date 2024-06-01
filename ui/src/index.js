import './main.js'

function createOverlay() {
  const overlay = document.createElement('mystique-overlay');
  document.body.insertAdjacentElement('afterbegin', overlay);
  return overlay;
}

createOverlay();

console.log('Mystique Overlay loaded');
