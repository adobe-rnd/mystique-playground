export function generateCssSelector(element) {
  if (!element || element.nodeType !== Node.ELEMENT_NODE) {
    return null;
  }
  
  if (element.id) {
    return `#${element.id}`;
  }
  
  const parts = [];
  
  while (element && element.nodeType === Node.ELEMENT_NODE) {
    let selector = element.nodeName.toLowerCase();
    
    if (element.id) {
      selector = `#${element.id}`;
      parts.unshift(selector);
      break;
    }
    
    if (element.className) {
      const classNames = element.className.trim().split(/\s+/);
      if (classNames.length > 0) {
        selector += '.' + classNames.join('.');
      }
    }
    
    let sibling = element;
    let nth = 1;
    while (sibling.previousElementSibling) {
      sibling = sibling.previousElementSibling;
      if (sibling.nodeName.toLowerCase() === element.nodeName.toLowerCase()) {
        nth++;
      }
    }
    if (nth !== 1 || (!element.id && !element.className)) {
      selector += `:nth-of-type(${nth})`;
    }
    
    parts.unshift(selector);
    element = element.parentElement;
    
    if (element && (element.id || element.nodeName.toLowerCase() === 'body')) {
      break;
    }
  }
  
  const finalSelector = parts.join(' > ');
  
  // Ensure uniqueness
  if (document.querySelectorAll(finalSelector).length === 1) {
    return finalSelector;
  }
  
  // Add nth-child to ensure uniqueness
  let uniqueSelector = finalSelector;
  const elementInstance = document.querySelector(finalSelector);
  if (elementInstance) {
    const parent = elementInstance.parentElement;
    if (parent) {
      const children = Array.from(parent.children);
      const index = children.indexOf(elementInstance) + 1;
      uniqueSelector += `:nth-child(${index})`;
    }
  }
  return uniqueSelector;
}

export function isElementVisible(element) {
  if (!element) {
    return false;
  }
  
  function checkVisibility(el) {
    const style = window.getComputedStyle(el);
    
    // Check if the current element is hidden
    if (style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0') {
      return false;
    }
    
    // Check if the current element has non-zero dimensions
    if (el.offsetWidth <= 0 && el.offsetHeight <= 0) {
      return false;
    }
    
    return true;
  }
  
  // Check the element and its ancestors
  let currentElement = element;
  while (currentElement) {
    if (!checkVisibility(currentElement)) {
      return false;
    }
    currentElement = currentElement.parentElement;
  }
  
  return true;
}

export function isElementPositionedOverContent(element) {
  if (!element) {
    return false;
  }
  
  // Helper function to check if the element is positioned absolutely or fixed
  function checkPosition(el) {
    const style = window.getComputedStyle(el);
    return style.position === 'absolute' || style.position === 'fixed';
  }
  
  // Check the element itself
  if (checkPosition(element)) {
    return true;
  }
  
  // Check the ancestors of the element
  let currentElement = element.parentElement;
  while (currentElement) {
    if (checkPosition(currentElement)) {
      return true;
    }
    currentElement = currentElement.parentElement;
  }
  
  return false;
}

export async function getElementHtml(element, includeStyles = false) {
  if (!includeStyles) {
    return element.outerHTML;
  }
  
  const essentialCssProperties = [
    "color",
    "background-color",
    "background-image",
    "font-family",
    "font-size",
    "font-weight",
    "line-height",
    "text-align",
    "text-decoration",
    "top",
    "right",
    "bottom",
    "left",
    "float",
    "margin",
    "padding",
    "border",
    "width",
    "height",
    "flex-direction",
    "justify-content",
    "align-items",
    "flex-wrap",
    "z-index"
  ];
  
  function getExplicitlySetStyles(element) {
    const computedStyle = window.getComputedStyle(element);
    const explicitlySetStyles = {};
    
    essentialCssProperties.forEach(property => {
      const value = computedStyle.getPropertyValue(property);
      if (value) {
        explicitlySetStyles[property] = value;
      }
    });
    
    return explicitlySetStyles;
  }
  
  function applyInlineStyles(element) {
    const styles = getExplicitlySetStyles(element);
    let styleString = '';
    for (let property in styles) {
      styleString += `${property}: ${styles[property]}; `;
    }
    element.setAttribute('style', styleString);
    
    // console.log('Style:', styleString);
    
    for (let child of element.children) {
      applyInlineStyles(child);
    }
  }
  
  function createStyledClone(element) {
    const clone = element.cloneNode(true);
    return clone;
  }
  
  // Attach element to the DOM to ensure styles are computed correctly
  const tempWrapper = document.createElement('div');
  tempWrapper.style.position = 'absolute';
  tempWrapper.style.left = '-9999px';
  document.body.appendChild(tempWrapper);
  
  const clonedElement = createStyledClone(element);
  tempWrapper.appendChild(clonedElement);
  applyInlineStyles(clonedElement);
  
  // Remove the temporary wrapper after applying styles
  const result = tempWrapper.innerHTML;
  document.body.removeChild(tempWrapper);
  
  return result;
}
