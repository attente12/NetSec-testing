<template>
  <div class="container">
    <div class="title">
      <h1>插件化扫描</h1>
    </div>

    <el-row :gutter="20">
      <el-col :span="8">
        <el-card class="box-card">
          <div slot="header">扫描目标</div>
          <el-radio-group v-model="all_ports" style="margin-bottom: 15px;">
            <el-radio :label="true">扫描所有端口</el-radio>
            <el-radio :label="false">扫描常见1000端口</el-radio>
          </el-radio-group>

          <el-select v-model="scanTarget" placeholder="请输入或选择要扫描的目标，例如：192.168.1.0" @change="changeServer" allow-create
            default-first-option style="width: 100%; margin-bottom: 10px;">
            <el-option v-for="ip in aliveHosts" :key="ip" :label="ip" :value="ip">
            </el-option>
          </el-select>
          <div style="margin-bottom: 10px; color: #409EFF; font-size: 13px;">
            <i class="el-icon-warning-outline" style="margin-right: 5px;"></i>如果该资产未进行过端口扫描，需要进行预扫描。
          </div>
          <div class="scan-button" style="margin-bottom: 60px;">
            <!--            <el-button size="small" @click="chooseDetect">扫描</el-button>-->
            <el-button size="small" @click="chooseDetect" :loading="detectState" icon="el-icon-search" type="primary">
              预扫描
            </el-button>
          </div>
        </el-card>
      </el-col>

      <el-col :span="16">
        <el-card class="box-card">
          <div slot="header">POC列表</div>
          <el-col :span="14" style="margin-right: 30px;">
            <div class="poc-list" style="max-height: 200px; overflow-y: auto;">
              <el-checkbox-group v-model="checkedPocs">
                <el-checkbox v-for="poc in pocList" :key="poc.id" :label="poc"
                  style="display: block; width: 480px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                  {{ poc.vul_name }}
                </el-checkbox>
              </el-checkbox-group>
            </div>
          </el-col>

          <el-col :span="9">
            <div style="margin-top: 10px;">
              <el-button size="small" @click="autoSelect">自动选择poc</el-button>
            </div>
            <div style="margin-top: 10px;">
              <el-checkbox v-model="match_infra" disabled>受影响的基础设施匹配</el-checkbox>
            </div>
            <div style="margin-top: 10px;">
              <el-checkbox v-model="portValidityCheck" disabled>端口有效性检查</el-checkbox>
            </div>
            <div class="scan-button">
              <!--              <el-button size="small" @click="runPoc">执行poc</el-button>-->
              <el-button size="small" @click="runPoc" :loading="runPocState" icon="el-icon-search" type="primary">
                执行poc
              </el-button>
            </div>
          </el-col>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card class="box-card">
          <div slot="header" class="clearfix">
            <span>扫描结果</span>
            <!--            <div style="float: right" v-if="result.scan_time">检测时间: {{ result.scan_time }}</div>-->
            <!--            <div style="float: right" v-if="time">检测时间: {{ time }}</div>-->
          </div>
          <el-button @click="printReport" :loading="printLoading" icon="el-icon-document" type="primary" size="small"
            style="margin-bottom: 15px;">
            打印检测报告
          </el-button>
          <el-table :data="sortedVulnResults" style="width: 100%" v-if="result.ports">
            <el-table-column prop="Vuln_id" label="漏洞ID" width="150"></el-table-column>
            <el-table-column prop="vul_name" label="漏洞名称" width="200"></el-table-column>
            <el-table-column prop="CVSS" label="CVSS" width="100"></el-table-column>
            <el-table-column prop="pocExist" label="POC存在" width="100">
              <template slot-scope="scope">
                {{ scope.row.pocExist ? '是' : '否' }}
              </template>
            </el-table-column>
            <el-table-column prop="vulExist" label="漏洞状态" width="100" :filters="[
              { text: '存在', value: '存在' },
              { text: '不存在', value: '不存在' },
              { text: '未验证', value: '未验证' }
            ]" :filter-method="filterVulExist">
              <template slot-scope="scope">
                <el-tag :type="scope.row.vulExist === '存在' ? 'danger' : 'info'">
                  {{ scope.row.vulExist }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="summary" label="描述"></el-table-column>
            <el-table-column prop="scan_time" label="检测时间" width="200"></el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <!-- 打印区域（默认隐藏） -->
    <div id="printable">
      <!-- 第一页 -->
      <div class="print-page">
        <h1 class="print-title">漏洞扫描报告</h1>
        <div class="print-info">
          <p><strong>IP地址：</strong>{{ result.ip }}</p>
          <p><strong>操作系统：</strong>{{ result.os_list ? result.os_list.join(', ') : '未知' }}</p>
          <p><strong>系统版本：</strong>{{ result.os_matches ? result.os_matches.join(', ') : '未知' }}</p>
          <!--          <p><strong>扫描时间：</strong>{{ result.scan_time }}</p>-->
        </div>
      </div>

      <!-- 第二页及后续 -->
      <div class="print-page">
        <h2>漏洞详情</h2>
        <table class="print-table">
          <thead>
            <tr>
              <th>漏洞ID</th>
              <th>漏洞名称</th>
              <th>CVSS</th>
              <!--            <th>POC存在</th>-->
              <!--            <th>是否检查</th>-->
              <th>漏洞状态</th>
              <th>描述</th>
              <th>检测时间</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="vuln in sortedVulnResults" :key="vuln.Vuln_id">
              <td>{{ vuln.Vuln_id }}</td>
              <td>{{ vuln.vul_name }}</td>
              <td>{{ vuln.CVSS || '-' }}</td>
              <!--            <td>{{ vuln.pocExist ? '是' : '否' }}</td>-->
              <!--            <td>{{ vuln.ifCheck ? '是' : '否' }}</td>-->
              <td>{{ vuln.vulExist }}</td>
              <td>{{ vuln.summary }}</td>
              <td>{{ vuln.scan_time }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import { jsPDF } from 'jspdf';
import html2canvas from 'html2canvas';
import _ from 'lodash';
import { Message } from "element-ui";

export default {
  data() {
    return {
      all_ports: false,
      scanTarget: '',
      pocList: [],
      checkedPocs: [],
      selectedPoc: [],
      selectedVulnIds: [], // 新增：存储选中的poc对应的vuln_id列表
      match_infra: true,
      portValidityCheck: true,
      result: { ports: [] }, // 初始化为包含空ports数组的对象
      aliveHosts: [], // 新增：存储活跃IP列表
      detectState: false,
      runPocState: false,
      printLoading: false,
      time: '',
    };
  },

  computed: {
    // 对漏洞结果进行排序，将"存在"的漏洞排在前面，并且只显示选中的poc对应的漏洞

    // 修改 sortedVulnResults 计算属性
    sortedVulnResults() {
      if (!this.result || !this.result.ports) return [];

      // 收集所有端口的漏洞结果
      let allVulns = [];
      this.result.ports.forEach(port => {
        if (port.vuln_result && port.vuln_result.length > 0) {
          allVulns = allVulns.concat(port.vuln_result);
        }
      });

      // 如果有操作系统相关的漏洞，也加入
      if (this.result.os_vuln_result && this.result.os_vuln_result.length > 0) {
        allVulns = allVulns.concat(this.result.os_vuln_result);
      }

      // 去重（基于Vuln_id）
      allVulns = _.uniqBy(allVulns, 'Vuln_id');

      // 新增：如果有选中的vuln_id列表，则只显示这些漏洞
      if (this.selectedVulnIds && this.selectedVulnIds.length > 0) {
        allVulns = allVulns.filter(vuln => this.selectedVulnIds.includes(vuln.Vuln_id));
      }

      // 明确定义排序顺序: 存在 > 不存在 > 未验证
      return _.sortBy(allVulns, [
        // 首要排序条件：按漏洞状态
        item => {
          if (item.vulExist === '存在') return 0;
          if (item.vulExist === '不存在') return 1;
          if (item.vulExist === '未验证') return 2;
          return 3; // 其他未知状态
        },
        // 次要排序条件：按漏洞ID
        'Vuln_id'
      ]);
    }
  },

  methods: {
    changeServer() {
      if (this.scanTarget) {
        this.loadTableData();
      }
    },
    chooseDetect() {
      if (this.all_ports === true) {
        this.detectAll();
      } else {
        this.detect();
      }
    },
    detect() {
      this.detectState = true;
      // localStorage.setItem('scanTarget', JSON.stringify(this.scanTarget));
      const target = { ip: this.scanTarget };
      this.$axios.post('/api/getNmapIp', target)
        .then(response => {
          console.log('Scan result:', response.data);
          Message.success('扫描完成');
          setTimeout(() => {
            this.detectState = false;
            window.location.reload(); // 刷新页面
          }, 2000); // 显示提示2秒后刷新页面
          // 在这里处理成功响应的数据
        })
        .catch(error => {
          this.detectState = false;
          console.error('There was an error scanning the target:', error);
          // 在这里处理错误
        });
    },
    detectAll() {
      this.detectState = true;//检测中状态
      // localStorage.setItem('scanTarget', JSON.stringify(this.scanTarget));
      //const target = { ip: this.scanTarget };
      // 生成请求体，默认包含 all_ports: true
      const target = {
        ip: this.scanTarget,
        all_ports: true // 默认发送 all_ports 为 true
      };
      this.$axios.post('/api/getNmapIp', target)
        .then(response => {
          console.log('Scan result:', response.data);
          Message.success('扫描完成');
          setTimeout(() => {
            this.detectState = false;//关闭检测中状态
            window.location.reload(); // 刷新页面
          }, 2000); // 显示提示2秒后刷新页面
          // 在这里处理成功响应的数据
        })
        .catch(error => {
          console.error('There was an error scanning the target:', error);
          this.detectState = false;//关闭检测中状态
          // 在这里处理错误
        });
    },
    // 获取活跃IP列表 - 修改为从localStorage获取
    fetchAliveHosts() {
      try {
        const storedHosts = sessionStorage.getItem('hostdiscovery');
        if (storedHosts) {
          this.aliveHosts = JSON.parse(storedHosts);
          if (!this.scanTarget && this.aliveHosts.length > 0) {
            this.scanTarget = this.aliveHosts[0];
            this.loadTableData();
          }
        } else {
          this.aliveHosts = [];
          Message.warning('未找到存活主机列表，请先进行主机发现');
        }
      } catch (error) {
        console.error('解析sessionStorage数据失败:', error);
        this.aliveHosts = [];
        this.$message.error('获取存活主机列表失败');
      }
    },
    // 新增：获取活跃IP列表的方法
    // fetchAliveHosts() {
    //   this.$axios.get('/api/getAliveHosts')
    //       .then(response => {
    //         this.aliveHosts = response.data.alive_hosts;
    //         if (!this.scanTarget) {
    //           this.scanTarget = this.aliveHosts[0];
    //           this.loadTableData();
    //         }
    //       })
    //       .catch(error => {
    //         console.error('获取活跃IP列表失败:', error);
    //         this.$message.error('获取活跃IP列表失败');
    //       });
    // },
    // loadTableData(){
    //   this.$axios.get('/api/getAllData').then(response => {
    //     this.pocList=response.data;
    //   })
    //   this.$axios.post('/api/pocScan/mergeResults', { ip: this.scanTarget })
    //       .then(response => {
    //         this.result = response.data;
    //         console.log(response.data);
    //       })
    //       .catch(error => {
    //         console.error('error:', error);
    //       });
    // },
    loadTableData() {
      this.$axios.get('/api/getAllData').then(response => {
        this.pocList = response.data;
      })
    },

    // 过滤漏洞状态
    filterVulExist(value, row) {
      return row.vulExist === value;
    },

    runPoc() {
      if (!this.scanTarget) {
        this.$message.error('请选择有效的IP地址');
        return;
      }
      this.runPocState = true;
      // localStorage.setItem('scanTarget', JSON.stringify(this.scanTarget));
      this.selectedPoc = this.checkedPocs.map(poc => poc.id);

      // 新增：获取选中的poc对应的vuln_id列表
      this.selectedVulnIds = this.checkedPocs.map(poc => poc.vuln_id);

      const postData = {
        ip: this.scanTarget,
        all_ports: this.all_ports,
        match_infra: this.match_infra,
        ids: this.selectedPoc
      };

      this.$axios.post('/api/pocScan', postData)
        .then(response => {
          console.log(response.data);
          this.time = response.data.scan_time;
          this.result = response.data;
          this.runPocState = false;
          this.$message.success('检测完成，结果已更新');
        })
        .catch(error => {
          console.error('Service detect error:', error);
        });
    },

    autoSelect() {
      if (!this.scanTarget) {
        this.$message.error('请选择有效的IP地址');
        return;
      }

      this.$axios.post('/api/pocScan/autoSelectPoc', { ip: this.scanTarget })
        .then(response => {
          const autoSelectedIds = response.data.map(poc => poc.id);
          this.checkedPocs = this.pocList.filter(poc => autoSelectedIds.includes(poc.id));
        })
        .catch(error => {
          console.error('Auto select error:', error);
        });
    },

    async printReport() {
      this.printLoading = true;
      try {
        const pdf = new jsPDF({
          orientation: 'p',
          unit: 'mm',
          format: 'a4'
        });

        // 显示打印区域（临时）
        const printableElement = document.getElementById('printable');

        // 临时将打印区域设置为可见，但调整样式确保用户不会看到
        printableElement.style.display = 'block';
        printableElement.style.position = 'fixed';
        printableElement.style.top = '-9999px';
        printableElement.style.left = '-9999px';
        printableElement.style.visibility = 'visible';
        printableElement.style.zIndex = '-1000';
        printableElement.style.opacity = '1'; // 使其对html2canvas可见，但对用户不可见

        // 首先处理第一页（封面）
        const firstPage = printableElement.getElementsByClassName('print-page')[0];
        const firstPageCanvas = await html2canvas(firstPage, {
          scale: 2,
          useCORS: true,
          logging: false,
          backgroundColor: '#ffffff'
        });

        // 添加封面
        const firstPageImgData = firstPageCanvas.toDataURL('image/jpeg', 0.8);
        const imgWidth = 190; // A4纸宽度减去边距
        let imgHeight = firstPageCanvas.height * imgWidth / firstPageCanvas.width;
        pdf.addImage(firstPageImgData, 'JPEG', 10, 10, imgWidth, imgHeight);

        // 添加新页面用于表格
        pdf.addPage();

        // 获取表格元素
        const tableElement = printableElement.querySelector('.print-table');

        // 先渲染表头
        const tableHeader = tableElement.querySelector('thead');
        const headerCanvas = await html2canvas(tableHeader, {
          scale: 2,
          useCORS: true
        });

        const headerImgData = headerCanvas.toDataURL('image/jpeg', 0.8);
        const headerImgWidth = 190;
        const headerImgHeight = headerCanvas.height * headerImgWidth / headerCanvas.width;

        // 添加表头到新页面
        pdf.addImage(headerImgData, 'JPEG', 10, 10, headerImgWidth, headerImgHeight);

        // 处理表格行
        const rows = tableElement.querySelectorAll('tbody tr');
        let currentY = 10 + headerImgHeight + 2; // 当前垂直位置，从表头下方开始

        const pageHeight = pdf.internal.pageSize.getHeight() - 20; // 页面可用高度（减去边距）

        for (let i = 0; i < rows.length; i++) {
          const row = rows[i];
          const rowCanvas = await html2canvas(row, {
            scale: 2,
            useCORS: true
          });

          const rowImgData = rowCanvas.toDataURL('image/jpeg', 0.8);
          const rowImgWidth = 190;
          const rowImgHeight = rowCanvas.height * rowImgWidth / rowCanvas.width;

          // 检查是否需要新页面
          if (currentY + rowImgHeight > pageHeight) {
            pdf.addPage();
            // 在新页面重新添加表头
            pdf.addImage(headerImgData, 'JPEG', 10, 10, headerImgWidth, headerImgHeight);
            currentY = 10 + headerImgHeight + 2; // 重置当前位置到表头下方
          }

          // 添加行内容
          pdf.addImage(rowImgData, 'JPEG', 10, currentY, rowImgWidth, rowImgHeight);
          currentY += rowImgHeight + 2; // 更新垂直位置，添加小间距
        }

        // 完全隐藏打印区域
        printableElement.style.display = 'none';
        printableElement.style.position = 'fixed';
        printableElement.style.top = '-9999px';
        printableElement.style.left = '-9999px';
        printableElement.style.visibility = 'hidden';
        printableElement.style.zIndex = '-1000';
        printableElement.style.opacity = '0';

        // 保存PDF
        pdf.save(`漏洞扫描报告_${this.result.ip}_${new Date().toISOString().split('T')[0]}.pdf`);

        this.$message.success('报告已生成');
      } catch (error) {
        console.error('Error generating PDF:', error);
        this.$message.error('生成报告时发生错误');

        // 确保错误情况下也完全隐藏打印区域
        const printableElement = document.getElementById('printable');
        if (printableElement) {
          printableElement.style.display = 'none';
          printableElement.style.position = 'fixed';
          printableElement.style.top = '-9999px';
          printableElement.style.left = '-9999px';
          printableElement.style.visibility = 'hidden';
          printableElement.style.zIndex = '-1000';
          printableElement.style.opacity = '0';
        }
      }
      this.printLoading = false;
    }
  },

  mounted() {
    this.fetchAliveHosts(); // 新增：组件挂载时获取活跃IP列表
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

/* 打印样式 */
@media print {
  #printable {
    display: block;
    font-size: 12px;
    background: white;
  }

  .container>*:not(#printable) {
    display: none;
  }
}

/* 隐藏打印区域 */
#printable {
  display: none;
  position: fixed;
  /* 改为fixed定位 */
  top: -9999px;
  /* 移出可视区域 */
  left: -9999px;
  visibility: hidden;
  /* 添加visibility属性进一步隐藏 */
  z-index: -1000;
  /* 确保在最底层 */
  opacity: 0;
  /* 完全透明 */
  pointer-events: none;
  /* 防止鼠标交互 */
  background: white;
  margin: 0;
  padding: 0;
}


#printable .print-page {
  padding: 40px;
  font-size: 30px;
}

#printable .print-title {
  font-size: 50px;
  font-weight: bold;
  margin-bottom: 30px;
}

