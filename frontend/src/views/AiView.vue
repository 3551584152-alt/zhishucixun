<template>
  <div class="page">
    <ct4-header title="AI 智能体">
      <template #right><button class="hdr-link" @click="$router.push('/dict')">词典</button></template>
      <div class="seg">
        <button v-for="t in aiTabs" :key="t.key" :class="['seg-item', tab === t.key ? 'on' : '']" @click="switchTab(t.key)">{{ t.label }}</button>
      </div>
    </ct4-header>

    <!-- ============ 学情规划 ============ -->
    <div v-if="tab === 'plan'" class="body">
      <div v-if="planLoading" class="center">正在分析学情…</div>
      <div v-else-if="planner" class="card ai-card">
        <div class="summ">
          <div class="summ-label">学情总览</div>
          <p class="summ-text">{{ planner.summary }}</p>
        </div>
        <div v-if="planner.strengths && planner.strengths.length" class="sec">
          <div class="sec-head"><span class="dot green"></span>优势</div>
          <div v-for="(s, i) in planner.strengths" :key="'s' + i" class="sec-line">{{ s }}</div>
        </div>
        <div v-if="planner.weaknesses && planner.weaknesses.length" class="sec">
          <div class="sec-head"><span class="dot orange"></span>薄弱</div>
          <div v-for="(w, i) in planner.weaknesses" :key="'w' + i" class="sec-line">{{ w }}</div>
        </div>
        <div v-if="planner.advice && planner.advice.length" class="sec">
          <div class="sec-head"><span class="dot blue"></span>建议</div>
          <div v-for="(a, i) in planner.advice" :key="'a' + i" class="sec-line">{{ a }}</div>
        </div>
        <div v-if="planner.note" class="note">{{ planner.note }}</div>
        <button class="btn ghost block redo" @click="loadPlanner">重新分析</button>
      </div>
    </div>

    <!-- ============ 词汇辅导 ============ -->
    <div v-else-if="tab === 'tutor'" class="body">
      <div class="search-wrap">
        <svg class="search-ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/></svg>
        <input v-model="tutorWord" class="search" placeholder="输入单词，如 abandon" @keyup.enter="loadTutor" />
        <button class="btn sm go" @click="loadTutor">讲解</button>
      </div>
      <div v-if="tutorLoading" class="center">正在生成讲解…</div>
      <div v-else-if="tutor" class="card ai-card tutor-card">
        <div class="t-word">{{ tutor.word }} <span class="t-meta">{{ tutor.phonetic }} {{ tutor.pos }}</span></div>
        <div class="sec">
          <div class="sec-head"><span class="dot blue"></span>释义 / 讲解</div>
          <p class="sec-text">{{ tutor.explanation || tutor.meaning }}</p>
        </div>
        <div v-if="tutor.mnemonic" class="sec">
          <div class="sec-head"><span class="dot purple"></span>联想记忆</div>
          <p class="sec-text">{{ tutor.mnemonic }}</p>
        </div>
        <div v-if="tutor.collocations && tutor.collocations.length" class="sec">
          <div class="sec-head"><span class="dot indigo"></span>写作 / 翻译搭配</div>
          <div class="tag-wrap"><span v-for="(x, i) in tutor.collocations" :key="i" class="chip gray">{{ x }}</span></div>
        </div>
        <div v-if="tutor.confusable && tutor.confusable.length" class="sec">
          <div class="sec-head"><span class="dot orange"></span>易混词</div>
          <div class="tag-wrap"><span v-for="(x, i) in tutor.confusable" :key="i" class="chip gray">{{ x }}</span></div>
        </div>
        <div v-if="tutor.usage" class="sec">
          <div class="sec-head"><span class="dot green"></span>例句</div>
          <p class="sec-text">{{ tutor.usage }}</p>
          <p v-if="tutor.example_cn" class="sec-sub">{{ tutor.example_cn }}</p>
        </div>
        <div v-if="tutor.note" class="note">{{ tutor.note }}</div>
      </div>
    </div>

    <!-- ============ 训练评估 ============ -->
    <div v-else class="body">
      <div class="seg topic-seg">
        <button v-for="t in topics" :key="t.key" :class="['seg-item', trainTopic === t.key ? 'on' : '']" @click="setTopic(t.key)">{{ t.label }}</button>
      </div>

      <div class="train-ctl card">
        <div class="search-wrap compact">
          <svg class="search-ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/></svg>
          <input v-model="trainTarget" class="search" placeholder="指定单词（可空）" />
          <button class="btn sm go" @click="generate">出题</button>
        </div>
        <label class="switch-row">
          <span class="switch-label">顽固词特训</span>
          <span class="switch">
            <input type="checkbox" v-model="stubbornOnly" @change="resetTrain" />
            <span class="slider"></span>
          </span>
        </label>
      </div>

      <div v-if="trainLoading" class="center">正在出题…</div>
      <div v-else-if="questions.length" class="quiz">
        <div class="quiz-head">
          <span>已答 {{ answeredCount }}/{{ questions.length }}</span>
          <span class="q-score">正确 {{ correctCount }}</span>
        </div>
        <div v-for="(q, qi) in questions" :key="qi" class="card q-card">
          <div class="q-top">
            <span class="chip blue">{{ topicLabel(trainTopic) }} · {{ q.type === 'typing' ? '拼写' : '选择' }}</span>
            <span class="q-no">{{ qi + 1 }}/{{ questions.length }}</span>
          </div>
          <div class="q-stem">{{ q.stem }}</div>
          <div v-if="q.listen" class="listen"><button class="listen-btn" @click="speak(q.word)">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="M11 5 6 9H2v6h4l5 4V5z"/><path d="M15.5 8.8a4.6 4.6 0 0 1 0 6.4"/></svg>
            听发音
          </button></div>
          <div v-if="q.hint && q.type === 'typing'" class="q-hint">{{ q.hint }}</div>

          <div v-if="q.type === 'choice'" class="options">
            <button v-for="opt in q.options" :key="opt" :class="['option', optClass(q, opt)]" @click="choose(q, opt)">
              <span>{{ opt }}</span>
              <svg v-if="q.answered && opt === q.answer" class="mk ok" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg>
              <svg v-if="q.answered && opt === q.chosen && opt !== q.answer" class="mk no" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round"><path d="M18 6 6 18M6 6l12 12"/></svg>
            </button>
          </div>
          <div v-else class="typing">
            <input v-model="q.userInput" class="textfield tinput" placeholder="输入英文" @keyup.enter="checkTyping(q)" />
            <button class="btn sm tbtn" @click="checkTyping(q)">提交</button>
          </div>

          <div v-if="q.answered" :class="['fb', q.ok ? 'good' : 'bad']">
            <div class="fb-line">{{ q.ok ? '回答正确' : '正确答案：' + q.answer }}</div>
            <span class="exp">{{ q.explanation }}</span>
          </div>
        </div>
      </div>
      <div v-else class="center muted">选择题型后点「出题」开始训练（答题结果将计入个人统计与复习排程）</div>
    </div>
  </div>
