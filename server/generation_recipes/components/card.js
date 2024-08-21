import { ImageComponent } from './image.js';
import { ButtonComponent } from './button.js';

export class CardComponent extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }
  
  connectedCallback() {
    this.render();
  }
  
  render() {
    const layout = this.getAttribute('layout') || 'vertical';
    const alignment = this.getAttribute('alignment') || 'left';
    
    const imageSrc = this.getAttribute('imageSrc') || '';
    const imageAlt = this.getAttribute('imageAlt') || '';
    const title = this.getAttribute('title') || '';
    const description = this.getAttribute('description') || '';
    const buttons = JSON.parse(this.getAttribute('buttons') || '[]');
    
    this.shadowRoot.innerHTML = `
      <style>
        * {
          margin: 0;
          padding: 0;
          box-sizing: border-box;
        }

        .card-container {
          display: flex;
          flex-direction: ${layout === 'horizontal' ? 'row' : 'column'};
          text-align: ${alignment};
          padding: var(--brand-padding-medium, 16px);
          border-radius: var(--brand-border-radius, 8px);
          background: var(--brand-background-color, #fff);
          box-shadow: var(--brand-box-shadow-small, 0 2px 4px rgba(0, 0, 0, 0.1));
          overflow: hidden;
          position: relative;
          height: 100%;
          margin: var(--brand-spacing-small, 16px);
        }

        .card-image {
          flex: 0 0 40%;
          margin-right: ${layout === 'horizontal' ? '16px' : '0'};
        }

        .card-image img {
          width: 100%;
          height: 100%;
          object-fit: cover;
        }

        .card-content {
          display: flex;
          flex-direction: column;
          justify-content: space-between;
          flex: 1;
          padding: ${layout === 'horizontal' ? '0' : '16px'};
        }

        .card-title {
          font-size: var(--brand-heading-font-size, 1.5rem);
          color: var(--brand-heading-color, #333);
          margin-bottom: var(--brand-spacing-small, 16px);
        }

        .card-description {
          font-size: var(--brand-font-size, 1rem);
          color: var(--brand-text-color, #666);
          margin-bottom: var(--brand-spacing-small, 16px);
          flex: 1;
        }

        .card-buttons {
          display: flex;
          gap: var(--brand-spacing-small, 16px);
          margin-top: auto;
        }

        @media (max-width: 768px) {
          .card-container {
            flex-direction: column;
          }

          .card-image {
            margin-right: 0;
            margin-bottom: 16px;
          }
        }
      </style>
      <div class="card-container">
        ${imageSrc ? `<div class="card-image"><img src="${imageSrc}" alt="${imageAlt}"></div>` : ''}
        <div class="card-content">
          ${title ? `<h3 class="card-title">${title}</h3>` : ''}
          ${description ? `<p class="card-description">${description}</p>` : ''}
          <div class="card-buttons">
            ${buttons.map(button => ButtonComponent.create(button).outerHTML).join('')}
          </div>
        </div>
      </div>
    `;
  }
  
  static create({ image, title, description, buttons, layout, alignment }) {
    const element = document.createElement('card-component');
    if (layout) element.setAttribute('layout', layout);
    if (alignment) element.setAttribute('alignment', alignment);
    
    if (image) {
      element.setAttribute('imageSrc', image.src);
      element.setAttribute('imageAlt', image.alt);
    }
    
    if (title) {
      element.setAttribute('title', title);
    }
    
    if (description) {
      element.setAttribute('description', description);
    }
    
    if (buttons && Array.isArray(buttons)) {
      element.setAttribute('buttons', JSON.stringify(buttons));
    }
    
    return element;
  }
}

customElements.define('card-component', CardComponent);
