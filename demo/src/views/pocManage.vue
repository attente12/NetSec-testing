<template>
  <div>
    <h1 id="pocmanage">POC管理</h1>

    <div style="margin: 10px 0">
      <el-input style="width: 200px;margin-left: 5px;margin-right: 10px" placeholder="请输入搜索关键字" suffix-icon="el-icon-search" v-model="searchKeyword"></el-input>
      <el-button class="ml-5" type="primary" @click="load">搜索</el-button>
      <el-button type="warning" @click="reset">重置</el-button>
    </div>

    <div style="margin: 10px 0">
      <el-button style="width: 80px;margin-left: 5px" type="primary" @click="handleAdd">新增 <i class="el-icon-circle-plus-outline"></i></el-button>
      <el-popconfirm
          class="ml-5"
          confirm-button-text="确定"
          cancel-button-text="我再想想"
          icon="el-icon-info"
          icon-color="red"
          title="您确定批量删除这些数据吗？"
          @confirm="delBatch"
      >
        <template v-slot:reference>
          <el-button style="width: 120px;margin: 10px" type="danger">批量删除 <i class="el-icon-remove-outline"></i></el-button>
        </template>
      </el-popconfirm>
    </div>

    <!-- 新增POC对话框 -->
    <el-dialog :visible.sync="addDialogVisible" title="新增POC" width="500px" :close-on-click-modal="false">
      <el-form :model="newPoc" ref="newPocForm">
        <el-form-item label="CVE编号">
          <el-input v-model="newPoc.cve_id" placeholder="CVE-xxxx-xxxx"></el-input>
        </el-form-item>
        <el-form-item label="漏洞名称">
          <el-input v-model="newPoc.vul_name"></el-input>
        </el-form-item>
        <!-- 修改为下拉选择框 -->
        <el-form-item label="漏洞类型">
          <el-select v-model="newPoc.type" placeholder="请选择漏洞类型" style="width: 100%;">
            <el-option
                v-for="type in vulTypes"
                :key="type"
                :label="type"
                :value="type">
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="漏洞描述">
          <el-input type="textarea" v-model="newPoc.description"></el-input>
        </el-form-item>

        <el-form-item label="受影响的基础设施（操作系统或软件或协议）" required>
          <el-autocomplete
              v-model="searchAffectedInfra"
              :fetch-suggestions="querySearch"
              placeholder="请输入关键字进行搜索，然后从列表中选择"
              @select="handleSelectNew"
              style="width: 300px;"
          />
          <div v-if="newPoc.affected_infra" style="margin-top: 5px; color: #67C23A;">
            <i class="el-icon-check"></i> 已选择: {{ newPoc.affected_infra }}
          </div>
          <div v-if="!affectedInfraValid && submitAttempted" style="color: #F56C6C; margin-top: 5px;">
            <i class="el-icon-warning"></i> 请从列表中选择一个有效选项
          </div>
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
          <el-upload
              class="upload-demo"
              ref="upload"
              :http-request="handleFileUpload"
              :before-upload="beforeFileUpload"
              :on-remove="handleRemove"
              :file-list="fileList"
              :limit="1">
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

      <el-dialog
          :visible.sync="codeDialogVisible"
          :append-to-body="true"
          width="1200px"
          class="custom-dialog">

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
          <el-form-item v-if="vulnerabilityType === 1 || vulnerabilityType === 2" label="Can we get result of command?" style="margin-bottom: 10px; font-weight: bold;">
            <el-radio-group v-model="canGetCommandResult">
              <el-radio :label="1">Yes</el-radio>
              <el-radio :label="0">No</el-radio>
            </el-radio-group>
          </el-form-item>

          <el-button type="primary" @click="generateTemplate" style="margin-bottom: 20px;">生成模板</el-button> <!-- 生成模板按钮 -->

          <el-form-item label="文件名" style="margin-bottom: 0px; font-weight: bold;">
            <el-input type="textarea" v-model="tempFilename" rows="1"></el-input> <!-- 临时变量 -->
          </el-form-item>
          <div style="font-weight: bold; margin-bottom: 4px;margin-top: 8px;">代码</div> <!-- 标签部分 -->
          <el-form-item style="margin-bottom: 0px;">
            <CodeEditor v-model="tempnewcode" />
          </el-form-item>
        </el-form>
        <span slot="footer" class="dialog-footer">
          <el-button @click="clearCode">清空</el-button> <!-- 添加"清空"按钮 -->
          <el-button @click="codeDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveCode">保存</el-button>
        </span>
      </el-dialog>
    </el-dialog>

    <el-dialog :visible.sync="dialogVisible" width="60%" :height="400" title="POC代码">
      <pre style="height: 500px; overflow-y: scroll;"><code class="language-python">{{ selectedPocCode }}</code></pre>
    </el-dialog>

    <!-- 编辑POC对话框 -->
    <el-dialog :visible.sync="editDialogVisible" title="编辑POC" width="500px" :close-on-click-modal="false">
      <el-form :model="editPoc" ref="editPocForm">
        <el-form-item label="CVE编号">
          <el-input v-model="editPoc.cve_id" placeholder="CVE-xxxx-xxxx"></el-input>
        </el-form-item>
        <el-form-item label="漏洞名称">
          <el-input v-model="editPoc.vul_name"></el-input>
        </el-form-item>
        <!-- 修改为下拉选择框 -->
        <el-form-item label="漏洞类型">
          <el-select v-model="editPoc.type" placeholder="请选择漏洞类型" style="width: 100%;">
            <el-option
                v-for="type in vulTypes"
                :key="type"
                :label="type"
                :value="type">
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="漏洞描述">
          <el-input type="textarea" v-model="editPoc.description"></el-input>
        </el-form-item>

        <el-form-item label="受影响的基础设施（操作系统或软件或协议）" required>
          <el-autocomplete
              v-model="editSearchAffectedInfra"
              :fetch-suggestions="querySearch"
              placeholder="请输入关键字进行搜索，然后从列表中选择"
              @select="handleSelectEdit"
              style="width: 300px;"
          />
          <div v-if="editPoc.affected_infra" style="margin-top: 5px; color: #67C23A;">
            <i class="el-icon-check"></i> 已选择: {{ editPoc.affected_infra }}
          </div>
          <div v-if="!editAffectedInfraValid && editSubmitAttempted" style="color: #F56C6C; margin-top: 5px;">
            <i class="el-icon-warning"></i> 请从列表中选择一个有效选项
          </div>
        </el-form-item>
        <el-form-item label="POC类型">
          <el-select v-model="editPoc.script_type" placeholder="请选择">
            <el-option label="python" value="python"></el-option>
            <el-option label="c/c++" value="c/c++"></el-option>
            <el-option label="yaml" value="yaml"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="POC代码">
          <el-upload
              class="upload-demo"
              ref="upload"
              :http-request="handleFileUpload"
              :before-upload="beforeFileUpload"
              :on-remove="handleRemove"
              :file-list="fileList"
              :limit="1"
              accept=".py">
            <el-button>选择文件</el-button>
          </el-upload>
          <el-button @click="editPocCode" style="margin-top: 10px;margin-left: 69px">编辑poc代码</el-button>
          <i v-if="newcode" class="el-icon-circle-check" style="color: green;"></i>
        </el-form-item>
      </el-form>
      <span slot="footer" class="dialog-footer">
        <el-button @click="cancelEdit">取消</el-button>
        <el-button type="primary" @click="submitEditPoc">确定</el-button>
      </span>

      <!-- 编辑poc-编辑poc代码 -->
      <el-dialog
          :visible.sync="editPocCodeDialogVisible"
          :append-to-body="true"
          width="1000px"
          class="custom-dialog">

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
        </el-form>
        <span slot="footer" class="dialog-footer">
          <el-button @click="clearCode">清空</el-button> <!-- 添加"清空"按钮 -->
          <el-button @click="editPocCodeDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveCode2">保存</el-button>
        </span>
      </el-dialog>
    </el-dialog>

    <el-table :data="paginatedData" style="width: 100%" ref="table">
      <el-table-column type="selection" width="50"></el-table-column>
      <!-- 新增：逻辑ID列，放在第一列 -->
      <el-table-column label="id" width="50" align="center">
        <template slot-scope="scope">
          {{ (currentPage - 1) * pageSize + scope.$index + 1 }}
        </template>
      </el-table-column>
