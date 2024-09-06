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
        <el-breadcrumb-item v-else>{{$route.meta.title}}</el-breadcrumb-item>
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

<style scoped>

</style>



<!--<template>-->
<!--  <div style="line-height: 60px; display: flex">-->
<!--    <div style="flex: 1;">-->
<!--      <span :class="collapseBtnClass" style="cursor: pointer; font-size: 18px;" @click="collapse"></span>-->
<!--      <el-breadcrumb separator="/" style="display: inline-block; margin-left: 10px;">-->
<!--        <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>-->

<!--        &lt;!&ndash; 漏洞扫描 &ndash;&gt;-->
<!--        <el-breadcrumb-item>-->
<!--          <router-link to="/pocScanner">漏洞扫描</router-link>-->
<!--        </el-breadcrumb-item>-->

<!--        &lt;!&ndash; POC验证 &ndash;&gt;-->
<!--        <el-breadcrumb-item v-if="$route.path === '/pocScanner'">-->
<!--          POC验证-->
<!--        </el-breadcrumb-item>-->

<!--        <el-breadcrumb-item v-if="$route.path === '/pocScanner/pocVerify'">-->
<!--          POC验证-->
<!--        </el-breadcrumb-item>-->

<!--        &lt;!&ndash; 其他页面 &ndash;&gt;-->
<!--        <el-breadcrumb-item v-if="!$route.path.startsWith('/pocScanner')">{{$route.meta.title}}</el-breadcrumb-item>-->
<!--      </el-breadcrumb>-->
<!--    </div>-->
<!--  </div>-->
<!--</template>-->

<!--<script>-->
<!--export default {-->
<!--  name: "Header",-->
<!--  props: {-->
<!--    collapseBtnClass: String,-->
<!--    collapse: Boolean,-->
<!--  }-->
<!--}-->
<!--</script>-->

<!--<style scoped>-->

<!--</style>-->



<!--<template>-->
<!--  <div style="line-height: 60px; display: flex">-->
<!--    <div style="flex: 1;">-->
<!--      <span :class="collapseBtnClass" style="cursor: pointer; font-size: 18px;" @click="collapse"></span>-->
<!--      <el-breadcrumb separator="/" style="display: inline-block; margin-left: 10px;">-->
<!--        <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>-->

<!--        &lt;!&ndash; 漏洞扫描页面及其子页面 &ndash;&gt;-->
<!--        <el-breadcrumb-item v-if="$route.path.startsWith('/pocScanner')">-->
<!--          <router-link to="/pocScanner">漏洞扫描</router-link>-->
<!--        </el-breadcrumb-item>-->

<!--        &lt;!&ndash; 仅在 POC 验证页面时显示 &ndash;&gt;-->
<!--        <el-breadcrumb-item v-if="$route.path === '/pocScanner/pocVerify'">-->
<!--          POC验证-->
<!--        </el-breadcrumb-item>-->

<!--        &lt;!&ndash; 其他页面的面包屑 &ndash;&gt;-->
<!--        <el-breadcrumb-item v-if="!$route.path.startsWith('/pocScanner')">{{$route.meta.title}}</el-breadcrumb-item>-->
<!--      </el-breadcrumb>-->
<!--    </div>-->
<!--  </div>-->
<!--</template>-->

<!--<script>-->
<!--export default {-->
<!--  name: "Header",-->
<!--  props: {-->
<!--    collapseBtnClass: String,-->
<!--    collapse: Boolean,-->
<!--  }-->
<!--}-->
<!--</script>-->

<!--<style scoped>-->

<!--</style>-->

