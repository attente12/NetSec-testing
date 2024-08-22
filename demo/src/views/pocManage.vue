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

    <!--   新增poc   -->
    <!-- 新增 POC 对话框 -->
    <!-- 新增 POC 对话框 -->
    <!-- 新增 POC 对话框 -->
<!--    <el-dialog :visible.sync="addDialogVisible" title="新增POC" width="500px" :close-on-click-modal="false">-->
<!--      <el-form :model="newPoc" ref="newPocForm">-->
<!--        <el-form-item label="CVE编号">-->
<!--          <el-input v-model="newPoc.cve_id" placeholder="CVE-xxxx-xxxx"></el-input>-->
<!--        </el-form-item>-->
<!--        <el-form-item label="漏洞名称">-->
<!--          <el-input v-model="newPoc.vul_name"></el-input>-->
<!--        </el-form-item>-->
<!--        <el-form-item label="漏洞描述">-->
<!--          <el-input type="textarea" v-model="newPoc.description"></el-input>-->
<!--        </el-form-item>-->
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
<!--              :before-upload="beforeFileUpload"-->
<!--              :on-change="handleFileChange"-->
<!--              :on-remove="handleRemove"-->
<!--              :file-list="fileList"-->
<!--              :limit="1">-->
<!--            <el-button>选择文件</el-button>-->
<!--          </el-upload>-->
<!--        </el-form-item>-->
<!--      </el-form>-->
<!--      <span slot="footer" class="dialog-footer">-->
<!--    <el-button @click="addDialogVisible = false">取消</el-button>-->
<!--    <el-button type="primary" @click="submitNewPoc">确定</el-button>-->
<!--  </span>-->
<!--    </el-dialog>-->
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
        </el-form-item>
      </el-form>
      <span slot="footer" class="dialog-footer">
    <el-button @click="addDialogVisible = false">取消</el-button>
    <el-button type="primary" @click="submitNewPoc">确定</el-button>
  </span>
    </el-dialog>




<!--    <el-dialog :visible.sync="addDialogVisible" title="新增POC" width="500px"  :close-on-click-modal="false">-->
<!--      <el-form :model="newPoc">-->
<!--        <el-form-item label="CVE编号">-->
<!--          <el-input v-model="newPoc.cve_id" placeholder="CVE-xxxx-xxxx"></el-input>-->
<!--        </el-form-item>-->
<!--        <el-form-item label="漏洞名称">-->
<!--          <el-input v-model="newPoc.vul_name"></el-input>-->
<!--        </el-form-item>-->
<!--        <el-form-item label="漏洞描述">-->
<!--          <el-input type="textarea" v-model="newPoc.description"></el-input>-->
<!--        </el-form-item>-->
<!--        <el-form-item label="POC类型">-->
<!--          <el-select v-model="newPoc.script_type" placeholder="请选择">-->
<!--            <el-option label="python" value="python"></el-option>-->
<!--            <el-option label="c/c++" value="c/c++" :disabled="true"></el-option>-->
<!--            <el-option label="yaml" value="yaml" :disabled="true"></el-option>-->
<!--          </el-select>-->
<!--        </el-form-item>-->
<!--        &lt;!&ndash; poc代码 上传文件 &ndash;&gt;-->
<!--        <el-form-item label="POC代码">-->
<!--          <el-button>选择文件</el-button>-->
<!--        </el-form-item>-->
<!--&lt;!&ndash;        <el-form-item label="POC代码">&ndash;&gt;-->
<!--&lt;!&ndash;          <el-button @click="codeDialogVisible = true">填写代码</el-button>&ndash;&gt;-->
<!--&lt;!&ndash;        </el-form-item>&ndash;&gt;-->
<!--&lt;!&ndash;        <el-dialog :visible.sync="codeDialogVisible" title="请输入Python格式代码" width="1000px"  :close-on-click-modal="false" :append-to-body="true">&ndash;&gt;-->
<!--&lt;!&ndash;          <el-input type="textarea" v-model="tempCode" rows="25" ref="codeInput"></el-input>&ndash;&gt;-->
<!--&lt;!&ndash;          <span slot="footer" class="dialog-footer">&ndash;&gt;-->
<!--&lt;!&ndash;                <el-button @click="codeDialogVisible = false">取消</el-button>&ndash;&gt;-->
<!--&lt;!&ndash;                <el-button type="primary" @click="saveCode">确定</el-button>&ndash;&gt;-->
<!--&lt;!&ndash;          </span>&ndash;&gt;-->
<!--&lt;!&ndash;        </el-dialog>&ndash;&gt;-->
<!--      </el-form>-->
<!--      <span slot="footer" class="dialog-footer">-->
<!--              <el-button @click="addDialogVisible = false">取消</el-button>-->
<!--              <el-button type="primary" @click="submitNewPoc">确定</el-button>-->
<!--        </span>-->
<!--    </el-dialog>-->


    <!-- 查看POC代码 -->
    <!--        <el-dialog :visible.sync="dialogVisible" width="60%" title="POC代码">-->
    <!--            <pre>{{ selectedPocCode }}</pre>-->
    <!--        </el-dialog>-->
    <el-dialog :visible.sync="dialogVisible" width="60%" :height="400" title="POC代码">
