<template>
  <div class="weak-password-container">
    <!-- 头部区域 -->
    <div class="header-section">
      <h1 class="main-title">弱口令检测系统</h1>
      <div class="system-info">
        <el-tag type="info">{{ new Date().toLocaleString() }}</el-tag>
      </div>
    </div>

    <!-- 控制面板区域 -->
    <div class="control-panel">
      <el-card class="control-card">
        <div class="control-row">
          <!-- 目标IP选择 -->
          <div class="control-item">
            <el-select
                v-model="scanTarget"
                placeholder="选择扫描目标IP"
                @change="changeServer"
                default-first-option
                size="medium">
              <el-option
                  v-for="ip in aliveHosts"
                  :key="ip"
                  :label="ip"
                  :value="ip">
              </el-option>
            </el-select>
<!--            <el-select-->
<!--                v-model="scanTarget"-->
<!--                placeholder="选择扫描目标IP"-->
<!--                filterable-->
<!--                allow-create-->
<!--                default-first-option-->
<!--                size="medium">-->
<!--              <el-option-->
<!--                  v-for="ip in aliveHosts"-->
<!--                  :key="ip"-->
<!--                  :label="ip"-->
<!--                  :value="ip">-->
<!--              </el-option>-->
<!--            </el-select>-->
          </div>

          <div class="info-alert">
            <i class="el-icon-warning-outline"></i>
            <span>如果该资产未进行过端口扫描，需要进行预扫描。</span>
          </div>

          <div class="control-action">
            <el-button
                @click="debouncedDetect"
                :loading="debouncedDetectLoading"
                icon="el-icon-search"
                type="primary"
                size="medium">
              预扫描
            </el-button>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 服务选择区域 -->
    <div class="service-section">
      <el-card class="service-card">
        <div slot="header" class="card-header">
          <span><i class="el-icon-s-operation"></i> 选择服务进行检测</span>

          <el-checkbox
              v-model="checkAllServices"
              :indeterminate="isIndeterminate"
              @change="handleCheckAllServices">
            全选服务
          </el-checkbox>
        </div>

        <el-checkbox-group v-model="selectedServices">
          <el-row :gutter="20">
            <el-col :span="6" v-for="service in services" :key="service.name">
              <el-checkbox :label="service.name" class="service-checkbox">
                {{ service.name }} ({{ service.port }})
              </el-checkbox>
            </el-col>
          </el-row>
        </el-checkbox-group>

        <div class="selected-services">
          <span class="section-label">已选择服务:</span>
          <template v-for="(serviceName, index) in selectedServices">
            {{ serviceName }}({{ getServiceDetails(serviceName).port }})
            <span v-if="index < selectedServices.length - 1" :key="'comma' + index">, </span>
          </template>
        </div>

        <!-- 字典上传区域 -->
        <div class="upload-section">
          <div class="upload-row">
            <div class="upload-item">
              <el-upload
                  class="upload"
                  action="#"
                  :auto-upload="false"
                  :on-change="handleUsernameFileChange"
                  :limit="1"
                  :show-file-list="false"
                  :file-list="[]"
                  ref="usernameUpload"
                  accept=".txt">
                <el-button size="medium" type="primary">上传用户名字典</el-button>
              </el-upload>
              <div v-if="usernameFile" class="file-info">
                {{ usernameFile.name }}
                <i class="el-icon-close" @click.stop="removeUsernameFile"></i>
              </div>
            </div>

            <div class="upload-item">
              <el-upload
                  class="upload"
                  action="#"
                  :auto-upload="false"
                  :on-change="handlePasswordFileChange"
                  :limit="1"
                  :show-file-list="false"
                  :file-list="[]"
                  ref="passwordUpload"
                  accept=".txt">
                <el-button size="medium" type="primary">上传密码字典</el-button>
              </el-upload>
              <div v-if="passwordFile" class="file-info">
                {{ passwordFile.name }}
                <i class="el-icon-close" @click.stop="removePasswordFile"></i>
              </div>
            </div>
          </div>
        </div>

        <div class="control-action">
          <el-button
              @click="debouncedServiceDetect"
              :loading="debouncedServiceDetectLoading"
              icon="el-icon-search"
              type="primary"
              size="medium">
            开始检测
          </el-button>
        </div>
      </el-card>
    </div>

    <!-- 检测结果区域 -->
    <div class="result-section">
      <el-card class="result-card">
        <div slot="header" class="card-header">
          <span><i class="el-icon-document"></i> 弱口令检测结果</span>
          <div class="header-actions">
            <el-button
                size="medium"
                type="success"
                icon="el-icon-printer"
                @click="printReport">
              打印当前主机弱口令
            </el-button>
            <el-button
                size="medium"
                type="warning"
                icon="el-icon-printer"
                @click="printAllHostsReport">
              打印所有主机弱口令
            </el-button>
