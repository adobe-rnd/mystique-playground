chrome.action.onClicked.addListener((tab) => {
  chrome.scripting.executeScript({
    target: { tabId: tab.id },
    func: () => {
      const scriptUrl = 'http://localhost:4010/copilot.js';
      const existingScript = document.querySelector(`script[src="${scriptUrl}"]`);
      if (existingScript) {
        window.dispatchEvent(new CustomEvent('toggleCopilot'));
      } else {
        const script = document.createElement('script');
        script.src = scriptUrl;
        script.type = 'text/javascript';
        script.async = true;
        script.crossOrigin = 'anonymous';
        document.head.appendChild(script);
      }
    }
  });
});
