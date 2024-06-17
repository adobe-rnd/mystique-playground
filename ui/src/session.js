import {action, observable} from 'mobx';

class AuthoringSession {
  @observable accessor prompt = '';
  @observable accessor selectedRegions = [];

  @action
  setPrompt(value) {
    console.log('Setting prompt:', value);
    this.prompt = value;
  }
  
  @action
  setSelectedRegions(value) {
    console.log('Setting selection:', value);
    this.selectedRegions = value;
  }
}

export const authoringSession = new AuthoringSession();
