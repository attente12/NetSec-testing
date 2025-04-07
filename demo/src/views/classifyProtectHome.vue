<template>
  <div class="container">
    <el-card class="box-card">
      <el-row>
        <el-col :span="24">
          <div class="header">
            <h1>Linux等级保护测评</h1>
<!--            <p class="subtitle">安全基线检测工具</p>-->
          </div>
        </el-col>
      </el-row>

      <el-form
          @submit.prevent="submitForm"
          :model="formData"
          :rules="rules"
          ref="form"
          label-width="120px"
          class="login-form">
        <el-form-item label="测评级别" prop="level">
          <el-select
              v-model="formData.level"
              placeholder="请选择测评级别"
              style="width: 100%">
            <el-option
                label="三级等保"
                :value="3">
            </el-option>
            <el-option
                label="二级等保"
                :value="2"
                disabled>
            </el-option>
            <el-option
                label="一级等保"
                :value="1"
                disabled>
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="IP 地址" prop="ip">
          <el-select
              v-model="formData.ip"
              placeholder="请选择或输入服务器IP地址"
              filterable
              allow-create
              default-first-option
              style="width: 100%">
            <el-option
                v-for="ip in aliveHosts"
                :key="ip"
                :label="ip"
                :value="ip">
            </el-option>
          </el-select>
          <!-- 新增查看临时结果链接 -->
          <div class="temp-check-link">
            <el-link
                type="primary"
                :underline="false"
                @click="handleViewTempResult"
                icon="el-icon-view">
              查看该IP的最近报告
            </el-link>
          </div>
        </el-form-item>
        <el-form-item label="root密码" prop="pd">
          <el-input
              v-model="formData.pd"
              type="password"
              placeholder="请输入root密码"
              prefix-icon="el-icon-lock"
              show-password>
          </el-input>
        </el-form-item>
        <el-form-item>
          <div class="control-bar">
            <el-checkbox
                v-model="checkAll"
                @change="handleCheckAllChange"
                style="margin-right: 15px;">
              全选检测项目
            </el-checkbox>
            <el-button
                type="primary"
                @click="startCheck"
                icon="el-icon-video-play"
                :loading="loading"
                :disabled="selectedItems.length === 0">
              开始检测
            </el-button>
          </div>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="box-card check-items">
      <div slot="header" class="card-header">
        <span>检测项目选择</span>
      </div>

      <el-checkbox-group v-model="selectedItems" @change="handleCheckedItemsChange">
        <el-row :gutter="20">
          <el-col :span="8" v-for="item in checkItems" :key="item.id">
            <el-checkbox :label="item.id">
              <el-tooltip :content="item.name" placement="top">
                <span class="checkbox-label">{{ item.name }}</span>
              </el-tooltip>
            </el-checkbox>
          </el-col>
        </el-row>
      </el-checkbox-group>


    </el-card>

    <el-dialog
        title="检测完成"
        :visible.sync="dialogVisible"
        width="30%"
        center>
      <span>检测任务已完成，是否查看结果？</span>
      <span slot="footer" class="dialog-footer">
        <el-button @click="dialogVisible = false">取 消</el-button>
        <el-button type="primary" @click="viewResult">查看结果</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import { Message } from "element-ui";

