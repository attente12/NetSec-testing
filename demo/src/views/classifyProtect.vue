

<template>
  <div>
    <h1 id="linuxBaseline">等级保护测评</h1>
    <el-button @click="onExportToPDF" style="width: 120px;margin-right: 20px;">导出 pdf 报告</el-button>

    <el-select v-model="selectedStatus" placeholder="请选择状态" style="width: 120px;margin-right: 20px;">
      <el-option label="全部" value="all"></el-option>
      <el-option label="通过" value="passed"></el-option>
      <el-option label="未通过" value="failed"></el-option>
    </el-select>

    <el-input placeholder="输入检测项关键字..." v-model="searchTerm" @input="filterSearchResults" style="width: 300px;margin-right: 20px;"></el-input>
    <el-button @click="computeResult" type="success" style="margin-right: 30px;">计算评分</el-button>
    <div class="result-container">
      <div class="score-display">得分：{{ resultScore }}</div>
      <div class="conclusion">
        结论：
        <template v-if="resultScore !== ''">
          <span v-if="resultScore >= 90">优</span>
          <span v-else-if="resultScore >= 80 && resultScore < 90">良</span>
          <span v-else-if="resultScore >= 70 && resultScore < 80">中</span>
          <span v-else>差</span>
        </template>
      </div>
    </div>

    <el-table :data="filteredCheckresults" style="width: 100%">
