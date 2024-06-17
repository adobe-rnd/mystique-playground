import html2canvas from 'html2canvas';
import * as polygonClipping from 'polygon-clipping';

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

export function calculateDistance(point1, point2) {
  return Math.sqrt((point1.x - point2.x) ** 2 + (point1.y - point2.y) ** 2);
}

// Ramer-Douglas-Peucker algorithm
export function optimizePath(path, epsilon = 2) {
  if (path.length < 3) return path;
  
  const sqr = (x) => x * x;
  
  const getSqDist = (p1, p2) => sqr(p1.x - p2.x) + sqr(p1.y - p2.y);
  
  const getSqSegDist = (p, v, w) => {
    let l2 = getSqDist(v, w);
    if (l2 === 0) return getSqDist(p, v);
    let t = ((p.x - v.x) * (w.x - v.x) + (p.y - v.y) * (w.y - v.y)) / l2;
    t = Math.max(0, Math.min(1, t));
    return getSqDist(p, { x: v.x + t * (w.x - v.x), y: v.y + t * (w.y - v.y) });
  };
  
  const simplifyDPStep = (points, first, last, epsilon, simplified) => {
    let maxDist = 0, index = 0;
    for (let i = first + 1; i < last; i++) {
      let dist = getSqSegDist(points[i], points[first], points[last]);
      if (dist > maxDist) {
        index = i;
        maxDist = dist;
      }
    }
    if (maxDist > epsilon * epsilon) {
      if (index - first > 1) simplifyDPStep(points, first, index, epsilon, simplified);
      simplified.push(points[index]);
      if (last - index > 1) simplifyDPStep(points, index, last, epsilon, simplified);
    }
  };
  
  let last = path.length - 1;
  let simplified = [path[0]];
  simplifyDPStep(path, 0, last, epsilon, simplified);
  simplified.push(path[last]);
  return simplified;
}

// body > main > div.section.featured-article-container > div > div > div.text > h2

export function getIntersectedElements(paths) {
  if (!paths || paths.length === 0) return [];
  
  const intersectedElements = new Set(); // Use Set to avoid duplicates
  
  // Get all DOM elements
  const allElements = document.querySelectorAll('*');
  
  // Helper function to check if a point is inside a polygon
  function isPointInsidePolygon(point, polygon) {
    let inside = false;
    for (let i = 0, j = polygon.length - 1; i < polygon.length; j = i++) {
      const xi = polygon[i].x, yi = polygon[i].y;
      const xj = polygon[j].x, yj = polygon[j].y;
      const intersect = ((yi > point.y) !== (yj > point.y)) &&
        (point.x < (xj - xi) * (point.y - yi) / (yj - yi) + xi);
      if (intersect) inside = !inside;
    }
    return inside;
  }
  
  // Helper function to calculate the area of a polygon
  function polygonArea(polygon) {
    let area = 0;
    for (let i = 0, j = polygon.length - 1; i < polygon.length; j = i++) {
      const xi = polygon[i][0], yi = polygon[i][1];
      const xj = polygon[j][0], yj = polygon[j][1];
      area += (xj + xi) * (yj - yi);
    }
    return Math.abs(area / 2);
  }
  
  // Helper function to get the intersection area of a rectangle and a polygon using polygon-clipping
  function getIntersectionArea(rect, polygon) {
    const { left, right, top, bottom } = rect;
    const rectPolygon = [
      [left, top],
      [right, top],
      [right, bottom],
      [left, bottom],
      [left, top]
    ];
    
    const polygonCoords = polygon.map(point => [point.x, point.y]);
    polygonCoords.push([polygon[0].x, polygon[0].y]); // Close the polygon
    
    const intersection = polygonClipping.intersection([rectPolygon], [polygonCoords]);
    
    if (intersection.length === 0) return 0;
    
    // Calculate the area of the intersection polygon
    return intersection.reduce((totalArea, poly) => totalArea + polygonArea(poly[0]), 0);
  }
  
  // Iterate over each path
  Array.from(paths).forEach(path => {
    // Close the polygon by connecting the last point to the first point
    const polygon = [...path, path[0]];
    
    // Check intersection with each DOM element
    allElements.forEach(element => {
      const rect = element.getBoundingClientRect();
      const boundingBox = {
        left: rect.left + window.scrollX,
        right: rect.right + window.scrollX,
        top: rect.top + window.scrollY,
        bottom: rect.bottom + window.scrollY
      };
      
      const boundingBoxArea = (boundingBox.right - boundingBox.left) * (boundingBox.bottom - boundingBox.top);
      const intersectionArea = getIntersectionArea(boundingBox, polygon);
      
      if (intersectionArea / boundingBoxArea >= 0.5) {
        intersectedElements.add(element); // Use Set to avoid duplicates
      }
    });
  });
  
  return Array.from(intersectedElements); // Convert Set to array
}

