<template>
  <div class="vulnerability-scan-container">
    <!-- 头部区域 -->
    <div class="header-section">
      <h1 class="main-title">漏洞扫描系统</h1>
      <div class="scan-info" v-if="scanResults.length > 0">
        <el-tag type="info">
          <i class="el-icon-time"></i>
          上次扫描时间：{{ scanResults[0].scan_time || '未知' }}
        </el-tag>
      </div>
    </div>

    <!-- 目标输入区域 -->
    <el-card class="target-card" shadow="hover">
      <div slot="header" class="card-header">
        <span><i class="el-icon-aim"></i> 扫描目标</span>
      </div>

      <div class="target-content">
        <el-select
            v-model="scanTarget"
            placeholder="请输入或选择要扫描的目标，例如：192.168.177.129"
            filterable
            allow-create
            default-first-option
            class="target-select">
          <el-option
              v-for="ip in aliveHosts"
              :key="ip"
              :label="ip"
              :value="ip">
          </el-option>
        </el-select>

        <div class="scan-actions">
          <el-button
              @click="detectAll"
              :loading="detectAllState"
              icon="el-icon-full-screen"
              type="primary">
            全端口扫描
          </el-button>
          <el-button
              @click="detect"
              :loading="detectState"
              icon="el-icon-search"
              type="primary">
            标准扫描
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 操作系统识别结果 -->
    <el-card
        v-if="scanResults.length > 0"
        class="os-card"
        shadow="hover">
      <div slot="header" class="card-header">
        <span><i class="el-icon-monitor"></i> 操作系统识别</span>
      </div>

      <div class="os-content">
        <el-tabs type="border-card">
          <el-tab-pane
              v-for="(result, index) in scanResults"
              :key="'result-' + index"
              :label="'主机: ' + result.ip">

            <div class="result-section">
<!--              <div class="section-title">-->
<!--                <i class="el-icon-cpu"></i> 硬件与系统信息-->
<!--              </div>-->

<!--              <el-row :gutter="20">-->
<!--                <el-col :span="24">-->
<!--                  <div class="ip-info">-->
<!--                    <span class="label">扫描IP：</span>-->
<!--                    <el-tag size="medium">{{ result.ip }}</el-tag>-->
<!--                  </div>-->
<!--                </el-col>-->
<!--              </el-row>-->

              <div class="section-subtitle">
                <i class="el-icon-notebook-2"></i> CPE列表 (组件与产品)
              </div>

              <div class="cpe-list">
                <div v-for="(cves, cpe) in result.cpes" :key="cpe" class="cpe-item">
                  <el-button
                      size="small"
                      @click="toggleCPE(cpe)"
                      type="info"
                      plain
                      class="cpe-button">
                    <i class="el-icon-document"></i> {{ cpe }}
                  </el-button>

                  <el-collapse v-if="visibleCPEs.includes(cpe)" accordion class="cve-collapse">
                    <el-collapse-item
                        v-for="cve in cves"
                        :key="cve.Vuln_id"
                        :name="cve.Vuln_id">
                      <template #title>
                        <div class="cve-title">
                          <i class="el-icon-warning-outline"></i> {{ cve.Vuln_id }}
                          <el-tag
                              size="mini"
                              :type="getCvssTagType(cve.CVSS)"
                              class="cvss-tag">
                            CVSS: {{ cve.CVSS }}
                          </el-tag>
                        </div>
                      </template>
                      <div class="cve-details">
                        <div class="detail-item">
                          <span class="detail-label">CVSS评分:</span>
                          <span class="detail-value">{{ cve.CVSS }}</span>
                        </div>
                        <div class="detail-item">
                          <span class="detail-label">漏洞状态:</span>
                          <span class="detail-value">{{ cve.vulExist }}</span>
                        </div>
                      </div>
                    </el-collapse-item>
                  </el-collapse>
                </div>
              </div>

              <div class="section-subtitle">
                <i class="el-icon-s-platform"></i> 操作系统分类
              </div>

              <div class="os-list">
                <el-tag
                    v-for="(oslist, idx) in result.os_list"
                    :key="idx"
                    type="success"
                    effect="plain"
                    class="os-tag">
                  {{ oslist }}
                </el-tag>
              </div>

              <div class="section-subtitle">
                <i class="el-icon-s-release"></i> 操作系统版本
              </div>

              <div class="os-versions">
                <el-tag
                    v-for="(os, idx) in result.os_matches"
                    :key="idx"
                    type="primary"
                    effect="plain"
                    class="os-tag">
                  {{ os }}
                </el-tag>
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </el-card>

    <!-- 端口扫描结果 -->
    <el-card class="ports-card" shadow="hover">
      <div slot="header" class="card-header">
        <span><i class="el-icon-connection"></i> 端口扫描结果</span>
