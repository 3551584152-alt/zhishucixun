import { post } from './request'
export function requestExample(wordId, word) {
  const payload = {}
  if (wordId) payload.word_id = wordId
  if (word) payload.word = word
  return post('/api/ai/example', payload)
}