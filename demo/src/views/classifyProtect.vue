<template>
  <div class="security-assessment-container">
    <!-- 头部区域 -->
    <div class="header-section">
      <h1 class="main-title">等级保护测评系统</h1>
      <div class="system-info">
        <el-tag type="info">{{ new Date().toLocaleString() }}</el-tag>
      </div>
    </div>

    <!-- 控制面板区域 -->
    <div class="control-panel">
      <el-card class="control-card">
        <div class="control-row">
          <!-- IP选择 -->
          <div class="control-item">
            <el-select
                v-model="selectedIP"
                placeholder="选择服务器IP"
                @change="changeServer"
                size="medium">
              <el-option
                  v-for="ip in serverIPs"
                  :key="ip"
                  :label="ip"
                  :value="ip">
              </el-option>
            </el-select>
          </div>

          <!-- 等级保护级别选择 -->
          <div class="control-item">
            <el-select
                v-model="protectionLevel"
                placeholder="选择等保级别"
                @change="changeProtectionLevel"
                size="medium">
              <el-option label="二级等保" value="2"></el-option>
              <el-option label="三级等保" value="3"></el-option>
            </el-select>
          </div>

          <!-- 状态筛选 -->
          <div class="control-item">
            <el-select
                v-model="selectedStatus"
                placeholder="请选择状态"
                size="medium">
              <el-option label="全部" value="all"></el-option>
              <el-option label="通过" value="passed"></el-option>
              <el-option label="未通过" value="failed"></el-option>
            </el-select>
          </div>

          <!-- 搜索框 -->
          <div class="control-item search-box">
            <el-input
                placeholder="输入检测项关键字..."
                v-model="searchTerm"
                @input="filterSearchResults"
                prefix-icon="el-icon-search"
                size="medium">
            </el-input>
          </div>
        </div>

        <div class="action-row">
          <el-button
              @click="computeResult"
              type="primary"
              icon="el-icon-data-analysis"
              size="medium">
            计算评分
          </el-button>