<!--      <pre style="height: 500px; overflow-y: scroll;">{{ selectedPocCode }}</pre>-->
        <pre style="height: 500px; overflow-y: scroll;"><code class="language-python">{{ selectedPocCode }}</code></pre>
    </el-dialog>

<!--    编辑poc代码-->
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
        <el-form-item label="POC代码（如需更改请上传）">
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
            <div slot="tip" class="el-upload__tip">只能上传.py文件</div>
          </el-upload>
        </el-form-item>
      </el-form>
      <span slot="footer" class="dialog-footer">
      <el-button @click="editDialogVisible = false">取消</el-button>
      <el-button type="primary" @click="submitEditPoc">确定</el-button>
    </span>
    </el-dialog>



<!--    <el-dialog :visible.sync="editDialogVisible" title="编辑POC" width="500px" :close-on-click-modal="false">-->
<!--      <el-form :model="editPoc">-->
<!--        <el-form-item label="CVE编号">-->
<!--          <el-input v-model="editPoc.cve_id"></el-input>-->
<!--        </el-form-item>-->
<!--        <el-form-item label="漏洞名称">-->
<!--          <el-input v-model="editPoc.vul_name"></el-input>-->
<!--        </el-form-item>-->
<!--        <el-form-item label="漏洞描述">-->
<!--          <el-input type="textarea" v-model="editPoc.description"></el-input>-->
<!--        </el-form-item>-->
<!--        <el-form-item label="POC类型">-->
<!--          <el-select v-model="editPoc.script_type" placeholder="请选择">-->
<!--            <el-option label="python" value="python" :disabled="true"></el-option>-->
<!--            <el-option label="c/c++" value="c/c++" :disabled="true"></el-option>-->
<!--            <el-option label="yaml" value="yaml" :disabled="true"></el-option>-->
<!--          </el-select>-->
<!--        </el-form-item>-->
<!--        <el-form-item label="POC代码（如需更改请上传）">-->
<!--          <el-button>选择文件</el-button>-->
<!--        </el-form-item>-->
<!--      </el-form>-->
<!--      <span slot="footer" class="dialog-footer">-->
<!--          <el-button @click="editDialogVisible = false">取消</el-button>-->
<!--          <el-button type="primary" @click="submitEditPoc">确定</el-button>-->
<!--      </span>-->
<!--    </el-dialog>-->

    <!-- 编辑POC代码的对话框 -->
<!--    <el-dialog :visible.sync="codeEditDialogVisible" title="编辑Python格式代码" width="1000px" :close-on-click-modal="false" :append-to-body="true">-->
<!--      <el-input type="textarea" v-model="tempCode" rows="25" ref="codeEditInput"></el-input>-->
<!--      <span slot="footer" class="dialog-footer">-->
<!--        <el-button @click="codeEditDialogVisible = false">取消</el-button>-->
<!--        <el-button type="primary" @click="saveEditedCode">确定</el-button>-->
<!--      </span>-->
<!--    </el-dialog>-->


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
      <el-table-column prop="script_type" label="POC类型" width="130"></el-table-column>

      <el-table-column prop="script" label="POC代码" width="150">
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

