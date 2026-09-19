<template>
  <div class="page">
    <ct4-header :title="headerTitle" :sub="headerSub">
      <template #right>
        <button class="hdr-link" @click="$router.push('/dict')">词典</button>
        <button class="hdr-link" @click="$router.push('/plan')">计划</button>
        <button class="hdr-link" @click="loadWords">刷新</button>
      </template>
      <div class="seg">
        <button :class="['seg-item', flow === 'learn' ? 'on' : '']" @click="switchFlow('learn')">背诵</button>
        <button :class="['seg-item', flow === 'practice' ? 'on' : '']" @click="switchFlow('practice')">练习测试</button>
      </div>
    </ct4-header>

    <!-- ============ 背诵 ============ -->
    <template v-if="flow === 'learn'">
      <div v-if="loading" class="center">加载中…</div>

      <div v-else-if="finished" class="center empty">
        <svg class="empty-symbol" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.1V12a10 10 0 1 1-5.9-9.1"/><path d="M22 4 12 14l-3-3"/></svg>
        <div class="empty-title">今日背诵完成</div>
        <div class="empty-sub">可切换到「练习测试」巩固，或去“词典 · 词库”挑词</div>
        <div class="empty-actions">
          <button class="btn ghost" @click="switchFlow('practice')">去做练习</button>
          <button class="btn" @click="loadWords">重新获取</button>
        </div>
      </div>

      <div v-else class="learn">
        <div class="progress">
          <span class="progress-text">今日剩余 {{ list.length - index }} 词</span>
          <span class="progress-text strong">{{ progressPercent }}%</span>
        </div>
        <div class="progress-bar"><div class="progress-inner" :style="{ width: progressPercent + '%' }"></div></div>

        <div class="card flash">
          <div class="flash-top">
            <span :class="['chip', current.is_new ? 'blue' : 'orange']">{{ current.is_new ? '新词' : '复习' }}</span>
            <span v-if="!current.is_new" class="chip gray">保持率 {{ retentionPercent }}%</span>
            <span class="chip gray">难度 {{ current.difficulty || 2 }}</span>
          </div>

          <div class="word">{{ current.word }}</div>

          <div class="meta">
            <span class="phonetic">{{ current.phonetic }}</span>
            <span class="pos">{{ current.pos }}</span>
            <span class="voice-links">
              <button class="voice-link" title="英式发音" @click="speakUK">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="M11 5 6 9H2v6h4l5 4V5z"/><path d="M15.5 8.8a4.6 4.6 0 0 1 0 6.4"/></svg>
                英音
              </button>
              <button class="voice-link" title="美式发音" @click="speakUS">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="M11 5 6 9H2v6h4l5 4V5z"/><path d="M15.5 8.8a4.6 4.6 0 0 1 0 6.4"/></svg>
                美音
              </button>
            </span>
          </div>

          <div v-if="current.freq_read !== undefined" class="freq">
            <span>阅读 <strong>{{ current.freq_read }}</strong></span>
            <span>听力 <strong>{{ current.freq_listen }}</strong></span>
            <span>翻译 <strong>{{ current.freq_translate }}</strong></span>
            <span>写作 <strong>{{ current.freq_write }}</strong></span>
          </div>

          <div v-if="showMeaning" class="meaning">
            <div class="meaning-text">{{ current.meaning }}</div>
            <div v-if="current.example" class="example">
              <div class="example-en">{{ current.example }}</div>
              <div v-if="current.example_cn" class="example-cn">{{ current.example_cn }}</div>
              <button class="listen-line" @click="speakExample">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="M11 5 6 9H2v6h4l5 4V5z"/><path d="M15.5 8.8a4.6 4.6 0 0 1 0 6.4"/></svg>
                朗读例句
              </button>
            </div>
            <div v-if="current.synonyms && current.synonyms.length" class="syn">
              <span class="syn-label">近义</span>{{ current.synonyms.join('、') }}
            </div>
          </div>
          <button v-else class="reveal" @click="reveal">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
            轻点显示释义与例句
          </button>

          <div class="actions">
            <button class="grade forget" @click="mark(1)">忘记了</button>
            <button class="grade blur" @click="mark(3)">模糊</button>
            <button class="grade know" @click="mark(5)">认识</button>
          </div>
          <div class="action-hint">答对后复习间隔自动拉长，答错会安排重学（艾宾浩斯）</div>
        </div>

        <!-- AI 例句 -->
        <div class="card panel">
          <div class="panel-head">
            <span class="panel-title">AI 例句</span>
            <button class="panel-link" @click="loadAiExample">{{ aiLoading ? '生成中…' : '换一批' }}</button>
          </div>
          <div v-if="aiLoading" class="panel-body muted small">正在生成例句…</div>
          <div v-else-if="aiExamples.length" class="panel-body">
            <div v-for="(item, i) in aiExamples" :key="i" class="ex-item">
              <div class="ex-en">{{ item.en }}</div>
              <div v-if="item.cn" class="ex-cn">{{ item.cn }}</div>
            </div>
            <div v-if="aiNote" class="panel-note">{{ aiNote }}</div>
          </div>
          <div v-else class="panel-body muted small">暂无例句，点右上角“换一批”生成</div>
        </div>

        <!-- 词汇辅导 -->
        <div class="card panel">
          <div class="panel-head">
            <span class="panel-title">词汇辅导</span>
            <button class="panel-link" @click="toggleTutor">{{ tutorOpen ? '收起' : '讲解' }}</button>
          </div>
          <div v-if="tutorOpen" class="panel-body">
            <div v-if="tutorLoading" class="muted small">正在生成讲解…</div>
            <div v-else-if="tutor">
              <div class="tutor-sec">
                <span class="tutor-label">释义 / 讲解</span>
                <div class="tutor-text">{{ tutor.explanation || tutor.meaning }}</div>
              </div>
              <div v-if="tutor.mnemonic" class="tutor-sec">
                <span class="tutor-label">联想记忆</span>
                <div class="tutor-text">{{ tutor.mnemonic }}</div>
              </div>
              <div v-if="tutor.collocations && tutor.collocations.length" class="tutor-sec">
                <span class="tutor-label">搭配</span>
                <div class="tag-wrap"><span v-for="(x, i) in tutor.collocations" :key="i" class="chip gray">{{ x }}</span></div>
              </div>
              <div v-if="tutor.confusable && tutor.confusable.length" class="tutor-sec">
                <span class="tutor-label">易混词</span>
                <div class="tag-wrap"><span v-for="(x, i) in tutor.confusable" :key="i" class="chip gray">{{ x }}</span></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- ============ 练习测试 ============ -->
    <template v-else>
      <div class="seg ptype-seg">
        <button v-for="m in practiceModes" :key="m.key" :class="['seg-item', practiceMode === m.key ? 'on' : '']" @click="switchPracticeMode(m.key)">{{ m.label }}</button>
      </div>

      <div v-if="qFinished" class="score-card card">
        <div class="score-num">{{ accuracy }}<span class="pct">%</span></div>
        <div class="score-sub">答对 {{ qCorrect }} / {{ qAnswered }} · 已完成一组练习</div>
        <div class="score-actions">
          <button class="btn ghost" @click="switchFlow('learn')">返回背诵</button>
          <button class="btn" @click="restartPractice()">再来一组</button>
        </div>
      </div>

      <div v-else-if="list.length" class="quiz">
        <div class="quiz-head">
          <span>{{ practiceModeObj.label }} · {{ qIndex + 1 }}/{{ list.length }}</span>
          <span class="q-score">正确率 {{ accuracy }}%</span>
        </div>
        <div class="card question-card">
          <div class="q-badge-row"><span class="chip blue">{{ practiceModeObj.label }}</span></div>

          <template v-if="practiceMode === 'chant'">
            <div class="q-listen">
              <button class="listen-play" @click="speakQ">
                <svg viewBox="0 0 24 24" fill="currentColor"><path d="M9 7.2v9.6a.6.6 0 0 0 .92.5l7.2-4.8a.6.6 0 0 0 0-1l-7.2-4.8a.6.6 0 0 0-.92.5z"/></svg>
              </button>
              <div class="q-meta">听读音，选择对应的释义</div>
            </div>
          </template>
          <template v-else>
            <div :class="['q-stem', practiceMode === 'c2e' || practiceMode === 'spell' ? 'cn' : '']">{{ qStemText }}</div>
            <div class="q-meta">{{ qMetaText }}</div>
          </template>

          <div v-if="needOptions" class="options">
            <button v-for="opt in options" :key="opt" :class="['option', optionClass(opt)]" @click="choose(opt)">
              <span>{{ opt }}</span>
              <svg v-if="locked && opt === q.answer" class="mk ok" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg>
              <svg v-if="locked && opt === chosen && opt !== q.answer" class="mk no" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round"><path d="M18 6 6 18M6 6l12 12"/></svg>
            </button>
          </div>
          <div v-else class="q-typing">
            <input v-model="q.userInput" class="textfield typing-input" placeholder="输入答案" @keyup.enter="submitTyping" />
            <button class="btn typing-btn" @click="submitTyping">提交</button>
          </div>

          <div v-if="locked" :class="['feedback', lastOk ? 'good' : 'bad']">
            <div class="fb-line">{{ lastOk ? '回答正确' : '正确答案：' + q.answer }}</div>
            <div class="q-explain">{{ q.explanation }}</div>
          </div>
        </div>
      </div>

      <div v-else class="center empty">
        <div class="empty-title">暂无单词</div>
        <div class="empty-sub">先回到「背诵」获取今日单词</div>
        <div class="empty-actions"><button class="btn" @click="switchFlow('learn')">返回背诵</button></div>
      </div>
    </template>
  </div>