</template>

<script>
import Ct4Header from '../components/Ct4Header.vue'
import speech from '../utils/speech'
import uni from '../utils/uni'
import { askPlanner, askTrain, askTutor } from '../api/agents'
import { submitRecord } from '../api/records'

const TOPICS = [
  { key: 'read', label: '阅读' }, { key: 'listen', label: '听力' },
  { key: 'translate', label: '翻译' }, { key: 'write', label: '写作' }
]
export default {
  components: { Ct4Header },
  data() {
    return {
      aiTabs: [{ key: 'plan', label: '学情规划' }, { key: 'tutor', label: '词汇辅导' }, { key: 'train', label: '训练评估' }],
      tab: 'plan', topics: TOPICS,
      planLoading: false, planner: null,
      tutorWord: '', tutorLoading: false, tutor: null,
      trainTopic: 'read', trainTarget: '', stubbornOnly: false, trainLoading: false,
      questions: [], correctCount: 0, answeredCount: 0
    }
  },
  mounted() {
    let agentWord = null, trainWord = null, trainTopic = null
    try { agentWord = JSON.parse(localStorage.getItem('ct4_agent_word')); localStorage.removeItem('ct4_agent_word') } catch (e) {}
    try { trainWord = JSON.parse(localStorage.getItem('ct4_train_word')); localStorage.removeItem('ct4_train_word') } catch (e) {}
    try { trainTopic = JSON.parse(localStorage.getItem('ct4_train_topic')); localStorage.removeItem('ct4_train_topic') } catch (e) {}
    if (agentWord) { this.tab = 'tutor'; this.tutorWord = agentWord; this.loadTutor() }
    else if (trainWord) {
      this.tab = 'train'; this.trainTarget = trainWord
      if (trainTopic) this.trainTopic = trainTopic
      this.generate()
    } else if (this.tab === 'plan') this.loadPlanner()
  },
  methods: {
    switchTab(t) { this.tab = t; if (t === 'plan' && !this.planner) this.loadPlanner() },
    topicLabel(k) { const f = this.topics.find((t) => t.key === k); return f ? f.label : k },
    async loadPlanner() {
      this.planLoading = true
      try { this.planner = await askPlanner(0) }
      catch (err) { uni.showToast({ title: (err && err.message) || '分析失败' }) }
      finally { this.planLoading = false }
    },
    async loadTutor() {
      const word = (this.tutorWord || '').trim()
      if (!word) { uni.showToast({ title: '请输入单词' }); return }
      this.tutorLoading = true
      try { this.tutor = await askTutor(0, word) }
      catch (err) { uni.showToast({ title: (err && err.message) || '讲解失败' }) }
      finally { this.tutorLoading = false }
    },
    setTopic(k) { this.trainTopic = k; this.resetTrain() },
    resetTrain() { this.questions = []; this.correctCount = 0; this.answeredCount = 0 },
    async generate() {
      this.trainLoading = true; this.resetTrain()
      try {
        const data = await askTrain({ topic: this.trainTopic, word: this.trainTarget || '', stubborn_only: this.stubbornOnly, count: 4 })
        this.questions = (data.questions || []).map((q) => Object.assign({}, q, { answered: false, ok: false, chosen: '', userInput: '' }))
        if (data.note) uni.showToast({ title: data.note })
      } catch (err) { uni.showToast({ title: (err && err.message) || '出题失败' }) }
      finally { this.trainLoading = false }
    },
    speak(text) { if (text) speech.speak(text) },
    optClass(q, opt) {
      if (!q.answered) return ''
      if (opt === q.answer) return 'right'
      if (opt === q.chosen) return 'wrong'
      return 'dim'
    },
    async choose(q, opt) {
      if (q.answered) return
      q.answered = true; q.chosen = opt; q.ok = opt === q.answer
      if (q.ok) this.correctCount += 1
      this.answeredCount += 1
      await this.recordAnswer(q, q.ok)
    },
    async checkTyping(q) {
      if (q.answered) return
      const val = ((q.userInput || '') + '').trim().toLowerCase()
      if (!val) { uni.showToast({ title: '请输入答案' }); return }
      q.answered = true; q.ok = val === String(q.answer).toLowerCase()
      if (q.ok) this.correctCount += 1
      this.answeredCount += 1
      await this.recordAnswer(q, q.ok)
    },
    async recordAnswer(q, ok) {
      const payload = {
        word_id: q.word_id || 0, quality: ok ? 4 : 1,
        review_type: 'test', topic: this.trainTopic,
        is_correct: ok, answered_at: new Date().toISOString()
      }
      if (!payload.word_id) return
      try { await submitRecord(payload) } catch (err) { /* 忽略 */ }
    }
  }
}
</script>

