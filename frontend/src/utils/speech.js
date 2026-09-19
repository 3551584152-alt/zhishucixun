// Web Speech API 发音（移植自 CT4项目1.0 utils/speech.js，去掉 uni 依赖）
function canSpeak() {
  try { return typeof window !== 'undefined' && !!window.speechSynthesis } catch (e) { return false }
}
function allVoices() {
  try { return window.speechSynthesis.getVoices() || [] } catch (e) { return [] }
}
function pickVoice(lang) {
  const voices = allVoices()
  const lower = (lang || 'en-US').toLowerCase()
  let hit = voices.find((v) => v.lang && v.lang.toLowerCase() === lower)
  if (hit) return hit
  const prefix = lower.split('-')[0] + '-'
  hit = voices.find((v) => v.lang && v.lang.toLowerCase().indexOf(prefix) === 0)
  return hit || null
}
function speakWith(text, lang) {
  const content = (text || '').trim()
  if (!content) return false
  if (canSpeak()) {
    try {
      window.speechSynthesis.cancel()
      const u = new SpeechSynthesisUtterance(content)
      u.lang = lang || 'en-US'
      u.rate = 0.8
      u.pitch = 1
      const v = pickVoice(u.lang)
      if (v) u.voice = v
      window.speechSynthesis.speak(u)
      return true
    } catch (e) { /* ignore */ }
  }
  return false
}
export function speak(text) { return speakWith(text, 'en-US') }
export function speakUK(text) { return speakWith(text, 'en-GB') }
export function speakUS(text) { return speakWith(text, 'en-US') }
export function speakSentence(text, lang) { return speakWith(text, lang || 'en-US') }
export default { speak, speakUK, speakUS, speakSentence }