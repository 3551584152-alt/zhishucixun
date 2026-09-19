<template>
  <div class="page no-tab">
    <div class="topbar">
      <button class="back" @click="$router.back()" aria-label="返回">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M15 6l-6 6 6 6"/></svg>
      </button>
      <span class="top-title">{{ tab === 'bank' ? '词库' : '词典' }}</span>
      <span class="top-spacer"></span>
    </div>

    <div class="seg dict-seg">
      <button :class="['seg-item', tab === 'bank' ? 'on' : '']" @click="switchTab('bank')">词库</button>
      <button :class="['seg-item', tab === 'lookup' ? 'on' : '']" @click="switchTab('lookup')">词典</button>
    </div>

    <!-- ============ 词库浏览 ============ -->
    <div v-if="tab === 'bank'" class="body">
      <div class="search-wrap">
        <svg class="search-ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/></svg>
        <input v-model="q" class="search" placeholder="搜索单词或释义" @keyup.enter="load(1)" />
        <button class="btn sm go" @click="load(1)">搜索</button>
      </div>

      <div class="f-row">
        <div class="sel-wrap">
          <select v-model="topic" class="sel" @change="load(1)">
            <option value="">全部题型</option><option value="read">阅读</option><option value="listen">听力</option>
            <option value="translate">翻译</option><option value="write">写作</option>
          </select>
        </div>
        <div class="sel-wrap">
          <select v-model="sort" class="sel" @change="load(1)">
            <option value="word">按单词</option><option value="freq">按考频</option>
            <option value="difficulty">按难度</option><option value="new">未学优先</option>
          </select>
        </div>
      </div>

      <div v-if="loading" class="center">加载中…</div>
      <div v-else-if="!items.length" class="center muted">没有匹配的单词，换个关键词试试</div>
      <div v-else class="group bank-list">
        <div v-for="w in items" :key="w.id" class="inset-row row-tap" @click="openDetail(w)">
          <div class="b-main">
            <div class="b-head">
              <span class="b-word">{{ w.word }}</span>
              <span :class="['chip', w.is_new ? 'blue' : 'green']">{{ w.is_new ? '未学' : '已学' }}</span>
            </div>
            <div class="b-meta">{{ w.phonetic }} {{ w.pos }} · {{ w.meaning }}</div>
            <div class="b-freq">
              <span>阅读 {{ w.freq_read }}</span><span>听力 {{ w.freq_listen }}</span><span>翻译 {{ w.freq_translate }}</span><span>写作 {{ w.freq_write }}</span><span class="b-diff">难度 {{ w.difficulty }}</span>
            </div>
          </div>
          <svg class="chev" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 6l6 6-6 6"/></svg>
        </div>
      </div>
      <div v-if="items.length < total" class="more-wrap">
        <button class="btn ghost sm" @click="load(page + 1)">加载更多 · {{ items.length }}/{{ total }}</button>
      </div>
    </div>

    <!-- ============ 词典查询 ============ -->
    <div v-else class="body">
      <div class="search-wrap">
        <svg class="search-ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/></svg>
        <input v-model="lookupWordText" class="search" placeholder="输入英文单词查询词库" @keyup.enter="doLookup" />
        <button class="btn sm go" @click="doLookup">查询</button>
      </div>

      <button class="ox-link" @click="oxFromInput">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><path d="M15 3h6v6"/><path d="M10 14 21 3"/></svg>
        用牛津词典查询（新窗口）
      </button>

      <div v-if="lookupLoading" class="center">查询中…</div>
      <div v-else-if="detail" class="card detail">
        <div class="d-head">
          <span class="d-word">{{ detail.word }}</span>
          <span :class="['chip', detail.is_new ? 'blue' : 'green']">{{ detail.is_new ? '未学' : '已学' }}</span>
        </div>
        <div class="d-line">
          <span class="d-phon">{{ detail.phonetic }} {{ detail.pos }}</span>
          <button class="listen-btn" @click="speakWord">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="M11 5 6 9H2v6h4l5 4V5z"/><path d="M15.5 8.8a4.6 4.6 0 0 1 0 6.4"/></svg>
            发音
          </button>
        </div>
        <div class="d-freq">
          <span>阅读 {{ detail.freq_read }}</span><span>听力 {{ detail.freq_listen }}</span><span>翻译 {{ detail.freq_translate }}</span><span>写作 {{ detail.freq_write }}</span><span class="d-diff">难度 {{ detail.difficulty }}</span>
        </div>

        <div class="d-sec">
          <div class="d-label">释义</div>
          <p class="d-text">{{ detail.meaning }}</p>
        </div>
        <div v-if="detail.example" class="d-sec">
          <div class="d-label">例句</div>
          <p class="d-text">{{ detail.example }}</p>
          <p class="d-sub">{{ detail.example_cn }}</p>
          <button class="listen-btn" @click="speakExample">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="M11 5 6 9H2v6h4l5 4V5z"/><path d="M15.5 8.8a4.6 4.6 0 0 1 0 6.4"/></svg>
            朗读例句
          </button>
        </div>
        <div v-if="detail.synonyms && detail.synonyms.length" class="d-sec">
          <div class="d-label">近义词</div>
          <div class="tag-wrap"><span v-for="(x, i) in detail.synonyms" :key="i" class="chip gray">{{ x }}</span></div>
        </div>
        <div v-if="detail.mnemonic" class="d-sec">
          <div class="d-label">联想记忆</div>
          <p class="d-text">{{ detail.mnemonic }}</p>
        </div>
        <div v-if="detail.collocations && detail.collocations.length" class="d-sec">
          <div class="d-label">搭配</div>
          <div class="tag-wrap"><span v-for="(x, i) in detail.collocations" :key="i" class="chip gray">{{ x }}</span></div>
        </div>
        <div v-if="detail.confusables && detail.confusables.length" class="d-sec">
          <div class="d-label">易混词</div>
          <div class="tag-wrap"><span v-for="(x, i) in detail.confusables" :key="i" class="chip gray">{{ x }}</span></div>
        </div>
        <div v-if="!detail.is_new" class="d-sec">
          <div class="d-label">学习状态</div>
          <p class="d-text">复习阶段 {{ detail.stage || 0 }} · 遗忘 {{ detail.lapses || 0 }} 次</p>
        </div>
        <div class="d-actions">
          <button class="btn ghost sm" @click="askTutor(detail)">词汇辅导</button>
          <button class="btn sm" @click="openOx(detail.word)">牛津词典</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import speech from '../utils/speech'