<!--        <el-button-->
<!--            @click="exportScanResults"-->
<!--            size="small"-->
<!--            icon="el-icon-download"-->
<!--            type="text"-->
<!--            v-if="scanResults.length > 0">-->
<!--          导出结果-->
<!--        </el-button>-->
      </div>

      <div class="ports-content">
        <div v-if="scanResults.length === 0" class="empty-data">
          <el-empty description="暂无扫描数据，请选择目标进行扫描"></el-empty>
        </div>

        <div v-else class="scan-summary">
          <el-alert
              title="扫描结果摘要"
              type="info"
              :closable="false"
              show-icon>
            <template #title>
              <div class="summary-content">
                <span>已扫描主机: {{ scanResults.length }} 台</span>
                <span>发现开放端口: {{ getTotalOpenPorts() }} 个</span>
                <span>潜在漏洞: {{ getTotalCves() }} 个</span>
                <span>是否全端口扫描: {{ { true: '是', false: '否' }[resultAllPorts] || '未知' }}</span>
<!--                <span>是否全端口扫描: {{ resultAllPorts }} </span>-->
              </div>
            </template>
          </el-alert>
        </div>

        <el-table
            :data="scanResults"
            style="width: 100%"
            border
            stripe
            :header-cell-style="{background:'#f5f7fa',color:'#606266'}"
            v-loading="tableLoading"
            v-if="scanResults.length > 0">
          <el-table-column prop="ip" label="IP 地址" width="150">
            <template slot-scope="scope">
              <div class="ip-cell">
                <i class="el-icon-position"></i>
                <span>{{ scope.row.ip }}</span>
              </div>
            </template>
          </el-table-column>

          <el-table-column>
            <template #header>
              <div class="ports-header">
                <i class="el-icon-s-operation"></i> 端口详情
              </div>
            </template>

            <template #default="scope">
              <el-table
                  :data="scope.row.ports"
                  style="width: 100%"
                  border
                  size="small">
                <el-table-column prop="portId" label="端口号" width="90">
                  <template slot-scope="port">
                    <el-tag size="medium" type="primary">{{ port.row.portId }}</el-tag>
                  </template>
                </el-table-column>

                <el-table-column prop="protocol" label="协议" width="80">
                  <template slot-scope="port">
                    <el-tag size="small" type="info">{{ port.row.protocol }}</el-tag>
                  </template>
                </el-table-column>

                <el-table-column prop="status" label="状态" width="90">
                  <template slot-scope="port">
                    <el-tag
                        size="small"
                        :type="port.row.status === 'open' ? 'success' : 'warning'">
                      {{ port.row.status }}
                    </el-tag>
                  </template>
                </el-table-column>

                <el-table-column prop="service_name" label="服务" width="100"></el-table-column>
