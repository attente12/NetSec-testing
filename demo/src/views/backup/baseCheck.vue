<!--tyf旧版本代码-->
<!--<template>-->
<!--  <div class="baseline-container">-->
<!--    &lt;!&ndash; 头部区域 &ndash;&gt;-->
<!--    <div class="header-section">-->
<!--      <h1 class="main-title">{{ isWindows ? 'Windows' : 'Linux' }}基线检测报告</h1>-->
<!--      <div class="date-info">-->
<!--        <el-tag type="info">检测时间：{{ new Date().toLocaleString() }}</el-tag>-->
<!--      </div>-->
<!--    </div>-->

<!--    &lt;!&ndash; 控制按钮区域 &ndash;&gt;-->
<!--    <div class="control-section">-->
<!--      <div class="button-group">-->
<!--        &lt;!&ndash; 新增的IP选择下拉框 &ndash;&gt;-->
<!--        <div class="control-item">-->
<!--          <el-select v-show="!isWindows" v-model="selectedIP" placeholder="选择服务器IP" @change="changeServer"-->
<!--                     size="medium">-->
<!--            <el-option v-for="ip in aliveHosts" :key="ip" :label="ip" :value="ip">-->
<!--            </el-option>-->
<!--          </el-select>-->
<!--        </div>-->

<!--        <el-button @click="onExportToPDF" :loading="pdfLoading" icon="el-icon-document" type="primary">-->
<!--          导出为 PDF-->
<!--        </el-button>-->
<!--        <el-button @click="changeOS" type="primary">-->
<!--          切换到{{ isWindows ? 'Linux' : 'Windows' }}检测报告-->
<!--        </el-button>-->
<!--        &lt;!&ndash;        <el-button&ndash;&gt;-->
<!--        &lt;!&ndash;            @click="goToClassifyProtect"&ndash;&gt;-->
<!--        &lt;!&ndash;            type="success"&ndash;&gt;-->
<!--        &lt;!&ndash;            icon="el-icon-s-check">&ndash;&gt;-->
<!--        &lt;!&ndash;          去进行等保测评&ndash;&gt;-->
<!--        &lt;!&ndash;        </el-button>&ndash;&gt;-->
<!--      </div>-->

<!--      <div class="filter-group">-->
<!--        <el-select v-model="selectedStatus" placeholder="请选择状态" size="medium">-->
<!--          <el-option label="全部" value="all"></el-option>-->
<!--          <el-option label="通过" value="passed"></el-option>-->
<!--          <el-option label="未通过" value="failed"></el-option>-->
<!--          <el-option label="待检查" value="pending"></el-option>-->
<!--        </el-select>-->

<!--        <el-input placeholder="输入检测项关键字..." v-model="searchTerm" @input="filterSearchResults"-->
<!--                  prefix-icon="el-icon-search" size="medium">-->
<!--        </el-input>-->
<!--      </div>-->
<!--    </div>-->

<!--    &lt;!&ndash; 服务器信息卡片 &ndash;&gt;-->
<!--    <el-card class="server-info-card">-->
<!--      <div slot="header" class="card-header">-->
<!--        <span><i class="el-icon-monitor"></i> 服务器信息</span>-->
<!--      </div>-->
<!--      <div class="server-info-grid">-->
<!--        <el-row :gutter="30">-->
<!--          <el-col :span="12">-->
<!--            <div class="info-item"><span class="info-label">主机名：</span>{{ serverInfo.hostname || '未知' }}</div>-->
<!--          </el-col>-->
<!--          <el-col :span="12">-->
<!--            <div class="info-item"><span class="info-label">主机架构：</span>{{ serverInfo.arch || '未知' }}</div>-->
<!--          </el-col>-->
<!--          <el-col :span="12">-->
<!--            <div class="info-item"><span class="info-label">主机CPU信息：</span>{{ serverInfo.cpu || '未知' }}</div>-->
<!--          </el-col>-->
<!--          <el-col :span="12">-->
<!--            <div class="info-item"><span class="info-label">主机物理CPU个数：</span>{{ serverInfo.cpuPhysical || '未知' }}</div>-->
<!--          </el-col>-->
<!--          <el-col :span="12">-->
<!--            <div class="info-item"><span class="info-label">主机物理CPU核心数：</span>{{ serverInfo.cpuCore || '未知' }}</div>-->
<!--          </el-col>-->
<!--          <el-col :span="12">-->
<!--            <div class="info-item"><span class="info-label">硬件型号：</span>{{ serverInfo.ProductName || '未知' }}</div>-->
<!--          </el-col>-->
<!--          <el-col :span="12">-->
<!--            <div class="info-item"><span class="info-label">主机版本信息：</span>{{ serverInfo.version || '未知' }}</div>-->
<!--          </el-col>-->
<!--          &lt;!&ndash;          <el-col :span="12"><div class="info-item"><span class="info-label">联网检测：</span>{{serverInfo.isInternet || '未知'}}</div></el-col>&ndash;&gt;-->
<!--        </el-row>-->
<!--      </div>-->
<!--    </el-card>-->

