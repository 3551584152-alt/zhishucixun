<template>
  <header class="nav">
    <div class="nav-top">
      <div class="nav-titles">
        <h1 class="nav-title">{{ title }}</h1>
        <p v-if="sub" class="nav-sub">{{ sub }}</p>
      </div>
      <div v-if="$slots.right" class="nav-right"><slot name="right" /></div>
    </div>
    <div v-if="$slots.default" class="nav-slot"><slot /></div>
  </header>
</template>

<script>
export default {
  name: 'Ct4Header',
  props: { title: { type: String, default: '' }, sub: { type: String, default: '' } }
}
</script>

<style scoped>
.nav {
  position: sticky; top: 0; z-index: 40; margin: 0 -16px;
  padding: calc(10px + env(safe-area-inset-top)) 16px 10px;
  background: rgba(246, 246, 248, .72);
  -webkit-backdrop-filter: saturate(180%) blur(20px);
  backdrop-filter: saturate(180%) blur(20px);
}
.nav-top { display: flex; align-items: flex-end; justify-content: space-between; gap: 12px; }
.nav-titles { flex: 1; min-width: 0; padding-top: 4px; }
.nav-title { font-size: 30px; font-weight: 700; letter-spacing: -.5px; line-height: 1.1; color: var(--label); }
.nav-sub { margin-top: 3px; font-size: 13px; color: var(--label-3); }
.nav-right { display: flex; align-items: center; gap: 14px; padding-bottom: 2px; flex: none; }
.nav-slot { margin-top: 12px; }
</style>