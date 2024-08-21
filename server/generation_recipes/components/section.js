import { HeroComponent } from './hero.js';
import { CardComponent } from './card.js';

export class SectionComponent extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }
  
  connectedCallback() {
    this.render();
  }
  
  render() {
    const spacing = this.getAttribute('spacing') || '1.5rem';
    const columns = this.getAttribute('columns') || '1';
    const childrenData = JSON.parse(this.getAttribute('children') || '[]');
    
    this.shadowRoot.innerHTML = `
      <style>
        .section-container {
          display: grid;
          gap: ${spacing};
          grid-template-columns: repeat(${columns}, 1fr);
          padding: var(--brand-padding-large, 40px);
          background: var(--brand-neutral-background, #f9f9f9);
          border-radius: var(--brand-border-radius, 8px);
          box-shadow: var(--brand-box-shadow-small, 0 2px 4px rgba(0, 0, 0, 0.1));
        }

        @media (max-width: 768px) {
          .section-container {
            grid-template-columns: 1fr;
          }
        }
      </style>
      <div class="section-container">
        ${childrenData.map(child => {
      switch (child.kind) {
        case 'hero':
          return HeroComponent.create(child).outerHTML;
        case 'card':
          return CardComponent.create(child).outerHTML;
        default:
          console.warn('Unknown component type:', child.kind);
          return '';
      }
    }).join('')}
      </div>
    `;
  }
  
  static create({ children, spacing, columns }) {
    const element = document.createElement('section-component');
    if (spacing) element.setAttribute('spacing', spacing);
    if (columns) element.setAttribute('columns', columns);
    if (children && Array.isArray(children)) {
      element.setAttribute('children', JSON.stringify(children));
    }
    return element;
  }
}

customElements.define('section-component', SectionComponent);
