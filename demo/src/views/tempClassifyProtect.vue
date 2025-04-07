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
        <el-tag type="info">检测时间：{{ new Date().toLocaleString() }}</el-tag>
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
        <el-table-column label="序号" width="70" type="index"></el-table-column>
        <el-table-column prop="description" label="检测项" min-width="80"></el-table-column>
        <el-table-column prop="basis" label="基准" min-width="150"></el-table-column>
        <el-table-column prop="result" label="检测结果" min-width="150"></el-table-column>
        <el-table-column label="是否通过检查" width="120">
          <template slot-scope="scope">
            <el-tag :type="scope.row.IsComply === 'true' ? 'success' : 'danger'">
              {{ scope.row.IsComply === 'true' ? '通过' : '未通过' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="修改建议" min-width="250">
          <template slot-scope="scope">
            <span v-if="scope.row.IsComply === 'false'">{{ scope.row.recommend }}</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

  </div>
</template>

<script>
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
      ip:'',
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
    // 获取检测结果函数
    fetchAndDisplayChenckResults() {
      const ip = this.$route.query.ip;
      this.ip=this.$route.query.ip;
      if (!ip) {
        this.$message.error('无效的访问参数');
        this.$router.push('/');
        return;
      }

      this.tableLoading = true;
      axios.get(`/api/level3TmpUserinfo?ip=${ip}`)
          .then(response => {
            this.checkresults = response.data.checkResults;
            this.tableLoading = false;
          })
          .catch(error => {
            console.error('Error:', error);
            this.tableLoading = false;
            this.$message.error('获取检测结果失败，请重试');
          });
    },
    goBack() {
      this.$router.push('/classifyProtectHome');
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

