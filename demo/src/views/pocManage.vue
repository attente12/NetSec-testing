<template>
  <div>
    <h1 id="pocmanage">POC管理</h1>

    <div style="margin: 10px 0">
      <el-input style="width: 200px;margin-left: 5px;margin-right: 10px" placeholder="请输入搜索关键字"
        suffix-icon="el-icon-search" v-model="searchKeyword"></el-input>
      <el-button class="ml-5" type="primary" @click="load">搜索</el-button>
      <el-button type="warning" @click="reset">重置</el-button>
    </div>

    <div style="margin: 10px 0">
      <el-button style="width: 80px;margin-left: 5px" type="primary" @click="handleAdd">新增 <i
          class="el-icon-circle-plus-outline"></i></el-button>
      <el-popconfirm class="ml-5" confirm-button-text="确定" cancel-button-text="我再想想" icon="el-icon-info"
        icon-color="red" title="您确定批量删除这些数据吗？" @confirm="delBatch">
        <template v-slot:reference>
          <el-button style="width: 120px;margin: 10px" type="danger">批量删除 <i
              class="el-icon-remove-outline"></i></el-button>
        </template>
      </el-popconfirm>
    </div>

    <el-dialog :visible.sync="addDialogVisible" title="新增POC" width="500px" :close-on-click-modal="false">
      <el-form :model="newPoc" ref="newPocForm">
        <el-form-item label="CVE编号">
          <el-input v-model="newPoc.cve_id" placeholder="CVE-xxxx-xxxx"></el-input>
        </el-form-item>
        <el-form-item label="漏洞名称">
          <el-input v-model="newPoc.vul_name"></el-input>
        </el-form-item>
        <el-form-item label="漏洞描述">
          <el-input type="textarea" v-model="newPoc.description"></el-input>
        </el-form-item>
        <el-form-item label="POC类型">
          <el-select v-model="newPoc.script_type" placeholder="请选择">
            <el-option label="python" value="python"></el-option>
            <el-option label="c/c++" value="c/c++" :disabled="true"></el-option>
            <el-option label="yaml" value="yaml" :disabled="true"></el-option>
          </el-select>
        </el-form-item>
        <!-- POC代码 上传文件 -->
        <el-form-item label="POC代码">
          <el-upload class="upload-demo" ref="upload" :http-request="handleFileUpload" :before-upload="beforeFileUpload"
            :on-remove="handleRemove" :file-list="fileList" :limit="1">
            <el-button>选择文件</el-button>
          </el-upload>
          <el-button @click="editCode" style="margin-right: 10px;margin-left: 70px;margin-top: 10px">编辑</el-button>
          <i v-if="newcode" class="el-icon-circle-check" style="color: green;"></i>
        </el-form-item>
      </el-form>
      <span slot="footer" class="dialog-footer">
        <el-button @click="addDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitNewPoc">确定</el-button>
      </span>

      <el-dialog :visible.sync="codeDialogVisible" :append-to-body="true" width="1200px" class="custom-dialog">

        <!-- 标题部分，添加内联样式 -->
        <template slot="title">
          <div style="background-color: #f5f5f5; padding: 20px; font-weight: bold; margin: -20px -20px 0 -20px;">
            编辑POC代码
          </div>
        </template>
        <el-form>

          <!-- 漏洞类型选择 -->
          <el-form-item label="漏洞类型" style="margin-bottom: 10px; font-weight: bold;">
            <el-radio-group v-model="vulnerabilityType">
              <el-radio :label="0">Arbitrary File Read</el-radio>
              <el-radio :label="1">Code Execution</el-radio>
              <el-radio :label="2">Command Execution</el-radio>
              <el-radio :label="3">Denial Of service</el-radio>
              <el-radio :label="4">Information Disclosure</el-radio>
              <el-radio :label="5">Login Bypass</el-radio>
              <el-radio :label="6">Path Traversal</el-radio>
              <el-radio :label="7">SQL Injection</el-radio>
              <el-radio :label="8">SSRF</el-radio>
              <el-radio :label="9">XSS</el-radio>
            </el-radio-group>
          </el-form-item>

          <!-- Authentication Required -->
          <el-form-item label="Authentication Required?" style="margin-bottom: 0px; font-weight: bold;">
            <el-radio-group v-model="authRequired">
              <el-radio :label="1">Yes</el-radio>
              <el-radio :label="0">No</el-radio>
            </el-radio-group>
          </el-form-item>

          <!-- Can we get result of command? -->
          <el-form-item v-if="vulnerabilityType === 1 || vulnerabilityType === 2" label="Can we get result of command?"
            style="margin-bottom: 10px; font-weight: bold;">
            <el-radio-group v-model="canGetCommandResult">
              <el-radio :label="1">Yes</el-radio>
              <el-radio :label="0">No</el-radio>
            </el-radio-group>
          </el-form-item>

          <el-button type="primary" @click="generateTemplate" style="margin-bottom: 20px;">生成模板</el-button>
          <!-- 生成模板按钮 -->

          <el-form-item label="文件名" style="margin-bottom: 0px; font-weight: bold;">
            <el-input type="textarea" v-model="tempFilename" rows="1"></el-input> <!-- 临时变量 -->
          </el-form-item>
          <div style="font-weight: bold; margin-bottom: 4px;margin-top: 8px;">代码</div> <!-- 标签部分 -->
          <el-form-item style="margin-bottom: 0px;">
            <CodeEditor v-model="tempnewcode" />
          </el-form-item>
          <!--          <el-form-item label="代码" style="margin-bottom: 0px; font-weight: bold;">-->
          <!--            <el-input type="textarea" v-model="tempnewcode" rows="15"></el-input> &lt;!&ndash; 临时变量 &ndash;&gt;-->
          <!--          </el-form-item>-->
        </el-form>
        <span slot="footer" class="dialog-footer">
          <el-button @click="clearCode">清空</el-button> <!-- 添加“清空”按钮 -->
          <el-button @click="codeDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveCode">保存</el-button>
        </span>
      </el-dialog>
    </el-dialog>

    <el-dialog :visible.sync="dialogVisible" width="60%" :height="400" title="POC代码">
      <pre style="height: 500px; overflow-y: scroll;"><code class="language-python">{{ selectedPocCode }}</code></pre>
    </el-dialog>

    <!--    编辑poc代码   -->
    <el-dialog :visible.sync="editDialogVisible" title="编辑POC" width="500px" :close-on-click-modal="false">
      <el-form :model="editPoc" ref="editPocForm">
        <el-form-item label="CVE编号">
          <el-input v-model="editPoc.cve_id" placeholder="CVE-xxxx-xxxx"></el-input>
        </el-form-item>
        <el-form-item label="漏洞名称">
          <el-input v-model="editPoc.vul_name"></el-input>
        </el-form-item>
        <el-form-item label="漏洞描述">
          <el-input type="textarea" v-model="editPoc.description"></el-input>
        </el-form-item>
        <el-form-item label="POC类型">
          <el-select v-model="editPoc.script_type" placeholder="请选择">
            <el-option label="python" value="python"></el-option>
            <el-option label="c/c++" value="c/c++"></el-option>
            <el-option label="yaml" value="yaml"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="POC代码">
          <el-upload class="upload-demo" ref="upload" :http-request="handleFileUpload" :before-upload="beforeFileUpload"
            :on-remove="handleRemove" :file-list="fileList" :limit="1" accept=".py">
            <el-button>选择文件</el-button>
            <!--            <span slot="tip" class="el-upload__tip">只能上传.py文件</span>-->
          </el-upload>
          <el-button @click="editPocCode" style="margin-top: 10px;margin-left: 69px">编辑poc代码</el-button>
          <i v-if="newcode" class="el-icon-circle-check" style="color: green;"></i>
        </el-form-item>
      </el-form>
      <span slot="footer" class="dialog-footer">
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitEditPoc">确定</el-button>
      </span>

      <!--      编辑poc-编辑poc代码       -->
      <el-dialog :visible.sync="editPocCodeDialogVisible" :append-to-body="true" width="1000px" class="custom-dialog">

        <!-- 标题部分，添加内联样式 -->
        <template slot="title">
          <div style="background-color: #f5f5f5; padding: 20px; font-weight: bold; margin: -20px -20px 0 -20px;">
            编辑POC代码
          </div>
        </template>
        <el-form>

          <el-form-item label="文件名" style="margin-bottom: 0px; font-weight: bold;">
            <el-input type="textarea" v-model="tempFilename" rows="1"></el-input> <!-- 临时变量 -->
          </el-form-item>
          <div style="font-weight: bold; margin-bottom: 4px;margin-top: 8px;">代码</div> <!-- 标签部分 -->
          <el-form-item style="margin-bottom: 0px;">
            <CodeEditor v-model="tempnewcode" />
          </el-form-item>
          <!--          <el-form-item label="代码" style="margin-bottom: 0px; font-weight: bold;">-->
          <!--            <CodeEditor v-model="tempnewcode"/>-->
          <!--&lt;!&ndash;            <el-input type="textarea" v-model="tempnewcode" rows="15"></el-input> &lt;!&ndash; 临时变量 &ndash;&gt;&ndash;&gt;-->
          <!--          </el-form-item>-->
        </el-form>
        <span slot="footer" class="dialog-footer">
          <el-button @click="clearCode">清空</el-button> <!-- 添加“清空”按钮 -->
          <el-button @click="editPocCodeDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveCode2">保存</el-button>
        </span>
      </el-dialog>
    </el-dialog>



    <el-table :data="paginatedData" style="width: 100%" ref="table">
      <el-table-column type="selection" width="55"></el-table-column>
      <el-table-column prop="id" label="ID" width="50"></el-table-column>
      <el-table-column prop="cve_id" label="CVE编号" width="170"></el-table-column>
      <el-table-column prop="vul_name" label="漏洞名称" width="130"></el-table-column>
      <el-table-column prop="description" label="漏洞描述" width="280">
        <template slot-scope="scope">
          <span v-if="!scope.row.showFullDescription">
            {{ scope.row.description.slice(0, 40) }}...
            <el-button type="text" @click="toggleDescription(scope.row)">展开</el-button>
          </span>
          <span v-else>
            {{ scope.row.description }}
            <el-button type="text" @click="toggleDescription(scope.row)">收起</el-button>
          </span>
        </template>
      </el-table-column>
      <el-table-column prop="cvss_mark" label="CVSS评分" width="130"></el-table-column>
      <el-table-column prop="script_state" label="POC状态" width="130"></el-table-column>
      <el-table-column prop="script_type" label="POC类型" width="130"></el-table-column>

      <el-table-column prop="script" label="POC代码" width="150">
        <template slot-scope="scope">
          <el-button type="success" @click="handleLook(scope.row)">查看</el-button>
        </template>
      </el-table-column>
      <el-table-column prop="timestamp" label="修改时间" width="160"></el-table-column>
      <el-table-column label="操作" align="center">
        <template slot-scope="scope">
          <el-button type="success" style="width: 80px;margin-left: 5px" @click="handleEdit(scope.row)">编辑 <i
              class="el-icon-edit"></i></el-button>
          <el-popconfirm title="您确定要删除这条数据吗？" @confirm="del(scope.row.id)">
            <template v-slot:reference>
              <el-button type="danger" style="width: 80px;margin-left: 5px">删除 <i
                  class="el-icon-delete"></i></el-button>
            </template>
          </el-popconfirm>

        </template>
      </el-table-column>
    </el-table>
    <el-pagination @size-change="handleSizeChange" @current-change="handleCurrentChange" :current-page="currentPage"
      :page-size="pageSize" :total="totalItems" layout="total, sizes, prev, pager, next, jumper">
    </el-pagination>
  </div>
