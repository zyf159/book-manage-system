<template>
  <div class="home-container">
    <Navbar />
    <div class="home-content">
      <el-card class="welcome-card">
        <template #header>
          <div class="card-header">
            <el-icon><Bell /></el-icon>
            <span>欢迎使用图书管理系统</span>
          </div>
        </template>
        <div class="welcome-message">
          <h3>你好，{{ user?.username }}！</h3>
          <p v-if="user?.role === 'admin'">作为管理员，你可以管理图书、用户和借阅记录。</p>
          <p v-else>作为读者，你可以浏览图书、申请借阅和查看个人借阅记录。</p>
        </div>
        <el-divider />
        <div class="system-status">
          <h4>系统状态</h4>
          <el-row :gutter="20">
            <el-col :span="8">
              <el-card shadow="hover" class="status-card">
                <div class="status-item">
                  <el-icon class="status-icon"><Collection /></el-icon>
                  <div class="status-info">
                    <div class="status-value">{{ totalBooks }}</div>
                    <div class="status-label">总图书数</div>
                  </div>
                </div>
              </el-card>
            </el-col>
            <el-col :span="8">
              <el-card shadow="hover" class="status-card">
                <div class="status-item">
                  <el-icon class="status-icon"><TakeawayBox /></el-icon>
                  <div class="status-info">
                    <div class="status-value">{{ borrowedBooks }}</div>
                    <div class="status-label">已借出</div>
                  </div>
                </div>
              </el-card>
            </el-col>
            <el-col :span="8">
              <el-card shadow="hover" class="status-card">
                <div class="status-item">
                  <el-icon class="status-icon"><Check /></el-icon>
                  <div class="status-info">
                    <div class="status-value">{{ availableBooks }}</div>
                    <div class="status-label">可借图书</div>
                  </div>
                </div>
              </el-card>
            </el-col>
          </el-row>
        </div>
      </el-card>
      
      <el-card class="recent-books" v-if="recentBooks.length > 0">
        <template #header>
          <div class="card-header">
            <el-icon><DocumentAdd /></el-icon>
            <span>最近添加的图书</span>
          </div>
        </template>
        <el-row :gutter="20">
          <el-col :span="8" v-for="book in recentBooks" :key="book.id">
            <el-card :body-style="{ padding: '0px' }" class="book-card">
              <div class="book-cover">
                <img :src="book.cover_image || 'https://via.placeholder.com/200x300'" :alt="book.title" />
              </div>
              <div class="book-info">
                <h4>{{ book.title }}</h4>
                <p>{{ book.author }}</p>
                <p class="book-status">
                  <el-tag :type="book.available_quantity > 0 ? 'success' : 'danger'">
                    {{ book.available_quantity > 0 ? '可借' : '已借出' }}
                  </el-tag>
                </p>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Bell, Collection, TakeawayBox, Check, DocumentAdd } from '@element-plus/icons-vue'
import Navbar from '../components/Navbar.vue'
import store from '../store'
import axios from 'axios'

const user = computed(() => store.state.user)
const totalBooks = ref(0)
const borrowedBooks = ref(0)
const availableBooks = ref(0)
const recentBooks = ref([])

const fetchSystemStatus = async () => {
  try {
    // 获取系统状态
    const statusResponse = await axios.get('/api/borrow-records/status/')
    const statusData = statusResponse.data
    
    totalBooks.value = statusData.total_books
    borrowedBooks.value = statusData.borrowed_books
    availableBooks.value = statusData.available_books
    
    // 获取最近添加的图书
    const booksResponse = await axios.get('/api/books/')
    recentBooks.value = booksResponse.data.results.slice(0, 3)
  } catch (error) {
    console.error('获取系统状态失败:', error)
  }
}

onMounted(() => {
  fetchSystemStatus()
})
</script>

<style scoped>
.home-container {
  padding: 20px;
}

.home-content {
  max-width: 1200px;
  margin: 0 auto;
}

.welcome-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  align-items: center;
}

.card-header span {
  margin-left: 10px;
  font-weight: bold;
}

.welcome-message {
  margin: 20px 0;
}

.system-status {
  margin-top: 20px;
}

.status-card {
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.status-item {
  display: flex;
  align-items: center;
  width: 100%;
  padding: 0 20px;
}

.status-icon {
  font-size: 48px;
  color: #409eff;
  margin-right: 20px;
}

.status-info {
  flex: 1;
}

.status-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.status-label {
  font-size: 14px;
  color: #606266;
}

.recent-books {
  margin-top: 20px;
}

.book-card {
  height: 350px;
  display: flex;
  flex-direction: column;
}

.book-cover {
  height: 200px;
  overflow: hidden;
}

.book-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.book-info {
  padding: 15px;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.book-info h4 {
  margin-bottom: 10px;
  font-size: 16px;
}

.book-info p {
  margin-bottom: 10px;
  color: #606266;
  font-size: 14px;
}

.book-status {
  margin-top: auto;
}
</style>