<!--            <el-button-->
<!--                size="medium"-->
<!--                type="danger"-->
<!--                icon="el-icon-delete"-->
<!--                @click="clearLocalStorage">-->
<!--              清除数据-->
<!--            </el-button>-->
          </div>
        </div>

        <el-table
            :data="tableData"
            style="width: 100%"
            border
            stripe
            :header-cell-style="{background:'#f5f7fa',color:'#606266'}">
          <el-table-column prop="port" label="端口" width="180"></el-table-column>
          <el-table-column prop="service_name" label="服务" width="180"></el-table-column>
          <el-table-column prop="weak_username" label="账号" width="180"></el-table-column>
          <el-table-column label="结果" width="180">存在弱密码</el-table-column>
        </el-table>
      </el-card>
    </div>

    <!-- 密码强度测试区域 -->
    <div class="strength-test-section">
      <el-card class="strength-card">
        <div slot="header" class="card-header">
          <span><i class="el-icon-key"></i> 自测密码强度</span>
          <el-tooltip
              content="
              密码规则：
              1.弱密码
              只包含数字（6-18位）或者只包含小写字母（6-18位）或者只包含大写字母（6-18位）。
              2.中等密码：
              包含数字和字母（大小写不限）的组合（6-18位）。
              或者包含数字和特殊字符的组合（6-18位）。
              或者包含字母（大小写不限）和特殊字符的组合（6-18位）。
              3.强密码：
              必须包含数字、小写字母、大写字母和特殊字符的组合（6-18位）。
              "
              placement="top"
              :popper-style="{ width: '400px', maxWidth: '450px' }"
              :popper-class="'password-rule-tooltip'">
            <i class="el-icon-question" style="cursor: pointer;"></i>
          </el-tooltip>
        </div>

        <div class="strength-test-content">
          <div class="password-input">
            <el-input
                v-model="secret"
                :type="passwordVisible ? 'text' : 'password'"
                placeholder="请输入密码"
                style="width: 300px;">
              <template v-slot:suffix>
                <i :class="passwordVisible ? 'el-icon-minus' : 'el-icon-view'"
                   @click="togglePasswordVisibility"
                   style="cursor: pointer;"></i>
              </template>
            </el-input>
          </div>

          <div class="test-action">
            <el-button
                @click="debouncedCheckPasswordStrength"
                :loading="PasswordStrengthLoading"
                icon="el-icon-search"
                type="primary"
                size="medium">
              检测强度
            </el-button>
          </div>

          <div class="strength-result" v-if="passwordStrength">
            <span class="result-label">结果：</span>
            <span :style="{ color: passwordStrengthColor, fontWeight: 'bold' }">
              {{ passwordStrength }}
            </span>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 隐藏的打印区域 -->
    <div id="printable" class="printable">
      <h1 class="print-title">弱口令检测报告</h1>
      <div class="print-info">
        <p>打印时间：{{ new Date().toLocaleString() }}</p>
        <p>检测主机IP: {{ scanTarget }}</p>
      </div>
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
          <td>{{ item.service_name }}</td>
          <td>{{ item.weak_username }}</td>
          <td>存在弱密码</td>
        </tr>
        </tbody>
      </table>
      <div class="signature-area">
        <span>检测人员签名：</span>
        <div class="signature-line"></div>
      </div>
    </div>
    <!-- 隐藏的所有主机打印区域 -->
    <div id="printableAllHosts" class="printable">
      <h1 class="print-title">全部主机弱口令检测报告</h1>
      <div class="print-info">
        <p>打印时间：{{ new Date().toLocaleString() }}</p>
      </div>
      <table class="print-table">
        <thead>
        <tr>
          <th>主机IP</th>
          <th>端口</th>
          <th>服务</th>
          <th>账号</th>
          <th>结果</th>
        </tr>
        </thead>
        <tbody>
        <template v-for="(host) in allHostsWeakPasswords">
          <tr v-for="(item, itemIndex) in host.weak_passwords" :key="host.ip + '-' + item.port + '-' + item.service_name + '-' + item.weak_username">
            <td v-if="itemIndex === 0" :rowspan="host.weak_passwords.length">{{ host.ip }}</td>
            <td>{{ item.port }}</td>
            <td>{{ item.service_name }}</td>
            <td>{{ item.weak_username }}</td>
            <td>存在弱密码</td>
          </tr>
        </template>
        </tbody>
      </table>
      <div class="signature-area">
        <span>检测人员签名：</span>
        <div class="signature-line"></div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import _ from 'lodash';

