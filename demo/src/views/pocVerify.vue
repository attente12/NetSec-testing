<template>
  <div class="container">
    <div class="title">
      <h1>POC验证 <small v-if="currentIp">- IP: {{ currentIp }}</small></h1>
      <el-button size="medium" @click="goPocScanner" type="info">返回上一步（漏洞扫描）</el-button>
    </div>

    <el-row style="margin-top: 20px;">
      <el-col :span="24">
        <el-card class="box-card">
          <div slot="header">POC任务</div>
          <el-button type="primary" @click="batchExecutePOC" style="margin-top: 5px;">批量执行POC</el-button>
          <!--          <el-button @click="printResult" style="margin-top: 5px;">打印报告</el-button>-->
          <el-table
              ref="table"
              :data="paginatedTasks"
              stripe
              style="width: 100%; margin-top: 10px"
              :row-key="row => row.CVE"
              :default-sort="{prop: 'CVE', order: 'descending'}">

            <el-table-column type="selection" width="55"></el-table-column>
            <!--            <el-table-column prop="CVE" label="漏洞编号" width="180"></el-table-column>-->
            <!-- el-tooltip显示漏洞描述 -->
            <el-table-column prop="CVE" label="漏洞编号" width="180">
              <template slot-scope="scope">
                <el-tooltip class="item" effect="dark" :content="scope.row.summary" placement="top">
                  <span>{{ scope.row.CVE }}</span>
                </el-tooltip>
              </template>
            </el-table-column>

            <el-table-column prop="CVEName" label="漏洞名称" width="180"></el-table-column>
            <el-table-column prop="CVSS" label="CVSS" width="100"></el-table-column>

            <el-table-column prop="POCState" label="POC是否存在" width="150">
              <template slot-scope="scope">
                <span :class="{ 'failed-result': scope.row.POCState === '否' }">{{ scope.row.POCState }}</span>
              </template>
            </el-table-column>

            <el-table-column prop="searchResult" label="扫描结果" width="140">
              <template slot-scope="scope">
                <span :class="{ 'failed-result': scope.row.searchResult === '存在' }">{{ scope.row.searchResult }}</span>
              </template>
            </el-table-column>

            <el-table-column label="操作" width="500">
              <template slot-scope="scope">
                <el-button size="mini" @click="ToVerify(scope.row)">编辑</el-button>
                <!--                <el-button size="mini" :disabled="scope.row.POCState === '是'" @click="handleEdit(scope.$index, scope.row)">编辑/上传POC</el-button>-->
                <!--                <el-button size="mini" @click="handleEdit(scope.$index, scope.row)">编辑/上传POC</el-button>-->
                <el-button size="mini" @click="executePOC(scope.row)">执行POC</el-button>
                <el-button size="mini" @click="lookDetails(scope.$index, scope.row)">查看执行细节</el-button>
                <!--                <el-button size="mini" type="danger" @click="handleDelete(scope.$index, scope.row)">删除</el-button>-->
              </template>
            </el-table-column>
          </el-table>
          <el-pagination
              @size-change="handleSizeChange"
              @current-change="handleCurrentChange"
              :current-page="pagination.currentPage"
              :page-sizes="[5, 10, 20, 50]"
              :page-size="pagination.pageSize"
              layout="total, sizes, prev, pager, next, jumper"
              :total="totalTasks">
          </el-pagination>

          <!-- 弹窗添加POC代码 -->
          <el-dialog :title="`添加POC代码: ${currentCveId2}`" :visible.sync="uploadDialogVisible" width="30%">
            <div>
              <p><strong>CVE ID:</strong> {{ currentCveId2 }}</p>
              <el-upload
                  ref="upload"
                  action=""
                  :file-list="fileList"
                  :on-change="handleFileChange"
                  :before-upload="beforeUpload"
                  :limit="1"
                  :auto-upload="false"
                  :multiple="false">
                <el-button size="small" type="primary">选择POC文件</el-button>
              </el-upload>
            </div>
            <span slot="footer" class="dialog-footer">
              <el-button @click="uploadDialogVisible = false">取消</el-button>
              <el-button type="primary" @click="submitPocUpload">确认上传</el-button>
            </span>
          </el-dialog>
        </el-card>
      </el-col>
    </el-row>

    <!-- 弹窗显示CVE详情 -->
    <el-dialog :title="currentCveId" :visible.sync="detailsDialogVisible" width="50%">
      <div>
        <p><strong>CVE ID:</strong> {{ currentCveId }}</p>
        <p><strong>漏洞名称:</strong> {{ currentCveName }}</p>
        <p><strong>CVSS:</strong> {{ currentCvss }}</p>
        <p><strong>详情:</strong> {{ details }}</p>
      </div>
      <span slot="footer" class="dialog-footer">
        <el-button @click="detailsDialogVisible = false">关闭</el-button>
      </span>
    </el-dialog>

    <!-- 打印区域（默认隐藏） -->
    <div id="printable" style="display: none;">
      <!-- 第一页 -->
      <div class="print-page">
        <h1 class="print-title">漏洞扫描报告</h1>
        <div class="print-info">
          <p><strong>IP地址：</strong>{{ scanResults[0]?.ip || currentIp }}</p>
          <p><strong>操作系统：</strong>{{ scanResults[0]?.os_list ? scanResults[0].os_list.join(', ') : '未知' }}</p>
          <p><strong>系统版本：</strong>{{ scanResults[0]?.os_matches ? scanResults[0].os_matches.join(', ') : '未知' }}</p>
          <p><strong>扫描时间：</strong>{{ scanResults[0]?.scan_time || '未知' }}</p>
        </div>
      </div>

      <!-- 漏洞详情表格 -->
      <div class="print-content">
        <h2 class="detail-title">漏洞详情</h2>
        <div class="print-table-container">
          <table class="print-table">
            <thead>
            <tr>
              <th style="width: 15%">漏洞ID</th>
              <th style="width: 15%">漏洞名称</th>
              <th style="width: 8%">CVSS</th>
              <th style="width: 10%">POC存在</th>
              <th style="width: 12%">漏洞状态</th>
              <th style="width: 40%">描述</th>
            </tr>
            </thead>
            <tbody>
            <tr v-for="vuln in sortedVulnerabilities" :key="vuln.Vuln_id">
              <td>{{ vuln.Vuln_id }}</td>
              <td>{{ vuln.vul_name || '未命名' }}</td>
              <td>{{ vuln.CVSS || '-' }}</td>
              <td>{{ vuln.pocExist ? '是' : '否' }}</td>
              <td>{{ vuln.vulExist }}</td>
              <td class="description-cell">{{ vuln.summary }}</td>
            </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import html2canvas from 'html2canvas';
import { jsPDF } from 'jspdf';
import _ from 'lodash';

