<template>
  <div class="page">
    <ct4-header :title="'今日计划'" :sub="headerSub">
      <template #right><button class="hdr-link" @click="load(true)">刷新</button></template>
    </ct4-header>

    <div v-if="loading" class="center">加载中…</div>

    <template v-else>
      <div v-if="total > 0" class="card sum">
        <div class="sum-head">
          <span class="sum-title">今日进度</span>
          <span class="sum-date">{{ today }}</span>
        </div>
        <div class="sum-main">
          <div class="sum-big">{{ progressPercent }}<span class="unit">%</span></div>
          <div class="sum-detail">
            <span>已完成 <b>{{ plan.completed }}</b></span>
            <span class="dot">·</span>
            <span>共 <b>{{ total }}</b> 词</span>
          </div>
        </div>
        <div class="sum-bar"><div class="sum-bar-inner" :style="{ width: progressPercent + '%' }"></div></div>
      </div>

      <div v-if="total === 0" class="center empty">
        <svg class="empty-symbol" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M12 7.5v5"/><path d="M12 16.5h.01"/></svg>
        <div class="empty-title">今日暂无学习任务</div>
        <div class="empty-sub">去背诵模块领取今日新词与复习安排</div>
        <div class="empty-actions"><button class="btn" @click="$router.push('/study')">去背诵新词</button></div>
      </div>

      <template v-else>
        <div v-if="learnNew.length" class="sec">
          <div class="sec-title">新学 <span class="sec-count">{{ learnNew.length }}</span></div>
          <div class="group">
            <div v-for="(it, i) in learnNew" :key="'l' + i" class="inset-row row-tap" @click="open(it)">
              <div class="cell-main">
                <div class="cell-word">{{ it.word.word }}</div>
                <div class="cell-mean">{{ it.word.meaning }}</div>
                <div class="cell-reason">{{ reasonText(it) }}</div>
              </div>
              <svg class="chev" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 6l6 6-6 6"/></svg>
            </div>
          </div>
        </div>

        <div v-if="review.length" class="sec">
          <div class="sec-title">复习 <span class="sec-count">{{ review.length }}</span></div>
          <div class="group">
            <div v-for="(it, i) in review" :key="'r' + i" class="inset-row row-tap" @click="open(it)">
              <div class="cell-main">
                <div class="cell-word">{{ it.word.word }}</div>
                <div class="cell-mean">{{ it.word.meaning }}</div>
                <div class="cell-reason">{{ reasonText(it) }}</div>
              </div>
              <svg class="chev" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 6l6 6-6 6"/></svg>
            </div>
          </div>
        </div>

        <div v-if="stubborn.length" class="sec">
          <div class="sec-title">顽固词 <span class="sec-count">{{ stubborn.length }}</span></div>
          <div class="group">
            <div v-for="(it, i) in stubborn" :key="'s' + i" class="inset-row row-tap" @click="open(it)">
              <div class="cell-main">
                <div class="cell-word stubborn-word">{{ it.word.word }}</div>
                <div class="cell-mean">{{ it.word.meaning }}</div>
                <div class="cell-reason stubborn-reason">遗忘 {{ it.word.lapses }} 次 · 优先攻克</div>
              </div>
              <svg class="chev" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 6l6 6-6 6"/></svg>
            </div>
          </div>
        </div>

        <div v-if="forecast.length" class="sec">
          <div class="sec-title">未来 7 天</div>
          <div class="group forecast-group">
            <div v-for="f in forecast" :key="f.date" class="fc-item" :class="{ today: f.date === today }">
              <div class="fc-week">{{ weekLabel(f.date) }}</div>
              <div class="fc-num">{{ f.total }}</div>
              <div class="fc-date">{{ shortDate(f.date) }}</div>
            </div>
          </div>
        </div>
      </template>
    </template>

    <!-- 快速复习：iOS 底部弹层 -->
    <transition name="sheet-fade">
      <div v-if="practice" class="mask" @click.self="closePractice">
        <div class="sheet">
          <div class="grabber"></div>
          <div class="sheet-head">
            <span :class="['chip', practice.kind === 'stubborn' ? 'red' : practice.kind === 'review' ? 'orange' : 'blue']">{{ kindLabel(practice.kind) }}</span>
            <button class="sheet-close" @click="closePractice" aria-label="关闭">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg>
            </button>
          </div>
          <div class="sheet-word">{{ practice.word.word }}</div>
          <div class="sheet-meta">{{ practice.word.phonetic }} {{ practice.word.pos }}</div>
          <div v-if="showMeaning" class="sheet-mean">{{ practice.word.meaning }}</div>
          <button v-else class="reveal" @click="showMeaning = true">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
            轻点显示释义
          </button>
          <div class="sheet-actions">
            <button class="btn ghost forget" @click="doReview(1)">忘记了</button>
            <button class="btn green" @click="doReview(5)">认识</button>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script>
