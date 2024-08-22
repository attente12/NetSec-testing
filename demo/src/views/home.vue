


<template>
  <div>
    这是首页
  </div>
</template>
<!--<template>-->
<!--  <el-container>-->
<!--    <el-header>-->
<!--      <h1>CPE and CVE</h1>-->
<!--    </el-header>-->
<!--    <el-main>-->
<!--      <el-row>-->
<!--        <el-col :span="24">-->
<!--          <h2>CPEs</h2>-->
<!--          <div v-for="cpe in uniqueCpes" :key="cpe" class="cpe-list">-->
<!--            {{ cpe }}-->
<!--          </div>-->
<!--        </el-col>-->
<!--      </el-row>-->
<!--      <el-row>-->
<!--        <el-col :span="24">-->
<!--          <h2>CVEs Details</h2>-->
<!--          <el-table :data="cveDetails" border stripe>-->
<!--            <el-table-column prop="cpe" label="CPE" width="250"/>-->
<!--            <el-table-column prop="cve_id" label="CVE ID" width="180"/>-->
<!--            <el-table-column prop="cvss" label="CVSS"/>-->
<!--            <el-table-column prop="pocExist" label="POC Exist"/>-->
<!--            <el-table-column prop="vulExist" label="Vulnerability Exists"/>-->
<!--            <el-table-column prop="ip_port" label="IP / Port" width="150"/>-->
<!--          </el-table>-->
<!--        </el-col>-->
<!--      </el-row>-->
<!--    </el-main>-->
<!--  </el-container>-->
<!--</template>-->

<!--<script>-->
<!--export default {-->
<!--  data() {-->
<!--    return {-->
<!--      uniqueCpes: [],-->
<!--      cveDetails: []-->
<!--    };-->
<!--  },-->
<!--  mounted() {-->
<!--    this.fetchData();-->
<!--  },-->
<!--  methods: {-->
<!--    fetchData() {-->
<!--      fetch('http://192.168.177.129:8080/cveScan') // 请替换成你的API端点-->
<!--          .then(response => {-->
<!--            if (response.ok) {-->
<!--              return response.json();-->
<!--            }-->
<!--            throw new Error('Network response was not ok.');-->
<!--          })-->
<!--          .then(data => {-->
<!--            this.extractData(data);-->
<!--          })-->
<!--          .catch(error => {-->
<!--            console.error("Error fetching data: ", error);-->
<!--          });-->
<!--    },-->
<!--    extractData(data) {-->
<!--      // 创建一个空的 Set 对象，用于存储唯一的 CPE-->
<!--      const cpesSet = new Set();-->

<!--      // 遍历输入的每个主机结果（hostResult）。-->
<!--      data.forEach(hostResult => {-->
<!--        // 检查当前主机结果中是否存在cpes字段-->
<!--        if (hostResult.cpes) {-->
<!--          // 遍历主机结果中的每个CPE-->
<!--          for (let cpe in hostResult.cpes) {-->
<!--            // 将当前 CPE 添加到cpesSet集合中-->
<!--            cpesSet.add(cpe);-->
<!--            // 遍历当前CPE下的每个CVE-->
<!--            hostResult.cpes[cpe].forEach(cve => {-->
<!--              // 将CVE详细信息添加到this.cveDetails数组中-->
<!--              this.cveDetails.push({-->
<!--                cpe: cpe,-->
<!--                cve_id: cve.CVE_id,-->
<!--                cvss: cve.CVSS,-->
<!--                pocExist: cve.pocExist ? 'Yes' : 'No',-->
<!--                vulExist: cve.vulExist,-->
<!--                ip_port: hostResult.ip-->
<!--              });-->
<!--            });-->
<!--          }-->
<!--        }-->
<!--        // 遍历主机结果中的每个端口-->
<!--        hostResult.ports.forEach(port => {-->
<!--          // 检查当前端口是否有cpes字段-->
<!--          if (port.cpes) {-->
<!--            // 遍历端口中的每个CPE-->
<!--            for (let cpe in port.cpes) {-->
<!--              // 将当前CPE添加到cpesSet集合中-->
<!--              cpesSet.add(cpe);-->

<!--              // 遍历当前CPE下的每个 CVE-->
<!--              port.cpes[cpe].forEach(cve => {-->
<!--                // 将CVE详细信息添加到this.cveDetails数组中-->
<!--                this.cveDetails.push({-->
<!--                  cpe: cpe,-->
<!--                  cve_id: cve.CVE_id,-->
<!--                  cvss: cve.CVSS,-->
<!--                  pocExist: cve.pocExist ? 'Yes' : 'No',-->
<!--                  vulExist: cve.vulExist,-->
<!--                  ip_port: `${hostResult.ip}:${port.portId}`//当前主机的IP地址及端口号-->
<!--                });-->
<!--              });-->
<!--            }-->
<!--          }-->
<!--        });-->
<!--      });-->
<!--      this.uniqueCpes = Array.from(cpesSet);//转换cpesSet为数组,使得Vue更好处理数组数据-->
<!--    }-->
<!--  }-->
<!--};-->
<!--</script>-->