import uni from '../utils/uni'
import { fetchWordList, lookupWord } from '../api/words'

export default {
  data() {
    return { tab: 'bank', q: '', topic: '', sort: 'word', page: 1, size: 30, total: 0, items: [], loading: false,
      lookupWordText: '', lookupLoading: false, detail: null }
  },
  mounted() {
    const idx = location.hash.indexOf('lookup')
    const qs = new URLSearchParams(location.search)
    if (qs.get('tab') === 'lookup') this.tab = 'lookup'
    if (this.tab === 'bank') this.load(1)
  },
  methods: {
    switchTab(t) { this.tab = t; if (t === 'bank') this.load(1) },
    async load(page) {
      this.loading = true
      try {
        const data = await fetchWordList({ q: this.q.trim(), topic: this.topic, learned: 0, sort: this.sort, page: page || 1, size: this.size })
        this.total = data.total || 0; this.page = data.page || 1
        this.items = page > 1 ? this.items.concat(data.items || []) : (data.items || [])
      } catch (err) { uni.showToast({ title: (err && err.message) || '获取词库失败' }) }
      finally { this.loading = false }
    },
    openDetail(w) { this.tab = 'lookup'; this.lookupWordText = w.word; this.doLookup() },
    async doLookup() {
      const word = (this.lookupWordText || '').trim()
      if (!word) { uni.showToast({ title: '请输入单词' }); return }
      this.lookupLoading = true
      try { this.detail = await lookupWord(word) }
      catch (err) { this.detail = null; uni.showToast({ title: (err && err.message) || '词库中未找到' }) }
      finally { this.lookupLoading = false }
    },
    speakWord() { if (this.detail && this.detail.word) speech.speak(this.detail.word) },
    speakExample() { if (this.detail && this.detail.example) speech.speak(this.detail.example) },
    openOx(word) { if (word) window.open('https://www.oxfordlearnersdictionaries.com/definition/english/' + encodeURIComponent(word.toLowerCase()), '_blank') },
    oxFromInput() {
      const word = (this.lookupWordText || '').trim()
      if (!word) { uni.showToast({ title: '请先输入单词' }); return }
      this.openOx(word)
    },
    askTutor(w) { localStorage.setItem('ct4_agent_word', JSON.stringify(w.word)); this.$router.push('/ai') }
  }
}
</script>

