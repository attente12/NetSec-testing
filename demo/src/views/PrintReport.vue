<template>
  <div class="print-report-container">
    <!-- 打印按钮 -->
    <div class="print-actions" v-show="!isPrinting">
      <el-button type="primary" @click="handlePrint" :loading="isLoading">
        <i class="el-icon-printer"></i>
        打印PDF报告
      </el-button>
    </div>

    <!-- 打印内容 - 针对PDF优化 -->
    <div ref="printContent" class="print-content" :class="{ 'print-mode': isPrinting }">
      <!-- 报告封面 -->
      <div class="report-cover">
        <div class="cover-content">
          <h1 class="report-title">网络安全评估报告</h1>
          <div class="cover-info">
            <div class="cover-item">
              <span class="cover-label">资产IP地址：</span>
              <span class="cover-value">{{ assetData.ip }}</span>
            </div>
            <div class="cover-item">
              <span class="cover-label">报告生成时间：</span>
              <span class="cover-value">{{ new Date().toLocaleString('zh-CN') }}</span>
            </div>
            <div class="cover-item" v-if="assetData.serverinfo && assetData.serverinfo.hostname">
              <span class="cover-label">主机名称：</span>
              <span class="cover-value">{{ assetData.serverinfo.hostname }}</span>
            </div>
          </div>
        </div>
        <div class="page-break"></div>
      </div>

      <!-- 目录 -->
      <div class="table-of-contents">
        <h2 class="toc-title">目录</h2>
        <div class="toc-content">
          <div class="toc-item">
            <span>1. 资产基本信息</span>
            <span class="toc-dots">.......................................</span>
            <span>3</span>
          </div>
          <div class="toc-item" v-if="assetData.baseline_summary">
            <span>2. 基线检测信息</span>
            <span class="toc-dots">.......................................</span>
            <span>4</span>
          </div>
          <div class="toc-item" v-if="assetData.level3_baseline_summary">
            <span>3. 等级保护测评信息</span>
            <span class="toc-dots">.......................................</span>
            <span>{{ assetData.baseline_summary ? '6' : '4' }}</span>
          </div>
          <div class="toc-item">
            <span>{{ getNextSectionNumber() }}. 软件资产信息</span>
            <span class="toc-dots">.......................................</span>
            <span>{{ getNextPageNumber() }}</span>
          </div>
          <div class="toc-item" v-if="weakPasswordPorts.length > 0">
            <span>{{ getNextSectionNumber() }}. 风险信息</span>
            <span class="toc-dots">.......................................</span>
            <span>{{ getNextPageNumber() }}</span>
          </div>
          <div class="toc-item">
            <span>{{ getNextSectionNumber() }}. 漏洞信息</span>
            <span class="toc-dots">.......................................</span>
            <span>{{ getNextPageNumber() }}</span>
          </div>
        </div>
        <div class="page-break"></div>
      </div>

      <!-- 1. 资产基本信息 -->
      <div class="report-section">
        <h2 class="section-title">1. 资产基本信息</h2>
        <div class="basic-info-grid">
          <div class="info-card">
            <div class="card-header">基础信息</div>
            <div class="card-content">
              <div class="info-row">
                <span class="info-label">IP地址：</span>
                <span class="info-value">{{ assetData.ip }}</span>
              </div>
              <div class="info-row" v-if="assetData.serverinfo">
                <span class="info-label">主机名：</span>
                <span class="info-value">{{ assetData.serverinfo.hostname || '未知' }}</span>
              </div>
              <div class="info-row" v-if="assetData.serverinfo">
                <span class="info-label">操作系统：</span>
                <span class="info-value">{{ assetData.serverinfo.osName || '未知' }}</span>
              </div>
              <div class="info-row" v-if="assetData.serverinfo">
                <span class="info-label">主机架构：</span>
                <span class="info-value">{{ assetData.serverinfo.arch || '未知' }}</span>
              </div>
            </div>
          </div>

          <div class="info-card">
            <div class="card-header">硬件信息</div>
            <div class="card-content">
              <div class="info-row" v-if="assetData.serverinfo">
                <span class="info-label">CPU：</span>
                <span class="info-value">{{ assetData.serverinfo.cpu || '未知' }}</span>
              </div>
              <div class="info-row" v-if="assetData.serverinfo">
                <span class="info-label">硬件型号：</span>
                <span class="info-value">{{ assetData.serverinfo.ProductName || '未知' }}</span>
              </div>
              <div class="info-row" v-if="assetData.serverinfo">
                <span class="info-label">空闲内存：</span>
                <span class="info-value">{{ assetData.serverinfo.free || '未知' }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">开放端口：</span>
                <span class="info-value">{{ formatOpenPorts }}</span>
              </div>
            </div>
          </div>
        </div>
        <div class="page-break"></div>
      </div>

      <!-- 2. 基线检测信息 -->
      <div class="report-section" v-if="assetData.baseline_summary">
        <h2 class="section-title">2. 基线检测信息</h2>

        <div class="summary-overview">
          <div class="overview-card danger-card">
            <div class="card-icon">⚠️</div>
            <div class="card-info">
              <div class="card-number">{{ assetData.baseline_summary.compliance_rate }}%</div>
              <div class="card-label">不合格率</div>
            </div>
          </div>

          <div class="overview-card info-card">
            <div class="card-icon">📊</div>
            <div class="card-info">
              <div class="card-number">{{ assetData.baseline_summary.total_checks }}</div>
              <div class="card-label">总检测项</div>
            </div>
          </div>

          <div class="overview-card success-card">
            <div class="card-icon">✅</div>
            <div class="card-info">
              <div class="card-number">{{ assetData.baseline_summary.compliant_items }}</div>
              <div class="card-label">合格项</div>
            </div>
          </div>

          <div class="overview-card danger-card">
            <div class="card-icon">❌</div>
            <div class="card-info">
              <div class="card-number">{{ assetData.baseline_summary.non_compliant_items }}</div>
              <div class="card-label">不合格项</div>
            </div>
          </div>
        </div>

        <!-- 基线检测详细表格 -->
        <div class="details-section" v-if="baselineDetails.length">
          <h3 class="subsection-title">2.1 基线检测详细信息</h3>
          <div class="table-container">
            <table class="detail-table">
              <thead>
                <tr>
                  <th class="col-status">状态</th>
                  <th class="col-item">检查项</th>
                  <th class="col-basis">检查依据</th>
                  <th class="col-result">检查结果</th>
                  <th class="col-suggest">建议</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(item, index) in baselineDetails" :key="index" :class="getRowClass(item.IsComply)">
                  <td class="status-cell">
                    <span :class="getStatusBadgeClass(item.IsComply)">
                      {{ getComplianceText(item.IsComply) }}
                    </span>
                  </td>
                  <td class="item-cell">{{ item.description }}</td>
                  <td class="basis-cell">{{ item.basis }}</td>
                  <td class="result-cell">{{ item.result }}</td>
                  <td class="suggest-cell">{{ item.IsComply === 'true' ? '-' : item.recommend }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        <div class="page-break"></div>
      </div>

      <!-- 3. 等保测评信息 -->
      <div class="report-section" v-if="assetData.level3_baseline_summary">
        <h2 class="section-title">3. 等级保护测评信息</h2>

        <!-- 等保得分展示 -->
        <div class="score-section" v-if="typeof assetData.M !== 'undefined'">
          <h3 class="subsection-title">3.1 等保测评得分</h3>
          <div class="score-display-card">
            <div class="score-circle" :class="getScoreCircleClass(assetData.M)">
              <div class="score-number">{{ assetData.M }}</div>
              <div class="score-unit">分</div>
            </div>
            <div class="score-details">
              <div class="score-grade" :class="getScoreGradeClass(assetData.M)">
                {{ getScoreGrade(assetData.M) }}
              </div>
              <div class="score-description">
                {{ getScoreDescription(assetData.M) }}
              </div>
            </div>
          </div>
        </div>

        <!-- 等保统计概览 -->
        <div class="level3-overview">
          <h3 class="subsection-title">3.2 等保检测统计</h3>
          <div class="summary-overview">
            <div class="overview-card danger-card">
              <div class="card-icon">⚠️</div>
              <div class="card-info">
                <div class="card-number">{{ assetData.level3_baseline_summary.compliance_rate }}%</div>
                <div class="card-label">不合格率</div>
              </div>
            </div>

            <div class="overview-card info-card">
              <div class="card-icon">📊</div>
              <div class="card-info">
                <div class="card-number">{{ assetData.level3_baseline_summary.total_checks }}</div>
                <div class="card-label">总检测项</div>
              </div>
            </div>

            <div class="overview-card success-card">
              <div class="card-icon">✅</div>
              <div class="card-info">
                <div class="card-number">{{ assetData.level3_baseline_summary.compliant_items }}</div>
                <div class="card-label">合格项</div>
              </div>
            </div>

            <div class="overview-card warning-card">
              <div class="card-icon">⚡</div>
              <div class="card-info">
                <div class="card-number">{{ assetData.level3_baseline_summary.half_compliant_items }}</div>
                <div class="card-label">部分合格</div>
              </div>
            </div>

            <div class="overview-card danger-card">
              <div class="card-icon">❌</div>
              <div class="card-info">
                <div class="card-number">{{ assetData.level3_baseline_summary.non_compliant_items }}</div>
                <div class="card-label">不合格项</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 等保检测详细表格 -->
        <div class="details-section" v-if="classifyDetails.length">
          <h3 class="subsection-title">3.3 等保检测详细信息</h3>
          <div class="table-container">
            <table class="detail-table">
              <thead>
                <tr>
                  <th class="col-status">状态</th>
                  <th class="col-item">检查项</th>
                  <th class="col-basis">检查依据</th>
                  <th class="col-result">检查结果</th>
                  <th class="col-suggest">建议</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(item, index) in classifyDetails" :key="index" :class="getRowClass(item.IsComply)">
                  <td class="status-cell">
                    <span :class="getStatusBadgeClass(item.IsComply)">
                      {{ getComplianceText(item.IsComply) }}
                    </span>
                  </td>
                  <td class="item-cell">{{ item.description }}</td>
                  <td class="basis-cell">{{ item.basis }}</td>
                  <td class="result-cell">{{ item.result }}</td>
                  <td class="suggest-cell">{{ item.IsComply === 'true' ? '-' : item.recommend }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- 未检查项 -->
        <div class="undo-section" v-if="assetData.undo_level3_baseline && assetData.undo_level3_baseline.length > 0">
          <h3 class="subsection-title">3.4 未检查项 ({{ assetData.undo_level3_baseline.length }}项)</h3>
          <div class="table-container">
            <table class="detail-table">
              <thead>
                <tr>
                  <th class="col-id">项目ID</th>
                  <th class="col-item">检查项</th>
                  <th class="col-level">重要级别</th>
                  <th class="col-basis">检查依据</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(item, index) in assetData.undo_level3_baseline" :key="index">
                  <td>{{ item.item_id }}</td>
                  <td>{{ item.description }}</td>
                  <td>
                    <span :class="getImportanceBadgeClass(item.important_level)">
                      {{ getLevel3ImportanceLevel(item.important_level) }}
                    </span>
                  </td>
                  <td>{{ item.basis }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        <div class="page-break"></div>
      </div>

      <!-- 软件资产信息 -->
      <div class="report-section" v-if="groupedPorts && Object.keys(groupedPorts).length > 0">
        <h2 class="section-title">{{ getSoftwareAssetSectionNumber() }}. 软件资产信息</h2>
        <div v-for="(ports, type, index) in groupedPorts" :key="type" class="asset-group">
          <h3 class="subsection-title">{{ getSoftwareAssetSectionNumber() }}.{{ index + 1 }} {{ type }}</h3>
          <div class="table-container">
            <table class="detail-table">
              <thead>
                <tr>
                  <th class="col-port">端口</th>
                  <th class="col-protocol">协议</th>
                  <th class="col-service">服务名称</th>
                  <th class="col-product">产品</th>
                  <th class="col-version">版本</th>
                  <th class="col-status">状态</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(port, portIndex) in ports" :key="portIndex">
                  <td>{{ port.port }}</td>
                  <td>{{ port.protocol }}</td>
                  <td>{{ port.service_name }}</td>
                  <td>{{ port.product || '未识别' }}</td>
                  <td>{{ port.version || '未识别' }}</td>
                  <td>
                    <span :class="getPortStatusClass(port.status)">
                      {{ port.status }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        <div class="page-break"></div>
      </div>

      <!-- 风险信息 -->
      <div class="report-section" v-if="weakPasswordPorts.length > 0">
        <h2 class="section-title">{{ getRiskSectionNumber() }}. 风险信息</h2>
        <div class="risk-alert">
          <div class="alert-icon">🚨</div>
          <div class="alert-content">
            <div class="alert-title">发现弱密码风险</div>
            <div class="alert-description">检测到 {{ weakPasswordPorts.length }} 个服务存在弱密码，建议立即修改密码。</div>
          </div>
        </div>

        <div class="table-container">
          <table class="detail-table risk-table">
            <thead>
              <tr>
                <th class="col-product">产品</th>
                <th class="col-port">端口</th>
                <th class="col-protocol">协议</th>
                <th class="col-service">服务名称</th>
                <th class="col-type">软件类型</th>
                <th class="col-account">账号</th>
                <th class="col-result">结果</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(port, index) in weakPasswordPorts" :key="index" class="risk-row">
                <td class="risk-text">{{ port.product || '未识别' }}</td>
                <td>{{ port.port }}</td>
                <td>{{ port.protocol }}</td>
                <td>{{ port.service_name }}</td>
                <td>{{ port.software_type }}</td>
                <td class="risk-text">{{ port.weak_username }}</td>
                <td class="risk-result">存在弱密码</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="page-break"></div>
      </div>

      <!-- 漏洞信息 -->
      <div class="report-section">
        <h2 class="section-title">{{ getVulnSectionNumber() }}. 漏洞信息</h2>

        <!-- 系统漏洞 -->
        <div v-if="assetData.host_vulnerabilities && assetData.host_vulnerabilities.length > 0" class="vuln-subsection">
          <h3 class="subsection-title">{{ getVulnSectionNumber() }}.1 系统漏洞</h3>
          <div class="table-container">
            <table class="detail-table vuln-table">
              <thead>
                <tr>
                  <th class="col-vuln-id">漏洞ID</th>
                  <th class="col-vuln-name">漏洞名称</th>
                  <th class="col-vuln-type">漏洞类型</th>
                  <th class="col-risk-level">风险等级</th>
                  <th class="col-description">漏洞描述</th>
                  <th class="col-exist">是否存在</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(vuln, index) in assetData.host_vulnerabilities" :key="index"
                  :class="getVulnRowClass(vuln.vulExist)">
                  <td>{{ vuln.vuln_id }}</td>
                  <td>{{ vuln.vuln_name }}</td>
                  <td>{{ vuln.vulType }}</td>
                  <td>
                    <span :class="getRiskLevelClass(vuln.cvss)">
                      {{ getRiskLevel(vuln.cvss) }}
                    </span>
                  </td>
                  <td class="description-cell">{{ vuln.summary }}</td>
                  <td>
                    <span :class="getExistStatusClass(vuln.vulExist)">
                      {{ vuln.vulExist }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- 软件资产漏洞 -->
        <div v-if="groupedPortVulnerabilities && Object.keys(groupedPortVulnerabilities).length > 0"
          class="vuln-subsection">
          <h3 class="subsection-title">{{ getVulnSectionNumber() }}.2 软件资产漏洞</h3>
          <div v-for="(vulnerabilities, type, index) in groupedPortVulnerabilities" :key="type" class="vuln-group">
            <h4 class="group-title">{{ getVulnSectionNumber() }}.2.{{ index + 1 }} {{ type }}</h4>
            <div class="table-container">
              <table class="detail-table vuln-table">
                <thead>
                  <tr>
                    <th class="col-port">端口</th>
                    <th class="col-service">服务</th>
                    <th class="col-vuln-id">漏洞ID</th>
                    <th class="col-vuln-name">漏洞名称</th>
                    <th class="col-vuln-type">漏洞类型</th>
                    <th class="col-risk-level">风险等级</th>
                    <th class="col-description">漏洞描述</th>
                    <th class="col-exist">是否存在</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(vuln, vulnIndex) in vulnerabilities" :key="vulnIndex"
                    :class="getVulnRowClass(vuln.vulExist)">
                    <td>{{ vuln.port_id }}</td>
                    <td>{{ vuln.service_name }}</td>
                    <td>{{ vuln.vuln_id }}</td>
                    <td>{{ vuln.vuln_name }}</td>
                    <td>{{ vuln.vulType }}</td>
                    <td>
                      <span :class="getRiskLevelClass(vuln.cvss)">
                        {{ getRiskLevel(vuln.cvss) }}
                      </span>
                    </td>
                    <td class="description-cell">{{ vuln.summary }}</td>
                    <td>
                      <span :class="getExistStatusClass(vuln.vulExist)">
                        {{ vuln.vulExist }}
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      <!-- 报告尾部 -->
      <div class="report-footer">
        <div class="footer-line"></div>
        <div class="footer-content">
          <div class="footer-left">
            <p><strong>网络安全评估报告</strong></p>
            <p>本报告由网络安全评估系统自动生成</p>
          </div>
          <div class="footer-right">
            <p>生成时间：{{ new Date().toLocaleString('zh-CN') }}</p>
            <p>资产IP：{{ assetData.ip }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PrintReport',
  props: {
    assetData: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      isPrinting: false,
      isLoading: false,
      baselineDetails: [],
      classifyDetails: [],
      sectionNumbers: {
        baseline: 2,
        level3: 3,
        software: 4,
        risk: 5,
        vuln: 6
      }
    }
  },
  computed: {
    formatOpenPorts() {
      if (!this.assetData || !this.assetData.ports) {
        return '无';
      }
      return this.assetData.ports
        .filter(port => port.status === 'open')
        .map(port => `${port.port}`)
        .join(', ');
    },
    groupedPorts() {
      if (!this.assetData || !this.assetData.ports) {
        return {};
      }

      const softwareTypes = ["系统工具", "Web应用", "中间件", "数据库", "操作系统", "未知类型"];
      const orderedGroups = {};

      softwareTypes.forEach(type => {
        orderedGroups[type] = [];
      });

      this.assetData.ports.forEach(port => {
        const type = port.software_type || '未知类型';
        if (softwareTypes.includes(type)) {
          orderedGroups[type].push(port);
        } else {
          orderedGroups['未知类型'].push(port);
        }
      });

      return Object.fromEntries(
        Object.entries(orderedGroups).filter(([, ports]) => ports.length > 0)
      );
    },
    groupedPortVulnerabilities() {
      if (!this.assetData || !this.assetData.port_vulnerabilities) {
        return {};
      }

      const softwareTypes = ["系统工具", "Web应用", "中间件", "数据库", "操作系统", "未知类型"];
      const orderedGroups = {};

      softwareTypes.forEach(type => {
        orderedGroups[type] = [];
      });

      this.assetData.port_vulnerabilities.forEach(vuln => {
        const type = vuln.softwareType || '未知类型';
        if (softwareTypes.includes(type)) {
          orderedGroups[type].push(vuln);
        } else {
          orderedGroups['未知类型'].push(vuln);
        }
      });

      return Object.fromEntries(
        Object.entries(orderedGroups).filter(([, vulns]) => vulns.length > 0)
      );
    },
    weakPasswordPorts() {
      if (!this.assetData || !this.assetData.ports) {
        return [];
      }
      return this.assetData.ports.filter(port =>
        port.weak_username && port.weak_password && port.verify_time
      );
    }
  },
  methods: {
    async handlePrint() {
      this.isLoading = true;

      try {
        // 获取基线检测详细信息
        if (this.assetData.baseline_summary) {
          await this.fetchBaselineDetails();
        }

        // 获取等保检测详细信息
        if (this.assetData.level3_baseline_summary) {
          await this.fetchClassifyDetails();
        }

        // 计算章节编号
        this.calculateSectionNumbers();

        // 短暂延迟确保数据渲染完成
        await this.$nextTick();
        setTimeout(() => {
          this.printReport();
          this.isLoading = false;
        }, 500);

      } catch (error) {
        console.error('获取详细信息失败:', error);
        this.isLoading = false;
        this.$message.error('获取详细信息失败，但仍可打印基本信息');
        this.printReport();
      }
    },

    async fetchBaselineDetails() {
      try {
        const response = await neoFetch(`/api/userinfo?ip=${this.assetData.ip}`);
        const data = await response.json();
        if (data && data.checkResults) {
          this.baselineDetails = data.checkResults;
        }
      } catch (error) {
        console.error('获取基线检测详细信息失败:', error);
      }
    },

    async fetchClassifyDetails() {
      try {
        const response = await neoFetch(`/api/level3Userinfo?ip=${this.assetData.ip}`);
        const data = await response.json();
        if (data && data.checkResults) {
          this.classifyDetails = data.checkResults;
        }
      } catch (error) {
        console.error('获取等保检测详细信息失败:', error);
      }
    },

    calculateSectionNumbers() {
      let currentSection = 2;

      if (this.assetData.baseline_summary) {
        this.sectionNumbers.baseline = currentSection++;
      }

      if (this.assetData.level3_baseline_summary) {
        this.sectionNumbers.level3 = currentSection++;
      }

      this.sectionNumbers.software = currentSection++;

      if (this.weakPasswordPorts.length > 0) {
        this.sectionNumbers.risk = currentSection++;
      }

      this.sectionNumbers.vuln = currentSection;
    },

    printReport() {
      this.isPrinting = true;
      this.$nextTick(() => {
        window.print();
        setTimeout(() => {
          this.isPrinting = false;
        }, 1000);
      });
    },

    // 章节编号方法
    getNextSectionNumber() {
      let section = 4;
      if (this.assetData.baseline_summary) section++;
      if (this.assetData.level3_baseline_summary) section++;
      return section;
    },

    getNextPageNumber() {
      let page = 8;
      if (this.assetData.baseline_summary) page += 2;
      if (this.assetData.level3_baseline_summary) page += 3;
      return page;
    },

    getSoftwareAssetSectionNumber() {
      return this.sectionNumbers.software;
    },

    getRiskSectionNumber() {
      return this.sectionNumbers.risk;
    },

    getVulnSectionNumber() {
      return this.sectionNumbers.vuln;
    },

    // 状态和样式方法
    getComplianceText(isComply) {
      if (isComply === 'true') return '通过';
      if (isComply === 'pending') return '待检查';
      return '不通过';
    },

    getStatusBadgeClass(isComply) {
      if (isComply === 'true') return 'status-pass';
      if (isComply === 'pending') return 'status-pending';
      return 'status-fail';
    },

    getRowClass(isComply) {
      if (isComply === 'true') return 'row-pass';
      if (isComply === 'pending') return 'row-pending';
      return 'row-fail';
    },

    getRiskLevel(score) {
      score = parseFloat(score);
      if (score >= 7.0) return '高风险';
      if (score >= 4.0) return '中风险';
      if (score >= 0.0) return '低风险';
      return '未知';
    },

    getRiskLevelClass(score) {
      score = parseFloat(score);
      if (score >= 7.0) return 'risk-high';
      if (score >= 4.0) return 'risk-medium';
      if (score >= 0.0) return 'risk-low';
      return 'risk-unknown';
    },

    getExistStatusClass(exist) {
      return exist === '存在' ? 'exist-danger' : 'exist-success';
    },

    getVulnRowClass(exist) {
      return exist === '存在' ? 'vuln-row-danger' : 'vuln-row-normal';
    },

    getPortStatusClass(status) {
      return status === 'open' ? 'port-open' : 'port-closed';
    },

    getScoreGrade(score) {
      if (score >= 90) return '优秀';
      if (score >= 80) return '良好';
      if (score >= 70) return '合格';
      if (score >= 60) return '基本符合';
      return '不符合';
    },

    getScoreGradeClass(score) {
      if (score >= 60) return 'grade-pass';
      return 'grade-fail';
    },

    getScoreCircleClass(score) {
      if (score >= 60) return 'score-circle-pass';
      return 'score-circle-fail';
    },

    getScoreDescription(score) {
      if (score >= 90) return '系统安全性优秀，符合等保要求';
      if (score >= 80) return '系统安全性良好，基本符合要求';
      if (score >= 70) return '系统安全性合格，存在部分改进空间';
      if (score >= 60) return '系统基本符合要求，需要加强安全措施';
      return '系统存在较多安全风险，需要立即整改';
    },

    getLevel3ImportanceLevel(level) {
      level = parseInt(level, 10);
      switch (level) {
        case 1: return '低';
        case 2: return '中';
        case 3: return '高';
        default: return '未知';
      }
    },

    getImportanceBadgeClass(level) {
      level = parseInt(level, 10);
      switch (level) {
        case 1: return 'importance-low';
        case 2: return 'importance-medium';
        case 3: return 'importance-high';
        default: return 'importance-unknown';
      }
    }
  }
}
</script>

<style scoped>
/* 基础容器样式 */
.print-report-container {
  width: 100%;
  font-family: 'Microsoft YaHei', 'SimSun', Arial, sans-serif;
}

.print-actions {
  margin-bottom: 20px;
  text-align: right;
}

.print-content {
  background: white;
  color: #333;
  font-size: 12px;
  line-height: 1.6;
  margin: 0 auto;
  max-width: 210mm;
}

/* 报告封面 */
.report-cover {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  margin-bottom: 0;
}

.cover-content {
  padding: 60px;
}

.report-title {
  font-size: 48px;
  font-weight: bold;
  margin-bottom: 80px;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
}

.cover-info {
  font-size: 20px;
  line-height: 2;
}

.cover-item {
  margin: 20px 0;
  padding: 15px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  backdrop-filter: blur(10px);
}

.cover-label {
  font-weight: bold;
  margin-right: 10px;
}

.cover-value {
  font-weight: normal;
}

/* 目录样式 */
.table-of-contents {
  padding: 40px;
  min-height: 80vh;
}

.toc-title {
  font-size: 32px;
  font-weight: bold;
  text-align: center;
  margin-bottom: 60px;
  color: #333;
  border-bottom: 3px solid #409EFF;
  padding-bottom: 20px;
}

.toc-content {
  max-width: 600px;
  margin: 0 auto;
}

.toc-item {
  display: flex;
  align-items: center;
  margin: 20px 0;
  font-size: 16px;
  line-height: 2;
}

.toc-item span:first-child {
  font-weight: bold;
  color: #333;
}

.toc-dots {
  flex: 1;
  text-align: center;
  color: #ccc;
  overflow: hidden;
}

.toc-item span:last-child {
  font-weight: bold;
  color: #409EFF;
  width: 30px;
  text-align: right;
}

/* 分页符 */
.page-break {
  page-break-after: always;
  height: 0;
  margin: 0;
  padding: 0;
}

/* 章节标题 */
.section-title {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin: 40px 0 30px 0;
  padding: 15px 0;
  border-bottom: 3px solid #409EFF;
  text-align: left;
}

.subsection-title {
  font-size: 18px;
  font-weight: bold;
  color: #555;
  margin: 30px 0 20px 0;
  padding-left: 15px;
  border-left: 4px solid #409EFF;
}

.group-title {
  font-size: 14px;
  font-weight: bold;
  color: #666;
  margin: 20px 0 15px 0;
  padding-left: 10px;
  border-left: 3px solid #E6A23C;
}

/* 报告区块 */
.report-section {
  margin-bottom: 40px;
  padding: 0 30px;
}

/* 基本信息卡片 */
.basic-info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
  margin: 30px 0;
}

.info-card {
  border: 2px solid #E6E6E6;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.card-header {
  background: linear-gradient(135deg, #409EFF, #66b1ff);
  color: white;
  padding: 15px 20px;
  font-weight: bold;
  font-size: 16px;
  text-align: center;
}

.card-content {
  padding: 20px;
  background: #fafafa;
}

.info-row {
  display: flex;
  margin: 12px 0;
  align-items: center;
}

.info-label {
  font-weight: bold;
  color: #666;
  width: 80px;
  flex-shrink: 0;
}

.info-value {
  color: #333;
  flex: 1;
  font-weight: 500;
}

/* 概览卡片 */
.summary-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin: 30px 0;
}

.overview-card {
  display: flex;
  align-items: center;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  min-height: 80px;
}

.overview-card.success-card {
  background: linear-gradient(135deg, #67C23A, #85ce61);
  color: white;
}

.overview-card.warning-card {
  background: linear-gradient(135deg, #E6A23C, #ebb563);
  color: white;
}

.overview-card.danger-card {
  background: linear-gradient(135deg, #F56C6C, #f78989);
  color: white;
}

.overview-card.info-card {
  background: linear-gradient(135deg, #409EFF, #66b1ff);
  color: white;
}

.card-icon {
  font-size: 32px;
  margin-right: 15px;
}

.card-info {
  flex: 1;
}

.card-number {
  font-size: 28px;
  font-weight: bold;
  line-height: 1;
}

.card-label {
  font-size: 14px;
  opacity: 0.9;
  margin-top: 5px;
}

/* 得分展示 */
.score-display-card {
  display: flex;
  align-items: center;
  background: linear-gradient(135deg, #f8f9ff, #e8f0ff);
  border: 2px solid #409EFF;
  border-radius: 16px;
  padding: 30px;
  margin: 30px 0;
  box-shadow: 0 8px 24px rgba(64, 158, 255, 0.2);
}

.score-circle {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  margin-right: 40px;
  position: relative;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
}

.score-circle-pass {
  background: linear-gradient(135deg, #67C23A, #85ce61);
  color: white;
}

.score-circle-fail {
  background: linear-gradient(135deg, #F56C6C, #f78989);
  color: white;
}

.score-number {
  font-size: 36px;
  font-weight: bold;
  line-height: 1;
}

.score-unit {
  font-size: 12px;
  opacity: 0.9;
}

.score-details {
  flex: 1;
}

.score-grade {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 10px;
}

.score-grade.grade-pass {
  color: #67C23A;
}

.score-grade.grade-fail {
  color: #F56C6C;
}

.score-description {
  font-size: 14px;
  color: #666;
  line-height: 1.8;
}

/* 风险提醒 */
.risk-alert {
  display: flex;
  align-items: center;
  background: linear-gradient(135deg, #fff2f0, #ffe6e6);
  border: 2px solid #F56C6C;
  border-radius: 12px;
  padding: 20px;
  margin: 20px 0;
}

.alert-icon {
  font-size: 32px;
  margin-right: 15px;
}

.alert-content {
  flex: 1;
}

.alert-title {
  font-size: 16px;
  font-weight: bold;
  color: #F56C6C;
  margin-bottom: 5px;
}

.alert-description {
  font-size: 14px;
  color: #666;
}

/* 表格样式 */
.table-container {
  margin: 20px 0;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.detail-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 11px;
  background: white;
}

.detail-table th {
  background: linear-gradient(135deg, #409EFF, #66b1ff);
  color: white;
  padding: 12px 8px;
  text-align: center;
  font-weight: bold;
  font-size: 11px;
  border: 1px solid #409EFF;
}

.detail-table td {
  padding: 10px 8px;
  border: 1px solid #E6E6E6;
  vertical-align: top;
  font-size: 10px;
}

.detail-table tbody tr:nth-child(even) {
  background: #fafafa;
}

.detail-table tbody tr:hover {
  background: #f0f8ff;
}

/* 表格列宽 */
.col-status {
  width: 80px;
}

.col-item {
  width: 200px;
}

.col-basis {
  width: 150px;
}

.col-result {
  width: 180px;
}

.col-suggest {
  width: auto;
}

.col-id {
  width: 80px;
}

.col-level {
  width: 80px;
}

.col-port {
  width: 60px;
}

.col-protocol {
  width: 60px;
}

.col-service {
  width: 100px;
}

.col-product {
  width: 120px;
}

.col-version {
  width: 120px;
}

.col-type {
  width: 100px;
}

.col-account {
  width: 100px;
}

.col-result {
  width: 100px;
}

.col-vuln-id {
  width: 120px;
}

.col-vuln-name {
  width: 150px;
}

.col-vuln-type {
  width: 120px;
}

.col-risk-level {
  width: 80px;
}

.col-description {
  width: auto;
}

.col-exist {
  width: 80px;
}

/* 状态标签 */
.status-pass {
  background: #67C23A;
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: bold;
}

.status-pending {
  background: #E6A23C;
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: bold;
}

.status-fail {
  background: #F56C6C;
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: bold;
}

.risk-high {
  background: #F56C6C;
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: bold;
}

.risk-medium {
  background: #E6A23C;
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: bold;
}

.risk-low {
  background: #67C23A;
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: bold;
}

.exist-danger {
  background: #F56C6C;
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: bold;
}

.exist-success {
  background: #67C23A;
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: bold;
}

.port-open {
  background: #67C23A;
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: bold;
}

.port-closed {
  background: #909399;
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: bold;
}

.importance-low {
  background: #909399;
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: bold;
}

.importance-medium {
  background: #E6A23C;
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: bold;
}

.importance-high {
  background: #F56C6C;
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: bold;
}

/* 表格行样式 */
.row-pass {
  background: rgba(103, 194, 58, 0.1);
}

.row-fail {
  background: rgba(245, 108, 108, 0.1);
}

.row-pending {
  background: rgba(230, 162, 60, 0.1);
}

.vuln-row-danger {
  background: rgba(245, 108, 108, 0.1);
  border-left: 4px solid #F56C6C;
}

.risk-row {
  background: rgba(245, 108, 108, 0.1);
  border-left: 4px solid #F56C6C;
}

.risk-text {
  color: #F56C6C;
  font-weight: bold;
}

.risk-result {
  background: #F56C6C;
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: bold;
  text-align: center;
}

.description-cell {
  max-width: 180px;
  word-wrap: break-word;
  word-break: break-all;
  line-height: 1.4;
}

/* 报告尾部 */
.report-footer {
  margin-top: 60px;
  padding: 30px;
  background: #f8f9fa;
  border-top: 3px solid #409EFF;
}

.footer-line {
  height: 2px;
  background: linear-gradient(90deg, #409EFF, #67C23A);
  margin-bottom: 20px;
}

.footer-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.footer-left,
.footer-right {
  flex: 1;
}

.footer-right {
  text-align: right;
}

.footer-content p {
  margin: 5px 0;
  color: #666;
  font-size: 12px;
}

.footer-content p strong {
  color: #333;
  font-size: 14px;
}

/* 打印模式样式 */
.print-mode {
  max-width: none !important;
  margin: 0 !important;
  padding: 0 !important;
}

/* 打印媒体查询 */
@media print {
  .print-actions {
    display: none !important;
  }

  .print-content {
    max-width: none !important;
    margin: 0 !important;
    padding: 0 !important;
    font-size: 10px !important;
    color: black !important;
    background: white !important;
  }

  .page-break {
    page-break-after: always !important;
    height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
  }

  .report-cover {
    height: 100vh !important;
    page-break-after: always !important;
  }

  .table-of-contents {
    page-break-after: always !important;
    min-height: 80vh !important;
  }

  .report-section {
    page-break-inside: avoid;
    padding: 0 15px !important;
  }

  .section-title {
    font-size: 18px !important;
    margin: 20px 0 15px 0 !important;
    page-break-after: avoid;
  }

  .subsection-title {
    font-size: 14px !important;
    margin: 15px 0 10px 0 !important;
    page-break-after: avoid;
  }

  .detail-table {
    font-size: 8px !important;
    page-break-inside: auto;
  }

  .detail-table th {
    font-size: 8px !important;
    padding: 6px 4px !important;
  }

  .detail-table td {
    font-size: 8px !important;
    padding: 4px !important;
  }

  .detail-table thead {
    display: table-header-group;
  }

  .detail-table tr {
    page-break-inside: avoid;
    page-break-after: auto;
  }

  .overview-card {
    padding: 15px !important;
    min-height: 60px !important;
  }

  .card-number {
    font-size: 20px !important;
  }

  .card-label {
    font-size: 11px !important;
  }

  .score-circle {
    width: 80px !important;
    height: 80px !important;
  }

  .score-number {
    font-size: 24px !important;
  }

  .score-grade {
    font-size: 16px !important;
  }

  .basic-info-grid {
    grid-template-columns: 1fr 1fr !important;
    gap: 15px !important;
  }

  .summary-overview {
    grid-template-columns: repeat(5, 1fr) !important;
    gap: 10px !important;
  }

  .description-cell {
    max-width: 120px !important;
    font-size: 7px !important;
  }

  /* 确保重要内容不被分页分割 */
  .score-display-card,
  .risk-alert,
  .info-card {
    page-break-inside: avoid;
  }

  /* 状态标签在打印时的样式 */
  .status-pass,
  .status-pending,
  .status-fail,
  .risk-high,
  .risk-medium,
  .risk-low,
  .exist-danger,
  .exist-success,
  .port-open,
  .port-closed,
  .importance-low,
  .importance-medium,
  .importance-high,
  .risk-result {
    -webkit-print-color-adjust: exact !important;
    color-adjust: exact !important;
    print-color-adjust: exact !important;
  }

  /* 渐变背景在打印时的处理 */
  .overview-card,
  .score-circle,
  .card-header {
    -webkit-print-color-adjust: exact !important;
    color-adjust: exact !important;
    print-color-adjust: exact !important;
  }
}
</style>