import { ImageComponent } from './image.js';

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
    const navigation = JSON.parse(this.getAttribute('navigation') || '[]');
    
    this.shadowRoot.innerHTML = `
      <style>
        .header-container {
          display: flex;
          justify-content: ${alignment};
          align-items: center;
          background-color: var(--brand-primary-color, #fff);
          padding: var(--brand-padding-medium, 16px);
          border-radius: var(--brand-border-radius, 8px);
          box-shadow: var(--brand-box-shadow-small, 0 2px 4px rgba(0, 0, 0, 0.1));
        }

        .logo img {
          height: 50px;
          width: auto;
          margin-right: var(--brand-spacing-small, 16px);
        }

        nav {
          display: flex;
          gap: var(--brand-spacing-small, 16px);
        }

        nav a {
          color: white;
          font-family: var(--brand-font-family, Arial, sans-serif);
          font-size: var(--brand-font-size, 16px);
          text-decoration: none;
          transition: color 0.3s ease;
        }

        nav a:hover {
          color: var(--brand-link-hover-color, #007BFF);
        }

        @media (max-width: 768px) {
          .header-container {
            flex-direction: column;
            text-align: center;
          }

          .logo {
            margin-bottom: var(--brand-spacing-small, 16px);
          }
        }
      </style>
      <div class="header-container">
        <nav>
          ${navigation.map(link => `
            <a href="${link.url}" class="nav-link">${link.text}</a>
          `).join('')}
        </nav>
      </div>
    `;
  }
  
  static create({ navigation, alignment }) {
    const element = document.createElement('header-component');
    if (alignment) element.setAttribute('alignment', alignment);
    
    if (navigation && Array.isArray(navigation)) {
      element.setAttribute('navigation', JSON.stringify(navigation));
    }
    
    return element;
  }
}

customElements.define('header-component', HeaderComponent);
