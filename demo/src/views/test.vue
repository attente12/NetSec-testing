<template>
  <div class="markdown-container">
    <h1>Markdown文档</h1>
    <div v-if="loading" class="loading">
      正在加载文档...
    </div>
    <div v-else-if="error" class="error">
      加载文档出错: {{ error }}
    </div>
    <div v-else>
      <div class="markdown-content" v-html="htmlContent"></div>
      <button class="download-btn" @click="downloadMarkdown">
        下载文档
      </button>
    </div>
  </div>
</template>

<script>
// 导入 markdown-it
import MarkdownIt from 'markdown-it'

export default {
  data() {
    return {
      markdownContent: '',
      htmlContent: '',
      loading: true,
      error: null,
      md: new MarkdownIt({
        html: true,        // 启用HTML标签
        breaks: true,      // 转换段落中的换行为 <br>
        linkify: true,     // 将类似URL的文本自动转换为链接
        typographer: true  // 启用一些语言中性的替换 + 引号美化
      })
    }
  },
  mounted() {
    this.fetchMarkdownFile();
  },
  methods: {
    async fetchMarkdownFile() {
      try {
        const response = await fetch('/poc_helper.md');
        if (!response.ok) {
          throw new Error(`HTTP错误 ${response.status}`);
        }

        // 获取原始Markdown内容
        this.markdownContent = await response.text();

        // 使用 markdown-it 渲染HTML
        this.htmlContent = this.md.render(this.markdownContent);

        this.loading = false;
      } catch (err) {
        console.error('获取Markdown文件失败:', err);
        this.error = err.message;
        this.loading = false;
      }
    },

    downloadMarkdown() {
      if (!this.markdownContent) return;

      const blob = new Blob([this.markdownContent], { type: 'text/markdown' });
      const url = URL.createObjectURL(blob);

      const a = document.createElement('a');
      a.href = url;
      a.download = 'poc_helper.md';
      document.body.appendChild(a);
      a.click();

      // 清理
      setTimeout(() => {
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      }, 100);
    }
  }
}
</script>

<style>
.markdown-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  font-family: Arial, sans-serif;
}

.markdown-content {
  border: 1px solid #ddd;
  border-radius: 5px;
  padding: 20px;
  margin-bottom: 20px;
  background-color: #f9f9f9;
  line-height: 1.6;
}

/* 基础样式 - 注意在Vue2中使用 >>> 来深度选择 */
.markdown-content >>> h1,
.markdown-content >>> h2,
.markdown-content >>> h3,
.markdown-content >>> h4 {
  margin-top: 20px;
  margin-bottom: 10px;
  color: #333;
}

.markdown-content >>> h1 {
  font-size: 24px;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
}

.markdown-content >>> h2 {
  font-size: 20px;
}

.markdown-content >>> h3 {
  font-size: 18px;
}

.markdown-content >>> p {
  margin-bottom: 16px;
}

.markdown-content >>> a {
  color: #0366d6;
  text-decoration: none;
}

.markdown-content >>> a:hover {
  text-decoration: underline;
}

.markdown-content >>> ul,
.markdown-content >>> ol {
  padding-left: 2em;
  margin-bottom: 16px;
}

.markdown-content >>> li {
  margin-bottom: 5px;
}

.markdown-content >>> pre {
  background-color: #f6f8fa;
  border-radius: 3px;
  padding: 16px;
  overflow: auto;
  margin-bottom: 16px;
}

.markdown-content >>> code {
  font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
  font-size: 85%;
  padding: 0.2em 0.4em;
  background-color: #f6f8fa;
  border-radius: 3px;
}

.markdown-content >>> pre code {
  padding: 0;
  background-color: transparent;
}

/* 表格样式 */
.markdown-content >>> table {
  border-collapse: collapse;
  width: 100%;
  margin-bottom: 16px;
}

.markdown-content >>> th,
.markdown-content >>> td {
  border: 1px solid #ddd;
  padding: 8px;
  text-align: left;
}

.markdown-content >>> th {
  background-color: #f2f2f2;
  font-weight: bold;
}

.markdown-content >>> tr:nth-child(even) {
  background-color: #f8f8f8;
}

.markdown-content >>> blockquote {
  color: #666;
  margin: 0;
  padding-left: 15px;
  border-left: 4px solid #ddd;
}

.download-btn {
  background-color: #4CAF50;
  color: white;
  padding: 10px 15px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  transition: background-color 0.3s;
}

.download-btn:hover {
  background-color: #45a049;
}

.loading, .error {
  padding: 20px;
  text-align: center;
  border: 1px solid #ddd;
  border-radius: 5px;
  margin-bottom: 20px;
}

.error {
  color: #721c24;
  background-color: #f8d7da;
  border-color: #f5c6cb;
}
</style>