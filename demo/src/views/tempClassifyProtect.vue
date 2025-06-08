<template>
  <div class="baseline-container">
    <!-- 头部区域 -->
    <div class="header-section">
      <el-button
          type="primary"
          icon="el-icon-arrow-left"
          @click="goBack"
          size="mini"
          style="margin-left:10px">
        返回检测
      </el-button>
      <h1 class="main-title">等保测评结果</h1>

      <div class="date-info">
        <el-tag type="info"> </el-tag>
      </div>
    </div>

    <!-- 控制按钮区域 -->
    <div class="control-section">
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

      <div class="action-buttons">
        <!-- 导出PDF按钮 -->
        <el-button
            type="warning"
            icon="el-icon-printer"
            @click="exportPdf"
            :loading="pdfExporting"
            size="medium">
          {{ pdfExporting ? '导出中...' : '导出PDF报告' }}
        </el-button>

        <!-- 保存评分按钮 -->
        <el-button
            type="success"
            icon="el-icon-check"
            @click="saveScores"
            :loading="saveLoading"
            :disabled="!canSave"
            size="medium">
          保存
        </el-button>
      </div>
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
        <el-table-column prop="description" label="检测项" min-width="80"></el-table-column>
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

  </div>
</template>

<script>
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
      saveLoading: false,
      pdfExporting: false, // PDF导出状态
      ip: '',
      // 新增等保得分相关数据
      protectionScore: {
        totalScore: 0,
        maxScore: 0,
        scorePercentage: 0,
        level: '',
        categoryScores: []
      }
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
    },
    // 检查是否所有pending项都已选择
    canSave() {
      const pendingItems = this.checkresults.filter(item => item.IsComply === 'pending');
      return pendingItems.every(item => item.score && item.score !== '');
    },

    // 获取未完成选择的pending项数量
    unfinishedPendingCount() {
      const pendingItems = this.checkresults.filter(item => item.IsComply === 'pending');
      return pendingItems.filter(item => !item.score || item.score === '').length;
    }
  },
  methods: {
    // 获取状态对应的类型（用于el-tag的type属性）
    getStatusType(status) {
      switch(status) {
        case 'true': return 'success';
        case 'false': return 'danger';
        case 'pending': return 'warning';
        default: return 'info';
      }
    },

    // 获取状态对应的文本
    getStatusText(status) {
      switch(status) {
        case 'true': return '通过';
        case 'false': return '未通过';
        case 'pending': return '待检查';
        default: return '未知';
      }
    },

    // 选择变化监听方法
    onScoreChange() {
      // 当用户改变选择时，强制更新视图以重新计算canSave
      this.$forceUpdate();
    },

    // 获取检测结果函数
    fetchAndDisplayChenckResults() {
      const ip = this.$route.query.ip;
      this.ip = this.$route.query.ip;
      if (!ip) {
        this.$message.error('无效的访问参数');
        this.$router.push('/');
        return;
      }

      this.tableLoading = true;
      axios.get(`/api/level3TmpUserinfo?ip=${ip}`)
          .then(response => {
            this.checkresults = response.data.checkResults.map(item => {
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
          })
          .catch(error => {
            console.error('Error:', error);
            this.tableLoading = false;
            this.$message.error('获取检测结果失败，请重试');
          });
    },

    // 新增：获取等保得分
    async fetchProtectionScore() {
      try {
        const response = await axios.get(`/api/getLevel3Score?ip=${this.ip}`);
        this.protectionScore = response.data;
      } catch (error) {
        console.error('获取等保得分失败:', error);
        // 设置默认值
        this.protectionScore = {
          totalScore: 0,
          maxScore: 100,
          scorePercentage: 0,
          level: '未评级',
          categoryScores: []
        };
      }
    },

    saveScores() {
      // 验证pending项是否都已选择
      if (!this.canSave) {
        this.$message.warning(`还有 ${this.unfinishedPendingCount} 个待检查项目需要人工判定，请完成后再保存`);
        return;
      }

      this.saveLoading = true;
      const scoreMeasures = this.checkresults.map(item => ({
        item_id: item.item_id,
        importantLevelJson: item.importantLevel,
        IsComplyLevel: item.score
      }));

      const requestData = {
        ip: this.ip,
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

    goBack() {
      this.$router.push('/classifyProtectHome');
    },

    // ==================== PDF导出功能 ====================

    // 主导出函数
    async exportPdf() {
      if (!this.ip) {
        this.$message.warning('缺少IP参数，无法导出');
        return;
      }

      this.pdfExporting = true;

      try {
        // 获取等保得分数据
        await this.fetchProtectionScore();

        // 动态导入库
        const jsPDF = (await import('jspdf')).default;
        const html2canvas = (await import('html2canvas')).default;

        // 创建临时的打印内容容器
        const printContent = this.createPrintContent();
        document.body.appendChild(printContent);

        // 等待内容渲染完成
        await this.$nextTick();
        await new Promise(resolve => setTimeout(resolve, 1500));

        // 转换为canvas
        const canvas = await html2canvas(printContent, {
          scale: 1.5,
          useCORS: true,
          allowTaint: true,
          backgroundColor: '#ffffff',
          width: printContent.scrollWidth,
          height: printContent.scrollHeight,
          scrollX: 0,
          scrollY: 0,
          windowWidth: printContent.scrollWidth,
          windowHeight: printContent.scrollHeight
        });

        // 移除临时容器
        document.body.removeChild(printContent);

        // 创建PDF
        const pdf = new jsPDF('p', 'mm', 'a4');
        const pdfWidth = pdf.internal.pageSize.getWidth();
        const pdfHeight = pdf.internal.pageSize.getHeight();

        // 生成多页PDF
        await this.createMultiPagePdf(pdf, canvas, pdfWidth, pdfHeight);

        // 保存PDF
        const fileName = `等保测评结果_${this.ip}_${new Date().toISOString().split('T')[0]}.pdf`;
        pdf.save(fileName);

        this.$message.success('PDF报告导出成功');

      } catch (error) {
        console.error('PDF导出失败:', error);
        this.$message.error('PDF导出失败，请重试');
      } finally {
        this.pdfExporting = false;
      }
    },

    // 创建打印内容
    createPrintContent() {
      const printDiv = document.createElement('div');
      printDiv.style.cssText = `
        position: absolute;
        top: -10000px;
        left: -10000px;
        width: 800px;
        background: white;
        padding: 20px;
        font-family: 'Microsoft YaHei', Arial, sans-serif;
        line-height: 1.8;
        color: #333;
        box-sizing: border-box;
        overflow: visible;
      `;

      printDiv.innerHTML = this.generatePrintHTML();

      // 优化表格样式
      const tables = printDiv.querySelectorAll('table');
      tables.forEach(table => {
        table.style.tableLayout = 'fixed';
        table.style.width = '100%';
        table.style.borderCollapse = 'collapse';
        table.style.marginBottom = '20px';
        table.style.pageBreakInside = 'avoid';

        const cells = table.querySelectorAll('td, th');
        cells.forEach(cell => {
          cell.style.wordWrap = 'break-word';
          cell.style.wordBreak = 'break-all';
          cell.style.overflow = 'visible';
          cell.style.whiteSpace = 'normal';
          cell.style.padding = '8px';
          cell.style.lineHeight = '1.6';
        });
      });

      // 为每个主要区块添加分页控制
      const sections = printDiv.querySelectorAll('div[style*="margin-bottom: 25px"]');
      sections.forEach(section => {
        section.style.pageBreakInside = 'avoid';
        section.style.marginBottom = '30px';
      });

      return printDiv;
    },

    // 生成打印HTML内容
    generatePrintHTML() {
      return `
        <div style="text-align: center; margin-bottom: 30px;">
          <h1 style="color: #333; font-size: 24px; margin: 0;">等保测评结果报告</h1>
          <p style="color: #666; margin: 10px 0;">资产IP：${this.ip}</p>
          <p style="color: #666; margin: 10px 0;">生成时间：${new Date().toLocaleString()}</p>
        </div>

        ${this.generateDetailTableHTML()}
        ${this.generateSignatureHTML()}
      `;
    },

    // 生成详细表格HTML
    generateDetailTableHTML() {
      let html = `
        <div style="margin-bottom: 25px;">
          <h2 style="color: #409EFF; font-size: 18px; border-bottom: 2px solid #409EFF; padding-bottom: 5px;">检测详情</h2>
          <table style="width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 11px;">
            <thead>
              <tr style="background: #f5f7fa;">
                <th style="padding: 6px; border: 1px solid #ddd; text-align: center; width: 4%;">序号</th>
                <th style="padding: 6px; border: 1px solid #ddd; text-align: center; width: 10%;">检测项</th>
                <th style="padding: 6px; border: 1px solid #ddd; text-align: center; width: 6%;">重要程度</th>
                <th style="padding: 6px; border: 1px solid #ddd; text-align: center; width: 15%;">基准</th>
                <th style="padding: 6px; border: 1px solid #ddd; text-align: center; width: 15%;">检测结果</th>
                <th style="padding: 6px; border: 1px solid #ddd; text-align: center; width: 7%;">是否通过</th>
                <th style="padding: 6px; border: 1px solid #ddd; text-align: center; width: 8%;">等保要求符合度</th>
                <th style="padding: 6px; border: 1px solid #ddd; text-align: center; width: 15%;">修改建议</th>
                <th style="padding: 6px; border: 1px solid #ddd; text-align: center; width: 8%;">检测时间</th>
              </tr>
            </thead>
            <tbody>
      `;

      this.checkresults.forEach((item, index) => {
        let statusText, statusColor;
        switch(item.IsComply) {
          case 'true':
            statusText = '通过';
            statusColor = '#67C23A';  // 绿色
            break;
          case 'false':
            statusText = '未通过';
            statusColor = '#F56C6C';  // 红色
            break;
          case 'pending':
            statusText = '待检查';
            statusColor = '#E6A23C';  // 橙色
            break;
          default:
            statusText = '未知';
            statusColor = '#909399';  // 灰色
            break;
        }
        const scoreText = this.getScoreText(item.score);
        const scoreColor = item.score === '1' ? '#67C23A' : item.score === '0.5' ? '#E6A23C' : '#F56C6C';
        const suggestion = item.IsComply === 'false' ? (item.recommend || '-') : '-';

        html += `
          <tr>
            <td style="padding: 5px; border: 1px solid #ddd; text-align: center;">${index + 1}</td>
            <td style="padding: 5px; border: 1px solid #ddd; font-size: 10px;">${item.description || '-'}</td>
            <td style="padding: 5px; border: 1px solid #ddd; text-align: center;">${item.importantLevel || '2'}</td>
            <td style="padding: 5px; border: 1px solid #ddd; font-size: 10px;">${item.basis || '-'}</td>
            <td style="padding: 5px; border: 1px solid #ddd; font-size: 10px;">${item.result || '-'}</td>
            <td style="padding: 5px; border: 1px solid #ddd; text-align: center; color: ${statusColor}; font-weight: bold;">${statusText}</td>
            <td style="padding: 5px; border: 1px solid #ddd; text-align: center; color: ${scoreColor}; font-weight: bold;">${scoreText}</td>
            <td style="padding: 5px; border: 1px solid #ddd; font-size: 10px;">${suggestion}</td>
            <td style="padding: 5px; border: 1px solid #ddd; font-size: 9px; text-align: center;">${item.check_time || '-'}</td>
          </tr>
        `;
      });

      html += `
            </tbody>
          </table>
        </div>
      `;

      return html;
    },

    // 新增：生成签名区域HTML
    generateSignatureHTML() {
      return `
        <div style="margin-top: 40px; margin-bottom: 30px;">
          <div style="display: flex; justify-content: space-between; align-items: flex-end; width: 100%;">
            <div style="flex: 1;">
              <p style="margin: 0; font-size: 14px; line-height: 2;">检测人员签名：____________________________</p>
            </div>
            <div style="flex: 1; text-align: right;">
              <p style="margin: 0; font-size: 14px; line-height: 2;">时间：____________________________</p>
            </div>
          </div>
        </div>
      `;
    },

    // 智能分页算法
    findOptimalBreakPoint(canvas, startY, maxHeight, canvasWidth) {
      const ctx = canvas.getContext('2d');
      const imageData = ctx.getImageData(0, startY, canvasWidth, maxHeight);
      const data = imageData.data;

      const minHeight = Math.max(50, maxHeight * 0.7);

      for (let y = Math.floor(maxHeight) - 1; y >= minHeight; y--) {
        if (this.isTableRowBoundary(data, y, canvasWidth, maxHeight)) {
          return y;
        }

        if (this.isRowEmpty(data, y, canvasWidth)) {
          let emptyRowCount = 0;
          for (let checkY = y; checkY >= Math.max(0, y - 10) && checkY < maxHeight; checkY--) {
            if (this.isRowEmpty(data, checkY, canvasWidth)) {
              emptyRowCount++;
            } else {
              break;
            }
          }

          if (emptyRowCount >= 3) {
            return y - emptyRowCount + 1;
          }
        }
      }

      for (let y = Math.floor(maxHeight) - 20; y >= minHeight; y--) {
        if (this.isSafeBreakPoint(data, y, canvasWidth, maxHeight)) {
          return y;
        }
      }

      return Math.floor(maxHeight * 0.9);
    },

    isTableRowBoundary(imageData, rowIndex, width, maxHeight) {
      const checkRange = 3;
      const currentRowBorderPixels = this.countBorderPixels(imageData, rowIndex, width);

      let aboveBorderCount = 0;
      for (let i = 1; i <= checkRange; i++) {
        const checkY = rowIndex - i;
        if (checkY >= 0) {
          const borderPixels = this.countBorderPixels(imageData, checkY, width);
          if (borderPixels > width * 0.1) {
            aboveBorderCount++;
          }
        }
      }

      let belowBorderCount = 0;
      for (let i = 1; i <= checkRange; i++) {
        const checkY = rowIndex + i;
        if (checkY < maxHeight) {
          const borderPixels = this.countBorderPixels(imageData, checkY, width);
          if (borderPixels > width * 0.1) {
            belowBorderCount++;
          }
        }
      }

      return currentRowBorderPixels > width * 0.15 &&
          aboveBorderCount <= 1 &&
          belowBorderCount <= 1;
    },

    countBorderPixels(imageData, rowIndex, width) {
      const rowStart = rowIndex * width * 4;
      const rowEnd = rowStart + width * 4;
      let borderPixels = 0;

      for (let i = rowStart; i < rowEnd; i += 4) {
        const r = imageData[i];
        const g = imageData[i + 1];
        const b = imageData[i + 2];

        if ((r < 100 && g < 100 && b < 100) ||
            (Math.abs(r - 221) < 10 && Math.abs(g - 221) < 10 && Math.abs(b - 221) < 10)) {
          borderPixels++;
        }
      }

      return borderPixels;
    },

    isSafeBreakPoint(imageData, rowIndex, width, maxHeight) {
      const checkRange = 5;
      let totalContentPixels = 0;
      let totalPixels = 0;

      for (let y = Math.max(0, rowIndex - checkRange);
           y <= Math.min(maxHeight - 1, rowIndex + checkRange); y++) {
        const rowStart = y * width * 4;
        const rowEnd = rowStart + width * 4;

        for (let i = rowStart; i < rowEnd; i += 4) {
          const r = imageData[i];
          const g = imageData[i + 1];
          const b = imageData[i + 2];

          totalPixels++;

          if (r < 250 || g < 250 || b < 250) {
            totalContentPixels++;
          }
        }
      }

      const contentDensity = totalContentPixels / totalPixels;
      return contentDensity < 0.05;
    },

    isRowEmpty(imageData, rowIndex, width) {
      const rowStart = rowIndex * width * 4;
      const rowEnd = rowStart + width * 4;

      for (let i = rowStart; i < rowEnd; i += 4) {
        const r = imageData[i];
        const g = imageData[i + 1];
        const b = imageData[i + 2];

        if (r < 250 || g < 250 || b < 250) {
          return false;
        }
      }
      return true;
    },

    // 创建多页PDF
    async createMultiPagePdf(pdf, canvas, pdfWidth, pdfHeight) {
      const imgWidth = canvas.width;
      const imgHeight = canvas.height;

      const pageHeight = pdfHeight - 50;
      const ratio = pdfWidth / imgWidth;
      const scaledWidth = pdfWidth;
      const scaledHeight = imgHeight * ratio;

      const pixelRatio = scaledHeight / imgHeight;
      const pageHeightInPixels = pageHeight / pixelRatio;

      let currentY = 0;
      let pageIndex = 0;
      const pages = [];

      while (currentY < imgHeight) {
        if (pageIndex > 0) {
          pdf.addPage();
        }

        let remainingHeight = imgHeight - currentY;
        let currentPageContentHeight = Math.min(pageHeightInPixels, remainingHeight);

        if (remainingHeight > pageHeightInPixels) {
          const optimalHeight = this.findOptimalBreakPoint(
              canvas,
              currentY,
              currentPageContentHeight,
              imgWidth
          );

          if (optimalHeight > pageHeightInPixels * 0.5) {
            currentPageContentHeight = optimalHeight;
          }
        }

        const pageCanvas = document.createElement('canvas');
        const pageCtx = pageCanvas.getContext('2d');

        pageCanvas.width = imgWidth;
        pageCanvas.height = currentPageContentHeight;

        pageCtx.fillStyle = '#ffffff';
        pageCtx.fillRect(0, 0, imgWidth, currentPageContentHeight);

        pageCtx.drawImage(
            canvas,
            0, currentY, imgWidth, currentPageContentHeight,
            0, 0, imgWidth, currentPageContentHeight
        );

        const pageImgData = pageCanvas.toDataURL('image/png');
        const pageScaledHeight = currentPageContentHeight * pixelRatio;

        pdf.addImage(
            pageImgData,
            'PNG',
            0,
            25,
            scaledWidth,
            pageScaledHeight
        );

        pages.push({
          pageNumber: pageIndex + 1,
          scaledHeight: pageScaledHeight
        });

        currentY += currentPageContentHeight;
        pageIndex++;

        if (pageIndex > 50) {
          console.warn('PDF页数过多，强制结束');
          break;
        }
      }

      const totalPages = pageIndex;

      // 添加页码
      for (let i = 0; i < totalPages; i++) {
        pdf.setPage(i + 1);
        pdf.setFontSize(10);
        pdf.setTextColor(102, 102, 102);

        const pageText = `${i + 1}/${totalPages}`;
        const textWidth = pdf.getTextWidth(pageText);
        const xPosition = (pdfWidth - textWidth) / 2;
        const yPosition = pdfHeight - 15;

        pdf.text(pageText, xPosition, yPosition);
      }
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

.header-section > div {
  display: flex;
  align-items: center;
  gap: 10px;
}

.main-title {
  color: #303133;
  font-size: 24px;
  font-weight: bold;
  margin: 0 !important;
}

.control-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 15px;
}

.filter-group {
  display: flex;
  gap: 10px;
}

.filter-group .el-input {
  width: 250px;
}

.action-buttons {
  display: flex;
  gap: 10px;
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

.server1 .el-col p {
  font-size: 16px;
  white-space: pre-wrap;
  line-height: 1.6;
  margin-bottom: 5px;
}

.report-content-title h2 {
  font-size: 18pt;
  color: #303133;
  margin: 0;
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

/* 新增样式 - pending状态的下拉框样式 */
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

  .action-buttons {
    width: 100%;
    justify-content: flex-end;
  }
}
</style>

<!--<template>-->
<!--  <div class="baseline-container">-->
<!--    &lt;!&ndash; 头部区域 &ndash;&gt;-->
<!--    <div class="header-section">-->
<!--      <el-button-->
<!--          type="primary"-->
<!--          icon="el-icon-arrow-left"-->
<!--          @click="goBack"-->
<!--          size="mini"-->
<!--          style="margin-left:10px">-->
<!--        返回检测-->
<!--      </el-button>-->
<!--      <h1 class="main-title">等保测评结果</h1>-->

<!--      <div class="date-info">-->
<!--        <el-tag type="info"> </el-tag>-->
<!--      </div>-->
<!--    </div>-->

<!--    &lt;!&ndash; 控制按钮区域 &ndash;&gt;-->
<!--    <div class="control-section">-->
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

<!--      <div class="action-buttons">-->
<!--        &lt;!&ndash; 导出PDF按钮 &ndash;&gt;-->
<!--        <el-button-->
<!--            type="warning"-->
<!--            icon="el-icon-printer"-->
<!--            @click="exportPdf"-->
<!--            :loading="pdfExporting"-->
<!--            size="medium">-->
<!--          {{ pdfExporting ? '导出中...' : '导出PDF报告' }}-->
<!--        </el-button>-->

<!--        &lt;!&ndash; 保存评分按钮 &ndash;&gt;-->
<!--        <el-button-->
<!--            type="success"-->
<!--            icon="el-icon-check"-->
<!--            @click="saveScores"-->
<!--            :loading="saveLoading"-->
<!--            size="medium">-->
<!--          保存-->
<!--        </el-button>-->
<!--      </div>-->
<!--    </div>-->

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
<!--        <el-table-column prop="description" label="检测项" min-width="80"></el-table-column>-->
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
<!--            &lt;!&ndash;            <el-tag :type="scope.row.IsComply === 'true' ? 'success' : 'danger'">&ndash;&gt;-->
<!--            &lt;!&ndash;              {{ scope.row.IsComply === 'true' ? '通过' : '未通过' }}&ndash;&gt;-->
<!--            &lt;!&ndash;            </el-tag>&ndash;&gt;-->
<!--            <el-tag :type="getStatusType(scope.row.IsComply)">-->
<!--              {{ getStatusText(scope.row.IsComply) }}-->
<!--            </el-tag>-->
<!--          </template>-->
<!--        </el-table-column>-->
<!--        &lt;!&ndash;        <el-table-column label="是否通过检查" width="120">&ndash;&gt;-->
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

<!--  </div>-->
<!--</template>-->

<!--<script>-->
<!--import axios from 'axios';-->

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
<!--      saveLoading: false,-->
<!--      pdfExporting: false, // PDF导出状态-->
<!--      ip: '',-->
<!--      // 新增等保得分相关数据-->
<!--      protectionScore: {-->
<!--        totalScore: 0,-->
<!--        maxScore: 0,-->
<!--        scorePercentage: 0,-->
<!--        level: '',-->
<!--        categoryScores: []-->
<!--      }-->
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
<!--    // 获取状态对应的类型（用于el-tag的type属性）-->
<!--    getStatusType(status) {-->
<!--      switch(status) {-->
<!--        case 'true': return 'success';-->
<!--        case 'false': return 'danger';-->
<!--        case 'pending': return 'warning';-->
<!--        default: return 'info';-->
<!--      }-->
<!--    },-->

<!--    // 获取状态对应的文本-->
<!--    getStatusText(status) {-->
<!--      switch(status) {-->
<!--        case 'true': return '通过';-->
<!--        case 'false': return '未通过';-->
<!--        case 'pending': return '待检查';-->
<!--        default: return '未知';-->
<!--      }-->
<!--    },-->
<!--    // 获取检测结果函数-->
<!--    fetchAndDisplayChenckResults() {-->
<!--      const ip = this.$route.query.ip;-->
<!--      this.ip = this.$route.query.ip;-->
<!--      if (!ip) {-->
<!--        this.$message.error('无效的访问参数');-->
<!--        this.$router.push('/');-->
<!--        return;-->
<!--      }-->

<!--      this.tableLoading = true;-->
<!--      axios.get(`/api/level3TmpUserinfo?ip=${ip}`)-->
<!--          .then(response => {-->
<!--            this.checkresults = response.data.checkResults.map(item => {-->
<!--              let score = '0';-->
<!--              if (item.tmp_IsComply === 'true') {-->
<!--                score = '1';-->
<!--              } else if (item.tmp_IsComply === 'half_true') {-->
<!--                score = '0.5';-->
<!--              }-->
<!--              return {-->
<!--                ...item,-->
<!--                score: score,-->
<!--                importantLevel: item.tmp_importantLevel || '2'-->
<!--              };-->
<!--            });-->
<!--            this.tableLoading = false;-->
<!--          })-->
<!--          .catch(error => {-->
<!--            console.error('Error:', error);-->
<!--            this.tableLoading = false;-->
<!--            this.$message.error('获取检测结果失败，请重试');-->
<!--          });-->
<!--    },-->

<!--    // 新增：获取等保得分-->
<!--    async fetchProtectionScore() {-->
<!--      try {-->
<!--        const response = await axios.get(`/api/getLevel3Score?ip=${this.ip}`);-->
<!--        this.protectionScore = response.data;-->
<!--      } catch (error) {-->
<!--        console.error('获取等保得分失败:', error);-->
<!--        // 设置默认值-->
<!--        this.protectionScore = {-->
<!--          totalScore: 0,-->
<!--          maxScore: 100,-->
<!--          scorePercentage: 0,-->
<!--          level: '未评级',-->
<!--          categoryScores: []-->
<!--        };-->
<!--      }-->
<!--    },-->

<!--    saveScores() {-->
<!--      this.saveLoading = true;-->
<!--      const scoreMeasures = this.checkresults.map(item => ({-->
<!--        item_id: item.item_id,-->
<!--        importantLevelJson: item.importantLevel,-->
<!--        IsComplyLevel: item.score-->
<!--      }));-->

<!--      const requestData = {-->
<!--        ip: this.ip,-->
<!--        scoreMeasures: scoreMeasures-->
<!--      };-->

<!--      axios.post('/api/updateLevel3Protect', requestData)-->
<!--          .then(response => {-->
<!--            this.saveLoading = false;-->
<!--            this.$message.success(`成功更新${response.data.itemsUpdated}项评分结果`);-->
<!--          })-->
<!--          .catch(error => {-->
<!--            this.saveLoading = false;-->
<!--            console.error('保存评分失败:', error);-->
<!--            this.$message.error('保存评分失败，请重试');-->
<!--          });-->
<!--    },-->

<!--    goBack() {-->
<!--      this.$router.push('/classifyProtectHome');-->
<!--    },-->

<!--    // ==================== PDF导出功能 ====================-->

<!--    // 主导出函数-->
<!--    async exportPdf() {-->
<!--      if (!this.ip) {-->
<!--        this.$message.warning('缺少IP参数，无法导出');-->
<!--        return;-->
<!--      }-->

<!--      this.pdfExporting = true;-->

<!--      try {-->
<!--        // 获取等保得分数据-->
<!--        await this.fetchProtectionScore();-->

<!--        // 动态导入库-->
<!--        const jsPDF = (await import('jspdf')).default;-->
<!--        const html2canvas = (await import('html2canvas')).default;-->

<!--        // 创建临时的打印内容容器-->
<!--        const printContent = this.createPrintContent();-->
<!--        document.body.appendChild(printContent);-->

<!--        // 等待内容渲染完成-->
<!--        await this.$nextTick();-->
<!--        await new Promise(resolve => setTimeout(resolve, 1500));-->

<!--        // 转换为canvas-->
<!--        const canvas = await html2canvas(printContent, {-->
<!--          scale: 1.5,-->
<!--          useCORS: true,-->
<!--          allowTaint: true,-->
<!--          backgroundColor: '#ffffff',-->
<!--          width: printContent.scrollWidth,-->
<!--          height: printContent.scrollHeight,-->
<!--          scrollX: 0,-->
<!--          scrollY: 0,-->
<!--          windowWidth: printContent.scrollWidth,-->
<!--          windowHeight: printContent.scrollHeight-->
<!--        });-->

<!--        // 移除临时容器-->
<!--        document.body.removeChild(printContent);-->

<!--        // 创建PDF-->
<!--        const pdf = new jsPDF('p', 'mm', 'a4');-->
<!--        const pdfWidth = pdf.internal.pageSize.getWidth();-->
<!--        const pdfHeight = pdf.internal.pageSize.getHeight();-->

<!--        // 生成多页PDF-->
<!--        await this.createMultiPagePdf(pdf, canvas, pdfWidth, pdfHeight);-->

<!--        // 保存PDF-->
<!--        const fileName = `等保测评结果_${this.ip}_${new Date().toISOString().split('T')[0]}.pdf`;-->
<!--        pdf.save(fileName);-->

<!--        this.$message.success('PDF报告导出成功');-->

<!--      } catch (error) {-->
<!--        console.error('PDF导出失败:', error);-->
<!--        this.$message.error('PDF导出失败，请重试');-->
<!--      } finally {-->
<!--        this.pdfExporting = false;-->
<!--      }-->
<!--    },-->

<!--    // 创建打印内容-->
<!--    createPrintContent() {-->
<!--      const printDiv = document.createElement('div');-->
<!--      printDiv.style.cssText = `-->
<!--        position: absolute;-->
<!--        top: -10000px;-->
<!--        left: -10000px;-->
<!--        width: 800px;-->
<!--        background: white;-->
<!--        padding: 20px;-->
<!--        font-family: 'Microsoft YaHei', Arial, sans-serif;-->
<!--        line-height: 1.8;-->
<!--        color: #333;-->
<!--        box-sizing: border-box;-->
<!--        overflow: visible;-->
<!--      `;-->

<!--      printDiv.innerHTML = this.generatePrintHTML();-->

<!--      // 优化表格样式-->
<!--      const tables = printDiv.querySelectorAll('table');-->
<!--      tables.forEach(table => {-->
<!--        table.style.tableLayout = 'fixed';-->
<!--        table.style.width = '100%';-->
<!--        table.style.borderCollapse = 'collapse';-->
<!--        table.style.marginBottom = '20px';-->
<!--        table.style.pageBreakInside = 'avoid';-->

<!--        const cells = table.querySelectorAll('td, th');-->
<!--        cells.forEach(cell => {-->
<!--          cell.style.wordWrap = 'break-word';-->
<!--          cell.style.wordBreak = 'break-all';-->
<!--          cell.style.overflow = 'visible';-->
<!--          cell.style.whiteSpace = 'normal';-->
<!--          cell.style.padding = '8px';-->
<!--          cell.style.lineHeight = '1.6';-->
<!--        });-->
<!--      });-->

<!--      // 为每个主要区块添加分页控制-->
<!--      const sections = printDiv.querySelectorAll('div[style*="margin-bottom: 25px"]');-->
<!--      sections.forEach(section => {-->
<!--        section.style.pageBreakInside = 'avoid';-->
<!--        section.style.marginBottom = '30px';-->
<!--      });-->

<!--      return printDiv;-->
<!--    },-->

<!--    // 生成打印HTML内容-->
<!--    generatePrintHTML() {-->
<!--      return `-->
<!--        <div style="text-align: center; margin-bottom: 30px;">-->
<!--          <h1 style="color: #333; font-size: 24px; margin: 0;">等保测评结果报告</h1>-->
<!--          <p style="color: #666; margin: 10px 0;">资产IP：${this.ip}</p>-->
<!--          <p style="color: #666; margin: 10px 0;">生成时间：${new Date().toLocaleString()}</p>-->
<!--        </div>-->

<!--        ${this.generateDetailTableHTML()}-->
<!--        ${this.generateSignatureHTML()}-->
<!--      `;-->
<!--    },-->

<!--    // 生成详细表格HTML-->
<!--    generateDetailTableHTML() {-->
<!--      let html = `-->
<!--        <div style="margin-bottom: 25px;">-->
<!--          <h2 style="color: #409EFF; font-size: 18px; border-bottom: 2px solid #409EFF; padding-bottom: 5px;">检测详情</h2>-->
<!--          <table style="width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 11px;">-->
<!--            <thead>-->
<!--              <tr style="background: #f5f7fa;">-->
<!--                <th style="padding: 6px; border: 1px solid #ddd; text-align: center; width: 4%;">序号</th>-->
<!--                <th style="padding: 6px; border: 1px solid #ddd; text-align: center; width: 10%;">检测项</th>-->
<!--                <th style="padding: 6px; border: 1px solid #ddd; text-align: center; width: 6%;">重要程度</th>-->
<!--                <th style="padding: 6px; border: 1px solid #ddd; text-align: center; width: 15%;">基准</th>-->
<!--                <th style="padding: 6px; border: 1px solid #ddd; text-align: center; width: 15%;">检测结果</th>-->
<!--                <th style="padding: 6px; border: 1px solid #ddd; text-align: center; width: 7%;">是否通过</th>-->
<!--                <th style="padding: 6px; border: 1px solid #ddd; text-align: center; width: 8%;">等保要求符合度</th>-->
<!--                <th style="padding: 6px; border: 1px solid #ddd; text-align: center; width: 15%;">修改建议</th>-->
<!--                <th style="padding: 6px; border: 1px solid #ddd; text-align: center; width: 8%;">检测时间</th>-->
<!--              </tr>-->
<!--            </thead>-->
<!--            <tbody>-->
<!--      `;-->

<!--      this.checkresults.forEach((item, index) => {-->
<!--        let statusText, statusColor;-->
<!--        switch(item.IsComply) {-->
<!--          case 'true':-->
<!--            statusText = '通过';-->
<!--            statusColor = '#67C23A';  // 绿色-->
<!--            break;-->
<!--          case 'false':-->
<!--            statusText = '未通过';-->
<!--            statusColor = '#F56C6C';  // 红色-->
<!--            break;-->
<!--          case 'pending':-->
<!--            statusText = '待检查';-->
<!--            statusColor = '#E6A23C';  // 橙色-->
<!--            break;-->
<!--          default:-->
<!--            statusText = '未知';-->
<!--            statusColor = '#909399';  // 灰色-->
<!--            break;-->
<!--        }-->
<!--        // const statusColor = item.IsComply === 'true' ? '#67C23A' : '#F56C6C';-->
<!--        // const statusText = item.IsComply === 'true' ? '通过' : '未通过';-->
<!--        const scoreText = this.getScoreText(item.score);-->
<!--        const scoreColor = item.score === '1' ? '#67C23A' : item.score === '0.5' ? '#E6A23C' : '#F56C6C';-->
<!--        const suggestion = item.IsComply === 'false' ? (item.recommend || '-') : '-';-->

<!--        html += `-->
<!--          <tr>-->
<!--            <td style="padding: 5px; border: 1px solid #ddd; text-align: center;">${index + 1}</td>-->
<!--            <td style="padding: 5px; border: 1px solid #ddd; font-size: 10px;">${item.description || '-'}</td>-->
<!--            <td style="padding: 5px; border: 1px solid #ddd; text-align: center;">${item.importantLevel || '2'}</td>-->
<!--            <td style="padding: 5px; border: 1px solid #ddd; font-size: 10px;">${item.basis || '-'}</td>-->
<!--            <td style="padding: 5px; border: 1px solid #ddd; font-size: 10px;">${item.result || '-'}</td>-->
<!--            <td style="padding: 5px; border: 1px solid #ddd; text-align: center; color: ${statusColor}; font-weight: bold;">${statusText}</td>-->
<!--            <td style="padding: 5px; border: 1px solid #ddd; text-align: center; color: ${scoreColor}; font-weight: bold;">${scoreText}</td>-->
<!--            <td style="padding: 5px; border: 1px solid #ddd; font-size: 10px;">${suggestion}</td>-->
<!--            <td style="padding: 5px; border: 1px solid #ddd; font-size: 9px; text-align: center;">${item.check_time || '-'}</td>-->
<!--          </tr>-->
<!--        `;-->
<!--      });-->

<!--      html += `-->
<!--            </tbody>-->
<!--          </table>-->
<!--        </div>-->
<!--      `;-->

<!--      return html;-->
<!--    },-->

<!--    // 新增：生成签名区域HTML-->
<!--    generateSignatureHTML() {-->
<!--      return `-->
<!--        <div style="margin-top: 40px; margin-bottom: 30px;">-->
<!--          <div style="display: flex; justify-content: space-between; align-items: flex-end; width: 100%;">-->
<!--            <div style="flex: 1;">-->
<!--              <p style="margin: 0; font-size: 14px; line-height: 2;">检测人员签名：____________________________</p>-->
<!--            </div>-->
<!--            <div style="flex: 1; text-align: right;">-->
<!--              <p style="margin: 0; font-size: 14px; line-height: 2;">时间：____________________________</p>-->
<!--            </div>-->
<!--          </div>-->
<!--        </div>-->
<!--      `;-->
<!--    },-->

<!--    // 智能分页算法-->
<!--    findOptimalBreakPoint(canvas, startY, maxHeight, canvasWidth) {-->
<!--      const ctx = canvas.getContext('2d');-->
<!--      const imageData = ctx.getImageData(0, startY, canvasWidth, maxHeight);-->
<!--      const data = imageData.data;-->

<!--      const minHeight = Math.max(50, maxHeight * 0.7);-->

<!--      for (let y = Math.floor(maxHeight) - 1; y >= minHeight; y&#45;&#45;) {-->
<!--        if (this.isTableRowBoundary(data, y, canvasWidth, maxHeight)) {-->
<!--          return y;-->
<!--        }-->

<!--        if (this.isRowEmpty(data, y, canvasWidth)) {-->
<!--          let emptyRowCount = 0;-->
<!--          for (let checkY = y; checkY >= Math.max(0, y - 10) && checkY < maxHeight; checkY&#45;&#45;) {-->
<!--            if (this.isRowEmpty(data, checkY, canvasWidth)) {-->
<!--              emptyRowCount++;-->
<!--            } else {-->
<!--              break;-->
<!--            }-->
<!--          }-->

<!--          if (emptyRowCount >= 3) {-->
<!--            return y - emptyRowCount + 1;-->
<!--          }-->
<!--        }-->
<!--      }-->

<!--      for (let y = Math.floor(maxHeight) - 20; y >= minHeight; y&#45;&#45;) {-->
<!--        if (this.isSafeBreakPoint(data, y, canvasWidth, maxHeight)) {-->
<!--          return y;-->
<!--        }-->
<!--      }-->

<!--      return Math.floor(maxHeight * 0.9);-->
<!--    },-->

<!--    isTableRowBoundary(imageData, rowIndex, width, maxHeight) {-->
<!--      const checkRange = 3;-->
<!--      const currentRowBorderPixels = this.countBorderPixels(imageData, rowIndex, width);-->

<!--      let aboveBorderCount = 0;-->
<!--      for (let i = 1; i <= checkRange; i++) {-->
<!--        const checkY = rowIndex - i;-->
<!--        if (checkY >= 0) {-->
<!--          const borderPixels = this.countBorderPixels(imageData, checkY, width);-->
<!--          if (borderPixels > width * 0.1) {-->
<!--            aboveBorderCount++;-->
<!--          }-->
<!--        }-->
<!--      }-->

<!--      let belowBorderCount = 0;-->
<!--      for (let i = 1; i <= checkRange; i++) {-->
<!--        const checkY = rowIndex + i;-->
<!--        if (checkY < maxHeight) {-->
<!--          const borderPixels = this.countBorderPixels(imageData, checkY, width);-->
<!--          if (borderPixels > width * 0.1) {-->
<!--            belowBorderCount++;-->
<!--          }-->
<!--        }-->
<!--      }-->

<!--      return currentRowBorderPixels > width * 0.15 &&-->
<!--          aboveBorderCount <= 1 &&-->
<!--          belowBorderCount <= 1;-->
<!--    },-->

<!--    countBorderPixels(imageData, rowIndex, width) {-->
<!--      const rowStart = rowIndex * width * 4;-->
<!--      const rowEnd = rowStart + width * 4;-->
<!--      let borderPixels = 0;-->

<!--      for (let i = rowStart; i < rowEnd; i += 4) {-->
<!--        const r = imageData[i];-->
<!--        const g = imageData[i + 1];-->
<!--        const b = imageData[i + 2];-->

<!--        if ((r < 100 && g < 100 && b < 100) ||-->
<!--            (Math.abs(r - 221) < 10 && Math.abs(g - 221) < 10 && Math.abs(b - 221) < 10)) {-->
<!--          borderPixels++;-->
<!--        }-->
<!--      }-->

<!--      return borderPixels;-->
<!--    },-->

<!--    isSafeBreakPoint(imageData, rowIndex, width, maxHeight) {-->
<!--      const checkRange = 5;-->
<!--      let totalContentPixels = 0;-->
<!--      let totalPixels = 0;-->

<!--      for (let y = Math.max(0, rowIndex - checkRange);-->
<!--           y <= Math.min(maxHeight - 1, rowIndex + checkRange); y++) {-->
<!--        const rowStart = y * width * 4;-->
<!--        const rowEnd = rowStart + width * 4;-->

<!--        for (let i = rowStart; i < rowEnd; i += 4) {-->
<!--          const r = imageData[i];-->
<!--          const g = imageData[i + 1];-->
<!--          const b = imageData[i + 2];-->

<!--          totalPixels++;-->

<!--          if (r < 250 || g < 250 || b < 250) {-->
<!--            totalContentPixels++;-->
<!--          }-->
<!--        }-->
<!--      }-->

<!--      const contentDensity = totalContentPixels / totalPixels;-->
<!--      return contentDensity < 0.05;-->
<!--    },-->

<!--    isRowEmpty(imageData, rowIndex, width) {-->
<!--      const rowStart = rowIndex * width * 4;-->
<!--      const rowEnd = rowStart + width * 4;-->

<!--      for (let i = rowStart; i < rowEnd; i += 4) {-->
<!--        const r = imageData[i];-->
<!--        const g = imageData[i + 1];-->
<!--        const b = imageData[i + 2];-->

<!--        if (r < 250 || g < 250 || b < 250) {-->
<!--          return false;-->
<!--        }-->
<!--      }-->
<!--      return true;-->
<!--    },-->

<!--    // 创建多页PDF-->
<!--    async createMultiPagePdf(pdf, canvas, pdfWidth, pdfHeight) {-->
<!--      const imgWidth = canvas.width;-->
<!--      const imgHeight = canvas.height;-->

<!--      const pageHeight = pdfHeight - 50;-->
<!--      const ratio = pdfWidth / imgWidth;-->
<!--      const scaledWidth = pdfWidth;-->
<!--      const scaledHeight = imgHeight * ratio;-->

<!--      const pixelRatio = scaledHeight / imgHeight;-->
<!--      const pageHeightInPixels = pageHeight / pixelRatio;-->

<!--      let currentY = 0;-->
<!--      let pageIndex = 0;-->
<!--      const pages = [];-->

<!--      while (currentY < imgHeight) {-->
<!--        if (pageIndex > 0) {-->
<!--          pdf.addPage();-->
<!--        }-->

<!--        let remainingHeight = imgHeight - currentY;-->
<!--        let currentPageContentHeight = Math.min(pageHeightInPixels, remainingHeight);-->

<!--        if (remainingHeight > pageHeightInPixels) {-->
<!--          const optimalHeight = this.findOptimalBreakPoint(-->
<!--              canvas,-->
<!--              currentY,-->
<!--              currentPageContentHeight,-->
<!--              imgWidth-->
<!--          );-->

<!--          if (optimalHeight > pageHeightInPixels * 0.5) {-->
<!--            currentPageContentHeight = optimalHeight;-->
<!--          }-->
<!--        }-->

<!--        const pageCanvas = document.createElement('canvas');-->
<!--        const pageCtx = pageCanvas.getContext('2d');-->

<!--        pageCanvas.width = imgWidth;-->
<!--        pageCanvas.height = currentPageContentHeight;-->

<!--        pageCtx.fillStyle = '#ffffff';-->
<!--        pageCtx.fillRect(0, 0, imgWidth, currentPageContentHeight);-->

<!--        pageCtx.drawImage(-->
<!--            canvas,-->
<!--            0, currentY, imgWidth, currentPageContentHeight,-->
<!--            0, 0, imgWidth, currentPageContentHeight-->
<!--        );-->

<!--        const pageImgData = pageCanvas.toDataURL('image/png');-->
<!--        const pageScaledHeight = currentPageContentHeight * pixelRatio;-->

<!--        pdf.addImage(-->
<!--            pageImgData,-->
<!--            'PNG',-->
<!--            0,-->
<!--            25,-->
<!--            scaledWidth,-->
<!--            pageScaledHeight-->
<!--        );-->

<!--        pages.push({-->
<!--          pageNumber: pageIndex + 1,-->
<!--          scaledHeight: pageScaledHeight-->
<!--        });-->

<!--        currentY += currentPageContentHeight;-->
<!--        pageIndex++;-->

<!--        if (pageIndex > 50) {-->
<!--          console.warn('PDF页数过多，强制结束');-->
<!--          break;-->
<!--        }-->
<!--      }-->

<!--      const totalPages = pageIndex;-->

<!--      // 添加页码-->
<!--      for (let i = 0; i < totalPages; i++) {-->
<!--        pdf.setPage(i + 1);-->
<!--        pdf.setFontSize(10);-->
<!--        pdf.setTextColor(102, 102, 102);-->

<!--        const pageText = `${i + 1}/${totalPages}`;-->
<!--        const textWidth = pdf.getTextWidth(pageText);-->
<!--        const xPosition = (pdfWidth - textWidth) / 2;-->
<!--        const yPosition = pdfHeight - 15;-->

<!--        pdf.text(pageText, xPosition, yPosition);-->
<!--      }-->
<!--    }-->
<!--  },-->
<!--  mounted() {-->
<!--    this.fetchAndDisplayChenckResults();-->
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

<!--.header-section > div {-->
<!--  display: flex;-->
<!--  align-items: center;-->
<!--  gap: 10px;-->
<!--}-->

<!--.main-title {-->
<!--  color: #303133;-->
<!--  font-size: 24px;-->
<!--  font-weight: bold;-->
<!--  margin: 0 !important;-->
<!--}-->

<!--.control-section {-->
<!--  display: flex;-->
<!--  justify-content: space-between;-->
<!--  align-items: center;-->
<!--  margin-bottom: 20px;-->
<!--  flex-wrap: wrap;-->
<!--  gap: 15px;-->
<!--}-->

<!--.filter-group {-->
<!--  display: flex;-->
<!--  gap: 10px;-->
<!--}-->

<!--.filter-group .el-input {-->
<!--  width: 250px;-->
<!--}-->

<!--.action-buttons {-->
<!--  display: flex;-->
<!--  gap: 10px;-->
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

<!--.server1 .el-col p {-->
<!--  font-size: 16px;-->
<!--  white-space: pre-wrap;-->
<!--  line-height: 1.6;-->
<!--  margin-bottom: 5px;-->
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

<!--  .action-buttons {-->
<!--    width: 100%;-->
<!--    justify-content: flex-end;-->
<!--  }-->
<!--}-->
<!--</style>-->

<!--<template>-->
<!--  <div class="baseline-container">-->
<!--    &lt;!&ndash; 头部区域 &ndash;&gt;-->
<!--    <div class="header-section">-->
<!--      <el-button-->
<!--          type="primary"-->
<!--          icon="el-icon-arrow-left"-->
<!--          @click="goBack"-->
<!--          size="mini"-->
<!--          style="margin-left:10px">-->
<!--        返回检测-->
<!--      </el-button>-->
<!--      <h1 class="main-title">等保测评结果</h1>-->

<!--      <div class="date-info">-->
<!--        <el-tag type="info"> </el-tag>-->
<!--      </div>-->
<!--    </div>-->

<!--    &lt;!&ndash; 控制按钮区域 &ndash;&gt;-->
<!--    <div class="control-section">-->
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

<!--      <div class="action-buttons">-->
<!--        &lt;!&ndash; 导出PDF按钮 &ndash;&gt;-->
<!--        <el-button-->
<!--            type="warning"-->
<!--            icon="el-icon-printer"-->
<!--            @click="exportPdf"-->
<!--            :loading="pdfExporting"-->
<!--            size="medium">-->
<!--          {{ pdfExporting ? '导出中...' : '导出PDF报告' }}-->
<!--        </el-button>-->

<!--        &lt;!&ndash; 保存评分按钮 &ndash;&gt;-->
<!--        <el-button-->
<!--            type="success"-->
<!--            icon="el-icon-check"-->
<!--            @click="saveScores"-->
<!--            :loading="saveLoading"-->
<!--            size="medium">-->
<!--          保存-->
<!--        </el-button>-->
<!--      </div>-->
<!--    </div>-->

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
<!--        <el-table-column prop="description" label="检测项" min-width="80"></el-table-column>-->
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
<!--        <el-table-column prop="check_time" label="检测时间" min-width="150"></el-table-column>-->
<!--      </el-table>-->
<!--    </el-card>-->

<!--  </div>-->
<!--</template>-->

<!--<script>-->
<!--import axios from 'axios';-->

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
<!--      saveLoading: false,-->
<!--      pdfExporting: false, // PDF导出状态-->
<!--      ip: '',-->
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
<!--    // 获取检测结果函数-->
<!--    fetchAndDisplayChenckResults() {-->
<!--      const ip = this.$route.query.ip;-->
<!--      this.ip = this.$route.query.ip;-->
<!--      if (!ip) {-->
<!--        this.$message.error('无效的访问参数');-->
<!--        this.$router.push('/');-->
<!--        return;-->
<!--      }-->

<!--      this.tableLoading = true;-->
<!--      axios.get(`/api/level3TmpUserinfo?ip=${ip}`)-->
<!--          .then(response => {-->
<!--            this.checkresults = response.data.checkResults.map(item => {-->
<!--              let score = '0';-->
<!--              if (item.tmp_IsComply === 'true') {-->
<!--                score = '1';-->
<!--              } else if (item.tmp_IsComply === 'half_true') {-->
<!--                score = '0.5';-->
<!--              }-->
<!--              return {-->
<!--                ...item,-->
<!--                score: score,-->
<!--                importantLevel: item.tmp_importantLevel || '2'-->
<!--              };-->
<!--            });-->
<!--            this.tableLoading = false;-->
<!--          })-->
<!--          .catch(error => {-->
<!--            console.error('Error:', error);-->
<!--            this.tableLoading = false;-->
<!--            this.$message.error('获取检测结果失败，请重试');-->
<!--          });-->
<!--    },-->

<!--    saveScores() {-->
<!--      this.saveLoading = true;-->
<!--      const scoreMeasures = this.checkresults.map(item => ({-->
<!--        item_id: item.item_id,-->
<!--        importantLevelJson: item.importantLevel,-->
<!--        IsComplyLevel: item.score-->
<!--      }));-->

<!--      const requestData = {-->
<!--        ip: this.ip,-->
<!--        scoreMeasures: scoreMeasures-->
<!--      };-->

<!--      axios.post('/api/updateLevel3Protect', requestData)-->
<!--          .then(response => {-->
<!--            this.saveLoading = false;-->
<!--            this.$message.success(`成功更新${response.data.itemsUpdated}项评分结果`);-->
<!--          })-->
<!--          .catch(error => {-->
<!--            this.saveLoading = false;-->
<!--            console.error('保存评分失败:', error);-->
<!--            this.$message.error('保存评分失败，请重试');-->
<!--          });-->
<!--    },-->

<!--    goBack() {-->
<!--      this.$router.push('/classifyProtectHome');-->
<!--    },-->

<!--    // ==================== PDF导出功能 ====================-->

<!--    // 主导出函数-->
<!--    async exportPdf() {-->
<!--      if (!this.ip) {-->
<!--        this.$message.warning('缺少IP参数，无法导出');-->
<!--        return;-->
<!--      }-->

<!--      this.pdfExporting = true;-->

<!--      try {-->
<!--        // 动态导入库-->
<!--        const jsPDF = (await import('jspdf')).default;-->
<!--        const html2canvas = (await import('html2canvas')).default;-->

<!--        // 创建临时的打印内容容器-->
<!--        const printContent = this.createPrintContent();-->
<!--        document.body.appendChild(printContent);-->

<!--        // 等待内容渲染完成-->
<!--        await this.$nextTick();-->
<!--        await new Promise(resolve => setTimeout(resolve, 1500));-->

<!--        // 转换为canvas-->
<!--        const canvas = await html2canvas(printContent, {-->
<!--          scale: 1.5,-->
<!--          useCORS: true,-->
<!--          allowTaint: true,-->
<!--          backgroundColor: '#ffffff',-->
<!--          width: printContent.scrollWidth,-->
<!--          height: printContent.scrollHeight,-->
<!--          scrollX: 0,-->
<!--          scrollY: 0,-->
<!--          windowWidth: printContent.scrollWidth,-->
<!--          windowHeight: printContent.scrollHeight-->
<!--        });-->

<!--        // 移除临时容器-->
<!--        document.body.removeChild(printContent);-->

<!--        // 创建PDF-->
<!--        const pdf = new jsPDF('p', 'mm', 'a4');-->
<!--        const pdfWidth = pdf.internal.pageSize.getWidth();-->
<!--        const pdfHeight = pdf.internal.pageSize.getHeight();-->

<!--        // 生成多页PDF-->
<!--        await this.createMultiPagePdf(pdf, canvas, pdfWidth, pdfHeight);-->

<!--        // 保存PDF-->
<!--        const fileName = `等保测评结果_${this.ip}_${new Date().toISOString().split('T')[0]}.pdf`;-->
<!--        pdf.save(fileName);-->

<!--        this.$message.success('PDF报告导出成功');-->

<!--      } catch (error) {-->
<!--        console.error('PDF导出失败:', error);-->
<!--        this.$message.error('PDF导出失败，请重试');-->
<!--      } finally {-->
<!--        this.pdfExporting = false;-->
<!--      }-->
<!--    },-->

<!--    // 创建打印内容-->
<!--    createPrintContent() {-->
<!--      const printDiv = document.createElement('div');-->
<!--      printDiv.style.cssText = `-->
<!--        position: absolute;-->
<!--        top: -10000px;-->
<!--        left: -10000px;-->
<!--        width: 800px;-->
<!--        background: white;-->
<!--        padding: 20px;-->
<!--        font-family: 'Microsoft YaHei', Arial, sans-serif;-->
<!--        line-height: 1.8;-->
<!--        color: #333;-->
<!--        box-sizing: border-box;-->
<!--        overflow: visible;-->
<!--      `;-->

<!--      printDiv.innerHTML = this.generatePrintHTML();-->

<!--      // 优化表格样式-->
<!--      const tables = printDiv.querySelectorAll('table');-->
<!--      tables.forEach(table => {-->
<!--        table.style.tableLayout = 'fixed';-->
<!--        table.style.width = '100%';-->
<!--        table.style.borderCollapse = 'collapse';-->
<!--        table.style.marginBottom = '20px';-->
<!--        table.style.pageBreakInside = 'avoid';-->

<!--        const cells = table.querySelectorAll('td, th');-->
<!--        cells.forEach(cell => {-->
<!--          cell.style.wordWrap = 'break-word';-->
<!--          cell.style.wordBreak = 'break-all';-->
<!--          cell.style.overflow = 'visible';-->
<!--          cell.style.whiteSpace = 'normal';-->
<!--          cell.style.padding = '8px';-->
<!--          cell.style.lineHeight = '1.6';-->
<!--        });-->
<!--      });-->

<!--      // 为每个主要区块添加分页控制-->
<!--      const sections = printDiv.querySelectorAll('div[style*="margin-bottom: 25px"]');-->
<!--      sections.forEach(section => {-->
<!--        section.style.pageBreakInside = 'avoid';-->
<!--        section.style.marginBottom = '30px';-->
<!--      });-->

<!--      return printDiv;-->
<!--    },-->

<!--    // 生成打印HTML内容-->
<!--    generatePrintHTML() {-->
<!--      return `-->
<!--        <div style="text-align: center; margin-bottom: 30px;">-->
<!--          <h1 style="color: #333; font-size: 24px; margin: 0;">等保测评结果报告</h1>-->
<!--          <p style="color: #666; margin: 10px 0;">资产IP：${this.ip}</p>-->
<!--          <p style="color: #666; margin: 10px 0;">生成时间：${new Date().toLocaleString()}</p>-->
<!--        </div>-->

<!--        ${this.generateSummaryHTML()}-->
<!--        ${this.generateDetailTableHTML()}-->
<!--      `;-->
<!--    },-->

<!--    // 生成汇总信息HTML-->
<!--    generateSummaryHTML() {-->
<!--      return `-->
<!--        <div style="margin-bottom: 25px;">-->
<!--          <h2 style="color: #409EFF; font-size: 18px; border-bottom: 2px solid #409EFF; padding-bottom: 5px;">检测汇总</h2>-->
<!--          <table style="width: 100%; border-collapse: collapse; margin-top: 10px;">-->
<!--            <tr>-->
<!--              <td style="padding: 12px; border: 1px solid #ddd; background: #f5f7fa; width: 25%; font-weight: bold; text-align: center;">总检测项数</td>-->
<!--              <td style="padding: 12px; border: 1px solid #ddd; width: 25%; text-align: center;">${this.totalCount}</td>-->
<!--              <td style="padding: 12px; border: 1px solid #ddd; background: #f5f7fa; width: 25%; font-weight: bold; text-align: center;">通过项数</td>-->
<!--              <td style="padding: 12px; border: 1px solid #ddd; width: 25%; text-align: center; color: #67C23A; font-weight: bold;">${this.passedCount}</td>-->
<!--            </tr>-->
<!--            <tr>-->
<!--              <td style="padding: 12px; border: 1px solid #ddd; background: #f5f7fa; font-weight: bold; text-align: center;">未通过项数</td>-->
<!--              <td style="padding: 12px; border: 1px solid #ddd; text-align: center; color: #F56C6C; font-weight: bold;">${this.failedCount}</td>-->
<!--              <td style="padding: 12px; border: 1px solid #ddd; background: #f5f7fa; font-weight: bold; text-align: center;">通过率</td>-->
<!--              <td style="padding: 12px; border: 1px solid #ddd; text-align: center; font-weight: bold;">${this.totalCount > 0 ? ((this.passedCount / this.totalCount) * 100).toFixed(1) + '%' : '0%'}</td>-->
<!--            </tr>-->
<!--          </table>-->
<!--        </div>-->
<!--      `;-->
<!--    },-->

<!--    // 生成详细表格HTML-->
<!--    generateDetailTableHTML() {-->
<!--      let html = `-->
<!--        <div style="margin-bottom: 25px;">-->
<!--          <h2 style="color: #409EFF; font-size: 18px; border-bottom: 2px solid #409EFF; padding-bottom: 5px;">检测详情</h2>-->
<!--          <table style="width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 11px;">-->
<!--            <thead>-->
<!--              <tr style="background: #f5f7fa;">-->
<!--                <th style="padding: 6px; border: 1px solid #ddd; text-align: center; width: 4%;">序号</th>-->
<!--                <th style="padding: 6px; border: 1px solid #ddd; text-align: center; width: 20%;">检测项</th>-->
<!--                <th style="padding: 6px; border: 1px solid #ddd; text-align: center; width: 6%;">重要程度</th>-->
<!--                <th style="padding: 6px; border: 1px solid #ddd; text-align: center; width: 15%;">基准</th>-->
<!--                <th style="padding: 6px; border: 1px solid #ddd; text-align: center; width: 15%;">检测结果</th>-->
<!--                <th style="padding: 6px; border: 1px solid #ddd; text-align: center; width: 7%;">是否通过</th>-->
<!--                <th style="padding: 6px; border: 1px solid #ddd; text-align: center; width: 8%;">等保要求符合度</th>-->
<!--                <th style="padding: 6px; border: 1px solid #ddd; text-align: center; width: 15%;">修改建议</th>-->
<!--                <th style="padding: 6px; border: 1px solid #ddd; text-align: center; width: 10%;">检测时间</th>-->
<!--              </tr>-->
<!--            </thead>-->
<!--            <tbody>-->
<!--      `;-->

<!--      this.checkresults.forEach((item, index) => {-->
<!--        const statusColor = item.IsComply === 'true' ? '#67C23A' : '#F56C6C';-->
<!--        const statusText = item.IsComply === 'true' ? '通过' : '未通过';-->
<!--        const scoreText = this.getScoreText(item.score);-->
<!--        const scoreColor = item.score === '1' ? '#67C23A' : item.score === '0.5' ? '#E6A23C' : '#F56C6C';-->
<!--        const suggestion = item.IsComply === 'false' ? (item.recommend || '-') : '-';-->

<!--        html += `-->
<!--          <tr>-->
<!--            <td style="padding: 5px; border: 1px solid #ddd; text-align: center;">${index + 1}</td>-->
<!--            <td style="padding: 5px; border: 1px solid #ddd; font-size: 10px;">${item.description || '-'}</td>-->
<!--            <td style="padding: 5px; border: 1px solid #ddd; text-align: center;">${item.importantLevel || '2'}</td>-->
<!--            <td style="padding: 5px; border: 1px solid #ddd; font-size: 10px;">${item.basis || '-'}</td>-->
<!--            <td style="padding: 5px; border: 1px solid #ddd; font-size: 10px;">${item.result || '-'}</td>-->
<!--            <td style="padding: 5px; border: 1px solid #ddd; text-align: center; color: ${statusColor}; font-weight: bold;">${statusText}</td>-->
<!--            <td style="padding: 5px; border: 1px solid #ddd; text-align: center; color: ${scoreColor}; font-weight: bold;">${scoreText}</td>-->
<!--            <td style="padding: 5px; border: 1px solid #ddd; font-size: 10px;">${suggestion}</td>-->
<!--            <td style="padding: 5px; border: 1px solid #ddd; font-size: 9px; text-align: center;">${item.check_time || '-'}</td>-->
<!--          </tr>-->
<!--        `;-->
<!--      });-->

<!--      html += `-->
<!--            </tbody>-->
<!--          </table>-->
<!--        </div>-->
<!--      `;-->

<!--      return html;-->
<!--    },-->

<!--    // 智能分页算法-->
<!--    findOptimalBreakPoint(canvas, startY, maxHeight, canvasWidth) {-->
<!--      const ctx = canvas.getContext('2d');-->
<!--      const imageData = ctx.getImageData(0, startY, canvasWidth, maxHeight);-->
<!--      const data = imageData.data;-->

<!--      const minHeight = Math.max(50, maxHeight * 0.7);-->

<!--      for (let y = Math.floor(maxHeight) - 1; y >= minHeight; y&#45;&#45;) {-->
<!--        if (this.isTableRowBoundary(data, y, canvasWidth, maxHeight)) {-->
<!--          return y;-->
<!--        }-->

<!--        if (this.isRowEmpty(data, y, canvasWidth)) {-->
<!--          let emptyRowCount = 0;-->
<!--          for (let checkY = y; checkY >= Math.max(0, y - 10) && checkY < maxHeight; checkY&#45;&#45;) {-->
<!--            if (this.isRowEmpty(data, checkY, canvasWidth)) {-->
<!--              emptyRowCount++;-->
<!--            } else {-->
<!--              break;-->
<!--            }-->
<!--          }-->

<!--          if (emptyRowCount >= 3) {-->
<!--            return y - emptyRowCount + 1;-->
<!--          }-->
<!--        }-->
<!--      }-->

<!--      for (let y = Math.floor(maxHeight) - 20; y >= minHeight; y&#45;&#45;) {-->
<!--        if (this.isSafeBreakPoint(data, y, canvasWidth, maxHeight)) {-->
<!--          return y;-->
<!--        }-->
<!--      }-->

<!--      return Math.floor(maxHeight * 0.9);-->
<!--    },-->

<!--    isTableRowBoundary(imageData, rowIndex, width, maxHeight) {-->
<!--      const checkRange = 3;-->
<!--      const currentRowBorderPixels = this.countBorderPixels(imageData, rowIndex, width);-->

<!--      let aboveBorderCount = 0;-->
<!--      for (let i = 1; i <= checkRange; i++) {-->
<!--        const checkY = rowIndex - i;-->
<!--        if (checkY >= 0) {-->
<!--          const borderPixels = this.countBorderPixels(imageData, checkY, width);-->
<!--          if (borderPixels > width * 0.1) {-->
<!--            aboveBorderCount++;-->
<!--          }-->
<!--        }-->
<!--      }-->

<!--      let belowBorderCount = 0;-->
<!--      for (let i = 1; i <= checkRange; i++) {-->
<!--        const checkY = rowIndex + i;-->
<!--        if (checkY < maxHeight) {-->
<!--          const borderPixels = this.countBorderPixels(imageData, checkY, width);-->
<!--          if (borderPixels > width * 0.1) {-->
<!--            belowBorderCount++;-->
<!--          }-->
<!--        }-->
<!--      }-->

<!--      return currentRowBorderPixels > width * 0.15 &&-->
<!--          aboveBorderCount <= 1 &&-->
<!--          belowBorderCount <= 1;-->
<!--    },-->

<!--    countBorderPixels(imageData, rowIndex, width) {-->
<!--      const rowStart = rowIndex * width * 4;-->
<!--      const rowEnd = rowStart + width * 4;-->
<!--      let borderPixels = 0;-->

<!--      for (let i = rowStart; i < rowEnd; i += 4) {-->
<!--        const r = imageData[i];-->
<!--        const g = imageData[i + 1];-->
<!--        const b = imageData[i + 2];-->

<!--        if ((r < 100 && g < 100 && b < 100) ||-->
<!--            (Math.abs(r - 221) < 10 && Math.abs(g - 221) < 10 && Math.abs(b - 221) < 10)) {-->
<!--          borderPixels++;-->
<!--        }-->
<!--      }-->

<!--      return borderPixels;-->
<!--    },-->

<!--    isSafeBreakPoint(imageData, rowIndex, width, maxHeight) {-->
<!--      const checkRange = 5;-->
<!--      let totalContentPixels = 0;-->
<!--      let totalPixels = 0;-->

<!--      for (let y = Math.max(0, rowIndex - checkRange);-->
<!--           y <= Math.min(maxHeight - 1, rowIndex + checkRange); y++) {-->
<!--        const rowStart = y * width * 4;-->
<!--        const rowEnd = rowStart + width * 4;-->

<!--        for (let i = rowStart; i < rowEnd; i += 4) {-->
<!--          const r = imageData[i];-->
<!--          const g = imageData[i + 1];-->
<!--          const b = imageData[i + 2];-->

<!--          totalPixels++;-->

<!--          if (r < 250 || g < 250 || b < 250) {-->
<!--            totalContentPixels++;-->
<!--          }-->
<!--        }-->
<!--      }-->

<!--      const contentDensity = totalContentPixels / totalPixels;-->
<!--      return contentDensity < 0.05;-->
<!--    },-->

<!--    isRowEmpty(imageData, rowIndex, width) {-->
<!--      const rowStart = rowIndex * width * 4;-->
<!--      const rowEnd = rowStart + width * 4;-->

<!--      for (let i = rowStart; i < rowEnd; i += 4) {-->
<!--        const r = imageData[i];-->
<!--        const g = imageData[i + 1];-->
<!--        const b = imageData[i + 2];-->

<!--        if (r < 250 || g < 250 || b < 250) {-->
<!--          return false;-->
<!--        }-->
<!--      }-->
<!--      return true;-->
<!--    },-->

<!--    // 创建多页PDF-->
<!--    async createMultiPagePdf(pdf, canvas, pdfWidth, pdfHeight) {-->
<!--      const imgWidth = canvas.width;-->
<!--      const imgHeight = canvas.height;-->

<!--      const pageHeight = pdfHeight - 50;-->
<!--      const ratio = pdfWidth / imgWidth;-->
<!--      const scaledWidth = pdfWidth;-->
<!--      const scaledHeight = imgHeight * ratio;-->

<!--      const pixelRatio = scaledHeight / imgHeight;-->
<!--      const pageHeightInPixels = pageHeight / pixelRatio;-->

<!--      let currentY = 0;-->
<!--      let pageIndex = 0;-->
<!--      const pages = [];-->

<!--      while (currentY < imgHeight) {-->
<!--        if (pageIndex > 0) {-->
<!--          pdf.addPage();-->
<!--        }-->

<!--        let remainingHeight = imgHeight - currentY;-->
<!--        let currentPageContentHeight = Math.min(pageHeightInPixels, remainingHeight);-->

<!--        if (remainingHeight > pageHeightInPixels) {-->
<!--          const optimalHeight = this.findOptimalBreakPoint(-->
<!--              canvas,-->
<!--              currentY,-->
<!--              currentPageContentHeight,-->
<!--              imgWidth-->
<!--          );-->

<!--          if (optimalHeight > pageHeightInPixels * 0.5) {-->
<!--            currentPageContentHeight = optimalHeight;-->
<!--          }-->
<!--        }-->

<!--        const pageCanvas = document.createElement('canvas');-->
<!--        const pageCtx = pageCanvas.getContext('2d');-->

<!--        pageCanvas.width = imgWidth;-->
<!--        pageCanvas.height = currentPageContentHeight;-->

<!--        pageCtx.fillStyle = '#ffffff';-->
<!--        pageCtx.fillRect(0, 0, imgWidth, currentPageContentHeight);-->

<!--        pageCtx.drawImage(-->
<!--            canvas,-->
<!--            0, currentY, imgWidth, currentPageContentHeight,-->
<!--            0, 0, imgWidth, currentPageContentHeight-->
<!--        );-->

<!--        const pageImgData = pageCanvas.toDataURL('image/png');-->
<!--        const pageScaledHeight = currentPageContentHeight * pixelRatio;-->

<!--        pdf.addImage(-->
<!--            pageImgData,-->
<!--            'PNG',-->
<!--            0,-->
<!--            25,-->
<!--            scaledWidth,-->
<!--            pageScaledHeight-->
<!--        );-->

<!--        pages.push({-->
<!--          pageNumber: pageIndex + 1,-->
<!--          scaledHeight: pageScaledHeight-->
<!--        });-->

<!--        currentY += currentPageContentHeight;-->
<!--        pageIndex++;-->

<!--        if (pageIndex > 50) {-->
<!--          console.warn('PDF页数过多，强制结束');-->
<!--          break;-->
<!--        }-->
<!--      }-->

<!--      const totalPages = pageIndex;-->

<!--      // 添加页码-->
<!--      for (let i = 0; i < totalPages; i++) {-->
<!--        pdf.setPage(i + 1);-->
<!--        pdf.setFontSize(10);-->
<!--        pdf.setTextColor(102, 102, 102);-->

<!--        const pageText = `${i + 1}/${totalPages}`;-->
<!--        const textWidth = pdf.getTextWidth(pageText);-->
<!--        const xPosition = (pdfWidth - textWidth) / 2;-->
<!--        const yPosition = pdfHeight - 15;-->

<!--        pdf.text(pageText, xPosition, yPosition);-->
<!--      }-->
<!--    }-->
<!--  },-->
<!--  mounted() {-->
<!--    this.fetchAndDisplayChenckResults();-->
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

<!--.header-section > div {-->
<!--  display: flex;-->
<!--  align-items: center;-->
<!--  gap: 10px;-->
<!--}-->

<!--.main-title {-->
<!--  color: #303133;-->
<!--  font-size: 24px;-->
<!--  font-weight: bold;-->
<!--  margin: 0 !important;-->
<!--}-->

<!--.control-section {-->
<!--  display: flex;-->
<!--  justify-content: space-between;-->
<!--  align-items: center;-->
<!--  margin-bottom: 20px;-->
<!--  flex-wrap: wrap;-->
<!--  gap: 15px;-->
<!--}-->

<!--.filter-group {-->
<!--  display: flex;-->
<!--  gap: 10px;-->
<!--}-->

<!--.filter-group .el-input {-->
<!--  width: 250px;-->
<!--}-->

<!--.action-buttons {-->
<!--  display: flex;-->
<!--  gap: 10px;-->
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

<!--.server1 .el-col p {-->
<!--  font-size: 16px;-->
<!--  white-space: pre-wrap;-->
<!--  line-height: 1.6;-->
<!--  margin-bottom: 5px;-->
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

<!--  .action-buttons {-->
<!--    width: 100%;-->
<!--    justify-content: flex-end;-->
<!--  }-->
<!--}-->
<!--</style>-->

<!--没有打印的版本-->
<!--<template>-->
<!--  <div class="baseline-container">-->
<!--    &lt;!&ndash; 头部区域 &ndash;&gt;-->
<!--    <div class="header-section">-->
<!--      <el-button-->
<!--          type="primary"-->
<!--          icon="el-icon-arrow-left"-->
<!--          @click="goBack"-->
<!--          size="mini"-->
<!--          style="margin-left:10px">-->
<!--        返回检测-->
<!--      </el-button>-->
<!--      <h1 class="main-title">等保测评结果</h1>-->

<!--      <div class="date-info">-->
<!--        <el-tag type="info"> </el-tag>-->
<!--      </div>-->
<!--      &lt;!&ndash;      <div class="date-info">&ndash;&gt;-->
<!--      &lt;!&ndash;        <el-tag type="info">检测时间：{{ new Date().toLocaleString() }}</el-tag>&ndash;&gt;-->
<!--      &lt;!&ndash;      </div>&ndash;&gt;-->
<!--    </div>-->

<!--    &lt;!&ndash; 控制按钮区域 &ndash;&gt;-->
<!--    <div class="control-section">-->
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
<!--        保存-->
<!--      </el-button>-->
<!--    </div>-->


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
<!--        &lt;!&ndash;        <el-table-column prop="item_id" label="检测项ID" min-width="50"></el-table-column>&ndash;&gt;-->
<!--        &lt;!&ndash;        <el-table-column label="序号" width="70" type="index"></el-table-column>&ndash;&gt;-->
<!--        <el-table-column prop="description" label="检测项" min-width="80"></el-table-column>-->
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
<!--        <el-table-column prop="check_time" label="检测时间" min-width="150"></el-table-column>-->
<!--      </el-table>-->
<!--    </el-card>-->

<!--  </div>-->
<!--</template>-->

<!--<script>-->
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
<!--      saveLoading: false, // 保存按钮的加载状态-->
<!--      ip:'',-->
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
<!--    // 获取检测结果函数-->
<!--    fetchAndDisplayChenckResults() {-->
<!--      const ip = this.$route.query.ip;-->
<!--      this.ip=this.$route.query.ip;-->
<!--      if (!ip) {-->
<!--        this.$message.error('无效的访问参数');-->
<!--        this.$router.push('/');-->
<!--        return;-->
<!--      }-->

<!--      this.tableLoading = true;-->
<!--      axios.get(`/api/level3TmpUserinfo?ip=${ip}`)-->
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
<!--          })-->
<!--          .catch(error => {-->
<!--            console.error('Error:', error);-->
<!--            this.tableLoading = false;-->
<!--            this.$message.error('获取检测结果失败，请重试');-->
<!--          });-->
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
<!--        ip: this.ip,-->
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
<!--    goBack() {-->
<!--      this.$router.push('/classifyProtectHome');-->
<!--    }-->
<!--  },-->
<!--  mounted() {-->
<!--    this.fetchAndDisplayChenckResults();-->
<!--  }-->
<!--}-->
<!--</script>-->

<!--<style scoped>-->
<!--.baseline-container {-->
<!--  padding: 20px;-->
<!--  background-color: #f5f7fa;-->
<!--  min-height: 100vh;-->
<!--}-->

<!--/* 调整标题对齐方式 */-->
<!--.header-section {-->
<!--  display: flex;-->
<!--  justify-content: space-between;-->
<!--  align-items: center;-->
<!--  margin-bottom: 20px;-->
<!--}-->

<!--/* 使标题和按钮水平排列 */-->
<!--.header-section > div {-->
<!--  display: flex;-->
<!--  align-items: center;-->
<!--  gap: 10px;-->
<!--}-->

<!--.main-title {-->
<!--  color: #303133;-->
<!--  font-size: 24px;-->
<!--  font-weight: bold;-->
<!--  margin: 0 !important; /* 移除原有标题的margin */-->
<!--}-->

<!--.control-section {-->
<!--  display: flex;-->
<!--  justify-content: space-between;-->
<!--  align-items: center;-->
<!--  margin-bottom: 20px;-->
<!--  flex-wrap: wrap;-->
<!--  gap: 15px;-->
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

<!--.server1 .el-col p {-->
<!--  font-size: 16px;-->
<!--  white-space: pre-wrap;-->
<!--  line-height: 1.6;-->
<!--  margin-bottom: 5px;-->
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



<!--<template>-->
<!--  <div class="baseline-container">-->
<!--    &lt;!&ndash; 头部区域 &ndash;&gt;-->
<!--    <div class="header-section">-->
<!--      <el-button-->
<!--          type="primary"-->
<!--          icon="el-icon-arrow-left"-->
<!--          @click="goBack"-->
<!--          size="mini"-->
<!--          style="margin-left:10px">-->
<!--        返回检测-->
<!--      </el-button>-->
<!--      <h1 class="main-title">等保测评结果</h1>-->

<!--      <div class="date-info">-->
<!--        <el-tag type="info"> </el-tag>-->
<!--      </div>-->
<!--&lt;!&ndash;      <div class="date-info">&ndash;&gt;-->
<!--&lt;!&ndash;        <el-tag type="info">检测时间：{{ new Date().toLocaleString() }}</el-tag>&ndash;&gt;-->
<!--&lt;!&ndash;      </div>&ndash;&gt;-->
<!--    </div>-->

<!--    &lt;!&ndash; 控制按钮区域 &ndash;&gt;-->
<!--    <div class="control-section">-->
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
<!--        保存-->
<!--      </el-button>-->
<!--    </div>-->


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
<!--&lt;!&ndash;        <el-table-column prop="item_id" label="检测项ID" min-width="50"></el-table-column>&ndash;&gt;-->
<!--&lt;!&ndash;        <el-table-column label="序号" width="70" type="index"></el-table-column>&ndash;&gt;-->
<!--        <el-table-column prop="description" label="检测项" min-width="80"></el-table-column>-->
<!--        <el-table-column prop="basis" label="基准" min-width="150"></el-table-column>-->
<!--        <el-table-column prop="result" label="检测结果" min-width="150"></el-table-column>-->
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

<!--  </div>-->
<!--</template>-->

<!--<script>-->
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
<!--      saveLoading: false, // 保存按钮的加载状态-->
<!--      ip:'',-->
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
<!--    // 获取检测结果函数-->
<!--    fetchAndDisplayChenckResults() {-->
<!--      const ip = this.$route.query.ip;-->
<!--      this.ip=this.$route.query.ip;-->
<!--      if (!ip) {-->
<!--        this.$message.error('无效的访问参数');-->
<!--        this.$router.push('/');-->
<!--        return;-->
<!--      }-->

<!--      this.tableLoading = true;-->
<!--      axios.get(`/api/level3TmpUserinfo?ip=${ip}`)-->
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
<!--                score: score-->
<!--              };-->
<!--            });-->
<!--            this.tableLoading = false;-->
<!--          })-->
<!--          .catch(error => {-->
<!--            console.error('Error:', error);-->
<!--            this.tableLoading = false;-->
<!--            this.$message.error('获取检测结果失败，请重试');-->
<!--          });-->
<!--      // axios.get(`/api/level3TmpUserinfo?ip=${ip}`)-->
<!--      //     .then(response  => {-->
<!--      //       this.checkresults = response.data.checkResults.map(item => ({-->
<!--      //         ...item,-->
<!--      //         score: item.IsComply === 'true' ? '1' : '0.5'-->
<!--      //       }));-->
<!--      //       this.tableLoading = false;-->
<!--      //     })-->
<!--      //     .catch(error => {-->
<!--      //       console.error('Error:', error);-->
<!--      //       this.tableLoading = false;-->
<!--      //       this.$message.error('获取检测结果失败，请重试');-->
<!--      //     });-->
<!--    },-->
<!--    saveScores() {-->
<!--      // 显示保存中状态-->
<!--      this.saveLoading = true;-->

<!--      // 准备请求数据-->
<!--      const scoreMeasures = this.checkresults.map(item => ({-->
<!--        item_id: item.item_id,-->
<!--        importantLevelJson: item.importantLevel || "2", // 如果有importantLevel字段则使用，否则默认为"2"-->
<!--        IsComplyLevel: item.score // 使用选择的评分值-->
<!--      }));-->

<!--      // 构建请求体-->
<!--      const requestData = {-->
<!--        ip: this.ip,-->
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
<!--    goBack() {-->
<!--      this.$router.push('/classifyProtectHome');-->
<!--    }-->
<!--  },-->
<!--  mounted() {-->
<!--    this.fetchAndDisplayChenckResults();-->
<!--  }-->
<!--}-->
<!--</script>-->

<!--<style scoped>-->
<!--.baseline-container {-->
<!--  padding: 20px;-->
<!--  background-color: #f5f7fa;-->
<!--  min-height: 100vh;-->
<!--}-->

<!--/* 调整标题对齐方式 */-->
<!--.header-section {-->
<!--  display: flex;-->
<!--  justify-content: space-between;-->
<!--  align-items: center;-->
<!--  margin-bottom: 20px;-->
<!--}-->

<!--/* 使标题和按钮水平排列 */-->
<!--.header-section > div {-->
<!--  display: flex;-->
<!--  align-items: center;-->
<!--  gap: 10px;-->
<!--}-->

<!--.main-title {-->
<!--  color: #303133;-->
<!--  font-size: 24px;-->
<!--  font-weight: bold;-->
<!--  margin: 0 !important; /* 移除原有标题的margin */-->
<!--}-->

<!--/*-->
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

<!-- */-->

<!--.control-section {-->
<!--  display: flex;-->
<!--  justify-content: space-between;-->
<!--  align-items: center;-->
<!--  margin-bottom: 20px;-->
<!--  flex-wrap: wrap;-->
<!--  gap: 15px;-->
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

<!--.server1 .el-col p {-->
<!--  font-size: 16px;-->
<!--  white-space: pre-wrap;-->
<!--  line-height: 1.6;-->
<!--  margin-bottom: 5px;-->
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