<!--                <el-table-column prop="product" label="应用" width="120"></el-table-column>-->
<!--                <el-table-column prop="version" label="版本" width="120"></el-table-column>-->

                <el-table-column prop="product" label="应用" width="120">
                  <template slot-scope="scope">
                    {{ scope.row.product || '未识别' }}
                  </template>
                </el-table-column>
                <el-table-column prop="version" label="版本" width="120">
                  <template slot-scope="scope">
                    {{ scope.row.version || '未识别' }}
                  </template>
                </el-table-column>

                <el-table-column label="潜在漏洞">
                  <template #default="port">
                    <div class="port-cpes">
                      <div v-if="Object.keys(port.row.cpes || {}).length === 0" class="no-cpes">
                        <i class="el-icon-check"></i> 未发现潜在漏洞
                      </div>

                      <div
                          v-for="(cves, cpe) in port.row.cpes"
                          :key="cpe"
                          class="port-cpe-item">
                        <el-button
                            size="mini"
                            @click="toggleCPE(cpe)"
                            type="warning"
                            plain
                            class="port-cpe-button">
                          <i class="el-icon-warning"></i> {{ cpe }}
                          <span class="cve-count">({{ cves.length }}个漏洞)</span>
                        </el-button>

                        <el-collapse v-if="visibleCPEs.includes(cpe)" accordion class="port-cve-collapse">
                          <el-collapse-item
                              v-for="cve in cves"
                              :key="cve.Vuln_id"
                              :name="cve.Vuln_id">
                            <template #title>
                              <div class="port-cve-title">
                                <span>{{ cve.Vuln_id }}</span>
                                <el-tag
                                    size="mini"
                                    :type="getCvssTagType(cve.CVSS)"
                                    class="port-cvss-tag">
                                  CVSS: {{ cve.CVSS }}
                                </el-tag>
                              </div>
                            </template>

                            <div class="port-cve-details">
                              <div class="port-detail-item">
                                <span class="port-detail-label">CVSS评分:</span>
                                <span class="port-detail-value">{{ cve.CVSS }}</span>
                              </div>
                              <div class="port-detail-item">
                                <span class="port-detail-label">漏洞状态:</span>
                                <span class="port-detail-value">{{ cve.vulExist }}</span>
                              </div>
                            </div>
                          </el-collapse-item>
                        </el-collapse>
                      </div>
                    </div>
                  </template>
                </el-table-column>
              </el-table>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-card>

    <!-- 底部操作区域 -->
    <div class="footer-actions">
      <el-button
          @click="goPocVerify"
          type="primary"
          icon="el-icon-s-check"
          :disabled="scanResults.length === 0">
        去进行POC验证
      </el-button>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import { Message } from "element-ui";