<!--      <el-table-column type="selection" width="55"></el-table-column>-->
      <el-table-column prop="description" label="检测项"></el-table-column>
      <el-table-column prop="basis" label="检测依据"></el-table-column>
      <el-table-column prop="importantLevel" label="重要程度"></el-table-column>
      <el-table-column prop="result" label="检测结果"></el-table-column>
      <el-table-column prop="IsComply" label="是否符合基线" width="150%">
        <template slot-scope="scope">
          <span :class="{ 'failed-result': scope.row.IsComply === 'false' }">{{ scope.row.IsComply }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="recommend" label="修改建议" width="400%"></el-table-column>
      <el-table-column label="结果评分" width="180">
        <template slot-scope="scope">
          <el-select v-model="scope.row.score" placeholder="请选择评分">
            <el-option label="符合" value="1"></el-option>
            <el-option label="部分符合" value="0.5"></el-option>
            <el-option label="不符合" value="0"></el-option>
          </el-select>
        </template>
      </el-table-column>
    </el-table>

    <!-- 这部分内容在正常情况下不显示，只在导出 PDF 时显示 -->
    <div class="pdf-content" v-show="showContentForPDF">
      <div class="server1">
        <h1 id="linuxBaseline2" style="font-size: 24pt; text-align: center;">Linux等级保护测评报告</h1>
        <!-- 检测时间 -->
        <div style="text-align:right; margin-top:20px;">
          <p style="font-size:18px;">检测时间：{{ new Date().toLocaleString() }}</p>
        </div>
        <!-- 空白分隔 -->
        <div style="height:100px;"></div>
        <div class="result-container2" style="font-size: 18pt;">
          <div style="font-size: 20pt;margin-right: 200px;">测评得分：{{ resultScore }}</div>

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

          <!-- Add a line break here to start a new line -->
          <div style="height:30px;"></div>

          <el-row :gutter="20">
            <el-col :span="24"><p style="font-size: 15pt;">主机名：{{ serverInfo.hostname }}</p></el-col>
            <el-col :span="24"><p style="font-size: 15pt;">主机架构：{{ serverInfo.arch }}</p></el-col>
            <el-col :span="24"><p style="font-size: 15pt;">主机CPU信息：{{ serverInfo.cpu }}</p></el-col>
            <el-col :span="24"><p style="font-size: 15pt;">主机物理CPU个数：{{ serverInfo.cpuPhysical }}</p></el-col>
            <el-col :span="24"><p style="font-size: 15pt;">主机物理CPU核心数：{{ serverInfo.cpuCore }}</p></el-col>
            <el-col :span="12"><p style="font-size: 15pt;">主机空闲内存：{{ serverInfo.free }}</p></el-col>
            <el-col :span="24"><p style="font-size: 15pt;">硬件型号：{{ serverInfo.ProductName }}</p></el-col>
            <el-col :span="24"><p style="font-size: 15pt;">主机版本信息：{{ serverInfo.version }}</p></el-col>
            <el-col :span="24"><p style="font-size: 15pt;">联网检测：{{ serverInfo.isInternet }}</p></el-col>
          </el-row>
        </div>
        <!-- 空白分隔 -->
        <div style="height:250px;"></div>
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
            <span :class="{ 'failed-result': scope.row.IsComply === 'false' }">{{ scope.row.IsComply }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="recommend" label="修改建议" width="400%"></el-table-column>
        <el-table-column label="结果评分" width="180">
          <template slot-scope="scope">
            <span>{{ getScoreText(scope.row.score) }}</span>
          </template>
<!--          <template slot-scope="scope">-->
<!--            <el-select v-model="scope.row.score" placeholder="请选择评分">-->
<!--              <el-option label="符合" value="1"></el-option>-->
<!--              <el-option label="部分符合" value="0.5"></el-option>-->
<!--              <el-option label="不符合" value="0"></el-option>-->
<!--            </el-select>-->
<!--          </template>-->
        </el-table-column>
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
      serverInfo:{},
      selectedStatus: 'all',
      searchTerm: '',
      resultScore: localStorage.getItem('resultScore') || '',
      showContentForPDF: false // 控制内容显示的数据属性
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
        const numericScore = parseFloat(score); // 将 score 转换为数字
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
      // return (score) => {
      //   if (score === 1) {
      //     return '符合';
      //   } else if (score === 0.5) {
      //     return '部分符合';
      //   } else if (score === 0) {
      //     return '不符合';
      //   } else {
      //     return '未知';
      //   }
      // };
    }
  },
  methods: {
    fetchAndDisplayCheckResults() {
      fetch('/api/userinfo')
          .then(response => response.json())
          .then(data => {
            this.checkresults = data.Event_result.map(item => ({
              ...item,
              score: item.IsComply === 'true' ? '1' : '0.5'
              //score: item.score || '1' // 从后端获取评分数据，如果没有则默认空
            }));
            this.serverInfo = data.ServerInfo;
          })
          .catch(error => console.error('Error:', error));
    },
    computeResult() {
      const scoreMeasures = this.checkresults.map(item => ({
        importantLevelJson: item.importantLevel,
        IsComplyLevel: item.score.toString(),
      }));

      fetch('/api/classifyProtect', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ scoreMeasures })
      })
          .then(response => response.json())
          .then(data => {
            console.log("Received score from backend:", data.score); // Log the received score
            this.resultScore = data.score; // 更新 resultScore
            localStorage.setItem('resultScore', this.resultScore); // 将 resultScore 存储到 localStorage 中
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
    }


  },
  mounted() {
    this.fetchAndDisplayCheckResults();
  }
}
</script>

<style scoped>
.failed-result {
  color: red;
}
.result-container {
  display: inline-flex;
  align-items: center;
  gap: 20px; /* Adds space between score and conclusion */
  margin-top: 10px;
}
.result-container2 {
  //display: inline-flex;
  align-items: center;
  gap: 20px; /* Adds space between score and conclusion */
  margin-top: 10px;
}
.score-display,
.conclusion {
  font-size: 18px;
  font-weight: bold;
  color: #4CAF50;
}

/*文字分割的正确版本*/
.pdf-content {
  font-size: 10pt; /* 设置字体大小为10磅 */
  max-width: 297mm; /* A4 宽度约为 210mm */
  padding: 15mm; /* A4 页面常用边距 */
  box-sizing: border-box;
}

/* 单独调整某些元素的字体大小 */
.pdf-content h1 {
  font-size: 14pt; /* 较大的标题字体 */
}

.pdf-content p {
  font-size: 9pt; /* 正文的字体大小 */
}
</style>