export function getSmallestEnclosingElement(elements) {
  if (!elements.length) return null;
  
  // Helper function to check if an element is a descendant of another
  function isDescendant(parent, child) {
    let node = child.parentNode;
    while (node != null) {
      if (node == parent) {
        return true;
      }
      node = node.parentNode;
    }
    return false;
  }
  
  // Iterate through the list of elements to find the smallest enclosing element
  let smallestEnclosingElement = elements[0];
  for (let i = 1; i < elements.length; i++) {
    if (isDescendant(elements[i], smallestEnclosingElement)) {
      smallestEnclosingElement = elements[i];
    } else if (!isDescendant(smallestEnclosingElement, elements[i])) {
      // If elements[i] is not a descendant of smallestEnclosingElement
      // and smallestEnclosingElement is not a descendant of elements[i],
      // we need to find the common ancestor
      let commonAncestor = smallestEnclosingElement.parentNode;
      while (commonAncestor && !isDescendant(commonAncestor, elements[i])) {
        commonAncestor = commonAncestor.parentNode;
      }
      smallestEnclosingElement = commonAncestor;
    }
  }
  
  return smallestEnclosingElement;
}

export async function captureScreenshot(element) {
  try {
    const canvas = await html2canvas(element);
    
    const blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/png'));
    const arrayBuffer = await blob.arrayBuffer();
    return new Uint8Array(arrayBuffer);
    
  } catch (error) {
    throw new Error('Error capturing screenshot: ' + error.message);
  }
}

export async function getElementHtmlWithStyles(element) {
  const essentialCssProperties = [
    "color",
    "background-color",
    "background-image",
    "background-size",
    "font-family",
    "font-size",
    "font-weight",
    "line-height",
    "text-align",
    "text-decoration",
    "text-transform",
    "display",
    "position",
    "top",
    "right",
    "bottom",
    "left",
    "float",
    "clear",
    "margin",
    "padding",
    "border",
    "width",
    "height",
    "box-sizing",
    "flex-direction",
    "justify-content",
    "align-items",
    "flex-wrap",
    "grid-template-columns",
    "grid-template-rows",
    "grid-gap",
    "transition",
    "animation",
    "keyframes",
    "transform",
    "translate",
    "rotate",
    "scale",
    "visibility",
    "opacity",
    "z-index",
    "media queries"
  ];
  
  function getExplicitlySetStyles(element) {
    const originalComputedStyle = window.getComputedStyle(element);
    console.log(originalComputedStyle);
    const explicitlySetStyles = {};
    for (let property of originalComputedStyle) {
      if (essentialCssProperties.includes(property)) {
        explicitlySetStyles[property] = originalComputedStyle.getPropertyValue(property);
      }
    }
    return explicitlySetStyles;
  }
  
  function applyInlineStyles(element) {
    const styles = getExplicitlySetStyles(element);
    console.log(styles);
    let styleString = '';
    for (let property in styles) {
      styleString += `${property}: ${styles[property]}; `;
    }
    element.setAttribute('style', styleString);
    for (let child of element.children) {
      applyInlineStyles(child);
    }
  }
  
  function createStyledClone(element) {
    const clone = element.cloneNode(true);
    applyInlineStyles(clone);
    return clone;
  }
  
  const clonedElement = createStyledClone(element);
  
  // Create a wrapper div to hold the cloned element
  const wrapper = document.createElement('div');
  wrapper.appendChild(clonedElement);
  
  return wrapper.innerHTML;
}