</template>

<script>
import Ct4Header from '../components/Ct4Header.vue'
import speech from '../utils/speech'
import uni from '../utils/uni'
import { fetchTodayWords } from '../api/words'
import { submitRecord } from '../api/records'
import { requestExample } from '../api/ai'
import { askTutor } from '../api/agents'

function shuffle(arr) {
  const a = arr.slice()
  for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); const t = a[i]; a[i] = a[j]; a[j] = t }
  return a
}
const PRACTICE_MODES = [
  { key: 'e2c', label: '英译汉', qType: 'choice', topic: 'read' },
  { key: 'c2e', label: '汉译英', qType: 'typing', topic: 'translate' },
  { key: 'spell', label: '拼写', qType: 'typing', topic: 'write' },
  { key: 'chant', label: '诵读', qType: 'choice', topic: 'listen' }
]

export default {
  components: { Ct4Header },
  data() {
    return {
      loading: false, flow: 'learn', practiceModes: PRACTICE_MODES,
      list: [], index: 0, showMeaning: false, finished: false,
      aiExamples: [], aiNote: '', aiLoading: false,
      tutor: null, tutorLoading: false, tutorOpen: false,
      practiceMode: 'e2c', qIndex: 0, options: [], chosen: '', locked: false,
      lastOk: false, qCorrect: 0, qAnswered: 0, qFinished: false
    }
  },
  computed: {
    headerTitle() { return '今日学习' },
    headerSub() { return '剩余 ' + Math.max(0, this.list.length - this.index) + ' 词 · 服务器智能排程' },
    current() { return this.list[this.index] || {} },
    progressPercent() { return this.list.length ? Math.round(this.index / this.list.length * 100) : 0 },
    retentionPercent() { const r = this.current.retention; return r === null || r === undefined ? 0 : Math.round(r * 100) },
    practiceModeObj() { return PRACTICE_MODES.find((m) => m.key === this.practiceMode) || PRACTICE_MODES[0] },
    needOptions() { return this.practiceModeObj.qType === 'choice' },
    q() { return this.list[this.qIndex] || {} },
    accuracy() { return this.qAnswered ? Math.round(this.qCorrect / this.qAnswered * 100) : 0 }
,
    qStemText() {
      const w = this.q
      if (!w || !w.word) return ''
      if (this.practiceMode === 'e2c') return w.word
      if (this.practiceMode === 'c2e' || this.practiceMode === 'spell') return w.meaning || ''
      return ''
    },
    qMetaText() {
      const w = this.q
      if (this.practiceMode === 'e2c') return ((w.phonetic || '') + (w.pos ? ' ' + w.pos : '')).trim()
      if (this.practiceMode === 'c2e') return '输入对应的英文单词'
      if (this.practiceMode === 'spell') return w.phonetic ? '音标 ' + w.phonetic : ''
      return w.hint || ''
    }
  },
  mounted() { this.loadWords() },
  methods: {
    switchFlow(f) { this.flow = f; if (f === 'practice') this.restartPractice() },
    switchPracticeMode(k) { this.practiceMode = k; this.restartPractice() },
    speakUK() { if (this.current.word) speech.speakUK(this.current.word) },
    speakUS() { if (this.current.word) speech.speakUS(this.current.word) },
    speakExample() { if (this.current.example) speech.speak(this.current.example) },
    async loadWords() {
      this.loading = true
      this.aiExamples = []; this.aiNote = ''
      try {
        const data = await fetchTodayWords(40)
        this.list = (data && data.items || []).map((w) => Object.assign({}, w, { userInput: '', answer: '', explanation: '' }))
      } catch (err) {
        this.list = []
        uni.showToast({ title: (err && err.message) || '获取失败' })
      }
      this.index = 0; this.showMeaning = false
      this.finished = this.list.length === 0
      this.restartPractice(false)
      this.loading = false
    },
    reveal() { this.showMeaning = true },
    async mark(quality) {
      const w = this.current
      if (!w || !w.id) return
      const isNew = w.is_new
      const payload = {
        word_id: w.id, quality,
        review_type: isNew ? 'learn' : 'review',
        is_correct: quality >= 3,
        answered_at: new Date().toISOString()
      }
      try {
        const plan = await submitRecord(payload)
        this.index += 1
        this.showMeaning = false; this.aiExamples = []; this.aiNote = ''; this.tutor = null; this.tutorOpen = false
        if (this.index >= this.list.length) this.finished = true
        uni.showToast({ title: '已安排：' + this.intervalLabel(plan) + ' 复习', icon: 'success' })
      } catch (err) {
        uni.showToast({ title: (err && err.message) || '提交失败' })
      }
    },
    intervalLabel(plan) {
      const mins = plan.interval_minutes || 0
      if (mins < 60) return mins + ' 分钟后'
      if (mins < 1440) return Math.round(mins / 60) + ' 小时后'
      return Math.round(mins / 1440) + ' 天后'
    },
    async loadAiExample() {
      const word = this.current
      if (!word || !word.id) return
      this.aiLoading = true; this.aiNote = ''
      try {
        const data = await requestExample(word.id, word.word)
        this.aiExamples = data.examples || []; this.aiNote = data.note || ''
      } catch (err) { this.aiExamples = []; this.aiNote = (err && err.message) || 'AI 例句获取失败' }
      finally { this.aiLoading = false }
    },
    async toggleTutor() {
      if (this.tutorOpen) { this.tutorOpen = false; return }
      this.tutorOpen = true
      const word = this.current
      if (!word || !word.id) return
      this.tutorLoading = true
      try { this.tutor = await askTutor(word.id, word.word) }
      catch (err) { this.tutor = { note: (err && err.message) || '讲解失败', meaning: word.meaning, explanation: '', mnemonic: '', collocations: [], confusable: [] } }
      finally { this.tutorLoading = false }
    },
    restartPractice(markFinished) {
      this.qIndex = 0; this.qCorrect = 0; this.qAnswered = 0
      this.qFinished = markFinished === false ? this.list.length === 0 : false
      if (this.flow === 'practice') this.buildQ()
    },
    explainOf(w) {
      let s = (w.pos ? w.pos + ' ' : '') + w.meaning
      if (w.example) s += ' 例：' + w.example
      if (w.synonyms && w.synonyms.length) s += ' 近义：' + w.synonyms.slice(0, 3).join('、')
      return s
    },
    buildQ() {
      const list = this.list
      if (!list.length || this.qIndex >= list.length) { this.qFinished = true; return }
      const w = list[this.qIndex]
      const typing = this.practiceModeObj.qType === 'typing'
      w.answer = typing ? w.word : w.meaning
      w.explanation = this.explainOf(w)
      if (!w.userInput) w.userInput = ''
      this.locked = false; this.chosen = ''; this.lastOk = false
      if (this.needOptions) {
        const others = list.filter((x) => x.id !== w.id)
        const seen = {}; seen[w.answer] = true; const dist = []
        for (const x of shuffle(others)) {
          const val = x.meaning
          if (val && !seen[val]) { seen[val] = true; dist.push(val) }
          if (dist.length >= 3) break
        }
        this.options = shuffle([w.answer].concat(dist))
      } else this.options = []
      if (this.practiceMode === 'chant') setTimeout(() => this.speakQ(), 300)
    },
    speakQ() { const w = this.q; if (w && w.word) speech.speak(w.word) },
    optionClass(opt) {
      const w = this.q
      if (!this.locked) return ''
      if (opt === w.answer) return 'correct'
      if (opt === this.chosen) return 'wrong'
      return 'dim'
    },
    choose(opt) { if (this.locked) return; this.locked = true; this.chosen = opt; this.judge(opt === this.q.answer) },
    submitTyping() {
      if (this.locked) return
      const w = this.q
      const val = ((w.userInput || '') + '').trim().toLowerCase()
      if (!val) { uni.showToast({ title: '请输入答案' }); return }
      this.locked = true
      this.judge(val === String(w.answer).trim().toLowerCase())
    },
    async judge(ok) {
      this.lastOk = ok
      if (ok) this.qCorrect += 1
      this.qAnswered += 1
      const w = this.q
      const payload = {
        word_id: w.id, quality: ok ? 4 : 1, review_type: 'test',
        topic: this.practiceModeObj.topic, is_correct: ok,
        answered_at: new Date().toISOString()
      }
      try { await submitRecord(payload) } catch (err) { /* 练习计分失败不阻断 */ }
      setTimeout(() => { this.qIndex += 1; this.buildQ() }, 1100)
    }
  }
}
</script>

