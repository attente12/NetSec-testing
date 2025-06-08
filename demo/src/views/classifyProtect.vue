<template>
  <div class="baseline-container">
    <!-- 头部区域 -->
    <div class="header-section">
      <el-button
          @click="goBackToTest"
          type="primary"
          icon="el-icon-back"
          size="medium">
        返回
      </el-button>
      <h1 class="main-title">等级保护测评</h1>
      <div class="date-info">
        <!--        <el-tag type="info">检测时间：{{ new Date().toLocaleString() }}</el-tag>-->
      </div>
    </div>

    <!-- 控制按钮区域 -->
    <div class="control-section">
      <div class="button-group">
        <div class="control-item">
          <el-tag type="primary" size="medium">
            当前IP: {{ selectedIP }}
          </el-tag>
        </div>
      </div>

      <div class="filter-group">
        <el-select
            v-model="selectedStatus"
            placeholder="请选择状态"
            size="medium">
          <el-option label="全部" value="all"></el-option>
          <el-option label="通过" value="passed"></el-option>
          <el-option label="未通过" value="failed"></el-option>
          <el-option label="待检查" value="pending"></el-option>
        </el-select>

        <el-input
            placeholder="输入检测项关键字..."
            v-model="searchTerm"
            @input="filterSearchResults"
            prefix-icon="el-icon-search"
            size="medium">
        </el-input>
      </div>

      <!-- 修改保存评分按钮 -->
      <el-button
          type="success"
          icon="el-icon-check"
          @click="saveScores"
          :loading="saveLoading"
          :disabled="!canSave"
          size="medium">
        保存人工判定结果
      </el-button>
      <el-button
          type="primary"
          icon="el-icon-data-analysis"
          @click="getProtectionLevelResult"
          :loading="resultLoading"
          size="medium">
        获取等保结果
      </el-button>
    </div>

    <!-- 人工判定提醒 -->
    <el-alert
        v-if="unfinishedPendingCount > 0"
        title=""
        type="warning"
        effect="dark"
        show-icon
        :closable="false"
        class="manual-review-alert">
