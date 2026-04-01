<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <div class="login-header">
          <h2>图书管理系统</h2>
          <p>登录</p>
        </div>
      </template>
      <el-form :model="loginForm" :rules="loginRules" ref="loginFormRef" label-width="80px">
        <el-form-item label="学号" prop="student_id">
          <el-input v-model="loginForm.student_id" placeholder="请输入学号" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="loginForm.password" type="password" placeholder="请输入密码" show-password />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleLogin" :loading="loading">登录</el-button>
          <el-button @click="navigateToRegister">注册</el-button>
        </el-form-item>
        <div class="login-footer">
          <a href="#">忘记密码？</a>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import store from '../store'

const router = useRouter()
const loginFormRef = ref(null)
const loading = ref(false)

const loginForm = reactive({
  student_id: '',
  password: ''
})

const loginRules = {
  student_id: [
    { required: true, message: '请输入学号', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        const response = await axios.post('/api/users/login/', loginForm)
        const { access, user } = response.data
        store.login(user, access)
        
        // 根据用户角色跳转到不同页面
        if (user.role === 'admin') {
          router.push('/admin')
        } else {
          router.push('/')
        }
      } catch (error) {
        console.error('登录失败:', error)
        if (error.response) {
          ElMessage.error(error.response.data.error || '登录失败')
        } else {
          ElMessage.error('网络错误，请稍后重试')
        }
      } finally {
        loading.value = false
      }
    }
  })
}

const navigateToRegister = () => {
  router.push('/register')
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f5f5f5;
}

.login-card {
  width: 400px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.login-header {
  text-align: center;
}

.login-header h2 {
  color: #409eff;
  margin-bottom: 10px;
}

.login-footer {
  text-align: right;
  margin-top: 10px;
}

.login-footer a {
  color: #409eff;
  text-decoration: none;
}
</style>
