// 接口地址配置：默认走 Vite 代理（同源 /api -> Django :8000），
// 也可在登录页“服务器设置”里填完整地址(如 http://127.0.0.1:8000) 直接跨域调试。
const DEFAULT_BASE_URL = ''

function baseUrl() {
  const saved = localStorage.getItem('ct4_server_url')
  return saved || DEFAULT_BASE_URL
}

function setBaseUrl(url) {
  const clean = (url || '').trim().replace(/\/+$/, '')
  localStorage.setItem('ct4_server_url', clean)
  return clean
}

export default { baseUrl, setBaseUrl }