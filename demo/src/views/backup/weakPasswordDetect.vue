<template>
  <div class="container">
    <div class="title">
      <h1>弱口令检测</h1>
    </div>

    <el-row :gutter="20">
      <el-col :span="8">
        <el-card class="box-card">
          <div slot="header">目标ip</div>
          <el-select v-model="scanTarget" placeholder="请输入或选择要扫描的目标，例如：192.168.1.0" filterable allow-create
            default-first-option style="width: 100%; margin-bottom: 10px;">
            <el-option v-for="ip in aliveHosts" :key="ip" :label="ip" :value="ip">
            </el-option>
          </el-select>
          <div style="margin-bottom: 10px; color: #409EFF; font-size: 13px;">
            <i class="el-icon-warning-outline" style="margin-right: 5px;"></i>如果该资产未进行过端口扫描，需要进行预扫描。
          </div>
          <div class="scan-button">
            <!--            <el-button size="small" @click="debouncedDetect">扫描</el-button>-->
            <el-button @click="debouncedDetect" :loading="debouncedDetectLoading" icon="el-icon-search" size="small"
              type="primary">
              扫描
            </el-button>
          </div>
        </el-card>
      </el-col>

      <el-col :span="16">
        <el-card class="box-card">
          <div slot="header">选择服务进行检测</div>
          <el-checkbox-group v-model="selectedServices">
            <el-row :gutter="20">
              <el-col :span="6" v-for="service in services" :key="service.name">
                <el-checkbox :label="service.name">
                  {{ service.name }} ({{ service.port }})
                </el-checkbox>
              </el-col>
            </el-row>
          </el-checkbox-group>

          <p>已选择服务:
            <template v-for="(serviceName, index) in selectedServices">
              {{ serviceName }}({{ getServiceDetails(serviceName).port }})
              <span v-if="index < selectedServices.length - 1" :key="'comma' + index">, </span>
            </template>
          </p>

          <!-- Upload section in template -->
          <div class="upload-container">
            <div class="upload-row">
              <div class="upload-item">
                <el-upload class="upload" action="#" :auto-upload="false" :on-change="handleUsernameFileChange"
                  :limit="1" :show-file-list="false" :file-list="[]" ref="usernameUpload" accept=".txt">
                  <el-button size="small" type="primary">上传用户名字典</el-button>
                </el-upload>
                <div v-if="usernameFile" class="file-info">{{ usernameFile.name }}
                  <i class="el-icon-close" @click.stop="removeUsernameFile"></i>
                </div>
              </div>

              <div class="upload-item" style="margin-left: 10px;">
                <el-upload class="upload" action="#" :auto-upload="false" :on-change="handlePasswordFileChange"
                  :limit="1" :show-file-list="false" :file-list="[]" ref="passwordUpload" accept=".txt">
                  <el-button size="small" type="primary">上传密码字典</el-button>
                </el-upload>
                <div v-if="passwordFile" class="file-info">{{ passwordFile.name }}
                  <i class="el-icon-close" @click.stop="removePasswordFile"></i>
                </div>
              </div>
            </div>
          </div>

          <div class="scan-button">
            <!--            <el-button size="small" @click="debouncedServiceDetect">检测</el-button>-->
            <el-button @click="debouncedServiceDetect" :loading="debouncedServiceDetectLoading" icon="el-icon-search"
              type="primary" size="small">
              检测
            </el-button>
          </div>
        </el-card>
      </el-col>

    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card class="box-card">
          <div slot="header">弱口令检测结果</div>
          <el-button size="small" @click="printReport">打印检测报告</el-button>
          <el-button size="small" type="danger" @click="clearLocalStorage">清除数据</el-button>
          <el-table :data="tableData" style="width: 100%">
            <el-table-column prop="port" label="端口" width="180"></el-table-column>
            <el-table-column prop="service" label="服务" width="180"></el-table-column>
            <el-table-column prop="account" label="账号" width="180"></el-table-column>
            <el-table-column prop="password" label="密码" width="180"></el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>


    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card class="box-card">
          <div slot="header">自测密码强度
            <el-tooltip content="

              密码规则：
              1.弱密码
              只包含数字（6-18位）或者只包含小写字母（6-18位）或者只包含大写字母（6-18位）。
              2.中等密码：
              包含数字和字母（大小写不限）的组合（6-18位）。
              或者包含数字和特殊字符的组合（6-18位）。
              或者包含字母（大小写不限）和特殊字符的组合（6-18位）。
              3.强密码：
              必须包含数字、小写字母、大写字母和特殊字符的组合（6-18位）。

          " placement="top" :popper-class="'password-rule-tooltip'">
              <i class="el-icon-question" style="font-size: 18px; cursor: pointer; margin-left: 10px;"></i>
            </el-tooltip>
          </div>
          <div>
            <el-input v-model="secret" :type="passwordVisible ? 'text' : 'password'" placeholder="请输入密钥"
              style="width: 200px; margin-right: 10px;">
              <template v-slot:suffix>
                <i :class="passwordVisible ? 'el-icon-minus' : 'el-icon-view'" @click="togglePasswordVisibility"
                  style="cursor: pointer; font-size: 24px;margin-top: 8px;"></i>
              </template>
            </el-input>
            <!--            <el-button size="small" @click="debouncedCheckPasswordStrength" style="margin-right: 20px;">检测</el-button>-->
            <el-button @click="debouncedCheckPasswordStrength" :loading="PasswordStrengthLoading" icon="el-icon-search"
              type="small" style="margin-right: 20px;">
              检测
            </el-button>
            <span>结果：</span>
            <span :style="{ color: passwordStrengthColor, fontWeight: 'bold' }">
              {{ passwordStrength }}
            </span>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 隐藏的打印区域 -->
    <div id="printable" class="printable">
      <h1 class="print-title">弱口令检测报告</h1>
      <p>检测主机IP: {{ scanTarget }}</p>
      <table class="print-table">
        <thead>
          <tr>
            <th>端口</th>
            <th>服务</th>
            <th>账号</th>
            <th>密码</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in tableData" :key="item.port + item.service">
            <td>{{ item.port }}</td>
            <td>{{ item.service }}</td>
            <td>{{ item.account }}</td>
            <td>{{ item.password }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import _ from 'lodash';

export default {
  data() {
    return {
      tableData: [],
      usernameFile: null,
      passwordFile: null,
      services: [
        { name: 'ssh', port: 22 },
        { name: 'mysql', port: 3306 },
        { name: 'rdp', port: 3389 },
        { name: 'ftp', port: 21 },
        { name: 'smtp', port: 25 },
        { name: 'smtps', port: 465 },
        { name: 'smtp-starttls', port: 587 },
        { name: 'pop3', port: 110 },
        { name: 'pop3s', port: 995 },
        { name: 'imap', port: 143 },
        { name: 'imaps', port: 993 },
        { name: 'postgresql', port: 5432 },
        { name: 'mssql', port: 1433 },
        { name: 'http', port: 80 },
        { name: 'https', port: 443 },
        { name: 'ldap', port: 389 },
        { name: 'ldaps', port: 636 },
        { name: 'smb', port: 445 },
        { name: 'vnc', port: 5900 },
        { name: 'telnet', port: 23 },
        { name: 'snmp', port: 161 },
        { name: 'oracle', port: 1521 },
        { name: 'redis', port: 6379 },
        { name: 'sip', port: 5060 },
        { name: 'sips', port: 5061 },
        { name: 'xmpp', port: 5222 },
        { name: 'xmpps', port: 5223 }
      ],
      selectedServices: [],
      scanTarget: '',
      secret: '',
      passwordVisible: false,
      passwordStrength: '',
      passwordStrengthColor: 'black',
      isDetecting: false, // 新增：用于跟踪检测状态
      isScanning: false, // 新增：用于跟踪扫描状态
      aliveHosts: [], // 新增：存储活跃IP列表
      debouncedDetectLoading: false,
      debouncedServiceDetectLoading: false,
      PasswordStrengthLoading: false,
    };
  },

  created() {
    // 创建防抖函数
    this.debouncedDetect = _.debounce(this.detect, 1000);
    this.debouncedServiceDetect = _.debounce(this.serviceDetect, 1000);
    this.debouncedCheckPasswordStrength = _.debounce(this.checkPasswordStrength, 500);
  },

  methods: {
    // 新增：获取活跃IP列表的方法
    fetchAliveHosts() {
      this.$axios.get('/getAliveHosts')
        .then(response => {
          this.aliveHosts = response.data.alive_hosts;
        })
        .catch(error => {
          console.error('获取活跃IP列表失败:', error);
          this.$message.error('获取活跃IP列表失败');
        });
    },
    getServiceDetails(serviceName) {
      return this.services.find(service => service.name === serviceName) || {};
    },

    validateInput(event) {
      this.scanTarget = event;
    },

    removeUsernameFile() {
      this.usernameFile = null;
      this.$refs.usernameUpload.clearFiles();
    },

    removePasswordFile() {
      this.passwordFile = null;
      this.$refs.passwordUpload.clearFiles();
    },

    handleUsernameFileChange(file) {
      if (file.raw.type !== 'text/plain') {
        this.$message.error('请上传txt文件');
        this.$refs.usernameUpload.clearFiles();
        return false;
      }
      this.usernameFile = file.raw;
    },

    handlePasswordFileChange(file) {
      //限制文件类型
      if (file.raw.type !== 'text/plain') {
        this.$message.error('请上传txt文件');
        this.$refs.passwordUpload.clearFiles();
        return false;
      }
      //限制文件大小1MB
      const maxSize = 1024 * 1024;
      if (file.raw.size > maxSize) {
        this.$message.error('文件大小不能超过1MB');
        this.$refs.usernameUpload.clearFiles();
        return false;
      }
      this.passwordFile = file.raw;
    },

    validateDictionaryFiles() {
      if (this.usernameFile && !this.passwordFile) {
        this.$message.error('请同时上传用户名和密码字典文件');
        return false;
      }
      if (!this.usernameFile && this.passwordFile) {
        this.$message.error('请同时上传用户名和密码字典文件');
        return false;
      }
      return true;
    },

    // 修改后的detect方法
    async detect() {
      this.debouncedDetectLoading = true;
      if (this.isScanning) {
        this.$message.warning('扫描正在进行中，请稍候...');
        return;
      }

      if (!this.scanTarget) {
        this.$message.error('请输入有效的IP地址');
        return;
      }

      this.isScanning = true;
      localStorage.setItem('scanTarget', JSON.stringify(this.scanTarget));

      try {
        const apiUrl = '/getNmapIp';
        const response = await this.$axios.post(apiUrl, {
          ip: this.scanTarget
        });

        if (response.data.message === 'Nmap 扫描完成并获取 CVE 数据。') {
          this.$message.success('Nmap 扫描完成并获取 CVE 数据');
        } else {
          this.$message.error('扫描失败，请重试');
        }
      } catch (error) {
        this.$message.error('网络错误或服务器无响应');
        console.error('Scan error:', error);
      } finally {
        this.isScanning = false;
        this.debouncedDetectLoading = false;
      }
    },

    // 修改后的serviceDetect方法
    async serviceDetect() {

      if (this.isDetecting) {
        this.$message.warning('检测正在进行中，请稍候...');
        return;
      }

      if (this.selectedServices.length === 0) {
        this.$message.error('请至少选择一个服务');
        return;
      }

      if (!this.scanTarget) {
        this.$message.error('请输入有效的IP地址');
        return;
      }

      if (!this.validateDictionaryFiles()) {
        return;
      }

      this.debouncedServiceDetectLoading = true;
      this.isDetecting = true;

      try {
        const serviceRequests = this.selectedServices.map(serviceName => {
          const serviceDetails = this.getServiceDetails(serviceName);
          const formData = new FormData();

          formData.append('ip', this.scanTarget);
          formData.append('portId', serviceDetails.port.toString());
          formData.append('service_name', serviceDetails.name);

          if (this.usernameFile && this.passwordFile) {
            formData.append('usernameFile', this.usernameFile);
            formData.append('passwordFile', this.passwordFile);
          }

          return formData;
        });

        const responses = await Promise.all(
          serviceRequests.map(formData =>
            this.$axios.post('/getWeakPassword', formData, {
              headers: {
                'Content-Type': 'multipart/form-data'
              }
            })
          )
        );

        let foundWeakPasswords = false;

        responses.forEach(response => {
          if (response.data && response.data.length > 0) {
            foundWeakPasswords = true;
            response.data.forEach(result => {
              this.tableData.push({
                port: result.port,
                service: result.service,
                account: result.login,
                password: result.password
              });
            });
          }
        });

        if (foundWeakPasswords) {
          this.$message.success('检测完成，结果已更新');
          this.saveTableData();
        } else {
          this.$message.warning('检测完成，但未发现弱口令');
        }
      } catch (error) {
        if (error.response?.data?.error === "Service not found") {
          this.$message.error(`${error.response.data.service_name}: Service not found`);
        } else {
          this.$message.error('检测失败，请检查网络或服务器');
        }
        console.error('Service detect error:', error);
      } finally {
        this.isDetecting = false;
        this.debouncedServiceDetectLoading = false;
      }
    },

    saveTableData() {
      localStorage.setItem('tableData', JSON.stringify(this.tableData));
    },

    loadTableData() {
      const data = localStorage.getItem('tableData');
      const dataStorage = localStorage.getItem('scanTarget');
      if (data) {
        this.tableData = JSON.parse(data);
      }
      if (dataStorage) {
        this.scanTarget = JSON.parse(dataStorage);
      }
    },

    clearLocalStorage() {
      localStorage.removeItem('tableData');
      this.tableData = [];
      this.$message.success('本地存储数据已清除');
    },

    printReport() {
      const printContents = document.getElementById('printable').innerHTML;
      const originalContents = document.body.innerHTML;
      document.body.innerHTML = printContents;
      window.print();
      document.body.innerHTML = originalContents;
      window.location.reload();
    },

    togglePasswordVisibility() {
      this.passwordVisible = !this.passwordVisible;
    },

    async checkPasswordStrength() {
      this.PasswordStrengthLoading = true;
      try {
        const response = await this.$axios.post('/testWeakPassword', { pd: this.secret });
        switch (response.data.message) {
          case 'Weak':
            this.passwordStrength = '弱';
            this.passwordStrengthColor = 'red';
            break;
          case 'Medium':
            this.passwordStrength = '中';
            this.passwordStrengthColor = 'orange';
            break;
          case 'Strong':
            this.passwordStrength = '强';
            this.passwordStrengthColor = 'green';
            break;
          case 'Invalid':
            this.passwordStrength = '不合法';
            this.passwordStrengthColor = 'black';
            break;
          default:
            this.passwordStrength = '未知';
            this.passwordStrengthColor = 'gray';
            break;
        }
      } catch (error) {
        console.error('Error checking password strength:', error);
        this.passwordStrength = '检测失败';
        this.passwordStrengthColor = 'black';
      } finally {
        this.PasswordStrengthLoading = false;
      }
    }
  },

  mounted() {
    this.loadTableData();
    this.fetchAliveHosts(); // 新增：组件挂载时获取活跃IP列表
  },

  // 组件销毁前取消防抖函数
  beforeDestroy() {
    this.debouncedDetect.cancel();
    this.debouncedServiceDetect.cancel();
    this.debouncedCheckPasswordStrength.cancel();
  }
}
</script>

<style scoped>
.container {
  margin: 20px;
}

.box-card {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.scan-button {
  text-align: right;
  margin-top: 10px;
}

/* 添加打印专用的样式 */
@media print {
  #printable {
    display: block;
    font-size: 12px;
    /* 调整打印字体大小 */
  }

  .print-title {
    text-align: center;
  }

  .print-table {
    width: 100%;
    border-collapse: collapse;
  }

  .print-table th,
  .print-table td {
    border: 1px solid #000;
    padding: 8px;
    text-align: left;
    word-wrap: break-word;
    word-break: break-all;
  }

  /* 隐藏不需要打印的部分 */
  .container,
  .el-button {
    display: none;
  }
}

/* 默认情况下隐藏可打印区域 */
#printable {
  display: none;
}

.upload-container {
  margin: 15px 0;
  padding: 10px 0;
}

.upload-row {
  display: flex;
  justify-content: flex-start;
  /* 改为左对齐 */
  align-items: center;
  gap: 40px;
  /* 减小间距 */
}

.upload-item {
  display: flex;
  align-items: center;
  gap: 8px;
  white-space: nowrap;
}

.upload {
  margin-right: 0;
}

.file-info {
  display: inline-flex;
  align-items: center;
  font-size: 12px;
  color: #606266;
  margin-left: 8px;
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.el-icon-close {
  margin-left: 5px;
  color: #909399;
  cursor: pointer;
  font-size: 14px;
  transition: color 0.2s;
}

.el-icon-close:hover {
  color: #f56c6c;
}
</style>
