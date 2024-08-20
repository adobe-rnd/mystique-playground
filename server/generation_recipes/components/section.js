import {HeroComponent} from './hero.js';
import {CardComponent} from './card.js';

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
    
    this.shadowRoot.innerHTML = `
      <style>
        * {
          margin: 0;
          padding: 0;
          box-sizing: border-box;
        }

        .section-container {
          display: grid;
          gap: ${spacing};
          grid-template-columns: repeat(${columns}, 1fr);
          padding: 2rem;
          background: rgba(255, 255, 255, 0.8);
          border-radius: 12px;
          box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
          transition: transform 0.3s ease, box-shadow 0.3s ease;
          position: relative;
        }

        .section-container::before {
          content: '';
          position: absolute;
          top: -10%;
          right: -10%;
          width: 200px;
          height: 200px;
          background: radial-gradient(circle at center, rgba(255, 107, 107, 0.5) 0%, transparent 80%);
          z-index: -1;
        }

        .section-container::after {
          content: '';
          position: absolute;
          bottom: -10%;
          left: -10%;
          width: 200px;
          height: 200px;
          background: radial-gradient(circle at center, rgba(107, 255, 107, 0.5) 0%, transparent 80%);
          z-index: -1;
        }

        .section-container:hover {
          transform: translateY(-5px);
          box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        }

        @media (max-width: 768px) {
          .section-container {
            grid-template-columns: 1fr;
            padding: 1.5rem;
          }
        }

        ::slotted(*) {
          transition: transform 0.3s ease;
        }

        ::slotted(*:hover) {
          transform: scale(1.03);
        }
      </style>
      <div class="section-container">
        <slot></slot>
      </div>
    `;
  }
  
  static create({ children, spacing, columns }) {
    const element = document.createElement('section-component');
    if (spacing) element.setAttribute('spacing', spacing);
    if (columns) element.setAttribute('columns', columns);
    
    if (children && Array.isArray(children)) {
      children.forEach(child => {
        switch (child.kind) {
          case 'hero':
            const heroElement = HeroComponent.create(child);
            element.appendChild(heroElement);
            break;
          case 'card':
            const cardElement = CardComponent.create(child);
            element.appendChild(cardElement);
            break;
          default:
            console.warn('Unknown component type:', child.kind);
        }
      });
    }
    
    return element;
  }
}

customElements.define('section-component', SectionComponent);
