<!--<template>-->
<!--  <div id="app">-->
<!--    <img alt="Vue logo" src="./assets/logo.png">-->
<!--    <HelloWorld msg="Welcome to Your Vue.js App"/>-->
<!--  </div>-->
<!--</template>-->

<!--<script>-->
<!--import HelloWorld from './components/HelloWorld.vue'-->

<!--export default {-->
<!--  name: 'App',-->
<!--  components: {-->
<!--    HelloWorld-->
<!--  }-->
<!--}-->
<!--</script>-->

<!--<style>-->
<!--#app {-->
<!--  font-family: Avenir, Helvetica, Arial, sans-serif;-->
<!--  -webkit-font-smoothing: antialiased;-->
<!--  -moz-osx-font-smoothing: grayscale;-->
<!--  text-align: center;-->
<!--  color: #2c3e50;-->
<!--  margin-top: 60px;-->
<!--}-->
<!--</style>-->
<template>
  <div class="app">
    <!-- 头部 -->
    <myHeader></myHeader>

    <el-container
            style="height: 100vh;
      border: 1px solid #eee;
      margin: 0;
      border: 0;
      padding: 0;">     <!-- style： 隐藏滚动条  去掉白边-->
      <!-- 侧边栏 -->
      <el-aside style="width: 200px;">
        <asideNav></asideNav>
      </el-aside>
      <!-- 主页面 -->
      <el-main>
        <router-view></router-view>
      </el-main>
    </el-container>
  </div>
</template>

<script>
  import myHeader from "@/components/myHeader"
  import asideNav from "@/components/asideNav"



  export default {
    name: "App",
    components: {
      myHeader,
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
</style>
