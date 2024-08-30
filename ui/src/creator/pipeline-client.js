// pipelineClient.js
import wretch from 'wretch';

const API_BASE_URL = 'http://localhost:4003';
const api = wretch(API_BASE_URL);

export async function fetchPipelines() {
  try {
    return await api
      .url('/pipelines')
      .get()
      .json();
  } catch (error) {
    console.error('Failed to fetch pipelines:', error);
    return [];
  }
}

export async function fetchPipelineData(pipelineId) {
  if (!pipelineId) return null;
  
  try {
    return await api
      .url(`/pipeline/${pipelineId}`)
      .get()
      .json();
  } catch (error) {
    console.error('Failed to fetch pipeline data:', error);
    return null;
  }
}

export async function fetchStepsData() {
  try {
    return await api
      .url('/pipeline-steps')
      .get()
      .json();
  } catch (error) {
    console.error('Failed to fetch steps data:', error);
    return [];
  }
}
