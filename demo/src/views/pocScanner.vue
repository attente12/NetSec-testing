<template>
  <div class="vulnerability-scan-container">
    <!-- 头部区域 -->
    <div class="header-section">
      <h1 class="main-title">漏洞扫描系统</h1>
    </div>

    <!-- 目标输入区域 -->
    <el-card class="target-card" shadow="hover">
      <div slot="header" class="card-header">
        <span><i class="el-icon-aim"></i> 扫描目标</span>
      </div>

      <div class="target-content">
        <el-select v-model="scanTarget" placeholder="请输入或选择要扫描的目标，例如：192.168.177.129" filterable allow-create
          default-first-option class="target-select">
          <el-option v-for="ip in aliveHosts" :key="ip" :label="ip" :value="ip">
          </el-option>
        </el-select>

        <div class="scan-actions">
          <el-button @click="detectAll" :loading="detectAllState" icon="el-icon-full-screen" type="primary">
            全端口扫描
          </el-button>
          <el-button @click="detect" :loading="detectState" icon="el-icon-search" type="primary">
            标准扫描
          </el-button>
          <el-button @click="clearScanHistory" icon="el-icon-delete" type="danger">
            清除历史记录
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 不需要单独的历史IP列表，已整合到tab中 -->

    <!-- 综合扫描结果区域 -->
    <el-card class="results-card" shadow="hover" v-if="scanResults.length > 0">
      <div slot="header" class="card-header">
        <span><i class="el-icon-data-analysis"></i> 扫描结果</span>
        <span v-if="currentViewIp" class="current-ip">当前查看: {{ currentViewIp }}</span>
      </div>

      <div class="scan-summary">
        <el-alert title="扫描结果摘要" type="info" :closable="false" show-icon>
          <template #title>
            <div class="summary-content">
              <span>已扫描主机: {{ historyIps.length }} 台</span>
            </div>
          </template>
        </el-alert>
      </div>

      <div class="results-content" v-loading="tableLoading">
        <el-tabs type="border-card" v-model="activeTabName" @tab-click="handleTabClick">
          <!-- 显示历史IP的tab -->
          <el-tab-pane v-for="ip in historyIps" :key="ip" :name="ip">
            <!-- 自定义tab标签，包含IP和删除按钮 -->
            <span slot="label" class="tab-label">
              <span class="tab-ip">主机: {{ ip }}</span>
              <i class="el-icon-close tab-close-btn" @click.stop="confirmDeleteIp(ip)" title="删除此主机">
              </i>
            </span>

            <!-- 主机摘要信息 -->
            <div class="host-summary" v-if="scanResults.length > 0">
              <el-alert type="info" :closable="false" show-icon>
                <template #title>
                  <div class="host-summary-content">
                    <span>发现开放端口: {{ (scanResults[0]?.ports || []).length }} 个</span>
                    <span>潜在漏洞: {{ scanResults[0] ? countHostCves(scanResults[0]) : 0 }} 个</span>
                    <span>是否全端口扫描: {{ { true: '是', false: '否' }[scanResults[0]?.allPorts] || '未知' }}</span>
                    <span v-if="scanResults[0]?.scan_time">
                      <i class="el-icon-time"></i>
                      扫描时间：{{ scanResults[0].scan_time }}
                    </span>
                  </div>
                </template>
              </el-alert>
            </div>

            <!-- 操作系统识别结果 -->
            <div class="section-container" v-if="scanResults.length > 0">
              <div class="section-header">
                <i class="el-icon-monitor"></i> 操作系统识别
              </div>

              <div class="section-content">
                <div class="result-section">
                  <div class="section-subtitle">
                    <i class="el-icon-notebook-2"></i> CPE列表 (组件与产品)
                  </div>

                  <div class="cpe-list">
                    <div v-for="(cves, cpe) in scanResults[0]?.cpes" :key="cpe" class="cpe-item">
                      <el-button size="small" @click="toggleCPE(cpe)" type="info" plain class="cpe-button">
                        <i class="el-icon-document"></i> {{ cpe }}
                      </el-button>

                      <el-collapse v-if="visibleCPEs.includes(cpe)" accordion class="cve-collapse">
                        <el-collapse-item v-for="cve in cves" :key="cve.Vuln_id" :name="cve.Vuln_id">
                          <template #title>
                            <div class="cve-title">
                              <i class="el-icon-warning-outline"></i> {{ cve.Vuln_id }}
                              <el-tag size="mini" :type="getCvssTagType(cve.CVSS)" class="cvss-tag">
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
                    <el-tag v-for="(oslist, idx) in scanResults[0]?.os_list" :key="idx" type="success" effect="plain"
                      class="os-tag">
                      {{ oslist }}
                    </el-tag>
                  </div>

                  <div class="section-subtitle">
                    <i class="el-icon-s-release"></i> 操作系统版本
                  </div>

                  <div class="os-versions">
                    <el-tag v-for="(os, idx) in scanResults[0]?.os_matches" :key="idx" type="primary" effect="plain"
                      class="os-tag">
                      {{ os }}
                    </el-tag>
                  </div>
                </div>
              </div>
            </div>

            <!-- 端口扫描结果 -->
            <div class="section-container" v-if="scanResults.length > 0">
              <div class="section-header">
                <i class="el-icon-connection"></i> 端口扫描结果
              </div>

              <div class="section-content">
                <el-table :data="scanResults[0]?.ports || []" style="width: 100%" border size="small">
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
                      <el-tag size="small" :type="port.row.status === 'open' ? 'success' : 'warning'">
                        {{ port.row.status }}
                      </el-tag>
                    </template>
                  </el-table-column>

                  <el-table-column prop="service_name" label="服务" width="100"></el-table-column>
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

                        <div v-for="(cves, cpe) in port.row.cpes" :key="cpe" class="port-cpe-item">
                          <el-button size="mini" @click="toggleCPE(cpe)" type="warning" plain class="port-cpe-button">
                            <i class="el-icon-warning"></i> {{ cpe }}
                            <span class="cve-count">({{ cves.length }}个漏洞)</span>
                          </el-button>

                          <el-collapse v-if="visibleCPEs.includes(cpe)" accordion class="port-cve-collapse">
                            <el-collapse-item v-for="cve in cves" :key="cve.Vuln_id" :name="cve.Vuln_id">
                              <template #title>
                                <div class="port-cve-title">
                                  <span>{{ cve.Vuln_id }}</span>
                                  <el-tag size="mini" :type="getCvssTagType(cve.CVSS)" class="port-cvss-tag">
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
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </el-card>

    <!-- 无数据时的显示 -->
    <el-card class="empty-card" shadow="hover" v-if="scanResults.length === 0">
      <div class="empty-data">
        <el-empty description="暂无扫描数据，请选择目标进行扫描"></el-empty>
      </div>
    </el-card>

    <!-- 底部操作区域 -->
    <div class="footer-actions">
      <el-button @click="goPocVerify" type="primary" icon="el-icon-s-check" :disabled="scanResults.length === 0">
        去进行POC验证
      </el-button>
    </div>
  </div>