<!--      <template slot="title">-->
<!--        <i class="el-icon-warning-outline"></i>-->
<!--        <strong>重要提醒：请完成人工判定</strong>-->
<!--      </template>-->
      <div class="alert-content">
        <p>检测到 <strong class="highlight-number">{{ unfinishedPendingCount }}</strong> 个项目需要进行人工判定，请仔细评估每个项目是否符合等保要求。</p>
        <p>👉 只有完成所有人工判定后才能保存结果</p>
      </div>
    </el-alert>

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
          <el-tag type="warning">待检查: {{ pendingCount }}</el-tag>
          <el-tag type="info">总计: {{ totalCount }}</el-tag>
          <el-tag v-if="unfinishedPendingCount > 0" type="warning" effect="plain">
            待人工判定: {{ unfinishedPendingCount }}
          </el-tag>
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
        <el-table-column label="重要程度" width="120">
          <template slot-scope="scope">
            <el-select
                v-model="scope.row.importantLevel"
                placeholder="请选择重要程度"
                size="mini">
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
            <el-tag :type="getStatusType(scope.row.IsComply)">
              {{ getStatusText(scope.row.IsComply) }}
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
            <el-select
                v-model="scope.row.score"
                :placeholder="scope.row.IsComply === 'pending' ? '请选择' : '请选择评分'"
                size="mini"
                @change="onScoreChange(scope.row)"
                :class="{ 'pending-select': scope.row.IsComply === 'pending' && !scope.row.score }">
              <el-option label="符合" value="1"></el-option>
              <el-option label="部分符合" value="0.5"></el-option>
              <el-option label="不符合" value="0"></el-option>
            </el-select>
            <div v-if="scope.row.IsComply === 'pending' && !scope.row.score"
                 style="font-size: 10px; color: #E6A23C; margin-top: 2px;">
              需人工判定
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="check_time" label="检测时间" min-width="150"></el-table-column>
      </el-table>
    </el-card>

    <!-- PDF内容（隐藏） -->
    <div class="pdf-content" v-show="showContentForPDF">
      <!-- 测试正文标题 -->
      <div class="report-content-title">
        <h2>等级保护测评报告</h2>
      </div>

      <el-table :data="filteredCheckresults" style="width: 100%">
        <el-table-column label="序号" width="70" type="index"></el-table-column>
        <el-table-column prop="description" label="检测项"></el-table-column>
        <el-table-column label="重要程度" width="80">
          <template slot-scope="scope">
            <span
                :style="{
                color:
                  scope.row.importantLevel == '3'
                    ? 'red'
                    : scope.row.importantLevel == '2'
                    ? 'orange'
                    : 'green'
              }"
            >
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
            <span
                :style="{
                color:
                  scope.row.score == 1
                    ? 'green'
                    : scope.row.score == 0.5
                    ? 'orange'
                    : 'red'
              }"
            >
              {{
                scope.row.score == 1
                    ? '符合'
                    : scope.row.score == 0.5
                        ? '部分符合'
                        : '不符合'
              }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="check_time" label="检测时间" min-width="150"></el-table-column>

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
      selectedIP: '', // 选中的IP
      saveLoading: false, // 保存按钮的加载状态
      // 等保评分相关计算属性
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
            (this.selectedStatus === 'failed' && result.IsComply === 'false') ||
            (this.selectedStatus === 'pending' && result.IsComply === 'pending');
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
    pendingCount() {
      return this.checkresults.filter(item => item.IsComply === 'pending').length;
    },
    totalCount() {
      return this.checkresults.length;
    },

    // 新增：检查是否所有pending项都已选择
    canSave() {
      const pendingItems = this.checkresults.filter(item => item.IsComply === 'pending');
      return pendingItems.every(item => item.score && item.score !== '');
    },

    // 新增：获取未完成选择的pending项数量
    unfinishedPendingCount() {
      const pendingItems = this.checkresults.filter(item => item.IsComply === 'pending');
      return pendingItems.filter(item => !item.score || item.score === '').length;
    },

    formattedScore() {
      return this.levelResult.score ? this.levelResult.score.toFixed(2) : '0.00';
    }
  },
  methods: {
    goBackToTest() {
      this.$router.push('/assetManage');
    },

    // 新增：选择变化监听方法
    onScoreChange() {
      // 当用户改变选择时，强制更新视图以重新计算canSave
      this.$forceUpdate();
    },

    // 修改后的获取检测结果函数
    fetchAndDisplayChenckResults() {
      this.tableLoading = true;
      axios.get(`/api/level3Userinfo?ip=${this.selectedIP}`)
          .then(response => {
            this.checkresults = response.data.checkResults.map(item => {
              // 根据 tmp_IsComply 的值来设置 score
              let score = '';

              // 根据不同状态设置初始score值
              if (item.tmp_IsComply === 'true') {
                score = '1';
              } else if (item.tmp_IsComply === 'half_true') {
                score = '0.5';
              } else if (item.tmp_IsComply === 'false') {
                score = '0';
              } else if (item.tmp_IsComply === 'pending') {
                score = ''; // pending状态默认为空，需要用户选择
              }

              return {
                ...item,
                score: score,
                importantLevel: item.tmp_importantLevel || '2'
              };
            });
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

    // 获取状态对应的类型（用于el-tag的type属性）
    getStatusType(status) {
      switch (status) {
        case 'true': return 'success';
        case 'false': return 'danger';
        case 'pending': return 'warning';
        default: return 'info';
      }
    },

    // 获取状态对应的文本
    getStatusText(status) {
      switch (status) {
        case 'true': return '通过';
        case 'false': return '未通过';
        case 'pending': return '待检查';
        default: return '未知';
      }
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
    },

    saveScores() {
      // 验证pending项是否都已选择
      if (!this.canSave) {
        this.$message.warning(`还有 ${this.unfinishedPendingCount} 个待检查项目需要人工判定，请完成后再保存`);
        return;
      }

      // 显示保存中状态
      this.saveLoading = true;

      // 准备请求数据
      const scoreMeasures = this.checkresults.map(item => ({
        item_id: item.item_id,
        importantLevelJson: item.importantLevel, // 如果有importantLevel字段则使用，否则默认为"2"
        IsComplyLevel: item.score // 使用选择的评分值
      }));

      // 构建请求体
      const requestData = {
        ip: this.selectedIP,
        scoreMeasures: scoreMeasures
      };

      // 发送POST请求
      axios.post('/api/updateLevel3Protect', requestData)
          .then(response => {
            // 保存成功
            this.saveLoading = false;
            this.$message.success(`成功更新${response.data.itemsUpdated}项评分结果`);
          })
          .catch(error => {
            // 保存失败
            this.saveLoading = false;
            console.error('保存评分失败:', error);
            this.$message.error('保存评分失败，请重试');
          });
    },
    // 获取等保评分
    getProtectionLevelResult() {
      this.resultLoading = true;
      axios.get(`/api/getlevel3ResultByIp?ip=${this.selectedIP}`)
          .then(response => {
            this.levelResult = response.data;
            this.showScoreResult = true;
            this.resultLoading = false;

            // 根据得分显示对应的消息提示
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
    // 从路由参数获取IP
    const routeIP = this.$route.query.ip;

    if (routeIP) {
      this.selectedIP = routeIP;
      this.fetchAndDisplayChenckResults();
    } else {
      this.$message.error('缺少IP参数，请从正确的入口访问此页面');
    }
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

/* 人工判定提醒样式 */
.manual-review-alert {
  margin-bottom: 20px;
  border-left: 4px solid #E6A23C;
  background: linear-gradient(135deg, #fdf6ec 0%, #fef7ed 100%);
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(230, 162, 60, 0.2);
}

.manual-review-alert .el-alert__title {
  font-size: 16px;
  font-weight: bold;
  color: #B8860B;
}

.alert-content {
  margin-top: 8px;
}

.alert-content p {
  margin: 5px 0;
  color: #8B4513;
  font-size: 14px;
  line-height: 1.5;
}

.highlight-number {
  color: #E6A23C;
  font-size: 18px;
  font-weight: bold;
  background: #fff;
  padding: 2px 6px;
  border-radius: 4px;
  border: 1px solid #E6A23C;
}

/* pending状态的下拉框样式 */
.pending-select {
  border: 1px solid #E6A23C !important;
  background-color: #fdf6ec !important;
}

.pending-select .el-input__inner {
  border-color: #E6A23C !important;
  background-color: #fdf6ec !important;
}

/* 禁用按钮样式 */
.el-button:disabled {
  background-color: #f5f7fa !important;
  border-color: #e4e7ed !important;
  color: #c0c4cc !important;
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
.score-excellent, .excellent-text {
  color: #67c23a;
}

.score-good, .good-text {
  color: #409eff;
}

.score-moderate, .warning-text {
  color: #e6a23c;
}

.score-poor, .danger-text {
  color: #f56c6c;
}

.excellent-text, .good-text, .warning-text, .danger-text {
  font-weight: bold;
}
</style>

<!--<template>-->
<!--  <div class="baseline-container">-->
<!--    &lt;!&ndash; 头部区域 &ndash;&gt;-->
<!--    <div class="header-section">-->
<!--      <el-button-->
<!--          @click="goBackToTest"-->
<!--          type="primary"-->
<!--          icon="el-icon-back"-->
<!--          size="medium">-->
<!--        返回-->
<!--      </el-button>-->
<!--      <h1 class="main-title">等级保护测评</h1>-->
<!--      <div class="date-info">-->
<!--&lt;!&ndash;        <el-tag type="info">检测时间：{{ new Date().toLocaleString() }}</el-tag>&ndash;&gt;-->
<!--      </div>-->
<!--    </div>-->

<!--    &lt;!&ndash; 控制按钮区域 &ndash;&gt;-->
<!--    <div class="control-section">-->
<!--      <div class="button-group">-->
<!--        &lt;!&ndash; 新增的IP选择下拉框 &ndash;&gt;-->
<!--&lt;!&ndash;        <div class="control-item">&ndash;&gt;-->
<!--&lt;!&ndash;          <el-select&ndash;&gt;-->
<!--&lt;!&ndash;              v-model="selectedIP"&ndash;&gt;-->
<!--&lt;!&ndash;              placeholder="选择服务器IP"&ndash;&gt;-->
<!--&lt;!&ndash;              @change="changeServer"&ndash;&gt;-->
<!--&lt;!&ndash;              size="medium">&ndash;&gt;-->
<!--&lt;!&ndash;            <el-option&ndash;&gt;-->
<!--&lt;!&ndash;                v-for="ip in aliveHosts"&ndash;&gt;-->
<!--&lt;!&ndash;                :key="ip"&ndash;&gt;-->
<!--&lt;!&ndash;                :label="ip"&ndash;&gt;-->
<!--&lt;!&ndash;                :value="ip">&ndash;&gt;-->
<!--&lt;!&ndash;            </el-option>&ndash;&gt;-->
<!--&lt;!&ndash;          </el-select>&ndash;&gt;-->
<!--&lt;!&ndash;        </div>&ndash;&gt;-->
<!--        <div class="control-item">-->
<!--          <el-tag type="primary" size="medium">-->
<!--            当前IP: {{ selectedIP }}-->
<!--          </el-tag>-->
<!--        </div>-->

<!--&lt;!&ndash;        <el-button&ndash;&gt;-->

<!--&lt;!&ndash;            @click="onExportToPDF"&ndash;&gt;-->
<!--&lt;!&ndash;            :loading="pdfLoading"&ndash;&gt;-->
<!--&lt;!&ndash;            icon="el-icon-document"&ndash;&gt;-->
<!--&lt;!&ndash;            type="primary"&ndash;&gt;-->
<!--&lt;!&ndash;            size="medium">&ndash;&gt;-->
<!--&lt;!&ndash;          导出为 PDF&ndash;&gt;-->
<!--&lt;!&ndash;        </el-button>&ndash;&gt;-->
<!--      </div>-->

<!--      <div class="filter-group">-->
<!--        <el-select-->
<!--            v-model="selectedStatus"-->
<!--            placeholder="请选择状态"-->
<!--            size="medium">-->
<!--          <el-option label="全部" value="all"></el-option>-->
<!--          <el-option label="通过" value="passed"></el-option>-->
<!--          <el-option label="未通过" value="failed"></el-option>-->
<!--          <el-option label="待检查" value="pending"></el-option>-->
<!--        </el-select>-->

<!--        <el-input-->
<!--            placeholder="输入检测项关键字..."-->
<!--            v-model="searchTerm"-->
<!--            @input="filterSearchResults"-->
<!--            prefix-icon="el-icon-search"-->
<!--            size="medium">-->
<!--        </el-input>-->
<!--      </div>-->

<!--      &lt;!&ndash; 新增保存评分按钮 &ndash;&gt;-->
<!--      <el-button-->
<!--          type="success"-->
<!--          icon="el-icon-check"-->
<!--          @click="saveScores"-->
<!--          :loading="saveLoading"-->
<!--          size="medium">-->
<!--        保存人工判定结果-->
<!--      </el-button>-->
<!--      <el-button-->
<!--          type="primary"-->
<!--          icon="el-icon-data-analysis"-->
<!--          @click="getProtectionLevelResult"-->
<!--          :loading="resultLoading"-->
<!--          size="medium">-->
<!--        获取等保结果-->
<!--      </el-button>-->
<!--    </div>-->

<!--    &lt;!&ndash; 得分显示部分，数字得分 &ndash;&gt;-->
<!--    <el-card class="score-card" v-if="showScoreResult" style="margin-bottom: 20px">-->
<!--      <div slot="header" class="card-header">-->
<!--        <span><i class="el-icon-data-line"></i> 等保测评结果</span>-->
<!--        <el-button type="text" @click="showScoreResult = false">-->
<!--          <i class="el-icon-close"></i>-->
<!--        </el-button>-->
<!--      </div>-->

<!--      <div class="score-content">-->
<!--        &lt;!&ndash; 替换仪表盘为简单的得分显示 &ndash;&gt;-->
<!--        <div class="score-display">-->
<!--          <div class="score-title">等保得分</div>-->
<!--          <div class="score-number" :class="getScoreClass(levelResult.score)">-->
<!--            {{ formattedScore }}-->
<!--          </div>-->
<!--        </div>-->

<!--        <div class="score-details">-->
<!--          <div class="detail-item">-->
<!--            <span class="detail-label">IP地址:</span>-->
<!--            <span class="detail-value">{{ levelResult.ip || selectedIP }}</span>-->
<!--          </div>-->
<!--          <div class="detail-item">-->
<!--            <span class="detail-label">等保级别:</span>-->
<!--            <span class="detail-value">三级</span>-->
<!--          </div>-->
<!--          <div class="detail-item">-->
<!--            <span class="detail-label">评估结论:</span>-->
<!--            <span class="detail-value" :class="getScoreClass(levelResult.score)">-->
<!--          {{ getScoreConclusion(levelResult.score) }}-->
<!--        </span>-->
<!--          </div>-->
<!--          <div class="detail-item">-->
<!--            <span class="detail-label">检测项总数:</span>-->
<!--            <span class="detail-value">{{ levelResult.totalItems || '0' }}</span>-->
<!--          </div>-->
<!--        </div>-->
<!--      </div>-->

<!--      <div class="score-summary">-->
<!--        <div class="summary-text">-->
<!--          <p>{{ levelResult.message || '三级等保评估结果' }}</p>-->

<!--          &lt;!&ndash; 根据不同分数区间显示不同的提示信息 &ndash;&gt;-->
<!--          <p v-if="levelResult.score >= 90" class="excellent-text">-->
<!--            <i class="el-icon-circle-check"></i>-->
<!--            得分优秀，符合等保三级要求，建议持续保持-->
<!--          </p>-->
<!--          <p v-else-if="levelResult.score >= 80" class="good-text">-->
<!--            <i class="el-icon-circle-check"></i>-->
<!--            得分良好，基本符合等保三级要求，可进一步完善个别项目-->
<!--          </p>-->
<!--          <p v-else-if="levelResult.score >= 60" class="warning-text">-->
<!--            <i class="el-icon-warning"></i>-->
<!--            得分基本合格，仍有提升空间，建议优化未完全符合的检测项-->
<!--          </p>-->
<!--          <p v-else class="danger-text">-->
<!--            <i class="el-icon-close"></i>-->
<!--            得分未达标，建议查看未通过检测项并根据建议进行整改-->
<!--          </p>-->
<!--        </div>-->
<!--      </div>-->
<!--    </el-card>-->
<!--&lt;!&ndash;    <el-card class="score-card" v-if="showScoreResult" style="margin-bottom: 30px">&ndash;&gt;-->
<!--&lt;!&ndash;      <div slot="header" class="card-header">&ndash;&gt;-->
<!--&lt;!&ndash;        <span><i class="el-icon-data-line"></i> 等保测评结果</span>&ndash;&gt;-->
<!--&lt;!&ndash;        <el-button type="text" @click="showScoreResult = false">&ndash;&gt;-->
<!--&lt;!&ndash;          <i class="el-icon-close"></i>&ndash;&gt;-->
<!--&lt;!&ndash;        </el-button>&ndash;&gt;-->
<!--&lt;!&ndash;      </div>&ndash;&gt;-->

<!--&lt;!&ndash;      <div class="score-content">&ndash;&gt;-->
<!--&lt;!&ndash;        <div class="score-gauge">&ndash;&gt;-->
<!--&lt;!&ndash;          <el-progress type="dashboard" :percentage="scorePercentage" :color="scoreColors" :stroke-width="12">&ndash;&gt;-->
<!--&lt;!&ndash;            <div class="score-value">{{ formattedScore }}</div>&ndash;&gt;-->
<!--&lt;!&ndash;          </el-progress>&ndash;&gt;-->
<!--&lt;!&ndash;        </div>&ndash;&gt;-->

<!--&lt;!&ndash;        <div class="score-details">&ndash;&gt;-->
<!--&lt;!&ndash;          <div class="detail-item">&ndash;&gt;-->
<!--&lt;!&ndash;            <span class="detail-label">IP地址:</span>&ndash;&gt;-->
<!--&lt;!&ndash;            <span class="detail-value">{{ levelResult.ip || selectedIP }}</span>&ndash;&gt;-->
<!--&lt;!&ndash;          </div>&ndash;&gt;-->
<!--&lt;!&ndash;          <div class="detail-item">&ndash;&gt;-->
<!--&lt;!&ndash;            <span class="detail-label">等保级别:</span>&ndash;&gt;-->
<!--&lt;!&ndash;            <span class="detail-value">三级</span>&ndash;&gt;-->
<!--&lt;!&ndash;          </div>&ndash;&gt;-->
<!--&lt;!&ndash;          <div class="detail-item">&ndash;&gt;-->
<!--&lt;!&ndash;            <span class="detail-label">评估结论:</span>&ndash;&gt;-->
<!--&lt;!&ndash;            <span class="detail-value" :class="getScoreClass(levelResult.score)">&ndash;&gt;-->
<!--&lt;!&ndash;          {{ getScoreConclusion(levelResult.score) }}&ndash;&gt;-->
<!--&lt;!&ndash;        </span>&ndash;&gt;-->
<!--&lt;!&ndash;          </div>&ndash;&gt;-->
<!--&lt;!&ndash;          <div class="detail-item">&ndash;&gt;-->
<!--&lt;!&ndash;            <span class="detail-label">检测项总数:</span>&ndash;&gt;-->
<!--&lt;!&ndash;            <span class="detail-value">{{ levelResult.totalItems || '0' }}</span>&ndash;&gt;-->
<!--&lt;!&ndash;          </div>&ndash;&gt;-->
<!--&lt;!&ndash;        </div>&ndash;&gt;-->
<!--&lt;!&ndash;      </div>&ndash;&gt;-->

<!--&lt;!&ndash;      <div class="score-summary">&ndash;&gt;-->
<!--&lt;!&ndash;        <div class="summary-text">&ndash;&gt;-->
<!--&lt;!&ndash;          <p>{{ levelResult.message || '三级等保评估结果' }}</p>&ndash;&gt;-->

<!--&lt;!&ndash;          &lt;!&ndash; 根据不同分数区间显示不同的提示信息 &ndash;&gt;&ndash;&gt;-->
<!--&lt;!&ndash;          <p v-if="levelResult.score >= 90" class="excellent-text">&ndash;&gt;-->
<!--&lt;!&ndash;            <i class="el-icon-circle-check"></i>&ndash;&gt;-->
<!--&lt;!&ndash;            得分优秀，符合等保三级要求，建议持续保持&ndash;&gt;-->
<!--&lt;!&ndash;          </p>&ndash;&gt;-->
<!--&lt;!&ndash;          <p v-else-if="levelResult.score >= 80" class="good-text">&ndash;&gt;-->
<!--&lt;!&ndash;            <i class="el-icon-circle-check"></i>&ndash;&gt;-->
<!--&lt;!&ndash;            得分良好，基本符合等保三级要求，可进一步完善个别项目&ndash;&gt;-->
<!--&lt;!&ndash;          </p>&ndash;&gt;-->
<!--&lt;!&ndash;          <p v-else-if="levelResult.score >= 60" class="warning-text">&ndash;&gt;-->
<!--&lt;!&ndash;            <i class="el-icon-warning"></i>&ndash;&gt;-->
<!--&lt;!&ndash;            得分基本合格，仍有提升空间，建议优化未完全符合的检测项&ndash;&gt;-->
<!--&lt;!&ndash;          </p>&ndash;&gt;-->
<!--&lt;!&ndash;          <p v-else class="danger-text">&ndash;&gt;-->
<!--&lt;!&ndash;            <i class="el-icon-close"></i>&ndash;&gt;-->
<!--&lt;!&ndash;            得分未达标，建议查看未通过检测项并根据建议进行整改&ndash;&gt;-->
<!--&lt;!&ndash;          </p>&ndash;&gt;-->
<!--&lt;!&ndash;        </div>&ndash;&gt;-->
<!--&lt;!&ndash;      </div>&ndash;&gt;-->
<!--&lt;!&ndash;    </el-card>&ndash;&gt;-->


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

<!--      <el-table-->
<!--          :data="filteredCheckresults"-->
<!--          style="width: 100%"-->
<!--          border-->
<!--          stripe-->
<!--          :header-cell-style="{background:'#f5f7fa',color:'#606266'}"-->
<!--          v-loading="tableLoading">-->
<!--        <el-table-column label="序号" width="70" type="index"></el-table-column>-->
<!--        <el-table-column prop="description" label="检测项" min-width="150"></el-table-column>-->
<!--        <el-table-column label="重要程度" width="120">-->
<!--          <template slot-scope="scope">-->
<!--            <el-select-->
<!--                v-model="scope.row.importantLevel"-->
<!--                placeholder="请选择重要程度"-->
<!--                size="mini">-->
<!--              <el-option label="1" value="1"></el-option>-->
<!--              <el-option label="2" value="2"></el-option>-->
<!--              <el-option label="3" value="3"></el-option>-->
<!--            </el-select>-->
<!--          </template>-->
<!--        </el-table-column>-->
<!--        <el-table-column prop="basis" label="基准" min-width="150"></el-table-column>-->
<!--        <el-table-column prop="result" label="检测结果" min-width="150"></el-table-column>-->
<!--        <el-table-column label="是否通过检查" width="120">-->
<!--          <template slot-scope="scope">-->
<!--            <el-tag :type="getStatusType(scope.row.IsComply)">-->
<!--              {{ getStatusText(scope.row.IsComply) }}-->
<!--            </el-tag>-->
<!--          </template>-->
<!--        </el-table-column>-->
<!--&lt;!&ndash;        <el-table-column label="是否通过检查" width="120">&ndash;&gt;-->
<!--&lt;!&ndash;          <template slot-scope="scope">&ndash;&gt;-->
<!--&lt;!&ndash;            <el-tag :type="scope.row.IsComply === 'true' ? 'success' : 'danger'">&ndash;&gt;-->
<!--&lt;!&ndash;              {{ scope.row.IsComply === 'true' ? '通过' : '未通过' }}&ndash;&gt;-->
<!--&lt;!&ndash;            </el-tag>&ndash;&gt;-->
<!--&lt;!&ndash;          </template>&ndash;&gt;-->
<!--&lt;!&ndash;        </el-table-column>&ndash;&gt;-->
<!--        <el-table-column label="修改建议" min-width="250">-->
<!--          <template slot-scope="scope">-->
<!--            <span v-if="scope.row.IsComply === 'false'">{{ scope.row.recommend }}</span>-->
<!--            <span v-else>-</span>-->
<!--          </template>-->
<!--        </el-table-column>-->
<!--        <el-table-column label="是否符合等保要求（人工判定）" width="120">-->
<!--          <template slot-scope="scope">-->
<!--            <el-select-->
<!--                v-model="scope.row.score"-->
<!--                placeholder="请选择评分"-->
<!--                size="mini">-->
<!--              <el-option label="符合" value="1"></el-option>-->
<!--              <el-option label="部分符合" value="0.5"></el-option>-->
<!--              <el-option label="不符合" value="0"></el-option>-->
<!--            </el-select>-->
<!--          </template>-->
<!--        </el-table-column>-->
<!--        <el-table-column prop="check_time" label="检测时间" min-width="150"></el-table-column>-->
<!--      </el-table>-->
<!--    </el-card>-->

<!--    &lt;!&ndash; PDF内容（隐藏） &ndash;&gt;-->
<!--    <div class="pdf-content" v-show="showContentForPDF">-->
<!--&lt;!&ndash;      <div class="server1">&ndash;&gt;-->
<!--&lt;!&ndash;        <h1 id="linuxBaseline2">Linux基线检测报告</h1>&ndash;&gt;-->
<!--&lt;!&ndash;        &lt;!&ndash; 检测时间 &ndash;&gt;&ndash;&gt;-->
<!--&lt;!&ndash;        <div style="text-align:right; margin-top:20px;">&ndash;&gt;-->
<!--&lt;!&ndash;          <p style="font-size:18px;">检测时间：{{ new Date().toLocaleString() }}</p>&ndash;&gt;-->
<!--&lt;!&ndash;        </div>&ndash;&gt;-->
<!--&lt;!&ndash;        <el-row :gutter="20">&ndash;&gt;-->
<!--&lt;!&ndash;          <el-col :span="24"><p>主机名：{{ serverInfo.hostname }}</p></el-col>&ndash;&gt;-->
<!--&lt;!&ndash;          <el-col :span="24"><p>主机架构：{{ serverInfo.arch }}</p></el-col>&ndash;&gt;-->
<!--&lt;!&ndash;          <el-col :span="24"><p>主机CPU信息：{{ serverInfo.cpu }}</p></el-col>&ndash;&gt;-->
<!--&lt;!&ndash;          <el-col :span="24"><p>主机物理CPU个数：{{ serverInfo.cpuPhysical }}</p></el-col>&ndash;&gt;-->
<!--&lt;!&ndash;          <el-col :span="24"><p>主机物理CPU核心数：{{ serverInfo.cpuCore }}</p></el-col>&ndash;&gt;-->
<!--&lt;!&ndash;          <el-col :span="12"><p>主机空闲内存：{{ serverInfo.free }}</p></el-col>&ndash;&gt;-->
<!--&lt;!&ndash;          <el-col :span="24"><p>硬件型号：{{ serverInfo.ProductName }}</p></el-col>&ndash;&gt;-->
<!--&lt;!&ndash;          <el-col :span="24"><p>主机版本信息：{{ serverInfo.version }}</p></el-col>&ndash;&gt;-->
<!--&lt;!&ndash;          <el-col :span="24"><p>服务器IP：{{ selectedIP }}</p></el-col>&ndash;&gt;-->
<!--&lt;!&ndash;        </el-row>&ndash;&gt;-->
<!--&lt;!&ndash;        &lt;!&ndash; 空白分隔 &ndash;&gt;&ndash;&gt;-->
<!--&lt;!&ndash;        <div style="height:200px;"></div>&ndash;&gt;-->
<!--&lt;!&ndash;        &lt;!&ndash; 检测人员签名 &ndash;&gt;&ndash;&gt;-->
<!--&lt;!&ndash;        <div style="text-align:right; margin-top:20px;">&ndash;&gt;-->
<!--&lt;!&ndash;          <span style="font-size:20px;">检测人员签名：</span>&ndash;&gt;-->
<!--&lt;!&ndash;          <span style="display: inline-block; width: 200px; border-bottom: 2px solid #000; margin-left: 10px;"></span>&ndash;&gt;-->
<!--&lt;!&ndash;        </div>&ndash;&gt;-->
<!--&lt;!&ndash;        &lt;!&ndash; 页码 &ndash;&gt;&ndash;&gt;-->
<!--&lt;!&ndash;        <div class="page-number">&ndash;&gt;-->
<!--&lt;!&ndash;          <span>1/{{ totalPages }}</span>&ndash;&gt;-->
<!--&lt;!&ndash;        </div>&ndash;&gt;-->
<!--&lt;!&ndash;      </div>&ndash;&gt;-->

<!--      &lt;!&ndash; 测试正文标题 &ndash;&gt;-->
<!--      <div class="report-content-title">-->
<!--        <h2>等级保护测评报告</h2>-->
<!--      </div>-->

<!--      <el-table :data="filteredCheckresults" style="width: 100%">-->
<!--        <el-table-column label="序号" width="70" type="index"></el-table-column>-->
<!--        <el-table-column prop="description" label="检测项"></el-table-column>-->
<!--        <el-table-column label="重要程度" width="80">-->
<!--          <template slot-scope="scope">-->
<!--            <span-->
<!--                :style="{-->
<!--                color:-->
<!--                  scope.row.importantLevel == '3'-->
<!--                    ? 'red'-->
<!--                    : scope.row.importantLevel == '2'-->
<!--                    ? 'orange'-->
<!--                    : 'green'-->
<!--              }"-->
<!--            >-->
<!--              {{ scope.row.importantLevel || '2' }}-->
<!--            </span>-->
<!--          </template>-->
<!--        </el-table-column>-->
<!--        <el-table-column prop="basis" label="检测依据" min-width="150"></el-table-column>-->
<!--        <el-table-column prop="result" label="检测结果" min-width="150"></el-table-column>-->
<!--        &lt;!&ndash;        <el-table-column label="基准/检测结果" min-width="200">&ndash;&gt;-->
<!--        &lt;!&ndash;          <template slot-scope="scope">&ndash;&gt;-->
<!--        &lt;!&ndash;            {{ scope.row.basis }}/{{ scope.row.result }}&ndash;&gt;-->
<!--        &lt;!&ndash;          </template>&ndash;&gt;-->
<!--        &lt;!&ndash;        </el-table-column>&ndash;&gt;-->
<!--        <el-table-column prop="IsComply" label="是否通过检查" width="120">-->
<!--          <template slot-scope="scope">-->
<!--            <span :class="{ 'failed-result': scope.row.IsComply === 'false' }">-->
<!--              {{ scope.row.IsComply === 'true' ? '通过' : '未通过' }}-->
<!--            </span>-->
<!--          </template>-->
<!--        </el-table-column>-->
<!--        <el-table-column label="修改建议" width="400">-->
<!--          <template slot-scope="scope">-->
<!--            <span v-if="scope.row.IsComply === 'false'">{{ scope.row.recommend }}</span>-->
<!--            <span v-else>-</span>-->
<!--          </template>-->
<!--        </el-table-column>-->
<!--        <el-table-column label="是否符合等保要求（人工判定）" width="120">-->
<!--          <template slot-scope="scope">-->
<!--            <span-->
<!--                :style="{-->
<!--                color:-->
<!--                  scope.row.score == 1-->
<!--                    ? 'green'-->
<!--                    : scope.row.score == 0.5-->
<!--                    ? 'orange'-->
<!--                    : 'red'-->
<!--              }"-->
<!--            >-->
<!--              {{-->
<!--                scope.row.score == 1-->
<!--                    ? '符合'-->
<!--                    : scope.row.score == 0.5-->
<!--                        ? '部分符合'-->
<!--                        : '不符合'-->
<!--              }}-->
<!--            </span>-->
<!--          </template>-->
<!--        </el-table-column>-->
<!--        <el-table-column prop="check_time" label="检测时间" min-width="150"></el-table-column>-->

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
<!--      //aliveHosts: [], // 活跃主机IP列表-->
<!--      selectedIP: '', // 选中的IP-->
<!--      saveLoading: false, // 保存按钮的加载状态-->
<!--      // 等保评分相关计算属性-->
<!--      resultLoading: false,-->
<!--      showScoreResult: false,-->
<!--      levelResult: {-->
<!--        ip: '',-->
<!--        message: '',-->
<!--        score: 0,-->
<!--        totalItems: 0-->
<!--      },-->
<!--    }-->
<!--  },-->
<!--  computed: {-->
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
<!--    },-->
<!--    // 等保评分相关计算属性-->
<!--    // scorePercentage() {-->
<!--    //   return this.levelResult.score ? Math.min(Math.round(parseFloat(this.levelResult.score)), 100) : 0;-->
<!--    // },-->
<!--    //-->
<!--    // scoreColors() {-->
<!--    //   return [-->
<!--    //     {color: '#f56c6c', percentage: 60},-->
<!--    //     {color: '#e6a23c', percentage: 70},-->
<!--    //     {color: '#409eff', percentage: 80},-->
<!--    //     {color: '#67c23a', percentage: 90}-->
<!--    //   ];-->
<!--    // },-->

<!--    formattedScore() {-->
<!--      return this.levelResult.score ? this.levelResult.score.toFixed(2) : '0.00';-->
<!--    }-->
<!--  },-->
<!--  methods: {-->
<!--    goBackToTest() {-->
<!--      this.$router.push('/assetManage');-->
<!--    },-->
<!--    // 获取活跃IP列表-->
<!--    // fetchAliveHosts() {-->
<!--    //   axios.get('/api/getAliveHosts')-->
<!--    //       .then(response => {-->
<!--    //         this.aliveHosts = response.data.alive_hosts;-->
<!--    //         // 如果有IP，默认选择第一个-->
<!--    //         if (this.aliveHosts && this.aliveHosts.length > 0) {-->
<!--    //           this.selectedIP = this.aliveHosts[0];-->
<!--    //           this.fetchAndDisplayChenckResults();-->
<!--    //         }-->
<!--    //       })-->
<!--    //       .catch(error => {-->
<!--    //         console.error('获取活跃IP列表失败:', error);-->
<!--    //         this.$message.error('获取活跃IP列表失败');-->
<!--    //       });-->
<!--    // },-->

<!--    // 切换服务器-->
<!--    // changeServer() {-->
<!--    //   if (this.selectedIP) {-->
<!--    //     this.fetchAndDisplayChenckResults();-->
<!--    //   }-->
<!--    // },-->

<!--    // 修改后的获取检测结果函数-->
<!--    fetchAndDisplayChenckResults() {-->
<!--      // if (!this.selectedIP) {-->
<!--      //   this.$message.warning('请先选择服务器IP');-->
<!--      //   return;-->
<!--      // }-->

<!--      this.tableLoading = true;-->
<!--      axios.get(`/api/level3Userinfo?ip=${this.selectedIP}`)-->
<!--          .then(response => {-->
<!--            this.checkresults = response.data.checkResults.map(item => {-->
<!--              // 根据 tmp_IsComply 的值来设置 score-->
<!--              let score = '0'; // 默认值为不符合-->
<!--              if (item.tmp_IsComply === 'true') {-->
<!--                score = '1'; // 符合-->
<!--              } else if (item.tmp_IsComply === 'half_true') {-->
<!--                score = '0.5'; // 部分符合-->
<!--              }-->
<!--              return {-->
<!--                ...item,-->
<!--                score: score,-->
<!--                importantLevel: item.tmp_importantLevel || '2'-->
<!--              };-->
<!--            });-->
<!--            this.tableLoading = false;-->
<!--            // 根据数据量预估页数-->
<!--            this.estimatePageCount();-->
<!--          })-->
<!--          .catch(error => {-->
<!--            console.error('Error:', error);-->
<!--            this.tableLoading = false;-->
<!--            this.$message.error('获取检测结果失败，请重试');-->
<!--          });-->
<!--      // axios.get(`/api/level3Userinfo?ip=${this.selectedIP}`)-->
<!--      //     .then(response => {-->
<!--      //       // this.checkresults = response.data.Event_result;-->
<!--      //       this.checkresults = response.data.checkResults;-->
<!--      //       // this.serverInfo = response.data.serverInfo;-->
<!--      //       this.tableLoading = false;-->
<!--      //       // 根据数据量预估页数-->
<!--      //       this.estimatePageCount();-->
<!--      //     })-->
<!--      //     .catch(error => {-->
<!--      //       console.error('Error:', error);-->
<!--      //       this.tableLoading = false;-->
<!--      //       this.$message.error('获取检测结果失败，请重试');-->
<!--      //     });-->
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
<!--        const filename = `Linux基线检测报告_${this.selectedIP}_${new Date().toISOString().slice(0,10)}.pdf`;-->
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

<!--    saveScores() {-->
<!--      // 显示保存中状态-->
<!--      this.saveLoading = true;-->

<!--      // 准备请求数据-->
<!--      const scoreMeasures = this.checkresults.map(item => ({-->
<!--        item_id: item.item_id,-->
<!--        importantLevelJson: item.importantLevel, // 如果有importantLevel字段则使用，否则默认为"2"-->
<!--        IsComplyLevel: item.score // 使用选择的评分值-->
<!--      }));-->

<!--      // 构建请求体-->
<!--      const requestData = {-->
<!--        ip: this.selectedIP,-->
<!--        scoreMeasures: scoreMeasures-->
<!--      };-->

<!--      // 发送POST请求-->
<!--      axios.post('/api/updateLevel3Protect', requestData)-->
<!--          .then(response => {-->
<!--            // 保存成功-->
<!--            this.saveLoading = false;-->
<!--            this.$message.success(`成功更新${response.data.itemsUpdated}项评分结果`);-->
<!--          })-->
<!--          .catch(error => {-->
<!--            // 保存失败-->
<!--            this.saveLoading = false;-->
<!--            console.error('保存评分失败:', error);-->
<!--            this.$message.error('保存评分失败，请重试');-->
<!--          });-->
<!--    },-->
<!--    // 获取等保评分-->
<!--    getProtectionLevelResult() {-->
<!--      // if (!this.selectedIP) {-->
<!--      //   this.$message.warning('请先选择服务器IP');-->
<!--      //   return;-->
<!--      // }-->

<!--      this.resultLoading = true;-->
<!--      axios.get(`/api/getlevel3ResultByIp?ip=${this.selectedIP}`)-->
<!--          .then(response => {-->
<!--            this.levelResult = response.data;-->
<!--            this.showScoreResult = true;-->
<!--            this.resultLoading = false;-->

<!--            // 根据得分显示对应的消息提示-->
<!--            const score = this.levelResult.score;-->
<!--            let message = '';-->

<!--            if (score >= 90) {-->
<!--              message = '恭喜！等保评估优秀';-->
<!--              this.$message.success(message);-->
<!--            } else if (score >= 80) {-->
<!--              message = '等保评估良好';-->
<!--              this.$message.success(message);-->
<!--            } else if (score >= 60) {-->
<!--              message = '等保评估合格，但仍有改进空间';-->
<!--              this.$message.warning(message);-->
<!--            } else {-->
<!--              message = '等保评估未达标，建议及时整改';-->
<!--              this.$message.error(message);-->
<!--            }-->
<!--          })-->
<!--          .catch(error => {-->
<!--            console.error('获取等保结果失败:', error);-->
<!--            this.resultLoading = false;-->
<!--            this.$message.error('获取等保结果失败，请重试');-->
<!--          });-->
<!--    },-->

<!--    getScoreConclusion(score) {-->
<!--      if (!score && score !== 0) return '未评估';-->

<!--      if (score >= 90) {-->
<!--        return '优秀';-->
<!--      } else if (score >= 80) {-->
<!--        return '良好';-->
<!--      } else if (score >= 60) {-->
<!--        return '合格';-->
<!--      } else {-->
<!--        return '未达标';-->
<!--      }-->
<!--    },-->

<!--    getScoreClass(score) {-->
<!--      if (!score && score !== 0) return '';-->

<!--      if (score >= 90) {-->
<!--        return 'score-excellent';-->
<!--      } else if (score >= 80) {-->
<!--        return 'score-good';-->
<!--      } else if (score >= 60) {-->
<!--        return 'score-moderate';-->
<!--      } else {-->
<!--        return 'score-poor';-->
<!--      }-->
<!--    }-->
<!--  },-->
<!--  mounted() {-->
<!--    // 从路由参数获取IP-->
<!--    const routeIP = this.$route.query.ip;-->

<!--    if (routeIP) {-->
<!--      this.selectedIP = routeIP;-->
<!--      this.fetchAndDisplayChenckResults();-->
<!--    } else {-->
<!--      this.$message.error('缺少IP参数，请从正确的入口访问此页面');-->
<!--    }-->
<!--    // 先获取活跃IP列表，然后会自动选择第一个IP并获取检测结果-->
<!--    // this.fetchAliveHosts();-->
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

<!--/* 计算评分显示评分部分样式 */-->
<!--/* 新增样式 */-->
<!--.score-card {-->
<!--  margin-top: 20px;-->
<!--  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);-->
<!--}-->

<!--.score-content {-->
<!--  display: flex;-->
<!--  align-items: center;-->
<!--  padding: 15px;-->
<!--}-->

<!--/* 替换原来的仪表盘样式为数字得分样式 */-->
<!--.score-display {-->
<!--  width: 150px;-->
<!--  text-align: center;-->
<!--  margin-right: 30px;-->
<!--  flex-shrink: 0;-->
<!--  border-right: 1px solid #ebeef5;-->
<!--  padding-right: 20px;-->
<!--}-->

<!--.score-title {-->
<!--  font-size: 16px;-->
<!--  color: #606266;-->
<!--  margin-bottom: 10px;-->
<!--}-->

<!--.score-number {-->
<!--  font-size: 36px;-->
<!--  font-weight: bold;-->
<!--  line-height: 1.2;-->
<!--}-->

<!--.score-details {-->
<!--  flex-grow: 1;-->
<!--  display: grid;-->
<!--  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));-->
<!--  gap: 15px;-->
<!--}-->

<!--.detail-item {-->
<!--  display: flex;-->
<!--  flex-direction: column;-->
<!--  background-color: #f5f7fa;-->
<!--  padding: 12px;-->
<!--  border-radius: 4px;-->
<!--}-->

<!--.detail-label {-->
<!--  font-size: 14px;-->
<!--  color: #606266;-->
<!--  margin-bottom: 5px;-->
<!--}-->

<!--.detail-value {-->
<!--  font-size: 18px;-->
<!--  font-weight: bold;-->
<!--  color: #303133;-->
<!--}-->

<!--.score-summary {-->
<!--  padding: 0 15px 15px;-->
<!--}-->

<!--.summary-text {-->
<!--  border-top: 1px solid #ebeef5;-->
<!--  padding-top: 15px;-->
<!--  color: #606266;-->
<!--}-->

<!--/* 不同得分等级的颜色样式 */-->
<!--.score-excellent, .excellent-text {-->
<!--  color: #67c23a;-->
<!--}-->

<!--.score-good, .good-text {-->
<!--  color: #409eff;-->
<!--}-->

<!--.score-moderate, .warning-text {-->
<!--  color: #e6a23c;-->
<!--}-->

<!--.score-poor, .danger-text {-->
<!--  color: #f56c6c;-->
<!--}-->

<!--.excellent-text, .good-text, .warning-text, .danger-text {-->
<!--  font-weight: bold;-->
<!--}-->
<!--</style>-->

<!--<template>-->
<!--  <div class="baseline-container">-->
<!--    &lt;!&ndash; 头部区域 &ndash;&gt;-->
<!--    <div class="header-section">-->
<!--      <h1 class="main-title">等级保护测评</h1>-->
<!--      <div class="date-info">-->
<!--        &lt;!&ndash;        <el-tag type="info">检测时间：{{ new Date().toLocaleString() }}</el-tag>&ndash;&gt;-->
<!--      </div>-->
<!--    </div>-->

<!--    &lt;!&ndash; 控制按钮区域 &ndash;&gt;-->
<!--    <div class="control-section">-->
<!--      <div class="button-group">-->
<!--        &lt;!&ndash; 新增的IP选择下拉框 &ndash;&gt;-->
<!--        <div class="control-item">-->
<!--          <el-select-->
<!--              v-model="selectedIP"-->
<!--              placeholder="选择服务器IP"-->
<!--              @change="changeServer"-->
<!--              size="medium">-->
<!--            <el-option-->
<!--                v-for="ip in aliveHosts"-->
<!--                :key="ip"-->
<!--                :label="ip"-->
<!--                :value="ip">-->
<!--            </el-option>-->
<!--          </el-select>-->
<!--        </div>-->

<!--        <el-button-->

<!--            @click="onExportToPDF"-->
<!--            :loading="pdfLoading"-->
<!--            icon="el-icon-document"-->
<!--            type="primary"-->
<!--            size="medium">-->
<!--          导出为 PDF-->
<!--        </el-button>-->
<!--      </div>-->

<!--      <div class="filter-group">-->
<!--        <el-select-->
<!--            v-model="selectedStatus"-->
<!--            placeholder="请选择状态"-->
<!--            size="medium">-->
<!--          <el-option label="全部" value="all"></el-option>-->
<!--          <el-option label="通过" value="passed"></el-option>-->
<!--          <el-option label="未通过" value="failed"></el-option>-->
<!--        </el-select>-->

<!--        <el-input-->
<!--            placeholder="输入检测项关键字..."-->
<!--            v-model="searchTerm"-->
<!--            @input="filterSearchResults"-->
<!--            prefix-icon="el-icon-search"-->
<!--            size="medium">-->
<!--        </el-input>-->
<!--      </div>-->

<!--      &lt;!&ndash; 新增保存评分按钮 &ndash;&gt;-->
<!--      <el-button-->
<!--          type="success"-->
<!--          icon="el-icon-check"-->
<!--          @click="saveScores"-->
<!--          :loading="saveLoading"-->
<!--          size="medium">-->
<!--        保存人工判定结果-->
<!--      </el-button>-->
<!--      <el-button-->
<!--          type="primary"-->
<!--          icon="el-icon-data-analysis"-->
<!--          @click="getProtectionLevelResult"-->
<!--          :loading="resultLoading"-->
<!--          size="medium">-->
<!--        获取等保结果-->
<!--      </el-button>-->
<!--    </div>-->

<!--    &lt;!&ndash; 得分显示部分，数字得分 &ndash;&gt;-->
<!--    <el-card class="score-card" v-if="showScoreResult" style="margin-bottom: 20px">-->
<!--      <div slot="header" class="card-header">-->
<!--        <span><i class="el-icon-data-line"></i> 等保测评结果</span>-->
<!--        <el-button type="text" @click="showScoreResult = false">-->
<!--          <i class="el-icon-close"></i>-->
<!--        </el-button>-->
<!--      </div>-->

<!--      <div class="score-content">-->
<!--        &lt;!&ndash; 替换仪表盘为简单的得分显示 &ndash;&gt;-->
<!--        <div class="score-display">-->
<!--          <div class="score-title">等保得分</div>-->
<!--          <div class="score-number" :class="getScoreClass(levelResult.score)">-->
<!--            {{ formattedScore }}-->
<!--          </div>-->
<!--        </div>-->

<!--        <div class="score-details">-->
<!--          <div class="detail-item">-->
<!--            <span class="detail-label">IP地址:</span>-->
<!--            <span class="detail-value">{{ levelResult.ip || selectedIP }}</span>-->
<!--          </div>-->
<!--          <div class="detail-item">-->
<!--            <span class="detail-label">等保级别:</span>-->
<!--            <span class="detail-value">三级</span>-->
<!--          </div>-->
<!--          <div class="detail-item">-->
<!--            <span class="detail-label">评估结论:</span>-->
<!--            <span class="detail-value" :class="getScoreClass(levelResult.score)">-->
<!--          {{ getScoreConclusion(levelResult.score) }}-->
<!--        </span>-->
<!--          </div>-->
<!--          <div class="detail-item">-->
<!--            <span class="detail-label">检测项总数:</span>-->
<!--            <span class="detail-value">{{ levelResult.totalItems || '0' }}</span>-->
<!--          </div>-->
<!--        </div>-->
<!--      </div>-->

<!--      <div class="score-summary">-->
<!--        <div class="summary-text">-->
<!--          <p>{{ levelResult.message || '三级等保评估结果' }}</p>-->

<!--          &lt;!&ndash; 根据不同分数区间显示不同的提示信息 &ndash;&gt;-->
<!--          <p v-if="levelResult.score >= 90" class="excellent-text">-->
<!--            <i class="el-icon-circle-check"></i>-->
<!--            得分优秀，符合等保三级要求，建议持续保持-->
<!--          </p>-->
<!--          <p v-else-if="levelResult.score >= 80" class="good-text">-->
<!--            <i class="el-icon-circle-check"></i>-->
<!--            得分良好，基本符合等保三级要求，可进一步完善个别项目-->
<!--          </p>-->
<!--          <p v-else-if="levelResult.score >= 60" class="warning-text">-->
<!--            <i class="el-icon-warning"></i>-->
<!--            得分基本合格，仍有提升空间，建议优化未完全符合的检测项-->
<!--          </p>-->
<!--          <p v-else class="danger-text">-->
<!--            <i class="el-icon-close"></i>-->
<!--            得分未达标，建议查看未通过检测项并根据建议进行整改-->
<!--          </p>-->
<!--        </div>-->
<!--      </div>-->
<!--    </el-card>-->
<!--    &lt;!&ndash;    <el-card class="score-card" v-if="showScoreResult" style="margin-bottom: 30px">&ndash;&gt;-->
<!--    &lt;!&ndash;      <div slot="header" class="card-header">&ndash;&gt;-->
<!--    &lt;!&ndash;        <span><i class="el-icon-data-line"></i> 等保测评结果</span>&ndash;&gt;-->
<!--    &lt;!&ndash;        <el-button type="text" @click="showScoreResult = false">&ndash;&gt;-->
<!--    &lt;!&ndash;          <i class="el-icon-close"></i>&ndash;&gt;-->
<!--    &lt;!&ndash;        </el-button>&ndash;&gt;-->
<!--    &lt;!&ndash;      </div>&ndash;&gt;-->

<!--    &lt;!&ndash;      <div class="score-content">&ndash;&gt;-->
<!--    &lt;!&ndash;        <div class="score-gauge">&ndash;&gt;-->
<!--    &lt;!&ndash;          <el-progress type="dashboard" :percentage="scorePercentage" :color="scoreColors" :stroke-width="12">&ndash;&gt;-->
<!--    &lt;!&ndash;            <div class="score-value">{{ formattedScore }}</div>&ndash;&gt;-->
<!--    &lt;!&ndash;          </el-progress>&ndash;&gt;-->
<!--    &lt;!&ndash;        </div>&ndash;&gt;-->

<!--    &lt;!&ndash;        <div class="score-details">&ndash;&gt;-->
<!--    &lt;!&ndash;          <div class="detail-item">&ndash;&gt;-->
<!--    &lt;!&ndash;            <span class="detail-label">IP地址:</span>&ndash;&gt;-->
<!--    &lt;!&ndash;            <span class="detail-value">{{ levelResult.ip || selectedIP }}</span>&ndash;&gt;-->
<!--    &lt;!&ndash;          </div>&ndash;&gt;-->
<!--    &lt;!&ndash;          <div class="detail-item">&ndash;&gt;-->
<!--    &lt;!&ndash;            <span class="detail-label">等保级别:</span>&ndash;&gt;-->
<!--    &lt;!&ndash;            <span class="detail-value">三级</span>&ndash;&gt;-->
<!--    &lt;!&ndash;          </div>&ndash;&gt;-->
<!--    &lt;!&ndash;          <div class="detail-item">&ndash;&gt;-->
<!--    &lt;!&ndash;            <span class="detail-label">评估结论:</span>&ndash;&gt;-->
<!--    &lt;!&ndash;            <span class="detail-value" :class="getScoreClass(levelResult.score)">&ndash;&gt;-->
<!--    &lt;!&ndash;          {{ getScoreConclusion(levelResult.score) }}&ndash;&gt;-->
<!--    &lt;!&ndash;        </span>&ndash;&gt;-->
<!--    &lt;!&ndash;          </div>&ndash;&gt;-->
<!--    &lt;!&ndash;          <div class="detail-item">&ndash;&gt;-->
<!--    &lt;!&ndash;            <span class="detail-label">检测项总数:</span>&ndash;&gt;-->
<!--    &lt;!&ndash;            <span class="detail-value">{{ levelResult.totalItems || '0' }}</span>&ndash;&gt;-->
<!--    &lt;!&ndash;          </div>&ndash;&gt;-->
<!--    &lt;!&ndash;        </div>&ndash;&gt;-->
<!--    &lt;!&ndash;      </div>&ndash;&gt;-->

<!--    &lt;!&ndash;      <div class="score-summary">&ndash;&gt;-->
<!--    &lt;!&ndash;        <div class="summary-text">&ndash;&gt;-->
<!--    &lt;!&ndash;          <p>{{ levelResult.message || '三级等保评估结果' }}</p>&ndash;&gt;-->

<!--    &lt;!&ndash;          &lt;!&ndash; 根据不同分数区间显示不同的提示信息 &ndash;&gt;&ndash;&gt;-->
<!--    &lt;!&ndash;          <p v-if="levelResult.score >= 90" class="excellent-text">&ndash;&gt;-->
<!--    &lt;!&ndash;            <i class="el-icon-circle-check"></i>&ndash;&gt;-->
<!--    &lt;!&ndash;            得分优秀，符合等保三级要求，建议持续保持&ndash;&gt;-->
<!--    &lt;!&ndash;          </p>&ndash;&gt;-->
<!--    &lt;!&ndash;          <p v-else-if="levelResult.score >= 80" class="good-text">&ndash;&gt;-->
<!--    &lt;!&ndash;            <i class="el-icon-circle-check"></i>&ndash;&gt;-->
<!--    &lt;!&ndash;            得分良好，基本符合等保三级要求，可进一步完善个别项目&ndash;&gt;-->
<!--    &lt;!&ndash;          </p>&ndash;&gt;-->
<!--    &lt;!&ndash;          <p v-else-if="levelResult.score >= 60" class="warning-text">&ndash;&gt;-->
<!--    &lt;!&ndash;            <i class="el-icon-warning"></i>&ndash;&gt;-->
<!--    &lt;!&ndash;            得分基本合格，仍有提升空间，建议优化未完全符合的检测项&ndash;&gt;-->
<!--    &lt;!&ndash;          </p>&ndash;&gt;-->
<!--    &lt;!&ndash;          <p v-else class="danger-text">&ndash;&gt;-->
<!--    &lt;!&ndash;            <i class="el-icon-close"></i>&ndash;&gt;-->
<!--    &lt;!&ndash;            得分未达标，建议查看未通过检测项并根据建议进行整改&ndash;&gt;-->
<!--    &lt;!&ndash;          </p>&ndash;&gt;-->
<!--    &lt;!&ndash;        </div>&ndash;&gt;-->
<!--    &lt;!&ndash;      </div>&ndash;&gt;-->
<!--    &lt;!&ndash;    </el-card>&ndash;&gt;-->


<!--    &lt;!&ndash; 检测结果表格 &ndash;&gt;-->
<!--    <el-card class="results-card">-->
<!--      <div slot="header" class="card-header">-->
<!--        <span><i class="el-icon-document-checked"></i> 检测结果</span>-->
<!--        <div class="summary">-->
<!--          <el-tag type="success">通过: {{ passedCount }}</el-tag>-->
<!--          <el-tag type="danger">未通过: {{ failedCount }}</el-tag>-->
<!--          <el-tag type="info">总计: {{ totalCount }}</el-tag>-->
<!--        </div>-->
<!--      </div>-->

<!--      <el-table-->
<!--          :data="filteredCheckresults"-->
<!--          style="width: 100%"-->
<!--          border-->
<!--          stripe-->
<!--          :header-cell-style="{background:'#f5f7fa',color:'#606266'}"-->
<!--          v-loading="tableLoading">-->
<!--        <el-table-column label="序号" width="70" type="index"></el-table-column>-->
<!--        <el-table-column prop="description" label="检测项" min-width="150"></el-table-column>-->
<!--        <el-table-column label="重要程度" width="120">-->
<!--          <template slot-scope="scope">-->
<!--            <el-select-->
<!--                v-model="scope.row.importantLevel"-->
<!--                placeholder="请选择重要程度"-->
<!--                size="mini">-->
<!--              <el-option label="1" value="1"></el-option>-->
<!--              <el-option label="2" value="2"></el-option>-->
<!--              <el-option label="3" value="3"></el-option>-->
<!--            </el-select>-->
<!--          </template>-->
<!--        </el-table-column>-->
<!--        <el-table-column prop="basis" label="基准" min-width="150"></el-table-column>-->
<!--        <el-table-column prop="result" label="检测结果" min-width="150"></el-table-column>-->
<!--        &lt;!&ndash;        <el-table-column label="基准/检测结果" min-width="200">&ndash;&gt;-->
<!--        &lt;!&ndash;          <template slot-scope="scope">&ndash;&gt;-->
<!--        &lt;!&ndash;            {{ scope.row.basis }}/{{ scope.row.result }}&ndash;&gt;-->
<!--        &lt;!&ndash;          </template>&ndash;&gt;-->
<!--        &lt;!&ndash;        </el-table-column>&ndash;&gt;-->
<!--        <el-table-column label="是否通过检查" width="120">-->
<!--          <template slot-scope="scope">-->
<!--            <el-tag :type="scope.row.IsComply === 'true' ? 'success' : 'danger'">-->
<!--              {{ scope.row.IsComply === 'true' ? '通过' : '未通过' }}-->
<!--            </el-tag>-->
<!--          </template>-->
<!--        </el-table-column>-->
<!--        <el-table-column label="修改建议" min-width="250">-->
<!--          <template slot-scope="scope">-->
<!--            <span v-if="scope.row.IsComply === 'false'">{{ scope.row.recommend }}</span>-->
<!--            <span v-else>-</span>-->
<!--          </template>-->
<!--        </el-table-column>-->
<!--        <el-table-column label="是否符合等保要求（人工判定）" width="120">-->
<!--          <template slot-scope="scope">-->
<!--            <el-select-->
<!--                v-model="scope.row.score"-->
<!--                placeholder="请选择评分"-->
<!--                size="mini">-->
<!--              <el-option label="符合" value="1"></el-option>-->
<!--              <el-option label="部分符合" value="0.5"></el-option>-->
<!--              <el-option label="不符合" value="0"></el-option>-->
<!--            </el-select>-->
<!--          </template>-->
<!--        </el-table-column>-->
<!--      </el-table>-->
<!--    </el-card>-->

<!--    &lt;!&ndash; PDF内容（隐藏） &ndash;&gt;-->
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
<!--          <el-col :span="24"><p>主机物理CPU核心数：{{ serverInfo.cpuCore }}</p></el-col>-->
<!--          <el-col :span="12"><p>主机空闲内存：{{ serverInfo.free }}</p></el-col>-->
<!--          <el-col :span="24"><p>硬件型号：{{ serverInfo.ProductName }}</p></el-col>-->
<!--          <el-col :span="24"><p>主机版本信息：{{ serverInfo.version }}</p></el-col>-->
<!--          <el-col :span="24"><p>服务器IP：{{ selectedIP }}</p></el-col>-->
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
<!--        <el-table-column label="重要程度" width="80">-->
<!--          <template slot-scope="scope">-->
<!--            <span-->
<!--                :style="{-->
<!--                color:-->
<!--                  scope.row.importantLevel == '3'-->
<!--                    ? 'red'-->
<!--                    : scope.row.importantLevel == '2'-->
<!--                    ? 'orange'-->
<!--                    : 'green'-->
<!--              }"-->
<!--            >-->
<!--              {{ scope.row.importantLevel || '2' }}-->
<!--            </span>-->
<!--          </template>-->
<!--        </el-table-column>-->
<!--        <el-table-column prop="basis" label="检测依据" min-width="150"></el-table-column>-->
<!--        <el-table-column prop="result" label="检测结果" min-width="150"></el-table-column>-->
<!--        &lt;!&ndash;        <el-table-column label="基准/检测结果" min-width="200">&ndash;&gt;-->
<!--        &lt;!&ndash;          <template slot-scope="scope">&ndash;&gt;-->
<!--        &lt;!&ndash;            {{ scope.row.basis }}/{{ scope.row.result }}&ndash;&gt;-->
<!--        &lt;!&ndash;          </template>&ndash;&gt;-->
<!--        &lt;!&ndash;        </el-table-column>&ndash;&gt;-->
<!--        <el-table-column prop="IsComply" label="是否通过检查" width="120">-->
<!--          <template slot-scope="scope">-->
<!--            <span :class="{ 'failed-result': scope.row.IsComply === 'false' }">-->
<!--              {{ scope.row.IsComply === 'true' ? '通过' : '未通过' }}-->
<!--            </span>-->
<!--          </template>-->
<!--        </el-table-column>-->
<!--        <el-table-column label="修改建议" width="400">-->
<!--          <template slot-scope="scope">-->
<!--            <span v-if="scope.row.IsComply === 'false'">{{ scope.row.recommend }}</span>-->
<!--            <span v-else>-</span>-->
<!--          </template>-->
<!--        </el-table-column>-->
<!--        <el-table-column label="是否符合等保要求（人工判定）" width="120">-->
<!--          <template slot-scope="scope">-->
<!--            <span-->
<!--                :style="{-->
<!--                color:-->
<!--                  scope.row.score == 1-->
<!--                    ? 'green'-->
<!--                    : scope.row.score == 0.5-->
<!--                    ? 'orange'-->
<!--                    : 'red'-->
<!--              }"-->
<!--            >-->
<!--              {{-->
<!--                scope.row.score == 1-->
<!--                    ? '符合'-->
<!--                    : scope.row.score == 0.5-->
<!--                        ? '部分符合'-->
<!--                        : '不符合'-->
<!--              }}-->
<!--            </span>-->
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
<!--      saveLoading: false, // 保存按钮的加载状态-->
<!--      // 等保评分相关计算属性-->
<!--      resultLoading: false,-->
<!--      showScoreResult: false,-->
<!--      levelResult: {-->
<!--        ip: '',-->
<!--        message: '',-->
<!--        score: 0,-->
<!--        totalItems: 0-->
<!--      },-->
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
<!--    passedCount() {-->
<!--      return this.checkresults.filter(item => item.IsComply === 'true').length;-->
<!--    },-->
<!--    failedCount() {-->
<!--      return this.checkresults.filter(item => item.IsComply === 'false').length;-->
<!--    },-->
<!--    totalCount() {-->
<!--      return this.checkresults.length;-->
<!--    },-->
<!--    // 等保评分相关计算属性-->
<!--    // scorePercentage() {-->
<!--    //   return this.levelResult.score ? Math.min(Math.round(parseFloat(this.levelResult.score)), 100) : 0;-->
<!--    // },-->
<!--    //-->
<!--    // scoreColors() {-->
<!--    //   return [-->
<!--    //     {color: '#f56c6c', percentage: 60},-->
<!--    //     {color: '#e6a23c', percentage: 70},-->
<!--    //     {color: '#409eff', percentage: 80},-->
<!--    //     {color: '#67c23a', percentage: 90}-->
<!--    //   ];-->
<!--    // },-->

<!--    formattedScore() {-->
<!--      return this.levelResult.score ? this.levelResult.score.toFixed(2) : '0.00';-->
<!--    }-->
<!--  },-->
<!--  methods: {-->
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
<!--            console.error('获取活跃IP列表失败:', error);-->
<!--            this.$message.error('获取活跃IP列表失败');-->
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
<!--      axios.get(`/api/level3Userinfo?ip=${this.selectedIP}`)-->
<!--          .then(response => {-->
<!--            this.checkresults = response.data.checkResults.map(item => {-->
<!--              // 根据 tmp_IsComply 的值来设置 score-->
<!--              let score = '0'; // 默认值为不符合-->
<!--              if (item.tmp_IsComply === 'true') {-->
<!--                score = '1'; // 符合-->
<!--              } else if (item.tmp_IsComply === 'half_true') {-->
<!--                score = '0.5'; // 部分符合-->
<!--              }-->
<!--              return {-->
<!--                ...item,-->
<!--                score: score,-->
<!--                importantLevel: item.tmp_importantLevel || '2'-->
<!--              };-->
<!--            });-->
<!--            this.tableLoading = false;-->
<!--            // 根据数据量预估页数-->
<!--            this.estimatePageCount();-->
<!--          })-->
<!--          .catch(error => {-->
<!--            console.error('Error:', error);-->
<!--            this.tableLoading = false;-->
<!--            this.$message.error('获取检测结果失败，请重试');-->
<!--          });-->
<!--      // axios.get(`/api/level3Userinfo?ip=${this.selectedIP}`)-->
<!--      //     .then(response => {-->
<!--      //       // this.checkresults = response.data.Event_result;-->
<!--      //       this.checkresults = response.data.checkResults;-->
<!--      //       // this.serverInfo = response.data.serverInfo;-->
<!--      //       this.tableLoading = false;-->
<!--      //       // 根据数据量预估页数-->
<!--      //       this.estimatePageCount();-->
<!--      //     })-->
<!--      //     .catch(error => {-->
<!--      //       console.error('Error:', error);-->
<!--      //       this.tableLoading = false;-->
<!--      //       this.$message.error('获取检测结果失败，请重试');-->
<!--      //     });-->
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
<!--        const filename = `Linux基线检测报告_${this.selectedIP}_${new Date().toISOString().slice(0,10)}.pdf`;-->
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

<!--    saveScores() {-->
<!--      // 显示保存中状态-->
<!--      this.saveLoading = true;-->

<!--      // 准备请求数据-->
<!--      const scoreMeasures = this.checkresults.map(item => ({-->
<!--        item_id: item.item_id,-->
<!--        importantLevelJson: item.importantLevel, // 如果有importantLevel字段则使用，否则默认为"2"-->
<!--        IsComplyLevel: item.score // 使用选择的评分值-->
<!--      }));-->

<!--      // 构建请求体-->
<!--      const requestData = {-->
<!--        ip: this.selectedIP,-->
<!--        scoreMeasures: scoreMeasures-->
<!--      };-->

<!--      // 发送POST请求-->
<!--      axios.post('/api/updateLevel3Protect', requestData)-->
<!--          .then(response => {-->
<!--            // 保存成功-->
<!--            this.saveLoading = false;-->
<!--            this.$message.success(`成功更新${response.data.itemsUpdated}项评分结果`);-->
<!--          })-->
<!--          .catch(error => {-->
<!--            // 保存失败-->
<!--            this.saveLoading = false;-->
<!--            console.error('保存评分失败:', error);-->
<!--            this.$message.error('保存评分失败，请重试');-->
<!--          });-->
<!--    },-->
<!--    // 获取等保评分-->
<!--    getProtectionLevelResult() {-->
<!--      if (!this.selectedIP) {-->
<!--        this.$message.warning('请先选择服务器IP');-->
<!--        return;-->
<!--      }-->

<!--      this.resultLoading = true;-->
<!--      axios.get(`/api/getlevel3ResultByIp?ip=${this.selectedIP}`)-->
<!--          .then(response => {-->
<!--            this.levelResult = response.data;-->
<!--            this.showScoreResult = true;-->
<!--            this.resultLoading = false;-->

<!--            // 根据得分显示对应的消息提示-->
<!--            const score = this.levelResult.score;-->
<!--            let message = '';-->

<!--            if (score >= 90) {-->
<!--              message = '恭喜！等保评估优秀';-->
<!--              this.$message.success(message);-->
<!--            } else if (score >= 80) {-->
<!--              message = '等保评估良好';-->
<!--              this.$message.success(message);-->
<!--            } else if (score >= 60) {-->
<!--              message = '等保评估合格，但仍有改进空间';-->
<!--              this.$message.warning(message);-->
<!--            } else {-->
<!--              message = '等保评估未达标，建议及时整改';-->
<!--              this.$message.error(message);-->
<!--            }-->
<!--          })-->
<!--          .catch(error => {-->
<!--            console.error('获取等保结果失败:', error);-->
<!--            this.resultLoading = false;-->
<!--            this.$message.error('获取等保结果失败，请重试');-->
<!--          });-->
<!--    },-->

<!--    getScoreConclusion(score) {-->
<!--      if (!score && score !== 0) return '未评估';-->

<!--      if (score >= 90) {-->
<!--        return '优秀';-->
<!--      } else if (score >= 80) {-->
<!--        return '良好';-->
<!--      } else if (score >= 60) {-->
<!--        return '合格';-->
<!--      } else {-->
<!--        return '未达标';-->
<!--      }-->
<!--    },-->

<!--    getScoreClass(score) {-->
<!--      if (!score && score !== 0) return '';-->

<!--      if (score >= 90) {-->
<!--        return 'score-excellent';-->
<!--      } else if (score >= 80) {-->
<!--        return 'score-good';-->
<!--      } else if (score >= 60) {-->
<!--        return 'score-moderate';-->
<!--      } else {-->
<!--        return 'score-poor';-->
<!--      }-->
<!--    }-->
<!--  },-->
<!--  mounted() {-->
<!--    // 先获取活跃IP列表，然后会自动选择第一个IP并获取检测结果-->
<!--    this.fetchAliveHosts();-->
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

<!--/* 计算评分显示评分部分样式 */-->
<!--/* 新增样式 */-->
<!--.score-card {-->
<!--  margin-top: 20px;-->
<!--  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);-->
<!--}-->