<!--          <el-button-->
<!--              @click="onExportToPDF"-->
<!--              :loading="pdfLoading"-->
<!--              type="success"-->
<!--              icon="el-icon-document"-->
<!--              size="medium">-->
<!--            导出PDF报告-->
<!--          </el-button>-->

          <!-- 显示结果 -->
          <div class="result-display">
            <div class="score-card">
              <div class="score-label">得分：</div>
              <div class="score-value">{{ resultScore !== '' ? Number(resultScore).toFixed(1) : '--' }}</div>
            </div>
            <div class="conclusion-card">
              <div class="conclusion-label">结论：</div>
              <div class="conclusion-value">
                <template v-if="resultScore !== ''">
                  <span v-if="resultScore >= 90">优</span>
                  <span v-else-if="resultScore >= 80 && resultScore < 90">良</span>
                  <span v-else-if="resultScore >= 70 && resultScore < 80">中</span>
                  <span v-else>差</span>
                </template>
                <template v-else>--</template>
              </div>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 服务器信息卡片 -->
    <div class="server-info-section" v-if="Object.keys(serverInfo).length > 0">
      <el-card class="server-info-card">
        <div slot="header" class="card-header">
          <span><i class="el-icon-monitor"></i> 服务器信息</span>
          <el-button
              style="float: right; padding: 3px 0"
              type="text"
              @click="toggleServerInfo">
            {{ showServerInfo ? '隐藏' : '显示' }}
          </el-button>
        </div>
        <div v-if="showServerInfo" class="server-info-grid">
          <div class="info-item">
            <span class="info-label">主机名：</span>
            <span class="info-value">{{ serverInfo.hostname || '未知' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">架构：</span>
            <span class="info-value">{{ serverInfo.arch || '未知' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">CPU信息：</span>
            <span class="info-value">{{ serverInfo.cpu || '未知' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">物理CPU个数：</span>
            <span class="info-value">{{ serverInfo.cpuPhysical || '未知' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">CPU核心数：</span>
            <span class="info-value">{{ serverInfo.cpuCore || '未知' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">空闲内存：</span>
            <span class="info-value">{{ serverInfo.free || '未知' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">硬件型号：</span>
            <span class="info-value">{{ serverInfo.ProductName || '未知' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">版本信息：</span>
            <span class="info-value">{{ serverInfo.version || '未知' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">联网状态：</span>
            <span class="info-value">{{ serverInfo.isInternet || '未知' }}</span>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 表格区域 -->
    <div class="table-section">
      <el-card class="table-card">
        <el-table
            :data="filteredCheckresults"
            style="width: 100%"
            border
            stripe
            :header-cell-style="{background:'#f5f7fa',color:'#606266'}"
            v-loading="loading">
          <el-table-column prop="description" label="检测项" min-width="180"></el-table-column>
          <el-table-column prop="basis" label="检测依据" min-width="180"></el-table-column>
          <el-table-column prop="importantLevel" label="重要程度" width="100">
            <template slot-scope="scope">
              <el-tag :type="getImportanceLevelType(scope.row.importantLevel)">
                {{ scope.row.importantLevel }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="result" label="检测结果" min-width="150"></el-table-column>
          <el-table-column prop="IsComply" label="是否符合基线" width="120">
            <template slot-scope="scope">
              <el-tag :type="scope.row.IsComply === 'true' ? 'success' : 'danger'">
                {{ scope.row.IsComply === 'true' ? '符合' : '不符合' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="recommend" label="修改建议" min-width="250"></el-table-column>
          <el-table-column label="结果评分" width="120">
            <template slot-scope="scope">
              <el-select
                  v-model="scope.row.score"
                  placeholder="请选择评分"
                  size="mini">
                <el-option label="符合" value="1"></el-option>
                <el-option label="部分符合" value="0.5"></el-option>
                <el-option label="不符合" value="0"></el-option>
              </el-select>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>

    <!-- PDF输出内容 (隐藏) -->
    <div class="pdf-content" v-show="showContentForPDF">
      <div class="server1">
        <h1 id="linuxBaseline2" style="font-size: 24pt; text-align: center;">Linux等级保护测评报告</h1>

        <!-- 报告头部信息 -->
        <div style="text-align:right; margin-top:20px;">
          <p style="font-size:18px;">检测时间：{{ new Date().toLocaleString() }}</p>
          <p style="font-size:18px;">等保级别：{{ protectionLevel === '2' ? '二级等保' : '三级等保' }}</p>
          <p style="font-size:18px;">服务器IP：{{ selectedIP || '未选择' }}</p>
        </div>

        <!-- 空白分隔 -->
        <div style="height:50px;"></div>

        <!-- 评分结果 -->
        <div class="result-container2" style="font-size: 18pt;">
          <div style="font-size: 20pt;margin-right: 200px;">测评得分：{{ resultScore !== '' ? Number(resultScore).toFixed(1) : '--' }}</div>

          <div style="height:10px;"></div>
          <div style="font-size: 20pt;">
            结论：
            <template v-if="resultScore !== ''">
              <span v-if="resultScore >= 90">优</span>
              <span v-else-if="resultScore >= 80 && resultScore < 90">良</span>
              <span v-else-if="resultScore >= 70 && resultScore < 80">中</span>
              <span v-else>差</span>
            </template>
          </div>

          <!-- 空行 -->
          <div style="height:30px;"></div>

          <!-- 服务器信息 -->
          <el-row :gutter="20">
            <el-col :span="24"><p style="font-size: 15pt;">主机名：{{ serverInfo.hostname || '未知' }}</p></el-col>
            <el-col :span="24"><p style="font-size: 15pt;">主机架构：{{ serverInfo.arch || '未知' }}</p></el-col>
            <el-col :span="24"><p style="font-size: 15pt;">主机CPU信息：{{ serverInfo.cpu || '未知' }}</p></el-col>
            <el-col :span="24"><p style="font-size: 15pt;">主机物理CPU个数：{{ serverInfo.cpuPhysical || '未知' }}</p></el-col>
            <el-col :span="24"><p style="font-size: 15pt;">主机物理CPU核心数：{{ serverInfo.cpuCore || '未知' }}</p></el-col>
            <el-col :span="12"><p style="font-size: 15pt;">主机空闲内存：{{ serverInfo.free || '未知' }}</p></el-col>
            <el-col :span="24"><p style="font-size: 15pt;">硬件型号：{{ serverInfo.ProductName || '未知' }}</p></el-col>
            <el-col :span="24"><p style="font-size: 15pt;">主机版本信息：{{ serverInfo.version || '未知' }}</p></el-col>
            <el-col :span="24"><p style="font-size: 15pt;">联网检测：{{ serverInfo.isInternet || '未知' }}</p></el-col>
          </el-row>
        </div>

        <!-- 空白分隔 -->
        <div style="height:200px;"></div>

        <!-- 检测人员签名 -->
        <div style="text-align:right; margin-top:20px;">
          <span style="font-size:20px;">检测人员签名：</span>
          <img src="../assets/szj.jpg" alt="Signature 1" style="max-width:150px;">
          <img src="../assets/hjj.jpg" alt="Signature 2" style="max-width:150px;">
          <img src="../assets/dyy.jpg" alt="Signature 3" style="max-width:150px;">
        </div>
      </div>

      <!-- PDF 表格部分 -->
      <el-table :data="filteredCheckresults" style="width: 100%" border>
        <el-table-column prop="description" label="检测项"></el-table-column>
        <el-table-column prop="basis" label="检测依据"></el-table-column>
        <el-table-column prop="importantLevel" label="重要程度" width="100"></el-table-column>
        <el-table-column prop="result" label="检测结果"></el-table-column>
        <el-table-column prop="IsComply" label="是否符合基线" width="120">
          <template slot-scope="scope">
            <span :class="{ 'failed-result': scope.row.IsComply === 'false' }">
              {{ scope.row.IsComply === 'true' ? '符合' : '不符合' }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="recommend" label="修改建议" width="400"></el-table-column>
        <el-table-column label="结果评分" width="120">
          <template slot-scope="scope">
            <span>{{ getScoreText(scope.row.score) }}</span>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script>
import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';
// import {Message} from "element-ui";
import axios from "axios";

export default {
  name: "baseCheck",
  data() {
    return {
      checkresults: [],
      serverInfo: {},
      serverIPs: [], // 示例IP列表
      selectedIP: '',
      protectionLevel: '2', // 默认二级等保
      selectedStatus: 'all',
      searchTerm: '',
      resultScore: localStorage.getItem('resultScore') || '',
      showContentForPDF: false,
      loading: false,
      showServerInfo: true,
      pdfLoading:false,
    }
  },
  computed: {
    filteredCheckresults() {
      return this.checkresults.filter(result => {
        const matchesStatus = this.selectedStatus === 'all' ||
            (this.selectedStatus === 'passed' && result.IsComply === 'true') ||
            (this.selectedStatus === 'failed' && result.IsComply === 'false');
        const matchesSearch = !this.searchTerm ||
            result.description.toLowerCase().includes(this.searchTerm.toLowerCase());
        return matchesStatus && matchesSearch;
      });
    },
    getScoreText() {
      return (score) => {
        const numericScore = parseFloat(score);
        if (numericScore === 1) {
          return '符合';
        } else if (numericScore === 0.5) {
          return '部分符合';
        } else if (numericScore === 0) {
          return '不符合';
        } else {
          return '未知';
        }
      };
    }
  },
  methods: {
    // fetchAliveHosts() {
    //   fetch('/api/getAliveHosts')
    //       .then(response => {
    //         if (!response.ok) {
    //           throw new Error(`HTTP status ${response.status}`);
    //         }
    //         return response.json();
    //       })
    //       .then(data => {
    //         this.serverIPs = data.alive_hosts;
    //         if (this.serverIPs && this.serverIPs.length > 0) {
    //           this.selectedIP = this.serverIPs[0];
    //           this.fetchAndDisplayChenckResults();
    //         }
    //         // this.selectedIP=data.alive_hosts[0];
    //       })
    //       .catch(error => {
    //         Message.error('获取活跃IP列表失败：' + error.message);
    //       });
    // },
    fetchAliveHosts() {
      axios.get('/api/getAliveHosts')
          .then(response => {
            this.serverIPs = response.data.alive_hosts;
            // 如果有IP，默认选择第一个
            if (this.serverIPs && this.serverIPs.length > 0) {
              this.selectedIP = this.serverIPs[0];
              this.fetchAndDisplayCheckResults();
            }
          })
          .catch(error => {
            console.error('获取活跃IP列表失败:', error);
            this.$message.error('获取活跃IP列表失败');
          });
    },
    // 切换服务器信息显示
    toggleServerInfo() {
      this.showServerInfo = !this.showServerInfo;
    },

    // 根据重要程度返回对应的标签类型
    getImportanceLevelType(level) {
      switch(level) {
        case '高':
          return 'danger';
        case '中':
          return 'warning';
        case '低':
          return 'info';
        default:
          return '';
      }
    },

    // 更改服务器
    changeServer() {
      this.loading = true;
      // 这里模拟向后端发送请求获取指定IP的服务器数据
      setTimeout(() => {
        this.fetchAndDisplayCheckResults();
        this.loading = false;
      }, 1000);
    },

    // 更改等保级别
    changeProtectionLevel() {
      this.loading = true;
      // 这里模拟向后端发送请求获取指定等保级别的检测项
      setTimeout(() => {
        this.fetchAndDisplayCheckResults();
        this.loading = false;
      }, 1000);
    },

    // 获取检测结果
    fetchAndDisplayCheckResults() {
      this.loading = true;

      // 构建请求参数，包含选择的IP和等保级别
      const params = new URLSearchParams();
      if (this.selectedIP) {
        params.append('ip', this.selectedIP);
      }
      //params.append('level', this.protectionLevel);

      // 发送请求
      fetch(`/api/userinfo?${params.toString()}`)
          .then(response => response.json())
          .then(data => {
            this.checkresults = data.checkResults.map(item => ({
              ...item,
              score: item.IsComply === 'true' ? '1' : '0.5'
            }));
            this.serverInfo = data.serverInfo;
            this.loading = false;
          })
          .catch(error => {
            console.error('Error:', error);
            this.loading = false;
            this.$message.error('获取检测结果失败，请重试！');
          });
    },

    // 计算结果
    computeResult() {
      this.loading = true;

      const scoreMeasures = this.checkresults.map(item => ({
        importantLevelJson: item.importantLevel,
        IsComplyLevel: item.score.toString(),
      }));

      // 添加等保级别参数
      const requestData = {
        scoreMeasures,
        protectionLevel: this.protectionLevel,
        serverIP: this.selectedIP
      };

      fetch('/api/classifyProtect', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestData)
      })
          .then(response => response.json())
          .then(data => {
            console.log("Received score from backend:", data.score);
            this.resultScore = data.score;
            localStorage.setItem('resultScore', this.resultScore);
            this.loading = false;
            this.$message.success('评分计算完成！');
          })
          .catch(error => {
            console.error('Error:', error);
            this.loading = false;
            this.$message.error('评分计算失败，请重试！');
          });
    },

    // 导出PDF
    // 导出PDF
    onExportToPDF() {
      this.pdfLoading = true; // 开始时设置loading为true
      this.showContentForPDF = true;

      this.$message({
        message: '正在生成PDF，请稍候...',
        type: 'info',
        duration: 2000
      });

      setTimeout(() => {
        const pdf = new jsPDF({
          orientation: 'p',
          unit: 'mm',
          format: 'a4'
        });

        // 渲染PDF的服务器信息页
        const contentForPDF = this.$el.querySelector('.pdf-content .server1');
        html2canvas(contentForPDF, {
          scale: 2,
          useCORS: true
        }).then(canvas => {
          const imgData = canvas.toDataURL('image/jpeg', 0.8);
          const imgWidth = 190;
          let imgHeight = canvas.height * imgWidth / canvas.width;

          pdf.addImage(imgData, 'JPEG', 10, 10, imgWidth, imgHeight);
          pdf.addPage();

          // 渲染表头
          const header = this.$el.querySelector('.pdf-content .el-table__header-wrapper');
          if (header) {
            html2canvas(header, {
              scale: 2,
              useCORS: true
            }).then(canvas => {
              const imgData = canvas.toDataURL('image/jpeg', 0.8);
              const imgWidth = 190;
              let imgHeight = canvas.height * imgWidth / canvas.width;

              pdf.addImage(imgData, 'JPEG', 10, 10, imgWidth, imgHeight);
              processRows(10 + imgHeight + 2);
            });
          }

          const processRows = (pdfY) => {
            const exportContents = this.$el.querySelectorAll('.pdf-content .el-table__body-wrapper table tr');
            const pageHeight = pdf.internal.pageSize.getHeight() - 20;

            const processRow = (index) => {
              if (index < exportContents.length) {
                const row = exportContents[index];
                html2canvas(row, {
                  scale: 2,
                  useCORS: true
                }).then(canvas => {
                  const imgData = canvas.toDataURL('image/jpeg', 0.8);
                  const imgWidth = 190;
                  let imgHeight = canvas.height * imgWidth / canvas.width;

                  if (pdfY + imgHeight > pageHeight) {
                    pdf.addPage();
                    pdfY = 10;
                  }

                  pdf.addImage(imgData, 'JPEG', 10, pdfY, imgWidth, imgHeight);
                  pdfY += imgHeight + 2;

                  processRow(index + 1);
                });
              } else {
                const filename = `等保测评报告_${this.selectedIP || '未知IP'}_${this.protectionLevel}级_${new Date().toISOString().slice(0,10)}.pdf`;
                pdf.save(filename);
                this.showContentForPDF = false;
                this.pdfLoading = false; // 在PDF生成完成后关闭loading状态
                this.$message.success('PDF报告导出成功！');
              }
            };

            processRow(0);
          };
        }).catch(error => {
          console.error('PDF生成错误:', error);
          this.showContentForPDF = false;
          this.pdfLoading = false; // 发生错误时也要关闭loading
          this.$message.error('PDF生成失败，请重试！');
        });
      }, 1000);
      // 删除这里的 this.pdfLoading = false;，让它在PDF完成时才设置为false
    },


    // 搜索过滤
    filterSearchResults() {
      // 这个方法由于使用了计算属性，现在可以为空，
      // 但保留此方法为将来可能的扩展
    }
  },
  mounted() {
    // this.fetchAndDisplayCheckResults();
    this.fetchAliveHosts();
  }
}
</script>

<style scoped>
.security-assessment-container {
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

.control-panel {
  margin-bottom: 20px;
}

.control-card {
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.control-row {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  margin-bottom: 15px;
}

.action-row {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 15px;
}

.control-item {
  min-width: 180px;
}

.search-box {
  flex-grow: 1;
}

.result-display {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-left: auto;
}

.score-card, .conclusion-card {
  display: flex;
  align-items: center;
  background: #f5f7fa;
  padding: 8px 15px;
  border-radius: 4px;
}

.score-label, .conclusion-label {
  font-size: 16px;
  font-weight: bold;
  color: #606266;
  margin-right: 5px;
}

.score-value {
  font-size: 18px;
  font-weight: bold;
  color: #f56c6c;
}

.conclusion-value {
  font-size: 18px;
  font-weight: bold;
  color: #f56c6c;
}

.server-info-section {
  margin-bottom: 20px;
}

.server-info-card {
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 16px;
  font-weight: bold;
}

.server-info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 15px;
}

.info-item {
  display: flex;
  align-items: center;
}

.info-label {
  font-weight: bold;
  color: #606266;
  margin-right: 5px;
}

.info-value {
  color: #303133;
}

.table-section {
  margin-bottom: 20px;
}

.table-card {
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.failed-result {
  color: #f56c6c;
}

/* PDF内容样式 */
.pdf-content {
  font-size: 10pt;
  max-width: 297mm;
  padding: 15mm;
  box-sizing: border-box;
  background: white;
}

.pdf-content h1 {
  font-size: 14pt;
}

.pdf-content p {
  font-size: 9pt;
}

@media print {
  .pdf-content {
    width: 210mm;
    height: 297mm;
  }
}

.el-table .warning-row {
  background: rgba(245, 108, 108, 0.1);
}

.el-table .success-row {
  background: rgba(103, 194, 58, 0.1);
}
</style>

<!--<template>-->
<!--  <div>-->
<!--    <h1 id="linuxBaseline">等级保护测评</h1>-->
<!--    <el-button @click="onExportToPDF" style="width: 120px;margin-right: 20px;">导出 pdf 报告</el-button>-->

<!--    <el-select v-model="selectedStatus" placeholder="请选择状态" style="width: 120px;margin-right: 20px;">-->
<!--      <el-option label="全部" value="all"></el-option>-->
<!--      <el-option label="通过" value="passed"></el-option>-->
<!--      <el-option label="未通过" value="failed"></el-option>-->
<!--    </el-select>-->

<!--    <el-input placeholder="输入检测项关键字..." v-model="searchTerm" @input="filterSearchResults" style="width: 300px;margin-right: 20px;"></el-input>-->
<!--    <el-button @click="computeResult" type="primary" style="margin-right: 30px;">计算评分</el-button>-->
<!--    <div class="result-container">-->
<!--      <div class="score-display">得分：<span style="color: indianred">{{ resultScore !== '' ? Number(resultScore).toFixed(1) : '' }}</span></div>-->
<!--      <div class="conclusion">-->
<!--        结论：-->
<!--        <span style="color: indianred">-->
<!--        <template v-if="resultScore !== ''">-->
<!--          <span v-if="resultScore >= 90">优</span>-->
<!--          <span v-else-if="resultScore >= 80 && resultScore < 90">良</span>-->
<!--          <span v-else-if="resultScore >= 70 && resultScore < 80">中</span>-->
<!--          <span v-else>差</span>-->
<!--        </template>-->
<!--        </span>-->
<!--      </div>-->
<!--    </div>-->

<!--    <el-table :data="filteredCheckresults" style="width: 100%">-->
<!--&lt;!&ndash;      <el-table-column type="selection" width="55"></el-table-column>&ndash;&gt;-->
<!--      <el-table-column prop="description" label="检测项"></el-table-column>-->
<!--      <el-table-column prop="basis" label="检测依据"></el-table-column>-->
<!--      <el-table-column prop="importantLevel" label="重要程度"></el-table-column>-->
<!--      <el-table-column prop="result" label="检测结果"></el-table-column>-->
<!--      <el-table-column prop="IsComply" label="是否符合基线" width="150%">-->
<!--        <template slot-scope="scope">-->
<!--          <span :class="{ 'failed-result': scope.row.IsComply === 'false' }">{{ scope.row.IsComply }}</span>-->
<!--        </template>-->
<!--      </el-table-column>-->
<!--      <el-table-column prop="recommend" label="修改建议" width="400%"></el-table-column>-->
<!--      <el-table-column label="结果评分" width="180">-->
<!--        <template slot-scope="scope">-->
<!--          <el-select v-model="scope.row.score" placeholder="请选择评分">-->
<!--            <el-option label="符合" value="1"></el-option>-->
<!--            <el-option label="部分符合" value="0.5"></el-option>-->
<!--            <el-option label="不符合" value="0"></el-option>-->
<!--          </el-select>-->
<!--        </template>-->
<!--      </el-table-column>-->
<!--    </el-table>-->

<!--    &lt;!&ndash; 这部分内容在正常情况下不显示，只在导出 PDF 时显示 &ndash;&gt;-->
<!--    <div class="pdf-content" v-show="showContentForPDF">-->
<!--      <div class="server1">-->
<!--        <h1 id="linuxBaseline2" style="font-size: 24pt; text-align: center;">Linux等级保护测评报告</h1>-->
<!--        &lt;!&ndash; 检测时间 &ndash;&gt;-->
<!--        <div style="text-align:right; margin-top:20px;">-->
<!--          <p style="font-size:18px;">检测时间：{{ new Date().toLocaleString() }}</p>-->
<!--        </div>-->
<!--        &lt;!&ndash; 空白分隔 &ndash;&gt;-->
<!--        <div style="height:100px;"></div>-->
<!--        <div class="result-container2" style="font-size: 18pt;">-->
<!--          <div style="font-size: 20pt;margin-right: 200px;">测评得分：{{ resultScore }}</div>-->

<!--          <div style="height:10px;"></div>-->
<!--          <div style="font-size: 20pt;">-->
<!--            结论：-->
<!--            <template v-if="resultScore !== ''">-->
<!--              <span v-if="resultScore >= 90">优</span>-->
<!--              <span v-else-if="resultScore >= 80 && resultScore < 90">良</span>-->
<!--              <span v-else-if="resultScore >= 70 && resultScore < 80">中</span>-->
<!--              <span v-else>差</span>-->
<!--            </template>-->
<!--          </div>-->

<!--          &lt;!&ndash; Add a line break here to start a new line &ndash;&gt;-->
<!--          <div style="height:30px;"></div>-->

<!--          <el-row :gutter="20">-->
<!--            <el-col :span="24"><p style="font-size: 15pt;">主机名：{{ serverInfo.hostname }}</p></el-col>-->
<!--            <el-col :span="24"><p style="font-size: 15pt;">主机架构：{{ serverInfo.arch }}</p></el-col>-->
<!--            <el-col :span="24"><p style="font-size: 15pt;">主机CPU信息：{{ serverInfo.cpu }}</p></el-col>-->
<!--            <el-col :span="24"><p style="font-size: 15pt;">主机物理CPU个数：{{ serverInfo.cpuPhysical }}</p></el-col>-->
<!--            <el-col :span="24"><p style="font-size: 15pt;">主机物理CPU核心数：{{ serverInfo.cpuCore }}</p></el-col>-->
<!--            <el-col :span="12"><p style="font-size: 15pt;">主机空闲内存：{{ serverInfo.free }}</p></el-col>-->
<!--            <el-col :span="24"><p style="font-size: 15pt;">硬件型号：{{ serverInfo.ProductName }}</p></el-col>-->
<!--            <el-col :span="24"><p style="font-size: 15pt;">主机版本信息：{{ serverInfo.version }}</p></el-col>-->
<!--            <el-col :span="24"><p style="font-size: 15pt;">联网检测：{{ serverInfo.isInternet }}</p></el-col>-->
<!--          </el-row>-->
<!--        </div>-->
<!--        &lt;!&ndash; 空白分隔 &ndash;&gt;-->
<!--        <div style="height:250px;"></div>-->
<!--        &lt;!&ndash; 检测人员签名 &ndash;&gt;-->
<!--        <div style="text-align:right; margin-top:20px;">-->
<!--          <span style="font-size:20px;">检测人员签名：</span>-->
<!--          <img src="../assets/szj.jpg" alt="Signature 1" style="max-width:150px;">-->
<!--          <img src="../assets/hjj.jpg" alt="Signature 2" style="max-width:150px;">-->
<!--          <img src="../assets/dyy.jpg" alt="Signature 3" style="max-width:150px;">-->
<!--        </div>-->
<!--      </div>-->


<!--      <el-table :data="filteredCheckresults" style="width: 100%">-->
<!--        <el-table-column prop="description" label="检测项"></el-table-column>-->
<!--        <el-table-column prop="basis" label="检测依据"></el-table-column>-->
<!--        <el-table-column prop="result" label="检测结果"></el-table-column>-->
<!--        <el-table-column prop="IsComply" label="是否符合基线" width="120%">-->
<!--          <template slot-scope="scope">-->
<!--            <span :class="{ 'failed-result': scope.row.IsComply === 'false' }">{{ scope.row.IsComply }}</span>-->
<!--          </template>-->
<!--        </el-table-column>-->
<!--        <el-table-column prop="recommend" label="修改建议" width="400%"></el-table-column>-->
<!--        <el-table-column label="结果评分" width="180">-->
<!--          <template slot-scope="scope">-->
<!--            <span>{{ getScoreText(scope.row.score) }}</span>-->
<!--          </template>-->
<!--        </el-table-column>-->
<!--      </el-table>-->
<!--    </div>-->
<!--  </div>-->



<!--</template>-->

<!--<script>-->

<!--import jsPDF from 'jspdf';//用于在客户端生成 PDF 文件-->
<!--import html2canvas from 'html2canvas';//将 HTML 元素转换为画布 (canvas) 图像-->

<!--export default {-->
<!--  name: "baseCheck",-->
<!--  data() {-->
<!--    return {-->
<!--      checkresults: [],-->
<!--      serverInfo:{},-->
<!--      selectedStatus: 'all',-->
<!--      searchTerm: '',-->
<!--      resultScore: localStorage.getItem('resultScore') || '',-->
<!--      showContentForPDF: false // 控制内容显示的数据属性-->
<!--    }-->
<!--  },-->
<!--  computed: {-->
<!--    filteredCheckresults() {-->
<!--      return this.checkresults.filter(result => {-->
<!--        const matchesStatus = this.selectedStatus === 'all' ||-->
<!--            (this.selectedStatus === 'passed' && result.IsComply === 'true') ||-->
<!--            (this.selectedStatus === 'failed' && result.IsComply === 'false');-->
<!--        const matchesSearch = !this.searchTerm ||-->
<!--            result.description.toLowerCase().includes(this.searchTerm.toLowerCase());-->
<!--        return matchesStatus && matchesSearch;-->
<!--      });-->
<!--    },-->
<!--    getScoreText() {-->
<!--      return (score) => {-->
<!--        const numericScore = parseFloat(score); // 将 score 转换为数字-->
<!--        if (numericScore === 1) {-->
<!--          return '符合';-->
<!--        } else if (numericScore === 0.5) {-->
<!--          return '部分符合';-->
<!--        } else if (numericScore === 0) {-->
<!--          return '不符合';-->
<!--        } else {-->
<!--          return '未知';-->
<!--        }-->
<!--      };-->
<!--    }-->
<!--  },-->
<!--  methods: {-->
<!--    fetchAndDisplayCheckResults() {-->
<!--      fetch('/api/userinfo')-->
<!--          .then(response => response.json())-->
<!--          .then(data => {-->
<!--            this.checkresults = data.Event_result.map(item => ({-->
<!--              ...item,-->
<!--              score: item.IsComply === 'true' ? '1' : '0.5'-->
<!--              //score: item.score || '1' // 从后端获取评分数据，如果没有则默认空-->
<!--            }));-->
<!--            this.serverInfo = data.ServerInfo;-->
<!--          })-->
<!--          .catch(error => console.error('Error:', error));-->
<!--    },-->
<!--    computeResult() {-->
<!--      const scoreMeasures = this.checkresults.map(item => ({-->
<!--        importantLevelJson: item.importantLevel,-->
<!--        IsComplyLevel: item.score.toString(),-->
<!--      }));-->

<!--      fetch('/api/classifyProtect', {-->
<!--        method: 'POST',-->
<!--        headers: {-->
<!--          'Content-Type': 'application/json'-->
<!--        },-->
<!--        body: JSON.stringify({ scoreMeasures })-->
<!--      })-->
<!--          .then(response => response.json())-->
<!--          .then(data => {-->
<!--            console.log("Received score from backend:", data.score); // Log the received score-->
<!--            this.resultScore = data.score; // 更新 resultScore-->
<!--            localStorage.setItem('resultScore', this.resultScore); // 将 resultScore 存储到 localStorage 中-->
<!--          })-->
<!--          .catch(error => console.error('Error:', error));-->
<!--    },-->
<!--    onExportToPDF() {-->
<!--      this.showContentForPDF = true; // 确保PDF相关内容是可见的-->

<!--      setTimeout(() => { // 增加延迟确保DOM完全更新-->
<!--        const pdf = new jsPDF({-->
<!--          orientation: 'p', // 横向-->
<!--          unit: 'mm',//单位为毫米-->
<!--          format: 'a4'//页面格式为A4-->
<!--        });-->
<!--        // 渲染PDF的服务器信息页-->
<!--        const contentForPDF = this.$el.querySelector('.pdf-content .server1');-->
<!--        html2canvas(contentForPDF, {-->
<!--          scale: 2,-->
<!--          useCORS: true-->
<!--        }).then(canvas => {-->
<!--          //const imgData = canvas.toDataURL('image/png');-->
<!--          const imgData = canvas.toDataURL('image/jpeg', 0.8);//用jpeg格式，文件会小一点-->
<!--          const imgWidth = 190; // 适应PDF的宽度-->
<!--          let imgHeight = canvas.height * imgWidth / canvas.width; // 根据比例计算高度-->

<!--          // 将服务器信息页添加到PDF-->
<!--          //pdf.addImage(imgData, 'PNG', 10, 10, imgWidth, imgHeight);-->
<!--          pdf.addImage(imgData, 'JPEG', 10, 10, imgWidth, imgHeight);-->

<!--          // 在添加表格内容之前添加一个新页面-->
<!--          pdf.addPage();-->

<!--          // 首先渲染表头-->
<!--          const header = this.$el.querySelector('.pdf-content .el-table__header-wrapper');-->
<!--          if (header) {-->
<!--            html2canvas(header, {  //转换成画布（canvas）-->
<!--              scale: 2,-->
<!--              useCORS: true-->
<!--            }).then(canvas => {-->
<!--              //const imgData = canvas.toDataURL('image/png');//转换为PNG格式的图像数据-->
<!--              const imgData = canvas.toDataURL('image/jpeg', 0.8);-->
<!--              const imgWidth = 190; // 适应PDF的宽度-->
<!--              let imgHeight = canvas.height * imgWidth / canvas.width; // 根据比例计算高度-->

<!--              //pdf.addImage(imgData, 'PNG', 10, 10, imgWidth, imgHeight);-->
<!--              pdf.addImage(imgData, 'JPEG', 10, 10, imgWidth, imgHeight);-->

<!--              // 然后开始渲染表格行-->
<!--              processRows(10 + imgHeight + 2); // 将表头下面的位置作为起始位置-->
<!--            });-->
<!--          }-->

<!--          //pdfY跟踪当前在PDF页面上的垂直位置-->
<!--          const processRows = (pdfY) => {-->
<!--            const exportContents = this.$el.querySelectorAll('.pdf-content .el-table__body-wrapper table tr');-->
<!--            const pageHeight = pdf.internal.pageSize.getHeight() - 20; // 页面总高度减去上下边距-->

<!--            const processRow = (index) => {-->
<!--              if (index < exportContents.length) {-->
<!--                const row = exportContents[index];-->
<!--                html2canvas(row, {-->
<!--                  scale: 2,-->
<!--                  useCORS: true-->
<!--                }).then(canvas => {-->
<!--                  //const imgData = canvas.toDataURL('image/png');-->
<!--                  const imgData = canvas.toDataURL('image/jpeg', 0.8);-->
<!--                  const imgWidth = 190; // 适应PDF的宽度-->
<!--                  let imgHeight = canvas.height * imgWidth / canvas.width; // 根据比例计算高度-->

<!--                  if (pdfY + imgHeight > pageHeight) {//当前行的图像加上当前的pdfY值超出pageHeight则新建一个pdf页面-->
<!--                    pdf.addPage(); // 添加新页面-->
<!--                    pdfY = 10; // 重置Y位置-->
<!--                  }-->

<!--                  //pdf.addImage(imgData, 'PNG', 10, pdfY, imgWidth, imgHeight);-->
<!--                  pdf.addImage(imgData, 'JPEG', 10, pdfY, imgWidth, imgHeight);-->
<!--                  pdfY += imgHeight + 2; // 更新Y位置，并添加间隔-->

<!--                  processRow(index + 1); // 处理下一行-->
<!--                });-->
<!--              } else {-->
<!--                pdf.save('report.pdf'); // 所有行处理完毕后保存PDF-->
<!--                this.showContentForPDF = false; // 隐藏PDF相关内容-->
<!--              }-->
<!--            };-->

<!--            processRow(0); // 从第一行开始处理-->
<!--          };-->
<!--        });-->
<!--      }, 1000);-->
<!--    }-->


<!--  },-->
<!--  mounted() {-->
<!--    this.fetchAndDisplayCheckResults();-->
<!--  }-->
<!--}-->
<!--</script>-->

<!--<style scoped>-->
<!--.failed-result {-->
<!--  color: red;-->
<!--}-->
<!--.result-container {-->
<!--  display: inline-flex;-->
<!--  align-items: center;-->
<!--  gap: 20px; /* Adds space between score and conclusion */-->
<!--  margin-top: 10px;-->
<!--}-->
<!--.result-container2 {-->
<!--  //display: inline-flex;-->
<!--  align-items: center;-->
<!--  gap: 20px; /* Adds space between score and conclusion */-->
<!--  margin-top: 10px;-->
<!--}-->
<!--.score-display,-->
<!--.conclusion {-->
<!--  font-size: 18px;-->
<!--  font-weight: bold;-->
<!--  color: darkslategrey;-->
<!--}-->

<!--/*文字分割的正确版本*/-->
<!--.pdf-content {-->
<!--  font-size: 10pt; /* 设置字体大小为10磅 */-->
<!--  max-width: 297mm; /* A4 宽度约为 210mm */-->
<!--  padding: 15mm; /* A4 页面常用边距 */-->
<!--  box-sizing: border-box;-->
<!--}-->

<!--/* 单独调整某些元素的字体大小 */-->
<!--.pdf-content h1 {-->
<!--  font-size: 14pt; /* 较大的标题字体 */-->
<!--}-->

<!--.pdf-content p {-->
<!--  font-size: 9pt; /* 正文的字体大小 */-->
<!--}-->
<!--</style>-->

