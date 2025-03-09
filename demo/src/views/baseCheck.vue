<template>
  <div class="baseline-container">
    <!-- 头部区域 -->
    <div class="header-section">
      <h1 class="main-title">Linux基线检测报告</h1>
      <div class="date-info">
        <el-tag type="info">检测时间：{{ new Date().toLocaleString() }}</el-tag>
      </div>
    </div>

    <!-- 控制按钮区域 -->
    <div class="control-section">
      <div class="button-group">
        <el-button
            @click="onExportToPDF"
            :loading="pdfLoading"
            icon="el-icon-document"
            type="primary">
          导出为 PDF
        </el-button>
        <el-button
            @click="goToClassifyProtect"
            type="success"
            icon="el-icon-s-check">
          去进行等保测评
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

    <!-- 服务器信息卡片 -->
    <el-card class="server-info-card">
      <div slot="header" class="card-header">
        <span><i class="el-icon-monitor"></i> 服务器信息</span>
      </div>
      <div class="server-info-grid">
        <el-row :gutter="30">
          <el-col :span="12"><div class="info-item"><span class="info-label">主机名：</span>{{serverInfo.hostname || '未知'}}</div></el-col>
          <el-col :span="12"><div class="info-item"><span class="info-label">主机架构：</span>{{serverInfo.arch || '未知'}}</div></el-col>
          <el-col :span="12"><div class="info-item"><span class="info-label">主机CPU信息：</span>{{serverInfo.cpu || '未知'}}</div></el-col>
          <el-col :span="12"><div class="info-item"><span class="info-label">主机物理CPU个数：</span>{{serverInfo.cpuPhysical || '未知'}}</div></el-col>
          <el-col :span="12"><div class="info-item"><span class="info-label">主机物理CPU核心数：</span>{{serverInfo.cpuCore || '未知'}}</div></el-col>
          <el-col :span="12"><div class="info-item"><span class="info-label">主机空闲内存：</span>{{serverInfo.free || '未知'}}</div></el-col>
          <el-col :span="12"><div class="info-item"><span class="info-label">硬件型号：</span>{{serverInfo.ProductName || '未知'}}</div></el-col>
          <el-col :span="12"><div class="info-item"><span class="info-label">主机版本信息：</span>{{serverInfo.version || '未知'}}</div></el-col>
          <el-col :span="12"><div class="info-item"><span class="info-label">联网检测：</span>{{serverInfo.isInternet || '未知'}}</div></el-col>
        </el-row>
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

      <el-table
          :data="filteredCheckresults"
          style="width: 100%"
          border
          stripe
          :header-cell-style="{background:'#f5f7fa',color:'#606266'}"
          v-loading="tableLoading">
        <el-table-column prop="description" label="检测项" min-width="150"></el-table-column>
        <el-table-column prop="basis" label="检测依据" min-width="150"></el-table-column>
        <el-table-column prop="result" label="检测结果" min-width="150"></el-table-column>
        <el-table-column label="是否符合基线" width="120">
          <template slot-scope="scope">
            <el-tag :type="scope.row.IsComply === 'true' ? 'success' : 'danger'">
              {{ scope.row.IsComply === 'true' ? '符合' : '不符合' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="recommend" label="修改建议" min-width="250"></el-table-column>
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
          <el-col :span="24"><p>联网检测：{{ serverInfo.isInternet }}</p></el-col>
        </el-row>
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

      <el-table :data="filteredCheckresults" style="width: 100%">
        <el-table-column prop="description" label="检测项"></el-table-column>
        <el-table-column prop="basis" label="检测依据"></el-table-column>
        <el-table-column prop="result" label="检测结果"></el-table-column>
        <el-table-column prop="IsComply" label="是否符合基线" width="120">
          <template slot-scope="scope">
            <span :class="{ 'failed-result': scope.row.IsComply === 'false' }">
              {{ scope.row.IsComply === 'true' ? '符合' : '不符合' }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="recommend" label="修改建议" width="400"></el-table-column>
      </el-table>
    </div>

  </div>
</template>

<script>
import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';

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
      tableLoading: false
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
    fetchAndDisplayChenckResults() {
      this.tableLoading = true;
      fetch('/api/userinfo')
          .then(response => response.json())
          .then(data => {
            this.checkresults = data.Event_result;
            this.serverInfo = data.ServerInfo;
            this.tableLoading = false;
          })
          .catch(error => {
            console.error('Error:', error);
            this.tableLoading = false;
            this.$message.error('获取检测结果失败，请重试');
          });
    },

    onExportToPDF() {
      this.pdfLoading = true;
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

          // 首先渲染表头
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
                const filename = `Linux基线检测报告_${new Date().toISOString().slice(0,10)}.pdf`;
                pdf.save(filename);
                this.showContentForPDF = false;
                this.pdfLoading = false;
                this.$message.success('PDF报告导出成功！');
              }
            };

            processRow(0);
          };
        }).catch(err => {
          console.error('Error during PDF export:', err);
          this.pdfLoading = false;
          this.showContentForPDF = false;
          this.$message.error('PDF生成失败，请重试！');
        });
      }, 1000);
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
    this.fetchAndDisplayChenckResults();
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
<!--  <div>-->
<!--    <h1 id="linuxBaseline">Linux基线检测报告</h1>-->
<!--    &lt;!&ndash; 检测时间 &ndash;&gt;-->
<!--    <div style="text-align:right; margin-top:20px;">-->
<!--      <p style="font-size:18px;">检测时间：{{ new Date().toLocaleString() }}</p>-->
<!--    </div>-->
<!--&lt;!&ndash;    <el-button @click="onExportToPDF">导出为 PDF</el-button>&ndash;&gt;-->
<!--    <el-button-->
<!--        @click="onExportToPDF"-->
<!--        :loading="pdfLoading"-->
<!--        icon="el-icon-document"-->
<!--        type="primary">-->
<!--      导出为 PDF-->
<!--    </el-button>-->
<!--    <el-row :gutter="20">-->
<!--      <el-col :span="12"><p>主机名：{{serverInfo.hostname}}</p></el-col>-->
<!--      <el-col :span="12"><p>主机架构：{{serverInfo.arch}}</p></el-col>-->
<!--      <el-col :span="12"><p>主机CPU信息：{{serverInfo.cpu}}</p></el-col>-->
<!--      <el-col :span="12"><p>主机物理CPU个数：{{serverInfo.cpuPhysical}}</p></el-col>-->
<!--      <el-col :span="12"><p>主机物理CPU核心数：{{serverInfo.cpuCore}}</p></el-col>-->
<!--      <el-col :span="12"><p>主机空闲内存：{{serverInfo.free}}</p></el-col>-->
<!--      <el-col :span="12"><p>硬件型号：{{serverInfo.ProductName}}</p></el-col>-->
<!--      <el-col :span="12"><p>主机版本信息：{{serverInfo.version}}</p></el-col>-->
<!--      <el-col :span="12"><p>联网检测：{{serverInfo.isInternet}}</p></el-col>-->
<!--    </el-row>-->

