export function selectBlock() {
  return new Promise((resolve) => {
    function addHighlight(event) {
      event.stopPropagation();
      event.preventDefault();
      const blockElement = event.target.closest('.block');
      if (!blockElement || !blockElement.classList) {
        return;
      }
      blockElement.classList.add('highlight');
    }
    
    function removeHighlight(event) {
      event.stopPropagation();
      event.preventDefault();
      const blockElement = event.target.closest('.block');
      if (!blockElement || !blockElement.classList) {
        return;
      }
      blockElement.classList.remove('highlight');
    }
    
    function handleSelection(event) {
      event.stopPropagation();
      event.preventDefault();
      const blockElement = event.target.closest('.block');
      if (!blockElement) {
        return;
      }
      removeEventListeners();
      document.querySelector('.highlight')?.classList.remove('highlight');
      resolve(blockElement);
    }
    
    function cancelSelection(event) {
      if (event.key === 'Escape') {
        removeEventListeners();
        document.querySelector('.highlight')?.classList.remove('highlight');
        resolve(null);
      }
    }
    
    function removeEventListeners() {
      document.removeEventListener('mouseover', addHighlight, true);
      document.removeEventListener('mouseout', removeHighlight, true);
      document.removeEventListener('click', handleSelection, true);
      document.removeEventListener('keydown', cancelSelection, true);
    }
    
    document.addEventListener('mouseover', addHighlight, true);
    document.addEventListener('mouseout', removeHighlight, true);
    document.addEventListener('click', handleSelection, true);
    document.addEventListener('keydown', cancelSelection, true);
  });
}

export function selectElement() {
  console.log('Selecting element...');
  return new Promise((resolve) => {
    const overlay = document.createElement('webgl-overlay');
    overlay.onDone = (selectedElement) => {
      console.log('Selected element1:', selectedElement);
      resolve(selectedElement);
      overlay.remove();
    };
    document.body.append(overlay);
  });
}
