<template>
  <div class="book-management-container">
    <Navbar />
    <div class="book-management-content">
      <el-card class="management-card">
        <template #header>
          <div class="card-header">
            <el-icon><DocumentAdd /></el-icon>
            <span>图书管理</span>
            <div class="header-actions">
              <el-button type="primary" @click="dialogVisible = true">
                <el-icon><Plus /></el-icon>
                新增图书
              </el-button>
              <el-button @click="handleBatchImport">
                <el-icon><Upload /></el-icon>
                批量导入
              </el-button>
            </div>
          </div>
        </template>
        
        <!-- 搜索和筛选 -->
        <div class="search-filter">
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
        </div>
        
        <!-- 图书列表 -->
        <el-table :data="books" style="width: 100%">
          <el-table-column type="index" label="序号" width="80" />
          <el-table-column prop="title" label="图书名称" width="200" />
          <el-table-column prop="author" label="作者" width="120" />
          <el-table-column prop="isbn" label="ISBN" width="150" />
          <el-table-column prop="category" label="分类" width="100" />
          <el-table-column prop="publisher" label="出版社" width="150" />
          <el-table-column prop="total_quantity" label="总数量" width="80" />
          <el-table-column prop="available_quantity" label="可借数量" width="80" />
          <el-table-column label="操作" width="150">
            <template #default="scope">
              <el-button type="primary" size="small" @click="handleEdit(scope.row)">
                <el-icon><Edit /></el-icon>
                编辑
              </el-button>
              <el-button type="danger" size="small" @click="handleDelete(scope.row.id)">
                <el-icon><Delete /></el-icon>
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
        
        <!-- 分页 -->
        <div class="pagination" v-if="totalBooks > 0">
          <el-pagination
            :current-page="currentPage"
            :page-size="pageSize"
            :page-sizes="[10, 20, 50]"
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
      
      <!-- 新增/编辑图书对话框 -->
      <el-dialog
        v-model="dialogVisible"
        :title="dialogTitle"
        width="700px"
      >
        <el-form :model="bookForm" :rules="bookRules" ref="bookFormRef" label-width="100px">
          <el-form-item label="图书名称" prop="title">
            <el-input v-model="bookForm.title" placeholder="请输入图书名称" />
          </el-form-item>
          <el-form-item label="作者" prop="author">
            <el-input v-model="bookForm.author" placeholder="请输入作者" />
          </el-form-item>
          <el-form-item label="ISBN" prop="isbn">
            <el-input v-model="bookForm.isbn" placeholder="请输入ISBN" />
          </el-form-item>
          <el-form-item label="分类" prop="category">
            <el-select v-model="bookForm.category" placeholder="请选择分类">
              <el-option
                v-for="category in categories"
                :key="category"
                :label="category"
                :value="category"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="出版社" prop="publisher">
            <el-input v-model="bookForm.publisher" placeholder="请输入出版社" />
          </el-form-item>
          <el-form-item label="定价" prop="price">
            <el-input-number v-model="bookForm.price" :min="0" :step="0.01" placeholder="请输入定价" />
          </el-form-item>
          <el-form-item label="馆藏地点" prop="location">
            <el-input v-model="bookForm.location" placeholder="请输入馆藏地点" />
          </el-form-item>
          <el-form-item label="索书号" prop="call_number">
            <el-input v-model="bookForm.call_number" placeholder="请输入索书号" />
          </el-form-item>
          <el-form-item label="总数量" prop="total_quantity">
            <el-input-number v-model="bookForm.total_quantity" :min="1" placeholder="请输入总数量" />
          </el-form-item>
          <el-form-item label="借阅期限" prop="borrow_period">
            <el-input-number v-model="bookForm.borrow_period" :min="1" :default="30" placeholder="请输入借阅期限（天）" />
          </el-form-item>
          <el-form-item label="内容简介" prop="description">
            <el-input v-model="bookForm.description" type="textarea" placeholder="请输入内容简介" :rows="3" />
          </el-form-item>
          <el-form-item label="封面图片">
            <el-upload
              class="avatar-uploader"
              action="/api/upload/"
              :show-file-list="false"
              :on-success="handleImageUpload"
              :before-upload="beforeUpload"
            >
              <img v-if="bookForm.cover_image" :src="bookForm.cover_image" class="avatar" />
              <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
            </el-upload>
          </el-form-item>
        </el-form>
        <template #footer>
          <span class="dialog-footer">
            <el-button @click="dialogVisible = false">取消</el-button>
            <el-button type="primary" @click="handleSave">保存</el-button>
          </span>
        </template>
      </el-dialog>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { DocumentAdd, Plus, Search, Upload, Edit, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import Navbar from '../../components/Navbar.vue'
import axios from 'axios'

const dialogVisible = ref(false)
const dialogTitle = ref('新增图书')
const bookFormRef = ref(null)
const books = ref([])
const totalBooks = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const searchQuery = ref('')
const categoryFilter = ref('')
const categories = ref([
  '计算机科学', '文学', '历史', '哲学', '艺术', '教育', '科学', '工程'
])

const bookForm = reactive({
  title: '',
  author: '',
  isbn: '',
  category: '',
  publisher: '',
  price: 0,
  location: '',
  call_number: '',
  total_quantity: 1,
  available_quantity: 1,
  borrow_period: 30,
  description: '',
  cover_image: ''
})

const bookRules = {
  title: [{ required: true, message: '请输入图书名称', trigger: 'blur' }],
  author: [{ required: true, message: '请输入作者', trigger: 'blur' }],
  isbn: [{ required: true, message: '请输入ISBN', trigger: 'blur' }],
  category: [{ required: true, message: '请选择分类', trigger: 'blur' }],
  publisher: [{ required: true, message: '请输入出版社', trigger: 'blur' }],
  price: [{ required: true, message: '请输入定价', trigger: 'blur' }],
  location: [{ required: true, message: '请输入馆藏地点', trigger: 'blur' }],
  call_number: [{ required: true, message: '请输入索书号', trigger: 'blur' }],
  total_quantity: [{ required: true, message: '请输入总数量', trigger: 'blur' }],
  borrow_period: [{ required: true, message: '请输入借阅期限', trigger: 'blur' }]
}

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

const handleEdit = (book) => {
  dialogTitle.value = '编辑图书'
  Object.assign(bookForm, book)
  dialogVisible.value = true
}

const handleDelete = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除这本书吗？', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await axios.delete(`/api/books/${id}/`)
    ElMessage.success('删除成功')
    fetchBooks()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

const handleSave = async () => {
  if (!bookFormRef.value) return
  
  await bookFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        // 准备要发送的数据
        const dataToSend = { ...bookForm }
        
        // 确保price是字符串类型，符合Django的DecimalField要求
        dataToSend.price = bookForm.price.toString()
        
        // 如果cover_image是空字符串，设置为null
        if (dataToSend.cover_image === '') {
          dataToSend.cover_image = null
        }
        
        // 如果是新增图书，设置可借数量等于总数量
        if (!bookForm.id) {
          dataToSend.available_quantity = bookForm.total_quantity
        }
        
        if (bookForm.id) {
          // 编辑
          await axios.put(`/api/books/${bookForm.id}/`, dataToSend)
          ElMessage.success('编辑成功')
        } else {
          // 新增
          await axios.post('/api/books/', dataToSend)
          ElMessage.success('新增成功')
        }
        dialogVisible.value = false
        fetchBooks()
        resetForm()
      } catch (error) {
        console.error('保存失败:', error)
        ElMessage.error(error.response?.data?.error || '保存失败')
      }
    }
  })
}