<!--    &lt;!&ndash; 检测结果表格 &ndash;&gt;-->
<!--    <el-card class="results-card">-->
<!--      <div slot="header" class="card-header">-->
<!--        <span><i class="el-icon-document-checked"></i> 检测结果</span>-->
<!--        <div class="summary">-->
<!--          <el-tag type="success">通过: {{ passedCount }}</el-tag>-->
<!--          <el-tag type="danger">未通过: {{ failedCount }}</el-tag>-->
<!--          <el-tag type="warning">待检查: {{ pendingCount }}</el-tag>-->
<!--          <el-tag type="info">总计: {{ totalCount }}</el-tag>-->
<!--        </div>-->
<!--      </div>-->

<!--      <el-table v-show="!isWindows" :data="filteredCheckresults" style="width: 100%" border stripe-->
<!--                :header-cell-style="{ background: '#f5f7fa', color: '#606266' }" v-loading="tableLoading">-->
<!--        <el-table-column label="序号" width="70" type="index"></el-table-column>-->
<!--        <el-table-column prop="description" label="检测项" min-width="150"></el-table-column>-->
<!--        <el-table-column prop="basis" label="基准" min-width="150"></el-table-column>-->
<!--        <el-table-column prop="result" label="检测结果" min-width="150"></el-table-column>-->
<!--        &lt;!&ndash;        <el-table-column label="基准/检测结果" min-width="200">&ndash;&gt;-->
<!--        &lt;!&ndash;          <template slot-scope="scope">&ndash;&gt;-->
<!--        &lt;!&ndash;            {{ scope.row.basis }}/{{ scope.row.result }}&ndash;&gt;-->
<!--        &lt;!&ndash;          </template>&ndash;&gt;-->
<!--        &lt;!&ndash;        </el-table-column>&ndash;&gt;-->
<!--        <el-table-column label="是否通过检查" width="120">-->
<!--          <template slot-scope="scope">-->
<!--            &lt;!&ndash;            <el-tag :type="scope.row.IsComply === 'true' ? 'success' : 'danger'">&ndash;&gt;-->
<!--            &lt;!&ndash;              {{ scope.row.IsComply === 'true' ? '通过' : '未通过' }}&ndash;&gt;-->
<!--            &lt;!&ndash;            </el-tag>&ndash;&gt;-->
<!--            <el-tag :type="getStatusType(scope.row.IsComply)">-->
<!--              {{ getStatusText(scope.row.IsComply) }}-->
<!--            </el-tag>-->
<!--          </template>-->
<!--        </el-table-column>-->
<!--        <el-table-column label="修改建议" min-width="250">-->
<!--          <template slot-scope="scope">-->
<!--            &lt;!&ndash;            <span v-if="scope.row.IsComply === 'false'">{{ scope.row.recommend }}</span>&ndash;&gt;-->
<!--            <span v-if="scope.row.IsComply === 'false' || scope.row.IsComply === 'pending'">{{ scope.row.recommend-->
<!--              }}</span>-->
<!--            <span v-else>-</span>-->
<!--          </template>-->
<!--        </el-table-column>-->
<!--      </el-table>-->

