import { get } from './request'
export function fetchDailyPlan(date, refresh) { return get('/api/plan/daily', { date: date || '', refresh: refresh ? 1 : 0 }) }