export default {
  name: "weakPasswordDetection",
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
      isDetecting: false,
      isScanning: false,
      aliveHosts: [],
      debouncedDetectLoading: false,
      debouncedServiceDetectLoading: false,
      PasswordStrengthLoading: false,
      checkAllServices: false,
      isIndeterminate: false,
      allHostsWeakPasswords: [], // 新增：存储所有主机的弱口令数据
    };
  },

  created() {
    // 创建防抖函数
    this.debouncedDetect = _.debounce(this.detect, 1000);
    this.debouncedServiceDetect = _.debounce(this.serviceDetect, 1000);
    this.debouncedCheckPasswordStrength = _.debounce(this.checkPasswordStrength, 500);
  },

  methods: {
    changeServer() {
      if (this.scanTarget) {
        this.fetchAndDisplayPasswordResults();
      }
    },
    handleCheckAllServices(val) {
      this.selectedServices = val ? this.services.map(s => s.name) : [];
      this.isIndeterminate = false;
    },
    // 获取活跃IP列表
    fetchAliveHosts() {
      axios.get('/api/getAliveHosts')
          .then(response => {
            this.aliveHosts = response.data.alive_hosts;
            if (!this.scanTarget) {
              this.scanTarget = this.aliveHosts[0];
            }
            this.fetchAndDisplayPasswordResults();
          })
          .catch(error => {
            console.error('获取活跃IP列表失败:', error);
            this.$message.error('获取活跃IP列表失败');
          });
    },
    fetchAndDisplayPasswordResults() {
      if (!this.scanTarget) {
        this.$message.warning('请先选择服务器IP');
        return;
      }

      axios.get(`/api/getWeakPasswordByIp?ip=${this.scanTarget}`)
          .then(response => {
            // this.checkresults = response.data.Event_result;
            this.tableData = response.data;
          })
          .catch(error => {
            console.error('Error:', error);
            this.$message.error('获取检测结果失败，请重试');
          });
    },
    // 获取所有主机的弱口令数据
    fetchAllHostsWeakPasswords() {
      return axios.get('/api/getAllWeakPassword')
          .then(response => {
            this.allHostsWeakPasswords = response.data;
            return response.data;
          })
          .catch(error => {
            console.error('获取所有主机弱口令数据失败:', error);
            this.$message.error('获取所有主机弱口令数据失败，请重试');
            throw error;
          });
    },
    // 打印所有主机弱口令报告
    async printAllHostsReport() {
      try {
        await this.fetchAllHostsWeakPasswords();
        if (this.allHostsWeakPasswords.length === 0) {
          this.$message.warning('没有发现弱口令数据');
          return;
        }

        // 执行打印操作
        const printContents = document.getElementById('printableAllHosts').innerHTML;
        const originalContents = document.body.innerHTML;
        document.body.innerHTML = printContents;
        window.print();
        document.body.innerHTML = originalContents;
        window.location.reload();
      } catch (error) {
        console.error('打印所有主机报告失败:', error);
      }
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
        this.$refs.passwordUpload.clearFiles();
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

    // 预扫描方法
    async detect() {
      this.debouncedDetectLoading = true;
      if (this.isScanning) {
        this.$message.warning('扫描正在进行中，请稍候...');
        return;
      }

      if (!this.scanTarget) {
        this.$message.error('请输入有效的IP地址');
        this.debouncedDetectLoading = false;
        return;
      }

      this.isScanning = true;
      localStorage.setItem('scanTarget', JSON.stringify(this.scanTarget));

      try {
        const apiUrl = '/api/getNmapIp';
        const response = await axios.post(apiUrl, {
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

    // 服务检测方法
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
                axios.post('/api/getWeakPassword', formData, {
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
            // response.data.forEach(result => {
            //   this.tableData.push({
            //     port: result.port,
            //     service: result.service,
            //     account: result.login,
            //     password: result.password
            //   });
            // });
          }
        });

        if (foundWeakPasswords) {
          // window.location.reload();
          this.fetchAndDisplayPasswordResults();
          this.$message.success('检测完成，结果已更新');
          // this.saveTableData();
        } else {
          this.$message.warning('检测完成，但未发现弱口令');
        }
      } catch (error) {
        this.$message.error(error.response.data.error);
        // if (error.response?.data?.error === "Service not found") {
        //   this.$message.error(`${error.response.data.service_name}: Service not found`);
        // } else {
        //   this.$message.error('检测失败，请检查网络或服务器');
        // }
        // console.error('Service detect error:', error);
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
        const response = await axios.post('/api/testWeakPassword', { pd: this.secret });
        switch (response.data.message) {
          case 'Weak':
            this.passwordStrength = '弱';
            this.passwordStrengthColor = '#f56c6c';
            break;
          case 'Medium':
            this.passwordStrength = '中';
            this.passwordStrengthColor = '#e6a23c';
            break;
          case 'Strong':
            this.passwordStrength = '强';
            this.passwordStrengthColor = '#67c23a';
            break;
          case 'Invalid':
            this.passwordStrength = '不合法';
            this.passwordStrengthColor = '#606266';
            break;
          default:
            this.passwordStrength = '未知';
            this.passwordStrengthColor = '#909399';
            break;
        }
      } catch (error) {
        console.error('Error checking password strength:', error);
        this.passwordStrength = '检测失败';
        this.passwordStrengthColor = '#f56c6c';
      } finally {
        this.PasswordStrengthLoading = false;
      }
    }
  },
  watch: {
    selectedServices(val) {
      const total = this.services.length;
      this.checkAllServices = val.length === total;
      this.isIndeterminate = val.length > 0 && val.length < total;
    }
  },
  mounted() {
    // this.loadTableData();

    this.fetchAliveHosts(); // 组件挂载时获取活跃IP列表

    // this.fetchAndDisplayPasswordResults();
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

.weak-password-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.main-title {
  color: #303133;
  font-size: 24px;
  font-weight: bold;
  margin: 0;
}

.control-panel, .service-section, .result-section, .strength-test-section {
  margin-bottom: 20px;
}

.control-card, .service-card, .result-card, .strength-card {
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.control-row {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 15px;
  margin-bottom: 15px;
}

.control-item {
  min-width: 200px;
}

.info-alert {
  display: flex;
  align-items: center;
  color: #409EFF;
  font-size: 13px;
}

.info-alert i {
  margin-right: 5px;
}

.control-action {
  margin-left: auto;
  text-align: right;
  margin-top: 10px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 16px;
  font-weight: bold;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.service-checkbox {
  margin-bottom: 12px;
  display: block;
}

.selected-services {
  margin: 15px 0;
  font-size: 14px;
  color: #606266;
}

.section-label {
  font-weight: bold;
  margin-right: 5px;
}

.upload-section {
  margin: 15px 0;
  border-top: 1px solid #ebeef5;
  padding-top: 15px;
}

.upload-row {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
}

.upload-item {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.file-info {
  display: inline-flex;
  align-items: center;
  font-size: 13px;
  color: #606266;
  margin-left: 10px;
  max-width: 180px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.el-icon-close {
  margin-left: 5px;
  color: #909399;
  cursor: pointer;
  transition: color 0.2s;
}

.el-icon-close:hover {
  color: #f56c6c;
}

.strength-test-content {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 15px;
}

.strength-result {
  display: flex;
  align-items: center;
  font-size: 16px;
}

.result-label {
  margin-right: 5px;
  font-weight: bold;
}

/* 打印样式 */
.printable {
  display: none;
}

@media print {
  .printable {
    display: block;
    padding: 20px;
    font-family: Arial, sans-serif;
  }

  .print-title {
    text-align: center;
    font-size: 24px;
    margin-bottom: 20px;
  }

  .print-info {
    text-align: right;
    margin-bottom: 20px;
    font-size: 14px;
  }

  .print-table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 30px;
  }

  .print-table th, .print-table td {
    border: 1px solid #000;
    padding: 8px;
    text-align: left;
  }

  .print-table th {
    background-color: #f5f7fa;
  }

  .signature-area {
    margin-top: 40px;
    text-align: right;
  }

  .signature-line {
    display: inline-block;
    width: 200px;
    border-bottom: 1px solid #000;
    margin-left: 10px;
  }
}
.service-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.service-header .el-checkbox {
  margin-left: 20px;
}

</style>