<style scoped>
.hdr-link { border: none; background: none; color: var(--tint); font-size: 16px; font-weight: 500; padding: 6px 0; }
.hdr-link:active { opacity: .55; }

.learn { padding-top: 18px; }
.progress { display: flex; justify-content: space-between; align-items: baseline; padding: 0 2px; }
.progress-text { font-size: 13px; color: var(--label-2); }
.progress-text.strong { font-weight: 600; color: var(--label); font-variant-numeric: tabular-nums; }
.progress-bar { height: 4px; background: rgba(38, 34, 28, .16); border-radius: 2px; margin: 7px 0 16px; overflow: hidden; }
.progress-inner { height: 100%; background: var(--tint); border-radius: 2px; transition: width .4s cubic-bezier(.22, .61, .36, 1); }

.flash { padding: 18px 18px 16px; border-radius: 18px; box-shadow: 0 3px 14px rgba(0, 0, 0, .05); }
.flash-top { display: flex; gap: 6px; flex-wrap: wrap; }
.word { margin-top: 16px; font-size: 42px; font-weight: 700; letter-spacing: -.8px; line-height: 1.08; color: var(--label); word-break: break-word; }
.meta { margin-top: 9px; display: flex; align-items: center; flex-wrap: wrap; gap: 8px; }
.phonetic { font-size: 15px; color: var(--label-3); }
.pos { font-size: 12px; color: var(--label-2); background: var(--fill); padding: 2px 9px; border-radius: 999px; }
.voice-links { margin-left: auto; display: inline-flex; gap: 6px; }
.voice-link { border: none; background: rgba(188, 62, 27, .09); color: var(--tint); display: inline-flex; align-items: center; gap: 4px; font-size: 13px; font-weight: 500; padding: 5px 11px; border-radius: 999px; }
.voice-link:active { opacity: .6; }
.voice-link svg { width: 14px; height: 14px; }
.freq { margin-top: 14px; padding-top: 12px; border-top: .5px solid var(--separator); display: flex; flex-wrap: wrap; font-size: 12px; color: var(--label-3); }
.freq span { display: inline-flex; align-items: baseline; gap: 3px; }
.freq span + span::before { content: "·"; margin: 0 9px; color: rgba(38, 34, 28, .22); }
.freq strong { font-weight: 600; color: var(--label-2); font-variant-numeric: tabular-nums; }

