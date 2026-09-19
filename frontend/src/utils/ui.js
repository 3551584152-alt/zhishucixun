// 轻量全局 toast（替代 uni.showToast）
import { reactive } from 'vue'

export const toastState = reactive({ show: false, text: '', icon: '' })
let timer = null

export function toast(text, icon = 'none', duration = 2000) {
  toastState.text = text
  toastState.icon = icon
  toastState.show = true
  if (timer) clearTimeout(timer)
  timer = setTimeout(() => { toastState.show = false }, duration)
}

export function loading(show, text) {
  // 简单 loading：复用 toast 无限显示由调用方关闭
  if (show) toast(text || '处理中…', 'none', 60000)
}