export default {
  data() {
    return {
      currentIp: '', // 当前处理的IP地址
      scanResults: [],
      pagination: {
        currentPage: 1,
        pageSize: 10
      },
      totalTasks: 0, // 总任务数量
      detailsDialogVisible: false, // 弹窗是否显示
      currentCveId: '', // 当前选择的CVE ID
      currentCveName: '', // 当前选择的漏洞名称
      currentCvss: '', // 当前选择的CVSS分数
      details: '', // 详情信息
      uploadDialogVisible: false, // 控制弹窗显示
      currentCveId2: '', // 当前选择的CVE ID
      fileList: [], // 存储用户上传的文件列表
    };
  },
  computed: {
    sortedVulnerabilities() {
      // 收集所有端口和CPE中的漏洞
      let allVulnerabilities = [];
      this.scanResults.forEach(scanResult => {
        scanResult.ports.forEach(port => {
          Object.values(port.cpes).forEach(cpeVulns => {
            allVulnerabilities = [...allVulnerabilities, ...cpeVulns];
          });
        });
      });

      // 按vulExist状态排序
      return _.orderBy(allVulnerabilities,
          [(v) => {
            if (v.vulExist === '存在') return 0;
            if (v.vulExist === '不存在') return 1;
            return 2;
          }],
          ['asc']
      );
    },
    paginatedTasks() {
      // 处理 scanResults 数据，提取需要的 CVE 信息
      let results = [];

      this.scanResults.forEach(scanHostResult => {
        scanHostResult.ports.forEach(port => {
          Object.keys(port.cpes).forEach(cpeKey => {
            const cveList = port.cpes[cpeKey];

            cveList.forEach(cve => {
              results.push({
                CVE: cve.Vuln_id,
                CVEName: cve.vul_name || 'N/A',
                CVSS: cve.CVSS || 'N/A',
                POCState: cve.pocExist ? '是' : '否',
                searchResult: cve.vulExist,
                summary: cve.summary || '没有描述'  // 添加summary字段
              });
            });
          });
        });
      });

      const start = (this.pagination.currentPage - 1) * this.pagination.pageSize;
      const end = start + this.pagination.pageSize;

      return results.slice(start, end);
    }
  },
  created() {
    // 从URL获取IP参数
    this.currentIp = this.$route.query.ip || '';
    if (!this.currentIp) {
      this.$message.warning('未提供IP地址参数，请返回扫描页面重新选择IP');
    }
    this.fetchCpeData();
  },
  methods: {
    // 更新localStorage中的POC验证结果
    updateLocalStorageWithPocResults(scanHostResult) {
      try {
        // 确保有IP地址
        if (!this.currentIp) {
          console.error('无法更新结果: 没有当前IP地址');
          return;
        }

        // 从localStorage获取现有结果
        const localStorageKey = `nmapResults-${this.currentIp}`;
        let existingData = sessionStorage.getItem(localStorageKey);
        let scanResults = [];

        if (existingData) {
          scanResults = JSON.parse(existingData);

          // 替换已有数据
          if (Array.isArray(scanResults) && scanResults.length > 0) {
            // 找到对应IP的索引，替换整个对象
            const index = scanResults.findIndex(item => item.ip === this.currentIp);
            if (index !== -1) {
              scanResults[index] = scanHostResult;
            } else {
              // 没找到就添加
              scanResults.push(scanHostResult);
            }
          } else {
            // 如果不是数组或为空，则创建新数组
            scanResults = [scanHostResult];
          }
        } else {
          // 如果不存在，则创建新数组
          scanResults = [scanHostResult];
        }

        // 保存回localStorage
        sessionStorage.setItem(localStorageKey, JSON.stringify(scanResults));
        console.log(`已更新 ${this.currentIp} 的POC验证结果到sessionStorage`);
      } catch (error) {
        console.error('更新sessionStorage中的POC验证结果失败:', error);
      }
    },

    fetchCpeData() {
      if (!this.currentIp) {
        this.$message.error('未提供IP地址参数');
        return;
      }

      // 从localStorage获取该IP的扫描结果
      const storedResults = sessionStorage.getItem(`nmapResults-${this.currentIp}`);
      if (storedResults) {
        try {
          this.scanResults = JSON.parse(storedResults);
          this.updateTotalTasks();  // 更新总任务数量
        } catch (error) {
          console.error('解析存储的扫描结果失败:', error);
          this.$message.error('加载扫描结果失败');

          // 如果本地存储解析失败，尝试从API获取
          this.fetchFromApi();
        }
      } else {
        // 如果本地没有保存，则从API获取
        this.fetchFromApi();
      }
    },

    // 从API获取数据
    fetchFromApi() {
      axios.post('api/pocSearch', { ip: this.currentIp })
          .then(response => {
            this.scanResults = response.data;
            this.updateTotalTasks();  // 更新总任务数量

            // 将结果保存到localStorage
            sessionStorage.setItem(`nmapResults-${this.currentIp}`, JSON.stringify(response.data));
          })
          .catch(error => {
            console.error("获取扫描结果失败:", error.response || error);
            this.$message.error('请求失败，请稍后再试');
          });
    },

    batchExecutePOC() {
      const selectedRows = this.$refs.table.selection;
      const cveIds = selectedRows.map(row => row.CVE);

      if (cveIds.length === 0) {
        this.$message.warning('请至少选择一个任务进行批量执行');
        return;
      }

      axios.post('/api/pocVerify', {
        cve_ids: cveIds,
        ip: this.currentIp  // 添加IP参数
      })
          .then(response => {
            this.$message.success('批量执行POC成功');

            // 更新本地存储中的数据
            if (response.data && response.data.ScanHostResult) {
              // 将响应数据保存到localStorage
              this.updateLocalStorageWithPocResults(response.data.ScanHostResult);
            }

            // 重新获取数据以显示最新结果
            this.fetchCpeData();
          })
          .catch(error => {
            console.error("There was an error during batch POC execution:", error);
            this.$message.error('批量执行POC失败，请稍后再试');
          });
    },

    executePOC(row) {
      axios.post('/api/pocVerify', {
        cve_ids: [row.CVE],
        ip: this.currentIp  // 添加IP参数
      })
          .then(response => {
            this.$message.info(`已执行POC: ${row.CVE}`);

            // 更新本地存储中的数据
            if (response.data && response.data.ScanHostResult) {
              // 将响应数据保存到localStorage
              this.updateLocalStorageWithPocResults(response.data.ScanHostResult);
            }

            // 重新获取数据以显示最新结果
            this.fetchCpeData();
          })
          .catch(error => {
            console.error(`There was an error executing POC for ${row.CVE}:`, error);
            this.$message.error('执行POC失败，请稍后再试');
          });
    },

    handleEdit(index, row) {
      console.log('编辑任务', index, row);
      // this.$router.push('/pocManage');
      this.currentCveId2 = row.CVE; // 设置当前选择的CVE ID
      this.fileList = []; // 清空文件列表
      this.uploadDialogVisible = true; // 显示上传对话框
    },
    // 文件上传时的处理逻辑
    handleFileChange(file, fileList) {
      this.fileList = fileList;
    },

    // 上传文件之前的处理逻辑（比如文件类型或大小限制）
    beforeUpload(file) {
      const isValid = file.size / 1024 / 1024 < 10; // 文件大小限制为10MB
      if (!isValid) {
        this.$message.error('文件大小不能超过10MB');
      }
      return isValid;
    },

    // 提交POC代码
    submitPocUpload() {
      if (this.fileList.length === 0) {
        this.$message.warning('请先选择文件');
        return;
      }

      const formData = new FormData();
      formData.append('cve_id', this.currentCveId2); // 添加CVE ID
      formData.append('file', this.fileList[0].raw); // 添加文件
      formData.append('ip', this.currentIp); // 添加IP参数

      // 发送POST请求
      axios
          .post('/api/updatePoc', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
          })
          .then(response => {
            // 使用后端返回的 message
            this.$message.success(response.data.message || 'POC上传成功');
            this.uploadDialogVisible = false; // 关闭对话框

            // 如果返回的数据包含更新后的扫描结果，更新localStorage
            if (response.data && response.data.ScanHostResult) {
              this.updateLocalStorageWithPocResults(response.data.ScanHostResult);
            }

            this.fetchCpeData(); // 刷新数据
          })
          .catch(error => {
            // 使用后端返回的错误消息
            const errorMessage = error.response?.data?.message || '上传失败，请稍后再试';
            this.$message.error(errorMessage);
            console.error('POC上传失败:', error);
          });
    },

    lookDetails(index, row) {
      console.log('查看细节', index, row);
      this.currentCveId = row.CVE;
      this.currentCveName = row.CVEName;
      this.currentCvss = row.CVSS;

      axios
          .post('/api/pocExcute', {
            CVE_id: row.CVE,
            ip: this.currentIp  // 添加IP参数
          })
          .then((response) => {
            this.details = response.data.message || '未提供详情';
            this.detailsDialogVisible = true; // 打开弹窗

            // 如果返回的数据包含更新后的扫描结果，更新localStorage
            if (response.data && response.data.ScanHostResult) {
              this.updateLocalStorageWithPocResults(response.data.ScanHostResult);
              // 刷新显示的数据
              this.fetchCpeData();
            }
          })
          .catch((error) => {
            console.error('获取漏洞详情失败:', error);
            this.$message.error('获取漏洞详情失败，请稍后再试');
          });
    },

    ToVerify(row){
      // 添加IP参数
      const rowWithIp = {...row, ip: this.currentIp};
      this.$router.push({
        path: '/toVerify', // 目标页面路径
        query: { data: JSON.stringify(rowWithIp) } // 将带IP的row对象序列化为字符串
      });
    },

    handleDelete(index, row) {
      console.log('删除任务', index, row);
    },

    updateTotalTasks() {
      let results = [];

      this.scanResults.forEach(scanHostResult => {
        scanHostResult.ports.forEach(port => {
          Object.keys(port.cpes).forEach(cpeKey => {
            const cveList = port.cpes[cpeKey];

            cveList.forEach(cve => {
              results.push({
                CVE: cve.Vuln_id,
                CVEName: cve.vul_name || 'N/A',
                CVSS: cve.CVSS || 'N/A',
                POCState: cve.pocExist ? '是' : '否',
                searchResult: cve.vulExist
              });
            });
          });
        });
      });

      this.totalTasks = results.length; // 更新总任务数量
    },

    handleSizeChange(newSize) {
      this.pagination.pageSize = newSize;
      this.pagination.currentPage = 1; // 重置到第一页
      this.updateTotalTasks(); // 更新总任务数
    },

    handleCurrentChange(newPage) {
      this.pagination.currentPage = newPage;
      this.updateTotalTasks(); // 更新总任务数
    },

    goPocScanner(){
      this.$nextTick(() => {
        // 返回时传递IP参数，保持连贯性
        this.$router.push({
          path: '/pocScanner',
          query: { ip: this.currentIp }
        });
      });
    },

    async printResult() {
      // 显示打印区域
      const printableArea = document.getElementById('printable');
      if (printableArea) {
        printableArea.style.display = 'block';
      }

      try {
        const pdf = new jsPDF({
          orientation: 'p',
          unit: 'mm',
          format: 'a4'
        });

        // 定义页面边距和可用区域
        const margin = 10;
        const pageWidth = pdf.internal.pageSize.getWidth();
        const pageHeight = pdf.internal.pageSize.getHeight();
        const contentWidth = pageWidth - (margin * 2);
        // const maxContentHeight = pageHeight - (margin * 2);

        // 渲染封面页
        const coverPage = document.querySelector('#printable .print-page');
        if (coverPage) {
          const canvas = await html2canvas(coverPage, {
            scale: 2,
            useCORS: true,
            backgroundColor: '#ffffff'
          });

          const imgData = canvas.toDataURL('image/jpeg', 1.0);
          const imgWidth = contentWidth;
          const imgHeight = canvas.height * imgWidth / canvas.width;

          pdf.addImage(imgData, 'JPEG', margin, margin, imgWidth, imgHeight);
          pdf.addPage();
        }

        // 渲染表格
        const table = document.querySelector('#printable .print-table');
        if (table) {
          // 获取表头
          const thead = table.querySelector('thead');
          const theadCanvas = await html2canvas(thead, {
            scale: 2,
            useCORS: true,
            backgroundColor: '#ffffff'
          });

          const headerImgData = theadCanvas.toDataURL('image/jpeg', 1.0);
          const headerImgWidth = contentWidth;
          const headerHeight = theadCanvas.height * headerImgWidth / theadCanvas.width;

          // 处理表格体
          const tbody = table.querySelector('tbody');
          const rows = tbody.querySelectorAll('tr');
          let currentY = margin;

          // 在每页开始时添加表头
          const addHeader = (y) => {
            pdf.addImage(headerImgData, 'JPEG', margin, y, headerImgWidth, headerHeight);
            return y + headerHeight + 2; // 返回表头后的Y位置
          };

          currentY = addHeader(currentY);

          // 逐行处理表格内容
          for (let row of rows) {
            const canvas = await html2canvas(row, {
              scale: 2,
              useCORS: true,
              backgroundColor: '#ffffff'
            });

            const imgData = canvas.toDataURL('image/jpeg', 1.0);
            const imgWidth = contentWidth;
            const imgHeight = canvas.height * imgWidth / canvas.width;

            // 检查是否需要新页面
            if (currentY + imgHeight > pageHeight - margin) {
              pdf.addPage();
              currentY = margin;
              currentY = addHeader(currentY); // 在新页面添加表头
            }

            pdf.addImage(imgData, 'JPEG', margin, currentY, imgWidth, imgHeight);
            currentY += imgHeight + 1; // 添加1mm的行间距
          }

          // 保存PDF
          pdf.save(`poc-verification-report-${this.currentIp}.pdf`);
        }
      } catch (error) {
        console.error('Error generating PDF:', error);
        this.$message.error('生成PDF报告时发生错误');
      } finally {
        // 隐藏打印区域
        if (printableArea) {
          printableArea.style.display = 'none';
        }
      }
    }
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
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1);
}