export default {
  data() {
    return {
      scanResults: [],
      visibleCPEs: [],
      activeNames: [],
      scanTarget: '',
      aliveHosts: [],
      detectAllState: false,
      detectState: false,
      tableLoading: false,
      resultAllPorts:'',
    };
  },
  methods: {
    // 获取活跃IP列表
    fetchAliveHosts() {
      axios.get('/api/getAliveHosts')
          .then(response => {
            this.aliveHosts = response.data.alive_hosts;
          })
          .catch(error => {
            console.error('获取活跃IP列表失败:', error);
            Message.error('获取活跃IP列表失败');
          });
    },

    // 获取CVSS标签类型
    getCvssTagType(cvss) {
      if (!cvss) return 'info';
      const score = parseFloat(cvss);
      if (score >= 9.0) return 'danger';
      if (score >= 7.0) return 'warning';
      if (score >= 4.0) return 'info';
      return 'success';
    },

    // 获取总开放端口数
    getTotalOpenPorts() {
      let count = 0;
      this.scanResults.forEach(result => {
        count += (result.ports || []).length;
      });
      return count;
    },

    // 获取总CVE数量
    getTotalCves() {
      let count = 0;
      this.scanResults.forEach(result => {
        if (result.cpes) {
          Object.values(result.cpes).forEach(cves => {
            count += cves.length;
          });
        }
        (result.ports || []).forEach(port => {
          if (port.cpes) {
            Object.values(port.cpes).forEach(cves => {
              count += cves.length;
            });
          }
        });
      });
      return count;
    },

    // 导出扫描结果
    exportScanResults() {
      try {
        const dataStr = JSON.stringify(this.scanResults, null, 2);
        const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);

        const exportFileDefaultName = `漏洞扫描结果_${new Date().toISOString().slice(0,10)}.json`;

        const linkElement = document.createElement('a');
        linkElement.setAttribute('href', dataUri);
        linkElement.setAttribute('download', exportFileDefaultName);
        linkElement.click();

        Message.success('扫描结果已导出');
      } catch (error) {
        console.error('导出结果失败:', error);
        Message.error('导出结果失败');
      }
    },

    validateInput(event) {
      // 允许所有输入
      this.scanTarget = event;
    },

    fetchScanResults() {
      this.tableLoading = true;
      const dataStorage = localStorage.getItem('scanTarget');
      if (dataStorage) {
        this.scanTarget = JSON.parse(dataStorage);
      }

      axios.get('/api/cveScan')
          .then(response => {
            this.scanResults = response.data;
            this.resultAllPorts=response.data[0].allPorts;
            this.tableLoading = false;
          })
          .catch(error => {
            console.error("获取扫描结果失败:", error);
            this.tableLoading = false;
            Message.error('获取扫描结果失败');
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
      if (!this.scanTarget) {
        Message.warning('请先选择或输入扫描目标');
        return;
      }

      this.detectState = true;
      localStorage.setItem('scanTarget', JSON.stringify(this.scanTarget));
      const target = { ip: this.scanTarget };

      axios.post('/api/getNmapIp', target)
          .then(response => {
            console.log('扫描结果:', response.data);
            Message.success({
              message: '扫描完成，页面即将刷新',
              duration: 2000
            });

            setTimeout(() => {
              this.detectState = false;
              window.location.reload();
            }, 2000);
          })
          .catch(error => {
            this.detectState = false;
            console.error('扫描目标时出错:', error);
            Message.error('扫描失败，请重试');
          });
    },

    detectAll() {
      if (!this.scanTarget) {
        Message.warning('请先选择或输入扫描目标');
        return;
      }

      this.detectAllState = true;
      localStorage.setItem('scanTarget', JSON.stringify(this.scanTarget));

      const target = {
        ip: this.scanTarget,
        all_ports: true
      };

      axios.post('/api/getNmapIp', target)
          .then(response => {
            console.log('全端口扫描结果:', response.data);
            Message.success({
              message: '全端口扫描完成，页面即将刷新',
              duration: 2000
            });

            setTimeout(() => {
              this.detectAllState = false;
              window.location.reload();
            }, 2000);
          })
          .catch(error => {
            console.error('全端口扫描失败:', error);
            this.detectAllState = false;
            Message.error('全端口扫描失败，请重试');
          });
    },

    goPocVerify() {
      this.$nextTick(() => {
        this.$router.push('/pocScanner/pocVerify');
      });
    }
  },

  mounted() {
    this.fetchScanResults();
    this.fetchAliveHosts();
  }
}
</script>

<style scoped>
.vulnerability-scan-container {
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

.scan-info {
  display: flex;
  align-items: center;
}

.target-card, .os-card, .ports-card {
  margin-bottom: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  transition: all 0.3s;
}

.target-card:hover,
.os-card:hover,
.ports-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 16px;
  font-weight: bold;
}

.card-header i {
  margin-right: 8px;
  font-size: 18px;
}

.target-content {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.target-select {
  width: 100%;
}

.scan-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.os-content, .ports-content {
  padding: 5px 0;
}

.result-section {
  padding: 10px 0;
}

.section-title {
  font-size: 18px;
  font-weight: bold;
  color: #409EFF;
  margin-bottom: 15px;
  border-bottom: 1px solid #EBEEF5;
  padding-bottom: 10px;
}

.section-subtitle {
  font-size: 16px;
  font-weight: bold;
  color: #606266;
  margin: 20px 0 10px 0;
}

.ip-info {
  margin-bottom: 15px;
}

.ip-info .label {
  font-weight: bold;
  margin-right: 10px;
}

.cpe-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.cpe-item {
  margin-bottom: 5px;
}

.cpe-button {
  text-align: left;
  width: 100%;
  margin-bottom: 5px;
}

.cve-collapse {
  margin-left: 20px;
  margin-bottom: 10px;
}

.cve-title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.cvss-tag {
  margin-left: auto;
}

.cve-details {
  padding: 10px;
  background-color: #f8f8f8;
  border-radius: 4px;
}

.detail-item {
  margin-bottom: 5px;
}

.detail-label {
  font-weight: bold;
  margin-right: 8px;
  color: #606266;
}

.os-list, .os-versions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 10px;
}

.os-tag {
  margin-bottom: 10px;
}

.empty-data {
  padding: 30px 0;
  text-align: center;
}

.scan-summary {
  margin-bottom: 15px;
}

.summary-content {
  display: flex;
  gap: 20px;
}

.ip-cell {
  display: flex;
  align-items: center;
  gap: 5px;
}

.ports-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
}

