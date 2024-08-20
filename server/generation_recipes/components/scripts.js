import { PageComponent } from './page.js';

function renderPage(data) {
  const page = PageComponent.create(data);
  document.getElementsByTagName('body').item(0).appendChild(page);
}

export function render(data) {
  document.addEventListener('DOMContentLoaded', () => {
    renderPage(data);
  });
}
