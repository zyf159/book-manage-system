import { createRouter, createWebHistory } from 'vue-router'
import store from '../store'

// 导入组件
const Login = () => import('../views/Login.vue')
const Register = () => import('../views/Register.vue')
const Home = () => import('../views/Home.vue')
const BookList = () => import('../views/BookList.vue')
const BookDetail = () => import('../views/BookDetail.vue')
const BorrowRecords = () => import('../views/BorrowRecords.vue')
const AdminDashboard = () => import('../views/admin/Dashboard.vue')
const AdminBookManagement = () => import('../views/admin/BookManagement.vue')
const AdminBorrowManagement = () => import('../views/admin/BorrowManagement.vue')
const AdminUserManagement = () => import('../views/admin/UserManagement.vue')

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresAuth: false }
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: { requiresAuth: true }
  },
  {
    path: '/books',
    name: 'BookList',
    component: BookList,
    meta: { requiresAuth: true }
  },
  {
    path: '/books/:id',
    name: 'BookDetail',
    component: BookDetail,
    meta: { requiresAuth: true }
  },
  {
    path: '/borrow-records',
    name: 'BorrowRecords',
    component: BorrowRecords,
    meta: { requiresAuth: true }
  },
  {
    path: '/admin',
    name: 'AdminDashboard',
    component: AdminDashboard,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/books',
    name: 'AdminBookManagement',
    component: AdminBookManagement,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/borrow-records',
    name: 'AdminBorrowManagement',
    component: AdminBorrowManagement,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/users',
    name: 'AdminUserManagement',
    component: AdminUserManagement,
    meta: { requiresAuth: true, requiresAdmin: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const user = JSON.parse(localStorage.getItem('user'))
  
  if (to.meta.requiresAuth) {
    if (!token) {
      next({ name: 'Login' })
    } else if (to.meta.requiresAdmin && user.role !== 'admin') {
      next({ name: 'Home' })
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router