<!--      <el-table v-show="isWindows" :data="filteredCheckresults" style="width: 100%" border stripe-->
<!--                :header-cell-style="{ background: '#f5f7fa', color: '#606266' }" v-loading="tableLoading">-->
<!--        <el-table-column label="序号" width="70" type="index"></el-table-column>-->
<!--        <el-table-column prop="description" label="检测项" min-width="150"></el-table-column>-->
<!--        <el-table-column prop="basis" label="基准" min-width="150"></el-table-column>-->
<!--        <el-table-column prop="result" label="检测结果" min-width="150"></el-table-column>-->
<!--        &lt;!&ndash;        <el-table-column label="基准/检测结果" min-width="200">&ndash;&gt;-->
<!--        &lt;!&ndash;          <template slot-scope="scope">&ndash;&gt;-->
<!--        &lt;!&ndash;            {{ scope.row.basis }}/{{ scope.row.result }}&ndash;&gt;-->
<!--        &lt;!&ndash;          </template>&ndash;&gt;-->
<!--        &lt;!&ndash;        </el-table-column>&ndash;&gt;-->
<!--        <el-table-column label="是否通过检查" width="120">-->
<!--          <template slot-scope="scope">-->
<!--            &lt;!&ndash;            <el-tag :type="scope.row.IsComply === 'true' ? 'success' : 'danger'">&ndash;&gt;-->
<!--            &lt;!&ndash;              {{ scope.row.IsComply === 'true' ? '通过' : '未通过' }}&ndash;&gt;-->
<!--            &lt;!&ndash;            </el-tag>&ndash;&gt;-->
<!--            <el-tag :type="getStatusType(scope.row.IsComply)">-->
<!--              {{ getStatusText(scope.row.IsComply) }}-->
<!--            </el-tag>-->
<!--          </template>-->
<!--        </el-table-column>-->
<!--        <el-table-column label="修改建议" min-width="250">-->
<!--          <template slot-scope="scope">-->
<!--            &lt;!&ndash;            <span v-if="scope.row.IsComply === 'false'">{{ scope.row.recommend }}</span>&ndash;&gt;-->
<!--            <span v-if="scope.row.IsComply === 'false' || scope.row.IsComply === 'pending'">{{ scope.row.recommend-->
<!--              }}</span>-->
<!--            <span v-else>-</span>-->
<!--          </template>-->
<!--        </el-table-column>-->
<!--      </el-table>-->

<!--    </el-card>-->

<!--    &lt;!&ndash; PDF内容（隐藏） &ndash;&gt;-->
<!--    <div class="pdf-content" v-show="showContentForPDF">-->
<!--      <div class="server1">-->
<!--        <h1 id="linuxBaseline2">{{ isWindows ? 'Windows' : 'Linux' }}</h1>-->
<!--        &lt;!&ndash; 检测时间 &ndash;&gt;-->
<!--        <div style="text-align:right; margin-top:20px;">-->
<!--          <p style="font-size:18px;">检测时间：{{ new Date().toLocaleString() }}</p>-->
<!--        </div>-->
<!--        <el-row :gutter="20">-->
<!--          <el-col :span="24">-->
<!--            <p>主机名：{{ serverInfo.hostname }}</p>-->
<!--          </el-col>-->
<!--          <el-col :span="24">-->
<!--            <p>主机架构：{{ serverInfo.arch }}</p>-->
<!--          </el-col>-->
<!--          <el-col :span="24">-->
<!--            <p>主机CPU信息：{{ serverInfo.cpu }}</p>-->
<!--          </el-col>-->
<!--          <el-col :span="24">-->
<!--            <p>主机物理CPU个数：{{ serverInfo.cpuPhysical }}</p>-->
<!--          </el-col>-->
<!--          <el-col :span="24">-->
<!--            <p>主机物理CPU核心数：{{ serverInfo.cpuCore }}</p>-->
<!--          </el-col>-->
<!--          <el-col :span="12">-->
<!--            <p>主机空闲内存：{{ serverInfo.free }}</p>-->
<!--          </el-col>-->
<!--          <el-col :span="24">-->
<!--            <p>硬件型号：{{ serverInfo.ProductName }}</p>-->
<!--          </el-col>-->
<!--          <el-col :span="24">-->
<!--            <p>主机版本信息：{{ serverInfo.version }}</p>-->
<!--          </el-col>-->
<!--          <el-col :span="24">-->
<!--            <p>服务器IP：{{ selectedIP }}</p>-->
<!--          </el-col>-->
<!--        </el-row>-->
<!--        &lt;!&ndash; 空白分隔 &ndash;&gt;-->
<!--        <div style="height:200px;"></div>-->
<!--        &lt;!&ndash; 检测人员签名 &ndash;&gt;-->
<!--        <div style="text-align:right; margin-top:20px;">-->
<!--          <span style="font-size:20px;">检测人员签名：</span>-->
<!--          <span style="display: inline-block; width: 200px; border-bottom: 2px solid #000; margin-left: 10px;"></span>-->
<!--        </div>-->
<!--        &lt;!&ndash; 页码 &ndash;&gt;-->
<!--        <div class="page-number">-->
<!--          <span>1/{{ totalPages }}</span>-->
<!--        </div>-->
<!--      </div>-->

