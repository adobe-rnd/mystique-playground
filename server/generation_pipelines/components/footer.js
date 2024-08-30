export class FooterComponent extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }
  
  connectedCallback() {
    this.render();
  }
  
  render() {
    const alignment = this.getAttribute('alignment') || 'center';
    const layout = this.getAttribute('layout') || 'inline';
    const textContent = this.getAttribute('text') || '';
    const links = JSON.parse(this.getAttribute('links') || '[]');
    
    this.shadowRoot.innerHTML = `
      <style>
        .footer-container {
          display: ${layout === 'stacked' ? 'block' : 'flex'};
          justify-content: ${alignment};
          align-items: center;
          padding: var(--brand-padding-medium, 16px);
          background-color: var(--brand-primary-color, #f8f8f8);
          color: var(--brand-text-color, #333);
          border-radius: var(--brand-border-radius, 8px);
          text-align: ${alignment};
        }

        .footer-text {
          margin-right: ${layout === 'stacked' ? '0' : 'auto'};
          margin-bottom: ${layout === 'stacked' ? '16px' : '0'};
        }

        .footer-links {
          display: flex;
          gap: var(--brand-spacing-small, 16px);
        }

        .footer-links a {
          color: var(--brand-link-color, #007BFF);
          text-decoration: none;
          transition: color 0.3s ease;
        }

        .footer-links a:hover {
          color: var(--brand-link-hover-color, #0056b3);
        }

        @media (max-width: 768px) {
          .footer-container {
            flex-direction: column;
            text-align: center;
          }

          .footer-text {
            margin-bottom: 16px;
          }
        }
      </style>
      <div class="footer-container">
        <div class="footer-text">${textContent}</div>
        <div class="footer-links">
          ${links.map(link => `
            <a href="${link.url}">${link.text}</a>
          `).join('')}
        </div>
      </div>
    `;
  }
  
  static create({ text, links, layout, alignment }) {
    const element = document.createElement('footer-component');
    if (layout) element.setAttribute('layout', layout);
    if (alignment) element.setAttribute('alignment', alignment);
    if (text) element.setAttribute('text', text);
    if (links && Array.isArray(links)) {
      element.setAttribute('links', JSON.stringify(links));
    }
    
    return element;
  }
}

customElements.define('footer-component', FooterComponent);
