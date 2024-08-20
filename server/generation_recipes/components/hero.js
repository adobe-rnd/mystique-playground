import {ButtonComponent} from './button.js';


export class HeroComponent extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }
  
  connectedCallback() {
    this.render();
  }
  
  render() {
    const background = this.getAttribute('background') || '';
    const alignment = this.getAttribute('alignment') || 'center';
    
    this.shadowRoot.innerHTML = `
      <style>
        * {
          margin: 0;
          padding: 0;
          box-sizing: border-box;
        }

        .hero-container {
          display: flex;
          flex-direction: column;
          justify-content: center;
          align-items: ${alignment};
          text-align: ${alignment};
          padding: 4rem 2rem;
          background-image: url('${background}');
          background-size: cover;
          background-position: center;
          background-repeat: no-repeat;
          position: relative;
          color: #ffffff;
          overflow: hidden;
          border-radius: 12px;
          box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
          animation: fadeIn 1s ease-in-out;
        }

        .hero-container::before {
          content: '';
          position: absolute;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          background: rgba(0, 0, 0, 0.4);
          backdrop-filter: blur(4px);
          z-index: 0;
        }

        .hero-headline {
          font-size: 3rem;
          font-weight: bold;
          margin: 1rem 0;
          z-index: 1;
          animation: slideInDown 0.8s ease-in-out;
        }

        .hero-subheadline {
          font-size: 1.8rem;
          font-weight: 300;
          margin: 0.5rem 0;
          z-index: 1;
          animation: slideInUp 0.8s ease-in-out;
        }

        .hero-buttons {
          margin-top: 2rem;
          z-index: 1;
          display: flex;
          gap: 1rem;
          animation: fadeIn 1.2s ease-in-out;
        }

        @keyframes fadeIn {
          0% {
            opacity: 0;
          }
          100% {
            opacity: 1;
          }
        }

        @keyframes slideInDown {
          0% {
            opacity: 0;
            transform: translateY(-50px);
          }
          100% {
            opacity: 1;
            transform: translateY(0);
          }
        }

        @keyframes slideInUp {
          0% {
            opacity: 0;
            transform: translateY(50px);
          }
          100% {
            opacity: 1;
            transform: translateY(0);
          }
        }

        @media (max-width: 768px) {
          .hero-headline {
            font-size: 2.2rem;
          }

          .hero-subheadline {
            font-size: 1.4rem;
          }

          .hero-buttons {
            flex-direction: column;
            gap: 0.5rem;
          }
        }
      </style>
      <div class="hero-container">
        <slot name="headline" class="hero-headline"></slot>
        <slot name="subheadline" class="hero-subheadline"></slot>
        <div class="hero-buttons">
          <slot name="buttons"></slot>
        </div>
      </div>
    `;
  }
  
  static create({ background, headline, subheadline, buttons, alignment }) {
    const element = document.createElement('hero-component');
    if (background) element.setAttribute('background', background);
    if (alignment) element.setAttribute('alignment', alignment);
    
    if (headline) {
      const headlineElement = document.createElement('h1');
      headlineElement.textContent = headline;
      headlineElement.slot = 'headline';
      element.appendChild(headlineElement);
    }
    
    if (subheadline) {
      const subheadlineElement = document.createElement('h2');
      subheadlineElement.textContent = subheadline;
      subheadlineElement.slot = 'subheadline';
      element.appendChild(subheadlineElement);
    }
    
    if (buttons && Array.isArray(buttons)) {
      buttons.forEach(button => {
        const buttonElement = ButtonComponent.create(button);
        buttonElement.slot = 'buttons';
        element.appendChild(buttonElement);
      });
    }
    
    return element;
  }
}

customElements.define('hero-component', HeroComponent);