.title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.title h1 small {
  font-size: 16px;
  font-weight: normal;
  color: #606266;
  margin-left: 10px;
}

.scan-button {
  text-align: right;
  margin-top: 10px;
}

.failed-result {
  color: red;
}

.print-title {
  font-size: 39px;  /* 增大标题字号 */
  font-weight: bold;
  text-align: center;
  margin-bottom: 40px;
  color: #000;
}

.detail-title {
  font-size: 30px;  /* 增大二级标题字号 */
  font-weight: bold;
  margin: 20px 0;
  color: #000;
}

.print-info {
  margin: 30px;
  font-size: 24px;  /* 增大基本信息字号 */
  line-height: 2;
}

.print-info p {
  margin: 15px 0;
}

.print-info strong {
  font-weight: bold;
  color: #000;
}

.print-table-container {
  padding: 15px;
}

.print-table {
  width: 100%;
  border-collapse: collapse;
  table-layout: fixed;
}

.print-table th,
.print-table td {
  border: 1.5px solid #000;  /* 加粗表格边框 */
  padding: 12px;  /* 增大单元格内边距 */
  text-align: left;
  vertical-align: top;
  word-wrap: break-word;
  font-size: 22px;  /* 增大表格内容字号 */
  line-height: 1.6;
  color: #000;
}

.print-table th {
  background-color: #f4f4f4;
  font-weight: bold;
  font-size: 16px;  /* 增大表头字号 */
  text-align: center;  /* 表头居中 */
  padding: 15px;  /* 增大表头内边距 */
}

.print-table td.description-cell {
  white-space: normal;
  min-height: 50px;  /* 增大描述单元格最小高度 */
  height: auto;
  line-height: 1.8;  /* 增大描述文字行高 */
}

/* 设置每列的宽度比例 */
.table-cell:nth-child(1) { flex: 2; }
.table-cell:nth-child(2) { flex: 2; }
.table-cell:nth-child(3) { flex: 1; }
.table-cell:nth-child(4) { flex: 1; }
.table-cell:nth-child(5) { flex: 1; }
.table-cell:nth-child(6) { flex: 3; }
</style>


<!--5.18数据-->
<!--<template>-->
<!--  <div class="container">-->
<!--    <div class="title">-->
<!--      <h1>POC验证</h1>-->
<!--      <el-button size="medium" @click="goPocScanner" type="info">返回上一步（漏洞扫描）</el-button>-->
<!--    </div>-->

<!--    <el-row style="margin-top: 20px;">-->
<!--      <el-col :span="24">-->
<!--        <el-card class="box-card">-->
<!--          <div slot="header">POC任务</div>-->
<!--          <el-button type="primary" @click="batchExecutePOC" style="margin-top: 5px;">批量执行POC</el-button>-->
<!--&lt;!&ndash;          <el-button @click="printResult" style="margin-top: 5px;">打印报告</el-button>&ndash;&gt;-->
<!--          <el-table-->
<!--              ref="table"-->
<!--              :data="paginatedTasks"-->
<!--              stripe-->
<!--              style="width: 100%; margin-top: 10px"-->
<!--              :row-key="row => row.CVE"-->
<!--              :default-sort="{prop: 'CVE', order: 'descending'}">-->

<!--            <el-table-column type="selection" width="55"></el-table-column>-->
<!--            &lt;!&ndash;            <el-table-column prop="CVE" label="漏洞编号" width="180"></el-table-column>&ndash;&gt;-->
<!--            &lt;!&ndash; el-tooltip显示漏洞描述 &ndash;&gt;-->
<!--            <el-table-column prop="CVE" label="漏洞编号" width="180">-->
<!--              <template slot-scope="scope">-->
<!--                <el-tooltip class="item" effect="dark" :content="scope.row.summary" placement="top">-->
<!--                  <span>{{ scope.row.CVE }}</span>-->
<!--                </el-tooltip>-->
<!--              </template>-->
<!--            </el-table-column>-->

<!--            <el-table-column prop="CVEName" label="漏洞名称" width="180"></el-table-column>-->
<!--            <el-table-column prop="CVSS" label="CVSS" width="100"></el-table-column>-->

<!--            <el-table-column prop="POCState" label="POC是否存在" width="150">-->
<!--              <template slot-scope="scope">-->
<!--                <span :class="{ 'failed-result': scope.row.POCState === '否' }">{{ scope.row.POCState }}</span>-->
<!--              </template>-->
<!--            </el-table-column>-->

<!--            <el-table-column prop="searchResult" label="扫描结果" width="140">-->
<!--              <template slot-scope="scope">-->
<!--                <span :class="{ 'failed-result': scope.row.searchResult === '存在' }">{{ scope.row.searchResult }}</span>-->
<!--              </template>-->
<!--            </el-table-column>-->

<!--            <el-table-column label="操作" width="500">-->
<!--              <template slot-scope="scope">-->
<!--                <el-button size="mini" @click="ToVerify(scope.row)">编辑</el-button>-->
<!--                &lt;!&ndash;                <el-button size="mini" :disabled="scope.row.POCState === '是'" @click="handleEdit(scope.$index, scope.row)">编辑/上传POC</el-button>&ndash;&gt;-->
<!--                &lt;!&ndash;                <el-button size="mini" @click="handleEdit(scope.$index, scope.row)">编辑/上传POC</el-button>&ndash;&gt;-->
<!--                <el-button size="mini" @click="executePOC(scope.row)">执行POC</el-button>-->
<!--                <el-button size="mini" @click="lookDetails(scope.$index, scope.row)">查看执行细节</el-button>-->
<!--                &lt;!&ndash;                <el-button size="mini" type="danger" @click="handleDelete(scope.$index, scope.row)">删除</el-button>&ndash;&gt;-->
<!--              </template>-->
<!--            </el-table-column>-->
<!--          </el-table>-->
<!--          <el-pagination-->
<!--              @size-change="handleSizeChange"-->
<!--              @current-change="handleCurrentChange"-->
<!--              :current-page="pagination.currentPage"-->
<!--              :page-sizes="[5, 10, 20, 50]"-->
<!--              :page-size="pagination.pageSize"-->
<!--              layout="total, sizes, prev, pager, next, jumper"-->
<!--              :total="totalTasks">-->
<!--          </el-pagination>-->