const resetForm = () => {
  Object.assign(bookForm, {
    id: '',
    title: '',
    author: '',
    isbn: '',
    category: '',
    publisher: '',
    price: 0,
    location: '',
    call_number: '',
    total_quantity: 1,
    available_quantity: 1,
    borrow_period: 30,
    description: '',
    cover_image: ''
  })
}

const handleImageUpload = (response, file, fileList) => {
  bookForm.cover_image = response.url
}

const beforeUpload = (file) => {
  const isJPG = file.type === 'image/jpeg' || file.type === 'image/png'
  const isLt2M = file.size / 1024 / 1024 < 2
  
  if (!isJPG) {
    ElMessage.error('只能上传JPG/PNG图片')
  }
  if (!isLt2M) {
    ElMessage.error('图片大小不能超过2MB')
  }
  
  return isJPG && isLt2M
}

const handleBatchImport = () => {
  // 批量导入功能
  ElMessage.info('批量导入功能开发中')
}

onMounted(() => {
  fetchBooks()
})
</script>

<style scoped>
.book-management-container {
  padding: 20px;
}

.book-management-content {
  max-width: 1200px;
  margin: 0 auto;
}

.management-card {
  margin-top: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-header span {
  margin-left: 10px;
  font-weight: bold;
}

.header-actions {
  display: flex;
  gap: 10px;
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

.avatar-uploader .el-upload {
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
}

.avatar-uploader .el-upload:hover {
  border-color: #409eff;
}

.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 100px;
  height: 100px;
  line-height: 100px;
  text-align: center;
}

.avatar {
  width: 100px;
  height: 100px;
  display: block;
}
</style>