</template>

<script>
import { Message } from "element-ui";

export default {
  data() {
    return {
      scanResults: [],
      visibleCPEs: [],
      activeNames: [],
      activeTabName: '', // 当前激活的标签页
      scanTarget: '',
      aliveHosts: [],
      historyIps: [], // 存储历史扫描过的IP
      currentViewIp: '', // 当前查看的IP
      detectAllState: false,
      detectState: false,
      tableLoading: false,
      resultAllPorts: '',
    };
  },
  methods: {
    // 确认删除IP
    confirmDeleteIp(ip) {
      this.$confirm(`确定要删除主机 ${ip} 的扫描记录吗？`, '删除确认', {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
        dangerouslyUseHTMLString: false
      }).then(() => {
        this.deleteIp(ip);
      }).catch(() => {
        // 用户取消删除
      });
    },

    // 删除IP及其相关数据
    deleteIp(ip) {
      try {
        // 从历史IP列表中移除
        const index = this.historyIps.indexOf(ip);
        if (index > -1) {
          this.historyIps.splice(index, 1);
          // 更新localStorage中的IP列表
          sessionStorage.setItem('nmapIps', JSON.stringify(this.historyIps));
        }

        // 删除该IP的扫描结果数据
        sessionStorage.removeItem(`nmapResults-${ip}`);

        // 如果删除的是当前查看的IP，需要处理当前视图
        if (this.currentViewIp === ip) {
          if (this.historyIps.length > 0) {
            // 切换到第一个可用的IP
            this.activeTabName = this.historyIps[0];
            this.loadHistoryResults(this.historyIps[0]);
          } else {
            // 没有其他IP了，清空当前视图
            this.currentViewIp = '';
            this.activeTabName = '';
            this.scanResults = [];
          }
        }

        Message.success(`主机 ${ip} 的扫描记录已删除`);
      } catch (error) {
        console.error('删除IP数据时出错:', error);
        Message.error('删除失败，请重试');
      }
    },

    // 初始化历史IP列表
    initHistoryIps() {
      const storedIps = sessionStorage.getItem('nmapIps');
      if (storedIps) {
        this.historyIps = JSON.parse(storedIps);
      }
    },

    // 保存IP到历史记录
    saveIpToHistory(ip) {
      if (!this.historyIps.includes(ip)) {
        this.historyIps.push(ip);
        sessionStorage.setItem('nmapIps', JSON.stringify(this.historyIps));
      }
    },

    // 保存扫描结果
    saveScanResult(ip, result) {
      sessionStorage.setItem(`nmapResults-${ip}`, JSON.stringify(result));
    },

    // 处理标签页点击事件
    handleTabClick(tab) {
      const ip = tab.name; // 获取IP地址（tab的name）
      this.loadHistoryResults(ip);
    },

    // 加载历史扫描结果
    loadHistoryResults(ip) {
      this.tableLoading = true;
      this.currentViewIp = ip;

      const storedResults = sessionStorage.getItem(`nmapResults-${ip}`);
      if (storedResults) {
        try {
          this.scanResults = JSON.parse(storedResults);
          this.tableLoading = false;
        } catch (error) {
          console.error('解析存储的扫描结果失败:', error);
          this.tableLoading = false;
          Message.error('加载历史扫描结果失败');
        }
      } else {
        // 如果本地没有保存，则尝试从API获取
        this.fetchScanResultsByIp(ip);
      }
    },

    // 根据特定IP获取扫描结果
    fetchScanResultsByIp(ip) {
      this.$axios.get(`/cveScan?ip=${ip}`)
        .then(response => {
          this.scanResults = response.data;
          // 保存到本地存储
          this.saveScanResult(ip, response.data);
          this.tableLoading = false;
        })
        .catch(error => {
          console.error(`获取IP ${ip} 的扫描结果失败:`, error);
          this.tableLoading = false;
          Message.error(`获取IP ${ip} 的扫描结果失败`);
        });
    },

    // 清除历史记录
    clearScanHistory() {
      this.$confirm('确定要清除所有扫描历史记录吗?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        // 清除所有历史IP
        this.historyIps.forEach(ip => {
          sessionStorage.removeItem(`nmapResults-${ip}`);
        });

        // 清除IP列表
        sessionStorage.removeItem('nmapIps');
        this.historyIps = [];

        // 清除当前视图
        if (this.currentViewIp !== '') {
          this.currentViewIp = '';
          this.scanResults = [];
        }

        Message.success('历史记录已清除');
      }).catch(() => {
        // 取消清除
      });
    },

    // 获取活跃IP列表 - 修改为从localStorage获取
    fetchAliveHosts() {
      try {
        const storedHosts = sessionStorage.getItem('hostdiscovery');
        if (storedHosts) {
          this.aliveHosts = JSON.parse(storedHosts);
        } else {
          this.aliveHosts = [];
          Message.warning('未找到存活主机列表，请先进行主机发现');
        }
      } catch (error) {
        console.error('解析sessionStorage数据失败:', error);
        this.aliveHosts = [];
        Message.error('获取存活主机列表失败');
      }
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

    // 获取主机的CVE总数
    countHostCves(hostResult) {
      let count = 0;

      // 统计主机CPE中的CVE
      if (hostResult.cpes) {
        Object.values(hostResult.cpes).forEach(cves => {
          count += cves.length;
        });
      }

      // 统计端口中的CVE
      (hostResult.ports || []).forEach(port => {
        if (port.cpes) {
          Object.values(port.cpes).forEach(cves => {
            count += cves.length;
          });
        }
      });

      return count;
    },

    validateInput(event) {
      // 允许所有输入
      this.scanTarget = event;
    },

    // 获取扫描结果
    fetchScanResults() {
      this.tableLoading = true;
      const dataStorage = sessionStorage.getItem('scanTarget');
      if (dataStorage) {
        this.scanTarget = JSON.parse(dataStorage);
      }

      this.$axios.get('/cveScan')
        .then(response => {
          this.scanResults = response.data;

          // 如果有结果，保存到历史记录
          if (response.data.length > 0) {
            const ip = response.data[0].ip;
            if (ip) {
              this.currentViewIp = ip;
              this.activeTabName = ip; // 设置当前活动标签为新扫描的IP
              this.saveIpToHistory(ip);
              this.saveScanResult(ip, response.data);
            }
          }

          this.resultAllPorts = response.data.length > 0 ? response.data[0].allPorts : '';
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
      sessionStorage.setItem('scanTarget', JSON.stringify(this.scanTarget));
      const target = { ip: this.scanTarget };

      this.$axios.post('/getNmapIp', target)
        .then(response => {
          console.log('扫描结果:', response.data);

          // 添加到历史记录
          this.saveIpToHistory(this.scanTarget);

          // 获取最新扫描结果
          this.$axios.get(`/cveScan?ip=${this.scanTarget}`)
            .then(scanResponse => {
              this.scanResults = scanResponse.data;
              this.saveScanResult(this.scanTarget, scanResponse.data);

              // 设置当前标签为新扫描的IP
              this.activeTabName = this.scanTarget;
              this.currentViewIp = this.scanTarget;

              this.detectState = false;
              Message.success('扫描完成');
            })
            .catch(error => {
              console.error('获取扫描结果失败:', error);
              this.detectState = false;
              Message.error('获取扫描结果失败');
            });
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
      sessionStorage.setItem('scanTarget', JSON.stringify(this.scanTarget));

      const target = {
        ip: this.scanTarget,
        all_ports: true
      };

      this.$axios.post('/getNmapIp', target)
        .then(response => {
          console.log('全端口扫描结果:', response.data);

          // 添加到历史记录
          this.saveIpToHistory(this.scanTarget);

          // 获取最新扫描结果
          this.$axios.get(`/cveScan?ip=${this.scanTarget}`)
            .then(scanResponse => {
              this.scanResults = scanResponse.data;
              this.saveScanResult(this.scanTarget, scanResponse.data);

              // 设置当前标签为新扫描的IP
              this.activeTabName = this.scanTarget;
              this.currentViewIp = this.scanTarget;

              this.detectAllState = false;
              Message.success('全端口扫描完成');
            })
            .catch(error => {
              console.error('获取扫描结果失败:', error);
              this.detectAllState = false;
              Message.error('获取扫描结果失败');
            });
        })
        .catch(error => {
          console.error('全端口扫描失败:', error);
          this.detectAllState = false;
          Message.error('全端口扫描失败，请重试');
        });
    },

    goPocVerify() {
      this.$nextTick(() => {
        // 传递当前查看的IP到POC验证页面
        this.$router.push({
          path: '/pocScanner/pocVerify',
          query: { ip: this.activeTabName || this.currentViewIp }
        });
      });
    },

    // 清理localStorage的方法（可以在组件销毁时调用）
    cleanupLocalStorage() {
      // 这里可以根据需要选择性清理部分数据或全部数据
      // localStorage.removeItem('nmapIps');
      // this.historyIps.forEach(ip => {
      //   localStorage.removeItem(`nmapResults-${ip}`);
      // });
    }
  },

  // 监听页面卸载事件
  beforeDestroy() {
    // 取消注释以在组件销毁时清理localStorage
    // this.cleanupLocalStorage();
  },

  mounted() {
    // 初始化历史IP列表
    this.initHistoryIps();

    if (this.historyIps.length > 0) {
      this.activeTabName = this.historyIps[0];
      this.loadHistoryResults(this.historyIps[0]);
    }

    // 如果有历史IP，加载第一个IP的结果
    // if (this.historyIps.length > 0) {
    //   this.activeTabName = this.historyIps[0];
    //   this.loadHistoryResults(this.historyIps[0]);
    // } else {
    //   this.fetchScanResults();
    // }

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

/* 自定义tab标签样式 */
.tab-label {
  display: flex;
  align-items: center;
  gap: 8px;
}

.tab-ip {
  flex: 1;
}

.tab-close-btn {
  color: #909399;
  cursor: pointer;
  padding: 2px;
  border-radius: 2px;
  transition: all 0.2s;
  font-size: 12px;
}

.tab-close-btn:hover {
  color: #f56c6c;
  background-color: #fef0f0;
}

.scan-info {
  display: flex;
  align-items: center;
}

.target-card,
.results-card,
.empty-card,
.history-card {
  margin-bottom: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  transition: all 0.3s;
}

.target-card:hover,
.results-card:hover,
.empty-card:hover,
.history-card:hover {
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

/* 历史IP标签样式 */
.history-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  padding: 10px 0;
}

.history-ip-tag {
  cursor: pointer;
  padding: 8px 12px;
  margin-bottom: 8px;
  transition: all 0.3s;
}

.history-ip-tag:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

/* 当前查看IP样式 */
.current-ip {
  font-size: 14px;
  color: #67C23A;
}

.section-container {
  margin-bottom: 25px;
  border: 1px solid #EBEEF5;
  border-radius: 4px;
  overflow: hidden;
}

.section-header {
  background-color: #f5f7fa;
  color: #409EFF;
  font-size: 16px;
  font-weight: bold;
  padding: 12px 15px;
  border-bottom: 1px solid #EBEEF5;
}

.section-content {
  padding: 15px;
}

.section-subtitle {
  font-size: 14px;
  font-weight: bold;
  color: #606266;
  margin: 15px 0 10px 0;
}

.section-subtitle:first-child {
  margin-top: 0;
}

.result-section {
  padding: 0;
}

.cpe-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
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

.os-list,
.os-versions {
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

.host-summary {
  margin-bottom: 15px;
}

.host-summary-content {
  display: flex;
  gap: 30px;
  /* 增加间距 */
}

.host-summary-content span {
  padding: 0 5px;
  /* 给每个span添加一些内部填充 */
  position: relative;
}

/* 添加分隔符，除了最后一个元素 */
.host-summary-content span:not(:last-child)::after {
  content: "";
  position: absolute;
  right: -15px;
  top: 50%;
  height: 14px;
  transform: translateY(-50%);
  border-right: 1px solid #dcdfe6;
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

  .host-summary-content {
    flex-direction: column;
    gap: 5px;
  }

  /* 在移动端移除分隔符 */
  .host-summary-content span:not(:last-child)::after {
    display: none;
  }
}
</style>