<template>
  <div class="page">
    <ct4-header title="个人统计" :sub="user.nickname || user.username || ''">
      <template #right><button class="hdr-link" @click="logout">退出登录</button></template>
    </ct4-header>

    <div class="body">
      <div class="card user-card">
        <div class="avatar">{{ avatarText }}</div>
        <div class="u-info">
          <div class="u-name">{{ user.nickname || user.username }}</div>
          <div class="u-sub">
            <span class="streak-dot"></span>
            连续学习 {{ summary.streak_days || 0 }} 天
          </div>
        </div>
      </div>

      <div class="stat-grid">
        <div class="stat"><div class="stat-num">{{ summary.learned_total || 0 }}</div><div class="stat-label">已学单词</div></div>
        <div class="stat"><div class="stat-num green">{{ summary.mastered || 0 }}</div><div class="stat-label">已掌握</div></div>
        <div class="stat"><div :class="['stat-num', (summary.due_today || 0) > 0 ? 'orange' : '']">{{ summary.due_today || 0 }}</div><div class="stat-label">今日待复习</div></div>
        <div class="stat"><div class="stat-num">{{ summary.new_remaining || 0 }}</div><div class="stat-label">未学</div></div>
        <div class="stat"><div class="stat-num blue">{{ accuracy }}%</div><div class="stat-label">正确率</div></div>
        <div class="stat"><div class="stat-num sm">{{ summary.plan_done || 0 }}/{{ summary.plan_total || 0 }}</div><div class="stat-label">今日计划</div></div>
      </div>

      <div class="nb-row">
        <div class="nb-card" @click="goNotebook('wrong')">
          <div class="nb-num red">{{ summary.wrong_count || 0 }}</div>
          <div class="nb-label">错题本</div>
          <svg class="nb-chev" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 6l6 6-6 6"/></svg>
        </div>
        <div class="nb-card" @click="goNotebook('stubborn')">
          <div class="nb-num orange">{{ summary.stubborn_count || 0 }}</div>
          <div class="nb-label">顽固词本</div>
          <svg class="nb-chev" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 6l6 6-6 6"/></svg>
        </div>
      </div>

      <div class="card block">
        <div class="block-title">题型正确率</div>
        <div v-if="!topics.length" class="muted empty-tip">暂无题型数据，去「练习测试」积累吧</div>
        <div v-for="t in topics" :key="t.topic" class="topic-row">
          <span class="topic-name">{{ topicLabel(t.topic) }}</span>
          <div class="bar"><div class="bar-inner" :class="accClass(t.accuracy)" :style="{ width: Math.round(t.accuracy * 100) + '%' }"></div></div>
          <span class="topic-pct">{{ Math.round(t.accuracy * 100) }}%</span>
        </div>
      </div>

      <div class="card block">
        <div class="block-title">近 7 天学习量</div>
        <div class="d-bar">
          <div v-for="d in daily" :key="d.date" class="d-col">
            <div class="d-num" :style="{ height: barH(d.count) }"></div>
            <div class="d-date">{{ shortDate(d.date) }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Ct4Header from '../components/Ct4Header.vue'
import uni from '../utils/uni'
import { fetchSummary } from '../api/stats'

export default {
  components: { Ct4Header },
  data() { return { loading: false, user: {}, summary: {}, daily: [] } },
  computed: {
    avatarText() { const name = (this.user && (this.user.nickname || this.user.username)) || '?'; return name.slice(0, 1).toUpperCase() },
    topics() { return (this.summary && this.summary.topics) || [] },
    accuracy() { const s = this.summary || {}; return Math.round((s.accuracy || 0) * 100) }
  },
  mounted() {
    try { this.user = JSON.parse(localStorage.getItem('ct4_user')) || {} } catch (e) { this.user = {} }
    this.loadStats()
  },
  methods: {
    async loadStats() {
      this.loading = true
      try { const data = await fetchSummary(); this.summary = data; this.daily = data.daily || [] }
      catch (err) { uni.showToast({ title: (err && err.message) || '获取统计失败' }) }
      finally { this.loading = false }
    },
    shortDate(iso) { return iso ? String(iso).slice(5).replace('-', '/') : '' },
    topicLabel(k) { return { read: '阅读', listen: '听力', translate: '翻译', write: '写作' }[k] || k },
    accClass(a) { if (a === null || a === undefined) return 'na'; if (a >= 0.8) return 'good'; if (a >= 0.6) return 'mid'; return 'bad' },
    barH(c) { const max = Math.max.apply(null, this.daily.map((d) => d.count).concat([1])); return Math.max(4, Math.round(c / max * 60)) + 'px' },
    goNotebook(tab) { localStorage.setItem('ct4_notebook_tab', JSON.stringify(tab)); this.$router.push('/notebook') },
    logout() { localStorage.removeItem('ct4_token'); localStorage.removeItem('ct4_user'); this.$router.push('/login') }
  }
}
</script>

<style scoped>
.hdr-link { border: none; background: none; color: var(--red); font-size: 16px; font-weight: 500; padding: 6px 0; }
.hdr-link:active { opacity: .55; }
.body { padding-top: 18px; }

.user-card { display: flex; align-items: center; gap: 14px; padding: 16px; border-radius: 18px; box-shadow: 0 3px 14px rgba(0, 0, 0, .05); }
.avatar { width: 48px; height: 48px; border-radius: 50%; background: linear-gradient(135deg, #A23217, #BC3E1B); color: #fff; display: flex; align-items: center; justify-content: center; font-size: 19px; font-weight: 600; flex: none; }
.u-name { font-size: 17px; font-weight: 600; }
.u-sub { display: flex; align-items: center; gap: 6px; font-size: 13px; color: var(--label-2); margin-top: 3px; }
.streak-dot { width: 7px; height: 7px; border-radius: 50%; background: var(--orange); flex: none; }

.stat-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 10px; margin-top: 14px; }
.stat { background: var(--card); border-radius: 14px; padding: 15px 4px; text-align: center; }
.stat-num { font-size: 22px; font-weight: 700; color: var(--label); letter-spacing: -.3px; font-variant-numeric: tabular-nums; }
.stat-num.sm { font-size: 17px; }
.stat-num.green { color: var(--green); }
.stat-num.orange { color: #7C4A06; }
.stat-num.blue { color: var(--tint); }
.stat-label { font-size: 11px; color: var(--label-3); margin-top: 3px; }

.nb-row { display: flex; gap: 10px; margin-top: 14px; }
.nb-card { position: relative; flex: 1; background: var(--card); border-radius: 14px; padding: 15px 16px; cursor: pointer; }
.nb-card:active { background: #F3EFE6; }
.nb-num { font-size: 24px; font-weight: 700; letter-spacing: -.4px; font-variant-numeric: tabular-nums; }
.nb-num.red { color: var(--red); }
.nb-num.orange { color: #7C4A06; }
.nb-label { font-size: 12px; color: var(--label-2); margin-top: 3px; }
.nb-chev { position: absolute; right: 12px; top: 50%; transform: translateY(-50%); width: 15px; height: 15px; color: var(--label-3); }

.block { margin-top: 14px; padding: 16px; border-radius: 18px; box-shadow: 0 3px 14px rgba(0, 0, 0, .05); }
.block-title { font-size: 16px; font-weight: 600; margin-bottom: 12px; }
.empty-tip { font-size: 13px; }
.topic-row { display: flex; align-items: center; gap: 10px; padding: 5px 0; }
.topic-name { width: 34px; font-size: 13px; color: var(--label-2); flex: none; }
.bar { flex: 1; height: 6px; background: var(--fill); border-radius: 3px; overflow: hidden; }
.bar-inner { height: 100%; border-radius: 3px; transition: width .4s ease; }
.bar-inner.good { background: var(--green); }
.bar-inner.mid { background: var(--orange); }
.bar-inner.bad { background: var(--red); }
.bar-inner.na { background: var(--fill-2); }
.topic-pct { width: 40px; text-align: right; font-size: 12px; color: var(--label-2); font-variant-numeric: tabular-nums; }

.d-bar { display: flex; align-items: flex-end; gap: 7px; height: 92px; padding-top: 6px; }
.d-col { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: flex-end; height: 100%; }
.d-num { width: 62%; background: linear-gradient(180deg, #E8834F, #BC3E1B); border-radius: 5px 5px 2px 2px; min-height: 4px; transition: height .4s ease; }
.d-date { font-size: 10px; color: var(--label-3); margin-top: 6px; font-variant-numeric: tabular-nums; }
</style>