export default {
  name: "pocManage",
  data(){
    return{
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
    };
  },
  watch: {
    codeDialogVisible(newVal) {
      if (newVal) { // 当对话框变为可见时
        this.$nextTick(() => {
          this.$refs.codeInput.focus(); // 聚焦到输入框
        });
      }
    },
    // dialogVisible(newVal) {
    //   if (newVal) {
    //     this.$nextTick(() => {
    //       Prism.highlightAll();  // 应用 Prism 高亮
    //     });
    //   }
    // }
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
  methods:{
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
    // handleLook(row) {
    //   this.selectedPocCode = row.script;
    //   // this.dialogVisible = true;
    //   this.$nextTick(() => {
    //     this.dialogVisible = true;
    //   });
    // },
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
            }
          })
          .catch(error => {
            // 处理请求错误
            console.error('Error fetching POC content:', error);
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
      fetch('http://192.168.177.129:8081/getAllData')
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
    saveCode() {
      this.newPoc.script = this.tempCode; // 将临时代码保存到newPoc中
      this.codeDialogVisible = false; // 关闭代码输入对话框
      this.tempCode = ''; // 清空临时代码
    },
    // submitNewPoc() {
    //   fetch('http://192.168.177.129:8081/insertData', {
    //     method: 'POST',
    //     headers: {
    //       'Content-Type': 'application/json',
    //     },
    //     body: JSON.stringify(this.newPoc)
    //   })
    //       .then(response => {
    //         return response.json().then(data => {  // 假设服务器返回的是JSON格式的数据
    //           if (response.ok) {
    //             this.addDialogVisible = false;  // 关闭对话框
    //             this.loadData();  // 重新加载数据
    //             this.$message.success('添加成功！');
    //           } else {
    //             throw new Error(data.message || '添加 POC 失败');  // 使用服务器提供的错误信息
    //           }
    //         });
    //       })
    //       .catch(error => {
    //         this.$message.error('添加失败：' + error.message);
    //       });
    // },
    //编辑poc
    handleEdit(row) {
      this.editPoc = { ...row }; // 复制行数据到编辑数据对象
      this.tempCode = row.script; // Set the temporary code to the existing script
      this.editDialogVisible = true; // 显示编辑对话框
    },
    editCode() {
      this.codeEditDialogVisible = true;
    },

    saveEditedCode() {
      this.editPoc.script = this.tempCode; // 将编辑后的代码保存回editPoc
      this.codeEditDialogVisible = false; // 关闭代码编辑对话框
    },

    // submitEditPoc() {
    //   // 确保包含ID和更新的时间戳
    //   // this.editPoc.timestamp = new Date().toISOString();
    //
    //   // 使用PUT方法发送请求
    //   fetch('http://192.168.177.129:8081/updateDataById', {
    //     method: 'PUT', // 更改为 PUT 方法
    //     headers: {
    //       'Content-Type': 'application/json',
    //     },
    //     body: JSON.stringify({
    //       id: this.editPoc.id,  // 确保发送 ID
    //       cve_id: this.editPoc.cve_id,
    //       vul_name: this.editPoc.vul_name,
    //       description: this.editPoc.description,
    //       script_type: this.editPoc.script_type,
    //       script: this.editPoc.script
    //     })
    //   })
    //       .then(response => {
    //         if (response.ok) {
    //           this.editDialogVisible = false; // 关闭对话框
    //           this.loadData(); // 重新加载数据
    //           this.$message.success('编辑成功！');
    //         } else {
    //           throw new Error('编辑 POC 失败');
    //         }
    //       })
    //       .catch(error => {
    //         this.$message.error('编辑失败：' + error.message);
    //       });
    // },
    del(id) {
      fetch(`http://192.168.177.129:8081/deleteDataById`, {
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
      fetch(`http://192.168.177.129:8081/deleteDataById`, {
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
      }
      return isPython;
    },
    handleFileUpload(param) {
      if (param.file) {
        this.fileList = [param.file];
      }
    },
    handleRemove() {
      this.fileList = [];
    },
    // async submitNewPoc() {
    //   const formData = new FormData();
    //   formData.append('cve_id', this.newPoc.cve_id);
    //   formData.append('vul_name', this.newPoc.vul_name);
    //   formData.append('description', this.newPoc.description);
    //   formData.append('script_type', this.newPoc.script_type);
    //   if (this.fileList.length > 0) {
    //     formData.append('file', this.fileList[0].raw);
    //   }
    //
    //   try {
    //     const response = await fetch('/api/insertData', {
    //       method: 'POST',
    //       body: formData,
    //     });
    //     const result = await response.json();
    //     if (response.ok) {
    //       this.$message.success(result.message);
    //       this.addDialogVisible = false;
    //       this.$refs.newPocForm.resetFields();
    //       this.fileList = [];
    //     } else {
    //       this.$message.error(result.message);
    //     }
    //   } catch (error) {
    //     this.$message.error('An error occurred: ' + error);
    //   }
    // },
    async submitNewPoc() {
      const formData = new FormData();
      formData.append('cve_id', this.newPoc.cve_id);
      formData.append('vul_name', this.newPoc.vul_name);
      formData.append('description', this.newPoc.description);
      formData.append('script_type', this.newPoc.script_type);
      if (this.fileList.length > 0) {
        formData.append('file', this.fileList[0].raw || this.fileList[0]); // 添加文件到表单数据
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
        formData.append('script', this.fileList[0].raw); // 这里的字段名称应与后端一致
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
        } else {
          this.$message.error('更新失败: ' + response.data.message);
        }
      } catch (error) {
        this.$message.error('网络错误或服务器异常: ' + error.message);
      }
    }

    // async submitEditPoc() {
    //   const formData = new FormData();
    //   formData.append('id', this.editPoc.id);
    //   formData.append('cve_id', this.editPoc.cve_id);
    //   formData.append('vul_name', this.editPoc.vul_name);
    //   formData.append('description', this.editPoc.description);
    //   formData.append('script_type', this.editPoc.script_type);
    //
    //   // 添加文件，如果有的话
    //   if (this.fileList.length > 0) {
    //     formData.append('file', this.fileList[0].raw);
    //   }
    //
    //   try {
    //     const response = await axios.post('/api/updateDataById', formData);
    //     if (response.data.success) {
    //       this.$message.success('POC更新成功');
    //       this.editDialogVisible = false;
    //       this.fileList = [];
    //     } else {
    //       this.$message.error('更新失败: ' + response.data.message);
    //     }
    //   } catch (error) {
    //     this.$message.error('网络错误或服务器异常: ' + error.message);
    //   }
    // }

  },


  created() {
    this.loadData();
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