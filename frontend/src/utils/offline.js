// 简易离线缓存（localStorage 实现，接口对齐 1.0 utils/offline.js，便于页面复用）
const KEY_TODAY = 'ct4_off_today'
const KEY_QUEUE = 'ct4_off_queue'
const KEY_STATES = 'ct4_off_states'

function read(k, d) { try { return JSON.parse(localStorage.getItem(k)) || d } catch (e) { return d } }
function write(k, v) { localStorage.setItem(k, JSON.stringify(v)) }

export default {
  async init() {
    write(KEY_QUEUE, read(KEY_QUEUE, []))
    write(KEY_STATES, read(KEY_STATES, {}))
  },
  async replaceToday(items) {
    write(KEY_TODAY, { items: items || [], savedAt: new Date().toISOString() })
  },
  async dueWords() {
    const today = read(KEY_TODAY, { items: [] })
    const states = read(KEY_STATES, {})
    const now = Date.now()
    return (today.items || []).filter((w) => {
      if (w.is_new) return true
      const st = states[w.id]
      if (!st) return false
      return st.next_review_at && new Date(st.next_review_at).getTime() <= now
    })
  },
  async queueList() {
    const q = read(KEY_QUEUE, [])
    return q.map((x, i) => ({ id: x.id || ('q' + i), payload: x.payload }))
  },
  async queueAdd(payload) {
    const q = read(KEY_QUEUE, [])
    q.push({ id: 'q' + Date.now() + Math.random().toString(36).slice(2, 6), payload })
    write(KEY_QUEUE, q)
  },
  async queueRemove(ids) {
    const q = read(KEY_QUEUE, [])
    write(KEY_QUEUE, q.filter((x) => ids.indexOf(x.id) < 0))
  },
  async updateFromPlan(wordId, plan) {
    const states = read(KEY_STATES, {})
    states[wordId] = { stage: plan.stage, interval_minutes: plan.interval_minutes, next_review_at: plan.next_review_at, lapses: plan.lapses }
    write(KEY_STATES, states)
  },
  async markReviewedLocal(wordId) {
    const states = read(KEY_STATES, {})
    states[wordId] = states[wordId] || {}
    states[wordId].reviewed = true
    write(KEY_STATES, states)
  },
  async summary() {
    const states = read(KEY_STATES, {})
    const learned = Object.keys(states).length
    const q = read(KEY_QUEUE, [])
    return { learned, pending: q.length }
  }
}