export class FooterComponent extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }
  
  connectedCallback() {
    this.render();
  }
  
  render() {
    const layout = this.getAttribute('layout') || 'inline';
    const alignment = this.getAttribute('alignment') || 'center';
    
    this.shadowRoot.innerHTML = `
      <style>
        * {
          margin: 0;
          padding: 0;
          box-sizing: border-box;
        }

        .footer-container {
          display: flex;
          flex-direction: ${layout === 'inline' ? 'row' : 'column'};
          align-items: ${alignment === 'center' ? 'center' : alignment === 'right' ? 'flex-end' : 'flex-start'};
          justify-content: ${alignment};
          text-align: ${alignment};
          padding: 2rem;
          background-color: #2b2e4a;
          color: white;
          border-radius: 12px;
          gap: 1rem;
          box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.1);
        }

        ::slotted(span) {
          font-size: 1rem;
          color: #dddddd;
        }

        .footer-links {
          display: flex;
          gap: 1rem;
        }

        ::slotted(a) {
          color: #ff6ec4;
          text-decoration: none;
          font-weight: 500;
          transition: color 0.3s ease;
        }

        ::slotted(a:hover) {
          color: #ffde17;
        }

        @media (max-width: 768px) {
          .footer-container {
            flex-direction: column;
            align-items: center;
            text-align: center;
          }
          
          .footer-links {
            flex-direction: column;
            align-items: center;
            gap: 0.5rem;
          }
        }
      </style>
      <div class="footer-container">
        <slot name="text"></slot>
        <div class="footer-links">
          <slot name="links"></slot>
        </div>
      </div>
    `;
  }
  
  static create({ text, links, layout, alignment }) {
    const element = document.createElement('footer-component');
    if (layout) element.setAttribute('layout', layout);
    if (alignment) element.setAttribute('alignment', alignment);
    
    if (text) {
      const textElement = document.createElement('span');
      textElement.textContent = text;
      textElement.slot = 'text';
      element.appendChild(textElement);
    }
    
    if (links && Array.isArray(links)) {
      const linkContainer = document.createElement('div');
      links.forEach(link => {
        const linkElement = document.createElement('a');
        linkElement.setAttribute('href', link.url);
        linkElement.textContent = link.text;
        linkContainer.appendChild(linkElement);
      });
      linkContainer.slot = 'links';
      element.appendChild(linkContainer);
    }
    
    return element;
  }
}

customElements.define('footer-component', FooterComponent);