<style scoped>
.hdr-link { border: none; background: none; color: var(--tint); font-size: 16px; font-weight: 500; padding: 6px 0; }
.hdr-link:active { opacity: .55; }
.body { padding-top: 18px; }

.ai-card { padding: 6px 18px 14px; border-radius: 18px; box-shadow: 0 3px 14px rgba(0, 0, 0, .05); }
.summ { padding: 14px 0 6px; }
.summ-label { font-size: 13px; font-weight: 600; color: var(--label-2); margin-bottom: 4px; }
.summ-text { font-size: 15px; line-height: 1.7; color: var(--label); }
.sec { padding: 12px 0 4px; border-top: .5px solid var(--separator); }
.sec-head { display: flex; align-items: center; gap: 7px; font-size: 13px; font-weight: 600; color: var(--label-2); margin-bottom: 5px; }
.dot { width: 7px; height: 7px; border-radius: 50%; flex: none; }
.dot.green { background: var(--green); }
.dot.orange { background: var(--orange); }
.dot.blue { background: var(--tint); }
.dot.purple { background: var(--purple); }
.dot.indigo { background: var(--indigo); }
.sec-line { font-size: 14px; color: var(--label); line-height: 1.6; margin: 4px 0 4px 14px; position: relative; }
.sec-line::before { content: ""; position: absolute; left: -10px; top: 10px; width: 3px; height: 3px; border-radius: 50%; background: rgba(38, 34, 28, .3); }
.sec-text { font-size: 14px; color: var(--label); line-height: 1.7; margin: 2px 0; }
.sec-sub { font-size: 13px; color: var(--label-2); line-height: 1.6; margin-top: 2px; }
.note { margin-top: 10px; font-size: 11px; color: var(--label-3); line-height: 1.6; }
.redo { margin-top: 14px; }
.tag-wrap { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 6px; }