.meaning { margin-top: 16px; padding-top: 14px; border-top: .5px solid var(--separator); animation: rise .25s ease; }
.meaning-text { font-size: 19px; font-weight: 600; line-height: 1.5; }
.example { margin-top: 10px; }
.example-en { font-size: 15px; color: var(--label); line-height: 1.65; }
.example-cn { font-size: 13px; color: var(--label-2); margin-top: 2px; line-height: 1.6; }
.listen-line { margin-top: 8px; border: none; background: none; color: var(--tint); font-size: 13px; font-weight: 500; display: inline-flex; align-items: center; gap: 4px; padding: 0; }
.listen-line svg { width: 14px; height: 14px; }
.syn { margin-top: 10px; font-size: 14px; color: var(--label-2); line-height: 1.6; }
.syn-label { color: var(--label-3); margin-right: 6px; font-size: 12px; }

.reveal { margin-top: 18px; width: 100%; border: none; border-radius: 13px; padding: 15px; background: rgba(188, 62, 27, .08); color: var(--tint); font-size: 15px; font-weight: 500; display: inline-flex; align-items: center; justify-content: center; gap: 7px; transition: background .15s; }
.reveal:active { background: rgba(188, 62, 27, .16); }
.reveal svg { width: 17px; height: 17px; }