.port-cpes {
  padding: 5px 0;
}

.no-cpes {
  color: #67C23A;
  text-align: center;
  padding: 5px;
}

.port-cpe-item {
  margin-bottom: 10px;
}

.port-cpe-button {
  text-align: left;
  width: 100%;
  margin-bottom: 5px;
}

.cve-count {
  font-size: 12px;
  color: #909399;
  margin-left: 5px;
}

.port-cve-collapse {
  margin-left: 15px;
}

.port-cve-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.port-cvss-tag {
  margin-left: 10px;
}

.port-cve-details {
  padding: 10px;
  background-color: #f8f8f8;
  border-radius: 4px;
  font-size: 12px;
}

.port-detail-item {
  margin-bottom: 5px;
}

.port-detail-label {
  font-weight: bold;
  margin-right: 8px;
  color: #606266;
}

.footer-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .scan-actions {
    flex-direction: column;
  }

  .summary-content {
    flex-direction: column;
    gap: 5px;
  }
}
</style>

<!--<template>-->
<!--  <div class="container">-->
<!--    <div class="title">-->
<!--      <h1>漏洞扫描</h1>-->
<!--      &lt;!&ndash;      <el-button size="medium" @click="goPocVerify">去进行poc验证</el-button>&ndash;&gt;-->
<!--      &lt;!&ndash;      <h1></h1>&ndash;&gt;-->
<!--      &lt;!&ndash;      <h2 style="text-align: right; font-size: 16px;">&ndash;&gt;-->
<!--      &lt;!&ndash;        上次扫描时间：{{scanResults.scan_time}}&ndash;&gt;-->
<!--      &lt;!&ndash;      </h2>&ndash;&gt;-->
<!--      <h2  v-if="scanResults.length > 0" style="text-align: right; font-size: 16px;">-->
<!--        &lt;!&ndash;        <span style="font-weight: normal;">上次扫描时间：</span><strong>2024.09.07 12:43</strong>&ndash;&gt;-->
<!--        <span style="font-weight: normal;">上次扫描时间：</span><strong>{{scanResults[0].scan_time}}</strong>-->
<!--      </h2>-->


<!--    </div>-->

