<!--<template>-->
<!--  <div class="app">-->
<!--    &lt;!&ndash; 头部 &ndash;&gt;-->
<!--    <myHeader></myHeader>-->

<!--    <el-container-->
<!--            style="height: 100vh;-->
<!--      border: 1px solid #eee;-->
<!--      margin: 0;-->
<!--      border: 0;-->
<!--      padding: 0;">     &lt;!&ndash; style： 隐藏滚动条  去掉白边&ndash;&gt;-->
<!--      &lt;!&ndash; 侧边栏 &ndash;&gt;-->
<!--      <el-aside style="width: 200px;">-->
<!--        <asideNav></asideNav>-->
<!--      </el-aside>-->
<!--      &lt;!&ndash; 主页面 &ndash;&gt;-->
<!--      <el-main>-->
<!--        <router-view></router-view>-->
<!--      </el-main>-->
<!--    </el-container>-->
<!--  </div>-->
<!--</template>-->

<!--<script>-->
<!--  import myHeader from "@/components/myHeader"-->
<!--  import asideNav from "@/components/asideNav"-->



<!--  export default {-->
<!--    name: "App",-->
<!--    components: {-->
<!--      myHeader,-->
<!--      asideNav,-->
<!--    }-->
<!--  }-->
<!--</script>-->

<!--<style>-->
<!--  html,-->
<!--  body{-->
<!--    height: 100%;-->
<!--    margin: 0;-->
<!--    border: 0;-->
<!--    padding: 0;-->
<!--  }-->
<!--</style>-->

<template>
  <div class="app">
    <!-- 整个页面容器 -->
    <el-container style="height: 100vh; margin: 0; padding: 0;">

      <!-- 固定在左侧的侧边栏 -->
      <el-aside style="width: 200px; height: 100vh; position: fixed; overflow: auto;">
        <asideNav></asideNav>
      </el-aside>

      <!-- 主内容区域，包括头部和主页面内容 -->
      <el-container style="margin-left: 200px;"> <!-- 左边距等于侧边栏宽度 -->

        <!-- 头部 -->
        <el-header style="height: 60px; line-height: 60px;">
          <header-comp></header-comp>
        </el-header>

        <!-- 主页面内容 -->
        <el-main>
          <router-view></router-view>
        </el-main>

      </el-container>

    </el-container>
  </div>
</template>

<script>
  import HeaderComp from "@/components/header"  // 确保这里的路径和组件名称与你的项目结构匹配
  import asideNav from "@/components/asideNav"

  export default {
    name: "App",
    components: {
      HeaderComp,  // 将 myHeader 替换为 HeaderComp
      asideNav,
    }
  }
</script>

<style>
  html,
  body{
    height: 100%;
    margin: 0;
    border: 0;
    padding: 0;
  }
  .el-aside {
    background-color: #333; /* 举例的颜色，您可以根据需要调整 */
  }

  .el-header {
    background-color: #fff; /* 举例的颜色，您可以根据需要调整 */
    box-shadow: 0 2px 4px rgba(0,0,0,.1); /* 添加阴影效果 */
  }

  /* 确保主内容区域的顶部不被覆盖 */
  .el-main {
    padding-top: 60px; /* 头部高度 */
  }
</style>