.search-wrap { display: flex; align-items: center; gap: 6px; background: var(--fill); border-radius: 12px; padding: 0 6px 0 12px; }
.search-wrap.compact { background: transparent; padding: 0; gap: 8px; }
.search-ico { width: 17px; height: 17px; color: var(--label-3); flex: none; }
.search { flex: 1; min-width: 0; height: 44px; border: none; background: none; outline: none; font-size: 16px; }
.search::placeholder { color: var(--label-3); }
.go { height: 36px; padding: 0 16px; }
.tutor-card { margin-top: 14px; }
.t-word { font-size: 24px; font-weight: 700; letter-spacing: -.3px; padding: 16px 0 6px; }
.t-meta { color: var(--label-3); font-size: 13px; font-weight: 400; margin-left: 6px; }

.topic-seg { margin-bottom: 14px; }
.train-ctl { padding: 16px 16px 12px; margin-bottom: 16px; }
.switch-row { display: flex; align-items: center; justify-content: space-between; margin-top: 12px; }
.switch-label { font-size: 14px; color: var(--label); }
.switch { position: relative; display: inline-block; width: 51px; height: 31px; flex: none; }
.switch input { opacity: 0; width: 0; height: 0; position: absolute; }
.slider { position: absolute; cursor: pointer; inset: 0; background: rgba(38, 34, 28, .26); border-radius: 16px; transition: background .2s; }
.slider::before { content: ""; position: absolute; left: 2px; top: 2px; width: 27px; height: 27px; border-radius: 50%; background: var(--card); box-shadow: 0 1px 3px rgba(0, 0, 0, .3); transition: transform .2s cubic-bezier(.32, .72, .28, 1); }
.switch input:checked + .slider { background: var(--green); }
.switch input:checked + .slider::before { transform: translateX(20px); }

.quiz-head { display: flex; justify-content: space-between; margin: 2px 2px 10px; font-size: 13px; color: var(--label-2); }
.q-score { font-weight: 600; color: var(--label); font-variant-numeric: tabular-nums; }
.q-card { padding: 14px 16px; margin-bottom: 14px; border-radius: 18px; box-shadow: 0 3px 14px rgba(0, 0, 0, .05); }
.q-top { display: flex; justify-content: space-between; align-items: center; }
.q-no { font-size: 12px; color: var(--label-3); font-variant-numeric: tabular-nums; }
.q-stem { font-size: 20px; font-weight: 600; margin-top: 10px; line-height: 1.45; word-break: break-word; }
.listen { margin-top: 8px; }
.listen-btn { border: none; background: rgba(188, 62, 27, .09); color: var(--tint); font-size: 13px; font-weight: 500; display: inline-flex; align-items: center; gap: 5px; padding: 6px 12px; border-radius: 999px; }
.listen-btn svg { width: 14px; height: 14px; }
.q-hint { color: var(--label-3); font-size: 13px; margin-top: 6px; }
.options { margin-top: 12px; }
.option { width: 100%; display: flex; align-items: center; justify-content: space-between; gap: 10px; padding: 12px 14px; margin-bottom: 8px; background: var(--card); border: 1px solid rgba(38, 34, 28, .16); border-radius: 12px; font-size: 14px; color: var(--label); text-align: left; }
.option.right { border-color: rgba(47, 122, 78, .55); background: rgba(47, 122, 78, .1); }
.option.wrong { border-color: rgba(192, 57, 43, .55); background: rgba(192, 57, 43, .09); }
.option.dim { opacity: .42; }
.mk { width: 17px; height: 17px; flex: none; }
.mk.ok { color: var(--green); }
.mk.no { color: var(--red); }
.typing { display: flex; gap: 8px; margin-top: 12px; }
.tinput { flex: 1; }
.tbtn { flex: none; }
.fb { margin-top: 12px; border-radius: 12px; padding: 10px 13px; font-size: 13px; line-height: 1.5; }
.fb-line { font-weight: 600; }
.fb.good { background: rgba(47, 122, 78, .12); color: #23603B; }
.fb.bad { background: rgba(192, 57, 43, .1); color: #9E2417; }
.exp { display: block; margin-top: 3px; color: var(--label-2); font-size: 12px; line-height: 1.6; }
</style>