<!--    <el-row :gutter="20">-->
<!--      <el-col :span="24">-->
<!--        <el-card class="box-card">-->
<!--          <div slot="header">目标</div>-->
<!--          <el-select-->
<!--              v-model="scanTarget"-->
<!--              placeholder="请输入或选择要扫描的目标，例如：192.168.177.129"-->
<!--              filterable-->
<!--              allow-create-->
<!--              default-first-option-->
<!--              style="width: 100%">-->
<!--            <el-option-->
<!--                v-for="ip in aliveHosts"-->
<!--                :key="ip"-->
<!--                :label="ip"-->
<!--                :value="ip">-->
<!--            </el-option>-->
<!--          </el-select>-->
<!--&lt;!&ndash;          <el-input&ndash;&gt;-->
<!--&lt;!&ndash;              type="textarea"&ndash;&gt;-->
<!--&lt;!&ndash;              rows="2"&ndash;&gt;-->
<!--&lt;!&ndash;              placeholder="请输入要扫描的目标，例如：192.168.177.129"&ndash;&gt;-->
<!--&lt;!&ndash;              v-model="scanTarget"&ndash;&gt;-->
<!--&lt;!&ndash;              @input="validateInput">&ndash;&gt;-->
<!--&lt;!&ndash;          </el-input>&ndash;&gt;-->
<!--          <div class="scan-button">-->
<!--&lt;!&ndash;            <el-button size="small" @click="detectAll" type="primary">全端口扫描</el-button>&ndash;&gt;-->
<!--            <el-button-->
<!--                size="small"-->
<!--                @click="detectAll"-->
<!--                :loading="detectAllState"-->
<!--                icon="el-icon-search"-->
<!--                type="primary">-->
<!--              全端口扫描-->
<!--            </el-button>-->
<!--&lt;!&ndash;            <el-button size="small" @click="detect" type="primary">扫描</el-button>&ndash;&gt;-->
<!--            <el-button-->
<!--                size="small"-->
<!--                @click="detect"-->
<!--                :loading="detectState"-->
<!--                icon="el-icon-search"-->
<!--                type="primary">-->
<!--              扫描-->
<!--            </el-button>-->
<!--          </div>-->
<!--        </el-card>-->
<!--      </el-col>-->
<!--    </el-row>-->

<!--    <el-row  v-if="scanResults.length > 0" :gutter="20" style="margin-top: 20px;">-->
<!--      <el-col :span="24">-->
<!--        <el-card class="box-card">-->
<!--          <div slot="header">操作系统识别</div>-->
<!--          <ul style="list-style-type: none; padding-left: 0;">-->
<!--            <li v-for="(result, index) in scanResults" :key="'result-' + index">-->
<!--              <div>ip：{{ result.ip }}</div>-->
<!--              &lt;!&ndash;              <div>{{result.scan_time}}</div>&ndash;&gt;-->
<!--              <br>-->
<!--              <ul style="list-style-type: none; padding-left: 20px;">-->
<!--                <li v-for="(cves, cpe) in result.cpes" :key="cpe">-->
<!--                  <el-button size="mini" @click="toggleCPE(cpe)" style="font-size: 16px;">{{ cpe }}</el-button>-->
<!--                  <el-collapse v-if="visibleCPEs.includes(cpe)" accordion>-->
<!--                    <el-collapse-item v-for="cve in cves" :key="cve.Vuln_id" :name="cve.Vuln_id">-->
<!--                      <template #title>-->
<!--                        <span style="padding-left: 30px;">{{ cve.Vuln_id }}</span>-->
<!--                      </template>-->
<!--                      <div style="color: slategrey; font-size: 12px; margin-left: 40px">-->
<!--                        CVSS: {{ cve.CVSS }}<br>-->
<!--&lt;!&ndash;                        PoC Exists: {{ cve.pocExist ? 'Yes' : 'No' }}<br>&ndash;&gt;-->
<!--                        Vulnerability Exists: {{ cve.vulExist }}<br>-->
<!--                      </div>-->
<!--                    </el-collapse-item>-->
<!--                  </el-collapse>-->
<!--                </li>-->
<!--              </ul>-->
<!--              <br>-->
<!--              <div>操作系统类别：</div>-->
<!--              <br>-->
<!--              <ul>-->
<!--                <li v-for="(oslist, index) in result.os_list" :key="index">-->
<!--                  {{ oslist }}-->
<!--                </li>-->
<!--              </ul>-->
<!--              <br>-->
<!--              <div>操作系统版本：</div>-->
<!--              <br>-->
<!--              <ul>-->
<!--                <li v-for="(os, index) in result.os_matches" :key="index">-->
<!--                  {{ os }}-->
<!--                </li>-->
<!--              </ul>-->