import Ct4Header from '../components/Ct4Header.vue'
import uni from '../utils/uni'
import { fetchDailyPlan } from '../api/plan'
import { submitRecord } from '../api/records'

function todayStr() {
  const d = new Date(); const p = (n) => (n < 10 ? '0' + n : '' + n)
  return d.getFullYear() + '-' + p(d.getMonth() + 1) + '-' + p(d.getDate())
}
export default {
  components: { Ct4Header },
  data() {
    return { today: todayStr(), loading: false,
      plan: { completed: 0, total: 0, progress: 0, learn_new: [], review: [], stubborn: [], forecast: [] },
      practice: null, showMeaning: false }
  },
  computed: {
    total() { return this.plan.total || 0 },
    progressPercent() { return this.total ? Math.round((this.plan.completed || 0) / this.total * 100) : 0 },
    learnNew() { return this.plan.learn_new || [] },
    review() { return this.plan.review || [] },
    stubborn() { return this.plan.stubborn || [] },
    forecast() { return this.plan.forecast || [] },
    headerSub() { return this.total ? '已完成 ' + (this.plan.completed || 0) + ' / ' + this.total + ' · ' + this.today : this.today }
  },
  mounted() { this.load(false) },
  methods: {
    async load(refresh) {
      this.loading = true
      try { this.plan = await fetchDailyPlan(this.today, refresh) }
      catch (err) { uni.showToast({ title: (err && err.message) || '获取计划失败' }) }
      finally { this.loading = false }
    },
    kindLabel(k) { return { learn: '新学', review: '复习', stubborn: '顽固' }[k] || k },
    reasonText(it) {
      const r = it.reasons || {}
      if (!r.priority) return '等待生成…'
      const parts = []
      parts.push('考频' + (r.freq_total || 0))
      if (r.topic_freq) parts.push('定向' + r.topic_freq)
      parts.push('难度' + (r.difficulty || 1))
      parts.push('遗忘率x' + (r.forgetting || 1))
      return parts.join(' · ')
    },
    shortDate(iso) { return iso ? String(iso).slice(5).replace('-', '/') : '' },
    weekLabel(iso) { const w = '日一二三四五六'; try { return '周' + w[new Date(iso).getDay()] } catch (e) { return '' } },
    open(item) { this.practice = item; this.showMeaning = false },
    closePractice() { this.practice = null },
    async doReview(q) {
      const it = this.practice
      if (!it) return
      const word = it.word
      const payload = {
        word_id: word.id, quality: q,
        review_type: it.kind === 'learn' ? 'learn' : 'review',
        is_correct: q >= 3, answered_at: new Date().toISOString()
      }
      try { await submitRecord(payload); uni.showToast({ title: '已记录', icon: 'success' }) }
      catch (err) { uni.showToast({ title: (err && err.message) || '提交失败' }); return }
      this.closePractice(); this.load(false)
    }
  }
}
</script>

<style scoped>
.hdr-link { border: none; background: none; color: var(--tint); font-size: 16px; font-weight: 500; padding: 6px 0; }
.hdr-link:active { opacity: .55; }

.sum { margin-top: 18px; padding: 18px 18px 16px; border-radius: 18px; box-shadow: 0 3px 14px rgba(0, 0, 0, .05); }
.sum-head { display: flex; justify-content: space-between; align-items: baseline; }
.sum-title { font-size: 16px; font-weight: 600; }
.sum-date { font-size: 12px; color: var(--label-3); font-variant-numeric: tabular-nums; }
.sum-main { display: flex; align-items: flex-end; justify-content: space-between; margin-top: 14px; }
.sum-big { font-size: 54px; font-weight: 700; letter-spacing: -1.5px; line-height: 1; color: var(--tint); font-variant-numeric: tabular-nums; }
.sum-big .unit { font-size: 22px; color: var(--label-3); letter-spacing: 0; margin-left: 2px; }
.sum-detail { display: flex; align-items: baseline; gap: 7px; color: var(--label-2); font-size: 13px; padding-bottom: 6px; }
.sum-detail b { color: var(--label); font-weight: 600; font-variant-numeric: tabular-nums; }
.sum-detail .dot { color: rgba(38, 34, 28, .25); }
.sum-bar { height: 6px; background: var(--fill); border-radius: 3px; margin-top: 14px; overflow: hidden; }
.sum-bar-inner { height: 100%; background: var(--tint); border-radius: 3px; transition: width .4s cubic-bezier(.22, .61, .36, 1); }

