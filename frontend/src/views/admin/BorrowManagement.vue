<template>
  <div class="borrow-management-container">
    <Navbar />
    <div class="borrow-management-content">
      <el-card class="management-card">
        <template #header>
          <div class="card-header">
            <el-icon><Operation /></el-icon>
            <span>借阅管理</span>
          </div>
        </template>
        
        <!-- 搜索和筛选 -->
        <div class="search-filter">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-input
                v-model="searchQuery"
                placeholder="搜索用户名或图书名称"
                prefix-icon="Search"
                @keyup.enter="handleSearch"
              >
                <template #append>
                  <el-button type="primary" @click="handleSearch">搜索</el-button>
                </template>
              </el-input>
            </el-col>
            <el-col :span="8">
              <el-select
                v-model="statusFilter"
                placeholder="按状态筛选"
                clearable
                @change="handleFilter"
              >
                <el-option label="全部" value="" />
                <el-option label="借阅中" value="borrowed" />
                <el-option label="已归还" value="returned" />
                <el-option label="已逾期" value="overdue" />
              </el-select>
            </el-col>
            <el-col :span="4">
              <el-button type="default" @click="resetFilters">重置</el-button>
            </el-col>
          </el-row>
        </div>
        
        <!-- 借阅记录列表 -->
        <el-table :data="borrowRecords" style="width: 100%">
          <el-table-column type="index" label="序号" width="80" />
          <el-table-column prop="user.username" label="用户" width="120" />
          <el-table-column prop="book.title" label="图书" width="200" />
          <el-table-column prop="borrow_date" label="借阅日期" width="150" />
          <el-table-column prop="due_date" label="应归还日期" width="150" />
          <el-table-column prop="return_date" label="实际归还日期" width="150" />
          <el-table-column prop="status" label="状态" width="100">
            <template #default="scope">
              <el-tag :type="getStatusType(scope.row.status)">
                {{ getStatusText(scope.row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="150">
            <template #default="scope">
              <el-button
                type="primary"
                size="small"
                @click="handleReturn(scope.row.id)"
                :disabled="scope.row.status !== 'borrowed'"
              >
                <el-icon><Check /></el-icon>
                归还
              </el-button>
              <el-button type="danger" size="small" @click="handleDelete(scope.row.id)">
                <el-icon><Delete /></el-icon>
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
        
        <!-- 分页 -->
        <div class="pagination" v-if="totalRecords > 0">
          <el-pagination
            :current-page="currentPage"
            :page-size="pageSize"
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
import { Operation, Search, Check, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import Navbar from '../../components/Navbar.vue'
import axios from 'axios'

const borrowRecords = ref([])
const totalRecords = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const searchQuery = ref('')
const statusFilter = ref('')

const fetchBorrowRecords = async () => {
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    
    if (searchQuery.value) {
      params.search = searchQuery.value
    }
    
    if (statusFilter.value) {
      params.status = statusFilter.value
    }
    
    const response = await axios.get('/api/borrow-records/', { params })
    borrowRecords.value = response.data.results
    totalRecords.value = response.data.count
  } catch (error) {
    console.error('获取借阅记录失败:', error)
  }
}

const handleSearch = () => {
  currentPage.value = 1
  fetchBorrowRecords()
}

const handleFilter = () => {
  currentPage.value = 1
  fetchBorrowRecords()
}

const resetFilters = () => {
  searchQuery.value = ''
  statusFilter.value = ''
  currentPage.value = 1
  fetchBorrowRecords()
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

const handleReturn = async (id) => {
  try {
    await ElMessageBox.confirm('确定要归还这本书吗？', '确认', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'info'
    })
    
    await axios.put(`/api/borrow-records/${id}/return/`)
    ElMessage.success('归还成功')
    fetchBorrowRecords()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('归还失败:', error)
      ElMessage.error('归还失败')
    }
  }
}

const handleDelete = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除这条借阅记录吗？', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await axios.delete(`/api/borrow-records/${id}/`)
    ElMessage.success('删除成功')
    fetchBorrowRecords()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
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
  fetchBorrowRecords()
})
</script>

<style scoped>
.borrow-management-container {
  padding: 20px;
}

.borrow-management-content {
  max-width: 1200px;
  margin: 0 auto;
}

.management-card {
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

.search-filter {
  margin-bottom: 20px;
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
</style>
