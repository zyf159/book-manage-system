<template>
  <el-menu
    :default-active="activeIndex"
    class="navbar-menu"
    mode="horizontal"
    background-color="#409eff"
    text-color="#fff"
    active-text-color="#ffd04b"
    router
  >
    <el-menu-item index="/">
      <el-icon><HomeFilled /></el-icon>
      <span>首页</span>
    </el-menu-item>
    <el-menu-item index="/books">
      <el-icon><Document /></el-icon>
      <span>图书列表</span>
    </el-menu-item>
    <el-menu-item index="/borrow-records">
      <el-icon><List /></el-icon>
      <span>借阅记录</span>
    </el-menu-item>
    
    <!-- 管理员菜单 -->
    <el-sub-menu v-if="user && user.role === 'admin'" index="admin">
      <template #title>
        <el-icon><Setting /></el-icon>
        <span>管理中心</span>
      </template>
      <el-menu-item index="/admin">
        <el-icon><DataAnalysis /></el-icon>
        <span>仪表盘</span>
      </el-menu-item>
      <el-menu-item index="/admin/books">
        <el-icon><DocumentAdd /></el-icon>
        <span>图书管理</span>
      </el-menu-item>
      <el-menu-item index="/admin/borrow-records">
        <el-icon><Operation /></el-icon>
        <span>借阅管理</span>
      </el-menu-item>
      <el-menu-item index="/admin/users">
        <el-icon><User /></el-icon>
        <span>用户管理</span>
      </el-menu-item>
    </el-sub-menu>
    
    <!-- 用户信息 -->
    <el-menu-item class="user-info" index="user">
      <el-dropdown>
        <span class="user-dropdown">
          <el-avatar :size="32" :src="userAvatar"></el-avatar>
          <span class="user-name">{{ user ? user.username : '未登录' }}</span>
          <el-icon class="el-icon--right"><ArrowDown /></el-icon>
        </span>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item @click="handleLogout">
              <el-icon><SwitchButton /></el-icon>
              <span>退出登录</span>
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </el-menu-item>
  </el-menu>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { HomeFilled, Document, List, Setting, DataAnalysis, DocumentAdd, Operation, User, ArrowDown, SwitchButton } from '@element-plus/icons-vue'
import store from '../store'

const router = useRouter()
const route = useRoute()

const activeIndex = computed(() => route.path)
const user = computed(() => store.state.user)
const userAvatar = computed(() => {
  // 这里可以根据用户信息生成头像，暂时使用默认头像
  return 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'
})

const handleLogout = () => {
  store.logout()
  router.push('/login')
}
</script>

<style scoped>
.navbar-menu {
  margin-bottom: 20px;
}

.user-info {
  margin-left: auto;
}

.user-dropdown {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.user-name {
  margin-left: 10px;
  margin-right: 5px;
}

.el-avatar {
  margin-right: 5px;
}
</style>
