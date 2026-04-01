<template>
  <div class="user-management-container">
    <Navbar />
    <div class="user-management-content">
      <el-card class="management-card">
        <template #header>
          <div class="card-header">
            <el-icon><User /></el-icon>
            <span>用户管理</span>
          </div>
        </template>
        
        <!-- 搜索 -->
        <div class="search-filter">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-input
                v-model="searchQuery"
                placeholder="搜索用户名或学号"
                prefix-icon="Search"
                @keyup.enter="handleSearch"
              >
                <template #append>
                  <el-button type="primary" @click="handleSearch">搜索</el-button>
                </template>
              </el-input>
            </el-col>
            <el-col :span="4">
              <el-button type="default" @click="resetFilters">重置</el-button>
            </el-col>
          </el-row>
        </div>
        
        <!-- 用户列表 -->
        <el-table :data="users" style="width: 100%">
          <el-table-column type="index" label="序号" width="80" />
          <el-table-column prop="username" label="用户名" width="120" />
          <el-table-column prop="student_id" label="学号" width="150" />
          <el-table-column prop="email" label="邮箱" width="200" />
          <el-table-column prop="role" label="角色" width="100">
            <template #default="scope">
              <el-tag :type="scope.row.role === 'admin' ? 'danger' : 'success'">
                {{ scope.row.role === 'admin' ? '管理员' : '普通用户' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="date_joined" label="注册时间" width="180" />
          <el-table-column label="操作" width="150">
            <template #default="scope">
              <el-button type="primary" size="small" @click="handleView(scope.row)">
                <el-icon><View /></el-icon>
                查看
              </el-button>
            </template>
          </el-table-column>
        </el-table>
        
        <!-- 分页 -->
        <div class="pagination" v-if="totalUsers > 0">
          <el-pagination
            :current-page="currentPage"
            :page-size="pageSize"
            :page-sizes="[10, 20, 50]"
            layout="total, sizes, prev, pager, next, jumper"
            :total="totalUsers"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
        
        <!-- 空状态 -->
        <div class="empty-state" v-if="users.length === 0">
          <el-empty description="暂无用户" />
        </div>
      </el-card>
      
      <!-- 用户详情对话框 -->
      <el-dialog
        v-model="dialogVisible"
        title="用户详情"
        width="500px"
      >
        <el-form :model="currentUser" label-width="100px">
          <el-form-item label="用户名">
            <el-input v-model="currentUser.username" disabled />
          </el-form-item>
          <el-form-item label="学号">
            <el-input v-model="currentUser.student_id" disabled />
          </el-form-item>
          <el-form-item label="邮箱">
            <el-input v-model="currentUser.email" disabled />
          </el-form-item>
          <el-form-item label="角色">
            <el-tag :type="currentUser.role === 'admin' ? 'danger' : 'success'">
              {{ currentUser.role === 'admin' ? '管理员' : '普通用户' }}
            </el-tag>
          </el-form-item>
          <el-form-item label="注册时间">
            <el-input v-model="currentUser.date_joined" disabled />
          </el-form-item>
        </el-form>
        <template #footer>
          <span class="dialog-footer">
            <el-button @click="dialogVisible = false">关闭</el-button>
          </span>
        </template>
      </el-dialog>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { User, Search, View } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import Navbar from '../../components/Navbar.vue'
import axios from 'axios'

const users = ref([])
const totalUsers = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const searchQuery = ref('')
const dialogVisible = ref(false)
const currentUser = reactive({})

const fetchUsers = async () => {
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    
    if (searchQuery.value) {
      params.search = searchQuery.value
    }
    
    console.log('Fetching users with params:', params)
    
    // 调用用户管理的API接口
    const response = await axios.get('/api/users/', { params })
    console.log('Users response:', response.data)
    
    users.value = response.data.results || []
    totalUsers.value = response.data.count || 0
  } catch (error) {
    console.error('获取用户列表失败:', error)
    console.error('Error response:', error.response?.data)
    ElMessage.error(error.response?.data?.error || '获取用户列表失败')
  }
}

const handleSearch = () => {
  currentPage.value = 1
  fetchUsers()
}

const resetFilters = () => {
  searchQuery.value = ''
  currentPage.value = 1
  fetchUsers()
}

const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  fetchUsers()
}

const handleCurrentChange = (page) => {
  currentPage.value = page
  fetchUsers()
}

const handleView = (user) => {
  Object.assign(currentUser, user)
  dialogVisible.value = true
}

onMounted(() => {
  fetchUsers()
})
</script>

<style scoped>
.user-management-container {
  padding: 20px;
}

.user-management-content {
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