<!--          &lt;!&ndash; 弹窗添加POC代码 &ndash;&gt;-->
<!--          <el-dialog :title="`添加POC代码: ${currentCveId2}`" :visible.sync="uploadDialogVisible" width="30%">-->
<!--            <div>-->
<!--              <p><strong>CVE ID:</strong> {{ currentCveId2 }}</p>-->
<!--              <el-upload-->
<!--                  ref="upload"-->
<!--                  action=""-->
<!--                  :file-list="fileList"-->
<!--                  :on-change="handleFileChange"-->
<!--                  :before-upload="beforeUpload"-->
<!--                  :limit="1"-->
<!--                  :auto-upload="false"-->
<!--                  :multiple="false">-->
<!--                <el-button size="small" type="primary">选择POC文件</el-button>-->
<!--              </el-upload>-->
<!--            </div>-->
<!--            <span slot="footer" class="dialog-footer">-->
<!--              <el-button @click="uploadDialogVisible = false">取消</el-button>-->
<!--              <el-button type="primary" @click="submitPocUpload">确认上传</el-button>-->
<!--            </span>-->
<!--          </el-dialog>-->
<!--        </el-card>-->
<!--      </el-col>-->
<!--    </el-row>-->

<!--    &lt;!&ndash; 弹窗显示CVE详情 &ndash;&gt;-->
<!--    <el-dialog :title="currentCveId" :visible.sync="detailsDialogVisible" width="50%">-->
<!--      <div>-->
<!--        <p><strong>CVE ID:</strong> {{ currentCveId }}</p>-->
<!--        <p><strong>漏洞名称:</strong> {{ currentCveName }}</p>-->
<!--        <p><strong>CVSS:</strong> {{ currentCvss }}</p>-->
<!--        <p><strong>详情:</strong> {{ details }}</p>-->
<!--      </div>-->
<!--      <span slot="footer" class="dialog-footer">-->
<!--        <el-button @click="detailsDialogVisible = false">关闭</el-button>-->
<!--      </span>-->
<!--    </el-dialog>-->

<!--    &lt;!&ndash; 打印区域（默认隐藏） &ndash;&gt;-->
<!--    <div id="printable" style="display: none;">-->
<!--      &lt;!&ndash; 第一页 &ndash;&gt;-->
<!--      <div class="print-page">-->
<!--        <h1 class="print-title">漏洞扫描报告</h1>-->
<!--        <div class="print-info">-->
<!--          <p><strong>IP地址：</strong>{{ scanResults[0].ip }}</p>-->
<!--          <p><strong>操作系统：</strong>{{ scanResults[0].os_list ? scanResults[0].os_list.join(', ') : '未知' }}</p>-->
<!--          <p><strong>系统版本：</strong>{{ scanResults[0].os_matches ? scanResults[0].os_matches.join(', ') : '未知' }}</p>-->
<!--          <p><strong>扫描时间：</strong>{{ scanResults[0].scan_time }}</p>-->
<!--        </div>-->
<!--      </div>-->

<!--      &lt;!&ndash; 漏洞详情表格 &ndash;&gt;-->
<!--      <div class="print-content">-->
<!--        <h2 class="detail-title">漏洞详情</h2>-->
<!--        <div class="print-table-container">-->
<!--          <table class="print-table">-->
<!--            <thead>-->
<!--            <tr>-->
<!--              <th style="width: 15%">漏洞ID</th>-->
<!--              <th style="width: 15%">漏洞名称</th>-->
<!--              <th style="width: 8%">CVSS</th>-->
<!--              <th style="width: 10%">POC存在</th>-->
<!--              <th style="width: 12%">漏洞状态</th>-->
<!--              <th style="width: 40%">描述</th>-->
<!--            </tr>-->
<!--            </thead>-->
<!--            <tbody>-->
<!--            <tr v-for="vuln in sortedVulnerabilities" :key="vuln.Vuln_id">-->
<!--              <td>{{ vuln.Vuln_id }}</td>-->
<!--              <td>{{ vuln.vul_name || '未命名' }}</td>-->
<!--              <td>{{ vuln.CVSS || '-' }}</td>-->
<!--              <td>{{ vuln.pocExist ? '是' : '否' }}</td>-->
<!--              <td>{{ vuln.vulExist }}</td>-->
<!--              <td class="description-cell">{{ vuln.summary }}</td>-->
<!--            </tr>-->
<!--            </tbody>-->
<!--          </table>-->
<!--        </div>-->
<!--      </div>-->
<!--    </div>-->

<!--    &lt;!&ndash; 打印区域（默认隐藏） &ndash;&gt;-->
<!--&lt;!&ndash;    <div id="printable" style="display: none;">&ndash;&gt;-->
<!--&lt;!&ndash;      &lt;!&ndash; 第一页 &ndash;&gt;&ndash;&gt;-->
<!--&lt;!&ndash;      <div class="print-page">&ndash;&gt;-->
<!--&lt;!&ndash;        <h1 class="print-title">漏洞扫描报告</h1>&ndash;&gt;-->
<!--&lt;!&ndash;        <div class="print-info">&ndash;&gt;-->
<!--&lt;!&ndash;          <p><strong>IP地址：</strong>{{ scanResults[0].ip }}</p>&ndash;&gt;-->
<!--&lt;!&ndash;          <p><strong>操作系统：</strong>{{ scanResults[0].os_list ? scanResults[0].os_list.join(', ') : '未知' }}</p>&ndash;&gt;-->
<!--&lt;!&ndash;          <p><strong>系统版本：</strong>{{ scanResults[0].os_matches ? scanResults[0].os_matches.join(', ') : '未知' }}</p>&ndash;&gt;-->
<!--&lt;!&ndash;          <p><strong>扫描时间：</strong>{{ scanResults[0].scan_time }}</p>&ndash;&gt;-->
<!--&lt;!&ndash;        </div>&ndash;&gt;-->
<!--&lt;!&ndash;      </div>&ndash;&gt;-->

<!--&lt;!&ndash;      &lt;!&ndash; 漏洞详情表格 &ndash;&gt;&ndash;&gt;-->
<!--&lt;!&ndash;      <div class="print-content">&ndash;&gt;-->
<!--&lt;!&ndash;        <h2>漏洞详情</h2>&ndash;&gt;-->
<!--&lt;!&ndash;        <div class="print-table-container">&ndash;&gt;-->
<!--&lt;!&ndash;          <table class="print-table">&ndash;&gt;-->
<!--&lt;!&ndash;            <thead>&ndash;&gt;-->
<!--&lt;!&ndash;            <tr>&ndash;&gt;-->
<!--&lt;!&ndash;              <th style="width: 15%">漏洞ID</th>&ndash;&gt;-->
<!--&lt;!&ndash;              <th style="width: 15%">漏洞名称</th>&ndash;&gt;-->
<!--&lt;!&ndash;              <th style="width: 8%">CVSS</th>&ndash;&gt;-->
<!--&lt;!&ndash;              <th style="width: 10%">POC存在</th>&ndash;&gt;-->
<!--&lt;!&ndash;              <th style="width: 12%">漏洞状态</th>&ndash;&gt;-->
<!--&lt;!&ndash;              <th style="width: 40%">描述</th>&ndash;&gt;-->
<!--&lt;!&ndash;            </tr>&ndash;&gt;-->
<!--&lt;!&ndash;            </thead>&ndash;&gt;-->
<!--&lt;!&ndash;            <tbody>&ndash;&gt;-->
<!--&lt;!&ndash;            <tr v-for="vuln in sortedVulnerabilities" :key="vuln.Vuln_id">&ndash;&gt;-->
<!--&lt;!&ndash;              <td>{{ vuln.Vuln_id }}</td>&ndash;&gt;-->
<!--&lt;!&ndash;              <td>{{ vuln.vul_name || '未命名' }}</td>&ndash;&gt;-->
<!--&lt;!&ndash;              <td>{{ vuln.CVSS || '-' }}</td>&ndash;&gt;-->
<!--&lt;!&ndash;              <td>{{ vuln.pocExist ? '是' : '否' }}</td>&ndash;&gt;-->
<!--&lt;!&ndash;              <td>{{ vuln.vulExist }}</td>&ndash;&gt;-->
<!--&lt;!&ndash;              <td class="description-cell">{{ vuln.summary }}</td>&ndash;&gt;-->
<!--&lt;!&ndash;            </tr>&ndash;&gt;-->
<!--&lt;!&ndash;            </tbody>&ndash;&gt;-->
<!--&lt;!&ndash;          </table>&ndash;&gt;-->
<!--&lt;!&ndash;        </div>&ndash;&gt;-->
<!--&lt;!&ndash;      </div>&ndash;&gt;-->
<!--&lt;!&ndash;    </div>&ndash;&gt;-->



