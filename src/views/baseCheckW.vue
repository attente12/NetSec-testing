<template>
    <div class="baseline-container">
        <div class="header-section">
            <h1 class="main-title">Windows基线检测报告</h1>
            <div class="date-info">
                <el-tag type="info">检测时间：{{ globalDate }}</el-tag>
            </div>
        </div>

        <div class="control-section">
            <div class="button-group">

                <el-button @click="onExportToPDF" :loading="pdfLoading" icon="el-icon-document" type="primary">
                    导出为 PDF
                </el-button>
            </div>

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
        </div>

        <el-card class="server-info-card">
            <div slot="header" class="card-header">
                <span><i class="el-icon-monitor"></i> 服务器信息</span>
            </div>
            <div class="server-info-grid">
                <el-row :gutter="30">
                    <el-col :span="12">
                        <div class="info-item"><span class="info-label">主机名：</span>{{ serverInfo.hostname || '未知' }}
                        </div>
                    </el-col>
                    <el-col :span="12">
                        <div class="info-item"><span class="info-label">主机架构：</span>{{ serverInfo.arch || '未知' }}</div>
                    </el-col>
                    <el-col :span="12">
                        <div class="info-item"><span class="info-label">主机CPU信息：</span>{{ serverInfo.cpu || '未知' }}
                        </div>
                    </el-col>
                    <el-col :span="12">
                        <div class="info-item"><span class="info-label">主机物理CPU个数：</span>{{ serverInfo.cpuPhysical ||
                            '未知' }}</div>
                    </el-col>
                    <el-col :span="12">
                        <div class="info-item"><span class="info-label">主机物理CPU核心数：</span>{{ serverInfo.cpuCore || '未知'
                        }}</div>
                    </el-col>
                    <el-col :span="12">
                        <div class="info-item"><span class="info-label">硬件型号：</span>{{ serverInfo.ProductName || '未知' }}
                        </div>
                    </el-col>
                    <el-col :span="12">
                        <div class="info-item"><span class="info-label">主机版本信息：</span>{{ serverInfo.version || '未知' }}
                        </div>
                    </el-col>
                </el-row>
            </div>
        </el-card>

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
                        <span v-if="scope.row.IsComply === 'false' || scope.row.IsComply === 'pending'">{{
                            scope.row.recommend
                        }}</span>
                        <span v-else>-</span>
                    </template>
                </el-table-column>
            </el-table>

        </el-card>

        <div class="pdf-content" v-if="showContentForPDF">
            <div class="server1">
                <h1 id="linuxBaseline2">Windows基线检测报告</h1>
                <div style="text-align:right; margin-top:20px;">
                    <p style="font-size:18px;">检测时间：{{ globalDate.toLocaleString() }}</p>
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
                    </el-col>
                    <el-col :span="12">
                        <p>主机空闲内存：{{ serverInfo.free }}</p>
                    </el-col>
                    <el-col :span="24">
                        <p>硬件型号：{{ serverInfo.ProductName }}</p>
                    </el-col>
                    <el-col :span="24">
                        <p>主机版本信息：{{ serverInfo.version }}</p>
                    </el-col>
                    <el-col :span="24">
                        <p>服务器IP：{{ selectedIP }}</p>
                    </el-col>
                </el-row>
                <div style="height:200px;"></div>
                <div style="text-align:right; margin-top:20px;">
                    <span style="font-size:20px;">检测人员签名：</span>
                    <span
                        style="display: inline-block; width: 200px; border-bottom: 2px solid #000; margin-left: 10px;"></span>
                </div>
                <div class="page-number">
                    <span>1/{{ totalPages }}</span>
                </div>
            </div>

            <div class="report-content-title">
                <h2>测试正文</h2>
            </div>

            <el-table :data="filteredCheckresults" style="width: 100%">
                <el-table-column label="序号" width="70" type="index"></el-table-column>
                <el-table-column prop="description" label="检测项"></el-table-column>
                <el-table-column prop="basis" label="检测依据" min-width="150"></el-table-column>
                <el-table-column prop="result" label="检测结果" min-width="150"></el-table-column>
                <el-table-column prop="IsComply" label="是否通过检查" width="120">
                    <template slot-scope="scope">
                        <span :class="getStatusClass(scope.row.IsComply)">
                            {{ getStatusText(scope.row.IsComply) }}
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
            <div class="page-numbers-container"></div>
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
            tableLoading: false,
            totalPages: 2,
            aliveHosts: [],
            selectedIP: '',
            globalDate: '',
            message: this.$store.state.message,
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
        changeServer() {
            if (this.selectedIP) {
                this.fetchAndDisplayChenckResults();
            }
        },

        estimatePageCount() {
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

            setTimeout(() => {
                const pdf = new jsPDF({
                    orientation: 'p',
                    unit: 'mm',
                    format: 'a4'
                });

                this.simulatePdfRendering(pdf).then(actualPageCount => {
                    this.totalPages = actualPageCount;
                    console.log('确定的总页数:', this.totalPages);

                    this.renderFinalPdf(pdf, this.totalPages);
                }).catch(err => {
                    console.error('PDF生成过程出错:', err);
                    this.pdfLoading = false;
                    this.showContentForPDF = false;
                    this.$message.error('PDF生成失败，请重试！');
                });
            }, 1000);
        },

        async simulatePdfRendering(pdf) {
            try {
                const originalPage = pdf.internal.getCurrentPageInfo().pageNumber;

                let pageCount = 0;

                const coverPage = this.$el.querySelector('.pdf-content .server1');
                await html2canvas(coverPage, { scale: 2, useCORS: true });
                pageCount = 1;

                pdf.addPage();
                pageCount++;

                const pageHeight = pdf.internal.pageSize.getHeight() - 20;

                const titleElement = this.$el.querySelector('.pdf-content .report-content-title');
                const titleCanvas = await html2canvas(titleElement, { scale: 2, useCORS: true });
                const titleWidth = 190;
                const titleHeight = titleCanvas.height * titleWidth / titleCanvas.width;

                let yPosition = 10 + titleHeight + 5;

                const headerElement = this.$el.querySelector('.pdf-content .el-table__header-wrapper');
                const headerCanvas = await html2canvas(headerElement, { scale: 2, useCORS: true });
                const headerWidth = 190;
                const headerHeight = headerCanvas.height * headerWidth / headerCanvas.width;

                yPosition += headerHeight + 2;

                const tableRows = this.$el.querySelectorAll('.pdf-content .el-table__body-wrapper table tr');

                for (let i = 0; i < tableRows.length; i++) {
                    const row = tableRows[i];
                    const rowCanvas = await html2canvas(row, { scale: 2, useCORS: true });
                    const rowWidth = 190;
                    const rowHeight = rowCanvas.height * rowWidth / rowCanvas.width;

                    if (yPosition + rowHeight > pageHeight) {
                        if (i < tableRows.length - 1) {
                            pdf.addPage();
                            pageCount++;
                            yPosition = 10;
                        }
                    }

                    yPosition += rowHeight + 2;
                }

                while (pdf.internal.getCurrentPageInfo().pageNumber > originalPage) {
                    pdf.deletePage(pdf.internal.getCurrentPageInfo().pageNumber);
                }

                return pageCount;
            } catch (error) {
                console.error('模拟渲染计算页数出错:', error);
                throw error;
            }
        },

        async renderFinalPdf(pdf, totalPageCount) {
            try {
                const coverPage = this.$el.querySelector('.pdf-content .server1');
                const coverCanvas = await html2canvas(coverPage, { scale: 2, useCORS: true });
                const imgData = coverCanvas.toDataURL('image/jpeg', 0.8);
                const imgWidth = 190;
                const imgHeight = coverCanvas.height * imgWidth / coverCanvas.width;

                pdf.addImage(imgData, 'JPEG', 10, 10, imgWidth, imgHeight);

                pdf.setFontSize(10);
                pdf.text(`1/${totalPageCount}`, pdf.internal.pageSize.getWidth() - 25, pdf.internal.pageSize.getHeight() - 10);

                pdf.addPage();

                const pageHeight = pdf.internal.pageSize.getHeight() - 20;
                let currentPageNum = 2;

                const titleElement = this.$el.querySelector('.pdf-content .report-content-title');
                const titleCanvas = await html2canvas(titleElement, { scale: 2, useCORS: true });
                const titleImgData = titleCanvas.toDataURL('image/jpeg', 0.8);
                const titleWidth = 190;
                const titleHeight = titleCanvas.height * titleWidth / titleCanvas.width;

                pdf.addImage(titleImgData, 'JPEG', 10, 10, titleWidth, titleHeight);
                let yPosition = 10 + titleHeight + 5;

                const headerElement = this.$el.querySelector('.pdf-content .el-table__header-wrapper');
                const headerCanvas = await html2canvas(headerElement, { scale: 2, useCORS: true });
                const headerImgData = headerCanvas.toDataURL('image/jpeg', 0.8);
                const headerWidth = 190;
                const headerHeight = headerCanvas.height * headerWidth / headerCanvas.width;

                pdf.addImage(headerImgData, 'JPEG', 10, yPosition, headerWidth, headerHeight);
                yPosition += headerHeight + 2;

                const tableRows = this.$el.querySelectorAll('.pdf-content .el-table__body-wrapper table tr');

                for (let i = 0; i < tableRows.length; i++) {
                    const row = tableRows[i];
                    const rowCanvas = await html2canvas(row, { scale: 2, useCORS: true });
                    const rowImgData = rowCanvas.toDataURL('image/jpeg', 0.8);
                    const rowWidth = 190;
                    const rowHeight = rowCanvas.height * rowWidth / rowCanvas.width;

                    if (yPosition + rowHeight > pageHeight) {
                        pdf.setFontSize(10);
                        pdf.text(`${currentPageNum}/${totalPageCount}`, pdf.internal.pageSize.getWidth() - 25, pdf.internal.pageSize.getHeight() - 10);

                        if (i < tableRows.length - 1) {
                            pdf.addPage();
                            currentPageNum++;
                            yPosition = 10;
                        }
                    }

                    pdf.addImage(rowImgData, 'JPEG', 10, yPosition, rowWidth, rowHeight);
                    yPosition += rowHeight + 2;
                }

                pdf.setFontSize(10);
                pdf.text(`${currentPageNum}/${totalPageCount}`, pdf.internal.pageSize.getWidth() - 25, pdf.internal.pageSize.getHeight() - 10);

                const filename = `Windows基线检测报告_${this.selectedIP}_${new Date().toISOString().slice(0, 10)}.pdf`;
                pdf.save(filename);

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
        getMessage() {
            this.serverInfo = this.message.ServerInfo;
            this.checkresults = this.message.Event_result;
        },
        goToClassifyProtect() {
            this.$router.push('/classifyProtect');
        },
        getStatusType(status) {
            switch (status) {
                case 'true': return 'success';
                case 'false': return 'danger';
                case 'pending': return 'warning';
                default: return 'info';
            }
        },

        getStatusText(status) {
            switch (status) {
                case 'true': return '通过';
                case 'false': return '未通过';
                case 'pending': return '待检查';
                default: return '未知';
            }
        },

        getStatusClass(status) {
            return {
                'failed-result': status === 'false',
                'pending-result': status === 'pending'
            };
        },


    },
    mounted() {
        this.getMessage()
        this.globalDate = new Date().toString();
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

.pdf-content {
    position: fixed;
    z-index: -1000;
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

.pending-result {
    color: #e6a23c;
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
