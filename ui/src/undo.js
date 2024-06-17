import { observable, action, computed } from 'mobx';
import { authoringSession } from './session';

class UndoEntry {
  constructor(undo, prompt, selectedRegions) {
    this.undo = undo;
    this.prompt = prompt;
    this.selectedRegions = selectedRegions;
  }
}

class UndoManager {
  @observable accessor entries = [];
  
  @action addEntry(undoCode, prompt, selectedRegions) {
    console.log(`[B] Adding entry, Can Undo: ${this.canUndo}`);
    this.entries.push(new UndoEntry(undoCode, prompt, selectedRegions));
    console.log(`[A] Adding entry, Can Undo: ${this.canUndo}`);
  }
  
  @computed get canUndo() {
    return this.entries.length > 0;
  }
  
  @action undo() {
    if (this.canUndo) {
      console.log(`[B] Undoing, Can Undo: ${this.canUndo}`);
      const entry = this.entries.pop();
      this.executeCode(entry.undo);
      authoringSession.setPrompt(entry.prompt);
      authoringSession.setSelectedRegions(entry.selectedRegions)
      console.log(`[A] Undoing, Can Undo: ${this.canUndo}`);
    }
  }
  
  executeCode(code) {
    try {
      console.log('Executing code:', code);
      const func = new Function(code);
      func();
    } catch (error) {
      console.error('Error executing code:', error);
    }
  }
}

export const undoManager = new UndoManager();
