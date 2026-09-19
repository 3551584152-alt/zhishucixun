<template>
  <div class="app-shell">
    <router-view />
    <nav v-if="route.meta && route.meta.tab" class="tabbar">
      <div class="tabbar-inner">
        <div v-for="t in tabs" :key="t.path" class="tab-item" :class="{ on: route.path === t.path }" @click="go(t.path)">
          <svg class="tab-ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path v-for="(d, i) in t.paths" :key="i" :d="d" />
          </svg>
          <span class="tab-label">{{ t.label }}</span>
        </div>
      </div>
    </nav>
    <transition name="toast">
      <div v-if="toast.show" class="toast" :class="{ ok: toast.icon === 'success' }">
        <svg v-if="toast.icon === 'success'" class="toast-ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6L9 17l-5-5" /></svg>
        {{ toast.text }}
      </div>
    </transition>
  </div>
</template>

<script>
import { useRoute, useRouter } from 'vue-router'
import { toastState } from './utils/ui'

const ICONS = {
  study: ['M4 19.5A2.5 2.5 0 0 1 6.5 17H20', 'M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z'],
  plan: ['M3 4h18v16a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4z', 'M3 9h18', 'M8 2v4', 'M16 2v4'],
  ai: ['M12 3l1.7 4.6L18.5 9.3l-4.8 1.7L12 15.6l-1.7-4.6L5.5 9.3l4.8-1.7L12 3z', 'M19 15l.8 2.2 2.2.8-2.2.8L19 21l-.8-2.2-2.2-.8 2.2-.8L19 15z'],
  stats: ['M18 20v-8', 'M12 20V5', 'M6 20v-4']
}

export default {
  setup() {
    const route = useRoute()
    const router = useRouter()
    return { route, router, toast: toastState }
  },
  data() {
    return {
      tabs: [
        { path: '/study', label: '背诵', paths: ICONS.study },
        { path: '/plan', label: '计划', paths: ICONS.plan },
        { path: '/ai', label: 'AI', paths: ICONS.ai },
        { path: '/stats', label: '统计', paths: ICONS.stats }
      ]
    }
  },
  methods: {
    go(path) {
      if (this.route.path !== path) this.router.push(path)
    }
  }
}
</script>

<style scoped>
.app-shell { min-height: 100vh; }
.tabbar {
  position: fixed; left: 50%; bottom: 0; transform: translateX(-50%);
  width: min(100%, 1500px); z-index: 80;
  background: rgba(249, 249, 249, .84);
  -webkit-backdrop-filter: saturate(180%) blur(20px);
  backdrop-filter: saturate(180%) blur(20px);
  border-top: .5px solid rgba(38, 34, 28, .16);
}
.tabbar-inner { display: flex; height: calc(52px + env(safe-area-inset-bottom)); padding-bottom: env(safe-area-inset-bottom); }
.tab-item { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 3px; color: #7B7263; }
.tab-item.on { color: var(--tint); }
.tab-ico { width: 24px; height: 24px; }
.tab-item.on .tab-ico { stroke-width: 2.1; }
.tab-label { font-size: 10px; line-height: 1; font-weight: 500; }
.tab-item.on .tab-label { font-weight: 600; }

.toast {
  position: fixed; left: 50%; bottom: calc(84px + env(safe-area-inset-bottom)); transform: translateX(-50%);
  display: flex; align-items: center; gap: 6px; max-width: min(84%, 420px);
  padding: 9px 16px; border-radius: 999px;
  background: rgba(28, 28, 30, .86); color: #fff; font-size: 14px; font-weight: 500;
  -webkit-backdrop-filter: blur(12px); backdrop-filter: blur(12px);
  box-shadow: 0 6px 24px rgba(0, 0, 0, .18); z-index: 999;
}
.toast-ico { width: 15px; height: 15px; color: var(--green); flex: none; }
.toast-enter-active, .toast-leave-active { transition: opacity .22s ease, transform .22s ease; }
.toast-enter-from, .toast-leave-to { opacity: 0; transform: translateX(-50%) translateY(8px); }
</style>