<!--    &lt;!&ndash;        <el-button @click="onRecheckButton">重新检测</el-button>&ndash;&gt;-->

<!--    <el-select v-model="selectedStatus" placeholder="请选择状态" style="width: 120px;">-->
<!--      <el-option label="全部" value="all"></el-option>-->
<!--      <el-option label="通过" value="passed"></el-option>-->
<!--      <el-option label="未通过" value="failed"></el-option>-->
<!--    </el-select>-->

<!--    <el-input placeholder="输入检测项关键字..." v-model="searchTerm" @input="filterSearchResults" style="width: 300px;"></el-input>-->



<!--    <el-table :data="filteredCheckresults" style="width: 100%">-->
<!--      <el-table-column type="selection" width="55"></el-table-column>-->
<!--      <el-table-column prop="description" label="检测项"></el-table-column>-->
<!--      <el-table-column prop="basis" label="检测依据"></el-table-column>-->
<!--      <el-table-column prop="result" label="检测结果"></el-table-column>-->
<!--      &lt;!&ndash;            <el-table-column prop="IsComply" label="是否符合基线" :formatter="formatCompliance"></el-table-column>&ndash;&gt;-->
<!--      <el-table-column prop="IsComply" label="是否符合基线" width="200%">-->
<!--        <template slot-scope="scope">-->
<!--          <span :class="{ 'failed-result': scope.row.IsComply === 'false' }">{{ scope.row.IsComply }}</span>-->
<!--        </template>-->
<!--      </el-table-column>-->
<!--      <el-table-column prop="recommend" label="修改建议" width="600%"></el-table-column>-->
<!--    </el-table>-->