</template>

<script>
import Prism from 'prismjs';
import 'prismjs/themes/prism.css';  // 或者选择你喜欢的主题
import axios from 'axios';
import CodeEditor from '@/components/CodeEditor.vue'; // 引入 CodeEditor 组件

export default {
  name: "pocManage",
  components: {
    CodeEditor,
  },
  data() {
    return {
      addDialogVisible: false,
      codeDialogVisible: false,
      newPoc: {
        cve_id: '',
        vul_name: '',
        description: '',
        script_type: '',
        //script: ''
      },
      //用来编辑poc
      editPoc: {
        id: '',
        cve_id: '',
        vul_name: '',
        description: '',
        script_type: '',
        script: ''
      },
      editDialogVisible: false,
      codeEditDialogVisible: false,
      editPocCodeDialogVisible: false,
      tempCode: '', // 临时存储代码输入
      //用来是实现搜索
      searchKeyword: '',
      showFullDescription: {},
      dialogVisible: false,
      selectedPocCode: '',
      currentPage: 1,
      pageSize: 10,
      totalItems: 0,
      pocs: [],
      fileList: [],
      tempFilename: '',  // 临时文件名变量
      tempnewcode: '',      // 临时代码内容变量
      newcode: '', // 存储POC代码
      editFilename: '',
      vulnerabilityType: 0, // 漏洞类型
      authRequired: 1, // 身份验证，默认是Yes
      canGetCommandResult: 1, // 命令执行结果，默认是Yes
      // codeMirrorOptions: {
      //   mode: 'python',      // 设置为 Python 模式
      //   theme: 'material',   // 设置编辑器的主题
      //   lineNumbers: true,   // 显示行号
      //   tabSize: 4,          // 缩进为 4 个空格
      //   indentUnit: 4,       // 缩进单位
      //   indentWithTabs: true,
      //   lineWrapping: true,  // 自动换行
      // },
    };
  },
  watch: {
    codeDialogVisible(newVal) {
      if (newVal) { // 当对话框变为可见时
        // 当对话框打开时，将实际变量的值赋给临时变量
        this.tempFilename = this.editFilename;
        this.tempnewcode = this.newcode;
        this.$nextTick(() => {
          this.$refs.codeInput.focus(); // 聚焦到输入框
        });
      }
    },
    editPocCodeDialogVisible(newVal) {
      if (newVal) { // 当对话框变为可见时
        // 当对话框打开时，将实际变量的值赋给临时变量
        this.tempFilename = this.tempCode;
        this.tempnewcode = this.selectedPocCode;
        this.$nextTick(() => {
          this.$refs.codeInput.focus(); // 聚焦到输入框
        });
      }
    },
    watch: {
      dialogVisible(newVal) {
        if (!newVal) {
          this.selectedPocCode = ''; // 当对话框关闭时清空代码
        } else {
          this.$nextTick(() => {
            Prism.highlightAll();  // 应用 Prism 高亮
          });
        }
      }
    }

  },
  computed: {
    paginatedData() {
      const start = (this.currentPage - 1) * this.pageSize;
      const end = start + this.pageSize;
      return this.pocs.slice(start, end);
    }
  },
  methods: {
    //搜索的实现
    load() {
      // let keyword = encodeURIComponent(this.searchKeyword.trim());
      // let query = new URLSearchParams({ keyword }).toString();
      let query = new URLSearchParams({ keyword: this.searchKeyword.trim() }).toString();
      fetch(`/api/searchData?${query}`)
        .then(response => {
          if (!response.ok) {
            throw new Error('Network response was not ok');
          }
          return response.json();
        })
        .then(data => {
          this.pocs = data.map(poc => ({
            ...poc,
            showFullDescription: false
          }));
          this.totalItems = this.pocs.length;
        })
        .catch(error => {
          console.error('Error fetching data:', error);
        });
    },

    reset() {
      this.searchKeyword = ''; // 清空搜索关键字
      this.loadData(); // 重新加载所有数据
    },

    toggleDescription(poc) {
      poc.showFullDescription = !poc.showFullDescription;
    },

    handleLook(row) {
      // 发送请求获取POC内容
      axios.get('/api/getPOCContent', {
        params: {
          id: row.id
        }
      })
        .then(response => {
          if (response.status === 200) {
            this.selectedPocCode = response.data.content;
            this.$nextTick(() => {
              this.dialogVisible = true;
            });
          } else {
            // 处理非200响应状态码
            console.error('Failed to fetch POC content:', response.status, response.statusText);
            // this.$message.error('操作失败: ' + response.data.error);
          }
        })
        .catch(error => {
          if (error.response && error.response.status === 500) {
            // 处理500错误状态码
            this.$message.error(error.response.data.error);
          } else {
            // 处理其他错误
            console.error('Error fetching POC content:', error);
            this.$message.error('操作失败: ' + error);
          }
        });
    },

    handleSizeChange(newSize) {
      this.pageSize = newSize;
      this.loadData();
    },
    handleCurrentChange(newPage) {
      this.currentPage = newPage;
      this.loadData();
    },
    loadData() {
      fetch('/api/getAllData')
        .then(response => {
          if (!response.ok) {
            throw new Error('Network response was not ok');
          }
          return response.json();
        })
        .then(data => {
          this.pocs = data.map(poc => ({
            id: poc.id,
            cve_id: poc.cve_id,
            vul_name: poc.vul_name,
            description: poc.description,
            script_type: poc.script_type,
            script: poc.script,
            timestamp: poc.timestamp,
            showFullDescription: false  // 保持这个字段，用于控制描述的展开/收起
          }));
          this.totalItems = this.pocs.length;
        })
        .catch(error => {
          console.error('Error fetching data:', error);
        });
    },
    handleAdd() {
      this.addDialogVisible = true;
    },

    //编辑poc
    handleEdit(row) {
      this.editPoc = { ...row }; // 复制行数据到编辑数据对象
      this.tempCode = row.script; // Set the temporary code to the existing script
      axios.get('/api/getPOCContent', {
        params: {
          id: row.id
        }
      })
        .then(response => {
          this.selectedPocCode = response.data.content;
        })
      this.editDialogVisible = true;
    },

    del(id) {
      fetch(`/api/deleteDataById`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ ids: id })
      })
        .then(response => {
          if (response.ok) {
            this.$message.success('删除成功！');
            this.loadData();  // 重新加载数据
          } else {
            this.$message.error('删除失败！');
          }
        })
        .catch(error => {
          console.error('删除操作失败:', error);
          this.$message.error('删除操作失败: ' + error.message);
        });
    },

    delBatch() {
      const idsToDelete = this.$refs.table.selection.map(row => row.id);
      fetch(`/api/deleteDataById`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ ids: idsToDelete })
      })
        .then(response => {
          if (response.ok) {
            this.$message.success('批量删除成功！');
            this.loadData();  // 重新加载数据
          } else {
            this.$message.error('批量删除失败！');
          }
        })
        .catch(error => {
          console.error('批量删除操作失败:', error);
          this.$message.error('批量删除操作失败: ' + error.message);
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

    // 触发编辑代码窗口(新增poc部分）
    editCode() {
      this.codeDialogVisible = true;
    },

    //触发编辑代码窗口(修改poc部分）
    editPocCode() {
      this.editPocCodeDialogVisible = true;
    },
    // 保存代码
    saveCode() {
      // 检查文件名是否以 .py 结尾
      if (!this.tempFilename.endsWith('.py')) {
        this.$message.error('文件名错误，必须以 .py 结尾');
        return;  // 停止保存流程
      }

      // 正则表达式数组（多行模式，处理空格和换行）
      const requiredFields = [
        { regex: /class\s+DemoPOC\s*:/m, label: 'class DemoPOC' },  // 类定义
        { regex: /def\s+__init__\s*\(self,\s*url,\s*ip,\s*port\)/m, label: 'def __init__(self,url,ip,port)' },  // 构造函数
        { regex: /def\s+_verify\s*\(self\)/m, label: 'def _verify(self)' },  // _verify 方法
        { regex: /result\['VerifyInfo'\]/m, label: "result['VerifyInfo']" },  // result['VerifyInfo']
        { regex: /\[!\]/m, label: '[!]' },  // [!]
        { regex: /\[SAFE\]/m, label: '[SAFE]' }  // [SAFE]
      ];

      // 检查每个正则表达式是否匹配代码
      let allFieldsPresent = true;
      requiredFields.forEach(field => {
        const isMatch = field.regex.test(this.tempnewcode);
        console.log(`Checking field: ${field.label}, Match: ${isMatch}`);  // 调试输出
        if (!isMatch) {
          this.$message.error(`代码中缺少必要的字段：${field.label}`);
          allFieldsPresent = false;  // 如果任意字段未匹配，标记为 false
        }
      });

      if (!allFieldsPresent) {
        return;  // 停止保存流程
      }

      // 如果检查都通过，保存临时变量到实际变量中
      this.editFilename = this.tempFilename;  // 将临时文件名赋值给实际文件名变量
      this.newcode = this.tempnewcode;           // 将临时代码赋值给实际代码变量
      this.codeDialogVisible = false;         // 关闭对话框
    },

    // 编辑poc的保存代码
    saveCode2() {
      // 检查文件名是否以 .py 结尾
      if (!this.tempFilename.endsWith('.py')) {
        this.$message.error('文件名错误，必须以 .py 结尾');
        return;  // 停止保存流程
      }

      // 正则表达式数组（多行模式，处理空格和换行）
      const requiredFields = [
        { regex: /class\s+DemoPOC\s*:/m, label: 'class DemoPOC' },  // 类定义
        { regex: /def\s+__init__\s*\(self,\s*url,\s*ip,\s*port\)/m, label: 'def __init__(self,url,ip,port)' },  // 构造函数
        { regex: /def\s+_verify\s*\(self\)/m, label: 'def _verify(self)' },  // _verify 方法
        { regex: /result\['VerifyInfo'\]/m, label: "result['VerifyInfo']" },  // result['VerifyInfo']
        { regex: /\[!\]/m, label: '[!]' },  // [!]
        { regex: /\[SAFE\]/m, label: '[SAFE]' }  // [SAFE]
      ];

      // 检查每个正则表达式是否匹配代码
      let allFieldsPresent = true;
      requiredFields.forEach(field => {
        const isMatch = field.regex.test(this.tempnewcode);
        console.log(`Checking field: ${field.label}, Match: ${isMatch}`);  // 调试输出
        if (!isMatch) {
          this.$message.error(`代码中缺少必要的字段：${field.label}`);
          allFieldsPresent = false;  // 如果任意字段未匹配，标记为 false
        }
      });

      if (!allFieldsPresent) {
        return;  // 停止保存流程
      }

      // 如果检查都通过，保存临时变量到实际变量中
      this.editFilename = this.tempFilename;  // 将临时文件名赋值给实际文件名变量
      this.newcode = this.tempnewcode;           // 将临时代码赋值给实际代码变量
      this.editPocCodeDialogVisible = false;         // 关闭对话框
    },

    // 清空代码并关闭窗口
    clearCode() {
      this.newcode = ''; // 清空newcode
      this.codeDialogVisible = false; // 关闭窗口
    },
    clearCode2() {
      this.newcode = ''; // 清空newcode
      this.editPocCodeDialogVisible = false; // 关闭窗口
    },
    async submitNewPoc() {
      const formData = new FormData();
      formData.append('cve_id', this.newPoc.cve_id);
      formData.append('vul_name', this.newPoc.vul_name);
      formData.append('description', this.newPoc.description);
      formData.append('script_type', this.newPoc.script_type);
      if (this.fileList.length > 0) {
        formData.append('mode', 'upload');
        formData.append('file', this.fileList[0].raw || this.fileList[0]); // 添加文件到表单数据
      } else if (this.newcode.length > 0) {
        formData.append('mode', 'edit');
        formData.append('edit_filename', this.editFilename);
        formData.append('poc_content', this.newcode);
      }

      try {
        const response = await fetch('/api/insertData', {
          method: 'POST',
          body: formData,
        });
        const result = await response.json();
        if (response.ok) {
          this.$message.success(result.message);
          this.addDialogVisible = false;
          this.$refs.newPocForm.resetFields();
          this.fileList = [];
        } else {
          this.$message.error(result.message);
        }
      } catch (error) {
        this.$message.error('An error occurred: ' + error);
      }
    },
    async submitEditPoc() {
      const formData = new FormData();
      formData.append('id', this.editPoc.id);
      formData.append('cve_id', this.editPoc.cve_id);
      formData.append('vul_name', this.editPoc.vul_name);
      formData.append('type', this.editPoc.type); // 确保字段名称正确
      formData.append('description', this.editPoc.description);
      formData.append('script_type', this.editPoc.script_type);

      // 添加文件，如果有的话
      if (this.fileList.length > 0) {
        formData.append('mode', 'upload');
        formData.append('file', this.fileList[0]); // 这里的字段名称应与后端一致
      } else if (this.editFilename.length > 0 && this.newcode.length > 0) {
        formData.append('mode', 'edit');
        formData.append('edit_filename', this.editFilename);
        formData.append('poc_content', this.newcode);
      }

      try {
        const response = await axios.put('/api/updateDataById', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });

        if (response.data.message === '更新成功') { // 后端可能返回的成功消息字段为 "message"
          this.$message.success('POC更新成功');
          this.editDialogVisible = false;
          this.fileList = [];
          window.location.reload();
        } else {
          this.$message.error('更新失败: ' + response.data.message);
        }
      } catch (error) {
        this.$message.error('网络错误或服务器异常: ' + error.message);
      }
    },

    // 生成模板
    async generateTemplate() {
      // 构造文件名，根据选择的漏洞类型和选项
      let filename = `${this.vulnerabilityType}${this.authRequired}`;
      if (this.vulnerabilityType === 1 || this.vulnerabilityType === 2) {
        filename += `${this.canGetCommandResult}`;
      }
      filename += '.py';

      // 加载文件内容，从`public`目录下读取
      fetch(`/${filename}`)
        .then(response => {
          if (!response.ok) {
            throw new Error('Network response was not ok');
          }
          return response.text();
        })
        .then(data => {
          this.tempnewcode = data; // 将文件内容保存到tempnewcode
        })
        .catch(error => {
          console.error('无法读取模板文件:', error);
          this.tempnewcode = '# 无法读取模板文件';
        });
    },

  },


  created() {
    this.loadData();
  }
}
</script>

<style scoped>
/*设置窗口内容自动换行*/
pre {
  white-space: pre-wrap;
  /* CSS3 的换行方式，保持格式的同时允许自动换行 */
  word-wrap: break-word;
  /* 较旧的浏览器也可以理解这种方式 */
  overflow-wrap: break-word;
  /* 标准的换行方式 */
  overflow-y: auto;
}

code[class*="language-"],
pre[class*="language-"] {
  color: black;
  /* 代码文字颜色 */
  background: none;
  /* 背景色 */
  text-shadow: 0 1px white;
  /* 文字阴影 */
  font-family: Consolas, Monaco, 'Andale Mono', 'Ubuntu Mono', monospace;
  font-size: 1em;
  text-align: left;
  white-space: pre;
  word-spacing: normal;
  word-break: normal;
  word-wrap: normal;
  line-height: 1.5;

  -moz-tab-size: 4;
  -o-tab-size: 4;
  tab-size: 4;

  -webkit-hyphens: none;
  -moz-hyphens: none;
  -ms-hyphens: none;
  hyphens: none;
}
</style>