<!--  </div>-->
<!--</template>-->

<!--<script>-->
<!--import axios from 'axios';-->
<!--import html2canvas from 'html2canvas';-->
<!--import { jsPDF } from 'jspdf';-->
<!--import _ from 'lodash';-->

<!--export default {-->
<!--  data() {-->
<!--    return {-->
<!--      scanResults: [],-->
<!--      pagination: {-->
<!--        currentPage: 1,-->
<!--        pageSize: 10-->
<!--      },-->
<!--      totalTasks: 0, // 总任务数量-->
<!--      detailsDialogVisible: false, // 弹窗是否显示-->
<!--      currentCveId: '', // 当前选择的CVE ID-->
<!--      currentCveName: '', // 当前选择的漏洞名称-->
<!--      currentCvss: '', // 当前选择的CVSS分数-->
<!--      details: '', // 详情信息-->
<!--      uploadDialogVisible: false, // 控制弹窗显示-->
<!--      currentCveId2: '', // 当前选择的CVE ID-->
<!--      fileList: [], // 存储用户上传的文件列表-->
<!--    };-->
<!--  },-->
<!--  computed: {-->
<!--    sortedVulnerabilities() {-->
<!--      // 收集所有端口和CPE中的漏洞-->
<!--      let allVulnerabilities = [];-->
<!--      this.scanResults.forEach(scanResult => {-->
<!--        scanResult.ports.forEach(port => {-->
<!--          Object.values(port.cpes).forEach(cpeVulns => {-->
<!--            allVulnerabilities = [...allVulnerabilities, ...cpeVulns];-->
<!--          });-->
<!--        });-->
<!--      });-->

<!--      // 按vulExist状态排序-->
<!--      return _.orderBy(allVulnerabilities,-->
<!--          [(v) => {-->
<!--            if (v.vulExist === '存在') return 0;-->
<!--            if (v.vulExist === '不存在') return 1;-->
<!--            return 2;-->
<!--          }],-->
<!--          ['asc']-->
<!--      );-->
<!--    },-->
<!--    paginatedTasks() {-->
<!--      // 处理 scanResults 数据，提取需要的 CVE 信息-->
<!--      let results = [];-->

<!--      this.scanResults.forEach(scanHostResult => {-->
<!--        scanHostResult.ports.forEach(port => {-->
<!--          Object.keys(port.cpes).forEach(cpeKey => {-->
<!--            const cveList = port.cpes[cpeKey];-->

<!--            cveList.forEach(cve => {-->
<!--              results.push({-->
<!--                CVE: cve.Vuln_id,-->
<!--                CVEName: cve.vul_name || 'N/A',-->
<!--                CVSS: cve.CVSS || 'N/A',-->
<!--                POCState: cve.pocExist ? '是' : '否',-->
<!--                searchResult: cve.vulExist,-->
<!--                summary: cve.summary || '没有描述'  // 添加summary字段-->
<!--              });-->
<!--            });-->
<!--          });-->
<!--        });-->
<!--      });-->

<!--      const start = (this.pagination.currentPage - 1) * this.pagination.pageSize;-->
<!--      const end = start + this.pagination.pageSize;-->

<!--      return results.slice(start, end);-->
<!--    }-->
<!--  },-->
<!--  created() {-->
<!--    this.fetchCpeData();-->
<!--  },-->
<!--  methods: {-->
<!--    fetchCpeData() {-->
<!--      axios.post('api/pocSearch', null)-->
<!--          .then(response => {-->
<!--            this.scanResults = response.data;-->
<!--            this.updateTotalTasks();  // 更新总任务数量-->
<!--          })-->
<!--          .catch(error => {-->
<!--            console.error("There was an error fetching the scan results:", error.response || error);-->
<!--            this.$message.error('请求失败，请稍后再试');-->
<!--          });-->
<!--    },-->
<!--    batchExecutePOC() {-->
<!--      const selectedRows = this.$refs.table.selection;-->
<!--      const cveIds = selectedRows.map(row => row.CVE);-->

<!--      if (cveIds.length === 0) {-->
<!--        this.$message.warning('请至少选择一个任务进行批量执行');-->
<!--        return;-->
<!--      }-->

<!--      axios.post('/api/pocVerify', { cve_ids: cveIds })-->
<!--          .then(() => {-->
<!--            this.$message.success('批量执行POC成功');-->
<!--            this.fetchCpeData(); // 刷新数据-->
<!--          })-->
<!--          .catch(error => {-->
<!--            console.error("There was an error during batch POC execution:", error);-->
<!--            this.$message.error('批量执行POC失败，请稍后再试');-->
<!--          });-->
<!--    },-->
<!--    executePOC(row) {-->
<!--      axios.post('/api/pocVerify', { cve_ids: [row.CVE] })-->
<!--          .then(() => {-->
<!--            this.$message.info(`已执行POC: ${row.CVE}`);-->
<!--            this.fetchCpeData(); // 刷新数据-->
<!--          })-->
<!--          .catch(error => {-->
<!--            console.error(`There was an error executing POC for ${row.CVE}:`, error);-->
<!--            this.$message.error('执行POC失败，请稍后再试');-->
<!--          });-->
<!--    },-->
<!--    handleEdit(index, row) {-->
<!--      console.log('编辑任务', index, row);-->
<!--      // this.$router.push('/pocManage');-->
<!--      this.currentCveId2 = row.CVE; // 设置当前选择的CVE ID-->
<!--      this.fileList = []; // 清空文件列表-->
<!--      this.uploadDialogVisible = true; // 显示上传对话框-->
<!--    },-->
<!--    // 文件上传时的处理逻辑-->
<!--    handleFileChange(file, fileList) {-->
<!--      this.fileList = fileList;-->
<!--    },-->

<!--    // 上传文件之前的处理逻辑（比如文件类型或大小限制）-->
<!--    beforeUpload(file) {-->
<!--      const isValid = file.size / 1024 / 1024 < 10; // 文件大小限制为10MB-->
<!--      if (!isValid) {-->
<!--        this.$message.error('文件大小不能超过10MB');-->
<!--      }-->
<!--      return isValid;-->
<!--    },-->

<!--    // 提交POC代码-->
<!--    submitPocUpload() {-->
<!--      if (this.fileList.length === 0) {-->
<!--        this.$message.warning('请先选择文件');-->
<!--        return;-->
<!--      }-->

<!--      const formData = new FormData();-->
<!--      formData.append('cve_id', this.currentCveId2); // 添加CVE ID-->
<!--      formData.append('file', this.fileList[0].raw); // 添加文件-->

<!--      // 发送POST请求-->
<!--      axios-->
<!--          .post('/api/updatePoc', formData, {-->
<!--            headers: { 'Content-Type': 'multipart/form-data' }-->
<!--          })-->
<!--          .then(response => {-->
<!--            // 使用后端返回的 message-->
<!--            this.$message.success(response.data.message || 'POC上传成功');-->
<!--            this.uploadDialogVisible = false; // 关闭对话框-->
<!--            this.fetchCpeData(); // 刷新数据-->
<!--          })-->
<!--          .catch(error => {-->
<!--            // 使用后端返回的错误消息-->
<!--            const errorMessage = error.response?.data?.message || '上传失败，请稍后再试';-->
<!--            this.$message.error(errorMessage);-->
<!--            console.error('POC上传失败:', error);-->
<!--          });-->
<!--    },-->
<!--    lookDetails(index, row) {-->
<!--      console.log('查看细节', index, row);-->
<!--      this.currentCveId = row.CVE;-->
<!--      this.currentCveName = row.CVEName;-->
<!--      this.currentCvss = row.CVSS;-->

<!--      axios-->
<!--          .post('/api/pocExcute', { CVE_id: row.CVE })-->
<!--          .then((response) => {-->
<!--            this.details = response.data.message || '未提供详情';-->
<!--            this.detailsDialogVisible = true; // 打开弹窗-->
<!--          })-->
<!--          .catch((error) => {-->
<!--            console.error('There was an error fetching the CVE details:', error);-->
<!--            this.$message.error('获取漏洞详情失败，请稍后再试');-->
<!--          });-->
<!--    },-->
<!--    ToVerify(row){-->
<!--      this.$router.push({-->
<!--        path: '/toVerify', // 目标页面路径-->
<!--        query: { data: JSON.stringify(row) } // 将 row 对象序列化为字符串-->
<!--      });-->
<!--    },-->
<!--    handleDelete(index, row) {-->
<!--      console.log('删除任务', index, row);-->
<!--    },-->
<!--    updateTotalTasks() {-->
<!--      let results = [];-->

<!--      this.scanResults.forEach(scanHostResult => {-->
<!--        scanHostResult.ports.forEach(port => {-->
<!--          Object.keys(port.cpes).forEach(cpeKey => {-->
<!--            const cveList = port.cpes[cpeKey];-->

<!--            cveList.forEach(cve => {-->
<!--              results.push({-->
<!--                CVE: cve.CVE_id,-->
<!--                CVEName: cve.vul_name || 'N/A',-->
<!--                CVSS: cve.CVSS || 'N/A',-->
<!--                POCState: cve.pocExist ? '是' : '否',-->
<!--                searchResult: cve.vulExist-->
<!--              });-->
<!--            });-->
<!--          });-->
<!--        });-->
<!--      });-->

<!--      this.totalTasks = results.length; // 更新总任务数量-->
<!--    },-->
<!--    handleSizeChange(newSize) {-->
<!--      this.pagination.pageSize = newSize;-->
<!--      this.pagination.currentPage = 1; // 重置到第一页-->
<!--      this.updateTotalTasks(); // 更新总任务数-->
<!--    },-->
<!--    handleCurrentChange(newPage) {-->
<!--      this.pagination.currentPage = newPage;-->
<!--      this.updateTotalTasks(); // 更新总任务数-->
<!--    },-->
<!--    goPocScanner(){-->
<!--      this.$nextTick(() => {-->
<!--        this.$router.push('/pocScanner');-->
<!--      });-->
<!--    },-->



<!--    async printResult() {-->
<!--      // 显示打印区域-->
<!--      const printableArea = document.getElementById('printable');-->
<!--      if (printableArea) {-->
<!--        printableArea.style.display = 'block';-->
<!--      }-->

<!--      try {-->
<!--        const pdf = new jsPDF({-->
<!--          orientation: 'p',-->
<!--          unit: 'mm',-->
<!--          format: 'a4'-->
<!--        });-->

<!--        // 定义页面边距和可用区域-->
<!--        const margin = 10;-->
<!--        const pageWidth = pdf.internal.pageSize.getWidth();-->
<!--        const pageHeight = pdf.internal.pageSize.getHeight();-->
<!--        const contentWidth = pageWidth - (margin * 2);-->
<!--        // const maxContentHeight = pageHeight - (margin * 2);-->

<!--        // 渲染封面页-->
<!--        const coverPage = document.querySelector('#printable .print-page');-->
<!--        if (coverPage) {-->
<!--          const canvas = await html2canvas(coverPage, {-->
<!--            scale: 2,-->
<!--            useCORS: true,-->
<!--            backgroundColor: '#ffffff'-->
<!--          });-->

<!--          const imgData = canvas.toDataURL('image/jpeg', 1.0);-->
<!--          const imgWidth = contentWidth;-->
<!--          const imgHeight = canvas.height * imgWidth / canvas.width;-->

<!--          pdf.addImage(imgData, 'JPEG', margin, margin, imgWidth, imgHeight);-->
<!--          pdf.addPage();-->
<!--        }-->

<!--        // 渲染表格-->
<!--        const table = document.querySelector('#printable .print-table');-->
<!--        if (table) {-->
<!--          // 获取表头-->
<!--          const thead = table.querySelector('thead');-->
<!--          const theadCanvas = await html2canvas(thead, {-->
<!--            scale: 2,-->
<!--            useCORS: true,-->
<!--            backgroundColor: '#ffffff'-->
<!--          });-->

<!--          const headerImgData = theadCanvas.toDataURL('image/jpeg', 1.0);-->
<!--          const headerImgWidth = contentWidth;-->
<!--          const headerHeight = theadCanvas.height * headerImgWidth / theadCanvas.width;-->

<!--          // 处理表格体-->
<!--          const tbody = table.querySelector('tbody');-->
<!--          const rows = tbody.querySelectorAll('tr');-->
<!--          let currentY = margin;-->

<!--          // 在每页开始时添加表头-->
<!--          const addHeader = (y) => {-->
<!--            pdf.addImage(headerImgData, 'JPEG', margin, y, headerImgWidth, headerHeight);-->
<!--            return y + headerHeight + 2; // 返回表头后的Y位置-->
<!--          };-->

<!--          currentY = addHeader(currentY);-->

<!--          // 逐行处理表格内容-->
<!--          for (let row of rows) {-->
<!--            const canvas = await html2canvas(row, {-->
<!--              scale: 2,-->
<!--              useCORS: true,-->
<!--              backgroundColor: '#ffffff'-->
<!--            });-->

<!--            const imgData = canvas.toDataURL('image/jpeg', 1.0);-->
<!--            const imgWidth = contentWidth;-->
<!--            const imgHeight = canvas.height * imgWidth / canvas.width;-->

<!--            // 检查是否需要新页面-->
<!--            if (currentY + imgHeight > pageHeight - margin) {-->
<!--              pdf.addPage();-->
<!--              currentY = margin;-->
<!--              currentY = addHeader(currentY); // 在新页面添加表头-->
<!--            }-->

<!--            pdf.addImage(imgData, 'JPEG', margin, currentY, imgWidth, imgHeight);-->
<!--            currentY += imgHeight + 1; // 添加1mm的行间距-->
<!--          }-->

<!--          // 保存PDF-->
<!--          pdf.save('poc-verification-report.pdf');-->
<!--        }-->
<!--      } catch (error) {-->
<!--        console.error('Error generating PDF:', error);-->
<!--        this.$message.error('生成PDF报告时发生错误');-->
<!--      } finally {-->
<!--        // 隐藏打印区域-->
<!--        if (printableArea) {-->
<!--          printableArea.style.display = 'none';-->
<!--        }-->
<!--      }-->
<!--    }-->


<!--  }-->
<!--}-->
<!--</script>-->

