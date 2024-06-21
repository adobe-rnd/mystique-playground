import { customElement, state } from 'lit/decorators.js';
import { ref, createRef } from 'lit/directives/ref.js';
import { css, html } from 'lit';
import {
  calculateDistance,
  getIntersectedElements,
  getSmallestEnclosingElement, optimizePath
} from './utils';
import {MobxLitElement} from '@adobe/lit-mobx';
import {appSettings}from './settings';
import {authoringSession} from './session';

@customElement('interactive-overlay')
export class InteractiveOverlay extends MobxLitElement {
  static styles = css`
    #overlayCanvas {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      pointer-events: none; /* Initially transparent to events */
      z-index: 1000;
      background-color: rgba(255, 255, 255, 0);
    }
    .interactive {
      pointer-events: auto !important; /* Make it interactive */
    }
  `;
  
  @state() accessor interactive = true;
  
  canvasRef = createRef();
  drawing = false;
  startX = 0;
  startY = 0;
  dashOffset = 0;
  currentPath = []; // Array to store the current path
  
  firstUpdated() {
    this.updateCanvasSize();
    const canvas = this.canvasRef.value;
    if (canvas) {
      window.addEventListener('resize', () => this.updateCanvasSize());
      window.addEventListener('scroll', () => this.updateCanvasSize());
      canvas.addEventListener('mousedown', (event) => this.startDrawing(event));
      canvas.addEventListener('mousemove', (event) => this.draw(event));
      canvas.addEventListener('mouseup', (event) => this.stopDrawing(event));
      canvas.addEventListener('mouseout', (event) => this.stopDrawing(event));
      this.animate();
    }
  }
  
  updateCanvasSize() {
    const canvas = this.canvasRef.value;
    if (canvas) {
      const width = Math.max(document.documentElement.clientWidth, document.documentElement.scrollWidth);
      const height = Math.max(document.documentElement.clientHeight, document.documentElement.scrollHeight);
      canvas.width = width;
      canvas.height = height;
      canvas.style.width = `${width}px`;
      canvas.style.height = `${height}px`;
    }
  }
  
  toggleCanvas() {
    this.interactive = !this.interactive;
    this.clearOverlay();
  }
  
  startDrawing(event) {
    if (!this.interactive) return;
    if (!event.shiftKey) {
      this.clearOverlay();
    }
    this.drawing = true;
    const canvas = this.canvasRef.value;
    const canvasRect = canvas.getBoundingClientRect();
    this.startX = event.clientX - canvasRect.left;
    this.startY = event.clientY - canvasRect.top;
    this.currentPath = [{ x: this.startX, y: this.startY }];
  }
  
  stopDrawing(event) {
    if (!this.interactive) return;
    this.drawing = false;
    if (this.currentPath.length > 0) {
      const optimizedPath = optimizePath(this.currentPath);
      authoringSession.setSelectedRegions([...authoringSession.selectedRegions, optimizedPath]);
    }
    this.currentPath = [];

    this.redraw();
  }
  
  draw(event) {
    if (!this.drawing || !this.interactive) return;
    const canvas = this.canvasRef.value;
    const canvasRect = canvas.getBoundingClientRect();
    const x = event.clientX - canvasRect.left;
    const y = event.clientY - canvasRect.top;
    
    if (this.currentPath.length > 0) {
      const lastPoint = this.currentPath[this.currentPath.length - 1];
      const distance = calculateDistance(lastPoint, { x, y });
      if (distance < 10) return;
    }
    
    this.currentPath.push({ x, y });
    
    this.redraw();
  }
  
  redraw() {
    const canvas = this.canvasRef.value;
    const context = canvas.getContext('2d');
    context.clearRect(0, 0, canvas.width, canvas.height);
    
    authoringSession.selectedRegions.forEach(path => {
      this.drawPath(context, path);
      this.drawPath(context, path, 'white', 3, 10);
    });
    
    if (this.currentPath.length > 0) {
      this.drawPath(context, this.currentPath);
      this.drawPath(context, this.currentPath, 'white', 3, 10);
    }
    
    if (appSettings.isDisplayingDebuggingInfo) {
      const selectedElements = getIntersectedElements([...authoringSession.selectedRegions, this.currentPath].filter(path => path.length > 0));
      const enclosingElement = getSmallestEnclosingElement(selectedElements);
      if (enclosingElement) {
        this.drawElements(context, selectedElements, 'rgba(0, 128, 0, 0.6)');
        this.drawElements(context, [enclosingElement], 'rgba(0, 0, 255, 0.6)');
      }
    }
  }
  
  animate() {
    let lastTimestamp = 0;
    
    const step = (timestamp) => {
      if (lastTimestamp) {
        const elapsed = timestamp - lastTimestamp;
        this.dashOffset -= (elapsed * 0.02);
      }
      lastTimestamp = timestamp;
      
      this.redraw();
      
      requestAnimationFrame(step);
    };
    
    requestAnimationFrame(step);
  }
  
  clearOverlay() {
    const canvas = this.canvasRef.value;
    const context = canvas.getContext('2d');
    context.clearRect(0, 0, canvas.width, canvas.height);
    authoringSession.setSelectedRegions([]);
    this.currentPath = [];
  }
  
  drawPath(context, path, color = 'red', lineWidth = 3, dashOffset = 0) {
    context.strokeStyle = color;
    context.lineWidth = lineWidth;
    context.setLineDash([10, 10]);
    context.lineDashOffset = this.dashOffset + dashOffset;

    context.beginPath();
    if (path.length > 0) {
      context.moveTo(path[0].x, path[0].y);
      for (let i = 1; i < path.length; i++) {
        context.lineTo(path[i].x, path[i].y);
      }
    }
    context.stroke();
  }
  
  drawElements(context, elements, color, lineWidth = 1) {
    elements.forEach(element => {
      const rect = element.getBoundingClientRect();
      const canvasRect = this.canvasRef.value.getBoundingClientRect();
      context.strokeStyle = color;
      context.lineWidth = lineWidth;
      context.setLineDash([10, 2]);
      context.strokeRect(rect.left - canvasRect.left, rect.top - canvasRect.top, rect.width, rect.height);
    });
  }
  
  render() {
    return html`
      <canvas id="overlayCanvas" class=${this.interactive ? 'interactive' : ''} ${ref(this.canvasRef)}></canvas>
    `;
  }
}