<style scoped>
.topbar {
  position: sticky; top: 0; z-index: 40; margin: 0 -16px;
  display: flex; align-items: center; justify-content: space-between;
  padding: calc(8px + env(safe-area-inset-top)) 16px 8px;
  background: rgba(246, 246, 248, .72);
  -webkit-backdrop-filter: saturate(180%) blur(20px);
  backdrop-filter: saturate(180%) blur(20px);
}
.back { border: none; background: none; color: var(--tint); width: 30px; height: 30px; display: flex; align-items: center; }
.back svg { width: 22px; height: 22px; }
.top-title { font-size: 17px; font-weight: 600; }
.top-spacer { width: 30px; }

.dict-seg { margin-top: 14px; }
.body { padding-top: 16px; }

.search-wrap { display: flex; align-items: center; gap: 6px; background: var(--card); border-radius: 13px; padding: 0 6px 0 12px; box-shadow: 0 1px 6px rgba(0, 0, 0, .05); }
.search-ico { width: 17px; height: 17px; color: var(--label-3); flex: none; }
.search { flex: 1; min-width: 0; height: 46px; border: none; background: none; outline: none; font-size: 16px; }
.search::placeholder { color: var(--label-3); }
.go { height: 36px; padding: 0 16px; }

.f-row { display: flex; gap: 10px; margin: 12px 0; }
.sel-wrap { flex: 1; position: relative; }
.sel-wrap::after { content: ""; position: absolute; right: 13px; top: 50%; transform: translateY(-70%) rotate(45deg); width: 6px; height: 6px; border-right: 1.6px solid var(--label-3); border-bottom: 1.6px solid var(--label-3); pointer-events: none; }
.sel { appearance: none; -webkit-appearance: none; width: 100%; height: 40px; border: none; background: var(--card); border-radius: 12px; padding: 0 28px 0 14px; font-size: 14px; color: var(--label); outline: none; box-shadow: 0 1px 6px rgba(0, 0, 0, .05); }
.sel option { color: var(--label); }

.bank-list { border-radius: 16px; box-shadow: 0 3px 14px rgba(0, 0, 0, .05); }
.b-main { flex: 1; min-width: 0; padding: 2px 0; }
.b-head { display: flex; align-items: center; gap: 8px; }
.b-word { font-size: 18px; font-weight: 600; }
.b-meta { font-size: 13px; color: var(--label-2); margin-top: 4px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.b-freq { display: flex; flex-wrap: wrap; column-gap: 12px; row-gap: 2px; margin-top: 7px; font-size: 11px; color: var(--label-3); }
.b-freq .b-diff { color: var(--purple); }
.chev { width: 15px; height: 15px; color: var(--label-3); flex: none; margin-left: auto; }
.more-wrap { display: flex; justify-content: center; margin: 18px 0 6px; }

.ox-link { width: 100%; display: inline-flex; align-items: center; justify-content: center; gap: 7px; margin: 12px 0 16px; border: none; background: rgba(188, 62, 27, .08); color: var(--tint); font-size: 14px; font-weight: 500; padding: 13px; border-radius: 13px; }
.ox-link svg { width: 16px; height: 16px; }
.ox-link:active { background: rgba(188, 62, 27, .15); }

.detail { padding: 18px 18px 16px; border-radius: 18px; box-shadow: 0 3px 14px rgba(0, 0, 0, .05); }
.d-head { display: flex; align-items: center; justify-content: space-between; gap: 10px; }
.d-word { font-size: 30px; font-weight: 700; letter-spacing: -.5px; word-break: break-word; }
.d-line { display: flex; align-items: center; justify-content: space-between; margin-top: 8px; }
.d-phon { color: var(--label-3); font-size: 15px; }
.listen-btn { border: none; background: rgba(188, 62, 27, .09); color: var(--tint); font-size: 13px; font-weight: 500; display: inline-flex; align-items: center; gap: 5px; padding: 6px 12px; border-radius: 999px; margin-top: 6px; }
.listen-btn svg { width: 14px; height: 14px; }
.d-freq { display: flex; flex-wrap: wrap; column-gap: 12px; row-gap: 3px; font-size: 12px; color: var(--label-3); margin: 12px 0 4px; }
.d-freq .d-diff { color: var(--purple); }
.d-sec { padding: 12px 0 6px; border-top: .5px solid var(--separator); }
.d-label { font-size: 12px; color: var(--label-3); margin-bottom: 4px; }
.d-text { font-size: 15px; color: var(--label); line-height: 1.65; margin: 2px 0; }
.d-sub { font-size: 13px; color: var(--label-2); line-height: 1.6; }
.tag-wrap { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 4px; }
.d-actions { display: flex; gap: 10px; margin-top: 16px; }
.d-actions .btn { flex: 1; }
</style>