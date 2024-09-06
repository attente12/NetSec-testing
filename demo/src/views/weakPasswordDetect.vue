<template>
  <div class="container">
    <div class="title">
      <h1>弱口令检测</h1>
    </div>

    <el-row :gutter="20">
      <el-col :span="12">
        <el-card class="box-card">
          <div slot="header">目标ip（首先您需要输入目标IP扫描得到存在的服务）</div>
          <el-input
              type="textarea"
              rows="3"
              placeholder="请输入要扫描的目标，例如：192.168.1.0"
              v-model="scanTarget"
              @input="validateInput">
          </el-input>
          <div class="scan-button">
            <el-button size="small" @click="detect">扫描</el-button>
          </div>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card class="box-card">
          <div slot="header">选择服务进行检测</div>
          <el-radio-group v-model="selectedServiceName">
            <el-radio
                v-for="service in services"
                :label="service.name"
                :key="service.name"
                :value="service.name">
              {{ service.name }}
            </el-radio>
          </el-radio-group>

          <p>
            已选择服务: {{ getServiceDetails(selectedServiceName).name || '无' }}，
            端口: {{ getServiceDetails(selectedServiceName).port || '无' }}
          </p>

          <div class="scan-button">
            <el-button size="small" @click="serviceDetect">检测</el-button>
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
                :popper-class="'password-rule-tooltip'"
            >
              <i class="el-icon-question" style="font-size: 18px; cursor: pointer; margin-left: 10px;"></i>
            </el-tooltip></div>
          <div>
            <el-input
                v-model="secret"
                :type="passwordVisible ? 'text' : 'password'"
                placeholder="请输入密钥"
                style="width: 200px; margin-right: 10px;">
              <template v-slot:suffix>
                <i :class="passwordVisible ? 'el-icon-minus' : 'el-icon-view'"
                   @click="togglePasswordVisibility"
                   style="cursor: pointer; font-size: 24px;margin-top: 8px;"></i>
              </template>
            </el-input>
            <el-button size="small" @click="checkPasswordStrength" style="margin-right: 20px;">检测</el-button>
            <span>结果：</span>
            <span :style="{ color: passwordStrengthColor, fontWeight: 'bold'  }">
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
import axios from 'axios';

