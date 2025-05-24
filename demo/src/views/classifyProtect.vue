<template>
  <div class="baseline-container">
    <!-- 头部区域 -->
    <div class="header-section">
      <h1 class="main-title">等级保护测评</h1>
      <div class="date-info">
        <el-tag type="info">检测时间：{{ new Date().toLocaleString() }}</el-tag>
      </div>
    </div>

    <!-- 控制按钮区域 -->
    <div class="control-section">
      <div class="button-group">
        <!-- 新增的IP选择下拉框 -->
        <div class="control-item">
          <el-select
              v-model="selectedIP"
              placeholder="选择服务器IP"
              @change="changeServer"
              size="medium">
            <el-option
                v-for="ip in aliveHosts"
                :key="ip"
                :label="ip"
                :value="ip">
            </el-option>
          </el-select>
        </div>

        <el-button
            @click="onExportToPDF"
            :loading="pdfLoading"
            icon="el-icon-document"
            type="primary">
          导出为 PDF
        </el-button>
      </div>

      <div class="filter-group">
        <el-select
            v-model="selectedStatus"
            placeholder="请选择状态"
            size="medium">
          <el-option label="全部" value="all"></el-option>
          <el-option label="通过" value="passed"></el-option>
          <el-option label="未通过" value="failed"></el-option>
        </el-select>

        <el-input
            placeholder="输入检测项关键字..."
            v-model="searchTerm"
            @input="filterSearchResults"
            prefix-icon="el-icon-search"
            size="medium">
        </el-input>
      </div>
    </div>



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

      <el-table
          :data="filteredCheckresults"
          style="width: 100%"
          border
          stripe
          :header-cell-style="{background:'#f5f7fa',color:'#606266'}"
          v-loading="tableLoading">
        <el-table-column label="序号" width="70" type="index"></el-table-column>
        <el-table-column prop="description" label="检测项" min-width="150"></el-table-column>
        <el-table-column prop="basis" label="基准" min-width="150"></el-table-column>
        <el-table-column prop="result" label="检测结果" min-width="150"></el-table-column>
        <!--        <el-table-column label="基准/检测结果" min-width="200">-->
        <!--          <template slot-scope="scope">-->
        <!--            {{ scope.row.basis }}/{{ scope.row.result }}-->
        <!--          </template>-->
        <!--        </el-table-column>-->
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
          <el-col :span="24"><p>主机名：{{ serverInfo.hostname }}</p></el-col>
          <el-col :span="24"><p>主机架构：{{ serverInfo.arch }}</p></el-col>
          <el-col :span="24"><p>主机CPU信息：{{ serverInfo.cpu }}</p></el-col>
          <el-col :span="24"><p>主机物理CPU个数：{{ serverInfo.cpuPhysical }}</p></el-col>
          <el-col :span="24"><p>主机物理CPU核心数：{{ serverInfo.cpuCore }}</p></el-col>
          <el-col :span="12"><p>主机空闲内存：{{ serverInfo.free }}</p></el-col>
          <el-col :span="24"><p>硬件型号：{{ serverInfo.ProductName }}</p></el-col>
          <el-col :span="24"><p>主机版本信息：{{ serverInfo.version }}</p></el-col>
          <el-col :span="24"><p>服务器IP：{{ selectedIP }}</p></el-col>
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
        <el-table-column prop="basis" label="检测依据" min-width="150"></el-table-column>
        <el-table-column prop="result" label="检测结果" min-width="150"></el-table-column>
        <!--        <el-table-column label="基准/检测结果" min-width="200">-->
        <!--          <template slot-scope="scope">-->
        <!--            {{ scope.row.basis }}/{{ scope.row.result }}-->
        <!--          </template>-->
        <!--        </el-table-column>-->
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
      </el-table>
      <!-- 页码容器 - PDF生成时会添加 -->
      <div class="page-numbers-container"></div>
    </div>

  </div>
</template>

