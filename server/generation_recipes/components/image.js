export class ImageComponent extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }
  
  static create({ src, alt }) {
    const element = document.createElement('image-component');
    element.setAttribute('src', src);
    element.setAttribute('alt', alt);
    return element;
  }
  
  connectedCallback() {
    const src = this.getAttribute('src');
    const alt = this.getAttribute('alt');
    
    this.shadowRoot.innerHTML = `
      <style>
        img {
          max-width: 100%;
          height: auto;
          border-radius: 12px;
          box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
          transition: transform 0.3s ease, box-shadow 0.3s ease;
        }

        img:hover {
          transform: scale(1.05);
          box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        }
      </style>
      <img src="${src}" alt="${alt}">
    `;
  }
}

customElements.define('image-component', ImageComponent);
