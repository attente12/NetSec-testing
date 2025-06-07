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
      <h1 class="main-title">Linux基线检测结果</h1>

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
      </div>
    </div>

    <!-- 服务器信息卡片 -->
    <el-card class="server-info-card">
      <div slot="header" class="card-header">
        <span><i class="el-icon-monitor"></i> 服务器信息</span>
      </div>
      <div class="server-info-grid">
        <el-row :gutter="30">
          <el-col :span="12"><div class="info-item"><span class="info-label">IP：</span>{{ip || '未知'}}</div></el-col>
          <el-col :span="12"><div class="info-item"><span class="info-label">主机名：</span>{{serverInfo.hostname || '未知'}}</div></el-col>
          <el-col :span="12"><div class="info-item"><span class="info-label">主机架构：</span>{{serverInfo.arch || '未知'}}</div></el-col>
          <el-col :span="12"><div class="info-item"><span class="info-label">主机CPU信息：</span>{{serverInfo.cpu || '未知'}}</div></el-col>
          <el-col :span="12"><div class="info-item"><span class="info-label">主机物理CPU个数：</span>{{serverInfo.cpuPhysical || '未知'}}</div></el-col>
          <el-col :span="12"><div class="info-item"><span class="info-label">主机物理CPU核心数：</span>{{serverInfo.cpuCore || '未知'}}</div></el-col>
          <el-col :span="12"><div class="info-item"><span class="info-label">硬件型号：</span>{{serverInfo.ProductName || '未知'}}</div></el-col>
          <el-col :span="12"><div class="info-item"><span class="info-label">主机版本信息：</span>{{serverInfo.version || '未知'}}</div></el-col>
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
          <el-tag type="warning">待检查: {{ pendingCount }}</el-tag>
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
        <el-table-column label="是否通过检查" width="120">
          <template slot-scope="scope">
            <el-tag :type="getStatusType(scope.row.IsComply)">
              {{ getStatusText(scope.row.IsComply) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="修改建议" min-width="250">
          <template slot-scope="scope">
            <span v-if="scope.row.IsComply === 'false' || scope.row.IsComply === 'pending'">{{ scope.row.recommend }}</span>
            <span v-else>-</span>
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
      tableLoading: false,
      ip: '',
      pdfExporting: false, // PDF导出状态
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
    }
  },
  methods: {
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
      axios.get(`/api/tmpUserinfo?ip=${ip}`)
          .then(response => {
            this.checkresults = response.data.checkResults;
            this.serverInfo = response.data.serverInfo;
            this.tableLoading = false;
          })
          .catch(error => {
            console.error('Error:', error);
            this.tableLoading = false;
            this.$message.error('获取检测结果失败，请重试');
          });
    },

    goBack() {
      this.$router.push('/baseCheckHome');
    },

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

    // ==================== PDF导出功能 ====================

    // ==================== PDF导出功能 ====================

// 主导出方法
    async exportPdf() {
      if (!this.checkresults || this.checkresults.length === 0) {
        this.$message.warning('暂无检测结果数据');
        return;
      }

      this.pdfExporting = true;

      try {
        // 动态导入依赖库
        const jsPDF = (await import('jspdf')).default;
        const html2canvas = (await import('html2canvas')).default;

        // 创建临时打印容器
        const printContent = this.createPrintContent();
        document.body.appendChild(printContent);

        // 等待内容渲染完成
        await this.$nextTick();
        await new Promise(resolve => setTimeout(resolve, 1500));

        // 转换为Canvas - 使用高精度设置
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

        // 使用智能分页
        await this.createMultiPagePdf(pdf, canvas, pdfWidth, pdfHeight);

        // 保存PDF文件
        const fileName = `Linux基线检测报告_${this.ip}_${new Date().toISOString().split('T')[0]}.pdf`;
        pdf.save(fileName);

        this.$message.success('PDF报告导出成功');

      } catch (error) {
        console.error('PDF导出失败:', error);
        this.$message.error('PDF导出失败，请重试');
      } finally {
        this.pdfExporting = false;
      }
    },