<!--      &lt;!&ndash; 测试正文标题 &ndash;&gt;-->
<!--      <div class="report-content-title">-->
<!--        <h2>测试正文</h2>-->
<!--      </div>-->

<!--      <el-table :data="filteredCheckresults" style="width: 100%">-->
<!--        <el-table-column label="序号" width="70" type="index"></el-table-column>-->
<!--        <el-table-column prop="description" label="检测项"></el-table-column>-->
<!--        <el-table-column prop="basis" label="检测依据" min-width="150"></el-table-column>-->
<!--        <el-table-column prop="result" label="检测结果" min-width="150"></el-table-column>-->
<!--        &lt;!&ndash;        <el-table-column label="基准/检测结果" min-width="200">&ndash;&gt;-->
<!--        &lt;!&ndash;          <template slot-scope="scope">&ndash;&gt;-->
<!--        &lt;!&ndash;            {{ scope.row.basis }}/{{ scope.row.result }}&ndash;&gt;-->
<!--        &lt;!&ndash;          </template>&ndash;&gt;-->
<!--        &lt;!&ndash;        </el-table-column>&ndash;&gt;-->
<!--        <el-table-column prop="IsComply" label="是否通过检查" width="120">-->
<!--          <template slot-scope="scope">-->
<!--            &lt;!&ndash;            <span :class="{ 'failed-result': scope.row.IsComply === 'false' }">&ndash;&gt;-->
<!--            &lt;!&ndash;              {{ scope.row.IsComply === 'true' ? '通过' : '未通过' }}&ndash;&gt;-->
<!--            &lt;!&ndash;            </span>&ndash;&gt;-->
<!--            <span :class="getStatusClass(scope.row.IsComply)">-->
<!--              {{ getStatusText(scope.row.IsComply) }}-->
<!--            </span>-->
<!--          </template>-->
<!--        </el-table-column>-->
<!--        <el-table-column label="修改建议" width="400">-->
<!--          <template slot-scope="scope">-->
<!--            <span v-if="scope.row.IsComply === 'false'">{{ scope.row.recommend }}</span>-->
<!--            <span v-else>-</span>-->
<!--          </template>-->
<!--        </el-table-column>-->
<!--      </el-table>-->
<!--      &lt;!&ndash; 页码容器 - PDF生成时会添加 &ndash;&gt;-->
<!--      <div class="page-numbers-container"></div>-->
<!--    </div>-->

<!--  </div>-->
<!--</template>-->

<!--<script>-->
<!--import jsPDF from 'jspdf';-->
<!--import html2canvas from 'html2canvas';-->
<!--import axios from 'axios'; // 引入axios-->

