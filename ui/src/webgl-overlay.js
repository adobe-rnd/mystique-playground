import {customElement, property, state} from 'lit/decorators.js';
import { ref, createRef } from 'lit/directives/ref.js';
import { css, html, LitElement } from 'lit';
import {
  calculateDistance, getIntersectedElements, getSmallestEnclosingElement,
  optimizePath
} from './utils';
import { mat4 } from 'gl-matrix';

const DASH_ANIMATION_SPEED = 25;

@customElement('webgl-overlay')
class WebglOverlay extends LitElement {
  static styles = css`
    #overlayCanvas {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      pointer-events: none;
      z-index: 1000;
      background-color: rgba(255, 255, 255, 0);
    }
    .interactive {
      pointer-events: auto !important;
    }
  `;
  
  @property() accessor onDone = (e) => {};
  
  @state() accessor interactive = true;
  @state() accessor lineWidth = 3;
  
  selectedRegions = [];
  
  canvasRef = createRef();
  gl = null;
  drawing = false;
  startX = 0;
  startY = 0;
  currentPath = [];
  shaderProgram = null;
  dashOffsetUniform = null;
  lineWidthUniform = null;
  colorUniform = null;
  projectionMatrixUniform = null;
  positionBuffer = null;
  offsetBuffer = null;
  lengthBuffer = null;
  indexBuffer = null;
  
