import { get } from './request'
export function fetchSummary() { return get('/api/stats/summary') }