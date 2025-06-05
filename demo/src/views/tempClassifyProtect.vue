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
      <!--      <div class="date-info">-->
      <!--        <el-tag type="info">检测时间：{{ new Date().toLocaleString() }}</el-tag>-->
      <!--      </div>-->
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

      <!-- 新增保存评分按钮 -->
      <el-button
          type="success"
          icon="el-icon-check"
          @click="saveScores"
          :loading="saveLoading"
          size="medium">
        保存
      </el-button>
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
        <!--        <el-table-column prop="item_id" label="检测项ID" min-width="50"></el-table-column>-->
        <!--        <el-table-column label="序号" width="70" type="index"></el-table-column>-->
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
        <el-table-column label="是否符合等保要求（人工判定）" width="120">
          <template slot-scope="scope">
            <el-select
                v-model="scope.row.score"
                placeholder="请选择评分"
                size="mini">
              <el-option label="符合" value="1"></el-option>
              <el-option label="部分符合" value="0.5"></el-option>
              <el-option label="不符合" value="0"></el-option>
            </el-select>
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
      saveLoading: false, // 保存按钮的加载状态
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
            this.checkresults = response.data.checkResults.map(item => {
              // 根据 tmp_IsComply 的值来设置 score
              let score = '0'; // 默认值为不符合
              if (item.tmp_IsComply === 'true') {
                score = '1'; // 符合
              } else if (item.tmp_IsComply === 'half_true') {
                score = '0.5'; // 部分符合
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
      // axios.get(`/api/level3TmpUserinfo?ip=${ip}`)
      //     .then(response  => {
      //       this.checkresults = response.data.checkResults.map(item => ({
      //         ...item,
      //         score: item.IsComply === 'true' ? '1' : '0.5'
      //       }));
      //       this.tableLoading = false;
      //     })
      //     .catch(error => {
      //       console.error('Error:', error);
      //       this.tableLoading = false;
      //       this.$message.error('获取检测结果失败，请重试');
      //     });
    },
    saveScores() {
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
        ip: this.ip,
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

