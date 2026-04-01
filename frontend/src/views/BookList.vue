<template>
  <div class="book-list-container">
    <Navbar />
    <div class="book-list-content">
      <el-card class="search-card">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-input
              v-model="searchQuery"
              placeholder="搜索图书名称、作者或ISBN"
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
              v-model="categoryFilter"
              placeholder="按分类筛选"
              clearable
              @change="handleFilter"
            >
              <el-option
                v-for="category in categories"
                :key="category"
                :label="category"
                :value="category"
              />
            </el-select>
          </el-col>
          <el-col :span="4">
            <el-button type="default" @click="resetFilters">重置</el-button>
          </el-col>
        </el-row>
      </el-card>
      
      <el-card class="books-card">
        <template #header>
          <div class="card-header">
            <el-icon><Collection /></el-icon>
            <span>图书列表</span>
            <span class="book-count">(共 {{ totalBooks }} 本)</span>
          </div>
        </template>
        <el-row :gutter="20">
          <el-col :xs="24" :sm="12" :md="8" :lg="6" v-for="book in books" :key="book.id">
            <el-card :body-style="{ padding: '0px' }" class="book-card">
              <div class="book-cover">
                <img :src="book.cover_image || 'https://via.placeholder.com/200x300'" :alt="book.title" />
              </div>
              <div class="book-info">
                <h4 @click="navigateToDetail(book.id)">{{ book.title }}</h4>
                <p>{{ book.author }}</p>
                <p class="book-publisher">{{ book.publisher }}</p>
                <div class="book-status">
                  <el-tag :type="book.available_quantity > 0 ? 'success' : 'danger'">
                    {{ book.available_quantity > 0 ? '可借' : '已借出' }}
                  </el-tag>
                  <span class="book-price">¥{{ book.price }}</span>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
        
        <!-- 分页 -->
        <div class="pagination" v-if="totalBooks > 0">
          <el-pagination
            :current-page="currentPage"
            :page-size="pageSize"
            :page-sizes="[12, 24, 36]"
            layout="total, sizes, prev, pager, next, jumper"
            :total="totalBooks"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
        
        <!-- 空状态 -->
        <div class="empty-state" v-if="books.length === 0">
          <el-empty description="暂无图书" />
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Collection, Search } from '@element-plus/icons-vue'
import Navbar from '../components/Navbar.vue'
import axios from 'axios'

const router = useRouter()
const books = ref([])
const totalBooks = ref(0)
const currentPage = ref(1)
const pageSize = ref(12)
const searchQuery = ref('')
const categoryFilter = ref('')
const categories = ref([
  '计算机科学', '文学', '历史', '哲学', '艺术', '教育', '科学', '工程'
])

const fetchBooks = async () => {
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    
    if (searchQuery.value) {
      params.search = searchQuery.value
    }
    
    if (categoryFilter.value) {
      params.category = categoryFilter.value
    }
    
    const response = await axios.get('/api/books/', { params })
    books.value = response.data.results
    totalBooks.value = response.data.count
  } catch (error) {
    console.error('获取图书列表失败:', error)
  }
}

const handleSearch = () => {
  currentPage.value = 1
  fetchBooks()
}

const handleFilter = () => {
  currentPage.value = 1
  fetchBooks()
}

const resetFilters = () => {
  searchQuery.value = ''
  categoryFilter.value = ''
  currentPage.value = 1
  fetchBooks()
}

const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  fetchBooks()
}

const handleCurrentChange = (page) => {
  currentPage.value = page
  fetchBooks()
}

const navigateToDetail = (id) => {
  router.push(`/books/${id}`)
}

onMounted(() => {
  fetchBooks()
})
</script>

<style scoped>
.book-list-container {
  padding: 20px;
}

.book-list-content {
  max-width: 1200px;
  margin: 0 auto;
}

.search-card {
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

.book-count {
  margin-left: 10px;
  font-size: 14px;
  color: #606266;
}

.books-card {
  margin-top: 20px;
}

.book-card {
  height: 400px;
  display: flex;
  flex-direction: column;
  transition: all 0.3s;
  cursor: pointer;
}

.book-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
}

.book-cover {
  height: 240px;
  overflow: hidden;
}

.book-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}

.book-card:hover .book-cover img {
  transform: scale(1.05);
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
  cursor: pointer;
  transition: color 0.3s;
}

.book-info h4:hover {
  color: #409eff;
}

.book-info p {
  margin-bottom: 8px;
  color: #606266;
  font-size: 14px;
}

.book-publisher {
  font-size: 12px;
  opacity: 0.8;
}

.book-status {
  margin-top: auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 10px;
}

.book-price {
  font-size: 14px;
  font-weight: bold;
  color: #f56c6c;
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