<!--            </li>-->
<!--          </ul>-->
<!--        </el-card>-->
<!--      </el-col>-->
<!--    </el-row>-->
<!--    <el-row :gutter="20" style="margin-top: 20px;">-->
<!--      <el-col :span="24">-->
<!--        <el-card class="box-card">-->
<!--          <div slot="header">端口扫描结果</div>-->
<!--          <el-table :data="scanResults" style="width: 100%">-->
<!--            <el-table-column prop="ip" label="IP 地址" width="150"></el-table-column>-->
<!--            <el-table-column>-->
<!--              <template #header>-->
<!--                <div style="text-align: center;">端 口</div>-->
<!--              </template>-->
<!--              <template #default="scope">-->
<!--                <el-table :data="scope.row.ports" style="width: 100%">-->
<!--                  <el-table-column prop="portId" label="端口号" width="100"></el-table-column>-->
<!--                  <el-table-column prop="protocol" label="协议" width="100"></el-table-column>-->
<!--                  <el-table-column prop="status" label="开放的状态" width="100"></el-table-column>-->
<!--                  <el-table-column prop="service_name" label="服务" width="100"></el-table-column>-->
<!--                  <el-table-column prop="product" label="应用" width="100"></el-table-column>-->
<!--                  <el-table-column prop="version" label="版本" width="180"></el-table-column>-->
<!--                  <el-table-column label="cpes与潜在CVEs对应信息">-->
<!--                    <template #default="subscope">-->
<!--                      <div v-for="(cves, cpe) in subscope.row.cpes" :key="cpe">-->
<!--                        <el-button size="mini" @click="toggleCPE(cpe)" style="font-size: 16px;">-->
<!--                          {{ cpe }}-->
<!--                        </el-button>-->
<!--                        <el-collapse v-if="visibleCPEs.includes(cpe)" accordion>-->
<!--                          <el-collapse-item v-for="cve in cves" :key="cve.Vuln_id" :name="cve.Vuln_id">-->
<!--                            <template #title>-->
<!--                              &lt;!&ndash;                              {{ cve.CVE_id }}&ndash;&gt;-->
<!--                              <span style="padding-left: 30px;">{{ cve.Vuln_id }}</span>-->
<!--                            </template>-->
<!--                            <div style="color: slategrey; font-size: 12px; margin-left: 40px">-->
<!--                              CVSS: {{ cve.CVSS }}<br>-->
<!--&lt;!&ndash;                              PoC Exists: {{ cve.pocExist ? 'Yes' : 'No' }}<br>&ndash;&gt;-->
<!--                              Vulnerability Exists: {{ cve.vulExist }}<br>-->
<!--                            </div>-->
<!--                          </el-collapse-item>-->
<!--                        </el-collapse>-->
<!--                      </div>-->
<!--                    </template>-->
<!--                  </el-table-column>-->
<!--                </el-table>-->
<!--              </template>-->
<!--            </el-table-column>-->
<!--          </el-table>-->
<!--        </el-card>-->
<!--      </el-col>-->
<!--    </el-row>-->
<!--    <h1></h1>-->
<!--    <div style="display: flex; justify-content: flex-end;">-->
<!--      <el-button size="medium" @click="goPocVerify" type="primary">去进行poc验证</el-button>-->
<!--    </div>-->
<!--  </div>-->

<!--</template>-->

<!--<script>-->
<!--import axios from "axios";-->
<!--import {Message} from "element-ui";-->