<script>
import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';
import axios from 'axios'; // 引入axios

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
      totalPages: 2, // 默认至少两页
      aliveHosts: [], // 活跃主机IP列表
      selectedIP: '' // 选中的IP
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
    }
  },
  methods: {
    // 获取活跃IP列表
    fetchAliveHosts() {
      axios.get('/api/getAliveHosts')
          .then(response => {
            this.aliveHosts = response.data.alive_hosts;
            // 如果有IP，默认选择第一个
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

    // 切换服务器
    changeServer() {
      if (this.selectedIP) {
        this.fetchAndDisplayChenckResults();
      }
    },

    // 修改后的获取检测结果函数
    fetchAndDisplayChenckResults() {
      if (!this.selectedIP) {
        this.$message.warning('请先选择服务器IP');
        return;
      }

      this.tableLoading = true;
      axios.get(`/api/level3Userinfo?ip=${this.selectedIP}`)
          .then(response => {
            // this.checkresults = response.data.Event_result;
            this.checkresults = response.data.checkResults;
            // this.serverInfo = response.data.serverInfo;
            this.tableLoading = false;
            // 根据数据量预估页数
            this.estimatePageCount();
          })
          .catch(error => {
            console.error('Error:', error);
            this.tableLoading = false;
            this.$message.error('获取检测结果失败，请重试');
          });
    },

    estimatePageCount() {
      // 粗略估算页数：第一页为封面，剩余按每页约10条记录计算
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

      // 延迟执行，确保DOM已完全渲染
      setTimeout(() => {
        // 创建PDF对象
        const pdf = new jsPDF({
          orientation: 'p',
          unit: 'mm',
          format: 'a4'
        });

        // 关键点：采用两遍渲染策略
        // 第一遍：只渲染，不保存，仅记录最终页码
        // 第二遍：用记录的正确页码重新渲染并保存

        // 第一阶段：模拟渲染，计算总页数
        this.simulatePdfRendering(pdf).then(actualPageCount => {
          // 保存实际总页数
          this.totalPages = actualPageCount;
          console.log('确定的总页数:', this.totalPages);

          // 第二阶段：使用确定的总页数重新生成PDF
          this.renderFinalPdf(pdf, this.totalPages);
        }).catch(err => {
          console.error('PDF生成过程出错:', err);
          this.pdfLoading = false;
          this.showContentForPDF = false;
          this.$message.error('PDF生成失败，请重试！');
        });
      }, 1000);
    },

    // 模拟渲染，确定实际总页数
    async simulatePdfRendering(pdf) {
      try {
        // 保存PDF状态
        const originalPage = pdf.internal.getCurrentPageInfo().pageNumber;

        let pageCount = 0;

        // 模拟渲染封面页
        const coverPage = this.$el.querySelector('.pdf-content .server1');
        await html2canvas(coverPage, { scale: 2, useCORS: true });
        pageCount = 1;  // 封面算第一页

        // 模拟渲染内容页
        pdf.addPage();
        pageCount++;

        // 页面参数
        const pageHeight = pdf.internal.pageSize.getHeight() - 20;

        // 模拟渲染标题
        const titleElement = this.$el.querySelector('.pdf-content .report-content-title');
        const titleCanvas = await html2canvas(titleElement, { scale: 2, useCORS: true });
        const titleWidth = 190;
        const titleHeight = titleCanvas.height * titleWidth / titleCanvas.width;

        let yPosition = 10 + titleHeight + 5;

        // 模拟渲染表头
        const headerElement = this.$el.querySelector('.pdf-content .el-table__header-wrapper');
        const headerCanvas = await html2canvas(headerElement, { scale: 2, useCORS: true });
        const headerWidth = 190;
        const headerHeight = headerCanvas.height * headerWidth / headerCanvas.width;

        yPosition += headerHeight + 2;

        // 模拟渲染每一行并计算页码
        const tableRows = this.$el.querySelectorAll('.pdf-content .el-table__body-wrapper table tr');

        for (let i = 0; i < tableRows.length; i++) {
          const row = tableRows[i];
          const rowCanvas = await html2canvas(row, { scale: 2, useCORS: true });
          const rowWidth = 190;
          const rowHeight = rowCanvas.height * rowWidth / rowCanvas.width;

          // 如果当前行放不下，需要新页面
          if (yPosition + rowHeight > pageHeight) {
            // 新页面
            if (i < tableRows.length - 1) { // 不是最后一行才需要新页面
              pdf.addPage();
              pageCount++;
              yPosition = 10; // 重置Y位置
            }
          }

          yPosition += rowHeight + 2;
        }

        // 恢复PDF状态
        while (pdf.internal.getCurrentPageInfo().pageNumber > originalPage) {
          pdf.deletePage(pdf.internal.getCurrentPageInfo().pageNumber);
        }

        return pageCount;
      } catch (error) {
        console.error('模拟渲染计算页数出错:', error);
        throw error;
      }
    },

    // 使用正确页码渲染最终PDF
    async renderFinalPdf(pdf, totalPageCount) {
      try {
        // 渲染封面页
        const coverPage = this.$el.querySelector('.pdf-content .server1');
        const coverCanvas = await html2canvas(coverPage, { scale: 2, useCORS: true });
        const imgData = coverCanvas.toDataURL('image/jpeg', 0.8);
        const imgWidth = 190;
        const imgHeight = coverCanvas.height * imgWidth / coverCanvas.width;

        pdf.addImage(imgData, 'JPEG', 10, 10, imgWidth, imgHeight);

        // 封面页页码
        pdf.setFontSize(10);
        pdf.text(`1/${totalPageCount}`, pdf.internal.pageSize.getWidth() - 25, pdf.internal.pageSize.getHeight() - 10);

        // 添加内容页
        pdf.addPage();

        // 页面参数
        const pageHeight = pdf.internal.pageSize.getHeight() - 20;
        let currentPageNum = 2; // 从第二页开始

        // 添加标题
        const titleElement = this.$el.querySelector('.pdf-content .report-content-title');
        const titleCanvas = await html2canvas(titleElement, { scale: 2, useCORS: true });
        const titleImgData = titleCanvas.toDataURL('image/jpeg', 0.8);
        const titleWidth = 190;
        const titleHeight = titleCanvas.height * titleWidth / titleCanvas.width;

        pdf.addImage(titleImgData, 'JPEG', 10, 10, titleWidth, titleHeight);
        let yPosition = 10 + titleHeight + 5;

        // 添加表头
        const headerElement = this.$el.querySelector('.pdf-content .el-table__header-wrapper');
        const headerCanvas = await html2canvas(headerElement, { scale: 2, useCORS: true });
        const headerImgData = headerCanvas.toDataURL('image/jpeg', 0.8);
        const headerWidth = 190;
        const headerHeight = headerCanvas.height * headerWidth / headerCanvas.width;

        pdf.addImage(headerImgData, 'JPEG', 10, yPosition, headerWidth, headerHeight);
        yPosition += headerHeight + 2;

        // 逐行添加表格内容
        const tableRows = this.$el.querySelectorAll('.pdf-content .el-table__body-wrapper table tr');

        for (let i = 0; i < tableRows.length; i++) {
          const row = tableRows[i];
          const rowCanvas = await html2canvas(row, { scale: 2, useCORS: true });
          const rowImgData = rowCanvas.toDataURL('image/jpeg', 0.8);
          const rowWidth = 190;
          const rowHeight = rowCanvas.height * rowWidth / rowCanvas.width;

          // 检查是否需要换页
          if (yPosition + rowHeight > pageHeight) {
            // 添加当前页码
            pdf.setFontSize(10);
            pdf.text(`${currentPageNum}/${totalPageCount}`, pdf.internal.pageSize.getWidth() - 25, pdf.internal.pageSize.getHeight() - 10);

            // 不是最后一行才需要新页面
            if (i < tableRows.length - 1) {
              // 新页面
              pdf.addPage();
              currentPageNum++;
              yPosition = 10;
            }
          }

          // 添加当前行
          pdf.addImage(rowImgData, 'JPEG', 10, yPosition, rowWidth, rowHeight);
          yPosition += rowHeight + 2;
        }

        // 最后一页页码
        pdf.setFontSize(10);
        pdf.text(`${currentPageNum}/${totalPageCount}`, pdf.internal.pageSize.getWidth() - 25, pdf.internal.pageSize.getHeight() - 10);

        // 保存PDF
        const filename = `Linux基线检测报告_${this.selectedIP}_${new Date().toISOString().slice(0,10)}.pdf`;
        pdf.save(filename);

        // 清理和完成
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
      // 通过计算属性自动过滤，此方法保留用于可能的扩展
    },

    goToClassifyProtect() {
      // 导航到等保测评页面
      this.$router.push('/classifyProtect');
    }
  },
  mounted() {
    // 先获取活跃IP列表，然后会自动选择第一个IP并获取检测结果
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
</style>






<!--<template>-->
<!--  <div class="security-assessment-container">-->
<!--    &lt;!&ndash; 头部区域 &ndash;&gt;-->
<!--    <div class="header-section">-->
<!--      <h1 class="main-title">等级保护测评系统</h1>-->
<!--      <div class="system-info">-->
<!--        <el-tag type="info">{{ new Date().toLocaleString() }}</el-tag>-->
<!--      </div>-->
<!--    </div>-->

<!--    &lt;!&ndash; 控制面板区域 &ndash;&gt;-->
<!--    <div class="control-panel">-->
<!--      <el-card class="control-card">-->
<!--        <div class="control-row">-->
<!--          &lt;!&ndash; IP选择 &ndash;&gt;-->
<!--          <div class="control-item">-->
<!--            <el-select-->
<!--                v-model="selectedIP"-->
<!--                placeholder="选择服务器IP"-->
<!--                @change="changeServer"-->
<!--                size="medium">-->
<!--              <el-option-->
<!--                  v-for="ip in serverIPs"-->
<!--                  :key="ip"-->
<!--                  :label="ip"-->
<!--                  :value="ip">-->
<!--              </el-option>-->
<!--            </el-select>-->
<!--          </div>-->

<!--          &lt;!&ndash; 等级保护级别选择 &ndash;&gt;-->
<!--          <div class="control-item">-->
<!--            <el-select-->
<!--                v-model="protectionLevel"-->
<!--                placeholder="选择等保级别"-->
<!--                @change="changeProtectionLevel"-->
<!--                size="medium">-->
<!--              <el-option label="二级等保" value="2" disabled></el-option>-->
<!--              <el-option label="三级等保" value="3"></el-option>-->
<!--            </el-select>-->
<!--          </div>-->

<!--          &lt;!&ndash; 状态筛选 &ndash;&gt;-->
<!--          <div class="control-item">-->
<!--            <el-select-->
<!--                v-model="selectedStatus"-->
<!--                placeholder="请选择状态"-->
<!--                size="medium">-->
<!--              <el-option label="全部" value="all"></el-option>-->
<!--              <el-option label="通过" value="passed"></el-option>-->
<!--              <el-option label="未通过" value="failed"></el-option>-->
<!--            </el-select>-->
<!--          </div>-->

<!--          &lt;!&ndash; 搜索框 &ndash;&gt;-->
<!--          <div class="control-item search-box">-->
<!--            <el-input-->
<!--                placeholder="输入检测项关键字..."-->
<!--                v-model="searchTerm"-->
<!--                @input="filterSearchResults"-->
<!--                prefix-icon="el-icon-search"-->
<!--                size="medium">-->
<!--            </el-input>-->
<!--          </div>-->
<!--        </div>-->

<!--        <div class="action-row">-->
<!--          <el-button-->
<!--              @click="computeResult"-->
<!--              type="primary"-->
<!--              icon="el-icon-data-analysis"-->
<!--              size="medium">-->
<!--            计算评分-->
<!--          </el-button>-->
<!--&lt;!&ndash;          <el-button&ndash;&gt;-->
<!--&lt;!&ndash;              @click="onExportToPDF"&ndash;&gt;-->
<!--&lt;!&ndash;              :loading="pdfLoading"&ndash;&gt;-->
<!--&lt;!&ndash;              type="success"&ndash;&gt;-->
<!--&lt;!&ndash;              icon="el-icon-document"&ndash;&gt;-->
<!--&lt;!&ndash;              size="medium">&ndash;&gt;-->
<!--&lt;!&ndash;            导出PDF报告&ndash;&gt;-->
<!--&lt;!&ndash;          </el-button>&ndash;&gt;-->

<!--          &lt;!&ndash; 显示结果 &ndash;&gt;-->
<!--          <div class="result-display">-->
<!--            <div class="score-card">-->
<!--              <div class="score-label">得分：</div>-->
<!--              <div class="score-value">{{ resultScore !== '' ? Number(resultScore).toFixed(1) : '&#45;&#45;' }}</div>-->
<!--            </div>-->
<!--            <div class="conclusion-card">-->
<!--              <div class="conclusion-label">结论：</div>-->
<!--              <div class="conclusion-value">-->
<!--                <template v-if="resultScore !== ''">-->
<!--                  <span v-if="resultScore >= 90">优</span>-->
<!--                  <span v-else-if="resultScore >= 80 && resultScore < 90">良</span>-->
<!--                  <span v-else-if="resultScore >= 70 && resultScore < 80">中</span>-->
<!--                  <span v-else>差</span>-->
<!--                </template>-->
<!--                <template v-else>&#45;&#45;</template>-->
<!--              </div>-->
<!--            </div>-->
<!--          </div>-->
<!--        </div>-->
<!--      </el-card>-->
<!--    </div>-->

<!--    &lt;!&ndash; 服务器信息卡片 &ndash;&gt;-->
<!--    <div class="server-info-section" v-if="Object.keys(serverInfo).length > 0">-->
<!--      <el-card class="server-info-card">-->
<!--        <div slot="header" class="card-header">-->
<!--          <span><i class="el-icon-monitor"></i> 服务器信息</span>-->
<!--          <el-button-->
<!--              style="float: right; padding: 3px 0"-->
<!--              type="text"-->
<!--              @click="toggleServerInfo">-->
<!--            {{ showServerInfo ? '隐藏' : '显示' }}-->
<!--          </el-button>-->
<!--        </div>-->
<!--        <div v-if="showServerInfo" class="server-info-grid">-->
<!--          <div class="info-item">-->
<!--            <span class="info-label">主机名：</span>-->
<!--            <span class="info-value">{{ serverInfo.hostname || '未知' }}</span>-->
<!--          </div>-->
<!--          <div class="info-item">-->
<!--            <span class="info-label">架构：</span>-->
<!--            <span class="info-value">{{ serverInfo.arch || '未知' }}</span>-->
<!--          </div>-->
<!--          <div class="info-item">-->
<!--            <span class="info-label">CPU信息：</span>-->
<!--            <span class="info-value">{{ serverInfo.cpu || '未知' }}</span>-->
<!--          </div>-->
<!--          <div class="info-item">-->
<!--            <span class="info-label">物理CPU个数：</span>-->
<!--            <span class="info-value">{{ serverInfo.cpuPhysical || '未知' }}</span>-->
<!--          </div>-->
<!--          <div class="info-item">-->
<!--            <span class="info-label">CPU核心数：</span>-->
<!--            <span class="info-value">{{ serverInfo.cpuCore || '未知' }}</span>-->
<!--          </div>-->
<!--          <div class="info-item">-->
<!--            <span class="info-label">空闲内存：</span>-->
<!--            <span class="info-value">{{ serverInfo.free || '未知' }}</span>-->
<!--          </div>-->
<!--          <div class="info-item">-->
<!--            <span class="info-label">硬件型号：</span>-->
<!--            <span class="info-value">{{ serverInfo.ProductName || '未知' }}</span>-->
<!--          </div>-->
<!--          <div class="info-item">-->
<!--            <span class="info-label">版本信息：</span>-->
<!--            <span class="info-value">{{ serverInfo.version || '未知' }}</span>-->
<!--          </div>-->
<!--&lt;!&ndash;          <div class="info-item">&ndash;&gt;-->
<!--&lt;!&ndash;            <span class="info-label">联网状态：</span>&ndash;&gt;-->
<!--&lt;!&ndash;            <span class="info-value">{{ serverInfo.isInternet || '未知' }}</span>&ndash;&gt;-->
<!--&lt;!&ndash;          </div>&ndash;&gt;-->
<!--        </div>-->
<!--      </el-card>-->
<!--    </div>-->

<!--    &lt;!&ndash; 表格区域 &ndash;&gt;-->
<!--    <div class="table-section">-->
<!--      <el-card class="table-card">-->
<!--        <el-table-->
<!--            :data="filteredCheckresults"-->
<!--            style="width: 100%"-->
<!--            border-->
<!--            stripe-->
<!--            :header-cell-style="{background:'#f5f7fa',color:'#606266'}"-->
<!--            v-loading="loading">-->
<!--          <el-table-column prop="description" label="检测项" min-width="180"></el-table-column>-->
<!--          <el-table-column prop="basis" label="检测依据" min-width="180"></el-table-column>-->
<!--          <el-table-column prop="importantLevel" label="重要程度" width="100">-->
<!--            <template slot-scope="scope">-->
<!--              <el-tag :type="getImportanceLevelType(scope.row.importantLevel)">-->
<!--                {{ scope.row.importantLevel }}-->
<!--              </el-tag>-->
<!--            </template>-->
<!--          </el-table-column>-->
<!--          <el-table-column prop="result" label="检测结果" min-width="150"></el-table-column>-->
<!--          <el-table-column prop="IsComply" label="是否符合基线" width="120">-->
<!--            <template slot-scope="scope">-->
<!--              <el-tag :type="scope.row.IsComply === 'true' ? 'success' : 'danger'">-->
<!--                {{ scope.row.IsComply === 'true' ? '符合' : '不符合' }}-->
<!--              </el-tag>-->
<!--            </template>-->
<!--          </el-table-column>-->
<!--          <el-table-column prop="recommend" label="修改建议" min-width="250"></el-table-column>-->
<!--          <el-table-column label="结果评分" width="120">-->
<!--            <template slot-scope="scope">-->
<!--              <el-select-->
<!--                  v-model="scope.row.score"-->
<!--                  placeholder="请选择评分"-->
<!--                  size="mini">-->
<!--                <el-option label="符合" value="1"></el-option>-->
<!--                <el-option label="部分符合" value="0.5"></el-option>-->
<!--                <el-option label="不符合" value="0"></el-option>-->
<!--              </el-select>-->
<!--            </template>-->
<!--          </el-table-column>-->
<!--        </el-table>-->
<!--      </el-card>-->
<!--    </div>-->

<!--    &lt;!&ndash; PDF输出内容 (隐藏) &ndash;&gt;-->
<!--    <div class="pdf-content" v-show="showContentForPDF">-->
<!--      <div class="server1">-->
<!--        <h1 id="linuxBaseline2" style="font-size: 24pt; text-align: center;">Linux等级保护测评报告</h1>-->

<!--        &lt;!&ndash; 报告头部信息 &ndash;&gt;-->
<!--        <div style="text-align:right; margin-top:20px;">-->
<!--          <p style="font-size:18px;">检测时间：{{ new Date().toLocaleString() }}</p>-->
<!--          <p style="font-size:18px;">等保级别：{{ protectionLevel === '2' ? '二级等保' : '三级等保' }}</p>-->
<!--          <p style="font-size:18px;">服务器IP：{{ selectedIP || '未选择' }}</p>-->
<!--        </div>-->

<!--        &lt;!&ndash; 空白分隔 &ndash;&gt;-->
<!--        <div style="height:50px;"></div>-->

<!--        &lt;!&ndash; 评分结果 &ndash;&gt;-->
<!--        <div class="result-container2" style="font-size: 18pt;">-->
<!--          <div style="font-size: 20pt;margin-right: 200px;">测评得分：{{ resultScore !== '' ? Number(resultScore).toFixed(1) : '&#45;&#45;' }}</div>-->

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

<!--          &lt;!&ndash; 空行 &ndash;&gt;-->
<!--          <div style="height:30px;"></div>-->

<!--          &lt;!&ndash; 服务器信息 &ndash;&gt;-->
<!--          <el-row :gutter="20">-->
<!--            <el-col :span="24"><p style="font-size: 15pt;">主机名：{{ serverInfo.hostname || '未知' }}</p></el-col>-->
<!--            <el-col :span="24"><p style="font-size: 15pt;">主机架构：{{ serverInfo.arch || '未知' }}</p></el-col>-->
<!--            <el-col :span="24"><p style="font-size: 15pt;">主机CPU信息：{{ serverInfo.cpu || '未知' }}</p></el-col>-->
<!--            <el-col :span="24"><p style="font-size: 15pt;">主机物理CPU个数：{{ serverInfo.cpuPhysical || '未知' }}</p></el-col>-->
<!--            <el-col :span="24"><p style="font-size: 15pt;">主机物理CPU核心数：{{ serverInfo.cpuCore || '未知' }}</p></el-col>-->
<!--            <el-col :span="12"><p style="font-size: 15pt;">主机空闲内存：{{ serverInfo.free || '未知' }}</p></el-col>-->
<!--            <el-col :span="24"><p style="font-size: 15pt;">硬件型号：{{ serverInfo.ProductName || '未知' }}</p></el-col>-->
<!--            <el-col :span="24"><p style="font-size: 15pt;">主机版本信息：{{ serverInfo.version || '未知' }}</p></el-col>-->
<!--            <el-col :span="24"><p style="font-size: 15pt;">联网检测：{{ serverInfo.isInternet || '未知' }}</p></el-col>-->
<!--          </el-row>-->
<!--        </div>-->

<!--        &lt;!&ndash; 空白分隔 &ndash;&gt;-->
<!--        <div style="height:200px;"></div>-->

<!--        &lt;!&ndash; 检测人员签名 &ndash;&gt;-->
<!--        <div style="text-align:right; margin-top:20px;">-->
<!--          <span style="font-size:20px;">检测人员签名：</span>-->
<!--          <img src="../assets/szj.jpg" alt="Signature 1" style="max-width:150px;">-->
<!--          <img src="../assets/hjj.jpg" alt="Signature 2" style="max-width:150px;">-->
<!--          <img src="../assets/dyy.jpg" alt="Signature 3" style="max-width:150px;">-->
<!--        </div>-->
<!--      </div>-->

<!--      &lt;!&ndash; PDF 表格部分 &ndash;&gt;-->
<!--      <el-table :data="filteredCheckresults" style="width: 100%" border>-->
<!--        <el-table-column prop="description" label="检测项"></el-table-column>-->
<!--        <el-table-column prop="basis" label="检测依据"></el-table-column>-->
<!--        <el-table-column prop="importantLevel" label="重要程度" width="100"></el-table-column>-->
<!--        <el-table-column prop="result" label="检测结果"></el-table-column>-->
<!--        <el-table-column prop="IsComply" label="是否符合基线" width="120">-->
<!--          <template slot-scope="scope">-->
<!--            <span :class="{ 'failed-result': scope.row.IsComply === 'false' }">-->
<!--              {{ scope.row.IsComply === 'true' ? '符合' : '不符合' }}-->
<!--            </span>-->
<!--          </template>-->
<!--        </el-table-column>-->
<!--        <el-table-column prop="recommend" label="修改建议" width="400"></el-table-column>-->
<!--        <el-table-column label="结果评分" width="120">-->
<!--          <template slot-scope="scope">-->
<!--            <span>{{ getScoreText(scope.row.score) }}</span>-->
<!--          </template>-->
<!--        </el-table-column>-->
<!--      </el-table>-->
<!--    </div>-->
<!--  </div>-->
<!--</template>-->

<!--<script>-->
<!--import jsPDF from 'jspdf';-->
<!--import html2canvas from 'html2canvas';-->
<!--// import {Message} from "element-ui";-->
<!--import axios from "axios";-->

<!--export default {-->
<!--  name: "baseCheck",-->
<!--  data() {-->
<!--    return {-->
<!--      checkresults: [],-->
<!--      serverInfo: {},-->
<!--      serverIPs: [], // 示例IP列表-->
<!--      selectedIP: '',-->
<!--      protectionLevel: '3', // 默认三级等保-->
<!--      selectedStatus: 'all',-->
<!--      searchTerm: '',-->
<!--      resultScore: localStorage.getItem('resultScore') || '',-->
<!--      showContentForPDF: false,-->
<!--      loading: false,-->
<!--      showServerInfo: true,-->
<!--      pdfLoading:false,-->
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
<!--        const numericScore = parseFloat(score);-->
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
<!--    // fetchAliveHosts() {-->
<!--    //   fetch('/api/getAliveHosts')-->
<!--    //       .then(response => {-->
<!--    //         if (!response.ok) {-->
<!--    //           throw new Error(`HTTP status ${response.status}`);-->
<!--    //         }-->
<!--    //         return response.json();-->
<!--    //       })-->
<!--    //       .then(data => {-->
<!--    //         this.serverIPs = data.alive_hosts;-->
<!--    //         if (this.serverIPs && this.serverIPs.length > 0) {-->
<!--    //           this.selectedIP = this.serverIPs[0];-->
<!--    //           this.fetchAndDisplayChenckResults();-->
<!--    //         }-->
<!--    //         // this.selectedIP=data.alive_hosts[0];-->
<!--    //       })-->
<!--    //       .catch(error => {-->
<!--    //         Message.error('获取活跃IP列表失败：' + error.message);-->
<!--    //       });-->
<!--    // },-->
<!--    fetchAliveHosts() {-->
<!--      axios.get('/api/getAliveHosts')-->
<!--          .then(response => {-->
<!--            this.serverIPs = response.data.alive_hosts;-->
<!--            // 如果有IP，默认选择第一个-->
<!--            if (this.serverIPs && this.serverIPs.length > 0) {-->
<!--              this.selectedIP = this.serverIPs[0];-->
<!--              this.fetchAndDisplayCheckResults();-->
<!--            }-->
<!--          })-->
<!--          .catch(error => {-->
<!--            console.error('获取活跃IP列表失败:', error);-->
<!--            this.$message.error('获取活跃IP列表失败');-->
<!--          });-->
<!--    },-->
<!--    // 切换服务器信息显示-->
<!--    toggleServerInfo() {-->
<!--      this.showServerInfo = !this.showServerInfo;-->
<!--    },-->

<!--    // 根据重要程度返回对应的标签类型-->
<!--    getImportanceLevelType(level) {-->
<!--      switch(level) {-->
<!--        case '高':-->
<!--          return 'danger';-->
<!--        case '中':-->
<!--          return 'warning';-->
<!--        case '低':-->
<!--          return 'info';-->
<!--        default:-->
<!--          return '';-->
<!--      }-->
<!--    },-->

<!--    // 更改服务器-->
<!--    changeServer() {-->
<!--      this.loading = true;-->
<!--      // 这里模拟向后端发送请求获取指定IP的服务器数据-->
<!--      setTimeout(() => {-->
<!--        this.fetchAndDisplayCheckResults();-->
<!--        this.loading = false;-->
<!--      }, 1000);-->
<!--    },-->

<!--    // 更改等保级别-->
<!--    changeProtectionLevel() {-->
<!--      this.loading = true;-->
<!--      // 这里模拟向后端发送请求获取指定等保级别的检测项-->
<!--      setTimeout(() => {-->
<!--        this.fetchAndDisplayCheckResults();-->
<!--        this.loading = false;-->
<!--      }, 1000);-->
<!--    },-->

<!--    // 获取检测结果-->
<!--    fetchAndDisplayCheckResults() {-->
<!--      this.loading = true;-->

<!--      // 构建请求参数，包含选择的IP和等保级别-->
<!--      const params = new URLSearchParams();-->
<!--      if (this.selectedIP) {-->
<!--        params.append('ip', this.selectedIP);-->
<!--      }-->
<!--      //params.append('level', this.protectionLevel);-->

<!--      // 发送请求-->
<!--      fetch(`/api/userinfo?${params.toString()}`)-->
<!--          .then(response => response.json())-->
<!--          .then(data => {-->
<!--            this.checkresults = data.checkResults.map(item => ({-->
<!--              ...item,-->
<!--              score: item.IsComply === 'true' ? '1' : '0.5'-->
<!--            }));-->
<!--            this.serverInfo = data.serverInfo;-->
<!--            this.loading = false;-->
<!--          })-->
<!--          .catch(error => {-->
<!--            console.error('Error:', error);-->
<!--            this.loading = false;-->
<!--            this.$message.error('获取检测结果失败，请重试！');-->
<!--          });-->
<!--    },-->

<!--    // 计算结果-->
<!--    computeResult() {-->
<!--      this.loading = true;-->

<!--      const scoreMeasures = this.checkresults.map(item => ({-->
<!--        importantLevelJson: item.importantLevel,-->
<!--        IsComplyLevel: item.score.toString(),-->
<!--      }));-->

<!--      // 添加等保级别参数-->
<!--      const requestData = {-->
<!--        scoreMeasures,-->
<!--        protectionLevel: this.protectionLevel,-->
<!--        serverIP: this.selectedIP-->
<!--      };-->

<!--      fetch('/api/classifyProtect', {-->
<!--        method: 'POST',-->
<!--        headers: {-->
<!--          'Content-Type': 'application/json'-->
<!--        },-->
<!--        body: JSON.stringify(requestData)-->
<!--      })-->
<!--          .then(response => response.json())-->
<!--          .then(data => {-->
<!--            console.log("Received score from backend:", data.score);-->
<!--            this.resultScore = data.score;-->
<!--            localStorage.setItem('resultScore', this.resultScore);-->
<!--            this.loading = false;-->
<!--            this.$message.success('评分计算完成！');-->
<!--          })-->
<!--          .catch(error => {-->
<!--            console.error('Error:', error);-->
<!--            this.loading = false;-->
<!--            this.$message.error('评分计算失败，请重试！');-->
<!--          });-->
<!--    },-->

<!--    // 导出PDF-->
<!--    // 导出PDF-->
<!--    onExportToPDF() {-->
<!--      this.pdfLoading = true; // 开始时设置loading为true-->
<!--      this.showContentForPDF = true;-->

<!--      this.$message({-->
<!--        message: '正在生成PDF，请稍候...',-->
<!--        type: 'info',-->
<!--        duration: 2000-->
<!--      });-->

<!--      setTimeout(() => {-->
<!--        const pdf = new jsPDF({-->
<!--          orientation: 'p',-->
<!--          unit: 'mm',-->
<!--          format: 'a4'-->
<!--        });-->

<!--        // 渲染PDF的服务器信息页-->
<!--        const contentForPDF = this.$el.querySelector('.pdf-content .server1');-->
<!--        html2canvas(contentForPDF, {-->
<!--          scale: 2,-->
<!--          useCORS: true-->
<!--        }).then(canvas => {-->
<!--          const imgData = canvas.toDataURL('image/jpeg', 0.8);-->
<!--          const imgWidth = 190;-->
<!--          let imgHeight = canvas.height * imgWidth / canvas.width;-->

<!--          pdf.addImage(imgData, 'JPEG', 10, 10, imgWidth, imgHeight);-->
<!--          pdf.addPage();-->

<!--          // 渲染表头-->
<!--          const header = this.$el.querySelector('.pdf-content .el-table__header-wrapper');-->
<!--          if (header) {-->
<!--            html2canvas(header, {-->
<!--              scale: 2,-->
<!--              useCORS: true-->
<!--            }).then(canvas => {-->
<!--              const imgData = canvas.toDataURL('image/jpeg', 0.8);-->
<!--              const imgWidth = 190;-->
<!--              let imgHeight = canvas.height * imgWidth / canvas.width;-->

<!--              pdf.addImage(imgData, 'JPEG', 10, 10, imgWidth, imgHeight);-->
<!--              processRows(10 + imgHeight + 2);-->
<!--            });-->
<!--          }-->

<!--          const processRows = (pdfY) => {-->
<!--            const exportContents = this.$el.querySelectorAll('.pdf-content .el-table__body-wrapper table tr');-->
<!--            const pageHeight = pdf.internal.pageSize.getHeight() - 20;-->

<!--            const processRow = (index) => {-->
<!--              if (index < exportContents.length) {-->
<!--                const row = exportContents[index];-->
<!--                html2canvas(row, {-->
<!--                  scale: 2,-->
<!--                  useCORS: true-->
<!--                }).then(canvas => {-->
<!--                  const imgData = canvas.toDataURL('image/jpeg', 0.8);-->
<!--                  const imgWidth = 190;-->
<!--                  let imgHeight = canvas.height * imgWidth / canvas.width;-->

<!--                  if (pdfY + imgHeight > pageHeight) {-->
<!--                    pdf.addPage();-->
<!--                    pdfY = 10;-->
<!--                  }-->

<!--                  pdf.addImage(imgData, 'JPEG', 10, pdfY, imgWidth, imgHeight);-->
<!--                  pdfY += imgHeight + 2;-->

<!--                  processRow(index + 1);-->
<!--                });-->
<!--              } else {-->
<!--                const filename = `等保测评报告_${this.selectedIP || '未知IP'}_${this.protectionLevel}级_${new Date().toISOString().slice(0,10)}.pdf`;-->
<!--                pdf.save(filename);-->
<!--                this.showContentForPDF = false;-->
<!--                this.pdfLoading = false; // 在PDF生成完成后关闭loading状态-->
<!--                this.$message.success('PDF报告导出成功！');-->
<!--              }-->
<!--            };-->

<!--            processRow(0);-->
<!--          };-->
<!--        }).catch(error => {-->
<!--          console.error('PDF生成错误:', error);-->
<!--          this.showContentForPDF = false;-->
<!--          this.pdfLoading = false; // 发生错误时也要关闭loading-->
<!--          this.$message.error('PDF生成失败，请重试！');-->
<!--        });-->
<!--      }, 1000);-->
<!--      // 删除这里的 this.pdfLoading = false;，让它在PDF完成时才设置为false-->
<!--    },-->


<!--    // 搜索过滤-->
<!--    filterSearchResults() {-->
<!--      // 这个方法由于使用了计算属性，现在可以为空，-->
<!--      // 但保留此方法为将来可能的扩展-->
<!--    }-->
<!--  },-->
<!--  mounted() {-->
<!--    // this.fetchAndDisplayCheckResults();-->
<!--    this.fetchAliveHosts();-->
<!--  }-->
<!--}-->
<!--</script>-->

<!--<style scoped>-->
<!--.security-assessment-container {-->
<!--  padding: 20px;-->
<!--  background-color: #f5f7fa;-->
<!--  min-height: 100vh;-->
<!--}-->

<!--.header-section {-->
<!--  display: flex;-->
<!--  justify-content: space-between;-->
<!--  align-items: center;-->
<!--  margin-bottom: 20px;-->
<!--}-->

<!--.main-title {-->
<!--  color: #303133;-->
<!--  font-size: 24px;-->
<!--  font-weight: bold;-->
<!--  margin: 0;-->
<!--}-->

<!--.control-panel {-->
<!--  margin-bottom: 20px;-->
<!--}-->

<!--.control-card {-->
<!--  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);-->
<!--}-->

<!--.control-row {-->
<!--  display: flex;-->
<!--  flex-wrap: wrap;-->
<!--  gap: 15px;-->
<!--  margin-bottom: 15px;-->
<!--}-->

<!--.action-row {-->
<!--  display: flex;-->
<!--  align-items: center;-->
<!--  flex-wrap: wrap;-->
<!--  gap: 15px;-->
<!--}-->

<!--.control-item {-->
<!--  min-width: 180px;-->
<!--}-->

<!--.search-box {-->
<!--  flex-grow: 1;-->
<!--}-->

<!--.result-display {-->
<!--  display: flex;-->
<!--  align-items: center;-->
<!--  gap: 20px;-->
<!--  margin-left: auto;-->
<!--}-->

<!--.score-card, .conclusion-card {-->
<!--  display: flex;-->
<!--  align-items: center;-->
<!--  background: #f5f7fa;-->
<!--  padding: 8px 15px;-->
<!--  border-radius: 4px;-->
<!--}-->

<!--.score-label, .conclusion-label {-->
<!--  font-size: 16px;-->
<!--  font-weight: bold;-->
<!--  color: #606266;-->
<!--  margin-right: 5px;-->
<!--}-->

<!--.score-value {-->
<!--  font-size: 18px;-->
<!--  font-weight: bold;-->
<!--  color: #f56c6c;-->
<!--}-->

<!--.conclusion-value {-->
<!--  font-size: 18px;-->
<!--  font-weight: bold;-->
<!--  color: #f56c6c;-->
<!--}-->

<!--.server-info-section {-->
<!--  margin-bottom: 20px;-->
<!--}-->

<!--.server-info-card {-->
<!--  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);-->
<!--}-->

<!--.card-header {-->
<!--  display: flex;-->
<!--  justify-content: space-between;-->
<!--  align-items: center;-->
<!--  font-size: 16px;-->
<!--  font-weight: bold;-->
<!--}-->

<!--.server-info-grid {-->
<!--  display: grid;-->
<!--  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));-->
<!--  gap: 15px;-->
<!--}-->

<!--.info-item {-->
<!--  display: flex;-->
<!--  align-items: center;-->
<!--}-->

<!--.info-label {-->
<!--  font-weight: bold;-->
<!--  color: #606266;-->
<!--  margin-right: 5px;-->
<!--}-->

<!--.info-value {-->
<!--  color: #303133;-->
<!--}-->

<!--.table-section {-->
<!--  margin-bottom: 20px;-->
<!--}-->

<!--.table-card {-->
<!--  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);-->
<!--}-->

<!--.failed-result {-->
<!--  color: #f56c6c;-->
<!--}-->

<!--/* PDF内容样式 */-->
<!--.pdf-content {-->
<!--  font-size: 10pt;-->
<!--  max-width: 297mm;-->
<!--  padding: 15mm;-->
<!--  box-sizing: border-box;-->
<!--  background: white;-->
<!--}-->

<!--.pdf-content h1 {-->
<!--  font-size: 14pt;-->
<!--}-->

<!--.pdf-content p {-->
<!--  font-size: 9pt;-->
<!--}-->

<!--@media print {-->
<!--  .pdf-content {-->
<!--    width: 210mm;-->
<!--    height: 297mm;-->
<!--  }-->
<!--}-->

<!--.el-table .warning-row {-->
<!--  background: rgba(245, 108, 108, 0.1);-->
<!--}-->

<!--.el-table .success-row {-->
<!--  background: rgba(103, 194, 58, 0.1);-->
<!--}-->
<!--</style>-->
