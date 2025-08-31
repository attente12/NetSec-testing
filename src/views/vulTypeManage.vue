<template>
  <div class="vuln-type-container">
    <div class="page-header">
      <h2>漏洞类型管理</h2>
      <el-button type="primary" size="small" @click="showAddDialog">新增漏洞类型</el-button>
    </div>

    <div class="tip-text">以下为POC管理中可设置的漏洞类型</div>

    <el-card class="list-card" shadow="hover">
      <div v-if="loading" class="loading-container">
        <el-skeleton :rows="6" animated />
      </div>

      <div v-else>
        <el-empty v-if="vulnTypes.length === 0" description="暂无漏洞类型数据"></el-empty>

        <el-table v-else :data="vulnTypes" style="width: 100%" border>
          <el-table-column prop="index" label="序号" width="80" align="center">
            <template slot-scope="scope">
              {{ scope.$index + 1 }}
            </template>
          </el-table-column>
          <el-table-column prop="type" label="漏洞类型名称" min-width="200">
            <template slot-scope="scope">
              <span>{{ scope.row }}</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120" align="center">
            <template slot-scope="scope">
              <el-button size="mini" type="danger" @click="handleDelete(scope.row)" icon="el-icon-delete"
                circle></el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-card>

    <!-- 新增漏洞类型对话框 -->
    <el-dialog title="新增漏洞类型" :visible.sync="addDialogVisible" width="30%" :close-on-click-modal="false">
      <el-form :model="addForm" :rules="rules" ref="addForm" label-width="100px">
        <el-form-item label="漏洞类型" prop="type">
          <el-input v-model="addForm.type" placeholder="请输入漏洞类型名称"></el-input>
        </el-form-item>
      </el-form>
      <span slot="footer" class="dialog-footer">
        <el-button @click="addDialogVisible = false">取 消</el-button>
        <el-button type="primary" @click="submitAdd" :loading="submitLoading">确 定</el-button>
      </span>
    </el-dialog>

    <!-- 删除确认对话框 -->
    <el-dialog title="删除确认" :visible.sync="deleteDialogVisible" width="30%" :close-on-click-modal="false">
      <div class="delete-confirm-content">
        <i class="el-icon-warning warning-icon"></i>
        <span>确定要删除漏洞类型 "{{ typeToDelete }}" 吗？</span>
      </div>
      <span slot="footer" class="dialog-footer">
        <el-button @click="deleteDialogVisible = false">取 消</el-button>
        <el-button type="danger" @click="confirmDelete" :loading="deleteLoading">确 定</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>

export default {
  name: 'VulnTypeManagement',
  data() {
    return {
      vulnTypes: [],
      loading: false,

      // 新增相关
      addDialogVisible: false,
      addForm: {
        type: ''
      },
      rules: {
        type: [
          { required: true, message: '请输入漏洞类型名称', trigger: 'blur' },
          { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
        ]
      },
      submitLoading: false,

      // 删除相关
      deleteDialogVisible: false,
      typeToDelete: '',
      deleteLoading: false
    }
  },
  created() {
    this.fetchVulnTypes()
  },
  methods: {
    // 获取所有漏洞类型
    async fetchVulnTypes() {
      this.loading = true
      try {
        const response = await this.$axios.get('/poc/getAllVulnTypes')

        this.vulnTypes = response.types || []
      } catch (error) {
        console.error('获取漏洞类型失败:', error)
        this.$message.error('获取漏洞类型失败，请稍后重试')
      } finally {
        this.loading = false
      }
    },

    // 显示新增对话框
    showAddDialog() {
      this.addForm.type = ''
      this.addDialogVisible = true
      // 等待DOM更新后获取表单引用
      this.$nextTick(() => {
        this.$refs.addForm && this.$refs.addForm.clearValidate()
      })
    },

    // 提交新增漏洞类型
    submitAdd() {
      this.$refs.addForm.validate(async (valid) => {
        if (!valid) return

        this.submitLoading = true
        try {
          // 使用导入的this.$axios
          const response = await this.$axios.post('/poc/editVulnType', {
            type: this.addForm.type,
            action: 'add'
          })

          console.log('新增响应:', response.message) // 调试信息
          window.alert(response.message || '添加成功')
          this.addDialogVisible = false
          this.fetchVulnTypes() // 重新获取列表
        } catch (error) {
          console.error('新增失败:', error) // 调试信息


        } finally {
          this.submitLoading = false
        }
      })
    },

    // 显示删除确认对话框
    handleDelete(type) {
      this.typeToDelete = type
      this.deleteDialogVisible = true
    },

    // 确认删除
    async confirmDelete() {
      this.deleteLoading = true
      try {
        // 使用导入的this.$axios
        const response = await this.$axios.post('/poc/editVulnType', {
          type: this.typeToDelete,
          action: 'delete'
        })

        console.log('删除响应:', response) // 调试信息
        window.alert(response.message || '删除成功')
        this.deleteDialogVisible = false
        this.fetchVulnTypes() // 重新获取列表
      } catch (error) {
        console.error('删除失败:', error) // 调试信息


      } finally {
        this.deleteLoading = false
      }
    }
  }
}
</script>

<style scoped>
.vuln-type-container {
  padding: 20px;
  width: 70%;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}


.tip-text {
  color: #606266;
  font-size: 14px;
  margin-bottom: 15px;
}

.list-card {
  margin-bottom: 20px;
}

.loading-container {
  padding: 20px 0;
}

.delete-confirm-content {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px 0;
}

.warning-icon {
  font-size: 24px;
  color: #E6A23C;
  margin-right: 10px;
}
</style>