export default {
  data() {
    return {
      tableData: [],
      services: [
        { name: 'ssh', port: 22 },
        { name: 'ftp', port: 21 },
        { name: 'email', port: 25 },
        { name: 'mysql', port: 3306 },
        { name: 'web', port: 80 },
        { name: 'cloud', port: 8080 },
        { name: 'vpn', port: 1723 },
        { name: 'storage', port: 2049 }
      ],
      selectedServiceName: '',
      scanTarget: '192.168.177.129',
      secret: '',
      passwordVisible: false,
      passwordStrength: '',
      passwordStrengthColor: 'black' // 默认为黑色
    };
  },

  methods: {
    getServiceDetails(serviceName) {
      return this.services.find(service => service.name === serviceName) || {};
    },
    validateInput(event) {
      this.scanTarget = event;
    },
    detect() {
      if (!this.scanTarget) {
        this.$message.error('请输入有效的IP地址');
        return;
      }

      const apiUrl = '/api/getNmapIp';
      axios.post(apiUrl, {
        ip: this.scanTarget
      }).then(response => {
        if (response.data.message === 'Nmap scan completed and CVE data fetched.') {
          this.$message.success('扫描完成');
        } else {
          this.$message.error('扫描失败，请重试');
        }
      }).catch(error => {
        this.$message.error('网络错误或服务器无响应');
        console.error('Scan error:', error);
      });
    },
    serviceDetect() {
      if (!this.selectedServiceName) {
        this.$message.error('请先选择一个服务');
        return;
      }

      const serviceDetails = this.getServiceDetails(this.selectedServiceName);

      if (!this.scanTarget) {
        this.$message.error('请输入有效的IP地址');
        return;
      }

      const postData = {
        ip: this.scanTarget,
        portId: serviceDetails.port.toString(),
        service_name: serviceDetails.name
      };

      axios.post('/api/getWeakPassword', postData)
          .then(response => {
            if (response.data && response.data.length > 0) {
              response.data.forEach(result => {
                this.tableData.push({
                  port: result.port,
                  service: result.service,
                  account: result.login,
                  password: result.password
                });
              });
              this.$message.success('检测完成，结果已更新');
              this.saveTableData();
            } else {
              this.$message.warning('检测完成，但未发现弱口令');
            }
          })
          .catch(error => {
            if (error.response && error.response.data && error.response.data.error) {
              if (error.response.data.error === "Service not found") {
                this.$message.error(`${error.response.data.service_name}: Service not found`);
              } else {
                this.$message.error('检测失败，请检查网络或服务器');
              }
            } else {
              this.$message.error('检测失败，请检查网络或服务器');
            }
            console.error('Service detect error:', error);
          });
    },
    saveTableData() {
      localStorage.setItem('tableData', JSON.stringify(this.tableData));
    },
    loadTableData() {
      const data = localStorage.getItem('tableData');
      if (data) {
        this.tableData = JSON.parse(data);
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
      try {
        const response = await axios.post('/api/testWeakPassword', { pd: this.secret });
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
            this.passwordStrength = '未知'; // Handle any unexpected response
            this.passwordStrengthColor = 'gray'; // Or any other color for unexpected cases
            break;
        }
      } catch (error) {
        console.error('Error checking password strength:', error);
        this.passwordStrength = '检测失败';
        this.passwordStrengthColor = 'black'; // 发生错误时用黑色表示
      }
    }
  },
  mounted() {
    this.loadTableData();
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
    font-size: 12px; /* 调整打印字体大小 */
  }

  .print-title {
    text-align: center;
  }

  .print-table {
    width: 100%;
    border-collapse: collapse;
  }

  .print-table th, .print-table td {
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
</style>


<!--<template>-->
<!--  <div class="container">-->
<!--    <div class="title">-->
<!--      <h1>弱口令检测</h1>-->
<!--    </div>-->

<!--    <el-row :gutter="20">-->
<!--      <el-col :span="12">-->
<!--        <el-card class="box-card">-->
<!--          <div slot="header">目标ip（首先您需要输入目标IP扫描得到存在的服务）</div>-->
<!--          <el-input-->
<!--              type="textarea"-->
<!--              rows="3"-->
<!--              placeholder="请输入要扫描的目标，例如：192.168.1.0"-->
<!--              v-model="scanTarget"-->
<!--              @input="validateInput">-->
<!--          </el-input>-->
<!--          <div class="scan-button">-->
<!--            <el-button size="small" @click="detect">扫描</el-button>-->
<!--          </div>-->
<!--        </el-card>-->
<!--      </el-col>-->

<!--      <el-col :span="12">-->
<!--        <el-card class="box-card">-->
<!--          <div slot="header">选择服务进行检测</div>-->
<!--          <el-radio-group v-model="selectedServiceName">-->
<!--            <el-radio-->
<!--                v-for="service in services"-->
<!--                :label="service.name"-->
<!--                :key="service.name"-->
<!--                :value="service.name">-->
<!--              {{ service.name }}-->
<!--            </el-radio>-->
<!--          </el-radio-group>-->

<!--          <p>-->
<!--            已选择服务: {{ getServiceDetails(selectedServiceName).name || '无' }}，-->
<!--            端口: {{ getServiceDetails(selectedServiceName).port || '无' }}-->
<!--          </p>-->

<!--          <div class="scan-button">-->
<!--            <el-button size="small" @click="serviceDetect">检测</el-button>-->
<!--          </div>-->
<!--        </el-card>-->
<!--      </el-col>-->
<!--    </el-row>-->


<!--    <el-row :gutter="20" style="margin-top: 20px;">-->
<!--      <el-col :span="24">-->
<!--        <el-card class="box-card">-->
<!--          <div slot="header">弱口令检测结果</div>-->
<!--          <el-button size="small" @click="printReport">打印检测报告</el-button>-->
<!--          <el-table :data="tableData" style="width: 100%">-->
<!--            <el-table-column prop="port" label="端口" width="180"></el-table-column>-->
<!--            <el-table-column prop="service" label="服务" width="180"></el-table-column>-->
<!--            <el-table-column prop="account" label="账号" width="180"></el-table-column>-->
<!--            <el-table-column prop="password" label="密码" width="180"></el-table-column>-->
<!--          </el-table>-->
<!--        </el-card>-->
<!--      </el-col>-->
<!--    </el-row>-->
<!--  </div>-->
<!--</template>-->

<!--<script>-->
<!--import axios from 'axios';-->

<!--export default {-->
<!--  data() {-->
<!--    return {-->
<!--      tableData: [],-->
<!--      services: [-->
<!--        { name: 'ssh', port: 22 },-->
<!--        { name: 'ftp', port: 21 },-->
<!--        { name: 'email', port: 25 },-->
<!--        { name: 'mysql', port: 3306 },-->
<!--        { name: 'web', port: 80 },-->
<!--        { name: 'cloud', port: 8080 },-->
<!--        { name: 'vpn', port: 1723 },-->
<!--        { name: 'storage', port: 2049 }-->
<!--      ],-->
<!--      selectedServiceName: '',-->
<!--      scanTarget: '192.168.177.129'-->
<!--    };-->
<!--  },-->

<!--  methods: {-->
<!--    getServiceDetails(serviceName) {-->
<!--      return this.services.find(service => service.name === serviceName) || {};-->
<!--    },-->
<!--    validateInput(event) {-->
<!--      this.scanTarget = event;-->
<!--    },-->
<!--    detect() {-->
<!--      if (!this.scanTarget) {-->
<!--        this.$message.error('请输入有效的IP地址');-->
<!--        return;-->
<!--      }-->

<!--      const apiUrl = '/api/getNmapIp';-->
<!--      axios.post(apiUrl, {-->
<!--        ip: this.scanTarget-->
<!--      }).then(response => {-->
<!--        if (response.data.message === 'Nmap scan completed and CVE data fetched.') {-->
<!--          this.$message.success('扫描完成');-->
<!--        } else {-->
<!--          this.$message.error('扫描失败，请重试');-->
<!--        }-->
<!--      }).catch(error => {-->
<!--        this.$message.error('网络错误或服务器无响应');-->
<!--        console.error('Scan error:', error);-->
<!--      });-->
<!--    },-->
<!--    serviceDetect() {-->
<!--      if (!this.selectedServiceName) {-->
<!--        this.$message.error('请先选择一个服务');-->
<!--        return;-->
<!--      }-->

<!--      const serviceDetails = this.getServiceDetails(this.selectedServiceName);-->

<!--      if (!this.scanTarget) {-->
<!--        this.$message.error('请输入有效的IP地址');-->
<!--        return;-->
<!--      }-->

<!--      const postData = {-->
<!--        ip: this.scanTarget,-->
<!--        portId: serviceDetails.port.toString(),-->
<!--        service_name: serviceDetails.name-->
<!--      };-->

<!--      axios.post('/api/getWeakPassword', postData)-->
<!--          .then(response => {-->
<!--            if (response.data && response.data.length > 0) {-->
<!--              response.data.forEach(result => {-->
<!--                this.tableData.push({-->
<!--                  port: result.port,-->
<!--                  service: result.service,-->
<!--                  account: result.login,-->
<!--                  password: result.password-->
<!--                });-->
<!--              });-->
<!--              this.$message.success('检测完成，结果已更新');-->
<!--              this.saveTableData();-->
<!--            } else {-->
<!--              this.$message.warning('检测完成，但未发现弱口令');-->
<!--            }-->
<!--          })-->
<!--          .catch(error => {-->
<!--            if (error.response && error.response.data && error.response.data.error) {-->
<!--              if (error.response.data.error === "Service not found") {-->
<!--                this.$message.error(`${error.response.data.service_name}: Service not found`);-->
<!--              } else {-->
<!--                this.$message.error('检测失败，请检查网络或服务器');-->
<!--              }-->
<!--            } else {-->
<!--              this.$message.error('检测失败，请检查网络或服务器');-->
<!--            }-->
<!--            console.error('Service detect error:', error);-->
<!--          });-->
<!--    },-->
<!--    saveTableData() {-->
<!--      localStorage.setItem('tableData', JSON.stringify(this.tableData));-->
<!--    },-->
<!--    loadTableData() {-->
<!--      const data = localStorage.getItem('tableData');-->
<!--      if (data) {-->
<!--        this.tableData = JSON.parse(data);-->
<!--      }-->
<!--    },-->
<!--    printReport() {-->
<!--      window.print();-->
<!--    }-->
<!--  },-->
<!--  mounted() {-->
<!--    this.loadTableData();-->
<!--  }-->
<!--}-->
<!--</script>-->

<!--<style scoped>-->
<!--.container {-->
<!--  margin: 20px;-->
<!--}-->

<!--.box-card {-->
<!--  display: flex;-->
<!--  flex-direction: column;-->
<!--  justify-content: space-between;-->
<!--  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);-->
<!--}-->

<!--.scan-button {-->
<!--  text-align: right;-->
<!--  margin-top: 10px;-->
<!--}-->
<!--</style>-->




<!--<template>-->
<!--  <div class="container">-->
<!--    <div class="title">-->
<!--      <h1>弱口令检测</h1>-->
<!--    </div>-->

<!--    <el-row :gutter="20">-->
<!--      <el-col :span="12">-->
<!--        <el-card class="box-card">-->
<!--          <div slot="header">目标ip（首先您需要输入目标IP扫描得到存在的服务）</div>-->
<!--          <el-input-->
<!--              type="textarea"-->
<!--              rows="3"-->
<!--              placeholder="请输入要扫描的目标，例如：192.168.1.0"-->
<!--              v-model="scanTarget"-->
<!--              @input="validateInput">-->
<!--          </el-input>-->
<!--          <div class="scan-button">-->
<!--            <el-button size="small" @click="detect">扫描</el-button>-->
<!--          </div>-->
<!--        </el-card>-->
<!--      </el-col>-->

<!--      <el-col :span="12">-->
<!--        <el-card class="box-card">-->
<!--          <div slot="header">选择服务进行检测</div>-->
<!--          <el-radio-group v-model="selectedServiceName">-->
<!--            <el-radio-->
<!--                v-for="service in services"-->
<!--                :label="service.name"-->
<!--                :key="service.name"-->
<!--                :value="service.name">-->
<!--              {{ service.name }}-->
<!--            </el-radio>-->
<!--          </el-radio-group>-->

<!--          <p>-->
<!--            已选择服务: {{ getServiceDetails(selectedServiceName).name || '无' }}，-->
<!--            端口: {{ getServiceDetails(selectedServiceName).port || '无' }}-->
<!--          </p>-->

<!--          <div class="scan-button">-->
<!--            <el-button size="small" @click="serviceDetect">检测</el-button>-->
<!--          </div>-->
<!--        </el-card>-->
<!--      </el-col>-->
<!--    </el-row>-->


<!--    <el-row :gutter="20" style="margin-top: 20px;">-->
<!--      <el-col :span="24">-->
<!--        <el-card class="box-card">-->
<!--          <div slot="header">弱口令检测结果</div>-->
<!--          <el-button size="small" @click="detect">打印检测报告</el-button>-->
<!--          <el-table :data="tableData" style="width: 100%">-->
<!--            <el-table-column prop="port" label="端口" width="180"></el-table-column>-->
<!--            <el-table-column prop="service" label="服务" width="180"></el-table-column>-->
<!--            <el-table-column prop="account" label="账号" width="180"></el-table-column>-->
<!--            <el-table-column prop="password" label="密码" width="180"></el-table-column>-->
<!--          </el-table>-->
<!--        </el-card>-->
<!--      </el-col>-->
<!--    </el-row>-->
<!--  </div>-->

<!--</template>-->

<!--<script>-->
<!--import axios from 'axios';-->


<!--export default {-->
<!--  data() {-->
<!--    return {-->
<!--      tableData: [-->
<!--        // { port: 22, service: 'ssh', account: 'root', password: '12341234' },-->
<!--      ],-->
<!--      services: [-->
<!--        { name: 'ssh', port: 22 },-->
<!--        { name: 'ftp', port: 21 },-->
<!--        { name: 'email', port: 25 },-->
<!--        { name: 'mysql', port: 3306 },-->
<!--        { name: 'web', port: 80 },-->
<!--        { name: 'cloud', port: 8080 },-->
<!--        { name: 'vpn', port: 1723 },-->
<!--        { name: 'storage', port: 2049 }-->
<!--      ],-->
<!--      //selectedService: '',-->
<!--      selectedServiceName: '',-->
<!--      selectedService: '',-->
<!--      scanTarget:'192.168.177.129'-->
<!--    };-->
<!--  },-->

<!--  methods: {-->
<!--    getServiceDetails(serviceName) {-->
<!--      return this.services.find(service => service.name === serviceName) || {};-->
<!--    },-->
<!--    validateInput(event) {-->
<!--      // 允许所有输入-->
<!--      this.scanTarget = event;-->
<!--    },-->
<!--    detect() {-->
<!--      // Check if the scanTarget is a valid IP address-->
<!--      if (!this.scanTarget) {-->
<!--        this.$message.error('请输入有效的IP地址');-->
<!--        return;-->
<!--      }-->

<!--      // Update URL to use proxy path-->
<!--      const apiUrl = '/api/getNmapIp';-->
<!--      axios.post(apiUrl, {-->
<!--        ip: this.scanTarget-->
<!--      }).then(response => {-->
<!--        // Check if the response has the expected message-->
<!--        if (response.data.message === 'Nmap scan completed and CVE data fetched.') {-->
<!--          this.$message.success('扫描完成');-->
<!--        } else {-->
<!--          this.$message.error('扫描失败，请重试');-->
<!--        }-->
<!--      }).catch(error => {-->
<!--        this.$message.error('网络错误或服务器无响应');-->
<!--        console.error('Scan error:', error);-->
<!--      });-->
<!--    },-->
<!--    serviceDetect() {-->
<!--      // 验证是否已选择服务-->
<!--      if (!this.selectedServiceName) {-->
<!--        this.$message.error('请先选择一个服务');-->
<!--        return;-->
<!--      }-->

<!--      const serviceDetails = this.getServiceDetails(this.selectedServiceName);-->

<!--      // 验证是否已输入IP地址-->
<!--      if (!this.scanTarget) {-->
<!--        this.$message.error('请输入有效的IP地址');-->
<!--        return;-->
<!--      }-->

<!--      // 构建请求数据，确保端口号为字符串-->
<!--      const postData = {-->
<!--        ip: this.scanTarget,-->
<!--        portId: serviceDetails.port.toString(), // 转换为字符串-->
<!--        service_name: serviceDetails.name-->
<!--      };-->

<!--      // 发起请求-->
<!--      axios.post('/api/getWeakPassword', postData)-->
<!--          .then(response => {-->
<!--            // 处理正常的响应-->
<!--            if (response.data && response.data.length > 0) {-->
<!--              response.data.forEach(result => {-->
<!--                this.tableData.push({-->
<!--                  port: result.port,-->
<!--                  service: result.service,-->
<!--                  account: result.login,-->
<!--                  password: result.password-->
<!--                });-->
<!--              });-->
<!--              this.$message.success('检测完成，结果已更新');-->
<!--            } else {-->
<!--              this.$message.warning('检测完成，但未发现弱口令');-->
<!--            }-->
<!--          })-->
<!--          .catch(error => {-->
<!--            // 处理网络请求错误-->
<!--            if (error.response && error.response.data && error.response.data.error) {-->
<!--              // 检查特定的错误消息-->
<!--              if (error.response.data.error === "Service not found") {-->
<!--                this.$message.error(`${error.response.data.service_name}: Service not found`);-->
<!--              } else {-->
<!--                // 通用错误处理-->
<!--                this.$message.error('检测失败，请检查网络或服务器');-->
<!--              }-->
<!--            } else {-->
<!--              this.$message.error('检测失败，请检查网络或服务器');-->
<!--            }-->
<!--            console.error('Service detect error:', error);-->
<!--          });-->
<!--    }-->
<!--  },-->
<!--  mounted() {-->

<!--  }-->
<!--}-->
<!--</script>-->

<!--<style scoped>-->
<!--.container {-->
<!--  margin: 20px;-->
<!--}-->

<!--.box-card {-->
<!--  display: flex;-->
<!--  flex-direction: column;-->
<!--  justify-content: space-between;-->
<!--  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);-->
<!--}-->

<!--.scan-button {-->
<!--  text-align: right;-->
<!--  margin-top: 10px;-->
<!--}-->


<!--</style>-->