<!--<style scoped>-->
<!--.container {-->
<!--  margin: 20px;-->
<!--}-->

<!--.box-card {-->
<!--  display: flex;-->
<!--  flex-direction: column;-->
<!--  justify-content: space-between;-->
<!--  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1);-->
<!--}-->

<!--.scan-button {-->
<!--  text-align: right;-->
<!--  margin-top: 10px;-->
<!--}-->

<!--.failed-result {-->
<!--  color: red;-->
<!--}-->

<!--.print-title {-->
<!--  font-size: 39px;  /* 增大标题字号 */-->
<!--  font-weight: bold;-->
<!--  text-align: center;-->
<!--  margin-bottom: 40px;-->
<!--  color: #000;-->
<!--}-->

<!--.detail-title {-->
<!--  font-size: 30px;  /* 增大二级标题字号 */-->
<!--  font-weight: bold;-->
<!--  margin: 20px 0;-->
<!--  color: #000;-->
<!--}-->

<!--.print-info {-->
<!--  margin: 30px;-->
<!--  font-size: 24px;  /* 增大基本信息字号 */-->
<!--  line-height: 2;-->
<!--}-->

<!--.print-info p {-->
<!--  margin: 15px 0;-->
<!--}-->

<!--.print-info strong {-->
<!--  font-weight: bold;-->
<!--  color: #000;-->
<!--}-->

<!--.print-table-container {-->
<!--  padding: 15px;-->
<!--}-->

<!--.print-table {-->
<!--  width: 100%;-->
<!--  border-collapse: collapse;-->
<!--  table-layout: fixed;-->
<!--}-->

<!--.print-table th,-->
<!--.print-table td {-->
<!--  border: 1.5px solid #000;  /* 加粗表格边框 */-->
<!--  padding: 12px;  /* 增大单元格内边距 */-->
<!--  text-align: left;-->
<!--  vertical-align: top;-->
<!--  word-wrap: break-word;-->
<!--  font-size: 22px;  /* 增大表格内容字号 */-->
<!--  line-height: 1.6;-->
<!--  color: #000;-->
<!--}-->

<!--.print-table th {-->
<!--  background-color: #f4f4f4;-->
<!--  font-weight: bold;-->
<!--  font-size: 16px;  /* 增大表头字号 */-->
<!--  text-align: center;  /* 表头居中 */-->
<!--  padding: 15px;  /* 增大表头内边距 */-->
<!--}-->

<!--.print-table td.description-cell {-->
<!--  white-space: normal;-->
<!--  min-height: 50px;  /* 增大描述单元格最小高度 */-->
<!--  height: auto;-->
<!--  line-height: 1.8;  /* 增大描述文字行高 */-->
<!--}-->

