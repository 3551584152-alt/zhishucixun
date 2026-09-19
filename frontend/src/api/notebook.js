import { get } from './request'
export function fetchWrong(limit) { return get('/api/notebook/wrong', { limit: limit || 200 }) }
export function fetchStubborn(limit) { return get('/api/notebook/stubborn', { limit: limit || 200 }) }
export function fetchNotebookSummary() { return get('/api/notebook/summary') }