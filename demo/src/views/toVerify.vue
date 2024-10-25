<template>
  <el-container style="height: 100%;font-size: 15px;">
    <el-main class="main-container">
      <el-card class="box-card">
        <div slot="header" class="clearfix">
          <span>{{ cveData.CVE }} 漏洞验证</span>
        </div>

        <div>
          <el-button size="medium" @click="returnFront">返回批量验证页面</el-button>
        </div>

        <el-row :gutter="20" class="content-row">
          <el-col :span="2">
            <label class="label">CVE 编号:</label>
          </el-col>
          <el-col :span="22" class="row-content">
            <span>{{ cveData.CVE }}</span>
          </el-col>

          <el-col :span="2">
            <label class="label">CVE 名称:</label>
          </el-col>
          <el-col :span="22" class="row-content">
            <span>{{ cveData.CVEName }}</span>
          </el-col>

          <el-col :span="2">
            <label class="label">CVSS 分值:</label>
          </el-col>
          <el-col :span="22" class="row-content">
            <span>{{ cveData.CVSS }}</span>
          </el-col>

          <el-col :span="2">
            <label class="label">POC 存在 ？</label>
          </el-col>
          <el-col :span="22" class="row-content">
            <span>{{ cveData.POCState }}</span>
          </el-col>

          <el-col :span="2">
            <label class="label">验证结果:</label>
          </el-col>
          <el-col :span="22" class="row-content">
            <span>{{ cveData.searchResult }}</span>
          </el-col>

          <el-col :span="2">
            <label class="label">漏洞描述:</label>
          </el-col>
          <el-col :span="22" class="row-content">
            <span>{{ cveData.summary }}</span>
          </el-col>

          <el-col :span="2">
            <label class="label">POC代码:</label>
          </el-col>
          <el-col :span="22" class="row-content2">
<!--            <el-upload-->
<!--                class="upload-demo"-->
<!--                ref="upload"-->
<!--                :http-request="handleFileUpload"-->
<!--                :before-upload="beforeFileUpload"-->
<!--                :on-remove="handleRemove"-->
<!--                :file-list="fileList"-->
<!--                :limit="1">-->
<!--              <el-button>选择文件</el-button>（如需修改请上传）-->
<!--            </el-upload>-->
<!--            <el-button @click="submitUpload">上传文件</el-button>-->
<!--            <span>文件名：</span>-->
<!--            <el-input v-model="filename"></el-input>-->
<!--            <el-button @click="submitCode">上传代码</el-button>-->
<!--            <CodeEditor v-model="code"/>-->
            <div style="display: flex; align-items: center;">
              <el-upload
                  class="upload-demo"
                  ref="upload"
                  :http-request="handleFileUpload"
                  :before-upload="beforeFileUpload"
                  :on-remove="handleRemove"
                  :file-list="fileList"
                  :limit="1">
                <el-button>选择文件</el-button>（如需修改请上传）
              </el-upload>
              <el-button @click="submitUpload" style="margin-left: 10px;">上传文件</el-button>
            </div>

            <!-- 文件名、输入框、上传代码按钮在同一行 -->
            <div style="display: flex; align-items: center; margin-top: 10px;">
              <span>文件名：</span>
              <el-input v-model="filename" style="width: 200px; margin-left: 10px;"></el-input>
              <el-button @click="submitCode" style="margin-left: 10px;">上传代码</el-button>
            </div>

            <!-- 代码编辑器 -->
            <CodeEditor v-model="code"/>
          </el-col>

          <div style="text-align: right;">
            <el-button size="medium" @click="startVerify" type="primary">开始验证</el-button>
          </div>

          <el-col :span="2">
            <label class="label">验证详情:</label>
          </el-col>
          <el-col :span="22" class="row-content2">
            <span>{{ details }}</span>
          </el-col>


        </el-row>
      </el-card>
    </el-main>
  </el-container>
</template>

<script>
import axios from 'axios';
import CodeEditor from "@/components/CodeEditor.vue";

