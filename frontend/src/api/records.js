import { post } from './request'
export function submitRecord(payload) { return post('/api/records', payload) }
export function syncRecords(records) { return post('/api/records/sync', { records }) }