<!--      <el-table-column prop="id" label="ID" width="50"></el-table-column>-->
      <el-table-column prop="cve_id" label="CVE编号" width="170"></el-table-column>
      <el-table-column prop="vul_name" label="漏洞名称" width="130"></el-table-column>
      <el-table-column prop="type" label="漏洞类型" width="110"></el-table-column>
      <el-table-column prop="affected_infra" label="漏洞影响的范围" width="130"></el-table-column>
      <el-table-column prop="description" label="漏洞描述" width="250">
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
      <el-table-column prop="script_type" label="POC类型" width="85"></el-table-column>

      <el-table-column prop="script" label="POC代码" width="100">
        <template slot-scope="scope">
          <el-button type="success" @click="handleLook(scope.row)">查看</el-button>
        </template>
      </el-table-column>
      <el-table-column prop="timestamp" label="修改时间" width="160"></el-table-column>
      <el-table-column label="操作" align="center">
        <template slot-scope="scope">
          <el-button type="success" style="width: 80px;margin-left: 5px" @click="handleEdit(scope.row)">编辑 <i class="el-icon-edit"></i></el-button>
          <el-popconfirm
              title="您确定要删除这条数据吗？"
              @confirm="del(scope.row.id)"
          >
            <template v-slot:reference>
              <el-button type="danger" style="width: 80px;margin-left: 5px">删除 <i class="el-icon-delete"></i></el-button>
            </template>
          </el-popconfirm>

        </template>
      </el-table-column>
    </el-table>
    <el-pagination
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
        :current-page="currentPage"
        :page-size="pageSize"
        :total="totalItems"
        layout="total, sizes, prev, pager, next, jumper">
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
  data(){
    return{
      addDialogVisible: false,
      codeDialogVisible: false,
      // 漏洞类型列表
      vulTypes: [],
      // vulTypes: [
      //   "缓冲区溢出",
      //   "文件上传漏洞",
      //   "代码注入",
      //   "SQL 注入",
      //   "跨站脚本攻击 (XSS)",
      //   "权限提升",
      //   "拒绝服务攻击 (DoS)",
      //   "身份验证绕过",
      //   "路径遍历",
      //   "信息泄露",
      //   "跨站请求伪造 (CSRF)",
      //   "XML 外部实体注入 (XXE)",
      //   "远程代码执行 (RCE)",
      //   "会话劫持",
      //   "未经授权的访问",
      //   "其他类型"
      // ],
      newPoc: {
        type: '',
        cve_id: '',
        vul_name: '',
        description: '',
        script_type: '',
        affected_infra: '',
        //script: ''
      },
      // 搜索时使用的输入值（不会被提交）
      searchAffectedInfra: '',

      //用来编辑poc
      editPoc: {
        id: '',
        cve_id: '',
        vul_name: '',
        type: '',
        description: '',
        affected_infra: '',
        script_type: '',
        script: '',
      },

      // 搜索时使用的输入值（不会被提交）
      editSearchAffectedInfra: '',

      // 验证标记
      affectedInfraValid: false,
      editAffectedInfraValid: false,

      editDialogVisible: false,
      codeEditDialogVisible: false,
      editPocCodeDialogVisible:false,
      tempCode: '', // 临时存储代码输入
      //用来是实现搜索
      searchKeyword: '',
      showFullDescription: {},
      dialogVisible: false,
      selectedPocCode: '',
      currentPage: 1,
      pageSize: 10,
      totalItems: 0,
      pocs:[],
      fileList: [],
      tempFilename: '',  // 临时文件名变量
      tempnewcode: '',      // 临时代码内容变量
      newcode: '', // 存储POC代码
      editFilename: '',
      vulnerabilityType: 0, // 漏洞类型
      authRequired: 1, // 身份验证，默认是Yes
      canGetCommandResult: 1, // 命令执行结果，默认是Yes
      submitAttempted: false, // 提交尝试标记
      editSubmitAttempted: false, // 编辑提交尝试标记
      suggestions: [], // 将文件内容读取后填充到此数组，格式为 { value: "文本" }
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
        // 修改：优先使用newcode，如果newcode为空则使用selectedPocCode
        this.tempFilename = this.editFilename || this.tempCode; // 优先使用已保存的文件名
        this.tempnewcode = this.newcode || this.selectedPocCode; // 优先使用已保存的代码
        this.$nextTick(() => {
          this.$refs.codeInput.focus(); // 聚焦到输入框
        });
      }
    },
    dialogVisible(newVal) {
      if (!newVal) {
        this.selectedPocCode = ''; // 当对话框关闭时清空代码
      } else {
        this.$nextTick(() => {
          Prism.highlightAll();  // 应用 Prism 高亮
        });
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
  methods:{
    loadVulTypes() {
      fetch('/api/poc/getAllVulnTypes')
          .then(response => {
            if (!response.ok) {
              throw new Error('Network response was not ok');
            }
            return response.json();
          })
          .then(data => {
            this.vulTypes = data.types; // 将API返回的类型列表赋值给 vulTypes
          })
          .catch(error => {
            console.error('Error fetching vulnerability types:', error);
            // 设置一个默认的漏洞类型列表作为备用
            this.vulTypes = [
                "缓冲区溢出",
                "文件上传漏洞",
                "代码注入",
                "SQL 注入",
                "跨站脚本攻击 (XSS)",
                "权限提升",
                "拒绝服务攻击 (DoS)",
                "身份验证绕过",
                "路径遍历",
                "信息泄露",
                "跨站请求伪造 (CSRF)",
                "XML 外部实体注入 (XXE)",
                "远程代码执行 (RCE)",
                "会话劫持",
                "未经授权的访问",
                "其他类型"
            ];
          });
    },
    //搜索的实现
    load() {
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
              cve_id: poc.vuln_id,
              affected_infra: poc.affected_infra,
              type: poc.type,
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
      this.submitAttempted = false;
      this.affectedInfraValid = false;
      this.searchAffectedInfra = '';
      this.newPoc = {
        type: '',
        cve_id: '',
        vul_name: '',
        description: '',
        script_type: '',
        affected_infra: '',
        // 其他属性的重置...
      };
    },

    //编辑poc
    handleEdit(row) {
      this.editPoc = { ...row }; // 复制行数据到编辑数据对象
      this.tempCode = row.script; // Set the temporary code to the existing script
      // 如果有affected_infra，则初始化为有效
      if (row.affected_infra && this.suggestions.some(item => item.value === row.affected_infra)) {
        this.editAffectedInfraValid = true;
        this.editSearchAffectedInfra = row.affected_infra; // 显示已有的值
      } else {
        this.editAffectedInfraValid = false;
        this.editSearchAffectedInfra = '';
        this.editPoc.affected_infra = '';
      }

      this.editSubmitAttempted = false;

      axios.get('/api/getPOCContent', {
        params: {
          id: row.id
        }
      })
          .then(response => {
            this.selectedPocCode = response.data.content;
          })
      this.editDialogVisible=true;
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
            /def\s+_verify\s*\(self\)/,     // 检查是否有 def _verify(self)
            /result\[['"]VerifyInfo['"]\]/, // 检查是否有 result['VerifyInfo'] 或 result["VerifyInfo"]
            /\[!\]/,                       // 检查是否有 [!]
            /\[SAFE\]/                     // 检查是否有 [SAFE]
          ];

          // 检查两种初始化方法中的任意一个
          const initPatterns = [
            /def\s+__init__\s*\(self,\s*url,\s*ip,\s*port\)/, // 检查是否有 def __init__(self, url, ip, port)
            /def\s+__init__\s*\(self,\s*url,\s*ip,\s*port,\s*server_ip,\s*server_port\)/ // 检查是否有 def __init__(self, url, ip, port, server_ip, server_port)
          ];

          // 检查必要内容是否满足要求
          const isValidRequiredPatterns = requiredPatterns.every((pattern) => pattern.test(content));
          // 检查两种初始化方法中是否有一个满足要求
          const isValidInitPattern = initPatterns.some((pattern) => pattern.test(content));

          if (!isValidRequiredPatterns || !isValidInitPattern) {
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
        { regex: /def\s+_verify\s*\(self\)/m, label: 'def _verify(self)' },  // _verify 方法
        { regex: /result\['VerifyInfo'\]/m, label: "result['VerifyInfo']" },  // result['VerifyInfo']
        { regex: /\[!\]/m, label: '[!]' },  // [!]
        { regex: /\[SAFE\]/m, label: '[SAFE]' }  // [SAFE]
      ];

      // 初始化方法的两种可能模式
      const initMethods = [
        { regex: /def\s+__init__\s*\(self,\s*url,\s*ip,\s*port\)/m, label: 'def __init__(self,url,ip,port)' },
        { regex: /def\s+__init__\s*\(self,\s*url,\s*ip,\s*port,\s*server_ip,\s*server_port\)/m, label: 'def __init__(self,url,ip,port,server_ip,server_port)' }
      ];

      // 检查每个必须字段是否匹配代码
      let allFieldsPresent = true;
      requiredFields.forEach(field => {
        const isMatch = field.regex.test(this.tempnewcode);
        console.log(`Checking field: ${field.label}, Match: ${isMatch}`);  // 调试输出
        if (!isMatch) {
          this.$message.error(`代码中缺少必要的字段：${field.label}`);
          allFieldsPresent = false;  // 如果任意字段未匹配，标记为 false
        }
      });

      // 检查初始化方法是否匹配其中一种模式
      const initMethodMatch = initMethods.some(method => method.regex.test(this.tempnewcode));
      console.log(`Checking init methods. Match: ${initMethodMatch}`);  // 调试输出
      if (!initMethodMatch) {
        this.$message.error(`代码中缺少必要的初始化方法，需要包含以下两种之一：
    - def __init__(self,url,ip,port)
    - def __init__(self,url,ip,port,server_ip,server_port)`);
        allFieldsPresent = false;
      }

      if (!allFieldsPresent) {
        return;  // 停止保存流程
      }

      // 如果检查都通过，保存临时变量到实际变量中
      this.editFilename = this.tempFilename;  // 将临时文件名赋值给实际文件名变量
      this.newcode = this.tempnewcode;        // 将临时代码赋值给实际代码变量
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
        { regex: /def\s+_verify\s*\(self\)/m, label: 'def _verify(self)' },  // _verify 方法
        { regex: /result\['VerifyInfo'\]/m, label: "result['VerifyInfo']" },  // result['VerifyInfo']
        { regex: /\[!\]/m, label: '[!]' },  // [!]
        { regex: /\[SAFE\]/m, label: '[SAFE]' }  // [SAFE]
      ];

      // 初始化方法的两种可能模式
      const initMethods = [
        { regex: /def\s+__init__\s*\(self,\s*url,\s*ip,\s*port\)/m, label: 'def __init__(self,url,ip,port)' },
        { regex: /def\s+__init__\s*\(self,\s*url,\s*ip,\s*port,\s*server_ip,\s*server_port\)/m, label: 'def __init__(self,url,ip,port,server_ip,server_port)' }
      ];

      // 检查每个必须字段是否匹配代码
      let allFieldsPresent = true;
      requiredFields.forEach(field => {
        const isMatch = field.regex.test(this.tempnewcode);
        console.log(`Checking field: ${field.label}, Match: ${isMatch}`);  // 调试输出
        if (!isMatch) {
          this.$message.error(`代码中缺少必要的字段：${field.label}`);
          allFieldsPresent = false;  // 如果任意字段未匹配，标记为 false
        }
      });

      // 检查初始化方法是否匹配其中一种模式
      const initMethodMatch = initMethods.some(method => method.regex.test(this.tempnewcode));
      console.log(`Checking init methods. Match: ${initMethodMatch}`);  // 调试输出
      if (!initMethodMatch) {
        this.$message.error(`代码中缺少必要的初始化方法，需要包含以下两种之一：
    - def __init__(self,url,ip,port)或
    - def __init__(self,url,ip,port,server_ip,server_port)`);
        allFieldsPresent = false;
      }

      if (!allFieldsPresent) {
        return;  // 停止保存流程
      }

      // 如果检查都通过，保存临时变量到实际变量中
      this.editFilename = this.tempFilename;  // 将临时文件名赋值给实际文件名变量
      this.newcode = this.tempnewcode;        // 将临时代码赋值给实际代码变量
      this.editPocCodeDialogVisible = false;  // 关闭对话框
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
      this.submitAttempted = true;

      // 检查是否选择了有效的affected_infra
      if (!this.affectedInfraValid || !this.newPoc.affected_infra) {
        this.$message.error('请从列表中选择有效的基础设施');
        return;
      }

      const formData = new FormData();
      formData.append('cve_id', this.newPoc.cve_id);
      formData.append('vul_name', this.newPoc.vul_name);
      formData.append('description', this.newPoc.description);
      formData.append('affected_infra', this.newPoc.affected_infra);
      formData.append('script_type', this.newPoc.script_type);
      formData.append('type', this.newPoc.type);
      if (this.fileList.length > 0) {
        formData.append('mode','upload');
        formData.append('file', this.fileList[0].raw || this.fileList[0]); // 添加文件到表单数据
      }else if(this.newcode.length>0){
        formData.append('mode','edit');
        formData.append('edit_filename',this.editFilename);
        formData.append('poc_content',this.newcode);
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
          window.location.reload();
        } else {
          this.$message.error(result.message);
        }
      } catch (error) {
        this.$message.error('An error occurred: ' + error);
      }
    },
    async submitEditPoc() {

      this.editSubmitAttempted = true;

      // 检查是否选择了有效的affected_infra
      if (!this.editAffectedInfraValid || !this.editPoc.affected_infra) {
        this.$message.error('请从列表中选择有效的基础设施');
        return;
      }

      const formData = new FormData();
      formData.append('id', this.editPoc.id);
      formData.append('cve_id', this.editPoc.cve_id);
      formData.append('vul_name', this.editPoc.vul_name);
      formData.append('type', this.editPoc.type);
      formData.append('description', this.editPoc.description);
      formData.append('script_type', this.editPoc.script_type);
      formData.append('affected_infra', this.editPoc.affected_infra);

      // 添加文件，如果有的话
      if (this.fileList.length > 0) {
        formData.append('mode','upload');
        formData.append('file', this.fileList[0]); // 这里的字段名称应与后端一致
      }else if(this.editFilename.length>0&&this.newcode.length>0){
        formData.append('mode','edit');
        formData.append('edit_filename',this.editFilename);
        formData.append('poc_content',this.newcode);
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

          // 清空变量，为下一次编辑做准备
          this.newcode = '';
          this.editFilename = '';
          this.tempnewcode = '';
          this.tempFilename = '';

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
      console.log("querySearch triggered with:", queryString);
      if (queryString.length >= 3) {
        const results = this.suggestions.filter(item =>
            item.value.toLowerCase().includes(queryString.toLowerCase())
        );
        console.log("Filtered results:", results);
        callback(results);
      } else {
        callback([]);
      }
    },
    // 新增时选择建议的处理方法
    handleSelectNew(item) {
      console.log("Selected for new POC:", item);
      // 将选中的值设置到实际存储字段
      this.newPoc.affected_infra = item.value;
      // 标记为有效
      this.affectedInfraValid = true;
    },

    // 编辑时选择建议的处理方法
    handleSelectEdit(item) {
      console.log("Selected for edit POC:", item);
      // 将选中的值设置到实际存储字段
      this.editPoc.affected_infra = item.value;
      // 标记为有效
      this.editAffectedInfraValid = true;
    },

    handleSelect(item) {
      console.log("Selected:", item);
    },
    cancelEdit(){
      // 清空变量，为下一次编辑做准备
      this.newcode = '';
      this.editFilename = '';
      this.tempnewcode = '';
      this.tempFilename = '';
      this.editDialogVisible = false;

      // 重置验证状态
      this.editAffectedInfraValid = false;
      this.editSearchAffectedInfra = '';
      this.editSubmitAttempted = false;
    }
  },

  created() {
    this.loadData();
    this.loadFile();
    this.loadVulTypes();
  }
}
</script>

<style scoped>
/*设置窗口内容自动换行*/
pre {
  white-space: pre-wrap;      /* CSS3 的换行方式，保持格式的同时允许自动换行 */
  word-wrap: break-word;      /* 较旧的浏览器也可以理解这种方式 */
  overflow-wrap: break-word;  /* 标准的换行方式 */
  overflow-y: auto;
}

code[class*="language-"],
pre[class*="language-"] {
  color: black; /* 代码文字颜色 */
  background: none; /* 背景色 */
  text-shadow: 0 1px white; /* 文字阴影 */
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



<!--<template>-->
<!--  <div>-->
<!--    <h1 id="pocmanage">POC管理</h1>-->

<!--    <div style="margin: 10px 0">-->
<!--      <el-input style="width: 200px;margin-left: 5px;margin-right: 10px" placeholder="请输入搜索关键字" suffix-icon="el-icon-search" v-model="searchKeyword"></el-input>-->
<!--      <el-button class="ml-5" type="primary" @click="load">搜索</el-button>-->
<!--      <el-button type="warning" @click="reset">重置</el-button>-->
<!--    </div>-->

<!--    <div style="margin: 10px 0">-->
<!--      <el-button style="width: 80px;margin-left: 5px" type="primary" @click="handleAdd">新增 <i class="el-icon-circle-plus-outline"></i></el-button>-->
<!--      <el-popconfirm-->
<!--          class="ml-5"-->
<!--          confirm-button-text="确定"-->
<!--          cancel-button-text="我再想想"-->
<!--          icon="el-icon-info"-->
<!--          icon-color="red"-->
<!--          title="您确定批量删除这些数据吗？"-->
<!--          @confirm="delBatch"-->
<!--      >-->
<!--        <template v-slot:reference>-->
<!--          <el-button style="width: 120px;margin: 10px" type="danger">批量删除 <i class="el-icon-remove-outline"></i></el-button>-->
<!--        </template>-->
<!--      </el-popconfirm>-->
<!--    </div>-->

<!--    <el-dialog :visible.sync="addDialogVisible" title="新增POC" width="500px" :close-on-click-modal="false">-->
<!--      <el-form :model="newPoc" ref="newPocForm">-->
<!--        <el-form-item label="CVE编号">-->
<!--          <el-input v-model="newPoc.cve_id" placeholder="CVE-xxxx-xxxx"></el-input>-->
<!--        </el-form-item>-->
<!--        <el-form-item label="漏洞名称">-->
<!--          <el-input v-model="newPoc.vul_name"></el-input>-->
<!--        </el-form-item>-->
<!--        <el-form-item label="漏洞类型">-->
<!--          <el-input v-model="newPoc.type"></el-input>-->
<!--        </el-form-item>-->
<!--        <el-form-item label="漏洞描述">-->
<!--          <el-input type="textarea" v-model="newPoc.description"></el-input>-->
<!--        </el-form-item>-->

<!--        <el-form-item label="受影响的基础设施（操作系统或软件或协议）" required>-->
<!--          <el-autocomplete-->
<!--              v-model="searchAffectedInfra"-->
<!--              :fetch-suggestions="querySearch"-->
<!--              placeholder="请输入关键字进行搜索，然后从列表中选择"-->
<!--              @select="handleSelectNew"-->
<!--              style="width: 300px;"-->
<!--          />-->
<!--          <div v-if="newPoc.affected_infra" style="margin-top: 5px; color: #67C23A;">-->
<!--            <i class="el-icon-check"></i> 已选择: {{ newPoc.affected_infra }}-->
<!--          </div>-->
<!--          <div v-if="!affectedInfraValid && submitAttempted" style="color: #F56C6C; margin-top: 5px;">-->
<!--            <i class="el-icon-warning"></i> 请从列表中选择一个有效选项-->
<!--          </div>-->
<!--        </el-form-item>-->
<!--&lt;!&ndash;        <el-form-item label="受影响的基础设施（操作系统或软件或协议）">&ndash;&gt;-->
<!--&lt;!&ndash;          <el-autocomplete&ndash;&gt;-->
<!--&lt;!&ndash;              v-model="newPoc.affected_infra"&ndash;&gt;-->
<!--&lt;!&ndash;              :fetch-suggestions="querySearch"&ndash;&gt;-->
<!--&lt;!&ndash;              placeholder="请输入内容"&ndash;&gt;-->
<!--&lt;!&ndash;              @select="handleSelect"&ndash;&gt;-->
<!--&lt;!&ndash;              style="width: 300px;"&ndash;&gt;-->
<!--&lt;!&ndash;          />&ndash;&gt;-->
<!--&lt;!&ndash;          &lt;!&ndash;          <el-input v-model="newPoc.affected_infra"></el-input>&ndash;&gt;&ndash;&gt;-->
<!--&lt;!&ndash;        </el-form-item>&ndash;&gt;-->
<!--        <el-form-item label="POC类型">-->
<!--          <el-select v-model="newPoc.script_type" placeholder="请选择">-->
<!--            <el-option label="python" value="python"></el-option>-->
<!--            <el-option label="c/c++" value="c/c++" :disabled="true"></el-option>-->
<!--            <el-option label="yaml" value="yaml" :disabled="true"></el-option>-->
<!--          </el-select>-->
<!--        </el-form-item>-->
<!--        &lt;!&ndash; POC代码 上传文件 &ndash;&gt;-->
<!--        <el-form-item label="POC代码">-->
<!--          <el-upload-->
<!--              class="upload-demo"-->
<!--              ref="upload"-->
<!--              :http-request="handleFileUpload"-->
<!--              :before-upload="beforeFileUpload"-->
<!--              :on-remove="handleRemove"-->
<!--              :file-list="fileList"-->
<!--              :limit="1">-->
<!--            <el-button>选择文件</el-button>-->
<!--          </el-upload>-->
<!--          <el-button @click="editCode" style="margin-right: 10px;margin-left: 70px;margin-top: 10px">编辑</el-button>-->
<!--          <i v-if="newcode" class="el-icon-circle-check" style="color: green;"></i>-->
<!--        </el-form-item>-->
<!--      </el-form>-->
<!--      <span slot="footer" class="dialog-footer">-->
<!--        <el-button @click="addDialogVisible = false">取消</el-button>-->
<!--        <el-button type="primary" @click="submitNewPoc">确定</el-button>-->
<!--      </span>-->

<!--      <el-dialog-->
<!--          :visible.sync="codeDialogVisible"-->
<!--          :append-to-body="true"-->
<!--          width="1200px"-->
<!--          class="custom-dialog">-->

<!--        &lt;!&ndash; 标题部分，添加内联样式 &ndash;&gt;-->
<!--        <template slot="title">-->
<!--          <div style="background-color: #f5f5f5; padding: 20px; font-weight: bold; margin: -20px -20px 0 -20px;">-->
<!--            编辑POC代码-->
<!--          </div>-->
<!--        </template>-->
<!--        <el-form>-->

<!--          &lt;!&ndash; 漏洞类型选择 &ndash;&gt;-->
<!--          <el-form-item label="漏洞类型" style="margin-bottom: 10px; font-weight: bold;">-->
<!--            <el-radio-group v-model="vulnerabilityType">-->
<!--              <el-radio :label="0">Arbitrary File Read</el-radio>-->
<!--              <el-radio :label="1">Code Execution</el-radio>-->
<!--              <el-radio :label="2">Command Execution</el-radio>-->
<!--              <el-radio :label="3">Denial Of service</el-radio>-->
<!--              <el-radio :label="4">Information Disclosure</el-radio>-->
<!--              <el-radio :label="5">Login Bypass</el-radio>-->
<!--              <el-radio :label="6">Path Traversal</el-radio>-->
<!--              <el-radio :label="7">SQL Injection</el-radio>-->
<!--              <el-radio :label="8">SSRF</el-radio>-->
<!--              <el-radio :label="9">XSS</el-radio>-->
<!--            </el-radio-group>-->
<!--          </el-form-item>-->

<!--          &lt;!&ndash; Authentication Required &ndash;&gt;-->
<!--          <el-form-item label="Authentication Required?" style="margin-bottom: 0px; font-weight: bold;">-->
<!--            <el-radio-group v-model="authRequired">-->
<!--              <el-radio :label="1">Yes</el-radio>-->
<!--              <el-radio :label="0">No</el-radio>-->
<!--            </el-radio-group>-->
<!--          </el-form-item>-->

<!--          &lt;!&ndash; Can we get result of command? &ndash;&gt;-->
<!--          <el-form-item v-if="vulnerabilityType === 1 || vulnerabilityType === 2" label="Can we get result of command?" style="margin-bottom: 10px; font-weight: bold;">-->
<!--            <el-radio-group v-model="canGetCommandResult">-->
<!--              <el-radio :label="1">Yes</el-radio>-->
<!--              <el-radio :label="0">No</el-radio>-->
<!--            </el-radio-group>-->
<!--          </el-form-item>-->

<!--          <el-button type="primary" @click="generateTemplate" style="margin-bottom: 20px;">生成模板</el-button> &lt;!&ndash; 生成模板按钮 &ndash;&gt;-->

<!--          <el-form-item label="文件名" style="margin-bottom: 0px; font-weight: bold;">-->
<!--            <el-input type="textarea" v-model="tempFilename" rows="1"></el-input> &lt;!&ndash; 临时变量 &ndash;&gt;-->
<!--          </el-form-item>-->
<!--          <div style="font-weight: bold; margin-bottom: 4px;margin-top: 8px;">代码</div> &lt;!&ndash; 标签部分 &ndash;&gt;-->
<!--          <el-form-item style="margin-bottom: 0px;">-->
<!--            <CodeEditor v-model="tempnewcode" />-->
<!--          </el-form-item>-->
<!--          &lt;!&ndash;          <el-form-item label="代码" style="margin-bottom: 0px; font-weight: bold;">&ndash;&gt;-->
<!--          &lt;!&ndash;            <el-input type="textarea" v-model="tempnewcode" rows="15"></el-input> &lt;!&ndash; 临时变量 &ndash;&gt;&ndash;&gt;-->
<!--          &lt;!&ndash;          </el-form-item>&ndash;&gt;-->
<!--        </el-form>-->
<!--        <span slot="footer" class="dialog-footer">-->
<!--          <el-button @click="clearCode">清空</el-button> &lt;!&ndash; 添加“清空”按钮 &ndash;&gt;-->
<!--          <el-button @click="codeDialogVisible = false">取消</el-button>-->
<!--          <el-button type="primary" @click="saveCode">保存</el-button>-->
<!--        </span>-->
<!--      </el-dialog>-->
<!--    </el-dialog>-->

<!--    <el-dialog :visible.sync="dialogVisible" width="60%" :height="400" title="POC代码">-->
<!--      <pre style="height: 500px; overflow-y: scroll;"><code class="language-python">{{ selectedPocCode }}</code></pre>-->
<!--    </el-dialog>-->

<!--    &lt;!&ndash;    编辑poc代码   &ndash;&gt;-->
<!--    <el-dialog :visible.sync="editDialogVisible" title="编辑POC" width="500px" :close-on-click-modal="false">-->
<!--      <el-form :model="editPoc" ref="editPocForm">-->
<!--        <el-form-item label="CVE编号">-->
<!--          <el-input v-model="editPoc.cve_id" placeholder="CVE-xxxx-xxxx"></el-input>-->
<!--        </el-form-item>-->
<!--        <el-form-item label="漏洞名称">-->
<!--          <el-input v-model="editPoc.vul_name"></el-input>-->
<!--        </el-form-item>-->
<!--        <el-form-item label="漏洞类型">-->
<!--          <el-input v-model="editPoc.type"></el-input>-->
<!--        </el-form-item>-->
<!--        <el-form-item label="漏洞描述">-->
<!--          <el-input type="textarea" v-model="editPoc.description"></el-input>-->
<!--        </el-form-item>-->

<!--        <el-form-item label="受影响的基础设施（操作系统或软件或协议）" required>-->
<!--          <el-autocomplete-->
<!--              v-model="editSearchAffectedInfra"-->
<!--              :fetch-suggestions="querySearch"-->
<!--              placeholder="请输入关键字进行搜索，然后从列表中选择"-->
<!--              @select="handleSelectEdit"-->
<!--              style="width: 300px;"-->
<!--          />-->
<!--          <div v-if="editPoc.affected_infra" style="margin-top: 5px; color: #67C23A;">-->
<!--            <i class="el-icon-check"></i> 已选择: {{ editPoc.affected_infra }}-->
<!--          </div>-->
<!--          <div v-if="!editAffectedInfraValid && editSubmitAttempted" style="color: #F56C6C; margin-top: 5px;">-->
<!--            <i class="el-icon-warning"></i> 请从列表中选择一个有效选项-->
<!--          </div>-->
<!--        </el-form-item>-->
<!--&lt;!&ndash;        <el-form-item label="受影响的基础设施（操作系统或软件或协议）">&ndash;&gt;-->
<!--&lt;!&ndash;          <el-autocomplete&ndash;&gt;-->
<!--&lt;!&ndash;              v-model="editPoc.affected_infra"&ndash;&gt;-->
<!--&lt;!&ndash;              :fetch-suggestions="querySearch"&ndash;&gt;-->
<!--&lt;!&ndash;              placeholder="请输入内容"&ndash;&gt;-->
<!--&lt;!&ndash;              @select="handleSelect"&ndash;&gt;-->
<!--&lt;!&ndash;              style="width: 300px;"&ndash;&gt;-->
<!--&lt;!&ndash;          />&ndash;&gt;-->
<!--&lt;!&ndash;          &lt;!&ndash;          <el-input v-model="editPoc.affected_infra"></el-input>&ndash;&gt;&ndash;&gt;-->
<!--&lt;!&ndash;        </el-form-item>&ndash;&gt;-->
<!--        <el-form-item label="POC类型">-->
<!--          <el-select v-model="editPoc.script_type" placeholder="请选择">-->
<!--            <el-option label="python" value="python"></el-option>-->
<!--            <el-option label="c/c++" value="c/c++"></el-option>-->
<!--            <el-option label="yaml" value="yaml"></el-option>-->
<!--          </el-select>-->
<!--        </el-form-item>-->
<!--        <el-form-item label="POC代码">-->
<!--          <el-upload-->
<!--              class="upload-demo"-->
<!--              ref="upload"-->
<!--              :http-request="handleFileUpload"-->
<!--              :before-upload="beforeFileUpload"-->
<!--              :on-remove="handleRemove"-->
<!--              :file-list="fileList"-->
<!--              :limit="1"-->
<!--              accept=".py">-->
<!--            <el-button>选择文件</el-button>-->
<!--            &lt;!&ndash;            <span slot="tip" class="el-upload__tip">只能上传.py文件</span>&ndash;&gt;-->
<!--          </el-upload>-->
<!--          <el-button @click="editPocCode" style="margin-top: 10px;margin-left: 69px">编辑poc代码</el-button>-->
<!--          <i v-if="newcode" class="el-icon-circle-check" style="color: green;"></i>-->
<!--        </el-form-item>-->
<!--      </el-form>-->
<!--      <span slot="footer" class="dialog-footer">-->
<!--&lt;!&ndash;        <el-button @click="editDialogVisible = false">取消</el-button>&ndash;&gt;-->
<!--        <el-button @click="cancelEdit">取消</el-button>-->
<!--        <el-button type="primary" @click="submitEditPoc">确定</el-button>-->
<!--      </span>-->

<!--      &lt;!&ndash;      编辑poc-编辑poc代码       &ndash;&gt;-->
<!--      <el-dialog-->
<!--          :visible.sync="editPocCodeDialogVisible"-->
<!--          :append-to-body="true"-->
<!--          width="1000px"-->
<!--          class="custom-dialog">-->

<!--        &lt;!&ndash; 标题部分，添加内联样式 &ndash;&gt;-->
<!--        <template slot="title">-->
<!--          <div style="background-color: #f5f5f5; padding: 20px; font-weight: bold; margin: -20px -20px 0 -20px;">-->
<!--            编辑POC代码-->
<!--          </div>-->
<!--        </template>-->
<!--        <el-form>-->

<!--          <el-form-item label="文件名" style="margin-bottom: 0px; font-weight: bold;">-->
<!--            <el-input type="textarea" v-model="tempFilename" rows="1"></el-input> &lt;!&ndash; 临时变量 &ndash;&gt;-->
<!--          </el-form-item>-->
<!--          <div style="font-weight: bold; margin-bottom: 4px;margin-top: 8px;">代码</div> &lt;!&ndash; 标签部分 &ndash;&gt;-->
<!--          <el-form-item style="margin-bottom: 0px;">-->
<!--            <CodeEditor v-model="tempnewcode" />-->
<!--          </el-form-item>-->
<!--          &lt;!&ndash;          <el-form-item label="代码" style="margin-bottom: 0px; font-weight: bold;">&ndash;&gt;-->
<!--          &lt;!&ndash;            <CodeEditor v-model="tempnewcode"/>&ndash;&gt;-->
<!--          &lt;!&ndash;&lt;!&ndash;            <el-input type="textarea" v-model="tempnewcode" rows="15"></el-input> &lt;!&ndash; 临时变量 &ndash;&gt;&ndash;&gt;&ndash;&gt;-->
<!--          &lt;!&ndash;          </el-form-item>&ndash;&gt;-->
<!--        </el-form>-->
<!--        <span slot="footer" class="dialog-footer">-->
<!--          <el-button @click="clearCode">清空</el-button> &lt;!&ndash; 添加“清空”按钮 &ndash;&gt;-->
<!--          <el-button @click="editPocCodeDialogVisible = false">取消</el-button>-->
<!--          <el-button type="primary" @click="saveCode2">保存</el-button>-->
<!--        </span>-->
<!--      </el-dialog>-->
<!--    </el-dialog>-->



<!--    <el-table :data="paginatedData" style="width: 100%" ref="table">-->
<!--      <el-table-column type="selection" width="55"></el-table-column>-->
<!--      <el-table-column prop="id" label="ID" width="50"></el-table-column>-->
<!--      <el-table-column prop="cve_id" label="CVE编号" width="170"></el-table-column>-->
<!--      <el-table-column prop="vul_name" label="漏洞名称" width="130"></el-table-column>-->
<!--      <el-table-column prop="type" label="漏洞类型" width="110"></el-table-column>-->
<!--      <el-table-column prop="affected_infra" label="漏洞影响的范围" width="130"></el-table-column>-->
<!--      <el-table-column prop="description" label="漏洞描述" width="250">-->
<!--        <template slot-scope="scope">-->
<!--                    <span v-if="!scope.row.showFullDescription">-->
<!--                        {{ scope.row.description.slice(0, 40) }}...-->
<!--                        <el-button type="text" @click="toggleDescription(scope.row)">展开</el-button>-->
<!--                    </span>-->
<!--          <span v-else>-->
<!--                        {{ scope.row.description }}-->
<!--                        <el-button type="text" @click="toggleDescription(scope.row)">收起</el-button>-->
<!--                    </span>-->
<!--        </template>-->
<!--      </el-table-column>-->
<!--      <el-table-column prop="script_type" label="POC类型" width="85"></el-table-column>-->

<!--      <el-table-column prop="script" label="POC代码" width="100">-->
<!--        <template slot-scope="scope">-->
<!--          <el-button type="success" @click="handleLook(scope.row)">查看</el-button>-->
<!--        </template>-->
<!--      </el-table-column>-->
<!--      <el-table-column prop="timestamp" label="修改时间" width="160"></el-table-column>-->
<!--      <el-table-column label="操作" align="center">-->
<!--        <template slot-scope="scope">-->
<!--          <el-button type="success" style="width: 80px;margin-left: 5px" @click="handleEdit(scope.row)">编辑 <i class="el-icon-edit"></i></el-button>-->
<!--          <el-popconfirm-->
<!--              title="您确定要删除这条数据吗？"-->
<!--              @confirm="del(scope.row.id)"-->
<!--          >-->
<!--            <template v-slot:reference>-->
<!--              <el-button type="danger" style="width: 80px;margin-left: 5px">删除 <i class="el-icon-delete"></i></el-button>-->
<!--            </template>-->
<!--          </el-popconfirm>-->

<!--        </template>-->
<!--      </el-table-column>-->
<!--    </el-table>-->
<!--    <el-pagination-->
<!--        @size-change="handleSizeChange"-->
<!--        @current-change="handleCurrentChange"-->
<!--        :current-page="currentPage"-->
<!--        :page-size="pageSize"-->
<!--        :total="totalItems"-->
<!--        layout="total, sizes, prev, pager, next, jumper">-->
<!--    </el-pagination>-->
<!--  </div>-->
<!--</template>-->

<!--<script>-->
<!--import Prism from 'prismjs';-->
<!--import 'prismjs/themes/prism.css';  // 或者选择你喜欢的主题-->
<!--import axios from 'axios';-->
<!--import CodeEditor from '@/components/CodeEditor.vue'; // 引入 CodeEditor 组件-->

<!--export default {-->
<!--  name: "pocManage",-->
<!--  components: {-->
<!--    CodeEditor,-->
<!--  },-->
<!--  data(){-->
<!--    return{-->
<!--      addDialogVisible: false,-->
<!--      codeDialogVisible: false,-->
<!--      newPoc: {-->
<!--        type: '',-->
<!--        cve_id: '',-->
<!--        vul_name: '',-->
<!--        description: '',-->
<!--        script_type: '',-->
<!--        affected_infra: '',-->
<!--        //script: ''-->
<!--      },-->
<!--      // 搜索时使用的输入值（不会被提交）-->
<!--      searchAffectedInfra: '',-->

<!--      //用来编辑poc-->
<!--      editPoc: {-->
<!--        id: '',-->
<!--        cve_id: '',-->
<!--        vul_name: '',-->
<!--        type: '',-->
<!--        description: '',-->
<!--        affected_infra: '',-->
<!--        script_type: '',-->
<!--        script: '',-->
<!--      },-->

<!--      // 搜索时使用的输入值（不会被提交）-->
<!--      editSearchAffectedInfra: '',-->

<!--      // 验证标记-->
<!--      affectedInfraValid: false,-->
<!--      editAffectedInfraValid: false,-->

<!--      editDialogVisible: false,-->
<!--      codeEditDialogVisible: false,-->
<!--      editPocCodeDialogVisible:false,-->
<!--      tempCode: '', // 临时存储代码输入-->
<!--      //用来是实现搜索-->
<!--      searchKeyword: '',-->
<!--      showFullDescription: {},-->
<!--      dialogVisible: false,-->
<!--      selectedPocCode: '',-->
<!--      currentPage: 1,-->
<!--      pageSize: 10,-->
<!--      totalItems: 0,-->
<!--      pocs:[],-->
<!--      fileList: [],-->
<!--      tempFilename: '',  // 临时文件名变量-->
<!--      tempnewcode: '',      // 临时代码内容变量-->
<!--      newcode: '', // 存储POC代码-->
<!--      editFilename: '',-->
<!--      vulnerabilityType: 0, // 漏洞类型-->
<!--      authRequired: 1, // 身份验证，默认是Yes-->
<!--      canGetCommandResult: 1, // 命令执行结果，默认是Yes-->
<!--      suggestions: [], // 将文件内容读取后填充到此数组，格式为 { value: "文本" }-->
<!--      // codeMirrorOptions: {-->
<!--      //   mode: 'python',      // 设置为 Python 模式-->
<!--      //   theme: 'material',   // 设置编辑器的主题-->
<!--      //   lineNumbers: true,   // 显示行号-->
<!--      //   tabSize: 4,          // 缩进为 4 个空格-->
<!--      //   indentUnit: 4,       // 缩进单位-->
<!--      //   indentWithTabs: true,-->
<!--      //   lineWrapping: true,  // 自动换行-->
<!--      // },-->
<!--    };-->
<!--  },-->
<!--  watch: {-->
<!--    codeDialogVisible(newVal) {-->
<!--      if (newVal) { // 当对话框变为可见时-->
<!--        // 当对话框打开时，将实际变量的值赋给临时变量-->
<!--        this.tempFilename = this.editFilename;-->
<!--        this.tempnewcode = this.newcode;-->
<!--        this.$nextTick(() => {-->
<!--          this.$refs.codeInput.focus(); // 聚焦到输入框-->
<!--        });-->
<!--      }-->
<!--    },-->
<!--    editPocCodeDialogVisible(newVal) {-->
<!--      if (newVal) { // 当对话框变为可见时-->
<!--        // 当对话框打开时，将实际变量的值赋给临时变量-->
<!--        // this.tempFilename = this.tempCode;-->
<!--        // this.tempnewcode = this.selectedPocCode;-->
<!--        // 修改：优先使用newcode，如果newcode为空则使用selectedPocCode-->
<!--        this.tempFilename = this.editFilename || this.tempCode; // 优先使用已保存的文件名-->
<!--        this.tempnewcode = this.newcode || this.selectedPocCode; // 优先使用已保存的代码-->
<!--        this.$nextTick(() => {-->
<!--          this.$refs.codeInput.focus(); // 聚焦到输入框-->
<!--        });-->
<!--      }-->
<!--    },-->
<!--    watch: {-->
<!--      dialogVisible(newVal) {-->
<!--        if (!newVal) {-->
<!--          this.selectedPocCode = ''; // 当对话框关闭时清空代码-->
<!--        } else {-->
<!--          this.$nextTick(() => {-->
<!--            Prism.highlightAll();  // 应用 Prism 高亮-->
<!--          });-->
<!--        }-->
<!--      }-->
<!--    }-->

<!--  },-->
<!--  computed: {-->
<!--    paginatedData() {-->
<!--      const start = (this.currentPage - 1) * this.pageSize;-->
<!--      const end = start + this.pageSize;-->
<!--      return this.pocs.slice(start, end);-->
<!--    }-->
<!--  },-->
<!--  methods:{-->
<!--    //搜索的实现-->
<!--    load() {-->
<!--      // let keyword = encodeURIComponent(this.searchKeyword.trim());-->
<!--      // let query = new URLSearchParams({ keyword }).toString();-->
<!--      let query = new URLSearchParams({ keyword: this.searchKeyword.trim() }).toString();-->
<!--      fetch(`/api/searchData?${query}`)-->
<!--          .then(response => {-->
<!--            if (!response.ok) {-->
<!--              throw new Error('Network response was not ok');-->
<!--            }-->
<!--            return response.json();-->
<!--          })-->
<!--          .then(data => {-->
<!--            this.pocs = data.map(poc => ({-->
<!--              ...poc,-->
<!--              showFullDescription: false-->
<!--            }));-->
<!--            this.totalItems = this.pocs.length;-->
<!--          })-->
<!--          .catch(error => {-->
<!--            console.error('Error fetching data:', error);-->
<!--          });-->
<!--    },-->

<!--    reset() {-->
<!--      this.searchKeyword = ''; // 清空搜索关键字-->
<!--      this.loadData(); // 重新加载所有数据-->
<!--    },-->

<!--    toggleDescription(poc) {-->
<!--      poc.showFullDescription = !poc.showFullDescription;-->
<!--    },-->

<!--    handleLook(row) {-->
<!--      // 发送请求获取POC内容-->
<!--      axios.get('/api/getPOCContent', {-->
<!--        params: {-->
<!--          id: row.id-->
<!--        }-->
<!--      })-->
<!--          .then(response => {-->
<!--            if (response.status === 200) {-->
<!--              this.selectedPocCode = response.data.content;-->
<!--              this.$nextTick(() => {-->
<!--                this.dialogVisible = true;-->
<!--              });-->
<!--            } else {-->
<!--              // 处理非200响应状态码-->
<!--              console.error('Failed to fetch POC content:', response.status, response.statusText);-->
<!--              // this.$message.error('操作失败: ' + response.data.error);-->
<!--            }-->
<!--          })-->
<!--          .catch(error => {-->
<!--            if (error.response && error.response.status === 500) {-->
<!--              // 处理500错误状态码-->
<!--              this.$message.error(error.response.data.error);-->
<!--            } else {-->
<!--              // 处理其他错误-->
<!--              console.error('Error fetching POC content:', error);-->
<!--              this.$message.error('操作失败: ' + error);-->
<!--            }-->
<!--          });-->
<!--    },-->

<!--    handleSizeChange(newSize) {-->
<!--      this.pageSize = newSize;-->
<!--      this.loadData();-->
<!--    },-->
<!--    handleCurrentChange(newPage) {-->
<!--      this.currentPage = newPage;-->
<!--      this.loadData();-->
<!--    },-->
<!--    loadData() {-->
<!--      fetch('/api/getAllData')-->
<!--          .then(response => {-->
<!--            if (!response.ok) {-->
<!--              throw new Error('Network response was not ok');-->
<!--            }-->
<!--            return response.json();-->
<!--          })-->
<!--          .then(data => {-->
<!--            this.pocs = data.map(poc => ({-->
<!--              id: poc.id,-->
<!--              cve_id: poc.vuln_id,-->
<!--              affected_infra: poc.affected_infra,-->
<!--              type: poc.type,-->
<!--              vul_name: poc.vul_name,-->
<!--              description: poc.description,-->
<!--              script_type: poc.script_type,-->
<!--              script: poc.script,-->
<!--              timestamp: poc.timestamp,-->
<!--              showFullDescription: false  // 保持这个字段，用于控制描述的展开/收起-->
<!--            }));-->
<!--            this.totalItems = this.pocs.length;-->
<!--          })-->
<!--          .catch(error => {-->
<!--            console.error('Error fetching data:', error);-->
<!--          });-->
<!--    },-->
<!--    handleAdd() {-->
<!--      this.addDialogVisible = true;-->
<!--      this.submitAttempted = false;-->
<!--      this.affectedInfraValid = false;-->
<!--      this.searchAffectedInfra = '';-->
<!--      this.newPoc = {-->
<!--        type: '',-->
<!--        cve_id: '',-->
<!--        vul_name: '',-->
<!--        description: '',-->
<!--        script_type: '',-->
<!--        affected_infra: '',-->
<!--        // 其他属性的重置...-->
<!--      };-->
<!--    },-->

<!--    //编辑poc-->
<!--    handleEdit(row) {-->
<!--      this.editPoc = { ...row }; // 复制行数据到编辑数据对象-->
<!--      this.tempCode = row.script; // Set the temporary code to the existing script-->
<!--      // 如果有affected_infra，则初始化为有效-->
<!--      if (row.affected_infra && this.suggestions.some(item => item.value === row.affected_infra)) {-->
<!--        this.editAffectedInfraValid = true;-->
<!--        this.editSearchAffectedInfra = row.affected_infra; // 显示已有的值-->
<!--      } else {-->
<!--        this.editAffectedInfraValid = false;-->
<!--        this.editSearchAffectedInfra = '';-->
<!--        this.editPoc.affected_infra = '';-->
<!--      }-->

<!--      this.editSubmitAttempted = false;-->

<!--      axios.get('/api/getPOCContent', {-->
<!--        params: {-->
<!--          id: row.id-->
<!--        }-->
<!--      })-->
<!--          .then(response => {-->
<!--            this.selectedPocCode = response.data.content;-->
<!--          })-->
<!--      this.editDialogVisible=true;-->
<!--    },-->

<!--    del(id) {-->
<!--      fetch(`/api/deleteDataById`, {-->
<!--        method: 'DELETE',-->
<!--        headers: {-->
<!--          'Content-Type': 'application/json',-->
<!--        },-->
<!--        body: JSON.stringify({ ids: id })-->
<!--      })-->
<!--          .then(response => {-->
<!--            if (response.ok) {-->
<!--              this.$message.success('删除成功！');-->
<!--              this.loadData();  // 重新加载数据-->
<!--            } else {-->
<!--              this.$message.error('删除失败！');-->
<!--            }-->
<!--          })-->
<!--          .catch(error => {-->
<!--            console.error('删除操作失败:', error);-->
<!--            this.$message.error('删除操作失败: ' + error.message);-->
<!--          });-->
<!--    },-->

<!--    delBatch() {-->
<!--      const idsToDelete = this.$refs.table.selection.map(row => row.id);-->
<!--      fetch(`/api/deleteDataById`, {-->
<!--        method: 'DELETE',-->
<!--        headers: {-->
<!--          'Content-Type': 'application/json',-->
<!--        },-->
<!--        body: JSON.stringify({ ids: idsToDelete })-->
<!--      })-->
<!--          .then(response => {-->
<!--            if (response.ok) {-->
<!--              this.$message.success('批量删除成功！');-->
<!--              this.loadData();  // 重新加载数据-->
<!--            } else {-->
<!--              this.$message.error('批量删除失败！');-->
<!--            }-->
<!--          })-->
<!--          .catch(error => {-->
<!--            console.error('批量删除操作失败:', error);-->
<!--            this.$message.error('批量删除操作失败: ' + error.message);-->
<!--          });-->
<!--    },-->

<!--    beforeFileUpload(file) {-->
<!--      const isPython = file.type === 'application/x-python-code' || file.name.endsWith('.py');-->
<!--      if (!isPython) {-->
<!--        this.$message.error('只能上传Python文件');-->
<!--        return false;-->
<!--      }-->

<!--      // 创建一个 Promise 来读取文件内容-->
<!--      // 创建一个 Promise 来读取文件内容-->
<!--      return new Promise((resolve, reject) => {-->
<!--        const reader = new FileReader();-->
<!--        reader.onload = (event) => {-->
<!--          const content = event.target.result;-->

<!--          // 定义需要包含的内容的正则表达式或简单字符串-->

<!--          const requiredPatterns = [-->
<!--            /class\s+DemoPOC:/,             // 检查是否有 class DemoPOC:-->
<!--            /def\s+_verify\s*\(self\)/,     // 检查是否有 def _verify(self)-->
<!--            /result\[['"]VerifyInfo['"]\]/, // 检查是否有 result['VerifyInfo'] 或 result["VerifyInfo"]-->
<!--            /\[!\]/,                       // 检查是否有 [!]-->
<!--            /\[SAFE\]/                     // 检查是否有 [SAFE]-->
<!--          ];-->

<!--          // 检查两种初始化方法中的任意一个-->
<!--          const initPatterns = [-->
<!--            /def\s+__init__\s*\(self,\s*url,\s*ip,\s*port\)/, // 检查是否有 def __init__(self, url, ip, port)-->
<!--            /def\s+__init__\s*\(self,\s*url,\s*ip,\s*port,\s*server_ip,\s*server_port\)/ // 检查是否有 def __init__(self, url, ip, port, server_ip, server_port)-->
<!--          ];-->

<!--          // 检查必要内容是否满足要求-->
<!--          const isValidRequiredPatterns = requiredPatterns.every((pattern) => pattern.test(content));-->
<!--          // 检查两种初始化方法中是否有一个满足要求-->
<!--          const isValidInitPattern = initPatterns.some((pattern) => pattern.test(content));-->

<!--          if (!isValidRequiredPatterns || !isValidInitPattern) {-->
<!--            this.$message.error('poc格式不规范');-->
<!--            reject(false);-->
<!--          } else {-->
<!--            resolve(true);-->
<!--          }-->
<!--        };-->

<!--        reader.onerror = () => {-->
<!--          this.$message.error('文件读取失败');-->
<!--          reject(false);-->
<!--        };-->

<!--        // 读取文件内容为文本-->
<!--        reader.readAsText(file);-->
<!--      });-->
<!--      // return new Promise((resolve, reject) => {-->
<!--      //   const reader = new FileReader();-->
<!--      //   reader.onload = (event) => {-->
<!--      //     const content = event.target.result;-->
<!--      //-->
<!--      //     // 定义需要包含的内容的正则表达式或简单字符串-->
<!--      //-->
<!--      //     const requiredPatterns = [-->
<!--      //       /class\s+DemoPOC:/,             // 检查是否有 class DemoPOC:-->
<!--      //       /def\s+__init__\s*\(self,\s*url,\s*ip,\s*port\)/, // 检查是否有 def __init__(self, url, ip, port)-->
<!--      //       /def\s+_verify\s*\(self\)/,     // 检查是否有 def _verify(self)-->
<!--      //       /result\[['"]VerifyInfo['"]\]/, // 检查是否有 result['VerifyInfo'] 或 result["VerifyInfo"]-->
<!--      //       /\[!\]/,                       // 检查是否有 [!]-->
<!--      //       /\[SAFE\]/                     // 检查是否有 [SAFE]-->
<!--      //     ];-->
<!--      //-->
<!--      //     // 检查内容是否满足要求-->
<!--      //     const isValid = requiredPatterns.every((pattern) => pattern.test(content));-->
<!--      //     if (!isValid) {-->
<!--      //       this.$message.error('poc格式不规范');-->
<!--      //       reject(false);-->
<!--      //     } else {-->
<!--      //       resolve(true);-->
<!--      //     }-->
<!--      //   };-->
<!--      //-->
<!--      //   reader.onerror = () => {-->
<!--      //     this.$message.error('文件读取失败');-->
<!--      //     reject(false);-->
<!--      //   };-->
<!--      //-->
<!--      //   // 读取文件内容为文本-->
<!--      //   reader.readAsText(file);-->
<!--      // });-->
<!--    },-->

<!--    handleFileUpload(param) {-->
<!--      if (param.file) {-->
<!--        this.fileList = [param.file];-->
<!--      }-->
<!--    },-->
<!--    handleRemove() {-->
<!--      this.fileList = [];-->
<!--    },-->

<!--    // 触发编辑代码窗口(新增poc部分）-->
<!--    editCode() {-->
<!--      this.codeDialogVisible = true;-->
<!--    },-->

<!--    //触发编辑代码窗口(修改poc部分）-->
<!--    editPocCode() {-->
<!--      this.editPocCodeDialogVisible = true;-->
<!--    },-->
<!--    // 保存代码-->
<!--    saveCode() {-->
<!--      // 检查文件名是否以 .py 结尾-->
<!--      if (!this.tempFilename.endsWith('.py')) {-->
<!--        this.$message.error('文件名错误，必须以 .py 结尾');-->
<!--        return;  // 停止保存流程-->
<!--      }-->

<!--      // 正则表达式数组（多行模式，处理空格和换行）-->
<!--      const requiredFields = [-->
<!--        { regex: /class\s+DemoPOC\s*:/m, label: 'class DemoPOC' },  // 类定义-->
<!--        { regex: /def\s+_verify\s*\(self\)/m, label: 'def _verify(self)' },  // _verify 方法-->
<!--        { regex: /result\['VerifyInfo'\]/m, label: "result['VerifyInfo']" },  // result['VerifyInfo']-->
<!--        { regex: /\[!\]/m, label: '[!]' },  // [!]-->
<!--        { regex: /\[SAFE\]/m, label: '[SAFE]' }  // [SAFE]-->
<!--      ];-->

<!--      // 初始化方法的两种可能模式-->
<!--      const initMethods = [-->
<!--        { regex: /def\s+__init__\s*\(self,\s*url,\s*ip,\s*port\)/m, label: 'def __init__(self,url,ip,port)' },-->
<!--        { regex: /def\s+__init__\s*\(self,\s*url,\s*ip,\s*port,\s*server_ip,\s*server_port\)/m, label: 'def __init__(self,url,ip,port,server_ip,server_port)' }-->
<!--      ];-->

<!--      // 检查每个必须字段是否匹配代码-->
<!--      let allFieldsPresent = true;-->
<!--      requiredFields.forEach(field => {-->
<!--        const isMatch = field.regex.test(this.tempnewcode);-->
<!--        console.log(`Checking field: ${field.label}, Match: ${isMatch}`);  // 调试输出-->
<!--        if (!isMatch) {-->
<!--          this.$message.error(`代码中缺少必要的字段：${field.label}`);-->
<!--          allFieldsPresent = false;  // 如果任意字段未匹配，标记为 false-->
<!--        }-->
<!--      });-->

<!--      // 检查初始化方法是否匹配其中一种模式-->
<!--      const initMethodMatch = initMethods.some(method => method.regex.test(this.tempnewcode));-->
<!--      console.log(`Checking init methods. Match: ${initMethodMatch}`);  // 调试输出-->
<!--      if (!initMethodMatch) {-->
<!--        this.$message.error(`代码中缺少必要的初始化方法，需要包含以下两种之一：-->
<!--    - def __init__(self,url,ip,port)-->
<!--    - def __init__(self,url,ip,port,server_ip,server_port)`);-->
<!--        allFieldsPresent = false;-->
<!--      }-->

<!--      if (!allFieldsPresent) {-->
<!--        return;  // 停止保存流程-->
<!--      }-->

<!--      // 如果检查都通过，保存临时变量到实际变量中-->
<!--      this.editFilename = this.tempFilename;  // 将临时文件名赋值给实际文件名变量-->
<!--      this.newcode = this.tempnewcode;        // 将临时代码赋值给实际代码变量-->
<!--      this.codeDialogVisible = false;         // 关闭对话框-->
<!--    },-->
<!--    // saveCode() {-->
<!--    //   // 检查文件名是否以 .py 结尾-->
<!--    //   if (!this.tempFilename.endsWith('.py')) {-->
<!--    //     this.$message.error('文件名错误，必须以 .py 结尾');-->
<!--    //     return;  // 停止保存流程-->
<!--    //   }-->
<!--    //-->
<!--    //   // 正则表达式数组（多行模式，处理空格和换行）-->
<!--    //   const requiredFields = [-->
<!--    //     { regex: /class\s+DemoPOC\s*:/m, label: 'class DemoPOC' },  // 类定义-->
<!--    //     { regex: /def\s+__init__\s*\(self,\s*url,\s*ip,\s*port\)/m, label: 'def __init__(self,url,ip,port)' },  // 构造函数-->
<!--    //     { regex: /def\s+_verify\s*\(self\)/m, label: 'def _verify(self)' },  // _verify 方法-->
<!--    //     { regex: /result\['VerifyInfo'\]/m, label: "result['VerifyInfo']" },  // result['VerifyInfo']-->
<!--    //     { regex: /\[!\]/m, label: '[!]' },  // [!]-->
<!--    //     { regex: /\[SAFE\]/m, label: '[SAFE]' }  // [SAFE]-->
<!--    //   ];-->
<!--    //-->
<!--    //   // 检查每个正则表达式是否匹配代码-->
<!--    //   let allFieldsPresent = true;-->
<!--    //   requiredFields.forEach(field => {-->
<!--    //     const isMatch = field.regex.test(this.tempnewcode);-->
<!--    //     console.log(`Checking field: ${field.label}, Match: ${isMatch}`);  // 调试输出-->
<!--    //     if (!isMatch) {-->
<!--    //       this.$message.error(`代码中缺少必要的字段：${field.label}`);-->
<!--    //       allFieldsPresent = false;  // 如果任意字段未匹配，标记为 false-->
<!--    //     }-->
<!--    //   });-->
<!--    //-->
<!--    //   if (!allFieldsPresent) {-->
<!--    //     return;  // 停止保存流程-->
<!--    //   }-->
<!--    //-->
<!--    //   // 如果检查都通过，保存临时变量到实际变量中-->
<!--    //   this.editFilename = this.tempFilename;  // 将临时文件名赋值给实际文件名变量-->
<!--    //   this.newcode = this.tempnewcode;           // 将临时代码赋值给实际代码变量-->
<!--    //   this.codeDialogVisible = false;         // 关闭对话框-->
<!--    // },-->

<!--    // 编辑poc的保存代码-->
<!--    saveCode2() {-->
<!--      // 检查文件名是否以 .py 结尾-->
<!--      if (!this.tempFilename.endsWith('.py')) {-->
<!--        this.$message.error('文件名错误，必须以 .py 结尾');-->
<!--        return;  // 停止保存流程-->
<!--      }-->

<!--      // 正则表达式数组（多行模式，处理空格和换行）-->
<!--      const requiredFields = [-->
<!--        { regex: /class\s+DemoPOC\s*:/m, label: 'class DemoPOC' },  // 类定义-->
<!--        { regex: /def\s+_verify\s*\(self\)/m, label: 'def _verify(self)' },  // _verify 方法-->
<!--        { regex: /result\['VerifyInfo'\]/m, label: "result['VerifyInfo']" },  // result['VerifyInfo']-->
<!--        { regex: /\[!\]/m, label: '[!]' },  // [!]-->
<!--        { regex: /\[SAFE\]/m, label: '[SAFE]' }  // [SAFE]-->
<!--      ];-->

<!--      // 初始化方法的两种可能模式-->
<!--      const initMethods = [-->
<!--        { regex: /def\s+__init__\s*\(self,\s*url,\s*ip,\s*port\)/m, label: 'def __init__(self,url,ip,port)' },-->
<!--        { regex: /def\s+__init__\s*\(self,\s*url,\s*ip,\s*port,\s*server_ip,\s*server_port\)/m, label: 'def __init__(self,url,ip,port,server_ip,server_port)' }-->
<!--      ];-->

<!--      // 检查每个必须字段是否匹配代码-->
<!--      let allFieldsPresent = true;-->
<!--      requiredFields.forEach(field => {-->
<!--        const isMatch = field.regex.test(this.tempnewcode);-->
<!--        console.log(`Checking field: ${field.label}, Match: ${isMatch}`);  // 调试输出-->
<!--        if (!isMatch) {-->
<!--          this.$message.error(`代码中缺少必要的字段：${field.label}`);-->
<!--          allFieldsPresent = false;  // 如果任意字段未匹配，标记为 false-->
<!--        }-->
<!--      });-->

<!--      // 检查初始化方法是否匹配其中一种模式-->
<!--      const initMethodMatch = initMethods.some(method => method.regex.test(this.tempnewcode));-->
<!--      console.log(`Checking init methods. Match: ${initMethodMatch}`);  // 调试输出-->
<!--      if (!initMethodMatch) {-->
<!--        this.$message.error(`代码中缺少必要的初始化方法，需要包含以下两种之一：-->
<!--    - def __init__(self,url,ip,port)或-->
<!--    - def __init__(self,url,ip,port,server_ip,server_port)`);-->
<!--        allFieldsPresent = false;-->
<!--      }-->

<!--      if (!allFieldsPresent) {-->
<!--        return;  // 停止保存流程-->
<!--      }-->

<!--      // 如果检查都通过，保存临时变量到实际变量中-->
<!--      this.editFilename = this.tempFilename;  // 将临时文件名赋值给实际文件名变量-->
<!--      this.newcode = this.tempnewcode;        // 将临时代码赋值给实际代码变量-->
<!--      this.editPocCodeDialogVisible = false;  // 关闭对话框-->
<!--    },-->
<!--    //以下只验证了一种初始化方法-->
<!--    // saveCode2() {-->
<!--    //   // 检查文件名是否以 .py 结尾-->
<!--    //   if (!this.tempFilename.endsWith('.py')) {-->
<!--    //     this.$message.error('文件名错误，必须以 .py 结尾');-->
<!--    //     return;  // 停止保存流程-->
<!--    //   }-->
<!--    //-->
<!--    //   // 正则表达式数组（多行模式，处理空格和换行）-->
<!--    //   const requiredFields = [-->
<!--    //     { regex: /class\s+DemoPOC\s*:/m, label: 'class DemoPOC' },  // 类定义-->
<!--    //     { regex: /def\s+__init__\s*\(self,\s*url,\s*ip,\s*port\)/m, label: 'def __init__(self,url,ip,port)' },  // 构造函数-->
<!--    //     { regex: /def\s+_verify\s*\(self\)/m, label: 'def _verify(self)' },  // _verify 方法-->
<!--    //     { regex: /result\['VerifyInfo'\]/m, label: "result['VerifyInfo']" },  // result['VerifyInfo']-->
<!--    //     { regex: /\[!\]/m, label: '[!]' },  // [!]-->
<!--    //     { regex: /\[SAFE\]/m, label: '[SAFE]' }  // [SAFE]-->
<!--    //   ];-->
<!--    //-->
<!--    //   // 检查每个正则表达式是否匹配代码-->
<!--    //   let allFieldsPresent = true;-->
<!--    //   requiredFields.forEach(field => {-->
<!--    //     const isMatch = field.regex.test(this.tempnewcode);-->
<!--    //     console.log(`Checking field: ${field.label}, Match: ${isMatch}`);  // 调试输出-->
<!--    //     if (!isMatch) {-->
<!--    //       this.$message.error(`代码中缺少必要的字段：${field.label}`);-->
<!--    //       allFieldsPresent = false;  // 如果任意字段未匹配，标记为 false-->
<!--    //     }-->
<!--    //   });-->
<!--    //-->
<!--    //   if (!allFieldsPresent) {-->
<!--    //     return;  // 停止保存流程-->
<!--    //   }-->
<!--    //-->
<!--    //   // 如果检查都通过，保存临时变量到实际变量中-->
<!--    //   this.editFilename = this.tempFilename;  // 将临时文件名赋值给实际文件名变量-->
<!--    //   this.newcode = this.tempnewcode;           // 将临时代码赋值给实际代码变量-->
<!--    //   this.editPocCodeDialogVisible = false;         // 关闭对话框-->
<!--    // },-->

<!--    // 清空代码并关闭窗口-->
<!--    clearCode() {-->
<!--      this.newcode = ''; // 清空newcode-->
<!--      this.codeDialogVisible = false; // 关闭窗口-->
<!--    },-->
<!--    clearCode2() {-->
<!--      this.newcode = ''; // 清空newcode-->
<!--      this.editPocCodeDialogVisible = false; // 关闭窗口-->
<!--    },-->
<!--    async submitNewPoc() {-->
<!--      this.submitAttempted = true;-->

<!--      // 检查是否选择了有效的affected_infra-->
<!--      if (!this.affectedInfraValid || !this.newPoc.affected_infra) {-->
<!--        this.$message.error('请从列表中选择有效的基础设施');-->
<!--        return;-->
<!--      }-->

<!--      const formData = new FormData();-->
<!--      formData.append('cve_id', this.newPoc.cve_id);-->
<!--      formData.append('vul_name', this.newPoc.vul_name);-->
<!--      formData.append('description', this.newPoc.description);-->
<!--      formData.append('affected_infra', this.newPoc.affected_infra);-->
<!--      formData.append('script_type', this.newPoc.script_type);-->
<!--      formData.append('type', this.newPoc.type);-->
<!--      if (this.fileList.length > 0) {-->
<!--        formData.append('mode','upload');-->
<!--        formData.append('file', this.fileList[0].raw || this.fileList[0]); // 添加文件到表单数据-->
<!--      }else if(this.newcode.length>0){-->
<!--        formData.append('mode','edit');-->
<!--        formData.append('edit_filename',this.editFilename);-->
<!--        formData.append('poc_content',this.newcode);-->
<!--      }-->

<!--      try {-->
<!--        const response = await fetch('/api/insertData', {-->
<!--          method: 'POST',-->
<!--          body: formData,-->
<!--        });-->
<!--        const result = await response.json();-->
<!--        if (response.ok) {-->
<!--          this.$message.success(result.message);-->
<!--          this.addDialogVisible = false;-->
<!--          this.$refs.newPocForm.resetFields();-->
<!--          this.fileList = [];-->
<!--          window.location.reload();-->
<!--        } else {-->
<!--          this.$message.error(result.message);-->
<!--        }-->
<!--      } catch (error) {-->
<!--        this.$message.error('An error occurred: ' + error);-->
<!--      }-->
<!--    },-->
<!--    async submitEditPoc() {-->

<!--      this.editSubmitAttempted = true;-->

<!--      // 检查是否选择了有效的affected_infra-->
<!--      if (!this.editAffectedInfraValid || !this.editPoc.affected_infra) {-->
<!--        this.$message.error('请从列表中选择有效的基础设施');-->
<!--        return;-->
<!--      }-->

<!--      const formData = new FormData();-->
<!--      formData.append('id', this.editPoc.id);-->
<!--      formData.append('cve_id', this.editPoc.cve_id);-->
<!--      formData.append('vul_name', this.editPoc.vul_name);-->
<!--      formData.append('type', this.editPoc.type); // 确保字段名称正确-->
<!--      formData.append('description', this.editPoc.description);-->
<!--      formData.append('script_type', this.editPoc.script_type);-->
<!--      formData.append('affected_infra', this.editPoc.affected_infra);//漏写-->

<!--      // 添加文件，如果有的话-->
<!--      if (this.fileList.length > 0) {-->
<!--        formData.append('mode','upload');-->
<!--        formData.append('file', this.fileList[0]); // 这里的字段名称应与后端一致-->
<!--      }else if(this.editFilename.length>0&&this.newcode.length>0){-->
<!--        formData.append('mode','edit');-->
<!--        formData.append('edit_filename',this.editFilename);-->
<!--        formData.append('poc_content',this.newcode);-->
<!--      }-->

<!--      try {-->
<!--        const response = await axios.put('/api/updateDataById', formData, {-->
<!--          headers: {-->
<!--            'Content-Type': 'multipart/form-data'-->
<!--          }-->
<!--        });-->

<!--        if (response.data.message === '更新成功') { // 后端可能返回的成功消息字段为 "message"-->
<!--          this.$message.success('POC更新成功');-->
<!--          this.editDialogVisible = false;-->
<!--          this.fileList = [];-->

<!--          // 清空变量，为下一次编辑做准备-->
<!--          this.newcode = '';-->
<!--          this.editFilename = '';-->
<!--          this.tempnewcode = '';-->
<!--          this.tempFilename = '';-->

<!--          window.location.reload();-->
<!--        } else {-->
<!--          this.$message.error('更新失败: ' + response.data.message);-->
<!--        }-->
<!--      } catch (error) {-->
<!--        this.$message.error('网络错误或服务器异常: ' + error.message);-->
<!--      }-->
<!--    },-->

<!--    // 生成模板-->
<!--    async generateTemplate() {-->
<!--      // 构造文件名，根据选择的漏洞类型和选项-->
<!--      let filename = `${this.vulnerabilityType}${this.authRequired}`;-->
<!--      if (this.vulnerabilityType === 1 || this.vulnerabilityType === 2) {-->
<!--        filename += `${this.canGetCommandResult}`;-->
<!--      }-->
<!--      filename += '.py';-->

<!--      // 加载文件内容，从`public`目录下读取-->
<!--      fetch(`/${filename}`)-->
<!--          .then(response => {-->
<!--            if (!response.ok) {-->
<!--              throw new Error('Network response was not ok');-->
<!--            }-->
<!--            return response.text();-->
<!--          })-->
<!--          .then(data => {-->
<!--            this.tempnewcode = data; // 将文件内容保存到tempnewcode-->
<!--          })-->
<!--          .catch(error => {-->
<!--            console.error('无法读取模板文件:', error);-->
<!--            this.tempnewcode = '# 无法读取模板文件';-->
<!--          });-->
<!--    },-->
<!--    async loadFile() {-->
<!--      try {-->
<!--        const response = await fetch("/nmap_infrastructure_list_grouped_multiline.txt");-->
<!--        if (!response.ok) throw new Error("Network response was not ok");-->
<!--        const text = await response.text();-->
<!--        // 将每一行内容处理为 { value: "文本" } 格式-->
<!--        this.suggestions = text.split("\n").map(line => ({ value: line.trim() })).filter(item => item.value);-->
<!--        console.log("Loaded suggestions:", this.suggestions);-->
<!--      } catch (error) {-->
<!--        console.error("Failed to load file:", error);-->
<!--      }-->
<!--    },-->

<!--    querySearch(queryString, callback) {-->
<!--      console.log("querySearch triggered with:", queryString);-->
<!--      if (queryString.length >= 3) {-->
<!--        const results = this.suggestions.filter(item =>-->
<!--            item.value.toLowerCase().includes(queryString.toLowerCase())-->
<!--        );-->
<!--        console.log("Filtered results:", results);-->
<!--        callback(results);-->
<!--      } else {-->
<!--        callback([]);-->
<!--      }-->
<!--    },-->
<!--    // 新增时选择建议的处理方法-->
<!--    handleSelectNew(item) {-->
<!--      console.log("Selected for new POC:", item);-->
<!--      // 将选中的值设置到实际存储字段-->
<!--      this.newPoc.affected_infra = item.value;-->
<!--      // 标记为有效-->
<!--      this.affectedInfraValid = true;-->
<!--    },-->

<!--    // 编辑时选择建议的处理方法-->
<!--    handleSelectEdit(item) {-->
<!--      console.log("Selected for edit POC:", item);-->
<!--      // 将选中的值设置到实际存储字段-->
<!--      this.editPoc.affected_infra = item.value;-->
<!--      // 标记为有效-->
<!--      this.editAffectedInfraValid = true;-->
<!--    },-->


<!--    // querySearch(queryString, callback) {-->
<!--    //   console.log("querySearch triggered with:", queryString); // 调试信息-->
<!--    //   // 仅当输入字符数达到或超过3个并且为连续匹配时才执行匹配-->
<!--    //   if (queryString.length >= 3) {-->
<!--    //     const results = this.suggestions.filter(item =>-->
<!--    //         item.value.toLowerCase().includes(queryString.toLowerCase())-->
<!--    //     );-->
<!--    //     console.log("Filtered results:", results); // 调试信息-->
<!--    //     callback(results);-->
<!--    //   } else {-->
<!--    //     // 输入字符数不足时返回空数组-->
<!--    //     callback([]);-->
<!--    //   }-->
<!--    // },-->
<!--    handleSelect(item) {-->
<!--      console.log("Selected:", item);-->
<!--    },-->
<!--    cancelEdit(){-->
<!--      // 清空变量，为下一次编辑做准备-->
<!--      this.newcode = '';-->
<!--      this.editFilename = '';-->
<!--      this.tempnewcode = '';-->
<!--      this.tempFilename = '';-->
<!--      this.editDialogVisible = false;-->

<!--      // 重置验证状态-->
<!--      this.editAffectedInfraValid = false;-->
<!--      this.editSearchAffectedInfra = '';-->
<!--      this.editSubmitAttempted = false;-->
<!--    }-->

<!--  },-->


<!--  created() {-->
<!--    this.loadData();-->
<!--    this.loadFile();-->
<!--  }-->
<!--}-->
<!--</script>-->

<!--<style scoped>-->
<!--/*设置窗口内容自动换行*/-->
<!--pre {-->
<!--  white-space: pre-wrap;      /* CSS3 的换行方式，保持格式的同时允许自动换行 */-->
<!--  word-wrap: break-word;      /* 较旧的浏览器也可以理解这种方式 */-->
<!--  overflow-wrap: break-word;  /* 标准的换行方式 */-->
<!--  overflow-y: auto;-->
<!--}-->

<!--code[class*="language-"],-->
<!--pre[class*="language-"] {-->
<!--  color: black; /* 代码文字颜色 */-->
<!--  background: none; /* 背景色 */-->
<!--  text-shadow: 0 1px white; /* 文字阴影 */-->
<!--  font-family: Consolas, Monaco, 'Andale Mono', 'Ubuntu Mono', monospace;-->
<!--  font-size: 1em;-->
<!--  text-align: left;-->
<!--  white-space: pre;-->
<!--  word-spacing: normal;-->
<!--  word-break: normal;-->
<!--  word-wrap: normal;-->
<!--  line-height: 1.5;-->

<!--  -moz-tab-size: 4;-->
<!--  -o-tab-size: 4;-->
<!--  tab-size: 4;-->

<!--  -webkit-hyphens: none;-->
<!--  -moz-hyphens: none;-->
<!--  -ms-hyphens: none;-->
<!--  hyphens: none;-->
<!--}-->


<!--</style>-->


