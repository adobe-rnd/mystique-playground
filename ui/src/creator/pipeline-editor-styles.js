// pipeline-editor-styles.js
import { css } from 'lit';

export const pipelineEditorStyles = css`
  #mainEditor {
    display: grid;
    grid-template-columns: 1fr 250px;
    gap: 20px;
    height: 100%;
    transition: grid-template-columns 0.3s ease; /* Smooth transition */
  }

  #mainEditor.expanded {
    grid-template-columns: 1fr 0; /* Expand the main editor to full width when side rail is collapsed */
  }

  #sideRail {
    width: 250px; /* Default width */
    transition: width 0.3s ease, opacity 0.3s ease;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    position: relative;
    opacity: 1; /* Fully visible */
  }

  #sideRail.collapsed {
    width: 0; /* Collapsed width */
    opacity: 0; /* Make content invisible when collapsed */
  }

  #collapseButton {
  }

  #controls {
    display: flex;
    gap: 10px;
    align-items: center;
    margin-bottom: 10px;
  }

  #editor-container {
    border-radius: 5px;
    position: relative;
    height: 600px;
    overflow: hidden;
    border: 2px dashed #ccc;
  }

  #editor-container.drag-over {
    border-color: blue;
  }

  .progress-container,
  .center-message {
    display: flex;
    justify-content: center;
    align-items: center;
    width: 100%;
    height: 100%;
  }

  .warning {
    color: red;
    font-size: 14px;
    margin-top: 10px;
  }

  .icon {
    font-size: 48px;
    color: #888;
    margin-bottom: 10px;
  }
`;
