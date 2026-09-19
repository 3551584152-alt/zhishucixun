// uni-app API 的 Web 适配层：让迁移过来的页面逻辑尽量少改动
import router from '../router'
import { toast } from './ui'

function nav(url) {
  const map = { login: '/login', study: '/study', plan: '/plan', ai: '/ai', stats: '/stats', notebook: '/notebook', dict: '/dict' }
  for (const k of Object.keys(map)) {
    if (url.indexOf('/pages/' + k + '/') >= 0) {
      router.push(map[k])
      return true
    }
  }
  return false
}

const uni = {
  getStorageSync(key) {
    try { return JSON.parse(localStorage.getItem('ct4_' + key)) } catch (e) { return localStorage.getItem('ct4_' + key) }
  },
  setStorageSync(key, val) {
    localStorage.setItem('ct4_' + key, JSON.stringify(val))
  },
  removeStorageSync(key) {
    localStorage.removeItem('ct4_' + key)
  },
  showToast(o) { toast(o.title || '', o.icon || 'none') },
  showLoading(o) { toast((o && o.title) || '处理中…', 'none', 60000) },
  hideLoading() {},
  reLaunch(o) { if (o && o.url) nav(o.url) },
  switchTab(o) { if (o && o.url) nav(o.url) },
  navigateTo(o) { if (o && o.url) nav(o.url) },
  navigateBack() { router.back() },
  getSystemInfoSync() { return { statusBarHeight: 0 } },
  request() {}
}
export default uni