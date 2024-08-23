import { ButtonComponent } from './button.js';

export class HeroComponent extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }
  
  connectedCallback() {
    this.render();
  }
  
  render() {
    const heading = this.getAttribute('heading') || '';
    const subheading = this.getAttribute('subheading') || '';
    const backgroundImageSrc = this.getAttribute('background-image-src') || '';
    const alignment = this.getAttribute('alignment') || 'center';
    const layout = this.getAttribute('layout') || 'stacked';
    
    const buttons = JSON.parse(this.getAttribute('buttons') || '[]');
    
    this.shadowRoot.innerHTML = `
      <style>
        .hero-container {
          padding: var(--brand-padding-large, 40px);
          background: linear-gradient(rgba(255, 255, 255, 1), rgba(255, 255, 255, 0.8)), url('${backgroundImageSrc}') center / cover;
          border-radius: var(--brand-border-radius, 8px);
          display: flex;
          flex-direction: ${layout === 'inline' ? 'row' : 'column'};
          align-items: ${alignment === 'center' ? 'center' : 'flex-start'};
          justify-content: ${alignment === 'center' ? 'center' : 'space-between'};
          text-align: ${alignment};
          color: var(--brand-text-color, #333);
          box-shadow: var(--brand-box-shadow-small, 0 2px 4px rgba(0, 0, 0, 0.1));
          position: relative;
          gap: var(--brand-spacing-medium, 20px);
        }
    
        .hero-headline {
          font-size: var(--brand-heading-font-size, 2.5rem);
          margin-bottom: var(--brand-spacing-small, 16px);
          text-align: inherit;
        }
    
        .hero-subheadline {
          font-size: var(--brand-large-font-size, 1.5rem);
          margin-bottom: var(--brand-spacing-small, 16px);
          text-align: inherit;
        }
    
        .hero-buttons {
          display: flex;
          gap: var(--brand-spacing-small, 16px);
          margin-top: var(--brand-spacing, 24px);
          justify-content: ${alignment};
        }
    
        @media (max-width: 768px) {
          .hero-container {
            flex-direction: column;
            text-align: center;
          }
        }
      </style>
      <div class="hero-container">
        <div class="hero-content">
          ${heading ? `<h1 class="hero-headline">${heading}</h1>` : ''}
          ${subheading ? `<h2 class="hero-subheadline">${subheading}</h2>` : ''}
          <div class="hero-buttons">
            ${buttons.map(button => ButtonComponent.create(button).outerHTML).join('')}
          </div>
        </div>
      </div>
    `;
  }
  
  static create({ heading, subheading, backgroundImage, buttons, alignment, layout }) {
    const element = document.createElement('hero-component');
    if (heading) element.setAttribute('heading', heading);
    if (subheading) element.setAttribute('subheading', subheading);
    if (backgroundImage) {
      element.setAttribute('background-image-src', backgroundImage.imageUrl);
      element.setAttribute('background-image-alt', backgroundImage.altText);
    }
    if (alignment) element.setAttribute('alignment', alignment);
    if (layout) element.setAttribute('layout', layout);
    
    if (buttons && Array.isArray(buttons)) {
      element.setAttribute('buttons', JSON.stringify(buttons));
    }
    
    return element;
  }
}

customElements.define('hero-component', HeroComponent);
