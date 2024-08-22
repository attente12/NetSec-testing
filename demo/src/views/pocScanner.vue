<template>
  <div class="container">
    <div class="title">
      <h1>漏洞扫描</h1>
    </div>

    <el-row :gutter="20">
      <el-col :span="24">
        <el-card class="box-card">
          <div slot="header">目标</div>
          <el-input
              type="textarea"
              rows="2"
              placeholder="请输入要扫描的目标，例如：192.168.177.129"
              v-model="scanTarget"
              @input="validateInput">
          </el-input>
          <div class="scan-button">
            <el-button size="small" @click="detect">扫描</el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card class="box-card">
          <div slot="header">操作系统识别</div>
          <ul style="list-style-type: none; padding-left: 0;">
            <li v-for="(result, index) in scanResults" :key="'result-' + index">
              <div>ip：{{ result.ip }}</div>
              <br>
              <ul style="list-style-type: none; padding-left: 20px;">
                <li v-for="(cves, cpe) in result.cpes" :key="cpe">
                  <el-button size="mini" @click="toggleCPE(cpe)" style="font-size: 16px;">{{ cpe }}</el-button>
                  <el-collapse v-if="visibleCPEs.includes(cpe)" accordion>
                    <el-collapse-item v-for="cve in cves" :key="cve.CVE_id" :name="cve.CVE_id">
                      <template #title>
<!--                        {{ cve.CVE_id }}-->
                        <span style="padding-left: 30px;">{{ cve.CVE_id }}</span>
                      </template>
                      <div style="color: slategrey; font-size: 12px; margin-left: 40px">
                          CVSS: {{ cve.CVSS }}<br>
                          PoC Exists: {{ cve.pocExist ? 'Yes' : 'No' }}<br>
                          Vulnerability Exists: {{ cve.vulExist }}<br>
                      </div>
                    </el-collapse-item>
                  </el-collapse>
                </li>
              </ul>
              <br>
              <div>操作系统版本：</div>
              <br>
              <ul>
                <li v-for="(os, index) in result.os_matches" :key="index">
                  {{ os }}
                </li>
              </ul>
            </li>
          </ul>
        </el-card>
      </el-col>
    </el-row>
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card class="box-card">
          <div slot="header">端口扫描结果</div>
          <el-table :data="scanResults" style="width: 100%">
            <el-table-column prop="ip" label="IP 地址" width="150"></el-table-column>
<!--            <el-table-column label="端口" >-->
            <el-table-column>
              <template #header>
                <div style="text-align: center;">端 口</div>
              </template>
              <template #default="scope">
                <el-table :data="scope.row.ports" style="width: 100%">
                  <el-table-column prop="portId" label="端口号" width="100"></el-table-column>
                  <el-table-column prop="protocol" label="协议" width="100"></el-table-column>
                  <el-table-column prop="status" label="开放的状态" width="100"></el-table-column>
                  <el-table-column prop="service_name" label="服务" width="100"></el-table-column>
                  <el-table-column prop="version" label="版本" width="180"></el-table-column>
                  <el-table-column label="cpes与潜在CVEs对应信息">
                    <template #default="subscope">
                      <div v-for="(cves, cpe) in subscope.row.cpes" :key="cpe">
                        <el-button size="mini" @click="toggleCPE(cpe)" style="font-size: 16px;">
                          {{ cpe }}
                        </el-button>
                        <el-collapse v-if="visibleCPEs.includes(cpe)" accordion>
                          <el-collapse-item v-for="cve in cves" :key="cve.CVE_id" :name="cve.CVE_id">
                            <template #title>
<!--                              {{ cve.CVE_id }}-->
                              <span style="padding-left: 30px;">{{ cve.CVE_id }}</span>
                            </template>
                            <div style="color: slategrey; font-size: 12px; margin-left: 40px">
                              CVSS: {{ cve.CVSS }}<br>
                              PoC Exists: {{ cve.pocExist ? 'Yes' : 'No' }}<br>
                              Vulnerability Exists: {{ cve.vulExist }}<br>
                            </div>
                          </el-collapse-item>
                        </el-collapse>
                      </div>
                    </template>
                  </el-table-column>
<!--                  <el-table :data="scope.row.ports" style="width: 100%">-->
<!--                    <el-collapse v-if="visibleCPEs.includes(cpe)" accordion>-->
<!--                      <el-collapse-item v-for="cve in cves" :key="cve.CVE_id" :name="cve.CVE_id">-->
<!--                        <template #title>-->
<!--                          &lt;!&ndash;                              {{ cve.CVE_id }}&ndash;&gt;-->
<!--                          <span style="padding-left: 30px;">{{ cve.CVE_id }}</span>-->
<!--                        </template>-->
<!--                        <div style="color: slategrey; font-size: 12px; margin-left: 40px">-->
<!--                          CVSS: {{ cve.CVSS }}<br>-->
<!--                          PoC Exists: {{ cve.pocExist ? 'Yes' : 'No' }}<br>-->
<!--                          Vulnerability Exists: {{ cve.vulExist }}<br>-->
<!--                        </div>-->
<!--                      </el-collapse-item>-->
<!--                    </el-collapse>-->
<!--                  </el-table>-->
                </el-table>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>

</template>

<script>
import axios from "axios";
import {Message} from "element-ui";

export default {
  data() {
    return {
      scanResults: [],
      visibleCPEs: [],
      activeNames: [],
      scanTarget:'192.168.177.129'
    };
  },
  // computed: {
  //
  // },
  // created() {
  //   // 在组件创建时调用函数以从服务器获取CPE数据
  //   this.fetchCpeData();
  // },
  methods: {
    validateInput(event) {
      // 允许所有输入
      this.scanTarget = event;
    },
    fetchScanResults() {
      //axios.get('http://192.168.177.129:8081/cveScan')
      axios.get('/api/cveScan')
          .then(response => {
            this.scanResults = response.data;
          })
          .catch(error => {
            console.error("There was an error fetching the scan results:", error);
          });
    },
    toggleCPE(cpe) {
      const index = this.visibleCPEs.indexOf(cpe);
      if (index > -1) {
        this.visibleCPEs.splice(index, 1);
      } else {
        this.visibleCPEs.push(cpe);
      }
    },
    detect() {
      const target = { ip: this.scanTarget };
      axios.post('/api/getNmapIp', target)
          .then(response => {
            console.log('Scan result:', response.data);
            Message.success('扫描完成');
            setTimeout(() => {
              window.location.reload(); // 刷新页面
            }, 2000); // 显示提示2秒后刷新页面
            // 在这里处理成功响应的数据
          })
          .catch(error => {
            console.error('There was an error scanning the target:', error);
            // 在这里处理错误
          });
    }
  },
  mounted() {
    this.fetchScanResults();
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

.failed-result {
  color: red;
}

</style>
