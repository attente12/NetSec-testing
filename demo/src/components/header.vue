<template>
  <div style="line-height: 60px; display: flex">
    <div style="flex: 1;">
      <span :class="collapseBtnClass" style="cursor: pointer; font-size: 18px;" @click="collapse"></span>
      <el-breadcrumb separator="/" style="display: inline-block; margin-left: 10px;">
        <!-- 首页 -->
        <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>

        <!-- 漏洞扫描页面 -->
        <el-breadcrumb-item v-if="$route.path.startsWith('/pocScanner')">
          <router-link to="/pocScanner">漏洞扫描</router-link>
        </el-breadcrumb-item>

        <!-- POC验证（不可点击） -->
        <el-breadcrumb-item v-if="$route.path === '/pocScanner' || $route.path === '/pocScanner/pocVerify'">
          POC验证
        </el-breadcrumb-item>

        <!-- 其他页面 -->
        <el-breadcrumb-item v-else>{{ $route.meta.title }}</el-breadcrumb-item>
      </el-breadcrumb>
    </div>
  </div>
</template>

<script>
export default {
  name: "Header",
  props: {
    collapseBtnClass: String,
    collapse: Boolean,
  }
}
</script>
