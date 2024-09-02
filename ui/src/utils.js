import html2canvas from 'html2canvas';
import * as polygonClipping from 'polygon-clipping';
import {isElementPositionedOverContent, isElementVisible} from './dom';

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
      if (!isElementVisible(element)) return;
      if (isElementPositionedOverContent(element)) return;
      if (element === document.body) return;
      if (element.style.opacity === '0') return;
      if (element.style.zIndex === '-1') return;
      if (element.style.pointerEvents === 'none') return;
      if (element.style.position === 'fixed') return;
      if (element.style.position === 'absolute') return;
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

export async function captureScreenshot(element, maxWidth = 214, maxHeight = 214) {
  try {
    const canvas = await html2canvas(element);
    let originalWidth = canvas.width;
    let originalHeight = canvas.height;
    
    // Calculate the scaling factor while maintaining the aspect ratio
    let scale = Math.min(maxWidth / originalWidth, maxHeight / originalHeight);
    
    // Set the scaled width and height
    let scaledWidth = originalWidth * scale;
    let scaledHeight = originalHeight * scale;
    
    // Create a new canvas to draw the scaled image
    const scaledCanvas = document.createElement('canvas');
    scaledCanvas.width = scaledWidth;
    scaledCanvas.height = scaledHeight;
    const ctx = scaledCanvas.getContext('2d');
    
    // Draw the scaled image on the new canvas
    ctx.drawImage(canvas, 0, 0, scaledWidth, scaledHeight);
    
    const blob = await new Promise(resolve => scaledCanvas.toBlob(resolve, 'image/png'));
    const arrayBuffer = await blob.arrayBuffer();
    return new Uint8Array(arrayBuffer);
    
  } catch (error) {
    throw new Error('Error capturing screenshot: ' + error.message);
  }
}

export function syntaxHighlightJson(json) {
  if (typeof json != 'string') {
    json = JSON.stringify(json, undefined, 2);
  }
  json = json.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  return json.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, function (match) {
    let style = 'color: #795548;'; // Muted brown for numbers
    if (/^"/.test(match)) {
      if (/:$/.test(match)) {
        style = 'color: #00897b;'; // Teal for keys
      } else {
        style = 'color: #388e3c;'; // Green for strings
      }
    } else if (/true|false/.test(match)) {
      style = 'color: #1976d2;'; // Blue for booleans
    } else if (/null/.test(match)) {
      style = 'color: #f57c00;'; // Orange for null
    }
    return '<span style="' + style + '">' + match + '</span>';
  });
}
