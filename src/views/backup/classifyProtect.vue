<template>
  <div class="baseline-container">
    <!-- 头部区域 -->
    <div class="header-section">
      <h1 class="main-title">等级保护测评</h1>
      <div class="date-info">
      </div>
    </div>

    <!-- 控制按钮区域 -->
    <div class="control-section">
      <div class="button-group">
        <!-- 新增的IP选择下拉框 -->
        <div class="control-item">
          <el-select v-model="selectedIP" placeholder="选择服务器IP" @change="changeServer" size="medium">
            <el-option v-for="ip in aliveHosts" :key="ip" :label="ip" :value="ip">
            </el-option>
          </el-select>
        </div>

        <el-button @click="onExportToPDF" :loading="pdfLoading" icon="el-icon-document" type="primary" size="medium">
          导出为 PDF
        </el-button>
      </div>

      <div class="filter-group">
        <el-select v-model="selectedStatus" placeholder="请选择状态" size="medium">
          <el-option label="全部" value="all"></el-option>
          <el-option label="通过" value="passed"></el-option>
          <el-option label="未通过" value="failed"></el-option>
        </el-select>

        <el-input placeholder="输入检测项关键字..." v-model="searchTerm" @input="filterSearchResults"
          prefix-icon="el-icon-search" size="medium">
        </el-input>
      </div>

      <!-- 新增保存评分按钮 -->
      <el-button type="success" icon="el-icon-check" @click="saveScores" :loading="saveLoading" size="medium">
        保存人工判定结果
      </el-button>
      <el-button type="primary" icon="el-icon-data-analysis" @click="getProtectionLevelResult" :loading="resultLoading"
        size="medium">
        获取等保结果
      </el-button>
    </div>

    <!-- 得分显示部分，数字得分 -->
    <el-card class="score-card" v-if="showScoreResult" style="margin-bottom: 20px">
      <div slot="header" class="card-header">
        <span><i class="el-icon-data-line"></i> 等保测评结果</span>
        <el-button type="text" @click="showScoreResult = false">
          <i class="el-icon-close"></i>
        </el-button>
      </div>

      <div class="score-content">
        <!-- 替换仪表盘为简单的得分显示 -->
        <div class="score-display">
          <div class="score-title">等保得分</div>
          <div class="score-number" :class="getScoreClass(levelResult.score)">
            {{ formattedScore }}
          </div>
        </div>

        <div class="score-details">
          <div class="detail-item">
            <span class="detail-label">IP地址:</span>
            <span class="detail-value">{{ levelResult.ip || selectedIP }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">等保级别:</span>
            <span class="detail-value">三级</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">评估结论:</span>
            <span class="detail-value" :class="getScoreClass(levelResult.score)">
              {{ getScoreConclusion(levelResult.score) }}
            </span>
          </div>
          <div class="detail-item">
            <span class="detail-label">检测项总数:</span>
            <span class="detail-value">{{ levelResult.totalItems || '0' }}</span>
          </div>
        </div>
      </div>

      <div class="score-summary">
        <div class="summary-text">
          <p>{{ levelResult.message || '三级等保评估结果' }}</p>

          <!-- 根据不同分数区间显示不同的提示信息 -->
          <p v-if="levelResult.score >= 90" class="excellent-text">
            <i class="el-icon-circle-check"></i>
            得分优秀，符合等保三级要求，建议持续保持
          </p>
          <p v-else-if="levelResult.score >= 80" class="good-text">
            <i class="el-icon-circle-check"></i>
            得分良好，基本符合等保三级要求，可进一步完善个别项目
          </p>
          <p v-else-if="levelResult.score >= 60" class="warning-text">
            <i class="el-icon-warning"></i>
            得分基本合格，仍有提升空间，建议优化未完全符合的检测项
          </p>
          <p v-else class="danger-text">
            <i class="el-icon-close"></i>
            得分未达标，建议查看未通过检测项并根据建议进行整改
          </p>
        </div>
      </div>
    </el-card>

    <!-- 检测结果表格 -->
    <el-card class="results-card">
      <div slot="header" class="card-header">
        <span><i class="el-icon-document-checked"></i> 检测结果</span>
        <div class="summary">
          <el-tag type="success">通过: {{ passedCount }}</el-tag>
          <el-tag type="danger">未通过: {{ failedCount }}</el-tag>
          <el-tag type="info">总计: {{ totalCount }}</el-tag>
        </div>
      </div>

      <el-table :data="filteredCheckresults" style="width: 100%" border stripe
        :header-cell-style="{ background: '#f5f7fa', color: '#606266' }" v-loading="tableLoading">
        <el-table-column label="序号" width="70" type="index"></el-table-column>
        <el-table-column prop="description" label="检测项" min-width="150"></el-table-column>
        <el-table-column label="重要程度" width="120">
          <template slot-scope="scope">
            <el-select v-model="scope.row.importantLevel" placeholder="请选择重要程度" size="mini">
              <el-option label="1" value="1"></el-option>
              <el-option label="2" value="2"></el-option>
              <el-option label="3" value="3"></el-option>
            </el-select>
          </template>
        </el-table-column>
        <el-table-column prop="basis" label="基准" min-width="150"></el-table-column>
        <el-table-column prop="result" label="检测结果" min-width="150"></el-table-column>
        <el-table-column label="是否通过检查" width="120">
          <template slot-scope="scope">
            <el-tag :type="scope.row.IsComply === 'true' ? 'success' : 'danger'">
              {{ scope.row.IsComply === 'true' ? '通过' : '未通过' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="修改建议" min-width="250">
          <template slot-scope="scope">
            <span v-if="scope.row.IsComply === 'false'">{{ scope.row.recommend }}</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="是否符合等保要求（人工判定）" width="120">
          <template slot-scope="scope">
            <el-select v-model="scope.row.score" placeholder="请选择评分" size="mini">
              <el-option label="符合" value="1"></el-option>
              <el-option label="部分符合" value="0.5"></el-option>
              <el-option label="不符合" value="0"></el-option>
            </el-select>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- PDF内容（隐藏） -->
    <div class="pdf-content" v-show="showContentForPDF">
      <div class="server1">
        <h1 id="linuxBaseline2">Linux基线检测报告</h1>
        <!-- 检测时间 -->
        <div style="text-align:right; margin-top:20px;">
          <p style="font-size:18px;">检测时间：{{ new Date().toLocaleString() }}</p>
        </div>
        <el-row :gutter="20">
          <el-col :span="24">
            <p>主机名：{{ serverInfo.hostname }}</p>
          </el-col>
          <el-col :span="24">
            <p>主机架构：{{ serverInfo.arch }}</p>
          </el-col>
          <el-col :span="24">
            <p>主机CPU信息：{{ serverInfo.cpu }}</p>
          </el-col>
          <el-col :span="24">
            <p>主机物理CPU个数：{{ serverInfo.cpuPhysical }}</p>
          </el-col>
          <el-col :span="24">
            <p>主机物理CPU核心数：{{ serverInfo.cpuCore }}</p>
          </el-col>
          <el-col :span="12">
            <p>主机空闲内存：{{ serverInfo.free }}</p>
          </el-col>
          <el-col :span="24">
            <p>硬件型号：{{ serverInfo.ProductName }}</p>
          </el-col>
          <el-col :span="24">
            <p>主机版本信息：{{ serverInfo.version }}</p>
          </el-col>
          <el-col :span="24">
            <p>服务器IP：{{ selectedIP }}</p>
          </el-col>
        </el-row>
        <!-- 空白分隔 -->
        <div style="height:200px;"></div>
        <!-- 检测人员签名 -->
        <div style="text-align:right; margin-top:20px;">
          <span style="font-size:20px;">检测人员签名：</span>
          <span style="display: inline-block; width: 200px; border-bottom: 2px solid #000; margin-left: 10px;"></span>
        </div>
        <!-- 页码 -->
        <div class="page-number">
          <span>1/{{ totalPages }}</span>
        </div>
      </div>

      <!-- 测试正文标题 -->
      <div class="report-content-title">
        <h2>测试正文</h2>
      </div>

      <el-table :data="filteredCheckresults" style="width: 100%">
        <el-table-column label="序号" width="70" type="index"></el-table-column>
        <el-table-column prop="description" label="检测项"></el-table-column>
        <el-table-column label="重要程度" width="80">
          <template slot-scope="scope">
            <span :style="{
              color:
                scope.row.importantLevel == '3'
                  ? 'red'
                  : scope.row.importantLevel == '2'
                    ? 'orange'
                    : 'green'
            }">
              {{ scope.row.importantLevel || '2' }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="basis" label="检测依据" min-width="150"></el-table-column>
        <el-table-column prop="result" label="检测结果" min-width="150"></el-table-column>
        <el-table-column prop="IsComply" label="是否通过检查" width="120">
          <template slot-scope="scope">
            <span :class="{ 'failed-result': scope.row.IsComply === 'false' }">
              {{ scope.row.IsComply === 'true' ? '通过' : '未通过' }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="修改建议" width="400">
          <template slot-scope="scope">
            <span v-if="scope.row.IsComply === 'false'">{{ scope.row.recommend }}</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="是否符合等保要求（人工判定）" width="120">
          <template slot-scope="scope">
            <span :style="{
              color:
                scope.row.score == 1
                  ? 'green'
                  : scope.row.score == 0.5
                    ? 'orange'
                    : 'red'
            }">
            </span>
          </template>
        </el-table-column>

      </el-table>
      <!-- 页码容器 - PDF生成时会添加 -->
      <div class="page-numbers-container"></div>
    </div>

  </div>
</template>

<script>
import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';
import axios from 'axios';

export default {
  name: "baseCheck",
  data() {
    return {
      checkresults: [],
      serverInfo: {},
      selectedStatus: 'all',
      searchTerm: '',
      showContentForPDF: false,
      pdfLoading: false,
      tableLoading: false,
      totalPages: 2,
      aliveHosts: [],
      selectedIP: '',
      saveLoading: false,
      resultLoading: false,
      showScoreResult: false,
      levelResult: {
        ip: '',
        message: '',
        score: 0,
        totalItems: 0
      },
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
    passedCount() {
      return this.checkresults.filter(item => item.IsComply === 'true').length;
    },
    failedCount() {
      return this.checkresults.filter(item => item.IsComply === 'false').length;
    },
    totalCount() {
      return this.checkresults.length;
    },
    formattedScore() {
      return this.levelResult.score ? this.levelResult.score.toFixed(2) : '0.00';
    }
  },
  methods: {
    fetchAliveHosts() {
      axios.get('/api/getAliveHosts')
        .then(response => {
          this.aliveHosts = response.data.alive_hosts;
          if (this.aliveHosts && this.aliveHosts.length > 0) {
            this.selectedIP = this.aliveHosts[0];
            this.fetchAndDisplayChenckResults();
          }
        })
        .catch(error => {
          console.error('获取活跃IP列表失败:', error);
          this.$message.error('获取活跃IP列表失败');
        });
    },
    changeServer() {
      if (this.selectedIP) {
        this.fetchAndDisplayChenckResults();
      }
    },
    fetchAndDisplayChenckResults() {
      if (!this.selectedIP) {
        this.$message.warning('请先选择服务器IP');
        return;
      }

      this.tableLoading = true;
      axios.get(`/api/level3Userinfo?ip=${this.selectedIP}`)
        .then(response => {
          this.checkresults = response.data.checkResults.map(item => {
            let score = '0';
            if (item.tmp_IsComply === 'true') {
              score = '1';
            } else if (item.tmp_IsComply === 'half_true') {
              score = '0.5';
            }
            return {
              ...item,
              score: score,
              importantLevel: item.tmp_importantLevel || '2'
            };
          });
          this.tableLoading = false;
          this.estimatePageCount();
        })
        .catch(error => {
          console.error('Error:', error);
          this.tableLoading = false;
          this.$message.error('获取检测结果失败，请重试');
        });
    },
    estimatePageCount() {
      const recordsPerPage = 10;
      this.totalPages = Math.ceil(this.checkresults.length / recordsPerPage) + 1;
    },
    onExportToPDF() {
      this.pdfLoading = true;
      this.showContentForPDF = true;

      this.$message({
        message: '正在生成PDF，请稍候...',
        type: 'info',
        duration: 5000
      });

      setTimeout(() => {
        const pdf = new jsPDF({
          orientation: 'p',
          unit: 'mm',
          format: 'a4'
        });

        this.simulatePdfRendering(pdf).then(actualPageCount => {
          this.totalPages = actualPageCount;
          this.renderFinalPdf(pdf, this.totalPages);
        }).catch(err => {
          console.error('PDF生成过程出错:', err);
          this.pdfLoading = false;
          this.showContentForPDF = false;
          this.$message.error('PDF生成失败，请重试！');
        });
      }, 1000);
    },
    async simulatePdfRendering(pdf) {
      try {
        const originalPage = pdf.internal.getCurrentPageInfo().pageNumber;

        let pageCount = 0;

        const coverPage = this.$el.querySelector('.pdf-content .server1');
        await html2canvas(coverPage, { scale: 2, useCORS: true });
        pageCount = 1;

        pdf.addPage();
        pageCount++;

        const pageHeight = pdf.internal.pageSize.getHeight() - 20;

        const titleElement = this.$el.querySelector('.pdf-content .report-content-title');
        const titleCanvas = await html2canvas(titleElement, { scale: 2, useCORS: true });
        const titleWidth = 190;
        const titleHeight = titleCanvas.height * titleWidth / titleCanvas.width;

        let yPosition = 10 + titleHeight + 5;

        const headerElement = this.$el.querySelector('.pdf-content .el-table__header-wrapper');
        const headerCanvas = await html2canvas(headerElement, { scale: 2, useCORS: true });
        const headerWidth = 190;
        const headerHeight = headerCanvas.height * headerWidth / headerCanvas.width;

        yPosition += headerHeight + 2;

        const tableRows = this.$el.querySelectorAll('.pdf-content .el-table__body-wrapper table tr');

        for (let i = 0; i < tableRows.length; i++) {
          const row = tableRows[i];
          const rowCanvas = await html2canvas(row, { scale: 2, useCORS: true });
          const rowWidth = 190;
          const rowHeight = rowCanvas.height * rowWidth / rowCanvas.width;

          if (yPosition + rowHeight > pageHeight) {
            if (i < tableRows.length - 1) {
              pdf.addPage();
              pageCount++;
              yPosition = 10;
            }
          }

          yPosition += rowHeight + 2;
        }

        while (pdf.internal.getCurrentPageInfo().pageNumber > originalPage) {
          pdf.deletePage(pdf.internal.getCurrentPageInfo().pageNumber);
        }

        return pageCount;
      } catch (error) {
        console.error('模拟渲染计算页数出错:', error);
        throw error;
      }
    },
    async renderFinalPdf(pdf, totalPageCount) {
      try {
        const coverPage = this.$el.querySelector('.pdf-content .server1');
        const coverCanvas = await html2canvas(coverPage, { scale: 2, useCORS: true });
        const imgData = coverCanvas.toDataURL('image/jpeg', 0.8);
        const imgWidth = 190;
        const imgHeight = coverCanvas.height * imgWidth / coverCanvas.width;

        pdf.addImage(imgData, 'JPEG', 10, 10, imgWidth, imgHeight);

        pdf.setFontSize(10);
        pdf.text(`1/${totalPageCount}`, pdf.internal.pageSize.getWidth() - 25, pdf.internal.pageSize.getHeight() - 10);

        pdf.addPage();

        const pageHeight = pdf.internal.pageSize.getHeight() - 20;
        let currentPageNum = 2;

        const titleElement = this.$el.querySelector('.pdf-content .report-content-title');
        const titleCanvas = await html2canvas(titleElement, { scale: 2, useCORS: true });
        const titleImgData = titleCanvas.toDataURL('image/jpeg', 0.8);
        const titleWidth = 190;
        const titleHeight = titleCanvas.height * titleWidth / titleCanvas.width;

        pdf.addImage(titleImgData, 'JPEG', 10, 10, titleWidth, titleHeight);
        let yPosition = 10 + titleHeight + 5;

        const headerElement = this.$el.querySelector('.pdf-content .el-table__header-wrapper');
        const headerCanvas = await html2canvas(headerElement, { scale: 2, useCORS: true });
        const headerImgData = headerCanvas.toDataURL('image/jpeg', 0.8);
        const headerWidth = 190;
        const headerHeight = headerCanvas.height * headerWidth / headerCanvas.width;

        pdf.addImage(headerImgData, 'JPEG', 10, yPosition, headerWidth, headerHeight);
        yPosition += headerHeight + 2;

        const tableRows = this.$el.querySelectorAll('.pdf-content .el-table__body-wrapper table tr');

        for (let i = 0; i < tableRows.length; i++) {
          const row = tableRows[i];
          const rowCanvas = await html2canvas(row, { scale: 2, useCORS: true });
          const rowImgData = rowCanvas.toDataURL('image/jpeg', 0.8);
          const rowWidth = 190;
          const rowHeight = rowCanvas.height * rowWidth / rowCanvas.width;

          if (yPosition + rowHeight > pageHeight) {
            pdf.setFontSize(10);
            pdf.text(`${currentPageNum}/${totalPageCount}`, pdf.internal.pageSize.getWidth() - 25, pdf.internal.pageSize.getHeight() - 10);

            if (i < tableRows.length - 1) {
              pdf.addPage();
              currentPageNum++;
              yPosition = 10;
            }
          }

          pdf.addImage(rowImgData, 'JPEG', 10, yPosition, rowWidth, rowHeight);
          yPosition += rowHeight + 2;
        }

        pdf.setFontSize(10);
        pdf.text(`${currentPageNum}/${totalPageCount}`, pdf.internal.pageSize.getWidth() - 25, pdf.internal.pageSize.getHeight() - 10);

        const filename = `Linux基线检测报告_${this.selectedIP}_${new Date().toISOString().slice(0, 10)}.pdf`;
        pdf.save(filename);

        this.showContentForPDF = false;
        this.pdfLoading = false;
        this.$message.success('PDF报告导出成功！');

      } catch (err) {
        console.error('生成PDF时出错:', err);
        this.pdfLoading = false;
        this.showContentForPDF = false;
        this.$message.error('PDF生成失败，请重试！');
      }
    },
    filterSearchResults() {
    },
    goToClassifyProtect() {
      this.$router.push('/classifyProtect');
    },
    saveScores() {
      this.saveLoading = true;

      const scoreMeasures = this.checkresults.map(item => ({
        item_id: item.item_id,
        importantLevelJson: item.importantLevel,
        IsComplyLevel: item.score
      }));

      const requestData = {
        ip: this.selectedIP,
        scoreMeasures: scoreMeasures
      };

      axios.post('/api/updateLevel3Protect', requestData)
        .then(response => {
          this.saveLoading = false;
          this.$message.success(`成功更新${response.data.itemsUpdated}项评分结果`);
        })
        .catch(error => {
          this.saveLoading = false;
          console.error('保存评分失败:', error);
          this.$message.error('保存评分失败，请重试');
        });
    },
    getProtectionLevelResult() {
      if (!this.selectedIP) {
        this.$message.warning('请先选择服务器IP');
        return;
      }

      this.resultLoading = true;
      axios.get(`/api/getlevel3ResultByIp?ip=${this.selectedIP}`)
        .then(response => {
          this.levelResult = response.data;
          this.showScoreResult = true;
          this.resultLoading = false;

          const score = this.levelResult.score;
          let message = '';

          if (score >= 90) {
            message = '恭喜！等保评估优秀';
            this.$message.success(message);
          } else if (score >= 80) {
            message = '等保评估良好';
            this.$message.success(message);
          } else if (score >= 60) {
            message = '等保评估合格，但仍有改进空间';
            this.$message.warning(message);
          } else {
            message = '等保评估未达标，建议及时整改';
            this.$message.error(message);
          }
        })
        .catch(error => {
          console.error('获取等保结果失败:', error);
          this.resultLoading = false;
          this.$message.error('获取等保结果失败，请重试');
        });
    },
    getScoreConclusion(score) {
      if (!score && score !== 0) return '未评估';

      if (score >= 90) {
        return '优秀';
      } else if (score >= 80) {
        return '良好';
      } else if (score >= 60) {
        return '合格';
      } else {
        return '未达标';
      }
    },
    getScoreClass(score) {
      if (!score && score !== 0) return '';

      if (score >= 90) {
        return 'score-excellent';
      } else if (score >= 80) {
        return 'score-good';
      } else if (score >= 60) {
        return 'score-moderate';
      } else {
        return 'score-poor';
      }
    }
  },
  mounted() {
    this.fetchAliveHosts();
  }
}
</script>

<style scoped>
.baseline-container {
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

.control-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 15px;
}

.button-group {
  display: flex;
  gap: 10px;
}

.control-item {
  margin-right: 10px;
}

.filter-group {
  display: flex;
  gap: 10px;
}

.filter-group .el-input {
  width: 250px;
}

.server-info-card {
  margin-bottom: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.card-header {
  font-size: 16px;
  font-weight: bold;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.summary {
  display: flex;
  gap: 10px;
}

.info-item {
  padding: 8px 0;
  border-bottom: 1px solid #ebeef5;
}

.info-label {
  font-weight: bold;
  color: #606266;
}

.results-card {
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

/* PDF内容样式 */
.pdf-content {
  font-size: 10pt;
  max-width: 297mm;
  padding: 15mm;
  box-sizing: border-box;
}

#linuxBaseline2 {
  font-size: 24pt;
  color: #141010e1;
  text-align: center;
  margin-top: 20px;
}

.server1 .el-col p {
  font-size: 16px;
  white-space: pre-wrap;
  line-height: 1.6;
  margin-bottom: 5px;
}

.failed-result {
  color: #f56c6c;
}

.page-number {
  position: absolute;
  bottom: 10mm;
  right: 10mm;
  font-size: 12px;
}

.report-content-title {
  margin-top: 20px;
  margin-bottom: 15px;
  text-align: center;
}

.report-content-title h2 {
  font-size: 18pt;
  color: #303133;
  margin: 0;
}

@media (max-width: 768px) {
  .control-section {
    flex-direction: column;
    align-items: flex-start;
  }

  .filter-group {
    width: 100%;
  }

  .filter-group .el-input {
    width: 100%;
  }
}

/* 计算评分显示评分部分样式 */
/* 新增样式 */
.score-card {
  margin-top: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.score-content {
  display: flex;
  align-items: center;
  padding: 15px;
}

/* 替换原来的仪表盘样式为数字得分样式 */
.score-display {
  width: 150px;
  text-align: center;
  margin-right: 30px;
  flex-shrink: 0;
  border-right: 1px solid #ebeef5;
  padding-right: 20px;
}

.score-title {
  font-size: 16px;
  color: #606266;
  margin-bottom: 10px;
}

.score-number {
  font-size: 36px;
  font-weight: bold;
  line-height: 1.2;
}

.score-details {
  flex-grow: 1;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 15px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  background-color: #f5f7fa;
  padding: 12px;
  border-radius: 4px;
}

.detail-label {
  font-size: 14px;
  color: #606266;
  margin-bottom: 5px;
}

.detail-value {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
}

.score-summary {
  padding: 0 15px 15px;
}

.summary-text {
  border-top: 1px solid #ebeef5;
  padding-top: 15px;
  color: #606266;
}

/* 不同得分等级的颜色样式 */
.score-excellent,
.excellent-text {
  color: #67c23a;
}

.score-good,
.good-text {
  color: #409eff;
}

.score-moderate,
.warning-text {
  color: #e6a23c;
}

.score-poor,
.danger-text {
  color: #f56c6c;
}

.excellent-text,
.good-text,
.warning-text,
.danger-text {
  font-weight: bold;
}
</style>
