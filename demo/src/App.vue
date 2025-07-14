<template>
  <div class="app">
    <router-view></router-view>
  </div>
</template>

<script>


export default {
  name: "App",
}
</script>

<style>
html,
body {
  height: 100%;
  margin: 0;
  border: 0;
  padding: 0;
}

.el-container {
  height: 100vh;
}

#main-aside {
  height: 100vh;
  overflow: hidden;
  background-color: #333;
}

.el-header {
  background-color: #fff;
  /* 举例的颜色，您可以根据需要调整 */
  box-shadow: 0 2px 4px rgba(0, 0, 0, .1);
  /* 添加阴影效果 */
}

/* 确保主内容区域的顶部不被覆盖 */
#main-container {
  width: 90vw;
  /* 减去侧边栏的宽度 */
  min-width: 600px;
  /* 头部高度 */
}
</style>
