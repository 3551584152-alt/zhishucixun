import { get } from './request'
export function fetchTodayWords(limit) { return get('/api/words/today', { limit: limit || 30 }) }
export function fetchWord(wordId) { return get('/api/words/' + wordId) }
export function fetchWordList(params) { return get('/api/words', params || {}) }
export function lookupWord(word) { return get('/api/words/lookup', { word }) }