<!--/*-->
<!--.print-title {-->
<!--  font-size: 24px;-->
<!--  text-align: center;-->
<!--  margin-bottom: 30px;-->
<!--}-->

<!--.print-info {-->
<!--  margin: 20px;-->
<!--  font-size: 14px;-->
<!--  line-height: 1.8;-->
<!--}-->

<!--.print-info p {-->
<!--  margin: 10px 0;-->
<!--}-->

<!--.print-table-container {-->
<!--  padding: 10px;-->
<!--}-->

<!--.print-table {-->
<!--  width: 100%;-->
<!--  border-collapse: collapse;-->
<!--  table-layout: fixed;-->
<!--}-->

<!--.print-table th,-->
<!--.print-table td {-->
<!--  border: 1px solid #ddd;-->
<!--  padding: 8px;-->
<!--  text-align: left;-->
<!--  vertical-align: top;-->
<!--  word-wrap: break-word;-->
<!--  font-size: 12px;-->
<!--  line-height: 1.4;-->
<!--}-->

<!--.print-table th {-->
<!--  background-color: #f4f4f4;-->
<!--  font-weight: bold;-->
<!--}-->

<!--.print-table td.description-cell {-->
<!--  white-space: normal;-->
<!--  min-height: 40px;-->
<!--  height: auto;-->
<!--}-->
<!--*/-->

<!--/*-->
<!--.print-table {-->
<!--  width: 100%;-->
<!--  border-collapse: collapse;-->
<!--}-->

<!--.print-table th,-->
<!--.print-table td,-->
<!--.table-cell {-->
<!--  border: 1px solid #ddd;-->
<!--  padding: 8px;-->
<!--  text-align: left;-->
<!--}-->

<!--.table-row {-->
<!--  display: flex;-->
<!--  border-bottom: 1px solid #ddd;-->
<!--}-->

<!--.table-cell {-->
<!--  flex: 1;-->
<!--  padding: 8px;-->
<!--  overflow: hidden;-->
<!--  text-overflow: ellipsis;-->
<!--  white-space: nowrap;-->
<!--}-->

<!-- */-->

<!--/* 设置每列的宽度比例 */-->
<!--.table-cell:nth-child(1) { flex: 2; }-->
<!--.table-cell:nth-child(2) { flex: 2; }-->
<!--.table-cell:nth-child(3) { flex: 1; }-->
<!--.table-cell:nth-child(4) { flex: 1; }-->
<!--.table-cell:nth-child(5) { flex: 1; }-->
<!--.table-cell:nth-child(6) { flex: 3; }-->
<!--</style>-->




<!--<template>-->
<!--  <div class="container">-->
<!--    <div class="title">-->
<!--      <h1>POC验证</h1>-->
<!--      <el-button size="medium" @click="goPocScanner" type="info">返回上一步（漏洞扫描）</el-button>-->
<!--    </div>-->

<!--    <el-row style="margin-top: 20px;">-->
<!--      <el-col :span="24">-->
<!--        <el-card class="box-card">-->
<!--          <div slot="header">POC任务</div>-->
<!--          <el-button type="primary" @click="batchExecutePOC" style="margin-top: 5px;">批量执行POC</el-button>-->
<!--          <el-button @click="printResult" style="margin-top: 5px;">打印报告</el-button>-->
<!--          <el-table-->
<!--              ref="table"-->
<!--              :data="paginatedTasks"-->
<!--              stripe-->
<!--              style="width: 100%; margin-top: 10px"-->
<!--              :row-key="row => row.CVE"-->
<!--              :default-sort="{prop: 'CVE', order: 'descending'}">-->

<!--            <el-table-column type="selection" width="55"></el-table-column>-->
<!--&lt;!&ndash;            <el-table-column prop="CVE" label="漏洞编号" width="180"></el-table-column>&ndash;&gt;-->
<!--            &lt;!&ndash; el-tooltip显示漏洞描述 &ndash;&gt;-->
<!--            <el-table-column prop="CVE" label="漏洞编号" width="180">-->
<!--              <template slot-scope="scope">-->
<!--                <el-tooltip class="item" effect="dark" :content="scope.row.summary" placement="top">-->
<!--                  <span>{{ scope.row.CVE }}</span>-->
<!--                </el-tooltip>-->
<!--              </template>-->
<!--            </el-table-column>-->

<!--            <el-table-column prop="CVEName" label="漏洞名称" width="180"></el-table-column>-->
<!--            <el-table-column prop="CVSS" label="CVSS" width="100"></el-table-column>-->

<!--            <el-table-column prop="POCState" label="POC是否存在" width="150">-->
<!--              <template slot-scope="scope">-->
<!--                <span :class="{ 'failed-result': scope.row.POCState === '否' }">{{ scope.row.POCState }}</span>-->
<!--              </template>-->
<!--            </el-table-column>-->

<!--            <el-table-column prop="searchResult" label="扫描结果" width="140">-->
<!--              <template slot-scope="scope">-->
<!--                <span :class="{ 'failed-result': scope.row.searchResult === '未发现漏洞' }">{{ scope.row.searchResult }}</span>-->
<!--              </template>-->
<!--            </el-table-column>-->

<!--            <el-table-column label="操作" width="500">-->
<!--              <template slot-scope="scope">-->
<!--                <el-button size="mini" @click="ToVerify(scope.row)">去验证</el-button>-->
<!--&lt;!&ndash;                <el-button size="mini" :disabled="scope.row.POCState === '是'" @click="handleEdit(scope.$index, scope.row)">编辑/上传POC</el-button>&ndash;&gt;-->
<!--&lt;!&ndash;                <el-button size="mini" @click="handleEdit(scope.$index, scope.row)">编辑/上传POC</el-button>&ndash;&gt;-->
<!--                <el-button size="mini" @click="executePOC(scope.row)">执行POC</el-button>-->
<!--                <el-button size="mini" @click="lookDetails(scope.$index, scope.row)">查看执行细节</el-button>-->
<!--                &lt;!&ndash;                <el-button size="mini" type="danger" @click="handleDelete(scope.$index, scope.row)">删除</el-button>&ndash;&gt;-->
<!--              </template>-->
<!--            </el-table-column>-->
<!--          </el-table>-->
<!--          <el-pagination-->
<!--              @size-change="handleSizeChange"-->
<!--              @current-change="handleCurrentChange"-->
<!--              :current-page="pagination.currentPage"-->
<!--              :page-sizes="[5, 10, 20, 50]"-->
<!--              :page-size="pagination.pageSize"-->
<!--              layout="total, sizes, prev, pager, next, jumper"-->
<!--              :total="totalTasks">-->
<!--          </el-pagination>-->

<!--          &lt;!&ndash; 弹窗添加POC代码 &ndash;&gt;-->
<!--          <el-dialog :title="`添加POC代码: ${currentCveId2}`" :visible.sync="uploadDialogVisible" width="30%">-->
<!--            <div>-->
<!--              <p><strong>CVE ID:</strong> {{ currentCveId2 }}</p>-->
<!--              <el-upload-->
<!--                  ref="upload"-->
<!--                  action=""-->
<!--                  :file-list="fileList"-->
<!--                  :on-change="handleFileChange"-->
<!--                  :before-upload="beforeUpload"-->
<!--                  :limit="1"-->
<!--                  :auto-upload="false"-->
<!--                  :multiple="false">-->
<!--                <el-button size="small" type="primary">选择POC文件</el-button>-->
<!--              </el-upload>-->
<!--            </div>-->
<!--            <span slot="footer" class="dialog-footer">-->
<!--              <el-button @click="uploadDialogVisible = false">取消</el-button>-->
<!--              <el-button type="primary" @click="submitPocUpload">确认上传</el-button>-->
<!--            </span>-->
<!--          </el-dialog>-->
<!--        </el-card>-->
<!--      </el-col>-->
<!--    </el-row>-->

<!--    &lt;!&ndash; 弹窗显示CVE详情 &ndash;&gt;-->
<!--    <el-dialog :title="currentCveId" :visible.sync="detailsDialogVisible" width="50%">-->
<!--      <div>-->
<!--        <p><strong>CVE ID:</strong> {{ currentCveId }}</p>-->
<!--        <p><strong>漏洞名称:</strong> {{ currentCveName }}</p>-->
<!--        <p><strong>CVSS:</strong> {{ currentCvss }}</p>-->
<!--        <p><strong>详情:</strong> {{ details }}</p>-->
<!--      </div>-->
<!--      <span slot="footer" class="dialog-footer">-->
<!--        <el-button @click="detailsDialogVisible = false">关闭</el-button>-->
<!--      </span>-->
<!--    </el-dialog>-->

<!--  </div>-->
<!--</template>-->

<!--<script>-->
<!--import axios from 'axios';-->

