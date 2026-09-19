<template>
  <div class="page no-tab login-page">
    <div class="hero">
      <div class="logo">智枢</div>
      <div class="title">智枢词训</div>
      <div class="sub">基于多智能体协同的四级英语自适应词汇学习项目</div>
      <div class="tag">考频加权艾宾浩斯 · 四题型自适应 · 多智能体协同辅导</div>
    </div>

    <div class="seg mode-seg">
      <button :class="['seg-item', mode === 'login' ? 'on' : '']" @click="mode = 'login'">登录</button>
      <button :class="['seg-item', mode === 'register' ? 'on' : '']" @click="mode = 'register'">注册</button>
    </div>

    <div class="card form-card">
      <div class="field">
        <label>用户名</label>
        <input v-model="username" class="textfield" placeholder="3–32 个字符" autocomplete="username" />
      </div>
      <div v-if="mode === 'register'" class="field">
        <label>昵称（可选）</label>
        <input v-model="nickname" class="textfield" placeholder="怎么称呼你" />
      </div>
      <div class="field">
        <label>密码</label>
        <input v-model="password" type="password" class="textfield" placeholder="至少 6 位" autocomplete="current-password" />
      </div>
      <button class="btn block submit" :disabled="loading" @click="submit">{{ loading ? '请稍候…' : (mode === 'login' ? '登 录' : '注册并登录') }}</button>
    </div>

    <p class="tips">安全约定：密码仅用于本次登录提交、不保存在本机；数据库与大模型密钥只存在于后端。</p>

    <div class="server">
      <button class="server-toggle" @click="showServer = !showServer">
        <span>服务器设置</span>
        <svg :class="{ open: showServer }" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 9l6 6 6-6"/></svg>
      </button>
      <transition name="fade">
        <div v-if="showServer" class="server-box">
          <input v-model="serverUrl" class="textfield" placeholder="留空 = 走 Vite 代理（推荐）；或填 http://127.0.0.1:8000" />
        </div>
      </transition>
    </div>
  </div>
</template>

<script>
import uni from '../utils/uni'
import config from '../utils/config'
import offline from '../utils/offline'
import { login, register } from '../api/auth'

export default {
  data() {
    return { mode: 'login', username: '', password: '', nickname: '', loading: false, showServer: false, serverUrl: '' }
  },
  mounted() { this.serverUrl = config.baseUrl() },
  methods: {
    saveServer() {
      if (this.serverUrl && this.serverUrl.indexOf('http') === 0) config.setBaseUrl(this.serverUrl)
      else if (this.serverUrl === '') config.setBaseUrl('')
    },
    async submit() {
      this.saveServer()
      const username = this.username.trim()
      if (!username || username.length < 3) { uni.showToast({ title: '用户名至少 3 个字符' }); return }
      if (!this.password || this.password.length < 6) { uni.showToast({ title: '密码至少 6 位' }); return }
      this.loading = true
      try {
        const data = this.mode === 'login'
          ? await login(username, this.password)
          : await register(username, this.password, this.nickname.trim())
        uni.setStorageSync('token', data.access_token)
        uni.setStorageSync('user', data.user)
        offline.init().catch(() => {})
        uni.showToast({ title: this.mode === 'login' ? '登录成功' : '注册成功', icon: 'success' })
        this.$router.push('/study')
      } catch (err) {
        if (!err.message) uni.showToast({ title: '请求失败，请检查服务器地址' })
      } finally { this.loading = false }
    }
  }
}
</script>

<style scoped>
.login-page { display: flex; flex-direction: column; min-height: 100vh; padding-top: calc(40px + env(safe-area-inset-top)); }
.hero { display: flex; flex-direction: column; align-items: center; margin-bottom: 30px; }
.logo {
  width: 86px; height: 86px; border-radius: 21px;
  background: linear-gradient(145deg, #E25A2A, #A23217);
  color: #fff; font-size: 30px; font-weight: 700; letter-spacing: .5px;
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 10px 28px rgba(188, 62, 27, .28);
}
.title { margin-top: 20px; font-size: 32px; font-weight: 700; letter-spacing: 2px; }
.sub { margin-top: 9px; color: var(--label-2); font-size: 13px; line-height: 1.7; max-width: 420px; }
.tag { margin-top: 12px; color: var(--label-3); font-size: 12px; line-height: 1.7; }

.mode-seg { margin: 0 auto 18px; width: min(100%, 480px); }
.form-card { padding: 20px 18px 18px; border-radius: 18px; box-shadow: 0 3px 14px rgba(0, 0, 0, .05); width: min(100%, 480px); margin: 0 auto; }
.field { margin-bottom: 14px; }
.field label { display: block; font-size: 12px; color: var(--label-2); margin: 0 0 7px 2px; }
.submit { margin-top: 6px; }

.tips { margin-top: 18px; text-align: center; font-size: 11px; color: var(--label-3); line-height: 1.7; padding: 0 22px; max-width: 480px; margin-left: auto; margin-right: auto; }
.server { margin-top: 20px; display: flex; flex-direction: column; align-items: center; }
.server-toggle { display: inline-flex; align-items: center; gap: 4px; border: none; background: none; color: var(--tint); font-size: 14px; font-weight: 500; padding: 8px; }
.server-toggle svg { width: 14px; height: 14px; transition: transform .2s ease; }
.server-toggle svg.open { transform: rotate(180deg); }
.server-box { width: 100%; margin-top: 8px; }
.fade-enter-active, .fade-leave-active { transition: opacity .18s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>