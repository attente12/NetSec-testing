<template>
  <div class="baseline-container">
    <!-- 头部区域 -->
    <div class="header-section">
      <el-button type="primary" icon="el-icon-arrow-left" @click="goBack" size="mini" style="margin-left:10px">
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
        <el-select v-model="selectedStatus" placeholder="请选择状态" size="medium">
          <el-option label="全部" value="all"></el-option>
          <el-option label="通过" value="passed"></el-option>
          <el-option label="未通过" value="failed"></el-option>
          <el-option label="待检查" value="pending"></el-option>
        </el-select>

        <el-input placeholder="输入检测项关键字..." v-model="searchTerm" @input="filterSearchResults"
          prefix-icon="el-icon-search" size="medium">
        </el-input>
      </div>

      <div class="action-buttons">
        <!-- 导出PDF按钮 -->
        <el-button type="warning" icon="el-icon-printer" @click="exportPdf" :loading="pdfExporting" size="medium">
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
          <el-col :span="12">
            <div class="info-item"><span class="info-label">IP：</span>{{ ip || '未知' }}</div>
          </el-col>
          <el-col :span="12">
            <div class="info-item"><span class="info-label">主机名：</span>{{ serverInfo.hostname || '未知' }}</div>
          </el-col>
          <el-col :span="12">
            <div class="info-item"><span class="info-label">主机架构：</span>{{ serverInfo.arch || '未知' }}</div>
          </el-col>
          <el-col :span="12">
            <div class="info-item"><span class="info-label">主机CPU信息：</span>{{ serverInfo.cpu || '未知' }}</div>
          </el-col>
          <el-col :span="12">
            <div class="info-item"><span class="info-label">主机物理CPU个数：</span>{{ serverInfo.cpuPhysical || '未知' }}</div>
          </el-col>
          <el-col :span="12">
            <div class="info-item"><span class="info-label">主机物理CPU核心数：</span>{{ serverInfo.cpuCore || '未知' }}</div>
          </el-col>
          <el-col :span="12">
            <div class="info-item"><span class="info-label">硬件型号：</span>{{ serverInfo.ProductName || '未知' }}</div>
          </el-col>
          <el-col :span="12">
            <div class="info-item"><span class="info-label">主机版本信息：</span>{{ serverInfo.version || '未知' }}</div>
          </el-col>
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

      <el-table :data="filteredCheckresults" style="width: 100%" border stripe
        :header-cell-style="{ background: '#f5f7fa', color: '#606266' }" v-loading="tableLoading">
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
            <span v-if="scope.row.IsComply === 'false' || scope.row.IsComply === 'pending'">{{ scope.row.recommend
            }}</span>
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
.header-section>div {
  display: flex;
  align-items: center;
  gap: 10px;
}

.main-title {
  color: #303133;
  font-size: 24px;
  font-weight: bold;
  margin: 0 !important;
  /* 移除原有标题的margin */
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

.server-info-card {
  margin-bottom: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.failed-result {
  color: #f56c6c;
  /* 这是Element UI的危险红色 */
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