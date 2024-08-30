export class ButtonComponent extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }
  
  static create({ text, url, style }) {
    const element = document.createElement('button-component');
    element.setAttribute('url', url);
    element.setAttribute('style', style || 'primary');
    element.textContent = text;
    return element;
  }
  
  connectedCallback() {
    const buttonStyle = this.getAttribute('style') || 'primary';
    const url = this.getAttribute('url') || '#';
    const buttonText = this.textContent;
    
    this.shadowRoot.innerHTML = `
      <style>
        a {
          text-decoration: none;
          padding: 0.75rem 1.5rem;
          font-size: 1rem;
          font-weight: 600;
          display: inline-block;
          border-radius: 8px;
          transition: background-color 0.3s ease, box-shadow 0.3s ease, transform 0.3s ease;
          text-align: center;
        }
        .button.primary {
          background-color: #ff6ec4;
          color: white;
          box-shadow: 0 4px 14px rgba(255, 110, 196, 0.3);
        }
        .button.primary:hover {
          background-color: #ff85d8;
          transform: translateY(-2px);
          box-shadow: 0 8px 18px rgba(255, 110, 196, 0.5);
        }
        .button.secondary {
          background-color: #6c757d;
          color: white;
          box-shadow: 0 4px 14px rgba(108, 117, 125, 0.3);
        }
        .button.secondary:hover {
          background-color: #868e96;
          transform: translateY(-2px);
          box-shadow: 0 8px 18px rgba(108, 117, 125, 0.5);
        }
        .button.link {
          background: none;
          color: #007bff;
          text-decoration: underline;
          padding: 0;
          box-shadow: none;
        }
        .button.link:hover {
          color: #0056b3;
        }
      </style>
      <a class="button ${buttonStyle}" href="${url}">
        ${buttonText}
      </a>
    `;
  }
}

customElements.define('button-component', ButtonComponent);
