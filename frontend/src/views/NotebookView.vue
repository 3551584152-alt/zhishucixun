<template>
  <div class="page no-tab">
    <div class="topbar">
      <button class="back" @click="$router.back()" aria-label="返回">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M15 6l-6 6 6 6"/></svg>
      </button>
      <span class="top-title">词本</span>
      <span class="top-spacer"></span>
    </div>

    <div class="seg book-seg">
      <button :class="['seg-item', tab === 'wrong' ? 'on' : '']" @click="switchTab('wrong')">错题本 ({{ counts.wrong_total || 0 }})</button>
      <button :class="['seg-item', tab === 'stubborn' ? 'on' : '']" @click="switchTab('stubborn')">顽固词 ({{ counts.stubborn_total || 0 }})</button>
    </div>

    <div v-if="loading" class="center">加载中…</div>
    <div v-else-if="!list.length" class="center empty">
      <svg class="empty-symbol" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.1V12a10 10 0 1 1-5.9-9.1"/><path d="M22 4 12 14l-3-3"/></svg>
      <div class="empty-title">暂无{{ tab === 'wrong' ? '错题' : '顽固词' }}</div>
      <div class="empty-sub">继续保持，答错的单词会自动进入这里</div>
    </div>
    <div v-else class="list">
      <div v-for="(it, i) in list" :key="i" class="card item" :class="tab">
        <div class="item-main">
          <div class="row-head">
            <span class="row-word">{{ it.word.word }}</span>
            <span class="row-meta">{{ it.word.phonetic }} {{ it.word.pos }}</span>
          </div>
          <div class="row-mean">{{ it.word.meaning }}</div>
          <div class="row-sub">
            <span v-if="tab === 'wrong'">错 {{ it.wrong_count }} 次</span>
            <span v-else>遗忘 {{ it.word.lapses }} 次 · 错 {{ it.wrong_count }} 次</span>
            <span v-if="it.last_wrong_at"> · {{ timeAgo(it.last_wrong_at) }}</span>
          </div>
        </div>
        <div class="item-actions">
          <button class="mini tint" @click="tutor(it)">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3l1.7 4.6L18.5 9.3l-4.8 1.7L12 15.6l-1.7-4.6L5.5 9.3l4.8-1.7L12 3z"/></svg>
            词汇辅导
          </button>
          <button class="mini orange" @click="train(it)">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="M13 2 3 14h7l-1 8 10-12h-7l1-8z"/></svg>
            专项特训
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import uni from '../utils/uni'
import { fetchNotebookSummary, fetchStubborn, fetchWrong } from '../api/notebook'

export default {
  data() {
    return { tab: 'wrong', loading: false, list: [], counts: { wrong_total: 0, stubborn_total: 0 } }
  },
  mounted() {
    try {
      const t = JSON.parse(localStorage.getItem('ct4_notebook_tab'))
      if (t === 'wrong' || t === 'stubborn') { this.tab = t; localStorage.removeItem('ct4_notebook_tab') }
    } catch (e) { /* ignore */ }
    this.loadAll()
  },
  methods: {
    async loadAll() {
      this.loading = true
      try {
        this.counts = await fetchNotebookSummary()
        this.list = this.tab === 'wrong' ? await fetchWrong(200) : await fetchStubborn(200)
      } catch (err) { uni.showToast({ title: (err && err.message) || '获取词本失败' }) }
      finally { this.loading = false }
    },
    switchTab(t) { this.tab = t; this.loadAll() },
    tutor(it) { localStorage.setItem('ct4_agent_word', JSON.stringify(it.word.word)); this.$router.push('/ai') },
    train(it) { localStorage.setItem('ct4_train_word', JSON.stringify(it.word.word)); localStorage.setItem('ct4_train_topic', JSON.stringify('translate')); this.$router.push('/ai') },
    timeAgo(iso) {
      if (!iso) return ''
      const diff = Date.now() - new Date(iso).getTime()
      const mins = Math.floor(diff / 60000)
      if (mins < 60) return mins + ' 分钟前'
      const hours = Math.floor(mins / 60)
      if (hours < 24) return hours + ' 小时前'
      return Math.floor(hours / 24) + ' 天前'
    }
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

.book-seg { margin-top: 16px; }
.list { margin-top: 16px; }
.item { border-radius: 16px; margin-bottom: 12px; box-shadow: 0 3px 14px rgba(0, 0, 0, .05); }
.item-main { padding: 14px 16px 12px; }
.row-head { display: flex; align-items: baseline; gap: 8px; }
.row-word { font-size: 18px; font-weight: 600; }
.item.stubborn .row-word { color: #7C4A06; }
.row-meta { color: var(--label-3); font-size: 12px; }
.row-mean { font-size: 14px; color: var(--label-2); margin-top: 4px; line-height: 1.55; }
.row-sub { font-size: 12px; margin-top: 8px; }
.item.wrong .row-sub { color: var(--red); }
.item.stubborn .row-sub { color: #7C4A06; }
.item-actions { display: flex; gap: 8px; padding: 10px 12px; border-top: .5px solid var(--separator); }
.mini { border: none; background: none; display: inline-flex; align-items: center; gap: 5px; font-size: 14px; font-weight: 500; padding: 6px 10px; border-radius: 10px; }
.mini svg { width: 14px; height: 14px; }
.mini.tint { color: var(--tint); }
.mini.tint:active { background: rgba(188, 62, 27, .08); }
.mini.orange { color: #7C4A06; }
.mini.orange:active { background: rgba(169, 105, 15, .12); }
</style>