.sec { margin-top: 24px; }
.sec-title { font-size: 13px; font-weight: 600; color: var(--label-2); margin: 0 4px 8px; letter-spacing: .2px; }
.sec-count { color: var(--label-3); font-weight: 500; margin-left: 4px; font-variant-numeric: tabular-nums; }
.group + .group { margin-top: 0; }
.cell-main { flex: 1; min-width: 0; padding: 2px 0; }
.cell-word { font-size: 17px; font-weight: 600; color: var(--label); }
.stubborn-word { color: #7C4A06; }
.cell-mean { font-size: 14px; color: var(--label-2); margin-top: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.cell-reason { font-size: 11px; color: var(--label-3); margin-top: 5px; }
.stubborn-reason { color: #7C4A06; }
.chev { width: 16px; height: 16px; color: var(--label-3); flex: none; margin-left: auto; }

.forecast-group { display: flex; padding: 6px 0; }
.fc-item { flex: 1; display: flex; flex-direction: column; align-items: center; padding: 10px 0 8px; border-radius: 12px; margin: 0 2px; }
.fc-item.today { background: rgba(188, 62, 27, .08); }
.fc-week { font-size: 10px; color: var(--label-3); }
.fc-item.today .fc-week { color: var(--tint); font-weight: 600; }
.fc-num { font-size: 19px; font-weight: 700; margin: 5px 0 2px; color: var(--label); font-variant-numeric: tabular-nums; }
.fc-item.today .fc-num { color: var(--tint); }
.fc-date { font-size: 10px; color: var(--label-3); font-variant-numeric: tabular-nums; }

.mask { position: fixed; inset: 0; background: rgba(0, 0, 0, .38); z-index: 90; display: flex; align-items: flex-end; justify-content: center; }
.sheet { width: 100%; max-width: 660px; background: var(--card); border-radius: 18px 18px 0 0; padding: 8px 22px calc(24px + env(safe-area-inset-bottom)); animation: sheetUp .3s cubic-bezier(.32, .72, .28, 1); }
.grabber { width: 36px; height: 5px; border-radius: 3px; background: rgba(38, 34, 28, .2); margin: 6px auto 12px; }
@keyframes sheetUp { from { transform: translateY(40px); opacity: .6; } to { transform: translateY(0); opacity: 1; } }
.sheet-fade-enter-active, .sheet-fade-leave-active { transition: opacity .22s ease; }
.sheet-fade-enter-from, .sheet-fade-leave-to { opacity: 0; }
.sheet-head { display: flex; justify-content: space-between; align-items: center; }
.sheet-close { border: none; background: var(--fill); color: var(--label-2); width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; }
.sheet-close:active { opacity: .6; }
.sheet-close svg { width: 13px; height: 13px; }
.sheet-word { font-size: 36px; font-weight: 700; letter-spacing: -.6px; margin-top: 16px; }
.sheet-meta { color: var(--label-3); font-size: 14px; margin-top: 5px; }
.sheet-mean { margin-top: 16px; font-size: 17px; line-height: 1.6; animation: rise .25s ease; }
.reveal { margin-top: 18px; width: 100%; border: none; border-radius: 13px; padding: 15px; background: rgba(188, 62, 27, .08); color: var(--tint); font-size: 15px; font-weight: 500; display: inline-flex; align-items: center; justify-content: center; gap: 7px; }
.reveal svg { width: 17px; height: 17px; }
.sheet-actions { display: flex; gap: 10px; margin-top: 20px; }
.sheet-actions .btn { flex: 1; }
.btn.forget { background: rgba(192, 57, 43, .1); color: #9E2417; }
.btn.green { background: var(--green); }
</style>