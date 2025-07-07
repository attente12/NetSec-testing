<!-- src/components/CodeEditor.vue -->
<template>
  <div class="code-editor">
    <codemirror v-model="code" :options="editorOptions"
      style="height: 300px; width: 100%; border: 1px solid #dcdfe6; border-radius: 4px;" />
  </div>
</template>

<script>
import { codemirror } from 'vue-codemirror'; // vue-codemirror 插件
import 'codemirror/lib/codemirror.css'; // CodeMirror 核心样式

// 改为浅色主题，如 'eclipse'
import 'codemirror/theme/eclipse.css'; // Eclipse 主题样式
import 'codemirror/mode/python/python'; // Python 语言支持

export default {
  name: 'CodeEditor',
  components: {
    codemirror,
  },
  props: {
    value: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      code: this.value, // 初始化时使用父组件传入的值
      editorOptions: {
        mode: 'python', // Python 语法模式
        theme: 'eclipse', // 使用浅色 Eclipse 主题
        lineNumbers: true, // 显示行号
        lineWrapping: true, // 自动换行
      },
    };
  },
  watch: {
    value(newVal) {
      this.code = newVal;
    },
    code(newVal) {
      this.$emit('input', newVal);
    },
  },
};
</script>

<style scoped>
/* 自定义编辑器容器样式 */
.code-editor {
  margin-top: 8px;
}

.code-editor>>>.CodeMirror {
  background-color: white !important;
  color: black;
  font-size: 14px;
  line-height: 1.3;
  padding: 8px;
}

.code-editor>>>.CodeMirror-line {
  line-height: 1.5 !important;
}
</style>
