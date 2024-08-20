import {ImageComponent} from './image.js';

export class HeaderComponent extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }
  
  connectedCallback() {
    this.render();
  }
  
  render() {
    const alignment = this.getAttribute('alignment') || 'left';
    
    this.shadowRoot.innerHTML = `
      <style>
        * {
          margin: 0;
          padding: 0;
          box-sizing: border-box;
        }
        
        .header-container {
          display: flex;
          align-items: center;
          justify-content: ${alignment === 'center' ? 'center' : alignment === 'right' ? 'flex-end' : 'flex-start'};
          text-align: ${alignment};
          background: linear-gradient(135deg, #ff6ec4, #7873f5);
          padding: 1rem 2rem;
          border-radius: 12px;
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }
        
        nav a {
          margin: 0 1rem;
          font-family: 'Poppins', sans-serif;
          font-size: 1rem;
          font-weight: 500;
          color: #ffffff;
          text-decoration: none;
          transition: color 0.3s, transform 0.3s;
        }

        nav a:hover {
          color: #ffde17;
          transform: scale(1.05);
        }

        nav {
          display: flex;
          gap: 1rem;
        }

        .header-container::before {
          content: '';
          position: absolute;
          width: 100%;
          height: 100%;
          top: 0;
          left: 0;
          background: linear-gradient(135deg, rgba(255, 255, 255, 0.1), rgba(0, 0, 0, 0.1));
          opacity: 0.3;
          pointer-events: none;
        }

        slot[name="logo"]::slotted(img) {
          width: 50px;
          height: auto;
          margin-right: 2rem;
        }

        @media (max-width: 768px) {
          .header-container {
            flex-direction: column;
            padding: 1rem;
            text-align: center;
          }
          
          nav {
            flex-direction: column;
            gap: 0.5rem;
          }
          
          slot[name="logo"]::slotted(img) {
            margin-bottom: 1rem;
          }
        }
      </style>
      <div class="header-container">
        <slot name="logo"></slot>
        <slot name="navigation"></slot>
      </div>
    `;
  }
  
  static create({ logo, navigation, alignment }) {
    const element = document.createElement('header-component');
    if (alignment) element.setAttribute('alignment', alignment);
    
    if (logo) {
      const logoElement = ImageComponent.create(logo);
      logoElement.slot = 'logo';
      element.appendChild(logoElement);
    }
    
    if (navigation && Array.isArray(navigation)) {
      const navContainer = document.createElement('nav');
      navigation.forEach(link => {
        const linkElement = document.createElement('a');
        linkElement.setAttribute('href', link.url);
        linkElement.textContent = link.text;
        navContainer.appendChild(linkElement);
      });
      navContainer.slot = 'navigation';
      element.appendChild(navContainer);
    }
    
    return element;
  }
}

customElements.define('header-component', HeaderComponent);
