import config from '../utils/config'
import { toast } from '../utils/ui'
import router from '../router'

function getToken() {
  try { return JSON.parse(localStorage.getItem('ct4_token')) } catch (e) { return localStorage.getItem('ct4_token') }
}

async function request(method, url, data) {
  const base = config.baseUrl()
  const headers = { 'Content-Type': 'application/json' }
  const token = getToken()
  if (token) headers.Authorization = 'Bearer ' + token
  let res
  try {
    res = await fetch(base + url, {
      method: method || 'GET',
      headers,
      body: data ? JSON.stringify(data) : undefined
    })
  } catch (e) {
    const err = new Error('网络连接失败')
    err.network = true
    throw err
  }
  let body = null
  try { body = await res.json() } catch (e) { /* noop */ }
  if (res.status === 401) {
    localStorage.removeItem('ct4_token')
    localStorage.removeItem('ct4_user')
    toast('请先登录', 'none')
    router.push('/login')
    throw new Error('登录已失效')
  }
  if (res.status >= 200 && res.status < 300) return body
  const detail = body && body.detail
  const msg = detail ? (typeof detail === 'string' ? detail : JSON.stringify(detail)) : ('请求失败(' + res.status + ')')
  toast(msg, 'none')
  throw new Error(msg)
}

export const get = (url, params) => {
  let q = ''
  if (params) {
    const s = Object.keys(params).filter((k) => params[k] !== '' && params[k] !== undefined && params[k] !== null)
      .map((k) => encodeURIComponent(k) + '=' + encodeURIComponent(params[k])).join('&')
    if (s) q = '?' + s
  }
  return request('GET', url + q)
}
export const post = (url, data) => request('POST', url, data || {})
export default { request, get, post }