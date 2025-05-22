<template>
  <div>
    <h1 id="linuxBaseline">基线检测报告</h1>
    <!-- 检测时间 -->
    <div style="text-align:right; margin-top:20px;">
      <p style="font-size:18px;">检测时间：{{ new Date().toLocaleString() }}</p>
    </div>
    <!--        <el-button @click="onExportToExcel">导出为 Excel</el-button>-->
    <el-button @click="onExportToPDF">导出为 PDF</el-button>
    <el-row :gutter="20">
      <el-col :span="12">
        <p>主机名：{{ serverInfo.hostname }}</p>
      </el-col>
      <el-col :span="12">
        <p>主机架构：{{ serverInfo.arch }}</p>
      </el-col>
      <el-col :span="12">
        <p>主机CPU信息：{{ serverInfo.cpu }}</p>
      </el-col>
      <el-col :span="12">
        <p>主机物理CPU个数：{{ serverInfo.cpuPhysical }}</p>
      </el-col>
      <el-col :span="12">
        <p>主机物理CPU核心数：{{ serverInfo.cpuCore }}</p>
      </el-col>
      <el-col :span="12">
        <p>主机空闲内存：{{ serverInfo.free }}</p>
      </el-col>
      <el-col :span="12">
        <p>硬件型号：{{ serverInfo.ProductName }}</p>
      </el-col>
      <el-col :span="12">
        <p>主机版本信息：{{ serverInfo.version }}</p>
      </el-col>
      <el-col :span="12">
        <p>联网检测：{{ serverInfo.isInternet }}</p>
      </el-col>
    </el-row>

    <!--        <el-button @click="onRecheckButton">重新检测</el-button>-->

    <el-select v-model="selectedStatus" placeholder="请选择状态" style="width: 120px;">
      <el-option label="全部" value="all"></el-option>
      <el-option label="通过" value="passed"></el-option>
      <el-option label="未通过" value="failed"></el-option>
    </el-select>

    <el-input placeholder="输入检测项关键字..." v-model="searchTerm" @input="filterSearchResults"
      style="width: 300px;"></el-input>



    <el-table :data="filteredCheckresults" style="width: 100%">
      <el-table-column type="selection" width="55"></el-table-column>
      <el-table-column prop="description" label="检测项"></el-table-column>
      <el-table-column prop="basis" label="检测依据"></el-table-column>
      <el-table-column prop="result" label="检测结果"></el-table-column>
      <el-table-column prop="IsComply" label="是否符合基线" width="200%">
        <template slot-scope="scope">
          <span :class="{ 'failed-result': scope.row.IsComply === 'false' }">{{ scope.row.IsComply }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="recommend" label="修改建议" width="600%"></el-table-column>
    </el-table>

    <!-- 这部分内容在正常情况下不显示，只在导出 PDF 时显示 -->
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
          </el-col><el-col :span="12">
            <p>主机空闲内存：{{ serverInfo.free }}</p>
          </el-col>
          <el-col :span="24">
            <p>硬件型号：{{ serverInfo.ProductName }}</p>
          </el-col>
          <el-col :span="24">
            <p>主机版本信息：{{ serverInfo.version }}</p>
          </el-col>
          <el-col :span="24">
            <p>联网检测：{{ serverInfo.isInternet }}</p>
          </el-col>
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
        <el-table-column prop="IsComply" label="是否符合基线" width="120%">
          <template slot-scope="scope">
            <span :class="{ 'failed-result': scope.row.IsComply === 'false' }">{{ scope.row.IsComply
            }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="recommend" label="修改建议" width="400%"></el-table-column>
      </el-table>
    </div>

  </div>
</template>

<script>

import jsPDF from 'jspdf';//用于在客户端生成 PDF 文件
import html2canvas from 'html2canvas';//将 HTML 元素转换为画布 (canvas) 图像

export default {
  name: "baseCheck",
  data() {
    return {
      checkresults: [],
      serverInfo: {},
      selectedStatus: 'all',
      searchTerm: '',
      showContentForPDF: false // 控制内容显示的数据属性
    }
  },
  computed: {
    message() {
      return this.$store.state.message; // 读取共享状态
    },
    filteredCheckresults() {
      return this.checkresults.filter(result => {
        const matchesStatus = this.selectedStatus === 'all' ||
          (this.selectedStatus === 'passed' && result.IsComply === 'true') ||
          (this.selectedStatus === 'failed' && result.IsComply === 'false');
        const matchesSearch = !this.searchTerm ||
          result.description.toLowerCase().includes(this.searchTerm.toLowerCase());
        return matchesStatus && matchesSearch;
      });
    }

  },
  methods: {
    fetchAndDisplayChenckResults() {
      fetch('/api/userinfo')
        .then(response => response.json())
        .then(data => {
          this.checkresults = data.Event_result;
          this.serverInfo = data.ServerInfo;
        })
        .catch(error => console.error('Error:', error));
    },

    onExportToPDF() {
      this.showContentForPDF = true; // 确保PDF相关内容是可见的

      setTimeout(() => { // 增加延迟确保DOM完全更新
        const pdf = new jsPDF({
          orientation: 'p', // 横向
          unit: 'mm',//单位为毫米
          format: 'a4'//页面格式为A4
        });
        // 渲染PDF的服务器信息页
        const contentForPDF = this.$el.querySelector('.pdf-content .server1');
        html2canvas(contentForPDF, {
          scale: 2,
          useCORS: true
        }).then(canvas => {
          //const imgData = canvas.toDataURL('image/png');
          const imgData = canvas.toDataURL('image/jpeg', 0.8);//用jpeg格式，文件会小一点
          const imgWidth = 190; // 适应PDF的宽度
          let imgHeight = canvas.height * imgWidth / canvas.width; // 根据比例计算高度

          // 将服务器信息页添加到PDF
          //pdf.addImage(imgData, 'PNG', 10, 10, imgWidth, imgHeight);
          pdf.addImage(imgData, 'JPEG', 10, 10, imgWidth, imgHeight);

          // 在添加表格内容之前添加一个新页面
          pdf.addPage();

          // 首先渲染表头
          const header = this.$el.querySelector('.pdf-content .el-table__header-wrapper');
          if (header) {
            html2canvas(header, {  //转换成画布（canvas）
              scale: 2,
              useCORS: true
            }).then(canvas => {
              //const imgData = canvas.toDataURL('image/png');//转换为PNG格式的图像数据
              const imgData = canvas.toDataURL('image/jpeg', 0.8);
              const imgWidth = 190; // 适应PDF的宽度
              let imgHeight = canvas.height * imgWidth / canvas.width; // 根据比例计算高度

              //pdf.addImage(imgData, 'PNG', 10, 10, imgWidth, imgHeight);
              pdf.addImage(imgData, 'JPEG', 10, 10, imgWidth, imgHeight);

              // 然后开始渲染表格行
              processRows(10 + imgHeight + 2); // 将表头下面的位置作为起始位置
            });
          }

          //pdfY跟踪当前在PDF页面上的垂直位置
          const processRows = (pdfY) => {
            const exportContents = this.$el.querySelectorAll('.pdf-content .el-table__body-wrapper table tr');
            const pageHeight = pdf.internal.pageSize.getHeight() - 20; // 页面总高度减去上下边距

            const processRow = (index) => {
              if (index < exportContents.length) {
                const row = exportContents[index];
                html2canvas(row, {
                  scale: 2,
                  useCORS: true
                }).then(canvas => {
                  //const imgData = canvas.toDataURL('image/png');
                  const imgData = canvas.toDataURL('image/jpeg', 0.8);
                  const imgWidth = 190; // 适应PDF的宽度
                  let imgHeight = canvas.height * imgWidth / canvas.width; // 根据比例计算高度

                  if (pdfY + imgHeight > pageHeight) {//当前行的图像加上当前的pdfY值超出pageHeight则新建一个pdf页面
                    pdf.addPage(); // 添加新页面
                    pdfY = 10; // 重置Y位置
                  }

                  //pdf.addImage(imgData, 'PNG', 10, pdfY, imgWidth, imgHeight);
                  pdf.addImage(imgData, 'JPEG', 10, pdfY, imgWidth, imgHeight);
                  pdfY += imgHeight + 2; // 更新Y位置，并添加间隔

                  processRow(index + 1); // 处理下一行
                });
              } else {
                pdf.save('report.pdf'); // 所有行处理完毕后保存PDF
                this.showContentForPDF = false; // 隐藏PDF相关内容
              }
            };

            processRow(0); // 从第一行开始处理
          };
        });
      }, 1000);
    },
    getData() {
      if (!this.message.ServerInfo) {
        this.fetchAndDisplayChenckResults()
      } else {
        this.serverInfo = this.message.ServerInfo
        this.checkresults = this.message.Event_result
      }
    }
  },
  // beforeMount() {
  //   this.getData()
  // },
}
</script>

<style scoped>
/* 保留原有样式或按需调整 */
#linuxBaseline {
  font-size: 24px;
  color: #141010e1;
  text-align: center;
  margin-top: 20px;
}

#linuxBaseline2 {
  font-size: 32px;
  color: #141010e1;
  text-align: center;
  margin-top: 20px;
}

/*结果为false则显示为红色*/
.failed-result {
  color: red;
}

.server1 .el-col p {
  font-size: 22px;
  /* 增大字体大小为16像素 */
  white-space: pre-wrap;
  /* 允许自动换行 */
  line-height: 1.6;
  /* 增加行间距使阅读更加舒适 */
  margin-bottom: 5px;
  /* 增加段落之间的底部间距 */
}



/*文字分割的正确版本*/
.pdf-content {
  font-size: 10pt;
  /* 设置字体大小为10磅 */
  max-width: 297mm;
  /* A4 宽度约为 210mm */
  padding: 15mm;
  /* A4 页面常用边距 */
  box-sizing: border-box;
}

/* 单独调整某些元素的字体大小 */
.pdf-content h1 {
  font-size: 14pt;
  /* 较大的标题字体 */
}

.pdf-content p {
  font-size: 9pt;
  /* 正文的字体大小 */
}
</style>