<!--export default {-->
<!--  name: "baseCheck",-->
<!--  data() {-->
<!--    return {-->
<!--      checkresults: [],-->
<!--      serverInfo: {},-->
<!--      selectedStatus: 'all',-->
<!--      searchTerm: '',-->
<!--      showContentForPDF: false,-->
<!--      pdfLoading: false,-->
<!--      tableLoading: false,-->
<!--      totalPages: 2, // 默认至少两页-->
<!--      aliveHosts: [], // 活跃主机IP列表-->
<!--      selectedIP: '', // 选中的IP-->
<!--      isWindows: false // 是否为Windows系统-->
<!--    }-->
<!--  },-->
<!--  computed: {-->
<!--    message() {-->
<!--      return this.$store.state.message; // 读取共享状态-->
<!--    },-->
<!--    filteredCheckresults() {-->
<!--      return this.checkresults.filter(result => {-->
<!--        const matchesStatus = this.selectedStatus === 'all' ||-->
<!--            (this.selectedStatus === 'passed' && result.IsComply === 'true') ||-->
<!--            (this.selectedStatus === 'failed' && result.IsComply === 'false') ||-->
<!--            (this.selectedStatus === 'pending' && result.IsComply === 'pending');-->
<!--        const matchesSearch = !this.searchTerm ||-->
<!--            result.description.toLowerCase().includes(this.searchTerm.toLowerCase());-->
<!--        return matchesStatus && matchesSearch;-->
<!--      });-->
<!--    },-->
<!--    passedCount() {-->
<!--      return this.checkresults.filter(item => item.IsComply === 'true').length;-->
<!--    },-->
<!--    failedCount() {-->
<!--      return this.checkresults.filter(item => item.IsComply === 'false').length;-->
<!--    },-->
<!--    pendingCount() {-->
<!--      return this.checkresults.filter(item => item.IsComply === 'pending').length;-->
<!--    },-->
<!--    totalCount() {-->
<!--      return this.checkresults.length;-->
<!--    }-->

<!--  },-->
<!--  methods: {-->

<!--    // 切换到W/L系统-->
<!--    changeOS() {-->
<!--      this.isWindows = !this.isWindows;-->
<!--      if (this.isWindows) {-->
<!--        if (this.message.Event_result) {-->
<!--          this.checkresults = this.message.Event_result-->
<!--          this.serverInfo = this.message.ServerInfo-->
<!--        }-->
<!--      } else {-->
<!--        this.checkresults = []-->
<!--        this.serverInfo = []-->
<!--      }-->
<!--    },-->


<!--    // 获取活跃IP列表-->
<!--    fetchAliveHosts() {-->
<!--      axios.get('/api/getAliveHosts')-->
<!--          .then(response => {-->
<!--            this.aliveHosts = response.data.alive_hosts;-->
<!--            // 如果有IP，默认选择第一个-->
<!--            if (this.aliveHosts && this.aliveHosts.length > 0) {-->
<!--              this.selectedIP = this.aliveHosts[0];-->
<!--              this.fetchAndDisplayChenckResults();-->
<!--            }-->
<!--          })-->
<!--          .catch(error => {-->
<!--            if (!this.isWindows) {-->
<!--              console.error('获取活跃IP列表失败:', error);-->
<!--              this.$message.error('获取活跃IP列表失败');-->
<!--            }-->
<!--          });-->
<!--    },-->

<!--    // 切换服务器-->
<!--    changeServer() {-->
<!--      if (this.selectedIP) {-->
<!--        this.fetchAndDisplayChenckResults();-->
<!--      }-->
<!--    },-->

<!--    // 修改后的获取检测结果函数-->
<!--    fetchAndDisplayChenckResults() {-->
<!--      if (!this.selectedIP) {-->
<!--        this.$message.warning('请先选择服务器IP');-->
<!--        return;-->
<!--      }-->

<!--      this.tableLoading = true;-->
<!--      axios.get(`/api/userinfo?ip=${this.selectedIP}`)-->
<!--          .then(response => {-->
<!--            // this.checkresults = response.data.Event_result;-->
<!--            this.checkresults = response.data.checkResults;-->
<!--            this.serverInfo = response.data.serverInfo;-->
<!--            this.tableLoading = false;-->
<!--            // 根据数据量预估页数-->
<!--            this.estimatePageCount();-->
<!--          })-->
<!--          .catch(error => {-->
<!--            console.error('Error:', error);-->
<!--            this.tableLoading = false;-->
<!--            this.$message.error('获取检测结果失败，请重试');-->
<!--          });-->
<!--    },-->

<!--    estimatePageCount() {-->
<!--      // 粗略估算页数：第一页为封面，剩余按每页约10条记录计算-->
<!--      const recordsPerPage = 10;-->
<!--      this.totalPages = Math.ceil(this.checkresults.length / recordsPerPage) + 1;-->
<!--    },-->

<!--    onExportToPDF() {-->
<!--      this.pdfLoading = true;-->
<!--      this.showContentForPDF = true;-->

<!--      this.$message({-->
<!--        message: '正在生成PDF，请稍候...',-->
<!--        type: 'info',-->
<!--        duration: 5000-->
<!--      });-->

<!--      // 延迟执行，确保DOM已完全渲染-->
<!--      setTimeout(() => {-->
<!--        // 创建PDF对象-->
<!--        const pdf = new jsPDF({-->
<!--          orientation: 'p',-->
<!--          unit: 'mm',-->
<!--          format: 'a4'-->
<!--        });-->

<!--        // 关键点：采用两遍渲染策略-->
<!--        // 第一遍：只渲染，不保存，仅记录最终页码-->
<!--        // 第二遍：用记录的正确页码重新渲染并保存-->

<!--        // 第一阶段：模拟渲染，计算总页数-->
<!--        this.simulatePdfRendering(pdf).then(actualPageCount => {-->
<!--          // 保存实际总页数-->
<!--          this.totalPages = actualPageCount;-->
<!--          console.log('确定的总页数:', this.totalPages);-->

<!--          // 第二阶段：使用确定的总页数重新生成PDF-->
<!--          this.renderFinalPdf(pdf, this.totalPages);-->
<!--        }).catch(err => {-->
<!--          console.error('PDF生成过程出错:', err);-->
<!--          this.pdfLoading = false;-->
<!--          this.showContentForPDF = false;-->
<!--          this.$message.error('PDF生成失败，请重试！');-->
<!--        });-->
<!--      }, 1000);-->
<!--    },-->

<!--    // 模拟渲染，确定实际总页数-->
<!--    async simulatePdfRendering(pdf) {-->
<!--      try {-->
<!--        // 保存PDF状态-->
<!--        const originalPage = pdf.internal.getCurrentPageInfo().pageNumber;-->

<!--        let pageCount = 0;-->

<!--        // 模拟渲染封面页-->
<!--        const coverPage = this.$el.querySelector('.pdf-content .server1');-->
<!--        await html2canvas(coverPage, { scale: 2, useCORS: true });-->
<!--        pageCount = 1;  // 封面算第一页-->

<!--        // 模拟渲染内容页-->
<!--        pdf.addPage();-->
<!--        pageCount++;-->

<!--        // 页面参数-->
<!--        const pageHeight = pdf.internal.pageSize.getHeight() - 20;-->

<!--        // 模拟渲染标题-->
<!--        const titleElement = this.$el.querySelector('.pdf-content .report-content-title');-->
<!--        const titleCanvas = await html2canvas(titleElement, { scale: 2, useCORS: true });-->
<!--        const titleWidth = 190;-->
<!--        const titleHeight = titleCanvas.height * titleWidth / titleCanvas.width;-->

<!--        let yPosition = 10 + titleHeight + 5;-->

<!--        // 模拟渲染表头-->
<!--        const headerElement = this.$el.querySelector('.pdf-content .el-table__header-wrapper');-->
<!--        const headerCanvas = await html2canvas(headerElement, { scale: 2, useCORS: true });-->
<!--        const headerWidth = 190;-->
<!--        const headerHeight = headerCanvas.height * headerWidth / headerCanvas.width;-->

<!--        yPosition += headerHeight + 2;-->

<!--        // 模拟渲染每一行并计算页码-->
<!--        const tableRows = this.$el.querySelectorAll('.pdf-content .el-table__body-wrapper table tr');-->

<!--        for (let i = 0; i < tableRows.length; i++) {-->
<!--          const row = tableRows[i];-->
<!--          const rowCanvas = await html2canvas(row, { scale: 2, useCORS: true });-->
<!--          const rowWidth = 190;-->
<!--          const rowHeight = rowCanvas.height * rowWidth / rowCanvas.width;-->

<!--          // 如果当前行放不下，需要新页面-->
<!--          if (yPosition + rowHeight > pageHeight) {-->
<!--            // 新页面-->
<!--            if (i < tableRows.length - 1) { // 不是最后一行才需要新页面-->
<!--              pdf.addPage();-->
<!--              pageCount++;-->
<!--              yPosition = 10; // 重置Y位置-->
<!--            }-->
<!--          }-->

<!--          yPosition += rowHeight + 2;-->
<!--        }-->

<!--        // 恢复PDF状态-->
<!--        while (pdf.internal.getCurrentPageInfo().pageNumber > originalPage) {-->
<!--          pdf.deletePage(pdf.internal.getCurrentPageInfo().pageNumber);-->
<!--        }-->

<!--        return pageCount;-->
<!--      } catch (error) {-->
<!--        console.error('模拟渲染计算页数出错:', error);-->
<!--        throw error;-->
<!--      }-->
<!--    },-->

<!--    // 使用正确页码渲染最终PDF-->
<!--    async renderFinalPdf(pdf, totalPageCount) {-->
<!--      try {-->
<!--        // 渲染封面页-->
<!--        const coverPage = this.$el.querySelector('.pdf-content .server1');-->
<!--        const coverCanvas = await html2canvas(coverPage, { scale: 2, useCORS: true });-->
<!--        const imgData = coverCanvas.toDataURL('image/jpeg', 0.8);-->
<!--        const imgWidth = 190;-->
<!--        const imgHeight = coverCanvas.height * imgWidth / coverCanvas.width;-->

<!--        pdf.addImage(imgData, 'JPEG', 10, 10, imgWidth, imgHeight);-->

<!--        // 封面页页码-->
<!--        pdf.setFontSize(10);-->
<!--        pdf.text(`1/${totalPageCount}`, pdf.internal.pageSize.getWidth() - 25, pdf.internal.pageSize.getHeight() - 10);-->

<!--        // 添加内容页-->
<!--        pdf.addPage();-->

<!--        // 页面参数-->
<!--        const pageHeight = pdf.internal.pageSize.getHeight() - 20;-->
<!--        let currentPageNum = 2; // 从第二页开始-->

<!--        // 添加标题-->
<!--        const titleElement = this.$el.querySelector('.pdf-content .report-content-title');-->
<!--        const titleCanvas = await html2canvas(titleElement, { scale: 2, useCORS: true });-->
<!--        const titleImgData = titleCanvas.toDataURL('image/jpeg', 0.8);-->
<!--        const titleWidth = 190;-->
<!--        const titleHeight = titleCanvas.height * titleWidth / titleCanvas.width;-->

<!--        pdf.addImage(titleImgData, 'JPEG', 10, 10, titleWidth, titleHeight);-->
<!--        let yPosition = 10 + titleHeight + 5;-->

<!--        // 添加表头-->
<!--        const headerElement = this.$el.querySelector('.pdf-content .el-table__header-wrapper');-->
<!--        const headerCanvas = await html2canvas(headerElement, { scale: 2, useCORS: true });-->
<!--        const headerImgData = headerCanvas.toDataURL('image/jpeg', 0.8);-->
<!--        const headerWidth = 190;-->
<!--        const headerHeight = headerCanvas.height * headerWidth / headerCanvas.width;-->

<!--        pdf.addImage(headerImgData, 'JPEG', 10, yPosition, headerWidth, headerHeight);-->
<!--        yPosition += headerHeight + 2;-->

<!--        // 逐行添加表格内容-->
<!--        const tableRows = this.$el.querySelectorAll('.pdf-content .el-table__body-wrapper table tr');-->

<!--        for (let i = 0; i < tableRows.length; i++) {-->
<!--          const row = tableRows[i];-->
<!--          const rowCanvas = await html2canvas(row, { scale: 2, useCORS: true });-->
<!--          const rowImgData = rowCanvas.toDataURL('image/jpeg', 0.8);-->
<!--          const rowWidth = 190;-->
<!--          const rowHeight = rowCanvas.height * rowWidth / rowCanvas.width;-->

<!--          // 检查是否需要换页-->
<!--          if (yPosition + rowHeight > pageHeight) {-->
<!--            // 添加当前页码-->
<!--            pdf.setFontSize(10);-->
<!--            pdf.text(`${currentPageNum}/${totalPageCount}`, pdf.internal.pageSize.getWidth() - 25, pdf.internal.pageSize.getHeight() - 10);-->

<!--            // 不是最后一行才需要新页面-->
<!--            if (i < tableRows.length - 1) {-->
<!--              // 新页面-->
<!--              pdf.addPage();-->
<!--              currentPageNum++;-->
<!--              yPosition = 10;-->
<!--            }-->
<!--          }-->

<!--          // 添加当前行-->
<!--          pdf.addImage(rowImgData, 'JPEG', 10, yPosition, rowWidth, rowHeight);-->
<!--          yPosition += rowHeight + 2;-->
<!--        }-->

<!--        // 最后一页页码-->
<!--        pdf.setFontSize(10);-->
<!--        pdf.text(`${currentPageNum}/${totalPageCount}`, pdf.internal.pageSize.getWidth() - 25, pdf.internal.pageSize.getHeight() - 10);-->

<!--        // 保存PDF-->
<!--        const filename = `Linux基线检测报告_${this.selectedIP}_${new Date().toISOString().slice(0, 10)}.pdf`;-->
<!--        pdf.save(filename);-->

<!--        // 清理和完成-->
<!--        this.showContentForPDF = false;-->
<!--        this.pdfLoading = false;-->
<!--        this.$message.success('PDF报告导出成功！');-->

<!--      } catch (err) {-->
<!--        console.error('生成PDF时出错:', err);-->
<!--        this.pdfLoading = false;-->
<!--        this.showContentForPDF = false;-->
<!--        this.$message.error('PDF生成失败，请重试！');-->
<!--      }-->
<!--    },-->

<!--    filterSearchResults() {-->
<!--      // 通过计算属性自动过滤，此方法保留用于可能的扩展-->
<!--    },-->

<!--    goToClassifyProtect() {-->
<!--      // 导航到等保测评页面-->
<!--      this.$router.push('/classifyProtect');-->
<!--    },-->
<!--    // 获取状态对应的类型（用于el-tag的type属性）-->
<!--    getStatusType(status) {-->
<!--      switch (status) {-->
<!--        case 'true': return 'success';-->
<!--        case 'false': return 'danger';-->
<!--        case 'pending': return 'warning';-->
<!--        default: return 'info';-->
<!--      }-->
<!--    },-->

<!--    // 获取状态对应的文本-->
<!--    getStatusText(status) {-->
<!--      switch (status) {-->
<!--        case 'true': return '通过';-->
<!--        case 'false': return '未通过';-->
<!--        case 'pending': return '待检查';-->
<!--        default: return '未知';-->
<!--      }-->
<!--    },-->

<!--    // 获取PDF中状态对应的CSS类-->
<!--    getStatusClass(status) {-->
<!--      return {-->
<!--        'failed-result': status === 'false',-->
<!--        'pending-result': status === 'pending'-->
<!--      };-->
<!--    },-->


<!--  },-->
<!--  mounted() {-->
<!--    // 先获取活跃IP列表，然后会自动选择第一个IP并获取检测结果-->
<!--    this.fetchAliveHosts();-->
<!--    if (this.message.Event_result && !this.isWindows) {-->
<!--      this.changeOS()-->
<!--    }-->
<!--  }-->
<!--}-->
<!--</script>-->