<!--export default {-->
<!--  data() {-->
<!--    return {-->
<!--      scanResults: [],-->
<!--      pagination: {-->
<!--        currentPage: 1,-->
<!--        pageSize: 10-->
<!--      },-->
<!--      totalTasks: 0, // 总任务数量-->
<!--      detailsDialogVisible: false, // 弹窗是否显示-->
<!--      currentCveId: '', // 当前选择的CVE ID-->
<!--      currentCveName: '', // 当前选择的漏洞名称-->
<!--      currentCvss: '', // 当前选择的CVSS分数-->
<!--      details: '', // 详情信息-->
<!--      uploadDialogVisible: false, // 控制弹窗显示-->
<!--      currentCveId2: '', // 当前选择的CVE ID-->
<!--      fileList: [], // 存储用户上传的文件列表-->
<!--    };-->
<!--  },-->
<!--  computed: {-->
<!--    paginatedTasks() {-->
<!--      // 处理 scanResults 数据，提取需要的 CVE 信息-->
<!--      let results = [];-->

<!--      this.scanResults.forEach(scanHostResult => {-->
<!--        scanHostResult.ports.forEach(port => {-->
<!--          Object.keys(port.cpes).forEach(cpeKey => {-->
<!--            const cveList = port.cpes[cpeKey];-->

<!--            cveList.forEach(cve => {-->
<!--              results.push({-->
<!--                CVE: cve.Vuln_id,-->
<!--                CVEName: cve.vul_name || 'N/A',-->
<!--                CVSS: cve.CVSS || 'N/A',-->
<!--                POCState: cve.pocExist ? '是' : '否',-->
<!--                searchResult: cve.vulExist,-->
<!--                summary: cve.summary || '没有描述'  // 添加summary字段-->
<!--              });-->
<!--            });-->
<!--          });-->
<!--        });-->
<!--      });-->

<!--      const start = (this.pagination.currentPage - 1) * this.pagination.pageSize;-->
<!--      const end = start + this.pagination.pageSize;-->

<!--      return results.slice(start, end);-->
<!--    }-->
<!--  },-->
<!--  created() {-->
<!--    this.fetchCpeData();-->
<!--  },-->
<!--  methods: {-->
<!--    fetchCpeData() {-->
<!--      axios.post('api/pocSearch', null)-->
<!--          .then(response => {-->
<!--            this.scanResults = response.data;-->
<!--            this.updateTotalTasks();  // 更新总任务数量-->
<!--          })-->
<!--          .catch(error => {-->
<!--            console.error("There was an error fetching the scan results:", error.response || error);-->
<!--            this.$message.error('请求失败，请稍后再试');-->
<!--          });-->
<!--    },-->
<!--    batchExecutePOC() {-->
<!--      const selectedRows = this.$refs.table.selection;-->
<!--      const cveIds = selectedRows.map(row => row.CVE);-->

<!--      if (cveIds.length === 0) {-->
<!--        this.$message.warning('请至少选择一个任务进行批量执行');-->
<!--        return;-->
<!--      }-->

<!--      axios.post('/api/pocVerify', { cve_ids: cveIds })-->
<!--          .then(() => {-->
<!--            this.$message.success('批量执行POC成功');-->
<!--            this.fetchCpeData(); // 刷新数据-->
<!--          })-->
<!--          .catch(error => {-->
<!--            console.error("There was an error during batch POC execution:", error);-->
<!--            this.$message.error('批量执行POC失败，请稍后再试');-->
<!--          });-->
<!--    },-->
<!--    executePOC(row) {-->
<!--      axios.post('/api/pocVerify', { cve_ids: [row.CVE] })-->
<!--          .then(() => {-->
<!--            this.$message.success(`POC 执行成功: ${row.CVE}`);-->
<!--            this.fetchCpeData(); // 刷新数据-->
<!--          })-->
<!--          .catch(error => {-->
<!--            console.error(`There was an error executing POC for ${row.CVE}:`, error);-->
<!--            this.$message.error('执行POC失败，请稍后再试');-->
<!--          });-->
<!--    },-->
<!--    handleEdit(index, row) {-->
<!--      console.log('编辑任务', index, row);-->
<!--      // this.$router.push('/pocManage');-->
<!--      this.currentCveId2 = row.CVE; // 设置当前选择的CVE ID-->
<!--      this.fileList = []; // 清空文件列表-->
<!--      this.uploadDialogVisible = true; // 显示上传对话框-->
<!--    },-->
<!--    // 文件上传时的处理逻辑-->
<!--    handleFileChange(file, fileList) {-->
<!--      this.fileList = fileList;-->
<!--    },-->

<!--    // 上传文件之前的处理逻辑（比如文件类型或大小限制）-->
<!--    beforeUpload(file) {-->
<!--      const isValid = file.size / 1024 / 1024 < 10; // 文件大小限制为10MB-->
<!--      if (!isValid) {-->
<!--        this.$message.error('文件大小不能超过10MB');-->
<!--      }-->
<!--      return isValid;-->
<!--    },-->

<!--    // 提交POC代码-->
<!--    submitPocUpload() {-->
<!--      if (this.fileList.length === 0) {-->
<!--        this.$message.warning('请先选择文件');-->
<!--        return;-->
<!--      }-->

<!--      const formData = new FormData();-->
<!--      formData.append('cve_id', this.currentCveId2); // 添加CVE ID-->
<!--      formData.append('file', this.fileList[0].raw); // 添加文件-->

<!--      // 发送POST请求-->
<!--      axios-->
<!--          .post('/api/updatePoc', formData, {-->
<!--            headers: { 'Content-Type': 'multipart/form-data' }-->
<!--          })-->
<!--          .then(response => {-->
<!--            // 使用后端返回的 message-->
<!--            this.$message.success(response.data.message || 'POC上传成功');-->
<!--            this.uploadDialogVisible = false; // 关闭对话框-->
<!--            this.fetchCpeData(); // 刷新数据-->
<!--          })-->
<!--          .catch(error => {-->
<!--            // 使用后端返回的错误消息-->
<!--            const errorMessage = error.response?.data?.message || '上传失败，请稍后再试';-->
<!--            this.$message.error(errorMessage);-->
<!--            console.error('POC上传失败:', error);-->
<!--          });-->
<!--    },-->
<!--    lookDetails(index, row) {-->
<!--      console.log('查看细节', index, row);-->
<!--      this.currentCveId = row.CVE;-->
<!--      this.currentCveName = row.CVEName;-->
<!--      this.currentCvss = row.CVSS;-->

<!--      axios-->
<!--          .post('/api/pocExcute', { CVE_id: row.CVE })-->
<!--          .then((response) => {-->
<!--            this.details = response.data.message || '未提供详情';-->
<!--            this.detailsDialogVisible = true; // 打开弹窗-->
<!--          })-->
<!--          .catch((error) => {-->
<!--            console.error('There was an error fetching the CVE details:', error);-->
<!--            this.$message.error('获取漏洞详情失败，请稍后再试');-->
<!--          });-->
<!--    },-->
<!--    ToVerify(row){-->
<!--      this.$router.push({-->
<!--        path: '/toVerify', // 目标页面路径-->
<!--        query: { data: JSON.stringify(row) } // 将 row 对象序列化为字符串-->
<!--      });-->
<!--    },-->
<!--    handleDelete(index, row) {-->
<!--      console.log('删除任务', index, row);-->
<!--    },-->
<!--    updateTotalTasks() {-->
<!--      let results = [];-->

<!--      this.scanResults.forEach(scanHostResult => {-->
<!--        scanHostResult.ports.forEach(port => {-->
<!--          Object.keys(port.cpes).forEach(cpeKey => {-->
<!--            const cveList = port.cpes[cpeKey];-->

<!--            cveList.forEach(cve => {-->
<!--              results.push({-->
<!--                CVE: cve.CVE_id,-->
<!--                CVEName: cve.vul_name || 'N/A',-->
<!--                CVSS: cve.CVSS || 'N/A',-->
<!--                POCState: cve.pocExist ? '是' : '否',-->
<!--                searchResult: cve.vulExist-->
<!--              });-->
<!--            });-->
<!--          });-->
<!--        });-->
<!--      });-->

<!--      this.totalTasks = results.length; // 更新总任务数量-->
<!--    },-->
<!--    handleSizeChange(newSize) {-->
<!--      this.pagination.pageSize = newSize;-->
<!--      this.pagination.currentPage = 1; // 重置到第一页-->
<!--      this.updateTotalTasks(); // 更新总任务数-->
<!--    },-->
<!--    handleCurrentChange(newPage) {-->
<!--      this.pagination.currentPage = newPage;-->
<!--      this.updateTotalTasks(); // 更新总任务数-->
<!--    },-->
<!--    goPocScanner(){-->
<!--      this.$nextTick(() => {-->
<!--        this.$router.push('/pocScanner');-->
<!--      });-->
<!--    },-->
<!--    printResult(){-->

<!--    }-->
<!--  }-->
<!--}-->
<!--</script>-->

<!--<style scoped>-->
<!--.container {-->
<!--  margin: 20px;-->
<!--}-->

<!--.box-card {-->
<!--  display: flex;-->
<!--  flex-direction: column;-->
<!--  justify-content: space-between;-->
<!--  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1);-->
<!--}-->

<!--.scan-button {-->
<!--  text-align: right;-->
<!--  margin-top: 10px;-->
<!--}-->

<!--.failed-result {-->
<!--  color: red;-->
<!--}-->
<!--</style>-->

