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
            <!--            <span>{{ cveData.CVEName }}</span>-->
            <el-input v-model="cveData.CVEName"></el-input>
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
            <label class="label">漏洞影响范围:</label>
          </el-col>
          <el-col :span="22" class="row-content">
            <!--            <span>{{affected_infra}}</span>-->
            <!--            <el-input v-model="affected_infra"></el-input>-->
            <el-autocomplete v-model="affected_infra" :fetch-suggestions="querySearch" placeholder="请输入内容"
              @select="handleSelect" style="width: 300px;" />
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

            <div style="display: flex; align-items: center;">
              <el-upload class="upload-demo" ref="upload" :http-request="handleFileUpload"
                :before-upload="beforeFileUpload" :on-remove="handleRemove" :file-list="fileList" :limit="1">
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
            <CodeEditor v-model="code" />
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
import CodeEditor from "@/components/CodeEditor.vue";

export default {
  name: 'TargetPage',
  components: {
    CodeEditor,
  },
  data() {
    return {
      cveData: '',
      code: '', // 表单数据绑定
      fileList: [],
      filename: '',
      details: '验证详情。。。。。。。。',
      affected_infra: '',
      suggestions: [], // 将文件内容读取后填充到此数组，格式为 { value: "文本" }
    };
  },
  created() {
    this.cveData = JSON.parse(this.$route.query.data); // 解析 row 对象
    console.log('接收到的数据:', this.cveData);
    this.lookDetails();
    this.getPoc();
    this.loadFile();
  },
  methods: {
    lookDetails() {
      this.$axios
        .post('/pocExcute', { CVE_id: this.cveData.CVE, ip: this.cveData.ip })
        .then((response) => {
          this.details = response.data.message || '未提供详情';
        })
        .catch((error) => {
          console.error('There was an error fetching the CVE details:', error);
          //this.$message.error('获取漏洞详情失败，请稍后再试');
        });
    },
    getPoc() {
      this.$axios.get('/getPOCContent', {
        params: {
          vuln_id: this.cveData.CVE
        }
      })
        .then(response => {
          this.code = response.data.content;
          this.affected_infra = response.data.affected_infra;
        })
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
      if (this.affected_infra === '') {
        this.$message.warning('请先输入影响范围');
        return;
      }

      if (this.fileList.length === 0) {
        this.$message.warning('请先选择文件');
        return;
      }

      const formData = new FormData();
      formData.append('cve_id', this.cveData.CVE); // 添加CVE ID
      formData.append('vul_name', this.cveData.CVEName); // 添加CVE ID
      formData.append('affected_infra', '影响范围'); // 添加CVE ID
      formData.append('mode', 'upload');
      formData.append('file', this.fileList[0]); // 添加文件

      // 发送POST请求
      this.$axios
        .put('/updatePoc', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })
        .then(response => {
          // 使用后端返回的 message
          this.$message.success(response.data.message || 'POC上传成功');
          //window.location.reload();//刷新页面
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
      // 检查文件名是否以 .py 结尾
      if (!this.filename.endsWith('.py')) {
        this.$message.error('文件名错误，必须以 .py 结尾');
        return;  // 停止保存流程
      }

      // 正则表达式数组（多行模式，处理空格和换行）
      const requiredFields = [
        { regex: /class\s+DemoPOC\s*:/m, label: 'class DemoPOC:' },  // 类定义
        { regex: /def\s+__init__\s*\(self,\s*url,\s*ip,\s*port\)/m, label: 'def __init__(self,url,ip,port)' },  // 构造函数
        { regex: /def\s+_verify\s*\(self\)/m, label: 'def _verify(self)' },  // _verify 方法
        { regex: /result\['VerifyInfo'\]/m, label: "result['VerifyInfo']" },  // result['VerifyInfo']
        { regex: /\[!\]/m, label: '[!]' },  // [!]
        { regex: /\[SAFE\]/m, label: '[SAFE]' }  // [SAFE]
      ];

      // 检查每个正则表达式是否匹配代码
      let allFieldsPresent = true;
      requiredFields.forEach(field => {
        const isMatch = field.regex.test(this.code);
        console.log(`Checking field: ${field.label}, Match: ${isMatch}`);  // 调试输出
        if (!isMatch) {
          this.$message.error(`代码中缺少必要的字段：${field.label}`);
          allFieldsPresent = false;  // 如果任意字段未匹配，标记为 false
        }
      });

      if (!allFieldsPresent) {
        return;  // 停止保存流程
      }

      const formData = new FormData();
      formData.append('cve_id', this.cveData.CVE); // 添加CVE ID
      formData.append('vul_name', this.cveData.CVEName); // 添加CVE ID
      formData.append('affected_infra', '影响范围'); // 添加CVE ID
      formData.append('mode', 'edit');
      formData.append('edit_filename', this.filename);
      formData.append('poc_content', this.code);

      // 发送POST请求
      this.$axios
        .put('/updatePoc', formData, {
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
    // startVerify() {
    //   this.$axios.post('/pocVerify', { cve_ids:[this.cveData.CVE] })
    //       .then(() => {
    //         this.$message.success(`POC 执行成功`);
    //         this.getPoc(); // 刷新数据
    //         window.location.reload();
    //       })
    //       .catch(error => {
    //         console.error(`There was an error executing POC for ${this.cveData.CVE}:`, error);
    //         //this.$message.error('执行POC失败，请稍后再试');
    //       });
    // },
    startVerify() {
      this.$axios.post('/pocVerify', {
        cve_ids: [this.cveData.CVE],
        ip: this.cveData.ip
      })
        .then(() => {
          this.$message.success("操作成功");
          this.getPoc(); // 刷新数据
          window.location.reload();
        })
        .catch(error => {
          console.error(`There was an error executing POC for ${this.cveData.CVE}:`, error);
          //this.$message.error('执行POC失败，请稍后再试');
        });
    },
    returnFront() {
      this.$nextTick(() => {
        // 从 cveData 中获取 ip 参数并传递到返回的路径中
        const ip = this.cveData.ip;
        if (ip) {
          this.$router.push({
            path: '/pocScanner/pocVerify',
            query: { ip: ip }
          });
        } else {
          // 如果没有 ip 参数，则直接跳转
          this.$router.push('/pocScanner/pocVerify');
        }
      });
    },
    // returnFront() {
    //   this.$nextTick(() => {
    //     this.$router.push('/pocScanner/pocVerify');
    //   });
    // },
    async loadFile() {
      try {
        const response = await fetch("/nmap_infrastructure_list_grouped_multiline.txt");
        if (!response.ok) throw new Error("Network response was not ok");
        const text = await response.text();
        // 将每一行内容处理为 { value: "文本" } 格式
        this.suggestions = text.split("\n").map(line => ({ value: line.trim() })).filter(item => item.value);
        console.log("Loaded suggestions:", this.suggestions);
      } catch (error) {
        console.error("Failed to load file:", error);
      }
    },
    querySearch(queryString, callback) {
      console.log("querySearch triggered with:", queryString); // 调试信息
      // 仅当输入字符数达到或超过3个并且为连续匹配时才执行匹配
      if (queryString.length >= 3) {
        const results = this.suggestions.filter(item =>
          item.value.toLowerCase().includes(queryString.toLowerCase())
        );
        console.log("Filtered results:", results); // 调试信息
        callback(results);
      } else {
        // 输入字符数不足时返回空数组
        callback([]);
      }
    },
    handleSelect(item) {
      console.log("Selected:", item);
    },
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
  width: 100%;
  /* 卡片宽度占屏幕的 80% */
  /*height: 100%;*/
  max-width: 2000px;
  /* 限制最大宽度 */
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
  margin-bottom: 12px;
  /* 增加行与行之间的间距 */
}

.row-content2 {
  margin-bottom: 35px;
  /* 增加行与行之间的间距 */
}
</style>