export default {
  name: "home",
  data() {
    return {
      formData: {
        ip: '',
        pd: '',
        level: 3 // 默认选择三级等保
      },
      aliveHosts: [], // 存储活跃IP列表
      selectedItems: [],
      checkAll: false,
      dialogVisible: false,
      loading: false,
      rules: {
        level: [
          { required: true, message: '请选择测评级别', trigger: 'change' }
        ],
        ip: [
          { required: true, message: '请输入IP地址', trigger: 'blur' },
          { pattern: /^(\d{1,3}\.){3}\d{1,3}$/, message: '请输入正确的IP地址格式', trigger: 'blur' }
        ],
        pd: [
          { required: true, message: '请输入密码', trigger: 'blur' }
        ]
      },
      checkItems: [
        { id: 1, name: '8.1.3.2.a 应在网络边界或区域之间根据访问控制策略设置访问控制规则，默认情况下除允许通信外受控接口拒绝所有通信' },
        { id: 2, name: '8.1.3.2.d 应能根据会话状态信息为进出数据流提供明确的允许/拒绝访问能力' },
        // { id: 2, name: '检查口令最小长度' },
        // { id: 3, name: '检查口令过期前警告天数' },
        // { id: 4, name: '检查设备密码复杂度策略' },
        // { id: 5, name: '检查是否存在空口令账号' },
      ]
    };
  },
  created() {
    // 组件创建时获取活跃IP列表
    this.fetchAliveHosts();
  },
  methods: {
    // 获取活跃IP列表
    fetchAliveHosts() {
      fetch('/api/getAliveHosts')
          .then(response => {
            if (!response.ok) {
              throw new Error(`HTTP status ${response.status}`);
            }
            return response.json();
          })
          .then(data => {
            this.aliveHosts = data.alive_hosts;
          })
          .catch(error => {
            Message.error('获取活跃IP列表失败：' + error.message);
          });
    },
    // 处理全选复选框变化
    handleCheckAllChange(val) {
      const allItemIds = this.checkItems.map(item => item.id);
      this.selectedItems = val ? allItemIds : [];
    },
    // 处理选中项变化
    handleCheckedItemsChange(value) {
      const checkedCount = value.length;
      this.checkAll = checkedCount === this.checkItems.length;
    },
    // 开始检测（合并了原来的submitForm和batchExecute方法）
    startCheck() {
      this.$refs.form.validate((valid) => {
        if (!valid) {
          return;
        }

        if (this.selectedItems.length === 0) {
          Message.warning('请选择至少一个检测项目');
          return;
        }

        this.loading = true;
        const payload = {
          //level: this.formData.level, // 添加测评级别到payload
          ip: this.formData.ip,
          pd: this.formData.pd,
          ids: this.selectedItems
        };

        fetch('/api/level3Login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(payload),
        })
            .then(response => {
              if (!response.ok) {
                if (response.status === 500) {
                  throw new Error("SSH会话无法启动");
                }
                throw new Error(`HTTP status ${response.status}`);
              }
              return response.json();
            })
            .then(data => {
              console.log(data);
              this.loading = false;
              this.dialogVisible = true;
            })
            .catch((error) => {
              this.loading = false;
              Message.error(error.message);
            });
      });
    },
    viewResult() {
      this.dialogVisible = false;
      this.$nextTick(() => {
        this.$router.push({
          path: '/tempClassifyProtect',  // 改为跳转到新页面
          query: {
            //level: this.formData.level, // 传递测评级别
            ip: this.formData.ip  // 传递检测的IP
          }
        });
      });
    },
    handleViewTempResult() {
      if (!this.formData.ip) {
        Message.warning('请先输入服务器IP地址');
        return;
      }

      // 验证IP格式（复用原有规则）
      const ipPattern = /^(\d{1,3}\.){3}\d{1,3}$/;
      if (!ipPattern.test(this.formData.ip.trim())) {
        Message.error('IP地址格式不正确，请检查输入');
        return;
      }

      this.$router.push({
        path: '/tempClassifyProtect',
        query: { ip: this.formData.ip }
      });
    },
  }
}
</script>

<style scoped>
.container {
  padding: 20px;
}

.box-card {
  margin-bottom: 20px;
}

.header {
  text-align: center;
  margin-bottom: 30px;
}

.header h1 {
  color: #409EFF;
  margin-bottom: 10px;
}

.subtitle {
  color: #909399;
  font-size: 14px;
}

.login-form {
  max-width: 500px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  align-items: center;
}

.check-items {
  margin-top: 30px;
}

.checkbox-label {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  display: inline-block;
  max-width: 200px;
}

.el-checkbox {
  margin-bottom: 15px;
  width: 100%;
}

.el-row {
  margin-bottom: 20px;
}

.control-bar {
  display: flex;
  align-items: center;
}

.selected-info {
  margin-top: 10px;
  color: #606266;
  font-size: 14px;
}

.temp-check-link {
  margin-top: -8px;
  margin-bottom: -13px;
  font-size: 12px;
  text-align: right;

  .el-link {
    display: inline-flex;
    align-items: center;

    i {
      margin-right: 3px;
      font-size: 14px;
    }
  }
}

.login-form >>> .el-form-item {
  margin-bottom: 18px;
}
</style>

