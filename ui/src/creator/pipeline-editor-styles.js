// pipeline-editor-styles.js
import { css } from 'lit';

export const pipelineEditorStyles = css`
  #editorWrapper {
    display: grid;
    grid-template-rows: auto 1fr;
    gap: 10px;
    width: 100%;
    height: 100%;
  }

  #controls {
    display: flex;
    gap: 10px;
    align-items: center;
    margin-bottom: 10px;
  }

  #mainEditor {
    display: grid;
    grid-template-columns: 1fr 250px;
    gap: 20px;
    height: 100%;
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