.actions { display: flex; gap: 10px; margin-top: 16px; }
.grade { flex: 1; height: 48px; border: none; border-radius: 13px; font-size: 15px; font-weight: 600; transition: filter .15s; }
.grade:active { filter: brightness(.95); }
.grade.forget { background: rgba(192, 57, 43, .1); color: #9E2417; }
.grade.blur { background: rgba(169, 105, 15, .16); color: #7C4A06; }
.grade.know { background: var(--tint); color: #fff; }
.action-hint { margin-top: 11px; text-align: center; font-size: 11px; color: var(--label-3); }

.panel { margin-top: 16px; }
.panel-head { display: flex; justify-content: space-between; align-items: center; padding: 15px 16px 2px; }
.panel-title { font-size: 16px; font-weight: 600; color: var(--label); }
.panel-link { border: none; background: none; color: var(--tint); font-size: 14px; font-weight: 500; padding: 6px 0; }
.panel-link:active { opacity: .55; }
.panel-body { padding: 10px 16px 14px; }
.panel-body.muted, .muted.small { font-size: 13px; }
.ex-item + .ex-item { border-top: .5px solid var(--separator); padding-top: 10px; margin-top: 10px; }
.ex-en { font-size: 15px; color: var(--label); line-height: 1.6; }
.ex-cn { font-size: 13px; color: var(--label-2); margin-top: 2px; line-height: 1.6; }
.panel-note { margin-top: 10px; font-size: 11px; color: var(--label-3); }
.tutor-sec { padding: 9px 0; }
.tutor-sec + .tutor-sec { border-top: .5px solid var(--separator); }
.tutor-label { display: block; font-size: 12px; color: var(--label-3); margin-bottom: 4px; }
.tutor-text { font-size: 14px; color: var(--label); line-height: 1.7; }
.tag-wrap { display: flex; flex-wrap: wrap; gap: 6px; }

.ptype-seg { margin-top: 18px; }
.quiz { padding-top: 16px; }
.quiz-head { display: flex; justify-content: space-between; margin: 0 2px 9px; font-size: 13px; color: var(--label-2); }
.q-score { font-weight: 600; color: var(--label); font-variant-numeric: tabular-nums; }
.question-card { padding: 16px 18px 18px; border-radius: 18px; box-shadow: 0 3px 14px rgba(0, 0, 0, .05); }
.q-badge-row { display: flex; }
.q-listen { display: flex; flex-direction: column; align-items: center; padding: 12px 0 6px; }
.listen-play { width: 84px; height: 84px; border-radius: 50%; border: none; background: rgba(188, 62, 27, .1); color: var(--tint); display: flex; align-items: center; justify-content: center; box-shadow: 0 0 0 10px rgba(188, 62, 27, .05); }
.listen-play:active { transform: scale(.96); }
.listen-play svg { width: 34px; height: 34px; }
.q-stem { font-size: 25px; font-weight: 600; text-align: center; line-height: 1.35; margin-top: 10px; word-break: break-word; }
.q-stem.cn { font-size: 22px; }
.q-meta { color: var(--label-3); font-size: 13px; text-align: center; margin-top: 9px; }
.options { margin-top: 18px; }
.option { width: 100%; display: flex; align-items: center; justify-content: space-between; gap: 12px; padding: 13px 16px; margin-bottom: 10px; background: var(--card); border: 1px solid rgba(38, 34, 28, .16); border-radius: 12px; font-size: 15px; color: var(--label); text-align: left; transition: border-color .15s, background .15s; }
.option:active { background: var(--fill); }
.option.correct { border-color: rgba(47, 122, 78, .55); background: rgba(47, 122, 78, .1); }
.option.wrong { border-color: rgba(192, 57, 43, .55); background: rgba(192, 57, 43, .09); }
.option.dim { opacity: .42; }
.mk { width: 19px; height: 19px; flex: none; }
.mk.ok { color: var(--green); }
.mk.no { color: var(--red); }
.q-typing { display: flex; gap: 10px; margin-top: 18px; }
.typing-input { flex: 1; }
.typing-btn { height: 44px; padding: 0 20px; font-size: 16px; }
.feedback { margin-top: 4px; border-radius: 12px; padding: 12px 14px; font-size: 14px; line-height: 1.5; }
.fb-line { font-weight: 600; }
.feedback.good { background: rgba(47, 122, 78, .12); color: #23603B; }
.feedback.bad { background: rgba(192, 57, 43, .1); color: #9E2417; }
.q-explain { margin-top: 4px; color: var(--label-2); font-size: 12px; line-height: 1.65; }

.score-card { margin: 24px auto 0; max-width: 620px; border-radius: 18px; padding: 30px 20px 26px; text-align: center; box-shadow: 0 3px 14px rgba(0, 0, 0, .05); }
.score-num { font-size: 64px; font-weight: 700; letter-spacing: -2px; color: var(--label); line-height: 1; font-variant-numeric: tabular-nums; }
.score-num .pct { font-size: 30px; color: var(--label-3); letter-spacing: 0; margin-left: 2px; }
.score-sub { color: var(--label-2); font-size: 13px; margin-top: 12px; }
.score-actions { display: flex; gap: 10px; justify-content: center; margin-top: 22px; }
@media (min-width: 1000px) {
  .options { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); column-gap: 10px; }
  .actions { max-width: 640px; margin-left: auto; margin-right: auto; }
  .flash { padding: 24px 30px 20px; }
  .word { font-size: 48px; }
}
</style>