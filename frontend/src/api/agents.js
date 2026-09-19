import { post } from './request'
export function askPlanner(remainingDays) { return post('/api/agents/plan', { remaining_days: remainingDays || 0 }) }
export function askTutor(wordId, word) {
  const payload = {}
  if (wordId) payload.word_id = wordId
  if (word) payload.word = word
  return post('/api/agents/tutor', payload)
}
export function askTrain(options) {
  return post('/api/agents/train', {
    topic: options.topic || 'read',
    word_id: options.word_id || null,
    word: options.word || null,
    stubborn_only: !!options.stubborn_only,
    count: options.count || 4
  })
}
export function askAnalyze(wordId, word) {
  const payload = {}
  if (wordId) payload.word_id = wordId
  if (word) payload.word = word
  return post('/api/agents/analyze', payload)
}