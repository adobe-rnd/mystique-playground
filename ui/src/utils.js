export function getCssSelector(element) {
  if (element.id) {
    return `#${element.id}`;
  }
  let selector = element.nodeName.toLowerCase();
  if (element.className) {
    selector += '.' + element.className.trim().replace(/\s+/g, '.');
  }
  let sib = element, nth = 1;
  while (sib = sib.previousElementSibling) {
    if (sib.nodeName.toLowerCase() === element.nodeName.toLowerCase()) {
      nth++;
    }
  }
  if (nth != 1) {
    selector += `:nth-of-type(${nth})`;
  }
  return selector;
}
