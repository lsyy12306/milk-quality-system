import axios from 'axios'

// 后端返回的时间是 naive UTC（如 2026-10-30T02:35:54.933235，无时区）。
// 统一按北京时间(Asia/Shanghai)展示，避免被当成当地时区导致差 8 小时。
export function fmtBeijing(v) {
  if (!v) return ''
  let iso = v
  // 没有时区偏移的 naive 字符串，按 UTC 解析
  if (/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/.test(v) && !/[Zz]|[+-]\d{2}:?\d{2}$/.test(v)) {
    iso = v + 'Z'
  }
  const d = new Date(iso)
  if (isNaN(d.getTime())) return v.replace('T', ' ').slice(0, 19)
  const parts = {}
  for (const p of new Intl.DateTimeFormat('zh-CN', {
    timeZone: 'Asia/Shanghai', year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false,
  }).formatToParts(d)) parts[p.type] = p.value
  return `${parts.year}-${parts.month}-${parts.day} ${parts.hour}:${parts.minute}:${parts.second}`
}

// 后端地址：开发期由 Vite 代理 /api -> http://127.0.0.1:8000
// 若直接连后端（如打包后单独部署），设置 VITE_API_BASE 为后端地址
const BASE = import.meta.env.VITE_API_BASE || ''

const api = axios.create({ baseURL: BASE })

// 自动附加 JWT
api.interceptors.request.use((config) => {
  const t = localStorage.getItem('token')
  if (t) config.headers.Authorization = `Bearer ${t}`
  return config
})

// 统一处理 401：登录失效则跳登录
api.interceptors.response.use(
  (r) => r,
  (err) => {
    if (err.response && err.response.status === 401 && localStorage.getItem('token')) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

export const predict = (data) => api.post('/api/predict', data)
export const predictCsv = (file, sourceId) => {
  const fd = new FormData()
  fd.append('file', file)
  const params = sourceId ? { source_id: sourceId } : {}
  return api.post('/api/predict/csv', fd, { params })
}
export const register = (data) => api.post('/api/auth/register', data)
export const login = (data) => api.post('/api/auth/login', data)
export const getHistory = () => api.get('/api/history')
export const getHistoryBatches = () => api.get('/api/history/batches')
export const exportHistory = (batch) =>
  api.get('/api/history/export',
    batch ? { params: { batch }, responseType: 'blob' } : { responseType: 'blob' })
export const getIndicators = () => api.get('/api/indicators')
export const getModelInfo = () => api.get('/api/model/info')

// 个人中心
export const getMe = () => api.get('/api/auth/me')
export const updateMe = (data) => api.put('/api/auth/me', data)
export const updatePassword = (data) => api.put('/api/auth/password', data)

// 企业来源档案
export const getSources = () => api.get('/api/sources')
export const createSource = (data) => api.post('/api/sources', data)
export const updateSource = (id, data) => api.put(`/api/sources/${id}`, data)
export const deleteSource = (id) => api.delete(`/api/sources/${id}`)

// Agent 智能体接口
export const agentAnalyze = (data) => api.post('/api/agent/analyze', data)
export const agentChat = (data) => api.post('/api/agent/chat', data)
export const agentTrends = (data) => api.post('/api/agent/trends', data)
export const agentReport = (data) => api.post('/api/agent/report', data)
export const getAgentTools = () => api.get('/api/agent/tools')
export const agentAnalyzeBatch = (data) => api.post('/api/agent/analyze/batch', data)
export const agentDailyReport = (data) => api.post('/api/agent/daily-report', data)

export default api
