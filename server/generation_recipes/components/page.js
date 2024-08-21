import { HeaderComponent } from './header.js';
import { SectionComponent } from './section.js';
import { FooterComponent } from './footer.js';

export class PageComponent extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }
  
  connectedCallback() {
    this.render();
  }
  
  render() {
    const headerData = this.getAttribute('header') ? JSON.parse(this.getAttribute('header')) : null;
    const sectionsData = this.getAttribute('sections') ? JSON.parse(this.getAttribute('sections')) : [];
    const footerData = this.getAttribute('footer') ? JSON.parse(this.getAttribute('footer')) : null;
    
    this.shadowRoot.innerHTML = `
    <style>
      * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
      }

      .page-container {
        display: flex;
        flex-direction: column;
        min-height: 100vh;
        background-color: var(--brand-background-color, #f8f8f8);
        font-family: var(--brand-font-family, Arial, sans-serif);
        padding: var(--brand-padding-large, 40px);
        gap: var(--brand-spacing-large, 32px);
      }

      @media (max-width: 768px) {
        .page-container {
          padding: var(--brand-padding-medium, 20px);
        }
      }
    </style>
    <div class="page-container">
      ${headerData ? HeaderComponent.create(headerData).outerHTML : ''}
      ${sectionsData.map(section => SectionComponent.create(section).outerHTML).join('')}
      ${footerData ? FooterComponent.create(footerData).outerHTML : ''}
    </div>
  `;
  }
  
  static create({ header, sections, footer }) {
    const element = document.createElement('page-component');
    if (header) element.setAttribute('header', JSON.stringify(header));
    if (sections) element.setAttribute('sections', JSON.stringify(sections));
    if (footer) element.setAttribute('footer', JSON.stringify(footer));
    return element;
  }
}

customElements.define('page-component', PageComponent);
