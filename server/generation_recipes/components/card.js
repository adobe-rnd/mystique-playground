import {ImageComponent} from './image.js';
import {ButtonComponent} from './button.js';

export class CardComponent extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }
  
  connectedCallback() {
    this.render();
  }
  
  render() {
    const layout = this.getAttribute('layout') || 'stacked';
    const alignment = this.getAttribute('alignment') || 'left';
    
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
          padding: 1.5rem;
          border-radius: 12px;
          background: #ffffff;
          box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
          transition: transform 0.3s ease, box-shadow 0.3s ease;
          overflow: hidden;
          position: relative;
        }

        .card-container:hover {
          transform: translateY(-5px);
          box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        }

        .card-container::before {
          content: '';
          position: absolute;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          background: linear-gradient(135deg, rgba(255, 107, 107, 0.15), rgba(107, 255, 107, 0.15));
          opacity: 0.2;
          z-index: 0;
        }

        ::slotted(img) {
          width: 100%;
          border-radius: 8px;
          margin-bottom: 1rem;
        }

        .card-content {
          z-index: 1;
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }

        ::slotted(h3) {
          font-size: 1.8rem;
          margin: 0;
          font-weight: 600;
          color: #333333;
        }

        ::slotted(p) {
          font-size: 1rem;
          font-weight: 300;
          color: #555555;
        }

        .card-buttons {
          display: flex;
          gap: 0.5rem;
          margin-top: 1rem;
        }

        @media (max-width: 768px) {
          .card-container {
            flex-direction: column;
          }
        }
      </style>
      <div class="card-container">
        <slot name="image"></slot>
        <div class="card-content">
          <slot name="title"></slot>
          <slot name="description"></slot>
          <div class="card-buttons">
            <slot name="buttons"></slot>
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
      const imageElement = ImageComponent.create(image);
      imageElement.slot = 'image';
      element.appendChild(imageElement);
    }
    
    if (title) {
      const titleElement = document.createElement('h3');
      titleElement.textContent = title;
      titleElement.slot = 'title';
      element.appendChild(titleElement);
    }
    
    if (description) {
      const descriptionElement = document.createElement('p');
      descriptionElement.textContent = description;
      descriptionElement.slot = 'description';
      element.appendChild(descriptionElement);
    }
    
    if (buttons && Array.isArray(buttons)) {
      const buttonContainer = document.createElement('div');
      buttons.forEach(button => {
        const buttonElement = ButtonComponent.create(button);
        buttonContainer.appendChild(buttonElement);
      });
      buttonContainer.slot = 'buttons';
      element.appendChild(buttonContainer);
    }
    
    return element;
  }
}

customElements.define('card-component', CardComponent);
