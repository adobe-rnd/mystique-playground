import {HeaderComponent} from './header.js';
import {SectionComponent} from './section.js';
import {FooterComponent} from './footer.js';

export class PageComponent extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }
  
  connectedCallback() {
    this.render();
  }
  
  render() {
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
          background: linear-gradient(120deg, #f6d365 0%, #fda085 100%);
          min-height: 100vh;
          font-family: 'Poppins', sans-serif;
          overflow-x: hidden;
        }

        .page-container ::slotted([slot="header"]) {
          padding: 2rem;
          background: #2b2e4a;
          box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
          border-radius: 12px;
          margin-bottom: 2rem;
        }

        .page-container ::slotted([slot="sections"]) {
          padding: 1.5rem;
          margin: 1rem 0;
          background: #ffffff;
          border-radius: 12px;
          box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
          transition: transform 0.3s ease, box-shadow 0.3s ease;
        }

        .page-container ::slotted([slot="sections"]:hover) {
          transform: translateY(-5px);
          box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        }

        .page-container ::slotted([slot="footer"]) {
          padding: 1.5rem;
          text-align: center;
          background: #2b2e4a;
          color: white;
          border-radius: 12px;
          margin-top: 2rem;
        }

        @media (max-width: 768px) {
          .page-container ::slotted([slot="header"]) {
            padding: 1rem;
          }

          .page-container ::slotted([slot="sections"]) {
            padding: 1rem;
            margin: 0.5rem 0;
          }

          .page-container ::slotted([slot="footer"]) {
            padding: 1rem;
          }
        }
      </style>
      <div class="page-container">
        <slot name="header"></slot>
        <slot name="sections"></slot>
        <slot name="footer"></slot>
      </div>
    `;
  }
  
  static create({ header, sections, footer }) {
    const element = document.createElement('page-component');
    
    if (header) {
      const headerElement = HeaderComponent.create(header);
      headerElement.slot = 'header';
      element.appendChild(headerElement);
    }
    
    if (sections) {
      sections.forEach(section => {
        const sectionElement = SectionComponent.create(section);
        sectionElement.slot = 'sections';
        element.appendChild(sectionElement);
      });
    }
    
    if (footer) {
      const footerElement = FooterComponent.create(footer);
      footerElement.slot = 'footer';
      element.appendChild(footerElement);
    }
    
    return element;
  }
}

customElements.define('page-component', PageComponent);
