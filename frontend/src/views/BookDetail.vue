<template>
  <div class="book-detail-container">
    <Navbar />
    <div class="book-detail-content">
      <el-card class="book-detail-card">
        <el-row :gutter="20">
          <el-col :span="8">
            <div class="book-cover">
              <img :src="book.cover_image || 'https://via.placeholder.com/300x450'" :alt="book.title" />
            </div>
          </el-col>
          <el-col :span="16">
            <div class="book-info">
              <h2>{{ book.title }}</h2>
              <p class="book-author">作者：{{ book.author }}</p>
              <p class="book-publisher">出版社：{{ book.publisher }}</p>
              <p class="book-isbn">ISBN：{{ book.isbn }}</p>
              <p class="book-category">分类：{{ book.category }}</p>
              <p class="book-location">馆藏地点：{{ book.location }}</p>
              <p class="book-call-number">索书号：{{ book.call_number }}</p>
              <p class="book-price">定价：¥{{ book.price }}</p>
              <div class="book-stock">
                <el-tag :type="book.available_quantity > 0 ? 'success' : 'danger'">
                  可借数量：{{ book.available_quantity }}
                </el-tag>
                <el-tag type="info">
                  总数量：{{ book.total_quantity }}
                </el-tag>
              </div>
              <el-button
                type="primary"
                size="large"
                @click="handleBorrow"
                :disabled="book.available_quantity <= 0 || loading"
                :loading="loading"
                class="borrow-button"
              >
                申请借阅
              </el-button>
            </div>
          </el-col>
        </el-row>
        <el-divider />
        <div class="book-description">
          <h3>内容简介</h3>
          <p>{{ book.description || '暂无简介' }}</p>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import Navbar from '../components/Navbar.vue'
import axios from 'axios'

const route = useRoute()
const bookId = route.params.id
const book = ref({})
const loading = ref(false)

const fetchBookDetail = async () => {
  try {
    const response = await axios.get(`/api/books/${bookId}/`)
    book.value = response.data
  } catch (error) {
    console.error('获取图书详情失败:', error)
    ElMessage.error('获取图书详情失败')
  }
}

const handleBorrow = async () => {
  loading.value = true
  try {
    await axios.post('/api/borrow-records/', {
      book_id: parseInt(bookId)
    })
    ElMessage.success('借阅申请成功')
    // 刷新图书信息
    fetchBookDetail()
  } catch (error) {
    console.error('借阅失败:', error)
    if (error.response) {
      ElMessage.error(error.response.data.error || '借阅失败')
    } else {
      ElMessage.error('网络错误，请稍后重试')
    }
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchBookDetail()
})
</script>

<style scoped>
.book-detail-container {
  padding: 20px;
}

.book-detail-content {
  max-width: 1200px;
  margin: 0 auto;
}

.book-detail-card {
  padding: 20px;
}

.book-cover {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 450px;
  overflow: hidden;
}

.book-cover img {
  max-width: 100%;
  max-height: 100%;
  object-fit: cover;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.book-info {
  padding: 0 20px;
}

.book-info h2 {
  margin-bottom: 20px;
  color: #303133;
}

.book-info p {
  margin-bottom: 10px;
  color: #606266;
  font-size: 16px;
}

.book-stock {
  margin: 20px 0;
}

.book-stock el-tag {
  margin-right: 10px;
}

.borrow-button {
  margin-top: 20px;
  width: 200px;
}

.book-description {
  margin-top: 20px;
}

.book-description h3 {
  margin-bottom: 15px;
  color: #303133;
}

.book-description p {
  line-height: 1.6;
  color: #606266;
  font-size: 14px;
}
</style>