// 智能分页方法
    async createMultiPagePdf(pdf, canvas, pdfWidth, pdfHeight) {
      const imgWidth = canvas.width;
      const imgHeight = canvas.height;

      const pageHeight = pdfHeight - 50; // 为页码和边距留出空间
      const ratio = pdfWidth / imgWidth;
      const scaledWidth = pdfWidth;
      const scaledHeight = imgHeight * ratio;

      // 计算实际像素对应的PDF高度
      const pixelRatio = scaledHeight / imgHeight;
      const pageHeightInPixels = pageHeight / pixelRatio;

      let currentY = 0;
      let pageIndex = 0;
      const pages = [];

      // 生成所有页面内容
      while (currentY < imgHeight) {
        if (pageIndex > 0) {
          pdf.addPage();
        }

        // 计算当前页要显示的内容高度
        let remainingHeight = imgHeight - currentY;
        let currentPageContentHeight = Math.min(pageHeightInPixels, remainingHeight);

        // 如果不是最后一页，寻找合适的分页点
        if (remainingHeight > pageHeightInPixels) {
          const optimalHeight = this.findOptimalBreakPoint(
              canvas,
              currentY,
              currentPageContentHeight,
              imgWidth
          );

          // 确保分页点不会太小
          if (optimalHeight > pageHeightInPixels * 0.5) {
            currentPageContentHeight = optimalHeight;
          }
        }

        // 创建当前页的canvas
        const pageCanvas = document.createElement('canvas');
        const pageCtx = pageCanvas.getContext('2d');

        pageCanvas.width = imgWidth;
        pageCanvas.height = currentPageContentHeight;

        // 绘制当前页内容
        pageCtx.fillStyle = '#ffffff';
        pageCtx.fillRect(0, 0, imgWidth, currentPageContentHeight);

        pageCtx.drawImage(
            canvas,
            0, currentY, imgWidth, currentPageContentHeight,
            0, 0, imgWidth, currentPageContentHeight
        );

        // 转换为图片并添加到PDF
        const pageImgData = pageCanvas.toDataURL('image/png');
        const pageScaledHeight = currentPageContentHeight * pixelRatio;

        pdf.addImage(
            pageImgData,
            'PNG',
            0,
            25, // 顶部留出边距
            scaledWidth,
            pageScaledHeight
        );

        pages.push({
          pageNumber: pageIndex + 1,
          scaledHeight: pageScaledHeight
        });

        currentY += currentPageContentHeight;
        pageIndex++;

        // 防止无限循环
        if (pageIndex > 50) {
          console.warn('PDF页数过多，强制结束');
          break;
        }
      }

      // 为每页添加页码
      const totalPages = pageIndex;
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
    },

// 寻找最佳分页点
    findOptimalBreakPoint(canvas, startY, maxHeight, canvasWidth) {
      const ctx = canvas.getContext('2d');
      const imageData = ctx.getImageData(0, startY, canvasWidth, maxHeight);
      const data = imageData.data;

      // 至少保留70%的页面高度
      const minHeight = Math.max(50, maxHeight * 0.7);

      // 从底部向上扫描，寻找合适的分页点
      for (let y = Math.floor(maxHeight) - 1; y >= minHeight; y--) {
        // 检查是否为表格行边界
        if (this.isTableRowBoundary(data, y, canvasWidth, maxHeight)) {
          return y;
        }

        // 检查是否为空白行
        if (this.isRowEmpty(data, y, canvasWidth)) {
          // 确保有足够的空白区域
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

      // 如果没找到合适的分页点，寻找表格外的安全区域
      for (let y = Math.floor(maxHeight) - 20; y >= minHeight; y--) {
        if (this.isSafeBreakPoint(data, y, canvasWidth, maxHeight)) {
          return y;
        }
      }

      // 最后的备选方案
      return Math.floor(maxHeight * 0.9);
    },

// 检测是否为表格行边界
    isTableRowBoundary(imageData, rowIndex, width, maxHeight) {
      const checkRange = 3;

      // 检查当前行是否有表格边框特征
      const currentRowBorderPixels = this.countBorderPixels(imageData, rowIndex, width);

      // 检查上面几行
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

      // 检查下面几行
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

      // 如果当前行有明显的水平边框，且上下行的边框较少，认为是表格行边界
      return currentRowBorderPixels > width * 0.15 &&
          aboveBorderCount <= 1 &&
          belowBorderCount <= 1;
    },

// 计算行中边框像素的数量
    countBorderPixels(imageData, rowIndex, width) {
      const rowStart = rowIndex * width * 4;
      const rowEnd = rowStart + width * 4;
      let borderPixels = 0;

      for (let i = rowStart; i < rowEnd; i += 4) {
        const r = imageData[i];
        const g = imageData[i + 1];
        const b = imageData[i + 2];

        // 检测边框颜色（深灰色或黑色）
        if ((r < 100 && g < 100 && b < 100) || // 深色边框
            (Math.abs(r - 221) < 10 && Math.abs(g - 221) < 10 && Math.abs(b - 221) < 10)) { // 浅灰色边框
          borderPixels++;
        }
      }

      return borderPixels;
    },

// 检查是否为空白行
    isRowEmpty(imageData, rowIndex, width) {
      const rowStart = rowIndex * width * 4;
      const rowEnd = rowStart + width * 4;

      for (let i = rowStart; i < rowEnd; i += 4) {
        const r = imageData[i];
        const g = imageData[i + 1];
        const b = imageData[i + 2];

        // 检查是否为白色或接近白色
        if (r < 250 || g < 250 || b < 250) {
          return false;
        }
      }
      return true;
    },

// 检查是否为安全的分页点
    isSafeBreakPoint(imageData, rowIndex, width, maxHeight) {
      // 检查当前行及周围行的内容密度
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

          // 非白色像素视为内容
          if (r < 250 || g < 250 || b < 250) {
            totalContentPixels++;
          }
        }
      }

      // 如果内容密度很低，认为是安全的分页点
      const contentDensity = totalContentPixels / totalPixels;
      return contentDensity < 0.05;
    },