export default {
  name: 'TargetPage',
  components: {
    CodeEditor,
  },
  data() {
    return {
      cveData: '',
      code: '# 初始化 Python 代码\nprint("Hello, World!")', // 表单数据绑定
      fileList: [],
      filename: '',
      details: '验证详情。。。。。。。。',
    };
  },
  created() {
    this.cveData = JSON.parse(this.$route.query.data); // 解析 row 对象
    console.log('接收到的数据:', this.cveData);
    this.lookDetails();
  },
  methods:{
    lookDetails() {
      axios
          .post('/api/details', { cve_id: this.cveData.CVE })
          .then((response) => {
            this.details = response.data.details || '未提供详情';
          })
          .catch((error) => {
            console.error('There was an error fetching the CVE details:', error);
            this.$message.error('获取漏洞详情失败，请稍后再试');
          });
    },
    beforeFileUpload(file) {
      const isPython = file.type === 'application/x-python-code' || file.name.endsWith('.py');
      if (!isPython) {
        this.$message.error('只能上传Python文件');
        return false;
      }

      // 创建一个 Promise 来读取文件内容
      return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = (event) => {
          const content = event.target.result;

          // 定义需要包含的内容的正则表达式或简单字符串
          const requiredPatterns = [
            /class\s+DemoPOC:/,             // 检查是否有 class DemoPOC:
            /def\s+__init__\s*\(self,\s*url,\s*ip,\s*port\)/, // 检查是否有 def __init__(self, url, ip, port)
            /def\s+_verify\s*\(self\)/,     // 检查是否有 def _verify(self)
            /result\[['"]VerifyInfo['"]\]/, // 检查是否有 result['VerifyInfo'] 或 result["VerifyInfo"]
            /\[!\]/,                       // 检查是否有 [!]
            /\[SAFE\]/                     // 检查是否有 [SAFE]
          ];

          // 检查内容是否满足要求
          const isValid = requiredPatterns.every((pattern) => pattern.test(content));
          if (!isValid) {
            this.$message.error('poc格式不规范');
            reject(false);
          } else {
            resolve(true);
          }
        };

        reader.onerror = () => {
          this.$message.error('文件读取失败');
          reject(false);
        };

        // 读取文件内容为文本
        reader.readAsText(file);
      });
    },
    handleFileUpload(param) {
      if (param.file) {
        this.fileList = [param.file];
      }
    },
    handleRemove() {
      this.fileList = [];
    },
    // 提交POC代码
    submitUpload() {
      if (this.fileList.length === 0) {
        this.$message.warning('请先选择文件');
        return;
      }

      const formData = new FormData();
      formData.append('cve_id', this.currentCveId2); // 添加CVE ID
      formData.append('mode','upload');
      formData.append('file', this.fileList[0].raw); // 添加文件

      // 发送POST请求
      axios
          .post('/api/updatePoc', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
          })
          .then(response => {
            // 使用后端返回的 message
            this.$message.success(response.data.message || 'POC上传成功');
            window.location.reload();//刷新页面
          })
          .catch(error => {
            // 使用后端返回的错误消息
            const errorMessage = error.response?.data?.message || '上传失败，请稍后再试';
            this.$message.error(errorMessage);
            console.error('POC上传失败:', error);
          });
    },
    submitCode() {
      //需要先进行文件检查，代码正则表达式检查（还没写）
      const formData = new FormData();
      formData.append('cve_id', this.currentCveId2); // 添加CVE ID
      formData.append('mode','edit');
      formData.append('edit_filename',this.filename);
      formData.append('poc_content',this.code);

      // 发送POST请求
      axios
          .post('/api/updatePoc', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
          })
          .then(response => {
            // 使用后端返回的 message
            this.$message.success(response.data.message || 'POC上传成功');
            window.location.reload();//刷新页面
          })
          .catch(error => {
            // 使用后端返回的错误消息
            const errorMessage = error.response?.data?.message || '上传失败，请稍后再试';
            this.$message.error(errorMessage);
            console.error('POC上传失败:', error);
          });
    },
    startVerify() {
      axios.post('/api/pocVerify', { cve_ids:this.cveData.CVE })
          .then(() => {
            this.$message.success(`POC 执行成功`);
            this.fetchCpeData(); // 刷新数据
          })
          .catch(error => {
            console.error(`There was an error executing POC for ${this.cveData.CVE}:`, error);
            this.$message.error('执行POC失败，请稍后再试');
          });
    },
    returnFront() {
      this.$nextTick(() => {
        this.$router.push('/pocScanner/pocVerify');
      });
    }
  }
};
</script>

<style scoped>
/* 主容器：保证垂直和水平居中 */
.main-container {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 120%;
}

/* 卡片的样式 */
.box-card {
  width: 100%; /* 卡片宽度占屏幕的 80% */
  /*height: 100%;*/
  max-width: 2000px; /* 限制最大宽度 */
  padding: 10px;
  border-radius: 8px;
  background-color: #ffffff;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

/* 标签的样式 */
.label {
  font-weight: bold;
  color: #606266;
}

/* 控制每一行的样式，增大每一行之间的间距 */
.content-row {
  margin-top: 20px;
}

.row-content {
  margin-bottom: 12px; /* 增加行与行之间的间距 */
}

.row-content2 {
  margin-bottom: 35px; /* 增加行与行之间的间距 */
}
</style>
