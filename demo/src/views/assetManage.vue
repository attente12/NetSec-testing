<template>
  <div class="vulnerability-container">
    <div class="ip-list">
      <div class="menu-header">
        <span class="title">资产</span>
        <el-badge
            :value="assets.length"
            class="asset-count"
            type="primary">
        </el-badge>
      </div>
      <el-menu
          :default-active="currentIp"
          class="ip-menu"
          @select="handleSelect">
        <el-menu-item
            v-for="asset in assets"
            :key="asset.ip"
            :index="asset.ip">
          <i class="el-icon-monitor"></i>
          <span>{{ asset.ip }}</span>
        </el-menu-item>
      </el-menu>
    </div>

    <!-- 右侧详情内容 -->
    <div class="content-area" v-if="currentAsset">
      <div class="ip-header">
        <h2>资产信息</h2>
        <div class="asset-info">
          <div class="info-item">
            <span class="label">IP地址：</span>
            <span class="value">{{ currentAsset.ip }}</span>
          </div>
          <div class="info-item">
            <span class="label">操作系统：</span>
            <span class="value">{{ currentAsset.os }}</span>
          </div>
          <div class="info-item">
            <span class="label">开放端口：</span>
<!--            <span class="value">{{ currentAsset.ports }}</span>-->
            <span class="value">{{ formatOpenPorts }}</span>
          </div>
        </div>
      </div>
      <!-- 前面的代码保持不变，直到漏洞信息标题 -->

      <!-- 新增：端口信息列表 -->
      <div class="ports-section">
        <h2>软件资产</h2>
        <div v-for="(ports, type) in groupedPorts" :key="type" class="port-group">
          <h3 class="group-title">{{ type }}</h3>
          <el-table
              :data="ports"
              border
              stripe
              :header-cell-style="{ backgroundColor: '#f5f7fa' }">
            <el-table-column prop="port" label="端口" width="80"></el-table-column>
            <el-table-column prop="protocol" label="协议" width="80"></el-table-column>
            <el-table-column prop="service_name" label="服务名称" width="120"></el-table-column>
            <el-table-column prop="product" label="产品" width="150"></el-table-column>
            <el-table-column prop="version" label="版本" width="150"></el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template slot-scope="scope">
                <el-tag :type="scope.row.status === 'open' ? 'success' : 'danger'">
                  {{ scope.row.status }}
                </el-tag>
              </template>
            </el-table-column>
<!--            &lt;!&ndash; 新增三列: 账号、弱密码和验证时间 &ndash;&gt;-->
<!--            <el-table-column prop="weak_username" label="账号" width="120"></el-table-column>-->
<!--            <el-table-column prop="weak_password" label="弱密码" width="120"></el-table-column>-->
<!--            <el-table-column prop="verify_time" label="验证时间" width="180"></el-table-column>-->
          </el-table>
        </div>
      </div>

      <!-- 新增弱口令项模块 -->
      <div class="weak-password-section">
        <h2>访问安全风险</h2>
        <el-table
            :data="weakPasswordPorts"
            border
            stripe
            :header-cell-style="{ backgroundColor: '#f5f7fa' }">