<!--<style scoped>-->
<!--.cpe-list {-->
<!--  margin-bottom: 20px;-->
<!--}-->
<!--</style>-->

<!--没用element-ui的版本-->
<!--<template>-->
<!--  <div class="hello">-->
<!--    <h1>Scan Results</h1>-->
<!--    <h2>Operating Systems and CPEs</h2>-->
<!--    <div v-for="(result, index) in scanResults" :key="'result-' + index">-->
<!--      <h3>{{ result.ip }}</h3>-->
<!--      <ul>-->
<!--        <li v-for="(cves, cpe) in result.cpes" :key="cpe">-->
<!--          <button @click="toggleCPE(cpe)">{{ cpe }}</button>-->
<!--          <ul v-if="visibleCPEs.includes(cpe)">-->
<!--            <li v-for="cve in cves" :key="cve.CVE_id">-->
<!--              CVE ID: {{ cve.CVE_id }}, CVSS: {{ cve.CVSS }}, PoC Exists: {{ cve.pocExist }}, Vulnerability Exists: {{ cve.vulExist }}-->
<!--            </li>-->
<!--          </ul>-->
<!--        </li>-->
<!--      </ul>-->
<!--    </div>-->
<!--    <h2>Ports and Services</h2>-->
<!--    <div v-for="(result, index) in scanResults" :key="'ports-' + index">-->
<!--      <h3>{{ result.ip }}</h3>-->
<!--      <table>-->
<!--        <thead>-->
<!--        <tr>-->
<!--          <th>Port ID</th>-->
<!--          <th>Protocol</th>-->
<!--          <th>Status</th>-->
<!--          <th>Service</th>-->
<!--          <th>Version</th>-->
<!--          <th>CPEs</th>-->
<!--        </tr>-->
<!--        </thead>-->
<!--        <tbody>-->
<!--        <tr v-for="port in result.ports" :key="port.portId">-->
<!--          <td>{{ port.portId }}</td>-->
<!--          <td>{{ port.protocol }}</td>-->
<!--          <td>{{ port.status }}</td>-->
<!--          <td>{{ port.service_name }}</td>-->
<!--          <td>{{ port.version }}</td>-->
<!--          <td>-->
<!--            <ul>-->
<!--              <li v-for="(cves, cpe) in port.cpes" :key="cpe">-->
<!--                <button @click="toggleCPE(cpe)">{{ cpe }}</button>-->
<!--                <ul v-if="visibleCPEs.includes(cpe)">-->
<!--                  <li v-for="cve in cves" :key="cve.CVE_id">-->
<!--                    CVE ID: {{ cve.CVE_id }}, CVSS: {{ cve.CVSS }}, PoC Exists: {{ cve.pocExist }}, Vulnerability Exists: {{ cve.vulExist }}-->
<!--                  </li>-->
<!--                </ul>-->
<!--              </li>-->
<!--            </ul>-->
<!--          </td>-->
<!--        </tr>-->
<!--        </tbody>-->
<!--      </table>-->
<!--    </div>-->
<!--  </div>-->
<!--</template>-->

<!--<script>-->
<!--import axios from 'axios';-->

<!--export default {-->
<!--  name: 'HelloWorld',-->
<!--  data() {-->
<!--    return {-->
<!--      scanResults: [],-->
<!--      visibleCPEs: []-->
<!--    };-->
<!--  },-->
<!--  methods: {-->
<!--    fetchScanResults() {-->
<!--      axios.get('http://192.168.177.129:8080/cveScan')-->
<!--          .then(response => {-->
<!--            this.scanResults = response.data;-->
<!--          })-->
<!--          .catch(error => {-->
<!--            console.error("There was an error fetching the scan results:", error);-->
<!--          });-->
<!--    },-->
<!--    toggleCPE(cpe) {-->
<!--      const index = this.visibleCPEs.indexOf(cpe);-->
<!--      if (index > -1) {-->
<!--        this.visibleCPEs.splice(index, 1);-->
<!--      } else {-->
<!--        this.visibleCPEs.push(cpe);-->
<!--      }-->
<!--    }-->
<!--  },-->
<!--  mounted() {-->
<!--    this.fetchScanResults();-->
<!--  }-->
<!--}-->
<!--</script>-->

<!--<style scoped>-->
<!--button {-->
<!--  margin: 5px;-->
<!--}-->
<!--</style>-->




<!--element-ui有错误的版本-->
<!--<template>-->
<!--  <div class="hello">-->
<!--    <el-row>-->
<!--      <el-col :span="24"><h1>Scan Results</h1></el-col>-->
<!--    </el-row>-->

