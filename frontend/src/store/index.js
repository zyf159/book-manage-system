import { reactive, ref } from 'vue'

// 状态管理
const state = reactive({
  user: JSON.parse(localStorage.getItem('user')) || null,
  token: localStorage.getItem('token') || null,
  loading: false,
  error: null
})

// 登录
const login = (user, token) => {
  state.user = user
  state.token = token
  localStorage.setItem('user', JSON.stringify(user))
  localStorage.setItem('token', token)
}

// 登出
const logout = () => {
  state.user = null
  state.token = null
  localStorage.removeItem('user')
  localStorage.removeItem('token')
}

// 设置加载状态
const setLoading = (loading) => {
  state.loading = loading
}

// 设置错误信息
const setError = (error) => {
  state.error = error
}

export default {
  state,
  login,
  logout,
  setLoading,
  setError
}
