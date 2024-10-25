<template>
  <el-form :model="form" label-width="80px">
    <el-form-item label="代码">
      <!-- 将代码编辑器作为输入框 -->
      <CodeEditor v-model="form.code"/>
    </el-form-item>

  </el-form>
</template>

<script>
import CodeEditor from '@/components/CodeEditor.vue'; // 引入 CodeEditor 组件

export default {
  name: 'CodeForm',
  components: {
    CodeEditor,
  },
  data() {
    return {
      form: {
        code: '# 初始化 Python 代码\nprint("Hello, World!")', // 表单数据绑定
      },
    };
  },
};
</script>

<style scoped>
/* 可根据需求调整表单样式 */
</style>




<!--<template>-->
<!--  <div>-->
<!--    这是首页-->
<!--  </div>-->
<!--</template>-->