<!--    <el-row>-->
<!--      <el-col :span="24">-->
<!--        <h2>Operating Systems and CPEs</h2>-->
<!--        <el-collapse v-model="activeNames">-->
<!--          <el-collapse-item v-for="(result, index) in scanResults" :key="'result-' + index" :name="'result-' + index">-->
<!--            <template #title>-->
<!--              {{ result.ip }}-->
<!--            </template>-->
<!--            <ul>-->
<!--              <li v-for="(cves, cpe) in result.cpes" :key="cpe">-->
<!--                <el-button @click="toggleCPE(cpe)">{{ cpe }}</el-button>-->
<!--                <el-collapse v-if="visibleCPEs.includes(cpe)" accordion>-->
<!--                  <el-collapse-item v-for="cve in cves" :key="cve.CVE_id" :name="cve.CVE_id">-->
<!--                    <template #title>-->
<!--                      {{ cve.CVE_id }}-->
<!--                    </template>-->
<!--                    CVSS: {{ cve.CVSS }}, PoC Exists: {{ cve.pocExist ? 'Yes' : 'No' }}, Vulnerability Exists: {{ cve.vulExist }}-->
<!--                  </el-collapse-item>-->
<!--                </el-collapse>-->
<!--              </li>-->
<!--            </ul>-->
<!--          </el-collapse-item>-->
<!--        </el-collapse>-->
<!--      </el-col>-->
<!--    </el-row>-->

<!--    <el-row>-->
<!--      <el-col :span="24">-->
<!--        <h2>Ports and Services</h2>-->
<!--        <el-table :data="scanResults" style="width: 100%">-->
<!--          <el-table-column prop="ip" label="IP Address" width="180"></el-table-column>-->
<!--          <el-table-column label="Ports">-->
<!--            <template #default="scope">-->
<!--              <el-table :data="scope.row.ports" style="width: 100%">-->
<!--                <el-table-column prop="portId" label="Port ID" width="100"></el-table-column>-->
<!--                <el-table-column prop="protocol" label="Protocol" width="100"></el-table-column>-->
<!--                <el-table-column prop="status" label="Status" width="100"></el-table-column>-->
<!--                <el-table-column prop="service_name" label="Service" width="100"></el-table-column>-->
<!--                <el-table-column prop="version" label="Version" width="180"></el-table-column>-->
<!--                <el-table-column label="CPEs">-->
<!--                  <template #default="subscope">-->
<!--                    <div v-for="(cves, cpe) in subscope.row.cpes" :key="cpe">-->
<!--                      <el-button size="mini" @click="toggleCPE(cpe)">-->
<!--                        {{ cpe }}-->
<!--                      </el-button>-->
<!--                      <el-collapse v-if="visibleCPEs.includes(cpe)" accordion>-->
<!--                        <el-collapse-item v-for="cve in cves" :key="cve.CVE_id" :name="cve.CVE_id">-->
<!--                          <template #title>-->
<!--                            {{ cve.CVE_id }}-->
<!--                          </template>-->
<!--                          CVSS: {{ cve.CVSS }}, PoC Exists: {{ cve.pocExist ? 'Yes' : 'No' }}, Vulnerability Exists: {{ cve.vulExist }}-->
<!--                        </el-collapse-item>-->
<!--                      </el-collapse>-->
<!--                    </div>-->
<!--                  </template>-->

<!--                </el-table-column>-->
<!--              </el-table>-->
<!--            </template>-->
<!--          </el-table-column>-->
<!--        </el-table>-->
<!--      </el-col>-->
<!--    </el-row>-->
<!--  </div>-->
<!--</template>-->

<!--<script>-->
<!--import axios from 'axios';-->

<!--export default {-->
<!--  name: 'HelloWorld',-->
<!--  data() {-->
<!--    return {-->
<!--      scanResults: [],-->
<!--      visibleCPEs: [],-->
<!--      activeNames: []-->
<!--    };-->
<!--  },-->
<!--  methods: {-->
<!--    fetchScanResults() {-->
<!--      axios.get('http://192.168.177.129:8080/cveScan')-->
<!--          .then(response => {-->
<!--            this.scanResults = response.data;-->
<!--          })-->
<!--          .catch(error => {-->
<!--            console.error("There was an error fetching the scan results:", error);-->
<!--          });-->
<!--    },-->
<!--    toggleCPE(cpe) {-->
<!--      const index = this.visibleCPEs.indexOf(cpe);-->
<!--      if (index > -1) {-->
<!--        this.visibleCPEs.splice(index, 1);-->
<!--      } else {-->
<!--        this.visibleCPEs.push(cpe);-->
<!--      }-->
<!--    }-->
<!--  },-->
<!--  mounted() {-->
<!--    this.fetchScanResults();-->
<!--  }-->
<!--}-->
<!--</script>-->

<!--<style scoped>-->
<!--.el-collapse-item__header {-->
<!--  background-color: #f5f7fa;-->
<!--}-->
<!--</style>-->