  firstUpdated() {
    this.updateCanvasSize();
    const canvas = this.canvasRef.value;
    if (canvas) {
      this.gl = canvas.getContext('webgl');
      if (!this.gl) {
        console.error('WebGL not supported');
        return;
      }
      this.initWebGL();
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
      if (this.gl) {
        this.gl.viewport(0, 0, width, height);
      }
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
      this.selectedRegions = [...this.selectedRegions, optimizedPath];
      if (!event.shiftKey) {
        const selectedElements = getIntersectedElements(this.selectedRegions);
        console.log('Selected elements:', selectedElements);
        const selectedElement = selectedElements.length > 0 ? getSmallestEnclosingElement(selectedElements) : null;
        console.log('Selected element:', selectedElement);
        this.onDone(selectedElement);
      }
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
  
  initWebGL() {
    const gl = this.gl;
    if (!gl) return;
    
    // Vertex shader program
    const vsSource = `
      attribute vec2 aVertexPosition;
      attribute vec2 aVertexOffset;
      attribute float aLength;
      uniform float uLineWidth;
      uniform mat4 uProjectionMatrix;
      varying float vLength;
      varying vec2 vTexCoord;
    
      void main(void) {
        vec2 offset = aVertexOffset * uLineWidth / 2.0;
        vec2 position = aVertexPosition + offset;
        gl_Position = uProjectionMatrix * vec4(position, 0.0, 1.0);
        vTexCoord = aVertexOffset;
        vLength = aLength;
      }
    `;
    
    // Fragment shader program
    const fsSource = `
      precision mediump float;
      varying vec2 vTexCoord;
      varying float vLength;
      uniform vec4 uColor;
      uniform float uDashOffset;

      void main(void) {
        float dashSize = 10.0;
        float gapSize = 10.0;
        float totalSize = dashSize + gapSize;
        float pattern = mod(vLength + uDashOffset, totalSize);
        
        if (pattern > dashSize) {
          gl_FragColor = vec4(1.0, 0.0, 0.0, 1.0);
        } else {
          gl_FragColor = vec4(1.0, 1.0, 1.0, 1.0);
        }
      }
    `;
    
    // Initialize shaders
    const vertexShader = this.loadShader(gl, gl.VERTEX_SHADER, vsSource);
    const fragmentShader = this.loadShader(gl, gl.FRAGMENT_SHADER, fsSource);
    
    // Create the shader program
    const shaderProgram = gl.createProgram();
    if (shaderProgram && vertexShader && fragmentShader) {
      gl.attachShader(shaderProgram, vertexShader);
      gl.attachShader(shaderProgram, fragmentShader);
      gl.linkProgram(shaderProgram);
      
      if (!gl.getProgramParameter(shaderProgram, gl.LINK_STATUS)) {
        console.error('Unable to initialize the shader program: ' + gl.getProgramInfoLog(shaderProgram));
        return;
      }
      
      this.shaderProgram = shaderProgram;
      gl.useProgram(shaderProgram);
      
      // Look up the location of the attribute and uniforms
      const vertexPosition = gl.getAttribLocation(shaderProgram, 'aVertexPosition');
      const vertexOffset = gl.getAttribLocation(shaderProgram, 'aVertexOffset');
      const vertexLength = gl.getAttribLocation(shaderProgram, 'aLength'); // Added length attribute
      this.lineWidthUniform = gl.getUniformLocation(shaderProgram, 'uLineWidth'); // Line width uniform
      this.colorUniform = gl.getUniformLocation(shaderProgram, 'uColor'); // Color uniform
      this.dashOffsetUniform = gl.getUniformLocation(shaderProgram, 'uDashOffset'); // Dash offset uniform
      this.projectionMatrixUniform = gl.getUniformLocation(shaderProgram, 'uProjectionMatrix'); // Projection matrix uniform
      
      // Enable the vertex attribute array
      gl.enableVertexAttribArray(vertexPosition);
      gl.enableVertexAttribArray(vertexOffset);
      gl.enableVertexAttribArray(vertexLength); // Enable the length attribute
      
      // Create buffers
      this.positionBuffer = gl.createBuffer();
      this.offsetBuffer = gl.createBuffer();
      this.lengthBuffer = gl.createBuffer(); // Added length buffer
      this.indexBuffer = gl.createBuffer(); // Added index buffer
    }
  }
  
  loadShader(gl, type, source) {
    const shader = gl.createShader(type);
    if (!shader) return null;
    
    gl.shaderSource(shader, source);
    gl.compileShader(shader);
    
    if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
      console.error('An error occurred compiling the shaders: ' + gl.getShaderInfoLog(shader));
      gl.deleteShader(shader);
      return null;
    }
    
    return shader;
  }
  
  redraw() {
    const gl = this.gl;
    if (!gl) return;
    
    gl.clear(gl.COLOR_BUFFER_BIT);
    
    const vertices = [];
    const offsets = [];
    const lengths = [];
    const indices = [];
    let vertexIndex = 0;
    
    const addVertex = (x, y, offsetX, offsetY, length) => {
      vertices.push(x, y);
      offsets.push(offsetX, offsetY);
      lengths.push(length);
      vertexIndex++;
    };
    
    const addPath = (path) => {
      let length = 0.0;
      for (let i = 0; i < path.length - 1; i++) {
        const start = path[i];
        const end = path[i + 1];
        
        const dx = end.x - start.x;
        const dy = end.y - start.y;
        const segmentLength = Math.sqrt(dx * dx + dy * dy);
        const ux = dy / segmentLength;
        const uy = -dx / segmentLength;
        
        addVertex(start.x, start.y, ux, uy, length);
        addVertex(start.x, start.y, -ux, -uy, length);
        length += segmentLength;
        addVertex(end.x, end.y, ux, uy, length);
        addVertex(end.x, end.y, -ux, -uy, length);
        
        indices.push(vertexIndex - 4, vertexIndex - 3, vertexIndex - 2);
        indices.push(vertexIndex - 3, vertexIndex - 2, vertexIndex - 1);
      }
    };
    
    // Add selected regions
    this.selectedRegions.forEach(addPath);
    
    // Add current path
    if (this.currentPath.length > 0) {
      addPath(this.currentPath);
    }
    
    // Convert vertex data to Float32Array and bind to buffer
    const vertexData = new Float32Array(vertices);
    const offsetData = new Float32Array(offsets);
    const lengthData = new Float32Array(lengths);
    const indexData = new Uint16Array(indices);
    
    // Bind position buffer
    gl.bindBuffer(gl.ARRAY_BUFFER, this.positionBuffer);
    gl.bufferData(gl.ARRAY_BUFFER, vertexData, gl.STREAM_DRAW);
    gl.vertexAttribPointer(gl.getAttribLocation(this.shaderProgram, 'aVertexPosition'), 2, gl.FLOAT, false, 0, 0);
    
    // Bind offset buffer
    gl.bindBuffer(gl.ARRAY_BUFFER, this.offsetBuffer);
    gl.bufferData(gl.ARRAY_BUFFER, offsetData, gl.STREAM_DRAW);
    gl.vertexAttribPointer(gl.getAttribLocation(this.shaderProgram, 'aVertexOffset'), 2, gl.FLOAT, false, 0, 0);
    
    // Bind length buffer
    gl.bindBuffer(gl.ARRAY_BUFFER, this.lengthBuffer);
    gl.bufferData(gl.ARRAY_BUFFER, lengthData, gl.STREAM_DRAW);
    gl.vertexAttribPointer(gl.getAttribLocation(this.shaderProgram, 'aLength'), 1, gl.FLOAT, false, 0, 0);
    
    // Bind index buffer
    gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, this.indexBuffer);
    gl.bufferData(gl.ELEMENT_ARRAY_BUFFER, indexData, gl.STREAM_DRAW);
    
    // Set the dash offset, line width, and color uniform
    gl.uniform1f(this.lineWidthUniform, this.lineWidth); // Bind the line width uniform
    gl.uniform4f(this.colorUniform, 1.0, 0.0, 0.0, 1.0); // Set line color to red
    gl.uniform1f(this.dashOffsetUniform, performance.now() / 1000 * DASH_ANIMATION_SPEED); // Bind the dash offset uniform
    
    // Set the projection matrix
    const projectionMatrix = mat4.create();
    mat4.ortho(projectionMatrix, 0, gl.canvas.width, gl.canvas.height, 0, -1, 1);
    gl.uniformMatrix4fv(this.projectionMatrixUniform, false, projectionMatrix);
    
    // Draw the lines
    gl.drawElements(gl.TRIANGLES, indexData.length, gl.UNSIGNED_SHORT, 0);
  }
  
  animate() {
    const step = () => {
      this.redraw();
      requestAnimationFrame(step);
    };
    
    requestAnimationFrame(step);
  }
  
  clearOverlay() {
    this.selectedRegions = [];
    this.currentPath = [];
    if (this.gl) {
      this.gl.clear(this.gl.COLOR_BUFFER_BIT);
    }
  }
  
  render() {
    return html`
      <canvas id="overlayCanvas" class=${this.interactive ? 'interactive' : ''} ${ref(this.canvasRef)}></canvas>
    `;
  }
}
