export function getCssSelector(element) {
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
        selector = '.' + classNames.join('.');
      }
    }
    
    if (!element.id && !element.className) {
      let sibling = element;
      let nth = 1;
      while (sibling.previousElementSibling) {
        sibling = sibling.previousElementSibling;
        if (sibling.nodeName.toLowerCase() === element.nodeName.toLowerCase()) {
          nth++;
        }
      }
      if (nth !== 1) {
        selector += `:nth-of-type(${nth})`;
      }
    }
    
    parts.unshift(selector);
    element = element.parentElement;
    
    // Stop if we've reached an element with an ID or a body element
    if (element && (element.id || element.nodeName.toLowerCase() === 'body')) {
      break;
    }
  }
  
  const finalSelector = parts.join(' > ');
  
  // Ensure uniqueness
  if (document.querySelectorAll(finalSelector).length === 1) {
    return finalSelector;
  }
  
  console.warn('Non-unique selector:', finalSelector);
  
  return parts.join(' > ');
}