<!--<style scoped>-->
<!--.baseline-container {-->
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

<!--.control-section {-->
<!--  display: flex;-->
<!--  justify-content: space-between;-->
<!--  align-items: center;-->
<!--  margin-bottom: 20px;-->
<!--  flex-wrap: wrap;-->
<!--  gap: 15px;-->
<!--}-->

<!--.button-group {-->
<!--  display: flex;-->
<!--  gap: 10px;-->
<!--}-->

<!--.control-item {-->
<!--  margin-right: 10px;-->
<!--}-->

<!--.filter-group {-->
<!--  display: flex;-->
<!--  gap: 10px;-->
<!--}-->

<!--.filter-group .el-input {-->
<!--  width: 250px;-->
<!--}-->

<!--.server-info-card {-->
<!--  margin-bottom: 20px;-->
<!--  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);-->
<!--}-->

<!--.card-header {-->
<!--  font-size: 16px;-->
<!--  font-weight: bold;-->
<!--  display: flex;-->
<!--  justify-content: space-between;-->
<!--  align-items: center;-->
<!--}-->

<!--.summary {-->
<!--  display: flex;-->
<!--  gap: 10px;-->
<!--}-->

<!--.info-item {-->
<!--  padding: 8px 0;-->
<!--  border-bottom: 1px solid #ebeef5;-->
<!--}-->