<!--    &lt;!&ndash; 这部分内容在正常情况下不显示，只在导出 PDF 时显示 &ndash;&gt;-->
<!--    <div class="pdf-content" v-show="showContentForPDF">-->
<!--      <div class="server1">-->
<!--        <h1 id="linuxBaseline2">Linux基线检测报告</h1>-->
<!--        &lt;!&ndash; 检测时间 &ndash;&gt;-->
<!--        <div style="text-align:right; margin-top:20px;">-->
<!--          <p style="font-size:18px;">检测时间：{{ new Date().toLocaleString() }}</p>-->
<!--        </div>-->
<!--        <el-row :gutter="20">-->
<!--          <el-col :span="24"><p>主机名：{{ serverInfo.hostname }}</p></el-col>-->
<!--          <el-col :span="24"><p>主机架构：{{ serverInfo.arch }}</p></el-col>-->
<!--          <el-col :span="24"><p>主机CPU信息：{{ serverInfo.cpu }}</p></el-col>-->
<!--          <el-col :span="24"><p>主机物理CPU个数：{{ serverInfo.cpuPhysical }}</p></el-col>-->
<!--          <el-col :span="24"><p>主机物理CPU核心数：{{ serverInfo.cpuCore }}</p></el-col><el-col :span="12"><p>主机空闲内存：{{ serverInfo.free }}</p></el-col>-->
<!--          <el-col :span="24"><p>硬件型号：{{ serverInfo.ProductName }}</p></el-col>-->
<!--          <el-col :span="24"><p>主机版本信息：{{ serverInfo.version }}</p></el-col>-->
<!--          <el-col :span="24"><p>联网检测：{{ serverInfo.isInternet }}</p></el-col>-->
<!--        </el-row>-->
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
<!--      </el-table>-->
<!--    </div>-->

<!--  </div>-->
<!--</template>-->

<!--<script>-->
<!--//引入xlsx库-->
<!--// import * as XLSX from 'xlsx';-->
<!--import jsPDF from 'jspdf';//用于在客户端生成 PDF 文件-->
<!--import html2canvas from 'html2canvas';//将 HTML 元素转换为画布 (canvas) 图像-->

<!--export default {-->
<!--  name:"baseCheck",-->
<!--  data() {-->
<!--    return {-->
<!--      checkresults: [],-->
<!--      serverInfo:{},-->
<!--      selectedStatus: 'all',-->
<!--      searchTerm: '',-->
<!--      showContentForPDF: false, // 控制内容显示的数据属性-->
<!--      pdfLoading: false // 新增PDF导出加载状态-->
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
<!--    }-->

<!--  },-->
<!--  methods: {-->
<!--    fetchAndDisplayChenckResults() {-->
<!--      fetch('/api/userinfo')-->
<!--          .then(response => response.json())-->
<!--          .then(data => {-->
<!--            this.checkresults = data.Event_result;-->
<!--            this.serverInfo = data.ServerInfo;-->
<!--          })-->
<!--          .catch(error => console.error('Error:', error));-->
<!--    },-->

<!--    onExportToPDF() {-->
<!--      this.pdfLoading = true; // 设置加载状态为true-->
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
<!--                this.pdfLoading = false; // 导出完成，设置加载状态为false-->
<!--              }-->
<!--            };-->

<!--            processRow(0); // 从第一行开始处理-->
<!--          };-->
<!--        }).catch(err => {-->
<!--          console.error('Error during PDF export:', err);-->
<!--          this.pdfLoading = false; // 出错时也要重置加载状态-->
<!--          this.showContentForPDF = false;-->
<!--        });-->
<!--      }, 1000);-->
<!--    }-->
<!--  },-->

<!--  mounted() {-->
<!--    this.fetchAndDisplayChenckResults();-->
<!--  }-->
<!--}-->
<!--</script>-->

<!--<style scoped>-->
<!--/* 保留原有样式或按需调整 */-->
<!--#linuxBaseline {-->
<!--  font-size: 24px;-->
<!--  color: #141010e1;-->
<!--  text-align: center;-->
<!--  margin-top: 20px;-->
<!--}-->

<!--#linuxBaseline2 {-->
<!--  font-size: 32px;-->
<!--  color: #141010e1;-->
<!--  text-align: center;-->
<!--  margin-top: 20px;-->
<!--}-->

<!--/*结果为false则显示为红色*/-->
<!--.failed-result {-->
<!--  color: red;-->
<!--}-->

<!--.server1 .el-col p {-->
<!--  font-size: 22px; /* 增大字体大小为16像素 */-->
<!--  white-space: pre-wrap; /* 允许自动换行 */-->
<!--  line-height: 1.6; /* 增加行间距使阅读更加舒适 */-->
<!--  margin-bottom: 5px; /* 增加段落之间的底部间距 */-->
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