<!--          <el-table-column prop="product" label="产品" width="150"></el-table-column>-->
          <el-table-column prop="product" label="产品" width="150">
            <template slot-scope="scope">
              <span style="color: #F56C6C; font-weight: bold;">{{ scope.row.product }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="port" label="端口" width="80"></el-table-column>
          <el-table-column prop="protocol" label="协议" width="80"></el-table-column>
          <el-table-column prop="service_name" label="服务名称" width="120"></el-table-column>

          <el-table-column prop="software_type" label="软件类型" width="120"></el-table-column>
          <el-table-column prop="weak_username" label="账号" width="120">
            <template slot-scope="scope">
              <span style="color: #F56C6C; font-weight: bold;">{{ scope.row.weak_username }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="weak_password" label="弱密码" width="120">
            <template slot-scope="scope">
              <span style="color: #F56C6C; font-weight: bold;">{{ scope.row.weak_password }}</span>
            </template>
          </el-table-column>
<!--          <el-table-column prop="weak_username" label="账号" width="120"></el-table-column>-->
<!--          <el-table-column prop="weak_password" label="弱密码" width="120"></el-table-column>-->
          <el-table-column prop="verify_time" label="验证时间" width="180"></el-table-column>
        </el-table>
      </div>

      <h2 class="flex justify-between items-center">
        <span style="font-size: 18px;">资产漏洞信息</span>
        <div class="chart-toggle">
          <el-radio-group v-model="displayType" size="small">
            <el-radio-button label="assetType">按资产类型分布</el-radio-button>
            <el-radio-button label="vulType">按漏洞类型分布</el-radio-button>
          </el-radio-group>
        </div>
      </h2>

      <!-- 资产类型视图 -->
      <template v-if="displayType === 'assetType'">
        <!-- 饼图 -->
        <el-card class="chart-section">
          <div slot="header" class="clearfix">
            <span>漏洞资产类型分布</span>
          </div>
          <div class="pie-chart" ref="pieChart" style="width: 100%; height: 300px;"></div>
        </el-card>

        <!-- 主机漏洞表格 -->
        <div class="table-section">
          <h3><strong>系统漏洞</strong></h3>
          <el-table
              :data="currentAsset.host_vulnerabilities"
              border
              stripe
              :header-cell-style="{ backgroundColor: '#f5f7fa' }"
          >
            <el-table-column prop="vuln_id" label="漏洞ID" width="150"></el-table-column>
            <el-table-column prop="vuln_name" label="漏洞名称" width="150"></el-table-column>
            <el-table-column prop="vulType" label="漏洞类型" width="150"></el-table-column>
            <el-table-column prop="cvss" label="风险等级" width="120">
              <template slot-scope="scope">
                <el-tag :type="getCvssType(scope.row.cvss)">{{ getRiskLevel(scope.row.cvss) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="summary" label="漏洞描述"></el-table-column>
            <el-table-column prop="vulExist" label="是否存在" width="100">
              <template slot-scope="scope">
                <el-tag :type="scope.row.vulExist === '存在' ? 'danger' : 'success'">
                  {{ scope.row.vulExist }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- 原有的端口漏洞分组表格 -->
        <div class="table-section">
          <h3><strong>软件资产漏洞</strong></h3>
          <div v-for="(vulnerabilities, type) in groupedPortVulnerabilities"
               :key="type"
               class="vulnerability-group">
            <h4 class="group-title">{{ type }}</h4>
            <el-table
                :data="vulnerabilities"
                border
                stripe
                :header-cell-style="{ backgroundColor: '#f5f7fa' }"
            >
              <el-table-column prop="port_id" label="端口" width="70"></el-table-column>
              <el-table-column prop="service_name" label="服务名称" width="100"></el-table-column>
              <el-table-column prop="vuln_id" label="漏洞ID" width="150"></el-table-column>
              <el-table-column prop="vuln_name" label="漏洞名称" width="150"></el-table-column>
              <el-table-column prop="vulType" label="漏洞类型" width="150"></el-table-column>
              <el-table-column prop="cvss" label="风险等级" width="120">
                <template slot-scope="scope">
                  <el-tag :type="getCvssType(scope.row.cvss)">{{ getRiskLevel(scope.row.cvss) }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="summary" label="漏洞描述"></el-table-column>
              <el-table-column prop="vulExist" label="是否存在" width="100">
                <template slot-scope="scope">
                  <el-tag :type="scope.row.vulExist === '存在' ? 'danger' : 'success'">
                    {{ scope.row.vulExist }}
                  </el-tag>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>
      </template>

      <!-- 漏洞类型视图 -->
      <template v-else>
        <!-- 漏洞类型饼图 -->
        <el-card class="chart-section">
          <div slot="header" class="clearfix">
            <span>漏洞类型分布</span>
          </div>
          <div class="pie-chart" ref="vulTypePieChart" style="width: 100%; height: 300px;"></div>
        </el-card>

        <!-- 按漏洞类型分组的表格 -->
        <div class="table-section">
          <h3><strong>漏洞详情</strong></h3>
          <div v-for="(vulnerabilities, type) in groupedVulTypeVulnerabilities"
               :key="type"
               class="vulnerability-group">
            <h4 class="group-title">{{ type }}</h4>
            <el-table
                :data="vulnerabilities"
                border
                stripe
                :header-cell-style="{ backgroundColor: '#f5f7fa' }"
            >
              <el-table-column prop="vuln_id" label="漏洞ID" width="150"></el-table-column>
              <el-table-column prop="vuln_name" label="漏洞名称" width="150"></el-table-column>
              <el-table-column prop="softwareType" label="资产类型" width="150"></el-table-column>
              <el-table-column prop="service_name" label="服务名称" width="100"></el-table-column>
              <el-table-column prop="cvss" label="风险等级" width="120">
                <template slot-scope="scope">
                  <el-tag :type="getCvssType(scope.row.cvss)">{{ getRiskLevel(scope.row.cvss) }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="summary" label="漏洞描述"></el-table-column>
              <el-table-column prop="vulExist" label="是否存在" width="100">
                <template slot-scope="scope">
                  <el-tag :type="scope.row.vulExist === '存在' ? 'danger' : 'success'">
                    {{ scope.row.vulExist }}
                  </el-tag>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script>
import * as echarts from 'echarts';

export default {
  name: 'VulnerabilityTable',
  data() {
    return {
      currentIp: '',
      pieChart: null,
      vulTypePieChart: null,
      displayType: 'assetType',
      assets: [

      ],
      vulTypes: [
        "Buffer Overflow", "File Upload Vulnerability", "Code Injection",
        "SQL Injection", "Cross-Site Scripting (XSS)", "Privilege Escalation",
        "Denial of Service (DoS)", "Authentication Bypass", "Path Traversal",
        "Information Disclosure", "Cross-Site Request Forgery (CSRF)",
        "XML External Entity (XXE)", "Remote Code Execution (RCE)",
        "Session Hijacking", "Unauthorized Access"
      ],
      // 新增端口信息的软件类型分类
      softwareTypes: [
        "系统工具", "Web应用", "中间件", "数据库", "操作系统", "未知类型"
      ]
    }
  },
  computed: {
    // 原有的计算属性保持不变
    currentAsset() {
      return this.assets.find(asset => asset.ip === this.currentIp);
    },
    groupedPortVulnerabilities() {
      if (!this.currentAsset || !this.currentAsset.port_vulnerabilities) {
        return {};
      }
      return this.currentAsset.port_vulnerabilities.reduce((groups, vuln) => {
        const type = vuln.softwareType || '未分类';
        if (!groups[type]) {
          groups[type] = [];
        }
        groups[type].push(vuln);
        return groups;
      }, {});
    },
    vulnerabilityTypeStats() {
      const stats = {
        '操作系统': 0,
        'Web应用': 0,
        '系统工具': 0,
        '中间件': 0,
        '未知类型': 0
      };

      if (this.currentAsset?.host_vulnerabilities) {
        this.currentAsset.host_vulnerabilities.forEach(vuln => {
          const type = vuln.softwareType || '未知类型';
          if (Object.hasOwn(stats, type)) {
            stats[type]++;
          } else {
            stats['未知类型']++;
          }
        });
      }

      if (this.currentAsset?.port_vulnerabilities) {
        this.currentAsset.port_vulnerabilities.forEach(vuln => {
          const type = vuln.softwareType || '未知类型';
          if (Object.hasOwn(stats, type)) {
            stats[type]++;
          } else {
            stats['未知类型']++;
          }
        });
      }

      return stats;
    },
    // 新增：按漏洞类型统计
    vulTypeStats() {
      const stats = {};

      // 初始化所有漏洞类型的计数为0
      this.vulTypes.forEach(type => {
        stats[type] = 0;
      });

      // 统计主机漏洞
      if (this.currentAsset?.host_vulnerabilities) {
        this.currentAsset.host_vulnerabilities.forEach(vuln => {
          if (vuln.vulType) {
            stats[vuln.vulType] = (stats[vuln.vulType] || 0) + 1;
          }
        });
      }

      // 统计端口漏洞
      if (this.currentAsset?.port_vulnerabilities) {
        this.currentAsset.port_vulnerabilities.forEach(vuln => {
          if (vuln.vulType) {
            stats[vuln.vulType] = (stats[vuln.vulType] || 0) + 1;
          }
        });
      }

      // 只返回数量大于0的类型
      return Object.fromEntries(
          Object.entries(stats).filter(([, count]) => count > 0)
      );
    },
    // 新增：按漏洞类型分组的所有漏洞
    groupedVulTypeVulnerabilities() {
      const groups = {};

      // 合并主机漏洞和端口漏洞
      const allVulnerabilities = [
        ...(this.currentAsset?.host_vulnerabilities || []),
        ...(this.currentAsset?.port_vulnerabilities || [])
      ];

      // 按漏洞类型分组
      allVulnerabilities.forEach(vuln => {
        const type = vuln.vulType || '未分类';
        if (!groups[type]) {
          groups[type] = [];
        }
        groups[type].push(vuln);
      });

      return groups;
    },
    // 新增：提取开放端口展示在资产信息中
    formatOpenPorts() {
      if (!this.currentAsset || !this.currentAsset.ports) {
        return '无';
      }
      return this.currentAsset.ports
          .filter(port => port.status === 'open')
          // .map(port => `${port.port}/${port.protocol}`)
          .map(port => `${port.port}`)
          .join(', ');
    },
    // 新增：按软件类型分组端口信息
    groupedPorts() {
      if (!this.currentAsset || !this.currentAsset.ports) {
        return {};
      }
      return this.currentAsset.ports.reduce((groups, port) => {
        const type = port.software_type || '未知类型';
        if (!groups[type]) {
          groups[type] = [];
        }
        groups[type].push(port);
        return groups;
      }, {});
    },
    weakPasswordPorts() {
      if (!this.currentAsset || !this.currentAsset.ports) {
        return [];
      }
      return this.currentAsset.ports.filter(port =>
          port.weak_username && port.weak_password && port.verify_time
      );
    }
  },
  methods: {
    getResults() {
      fetch('/api/getAllAssetInfo')
          .then(response => response.json())
          .then(data => {
            this.assets = data;
          })
          .catch(error => console.error('Error:', error));
    },
    handleSelect(ip) {
      this.currentIp = ip;
      this.displayType = 'assetType';
      // 检查图表实例是否存在
      if (!this.pieChart || !this.pieChart.isDisposed()) {
        this.initCharts();  // 不存在或已销毁:初始化
      } else {
        this.updateCharts(); // 否则直接更新数据
      }
      // this.updateCharts();
      // this.initCharts();
      // 使用 nextTick 确保 DOM 更新后再初始化图表
      // this.$nextTick(() => {
      //   this.initCharts();  // 改用 initCharts 而不是 updateCharts
      // });
    },
    // handleSelect(ip) {
    //   this.currentIp = ip;
    //   this.displayType ='assetType';
    //   this.updateCharts();
    // },
    getCvssType(score) {
      score = parseFloat(score);
      if (score >= 7.0) return 'danger';
      if (score >= 4.0) return 'warning';
      if (score >= 0.0) return 'success';
      return 'info';
    },
    getRiskLevel(score) {
      score = parseFloat(score);
      if (score >= 7.0) return '高风险';
      if (score >= 4.0) return '中风险';
      if (score >= 0.0) return '低风险';
      return '信息';
    },
    async initCharts() {
      await this.$nextTick();

      // 初始化资产类型饼图
      if (this.$refs.pieChart) {
        if (this.pieChart) {
          this.pieChart.dispose();
        }
        this.pieChart = echarts.init(this.$refs.pieChart);
      }

      // 初始化漏洞类型饼图
      if (this.$refs.vulTypePieChart) {
        if (this.vulTypePieChart) {
          this.vulTypePieChart.dispose();
        }
        this.vulTypePieChart = echarts.init(this.$refs.vulTypePieChart);
      }

      window.addEventListener('resize', () => {
        this.pieChart && this.pieChart.resize();
        this.vulTypePieChart && this.vulTypePieChart.resize();
      });

      this.updateCharts();
    },
    updateCharts() {
      if (this.displayType === 'assetType') {
        this.updateAssetPieChart();
      } else {
        this.updateVulTypePieChart();
      }
    },
    // 原有的资产类型饼图更新方法
    updateAssetPieChart() {
      if (!this.pieChart) return;

      const stats = this.vulnerabilityTypeStats;
      const data = Object.entries(stats)
          .filter(([, value]) => value > 0)
          .map(([name, value]) => ({
            name,
            value
          }));

      const option = {
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b}: {c} ({d}%)'
        },
        legend: {
          orient: 'vertical',
          right: 'right',
          top: 'middle',
          data: data.map(item => item.name)
        },
        series: [{
          name: '资产类型分布',
          type: 'pie',
          radius: ['40%', '70%'],
          center: ['40%', '50%'],
          avoidLabelOverlap: false,
          itemStyle: {
            borderRadius: 10,
            borderColor: '#fff',
            borderWidth: 2
          },
          label: {
            show: true,
            formatter: '{b}: {c}个'
          },
          emphasis: {
            label: {
              show: true,
              fontSize: '18',
              fontWeight: 'bold'
            }
          },
          labelLine: {
            show: true
          },
          data: data
        }]
      };

      this.pieChart.setOption(option);
    },
    // 新增：漏洞类型饼图更新方法
    updateVulTypePieChart() {
      if (!this.vulTypePieChart) return;

      const stats = this.vulTypeStats;
      const data = Object.entries(stats)
          .map(([name, value]) => ({
            name,
            value
          }));

      const option = {
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b}: {c} ({d}%)'
        },
        legend: {
          orient: 'vertical',
          right: 'right',
          top: 'middle',
          data: data.map(item => item.name)
        },
        series: [{
          name: '漏洞类型分布',
          type: 'pie',
          radius: ['40%', '70%'],
          center: ['40%', '50%'],
          avoidLabelOverlap: false,
          itemStyle: {
            borderRadius: 10,
            borderColor: '#fff',
            borderWidth: 2
          },
          label: {
            show: true,
            formatter: '{b}: {c}个'
          },
          emphasis: {
            label: {
              show: true,
              fontSize: '18',
              fontWeight: 'bold'
            }
          },
          labelLine: {
            show: true
          },
          data: data
        }]
      };

      this.vulTypePieChart.setOption(option);
    }
  },
  watch: {
    currentAsset() {
      this.$nextTick(() => {
        this.updateCharts();
      });
    },
    displayType() {
      this.$nextTick(() => {
        this.initCharts();
      });
    }
  },
  // created() {
  //   this.getResults().then(() => {
  //     if (this.assets.length > 0) {
  //       this.currentIp = this.assets[0].ip;
  //       this.displayType = 'assetType';
  //       this.$nextTick(() => {
  //         this.initCharts();
  //       });
  //     }
  //   });
  // },
  created() {
    this.getResults();
  },
  mounted() {
    if (this.assets.length > 0) {
      this.currentIp = this.assets[0].ip;
    }
    this.initCharts();
  },
  beforeDestroy() {
    if (this.pieChart) {
      this.pieChart.dispose();
      this.pieChart = null;
    }
    if (this.vulTypePieChart) {
      this.vulTypePieChart.dispose();
      this.vulTypePieChart = null;
    }
  }
}
</script>

<style scoped>
.vulnerability-container {
  display: flex;
  height: 100%;
  min-height: 600px;
  background-color: #fff;
}

.ip-list {
  width: 180px;
  border-right: 1px solid #e6e6e6;
  background-color: #f5f7fa;
}

.menu-header {
  height: 50px;
  display: flex;
  align-items: center;
  padding: 0 20px;
  border-bottom: 1px solid #e6e6e6;
}

.menu-header .title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.menu-header .asset-count {
  margin-left: 10px;
}

.ip-menu {
  border-right: none;
}

.content-area {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

.empty-content {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
}

.ip-header {
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #ebeef5;
}

.ip-header h2 {
  color: #303133;
  font-size: 18px;
  font-weight: 600;
  margin: 0 0 15px 0;
}

.chart-toggle {
  margin-right: 20px;
  margin-top: 15px;
}

.chart-section {
  margin: 20px 0;
  padding: 0;
  background-color: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1);
}

.pie-chart {
  width: 100%;
  height: 400px;
}

.asset-info {
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.info-item {
  line-height: 28px;
  display: flex;
}

.info-item .label {
  color: #606266;
  width: 80px;
  text-align: right;
  margin-right: 15px;
}

.info-item .value {
  color: #303133;
  flex: 1;
}

.table-section {
  margin-bottom: 30px;
}

.table-section h3 {
  margin: 15px 0;
  color: #303133;
  font-size: 16px;
  font-weight: 500;
}

.el-tag {
  width: 65px;
  text-align: center;
}

.el-table .cell {
  text-align: center;
}

.el-table .el-table__row td:nth-child(4) .cell {
  text-align: left;
}

.vulnerability-group {
  margin-bottom: 20px;
}

.group-title {
  color: #606266;
  font-size: 14px;
  font-weight: 500;
  margin: 10px 0;
  padding-left: 10px;
  border-left: 3px solid #409EFF;
}

.port-group {
  margin-bottom: 20px;
}

.ports-section {
  margin-bottom: 30px;
}

.ports-section h2 {
  color: #303133;
  font-size: 18px;
  font-weight: 600;
  margin: 0 0 15px 0;
  padding-bottom: 10px;
  border-bottom: 1px solid #ebeef5;
}

.weak-password-section {
  margin-bottom: 30px;
}

.weak-password-section h2 {
  color: #303133;
  font-size: 18px;
  font-weight: 600;
  margin: 0 0 15px 0;
  padding-bottom: 10px;
  border-bottom: 1px solid #ebeef5;
}
</style>


<!--没有添加端口信息的代码-->
<!--<template>-->
<!--  <div class="vulnerability-container">-->
<!--    <div class="ip-list">-->
<!--      <div class="menu-header">-->
<!--        <span class="title">资产</span>-->
<!--        <el-badge-->
<!--            :value="assets.length"-->
<!--            class="asset-count"-->
<!--            type="primary">-->
<!--        </el-badge>-->
<!--      </div>-->
<!--      <el-menu-->
<!--          :default-active="currentIp"-->
<!--          class="ip-menu"-->
<!--          @select="handleSelect">-->
<!--        <el-menu-item-->
<!--            v-for="asset in assets"-->
<!--            :key="asset.ip"-->
<!--            :index="asset.ip">-->
<!--          <i class="el-icon-monitor"></i>-->
<!--          <span>{{ asset.ip }}</span>-->
<!--        </el-menu-item>-->
<!--      </el-menu>-->
<!--    </div>-->

<!--    &lt;!&ndash; 右侧详情内容 &ndash;&gt;-->
<!--    <div class="content-area" v-if="currentAsset">-->
<!--      <div class="ip-header">-->
<!--        <h2>资产信息</h2>-->
<!--        <div class="asset-info">-->
<!--          <div class="info-item">-->
<!--            <span class="label">IP地址：</span>-->
<!--            <span class="value">{{ currentAsset.ip }}</span>-->
<!--          </div>-->
<!--          <div class="info-item">-->
<!--            <span class="label">操作系统：</span>-->
<!--            <span class="value">{{ currentAsset.os }}</span>-->
<!--          </div>-->
<!--          <div class="info-item">-->
<!--            <span class="label">开放端口：</span>-->
<!--            <span class="value">{{ currentAsset.ports }}</span>-->
<!--          </div>-->
<!--        </div>-->
<!--      </div>-->
<!--      &lt;!&ndash; 前面的代码保持不变，直到漏洞信息标题 &ndash;&gt;-->

<!--      <h2 class="flex justify-between items-center">-->
<!--        <span style="font-size: 18px;">所含漏洞信息</span>-->
<!--        <div class="chart-toggle">-->
<!--          <el-radio-group v-model="displayType" size="small">-->
<!--            <el-radio-button label="assetType">按资产类型分布</el-radio-button>-->
<!--            <el-radio-button label="vulType">按漏洞类型分布</el-radio-button>-->
<!--          </el-radio-group>-->
<!--        </div>-->
<!--      </h2>-->

<!--      &lt;!&ndash; 资产类型视图 &ndash;&gt;-->
<!--      <template v-if="displayType === 'assetType'">-->
<!--        &lt;!&ndash; 饼图 &ndash;&gt;-->
<!--        <el-card class="chart-section">-->
<!--          <div slot="header" class="clearfix">-->
<!--            <span>漏洞资产类型分布</span>-->
<!--          </div>-->
<!--          <div class="pie-chart" ref="pieChart" style="width: 100%; height: 300px;"></div>-->
<!--        </el-card>-->

<!--        &lt;!&ndash; 主机漏洞表格 &ndash;&gt;-->
<!--        <div class="table-section">-->
<!--          <h3><strong>系统漏洞</strong></h3>-->
<!--          <el-table-->
<!--              :data="currentAsset.host_vulnerabilities"-->
<!--              border-->
<!--              stripe-->
<!--              :header-cell-style="{ backgroundColor: '#f5f7fa' }"-->
<!--          >-->
<!--            <el-table-column prop="vuln_id" label="漏洞ID" width="150"></el-table-column>-->
<!--            <el-table-column prop="vuln_name" label="漏洞名称" width="150"></el-table-column>-->
<!--            <el-table-column prop="vulType" label="漏洞类型" width="150"></el-table-column>-->
<!--            <el-table-column prop="cvss" label="风险等级" width="120">-->
<!--              <template slot-scope="scope">-->
<!--                <el-tag :type="getCvssType(scope.row.cvss)">{{ getRiskLevel(scope.row.cvss) }}</el-tag>-->
<!--              </template>-->
<!--            </el-table-column>-->
<!--            <el-table-column prop="summary" label="漏洞描述"></el-table-column>-->
<!--            <el-table-column prop="vulExist" label="是否存在" width="100">-->
<!--              <template slot-scope="scope">-->
<!--                <el-tag :type="scope.row.vulExist === '存在' ? 'danger' : 'success'">-->
<!--                  {{ scope.row.vulExist }}-->
<!--                </el-tag>-->
<!--              </template>-->
<!--            </el-table-column>-->
<!--          </el-table>-->
<!--        </div>-->

<!--        &lt;!&ndash; 原有的端口漏洞分组表格 &ndash;&gt;-->
<!--        <div class="table-section">-->
<!--          <h3><strong>软件资产漏洞</strong></h3>-->
<!--          <div v-for="(vulnerabilities, type) in groupedPortVulnerabilities"-->
<!--               :key="type"-->
<!--               class="vulnerability-group">-->
<!--            <h4 class="group-title">{{ type }}</h4>-->
<!--            <el-table-->
<!--                :data="vulnerabilities"-->
<!--                border-->
<!--                stripe-->
<!--                :header-cell-style="{ backgroundColor: '#f5f7fa' }"-->
<!--            >-->
<!--              <el-table-column prop="port_id" label="端口" width="70"></el-table-column>-->
<!--              <el-table-column prop="service_name" label="服务名称" width="100"></el-table-column>-->
<!--              <el-table-column prop="vuln_id" label="漏洞ID" width="150"></el-table-column>-->
<!--              <el-table-column prop="vuln_name" label="漏洞名称" width="150"></el-table-column>-->
<!--              <el-table-column prop="vulType" label="漏洞类型" width="150"></el-table-column>-->
<!--              <el-table-column prop="cvss" label="风险等级" width="120">-->
<!--                <template slot-scope="scope">-->
<!--                  <el-tag :type="getCvssType(scope.row.cvss)">{{ getRiskLevel(scope.row.cvss) }}</el-tag>-->
<!--                </template>-->
<!--              </el-table-column>-->
<!--              <el-table-column prop="summary" label="漏洞描述"></el-table-column>-->
<!--              <el-table-column prop="vulExist" label="是否存在" width="100">-->
<!--                <template slot-scope="scope">-->
<!--                  <el-tag :type="scope.row.vulExist === '存在' ? 'danger' : 'success'">-->
<!--                    {{ scope.row.vulExist }}-->
<!--                  </el-tag>-->
<!--                </template>-->
<!--              </el-table-column>-->
<!--            </el-table>-->
<!--          </div>-->
<!--        </div>-->
<!--      </template>-->

<!--      &lt;!&ndash; 漏洞类型视图 &ndash;&gt;-->
<!--      <template v-else>-->
<!--        &lt;!&ndash; 漏洞类型饼图 &ndash;&gt;-->
<!--        <el-card class="chart-section">-->
<!--          <div slot="header" class="clearfix">-->
<!--            <span>漏洞类型分布</span>-->
<!--          </div>-->
<!--          <div class="pie-chart" ref="vulTypePieChart" style="width: 100%; height: 300px;"></div>-->
<!--        </el-card>-->

<!--        &lt;!&ndash; 按漏洞类型分组的表格 &ndash;&gt;-->
<!--        <div class="table-section">-->
<!--          <h3><strong>漏洞详情</strong></h3>-->
<!--          <div v-for="(vulnerabilities, type) in groupedVulTypeVulnerabilities"-->
<!--               :key="type"-->
<!--               class="vulnerability-group">-->
<!--            <h4 class="group-title">{{ type }}</h4>-->
<!--            <el-table-->
<!--                :data="vulnerabilities"-->
<!--                border-->
<!--                stripe-->
<!--                :header-cell-style="{ backgroundColor: '#f5f7fa' }"-->
<!--            >-->
<!--              <el-table-column prop="vuln_id" label="漏洞ID" width="150"></el-table-column>-->
<!--              <el-table-column prop="vuln_name" label="漏洞名称" width="150"></el-table-column>-->
<!--              <el-table-column prop="softwareType" label="资产类型" width="150"></el-table-column>-->
<!--              <el-table-column prop="service_name" label="服务名称" width="100"></el-table-column>-->
<!--              <el-table-column prop="cvss" label="风险等级" width="120">-->
<!--                <template slot-scope="scope">-->
<!--                  <el-tag :type="getCvssType(scope.row.cvss)">{{ getRiskLevel(scope.row.cvss) }}</el-tag>-->
<!--                </template>-->
<!--              </el-table-column>-->
<!--              <el-table-column prop="summary" label="漏洞描述"></el-table-column>-->
<!--              <el-table-column prop="vulExist" label="是否存在" width="100">-->
<!--                <template slot-scope="scope">-->
<!--                  <el-tag :type="scope.row.vulExist === '存在' ? 'danger' : 'success'">-->
<!--                    {{ scope.row.vulExist }}-->
<!--                  </el-tag>-->
<!--                </template>-->
<!--              </el-table-column>-->
<!--            </el-table>-->
<!--          </div>-->
<!--        </div>-->
<!--      </template>-->
<!--    </div>-->
<!--  </div>-->
<!--</template>-->

<!--<script>-->
<!--import * as echarts from 'echarts';-->

<!--export default {-->
<!--  name: 'VulnerabilityTable',-->
<!--  data() {-->
<!--    return {-->
<!--      currentIp: '',-->
<!--      pieChart: null,-->
<!--      vulTypePieChart: null,-->
<!--      displayType: 'assetType',-->
<!--      assets: [-->

<!--      ],-->
<!--      vulTypes: [-->
<!--        "Buffer Overflow", "File Upload Vulnerability", "Code Injection",-->
<!--        "SQL Injection", "Cross-Site Scripting (XSS)", "Privilege Escalation",-->
<!--        "Denial of Service (DoS)", "Authentication Bypass", "Path Traversal",-->
<!--        "Information Disclosure", "Cross-Site Request Forgery (CSRF)",-->
<!--        "XML External Entity (XXE)", "Remote Code Execution (RCE)",-->
<!--        "Session Hijacking", "Unauthorized Access"-->
<!--      ]-->
<!--    }-->
<!--  },-->
<!--  computed: {-->
<!--    // 原有的计算属性保持不变-->
<!--    currentAsset() {-->
<!--      return this.assets.find(asset => asset.ip === this.currentIp);-->
<!--    },-->
<!--    groupedPortVulnerabilities() {-->
<!--      if (!this.currentAsset || !this.currentAsset.port_vulnerabilities) {-->
<!--        return {};-->
<!--      }-->
<!--      return this.currentAsset.port_vulnerabilities.reduce((groups, vuln) => {-->
<!--        const type = vuln.softwareType || '未分类';-->
<!--        if (!groups[type]) {-->
<!--          groups[type] = [];-->
<!--        }-->
<!--        groups[type].push(vuln);-->
<!--        return groups;-->
<!--      }, {});-->
<!--    },-->
<!--    vulnerabilityTypeStats() {-->
<!--      const stats = {-->
<!--        '操作系统': 0,-->
<!--        'Web应用': 0,-->
<!--        '系统工具': 0,-->
<!--        '中间件': 0,-->
<!--        '未知类型': 0-->
<!--      };-->

<!--      if (this.currentAsset?.host_vulnerabilities) {-->
<!--        this.currentAsset.host_vulnerabilities.forEach(vuln => {-->
<!--          const type = vuln.softwareType || '未知类型';-->
<!--          if (Object.hasOwn(stats, type)) {-->
<!--            stats[type]++;-->
<!--          } else {-->
<!--            stats['未知类型']++;-->
<!--          }-->
<!--        });-->
<!--      }-->

<!--      if (this.currentAsset?.port_vulnerabilities) {-->
<!--        this.currentAsset.port_vulnerabilities.forEach(vuln => {-->
<!--          const type = vuln.softwareType || '未知类型';-->
<!--          if (Object.hasOwn(stats, type)) {-->
<!--            stats[type]++;-->
<!--          } else {-->
<!--            stats['未知类型']++;-->
<!--          }-->
<!--        });-->
<!--      }-->

<!--      return stats;-->
<!--    },-->
<!--    // 新增：按漏洞类型统计-->
<!--    vulTypeStats() {-->
<!--      const stats = {};-->

<!--      // 初始化所有漏洞类型的计数为0-->
<!--      this.vulTypes.forEach(type => {-->
<!--        stats[type] = 0;-->
<!--      });-->

<!--      // 统计主机漏洞-->
<!--      if (this.currentAsset?.host_vulnerabilities) {-->
<!--        this.currentAsset.host_vulnerabilities.forEach(vuln => {-->
<!--          if (vuln.vulType) {-->
<!--            stats[vuln.vulType] = (stats[vuln.vulType] || 0) + 1;-->
<!--          }-->
<!--        });-->
<!--      }-->

<!--      // 统计端口漏洞-->
<!--      if (this.currentAsset?.port_vulnerabilities) {-->
<!--        this.currentAsset.port_vulnerabilities.forEach(vuln => {-->
<!--          if (vuln.vulType) {-->
<!--            stats[vuln.vulType] = (stats[vuln.vulType] || 0) + 1;-->
<!--          }-->
<!--        });-->
<!--      }-->

<!--      // 只返回数量大于0的类型-->
<!--      return Object.fromEntries(-->
<!--          Object.entries(stats).filter(([, count]) => count > 0)-->
<!--      );-->
<!--    },-->
<!--    // 新增：按漏洞类型分组的所有漏洞-->
<!--    groupedVulTypeVulnerabilities() {-->
<!--      const groups = {};-->

<!--      // 合并主机漏洞和端口漏洞-->
<!--      const allVulnerabilities = [-->
<!--        ...(this.currentAsset?.host_vulnerabilities || []),-->
<!--        ...(this.currentAsset?.port_vulnerabilities || [])-->
<!--      ];-->

<!--      // 按漏洞类型分组-->
<!--      allVulnerabilities.forEach(vuln => {-->
<!--        const type = vuln.vulType || '未分类';-->
<!--        if (!groups[type]) {-->
<!--          groups[type] = [];-->
<!--        }-->
<!--        groups[type].push(vuln);-->
<!--      });-->

<!--      return groups;-->
<!--    }-->
<!--  },-->
<!--  methods: {-->
<!--    getResults() {-->
<!--      fetch('/api/getAllAssetsVulnData')-->
<!--          .then(response => response.json())-->
<!--          .then(data => {-->
<!--            this.assets = data;-->
<!--          })-->
<!--          .catch(error => console.error('Error:', error));-->
<!--    },-->
<!--    handleSelect(ip) {-->
<!--      this.currentIp = ip;-->
<!--      this.displayType = 'assetType';-->
<!--      // 检查图表实例是否存在-->
<!--      if (!this.pieChart || !this.pieChart.isDisposed()) {-->
<!--        this.initCharts();  // 不存在或已销毁:初始化-->
<!--      } else {-->
<!--        this.updateCharts(); // 否则直接更新数据-->
<!--      }-->
<!--      // this.updateCharts();-->
<!--      // this.initCharts();-->
<!--      // 使用 nextTick 确保 DOM 更新后再初始化图表-->
<!--      // this.$nextTick(() => {-->
<!--      //   this.initCharts();  // 改用 initCharts 而不是 updateCharts-->
<!--      // });-->
<!--    },-->
<!--    // handleSelect(ip) {-->
<!--    //   this.currentIp = ip;-->
<!--    //   this.displayType ='assetType';-->
<!--    //   this.updateCharts();-->
<!--    // },-->
<!--    getCvssType(score) {-->
<!--      score = parseFloat(score);-->
<!--      if (score >= 7.0) return 'danger';-->
<!--      if (score >= 4.0) return 'warning';-->
<!--      if (score >= 0.0) return 'success';-->
<!--      return 'info';-->
<!--    },-->
<!--    getRiskLevel(score) {-->
<!--      score = parseFloat(score);-->
<!--      if (score >= 7.0) return '高风险';-->
<!--      if (score >= 4.0) return '中风险';-->
<!--      if (score >= 0.0) return '低风险';-->
<!--      return '信息';-->
<!--    },-->
<!--    async initCharts() {-->
<!--      await this.$nextTick();-->

<!--      // 初始化资产类型饼图-->
<!--      if (this.$refs.pieChart) {-->
<!--        if (this.pieChart) {-->
<!--          this.pieChart.dispose();-->
<!--        }-->
<!--        this.pieChart = echarts.init(this.$refs.pieChart);-->
<!--      }-->

<!--      // 初始化漏洞类型饼图-->
<!--      if (this.$refs.vulTypePieChart) {-->
<!--        if (this.vulTypePieChart) {-->
<!--          this.vulTypePieChart.dispose();-->
<!--        }-->
<!--        this.vulTypePieChart = echarts.init(this.$refs.vulTypePieChart);-->
<!--      }-->

<!--      window.addEventListener('resize', () => {-->
<!--        this.pieChart && this.pieChart.resize();-->
<!--        this.vulTypePieChart && this.vulTypePieChart.resize();-->
<!--      });-->

<!--      this.updateCharts();-->
<!--    },-->
<!--    updateCharts() {-->
<!--      if (this.displayType === 'assetType') {-->
<!--        this.updateAssetPieChart();-->
<!--      } else {-->
<!--        this.updateVulTypePieChart();-->
<!--      }-->
<!--    },-->
<!--    // 原有的资产类型饼图更新方法-->
<!--    updateAssetPieChart() {-->
<!--      if (!this.pieChart) return;-->

<!--      const stats = this.vulnerabilityTypeStats;-->
<!--      const data = Object.entries(stats)-->
<!--          .filter(([, value]) => value > 0)-->
<!--          .map(([name, value]) => ({-->
<!--            name,-->
<!--            value-->
<!--          }));-->

<!--      const option = {-->
<!--        tooltip: {-->
<!--          trigger: 'item',-->
<!--          formatter: '{a} <br/>{b}: {c} ({d}%)'-->
<!--        },-->
<!--        legend: {-->
<!--          orient: 'vertical',-->
<!--          right: 'right',-->
<!--          top: 'middle',-->
<!--          data: data.map(item => item.name)-->
<!--        },-->
<!--        series: [{-->
<!--          name: '资产类型分布',-->
<!--          type: 'pie',-->
<!--          radius: ['40%', '70%'],-->
<!--          center: ['40%', '50%'],-->
<!--          avoidLabelOverlap: false,-->
<!--          itemStyle: {-->
<!--            borderRadius: 10,-->
<!--            borderColor: '#fff',-->
<!--            borderWidth: 2-->
<!--          },-->
<!--          label: {-->
<!--            show: true,-->
<!--            formatter: '{b}: {c}个'-->
<!--          },-->
<!--          emphasis: {-->
<!--            label: {-->
<!--              show: true,-->
<!--              fontSize: '18',-->
<!--              fontWeight: 'bold'-->
<!--            }-->
<!--          },-->
<!--          labelLine: {-->
<!--            show: true-->
<!--          },-->
<!--          data: data-->
<!--        }]-->
<!--      };-->

<!--      this.pieChart.setOption(option);-->
<!--    },-->
<!--    // 新增：漏洞类型饼图更新方法-->
<!--    updateVulTypePieChart() {-->
<!--      if (!this.vulTypePieChart) return;-->

<!--      const stats = this.vulTypeStats;-->
<!--      const data = Object.entries(stats)-->
<!--          .map(([name, value]) => ({-->
<!--            name,-->
<!--            value-->
<!--          }));-->

<!--      const option = {-->
<!--        tooltip: {-->
<!--          trigger: 'item',-->
<!--          formatter: '{a} <br/>{b}: {c} ({d}%)'-->
<!--        },-->
<!--        legend: {-->
<!--          orient: 'vertical',-->
<!--          right: 'right',-->
<!--          top: 'middle',-->
<!--          data: data.map(item => item.name)-->
<!--        },-->
<!--        series: [{-->
<!--          name: '漏洞类型分布',-->
<!--          type: 'pie',-->
<!--          radius: ['40%', '70%'],-->
<!--          center: ['40%', '50%'],-->
<!--          avoidLabelOverlap: false,-->
<!--          itemStyle: {-->
<!--            borderRadius: 10,-->
<!--            borderColor: '#fff',-->
<!--            borderWidth: 2-->
<!--          },-->
<!--          label: {-->
<!--            show: true,-->
<!--            formatter: '{b}: {c}个'-->
<!--          },-->
<!--          emphasis: {-->
<!--            label: {-->
<!--              show: true,-->
<!--              fontSize: '18',-->
<!--              fontWeight: 'bold'-->
<!--            }-->
<!--          },-->
<!--          labelLine: {-->
<!--            show: true-->
<!--          },-->
<!--          data: data-->
<!--        }]-->
<!--      };-->

<!--      this.vulTypePieChart.setOption(option);-->
<!--    }-->
<!--  },-->
<!--  watch: {-->
<!--    currentAsset() {-->
<!--      this.$nextTick(() => {-->
<!--        this.updateCharts();-->
<!--      });-->
<!--    },-->
<!--    displayType() {-->
<!--      this.$nextTick(() => {-->
<!--        this.initCharts();-->
<!--      });-->
<!--    }-->
<!--  },-->
<!--  // created() {-->
<!--  //   this.getResults().then(() => {-->
<!--  //     if (this.assets.length > 0) {-->
<!--  //       this.currentIp = this.assets[0].ip;-->
<!--  //       this.displayType = 'assetType';-->
<!--  //       this.$nextTick(() => {-->
<!--  //         this.initCharts();-->
<!--  //       });-->
<!--  //     }-->
<!--  //   });-->
<!--  // },-->
<!--  created() {-->
<!--    this.getResults();-->
<!--  },-->
<!--  mounted() {-->
<!--    if (this.assets.length > 0) {-->
<!--      this.currentIp = this.assets[0].ip;-->
<!--    }-->
<!--    this.initCharts();-->
<!--  },-->
<!--  beforeDestroy() {-->
<!--    if (this.pieChart) {-->
<!--      this.pieChart.dispose();-->
<!--      this.pieChart = null;-->
<!--    }-->
<!--    if (this.vulTypePieChart) {-->
<!--      this.vulTypePieChart.dispose();-->
<!--      this.vulTypePieChart = null;-->
<!--    }-->
<!--  }-->
<!--}-->
<!--</script>-->

<!--<style scoped>-->
<!--.vulnerability-container {-->
<!--  display: flex;-->
<!--  height: 100%;-->
<!--  min-height: 600px;-->
<!--  background-color: #fff;-->
<!--}-->

<!--.ip-list {-->
<!--  width: 180px;-->
<!--  border-right: 1px solid #e6e6e6;-->
<!--  background-color: #f5f7fa;-->
<!--}-->

<!--.menu-header {-->
<!--  height: 50px;-->
<!--  display: flex;-->
<!--  align-items: center;-->
<!--  padding: 0 20px;-->
<!--  border-bottom: 1px solid #e6e6e6;-->
<!--}-->

<!--.menu-header .title {-->
<!--  font-size: 16px;-->
<!--  font-weight: 600;-->
<!--  color: #303133;-->
<!--}-->

<!--.menu-header .asset-count {-->
<!--  margin-left: 10px;-->
<!--}-->

<!--.ip-menu {-->
<!--  border-right: none;-->
<!--}-->

<!--.content-area {-->
<!--  flex: 1;-->
<!--  padding: 20px;-->
<!--  overflow-y: auto;-->
<!--}-->

<!--.empty-content {-->
<!--  flex: 1;-->
<!--  display: flex;-->
<!--  justify-content: center;-->
<!--  align-items: center;-->
<!--}-->

<!--.ip-header {-->
<!--  margin-bottom: 20px;-->
<!--  padding-bottom: 10px;-->
<!--  border-bottom: 1px solid #ebeef5;-->
<!--}-->

<!--.ip-header h2 {-->
<!--  color: #303133;-->
<!--  font-size: 18px;-->
<!--  font-weight: 600;-->
<!--  margin: 0 0 15px 0;-->
<!--}-->

<!--.chart-toggle {-->
<!--  margin-right: 20px;-->
<!--  margin-top: 15px;-->
<!--}-->

<!--.chart-section {-->
<!--  margin: 20px 0;-->
<!--  padding: 0;-->
<!--  background-color: #fff;-->
<!--  border-radius: 4px;-->
<!--  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1);-->
<!--}-->

<!--.pie-chart {-->
<!--  width: 100%;-->
<!--  height: 400px;-->
<!--}-->

<!--.asset-info {-->
<!--  padding: 15px;-->
<!--  background-color: #f5f7fa;-->
<!--  border-radius: 4px;-->
<!--}-->

<!--.info-item {-->
<!--  line-height: 28px;-->
<!--  display: flex;-->
<!--}-->

<!--.info-item .label {-->
<!--  color: #606266;-->
<!--  width: 80px;-->
<!--  text-align: right;-->
<!--  margin-right: 15px;-->
<!--}-->

<!--.info-item .value {-->
<!--  color: #303133;-->
<!--  flex: 1;-->
<!--}-->

<!--.table-section {-->
<!--  margin-bottom: 30px;-->
<!--}-->

<!--.table-section h3 {-->
<!--  margin: 15px 0;-->
<!--  color: #303133;-->
<!--  font-size: 16px;-->
<!--  font-weight: 500;-->
<!--}-->

<!--.el-tag {-->
<!--  width: 65px;-->
<!--  text-align: center;-->
<!--}-->

<!--.el-table .cell {-->
<!--  text-align: center;-->
<!--}-->

<!--.el-table .el-table__row td:nth-child(4) .cell {-->
<!--  text-align: left;-->
<!--}-->

<!--.vulnerability-group {-->
<!--  margin-bottom: 20px;-->
<!--}-->

<!--.group-title {-->
<!--  color: #606266;-->
<!--  font-size: 14px;-->
<!--  font-weight: 500;-->
<!--  margin: 10px 0;-->
<!--  padding-left: 10px;-->
<!--  border-left: 3px solid #409EFF;-->
<!--}-->
<!--</style>-->

<!--没有分两类的方法-->
<!--<template>-->
<!--  <div class="vulnerability-container">-->
<!--    &lt;!&ndash; 左侧IP列表 &ndash;&gt;-->
<!--    <div class="ip-list">-->
<!--      <div class="menu-header">-->
<!--        <span class="title">资产</span>-->
<!--        <el-badge-->
<!--            :value="assets.length"-->
<!--            class="asset-count"-->
<!--            type="primary">-->
<!--        </el-badge>-->
<!--      </div>-->
<!--      <el-menu-->
<!--          :default-active="currentIp"-->
<!--          class="ip-menu"-->
<!--          @select="handleSelect">-->
<!--        <el-menu-item-->
<!--            v-for="asset in assets"-->
<!--            :key="asset.ip"-->
<!--            :index="asset.ip">-->
<!--          <i class="el-icon-monitor"></i>-->
<!--          <span>{{ asset.ip }}</span>-->
<!--        </el-menu-item>-->
<!--      </el-menu>-->
<!--    </div>-->

<!--    &lt;!&ndash; 右侧详情内容 &ndash;&gt;-->
<!--    <div class="content-area" v-if="currentAsset">-->
<!--      <div class="ip-header">-->
<!--        <h2>资产信息</h2>-->
<!--        <div class="asset-info">-->
<!--          <div class="info-item">-->
<!--            <span class="label">IP地址：</span>-->
<!--            <span class="value">{{ currentAsset.ip }}</span>-->
<!--          </div>-->
<!--          <div class="info-item">-->
<!--            <span class="label">操作系统：</span>-->
<!--            <span class="value">{{ currentAsset.os }}</span>-->
<!--          </div>-->
<!--          <div class="info-item">-->
<!--            <span class="label">开放端口：</span>-->
<!--            <span class="value">{{ currentAsset.ports }}</span>-->
<!--          </div>-->
<!--        </div>-->
<!--      </div>-->

<!--      <h2>漏洞信息</h2>-->
<!--      &lt;!&ndash; 漏洞类型统计饼图 &ndash;&gt;-->
<!--      <el-card class="chart-section">-->
<!--        <div slot="header" class="clearfix">-->
<!--          <span>漏洞类型分布</span>-->
<!--        </div>-->
<!--        <div class="pie-chart" ref="pieChart" style="width: 100%; height: 300px;"></div>-->
<!--      </el-card>-->

<!--      &lt;!&ndash; 主机漏洞表格 &ndash;&gt;-->
<!--      <div class="table-section">-->
<!--        <h3><strong>系统漏洞</strong></h3>-->
<!--        <el-table-->
<!--            :data="currentAsset.host_vulnerabilities"-->
<!--            border-->
<!--            stripe-->
<!--            :header-cell-style="{ backgroundColor: '#f5f7fa' }"-->
<!--        >-->
<!--          <el-table-column prop="vuln_id" label="漏洞ID" width="150"></el-table-column>-->
<!--          <el-table-column prop="vuln_name" label="漏洞名称" width="150"></el-table-column>-->
<!--          <el-table-column prop="vulType" label="漏洞类型" width="150"></el-table-column>-->
<!--          <el-table-column prop="cvss" label="风险等级" width="120">-->
<!--            <template slot-scope="scope">-->
<!--              <el-tag :type="getCvssType(scope.row.cvss)">{{ getRiskLevel(scope.row.cvss) }}</el-tag>-->
<!--            </template>-->
<!--          </el-table-column>-->
<!--          <el-table-column prop="summary" label="漏洞描述"></el-table-column>-->
<!--          <el-table-column prop="vulExist" label="是否存在" width="100">-->
<!--            <template slot-scope="scope">-->
<!--              <el-tag :type="scope.row.vulExist === '存在' ? 'danger' : 'success'">-->
<!--                {{ scope.row.vulExist }}-->
<!--              </el-tag>-->
<!--            </template>-->
<!--          </el-table-column>-->
<!--        </el-table>-->
<!--      </div>-->

<!--      &lt;!&ndash; 端口漏洞表格 &ndash;&gt;-->
<!--      <div class="table-section">-->
<!--        <h3><strong>软件资产漏洞</strong></h3>-->
<!--        <div v-for="(vulnerabilities, type) in groupedPortVulnerabilities"-->
<!--             :key="type"-->
<!--             class="vulnerability-group">-->
<!--          <h4 class="group-title">{{ type }}</h4>-->
<!--          <el-table-->
<!--              :data="vulnerabilities"-->
<!--              border-->
<!--              stripe-->
<!--              :header-cell-style="{ backgroundColor: '#f5f7fa' }"-->
<!--          >-->
<!--            <el-table-column prop="port_id" label="端口" width="70"></el-table-column>-->
<!--            <el-table-column prop="vuln_id" label="漏洞ID" width="150"></el-table-column>-->
<!--            <el-table-column prop="vuln_name" label="漏洞名称" width="150"></el-table-column>-->
<!--            <el-table-column prop="vulType" label="漏洞类型" width="150"></el-table-column>-->
<!--            <el-table-column prop="cvss" label="风险等级" width="120">-->
<!--              <template slot-scope="scope">-->
<!--                <el-tag :type="getCvssType(scope.row.cvss)">{{ getRiskLevel(scope.row.cvss) }}</el-tag>-->
<!--              </template>-->
<!--            </el-table-column>-->
<!--            <el-table-column prop="summary" label="漏洞描述"></el-table-column>-->
<!--            <el-table-column prop="vulExist" label="是否存在" width="100">-->
<!--              <template slot-scope="scope">-->
<!--                <el-tag :type="scope.row.vulExist === '存在' ? 'danger' : 'success'">-->
<!--                  {{ scope.row.vulExist }}-->
<!--                </el-tag>-->
<!--              </template>-->
<!--            </el-table-column>-->
<!--          </el-table>-->
<!--        </div>-->
<!--      </div>-->
<!--    </div>-->

<!--    &lt;!&ndash; 未选择IP时的提示 &ndash;&gt;-->
<!--    <div class="empty-content" v-else>-->
<!--      <el-empty description="请选择左侧IP地址查看详情"></el-empty>-->
<!--    </div>-->
<!--  </div>-->
<!--</template>-->

<!--<script>-->
<!--import * as echarts from 'echarts';-->

<!--export default {-->
<!--  name: 'VulnerabilityTable',-->
<!--  data() {-->
<!--    return {-->
<!--      currentIp: '',-->
<!--      pieChart: null,-->
<!--      assets: []-->
<!--    }-->
<!--  },-->
<!--  computed: {-->
<!--    currentAsset() {-->
<!--      return this.assets.find(asset => asset.ip === this.currentIp);-->
<!--    },-->
<!--    groupedPortVulnerabilities() {-->
<!--      if (!this.currentAsset || !this.currentAsset.port_vulnerabilities) {-->
<!--        return {};-->
<!--      }-->
<!--      return this.currentAsset.port_vulnerabilities.reduce((groups, vuln) => {-->
<!--        const type = vuln.softwareType || '未分类';-->
<!--        if (!groups[type]) {-->
<!--          groups[type] = [];-->
<!--        }-->
<!--        groups[type].push(vuln);-->
<!--        return groups;-->
<!--      }, {});-->
<!--    },-->
<!--    vulnerabilityTypeStats() {-->
<!--      const stats = {-->
<!--        '操作系统': 0,-->
<!--        'Web应用程序': 0,-->
<!--        '系统工具': 0,-->
<!--        '中间件': 0,-->
<!--        '未知类型': 0-->
<!--      };-->

<!--      // 统计主机漏洞-->
<!--      if (this.currentAsset?.host_vulnerabilities) {-->
<!--        this.currentAsset.host_vulnerabilities.forEach(vuln => {-->
<!--          const type = vuln.softwareType || '未知类型';-->
<!--          if (Object.hasOwn(stats, type)) {-->
<!--            stats[type]++;-->
<!--          } else {-->
<!--            stats['未知类型']++;-->
<!--          }-->
<!--        });-->
<!--      }-->

<!--      // 统计端口漏洞-->
<!--      if (this.currentAsset?.port_vulnerabilities) {-->
<!--        this.currentAsset.port_vulnerabilities.forEach(vuln => {-->
<!--          const type = vuln.softwareType || '未知类型';-->
<!--          if (Object.hasOwn(stats, type)) {-->
<!--            stats[type]++;-->
<!--          } else {-->
<!--            stats['未知类型']++;-->
<!--          }-->
<!--        });-->
<!--      }-->

<!--      return stats;-->
<!--    }-->
<!--  },-->
<!--  methods: {-->
<!--    getResults() {-->
<!--      fetch('/api/getAllAssetsVulnData')-->
<!--          .then(response => response.json())-->
<!--          .then(data => {-->
<!--            this.assets = data;-->
<!--          })-->
<!--          .catch(error => console.error('Error:', error));-->
<!--    },-->
<!--    handleSelect(ip) {-->
<!--      this.currentIp = ip;-->
<!--      this.updatePieChart();-->
<!--    },-->
<!--    getCvssType(score) {-->
<!--      score = parseFloat(score);-->
<!--      if (score >= 7.0) return 'danger';-->
<!--      if (score >= 4.0) return 'warning';-->
<!--      if (score >= 0.0) return 'success';-->
<!--      return 'info';-->
<!--    },-->
<!--    getRiskLevel(score) {-->
<!--      score = parseFloat(score);-->
<!--      if (score >= 7.0) return '高风险';-->
<!--      if (score >= 4.0) return '中风险';-->
<!--      if (score >= 0.0) return '低风险';-->
<!--      return '信息';-->
<!--    },-->
<!--    async initPieChart() {-->
<!--      await this.$nextTick();-->
<!--      if (this.$refs.pieChart) {-->
<!--        if (this.pieChart) {-->
<!--          this.pieChart.dispose();-->
<!--        }-->
<!--        this.pieChart = echarts.init(this.$refs.pieChart);-->
<!--        window.addEventListener('resize', () => {-->
<!--          this.pieChart && this.pieChart.resize();-->
<!--        });-->
<!--        this.updatePieChart();-->
<!--      }-->
<!--    },-->
<!--    updatePieChart() {-->
<!--      if (!this.pieChart) {-->
<!--        this.initPieChart();-->
<!--        return;-->
<!--      }-->

<!--      const stats = this.vulnerabilityTypeStats;-->
<!--      const data = Object.entries(stats)-->
<!--          .filter(([, value]) => value > 0) // 只显示数量大于0的类型-->
<!--          .map(([name, value]) => ({-->
<!--            name,-->
<!--            value-->
<!--          }));-->

<!--      const option = {-->
<!--        tooltip: {-->
<!--          trigger: 'item',-->
<!--          formatter: '{a} <br/>{b}: {c} ({d}%)'-->
<!--        },-->
<!--        legend: {-->
<!--          orient: 'vertical',-->
<!--          right: 'right',-->
<!--          top: 'middle',-->
<!--          data: data.map(item => item.name)-->
<!--        },-->
<!--        series: [-->
<!--          {-->
<!--            name: '漏洞类型分布',-->
<!--            type: 'pie',-->
<!--            radius: ['40%', '70%'],-->
<!--            center: ['40%', '50%'],-->
<!--            avoidLabelOverlap: false,-->
<!--            itemStyle: {-->
<!--              borderRadius: 10,-->
<!--              borderColor: '#fff',-->
<!--              borderWidth: 2-->
<!--            },-->
<!--            label: {-->
<!--              show: true,-->
<!--              formatter: '{b}: {c}个'-->
<!--            },-->
<!--            emphasis: {-->
<!--              label: {-->
<!--                show: true,-->
<!--                fontSize: '18',-->
<!--                fontWeight: 'bold'-->
<!--              }-->
<!--            },-->
<!--            labelLine: {-->
<!--              show: true-->
<!--            },-->
<!--            data: data-->
<!--          }-->
<!--        ]-->
<!--      };-->

<!--      this.pieChart.setOption(option);-->
<!--    }-->
<!--  },-->
<!--  created() {-->
<!--    this.getResults();-->
<!--  },-->
<!--  mounted() {-->
<!--    // 默认选中第一个IP-->
<!--    if (this.assets.length > 0) {-->
<!--      this.currentIp = this.assets[0].ip;-->
<!--    }-->
<!--    this.$nextTick(() => {-->
<!--      this.initPieChart();-->
<!--    });-->
<!--  },-->
<!--  beforeDestroy() {-->
<!--    if (this.pieChart) {-->
<!--      this.pieChart.dispose();-->
<!--      this.pieChart = null;-->
<!--    }-->
<!--  },-->
<!--  watch: {-->
<!--    currentAsset() {-->
<!--      this.$nextTick(() => {-->
<!--        this.updatePieChart();-->
<!--      });-->
<!--    }-->
<!--  }-->
<!--}-->
<!--</script>-->

<!--<style scoped>-->
<!--.vulnerability-container {-->
<!--  display: flex;-->
<!--  height: 100%;-->
<!--  min-height: 600px;-->
<!--  background-color: #fff;-->
<!--}-->

<!--.ip-list {-->
<!--  width: 250px;-->
<!--  border-right: 1px solid #e6e6e6;-->
<!--  background-color: #f5f7fa;-->
<!--}-->

<!--.menu-header {-->
<!--  height: 50px;-->
<!--  display: flex;-->
<!--  align-items: center;-->
<!--  padding: 0 20px;-->
<!--  border-bottom: 1px solid #e6e6e6;-->
<!--}-->

<!--.menu-header .title {-->
<!--  font-size: 16px;-->
<!--  font-weight: 600;-->
<!--  color: #303133;-->
<!--}-->

<!--.menu-header .asset-count {-->
<!--  margin-left: 10px;-->
<!--}-->

<!--.ip-menu {-->
<!--  border-right: none;-->
<!--}-->

<!--.content-area {-->
<!--  flex: 1;-->
<!--  padding: 20px;-->
<!--  overflow-y: auto;-->
<!--}-->

<!--.empty-content {-->
<!--  flex: 1;-->
<!--  display: flex;-->
<!--  justify-content: center;-->
<!--  align-items: center;-->
<!--}-->

<!--.ip-header {-->
<!--  margin-bottom: 20px;-->
<!--  padding-bottom: 10px;-->
<!--  border-bottom: 1px solid #ebeef5;-->
<!--}-->

<!--.ip-header h2 {-->
<!--  color: #303133;-->
<!--  font-size: 18px;-->
<!--  font-weight: 600;-->
<!--  margin: 0 0 15px 0;-->
<!--}-->

<!--.asset-info {-->
<!--  padding: 15px;-->
<!--  background-color: #f5f7fa;-->
<!--  border-radius: 4px;-->
<!--}-->

<!--.info-item {-->
<!--  line-height: 28px;-->
<!--  display: flex;-->
<!--}-->

<!--.info-item .label {-->
<!--  color: #606266;-->
<!--  width: 80px;-->
<!--  text-align: right;-->
<!--  margin-right: 15px;-->
<!--}-->

<!--.info-item .value {-->
<!--  color: #303133;-->
<!--  flex: 1;-->
<!--}-->

<!--.table-section {-->
<!--  margin-bottom: 30px;-->
<!--}-->

<!--.table-section h3 {-->
<!--  margin: 15px 0;-->
<!--  color: #303133;-->
<!--  font-size: 16px;-->
<!--  font-weight: 500;-->
<!--}-->

<!--.el-tag {-->
<!--  width: 65px;-->
<!--  text-align: center;-->
<!--}-->

<!--/* 表格内的标签居中显示 */-->
<!--.el-table .cell {-->
<!--  text-align: center;-->
<!--}-->

<!--/* 确保描述列左对齐 */-->
<!--.el-table .el-table__row td:nth-child(4) .cell {-->
<!--  text-align: left;-->
<!--}-->

<!--.vulnerability-group {-->
<!--  margin-bottom: 20px;-->
<!--}-->

<!--.group-title {-->
<!--  color: #606266;-->
<!--  font-size: 14px;-->
<!--  font-weight: 500;-->
<!--  margin: 10px 0;-->
<!--  padding-left: 10px;-->
<!--  border-left: 3px solid #409EFF;-->
<!--}-->

<!--/* 新增的饼图相关样式 */-->
<!--.chart-section {-->
<!--  margin: 20px 0;-->
<!--  padding: 0px;-->
<!--  background-color: #fff;-->
<!--  border-radius: 4px;-->
<!--  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1);-->
<!--}-->

<!--.chart-section h3 {-->
<!--  margin-bottom: 20px;-->
<!--  color: #303133;-->
<!--}-->

<!--.pie-chart {-->
<!--  width: 100%;-->
<!--  height: 400px;-->
<!--}-->
<!--</style>-->


<!--没有饼状图的代码 -->
<!--<template>-->
<!--  <div class="vulnerability-container">-->
<!--    &lt;!&ndash; 左侧IP列表 &ndash;&gt;-->
<!--    <div class="ip-list">-->
<!--      <div class="menu-header">-->
<!--        <span class="title">资产</span>-->
<!--        <el-badge-->
<!--            :value="assets.length"-->
<!--            class="asset-count"-->
<!--            type="primary">-->
<!--        </el-badge>-->
<!--      </div>-->
<!--      <el-menu-->
<!--          :default-active="currentIp"-->
<!--          class="ip-menu"-->
<!--          @select="handleSelect">-->
<!--        <el-menu-item-->
<!--            v-for="asset in assets"-->
<!--            :key="asset.ip"-->
<!--            :index="asset.ip">-->
<!--          <i class="el-icon-monitor"></i>-->
<!--          <span>{{ asset.ip }}</span>-->
<!--        </el-menu-item>-->
<!--      </el-menu>-->
<!--    </div>-->

<!--    &lt;!&ndash; 右侧详情内容 &ndash;&gt;-->
<!--    <div class="content-area" v-if="currentAsset">-->
<!--      <div class="ip-header">-->
<!--        <h2>资产信息</h2>-->
<!--        <div class="asset-info">-->
<!--          <div class="info-item">-->
<!--            <span class="label">IP地址：</span>-->
<!--            <span class="value">{{ currentAsset.ip }}</span>-->
<!--          </div>-->
<!--          <div class="info-item">-->
<!--            <span class="label">操作系统：</span>-->
<!--            <span class="value">{{ currentAsset.os }}</span>-->
<!--          </div>-->
<!--          <div class="info-item">-->
<!--            <span class="label">开放端口：</span>-->
<!--            <span class="value">{{ currentAsset.ports }}</span>-->
<!--          </div>-->
<!--        </div>-->
<!--      </div>-->

<!--      &lt;!&ndash; 主机漏洞表格 &ndash;&gt;-->
<!--      <div class="table-section">-->
<!--        <h3>主机漏洞</h3>-->
<!--        <el-table-->
<!--            :data="currentAsset.host_vulnerabilities"-->
<!--            border-->
<!--            stripe-->
<!--            :header-cell-style="{ backgroundColor: '#f5f7fa' }"-->
<!--        >-->
<!--          <el-table-column prop="vuln_id" label="漏洞ID" width="150"></el-table-column>-->
<!--          <el-table-column prop="vuln_name" label="漏洞名称" width="150"></el-table-column>-->
<!--          <el-table-column prop="cvss" label="风险等级" width="120">-->
<!--            <template slot-scope="scope">-->
<!--              <el-tag :type="getCvssType(scope.row.cvss)">{{ getRiskLevel(scope.row.cvss) }}</el-tag>-->
<!--            </template>-->
<!--          </el-table-column>-->
<!--          <el-table-column prop="summary" label="漏洞描述"></el-table-column>-->
<!--          <el-table-column prop="vulExist" label="是否存在" width="100">-->
<!--            <template slot-scope="scope">-->
<!--              <el-tag :type="scope.row.vulExist === '存在' ? 'danger' : 'success'">-->
<!--                {{ scope.row.vulExist }}-->
<!--              </el-tag>-->
<!--            </template>-->
<!--          </el-table-column>-->
<!--        </el-table>-->
<!--      </div>-->

<!--      &lt;!&ndash; 端口漏洞表格 &ndash;&gt;-->
<!--      &lt;!&ndash; 将原来的端口漏洞表格部分替换成以下代码 &ndash;&gt;-->
<!--      &lt;!&ndash; 端口漏洞表格 &ndash;&gt;-->
<!--      <div class="table-section">-->
<!--        <h3>端口漏洞</h3>-->
<!--        <div v-for="(vulnerabilities, type) in groupedPortVulnerabilities"-->
<!--             :key="type"-->
<!--             class="vulnerability-group">-->
<!--          <h4 class="group-title">{{ type }}</h4>-->
<!--          <el-table-->
<!--              :data="vulnerabilities"-->
<!--              border-->
<!--              stripe-->
<!--              :header-cell-style="{ backgroundColor: '#f5f7fa' }"-->
<!--          >-->
<!--            <el-table-column prop="port_id" label="端口" width="100"></el-table-column>-->
<!--            <el-table-column prop="vuln_id" label="漏洞ID" width="150"></el-table-column>-->
<!--            <el-table-column prop="vuln_name" label="漏洞名称" width="150"></el-table-column>-->
<!--            <el-table-column prop="cvss" label="风险等级" width="120">-->
<!--              <template slot-scope="scope">-->
<!--                <el-tag :type="getCvssType(scope.row.cvss)">{{ getRiskLevel(scope.row.cvss) }}</el-tag>-->
<!--              </template>-->
<!--            </el-table-column>-->
<!--            <el-table-column prop="summary" label="漏洞描述"></el-table-column>-->
<!--            <el-table-column prop="vulExist" label="是否存在" width="100">-->
<!--              <template slot-scope="scope">-->
<!--                <el-tag :type="scope.row.vulExist === '存在' ? 'danger' : 'success'">-->
<!--                  {{ scope.row.vulExist }}-->
<!--                </el-tag>-->
<!--              </template>-->
<!--            </el-table-column>-->
<!--          </el-table>-->
<!--        </div>-->
<!--      </div>-->
<!--    </div>-->

<!--    &lt;!&ndash; 未选择IP时的提示 &ndash;&gt;-->
<!--    <div class="empty-content" v-else>-->
<!--      <el-empty description="请选择左侧IP地址查看详情"></el-empty>-->
<!--    </div>-->
<!--  </div>-->
<!--</template>-->

<!--<script>-->
<!--export default {-->
<!--  name: 'VulnerabilityTable',-->
<!--  data() {-->
<!--    return {-->
<!--      currentIp: '',-->
<!--      assets: [-->
<!--        {-->
<!--          "host_vulnerabilities": [-->
<!--            {-->
<!--              "cvss": "9.800000",-->
<!--              "softwareType": "操作系统",-->
<!--              "summary": "MongoDB 4.2.7存在权限提升漏洞，攻击者可以通过特定的构造命令绕过认证并获得管理员权限。",-->
<!--              "vulExist": "存在",-->
<!--              "vuln_id": "CVE-2020-12345",-->
<!--              "vuln_name": ""-->
<!--            },-->
<!--            {-->
<!--              "cvss": "7.500000",-->
<!--              "softwareType": "操作系统",-->
<!--              "summary": "Windows SMBv3协议存在内存损坏漏洞，允许远程代码执行。",-->
<!--              "vulExist": "存在",-->
<!--              "vuln_id": "CVE-2021-34527",-->
<!--              "vuln_name": ""-->
<!--            }-->
<!--          ],-->
<!--          "ip": "10.8.250.77",-->
<!--          "port_vulnerabilities": [-->
<!--            {-->
<!--              "cvss": "8.900000",-->
<!--              "port_id": 8080,-->
<!--              "softwareType": "Web应用程序",-->
<!--              "summary": "Apache Struts 2.3.34 存在远程代码执行漏洞，攻击者可通过恶意请求触发。",-->
<!--              "vulExist": "存在",-->
<!--              "vuln_id": "CVE-2018-11776",-->
<!--              "vuln_name": ""-->
<!--            },-->
<!--            {-->
<!--              "cvss": "8.900000",-->
<!--              "port_id": 804,-->
<!--              "softwareType": "Web应用程序",-->
<!--              "summary": "描述。",-->
<!--              "vulExist": "存在",-->
<!--              "vuln_id": "CVE-2018-12436",-->
<!--              "vuln_name": ""-->
<!--            },-->
<!--            {-->
<!--              "cvss": "8.900000",-->
<!--              "port_id": 808,-->
<!--              "softwareType": "系统工具",-->
<!--              "summary": "Apache Struts 2.3.34 存在远程代码执行漏洞，攻击者可通过恶意请求触发。",-->
<!--              "vulExist": "存在",-->
<!--              "vuln_id": "CVE-2018-1236",-->
<!--              "vuln_name": ""-->
<!--            },-->
<!--            {-->
<!--              "cvss": "8.900000",-->
<!--              "port_id": 80,-->
<!--              "softwareType": "未知类型",-->
<!--              "summary": "描述。",-->
<!--              "vulExist": "存在",-->
<!--              "vuln_id": "CVE-2018-132",-->
<!--              "vuln_name": ""-->
<!--            }-->
<!--          ]-->
<!--        },-->
<!--        {-->
<!--          "host_vulnerabilities": [-->
<!--            {-->
<!--              "cvss": "6.500000",-->
<!--              "softwareType": "操作系统",-->
<!--              "summary": "VMware ESXi 7.0中的特定模块存在拒绝服务漏洞，可能导致虚拟机异常终止。",-->
<!--              "vulExist": "存在",-->
<!--              "vuln_id": "CVE-2022-12345",-->
<!--              "vuln_name": ""-->
<!--            }-->
<!--          ],-->
<!--          "ip": "192.168.1.100",-->
<!--          "port_vulnerabilities": [-->
<!--            {-->
<!--              "cvss": "10.000000",-->
<!--              "port_id": 443,-->
<!--              "softwareType": "Web服务器",-->
<!--              "summary": "nginx 1.18.0 存在缓冲区溢出漏洞，允许远程攻击者执行任意代码。",-->
<!--              "vulExist": "存在",-->
<!--              "vuln_id": "CVE-2021-23017",-->
<!--              "vuln_name": ""-->
<!--            }-->
<!--          ]-->
<!--        }-->
<!--      ]-->
<!--    }-->
<!--  },-->
<!--  computed: {-->
<!--    currentAsset() {-->
<!--      return this.assets.find(asset => asset.ip === this.currentIp);-->
<!--    },-->
<!--    groupedPortVulnerabilities() {-->
<!--      if (!this.currentAsset || !this.currentAsset.port_vulnerabilities) {-->
<!--        return {};-->
<!--      }-->
<!--      return this.currentAsset.port_vulnerabilities.reduce((groups, vuln) => {-->
<!--        const type = vuln.softwareType || '未分类';-->
<!--        if (!groups[type]) {-->
<!--          groups[type] = [];-->
<!--        }-->
<!--        groups[type].push(vuln);-->
<!--        return groups;-->
<!--      }, {});-->
<!--    }-->
<!--  },-->
<!--  methods: {-->
<!--    getResults() {-->
<!--      fetch('/api/getAllAssetsVulnData')-->
<!--          .then(response => response.json())-->
<!--          .then(data => {-->
<!--            this.assets = data;-->
<!--          })-->
<!--          .catch(error => console.error('Error:', error));-->
<!--    },-->
<!--    handleSelect(ip) {-->
<!--      this.currentIp = ip;-->
<!--    },-->
<!--    getCvssType(score) {-->
<!--      score = parseFloat(score);-->
<!--      if (score >= 7.0) return 'danger';-->
<!--      if (score >= 4.0) return 'warning';-->
<!--      if (score >= 0.0) return 'success';-->
<!--      return 'info';-->
<!--    },-->
<!--    getRiskLevel(score) {-->
<!--      score = parseFloat(score);-->
<!--      if (score >= 7.0) return '高风险';-->
<!--      if (score >= 4.0) return '中风险';-->
<!--      if (score >= 0.0) return '低风险';-->
<!--      return '信息';-->
<!--    }-->
<!--  },-->
<!--  created() {-->
<!--    this.getResults();-->
<!--  },-->
<!--  mounted() {-->
<!--    // 默认选中第一个IP-->
<!--    if (this.assets.length > 0) {-->
<!--      this.currentIp = this.assets[0].ip;-->
<!--    }-->
<!--  }-->
<!--}-->
<!--</script>-->

<!--<style scoped>-->
<!--.vulnerability-container {-->
<!--  display: flex;-->
<!--  height: 100%;-->
<!--  min-height: 600px;-->
<!--  background-color: #fff;-->
<!--}-->

<!--.ip-list {-->
<!--  width: 250px;-->
<!--  border-right: 1px solid #e6e6e6;-->
<!--  background-color: #f5f7fa;-->
<!--}-->

<!--.menu-header {-->
<!--  height: 50px;-->
<!--  display: flex;-->
<!--  align-items: center;-->
<!--  padding: 0 20px;-->
<!--  border-bottom: 1px solid #e6e6e6;-->
<!--}-->

<!--.menu-header .title {-->
<!--  font-size: 16px;-->
<!--  font-weight: 600;-->
<!--  color: #303133;-->
<!--}-->

<!--.menu-header .asset-count {-->
<!--  margin-left: 10px;-->
<!--}-->

<!--.ip-menu {-->
<!--  border-right: none;-->
<!--}-->

<!--.content-area {-->
<!--  flex: 1;-->
<!--  padding: 20px;-->
<!--  overflow-y: auto;-->
<!--}-->

<!--.empty-content {-->
<!--  flex: 1;-->
<!--  display: flex;-->
<!--  justify-content: center;-->
<!--  align-items: center;-->
<!--}-->

<!--.ip-header {-->
<!--  margin-bottom: 20px;-->
<!--  padding-bottom: 10px;-->
<!--  border-bottom: 1px solid #ebeef5;-->
<!--}-->

<!--.ip-header h2 {-->
<!--  color: #303133;-->
<!--  font-size: 18px;-->
<!--  font-weight: 600;-->
<!--  margin: 0 0 15px 0;-->
<!--}-->

<!--.asset-info {-->
<!--  padding: 15px;-->
<!--  background-color: #f5f7fa;-->
<!--  border-radius: 4px;-->
<!--}-->

<!--.info-item {-->
<!--  line-height: 28px;-->
<!--  display: flex;-->
<!--}-->

<!--.info-item .label {-->
<!--  color: #606266;-->
<!--  width: 80px;-->
<!--  text-align: right;-->
<!--  margin-right: 15px;-->
<!--}-->

<!--.info-item .value {-->
<!--  color: #303133;-->
<!--  flex: 1;-->
<!--}-->

<!--.table-section {-->
<!--  margin-bottom: 30px;-->
<!--}-->

<!--.table-section h3 {-->
<!--  margin: 15px 0;-->
<!--  color: #303133;-->
<!--  font-size: 16px;-->
<!--  font-weight: 500;-->
<!--}-->

<!--.el-tag {-->
<!--  width: 65px;-->
<!--  text-align: center;-->
<!--}-->

<!--/* 表格内的标签居中显示 */-->
<!--.el-table .cell {-->
<!--  text-align: center;-->
<!--}-->

<!--/* 确保描述列左对齐 */-->
<!--.el-table .el-table__row td:nth-child(4) .cell {-->
<!--  text-align: left;-->
<!--}-->

<!--.vulnerability-group {-->
<!--  margin-bottom: 20px;-->
<!--}-->

<!--.group-title {-->
<!--  color: #606266;-->
<!--  font-size: 14px;-->
<!--  font-weight: 500;-->
<!--  margin: 10px 0;-->
<!--  padding-left: 10px;-->
<!--  border-left: 3px solid #409EFF;-->
<!--}-->
<!--</style>-->