#printable .print-info {
  font-size: 18px;
  /* 原来是120px但显示效果不如预期 */
  line-height: 2;
  margin: 30px 0;
  font-weight: bold;
  /* 增加粗体提高可读性 */
}

#printable .print-info p {
  margin: 15px 0;
  /* 增加行间距 */
  font-size: 30px;
  /* 确保内部段落也有正确的字体大小 */
}

#printable h2 {
  font-size: 40px;
  margin: 20px 0;
}

#printable .print-table {
  width: 100%;
  margin-top: 20px;
  font-size: 25px;
}

#printable .print-table th {
  font-size: 30px;
  font-weight: bold;
  background-color: #f5f7fa;
  padding: 30px 15px;
}

#printable .print-table td {
  padding: 10px 8px;
  line-height: 1.4;
}

/* 确保表格内容不会太拥挤 */
#printable .print-table th,
#printable .print-table td {
  min-width: 80px;
  max-width: 300px;
}

/* 默认隐藏打印区域 */
#printable {
  display: none;
}

.print-page {
  padding: 40px;
  page-break-after: always;
}

.print-title {
  text-align: center;
  margin-bottom: 40px;
}

.print-info {
  margin: 20px 0;
  line-height: 1.8;
}

.print-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
}

.print-table th,
.print-table td {
  border: 1px solid #dcdfe6;
  padding: 8px;
  text-align: center;
}

.print-table th {
  background-color: #f5f7fa;
}

.poc-list {
  max-height: 200px;
  overflow-y: auto;
}

.clearfix:after {
  content: "";
  display: table;
  clear: both;
}
</style>