<!--.info-label {-->
<!--  font-weight: bold;-->
<!--  color: #606266;-->
<!--}-->

<!--.results-card {-->
<!--  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);-->
<!--}-->

<!--/* PDF内容样式 */-->
<!--.pdf-content {-->
<!--  font-size: 10pt;-->
<!--  max-width: 297mm;-->
<!--  padding: 15mm;-->
<!--  box-sizing: border-box;-->
<!--}-->

<!--#linuxBaseline2 {-->
<!--  font-size: 24pt;-->
<!--  color: #141010e1;-->
<!--  text-align: center;-->
<!--  margin-top: 20px;-->
<!--}-->

<!--.server1 .el-col p {-->
<!--  font-size: 16px;-->
<!--  white-space: pre-wrap;-->
<!--  line-height: 1.6;-->
<!--  margin-bottom: 5px;-->
<!--}-->

<!--.failed-result {-->
<!--  color: #f56c6c;-->
<!--}-->

<!--.pending-result {-->
<!--  color: #e6a23c;-->
<!--}-->


<!--.page-number {-->
<!--  position: absolute;-->
<!--  bottom: 10mm;-->
<!--  right: 10mm;-->
<!--  font-size: 12px;-->
<!--}-->

<!--.report-content-title {-->
<!--  margin-top: 20px;-->
<!--  margin-bottom: 15px;-->
<!--  text-align: center;-->
<!--}-->

<!--.report-content-title h2 {-->
<!--  font-size: 18pt;-->
<!--  color: #303133;-->
<!--  margin: 0;-->
<!--}-->

<!--@media (max-width: 768px) {-->
<!--  .control-section {-->
<!--    flex-direction: column;-->
<!--    align-items: flex-start;-->
<!--  }-->

<!--  .filter-group {-->
<!--    width: 100%;-->
<!--  }-->

<!--  .filter-group .el-input {-->
<!--    width: 100%;-->
<!--  }-->
<!--}-->
<!--</style>-->
