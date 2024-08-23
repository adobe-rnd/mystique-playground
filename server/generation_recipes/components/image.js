export class ImageComponent extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }
  
  static create({ imageUrl, altText }) {
    console.log('imageUrl:', imageUrl);
    const element = document.createElement('image-component');
    element.setAttribute('src', imageUrl);
    element.setAttribute('alt', altText);
    return element;
  }
  
  connectedCallback() {
    const src = this.getAttribute('src');
    const alt = this.getAttribute('alt');
    
    this.shadowRoot.innerHTML = `
      <style>
        img {
          width: 100%;
          height: 100%;
          object-fit: cover;
          border-radius: var(--brand-border-radius-small);
          box-shadow: var(--brand-box-shadow-small);
        }
      </style>
      <img src="${src}" alt="${alt}">
    `;
  }
}

customElements.define('image-component', ImageComponent);