<!--export default {-->
<!--  data() {-->
<!--    return {-->
<!--      scanResults: [],-->
<!--      visibleCPEs: [],-->
<!--      activeNames: [],-->
<!--      scanTarget:'',-->
<!--      aliveHosts: [], // 新增：存储活跃IP列表-->
<!--      detectAllState: false,//检测中状态-->
<!--      detectState: false,-->
<!--    };-->
<!--  },-->
<!--  // computed: {-->
<!--  //-->
<!--  // },-->
<!--  // created() {-->
<!--  //   // 在组件创建时调用函数以从服务器获取CPE数据-->
<!--  //   this.fetchCpeData();-->
<!--  // },-->
<!--  methods: {-->
<!--    // 新增：获取活跃IP列表的方法-->
<!--    fetchAliveHosts() {-->
<!--      axios.get('/api/getAliveHosts')-->
<!--          .then(response => {-->
<!--            this.aliveHosts = response.data.alive_hosts;-->
<!--          })-->
<!--          .catch(error => {-->
<!--            console.error('获取活跃IP列表失败:', error);-->
<!--            Message.error('获取活跃IP列表失败');-->
<!--          });-->
<!--    },-->
<!--    validateInput(event) {-->
<!--      // 允许所有输入-->
<!--      this.scanTarget = event;-->
<!--    },-->
<!--    fetchScanResults() {-->
<!--      const dataStorage=localStorage.getItem('scanTarget');-->
<!--      if (dataStorage) {-->
<!--        this.scanTarget = JSON.parse(dataStorage);-->
<!--      }-->
<!--      //axios.get('http://192.168.177.129:8081/cveScan')-->
<!--      axios.get('/api/cveScan')-->
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
<!--    },-->
<!--    detect() {-->
<!--      this.detectState=true;-->
<!--      localStorage.setItem('scanTarget', JSON.stringify(this.scanTarget));-->
<!--      const target = { ip: this.scanTarget };-->
<!--      axios.post('/api/getNmapIp', target)-->
<!--          .then(response => {-->
<!--            console.log('Scan result:', response.data);-->
<!--            Message.success('扫描完成');-->
<!--            setTimeout(() => {-->
<!--              this.detectState=false;-->
<!--              window.location.reload(); // 刷新页面-->
<!--            }, 2000); // 显示提示2秒后刷新页面-->
<!--            // 在这里处理成功响应的数据-->
<!--          })-->
<!--          .catch(error => {-->
<!--            this.detectState=false;-->
<!--            console.error('There was an error scanning the target:', error);-->
<!--            // 在这里处理错误-->
<!--          });-->
<!--    },-->
<!--    detectAll() {-->
<!--      this.detectAllState=true;//检测中状态-->
<!--      localStorage.setItem('scanTarget', JSON.stringify(this.scanTarget));-->
<!--      //const target = { ip: this.scanTarget };-->
<!--      // 生成请求体，默认包含 all_ports: true-->
<!--      const target = {-->
<!--        ip: this.scanTarget,-->
<!--        all_ports: true // 默认发送 all_ports 为 true-->
<!--      };-->
<!--      axios.post('/api/getNmapIp', target)-->
<!--          .then(response => {-->
<!--            console.log('Scan result:', response.data);-->
<!--            Message.success('扫描完成');-->
<!--            setTimeout(() => {-->
<!--              this.detectAllState=false;//关闭检测中状态-->
<!--              window.location.reload(); // 刷新页面-->
<!--            }, 2000); // 显示提示2秒后刷新页面-->
<!--            // 在这里处理成功响应的数据-->
<!--          })-->
<!--          .catch(error => {-->
<!--            console.error('There was an error scanning the target:', error);-->
<!--            this.detectAllState=false;//关闭检测中状态-->
<!--            // 在这里处理错误-->
<!--          });-->
<!--    },-->
<!--    goPocVerify(){-->
<!--      this.$nextTick(() => {-->
<!--        this.$router.push('/pocScanner/pocVerify');-->
<!--      });-->
<!--    }-->
<!--  },-->
<!--  mounted() {-->
<!--    this.fetchScanResults();-->
<!--    this.fetchAliveHosts(); // 新增：组件挂载时获取活跃IP列表-->
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

<!--.failed-result {-->
<!--  color: red;-->
<!--}-->

<!--</style>-->

