<template>
  <div class="borrow-records-container">
    <Navbar />
    <div class="borrow-records-content">
      <el-card class="records-card">
        <template #header>
          <div class="card-header">
            <el-icon><List /></el-icon>
            <span>我的借阅记录</span>
          </div>
        </template>
        <el-table :data="borrowRecords" style="width: 100%">
          <el-table-column prop="book.title" label="图书名称" width="200">
            <template #default="scope">
              <span @click="navigateToBookDetail(scope.row.book.id)">{{ scope.row.book.title }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="borrow_date" label="借阅日期" width="180" />
          <el-table-column prop="due_date" label="应归还日期" width="180" />
          <el-table-column prop="return_date" label="实际归还日期" width="180" />
          <el-table-column prop="status" label="状态" width="120">
            <template #default="scope">
              <el-tag :type="getStatusType(scope.row.status)">
                {{ getStatusText(scope.row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="剩余天数" width="100" v-if="false">
            <template #default="scope">
              <span v-if="scope.row.status === 'borrowed'" :class="getDaysClass(scope.row.due_date)">
                {{ calculateDaysLeft(scope.row.due_date) }}
              </span>
              <span v-else>-</span>
            </template>
          </el-table-column>
        </el-table>
        
        <!-- 分页 -->
        <div class="pagination" v-if="totalRecords > 0">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50]"
            layout="total, sizes, prev, pager, next, jumper"
            :total="totalRecords"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
        
        <!-- 空状态 -->
        <div class="empty-state" v-if="borrowRecords.length === 0">
          <el-empty description="暂无借阅记录" />
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { List } from '@element-plus/icons-vue'
import Navbar from '../components/Navbar.vue'
import axios from 'axios'

const router = useRouter()
const borrowRecords = ref([])
const totalRecords = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)

const fetchBorrowRecords = async () => {
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    
    const response = await axios.get('/api/borrow-records/', { params })
    borrowRecords.value = response.data.results
    totalRecords.value = response.data.count
  } catch (error) {
    console.error('获取借阅记录失败:', error)
  }
}

const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  fetchBorrowRecords()
}

const handleCurrentChange = (page) => {
  currentPage.value = page
  fetchBorrowRecords()
}

const navigateToBookDetail = (bookId) => {
  router.push(`/books/${bookId}`)
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

const calculateDaysLeft = (dueDate) => {
  const today = new Date()
  const due = new Date(dueDate)
  const diffTime = due - today
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  return diffDays
}

const getDaysClass = (dueDate) => {
  const daysLeft = calculateDaysLeft(dueDate)
  if (daysLeft < 0) return 'days-overdue'
  if (daysLeft <= 3) return 'days-warning'
  return 'days-normal'
}

onMounted(() => {
  fetchBorrowRecords()
})
</script>

<style scoped>
.borrow-records-container {
  padding: 20px;
}

.borrow-records-content {
  max-width: 1200px;
  margin: 0 auto;
}

.records-card {
  margin-top: 20px;
}

.card-header {
  display: flex;
  align-items: center;
}

.card-header span {
  margin-left: 10px;
  font-weight: bold;
}

.el-table-column:nth-child(2) span {
  color: #409eff;
  cursor: pointer;
}

.el-table-column:nth-child(2) span:hover {
  text-decoration: underline;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.empty-state {
  padding: 40px 0;
  text-align: center;
}

.days-normal {
  color: #67c23a;
}

.days-warning {
  color: #e6a23c;
  font-weight: bold;
}

.days-overdue {
  color: #f56c6c;
  font-weight: bold;
}
</style>