<!--.score-content {-->
<!--  display: flex;-->
<!--  align-items: center;-->
<!--  padding: 15px;-->
<!--}-->

<!--/* 替换原来的仪表盘样式为数字得分样式 */-->
<!--.score-display {-->
<!--  width: 150px;-->
<!--  text-align: center;-->
<!--  margin-right: 30px;-->
<!--  flex-shrink: 0;-->
<!--  border-right: 1px solid #ebeef5;-->
<!--  padding-right: 20px;-->
<!--}-->

<!--.score-title {-->
<!--  font-size: 16px;-->
<!--  color: #606266;-->
<!--  margin-bottom: 10px;-->
<!--}-->

<!--.score-number {-->
<!--  font-size: 36px;-->
<!--  font-weight: bold;-->
<!--  line-height: 1.2;-->
<!--}-->

<!--.score-details {-->
<!--  flex-grow: 1;-->
<!--  display: grid;-->
<!--  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));-->
<!--  gap: 15px;-->
<!--}-->

<!--.detail-item {-->
<!--  display: flex;-->
<!--  flex-direction: column;-->
<!--  background-color: #f5f7fa;-->
<!--  padding: 12px;-->
<!--  border-radius: 4px;-->
<!--}-->

<!--.detail-label {-->
<!--  font-size: 14px;-->
<!--  color: #606266;-->
<!--  margin-bottom: 5px;-->
<!--}-->

<!--.detail-value {-->
<!--  font-size: 18px;-->
<!--  font-weight: bold;-->
<!--  color: #303133;-->
<!--}-->

<!--.score-summary {-->
<!--  padding: 0 15px 15px;-->
<!--}-->

<!--.summary-text {-->
<!--  border-top: 1px solid #ebeef5;-->
<!--  padding-top: 15px;-->
<!--  color: #606266;-->
<!--}-->

<!--/* 不同得分等级的颜色样式 */-->
<!--.score-excellent, .excellent-text {-->
<!--  color: #67c23a;-->
<!--}-->

<!--.score-good, .good-text {-->
<!--  color: #409eff;-->
<!--}-->

<!--.score-moderate, .warning-text {-->
<!--  color: #e6a23c;-->
<!--}-->

<!--.score-poor, .danger-text {-->
<!--  color: #f56c6c;-->
<!--}-->

<!--.excellent-text, .good-text, .warning-text, .danger-text {-->
<!--  font-weight: bold;-->
<!--}-->
<!--</style>-->


