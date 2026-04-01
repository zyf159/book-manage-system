<template>
  <div class="dashboard-container">
    <Navbar />
    <div class="dashboard-content">
      <el-card class="stats-card">
        <template #header>
          <div class="card-header">
            <el-icon><DataAnalysis /></el-icon>
            <span>系统统计</span>
          </div>
        </template>
        <el-row :gutter="20">
          <el-col :span="6">
            <el-card shadow="hover" class="stat-item">
              <div class="stat-content">
                <div class="stat-value">{{ totalBooks }}</div>
                <div class="stat-label">总图书数</div>
              </div>
              <el-icon class="stat-icon"><Collection /></el-icon>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="stat-item">
              <div class="stat-content">
                <div class="stat-value">{{ borrowedBooks }}</div>
                <div class="stat-label">已借出</div>
              </div>
              <el-icon class="stat-icon"><TakeawayBox /></el-icon>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="stat-item">
              <div class="stat-content">
                <div class="stat-value">{{ availableBooks }}</div>
                <div class="stat-label">可借图书</div>
              </div>
              <el-icon class="stat-icon"><Check /></el-icon>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="stat-item">
              <div class="stat-content">
                <div class="stat-value">{{ totalUsers }}</div>
                <div class="stat-label">总用户数</div>
              </div>
              <el-icon class="stat-icon"><User /></el-icon>
            </el-card>
          </el-col>
        </el-row>
      </el-card>
      
      <el-row :gutter="20">
        <el-col :span="12">
          <el-card class="recent-borrows">
            <template #header>
              <div class="card-header">
                <el-icon><Clock /></el-icon>
                <span>最近借阅记录</span>
              </div>
            </template>
            <el-table :data="recentBorrows" style="width: 100%">
              <el-table-column prop="user.username" label="用户" width="120" />
              <el-table-column prop="book.title" label="图书" width="200" />
              <el-table-column prop="borrow_date" label="借阅日期" width="150" />
              <el-table-column prop="due_date" label="应归还日期" width="150" />
              <el-table-column prop="status" label="状态" width="100">
                <template #default="scope">
                  <el-tag :type="getStatusType(scope.row.status)">
                    {{ getStatusText(scope.row.status) }}
                  </el-tag>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card class="popular-books">
            <template #header>
              <div class="card-header">
                <el-icon><Star /></el-icon>
                <span>热门图书</span>
              </div>
            </template>
            <el-table :data="popularBooks" style="width: 100%">
              <el-table-column prop="title" label="图书名称" width="200" />
              <el-table-column prop="author" label="作者" width="120" />
              <el-table-column prop="borrow_count" label="借阅次数" width="100" />
              <el-table-column prop="available_quantity" label="可借数量" width="100" />
            </el-table>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { DataAnalysis, Collection, TakeawayBox, Check, User, Clock, Star } from '@element-plus/icons-vue'
import Navbar from '../../components/Navbar.vue'
import axios from 'axios'

const totalBooks = ref(0)
const borrowedBooks = ref(0)
const availableBooks = ref(0)
const totalUsers = ref(0)
const recentBorrows = ref([])
const popularBooks = ref([])

const fetchDashboardData = async () => {
  try {
    // 获取系统状态
    const statusResponse = await axios.get('/api/borrow-records/status/')
    const statusData = statusResponse.data
    
    totalBooks.value = statusData.total_books
    borrowedBooks.value = statusData.borrowed_books
    availableBooks.value = statusData.available_books
    
    // 获取总用户数
    const usersResponse = await axios.get('/api/users/profile/')
    totalUsers.value = 1 // 暂时硬编码，实际应调用后端用户统计接口
    
    // 获取最近借阅记录
    const borrowResponse = await axios.get('/api/borrow-records/')
    recentBorrows.value = borrowResponse.data.results.slice(0, 5)
    
    // 获取热门图书（模拟数据）
    const bookResponse = await axios.get('/api/books/')
    popularBooks.value = bookResponse.data.results.slice(0, 5).map(book => ({
      ...book,
      borrow_count: Math.floor(Math.random() * 100) + 1
    }))
  } catch (error) {
    console.error('获取仪表盘数据失败:', error)
  }
}

const getStatusType = (status) => {
  switch (status) {
    case 'borrowed': return 'warning'
    case 'returned': return 'success'
    case 'overdue': return 'danger'
    default: return 'info'
  }
}

const getStatusText = (status) => {
  switch (status) {
    case 'borrowed': return '借阅中'
    case 'returned': return '已归还'
    case 'overdue': return '已逾期'
    default: return '未知状态'
  }
}

onMounted(() => {
  fetchDashboardData()
})
</script>

<style scoped>
.dashboard-container {
  padding: 20px;
}

.dashboard-content {
  max-width: 1200px;
  margin: 0 auto;
}

.stats-card {
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

.stat-item {
  position: relative;
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.stat-content {
  text-align: center;
  z-index: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: #606266;
}

.stat-icon {
  position: absolute;
  right: 20px;
  bottom: 20px;
  font-size: 48px;
  color: rgba(64, 158, 255, 0.1);
  z-index: 0;
}

.recent-borrows,
.popular-books {
  margin-top: 20px;
  height: 300px;
}
</style>