// 创建打印内容容器
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

      // 优化表格样式，确保正确渲染
      const tables = printDiv.querySelectorAll('table');
      tables.forEach(table => {
        table.style.tableLayout = 'fixed';
        table.style.width = '100%';
        table.style.borderCollapse = 'collapse';
        table.style.marginBottom = '20px';
        table.style.pageBreakInside = 'avoid';

        // 确保单元格内容不会被截断
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

      // 为标题添加适当的间距
      const headings = printDiv.querySelectorAll('h2, h3');
      headings.forEach(heading => {
        heading.style.pageBreakAfter = 'avoid';
        heading.style.marginTop = '25px';
        heading.style.marginBottom = '15px';
      });

      return printDiv;
    },

// 生成打印HTML内容
    generatePrintHTML() {
      return `
    <div style="text-align: center; margin-bottom: 30px;">
      <h1 style="color: #333; font-size: 24px; margin: 0;">Linux基线检测报告</h1>
      <p style="color: #666; margin: 10px 0;">生成时间：${new Date().toLocaleString()}</p>
    </div>

    ${this.generateServerInfoHTML()}

    ${this.generateResultsTableHTML()}
    ${this.generateSignatureHTML()}
  `;
    },

// 生成服务器信息HTML
    generateServerInfoHTML() {
      return `
    <div style="margin-bottom: 25px;">
      <h2 style="color: #409EFF; font-size: 18px; border-bottom: 2px solid #409EFF; padding-bottom: 5px;">服务器信息</h2>
      <table style="width: 100%; border-collapse: collapse; margin-top: 10px;">
        <tr>
          <td style="padding: 8px; border: 1px solid #ddd; background: #f5f7fa; width: 25%; font-weight: bold;">IP地址</td>
          <td style="padding: 8px; border: 1px solid #ddd; width: 25%;">${this.ip || '未知'}</td>
          <td style="padding: 8px; border: 1px solid #ddd; background: #f5f7fa; width: 25%; font-weight: bold;">主机名</td>
          <td style="padding: 8px; border: 1px solid #ddd; width: 25%;">${this.serverInfo.hostname || '未知'}</td>
        </tr>
        <tr>
          <td style="padding: 8px; border: 1px solid #ddd; background: #f5f7fa; font-weight: bold;">主机架构</td>
          <td style="padding: 8px; border: 1px solid #ddd;">${this.serverInfo.arch || '未知'}</td>
          <td style="padding: 8px; border: 1px solid #ddd; background: #f5f7fa; font-weight: bold;">CPU信息</td>
          <td style="padding: 8px; border: 1px solid #ddd;">${this.serverInfo.cpu || '未知'}</td>
        </tr>
        <tr>
          <td style="padding: 8px; border: 1px solid #ddd; background: #f5f7fa; font-weight: bold;">物理CPU个数</td>
          <td style="padding: 8px; border: 1px solid #ddd;">${this.serverInfo.cpuPhysical || '未知'}</td>
          <td style="padding: 8px; border: 1px solid #ddd; background: #f5f7fa; font-weight: bold;">CPU核心数</td>
          <td style="padding: 8px; border: 1px solid #ddd;">${this.serverInfo.cpuCore || '未知'}</td>
        </tr>
        <tr>
          <td style="padding: 8px; border: 1px solid #ddd; background: #f5f7fa; font-weight: bold;">硬件型号</td>
          <td style="padding: 8px; border: 1px solid #ddd;">${this.serverInfo.ProductName || '未知'}</td>
          <td style="padding: 8px; border: 1px solid #ddd; background: #f5f7fa; font-weight: bold;">版本信息</td>
          <td style="padding: 8px; border: 1px solid #ddd;">${this.serverInfo.version || '未知'}</td>
        </tr>
      </table>
    </div>
  `;
    },

// 生成统计摘要HTML
    generateSummaryHTML() {
      return `
    <div style="margin-bottom: 25px;">
      <h2 style="color: #409EFF; font-size: 18px; border-bottom: 2px solid #409EFF; padding-bottom: 5px;">检测结果统计</h2>
      <div style="display: flex; justify-content: space-around; padding: 20px; background-color: #f5f7fa; border-radius: 8px; margin-top: 15px;">
        <div style="text-align: center;">
          <div style="font-size: 24px; font-weight: bold; color: #67C23A; margin-bottom: 5px;">${this.passedCount}</div>
          <div style="color: #606266;">通过</div>
        </div>
        <div style="text-align: center;">
          <div style="font-size: 24px; font-weight: bold; color: #F56C6C; margin-bottom: 5px;">${this.failedCount}</div>
          <div style="color: #606266;">未通过</div>
        </div>
        <div style="text-align: center;">
          <div style="font-size: 24px; font-weight: bold; color: #E6A23C; margin-bottom: 5px;">${this.pendingCount}</div>
          <div style="color: #606266;">待检查</div>
        </div>
        <div style="text-align: center;">
          <div style="font-size: 24px; font-weight: bold; color: #909399; margin-bottom: 5px;">${this.totalCount}</div>
          <div style="color: #606266;">总计</div>
        </div>
      </div>
    </div>
  `;
    },

// 生成检测结果表格HTML
    generateResultsTableHTML() {
      let html = `
    <div style="margin-bottom: 25px;">
      <h2 style="color: #409EFF; font-size: 18px; border-bottom: 2px solid #409EFF; padding-bottom: 5px;">详细检测结果</h2>
      <table style="width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 11px;">
        <thead>
          <tr style="background: #f5f7fa;">
            <th style="padding: 8px; border: 1px solid #ddd; text-align: center; width: 5%;">序号</th>
            <th style="padding: 8px; border: 1px solid #ddd; text-align: center; width: 20%;">检测项</th>
            <th style="padding: 8px; border: 1px solid #ddd; text-align: center; width: 15%;">基准</th>
            <th style="padding: 8px; border: 1px solid #ddd; text-align: center; width: 20%;">检测结果</th>
            <th style="padding: 8px; border: 1px solid #ddd; text-align: center; width: 10%;">是否通过</th>
            <th style="padding: 8px; border: 1px solid #ddd; text-align: center; width: 25%;">修改建议</th>
            <th style="padding: 8px; border: 1px solid #ddd; text-align: center; width: 15%;">检测时间</th>
          </tr>
        </thead>
        <tbody>
  `;

      this.checkresults.forEach((item, index) => {
        const statusColor = item.IsComply === 'true' ? '#67C23A' :
            item.IsComply === 'false' ? '#F56C6C' : '#E6A23C';
        const statusText = this.getStatusText(item.IsComply);
        const suggestion = (item.IsComply === 'false' || item.IsComply === 'pending') ?
            (item.recommend || '-') : '-';

        html += `
      <tr>
        <td style="padding: 6px; border: 1px solid #ddd; text-align: center;">${index + 1}</td>
        <td style="padding: 6px; border: 1px solid #ddd; font-size: 10px;">${item.description || '-'}</td>
        <td style="padding: 6px; border: 1px solid #ddd; font-size: 10px;">${item.basis || '-'}</td>
        <td style="padding: 6px; border: 1px solid #ddd; font-size: 10px;">${item.result || '-'}</td>
        <td style="padding: 6px; border: 1px solid #ddd; text-align: center; color: ${statusColor}; font-weight: bold;">${statusText}</td>
        <td style="padding: 6px; border: 1px solid #ddd; font-size: 10px;">${suggestion}</td>
        <td style="padding: 6px; border: 1px solid #ddd; text-align: center; font-size: 10px;">${item.check_time || '-'}</td>
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

/* 调整标题对齐方式 */
.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

/* 使标题和按钮水平排列 */
.header-section > div {
  display: flex;
  align-items: center;
  gap: 10px;
}

.main-title {
  color: #303133;
  font-size: 24px;
  font-weight: bold;
  margin: 0 !important; /* 移除原有标题的margin */
}

/*
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

 */

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

.server-info-card {
  margin-bottom: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.failed-result {
  color: #f56c6c;  /* 这是Element UI的危险红色 */
}
.pending-result {
  color: #e6a23c;
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

/*以下新增*/
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


/*到这*/
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

/* PDF导出相关样式 - 添加到现有style标签中 */

/* 确保表格在PDF中正确渲染 */
.el-table {
  page-break-inside: avoid;
}

.el-table .el-table__row {
  page-break-inside: avoid;
  break-inside: avoid;
}

/* PDF打印时的特殊样式 */
@media print {
  .baseline-container {
    padding: 0;
    background-color: white;
  }

  .control-section,
  .header-section .el-button {
    display: none !important;
  }

  .server-info-card,
  .results-card {
    box-shadow: none;
    border: 1px solid #ddd;
  }
}

/* 临时PDF容器样式（用于html2canvas） */
.pdf-temp-container {
  position: absolute;
  top: -10000px;
  left: -10000px;
  width: 800px;
  background: white;
  padding: 20px;
  font-family: 'Microsoft YaHei', Arial, sans-serif;
  line-height: 1.6;
  color: #333;
  box-sizing: border-box;
}

.pdf-temp-container table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 20px;
  page-break-inside: avoid;
}

.pdf-temp-container th,
.pdf-temp-container td {
  padding: 8px;
  border: 1px solid #ddd;
  word-wrap: break-word;
  word-break: break-all;
  line-height: 1.4;
}

.pdf-temp-container th {
  background-color: #f5f7fa;
  font-weight: bold;
  text-align: center;
}

/* 状态标签在PDF中的样式 */
.pdf-temp-container .status-passed {
  color: #67C23A;
  font-weight: bold;
}

.pdf-temp-container .status-failed {
  color: #F56C6C;
  font-weight: bold;
}

.pdf-temp-container .status-pending {
  color: #E6A23C;
  font-weight: bold;
}
</style>

<!--版本：缺页-->
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
<!--      <h1 class="main-title">Linux基线检测结果</h1>-->

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
<!--      </div>-->
<!--    </div>-->

<!--    &lt;!&ndash; 服务器信息卡片 &ndash;&gt;-->
<!--    <el-card class="server-info-card">-->
<!--      <div slot="header" class="card-header">-->
<!--        <span><i class="el-icon-monitor"></i> 服务器信息</span>-->
<!--      </div>-->
<!--      <div class="server-info-grid">-->
<!--        <el-row :gutter="30">-->
<!--          <el-col :span="12"><div class="info-item"><span class="info-label">IP：</span>{{ip || '未知'}}</div></el-col>-->
<!--          <el-col :span="12"><div class="info-item"><span class="info-label">主机名：</span>{{serverInfo.hostname || '未知'}}</div></el-col>-->
<!--          <el-col :span="12"><div class="info-item"><span class="info-label">主机架构：</span>{{serverInfo.arch || '未知'}}</div></el-col>-->
<!--          <el-col :span="12"><div class="info-item"><span class="info-label">主机CPU信息：</span>{{serverInfo.cpu || '未知'}}</div></el-col>-->
<!--          <el-col :span="12"><div class="info-item"><span class="info-label">主机物理CPU个数：</span>{{serverInfo.cpuPhysical || '未知'}}</div></el-col>-->
<!--          <el-col :span="12"><div class="info-item"><span class="info-label">主机物理CPU核心数：</span>{{serverInfo.cpuCore || '未知'}}</div></el-col>-->
<!--          <el-col :span="12"><div class="info-item"><span class="info-label">硬件型号：</span>{{serverInfo.ProductName || '未知'}}</div></el-col>-->
<!--          <el-col :span="12"><div class="info-item"><span class="info-label">主机版本信息：</span>{{serverInfo.version || '未知'}}</div></el-col>-->
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

<!--      <el-table-->
<!--          :data="filteredCheckresults"-->
<!--          style="width: 100%"-->
<!--          border-->
<!--          stripe-->
<!--          :header-cell-style="{background:'#f5f7fa',color:'#606266'}"-->
<!--          v-loading="tableLoading">-->
<!--        <el-table-column label="序号" width="70" type="index"></el-table-column>-->
<!--        <el-table-column prop="description" label="检测项" min-width="150"></el-table-column>-->
<!--        <el-table-column prop="basis" label="基准" min-width="150"></el-table-column>-->
<!--        <el-table-column prop="result" label="检测结果" min-width="150"></el-table-column>-->
<!--        <el-table-column label="是否通过检查" width="120">-->
<!--          <template slot-scope="scope">-->
<!--            <el-tag :type="getStatusType(scope.row.IsComply)">-->
<!--              {{ getStatusText(scope.row.IsComply) }}-->
<!--            </el-tag>-->
<!--          </template>-->
<!--        </el-table-column>-->
<!--        <el-table-column label="修改建议" min-width="250">-->
<!--          <template slot-scope="scope">-->
<!--            <span v-if="scope.row.IsComply === 'false' || scope.row.IsComply === 'pending'">{{ scope.row.recommend }}</span>-->
<!--            <span v-else>-</span>-->
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
<!--      tableLoading: false,-->
<!--      ip: '',-->
<!--      pdfExporting: false, // PDF导出状态-->
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
<!--      axios.get(`/api/tmpUserinfo?ip=${ip}`)-->
<!--          .then(response => {-->
<!--            this.checkresults = response.data.checkResults;-->
<!--            this.serverInfo = response.data.serverInfo;-->
<!--            this.tableLoading = false;-->
<!--          })-->
<!--          .catch(error => {-->
<!--            console.error('Error:', error);-->
<!--            this.tableLoading = false;-->
<!--            this.$message.error('获取检测结果失败，请重试');-->
<!--          });-->
<!--    },-->

<!--    goBack() {-->
<!--      this.$router.push('/baseCheckHome');-->
<!--    },-->

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
<!--        const fileName = `Linux基线检测报告_${this.ip}_${new Date().toISOString().split('T')[0]}.pdf`;-->
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
<!--          <h1 style="color: #333; font-size: 24px; margin: 0;">Linux基线检测报告</h1>-->
<!--          <p style="color: #666; margin: 10px 0;">服务器IP：${this.ip}</p>-->
<!--          <p style="color: #666; margin: 10px 0;">生成时间：${new Date().toLocaleString()}</p>-->
<!--        </div>-->

<!--        ${this.generateServerInfoHTML()}-->
<!--        ${this.generateSummaryHTML()}-->
<!--        ${this.generateDetailTableHTML()}-->
<!--        ${this.generateSignatureHTML()}-->
<!--      `;-->
<!--    },-->

<!--    // 生成服务器信息HTML-->
<!--    generateServerInfoHTML() {-->
<!--      return `-->
<!--        <div style="margin-bottom: 25px;">-->
<!--          <h2 style="color: #409EFF; font-size: 18px; border-bottom: 2px solid #409EFF; padding-bottom: 5px;">服务器信息</h2>-->
<!--          <table style="width: 100%; border-collapse: collapse; margin-top: 10px;">-->
<!--            <tr>-->
<!--              <td style="padding: 12px; border: 1px solid #ddd; background: #f5f7fa; width: 25%; font-weight: bold;">IP地址</td>-->
<!--              <td style="padding: 12px; border: 1px solid #ddd; width: 25%;">${this.ip || '未知'}</td>-->
<!--              <td style="padding: 12px; border: 1px solid #ddd; background: #f5f7fa; width: 25%; font-weight: bold;">主机名</td>-->
<!--              <td style="padding: 12px; border: 1px solid #ddd; width: 25%;">${this.serverInfo.hostname || '未知'}</td>-->
<!--            </tr>-->
<!--            <tr>-->
<!--              <td style="padding: 12px; border: 1px solid #ddd; background: #f5f7fa; font-weight: bold;">主机架构</td>-->
<!--              <td style="padding: 12px; border: 1px solid #ddd;">${this.serverInfo.arch || '未知'}</td>-->
<!--              <td style="padding: 12px; border: 1px solid #ddd; background: #f5f7fa; font-weight: bold;">CPU信息</td>-->
<!--              <td style="padding: 12px; border: 1px solid #ddd;">${this.serverInfo.cpu || '未知'}</td>-->
<!--            </tr>-->
<!--            <tr>-->
<!--              <td style="padding: 12px; border: 1px solid #ddd; background: #f5f7fa; font-weight: bold;">物理CPU个数</td>-->
<!--              <td style="padding: 12px; border: 1px solid #ddd;">${this.serverInfo.cpuPhysical || '未知'}</td>-->
<!--              <td style="padding: 12px; border: 1px solid #ddd; background: #f5f7fa; font-weight: bold;">CPU核心数</td>-->
<!--              <td style="padding: 12px; border: 1px solid #ddd;">${this.serverInfo.cpuCore || '未知'}</td>-->
<!--            </tr>-->
<!--            <tr>-->
<!--              <td style="padding: 12px; border: 1px solid #ddd; background: #f5f7fa; font-weight: bold;">硬件型号</td>-->
<!--              <td style="padding: 12px; border: 1px solid #ddd;">${this.serverInfo.ProductName || '未知'}</td>-->
<!--              <td style="padding: 12px; border: 1px solid #ddd; background: #f5f7fa; font-weight: bold;">版本信息</td>-->
<!--              <td style="padding: 12px; border: 1px solid #ddd;">${this.serverInfo.version || '未知'}</td>-->
<!--            </tr>-->
<!--          </table>-->
<!--        </div>-->
<!--      `;-->
<!--    },-->

<!--    // 生成汇总信息HTML-->
<!--    generateSummaryHTML() {-->
<!--      return `-->
<!--        <div style="margin-bottom: 25px;">-->
<!--          <h2 style="color: #409EFF; font-size: 18px; border-bottom: 2px solid #409EFF; padding-bottom: 5px;">检测汇总</h2>-->
<!--          <table style="width: 100%; border-collapse: collapse; margin-top: 10px;">-->
<!--            <tr>-->
<!--              <td style="padding: 12px; border: 1px solid #ddd; background: #f5f7fa; width: 25%; font-weight: bold; text-align: center;">总计</td>-->
<!--              <td style="padding: 12px; border: 1px solid #ddd; width: 25%; text-align: center; font-weight: bold; font-size: 16px;">${this.totalCount}</td>-->
<!--              <td style="padding: 12px; border: 1px solid #ddd; background: #f5f7fa; width: 25%; font-weight: bold; text-align: center;">通过</td>-->
<!--              <td style="padding: 12px; border: 1px solid #ddd; width: 25%; text-align: center; color: #67C23A; font-weight: bold; font-size: 16px;">${this.passedCount}</td>-->
<!--            </tr>-->
<!--            <tr>-->
<!--              <td style="padding: 12px; border: 1px solid #ddd; background: #f5f7fa; font-weight: bold; text-align: center;">未通过</td>-->
<!--              <td style="padding: 12px; border: 1px solid #ddd; text-align: center; color: #F56C6C; font-weight: bold; font-size: 16px;">${this.failedCount}</td>-->
<!--              <td style="padding: 12px; border: 1px solid #ddd; background: #f5f7fa; font-weight: bold; text-align: center;">待检查</td>-->
<!--              <td style="padding: 12px; border: 1px solid #ddd; text-align: center; color: #E6A23C; font-weight: bold; font-size: 16px;">${this.pendingCount}</td>-->
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
<!--                <th style="padding: 6px; border: 1px solid #ddd; text-align: center; width: 20%;">基准</th>-->
<!--                <th style="padding: 6px; border: 1px solid #ddd; text-align: center; width: 20%;">检测结果</th>-->
<!--                <th style="padding: 6px; border: 1px solid #ddd; text-align: center; width: 8%;">是否通过</th>-->
<!--                <th style="padding: 6px; border: 1px solid #ddd; text-align: center; width: 20%;">修改建议</th>-->
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
<!--            statusColor = '#67C23A';-->
<!--            break;-->
<!--          case 'false':-->
<!--            statusText = '未通过';-->
<!--            statusColor = '#F56C6C';-->
<!--            break;-->
<!--          case 'pending':-->
<!--            statusText = '待检查';-->
<!--            statusColor = '#E6A23C';-->
<!--            break;-->
<!--          default:-->
<!--            statusText = '未知';-->
<!--            statusColor = '#909399';-->
<!--            break;-->
<!--        }-->

<!--        const suggestion = (item.IsComply === 'false' || item.IsComply === 'pending') ? (item.recommend || '-') : '-';-->

<!--        html += `-->
<!--          <tr>-->
<!--            <td style="padding: 5px; border: 1px solid #ddd; text-align: center;">${index + 1}</td>-->
<!--            <td style="padding: 5px; border: 1px solid #ddd; font-size: 10px;">${item.description || '-'}</td>-->
<!--            <td style="padding: 5px; border: 1px solid #ddd; font-size: 10px;">${item.basis || '-'}</td>-->
<!--            <td style="padding: 5px; border: 1px solid #ddd; font-size: 10px;">${item.result || '-'}</td>-->
<!--            <td style="padding: 5px; border: 1px solid #ddd; text-align: center; color: ${statusColor}; font-weight: bold;">${statusText}</td>-->
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

<!--    // 生成签名区域HTML-->
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

<!--.failed-result {-->
<!--  color: #f56c6c;  /* 这是Element UI的危险红色 */-->
<!--}-->
<!--.pending-result {-->
<!--  color: #e6a23c;-->
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

<!--/*以下新增*/-->
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


<!--/*到这*/-->
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





<!--版本：打印慢-->
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
<!--      <h1 class="main-title">Linux基线检测结果</h1>-->

<!--      <div class="date-info">-->
<!--        <el-tag type="info"> </el-tag>-->
<!--      </div>-->
<!--    </div>-->

<!--    &lt;!&ndash; 控制按钮区域 &ndash;&gt;-->
<!--    <div class="control-section">-->
<!--      <el-button-->
<!--          @click="onExportToPDF"-->
<!--          :loading="pdfLoading"-->
<!--          icon="el-icon-document"-->
<!--          type="">-->
<!--        导出为 PDF-->
<!--      </el-button>-->
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
<!--    </div>-->

<!--    &lt;!&ndash; 服务器信息卡片 &ndash;&gt;-->
<!--    <el-card class="server-info-card">-->
<!--      <div slot="header" class="card-header">-->
<!--        <span><i class="el-icon-monitor"></i> 服务器信息</span>-->
<!--      </div>-->
<!--      <div class="server-info-grid">-->
<!--        <el-row :gutter="30">-->
<!--          <el-col :span="12"><div class="info-item"><span class="info-label">ip：</span>{{ip || '未知'}}</div></el-col>-->
<!--          <el-col :span="12"><div class="info-item"><span class="info-label">主机名：</span>{{serverInfo.hostname || '未知'}}</div></el-col>-->
<!--          <el-col :span="12"><div class="info-item"><span class="info-label">主机架构：</span>{{serverInfo.arch || '未知'}}</div></el-col>-->
<!--          <el-col :span="12"><div class="info-item"><span class="info-label">主机CPU信息：</span>{{serverInfo.cpu || '未知'}}</div></el-col>-->
<!--          <el-col :span="12"><div class="info-item"><span class="info-label">主机物理CPU个数：</span>{{serverInfo.cpuPhysical || '未知'}}</div></el-col>-->
<!--          <el-col :span="12"><div class="info-item"><span class="info-label">主机物理CPU核心数：</span>{{serverInfo.cpuCore || '未知'}}</div></el-col>-->
<!--&lt;!&ndash;          <el-col :span="12"><div class="info-item"><span class="info-label">主机空闲内存：</span>{{serverInfo.free || '未知'}}</div></el-col>&ndash;&gt;-->
<!--          <el-col :span="12"><div class="info-item"><span class="info-label">硬件型号：</span>{{serverInfo.ProductName || '未知'}}</div></el-col>-->
<!--          <el-col :span="12"><div class="info-item"><span class="info-label">主机版本信息：</span>{{serverInfo.version || '未知'}}</div></el-col>-->
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

<!--      <el-table-->
<!--          :data="filteredCheckresults"-->
<!--          style="width: 100%"-->
<!--          border-->
<!--          stripe-->
<!--          :header-cell-style="{background:'#f5f7fa',color:'#606266'}"-->
<!--          v-loading="tableLoading">-->
<!--        <el-table-column label="序号" width="70" type="index"></el-table-column>-->
<!--        <el-table-column prop="description" label="检测项" min-width="150"></el-table-column>-->
<!--        <el-table-column prop="basis" label="基准" min-width="150"></el-table-column>-->
<!--        <el-table-column prop="result" label="检测结果" min-width="150"></el-table-column>-->
<!--        <el-table-column label="是否通过检查" width="120">-->
<!--          <template slot-scope="scope">-->
<!--&lt;!&ndash;            <el-tag :type="scope.row.IsComply === 'true' ? 'success' : 'danger'">&ndash;&gt;-->
<!--&lt;!&ndash;              {{ scope.row.IsComply === 'true' ? '通过' : '未通过' }}&ndash;&gt;-->
<!--&lt;!&ndash;            </el-tag>&ndash;&gt;-->
<!--            <el-tag :type="getStatusType(scope.row.IsComply)">-->
<!--                  {{ getStatusText(scope.row.IsComply) }}-->
<!--            </el-tag>-->
<!--          </template>-->
<!--        </el-table-column>-->
<!--        <el-table-column label="修改建议" min-width="250">-->
<!--          <template slot-scope="scope">-->
<!--&lt;!&ndash;            <span v-if="scope.row.IsComply === 'false'">{{ scope.row.recommend }}</span>&ndash;&gt;-->
<!--            <span v-if="scope.row.IsComply === 'false' || scope.row.IsComply === 'pending'">{{ scope.row.recommend }}</span>-->
<!--            <span v-else>-</span>-->
<!--          </template>-->
<!--        </el-table-column>-->
<!--        <el-table-column prop="check_time" label="检测时间" min-width="150"></el-table-column>-->
<!--      </el-table>-->
<!--    </el-card>-->

<!--    &lt;!&ndash; PDF内容（隐藏） &ndash;&gt;-->
<!--    <div class="pdf-content" v-show="showContentForPDF">-->
<!--      <div class="server1">-->
<!--        <h1 id="linuxBaseline2">Linux基线检测报告</h1>-->
<!--        &lt;!&ndash; 检测时间 &ndash;&gt;-->
<!--        <div style="text-align:right; margin-top:20px;">-->
<!--          <p style="font-size:18px;">打印时间：{{ new Date().toLocaleString() }}</p>-->
<!--        </div>-->
<!--        <el-row :gutter="20">-->
<!--          <el-col :span="24"><p>主机名：{{ serverInfo.hostname }}</p></el-col>-->
<!--          <el-col :span="24"><p>主机架构：{{ serverInfo.arch }}</p></el-col>-->
<!--          <el-col :span="24"><p>主机CPU信息：{{ serverInfo.cpu }}</p></el-col>-->
<!--          <el-col :span="24"><p>主机物理CPU个数：{{ serverInfo.cpuPhysical }}</p></el-col>-->
<!--          <el-col :span="24"><p>主机物理CPU核心数：{{ serverInfo.cpuCore }}</p></el-col>-->
<!--&lt;!&ndash;          <el-col :span="12"><p>主机空闲内存：{{ serverInfo.free }}</p></el-col>&ndash;&gt;-->
<!--          <el-col :span="24"><p>硬件型号：{{ serverInfo.ProductName }}</p></el-col>-->
<!--          <el-col :span="24"><p>主机版本信息：{{ serverInfo.version }}</p></el-col>-->
<!--          <el-col :span="24"><p>服务器IP：{{ ip }}</p></el-col>-->
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
<!--        <el-table-column prop="IsComply" label="是否通过检查" width="80">-->
<!--          <template slot-scope="scope">-->
<!--            &lt;!&ndash;            <span :class="{ 'failed-result': scope.row.IsComply === 'false' }">&ndash;&gt;-->
<!--            &lt;!&ndash;              {{ scope.row.IsComply === 'true' ? '通过' : '未通过' }}&ndash;&gt;-->
<!--            &lt;!&ndash;            </span>&ndash;&gt;-->
<!--            <span :class="getStatusClass(scope.row.IsComply)">-->
<!--                 {{ getStatusText(scope.row.IsComply) }}-->
<!--            </span>-->
<!--          </template>-->
<!--        </el-table-column>-->
<!--        <el-table-column label="修改建议" width="300">-->
<!--          <template slot-scope="scope">-->
<!--            <span v-if="scope.row.IsComply === 'false'">{{ scope.row.recommend }}</span>-->
<!--            <span v-else>-</span>-->
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
<!--      ip:'',-->
<!--      totalPages: 2, // 默认至少两页-->
<!--      aliveHosts: [], // 活跃主机IP列表-->
<!--    }-->
<!--  },-->
<!--  computed: {-->
<!--    filteredCheckresults() {-->
<!--      return this.checkresults.filter(result => {-->
<!--        const matchesStatus = this.selectedStatus === 'all' ||-->
<!--            (this.selectedStatus === 'passed' && result.IsComply === 'true') ||-->
<!--            (this.selectedStatus === 'failed' && result.IsComply === 'false') ||-->
<!--            (this.selectedStatus === 'pending' && result.IsComply === 'pending');-->
<!--            // (this.selectedStatus === 'failed' && result.IsComply === 'false');-->
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
<!--      axios.get(`/api/tmpUserinfo?ip=${ip}`)-->
<!--          .then(response => {-->
<!--            this.checkresults = response.data.checkResults;-->
<!--            this.serverInfo = response.data.serverInfo;-->
<!--            this.tableLoading = false;-->
<!--          })-->
<!--          .catch(error => {-->
<!--            console.error('Error:', error);-->
<!--            this.tableLoading = false;-->
<!--            this.$message.error('获取检测结果失败，请重试');-->
<!--          });-->
<!--    },-->
<!--    goBack() {-->
<!--      this.$router.push('/baseCheckHome');-->
<!--    },-->
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
<!--        const filename = `Linux基线检测报告_${this.ip}_${new Date().toISOString().slice(0,10)}.pdf`;-->
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
<!--    // 获取PDF中状态对应的CSS类-->
<!--    getStatusClass(status) {-->
<!--      return {-->
<!--        'failed-result': status === 'false',-->
<!--        'pending-result': status === 'pending'-->
<!--      };-->
<!--    },-->



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

<!--.failed-result {-->
<!--  color: #f56c6c;  /* 这是Element UI的危险红色 */-->
<!--}-->
<!--.pending-result {-->
<!--  color: #e6a23c;-->
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

<!--/*以下新增*/-->
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


<!--/*到这*/-->
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

